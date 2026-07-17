import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.tools.architecture_module_classifier import classify_runtime_modules
from ashl_core_v1.tools.architecture_test_mapper import build_test_coverage_map


class ArchitectureModuleClassifierTests(unittest.TestCase):
    def test_classifier_distinguishes_runtime_schema_cli_and_test_harness(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = root / "ashl_core_v1" / "runtime"
            tests = root / "ashl_core_v1" / "tests"
            runtime.mkdir(parents=True)
            tests.mkdir(parents=True)
            (runtime / "sample_runtime.py").write_text(
                """
from ashl_core_v1.runtime.sample_schema import SampleRecord

def run_session():
    return SampleRecord("x")
""",
                encoding="utf-8",
            )
            (runtime / "sample_schema.py").write_text(
                """
from dataclasses import dataclass

@dataclass(frozen=True)
class SampleRecord:
    sample_id: str
""",
                encoding="utf-8",
            )
            (runtime / "sample_cli.py").write_text(
                """
import argparse
def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_subparsers().add_parser("run-sample")
    return parser
""",
                encoding="utf-8",
            )
            (tests / "test_sample_runtime.py").write_text(
                """
from ashl_core_v1.runtime.sample_runtime import run_session
def test_run_session(): assert run_session().sample_id == "x"
""",
                encoding="utf-8",
            )

            test_records = build_test_coverage_map(root)
            records = {record.module_path: record for record in classify_runtime_modules(root, test_records=test_records)}

            self.assertEqual(records["ashl_core_v1.runtime.sample_runtime"].implementation_status, "actual_runtime")
            self.assertEqual(records["ashl_core_v1.runtime.sample_schema"].implementation_status, "schema_only")
            self.assertEqual(records["ashl_core_v1.runtime.sample_cli"].implementation_status, "actual_cli")
            self.assertTrue(records["ashl_core_v1.runtime.sample_runtime"].verified_by_tests)
            self.assertIn("runtime_behavior_not_established_by_schema", records["ashl_core_v1.runtime.sample_schema"].blocked_capabilities)


if __name__ == "__main__":
    unittest.main()
