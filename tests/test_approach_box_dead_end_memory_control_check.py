import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_approach_box_dead_end_memory_control_check_cli


class ApproachBoxDeadEndMemoryControlCheckTests(unittest.TestCase):
    def test_memory_control_check_returns_required_sections(self):
        result = run_approach_box_dead_end_memory_control_check_cli(max_steps=100, runs=3)

        self.assertEqual(result["command"], "run-approach-box-dead-end-memory-control-check")
        self.assertEqual(result["flow"], "dead_end_memory_control_check_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["level_id"], "approach_box_dead_end_v0")
        self.assertEqual(result["runs"], 3)
        self.assertEqual(result["max_steps"], 100)
        self.assertIn("with_memory", result)
        self.assertIn("without_memory", result)
        self.assertIn("trial1_source_audit", result)
        self.assertIn("conditioned_on_trial1_dead_end", result)
        self.assertIn("comparison", result)
        self.assertIn("boundary_check", result)

    def test_memory_control_group_summaries_match_requested_runs(self):
        result = run_approach_box_dead_end_memory_control_check_cli(max_steps=100, runs=4)
        with_memory = result["with_memory"]
        without_memory = result["without_memory"]

        self.assertEqual(with_memory["run_count"], 4)
        self.assertEqual(without_memory["run_count"], 4)
        self.assertEqual(len(with_memory["trial2_step_counts"]), 4)
        self.assertEqual(len(without_memory["trial2_step_counts"]), 4)
        self.assertGreaterEqual(with_memory["trial2_completed_count"], 0)
        self.assertGreaterEqual(without_memory["trial2_completed_count"], 0)
        self.assertGreaterEqual(with_memory["trial2_entered_dead_end_count"], 0)
        self.assertGreaterEqual(without_memory["trial2_entered_dead_end_count"], 0)
        self.assertGreaterEqual(with_memory["trial2_blocked_or_failed_total"], 0)
        self.assertGreaterEqual(without_memory["trial2_blocked_or_failed_total"], 0)

    def test_comparison_reports_control_metrics_without_requiring_memory_win(self):
        result = run_approach_box_dead_end_memory_control_check_cli(max_steps=100, runs=2)
        comparison = result["comparison"]

        self.assertIn("entered_dead_end_count_delta", comparison)
        self.assertIn("blocked_or_failed_total_delta", comparison)
        self.assertIn("average_step_count_delta", comparison)
        self.assertIn("completed_count_delta", comparison)
        self.assertIn("memory_effect_observed", comparison)
        self.assertTrue(comparison["control_group_used"])
        self.assertIsInstance(comparison["memory_effect_observed"], bool)

    def test_trial1_source_audit_reports_memory_source_fields(self):
        result = run_approach_box_dead_end_memory_control_check_cli(max_steps=100, runs=3)
        audit = result["trial1_source_audit"]

        self.assertIn("with_memory_trial1_entered_dead_end_count", audit)
        self.assertIn("with_memory_trial1_blocked_or_failed_total", audit)
        self.assertIn("with_memory_trial1_local_memory_written_count", audit)
        self.assertIn("with_memory_trial1_average_step_count", audit)
        self.assertIn("with_memory_trial1_step_counts", audit)
        self.assertIn("without_memory_trial1_entered_dead_end_count", audit)
        self.assertIn("without_memory_trial1_blocked_or_failed_total", audit)
        self.assertIn("without_memory_trial1_local_memory_written_count", audit)
        self.assertIn("without_memory_trial1_average_step_count", audit)
        self.assertIn("without_memory_trial1_step_counts", audit)
        self.assertEqual(len(audit["with_memory_trial1_step_counts"]), 3)
        self.assertEqual(len(audit["without_memory_trial1_step_counts"]), 3)

    def test_conditioned_analysis_reports_trial1_dead_end_sample_fields(self):
        result = run_approach_box_dead_end_memory_control_check_cli(max_steps=100, runs=3)
        conditioned = result["conditioned_on_trial1_dead_end"]

        self.assertIn("with_memory_sample_count", conditioned)
        self.assertIn("with_memory_trial2_avoided_count", conditioned)
        self.assertIn("with_memory_trial2_avoid_rate", conditioned)
        self.assertIn("without_memory_sample_count", conditioned)
        self.assertIn("without_memory_trial2_avoided_count", conditioned)
        self.assertIn("without_memory_trial2_avoid_rate", conditioned)
        self.assertIn("conditioned_memory_effect_observed", conditioned)
        self.assertIsInstance(conditioned["conditioned_memory_effect_observed"], bool)

    def test_boundary_check_rejects_forbidden_sources(self):
        boundary = run_approach_box_dead_end_memory_control_check_cli(max_steps=100, runs=2)["boundary_check"]

        self.assertTrue(boundary["trial1_source_audit_present"])
        self.assertTrue(boundary["conditioned_analysis_present"])
        self.assertTrue(boundary["with_memory_trial2_read_local_outcome_memory"])
        self.assertFalse(boundary["without_memory_trial2_read_local_outcome_memory"])
        self.assertFalse(boundary["with_memory_trial2_replayed_full_route"])
        self.assertFalse(boundary["without_memory_trial2_replayed_full_route"])
        self.assertFalse(boundary["trial2_used_llm"])
        self.assertFalse(boundary["trial2_used_lesson_store"])
        self.assertFalse(boundary["trial2_used_memory_layer"])
        self.assertFalse(boundary["trial2_used_long_term_memory"])
        self.assertFalse(boundary["trial2_used_lesson_candidate"])
        self.assertFalse(boundary["trial2_used_pathfinding"])
        self.assertFalse(boundary["trial2_used_human_hint"])

    def test_module_cli_memory_control_check_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-approach-box-dead-end-memory-control-check",
                "--max-steps",
                "100",
                "--runs",
                "3",
                "--random-seed",
                "17",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "dead_end_memory_control_check_v0")
        self.assertEqual(result["runs"], 3)
        self.assertEqual(result["random_seed"], 17)
        self.assertEqual(result["with_memory"]["run_count"], 3)
        self.assertEqual(result["without_memory"]["run_count"], 3)
        self.assertIn("trial1_source_audit", result)
        self.assertIn("conditioned_on_trial1_dead_end", result)
        self.assertTrue(result["comparison"]["control_group_used"])
        self.assertTrue(result["boundary_check"]["trial1_source_audit_present"])
        self.assertTrue(result["boundary_check"]["conditioned_analysis_present"])
        self.assertTrue(result["boundary_check"]["with_memory_trial2_read_local_outcome_memory"])
        self.assertFalse(result["boundary_check"]["without_memory_trial2_read_local_outcome_memory"])


if __name__ == "__main__":
    unittest.main()
