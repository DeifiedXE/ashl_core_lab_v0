import copy
import unittest

from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record,
)
from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_minimal import (
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_minimal_check,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationReorderedCandidateFeedbackGatedCandidateReorderingApprovalBoundaryMinimalTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.sources = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_minimal_check()[
                "valid_records"
            ]
        )
        cls.result = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_minimal_check()
        )
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_reordering_approval_boundaries_are_created(self):
        for record in self.records:
            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                    record
                )
            )

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_minimal",
            )
            self.assertEqual(record["boundary_index_before"], BOUNDARY_INDEX_BEFORE)
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(
                record["feedback_gated_reordering_approval_boundary"]["future_candidate_reordering_allowed"]
            )

    def test_default_builder_uses_b167_feedback_application_source(self):
        record = (
            build_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record()
        )
        source = record["source_feedback_application"]
        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                record
            )
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b167")
        self.assertTrue(source["feedback_applied"])
        self.assertEqual(source["feedback_application_effect_scope"], "record_only_no_ordering_change")

    def test_reach_front_item_application_can_enter_future_reordering(self):
        record = (
            build_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                self.sources[0]
            )
        )
        boundary = record["feedback_gated_reordering_approval_boundary"]
        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                record
            )
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "item_reachable_feedback_prioritizes_reach")
        self.assertEqual(boundary["candidate_for_future_reordering"], "reach_front_item")

    def test_wait_context_application_can_enter_future_reordering(self):
        boundary = self.wait["feedback_gated_reordering_approval_boundary"]
        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                self.wait
            )
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "item_not_afforded_blocks_feedback_priority")
        self.assertEqual(boundary["candidate_for_future_reordering"], "wait_or_observe")

    def test_probe_application_can_enter_future_reordering(self):
        boundary = self.probe["feedback_gated_reordering_approval_boundary"]
        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                self.probe
            )
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "mismatch_feedback_outranks_retry_tendency")
        self.assertEqual(boundary["candidate_for_future_reordering"], "observe_or_alternative_probe")

    def test_boundary_does_not_reorder_or_change_scores(self):
        for record in self.records:
            boundary = record["feedback_gated_reordering_approval_boundary"]

            self.assertTrue(boundary["future_candidate_reordering_allowed"])
            self.assertFalse(boundary["candidate_reordering_applied_in_this_package"])
            self.assertFalse(boundary["candidate_ordering_changed_in_this_package"])
            self.assertFalse(boundary["candidate_scores_changed_in_this_package"])
            self.assertFalse(boundary["next_cycle_candidate_ordering_changed_in_this_package"])
            self.assertEqual(boundary["candidate_order_before"], [])
            self.assertEqual(boundary["candidate_order_after"], [])
            self.assertEqual(boundary["ordering_delta"], 0.0)

    def test_boundary_does_not_create_actions_commands_execution_or_observation(self):
        for record in self.records:
            boundary = record["feedback_gated_reordering_approval_boundary"]

            self.assertFalse(boundary["new_action_created_in_this_package"])
            self.assertFalse(boundary["new_selected_action_created_in_this_package"])
            self.assertFalse(boundary["new_final_action_created_in_this_package"])
            self.assertFalse(boundary["new_direct_command_created_in_this_package"])
            self.assertFalse(boundary["new_execution_created_in_this_package"])
            self.assertFalse(boundary["new_outcome_observation_created_in_this_package"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_feedback_application"]["source_validated"] = False

        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                bad
            )
        )

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_source_without_applied_record_only_feedback_blocks(self):
        for field, value, error in (
            ("feedback_applied", False, "source_feedback_applied_not_expected"),
            (
                "feedback_application_effect_scope",
                "ordering_change",
                "source_feedback_application_effect_scope_not_expected",
            ),
        ):
            bad = copy.deepcopy(self.reach)
            bad["source_feedback_application"][field] = value

            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(error, result["error_codes"])

    def test_source_already_reordered_blocks(self):
        for field in (
            "candidate_reordering_created_in_source_package",
            "candidate_scores_changed_in_source_package",
            "next_cycle_candidate_ordering_changed_in_source_package",
        ):
            bad = copy.deepcopy(self.reach)
            bad["source_feedback_application"][field] = True

            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"source_{field}_not_expected", result["error_codes"])

    def test_bad_application_type_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_feedback_application"]["feedback_application_type"] = "unknown"

        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                bad
            )
        )

        self.assertFalse(result["valid"])
        self.assertIn("source_feedback_application_type_not_supported", result["error_codes"])

    def test_future_reordering_not_allowed_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["feedback_gated_reordering_approval_boundary"]["future_candidate_reordering_allowed"] = False

        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                bad
            )
        )

        self.assertFalse(result["valid"])
        self.assertIn(
            "feedback_gated_reordering_approval_boundary_future_candidate_reordering_allowed_not_expected",
            result["error_codes"],
        )

    def test_reordering_or_ordering_change_true_blocks(self):
        for field in (
            "candidate_reordering_applied_in_this_package",
            "candidate_ordering_changed_in_this_package",
            "candidate_scores_changed_in_this_package",
            "next_cycle_candidate_ordering_changed_in_this_package",
        ):
            bad = copy.deepcopy(self.wait)
            bad["feedback_gated_reordering_approval_boundary"][field] = True

            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"feedback_gated_reordering_approval_boundary_{field}_not_expected", result["error_codes"])

    def test_new_action_command_execution_or_observation_true_blocks(self):
        for field in (
            "new_action_created_in_this_package",
            "new_selected_action_created_in_this_package",
            "new_final_action_created_in_this_package",
            "new_direct_command_created_in_this_package",
            "new_execution_created_in_this_package",
            "new_outcome_observation_created_in_this_package",
        ):
            bad = copy.deepcopy(self.reach)
            bad["feedback_gated_reordering_approval_boundary"][field] = True

            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"feedback_gated_reordering_approval_boundary_{field}_not_expected", result["error_codes"])

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
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["reordering_approval_boundary_result_count"], 49)
        self.assertEqual(summary["valid_reordering_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_reordering_approval_boundary_count"], 46)
        self.assertEqual(summary["future_candidate_reordering_allowed_count"], 3)
        self.assertEqual(summary["positive_item_reordering_boundary_count"], 1)
        self.assertEqual(summary["wait_context_reordering_boundary_count"], 1)
        self.assertEqual(summary["mismatch_probe_reordering_boundary_count"], 1)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["feedback_loop_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-feedback-gated-candidate-reordering-approval-boundary-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-feedback-gated-candidate-reordering-approval-boundary-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
