import unittest
from copy import deepcopy

from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_record,
)
from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal import (
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal_check,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationReorderedCandidateDirectCommandExecutionApprovalBoundaryMinimalTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal_check()[
            "valid_records"
        ]
        cls.result = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_minimal_check()
        )
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def assert_invalid(self, record: dict) -> list[str]:
        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_record(
                record
            )
        )
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])
        return result["error_codes"]

    def test_valid_execution_approval_boundaries_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_record(
                    record
                )
            )
            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["execution_approval_boundary"]["future_execution_allowed"])

    def test_boundary_versions_are_b160_to_b161(self):
        boundary = self.result["boundary"]

        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b160")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b161")

    def test_default_builder_uses_reordered_direct_command_source(self):
        record = (
            build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_record()
        )
        source = record["source_sandbox_direct_command"]
        boundary = record["execution_approval_boundary"]

        self.assertEqual(source["source_boundary_index"], "2026-06-09-b160")
        self.assertTrue(source["direct_command_created"])
        self.assertEqual(source["direct_command_scope"], "same_session_sandbox_only")
        self.assertEqual(boundary["candidate_for_future_execution"], source["direct_command"])

    def test_direct_commands_can_enter_future_execution(self):
        self.assertEqual(
            self.reach["execution_approval_boundary"]["candidate_for_future_execution"],
            "sandbox.arbitration.reach_front_item",
        )
        self.assertEqual(
            self.wait["execution_approval_boundary"]["candidate_for_future_execution"],
            "sandbox.arbitration.wait_or_observe",
        )
        self.assertEqual(
            self.probe["execution_approval_boundary"]["candidate_for_future_execution"],
            "sandbox.arbitration.observe_or_alternative_probe",
        )

    def test_boundary_does_not_execute_or_observe_outcome(self):
        for record in self.records:
            boundary = record["execution_approval_boundary"]

            self.assertTrue(boundary["future_execution_allowed"])
            self.assertEqual(boundary["execution_scope"], "same_session_sandbox_only")
            self.assertFalse(boundary["sandbox_execution_created_in_this_package"])
            self.assertFalse(boundary["execution_result_created_in_this_package"])
            self.assertFalse(boundary["new_outcome_observation_created_in_this_package"])
            self.assertTrue(boundary["future_outcome_observation_requires_separate_boundary"])

    def test_boundary_does_not_change_scores_ordering_feedback_or_actions(self):
        for record in self.records:
            boundary = record["execution_approval_boundary"]

            self.assertFalse(boundary["candidate_scores_changed_in_this_package"])
            self.assertFalse(boundary["runtime_next_cycle_candidate_ordering_changed_in_this_package"])
            self.assertFalse(boundary["feedback_loop_created_in_this_package"])
            self.assertFalse(boundary["selected_action_created_in_this_package"])
            self.assertFalse(boundary["final_action_created_in_this_package"])
            self.assertFalse(boundary["new_direct_command_created_in_this_package"])

    def test_source_direct_command_is_preserved(self):
        for record in self.records:
            source = record["source_sandbox_direct_command"]

            self.assertTrue(source["source_validated"])
            self.assertEqual(source["source_boundary_index"], "2026-06-09-b160")
            self.assertTrue(source["direct_command_created"])
            self.assertEqual(source["direct_command_scope"], "same_session_sandbox_only")
            self.assertFalse(source["source_sandbox_execution_created"])
            self.assertEqual(source["source_execution_count"], 0)
            self.assertFalse(source["source_new_outcome_observation_created"])
            self.assertTrue(source["source_arbitration_rules_preserved"])

    def test_bad_source_blocks(self):
        bad = deepcopy(self.reach)
        bad["source_sandbox_direct_command"]["source_validated"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("source_validated_not_true", errors)

    def test_source_direct_command_created_false_blocks(self):
        bad = deepcopy(self.reach)
        bad["source_sandbox_direct_command"]["direct_command_created"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("source_direct_command_created_not_expected", errors)

    def test_source_execution_state_blocks(self):
        for field, value in (
            ("source_sandbox_execution_created", True),
            ("source_execution_count", 1),
            ("source_new_outcome_observation_created", True),
        ):
            bad = deepcopy(self.reach)
            bad["source_sandbox_direct_command"][field] = value

            errors = self.assert_invalid(bad)

            self.assertIn(f"source_{field}_not_expected", errors)

    def test_future_execution_not_allowed_blocks(self):
        bad = deepcopy(self.reach)
        bad["execution_approval_boundary"]["future_execution_allowed"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("execution_approval_boundary_future_execution_allowed_not_expected", errors)

    def test_wrong_future_execution_blocks(self):
        bad = deepcopy(self.reach)
        bad["execution_approval_boundary"]["candidate_for_future_execution"] = "sandbox.bad"

        errors = self.assert_invalid(bad)

        self.assertIn("execution_approval_boundary_candidate_for_future_execution_not_expected", errors)

    def test_execution_result_or_outcome_created_blocks(self):
        for field in (
            "sandbox_execution_created_in_this_package",
            "execution_result_created_in_this_package",
            "new_outcome_observation_created_in_this_package",
        ):
            bad = deepcopy(self.reach)
            bad["execution_approval_boundary"][field] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"execution_approval_boundary_{field}_not_expected", errors)

    def test_score_runtime_feedback_and_action_creation_blocks(self):
        for field in (
            "candidate_scores_changed_in_this_package",
            "runtime_next_cycle_candidate_ordering_changed_in_this_package",
            "feedback_loop_created_in_this_package",
            "selected_action_created_in_this_package",
            "final_action_created_in_this_package",
            "new_direct_command_created_in_this_package",
        ):
            bad = deepcopy(self.wait)
            bad["execution_approval_boundary"][field] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"execution_approval_boundary_{field}_not_expected", errors)

    def test_future_boundaries_are_required(self):
        for field in (
            "future_outcome_observation_requires_separate_boundary",
            "future_feedback_requires_separate_boundary",
            "future_memory_write_requires_separate_boundary",
            "future_retention_requires_separate_boundary",
            "future_predictor_influence_requires_separate_boundary",
            "future_production_promotion_requires_separate_boundary",
        ):
            bad = deepcopy(self.reach)
            bad["execution_approval_boundary"][field] = False

            errors = self.assert_invalid(bad)

            self.assertIn(f"execution_approval_boundary_{field}_not_expected", errors)

    def test_memory_predictor_direct_feed_and_proof_flags_block(self):
        for flag in (
            "memory_write",
            "retention_write",
            "persistent_feedback_written",
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

        self.assertEqual(summary["execution_approval_boundary_result_count"], 71)
        self.assertEqual(summary["valid_execution_approval_boundary_count"], 3)
        self.assertEqual(summary["invalid_execution_approval_boundary_count"], 68)
        self.assertEqual(summary["future_execution_allowed_count"], 3)
        self.assertEqual(summary["source_direct_command_preserved_count"], 3)
        self.assertEqual(summary["source_reordering_preserved_count"], 3)
        self.assertEqual(summary["reach_front_item_execution_candidate_count"], 1)
        self.assertEqual(summary["wait_or_observe_execution_candidate_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_execution_candidate_count"], 1)
        self.assertEqual(summary["execution_creation_blocked_count"], 3)
        self.assertEqual(summary["outcome_observation_blocked_count"], 3)
        self.assertEqual(summary["candidate_scores_blocked_count"], 3)
        self.assertEqual(summary["runtime_next_cycle_blocked_count"], 3)
        self.assertEqual(summary["feedback_loop_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["arbitration_rules_preserved_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-direct-command-execution-approval-boundary-minimal-check"
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            result["flow"],
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_minimal_v0",
        )


if __name__ == "__main__":
    unittest.main()
