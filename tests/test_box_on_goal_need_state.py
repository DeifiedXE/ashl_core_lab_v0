import copy
import unittest

from ashl_core.micro_push_box_sandbox import (
    apply_tactile_action,
    build_box_on_goal_need_state,
    build_initial_state,
)


class BoxOnGoalNeedStateTests(unittest.TestCase):
    def test_initial_state_need_is_unsatisfied(self):
        need_state = build_box_on_goal_need_state(build_initial_state())

        self.assertEqual(
            need_state,
            {
                "need_name": "box_on_goal",
                "target_value": 1,
                "current_value": 0,
                "satisfied": False,
            },
        )

    def test_box_on_goal_need_is_satisfied(self):
        state = build_initial_state()
        state["box_pos"] = state["goal_pos"]

        need_state = build_box_on_goal_need_state(state)

        self.assertEqual(need_state["need_name"], "box_on_goal")
        self.assertEqual(need_state["target_value"], 1)
        self.assertEqual(need_state["current_value"], 1)
        self.assertTrue(need_state["satisfied"])

    def test_push_box_to_goal_trace_contains_satisfied_need_state(self):
        state = build_initial_state()
        state["agent_pos"] = (1, 3)
        state["box_pos"] = (2, 3)

        trace = apply_tactile_action(state, "push_down")["trace"]

        self.assertEqual(trace["result"], "goal_reached")
        self.assertEqual(
            trace["need_state"],
            {
                "need_name": "box_on_goal",
                "target_value": 1,
                "current_value": 1,
                "satisfied": True,
            },
        )

    def test_box_blocked_trace_need_state_remains_unsatisfied(self):
        trace = apply_tactile_action(build_initial_state(), "push_right")["trace"]

        self.assertEqual(trace["result"], "box_blocked")
        self.assertEqual(trace["need_state"]["current_value"], 0)
        self.assertFalse(trace["need_state"]["satisfied"])

    def test_helper_does_not_modify_state(self):
        state = build_initial_state()
        before = copy.deepcopy(state)

        build_box_on_goal_need_state(state)

        self.assertEqual(state, before)

    def test_need_state_does_not_write_learning_or_memory_outputs(self):
        trace = apply_tactile_action(build_initial_state(), "push_right")["trace"]
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

        self.assertTrue(forbidden_keys.isdisjoint(trace))
        self.assertTrue(forbidden_keys.isdisjoint(trace["need_state"]))


if __name__ == "__main__":
    unittest.main()
