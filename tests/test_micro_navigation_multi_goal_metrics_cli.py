import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_navigation_multi_goal_metrics_cli


class MicroNavigationMultiGoalMetricsCliTests(unittest.TestCase):
    def test_multi_goal_metrics_cli_returns_ok_metrics(self):
        result = run_navigation_multi_goal_metrics_cli(runs=4, trial_count=5, max_steps=20)

        self.assertEqual(result["command"], "run-navigation-multi-goal-metrics")
        self.assertEqual(result["flow"], "navigation_multi_goal_metrics_cli_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["runs"], 4)
        self.assertEqual(result["trial_count_per_run"], 5)
        self.assertEqual(result["total_trials"], 20)
        self.assertEqual(result["total_completed"], 20)
        self.assertEqual(result["overall_success_rate"], 1.0)
        self.assertIn("overall_average_step_count", result)
        self.assertIn("max_steps_reached_count", result)
        self.assertIn("human_summary", result)
        self.assertEqual(len(result["run_summaries"]), 4)

    def test_run_summaries_have_required_shape(self):
        result = run_navigation_multi_goal_metrics_cli(runs=2, trial_count=3, max_steps=20)

        for index, summary in enumerate(result["run_summaries"]):
            self.assertEqual(summary["run_index"], index)
            self.assertEqual(summary["completed_count"], 3)
            self.assertEqual(summary["trial_count"], 3)
            self.assertEqual(summary["success_rate"], 1.0)
            self.assertEqual(summary["step_counts"], [10, 10, 10])
            self.assertEqual(summary["average_step_count"], 10)
            self.assertEqual(summary["min_step_count"], 10)
            self.assertEqual(summary["max_step_count"], 10)
            self.assertEqual(summary["max_steps_reached_count"], 0)

    def test_trial_summaries_use_multi_goal_semantics(self):
        result = run_navigation_multi_goal_metrics_cli(runs=1, trial_count=2, max_steps=20)
        trial_summaries = result["run_summaries"][0]["trial_summaries"]

        self.assertEqual(len(trial_summaries), 2)
        for trial in trial_summaries:
            self.assertTrue(trial["completed_all_goals"])
            self.assertEqual(trial["goals_reached"], 2)
            self.assertEqual(trial["goal_count"], 2)
            self.assertEqual(trial["step_count"], 10)
            self.assertEqual(
                trial["selected_actions"],
                [
                    "move_down",
                    "move_down",
                    "move_right",
                    "move_right",
                    "move_right",
                    "move_right",
                    "move_left",
                    "move_left",
                    "move_left",
                    "move_left",
                ],
            )

    def test_total_trials_equals_runs_times_trial_count(self):
        result = run_navigation_multi_goal_metrics_cli(runs=4, trial_count=5, max_steps=20)

        self.assertEqual(result["total_trials"], result["runs"] * result["trial_count_per_run"])
        self.assertEqual(
            result["total_completed"],
            sum(summary["completed_count"] for summary in result["run_summaries"]),
        )

    def test_max_steps_reached_count_when_trials_cannot_finish(self):
        result = run_navigation_multi_goal_metrics_cli(runs=2, trial_count=3, max_steps=1)

        self.assertEqual(result["total_trials"], 6)
        self.assertEqual(result["total_completed"], 0)
        self.assertEqual(result["overall_success_rate"], 0)
        self.assertEqual(result["max_steps_reached_count"], 6)

    def test_boundary_flags_are_false(self):
        result = run_navigation_multi_goal_metrics_cli(runs=1, trial_count=1, max_steps=20)
        boundary = result["boundary"]

        self.assertIs(boundary["llm_used"], False)
        self.assertIs(boundary["creates_lesson_candidate"], False)
        self.assertIs(boundary["writes_lesson_store"], False)
        self.assertIs(boundary["writes_memory_layer"], False)
        self.assertIs(boundary["awakening_claim"], False)
        self.assertIs(boundary["changes_navigation_behavior"], False)

    def test_cli_does_not_return_learning_outputs(self):
        result = run_navigation_multi_goal_metrics_cli(runs=1, trial_count=1, max_steps=20)
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
            for trial in summary["trial_summaries"]:
                self.assertTrue(forbidden_keys.isdisjoint(trial))

    def test_module_cli_multi_goal_metrics_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-navigation-multi-goal-metrics",
                "--runs",
                "4",
                "--trial-count",
                "5",
                "--max-steps",
                "20",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "navigation_multi_goal_metrics_cli_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["total_trials"], 20)
        self.assertEqual(result["total_completed"], 20)
        self.assertEqual(len(result["run_summaries"]), 4)
        self.assertIn("human_summary", result)


if __name__ == "__main__":
    unittest.main()
