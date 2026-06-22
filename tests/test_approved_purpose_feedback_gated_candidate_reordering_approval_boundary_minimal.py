import unittest
from copy import deepcopy

from ashl_core.approved_purpose_feedback_gated_candidate_reordering_approval_boundary_minimal import (
    build_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_record,
    run_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_minimal_check,
    validate_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_record,
)
from ashl_core.teaching_cli import run_command


class ApprovedPurposeFeedbackGatedCandidateReorderingApprovalBoundaryMinimalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = run_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_minimal_check()
        self.records = self.result["valid_records"]
        self.first = self.records[0]

    def assert_invalid(self, record: dict) -> None:
        validation = validate_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_record(record)
        self.assertFalse(validation["valid"])
        self.assertTrue(validation["error_codes"])

    def test_valid_records_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            validation = validate_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_record(record)
            self.assertTrue(validation["valid"], validation["error_codes"])

    def test_boundary_versions_are_b136_to_b137(self):
        boundary = self.result["boundary"]
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b136")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b137")
        self.assertTrue(boundary["boundary_change_required"])

    def test_positive_feedback_opens_positive_item_future_reordering_boundary(self):
        boundary = self.records[0]["feedback_gated_reordering_boundary"]
        self.assertEqual(boundary["feedback_type"], "positive_item_contact_feedback")
        self.assertEqual(boundary["approved_purpose"], "approach_or_reach_item")
        self.assertEqual(boundary["candidate_family"], "positive_item_interaction_candidates")
        self.assertEqual(boundary["candidate_to_prioritize_in_future_package"], "reach_front_item")

    def test_mismatch_feedback_opens_verification_future_reordering_boundary(self):
        boundary = self.records[1]["feedback_gated_reordering_boundary"]
        self.assertEqual(boundary["feedback_type"], "mismatch_resolution_observation_feedback")
        self.assertEqual(boundary["approved_purpose"], "resolve_mismatch")
        self.assertEqual(boundary["candidate_family"], "verification_or_observation_candidates")
        self.assertEqual(boundary["candidate_to_prioritize_in_future_package"], "observe_or_alternative_probe")

    def test_support_feedback_opens_support_future_reordering_boundary(self):
        boundary = self.records[2]["feedback_gated_reordering_boundary"]
        self.assertEqual(boundary["feedback_type"], "bounded_support_outcome_feedback")
        self.assertEqual(boundary["approved_purpose"], "support_user_comfort")
        self.assertEqual(boundary["candidate_family"], "bounded_comfort_support_candidates")
        self.assertEqual(boundary["candidate_to_prioritize_in_future_package"], "offer_low_pressure_support")

    def test_no_candidate_order_changes_now(self):
        boundary = self.first["feedback_gated_reordering_boundary"]
        self.assertTrue(boundary["candidate_reordering_allowed_in_future_package"])
        self.assertFalse(boundary["candidate_reordering_applied_in_this_package"])
        self.assertFalse(boundary["candidate_ordering_changed"])
        self.assertEqual(boundary["candidate_order_before"], [])
        self.assertEqual(boundary["candidate_order_after"], [])
        self.assertEqual(boundary["ordering_delta"], 0.0)

    def test_no_action_creation_or_execution(self):
        boundary = self.first["feedback_gated_reordering_boundary"]
        self.assertFalse(boundary["action_intent_created"])
        self.assertFalse(boundary["selected_action_created"])
        self.assertFalse(boundary["final_action_created"])
        self.assertFalse(boundary["direct_command_created"])
        self.assertFalse(boundary["sandbox_execution_created"])

    def test_no_direct_endocrine_or_tendency_feed(self):
        safety = self.first["feedback_safety_boundary"]
        self.assertTrue(safety["feedback_must_be_trace_only"])
        self.assertTrue(safety["same_session_scope_required"])
        self.assertFalse(safety["direct_endocrine_feed_allowed"])
        self.assertFalse(safety["direct_tendency_feed_allowed"])

    def test_memory_retention_and_predictor_require_separate_boundaries(self):
        safety = self.first["feedback_safety_boundary"]
        self.assertTrue(safety["memory_write_requires_separate_boundary"])
        self.assertTrue(safety["retention_write_requires_separate_boundary"])
        self.assertTrue(safety["predictor_influence_requires_separate_boundary"])

    def test_bad_feedback_type_blocks(self):
        record = deepcopy(self.first)
        record["source_feedback_trace"]["feedback_type"] = "bad_feedback"
        self.assert_invalid(record)

    def test_candidate_reordering_now_blocks(self):
        record = deepcopy(self.first)
        record["feedback_gated_reordering_boundary"]["candidate_reordering_applied_in_this_package"] = True
        self.assert_invalid(record)

    def test_action_creation_blocks(self):
        record = deepcopy(self.first)
        record["feedback_gated_reordering_boundary"]["selected_action_created"] = True
        self.assert_invalid(record)

    def test_direct_tendency_feed_blocks(self):
        record = deepcopy(self.first)
        record["feedback_safety_boundary"]["direct_tendency_feed_allowed"] = True
        self.assert_invalid(record)

    def test_blocked_flags_true_block(self):
        record = deepcopy(self.first)
        record["blocked_flags"]["memory_write"] = True
        self.assert_invalid(record)

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]
        self.assertEqual(summary["reordering_boundary_result_count"], 38)
        self.assertEqual(summary["valid_reordering_boundary_count"], 3)
        self.assertEqual(summary["invalid_reordering_boundary_count"], 35)
        self.assertEqual(summary["future_reordering_boundary_opened_count"], 3)
        self.assertEqual(summary["candidate_reordering_allowed_future_count"], 3)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["direct_feedback_to_endocrine_blocked_count"], 3)
        self.assertEqual(summary["direct_feedback_to_tendency_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-approved-purpose-feedback-gated-candidate-reordering-approval-boundary-minimal-check"
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["valid_reordering_boundary_count"], 3)


if __name__ == "__main__":
    unittest.main()
