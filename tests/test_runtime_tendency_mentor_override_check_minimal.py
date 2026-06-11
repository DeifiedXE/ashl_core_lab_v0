import json
import subprocess
import sys
import unittest

from ashl_core.runtime_tendency_mentor_override_check_minimal import (
    build_runtime_tendency_mentor_override_result,
    run_runtime_tendency_mentor_override_check_minimal_check,
    validate_runtime_tendency_mentor_override_result,
)
from ashl_core.teaching_cli import run_command


class RuntimeTendencyMentorOverrideCheckMinimalTests(unittest.TestCase):
    def _valid_result(self):
        return build_runtime_tendency_mentor_override_result()

    def _assert_invalid(self, record, error_code):
        validation = validate_runtime_tendency_mentor_override_result(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_mentor_override_check_is_created(self):
        result = self._valid_result()
        validation = validate_runtime_tendency_mentor_override_result(result)

        self.assertTrue(validation["valid"])
        self.assertEqual(
            set(result),
            {
                "mentor_override_result_id",
                "scenario_id",
                "same_runner_used",
                "same_state_used",
                "same_candidate_actions_used",
                "sequence",
                "mentor_override_check",
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

    def test_memory_on_with_mentor_override_matches_memory_off_exactly(self):
        sequence = self._valid_result()["sequence"]

        self.assertEqual(
            sequence["memory_on_with_mentor_override"]["scores"],
            sequence["memory_off"]["scores"],
        )

    def test_mentor_override_check_flags_are_true(self):
        check = self._valid_result()["mentor_override_check"]

        self.assertTrue(check["memory_on_changed_scores"])
        self.assertTrue(check["mentor_override_suppressed_memory_influence"])
        self.assertTrue(check["override_result_matches_baseline"])
        self.assertTrue(check["mentor_override_available"])
        self.assertTrue(check["safe_to_continue_to_multi_scenario_check"])

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

    def test_override_memory_enabled_false_blocks(self):
        record = self._valid_result()
        record["sequence"]["memory_on_with_mentor_override"]["memory_influence_enabled"] = False
        self._assert_invalid(record, "override_memory_influence_enabled_not_true")

    def test_override_inactive_blocks(self):
        record = self._valid_result()
        record["sequence"]["memory_on_with_mentor_override"]["mentor_override_active"] = False
        self._assert_invalid(record, "override_mentor_override_active_not_true")

    def test_memory_on_no_score_change_blocks(self):
        record = self._valid_result()
        record["sequence"]["memory_on"]["scores"] = dict(record["sequence"]["memory_off"]["scores"])
        self._assert_invalid(record, "memory_on_scores_not_changed")

    def test_override_not_suppressed_blocks(self):
        record = self._valid_result()
        record["sequence"]["memory_on_with_mentor_override"]["scores"] = dict(
            record["sequence"]["memory_on"]["scores"]
        )
        self._assert_invalid(record, "mentor_override_did_not_suppress_memory_influence")

    def test_override_baseline_mismatch_blocks(self):
        record = self._valid_result()
        record["sequence"]["memory_on_with_mentor_override"]["scores"]["check_before_retry"] = 0.49
        self._assert_invalid(record, "override_result_baseline_mismatch")

    def test_mentor_override_available_false_blocks(self):
        record = self._valid_result()
        record["mentor_override_check"]["mentor_override_available"] = False
        self._assert_invalid(record, "mentor_override_available_not_true")

    def test_safe_to_continue_false_blocks(self):
        record = self._valid_result()
        record["mentor_override_check"]["safe_to_continue_to_multi_scenario_check"] = False
        self._assert_invalid(record, "safe_to_continue_to_multi_scenario_check_not_true")

    def test_empty_override_summary_blocks(self):
        record = self._valid_result()
        record["human_summary"]["override"] = ""
        self._assert_invalid(record, "override_empty_or_not_string")

    def test_empty_plain_result_blocks(self):
        record = self._valid_result()
        record["human_summary"]["plain_result"] = ""
        self._assert_invalid(record, "plain_result_empty_or_not_string")

    def test_blocked_flags_true_block(self):
        cases = {
            "production_action_selection": "production_action_selection_enabled",
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
        result = run_runtime_tendency_mentor_override_check_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-runtime-tendency-mentor-override-check-minimal-check")
        self.assertEqual(result["flow"], "runtime_tendency_mentor_override_check_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["mentor_override_result_count"], 31)
        self.assertEqual(summary["valid_mentor_override_result_count"], 1)
        self.assertEqual(summary["invalid_mentor_override_result_count"], 30)
        self.assertEqual(summary["memory_on_changed_scores_count"], 1)
        self.assertEqual(summary["mentor_override_suppressed_memory_influence_count"], 1)
        self.assertEqual(summary["override_result_matches_baseline_count"], 1)
        self.assertEqual(summary["mentor_override_available_count"], 1)
        self.assertEqual(summary["same_runner_violation_blocked_count"], 1)
        self.assertEqual(summary["same_state_violation_blocked_count"], 1)
        self.assertEqual(summary["same_candidate_actions_violation_blocked_count"], 1)
        self.assertEqual(summary["memory_off_enabled_violation_blocked_count"], 1)
        self.assertEqual(summary["memory_on_disabled_violation_blocked_count"], 1)
        self.assertEqual(summary["override_memory_enabled_false_blocked_count"], 1)
        self.assertEqual(summary["override_inactive_blocked_count"], 1)
        self.assertEqual(summary["memory_on_no_change_blocked_count"], 1)
        self.assertEqual(summary["override_not_suppressed_blocked_count"], 1)
        self.assertEqual(summary["override_baseline_mismatch_blocked_count"], 1)
        self.assertEqual(summary["mentor_override_unavailable_blocked_count"], 1)
        self.assertEqual(summary["safe_to_continue_false_blocked_count"], 1)
        self.assertEqual(summary["empty_override_summary_blocked_count"], 1)
        self.assertEqual(summary["empty_plain_result_blocked_count"], 1)
        self.assertEqual(summary["production_action_selection_blocked_count"], 1)
        self.assertEqual(summary["final_action_created_blocked_count"], 1)
        self.assertEqual(summary["action_executed_blocked_count"], 1)
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
        self.assertTrue(boundary["mentor_override_suppresses_memory_influence"])
        self.assertTrue(boundary["override_result_matches_baseline"])
        self.assertTrue(boundary["mentor_override_available"])
        self.assertTrue(boundary["safe_to_continue_to_multi_scenario_check"])
        self.assertFalse(boundary["production_action_selection_added"])
        self.assertFalse(boundary["final_action_creation_added"])
        self.assertFalse(boundary["action_execution_added"])
        self.assertFalse(boundary["direct_action_command_added"])
        self.assertFalse(boundary["real_navigation_change_added"])
        self.assertFalse(boundary["ui_behavior_change_added"])
        self.assertFalse(boundary["persistent_policy_write_added"])
        self.assertFalse(boundary["general_behavior_change_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-runtime-tendency-mentor-override-check-minimal-check")

        self.assertEqual(result["command"], "run-runtime-tendency-mentor-override-check-minimal-check")
        self.assertEqual(result["summary"]["valid_mentor_override_result_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-runtime-tendency-mentor-override-check-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-runtime-tendency-mentor-override-check-minimal-check")
        self.assertEqual(result["summary"]["mentor_override_suppressed_memory_influence_count"], 1)


if __name__ == "__main__":
    unittest.main()
