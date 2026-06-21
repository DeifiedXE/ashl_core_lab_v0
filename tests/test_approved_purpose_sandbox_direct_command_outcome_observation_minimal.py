import copy
import unittest

from ashl_core.approved_purpose_sandbox_direct_command_execution_minimal import (
    run_approved_purpose_sandbox_direct_command_execution_minimal_check,
)
from ashl_core.approved_purpose_sandbox_direct_command_outcome_observation_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_approved_purpose_sandbox_direct_command_outcome_observation_record,
    run_approved_purpose_sandbox_direct_command_outcome_observation_minimal_check,
    validate_approved_purpose_sandbox_direct_command_outcome_observation_record,
)
from ashl_core.teaching_cli import run_command


class ApprovedPurposeSandboxDirectCommandOutcomeObservationMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_approved_purpose_sandbox_direct_command_execution_minimal_check()["valid_records"]
        cls.result = run_approved_purpose_sandbox_direct_command_outcome_observation_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.comfort = cls.records[2]

    def test_valid_outcome_observations_are_created(self):
        for record in self.records:
            result = validate_approved_purpose_sandbox_direct_command_outcome_observation_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(
                record["record_type"],
                "approved_purpose_sandbox_direct_command_outcome_observation_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["outcome_observation"]["outcome_observation_created"])
            self.assertEqual(record["outcome_observation"]["outcome_scope"], "sandbox_only")

    def test_reach_front_outcome_observed(self):
        record = build_approved_purpose_sandbox_direct_command_outcome_observation_record(self.sources[0])
        observation = record["outcome_observation"]
        result = validate_approved_purpose_sandbox_direct_command_outcome_observation_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "approach_or_reach_item")
        self.assertEqual(observation["direct_command"], "sandbox.approved_purpose.reach_front_item")
        self.assertEqual(observation["observed_outcome"], "front_item_reached")
        self.assertEqual(observation["outcome_label"], "positive_item_contact_observed")

    def test_probe_outcome_observed(self):
        observation = self.mismatch["outcome_observation"]
        result = validate_approved_purpose_sandbox_direct_command_outcome_observation_record(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "resolve_mismatch")
        self.assertEqual(observation["direct_command"], "sandbox.approved_purpose.observe_or_alternative_probe")
        self.assertEqual(observation["observed_outcome"], "local_context_observed")
        self.assertEqual(observation["outcome_label"], "mismatch_probe_context_observed")

    def test_support_outcome_observed(self):
        observation = self.comfort["outcome_observation"]
        result = validate_approved_purpose_sandbox_direct_command_outcome_observation_record(self.comfort)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "support_user_comfort")
        self.assertEqual(observation["direct_command"], "sandbox.approved_purpose.offer_low_pressure_support")
        self.assertEqual(observation["observed_outcome"], "low_pressure_support_offered")
        self.assertEqual(observation["outcome_label"], "bounded_support_trace_observed")

    def test_observation_does_not_create_feedback_or_reordering(self):
        for record in self.records:
            observation = record["outcome_observation"]

            self.assertFalse(observation["feedback_loop_created"])
            self.assertTrue(observation["future_feedback_requires_separate_boundary"])
            self.assertFalse(record["blocked_flags"]["feedback_loop_created"])
            self.assertFalse(record["blocked_flags"]["candidate_reordering_created"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_sandbox_execution"]["source_validated"] = False

        result = validate_approved_purpose_sandbox_direct_command_outcome_observation_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_source_must_have_executed_command(self):
        bad = copy.deepcopy(self.reward)
        bad["source_sandbox_execution"]["direct_command_executed"] = False

        result = validate_approved_purpose_sandbox_direct_command_outcome_observation_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("direct_command_executed_not_expected", result["error_codes"])

    def test_wrong_observed_outcome_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["outcome_observation"]["observed_outcome"] = "unknown"

        result = validate_approved_purpose_sandbox_direct_command_outcome_observation_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("outcome_observation_observed_outcome_not_expected", result["error_codes"])

    def test_feedback_true_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["outcome_observation"]["feedback_loop_created"] = True

        result = validate_approved_purpose_sandbox_direct_command_outcome_observation_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("outcome_observation_feedback_loop_created_not_expected", result["error_codes"])

    def test_memory_predictor_manipulation_and_proof_flags_block(self):
        for field in (
            "memory_write",
            "predictor_modified",
            "emotional_manipulation",
            "proof_of_learning_claim",
        ):
            bad = copy.deepcopy(self.comfort)
            bad["blocked_flags"][field] = True

            result = validate_approved_purpose_sandbox_direct_command_outcome_observation_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["outcome_observation_result_count"], 32)
        self.assertEqual(summary["valid_outcome_observation_count"], 3)
        self.assertEqual(summary["invalid_outcome_observation_count"], 29)
        self.assertEqual(summary["outcome_observation_created_count"], 3)
        self.assertEqual(summary["sandbox_only_observation_count"], 3)
        self.assertEqual(summary["observation_budget_checked_count"], 3)
        self.assertEqual(summary["approach_or_reach_item_observation_count"], 1)
        self.assertEqual(summary["resolve_mismatch_observation_count"], 1)
        self.assertEqual(summary["support_user_comfort_observation_count"], 1)
        self.assertEqual(summary["feedback_loop_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-approved-purpose-sandbox-direct-command-outcome-observation-minimal-check")

        self.assertEqual(
            result["command"],
            "run-approved-purpose-sandbox-direct-command-outcome-observation-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
