import json
import subprocess
import sys
import unittest

from ashl_core.grounded_action_experience import (
    build_experience_key,
    run_grounded_action_experience_check,
)
from ashl_core.teaching_cli import run_grounded_action_experience_check as run_cli_helper


class GroundedActionExperienceTests(unittest.TestCase):
    def test_experience_key(self):
        self.assertEqual(
            build_experience_key(front_symbol="w", action="move_forward"),
            "front_symbol=w|action=move_forward",
        )

    def test_default_runs_wall_empty_and_item(self):
        result = run_grounded_action_experience_check()
        scenarios = [item["scenario"] for item in result["scenario_results"]]

        self.assertEqual(result["command"], "run-grounded-action-experience-check")
        self.assertEqual(result["flow"], "grounded_action_experience_v0")
        self.assertEqual(scenarios, ["wall", "empty", "item"])
        self.assertEqual(result["experience_summary"]["experience_count"], 3)

    def test_wall_experience_record(self):
        result = run_grounded_action_experience_check(scenario="wall")
        scenario = result["scenario_results"][0]
        record = result["experience_records"][0]

        self.assertEqual(scenario["front_symbol"], "w")
        self.assertEqual(scenario["action"], "move_forward")
        self.assertEqual(scenario["actual_outcome"], "blocked")
        self.assertEqual(scenario["failure_reasons"], ["wall_blocked"])
        self.assertFalse(scenario["position_changed"])
        self.assertTrue(scenario["experience_recorded"])
        self.assertTrue(scenario["grounded_experience_match"])
        self.assertEqual(record["outcome_type"], "blocked")
        self.assertEqual(record["experience_key"], "front_symbol=w|action=move_forward")

    def test_empty_experience_record(self):
        result = run_grounded_action_experience_check(scenario="empty")
        scenario = result["scenario_results"][0]
        record = result["experience_records"][0]

        self.assertEqual(scenario["front_symbol"], "e")
        self.assertEqual(scenario["action"], "move_forward")
        self.assertEqual(scenario["actual_outcome"], "moved")
        self.assertEqual(scenario["failure_reasons"], [])
        self.assertTrue(scenario["position_changed"])
        self.assertTrue(scenario["grounded_experience_match"])
        self.assertEqual(record["outcome_type"], "moved")
        self.assertEqual(record["experience_key"], "front_symbol=e|action=move_forward")

    def test_item_experience_record(self):
        result = run_grounded_action_experience_check(scenario="item")
        scenario = result["scenario_results"][0]
        record = result["experience_records"][0]

        self.assertEqual(scenario["front_symbol"], "i")
        self.assertEqual(scenario["action"], "move_forward")
        self.assertEqual(scenario["actual_outcome"], "item_contact")
        self.assertIn("item_contact", scenario["effect_tags"])
        self.assertTrue(scenario["grounded_experience_match"])
        self.assertEqual(record["outcome_type"], "item_contact")
        self.assertIn("item_contact", record["effect_tags"])
        self.assertEqual(record["experience_key"], "front_symbol=i|action=move_forward")

    def test_experience_records_have_required_fields(self):
        result = run_grounded_action_experience_check()

        for record in result["experience_records"]:
            self.assertIn("tick", record)
            self.assertTrue(record["experience_key"])
            self.assertTrue(record["state_key"])
            self.assertIn("state_snapshot", record)
            self.assertIn("front_symbol", record)
            self.assertIn("action", record)
            self.assertIn("outcome_type", record)
            self.assertIn("failure_reasons", record)
            self.assertIn("metadata", record)
            self.assertEqual(record["metadata"]["front_symbol_source"], "current_viewport[1][1]")
            self.assertIs(record["metadata"]["experience_used_for_decision"], False)

    def test_experience_summary(self):
        summary = run_grounded_action_experience_check()["experience_summary"]

        self.assertEqual(summary["experience_count"], 3)
        self.assertTrue(summary["wall_experience_recorded"])
        self.assertTrue(summary["empty_experience_recorded"])
        self.assertTrue(summary["item_experience_recorded"])
        self.assertTrue(summary["experience_records_have_front_symbol"])
        self.assertTrue(summary["experience_records_have_action"])
        self.assertTrue(summary["experience_records_have_outcome"])
        self.assertTrue(summary["all_grounded_action_experiences_recorded"])

    def test_boundary_check(self):
        boundary = run_grounded_action_experience_check()["boundary_check"]

        self.assertIs(boundary["grounded_action_experience_enabled"], True)
        self.assertIs(boundary["first_person_viewport"], True)
        self.assertEqual(boundary["agent_viewport_position"], [2, 1])
        self.assertEqual(boundary["front_symbol_position"], [1, 1])
        self.assertEqual(boundary["far_front_symbol_position"], [0, 1])
        self.assertIs(boundary["centered_top_down_viewport"], False)
        self.assertIs(boundary["grounded_action_influence_enabled"], False)
        self.assertIs(boundary["action_selection_modified"], False)
        self.assertIs(boundary["experience_used_for_decision"], False)
        self.assertIs(boundary["pathfinding_used"], False)
        self.assertIs(boundary["llm_vision_used"], False)
        self.assertIs(boundary["long_term_memory_write"], False)
        self.assertIs(boundary["item_seeking_added"], False)
        self.assertIs(boundary["item_pickup_added"], False)
        self.assertIs(boundary["inventory_added"], False)

    def test_invalid_scenario_raises(self):
        with self.assertRaises(ValueError):
            run_grounded_action_experience_check(scenario="water")

    def test_cli_helper_accepts_scenario(self):
        result = run_cli_helper(scenario="wall")

        self.assertEqual(len(result["scenario_results"]), 1)
        self.assertEqual(result["scenario_results"][0]["scenario"], "wall")

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-grounded-action-experience-check",
                "--scenario",
                "item",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-grounded-action-experience-check")
        self.assertEqual(result["scenario_results"][0]["scenario"], "item")
        self.assertEqual(result["experience_records"][0]["front_symbol"], "i")


if __name__ == "__main__":
    unittest.main()
