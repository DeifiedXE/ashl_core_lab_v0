import json
import subprocess
import sys
import unittest

from ashl_core.first_output_runtime import UTTERANCE_MAP
from ashl_core.teaching_cli import run_tactile_interaction


class TactileInteractionCliBridgeTests(unittest.TestCase):
    def test_valid_action_returns_ok_json_shape(self):
        result = run_tactile_interaction(action="push_right")

        self.assertEqual(result["flow"], "tactile_interaction_cli_bridge_v0")
        self.assertEqual(result["status"], "ok")
        self.assertIn("tactile_result", result)
        self.assertIn("state_key", result)
        self.assertIn("utterance", result)
        self.assertIn("tactile_sandbox_trace", result)
        self.assertIn("boundary", result)

    def test_push_right_maps_box_blocked_to_blocked_utterance(self):
        result = run_tactile_interaction(action="push_right")

        self.assertEqual(result["tactile_result"], "box_blocked")
        self.assertEqual(result["state_key"], "blocked")
        self.assertEqual(result["utterance"], UTTERANCE_MAP["blocked"])

    def test_touch_right_maps_box_contact_to_observed_utterance(self):
        result = run_tactile_interaction(action="touch_right")

        self.assertEqual(result["tactile_result"], "box_contact")
        self.assertEqual(result["state_key"], "observed")
        self.assertEqual(result["utterance"], UTTERANCE_MAP["observed"])

    def test_boundary_flags_are_false(self):
        boundary = run_tactile_interaction(action="push_right")["boundary"]

        self.assertIs(boundary["llm_used"], False)
        self.assertIs(boundary["creates_lesson_candidate"], False)
        self.assertIs(boundary["writes_lesson_store"], False)
        self.assertIs(boundary["writes_memory_layer"], False)
        self.assertIs(boundary["awakening_claim"], False)

    def test_invalid_action_returns_error_without_learning_outputs(self):
        result = run_tactile_interaction(action="move_diagonal")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["flow"], "tactile_interaction_cli_bridge_v0")
        self.assertIn("unsupported action", result["error"])
        self.assertNotIn("lesson_candidate", result)
        self.assertNotIn("failure_event", result)
        self.assertNotIn("review_decision", result)
        self.assertNotIn("selection_eligibility", result)
        self.assertNotIn("activation", result)

    def test_module_cli_accepts_action_argument(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-tactile-interaction",
                "--action",
                "push_right",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["tactile_result"], "box_blocked")
        self.assertEqual(result["state_key"], "blocked")


if __name__ == "__main__":
    unittest.main()
