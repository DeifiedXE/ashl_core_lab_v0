import copy
import unittest

from ashl_core.micro_push_box_sandbox import (
    apply_tactile_action,
    build_initial_state,
    suggest_next_action_avoiding_repeat_blocked,
)


class AvoidRepeatedBlockedActionTests(unittest.TestCase):
    def test_push_right_blocked_then_candidates_push_right_wait_suggests_wait(self):
        first = apply_tactile_action(build_initial_state(), "push_right")

        self.assertEqual(first["trace"]["result"], "box_blocked")
        self.assertEqual(
            suggest_next_action_avoiding_repeat_blocked(first["state"], ["push_right", "wait"]),
            "wait",
        )

    def test_push_right_blocked_then_candidates_push_right_touch_left_suggests_touch_left(self):
        first = apply_tactile_action(build_initial_state(), "push_right")

        self.assertEqual(
            suggest_next_action_avoiding_repeat_blocked(first["state"], ["push_right", "touch_left"]),
            "touch_left",
        )

    def test_unblocked_action_is_not_avoided(self):
        first = apply_tactile_action(build_initial_state(), "touch_right")

        self.assertEqual(first["trace"]["result"], "box_contact")
        self.assertEqual(
            suggest_next_action_avoiding_repeat_blocked(first["state"], ["touch_right", "wait"]),
            "touch_right",
        )

    def test_missing_action_history_returns_first_candidate(self):
        state = build_initial_state()
        state.pop("action_history")

        self.assertEqual(
            suggest_next_action_avoiding_repeat_blocked(state, ["push_right", "wait"]),
            "push_right",
        )

    def test_all_candidates_blocked_returns_wait(self):
        state = build_initial_state()
        state["action_history"] = (
            {"action": "push_right", "result": "box_blocked", "tick": 1},
            {"action": "move_left", "result": "wall_blocked", "tick": 2},
        )

        self.assertEqual(
            suggest_next_action_avoiding_repeat_blocked(state, ["push_right", "move_left"]),
            "wait",
        )

    def test_invalid_candidate_action_raises_value_error(self):
        with self.assertRaises(ValueError):
            suggest_next_action_avoiding_repeat_blocked(build_initial_state(), ["push_right", "push right"])

    def test_helper_does_not_mutate_state(self):
        first = apply_tactile_action(build_initial_state(), "push_right")
        before = copy.deepcopy(first["state"])

        suggest_next_action_avoiding_repeat_blocked(first["state"], ["push_right", "wait"])

        self.assertEqual(first["state"], before)

    def test_helper_does_not_create_learning_or_memory_outputs(self):
        first = apply_tactile_action(build_initial_state(), "push_right")
        suggestion = suggest_next_action_avoiding_repeat_blocked(first["state"], ["push_right", "wait"])

        self.assertEqual(suggestion, "wait")
        self.assertNotIn("lesson_store_write", first["state"])
        self.assertNotIn("memory_layer_write", first["state"])
        self.assertNotIn("lesson_candidate", first["state"])


if __name__ == "__main__":
    unittest.main()
