"""Focused regression checks for F4 API response validation."""

import contextlib
import copy
import io
import os
import unittest
from unittest.mock import Mock, patch

from test_graphhopper_cli import app


KEY = "offline-test-key"
ORIGIN = (200, 1, 2, "Origin")
DESTINATION = (200, 3, 4, "Destination")


def response(data, status=200):
    return Mock(status_code=status, json=Mock(return_value=data))


def valid_hit():
    return {"name": "Test city", "point": {"lat": 0, "lng": 0}}


def valid_path():
    return {"distance": 1609.344, "time": 3661000, "instructions": [
        {"text": "Arrive", "distance": 1609.344},
    ]}


class ResponseValidationTests(unittest.TestCase):
    def geocode(self, data):
        with patch.object(app.requests, "get", return_value=response(data)), contextlib.redirect_stdout(io.StringIO()):
            return app.geocoding("Test city", KEY)

    def route(self, data):
        with patch.object(app.requests, "get", return_value=response(data)), contextlib.redirect_stdout(io.StringIO()):
            return app.routing(ORIGIN, DESTINATION, "car", KEY)

    def test_valid_coordinates_include_zero_and_optional_names(self):
        self.assertEqual(self.geocode({"hits": [valid_hit()]}), (200, 0, 0, "Test city"))

    def test_invalid_top_level_json_and_list_fields(self):
        for data in [None, [], "error", 7, {"hits": {}}, {}, {"hits": None}]:
            with self.subTest(service="geocoding", data=data), self.assertRaises(app.APIResponseError):
                self.geocode(data)
        for data in [None, [], "error", 7, {"paths": {}}, {}, {"paths": None}]:
            with self.subTest(service="routing", data=data), self.assertRaises(app.APIResponseError):
                self.route(data)

    def test_invalid_coordinate_fields(self):
        for field, values in [("lat", [None, "0", True, float("nan"), float("inf"), -91, 91]), ("lng", [None, "0", False, -181, 181])]:
            for value in values:
                hit = valid_hit()
                hit["point"][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(app.APIResponseError):
                    self.geocode({"hits": [hit]})
        for hit in [None, [], {"name": "Test city"}, {"name": "Test city", "point": []}]:
            with self.subTest(hit=hit), self.assertRaises(app.APIResponseError):
                self.geocode({"hits": [hit]})

    def test_invalid_place_names(self):
        for field, value in [("name", None), ("name", " "), ("name", 4), ("country", []), ("state", False)]:
            hit = valid_hit()
            hit[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(app.APIResponseError):
                self.geocode({"hits": [hit]})

    def test_missing_and_invalid_route_numbers(self):
        for field in ["distance", "time"]:
            for value in [None, "1", True, -1, float("inf"), float("nan"), 10**400]:
                path = valid_path()
                path[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(app.APIResponseError):
                    self.route({"paths": [path]})
            path = valid_path()
            del path[field]
            with self.subTest(missing=field), self.assertRaises(app.APIResponseError):
                self.route({"paths": [path]})
        with self.assertRaises(app.APIResponseError):
            self.route({"paths": [None]})

    def test_malformed_instruction_list_and_steps(self):
        for steps in [None, {}, "steps", [None], [{}], [{"text": " ", "distance": 0}], [{"text": 3, "distance": 0}], [{"text": "Arrive", "distance": None}], [{"text": "Arrive", "distance": -1}]]:
            path = valid_path()
            path["instructions"] = steps
            with self.subTest(steps=steps), self.assertRaises(app.APIResponseError):
                self.route({"paths": [path]})
        path = valid_path()
        del path["instructions"]
        with self.assertRaises(app.APIResponseError):
            self.route({"paths": [path]})

    def test_empty_results_are_safe(self):
        self.assertEqual(self.geocode({"hits": []}), (200, None, None, "Test city"))
        self.assertIsNone(self.route({"paths": []}))
        path = valid_path()
        path["instructions"] = []
        self.assertEqual(self.route({"paths": [path]}), path)

    def test_valid_route_keeps_units_and_duration(self):
        path = self.route({"paths": [valid_path()]})
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            app.display_route(path, "Origin", "Destination", "car", "imperial")
        self.assertIn("1.0 miles", output.getvalue())
        self.assertIn("01:01:01", output.getvalue())

    def test_http_messages_and_instruction_text_redact_key(self):
        output = io.StringIO()
        with patch.object(app.requests, "get", return_value=response({"message": "Invalid key: " + KEY}, 400)), contextlib.redirect_stdout(output):
            app.geocoding("Test city", KEY)
            app.routing(ORIGIN, DESTINATION, "car", KEY)
        self.assertNotIn(KEY, output.getvalue())
        self.assertIn("[REDACTED]", output.getvalue())
        path = valid_path()
        path["instructions"][0]["text"] = "Do not display " + KEY
        self.assertNotIn(KEY, self.route({"paths": [path]})["instructions"][0]["text"])

    def test_invalid_json_does_not_reveal_parser_error_contents(self):
        resp = Mock(status_code=200, json=Mock(side_effect=ValueError(KEY)))
        with patch.object(app.requests, "get", return_value=resp):
            for call in [lambda: app.geocoding("Test city", KEY), lambda: app.routing(ORIGIN, DESTINATION, "car", KEY)]:
                with self.assertRaises(app.APIResponseError) as error:
                    call()
                self.assertNotIn(KEY, str(error.exception))
                self.assertIn("invalid JSON", str(error.exception))

    def test_bad_geocoding_returns_to_prompt_without_routing(self):
        output = io.StringIO()
        with patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}), patch.object(app, "load_dotenv"), patch("builtins.input", side_effect=["car", "metric", "Origin", "q"]), patch.object(app.requests, "get", return_value=response({"hits": [{"name": KEY, "point": []}]})) as get, patch.object(app, "routing") as route, contextlib.redirect_stdout(output):
            self.assertEqual(app.main(), 0)
            self.assertEqual(get.call_count, 1)
            route.assert_not_called()
        self.assertIn("API response error:", output.getvalue())
        self.assertNotIn("Traceback", output.getvalue())
        self.assertNotIn(KEY, output.getvalue())

    def test_bad_routing_returns_to_prompt_without_partial_output(self):
        for bad in [[], {"paths": [None]}, {"paths": [{"distance": -1}]}]:
            output = io.StringIO()
            replies = [response({"hits": [valid_hit()]}), response({"hits": [valid_hit()]}), response(copy.deepcopy(bad))]
            with self.subTest(reply=bad), patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}), patch.object(app, "load_dotenv"), patch("builtins.input", side_effect=["car", "metric", "Origin", "Destination", "q"]), patch.object(app.requests, "get", side_effect=replies), contextlib.redirect_stdout(output):
                self.assertEqual(app.main(), 0)
            self.assertIn("API response error:", output.getvalue())
            self.assertNotIn("ROUTE SUMMARY", output.getvalue())
            self.assertNotIn("Traceback", output.getvalue())
            self.assertNotIn(KEY, output.getvalue())


if __name__ == "__main__":
    unittest.main()
