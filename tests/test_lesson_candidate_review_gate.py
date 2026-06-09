import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.lesson_candidate_from_failure_reason import (
    run_lesson_candidate_from_failure_reason_check,
    validate_lesson_candidate_record,
)
from ashl_core.lesson_candidate_review_gate import (
    evaluate_lesson_candidate_review_gate,
    run_lesson_candidate_review_gate_check,
    validate_lesson_candidate_review_gate_result,
)
from ashl_core.teaching_cli import run_command


class LessonCandidateReviewGateTests(unittest.TestCase):
    def _valid_candidate(self):
        result = run_lesson_candidate_from_failure_reason_check()
        return next(
            record
            for record, validation in zip(result["lesson_candidate_records"], result["validation_results"])
            if validation["valid"]
        )

    def _pending_gate_result(self):
        return evaluate_lesson_candidate_review_gate(self._valid_candidate())

    def test_valid_lesson_candidate_produces_pending_review_gate_result(self):
        gate_result = self._pending_gate_result()
        validation = validate_lesson_candidate_review_gate_result(gate_result)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(gate_result["gate_status"], "pending_review")
        self.assertTrue(gate_result["eligible_for_human_review"])
        self.assertEqual(gate_result["blocked_reasons"], [])

    def test_pending_review_is_not_approval(self):
        gate_result = self._pending_gate_result()

        self.assertTrue(gate_result["review_state"]["pending_review"])
        self.assertFalse(gate_result["review_state"]["approved"])
        self.assertFalse(gate_result["safety_flags"]["approved_lesson"])

    def test_eligible_for_human_review_is_not_approval(self):
        gate_result = self._pending_gate_result()

        self.assertTrue(gate_result["eligible_for_human_review"])
        self.assertFalse(gate_result["review_state"]["reviewed_by_human"])
        self.assertFalse(gate_result["review_state"]["approved"])

    def test_invalid_lesson_candidate_is_blocked(self):
        candidate = self._valid_candidate()
        candidate["candidate_type"] = "free_form_lesson"
        gate_result = evaluate_lesson_candidate_review_gate(candidate)

        self.assertEqual(gate_result["gate_status"], "blocked")
        self.assertIn("invalid_lesson_candidate", gate_result["blocked_reasons"])

    def test_missing_source_failure_reason_id_blocks_review_gate(self):
        candidate = self._valid_candidate()
        candidate.pop("source_failure_reason_id")
        self._assert_gate_blocks(candidate, "missing_source_failure_reason")

    def test_review_required_false_blocks_review_gate(self):
        candidate = self._valid_candidate()
        candidate["review_boundary"]["review_required"] = False
        self._assert_gate_blocks(candidate, "review_not_required")

    def test_approved_true_blocks_review_gate(self):
        candidate = self._valid_candidate()
        candidate["review_boundary"]["approved"] = True
        self._assert_gate_blocks(candidate, "already_approved")

    def test_rejected_true_blocks_review_gate(self):
        candidate = self._valid_candidate()
        candidate["review_boundary"]["rejected"] = True
        self._assert_gate_blocks(candidate, "already_rejected")

    def test_lesson_application_allowed_true_blocks_review_gate(self):
        self._assert_review_boundary_blocks("lesson_application_allowed", True, "lesson_application_unblocked")

    def test_persistent_learning_allowed_true_blocks_review_gate(self):
        self._assert_review_boundary_blocks("persistent_learning_allowed", True, "persistent_learning_unblocked")

    def test_memory_write_allowed_true_blocks_review_gate(self):
        self._assert_review_boundary_blocks("memory_write_allowed", True, "memory_write_unblocked")

    def test_predictor_mutation_allowed_true_blocks_review_gate(self):
        self._assert_review_boundary_blocks("predictor_mutation_allowed", True, "predictor_mutation_unblocked")

    def test_approved_lesson_true_blocks_review_gate(self):
        self._assert_safety_blocks("approved_lesson", True, "approved_lesson_flag_set")

    def test_lesson_applied_true_blocks_review_gate(self):
        self._assert_safety_blocks("lesson_applied", True, "lesson_applied_flag_set")

    def test_persistent_candidate_created_true_blocks_review_gate(self):
        candidate = self._valid_candidate()
        candidate["safety_flags"]["persistent_candidate_created"] = True
        self.assertTrue(validate_lesson_candidate_record(candidate)["valid"])
        self._assert_gate_blocks(candidate, "persistent_candidate_created")

    def test_blocked_from_action_selection_false_blocks_review_gate(self):
        self._assert_safety_blocks("blocked_from_action_selection", False, "action_selection_unblocked")

    def test_blocked_from_action_behavior_change_false_blocks_review_gate(self):
        self._assert_safety_blocks("blocked_from_action_behavior_change", False, "action_behavior_change_not_blocked")

    def test_blocked_from_lesson_application_false_blocks_review_gate(self):
        self._assert_safety_blocks("blocked_from_lesson_application", False, "lesson_application_not_blocked")

    def test_blocked_from_memory_write_false_blocks_review_gate(self):
        self._assert_safety_blocks("blocked_from_memory_write", False, "memory_write_not_blocked")

    def test_blocked_from_predictor_mutation_false_blocks_review_gate(self):
        self._assert_safety_blocks("blocked_from_predictor_mutation", False, "predictor_mutation_not_blocked")

    def test_blocked_from_persistent_rule_write_false_blocks_review_gate(self):
        self._assert_safety_blocks("blocked_from_persistent_rule_write", False, "persistent_rule_write_not_blocked")

    def test_action_selection_influence_true_blocks_gate_result(self):
        self._assert_gate_result_safety_error("action_selection_influence", True, "action_selection_influence_enabled")

    def test_action_behavior_changed_nonzero_blocks_gate_result(self):
        self._assert_gate_result_safety_error("action_behavior_changed", 1, "action_behavior_changed_enabled")

    def test_lesson_application_runtime_true_blocks_gate_result(self):
        self._assert_gate_result_safety_error("lesson_application_runtime", True, "lesson_application_runtime_enabled")

    def test_memory_write_true_blocks_gate_result(self):
        self._assert_gate_result_safety_error("memory_write", True, "memory_write_enabled")

    def test_predictor_modified_true_blocks_gate_result(self):
        self._assert_gate_result_safety_error("predictor_modified", True, "predictor_modified_enabled")

    def test_persistent_rule_write_true_blocks_gate_result(self):
        self._assert_gate_result_safety_error("persistent_rule_write", True, "persistent_rule_write_enabled")

    def test_endocrine_control_true_blocks_gate_result(self):
        self._assert_gate_result_safety_error("endocrine_control", True, "endocrine_control_enabled")

    def test_autonomy_enabled_true_blocks_gate_result(self):
        self._assert_gate_result_safety_error("autonomy_enabled", True, "autonomy_enabled_enabled")

    def test_evaluate_does_not_mutate_lesson_candidate(self):
        candidate = self._valid_candidate()
        original = deepcopy(candidate)

        evaluate_lesson_candidate_review_gate(candidate)

        self.assertEqual(candidate, original)

    def test_demo_check_summary_has_expected_counts(self):
        result = run_lesson_candidate_review_gate_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-lesson-candidate-review-gate-check")
        self.assertEqual(result["flow"], "lesson_candidate_review_gate_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["lesson_candidate_record_count"], 15)
        self.assertEqual(summary["valid_lesson_candidate_count"], 2)
        self.assertEqual(summary["invalid_lesson_candidate_count"], 13)
        self.assertEqual(summary["review_gate_result_count"], 15)
        self.assertEqual(summary["pending_review_count"], 1)
        self.assertEqual(summary["blocked_count"], 14)
        self.assertEqual(summary["eligible_for_human_review_count"], 1)
        self.assertGreaterEqual(summary["invalid_lesson_candidate_blocked_count"], 1)
        self.assertEqual(summary["missing_source_failure_reason_blocked_count"], 1)
        self.assertEqual(summary["review_not_required_blocked_count"], 1)
        self.assertEqual(summary["already_approved_blocked_count"], 1)
        self.assertEqual(summary["already_rejected_blocked_count"], 1)
        self.assertEqual(summary["lesson_application_unblocked_blocked_count"], 1)
        self.assertEqual(summary["persistent_learning_unblocked_blocked_count"], 1)
        self.assertEqual(summary["memory_write_unblocked_blocked_count"], 1)
        self.assertEqual(summary["predictor_mutation_unblocked_blocked_count"], 1)
        self.assertEqual(summary["approved_lesson_flag_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_flag_blocked_count"], 1)
        self.assertEqual(summary["action_selection_unblocked_blocked_count"], 1)
        for field in [
            "persistent_candidate_created_count",
            "action_selection_influence_count",
            "action_behavior_changed_count",
            "lesson_application_runtime_count",
            "memory_write_count",
            "predictor_modified_count",
            "persistent_rule_write_count",
            "endocrine_control_count",
            "autonomy_enabled_count",
        ]:
            with self.subTest(field=field):
                self.assertEqual(summary[field], 0)
        self.assertTrue(boundary["trace_check_only"])
        self.assertTrue(boundary["uses_lesson_candidate_from_failure_reason"])
        self.assertFalse(boundary["pending_review_is_approval"])
        self.assertFalse(boundary["eligible_for_human_review_is_approval"])
        self.assertFalse(boundary["lesson_candidate_approval_added"])
        self.assertFalse(boundary["lesson_application_runtime_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["persistent_candidate_creation_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["autonomy_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-lesson-candidate-review-gate-check")

        self.assertEqual(result["command"], "run-lesson-candidate-review-gate-check")
        self.assertEqual(result["summary"]["pending_review_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-lesson-candidate-review-gate-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-lesson-candidate-review-gate-check")
        self.assertEqual(result["summary"]["review_gate_result_count"], 15)

    def _assert_review_boundary_blocks(self, field, value, reason):
        candidate = self._valid_candidate()
        candidate["review_boundary"][field] = value
        self._assert_gate_blocks(candidate, reason)

    def _assert_safety_blocks(self, field, value, reason):
        candidate = self._valid_candidate()
        candidate["safety_flags"][field] = value
        self._assert_gate_blocks(candidate, reason)

    def _assert_gate_blocks(self, candidate, reason):
        gate_result = evaluate_lesson_candidate_review_gate(candidate)
        validation = validate_lesson_candidate_review_gate_result(gate_result)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(gate_result["gate_status"], "blocked")
        self.assertFalse(gate_result["eligible_for_human_review"])
        self.assertIn(reason, gate_result["blocked_reasons"])

    def _assert_gate_result_safety_error(self, field, value, error_code):
        gate_result = self._pending_gate_result()
        gate_result["safety_flags"][field] = value
        validation = validate_lesson_candidate_review_gate_result(gate_result)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
