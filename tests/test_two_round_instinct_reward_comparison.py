import json
import subprocess
import sys
import unittest

from ashl_core.two_round_instinct_reward_comparison import run_two_round_instinct_reward_comparison
from ashl_core.teaching_cli import run_command


class TwoRoundInstinctRewardComparisonTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_two_round_instinct_reward_comparison()

        self.assertEqual(result["command"], "run-two-round-instinct-reward-comparison")
        self.assertEqual(result["flow"], "two_round_instinct_reward_comparison_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["level_id"], "simulated_vision_larger_sandbox_v0")
        self.assertEqual(result["seed"], 1)
        self.assertEqual(result["trials"], 20)
        self.assertIn("round1", result)
        self.assertIn("round2", result)
        self.assertIn("comparison", result)
        self.assertIn("boundary_check", result)

    def test_round1_wall_control_uses_no_experience(self):
        wall = run_two_round_instinct_reward_comparison()["round1"]["wall_control"]

        self.assertEqual(wall["front_symbol"], "w")
        self.assertEqual(wall["candidate_action"], "move_forward")
        self.assertEqual(wall["selected_action"], "move_forward")
        self.assertFalse(wall["experience_used_for_decision"])
        self.assertFalse(wall["influence_applied"])

    def test_round2_wall_experience_suppresses_move_forward(self):
        result = run_two_round_instinct_reward_comparison()
        wall = result["round2"]["wall_with_experience"]

        self.assertTrue(wall["carried_wall_experience"])
        self.assertEqual(wall["front_symbol"], "w")
        self.assertEqual(wall["candidate_action"], "move_forward")
        self.assertNotEqual(wall["selected_action"], "move_forward")
        self.assertTrue(wall["experience_used_for_decision"])
        self.assertTrue(wall["influence_applied"])
        self.assertEqual(wall["influence_type"], "suppress")
        self.assertTrue(result["comparison"]["wall_round2_improved"])

    def test_round1_item_control_has_no_reward_bias(self):
        item = run_two_round_instinct_reward_comparison(seed=1, trials=20)["round1"]["item_control"]

        self.assertEqual(item["front_symbol"], "i")
        self.assertEqual(item["candidate_action"], "move_forward")
        self.assertFalse(item["reward_bias_applied"])
        self.assertEqual(item["move_forward_score"], 1.0)
        self.assertEqual(item["move_forward_selected_count"], 7)

    def test_round2_item_reward_bias_improves_immediate_tendency(self):
        result = run_two_round_instinct_reward_comparison(seed=1, trials=20)
        round1_item = result["round1"]["item_control"]
        round2_item = result["round2"]["item_with_reward"]

        self.assertTrue(round2_item["carried_item_reward"])
        self.assertEqual(round2_item["front_symbol"], "i")
        self.assertEqual(round2_item["candidate_action"], "move_forward")
        self.assertTrue(round2_item["reward_bias_applied"])
        self.assertTrue(round2_item["reward_used_for_decision"])
        self.assertEqual(round2_item["reward_bias_delta"], 0.5)
        self.assertGreater(round2_item["move_forward_score"], round1_item["move_forward_score"])
        self.assertGreaterEqual(
            round2_item["move_forward_selected_count"],
            round1_item["move_forward_selected_count"],
        )
        self.assertTrue(result["comparison"]["item_round2_bias_improved"])

    def test_comparison_all_checks_pass(self):
        comparison = run_two_round_instinct_reward_comparison(seed=1, trials=20)["comparison"]

        self.assertTrue(comparison["wall_round2_improved"])
        self.assertTrue(comparison["item_round2_bias_improved"])
        self.assertEqual(comparison["move_forward_score_delta_for_i"], 0.5)
        self.assertEqual(comparison["move_forward_selected_count_delta_for_i"], 1)
        self.assertTrue(comparison["round2_uses_carried_experience"])
        self.assertTrue(comparison["round2_uses_carried_reward"])
        self.assertTrue(comparison["all_two_round_checks_passed"])

    def test_boundary_check(self):
        boundary = run_two_round_instinct_reward_comparison()["boundary_check"]

        self.assertTrue(boundary["two_round_instinct_reward_comparison_enabled"])
        self.assertTrue(boundary["controlled_immediate_tendency_comparison"])
        self.assertTrue(boundary["wall_experience_influence_enabled"])
        self.assertTrue(boundary["item_reward_event_enabled"])
        self.assertTrue(boundary["reward_biased_action_tendency_enabled"])
        self.assertTrue(boundary["reward_biased_random_walk_check_enabled"])
        self.assertTrue(boundary["requires_prior_wall_experience_for_wall_influence"])
        self.assertTrue(boundary["requires_prior_reward_for_item_bias"])
        self.assertTrue(boundary["no_experience_controls_used"])
        self.assertFalse(boundary["whole_map_item_seeking_claimed"])
        self.assertFalse(boundary["whole_map_random_walk_improvement_claimed"])
        self.assertFalse(boundary["item_seeking_enabled"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["route_planner_added"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["pleasure_claimed"])
        self.assertFalse(boundary["desire_claimed"])
        self.assertFalse(boundary["consciousness_claimed"])
        self.assertFalse(boundary["subjective_experience_claimed"])

    def test_invalid_negative_trials_raises(self):
        with self.assertRaises(ValueError):
            run_two_round_instinct_reward_comparison(trials=-1)

    def test_run_command_uses_default(self):
        result = run_command("run-two-round-instinct-reward-comparison")

        self.assertEqual(result["command"], "run-two-round-instinct-reward-comparison")
        self.assertTrue(result["comparison"]["all_two_round_checks_passed"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-two-round-instinct-reward-comparison",
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

        self.assertEqual(result["command"], "run-two-round-instinct-reward-comparison")
        self.assertTrue(result["comparison"]["all_two_round_checks_passed"])
        self.assertFalse(result["boundary_check"]["whole_map_item_seeking_claimed"])


if __name__ == "__main__":
    unittest.main()
