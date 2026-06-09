import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.failure_reason_from_outcome_pair import run_failure_reason_from_outcome_pair_check
from ashl_core.lesson_candidate_from_failure_reason import (
    ALLOWED_CANDIDATE_TYPES,
    ALLOWED_CORRECTION_TYPES,
    build_lesson_candidate_from_failure_reason,
    run_lesson_candidate_from_failure_reason_check,
    validate_lesson_candidate_record,
)
from ashl_core.teaching_cli import run_command


class LessonCandidateFromFailureReasonTests(unittest.TestCase):
    def _valid_failure_reason(self):
        result = run_failure_reason_from_outcome_pair_check()
        return next(record for record, validation in zip(result["failure_reason_records"], result["validation_results"]) if validation["valid"])

    def _valid_candidate(self):
        return build_lesson_candidate_from_failure_reason(self._valid_failure_reason())

    def test_valid_failure_reason_produces_valid_lesson_candidate(self):
        candidate = self._valid_candidate()
        validation = validate_lesson_candidate_record(candidate)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(candidate["candidate_type"], "precondition_or_correction")
        self.assertEqual(candidate["review_boundary"]["review_required"], True)

    def test_invalid_failure_reason_does_not_produce_valid_lesson_candidate(self):
        result = run_failure_reason_from_outcome_pair_check()
        invalid_reason = next(record for record, validation in zip(result["failure_reason_records"], result["validation_results"]) if not validation["valid"])

        with self.assertRaisesRegex(ValueError, "invalid_failure_reason"):
            build_lesson_candidate_from_failure_reason(invalid_reason)

    def test_lesson_candidate_links_to_source_failure_reason_id(self):
        reason = self._valid_failure_reason()
        candidate = build_lesson_candidate_from_failure_reason(reason)

        self.assertEqual(candidate["source_failure_reason_id"], reason["failure_reason_id"])
        self.assertEqual(candidate["source_trace"]["source_failure_reason_id"], reason["failure_reason_id"])

    def test_lesson_candidate_links_to_source_pair_id_and_action_intent_id(self):
        reason = self._valid_failure_reason()
        candidate = build_lesson_candidate_from_failure_reason(reason)

        self.assertEqual(candidate["source_pair_id"], reason["source_pair_id"])
        self.assertEqual(candidate["action_intent_id"], reason["action_intent_id"])

    def test_candidate_type_must_be_allowed(self):
        self.assertIn(self._valid_candidate()["candidate_type"], ALLOWED_CANDIDATE_TYPES)

    def test_correction_type_must_be_allowed(self):
        self.assertIn(self._valid_candidate()["proposed_correction"]["correction_type"], ALLOWED_CORRECTION_TYPES)

    def test_unknown_candidate_type_blocks_record(self):
        candidate = self._valid_candidate()
        candidate["candidate_type"] = "free_form_lesson"
        validation = validate_lesson_candidate_record(candidate)

        self.assertFalse(validation["valid"])
        self.assertIn("unknown_candidate_type", validation["error_codes"])

    def test_unknown_correction_type_blocks_record(self):
        candidate = self._valid_candidate()
        candidate["proposed_correction"]["correction_type"] = "move_anyway"
        validation = validate_lesson_candidate_record(candidate)

        self.assertFalse(validation["valid"])
        self.assertIn("unknown_correction_type", validation["error_codes"])

    def test_correction_applied_true_blocks_record(self):
        candidate = self._valid_candidate()
        candidate["proposed_correction"]["correction_applied"] = True
        validation = validate_lesson_candidate_record(candidate)

        self.assertFalse(validation["valid"])
        self.assertIn("correction_applied_enabled", validation["error_codes"])

    def test_review_required_false_blocks_record(self):
        self._assert_review_boundary_error("review_required", False, "review_required_not_true")

    def test_approved_true_blocks_record(self):
        self._assert_review_boundary_error("approved", True, "approved_enabled")

    def test_rejected_true_blocks_record(self):
        self._assert_review_boundary_error("rejected", True, "rejected_enabled")

    def test_lesson_application_allowed_true_blocks_record(self):
        self._assert_review_boundary_error(
            "lesson_application_allowed",
            True,
            "lesson_application_allowed_enabled",
        )

    def test_persistent_learning_allowed_true_blocks_record(self):
        self._assert_review_boundary_error(
            "persistent_learning_allowed",
            True,
            "persistent_learning_allowed_enabled",
        )

    def test_memory_write_allowed_true_blocks_record(self):
        self._assert_review_boundary_error("memory_write_allowed", True, "memory_write_allowed_enabled")

    def test_predictor_mutation_allowed_true_blocks_record(self):
        self._assert_review_boundary_error(
            "predictor_mutation_allowed",
            True,
            "predictor_mutation_allowed_enabled",
        )

    def test_approved_lesson_true_blocks_record(self):
        self._assert_safety_error("approved_lesson", True, "approved_lesson_enabled")

    def test_lesson_applied_true_blocks_record(self):
        self._assert_safety_error("lesson_applied", True, "lesson_applied_enabled")

    def test_blocked_from_action_selection_false_blocks_record(self):
        self._assert_safety_error("blocked_from_action_selection", False, "action_selection_not_blocked")

    def test_blocked_from_action_behavior_change_false_blocks_record(self):
        self._assert_safety_error(
            "blocked_from_action_behavior_change",
            False,
            "action_behavior_change_not_blocked",
        )

    def test_blocked_from_lesson_application_false_blocks_record(self):
        self._assert_safety_error("blocked_from_lesson_application", False, "lesson_application_not_blocked")

    def test_blocked_from_memory_write_false_blocks_record(self):
        self._assert_safety_error("blocked_from_memory_write", False, "memory_write_not_blocked")

    def test_blocked_from_predictor_mutation_false_blocks_record(self):
        self._assert_safety_error("blocked_from_predictor_mutation", False, "predictor_mutation_not_blocked")

    def test_blocked_from_persistent_rule_write_false_blocks_record(self):
        self._assert_safety_error(
            "blocked_from_persistent_rule_write",
            False,
            "persistent_rule_write_not_blocked",
        )

    def test_action_selection_influence_true_blocks_record(self):
        self._assert_safety_error("action_selection_influence", True, "action_selection_influence_enabled")

    def test_action_behavior_changed_nonzero_blocks_record(self):
        self._assert_safety_error("action_behavior_changed", 1, "action_behavior_changed_enabled")

    def test_lesson_application_runtime_true_blocks_record(self):
        self._assert_safety_error("lesson_application_runtime", True, "lesson_application_runtime_enabled")

    def test_memory_write_true_blocks_record(self):
        self._assert_safety_error("memory_write", True, "memory_write_enabled")

    def test_predictor_modified_true_blocks_record(self):
        self._assert_safety_error("predictor_modified", True, "predictor_modified_enabled")

    def test_persistent_rule_write_true_blocks_record(self):
        self._assert_safety_error("persistent_rule_write", True, "persistent_rule_write_enabled")

    def test_endocrine_control_true_blocks_record(self):
        self._assert_safety_error("endocrine_control", True, "endocrine_control_enabled")

    def test_autonomy_enabled_true_blocks_record(self):
        self._assert_safety_error("autonomy_enabled", True, "autonomy_enabled_enabled")

    def test_build_does_not_mutate_failure_reason(self):
        reason = self._valid_failure_reason()
        original = deepcopy(reason)

        build_lesson_candidate_from_failure_reason(reason)

        self.assertEqual(reason, original)

    def test_demo_check_summary_has_expected_counts(self):
        result = run_lesson_candidate_from_failure_reason_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-lesson-candidate-from-failure-reason-check")
        self.assertEqual(result["flow"], "lesson_candidate_from_failure_reason_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["failure_reason_record_count"], 11)
        self.assertEqual(summary["valid_failure_reason_count"], 1)
        self.assertEqual(summary["invalid_failure_reason_count"], 10)
        self.assertEqual(summary["generated_lesson_candidate_count"], 1)
        self.assertEqual(summary["valid_lesson_candidate_count"], 1)
        self.assertEqual(summary["invalid_lesson_candidate_count"], 12)
        self.assertEqual(summary["missing_failure_reason_source_blocked_count"], 1)
        self.assertEqual(summary["unknown_candidate_type_blocked_count"], 1)
        self.assertEqual(summary["unknown_correction_type_blocked_count"], 1)
        self.assertEqual(summary["review_required_missing_blocked_count"], 1)
        self.assertEqual(summary["approved_lesson_blocked_count"], 1)
        self.assertEqual(summary["lesson_application_allowed_blocked_count"], 1)
        self.assertEqual(summary["persistent_learning_allowed_blocked_count"], 1)
        self.assertEqual(summary["memory_write_allowed_blocked_count"], 1)
        self.assertEqual(summary["predictor_mutation_allowed_blocked_count"], 1)
        self.assertEqual(summary["action_selection_unblocked_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        for field in [
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
        self.assertTrue(boundary["uses_failure_reason_from_outcome_pair"])
        self.assertTrue(boundary["v0_local_lesson_candidate_validator"])
        self.assertFalse(boundary["lesson_candidate_approval_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["new_action_behavior_added"])
        self.assertFalse(boundary["lesson_application_runtime_added"])
        self.assertFalse(boundary["persistent_learning_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["autonomy_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-lesson-candidate-from-failure-reason-check")

        self.assertEqual(result["command"], "run-lesson-candidate-from-failure-reason-check")
        self.assertEqual(result["summary"]["valid_lesson_candidate_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-lesson-candidate-from-failure-reason-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-lesson-candidate-from-failure-reason-check")
        self.assertEqual(result["summary"]["generated_lesson_candidate_count"], 1)

    def _assert_review_boundary_error(self, field, value, error_code):
        candidate = self._valid_candidate()
        candidate["review_boundary"][field] = value
        validation = validate_lesson_candidate_record(candidate)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def _assert_safety_error(self, field, value, error_code):
        candidate = self._valid_candidate()
        candidate["safety_flags"][field] = value
        validation = validate_lesson_candidate_record(candidate)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
