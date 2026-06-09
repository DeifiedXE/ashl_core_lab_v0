import json
import subprocess
import sys
import unittest

from ashl_core.simulated_vision_larger_sandbox_contact import run_larger_sandbox_symbol_contact_smoke
from ashl_core.teaching_cli import run_larger_sandbox_symbol_contact_smoke as run_cli_helper


class LargerSandboxSymbolContactSmokeTests(unittest.TestCase):
    def test_default_runs_all_scenarios(self):
        result = run_larger_sandbox_symbol_contact_smoke()
        scenarios = [item["scenario"] for item in result["scenario_results"]]

        self.assertEqual(result["command"], "run-larger-sandbox-symbol-contact-smoke")
        self.assertEqual(result["flow"], "larger_sandbox_symbol_contact_smoke_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(scenarios, ["doorway_d", "item_i", "exit_g"])
        self.assertTrue(result["summary"]["all_larger_sandbox_symbol_contact_checks_passed"])

    def test_doorway_contact(self):
        result = run_larger_sandbox_symbol_contact_smoke(scenario="doorway")
        scenario = result["scenario_results"][0]

        self.assertEqual(scenario["front_symbol"], "d")
        self.assertEqual(scenario["actual_outcome"], "moved")
        self.assertEqual(scenario["failure_reasons"], [])
        self.assertIn("passage_crossed", scenario["effect_tags"])
        self.assertTrue(scenario["position_changed"])
        self.assertTrue(scenario["contact_match"])

    def test_item_contact(self):
        result = run_larger_sandbox_symbol_contact_smoke(scenario="item")
        scenario = result["scenario_results"][0]

        self.assertEqual(scenario["front_symbol"], "i")
        self.assertEqual(scenario["actual_outcome"], "item_contact")
        self.assertEqual(scenario["failure_reasons"], [])
        self.assertIn("item_contact", scenario["effect_tags"])
        self.assertTrue(scenario["contact_match"])
        self.assertFalse(result["boundary_check"]["item_collection_enabled"])

    def test_exit_contact(self):
        result = run_larger_sandbox_symbol_contact_smoke(scenario="exit")
        scenario = result["scenario_results"][0]

        self.assertEqual(scenario["front_symbol"], "g")
        self.assertEqual(scenario["actual_outcome"], "exit_contact")
        self.assertEqual(scenario["failure_reasons"], [])
        self.assertIn("exit_contact", scenario["effect_tags"])
        self.assertTrue(scenario["contact_match"])
        self.assertFalse(result["boundary_check"]["exit_conditional_spawn_enabled"])

    def test_summary(self):
        summary = run_larger_sandbox_symbol_contact_smoke()["summary"]

        self.assertEqual(summary["scenario_count"], 3)
        self.assertEqual(summary["passed_count"], 3)
        self.assertEqual(summary["failed_count"], 0)
        self.assertTrue(summary["doorway_contact_passed"])
        self.assertTrue(summary["item_contact_passed"])
        self.assertTrue(summary["exit_contact_passed"])

    def test_boundary_check(self):
        boundary = run_larger_sandbox_symbol_contact_smoke()["boundary_check"]

        self.assertTrue(boundary["symbol_contact_smoke_enabled"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["route_planner_added"])
        self.assertFalse(boundary["item_collection_enabled"])
        self.assertFalse(boundary["item_pickup_enabled"])
        self.assertFalse(boundary["inventory_enabled"])
        self.assertFalse(boundary["exit_conditional_spawn_enabled"])
        self.assertFalse(boundary["task_completion_enabled"])
        self.assertFalse(boundary["win_condition_enabled"])
        self.assertFalse(boundary["curiosity_enabled"])
        self.assertFalse(boundary["prediction_error_enabled"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["doorway_semantic_boundary_given_to_agent"])

    def test_invalid_scenario_raises(self):
        with self.assertRaises(ValueError):
            run_larger_sandbox_symbol_contact_smoke(scenario="water")

    def test_cli_helper_accepts_scenario(self):
        result = run_cli_helper(scenario="doorway")

        self.assertEqual(len(result["scenario_results"]), 1)
        self.assertEqual(result["scenario_results"][0]["scenario"], "doorway_d")

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-larger-sandbox-symbol-contact-smoke",
                "--scenario",
                "exit",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-larger-sandbox-symbol-contact-smoke")
        self.assertEqual(result["scenario_results"][0]["front_symbol"], "g")
        self.assertTrue(result["summary"]["all_larger_sandbox_symbol_contact_checks_passed"])


if __name__ == "__main__":
    unittest.main()
