import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_approach_box_trial_cli


class ApproachBoxTrialCliTests(unittest.TestCase):
    def test_approach_box_trial_cli_wrapper_returns_ok(self):
        result = run_approach_box_trial_cli(max_steps=20)
        boundary = result["boundary"]

        self.assertEqual(result["command"], "run-approach-box-trial")
        self.assertEqual(result["flow"], "approach_box_trial_cli_v0")
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["completed_approach"])
        self.assertEqual(result["initial_agent_pos"], [1, 1])
        self.assertEqual(result["box_pos"], [3, 4])
        self.assertEqual(result["final_agent_pos"], [3, 3])
        self.assertEqual(result["final_distance_to_box"], 1)
        self.assertEqual(result["step_count"], 4)
        self.assertEqual(result["selected_actions"], ["move_down", "move_down", "move_right", "move_right"])
        self.assertIs(result["llm_used"], False)
        self.assertIs(boundary["llm_used"], False)
        self.assertIs(boundary["creates_lesson_candidate"], False)
        self.assertIs(boundary["writes_lesson_store"], False)
        self.assertIs(boundary["writes_memory_layer"], False)
        self.assertIs(boundary["changes_navigation_behavior"], False)
        self.assertIs(boundary["two_trial_learning_check"], False)
        self.assertIs(boundary["pathfinding_used"], False)
        self.assertIs(boundary["box_pushed"], False)

    def test_approach_box_trial_cli_respects_max_steps(self):
        result = run_approach_box_trial_cli(max_steps=1)

        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["completed_approach"])
        self.assertEqual(result["final_distance_to_box"], 4)
        self.assertEqual(result["step_count"], 1)
        self.assertEqual(result["stop_reason"], "max_steps_reached")
        self.assertEqual(result["selected_actions"], ["move_down"])
        self.assertIs(result["llm_used"], False)

    def test_approach_box_trial_cli_does_not_return_learning_outputs(self):
        result = run_approach_box_trial_cli(max_steps=20)
        forbidden_keys = {
            "lesson_candidate",
            "lesson_store_write",
            "memory_layer_write",
            "memory_write",
            "llm_prompt",
            "pathfinding",
            "full_route_replay",
            "two_trial_learning_check",
        }

        self.assertTrue(forbidden_keys.isdisjoint(result))

    def test_module_cli_approach_box_trial_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-approach-box-trial",
                "--max-steps",
                "10",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["command"], "run-approach-box-trial")
        self.assertEqual(result["flow"], "approach_box_trial_cli_v0")
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["completed_approach"])
        self.assertEqual(result["final_distance_to_box"], 1)
        self.assertIs(result["llm_used"], False)


if __name__ == "__main__":
    unittest.main()
