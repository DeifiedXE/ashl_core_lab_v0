import unittest
from pathlib import Path

from ashl_core_v1.tools.architecture_repo_scanner import run_architecture_scan


class ArchitecturePackage123GoNoGoTests(unittest.TestCase):
    _scan = None

    @classmethod
    def scan(cls):
        if cls._scan is None:
            cls._scan = run_architecture_scan(Path(__file__).resolve().parents[2])
        return cls._scan

    def test_package_123_go_no_go_reads_actual_package_122_and_cross_process_bindings(self):
        scan = self.scan()
        record = scan["analysis"]["package_123_go_no_go"]
        self.assertTrue(record["package_122_runtime_valid"])
        self.assertTrue(record["perception_lineage_valid"])
        self.assertTrue(record["teacher_gate_path_valid"])
        self.assertTrue(record["cross_process_growth_path_valid"])
        self.assertTrue(record["missing_live_experience_data_only"])
        self.assertTrue(record["package_123_go"])
        self.assertEqual(record["architecture_blockers"], [])


if __name__ == "__main__":
    unittest.main()
