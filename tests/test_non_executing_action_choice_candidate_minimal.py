import json
import subprocess
import sys
import unittest

from ashl_core.action_selection_adjacent_review_minimal import build_action_selection_adjacent_review
from ashl_core.non_executing_action_choice_candidate_minimal import (
    build_non_executing_action_choice_candidate,
    run_non_executing_action_choice_candidate_minimal_check,
    validate_non_executing_action_choice_candidate,
)
from ashl_core.teaching_cli import run_command


class NonExecutingActionChoiceCandidateMinimalTests(unittest.TestCase):
    def _valid_candidate(self):
        return build_non_executing_action_choice_candidate()

    def _assert_invalid(self, record, error_code):
        validation = validate_non_executing_action_choice_candidate(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_non_executing_choice_candidate_is_created(self):
        record = self._valid_candidate()
        validation = validate_non_executing_action_choice_candidate(record)

        self.assertTrue(validation["valid"])
        self.assertEqual(record["choice_mode"], "non_executing_choice_candidate_only")
        self.assertEqual(record["choice_candidate_action"], "check_before_retry")

    def test_valid_candidate_reuses_action_selection_adjacent_review(self):
        review = build_action_selection_adjacent_review()
        record = build_non_executing_action_choice_candidate(review)

        self.assertEqual(record["source_review_id"], review["review_id"])
        self.assertEqual(record["choice_source"]["source_review_mode"], "action_selection_adjacent_review_only")

    def test_choice_source_matches_review_highlight(self):
        source = self._valid_candidate()["choice_source"]

        self.assertEqual(source["source_most_review_worthy_candidate"], "check_before_retry")
        self.assertEqual(source["source_scenario_id"], "obstacle_retry_failed_same_state")
        self.assertEqual(source["source_exact_key"], "obstacle_retry_failed")

    def test_choice_constraints_block_selection_and_execution(self):
        constraints = self._valid_candidate()["choice_constraints"]

        self.assertTrue(constraints["candidate_only"])
        self.assertTrue(constraints["non_executing"])
        self.assertFalse(constraints["selected_action"])
        self.assertFalse(constraints["final_action"])
        self.assertFalse(constraints["action_execution"])
        self.assertFalse(constraints["direct_command"])
        self.assertFalse(constraints["runtime_action_selection"])
        self.assertTrue(constraints["may_enter_one_step_sandbox_action_intent"])

    def test_bad_choice_mode_blocks(self):
        record = self._valid_candidate()
        record["choice_mode"] = "runtime_action_selection_choice"
        self._assert_invalid(record, "choice_mode_not_non_executing_choice_candidate_only")

    def test_wrong_choice_candidate_action_blocks(self):
        record = self._valid_candidate()
        record["choice_candidate_action"] = "ask_for_help"
        self._assert_invalid(record, "choice_candidate_action_not_check_before_retry")

    def test_source_mismatch_blocks(self):
        cases = {
            "source_most_review_worthy_candidate": "source_most_review_worthy_candidate_mismatch",
            "source_scenario_id": "source_scenario_id_not_obstacle_retry_failed_same_state",
            "source_exact_key": "source_exact_key_not_obstacle_retry_failed",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_candidate()
                record["choice_source"][field] = "mismatch"
                self._assert_invalid(record, error_code)

    def test_constraint_false_or_true_blocks(self):
        cases = {
            "candidate_only": (False, "candidate_only_not_true"),
            "non_executing": (False, "non_executing_not_true"),
            "selected_action": (True, "selected_action_not_false"),
            "final_action": (True, "final_action_not_false"),
            "action_execution": (True, "action_execution_not_false"),
            "direct_command": (True, "direct_command_not_false"),
            "runtime_action_selection": (True, "runtime_action_selection_not_false"),
            "may_enter_one_step_sandbox_action_intent": (
                False,
                "may_enter_one_step_sandbox_action_intent_not_true",
            ),
        }
        for field, (value, error_code) in cases.items():
            with self.subTest(field=field):
                record = self._valid_candidate()
                record["choice_constraints"][field] = value
                self._assert_invalid(record, error_code)

    def test_empty_human_summary_fields_block(self):
        cases = {
            "what_was_named": "what_was_named_empty_or_not_string",
            "what_it_is_not": "what_it_is_not_empty_or_not_string",
            "plain_result": "plain_result_empty_or_not_string",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_candidate()
                record["human_summary"][field] = ""
                self._assert_invalid(record, error_code)

    def test_blocked_flags_true_block(self):
        cases = {
            "production_action_selection": "production_action_selection_enabled",
            "runtime_action_selection": "runtime_action_selection_enabled",
            "selected_action_created": "selected_action_created_enabled",
            "final_action_created": "final_action_created_enabled",
            "action_executed": "action_executed_enabled",
            "direct_action_command": "direct_action_command_enabled",
            "real_navigation_changed": "real_navigation_changed_enabled",
            "ui_behavior_changed": "ui_behavior_changed_enabled",
            "persistent_policy_written": "persistent_policy_written_enabled",
            "general_behavior_changed": "general_behavior_changed_enabled",
            "semantic_or_fuzzy_match_used": "semantic_or_fuzzy_match_used_enabled",
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
                record = self._valid_candidate()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_non_executing_action_choice_candidate_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-non-executing-action-choice-candidate-minimal-check")
        self.assertEqual(result["flow"], "non_executing_action_choice_candidate_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["choice_candidate_result_count"], 37)
        self.assertEqual(summary["valid_choice_candidate_result_count"], 1)
        self.assertEqual(summary["invalid_choice_candidate_result_count"], 36)
        self.assertEqual(summary["choice_candidate_action_count"], 1)
        self.assertEqual(summary["candidate_only_count"], 1)
        self.assertEqual(summary["non_executing_count"], 1)
        self.assertEqual(summary["not_selected_action_count"], 1)
        self.assertEqual(summary["not_final_action_count"], 1)
        self.assertEqual(summary["not_action_execution_count"], 1)
        self.assertEqual(summary["not_direct_command_count"], 1)
        self.assertEqual(summary["not_runtime_action_selection_count"], 1)
        self.assertEqual(summary["may_enter_one_step_sandbox_action_intent_count"], 1)
        self.assertEqual(summary["bad_choice_mode_blocked_count"], 1)
        self.assertEqual(summary["wrong_choice_candidate_action_blocked_count"], 1)
        self.assertEqual(summary["source_mismatch_blocked_count"], 3)
        self.assertEqual(summary["selected_action_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertEqual(boundary["choice_candidate_action"], "check_before_retry")
        self.assertTrue(boundary["candidate_only"])
        self.assertTrue(boundary["non_executing"])
        self.assertFalse(boundary["selected_action_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-non-executing-action-choice-candidate-minimal-check")

        self.assertEqual(result["command"], "run-non-executing-action-choice-candidate-minimal-check")
        self.assertEqual(result["summary"]["valid_choice_candidate_result_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-non-executing-action-choice-candidate-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-non-executing-action-choice-candidate-minimal-check")
        self.assertEqual(result["summary"]["choice_candidate_action_count"], 1)


if __name__ == "__main__":
    unittest.main()
