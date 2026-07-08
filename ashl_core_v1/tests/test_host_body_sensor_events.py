from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.host_body import host_body_sensor_events as sensor
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_sensor_event_from_guided_cradle_growth_console,
)


SENSOR_CLI = "ashl_core_v1.host_body.host_body_sensor_events_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class HostBodySensorEventsTests(unittest.TestCase):
    def test_host_body_event_records_fixture_only_and_blocks_forbidden_boundaries(self) -> None:
        event = sensor.build_host_body_event_record(
            source_host_body_port_map_id="port_map:demo",
            source_port_id="camera:demo",
            source_port_kind="camera_port",
            event_type="camera_frame_available",
        )
        self.assertEqual(event.event_family, "camera_low_level_event")
        self.assertEqual(event.event_status, "host_body_event_recorded_fixture_only")
        self.assertTrue(event.fixture_only)
        self.assertTrue(event.read_only_event)
        self.assertFalse(event.real_hardware_event)
        self.assertIsNone(event.semantic_label)
        self.assertFalse(event.real_camera_accessed)
        self.assertFalse(event.real_mic_accessed)
        self.assertFalse(event.action_selection_influence_created)
        self.assertFalse(event.memory_layer_write_performed)
        self.assertFalse(event.first_output_created)
        self.assertFalse(event.live_runtime_session_created)
        self.assertTrue(sensor.validate_host_body_event_record(event)["valid"])

        blocked_cases = {
            "real_hardware": (
                {"real_hardware_event": True},
                "host_body_event_blocked_real_hardware",
            ),
            "semantic_label": (
                {"semantic_label": "person"},
                "host_body_event_blocked_semantic_interpretation",
            ),
            "camera": (
                {"real_camera_accessed": True},
                "host_body_event_blocked_real_hardware",
            ),
            "mic": (
                {"real_mic_accessed": True},
                "host_body_event_blocked_real_hardware",
            ),
            "capture": (
                {"camera_capture_started": True},
                "host_body_event_blocked_real_hardware",
            ),
            "stream": (
                {"mic_stream_started": True},
                "host_body_event_blocked_real_hardware",
            ),
            "image": (
                {"image_frame_stored": True},
                "host_body_event_blocked_real_hardware",
            ),
            "audio": (
                {"audio_stored": True},
                "host_body_event_blocked_real_hardware",
            ),
            "vision": (
                {"semantic_vision_created": True},
                "host_body_event_blocked_semantic_interpretation",
            ),
            "object": (
                {"object_recognition_created": True},
                "host_body_event_blocked_semantic_interpretation",
            ),
            "face": (
                {"face_recognition_created": True},
                "host_body_event_blocked_semantic_interpretation",
            ),
            "speech": (
                {"speech_recognition_created": True},
                "host_body_event_blocked_semantic_interpretation",
            ),
            "speaker": (
                {"speaker_identification_created": True},
                "host_body_event_blocked_semantic_interpretation",
            ),
            "voice": (
                {"voice_command_created": True},
                "host_body_event_blocked_semantic_interpretation",
            ),
            "language": (
                {"language_understanding_created": True},
                "host_body_event_blocked_semantic_interpretation",
            ),
            "action": (
                {"action_selection_influence_created": True},
                "host_body_event_blocked_semantic_interpretation",
            ),
            "external": (
                {"external_control_created": True},
                "host_body_event_blocked_external_control",
            ),
            "memory": (
                {"memory_layer_write_performed": True},
                "host_body_event_blocked_memory_write",
            ),
            "approval": (
                {"automatic_learning_approval_created": True},
                "host_body_event_blocked_memory_write",
            ),
            "first": (
                {"first_output_created": True},
                "host_body_event_blocked_first_output",
            ),
            "live": (
                {"live_runtime_session_created": True},
                "host_body_event_blocked_first_output",
            ),
        }
        for case, (kwargs, expected_status) in blocked_cases.items():
            with self.subTest(case=case):
                record = sensor.build_host_body_event_record(
                    source_host_body_port_map_id="port_map:demo",
                    source_port_id="camera:demo",
                    source_port_kind="camera_port",
                    event_type="camera_frame_available",
                    **kwargs,
                )
                self.assertEqual(record.event_status, expected_status)
                self.assertIsNone(record.semantic_label)

    def test_camera_event_records_low_level_events_and_blocks_semantics(self) -> None:
        host_event = self._host_event("camera_frame_available", "camera_port")
        frame = sensor.build_host_body_camera_event_record(
            host_body_event=host_event,
            source_camera_port_id="camera_port:demo",
            camera_event_type="camera_frame_available",
        )
        self.assertEqual(frame.camera_event_status, "camera_event_recorded_fixture_only")
        self.assertTrue(frame.frame_available)
        self.assertIsNone(frame.semantic_label)
        self.assertFalse(frame.real_camera_accessed)

        changed = sensor.build_host_body_camera_event_record(
            host_body_event=self._host_event("camera_frame_changed", "camera_port"),
            source_camera_port_id="camera_port:demo",
            camera_event_type="camera_frame_changed",
            change_bucket="medium",
        )
        self.assertTrue(changed.frame_changed)
        self.assertEqual(changed.change_bucket, "medium")
        self.assertEqual(
            sensor.build_host_body_camera_event_record(
                host_body_event=self._host_event("camera_brightness_changed", "camera_port"),
                source_camera_port_id="camera_port:demo",
                camera_event_type="camera_brightness_changed",
                brightness_bucket="low",
            ).brightness_bucket,
            "low",
        )
        self.assertTrue(
            sensor.build_host_body_camera_event_record(
                host_body_event=self._host_event("camera_motion_proxy_changed", "camera_port"),
                source_camera_port_id="camera_port:demo",
                camera_event_type="camera_motion_proxy_changed",
                motion_proxy_bucket="high",
            ).motion_proxy_changed
        )

        blocked = {
            "real": ({"real_camera_accessed": True}, "camera_event_blocked_real_camera"),
            "capture": (
                {"camera_capture_started": True},
                "camera_event_blocked_real_camera",
            ),
            "stored": ({"image_frame_stored": True}, "camera_event_blocked_real_camera"),
            "semantic": (
                {"semantic_label": "room"},
                "camera_event_blocked_semantic_vision",
            ),
            "object": (
                {"object_recognition_created": True},
                "camera_event_blocked_object_recognition",
            ),
            "face": (
                {"face_recognition_created": True},
                "camera_event_blocked_object_recognition",
            ),
            "person": (
                {"person_identification_created": True},
                "camera_event_blocked_object_recognition",
            ),
            "scene": (
                {"scene_understanding_created": True},
                "camera_event_blocked_semantic_vision",
            ),
            "action": (
                {"vision_to_action_created": True},
                "camera_event_blocked_vision_to_action",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                record = sensor.build_host_body_camera_event_record(
                    host_body_event=host_event,
                    source_camera_port_id="camera_port:demo",
                    camera_event_type="camera_frame_available",
                    **kwargs,
                )
                self.assertEqual(record.camera_event_status, expected_status)
                self.assertIsNone(record.semantic_label)

    def test_mic_event_records_low_level_events_and_blocks_speech(self) -> None:
        host_event = self._host_event("mic_level_changed", "mic_port")
        level = sensor.build_host_body_mic_event_record(
            host_body_event=host_event,
            source_mic_port_id="mic_port:demo",
            mic_event_type="mic_level_changed",
            sound_level_bucket="medium",
        )
        self.assertEqual(level.mic_event_status, "mic_event_recorded_fixture_only")
        self.assertEqual(level.sound_level_bucket, "medium")
        self.assertIsNone(level.speech_text)
        self.assertIsNone(level.speaker_id)

        self.assertTrue(
            sensor.build_host_body_mic_event_record(
                host_body_event=self._host_event("mic_peak_detected", "mic_port"),
                source_mic_port_id="mic_port:demo",
                mic_event_type="mic_peak_detected",
            ).peak_detected
        )
        self.assertTrue(
            sensor.build_host_body_mic_event_record(
                host_body_event=self._host_event("mic_silence", "mic_port"),
                source_mic_port_id="mic_port:demo",
                mic_event_type="mic_silence",
            ).silence_detected
        )
        self.assertTrue(
            sensor.build_host_body_mic_event_record(
                host_body_event=self._host_event("mic_sustained_noise", "mic_port"),
                source_mic_port_id="mic_port:demo",
                mic_event_type="mic_sustained_noise",
            ).sustained_noise_detected
        )

        blocked = {
            "real": ({"real_mic_accessed": True}, "mic_event_blocked_real_mic"),
            "stream": ({"mic_stream_started": True}, "mic_event_blocked_real_mic"),
            "stored": ({"audio_stored": True}, "mic_event_blocked_real_mic"),
            "speech": (
                {"speech_recognition_created": True, "speech_text": "hello"},
                "mic_event_blocked_speech_recognition",
            ),
            "speaker": (
                {"speaker_identification_created": True, "speaker_id": "speaker"},
                "mic_event_blocked_speech_recognition",
            ),
            "voice": (
                {"voice_command_created": True},
                "mic_event_blocked_voice_command",
            ),
            "language": (
                {"language_understanding_created": True},
                "mic_event_blocked_speech_recognition",
            ),
            "action": (
                {"audio_to_action_created": True},
                "mic_event_blocked_audio_to_action",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                record = sensor.build_host_body_mic_event_record(
                    host_body_event=host_event,
                    source_mic_port_id="mic_port:demo",
                    mic_event_type="mic_level_changed",
                    **kwargs,
                )
                self.assertEqual(record.mic_event_status, expected_status)
                self.assertIsNone(record.speech_text)
                self.assertIsNone(record.speaker_id)

    def test_idle_event_records_host_status_and_blocks_runtime_expansion(self) -> None:
        event = sensor.build_host_body_idle_event_record(idle_event_type="host_idle")
        self.assertEqual(event.idle_event_status, "host_idle_event_recorded_fixture_only")
        self.assertEqual(event.host_power_state, "host_power_on_fixture")
        self.assertEqual(event.host_activity_bucket, "idle")
        self.assertFalse(event.runtime_tick_created)
        self.assertFalse(event.live_runtime_session_created)
        self.assertFalse(event.autonomous_scheduler_created)
        self.assertFalse(event.open_ended_loop_created)
        self.assertFalse(event.background_daemon_created)
        self.assertFalse(event.memory_layer_write_performed)
        self.assertFalse(event.production_behavior_created)

        self.assertEqual(
            sensor.build_host_body_idle_event_record(
                idle_event_type="host_power_on_observed",
                host_activity_bucket="active_fixture",
            ).host_activity_bucket,
            "active_fixture",
        )
        self.assertEqual(
            sensor.build_host_body_idle_event_record(
                idle_event_type="host_low_activity_tick",
                host_activity_bucket="low_activity",
            ).idle_event_status,
            "host_idle_event_recorded_fixture_only",
        )

        blocked = {
            "tick": (
                {"runtime_tick_created": True},
                "host_idle_event_blocked_live_runtime_tick",
            ),
            "live": (
                {"live_runtime_session_created": True},
                "host_idle_event_blocked_live_runtime_tick",
            ),
            "autonomous": (
                {"autonomous_scheduler_created": True},
                "host_idle_event_blocked_autonomous_scheduler",
            ),
            "open": (
                {"open_ended_loop_created": True},
                "host_idle_event_blocked_open_ended_loop",
            ),
            "daemon": (
                {"background_daemon_created": True},
                "host_idle_event_blocked_autonomous_scheduler",
            ),
            "memory": (
                {"memory_layer_write_performed": True},
                "host_idle_event_blocked_live_runtime_tick",
            ),
            "production": (
                {"production_behavior_created": True},
                "host_idle_event_blocked_live_runtime_tick",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                self.assertEqual(
                    sensor.build_host_body_idle_event_record(
                        idle_event_type="host_idle",
                        **kwargs,
                    ).idle_event_status,
                    expected_status,
                )

    def test_sensor_event_set_summary_and_readiness_records(self) -> None:
        payload = sensor.build_demo_mixed_host_sensor_event_set()
        event_set = sensor.HostBodySensorEventSetRecord.from_dict(
            payload["host_body_sensor_event_set"]
        )
        summary = sensor.HostBodySensorEventSummaryRecord.from_dict(
            payload["host_body_sensor_event_summary"]
        )
        readiness = sensor.HostBodySensorEventReadinessRecord.from_dict(
            payload["host_body_sensor_event_readiness"]
        )
        self.assertEqual(event_set.event_set_status, "host_sensor_event_set_recorded_fixture_only")
        self.assertEqual(event_set.camera_event_count, 2)
        self.assertEqual(event_set.mic_event_count, 2)
        self.assertEqual(event_set.idle_event_count, 1)
        self.assertEqual(event_set.total_event_count, 5)
        self.assertFalse(event_set.real_hardware_accessed)
        self.assertFalse(event_set.semantic_interpretation_created)
        self.assertFalse(event_set.external_control_created)
        self.assertFalse(event_set.memory_layer_write_performed)
        self.assertFalse(event_set.first_output_created)
        self.assertFalse(event_set.live_runtime_session_created)
        self.assertEqual(summary.summary_status, "host_sensor_event_summary_recorded")
        self.assertEqual(summary.low_level_event_count, 5)
        self.assertEqual(summary.blocked_event_count, 0)
        self.assertEqual(
            readiness.readiness_status,
            "ready_for_host_body_event_runtime_eventframe_bridge_only",
        )
        self.assertTrue(readiness.ready_for_host_body_event_to_runtime_eventframe)
        self.assertTrue(readiness.ready_for_runtime_eventframe_fixture_bridge)
        self.assertTrue(readiness.ready_for_unity_home_internal_space_surface)
        self.assertTrue(readiness.ready_for_internal_action_choice_only)
        self.assertFalse(readiness.ready_for_real_camera_connection)
        self.assertFalse(readiness.ready_for_real_mic_connection)
        self.assertFalse(readiness.ready_for_speech_recognition)
        self.assertFalse(readiness.ready_for_semantic_vision)
        self.assertFalse(readiness.ready_for_external_control)
        self.assertFalse(readiness.ready_for_first_output)
        self.assertFalse(readiness.ready_for_live_runtime_session)
        self.assertFalse(readiness.ready_for_memory_layer_write)
        self.assertFalse(readiness.ready_for_autonomous_scheduler)

    def test_audit_passes_fixture_events_and_blocks_required_cases(self) -> None:
        pass_cases = {
            "camera": (
                sensor.build_demo_camera_frame_available_event,
                "passed_camera_fixture_event_only",
            ),
            "mic": (
                sensor.build_demo_mic_level_changed_event,
                "passed_mic_fixture_event_only",
            ),
            "idle": (
                sensor.build_demo_host_idle_event,
                "passed_idle_fixture_event_only",
            ),
            "mixed": (
                sensor.build_demo_mixed_host_sensor_event_set,
                "passed_host_body_read_only_sensor_event_shell",
            ),
        }
        for case, (builder, expected_status) in pass_cases.items():
            with self.subTest(case=case):
                self.assertEqual(
                    builder()["host_body_sensor_event_audit"]["audit_status"],
                    expected_status,
                )

        blocked_cases = {
            "real_camera": (
                sensor.build_demo_blocked_real_camera_event,
                "blocked_real_camera_access_detected",
            ),
            "speech": (
                sensor.build_demo_blocked_speech_recognition_event,
                "blocked_speech_recognition_detected",
            ),
            "bridge": (
                sensor.build_demo_blocked_runtime_eventframe_bridge_event,
                "blocked_runtime_eventframe_bridge_detected",
            ),
            "external": (
                sensor.build_demo_blocked_external_control_sensor_event,
                "blocked_external_control_detected",
            ),
            "first": (
                sensor.build_demo_blocked_first_output_sensor_event,
                "blocked_first_output_detected",
            ),
        }
        for case, (builder, expected_status) in blocked_cases.items():
            with self.subTest(blocked_case=case):
                self.assertEqual(
                    builder()["host_body_sensor_event_audit"]["audit_status"],
                    expected_status,
                )

        payload = sensor.build_demo_mixed_host_sensor_event_set()
        audit = sensor.build_host_body_sensor_event_audit(
            host_sensor_event_set=payload["host_body_sensor_event_set"],
            host_sensor_event_summary=payload["host_body_sensor_event_summary"],
            host_body_port_map=payload["host_body_port_map"],
            force_autonomous_scheduler=True,
        )
        self.assertEqual(audit.audit_status, "blocked_forbidden_authority_detected")
        self.assertFalse(audit.no_autonomous_scheduler)
        self.assertTrue(sensor.validate_host_body_sensor_event_audit(payload["host_body_sensor_event_audit"])["valid"])

    def test_renderers_create_summary_and_event_table(self) -> None:
        payload = sensor.build_demo_mixed_host_sensor_event_set()
        summary = payload["rendered_host_sensor_event_summary"]
        table = payload["rendered_host_sensor_event_table"]
        self.assertIn("host_sensor_event_audit=passed_host_body_read_only_sensor_event_shell", summary)
        self.assertIn("camera_frame_available", table)
        self.assertIn("mic_peak_detected", table)
        self.assertIn("host_idle", table)

    def test_cli_commands_work(self) -> None:
        commands = {
            ("show-demo-camera-frame",): "passed_camera_fixture_event_only",
            ("show-demo-camera-change",): "passed_camera_fixture_event_only",
            ("show-demo-mic-level",): "passed_mic_fixture_event_only",
            ("show-demo-mic-peak",): "passed_mic_fixture_event_only",
            ("show-demo-host-idle",): "passed_idle_fixture_event_only",
            ("show-demo-mixed-set",): "passed_host_body_read_only_sensor_event_shell",
            ("show-demo-summary",): "host_sensor_event_summary_recorded",
            ("show-demo-readiness",): "ready_for_host_body_event_runtime_eventframe_bridge_only",
            ("validate-demo-sensor-events",): "passed_host_body_read_only_sensor_event_shell",
            ("show-demo-blocked", "--case", "real-camera"): "blocked_real_camera_access_detected",
            ("show-demo-blocked", "--case", "speech-recognition"): "blocked_speech_recognition_detected",
            ("show-demo-blocked", "--case", "runtime-eventframe-bridge"): "blocked_runtime_eventframe_bridge_detected",
            ("show-demo-blocked", "--case", "external-control"): "blocked_external_control_detected",
            ("show-demo-blocked", "--case", "first-output"): "blocked_first_output_detected",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(SENSOR_CLI, *command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_guided_console_sensor_event_demo_works(self) -> None:
        validation = validate_host_body_sensor_event_from_guided_cradle_growth_console()
        self.assertEqual(validation["guided_console_action"], "host_body_validate_sensor_event_demo")
        self.assertTrue(validation["validation"]["valid"])
        self.assertFalse(validation["camera_connected"])
        self.assertFalse(validation["microphone_connected"])
        self.assertFalse(validation["runtime_eventframe_bridge_created"])
        self.assertFalse(validation["first_output_created"])
        self.assertFalse(validation["external_action_executed"])
        self.assertFalse(validation["memory_layer_write_performed"])

        commands = {
            "host-body-show-camera-frame-event-demo": "camera_frame_available",
            "host-body-show-camera-change-event-demo": "camera_frame_changed",
            "host-body-show-mic-level-event-demo": "mic_level_changed",
            "host-body-show-mic-peak-event-demo": "mic_peak_detected",
            "host-body-show-idle-event-demo": "host_idle",
            "host-body-show-mixed-sensor-event-set-demo": "passed_host_body_read_only_sensor_event_shell",
            "host-body-show-sensor-event-readiness": "ready_for_host_body_event_runtime_eventframe_bridge_only",
            "host-body-validate-sensor-event-demo": "passed_host_body_read_only_sensor_event_shell",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(GUIDED_CLI, command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _host_event(self, event_type: str, source_port_kind: str) -> sensor.HostBodyEventRecord:
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
