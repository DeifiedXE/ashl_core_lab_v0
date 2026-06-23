import unittest
from copy import deepcopy

from ashl_core.sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal import (
    run_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal_check,
)
from ashl_core.sandbox_candidate_ordering_arbitration_direct_command_minimal import (
    build_sandbox_candidate_ordering_arbitration_direct_command_record,
    run_sandbox_candidate_ordering_arbitration_direct_command_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_direct_command_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationDirectCommandMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal_check()[
            "valid_records"
        ]
        cls.result = run_sandbox_candidate_ordering_arbitration_direct_command_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reachable = cls.records[0]
        cls.not_afforded = cls.records[1]
        cls.mismatch = cls.records[2]

    def assert_invalid(self, record: dict) -> None:
        result = validate_sandbox_candidate_ordering_arbitration_direct_command_record(record)
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])

    def test_valid_direct_command_records_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_direct_command_record(record)
            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(record["record_type"], "sandbox_candidate_ordering_arbitration_direct_command_minimal")
            self.assertTrue(record["sandbox_direct_command"]["direct_command_created"])

    def test_boundary_versions_are_b144_to_b145(self):
        boundary = self.result["boundary"]
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b144")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b145")

    def test_default_builder_uses_arbitration_direct_command_approval_boundary_source(self):
        record = build_sandbox_candidate_ordering_arbitration_direct_command_record()
        source = record["source_direct_command_approval_boundary"]
        command = record["sandbox_direct_command"]
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b144")
        self.assertEqual(command["direct_command"], source["candidate_for_future_direct_command"])

    def test_direct_commands_match_arbitration_final_actions(self):
        self.assertEqual(self.reachable["sandbox_direct_command"]["direct_command"], "sandbox.arbitration.reach_front_item")
        self.assertEqual(self.not_afforded["sandbox_direct_command"]["direct_command"], "sandbox.arbitration.wait_or_observe")
        self.assertEqual(
            self.mismatch["sandbox_direct_command"]["direct_command"],
            "sandbox.arbitration.observe_or_alternative_probe",
        )

    def test_direct_command_does_not_execute(self):
        for record in self.records:
            command = record["sandbox_direct_command"]
            self.assertTrue(command["direct_command_created"])
            self.assertEqual(command["direct_command_scope"], "sandbox_only")
            self.assertFalse(command["sandbox_action_executed"])
            self.assertFalse(command["execution_result_created"])
            self.assertFalse(command["execution_allowed_in_this_package"])
            self.assertTrue(command["future_execution_requires_separate_boundary"])

    def test_source_approval_boundary_is_preserved(self):
        source = self.reachable["source_direct_command_approval_boundary"]
        self.assertTrue(source["source_validated"])
        self.assertTrue(source["future_direct_command_allowed"])
        self.assertFalse(source["source_direct_command_created_in_source_package"])
        self.assertTrue(source["source_arbitration_rules_preserved"])
        self.assertEqual(source["candidate_for_future_direct_command"], "sandbox.arbitration.reach_front_item")

    def test_rollback_removes_direct_command_without_dirty_state(self):
        rollback = self.reachable["rollback_preview"]
        result = validate_sandbox_candidate_ordering_arbitration_direct_command_record(self.reachable)
        self.assertTrue(result["rollback_available"])
        self.assertTrue(rollback["rollback_available"])
        self.assertTrue(rollback["direct_command_removed_on_rollback"])
        self.assertFalse(rollback["dirty_state_after_rollback"])
        self.assertFalse(rollback["persistent_update_performed"])

    def test_bad_source_blocks(self):
        bad = deepcopy(self.reachable)
        bad["source_direct_command_approval_boundary"]["source_validated"] = False
        self.assert_invalid(bad)

    def test_direct_command_created_false_blocks(self):
        bad = deepcopy(self.reachable)
        bad["sandbox_direct_command"]["direct_command_created"] = False
        self.assert_invalid(bad)

    def test_wrong_direct_command_blocks(self):
        bad = deepcopy(self.reachable)
        bad["sandbox_direct_command"]["direct_command"] = "sandbox.arbitration.wait"
        self.assert_invalid(bad)

    def test_direct_command_scope_and_source_block(self):
        for field, value in (
            ("direct_command_scope", "production"),
            ("direct_command_source", "unapproved_boundary"),
            ("arbitration_rules_preserved", False),
        ):
            bad = deepcopy(self.reachable)
            bad["sandbox_direct_command"][field] = value
            self.assert_invalid(bad)

    def test_execution_blocks(self):
        for field in ("sandbox_action_executed", "execution_result_created", "execution_allowed_in_this_package"):
            bad = deepcopy(self.reachable)
            bad["sandbox_direct_command"][field] = True
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
        self.assertEqual(summary["direct_command_result_count"], 32)
        self.assertEqual(summary["valid_direct_command_count"], 3)
        self.assertEqual(summary["invalid_direct_command_count"], 29)
        self.assertEqual(summary["direct_command_created_count"], 3)
        self.assertEqual(summary["reach_front_item_direct_command_count"], 1)
        self.assertEqual(summary["wait_or_observe_direct_command_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_direct_command_count"], 1)
        self.assertEqual(summary["sandbox_only_direct_command_count"], 3)
        self.assertEqual(summary["arbitration_rules_preserved_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["rollback_available_count"], 3)

    def test_cli_command(self):
        result = run_command("run-sandbox-candidate-ordering-arbitration-direct-command-minimal-check")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["valid_direct_command_count"], 3)


if __name__ == "__main__":
    unittest.main()
