import json
import subprocess
import sys
import unittest

from ashl_core.micro_navigation_sandbox import ALLOWED_NAVIGATION_ACTIONS
from ashl_core.teaching_cli import run_navigation_obstacle_trial_cli


class NavigationObstacleTrialCliTests(unittest.TestCase):
    def test_obstacle_trial_cli_returns_ok(self):
        result = run_navigation_obstacle_trial_cli(max_steps=20)

        self.assertEqual(result["command"], "run-navigation-obstacle-trial")
        self.assertEqual(result["flow"], "navigation_obstacle_trial_cli_patch")
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["completed_goal"])
        self.assertGreater(result["step_count"], 2)
        self.assertEqual(result["stop_reason"], "goal_reached")
        self.assertEqual(result["initial_agent_pos"], (1, 1))
        self.assertEqual(result["goal_pos"], (3, 5))
        self.assertEqual(result["final_agent_pos"], (3, 5))
        self.assertTrue(result["selected_actions"])
        self.assertTrue(result["wall_blocked_avoided"])

    def test_obstacle_trial_cli_selected_actions_are_allowed(self):
        result = run_navigation_obstacle_trial_cli(max_steps=20)

        self.assertTrue(all(action in ALLOWED_NAVIGATION_ACTIONS for action in result["selected_actions"]))

    def test_obstacle_trial_cli_boundary_flags_are_false(self):
        result = run_navigation_obstacle_trial_cli(max_steps=20)
        boundary = result["boundary"]

        self.assertIs(boundary["llm_used"], False)
        self.assertIs(boundary["creates_lesson_candidate"], False)
        self.assertIs(boundary["writes_lesson_store"], False)
        self.assertIs(boundary["writes_memory_layer"], False)
        self.assertIs(boundary["awakening_claim"], False)
        self.assertIs(boundary["changes_navigation_behavior"], False)

    def test_obstacle_trial_cli_respects_max_steps(self):
        result = run_navigation_obstacle_trial_cli(max_steps=1)

        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["completed_goal"])
        self.assertEqual(result["step_count"], 1)
        self.assertEqual(result["stop_reason"], "max_steps_reached")
        self.assertTrue(result["wall_blocked_avoided"])

    def test_module_cli_obstacle_trial_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-navigation-obstacle-trial",
                "--max-steps",
                "20",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["command"], "run-navigation-obstacle-trial")
        self.assertEqual(result["flow"], "navigation_obstacle_trial_cli_patch")
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["completed_goal"])
        self.assertTrue(result["wall_blocked_avoided"])

    def test_module_cli_obstacle_trial_default_outputs_json(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-navigation-obstacle-trial"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["completed_goal"])


if __name__ == "__main__":
    unittest.main()
