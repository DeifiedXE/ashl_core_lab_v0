import unittest

from ashl_core.micro_navigation_sandbox import (
    ALLOWED_NAVIGATION_ACTIONS,
    apply_navigation_action,
    build_initial_navigation_state,
    manhattan_distance_to_goal,
    select_navigation_action_toward_goal,
    validate_navigation_action,
)


class MicroNavigationSandboxTests(unittest.TestCase):
    def test_initial_state_shape(self):
        state = build_initial_navigation_state()

        self.assertEqual(state["grid"], ("#####", "#...#", "#.Q.#", "#..G#", "#####"))
        self.assertEqual(state["agent_pos"], (2, 2))
        self.assertEqual(state["goal_pos"], (3, 3))
        self.assertEqual(state["tick"], 0)

    def test_move_into_wall_returns_wall_blocked(self):
        state = build_initial_navigation_state()
        result = apply_navigation_action(state, "move_left")
        result = apply_navigation_action(result["state"], "move_left")

        self.assertEqual(result["trace"]["result"], "wall_blocked")
        self.assertTrue(result["trace"]["blocked"])
        self.assertEqual(result["trace"]["agent_pos"], (2, 1))

    def test_move_toward_empty_returns_moved(self):
        result = apply_navigation_action(build_initial_navigation_state(), "move_down")

        self.assertEqual(result["trace"]["result"], "moved")
        self.assertFalse(result["trace"]["blocked"])
        self.assertEqual(result["trace"]["agent_pos"], (3, 2))

    def test_move_into_goal_returns_goal_reached(self):
        state = apply_navigation_action(build_initial_navigation_state(), "move_down")["state"]
        result = apply_navigation_action(state, "move_right")

        self.assertEqual(result["trace"]["result"], "goal_reached")
        self.assertEqual(result["trace"]["agent_pos"], result["trace"]["goal_pos"])
        self.assertEqual(result["trace"]["distance_to_goal"], 0)

    def test_wait_returns_wait_without_moving(self):
        state = build_initial_navigation_state()
        result = apply_navigation_action(state, "wait")

        self.assertEqual(result["trace"]["result"], "wait")
        self.assertEqual(result["trace"]["agent_pos"], state["agent_pos"])
        self.assertFalse(result["trace"]["blocked"])

    def test_manhattan_distance_to_goal(self):
        self.assertEqual(manhattan_distance_to_goal((2, 2), (3, 3)), 2)
        self.assertEqual(manhattan_distance_to_goal((3, 3), (3, 3)), 0)

    def test_selection_favors_action_reducing_distance(self):
        action = select_navigation_action_toward_goal(
            build_initial_navigation_state(),
            ["move_up", "move_down", "move_right"],
        )

        self.assertEqual(action, "move_down")

    def test_selection_falls_back_to_first_candidate_when_no_reducing_action(self):
        action = select_navigation_action_toward_goal(build_initial_navigation_state(), ["wait", "move_up"])

        self.assertEqual(action, "wait")

    def test_allowed_action_set_is_closed(self):
        self.assertEqual(
            ALLOWED_NAVIGATION_ACTIONS,
            {"move_up", "move_down", "move_left", "move_right", "wait"},
        )

    def test_invalid_action_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_navigation_action("push_down")
        with self.assertRaises(ValueError):
            apply_navigation_action(build_initial_navigation_state(), "push_down")


if __name__ == "__main__":
    unittest.main()
