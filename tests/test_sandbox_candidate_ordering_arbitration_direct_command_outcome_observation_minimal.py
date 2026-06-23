import copy
import unittest

from ashl_core.sandbox_candidate_ordering_arbitration_direct_command_execution_minimal import (
    run_sandbox_candidate_ordering_arbitration_direct_command_execution_minimal_check,
)
from ashl_core.sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record,
    run_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationDirectCommandOutcomeObservationMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_direct_command_execution_minimal_check()[
            "valid_records"
        ]
        cls.result = run_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_outcome_observations_are_created(self):
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(
                record
            )

            self.assertTrue(result["valid"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["outcome_observation"]["outcome_observation_created"])
            self.assertEqual(record["outcome_observation"]["outcome_scope"], "sandbox_only")

    def test_reach_front_item_outcome_observed(self):
        record = build_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(
            self.sources[0]
        )
        observation = record["outcome_observation"]
        result = validate_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(
            record
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "item_reachable_feedback_prioritizes_reach")
        self.assertEqual(observation["direct_command"], "sandbox.arbitration.reach_front_item")
        self.assertEqual(observation["observed_outcome"], "front_item_reached")
        self.assertEqual(observation["outcome_label"], "arbitration_positive_item_contact_observed")

    def test_wait_or_observe_outcome_observed(self):
        observation = self.wait["outcome_observation"]
        result = validate_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(
            self.wait
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "item_not_afforded_blocks_feedback_priority")
        self.assertEqual(observation["direct_command"], "sandbox.arbitration.wait_or_observe")
        self.assertEqual(observation["observed_outcome"], "local_context_observed")
        self.assertEqual(observation["outcome_label"], "arbitration_wait_context_observed")

    def test_probe_outcome_observed(self):
        observation = self.probe["outcome_observation"]
        result = validate_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(
            self.probe
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "mismatch_feedback_outranks_retry_tendency")
        self.assertEqual(observation["direct_command"], "sandbox.arbitration.observe_or_alternative_probe")
        self.assertEqual(observation["observed_outcome"], "local_context_observed")
        self.assertEqual(observation["outcome_label"], "arbitration_mismatch_probe_context_observed")

    def test_observation_does_not_create_feedback_or_reordering(self):
        for record in self.records:
            observation = record["outcome_observation"]

            self.assertFalse(observation["feedback_loop_created"])
            self.assertTrue(observation["future_feedback_requires_separate_boundary"])
            self.assertFalse(record["blocked_flags"]["feedback_loop_created"])
            self.assertFalse(record["blocked_flags"]["candidate_reordering_created"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_sandbox_execution"]["source_validated"] = False

        result = validate_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_source_must_have_executed_command(self):
        bad = copy.deepcopy(self.reach)
        bad["source_sandbox_execution"]["direct_command_executed"] = False

        result = validate_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn("direct_command_executed_not_expected", result["error_codes"])

    def test_wrong_observed_outcome_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["outcome_observation"]["observed_outcome"] = "unknown"

        result = validate_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn("outcome_observation_observed_outcome_not_expected", result["error_codes"])

    def test_feedback_true_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["outcome_observation"]["feedback_loop_created"] = True

        result = validate_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(
            bad
        )

        self.assertFalse(result["valid"])
        self.assertIn("outcome_observation_feedback_loop_created_not_expected", result["error_codes"])

    def test_memory_predictor_direct_feed_and_proof_flags_block(self):
        for field in (
            "memory_write",
            "predictor_modified",
            "direct_endocrine_feed",
            "direct_tendency_feed",
            "proof_of_learning_claim",
        ):
            bad = copy.deepcopy(self.probe)
            bad["blocked_flags"][field] = True

            result = validate_sandbox_candidate_ordering_arbitration_direct_command_outcome_observation_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["outcome_observation_result_count"], 35)
        self.assertEqual(summary["valid_outcome_observation_count"], 3)
        self.assertEqual(summary["invalid_outcome_observation_count"], 32)
        self.assertEqual(summary["outcome_observation_created_count"], 3)
        self.assertEqual(summary["sandbox_only_observation_count"], 3)
        self.assertEqual(summary["observation_budget_checked_count"], 3)
        self.assertEqual(summary["reach_front_item_observation_count"], 1)
        self.assertEqual(summary["wait_or_observe_observation_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_observation_count"], 1)
        self.assertEqual(summary["feedback_loop_blocked_count"], 3)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-direct-command-outcome-observation-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-sandbox-candidate-ordering-arbitration-direct-command-outcome-observation-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
