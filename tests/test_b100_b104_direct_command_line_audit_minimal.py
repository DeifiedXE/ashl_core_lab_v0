import unittest
from copy import deepcopy

from ashl_core.b100_b104_direct_command_line_audit_minimal import (
    AUDITED_STEPS,
    BOUNDARY_INDEX,
    build_b100_b104_direct_command_line_audit_record,
    run_b100_b104_direct_command_line_audit_minimal_check,
    validate_b100_b104_direct_command_line_audit_record,
)
from ashl_core.sandbox_direct_command_minimal import DIRECT_COMMAND


class B100B104DirectCommandLineAuditMinimalTests(unittest.TestCase):
    def setUp(self):
        self.audit = build_b100_b104_direct_command_line_audit_record()

    def test_valid_audit(self):
        result = validate_b100_b104_direct_command_line_audit_record(self.audit)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("b100_b104_direct_command_line_audit", self.audit["record_type"])
        self.assertEqual("passed_b100_b104_direct_command_line_audit", self.audit["audit_status"])
        self.assertEqual(BOUNDARY_INDEX, self.audit["boundary_index_before"])
        self.assertEqual(BOUNDARY_INDEX, self.audit["boundary_index_after"])
        self.assertFalse(self.audit["boundary_change_required"])
        self.assertFalse(self.audit["boundary_index_update_required"])
        self.assertEqual(len(AUDITED_STEPS), result["audited_step_count"])
        self.assertEqual(0, result["missing_step_count"])

    def test_all_b100_b104_sources_are_validated(self):
        result = validate_b100_b104_direct_command_line_audit_record(self.audit)
        self.assertTrue(result["source_chain_checked"])
        for field in (
            "source_b100_direct_command_approval_boundary_record",
            "source_b101_sandbox_direct_command_record",
            "source_b102_execution_approval_boundary_record",
            "source_b103_direct_command_execution_record",
            "source_b104_feedback_trace_record",
            "source_b104_ephemeral_application_record",
            "source_b104_reordering_record",
            "source_b104_rollback_record",
        ):
            bad = deepcopy(self.audit)
            bad[field] = {}
            self.assertFalse(validate_b100_b104_direct_command_line_audit_record(bad)["valid"], field)

    def test_direct_command_created_and_executed_once(self):
        result = validate_b100_b104_direct_command_line_audit_record(self.audit)
        self.assertTrue(result["direct_command_created_once_checked"])
        self.assertTrue(result["direct_command_executed_once_checked"])
        self.assertEqual(DIRECT_COMMAND, self.audit["direct_command"])
        self.assertEqual(1, self.audit["execution_count"])
        self.assertEqual(1, self.audit["execution_budget"])
        self.assertTrue(self.audit["direct_command_created_once"])
        self.assertTrue(self.audit["direct_command_executed_once"])

    def test_same_session_feedback_and_rollback_checked(self):
        result = validate_b100_b104_direct_command_line_audit_record(self.audit)
        self.assertTrue(result["same_session_feedback_loop_checked"])
        self.assertTrue(result["rollback_checked"])
        self.assertTrue(self.audit["feedback_trace_generated"])
        self.assertTrue(self.audit["same_session_ephemeral_feedback_applied"])
        self.assertTrue(self.audit["same_session_candidate_reordering_previewed"])
        self.assertTrue(self.audit["rollback_completed"])
        self.assertFalse(self.audit["dirty_state_after_rollback"])

    def test_boundary_unchanged_required(self):
        bad = deepcopy(self.audit)
        bad["boundary_index_after"] = "2026-06-09-b105"
        result = validate_b100_b104_direct_command_line_audit_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("boundary_index_after_not_expected", result["error_codes"])
        self.assertFalse(result["boundary_unchanged_checked"])

    def test_wrong_direct_command_blocks(self):
        bad = deepcopy(self.audit)
        bad["direct_command"] = "sandbox.retry_same_action"
        result = validate_b100_b104_direct_command_line_audit_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("direct_command_not_expected", result["error_codes"])

    def test_execution_count_greater_than_one_blocks(self):
        bad = deepcopy(self.audit)
        bad["execution_count"] = 2
        result = validate_b100_b104_direct_command_line_audit_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("execution_count_not_expected", result["error_codes"])
        self.assertFalse(result["direct_command_executed_once_checked"])

    def test_feedback_not_generated_blocks(self):
        self._assert_true_field_required("feedback_trace_generated")

    def test_same_session_ephemeral_feedback_not_applied_blocks(self):
        self._assert_true_field_required("same_session_ephemeral_feedback_applied")

    def test_same_session_reordering_not_previewed_blocks(self):
        self._assert_true_field_required("same_session_candidate_reordering_previewed")

    def test_rollback_not_completed_blocks(self):
        self._assert_true_field_required("rollback_completed")

    def test_dirty_state_after_rollback_blocks(self):
        self._assert_false_field_blocks("dirty_state_after_rollback")

    def test_persistent_feedback_blocks(self):
        self._assert_false_field_blocks("persistent_feedback_created")
        self._assert_false_field_blocks("cross_session_feedback_persistence")

    def test_production_navigation_ui_blocked(self):
        self._assert_false_field_blocks("production_behavior_changed")
        self._assert_false_field_blocks("real_navigation_changed")
        self._assert_false_field_blocks("ui_behavior_changed")

    def test_memory_retention_predictor_blocked(self):
        for field in (
            "memory_write_performed",
            "retained_jsonl_write_performed",
            "retention_write_performed",
            "predictor_read_enabled",
            "predictor_influence_enabled",
            "predictor_mutation_performed",
        ):
            self._assert_false_field_blocks(field)

    def test_new_action_creation_blocked(self):
        self._assert_false_field_blocks("selected_action_created")
        self._assert_false_field_blocks("final_action_created")
        self._assert_false_field_blocks("new_direct_command_created")

    def test_proof_and_autonomous_claims_blocked(self):
        self._assert_false_field_blocks("proof_of_learning_claim_allowed")
        self._assert_false_field_blocks("autonomous_learning_claim_allowed")
        self._assert_false_field_blocks("autonomous_action_claim_allowed")

    def test_missing_audited_step_blocks(self):
        bad = deepcopy(self.audit)
        bad["audited_steps"] = ["b101_sandbox_direct_command_created"]
        result = validate_b100_b104_direct_command_line_audit_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("audited_steps_missing_required", result["error_codes"])
        self.assertEqual(len(AUDITED_STEPS) - 1, result["missing_step_count"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_b100_b104_direct_command_line_audit_minimal_check()
        summary = result["summary"]
        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_audit_count"])
        self.assertEqual(43, summary["invalid_audit_count"])
        self.assertEqual(len(AUDITED_STEPS), summary["audited_step_count"])
        self.assertEqual(0, summary["missing_step_count"])
        self.assertEqual(1, summary["source_chain_checked_count"])
        self.assertEqual(1, summary["boundary_unchanged_checked_count"])
        self.assertEqual(1, summary["direct_command_created_once_checked_count"])
        self.assertEqual(1, summary["direct_command_executed_once_checked_count"])
        self.assertEqual(1, summary["same_session_feedback_loop_checked_count"])
        self.assertEqual(1, summary["rollback_checked_count"])
        self.assertEqual(1, summary["persistent_feedback_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["real_navigation_blocked_count"])
        self.assertEqual(1, summary["ui_behavior_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["new_action_creation_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_b100_b104_direct_command_line_audit_checks_passed"])

    def _assert_true_field_required(self, field):
        bad = deepcopy(self.audit)
        bad[field] = False
        result = validate_b100_b104_direct_command_line_audit_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn(f"{field}_not_true", result["error_codes"])

    def _assert_false_field_blocks(self, field):
        bad = deepcopy(self.audit)
        bad[field] = True
        result = validate_b100_b104_direct_command_line_audit_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn(f"{field}_not_false", result["error_codes"])


if __name__ == "__main__":
    unittest.main()
