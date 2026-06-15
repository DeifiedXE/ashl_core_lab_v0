import unittest
from copy import deepcopy

from ashl_core.ephemeral_feedback_application_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_ephemeral_feedback_application_record,
    build_ephemeral_feedback_rollback_record,
    run_ephemeral_feedback_application_minimal_check,
    validate_ephemeral_feedback_application_record,
    validate_ephemeral_feedback_rollback_record,
)
from ashl_core.teaching_cli import run_command


class EphemeralFeedbackApplicationMinimalTests(unittest.TestCase):
    def test_valid_ephemeral_application(self):
        record = build_ephemeral_feedback_application_record()
        result = validate_ephemeral_feedback_application_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("ephemeral_feedback_application", record["record_type"])
        self.assertEqual("applied_same_session_ephemeral_feedback", record["application_status"])
        self.assertEqual("same_sandbox_session_only", record["application_scope"])
        self.assertTrue(record["ephemeral_update_applied"])

    def test_valid_application_requires_b91_feedback_source(self):
        record = build_ephemeral_feedback_application_record()

        self.assertEqual("verification_result_feedback_trace_b91", record["source_feedback_trace"])
        self.assertTrue(validate_ephemeral_feedback_application_record(record)["feedback_source_checked"])
        self.assertEqual("2026-06-09-b91", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b92", BOUNDARY_INDEX_VERSION_AFTER)

    def test_ephemeral_scores_match_feedback_trace(self):
        record = build_ephemeral_feedback_application_record()

        self.assertEqual(0.71, record["doubt_before"])
        self.assertEqual(0.61, record["doubt_after_ephemeral"])
        self.assertEqual(0.50, record["verification_candidate_trust_before"])
        self.assertEqual(0.55, record["verification_candidate_trust_after_ephemeral"])
        self.assertEqual(0.50, record["direct_retry_weight_before"])
        self.assertEqual(0.35, record["direct_retry_weight_after_ephemeral"])
        self.assertEqual(record["hypothesis_trust_before"], record["hypothesis_trust_after_ephemeral"])

    def test_valid_rollback(self):
        application = build_ephemeral_feedback_application_record()
        rollback = build_ephemeral_feedback_rollback_record(application)
        result = validate_ephemeral_feedback_rollback_record(rollback)

        self.assertTrue(result["valid"])
        self.assertEqual("ephemeral_feedback_rollback", rollback["record_type"])
        self.assertEqual("ephemeral_feedback_rolled_back", rollback["rollback_status"])
        self.assertTrue(rollback["session_end_triggered"])
        self.assertFalse(rollback["dirty_state_after_rollback"])
        self.assertEqual(application["doubt_before"], rollback["doubt_restored"])
        self.assertEqual(application["verification_candidate_trust_before"], rollback["verification_candidate_trust_restored"])
        self.assertEqual(application["direct_retry_weight_before"], rollback["direct_retry_weight_restored"])
        self.assertEqual(application["hypothesis_trust_before"], rollback["hypothesis_trust_restored"])

    def test_boundaries_remain_blocked_in_application(self):
        record = build_ephemeral_feedback_application_record()

        for field in (
            "persistent_update_performed",
            "cross_session_available",
            "selected_action_created",
            "final_action_created",
            "direct_command_created",
            "persistent_rule_created",
            "memory_write_performed",
            "retained_jsonl_write_performed",
            "retention_write_performed",
            "predictor_mutation_performed",
            "production_behavior_changed",
            "proof_of_learning_claim_allowed",
            "llm_used",
            "autonomous_learning_claim_allowed",
            "autonomous_action_claim_allowed",
        ):
            with self.subTest(field=field):
                self.assertFalse(record[field])

    def test_boundaries_remain_blocked_in_rollback(self):
        rollback = build_ephemeral_feedback_rollback_record()

        for field in (
            "persistent_update_performed",
            "selected_action_created",
            "final_action_created",
            "direct_command_created",
            "persistent_rule_created",
            "memory_write_performed",
            "retained_jsonl_write_performed",
            "retention_write_performed",
            "predictor_mutation_performed",
            "production_behavior_changed",
            "proof_of_learning_claim_allowed",
            "llm_used",
            "autonomous_learning_claim_allowed",
            "autonomous_action_claim_allowed",
        ):
            with self.subTest(field=field):
                self.assertFalse(rollback[field])

    def test_cli_command_returns_ok(self):
        result = run_command("run-ephemeral-feedback-application-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_application_count"])
        self.assertEqual(1, result["summary"]["valid_rollback_count"])

    def test_invalid_missing_feedback_source(self):
        self.assertInvalidApplication("source_feedback_trace_record", {})

    def test_invalid_cross_session_availability(self):
        self.assertInvalidApplication("cross_session_available", True)
        self.assertInvalidApplication("application_scope", "cross_session")

    def test_invalid_persistent_update(self):
        self.assertInvalidApplication("persistent_update_performed", True)
        self.assertInvalidRollback("persistent_update_performed", True)

    def test_invalid_hypothesis_trust_increase(self):
        self.assertInvalidApplication("hypothesis_trust_after_ephemeral", 0.63)

    def test_invalid_rollback_missing(self):
        self.assertInvalidApplication("rollback_required", False)
        self.assertInvalidApplication("rollback_available", False)
        self.assertInvalidRollback("session_end_triggered", False)

    def test_invalid_dirty_rollback(self):
        self.assertInvalidRollback("dirty_state_after_rollback", True)

    def test_invalid_memory_retention_predictor(self):
        self.assertInvalidApplication("memory_write_performed", True)
        self.assertInvalidApplication("retained_jsonl_write_performed", True)
        self.assertInvalidApplication("retention_write_performed", True)
        self.assertInvalidApplication("predictor_mutation_performed", True)
        self.assertInvalidRollback("memory_write_performed", True)
        self.assertInvalidRollback("retention_write_performed", True)
        self.assertInvalidRollback("predictor_mutation_performed", True)

    def test_invalid_selected_final_direct_rule(self):
        self.assertInvalidApplication("selected_action_created", True)
        self.assertInvalidApplication("final_action_created", True)
        self.assertInvalidApplication("direct_command_created", True)
        self.assertInvalidApplication("persistent_rule_created", True)
        self.assertInvalidRollback("selected_action_created", True)
        self.assertInvalidRollback("final_action_created", True)
        self.assertInvalidRollback("direct_command_created", True)
        self.assertInvalidRollback("persistent_rule_created", True)

    def test_invalid_production_proof_autonomous_llm(self):
        self.assertInvalidApplication("production_behavior_changed", True)
        self.assertInvalidApplication("proof_of_learning_claim_allowed", True)
        self.assertInvalidApplication("autonomous_learning_claim_allowed", True)
        self.assertInvalidApplication("autonomous_action_claim_allowed", True)
        self.assertInvalidApplication("llm_used", True)
        self.assertInvalidRollback("production_behavior_changed", True)
        self.assertInvalidRollback("proof_of_learning_claim_allowed", True)
        self.assertInvalidRollback("autonomous_learning_claim_allowed", True)
        self.assertInvalidRollback("autonomous_action_claim_allowed", True)
        self.assertInvalidRollback("llm_used", True)

    def test_summary_counts_are_deterministic(self):
        result = run_ephemeral_feedback_application_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_application_count"])
        self.assertEqual(1, summary["valid_rollback_count"])
        self.assertGreaterEqual(summary["invalid_application_count"], 20)
        self.assertGreaterEqual(summary["invalid_rollback_count"], 17)
        self.assertEqual(1, summary["feedback_source_checked_count"])
        self.assertEqual(1, summary["ephemeral_update_checked_count"])
        self.assertEqual(1, summary["rollback_checked_count"])
        self.assertEqual(1, summary["persistent_update_blocked_count"])
        self.assertEqual(1, summary["cross_session_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_ephemeral_feedback_application_checks_passed"])

    def assertInvalidApplication(self, field, value):
        record = deepcopy(build_ephemeral_feedback_application_record())
        record[field] = value

        self.assertFalse(validate_ephemeral_feedback_application_record(record)["valid"])

    def assertInvalidRollback(self, field, value):
        record = deepcopy(build_ephemeral_feedback_rollback_record())
        record[field] = value

        self.assertFalse(validate_ephemeral_feedback_rollback_record(record)["valid"])


if __name__ == "__main__":
    unittest.main()
