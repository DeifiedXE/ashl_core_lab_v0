import json
import subprocess
import sys
import unittest

from ashl_core.grounded_action_experience import run_grounded_action_experience_check
from ashl_core.grounded_action_experience_influence import (
    build_experience_store,
    choose_action_from_experience,
    lookup_grounded_experience,
    run_grounded_action_experience_influence_check,
)
from ashl_core.teaching_cli import (
    run_grounded_action_experience_influence_check as run_cli_helper,
)


class GroundedActionExperienceInfluenceTests(unittest.TestCase):
    def test_build_and_lookup_experience_store(self):
        records = run_grounded_action_experience_check()["experience_records"]
        store = build_experience_store(records)

        experience = lookup_grounded_experience(store, "w", "move_forward")

        self.assertIsNotNone(experience)
        self.assertEqual(experience["outcome_type"], "blocked")
        self.assertEqual(experience["count"], 1)

    def test_choose_action_requires_prior_experience(self):
        choice = choose_action_from_experience("w", "move_forward", {})

        self.assertFalse(choice["matching_experience_found"])
        self.assertFalse(choice["experience_used_for_decision"])
        self.assertEqual(choice["selected_action"], "move_forward")
        self.assertFalse(choice["influence_applied"])

    def test_default_runs_wall_empty_and_item(self):
        result = run_grounded_action_experience_influence_check()
        scenarios = [item["scenario"] for item in result["scenario_results"]]

        self.assertEqual(result["command"], "run-grounded-action-experience-influence-check")
        self.assertEqual(result["flow"], "grounded_action_experience_influence_v0")
        self.assertEqual(scenarios, ["wall", "empty", "item"])
        self.assertTrue(result["summary"]["all_grounded_action_experience_influence_checks_passed"])

    def test_wall_influence_suppresses_move_forward(self):
        result = run_grounded_action_experience_influence_check(scenario="wall")
        scenario = result["scenario_results"][0]

        self.assertEqual(scenario["trial1"]["front_symbol"], "w")
        self.assertEqual(scenario["trial1"]["outcome_type"], "blocked")
        self.assertEqual(scenario["trial1"]["failure_reasons"], ["wall_blocked"])
        self.assertTrue(scenario["matching_experience_found"])
        self.assertTrue(scenario["experience_used_for_decision"])
        self.assertNotEqual(scenario["selected_action"], "move_forward")
        self.assertEqual(scenario["selected_action"], "turn_right")
        self.assertTrue(scenario["influence_applied"])
        self.assertEqual(scenario["influence_type"], "suppress")
        self.assertEqual(scenario["suppressed_action"], "move_forward")
        self.assertTrue(scenario["grounded_experience_influence_match"])

    def test_empty_influence_allows_move_forward(self):
        result = run_grounded_action_experience_influence_check(scenario="empty")
        scenario = result["scenario_results"][0]

        self.assertEqual(scenario["trial1"]["front_symbol"], "e")
        self.assertEqual(scenario["trial1"]["outcome_type"], "moved")
        self.assertTrue(scenario["matching_experience_found"])
        self.assertTrue(scenario["experience_used_for_decision"])
        self.assertEqual(scenario["selected_action"], "move_forward")
        self.assertEqual(scenario["influence_type"], "allow")
        self.assertTrue(scenario["grounded_experience_influence_match"])

    def test_item_influence_allows_contact(self):
        result = run_grounded_action_experience_influence_check(scenario="item")
        scenario = result["scenario_results"][0]

        self.assertEqual(scenario["trial1"]["front_symbol"], "i")
        self.assertEqual(scenario["trial1"]["outcome_type"], "item_contact")
        self.assertTrue(scenario["matching_experience_found"])
        self.assertTrue(scenario["experience_used_for_decision"])
        self.assertEqual(scenario["selected_action"], "move_forward")
        self.assertEqual(scenario["influence_type"], "allow_contact")
        self.assertTrue(scenario["grounded_experience_influence_match"])

    def test_no_experience_wall_control(self):
        control = run_grounded_action_experience_influence_check()["control_results"][0]

        self.assertEqual(control["control_name"], "wall_without_prior_experience")
        self.assertEqual(control["front_symbol"], "w")
        self.assertEqual(control["candidate_action"], "move_forward")
        self.assertFalse(control["matching_experience_found"])
        self.assertEqual(control["selected_action"], "move_forward")
        self.assertFalse(control["experience_used_for_decision"])
        self.assertFalse(control["influence_applied"])
        self.assertTrue(control["passed"])

    def test_experience_store_summary(self):
        summary = run_grounded_action_experience_influence_check()["experience_store_summary"]

        self.assertEqual(summary["experience_count"], 3)
        self.assertTrue(summary["wall_experience_available"])
        self.assertTrue(summary["empty_experience_available"])
        self.assertTrue(summary["item_experience_available"])

    def test_boundary_check(self):
        boundary = run_grounded_action_experience_influence_check()["boundary_check"]

        self.assertIs(boundary["first_person_viewport"], True)
        self.assertEqual(boundary["agent_viewport_position"], [2, 1])
        self.assertEqual(boundary["front_symbol_position"], [1, 1])
        self.assertEqual(boundary["far_front_symbol_position"], [0, 1])
        self.assertIs(boundary["centered_top_down_viewport"], False)
        self.assertIs(boundary["requires_prior_experience_for_influence"], True)
        self.assertIs(boundary["no_experience_control_used"], True)
        self.assertIs(boundary["action_selection_modified_in_this_runner_only"], True)
        self.assertIs(boundary["existing_navigation_action_selection_modified"], False)
        self.assertIs(boundary["pathfinding_used"], False)
        self.assertIs(boundary["llm_vision_used"], False)
        self.assertIs(boundary["long_term_memory_write"], False)
        self.assertIs(boundary["item_seeking_added"], False)
        self.assertIs(boundary["inventory_added"], False)

    def test_invalid_scenario_raises(self):
        with self.assertRaises(ValueError):
            run_grounded_action_experience_influence_check(scenario="water")

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
                "run-grounded-action-experience-influence-check",
                "--scenario",
                "wall",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-grounded-action-experience-influence-check")
        self.assertEqual(result["scenario_results"][0]["scenario"], "wall")
        self.assertTrue(result["control_results"][0]["passed"])


if __name__ == "__main__":
    unittest.main()
