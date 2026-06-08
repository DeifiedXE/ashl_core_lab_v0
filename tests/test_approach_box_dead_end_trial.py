import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_approach_box_dead_end_trial_cli


class ApproachBoxDeadEndTrialTests(unittest.TestCase):
    def test_dead_end_trial_cli_returns_required_fields(self):
        result = run_approach_box_dead_end_trial_cli(max_steps=100)

        self.assertEqual(result["command"], "run-approach-box-dead-end-trial")
        self.assertEqual(result["flow"], "approach_box_dead_end_trial_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["level_id"], "approach_box_dead_end_v0")
        self.assertTrue(result["completed_approach"])
        self.assertEqual(result["initial_agent_pos"], [1, 1])
        self.assertEqual(result["box_pos"], [4, 4])
        self.assertEqual(result["approach_positions"], [[3, 4]])
        self.assertEqual(result["final_agent_pos"], [3, 4])
        self.assertEqual(result["final_distance_to_box"], 1)
        self.assertEqual(result["max_steps"], 100)
        self.assertGreater(result["step_count"], 0)
        self.assertTrue(result["selected_actions"])
        self.assertTrue(result["entered_dead_end_area"])
        self.assertEqual(result["dead_end_positions_visited"], [[4, 1], [4, 2]])
        self.assertTrue(result["blocked_or_failed_actions"])
        self.assertFalse(result["llm_used"])

    def test_dead_end_boundaries_are_explicit(self):
        boundary = run_approach_box_dead_end_trial_cli(max_steps=100)["boundary"]

        self.assertFalse(boundary["changes_approach_box_runner"])
        self.assertFalse(boundary["changes_navigation_sandbox"])
        self.assertFalse(boundary["changes_push_box_sandbox"])
        self.assertFalse(boundary["two_trial_learning_check"])
        self.assertFalse(boundary["creates_learning_rule"])
        self.assertFalse(boundary["changes_action_selection"])
        self.assertFalse(boundary["changes_goal_bias"])
        self.assertFalse(boundary["changes_state_action_memory"])
        self.assertFalse(boundary["uses_penalty_or_stuck_detection"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["full_route_replay"])
        self.assertFalse(boundary["creates_lesson_candidate"])
        self.assertFalse(boundary["writes_lesson_store"])
        self.assertFalse(boundary["writes_memory_layer"])
        self.assertFalse(boundary["llm_used"])
        self.assertFalse(boundary["proof_of_learning"])

    def test_dead_end_positions_do_not_include_wall_approach_position(self):
        result = run_approach_box_dead_end_trial_cli(max_steps=100)

        self.assertNotIn([4, 3], result["approach_positions"])
        self.assertNotIn([4, 3], result["dead_end_positions_visited"])
        self.assertEqual(result["blocked_or_failed_actions"][0]["blocked_at"], [4, 3])
        self.assertEqual(result["blocked_or_failed_actions"][0]["result"], "wall_blocked")

    def test_dead_end_trial_does_not_return_learning_outputs_or_full_route(self):
        result = run_approach_box_dead_end_trial_cli(max_steps=100)
        forbidden_keys = {
            "lesson_candidate",
            "lesson_store_write",
            "memory_layer_write",
            "learning_rule",
            "pathfinding",
            "route",
            "full_route",
            "trace",
            "steps",
            "two_trial_learning_check_result",
            "proof_of_learning_claim",
        }

        self.assertTrue(forbidden_keys.isdisjoint(result))

    def test_module_cli_dead_end_trial_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-approach-box-dead-end-trial",
                "--max-steps",
                "100",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "approach_box_dead_end_trial_v0")
        self.assertTrue(result["completed_approach"])
        self.assertTrue(result["entered_dead_end_area"])
        self.assertEqual(result["approach_positions"], [[3, 4]])
        self.assertFalse(result["llm_used"])


if __name__ == "__main__":
    unittest.main()
