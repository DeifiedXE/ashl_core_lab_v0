import unittest
from copy import deepcopy

from ashl_core.b95_b97_sandbox_action_boundary_audit_minimal import (
    AUDITED_STEPS,
    BOUNDARY_INDEX_VERSION,
    build_b95_b97_sandbox_action_boundary_audit_record,
    run_b95_b97_sandbox_action_boundary_audit_minimal_check,
    validate_b95_b97_sandbox_action_boundary_audit_record,
)
from ashl_core.teaching_cli import run_command


class B95B97SandboxActionBoundaryAuditMinimalTests(unittest.TestCase):
    def test_valid_audit_record_is_created(self):
        record = build_b95_b97_sandbox_action_boundary_audit_record()
        result = validate_b95_b97_sandbox_action_boundary_audit_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("b95_b97_sandbox_action_boundary_audit", record["record_type"])
        self.assertEqual("passed_sandbox_action_boundary_audit", record["audit_status"])

    def test_boundary_index_remains_unchanged(self):
        record = build_b95_b97_sandbox_action_boundary_audit_record()

        self.assertEqual("2026-06-09-b97", BOUNDARY_INDEX_VERSION)
        self.assertEqual("2026-06-09-b97", record["boundary_index_before"])
        self.assertEqual("2026-06-09-b97", record["boundary_index_after"])
        self.assertFalse(record["boundary_change_required"])
        self.assertFalse(record["boundary_index_update_required"])

    def test_all_b95_b97_steps_are_audited(self):
        record = build_b95_b97_sandbox_action_boundary_audit_record()
        result = validate_b95_b97_sandbox_action_boundary_audit_record(record)

        self.assertEqual(AUDITED_STEPS, record["audited_steps"])
        self.assertEqual(3, result["audited_step_count"])
        self.assertEqual(0, result["missing_step_count"])

    def test_selected_action_execution_feedback_and_rollback_are_checked(self):
        record = build_b95_b97_sandbox_action_boundary_audit_record()
        result = validate_b95_b97_sandbox_action_boundary_audit_record(record)

        self.assertTrue(record["selected_action_created"])
        self.assertEqual("observe_or_alternative_probe", record["selected_action"])
        self.assertTrue(record["action_executed"])
        self.assertEqual(1, record["execution_count"])
        self.assertEqual("local_context_observed", record["execution_result"])
        self.assertTrue(record["same_session_feedback_loop_present"])
        self.assertTrue(record["same_session_only"])
        self.assertTrue(record["rollback_required"])
        self.assertTrue(record["rollback_verified"])
        self.assertFalse(record["dirty_state_after_rollback"])
        self.assertTrue(result["selected_action_checked"])
        self.assertTrue(result["execution_checked"])
        self.assertTrue(result["feedback_loop_checked"])
        self.assertTrue(result["rollback_checked"])

    def test_forbidden_boundaries_are_false(self):
        record = build_b95_b97_sandbox_action_boundary_audit_record()

        for field in (
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
        result = run_command("run-b95-b97-sandbox-action-boundary-audit-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_audit_count"])

    def test_invalid_missing_b95_source_blocks(self):
        record = deepcopy(build_b95_b97_sandbox_action_boundary_audit_record())
        record["audited_steps"] = [
            "sandbox_action_execution_b96",
            "sandbox_execution_result_feedback_loop_b97",
        ]

        self.assertInvalidRecord(record)

    def test_invalid_missing_b96_source_blocks(self):
        record = deepcopy(build_b95_b97_sandbox_action_boundary_audit_record())
        record["audited_steps"] = [
            "sandbox_selected_action_and_execution_approval_b95",
            "sandbox_execution_result_feedback_loop_b97",
        ]

        self.assertInvalidRecord(record)

    def test_invalid_missing_b97_source_blocks(self):
        record = deepcopy(build_b95_b97_sandbox_action_boundary_audit_record())
        record["audited_steps"] = [
            "sandbox_selected_action_and_execution_approval_b95",
            "sandbox_action_execution_b96",
        ]

        self.assertInvalidRecord(record)

    def test_invalid_source_records_block(self):
        self.assertInvalid("source_b95_selected_action_record", {})
        self.assertInvalid("source_b96_action_execution_record", {})
        self.assertInvalid("source_b97_feedback_reordering_record", {})
        self.assertInvalid("source_b97_rollback_record", {})

    def test_invalid_boundary_index_changed_blocks(self):
        self.assertInvalid("boundary_index_after", "2026-06-09-b98")
        self.assertInvalid("boundary_change_required", True)
        self.assertInvalid("boundary_index_update_required", True)

    def test_invalid_selected_action_missing_blocks(self):
        self.assertInvalid("selected_action_created", False)
        self.assertInvalid("selected_action", "")

    def test_invalid_execution_count_greater_than_one_blocks(self):
        self.assertInvalid("execution_count", 2)

    def test_invalid_execution_outside_sandbox_scope_blocks(self):
        self.assertInvalid("sandbox_scope", "production")

    def test_invalid_final_action_blocks(self):
        self.assertInvalid("final_action_created", True)

    def test_invalid_direct_command_blocks(self):
        self.assertInvalid("direct_command_created", True)

    def test_invalid_production_behavior_blocks(self):
        self.assertInvalid("production_behavior_changed", True)

    def test_invalid_persistent_rule_blocks(self):
        self.assertInvalid("persistent_rule_created", True)

    def test_invalid_persistent_trust_doubt_update_blocks(self):
        self.assertInvalid("persistent_trust_doubt_update_performed", True)

    def test_invalid_cross_session_feedback_persistence_blocks(self):
        self.assertInvalid("cross_session_feedback_persistence", True)

    def test_invalid_memory_write_blocks(self):
        self.assertInvalid("memory_write_performed", True)

    def test_invalid_retained_jsonl_write_blocks(self):
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

    def test_invalid_rollback_missing_blocks(self):
        self.assertInvalid("rollback_required", False)
        self.assertInvalid("rollback_verified", False)

    def test_invalid_dirty_rollback_blocks(self):
        self.assertInvalid("dirty_state_after_rollback", True)

    def test_summary_counts_are_deterministic(self):
        result = run_b95_b97_sandbox_action_boundary_audit_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_audit_count"])
        self.assertGreaterEqual(summary["invalid_audit_count"], 30)
        self.assertEqual(3, summary["audited_step_count"])
        self.assertEqual(0, summary["missing_step_count"])
        self.assertEqual(1, summary["boundary_unchanged_checked_count"])
        self.assertEqual(1, summary["selected_action_checked_count"])
        self.assertEqual(1, summary["execution_checked_count"])
        self.assertEqual(1, summary["feedback_loop_checked_count"])
        self.assertEqual(1, summary["rollback_checked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["direct_command_blocked_count"])
        self.assertEqual(1, summary["persistent_update_blocked_count"])
        self.assertEqual(1, summary["cross_session_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_b95_b97_sandbox_action_boundary_audit_checks_passed"])

    def assertInvalid(self, field, value):
        record = deepcopy(build_b95_b97_sandbox_action_boundary_audit_record())
        record[field] = value

        self.assertInvalidRecord(record)

    def assertInvalidRecord(self, record):
        self.assertFalse(validate_b95_b97_sandbox_action_boundary_audit_record(record)["valid"])


if __name__ == "__main__":
    unittest.main()
