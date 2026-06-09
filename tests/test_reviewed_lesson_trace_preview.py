import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.reviewed_lesson_trace_preview import (
    build_reviewed_lesson_trace_preview,
    run_reviewed_lesson_trace_preview_check,
    validate_reviewed_lesson_trace_preview,
)
from ashl_core.teaching_cli import run_command


class ReviewedLessonTracePreviewTests(unittest.TestCase):
    def _result(self):
        return run_reviewed_lesson_trace_preview_check()

    def _valid_preview(self):
        result = self._result()
        return next(
            preview
            for preview, validation in zip(result["preview_records"], result["validation_results"])
            if validation["valid"]
        )

    def _source_candidate(self):
        return deepcopy(self._result()["source_lesson_candidate"])

    def _decision(self, status="approved_for_preview"):
        result = self._result()
        return deepcopy(
            next(decision for decision in result["source_review_decisions"] if decision["decision"]["status"] == status)
        )

    def test_approved_for_preview_creates_valid_trace_preview(self):
        preview = build_reviewed_lesson_trace_preview(self._source_candidate(), self._decision())
        validation = validate_reviewed_lesson_trace_preview(preview)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertTrue(preview["preview_status"]["created"])
        self.assertEqual(preview["preview_status"]["source_decision_status"], "approved_for_preview")
        self.assertEqual(preview["preview_content"]["preview_type"], "precondition_or_correction_trace")
        self.assertFalse(preview["preview_status"]["applied"])
        self.assertFalse(preview["preview_content"]["changes_action_selection"])
        self.assertFalse(preview["preview_content"]["changes_action_behavior"])
        self.assertFalse(preview["preview_content"]["writes_memory"])
        self.assertFalse(preview["preview_content"]["mutates_predictor"])
        self.assertFalse(preview["preview_content"]["creates_persistent_rule"])

    def test_rejected_needs_revision_and_stale_do_not_create_valid_preview(self):
        expected = {
            "rejected": "rejected_decision_blocked",
            "needs_revision": "needs_revision_decision_blocked",
            "stale": "stale_decision_blocked",
        }
        for status, error_code in expected.items():
            with self.subTest(status=status):
                preview = build_reviewed_lesson_trace_preview(self._source_candidate(), self._decision(status))
                validation = validate_reviewed_lesson_trace_preview(preview)

                self.assertFalse(preview["preview_status"]["created"])
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_missing_review_decision_blocks_preview(self):
        preview = build_reviewed_lesson_trace_preview(self._source_candidate(), None)
        validation = validate_reviewed_lesson_trace_preview(preview)

        self.assertFalse(preview["preview_status"]["created"])
        self.assertFalse(validation["valid"])
        self.assertIn("missing_review_decision", validation["error_codes"])

    def test_source_linkage_mismatch_blocks_preview(self):
        preview = self._valid_preview()
        preview["source_trace"]["source_lesson_candidate_id"] = "other"
        validation = validate_reviewed_lesson_trace_preview(preview)

        self.assertFalse(validation["valid"])
        self.assertIn("source_linkage_mismatch", validation["error_codes"])

    def test_unknown_preview_type_blocks_preview(self):
        self._assert_content_flag_blocks("preview_type", "free_form_trace", "unknown_preview_type")

    def test_lesson_application_allowed_blocks_preview(self):
        self._assert_boundary_flag_blocks(
            "lesson_application_allowed",
            True,
            "lesson_application_allowed_enabled",
        )

    def test_lesson_applied_blocks_preview(self):
        self._assert_boundary_flag_blocks("lesson_applied", True, "lesson_applied_enabled")

    def test_action_selection_influence_blocks_preview(self):
        self._assert_boundary_flag_blocks(
            "action_selection_influence",
            True,
            "action_selection_influence_enabled",
        )

    def test_action_behavior_changed_blocks_preview(self):
        self._assert_boundary_flag_blocks(
            "action_behavior_changed",
            True,
            "action_behavior_changed_enabled",
        )

    def test_memory_write_blocks_preview(self):
        self._assert_boundary_flag_blocks("memory_write", True, "memory_write_enabled")

    def test_predictor_modified_blocks_preview(self):
        self._assert_boundary_flag_blocks("predictor_modified", True, "predictor_modified_enabled")

    def test_persistent_rule_write_blocks_preview(self):
        self._assert_boundary_flag_blocks("persistent_rule_write", True, "persistent_rule_write_enabled")

    def test_persistent_learning_blocks_preview(self):
        self._assert_boundary_flag_blocks("persistent_learning", True, "persistent_learning_enabled")

    def test_trace_only_preview_false_blocks_preview(self):
        self._assert_boundary_flag_blocks("trace_only_preview", False, "trace_only_preview_not_true")

    def test_content_side_effect_flags_block_preview(self):
        for field, error_code in [
            ("changes_action_selection", "action_selection_influence_enabled"),
            ("changes_action_behavior", "action_behavior_changed_enabled"),
            ("writes_memory", "memory_write_enabled"),
            ("mutates_predictor", "predictor_modified_enabled"),
            ("creates_persistent_rule", "persistent_rule_write_enabled"),
        ]:
            with self.subTest(field=field):
                self._assert_content_flag_blocks(field, True, error_code)

    def test_required_safety_flags_block_preview_when_false(self):
        for field, error_code in [
            ("blocked_from_lesson_application", "lesson_application_not_blocked"),
            ("blocked_from_action_selection", "action_selection_not_blocked"),
            ("blocked_from_action_behavior_change", "action_behavior_change_not_blocked"),
            ("blocked_from_memory_write", "memory_write_not_blocked"),
            ("blocked_from_predictor_mutation", "predictor_mutation_not_blocked"),
            ("blocked_from_persistent_rule_write", "persistent_rule_write_not_blocked"),
        ]:
            with self.subTest(field=field):
                preview = self._valid_preview()
                preview["safety_flags"][field] = False
                validation = validate_reviewed_lesson_trace_preview(preview)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_demo_check_summary_has_expected_counts(self):
        result = self._result()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-reviewed-lesson-trace-preview-check")
        self.assertEqual(result["flow"], "reviewed_lesson_trace_preview_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["review_decision_record_count"], 13)
        self.assertEqual(summary["valid_review_decision_count"], 4)
        self.assertEqual(summary["approved_for_preview_count"], 1)
        self.assertEqual(summary["rejected_count"], 1)
        self.assertEqual(summary["needs_revision_count"], 1)
        self.assertEqual(summary["stale_count"], 1)
        self.assertEqual(summary["preview_record_count"], 22)
        self.assertEqual(summary["valid_preview_count"], 1)
        self.assertEqual(summary["invalid_preview_count"], 21)
        self.assertEqual(summary["blocked_preview_count"], 21)
        for field in [
            "rejected_preview_blocked_count",
            "needs_revision_preview_blocked_count",
            "stale_preview_blocked_count",
            "missing_review_decision_blocked_count",
            "source_linkage_mismatch_blocked_count",
            "unknown_preview_type_blocked_count",
            "lesson_application_allowed_blocked_count",
            "lesson_applied_blocked_count",
            "action_selection_influence_blocked_count",
            "action_behavior_changed_blocked_count",
            "memory_write_blocked_count",
            "predictor_mutation_blocked_count",
            "persistent_rule_write_blocked_count",
            "persistent_learning_blocked_count",
        ]:
            with self.subTest(field=field):
                self.assertGreaterEqual(summary[field], 1)
        for field in [
            "lesson_application_runtime_count",
            "action_selection_influence_count",
            "action_behavior_changed_count",
            "memory_write_count",
            "predictor_modified_count",
            "persistent_rule_write_count",
            "autonomy_enabled_count",
        ]:
            with self.subTest(field=field):
                self.assertEqual(summary[field], 0)
        self.assertTrue(boundary["trace_only_preview"])
        self.assertTrue(boundary["approved_for_preview_only"])
        self.assertFalse(boundary["lesson_application_allowed"])
        self.assertFalse(boundary["lesson_applied"])
        self.assertFalse(boundary["action_selection_influence"])
        self.assertFalse(boundary["action_behavior_changed"])
        self.assertFalse(boundary["memory_write"])
        self.assertFalse(boundary["predictor_modified"])
        self.assertFalse(boundary["persistent_rule_write"])
        self.assertFalse(boundary["persistent_learning"])
        self.assertFalse(boundary["llm_planning_used"])
        self.assertFalse(boundary["pathfinding_used"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-reviewed-lesson-trace-preview-check")

        self.assertEqual(result["command"], "run-reviewed-lesson-trace-preview-check")
        self.assertEqual(result["summary"]["valid_preview_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-reviewed-lesson-trace-preview-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-reviewed-lesson-trace-preview-check")
        self.assertEqual(result["summary"]["blocked_preview_count"], 21)

    def _assert_boundary_flag_blocks(self, field, value, error_code):
        preview = self._valid_preview()
        preview["boundary_summary"][field] = value
        validation = validate_reviewed_lesson_trace_preview(preview)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def _assert_content_flag_blocks(self, field, value, error_code):
        preview = self._valid_preview()
        preview["preview_content"][field] = value
        validation = validate_reviewed_lesson_trace_preview(preview)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
