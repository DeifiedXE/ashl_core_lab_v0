import copy
import unittest

from ashl_core.experience_derived_proto_purpose_candidate_trace_minimal import (
    build_experience_derived_proto_purpose_candidate_traces,
)
from ashl_core.proto_purpose_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_proto_purpose_approval_boundary_record,
    run_proto_purpose_approval_boundary_minimal_check,
    validate_proto_purpose_approval_boundary_record,
)
from ashl_core.teaching_cli import run_command


class ProtoPurposeApprovalBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_records = build_experience_derived_proto_purpose_candidate_traces()["records"]
        cls.result = run_proto_purpose_approval_boundary_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.comfort = cls.records[2]

    def test_valid_approval_boundary_records_are_created(self):
        for record in self.records:
            result = validate_proto_purpose_approval_boundary_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(record["approval_record_type"], "proto_purpose_approval_boundary_minimal")
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_reward_proto_purpose_becomes_bounded_approved_purpose(self):
        record = build_proto_purpose_approval_boundary_record(self.source_records[0])
        result = validate_proto_purpose_approval_boundary_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["proto_purpose"], "approach_or_reach_item")
        self.assertEqual(record["approved_purpose_record"]["approved_purpose"], "approach_or_reach_item")
        self.assertEqual(
            record["approved_purpose_record"]["approved_purpose_scope"],
            "bounded_positive_item_contact_scope",
        )

    def test_mismatch_proto_purpose_becomes_bounded_approved_purpose(self):
        result = validate_proto_purpose_approval_boundary_record(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["proto_purpose"], "resolve_mismatch")
        self.assertEqual(
            self.mismatch["approved_purpose_record"]["approved_purpose_scope"],
            "bounded_verification_scope",
        )

    def test_comfort_proto_purpose_becomes_bounded_approved_purpose(self):
        result = validate_proto_purpose_approval_boundary_record(self.comfort)

        self.assertTrue(result["valid"])
        self.assertEqual(result["proto_purpose"], "support_user_comfort")
        self.assertEqual(
            self.comfort["approved_purpose_record"]["approved_purpose_scope"],
            "bounded_comfort_support_scope",
        )

    def test_approved_purpose_does_not_grant_action_authority(self):
        for record in self.records:
            purpose = record["approved_purpose_record"]
            downstream = record["downstream_boundary"]

            self.assertTrue(purpose["approved_purpose_created"])
            self.assertFalse(purpose["action_authority_granted"])
            self.assertTrue(downstream["may_enter_future_candidate_ordering_boundary"])
            self.assertFalse(downstream["candidate_ordering_authorized_in_this_package"])
            self.assertFalse(downstream["candidate_ordering_changed"])
            self.assertFalse(downstream["selected_action_created"])
            self.assertFalse(downstream["final_action_created"])
            self.assertFalse(downstream["direct_command_created"])

    def test_source_already_approved_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_proto_purpose_trace"]["source_approved_purpose_created"] = True

        result = validate_proto_purpose_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_approved_purpose_created_not_false", result["error_codes"])

    def test_unknown_proto_purpose_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_proto_purpose_trace"]["proto_purpose"] = "seek_reward_forever"

        result = validate_proto_purpose_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_proto_purpose_not_allowed", result["error_codes"])

    def test_bad_approval_scope_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["purpose_approval_decision"]["approval_scope"] = "unbounded_reward_scope"

        result = validate_proto_purpose_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("approval_scope_not_expected_for_proto_purpose", result["error_codes"])

    def test_approval_as_action_authority_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["purpose_approval_decision"]["approval_is_action_authority"] = True

        result = validate_proto_purpose_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("approval_is_action_authority_not_false", result["error_codes"])

    def test_purpose_action_authority_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["approved_purpose_record"]["action_authority_granted"] = True

        result = validate_proto_purpose_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("approved_purpose_action_authority_granted_not_false", result["error_codes"])

    def test_candidate_ordering_in_this_package_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["downstream_boundary"]["candidate_ordering_authorized_in_this_package"] = True

        result = validate_proto_purpose_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "downstream_boundary_candidate_ordering_authorized_in_this_package_not_expected",
            result["error_codes"],
        )

    def test_selected_action_created_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["downstream_boundary"]["selected_action_created"] = True

        result = validate_proto_purpose_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("downstream_boundary_selected_action_created_not_expected", result["error_codes"])

    def test_memory_write_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["blocked_flags"]["memory_write"] = True

        result = validate_proto_purpose_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_memory_write_not_false", result["error_codes"])

    def test_predictor_modified_blocks(self):
        bad = copy.deepcopy(self.mismatch)
        bad["blocked_flags"]["predictor_modified"] = True

        result = validate_proto_purpose_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_predictor_modified_not_false", result["error_codes"])

    def test_emotional_manipulation_blocks(self):
        bad = copy.deepcopy(self.comfort)
        bad["blocked_flags"]["emotional_manipulation"] = True

        result = validate_proto_purpose_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_emotional_manipulation_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["proto_purpose_approval_boundary_result_count"], 32)
        self.assertEqual(summary["valid_proto_purpose_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_proto_purpose_approval_boundary_count"], 29)
        self.assertEqual(summary["approved_purpose_created_count"], 3)
        self.assertEqual(summary["approach_or_reach_item_approved_count"], 1)
        self.assertEqual(summary["resolve_mismatch_approved_count"], 1)
        self.assertEqual(summary["support_user_comfort_approved_count"], 1)
        self.assertEqual(summary["may_enter_future_candidate_ordering_boundary_count"], 3)
        self.assertEqual(summary["candidate_ordering_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-proto-purpose-approval-boundary-minimal-check")

        self.assertEqual(result["command"], "run-proto-purpose-approval-boundary-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()

