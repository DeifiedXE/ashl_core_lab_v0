import copy
import unittest

from ashl_core.sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_minimal import (
    run_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_minimal_check,
)
from ashl_core.sandbox_candidate_ordering_arbitration_outcome_feedback_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_outcome_feedback_record,
    run_sandbox_candidate_ordering_arbitration_outcome_feedback_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_outcome_feedback_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationOutcomeFeedbackMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_minimal_check()[
            "valid_records"
        ]
        cls.result = run_sandbox_candidate_ordering_arbitration_outcome_feedback_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_feedback_records_are_created(self):
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(record["record_type"], "sandbox_candidate_ordering_arbitration_outcome_feedback_minimal")
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["same_session_feedback"]["feedback_created"])
            self.assertTrue(record["same_session_feedback"]["feedback_evaluation_created"])

    def test_reach_front_item_feedback_record_created(self):
        record = build_sandbox_candidate_ordering_arbitration_outcome_feedback_record(self.sources[0])
        feedback = record["same_session_feedback"]
        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "item_reachable_feedback_prioritizes_reach")
        self.assertEqual(feedback["feedback_type"], "arbitration_positive_item_contact_feedback")
        self.assertEqual(feedback["signals"]["success"], 1.0)

    def test_wait_or_observe_feedback_record_created(self):
        feedback = self.wait["same_session_feedback"]
        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_record(self.wait)

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "item_not_afforded_blocks_feedback_priority")
        self.assertEqual(feedback["feedback_type"], "arbitration_wait_context_observation_feedback")
        self.assertEqual(feedback["feedback_valence"], "bounded_context_observation")

    def test_probe_feedback_record_created(self):
        feedback = self.probe["same_session_feedback"]
        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_record(self.probe)

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "mismatch_feedback_outranks_retry_tendency")
        self.assertEqual(feedback["feedback_type"], "arbitration_mismatch_probe_context_feedback")
        self.assertEqual(feedback["feedback_valence"], "bounded_probe_resolution")

    def test_feedback_record_does_not_apply_or_reorder(self):
        for record in self.records:
            feedback = record["same_session_feedback"]

            self.assertTrue(feedback["feedback_evaluation_created"])
            self.assertFalse(feedback["feedback_applied"])
            self.assertFalse(feedback["feedback_loop_created"])
            self.assertFalse(feedback["candidate_reordering_created"])
            self.assertFalse(feedback["candidate_scores_changed"])
            self.assertFalse(feedback["next_cycle_candidate_ordering_changed"])
            self.assertTrue(feedback["future_candidate_reordering_requires_separate_boundary"])

    def test_feedback_record_does_not_create_action_command_or_execution(self):
        for record in self.records:
            feedback = record["same_session_feedback"]

            self.assertFalse(feedback["new_action_created"])
            self.assertFalse(feedback["new_selected_action_created"])
            self.assertFalse(feedback["new_final_action_created"])
            self.assertFalse(feedback["new_direct_command_created"])
            self.assertFalse(feedback["new_execution_created"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_feedback_approval_boundary"]["source_validated"] = False

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_source_without_approval_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_feedback_approval_boundary"]["future_feedback_allowed"] = False

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_future_feedback_allowed_not_expected", result["error_codes"])

    def test_bad_feedback_type_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["same_session_feedback"]["feedback_type"] = "unknown"

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("same_session_feedback_feedback_type_not_expected", result["error_codes"])

    def test_feedback_evaluation_missing_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["same_session_feedback"]["feedback_evaluation_created"] = False

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("same_session_feedback_feedback_evaluation_created_not_expected", result["error_codes"])

    def test_feedback_application_true_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["same_session_feedback"]["feedback_applied"] = True

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("same_session_feedback_feedback_applied_not_expected", result["error_codes"])

    def test_reordering_or_score_change_true_blocks(self):
        for field in (
            "candidate_reordering_created",
            "candidate_scores_changed",
            "next_cycle_candidate_ordering_changed",
        ):
            bad = copy.deepcopy(self.wait)
            bad["same_session_feedback"][field] = True

            result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"same_session_feedback_{field}_not_expected", result["error_codes"])

    def test_new_action_or_command_or_execution_true_blocks(self):
        for field in (
            "new_action_created",
            "new_selected_action_created",
            "new_final_action_created",
            "new_direct_command_created",
            "new_execution_created",
        ):
            bad = copy.deepcopy(self.reach)
            bad["same_session_feedback"][field] = True

            result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"same_session_feedback_{field}_not_expected", result["error_codes"])

    def test_memory_predictor_direct_feed_and_proof_flags_block(self):
        for field in (
            "memory_write",
            "retention_write",
            "predictor_read_enabled",
            "predictor_influence_enabled",
            "predictor_modified",
            "direct_endocrine_feed",
            "direct_tendency_feed",
            "proof_of_learning_claim",
        ):
            bad = copy.deepcopy(self.probe)
            bad["blocked_flags"][field] = True

            result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["feedback_result_count"], 42)
        self.assertEqual(summary["valid_feedback_count"], 3)
        self.assertEqual(summary["invalid_feedback_count"], 39)
        self.assertEqual(summary["feedback_created_count"], 3)
        self.assertEqual(summary["feedback_evaluation_created_count"], 3)
        self.assertEqual(summary["sandbox_only_feedback_count"], 3)
        self.assertEqual(summary["feedback_budget_checked_count"], 3)
        self.assertEqual(summary["positive_item_feedback_count"], 1)
        self.assertEqual(summary["wait_context_feedback_count"], 1)
        self.assertEqual(summary["mismatch_probe_feedback_count"], 1)
        self.assertEqual(summary["feedback_application_blocked_count"], 3)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-sandbox-candidate-ordering-arbitration-outcome-feedback-minimal-check")

        self.assertEqual(
            result["command"],
            "run-sandbox-candidate-ordering-arbitration-outcome-feedback-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
