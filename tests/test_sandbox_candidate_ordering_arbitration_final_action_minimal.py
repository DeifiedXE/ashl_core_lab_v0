import unittest
from copy import deepcopy

from ashl_core.sandbox_candidate_ordering_arbitration_final_action_approval_boundary_minimal import (
    run_sandbox_candidate_ordering_arbitration_final_action_approval_boundary_minimal_check,
)
from ashl_core.sandbox_candidate_ordering_arbitration_final_action_minimal import (
    build_sandbox_candidate_ordering_arbitration_final_action_record,
    run_sandbox_candidate_ordering_arbitration_final_action_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_final_action_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationFinalActionMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_final_action_approval_boundary_minimal_check()[
            "valid_records"
        ]
        cls.result = run_sandbox_candidate_ordering_arbitration_final_action_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reachable = cls.records[0]
        cls.not_afforded = cls.records[1]
        cls.mismatch = cls.records[2]

    def assert_invalid(self, record: dict) -> None:
        result = validate_sandbox_candidate_ordering_arbitration_final_action_record(record)
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])

    def test_valid_final_action_records_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_final_action_record(record)
            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(record["record_type"], "sandbox_candidate_ordering_arbitration_final_action_minimal")
            self.assertTrue(record["sandbox_final_action"]["final_action_created"])

    def test_boundary_versions_are_b142_to_b143(self):
        boundary = self.result["boundary"]
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b142")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b143")

    def test_default_builder_uses_final_action_approval_boundary_source(self):
        record = build_sandbox_candidate_ordering_arbitration_final_action_record()
        source = record["source_final_action_approval_boundary"]
        final = record["sandbox_final_action"]
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b142")
        self.assertEqual(final["final_action"], source["candidate_for_future_final_action"])

    def test_final_actions_match_arbitration_selected_actions(self):
        self.assertEqual(self.reachable["sandbox_final_action"]["final_action"], "reach_front_item")
        self.assertEqual(self.not_afforded["sandbox_final_action"]["final_action"], "wait_or_observe")
        self.assertEqual(self.mismatch["sandbox_final_action"]["final_action"], "observe_or_alternative_probe")

    def test_final_action_does_not_command_or_execute(self):
        for record in self.records:
            final = record["sandbox_final_action"]
            self.assertTrue(final["final_action_created"])
            self.assertEqual(final["final_action_scope"], "sandbox_only")
            self.assertFalse(final["direct_command_created"])
            self.assertFalse(final["sandbox_execution_created"])
            self.assertFalse(final["execution_allowed_in_this_package"])
            self.assertTrue(final["future_direct_command_requires_separate_boundary"])
            self.assertTrue(final["future_execution_requires_separate_boundary"])

    def test_source_approval_boundary_is_preserved(self):
        source = self.reachable["source_final_action_approval_boundary"]
        self.assertTrue(source["source_validated"])
        self.assertTrue(source["future_final_action_allowed"])
        self.assertFalse(source["source_final_action_created_in_source_package"])
        self.assertTrue(source["source_arbitration_rules_preserved"])
        self.assertEqual(source["candidate_for_future_final_action"], "reach_front_item")

    def test_rollback_removes_final_action_without_dirty_state(self):
        rollback = self.reachable["rollback_preview"]
        result = validate_sandbox_candidate_ordering_arbitration_final_action_record(self.reachable)
        self.assertTrue(result["rollback_available"])
        self.assertTrue(rollback["rollback_available"])
        self.assertTrue(rollback["final_action_removed_on_rollback"])
        self.assertFalse(rollback["dirty_state_after_rollback"])
        self.assertFalse(rollback["persistent_update_performed"])

    def test_bad_source_blocks(self):
        bad = deepcopy(self.reachable)
        bad["source_final_action_approval_boundary"]["source_validated"] = False
        self.assert_invalid(bad)

    def test_final_action_created_false_blocks(self):
        bad = deepcopy(self.reachable)
        bad["sandbox_final_action"]["final_action_created"] = False
        self.assert_invalid(bad)

    def test_wrong_final_action_blocks(self):
        bad = deepcopy(self.reachable)
        bad["sandbox_final_action"]["final_action"] = "wait_or_observe"
        self.assert_invalid(bad)

    def test_direct_command_and_execution_block(self):
        for field in ("direct_command_created", "sandbox_execution_created", "execution_allowed_in_this_package"):
            bad = deepcopy(self.reachable)
            bad["sandbox_final_action"][field] = True
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
        self.assertEqual(summary["final_action_result_count"], 30)
        self.assertEqual(summary["valid_final_action_count"], 3)
        self.assertEqual(summary["invalid_final_action_count"], 27)
        self.assertEqual(summary["final_action_created_count"], 3)
        self.assertEqual(summary["sandbox_only_final_action_count"], 3)
        self.assertEqual(summary["arbitration_rules_preserved_count"], 3)
        self.assertEqual(summary["reach_front_item_final_action_count"], 1)
        self.assertEqual(summary["wait_or_observe_final_action_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_final_action_count"], 1)
        self.assertEqual(summary["direct_command_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["rollback_available_count"], 3)

    def test_cli_command(self):
        result = run_command("run-sandbox-candidate-ordering-arbitration-final-action-minimal-check")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["valid_final_action_count"], 3)


if __name__ == "__main__":
    unittest.main()
