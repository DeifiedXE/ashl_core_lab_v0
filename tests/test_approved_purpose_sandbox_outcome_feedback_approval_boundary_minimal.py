import copy
import unittest

from ashl_core.approved_purpose_sandbox_direct_command_outcome_observation_minimal import (
    run_approved_purpose_sandbox_direct_command_outcome_observation_minimal_check,
)
from ashl_core.approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_approved_purpose_sandbox_outcome_feedback_approval_boundary_record,
    run_approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal_check,
    validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record,
)
from ashl_core.teaching_cli import run_command


class ApprovedPurposeSandboxOutcomeFeedbackApprovalBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_approved_purpose_sandbox_direct_command_outcome_observation_minimal_check()[
            "valid_records"
        ]
        cls.result = run_approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.comfort = cls.records[2]

    def test_valid_feedback_approval_boundaries_are_created(self):
        for record in self.records:
            result = validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(
                record["record_type"],
                "approved_purpose_sandbox_outcome_feedback_approval_boundary_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["feedback_approval_boundary"]["future_feedback_allowed"])

    def test_reach_outcome_can_enter_future_feedback(self):
        record = build_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(self.sources[0])
        boundary = record["feedback_approval_boundary"]
        result = validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "approach_or_reach_item")
        self.assertEqual(result["observed_outcome"], "front_item_reached")
        self.assertEqual(boundary["candidate_for_future_feedback"], "positive_item_contact_feedback")

    def test_probe_outcome_can_enter_future_feedback(self):
        boundary = self.mismatch["feedback_approval_boundary"]
        result = validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["observed_outcome"], "local_context_observed")
        self.assertEqual(boundary["candidate_for_future_feedback"], "mismatch_resolution_observation_feedback")

    def test_support_outcome_can_enter_future_feedback(self):
        boundary = self.comfort["feedback_approval_boundary"]
        result = validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(self.comfort)

        self.assertTrue(result["valid"])
        self.assertEqual(result["observed_outcome"], "low_pressure_support_offered")
        self.assertEqual(boundary["candidate_for_future_feedback"], "bounded_support_outcome_feedback")

    def test_boundary_does_not_apply_feedback_or_reorder(self):
        for record in self.records:
            boundary = record["feedback_approval_boundary"]

            self.assertFalse(boundary["feedback_applied_in_this_package"])
            self.assertFalse(boundary["candidate_reordering_created_in_this_package"])
            self.assertFalse(boundary["new_action_created_in_this_package"])
            self.assertTrue(boundary["future_candidate_reordering_requires_separate_boundary"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_outcome_observation"]["source_validated"] = False

        result = validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_source_already_has_feedback_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_outcome_observation"]["feedback_loop_created"] = True

        result = validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("feedback_loop_created_not_expected", result["error_codes"])

    def test_feedback_application_true_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["feedback_approval_boundary"]["feedback_applied_in_this_package"] = True

        result = validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("feedback_approval_boundary_feedback_applied_in_this_package_not_expected", result["error_codes"])

    def test_reordering_true_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["feedback_approval_boundary"]["candidate_reordering_created_in_this_package"] = True

        result = validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "feedback_approval_boundary_candidate_reordering_created_in_this_package_not_expected",
            result["error_codes"],
        )

    def test_memory_predictor_manipulation_and_proof_flags_block(self):
        for field in (
            "memory_write",
            "predictor_modified",
            "emotional_manipulation",
            "proof_of_learning_claim",
        ):
            bad = copy.deepcopy(self.comfort)
            bad["blocked_flags"][field] = True

            result = validate_approved_purpose_sandbox_outcome_feedback_approval_boundary_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["feedback_approval_boundary_result_count"], 34)
        self.assertEqual(summary["valid_feedback_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_feedback_approval_boundary_count"], 31)
        self.assertEqual(summary["future_feedback_allowed_count"], 3)
        self.assertEqual(summary["positive_item_feedback_boundary_count"], 1)
        self.assertEqual(summary["mismatch_feedback_boundary_count"], 1)
        self.assertEqual(summary["support_feedback_boundary_count"], 1)
        self.assertEqual(summary["feedback_application_blocked_count"], 3)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-approved-purpose-sandbox-outcome-feedback-approval-boundary-minimal-check")

        self.assertEqual(
            result["command"],
            "run-approved-purpose-sandbox-outcome-feedback-approval-boundary-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
