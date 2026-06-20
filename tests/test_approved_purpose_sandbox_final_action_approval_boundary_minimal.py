import copy
import unittest

from ashl_core.approved_purpose_sandbox_final_action_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_approved_purpose_sandbox_final_action_approval_boundary_record,
    run_approved_purpose_sandbox_final_action_approval_boundary_minimal_check,
    validate_approved_purpose_sandbox_final_action_approval_boundary_record,
)
from ashl_core.approved_purpose_sandbox_selected_action_minimal import (
    run_approved_purpose_sandbox_selected_action_minimal_check,
)
from ashl_core.teaching_cli import run_command


class ApprovedPurposeSandboxFinalActionApprovalBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_approved_purpose_sandbox_selected_action_minimal_check()["valid_records"]
        cls.result = run_approved_purpose_sandbox_final_action_approval_boundary_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.comfort = cls.records[2]

    def test_valid_final_action_approval_boundary_records_are_created(self):
        for record in self.records:
            result = validate_approved_purpose_sandbox_final_action_approval_boundary_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(
                record["record_type"],
                "approved_purpose_sandbox_final_action_approval_boundary_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_approach_or_reach_item_allows_future_reach_front_item_final_action(self):
        record = build_approved_purpose_sandbox_final_action_approval_boundary_record(self.sources[0])
        boundary = record["final_action_approval_boundary"]
        result = validate_approved_purpose_sandbox_final_action_approval_boundary_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "approach_or_reach_item")
        self.assertTrue(boundary["future_final_action_allowed"])
        self.assertEqual(boundary["candidate_for_future_final_action"], "reach_front_item")

    def test_resolve_mismatch_allows_future_probe_final_action(self):
        boundary = self.mismatch["final_action_approval_boundary"]
        result = validate_approved_purpose_sandbox_final_action_approval_boundary_record(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "resolve_mismatch")
        self.assertEqual(boundary["candidate_for_future_final_action"], "observe_or_alternative_probe")

    def test_support_user_comfort_allows_future_low_pressure_support_final_action(self):
        boundary = self.comfort["final_action_approval_boundary"]
        result = validate_approved_purpose_sandbox_final_action_approval_boundary_record(self.comfort)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "support_user_comfort")
        self.assertEqual(boundary["candidate_for_future_final_action"], "offer_low_pressure_support")

    def test_boundary_does_not_create_final_action_command_or_execution(self):
        for record in self.records:
            boundary = record["final_action_approval_boundary"]

            self.assertTrue(boundary["future_final_action_allowed"])
            self.assertFalse(boundary["final_action_created_in_this_package"])
            self.assertFalse(boundary["direct_command_created"])
            self.assertFalse(boundary["sandbox_action_executed"])
            self.assertFalse(boundary["execution_allowed_in_this_package"])
            self.assertTrue(boundary["future_direct_command_requires_separate_boundary"])
            self.assertTrue(boundary["future_execution_requires_separate_boundary"])

    def test_source_selected_action_required(self):
        source = self.reward["source_sandbox_selected_action"]

        self.assertTrue(source["source_validated"])
        self.assertTrue(source["selected_action_created"])
        self.assertEqual(source["selected_action_scope"], "sandbox_only")
        self.assertEqual(source["selected_action"], "reach_front_item")

    def test_source_selected_action_not_created_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_sandbox_selected_action"]["selected_action_created"] = False

        result = validate_approved_purpose_sandbox_final_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_selected_action_created_not_true", result["error_codes"])

    def test_future_final_action_not_allowed_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["final_action_approval_boundary"]["future_final_action_allowed"] = False

        result = validate_approved_purpose_sandbox_final_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("final_action_approval_boundary_future_final_action_allowed_not_expected", result["error_codes"])

    def test_wrong_future_candidate_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["final_action_approval_boundary"]["candidate_for_future_final_action"] = "wait_or_observe"

        result = validate_approved_purpose_sandbox_final_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "final_action_approval_boundary_candidate_for_future_final_action_not_expected",
            result["error_codes"],
        )

    def test_final_action_created_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["final_action_approval_boundary"]["final_action_created_in_this_package"] = True

        result = validate_approved_purpose_sandbox_final_action_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "final_action_approval_boundary_final_action_created_in_this_package_not_expected",
            result["error_codes"],
        )

    def test_direct_command_and_execution_block(self):
        for field, error in (
            ("direct_command_created", "final_action_approval_boundary_direct_command_created_not_expected"),
            ("sandbox_action_executed", "final_action_approval_boundary_sandbox_action_executed_not_expected"),
            ("execution_allowed_in_this_package", "final_action_approval_boundary_execution_allowed_in_this_package_not_expected"),
        ):
            bad = copy.deepcopy(self.reward)
            bad["final_action_approval_boundary"][field] = True

            result = validate_approved_purpose_sandbox_final_action_approval_boundary_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(error, result["error_codes"])

    def test_memory_predictor_manipulation_and_proof_flags_block(self):
        for field in (
            "memory_write",
            "predictor_modified",
            "emotional_manipulation",
            "proof_of_learning_claim",
        ):
            bad = copy.deepcopy(self.comfort)
            bad["blocked_flags"][field] = True

            result = validate_approved_purpose_sandbox_final_action_approval_boundary_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["final_action_approval_boundary_result_count"], 30)
        self.assertEqual(summary["valid_final_action_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_final_action_approval_boundary_count"], 27)
        self.assertEqual(summary["future_final_action_allowed_count"], 3)
        self.assertEqual(summary["approach_or_reach_item_boundary_count"], 1)
        self.assertEqual(summary["resolve_mismatch_boundary_count"], 1)
        self.assertEqual(summary["support_user_comfort_boundary_count"], 1)
        self.assertEqual(summary["final_action_creation_blocked_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-approved-purpose-sandbox-final-action-approval-boundary-minimal-check")

        self.assertEqual(
            result["command"],
            "run-approved-purpose-sandbox-final-action-approval-boundary-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
