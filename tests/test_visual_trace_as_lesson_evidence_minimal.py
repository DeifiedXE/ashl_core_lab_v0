import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.simple_retina_focus_preview_minimal import run_simple_retina_focus_preview_minimal_check
from ashl_core.teaching_cli import run_command
from ashl_core.visual_trace_as_lesson_evidence_minimal import (
    build_visual_lesson_evidence_candidate,
    run_visual_trace_as_lesson_evidence_minimal_check,
    validate_visual_lesson_evidence_candidate,
)


EXPECTED_FIELDS = {
    "visual_lesson_evidence_candidate_id",
    "source_retina_focus_preview_id",
    "source_visual_experience_candidate_id",
    "evidence_type",
    "trace_only",
    "lesson_review_use",
    "human_summary",
    "blocked_flags",
}


class VisualTraceAsLessonEvidenceMinimalTests(unittest.TestCase):
    def _preview(self, *, with_focus=True):
        result = run_simple_retina_focus_preview_minimal_check()
        return deepcopy(
            next(
                preview
                for preview in result["retina_focus_previews"]
                if (preview["human_summary"]["focus_available"] is True) is with_focus
            )
        )

    def _valid_candidate(self):
        return build_visual_lesson_evidence_candidate(self._preview(with_focus=True))

    def test_valid_retina_focus_preview_creates_visual_lesson_evidence_candidate(self):
        candidate = build_visual_lesson_evidence_candidate(self._preview(with_focus=False))
        validation = validate_visual_lesson_evidence_candidate(candidate)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertTrue(candidate["source_retina_focus_preview_id"])

    def test_candidate_with_focus_preview_is_valid(self):
        candidate = self._valid_candidate()
        validation = validate_visual_lesson_evidence_candidate(candidate)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(candidate["evidence_type"], "visual_trace_focus_preview")

    def test_candidate_without_focus_preview_is_valid(self):
        candidate = build_visual_lesson_evidence_candidate(self._preview(with_focus=False))
        validation = validate_visual_lesson_evidence_candidate(candidate)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(candidate["evidence_type"], "visual_trace_change_preview")

    def test_record_has_only_expected_top_level_fields(self):
        candidate = self._valid_candidate()

        self.assertEqual(set(candidate), EXPECTED_FIELDS)
        self.assertEqual(len(candidate), 8)

    def test_review_use_flags_require_human_review_without_lesson_creation(self):
        candidate = self._valid_candidate()
        use = candidate["lesson_review_use"]

        self.assertTrue(use["usable_as_evidence"])
        self.assertTrue(use["requires_human_review"])
        self.assertFalse(use["can_create_lesson_candidate"])
        self.assertFalse(use["can_apply_lesson"])

    def test_trace_only_false_blocks(self):
        candidate = self._valid_candidate()
        candidate["trace_only"] = False
        self._assert_invalid(candidate, "trace_only_not_true")

    def test_unknown_evidence_type_blocks(self):
        candidate = self._valid_candidate()
        candidate["evidence_type"] = "semantic_visual_scene_evidence"
        self._assert_invalid(candidate, "unknown_evidence_type")

    def test_missing_source_retina_focus_preview_id_blocks(self):
        candidate = self._valid_candidate()
        candidate["source_retina_focus_preview_id"] = ""
        self._assert_invalid(candidate, "source_retina_focus_preview_id_missing")

    def test_lesson_review_use_invalid_values_block(self):
        cases = {
            "usable_as_evidence": (False, "usable_as_evidence_not_true"),
            "requires_human_review": (False, "requires_human_review_not_true"),
            "can_create_lesson_candidate": (True, "can_create_lesson_candidate_not_false"),
            "can_apply_lesson": (True, "can_apply_lesson_not_false"),
        }
        for field, (value, error_code) in cases.items():
            with self.subTest(field=field):
                candidate = self._valid_candidate()
                candidate["lesson_review_use"][field] = value
                self._assert_invalid(candidate, error_code)

    def test_empty_observed_visual_change_blocks(self):
        candidate = self._valid_candidate()
        candidate["human_summary"]["observed_visual_change"] = ""
        self._assert_invalid(candidate, "observed_visual_change_empty_or_not_string")

    def test_empty_plain_result_blocks(self):
        candidate = self._valid_candidate()
        candidate["human_summary"]["plain_result"] = ""
        self._assert_invalid(candidate, "plain_result_empty_or_not_string")

    def test_blocked_flags_true_block(self):
        cases = {
            "object_recognition": "object_recognition_enabled",
            "semantic_labeling": "semantic_labeling_enabled",
            "active_focus_applied": "active_focus_applied_enabled",
            "lesson_candidate_created": "lesson_candidate_created_enabled",
            "lesson_applied": "lesson_applied_enabled",
            "action_selection_influence": "action_selection_influence_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
            "memory_write": "memory_write_enabled",
            "lesson_retained": "lesson_retained_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                candidate = self._valid_candidate()
                candidate["blocked_flags"][flag] = True
                self._assert_invalid(candidate, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_visual_trace_as_lesson_evidence_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-visual-trace-as-lesson-evidence-minimal-check")
        self.assertEqual(result["flow"], "visual_trace_as_lesson_evidence_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["visual_lesson_evidence_candidate_count"], 22)
        self.assertEqual(summary["valid_visual_lesson_evidence_candidate_count"], 2)
        self.assertEqual(summary["invalid_visual_lesson_evidence_candidate_count"], 20)
        self.assertEqual(summary["with_focus_evidence_count"], 1)
        self.assertEqual(summary["without_focus_evidence_count"], 1)
        self.assertEqual(summary["trace_only_false_blocked_count"], 1)
        self.assertEqual(summary["evidence_type_blocked_count"], 1)
        self.assertEqual(summary["missing_source_preview_blocked_count"], 1)
        self.assertEqual(summary["usable_as_evidence_false_blocked_count"], 1)
        self.assertEqual(summary["requires_human_review_false_blocked_count"], 1)
        self.assertEqual(summary["can_create_lesson_candidate_blocked_count"], 1)
        self.assertEqual(summary["can_apply_lesson_blocked_count"], 1)
        self.assertEqual(summary["empty_observed_visual_change_blocked_count"], 1)
        self.assertEqual(summary["empty_plain_result_blocked_count"], 1)
        self.assertEqual(summary["object_recognition_blocked_count"], 1)
        self.assertEqual(summary["semantic_labeling_blocked_count"], 1)
        self.assertEqual(summary["active_focus_applied_blocked_count"], 1)
        self.assertEqual(summary["lesson_candidate_created_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["lesson_retained_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertTrue(boundary["requires_human_review"])
        self.assertFalse(boundary["automatic_lesson_candidate_creation_added"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["object_recognition_added"])
        self.assertFalse(boundary["semantic_vision_added"])
        self.assertFalse(boundary["active_focus_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["retention_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-visual-trace-as-lesson-evidence-minimal-check")

        self.assertEqual(result["command"], "run-visual-trace-as-lesson-evidence-minimal-check")
        self.assertEqual(result["summary"]["valid_visual_lesson_evidence_candidate_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-visual-trace-as-lesson-evidence-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-visual-trace-as-lesson-evidence-minimal-check")
        self.assertEqual(result["summary"]["visual_lesson_evidence_candidate_count"], 22)

    def _assert_invalid(self, candidate, error_code):
        validation = validate_visual_lesson_evidence_candidate(candidate)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
