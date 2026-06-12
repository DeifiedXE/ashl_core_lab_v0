import json
import subprocess
import sys
import unittest

from ashl_core.one_step_sandbox_action_execution_minimal import build_one_step_sandbox_action_execution
from ashl_core.sandbox_execution_outcome_integration_minimal import (
    build_sandbox_action_outcome_trace,
    build_sandbox_execution_outcome_pair,
    run_sandbox_execution_outcome_integration_minimal_check,
    validate_sandbox_action_outcome_trace,
    validate_sandbox_execution_outcome_pair,
)
from ashl_core.teaching_cli import run_command


class SandboxExecutionOutcomeIntegrationMinimalTests(unittest.TestCase):
    def _pair(self):
        return build_sandbox_execution_outcome_pair()

    def _trace(self):
        return build_sandbox_action_outcome_trace(self._pair())

    def _assert_pair_invalid(self, record, error_code):
        validation = validate_sandbox_execution_outcome_pair(record)
        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def _assert_trace_invalid(self, record, error_code):
        validation = validate_sandbox_action_outcome_trace(record)
        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_sandbox_execution_outcome_pair_is_created(self):
        pair = self._pair()
        validation = validate_sandbox_execution_outcome_pair(pair)

        self.assertTrue(validation["valid"])
        self.assertEqual(pair["action_context"]["executed_sandbox_action"], "check_before_retry")

    def test_valid_action_outcome_trace_is_created(self):
        trace = self._trace()
        validation = validate_sandbox_action_outcome_trace(trace)

        self.assertTrue(validation["valid"])
        self.assertEqual(trace["trace_mode"], "sandbox_execution_outcome_trace_only")

    def test_outcome_pair_reuses_one_step_sandbox_execution(self):
        execution = build_one_step_sandbox_action_execution()
        pair = build_sandbox_execution_outcome_pair(execution)

        self.assertEqual(pair["source_sandbox_execution_id"], execution["sandbox_execution_id"])
        self.assertEqual(pair["actual_outcome"]["checked_before_retry"], True)

    def test_expected_outcome_matches_actual_outcome(self):
        pair = self._pair()

        self.assertEqual(pair["expected_outcome"], pair["actual_outcome"])
        self.assertTrue(pair["comparison_result"]["outcome_match"])
        self.assertFalse(pair["comparison_result"]["failure_detected"])
        self.assertTrue(pair["comparison_result"]["sandbox_check_success"])
        self.assertEqual(pair["comparison_result"]["mismatch_keys"], [])

    def test_required_outcome_values(self):
        actual = self._pair()["actual_outcome"]

        self.assertTrue(actual["checked_before_retry"])
        self.assertTrue(actual["obstacle_detected"])
        self.assertFalse(actual["retry_same_action_executed"])
        self.assertFalse(actual["movement_executed"])
        self.assertFalse(actual["real_world_effect"])
        self.assertFalse(actual["production_effect"])

    def test_trace_can_feed_lesson_review_evidence_only(self):
        trace = self._trace()
        source = trace["lesson_evidence_candidate_source"]

        self.assertTrue(trace["trace_result"]["evidence_available"])
        self.assertTrue(source["can_feed_lesson_evidence_candidate"])
        self.assertTrue(source["requires_human_review_before_lesson"])
        self.assertFalse(source["lesson_applied"])
        self.assertFalse(source["memory_write"])
        self.assertFalse(source["retention_write"])

    def test_bad_sandbox_context_blocks(self):
        cases = {
            "sandbox_id": "sandbox_id_not_phase0_toy_sandbox_obstacle_retry_failed",
            "executed_sandbox_action": "executed_sandbox_action_not_check_before_retry",
            "state_mutation_scope": "state_mutation_scope_not_sandbox_record_only",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                pair = self._pair()
                pair["action_context"][field] = "bad"
                self._assert_pair_invalid(pair, error_code)

    def test_bad_actual_outcome_blocks(self):
        cases = {
            "checked_before_retry": (False, "actual_checked_before_retry_not_true"),
            "obstacle_detected": (False, "actual_obstacle_detected_not_true"),
            "retry_same_action_executed": (True, "actual_retry_same_action_executed_not_false"),
            "movement_executed": (True, "actual_movement_executed_not_false"),
            "real_world_effect": (True, "actual_real_world_effect_not_false"),
            "production_effect": (True, "actual_production_effect_not_false"),
        }
        for field, (value, error_code) in cases.items():
            with self.subTest(field=field):
                pair = self._pair()
                pair["actual_outcome"][field] = value
                self._assert_pair_invalid(pair, error_code)

    def test_bad_comparison_result_blocks(self):
        cases = {
            "outcome_match": (False, "outcome_match_not_true"),
            "failure_detected": (True, "failure_detected_not_false"),
            "sandbox_check_success": (False, "sandbox_check_success_not_true"),
            "mismatch_keys": (["obstacle_detected"], "mismatch_keys_not_empty"),
        }
        for field, (value, error_code) in cases.items():
            with self.subTest(field=field):
                pair = self._pair()
                pair["comparison_result"][field] = value
                self._assert_pair_invalid(pair, error_code)

    def test_bad_trace_result_blocks(self):
        cases = {
            "outcome_match": (False, "trace_outcome_match_not_true"),
            "failure_detected": (True, "trace_failure_detected_not_false"),
            "evidence_available": (False, "trace_evidence_available_not_true"),
        }
        for field, (value, error_code) in cases.items():
            with self.subTest(field=field):
                trace = self._trace()
                trace["trace_result"][field] = value
                self._assert_trace_invalid(trace, error_code)

    def test_lesson_memory_retention_writes_block(self):
        cases = {
            "lesson_applied": "lesson_applied_not_false",
            "memory_write": "memory_write_not_false",
            "retention_write": "retention_write_not_false",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                trace = self._trace()
                trace["lesson_evidence_candidate_source"][field] = True
                self._assert_trace_invalid(trace, error_code)

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
            "lesson_applied": "lesson_applied_enabled",
            "memory_write": "memory_write_enabled",
            "new_retention_written": "new_retention_written_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                pair = self._pair()
                trace = self._trace()
                pair["blocked_flags"][flag] = True
                trace["blocked_flags"][flag] = True
                self._assert_pair_invalid(pair, error_code)
                self._assert_trace_invalid(trace, error_code)

    def test_empty_human_summary_fields_block(self):
        pair = self._pair()
        pair["human_summary"]["plain_result"] = ""
        self._assert_pair_invalid(pair, "plain_result_empty_or_not_string")

        trace = self._trace()
        trace["human_summary"]["plain_result"] = ""
        self._assert_trace_invalid(trace, "plain_result_empty_or_not_string")

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_execution_outcome_integration_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-sandbox-execution-outcome-integration-minimal-check")
        self.assertEqual(result["flow"], "sandbox_execution_outcome_integration_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["sandbox_outcome_integration_result_count"], 61)
        self.assertEqual(summary["valid_outcome_pair_count"], 1)
        self.assertEqual(summary["valid_action_outcome_trace_count"], 1)
        self.assertEqual(summary["invalid_outcome_pair_count"], 32)
        self.assertEqual(summary["invalid_action_outcome_trace_count"], 27)
        self.assertEqual(summary["outcome_match_count"], 1)
        self.assertEqual(summary["sandbox_check_success_count"], 1)
        self.assertEqual(summary["evidence_available_count"], 1)
        self.assertEqual(summary["can_feed_lesson_evidence_candidate_count"], 1)
        self.assertEqual(summary["requires_human_review_before_lesson_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["retention_write_blocked_count"], 1)
        self.assertFalse(boundary["new_sandbox_execution_added"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-sandbox-execution-outcome-integration-minimal-check")

        self.assertEqual(result["command"], "run-sandbox-execution-outcome-integration-minimal-check")
        self.assertEqual(result["summary"]["valid_outcome_pair_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-sandbox-execution-outcome-integration-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-sandbox-execution-outcome-integration-minimal-check")
        self.assertEqual(result["summary"]["valid_action_outcome_trace_count"], 1)


if __name__ == "__main__":
    unittest.main()
