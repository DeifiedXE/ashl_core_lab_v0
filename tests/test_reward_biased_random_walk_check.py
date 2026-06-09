import json
import subprocess
import sys
import unittest

from ashl_core.reward_biased_action_tendency import BASE_ACTION_SCORE, ITEM_REWARD_BIAS_DELTA
from ashl_core.reward_biased_random_walk_check import (
    ACTION_ORDER,
    run_reward_biased_random_walk_check,
    sample_actions_from_scores,
    score_actions_for_front_symbol,
)
from ashl_core.teaching_cli import run_command


class RewardBiasedRandomWalkCheckTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_reward_biased_random_walk_check()

        self.assertEqual(result["command"], "run-reward-biased-random-walk-check")
        self.assertEqual(result["flow"], "reward_biased_random_walk_check_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["level_id"], "simulated_vision_larger_sandbox_v0")
        self.assertEqual(result["seed"], 1)
        self.assertEqual(result["trials"], 20)
        self.assertIn("no_reward_result", result)
        self.assertIn("with_reward_result", result)
        self.assertIn("comparison", result)
        self.assertIn("boundary_check", result)

    def test_no_reward_control_does_not_apply_bias(self):
        result = run_reward_biased_random_walk_check(seed=1, trials=20)
        no_reward = result["no_reward_result"]

        self.assertEqual(no_reward["front_symbol"], "i")
        self.assertTrue(no_reward["reward_store_empty"])
        self.assertFalse(no_reward["reward_bias_applied"])
        self.assertEqual(no_reward["move_forward_score"], BASE_ACTION_SCORE)
        self.assertEqual(no_reward["action_scores"]["move_forward"], BASE_ACTION_SCORE)
        self.assertEqual(sum(no_reward["selected_action_counts"].values()), 20)
        self.assertEqual(no_reward["move_forward_selected_count"], no_reward["selected_action_counts"]["move_forward"])

    def test_with_reward_applies_bias_and_increases_score(self):
        result = run_reward_biased_random_walk_check(seed=1, trials=20)
        no_reward = result["no_reward_result"]
        with_reward = result["with_reward_result"]

        self.assertEqual(with_reward["front_symbol"], "i")
        self.assertEqual(with_reward["reward_event_count"], 1)
        self.assertTrue(with_reward["matching_reward_event_found"])
        self.assertTrue(with_reward["reward_bias_applied"])
        self.assertEqual(with_reward["reward_bias_delta"], ITEM_REWARD_BIAS_DELTA)
        self.assertGreater(with_reward["move_forward_score"], no_reward["move_forward_score"])
        self.assertGreaterEqual(with_reward["move_forward_selected_count"], no_reward["move_forward_selected_count"])

    def test_comparison_reports_observed_local_effect(self):
        comparison = run_reward_biased_random_walk_check(seed=1, trials=20)["comparison"]

        self.assertEqual(comparison["move_forward_score_delta"], ITEM_REWARD_BIAS_DELTA)
        self.assertGreaterEqual(comparison["move_forward_selected_count_delta"], 0)
        self.assertTrue(comparison["with_reward_score_higher"])
        self.assertTrue(comparison["with_reward_selection_not_lower"])
        self.assertTrue(comparison["reward_bias_effect_observed"])

    def test_sampling_is_deterministic_for_same_seed(self):
        result_a = run_reward_biased_random_walk_check(seed=7, trials=30)
        result_b = run_reward_biased_random_walk_check(seed=7, trials=30)

        self.assertEqual(result_a["no_reward_result"]["selected_actions"], result_b["no_reward_result"]["selected_actions"])
        self.assertEqual(result_a["with_reward_result"]["selected_actions"], result_b["with_reward_result"]["selected_actions"])
        self.assertEqual(
            result_a["with_reward_result"]["selected_action_counts"],
            result_b["with_reward_result"]["selected_action_counts"],
        )

    def test_helpers_score_and_sample_actions(self):
        scored = score_actions_for_front_symbol("i", {})
        sampled = sample_actions_from_scores(scored["action_scores"], seed=1, trials=4)

        self.assertEqual(tuple(sampled["selected_action_counts"].keys()), ACTION_ORDER)
        self.assertFalse(scored["reward_bias_applied"])
        self.assertEqual(sum(sampled["selected_action_counts"].values()), 4)

    def test_boundary_check(self):
        boundary = run_reward_biased_random_walk_check()["boundary_check"]

        self.assertTrue(boundary["reward_biased_random_walk_check_enabled"])
        self.assertTrue(boundary["controlled_front_symbol_item_scenario"])
        self.assertTrue(boundary["item_reward_event_enabled"])
        self.assertTrue(boundary["reward_biased_action_tendency_enabled"])
        self.assertTrue(boundary["requires_prior_reward_for_bias"])
        self.assertTrue(boundary["no_reward_control_used"])
        self.assertFalse(boundary["whole_map_random_walk_improvement_claimed"])
        self.assertFalse(boundary["item_seeking_enabled"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["route_planner_added"])
        self.assertFalse(boundary["observed_map_route_use"])
        self.assertFalse(boundary["random_walk_base_behavior_modified"])
        self.assertTrue(boundary["action_selection_modified_in_this_check_only"])
        self.assertFalse(boundary["existing_navigation_action_selection_modified"])
        self.assertFalse(boundary["item_collection_enabled"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["pleasure_claimed"])
        self.assertFalse(boundary["desire_claimed"])
        self.assertFalse(boundary["consciousness_claimed"])
        self.assertFalse(boundary["subjective_experience_claimed"])

    def test_invalid_negative_trials_raises(self):
        with self.assertRaises(ValueError):
            run_reward_biased_random_walk_check(trials=-1)

    def test_run_command_uses_default(self):
        result = run_command("run-reward-biased-random-walk-check")

        self.assertEqual(result["command"], "run-reward-biased-random-walk-check")
        self.assertTrue(result["comparison"]["reward_bias_effect_observed"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-reward-biased-random-walk-check",
                "--seed",
                "1",
                "--trials",
                "20",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-reward-biased-random-walk-check")
        self.assertTrue(result["comparison"]["reward_bias_effect_observed"])
        self.assertFalse(result["boundary_check"]["whole_map_random_walk_improvement_claimed"])


if __name__ == "__main__":
    unittest.main()
