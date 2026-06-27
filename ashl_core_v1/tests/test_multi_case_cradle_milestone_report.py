import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.cradle_cases import list_cradle_case_ids
from ashl_core_v1.runtime.milestone_report import (
    build_multi_case_cradle_milestone_report,
    write_multi_case_cradle_milestone_report,
)


class MultiCaseCradleMilestoneReportTests(unittest.TestCase):
    def test_report_builder_returns_dict(self):
        report = build_multi_case_cradle_milestone_report()

        self.assertIsInstance(report, dict)
        self.assertEqual("complete", report["status"])

    def test_report_includes_package_1_through_package_10(self):
        package_range = build_multi_case_cradle_milestone_report()["package_range"]

        for index in range(1, 11):
            with self.subTest(index=index):
                self.assertIn(f"Package {index}", package_range)

    def test_report_includes_all_cradle_case_ids(self):
        report = build_multi_case_cradle_milestone_report()

        self.assertEqual(set(list_cradle_case_ids()), set(report["case_inventory"]))

    def test_report_includes_current_allowed_claim(self):
        report = build_multi_case_cradle_milestone_report()

        self.assertIn("ASHL Core v1 can run fixed first-stage cradle circulation cases", report["current_allowed_claim"])
        self.assertIn("清音 v1 現在可以", report["current_allowed_claim_zh"])

    def test_report_includes_current_not_yet_claim(self):
        report = build_multi_case_cradle_milestone_report()

        self.assertIn("This is not free runtime.", report["current_not_yet_claim"])
        self.assertIn("這還不是清音正式開始生活。", report["current_not_yet_claim_zh"])

    def test_report_includes_next_recommended_packages(self):
        report = build_multi_case_cradle_milestone_report()

        for index in range(11, 16):
            with self.subTest(index=index):
                self.assertIn(f"Package {index}", report["next_recommended_packages"])

    def test_write_function_creates_markdown_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "report.md"

            result = write_multi_case_cradle_milestone_report(str(path))

            self.assertEqual(str(path), result["path"])
            self.assertTrue(path.is_file())

    def test_markdown_report_contains_title(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "report.md"
            write_multi_case_cradle_milestone_report(str(path))

            self.assertIn("# ASHL Core v1 Multi-Case Cradle Milestone Report v0", path.read_text(encoding="utf-8"))

    def test_markdown_report_contains_case_inventory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "report.md"
            write_multi_case_cradle_milestone_report(str(path))
            text = path.read_text(encoding="utf-8")

            for case_id in list_cradle_case_ids():
                with self.subTest(case_id=case_id):
                    self.assertIn(case_id, text)

    def test_markdown_report_contains_current_allowed_claim(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "report.md"
            write_multi_case_cradle_milestone_report(str(path))
            text = path.read_text(encoding="utf-8")

            self.assertIn("ASHL Core v1 can run fixed first-stage cradle circulation cases", text)


if __name__ == "__main__":
    unittest.main()
