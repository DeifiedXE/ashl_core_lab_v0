import copy
import unittest

from ashl_core.sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_minimal import (
    run_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_minimal_check,
)
from ashl_core.sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationOutcomeFeedbackApprovalBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_minimal_check()[
            "valid_records"
        ]
        cls.result = run_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_feedback_approval_boundaries_are_created(self):
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record(
                record
            )

            self.assertTrue(result["valid"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["feedback_approval_boundary"]["future_feedback_allowed"])

    def test_reach_front_item_outcome_can_enter_future_feedback(self):
        record = build_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record(
            self.sources[0]
        )
        boundary = record["feedback_approval_boundary"]
        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record(
            record
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "item_reachable_feedback_prioritizes_reach")
        self.assertEqual(result["outcome_label"], "arbitration_positive_item_contact_observed")
        self.assertEqual(boundary["candidate_for_future_feedback"], "arbitration_positive_item_contact_feedback")

    def test_wait_or_observe_outcome_can_enter_future_feedback(self):
        boundary = self.wait["feedback_approval_boundary"]
        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record(
            self.wait
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "item_not_afforded_blocks_feedback_priority")
        self.assertEqual(result["outcome_label"], "arbitration_wait_context_observed")
        self.assertEqual(boundary["candidate_for_future_feedback"], "arbitration_wait_context_observation_feedback")

    def test_probe_outcome_can_enter_future_feedback(self):
        boundary = self.probe["feedback_approval_boundary"]
        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record(
            self.probe
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "mismatch_feedback_outranks_retry_tendency")
        self.assertEqual(result["outcome_label"], "arbitration_mismatch_probe_context_observed")
        self.assertEqual(boundary["candidate_for_future_feedback"], "arbitration_mismatch_probe_context_feedback")

    def test_boundary_does_not_create_feedback_or_reordering(self):
        for record in self.records:
            boundary = record["feedback_approval_boundary"]

            self.assertFalse(boundary["feedback_evaluation_created_in_this_package"])
            self.assertFalse(boundary["feedback_applied_in_this_package"])
            self.assertFalse(boundary["feedback_loop_created_in_this_package"])
            self.assertFalse(boundary["candidate_reordering_created_in_this_package"])
            self.assertFalse(boundary["new_action_created_in_this_package"])
            self.assertTrue(boundary["future_candidate_reordering_requires_separate_boundary"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_outcome_observation"]["source_validated"] = False

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_source_already_has_feedback_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_outcome_observation"]["feedback_loop_created"] = True

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("feedback_loop_created_not_expected", result["error_codes"])

    def test_bad_outcome_label_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_outcome_observation"]["outcome_label"] = "unknown"

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_outcome_label_not_feedback_eligible", result["error_codes"])

    def test_feedback_evaluation_true_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["feedback_approval_boundary"]["feedback_evaluation_created_in_this_package"] = True

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "feedback_approval_boundary_feedback_evaluation_created_in_this_package_not_expected",
            result["error_codes"],
        )

    def test_feedback_application_true_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["feedback_approval_boundary"]["feedback_applied_in_this_package"] = True

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "feedback_approval_boundary_feedback_applied_in_this_package_not_expected",
            result["error_codes"],
        )

    def test_reordering_true_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["feedback_approval_boundary"]["candidate_reordering_created_in_this_package"] = True

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "feedback_approval_boundary_candidate_reordering_created_in_this_package_not_expected",
            result["error_codes"],
        )

    def test_new_action_or_command_or_execution_true_blocks(self):
        for field in (
            "new_action_created_in_this_package",
            "new_selected_action_created_in_this_package",
            "new_final_action_created_in_this_package",
            "new_direct_command_created_in_this_package",
            "new_execution_created_in_this_package",
        ):
            bad = copy.deepcopy(self.reach)
            bad["feedback_approval_boundary"][field] = True

            result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"feedback_approval_boundary_{field}_not_expected", result["error_codes"])

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

            result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_approval_boundary_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["feedback_approval_boundary_result_count"], 37)
        self.assertEqual(summary["valid_feedback_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_feedback_approval_boundary_count"], 34)
        self.assertEqual(summary["future_feedback_allowed_count"], 3)
        self.assertEqual(summary["positive_item_feedback_boundary_count"], 1)
        self.assertEqual(summary["wait_context_feedback_boundary_count"], 1)
        self.assertEqual(summary["mismatch_probe_feedback_boundary_count"], 1)
        self.assertEqual(summary["feedback_creation_blocked_count"], 3)
        self.assertEqual(summary["feedback_application_blocked_count"], 3)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-outcome-feedback-approval-boundary-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-sandbox-candidate-ordering-arbitration-outcome-feedback-approval-boundary-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
