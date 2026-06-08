import unittest

from ashl_core.micro_navigation_sandbox import ALLOWED_NAVIGATION_ACTIONS
from ashl_core.micro_navigation_trial_runner import (
    run_navigation_goal_trial,
    run_navigation_multi_goal_trial,
    run_navigation_obstacle_trial,
)


class MicroNavigationTrialRunnerTests(unittest.TestCase):
    def test_trial_reaches_goal(self):
        result = run_navigation_goal_trial(max_steps=10)

        self.assertTrue(result["completed_goal"])
        self.assertEqual(result["stop_reason"], "goal_reached")
        self.assertEqual(result["final_agent_pos"], result["goal_pos"])
        self.assertLessEqual(result["step_count"], 10)

    def test_trial_records_summary_shape(self):
        result = run_navigation_goal_trial(max_steps=10)

        self.assertIn("completed_goal", result)
        self.assertIn("step_count", result)
        self.assertIn("stop_reason", result)
        self.assertIn("final_agent_pos", result)
        self.assertIn("goal_pos", result)
        self.assertIn("selected_actions", result)
        self.assertIn("steps", result)

    def test_trial_selected_actions_only_from_allowed_candidates(self):
        candidates = ["move_down", "move_right"]
        result = run_navigation_goal_trial(candidate_actions=candidates, max_steps=10)

        self.assertTrue(result["completed_goal"])
        self.assertTrue(all(action in candidates for action in result["selected_actions"]))

    def test_trial_stops_when_goal_reached(self):
        result = run_navigation_goal_trial(candidate_actions=["move_down", "move_right"], max_steps=10)

        self.assertEqual(result["step_count"], 2)
        self.assertEqual(result["selected_actions"], ["move_down", "move_right"])
        self.assertEqual(result["steps"][-1]["navigation_result"], "goal_reached")

    def test_trial_respects_max_steps(self):
        result = run_navigation_goal_trial(candidate_actions=["wait"], max_steps=3)

        self.assertFalse(result["completed_goal"])
        self.assertEqual(result["stop_reason"], "max_steps_reached")
        self.assertEqual(result["step_count"], 3)
        self.assertEqual(result["selected_actions"], ["wait", "wait", "wait"])

    def test_step_trace_shape(self):
        result = run_navigation_goal_trial(candidate_actions=["move_down"], max_steps=1)
        step = result["steps"][0]

        self.assertEqual(
            set(step),
            {
                "step_index",
                "selected_action",
                "navigation_result",
                "agent_pos",
                "goal_pos",
                "distance_to_goal",
                "trace",
            },
        )
        self.assertEqual(step["trace"]["trace_type"], "navigation_sandbox_trace")

    def test_invalid_candidate_action_raises_value_error(self):
        with self.assertRaises(ValueError):
            run_navigation_goal_trial(candidate_actions=["move_down", "push_down"], max_steps=3)

    def test_multi_goal_trial_reaches_two_goals(self):
        result = run_navigation_multi_goal_trial(max_steps=20)

        self.assertTrue(result["completed_all_goals"])
        self.assertEqual(result["goals_reached"], 2)
        self.assertEqual(result["goal_count"], 2)
        self.assertEqual(result["stop_reason"], "all_goals_reached")
        self.assertEqual(result["final_agent_pos"], result["final_goal_pos"])
        self.assertGreater(result["step_count"], 2)
        self.assertTrue(all(action in ALLOWED_NAVIGATION_ACTIONS for action in result["selected_actions"]))

    def test_multi_goal_trial_records_first_goal_and_second_goal_spawn(self):
        result = run_navigation_multi_goal_trial(max_steps=20)
        reached_steps = [step for step in result["steps"] if step["goal_reached_this_step"]]

        self.assertEqual(len(reached_steps), 2)
        self.assertTrue(reached_steps[0]["next_goal_spawned"])
        self.assertEqual(reached_steps[0]["goals_reached"], 1)
        self.assertEqual(reached_steps[0]["goal_index"], 1)
        self.assertFalse(reached_steps[1]["next_goal_spawned"])
        self.assertEqual(reached_steps[1]["goals_reached"], 2)
        self.assertEqual(reached_steps[1]["goal_index"], 2)

    def test_multi_goal_trial_summary_shape(self):
        result = run_navigation_multi_goal_trial(max_steps=20)

        self.assertIn("completed_all_goals", result)
        self.assertIn("goals_reached", result)
        self.assertIn("goal_count", result)
        self.assertIn("step_count", result)
        self.assertIn("selected_actions", result)
        self.assertIn("final_agent_pos", result)
        self.assertIn("final_goal_pos", result)
        self.assertIn("steps", result)

    def test_multi_goal_trial_respects_max_steps(self):
        result = run_navigation_multi_goal_trial(candidate_actions=["wait"], max_steps=3)

        self.assertFalse(result["completed_all_goals"])
        self.assertEqual(result["goals_reached"], 0)
        self.assertEqual(result["stop_reason"], "max_steps_reached")
        self.assertEqual(result["step_count"], 3)
        self.assertEqual(result["selected_actions"], ["wait", "wait", "wait"])

    def test_multi_goal_invalid_candidate_action_raises_value_error(self):
        with self.assertRaises(ValueError):
            run_navigation_multi_goal_trial(candidate_actions=["move_down", "push_down"], max_steps=3)

    def test_obstacle_trial_reaches_goal(self):
        result = run_navigation_obstacle_trial(max_steps=20)

        self.assertTrue(result["completed_goal"])
        self.assertEqual(result["stop_reason"], "goal_reached")
        self.assertEqual(result["final_agent_pos"], result["goal_pos"])
        self.assertGreater(result["step_count"], 2)
        self.assertTrue(all(action in ALLOWED_NAVIGATION_ACTIONS for action in result["selected_actions"]))

    def test_obstacle_trial_uses_blocked_aware_selection(self):
        result = run_navigation_obstacle_trial(max_steps=20)

        self.assertTrue(any(step["selection_rule"] == "blocked_aware_min_distance" for step in result["steps"]))
        self.assertTrue(any(step["blocked_candidates"] for step in result["steps"]))
        self.assertNotIn("wall_blocked", [step["navigation_result"] for step in result["steps"]])

    def test_obstacle_trial_summary_shape(self):
        result = run_navigation_obstacle_trial(max_steps=20)

        self.assertIn("completed_goal", result)
        self.assertIn("step_count", result)
        self.assertIn("stop_reason", result)
        self.assertIn("selected_actions", result)
        self.assertIn("final_agent_pos", result)
        self.assertIn("goal_pos", result)
        self.assertIn("steps", result)

    def test_obstacle_trial_respects_max_steps(self):
        result = run_navigation_obstacle_trial(candidate_actions=["wait"], max_steps=3)

        self.assertFalse(result["completed_goal"])
        self.assertEqual(result["stop_reason"], "max_steps_reached")
        self.assertEqual(result["step_count"], 3)
        self.assertEqual(result["selected_actions"], ["wait", "wait", "wait"])

    def test_obstacle_trial_invalid_candidate_action_raises_value_error(self):
        with self.assertRaises(ValueError):
            run_navigation_obstacle_trial(candidate_actions=["move_down", "push_down"], max_steps=3)


if __name__ == "__main__":
    unittest.main()
