import json
import subprocess
import sys
import unittest

from ashl_core.generalized_prediction_confidence_check import (
    build_prediction_confidence_suggestions,
    evaluate_prediction_confidence_for_bucket,
    run_generalized_prediction_confidence_check,
)
from ashl_core.teaching_cli import run_command


class GeneralizedPredictionConfidenceCheckTests(unittest.TestCase):
    def test_check_runner_returns_pass_status(self):
        result = run_generalized_prediction_confidence_check()

        self.assertEqual(result["command"], "run-generalized-prediction-confidence-check")
        self.assertEqual(result["flow"], "generalized_prediction_confidence_check_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["suggestion_count"], result["summary"]["bucket_count"])

    def test_stable_wall_bucket_suggests_increase(self):
        stable_wall = self._suggestion_by_reason("front_cell_wall")

        self.assertEqual(stable_wall["prediction_confidence_suggestion"], "increase_confidence")
        self.assertEqual(stable_wall["suggested_confidence_label"], "high")
        self.assertFalse(stable_wall["applied_to_predictor"])
        self.assertFalse(stable_wall["action_selection_influence"])
        self.assertFalse(stable_wall["candidate_created"])
        self.assertEqual(stable_wall["block_reasons"], [])

    def test_stable_item_bucket_suggests_increase(self):
        stable_item = self._suggestion_by_reason("front_cell_item_contact")

        self.assertEqual(stable_item["prediction_confidence_suggestion"], "increase_confidence")
        self.assertEqual(stable_item["suggested_confidence_label"], "high")
        self.assertFalse(stable_item["applied_to_predictor"])
        self.assertFalse(stable_item["candidate_created"])

    def test_mixed_empty_bucket_blocks_increase(self):
        mixed_empty = self._suggestion_by_key(
            "front_symbol=e|action=move_forward|primary_reason=front_cell_empty_walkable"
        )

        self.assertNotEqual(mixed_empty["prediction_confidence_suggestion"], "increase_confidence")
        self.assertEqual(
            mixed_empty["prediction_confidence_suggestion"],
            "blocked_conflict_like_distribution",
        )
        self.assertTrue(mixed_empty["conflict_like_distribution"])
        self.assertIn("conflict_like_distribution", mixed_empty["block_reasons"])
        self.assertFalse(mixed_empty["applied_to_predictor"])

    def test_single_session_bucket_is_blocked(self):
        single_session = self._suggestion_by_reason("front_cell_door_observed")

        self.assertEqual(
            single_session["prediction_confidence_suggestion"],
            "blocked_single_session_evidence",
        )
        self.assertEqual(single_session["session_count"], 1)
        self.assertIn("single_session_evidence", single_session["block_reasons"])

    def test_missing_required_fields_are_blocked_safely(self):
        suggestion = evaluate_prediction_confidence_for_bucket(
            {
                "similar_context_key": "front_symbol=x|action=look",
                "session_count": 2,
            }
        )

        self.assertEqual(
            suggestion["prediction_confidence_suggestion"],
            "blocked_missing_required_fields",
        )
        self.assertFalse(suggestion["applied_to_predictor"])
        self.assertFalse(suggestion["action_selection_influence"])
        self.assertFalse(suggestion["candidate_created"])
        self.assertTrue(suggestion["block_reasons"])

    def test_hold_confidence_when_data_is_not_stable_enough(self):
        suggestion = evaluate_prediction_confidence_for_bucket(
            {
                "similar_context_key": "front_symbol=p|action=move_forward|primary_reason=partial",
                "session_count": 3,
                "pattern_count": 5,
                "outcome_distribution": {"moved": 3, "observed": 2},
                "primary_outcome": "moved",
                "primary_reason": "partial",
                "dominant_outcome_ratio": 0.6,
                "confidence_label": "medium",
                "conflict_like_distribution": False,
                "candidate_created": False,
            }
        )

        self.assertEqual(suggestion["prediction_confidence_suggestion"], "hold_confidence")
        self.assertEqual(suggestion["suggested_confidence_label"], "medium")
        self.assertFalse(suggestion["applied_to_predictor"])

    def test_insufficient_pattern_count_blocks(self):
        suggestion = evaluate_prediction_confidence_for_bucket(
            {
                "similar_context_key": "front_symbol=w|action=move_forward|primary_reason=front_cell_wall",
                "session_count": 2,
                "pattern_count": 2,
                "outcome_distribution": {"blocked": 2},
                "primary_outcome": "blocked",
                "primary_reason": "front_cell_wall",
                "dominant_outcome_ratio": 1.0,
                "confidence_label": "medium",
                "conflict_like_distribution": False,
                "candidate_created": False,
            }
        )

        self.assertEqual(
            suggestion["prediction_confidence_suggestion"],
            "blocked_insufficient_pattern_count",
        )
        self.assertIn("insufficient_pattern_count", suggestion["block_reasons"])

    def test_summary_counts_and_boundary_flags(self):
        result = run_generalized_prediction_confidence_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["bucket_count"], 4)
        self.assertEqual(summary["suggestion_count"], 4)
        self.assertEqual(summary["increase_confidence_count"], 2)
        self.assertEqual(summary["hold_confidence_count"], 0)
        self.assertEqual(summary["decrease_confidence_count"], 0)
        self.assertEqual(summary["blocked_conflict_like_count"], 1)
        self.assertEqual(summary["blocked_single_session_count"], 1)
        self.assertEqual(summary["blocked_insufficient_pattern_count"], 0)
        self.assertEqual(summary["applied_to_predictor_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["candidate_created_count"], 0)

        self.assertTrue(boundary["confidence_check_only"])
        self.assertTrue(boundary["uses_exact_key_buckets"])
        self.assertFalse(boundary["fuzzy_similarity_enabled"])
        self.assertFalse(boundary["semantic_similarity_enabled"])
        self.assertFalse(boundary["llm_similarity_enabled"])
        self.assertFalse(boundary["visual_similarity_enabled"])
        self.assertTrue(boundary["prediction_confidence_suggestions_generated"])
        self.assertFalse(boundary["prediction_confidence_applied_to_predictor"])
        self.assertFalse(boundary["prediction_rule_modified"])
        self.assertFalse(boundary["global_predictor_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["lesson_store_write"])
        self.assertFalse(boundary["memory_layer_write"])

    def test_build_prediction_confidence_suggestions_preserves_count(self):
        buckets = [
            {
                "similar_context_key": "a",
                "session_count": 2,
                "pattern_count": 3,
                "outcome_distribution": {"blocked": 3},
                "primary_outcome": "blocked",
                "primary_reason": "wall",
                "dominant_outcome_ratio": 1.0,
                "confidence_label": "high",
                "conflict_like_distribution": False,
                "candidate_created": False,
            },
            {
                "similar_context_key": "b",
                "session_count": 1,
                "pattern_count": 1,
                "outcome_distribution": {"observed": 1},
                "primary_outcome": "observed",
                "primary_reason": "door",
                "dominant_outcome_ratio": 1.0,
                "confidence_label": "medium",
                "conflict_like_distribution": False,
                "candidate_created": False,
            },
        ]
        suggestions = build_prediction_confidence_suggestions(buckets)

        self.assertEqual(len(suggestions), 2)
        self.assertEqual(suggestions[0]["prediction_confidence_suggestion"], "increase_confidence")
        self.assertEqual(
            suggestions[1]["prediction_confidence_suggestion"],
            "blocked_single_session_evidence",
        )

    def test_run_command_uses_default(self):
        result = run_command("run-generalized-prediction-confidence-check")

        self.assertEqual(result["command"], "run-generalized-prediction-confidence-check")
        self.assertEqual(result["summary"]["applied_to_predictor_count"], 0)
        self.assertFalse(result["boundary_check"]["global_predictor_modified"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-generalized-prediction-confidence-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-generalized-prediction-confidence-check")
        self.assertEqual(result["summary"]["bucket_count"], 4)
        self.assertEqual(result["summary"]["candidate_created_count"], 0)

    def _suggestion_by_reason(self, reason):
        return next(
            item
            for item in run_generalized_prediction_confidence_check()["confidence_suggestions"]
            if item["primary_reason"] == reason
        )

    def _suggestion_by_key(self, key):
        return next(
            item
            for item in run_generalized_prediction_confidence_check()["confidence_suggestions"]
            if item["similar_context_key"] == key
        )


if __name__ == "__main__":
    unittest.main()
