import unittest
from copy import deepcopy

from ashl_core.sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal import (
    build_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_record,
)
from ashl_core.sandbox_candidate_ordering_arbitration_final_action_minimal import (
    run_sandbox_candidate_ordering_arbitration_final_action_minimal_check,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationDirectCommandApprovalBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_final_action_minimal_check()["valid_records"]
        cls.result = run_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reachable = cls.records[0]
        cls.not_afforded = cls.records[1]
        cls.mismatch = cls.records[2]

    def assert_invalid(self, record: dict) -> None:
        result = validate_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])

    def test_valid_direct_command_approval_boundaries_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_record(record)
            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal",
            )

    def test_boundary_versions_are_b143_to_b144(self):
        boundary = self.result["boundary"]
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b143")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b144")

    def test_default_builder_uses_arbitration_final_action_source(self):
        record = build_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_record()
        source = record["source_sandbox_final_action"]
        boundary = record["direct_command_approval_boundary"]
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b143")
        self.assertEqual(boundary["candidate_for_future_direct_command"], f"sandbox.arbitration.{source['final_action']}")

    def test_future_direct_commands_match_final_actions(self):
        self.assertEqual(
            self.reachable["direct_command_approval_boundary"]["candidate_for_future_direct_command"],
            "sandbox.arbitration.reach_front_item",
        )
        self.assertEqual(
            self.not_afforded["direct_command_approval_boundary"]["candidate_for_future_direct_command"],
            "sandbox.arbitration.wait_or_observe",
        )
        self.assertEqual(
            self.mismatch["direct_command_approval_boundary"]["candidate_for_future_direct_command"],
            "sandbox.arbitration.observe_or_alternative_probe",
        )

    def test_boundary_does_not_create_command_or_execute(self):
        for record in self.records:
            boundary = record["direct_command_approval_boundary"]
            self.assertTrue(boundary["future_direct_command_allowed"])
            self.assertFalse(boundary["direct_command_created_in_this_package"])
            self.assertFalse(boundary["sandbox_execution_created"])
            self.assertFalse(boundary["execution_allowed_in_this_package"])
            self.assertTrue(boundary["future_execution_requires_separate_boundary"])

    def test_source_final_action_required(self):
        source = self.reachable["source_sandbox_final_action"]
        self.assertTrue(source["source_validated"])
        self.assertTrue(source["final_action_created"])
        self.assertEqual(source["final_action_scope"], "sandbox_only")
        self.assertEqual(source["final_action_source"], "sandbox_candidate_ordering_arbitration_final_action_approval_boundary")
        self.assertTrue(source["source_arbitration_rules_preserved"])

    def test_source_final_action_not_created_blocks(self):
        bad = deepcopy(self.reachable)
        bad["source_sandbox_final_action"]["final_action_created"] = False
        self.assert_invalid(bad)

    def test_wrong_future_command_blocks(self):
        bad = deepcopy(self.reachable)
        bad["direct_command_approval_boundary"]["candidate_for_future_direct_command"] = "sandbox.arbitration.wait"
        self.assert_invalid(bad)

    def test_future_direct_command_not_allowed_blocks(self):
        bad = deepcopy(self.reachable)
        bad["direct_command_approval_boundary"]["future_direct_command_allowed"] = False
        self.assert_invalid(bad)

    def test_direct_command_created_blocks(self):
        bad = deepcopy(self.reachable)
        bad["direct_command_approval_boundary"]["direct_command_created_in_this_package"] = True
        self.assert_invalid(bad)

    def test_execution_blocks(self):
        for field in ("sandbox_execution_created", "execution_allowed_in_this_package"):
            bad = deepcopy(self.reachable)
            bad["direct_command_approval_boundary"][field] = True
            self.assert_invalid(bad)

    def test_memory_predictor_direct_feed_and_proof_flags_block(self):
        for flag in (
            "memory_write",
            "retention_write",
            "predictor_read_enabled",
            "predictor_influence_enabled",
            "direct_tendency_feed",
            "proof_of_learning_claim",
        ):
            bad = deepcopy(self.mismatch)
            bad["blocked_flags"][flag] = True
            self.assert_invalid(bad)

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]
        self.assertEqual(summary["direct_command_approval_boundary_result_count"], 28)
        self.assertEqual(summary["valid_direct_command_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_direct_command_approval_boundary_count"], 25)
        self.assertEqual(summary["future_direct_command_allowed_count"], 3)
        self.assertEqual(summary["reach_front_item_direct_command_candidate_count"], 1)
        self.assertEqual(summary["wait_or_observe_direct_command_candidate_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_direct_command_candidate_count"], 1)
        self.assertEqual(summary["direct_command_creation_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-direct-command-approval-boundary-minimal-check"
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["valid_direct_command_approval_boundary_count"], 3)


if __name__ == "__main__":
    unittest.main()
