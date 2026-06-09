import json
import subprocess
import sys
import unittest

from ashl_core.approved_candidate_preview import (
    build_approved_candidate_preview,
    run_approved_candidate_preview_check,
)
from ashl_core.rule_candidate_from_mismatch import run_rule_candidate_from_mismatch_check
from ashl_core.rule_candidate_review_gate import enter_review, review_candidate
from ashl_core.teaching_cli import run_command


class ApprovedCandidatePreviewTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_approved_candidate_preview_check()

        self.assertEqual(result["command"], "run-approved-candidate-preview-check")
        self.assertEqual(result["flow"], "approved_candidate_preview_v0")
        self.assertEqual(result["status"], "ok")
        self.assertIn("preview_results", result)
        self.assertIn("summary", result)
        self.assertIn("boundary_check", result)

    def test_approved_outcome_revision_creates_preview(self):
        preview = self._preview("approved_outcome_revision_preview")

        self.assertTrue(preview["preview_created"])
        self.assertEqual(preview["preview_type"], "rule_revision_preview")
        self.assertIn("predicted_outcome_type", preview["changed_fields"])
        self.assertIn("predicted_primary_reason", preview["changed_fields"])
        self.assertEqual(preview["proposed_state"]["predicted_outcome_type"], "blocked")
        self.assertEqual(preview["proposed_state"]["predicted_primary_reason"], "front_cell_wall")

    def test_approved_reason_revision_creates_preview(self):
        preview = self._preview("approved_reason_revision_preview")

        self.assertTrue(preview["preview_created"])
        self.assertEqual(preview["preview_type"], "rule_revision_preview")
        self.assertNotIn("predicted_outcome_type", preview["changed_fields"])
        self.assertIn("predicted_primary_reason", preview["changed_fields"])
        self.assertEqual(preview["proposed_state"]["predicted_outcome_type"], "moved")
        self.assertEqual(preview["proposed_state"]["predicted_primary_reason"], "front_cell_passage_crossed")

    def test_approved_unknown_context_creates_new_entry_preview(self):
        preview = self._preview("approved_unknown_context_preview")

        self.assertTrue(preview["preview_created"])
        self.assertEqual(preview["preview_type"], "new_prediction_entry_preview")
        self.assertIn("new_prediction_entry", preview["changed_fields"])
        self.assertIsNone(preview["current_state"])
        self.assertEqual(preview["proposed_state"]["predicted_outcome_type"], "moved")

    def test_pending_candidate_preview_is_blocked(self):
        preview = self._preview("pending_candidate_preview_blocked")

        self.assertFalse(preview["preview_created"])
        self.assertEqual(preview["preview_blocked_reason"], "candidate_not_approved")
        self.assertFalse(preview["applied_now"])

    def test_rejected_candidate_preview_is_blocked(self):
        preview = self._preview("rejected_candidate_preview_blocked")

        self.assertFalse(preview["preview_created"])
        self.assertEqual(preview["preview_blocked_reason"], "candidate_not_approved")
        self.assertFalse(preview["applied_now"])

    def test_no_preview_applies_or_modifies_now(self):
        previews = [item["preview"] for item in run_approved_candidate_preview_check()["preview_results"]]

        self.assertTrue(all(preview["applied_now"] is False for preview in previews))
        self.assertTrue(all(preview["predictor_modified_now"] is False for preview in previews))
        self.assertTrue(all(preview["would_modify_action_selection"] is False for preview in previews))
        self.assertTrue(all(preview["would_write_lesson_store"] is False for preview in previews))
        self.assertTrue(all(preview["would_write_memory_layer"] is False for preview in previews))

    def test_helper_blocks_non_approved_candidate(self):
        pending = enter_review(self._source_candidate("outcome_mismatch_candidate"))["candidate_after"]
        preview = build_approved_candidate_preview(
            pending,
            {
                "predicted_outcome_type": "moved",
                "predicted_primary_reason": "front_cell_empty_walkable",
            },
        )

        self.assertFalse(preview["preview_created"])
        self.assertEqual(preview["preview_blocked_reason"], "candidate_not_approved")
        self.assertFalse(preview["application_allowed_later"])
        self.assertFalse(preview["requires_application_step"])

    def test_helper_creates_approved_preview(self):
        pending = enter_review(self._source_candidate("outcome_mismatch_candidate"))["candidate_after"]
        approved = review_candidate(pending, "approve")["candidate_after"]
        preview = build_approved_candidate_preview(
            approved,
            {
                "predicted_outcome_type": "moved",
                "predicted_primary_reason": "front_cell_empty_walkable",
            },
        )

        self.assertTrue(preview["preview_created"])
        self.assertTrue(preview["would_modify_predictor"])
        self.assertFalse(preview["predictor_modified_now"])
        self.assertFalse(preview["applied_now"])
        self.assertTrue(preview["requires_application_step"])
        self.assertEqual(preview["created_by"], "deterministic_approved_candidate_preview_v0")

    def test_summary(self):
        summary = run_approved_candidate_preview_check()["summary"]

        self.assertEqual(summary["case_count"], 5)
        self.assertEqual(summary["passed_count"], 5)
        self.assertEqual(summary["failed_count"], 0)
        self.assertEqual(summary["preview_created_count"], 3)
        self.assertEqual(summary["preview_blocked_count"], 2)
        self.assertEqual(summary["approved_preview_count"], 3)
        self.assertEqual(summary["applied_now_count"], 0)
        self.assertEqual(summary["predictor_modified_now_count"], 0)
        self.assertTrue(summary["all_approved_candidate_preview_checks_passed"])

    def test_boundary_check(self):
        boundary = run_approved_candidate_preview_check()["boundary_check"]

        self.assertTrue(boundary["approved_candidate_preview_enabled"])
        self.assertTrue(boundary["requires_approved_candidate"])
        self.assertTrue(boundary["preview_only"])
        self.assertFalse(boundary["application_step_enabled"])
        self.assertFalse(boundary["candidate_application_enabled"])
        self.assertFalse(boundary["predictor_rule_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["rule_learning_enabled"])
        self.assertFalse(boundary["rule_revision_enabled"])
        self.assertFalse(boundary["rule_application_enabled"])
        self.assertFalse(boundary["lesson_store_write"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["llm_reasoning_used"])

    def test_run_command_uses_default(self):
        result = run_command("run-approved-candidate-preview-check")

        self.assertEqual(result["command"], "run-approved-candidate-preview-check")
        self.assertTrue(result["summary"]["all_approved_candidate_preview_checks_passed"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-approved-candidate-preview-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-approved-candidate-preview-check")
        self.assertEqual(result["summary"]["case_count"], 5)
        self.assertTrue(result["summary"]["all_approved_candidate_preview_checks_passed"])

    def _preview(self, case_name):
        result = run_approved_candidate_preview_check()
        return next(item for item in result["preview_results"] if item["case_name"] == case_name)["preview"]

    def _source_candidate(self, case_name):
        result = run_rule_candidate_from_mismatch_check()
        return next(item for item in result["candidate_results"] if item["case_name"] == case_name)["candidate"]


if __name__ == "__main__":
    unittest.main()
