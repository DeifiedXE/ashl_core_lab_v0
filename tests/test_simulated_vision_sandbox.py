import json
import subprocess
import sys
import unittest

from ashl_core.simulated_vision_sandbox import (
    ALLOWED_VIEWPORT_SYMBOLS,
    apply_simulated_vision_action,
    build_initial_simulated_vision_state,
    create_simulated_vision_room,
    look,
    render_viewport,
    run_simulated_vision_viewport_demo,
    turn_left,
    turn_right,
    validate_simulated_vision_action,
)
from ashl_core.teaching_cli import run_simulated_vision_viewport_demo as run_cli_helper


class SimulatedVisionSandboxTests(unittest.TestCase):
    def test_initial_state_is_north_facing(self):
        level = create_simulated_vision_room()
        state = build_initial_simulated_vision_state(level)

        self.assertEqual(level["level_id"], "simulated_vision_room_v0")
        self.assertEqual(state["pos"], (3, 3))
        self.assertEqual(state["facing"], "north")

    def test_turn_left_and_right(self):
        self.assertEqual(turn_left("north"), "west")
        self.assertEqual(turn_left("west"), "south")
        self.assertEqual(turn_right("north"), "east")
        self.assertEqual(turn_right("east"), "south")

    def test_turning_does_not_change_position(self):
        level = create_simulated_vision_room()
        state = build_initial_simulated_vision_state(level)

        result = apply_simulated_vision_action(state, level, "turn_right")

        self.assertEqual(result["state"]["pos"], (3, 3))
        self.assertEqual(result["state"]["facing"], "east")
        self.assertEqual(result["trace"]["result"], "turned")
        self.assertEqual(result["trace"]["failure_reasons"], [])

    def test_look_returns_viewport_and_visible_symbols(self):
        level = create_simulated_vision_room()
        state = build_initial_simulated_vision_state(level)

        observation = look(state, level)

        self.assertEqual(observation["pos"], [3, 3])
        self.assertEqual(observation["facing"], "north")
        self.assertEqual(len(observation["viewport"]), 3)
        self.assertEqual(len(observation["viewport"][0]), 3)
        self.assertIn("a", observation["visible_symbols"])

    def test_viewport_contains_only_allowed_symbols(self):
        level = create_simulated_vision_room()
        state = build_initial_simulated_vision_state(level)

        viewport = render_viewport(state, level)
        symbols = {symbol for row in viewport for symbol in row}

        self.assertTrue(symbols <= ALLOWED_VIEWPORT_SYMBOLS)

    def test_viewport_renders_wall_empty_item_and_out_of_view(self):
        level = create_simulated_vision_room()

        wall_state = {"level_id": level["level_id"], "pos": (3, 1), "facing": "north", "tick": 0}
        item_state = {"level_id": level["level_id"], "pos": (3, 1), "facing": "east", "tick": 0}
        edge_state = {"level_id": level["level_id"], "pos": (0, 0), "facing": "north", "tick": 0}

        self.assertIn("w", {symbol for row in render_viewport(wall_state, level) for symbol in row})
        self.assertIn("e", {symbol for row in render_viewport(wall_state, level) for symbol in row})
        self.assertIn("i", {symbol for row in render_viewport(item_state, level) for symbol in row})
        self.assertIn("x", {symbol for row in render_viewport(edge_state, level) for symbol in row})

    def test_move_forward_updates_position_when_walkable(self):
        level = create_simulated_vision_room()
        state = build_initial_simulated_vision_state(level)

        result = apply_simulated_vision_action(state, level, "move_forward")

        self.assertEqual(result["state"]["pos"], (3, 2))
        self.assertEqual(result["trace"]["result"], "moved")
        self.assertEqual(result["trace"]["failure_reasons"], [])

    def test_move_forward_blocks_on_wall(self):
        level = create_simulated_vision_room()
        state = {"level_id": level["level_id"], "pos": (3, 1), "facing": "north", "tick": 0}

        result = apply_simulated_vision_action(state, level, "move_forward")

        self.assertEqual(result["state"]["pos"], (3, 1))
        self.assertEqual(result["trace"]["result"], "blocked")
        self.assertEqual(result["trace"]["failure_reasons"], ["wall_blocked"])

    def test_move_forward_onto_item_reports_item_contact(self):
        level = create_simulated_vision_room()
        state = {"level_id": level["level_id"], "pos": (4, 2), "facing": "north", "tick": 0}

        result = apply_simulated_vision_action(state, level, "move_forward")

        self.assertEqual(result["state"]["pos"], (4, 1))
        self.assertEqual(result["trace"]["result"], "item_contact")
        self.assertEqual(result["trace"]["failure_reasons"], [])

    def test_invalid_action_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_simulated_vision_action("move_up")
        with self.assertRaises(ValueError):
            apply_simulated_vision_action(
                build_initial_simulated_vision_state(),
                create_simulated_vision_room(),
                "move_up",
            )

    def test_demo_runs_with_boundary_check(self):
        result = run_simulated_vision_viewport_demo()
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-simulated-vision-viewport-demo")
        self.assertEqual(result["flow"], "simulated_vision_facing_viewport_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["initial_state"], {"pos": [3, 3], "facing": "north"})
        self.assertEqual(len(result["action_trace"]), 7)
        self.assertIs(boundary["simulated_vision_only"], True)
        self.assertIs(boundary["real_image_vision"], False)
        self.assertIs(boundary["pathfinding_used"], False)
        self.assertIs(boundary["llm_vision_used"], False)
        self.assertIs(boundary["session_memory_write"], False)

    def test_cli_helper_accepts_action_sequence(self):
        result = run_cli_helper(action_sequence=["look", "turn_right", "move_forward"])

        self.assertEqual(len(result["action_trace"]), 3)
        self.assertEqual(result["final_state"], {"pos": [4, 3], "facing": "east"})

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-simulated-vision-viewport-demo",
                "--action-sequence",
                "look,turn_right,move_forward",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-simulated-vision-viewport-demo")
        self.assertEqual(result["final_state"], {"pos": [4, 3], "facing": "east"})
        self.assertIs(result["boundary_check"]["full_map_visible_to_agent"], False)


if __name__ == "__main__":
    unittest.main()
