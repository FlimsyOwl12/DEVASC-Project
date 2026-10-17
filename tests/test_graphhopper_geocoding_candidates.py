"""Offline unit and acceptance tests for F8 — Multiple Geocoding Candidates."""

import contextlib
import io
import os
import unittest
from unittest.mock import Mock, patch

import requests

from test_graphhopper_cli import app


KEY = "offline-geocode-key"


def response(data, status=200):
    return Mock(status_code=status, json=Mock(return_value=data))


def springfield_hits():
    return [
        {
            "name": "Springfield",
            "city": "Springfield",
            "state": "Illinois",
            "country": "United States",
            "osm_value": "city",
            "point": {"lat": 39.7817, "lng": -89.6501},
        },
        {
            "name": "Springfield",
            "city": "Springfield",
            "state": "Missouri",
            "country": "United States",
            "osm_value": "city",
            "point": {"lat": 37.2090, "lng": -93.2923},
        },
        {
            "name": "Springfield",
            "city": "Springfield",
            "state": "Massachusetts",
            "country": "United States",
            "osm_value": "city",
            "point": {"lat": 42.1015, "lng": -72.5898},
        },
    ]


class MultipleGeocodingCandidatesTests(unittest.TestCase):
    def test_multiple_candidates_are_displayed_and_selected_coordinates_are_returned(self):
        output = io.StringIO()
        with (
            patch.object(app.requests, "get", return_value=response({"hits": springfield_hits()})) as get,
            patch("builtins.input", return_value="2"),
            contextlib.redirect_stdout(output),
        ):
            result = app.geocoding("Springfield", KEY)

        self.assertEqual(
            result,
            (200, 37.2090, -93.2923, "Springfield, Missouri, United States"),
        )
        self.assertEqual(get.call_count, 1)
        text = output.getvalue()
        self.assertIn('Search results for "Springfield":', text)
        self.assertIn("1. Springfield, Illinois, United States", text)
        self.assertIn("2. Springfield, Missouri, United States", text)
        self.assertIn("3. Springfield, Massachusetts, United States", text)

    def test_single_valid_candidate_skips_selection_menu(self):
        output = io.StringIO()
        single = [springfield_hits()[0]]
        with (
            patch.object(app.requests, "get", return_value=response({"hits": single})),
            patch("builtins.input") as mocked_input,
            contextlib.redirect_stdout(output),
        ):
            result = app.geocoding("Springfield", KEY)

        mocked_input.assert_not_called()
        self.assertEqual(result, (200, 39.7817, -89.6501, "Springfield, Illinois, United States"))
        self.assertNotIn("Search results for", output.getvalue())
        self.assertIn("Location: Springfield, Illinois, United States", output.getvalue())

    def test_invalid_selections_are_rejected_without_duplicate_api_requests(self):
        output = io.StringIO()
        with (
            patch.object(app.requests, "get", return_value=response({"hits": springfield_hits()})) as get,
            patch("builtins.input", side_effect=["", "0", "4", "abc", "-1", "3"]),
            contextlib.redirect_stdout(output),
        ):
            result = app.geocoding("Springfield", KEY)

        self.assertEqual(get.call_count, 1)
        self.assertEqual(
            result,
            (200, 42.1015, -72.5898, "Springfield, Massachusetts, United States"),
        )
        self.assertIn("Invalid selection", output.getvalue())

    def test_search_retry_requests_new_location_and_returns_chosen_candidate(self):
        boston_hit = [{
            "name": "Boston",
            "state": "Massachusetts",
            "country": "United States",
            "osm_value": "city",
            "point": {"lat": 42.3601, "lng": -71.0589},
        }]
        replies = [
            response({"hits": springfield_hits()}),
            response({"hits": boston_hit}),
        ]
        output = io.StringIO()
        with (
            patch.object(app.requests, "get", side_effect=replies) as get,
            patch("builtins.input", side_effect=["R", "Boston"]),
            contextlib.redirect_stdout(output),
        ):
            result = app.geocoding("Springfield", KEY)

        self.assertEqual(get.call_count, 2)
        self.assertIn("q=Springfield", get.call_args_list[0].args[0])
        self.assertIn("q=Boston", get.call_args_list[1].args[0])
        self.assertEqual(result, (200, 42.3601, -71.0589, "Boston, Massachusetts, United States"))

    def test_quitting_during_candidate_selection_makes_no_further_api_requests(self):
        output = io.StringIO()
        with (
            patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}),
            patch.object(app, "load_dotenv"),
            patch.object(app.requests, "get", return_value=response({"hits": springfield_hits()})) as get,
            patch("builtins.input", side_effect=["1", "car", "metric", "detailed", "Springfield", "Q"]),
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(app.main(), 0)

        self.assertEqual(get.call_count, 1)

    def test_selected_candidate_coordinates_are_passed_to_routing_for_origin_and_destination(self):
        dest_hits = [
            {
                "name": "Columbus",
                "state": "Ohio",
                "country": "United States",
                "point": {"lat": 39.9612, "lng": -82.9988},
            },
            {
                "name": "Columbus",
                "state": "Georgia",
                "country": "United States",
                "point": {"lat": 32.4610, "lng": -84.9877},
            },
        ]
        route_payload = {
            "paths": [{
                "distance": 1609.344,
                "time": 60000,
                "instructions": [{"text": "Arrive", "distance": 1609.344}],
            }]
        }
        replies = [
            response({"hits": springfield_hits()}),
            response({"hits": dest_hits}),
            response(route_payload),
        ]
        output = io.StringIO()
        inputs = [
            "1",
            "car",
            "imperial",
            "summary",
            "Springfield",
            "2",  # Select Springfield, Missouri (37.209, -93.2923)
            "Columbus",
            "2",  # Select Columbus, Georgia (32.461, -84.9877)
            "no",
            "4",
        ]
        with (
            patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}),
            patch.object(app, "load_dotenv"),
            patch.object(app.requests, "get", side_effect=replies) as get,
            patch("builtins.input", side_effect=inputs),
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(app.main(), 0)

        self.assertEqual(get.call_count, 3)
        route_url = get.call_args_list[2].args[0]
        self.assertIn("point=37.209%2C-93.2923", route_url)
        self.assertIn("point=32.461%2C-84.9877", route_url)
        self.assertNotIn("39.7817", route_url)
        self.assertNotIn("39.9612", route_url)
        text = output.getvalue()
        self.assertIn("Springfield, Missouri, United States", text)
        self.assertIn("Columbus, Georgia, United States", text)

    def test_malformed_candidates_are_filtered_out_when_valid_candidates_exist(self):
        mixed_hits = [
            {"name": "Broken coord", "point": {"lat": 999, "lng": 0}},
            {"name": "", "point": {"lat": 10, "lng": 20}},
            {
                "name": "Valid Place",
                "city": "Metro",
                "state": "Region",
                "country": "Country",
                "point": {"lat": 12.34, "lng": 56.78},
            },
        ]
        with (
            patch.object(app.requests, "get", return_value=response({"hits": mixed_hits})),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            result = app.geocoding("Valid Place", KEY)

        self.assertEqual(result, (200, 12.34, 56.78, "Valid Place, Metro, Region, Country"))

    def test_max_candidates_limits_displayed_choices_to_five_by_default(self):
        many_hits = [
            {
                "name": f"Place {i}",
                "country": "Country",
                "point": {"lat": float(i), "lng": float(i)},
            }
            for i in range(1, 9)
        ]
        output = io.StringIO()
        with (
            patch.object(app.requests, "get", return_value=response({"hits": many_hits})),
            patch("builtins.input", side_effect=["6", "5"]),
            contextlib.redirect_stdout(output),
        ):
            result = app.geocoding("Place", KEY)

        self.assertEqual(result, (200, 5.0, 5.0, "Place 5, Country"))
        text = output.getvalue()
        self.assertIn("5. Place 5, Country", text)
        self.assertNotIn("6. Place 6, Country", text)

    def test_routing_rejects_missing_or_invalid_coordinates(self):
        with self.assertRaises(ValueError):
            app.routing((200, None, None, "Bad"), (200, 10, 20, "Ok"), "car", KEY)
        with self.assertRaises(app.APIResponseError):
            app.routing((200, 95, 0, "Bad lat"), (200, 10, 20, "Ok"), "car", KEY)

    def test_api_failures_and_timeouts_during_geocoding_do_not_crash(self):
        output = io.StringIO()
        with (
            patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}),
            patch.object(app, "load_dotenv"),
            patch.object(app.requests, "get", side_effect=requests.ConnectionError("offline")),
            patch("builtins.input", side_effect=["1", "car", "metric", "detailed", "Manila", "4"]),
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(app.main(), 0)

        self.assertIn("request failed or timed out", output.getvalue())


if __name__ == "__main__":
    unittest.main()
