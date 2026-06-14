import unittest

from ashl_core.bucket_signal_human_interpretation_review_minimal import (
    build_human_interpretation_review_decision,
)
from ashl_core.memory_readiness_design_for_approved_bucket_lesson_minimal import (
    BOUNDARY_VERSION,
    REQUIRED_BEFORE_MEMORY_WRITE,
    build_memory_readiness_design_for_approved_bucket_lesson,
    run_memory_readiness_design_for_approved_bucket_lesson_minimal_check,
    validate_memory_readiness_design_for_approved_bucket_lesson,
)


class MemoryReadinessDesignForApprovedBucketLessonMinimalTests(unittest.TestCase):
    def test_valid_memory_readiness_design_from_approved_review(self):
        record = build_memory_readiness_design_for_approved_bucket_lesson()
        result = validate_memory_readiness_design_for_approved_bucket_lesson(record)
        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "memory_readiness_design_for_approved_bucket_lesson")
        self.assertEqual(record["source_review_decision"], "approved_for_future_memory_readiness_design_only")
        self.assertEqual(record["source_signal_authorship"], "qingyin_bucket_derived_system_detected")
        self.assertEqual(record["interpretation_author_type"], "human_or_human_gpt_assisted")
        self.assertEqual(record["memory_admission_status"], "not_admitted_to_memory")
        self.assertEqual(record["memory_write_status"], "not_written")
        self.assertEqual(record["current_allowed_use"], "future_memory_readiness_design_only")
        self.assertEqual(record["proposed_future_memory_form"], "reviewed_lesson_memory_candidate")
        self.assertEqual(record["proposed_future_memory_scope"], "future_sandbox_influence_design_only")
        self.assertEqual(record["proposed_runtime_influence"], "blocked")
        self.assertEqual(record["proposed_predictor_influence"], "blocked")
        self.assertTrue(set(REQUIRED_BEFORE_MEMORY_WRITE).issubset(record["required_before_any_memory_write"]))
        self.assertTrue(record["repo_audit_acknowledged"])
        self.assertEqual(record["qingyin_current_status"], "phase0_trace_checker_system")
        self.assertFalse(record["qingyin_self_authored_lesson_text"])
        self.assertFalse(record["autonomous_learning_claim_allowed"])

    def test_builder_rejects_non_approved_review_decisions(self):
        for decision in ("rejected", "needs_more_evidence", "needs_rewrite"):
            with self.subTest(decision=decision):
                review = build_human_interpretation_review_decision(review_decision=decision)
                with self.assertRaises(ValueError):
                    build_memory_readiness_design_for_approved_bucket_lesson(review)

    def test_invalid_if_source_is_not_bucket_derived(self):
        record = build_memory_readiness_design_for_approved_bucket_lesson()
        record["source_signal_authorship"] = "manual_note"
        result = validate_memory_readiness_design_for_approved_bucket_lesson(record)
        self.assertFalse(result["valid"])
        self.assertIn("source_signal_authorship_not_qingyin_bucket_derived_system_detected", result["error_codes"])

    def test_invalid_if_interpretation_marked_qingyin_authored(self):
        record = build_memory_readiness_design_for_approved_bucket_lesson()
        record["interpretation_author_type"] = "qingyin"
        record["qingyin_self_authored_lesson_text"] = True
        result = validate_memory_readiness_design_for_approved_bucket_lesson(record)
        self.assertFalse(result["valid"])
        self.assertIn("interpretation_author_type_not_human_or_human_gpt_assisted", result["error_codes"])
        self.assertIn("qingyin_self_authored_lesson_text_not_false", result["error_codes"])

    def test_invalid_if_repo_audit_not_acknowledged(self):
        record = build_memory_readiness_design_for_approved_bucket_lesson()
        record["repo_audit_acknowledged"] = False
        result = validate_memory_readiness_design_for_approved_bucket_lesson(record)
        self.assertFalse(result["valid"])
        self.assertIn("repo_audit_acknowledged_not_true", result["error_codes"])

    def test_invalid_memory_status_claims_block(self):
        cases = [
            ("memory_admission_status", "admitted", "memory_admission_status_not_not_admitted"),
            ("memory_write_status", "written", "memory_write_status_not_not_written"),
            ("current_allowed_use", "memory_write", "current_allowed_use_not_design_only"),
            (
                "proposed_future_memory_form",
                "Long-term Memory",
                "proposed_future_memory_form_not_reviewed_lesson_memory_candidate",
            ),
            ("proposed_runtime_influence", "allowed", "proposed_runtime_influence_not_blocked"),
            ("proposed_predictor_influence", "allowed", "proposed_predictor_influence_not_blocked"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field):
                record = build_memory_readiness_design_for_approved_bucket_lesson()
                record[field] = value
                result = validate_memory_readiness_design_for_approved_bucket_lesson(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_invalid_if_required_before_memory_write_list_incomplete(self):
        record = build_memory_readiness_design_for_approved_bucket_lesson()
        record["required_before_any_memory_write"] = list(REQUIRED_BEFORE_MEMORY_WRITE[:-1])
        result = validate_memory_readiness_design_for_approved_bucket_lesson(record)
        self.assertFalse(result["valid"])
        self.assertIn(
            "missing_required_before_memory_write:audit_and_revocation_path",
            result["error_codes"],
        )

    def test_invalid_for_forbidden_capability_flags(self):
        for field in (
            "memory_write_allowed",
            "retained_jsonl_write_allowed",
            "retention_write_allowed",
            "runtime_influence_allowed",
            "predictor_influence_allowed",
            "production_behavior_change_allowed",
            "selected_action_allowed",
            "final_action_allowed",
            "proof_of_learning_claim_allowed",
        ):
            with self.subTest(field=field):
                record = build_memory_readiness_design_for_approved_bucket_lesson()
                record[field] = True
                result = validate_memory_readiness_design_for_approved_bucket_lesson(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_summary_counts_are_deterministic(self):
        result = run_memory_readiness_design_for_approved_bucket_lesson_minimal_check()
        summary = result["summary"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_memory_readiness_design_count"], 1)
        self.assertGreaterEqual(summary["invalid_memory_readiness_design_count"], 1)
        self.assertEqual(summary["approved_review_checked_count"], 1)
        self.assertEqual(summary["bucket_signal_source_checked_count"], 1)
        self.assertEqual(summary["repo_audit_acknowledged_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["retained_jsonl_write_blocked_count"], 1)
        self.assertEqual(summary["runtime_influence_blocked_count"], 1)
        self.assertEqual(summary["predictor_influence_blocked_count"], 1)
        self.assertEqual(summary["future_requirements_recorded_count"], 1)
        self.assertEqual(summary["proof_claim_blocked_count"], 1)

    def test_boundary_index_is_unchanged(self):
        result = run_memory_readiness_design_for_approved_bucket_lesson_minimal_check()
        boundary = result["boundary"]
        self.assertFalse(boundary["boundary_change_required"])
        self.assertFalse(boundary["boundary_index_update_required"])
        self.assertEqual(boundary["boundary_index_version_before"], BOUNDARY_VERSION)
        self.assertEqual(boundary["boundary_index_version_after"], BOUNDARY_VERSION)


if __name__ == "__main__":
    unittest.main()
