import unittest

from ashl_core.level2_sandbox_application_observation_evaluation_summary_minimal import (
    EVALUATION_PASSED,
    SAFE_CLAIM,
    build_level2_sandbox_application_evaluation_record,
    build_level2_sandbox_application_human_review_summary,
    build_level2_sandbox_application_observation_record,
    build_level2_sandbox_application_record,
    run_level2_sandbox_application_observation_evaluation_summary_minimal_check,
    validate_level2_sandbox_application_evaluation_record,
    validate_level2_sandbox_application_human_review_summary,
    validate_level2_sandbox_application_observation_record,
    validate_level2_sandbox_application_record,
)


class Level2SandboxApplicationObservationEvaluationSummaryMinimalTests(unittest.TestCase):
    def test_valid_full_level2_sandbox_only_loop_passes(self):
        application = build_level2_sandbox_application_record()
        observation = build_level2_sandbox_application_observation_record(application)
        evaluation = build_level2_sandbox_application_evaluation_record(observation)
        summary = build_level2_sandbox_application_human_review_summary(evaluation)

        self.assertTrue(validate_level2_sandbox_application_record(application)["valid"])
        self.assertTrue(validate_level2_sandbox_application_observation_record(observation)["valid"])
        self.assertTrue(validate_level2_sandbox_application_evaluation_record(evaluation)["valid"])
        self.assertTrue(validate_level2_sandbox_application_human_review_summary(summary)["valid"])

    def test_application_requires_explicit_user_approval(self):
        record = build_level2_sandbox_application_record()
        record["approval_checked"] = False
        result = validate_level2_sandbox_application_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("approval_checked_not_true", result["error_codes"])

    def test_codex_ai_task_queue_fixture_and_passing_tests_do_not_count_as_approval(self):
        for source in ("codex", "ai", "task_queue", "test_fixture", "passing_tests"):
            with self.subTest(source=source):
                record = build_level2_sandbox_application_record()
                record["approval_source"] = source
                result = validate_level2_sandbox_application_record(record)
                self.assertFalse(result["valid"])
                self.assertIn("approval_source_not_explicit_user_statement", result["error_codes"])

    def test_invalid_scenario_plan_blocks_application(self):
        record = build_level2_sandbox_application_record()
        record["source_scenario_plan_valid"] = False
        result = validate_level2_sandbox_application_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("source_scenario_plan_valid_not_true", result["error_codes"])

    def test_invalid_dry_run_evaluation_blocks_application(self):
        record = build_level2_sandbox_application_record()
        record["source_dry_run_evaluation_valid"] = False
        result = validate_level2_sandbox_application_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("source_dry_run_evaluation_valid_not_true", result["error_codes"])

    def test_wrong_target_scope_blocks_application(self):
        record = build_level2_sandbox_application_record()
        record["target_scope"] = "production"
        result = validate_level2_sandbox_application_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("target_scope_not_phase0_level2_sandbox_only", result["error_codes"])

    def test_forbidden_runtime_memory_predictor_production_flags_block_application(self):
        for field in (
            "runtime_behavior_changed",
            "production_behavior_changed",
            "memory_written",
            "retained_jsonl_written",
            "retention_written",
            "predictor_mutated",
            "selected_action_created",
            "final_action_created",
            "direct_command_created",
            "proof_of_learning_claimed",
        ):
            with self.subTest(field=field):
                record = build_level2_sandbox_application_record()
                record[field] = True
                result = validate_level2_sandbox_application_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_observation_requires_valid_application(self):
        observation = build_level2_sandbox_application_observation_record()
        observation["source_application_valid"] = False
        result = validate_level2_sandbox_application_observation_record(observation)
        self.assertFalse(result["valid"])
        self.assertIn("source_application_valid_not_true", result["error_codes"])

    def test_evaluation_requires_valid_observation(self):
        evaluation = build_level2_sandbox_application_evaluation_record()
        evaluation["source_observation_valid"] = False
        result = validate_level2_sandbox_application_evaluation_record(evaluation)
        self.assertFalse(result["valid"])
        self.assertIn("source_observation_valid_not_true", result["error_codes"])

    def test_human_review_summary_requires_valid_evaluation(self):
        summary = build_level2_sandbox_application_human_review_summary()
        summary["source_evaluation_valid"] = False
        result = validate_level2_sandbox_application_human_review_summary(summary)
        self.assertFalse(result["valid"])
        self.assertIn("source_evaluation_valid_not_true", result["error_codes"])

    def test_proof_of_learning_claim_is_rejected(self):
        summary = build_level2_sandbox_application_human_review_summary()
        summary["proof_of_learning_claimed"] = True
        result = validate_level2_sandbox_application_human_review_summary(summary)
        self.assertFalse(result["valid"])
        self.assertIn("proof_of_learning_claimed_not_false", result["error_codes"])

    def test_audit_and_rollback_are_required(self):
        for field in ("audit_recorded", "rollback_available"):
            with self.subTest(field=field):
                record = build_level2_sandbox_application_record()
                record[field] = False
                result = validate_level2_sandbox_application_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_true", result["error_codes"])

    def test_evaluation_passed_status_and_safe_summary(self):
        evaluation = build_level2_sandbox_application_evaluation_record()
        summary = build_level2_sandbox_application_human_review_summary(evaluation)
        self.assertEqual(evaluation["evaluation_status"], EVALUATION_PASSED)
        self.assertEqual(summary["allowed_claims"], [SAFE_CLAIM])

    def test_boundary_index_is_not_incremented_by_package_completion(self):
        result = run_level2_sandbox_application_observation_evaluation_summary_minimal_check()
        boundary = result["boundary"]
        self.assertTrue(boundary["boundary_change_required"])
        self.assertTrue(boundary["boundary_index_update_required"])
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b72")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b73")
        self.assertIn("sandbox application permission boundary", boundary["boundary_change_rationale"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_level2_sandbox_application_observation_evaluation_summary_minimal_check()
        summary = result["summary"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_level2_sandbox_application_count"], 1)
        self.assertEqual(summary["valid_level2_observation_count"], 1)
        self.assertEqual(summary["valid_level2_evaluation_count"], 1)
        self.assertEqual(summary["valid_level2_human_review_summary_count"], 1)
        self.assertGreaterEqual(summary["invalid_level2_records_blocked_count"], 1)
        self.assertEqual(summary["forbidden_capability_detected_count"], 0)
        self.assertEqual(summary["proof_of_learning_claim_detected_count"], 0)


if __name__ == "__main__":
    unittest.main()
