import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_trial_metrics_baseline_compare_cli


class TrialMetricsBaselineComparisonTests(unittest.TestCase):
    def test_baseline_comparison_returns_required_fields(self):
        result = run_trial_metrics_baseline_compare_cli()

        self.assertEqual(result["command"], "run-trial-metrics-baseline-compare")
        self.assertEqual(result["flow"], "trial_metrics_baseline_comparison_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["baseline_id"], "trial_metrics_baseline_v0")
        self.assertIn("baseline_commit", result)
        self.assertIn("run-trial-metrics-comparison", result["baseline_source_command"])
        self.assertTrue(result["same_config_used"])
        self.assertTrue(result["comparison_only"])
        self.assertFalse(result["proof_of_learning"])

    def test_baseline_current_and_delta_metrics_are_reported(self):
        result = run_trial_metrics_baseline_compare_cli()

        self.assertEqual(result["baseline_total_trials"], 20)
        self.assertEqual(result["current_total_trials"], 20)
        self.assertEqual(result["baseline_total_completed"], 13)
        self.assertEqual(result["current_total_completed"], 13)
        self.assertEqual(result["total_completed_delta"], 0)
        self.assertEqual(result["baseline_overall_success_rate"], 0.65)
        self.assertEqual(result["current_overall_success_rate"], 0.65)
        self.assertEqual(result["success_rate_delta"], 0)
        self.assertEqual(result["baseline_overall_average_step_count"], 6.6)
        self.assertEqual(result["current_overall_average_step_count"], 6.6)
        self.assertEqual(result["average_step_count_delta"], 0)
        self.assertEqual(result["baseline_max_steps_reached_count"], 7)
        self.assertEqual(result["current_max_steps_reached_count"], 7)
        self.assertEqual(result["max_steps_reached_delta"], 0)

    def test_baseline_config_is_reused(self):
        parameters = run_trial_metrics_baseline_compare_cli()["parameters"]

        self.assertEqual(parameters["runs"], 4)
        self.assertEqual(parameters["trial_count"], 5)
        self.assertEqual(parameters["max_steps"], 10)
        self.assertEqual(parameters["random_seed"], 17)

    def test_baseline_comparison_boundaries_are_false(self):
        boundary = run_trial_metrics_baseline_compare_cli()["boundary"]

        self.assertIs(boundary["changes_trial_runner_behavior"], False)
        self.assertIs(boundary["changes_action_selection"], False)
        self.assertIs(boundary["changes_goal_bias"], False)
        self.assertIs(boundary["changes_state_action_memory"], False)
        self.assertIs(boundary["changes_penalty_or_stuck_detection"], False)
        self.assertIs(boundary["creates_learning_rule"], False)
        self.assertIs(boundary["creates_lesson_candidate"], False)
        self.assertIs(boundary["writes_lesson_store"], False)
        self.assertIs(boundary["writes_memory_layer"], False)
        self.assertIs(boundary["llm_used"], False)

    def test_baseline_comparison_does_not_return_learning_outputs(self):
        result = run_trial_metrics_baseline_compare_cli()
        forbidden_keys = {
            "lesson_candidate",
            "lesson_store_write",
            "memory_layer_write",
            "learning_rule",
            "proof_of_learning_claim",
            "llm_prompt",
        }

        self.assertTrue(forbidden_keys.isdisjoint(result))

    def test_module_cli_baseline_compare_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "compare-trial-metrics-baseline",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "trial_metrics_baseline_comparison_v0")
        self.assertTrue(result["same_config_used"])
        self.assertTrue(result["comparison_only"])
        self.assertFalse(result["proof_of_learning"])
        self.assertEqual(result["total_completed_delta"], 0)


if __name__ == "__main__":
    unittest.main()
