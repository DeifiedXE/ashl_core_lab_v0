import unittest
from copy import deepcopy

from ashl_core.sandbox_action_execution_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    SELECTED_ACTION,
    build_sandbox_action_execution_record,
    build_sandbox_action_execution_result_record,
    run_sandbox_action_execution_minimal_check,
    validate_sandbox_action_execution_record,
    validate_sandbox_action_execution_result_record,
)
from ashl_core.teaching_cli import run_command


class SandboxActionExecutionMinimalTests(unittest.TestCase):
    def test_valid_sandbox_action_execution(self):
        record = build_sandbox_action_execution_record()
        result = validate_sandbox_action_execution_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("2026-06-09-b95", BOUNDARY_INDEX_BEFORE)
        self.assertEqual("2026-06-09-b96", BOUNDARY_INDEX_AFTER)
        self.assertEqual("sandbox_action_execution", record["record_type"])
        self.assertEqual("sandbox_selected_action_and_execution_approval_b95", record["source_selected_action_boundary"])
        self.assertEqual("phase0_level3_sandbox_only", record["sandbox_scope"])
        self.assertEqual("sandbox_only", record["execution_scope"])
        self.assertEqual(SELECTED_ACTION, record["selected_action"])
        self.assertTrue(record["selected_action_created"])
        self.assertTrue(record["execution_allowed"])
        self.assertTrue(record["action_executed"])
        self.assertEqual(1, record["execution_count"])
        self.assertEqual(1, record["execution_budget"])
        self.assertEqual(0, record["budget_remaining"])
        self.assertTrue(record["stop_condition_met"])
        self.assertEqual("local_context_observed", record["execution_result"])
        self.assertFalse(record["final_action_created"])
        self.assertFalse(record["direct_command_created"])

    def test_valid_execution_result(self):
        record = build_sandbox_action_execution_result_record()
        result = validate_sandbox_action_execution_result_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("sandbox_action_execution_result", record["record_type"])
        self.assertEqual("sandbox_action_execution", record["source_execution_record_type"])
        self.assertEqual(SELECTED_ACTION, record["selected_action"])
        self.assertEqual("local_context_observed", record["execution_result"])
        self.assertTrue(record["result_recorded"])
        self.assertFalse(record["final_action_created"])

    def test_cli_command_returns_ok(self):
        result = run_command("run-sandbox-action-execution-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_execution_count"])

    def test_invalid_missing_b95_selected_action_source(self):
        self.assertInvalidExecution("source_selected_action_boundary", "missing_b95_selected_action_source")

    def test_invalid_selected_action_differs(self):
        self.assertInvalidExecution("selected_action", "check_before_retry")
        self.assertInvalidResult("selected_action", "check_before_retry")

    def test_invalid_execution_outside_sandbox_scope(self):
        self.assertInvalidExecution("sandbox_scope", "production_scope")
        self.assertInvalidExecution("execution_scope", "runtime")

    def test_invalid_execution_count_over_one(self):
        self.assertInvalidExecution("execution_count", 2)
        self.assertInvalidResult("execution_count", 2)

    def test_invalid_execution_budget_over_one(self):
        self.assertInvalidExecution("execution_budget", 2)

    def test_invalid_budget_remaining_negative(self):
        self.assertInvalidExecution("budget_remaining", -1)

    def test_invalid_missing_stop_condition(self):
        self.assertInvalidExecution("stop_condition_met", False)
        self.assertInvalidResult("stop_condition_met", False)

    def test_invalid_result_outside_vocabulary(self):
        self.assertInvalidExecution("execution_result", "free_text_result")
        self.assertInvalidResult("execution_result", "free_text_result")

    def test_invalid_natural_language_action(self):
        self.assertInvalidExecution("natural_language_action_executed", True)

    def test_invalid_external_tool_action(self):
        self.assertInvalidExecution("external_tool_action_executed", True)

    def test_invalid_final_action(self):
        self.assertInvalidExecution("final_action_created", True)
        self.assertInvalidResult("final_action_created", True)

    def test_invalid_direct_command(self):
        self.assertInvalidExecution("direct_command_created", True)
        self.assertInvalidResult("direct_command_created", True)

    def test_invalid_production_behavior(self):
        self.assertInvalidExecution("production_behavior_changed", True)
        self.assertInvalidResult("production_behavior_changed", True)

    def test_invalid_persistent_rule(self):
        self.assertInvalidExecution("persistent_rule_created", True)

    def test_invalid_persistent_trust_doubt_update(self):
        self.assertInvalidExecution("persistent_trust_doubt_update_performed", True)

    def test_invalid_cross_session_feedback_persistence(self):
        self.assertInvalidExecution("cross_session_feedback_persistence", True)

    def test_invalid_memory_write(self):
        self.assertInvalidExecution("memory_write_performed", True)
        self.assertInvalidExecution("retained_jsonl_write_performed", True)
        self.assertInvalidResult("memory_write_performed", True)

    def test_invalid_retention_write(self):
        self.assertInvalidExecution("retention_write_performed", True)
        self.assertInvalidResult("retention_write_performed", True)

    def test_invalid_predictor_read_influence_mutation(self):
        self.assertInvalidExecution("predictor_read_enabled", True)
        self.assertInvalidExecution("predictor_influence_enabled", True)
        self.assertInvalidExecution("predictor_mutation_performed", True)
        self.assertInvalidResult("predictor_mutation_performed", True)

    def test_invalid_proof_claim(self):
        self.assertInvalidExecution("proof_of_learning_claim_allowed", True)
        self.assertInvalidResult("proof_of_learning_claim_allowed", True)

    def test_invalid_autonomous_learning_action_claim(self):
        self.assertInvalidExecution("autonomous_learning_claim_allowed", True)
        self.assertInvalidExecution("autonomous_action_claim_allowed", True)

    def test_invalid_llm_used(self):
        self.assertInvalidExecution("llm_used", True)

    def test_invalid_result_missing_execution_source(self):
        self.assertInvalidResult("source_execution_record_type", "missing_execution_record")

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_action_execution_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_execution_count"])
        self.assertGreaterEqual(summary["invalid_execution_count"], 25)
        self.assertEqual(1, summary["valid_result_count"])
        self.assertGreaterEqual(summary["invalid_result_count"], 14)
        self.assertEqual(1, summary["selected_action_source_checked_count"])
        self.assertEqual(1, summary["execution_scope_checked_count"])
        self.assertEqual(1, summary["execution_budget_checked_count"])
        self.assertEqual(1, summary["stop_condition_checked_count"])
        self.assertEqual(1, summary["result_checked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["direct_command_blocked_count"])
        self.assertEqual(1, summary["persistent_update_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_sandbox_action_execution_minimal_checks_passed"])

    def assertInvalidExecution(self, field, value):
        record = deepcopy(build_sandbox_action_execution_record())
        record[field] = value
        self.assertFalse(validate_sandbox_action_execution_record(record)["valid"])

    def assertInvalidResult(self, field, value):
        record = deepcopy(build_sandbox_action_execution_result_record())
        record[field] = value
        self.assertFalse(validate_sandbox_action_execution_result_record(record)["valid"])


if __name__ == "__main__":
    unittest.main()
