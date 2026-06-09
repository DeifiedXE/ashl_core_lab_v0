import json
import subprocess
import sys
import unittest

from ashl_core.item_reward_event import run_item_reward_event_check
from ashl_core.teaching_cli import run_command


class ItemRewardEventTests(unittest.TestCase):
    def test_default_check_shape(self):
        result = run_item_reward_event_check()

        self.assertEqual(result["command"], "run-item-reward-event-check")
        self.assertEqual(result["flow"], "item_reward_event_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["level_id"], "simulated_vision_larger_sandbox_v0")
        self.assertIn("scenario_result", result)
        self.assertIn("reward_event", result)
        self.assertIn("reward_summary", result)
        self.assertIn("boundary_check", result)

    def test_item_contact_scenario(self):
        scenario = run_item_reward_event_check()["scenario_result"]

        self.assertEqual(scenario["scenario"], "item_contact_reward")
        self.assertEqual(scenario["front_symbol"], "i")
        self.assertEqual(scenario["action"], "move_forward")
        self.assertEqual(scenario["actual_outcome"], "item_contact")
        self.assertEqual(scenario["failure_reasons"], [])
        self.assertIn("item_contact", scenario["effect_tags"])
        self.assertTrue(scenario["position_changed"])

    def test_reward_event_shape(self):
        result = run_item_reward_event_check()
        scenario = result["scenario_result"]
        event = result["reward_event"]

        self.assertEqual(event["event_id"], "item_reward:simulated_vision_larger_sandbox_v0:1:8_1")
        self.assertEqual(event["tick"], 1)
        self.assertEqual(event["level_id"], result["level_id"])
        self.assertEqual(event["source"], "grounded_action_experience")
        self.assertEqual(event["trigger"], "item_contact")
        self.assertEqual(event["front_symbol"], "i")
        self.assertEqual(event["action"], "move_forward")
        self.assertEqual(event["outcome_type"], "item_contact")
        self.assertIn("item_contact", event["effect_tags"])
        self.assertEqual(event["reward_type"], "item_contact_reward")
        self.assertEqual(event["reward_value"], 1.0)
        self.assertTrue(event["dopamine_like_signal"])
        self.assertTrue(event["non_subjective"])
        self.assertEqual(event["metadata"]["position_before"], scenario["position_before"])
        self.assertEqual(event["metadata"]["position_after"], scenario["position_after"])
        self.assertEqual(event["metadata"]["facing"], scenario["initial_facing"])
        self.assertEqual(event["metadata"]["viewport"], scenario["current_viewport"])

    def test_reward_summary(self):
        summary = run_item_reward_event_check()["reward_summary"]

        self.assertTrue(summary["reward_event_created"])
        self.assertEqual(summary["reward_event_count"], 1)
        self.assertEqual(summary["item_contact_reward_count"], 1)
        self.assertEqual(summary["dopamine_like_signal_count"], 1)
        self.assertEqual(summary["total_reward_value"], 1.0)
        self.assertEqual(summary["non_subjective_reward_events"], 1)

    def test_boundary_check(self):
        boundary = run_item_reward_event_check()["boundary_check"]

        self.assertTrue(boundary["item_reward_event_enabled"])
        self.assertTrue(boundary["dopamine_like_signal_enabled"])
        self.assertFalse(boundary["reward_bias_enabled"])
        self.assertFalse(boundary["item_seeking_enabled"])
        self.assertFalse(boundary["reward_used_for_action_selection"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["route_planner_added"])
        self.assertFalse(boundary["item_collection_enabled"])
        self.assertFalse(boundary["item_pickup_enabled"])
        self.assertFalse(boundary["inventory_enabled"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["pleasure_claimed"])
        self.assertFalse(boundary["desire_claimed"])
        self.assertFalse(boundary["self_awareness_claimed"])
        self.assertFalse(boundary["consciousness_claimed"])
        self.assertFalse(boundary["subjective_experience_claimed"])

    def test_run_command_uses_default(self):
        result = run_command("run-item-reward-event-check")

        self.assertEqual(result["command"], "run-item-reward-event-check")
        self.assertEqual(result["scenario_result"]["front_symbol"], "i")
        self.assertTrue(result["reward_summary"]["reward_event_created"])

    def test_invalid_scenario_raises(self):
        with self.assertRaises(ValueError):
            run_item_reward_event_check(scenario="wall")

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-item-reward-event-check",
                "--scenario",
                "item",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-item-reward-event-check")
        self.assertEqual(result["scenario_result"]["actual_outcome"], "item_contact")
        self.assertEqual(result["reward_event"]["reward_type"], "item_contact_reward")


if __name__ == "__main__":
    unittest.main()
