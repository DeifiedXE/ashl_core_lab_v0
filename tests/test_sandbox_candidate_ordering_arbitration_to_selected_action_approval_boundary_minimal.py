import unittest
from copy import deepcopy

from ashl_core.sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_minimal import (
    build_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_record,
)
from ashl_core.sandbox_candidate_ordering_signal_arbitration_minimal import (
    run_sandbox_candidate_ordering_signal_arbitration_minimal_check,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationToSelectedActionApprovalBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_signal_arbitration_minimal_check()["valid_records"]
        cls.result = run_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reachable = cls.records[0]
        cls.not_afforded = cls.records[1]
        cls.mismatch = cls.records[2]

    def assert_invalid(self, record: dict) -> None:
        result = validate_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])

    def test_valid_selected_action_approval_boundaries_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_record(record)
            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_minimal",
            )

    def test_boundary_versions_are_b139_to_b140(self):
        boundary = self.result["boundary"]
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b139")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b140")

    def test_default_builder_uses_signal_arbitration_source(self):
        record = build_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_record()
        source = record["source_signal_arbitration"]
        boundary = record["selected_action_approval_boundary"]
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b139")
        self.assertEqual(boundary["candidate_for_future_selected_action"], source["top_ranked_candidate"])

    def test_future_selected_action_allowed_but_not_created(self):
        boundary = self.reachable["selected_action_approval_boundary"]
        self.assertTrue(boundary["future_selected_action_allowed"])
        self.assertEqual(boundary["candidate_for_future_selected_action"], "reach_front_item")
        self.assertFalse(boundary["selected_action_created_in_this_package"])
        self.assertFalse(boundary["sandbox_execution_created"])

    def test_unavailable_reach_source_preserves_affordance_gate_result(self):
        source = self.not_afforded["source_signal_arbitration"]
        boundary = self.not_afforded["selected_action_approval_boundary"]
        self.assertTrue(source["affordance_gate_applied"])
        self.assertEqual(source["top_ranked_candidate"], "wait_or_observe")
        self.assertEqual(boundary["candidate_for_future_selected_action"], "wait_or_observe")

    def test_mismatch_source_preserves_feedback_over_tendency_result(self):
        source = self.mismatch["source_signal_arbitration"]
        boundary = self.mismatch["selected_action_approval_boundary"]
        self.assertTrue(source["feedback_within_purpose_checked"])
        self.assertTrue(source["tendency_limited_checked"])
        self.assertEqual(source["top_ranked_candidate"], "observe_or_alternative_probe")
        self.assertEqual(boundary["candidate_for_future_selected_action"], "observe_or_alternative_probe")

    def test_arbitration_rules_are_preserved(self):
        for record in self.records:
            source = record["source_signal_arbitration"]
            self.assertTrue(source["purpose_scope_preserved"])
            self.assertTrue(source["affordance_gate_applied"])
            self.assertTrue(source["feedback_within_purpose_checked"])
            self.assertTrue(source["tendency_limited_checked"])
            self.assertFalse(source["raw_weighted_sum_used"])

    def test_no_action_creation_or_execution(self):
        boundary = self.reachable["selected_action_approval_boundary"]
        self.assertFalse(boundary["selected_action_created_in_this_package"])
        self.assertFalse(boundary["final_action_created"])
        self.assertFalse(boundary["direct_command_created"])
        self.assertFalse(boundary["sandbox_execution_created"])
        self.assertFalse(boundary["execution_allowed_in_this_package"])

    def test_invalid_source_blocks(self):
        bad = deepcopy(self.reachable)
        bad["source_signal_arbitration"]["source_validated"] = False
        self.assert_invalid(bad)

    def test_wrong_future_candidate_blocks(self):
        bad = deepcopy(self.reachable)
        bad["selected_action_approval_boundary"]["candidate_for_future_selected_action"] = "wrong"
        self.assert_invalid(bad)

    def test_selected_action_created_blocks(self):
        bad = deepcopy(self.reachable)
        bad["selected_action_approval_boundary"]["selected_action_created_in_this_package"] = True
        self.assert_invalid(bad)

    def test_execution_allowed_blocks(self):
        bad = deepcopy(self.reachable)
        bad["selected_action_approval_boundary"]["execution_allowed_in_this_package"] = True
        self.assert_invalid(bad)

    def test_raw_weighted_sum_source_blocks(self):
        bad = deepcopy(self.reachable)
        bad["source_signal_arbitration"]["raw_weighted_sum_used"] = True
        self.assert_invalid(bad)

    def test_blocked_flags_true_block(self):
        bad = deepcopy(self.reachable)
        bad["blocked_flags"]["proof_of_learning_claim"] = True
        self.assert_invalid(bad)

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]
        self.assertEqual(summary["selected_action_approval_boundary_result_count"], 31)
        self.assertEqual(summary["valid_selected_action_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_selected_action_approval_boundary_count"], 28)
        self.assertEqual(summary["future_selected_action_allowed_count"], 3)
        self.assertEqual(summary["selected_action_creation_blocked_count"], 3)
        self.assertEqual(summary["final_action_blocked_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["arbitration_rules_preserved_count"], 3)
        self.assertEqual(summary["purpose_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-to-selected-action-approval-boundary-minimal-check"
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["valid_selected_action_approval_boundary_count"], 3)


if __name__ == "__main__":
    unittest.main()
