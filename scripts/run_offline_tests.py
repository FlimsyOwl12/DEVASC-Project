"""Run unittest checks without reading .env files or opening network connections."""

from contextlib import ExitStack, redirect_stderr, redirect_stdout
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


class Tee:
    def __init__(self, console, report):
        self.console = console
        self.report = report

    def write(self, text):
        self.console.write(text)
        self.report.write(text)

    def flush(self):
        self.console.flush()
        self.report.flush()


def block_network(*args, **kwargs):
    raise AssertionError("Network access is disabled: mock HTTP calls in offline tests.")


def main():
    report_dir = ROOT / "test-results"
    report_dir.mkdir(exist_ok=True)
    with (report_dir / "unittest.txt").open("w", encoding="utf-8") as report:
        output = Tee(sys.stderr, report)
        with ExitStack() as stack:
            stack.enter_context(redirect_stdout(output))
            stack.enter_context(redirect_stderr(output))
            stack.enter_context(patch.dict(os.environ, {
                "GRAPHHOPPER_API_KEY": "",
                "PYTHON_DOTENV_DISABLED": "1",
            }))
            stack.enter_context(patch("dotenv.load_dotenv", return_value=False))
            # Guard discovery as well as execution. Tests may still mock requests.get.
            stack.enter_context(patch("requests.sessions.Session.request", side_effect=block_network))
            stack.enter_context(patch("socket.create_connection", side_effect=block_network))
            stack.enter_context(patch("socket.socket.connect", side_effect=block_network))
            stack.enter_context(patch("socket.socket.connect_ex", side_effect=block_network))
            suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
            if suite.countTestCases() == 0:
                print("ERROR: No tests were discovered.")
                return 1
            result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
            return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
