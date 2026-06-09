import json
import subprocess
import sys
import unittest

from ashl_core.generalized_candidate_review_preview import (
    preview_approved_generalized_candidate,
    review_generalized_candidate,
    run_generalized_candidate_review_preview_check,
)
from ashl_core.generalized_candidate_from_pattern import run_generalized_candidate_from_pattern_check
from ashl_core.teaching_cli import run_command


class GeneralizedCandidateReviewPreviewTests(unittest.TestCase):
    def test_check_runner_returns_pass_status(self):
        result = run_generalized_candidate_review_preview_check()

        self.assertEqual(result["command"], "run-generalized-candidate-review-preview-check")
        self.assertEqual(result["flow"], "generalized_candidate_review_preview_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["case_count"], 6)

    def test_approve_stable_wall_candidate_creates_preview(self):
        case = self._case("approve_stable_wall_candidate")

        self.assertTrue(case["review_allowed"])
        self.assertEqual(case["candidate_status_after_review"], "approved")
        self.assertTrue(case["preview_allowed"])
        preview = case["preview_result"]
        self.assertEqual(preview["preview_type"], "generalized_prediction_confidence_preview")
        self.assertFalse(preview["applied_now"])
        self.assertFalse(preview["would_modify_predictor"])
        self.assertFalse(preview["would_modify_action_selection"])

    def test_approve_stable_item_candidate_creates_preview(self):
        case = self._case("approve_stable_item_candidate")

        self.assertTrue(case["approved"])
        self.assertTrue(case["preview_allowed"])
        self.assertEqual(case["preview_result"]["primary_outcome"], "item_contact")
        self.assertFalse(case["applied"])

    def test_rejected_candidate_preview_is_blocked(self):
        case = self._case("reject_candidate_preview_blocked")

        self.assertTrue(case["review_allowed"])
        self.assertTrue(case["rejected"])
        self.assertFalse(case["preview_allowed"])
        self.assertIsNone(case["preview_result"])
        self.assertIn("candidate_rejected", case["block_reasons"])

    def test_deferred_candidate_preview_is_blocked(self):
        case = self._case("defer_candidate_preview_blocked")

        self.assertTrue(case["deferred"])
        self.assertFalse(case["preview_allowed"])
        self.assertIn("candidate_deferred", case["block_reasons"])

    def test_pending_candidate_preview_is_blocked(self):
        case = self._case("pending_candidate_preview_blocked")

        self.assertFalse(case["review_allowed"])
        self.assertEqual(case["candidate_status_after_review"], "pending_review")
        self.assertFalse(case["preview_allowed"])
        self.assertIn("candidate_pending_review", case["block_reasons"])

    def test_qingyin_self_approval_is_blocked(self):
        case = self._case("qingyin_self_approval_blocked")

        self.assertFalse(case["review_allowed"])
        self.assertEqual(case["candidate_status_after_review"], "pending_review")
        self.assertFalse(case["approved"])
        self.assertFalse(case["preview_allowed"])
        self.assertIn("non_human_reviewer_blocked", case["block_reasons"])

    def test_helper_review_human_decisions(self):
        candidate = self._source_candidate("front_cell_wall")

        approved = review_generalized_candidate(candidate, "approve")
        rejected = review_generalized_candidate(candidate, "reject")
        deferred = review_generalized_candidate(candidate, "defer")

        self.assertEqual(approved["candidate_after"]["candidate_status"], "approved")
        self.assertTrue(approved["candidate_after"]["approved"])
        self.assertEqual(rejected["candidate_after"]["candidate_status"], "rejected")
        self.assertEqual(deferred["candidate_after"]["candidate_status"], "deferred")
        self.assertFalse(approved["applied"])

    def test_helper_preview_requires_human_approved_candidate(self):
        candidate = self._source_candidate("front_cell_wall")
        approved = review_generalized_candidate(candidate, "approve")["candidate_after"]
        approved["reviewer_type"] = "human"
        preview = preview_approved_generalized_candidate(approved)

        self.assertEqual(preview["preview_type"], "generalized_prediction_confidence_preview")
        self.assertFalse(preview["would_modify_predictor"])
        self.assertFalse(preview["would_write_memory"])
        self.assertFalse(preview["would_create_persistent_candidate"])
        self.assertFalse(preview["applied_now"])

    def test_summary_counts_and_boundary_flags(self):
        result = run_generalized_candidate_review_preview_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["case_count"], 6)
        self.assertEqual(summary["source_candidate_count"], 2)
        self.assertEqual(summary["review_allowed_count"], 4)
        self.assertEqual(summary["review_blocked_count"], 2)
        self.assertEqual(summary["approved_count"], 2)
        self.assertEqual(summary["rejected_count"], 1)
        self.assertEqual(summary["deferred_count"], 1)
        self.assertEqual(summary["pending_review_count"], 2)
        self.assertEqual(summary["preview_created_count"], 2)
        self.assertEqual(summary["preview_blocked_count"], 4)
        self.assertEqual(summary["applied_count"], 0)
        self.assertEqual(summary["persistent_candidate_count"], 0)
        self.assertEqual(summary["persistent_rule_write_allowed_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)

        self.assertTrue(boundary["review_preview_only"])
        self.assertTrue(boundary["human_review_required"])
        self.assertFalse(boundary["qingyin_self_approval_allowed"])
        self.assertFalse(boundary["candidate_auto_approved"])
        self.assertFalse(boundary["candidate_auto_applied"])
        self.assertTrue(boundary["approved_preview_enabled"])
        self.assertFalse(boundary["preview_applied"])
        self.assertFalse(boundary["prediction_confidence_applied_to_predictor"])
        self.assertFalse(boundary["global_predictor_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["persistent_candidate_created"])
        self.assertFalse(boundary["persistent_rule_write_enabled"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["lesson_store_write"])
        self.assertFalse(boundary["memory_layer_write"])
        self.assertFalse(boundary["fuzzy_similarity_enabled"])
        self.assertFalse(boundary["llm_similarity_enabled"])

    def test_run_command_uses_default(self):
        result = run_command("run-generalized-candidate-review-preview-check")

        self.assertEqual(result["command"], "run-generalized-candidate-review-preview-check")
        self.assertEqual(result["summary"]["preview_created_count"], 2)
        self.assertEqual(result["summary"]["applied_count"], 0)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-generalized-candidate-review-preview-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-generalized-candidate-review-preview-check")
        self.assertEqual(result["summary"]["case_count"], 6)
        self.assertEqual(result["summary"]["predictor_modified_count"], 0)

    def _case(self, case_name):
        return next(
            item
            for item in run_generalized_candidate_review_preview_check()["case_results"]
            if item["case_name"] == case_name
        )

    def _source_candidate(self, primary_reason):
        result = run_generalized_candidate_from_pattern_check()
        return next(
            item["candidate"]
            for item in result["candidate_results"]
            if item["primary_reason"] == primary_reason
        )


if __name__ == "__main__":
    unittest.main()
