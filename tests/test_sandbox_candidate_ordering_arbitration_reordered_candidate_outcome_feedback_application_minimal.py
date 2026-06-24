import copy
import unittest

from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_approval_boundary_minimal import (
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_approval_boundary_minimal_check,
)
from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationReorderedCandidateOutcomeFeedbackApplicationMinimalTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.sources = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_approval_boundary_minimal_check()[
                "valid_records"
            ]
        )
        cls.result = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_minimal_check()
        )
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_feedback_application_records_are_created(self):
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
                record
            )

            self.assertTrue(result["valid"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_minimal",
            )
            self.assertEqual(record["boundary_index_before"], BOUNDARY_INDEX_BEFORE)
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["same_session_feedback_application"]["feedback_application_created"])
            self.assertTrue(record["same_session_feedback_application"]["feedback_applied"])
            self.assertEqual(
                record["same_session_feedback_application"]["feedback_application_effect_scope"],
                "record_only_no_ordering_change",
            )

    def test_default_builder_uses_b166_application_boundary_source(self):
        record = build_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record()
        source = record["source_feedback_application_approval_boundary"]
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
            record
        )

        self.assertTrue(result["valid"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b166")
        self.assertTrue(source["future_feedback_application_allowed"])
        self.assertFalse(source["feedback_applied_in_source_package"])

    def test_reach_front_item_feedback_application_record_created(self):
        record = build_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
            self.sources[0]
        )
        application = record["same_session_feedback_application"]
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
            record
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "item_reachable_feedback_prioritizes_reach")
        self.assertEqual(
            application["feedback_application_type"],
            "arbitration_reordered_positive_item_contact_feedback_application",
        )

    def test_wait_context_feedback_application_record_created(self):
        application = self.wait["same_session_feedback_application"]
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
            self.wait
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "item_not_afforded_blocks_feedback_priority")
        self.assertEqual(
            application["feedback_application_type"],
            "arbitration_reordered_wait_context_observation_feedback_application",
        )

    def test_probe_feedback_application_record_created(self):
        application = self.probe["same_session_feedback_application"]
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
            self.probe
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "mismatch_feedback_outranks_retry_tendency")
        self.assertEqual(
            application["feedback_application_type"],
            "arbitration_reordered_mismatch_probe_context_feedback_application",
        )

    def test_application_does_not_create_loop_or_reordering(self):
        for record in self.records:
            application = record["same_session_feedback_application"]

            self.assertTrue(application["feedback_applied"])
            self.assertEqual(application["feedback_application_effect_scope"], "record_only_no_ordering_change")
            self.assertFalse(application["feedback_loop_created"])
            self.assertFalse(application["candidate_reordering_created"])
            self.assertFalse(application["candidate_scores_changed"])
            self.assertFalse(application["next_cycle_candidate_ordering_changed"])
            self.assertTrue(application["future_candidate_reordering_requires_separate_boundary"])

    def test_application_does_not_create_action_command_execution_or_observation(self):
        for record in self.records:
            application = record["same_session_feedback_application"]

            self.assertFalse(application["new_action_created"])
            self.assertFalse(application["new_selected_action_created"])
            self.assertFalse(application["new_final_action_created"])
            self.assertFalse(application["new_direct_command_created"])
            self.assertFalse(application["new_execution_created"])
            self.assertFalse(application["new_outcome_observation_created"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_feedback_application_approval_boundary"]["source_validated"] = False

        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_source_without_future_application_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_feedback_application_approval_boundary"]["future_feedback_application_allowed"] = False

        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn("source_future_feedback_application_allowed_not_expected", result["error_codes"])

    def test_source_already_applied_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_feedback_application_approval_boundary"]["feedback_applied_in_source_package"] = True

        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn("source_feedback_applied_in_source_package_not_expected", result["error_codes"])

    def test_application_not_created_or_not_applied_blocks(self):
        for field in ("feedback_application_created", "feedback_applied"):
            bad = copy.deepcopy(self.reach)
            bad["same_session_feedback_application"][field] = False

            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"same_session_feedback_application_{field}_not_expected", result["error_codes"])

    def test_wrong_effect_scope_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["same_session_feedback_application"]["feedback_application_effect_scope"] = "ordering_change"

        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn(
            "same_session_feedback_application_feedback_application_effect_scope_not_expected",
            result["error_codes"],
        )

    def test_loop_or_reordering_true_blocks(self):
        for field in (
            "feedback_loop_created",
            "candidate_reordering_created",
            "candidate_scores_changed",
            "next_cycle_candidate_ordering_changed",
        ):
            bad = copy.deepcopy(self.wait)
            bad["same_session_feedback_application"][field] = True

            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"same_session_feedback_application_{field}_not_expected", result["error_codes"])

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
            bad["same_session_feedback_application"][field] = True

            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"same_session_feedback_application_{field}_not_expected", result["error_codes"])

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
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_application_record(
                    bad
                )
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["feedback_application_result_count"], 48)
        self.assertEqual(summary["valid_feedback_application_count"], 3)
        self.assertEqual(summary["invalid_feedback_application_count"], 45)
        self.assertEqual(summary["feedback_application_created_count"], 3)
        self.assertEqual(summary["feedback_applied_count"], 3)
        self.assertEqual(summary["record_only_application_count"], 3)
        self.assertEqual(summary["positive_item_feedback_application_count"], 1)
        self.assertEqual(summary["wait_context_feedback_application_count"], 1)
        self.assertEqual(summary["mismatch_probe_feedback_application_count"], 1)
        self.assertEqual(summary["feedback_loop_blocked_count"], 3)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-outcome-feedback-application-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-outcome-feedback-application-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
