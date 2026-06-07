import json
import subprocess
import sys
import unittest

from ashl_core.first_output_runtime import UTTERANCE_MAP
from ashl_core.teaching_cli import run_grounded_learning_check


class GroundedLearningVerificationCliTests(unittest.TestCase):
    def test_push_right_push_right_returns_status_ok(self):
        result = run_grounded_learning_check(actions=["push_right", "push_right"])

        self.assertEqual(result["flow"], "grounded_learning_verification_cli_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["actions"], ["push_right", "push_right"])
        self.assertEqual(len(result["steps"]), 2)

    def test_steps_map_blocked_result_to_blocked_utterance(self):
        result = run_grounded_learning_check(actions=["push_right", "push_right"])

        for step in result["steps"]:
            self.assertEqual(step["tactile_result"], "box_blocked")
            self.assertEqual(step["state_key"], "blocked")
            self.assertEqual(step["utterance"], UTTERANCE_MAP["blocked"])
            self.assertEqual(step["trace"]["trace_type"], "tactile_sandbox_trace")

    def test_second_step_reads_previous_push_right_blocked_history(self):
        result = run_grounded_learning_check(actions=["push_right", "push_right"])
        first_history = result["steps"][0]["history"]
        second_history = result["steps"][1]["history"]

        self.assertFalse(first_history["same_action_attempted_before"])
        self.assertTrue(second_history["same_action_attempted_before"])
        self.assertEqual(second_history["previous_same_action_result"], "box_blocked")
        self.assertEqual(second_history["previous_same_action_tick"], 1)

    def test_suggested_next_action_avoids_push_right(self):
        result = run_grounded_learning_check(actions=["push_right", "push_right"])

        self.assertNotEqual(result["suggested_next_action"], "push_right")
        self.assertEqual(result["suggested_next_action"], "wait")

    def test_boundary_flags_are_false(self):
        boundary = run_grounded_learning_check(actions=["push_right", "push_right"])["boundary"]

        self.assertFalse(boundary["llm_used"])
        self.assertFalse(boundary["creates_lesson_candidate"])
        self.assertFalse(boundary["writes_lesson_store"])
        self.assertFalse(boundary["writes_memory_layer"])
        self.assertFalse(boundary["learning_pipeline_used"])
        self.assertFalse(boundary["teaching_chat_loop_used"])
        self.assertFalse(boundary["awakening_claim"])

    def test_invalid_action_fails_through_allowed_action_validation(self):
        result = run_grounded_learning_check(actions=["push_right", "push right"])

        self.assertEqual(result["status"], "error")
        self.assertIn("unsupported action", result["error"])
        self.assertEqual(len(result["steps"]), 1)
        self.assertFalse(result["boundary"]["creates_lesson_candidate"])

    def test_module_cli_accepts_actions_argument(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-grounded-learning-check",
                "--actions",
                "push_right",
                "push_right",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["steps"]), 2)
        self.assertEqual(result["steps"][1]["history"]["previous_same_action_result"], "box_blocked")
        self.assertEqual(result["suggested_next_action"], "wait")


if __name__ == "__main__":
    unittest.main()
