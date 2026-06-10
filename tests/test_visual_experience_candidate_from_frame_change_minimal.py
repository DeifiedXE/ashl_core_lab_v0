import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.focus_candidate_from_change_trace import run_focus_candidate_from_change_trace_check
from ashl_core.focus_candidate_ranking_trace import run_focus_candidate_ranking_trace_check
from ashl_core.teaching_cli import run_command
from ashl_core.visual_experience_candidate_from_frame_change_minimal import (
    build_visual_experience_candidate,
    run_visual_experience_candidate_from_frame_change_minimal_check,
    validate_visual_experience_candidate,
)
from ashl_core.visual_frame_change_trace import run_visual_frame_change_trace_check


EXPECTED_FIELDS = {
    "visual_experience_candidate_id",
    "source_change_trace_id",
    "source_focus_candidate_id",
    "source_ranking_trace_id",
    "experience_type",
    "trace_only",
    "summary",
    "blocked_flags",
}


class VisualExperienceCandidateFromFrameChangeMinimalTests(unittest.TestCase):
    def _source_change(self):
        return deepcopy(run_visual_frame_change_trace_check()["change_records"][0])

    def _source_focus(self):
        return deepcopy(run_focus_candidate_from_change_trace_check()["focus_candidates"][0])

    def _source_ranking_trace(self):
        return deepcopy(run_focus_candidate_ranking_trace_check()["ranking_trace"])

    def _valid_candidate(self):
        return build_visual_experience_candidate(
            self._source_change(),
            self._source_focus(),
            self._source_ranking_trace(),
        )

    def test_valid_frame_change_trace_creates_visual_experience_candidate(self):
        candidate = build_visual_experience_candidate(self._source_change())
        validation = validate_visual_experience_candidate(candidate)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(candidate["source_change_trace_id"], "visual_frame_change_trace:001")

    def test_candidate_with_focus_candidate_is_valid(self):
        candidate = self._valid_candidate()
        validation = validate_visual_experience_candidate(candidate)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(candidate["experience_type"], "visual_change_with_focus_candidate")
        self.assertTrue(candidate["summary"]["focus_candidate_available"])
        self.assertTrue(candidate["summary"]["ranking_trace_available"])

    def test_candidate_without_focus_candidate_is_valid(self):
        candidate = build_visual_experience_candidate(self._source_change())
        validation = validate_visual_experience_candidate(candidate)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(candidate["experience_type"], "visual_change_without_focus_candidate")
        self.assertIsNone(candidate["source_focus_candidate_id"])
        self.assertIsNone(candidate["source_ranking_trace_id"])

    def test_record_has_only_expected_top_level_fields(self):
        candidate = self._valid_candidate()

        self.assertEqual(set(candidate), EXPECTED_FIELDS)
        self.assertEqual(len(candidate), 8)

    def test_trace_only_false_blocks(self):
        candidate = self._valid_candidate()
        candidate["trace_only"] = False
        self._assert_invalid(candidate, "trace_only_not_true")

    def test_unknown_experience_type_blocks(self):
        candidate = self._valid_candidate()
        candidate["experience_type"] = "semantic_scene_experience"
        self._assert_invalid(candidate, "unknown_experience_type")

    def test_missing_source_change_trace_id_blocks(self):
        candidate = self._valid_candidate()
        candidate["source_change_trace_id"] = ""
        self._assert_invalid(candidate, "source_change_trace_id_missing")

    def test_empty_human_readable_summary_blocks(self):
        candidate = self._valid_candidate()
        candidate["summary"]["human_readable"] = ""
        self._assert_invalid(candidate, "human_readable_empty_or_not_string")

    def test_blocked_flags_true_block(self):
        cases = {
            "object_recognition": "object_recognition_enabled",
            "semantic_labeling": "semantic_labeling_enabled",
            "active_focus_applied": "active_focus_applied_enabled",
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
        result = run_visual_experience_candidate_from_frame_change_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-visual-experience-candidate-from-frame-change-minimal-check")
        self.assertEqual(result["flow"], "visual_experience_candidate_from_frame_change_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["visual_experience_candidate_count"], 15)
        self.assertEqual(summary["valid_visual_experience_candidate_count"], 2)
        self.assertEqual(summary["invalid_visual_experience_candidate_count"], 13)
        self.assertEqual(summary["with_focus_candidate_count"], 1)
        self.assertEqual(summary["without_focus_candidate_count"], 1)
        self.assertEqual(summary["trace_only_false_blocked_count"], 1)
        self.assertEqual(summary["experience_type_blocked_count"], 1)
        self.assertEqual(summary["missing_source_change_trace_blocked_count"], 1)
        self.assertEqual(summary["empty_human_readable_blocked_count"], 1)
        self.assertEqual(summary["object_recognition_blocked_count"], 1)
        self.assertEqual(summary["semantic_labeling_blocked_count"], 1)
        self.assertEqual(summary["active_focus_applied_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["lesson_retained_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertTrue(boundary["minimal_record_shape"])
        self.assertEqual(boundary["top_level_field_count"], 8)
        self.assertFalse(boundary["object_recognition_added"])
        self.assertFalse(boundary["semantic_vision_added"])
        self.assertFalse(boundary["active_focus_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["retention_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-visual-experience-candidate-from-frame-change-minimal-check")

        self.assertEqual(result["command"], "run-visual-experience-candidate-from-frame-change-minimal-check")
        self.assertEqual(result["summary"]["valid_visual_experience_candidate_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-visual-experience-candidate-from-frame-change-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-visual-experience-candidate-from-frame-change-minimal-check")
        self.assertEqual(result["summary"]["visual_experience_candidate_count"], 15)

    def _assert_invalid(self, candidate, error_code):
        validation = validate_visual_experience_candidate(candidate)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
