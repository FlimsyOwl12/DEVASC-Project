"""Offline F3 acceptance tests using only mocked HTTP responses."""

import contextlib
import io
import os
import re
import unittest
from unittest.mock import Mock, patch

from test_graphhopper_cli import app


KEY = "offline-output-mode-key"


def route_data():
    return {
        "distance": 3218.688,
        "time": 3661000,
        "instructions": [
            {"text": "Turn left", "distance": 1609.344},
            {"text": "Arrive", "distance": 1609.344},
        ],
    }


def route_responses():
    hit = {"hits": [{"name": "Test city", "point": {"lat": 1, "lng": 2}}]}
    return [
        Mock(status_code=200, json=Mock(return_value=data))
        for data in (hit, hit, {"paths": [route_data()]})
    ]


class OutputModeTests(unittest.TestCase):
    def render(self, mode, units="metric", path=None):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            app.display_route(path or route_data(), "Origin city", "Destination city", "car", units, mode)
        return output.getvalue()

    def test_summary_retains_totals_and_metadata_without_steps(self):
        for units, distance in [("metric", "3.2 km"), ("imperial", "2.0 miles")]:
            with self.subTest(units=units):
                text = self.render("summary", units)
                for value in ["ROUTE SUMMARY", "Origin city", "Destination city", "car", distance, "01:01:01"]:
                    self.assertIn(value, text)
                self.assertNotIn("DIRECTIONS", text)
                self.assertNotIn("Turn left", text)
                self.assertNotIn("Arrive", text)
                self.assertIsNone(re.search(r"(?m)^\s*\d+\. ", text))

    def test_detailed_mode_keeps_numbered_directions_in_selected_units(self):
        for units, step_distance in [("metric", "1.6 km"), ("imperial", "1.0 miles")]:
            with self.subTest(units=units):
                text = self.render("detailed", units)
                self.assertIn("DIRECTIONS", text)
                self.assertRegex(text, rf"(?m)^\s*1\. Turn left \({re.escape(step_distance)}\)$")
                self.assertRegex(text, rf"(?m)^\s*2\. Arrive \({re.escape(step_distance)}\)$")

    def test_summary_does_not_show_empty_directions_message(self):
        path = route_data()
        path["instructions"] = []
        text = self.render("summary", path=path)
        self.assertIn("3.2 km", text)
        self.assertNotIn("DIRECTIONS", text)
        self.assertNotIn("No direction steps", text)

    def test_blank_and_invalid_modes_reprompt_and_accept_case_insensitive_choice(self):
        with patch("builtins.input", side_effect=["", "compact", " SUMMARY "]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.read_output_mode(), "summary")
        with patch("builtins.input", return_value="DETAILED"):
            self.assertEqual(app.read_output_mode(), "detailed")

    def test_quitting_mode_prompt_does_not_make_requests(self):
        for keyword in ["q", "quit", " Q "]:
            with (
                self.subTest(keyword=keyword),
                patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}),
                patch.object(app, "load_dotenv"),
                patch("builtins.input", side_effect=["car", "metric", keyword]),
                patch.object(app.requests, "get") as get,
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(app.main(), 0)
                get.assert_not_called()

    def test_main_uses_selected_mode_with_mocked_route(self):
        for mode in ["summary", "detailed"]:
            output = io.StringIO()
            with (
                self.subTest(mode=mode),
                patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}),
                patch.object(app, "load_dotenv"),
                patch("builtins.input", side_effect=["car", "imperial", mode, "Origin", "Destination", "q"]),
                patch.object(app.requests, "get", side_effect=route_responses()) as get,
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(app.main(), 0)
                self.assertEqual(get.call_count, 3)
            text = output.getvalue()
            self.assertIn("2.0 miles", text)
            self.assertIn("01:01:01", text)
            self.assertEqual("DIRECTIONS" in text, mode == "detailed")
            self.assertNotIn(KEY, text)

    def test_mode_can_change_between_route_requests(self):
        answers = [
            "car", "metric", "summary", "Origin", "Destination",
            "bike", "imperial", "detailed", "Origin", "Destination", "q",
        ]
        output = io.StringIO()
        with (
            patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}),
            patch.object(app, "load_dotenv"),
            patch("builtins.input", side_effect=answers),
            patch.object(app.requests, "get", side_effect=route_responses() + route_responses()),
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(app.main(), 0)
        _, first, second = output.getvalue().split("ROUTE SUMMARY")
        self.assertIn("3.2 km", first)
        self.assertNotIn("DIRECTIONS", first)
        self.assertIn("2.0 miles", second)
        self.assertIn("DIRECTIONS", second)

    def test_unknown_display_mode_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "summary or detailed"):
            self.render("compact")


if __name__ == "__main__":
    unittest.main()
