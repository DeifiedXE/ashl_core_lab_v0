import unittest
from copy import deepcopy

from ashl_core.sandbox_candidate_ordering_arbitration_selected_action_minimal import (
    build_sandbox_candidate_ordering_arbitration_selected_action_record,
    run_sandbox_candidate_ordering_arbitration_selected_action_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_selected_action_record,
)
from ashl_core.sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_minimal import (
    run_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_minimal_check,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationSelectedActionMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_minimal_check()[
            "valid_records"
        ]
        cls.result = run_sandbox_candidate_ordering_arbitration_selected_action_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reachable = cls.records[0]
        cls.not_afforded = cls.records[1]
        cls.mismatch = cls.records[2]

    def assert_invalid(self, record: dict) -> None:
        result = validate_sandbox_candidate_ordering_arbitration_selected_action_record(record)
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])

    def test_valid_selected_action_records_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_selected_action_record(record)
            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(record["record_type"], "sandbox_candidate_ordering_arbitration_selected_action_minimal")

    def test_boundary_versions_are_b140_to_b141(self):
        boundary = self.result["boundary"]
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b140")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b141")

    def test_default_builder_uses_selected_action_approval_boundary_source(self):
        record = build_sandbox_candidate_ordering_arbitration_selected_action_record()
        source = record["source_selected_action_approval_boundary"]
        selected = record["sandbox_selected_action"]
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b140")
        self.assertEqual(selected["selected_action"], source["candidate_for_future_selected_action"])

    def test_selected_actions_match_arbitration_checked_sources(self):
        self.assertEqual(self.reachable["sandbox_selected_action"]["selected_action"], "reach_front_item")
        self.assertEqual(self.not_afforded["sandbox_selected_action"]["selected_action"], "wait_or_observe")
        self.assertEqual(
            self.mismatch["sandbox_selected_action"]["selected_action"],
            "observe_or_alternative_probe",
        )

    def test_source_approval_boundary_is_preserved(self):
        for record in self.records:
            source = record["source_selected_action_approval_boundary"]
            selected = record["sandbox_selected_action"]
            self.assertTrue(source["future_selected_action_allowed"])
            self.assertEqual(source["selected_action_scope"], "sandbox_only")
            self.assertEqual(selected["selected_action"], source["candidate_for_future_selected_action"])

    def test_arbitration_rules_are_preserved(self):
        for record in self.records:
            source = record["source_selected_action_approval_boundary"]
            selected = record["sandbox_selected_action"]
            self.assertTrue(source["arbitration_rules_preserved"])
            self.assertTrue(selected["arbitration_rules_preserved"])

    def test_final_direct_and_execution_remain_blocked(self):
        selected = self.reachable["sandbox_selected_action"]
        self.assertTrue(selected["selected_action_created"])
        self.assertFalse(selected["final_action_created"])
        self.assertFalse(selected["direct_command_created"])
        self.assertFalse(selected["sandbox_execution_created"])
        self.assertFalse(selected["execution_allowed_in_this_package"])

    def test_rollback_removes_selected_action_cleanly(self):
        rollback = self.reachable["rollback_preview"]
        self.assertTrue(rollback["rollback_available"])
        self.assertTrue(rollback["selected_action_removed_on_rollback"])
        self.assertFalse(rollback["dirty_state_after_rollback"])
        self.assertFalse(rollback["persistent_update_performed"])

    def test_bad_source_blocks(self):
        bad = deepcopy(self.reachable)
        bad["source_selected_action_approval_boundary"]["source_validated"] = False
        self.assert_invalid(bad)

    def test_wrong_selected_action_blocks(self):
        bad = deepcopy(self.reachable)
        bad["sandbox_selected_action"]["selected_action"] = "wait_or_observe"
        self.assert_invalid(bad)

    def test_selected_action_created_false_blocks(self):
        bad = deepcopy(self.reachable)
        bad["sandbox_selected_action"]["selected_action_created"] = False
        self.assert_invalid(bad)

    def test_final_action_true_blocks(self):
        bad = deepcopy(self.reachable)
        bad["sandbox_selected_action"]["final_action_created"] = True
        self.assert_invalid(bad)

    def test_direct_command_true_blocks(self):
        bad = deepcopy(self.reachable)
        bad["sandbox_selected_action"]["direct_command_created"] = True
        self.assert_invalid(bad)

    def test_execution_true_blocks(self):
        bad = deepcopy(self.reachable)
        bad["sandbox_selected_action"]["sandbox_execution_created"] = True
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
            bad = deepcopy(self.reachable)
            bad["blocked_flags"][flag] = True
            self.assert_invalid(bad)

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]
        self.assertEqual(summary["selected_action_result_count"], 31)
        self.assertEqual(summary["valid_selected_action_count"], 3)
        self.assertEqual(summary["invalid_selected_action_count"], 28)
        self.assertEqual(summary["selected_action_created_count"], 3)
        self.assertEqual(summary["sandbox_only_selected_action_count"], 3)
        self.assertEqual(summary["arbitration_rules_preserved_count"], 3)
        self.assertEqual(summary["reach_front_item_selected_count"], 1)
        self.assertEqual(summary["wait_or_observe_selected_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_selected_count"], 1)
        self.assertEqual(summary["final_action_blocked_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["rollback_available_count"], 3)

    def test_cli_command(self):
        result = run_command("run-sandbox-candidate-ordering-arbitration-selected-action-minimal-check")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["valid_selected_action_count"], 3)


if __name__ == "__main__":
    unittest.main()
