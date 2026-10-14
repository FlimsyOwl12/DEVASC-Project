"""Offline F5 API and CLI coverage with mocked HTTP calls."""

import contextlib
import io
import os
import unittest
from unittest.mock import Mock, patch

import requests

from test_graphhopper_cli import app


KEY = "offline-test-key"
ORIGIN = (200, 14.5995, 120.9842, "Manila")
DESTINATION = (200, 14.676, 121.0437, "Quezon City")


def response(data, status=200):
    return Mock(status_code=status, json=Mock(return_value=data))


def hit(name="Manila", lat=14.5995, lng=120.9842):
    return {
        "name": name,
        "state": "Metro Manila",
        "country": "Philippines",
        "osm_value": "city",
        "point": {"lat": lat, "lng": lng},
    }


def path(distance=1609.344, duration=3661000):
    return {
        "distance": distance,
        "time": duration,
        "instructions": [
            {"text": "Head north", "distance": 804.672},
            {"text": "Arrive", "distance": 804.672},
        ],
    }


class MockedHTTPTests(unittest.TestCase):
    def test_successful_geocoding_uses_expected_request_and_returns_tuple(self):
        fake_response = response({"hits": [hit()]})
        with patch.object(app.requests, "get", return_value=fake_response) as get, contextlib.redirect_stdout(io.StringIO()):
            result = app.geocoding("Manila", KEY)

        self.assertEqual(result, (200, 14.5995, 120.9842, "Manila, Metro Manila, Philippines"))
        url = get.call_args.args[0]
        self.assertIn("q=Manila", url)
        self.assertIn("limit=1", url)
        self.assertIn("key=" + KEY, url)
        self.assertEqual(get.call_args.kwargs["timeout"], app.TIMEOUT_SECONDS)

    def test_successful_routing_uses_profile_points_and_returns_validated_path(self):
        route = path()
        with patch.object(app.requests, "get", return_value=response({"paths": [route]})) as get, contextlib.redirect_stdout(io.StringIO()):
            result = app.routing(ORIGIN, DESTINATION, "bike", KEY)

        self.assertEqual(result["distance"], 1609.344)
        self.assertEqual(result["instructions"][0]["text"], "Head north")
        url = get.call_args.args[0]
        self.assertIn("profile=bike", url)
        self.assertIn("point=14.5995%2C120.9842", url)
        self.assertIn("point=14.676%2C121.0437", url)
        self.assertEqual(get.call_args.kwargs["timeout"], app.TIMEOUT_SECONDS)

    def test_empty_hits_and_paths_do_not_crash(self):
        output = io.StringIO()
        with patch.object(app.requests, "get", side_effect=[response({"hits": []}), response({"paths": []})]), contextlib.redirect_stdout(output):
            self.assertEqual(app.geocoding("Atlantis", KEY), (200, None, None, "Atlantis"))
            self.assertIsNone(app.routing(ORIGIN, DESTINATION, "car", KEY))

        text = output.getvalue()
        self.assertIn("No location found for: Atlantis", text)
        self.assertIn("No route was returned", text)

    def test_http_401_429_and_server_errors_are_reported_without_route_data(self):
        cases = [
            ("geocoding", lambda: app.geocoding("Manila", KEY), 401),
            ("geocoding", lambda: app.geocoding("Manila", KEY), 429),
            ("routing", lambda: app.routing(ORIGIN, DESTINATION, "car", KEY), 500),
        ]
        for service, call, status in cases:
            with self.subTest(service=service, status=status):
                output = io.StringIO()
                with patch.object(app.requests, "get", return_value=response({"message": f"bad key {KEY}"}, status)), contextlib.redirect_stdout(output):
                    result = call()
                if service == "geocoding":
                    self.assertEqual(result[:3], (status, None, None))
                else:
                    self.assertIsNone(result)
                self.assertIn(str(status), output.getvalue())
                self.assertNotIn(KEY, output.getvalue())

    def test_invalid_json_and_malformed_schemas_raise_controlled_error(self):
        bad_json = Mock(status_code=200, json=Mock(side_effect=ValueError("not json")))
        with patch.object(app.requests, "get", return_value=bad_json):
            with self.assertRaisesRegex(app.APIResponseError, "invalid JSON"):
                app.geocoding("Manila", KEY)
            with self.assertRaisesRegex(app.APIResponseError, "invalid JSON"):
                app.routing(ORIGIN, DESTINATION, "car", KEY)

        cases = [
            ({"hits": [{"name": "Missing point"}]}, lambda: app.geocoding("Manila", KEY)),
            ({"paths": [{"distance": 1, "time": 1}]}, lambda: app.routing(ORIGIN, DESTINATION, "car", KEY)),
        ]
        for data, call in cases:
            with self.subTest(data=data), patch.object(app.requests, "get", return_value=response(data)):
                with self.assertRaises(app.APIResponseError):
                    call()

    def test_timeouts_are_handled_by_main_loop(self):
        output = io.StringIO()
        with patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}), patch.object(app, "load_dotenv"), patch("builtins.input", side_effect=["car", "metric", "detailed", "Origin", "q"]), patch.object(app.requests, "get", side_effect=requests.Timeout), contextlib.redirect_stdout(output):
            self.assertEqual(app.main(), 0)

        self.assertIn("request failed or timed out", output.getvalue())

    def test_blank_location_reprompts_and_quit_exits_without_http(self):
        output = io.StringIO()
        with patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}), patch.object(app, "load_dotenv"), patch("builtins.input", side_effect=["car", "metric", "detailed", "", "quit"]), patch.object(app.requests, "get") as get, contextlib.redirect_stdout(output):
            self.assertEqual(app.main(), 0)

        get.assert_not_called()
        self.assertIn("Please enter a value", output.getvalue())

    def test_routing_is_skipped_after_unsuccessful_origin_geocoding(self):
        with patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}), patch.object(app, "load_dotenv"), patch("builtins.input", side_effect=["car", "metric", "detailed", "Nowhere", "q"]), patch.object(app, "geocoding", return_value=(200, None, None, "Nowhere")) as geocode, patch.object(app, "routing") as route, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.main(), 0)

        geocode.assert_called_once_with("Nowhere", KEY)
        route.assert_not_called()

    def test_suite_does_not_need_real_api_key(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(app, "load_dotenv"), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.main(), 1)


if __name__ == "__main__":
    unittest.main()
