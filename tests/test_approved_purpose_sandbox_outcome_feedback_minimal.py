import copy
import unittest

from ashl_core.approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal import (
    run_approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal_check,
)
from ashl_core.approved_purpose_sandbox_outcome_feedback_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_approved_purpose_sandbox_outcome_feedback_record,
    run_approved_purpose_sandbox_outcome_feedback_minimal_check,
    validate_approved_purpose_sandbox_outcome_feedback_record,
)
from ashl_core.teaching_cli import run_command


class ApprovedPurposeSandboxOutcomeFeedbackMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal_check()[
            "valid_records"
        ]
        cls.result = run_approved_purpose_sandbox_outcome_feedback_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.support = cls.records[2]

    def test_valid_feedback_traces_are_created(self):
        for record in self.records:
            result = validate_approved_purpose_sandbox_outcome_feedback_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(record["record_type"], "approved_purpose_sandbox_outcome_feedback_minimal")
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["same_session_feedback_trace"]["feedback_created"])
            self.assertTrue(record["same_session_feedback_trace"]["trace_only"])

    def test_positive_item_feedback_created_from_front_item_reached(self):
        record = build_approved_purpose_sandbox_outcome_feedback_record(self.sources[0])
        feedback = record["same_session_feedback_trace"]
        result = validate_approved_purpose_sandbox_outcome_feedback_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["observed_outcome"], "front_item_reached")
        self.assertEqual(feedback["feedback_type"], "positive_item_contact_feedback")
        self.assertEqual(feedback["signals"]["success"], 1.0)

    def test_mismatch_feedback_created_from_local_context_observed(self):
        feedback = self.mismatch["same_session_feedback_trace"]
        result = validate_approved_purpose_sandbox_outcome_feedback_record(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["observed_outcome"], "local_context_observed")
        self.assertEqual(feedback["feedback_type"], "mismatch_resolution_observation_feedback")
        self.assertEqual(feedback["feedback_valence"], "bounded_resolution")

    def test_support_feedback_does_not_claim_user_happiness(self):
        feedback = self.support["same_session_feedback_trace"]
        result = validate_approved_purpose_sandbox_outcome_feedback_record(self.support)

        self.assertTrue(result["valid"])
        self.assertEqual(result["observed_outcome"], "low_pressure_support_offered")
        self.assertEqual(feedback["feedback_type"], "bounded_support_outcome_feedback")
        self.assertFalse(feedback["user_happiness_claim"])
        self.assertFalse(feedback["emotional_manipulation"])

    def test_feedback_does_not_reorder_or_create_actions(self):
        for record in self.records:
            feedback = record["same_session_feedback_trace"]

            self.assertFalse(feedback["candidate_reordering_created"])
            self.assertFalse(feedback["action_intent_created"])
            self.assertFalse(feedback["selected_action_created"])
            self.assertFalse(feedback["final_action_created"])
            self.assertFalse(feedback["direct_command_created"])
            self.assertFalse(feedback["sandbox_execution_created"])

    def test_feedback_does_not_directly_feed_endocrine_or_tendency(self):
        for record in self.records:
            feedback = record["same_session_feedback_trace"]
            safety = record["feedback_safety_boundary"]

            self.assertFalse(feedback["direct_endocrine_feed"])
            self.assertFalse(feedback["direct_tendency_feed"])
            self.assertTrue(safety["feedback_must_enter_trace_first"])
            self.assertFalse(safety["direct_endocrine_feed_allowed"])
            self.assertFalse(safety["direct_tendency_feed_allowed"])

    def test_future_reordering_requires_separate_boundary(self):
        for record in self.records:
            safety = record["feedback_safety_boundary"]

            self.assertTrue(safety["candidate_reordering_requires_separate_boundary"])
            self.assertTrue(safety["memory_write_requires_separate_boundary"])
            self.assertTrue(safety["predictor_influence_requires_separate_boundary"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_feedback_approval_boundary"]["source_validated"] = False

        result = validate_approved_purpose_sandbox_outcome_feedback_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_wrong_feedback_type_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["same_session_feedback_trace"]["feedback_type"] = "unknown"

        result = validate_approved_purpose_sandbox_outcome_feedback_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("same_session_feedback_trace_feedback_type_not_expected", result["error_codes"])

    def test_candidate_reordering_true_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["same_session_feedback_trace"]["candidate_reordering_created"] = True

        result = validate_approved_purpose_sandbox_outcome_feedback_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("same_session_feedback_trace_candidate_reordering_created_not_expected", result["error_codes"])

    def test_direct_tendency_feed_true_blocks(self):
        bad = copy.deepcopy(self.mismatch)
        bad["same_session_feedback_trace"]["direct_tendency_feed"] = True

        result = validate_approved_purpose_sandbox_outcome_feedback_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("same_session_feedback_trace_direct_tendency_feed_not_expected", result["error_codes"])

    def test_safety_direct_endocrine_allowed_blocks(self):
        bad = copy.deepcopy(self.support)
        bad["feedback_safety_boundary"]["direct_endocrine_feed_allowed"] = True

        result = validate_approved_purpose_sandbox_outcome_feedback_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("feedback_safety_boundary_direct_endocrine_feed_allowed_not_expected", result["error_codes"])

    def test_blocked_flags_true_block(self):
        bad = copy.deepcopy(self.support)
        bad["blocked_flags"]["proof_of_learning_claim"] = True

        result = validate_approved_purpose_sandbox_outcome_feedback_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_proof_of_learning_claim_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["feedback_result_count"], 44)
        self.assertEqual(summary["valid_feedback_count"], 3)
        self.assertEqual(summary["invalid_feedback_count"], 41)
        self.assertEqual(summary["feedback_created_count"], 3)
        self.assertEqual(summary["positive_item_feedback_count"], 1)
        self.assertEqual(summary["mismatch_feedback_count"], 1)
        self.assertEqual(summary["support_feedback_count"], 1)
        self.assertEqual(summary["trace_only_count"], 3)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["direct_feedback_to_endocrine_blocked_count"], 3)
        self.assertEqual(summary["direct_feedback_to_tendency_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-approved-purpose-sandbox-outcome-feedback-minimal-check")

        self.assertEqual(result["command"], "run-approved-purpose-sandbox-outcome-feedback-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
