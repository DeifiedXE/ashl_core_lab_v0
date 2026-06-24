import copy
import unittest

from ashl_core.sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal import (
    run_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal_check,
)
from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationReorderedCandidateToSelectedActionApprovalBoundaryMinimalTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_minimal_check()[
            "valid_records"
        ]
        cls.result = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal_check()
        )
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_selected_action_approval_boundaries_are_created(self):
        for record in self.records:
            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
                    record
                )
            )

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["selected_action_approval_boundary"]["future_selected_action_allowed"])
            self.assertFalse(
                record["selected_action_approval_boundary"]["selected_action_created_in_this_package"]
            )

    def test_reach_reordered_candidate_can_enter_future_selected_action(self):
        record = build_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
            self.sources[0]
        )
        boundary = record["selected_action_approval_boundary"]
        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
                record
            )
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "item_reachable_feedback_prioritizes_reach")
        self.assertEqual(boundary["candidate_for_future_selected_action"], "reach_front_item")

    def test_wait_reordered_candidate_can_enter_future_selected_action(self):
        boundary = self.wait["selected_action_approval_boundary"]
        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
                self.wait
            )
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "item_not_afforded_blocks_feedback_priority")
        self.assertEqual(boundary["candidate_for_future_selected_action"], "wait_or_observe")

    def test_probe_reordered_candidate_can_enter_future_selected_action(self):
        boundary = self.probe["selected_action_approval_boundary"]
        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
                self.probe
            )
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "mismatch_feedback_outranks_retry_tendency")
        self.assertEqual(boundary["candidate_for_future_selected_action"], "observe_or_alternative_probe")

    def test_boundary_does_not_create_selected_action_or_later_action_layers(self):
        for record in self.records:
            boundary = record["selected_action_approval_boundary"]

            self.assertFalse(boundary["selected_action_created_in_this_package"])
            self.assertFalse(boundary["final_action_created"])
            self.assertFalse(boundary["direct_command_created"])
            self.assertFalse(boundary["sandbox_execution_created"])
            self.assertFalse(boundary["new_outcome_observation_created"])
            self.assertFalse(boundary["execution_allowed_in_this_package"])

    def test_source_reordering_must_be_preserved(self):
        for field in (
            "candidate_reordering_created",
            "candidate_reordering_applied",
            "candidate_order_changed",
        ):
            bad = copy.deepcopy(self.reach)
            bad["source_feedback_gated_candidate_reordering"][field] = False

            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"source_{field}_not_expected", result["error_codes"])

    def test_source_score_or_runtime_order_change_blocks(self):
        for field in ("candidate_scores_changed", "runtime_next_cycle_candidate_ordering_changed"):
            bad = copy.deepcopy(self.wait)
            bad["source_feedback_gated_candidate_reordering"][field] = True

            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"source_{field}_not_expected", result["error_codes"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_feedback_gated_candidate_reordering"]["source_validated"] = False

        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_future_selected_action_not_allowed_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["selected_action_approval_boundary"]["future_selected_action_allowed"] = False

        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn(
            "selected_action_approval_boundary_future_selected_action_allowed_not_expected",
            result["error_codes"],
        )

    def test_wrong_future_selected_action_candidate_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["selected_action_approval_boundary"]["candidate_for_future_selected_action"] = "wait_or_observe"

        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn(
            "selected_action_approval_boundary_candidate_for_future_selected_action_not_expected",
            result["error_codes"],
        )

    def test_selected_action_true_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["selected_action_approval_boundary"]["selected_action_created_in_this_package"] = True

        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn(
            "selected_action_approval_boundary_selected_action_created_in_this_package_not_expected",
            result["error_codes"],
        )

    def test_final_direct_execution_or_observation_true_blocks(self):
        for field in (
            "final_action_created",
            "direct_command_created",
            "sandbox_execution_created",
            "new_outcome_observation_created",
            "execution_allowed_in_this_package",
        ):
            bad = copy.deepcopy(self.reach)
            bad["selected_action_approval_boundary"][field] = True

            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"selected_action_approval_boundary_{field}_not_expected", result["error_codes"])

    def test_future_boundaries_remain_required(self):
        for field in (
            "future_final_action_requires_separate_boundary",
            "future_direct_command_requires_separate_boundary",
            "future_execution_requires_separate_boundary",
            "future_outcome_observation_requires_separate_boundary",
        ):
            bad = copy.deepcopy(self.reach)
            bad["selected_action_approval_boundary"][field] = False

            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"selected_action_approval_boundary_{field}_not_expected", result["error_codes"])

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

            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["selected_action_approval_boundary_result_count"], 56)
        self.assertEqual(summary["valid_selected_action_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_selected_action_approval_boundary_count"], 53)
        self.assertEqual(summary["future_selected_action_allowed_count"], 3)
        self.assertEqual(summary["reach_selected_action_boundary_count"], 1)
        self.assertEqual(summary["wait_selected_action_boundary_count"], 1)
        self.assertEqual(summary["probe_selected_action_boundary_count"], 1)
        self.assertEqual(summary["source_reordering_preserved_count"], 3)
        self.assertEqual(summary["same_session_sandbox_only_count"], 3)
        self.assertEqual(summary["selected_action_creation_blocked_count"], 3)
        self.assertEqual(summary["final_action_blocked_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["outcome_observation_blocked_count"], 3)
        self.assertEqual(summary["candidate_scores_blocked_count"], 3)
        self.assertEqual(summary["runtime_next_cycle_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-to-selected-action-"
            "approval-boundary-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-to-selected-action-"
            "approval-boundary-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
