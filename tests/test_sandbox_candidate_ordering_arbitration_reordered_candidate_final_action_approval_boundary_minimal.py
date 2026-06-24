import unittest
from copy import deepcopy

from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_record,
)
from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_minimal import (
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_minimal_check,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationReorderedCandidateFinalActionApprovalBoundaryMinimalTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.sources = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_minimal_check()[
                "valid_records"
            ]
        )
        cls.result = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_minimal_check()
        )
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def assert_invalid(self, record: dict) -> list[str]:
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_record(
            record
        )
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])
        return result["error_codes"]

    def test_valid_final_action_approval_boundaries_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_record(
                    record
                )
            )
            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_boundary_versions_are_b156_to_b157(self):
        boundary = self.result["boundary"]
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b156")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b157")

    def test_default_builder_uses_reordered_candidate_selected_action_source(self):
        record = (
            build_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_record()
        )
        source = record["source_sandbox_selected_action"]
        boundary = record["final_action_approval_boundary"]

        self.assertEqual(source["source_boundary_index"], "2026-06-09-b156")
        self.assertEqual(source["selected_action_source"], "reordered_candidate_selected_action_approval_boundary")
        self.assertEqual(boundary["candidate_for_future_final_action"], source["selected_action"])

    def test_future_final_action_candidates_match_selected_actions(self):
        self.assertEqual(
            self.reach["final_action_approval_boundary"]["candidate_for_future_final_action"],
            "reach_front_item",
        )
        self.assertEqual(
            self.wait["final_action_approval_boundary"]["candidate_for_future_final_action"],
            "wait_or_observe",
        )
        self.assertEqual(
            self.probe["final_action_approval_boundary"]["candidate_for_future_final_action"],
            "observe_or_alternative_probe",
        )

    def test_source_selected_action_required(self):
        for record in self.records:
            source = record["source_sandbox_selected_action"]

            self.assertTrue(source["source_validated"])
            self.assertTrue(source["selected_action_created"])
            self.assertEqual(source["selected_action_scope"], "same_session_sandbox_only")
            self.assertEqual(
                source["selected_action_source"],
                "reordered_candidate_selected_action_approval_boundary",
            )
            self.assertTrue(source["source_reordering_preserved"])
            self.assertTrue(source["same_purpose_only"])
            self.assertTrue(source["arbitration_rules_preserved"])

    def test_boundary_does_not_create_final_action_command_execution_or_observation(self):
        for record in self.records:
            boundary = record["final_action_approval_boundary"]

            self.assertTrue(boundary["future_final_action_allowed"])
            self.assertFalse(boundary["final_action_created_in_this_package"])
            self.assertFalse(boundary["direct_command_created"])
            self.assertFalse(boundary["sandbox_execution_created"])
            self.assertFalse(boundary["new_outcome_observation_created"])
            self.assertFalse(boundary["execution_allowed_in_this_package"])

    def test_boundary_does_not_change_scores_ordering_or_feedback(self):
        for record in self.records:
            boundary = record["final_action_approval_boundary"]

            self.assertFalse(boundary["candidate_scores_changed"])
            self.assertFalse(boundary["runtime_next_cycle_candidate_ordering_changed"])
            self.assertFalse(boundary["feedback_loop_created"])

    def test_source_selected_action_not_created_blocks(self):
        bad = deepcopy(self.reach)
        bad["source_sandbox_selected_action"]["selected_action_created"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("source_selected_action_created_not_expected", errors)

    def test_source_already_has_final_action_or_execution_blocks(self):
        for field in (
            "source_final_action_created",
            "source_direct_command_created",
            "source_sandbox_execution_created",
            "source_new_outcome_observation_created",
            "source_execution_allowed_in_source_package",
        ):
            bad = deepcopy(self.reach)
            bad["source_sandbox_selected_action"][field] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"source_{field}_not_expected", errors)

    def test_bad_source_scope_or_candidate_blocks(self):
        bad_scope = deepcopy(self.reach)
        bad_scope["source_sandbox_selected_action"]["selected_action_scope"] = "production"
        self.assertIn(
            "source_selected_action_scope_not_expected",
            self.assert_invalid(bad_scope),
        )

        bad_candidate = deepcopy(self.reach)
        bad_candidate["source_sandbox_selected_action"]["selected_action"] = "wait_or_observe"
        self.assert_invalid(bad_candidate)

    def test_wrong_future_candidate_blocks(self):
        bad = deepcopy(self.reach)
        bad["final_action_approval_boundary"]["candidate_for_future_final_action"] = "wait_or_observe"

        errors = self.assert_invalid(bad)

        self.assertIn("final_action_approval_boundary_candidate_for_future_final_action_not_expected", errors)

    def test_future_final_action_not_allowed_blocks(self):
        bad = deepcopy(self.reach)
        bad["final_action_approval_boundary"]["future_final_action_allowed"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("final_action_approval_boundary_future_final_action_allowed_not_expected", errors)

    def test_final_action_created_blocks(self):
        bad = deepcopy(self.reach)
        bad["final_action_approval_boundary"]["final_action_created_in_this_package"] = True

        errors = self.assert_invalid(bad)

        self.assertIn("final_action_approval_boundary_final_action_created_in_this_package_not_expected", errors)

    def test_direct_command_execution_or_observation_blocks(self):
        for field in (
            "direct_command_created",
            "sandbox_execution_created",
            "new_outcome_observation_created",
            "execution_allowed_in_this_package",
        ):
            bad = deepcopy(self.reach)
            bad["final_action_approval_boundary"][field] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"final_action_approval_boundary_{field}_not_expected", errors)

    def test_score_runtime_feedback_blocks(self):
        for field in (
            "candidate_scores_changed",
            "runtime_next_cycle_candidate_ordering_changed",
            "feedback_loop_created",
        ):
            bad = deepcopy(self.wait)
            bad["final_action_approval_boundary"][field] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"final_action_approval_boundary_{field}_not_expected", errors)

    def test_memory_predictor_direct_feed_and_proof_flags_block(self):
        for flag in (
            "memory_write",
            "retention_write",
            "predictor_read_enabled",
            "predictor_influence_enabled",
            "predictor_modified",
            "direct_endocrine_feed",
            "direct_tendency_feed",
            "proof_of_learning_claim",
        ):
            bad = deepcopy(self.probe)
            bad["blocked_flags"][flag] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"blocked_flags_{flag}_not_false", errors)

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(summary["final_action_approval_boundary_result_count"], 58)
        self.assertEqual(summary["valid_final_action_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_final_action_approval_boundary_count"], 55)
        self.assertEqual(summary["future_final_action_allowed_count"], 3)
        self.assertEqual(summary["reach_front_item_final_action_candidate_count"], 1)
        self.assertEqual(summary["wait_or_observe_final_action_candidate_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_final_action_candidate_count"], 1)
        self.assertEqual(summary["final_action_creation_blocked_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["outcome_observation_blocked_count"], 3)
        self.assertEqual(summary["candidate_scores_blocked_count"], 3)
        self.assertEqual(summary["runtime_next_cycle_blocked_count"], 3)
        self.assertEqual(summary["feedback_loop_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["arbitration_rules_preserved_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-final-action-approval-boundary-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-final-action-approval-boundary-minimal-check",
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["valid_final_action_approval_boundary_count"], 3)


if __name__ == "__main__":
    unittest.main()
