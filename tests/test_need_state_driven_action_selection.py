import copy
import unittest

from ashl_core.micro_push_box_sandbox import (
    build_initial_state,
    select_action_for_need_state,
)


class NeedStateDrivenActionSelectionTests(unittest.TestCase):
    def test_unsatisfied_need_uses_intrinsic_action_selection(self):
        state = build_initial_state()
        state["action_history"] = (
            {"action": "push_right", "result": "box_blocked", "tick": 1},
            {"action": "push_down", "result": "box_pushed", "tick": 2},
        )

        result = select_action_for_need_state(state, ["push_right", "push_down"], random_seed=5)

        self.assertEqual(result["need_state"]["current_value"], 0)
        self.assertFalse(result["need_state"]["satisfied"])
        self.assertEqual(result["selected_action"], "push_down")
        self.assertEqual(result["selection_reason"], "need_unsatisfied_intrinsic_selection")
        self.assertEqual(result["candidate_actions"], ["push_right", "push_down"])

    def test_satisfied_need_selects_wait(self):
        state = build_initial_state()
        state["box_pos"] = state["goal_pos"]

        result = select_action_for_need_state(state, ["push_right", "push_down"], random_seed=5)

        self.assertEqual(result["need_state"]["current_value"], 1)
        self.assertTrue(result["need_state"]["satisfied"])
        self.assertEqual(result["selected_action"], "wait")
        self.assertEqual(result["selection_reason"], "need_satisfied_wait")

    def test_invalid_candidate_action_raises_value_error(self):
        with self.assertRaises(ValueError):
            select_action_for_need_state(build_initial_state(), ["push right"], random_seed=1)

    def test_empty_candidate_actions_raises_value_error(self):
        with self.assertRaises(ValueError):
            select_action_for_need_state(build_initial_state(), [], random_seed=1)

    def test_helper_does_not_modify_state(self):
        state = build_initial_state()
        state["action_history"] = (
            {"action": "push_right", "result": "box_blocked", "tick": 1},
            {"action": "push_down", "result": "box_pushed", "tick": 2},
        )
        before = copy.deepcopy(state)

        select_action_for_need_state(state, ["push_right", "push_down"], random_seed=7)

        self.assertEqual(state, before)

    def test_result_does_not_write_learning_or_memory_outputs(self):
        result = select_action_for_need_state(build_initial_state(), ["push_right", "push_down"], random_seed=3)
        forbidden_keys = {
            "lesson_store_write",
            "memory_layer_write",
            "memory_write",
            "lesson_candidate",
            "emotion",
            "dopamine",
            "solver",
            "pathfinding",
        }

        self.assertTrue(forbidden_keys.isdisjoint(result))
        self.assertTrue(forbidden_keys.isdisjoint(result["need_state"]))


if __name__ == "__main__":
    unittest.main()
