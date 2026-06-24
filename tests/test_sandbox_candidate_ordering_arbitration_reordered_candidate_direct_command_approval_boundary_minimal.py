import unittest
from copy import deepcopy

from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_record,
)
from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_minimal import (
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_minimal_check,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationReorderedCandidateDirectCommandApprovalBoundaryMinimalTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_minimal_check()[
            "valid_records"
        ]
        cls.result = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_minimal_check()
        )
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def assert_invalid(self, record: dict) -> list[str]:
        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_record(
                record
            )
        )
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])
        return result["error_codes"]

    def test_valid_direct_command_approval_boundaries_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_record(
                    record
                )
            )
            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_boundary_versions_are_b158_to_b159(self):
        boundary = self.result["boundary"]
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b158")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b159")

    def test_default_builder_uses_reordered_final_action_source(self):
        record = (
            build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_record()
        )
        source = record["source_sandbox_final_action"]
        boundary = record["direct_command_approval_boundary"]

        self.assertEqual(source["source_boundary_index"], "2026-06-09-b158")
        self.assertTrue(source["final_action_created"])
        self.assertEqual(source["final_action_scope"], "same_session_sandbox_only")
        self.assertEqual(boundary["candidate_for_future_direct_command"], source["direct_command"])

    def test_future_direct_commands_match_final_actions(self):
        self.assertEqual(
            self.reach["direct_command_approval_boundary"]["candidate_for_future_direct_command"],
            "sandbox.arbitration.reach_front_item",
        )
        self.assertEqual(
            self.wait["direct_command_approval_boundary"]["candidate_for_future_direct_command"],
            "sandbox.arbitration.wait_or_observe",
        )
        self.assertEqual(
            self.probe["direct_command_approval_boundary"]["candidate_for_future_direct_command"],
            "sandbox.arbitration.observe_or_alternative_probe",
        )

    def test_source_final_action_required(self):
        for record in self.records:
            source = record["source_sandbox_final_action"]

            self.assertTrue(source["source_validated"])
            self.assertTrue(source["final_action_created"])
            self.assertEqual(source["final_action_scope"], "same_session_sandbox_only")
            self.assertEqual(source["final_action_source"], "reordered_candidate_final_action_approval_boundary")
            self.assertEqual(source["final_action"], source["selected_action"])
            self.assertTrue(source["source_reordering_preserved"])
            self.assertTrue(source["same_purpose_only"])
            self.assertTrue(source["arbitration_rules_preserved"])

    def test_boundary_does_not_create_command_execution_or_observation(self):
        for record in self.records:
            boundary = record["direct_command_approval_boundary"]

            self.assertTrue(boundary["future_direct_command_allowed"])
            self.assertFalse(boundary["direct_command_created_in_this_package"])
            self.assertFalse(boundary["sandbox_execution_created"])
            self.assertFalse(boundary["new_outcome_observation_created"])
            self.assertFalse(boundary["execution_allowed_in_this_package"])
            self.assertTrue(boundary["future_execution_requires_separate_boundary"])
            self.assertTrue(boundary["future_outcome_observation_requires_separate_boundary"])

    def test_boundary_does_not_change_scores_ordering_or_feedback(self):
        for record in self.records:
            boundary = record["direct_command_approval_boundary"]

            self.assertFalse(boundary["candidate_scores_changed"])
            self.assertFalse(boundary["runtime_next_cycle_candidate_ordering_changed"])
            self.assertFalse(boundary["feedback_loop_created"])

    def test_bad_source_blocks(self):
        bad = deepcopy(self.reach)
        bad["source_sandbox_final_action"]["source_validated"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("source_validated_not_true", errors)

    def test_source_final_action_not_created_blocks(self):
        bad = deepcopy(self.reach)
        bad["source_sandbox_final_action"]["final_action_created"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("source_final_action_created_not_expected", errors)

    def test_source_wrong_direct_command_blocks(self):
        bad = deepcopy(self.reach)
        bad["source_sandbox_final_action"]["direct_command"] = "sandbox.bad"

        errors = self.assert_invalid(bad)

        self.assertIn("source_direct_command_not_from_final_action", errors)

    def test_future_direct_command_not_allowed_blocks(self):
        bad = deepcopy(self.reach)
        bad["direct_command_approval_boundary"]["future_direct_command_allowed"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("direct_command_approval_boundary_future_direct_command_allowed_not_expected", errors)

    def test_wrong_future_command_blocks(self):
        bad = deepcopy(self.reach)
        bad["direct_command_approval_boundary"]["candidate_for_future_direct_command"] = "sandbox.bad"

        errors = self.assert_invalid(bad)

        self.assertIn("direct_command_approval_boundary_candidate_for_future_direct_command_not_expected", errors)

    def test_direct_command_created_blocks(self):
        bad = deepcopy(self.reach)
        bad["direct_command_approval_boundary"]["direct_command_created_in_this_package"] = True

        errors = self.assert_invalid(bad)

        self.assertIn("direct_command_approval_boundary_direct_command_created_in_this_package_not_expected", errors)

    def test_execution_or_observation_blocks(self):
        for field in (
            "sandbox_execution_created",
            "new_outcome_observation_created",
            "execution_allowed_in_this_package",
        ):
            bad = deepcopy(self.reach)
            bad["direct_command_approval_boundary"][field] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"direct_command_approval_boundary_{field}_not_expected", errors)

    def test_score_runtime_feedback_blocks(self):
        for field in (
            "candidate_scores_changed",
            "runtime_next_cycle_candidate_ordering_changed",
            "feedback_loop_created",
        ):
            bad = deepcopy(self.wait)
            bad["direct_command_approval_boundary"][field] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"direct_command_approval_boundary_{field}_not_expected", errors)

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

        self.assertEqual(summary["direct_command_approval_boundary_result_count"], 69)
        self.assertEqual(summary["valid_direct_command_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_direct_command_approval_boundary_count"], 66)
        self.assertEqual(summary["future_direct_command_allowed_count"], 3)
        self.assertEqual(summary["source_final_action_preserved_count"], 3)
        self.assertEqual(summary["source_reordering_preserved_count"], 3)
        self.assertEqual(summary["reach_front_item_direct_command_candidate_count"], 1)
        self.assertEqual(summary["wait_or_observe_direct_command_candidate_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_direct_command_candidate_count"], 1)
        self.assertEqual(summary["direct_command_creation_blocked_count"], 3)
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
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-direct-command-approval-boundary-minimal-check"
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            result["flow"],
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_minimal_v0",
        )


if __name__ == "__main__":
    unittest.main()
