import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.package_124_source_audit import inspect_package_124_source


class Package124SourceAuditTests(unittest.TestCase):
    def test_inspect_source_reports_missing_databases_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = inspect_package_124_source(Path(tmp), expected_commit="8c38918")
            self.assertTrue(result["source_state_dir_exists"])
            self.assertTrue(result["expected_commit_verified"])
            self.assertFalse(result["databases"]["package_123"]["exists"])


if __name__ == "__main__":
    unittest.main()
