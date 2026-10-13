"""Offline acceptance checks for the implemented CLI enhancements."""

import contextlib
import importlib.util
import io
import os
from pathlib import Path
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "labs/devnet-src/graphhopper/graphhopper_parse-json_7.py"
SPEC = importlib.util.spec_from_file_location("graphhopper_cli", SCRIPT)
app = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(app)


class UnitSelectionTests(unittest.TestCase):
    def test_distance_conversion(self):
        self.assertEqual(app.format_distance(1609.344, "imperial"), "1.0 miles")
        self.assertEqual(app.format_distance(1000, "metric"), "1.0 km")
        self.assertEqual(app.format_distance(0, "metric"), "0.0 km")

    def test_selected_units_apply_to_total_and_every_instruction(self):
        path = {"distance": 3218.688, "time": 3661000, "instructions": [
            {"text": "Turn left", "distance": 1609.344},
            {"text": "Arrive", "distance": 1609.344},
        ]}
        for units, label, other in [("metric", "km", "miles"), ("imperial", "miles", "km")]:
            with self.subTest(units=units):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    app.display_route(path, "Origin", "Destination", "car", units)
                text = output.getvalue()
                self.assertEqual(text.count(label), 3)
                self.assertNotIn(other, text)
                self.assertIn("01:01:01", text)
                if units == "imperial":
                    self.assertIn("2.0 miles", text)
                    self.assertEqual(text.count("1.0 miles"), 2)

    def test_invalid_and_blank_units_are_reprompted(self):
        with patch("builtins.input", side_effect=["", "feet", "IMPERIAL"]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.read_units(), "imperial")

    def test_quitting_unit_prompt_does_not_call_api(self):
        for keyword in ["q", "quit", " Q "]:
            with self.subTest(keyword=keyword), patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": "offline-test-key"}), patch.object(app, "load_dotenv"), patch("builtins.input", side_effect=["car", keyword]), patch.object(app.requests, "get") as get, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(app.main(), 0)
                get.assert_not_called()

    def test_main_passes_the_selected_units_to_output(self):
        path = {"distance": 1609.344, "time": 1000, "instructions": []}
        with patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": "offline-test-key"}), patch.object(app, "load_dotenv"), patch("builtins.input", side_effect=["car", "imperial", "Origin", "Destination", "q"]), patch.object(app, "geocoding", side_effect=[(200, 1, 2, "Origin"), (200, 3, 4, "Destination")]), patch.object(app, "routing", return_value=path), patch.object(app, "display_route") as display, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.main(), 0)
            display.assert_called_once_with(path, "Origin", "Destination", "car", "imperial")


if __name__ == "__main__":
    unittest.main()
