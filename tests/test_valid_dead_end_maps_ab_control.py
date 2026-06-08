import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_valid_dead_end_maps_ab_control_cli


class ValidDeadEndMapsAbControlTests(unittest.TestCase):
    def test_valid_dead_end_maps_ab_control_returns_required_sections(self):
        result = run_valid_dead_end_maps_ab_control_cli(runs_per_map=3, max_steps=100)

        self.assertEqual(result["command"], "run-valid-dead-end-maps-ab-control")
        self.assertEqual(result["flow"], "valid_dead_end_maps_ab_control_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["runs_per_map"], 3)
        self.assertEqual(result["max_steps"], 100)
        self.assertIn("included_maps", result)
        self.assertIn("excluded_maps", result)
        self.assertIn("map_results", result)
        self.assertIn("overall_summary", result)
        self.assertIn("boundary_check", result)

    def test_includes_exact_valid_maps_and_excludes_shortcut_map(self):
        result = run_valid_dead_end_maps_ab_control_cli(runs_per_map=2, max_steps=100)

        self.assertEqual(
            result["included_maps"],
            [
                "approach_box_dead_end_v0",
                "mid_branch_dead_end_candidate_v0",
                "lower_branch_dead_end_candidate_v0",
            ],
        )
        self.assertNotIn("user_maze_dead_end_candidate_v0", result["included_maps"])
        self.assertIn(
            {
                "level_id": "user_maze_dead_end_candidate_v0",
                "reason": "has_shortcut_no_dead_end_event",
            },
            result["excluded_maps"],
        )

    def test_map_results_have_ab_control_sections(self):
        result = run_valid_dead_end_maps_ab_control_cli(runs_per_map=3, max_steps=100)

        self.assertEqual(len(result["map_results"]), 3)
        for map_result in result["map_results"]:
            self.assertIn("level_id", map_result)
            self.assertIn("runs", map_result)
            self.assertEqual(map_result["runs"], 3)
            self.assertIn("with_memory", map_result)
            self.assertIn("without_memory", map_result)
            self.assertIn("comparison", map_result)
            self.assertIn("trial1_source_audit", map_result)
            self.assertIn("conditioned_on_trial1_dead_end", map_result)
            self.assertIn("map_status", map_result)

    def test_group_summaries_and_comparison_fields_are_present(self):
        result = run_valid_dead_end_maps_ab_control_cli(runs_per_map=2, max_steps=100)

        for map_result in result["map_results"]:
            for group_name in ("with_memory", "without_memory"):
                group = map_result[group_name]
                self.assertIn("trial2_completed_count", group)
                self.assertIn("trial2_entered_dead_end_count", group)
                self.assertIn("trial2_blocked_or_failed_total", group)
                self.assertIn("trial2_average_step_count", group)
                self.assertIn("trial2_step_counts", group)
                self.assertEqual(len(group["trial2_step_counts"]), 2)

            comparison = map_result["comparison"]
            self.assertIn("entered_dead_end_count_delta", comparison)
            self.assertIn("blocked_or_failed_total_delta", comparison)
            self.assertIn("average_step_count_delta", comparison)
            self.assertIn("completed_count_delta", comparison)
            self.assertIn("memory_effect_observed", comparison)
            self.assertTrue(comparison["control_group_used"])
            self.assertIsInstance(comparison["memory_effect_observed"], bool)

    def test_trial1_source_audit_and_conditioned_analysis_fields_are_present(self):
        result = run_valid_dead_end_maps_ab_control_cli(runs_per_map=2, max_steps=100)

        for map_result in result["map_results"]:
            audit = map_result["trial1_source_audit"]
            self.assertIn("with_memory_trial1_entered_dead_end_count", audit)
            self.assertIn("with_memory_trial1_blocked_or_failed_total", audit)
            self.assertIn("with_memory_trial1_local_memory_written_count", audit)
            self.assertIn("without_memory_trial1_entered_dead_end_count", audit)
            self.assertIn("without_memory_trial1_blocked_or_failed_total", audit)
            self.assertIn("without_memory_trial1_local_memory_written_count", audit)

            conditioned = map_result["conditioned_on_trial1_dead_end"]
            self.assertIn("with_memory_sample_count", conditioned)
            self.assertIn("with_memory_trial2_avoided_count", conditioned)
            self.assertIn("with_memory_trial2_avoid_rate", conditioned)
            self.assertIn("without_memory_sample_count", conditioned)
            self.assertIn("without_memory_trial2_avoided_count", conditioned)
            self.assertIn("without_memory_trial2_avoid_rate", conditioned)
            self.assertIn("conditioned_memory_effect_observed", conditioned)
            self.assertIsInstance(conditioned["conditioned_memory_effect_observed"], bool)

    def test_overall_summary_and_boundary(self):
        result = run_valid_dead_end_maps_ab_control_cli(runs_per_map=3, max_steps=100)
        summary = result["overall_summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["map_count"], 3)
        self.assertEqual(summary["included_map_count"], 3)
        self.assertEqual(summary["excluded_map_count"], 1)
        self.assertEqual(summary["runs_per_map"], 3)
        self.assertIn("maps_with_memory_effect_observed", summary)
        self.assertIn("maps_without_memory_effect_observed", summary)
        self.assertIn("maps_with_mixed_result", summary)
        self.assertIn("overall_interpretation", summary)
        self.assertTrue(boundary["valid_maps_only"])
        self.assertTrue(boundary["excluded_shortcut_map"])
        self.assertTrue(boundary["with_memory_trial2_reads_local_memory"])
        self.assertFalse(boundary["without_memory_trial2_reads_local_memory"])
        self.assertFalse(boundary["replayed_full_route"])
        self.assertFalse(boundary["used_llm"])
        self.assertFalse(boundary["used_pathfinding"])
        self.assertFalse(boundary["used_lesson_store"])
        self.assertFalse(boundary["used_memory_layer"])
        self.assertFalse(boundary["modified_action_selection"])
        self.assertFalse(boundary["modified_goal_bias"])
        self.assertFalse(boundary["modified_state_action_memory"])

    def test_module_cli_valid_dead_end_maps_ab_control_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-valid-dead-end-maps-ab-control",
                "--runs-per-map",
                "3",
                "--max-steps",
                "100",
                "--random-seed",
                "17",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "valid_dead_end_maps_ab_control_v0")
        self.assertEqual(result["runs_per_map"], 3)
        self.assertEqual(result["random_seed"], 17)
        self.assertEqual(len(result["map_results"]), 3)
        self.assertNotIn("user_maze_dead_end_candidate_v0", result["included_maps"])
        self.assertTrue(result["boundary_check"]["valid_maps_only"])
        self.assertTrue(result["boundary_check"]["excluded_shortcut_map"])
        self.assertFalse(result["boundary_check"]["replayed_full_route"])
        self.assertFalse(result["boundary_check"]["used_llm"])
        self.assertFalse(result["boundary_check"]["used_pathfinding"])


if __name__ == "__main__":
    unittest.main()
