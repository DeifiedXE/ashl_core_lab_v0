import json
import subprocess
import sys
import unittest

from ashl_core.memory_influence_candidate_preview_minimal import (
    run_memory_influence_candidate_preview_minimal_check,
)
from ashl_core.memory_influenced_action_tendency_preview_minimal import (
    build_memory_influenced_action_tendency_preview,
    run_memory_influenced_action_tendency_preview_minimal_check,
    validate_memory_influenced_action_tendency_preview,
)
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "tendency_preview_id",
    "source_memory_influence_candidate_id",
    "target_action_tendency",
    "preview_delta",
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


class MemoryInfluencedActionTendencyPreviewMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        candidate_result = run_memory_influence_candidate_preview_minimal_check()
        cls.increase_candidate = next(
            candidate
            for candidate, validation in zip(
                candidate_result["memory_influence_candidates"],
                candidate_result["validation_results"],
            )
            if validation["valid"] and validation["increase_tendency"]
        )
        cls.decrease_candidate = next(
            candidate
            for candidate, validation in zip(
                candidate_result["memory_influence_candidates"],
                candidate_result["validation_results"],
            )
            if validation["valid"] and validation["decrease_tendency"]
        )

    def _valid_preview(self):
        return build_memory_influenced_action_tendency_preview(self.increase_candidate)

    def test_valid_increase_preview_is_created(self):
        preview = self._valid_preview()
        validation = validate_memory_influenced_action_tendency_preview(preview)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(preview["preview_delta"]["baseline_score"], 0.5)
        self.assertEqual(preview["preview_delta"]["memory_delta"], 0.1)
        self.assertEqual(preview["preview_delta"]["preview_score"], 0.6)
        self.assertEqual(preview["preview_delta"]["influence_direction"], "increase")

    def test_valid_decrease_preview_is_created(self):
        preview = build_memory_influenced_action_tendency_preview(self.decrease_candidate)
        validation = validate_memory_influenced_action_tendency_preview(preview)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(preview["preview_delta"]["memory_delta"], -0.1)
        self.assertEqual(preview["preview_delta"]["preview_score"], 0.4)
        self.assertEqual(preview["preview_delta"]["influence_direction"], "decrease")

    def test_record_has_only_expected_top_level_fields(self):
        preview = self._valid_preview()

        self.assertEqual(set(preview), EXPECTED_FIELDS)
        self.assertEqual(len(preview), 7)

    def test_baseline_score_bounds_are_enforced(self):
        preview = self._valid_preview()
        preview["preview_delta"]["baseline_score"] = -0.01
        self._assert_invalid(preview, "baseline_score_below_min")

        preview = self._valid_preview()
        preview["preview_delta"]["baseline_score"] = 1.01
        self._assert_invalid(preview, "baseline_score_above_max")

    def test_memory_delta_bounds_are_enforced(self):
        preview = self._valid_preview()
        preview["preview_delta"]["memory_delta"] = 0.31
        self._assert_invalid(preview, "memory_delta_above_max")

        preview = self._valid_preview()
        preview["preview_delta"]["memory_delta"] = -0.31
        self._assert_invalid(preview, "memory_delta_below_min")

    def test_preview_score_bounds_are_enforced(self):
        preview = self._valid_preview()
        preview["preview_delta"]["preview_score"] = -0.01
        self._assert_invalid(preview, "preview_score_below_min")

        preview = self._valid_preview()
        preview["preview_delta"]["preview_score"] = 1.01
        self._assert_invalid(preview, "preview_score_above_max")

    def test_preview_only_false_blocks(self):
        preview = self._valid_preview()
        preview["preview_only"] = False
        self._assert_invalid(preview, "preview_only_not_true")

    def test_unknown_target_action_tendency_blocks(self):
        preview = self._valid_preview()
        preview["target_action_tendency"] = "choose_final_action"
        self._assert_invalid(preview, "target_action_tendency_not_allowed")

    def test_unknown_influence_direction_blocks(self):
        preview = self._valid_preview()
        preview["preview_delta"]["influence_direction"] = "force"
        self._assert_invalid(preview, "influence_direction_not_allowed")

    def test_empty_exploration_note_blocks(self):
        preview = self._valid_preview()
        preview["human_summary"]["exploration_note"] = ""
        self._assert_invalid(preview, "exploration_note_empty_or_not_string")

    def test_blocked_flags_true_block(self):
        for flag, error_code in BLOCKED_FLAG_ERRORS.items():
            with self.subTest(flag=flag):
                preview = self._valid_preview()
                preview["blocked_flags"][flag] = True
                self._assert_invalid(preview, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_memory_influenced_action_tendency_preview_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-memory-influenced-action-tendency-preview-minimal-check")
        self.assertEqual(result["flow"], "memory_influenced_action_tendency_preview_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["memory_tendency_preview_count"], 25)
        self.assertEqual(summary["valid_memory_tendency_preview_count"], 2)
        self.assertEqual(summary["invalid_memory_tendency_preview_count"], 23)
        self.assertEqual(summary["increase_preview_count"], 1)
        self.assertEqual(summary["decrease_preview_count"], 1)
        self.assertEqual(summary["preview_only_false_blocked_count"], 1)
        self.assertEqual(summary["target_action_tendency_blocked_count"], 1)
        self.assertEqual(summary["influence_direction_blocked_count"], 1)
        self.assertEqual(summary["baseline_score_low_blocked_count"], 1)
        self.assertEqual(summary["baseline_score_high_blocked_count"], 1)
        self.assertEqual(summary["memory_delta_high_blocked_count"], 1)
        self.assertEqual(summary["memory_delta_low_blocked_count"], 1)
        self.assertEqual(summary["preview_score_low_blocked_count"], 1)
        self.assertEqual(summary["preview_score_high_blocked_count"], 1)
        self.assertEqual(summary["empty_exploration_note_blocked_count"], 1)
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
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["action_behavior_changed_count"], 0)
        self.assertEqual(summary["exploration_blocked_valid_count"], 0)
        self.assertEqual(summary["curiosity_overridden_count"], 0)
        self.assertEqual(summary["mentor_override_blocked_valid_count"], 0)
        self.assertEqual(summary["lesson_applied_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["new_retention_written_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertEqual(summary["proof_of_learning_claim_count"], 0)
        self.assertTrue(boundary["preview_only"])
        self.assertTrue(boundary["memory_can_tilt_previewed_tendency"])
        self.assertTrue(boundary["memory_cannot_choose_action"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-memory-influenced-action-tendency-preview-minimal-check")

        self.assertEqual(result["command"], "run-memory-influenced-action-tendency-preview-minimal-check")
        self.assertEqual(result["summary"]["valid_memory_tendency_preview_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-memory-influenced-action-tendency-preview-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-memory-influenced-action-tendency-preview-minimal-check")
        self.assertEqual(result["summary"]["memory_tendency_preview_count"], 25)

    def _assert_invalid(self, preview, error_code):
        validation = validate_memory_influenced_action_tendency_preview(preview)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
