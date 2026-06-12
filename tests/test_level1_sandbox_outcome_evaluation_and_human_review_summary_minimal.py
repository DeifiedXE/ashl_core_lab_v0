import unittest

from ashl_core.level1_sandbox_lesson_application_outcome_observation_minimal import (
    build_level1_sandbox_lesson_application_outcome_observation,
)
from ashl_core.level1_sandbox_outcome_evaluation_and_human_review_summary_minimal import (
    FORBIDDEN_EFFECTS,
    PASS_RESULT,
    SAFE_CLAIM,
    STATUS_FAILED,
    STATUS_INCONCLUSIVE,
    STATUS_PASSED,
    build_level1_sandbox_outcome_evaluation_and_human_review_summary,
    run_level1_sandbox_outcome_evaluation_and_human_review_summary_minimal_check,
    validate_level1_sandbox_outcome_evaluation_and_human_review_summary,
)
from ashl_core.teaching_cli import run_command


class Level1SandboxOutcomeEvaluationAndHumanReviewSummaryMinimalTests(unittest.TestCase):
    def setUp(self):
        self.source = build_level1_sandbox_lesson_application_outcome_observation()
        self.record = build_level1_sandbox_outcome_evaluation_and_human_review_summary(self.source)

    def test_valid_observed_outcome_evaluates_as_passed(self):
        result = validate_level1_sandbox_outcome_evaluation_and_human_review_summary(self.record)

        self.assertTrue(result["valid"])
        self.assertEqual(STATUS_PASSED, self.record["evaluation_status"])
        self.assertTrue(result["passed_expected_sandbox_outcome"])

    def test_valid_record_uses_level1_observation_source(self):
        self.assertEqual("level1_sandbox_lesson_application_outcome_observation", self.record["source_observation_record_type"])
        self.assertEqual("phase0_level1_sandbox_only", self.record["source_observation_target_scope"])
        self.assertTrue(self.record["observation_valid"])

    def test_expected_fields_match_observed_fields(self):
        self.assertEqual("d", self.record["observed_front_symbol"])
        self.assertEqual("check_before_retry", self.record["observed_sandbox_action"])
        self.assertTrue(self.record["observed_blocks_retry_same_action_until_check"])
        self.assertTrue(self.record["audit_record_present"])
        self.assertTrue(self.record["rollback_record_present"])

    def test_missing_observation_evaluates_as_inconclusive(self):
        record = build_level1_sandbox_outcome_evaluation_and_human_review_summary({})

        self.assertEqual(STATUS_INCONCLUSIVE, record["evaluation_status"])
        self.assertTrue(validate_level1_sandbox_outcome_evaluation_and_human_review_summary(record)["valid"])

    def test_malformed_observation_evaluates_as_inconclusive(self):
        record = build_level1_sandbox_outcome_evaluation_and_human_review_summary("not a record")

        self.assertEqual(STATUS_INCONCLUSIVE, record["evaluation_status"])
        self.assertTrue(validate_level1_sandbox_outcome_evaluation_and_human_review_summary(record)["valid"])

    def test_wrong_target_scope_is_inconclusive(self):
        source = self._source_with("target_scope", "production")
        record = build_level1_sandbox_outcome_evaluation_and_human_review_summary(source)

        self.assertEqual(STATUS_INCONCLUSIVE, record["evaluation_status"])

    def test_wrong_front_symbol_fails(self):
        source = self._source_with("observed_front_symbol", ".")
        record = build_level1_sandbox_outcome_evaluation_and_human_review_summary(source)

        self.assertEqual(STATUS_FAILED, record["evaluation_status"])
        self.assertTrue(validate_level1_sandbox_outcome_evaluation_and_human_review_summary(record)["valid"])

    def test_wrong_sandbox_action_fails(self):
        source = self._source_with("observed_sandbox_action", "retry_same_action")
        record = build_level1_sandbox_outcome_evaluation_and_human_review_summary(source)

        self.assertEqual(STATUS_FAILED, record["evaluation_status"])

    def test_missing_retry_same_action_block_fails(self):
        source = self._source_with("observed_blocks_retry_same_action_until_check", False)
        record = build_level1_sandbox_outcome_evaluation_and_human_review_summary(source)

        self.assertEqual(STATUS_FAILED, record["evaluation_status"])

    def test_missing_audit_fails(self):
        source = self._source_with("audit_record_present", False)
        record = build_level1_sandbox_outcome_evaluation_and_human_review_summary(source)

        self.assertEqual(STATUS_FAILED, record["evaluation_status"])

    def test_missing_rollback_fails(self):
        source = self._source_with("rollback_record_present", False)
        record = build_level1_sandbox_outcome_evaluation_and_human_review_summary(source)

        self.assertEqual(STATUS_FAILED, record["evaluation_status"])

    def test_forbidden_effect_claims_are_invalid(self):
        for flag in FORBIDDEN_EFFECTS:
            with self.subTest(flag=flag):
                record = build_level1_sandbox_outcome_evaluation_and_human_review_summary(self.source)
                record["forbidden_effects"][flag] = True

                self.assertFalse(validate_level1_sandbox_outcome_evaluation_and_human_review_summary(record)["valid"])

    def test_human_review_summary_is_conservative(self):
        summary = self.record["human_review_summary"]

        self.assertEqual(PASS_RESULT, summary["plain_language_result"])
        self.assertEqual(SAFE_CLAIM, summary["safe_claim"])
        self.assertTrue(summary["not_proof_of_learning"])
        self.assertTrue(summary["not_runtime_behavior_change"])
        self.assertTrue(summary["not_memory_write"])
        self.assertTrue(summary["not_predictor_mutation"])
        self.assertTrue(summary["not_production_promotion"])

    def test_forbidden_human_summary_wording_blocks(self):
        record = build_level1_sandbox_outcome_evaluation_and_human_review_summary(self.source)
        record["human_review_summary"]["safe_claim"] = "ASHL Core learned the lesson."

        self.assertFalse(validate_level1_sandbox_outcome_evaluation_and_human_review_summary(record)["valid"])

    def test_task_queue_completion_does_not_count_as_approval(self):
        record = build_level1_sandbox_outcome_evaluation_and_human_review_summary(self.source)
        record["task_queue_note"]["completed_task_is_approval"] = True

        errors = validate_level1_sandbox_outcome_evaluation_and_human_review_summary(record)["error_codes"]

        self.assertIn("task_queue_note_completed_task_is_approval_not_false", errors)

    def test_passing_tests_do_not_count_as_approval(self):
        record = build_level1_sandbox_outcome_evaluation_and_human_review_summary(self.source)
        record["task_queue_note"]["passing_tests_are_approval"] = True

        errors = validate_level1_sandbox_outcome_evaluation_and_human_review_summary(record)["error_codes"]

        self.assertIn("task_queue_note_passing_tests_are_approval_not_false", errors)

    def test_codex_generated_status_does_not_count_as_approval(self):
        record = build_level1_sandbox_outcome_evaluation_and_human_review_summary(self.source)
        record["task_queue_note"]["codex_generated_status_is_approval"] = True

        errors = validate_level1_sandbox_outcome_evaluation_and_human_review_summary(record)["error_codes"]

        self.assertIn("task_queue_note_codex_generated_status_is_approval_not_false", errors)

    def test_cli_returns_status_ok(self):
        result = run_command("run-level1-sandbox-outcome-evaluation-and-human-review-summary-minimal-check")

        self.assertEqual("ok", result["status"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = run_level1_sandbox_outcome_evaluation_and_human_review_summary_minimal_check()["summary"]

        self.assertEqual(4, summary["valid_evaluation_count"])
        self.assertGreaterEqual(summary["invalid_evaluation_count"], 1)
        self.assertEqual(1, summary["passed_expected_sandbox_outcome_count"])
        self.assertEqual(2, summary["failed_expected_sandbox_outcome_count"])
        self.assertEqual(1, summary["inconclusive_missing_or_invalid_observation_count"])
        self.assertEqual(4, summary["human_review_summary_count"])
        self.assertEqual(4, summary["forbidden_effects_blocked_count"])
        self.assertEqual(4, summary["task_queue_not_approval_count"])

    def _source_with(self, field, value):
        source = build_level1_sandbox_lesson_application_outcome_observation()
        source[field] = value
        return source


if __name__ == "__main__":
    unittest.main()
