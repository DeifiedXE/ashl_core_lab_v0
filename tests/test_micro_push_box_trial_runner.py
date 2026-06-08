import unittest

from ashl_core.micro_push_box_trial_runner import (
    _select_action_for_trial,
    run_need_state_driven_trial,
    run_need_state_driven_trial_batch,
)
from ashl_core.micro_push_box_sandbox import (
    build_initial_state,
    build_state_action_key,
    score_action_from_state_action_memory,
)


class MicroPushBoxTrialRunnerTests(unittest.TestCase):
    def test_trial_returns_steps_and_summary(self):
        result = run_need_state_driven_trial(["move_up", "move_right", "push_down"], max_steps=3, random_seed=0)

        self.assertIn("steps", result)
        self.assertLessEqual(result["step_count"], 3)
        self.assertIsInstance(result["completed_goal"], bool)
        self.assertIn("final_need_state", result)
        self.assertIn("final_result", result)

    def test_reachable_candidate_actions_can_complete_goal(self):
        result = run_need_state_driven_trial(["move_up", "move_right", "push_down"], max_steps=10, random_seed=0)

        self.assertTrue(result["completed_goal"])
        self.assertEqual(result["stop_reason"], "need_satisfied")
        self.assertEqual(result["final_need_state"]["current_value"], 1)
        self.assertTrue(result["final_need_state"]["satisfied"])
        self.assertEqual(result["final_result"], "goal_reached")
        self.assertLessEqual(result["step_count"], 10)

    def test_blocked_candidates_stop_at_max_steps(self):
        result = run_need_state_driven_trial(["push_right", "wait"], max_steps=3, random_seed=0)

        self.assertFalse(result["completed_goal"])
        self.assertEqual(result["stop_reason"], "max_steps_reached")
        self.assertEqual(result["step_count"], 3)
        self.assertEqual(result["final_need_state"]["current_value"], 0)
        self.assertFalse(result["final_need_state"]["satisfied"])

    def test_each_selected_action_is_from_candidates_or_wait(self):
        candidates = ["move_up", "move_right", "push_down"]
        result = run_need_state_driven_trial(candidates, max_steps=10, random_seed=0)

        for step in result["steps"]:
            self.assertIn(step["selected_action"], candidates + ["wait"])

    def test_step_shape_contains_selection_and_trace_fields(self):
        result = run_need_state_driven_trial(["move_up", "move_right", "push_down"], max_steps=1, random_seed=0)
        step = result["steps"][0]

        self.assertEqual(
            set(step),
            {
                "step_index",
                "selected_action",
                "selection_reason",
                "selection_source",
                "state_action_memory_used",
                "tactile_result",
                "need_state",
                "agent_pos",
                "box_pos",
                "trace",
            },
        )

    def test_trial_steps_record_state_action_memory_selection_source(self):
        result = run_need_state_driven_trial(["move_up", "move_right", "push_down"], max_steps=10, random_seed=0)

        self.assertTrue(result["steps"])
        self.assertTrue(
            all(
                step["selection_source"] == "state_action_memory_plus_outcome_weight_plus_goal_bias"
                for step in result["steps"]
            )
        )
        self.assertTrue(all(step["state_action_memory_used"] is True for step in result["steps"]))

    def test_goal_bias_favors_goal_improving_push_when_available(self):
        result = run_need_state_driven_trial(["move_up", "move_right", "push_down"], max_steps=10, random_seed=0)

        self.assertTrue(result["completed_goal"])
        self.assertEqual(result["steps"][-1]["selected_action"], "push_down")
        self.assertEqual(
            result["steps"][-1]["selection_source"],
            "state_action_memory_plus_outcome_weight_plus_goal_bias",
        )

    def test_state_action_memory_can_affect_trial_candidate_ordering(self):
        state = build_initial_state()
        state["agent_pos"] = (1, 3)
        state["box_pos"] = (2, 3)
        state["goal_pos"] = (3, 3)
        push_right_key = build_state_action_key(state, "push_right")
        push_down_key = build_state_action_key(state, "push_down")
        state["action_history"] = (
            {**push_right_key, "result": "box_blocked", "tick": 1},
            {**push_down_key, "result": "box_pushed", "tick": 2},
        )

        selection = _select_action_for_trial(state, ["push_right", "push_down"], random_seed=0)
        different_context = dict(state)
        different_context["agent_pos"] = (1, 2)

        self.assertEqual(selection["selected_action"], "push_down")
        self.assertEqual(selection["selection_source"], "state_action_memory_plus_outcome_weight_plus_goal_bias")
        self.assertTrue(selection["state_action_memory_used"])
        self.assertEqual(score_action_from_state_action_memory(different_context, "push_down"), 0)

    def test_invalid_candidate_action_raises_value_error(self):
        with self.assertRaises(ValueError):
            run_need_state_driven_trial(["push right"], max_steps=1, random_seed=0)

    def test_trial_does_not_write_learning_or_memory_outputs(self):
        result = run_need_state_driven_trial(["move_up", "move_right", "push_down"], max_steps=2, random_seed=0)
        forbidden_keys = {
            "lesson_store_write",
            "memory_layer_write",
            "memory_write",
            "lesson_candidate",
            "solver",
            "pathfinding",
            "llm_prompt",
        }

        self.assertTrue(forbidden_keys.isdisjoint(result))
        for step in result["steps"]:
            self.assertTrue(forbidden_keys.isdisjoint(step))
            self.assertTrue(forbidden_keys.isdisjoint(step["trace"]))

    def test_trial_batch_defaults_to_five_trials(self):
        result = run_need_state_driven_trial_batch(random_seed=0)

        self.assertEqual(result["trial_count"], 5)
        self.assertEqual(len(result["trials"]), 5)
        self.assertEqual(len(result["step_counts"]), 5)
        self.assertIn("average_step_count", result)
        self.assertIn("min_step_count", result)
        self.assertIn("max_step_count", result)

    def test_trial_batch_records_trial_summaries(self):
        result = run_need_state_driven_trial_batch(
            trial_count=5,
            candidate_actions=["move_up", "move_right", "push_down"],
            max_steps=10,
            random_seed=0,
        )

        for index, trial in enumerate(result["trials"]):
            self.assertEqual(trial["trial_index"], index)
            self.assertIn("completed_goal", trial)
            self.assertIn("stop_reason", trial)
            self.assertIn("step_count", trial)
            self.assertIn("final_need_state", trial)
            self.assertIn("selected_actions", trial)
            self.assertIsInstance(trial["selected_actions"], list)

    def test_trial_batch_reproducible_with_same_seed(self):
        first = run_need_state_driven_trial_batch(random_seed=13)
        second = run_need_state_driven_trial_batch(random_seed=13)

        self.assertEqual(first, second)

    def test_trial_batch_supports_blocked_max_steps_case(self):
        result = run_need_state_driven_trial_batch(
            trial_count=5,
            candidate_actions=["push_right", "wait"],
            max_steps=3,
            random_seed=0,
        )

        self.assertEqual(result["trial_count"], 5)
        self.assertEqual(result["completed_count"], 0)
        self.assertEqual(result["step_counts"], [3, 3, 3, 3, 3])
        self.assertEqual(result["average_step_count"], 3)
        self.assertEqual(result["min_step_count"], 3)
        self.assertEqual(result["max_step_count"], 3)

    def test_trial_batch_does_not_write_learning_or_memory_outputs(self):
        result = run_need_state_driven_trial_batch(random_seed=0)
        forbidden_keys = {
            "lesson_store_write",
            "memory_layer_write",
            "memory_write",
            "lesson_candidate",
            "solver",
            "pathfinding",
            "llm_prompt",
        }

        self.assertTrue(forbidden_keys.isdisjoint(result))
        for trial in result["trials"]:
            self.assertTrue(forbidden_keys.isdisjoint(trial))


if __name__ == "__main__":
    unittest.main()
