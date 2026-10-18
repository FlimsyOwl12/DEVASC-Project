"""Offline unit and acceptance tests for F7 — Route Export System."""

import contextlib
import csv
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from test_graphhopper_cli import app


KEY = "secret-api-key-999"


def make_record(units="metric", with_steps=True, timestamp="2026-10-17T18:30:00Z"):
    steps = [
        {"text": "Head north on Main St", "distance": 1609.344},
        {"text": "Turn right onto Oak Ave", "distance": 804.672},
    ] if with_steps else []
    path = {
        "distance": 2414.016,
        "time": 3661000,
        "instructions": steps,
    }
    origin = (200, 39.7817, -89.6501, "Springfield, Illinois, United States")
    destination = (200, 41.8781, -87.6298, "Chicago, Illinois, United States")
    return app.create_route_record(
        path,
        origin,
        destination,
        profile="car",
        units=units,
        timestamp=timestamp,
        key=KEY,
    )


class RouteExportTests(unittest.TestCase):
    def test_txt_export_contains_all_required_fields_and_directions(self):
        record = make_record(units="metric")
        with tempfile.TemporaryDirectory() as tmp_dir:
            saved = app.export_route_txt(record, export_dir=tmp_dir)
            self.assertTrue(saved.exists())
            self.assertEqual(saved.suffix, ".txt")
            content = saved.read_text(encoding="utf-8")

        self.assertIn("Springfield, Illinois, United States", content)
        self.assertIn("Chicago, Illinois, United States", content)
        self.assertIn("car", content)
        self.assertIn("Metric", content)
        self.assertIn("2.4 km", content)
        self.assertIn("01:01:01", content)
        self.assertIn("2026-10-17T18:30:00Z", content)
        self.assertIn("1. Head north on Main St (1.6 km)", content)
        self.assertIn("2. Turn right onto Oak Ave (0.8 km)", content)

    def test_json_export_structure_and_values(self):
        record = make_record(units="metric")
        with tempfile.TemporaryDirectory() as tmp_dir:
            saved = app.export_route_json(record, export_dir=tmp_dir)
            self.assertTrue(saved.exists())
            self.assertEqual(saved.suffix, ".json")
            data = json.loads(saved.read_text(encoding="utf-8"))

        self.assertEqual(data["origin"], "Springfield, Illinois, United States")
        self.assertEqual(data["destination"], "Chicago, Illinois, United States")
        self.assertEqual(data["profile"], "car")
        self.assertEqual(data["units"], "metric")
        self.assertEqual(data["distance"]["unit"], "km")
        self.assertAlmostEqual(data["distance"]["value"], 2.41, places=2)
        self.assertEqual(data["duration"]["unit"], "minutes")
        self.assertAlmostEqual(data["duration"]["value"], 61.02, places=2)
        self.assertEqual(data["exported_at"], "2026-10-17T18:30:00Z")
        self.assertEqual(len(data["instructions"]), 2)
        self.assertEqual(data["instructions"][0]["step"], 1)
        self.assertEqual(data["instructions"][0]["text"], "Head north on Main St")
        self.assertEqual(data["instructions"][0]["distance"]["unit"], "km")
        self.assertAlmostEqual(data["instructions"][0]["distance"]["value"], 1.61, places=2)

    def test_csv_export_validity_and_schema(self):
        record = make_record(units="imperial")
        with tempfile.TemporaryDirectory() as tmp_dir:
            saved = app.export_route_csv(record, export_dir=tmp_dir)
            self.assertTrue(saved.exists())
            self.assertEqual(saved.suffix, ".csv")
            with saved.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(tuple(reader.fieldnames), app.CSV_COLUMNS)
                rows = list(reader)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["origin"], "Springfield, Illinois, United States")
        self.assertEqual(rows[0]["destination"], "Chicago, Illinois, United States")
        self.assertEqual(rows[0]["profile"], "car")
        self.assertEqual(rows[0]["units"], "imperial")
        self.assertEqual(rows[0]["total_distance"], "1.5")
        self.assertEqual(rows[0]["distance_unit"], "miles")
        self.assertEqual(rows[0]["duration_formatted"], "01:01:01")
        self.assertEqual(rows[0]["step_number"], "1")
        self.assertEqual(rows[0]["instruction"], "Head north on Main St")
        self.assertEqual(rows[0]["step_distance"], "1.0")
        self.assertEqual(rows[1]["step_number"], "2")
        self.assertEqual(rows[1]["step_distance"], "0.5")

    def test_metric_and_imperial_consistency_across_all_export_formats(self):
        for units, total_label, step1_label, unit_code in [
            ("metric", "2.4 km", "1.6 km", "km"),
            ("imperial", "1.5 miles", "1.0 miles", "miles"),
        ]:
            record = make_record(units=units)
            with self.subTest(units=units), tempfile.TemporaryDirectory() as tmp_dir:
                txt_path = app.export_route_txt(record, export_dir=tmp_dir)
                json_path = app.export_route_json(record, export_dir=tmp_dir)
                csv_path = app.export_route_csv(record, export_dir=tmp_dir)

                txt = txt_path.read_text(encoding="utf-8")
                self.assertIn(total_label, txt)
                self.assertIn(step1_label, txt)

                payload = json.loads(json_path.read_text(encoding="utf-8"))
                self.assertEqual(payload["distance"]["unit"], unit_code)
                self.assertEqual(payload["instructions"][0]["distance"]["unit"], unit_code)

                with csv_path.open("r", encoding="utf-8", newline="") as handle:
                    rows = list(csv.DictReader(handle))
                self.assertEqual(rows[0]["distance_unit"], unit_code)
                self.assertEqual(rows[0]["step_distance_formatted"], step1_label)

    def test_summary_terminal_mode_still_exports_all_directions(self):
        origin_hit = {"hits": [{"name": "Manila", "point": {"lat": 14.5995, "lng": 120.9842}}]}
        dest_hit = {"hits": [{"name": "Quezon City", "point": {"lat": 14.676, "lng": 121.0437}}]}
        route_reply = {
            "paths": [{
                "distance": 2000.0,
                "time": 600000,
                "instructions": [
                    {"text": "Step one direction", "distance": 1000.0},
                    {"text": "Step two direction", "distance": 1000.0},
                ],
            }]
        }
        responses = [
            Mock(status_code=200, json=Mock(return_value=origin_hit)),
            Mock(status_code=200, json=Mock(return_value=dest_hit)),
            Mock(status_code=200, json=Mock(return_value=route_reply)),
        ]
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp_dir:
            inputs = ["1", "car", "metric", "summary", "Manila", "Quezon City", "yes", "1", "4"]
            with (
                patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}),
                patch.object(app, "load_dotenv"),
                patch("builtins.input", side_effect=inputs),
                patch.object(app.requests, "get", side_effect=responses) as get,
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(app.main(export_dir=tmp_dir), 0)
                self.assertEqual(get.call_count, 3)

            files = list(Path(tmp_dir).glob("*.txt"))
            self.assertEqual(len(files), 1)
            exported_text = files[0].read_text(encoding="utf-8")

        terminal_text = output.getvalue()
        self.assertNotIn("Step one direction", terminal_text)
        self.assertIn("1. Step one direction (1.0 km)", exported_text)
        self.assertIn("2. Step two direction (1.0 km)", exported_text)

    def test_safe_filename_generation_and_path_traversal_prevention(self):
        self.assertEqual(app.sanitize_filename_component("Manila / Quezon: *City*?"), "manila_quezon_city")
        self.assertEqual(app.sanitize_filename_component("CON"), "location")
        self.assertEqual(app.sanitize_filename_component("   "), "location")

        for unsafe in ["../evil.txt", "..\\evil.txt", "/tmp/evil.txt", "C:\\evil.txt", "sub/file.txt", "..", "CON.txt"]:
            with self.subTest(unsafe=unsafe), self.assertRaises(ValueError):
                app.validate_safe_filename(unsafe, "txt")

    def test_duplicate_filename_handling_prevents_silent_overwrite(self):
        record = make_record()
        with tempfile.TemporaryDirectory() as tmp_dir:
            first = app.export_route_txt(record, export_dir=tmp_dir, filename="custom_route.txt")
            self.assertTrue(first.exists())

            with self.assertRaises(FileExistsError):
                app.export_route_txt(record, export_dir=tmp_dir, filename="custom_route.txt")

            renamed = app.export_route_txt(
                record, export_dir=tmp_dir, filename="custom_route.txt", auto_rename=True
            )
            self.assertNotEqual(first, renamed)
            self.assertEqual(renamed.name, "custom_route_1.txt")
            self.assertTrue(renamed.exists())

    def test_interactive_duplicate_filename_allows_custom_name_or_auto_rename(self):
        record = make_record()
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp_dir:
            first = app.export_route_txt(record, export_dir=tmp_dir)
            self.assertTrue(first.exists())

            with patch("builtins.input", side_effect=["1", "../bad.txt", "user_chosen_name"]), contextlib.redirect_stdout(output):
                second = app.prompt_export_format_and_save(record, export_dir=tmp_dir, key=KEY)

            self.assertIsNotNone(second)
            self.assertEqual(second.name, "user_chosen_name.txt")
            self.assertTrue(first.exists())
            self.assertTrue(second.exists())
        self.assertIn("Invalid filename", output.getvalue())

    def test_filesystem_errors_are_handled_gracefully(self):
        record = make_record()
        output = io.StringIO()
        with (
            tempfile.TemporaryDirectory() as tmp_dir,
            patch("builtins.input", side_effect=["1"]),
            patch.object(app, "export_route", side_effect=OSError(f"Permission denied for {KEY}")),
            contextlib.redirect_stdout(output),
        ):
            result = app.prompt_export_format_and_save(record, export_dir=tmp_dir, key=KEY)

        self.assertIsNone(result)
        self.assertIn("Could not export route:", output.getvalue())
        self.assertNotIn(KEY, output.getvalue())

    def test_api_keys_never_appear_in_exports_and_no_extra_http_requests_occur(self):
        path = {
            "distance": 1000.0,
            "time": 60000,
            "instructions": [{"text": f"Turn at {KEY} boulevard", "distance": 1000.0}],
        }
        origin = (200, 10.0, 20.0, f"Origin {KEY}")
        destination = (200, 11.0, 21.0, f"Destination {KEY}")
        record = app.create_route_record(path, origin, destination, "car", "metric", key=KEY)

        with tempfile.TemporaryDirectory() as tmp_dir, patch.object(app.requests, "get") as get:
            txt_file = app.export_route_txt(record, export_dir=tmp_dir, key=KEY)
            json_file = app.export_route_json(record, export_dir=tmp_dir, key=KEY)
            csv_file = app.export_route_csv(record, export_dir=tmp_dir, key=KEY)
            get.assert_not_called()

            for exported in (txt_file, json_file, csv_file):
                content = exported.read_text(encoding="utf-8")
                self.assertNotIn(KEY, content)
                self.assertIn("[REDACTED]", content)


if __name__ == "__main__":
    unittest.main()
