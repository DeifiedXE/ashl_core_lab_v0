import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.memory_influence_candidate_preview_minimal import (
    build_memory_influence_candidate_preview,
    run_memory_influence_candidate_preview_minimal_check,
    validate_memory_influence_candidate_preview,
)
from ashl_core.retained_experience_into_dry_run_minimal import (
    run_retained_experience_into_dry_run_minimal_check,
)
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "memory_influence_candidate_id",
    "source_dry_run_context_id",
    "target_action_tendency",
    "influence_direction",
    "influence_strength",
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


class MemoryInfluenceCandidatePreviewMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dry_run_result = run_retained_experience_into_dry_run_minimal_check()
        cls.valid_context = next(
            context
            for context, validation in zip(
                dry_run_result["retained_experience_dry_run_contexts"],
                dry_run_result["validation_results"],
            )
            if validation["valid"] and validation["matched_context"]
        )

    def _valid_candidate(self):
        return build_memory_influence_candidate_preview(self.valid_context)

    def test_valid_retained_dry_run_context_creates_memory_influence_candidate(self):
        candidate = self._valid_candidate()
        validation = validate_memory_influence_candidate_preview(candidate)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(candidate["target_action_tendency"], "check_before_retry")
        self.assertEqual(candidate["influence_direction"], "increase")

    def test_candidate_is_preview_only(self):
        candidate = self._valid_candidate()

        self.assertTrue(candidate["preview_only"])
        self.assertIn("cannot choose or block an action", candidate["human_summary"]["plain_result"])

    def test_candidate_has_only_expected_top_level_fields(self):
        candidate = self._valid_candidate()

        self.assertEqual(set(candidate), EXPECTED_FIELDS)
        self.assertEqual(len(candidate), 8)

    def test_influence_strength_within_range_is_valid(self):
        for strength in (0.0, 0.1, 0.3):
            with self.subTest(strength=strength):
                candidate = build_memory_influence_candidate_preview(
                    self.valid_context,
                    {
                        "target_action_tendency": "check_before_retry",
                        "influence_direction": "increase",
                        "influence_strength": strength,
                    },
                )
                validation = validate_memory_influence_candidate_preview(candidate)

                self.assertTrue(validation["valid"], validation["error_codes"])

    def test_influence_strength_over_0_3_blocks(self):
        candidate = self._valid_candidate()
        candidate["influence_strength"] = 0.31
        self._assert_invalid(candidate, "influence_strength_above_max")

    def test_influence_strength_below_0_0_blocks(self):
        candidate = self._valid_candidate()
        candidate["influence_strength"] = -0.01
        self._assert_invalid(candidate, "influence_strength_below_min")

    def test_unknown_target_action_tendency_blocks(self):
        candidate = self._valid_candidate()
        candidate["target_action_tendency"] = "choose_final_action"
        self._assert_invalid(candidate, "target_action_tendency_not_allowed")

    def test_unknown_influence_direction_blocks(self):
        candidate = self._valid_candidate()
        candidate["influence_direction"] = "force"
        self._assert_invalid(candidate, "influence_direction_not_allowed")

    def test_empty_exploration_note_blocks(self):
        candidate = self._valid_candidate()
        candidate["human_summary"]["exploration_note"] = ""
        self._assert_invalid(candidate, "exploration_note_empty_or_not_string")

    def test_blocked_flags_true_block(self):
        for flag, error_code in BLOCKED_FLAG_ERRORS.items():
            with self.subTest(flag=flag):
                candidate = self._valid_candidate()
                candidate["blocked_flags"][flag] = True
                self._assert_invalid(candidate, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_memory_influence_candidate_preview_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-memory-influence-candidate-preview-minimal-check")
        self.assertEqual(result["flow"], "memory_influence_candidate_preview_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["memory_influence_candidate_count"], 21)
        self.assertEqual(summary["valid_memory_influence_candidate_count"], 2)
        self.assertEqual(summary["invalid_memory_influence_candidate_count"], 19)
        self.assertEqual(summary["increase_tendency_count"], 1)
        self.assertEqual(summary["decrease_tendency_count"], 1)
        self.assertEqual(summary["preview_only_false_blocked_count"], 1)
        self.assertEqual(summary["target_action_tendency_blocked_count"], 1)
        self.assertEqual(summary["influence_direction_blocked_count"], 1)
        self.assertEqual(summary["influence_strength_high_blocked_count"], 1)
        self.assertEqual(summary["influence_strength_low_blocked_count"], 1)
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
        self.assertTrue(boundary["memory_is_warning_not_ban"])
        self.assertTrue(boundary["past_failure_does_not_forbid_action"])
        self.assertTrue(boundary["curiosity_exploration_preserved"])
        self.assertFalse(boundary["real_memory_influenced_behavior_added"])
        self.assertFalse(boundary["final_action_creation_added"])
        self.assertFalse(boundary["direct_action_command_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])
        self.assertFalse(boundary["exploration_blocking_added"])
        self.assertFalse(boundary["curiosity_override_added"])
        self.assertFalse(boundary["mentor_override_blocking_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-memory-influence-candidate-preview-minimal-check")

        self.assertEqual(result["command"], "run-memory-influence-candidate-preview-minimal-check")
        self.assertEqual(result["summary"]["valid_memory_influence_candidate_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-memory-influence-candidate-preview-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-memory-influence-candidate-preview-minimal-check")
        self.assertEqual(result["summary"]["memory_influence_candidate_count"], 21)

    def _assert_invalid(self, candidate, error_code):
        validation = validate_memory_influence_candidate_preview(candidate)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
