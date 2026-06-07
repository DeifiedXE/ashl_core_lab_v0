import copy
import unittest

from ashl_core.micro_push_box_sandbox import (
    OUTCOME_WEIGHTS,
    build_initial_state,
    rank_candidate_actions_by_outcome_weight,
    score_action_from_history,
    suggest_next_action_by_outcome_weight,
)


class ActionOutcomeWeightingTests(unittest.TestCase):
    def test_outcome_weights_are_minimal_fixed_values(self):
        self.assertEqual(
            OUTCOME_WEIGHTS,
            {
                "box_blocked": -2,
                "wall_blocked": -2,
                "blocked": -2,
                "box_contact": 0,
                "empty": 0,
                "wait": 0,
                "box_pushed": 2,
                "goal_reached": 5,
            },
        )

    def test_box_pushed_scores_higher_than_box_blocked(self):
        state = build_initial_state()
        state["action_history"] = (
            {"action": "push_right", "result": "box_blocked", "tick": 1},
            {"action": "push_down", "result": "box_pushed", "tick": 2},
        )

        self.assertLess(score_action_from_history(state, "push_right"), score_action_from_history(state, "push_down"))
        self.assertEqual(
            rank_candidate_actions_by_outcome_weight(state, ["push_right", "push_down"]),
            ["push_down", "push_right"],
        )
        self.assertEqual(suggest_next_action_by_outcome_weight(state, ["push_right", "push_down"]), "push_down")

    def test_goal_reached_scores_highest_candidate(self):
        state = build_initial_state()
        state["action_history"] = (
            {"action": "push_down", "result": "box_pushed", "tick": 1},
            {"action": "move_down", "result": "goal_reached", "tick": 2},
        )

        self.assertEqual(
            rank_candidate_actions_by_outcome_weight(state, ["push_down", "move_down"]),
            ["move_down", "push_down"],
        )
        self.assertEqual(suggest_next_action_by_outcome_weight(state, ["push_down", "move_down"]), "move_down")

    def test_tie_keeps_candidate_order(self):
        state = build_initial_state()
        state["action_history"] = (
            {"action": "touch_right", "result": "box_contact", "tick": 1},
            {"action": "wait", "result": "wait", "tick": 2},
        )

        self.assertEqual(
            rank_candidate_actions_by_outcome_weight(state, ["wait", "touch_right"]),
            ["wait", "touch_right"],
        )

    def test_no_history_keeps_candidate_order(self):
        state = build_initial_state()

        self.assertEqual(score_action_from_history(state, "push_right"), 0)
        self.assertEqual(
            rank_candidate_actions_by_outcome_weight(state, ["push_right", "push_down"]),
            ["push_right", "push_down"],
        )

    def test_invalid_candidate_action_raises_value_error(self):
        with self.assertRaises(ValueError):
            rank_candidate_actions_by_outcome_weight(build_initial_state(), ["push_right", "push right"])

        with self.assertRaises(ValueError):
            suggest_next_action_by_outcome_weight(build_initial_state(), ["open_door"])

    def test_empty_candidate_list_raises_value_error_for_suggestion(self):
        with self.assertRaises(ValueError):
            suggest_next_action_by_outcome_weight(build_initial_state(), [])

    def test_helpers_do_not_mutate_state(self):
        state = build_initial_state()
        state["action_history"] = (
            {"action": "push_right", "result": "box_blocked", "tick": 1},
            {"action": "push_down", "result": "box_pushed", "tick": 2},
        )
        before = copy.deepcopy(state)

        score_action_from_history(state, "push_down")
        rank_candidate_actions_by_outcome_weight(state, ["push_right", "push_down"])
        suggest_next_action_by_outcome_weight(state, ["push_right", "push_down"])

        self.assertEqual(state, before)

    def test_suggested_action_is_always_from_candidates(self):
        state = build_initial_state()
        state["action_history"] = ({"action": "push_down", "result": "goal_reached", "tick": 1},)

        suggestion = suggest_next_action_by_outcome_weight(state, ["push_right", "wait"])

        self.assertIn(suggestion, ["push_right", "wait"])


if __name__ == "__main__":
    unittest.main()
