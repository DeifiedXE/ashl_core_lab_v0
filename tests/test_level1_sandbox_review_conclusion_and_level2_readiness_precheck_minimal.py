import unittest

from ashl_core.level1_sandbox_outcome_evaluation_and_human_review_summary_minimal import (
    build_level1_sandbox_outcome_evaluation_and_human_review_summary,
)
from ashl_core.level1_sandbox_review_conclusion_and_level2_readiness_precheck_minimal import (
    CONCLUSION_FAILED,
    CONCLUSION_INCONCLUSIVE,
    CONCLUSION_MISSING_SUMMARY,
    CONCLUSION_PASSED,
    PRECHECK_MISSING_LEVEL1_PASS,
    PRECHECK_READY,
    build_level1_sandbox_review_conclusion_and_level2_readiness_precheck,
    run_level1_sandbox_review_conclusion_and_level2_readiness_precheck_minimal_check,
    validate_level1_sandbox_review_conclusion_and_level2_readiness_precheck,
)
from ashl_core.teaching_cli import run_command


class Level1SandboxReviewConclusionAndLevel2ReadinessPrecheckMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_level1_sandbox_review_conclusion_and_level2_readiness_precheck()

    def test_valid_passed_level1_review_conclusion(self):
        result = validate_level1_sandbox_review_conclusion_and_level2_readiness_precheck(self.record)

        self.assertTrue(result["valid"])
        self.assertEqual(CONCLUSION_PASSED, self.record["level1_review_conclusion_status"])
        self.assertEqual(PRECHECK_READY, self.record["level2_readiness_precheck_status"])

    def test_failed_evaluation_cannot_produce_passed_conclusion(self):
        source = self._evaluation_from_observation("observed_front_symbol", ".")
        record = build_level1_sandbox_review_conclusion_and_level2_readiness_precheck(source)

        self.assertEqual(CONCLUSION_FAILED, record["level1_review_conclusion_status"])
        self.assertEqual(PRECHECK_MISSING_LEVEL1_PASS, record["level2_readiness_precheck_status"])

        record["level1_review_conclusion_status"] = CONCLUSION_PASSED
        self.assertFalse(validate_level1_sandbox_review_conclusion_and_level2_readiness_precheck(record)["valid"])

    def test_inconclusive_evaluation_cannot_produce_passed_conclusion(self):
        source = build_level1_sandbox_outcome_evaluation_and_human_review_summary({})
        record = build_level1_sandbox_review_conclusion_and_level2_readiness_precheck(source)

        self.assertEqual(CONCLUSION_INCONCLUSIVE, record["level1_review_conclusion_status"])
        self.assertEqual(PRECHECK_MISSING_LEVEL1_PASS, record["level2_readiness_precheck_status"])

        record["level1_review_conclusion_status"] = CONCLUSION_PASSED
        self.assertFalse(validate_level1_sandbox_review_conclusion_and_level2_readiness_precheck(record)["valid"])

    def test_missing_human_review_summary_blocks_conclusion(self):
        source = build_level1_sandbox_outcome_evaluation_and_human_review_summary()
        source.pop("human_review_summary")
        record = build_level1_sandbox_review_conclusion_and_level2_readiness_precheck(source)

        self.assertEqual(CONCLUSION_MISSING_SUMMARY, record["level1_review_conclusion_status"])
        self.assertFalse(record["human_summary_present"])

    def test_proof_of_learning_claim_is_rejected(self):
        self.assert_field_true_blocks("proof_of_learning_claimed")

    def test_runtime_behavior_change_is_rejected(self):
        self.assert_field_true_blocks("runtime_behavior_changed")

    def test_memory_write_is_rejected(self):
        self.assert_field_true_blocks("memory_written")

    def test_retained_jsonl_write_is_rejected(self):
        self.assert_field_true_blocks("retained_jsonl_written")

    def test_retention_write_is_rejected(self):
        self.assert_field_true_blocks("retention_written")

    def test_predictor_mutation_is_rejected(self):
        self.assert_field_true_blocks("predictor_mutated")

    def test_selected_action_final_action_direct_command_are_rejected(self):
        for field in ("selected_action_created", "final_action_created", "direct_command_created"):
            with self.subTest(field=field):
                self.assert_field_true_blocks(field)

    def test_production_promotion_is_rejected(self):
        self.assert_field_true_blocks("production_promoted")

    def test_level2_precheck_does_not_allow_level2_application(self):
        self.assertFalse(self.record["level2_application_allowed"])
        self.assert_field_true_blocks("level2_application_allowed")

    def test_level2_precheck_does_not_allow_level2_execution(self):
        self.assertFalse(self.record["level2_execution_allowed"])
        self.assert_field_true_blocks("level2_execution_allowed")

    def test_future_package_required_for_level2(self):
        record = build_level1_sandbox_review_conclusion_and_level2_readiness_precheck()
        record["future_package_required_for_level2"] = False

        errors = validate_level1_sandbox_review_conclusion_and_level2_readiness_precheck(record)["error_codes"]

        self.assertIn("future_package_required_for_level2_not_true", errors)

    def test_task_queue_completed_status_is_not_approval(self):
        self.assert_field_true_blocks("task_queue_completed_state_is_approval")

    def test_passing_tests_are_not_approval(self):
        self.assert_field_true_blocks("passing_tests_are_approval")

    def test_codex_generated_review_conclusion_is_not_approval(self):
        self.assert_field_true_blocks("codex_generated_review_conclusion_is_approval")

    def test_level2_precheck_is_not_approval(self):
        self.assert_field_true_blocks("level2_precheck_is_approval")

    def test_cli_returns_status_ok(self):
        result = run_command("run-level1-sandbox-review-conclusion-and-level2-readiness-precheck-minimal-check")

        self.assertEqual("ok", result["status"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = run_level1_sandbox_review_conclusion_and_level2_readiness_precheck_minimal_check()["summary"]

        self.assertEqual(1, summary["valid_level1_review_conclusion_count"])
        self.assertGreaterEqual(summary["valid_record_count"], 3)
        self.assertGreaterEqual(summary["invalid_level1_review_conclusion_count"], 1)
        self.assertEqual(1, summary["level2_precheck_ready_count"])
        self.assertEqual(0, summary["level2_application_allowed_count"])
        self.assertEqual(0, summary["level2_execution_allowed_count"])
        self.assertEqual(0, summary["proof_of_learning_claim_count"])
        self.assertEqual(0, summary["runtime_behavior_change_count"])
        self.assertEqual(0, summary["memory_write_count"])
        self.assertEqual(0, summary["predictor_mutation_count"])
        self.assertEqual(0, summary["production_promotion_count"])

    def assert_field_true_blocks(self, field):
        record = build_level1_sandbox_review_conclusion_and_level2_readiness_precheck()
        record[field] = True

        errors = validate_level1_sandbox_review_conclusion_and_level2_readiness_precheck(record)["error_codes"]

        self.assertIn(f"{field}_not_false", errors)

    def _evaluation_from_observation(self, field, value):
        source = build_level1_sandbox_outcome_evaluation_and_human_review_summary()["source_observation"]
        source[field] = value
        return build_level1_sandbox_outcome_evaluation_and_human_review_summary(source)


if __name__ == "__main__":
    unittest.main()
