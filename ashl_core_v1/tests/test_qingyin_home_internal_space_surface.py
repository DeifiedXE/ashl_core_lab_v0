from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from ashl_core_v1.host_body import host_body_port_map as port_map_mod
from ashl_core_v1.host_body import host_body_runtime_bridge as runtime_bridge
from ashl_core_v1.host_body import host_body_sensor_events as sensor
from ashl_core_v1.host_body import qingyin_home_internal_space_surface as home
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_home_surface_from_guided_cradle_growth_console,
)


HOME_CLI = "ashl_core_v1.host_body.qingyin_home_internal_space_surface_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class QingyinHomeInternalSpaceSurfaceTests(unittest.TestCase):
    def test_home_surface_plan_builds_and_blocks_forbidden_authority(self) -> None:
        identity, port_map, internal_space, bridge_audit = self._plan_inputs()
        plan = home.build_qingyin_home_internal_space_surface_plan(
            host_body_identity=identity,
            host_body_port_map=port_map,
            internal_space_port=internal_space,
            host_runtime_bridge_audit=bridge_audit,
        )
        self.assertEqual(plan.surface_plan_status, "surface_plan_created")
        self.assertEqual(plan.surface_name, "qingyin_home")
        self.assertTrue(plan.read_only_surface)
        self.assertTrue(plan.internal_space_only)
        self.assertTrue(plan.teacher_observed_only)
        self.assertIn("host_body_ports", plan.allowed_surface_sections)
        self.assertFalse(plan.unity_runtime_connection_allowed)
        self.assertFalse(plan.avatar_control_allowed)
        self.assertFalse(plan.real_camera_access_allowed)
        self.assertFalse(plan.first_output_allowed)
        self.assertTrue(home.validate_qingyin_home_internal_space_surface_plan(plan)["valid"])

        blocked = {
            "missing_map": (
                {"host_body_port_map": None},
                "blocked_missing_host_body_port_map",
            ),
            "missing_space": (
                {"internal_space_port": None},
                "blocked_missing_host_body_port_map",
            ),
            "missing_bridge": (
                {"host_runtime_bridge_audit": None},
                "blocked_missing_runtime_bridge_audit",
            ),
            "unity": (
                {"unity_runtime_connection_allowed": True},
                "blocked_unity_runtime_connection_requested",
            ),
            "scene": (
                {"unity_scene_mutation_allowed": True},
                "blocked_unity_runtime_connection_requested",
            ),
            "avatar": (
                {"avatar_control_allowed": True},
                "blocked_avatar_control_requested",
            ),
            "game": (
                {"game_character_control_allowed": True},
                "blocked_avatar_control_requested",
            ),
            "camera": (
                {"real_camera_access_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
            "mic": (
                {"real_mic_access_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
            "semantic": (
                {"semantic_interpretation_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
            "speech": (
                {"speech_recognition_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
            "action": (
                {"action_selection_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
            "external": (
                {"external_control_allowed": True},
                "blocked_external_control_requested",
            ),
            "memory": (
                {"memory_write_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
            "first": (
                {"first_output_allowed": True},
                "blocked_first_output_requested",
            ),
            "live": (
                {"live_runtime_session_allowed": True},
                "blocked_forbidden_authority_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                args = {
                    "host_body_identity": identity,
                    "host_body_port_map": port_map,
                    "internal_space_port": internal_space,
                    "host_runtime_bridge_audit": bridge_audit,
                    **kwargs,
                }
                self.assertEqual(
                    home.build_qingyin_home_internal_space_surface_plan(**args).surface_plan_status,
                    expected_status,
                )

    def test_port_surface_shows_all_ports_and_blocks_connections(self) -> None:
        plan = self._plan()
        port_map = self._port_map()
        surface = home.build_qingyin_home_port_surface(
            home_surface_plan=plan,
            host_body_port_map=port_map,
        )
        self.assertEqual(surface.port_surface_status, "port_surface_created")
        self.assertTrue(surface.camera_port_visible)
        self.assertTrue(surface.mic_port_visible)
        self.assertTrue(surface.internal_space_port_visible)
        self.assertTrue(surface.output_surface_port_visible)
        self.assertTrue(surface.trace_history_port_visible)
        self.assertTrue(surface.internal_action_port_visible)
        self.assertFalse(surface.real_camera_connected)
        self.assertFalse(surface.real_mic_connected)
        self.assertFalse(surface.external_control_connected)
        self.assertFalse(surface.memory_write_connected)
        self.assertFalse(surface.first_output_connected)

        blocked = {
            "missing": (
                {"host_body_port_map": None},
                "blocked_missing_port_map",
            ),
            "camera": (
                {"real_camera_connected": True},
                "blocked_real_hardware_connection_detected",
            ),
            "mic": (
                {"real_mic_connected": True},
                "blocked_real_hardware_connection_detected",
            ),
            "external": (
                {"external_control_connected": True},
                "blocked_external_control_detected",
            ),
            "memory": (
                {"memory_write_connected": True},
                "blocked_memory_write_detected",
            ),
            "first": (
                {"first_output_connected": True},
                "blocked_first_output_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                args = {
                    "home_surface_plan": plan,
                    "host_body_port_map": port_map,
                    **kwargs,
                }
                self.assertEqual(
                    home.build_qingyin_home_port_surface(**args).port_surface_status,
                    expected_status,
                )

    def test_host_event_surface_creates_rows_counts_and_blocks_interpretation(self) -> None:
        payload = runtime_bridge.build_demo_mixed_host_body_runtime_bridge()
        sensor_payload = sensor.build_demo_mixed_host_sensor_event_set()
        event_set = sensor.HostBodySensorEventSetRecord.from_dict(
            sensor_payload["host_body_sensor_event_set"]
        )
        trace = runtime_bridge.HostBodyRuntimeBridgeTraceRecord.from_dict(
            payload["host_body_runtime_bridge_trace"]
        )
        mappings = tuple(
            runtime_bridge.HostBodyEventToRuntimeFrameMappingRecord.from_dict(item)
            for item in payload["host_body_event_runtime_mappings"]
        )
        links = tuple(
            runtime_bridge.HostBodyRuntimeDispatchLinkRecord.from_dict(item)
            for item in payload["host_body_runtime_dispatch_links"]
        )
        surface = home.build_qingyin_home_host_event_surface(
            home_surface_plan=self._plan(),
            host_sensor_event_set=event_set,
            host_runtime_bridge_trace=trace,
            event_mappings=mappings,
            dispatch_links=links,
        )
        self.assertEqual(surface.host_event_surface_status, "host_event_surface_created")
        self.assertEqual(surface.camera_event_count, 2)
        self.assertEqual(surface.mic_event_count, 2)
        self.assertEqual(surface.idle_event_count, 1)
        self.assertEqual(surface.total_event_count, 5)
        self.assertEqual(len(surface.surface_event_rows), 5)
        first_row = surface.surface_event_rows[0]
        self.assertIn("bridge_status", first_row)
        self.assertIn("target_engine_lane", first_row)
        self.assertTrue(first_row["read_only"])
        self.assertTrue(first_row["fixture_only"])
        self.assertTrue(home.validate_qingyin_home_host_event_surface(surface)["valid"])

        empty = home.build_qingyin_home_host_event_surface(home_surface_plan=self._plan())
        self.assertEqual(empty.host_event_surface_status, "host_event_surface_created_empty")

        blocked = {
            "raw_image": (
                {"raw_image_data_included": True},
                "blocked_semantic_interpretation_detected",
            ),
            "raw_audio": (
                {"raw_audio_data_included": True},
                "blocked_semantic_interpretation_detected",
            ),
            "semantic": (
                {"semantic_label_created": True},
                "blocked_semantic_interpretation_detected",
            ),
            "action": (
                {"action_selection_influence_created": True},
                "blocked_action_selection_influence_detected",
            ),
            "external": (
                {"external_control_created": True},
                "blocked_external_control_detected",
            ),
            "first": (
                {"first_output_created": True},
                "blocked_first_output_detected",
            ),
            "live": (
                {"live_runtime_session_created": True},
                "blocked_first_output_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                self.assertEqual(
                    home.build_qingyin_home_host_event_surface(
                        home_surface_plan=self._plan(),
                        host_sensor_event_set=event_set,
                        host_runtime_bridge_trace=trace,
                        event_mappings=mappings,
                        dispatch_links=links,
                        **kwargs,
                    ).host_event_surface_status,
                    expected_status,
                )

    def test_runtime_bridge_surface_counts_and_blocks_runtime_expansion(self) -> None:
        payload = runtime_bridge.build_demo_mixed_host_body_runtime_bridge()
        trace = runtime_bridge.HostBodyRuntimeBridgeTraceRecord.from_dict(
            payload["host_body_runtime_bridge_trace"]
        )
        mappings = tuple(
            runtime_bridge.HostBodyEventToRuntimeFrameMappingRecord.from_dict(item)
            for item in payload["host_body_event_runtime_mappings"]
        )
        links = tuple(
            runtime_bridge.HostBodyRuntimeDispatchLinkRecord.from_dict(item)
            for item in payload["host_body_runtime_dispatch_links"]
        )
        surface = home.build_qingyin_home_runtime_bridge_surface(
            home_surface_plan=self._plan(),
            host_runtime_bridge_trace=trace,
            event_mappings=mappings,
            dispatch_links=links,
        )
        self.assertEqual(surface.runtime_bridge_surface_status, "runtime_bridge_surface_created")
        self.assertEqual(surface.bridged_event_count, 5)
        self.assertEqual(surface.sense_eventframe_count, 4)
        self.assertEqual(surface.runtime_eventframe_count, 1)
        self.assertEqual(surface.state_eventframe_count, 0)
        self.assertEqual(surface.deferred_dispatch_count, 0)
        self.assertTrue(surface.runtime_eventframe_bridge_visible)
        self.assertTrue(surface.dispatch_adapter_status_visible)
        self.assertTrue(surface.return_payload_status_visible)

        deferred_payload = runtime_bridge.build_demo_deferred_dispatch_host_body_runtime_bridge()
        deferred = home.build_qingyin_home_runtime_bridge_surface(
            home_surface_plan=self._plan(),
            host_runtime_bridge_trace=deferred_payload["host_body_runtime_bridge_trace"],
            event_mappings=deferred_payload["host_body_event_runtime_mappings"],
            dispatch_links=deferred_payload["host_body_runtime_dispatch_links"],
        )
        self.assertEqual(
            deferred.runtime_bridge_surface_status,
            "runtime_bridge_surface_created_with_deferred_dispatch",
        )
        self.assertEqual(deferred.deferred_dispatch_count, 5)

        blocked = {
            "missing": (
                {"host_runtime_bridge_trace": None},
                "blocked_missing_runtime_bridge_trace",
            ),
            "live": (
                {"live_runtime_session_created": True},
                "blocked_live_runtime_detected",
            ),
            "engine": (
                {"live_engine_invocation_created": True},
                "blocked_live_engine_invocation_detected",
            ),
            "dynamic": (
                {"dynamic_scheduling_created": True},
                "blocked_dynamic_scheduling_detected",
            ),
            "memory": (
                {"memory_write_performed": True},
                "blocked_memory_write_detected",
            ),
            "first": (
                {"first_output_created": True},
                "blocked_first_output_detected",
            ),
            "production": (
                {"production_behavior_created": True},
                "blocked_first_output_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                args = {
                    "home_surface_plan": self._plan(),
                    "host_runtime_bridge_trace": trace,
                    "event_mappings": mappings,
                    "dispatch_links": links,
                    **kwargs,
                }
                self.assertEqual(
                    home.build_qingyin_home_runtime_bridge_surface(**args).runtime_bridge_surface_status,
                    expected_status,
                )

    def test_status_lights_teacher_surface_and_render_block_side_effects(self) -> None:
        plan = self._plan()
        for kind in (
            "host_body_ready",
            "sensor_event_seen",
            "runtime_bridge_ready",
            "teacher_review_pending",
            "boundary_warning",
            "idle",
        ):
            with self.subTest(kind=kind):
                light = home.build_qingyin_home_status_light(
                    home_surface_plan=plan,
                    status_light_kind=kind,
                )
                self.assertEqual(light.status_light_surface_status, "status_light_recorded")

        self.assertEqual(
            home.build_qingyin_home_status_light(
                home_surface_plan=plan,
                status_light_kind="idle",
                sound_output_played=True,
            ).status_light_surface_status,
            "blocked_output_side_effect_detected",
        )
        self.assertEqual(
            home.build_qingyin_home_status_light(
                home_surface_plan=plan,
                status_light_kind="idle",
                screen_output_mutated=True,
            ).status_light_surface_status,
            "blocked_output_side_effect_detected",
        )
        self.assertEqual(
            home.build_qingyin_home_status_light(
                home_surface_plan=plan,
                status_light_kind="idle",
                unity_runtime_mutated=True,
            ).status_light_surface_status,
            "blocked_unity_runtime_mutation_detected",
        )
        self.assertEqual(
            home.build_qingyin_home_status_light(
                home_surface_plan=plan,
                status_light_kind="idle",
                first_output_created=True,
            ).status_light_surface_status,
            "blocked_first_output_detected",
        )

        teacher = home.build_qingyin_home_teacher_observed_surface(
            home_surface_plan=plan,
            status_lights=(home.build_qingyin_home_status_light(home_surface_plan=plan, status_light_kind="idle"),),
        )
        self.assertEqual(teacher.teacher_surface_status, "teacher_observed_surface_created")
        for section in ("host_body_identity", "host_body_ports", "recent_host_events", "runtime_bridge_status", "status_lights", "readiness"):
            self.assertIn(section, teacher.teacher_observed_sections)
        self.assertFalse(teacher.approval_created)
        self.assertEqual(
            home.build_qingyin_home_teacher_observed_surface(
                home_surface_plan=plan,
                approval_created=True,
            ).teacher_surface_status,
            "blocked_approval_created",
        )
        self.assertEqual(
            home.build_qingyin_home_teacher_observed_surface(
                home_surface_plan=plan,
                learning_approval_created=True,
            ).teacher_surface_status,
            "blocked_learning_approval_created",
        )
        self.assertEqual(
            home.build_qingyin_home_teacher_observed_surface(
                home_surface_plan=plan,
                memory_write_approval_created=True,
            ).teacher_surface_status,
            "blocked_memory_write_approval_created",
        )

        render = home.build_qingyin_home_internal_space_render(home_surface_plan=plan)
        self.assertEqual(render.render_status, "home_internal_space_render_created_empty")
        self.assertTrue(render.read_only_render)
        for kind in ("text_summary_render", "json_snapshot_render", "read_only_card_render", "status_light_render"):
            self.assertEqual(
                home.build_qingyin_home_internal_space_render(
                    home_surface_plan=plan,
                    render_kind=kind,
                ).render_kind,
                kind,
            )
        render_blocks = {
            "unity": ({"unity_runtime_started": True}, "blocked_unity_runtime_started"),
            "scene": ({"unity_scene_mutated": True}, "blocked_unity_scene_mutation"),
            "avatar": ({"avatar_control_created": True}, "blocked_avatar_control"),
            "game": ({"game_character_control_created": True}, "blocked_avatar_control"),
            "file": ({"file_written": True}, "blocked_file_write"),
            "network": ({"network_output_created": True}, "blocked_network_output"),
            "first": ({"first_output_created": True}, "blocked_first_output"),
            "production": ({"production_behavior_created": True}, "blocked_production_behavior"),
        }
        for case, (kwargs, expected_status) in render_blocks.items():
            with self.subTest(render_case=case):
                self.assertEqual(
                    home.build_qingyin_home_internal_space_render(
                        home_surface_plan=plan,
                        **kwargs,
                    ).render_status,
                    expected_status,
                )

    def test_audit_and_readiness_pass_and_block_required_cases(self) -> None:
        pass_cases = {
            "full": (
                home.build_demo_qingyin_home_internal_space_surface,
                "passed_qingyin_home_internal_space_event_surface",
            ),
            "empty": (
                home.build_demo_empty_qingyin_home_surface,
                "passed_home_surface_with_empty_events",
            ),
            "deferred": (
                home.build_demo_deferred_dispatch_qingyin_home_surface,
                "passed_home_surface_with_deferred_dispatch",
            ),
        }
        for case, (builder, expected_status) in pass_cases.items():
            with self.subTest(case=case):
                payload = builder()
                self.assertEqual(
                    payload["home_internal_space_surface_audit"]["audit_status"],
                    expected_status,
                )
                self.assertTrue(
                    home.validate_qingyin_home_internal_space_surface_audit(
                        payload["home_internal_space_surface_audit"]
                    )["valid"]
                )

        blocked_cases = {
            "missing": (
                lambda: {"home_internal_space_surface_audit": home.build_qingyin_home_internal_space_surface_audit(home_surface_plan=None).to_dict()},
                "blocked_missing_home_surface_plan",
            ),
            "avatar": (
                home.build_demo_blocked_avatar_body_claim_home_surface,
                "blocked_avatar_control_detected",
            ),
            "unity": (
                home.build_demo_blocked_unity_runtime_connection_home_surface,
                "blocked_unity_runtime_connection_detected",
            ),
            "teacher": (
                home.build_demo_blocked_teacher_approval_home_surface,
                "blocked_teacher_approval_created",
            ),
            "first": (
                home.build_demo_blocked_first_output_home_surface,
                "blocked_first_output_detected",
            ),
            "external": (
                home.build_demo_blocked_external_control_home_surface,
                "blocked_external_control_detected",
            ),
        }
        for case, (builder, expected_status) in blocked_cases.items():
            with self.subTest(blocked_case=case):
                self.assertEqual(
                    builder()["home_internal_space_surface_audit"]["audit_status"],
                    expected_status,
                )

        readiness = home.QingyinHomeInternalSpaceSurfaceReadinessRecord.from_dict(
            home.build_demo_qingyin_home_internal_space_surface()[
                "home_internal_space_surface_readiness"
            ]
        )
        self.assertEqual(readiness.readiness_status, "ready_for_host_body_trace_history_lane_only")
        self.assertTrue(readiness.ready_for_host_body_trace_history_lane)
        self.assertTrue(readiness.ready_for_internal_action_choice_only)
        self.assertTrue(readiness.ready_for_teacher_observed_host_body_cli)
        self.assertFalse(readiness.ready_for_unity_runtime_connection)
        self.assertFalse(readiness.ready_for_avatar_control)
        self.assertFalse(readiness.ready_for_real_camera_connection)
        self.assertFalse(readiness.ready_for_real_mic_connection)
        self.assertFalse(readiness.ready_for_semantic_vision)
        self.assertFalse(readiness.ready_for_speech_recognition)
        self.assertFalse(readiness.ready_for_external_control)
        self.assertFalse(readiness.ready_for_first_output)
        self.assertFalse(readiness.ready_for_live_runtime_session)
        self.assertFalse(readiness.ready_for_memory_layer_write)
        self.assertFalse(readiness.ready_for_autonomous_scheduler)

    def test_cli_commands_work(self) -> None:
        commands = {
            ("show-demo-home-surface",): "passed_qingyin_home_internal_space_event_surface",
            ("show-demo-empty",): "passed_home_surface_with_empty_events",
            ("show-demo-deferred-dispatch",): "passed_home_surface_with_deferred_dispatch",
            ("show-demo-port-surface",): "port_surface_created",
            ("show-demo-event-surface",): "host_event_surface_created",
            ("show-demo-runtime-bridge-surface",): "runtime_bridge_surface_created",
            ("show-demo-status-lights",): "status_light_recorded",
            ("show-demo-teacher-surface",): "teacher_observed_surface_created",
            ("show-demo-render",): "home_internal_space_render_created",
            ("show-demo-readiness",): "ready_for_host_body_trace_history_lane_only",
            ("validate-demo-home-surface",): "passed_qingyin_home_internal_space_event_surface",
            ("show-demo-blocked", "--case", "avatar-body-claim"): "blocked_avatar_control_detected",
            ("show-demo-blocked", "--case", "unity-runtime-connection"): "blocked_unity_runtime_connection_detected",
            ("show-demo-blocked", "--case", "teacher-approval"): "blocked_teacher_approval_created",
            ("show-demo-blocked", "--case", "first-output"): "blocked_first_output_detected",
            ("show-demo-blocked", "--case", "external-control"): "blocked_external_control_detected",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(HOME_CLI, *command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_guided_console_home_surface_demo_works(self) -> None:
        validation = validate_host_body_home_surface_from_guided_cradle_growth_console()
        self.assertEqual(validation["guided_console_action"], "host_body_validate_home_surface_demo")
        self.assertTrue(validation["validation"]["valid"])
        self.assertFalse(validation["unity_started"])
        self.assertFalse(validation["avatar_control_created"])
        self.assertFalse(validation["teacher_approval_created"])
        self.assertFalse(validation["first_output_created"])
        self.assertFalse(validation["memory_layer_write_performed"])

        commands = {
            "host-body-show-home-surface-demo": "passed_qingyin_home_internal_space_event_surface",
            "host-body-show-home-empty-surface-demo": "passed_home_surface_with_empty_events",
            "host-body-show-home-port-surface-demo": "port_surface_created",
            "host-body-show-home-event-surface-demo": "host_event_surface_created",
            "host-body-show-home-runtime-bridge-surface-demo": "runtime_bridge_surface_created",
            "host-body-show-home-status-lights-demo": "status_light_recorded",
            "host-body-show-home-teacher-surface-demo": "teacher_observed_surface_created",
            "host-body-show-home-surface-readiness": "ready_for_host_body_trace_history_lane_only",
            "host-body-validate-home-surface-demo": "passed_qingyin_home_internal_space_event_surface",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(GUIDED_CLI, command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _plan_inputs(self):
        port_payload = port_map_mod.build_demo_qingyin_host_body_port_map()
        bridge_payload = runtime_bridge.build_demo_mixed_host_body_runtime_bridge()
        return (
            port_map_mod.HostBodyIdentityRecord.from_dict(port_payload["host_body_identity"]),
            port_map_mod.HostBodyPortMapRecord.from_dict(port_payload["host_body_port_map"]),
            port_map_mod.HostInternalSpacePortRecord.from_dict(port_payload["host_internal_space_port"]),
            runtime_bridge.HostBodyRuntimeBridgeAudit.from_dict(
                bridge_payload["host_body_runtime_bridge_audit"]
            ),
        )

    def _plan(self) -> home.QingyinHomeInternalSpaceSurfacePlanRecord:
        identity, port_map, internal_space, bridge_audit = self._plan_inputs()
        return home.build_qingyin_home_internal_space_surface_plan(
            host_body_identity=identity,
            host_body_port_map=port_map,
            internal_space_port=internal_space,
            host_runtime_bridge_audit=bridge_audit,
        )

    def _port_map(self) -> port_map_mod.HostBodyPortMapRecord:
        return port_map_mod.HostBodyPortMapRecord.from_dict(
            port_map_mod.build_demo_qingyin_host_body_port_map()["host_body_port_map"]
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
