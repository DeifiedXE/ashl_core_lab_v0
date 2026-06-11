import json
import subprocess
import sys
import unittest

from ashl_core.runtime_tendency_memory_influence_rollback_check_minimal import (
    build_runtime_tendency_memory_influence_rollback_result,
    run_runtime_tendency_memory_influence_rollback_check_minimal_check,
    validate_runtime_tendency_memory_influence_rollback_result,
)
from ashl_core.teaching_cli import run_command


class RuntimeTendencyMemoryInfluenceRollbackCheckMinimalTests(unittest.TestCase):
    def _valid_result(self):
        return build_runtime_tendency_memory_influence_rollback_result()

    def _assert_invalid(self, record, error_code):
        validation = validate_runtime_tendency_memory_influence_rollback_result(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_rollback_check_is_created(self):
        result = self._valid_result()
        validation = validate_runtime_tendency_memory_influence_rollback_result(result)

        self.assertTrue(validation["valid"])
        self.assertEqual(
            set(result),
            {
                "rollback_result_id",
                "scenario_id",
                "same_runner_used",
                "same_state_used",
                "same_candidate_actions_used",
                "sequence",
                "rollback_check",
                "human_summary",
                "blocked_flags",
            },
        )

    def test_same_runner_state_and_candidate_actions_are_used(self):
        result = self._valid_result()

        self.assertTrue(result["same_runner_used"])
        self.assertTrue(result["same_state_used"])
        self.assertTrue(result["same_candidate_actions_used"])

    def test_memory_off_baseline_scores_are_correct(self):
        scores = self._valid_result()["sequence"]["memory_off"]["scores"]

        self.assertEqual(scores["retry_same_action"], 0.50)
        self.assertEqual(scores["check_before_retry"], 0.50)
        self.assertEqual(scores["ask_for_help"], 0.20)
        self.assertEqual(scores["slow_down_or_reduce_cost"], 0.30)

    def test_memory_on_changed_scores_are_correct(self):
        scores = self._valid_result()["sequence"]["memory_on"]["scores"]

        self.assertEqual(scores["retry_same_action"], 0.45)
        self.assertEqual(scores["check_before_retry"], 0.60)
        self.assertEqual(scores["ask_for_help"], 0.20)
        self.assertEqual(scores["slow_down_or_reduce_cost"], 0.30)

    def test_memory_off_again_matches_memory_off_exactly(self):
        sequence = self._valid_result()["sequence"]

        self.assertEqual(sequence["memory_off_again"]["scores"], sequence["memory_off"]["scores"])

    def test_rollback_check_flags_are_safe(self):
        rollback_check = self._valid_result()["rollback_check"]

        self.assertTrue(rollback_check["memory_on_changed_scores"])
        self.assertTrue(rollback_check["memory_off_again_matches_baseline"])
        self.assertFalse(rollback_check["dirty_state_detected"])
        self.assertFalse(rollback_check["persistent_influence_detected"])
        self.assertTrue(rollback_check["safe_to_continue_to_safety_envelope"])

    def test_same_runner_used_false_blocks(self):
        record = self._valid_result()
        record["same_runner_used"] = False
        self._assert_invalid(record, "same_runner_used_not_true")

    def test_same_state_used_false_blocks(self):
        record = self._valid_result()
        record["same_state_used"] = False
        self._assert_invalid(record, "same_state_used_not_true")

    def test_same_candidate_actions_used_false_blocks(self):
        record = self._valid_result()
        record["same_candidate_actions_used"] = False
        self._assert_invalid(record, "same_candidate_actions_used_not_true")

    def test_memory_off_enabled_true_blocks(self):
        record = self._valid_result()
        record["sequence"]["memory_off"]["memory_influence_enabled"] = True
        self._assert_invalid(record, "memory_off_influence_enabled_not_false")

    def test_memory_on_enabled_false_blocks(self):
        record = self._valid_result()
        record["sequence"]["memory_on"]["memory_influence_enabled"] = False
        self._assert_invalid(record, "memory_on_influence_enabled_not_true")

    def test_memory_off_again_enabled_true_blocks(self):
        record = self._valid_result()
        record["sequence"]["memory_off_again"]["memory_influence_enabled"] = True
        self._assert_invalid(record, "memory_off_again_influence_enabled_not_false")

    def test_memory_on_no_score_change_blocks(self):
        record = self._valid_result()
        record["sequence"]["memory_on"]["scores"] = dict(record["sequence"]["memory_off"]["scores"])
        self._assert_invalid(record, "memory_on_scores_not_changed")

    def test_rollback_mismatch_blocks(self):
        record = self._valid_result()
        record["sequence"]["memory_off_again"]["scores"]["check_before_retry"] = 0.49
        self._assert_invalid(record, "memory_off_again_baseline_mismatch")

    def test_dirty_state_detected_true_blocks(self):
        record = self._valid_result()
        record["rollback_check"]["dirty_state_detected"] = True
        self._assert_invalid(record, "dirty_state_detected")

    def test_persistent_influence_detected_true_blocks(self):
        record = self._valid_result()
        record["rollback_check"]["persistent_influence_detected"] = True
        self._assert_invalid(record, "persistent_influence_detected")

    def test_safe_to_continue_false_blocks(self):
        record = self._valid_result()
        record["rollback_check"]["safe_to_continue_to_safety_envelope"] = False
        self._assert_invalid(record, "safe_to_continue_to_safety_envelope_not_true")

    def test_empty_rollback_summary_blocks(self):
        record = self._valid_result()
        record["human_summary"]["rollback"] = ""
        self._assert_invalid(record, "rollback_empty_or_not_string")

    def test_empty_plain_result_blocks(self):
        record = self._valid_result()
        record["human_summary"]["plain_result"] = ""
        self._assert_invalid(record, "plain_result_empty_or_not_string")

    def test_blocked_flags_true_block(self):
        cases = {
            "final_action_created": "final_action_created_enabled",
            "action_executed": "action_executed_enabled",
            "direct_action_command": "direct_action_command_enabled",
            "real_navigation_changed": "real_navigation_changed_enabled",
            "ui_behavior_changed": "ui_behavior_changed_enabled",
            "persistent_policy_written": "persistent_policy_written_enabled",
            "general_behavior_changed": "general_behavior_changed_enabled",
            "dirty_state_leftover": "dirty_state_leftover_enabled",
            "persistent_influence_written": "persistent_influence_written_enabled",
            "exploration_blocked": "exploration_blocked_enabled",
            "curiosity_overridden": "curiosity_overridden_enabled",
            "mentor_override_blocked": "mentor_override_blocked_enabled",
            "lesson_applied": "lesson_applied_enabled",
            "memory_write": "memory_write_enabled",
            "new_retention_written": "new_retention_written_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                record = self._valid_result()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_runtime_tendency_memory_influence_rollback_check_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-runtime-tendency-memory-influence-rollback-check-minimal-check")
        self.assertEqual(result["flow"], "runtime_tendency_memory_influence_rollback_check_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["rollback_result_count"], 31)
        self.assertEqual(summary["valid_rollback_result_count"], 1)
        self.assertEqual(summary["invalid_rollback_result_count"], 30)
        self.assertEqual(summary["memory_on_changed_scores_count"], 1)
        self.assertEqual(summary["memory_off_again_matches_baseline_count"], 1)
        self.assertEqual(summary["dirty_state_detected_blocked_count"], 1)
        self.assertEqual(summary["persistent_influence_detected_blocked_count"], 1)
        self.assertEqual(summary["safe_to_continue_false_blocked_count"], 1)
        self.assertEqual(summary["same_runner_violation_blocked_count"], 1)
        self.assertEqual(summary["same_state_violation_blocked_count"], 1)
        self.assertEqual(summary["same_candidate_actions_violation_blocked_count"], 1)
        self.assertEqual(summary["memory_off_enabled_violation_blocked_count"], 1)
        self.assertEqual(summary["memory_on_disabled_violation_blocked_count"], 1)
        self.assertEqual(summary["memory_off_again_enabled_violation_blocked_count"], 1)
        self.assertEqual(summary["memory_on_no_change_blocked_count"], 1)
        self.assertEqual(summary["rollback_mismatch_blocked_count"], 1)
        self.assertEqual(summary["empty_rollback_summary_blocked_count"], 1)
        self.assertEqual(summary["empty_plain_result_blocked_count"], 1)
        self.assertEqual(summary["final_action_created_blocked_count"], 1)
        self.assertEqual(summary["action_executed_blocked_count"], 1)
        self.assertEqual(summary["direct_action_command_blocked_count"], 1)
        self.assertEqual(summary["real_navigation_changed_blocked_count"], 1)
        self.assertEqual(summary["ui_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["persistent_policy_written_blocked_count"], 1)
        self.assertEqual(summary["general_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["dirty_state_leftover_blocked_count"], 1)
        self.assertEqual(summary["persistent_influence_written_blocked_count"], 1)
        self.assertEqual(summary["exploration_blocked_count"], 1)
        self.assertEqual(summary["curiosity_overridden_blocked_count"], 1)
        self.assertEqual(summary["mentor_override_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["new_retention_written_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertEqual(summary["dirty_state_detected_count"], 0)
        self.assertEqual(summary["persistent_influence_detected_count"], 0)
        self.assertTrue(boundary["memory_on_changes_runtime_tendency_scores"])
        self.assertTrue(boundary["memory_off_again_matches_baseline"])
        self.assertFalse(boundary["dirty_state_detected"])
        self.assertFalse(boundary["persistent_influence_detected"])
        self.assertTrue(boundary["safe_to_continue_to_safety_envelope"])
        self.assertFalse(boundary["final_action_creation_added"])
        self.assertFalse(boundary["action_execution_added"])
        self.assertFalse(boundary["direct_action_command_added"])
        self.assertFalse(boundary["real_navigation_change_added"])
        self.assertFalse(boundary["ui_behavior_change_added"])
        self.assertFalse(boundary["persistent_policy_write_added"])
        self.assertFalse(boundary["general_behavior_change_added"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["new_retention_write_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-runtime-tendency-memory-influence-rollback-check-minimal-check")

        self.assertEqual(result["command"], "run-runtime-tendency-memory-influence-rollback-check-minimal-check")
        self.assertEqual(result["summary"]["valid_rollback_result_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-runtime-tendency-memory-influence-rollback-check-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-runtime-tendency-memory-influence-rollback-check-minimal-check")
        self.assertEqual(result["summary"]["memory_off_again_matches_baseline_count"], 1)


if __name__ == "__main__":
    unittest.main()
