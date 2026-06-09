import json
import subprocess
import sys
import unittest

from ashl_core.generalized_memory_exact_key_bucket import (
    build_demo_cross_session_experience_records,
    build_exact_key_buckets,
    run_generalized_memory_exact_key_bucket_check,
    summarize_exact_key_bucket,
)
from ashl_core.teaching_cli import run_command


class GeneralizedMemoryExactKeyBucketTests(unittest.TestCase):
    def test_check_runner_returns_pass_status(self):
        result = run_generalized_memory_exact_key_bucket_check()

        self.assertEqual(result["command"], "run-generalized-memory-exact-key-bucket-check")
        self.assertEqual(result["flow"], "generalized_memory_exact_key_bucket_v0")
        self.assertEqual(result["status"], "ok")
        self.assertGreaterEqual(result["summary"]["bucket_count"], 3)

    def test_stable_wall_bucket_aggregates_multiple_sessions(self):
        stable_wall = self._bucket_by_reason("front_cell_wall")

        self.assertEqual(stable_wall["session_count"], 3)
        self.assertEqual(stable_wall["pattern_count"], 3)
        self.assertEqual(stable_wall["primary_outcome"], "blocked")
        self.assertEqual(stable_wall["dominant_outcome_ratio"], 1.0)
        self.assertEqual(stable_wall["confidence_label"], "high")
        self.assertTrue(stable_wall["eligible_for_generalized_candidate"])
        self.assertFalse(stable_wall["candidate_created"])

    def test_stable_item_bucket_has_no_candidate_creation(self):
        stable_item = self._bucket_by_reason("front_cell_item_contact")

        self.assertEqual(stable_item["primary_outcome"], "item_contact")
        self.assertIn(stable_item["confidence_label"], {"high", "medium"})
        self.assertFalse(stable_item["candidate_created"])

    def test_mixed_empty_bucket_reports_conflict_like_distribution(self):
        mixed_empty = self._bucket_by_key(
            "front_symbol=e|action=move_forward|primary_reason=front_cell_empty_walkable"
        )

        self.assertTrue(mixed_empty["conflict_like_distribution"])
        self.assertNotEqual(mixed_empty["confidence_label"], "high")
        self.assertFalse(mixed_empty["eligible_for_generalized_candidate"])
        self.assertFalse(mixed_empty["candidate_created"])

    def test_single_session_bucket_is_not_eligible(self):
        single_session = self._bucket_by_reason("front_cell_door_observed")

        self.assertEqual(single_session["session_count"], 1)
        self.assertFalse(single_session["eligible_for_generalized_candidate"])
        self.assertFalse(single_session["candidate_created"])

    def test_exact_key_rule_does_not_group_related_keys(self):
        records = [
            {
                "session_id": "session_A",
                "experience_id": "a",
                "tick": 1,
                "similar_context_key": "front_symbol=w|action=move_forward|primary_reason=front_cell_wall",
                "action": "move_forward",
                "outcome_type": "blocked",
                "reason": "front_cell_wall",
                "metadata": {},
            },
            {
                "session_id": "session_B",
                "experience_id": "b",
                "tick": 1,
                "similar_context_key": "front_symbol=w|action=turn_right|primary_reason=turn_action_orientation_change",
                "action": "turn_right",
                "outcome_type": "turned",
                "reason": "turn_action_orientation_change",
                "metadata": {},
            },
        ]
        buckets = build_exact_key_buckets(records)

        self.assertEqual(len(buckets), 2)
        self.assertIn("front_symbol=w|action=move_forward|primary_reason=front_cell_wall", buckets)
        self.assertIn("front_symbol=w|action=turn_right|primary_reason=turn_action_orientation_change", buckets)

    def test_missing_similar_context_key_is_rejected(self):
        with self.assertRaises(ValueError):
            build_exact_key_buckets([{"session_id": "session_A"}])

    def test_custom_thresholds_are_supported_without_side_effects(self):
        records = build_demo_cross_session_experience_records()
        buckets = build_exact_key_buckets(records)
        stable_wall = buckets["front_symbol=w|action=move_forward|primary_reason=front_cell_wall"]
        summary = summarize_exact_key_bucket(
            stable_wall,
            thresholds={"candidate_min_pattern_count": 4},
        )

        self.assertEqual(summary["confidence_label"], "high")
        self.assertFalse(summary["eligible_for_generalized_candidate"])
        self.assertFalse(summary["candidate_created"])

    def test_summary_counts_and_boundary_flags(self):
        result = run_generalized_memory_exact_key_bucket_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["record_count"], 10)
        self.assertEqual(summary["bucket_count"], 4)
        self.assertEqual(summary["cross_session_bucket_count"], 3)
        self.assertEqual(summary["stable_bucket_count"], 3)
        self.assertEqual(summary["mixed_bucket_count"], 1)
        self.assertEqual(summary["single_session_bucket_count"], 1)
        self.assertEqual(summary["eligible_for_generalized_candidate_count"], 2)
        self.assertEqual(summary["candidate_created_count"], 0)
        self.assertEqual(summary["high_confidence_bucket_count"], 2)
        self.assertEqual(summary["medium_confidence_bucket_count"], 2)
        self.assertEqual(summary["low_confidence_bucket_count"], 0)

        self.assertTrue(boundary["generalized_memory_exact_key_bucket_enabled"])
        self.assertTrue(boundary["exact_key_bucket_only"])
        self.assertTrue(boundary["exact_similar_context_key_only"])
        self.assertFalse(boundary["fuzzy_similarity_enabled"])
        self.assertFalse(boundary["semantic_similarity_enabled"])
        self.assertFalse(boundary["llm_similarity_enabled"])
        self.assertFalse(boundary["visual_similarity_enabled"])
        self.assertTrue(boundary["prediction_confidence_calculated"])
        self.assertFalse(boundary["prediction_confidence_applied_to_predictor"])
        self.assertFalse(boundary["global_predictor_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["lesson_store_write"])
        self.assertFalse(boundary["memory_layer_write"])

    def test_run_command_uses_default(self):
        result = run_command("run-generalized-memory-exact-key-bucket-check")

        self.assertEqual(result["command"], "run-generalized-memory-exact-key-bucket-check")
        self.assertEqual(result["summary"]["candidate_created_count"], 0)
        self.assertFalse(result["boundary_check"]["prediction_confidence_applied_to_predictor"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-generalized-memory-exact-key-bucket-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-generalized-memory-exact-key-bucket-check")
        self.assertEqual(result["summary"]["bucket_count"], 4)
        self.assertEqual(result["summary"]["candidate_created_count"], 0)

    def _bucket_by_reason(self, reason):
        return next(
            item
            for item in run_generalized_memory_exact_key_bucket_check()["bucket_summaries"]
            if item["primary_reason"] == reason
        )

    def _bucket_by_key(self, key):
        return next(
            item
            for item in run_generalized_memory_exact_key_bucket_check()["bucket_summaries"]
            if item["similar_context_key"] == key
        )


if __name__ == "__main__":
    unittest.main()
