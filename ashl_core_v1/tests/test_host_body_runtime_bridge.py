from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from ashl_core_v1.host_body import host_body_runtime_bridge as bridge
from ashl_core_v1.host_body import host_body_sensor_events as sensor
from ashl_core_v1.runtime.continuous_event_loop import RuntimeEventFrameRecord
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_runtime_bridge_from_guided_cradle_growth_console,
)


BRIDGE_CLI = "ashl_core_v1.host_body.host_body_runtime_bridge_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class HostBodyRuntimeBridgeTests(unittest.TestCase):
    def test_bridge_plan_builds_from_sensor_audit_and_blocks_expansion(self) -> None:
        payload = sensor.build_demo_mixed_host_sensor_event_set()
        audit = sensor.HostBodySensorEventAudit.from_dict(
            payload["host_body_sensor_event_audit"]
        )
        event_set = sensor.HostBodySensorEventSetRecord.from_dict(
            payload["host_body_sensor_event_set"]
        )
        plan = bridge.build_host_body_runtime_bridge_plan(
            host_sensor_event_audit=audit,
            source_host_body_port_map_id=event_set.source_host_body_port_map_id,
        )
        self.assertEqual(plan.bridge_plan_status, "bridge_plan_created")
        self.assertIn("camera_low_level_event", plan.allowed_source_event_families)
        self.assertIn("mic_low_level_event", plan.allowed_source_event_families)
        self.assertIn("host_idle_event", plan.allowed_source_event_families)
        self.assertIn("host_status_event", plan.allowed_source_event_families)
        self.assertIn("sense_event", plan.allowed_target_event_families)
        self.assertIn("runtime", plan.allowed_target_engine_lanes)
        self.assertTrue(plan.fixture_only_required)
        self.assertTrue(plan.read_only_required)
        self.assertTrue(plan.runtime_eventframe_only)
        self.assertFalse(plan.real_hardware_allowed)
        self.assertFalse(plan.live_runtime_session_allowed)
        self.assertTrue(bridge.validate_host_body_runtime_bridge_plan(plan)["valid"])

        blocked_cases = {
            "missing": (
                {"host_sensor_event_audit": None},
                "blocked_missing_host_sensor_event_audit",
            ),
            "source": (
                {
                    "host_sensor_event_audit": audit,
                    "allowed_source_event_families": ("learning_event",),
                },
                "blocked_unapproved_source_event_family",
            ),
            "family": (
                {
                    "host_sensor_event_audit": audit,
                    "allowed_target_event_families": ("learning_event",),
                },
                "blocked_unapproved_target_event_family",
            ),
            "learning_lane": (
                {
                    "host_sensor_event_audit": audit,
                    "allowed_target_engine_lanes": ("learning_engine",),
                },
                "blocked_forbidden_authority_detected",
            ),
            "hardware": (
                {"host_sensor_event_audit": audit, "real_hardware_allowed": True},
                "blocked_real_hardware_allowed",
            ),
            "semantic": (
                {"host_sensor_event_audit": audit, "semantic_interpretation_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
            "action": (
                {"host_sensor_event_audit": audit, "action_selection_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
            "external": (
                {"host_sensor_event_audit": audit, "external_control_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
            "memory": (
                {"host_sensor_event_audit": audit, "memory_write_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
            "first": (
                {"host_sensor_event_audit": audit, "first_output_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
            "live": (
                {"host_sensor_event_audit": audit, "live_runtime_session_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
            "dynamic": (
                {"host_sensor_event_audit": audit, "dynamic_scheduling_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked_cases.items():
            with self.subTest(case=case):
                self.assertEqual(
                    bridge.build_host_body_runtime_bridge_plan(**kwargs).bridge_plan_status,
                    expected_status,
                )

    def test_host_body_event_mapping_routes_allowed_families_and_blocks_forbidden_targets(self) -> None:
        plan = self._bridge_plan()
        camera_event = self._event("camera_frame_available", "camera_port")
        mic_event = self._event("mic_peak_detected", "mic_port")
        idle_event = self._event("host_idle", "host_status_port")
        status_event = self._event("host_status_available", "host_status_port")

        camera_mapping = bridge.map_host_body_event_to_runtime_eventframe(
            bridge_plan=plan,
            host_body_event=camera_event,
        )
        self.assertEqual(camera_mapping.target_event_type, "host_camera_event")
        self.assertEqual(camera_mapping.target_event_family, "sense_event")
        self.assertEqual(camera_mapping.target_engine_lane, "sense_interface")
        self.assertEqual(camera_mapping.mapping_status, "host_event_mapped_to_sense_eventframe")
        self.assertTrue(camera_mapping.mapping_is_fixture_only)
        self.assertTrue(camera_mapping.mapping_is_read_only)
        self.assertTrue(camera_mapping.semantic_label_preserved_null)

        mic_mapping = bridge.map_host_body_event_to_runtime_eventframe(
            bridge_plan=plan,
            host_body_event=mic_event,
        )
        self.assertEqual(mic_mapping.target_event_type, "host_mic_event")
        self.assertEqual(mic_mapping.target_engine_lane, "sense_interface")

        idle_mapping = bridge.map_host_body_event_to_runtime_eventframe(
            bridge_plan=plan,
            host_body_event=idle_event,
        )
        self.assertEqual(idle_mapping.target_event_type, "host_idle_event")
        self.assertEqual(idle_mapping.target_event_family, "runtime_event")
        self.assertEqual(idle_mapping.target_engine_lane, "runtime")

        state_mapping = bridge.map_host_body_event_to_runtime_eventframe(
            bridge_plan=plan,
            host_body_event=status_event,
        )
        self.assertEqual(state_mapping.target_event_type, "host_status_event")
        self.assertEqual(state_mapping.target_event_family, "state_event")
        self.assertEqual(state_mapping.target_engine_lane, "state_engine")

        unknown = self._event("summon", "unknown_port")
        self.assertEqual(
            bridge.map_host_body_event_to_runtime_eventframe(
                bridge_plan=plan,
                host_body_event=unknown,
            ).mapping_status,
            "blocked_unknown_host_event_family",
        )
        for lane in ("learning_engine", "memory_engine", "task_engine", "selected_action"):
            with self.subTest(lane=lane):
                self.assertEqual(
                    bridge.map_host_body_event_to_runtime_eventframe(
                        bridge_plan=plan,
                        host_body_event=camera_event,
                        target_engine_lane=lane,
                    ).mapping_status,
                    "blocked_forbidden_target_engine",
                )
        blocked_flags = {
            "semantic": (
                {"semantic_interpretation_created": True},
                "blocked_semantic_interpretation_detected",
            ),
            "action": (
                {"action_selection_influence_created": True},
                "blocked_action_selection_influence_detected",
            ),
            "external": (
                {"external_control_created": True},
                "blocked_forbidden_authority_detected",
            ),
            "memory": (
                {"memory_write_performed": True},
                "blocked_forbidden_authority_detected",
            ),
            "first": (
                {"first_output_created": True},
                "blocked_forbidden_authority_detected",
            ),
            "live": (
                {"live_runtime_session_created": True},
                "blocked_forbidden_authority_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked_flags.items():
            with self.subTest(flag=case):
                self.assertEqual(
                    bridge.map_host_body_event_to_runtime_eventframe(
                        bridge_plan=plan,
                        host_body_event=camera_event,
                        **kwargs,
                    ).mapping_status,
                    expected_status,
                )

    def test_runtime_eventframe_bridge_creates_fixture_only_eventframe_and_blocks_expansion(self) -> None:
        mapping = bridge.map_host_body_event_to_runtime_eventframe(
            bridge_plan=self._bridge_plan(),
            host_body_event=self._event("camera_frame_available", "camera_port"),
        )
        frame_bridge, runtime_frame = bridge.build_host_body_runtime_eventframe_bridge(
            mapping=mapping
        )
        self.assertEqual(
            frame_bridge.bridge_status,
            "runtime_eventframe_bridge_created_for_sense_event",
        )
        self.assertTrue(frame_bridge.runtime_eventframe_created)
        self.assertTrue(frame_bridge.runtime_eventframe_fixture_only)
        self.assertTrue(frame_bridge.runtime_eventframe_read_only)
        self.assertTrue(frame_bridge.dispatch_required)
        self.assertFalse(frame_bridge.parent_resume_required)
        self.assertIsInstance(runtime_frame, RuntimeEventFrameRecord)
        self.assertEqual(runtime_frame.event_type, "host_camera_event")
        self.assertEqual(runtime_frame.source_engine, "runtime")
        self.assertFalse(runtime_frame.memory_write_performed)
        self.assertTrue(
            bridge.validate_host_body_runtime_eventframe_bridge(frame_bridge)["valid"]
        )

        invalid_mapping = bridge.map_host_body_event_to_runtime_eventframe(
            bridge_plan=self._bridge_plan(),
            host_body_event=self._event("camera_frame_available", "camera_port"),
            target_engine_lane="learning_engine",
        )
        invalid_bridge, invalid_frame = bridge.build_host_body_runtime_eventframe_bridge(
            mapping=invalid_mapping
        )
        self.assertEqual(invalid_bridge.bridge_status, "blocked_invalid_mapping")
        self.assertIsNone(invalid_frame)

        blocked = {
            "live": (
                {"live_runtime_session_created": True},
                "blocked_live_runtime_detected",
            ),
            "dynamic": (
                {"dynamic_child_event_created": True},
                "blocked_dynamic_child_event_detected",
            ),
            "external": (
                {"external_execution_created": True},
                "blocked_forbidden_authority_detected",
            ),
            "memory": (
                {"memory_layer_write_performed": True},
                "blocked_forbidden_authority_detected",
            ),
            "approval": (
                {"automatic_learning_approval_created": True},
                "blocked_forbidden_authority_detected",
            ),
            "first": (
                {"first_output_created": True},
                "blocked_forbidden_authority_detected",
            ),
            "production": (
                {"production_behavior_created": True},
                "blocked_forbidden_authority_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                record, _ = bridge.build_host_body_runtime_eventframe_bridge(
                    mapping=mapping,
                    **kwargs,
                )
                self.assertEqual(record.bridge_status, expected_status)

    def test_dispatch_link_records_adapter_only_and_blocks_live_invocation(self) -> None:
        mapping = bridge.map_host_body_event_to_runtime_eventframe(
            bridge_plan=self._bridge_plan(),
            host_body_event=self._event("camera_frame_available", "camera_port"),
        )
        sense_bridge, _ = bridge.build_host_body_runtime_eventframe_bridge(mapping=mapping)
        sense = bridge.build_host_body_runtime_dispatch_link(eventframe_bridge=sense_bridge)
        self.assertEqual(sense.dispatch_link_status, "dispatch_link_created_sense_adapter_only")
        self.assertTrue(sense.dispatch_adapter_only)
        self.assertFalse(sense.handler_invoked)
        self.assertFalse(sense.live_engine_invocation_created)
        self.assertEqual(sense.return_payload_status, "returned_success")
        self.assertTrue(bridge.validate_host_body_runtime_dispatch_link(sense)["valid"])

        runtime_mapping = bridge.map_host_body_event_to_runtime_eventframe(
            bridge_plan=self._bridge_plan(),
            host_body_event=self._event("host_idle", "host_status_port"),
        )
        runtime_bridge, _ = bridge.build_host_body_runtime_eventframe_bridge(
            mapping=runtime_mapping
        )
        self.assertEqual(
            bridge.build_host_body_runtime_dispatch_link(
                eventframe_bridge=runtime_bridge
            ).dispatch_link_status,
            "dispatch_link_created_runtime_adapter_only",
        )
        state_mapping = bridge.map_host_body_event_to_runtime_eventframe(
            bridge_plan=self._bridge_plan(),
            host_body_event=self._event("host_status_available", "host_status_port"),
        )
        state_bridge, _ = bridge.build_host_body_runtime_eventframe_bridge(
            mapping=state_mapping
        )
        self.assertEqual(
            bridge.build_host_body_runtime_dispatch_link(
                eventframe_bridge=state_bridge
            ).dispatch_link_status,
            "dispatch_link_created_state_adapter_only",
        )
        self.assertEqual(
            bridge.build_host_body_runtime_dispatch_link(
                eventframe_bridge=sense_bridge,
                defer_dispatch_adapter=True,
            ).dispatch_link_status,
            "dispatch_link_deferred_missing_dispatch_adapter",
        )
        self.assertEqual(
            bridge.build_host_body_runtime_dispatch_link(
                eventframe_bridge=None,
            ).dispatch_link_status,
            "blocked_missing_eventframe_bridge",
        )
        blocked = {
            "live": (
                {"live_engine_invocation_created": True},
                "blocked_live_engine_invocation_detected",
            ),
            "external": (
                {"external_execution_created": True},
                "blocked_forbidden_authority_detected",
            ),
            "memory": (
                {"memory_layer_write_performed": True},
                "blocked_forbidden_authority_detected",
            ),
            "approval": (
                {"automatic_learning_approval_created": True},
                "blocked_forbidden_authority_detected",
            ),
            "first": (
                {"first_output_created": True},
                "blocked_forbidden_authority_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                self.assertEqual(
                    bridge.build_host_body_runtime_dispatch_link(
                        eventframe_bridge=sense_bridge,
                        **kwargs,
                    ).dispatch_link_status,
                    expected_status,
                )

    def test_bridge_trace_records_counts_and_blocked_cases(self) -> None:
        mixed = bridge.build_demo_mixed_host_body_runtime_bridge()
        trace = bridge.HostBodyRuntimeBridgeTraceRecord.from_dict(
            mixed["host_body_runtime_bridge_trace"]
        )
        self.assertEqual(trace.bridge_trace_status, "host_body_runtime_bridge_trace_complete")
        self.assertEqual(trace.bridged_event_count, 5)
        self.assertEqual(trace.camera_event_bridge_count, 2)
        self.assertEqual(trace.mic_event_bridge_count, 2)
        self.assertEqual(trace.idle_event_bridge_count, 1)
        self.assertTrue(trace.all_events_fixture_only)
        self.assertTrue(trace.all_events_read_only)
        self.assertTrue(trace.all_events_mapped_to_allowed_eventframes)
        self.assertTrue(trace.all_bridged_eventframes_dispatchable)

        deferred = bridge.build_demo_deferred_dispatch_host_body_runtime_bridge()
        self.assertEqual(
            deferred["host_body_runtime_bridge_trace"]["bridge_trace_status"],
            "host_body_runtime_bridge_trace_complete_with_deferred_dispatch",
        )
        self.assertEqual(
            bridge.build_host_body_runtime_bridge_trace(
                bridge_plan=None,
                host_body_events=(),
                event_mappings=(),
                eventframe_bridges=(),
                dispatch_links=(),
            ).bridge_trace_status,
            "host_body_runtime_bridge_trace_blocked_missing_plan",
        )
        plan = self._bridge_plan()
        self.assertEqual(
            bridge.build_host_body_runtime_bridge_trace(
                bridge_plan=plan,
                host_body_events=(),
                event_mappings=(),
                eventframe_bridges=(),
                dispatch_links=(),
            ).bridge_trace_status,
            "host_body_runtime_bridge_trace_blocked_missing_mapping",
        )

    def test_audit_passes_and_blocks_required_cases(self) -> None:
        pass_cases = {
            "camera": (
                bridge.build_demo_camera_event_to_sense_eventframe_bridge,
                "passed_camera_event_to_sense_eventframe_bridge",
            ),
            "mic": (
                bridge.build_demo_mic_event_to_sense_eventframe_bridge,
                "passed_mic_event_to_sense_eventframe_bridge",
            ),
            "idle": (
                bridge.build_demo_idle_event_to_runtime_eventframe_bridge,
                "passed_idle_event_to_runtime_eventframe_bridge",
            ),
            "mixed": (
                bridge.build_demo_mixed_host_body_runtime_bridge,
                "passed_host_body_event_runtime_eventframe_bridge",
            ),
            "deferred": (
                bridge.build_demo_deferred_dispatch_host_body_runtime_bridge,
                "passed_host_body_runtime_bridge_with_deferred_dispatch",
            ),
        }
        for case, (builder, expected_status) in pass_cases.items():
            with self.subTest(case=case):
                payload = builder()
                self.assertEqual(
                    payload["host_body_runtime_bridge_audit"]["audit_status"],
                    expected_status,
                )
                self.assertTrue(
                    bridge.validate_host_body_runtime_bridge_audit(
                        payload["host_body_runtime_bridge_audit"]
                    )["valid"]
                )

        blocked_cases = {
            "learning": (
                bridge.build_demo_blocked_direct_learning_mapping_bridge,
                "blocked_invalid_event_mapping",
            ),
            "action": (
                bridge.build_demo_blocked_action_selection_influence_bridge,
                "blocked_action_selection_influence_detected",
            ),
            "live": (
                bridge.build_demo_blocked_live_runtime_bridge,
                "blocked_live_runtime_detected",
            ),
            "first": (
                bridge.build_demo_blocked_first_output_bridge,
                "blocked_first_output_detected",
            ),
            "real": (
                bridge.build_demo_blocked_real_hardware_bridge,
                "blocked_real_hardware_access_detected",
            ),
        }
        for case, (builder, expected_status) in blocked_cases.items():
            with self.subTest(blocked_case=case):
                self.assertEqual(
                    builder()["host_body_runtime_bridge_audit"]["audit_status"],
                    expected_status,
                )

        missing = bridge.build_host_body_runtime_bridge_audit(
            host_sensor_event_audit=None,
            bridge_plan=None,
            bridge_trace=None,
        )
        self.assertEqual(missing.audit_status, "blocked_missing_sensor_event_audit")

        valid = bridge.build_demo_mixed_host_body_runtime_bridge()
        audit = bridge.build_host_body_runtime_bridge_audit(
            host_sensor_event_audit=valid["host_body_sensor_event_audit"],
            bridge_plan=valid["host_body_runtime_bridge_plan"],
            bridge_trace=valid["host_body_runtime_bridge_trace"],
            event_mappings=valid["host_body_event_runtime_mappings"],
            eventframe_bridges=valid["host_body_runtime_eventframe_bridges"],
            dispatch_links=valid["host_body_runtime_dispatch_links"],
            force_dynamic_scheduling=True,
        )
        self.assertEqual(audit.audit_status, "blocked_dynamic_scheduling_detected")

    def test_readiness_recommends_internal_space_surface_only(self) -> None:
        payload = bridge.build_demo_mixed_host_body_runtime_bridge()
        readiness = bridge.HostBodyRuntimeBridgeReadinessRecord.from_dict(
            payload["host_body_runtime_bridge_readiness"]
        )
        self.assertEqual(
            readiness.readiness_status,
            "ready_for_unity_home_internal_space_surface_only",
        )
        self.assertTrue(readiness.ready_for_unity_home_internal_space_surface)
        self.assertTrue(readiness.ready_for_host_body_trace_history_lane)
        self.assertTrue(readiness.ready_for_internal_action_choice_only)
        self.assertTrue(readiness.ready_for_teacher_observed_host_event_cli)
        self.assertFalse(readiness.ready_for_real_camera_connection)
        self.assertFalse(readiness.ready_for_real_mic_connection)
        self.assertFalse(readiness.ready_for_speech_recognition)
        self.assertFalse(readiness.ready_for_semantic_vision)
        self.assertFalse(readiness.ready_for_external_control)
        self.assertFalse(readiness.ready_for_first_output)
        self.assertFalse(readiness.ready_for_live_runtime_session)
        self.assertFalse(readiness.ready_for_memory_layer_write)
        self.assertFalse(readiness.ready_for_autonomous_scheduler)
        self.assertFalse(readiness.ready_for_live_engine_invocation)

    def test_cli_commands_work(self) -> None:
        commands = {
            ("show-demo-camera-bridge",): "passed_camera_event_to_sense_eventframe_bridge",
            ("show-demo-mic-bridge",): "passed_mic_event_to_sense_eventframe_bridge",
            ("show-demo-idle-bridge",): "passed_idle_event_to_runtime_eventframe_bridge",
            ("show-demo-mixed-bridge",): "passed_host_body_event_runtime_eventframe_bridge",
            ("show-demo-deferred-dispatch",): "passed_host_body_runtime_bridge_with_deferred_dispatch",
            ("show-demo-summary",): "host_body_runtime_bridge_trace_complete",
            ("show-demo-readiness",): "ready_for_unity_home_internal_space_surface_only",
            ("validate-demo-runtime-bridge",): "passed_host_body_event_runtime_eventframe_bridge",
            ("show-demo-blocked", "--case", "direct-learning-mapping"): "blocked_invalid_event_mapping",
            ("show-demo-blocked", "--case", "action-selection-influence"): "blocked_action_selection_influence_detected",
            ("show-demo-blocked", "--case", "live-runtime"): "blocked_live_runtime_detected",
            ("show-demo-blocked", "--case", "first-output"): "blocked_first_output_detected",
            ("show-demo-blocked", "--case", "real-hardware"): "blocked_real_hardware_access_detected",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(BRIDGE_CLI, *command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_guided_console_runtime_bridge_demo_works(self) -> None:
        validation = validate_host_body_runtime_bridge_from_guided_cradle_growth_console()
        self.assertEqual(validation["guided_console_action"], "host_body_validate_runtime_bridge_demo")
        self.assertTrue(validation["validation"]["valid"])
        self.assertFalse(validation["camera_connected"])
        self.assertFalse(validation["microphone_connected"])
        self.assertFalse(validation["live_runtime_session_created"])
        self.assertFalse(validation["live_engine_invocation_created"])
        self.assertFalse(validation["first_output_created"])
        self.assertFalse(validation["external_action_executed"])
        self.assertFalse(validation["memory_layer_write_performed"])

        commands = {
            "host-body-show-camera-runtime-bridge-demo": "host_camera_event",
            "host-body-show-mic-runtime-bridge-demo": "host_mic_event",
            "host-body-show-idle-runtime-bridge-demo": "host_idle_event",
            "host-body-show-mixed-runtime-bridge-demo": "passed_host_body_event_runtime_eventframe_bridge",
            "host-body-show-runtime-bridge-readiness": "ready_for_unity_home_internal_space_surface_only",
            "host-body-validate-runtime-bridge-demo": "passed_host_body_event_runtime_eventframe_bridge",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(GUIDED_CLI, command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _bridge_plan(self) -> bridge.HostBodyRuntimeBridgePlanRecord:
        payload = sensor.build_demo_mixed_host_sensor_event_set()
        audit = sensor.HostBodySensorEventAudit.from_dict(
            payload["host_body_sensor_event_audit"]
        )
        event_set = sensor.HostBodySensorEventSetRecord.from_dict(
            payload["host_body_sensor_event_set"]
        )
        return bridge.build_host_body_runtime_bridge_plan(
            host_sensor_event_audit=audit,
            source_host_body_port_map_id=event_set.source_host_body_port_map_id,
        )

    def _event(self, event_type: str, source_port_kind: str) -> sensor.HostBodyEventRecord:
        return sensor.build_host_body_event_record(
            source_host_body_port_map_id="port_map:demo",
            source_port_id=f"{source_port_kind}:demo",
            source_port_kind=source_port_kind,
            event_type=event_type,
        )

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
