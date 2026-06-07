import copy
import unittest

from ashl_core.micro_push_box_sandbox import (
    build_initial_state,
    select_intrinsic_action,
)


class IntrinsicActionSelectionTests(unittest.TestCase):
    def test_select_only_returns_action_from_candidate_actions(self):
        state = build_initial_state()

        selected = select_intrinsic_action(state, ["push_right", "wait"], random_seed=7)

        self.assertIn(selected, ["push_right", "wait"])

    def test_invalid_candidate_action_raises_value_error(self):
        with self.assertRaises(ValueError):
            select_intrinsic_action(build_initial_state(), ["push_right", "push right"], random_seed=1)

    def test_empty_candidate_actions_raises_value_error(self):
        with self.assertRaises(ValueError):
            select_intrinsic_action(build_initial_state(), [], random_seed=1)

    def test_same_random_seed_returns_same_result_for_tied_candidates(self):
        state = build_initial_state()
        candidates = ["push_right", "push_down", "wait"]

        first = select_intrinsic_action(state, candidates, random_seed=42)
        second = select_intrinsic_action(state, candidates, random_seed=42)

        self.assertEqual(first, second)
        self.assertIn(first, candidates)

    def test_different_seed_can_vary_among_tied_candidates(self):
        state = build_initial_state()
        candidates = ["push_right", "push_down", "wait"]

        selected = {
            select_intrinsic_action(state, candidates, random_seed=seed)
            for seed in range(20)
        }

        self.assertGreater(len(selected), 1)
        self.assertTrue(selected.issubset(set(candidates)))

    def test_higher_weighted_action_wins_over_lower_weighted_action(self):
        state = build_initial_state()
        state["action_history"] = (
            {"action": "push_right", "result": "box_blocked", "tick": 1},
            {"action": "push_down", "result": "box_pushed", "tick": 2},
        )

        selected = select_intrinsic_action(state, ["push_right", "push_down"], random_seed=99)

        self.assertEqual(selected, "push_down")

    def test_empty_history_does_not_crash(self):
        selected = select_intrinsic_action(build_initial_state(), ["push_right", "push_down"], random_seed=3)

        self.assertIn(selected, ["push_right", "push_down"])

    def test_helper_does_not_modify_state(self):
        state = build_initial_state()
        state["action_history"] = (
            {"action": "push_right", "result": "box_blocked", "tick": 1},
            {"action": "push_down", "result": "box_pushed", "tick": 2},
        )
        before = copy.deepcopy(state)

        select_intrinsic_action(state, ["push_right", "push_down"], random_seed=11)

        self.assertEqual(state, before)


if __name__ == "__main__":
    unittest.main()
