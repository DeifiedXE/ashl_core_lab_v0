import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.teaching_cli import run_command
from ashl_core.visual_retained_experience_link_preview_minimal import (
    VISUAL_DEMO_EXACT_KEY,
    build_visual_retained_experience_link_preview,
    run_visual_retained_experience_link_preview_minimal_check,
    validate_visual_retained_experience_link_preview,
)
from ashl_core.visual_trace_as_lesson_evidence_minimal import (
    run_visual_trace_as_lesson_evidence_minimal_check,
)


EXPECTED_FIELDS = {
    "visual_retained_experience_link_preview_id",
    "source_visual_lesson_evidence_candidate_id",
    "source_retained_record_id",
    "match_status",
    "read_only",
    "match_rule",
    "human_summary",
    "blocked_flags",
}


class VisualRetainedExperienceLinkPreviewMinimalTests(unittest.TestCase):
    def _visual_evidence(self):
        result = run_visual_trace_as_lesson_evidence_minimal_check()
        return deepcopy(result["visual_lesson_evidence_candidates"][0])

    def _retained_record(self, exact_key=VISUAL_DEMO_EXACT_KEY):
        return {
            "retained_record_id": "retained_experience_demo_001",
            "source_experience_record_id": "session_experience_demo_001",
            "exact_key": exact_key,
            "experience_type": "lesson_effect_trace_difference",
            "retention_status": "retained",
            "retained_by": "mentor",
            "retention_reason": "mentor_text:approval",
            "source_snapshot": {
                "source_evidence_trace_id": "lesson_effect_evidence_demo_001",
                "source_bucket_candidate_id": "exact_key_bucket_candidate_demo_001",
                "original_retention_status": "not_retained",
            },
            "blocked_flags": {
                "action_selection_influence": False,
                "action_behavior_changed": False,
                "predictor_modified": False,
                "proof_of_learning_claim": False,
            },
        }

    def _valid_preview(self):
        return build_visual_retained_experience_link_preview(
            self._visual_evidence(),
            self._retained_record(),
        )

    def test_valid_visual_evidence_with_retained_match_creates_preview(self):
        preview = self._valid_preview()
        validation = validate_visual_retained_experience_link_preview(preview)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(preview["match_status"], "matched")
        self.assertEqual(preview["match_rule"], "same_exact_key_only")

    def test_valid_visual_evidence_without_retained_match_creates_preview(self):
        preview = build_visual_retained_experience_link_preview(
            self._visual_evidence(),
            self._retained_record("action_type:move|correction_type:avoid_same_retry|failure_type:blocked"),
        )
        validation = validate_visual_retained_experience_link_preview(preview)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(preview["match_status"], "not_matched")

    def test_record_has_only_expected_top_level_fields(self):
        preview = self._valid_preview()

        self.assertEqual(set(preview), EXPECTED_FIELDS)
        self.assertEqual(len(preview), 8)

    def test_match_rule_is_same_exact_key_only(self):
        preview = self._valid_preview()

        self.assertEqual(preview["match_rule"], "same_exact_key_only")

    def test_read_only_false_blocks(self):
        preview = self._valid_preview()
        preview["read_only"] = False
        self._assert_invalid(preview, "read_only_not_true")

    def test_unknown_match_status_blocks(self):
        preview = self._valid_preview()
        preview["match_status"] = "semantic_match"
        self._assert_invalid(preview, "unknown_match_status")

    def test_wrong_match_rule_blocks(self):
        preview = self._valid_preview()
        preview["match_rule"] = "semantic_similarity"
        self._assert_invalid(preview, "match_rule_not_same_exact_key_only")

    def test_missing_source_visual_lesson_evidence_candidate_id_blocks(self):
        preview = self._valid_preview()
        preview["source_visual_lesson_evidence_candidate_id"] = ""
        self._assert_invalid(preview, "source_visual_lesson_evidence_candidate_id_missing")

    def test_empty_visual_evidence_seen_blocks(self):
        preview = self._valid_preview()
        preview["human_summary"]["visual_evidence_seen"] = ""
        self._assert_invalid(preview, "visual_evidence_seen_empty_or_not_string")

    def test_empty_plain_result_blocks(self):
        preview = self._valid_preview()
        preview["human_summary"]["plain_result"] = ""
        self._assert_invalid(preview, "plain_result_empty_or_not_string")

    def test_blocked_flags_true_block(self):
        cases = {
            "semantic_match": "semantic_match_enabled",
            "fuzzy_match": "fuzzy_match_enabled",
            "vector_match": "vector_match_enabled",
            "lesson_applied": "lesson_applied_enabled",
            "action_selection_influence": "action_selection_influence_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
            "memory_write": "memory_write_enabled",
            "new_retention_written": "new_retention_written_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                preview = self._valid_preview()
                preview["blocked_flags"][flag] = True
                self._assert_invalid(preview, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_visual_retained_experience_link_preview_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-visual-retained-experience-link-preview-minimal-check")
        self.assertEqual(result["flow"], "visual_retained_experience_link_preview_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["visual_retained_experience_link_preview_count"], 18)
        self.assertEqual(summary["valid_visual_retained_experience_link_preview_count"], 2)
        self.assertEqual(summary["invalid_visual_retained_experience_link_preview_count"], 16)
        self.assertEqual(summary["matched_link_preview_count"], 1)
        self.assertEqual(summary["not_matched_link_preview_count"], 1)
        self.assertEqual(summary["read_only_false_blocked_count"], 1)
        self.assertEqual(summary["match_status_blocked_count"], 1)
        self.assertEqual(summary["match_rule_blocked_count"], 1)
        self.assertEqual(summary["missing_source_visual_evidence_blocked_count"], 1)
        self.assertEqual(summary["empty_visual_evidence_seen_blocked_count"], 1)
        self.assertEqual(summary["empty_plain_result_blocked_count"], 1)
        self.assertEqual(summary["semantic_match_blocked_count"], 1)
        self.assertEqual(summary["fuzzy_match_blocked_count"], 1)
        self.assertEqual(summary["vector_match_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["new_retention_written_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertTrue(boundary["same_exact_key_only"])
        self.assertFalse(boundary["writes_retained_jsonl"])
        self.assertFalse(boundary["semantic_matching_added"])
        self.assertFalse(boundary["fuzzy_retrieval_added"])
        self.assertFalse(boundary["vector_retrieval_added"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["new_retention_write_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-visual-retained-experience-link-preview-minimal-check")

        self.assertEqual(result["command"], "run-visual-retained-experience-link-preview-minimal-check")
        self.assertEqual(result["summary"]["valid_visual_retained_experience_link_preview_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-visual-retained-experience-link-preview-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-visual-retained-experience-link-preview-minimal-check")
        self.assertEqual(result["summary"]["visual_retained_experience_link_preview_count"], 18)

    def _assert_invalid(self, preview, error_code):
        validation = validate_visual_retained_experience_link_preview(preview)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
