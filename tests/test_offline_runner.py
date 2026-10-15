"""Check the CI command's credential isolation, network guard, and exit codes."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


RUNNER = Path(__file__).resolve().parents[1] / "scripts/run_offline_tests.py"


class OfflineRunnerTests(unittest.TestCase):
    def run_fixture(self, source):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "tests").mkdir()
            shutil.copyfile(RUNNER, root / "scripts/run_offline_tests.py")
            (root / ".env").write_text("GRAPHHOPPER_API_KEY=file-sentinel\n", encoding="utf-8")
            if source is not None:
                (root / "tests/test_fixture.py").write_text(source, encoding="utf-8")
            environment = dict(os.environ, GRAPHHOPPER_API_KEY="exported-sentinel")
            result = subprocess.run(
                [sys.executable, str(root / "scripts/run_offline_tests.py")],
                cwd=directory, env=environment, capture_output=True, text=True, timeout=30,
            )
            report = (root / "test-results/unittest.txt").read_text(encoding="utf-8")
            return result, report

    def test_key_and_dotenv_are_disabled_while_mocks_still_work(self):
        result, report = self.run_fixture('''import os
import socket
import unittest
from unittest.mock import patch
from dotenv import load_dotenv
import requests

class Fixture(unittest.TestCase):
    def test_isolation(self):
        load_dotenv()
        self.assertEqual(os.environ['GRAPHHOPPER_API_KEY'], '')
        self.assertEqual(os.environ['PYTHON_DOTENV_DISABLED'], '1')
        with patch('requests.get', return_value='mocked'):
            self.assertEqual(requests.get('https://example.invalid'), 'mocked')
        with self.assertRaisesRegex(AssertionError, 'Network access is disabled'):
            socket.create_connection(('127.0.0.1', 9))
        with self.assertRaisesRegex(AssertionError, 'Network access is disabled'):
            socket.socket.connect(None, ('127.0.0.1', 9))
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK", report)
        self.assertNotIn("exported-sentinel", report)
        self.assertNotIn("file-sentinel", report)

    def test_failure_has_nonzero_status_and_saved_diagnostics(self):
        result, report = self.run_fixture('''import unittest
class Fixture(unittest.TestCase):
    def test_failure(self):
        self.fail('deliberate CI failure')
''')
        self.assertEqual(result.returncode, 1)
        self.assertIn("deliberate CI failure", report)
        self.assertIn("FAILED", report)

    def test_unmocked_http_fails_without_sending_request(self):
        result, report = self.run_fixture('''import unittest
import requests
class Fixture(unittest.TestCase):
    def test_unmocked_http(self):
        requests.get('https://example.invalid', timeout=1)
''')
        self.assertEqual(result.returncode, 1)
        self.assertIn("Network access is disabled", report)

    def test_empty_suite_fails_instead_of_passing_silently(self):
        result, report = self.run_fixture(None)
        self.assertEqual(result.returncode, 1)
        self.assertIn("No tests were discovered", report)


if __name__ == "__main__":
    unittest.main()
