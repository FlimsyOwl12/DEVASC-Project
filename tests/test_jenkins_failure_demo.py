"""Intentional failure on a disposable branch; never merge this into main."""

import unittest


class JenkinsFailureDemonstration(unittest.TestCase):
    def test_intentional_failure_for_jenkins_evidence(self):
        self.fail(
            "Intentional Jenkins demonstration failure; "
            "revert this demo commit to recover."
        )
