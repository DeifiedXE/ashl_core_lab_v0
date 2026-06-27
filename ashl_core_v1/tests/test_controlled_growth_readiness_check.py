import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.growth_readiness import (
    CURRENT_ALLOWED_CLAIM,
    CURRENT_NOT_YET_CLAIM,
    build_controlled_growth_readiness_check,
    write_controlled_growth_readiness_report,
)


class ControlledGrowthReadinessCheckTests(unittest.TestCase):
    def test_readiness_check_returns_dict(self):
        report = build_controlled_growth_readiness_check()

        self.assertIsInstance(report, dict)
        self.assertIn("checked_capabilities", report)

    def test_all_expected_readiness_keys_exist(self):
        capabilities = build_controlled_growth_readiness_check()["checked_capabilities"]

        for key in (
            "data_shapes_ready",
            "multi_case_cradle_ready",
            "review_cli_ready",
            "memory_trace_query_ready",
            "review_routing_matrix_ready",
            "summary_cli_ready",
            "session_persistence_ready",
            "session_start_close_ready",
            "session_replay_ready",
            "teacher_correction_ready",
            "controlled_growth_minimum_ready",
            "daily_no_codex_ready",
        ):
            with self.subTest(key=key):
                self.assertIn(key, capabilities)

    def test_controlled_growth_minimum_ready_is_true_when_required_components_exist(self):
        capabilities = build_controlled_growth_readiness_check()["checked_capabilities"]

        self.assertTrue(capabilities["controlled_growth_minimum_ready"])

    def test_daily_no_codex_ready_is_false(self):
        capabilities = build_controlled_growth_readiness_check()["checked_capabilities"]

        self.assertFalse(capabilities["daily_no_codex_ready"])

    def test_write_report_creates_markdown_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "readiness.md"

            result = write_controlled_growth_readiness_report(path)

            self.assertEqual(str(path), result["path"])
            self.assertTrue(path.is_file())

    def test_report_includes_current_allowed_claim(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "readiness.md"
            write_controlled_growth_readiness_report(path)
            text = path.read_text(encoding="utf-8")

            self.assertIn(CURRENT_ALLOWED_CLAIM, text)

    def test_report_includes_current_not_yet_claim(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "readiness.md"
            write_controlled_growth_readiness_report(path)
            text = path.read_text(encoding="utf-8")

            for claim in CURRENT_NOT_YET_CLAIM:
                with self.subTest(claim=claim):
                    self.assertIn(claim, text)

    def test_report_includes_next_recommended_packages(self):
        report = build_controlled_growth_readiness_check()

        for index in range(16, 21):
            with self.subTest(index=index):
                self.assertIn(f"Package {index}", report["next_recommended_packages"])

    def test_report_includes_ready_items_and_not_ready_items(self):
        report = build_controlled_growth_readiness_check()

        self.assertIn("controlled_growth_minimum_ready", report["ready_items"])
        self.assertIn("daily_no_codex_ready", report["not_ready_items"])


if __name__ == "__main__":
    unittest.main()
