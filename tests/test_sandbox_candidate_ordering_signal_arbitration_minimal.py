import unittest
from copy import deepcopy

from ashl_core.sandbox_candidate_ordering_signal_arbitration_minimal import (
    build_sandbox_candidate_ordering_signal_arbitration_record,
    run_sandbox_candidate_ordering_signal_arbitration_minimal_check,
    validate_sandbox_candidate_ordering_signal_arbitration_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingSignalArbitrationMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_sandbox_candidate_ordering_signal_arbitration_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reachable = cls.records[0]
        cls.not_afforded = cls.records[1]
        cls.mismatch = cls.records[2]

    def assert_invalid(self, record: dict) -> None:
        result = validate_sandbox_candidate_ordering_signal_arbitration_record(record)
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])

    def test_valid_arbitration_records_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = validate_sandbox_candidate_ordering_signal_arbitration_record(record)
            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(record["record_type"], "sandbox_candidate_ordering_signal_arbitration_minimal")

    def test_boundary_versions_are_b138_to_b139(self):
        boundary = self.result["boundary"]
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b138")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b139")

    def test_authority_order_is_purpose_affordance_feedback_then_tendency(self):
        self.assertEqual(
            self.reachable["signal_authority_order"],
            [
                "approved_purpose_scope",
                "safety_boundary",
                "affordance_feasibility_gate",
                "approved_purpose_feedback_reorder",
                "tendency_tie_break_or_small_nudge",
            ],
        )

    def test_reachable_item_feedback_prioritizes_reach(self):
        result = self.reachable["arbitration_result"]
        source = self.reachable["source_signals"]
        self.assertEqual(source["approved_purpose"], "approach_or_reach_item")
        self.assertTrue(source["affordance_signal"]["affordance_available"])
        self.assertEqual(result["candidate_actions_after_arbitration"][0], "reach_front_item")
        self.assertEqual(result["primary_ranked_action"], "reach_front_item")

    def test_affordance_gate_blocks_unavailable_reach_despite_feedback(self):
        result = self.not_afforded["arbitration_result"]
        source = self.not_afforded["source_signals"]
        self.assertFalse(source["affordance_signal"]["affordance_available"])
        self.assertEqual(source["approved_purpose_feedback_signal"]["feedback_type"], "positive_item_contact_feedback")
        self.assertNotIn("reach_front_item", result["candidate_actions_after_arbitration"])
        self.assertEqual(result["primary_ranked_action"], "wait_or_observe")

    def test_mismatch_feedback_outranks_retry_tendency(self):
        result = self.mismatch["arbitration_result"]
        after = result["candidate_actions_after_arbitration"]
        tendency = self.mismatch["source_signals"]["tendency_signal"]
        self.assertEqual(tendency["tendency_source"], "bounded_retry_pressure")
        self.assertEqual(after[0], "observe_or_alternative_probe")
        self.assertLess(after.index("check_before_retry"), after.index("retry_same_action_without_check"))

    def test_no_raw_weighted_sum_or_purpose_creation(self):
        source = self.reachable["source_signals"]
        self.assertFalse(source["raw_weighted_sum_used"])
        self.assertFalse(source["purpose_created_by_signals"])

    def test_tendency_is_bounded_and_limited(self):
        for record in self.records:
            tendency = record["source_signals"]["tendency_signal"]
            self.assertLessEqual(abs(tendency["tendency_delta"]), 0.10)
            self.assertEqual(tendency["tendency_role"], "tie_break_or_small_nudge")

    def test_no_action_creation_or_execution(self):
        result = self.reachable["arbitration_result"]
        self.assertFalse(result["action_intent_created"])
        self.assertFalse(result["selected_action_created"])
        self.assertFalse(result["final_action_created"])
        self.assertFalse(result["direct_command_created"])
        self.assertFalse(result["sandbox_execution_created"])

    def test_rollback_preview_restores_before_order(self):
        for record in self.records:
            rollback = record["rollback_preview"]
            self.assertTrue(rollback["rollback_available"])
            self.assertEqual(
                rollback["candidate_actions_restored"],
                record["arbitration_result"]["candidate_actions_before_arbitration"],
            )
            self.assertFalse(rollback["dirty_state_after_rollback"])

    def test_wrong_authority_order_blocks(self):
        bad = deepcopy(self.reachable)
        bad["signal_authority_order"] = list(reversed(bad["signal_authority_order"]))
        self.assert_invalid(bad)

    def test_raw_weighted_sum_blocks(self):
        bad = deepcopy(self.reachable)
        bad["source_signals"]["raw_weighted_sum_used"] = True
        self.assert_invalid(bad)

    def test_purpose_created_by_signals_blocks(self):
        bad = deepcopy(self.reachable)
        bad["source_signals"]["purpose_created_by_signals"] = True
        self.assert_invalid(bad)

    def test_feedback_cross_purpose_blocks(self):
        bad = deepcopy(self.reachable)
        bad["source_signals"]["approved_purpose_feedback_signal"]["feedback_scope_matches_purpose"] = False
        self.assert_invalid(bad)

    def test_tendency_delta_too_high_blocks(self):
        bad = deepcopy(self.reachable)
        bad["source_signals"]["tendency_signal"]["tendency_delta"] = 0.22
        self.assert_invalid(bad)

    def test_affordance_used_as_desire_blocks(self):
        bad = deepcopy(self.reachable)
        bad["source_signals"]["affordance_signal"]["affordance_role"] = "desire_score"
        self.assert_invalid(bad)

    def test_unavailable_affordance_not_blocked_blocks(self):
        bad = deepcopy(self.not_afforded)
        bad["arbitration_result"]["candidate_actions_after_arbitration"] = [
            "reach_front_item",
            "wait_or_observe",
        ]
        self.assert_invalid(bad)

    def test_selected_action_created_blocks(self):
        bad = deepcopy(self.reachable)
        bad["arbitration_result"]["selected_action_created"] = True
        self.assert_invalid(bad)

    def test_blocked_flags_true_block(self):
        bad = deepcopy(self.reachable)
        bad["blocked_flags"]["tendency_overrode_purpose"] = True
        self.assert_invalid(bad)

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]
        self.assertEqual(summary["arbitration_result_count"], 36)
        self.assertEqual(summary["valid_arbitration_result_count"], 3)
        self.assertEqual(summary["invalid_arbitration_result_count"], 33)
        self.assertEqual(summary["purpose_scope_preserved_count"], 3)
        self.assertEqual(summary["affordance_gate_applied_count"], 3)
        self.assertEqual(summary["feedback_within_purpose_checked_count"], 3)
        self.assertEqual(summary["tendency_limited_checked_count"], 3)
        self.assertEqual(summary["raw_weighted_sum_blocked_count"], 3)
        self.assertEqual(summary["purpose_creation_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["rollback_available_count"], 3)
        self.assertEqual(summary["affordance_blocks_unavailable_feedback_count"], 1)
        self.assertEqual(summary["feedback_outranks_tendency_count"], 1)

    def test_cli_command(self):
        result = run_command("run-sandbox-candidate-ordering-signal-arbitration-minimal-check")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["valid_arbitration_result_count"], 3)


if __name__ == "__main__":
    unittest.main()
