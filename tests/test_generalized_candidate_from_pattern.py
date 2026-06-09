import json
import subprocess
import sys
import unittest

from ashl_core.generalized_candidate_from_pattern import (
    build_generalized_candidates_from_confidence_suggestions,
    evaluate_generalized_candidate_eligibility,
    run_generalized_candidate_from_pattern_check,
)
from ashl_core.teaching_cli import run_command


class GeneralizedCandidateFromPatternTests(unittest.TestCase):
    def test_check_runner_returns_pass_status(self):
        result = run_generalized_candidate_from_pattern_check()

        self.assertEqual(result["command"], "run-generalized-candidate-from-pattern-check")
        self.assertEqual(result["flow"], "generalized_candidate_from_pattern_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["candidate_created_count"], 2)

    def test_stable_wall_bucket_creates_pending_review_candidate(self):
        result = self._result_by_reason("front_cell_wall")
        candidate = result["candidate"]

        self.assertTrue(result["candidate_created"])
        self.assertEqual(candidate["candidate_status"], "pending_review")
        self.assertEqual(candidate["review_status"], "pending_review")
        self.assertTrue(candidate["review_required"])
        self.assertFalse(candidate["approved"])
        self.assertFalse(candidate["applied"])
        self.assertFalse(candidate["persistent_candidate"])
        self.assertFalse(candidate["persistent_rule_write_allowed"])
        self.assertFalse(candidate["action_selection_influence"])

    def test_stable_item_bucket_creates_pending_review_candidate(self):
        result = self._result_by_reason("front_cell_item_contact")
        candidate = result["candidate"]

        self.assertTrue(result["candidate_created"])
        self.assertEqual(candidate["candidate_status"], "pending_review")
        self.assertEqual(candidate["proposed_prediction_outcome"], "item_contact")
        self.assertEqual(candidate["proposed_prediction_reason"], "front_cell_item_contact")
        self.assertEqual(candidate["evidence"]["confidence_label"], "high")
        self.assertFalse(candidate["approved"])
        self.assertFalse(candidate["applied"])

    def test_mixed_empty_bucket_does_not_create_candidate(self):
        result = self._result_by_key(
            "front_symbol=e|action=move_forward|primary_reason=front_cell_empty_walkable"
        )
        candidate = result["candidate"]

        self.assertFalse(result["candidate_created"])
        self.assertEqual(candidate["candidate_status"], "blocked")
        self.assertIn("conflict_like_distribution", result["block_reasons"])
        self.assertFalse(candidate["approved"])
        self.assertFalse(candidate["applied"])

    def test_single_session_bucket_does_not_create_candidate(self):
        result = self._result_by_reason("front_cell_door_observed")

        self.assertFalse(result["candidate_created"])
        self.assertIn("single_session_evidence", result["block_reasons"])
        self.assertEqual(result["candidate"]["review_status"], "not_created")

    def test_missing_required_fields_are_blocked(self):
        result = evaluate_generalized_candidate_eligibility(
            {
                "similar_context_key": "front_symbol=x|action=look",
                "prediction_confidence_suggestion": "increase_confidence",
            }
        )

        self.assertFalse(result["candidate_created"])
        self.assertTrue(result["block_reasons"])
        self.assertTrue(
            any(reason.startswith("missing_required_field:") for reason in result["block_reasons"])
        )
        self.assertFalse(result["candidate"]["approved"])
        self.assertFalse(result["candidate"]["applied"])

    def test_non_high_confidence_is_blocked(self):
        suggestion = self._base_suggestion()
        suggestion["suggested_confidence_label"] = "medium"
        result = evaluate_generalized_candidate_eligibility(suggestion)

        self.assertFalse(result["candidate_created"])
        self.assertIn("confidence_not_high", result["block_reasons"])

    def test_suggestion_not_increase_is_blocked(self):
        suggestion = self._base_suggestion()
        suggestion["prediction_confidence_suggestion"] = "hold_confidence"
        result = evaluate_generalized_candidate_eligibility(suggestion)

        self.assertFalse(result["candidate_created"])
        self.assertIn("suggestion_not_increase_confidence", result["block_reasons"])

    def test_build_candidates_preserves_count(self):
        suggestions = [self._base_suggestion(), {**self._base_suggestion(), "session_count": 1}]
        results = build_generalized_candidates_from_confidence_suggestions(suggestions)

        self.assertEqual(len(results), 2)
        self.assertTrue(results[0]["candidate_created"])
        self.assertFalse(results[1]["candidate_created"])

    def test_summary_counts_and_boundary_flags(self):
        result = run_generalized_candidate_from_pattern_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["suggestion_count"], 4)
        self.assertEqual(summary["candidate_created_count"], 2)
        self.assertEqual(summary["pending_review_count"], 2)
        self.assertEqual(summary["blocked_count"], 2)
        self.assertEqual(summary["approved_count"], 0)
        self.assertEqual(summary["applied_count"], 0)
        self.assertEqual(summary["persistent_candidate_count"], 0)
        self.assertEqual(summary["persistent_rule_write_allowed_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["blocked_conflict_like_count"], 1)
        self.assertEqual(summary["blocked_single_session_count"], 1)

        self.assertTrue(boundary["candidate_generation_check_only"])
        self.assertTrue(boundary["exact_similar_context_key_only"])
        self.assertFalse(boundary["fuzzy_similarity_enabled"])
        self.assertFalse(boundary["semantic_similarity_enabled"])
        self.assertFalse(boundary["llm_similarity_enabled"])
        self.assertFalse(boundary["visual_similarity_enabled"])
        self.assertTrue(boundary["generalized_candidate_created_in_output"])
        self.assertFalse(boundary["generalized_candidate_persisted"])
        self.assertFalse(boundary["candidate_auto_approved"])
        self.assertFalse(boundary["candidate_auto_applied"])
        self.assertTrue(boundary["review_required"])
        self.assertTrue(boundary["review_status_pending_only"])
        self.assertFalse(boundary["prediction_confidence_applied_to_predictor"])
        self.assertFalse(boundary["global_predictor_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["persistent_candidate_created"])
        self.assertFalse(boundary["persistent_rule_write_enabled"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["lesson_store_write"])
        self.assertFalse(boundary["memory_layer_write"])

    def test_run_command_uses_default(self):
        result = run_command("run-generalized-candidate-from-pattern-check")

        self.assertEqual(result["command"], "run-generalized-candidate-from-pattern-check")
        self.assertEqual(result["summary"]["candidate_created_count"], 2)
        self.assertEqual(result["summary"]["approved_count"], 0)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-generalized-candidate-from-pattern-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-generalized-candidate-from-pattern-check")
        self.assertEqual(result["summary"]["candidate_created_count"], 2)
        self.assertEqual(result["summary"]["applied_count"], 0)

    def _result_by_reason(self, reason):
        return next(
            item
            for item in run_generalized_candidate_from_pattern_check()["candidate_results"]
            if item["primary_reason"] == reason
        )

    def _result_by_key(self, key):
        return next(
            item
            for item in run_generalized_candidate_from_pattern_check()["candidate_results"]
            if item["similar_context_key"] == key
        )

    def _base_suggestion(self):
        return {
            "similar_context_key": "front_symbol=w|action=move_forward|primary_reason=front_cell_wall",
            "session_count": 3,
            "pattern_count": 3,
            "primary_outcome": "blocked",
            "primary_reason": "front_cell_wall",
            "outcome_distribution": {"blocked": 3},
            "dominant_outcome_ratio": 1.0,
            "bucket_confidence_label": "high",
            "conflict_like_distribution": False,
            "prediction_confidence_suggestion": "increase_confidence",
            "suggested_confidence_label": "high",
            "applied_to_predictor": False,
            "action_selection_influence": False,
            "candidate_created": False,
            "block_reasons": [],
        }


if __name__ == "__main__":
    unittest.main()
