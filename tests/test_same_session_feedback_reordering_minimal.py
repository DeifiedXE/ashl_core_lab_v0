import unittest
from copy import deepcopy

from ashl_core.same_session_feedback_reordering_minimal import (
    AFTER_ACTIONS,
    BEFORE_ACTIONS,
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_same_session_feedback_reordering_record,
    build_same_session_feedback_reordering_rollback_record,
    run_same_session_feedback_reordering_minimal_check,
    validate_same_session_feedback_reordering_record,
    validate_same_session_feedback_reordering_rollback_record,
)
from ashl_core.teaching_cli import run_command


class SameSessionFeedbackReorderingMinimalTests(unittest.TestCase):
    def test_valid_same_session_feedback_reordering(self):
        record = build_same_session_feedback_reordering_record()
        result = validate_same_session_feedback_reordering_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("same_session_feedback_reordering", record["record_type"])
        self.assertEqual("completed_same_session_feedback_reordering", record["reordering_status"])
        self.assertEqual("ephemeral_feedback_application_b92", record["source_ephemeral_feedback_application"])
        self.assertTrue(record["same_session_only"])
        self.assertTrue(record["ephemeral_feedback_used"])

    def test_uses_b92_ephemeral_feedback_source(self):
        record = build_same_session_feedback_reordering_record()

        self.assertEqual("2026-06-09-b92", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b93", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual(0.61, record["doubt_after_ephemeral"])
        self.assertEqual(0.55, record["verification_candidate_trust_after_ephemeral"])
        self.assertEqual(0.35, record["direct_retry_weight_after_ephemeral"])
        self.assertEqual(0.62, record["hypothesis_trust_after_ephemeral"])

    def test_candidate_ordering_is_reordered(self):
        record = build_same_session_feedback_reordering_record()

        self.assertEqual(BEFORE_ACTIONS, record["candidate_actions_before_reordering"])
        self.assertEqual(AFTER_ACTIONS, record["candidate_actions_after_reordering"])
        self.assertLess(
            record["candidate_actions_after_reordering"].index("observe_or_alternative_probe"),
            record["candidate_actions_after_reordering"].index("retry_same_action_without_check"),
        )
        self.assertLess(
            record["candidate_actions_after_reordering"].index("check_before_retry"),
            record["candidate_actions_after_reordering"].index("retry_same_action_without_check"),
        )
        self.assertEqual("retry_same_action_without_check", record["candidate_actions_after_reordering"][-1])

    def test_valid_rollback(self):
        reordering = build_same_session_feedback_reordering_record()
        rollback = build_same_session_feedback_reordering_rollback_record(reordering)
        result = validate_same_session_feedback_reordering_rollback_record(rollback)

        self.assertTrue(result["valid"])
        self.assertEqual("same_session_feedback_reordering_rollback", rollback["record_type"])
        self.assertEqual("same_session_feedback_reordering_rolled_back", rollback["rollback_status"])
        self.assertTrue(rollback["session_end_triggered"])
        self.assertEqual(BEFORE_ACTIONS, rollback["candidate_actions_restored"])
        self.assertFalse(rollback["dirty_state_after_rollback"])

    def test_boundaries_remain_blocked_in_reordering(self):
        record = build_same_session_feedback_reordering_record()

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
            "predictor_read_enabled",
            "predictor_influence_enabled",
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
        rollback = build_same_session_feedback_reordering_rollback_record()

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
            "predictor_read_enabled",
            "predictor_influence_enabled",
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
        result = run_command("run-same-session-feedback-reordering-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_reordering_count"])
        self.assertEqual(1, result["summary"]["valid_rollback_count"])

    def test_invalid_missing_b92_source(self):
        self.assertInvalidReordering("source_ephemeral_feedback_application_record", {})

    def test_invalid_verification_candidate_not_before_direct_retry(self):
        self.assertInvalidReordering("candidate_actions_after_reordering", BEFORE_ACTIONS[:])
        self.assertInvalidReordering("verification_candidate_ranked_before_direct_retry", False)

    def test_invalid_check_before_retry_not_before_direct_retry(self):
        bad_actions = [
            "observe_or_alternative_probe",
            "fallback_stop_and_report",
            "retry_same_action_without_check",
            "check_before_retry",
        ]
        self.assertInvalidReordering("candidate_actions_after_reordering", bad_actions)
        self.assertInvalidReordering("check_before_retry_ranked_before_direct_retry", False)

    def test_invalid_direct_retry_not_last(self):
        self.assertInvalidReordering("candidate_actions_after_reordering", BEFORE_ACTIONS[:])
        self.assertInvalidReordering("direct_retry_ranked_last", False)

    def test_invalid_selected_final_direct_rule(self):
        self.assertInvalidReordering("selected_action_created", True)
        self.assertInvalidReordering("final_action_created", True)
        self.assertInvalidReordering("direct_command_created", True)
        self.assertInvalidReordering("persistent_rule_created", True)
        self.assertInvalidRollback("selected_action_created", True)
        self.assertInvalidRollback("final_action_created", True)
        self.assertInvalidRollback("direct_command_created", True)
        self.assertInvalidRollback("persistent_rule_created", True)

    def test_invalid_persistent_update_and_cross_session(self):
        self.assertInvalidReordering("persistent_update_performed", True)
        self.assertInvalidReordering("cross_session_available", True)
        self.assertInvalidRollback("persistent_update_performed", True)
        self.assertInvalidRollback("cross_session_available", True)

    def test_invalid_rollback_missing_or_dirty(self):
        self.assertInvalidReordering("rollback_required", False)
        self.assertInvalidReordering("rollback_available", False)
        self.assertInvalidRollback("session_end_triggered", False)
        self.assertInvalidRollback("dirty_state_after_rollback", True)

    def test_invalid_memory_retention_predictor(self):
        self.assertInvalidReordering("memory_write_performed", True)
        self.assertInvalidReordering("retained_jsonl_write_performed", True)
        self.assertInvalidReordering("retention_write_performed", True)
        self.assertInvalidReordering("predictor_read_enabled", True)
        self.assertInvalidReordering("predictor_influence_enabled", True)
        self.assertInvalidReordering("predictor_mutation_performed", True)
        self.assertInvalidRollback("memory_write_performed", True)
        self.assertInvalidRollback("retention_write_performed", True)
        self.assertInvalidRollback("predictor_mutation_performed", True)

    def test_invalid_production_proof_autonomous_llm(self):
        self.assertInvalidReordering("production_behavior_changed", True)
        self.assertInvalidReordering("proof_of_learning_claim_allowed", True)
        self.assertInvalidReordering("autonomous_learning_claim_allowed", True)
        self.assertInvalidReordering("autonomous_action_claim_allowed", True)
        self.assertInvalidReordering("llm_used", True)
        self.assertInvalidRollback("production_behavior_changed", True)
        self.assertInvalidRollback("proof_of_learning_claim_allowed", True)
        self.assertInvalidRollback("autonomous_learning_claim_allowed", True)
        self.assertInvalidRollback("autonomous_action_claim_allowed", True)
        self.assertInvalidRollback("llm_used", True)

    def test_summary_counts_are_deterministic(self):
        result = run_same_session_feedback_reordering_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_reordering_count"])
        self.assertEqual(1, summary["valid_rollback_count"])
        self.assertGreaterEqual(summary["invalid_reordering_count"], 25)
        self.assertGreaterEqual(summary["invalid_rollback_count"], 21)
        self.assertEqual(1, summary["feedback_source_checked_count"])
        self.assertEqual(1, summary["verification_rank_checked_count"])
        self.assertEqual(1, summary["check_before_retry_rank_checked_count"])
        self.assertEqual(1, summary["direct_retry_suppression_checked_count"])
        self.assertEqual(1, summary["same_session_checked_count"])
        self.assertEqual(1, summary["rollback_checked_count"])
        self.assertEqual(1, summary["persistent_update_blocked_count"])
        self.assertEqual(1, summary["cross_session_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_same_session_feedback_reordering_checks_passed"])

    def assertInvalidReordering(self, field, value):
        record = deepcopy(build_same_session_feedback_reordering_record())
        record[field] = value

        self.assertFalse(validate_same_session_feedback_reordering_record(record)["valid"])

    def assertInvalidRollback(self, field, value):
        record = deepcopy(build_same_session_feedback_reordering_rollback_record())
        record[field] = value

        self.assertFalse(validate_same_session_feedback_reordering_rollback_record(record)["valid"])


if __name__ == "__main__":
    unittest.main()
