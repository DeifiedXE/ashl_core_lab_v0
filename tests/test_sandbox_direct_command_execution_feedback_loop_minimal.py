import unittest
from copy import deepcopy

from ashl_core.sandbox_direct_command_execution_feedback_loop_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    CANDIDATE_ORDER,
    DIRECT_COMMAND,
    build_sandbox_direct_command_execution_ephemeral_feedback_application,
    build_sandbox_direct_command_execution_feedback_loop_rollback_record,
    build_sandbox_direct_command_execution_feedback_reordering_record,
    build_sandbox_direct_command_execution_feedback_trace,
    run_sandbox_direct_command_execution_feedback_loop_minimal_check,
    validate_sandbox_direct_command_execution_ephemeral_feedback_application,
    validate_sandbox_direct_command_execution_feedback_loop_rollback_record,
    validate_sandbox_direct_command_execution_feedback_reordering_record,
    validate_sandbox_direct_command_execution_feedback_trace,
)
from ashl_core.teaching_cli import run_command


class SandboxDirectCommandExecutionFeedbackLoopMinimalTests(unittest.TestCase):
    def test_valid_feedback_trace(self):
        record = build_sandbox_direct_command_execution_feedback_trace()
        result = validate_sandbox_direct_command_execution_feedback_trace(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("2026-06-09-b103", BOUNDARY_INDEX_BEFORE)
        self.assertEqual("2026-06-09-b104", BOUNDARY_INDEX_AFTER)
        self.assertEqual("sandbox_direct_command_execution_result_feedback_trace", record["record_type"])
        self.assertEqual("sandbox_direct_command_execution_b103", record["source_direct_command_execution"])
        self.assertEqual(DIRECT_COMMAND, record["direct_command"])
        self.assertTrue(record["source_direct_command_executed"])
        self.assertEqual("local_context_observed", record["execution_result"])
        self.assertEqual("trace_only_feedback_generated", record["feedback_status"])
        self.assertTrue(result["execution_source_checked"])
        self.assertTrue(result["feedback_generated"])

    def test_valid_ephemeral_application(self):
        record = build_sandbox_direct_command_execution_ephemeral_feedback_application()
        result = validate_sandbox_direct_command_execution_ephemeral_feedback_application(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("same_sandbox_session_only", record["application_scope"])
        self.assertLess(record["doubt_after_ephemeral"], record["doubt_before"])
        self.assertGreater(
            record["direct_command_confidence_after_ephemeral"],
            record["direct_command_confidence_before"],
        )
        self.assertLessEqual(record["direct_retry_weight_after_ephemeral"], record["direct_retry_weight_before"])
        self.assertTrue(record["ephemeral_update_applied"])

    def test_valid_same_session_reordering(self):
        record = build_sandbox_direct_command_execution_feedback_reordering_record()
        result = validate_sandbox_direct_command_execution_feedback_reordering_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(CANDIDATE_ORDER, record["candidate_actions_after_reordering"])
        self.assertTrue(record["observe_or_alternative_probe_remains_ranked_first"])
        self.assertTrue(record["check_before_retry_ranked_before_direct_retry"])
        self.assertTrue(record["direct_retry_ranked_last"])
        self.assertTrue(record["same_session_only"])

    def test_valid_rollback(self):
        record = build_sandbox_direct_command_execution_feedback_loop_rollback_record()
        result = validate_sandbox_direct_command_execution_feedback_loop_rollback_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("sandbox_direct_command_execution_feedback_loop_rolled_back", record["rollback_status"])
        self.assertTrue(record["session_end_triggered"])
        self.assertEqual(CANDIDATE_ORDER, record["candidate_ordering_restored"])
        self.assertFalse(record["dirty_state_after_rollback"])

    def test_cli_command_returns_ok(self):
        result = run_command("run-sandbox-direct-command-execution-feedback-loop-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_feedback_trace_count"])

    def test_invalid_missing_b103_execution_source(self):
        self.assertInvalidFeedbackTrace("source_direct_command_execution_record", {})

    def test_invalid_feedback_not_trace_only(self):
        self.assertInvalidFeedbackTrace("feedback_status", "applied")
        self.assertInvalidFeedbackTrace("feedback_applied_persistently", True)
        record = build_sandbox_direct_command_execution_feedback_trace()
        record["doubt_feedback"]["applied_persistently"] = True
        self.assertFalse(validate_sandbox_direct_command_execution_feedback_trace(record)["valid"])

    def test_invalid_ephemeral_application_values(self):
        self.assertInvalidApplication("application_scope", "cross_session")
        self.assertInvalidApplication("doubt_after_ephemeral", 0.57)
        self.assertInvalidApplication("direct_command_confidence_after_ephemeral", 0.49)
        self.assertInvalidApplication("direct_retry_weight_after_ephemeral", 0.40)
        self.assertInvalidApplication("ephemeral_update_applied", False)

    def test_invalid_reordering_values(self):
        self.assertInvalidReordering("candidate_actions_after_reordering", list(reversed(CANDIDATE_ORDER)))
        self.assertInvalidReordering("observe_or_alternative_probe_remains_ranked_first", False)
        self.assertInvalidReordering("check_before_retry_ranked_before_direct_retry", False)
        self.assertInvalidReordering("direct_retry_ranked_last", False)
        self.assertInvalidReordering("same_session_only", False)

    def test_invalid_rollback_values(self):
        self.assertInvalidRollback("session_end_triggered", False)
        self.assertInvalidRollback("dirty_state_after_rollback", True)
        self.assertInvalidRollback("candidate_ordering_restored", [])

    def test_forbidden_boundaries_block_across_records(self):
        fields = (
            "persistent_update_performed",
            "cross_session_available",
            "memory_write_performed",
            "retained_jsonl_write_performed",
            "retention_write_performed",
            "predictor_read_enabled",
            "predictor_influence_enabled",
            "predictor_mutation_performed",
            "production_behavior_changed",
            "real_navigation_changed",
            "ui_behavior_changed",
            "selected_action_created",
            "final_action_created",
            "new_direct_command_created",
            "proof_of_learning_claim_allowed",
            "autonomous_learning_claim_allowed",
            "autonomous_action_claim_allowed",
        )
        for field in fields:
            with self.subTest(field=field):
                self.assertInvalidFeedbackTrace(field, True)
                self.assertInvalidApplication(field, True)
                self.assertInvalidReordering(field, True)
                self.assertInvalidRollback(field, True)

    def test_summary_counts_are_deterministic(self):
        result = run_sandbox_direct_command_execution_feedback_loop_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_feedback_trace_count"])
        self.assertGreaterEqual(summary["invalid_feedback_trace_count"], 25)
        self.assertEqual(1, summary["valid_ephemeral_application_count"])
        self.assertGreaterEqual(summary["invalid_ephemeral_application_count"], 20)
        self.assertEqual(1, summary["valid_reordering_count"])
        self.assertGreaterEqual(summary["invalid_reordering_count"], 20)
        self.assertEqual(1, summary["valid_rollback_count"])
        self.assertGreaterEqual(summary["invalid_rollback_count"], 20)
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
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["real_navigation_blocked_count"])
        self.assertEqual(1, summary["ui_behavior_blocked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["new_direct_command_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_sandbox_direct_command_execution_feedback_loop_checks_passed"])

    def assertInvalidFeedbackTrace(self, field, value):
        record = deepcopy(build_sandbox_direct_command_execution_feedback_trace())
        record[field] = value
        self.assertFalse(validate_sandbox_direct_command_execution_feedback_trace(record)["valid"])

    def assertInvalidApplication(self, field, value):
        record = deepcopy(build_sandbox_direct_command_execution_ephemeral_feedback_application())
        record[field] = value
        self.assertFalse(validate_sandbox_direct_command_execution_ephemeral_feedback_application(record)["valid"])

    def assertInvalidReordering(self, field, value):
        record = deepcopy(build_sandbox_direct_command_execution_feedback_reordering_record())
        record[field] = value
        self.assertFalse(validate_sandbox_direct_command_execution_feedback_reordering_record(record)["valid"])

    def assertInvalidRollback(self, field, value):
        record = deepcopy(build_sandbox_direct_command_execution_feedback_loop_rollback_record())
        record[field] = value
        self.assertFalse(validate_sandbox_direct_command_execution_feedback_loop_rollback_record(record)["valid"])


if __name__ == "__main__":
    unittest.main()
