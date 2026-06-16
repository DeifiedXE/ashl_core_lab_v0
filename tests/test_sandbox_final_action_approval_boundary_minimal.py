import unittest
from copy import deepcopy

from ashl_core.sandbox_final_action_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    build_sandbox_final_action_approval_boundary_record,
    run_sandbox_final_action_approval_boundary_minimal_check,
    validate_sandbox_final_action_approval_boundary_record,
)
from ashl_core.teaching_cli import run_command


class SandboxFinalActionApprovalBoundaryMinimalTests(unittest.TestCase):
    def test_valid_final_action_approval_boundary(self):
        record = build_sandbox_final_action_approval_boundary_record()
        result = validate_sandbox_final_action_approval_boundary_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("sandbox_final_action_approval_boundary", record["record_type"])
        self.assertEqual("approved_for_future_sandbox_final_action_package_only", record["approval_status"])

    def test_boundary_index_moves_b97_to_b98(self):
        result = run_sandbox_final_action_approval_boundary_minimal_check()
        boundary = result["boundary"]

        self.assertEqual("2026-06-09-b97", BOUNDARY_INDEX_BEFORE)
        self.assertEqual("2026-06-09-b98", BOUNDARY_INDEX_AFTER)
        self.assertTrue(boundary["boundary_change_required"])
        self.assertTrue(boundary["boundary_index_update_required"])
        self.assertEqual("2026-06-09-b97", boundary["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b98", boundary["boundary_index_version_after"])

    def test_required_sources_are_checked(self):
        record = build_sandbox_final_action_approval_boundary_record()
        result = validate_sandbox_final_action_approval_boundary_record(record)

        self.assertTrue(result["source_selected_action_checked"])
        self.assertTrue(result["source_execution_checked"])
        self.assertTrue(result["source_feedback_loop_checked"])
        self.assertTrue(result["source_audit_checked"])

    def test_future_final_action_is_approved_but_not_created(self):
        record = build_sandbox_final_action_approval_boundary_record()
        result = validate_sandbox_final_action_approval_boundary_record(record)

        self.assertEqual("Sandbox Final Action Minimal v0", record["allowed_next_package"])
        self.assertEqual(
            "convert_sandbox_execution_result_to_sandbox_final_action",
            record["allowed_future_behavior"],
        )
        self.assertFalse(record["implementation_in_this_package"])
        self.assertFalse(record["final_action_created"])
        self.assertTrue(record["final_action_allowed_in_future_package"])
        self.assertTrue(result["future_final_action_approval_checked"])
        self.assertTrue(result["final_action_blocked"])

    def test_forbidden_boundaries_are_false(self):
        record = build_sandbox_final_action_approval_boundary_record()

        for field in (
            "direct_command_created",
            "direct_command_allowed",
            "production_behavior_changed",
            "persistent_rule_created",
            "persistent_trust_doubt_update_performed",
            "cross_session_feedback_persistence",
            "memory_write_performed",
            "retained_jsonl_write_performed",
            "retention_write_performed",
            "predictor_read_enabled",
            "predictor_influence_enabled",
            "predictor_mutation_performed",
            "proof_of_learning_claim_allowed",
            "autonomous_learning_claim_allowed",
            "autonomous_action_claim_allowed",
        ):
            with self.subTest(field=field):
                self.assertFalse(record[field])

    def test_cli_command_returns_ok(self):
        result = run_command("run-sandbox-final-action-approval-boundary-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_approval_count"])

    def test_invalid_missing_b95_selected_action_source_blocks(self):
        self.assertInvalid("required_source_selected_action_record", {})

    def test_invalid_missing_b96_execution_source_blocks(self):
        self.assertInvalid("required_source_execution_record", {})

    def test_invalid_missing_b97_feedback_loop_source_blocks(self):
        self.assertInvalid("required_source_execution_feedback_loop_record", {})

    def test_invalid_missing_b95_b97_audit_blocks(self):
        self.assertInvalid("required_source_boundary_audit_record", {})

    def test_invalid_source_audit_not_passed_blocks(self):
        self.assertInvalid("required_source_audit_passed", False)

    def test_invalid_source_rollback_not_verified_blocks(self):
        self.assertInvalid("required_source_rollback_verified", False)

    def test_invalid_source_not_same_session_blocks(self):
        self.assertInvalid("required_source_same_session_only", False)

    def test_invalid_final_action_created_in_this_package_blocks(self):
        self.assertInvalid("final_action_created", True)
        self.assertInvalid("implementation_in_this_package", True)

    def test_invalid_direct_command_allowed_blocks(self):
        self.assertInvalid("direct_command_allowed", True)
        self.assertInvalid("future_direct_command_requires_separate_boundary", False)

    def test_invalid_direct_command_created_blocks(self):
        self.assertInvalid("direct_command_created", True)

    def test_invalid_production_behavior_blocks(self):
        self.assertInvalid("production_behavior_changed", True)

    def test_invalid_persistent_rule_blocks(self):
        self.assertInvalid("persistent_rule_created", True)

    def test_invalid_persistent_trust_doubt_update_blocks(self):
        self.assertInvalid("persistent_trust_doubt_update_performed", True)

    def test_invalid_cross_session_persistence_blocks(self):
        self.assertInvalid("cross_session_feedback_persistence", True)

    def test_invalid_memory_write_blocks(self):
        self.assertInvalid("memory_write_performed", True)
        self.assertInvalid("retained_jsonl_write_performed", True)

    def test_invalid_retention_write_blocks(self):
        self.assertInvalid("retention_write_performed", True)

    def test_invalid_predictor_read_influence_mutation_blocks(self):
        self.assertInvalid("predictor_read_enabled", True)
        self.assertInvalid("predictor_influence_enabled", True)
        self.assertInvalid("predictor_mutation_performed", True)

    def test_invalid_proof_claim_blocks(self):
        self.assertInvalid("proof_of_learning_claim_allowed", True)

    def test_invalid_autonomous_learning_action_claim_blocks(self):
        self.assertInvalid("autonomous_learning_claim_allowed", True)
        self.assertInvalid("autonomous_action_claim_allowed", True)

    def test_summary_counts_are_deterministic(self):
        result = run_sandbox_final_action_approval_boundary_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_approval_count"])
        self.assertGreaterEqual(summary["invalid_approval_count"], 25)
        self.assertEqual(1, summary["source_selected_action_checked_count"])
        self.assertEqual(1, summary["source_execution_checked_count"])
        self.assertEqual(1, summary["source_feedback_loop_checked_count"])
        self.assertEqual(1, summary["source_audit_checked_count"])
        self.assertEqual(1, summary["future_final_action_approval_checked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["direct_command_blocked_count"])
        self.assertEqual(1, summary["persistent_update_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_sandbox_final_action_approval_boundary_checks_passed"])

    def assertInvalid(self, field, value):
        record = deepcopy(build_sandbox_final_action_approval_boundary_record())
        record[field] = value

        self.assertFalse(validate_sandbox_final_action_approval_boundary_record(record)["valid"])


if __name__ == "__main__":
    unittest.main()
