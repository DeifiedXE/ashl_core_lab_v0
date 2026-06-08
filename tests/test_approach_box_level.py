import unittest

from ashl_core.micro_navigation_sandbox import (
    ALLOWED_NAVIGATION_ACTIONS,
    apply_navigation_approach_box_action,
    create_navigation_approach_box_level_state,
    manhattan_distance_to_box,
    select_navigation_action_toward_box,
)
from ashl_core.micro_navigation_trial_runner import run_navigation_approach_box_trial


class ApproachBoxLevelTests(unittest.TestCase):
    def test_approach_box_initial_state_shape(self):
        state = create_navigation_approach_box_level_state()

        self.assertEqual(state["grid"], ("#######", "#Q....#", "#.###.#", "#...B.#", "#######"))
        self.assertEqual(state["agent_pos"], (1, 1))
        self.assertEqual(state["box_pos"], (3, 4))
        self.assertEqual(state["tick"], 0)
        self.assertNotIn("goal_pos", state)

    def test_manhattan_distance_to_box(self):
        self.assertEqual(manhattan_distance_to_box((1, 1), (3, 4)), 5)
        self.assertEqual(manhattan_distance_to_box((3, 3), (3, 4)), 1)

    def test_approach_box_action_trace_shape(self):
        result = apply_navigation_approach_box_action(create_navigation_approach_box_level_state(), "move_down")
        trace = result["trace"]

        self.assertEqual(trace["trace_type"], "navigation_approach_box_trace")
        self.assertEqual(trace["action"], "move_down")
        self.assertEqual(trace["result"], "moved")
        self.assertFalse(trace["blocked"])
        self.assertEqual(trace["agent_pos"], (2, 1))
        self.assertEqual(trace["box_pos"], (3, 4))
        self.assertEqual(trace["distance_to_box"], 4)
        self.assertFalse(trace["box_adjacent"])

    def test_approach_box_move_into_wall_returns_wall_blocked(self):
        result = apply_navigation_approach_box_action(create_navigation_approach_box_level_state(), "move_up")

        self.assertEqual(result["trace"]["result"], "wall_blocked")
        self.assertTrue(result["trace"]["blocked"])
        self.assertEqual(result["trace"]["agent_pos"], (1, 1))

    def test_approach_box_wait_returns_wait(self):
        result = apply_navigation_approach_box_action(create_navigation_approach_box_level_state(), "wait")

        self.assertEqual(result["trace"]["result"], "wait")
        self.assertFalse(result["trace"]["blocked"])
        self.assertEqual(result["trace"]["agent_pos"], (1, 1))

    def test_selection_moves_toward_box_and_avoids_wall(self):
        selection = select_navigation_action_toward_box(
            create_navigation_approach_box_level_state(),
            ["move_up", "move_down", "move_right"],
        )

        self.assertEqual(selection["selection_rule"], "toward_box_blocked_aware_min_distance")
        self.assertEqual(selection["selected_action"], "move_down")
        self.assertIn("move_up", selection["blocked_candidates"])

    def test_trial_reaches_box_adjacency(self):
        result = run_navigation_approach_box_trial(max_steps=20)

        self.assertTrue(result["completed_approach"])
        self.assertEqual(result["stop_reason"], "box_adjacent")
        self.assertEqual(manhattan_distance_to_box(result["final_agent_pos"], result["box_pos"]), 1)
        self.assertGreater(result["step_count"], 0)
        self.assertTrue(all(action in ALLOWED_NAVIGATION_ACTIONS for action in result["selected_actions"]))

    def test_trial_stops_when_box_adjacency_reached(self):
        result = run_navigation_approach_box_trial(max_steps=20)

        self.assertEqual(result["selected_actions"], ["move_down", "move_down", "move_right", "move_right"])
        self.assertEqual(result["step_count"], 4)
        self.assertTrue(result["steps"][-1]["box_adjacent"])

    def test_trial_respects_max_steps(self):
        result = run_navigation_approach_box_trial(candidate_actions=["wait"], max_steps=3)

        self.assertFalse(result["completed_approach"])
        self.assertEqual(result["stop_reason"], "max_steps_reached")
        self.assertEqual(result["step_count"], 3)
        self.assertEqual(result["selected_actions"], ["wait", "wait", "wait"])

    def test_invalid_action_raises_value_error(self):
        with self.assertRaises(ValueError):
            apply_navigation_approach_box_action(create_navigation_approach_box_level_state(), "push_down")
        with self.assertRaises(ValueError):
            run_navigation_approach_box_trial(candidate_actions=["move_down", "push_down"], max_steps=3)

    def test_approach_box_level_does_not_create_learning_outputs(self):
        result = run_navigation_approach_box_trial(max_steps=20)
        forbidden_keys = {
            "lesson_candidate",
            "lesson_store_write",
            "memory_layer_write",
            "memory_write",
            "llm_prompt",
            "full_route_replay",
            "two_trial_learning_check",
        }

        self.assertTrue(forbidden_keys.isdisjoint(result))
        for step in result["steps"]:
            self.assertTrue(forbidden_keys.isdisjoint(step))


if __name__ == "__main__":
    unittest.main()
