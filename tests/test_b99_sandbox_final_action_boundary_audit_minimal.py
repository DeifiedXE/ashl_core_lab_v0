import unittest
from copy import deepcopy

from ashl_core.b99_sandbox_final_action_boundary_audit_minimal import (
    BOUNDARY_INDEX,
    build_b99_sandbox_final_action_boundary_audit_record,
    run_b99_sandbox_final_action_boundary_audit_minimal_check,
    validate_b99_sandbox_final_action_boundary_audit_record,
)


class B99SandboxFinalActionBoundaryAuditMinimalTests(unittest.TestCase):
    def setUp(self):
        self.audit = build_b99_sandbox_final_action_boundary_audit_record()

    def test_valid_audit(self):
        result = validate_b99_sandbox_final_action_boundary_audit_record(self.audit)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(BOUNDARY_INDEX, self.audit["boundary_index_before"])
        self.assertEqual(BOUNDARY_INDEX, self.audit["boundary_index_after"])
        self.assertFalse(self.audit["boundary_change_required"])
        self.assertFalse(self.audit["boundary_index_update_required"])
        self.assertEqual(2, result["audited_step_count"])
        self.assertEqual(0, result["missing_step_count"])

    def test_invalid_missing_b99_final_action_source(self):
        audit = deepcopy(self.audit)
        audit["source_sandbox_final_action_record"] = {}
        self.assertIn(
            "missing_or_invalid_b99_final_action_source",
            validate_b99_sandbox_final_action_boundary_audit_record(audit)["error_codes"],
        )

    def test_invalid_missing_b99_test_tier_policy_source(self):
        audit = deepcopy(self.audit)
        audit["source_test_tier_policy_record"] = {}
        self.assertIn(
            "missing_or_invalid_b99_test_tier_policy_source",
            validate_b99_sandbox_final_action_boundary_audit_record(audit)["error_codes"],
        )

    def test_invalid_boundary_index_changed(self):
        audit = deepcopy(self.audit)
        audit["boundary_index_after"] = "2026-06-09-b100"
        self.assertIn(
            "boundary_index_after_not_expected",
            validate_b99_sandbox_final_action_boundary_audit_record(audit)["error_codes"],
        )

    def test_invalid_final_action_outside_sandbox_scope(self):
        audit = deepcopy(self.audit)
        audit["final_action_scope"] = "production"
        self.assertIn(
            "final_action_scope_not_expected",
            validate_b99_sandbox_final_action_boundary_audit_record(audit)["error_codes"],
        )

    def test_invalid_final_action_differs_from_expected(self):
        audit = deepcopy(self.audit)
        audit["final_action"] = "retry_same_action_without_check"
        self.assertIn(
            "final_action_not_expected",
            validate_b99_sandbox_final_action_boundary_audit_record(audit)["error_codes"],
        )

    def test_invalid_direct_command(self):
        self._assert_false_field_blocks("direct_command_created")

    def test_invalid_direct_command_allowed(self):
        self._assert_false_field_blocks("direct_command_allowed")

    def test_invalid_production_behavior(self):
        self._assert_false_field_blocks("production_behavior_changed")

    def test_invalid_persistent_rule(self):
        self._assert_false_field_blocks("persistent_rule_created")

    def test_invalid_persistent_trust_doubt_update(self):
        self._assert_false_field_blocks("persistent_trust_doubt_update_performed")

    def test_invalid_cross_session_persistence(self):
        self._assert_false_field_blocks("cross_session_feedback_persistence")

    def test_invalid_memory_write(self):
        self._assert_false_field_blocks("memory_write_performed")

    def test_invalid_retained_jsonl_write(self):
        self._assert_false_field_blocks("retained_jsonl_write_performed")

    def test_invalid_retention_write(self):
        self._assert_false_field_blocks("retention_write_performed")

    def test_invalid_predictor_read_influence_mutation(self):
        self._assert_false_field_blocks("predictor_read_enabled")
        self._assert_false_field_blocks("predictor_influence_enabled")
        self._assert_false_field_blocks("predictor_mutation_performed")

    def test_invalid_proof_claim(self):
        self._assert_false_field_blocks("proof_of_learning_claim_allowed")

    def test_invalid_autonomous_learning_action_claim(self):
        self._assert_false_field_blocks("autonomous_learning_claim_allowed")
        self._assert_false_field_blocks("autonomous_action_claim_allowed")

    def test_invalid_test_tier_policy_treated_as_runtime_capability(self):
        self._assert_false_field_blocks("test_tier_policy_runtime_capability")

    def test_invalid_test_tier_policy_changes_boundary_by_itself(self):
        self._assert_false_field_blocks("test_tier_policy_boundary_change_required_by_itself")

    def test_invalid_missing_audited_step(self):
        audit = deepcopy(self.audit)
        audit["audited_steps"] = ["sandbox_final_action_b99"]
        result = validate_b99_sandbox_final_action_boundary_audit_record(audit)
        self.assertIn("audited_steps_missing_required", result["error_codes"])
        self.assertEqual(1, result["missing_step_count"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_b99_sandbox_final_action_boundary_audit_minimal_check()
        summary = result["summary"]
        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_audit_count"])
        self.assertEqual(24, summary["invalid_audit_count"])
        self.assertEqual(2, summary["audited_step_count"])
        self.assertEqual(0, summary["missing_step_count"])
        self.assertEqual(1, summary["boundary_unchanged_checked_count"])
        self.assertEqual(1, summary["final_action_checked_count"])
        self.assertEqual(1, summary["sandbox_scope_checked_count"])
        self.assertEqual(1, summary["direct_command_blocked_count"])
        self.assertEqual(1, summary["persistent_update_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["test_policy_workflow_only_checked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_b99_sandbox_final_action_boundary_audit_checks_passed"])

    def _assert_false_field_blocks(self, field):
        audit = deepcopy(self.audit)
        audit[field] = True
        self.assertIn(
            f"{field}_not_false",
            validate_b99_sandbox_final_action_boundary_audit_record(audit)["error_codes"],
        )


if __name__ == "__main__":
    unittest.main()
