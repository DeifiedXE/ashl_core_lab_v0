import unittest
from copy import deepcopy

from ashl_core.approved_purpose_feedback_gated_candidate_reordering_approval_boundary_minimal import (
    run_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_minimal_check,
)
from ashl_core.approved_purpose_feedback_gated_candidate_reordering_minimal import (
    build_approved_purpose_feedback_gated_candidate_reordering_record,
    run_approved_purpose_feedback_gated_candidate_reordering_minimal_check,
    validate_approved_purpose_feedback_gated_candidate_reordering_record,
)
from ashl_core.teaching_cli import run_command


class ApprovedPurposeFeedbackGatedCandidateReorderingMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_approved_purpose_feedback_gated_candidate_reordering_approval_boundary_minimal_check()[
            "valid_records"
        ]
        cls.result = run_approved_purpose_feedback_gated_candidate_reordering_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.support = cls.records[2]

    def assert_invalid(self, record: dict) -> None:
        result = validate_approved_purpose_feedback_gated_candidate_reordering_record(record)
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])

    def test_valid_reordering_records_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = validate_approved_purpose_feedback_gated_candidate_reordering_record(record)
            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(record["record_type"], "approved_purpose_feedback_gated_candidate_reordering_minimal")

    def test_boundary_versions_are_b137_to_b138(self):
        boundary = self.result["boundary"]
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b137")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b138")

    def test_positive_item_feedback_prioritizes_reach_front_item(self):
        record = build_approved_purpose_feedback_gated_candidate_reordering_record(self.sources[0])
        reordering = record["feedback_gated_candidate_reordering"]
        self.assertEqual(reordering["feedback_type"], "positive_item_contact_feedback")
        self.assertEqual(reordering["candidate_family"], "positive_item_interaction_candidates")
        self.assertEqual(reordering["candidate_actions_after_reordering"][0], "reach_front_item")
        self.assertEqual(reordering["primary_ranked_action"], "reach_front_item")

    def test_mismatch_feedback_prioritizes_observation_before_retry(self):
        reordering = self.mismatch["feedback_gated_candidate_reordering"]
        after = reordering["candidate_actions_after_reordering"]
        self.assertEqual(reordering["feedback_type"], "mismatch_resolution_observation_feedback")
        self.assertEqual(after[0], "observe_or_alternative_probe")
        self.assertLess(after.index("check_before_retry"), after.index("retry_same_action_without_check"))

    def test_support_feedback_prioritizes_low_pressure_support(self):
        reordering = self.support["feedback_gated_candidate_reordering"]
        self.assertEqual(reordering["feedback_type"], "bounded_support_outcome_feedback")
        self.assertEqual(reordering["candidate_actions_after_reordering"][0], "offer_low_pressure_support")
        self.assertNotIn("force_user_happiness", reordering["candidate_actions_after_reordering"])

    def test_reordering_is_sandbox_only_and_advisory(self):
        for record in self.records:
            reordering = record["feedback_gated_candidate_reordering"]
            self.assertTrue(reordering["candidate_reordering_applied"])
            self.assertTrue(reordering["candidate_order_changed"])
            self.assertTrue(reordering["reordering_is_sandbox_only"])
            self.assertTrue(reordering["reordering_is_advisory"])

    def test_no_action_creation_or_execution(self):
        reordering = self.reward["feedback_gated_candidate_reordering"]
        self.assertFalse(reordering["action_intent_created"])
        self.assertFalse(reordering["selected_action_created"])
        self.assertFalse(reordering["final_action_created"])
        self.assertFalse(reordering["direct_command_created"])
        self.assertFalse(reordering["sandbox_execution_created"])

    def test_no_direct_endocrine_or_tendency_feed(self):
        reordering = self.reward["feedback_gated_candidate_reordering"]
        self.assertFalse(reordering["direct_endocrine_feed"])
        self.assertFalse(reordering["direct_tendency_feed"])

    def test_rollback_preview_restores_before_order(self):
        for record in self.records:
            self.assertTrue(record["rollback_preview"]["rollback_available"])
            self.assertEqual(
                record["rollback_preview"]["candidate_actions_restored"],
                record["feedback_gated_candidate_reordering"]["candidate_actions_before_reordering"],
            )
            self.assertFalse(record["rollback_preview"]["dirty_state_after_rollback"])

    def test_candidate_reordering_not_applied_blocks(self):
        bad = deepcopy(self.reward)
        bad["feedback_gated_candidate_reordering"]["candidate_reordering_applied"] = False
        self.assert_invalid(bad)

    def test_primary_not_first_blocks(self):
        bad = deepcopy(self.reward)
        bad["feedback_gated_candidate_reordering"]["candidate_actions_after_reordering"] = [
            "wait_or_observe",
            "reach_front_item",
            "step_toward_item",
            "fallback_stop_and_report",
        ]
        self.assert_invalid(bad)

    def test_selected_action_created_blocks(self):
        bad = deepcopy(self.reward)
        bad["feedback_gated_candidate_reordering"]["selected_action_created"] = True
        self.assert_invalid(bad)

    def test_direct_tendency_feed_blocks(self):
        bad = deepcopy(self.reward)
        bad["feedback_gated_candidate_reordering"]["direct_tendency_feed"] = True
        self.assert_invalid(bad)

    def test_memory_write_blocks(self):
        bad = deepcopy(self.mismatch)
        bad["blocked_flags"]["memory_write"] = True
        self.assert_invalid(bad)

    def test_manipulative_candidate_blocks(self):
        bad = deepcopy(self.support)
        bad["feedback_gated_candidate_reordering"]["candidate_actions_after_reordering"] = [
            "force_user_happiness",
            "offer_low_pressure_support",
            "ask_if_help_needed",
            "stop_and_wait",
        ]
        self.assert_invalid(bad)

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]
        self.assertEqual(summary["feedback_gated_reordering_result_count"], 38)
        self.assertEqual(summary["valid_feedback_gated_reordering_count"], 3)
        self.assertEqual(summary["invalid_feedback_gated_reordering_count"], 35)
        self.assertEqual(summary["candidate_reordering_applied_count"], 3)
        self.assertEqual(summary["candidate_order_changed_count"], 3)
        self.assertEqual(summary["sandbox_only_checked_count"], 3)
        self.assertEqual(summary["advisory_only_checked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["direct_feedback_to_endocrine_blocked_count"], 3)
        self.assertEqual(summary["direct_feedback_to_tendency_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["rollback_available_count"], 3)

    def test_cli_command(self):
        result = run_command("run-approved-purpose-feedback-gated-candidate-reordering-minimal-check")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["valid_feedback_gated_reordering_count"], 3)


if __name__ == "__main__":
    unittest.main()
