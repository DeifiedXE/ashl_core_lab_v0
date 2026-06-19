import copy
import unittest

from ashl_core.approved_purpose_candidate_ordering_minimal import (
    run_approved_purpose_candidate_ordering_minimal_check,
)
from ashl_core.approved_purpose_to_sandbox_selected_action_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_approved_purpose_to_sandbox_selected_action_approval_boundary_record,
    run_approved_purpose_to_sandbox_selected_action_approval_boundary_minimal_check,
    validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record,
)
from ashl_core.teaching_cli import run_command


class ApprovedPurposeToSandboxSelectedActionApprovalBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_approved_purpose_candidate_ordering_minimal_check()["valid_records"]
        cls.result = run_approved_purpose_to_sandbox_selected_action_approval_boundary_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.comfort = cls.records[2]

    def test_valid_selected_action_approval_boundary_records_are_created(self):
        for record in self.records:
            result = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(
                record["record_type"],
                "approved_purpose_to_sandbox_selected_action_approval_boundary_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_approach_or_reach_item_allows_future_reach_front_item_selected_action(self):
        record = build_approved_purpose_to_sandbox_selected_action_approval_boundary_record(self.sources[0])
        boundary = record["selected_action_approval_boundary"]
        result = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "approach_or_reach_item")
        self.assertTrue(boundary["future_selected_action_allowed"])
        self.assertEqual(boundary["candidate_for_future_selected_action"], "reach_front_item")

    def test_resolve_mismatch_allows_future_probe_selected_action(self):
        boundary = self.mismatch["selected_action_approval_boundary"]
        result = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "resolve_mismatch")
        self.assertEqual(boundary["candidate_for_future_selected_action"], "observe_or_alternative_probe")

    def test_support_user_comfort_allows_future_low_pressure_support_selected_action(self):
        boundary = self.comfort["selected_action_approval_boundary"]
        result = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(self.comfort)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "support_user_comfort")
        self.assertEqual(boundary["candidate_for_future_selected_action"], "offer_low_pressure_support")

    def test_boundary_does_not_create_selected_action_or_execute(self):
        for record in self.records:
            boundary = record["selected_action_approval_boundary"]

            self.assertTrue(boundary["future_selected_action_allowed"])
            self.assertFalse(boundary["selected_action_created_in_this_package"])
            self.assertFalse(boundary["final_action_created"])
            self.assertFalse(boundary["direct_command_created"])
            self.assertFalse(boundary["sandbox_action_executed"])
            self.assertFalse(boundary["execution_allowed_in_this_package"])

    def test_source_ordering_not_applied_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_approved_purpose_ordering"]["candidate_ordering_applied"] = False

        result = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_candidate_ordering_applied_not_true", result["error_codes"])

    def test_future_selected_action_not_allowed_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["selected_action_approval_boundary"]["future_selected_action_allowed"] = False

        result = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("selected_action_approval_boundary_future_selected_action_allowed_not_expected", result["error_codes"])

    def test_wrong_future_candidate_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["selected_action_approval_boundary"]["candidate_for_future_selected_action"] = "wait_or_observe"

        result = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "selected_action_approval_boundary_candidate_for_future_selected_action_not_expected",
            result["error_codes"],
        )

    def test_selected_action_created_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["selected_action_approval_boundary"]["selected_action_created_in_this_package"] = True

        result = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "selected_action_approval_boundary_selected_action_created_in_this_package_not_expected",
            result["error_codes"],
        )

    def test_final_action_created_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["selected_action_approval_boundary"]["final_action_created"] = True

        result = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("selected_action_approval_boundary_final_action_created_not_expected", result["error_codes"])

    def test_execution_allowed_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["selected_action_approval_boundary"]["execution_allowed_in_this_package"] = True

        result = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "selected_action_approval_boundary_execution_allowed_in_this_package_not_expected",
            result["error_codes"],
        )

    def test_memory_write_blocks(self):
        bad = copy.deepcopy(self.mismatch)
        bad["blocked_flags"]["memory_write"] = True

        result = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_memory_write_not_false", result["error_codes"])

    def test_predictor_modified_blocks(self):
        bad = copy.deepcopy(self.mismatch)
        bad["blocked_flags"]["predictor_modified"] = True

        result = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_predictor_modified_not_false", result["error_codes"])

    def test_emotional_manipulation_blocks(self):
        bad = copy.deepcopy(self.comfort)
        bad["blocked_flags"]["emotional_manipulation"] = True

        result = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_emotional_manipulation_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["selected_action_approval_boundary_result_count"], 28)
        self.assertEqual(summary["valid_selected_action_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_selected_action_approval_boundary_count"], 25)
        self.assertEqual(summary["future_selected_action_allowed_count"], 3)
        self.assertEqual(summary["approach_or_reach_item_boundary_count"], 1)
        self.assertEqual(summary["resolve_mismatch_boundary_count"], 1)
        self.assertEqual(summary["support_user_comfort_boundary_count"], 1)
        self.assertEqual(summary["selected_action_creation_blocked_count"], 3)
        self.assertEqual(summary["final_action_blocked_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-approved-purpose-to-sandbox-selected-action-approval-boundary-minimal-check")

        self.assertEqual(
            result["command"],
            "run-approved-purpose-to-sandbox-selected-action-approval-boundary-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
