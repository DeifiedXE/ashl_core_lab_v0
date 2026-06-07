import unittest

from ashl_core.micro_push_box_sandbox import apply_tactile_action, build_initial_state


class RepeatedBlockedActionTraceTests(unittest.TestCase):
    def test_first_push_right_has_no_same_action_history(self):
        first = apply_tactile_action(build_initial_state(), "push_right")

        self.assertEqual(first["trace"]["result"], "box_blocked")
        self.assertEqual(first["trace"]["history"], {"same_action_attempted_before": False})

    def test_second_push_right_records_previous_blocked_result(self):
        first = apply_tactile_action(build_initial_state(), "push_right")
        second = apply_tactile_action(first["state"], "push_right")
        history = second["trace"]["history"]

        self.assertEqual(second["trace"]["result"], "box_blocked")
        self.assertTrue(history["same_action_attempted_before"])
        self.assertEqual(history["previous_same_action_result"], "box_blocked")
        self.assertEqual(history["previous_same_action_tick"], 1)

    def test_different_action_does_not_count_as_same_action_history(self):
        first = apply_tactile_action(build_initial_state(), "push_right")
        second = apply_tactile_action(first["state"], "touch_right")

        self.assertEqual(second["trace"]["result"], "box_contact")
        self.assertEqual(second["trace"]["history"], {"same_action_attempted_before": False})

    def test_state_history_is_carried_into_next_state(self):
        first = apply_tactile_action(build_initial_state(), "push_right")
        second = apply_tactile_action(first["state"], "push_right")

        self.assertEqual(len(first["state"]["action_history"]), 1)
        self.assertEqual(len(second["state"]["action_history"]), 2)
        self.assertEqual(second["state"]["action_history"][0]["action"], "push_right")
        self.assertEqual(second["state"]["action_history"][0]["result"], "box_blocked")
        self.assertEqual(second["state"]["action_history"][1]["action"], "push_right")
        self.assertEqual(second["state"]["action_history"][1]["result"], "box_blocked")

    def test_repeated_trace_does_not_create_learning_or_persistence_outputs(self):
        first = apply_tactile_action(build_initial_state(), "push_right")
        second_trace = apply_tactile_action(first["state"], "push_right")["trace"]
        forbidden_keys = {
            "lesson_store_write",
            "memory_layer_write",
            "memory_write",
            "lesson_candidate",
            "llm_prompt",
            "solver",
            "pathfinding",
            "persistence",
            "jsonl_write",
        }

        self.assertTrue(forbidden_keys.isdisjoint(second_trace))


if __name__ == "__main__":
    unittest.main()
