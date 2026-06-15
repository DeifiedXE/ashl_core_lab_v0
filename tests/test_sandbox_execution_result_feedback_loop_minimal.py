import unittest
from copy import deepcopy

from ashl_core.sandbox_execution_result_feedback_loop_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    build_sandbox_execution_ephemeral_feedback_application,
    build_sandbox_execution_feedback_loop_rollback_record,
    build_sandbox_execution_feedback_reordering_record,
    build_sandbox_execution_result_feedback_trace,
    run_sandbox_execution_result_feedback_loop_minimal_check,
    validate_sandbox_execution_ephemeral_feedback_application,
    validate_sandbox_execution_feedback_loop_rollback_record,
    validate_sandbox_execution_feedback_reordering_record,
    validate_sandbox_execution_result_feedback_trace,
)
from ashl_core.teaching_cli import run_command


class SandboxExecutionResultFeedbackLoopMinimalTests(unittest.TestCase):
    def test_valid_feedback_trace(self):
        record = build_sandbox_execution_result_feedback_trace()
        result = validate_sandbox_execution_result_feedback_trace(record)

        self.assertTrue(result["valid"])
        self.assertEqual("2026-06-09-b96", BOUNDARY_INDEX_BEFORE)
        self.assertEqual("2026-06-09-b97", BOUNDARY_INDEX_AFTER)
        self.assertEqual("sandbox_execution_result_feedback_trace", record["record_type"])
        self.assertEqual("sandbox_action_execution_b96", record["source_sandbox_action_execution"])
        self.assertEqual("observe_or_alternative_probe", record["selected_action"])
        self.assertEqual("local_context_observed", record["execution_result"])
        self.assertEqual(1, record["execution_count"])
        self.assertEqual(1, record["execution_budget"])
        self.assertTrue(record["stop_condition_met"])
        self.assertEqual("trace_only_feedback_generated", record["feedback_status"])

    def test_valid_ephemeral_application(self):
        record = build_sandbox_execution_ephemeral_feedback_application()
        result = validate_sandbox_execution_ephemeral_feedback_application(record)

        self.assertTrue(result["valid"])
        self.assertEqual("sandbox_execution_ephemeral_feedback_application", record["record_type"])
        self.assertEqual("applied_same_session_execution_feedback", record["application_status"])
        self.assertEqual("same_sandbox_session_only", record["application_scope"])
        self.assertLess(record["doubt_after_ephemeral"], record["doubt_before"])
        self.assertGreater(record["selected_action_confidence_after_ephemeral"], record["selected_action_confidence_before"])
        self.assertLessEqual(record["direct_retry_weight_after_ephemeral"], record["direct_retry_weight_before"])

    def test_valid_same_session_reordering(self):
        record = build_sandbox_execution_feedback_reordering_record()
        result = validate_sandbox_execution_feedback_reordering_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("sandbox_execution_feedback_reordering", record["record_type"])
        self.assertTrue(record["selected_action_remains_ranked_first"])
        self.assertTrue(record["check_before_retry_ranked_before_direct_retry"])
        self.assertTrue(record["direct_retry_ranked_last"])
        self.assertEqual("observe_or_alternative_probe", record["candidate_actions_after_reordering"][0])
        self.assertEqual("retry_same_action_without_check", record["candidate_actions_after_reordering"][-1])

    def test_valid_rollback(self):
        record = build_sandbox_execution_feedback_loop_rollback_record()
        result = validate_sandbox_execution_feedback_loop_rollback_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("sandbox_execution_feedback_loop_rollback", record["record_type"])
        self.assertEqual("sandbox_execution_feedback_loop_rolled_back", record["rollback_status"])
        self.assertTrue(record["session_end_triggered"])
        self.assertFalse(record["dirty_state_after_rollback"])
        self.assertEqual(0.61, record["doubt_restored"])
        self.assertEqual(0.50, record["selected_action_confidence_restored"])
        self.assertEqual(0.35, record["direct_retry_weight_restored"])

    def test_cli_command_returns_ok(self):
        result = run_command("run-sandbox-execution-result-feedback-loop-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_feedback_trace_count"])

    def test_invalid_missing_b96_execution_source(self):
        self.assertInvalidFeedbackTrace("source_sandbox_action_execution_record", {})

    def test_invalid_execution_result_missing(self):
        self.assertInvalidFeedbackTrace("execution_result", "")

    def test_invalid_execution_count_not_one(self):
        self.assertInvalidFeedbackTrace("execution_count", 2)

    def test_invalid_execution_budget_not_one(self):
        self.assertInvalidFeedbackTrace("execution_budget", 2)

    def test_invalid_stop_condition_not_met(self):
        self.assertInvalidFeedbackTrace("stop_condition_met", False)

    def test_invalid_persistent_feedback_application(self):
        record = build_sandbox_execution_result_feedback_trace()
        record["doubt_feedback"]["applied_persistently"] = True
        self.assertFalse(validate_sandbox_execution_result_feedback_trace(record)["valid"])

    def test_invalid_runtime_feedback_outside_ephemeral_application(self):
        self.assertInvalidFeedbackTrace("feedback_applied_to_runtime", True)

    def test_invalid_cross_session_feedback(self):
        self.assertInvalidApplication("cross_session_available", True)
        self.assertInvalidApplication("application_scope", "cross_session")
        self.assertInvalidReordering("cross_session_available", True)
        self.assertInvalidRollback("cross_session_available", True)

    def test_invalid_direct_retry_weight_increases(self):
        self.assertInvalidApplication("direct_retry_weight_after_ephemeral", 0.40)

    def test_invalid_final_action(self):
        self.assertInvalidFeedbackTrace("final_action_created", True)
        self.assertInvalidApplication("final_action_created", True)
        self.assertInvalidReordering("final_action_created", True)
        self.assertInvalidRollback("final_action_created", True)

    def test_invalid_direct_command(self):
        self.assertInvalidFeedbackTrace("direct_command_created", True)
        self.assertInvalidApplication("direct_command_created", True)
        self.assertInvalidReordering("direct_command_created", True)
        self.assertInvalidRollback("direct_command_created", True)

    def test_invalid_persistent_rule(self):
        self.assertInvalidFeedbackTrace("persistent_rule_created", True)
        self.assertInvalidApplication("persistent_rule_created", True)
        self.assertInvalidReordering("persistent_rule_created", True)

    def test_invalid_memory_write(self):
        self.assertInvalidFeedbackTrace("memory_write_performed", True)
        self.assertInvalidFeedbackTrace("retained_jsonl_write_performed", True)
        self.assertInvalidApplication("memory_write_performed", True)
        self.assertInvalidApplication("retained_jsonl_write_performed", True)
        self.assertInvalidRollback("memory_write_performed", True)

    def test_invalid_retention_write(self):
        self.assertInvalidFeedbackTrace("retention_write_performed", True)
        self.assertInvalidApplication("retention_write_performed", True)
        self.assertInvalidReordering("retention_write_performed", True)
        self.assertInvalidRollback("retention_write_performed", True)

    def test_invalid_predictor_read_influence_mutation(self):
        for field in ("predictor_read_enabled", "predictor_influence_enabled", "predictor_mutation_performed"):
            with self.subTest(field=field):
                self.assertInvalidFeedbackTrace(field, True)
                self.assertInvalidApplication(field, True)
                self.assertInvalidReordering(field, True)
                self.assertInvalidRollback(field, True)

    def test_invalid_production_behavior(self):
        self.assertInvalidFeedbackTrace("production_behavior_changed", True)
        self.assertInvalidApplication("production_behavior_changed", True)
        self.assertInvalidReordering("production_behavior_changed", True)

    def test_invalid_proof_claim(self):
        self.assertInvalidFeedbackTrace("proof_of_learning_claim_allowed", True)
        self.assertInvalidApplication("proof_of_learning_claim_allowed", True)
        self.assertInvalidReordering("proof_of_learning_claim_allowed", True)
        self.assertInvalidRollback("proof_of_learning_claim_allowed", True)

    def test_invalid_autonomous_learning_action_claim(self):
        for field in ("autonomous_learning_claim_allowed", "autonomous_action_claim_allowed"):
            with self.subTest(field=field):
                self.assertInvalidFeedbackTrace(field, True)
                self.assertInvalidApplication(field, True)
                self.assertInvalidReordering(field, True)
                self.assertInvalidRollback(field, True)

    def test_invalid_llm_used_true(self):
        self.assertInvalidFeedbackTrace("llm_used", True)
        self.assertInvalidApplication("llm_used", True)
        self.assertInvalidReordering("llm_used", True)

    def test_invalid_rollback_missing(self):
        self.assertInvalidApplication("rollback_required", False)
        self.assertInvalidApplication("rollback_available", False)
        self.assertInvalidReordering("rollback_required", False)
        self.assertInvalidReordering("rollback_available", False)
        self.assertInvalidRollback("session_end_triggered", False)

    def test_invalid_dirty_rollback(self):
        self.assertInvalidRollback("dirty_state_after_rollback", True)

    def test_summary_counts_are_deterministic(self):
        result = run_sandbox_execution_result_feedback_loop_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_feedback_trace_count"])
        self.assertGreaterEqual(summary["invalid_feedback_trace_count"], 20)
        self.assertEqual(1, summary["valid_ephemeral_application_count"])
        self.assertGreaterEqual(summary["invalid_ephemeral_application_count"], 20)
        self.assertEqual(1, summary["valid_reordering_count"])
        self.assertGreaterEqual(summary["invalid_reordering_count"], 20)
        self.assertEqual(1, summary["valid_rollback_count"])
        self.assertGreaterEqual(summary["invalid_rollback_count"], 15)
        self.assertEqual(1, summary["execution_source_checked_count"])
        self.assertEqual(1, summary["feedback_generated_count"])
        self.assertEqual(1, summary["ephemeral_application_checked_count"])
        self.assertEqual(1, summary["same_session_reordering_checked_count"])
        self.assertEqual(1, summary["rollback_checked_count"])
        self.assertEqual(1, summary["persistent_update_blocked_count"])
        self.assertEqual(1, summary["cross_session_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["direct_command_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_sandbox_execution_result_feedback_loop_checks_passed"])

    def assertInvalidFeedbackTrace(self, field, value):
        record = deepcopy(build_sandbox_execution_result_feedback_trace())
        record[field] = value
        self.assertFalse(validate_sandbox_execution_result_feedback_trace(record)["valid"])

    def assertInvalidApplication(self, field, value):
        record = deepcopy(build_sandbox_execution_ephemeral_feedback_application())
        record[field] = value
        self.assertFalse(validate_sandbox_execution_ephemeral_feedback_application(record)["valid"])

    def assertInvalidReordering(self, field, value):
        record = deepcopy(build_sandbox_execution_feedback_reordering_record())
        record[field] = value
        self.assertFalse(validate_sandbox_execution_feedback_reordering_record(record)["valid"])

    def assertInvalidRollback(self, field, value):
        record = deepcopy(build_sandbox_execution_feedback_loop_rollback_record())
        record[field] = value
        self.assertFalse(validate_sandbox_execution_feedback_loop_rollback_record(record)["valid"])


if __name__ == "__main__":
    unittest.main()
