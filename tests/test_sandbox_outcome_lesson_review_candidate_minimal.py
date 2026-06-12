import json
import subprocess
import sys
import unittest

from ashl_core.sandbox_execution_outcome_integration_minimal import build_sandbox_action_outcome_trace
from ashl_core.sandbox_outcome_lesson_review_candidate_minimal import (
    build_sandbox_outcome_lesson_review_candidate,
    run_sandbox_outcome_lesson_review_candidate_minimal_check,
    validate_sandbox_outcome_lesson_review_candidate,
)
from ashl_core.teaching_cli import run_command


class SandboxOutcomeLessonReviewCandidateMinimalTests(unittest.TestCase):
    def _candidate(self):
        return build_sandbox_outcome_lesson_review_candidate()

    def _assert_invalid(self, record, error_code):
        validation = validate_sandbox_outcome_lesson_review_candidate(record)
        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_lesson_review_candidate_is_created(self):
        candidate = self._candidate()
        validation = validate_sandbox_outcome_lesson_review_candidate(candidate)

        self.assertTrue(validation["valid"])
        self.assertEqual(candidate["candidate_mode"], "sandbox_outcome_lesson_review_candidate_only")

    def test_candidate_reuses_sandbox_action_outcome_trace(self):
        trace = build_sandbox_action_outcome_trace()
        candidate = build_sandbox_outcome_lesson_review_candidate(trace)

        self.assertEqual(candidate["source_action_outcome_trace_id"], trace["action_outcome_trace_id"])
        self.assertEqual(candidate["candidate_context"]["action_observed"], "check_before_retry")

    def test_candidate_context_matches_successful_check(self):
        context = self._candidate()["candidate_context"]

        self.assertEqual(context["sandbox_id"], "phase0_toy_sandbox_obstacle_retry_failed")
        self.assertEqual(context["scenario_id"], "obstacle_retry_failed_same_state")
        self.assertEqual(context["exact_key"], "obstacle_retry_failed")
        self.assertEqual(context["action_observed"], "check_before_retry")
        self.assertTrue(context["outcome_match"])
        self.assertTrue(context["sandbox_check_success"])
        self.assertFalse(context["failure_detected"])

    def test_candidate_content_is_controlled_sandbox_evidence(self):
        content = self._candidate()["candidate_content"]

        self.assertEqual(content["candidate_type"], "successful_sandbox_check_evidence")
        self.assertIn("check_before_retry", content["candidate_statement"])
        self.assertIn("obstacle_detected=True", content["evidence_summary"])
        self.assertTrue(content["suggested_review_question"])
        self.assertEqual(content["confidence_scope"], "controlled_sandbox_only")

    def test_review_requirements_block_application_and_writes(self):
        requirements = self._candidate()["review_requirements"]

        self.assertTrue(requirements["requires_human_review"])
        self.assertFalse(requirements["approved_for_lesson_application"])
        self.assertFalse(requirements["approved_for_memory_write"])
        self.assertFalse(requirements["approved_for_retention_write"])
        self.assertFalse(requirements["approved_for_predictor_mutation"])
        self.assertFalse(requirements["approved_for_runtime_behavior_change"])

    def test_bad_candidate_context_blocks(self):
        cases = {
            "sandbox_id": "sandbox_id_not_phase0_toy_sandbox_obstacle_retry_failed",
            "scenario_id": "scenario_id_not_obstacle_retry_failed_same_state",
            "exact_key": "exact_key_not_obstacle_retry_failed",
            "action_observed": "action_observed_not_check_before_retry",
            "outcome_match": "outcome_match_not_true",
            "sandbox_check_success": "sandbox_check_success_not_true",
            "failure_detected": "failure_detected_not_false",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                candidate = self._candidate()
                candidate["candidate_context"][field] = False if field != "failure_detected" else True
                if field in {"sandbox_id", "scenario_id", "exact_key", "action_observed"}:
                    candidate["candidate_context"][field] = "bad"
                self._assert_invalid(candidate, error_code)

    def test_bad_candidate_content_blocks(self):
        cases = {
            "candidate_type": ("applied_lesson", "candidate_type_not_successful_sandbox_check_evidence"),
            "candidate_statement": ("", "candidate_statement_empty_or_not_string"),
            "evidence_summary": ("", "evidence_summary_empty_or_not_string"),
            "suggested_review_question": ("", "suggested_review_question_empty_or_not_string"),
            "confidence_scope": ("generalized_behavior", "confidence_scope_not_controlled_sandbox_only"),
        }
        for field, (value, error_code) in cases.items():
            with self.subTest(field=field):
                candidate = self._candidate()
                candidate["candidate_content"][field] = value
                self._assert_invalid(candidate, error_code)

    def test_requires_human_review_false_blocks(self):
        candidate = self._candidate()
        candidate["review_requirements"]["requires_human_review"] = False
        self._assert_invalid(candidate, "requires_human_review_not_true")

    def test_approved_for_fields_true_block(self):
        cases = {
            "approved_for_lesson_application": "approved_for_lesson_application_not_false",
            "approved_for_memory_write": "approved_for_memory_write_not_false",
            "approved_for_retention_write": "approved_for_retention_write_not_false",
            "approved_for_predictor_mutation": "approved_for_predictor_mutation_not_false",
            "approved_for_runtime_behavior_change": "approved_for_runtime_behavior_change_not_false",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                candidate = self._candidate()
                candidate["review_requirements"][field] = True
                self._assert_invalid(candidate, error_code)

    def test_blocked_flags_true_block(self):
        cases = {
            "lesson_applied": "lesson_applied_enabled",
            "memory_write": "memory_write_enabled",
            "retention_write": "retention_write_enabled",
            "new_retention_written": "new_retention_written_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "runtime_behavior_changed": "runtime_behavior_changed_enabled",
            "production_action_selection": "production_action_selection_enabled",
            "runtime_action_selection": "runtime_action_selection_enabled",
            "selected_action_created": "selected_action_created_enabled",
            "final_action_created": "final_action_created_enabled",
            "direct_action_command": "direct_action_command_enabled",
            "real_navigation_changed": "real_navigation_changed_enabled",
            "ui_behavior_changed": "ui_behavior_changed_enabled",
            "persistent_policy_written": "persistent_policy_written_enabled",
            "general_behavior_changed": "general_behavior_changed_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                candidate = self._candidate()
                candidate["blocked_flags"][flag] = True
                self._assert_invalid(candidate, error_code)

    def test_empty_human_summary_fields_block(self):
        cases = {
            "what_was_created": "what_was_created_empty_or_not_string",
            "what_review_is_required": "what_review_is_required_empty_or_not_string",
            "plain_result": "plain_result_empty_or_not_string",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                candidate = self._candidate()
                candidate["human_summary"][field] = ""
                self._assert_invalid(candidate, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_outcome_lesson_review_candidate_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-sandbox-outcome-lesson-review-candidate-minimal-check")
        self.assertEqual(result["flow"], "sandbox_outcome_lesson_review_candidate_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["lesson_review_candidate_result_count"], 39)
        self.assertEqual(summary["valid_lesson_review_candidate_count"], 1)
        self.assertEqual(summary["invalid_lesson_review_candidate_count"], 38)
        self.assertEqual(summary["candidate_created_count"], 1)
        self.assertEqual(summary["requires_human_review_count"], 1)
        self.assertEqual(summary["approved_for_lesson_application_blocked_count"], 1)
        self.assertEqual(summary["approved_for_memory_write_blocked_count"], 1)
        self.assertEqual(summary["approved_for_retention_write_blocked_count"], 1)
        self.assertEqual(summary["approved_for_predictor_mutation_blocked_count"], 1)
        self.assertEqual(summary["approved_for_runtime_behavior_change_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["retention_write_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["predictor_mutation_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-sandbox-outcome-lesson-review-candidate-minimal-check")

        self.assertEqual(result["command"], "run-sandbox-outcome-lesson-review-candidate-minimal-check")
        self.assertEqual(result["summary"]["valid_lesson_review_candidate_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-sandbox-outcome-lesson-review-candidate-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-sandbox-outcome-lesson-review-candidate-minimal-check")
        self.assertEqual(result["summary"]["candidate_created_count"], 1)


if __name__ == "__main__":
    unittest.main()
