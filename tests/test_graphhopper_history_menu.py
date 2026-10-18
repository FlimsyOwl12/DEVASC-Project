"""Offline unit and acceptance tests for Main Menu UX and Session Route History."""

import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from test_graphhopper_cli import app


KEY = "offline-history-key"


def response(data, status=200):
    return Mock(status_code=status, json=Mock(return_value=data))


def sample_record(index=1, units="metric"):
    path = {
        "distance": 1000.0 * index,
        "time": 60000 * index,
        "instructions": [{"text": f"Step for route {index}", "distance": 1000.0 * index}],
    }
    return app.create_route_record(
        path,
        (200, 10.0 + index, 20.0 + index, f"Origin {index}"),
        (200, 30.0 + index, 40.0 + index, f"Destination {index}"),
        profile="car",
        units=units,
        timestamp=f"2026-10-17T18:{index:02d}:00Z",
        key=KEY,
    )


class RouteHistoryAndMenuTests(unittest.TestCase):
    def test_history_stores_only_last_ten_successful_routes(self):
        history = app.RouteHistory(max_size=10)
        for i in range(1, 13):
            history.add(sample_record(i))

        self.assertEqual(len(history), 10)
        entries = history.entries()
        self.assertEqual(entries[0].origin, "Origin 3")
        self.assertEqual(entries[-1].origin, "Origin 12")

    def test_failed_routes_are_not_stored_in_history(self):
        origin_hit = {"hits": [{"name": "Origin", "point": {"lat": 1.0, "lng": 2.0}}]}
        dest_hit = {"hits": [{"name": "Destination", "point": {"lat": 3.0, "lng": 4.0}}]}
        replies = [
            # Attempt 1: origin geocoding returns empty hits
            response({"hits": []}),
            # Attempt 2: origin and destination succeed, but routing fails with HTTP 400
            response(origin_hit),
            response(dest_hit),
            response({"message": "No connection"}, status=400),
        ]
        inputs = [
            "1", "car", "metric", "summary", "Nowhere",
            "1", "car", "metric", "summary", "Origin", "Destination",
            "2",  # View Route History
            "4",  # Exit
        ]
        output = io.StringIO()
        with (
            patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}),
            patch.object(app, "load_dotenv"),
            patch.object(app.requests, "get", side_effect=replies),
            patch("builtins.input", side_effect=inputs),
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(app.main(), 0)

        self.assertIn("No routes in session history yet.", output.getvalue())

    def test_view_route_history_displays_saved_route_without_network_requests(self):
        history = app.RouteHistory()
        history.add(sample_record(1, units="metric"))
        history.add(sample_record(2, units="imperial"))

        output = io.StringIO()
        with (
            patch.object(app.requests, "get") as get,
            patch("builtins.input", side_effect=["invalid", "9", "2"]),
            contextlib.redirect_stdout(output),
        ):
            app.handle_view_history(history)
            get.assert_not_called()

        text = output.getvalue()
        self.assertIn("ROUTE HISTORY", text)
        self.assertIn("1. Origin 1 -> Destination 1 | Profile: car | Distance: 1.0 km", text)
        self.assertIn("2. Origin 2 -> Destination 2 | Profile: car | Distance: 1.2 miles", text)
        self.assertIn("Step for route 2", text)

    def test_export_previous_route_from_history_requires_no_network_requests(self):
        history = app.RouteHistory()
        history.add(sample_record(1, units="metric"))

        output = io.StringIO()
        with (
            tempfile.TemporaryDirectory() as tmp_dir,
            patch.object(app.requests, "get") as get,
            patch("builtins.input", side_effect=["1", "2"]),  # Route #1, format 2 (JSON)
            contextlib.redirect_stdout(output),
        ):
            saved = app.handle_export_history(history, export_dir=tmp_dir, key=KEY)
            get.assert_not_called()
            self.assertIsNotNone(saved)
            self.assertTrue(saved.exists())
            payload = json.loads(saved.read_text(encoding="utf-8"))

        self.assertEqual(payload["origin"], "Origin 1")
        self.assertEqual(payload["destination"], "Destination 1")
        self.assertEqual(payload["instructions"][0]["text"], "Step for route 1")

    def test_end_to_end_menu_navigation_find_view_export_and_exit(self):
        origin_hit = {"hits": [{"name": "Manila", "point": {"lat": 14.5995, "lng": 120.9842}}]}
        dest_hit = {"hits": [{"name": "Makati", "point": {"lat": 14.5547, "lng": 121.0244}}]}
        route_reply = {
            "paths": [{
                "distance": 5000.0,
                "time": 900000,
                "instructions": [{"text": "Drive south", "distance": 5000.0}],
            }]
        }
        replies = [
            response(origin_hit),
            response(dest_hit),
            response(route_reply),
        ]
        inputs = [
            "invalid-menu-choice",  # Invalid main menu entry
            "2",                    # View history when empty
            "3",                    # Export history when empty
            "1",                    # Find a Route
            "car",
            "metric",
            "summary",
            "Manila",
            "Makati",
            "no",                   # Decline immediate export
            "2",                    # View Route History
            "1",                    # Select route 1 to view
            "3",                    # Export Previous Route
            "1",                    # Select route 1 to export
            "1",                    # Export as TXT
            "4",                    # Exit
        ]
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp_dir:
            with (
                patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}),
                patch.object(app, "load_dotenv"),
                patch.object(app.requests, "get", side_effect=replies) as get,
                patch("builtins.input", side_effect=inputs),
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(app.main(export_dir=tmp_dir), 0)
                # Only 3 HTTP requests for the single route generation; 0 for history view/export
                self.assertEqual(get.call_count, 3)

            exported_files = list(Path(tmp_dir).glob("*.txt"))
            self.assertEqual(len(exported_files), 1)
            exported_content = exported_files[0].read_text(encoding="utf-8")

        text = output.getvalue()
        self.assertIn("DEVASC ROUTE FINDER", text)
        self.assertIn("Invalid option. Please choose 1, 2, 3, or 4.", text)
        self.assertIn("No routes in session history yet.", text)
        self.assertIn("Drive south", text)  # Shown when viewing from history
        self.assertIn("Drive south", exported_content)
        self.assertNotIn(KEY, text)
        self.assertNotIn(KEY, exported_content)

    def test_cancel_and_eof_interrupt_exit_cleanly(self):
        for exc in (EOFError, KeyboardInterrupt):
            output = io.StringIO()
            with (
                self.subTest(exception=exc),
                patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY}),
                patch.object(app, "load_dotenv"),
                patch("builtins.input", side_effect=exc),
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(app.main(), 0)
            self.assertIn("Exiting.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
