import json
import subprocess
import sys
import unittest

from ashl_core.one_step_sandbox_action_execution_minimal import (
    build_one_step_sandbox_action_execution,
    run_one_step_sandbox_action_execution_minimal_check,
    validate_one_step_sandbox_action_execution,
)
from ashl_core.one_step_sandbox_action_intent_minimal import build_one_step_sandbox_action_intent
from ashl_core.teaching_cli import run_command


class OneStepSandboxActionExecutionMinimalTests(unittest.TestCase):
    def _valid_execution(self):
        return build_one_step_sandbox_action_execution()

    def _assert_invalid(self, record, error_code):
        validation = validate_one_step_sandbox_action_execution(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_one_step_sandbox_action_execution_is_created(self):
        record = self._valid_execution()
        validation = validate_one_step_sandbox_action_execution(record)

        self.assertTrue(validation["valid"])
        self.assertEqual(record["execution_mode"], "one_step_sandbox_execution_only")
        self.assertEqual(record["executed_sandbox_action"], "check_before_retry")

    def test_valid_execution_reuses_one_step_sandbox_action_intent(self):
        intent = build_one_step_sandbox_action_intent()
        record = build_one_step_sandbox_action_execution(intent)

        self.assertEqual(record["source_sandbox_action_intent_id"], intent["sandbox_action_intent_id"])
        self.assertEqual(record["executed_sandbox_action"], intent["intended_sandbox_action"])

    def test_sandbox_before_state_is_obstacle_retry_failed(self):
        before = self._valid_execution()["sandbox_before"]

        self.assertEqual(before["sandbox_id"], "phase0_toy_sandbox_obstacle_retry_failed")
        self.assertEqual(before["scenario_id"], "obstacle_retry_failed_same_state")
        self.assertEqual(before["exact_key"], "obstacle_retry_failed")
        self.assertTrue(before["obstacle_ahead"])
        self.assertTrue(before["previous_action_failed"])
        self.assertEqual(before["previous_failure_reason"], "blocked_by_obstacle")
        self.assertFalse(before["production_context"])

    def test_sandbox_after_records_check_without_retry_or_movement(self):
        after = self._valid_execution()["sandbox_after"]

        self.assertTrue(after["checked_before_retry"])
        self.assertTrue(after["obstacle_detected"])
        self.assertFalse(after["retry_same_action_executed"])
        self.assertFalse(after["movement_executed"])
        self.assertFalse(after["production_context"])

    def test_execution_outcome_is_sandbox_record_only(self):
        outcome = self._valid_execution()["execution_outcome"]

        self.assertTrue(outcome["sandbox_action_executed"])
        self.assertTrue(outcome["executed_once"])
        self.assertEqual(outcome["outcome_type"], "sandbox_check_result")
        self.assertFalse(outcome["real_world_effect"])
        self.assertFalse(outcome["production_effect"])
        self.assertEqual(outcome["state_mutation_scope"], "sandbox_record_only")

    def test_audit_trace_and_rollback_are_recorded(self):
        record = self._valid_execution()
        audit = record["audit_trace"]
        rollback = record["rollback_record"]

        self.assertTrue(audit["audit_trace_recorded"])
        self.assertTrue(audit["source_intent_checked"])
        self.assertTrue(audit["execution_boundary_checked"])
        self.assertTrue(audit["blocked_flags_checked"])
        self.assertTrue(rollback["rollback_available"])
        self.assertEqual(rollback["rollback_scope"], "sandbox_record_only")

    def test_bad_execution_mode_blocks(self):
        record = self._valid_execution()
        record["execution_mode"] = "production_execution"
        self._assert_invalid(record, "execution_mode_not_one_step_sandbox_execution_only")

    def test_wrong_executed_sandbox_action_blocks(self):
        record = self._valid_execution()
        record["executed_sandbox_action"] = "retry_same_action"
        self._assert_invalid(record, "executed_sandbox_action_not_check_before_retry")

    def test_wrong_sandbox_context_blocks(self):
        cases = {
            "sandbox_id": "sandbox_before_sandbox_id_not_phase0_toy_sandbox_obstacle_retry_failed",
            "scenario_id": "scenario_id_not_obstacle_retry_failed_same_state",
            "exact_key": "exact_key_not_obstacle_retry_failed",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_execution()
                record["sandbox_before"][field] = "mismatch"
                self._assert_invalid(record, error_code)

    def test_production_context_true_blocks(self):
        record = self._valid_execution()
        record["sandbox_before"]["production_context"] = True
        self._assert_invalid(record, "production_context_not_false")

    def test_retry_and_movement_execution_block(self):
        cases = {
            "retry_same_action_executed": "retry_same_action_executed_not_false",
            "movement_executed": "movement_executed_not_false",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_execution()
                record["sandbox_after"][field] = True
                self._assert_invalid(record, error_code)

    def test_real_world_and_production_effects_block(self):
        cases = {
            "real_world_effect": "real_world_effect_not_false",
            "production_effect": "production_effect_not_false",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_execution()
                record["execution_outcome"][field] = True
                self._assert_invalid(record, error_code)

    def test_wrong_state_mutation_scope_blocks(self):
        record = self._valid_execution()
        record["execution_outcome"]["state_mutation_scope"] = "persistent_policy"
        self._assert_invalid(record, "state_mutation_scope_not_sandbox_record_only")

    def test_audit_flags_false_block(self):
        cases = {
            "audit_trace_required": "audit_trace_required_not_true",
            "audit_trace_recorded": "audit_trace_recorded_not_true",
            "source_intent_checked": "source_intent_checked_not_true",
            "execution_boundary_checked": "execution_boundary_checked_not_true",
            "blocked_flags_checked": "blocked_flags_checked_not_true",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_execution()
                record["audit_trace"][field] = False
                self._assert_invalid(record, error_code)

    def test_rollback_flags_false_block(self):
        cases = {
            "rollback_available": "rollback_available_not_true",
            "rollback_required_before_execution": "rollback_required_before_execution_not_true",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_execution()
                record["rollback_record"][field] = False
                self._assert_invalid(record, error_code)

    def test_empty_human_summary_fields_block(self):
        cases = {
            "what_executed": "what_executed_empty_or_not_string",
            "what_did_not_happen": "what_did_not_happen_empty_or_not_string",
            "plain_result": "plain_result_empty_or_not_string",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_execution()
                record["human_summary"][field] = ""
                self._assert_invalid(record, error_code)

    def test_blocked_flags_true_block(self):
        cases = {
            "production_action_selection": "production_action_selection_enabled",
            "runtime_action_selection": "runtime_action_selection_enabled",
            "selected_action_created": "selected_action_created_enabled",
            "final_action_created": "final_action_created_enabled",
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
                record = self._valid_execution()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_one_step_sandbox_action_execution_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-one-step-sandbox-action-execution-minimal-check")
        self.assertEqual(result["flow"], "one_step_sandbox_action_execution_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["sandbox_execution_result_count"], 51)
        self.assertEqual(summary["valid_sandbox_execution_result_count"], 1)
        self.assertEqual(summary["invalid_sandbox_execution_result_count"], 50)
        self.assertEqual(summary["sandbox_action_executed_count"], 1)
        self.assertEqual(summary["executed_once_count"], 1)
        self.assertEqual(summary["check_before_retry_executed_count"], 1)
        self.assertEqual(summary["obstacle_detected_count"], 1)
        self.assertEqual(summary["audit_trace_recorded_count"], 1)
        self.assertEqual(summary["rollback_available_count"], 1)
        self.assertEqual(summary["sandbox_record_only_count"], 1)
        self.assertEqual(summary["real_world_effect_blocked_count"], 1)
        self.assertEqual(summary["production_effect_blocked_count"], 1)
        self.assertEqual(summary["movement_executed_blocked_count"], 1)
        self.assertEqual(summary["retry_same_action_executed_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertEqual(boundary["executed_sandbox_action"], "check_before_retry")
        self.assertTrue(boundary["sandbox_action_executed"])
        self.assertFalse(boundary["production_effect_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-one-step-sandbox-action-execution-minimal-check")

        self.assertEqual(result["command"], "run-one-step-sandbox-action-execution-minimal-check")
        self.assertEqual(result["summary"]["valid_sandbox_execution_result_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-one-step-sandbox-action-execution-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-one-step-sandbox-action-execution-minimal-check")
        self.assertEqual(result["summary"]["sandbox_action_executed_count"], 1)


if __name__ == "__main__":
    unittest.main()
