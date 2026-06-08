import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import validate_dead_end_trial1_maps_cli


class DeadEndMapTrial1ValidationTests(unittest.TestCase):
    def test_validation_handler_returns_required_sections(self):
        result = validate_dead_end_trial1_maps_cli(runs_per_map=3, max_steps=100)

        self.assertEqual(result["command"], "validate-dead-end-trial1-maps")
        self.assertEqual(result["flow"], "dead_end_map_trial1_validation_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["runs_per_map"], 3)
        self.assertEqual(result["max_steps"], 100)
        self.assertIn("map_results", result)
        self.assertIn("overall_summary", result)
        self.assertIn("boundary_check", result)

    def test_validation_reports_four_maps_with_required_fields(self):
        result = validate_dead_end_trial1_maps_cli(runs_per_map=2, max_steps=100)
        map_results = result["map_results"]

        self.assertEqual(len(map_results), 4)
        for map_result in map_results:
            self.assertIn("level_id", map_result)
            self.assertIn("runs", map_result)
            self.assertIn("completed_count", map_result)
            self.assertIn("entered_dead_end_count", map_result)
            self.assertIn("blocked_or_failed_total", map_result)
            self.assertIn("average_step_count", map_result)
            self.assertIn("step_counts", map_result)
            self.assertIn("selected_actions_samples", map_result)
            self.assertIn("dead_end_positions_visited_samples", map_result)
            self.assertIn("blocked_or_failed_samples", map_result)
            self.assertIn("map_status", map_result)
            self.assertIn("validation_notes", map_result)
            self.assertIn(
                map_result["map_status"],
                {
                    "valid_for_two_trial",
                    "no_dead_end_event",
                    "unreachable",
                    "has_shortcut",
                    "mixed",
                    "needs_map_fix",
                },
            )

    def test_existing_dead_end_map_runs_trial1_validation(self):
        result = validate_dead_end_trial1_maps_cli(runs_per_map=2, max_steps=100)
        existing = next(item for item in result["map_results"] if item["level_id"] == "approach_box_dead_end_v0")

        self.assertEqual(existing["runs"], 2)
        self.assertEqual(existing["completed_count"], 2)
        self.assertGreaterEqual(existing["entered_dead_end_count"], 1)
        self.assertGreaterEqual(existing["blocked_or_failed_total"], 1)
        self.assertEqual(existing["map_status"], "valid_for_two_trial")

    def test_candidate_maps_are_reported_honestly_when_runner_adapter_is_missing(self):
        result = validate_dead_end_trial1_maps_cli(runs_per_map=2, max_steps=100)
        candidate_results = [
            item for item in result["map_results"] if item["level_id"] != "approach_box_dead_end_v0"
        ]

        self.assertEqual(len(candidate_results), 3)
        for candidate in candidate_results:
            self.assertEqual(candidate["map_status"], "needs_map_fix")
            self.assertEqual(candidate["completed_count"], 0)
            self.assertIsNone(candidate["average_step_count"])
            self.assertTrue(candidate["validation_notes"])

    def test_overall_summary_and_boundary(self):
        result = validate_dead_end_trial1_maps_cli(runs_per_map=2, max_steps=100)
        summary = result["overall_summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["map_count"], 4)
        self.assertIn("valid_for_two_trial_count", summary)
        self.assertIn("no_dead_end_event_count", summary)
        self.assertIn("unreachable_count", summary)
        self.assertIn("has_shortcut_count", summary)
        self.assertIn("mixed_count", summary)
        self.assertIn("needs_map_fix_count", summary)
        self.assertIn("recommended_next_step", summary)
        self.assertTrue(boundary["trial1_validation_only"])
        self.assertFalse(boundary["two_trial_run"])
        self.assertFalse(boundary["memory_control_run"])
        self.assertFalse(boundary["replayed_full_route"])
        self.assertFalse(boundary["used_llm"])
        self.assertFalse(boundary["used_pathfinding"])
        self.assertFalse(boundary["used_lesson_store"])
        self.assertFalse(boundary["used_memory_layer"])
        self.assertFalse(boundary["modified_action_selection"])
        self.assertFalse(boundary["modified_goal_bias"])
        self.assertFalse(boundary["modified_state_action_memory"])

    def test_module_cli_validation_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "validate-dead-end-trial1-maps",
                "--runs-per-map",
                "2",
                "--max-steps",
                "100",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "dead_end_map_trial1_validation_v0")
        self.assertEqual(result["runs_per_map"], 2)
        self.assertEqual(result["overall_summary"]["map_count"], 4)
        self.assertTrue(result["boundary_check"]["trial1_validation_only"])
        self.assertFalse(result["boundary_check"]["two_trial_run"])
        self.assertFalse(result["boundary_check"]["used_llm"])
        self.assertFalse(result["boundary_check"]["used_pathfinding"])


if __name__ == "__main__":
    unittest.main()
