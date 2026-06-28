import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.long_term_cultivation_gap_report import (
    CURRENT_ALLOWED_CLAIM,
    CURRENT_NOT_YET_CLAIM,
    build_long_term_cultivation_gap_report,
    write_long_term_cultivation_gap_report,
)


class LongTermCultivationGapReportTests(unittest.TestCase):
    def test_gap_report_builder_returns_dict(self):
        report = build_long_term_cultivation_gap_report()

        self.assertIsInstance(report, dict)
        self.assertEqual("ASHL Core v1 Long-Term Cultivation Gap Report Minimal v0", report["title"])

    def test_readiness_keys_exist(self):
        report = build_long_term_cultivation_gap_report()

        self.assertIn("manual_fixed_daily_ready", report)
        self.assertIn("first_output_record_ready", report)
        self.assertIn("continuity_stress_ready", report)

    def test_long_term_cultivation_ready_is_false(self):
        report = build_long_term_cultivation_gap_report()

        self.assertFalse(report["long_term_cultivation_ready"])

    def test_gap_items_include_required_gaps(self):
        report = build_long_term_cultivation_gap_report()

        self.assertIn("open_ended_cradle_life", report["gap_items"])
        self.assertIn("long_horizon_memory_promotion", report["gap_items"])
        self.assertIn("Unity_Home_integration", report["gap_items"])

    def test_write_report_creates_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "gap.md"

            result = write_long_term_cultivation_gap_report(path)

            self.assertEqual(str(path), result["path"])
            self.assertTrue(path.is_file())

    def test_markdown_includes_current_allowed_claim(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "gap.md"
            write_long_term_cultivation_gap_report(path)

            self.assertIn(CURRENT_ALLOWED_CLAIM, path.read_text(encoding="utf-8"))

    def test_markdown_includes_current_not_yet_claim(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "gap.md"
            write_long_term_cultivation_gap_report(path)
            text = path.read_text(encoding="utf-8")

            for claim in CURRENT_NOT_YET_CLAIM:
                with self.subTest(claim=claim):
                    self.assertIn(claim, text)

    def test_markdown_includes_next_recommended_packages(self):
        report = build_long_term_cultivation_gap_report()

        for index in range(26, 31):
            with self.subTest(index=index):
                self.assertIn(f"Package {index}", report["next_recommended_packages"])


if __name__ == "__main__":
    unittest.main()
