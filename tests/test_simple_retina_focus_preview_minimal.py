import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.focus_candidate_from_change_trace import run_focus_candidate_from_change_trace_check
from ashl_core.focus_candidate_ranking_trace import run_focus_candidate_ranking_trace_check
from ashl_core.simple_retina_focus_preview_minimal import (
    build_retina_focus_preview,
    run_simple_retina_focus_preview_minimal_check,
    validate_retina_focus_preview,
)
from ashl_core.teaching_cli import run_command
from ashl_core.visual_experience_candidate_from_frame_change_minimal import (
    run_visual_experience_candidate_from_frame_change_minimal_check,
)


EXPECTED_FIELDS = {
    "retina_focus_preview_id",
    "source_visual_experience_candidate_id",
    "source_focus_candidate_id",
    "source_ranking_trace_id",
    "preview_type",
    "read_only",
    "human_summary",
    "blocked_flags",
}


class SimpleRetinaFocusPreviewMinimalTests(unittest.TestCase):
    def _visual_candidate(self, *, with_focus=True):
        result = run_visual_experience_candidate_from_frame_change_minimal_check()
        return deepcopy(
            next(
                candidate
                for candidate in result["visual_experience_candidates"]
                if (candidate["source_focus_candidate_id"] is not None) is with_focus
            )
        )

    def _source_focus(self):
        return deepcopy(run_focus_candidate_from_change_trace_check()["focus_candidates"][0])

    def _source_ranking_trace(self):
        return deepcopy(run_focus_candidate_ranking_trace_check()["ranking_trace"])

    def _valid_preview(self):
        return build_retina_focus_preview(
            self._visual_candidate(with_focus=True),
            self._source_focus(),
            self._source_ranking_trace(),
        )

    def test_valid_visual_experience_candidate_creates_retina_focus_preview(self):
        preview = build_retina_focus_preview(self._visual_candidate(with_focus=False))
        validation = validate_retina_focus_preview(preview)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertTrue(preview["source_visual_experience_candidate_id"])

    def test_preview_with_focus_candidate_is_valid(self):
        preview = self._valid_preview()
        validation = validate_retina_focus_preview(preview)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(preview["preview_type"], "visual_focus_readback")
        self.assertTrue(preview["human_summary"]["focus_available"])
        self.assertTrue(preview["human_summary"]["ranking_available"])

    def test_preview_without_focus_candidate_is_valid(self):
        preview = build_retina_focus_preview(self._visual_candidate(with_focus=False))
        validation = validate_retina_focus_preview(preview)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(preview["preview_type"], "visual_change_readback_without_focus")
        self.assertIsNone(preview["source_focus_candidate_id"])
        self.assertIsNone(preview["source_ranking_trace_id"])

    def test_record_has_only_expected_top_level_fields(self):
        preview = self._valid_preview()

        self.assertEqual(set(preview), EXPECTED_FIELDS)
        self.assertEqual(len(preview), 8)

    def test_human_summary_has_required_text(self):
        preview = self._valid_preview()
        summary = preview["human_summary"]

        self.assertTrue(summary["what_changed"])
        self.assertTrue(summary["what_focus_points_to"])
        self.assertTrue(summary["plain_result"])

    def test_read_only_false_blocks(self):
        preview = self._valid_preview()
        preview["read_only"] = False
        self._assert_invalid(preview, "read_only_not_true")

    def test_unknown_preview_type_blocks(self):
        preview = self._valid_preview()
        preview["preview_type"] = "semantic_object_focus_preview"
        self._assert_invalid(preview, "unknown_preview_type")

    def test_missing_source_visual_experience_candidate_id_blocks(self):
        preview = self._valid_preview()
        preview["source_visual_experience_candidate_id"] = ""
        self._assert_invalid(preview, "source_visual_experience_candidate_id_missing")

    def test_empty_what_changed_blocks(self):
        preview = self._valid_preview()
        preview["human_summary"]["what_changed"] = ""
        self._assert_invalid(preview, "what_changed_empty_or_not_string")

    def test_empty_plain_result_blocks(self):
        preview = self._valid_preview()
        preview["human_summary"]["plain_result"] = ""
        self._assert_invalid(preview, "plain_result_empty_or_not_string")

    def test_blocked_flags_true_block(self):
        cases = {
            "object_recognition": "object_recognition_enabled",
            "semantic_labeling": "semantic_labeling_enabled",
            "active_focus_applied": "active_focus_applied_enabled",
            "focus_applied": "focus_applied_enabled",
            "attention_control": "attention_control_enabled",
            "action_selection_influence": "action_selection_influence_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
            "memory_write": "memory_write_enabled",
            "lesson_retained": "lesson_retained_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                preview = self._valid_preview()
                preview["blocked_flags"][flag] = True
                self._assert_invalid(preview, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_simple_retina_focus_preview_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-simple-retina-focus-preview-minimal-check")
        self.assertEqual(result["flow"], "simple_retina_focus_preview_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["retina_focus_preview_count"], 17)
        self.assertEqual(summary["valid_retina_focus_preview_count"], 2)
        self.assertEqual(summary["invalid_retina_focus_preview_count"], 15)
        self.assertEqual(summary["with_focus_preview_count"], 1)
        self.assertEqual(summary["without_focus_preview_count"], 1)
        self.assertEqual(summary["read_only_false_blocked_count"], 1)
        self.assertEqual(summary["preview_type_blocked_count"], 1)
        self.assertEqual(summary["missing_source_visual_experience_blocked_count"], 1)
        self.assertEqual(summary["empty_what_changed_blocked_count"], 1)
        self.assertEqual(summary["empty_plain_result_blocked_count"], 1)
        self.assertEqual(summary["object_recognition_blocked_count"], 1)
        self.assertEqual(summary["semantic_labeling_blocked_count"], 1)
        self.assertEqual(summary["active_focus_applied_blocked_count"], 1)
        self.assertEqual(summary["focus_applied_blocked_count"], 1)
        self.assertEqual(summary["attention_control_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["lesson_retained_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertTrue(boundary["read_only"])
        self.assertEqual(boundary["top_level_field_count"], 8)
        self.assertFalse(boundary["object_recognition_added"])
        self.assertFalse(boundary["semantic_vision_added"])
        self.assertFalse(boundary["active_focus_added"])
        self.assertFalse(boundary["focus_applied_added"])
        self.assertFalse(boundary["attention_control_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-simple-retina-focus-preview-minimal-check")

        self.assertEqual(result["command"], "run-simple-retina-focus-preview-minimal-check")
        self.assertEqual(result["summary"]["valid_retina_focus_preview_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-simple-retina-focus-preview-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-simple-retina-focus-preview-minimal-check")
        self.assertEqual(result["summary"]["retina_focus_preview_count"], 17)

    def _assert_invalid(self, preview, error_code):
        validation = validate_retina_focus_preview(preview)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
