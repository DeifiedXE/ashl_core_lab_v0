import copy
import unittest

from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_minimal import (
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_minimal_check,
)
from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationReorderedCandidateDirectCommandOutcomeObservationMinimalTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_minimal_check()[
            "valid_records"
        ]
        cls.result = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_minimal_check()
        )
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def assert_invalid(self, record: dict) -> list[str]:
        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_record(
                record
            )
        )
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])
        return result["error_codes"]

    def test_valid_outcome_observations_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = (
                validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_record(
                    record
                )
            )

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["outcome_observation"]["outcome_observation_created"])
            self.assertEqual(record["outcome_observation"]["outcome_scope"], "same_session_sandbox_only")

    def test_boundary_versions_are_b162_to_b163(self):
        boundary = self.result["boundary"]

        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b162")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b163")

    def test_default_builder_uses_b162_execution_source(self):
        record = build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_record()
        source = record["source_sandbox_execution"]
        observation = record["outcome_observation"]

        self.assertEqual(source["source_boundary_index"], "2026-06-09-b162")
        self.assertTrue(source["direct_command_executed"])
        self.assertTrue(source["sandbox_action_executed"])
        self.assertEqual(observation["direct_command"], source["direct_command"])

    def test_reach_front_item_outcome_observed(self):
        record = build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_record(
            self.sources[0]
        )
        observation = record["outcome_observation"]
        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_record(
                record
            )
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "item_reachable_feedback_prioritizes_reach")
        self.assertEqual(observation["direct_command"], "sandbox.arbitration.reach_front_item")
        self.assertEqual(observation["observed_outcome"], "front_item_reached")
        self.assertEqual(observation["outcome_label"], "arbitration_reordered_positive_item_contact_observed")

    def test_wait_or_observe_outcome_observed(self):
        observation = self.wait["outcome_observation"]
        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_record(
                self.wait
            )
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "item_not_afforded_blocks_feedback_priority")
        self.assertEqual(observation["direct_command"], "sandbox.arbitration.wait_or_observe")
        self.assertEqual(observation["observed_outcome"], "local_context_observed")
        self.assertEqual(observation["outcome_label"], "arbitration_reordered_wait_context_observed")

    def test_probe_outcome_observed(self):
        observation = self.probe["outcome_observation"]
        result = (
            validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_record(
                self.probe
            )
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "mismatch_feedback_outranks_retry_tendency")
        self.assertEqual(observation["direct_command"], "sandbox.arbitration.observe_or_alternative_probe")
        self.assertEqual(observation["observed_outcome"], "local_context_observed")
        self.assertEqual(observation["outcome_label"], "arbitration_reordered_mismatch_probe_context_observed")

    def test_observation_does_not_create_feedback_reordering_or_score_changes(self):
        for record in self.records:
            observation = record["outcome_observation"]

            self.assertFalse(observation["feedback_loop_created"])
            self.assertFalse(observation["candidate_reordering_created"])
            self.assertFalse(observation["candidate_scores_changed"])
            self.assertFalse(observation["runtime_next_cycle_candidate_ordering_changed"])
            self.assertTrue(observation["future_feedback_requires_separate_boundary"])
            self.assertTrue(observation["future_candidate_reordering_requires_separate_boundary"])

    def test_observation_does_not_create_actions_or_execution(self):
        for record in self.records:
            observation = record["outcome_observation"]

            self.assertFalse(observation["new_selected_action_created"])
            self.assertFalse(observation["new_final_action_created"])
            self.assertFalse(observation["new_direct_command_created"])
            self.assertFalse(observation["new_execution_created"])

    def test_source_execution_is_preserved(self):
        for record in self.records:
            source = record["source_sandbox_execution"]

            self.assertTrue(source["source_validated"])
            self.assertEqual(source["source_boundary_index"], "2026-06-09-b162")
            self.assertEqual(source["execution_scope"], "same_session_sandbox_only")
            self.assertTrue(source["direct_command_executed"])
            self.assertTrue(source["sandbox_action_executed"])
            self.assertFalse(source["source_outcome_observation_created"])
            self.assertTrue(source["source_arbitration_rules_preserved"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_sandbox_execution"]["source_validated"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("source_validated_not_true", errors)

    def test_source_must_have_executed_command(self):
        bad = copy.deepcopy(self.reach)
        bad["source_sandbox_execution"]["direct_command_executed"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("direct_command_executed_not_expected", errors)

    def test_wrong_observed_outcome_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["outcome_observation"]["observed_outcome"] = "unknown"

        errors = self.assert_invalid(bad)

        self.assertIn("outcome_observation_observed_outcome_not_expected", errors)

    def test_feedback_true_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["outcome_observation"]["feedback_loop_created"] = True

        errors = self.assert_invalid(bad)

        self.assertIn("outcome_observation_feedback_loop_created_not_expected", errors)

    def test_reordering_scores_runtime_and_action_creation_block(self):
        for field in (
            "candidate_reordering_created",
            "candidate_scores_changed",
            "runtime_next_cycle_candidate_ordering_changed",
            "new_selected_action_created",
            "new_final_action_created",
            "new_direct_command_created",
            "new_execution_created",
        ):
            bad = copy.deepcopy(self.wait)
            bad["outcome_observation"][field] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"outcome_observation_{field}_not_expected", errors)

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

            errors = self.assert_invalid(bad)

            self.assertIn(f"blocked_flags_{field}_not_false", errors)

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(summary["outcome_observation_result_count"], 84)
        self.assertEqual(summary["valid_outcome_observation_count"], 3)
        self.assertEqual(summary["invalid_outcome_observation_count"], 81)
        self.assertEqual(summary["outcome_observation_created_count"], 3)
        self.assertEqual(summary["same_session_sandbox_only_observation_count"], 3)
        self.assertEqual(summary["observation_budget_checked_count"], 3)
        self.assertEqual(summary["source_execution_preserved_count"], 3)
        self.assertEqual(summary["source_reordering_preserved_count"], 3)
        self.assertEqual(summary["reach_front_item_observation_count"], 1)
        self.assertEqual(summary["wait_or_observe_observation_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_observation_count"], 1)
        self.assertEqual(summary["positive_item_observation_count"], 1)
        self.assertEqual(summary["wait_context_observation_count"], 1)
        self.assertEqual(summary["mismatch_probe_observation_count"], 1)
        self.assertEqual(summary["feedback_loop_blocked_count"], 3)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["candidate_scores_blocked_count"], 3)
        self.assertEqual(summary["runtime_next_cycle_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-direct-command-outcome-observation-minimal-check"
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            result["flow"],
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_minimal_v0",
        )


if __name__ == "__main__":
    unittest.main()
