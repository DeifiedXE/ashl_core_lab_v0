import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.lesson_candidate_human_review_decision_schema import (
    build_lesson_candidate_human_review_decision,
    run_lesson_candidate_human_review_decision_schema_check,
    validate_lesson_candidate_human_review_decision,
)
from ashl_core.lesson_candidate_review_evidence_summary import (
    run_lesson_candidate_review_evidence_summary_check,
)
from ashl_core.teaching_cli import run_command


class LessonCandidateHumanReviewDecisionSchemaTests(unittest.TestCase):
    def _valid_evidence_summary(self):
        result = run_lesson_candidate_review_evidence_summary_check()
        return next(
            summary
            for summary, validation in zip(result["evidence_summaries"], result["evidence_summary_validations"])
            if validation["valid"]
        )

    def _decision(self, status="approved_for_preview"):
        return build_lesson_candidate_human_review_decision(self._valid_evidence_summary(), status)

    def test_valid_approved_for_preview_decision_passes(self):
        self._assert_valid_status("approved_for_preview", allows_preview=True)

    def test_valid_rejected_decision_passes(self):
        self._assert_valid_status("rejected", allows_preview=False)

    def test_valid_needs_revision_decision_passes(self):
        self._assert_valid_status("needs_revision", allows_preview=False)

    def test_valid_stale_decision_passes(self):
        self._assert_valid_status("stale", allows_preview=False)

    def test_unknown_decision_status_blocks_record(self):
        decision = self._decision()
        decision["decision"]["status"] = "approved"
        self._assert_invalid(decision, "unknown_decision_status")

    def test_missing_source_evidence_summary_id_blocks_record(self):
        self._assert_missing_linkage_blocks("source_evidence_summary_id")

    def test_missing_source_lesson_candidate_id_blocks_record(self):
        self._assert_missing_linkage_blocks("source_lesson_candidate_id")

    def test_missing_source_review_gate_result_id_blocks_record(self):
        self._assert_missing_linkage_blocks("source_review_gate_result_id")

    def test_missing_source_failure_reason_id_blocks_record(self):
        self._assert_missing_linkage_blocks("source_failure_reason_id")

    def test_missing_source_pair_id_blocks_record(self):
        self._assert_missing_linkage_blocks("source_pair_id")

    def test_missing_action_intent_id_blocks_record(self):
        self._assert_missing_linkage_blocks("action_intent_id")

    def test_reviewer_type_llm_blocks_record(self):
        decision = self._decision()
        decision["reviewer_trace"]["reviewer_type"] = "llm"
        self._assert_invalid(decision, "non_human_reviewer")

    def test_review_mode_automatic_blocks_record(self):
        decision = self._decision()
        decision["reviewer_trace"]["review_mode"] = "automatic"
        self._assert_invalid(decision, "automatic_review_mode")

    def test_reviewed_by_human_false_blocks_record(self):
        decision = self._decision()
        decision["decision"]["reviewed_by_human"] = False
        self._assert_invalid(decision, "reviewed_by_human_not_true")

    def test_approved_for_lesson_application_true_blocks_record(self):
        self._assert_decision_flag_blocks("approved_for_lesson_application", True, "approved_for_application_enabled")

    def test_approved_for_persistent_learning_true_blocks_record(self):
        self._assert_decision_flag_blocks(
            "approved_for_persistent_learning",
            True,
            "approved_for_persistent_learning_enabled",
        )

    def test_approved_for_memory_write_true_blocks_record(self):
        self._assert_decision_flag_blocks("approved_for_memory_write", True, "approved_for_memory_write_enabled")

    def test_approved_for_predictor_mutation_true_blocks_record(self):
        self._assert_decision_flag_blocks(
            "approved_for_predictor_mutation",
            True,
            "approved_for_predictor_mutation_enabled",
        )

    def test_allows_application_true_blocks_record(self):
        self._assert_scope_flag_blocks("allows_application", True, "allows_application_enabled")

    def test_allows_action_selection_influence_true_blocks_record(self):
        self._assert_scope_flag_blocks(
            "allows_action_selection_influence",
            True,
            "allows_action_selection_influence_enabled",
        )

    def test_allows_memory_write_true_blocks_record(self):
        self._assert_scope_flag_blocks("allows_memory_write", True, "allows_memory_write_enabled")

    def test_allows_persistent_rule_write_true_blocks_record(self):
        self._assert_scope_flag_blocks(
            "allows_persistent_rule_write",
            True,
            "allows_persistent_rule_write_enabled",
        )

    def test_allows_predictor_mutation_true_blocks_record(self):
        self._assert_scope_flag_blocks("allows_predictor_mutation", True, "allows_predictor_mutation_enabled")

    def test_behavior_preview_created_true_blocks_record(self):
        self._assert_boundary_flag_blocks("behavior_preview_created", True, "behavior_preview_created_enabled")

    def test_lesson_applied_true_blocks_record(self):
        self._assert_boundary_flag_blocks("lesson_applied", True, "lesson_applied_enabled")

    def test_action_selection_influence_nonzero_blocks_record(self):
        self._assert_boundary_flag_blocks(
            "action_selection_influence",
            1,
            "action_selection_influence_enabled",
        )

    def test_memory_write_true_blocks_record(self):
        self._assert_boundary_flag_blocks("memory_write", True, "memory_write_enabled")

    def test_predictor_modified_true_blocks_record(self):
        self._assert_boundary_flag_blocks("predictor_modified", True, "predictor_modified_enabled")

    def test_persistent_rule_write_true_blocks_record(self):
        self._assert_boundary_flag_blocks("persistent_rule_write", True, "persistent_rule_write_enabled")

    def test_trace_only_decision_false_blocks_record(self):
        self._assert_safety_flag_blocks("trace_only_decision", False, "trace_only_decision_not_true")

    def test_blocked_from_lesson_application_false_blocks_record(self):
        self._assert_safety_flag_blocks("blocked_from_lesson_application", False, "lesson_application_not_blocked")

    def test_blocked_from_action_selection_false_blocks_record(self):
        self._assert_safety_flag_blocks("blocked_from_action_selection", False, "action_selection_not_blocked")

    def test_blocked_from_action_behavior_change_false_blocks_record(self):
        self._assert_safety_flag_blocks(
            "blocked_from_action_behavior_change",
            False,
            "action_behavior_change_not_blocked",
        )

    def test_blocked_from_memory_write_false_blocks_record(self):
        self._assert_safety_flag_blocks("blocked_from_memory_write", False, "memory_write_not_blocked")

    def test_blocked_from_predictor_mutation_false_blocks_record(self):
        self._assert_safety_flag_blocks("blocked_from_predictor_mutation", False, "predictor_mutation_not_blocked")

    def test_blocked_from_persistent_rule_write_false_blocks_record(self):
        self._assert_safety_flag_blocks(
            "blocked_from_persistent_rule_write",
            False,
            "persistent_rule_write_not_blocked",
        )

    def test_demo_check_summary_has_expected_counts(self):
        result = run_lesson_candidate_human_review_decision_schema_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-lesson-candidate-human-review-decision-schema-check")
        self.assertEqual(result["flow"], "lesson_candidate_human_review_decision_schema_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["review_decision_record_count"], 13)
        self.assertEqual(summary["valid_review_decision_count"], 4)
        self.assertEqual(summary["invalid_review_decision_count"], 9)
        self.assertEqual(summary["approved_for_preview_count"], 1)
        self.assertEqual(summary["rejected_count"], 1)
        self.assertEqual(summary["needs_revision_count"], 1)
        self.assertEqual(summary["stale_count"], 1)
        self.assertGreaterEqual(summary["missing_evidence_linkage_blocked_count"], 1)
        self.assertGreaterEqual(summary["non_human_reviewer_blocked_count"], 1)
        self.assertGreaterEqual(summary["automatic_review_blocked_count"], 1)
        self.assertGreaterEqual(summary["approved_for_application_blocked_count"], 1)
        self.assertGreaterEqual(summary["memory_write_allowed_blocked_count"], 1)
        self.assertGreaterEqual(summary["predictor_mutation_allowed_blocked_count"], 1)
        self.assertGreaterEqual(summary["behavior_preview_created_blocked_count"], 1)
        self.assertGreaterEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertGreaterEqual(summary["action_selection_influence_blocked_count"], 1)
        for field in [
            "lesson_application_runtime_count",
            "memory_write_count",
            "predictor_modified_count",
            "persistent_rule_write_count",
            "action_selection_influence_count",
            "autonomy_enabled_count",
        ]:
            with self.subTest(field=field):
                self.assertEqual(summary[field], 0)
        self.assertTrue(boundary["human_manual_review_required"])
        self.assertFalse(boundary["approved_for_preview_is_application_approval"])
        self.assertFalse(boundary["behavior_preview_created"])
        self.assertFalse(boundary["lesson_application_runtime_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["llm_review_decision_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-lesson-candidate-human-review-decision-schema-check")

        self.assertEqual(result["command"], "run-lesson-candidate-human-review-decision-schema-check")
        self.assertEqual(result["summary"]["valid_review_decision_count"], 4)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-lesson-candidate-human-review-decision-schema-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-lesson-candidate-human-review-decision-schema-check")
        self.assertEqual(result["summary"]["approved_for_preview_count"], 1)

    def _assert_valid_status(self, status, *, allows_preview):
        decision = self._decision(status)
        validation = validate_lesson_candidate_human_review_decision(decision)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(validation["decision_status"], status)
        self.assertIs(validation["allows_preview"], allows_preview)
        self.assertFalse(validation["allows_application"])

    def _assert_missing_linkage_blocks(self, field):
        decision = self._decision()
        decision.pop(field)
        self._assert_invalid(decision, f"missing_source_linkage:{field}")

    def _assert_decision_flag_blocks(self, field, value, error_code):
        decision = self._decision()
        decision["decision"][field] = value
        self._assert_invalid(decision, error_code)

    def _assert_scope_flag_blocks(self, field, value, error_code):
        decision = self._decision()
        decision["decision_scope"][field] = value
        self._assert_invalid(decision, error_code)

    def _assert_boundary_flag_blocks(self, field, value, error_code):
        decision = self._decision()
        decision["boundary_summary"][field] = value
        self._assert_invalid(decision, error_code)

    def _assert_safety_flag_blocks(self, field, value, error_code):
        decision = self._decision()
        decision["safety_flags"][field] = value
        self._assert_invalid(decision, error_code)

    def _assert_invalid(self, decision, error_code):
        original = deepcopy(decision)
        validation = validate_lesson_candidate_human_review_decision(decision)

        self.assertEqual(decision, original)
        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
