import copy
import unittest

from ashl_core.micro_push_box_sandbox import (
    build_initial_state,
    manhattan_distance_to_goal,
    rank_candidate_actions_with_goal_bias,
    score_action_goal_direction,
    suggest_next_action_with_goal_bias,
)


class GoalDirectionBiasTests(unittest.TestCase):
    def test_manhattan_distance_to_goal(self):
        self.assertEqual(manhattan_distance_to_goal((2, 3), (3, 3)), 1)
        self.assertEqual(manhattan_distance_to_goal((1, 1), (3, 4)), 5)

    def test_push_toward_goal_scores_positive(self):
        state = build_initial_state()

        self.assertEqual(state["box_pos"], (2, 3))
        self.assertEqual(state["goal_pos"], (3, 3))
        self.assertEqual(score_action_goal_direction(state, "push_down"), 2)

    def test_push_away_from_goal_scores_negative(self):
        state = build_initial_state()

        self.assertEqual(score_action_goal_direction(state, "push_up"), -2)

    def test_move_touch_wait_goal_bias_is_zero(self):
        state = build_initial_state()

        self.assertEqual(score_action_goal_direction(state, "move_down"), 0)
        self.assertEqual(score_action_goal_direction(state, "touch_down"), 0)
        self.assertEqual(score_action_goal_direction(state, "wait"), 0)

    def test_invalid_candidate_raises_value_error(self):
        with self.assertRaises(ValueError):
            score_action_goal_direction(build_initial_state(), "push diagonal")

        with self.assertRaises(ValueError):
            rank_candidate_actions_with_goal_bias(build_initial_state(), ["push_down", "open_door"])

    def test_ranking_puts_goal_improving_action_ahead_of_worsening_action(self):
        state = build_initial_state()

        self.assertEqual(
            rank_candidate_actions_with_goal_bias(state, ["push_up", "push_down"]),
            ["push_down", "push_up"],
        )
        self.assertEqual(suggest_next_action_with_goal_bias(state, ["push_up", "push_down"]), "push_down")

    def test_goal_bias_combines_with_existing_outcome_weighting(self):
        state = build_initial_state()
        state["action_history"] = (
            {"action": "push_up", "result": "goal_reached", "tick": 1},
            {"action": "push_down", "result": "empty", "tick": 2},
        )

        self.assertEqual(score_action_goal_direction(state, "push_up"), -2)
        self.assertEqual(score_action_goal_direction(state, "push_down"), 2)
        self.assertEqual(
            rank_candidate_actions_with_goal_bias(state, ["push_up", "push_down"]),
            ["push_up", "push_down"],
        )

    def test_helpers_do_not_modify_state_or_write_learning_outputs(self):
        state = build_initial_state()
        before = copy.deepcopy(state)

        rank_candidate_actions_with_goal_bias(state, ["push_up", "push_down", "wait"])
        suggestion = suggest_next_action_with_goal_bias(state, ["push_up", "push_down"])

        self.assertEqual(state, before)
        self.assertEqual(suggestion, "push_down")
        forbidden_keys = {
            "lesson_store_write",
            "memory_layer_write",
            "memory_write",
            "lesson_candidate",
            "solver",
            "pathfinding",
        }
        self.assertTrue(forbidden_keys.isdisjoint(state))


if __name__ == "__main__":
    unittest.main()
