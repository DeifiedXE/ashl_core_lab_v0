import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_command
from ashl_core.wall_experience_influence import run_wall_experience_influence_check


class WallExperienceInfluenceTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_wall_experience_influence_check()

        self.assertEqual(result["command"], "run-wall-experience-influence-check")
        self.assertEqual(result["flow"], "wall_experience_influence_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["level_id"], "simulated_vision_larger_sandbox_v0")
        self.assertEqual(result["seed"], 1)
        self.assertEqual(result["max_steps"], 50)
        self.assertIn("control_result", result)
        self.assertIn("influence_result", result)
        self.assertIn("experience_store_summary", result)
        self.assertIn("summary", result)

    def test_control_without_prior_experience_does_not_suppress_move_forward(self):
        control = run_wall_experience_influence_check()["control_result"]

        self.assertEqual(control["control_name"], "wall_without_prior_experience")
        self.assertEqual(control["front_symbol"], "w")
        self.assertEqual(control["candidate_action"], "move_forward")
        self.assertFalse(control["matching_experience_found"])
        self.assertEqual(control["selected_action"], "move_forward")
        self.assertFalse(control["experience_used_for_decision"])
        self.assertFalse(control["influence_applied"])
        self.assertTrue(control["passed"])

    def test_prior_wall_experience_suppresses_move_forward(self):
        influence = run_wall_experience_influence_check()["influence_result"]

        self.assertEqual(influence["scenario"], "wall_with_prior_experience")
        self.assertEqual(influence["front_symbol"], "w")
        self.assertEqual(influence["prior_experience"]["front_symbol"], "w")
        self.assertEqual(influence["prior_experience"]["action"], "move_forward")
        self.assertEqual(influence["prior_experience"]["outcome_type"], "blocked")
        self.assertEqual(influence["prior_experience"]["failure_reasons"], ["wall_blocked"])
        self.assertEqual(influence["candidate_action"], "move_forward")
        self.assertEqual(influence["selected_action"], "turn_right")
        self.assertNotEqual(influence["selected_action"], "move_forward")
        self.assertTrue(influence["matching_experience_found"])
        self.assertTrue(influence["experience_used_for_decision"])
        self.assertTrue(influence["influence_applied"])
        self.assertEqual(influence["influence_type"], "suppress")
        self.assertEqual(influence["suppressed_action"], "move_forward")
        self.assertTrue(influence["passed"])

    def test_experience_store_summary_and_summary(self):
        result = run_wall_experience_influence_check()

        self.assertEqual(result["experience_store_summary"]["experience_count"], 1)
        self.assertEqual(result["experience_store_summary"]["experience_keys"], ["front_symbol=w|action=move_forward"])
        self.assertTrue(result["experience_store_summary"]["wall_blocked_experience_available"])
        self.assertTrue(result["summary"]["control_passed"])
        self.assertTrue(result["summary"]["influence_passed"])
        self.assertTrue(result["summary"]["requires_prior_experience_for_influence"])
        self.assertTrue(result["summary"]["all_wall_experience_influence_checks_passed"])

    def test_boundary_flags(self):
        boundary = run_wall_experience_influence_check()["boundary_check"]

        self.assertTrue(boundary["wall_experience_influence_enabled"])
        self.assertTrue(boundary["requires_prior_experience_for_influence"])
        self.assertTrue(boundary["no_experience_control_used"])
        self.assertFalse(boundary["item_reward_bias_enabled"])
        self.assertFalse(boundary["dopamine_like_signal_enabled"])
        self.assertFalse(boundary["item_seeking_enabled"])
        self.assertFalse(boundary["two_round_item_comparison_enabled"])
        self.assertFalse(boundary["llm_planning_used"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["route_planner_added"])
        self.assertFalse(boundary["full_map_visible_to_agent"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["memory_layer_write"])
        self.assertFalse(boundary["lesson_store_write"])
        self.assertFalse(boundary["general_learning_claimed"])

    def test_run_command_uses_default(self):
        result = run_command("run-wall-experience-influence-check")

        self.assertEqual(result["command"], "run-wall-experience-influence-check")
        self.assertEqual(result["seed"], 1)
        self.assertEqual(result["max_steps"], 50)
        self.assertTrue(result["summary"]["all_wall_experience_influence_checks_passed"])

    def test_cli_accepts_seed_and_max_steps(self):
        output = subprocess.check_output(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-wall-experience-influence-check",
                "--seed",
                "9",
                "--max-steps",
                "12",
            ],
            text=True,
            encoding="utf-8",
        )
        result = json.loads(output)

        self.assertEqual(result["seed"], 9)
        self.assertEqual(result["max_steps"], 12)
        self.assertTrue(result["control_result"]["passed"])
        self.assertTrue(result["influence_result"]["passed"])


if __name__ == "__main__":
    unittest.main()
