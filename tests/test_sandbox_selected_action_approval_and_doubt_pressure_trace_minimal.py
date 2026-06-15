import unittest
from copy import deepcopy

from ashl_core.sandbox_selected_action_approval_and_doubt_pressure_trace_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    build_combined_boundary_summary,
    build_cortisol_like_doubt_pressure_trace,
    build_sandbox_selected_action_approval_record,
    run_sandbox_selected_action_approval_and_doubt_pressure_trace_minimal_check,
    validate_combined_boundary_summary,
    validate_cortisol_like_doubt_pressure_trace,
    validate_sandbox_selected_action_approval_record,
)
from ashl_core.teaching_cli import run_command


class SandboxSelectedActionApprovalAndDoubtPressureTraceMinimalTests(unittest.TestCase):
    def test_valid_selected_action_approval_boundary(self):
        record = build_sandbox_selected_action_approval_record()
        result = validate_sandbox_selected_action_approval_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("approved_for_future_sandbox_selected_action_package_only", record["approval_status"])
        self.assertTrue(record["selected_action_allowed_in_future_package"])
        self.assertFalse(record["implementation_in_this_package"])
        self.assertFalse(record["selected_action_created"])

    def test_valid_cortisol_like_pressure_trace(self):
        record = build_cortisol_like_doubt_pressure_trace()
        result = validate_cortisol_like_doubt_pressure_trace(record)

        self.assertTrue(result["valid"])
        self.assertGreater(record["pressure_after"], record["pressure_before"])
        self.assertGreaterEqual(record["doubt_weight_after_pressure_preview"], record["doubt_weight_before"])
        self.assertGreaterEqual(
            record["strategy_shift_weight_after_pressure_preview"],
            record["strategy_shift_weight_before"],
        )
        self.assertLessEqual(record["direct_retry_weight_after_pressure_preview"], record["direct_retry_weight_before"])

    def test_valid_combined_boundary_summary(self):
        record = build_combined_boundary_summary()
        result = validate_combined_boundary_summary(record)

        self.assertTrue(result["valid"])
        self.assertEqual("2026-06-09-b93", BOUNDARY_INDEX_BEFORE)
        self.assertEqual("2026-06-09-b94", BOUNDARY_INDEX_AFTER)
        self.assertTrue(record["boundary_change_required"])
        self.assertTrue(record["boundary_index_update_required"])
        self.assertFalse(record["selected_action_created"])

    def test_cli_command_returns_ok(self):
        result = run_command("run-sandbox-selected-action-approval-and-doubt-pressure-trace-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_selected_action_approval_count"])

    def test_invalid_missing_b85_b93_audited_source(self):
        self.assertInvalidApproval("required_source_loop_audited", False)

    def test_invalid_source_loop_not_rollback_verified(self):
        self.assertInvalidApproval("required_source_loop_rollback_verified", False)

    def test_invalid_selected_action_created(self):
        self.assertInvalidApproval("selected_action_created", True)
        self.assertInvalidPressure("selected_action_created", True)
        self.assertInvalidSummary("selected_action_created", True)

    def test_invalid_final_action_allowed(self):
        self.assertInvalidApproval("final_action_allowed", True)
        self.assertInvalidApproval("final_action_created", True)
        self.assertInvalidPressure("final_action_created", True)
        self.assertInvalidSummary("final_action_created", True)

    def test_invalid_direct_command(self):
        self.assertInvalidApproval("direct_command_created", True)
        self.assertInvalidPressure("direct_command_created", True)
        self.assertInvalidSummary("direct_command_created", True)

    def test_invalid_pressure_applied_to_runtime(self):
        self.assertInvalidPressure("pressure_effect_applied_to_runtime", True)
        self.assertInvalidSummary("pressure_runtime_effect_applied", True)

    def test_invalid_pressure_persisted(self):
        self.assertInvalidPressure("pressure_effect_persisted", True)
        self.assertInvalidSummary("pressure_persisted", True)

    def test_invalid_pressure_causes_never_try_state(self):
        self.assertInvalidPressure("never_try_state_allowed", True)

    def test_invalid_pressure_causes_permanent_action_ban(self):
        self.assertInvalidPressure("permanent_action_ban_allowed", True)

    def test_invalid_missing_paranoia_guard(self):
        self.assertInvalidPressure("paranoia_guard_enabled", False)
        self.assertInvalidPressure("paranoia_guard_status", "missing")
        self.assertInvalidSummary("paranoia_guard_passed", False)

    def test_invalid_low_risk_action_not_allowed(self):
        self.assertInvalidPressure("low_risk_action_still_allowed", False)

    def test_invalid_missing_verification_budget(self):
        self.assertInvalidPressure("verification_budget_required", False)

    def test_invalid_missing_stop_condition(self):
        self.assertInvalidPressure("stop_condition_required", False)

    def test_invalid_persistent_rule(self):
        self.assertInvalidApproval("persistent_rule_created", True)
        self.assertInvalidPressure("persistent_rule_created", True)
        self.assertInvalidSummary("persistent_rule_created", True)

    def test_invalid_persistent_trust_doubt_update(self):
        self.assertInvalidApproval("persistent_trust_doubt_update_performed", True)
        self.assertInvalidPressure("persistent_trust_doubt_update_performed", True)

    def test_invalid_cross_session_persistence(self):
        self.assertInvalidApproval("cross_session_feedback_persistence", True)
        self.assertInvalidPressure("cross_session_feedback_persistence", True)

    def test_invalid_memory_write(self):
        self.assertInvalidApproval("memory_write_performed", True)
        self.assertInvalidPressure("memory_write_performed", True)
        self.assertInvalidSummary("memory_write_performed", True)

    def test_invalid_retention_write(self):
        self.assertInvalidApproval("retention_write_performed", True)
        self.assertInvalidPressure("retention_write_performed", True)
        self.assertInvalidSummary("retention_write_performed", True)

    def test_invalid_predictor_read_influence_mutation(self):
        self.assertInvalidApproval("predictor_read_enabled", True)
        self.assertInvalidApproval("predictor_influence_enabled", True)
        self.assertInvalidApproval("predictor_mutation_performed", True)
        self.assertInvalidPressure("predictor_read_enabled", True)
        self.assertInvalidPressure("predictor_influence_enabled", True)
        self.assertInvalidPressure("predictor_mutation_performed", True)
        self.assertInvalidSummary("predictor_mutation_performed", True)

    def test_invalid_production_behavior(self):
        self.assertInvalidApproval("production_behavior_changed", True)
        self.assertInvalidPressure("production_behavior_changed", True)
        self.assertInvalidSummary("production_behavior_changed", True)

    def test_invalid_proof_claim(self):
        self.assertInvalidApproval("proof_of_learning_claim_allowed", True)
        self.assertInvalidPressure("proof_of_learning_claim_allowed", True)
        self.assertInvalidSummary("proof_of_learning_claim_allowed", True)

    def test_invalid_autonomous_learning_action_claim(self):
        self.assertInvalidApproval("autonomous_learning_claim_allowed", True)
        self.assertInvalidApproval("autonomous_action_claim_allowed", True)
        self.assertInvalidPressure("autonomous_learning_claim_allowed", True)
        self.assertInvalidPressure("autonomous_action_claim_allowed", True)
        self.assertInvalidSummary("autonomous_learning_claim_allowed", True)
        self.assertInvalidSummary("autonomous_action_claim_allowed", True)

    def test_invalid_future_final_action_without_separate_boundary(self):
        self.assertInvalidApproval("future_final_action_requires_separate_boundary", False)

    def test_summary_counts_are_deterministic(self):
        result = run_sandbox_selected_action_approval_and_doubt_pressure_trace_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_selected_action_approval_count"])
        self.assertGreaterEqual(summary["invalid_selected_action_approval_count"], 20)
        self.assertEqual(1, summary["valid_pressure_trace_count"])
        self.assertGreaterEqual(summary["invalid_pressure_trace_count"], 30)
        self.assertEqual(1, summary["valid_combined_summary_count"])
        self.assertGreaterEqual(summary["invalid_combined_summary_count"], 20)
        self.assertEqual(1, summary["source_loop_checked_count"])
        self.assertEqual(1, summary["rollback_checked_count"])
        self.assertEqual(1, summary["paranoia_guard_checked_count"])
        self.assertEqual(1, summary["low_risk_action_allowed_checked_count"])
        self.assertEqual(1, summary["future_selected_action_approval_checked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["pressure_runtime_application_blocked_count"])
        self.assertEqual(1, summary["pressure_persistence_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_sandbox_selected_action_approval_and_doubt_pressure_trace_checks_passed"])

    def assertInvalidApproval(self, field, value):
        record = deepcopy(build_sandbox_selected_action_approval_record())
        record[field] = value
        self.assertFalse(validate_sandbox_selected_action_approval_record(record)["valid"])

    def assertInvalidPressure(self, field, value):
        record = deepcopy(build_cortisol_like_doubt_pressure_trace())
        record[field] = value
        self.assertFalse(validate_cortisol_like_doubt_pressure_trace(record)["valid"])

    def assertInvalidSummary(self, field, value):
        record = deepcopy(build_combined_boundary_summary())
        record[field] = value
        self.assertFalse(validate_combined_boundary_summary(record)["valid"])


if __name__ == "__main__":
    unittest.main()
