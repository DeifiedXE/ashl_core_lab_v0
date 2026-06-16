import unittest
from copy import deepcopy

from ashl_core.sandbox_direct_command_execution_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    DIRECT_COMMAND,
    EXECUTION_RESULT,
    build_sandbox_direct_command_execution_record,
    build_sandbox_direct_command_execution_result_record,
    run_sandbox_direct_command_execution_minimal_check,
    validate_sandbox_direct_command_execution_record,
    validate_sandbox_direct_command_execution_result_record,
)


class SandboxDirectCommandExecutionMinimalTests(unittest.TestCase):
    def setUp(self):
        self.execution = build_sandbox_direct_command_execution_record()
        self.result_record = build_sandbox_direct_command_execution_result_record(self.execution)

    def assertInvalidExecution(self, field, value, expected_error):
        record = deepcopy(self.execution)
        record[field] = value
        result = validate_sandbox_direct_command_execution_record(record)
        self.assertFalse(result["valid"])
        self.assertIn(expected_error, result["error_codes"])

    def assertInvalidResult(self, field, value, expected_error):
        record = deepcopy(self.result_record)
        record[field] = value
        result = validate_sandbox_direct_command_execution_result_record(record)
        self.assertFalse(result["valid"])
        self.assertIn(expected_error, result["error_codes"])

    def test_valid_direct_command_execution_is_created(self):
        result = validate_sandbox_direct_command_execution_record(self.execution)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("sandbox_direct_command_execution", self.execution["record_type"])
        self.assertEqual(DIRECT_COMMAND, self.execution["direct_command"])
        self.assertEqual(BOUNDARY_INDEX_BEFORE, self.execution["source_boundary_index"])

    def test_reuses_b102_execution_approval_boundary(self):
        result = validate_sandbox_direct_command_execution_record(self.execution)
        self.assertTrue(result["execution_approval_source_checked"])
        self.assertEqual(
            "sandbox_direct_command_execution_approval_boundary_b102",
            self.execution["source_execution_approval_boundary"],
        )

    def test_executes_once_inside_sandbox_scope(self):
        result = validate_sandbox_direct_command_execution_record(self.execution)
        self.assertTrue(result["sandbox_scope_checked"])
        self.assertTrue(result["direct_command_execution_checked"])
        self.assertTrue(result["execution_budget_checked"])
        self.assertTrue(self.execution["direct_command_executed"])
        self.assertEqual(1, self.execution["execution_count"])
        self.assertEqual(1, self.execution["execution_budget"])
        self.assertEqual(0, self.execution["budget_remaining"])

    def test_result_record_is_created(self):
        result = validate_sandbox_direct_command_execution_result_record(self.result_record)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertTrue(result["execution_source_checked"])
        self.assertTrue(result["result_checked"])
        self.assertEqual(EXECUTION_RESULT, self.result_record["execution_result"])
        self.assertTrue(self.result_record["execution_result_created"])
        self.assertTrue(self.result_record["result_recorded"])

    def test_feedback_and_production_are_blocked(self):
        execution_result = validate_sandbox_direct_command_execution_record(self.execution)
        result_validation = validate_sandbox_direct_command_execution_result_record(self.result_record)
        self.assertTrue(execution_result["feedback_loop_blocked"])
        self.assertTrue(result_validation["feedback_loop_blocked"])
        self.assertTrue(execution_result["production_behavior_blocked"])
        self.assertTrue(result_validation["production_behavior_blocked"])
        self.assertFalse(self.execution["feedback_loop_created"])
        self.assertFalse(self.execution["production_behavior_changed"])

    def test_memory_retention_predictor_navigation_ui_and_proof_are_blocked(self):
        execution_result = validate_sandbox_direct_command_execution_record(self.execution)
        result_validation = validate_sandbox_direct_command_execution_result_record(self.result_record)
        self.assertTrue(execution_result["memory_write_blocked"])
        self.assertTrue(result_validation["memory_write_blocked"])
        self.assertTrue(execution_result["retention_blocked"])
        self.assertTrue(result_validation["retention_blocked"])
        self.assertTrue(execution_result["predictor_mutation_blocked"])
        self.assertTrue(result_validation["predictor_mutation_blocked"])
        self.assertTrue(execution_result["real_navigation_blocked"])
        self.assertTrue(result_validation["real_navigation_blocked"])
        self.assertTrue(execution_result["ui_behavior_blocked"])
        self.assertTrue(result_validation["ui_behavior_blocked"])
        self.assertTrue(execution_result["proof_claim_blocked"])
        self.assertTrue(result_validation["proof_claim_blocked"])

    def test_invalid_missing_b102_source_blocks(self):
        self.assertInvalidExecution(
            "source_execution_approval_boundary_record",
            {},
            "missing_or_invalid_b102_execution_approval_boundary_source",
        )

    def test_invalid_scope_and_command_blocks(self):
        self.assertInvalidExecution("sandbox_scope", "production", "sandbox_scope_not_expected")
        self.assertInvalidExecution("execution_scope", "production", "execution_scope_not_expected")
        self.assertInvalidExecution("direct_command", "sandbox.retry_same_action", "direct_command_not_expected")

    def test_invalid_execution_fields_block(self):
        self.assertInvalidExecution("direct_command_executed", False, "direct_command_executed_not_true")
        self.assertInvalidExecution("execution_allowed", False, "execution_allowed_not_true")
        self.assertInvalidExecution("execution_count", 2, "execution_count_not_one")
        self.assertInvalidExecution("execution_budget", 2, "execution_budget_not_one")
        self.assertInvalidExecution("budget_remaining", -1, "budget_remaining_not_zero")

    def test_invalid_result_fields_block(self):
        self.assertInvalidResult("direct_command_executed", False, "direct_command_executed_not_true")
        self.assertInvalidResult("execution_result_created", False, "execution_result_created_not_true")
        self.assertInvalidResult("result_recorded", False, "result_recorded_not_true")
        self.assertInvalidResult("execution_result", "free_text_result", "execution_result_not_expected")

    def test_invalid_feedback_production_memory_and_proof_block(self):
        for field in (
            "feedback_loop_created",
            "production_behavior_changed",
            "real_navigation_changed",
            "ui_behavior_changed",
            "memory_write_performed",
            "retention_write_performed",
            "predictor_mutation_performed",
            "proof_of_learning_claim_allowed",
        ):
            with self.subTest(field=field):
                self.assertInvalidResult(field, True, f"{field}_not_false")

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_direct_command_execution_minimal_check()
        summary = result["summary"]
        boundary = result["boundary"]
        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_direct_command_execution_count"])
        self.assertEqual(39, summary["invalid_direct_command_execution_count"])
        self.assertEqual(1, summary["valid_direct_command_execution_result_count"])
        self.assertEqual(20, summary["invalid_direct_command_execution_result_count"])
        self.assertEqual(1, summary["execution_approval_source_checked_count"])
        self.assertEqual(1, summary["direct_command_execution_checked_count"])
        self.assertEqual(1, summary["execution_budget_checked_count"])
        self.assertEqual(1, summary["result_checked_count"])
        self.assertEqual(1, summary["feedback_loop_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_sandbox_direct_command_execution_minimal_checks_passed"])
        self.assertEqual(BOUNDARY_INDEX_BEFORE, boundary["boundary_index_version_before"])
        self.assertEqual(BOUNDARY_INDEX_AFTER, boundary["boundary_index_version_after"])


if __name__ == "__main__":
    unittest.main()
