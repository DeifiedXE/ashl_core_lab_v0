import copy
import unittest

from ashl_core.approved_purpose_sandbox_direct_command_execution_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_approved_purpose_sandbox_direct_command_execution_approval_boundary_record,
    run_approved_purpose_sandbox_direct_command_execution_approval_boundary_minimal_check,
    validate_approved_purpose_sandbox_direct_command_execution_approval_boundary_record,
)
from ashl_core.approved_purpose_sandbox_direct_command_minimal import (
    run_approved_purpose_sandbox_direct_command_minimal_check,
)
from ashl_core.teaching_cli import run_command


class ApprovedPurposeSandboxDirectCommandExecutionApprovalBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_approved_purpose_sandbox_direct_command_minimal_check()["valid_records"]
        cls.result = run_approved_purpose_sandbox_direct_command_execution_approval_boundary_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.comfort = cls.records[2]

    def test_valid_execution_approval_boundaries_are_created(self):
        for record in self.records:
            result = validate_approved_purpose_sandbox_direct_command_execution_approval_boundary_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(
                record["record_type"],
                "approved_purpose_sandbox_direct_command_execution_approval_boundary_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["execution_approval_boundary"]["future_execution_allowed"])

    def test_reach_front_command_can_enter_future_execution(self):
        record = build_approved_purpose_sandbox_direct_command_execution_approval_boundary_record(self.sources[0])
        boundary = record["execution_approval_boundary"]
        result = validate_approved_purpose_sandbox_direct_command_execution_approval_boundary_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "approach_or_reach_item")
        self.assertEqual(boundary["candidate_for_future_execution"], "sandbox.approved_purpose.reach_front_item")
        self.assertEqual(boundary["execution_scope"], "sandbox_only")

    def test_probe_command_can_enter_future_execution(self):
        boundary = self.mismatch["execution_approval_boundary"]
        result = validate_approved_purpose_sandbox_direct_command_execution_approval_boundary_record(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "resolve_mismatch")
        self.assertEqual(boundary["candidate_for_future_execution"], "sandbox.approved_purpose.observe_or_alternative_probe")

    def test_support_command_can_enter_future_execution(self):
        boundary = self.comfort["execution_approval_boundary"]
        result = validate_approved_purpose_sandbox_direct_command_execution_approval_boundary_record(self.comfort)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "support_user_comfort")
        self.assertEqual(boundary["candidate_for_future_execution"], "sandbox.approved_purpose.offer_low_pressure_support")

    def test_boundary_does_not_execute_or_create_result(self):
        for record in self.records:
            boundary = record["execution_approval_boundary"]

            self.assertTrue(boundary["future_execution_allowed"])
            self.assertFalse(boundary["sandbox_action_executed_in_this_package"])
            self.assertFalse(boundary["execution_result_created_in_this_package"])
            self.assertTrue(boundary["future_outcome_observation_requires_separate_boundary"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_sandbox_direct_command"]["source_validated"] = False

        result = validate_approved_purpose_sandbox_direct_command_execution_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_source_direct_command_created_false_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_sandbox_direct_command"]["direct_command_created"] = False

        result = validate_approved_purpose_sandbox_direct_command_execution_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_direct_command_created_not_true", result["error_codes"])

    def test_execution_or_result_created_blocks(self):
        for field, error in (
            (
                "sandbox_action_executed_in_this_package",
                "execution_approval_boundary_sandbox_action_executed_in_this_package_not_expected",
            ),
            (
                "execution_result_created_in_this_package",
                "execution_approval_boundary_execution_result_created_in_this_package_not_expected",
            ),
        ):
            bad = copy.deepcopy(self.reward)
            bad["execution_approval_boundary"][field] = True

            result = validate_approved_purpose_sandbox_direct_command_execution_approval_boundary_record(bad)

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

            result = validate_approved_purpose_sandbox_direct_command_execution_approval_boundary_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["execution_approval_boundary_result_count"], 26)
        self.assertEqual(summary["valid_execution_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_execution_approval_boundary_count"], 23)
        self.assertEqual(summary["future_execution_allowed_count"], 3)
        self.assertEqual(summary["approach_or_reach_item_boundary_count"], 1)
        self.assertEqual(summary["resolve_mismatch_boundary_count"], 1)
        self.assertEqual(summary["support_user_comfort_boundary_count"], 1)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-approved-purpose-sandbox-direct-command-execution-approval-boundary-minimal-check")

        self.assertEqual(
            result["command"],
            "run-approved-purpose-sandbox-direct-command-execution-approval-boundary-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
