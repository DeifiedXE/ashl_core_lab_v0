import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.raising_threshold_review import (
    CURRENT_ALLOWED_CLAIM,
    CURRENT_NOT_YET_CLAIM,
    build_raising_threshold_review,
    write_raising_threshold_review_report,
)


class RaisingThresholdReviewTests(unittest.TestCase):
    def test_review_builder_returns_dict(self):
        review = build_raising_threshold_review()

        self.assertIsInstance(review, dict)
        self.assertEqual("ASHL Core v1 Raising Threshold Review Minimal v0", review["title"])

    def test_all_threshold_keys_exist(self):
        thresholds = build_raising_threshold_review()["thresholds"]

        for key in (
            "fixed_cradle_operation_ready",
            "manual_daily_cli_ready",
            "backup_restore_ready",
            "teacher_correction_ready",
            "first_output_candidate_trace_ready",
            "controlled_growth_minimum_ready",
            "daily_no_codex_fixed_case_ready",
            "open_ended_cradle_life_ready",
            "long_term_cultivation_ready",
        ):
            with self.subTest(key=key):
                self.assertIn(key, thresholds)

    def test_manual_daily_cli_ready_can_be_true_when_package_surfaces_are_detected(self):
        thresholds = build_raising_threshold_review()["thresholds"]

        self.assertTrue(thresholds["manual_daily_cli_ready"])

    def test_daily_no_codex_fixed_case_ready_mirrors_manual_daily_cli_ready(self):
        thresholds = build_raising_threshold_review()["thresholds"]

        self.assertEqual(
            thresholds["manual_daily_cli_ready"],
            thresholds["daily_no_codex_fixed_case_ready"],
        )

    def test_open_ended_cradle_life_ready_is_false(self):
        thresholds = build_raising_threshold_review()["thresholds"]

        self.assertFalse(thresholds["open_ended_cradle_life_ready"])

    def test_long_term_cultivation_ready_is_false(self):
        thresholds = build_raising_threshold_review()["thresholds"]

        self.assertFalse(thresholds["long_term_cultivation_ready"])

    def test_report_writer_creates_markdown_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "threshold.md"

            result = write_raising_threshold_review_report(path)

            self.assertEqual(str(path), result["path"])
            self.assertTrue(path.is_file())

    def test_report_includes_current_allowed_claim(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "threshold.md"
            write_raising_threshold_review_report(path)

            self.assertIn(CURRENT_ALLOWED_CLAIM, path.read_text(encoding="utf-8"))

    def test_report_includes_current_not_yet_claim(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "threshold.md"
            write_raising_threshold_review_report(path)
            text = path.read_text(encoding="utf-8")

            for claim in CURRENT_NOT_YET_CLAIM:
                with self.subTest(claim=claim):
                    self.assertIn(claim, text)

    def test_report_includes_next_recommended_packages(self):
        review = build_raising_threshold_review()

        for index in range(21, 26):
            with self.subTest(index=index):
                self.assertIn(f"Package {index}", review["next_recommended_packages"])


if __name__ == "__main__":
    unittest.main()
