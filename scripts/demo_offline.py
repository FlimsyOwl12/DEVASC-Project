"""Replay the enhanced CLI with synthetic data and no live HTTP requests."""

import argparse
from contextlib import ExitStack, redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
KEY = "offline-demo-key"


def reply(data):
    return Mock(status_code=200, json=Mock(return_value=data))


def blocked(*args, **kwargs):
    raise AssertionError("Live network access is disabled for the offline demo.")


def run_demo(export_dir):
    script = ROOT / "labs/devnet-src/graphhopper/graphhopper_parse-json_7.py"
    spec = importlib.util.spec_from_file_location("graphhopper_demo", script)
    app = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = app
    spec.loader.exec_module(app)
    origins = {"hits": [
        {"name": "Central Park", "city": "Example City", "point": {"lat": 10.0, "lng": 20.0}},
        {"name": "Central Park", "city": "Example City", "point": {"lat": 11.0, "lng": 21.0}},
    ]}
    destination = {"hits": [{"name": "Demo Destination", "point": {"lat": 12.0, "lng": 22.0}}]}
    route = {"paths": [{"distance": 3218.688, "time": 600000, "instructions": [
        {"text": "Turn left onto Example Street", "distance": 1609.344},
        {"text": "Arrive at Demo Destination", "distance": 1609.344},
    ]}]}
    choices = iter([
        "1", "car", "imperial", "detailed", "Central Park", "2", "Demo Destination",
        "yes", "2",  # Immediate JSON export.
        "2", "1",   # View the route from session history.
        "3", "1", "1",  # TXT export from history.
        "3", "1", "3",  # CSV export from history.
        "4",
    ])

    def answer(prompt):
        value = next(choices)
        print(prompt + value)
        return value

    capture = io.StringIO()
    with ExitStack() as stack:
        stack.enter_context(patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": KEY, "PYTHON_DOTENV_DISABLED": "1"}))
        stack.enter_context(patch.object(app, "load_dotenv", return_value=False))
        stack.enter_context(patch("requests.sessions.Session.request", side_effect=blocked))
        stack.enter_context(patch("socket.create_connection", side_effect=blocked))
        stack.enter_context(patch("socket.socket.connect", side_effect=blocked))
        stack.enter_context(patch("socket.socket.connect_ex", side_effect=blocked))
        get = stack.enter_context(patch.object(app.requests, "get", side_effect=[reply(origins), reply(destination), reply(route)]))
        stack.enter_context(patch("builtins.input", side_effect=answer))
        stack.enter_context(redirect_stdout(capture))
        result = app.main(export_dir=export_dir)
    assert result == 0 and get.call_count == 3
    assert "point=11.0%2C21.0" in get.call_args_list[2].args[0]
    text = capture.getvalue()
    assert KEY not in text
    json_files = list(Path(export_dir).glob("*.json"))
    assert len(json_files) == 1
    payload = json.loads(json_files[0].read_text())
    assert payload["distance"]["formatted"] == "2.0 miles"
    assert payload["duration"]["formatted"] == "00:10:00"
    assert len(payload["instructions"]) == 2
    for extension in ("txt", "json", "csv"):
        files = list(Path(export_dir).glob("*." + extension))
        assert len(files) == 1 and KEY not in files[0].read_text()
    print(text)
    print("Verified: selected coordinates, 2.0 miles, 00:10:00, TXT/JSON/CSV, and no extra HTTP for history.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep-exports", action="store_true", help="Keep synthetic exports in a new temporary directory.")
    args = parser.parse_args()
    print("OFFLINE DEMONSTRATION — SYNTHETIC DATA; NO LIVE GRAPHHOPPER REQUESTS")
    if args.keep_exports:
        directory = tempfile.mkdtemp(prefix="devasc-demo-")
        run_demo(directory)
        print("Synthetic exports retained at:", directory)
    else:
        with tempfile.TemporaryDirectory(prefix="devasc-demo-") as directory:
            run_demo(directory)
        print("Temporary synthetic exports removed. Use --keep-exports to inspect them afterward.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
