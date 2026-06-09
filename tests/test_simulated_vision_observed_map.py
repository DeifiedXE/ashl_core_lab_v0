import json
import subprocess
import sys
import unittest

from ashl_core.simulated_vision_observed_map import (
    create_observed_local_map,
    iter_viewport_world_symbols,
    render_observed_local_map,
    run_simulated_vision_observed_map_demo,
    symbol_for_world_cell_in_viewport,
    update_observed_map_from_viewport,
)
from ashl_core.teaching_cli import run_simulated_vision_observed_map_demo as run_cli_helper


class SimulatedVisionObservedMapTests(unittest.TestCase):
    def test_observed_map_starts_empty(self):
        observed_map = create_observed_local_map("simulated_vision_room_v0")

        self.assertEqual(observed_map["known_cells"], {})
        self.assertEqual(observed_map["tick"], 0)

    def test_look_increases_known_cell_count(self):
        observed_map = create_observed_local_map("simulated_vision_room_v0")
        state = {"level_id": "simulated_vision_room_v0", "pos": (3, 3), "facing": "north", "tick": 1}
        viewport = [["e", "e", "e"], ["e", "a", "e"], ["e", "e", "e"]]

        update = update_observed_map_from_viewport(observed_map, state, viewport)

        self.assertEqual(update["known_cell_count_before"], 0)
        self.assertEqual(update["known_cell_count_after"], 9)

    def test_viewport_symbols_map_to_world_coordinates(self):
        state = {"level_id": "simulated_vision_room_v0", "pos": (3, 3), "facing": "north", "tick": 1}
        viewport = [["w", "e", "i"], ["e", "a", "e"], ["e", "e", "e"]]

        mapped = dict(iter_viewport_world_symbols(state, viewport))

        self.assertEqual(mapped[(2, 2)], "w")
        self.assertEqual(mapped[(3, 2)], "e")
        self.assertEqual(mapped[(4, 2)], "i")
        self.assertEqual(mapped[(3, 3)], "a")

    def test_x_does_not_erase_known_cell(self):
        observed_map = create_observed_local_map("simulated_vision_room_v0")
        state = {"level_id": "simulated_vision_room_v0", "pos": (3, 3), "facing": "north", "tick": 1}
        update_observed_map_from_viewport(observed_map, state, [["e", "e", "e"], ["e", "a", "e"], ["e", "e", "e"]])

        update_observed_map_from_viewport(observed_map, state, [["x", "x", "x"], ["x", "a", "x"], ["x", "x", "x"]])

        self.assertEqual(observed_map["known_cells"]["(3,2)"], "e")

    def test_turning_changes_viewport_but_preserves_observed_cells(self):
        result = run_simulated_vision_observed_map_demo(
            action_sequence=["look", "turn_right", "look"],
        )

        self.assertEqual(result["observed_map_trace"][0]["known_cell_count_after"], 9)
        self.assertGreaterEqual(result["observed_map_trace"][2]["known_cell_count_after"], 9)
        self.assertIn(
            {"pos": [3, 2], "symbol": "e"},
            result["observed_map_trace"][2]["observed_local_map"]["known_cells"],
        )

    def test_unseen_cells_are_not_inferred(self):
        result = run_simulated_vision_observed_map_demo(action_sequence=["look"])
        known_positions = {
            tuple(cell["pos"]) for cell in result["observed_map_trace"][-1]["observed_local_map"]["known_cells"]
        }

        self.assertNotIn((0, 0), known_positions)
        self.assertEqual(result["observed_map_trace"][-1]["known_cell_count_after"], 9)

    def test_observed_map_can_remember_item_after_it_leaves_viewport(self):
        result = run_simulated_vision_observed_map_demo(
            action_sequence=["move_forward", "move_forward", "turn_right", "look"],
        )
        final_known_cells = result["observed_map_trace"][-1]["observed_local_map"]["known_cells"]

        self.assertIn({"pos": [4, 1], "symbol": "i"}, final_known_cells)

    def test_agent_marker_does_not_permanently_overwrite_known_cell(self):
        observed_map = create_observed_local_map("simulated_vision_room_v0")
        state = {"level_id": "simulated_vision_room_v0", "pos": (3, 3), "facing": "north", "tick": 1}

        update_observed_map_from_viewport(observed_map, state, [["e", "e", "e"], ["e", "a", "e"], ["e", "e", "e"]])

        self.assertEqual(observed_map["known_cells"]["(3,3)"], "e")
        self.assertIn("a", "".join(render_observed_local_map(observed_map)))

    def test_symbol_for_world_cell_returns_x_when_not_currently_visible(self):
        state = {"level_id": "simulated_vision_room_v0", "pos": (4, 3), "facing": "north", "tick": 1}
        viewport = [["e", "e", "e"], ["e", "a", "e"], ["e", "e", "e"]]

        self.assertEqual(symbol_for_world_cell_in_viewport((2, 2), state, viewport), "x")

    def test_demo_runs_with_persistence_check(self):
        result = run_simulated_vision_observed_map_demo()
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-simulated-vision-observed-map-demo")
        self.assertEqual(result["flow"], "simulated_vision_observed_local_map_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["action_trace"]), len(result["observed_map_trace"]))
        self.assertTrue(result["persistence_check"]["passed"])
        self.assertIs(boundary["observed_local_map_enabled"], True)
        self.assertIs(boundary["x_does_not_erase_known_cells"], True)
        self.assertIs(boundary["unseen_cells_not_inferred"], True)
        self.assertIs(boundary["action_selection_modified"], False)
        self.assertIs(boundary["pathfinding_used"], False)
        self.assertIs(boundary["llm_vision_used"], False)
        self.assertIs(boundary["session_memory_write"], False)

    def test_cli_helper_accepts_action_sequence(self):
        result = run_cli_helper(action_sequence=["look", "turn_right", "look"])

        self.assertEqual(len(result["action_trace"]), 3)
        self.assertEqual(len(result["observed_map_trace"]), 3)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-simulated-vision-observed-map-demo",
                "--action-sequence",
                "look,turn_right,look",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-simulated-vision-observed-map-demo")
        self.assertEqual(len(result["observed_map_trace"]), 3)
        self.assertIs(result["boundary_check"]["observed_local_map_enabled"], True)


if __name__ == "__main__":
    unittest.main()
