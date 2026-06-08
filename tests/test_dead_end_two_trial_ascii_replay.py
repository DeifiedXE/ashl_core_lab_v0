import subprocess
import sys
import unittest

from ashl_core.teaching_cli import (
    _format_dead_end_ascii_replay_text,
    run_approach_box_dead_end_two_trial_ascii_replay_cli,
)


class DeadEndTwoTrialAsciiReplayTests(unittest.TestCase):
    def test_ascii_replay_handler_returns_required_sections(self):
        result = run_approach_box_dead_end_two_trial_ascii_replay_cli(max_steps=100)

        self.assertEqual(result["command"], "replay-approach-box-dead-end-two-trial")
        self.assertEqual(result["flow"], "dead_end_two_trial_ascii_replay_v0")
        self.assertEqual(result["level_id"], "approach_box_dead_end_v0")
        self.assertEqual(result["max_steps"], 100)
        self.assertIn("legend", result)
        self.assertIn("trial_1_replay", result)
        self.assertIn("trial_2_replay", result)
        self.assertIn("summary", result)
        self.assertIn("boundary_check", result)

    def test_ascii_replay_frames_include_step_metadata_and_grid(self):
        result = run_approach_box_dead_end_two_trial_ascii_replay_cli(max_steps=100)
        first_frame = result["trial_1_replay"][0]

        self.assertEqual(first_frame["trial"], "Trial 1")
        self.assertEqual(first_frame["step_index"], 0)
        self.assertEqual(first_frame["action"], "START")
        self.assertEqual(first_frame["result"], "start")
        self.assertEqual(first_frame["agent_pos"], [1, 1])
        self.assertIn("########", first_frame["grid"])
        self.assertIn("A", first_frame["grid"])
        self.assertIn("B", first_frame["grid"])
        self.assertIn("x", first_frame["grid"])

    def test_ascii_replay_reports_dead_end_and_blocked_events(self):
        result = run_approach_box_dead_end_two_trial_ascii_replay_cli(max_steps=100)
        trial_1 = result["trial_1_replay"]
        trial_2 = result["trial_2_replay"]

        self.assertTrue(any(frame.get("entered_dead_end_area") is True for frame in trial_1))
        self.assertTrue(any(frame.get("blocked_at") == [4, 3] for frame in trial_1))
        self.assertFalse(any(frame.get("entered_dead_end_area") is True for frame in trial_2))
        self.assertFalse(any("blocked_at" in frame for frame in trial_2))

    def test_ascii_replay_summary_and_boundary(self):
        result = run_approach_box_dead_end_two_trial_ascii_replay_cli(max_steps=100)
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["trial1_step_count"], 11)
        self.assertEqual(summary["trial2_step_count"], 5)
        self.assertEqual(summary["step_count_delta"], -6)
        self.assertTrue(summary["trial1_entered_dead_end_area"])
        self.assertFalse(summary["trial2_entered_dead_end_area"])
        self.assertEqual(summary["trial1_blocked_or_failed_count"], 1)
        self.assertEqual(summary["trial2_blocked_or_failed_count"], 0)
        self.assertFalse(summary["llm_used"])
        self.assertTrue(boundary["replay_only"])
        self.assertFalse(boundary["runner_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["used_llm"])
        self.assertFalse(boundary["used_pathfinding"])
        self.assertFalse(boundary["used_memory_layer"])
        self.assertFalse(boundary["used_lesson_store"])
        self.assertFalse(boundary["replayed_full_route_as_input"])

    def test_ascii_replay_text_contains_key_sections(self):
        result = run_approach_box_dead_end_two_trial_ascii_replay_cli(max_steps=100)
        text = _format_dead_end_ascii_replay_text(result)

        self.assertIn("command: replay-approach-box-dead-end-two-trial", text)
        self.assertIn("legend:", text)
        self.assertIn("trial_1_replay:", text)
        self.assertIn("trial_2_replay:", text)
        self.assertIn("Trial 1 / Step 0", text)
        self.assertIn("Trial 2 / Step 0", text)
        self.assertIn("summary:", text)
        self.assertIn("boundary_check:", text)
        self.assertIn("replay_only: true", text)
        self.assertIn("used_llm: false", text)

    def test_module_cli_ascii_replay_outputs_text(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "replay-approach-box-dead-end-two-trial",
                "--max-steps",
                "100",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        output = process.stdout

        self.assertIn("command: replay-approach-box-dead-end-two-trial", output)
        self.assertIn("Trial 1 / Step 0", output)
        self.assertIn("Trial 2 / Step 0", output)
        self.assertIn("########", output)
        self.assertIn("summary:", output)
        self.assertIn("boundary_check:", output)
        self.assertIn("replay_only: true", output)
        self.assertIn("used_llm: false", output)


if __name__ == "__main__":
    unittest.main()
