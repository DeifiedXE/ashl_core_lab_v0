import json
import subprocess
import sys
import unittest

from ashl_core.reward_biased_action_tendency import (
    REWARD_BIAS_KEY,
    run_reward_biased_action_tendency_check,
)
from ashl_core.teaching_cli import run_command


class RewardBiasedActionTendencyTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_reward_biased_action_tendency_check()

        self.assertEqual(result["command"], "run-reward-biased-action-tendency-check")
        self.assertEqual(result["flow"], "reward_biased_action_tendency_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["level_id"], "simulated_vision_larger_sandbox_v0")
        self.assertIn("control_result", result)
        self.assertIn("reward_bias_result", result)
        self.assertIn("reward_store_summary", result)
        self.assertIn("summary", result)

    def test_no_reward_control_does_not_apply_bias(self):
        control = run_reward_biased_action_tendency_check()["control_result"]

        self.assertEqual(control["scenario"], "no_reward_control")
        self.assertEqual(control["front_symbol"], "i")
        self.assertEqual(control["candidate_action"], "move_forward")
        self.assertFalse(control["matching_reward_event_found"])
        self.assertFalse(control["reward_bias_applied"])
        self.assertFalse(control["reward_used_for_decision"])
        self.assertEqual(control["selected_action"], "move_forward")
        self.assertEqual(control["base_action_score"], 1.0)
        self.assertEqual(control["reward_bias_delta"], 0.0)
        self.assertEqual(control["final_action_score"], 1.0)
        self.assertTrue(control["passed"])

    def test_prior_item_reward_applies_immediate_bias(self):
        reward_bias = run_reward_biased_action_tendency_check()["reward_bias_result"]

        self.assertEqual(reward_bias["scenario"], "with_item_reward")
        self.assertEqual(reward_bias["trial1_reward_event"]["reward_type"], "item_contact_reward")
        self.assertEqual(reward_bias["trial1_reward_event"]["front_symbol"], "i")
        self.assertEqual(reward_bias["front_symbol"], "i")
        self.assertEqual(reward_bias["candidate_action"], "move_forward")
        self.assertTrue(reward_bias["matching_reward_event_found"])
        self.assertTrue(reward_bias["reward_bias_applied"])
        self.assertTrue(reward_bias["reward_used_for_decision"])
        self.assertEqual(reward_bias["selected_action"], "move_forward")
        self.assertEqual(reward_bias["base_action_score"], 1.0)
        self.assertGreater(reward_bias["reward_bias_delta"], 0.0)
        self.assertGreater(reward_bias["final_action_score"], reward_bias["base_action_score"])
        self.assertTrue(reward_bias["passed"])

    def test_reward_store_summary_and_summary(self):
        result = run_reward_biased_action_tendency_check()
        store_summary = result["reward_store_summary"]
        summary = result["summary"]

        self.assertEqual(store_summary["reward_event_count"], 1)
        self.assertEqual(store_summary["reward_keys"], [REWARD_BIAS_KEY])
        self.assertTrue(store_summary["item_contact_reward_available"])
        self.assertEqual(store_summary["dopamine_like_signal_count"], 1)
        self.assertEqual(store_summary["total_reward_value"], 1.0)
        self.assertTrue(summary["control_passed"])
        self.assertTrue(summary["reward_bias_passed"])
        self.assertTrue(summary["requires_prior_reward_for_bias"])
        self.assertTrue(summary["all_reward_biased_action_tendency_checks_passed"])

    def test_boundary_check(self):
        boundary = run_reward_biased_action_tendency_check()["boundary_check"]

        self.assertTrue(boundary["reward_biased_action_tendency_enabled"])
        self.assertTrue(boundary["requires_prior_reward_for_bias"])
        self.assertTrue(boundary["no_reward_control_used"])
        self.assertTrue(boundary["item_reward_event_enabled"])
        self.assertTrue(boundary["dopamine_like_signal_enabled"])
        self.assertFalse(boundary["item_seeking_enabled"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["route_planner_added"])
        self.assertFalse(boundary["observed_map_route_use"])
        self.assertFalse(boundary["full_map_visible_to_agent"])
        self.assertTrue(boundary["action_selection_modified_in_this_runner_only"])
        self.assertFalse(boundary["existing_navigation_action_selection_modified"])
        self.assertFalse(boundary["item_collection_enabled"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["pleasure_claimed"])
        self.assertFalse(boundary["desire_claimed"])
        self.assertFalse(boundary["consciousness_claimed"])
        self.assertFalse(boundary["subjective_experience_claimed"])

    def test_run_command_uses_default(self):
        result = run_command("run-reward-biased-action-tendency-check")

        self.assertEqual(result["command"], "run-reward-biased-action-tendency-check")
        self.assertTrue(result["summary"]["all_reward_biased_action_tendency_checks_passed"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-reward-biased-action-tendency-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-reward-biased-action-tendency-check")
        self.assertTrue(result["control_result"]["passed"])
        self.assertTrue(result["reward_bias_result"]["passed"])


if __name__ == "__main__":
    unittest.main()
