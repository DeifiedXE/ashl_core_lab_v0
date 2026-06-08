import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_approach_box_dead_end_two_trial_check_cli


class ApproachBoxDeadEndTwoTrialLearningCheckTests(unittest.TestCase):
    def test_dead_end_two_trial_check_returns_required_sections(self):
        result = run_approach_box_dead_end_two_trial_check_cli(max_steps=100)

        self.assertEqual(result["command"], "run-approach-box-dead-end-two-trial-check")
        self.assertEqual(result["flow"], "approach_box_dead_end_two_trial_learning_check_v0")
        self.assertEqual(result["status"], "ok")
        self.assertIn("trial_1", result)
        self.assertIn("trial_2", result)
        self.assertIn("comparison", result)
        self.assertIn("boundary_check", result)

    def test_trial_summaries_have_expected_shape(self):
        result = run_approach_box_dead_end_two_trial_check_cli(max_steps=100)
        trial_1 = result["trial_1"]
        trial_2 = result["trial_2"]

        self.assertEqual(trial_1["level_id"], "approach_box_dead_end_v0")
        self.assertEqual(trial_2["level_id"], "approach_box_dead_end_v0")
        self.assertTrue(trial_1["completed_approach"])
        self.assertTrue(trial_2["completed_approach"])
        self.assertEqual(trial_1["approach_positions"], [[3, 4]])
        self.assertEqual(trial_2["approach_positions"], [[3, 4]])
        self.assertTrue(trial_1["entered_dead_end_area"])
        self.assertFalse(trial_2["entered_dead_end_area"])
        self.assertEqual(trial_1["dead_end_positions_visited"], [[4, 1], [4, 2]])
        self.assertEqual(trial_2["dead_end_positions_visited"], [])
        self.assertTrue(trial_1["blocked_or_failed_actions"])
        self.assertEqual(trial_2["blocked_or_failed_actions"], [])
        self.assertGreater(trial_1["step_count"], trial_2["step_count"])
        self.assertTrue(trial_1["selected_actions"])
        self.assertTrue(trial_2["selected_actions"])
        self.assertNotEqual(trial_1["selected_actions"], trial_2["selected_actions"])
        self.assertTrue(trial_1["local_outcome_memory_written"])
        self.assertTrue(trial_2["local_outcome_memory_read"])
        self.assertTrue(trial_2["used_trial1_local_memory"])
        self.assertTrue(trial_2["avoided_trial1_dead_end_action"])
        self.assertFalse(trial_1["llm_used"])
        self.assertFalse(trial_2["llm_used"])

    def test_comparison_reports_dead_end_deltas(self):
        comparison = run_approach_box_dead_end_two_trial_check_cli(max_steps=100)["comparison"]

        self.assertEqual(comparison["trial1_step_count"], 11)
        self.assertEqual(comparison["trial2_step_count"], 5)
        self.assertEqual(comparison["step_count_delta"], -6)
        self.assertTrue(comparison["trial1_entered_dead_end_area"])
        self.assertFalse(comparison["trial2_entered_dead_end_area"])
        self.assertEqual(comparison["trial1_dead_end_positions_visited"], [[4, 1], [4, 2]])
        self.assertEqual(comparison["trial2_dead_end_positions_visited"], [])
        self.assertEqual(comparison["dead_end_positions_visited_delta"], -2)
        self.assertEqual(comparison["trial1_blocked_or_failed_count"], 1)
        self.assertEqual(comparison["trial2_blocked_or_failed_count"], 0)
        self.assertEqual(comparison["blocked_or_failed_delta"], -1)
        self.assertTrue(comparison["avoided_trial1_dead_end_action"])

    def test_boundary_check_rejects_forbidden_sources(self):
        boundary = run_approach_box_dead_end_two_trial_check_cli(max_steps=100)["boundary_check"]

        self.assertTrue(boundary["trial2_read_local_outcome_memory_only"])
        self.assertFalse(boundary["trial2_replayed_full_route"])
        self.assertFalse(boundary["trial2_used_llm"])
        self.assertFalse(boundary["trial2_used_lesson_store"])
        self.assertFalse(boundary["trial2_used_memory_layer"])
        self.assertFalse(boundary["trial2_used_long_term_memory"])
        self.assertFalse(boundary["trial2_used_lesson_candidate"])
        self.assertFalse(boundary["trial2_used_pathfinding"])
        self.assertFalse(boundary["trial2_used_human_hint"])

    def test_dead_end_two_trial_check_does_not_return_full_traces_or_learning_outputs(self):
        result = run_approach_box_dead_end_two_trial_check_cli(max_steps=100)
        forbidden_keys = {
            "steps",
            "trace",
            "route",
            "full_route",
            "solution",
            "preloaded_actions",
            "lesson_candidate",
            "lesson_store_write",
            "memory_layer_write",
            "long_term_memory_write",
            "llm_prompt",
            "pathfinding",
            "proof_of_learning_claim",
        }

        self.assertTrue(forbidden_keys.isdisjoint(result))
        self.assertTrue(forbidden_keys.isdisjoint(result["trial_1"]))
        self.assertTrue(forbidden_keys.isdisjoint(result["trial_2"]))

    def test_module_cli_dead_end_two_trial_check_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-approach-box-dead-end-two-trial-check",
                "--max-steps",
                "100",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "approach_box_dead_end_two_trial_learning_check_v0")
        self.assertEqual(result["trial_1"]["level_id"], "approach_box_dead_end_v0")
        self.assertEqual(result["trial_2"]["level_id"], "approach_box_dead_end_v0")
        self.assertTrue(result["trial_2"]["local_outcome_memory_read"])
        self.assertTrue(result["comparison"]["avoided_trial1_dead_end_action"])
        self.assertFalse(result["boundary_check"]["trial2_replayed_full_route"])
        self.assertFalse(result["boundary_check"]["trial2_used_llm"])


if __name__ == "__main__":
    unittest.main()
