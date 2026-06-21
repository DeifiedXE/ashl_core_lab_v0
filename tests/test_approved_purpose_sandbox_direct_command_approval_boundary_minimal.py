import copy
import unittest

from ashl_core.approved_purpose_sandbox_direct_command_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_approved_purpose_sandbox_direct_command_approval_boundary_record,
    run_approved_purpose_sandbox_direct_command_approval_boundary_minimal_check,
    validate_approved_purpose_sandbox_direct_command_approval_boundary_record,
)
from ashl_core.approved_purpose_sandbox_final_action_minimal import (
    run_approved_purpose_sandbox_final_action_minimal_check,
)
from ashl_core.teaching_cli import run_command


class ApprovedPurposeSandboxDirectCommandApprovalBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_approved_purpose_sandbox_final_action_minimal_check()["valid_records"]
        cls.result = run_approved_purpose_sandbox_direct_command_approval_boundary_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.comfort = cls.records[2]

    def test_valid_direct_command_approval_boundaries_are_created(self):
        for record in self.records:
            result = validate_approved_purpose_sandbox_direct_command_approval_boundary_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(
                record["record_type"],
                "approved_purpose_sandbox_direct_command_approval_boundary_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["direct_command_approval_boundary"]["future_direct_command_allowed"])

    def test_approach_or_reach_item_opens_reach_front_command_candidate(self):
        record = build_approved_purpose_sandbox_direct_command_approval_boundary_record(self.sources[0])
        boundary = record["direct_command_approval_boundary"]
        result = validate_approved_purpose_sandbox_direct_command_approval_boundary_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "approach_or_reach_item")
        self.assertEqual(boundary["candidate_for_future_direct_command"], "sandbox.approved_purpose.reach_front_item")
        self.assertEqual(boundary["direct_command_scope"], "sandbox_only")

    def test_resolve_mismatch_opens_probe_command_candidate(self):
        boundary = self.mismatch["direct_command_approval_boundary"]
        result = validate_approved_purpose_sandbox_direct_command_approval_boundary_record(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "resolve_mismatch")
        self.assertEqual(
            boundary["candidate_for_future_direct_command"],
            "sandbox.approved_purpose.observe_or_alternative_probe",
        )

    def test_support_user_comfort_opens_low_pressure_support_command_candidate(self):
        boundary = self.comfort["direct_command_approval_boundary"]
        result = validate_approved_purpose_sandbox_direct_command_approval_boundary_record(self.comfort)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "support_user_comfort")
        self.assertEqual(
            boundary["candidate_for_future_direct_command"],
            "sandbox.approved_purpose.offer_low_pressure_support",
        )

    def test_boundary_does_not_create_command_or_execute(self):
        for record in self.records:
            boundary = record["direct_command_approval_boundary"]

            self.assertTrue(boundary["future_direct_command_allowed"])
            self.assertFalse(boundary["direct_command_created_in_this_package"])
            self.assertFalse(boundary["sandbox_action_executed"])
            self.assertFalse(boundary["execution_allowed_in_this_package"])
            self.assertTrue(boundary["future_execution_requires_separate_boundary"])

    def test_source_final_action_is_preserved(self):
        source = self.reward["source_sandbox_final_action"]

        self.assertTrue(source["source_validated"])
        self.assertTrue(source["final_action_created"])
        self.assertEqual(source["final_action"], "reach_front_item")
        self.assertFalse(source["source_direct_command_created"])
        self.assertTrue(source["source_future_direct_command_requires_separate_boundary"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_sandbox_final_action"]["source_validated"] = False

        result = validate_approved_purpose_sandbox_direct_command_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_source_final_action_created_false_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_sandbox_final_action"]["final_action_created"] = False

        result = validate_approved_purpose_sandbox_direct_command_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_final_action_created_not_true", result["error_codes"])

    def test_wrong_direct_command_candidate_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["direct_command_approval_boundary"]["candidate_for_future_direct_command"] = (
            "sandbox.approved_purpose.wait"
        )

        result = validate_approved_purpose_sandbox_direct_command_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "direct_command_approval_boundary_candidate_for_future_direct_command_not_expected",
            result["error_codes"],
        )

    def test_direct_command_and_execution_block(self):
        for field, error in (
            (
                "direct_command_created_in_this_package",
                "direct_command_approval_boundary_direct_command_created_in_this_package_not_expected",
            ),
            ("sandbox_action_executed", "direct_command_approval_boundary_sandbox_action_executed_not_expected"),
            (
                "execution_allowed_in_this_package",
                "direct_command_approval_boundary_execution_allowed_in_this_package_not_expected",
            ),
        ):
            bad = copy.deepcopy(self.reward)
            bad["direct_command_approval_boundary"][field] = True

            result = validate_approved_purpose_sandbox_direct_command_approval_boundary_record(bad)

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

            result = validate_approved_purpose_sandbox_direct_command_approval_boundary_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["direct_command_approval_boundary_result_count"], 29)
        self.assertEqual(summary["valid_direct_command_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_direct_command_approval_boundary_count"], 26)
        self.assertEqual(summary["future_direct_command_allowed_count"], 3)
        self.assertEqual(summary["approach_or_reach_item_boundary_count"], 1)
        self.assertEqual(summary["resolve_mismatch_boundary_count"], 1)
        self.assertEqual(summary["support_user_comfort_boundary_count"], 1)
        self.assertEqual(summary["direct_command_creation_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-approved-purpose-sandbox-direct-command-approval-boundary-minimal-check")

        self.assertEqual(
            result["command"],
            "run-approved-purpose-sandbox-direct-command-approval-boundary-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
