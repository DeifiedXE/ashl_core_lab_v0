import json
import unittest
from pathlib import Path


BASELINE_PATH = Path("data/baselines/trial_metrics_baseline_v0.json")


class TrialMetricsBaselineSnapshotTests(unittest.TestCase):
    def test_baseline_json_exists_and_is_valid(self):
        self.assertTrue(BASELINE_PATH.exists())
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

        self.assertEqual(baseline["baseline_id"], "trial_metrics_baseline_v0")
        self.assertEqual(baseline["created_for"], "push_box_need_state_trial_metrics")
        self.assertIn("run-trial-metrics-comparison", baseline["source_command"])
        self.assertIn("--random-seed 17", baseline["source_command"])
        self.assertIn("commit", baseline)
        self.assertEqual(baseline["boundary_index_version"], "Boundary Index Version: 2026-06-06-b30")

    def test_baseline_parameters_are_recorded(self):
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        parameters = baseline["parameters"]

        self.assertEqual(parameters["runs"], 4)
        self.assertEqual(parameters["trial_count"], 5)
        self.assertEqual(parameters["max_steps"], 10)
        self.assertEqual(parameters["random_seed"], 17)

    def test_baseline_metrics_are_recorded(self):
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        metrics = baseline["metrics"]

        self.assertEqual(metrics["total_trials"], 20)
        self.assertEqual(metrics["total_completed"], 13)
        self.assertEqual(metrics["overall_success_rate"], 0.65)
        self.assertEqual(metrics["overall_average_step_count"], 6.6)
        self.assertEqual(metrics["max_steps_reached_count"], 7)
        self.assertEqual(len(metrics["run_summaries"]), 4)
        self.assertIn("20 trials, 13 completed", metrics["human_summary"])

    def test_baseline_notes_keep_snapshot_non_behavioral(self):
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        notes_text = " ".join(baseline["notes"])

        self.assertIn("comparison only", notes_text)
        self.assertIn("does not modify behavior", notes_text)
        self.assertIn("not proof of learning", notes_text)

    def test_baseline_does_not_contain_learning_outputs(self):
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        forbidden_keys = {
            "lesson_candidate",
            "lesson_store_write",
            "memory_layer_write",
            "solver",
            "pathfinding",
            "llm_prompt",
            "behavior_change",
        }

        self.assertTrue(forbidden_keys.isdisjoint(baseline))
        self.assertTrue(forbidden_keys.isdisjoint(baseline["metrics"]))


if __name__ == "__main__":
    unittest.main()
