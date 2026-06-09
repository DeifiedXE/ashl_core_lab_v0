import json
import subprocess
import sys
import unittest

from ashl_core.session_working_memory import build_state_snapshot_key
from ashl_core.simulated_vision_memory_bridge import run_simulated_vision_memory_bridge_demo
from ashl_core.teaching_cli import run_simulated_vision_memory_bridge_demo as run_cli_helper


class SimulatedVisionMemoryBridgeTests(unittest.TestCase):
    def test_demo_runs_and_records_each_action(self):
        result = run_simulated_vision_memory_bridge_demo()

        self.assertEqual(result["command"], "run-simulated-vision-memory-bridge-demo")
        self.assertEqual(result["flow"], "simulated_vision_session_memory_bridge_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["level_id"], "simulated_vision_room_v0")
        self.assertEqual(len(result["memory_records"]), len(result["action_trace"]))
        self.assertEqual(result["query_summary"]["record_count_before_clear"], len(result["action_trace"]))
        self.assertEqual(result["clear_summary"], {"cleared": True, "record_count_after_clear": 0})

    def test_memory_records_have_state_key_viewport_and_visible_symbols(self):
        result = run_simulated_vision_memory_bridge_demo()

        for record in result["memory_records"]:
            self.assertTrue(record["state_key"])
            self.assertIn("viewport", record["state_snapshot"])
            self.assertIn("visible_symbols", record["state_snapshot"])
            self.assertIn("viewport", record["metadata"])
            self.assertIn("visible_symbols", record["metadata"])
            self.assertEqual(record["metadata"]["source"], "simulated_vision_memory_bridge_v0")

    def test_memory_records_corrected_first_person_viewport(self):
        result = run_simulated_vision_memory_bridge_demo(action_sequence=["look"])
        viewport = result["memory_records"][0]["state_snapshot"]["viewport"]

        self.assertEqual(viewport[2][1], "a")
        self.assertNotEqual(viewport[1][1], "a")

    def test_vision_state_key_includes_facing_without_breaking_non_vision_key(self):
        vision_snapshot = {"level_id": "simulated_vision_room_v0", "agent_pos": [3, 3], "facing": "north"}
        non_vision_snapshot = {"level_id": "demo", "agent_pos": [1, 1]}

        self.assertEqual(
            build_state_snapshot_key(vision_snapshot),
            "level=simulated_vision_room_v0|agent=(3,3)|facing=north|box=null|goal=null",
        )
        self.assertEqual(
            build_state_snapshot_key(non_vision_snapshot),
            "level=demo|agent=(1,1)|box=null|goal=null",
        )

    def test_required_action_records_exist(self):
        result = run_simulated_vision_memory_bridge_demo()
        actions = [record["action"] for record in result["memory_records"]]

        self.assertIn("look", actions)
        self.assertIn("turn_right", actions)
        self.assertIn("move_forward", actions)

    def test_query_summary_counts_actions_and_visible_symbols(self):
        result = run_simulated_vision_memory_bridge_demo()
        query_summary = result["query_summary"]

        self.assertEqual(query_summary["query_by_action_look_count"], 4)
        self.assertEqual(query_summary["query_by_action_turn_right_count"], 1)
        self.assertEqual(query_summary["query_by_action_move_forward_count"], 1)
        self.assertGreaterEqual(query_summary["query_by_visible_symbol_i_count"], 0)
        self.assertIn("query_by_visible_symbol_w_count", query_summary)
        self.assertGreaterEqual(query_summary["query_by_state_key_count"], 1)

    def test_blocked_move_records_wall_blocked(self):
        result = run_simulated_vision_memory_bridge_demo(
            action_sequence=["move_forward", "move_forward", "move_forward"],
        )
        blocked_records = [
            record for record in result["memory_records"] if record["outcome_type"] == "blocked"
        ]

        self.assertEqual(len(blocked_records), 1)
        self.assertEqual(blocked_records[0]["failure_reasons"], ["wall_blocked"])
        self.assertEqual(blocked_records[0]["metadata"]["blocked_at"], [3, 0])
        self.assertEqual(result["query_summary"]["query_by_outcome_type_blocked_count"], 1)
        self.assertEqual(result["query_summary"]["query_by_failure_reason_wall_blocked_count"], 1)

    def test_boundary_check(self):
        boundary = run_simulated_vision_memory_bridge_demo()["boundary_check"]

        self.assertIs(boundary["session_memory_write"], True)
        self.assertIs(boundary["session_memory_cleared"], True)
        self.assertIs(boundary["first_person_viewport"], True)
        self.assertEqual(boundary["agent_viewport_position"], [2, 1])
        self.assertEqual(boundary["front_symbol_position"], [1, 1])
        self.assertIs(boundary["centered_top_down_viewport"], False)
        self.assertIs(boundary["real_image_vision"], False)
        self.assertIs(boundary["llm_vision_used"], False)
        self.assertIs(boundary["pathfinding_used"], False)
        self.assertIs(boundary["action_selection_modified"], False)
        self.assertIs(boundary["visual_understanding_claimed"], False)
        self.assertIs(boundary["symbol_grounding_claimed"], False)

    def test_cli_helper_accepts_action_sequence_and_max_records(self):
        result = run_cli_helper(
            action_sequence=["look", "turn_right", "look", "move_forward", "look"],
            max_records=20,
        )

        self.assertEqual(result["max_records"], 20)
        self.assertEqual(len(result["action_trace"]), 5)
        self.assertEqual(len(result["memory_records"]), 5)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-simulated-vision-memory-bridge-demo",
                "--action-sequence",
                "look,turn_right,look,move_forward,look",
                "--max-records",
                "20",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-simulated-vision-memory-bridge-demo")
        self.assertEqual(len(result["memory_records"]), 5)
        self.assertIs(result["boundary_check"]["session_memory_write"], True)


if __name__ == "__main__":
    unittest.main()
