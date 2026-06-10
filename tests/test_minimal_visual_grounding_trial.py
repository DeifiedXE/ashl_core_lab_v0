import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.minimal_visual_grounding_trial import (
    build_minimal_visual_grounding_trial,
    run_minimal_visual_grounding_trial_check,
    validate_minimal_visual_grounding_trial,
)
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "trial_id",
    "demo_input",
    "source_ids",
    "read_only",
    "human_summary",
    "trial_result",
    "blocked_flags",
}


class MinimalVisualGroundingTrialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_minimal_visual_grounding_trial_check()

    def _trial(self, match_status="matched"):
        for trial in self.result["minimal_visual_grounding_trials"]:
            if trial["human_summary"]["retained_match_status"] == match_status:
                return deepcopy(trial)
        raise AssertionError(f"missing trial: {match_status}")

    def test_valid_minimal_visual_grounding_trial_is_created(self):
        trial = build_minimal_visual_grounding_trial()
        validation = validate_minimal_visual_grounding_trial(trial)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(trial["human_summary"]["retained_match_status"], "matched")

    def test_valid_not_matched_minimal_visual_grounding_trial_is_created(self):
        trial = self._trial("not_matched")
        validation = validate_minimal_visual_grounding_trial(trial)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(trial["human_summary"]["retained_match_status"], "not_matched")

    def test_record_has_only_expected_top_level_fields(self):
        trial = self._trial()

        self.assertEqual(set(trial), EXPECTED_FIELDS)
        self.assertEqual(len(trial), 7)

    def test_human_summary_includes_expected_fields(self):
        summary = self._trial()["human_summary"]

        self.assertIn("what_happened", summary)
        self.assertIn("what_was_noticed", summary)
        self.assertIn("what_focus_preview_says", summary)
        self.assertIn("what_evidence_says", summary)
        self.assertIn("retained_match_status", summary)
        self.assertIn("plain_result", summary)

    def test_trial_result_flags_are_true(self):
        trial_result = self._trial()["trial_result"]

        self.assertTrue(trial_result["visual_change_observed"])
        self.assertTrue(trial_result["focus_preview_available"])
        self.assertTrue(trial_result["lesson_evidence_available"])
        self.assertTrue(trial_result["retained_link_preview_available"])
        self.assertTrue(trial_result["same_exact_key_only"])

    def test_read_only_false_blocks(self):
        trial = self._trial()
        trial["read_only"] = False
        self._assert_invalid(trial, "read_only_not_true")

    def test_wrong_input_type_blocks(self):
        trial = self._trial()
        trial["demo_input"]["input_type"] = "semantic_scene_change"
        self._assert_invalid(trial, "input_type_not_controlled_symbolic_visual_change")

    def test_missing_source_id_blocks(self):
        trial = self._trial()
        trial["source_ids"]["visual_experience_candidate_id"] = ""
        self._assert_invalid(trial, "missing_source_id:visual_experience_candidate_id")

    def test_empty_what_happened_blocks(self):
        trial = self._trial()
        trial["human_summary"]["what_happened"] = ""
        self._assert_invalid(trial, "what_happened_empty_or_not_string")

    def test_empty_plain_result_blocks(self):
        trial = self._trial()
        trial["human_summary"]["plain_result"] = ""
        self._assert_invalid(trial, "plain_result_empty_or_not_string")

    def test_bad_retained_match_status_blocks(self):
        trial = self._trial()
        trial["human_summary"]["retained_match_status"] = "semantic_match"
        self._assert_invalid(trial, "retained_match_status_not_matched_or_not_matched")

    def test_trial_result_false_blocks(self):
        cases = {
            "visual_change_observed": "visual_change_observed_not_true",
            "focus_preview_available": "focus_preview_available_not_true",
            "lesson_evidence_available": "lesson_evidence_available_not_true",
            "retained_link_preview_available": "retained_link_preview_available_not_true",
            "same_exact_key_only": "same_exact_key_only_not_true",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                trial = self._trial()
                trial["trial_result"][flag] = False
                self._assert_invalid(trial, error_code)

    def test_blocked_flags_true_block(self):
        cases = {
            "object_recognition": "object_recognition_enabled",
            "semantic_vision": "semantic_vision_enabled",
            "active_focus_applied": "active_focus_applied_enabled",
            "attention_control": "attention_control_enabled",
            "lesson_candidate_created": "lesson_candidate_created_enabled",
            "lesson_applied": "lesson_applied_enabled",
            "action_selection_influence": "action_selection_influence_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
            "memory_write": "memory_write_enabled",
            "new_retention_written": "new_retention_written_enabled",
            "semantic_match": "semantic_match_enabled",
            "fuzzy_match": "fuzzy_match_enabled",
            "vector_match": "vector_match_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                trial = self._trial()
                trial["blocked_flags"][flag] = True
                self._assert_invalid(trial, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]
        boundary = self.result["boundary_check"]

        self.assertEqual(self.result["command"], "run-minimal-visual-grounding-trial-check")
        self.assertEqual(self.result["flow"], "minimal_visual_grounding_trial_v0")
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["minimal_visual_grounding_trial_count"], 28)
        self.assertEqual(summary["valid_minimal_visual_grounding_trial_count"], 2)
        self.assertEqual(summary["invalid_minimal_visual_grounding_trial_count"], 26)
        self.assertEqual(summary["matched_trial_count"], 1)
        self.assertEqual(summary["not_matched_trial_count"], 1)
        self.assertEqual(summary["read_only_false_blocked_count"], 1)
        self.assertEqual(summary["input_type_blocked_count"], 1)
        self.assertEqual(summary["missing_source_id_blocked_count"], 1)
        self.assertEqual(summary["empty_what_happened_blocked_count"], 1)
        self.assertEqual(summary["empty_plain_result_blocked_count"], 1)
        self.assertEqual(summary["retained_match_status_blocked_count"], 1)
        self.assertEqual(summary["visual_change_observed_false_blocked_count"], 1)
        self.assertEqual(summary["focus_preview_available_false_blocked_count"], 1)
        self.assertEqual(summary["lesson_evidence_available_false_blocked_count"], 1)
        self.assertEqual(summary["retained_link_preview_available_false_blocked_count"], 1)
        self.assertEqual(summary["same_exact_key_only_false_blocked_count"], 1)
        self.assertEqual(summary["object_recognition_blocked_count"], 1)
        self.assertEqual(summary["semantic_vision_blocked_count"], 1)
        self.assertEqual(summary["active_focus_applied_blocked_count"], 1)
        self.assertEqual(summary["attention_control_blocked_count"], 1)
        self.assertEqual(summary["lesson_candidate_created_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["new_retention_written_blocked_count"], 1)
        self.assertEqual(summary["semantic_match_blocked_count"], 1)
        self.assertEqual(summary["fuzzy_match_blocked_count"], 1)
        self.assertEqual(summary["vector_match_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertEqual(summary["object_recognition_count"], 0)
        self.assertEqual(summary["semantic_vision_count"], 0)
        self.assertEqual(summary["active_focus_applied_count"], 0)
        self.assertEqual(summary["attention_control_count"], 0)
        self.assertEqual(summary["lesson_candidate_created_count"], 0)
        self.assertEqual(summary["lesson_applied_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["action_behavior_changed_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["new_retention_written_count"], 0)
        self.assertEqual(summary["semantic_match_count"], 0)
        self.assertEqual(summary["fuzzy_match_count"], 0)
        self.assertEqual(summary["vector_match_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertEqual(summary["proof_of_learning_claim_count"], 0)
        self.assertTrue(boundary["read_only"])
        self.assertTrue(boundary["same_exact_key_only"])
        self.assertFalse(boundary["object_recognition_added"])
        self.assertFalse(boundary["semantic_vision_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["new_retention_write_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-minimal-visual-grounding-trial-check")

        self.assertEqual(result["command"], "run-minimal-visual-grounding-trial-check")
        self.assertEqual(result["summary"]["valid_minimal_visual_grounding_trial_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-minimal-visual-grounding-trial-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-minimal-visual-grounding-trial-check")
        self.assertEqual(result["summary"]["minimal_visual_grounding_trial_count"], 28)
        self.assertEqual(len(result["valid_human_summaries"]), 2)

    def _assert_invalid(self, trial, error_code):
        validation = validate_minimal_visual_grounding_trial(trial)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
