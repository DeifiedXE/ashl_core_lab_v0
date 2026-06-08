import unittest

from ashl_core.micro_push_box_trial_runner import run_need_state_driven_trial


class MicroPushBoxTrialRunnerTests(unittest.TestCase):
    def test_trial_returns_steps_and_summary(self):
        result = run_need_state_driven_trial(["move_up", "move_right", "push_down"], max_steps=3, random_seed=0)

        self.assertIn("steps", result)
        self.assertLessEqual(result["step_count"], 3)
        self.assertIsInstance(result["completed_goal"], bool)
        self.assertIn("final_need_state", result)
        self.assertIn("final_result", result)

    def test_reachable_candidate_actions_can_complete_goal(self):
        result = run_need_state_driven_trial(["move_up", "move_right", "push_down"], max_steps=10, random_seed=0)

        self.assertTrue(result["completed_goal"])
        self.assertEqual(result["stop_reason"], "need_satisfied")
        self.assertEqual(result["final_need_state"]["current_value"], 1)
        self.assertTrue(result["final_need_state"]["satisfied"])
        self.assertEqual(result["final_result"], "goal_reached")
        self.assertLessEqual(result["step_count"], 10)

    def test_blocked_candidates_stop_at_max_steps(self):
        result = run_need_state_driven_trial(["push_right", "wait"], max_steps=3, random_seed=0)

        self.assertFalse(result["completed_goal"])
        self.assertEqual(result["stop_reason"], "max_steps_reached")
        self.assertEqual(result["step_count"], 3)
        self.assertEqual(result["final_need_state"]["current_value"], 0)
        self.assertFalse(result["final_need_state"]["satisfied"])

    def test_each_selected_action_is_from_candidates_or_wait(self):
        candidates = ["move_up", "move_right", "push_down"]
        result = run_need_state_driven_trial(candidates, max_steps=10, random_seed=0)

        for step in result["steps"]:
            self.assertIn(step["selected_action"], candidates + ["wait"])

    def test_step_shape_contains_selection_and_trace_fields(self):
        result = run_need_state_driven_trial(["move_up", "move_right", "push_down"], max_steps=1, random_seed=0)
        step = result["steps"][0]

        self.assertEqual(
            set(step),
            {
                "step_index",
                "selected_action",
                "selection_reason",
                "tactile_result",
                "need_state",
                "agent_pos",
                "box_pos",
                "trace",
            },
        )

    def test_invalid_candidate_action_raises_value_error(self):
        with self.assertRaises(ValueError):
            run_need_state_driven_trial(["push right"], max_steps=1, random_seed=0)

    def test_trial_does_not_write_learning_or_memory_outputs(self):
        result = run_need_state_driven_trial(["move_up", "move_right", "push_down"], max_steps=2, random_seed=0)
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
        for step in result["steps"]:
            self.assertTrue(forbidden_keys.isdisjoint(step))
            self.assertTrue(forbidden_keys.isdisjoint(step["trace"]))


if __name__ == "__main__":
    unittest.main()
