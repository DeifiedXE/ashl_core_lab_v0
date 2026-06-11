import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.runtime_action_tendency_memory_influence_ab_minimal import (
    CANDIDATE_ACTIONS,
    DEMO_STATE,
    build_runtime_action_tendency_memory_influence_ab_result,
    build_runtime_action_tendency_scores,
    run_runtime_action_tendency_memory_influence_ab_minimal_check,
    validate_runtime_action_tendency_memory_influence_ab_result,
)
from ashl_core.teaching_cli import run_command


class RuntimeActionTendencyMemoryInfluenceABMinimalTests(unittest.TestCase):
    def _valid_result(self):
        return build_runtime_action_tendency_memory_influence_ab_result()

    def _memory_signal(self):
        return {
            "memory_signal_id": "retained_memory_signal_obstacle_retry_failed_001",
            "exact_key": "obstacle_retry_failed",
            "source": "retained_experience_exact_key_lookup",
            "valid": True,
            "target_action_tendency": "check_before_retry",
            "influence": {
                "check_before_retry": 0.10,
                "retry_same_action": -0.05,
            },
            "blocked_flags": {
                "semantic_or_fuzzy_match": False,
                "memory_write": False,
                "new_retention_written": False,
            },
        }

    def _assert_invalid(self, record, error_code):
        validation = validate_runtime_action_tendency_memory_influence_ab_result(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_same_runner_produces_memory_off_scores(self):
        result = build_runtime_action_tendency_scores(
            deepcopy(DEMO_STATE),
            list(CANDIDATE_ACTIONS),
            memory_influence_enabled=False,
            memory_signal=self._memory_signal(),
        )

        self.assertFalse(result["memory_influence_enabled"])
        self.assertEqual(result["scores"]["retry_same_action"], 0.50)
        self.assertEqual(result["scores"]["check_before_retry"], 0.50)
        self.assertEqual(result["scores"]["ask_for_help"], 0.20)
        self.assertEqual(result["scores"]["slow_down_or_reduce_cost"], 0.30)

    def test_same_runner_produces_memory_on_scores(self):
        result = build_runtime_action_tendency_scores(
            deepcopy(DEMO_STATE),
            list(CANDIDATE_ACTIONS),
            memory_influence_enabled=True,
            memory_signal=self._memory_signal(),
        )

        self.assertTrue(result["memory_influence_enabled"])
        self.assertEqual(result["scores"]["retry_same_action"], 0.45)
        self.assertEqual(result["scores"]["check_before_retry"], 0.60)
        self.assertEqual(result["scores"]["ask_for_help"], 0.20)
        self.assertEqual(result["scores"]["slow_down_or_reduce_cost"], 0.30)

    def test_memory_on_changes_check_before_retry_from_050_to_060(self):
        result = self._valid_result()

        self.assertEqual(result["memory_off_result"]["scores"]["check_before_retry"], 0.50)
        self.assertEqual(result["memory_on_result"]["scores"]["check_before_retry"], 0.60)
        self.assertEqual(result["score_deltas"]["check_before_retry"], 0.10)

    def test_memory_on_changes_retry_same_action_from_050_to_045(self):
        result = self._valid_result()

        self.assertEqual(result["memory_off_result"]["scores"]["retry_same_action"], 0.50)
        self.assertEqual(result["memory_on_result"]["scores"]["retry_same_action"], 0.45)
        self.assertEqual(result["score_deltas"]["retry_same_action"], -0.05)

    def test_unaffected_actions_remain_unchanged(self):
        result = self._valid_result()

        self.assertEqual(result["memory_on_result"]["scores"]["ask_for_help"], 0.20)
        self.assertEqual(result["memory_on_result"]["scores"]["slow_down_or_reduce_cost"], 0.30)
        self.assertEqual(result["score_deltas"]["ask_for_help"], 0.00)
        self.assertEqual(result["score_deltas"]["slow_down_or_reduce_cost"], 0.00)

    def test_same_runner_used_enforced(self):
        record = self._valid_result()
        record["same_runner_used"] = False
        self._assert_invalid(record, "same_runner_used_not_true")

    def test_same_state_used_enforced(self):
        record = self._valid_result()
        record["same_state_used"] = False
        self._assert_invalid(record, "same_state_used_not_true")

    def test_same_candidate_actions_used_enforced(self):
        record = self._valid_result()
        record["same_candidate_actions_used"] = False
        self._assert_invalid(record, "same_candidate_actions_used_not_true")

    def test_memory_off_result_must_have_memory_influence_enabled_false(self):
        record = self._valid_result()
        record["memory_off_result"]["memory_influence_enabled"] = True
        self._assert_invalid(record, "memory_off_influence_enabled_not_false")

    def test_memory_on_result_must_have_memory_influence_enabled_true(self):
        record = self._valid_result()
        record["memory_on_result"]["memory_influence_enabled"] = False
        self._assert_invalid(record, "memory_on_influence_enabled_not_true")

    def test_delta_correctness_enforced(self):
        record = self._valid_result()
        record["score_deltas"]["check_before_retry"] = 0.09
        self._assert_invalid(record, "check_before_retry_delta_unexpected")

    def test_runtime_tendency_changed_must_be_true_when_delta_exists(self):
        record = self._valid_result()
        record["runtime_tendency_changed"] = False
        self._assert_invalid(record, "runtime_tendency_changed_mismatch")

    def test_final_action_selected_true_blocks(self):
        record = self._valid_result()
        record["behavior_boundary"]["final_action_selected"] = True
        self._assert_invalid(record, "final_action_selected_enabled")

    def test_action_executed_true_blocks(self):
        record = self._valid_result()
        record["behavior_boundary"]["action_executed"] = True
        self._assert_invalid(record, "action_executed_enabled")

    def test_direct_command_created_true_blocks(self):
        record = self._valid_result()
        record["behavior_boundary"]["direct_command_created"] = True
        self._assert_invalid(record, "direct_command_created_enabled")

    def test_real_behavior_changed_true_blocks(self):
        record = self._valid_result()
        record["behavior_boundary"]["real_behavior_changed"] = True
        self._assert_invalid(record, "real_behavior_changed_enabled")

    def test_blocked_flags_true_block(self):
        cases = {
            "final_action_created": "final_action_created_enabled",
            "action_executed": "action_executed_enabled",
            "direct_action_command": "direct_action_command_enabled",
            "real_navigation_changed": "real_navigation_changed_enabled",
            "ui_behavior_changed": "ui_behavior_changed_enabled",
            "persistent_policy_written": "persistent_policy_written_enabled",
            "general_behavior_changed": "general_behavior_changed_enabled",
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
        result = run_runtime_action_tendency_memory_influence_ab_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-runtime-action-tendency-memory-influence-ab-minimal-check")
        self.assertEqual(result["flow"], "runtime_action_tendency_memory_influence_ab_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["runtime_tendency_ab_result_count"], 28)
        self.assertEqual(summary["valid_runtime_tendency_ab_result_count"], 1)
        self.assertEqual(summary["invalid_runtime_tendency_ab_result_count"], 27)
        self.assertEqual(summary["runtime_tendency_changed_count"], 1)
        self.assertEqual(summary["same_runner_violation_blocked_count"], 1)
        self.assertEqual(summary["same_state_violation_blocked_count"], 1)
        self.assertEqual(summary["same_candidate_actions_violation_blocked_count"], 1)
        self.assertEqual(summary["memory_off_enabled_violation_blocked_count"], 1)
        self.assertEqual(summary["memory_on_disabled_violation_blocked_count"], 1)
        self.assertEqual(summary["wrong_check_before_retry_delta_blocked_count"], 1)
        self.assertEqual(summary["wrong_retry_same_action_delta_blocked_count"], 1)
        self.assertEqual(summary["runtime_tendency_changed_false_blocked_count"], 1)
        self.assertEqual(summary["final_action_selected_blocked_count"], 1)
        self.assertEqual(summary["action_executed_blocked_count"], 2)
        self.assertEqual(summary["direct_command_created_blocked_count"], 1)
        self.assertEqual(summary["real_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["final_action_created_blocked_count"], 1)
        self.assertEqual(summary["direct_action_command_blocked_count"], 1)
        self.assertEqual(summary["real_navigation_changed_blocked_count"], 1)
        self.assertEqual(summary["ui_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["persistent_policy_written_blocked_count"], 1)
        self.assertEqual(summary["general_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["exploration_blocked_count"], 1)
        self.assertEqual(summary["curiosity_overridden_blocked_count"], 1)
        self.assertEqual(summary["mentor_override_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["new_retention_written_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertTrue(boundary["memory_influence_changes_runtime_tendency_scores"])
        self.assertTrue(boundary["runtime_tendency_scores_only"])
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
        result = run_command("run-runtime-action-tendency-memory-influence-ab-minimal-check")

        self.assertEqual(result["command"], "run-runtime-action-tendency-memory-influence-ab-minimal-check")
        self.assertEqual(result["summary"]["valid_runtime_tendency_ab_result_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-runtime-action-tendency-memory-influence-ab-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-runtime-action-tendency-memory-influence-ab-minimal-check")
        self.assertEqual(result["summary"]["runtime_tendency_changed_count"], 1)


if __name__ == "__main__":
    unittest.main()
