import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.tools.architecture_test_mapper import build_test_coverage_map


class ArchitectureTestMapperTests(unittest.TestCase):
    def test_test_mapper_links_direct_integration_negative_and_lineage_tests(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = root / "ashl_core_v1" / "runtime"
            tests = root / "ashl_core_v1" / "tests"
            runtime.mkdir(parents=True)
            tests.mkdir(parents=True)
            (runtime / "sample_runtime.py").write_text("def run(): return True\n", encoding="utf-8")
            (tests / "test_sample_runtime.py").write_text(
                """
from ashl_core_v1.runtime.sample_runtime import run

def test_positive_and_negative_lineage():
    assert run()
    assert "source_trace_refs"
    assert "reject invalid missing wrong"
""",
                encoding="utf-8",
            )

            records = {record.module_path: record for record in build_test_coverage_map(root)}
            record = records["ashl_core_v1.runtime.sample_runtime"]
            self.assertTrue(record.direct_test_files)
            self.assertGreater(record.positive_case_count, 0)
            self.assertGreater(record.negative_case_count, 0)
            self.assertTrue(record.lineage_tested)
            self.assertEqual(record.coverage_status, "verified_by_tests")


if __name__ == "__main__":
    unittest.main()
