import unittest

from ashl_core.level2_sandbox_dry_run_observation_evaluation_summary_minimal import (
    EVALUATION_BLOCKED,
    EVALUATION_FAILED,
    EVALUATION_INCONCLUSIVE,
    EVALUATION_PASSED,
    NOT_CLAIMED,
    build_level2_sandbox_dry_run_evaluation_record,
    build_level2_sandbox_dry_run_human_review_summary,
    build_level2_sandbox_dry_run_observation_record,
    build_level2_sandbox_dry_run_record,
    run_level2_sandbox_dry_run_observation_evaluation_summary_minimal_check,
    validate_level2_sandbox_dry_run_evaluation_record,
    validate_level2_sandbox_dry_run_human_review_summary,
    validate_level2_sandbox_dry_run_observation_record,
    validate_level2_sandbox_dry_run_record,
)
from ashl_core.teaching_cli import run_command


class Level2SandboxDryRunObservationEvaluationSummaryMinimalTests(unittest.TestCase):
    def setUp(self):
        self.dry_run = build_level2_sandbox_dry_run_record()
        self.observation = build_level2_sandbox_dry_run_observation_record(self.dry_run)
        self.evaluation = build_level2_sandbox_dry_run_evaluation_record(self.observation)
        self.summary = build_level2_sandbox_dry_run_human_review_summary(self.evaluation)

    def test_valid_dry_run_builds_from_valid_upstream_records(self):
        result = validate_level2_sandbox_dry_run_record(self.dry_run)

        self.assertTrue(result["valid"])
        self.assertEqual("level2_sandbox_dry_run", self.dry_run["record_type"])
        self.assertTrue(self.dry_run["dry_run_only"])
        self.assertTrue(self.dry_run["source_scenario_plan_valid"])
        self.assertTrue(self.dry_run["source_design_envelope_valid"])

    def test_dry_run_rejects_missing_design_envelope(self):
        record = build_level2_sandbox_dry_run_record()
        record["source_design_envelope_valid"] = False

        self.assertIn("source_design_envelope_valid_not_true", self._dry_run_errors(record))

    def test_dry_run_rejects_missing_scenario_plan(self):
        record = build_level2_sandbox_dry_run_record()
        record["source_scenario_plan_valid"] = False

        self.assertIn("source_scenario_plan_valid_not_true", self._dry_run_errors(record))

    def test_dry_run_rejects_outside_envelope_scenario(self):
        record = build_level2_sandbox_dry_run_record()
        record["scenario_inside_design_envelope"] = False

        self.assertIn("scenario_inside_design_envelope_not_true", self._dry_run_errors(record))

    def test_dry_run_rejects_level2_application_claim(self):
        self.assert_dry_run_false_field_blocks("level2_application_performed")

    def test_dry_run_rejects_level2_execution_claim(self):
        self.assert_dry_run_false_field_blocks("level2_execution_performed")

    def test_runtime_behavior_remains_blocked(self):
        self.assert_dry_run_false_field_blocks("runtime_behavior_changed")

    def test_memory_and_retained_jsonl_writes_remain_blocked(self):
        self.assert_dry_run_false_field_blocks("memory_written")
        self.assert_dry_run_false_field_blocks("retained_jsonl_written")

    def test_retention_write_remains_blocked(self):
        self.assert_dry_run_false_field_blocks("retention_written")

    def test_predictor_mutation_remains_blocked(self):
        self.assert_dry_run_false_field_blocks("predictor_mutated")

    def test_selected_action_final_action_direct_command_remain_blocked(self):
        self.assert_dry_run_false_field_blocks("selected_action_created")
        self.assert_dry_run_false_field_blocks("final_action_created")
        self.assert_dry_run_false_field_blocks("direct_command_created")

    def test_production_claim_remains_blocked(self):
        self.assert_dry_run_false_field_blocks("production_behavior_changed")

    def test_proof_of_learning_claim_remains_blocked(self):
        self.assert_dry_run_false_field_blocks("proof_of_learning_claimed")

    def test_observation_requires_valid_dry_run(self):
        invalid_dry_run = build_level2_sandbox_dry_run_record()
        invalid_dry_run["level2_application_performed"] = True
        observation = build_level2_sandbox_dry_run_observation_record(invalid_dry_run)

        self.assertIn("source_dry_run_valid_not_true", self._observation_errors(observation))

    def test_valid_observation_passes(self):
        result = validate_level2_sandbox_dry_run_observation_record(self.observation)

        self.assertTrue(result["valid"])
        self.assertTrue(self.observation["observation_only"])
        self.assertTrue(self.observation["observed_no_level2_application"])

    def test_evaluation_requires_valid_observation_for_pass(self):
        observation = build_level2_sandbox_dry_run_observation_record()
        observation["observed_no_memory_write"] = False
        evaluation = build_level2_sandbox_dry_run_evaluation_record(observation, EVALUATION_PASSED)

        self.assertIn("passed_source_observation_valid_not_true", self._evaluation_errors(evaluation))

    def test_valid_evaluation_passes(self):
        result = validate_level2_sandbox_dry_run_evaluation_record(self.evaluation)

        self.assertTrue(result["valid"])
        self.assertEqual(EVALUATION_PASSED, self.evaluation["evaluation_status"])
        self.assertFalse(self.evaluation["passing_evaluation_authorizes_level2_application"])

    def test_evaluation_supports_fail_inconclusive_and_blocked_statuses(self):
        failed = build_level2_sandbox_dry_run_evaluation_record(self.observation, EVALUATION_FAILED)
        inconclusive = build_level2_sandbox_dry_run_evaluation_record({}, EVALUATION_INCONCLUSIVE)
        blocked_observation = build_level2_sandbox_dry_run_observation_record()
        blocked_observation["observed_no_memory_write"] = False
        blocked = build_level2_sandbox_dry_run_evaluation_record(blocked_observation)

        self.assertTrue(validate_level2_sandbox_dry_run_evaluation_record(failed)["valid"])
        self.assertTrue(validate_level2_sandbox_dry_run_evaluation_record(inconclusive)["valid"])
        self.assertEqual(EVALUATION_BLOCKED, blocked["evaluation_status"])
        self.assertTrue(validate_level2_sandbox_dry_run_evaluation_record(blocked)["valid"])

    def test_human_review_summary_is_conservative(self):
        result = validate_level2_sandbox_dry_run_human_review_summary(self.summary)

        self.assertTrue(result["valid"])
        self.assertEqual("conservative_human_review", self.summary["summary_type"])
        self.assertEqual(set(NOT_CLAIMED), set(self.summary["not_claimed"]))

    def test_human_review_summary_does_not_claim_proof_of_learning(self):
        summary = build_level2_sandbox_dry_run_human_review_summary()
        summary["proof_of_learning_claimed"] = True

        self.assertIn("proof_of_learning_claimed_not_false", self._summary_errors(summary))

    def test_passing_evaluation_does_not_authorize_level2_application(self):
        evaluation = build_level2_sandbox_dry_run_evaluation_record()
        evaluation["passing_evaluation_authorizes_level2_application"] = True

        self.assertIn("passing_evaluation_authorizes_level2_application_not_false", self._evaluation_errors(evaluation))

    def test_passing_tests_and_task_queue_completion_do_not_count_as_approval_or_proof(self):
        record = build_level2_sandbox_dry_run_record()
        record["task_queue_completed_status_is_approval"] = True
        record["passing_tests_are_proof_of_learning"] = True

        errors = self._dry_run_errors(record)
        self.assertIn("task_queue_completed_status_is_approval_not_false", errors)
        self.assertIn("passing_tests_are_proof_of_learning_not_false", errors)

    def test_cli_path_returns_ok(self):
        result = run_command("run-level2-sandbox-dry-run-observation-evaluation-summary-minimal-check")

        self.assertEqual("ok", result["status"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = run_level2_sandbox_dry_run_observation_evaluation_summary_minimal_check()["summary"]

        self.assertEqual(1, summary["valid_level2_sandbox_dry_run_count"])
        self.assertEqual(1, summary["valid_level2_sandbox_dry_run_observation_count"])
        self.assertEqual(1, summary["valid_level2_sandbox_dry_run_evaluation_count"])
        self.assertEqual(1, summary["valid_level2_sandbox_dry_run_human_review_summary_count"])
        self.assertGreaterEqual(summary["invalid_level2_sandbox_dry_run_count"], 1)
        self.assertGreaterEqual(summary["level2_application_blocked_count"], 1)
        self.assertGreaterEqual(summary["level2_execution_blocked_count"], 1)
        self.assertGreaterEqual(summary["forbidden_runtime_memory_predictor_claim_blocked_count"], 1)
        self.assertGreaterEqual(summary["proof_of_learning_claim_blocked_count"], 1)

    def assert_dry_run_false_field_blocks(self, field):
        record = build_level2_sandbox_dry_run_record()
        record[field] = True

        self.assertIn(f"{field}_not_false", self._dry_run_errors(record))

    def _dry_run_errors(self, record):
        return validate_level2_sandbox_dry_run_record(record)["error_codes"]

    def _observation_errors(self, record):
        return validate_level2_sandbox_dry_run_observation_record(record)["error_codes"]

    def _evaluation_errors(self, record):
        return validate_level2_sandbox_dry_run_evaluation_record(record)["error_codes"]

    def _summary_errors(self, record):
        return validate_level2_sandbox_dry_run_human_review_summary(record)["error_codes"]


if __name__ == "__main__":
    unittest.main()
