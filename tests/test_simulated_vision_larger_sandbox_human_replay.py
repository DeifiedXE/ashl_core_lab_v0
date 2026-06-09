import json
import subprocess
import sys
import unittest

from ashl_core.simulated_vision_larger_sandbox import run_simulated_vision_larger_sandbox_demo
from ashl_core.simulated_vision_larger_sandbox_human_replay import (
    get_front_symbol_for_replay,
    run_larger_sandbox_human_replay,
)
from ashl_core.teaching_cli import run_larger_sandbox_human_replay as run_cli_helper


class LargerSandboxHumanReplayTests(unittest.TestCase):
    def test_demo_replay_is_plain_text_with_legend_and_steps(self):
        text = run_larger_sandbox_human_replay()

        self.assertIsInstance(text, str)
        self.assertIn("Larger Sandbox Human Replay", text)
        self.assertIn("Level: simulated_vision_larger_sandbox_v0", text)
        self.assertIn("Mode: demo", text)
        self.assertIn("Legend:", text)
        self.assertIn("w = wall", text)
        self.assertIn("e = empty", text)
        self.assertIn("i = item", text)
        self.assertIn("d = passage marker", text)
        self.assertIn("g = exit placeholder", text)
        self.assertIn("x = unseen / out of view", text)
        self.assertIn("a = Qingyin", text)
        self.assertIn("Step 1: look", text)
        self.assertIn("Position:", text)
        self.assertIn("Facing:", text)
        self.assertIn("Visible symbols:", text)
        self.assertIn("Front symbol:", text)

    def test_demo_replay_contains_stable_viewport_rows(self):
        text = run_larger_sandbox_human_replay()

        self.assertIn("w w w\ne e e\ne a e", text)

    def test_front_symbol_helper_uses_immediate_front_cell(self):
        viewport = [
            ["w", "w", "w"],
            ["e", "e", "e"],
            ["e", "a", "d"],
        ]

        self.assertEqual(get_front_symbol_for_replay(viewport), "e")

    def test_demo_side_d_viewport_reports_empty_front_symbol(self):
        text = run_larger_sandbox_human_replay()
        bad_case = (
            "Viewport:\n"
            "w w w\n"
            "e e e\n"
            "e a d\n"
            "Visible symbols: passage marker, empty, wall\n"
            "Front symbol: e"
        )

        self.assertIn(bad_case, text)

    def test_contact_replay_names_contact_scenarios_and_results(self):
        text = run_larger_sandbox_human_replay(mode="contact")

        self.assertIn("Mode: contact", text)
        self.assertIn("doorway_d", text)
        self.assertIn("item_i", text)
        self.assertIn("exit_g", text)
        self.assertIn("Front symbol: d", text)
        self.assertIn("Front symbol: i", text)
        self.assertIn("Front symbol: g", text)
        self.assertIn("Result: moved", text)
        self.assertIn("Result: item_contact", text)
        self.assertIn("Result: exit_contact", text)
        self.assertIn("passage_crossed", text)
        self.assertIn("item_contact", text)
        self.assertIn("exit_contact", text)

    def test_replay_boundary_is_readability_only(self):
        text = run_larger_sandbox_human_replay()

        self.assertIn("Boundary:", text)
        self.assertIn("Readability replay only.", text)
        self.assertIn("No runtime behavior changed.", text)
        self.assertIn("No action selection changed.", text)
        self.assertIn("No pathfinding.", text)
        self.assertIn("No item collection.", text)
        self.assertIn("No exit activation.", text)
        self.assertIn("No curiosity.", text)
        self.assertIn("No prediction error.", text)
        self.assertIn("No place memory.", text)
        self.assertIn("No home sandbox.", text)
        self.assertIn("No visual understanding claim.", text)

    def test_observed_map_replay_is_readability_only_plain_text(self):
        text = run_larger_sandbox_human_replay(mode="observed-map")

        self.assertIn("Mode: observed-map", text)
        self.assertIn("Observed Map Steps:", text)
        self.assertIn("doorway_d", text)
        self.assertIn("item_i", text)
        self.assertIn("exit_g", text)
        self.assertIn("Observed Map Summary:", text)
        self.assertIn("Boundary:", text)
        self.assertFalse(text.lstrip().startswith("{"))

    def test_cli_helper_returns_plain_text(self):
        text = run_cli_helper(mode="contact")

        self.assertIsInstance(text, str)
        self.assertIn("Larger Sandbox Human Replay", text)
        self.assertFalse(text.lstrip().startswith("{"))

    def test_cli_command_outputs_plain_text_not_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "replay-larger-sandbox-human",
                "--mode",
                "contact",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        stdout = completed.stdout
        self.assertIn("Larger Sandbox Human Replay", stdout)
        self.assertIn("Mode: contact", stdout)
        self.assertFalse(stdout.lstrip().startswith("{"))
        with self.assertRaises(json.JSONDecodeError):
            json.loads(stdout)

    def test_replay_does_not_modify_larger_sandbox_demo_behavior(self):
        before = run_simulated_vision_larger_sandbox_demo()
        run_larger_sandbox_human_replay()
        after = run_simulated_vision_larger_sandbox_demo()

        self.assertEqual(after["action_trace"], before["action_trace"])
        self.assertEqual(after["boundary_check"], before["boundary_check"])
        self.assertEqual(after["action_trace"][3]["result"], "moved")

    def test_unsupported_mode_raises_value_error(self):
        with self.assertRaises(ValueError):
            run_larger_sandbox_human_replay(mode="route")


if __name__ == "__main__":
    unittest.main()
