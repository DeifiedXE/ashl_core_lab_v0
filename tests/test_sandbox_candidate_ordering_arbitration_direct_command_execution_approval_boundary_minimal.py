import unittest
from copy import deepcopy

from ashl_core.sandbox_candidate_ordering_arbitration_direct_command_execution_approval_boundary_minimal import (
    build_sandbox_candidate_ordering_arbitration_direct_command_execution_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_direct_command_execution_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_direct_command_execution_approval_boundary_record,
)
from ashl_core.sandbox_candidate_ordering_arbitration_direct_command_minimal import (
    run_sandbox_candidate_ordering_arbitration_direct_command_minimal_check,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationDirectCommandExecutionApprovalBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_direct_command_minimal_check()["valid_records"]
        cls.result = run_sandbox_candidate_ordering_arbitration_direct_command_execution_approval_boundary_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reachable = cls.records[0]
        cls.not_afforded = cls.records[1]
        cls.mismatch = cls.records[2]

    def assert_invalid(self, record: dict) -> None:
        result = validate_sandbox_candidate_ordering_arbitration_direct_command_execution_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])

    def test_valid_execution_approval_boundaries_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_direct_command_execution_approval_boundary_record(record)
            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_direct_command_execution_approval_boundary_minimal",
            )
            self.assertTrue(record["execution_approval_boundary"]["future_execution_allowed"])

    def test_boundary_versions_are_b145_to_b146(self):
        boundary = self.result["boundary"]
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b145")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b146")

    def test_default_builder_uses_arbitration_direct_command_source(self):
        record = build_sandbox_candidate_ordering_arbitration_direct_command_execution_approval_boundary_record()
        source = record["source_sandbox_direct_command"]
        boundary = record["execution_approval_boundary"]
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b145")
        self.assertEqual(boundary["candidate_for_future_execution"], source["direct_command"])

    def test_direct_commands_can_enter_future_execution(self):
        self.assertEqual(
            self.reachable["execution_approval_boundary"]["candidate_for_future_execution"],
            "sandbox.arbitration.reach_front_item",
        )
        self.assertEqual(
            self.not_afforded["execution_approval_boundary"]["candidate_for_future_execution"],
            "sandbox.arbitration.wait_or_observe",
        )
        self.assertEqual(
            self.mismatch["execution_approval_boundary"]["candidate_for_future_execution"],
            "sandbox.arbitration.observe_or_alternative_probe",
        )

    def test_boundary_does_not_execute_or_create_result(self):
        for record in self.records:
            boundary = record["execution_approval_boundary"]
            self.assertTrue(boundary["future_execution_allowed"])
            self.assertEqual(boundary["execution_scope"], "sandbox_only")
            self.assertFalse(boundary["sandbox_action_executed_in_this_package"])
            self.assertFalse(boundary["execution_result_created_in_this_package"])
            self.assertTrue(boundary["future_outcome_observation_requires_separate_boundary"])

    def test_source_direct_command_is_preserved(self):
        source = self.reachable["source_sandbox_direct_command"]
        self.assertTrue(source["source_validated"])
        self.assertTrue(source["direct_command_created"])
        self.assertEqual(source["direct_command_scope"], "sandbox_only")
        self.assertEqual(
            source["direct_command_source"],
            "sandbox_candidate_ordering_arbitration_direct_command_approval_boundary",
        )
        self.assertTrue(source["source_arbitration_rules_preserved"])
        self.assertFalse(source["source_sandbox_action_executed"])
        self.assertFalse(source["source_execution_result_created"])

    def test_bad_source_blocks(self):
        bad = deepcopy(self.reachable)
        bad["source_sandbox_direct_command"]["source_validated"] = False
        self.assert_invalid(bad)

    def test_source_direct_command_created_false_blocks(self):
        bad = deepcopy(self.reachable)
        bad["source_sandbox_direct_command"]["direct_command_created"] = False
        self.assert_invalid(bad)

    def test_source_execution_state_blocks(self):
        for field in ("source_sandbox_action_executed", "source_execution_result_created"):
            bad = deepcopy(self.reachable)
            bad["source_sandbox_direct_command"][field] = True
            self.assert_invalid(bad)

    def test_wrong_future_execution_blocks(self):
        bad = deepcopy(self.reachable)
        bad["execution_approval_boundary"]["candidate_for_future_execution"] = "sandbox.arbitration.wait"
        self.assert_invalid(bad)

    def test_future_execution_not_allowed_blocks(self):
        bad = deepcopy(self.reachable)
        bad["execution_approval_boundary"]["future_execution_allowed"] = False
        self.assert_invalid(bad)

    def test_execution_or_result_created_blocks(self):
        for field in ("sandbox_action_executed_in_this_package", "execution_result_created_in_this_package"):
            bad = deepcopy(self.reachable)
            bad["execution_approval_boundary"][field] = True
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
        self.assertEqual(summary["execution_approval_boundary_result_count"], 30)
        self.assertEqual(summary["valid_execution_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_execution_approval_boundary_count"], 27)
        self.assertEqual(summary["future_execution_allowed_count"], 3)
        self.assertEqual(summary["reach_front_item_execution_candidate_count"], 1)
        self.assertEqual(summary["wait_or_observe_execution_candidate_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_execution_candidate_count"], 1)
        self.assertEqual(summary["arbitration_rules_preserved_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-direct-command-execution-approval-boundary-minimal-check"
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["valid_execution_approval_boundary_count"], 3)


if __name__ == "__main__":
    unittest.main()
