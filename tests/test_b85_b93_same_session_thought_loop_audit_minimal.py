import unittest
from copy import deepcopy

from ashl_core.b85_b93_same_session_thought_loop_audit_minimal import (
    AUDITED_STEPS,
    BOUNDARY_INDEX_VERSION,
    build_b85_b93_thought_loop_audit_record,
    run_b85_b93_same_session_thought_loop_audit_minimal_check,
    validate_b85_b93_thought_loop_audit_record,
)
from ashl_core.teaching_cli import run_command


class B85B93SameSessionThoughtLoopAuditMinimalTests(unittest.TestCase):
    def test_valid_audit_record_is_created(self):
        record = build_b85_b93_thought_loop_audit_record()
        result = validate_b85_b93_thought_loop_audit_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("b85_b93_same_session_thought_loop_audit", record["record_type"])
        self.assertEqual("passed_same_session_thought_loop_boundary_audit", record["audit_status"])

    def test_boundary_index_remains_unchanged(self):
        record = build_b85_b93_thought_loop_audit_record()

        self.assertEqual("2026-06-09-b93", BOUNDARY_INDEX_VERSION)
        self.assertEqual("2026-06-09-b93", record["boundary_index_before"])
        self.assertEqual("2026-06-09-b93", record["boundary_index_after"])
        self.assertFalse(record["boundary_change_required"])
        self.assertFalse(record["boundary_index_update_required"])

    def test_all_b85_b93_steps_are_audited(self):
        record = build_b85_b93_thought_loop_audit_record()
        result = validate_b85_b93_thought_loop_audit_record(record)

        self.assertEqual(AUDITED_STEPS, record["audited_steps"])
        self.assertEqual(9, result["audited_step_count"])
        self.assertEqual(0, result["missing_step_count"])

    def test_same_session_and_rollback_are_checked(self):
        record = build_b85_b93_thought_loop_audit_record()
        result = validate_b85_b93_thought_loop_audit_record(record)

        self.assertTrue(record["same_session_only"])
        self.assertTrue(record["rollback_required"])
        self.assertTrue(record["rollback_verified"])
        self.assertFalse(record["dirty_state_after_rollback"])
        self.assertTrue(result["rollback_checked"])

    def test_allowed_same_session_components_are_true(self):
        record = build_b85_b93_thought_loop_audit_record()

        for field in (
            "candidate_ordering_allowed",
            "doubt_trace_allowed",
            "verification_candidate_registry_allowed",
            "verification_planning_allowed",
            "sandbox_verification_execution_allowed",
            "trace_only_feedback_allowed",
            "ephemeral_feedback_application_allowed",
            "same_session_reordering_allowed",
            "audit_recorded",
        ):
            with self.subTest(field=field):
                self.assertTrue(record[field])

    def test_forbidden_boundaries_are_false(self):
        record = build_b85_b93_thought_loop_audit_record()

        for field in (
            "selected_action_created",
            "final_action_created",
            "direct_command_created",
            "persistent_rule_created",
            "persistent_trust_doubt_update_performed",
            "cross_session_feedback_persistence",
            "memory_write_performed",
            "retained_jsonl_write_performed",
            "retention_write_performed",
            "predictor_read_enabled",
            "predictor_influence_enabled",
            "predictor_mutation_performed",
            "production_behavior_changed",
            "proof_of_learning_claim_allowed",
            "autonomous_learning_claim_allowed",
            "autonomous_action_claim_allowed",
        ):
            with self.subTest(field=field):
                self.assertFalse(record[field])

    def test_cli_command_returns_ok(self):
        result = run_command("run-b85-b93-same-session-thought-loop-audit-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_audit_count"])

    def test_invalid_missing_audited_step_blocks(self):
        record = deepcopy(build_b85_b93_thought_loop_audit_record())
        record["audited_steps"] = record["audited_steps"][:-1]

        self.assertFalse(validate_b85_b93_thought_loop_audit_record(record)["valid"])

    def test_invalid_boundary_change_blocks(self):
        self.assertInvalid("boundary_index_after", "2026-06-09-b94")
        self.assertInvalid("boundary_change_required", True)
        self.assertInvalid("boundary_index_update_required", True)

    def test_invalid_selected_final_direct_blocks(self):
        self.assertInvalid("selected_action_created", True)
        self.assertInvalid("final_action_created", True)
        self.assertInvalid("direct_command_created", True)

    def test_invalid_persistent_and_cross_session_blocks(self):
        self.assertInvalid("persistent_rule_created", True)
        self.assertInvalid("persistent_trust_doubt_update_performed", True)
        self.assertInvalid("cross_session_feedback_persistence", True)

    def test_invalid_memory_retention_blocks(self):
        self.assertInvalid("memory_write_performed", True)
        self.assertInvalid("retained_jsonl_write_performed", True)
        self.assertInvalid("retention_write_performed", True)

    def test_invalid_predictor_blocks(self):
        self.assertInvalid("predictor_read_enabled", True)
        self.assertInvalid("predictor_influence_enabled", True)
        self.assertInvalid("predictor_mutation_performed", True)

    def test_invalid_production_proof_autonomous_blocks(self):
        self.assertInvalid("production_behavior_changed", True)
        self.assertInvalid("proof_of_learning_claim_allowed", True)
        self.assertInvalid("autonomous_learning_claim_allowed", True)
        self.assertInvalid("autonomous_action_claim_allowed", True)

    def test_invalid_rollback_blocks(self):
        self.assertInvalid("rollback_required", False)
        self.assertInvalid("rollback_verified", False)
        self.assertInvalid("dirty_state_after_rollback", True)

    def test_summary_counts_are_deterministic(self):
        result = run_b85_b93_same_session_thought_loop_audit_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_audit_count"])
        self.assertGreaterEqual(summary["invalid_audit_count"], 20)
        self.assertEqual(9, summary["audited_step_count"])
        self.assertEqual(0, summary["missing_step_count"])
        self.assertEqual(1, summary["boundary_unchanged_checked_count"])
        self.assertEqual(1, summary["rollback_checked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["persistent_update_blocked_count"])
        self.assertEqual(1, summary["cross_session_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_b85_b93_same_session_thought_loop_audit_checks_passed"])

    def assertInvalid(self, field, value):
        record = deepcopy(build_b85_b93_thought_loop_audit_record())
        record[field] = value

        self.assertFalse(validate_b85_b93_thought_loop_audit_record(record)["valid"])


if __name__ == "__main__":
    unittest.main()
