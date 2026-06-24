import copy
import unittest

from ashl_core.sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record,
)
from ashl_core.sandbox_candidate_ordering_arbitration_outcome_feedback_minimal import (
    run_sandbox_candidate_ordering_arbitration_outcome_feedback_minimal_check,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationOutcomeFeedbackApplicationApprovalBoundaryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_outcome_feedback_minimal_check()["valid_records"]
        cls.result = (
            run_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_minimal_check()
        )
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_feedback_application_approval_boundaries_are_created(self):
        for record in self.records:
            result = (
                validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
                    record
                )
            )

            self.assertTrue(result["valid"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(
                record["feedback_application_approval_boundary"]["future_feedback_application_allowed"]
            )

    def test_reach_front_item_feedback_can_enter_future_application(self):
        record = build_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
            self.sources[0]
        )
        boundary = record["feedback_application_approval_boundary"]
        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
            record
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "item_reachable_feedback_prioritizes_reach")
        self.assertEqual(result["feedback_type"], "arbitration_positive_item_contact_feedback")
        self.assertEqual(
            boundary["candidate_for_future_feedback_application"],
            "arbitration_positive_item_contact_feedback_application",
        )

    def test_wait_context_feedback_can_enter_future_application(self):
        boundary = self.wait["feedback_application_approval_boundary"]
        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
            self.wait
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "item_not_afforded_blocks_feedback_priority")
        self.assertEqual(result["feedback_type"], "arbitration_wait_context_observation_feedback")
        self.assertEqual(
            boundary["candidate_for_future_feedback_application"],
            "arbitration_wait_context_observation_feedback_application",
        )

    def test_probe_feedback_can_enter_future_application(self):
        boundary = self.probe["feedback_application_approval_boundary"]
        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
            self.probe
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "mismatch_feedback_outranks_retry_tendency")
        self.assertEqual(result["feedback_type"], "arbitration_mismatch_probe_context_feedback")
        self.assertEqual(
            boundary["candidate_for_future_feedback_application"],
            "arbitration_mismatch_probe_context_feedback_application",
        )

    def test_boundary_does_not_apply_feedback_or_reorder(self):
        for record in self.records:
            boundary = record["feedback_application_approval_boundary"]

            self.assertFalse(boundary["feedback_applied_in_this_package"])
            self.assertFalse(boundary["feedback_loop_created_in_this_package"])
            self.assertFalse(boundary["candidate_reordering_created_in_this_package"])
            self.assertFalse(boundary["candidate_scores_changed_in_this_package"])
            self.assertFalse(boundary["next_cycle_candidate_ordering_changed_in_this_package"])
            self.assertTrue(boundary["future_candidate_reordering_requires_separate_boundary"])

    def test_boundary_does_not_create_action_command_execution_or_observation(self):
        for record in self.records:
            boundary = record["feedback_application_approval_boundary"]

            self.assertFalse(boundary["new_action_created_in_this_package"])
            self.assertFalse(boundary["new_selected_action_created_in_this_package"])
            self.assertFalse(boundary["new_final_action_created_in_this_package"])
            self.assertFalse(boundary["new_direct_command_created_in_this_package"])
            self.assertFalse(boundary["new_execution_created_in_this_package"])
            self.assertFalse(boundary["new_outcome_observation_created_in_this_package"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_feedback_record"]["source_validated"] = False

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_source_feedback_not_created_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_feedback_record"]["feedback_created"] = False

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn("source_feedback_created_not_expected", result["error_codes"])

    def test_source_feedback_already_applied_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_feedback_record"]["feedback_applied"] = True

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn("source_feedback_applied_not_expected", result["error_codes"])

    def test_bad_feedback_type_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_feedback_record"]["feedback_type"] = "unknown"

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn("source_feedback_type_not_application_eligible", result["error_codes"])

    def test_future_application_not_allowed_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["feedback_application_approval_boundary"]["future_feedback_application_allowed"] = False

        result = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn(
            "feedback_application_approval_boundary_future_feedback_application_allowed_not_expected",
            result["error_codes"],
        )

    def test_application_or_loop_true_blocks(self):
        for field in ("feedback_applied_in_this_package", "feedback_loop_created_in_this_package"):
            bad = copy.deepcopy(self.reach)
            bad["feedback_application_approval_boundary"][field] = True

            result = (
                validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"feedback_application_approval_boundary_{field}_not_expected", result["error_codes"])

    def test_reordering_or_score_change_true_blocks(self):
        for field in (
            "candidate_reordering_created_in_this_package",
            "candidate_scores_changed_in_this_package",
            "next_cycle_candidate_ordering_changed_in_this_package",
        ):
            bad = copy.deepcopy(self.wait)
            bad["feedback_application_approval_boundary"][field] = True

            result = (
                validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"feedback_application_approval_boundary_{field}_not_expected", result["error_codes"])

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
            bad["feedback_application_approval_boundary"][field] = True

            result = (
                validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"feedback_application_approval_boundary_{field}_not_expected", result["error_codes"])

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
                validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["feedback_application_approval_boundary_result_count"], 43)
        self.assertEqual(summary["valid_feedback_application_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_feedback_application_approval_boundary_count"], 40)
        self.assertEqual(summary["future_feedback_application_allowed_count"], 3)
        self.assertEqual(summary["positive_item_feedback_application_boundary_count"], 1)
        self.assertEqual(summary["wait_context_feedback_application_boundary_count"], 1)
        self.assertEqual(summary["mismatch_probe_feedback_application_boundary_count"], 1)
        self.assertEqual(summary["feedback_application_blocked_count"], 3)
        self.assertEqual(summary["feedback_loop_blocked_count"], 3)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-outcome-feedback-application-approval-boundary-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-sandbox-candidate-ordering-arbitration-outcome-feedback-application-approval-boundary-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
