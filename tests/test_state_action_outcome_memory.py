import copy
import unittest

from ashl_core.micro_push_box_sandbox import (
    apply_tactile_action,
    build_initial_state,
    build_state_action_key,
    find_previous_same_state_action_result,
    rank_candidate_actions_by_state_action_memory,
    score_action_from_state_action_memory,
    suggest_next_action_by_state_action_memory,
)


class StateActionOutcomeMemoryTests(unittest.TestCase):
    def test_same_state_action_blocked_result_can_be_read_back(self):
        state = apply_tactile_action(build_initial_state(), "push_right")["state"]
        previous = find_previous_same_state_action_result(state, "push_right")

        self.assertIsNotNone(previous)
        self.assertEqual(previous["agent_pos"], (2, 2))
        self.assertEqual(previous["box_pos"], (2, 3))
        self.assertEqual(previous["goal_pos"], (3, 3))
        self.assertEqual(previous["action"], "push_right")
        self.assertEqual(previous["result"], "box_blocked")

    def test_same_action_different_agent_pos_does_not_reuse_previous_result(self):
        state = apply_tactile_action(build_initial_state(), "push_right")["state"]
        state["agent_pos"] = (1, 1)

        self.assertIsNone(find_previous_same_state_action_result(state, "push_right"))
        self.assertEqual(score_action_from_state_action_memory(state, "push_right"), 0)

    def test_same_action_different_box_pos_does_not_reuse_previous_result(self):
        state = apply_tactile_action(build_initial_state(), "push_right")["state"]
        state["box_pos"] = (1, 3)

        self.assertIsNone(find_previous_same_state_action_result(state, "push_right"))
        self.assertEqual(score_action_from_state_action_memory(state, "push_right"), 0)

    def test_state_action_scores_use_local_result_weights(self):
        state = build_initial_state()
        key = build_state_action_key(state, "push_down")
        state["action_history"] = ({**key, "result": "box_blocked", "tick": 1},)
        self.assertEqual(score_action_from_state_action_memory(state, "push_down"), -2)

        state["action_history"] = ({**key, "result": "box_pushed", "tick": 2},)
        self.assertEqual(score_action_from_state_action_memory(state, "push_down"), 2)

        state["action_history"] = ({**key, "result": "goal_reached", "tick": 3},)
        self.assertEqual(score_action_from_state_action_memory(state, "push_down"), 5)

        state["action_history"] = ({**key, "result": "empty", "tick": 4},)
        self.assertEqual(score_action_from_state_action_memory(state, "push_down"), 0)

    def test_no_local_history_scores_zero(self):
        self.assertEqual(score_action_from_state_action_memory(build_initial_state(), "push_right"), 0)

    def test_ranking_uses_local_state_action_score_and_keeps_tie_order(self):
        state = build_initial_state()
        right_key = build_state_action_key(state, "push_right")
        down_key = build_state_action_key(state, "push_down")
        state["action_history"] = (
            {**right_key, "result": "box_blocked", "tick": 1},
            {**down_key, "result": "box_pushed", "tick": 2},
        )

        self.assertEqual(
            rank_candidate_actions_by_state_action_memory(state, ["push_right", "push_down"]),
            ["push_down", "push_right"],
        )
        self.assertEqual(
            rank_candidate_actions_by_state_action_memory(build_initial_state(), ["wait", "touch_right"]),
            ["wait", "touch_right"],
        )

    def test_suggest_next_action_by_state_action_memory(self):
        state = build_initial_state()
        right_key = build_state_action_key(state, "push_right")
        down_key = build_state_action_key(state, "push_down")
        state["action_history"] = (
            {**right_key, "result": "box_blocked", "tick": 1},
            {**down_key, "result": "goal_reached", "tick": 2},
        )

        self.assertEqual(suggest_next_action_by_state_action_memory(state, ["push_right", "push_down"]), "push_down")

    def test_invalid_candidate_raises_value_error(self):
        with self.assertRaises(ValueError):
            build_state_action_key(build_initial_state(), "push diagonal")

        with self.assertRaises(ValueError):
            rank_candidate_actions_by_state_action_memory(build_initial_state(), ["push_right", "open_door"])

        with self.assertRaises(ValueError):
            suggest_next_action_by_state_action_memory(build_initial_state(), [])

    def test_helpers_do_not_modify_state_or_write_learning_outputs(self):
        state = apply_tactile_action(build_initial_state(), "push_right")["state"]
        before = copy.deepcopy(state)

        find_previous_same_state_action_result(state, "push_right")
        score_action_from_state_action_memory(state, "push_right")
        rank_candidate_actions_by_state_action_memory(state, ["push_right", "wait"])
        suggest_next_action_by_state_action_memory(state, ["push_right", "wait"])

        self.assertEqual(state, before)
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
