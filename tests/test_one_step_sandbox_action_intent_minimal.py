import json
import subprocess
import sys
import unittest

from ashl_core.non_executing_action_choice_candidate_minimal import (
    build_non_executing_action_choice_candidate,
)
from ashl_core.one_step_sandbox_action_intent_minimal import (
    build_one_step_sandbox_action_intent,
    run_one_step_sandbox_action_intent_minimal_check,
    validate_one_step_sandbox_action_intent,
)
from ashl_core.teaching_cli import run_command


class OneStepSandboxActionIntentMinimalTests(unittest.TestCase):
    def _valid_intent(self):
        return build_one_step_sandbox_action_intent()

    def _assert_invalid(self, record, error_code):
        validation = validate_one_step_sandbox_action_intent(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_one_step_sandbox_action_intent_is_created(self):
        record = self._valid_intent()
        validation = validate_one_step_sandbox_action_intent(record)

        self.assertTrue(validation["valid"])
        self.assertEqual(record["intent_mode"], "one_step_sandbox_intent_only")
        self.assertEqual(record["intended_sandbox_action"], "check_before_retry")

    def test_valid_intent_reuses_non_executing_choice_candidate(self):
        candidate = build_non_executing_action_choice_candidate()
        record = build_one_step_sandbox_action_intent(candidate)

        self.assertEqual(record["source_choice_candidate_id"], candidate["choice_candidate_id"])
        self.assertEqual(record["intended_sandbox_action"], candidate["choice_candidate_action"])

    def test_sandbox_context_matches_expected_controlled_case(self):
        context = self._valid_intent()["sandbox_context"]

        self.assertEqual(context["sandbox_id"], "phase0_toy_sandbox_obstacle_retry_failed")
        self.assertEqual(context["scenario_id"], "obstacle_retry_failed_same_state")
        self.assertEqual(context["exact_key"], "obstacle_retry_failed")
        self.assertTrue(context["one_step_only"])
        self.assertFalse(context["production_context"])

    def test_intent_constraints_block_selection_execution_and_policy(self):
        constraints = self._valid_intent()["intent_constraints"]

        self.assertTrue(constraints["intent_only"])
        self.assertTrue(constraints["sandbox_only"])
        self.assertTrue(constraints["one_step_only"])
        self.assertTrue(constraints["non_executing"])
        self.assertFalse(constraints["selected_action"])
        self.assertFalse(constraints["final_action"])
        self.assertFalse(constraints["action_execution"])
        self.assertFalse(constraints["direct_command"])
        self.assertFalse(constraints["runtime_action_selection"])
        self.assertFalse(constraints["persistent_policy"])
        self.assertTrue(constraints["rollback_required_before_execution"])
        self.assertTrue(constraints["audit_trace_required"])
        self.assertTrue(constraints["mentor_override_available"])

    def test_allowed_next_layer_blocks_production_and_real_action(self):
        allowed = self._valid_intent()["allowed_next_layer"]

        self.assertTrue(allowed["may_enter_one_step_sandbox_action_execution"])
        self.assertFalse(allowed["may_enter_production_action_selection"])
        self.assertFalse(allowed["may_create_final_action"])
        self.assertFalse(allowed["may_execute_real_action"])
        self.assertFalse(allowed["may_create_direct_command"])
        self.assertFalse(allowed["may_write_persistent_policy"])

    def test_bad_intent_mode_blocks(self):
        record = self._valid_intent()
        record["intent_mode"] = "production_action_intent"
        self._assert_invalid(record, "intent_mode_not_one_step_sandbox_intent_only")

    def test_wrong_intended_sandbox_action_blocks(self):
        record = self._valid_intent()
        record["intended_sandbox_action"] = "ask_for_help"
        self._assert_invalid(record, "intended_sandbox_action_not_check_before_retry")

    def test_wrong_sandbox_context_blocks(self):
        cases = {
            "sandbox_id": "sandbox_id_not_phase0_toy_sandbox_obstacle_retry_failed",
            "scenario_id": "scenario_id_not_obstacle_retry_failed_same_state",
            "exact_key": "exact_key_not_obstacle_retry_failed",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_intent()
                record["sandbox_context"][field] = "mismatch"
                self._assert_invalid(record, error_code)

    def test_production_context_true_blocks(self):
        record = self._valid_intent()
        record["sandbox_context"]["production_context"] = True
        self._assert_invalid(record, "production_context_not_false")

    def test_constraint_false_or_true_blocks(self):
        cases = {
            "intent_only": (False, "intent_only_not_true"),
            "sandbox_only": (False, "sandbox_only_not_true"),
            "one_step_only": (False, "one_step_only_not_true"),
            "non_executing": (False, "non_executing_not_true"),
            "selected_action": (True, "selected_action_not_false"),
            "final_action": (True, "final_action_not_false"),
            "action_execution": (True, "action_execution_not_false"),
            "direct_command": (True, "direct_command_not_false"),
            "runtime_action_selection": (True, "runtime_action_selection_not_false"),
            "persistent_policy": (True, "persistent_policy_not_false"),
        }
        for field, (value, error_code) in cases.items():
            with self.subTest(field=field):
                record = self._valid_intent()
                record["intent_constraints"][field] = value
                self._assert_invalid(record, error_code)

    def test_missing_rollback_audit_mentor_flags_block(self):
        cases = {
            "rollback_required_before_execution": "rollback_required_before_execution_not_true",
            "audit_trace_required": "audit_trace_required_not_true",
            "mentor_override_available": "mentor_override_available_not_true",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_intent()
                record["intent_constraints"][field] = False
                self._assert_invalid(record, error_code)

    def test_allowed_next_layer_violations_block(self):
        cases = {
            "may_enter_one_step_sandbox_action_execution": (
                False,
                "may_enter_one_step_sandbox_action_execution_not_true",
            ),
            "may_enter_production_action_selection": (
                True,
                "may_enter_production_action_selection_not_false",
            ),
            "may_create_final_action": (True, "may_create_final_action_not_false"),
            "may_execute_real_action": (True, "may_execute_real_action_not_false"),
            "may_create_direct_command": (True, "may_create_direct_command_not_false"),
            "may_write_persistent_policy": (True, "may_write_persistent_policy_not_false"),
        }
        for field, (value, error_code) in cases.items():
            with self.subTest(field=field):
                record = self._valid_intent()
                record["allowed_next_layer"][field] = value
                self._assert_invalid(record, error_code)

    def test_empty_human_summary_fields_block(self):
        cases = {
            "what_was_created": "what_was_created_empty_or_not_string",
            "why_it_was_created": "why_it_was_created_empty_or_not_string",
            "what_it_is_not": "what_it_is_not_empty_or_not_string",
            "plain_result": "plain_result_empty_or_not_string",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_intent()
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
                record = self._valid_intent()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_one_step_sandbox_action_intent_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-one-step-sandbox-action-intent-minimal-check")
        self.assertEqual(result["flow"], "one_step_sandbox_action_intent_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["sandbox_action_intent_result_count"], 51)
        self.assertEqual(summary["valid_sandbox_action_intent_result_count"], 1)
        self.assertEqual(summary["invalid_sandbox_action_intent_result_count"], 50)
        self.assertEqual(summary["intent_action_count"], 1)
        self.assertEqual(summary["intent_only_count"], 1)
        self.assertEqual(summary["sandbox_only_count"], 1)
        self.assertEqual(summary["one_step_only_count"], 1)
        self.assertEqual(summary["non_executing_count"], 1)
        self.assertEqual(summary["not_selected_action_count"], 1)
        self.assertEqual(summary["not_final_action_count"], 1)
        self.assertEqual(summary["not_action_execution_count"], 1)
        self.assertEqual(summary["not_direct_command_count"], 1)
        self.assertEqual(summary["not_runtime_action_selection_count"], 1)
        self.assertEqual(summary["rollback_required_count"], 1)
        self.assertEqual(summary["audit_trace_required_count"], 1)
        self.assertEqual(summary["mentor_override_available_count"], 1)
        self.assertEqual(summary["may_enter_one_step_sandbox_action_execution_count"], 1)
        self.assertEqual(summary["bad_intent_mode_blocked_count"], 1)
        self.assertEqual(summary["wrong_intended_sandbox_action_blocked_count"], 1)
        self.assertEqual(summary["wrong_sandbox_context_blocked_count"], 3)
        self.assertEqual(summary["selected_action_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertEqual(boundary["intended_sandbox_action"], "check_before_retry")
        self.assertEqual(boundary["sandbox_id"], "phase0_toy_sandbox_obstacle_retry_failed")
        self.assertTrue(boundary["intent_only"])
        self.assertFalse(boundary["action_execution_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-one-step-sandbox-action-intent-minimal-check")

        self.assertEqual(result["command"], "run-one-step-sandbox-action-intent-minimal-check")
        self.assertEqual(result["summary"]["valid_sandbox_action_intent_result_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-one-step-sandbox-action-intent-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-one-step-sandbox-action-intent-minimal-check")
        self.assertEqual(result["summary"]["intent_action_count"], 1)


if __name__ == "__main__":
    unittest.main()
