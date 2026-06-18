import copy
import unittest

from ashl_core.approved_purpose_candidate_ordering_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_approved_purpose_candidate_ordering_boundary_record,
    run_approved_purpose_candidate_ordering_boundary_minimal_check,
    validate_approved_purpose_candidate_ordering_boundary_record,
)
from ashl_core.proto_purpose_approval_boundary_minimal import run_proto_purpose_approval_boundary_minimal_check
from ashl_core.teaching_cli import run_command


class ApprovedPurposeCandidateOrderingBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_proto_purpose_approval_boundary_minimal_check()["valid_records"]
        cls.result = run_approved_purpose_candidate_ordering_boundary_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.comfort = cls.records[2]

    def test_valid_ordering_boundary_records_are_created(self):
        for record in self.records:
            result = validate_approved_purpose_candidate_ordering_boundary_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(
                record["ordering_boundary_type"],
                "approved_purpose_candidate_ordering_boundary_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_approach_or_reach_item_opens_positive_item_candidate_family(self):
        record = build_approved_purpose_candidate_ordering_boundary_record(self.sources[0])
        boundary = record["candidate_ordering_boundary"]
        result = validate_approved_purpose_candidate_ordering_boundary_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "approach_or_reach_item")
        self.assertEqual(boundary["allowed_candidate_family"], "positive_item_interaction_candidates")
        self.assertEqual(boundary["ordering_scope"], "sandbox_positive_item_scope")

    def test_resolve_mismatch_opens_verification_candidate_family(self):
        boundary = self.mismatch["candidate_ordering_boundary"]
        result = validate_approved_purpose_candidate_ordering_boundary_record(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "resolve_mismatch")
        self.assertEqual(boundary["allowed_candidate_family"], "verification_or_observation_candidates")
        self.assertEqual(boundary["ordering_scope"], "sandbox_verification_scope")

    def test_support_user_comfort_opens_bounded_comfort_candidate_family(self):
        boundary = self.comfort["candidate_ordering_boundary"]
        result = validate_approved_purpose_candidate_ordering_boundary_record(self.comfort)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "support_user_comfort")
        self.assertEqual(boundary["allowed_candidate_family"], "bounded_comfort_support_candidates")
        self.assertEqual(boundary["ordering_scope"], "bounded_interaction_support_scope")

    def test_boundary_does_not_apply_ordering_or_create_actions(self):
        for record in self.records:
            boundary = record["candidate_ordering_boundary"]

            self.assertTrue(boundary["candidate_ordering_boundary_opened"])
            self.assertTrue(boundary["candidate_ordering_allowed_in_future_package"])
            self.assertFalse(boundary["candidate_ordering_applied_in_this_package"])
            self.assertFalse(boundary["candidate_ordering_changed"])
            self.assertEqual(boundary["candidate_order_before"], [])
            self.assertEqual(boundary["candidate_order_after"], [])
            self.assertEqual(boundary["ordering_delta"], 0.0)
            self.assertFalse(boundary["selected_action_created"])
            self.assertFalse(boundary["final_action_created"])
            self.assertFalse(boundary["direct_command_created"])
            self.assertFalse(boundary["sandbox_action_executed"])

    def test_unvalidated_source_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_approved_purpose"]["source_validated"] = False

        result = validate_approved_purpose_candidate_ordering_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_unknown_approved_purpose_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_approved_purpose"]["approved_purpose"] = "make_user_happy"

        result = validate_approved_purpose_candidate_ordering_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("approved_purpose_not_allowed", result["error_codes"])

    def test_source_action_authority_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_approved_purpose"]["action_authority_granted"] = True

        result = validate_approved_purpose_candidate_ordering_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_action_authority_granted_not_false", result["error_codes"])

    def test_wrong_candidate_family_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["candidate_ordering_boundary"]["allowed_candidate_family"] = "reward_chase"

        result = validate_approved_purpose_candidate_ordering_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("allowed_candidate_family_not_expected", result["error_codes"])

    def test_ordering_applied_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["candidate_ordering_boundary"]["candidate_ordering_applied_in_this_package"] = True

        result = validate_approved_purpose_candidate_ordering_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "candidate_ordering_boundary_candidate_ordering_applied_in_this_package_not_expected",
            result["error_codes"],
        )

    def test_candidate_order_changed_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["candidate_ordering_boundary"]["candidate_order_after"] = ["reach_item"]

        result = validate_approved_purpose_candidate_ordering_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("candidate_ordering_boundary_candidate_order_after_not_expected", result["error_codes"])

    def test_selected_action_created_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["candidate_ordering_boundary"]["selected_action_created"] = True

        result = validate_approved_purpose_candidate_ordering_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("candidate_ordering_boundary_selected_action_created_not_expected", result["error_codes"])

    def test_memory_write_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["blocked_flags"]["memory_write"] = True

        result = validate_approved_purpose_candidate_ordering_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_memory_write_not_false", result["error_codes"])

    def test_predictor_modified_blocks(self):
        bad = copy.deepcopy(self.mismatch)
        bad["blocked_flags"]["predictor_modified"] = True

        result = validate_approved_purpose_candidate_ordering_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_predictor_modified_not_false", result["error_codes"])

    def test_emotional_manipulation_blocks(self):
        bad = copy.deepcopy(self.comfort)
        bad["blocked_flags"]["emotional_manipulation"] = True

        result = validate_approved_purpose_candidate_ordering_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_emotional_manipulation_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["approved_purpose_candidate_ordering_boundary_result_count"], 31)
        self.assertEqual(summary["valid_approved_purpose_candidate_ordering_boundary_count"], 3)
        self.assertEqual(summary["invalid_approved_purpose_candidate_ordering_boundary_count"], 28)
        self.assertEqual(summary["candidate_ordering_boundary_opened_count"], 3)
        self.assertEqual(summary["future_candidate_ordering_allowed_count"], 3)
        self.assertEqual(summary["approach_or_reach_item_boundary_count"], 1)
        self.assertEqual(summary["resolve_mismatch_boundary_count"], 1)
        self.assertEqual(summary["support_user_comfort_boundary_count"], 1)
        self.assertEqual(summary["candidate_ordering_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-approved-purpose-candidate-ordering-boundary-minimal-check")

        self.assertEqual(result["command"], "run-approved-purpose-candidate-ordering-boundary-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()

