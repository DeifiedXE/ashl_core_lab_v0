import unittest

from ashl_core.bucket_derived_lesson_candidate_signal_minimal import (
    BOUNDARY_VERSION,
    build_bucket_derived_lesson_candidate_signal,
    run_bucket_derived_lesson_candidate_signal_minimal_check,
    validate_bucket_derived_lesson_candidate_signal,
)
from ashl_core.codex_task_queue_minimal import build_codex_task_queue_minimal
from ashl_core.teaching_cli import run_command


class BucketDerivedLessonCandidateSignalMinimalTests(unittest.TestCase):
    def test_valid_bucket_derived_candidate_signal(self):
        record = build_bucket_derived_lesson_candidate_signal()
        result = validate_bucket_derived_lesson_candidate_signal(record)

        self.assertTrue(result["valid"])
        self.assertEqual("bucket_derived_lesson_candidate_signal", record["record_type"])
        self.assertEqual("pending_human_interpretation", record["candidate_signal_status"])
        self.assertFalse(record["qingyin_generated_text"])
        self.assertIsNone(record["generated_lesson_text"])
        self.assertIsNone(record["suggested_human_interpretation"])

    def test_invalid_when_generated_lesson_text_is_present(self):
        record = build_bucket_derived_lesson_candidate_signal()
        record["generated_lesson_text"] = "Check before retrying."

        result = validate_bucket_derived_lesson_candidate_signal(record)

        self.assertFalse(result["valid"])
        self.assertIn("generated_lesson_text_not_null", result["error_codes"])

    def test_invalid_when_qingyin_generated_text_is_true(self):
        record = build_bucket_derived_lesson_candidate_signal()
        record["qingyin_generated_text"] = True

        result = validate_bucket_derived_lesson_candidate_signal(record)

        self.assertFalse(result["valid"])
        self.assertIn("qingyin_generated_text_not_false", result["error_codes"])

    def test_invalid_when_human_interpretation_required_is_false(self):
        record = build_bucket_derived_lesson_candidate_signal()
        record["human_interpretation_required"] = False

        result = validate_bucket_derived_lesson_candidate_signal(record)

        self.assertFalse(result["valid"])
        self.assertIn("human_interpretation_required_not_true", result["error_codes"])

    def test_invalid_when_occurrence_count_is_below_threshold(self):
        record = build_bucket_derived_lesson_candidate_signal()
        record["occurrence_count"] = 2

        result = validate_bucket_derived_lesson_candidate_signal(record)

        self.assertFalse(result["valid"])
        self.assertIn("occurrence_count_below_threshold", result["error_codes"])

    def test_invalid_when_supporting_contexts_are_missing(self):
        record = build_bucket_derived_lesson_candidate_signal()
        record["supporting_contexts"] = ["safe_path_variant"]

        result = validate_bucket_derived_lesson_candidate_signal(record)

        self.assertFalse(result["valid"])
        self.assertIn("supporting_contexts_missing_required_variants", result["error_codes"])

    def test_invalid_when_source_scope_is_not_level3_variant_suite(self):
        record = build_bucket_derived_lesson_candidate_signal()
        record["source_scope"] = "phase0_level3_toy_minefield_sandbox_only"

        result = validate_bucket_derived_lesson_candidate_signal(record)

        self.assertFalse(result["valid"])
        self.assertIn("source_scope_not_level3_variant_suite_only", result["error_codes"])

    def test_blocked_permission_fields_are_rejected(self):
        for field in (
            "memory_write_allowed",
            "retained_jsonl_write_allowed",
            "runtime_influence_allowed",
            "predictor_influence_allowed",
            "production_behavior_change_allowed",
            "selected_action_allowed",
            "final_action_allowed",
            "proof_of_learning_claim_allowed",
        ):
            with self.subTest(field=field):
                record = build_bucket_derived_lesson_candidate_signal()
                record[field] = True
                result = validate_bucket_derived_lesson_candidate_signal(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_task_queue_or_tests_as_approval_are_rejected(self):
        for field in (
            "task_queue_completed_status_is_approval",
            "passing_tests_are_approval",
            "codex_generated_candidate_text_is_qingyin_authored",
        ):
            with self.subTest(field=field):
                record = build_bucket_derived_lesson_candidate_signal()
                record[field] = True
                result = validate_bucket_derived_lesson_candidate_signal(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_old_sandbox_stable_lesson_candidate_proposal_is_superseded_in_task_queue(self):
        queue = build_codex_task_queue_minimal()
        task = next(
            task
            for task in queue["task_entries"]
            if task["package_title"] == "Sandbox-Stable Lesson Candidate Proposal Minimal v0"
        )

        self.assertEqual("superseded", task["task_status"])
        self.assertEqual("superseded", task["status"])
        self.assertEqual("Bucket-Derived Lesson Candidate Signal Minimal v0", task["superseded_by"])
        self.assertIn("structured bucket-derived signal", task["notes"])

    def test_cli_summary_shape(self):
        result = run_command("run-bucket-derived-lesson-candidate-signal-minimal-check")
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_signal_count"])
        self.assertGreaterEqual(summary["invalid_signal_count"], 1)
        self.assertEqual(1, summary["source_bucket_checked_count"])
        self.assertEqual(1, summary["repeated_key_checked_count"])
        self.assertEqual(1, summary["threshold_checked_count"])
        self.assertEqual(1, summary["supporting_context_checked_count"])
        self.assertEqual(1, summary["human_interpretation_required_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["runtime_influence_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])

    def test_boundary_index_does_not_change(self):
        result = run_bucket_derived_lesson_candidate_signal_minimal_check()
        boundary = result["boundary"]

        self.assertFalse(boundary["boundary_change_required"])
        self.assertFalse(boundary["boundary_index_update_required"])
        self.assertEqual(BOUNDARY_VERSION, boundary["boundary_index_version_before"])
        self.assertEqual(BOUNDARY_VERSION, boundary["boundary_index_version_after"])


if __name__ == "__main__":
    unittest.main()
