import json
import subprocess
import sys
import unittest

from ashl_core.instinct_random_walk_runner import run_instinct_random_walk
from ashl_core.teaching_cli import run_command


class InstinctRandomWalkRunnerTests(unittest.TestCase):
    def test_default_runner_shape(self):
        result = run_instinct_random_walk()

        self.assertEqual(result["command"], "run-instinct-random-walk")
        self.assertEqual(result["flow"], "instinct_random_walk_runner_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["level_id"], "simulated_vision_larger_sandbox_v0")
        self.assertEqual(result["seed"], 1)
        self.assertEqual(result["max_steps"], 50)
        self.assertEqual(result["metrics"]["step_count"], 50)
        self.assertLessEqual(result["metrics"]["step_count"], result["max_steps"])
        self.assertIn("wall_blocked_count", result["metrics"])
        self.assertIn("item_contact_count", result["metrics"])
        self.assertEqual(result["experience_summary"]["experience_count"], 50)

    def test_same_seed_is_deterministic(self):
        first = run_instinct_random_walk(seed=7, max_steps=20)
        second = run_instinct_random_walk(seed=7, max_steps=20)

        self.assertEqual(first["step_trace"], second["step_trace"])
        self.assertEqual(first["experience_summary"], second["experience_summary"])
        self.assertEqual(first["metrics"], second["metrics"])

    def test_different_seed_can_produce_different_trace(self):
        first = run_instinct_random_walk(seed=1, max_steps=20)
        second = run_instinct_random_walk(seed=2, max_steps=20)

        first_actions = [step["selected_action"] for step in first["step_trace"]]
        second_actions = [step["selected_action"] for step in second["step_trace"]]
        self.assertNotEqual(first_actions, second_actions)

    def test_step_trace_and_experience_records(self):
        result = run_instinct_random_walk(seed=3, max_steps=8)

        self.assertEqual(len(result["step_trace"]), 8)
        for step in result["step_trace"]:
            self.assertIn(step["selected_action"], {"look", "turn_left", "turn_right", "move_forward"})
            self.assertIn("viewport_before", step)
            self.assertIn("viewport_after", step)
            self.assertIn("front_symbol_before", step)
            self.assertIn("experience_record", step)
            record = step["experience_record"]
            self.assertEqual(record["front_symbol"], step["front_symbol_before"])
            self.assertEqual(record["action"], step["selected_action"])
            self.assertIn(record["outcome_type"], {"observed", "turned", "blocked", "moved", "item_contact", "exit_contact"})
            self.assertTrue(record["experience_key"].startswith("front_symbol="))
            self.assertIn("|action=", record["experience_key"])

    def test_boundary_flags_stay_inside_round_1_limits(self):
        boundary = run_instinct_random_walk(seed=1, max_steps=5)["boundary_check"]

        self.assertTrue(boundary["instinct_random_walk_enabled"])
        self.assertTrue(boundary["round_1_only"])
        self.assertTrue(boundary["bounded_seeded_runner"])
        self.assertFalse(boundary["prior_experience_loaded"])
        self.assertFalse(boundary["experience_influence_enabled"])
        self.assertFalse(boundary["reward_bias_enabled"])
        self.assertFalse(boundary["dopamine_like_signal_enabled"])
        self.assertFalse(boundary["two_round_comparison_enabled"])
        self.assertFalse(boundary["llm_planning_used"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["route_planner_added"])
        self.assertFalse(boundary["full_map_visible_to_agent"])
        self.assertFalse(boundary["item_collection_enabled"])
        self.assertFalse(boundary["memory_layer_write"])
        self.assertFalse(boundary["long_term_memory_write"])

    def test_run_command_uses_default(self):
        result = run_command("run-instinct-random-walk")

        self.assertEqual(result["command"], "run-instinct-random-walk")
        self.assertEqual(result["seed"], 1)
        self.assertEqual(result["max_steps"], 50)

    def test_cli_accepts_seed_and_max_steps(self):
        output = subprocess.check_output(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-instinct-random-walk",
                "--seed",
                "3",
                "--max-steps",
                "7",
            ],
            text=True,
            encoding="utf-8",
        )
        result = json.loads(output)

        self.assertEqual(result["seed"], 3)
        self.assertEqual(result["max_steps"], 7)
        self.assertEqual(len(result["step_trace"]), 7)


if __name__ == "__main__":
    unittest.main()
