import json
import subprocess
import sys
import unittest

from ashl_core.simulated_vision_larger_sandbox_observed_map import (
    run_larger_sandbox_observed_map_smoke,
)
from ashl_core.teaching_cli import run_larger_sandbox_observed_map_smoke as run_cli_helper


class LargerSandboxObservedMapSmokeTests(unittest.TestCase):
    def test_smoke_runs_required_scenarios(self):
        result = run_larger_sandbox_observed_map_smoke()
        scenarios = {item["scenario"]: item for item in result["scenario_results"]}

        self.assertEqual(result["command"], "run-larger-sandbox-observed-map-smoke")
        self.assertEqual(result["flow"], "larger_sandbox_observed_map_smoke_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(set(scenarios), {"doorway_d", "item_i", "exit_g"})
        self.assertTrue(scenarios["doorway_d"]["passed"])
        self.assertTrue(scenarios["item_i"]["passed"])
        self.assertTrue(scenarios["exit_g"]["passed"])

    def test_map_summary(self):
        summary = run_larger_sandbox_observed_map_smoke()["map_summary"]

        self.assertEqual(summary["width"], 12)
        self.assertEqual(summary["height"], 9)
        self.assertEqual(summary["item_count"], 4)
        self.assertEqual(summary["doorway_count"], 2)
        self.assertEqual(summary["exit_count"], 1)

    def test_observed_map_records_d_i_g(self):
        summary = run_larger_sandbox_observed_map_smoke()["observed_map_summary"]

        self.assertIn("d", summary["remembered_symbols"])
        self.assertIn("i", summary["remembered_symbols"])
        self.assertIn("g", summary["remembered_symbols"])
        self.assertGreaterEqual(summary["remembered_d_count"], 1)
        self.assertGreaterEqual(summary["remembered_i_count"], 1)
        self.assertGreaterEqual(summary["remembered_g_count"], 1)

    def test_x_does_not_erase_d_i_g_after_view_changes(self):
        result = run_larger_sandbox_observed_map_smoke()

        for check in result["persistence_checks"]:
            self.assertEqual(check["current_visibility"], "not_in_current_viewport")
            self.assertEqual(check["previously_observed_symbol"], check["symbol"])
            self.assertEqual(check["still_remembered_symbol"], check["symbol"])
            self.assertTrue(check["passed"])
        self.assertTrue(result["observed_map_summary"]["x_does_not_erase_known_cells"])

    def test_unseen_cells_are_not_inferred(self):
        result = run_larger_sandbox_observed_map_smoke()
        known_cell_count = result["observed_map_summary"]["known_cell_count"]
        total_map_cells = result["map_summary"]["width"] * result["map_summary"]["height"]

        self.assertLess(known_cell_count, total_map_cells)
        self.assertTrue(result["observed_map_summary"]["unseen_cells_not_inferred"])

    def test_first_person_viewport_convention(self):
        scenario = run_larger_sandbox_observed_map_smoke()["scenario_results"][0]
        viewport = scenario["current_viewport"]

        self.assertEqual(viewport[2][1], "a")
        self.assertNotEqual(viewport[1][1], "a")

    def test_boundary_check(self):
        boundary = run_larger_sandbox_observed_map_smoke()["boundary_check"]

        self.assertIs(boundary["larger_static_sandbox_used"], True)
        self.assertIs(boundary["observed_local_map_enabled"], True)
        self.assertIs(boundary["doorway_remembered"], True)
        self.assertIs(boundary["item_remembered"], True)
        self.assertIs(boundary["exit_remembered"], True)
        self.assertIs(boundary["pathfinding_used"], False)
        self.assertIs(boundary["route_planner_added"], False)
        self.assertIs(boundary["item_collection_enabled"], False)
        self.assertIs(boundary["exit_conditional_spawn_enabled"], False)
        self.assertIs(boundary["curiosity_enabled"], False)
        self.assertIs(boundary["prediction_error_enabled"], False)
        self.assertIs(boundary["place_memory_enabled"], False)
        self.assertIs(boundary["long_term_memory_write"], False)

    def test_cli_helper_accepts_action_sequence(self):
        result = run_cli_helper(action_sequence=["look", "turn_right"])

        self.assertEqual(result["command"], "run-larger-sandbox-observed-map-smoke")
        self.assertEqual(len(result["scenario_results"]), 3)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-larger-sandbox-observed-map-smoke",
                "--action-sequence",
                "look,turn_right",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-larger-sandbox-observed-map-smoke")
        self.assertTrue(result["boundary_check"]["observed_local_map_enabled"])


if __name__ == "__main__":
    unittest.main()
