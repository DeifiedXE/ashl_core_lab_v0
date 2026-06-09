import json
import subprocess
import sys
import unittest

from ashl_core.simulated_vision_sandbox import create_simulated_vision_room, render_viewport
from ashl_core.simulated_vision_symbol_grounding import (
    build_symbol_grounding_scenarios,
    get_front_symbol_from_viewport,
    run_symbol_grounding_check,
)
from ashl_core.teaching_cli import run_symbol_grounding_check as run_cli_helper


class SimulatedVisionSymbolGroundingTests(unittest.TestCase):
    def test_front_symbol_uses_front_center_cell(self):
        viewport = [["w", "i", "e"], ["e", "a", "e"], ["e", "e", "e"]]

        self.assertEqual(get_front_symbol_from_viewport(viewport), "i")

    def test_scenarios_have_expected_front_symbols(self):
        level = create_simulated_vision_room()
        scenarios = build_symbol_grounding_scenarios(level)

        self.assertEqual(get_front_symbol_from_viewport(render_viewport(scenarios["wall"]["state"], level)), "w")
        self.assertEqual(get_front_symbol_from_viewport(render_viewport(scenarios["empty"]["state"], level)), "e")
        self.assertEqual(get_front_symbol_from_viewport(render_viewport(scenarios["item"]["state"], level)), "i")

    def test_default_runs_all_scenarios(self):
        result = run_symbol_grounding_check()
        scenario_names = [scenario["scenario"] for scenario in result["scenario_results"]]

        self.assertEqual(result["command"], "run-simulated-vision-symbol-grounding-check")
        self.assertEqual(result["flow"], "simulated_vision_symbol_grounding_check_v0")
        self.assertEqual(scenario_names, ["wall", "empty", "item"])
        self.assertEqual(result["summary"]["scenario_count"], 3)
        self.assertTrue(result["summary"]["all_grounding_checks_passed"])

    def test_wall_scenario_grounding(self):
        result = run_symbol_grounding_check(scenario="wall")
        scenario = result["scenario_results"][0]

        self.assertEqual(scenario["front_symbol"], "w")
        self.assertEqual(scenario["actual_outcome"], "blocked")
        self.assertEqual(scenario["failure_reasons"], ["wall_blocked"])
        self.assertFalse(scenario["position_changed"])
        self.assertTrue(scenario["grounding_match"])

    def test_empty_scenario_grounding(self):
        result = run_symbol_grounding_check(scenario="empty")
        scenario = result["scenario_results"][0]

        self.assertEqual(scenario["front_symbol"], "e")
        self.assertEqual(scenario["actual_outcome"], "moved")
        self.assertEqual(scenario["failure_reasons"], [])
        self.assertTrue(scenario["position_changed"])
        self.assertTrue(scenario["grounding_match"])

    def test_item_scenario_grounding(self):
        result = run_symbol_grounding_check(scenario="item")
        scenario = result["scenario_results"][0]

        self.assertEqual(scenario["front_symbol"], "i")
        self.assertEqual(scenario["actual_outcome"], "item_contact")
        self.assertTrue(scenario["position_changed"])
        self.assertTrue(scenario["item_grounding_match"])
        self.assertEqual(scenario["effect_tags"], ["item_contact"])

    def test_summary(self):
        summary = run_symbol_grounding_check()["summary"]

        self.assertEqual(summary["passed_count"], 3)
        self.assertEqual(summary["failed_count"], 0)
        self.assertTrue(summary["wall_grounding_passed"])
        self.assertTrue(summary["empty_grounding_passed"])
        self.assertTrue(summary["item_grounding_passed"])

    def test_boundary_check(self):
        boundary = run_symbol_grounding_check()["boundary_check"]

        self.assertIs(boundary["symbol_grounding_check_enabled"], True)
        self.assertIs(boundary["symbol_grounding_solved_claimed"], False)
        self.assertIs(boundary["visual_understanding_claimed"], False)
        self.assertIs(boundary["pathfinding_used"], False)
        self.assertIs(boundary["llm_vision_used"], False)
        self.assertIs(boundary["action_selection_modified"], False)
        self.assertIs(boundary["item_seeking_added"], False)
        self.assertIs(boundary["inventory_added"], False)

    def test_invalid_scenario_raises(self):
        with self.assertRaises(ValueError):
            run_symbol_grounding_check(scenario="water")

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
                "run-simulated-vision-symbol-grounding-check",
                "--scenario",
                "item",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-simulated-vision-symbol-grounding-check")
        self.assertEqual(result["scenario_results"][0]["scenario"], "item")
        self.assertTrue(result["summary"]["all_grounding_checks_passed"])


if __name__ == "__main__":
    unittest.main()
