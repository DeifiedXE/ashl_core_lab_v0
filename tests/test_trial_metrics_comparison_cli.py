import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_trial_metrics_comparison_cli


class TrialMetricsComparisonCliTests(unittest.TestCase):
    def test_trial_metrics_comparison_cli_returns_ok_metrics(self):
        result = run_trial_metrics_comparison_cli(runs=4, trial_count=5, max_steps=10, random_seed=0)

        self.assertEqual(result["command"], "run-trial-metrics-comparison")
        self.assertEqual(result["flow"], "trial_metrics_comparison_cli_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["runs"], 4)
        self.assertEqual(result["trial_count_per_run"], 5)
        self.assertEqual(result["total_trials"], 20)
        self.assertIn("overall_success_rate", result)
        self.assertIn("overall_average_step_count", result)
        self.assertIn("max_steps_reached_count", result)
        self.assertIn("human_summary", result)
        self.assertEqual(len(result["run_summaries"]), 4)

    def test_run_summaries_have_required_shape(self):
        result = run_trial_metrics_comparison_cli(runs=2, trial_count=3, max_steps=10, random_seed=0)

        for index, summary in enumerate(result["run_summaries"]):
            self.assertEqual(summary["run_index"], index)
            self.assertIn("completed_count", summary)
            self.assertEqual(summary["trial_count"], 3)
            self.assertIn("success_rate", summary)
            self.assertEqual(len(summary["step_counts"]), 3)
            self.assertIn("average_step_count", summary)
            self.assertIn("min_step_count", summary)
            self.assertIn("max_step_count", summary)
            self.assertIn("max_steps_reached_count", summary)

    def test_total_trials_equals_runs_times_trial_count(self):
        result = run_trial_metrics_comparison_cli(runs=4, trial_count=5, max_steps=10, random_seed=0)

        self.assertEqual(result["total_trials"], result["runs"] * result["trial_count_per_run"])
        self.assertEqual(
            result["total_completed"],
            sum(summary["completed_count"] for summary in result["run_summaries"]),
        )

    def test_random_seed_makes_output_reproducible(self):
        first = run_trial_metrics_comparison_cli(runs=4, trial_count=5, max_steps=10, random_seed=17)
        second = run_trial_metrics_comparison_cli(runs=4, trial_count=5, max_steps=10, random_seed=17)

        self.assertEqual(first, second)

    def test_boundary_flags_are_false(self):
        result = run_trial_metrics_comparison_cli(runs=1, trial_count=1, max_steps=1, random_seed=0)
        boundary = result["boundary"]

        self.assertIs(boundary["llm_used"], False)
        self.assertIs(boundary["creates_lesson_candidate"], False)
        self.assertIs(boundary["writes_lesson_store"], False)
        self.assertIs(boundary["writes_memory_layer"], False)
        self.assertIs(boundary["awakening_claim"], False)
        self.assertIs(boundary["changes_trial_runner_behavior"], False)

    def test_comparison_cli_does_not_return_learning_outputs(self):
        result = run_trial_metrics_comparison_cli(runs=1, trial_count=1, max_steps=1, random_seed=0)
        forbidden_keys = {
            "lesson_store_write",
            "memory_layer_write",
            "memory_write",
            "lesson_candidate",
            "solver",
            "pathfinding",
            "llm_prompt",
        }

        self.assertTrue(forbidden_keys.isdisjoint(result))
        for summary in result["run_summaries"]:
            self.assertTrue(forbidden_keys.isdisjoint(summary))

    def test_module_cli_trial_metrics_comparison_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-trial-metrics-comparison",
                "--runs",
                "4",
                "--trial-count",
                "5",
                "--max-steps",
                "10",
                "--random-seed",
                "0",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "trial_metrics_comparison_cli_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["total_trials"], 20)
        self.assertEqual(len(result["run_summaries"]), 4)
        self.assertIn("human_summary", result)


if __name__ == "__main__":
    unittest.main()
