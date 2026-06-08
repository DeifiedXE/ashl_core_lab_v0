import subprocess
import sys
import unittest

from ashl_core.teaching_cli import (
    _format_candidate_map_trial1_ascii_replay_text,
    run_candidate_dead_end_trial1_ascii_replay_cli,
)


class CandidateMapTrial1AsciiReplayTests(unittest.TestCase):
    def test_candidate_map_replay_handler_returns_required_sections(self):
        result = run_candidate_dead_end_trial1_ascii_replay_cli(max_steps=100)

        self.assertEqual(result["command"], "replay-dead-end-trial1-candidate-maps")
        self.assertEqual(result["flow"], "candidate_map_trial1_ascii_replay_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["max_steps"], 100)
        self.assertEqual(result["map_count"], 4)
        self.assertIn("legend", result)
        self.assertIn("replays", result)
        self.assertIn("overall_summary", result)
        self.assertIn("boundary_check", result)

    def test_candidate_map_replay_includes_all_level_ids(self):
        result = run_candidate_dead_end_trial1_ascii_replay_cli(max_steps=100)
        level_ids = {replay["level_id"] for replay in result["replays"]}

        self.assertEqual(
            level_ids,
            {
                "approach_box_dead_end_v0",
                "user_maze_dead_end_candidate_v0",
                "mid_branch_dead_end_candidate_v0",
                "lower_branch_dead_end_candidate_v0",
            },
        )

    def test_candidate_map_replay_frames_include_grid_and_step_zero(self):
        result = run_candidate_dead_end_trial1_ascii_replay_cli(max_steps=100)

        for replay in result["replays"]:
            self.assertIn("map_status", replay)
            self.assertIn("trial_1_frames", replay)
            self.assertIn("summary", replay)
            first_frame = replay["trial_1_frames"][0]
            self.assertEqual(first_frame["step_index"], 0)
            self.assertEqual(first_frame["action"], "START")
            self.assertIn("grid", first_frame)
            self.assertIn("#", first_frame["grid"])
            self.assertIn("A", first_frame["grid"])
            self.assertIn("B", first_frame["grid"])

    def test_candidate_map_replay_summary_and_boundary(self):
        result = run_candidate_dead_end_trial1_ascii_replay_cli(max_steps=100)
        boundary = result["boundary_check"]
        summary = result["overall_summary"]

        self.assertEqual(summary["replayed_map_count"], 4)
        self.assertIn("valid_for_two_trial_count", summary)
        self.assertIn("has_shortcut_count", summary)
        self.assertIn("recommended_next_step", summary)
        self.assertTrue(boundary["trial1_replay_only"])
        self.assertFalse(boundary["two_trial_run"])
        self.assertFalse(boundary["memory_control_run"])
        self.assertTrue(boundary["replay_output_only"])
        self.assertFalse(boundary["runner_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["used_llm"])
        self.assertFalse(boundary["used_pathfinding"])
        self.assertFalse(boundary["used_lesson_store"])
        self.assertFalse(boundary["used_memory_layer"])
        self.assertFalse(boundary["modified_docs_current_boundary_index"])

    def test_candidate_map_replay_text_contains_key_sections(self):
        result = run_candidate_dead_end_trial1_ascii_replay_cli(max_steps=100)
        text = _format_candidate_map_trial1_ascii_replay_text(result)

        self.assertIn("command: replay-dead-end-trial1-candidate-maps", text)
        self.assertIn("approach_box_dead_end_v0", text)
        self.assertIn("user_maze_dead_end_candidate_v0", text)
        self.assertIn("mid_branch_dead_end_candidate_v0", text)
        self.assertIn("lower_branch_dead_end_candidate_v0", text)
        self.assertIn("Map 1 / approach_box_dead_end_v0 / Step 0", text)
        self.assertIn("grid:", text)
        self.assertIn("legend:", text)
        self.assertIn("summary:", text)
        self.assertIn("boundary_check:", text)
        self.assertIn("trial1_replay_only: true", text)
        self.assertIn("used_llm: false", text)

    def test_module_cli_candidate_map_replay_outputs_text(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "replay-dead-end-trial1-candidate-maps",
                "--max-steps",
                "100",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        output = process.stdout

        self.assertIn("command: replay-dead-end-trial1-candidate-maps", output)
        self.assertIn("approach_box_dead_end_v0", output)
        self.assertIn("user_maze_dead_end_candidate_v0", output)
        self.assertIn("Step 0", output)
        self.assertIn("grid:", output)
        self.assertIn("boundary_check:", output)
        self.assertIn("trial1_replay_only: true", output)
        self.assertIn("used_pathfinding: false", output)


if __name__ == "__main__":
    unittest.main()
