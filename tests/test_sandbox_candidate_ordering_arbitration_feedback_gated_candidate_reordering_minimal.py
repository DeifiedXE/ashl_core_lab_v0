import copy
import unittest

from ashl_core.sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_minimal import (
    run_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_minimal_check,
)
from ashl_core.sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record,
    run_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationFeedbackGatedCandidateReorderingMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_minimal_check()[
            "valid_records"
        ]
        cls.result = run_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_reordering_records_are_created(self):
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(
                record
            )

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["feedback_gated_candidate_reordering"]["candidate_reordering_created"])
            self.assertTrue(record["feedback_gated_candidate_reordering"]["candidate_reordering_applied"])
            self.assertTrue(record["feedback_gated_candidate_reordering"]["candidate_order_changed"])

    def test_reach_feedback_prioritizes_reach_front_item(self):
        record = build_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(
            self.sources[0]
        )
        reordering = record["feedback_gated_candidate_reordering"]
        result = validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "item_reachable_feedback_prioritizes_reach")
        self.assertEqual(reordering["candidate_actions_after_reordering"][0], "reach_front_item")
        self.assertEqual(reordering["primary_ranked_action"], "reach_front_item")

    def test_wait_context_feedback_prioritizes_wait_or_observe(self):
        reordering = self.wait["feedback_gated_candidate_reordering"]
        result = validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(
            self.wait
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "item_not_afforded_blocks_feedback_priority")
        self.assertEqual(reordering["candidate_actions_after_reordering"][0], "wait_or_observe")
        self.assertEqual(reordering["primary_ranked_action"], "wait_or_observe")

    def test_probe_feedback_prioritizes_observe_or_alternative_probe(self):
        reordering = self.probe["feedback_gated_candidate_reordering"]
        after = reordering["candidate_actions_after_reordering"]
        result = validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(
            self.probe
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "mismatch_feedback_outranks_retry_tendency")
        self.assertEqual(after[0], "observe_or_alternative_probe")
        self.assertLess(after.index("check_before_retry"), after.index("retry_same_action_without_check"))

    def test_reordering_is_sandbox_only_and_advisory(self):
        for record in self.records:
            reordering = record["feedback_gated_candidate_reordering"]

            self.assertTrue(reordering["reordering_is_sandbox_only"])
            self.assertTrue(reordering["reordering_is_advisory"])
            self.assertEqual(reordering["reordering_scope"], "same_session_sandbox_only")
            self.assertEqual(reordering["reordering_effect_scope"], "same_session_sandbox_advisory_record_only")

    def test_reordering_does_not_change_scores_or_runtime_next_cycle(self):
        for record in self.records:
            reordering = record["feedback_gated_candidate_reordering"]

            self.assertTrue(reordering["candidate_order_changed"])
            self.assertFalse(reordering["candidate_scores_changed"])
            self.assertFalse(reordering["runtime_next_cycle_candidate_ordering_changed"])

    def test_no_action_command_execution_or_observation(self):
        for record in self.records:
            reordering = record["feedback_gated_candidate_reordering"]

            self.assertFalse(reordering["new_action_created"])
            self.assertFalse(reordering["new_selected_action_created"])
            self.assertFalse(reordering["new_final_action_created"])
            self.assertFalse(reordering["new_direct_command_created"])
            self.assertFalse(reordering["new_execution_created"])
            self.assertFalse(reordering["new_outcome_observation_created"])

    def test_rollback_preview_restores_before_order(self):
        for record in self.records:
            rollback = record["rollback_preview"]
            reordering = record["feedback_gated_candidate_reordering"]

            self.assertTrue(rollback["rollback_available"])
            self.assertEqual(
                rollback["candidate_actions_restored"],
                reordering["candidate_actions_before_reordering"],
            )
            self.assertFalse(rollback["dirty_state_after_rollback"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_reordering_approval_boundary"]["source_validated"] = False

        result = validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_source_without_future_reordering_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_reordering_approval_boundary"]["future_candidate_reordering_allowed"] = False

        result = validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_future_candidate_reordering_allowed_not_expected", result["error_codes"])

    def test_source_already_reordered_blocks(self):
        for field in (
            "candidate_reordering_applied_in_source_package",
            "candidate_ordering_changed_in_source_package",
            "candidate_scores_changed_in_source_package",
        ):
            bad = copy.deepcopy(self.reach)
            bad["source_reordering_approval_boundary"][field] = True

            result = validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"source_{field}_not_expected", result["error_codes"])

    def test_reordering_not_applied_or_order_not_changed_blocks(self):
        for field in ("candidate_reordering_created", "candidate_reordering_applied", "candidate_order_changed"):
            bad = copy.deepcopy(self.reach)
            bad["feedback_gated_candidate_reordering"][field] = False

            result = validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"feedback_gated_candidate_reordering_{field}_not_expected", result["error_codes"])

    def test_primary_not_first_or_same_order_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["feedback_gated_candidate_reordering"]["candidate_actions_after_reordering"] = [
            "wait_or_observe",
            "reach_front_item",
            "step_toward_item",
            "fallback_stop_and_report",
        ]
        result = validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("primary_ranked_action_not_first", result["error_codes"])

        same = copy.deepcopy(self.reach)
        same["feedback_gated_candidate_reordering"]["candidate_actions_after_reordering"] = list(
            same["feedback_gated_candidate_reordering"]["candidate_actions_before_reordering"]
        )
        result = validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(same)
        self.assertFalse(result["valid"])
        self.assertIn("candidate_order_not_changed", result["error_codes"])

    def test_new_action_command_execution_or_observation_true_blocks(self):
        for field in (
            "new_action_created",
            "new_selected_action_created",
            "new_final_action_created",
            "new_direct_command_created",
            "new_execution_created",
            "new_outcome_observation_created",
        ):
            bad = copy.deepcopy(self.reach)
            bad["feedback_gated_candidate_reordering"][field] = True

            result = validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"feedback_gated_candidate_reordering_{field}_not_expected", result["error_codes"])

    def test_memory_predictor_direct_feed_and_proof_flags_block(self):
        for field in (
            "memory_write",
            "retention_write",
            "predictor_read_enabled",
            "predictor_influence_enabled",
            "predictor_modified",
            "direct_endocrine_feed",
            "direct_tendency_feed",
            "proof_of_learning_claim",
        ):
            bad = copy.deepcopy(self.probe)
            bad["blocked_flags"][field] = True

            result = validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["feedback_gated_reordering_result_count"], 46)
        self.assertEqual(summary["valid_feedback_gated_reordering_count"], 3)
        self.assertEqual(summary["invalid_feedback_gated_reordering_count"], 43)
        self.assertEqual(summary["candidate_reordering_created_count"], 3)
        self.assertEqual(summary["candidate_reordering_applied_count"], 3)
        self.assertEqual(summary["candidate_order_changed_count"], 3)
        self.assertEqual(summary["reach_reordering_count"], 1)
        self.assertEqual(summary["wait_reordering_count"], 1)
        self.assertEqual(summary["probe_reordering_count"], 1)
        self.assertEqual(summary["candidate_scores_blocked_count"], 3)
        self.assertEqual(summary["runtime_next_cycle_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-feedback-gated-candidate-reordering-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-sandbox-candidate-ordering-arbitration-feedback-gated-candidate-reordering-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
