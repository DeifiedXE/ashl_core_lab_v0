import unittest

from ashl_core.level2_sandbox_review_conclusion_and_promotion_readiness_minimal import (
    CONCLUSION_FAILED,
    CONCLUSION_INCONCLUSIVE,
    CONCLUSION_PASSED,
    READINESS_FAILED,
    READINESS_INCONCLUSIVE,
    READINESS_READY,
    build_level2_sandbox_review_conclusion,
    build_phase0_future_promotion_readiness,
    run_level2_sandbox_review_conclusion_and_promotion_readiness_minimal_check,
    validate_level2_sandbox_review_conclusion,
    validate_phase0_future_promotion_readiness,
)


class Level2SandboxReviewConclusionPromotionReadinessMinimalTests(unittest.TestCase):
    def test_valid_passed_level2_review_conclusion(self):
        record = build_level2_sandbox_review_conclusion()
        result = validate_level2_sandbox_review_conclusion(record)
        self.assertTrue(result["valid"])
        self.assertEqual(record["review_conclusion_status"], CONCLUSION_PASSED)
        self.assertTrue(record["audit_present"])
        self.assertTrue(record["rollback_present"])

    def test_valid_conservative_promotion_readiness(self):
        readiness = build_phase0_future_promotion_readiness()
        result = validate_phase0_future_promotion_readiness(readiness)
        self.assertTrue(result["valid"])
        self.assertEqual(readiness["readiness_status"], READINESS_READY)
        self.assertTrue(readiness["ready_for_future_higher_level_design_package"])
        self.assertEqual(readiness["next_allowed_package_kind"], "future_design_package_only")

    def test_failed_evaluation_blocks_future_design_readiness(self):
        conclusion = build_level2_sandbox_review_conclusion()
        conclusion["level2_evaluation_status"] = "failed_expected_level2_sandbox_outcome"
        conclusion["review_conclusion_status"] = CONCLUSION_FAILED
        readiness = build_phase0_future_promotion_readiness(conclusion)
        result = validate_phase0_future_promotion_readiness(readiness)
        self.assertTrue(result["valid"])
        self.assertEqual(readiness["readiness_status"], READINESS_FAILED)
        self.assertFalse(readiness["ready_for_future_higher_level_design_package"])

    def test_inconclusive_evaluation_blocks_future_design_readiness(self):
        conclusion = build_level2_sandbox_review_conclusion()
        conclusion["level2_evaluation_status"] = "inconclusive_missing_or_invalid_observation"
        conclusion["review_conclusion_status"] = CONCLUSION_INCONCLUSIVE
        readiness = build_phase0_future_promotion_readiness(conclusion)
        result = validate_phase0_future_promotion_readiness(readiness)
        self.assertTrue(result["valid"])
        self.assertEqual(readiness["readiness_status"], READINESS_INCONCLUSIVE)
        self.assertFalse(readiness["ready_for_future_higher_level_design_package"])

    def test_missing_audit_blocks_passed_conclusion(self):
        record = build_level2_sandbox_review_conclusion()
        record["audit_present"] = False
        result = validate_level2_sandbox_review_conclusion(record)
        self.assertFalse(result["valid"])
        self.assertIn("audit_present_not_true", result["error_codes"])

    def test_missing_rollback_blocks_passed_conclusion(self):
        record = build_level2_sandbox_review_conclusion()
        record["rollback_present"] = False
        result = validate_level2_sandbox_review_conclusion(record)
        self.assertFalse(result["valid"])
        self.assertIn("rollback_present_not_true", result["error_codes"])

    def test_forbidden_conclusion_flags_are_rejected(self):
        for field in (
            "runtime_behavior_changed",
            "memory_written",
            "retained_jsonl_written",
            "retention_written",
            "predictor_mutated",
            "selected_action_created",
            "final_action_created",
            "production_promotion_claimed",
            "proof_of_learning_claimed",
        ):
            with self.subTest(field=field):
                record = build_level2_sandbox_review_conclusion()
                record[field] = True
                result = validate_level2_sandbox_review_conclusion(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_proof_of_learning_language_is_rejected(self):
        record = build_level2_sandbox_review_conclusion()
        record["review_conclusion_reason"] = "This is proof of learning."
        result = validate_level2_sandbox_review_conclusion(record)
        self.assertFalse(result["valid"])
        self.assertIn("review_conclusion_reason_contains_proof_language", result["error_codes"])

    def test_promotion_readiness_does_not_authorize_runtime_memory_predictor_action_or_production(self):
        readiness = build_phase0_future_promotion_readiness()
        for field in (
            "ready_for_runtime_behavior_change",
            "ready_for_memory_write",
            "ready_for_retained_jsonl_write",
            "ready_for_predictor_mutation",
            "ready_for_production_promotion",
            "ready_for_selected_action",
            "ready_for_final_action",
            "promotion_performed",
            "proof_of_learning_claimed",
        ):
            with self.subTest(field=field):
                candidate = dict(readiness)
                candidate[field] = True
                result = validate_phase0_future_promotion_readiness(candidate)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_package_id_boundary_index_separation_is_respected(self):
        result = run_level2_sandbox_review_conclusion_and_promotion_readiness_minimal_check()
        boundary = result["boundary"]
        self.assertFalse(boundary["boundary_change_required"])
        self.assertFalse(boundary["boundary_index_update_required"])
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b73")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b73")

    def test_demo_summary_counts_are_deterministic(self):
        result = run_level2_sandbox_review_conclusion_and_promotion_readiness_minimal_check()
        summary = result["summary"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_level2_sandbox_review_conclusion_count"], 1)
        self.assertGreaterEqual(summary["invalid_level2_sandbox_review_conclusion_count"], 1)
        self.assertEqual(summary["valid_promotion_readiness_count"], 1)
        self.assertGreaterEqual(summary["invalid_promotion_readiness_count"], 1)
        self.assertEqual(summary["ready_for_future_design_package_only_count"], 1)
        self.assertEqual(summary["runtime_behavior_changed_count"], 0)
        self.assertEqual(summary["memory_written_count"], 0)
        self.assertEqual(summary["retained_jsonl_written_count"], 0)
        self.assertEqual(summary["predictor_mutated_count"], 0)
        self.assertEqual(summary["selected_action_created_count"], 0)
        self.assertEqual(summary["final_action_created_count"], 0)
        self.assertEqual(summary["production_promotion_claimed_count"], 0)
        self.assertEqual(summary["proof_of_learning_claimed_count"], 0)


if __name__ == "__main__":
    unittest.main()
