import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_approach_box_two_trial_check_cli


class ApproachBoxTwoTrialLearningCheckTests(unittest.TestCase):
    def test_two_trial_check_returns_required_sections(self):
        result = run_approach_box_two_trial_check_cli(max_steps=10)

        self.assertEqual(result["command"], "run-approach-box-two-trial-check")
        self.assertEqual(result["flow"], "approach_box_two_trial_learning_check_v0")
        self.assertEqual(result["status"], "ok")
        self.assertIn("trial_1", result)
        self.assertIn("trial_2", result)
        self.assertIn("comparison", result)
        self.assertIn("boundary_check", result)

    def test_trial_summaries_have_expected_shape(self):
        result = run_approach_box_two_trial_check_cli(max_steps=10)
        trial_1 = result["trial_1"]
        trial_2 = result["trial_2"]

        self.assertTrue(trial_1["completed_approach"])
        self.assertTrue(trial_2["completed_approach"])
        self.assertEqual(trial_1["initial_agent_pos"], [1, 1])
        self.assertEqual(trial_2["initial_agent_pos"], [1, 1])
        self.assertEqual(trial_1["box_pos"], [3, 4])
        self.assertEqual(trial_2["box_pos"], [3, 4])
        self.assertEqual(trial_1["final_agent_pos"], [3, 3])
        self.assertEqual(trial_2["final_agent_pos"], [3, 3])
        self.assertEqual(trial_1["final_distance_to_box"], 1)
        self.assertEqual(trial_2["final_distance_to_box"], 1)
        self.assertEqual(trial_1["step_count"], 4)
        self.assertEqual(trial_2["step_count"], 4)
        self.assertEqual(trial_1["selected_actions"], ["move_down", "move_down", "move_right", "move_right"])
        self.assertEqual(trial_2["selected_actions"], ["move_down", "move_down", "move_right", "move_right"])
        self.assertTrue(trial_1["local_outcome_memory_written"])
        self.assertTrue(trial_2["local_outcome_memory_read"])
        self.assertTrue(trial_2["used_trial1_local_memory"])
        self.assertIs(trial_1["llm_used"], False)
        self.assertIs(trial_2["llm_used"], False)

    def test_comparison_reports_trial_deltas(self):
        comparison = run_approach_box_two_trial_check_cli(max_steps=10)["comparison"]

        self.assertEqual(comparison["trial1_step_count"], 4)
        self.assertEqual(comparison["trial2_step_count"], 4)
        self.assertEqual(comparison["step_count_delta"], 0)
        self.assertEqual(comparison["trial1_failed_or_blocked_actions"], 0)
        self.assertEqual(comparison["trial2_failed_or_blocked_actions"], 0)
        self.assertEqual(comparison["failed_or_blocked_delta"], 0)
        self.assertEqual(comparison["trial1_selected_actions"], ["move_down", "move_down", "move_right", "move_right"])
        self.assertEqual(comparison["trial2_selected_actions"], ["move_down", "move_down", "move_right", "move_right"])

    def test_boundary_check_rejects_forbidden_sources(self):
        boundary = run_approach_box_two_trial_check_cli(max_steps=10)["boundary_check"]

        self.assertTrue(boundary["trial2_read_local_outcome_memory_only"])
        self.assertFalse(boundary["trial2_replayed_full_route"])
        self.assertFalse(boundary["trial2_used_llm"])
        self.assertFalse(boundary["trial2_used_lesson_store"])
        self.assertFalse(boundary["trial2_used_memory_layer"])
        self.assertFalse(boundary["trial2_used_long_term_memory"])
        self.assertFalse(boundary["trial2_used_lesson_candidate"])
        self.assertFalse(boundary["trial2_used_pathfinding"])
        self.assertFalse(boundary["trial2_used_human_hint"])

    def test_two_trial_check_does_not_return_full_traces_or_learning_outputs(self):
        result = run_approach_box_two_trial_check_cli(max_steps=10)
        forbidden_keys = {
            "steps",
            "trace",
            "route",
            "solution",
            "preloaded_actions",
            "lesson_candidate",
            "lesson_store_write",
            "memory_layer_write",
            "long_term_memory_write",
            "llm_prompt",
            "pathfinding",
        }

        self.assertTrue(forbidden_keys.isdisjoint(result))
        self.assertTrue(forbidden_keys.isdisjoint(result["trial_1"]))
        self.assertTrue(forbidden_keys.isdisjoint(result["trial_2"]))

    def test_module_cli_two_trial_check_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-approach-box-two-trial-check",
                "--max-steps",
                "10",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "approach_box_two_trial_learning_check_v0")
        self.assertTrue(result["trial_1"]["completed_approach"])
        self.assertTrue(result["trial_2"]["completed_approach"])
        self.assertEqual(result["comparison"]["step_count_delta"], 0)
        self.assertFalse(result["boundary_check"]["trial2_replayed_full_route"])
        self.assertFalse(result["boundary_check"]["trial2_used_llm"])


if __name__ == "__main__":
    unittest.main()
