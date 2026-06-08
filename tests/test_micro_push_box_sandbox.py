import unittest

from ashl_core.micro_push_box_sandbox import (
    ALLOWED_ACTION_SET,
    OUTCOME_WEIGHTS,
    INITIAL_MAP,
    SUPPORTED_ACTIONS,
    apply_tactile_action,
    build_box_on_goal_need_state,
    build_initial_state,
    rank_candidate_actions_by_outcome_weight,
    score_action_from_history,
    select_action_for_need_state,
    select_intrinsic_action,
    suggest_next_action_avoiding_repeat_blocked,
    suggest_next_action_by_outcome_weight,
    validate_allowed_action,
)


class MicroPushBoxSandboxTests(unittest.TestCase):
    def test_initial_state_shape(self):
        state = build_initial_state()

        self.assertEqual(INITIAL_MAP, ("#####", "#...#", "#.QB#", "#..G#", "#####"))
        self.assertEqual(state["agent_pos"], (2, 2))
        self.assertEqual(state["box_pos"], (2, 3))
        self.assertEqual(state["goal_pos"], (3, 3))
        self.assertEqual(state["tick"], 0)
        self.assertEqual(state["action_history"], ())
        self.assertEqual(build_box_on_goal_need_state(state)["current_value"], 0)

    def test_supported_actions_include_touch_move_push(self):
        self.assertIn("touch_right", SUPPORTED_ACTIONS)
        self.assertIn("move_right", SUPPORTED_ACTIONS)
        self.assertIn("push_right", SUPPORTED_ACTIONS)
        self.assertIn("wait", SUPPORTED_ACTIONS)
        self.assertEqual(len(SUPPORTED_ACTIONS), 13)

    def test_allowed_action_set_has_expected_actions(self):
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

    def test_validate_allowed_action_returns_allowed_action(self):
        self.assertEqual(validate_allowed_action("touch_right"), "touch_right")
        self.assertEqual(validate_allowed_action("wait"), "wait")

    def test_validate_allowed_action_rejects_invalid_action(self):
        for action in ("move_diagonal", "push right", "open_door"):
            with self.subTest(action=action):
                with self.assertRaises(ValueError):
                    validate_allowed_action(action)

    def test_touch_box_returns_box_contact_without_moving(self):
        state = build_initial_state()
        result = apply_tactile_action(state, "touch_right")
        trace = result["trace"]

        self.assertEqual(trace["result"], "box_contact")
        self.assertEqual(trace["contact"], "box")
        self.assertFalse(trace["blocked"])
        self.assertEqual(result["state"]["agent_pos"], (2, 2))
        self.assertEqual(result["state"]["box_pos"], (2, 3))

    def test_touch_wall_returns_wall_blocked(self):
        state = build_initial_state()
        state["agent_pos"] = (1, 1)
        trace = apply_tactile_action(state, "touch_left")["trace"]

        self.assertEqual(trace["result"], "wall_blocked")
        self.assertEqual(trace["contact"], "wall")
        self.assertTrue(trace["blocked"])

    def test_move_empty_moves_agent(self):
        result = apply_tactile_action(build_initial_state(), "move_up")

        self.assertEqual(result["trace"]["result"], "empty")
        self.assertEqual(result["state"]["agent_pos"], (1, 2))

    def test_move_wall_is_blocked(self):
        state = build_initial_state()
        state["agent_pos"] = (1, 1)
        result = apply_tactile_action(state, "move_left")

        self.assertEqual(result["trace"]["result"], "wall_blocked")
        self.assertEqual(result["state"]["agent_pos"], (1, 1))

    def test_move_into_box_without_push_is_blocked(self):
        result = apply_tactile_action(build_initial_state(), "move_right")

        self.assertEqual(result["trace"]["result"], "box_blocked")
        self.assertEqual(result["state"]["agent_pos"], (2, 2))
        self.assertEqual(result["state"]["box_pos"], (2, 3))

    def test_push_box_into_empty_moves_box(self):
        state = build_initial_state()
        state["agent_pos"] = (1, 2)
        state["box_pos"] = (2, 2)
        result = apply_tactile_action(state, "push_down")

        self.assertEqual(result["trace"]["result"], "box_pushed")
        self.assertEqual(result["state"]["agent_pos"], (2, 2))
        self.assertEqual(result["state"]["box_pos"], (3, 2))

    def test_push_box_into_wall_is_blocked(self):
        result = apply_tactile_action(build_initial_state(), "push_right")

        self.assertEqual(result["trace"]["result"], "box_blocked")
        self.assertEqual(result["state"]["agent_pos"], (2, 2))
        self.assertEqual(result["state"]["box_pos"], (2, 3))

    def test_push_box_to_goal_returns_goal_reached(self):
        state = build_initial_state()
        state["agent_pos"] = (1, 3)
        state["box_pos"] = (2, 3)
        result = apply_tactile_action(state, "push_down")

        self.assertEqual(result["trace"]["result"], "goal_reached")
        self.assertEqual(result["trace"]["need_state"]["current_value"], 1)
        self.assertTrue(result["trace"]["need_state"]["satisfied"])
        self.assertEqual(result["state"]["agent_pos"], (2, 3))
        self.assertEqual(result["state"]["box_pos"], (3, 3))

    def test_wait_increments_tick_without_moving_agent_or_box(self):
        state = build_initial_state()
        result = apply_tactile_action(state, "wait")
        trace = result["trace"]

        self.assertEqual(trace["trace_type"], "tactile_sandbox_trace")
        self.assertEqual(trace["result"], "wait")
        self.assertEqual(trace["contact"], "none")
        self.assertFalse(trace["blocked"])
        self.assertEqual(trace["tick"], 1)
        self.assertEqual(result["state"]["agent_pos"], state["agent_pos"])
        self.assertEqual(result["state"]["box_pos"], state["box_pos"])
        self.assertEqual(result["state"]["goal_pos"], state["goal_pos"])

    def test_trace_includes_before_and_after(self):
        result = apply_tactile_action(build_initial_state(), "touch_right")
        trace = result["trace"]

        self.assertEqual(trace["trace_type"], "tactile_sandbox_trace")
        self.assertIn("before", trace)
        self.assertIn("after", trace)
        self.assertEqual(trace["tick"], 1)
        self.assertEqual(trace["agent_pos"], trace["after"]["agent_pos"])
        self.assertEqual(trace["box_pos"], trace["after"]["box_pos"])
        self.assertEqual(trace["goal_pos"], trace["after"]["goal_pos"])
        self.assertEqual(trace["history"], {"same_action_attempted_before": False})
        self.assertEqual(trace["need_state"]["need_name"], "box_on_goal")

    def test_repeated_action_trace_includes_previous_same_action_result(self):
        first = apply_tactile_action(build_initial_state(), "push_right")
        second = apply_tactile_action(first["state"], "push_right")

        self.assertEqual(first["trace"]["result"], "box_blocked")
        self.assertEqual(first["trace"]["history"], {"same_action_attempted_before": False})
        self.assertEqual(second["trace"]["result"], "box_blocked")
        self.assertTrue(second["trace"]["history"]["same_action_attempted_before"])
        self.assertEqual(second["trace"]["history"]["previous_same_action_result"], "box_blocked")
        self.assertEqual(second["trace"]["history"]["previous_same_action_tick"], 1)
        self.assertEqual(len(second["state"]["action_history"]), 2)

    def test_suggest_next_action_avoids_repeated_blocked_action(self):
        first = apply_tactile_action(build_initial_state(), "push_right")

        self.assertEqual(
            suggest_next_action_avoiding_repeat_blocked(first["state"], ["push_right", "wait"]),
            "wait",
        )

    def test_outcome_weights_include_expected_result_scores(self):
        self.assertEqual(OUTCOME_WEIGHTS["box_blocked"], -2)
        self.assertEqual(OUTCOME_WEIGHTS["wall_blocked"], -2)
        self.assertEqual(OUTCOME_WEIGHTS["box_pushed"], 2)
        self.assertEqual(OUTCOME_WEIGHTS["goal_reached"], 5)

    def test_outcome_weighting_prefers_pushed_over_blocked(self):
        state = build_initial_state()
        state["action_history"] = (
            {"action": "push_right", "result": "box_blocked", "tick": 1},
            {"action": "push_down", "result": "box_pushed", "tick": 2},
        )

        self.assertEqual(score_action_from_history(state, "push_right"), -2)
        self.assertEqual(score_action_from_history(state, "push_down"), 2)
        self.assertEqual(
            rank_candidate_actions_by_outcome_weight(state, ["push_right", "push_down"]),
            ["push_down", "push_right"],
        )
        self.assertEqual(suggest_next_action_by_outcome_weight(state, ["push_right", "push_down"]), "push_down")

    def test_intrinsic_action_selection_prefers_weighted_outcome_within_candidates(self):
        state = build_initial_state()
        state["action_history"] = (
            {"action": "push_right", "result": "box_blocked", "tick": 1},
            {"action": "push_down", "result": "box_pushed", "tick": 2},
        )

        self.assertEqual(select_intrinsic_action(state, ["push_right", "push_down"], random_seed=1), "push_down")

    def test_need_state_driven_selection_uses_wait_when_satisfied(self):
        state = build_initial_state()
        state["box_pos"] = state["goal_pos"]

        result = select_action_for_need_state(state, ["push_right", "push_down"], random_seed=1)

        self.assertEqual(result["selected_action"], "wait")
        self.assertEqual(result["selection_reason"], "need_satisfied_wait")

    def test_trace_does_not_write_learning_or_memory_outputs(self):
        trace = apply_tactile_action(build_initial_state(), "touch_right")["trace"]
        forbidden_keys = {
            "lesson_store_write",
            "memory_layer_write",
            "memory_write",
            "lesson_candidate",
            "llm_prompt",
            "solver",
            "pathfinding",
        }

        self.assertTrue(forbidden_keys.isdisjoint(trace))

    def test_invalid_action_raises_value_error(self):
        with self.assertRaises(ValueError):
            apply_tactile_action(build_initial_state(), "solve")


if __name__ == "__main__":
    unittest.main()
