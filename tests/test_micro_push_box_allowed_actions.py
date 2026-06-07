import unittest

from ashl_core.micro_push_box_sandbox import (
    ALLOWED_ACTION_SET,
    apply_tactile_action,
    build_initial_state,
    validate_allowed_action,
)


class MicroPushBoxAllowedActionTests(unittest.TestCase):
    def test_allowed_action_set_contains_thirteen_actions(self):
        self.assertEqual(len(ALLOWED_ACTION_SET), 13)
        self.assertEqual(
            ALLOWED_ACTION_SET,
            frozenset(
                {
                    "touch_up",
                    "touch_down",
                    "touch_left",
                    "touch_right",
                    "move_up",
                    "move_down",
                    "move_left",
                    "move_right",
                    "push_up",
                    "push_down",
                    "push_left",
                    "push_right",
                    "wait",
                }
            ),
        )

    def test_touch_move_push_and_wait_are_allowed(self):
        for action in (
            "touch_up",
            "touch_down",
            "touch_left",
            "touch_right",
            "move_up",
            "move_down",
            "move_left",
            "move_right",
            "push_up",
            "push_down",
            "push_left",
            "push_right",
            "wait",
        ):
            with self.subTest(action=action):
                self.assertEqual(validate_allowed_action(action), action)

    def test_invalid_actions_raise_value_error(self):
        for action in ("move_diagonal", "push right", "open_door"):
            with self.subTest(action=action):
                with self.assertRaises(ValueError):
                    validate_allowed_action(action)
                with self.assertRaises(ValueError):
                    apply_tactile_action(build_initial_state(), action)

    def test_wait_action_returns_tactile_trace_without_motion(self):
        state = build_initial_state()
        before_agent_pos = state["agent_pos"]
        before_box_pos = state["box_pos"]

        result = apply_tactile_action(state, "wait")
        trace = result["trace"]

        self.assertEqual(trace["trace_type"], "tactile_sandbox_trace")
        self.assertEqual(trace["action"], "wait")
        self.assertEqual(trace["result"], "wait")
        self.assertEqual(trace["contact"], "none")
        self.assertFalse(trace["blocked"])
        self.assertEqual(trace["tick"], 1)
        self.assertEqual(result["state"]["agent_pos"], before_agent_pos)
        self.assertEqual(result["state"]["box_pos"], before_box_pos)


if __name__ == "__main__":
    unittest.main()
