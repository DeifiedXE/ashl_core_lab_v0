import json
import subprocess
import sys
import unittest

from ashl_core.simulated_vision_larger_sandbox import (
    ALLOWED_LARGER_VIEWPORT_SYMBOLS,
    apply_larger_sandbox_action,
    build_initial_larger_sandbox_state,
    build_larger_sandbox_map_summary,
    create_simulated_vision_larger_sandbox,
    render_larger_sandbox_viewport,
    run_simulated_vision_larger_sandbox_demo,
    symbol_at_larger_sandbox,
)
from ashl_core.teaching_cli import run_simulated_vision_larger_sandbox_demo as run_cli_helper


class SimulatedVisionLargerSandboxTests(unittest.TestCase):
    def test_level_id_map_dimensions_and_counts(self):
        level = create_simulated_vision_larger_sandbox()
        summary = build_larger_sandbox_map_summary(level)

        self.assertEqual(level["level_id"], "simulated_vision_larger_sandbox_v0")
        self.assertEqual(summary["width"], 12)
        self.assertEqual(summary["height"], 9)
        self.assertEqual(summary["agent_start"], [2, 2])
        self.assertEqual(summary["initial_facing"], "north")
        self.assertEqual(summary["item_count"], 4)
        self.assertEqual(summary["doorway_count"], 2)
        self.assertEqual(summary["exit_count"], 1)
        self.assertEqual(summary["unsupported_symbols"], [])

    def test_initial_state_and_first_person_viewport(self):
        level = create_simulated_vision_larger_sandbox()
        state = build_initial_larger_sandbox_state(level)

        viewport = render_larger_sandbox_viewport(state, level)

        self.assertEqual(state["pos"], (2, 2))
        self.assertEqual(state["facing"], "north")
        self.assertEqual(viewport[2][1], "a")
        self.assertNotEqual(viewport[1][1], "a")
        self.assertTrue({symbol for row in viewport for symbol in row} <= ALLOWED_LARGER_VIEWPORT_SYMBOLS)

    def test_doorway_renders_as_d_when_visible(self):
        level = create_simulated_vision_larger_sandbox()
        state = {"level_id": level["level_id"], "pos": (2, 2), "facing": "east", "tick": 0}

        viewport = render_larger_sandbox_viewport(state, level)

        self.assertIn("d", {symbol for row in viewport for symbol in row})
        self.assertEqual(viewport[0][1], "d")

    def test_exit_renders_as_g_when_visible(self):
        level = create_simulated_vision_larger_sandbox()
        state = {"level_id": level["level_id"], "pos": (10, 7), "facing": "east", "tick": 0}

        viewport = render_larger_sandbox_viewport(state, level)

        self.assertEqual(viewport[1][1], "g")

    def test_symbol_rules(self):
        level = create_simulated_vision_larger_sandbox()

        self.assertEqual(symbol_at_larger_sandbox(level, (0, 0)), "w")
        self.assertEqual(symbol_at_larger_sandbox(level, (1, 1)), "e")
        self.assertEqual(symbol_at_larger_sandbox(level, (8, 1)), "i")
        self.assertEqual(symbol_at_larger_sandbox(level, (4, 2)), "d")
        self.assertEqual(symbol_at_larger_sandbox(level, (11, 7)), "g")
        self.assertEqual(symbol_at_larger_sandbox(level, (12, 7)), "x")

    def test_wall_blocks_empty_moves_and_doorway_crosses(self):
        level = create_simulated_vision_larger_sandbox()
        wall_state = {"level_id": level["level_id"], "pos": (2, 1), "facing": "north", "tick": 0}
        empty_state = {"level_id": level["level_id"], "pos": (2, 2), "facing": "east", "tick": 0}
        doorway_state = {"level_id": level["level_id"], "pos": (3, 2), "facing": "east", "tick": 0}

        blocked = apply_larger_sandbox_action(wall_state, level, "move_forward")
        moved = apply_larger_sandbox_action(empty_state, level, "move_forward")
        doorway = apply_larger_sandbox_action(doorway_state, level, "move_forward")

        self.assertEqual(blocked["trace"]["front_symbol"], "w")
        self.assertEqual(blocked["trace"]["result"], "blocked")
        self.assertEqual(blocked["trace"]["failure_reasons"], ["wall_blocked"])
        self.assertEqual(blocked["state"]["pos"], (2, 1))
        self.assertEqual(moved["trace"]["front_symbol"], "e")
        self.assertEqual(moved["trace"]["result"], "moved")
        self.assertEqual(moved["state"]["pos"], (3, 2))
        self.assertEqual(doorway["trace"]["front_symbol"], "d")
        self.assertEqual(doorway["trace"]["result"], "moved")
        self.assertEqual(doorway["trace"]["effect_tags"], ["passage_crossed"])
        self.assertEqual(doorway["state"]["pos"], (4, 2))

    def test_item_and_exit_contact(self):
        level = create_simulated_vision_larger_sandbox()
        item_state = {"level_id": level["level_id"], "pos": (8, 2), "facing": "north", "tick": 0}
        exit_state = {"level_id": level["level_id"], "pos": (10, 7), "facing": "east", "tick": 0}

        item = apply_larger_sandbox_action(item_state, level, "move_forward")
        exit_result = apply_larger_sandbox_action(exit_state, level, "move_forward")

        self.assertEqual(item["trace"]["front_symbol"], "i")
        self.assertEqual(item["trace"]["result"], "item_contact")
        self.assertEqual(item["trace"]["effect_tags"], ["item_contact"])
        self.assertEqual(item["state"]["pos"], (8, 1))
        self.assertEqual(exit_result["trace"]["front_symbol"], "g")
        self.assertEqual(exit_result["trace"]["result"], "exit_contact")
        self.assertEqual(exit_result["trace"]["effect_tags"], ["exit_contact"])
        self.assertEqual(exit_result["state"]["pos"], (11, 7))

    def test_demo_runs_with_boundary_check(self):
        result = run_simulated_vision_larger_sandbox_demo()
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-simulated-vision-larger-sandbox-demo")
        self.assertEqual(result["flow"], "simulated_vision_larger_sandbox_static_runtime_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["map_summary"]["item_count"], 4)
        self.assertEqual(result["map_summary"]["doorway_count"], 2)
        self.assertEqual(result["map_summary"]["exit_count"], 1)
        self.assertEqual(len(result["action_trace"]), 7)
        self.assertIs(boundary["larger_static_sandbox_enabled"], True)
        self.assertIs(boundary["doorway_symbol_supported"], True)
        self.assertIs(boundary["doorway_passable"], True)
        self.assertIs(boundary["doorway_semantic_boundary_given_to_agent"], False)
        self.assertIs(boundary["exit_placeholder_supported"], True)
        self.assertIs(boundary["exit_conditional_spawn_enabled"], False)
        self.assertIs(boundary["task_completion_enabled"], False)
        self.assertIs(boundary["item_collection_enabled"], False)
        self.assertIs(boundary["curiosity_enabled"], False)
        self.assertIs(boundary["prediction_error_enabled"], False)
        self.assertIs(boundary["pathfinding_used"], False)
        self.assertIs(boundary["long_term_memory_write"], False)

    def test_cli_helper_accepts_action_sequence(self):
        result = run_cli_helper(action_sequence=["look", "turn_right", "look"])

        self.assertEqual(len(result["action_trace"]), 3)
        self.assertEqual(result["final_state"], {"pos": [2, 2], "facing": "east"})

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-simulated-vision-larger-sandbox-demo",
                "--action-sequence",
                "look,turn_right,look",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-simulated-vision-larger-sandbox-demo")
        self.assertEqual(result["final_state"], {"pos": [2, 2], "facing": "east"})
        self.assertIs(result["boundary_check"]["larger_static_sandbox_enabled"], True)


if __name__ == "__main__":
    unittest.main()
