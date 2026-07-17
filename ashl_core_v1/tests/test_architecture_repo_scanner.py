import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.tools.architecture_repo_scanner import scan_repo_baseline


class ArchitectureRepoScannerTests(unittest.TestCase):
    def test_repo_scanner_discovers_counts_and_works_without_git(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = root / "ashl_core_v1" / "runtime"
            tests = root / "ashl_core_v1" / "tests"
            docs = root / "ashl_core_v1" / "docs"
            runtime.mkdir(parents=True)
            tests.mkdir(parents=True)
            docs.mkdir(parents=True)
            (runtime / "sample_cli.py").write_text(
                """
import argparse
import sqlite3
from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class SampleRecord:
    schema_version: str = "ashl_sample_record_v0"

class SampleStatus(str, Enum):
    READY = "ready"

def validate_sample() -> bool:
    return True

def build_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    sub.add_parser("show-sample")
    return parser

SQL = "CREATE TABLE IF NOT EXISTS sample_records (sample_id TEXT PRIMARY KEY)"
""",
                encoding="utf-8",
            )
            (tests / "test_sample_cli.py").write_text("def test_ok(): assert True\n", encoding="utf-8")
            (docs / "sample.md").write_text("# Sample\n", encoding="utf-8")

            first = scan_repo_baseline(root)
            second = scan_repo_baseline(root)

            self.assertIsNone(first.scanned_commit)
            self.assertGreaterEqual(first.python_file_count, 2)
            self.assertEqual(first.runtime_module_count, 1)
            self.assertEqual(first.test_file_count, 1)
            self.assertEqual(first.document_file_count, 1)
            self.assertEqual(first.dataclass_count, 1)
            self.assertEqual(first.enum_count, 1)
            self.assertEqual(first.validator_count, 1)
            self.assertEqual(first.cli_command_count, 1)
            self.assertEqual(first.sqlite_table_count, 1)
            self.assertEqual(first.scan_result_sha256, second.scan_result_sha256)


if __name__ == "__main__":
    unittest.main()
