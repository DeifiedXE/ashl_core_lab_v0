import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.memory_influence_dry_run_contrast_minimal import (
    build_memory_influence_dry_run_contrast,
    run_memory_influence_dry_run_contrast_minimal_check,
    validate_memory_influence_dry_run_contrast,
)
from ashl_core.memory_influenced_action_tendency_preview_minimal import (
    run_memory_influenced_action_tendency_preview_minimal_check,
)
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "contrast_id",
    "source_memory_tendency_preview_id",
    "target_action_tendency",
    "contrast_result",
    "preview_only",
    "human_summary",
    "blocked_flags",
}

BLOCKED_FLAG_ERRORS = {
    "final_action_created": "final_action_created_enabled",
    "direct_action_command": "direct_action_command_enabled",
    "runtime_action_selection": "runtime_action_selection_enabled",
    "action_selection_influence": "action_selection_influence_enabled",
    "action_behavior_changed": "action_behavior_changed_enabled",
    "exploration_blocked": "exploration_blocked_enabled",
    "curiosity_overridden": "curiosity_overridden_enabled",
    "mentor_override_blocked": "mentor_override_blocked_enabled",
    "lesson_applied": "lesson_applied_enabled",
    "memory_write": "memory_write_enabled",
    "new_retention_written": "new_retention_written_enabled",
    "predictor_modified": "predictor_modified_enabled",
    "proof_of_learning_claim": "proof_of_learning_claim_enabled",
}


class MemoryInfluenceDryRunContrastMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        preview_result = run_memory_influenced_action_tendency_preview_minimal_check()
        cls.increase_preview = next(
            preview
            for preview, validation in zip(
                preview_result["memory_influenced_action_tendency_previews"],
                preview_result["validation_results"],
            )
            if validation["valid"] and validation["increase_preview"]
        )
        cls.decrease_preview = next(
            preview
            for preview, validation in zip(
                preview_result["memory_influenced_action_tendency_previews"],
                preview_result["validation_results"],
            )
            if validation["valid"] and validation["decrease_preview"]
        )
        cls.none_preview = deepcopy(cls.increase_preview)
        cls.none_preview["tendency_preview_id"] = f"{cls.none_preview['tendency_preview_id']}:none"
        cls.none_preview["preview_delta"]["memory_delta"] = 0.0
        cls.none_preview["preview_delta"]["preview_score"] = cls.none_preview["preview_delta"]["baseline_score"]

    def _valid_contrast(self):
        return build_memory_influence_dry_run_contrast(self.increase_preview)

    def test_valid_increase_contrast_is_created(self):
        contrast = self._valid_contrast()
        validation = validate_memory_influence_dry_run_contrast(contrast)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(contrast["contrast_result"]["baseline_score"], 0.5)
        self.assertEqual(contrast["contrast_result"]["memory_influenced_score"], 0.6)
        self.assertEqual(contrast["contrast_result"]["delta"], 0.1)
        self.assertEqual(contrast["contrast_result"]["direction"], "increase")
        self.assertTrue(contrast["contrast_result"]["visible_tendency_difference"])

    def test_valid_decrease_contrast_is_created(self):
        contrast = build_memory_influence_dry_run_contrast(self.decrease_preview)
        validation = validate_memory_influence_dry_run_contrast(contrast)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(contrast["contrast_result"]["delta"], -0.1)
        self.assertEqual(contrast["contrast_result"]["direction"], "decrease")
        self.assertTrue(contrast["contrast_result"]["visible_tendency_difference"])

    def test_valid_none_contrast_is_created(self):
        contrast = build_memory_influence_dry_run_contrast(self.none_preview)
        validation = validate_memory_influence_dry_run_contrast(contrast)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(contrast["contrast_result"]["delta"], 0.0)
        self.assertEqual(contrast["contrast_result"]["direction"], "none")
        self.assertFalse(contrast["contrast_result"]["visible_tendency_difference"])

    def test_record_has_only_expected_top_level_fields(self):
        contrast = self._valid_contrast()

        self.assertEqual(set(contrast), EXPECTED_FIELDS)
        self.assertEqual(len(contrast), 7)

    def test_delta_must_match_score_difference(self):
        contrast = self._valid_contrast()
        contrast["contrast_result"]["delta"] = 0.2
        self._assert_invalid(contrast, "delta_mismatch")

    def test_direction_must_match_delta(self):
        contrast = self._valid_contrast()
        contrast["contrast_result"]["direction"] = "decrease"
        self._assert_invalid(contrast, "direction_mismatch")

    def test_visible_tendency_difference_must_match_delta(self):
        contrast = self._valid_contrast()
        contrast["contrast_result"]["visible_tendency_difference"] = False
        self._assert_invalid(contrast, "visible_tendency_difference_mismatch")

    def test_preview_only_false_blocks(self):
        contrast = self._valid_contrast()
        contrast["preview_only"] = False
        self._assert_invalid(contrast, "preview_only_not_true")

    def test_score_bounds_are_enforced(self):
        cases = [
            ("baseline_score", -0.01, "baseline_score_below_min"),
            ("baseline_score", 1.01, "baseline_score_above_max"),
            ("memory_influenced_score", -0.01, "memory_score_below_min"),
            ("memory_influenced_score", 1.01, "memory_score_above_max"),
        ]
        for field, value, error_code in cases:
            with self.subTest(field=field, value=value):
                contrast = self._valid_contrast()
                contrast["contrast_result"][field] = value
                self._assert_invalid(contrast, error_code)

    def test_empty_before_blocks(self):
        contrast = self._valid_contrast()
        contrast["human_summary"]["before"] = ""
        self._assert_invalid(contrast, "before_empty_or_not_string")

    def test_empty_plain_result_blocks(self):
        contrast = self._valid_contrast()
        contrast["human_summary"]["plain_result"] = ""
        self._assert_invalid(contrast, "plain_result_empty_or_not_string")

    def test_blocked_flags_true_block(self):
        for flag, error_code in BLOCKED_FLAG_ERRORS.items():
            with self.subTest(flag=flag):
                contrast = self._valid_contrast()
                contrast["blocked_flags"][flag] = True
                self._assert_invalid(contrast, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_memory_influence_dry_run_contrast_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-memory-influence-dry-run-contrast-minimal-check")
        self.assertEqual(result["flow"], "memory_influence_dry_run_contrast_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["memory_influence_dry_run_contrast_count"], 26)
        self.assertEqual(summary["valid_memory_influence_dry_run_contrast_count"], 3)
        self.assertEqual(summary["invalid_memory_influence_dry_run_contrast_count"], 23)
        self.assertEqual(summary["increase_contrast_count"], 1)
        self.assertEqual(summary["decrease_contrast_count"], 1)
        self.assertEqual(summary["none_contrast_count"], 1)
        self.assertEqual(summary["visible_tendency_difference_count"], 2)
        self.assertEqual(summary["preview_only_false_blocked_count"], 1)
        self.assertEqual(summary["baseline_score_low_blocked_count"], 1)
        self.assertEqual(summary["baseline_score_high_blocked_count"], 1)
        self.assertEqual(summary["memory_score_low_blocked_count"], 1)
        self.assertEqual(summary["memory_score_high_blocked_count"], 1)
        self.assertEqual(summary["wrong_delta_blocked_count"], 1)
        self.assertEqual(summary["wrong_direction_blocked_count"], 1)
        self.assertEqual(summary["wrong_visible_difference_blocked_count"], 1)
        self.assertEqual(summary["empty_before_blocked_count"], 1)
        self.assertEqual(summary["empty_plain_result_blocked_count"], 1)
        for field in BLOCKED_FLAG_ERRORS:
            blocked_key = f"{field}_blocked_count"
            if field == "exploration_blocked":
                blocked_key = "exploration_blocked_count"
            if field == "mentor_override_blocked":
                blocked_key = "mentor_override_blocked_count"
            self.assertEqual(summary[blocked_key], 1)
        self.assertEqual(summary["final_action_created_count"], 0)
        self.assertEqual(summary["direct_action_command_count"], 0)
        self.assertEqual(summary["runtime_action_selection_count"], 0)
        self.assertEqual(summary["action_behavior_changed_count"], 0)
        self.assertTrue(boundary["preview_only"])
        self.assertTrue(boundary["trace_level_contrast_only"])
        self.assertTrue(boundary["memory_influence_may_be_contrasted_not_control_behavior"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-memory-influence-dry-run-contrast-minimal-check")

        self.assertEqual(result["command"], "run-memory-influence-dry-run-contrast-minimal-check")
        self.assertEqual(result["summary"]["valid_memory_influence_dry_run_contrast_count"], 3)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-memory-influence-dry-run-contrast-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-memory-influence-dry-run-contrast-minimal-check")
        self.assertEqual(result["summary"]["memory_influence_dry_run_contrast_count"], 26)

    def _assert_invalid(self, contrast, error_code):
        validation = validate_memory_influence_dry_run_contrast(contrast)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
