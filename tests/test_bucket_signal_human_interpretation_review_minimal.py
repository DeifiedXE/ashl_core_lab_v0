import unittest
from copy import deepcopy

from ashl_core.bucket_signal_human_interpretation_review_minimal import (
    BOUNDARY_VERSION,
    build_human_interpreted_lesson_candidate_from_bucket_signal,
    build_human_interpretation_review_decision,
    run_bucket_signal_human_interpretation_review_minimal_check,
    validate_human_interpreted_lesson_candidate,
    validate_human_interpretation_review_decision,
)


class BucketSignalHumanInterpretationReviewMinimalTests(unittest.TestCase):
    def test_valid_human_interpreted_candidate_from_bucket_signal(self):
        record = build_human_interpreted_lesson_candidate_from_bucket_signal()
        result = validate_human_interpreted_lesson_candidate(record)
        self.assertTrue(result["valid"])
        self.assertEqual(record["source_signal_type"], "bucket_derived_lesson_candidate_signal")
        self.assertEqual(record["source_signal_authorship"], "qingyin_bucket_derived_system_detected")
        self.assertEqual(record["source_repeated_key"], "retry_same_risky_action_without_check")
        self.assertGreaterEqual(record["source_occurrence_count"], record["source_minimum_signal_threshold"])
        self.assertEqual(record["interpretation_author_type"], "human_or_human_gpt_assisted")
        self.assertFalse(record["qingyin_generated_text"])
        self.assertFalse(record["qingyin_self_proposed_text"])
        self.assertFalse(record["candidate_text_generated_by_qingyin"])
        self.assertTrue(record["repo_audit_acknowledged"])
        self.assertEqual(record["qingyin_current_status"], "phase0_trace_checker_system")
        self.assertFalse(record["qingyin_autonomous_learning_claim_allowed"])
        self.assertFalse(record["qingyin_autonomous_action_claim_allowed"])
        self.assertEqual(record["runtime_memory_influenced_behavior_count"], 0)
        self.assertTrue(record["human_review_required"])

    def test_valid_all_review_decisions(self):
        candidate = build_human_interpreted_lesson_candidate_from_bucket_signal()
        expected = {
            "approved_for_future_memory_readiness_design_only": True,
            "rejected": False,
            "needs_more_evidence": False,
            "needs_rewrite": False,
        }
        for decision, allowed in expected.items():
            with self.subTest(decision=decision):
                record = build_human_interpretation_review_decision(candidate, decision)
                result = validate_human_interpretation_review_decision(record)
                self.assertTrue(result["valid"])
                self.assertEqual(record["review_decision"], decision)
                self.assertEqual(record["memory_readiness_design_allowed"], allowed)
                self.assertTrue(record["not_application_approval"])
                self.assertTrue(record["not_memory_write_approval"])
                self.assertTrue(record["not_runtime_influence_approval"])
                self.assertTrue(record["not_predictor_approval"])
                self.assertTrue(record["not_proof_of_learning"])
                self.assertFalse(record["memory_write_allowed"])
                self.assertFalse(record["retained_jsonl_write_allowed"])
                self.assertFalse(record["runtime_influence_allowed"])
                self.assertFalse(record["predictor_influence_allowed"])
                self.assertFalse(record["proof_of_learning_claim_allowed"])

    def test_invalid_candidate_self_authorship_flags_block(self):
        for field in ("qingyin_generated_text", "qingyin_self_proposed_text", "candidate_text_generated_by_qingyin"):
            with self.subTest(field=field):
                record = build_human_interpreted_lesson_candidate_from_bucket_signal()
                record[field] = True
                result = validate_human_interpreted_lesson_candidate(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_invalid_candidate_audit_claims_block(self):
        cases = [
            ("repo_audit_acknowledged", False, "repo_audit_acknowledged_not_expected"),
            ("qingyin_current_status", "autonomous_learner", "qingyin_current_status_not_expected"),
            (
                "qingyin_autonomous_learning_claim_allowed",
                True,
                "qingyin_autonomous_learning_claim_allowed_not_expected",
            ),
            (
                "qingyin_autonomous_action_claim_allowed",
                True,
                "qingyin_autonomous_action_claim_allowed_not_expected",
            ),
            (
                "runtime_memory_influenced_behavior_count",
                1,
                "runtime_memory_influenced_behavior_count_not_expected",
            ),
        ]
        for field, value, error in cases:
            with self.subTest(field=field):
                record = build_human_interpreted_lesson_candidate_from_bucket_signal()
                record[field] = value
                result = validate_human_interpreted_lesson_candidate(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_invalid_candidate_required_fields_block(self):
        cases = [
            ("human_review_required", False, "human_review_required_not_true"),
            ("source_occurrence_count", 2, "source_occurrence_count_below_threshold"),
            ("interpreted_lesson_text", "", "interpreted_lesson_text_empty"),
            ("plain_language_summary", "", "plain_language_summary_empty"),
            ("source_repeated_key", "wrong", "source_repeated_key_not_expected"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field):
                record = build_human_interpreted_lesson_candidate_from_bucket_signal()
                record[field] = value
                result = validate_human_interpreted_lesson_candidate(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_invalid_candidate_permission_flags_block(self):
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
            "task_queue_status_is_approval",
            "passing_tests_are_approval",
            "codex_generated_status_is_approval",
        ):
            with self.subTest(field=field):
                record = build_human_interpreted_lesson_candidate_from_bucket_signal()
                record[field] = True
                result = validate_human_interpreted_lesson_candidate(record)
                self.assertFalse(result["valid"])
                self.assertTrue(any(error.startswith(field) for error in result["error_codes"]))

    def test_invalid_review_identity_and_text_block(self):
        candidate = build_human_interpreted_lesson_candidate_from_bucket_signal()
        cases = [
            ("reviewer_actor", "codex", "reviewer_actor_not_human"),
            ("reviewer_role", "assistant", "reviewer_role_not_project_owner"),
            ("review_text", "", "review_text_empty"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field):
                record = build_human_interpretation_review_decision(candidate)
                record[field] = value
                result = validate_human_interpretation_review_decision(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_invalid_review_approval_claims_block(self):
        candidate = build_human_interpreted_lesson_candidate_from_bucket_signal()
        cases = [
            ("not_application_approval", False, "not_application_approval_not_true"),
            ("not_memory_write_approval", False, "not_memory_write_approval_not_true"),
            ("not_runtime_influence_approval", False, "not_runtime_influence_approval_not_true"),
            ("not_predictor_approval", False, "not_predictor_approval_not_true"),
            ("not_proof_of_learning", False, "not_proof_of_learning_not_true"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field):
                record = build_human_interpretation_review_decision(candidate)
                record[field] = value
                result = validate_human_interpretation_review_decision(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_invalid_review_permission_flags_block(self):
        candidate = build_human_interpreted_lesson_candidate_from_bucket_signal()
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
            "task_queue_status_is_approval",
            "passing_tests_are_approval",
            "codex_generated_status_is_approval",
        ):
            with self.subTest(field=field):
                record = build_human_interpretation_review_decision(candidate)
                record[field] = True
                result = validate_human_interpretation_review_decision(record)
                self.assertFalse(result["valid"])
                self.assertTrue(any(error.startswith(field) for error in result["error_codes"]))

    def test_non_approved_review_cannot_allow_memory_readiness_design(self):
        candidate = build_human_interpreted_lesson_candidate_from_bucket_signal()
        record = build_human_interpretation_review_decision(candidate, "rejected")
        record["memory_readiness_design_allowed"] = True
        result = validate_human_interpretation_review_decision(record)
        self.assertFalse(result["valid"])
        self.assertIn("non_approved_decision_allowed_memory_readiness_design", result["error_codes"])

    def test_summary_counts_are_deterministic(self):
        result = run_bucket_signal_human_interpretation_review_minimal_check()
        summary = result["summary"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_interpreted_candidate_count"], 1)
        self.assertGreaterEqual(summary["invalid_interpreted_candidate_count"], 1)
        self.assertEqual(summary["valid_review_decision_count"], 4)
        self.assertGreaterEqual(summary["invalid_review_decision_count"], 1)
        self.assertEqual(summary["repo_audit_acknowledged_count"], 1)
        self.assertEqual(summary["qingyin_self_authorship_blocked_count"], 1)
        self.assertEqual(summary["human_review_required_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 5)
        self.assertEqual(summary["runtime_influence_blocked_count"], 5)
        self.assertEqual(summary["proof_claim_blocked_count"], 5)

    def test_boundary_index_is_unchanged(self):
        result = run_bucket_signal_human_interpretation_review_minimal_check()
        boundary = result["boundary"]
        self.assertFalse(boundary["boundary_change_required"])
        self.assertFalse(boundary["boundary_index_update_required"])
        self.assertEqual(boundary["boundary_index_version_before"], BOUNDARY_VERSION)
        self.assertEqual(boundary["boundary_index_version_after"], BOUNDARY_VERSION)

    def test_builder_rejects_invalid_source_signal(self):
        signal = build_human_interpreted_lesson_candidate_from_bucket_signal()["source_bucket_signal"]
        invalid_signal = deepcopy(signal)
        invalid_signal["repeated_key"] = "wrong"
        with self.assertRaises(ValueError):
            build_human_interpreted_lesson_candidate_from_bucket_signal(invalid_signal)


if __name__ == "__main__":
    unittest.main()
