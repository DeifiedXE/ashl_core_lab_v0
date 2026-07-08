from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from ashl_core_v1.host_body import host_body_runtime_bridge as runtime_bridge
from ashl_core_v1.host_body import host_body_sensor_events as sensor
from ashl_core_v1.host_body import host_body_trace_history_lane as trace
from ashl_core_v1.host_body import qingyin_home_internal_space_surface as home
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_trace_history_from_guided_cradle_growth_console,
)


TRACE_CLI = "ashl_core_v1.host_body.host_body_trace_history_lane_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class HostBodyTraceHistoryLaneTests(unittest.TestCase):
    def test_trace_history_lane_plan_builds_and_blocks_forbidden_authority(self) -> None:
        port_map, home_audit, bridge_audit = self._plan_inputs()
        plan = trace.build_host_body_trace_history_lane_plan(
            host_body_port_map=port_map,
            home_surface_audit=home_audit,
            host_runtime_bridge_audit=bridge_audit,
        )
        self.assertEqual(plan.lane_plan_status, "lane_plan_created")
        self.assertTrue(plan.read_only_lane)
        self.assertTrue(plan.demo_record_only)
        self.assertTrue(plan.in_memory_only)
        self.assertIn("host_body_event", plan.allowed_source_families)
        self.assertIn("recent_n_entries", plan.allowed_query_modes)
        self.assertFalse(plan.memory_layer_write_allowed)
        self.assertFalse(plan.state_persistence_write_allowed)
        self.assertFalse(plan.file_write_allowed)
        self.assertFalse(plan.learning_candidate_creation_allowed)
        self.assertFalse(plan.action_selection_allowed)
        self.assertFalse(plan.first_output_allowed)
        self.assertFalse(plan.live_runtime_session_allowed)
        self.assertTrue(trace.validate_host_body_trace_history_lane_plan(plan)["valid"])

        blocked = {
            "missing_home": ({"home_surface_audit": None}, "blocked_missing_home_surface_audit"),
            "missing_bridge": (
                {"host_runtime_bridge_audit": None},
                "blocked_missing_host_runtime_bridge_audit",
            ),
            "memory": ({"memory_layer_write_allowed": True}, "blocked_memory_write_allowed"),
            "long": ({"long_term_memory_write_allowed": True}, "blocked_memory_write_allowed"),
            "core": ({"core_memory_write_allowed": True}, "blocked_memory_write_allowed"),
            "state": (
                {"state_persistence_write_allowed": True},
                "blocked_state_persistence_write_allowed",
            ),
            "jsonl": (
                {"retained_jsonl_write_allowed": True},
                "blocked_file_write_allowed",
            ),
            "file": ({"file_write_allowed": True}, "blocked_file_write_allowed"),
            "learning": (
                {"learning_candidate_creation_allowed": True},
                "blocked_learning_candidate_creation_allowed",
            ),
            "action": ({"action_selection_allowed": True}, "blocked_action_selection_allowed"),
            "internal_action": (
                {"internal_action_choice_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
            "first": ({"first_output_allowed": True}, "blocked_first_output_allowed"),
            "live": ({"live_runtime_session_allowed": True}, "blocked_live_runtime_allowed"),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                args = {
                    "host_body_port_map": port_map,
                    "home_surface_audit": home_audit,
                    "host_runtime_bridge_audit": bridge_audit,
                    **kwargs,
                }
                self.assertEqual(
                    trace.build_host_body_trace_history_lane_plan(**args).lane_plan_status,
                    expected_status,
                )

    def test_trace_history_entry_records_sources_and_blocks_forbidden_content(self) -> None:
        plan = self._plan()
        source_records = self._source_records()
        expected_families = {
            "host_body_event",
            "host_body_camera_event",
            "host_body_mic_event",
            "host_body_idle_event",
            "host_body_sensor_event_set",
            "host_body_runtime_bridge",
            "qingyin_home_port_surface",
            "qingyin_home_host_event_surface",
            "qingyin_home_runtime_bridge_surface",
            "qingyin_home_status_light",
            "qingyin_home_teacher_observed_surface",
            "qingyin_home_render",
        }
        entries = [
            trace.build_host_body_trace_history_entry(
                lane_plan=plan,
                sequence_index=index,
                source_record=record,
            )
            for index, record in enumerate(source_records)
        ]
        self.assertTrue(expected_families.issubset({entry.source_record_family for entry in entries}))
        self.assertTrue(all(entry.read_only_entry for entry in entries))
        self.assertTrue(all(trace.validate_host_body_trace_history_entry(entry)["valid"] for entry in entries))
        self.assertTrue(any(entry.entry_kind == "runtime_bridge_entry" for entry in entries))
        self.assertTrue(any(entry.entry_kind == "status_light_entry" for entry in entries))
        self.assertTrue(any(entry.entry_kind == "teacher_observed_entry" for entry in entries))
        self.assertTrue(any(entry.entry_kind == "render_entry" for entry in entries))

        blocked = {
            "unknown": (
                {"source_record": {}, "source_record_family": "unknown_source_family"},
                "trace_history_entry_blocked_unknown_source_family",
            ),
            "semantic": (
                {"semantic_interpretation_created": True},
                "trace_history_entry_blocked_semantic_interpretation",
            ),
            "raw_image": (
                {"entry_payload": {"raw_image_bytes": "blocked"}},
                "trace_history_entry_blocked_semantic_interpretation",
            ),
            "raw_audio": (
                {"entry_payload": {"raw_audio_bytes": "blocked"}},
                "trace_history_entry_blocked_semantic_interpretation",
            ),
            "free_output": (
                {"entry_payload": {"free_form_qingyin_output": "blocked"}},
                "trace_history_entry_blocked_semantic_interpretation",
            ),
            "action": (
                {"action_selection_influence_created": True},
                "trace_history_entry_blocked_action_selection",
            ),
            "memory": (
                {"memory_layer_write_performed": True},
                "trace_history_entry_blocked_memory_write",
            ),
            "state": (
                {"state_persistence_write_performed": True},
                "trace_history_entry_blocked_memory_write",
            ),
            "file": (
                {"file_write_performed": True},
                "trace_history_entry_blocked_file_write",
            ),
            "learning": (
                {"learning_candidate_created": True},
                "trace_history_entry_blocked_memory_write",
            ),
            "first": (
                {"first_output_created": True},
                "trace_history_entry_blocked_first_output",
            ),
            "live": (
                {"live_runtime_session_created": True},
                "trace_history_entry_blocked_live_runtime",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                args = {
                    "lane_plan": plan,
                    "sequence_index": 99,
                    "source_record": source_records[0],
                    **kwargs,
                }
                self.assertEqual(
                    trace.build_host_body_trace_history_entry(**args).entry_status,
                    expected_status,
                )

    def test_trace_history_lane_index_readback_and_render(self) -> None:
        payload = trace.build_demo_full_host_body_trace_history_lane()
        entries = [trace.HostBodyTraceHistoryEntryRecord.from_dict(item) for item in payload["trace_history_entries"]]
        lane = trace.HostBodyTraceHistoryLaneRecord.from_dict(payload["trace_history_lane"])
        index = trace.HostBodyTraceHistoryIndexRecord.from_dict(payload["trace_history_index"])
        readback = trace.HostBodyTraceHistoryReadbackRecord.from_dict(payload["trace_history_readback"])
        render = trace.HostBodyTraceHistoryRenderRecord.from_dict(payload["trace_history_render"])

        self.assertEqual(lane.lane_status, "trace_history_lane_recorded")
        self.assertEqual(lane.entry_count, len(entries))
        self.assertGreater(lane.sensor_event_entry_count, 0)
        self.assertGreater(lane.runtime_bridge_entry_count, 0)
        self.assertGreater(lane.home_surface_entry_count, 0)
        self.assertGreater(lane.status_light_entry_count, 0)
        self.assertGreater(lane.teacher_observed_entry_count, 0)
        self.assertGreater(lane.render_entry_count, 0)
        self.assertTrue(lane.entries_sorted_by_sequence)
        self.assertFalse(lane.duplicate_sequence_detected)
        self.assertIn("host_body_event", index.entries_by_source_family)
        self.assertIn("camera_frame_available", index.entries_by_event_type)
        self.assertIn("camera_port", index.entries_by_port_kind)
        self.assertIn("read_only_port_map_surface", index.entries_by_surface_kind)
        self.assertTrue(index.entries_by_bridge_status)
        self.assertEqual(readback.readback_status, "trace_history_readback_recorded")
        self.assertFalse(readback.readback_is_memory_retrieval)
        self.assertFalse(readback.readback_can_influence_action)
        self.assertEqual(render.render_status, "trace_history_render_created")
        self.assertTrue(render.read_only_render)

        duplicate = trace.build_host_body_trace_history_entry(
            lane_plan=self._plan(),
            sequence_index=0,
            source_record=self._source_records()[1],
        )
        self.assertEqual(
            trace.build_host_body_trace_history_lane(
                lane_plan=self._plan(),
                entries=(entries[0], duplicate),
            ).lane_status,
            "trace_history_lane_blocked_duplicate_sequence",
        )

        empty = trace.build_demo_empty_host_body_trace_history_lane()
        self.assertEqual(empty["trace_history_lane"]["lane_status"], "trace_history_lane_recorded_empty")
        self.assertEqual(empty["trace_history_index"]["index_status"], "trace_history_index_recorded_empty")
        self.assertEqual(empty["trace_history_render"]["render_status"], "trace_history_render_created_empty")

    def test_readback_modes_and_blocked_readback_cases(self) -> None:
        payload = trace.build_demo_full_host_body_trace_history_lane()
        entries = [trace.HostBodyTraceHistoryEntryRecord.from_dict(item) for item in payload["trace_history_entries"]]
        lane = trace.HostBodyTraceHistoryLaneRecord.from_dict(payload["trace_history_lane"])
        index = trace.HostBodyTraceHistoryIndexRecord.from_dict(payload["trace_history_index"])
        queries = {
            "recent_n_entries": {"n": 3},
            "by_source_family": {"source_family": "host_body_event"},
            "by_event_type": {"event_type": "camera_frame_available"},
            "by_surface_kind": {"surface_kind": "read_only_port_map_surface"},
            "by_bridge_status": {"bridge_status": "host_body_runtime_bridge_trace_complete"},
        }
        for mode, query in queries.items():
            with self.subTest(mode=mode):
                readback = trace.build_host_body_trace_history_readback(
                    lane=lane,
                    entries=entries,
                    index=index,
                    readback_mode=mode,
                    readback_query=query,
                )
                self.assertTrue(readback.readback_status.startswith("trace_history_readback_recorded"))
                self.assertFalse(readback.readback_is_memory_retrieval)
                self.assertFalse(readback.readback_can_influence_action)

        blocked = {
            "invalid": ({"readback_query": {"n": -1}}, "trace_history_readback_blocked_invalid_query"),
            "memory": (
                {"readback_is_memory_retrieval": True},
                "trace_history_readback_blocked_memory_retrieval_claim",
            ),
            "action": (
                {"readback_can_influence_action": True},
                "trace_history_readback_blocked_action_influence",
            ),
            "learning": (
                {"readback_can_create_learning": True},
                "trace_history_readback_blocked_learning_creation",
            ),
            "first": (
                {"readback_can_create_first_output": True},
                "trace_history_readback_blocked_first_output",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                args = {
                    "lane": lane,
                    "entries": entries,
                    "index": index,
                    "readback_mode": "recent_n_entries",
                    "readback_query": {"n": 3},
                    **kwargs,
                }
                self.assertEqual(
                    trace.build_host_body_trace_history_readback(**args).readback_status,
                    expected_status,
                )

    def test_render_modes_and_blocked_render_cases(self) -> None:
        payload = trace.build_demo_full_host_body_trace_history_lane()
        entries = [trace.HostBodyTraceHistoryEntryRecord.from_dict(item) for item in payload["trace_history_entries"]]
        lane = trace.HostBodyTraceHistoryLaneRecord.from_dict(payload["trace_history_lane"])
        for render_kind in (
            "timeline_text_render",
            "compact_table_render",
            "json_snapshot_render",
            "recent_history_card_render",
        ):
            with self.subTest(render_kind=render_kind):
                render = trace.build_host_body_trace_history_render(
                    lane=lane,
                    entries=entries,
                    render_kind=render_kind,
                )
                self.assertEqual(render.render_status, "trace_history_render_created")
                self.assertTrue(render.render_text)

        blocked = {
            "file": ({"file_written": True}, "trace_history_render_blocked_file_write"),
            "network": (
                {"network_output_created": True},
                "trace_history_render_blocked_network_output",
            ),
            "screen": (
                {"screen_mutated": True},
                "trace_history_render_blocked_screen_mutation",
            ),
            "unity": (
                {"unity_runtime_mutated": True},
                "trace_history_render_blocked_screen_mutation",
            ),
            "first": ({"first_output_created": True}, "trace_history_render_blocked_first_output"),
            "prod": (
                {"production_behavior_created": True},
                "trace_history_render_blocked_production_behavior",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                self.assertEqual(
                    trace.build_host_body_trace_history_render(
                        lane=lane,
                        entries=entries,
                        **kwargs,
                    ).render_status,
                    expected_status,
                )

    def test_audit_readiness_and_blocked_demos(self) -> None:
        full = trace.build_demo_full_host_body_trace_history_lane()
        self.assertEqual(full["trace_history_audit"]["audit_status"], "passed_host_body_trace_history_lane")
        self.assertEqual(
            full["trace_history_readiness"]["readiness_status"],
            "ready_for_internal_action_choice_only",
        )
        self.assertFalse(full["trace_history_readiness"]["ready_for_memory_layer_write"])
        self.assertFalse(full["trace_history_readiness"]["ready_for_long_term_memory"])
        self.assertFalse(full["trace_history_readiness"]["ready_for_state_persistence_write"])
        self.assertFalse(full["trace_history_readiness"]["ready_for_file_persistence"])
        self.assertFalse(full["trace_history_readiness"]["ready_for_learning_candidate_creation"])
        self.assertFalse(full["trace_history_readiness"]["ready_for_action_selection_influence"])
        self.assertFalse(full["trace_history_readiness"]["ready_for_external_control"])
        self.assertFalse(full["trace_history_readiness"]["ready_for_first_output"])
        self.assertFalse(full["trace_history_readiness"]["ready_for_live_runtime_session"])
        self.assertTrue(full["trace_history_readiness"]["ready_for_teacher_observed_host_body_cli"])
        self.assertTrue(full["trace_history_readiness"]["ready_for_runtime_state_persistence_binding"])

        self.assertEqual(
            trace.build_demo_recent_n_trace_history_readback()["trace_history_audit"]["audit_status"],
            "passed_trace_history_readback_only",
        )
        self.assertEqual(
            trace.build_demo_blocked_memory_write_trace_history()["trace_history_audit"]["audit_status"],
            "blocked_memory_write_detected",
        )
        self.assertEqual(
            trace.build_demo_blocked_state_persistence_write_trace_history()["trace_history_audit"]["audit_status"],
            "blocked_state_persistence_write_detected",
        )
        self.assertEqual(
            trace.build_demo_blocked_first_output_trace_history()["trace_history_audit"]["audit_status"],
            "blocked_first_output_detected",
        )
        self.assertEqual(
            trace.build_demo_blocked_action_influence_trace_history()["trace_history_audit"]["audit_status"],
            "blocked_action_selection_influence_detected",
        )
        self.assertEqual(
            trace.build_demo_blocked_file_write_trace_history()["trace_history_audit"]["audit_status"],
            "blocked_file_write_detected",
        )

        plan = self._plan()
        self.assertEqual(
            trace.build_host_body_trace_history_audit(lane_plan=None).audit_status,
            "blocked_missing_lane_plan",
        )
        self.assertEqual(
            trace.build_host_body_trace_history_audit(
                lane_plan=plan,
                force_live_runtime_session=True,
            ).audit_status,
            "blocked_live_runtime_detected",
        )
        self.assertEqual(
            trace.build_host_body_trace_history_audit(
                lane_plan=plan,
                force_production_behavior=True,
            ).audit_status,
            "blocked_production_behavior_detected",
        )

    def test_cli_commands_work(self) -> None:
        commands = {
            ("show-demo-full",): "passed_host_body_trace_history_lane",
            ("show-demo-empty",): "passed_empty_host_body_trace_history_lane",
            ("show-demo-recent",): "passed_trace_history_readback_only",
            ("show-demo-filter-source-family",): "by_source_family",
            ("show-demo-index",): "trace_history_index_recorded",
            ("show-demo-render",): "trace_history_render_created",
            ("show-demo-readiness",): "ready_for_internal_action_choice_only",
            ("validate-demo-trace-history",): "passed_host_body_trace_history_lane",
            ("show-demo-blocked", "--case", "memory-write"): "blocked_memory_write_detected",
            ("show-demo-blocked", "--case", "state-persistence-write"): "blocked_state_persistence_write_detected",
            ("show-demo-blocked", "--case", "first-output"): "blocked_first_output_detected",
            ("show-demo-blocked", "--case", "action-influence"): "blocked_action_selection_influence_detected",
            ("show-demo-blocked", "--case", "file-write"): "blocked_file_write_detected",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(TRACE_CLI, *command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_guided_console_trace_history_demo_works(self) -> None:
        validation = validate_host_body_trace_history_from_guided_cradle_growth_console()
        self.assertEqual(validation["guided_console_action"], "host_body_validate_trace_history_demo")
        self.assertTrue(validation["validation"]["valid"])
        self.assertFalse(validation["memory_layer_write_performed"])
        self.assertFalse(validation["state_persistence_write_performed"])
        self.assertFalse(validation["file_written"])
        self.assertFalse(validation["action_selection_influence_created"])
        self.assertFalse(validation["first_output_created"])
        self.assertFalse(validation["live_runtime_session_created"])

        commands = {
            "host-body-show-trace-history-full-demo": "passed_host_body_trace_history_lane",
            "host-body-show-trace-history-empty-demo": "passed_empty_host_body_trace_history_lane",
            "host-body-show-trace-history-recent-demo": "passed_trace_history_readback_only",
            "host-body-show-trace-history-index-demo": "trace_history_index_recorded",
            "host-body-show-trace-history-render-demo": "trace_history_render_created",
            "host-body-show-trace-history-readiness": "ready_for_internal_action_choice_only",
            "host-body-validate-trace-history-demo": "passed_host_body_trace_history_lane",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(GUIDED_CLI, command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _plan_inputs(self):
        sensor_payload = sensor.build_demo_mixed_host_sensor_event_set()
        bridge_payload = runtime_bridge.build_demo_mixed_host_body_runtime_bridge()
        home_payload = home.build_demo_qingyin_home_internal_space_surface()
        return (
            sensor_payload["host_body_port_map"],
            home_payload["home_internal_space_surface_audit"],
            bridge_payload["host_body_runtime_bridge_audit"],
        )

    def _plan(self) -> trace.HostBodyTraceHistoryLanePlanRecord:
        port_map, home_audit, bridge_audit = self._plan_inputs()
        return trace.build_host_body_trace_history_lane_plan(
            host_body_port_map=port_map,
            home_surface_audit=home_audit,
            host_runtime_bridge_audit=bridge_audit,
        )

    def _source_records(self) -> list[dict[str, object]]:
        sensor_payload = sensor.build_demo_mixed_host_sensor_event_set()
        bridge_payload = runtime_bridge.build_demo_mixed_host_body_runtime_bridge()
        home_payload = home.build_demo_qingyin_home_internal_space_surface()
        records: list[dict[str, object]] = []
        records.extend(sensor_payload["host_body_events"])
        records.extend(sensor_payload["host_body_camera_events"])
        records.extend(sensor_payload["host_body_mic_events"])
        records.extend(sensor_payload["host_body_idle_events"])
        records.append(sensor_payload["host_body_sensor_event_set"])
        records.append(bridge_payload["host_body_runtime_bridge_trace"])
        records.append(bridge_payload["host_body_runtime_eventframe_bridges"][0])
        records.append(bridge_payload["host_body_runtime_dispatch_links"][0])
        records.append(home_payload["home_port_surface"])
        records.append(home_payload["home_host_event_surface"])
        records.append(home_payload["home_runtime_bridge_surface"])
        records.append(home_payload["home_status_lights"][0])
        records.append(home_payload["home_teacher_observed_surface"])
        records.append(home_payload["home_internal_space_render"])
        return records

    def _run_json(self, module: str, *args: str) -> dict[str, object]:
        completed = subprocess.run(
            ["py", "-3", "-m", module, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
