import json
import subprocess
import sys
import unittest

from ashl_core.session_working_memory import (
    SUPPORTED_OUTCOME_TYPES,
    append_outcome_record,
    build_session_outcome_record,
    build_state_snapshot_key,
    clear_session_working_memory,
    create_session_working_memory,
    query_recent_outcomes,
)
from ashl_core.teaching_cli import demo_session_working_memory_cli


class SessionWorkingMemoryTests(unittest.TestCase):
    def test_create_empty_session_working_memory(self):
        memory = create_session_working_memory(max_records=20)

        self.assertEqual(memory["type"], "session_working_memory")
        self.assertEqual(memory["scope"], "session_local")
        self.assertEqual(memory["max_records"], 20)
        self.assertEqual(memory["records"], [])
        self.assertTrue(memory["boundary"]["session_local_only"])
        self.assertTrue(memory["boundary"]["state_key_generated"])
        self.assertTrue(memory["boundary"]["state_key_deterministic"])
        self.assertFalse(memory["boundary"]["persistent_memory_write"])

    def test_build_state_snapshot_key_is_deterministic(self):
        snapshot = {"level_id": "demo", "agent_pos": [4, 2], "box_pos": [4, 4]}

        self.assertEqual(build_state_snapshot_key(snapshot), build_state_snapshot_key(snapshot))

    def test_build_state_snapshot_key_ignores_dict_order(self):
        first = {"level_id": "demo", "agent_pos": [4, 2], "box_pos": [4, 4]}
        second = {"box_pos": [4, 4], "agent_pos": [4, 2], "level_id": "demo"}

        self.assertEqual(build_state_snapshot_key(first), build_state_snapshot_key(second))

    def test_build_state_snapshot_key_handles_missing_optional_fields(self):
        self.assertEqual(
            build_state_snapshot_key({"level_id": "demo", "agent_pos": [1, 1]}),
            "level=demo|agent=(1,1)|box=null|goal=null",
        )

    def test_build_state_snapshot_key_handles_empty_snapshot(self):
        self.assertEqual(build_state_snapshot_key({}), "unknown_state")

    def test_append_moved_outcome(self):
        memory = create_session_working_memory()
        record = build_session_outcome_record(
            tick=1,
            state_snapshot={"agent_pos": [1, 1], "level_id": "demo"},
            action="move_right",
            outcome_type="moved",
        )

        append_outcome_record(memory, record)

        self.assertEqual(memory["records"], [record])
        self.assertEqual(memory["records"][0]["state_key"], "level=demo|agent=(1,1)|box=null|goal=null")
        self.assertEqual(memory["records"][0]["failure_reasons"], [])

    def test_append_generates_state_key_when_missing(self):
        memory = create_session_working_memory()
        record = {
            "tick": 1,
            "state_key": None,
            "state_snapshot": {"level_id": "demo", "agent_pos": [2, 3]},
            "action": "move_right",
            "target": None,
            "outcome_type": "moved",
            "outcome_detail": None,
            "failure_reasons": [],
            "effect_tags": [],
            "metadata": {},
        }

        append_outcome_record(memory, record)

        self.assertEqual(memory["records"][0]["state_key"], "level=demo|agent=(2,3)|box=null|goal=null")

    def test_provided_state_key_is_preserved(self):
        memory = create_session_working_memory()
        record = build_session_outcome_record(
            tick=1,
            state_key="custom_state_key",
            state_snapshot={"level_id": "demo", "agent_pos": [1, 1]},
            action="move_right",
            outcome_type="moved",
        )

        append_outcome_record(memory, record)

        self.assertEqual(memory["records"][0]["state_key"], "custom_state_key")

    def test_append_blocked_outcome(self):
        memory = create_session_working_memory()
        record = build_session_outcome_record(
            tick=2,
            state_snapshot={"agent_pos": [2, 1], "box_pos": [3, 1]},
            action="move_right",
            outcome_type="blocked",
            failure_reasons=["wall_blocked"],
            metadata={"blocked_at": [3, 1], "raw_result": "wall_blocked"},
        )

        append_outcome_record(memory, record)

        self.assertEqual(memory["records"][0]["outcome_type"], "blocked")
        self.assertEqual(memory["records"][0]["failure_reasons"], ["wall_blocked"])
        self.assertEqual(memory["records"][0]["metadata"]["blocked_at"], [3, 1])

    def test_append_unknown_failure_reason(self):
        memory = create_session_working_memory()
        record = build_session_outcome_record(
            tick=3,
            state_snapshot={"agent_pos": [2, 2]},
            action="wait",
            outcome_type="unknown",
            failure_reasons=["unknown"],
            metadata={"raw_result": "unknown"},
        )

        append_outcome_record(memory, record)

        self.assertEqual(memory["records"][0]["outcome_type"], "unknown")
        self.assertEqual(memory["records"][0]["failure_reasons"], ["unknown"])

    def test_append_multiple_failure_reasons(self):
        memory = create_session_working_memory()
        record = build_session_outcome_record(
            tick=4,
            state_snapshot={"agent_pos": [4, 2], "box_pos": [4, 4]},
            action="move_down",
            outcome_type="blocked",
            failure_reasons=["wall_blocked", "no_progress"],
            metadata={"blocked_at": [4, 3]},
        )

        append_outcome_record(memory, record)

        self.assertEqual(memory["records"][0]["failure_reasons"], ["wall_blocked", "no_progress"])

    def test_failure_reasons_must_be_list(self):
        with self.assertRaises(TypeError):
            build_session_outcome_record(
                tick=5,
                state_snapshot={"agent_pos": [1, 1]},
                action="move_up",
                outcome_type="blocked",
                failure_reasons="wall_blocked",
            )

    def test_query_by_action(self):
        memory = create_session_working_memory()
        append_outcome_record(
            memory,
            build_session_outcome_record(
                tick=1,
                state_snapshot={"agent_pos": [1, 1]},
                action="move_right",
                outcome_type="moved",
            ),
        )
        append_outcome_record(
            memory,
            build_session_outcome_record(
                tick=2,
                state_snapshot={"agent_pos": [2, 1]},
                action="move_down",
                outcome_type="blocked",
                failure_reasons=["wall_blocked"],
            ),
        )

        results = query_recent_outcomes(memory, action="move_down")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["action"], "move_down")

    def test_query_by_outcome_type(self):
        memory = create_session_working_memory()
        append_outcome_record(
            memory,
            build_session_outcome_record(
                tick=1,
                state_snapshot={"agent_pos": [1, 1]},
                action="move_right",
                outcome_type="moved",
            ),
        )
        append_outcome_record(
            memory,
            build_session_outcome_record(
                tick=2,
                state_snapshot={"agent_pos": [2, 1]},
                action="move_down",
                outcome_type="blocked",
                failure_reasons=["wall_blocked"],
            ),
        )

        results = query_recent_outcomes(memory, outcome_type="blocked")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["outcome_type"], "blocked")

    def test_query_by_state_and_action(self):
        memory = create_session_working_memory()
        state = {"agent_pos": [1, 1], "box_pos": [2, 2], "level_id": "demo"}
        append_outcome_record(
            memory,
            build_session_outcome_record(
                tick=1,
                state_snapshot=state,
                action="move_right",
                outcome_type="moved",
            ),
        )

        results = query_recent_outcomes(memory, state_snapshot=state, action="move_right")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["state_snapshot"], state)

    def test_query_by_state_key_and_action(self):
        memory = create_session_working_memory()
        state = {"agent_pos": [4, 2], "box_pos": [4, 4], "level_id": "demo"}
        state_key = build_state_snapshot_key(state)
        append_outcome_record(
            memory,
            build_session_outcome_record(
                tick=1,
                state_snapshot=state,
                action="move_down",
                outcome_type="blocked",
                failure_reasons=["wall_blocked"],
            ),
        )

        by_state_key = query_recent_outcomes(memory, state_key=state_key)
        by_state_key_action = query_recent_outcomes(memory, state_key=state_key, action="move_down")

        self.assertEqual(len(by_state_key), 1)
        self.assertEqual(len(by_state_key_action), 1)
        self.assertEqual(by_state_key_action[0]["action"], "move_down")

    def test_max_records_drops_oldest_record(self):
        memory = create_session_working_memory(max_records=2)
        for tick in range(3):
            append_outcome_record(
                memory,
                build_session_outcome_record(
                    tick=tick,
                    state_snapshot={"agent_pos": [tick, 0]},
                    action="move_right",
                    outcome_type="moved",
                ),
            )

        self.assertEqual([record["tick"] for record in memory["records"]], [1, 2])

    def test_clear_memory_removes_records(self):
        memory = create_session_working_memory()
        append_outcome_record(
            memory,
            build_session_outcome_record(
                tick=1,
                state_snapshot={"agent_pos": [1, 1]},
                action="move_right",
                outcome_type="moved",
            ),
        )

        clear_session_working_memory(memory)

        self.assertEqual(memory["records"], [])

    def test_does_not_write_lesson_store_or_memory_layer(self):
        memory = create_session_working_memory()
        boundary = memory["boundary"]

        self.assertFalse(boundary["persistent_memory_write"])
        self.assertFalse(boundary["lesson_store_write"])
        self.assertFalse(boundary["memory_layer_write"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["used_llm"])
        self.assertFalse(boundary["used_pathfinding"])

    def test_does_not_persist_across_new_memory_instance(self):
        first = create_session_working_memory()
        second = create_session_working_memory()
        append_outcome_record(
            first,
            build_session_outcome_record(
                tick=1,
                state_snapshot={"agent_pos": [1, 1]},
                action="move_right",
                outcome_type="moved",
            ),
        )

        self.assertEqual(len(first["records"]), 1)
        self.assertEqual(second["records"], [])

    def test_supported_outcome_types_are_generic(self):
        self.assertTrue(
            {
                "moved",
                "blocked",
                "no_progress",
                "entered_trap",
                "goal_progress",
                "goal_reached",
                "unknown",
            }.issubset(SUPPORTED_OUTCOME_TYPES)
        )
        self.assertNotIn("wall_memory", SUPPORTED_OUTCOME_TYPES)
        self.assertNotIn("dead_end_memory", SUPPORTED_OUTCOME_TYPES)

    def test_demo_cli_handler_returns_boundary_and_queries(self):
        result = demo_session_working_memory_cli(max_records=20)

        self.assertEqual(result["command"], "demo-session-working-memory")
        self.assertEqual(result["flow"], "session_working_memory_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["max_records"], 20)
        self.assertTrue(result["failure_reasons_supports_list"])
        self.assertTrue(result["unknown_failure_supported"])
        self.assertTrue(result["multiple_failure_reasons_supported"])
        self.assertFalse(result["persistent_write"])
        self.assertEqual(result["demo"]["query_by_action_count"], 2)
        self.assertEqual(result["demo"]["query_by_outcome_type_count"], 2)
        self.assertEqual(result["demo"]["query_by_state_action_count"], 1)
        self.assertEqual(result["demo"]["query_by_state_key_count"], 1)
        self.assertEqual(result["demo"]["query_by_state_key_action_count"], 1)
        self.assertEqual(result["demo"]["record_count_after_clear"], 0)
        self.assertTrue(result["boundary_check"]["state_key_generated"])
        self.assertTrue(result["boundary_check"]["state_key_deterministic"])
        self.assertTrue(result["boundary_check"]["session_local_only"])
        self.assertFalse(result["boundary_check"]["lesson_store_write"])
        self.assertFalse(result["boundary_check"]["memory_layer_write"])

    def test_module_cli_demo_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "demo-session-working-memory",
                "--max-records",
                "20",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "session_working_memory_v0")
        self.assertTrue(result["failure_reasons_supports_list"])
        self.assertTrue(result["unknown_failure_supported"])
        self.assertTrue(result["multiple_failure_reasons_supported"])
        self.assertTrue(result["boundary_check"]["state_key_generated"])
        self.assertFalse(result["boundary_check"]["memory_layer_write"])
        self.assertFalse(result["boundary_check"]["used_pathfinding"])


if __name__ == "__main__":
    unittest.main()
