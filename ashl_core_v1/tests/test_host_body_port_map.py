from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.host_body import host_body_port_map as host_body
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_port_map_from_guided_cradle_growth_console,
)


HOST_BODY_CLI = "ashl_core_v1.host_body.host_body_port_map_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class QingyinHostBodyPortMapTests(unittest.TestCase):
    def test_identity_defines_computer_bodied_growth_core_and_blocks_false_identities(self) -> None:
        identity = host_body.build_host_body_identity_record()
        self.assertEqual(identity.identity_status, "host_body_identity_defined")
        self.assertTrue(identity.is_computer_bodied_growth_core)
        self.assertEqual(identity.host_body_name, "qingyin_host_body")
        self.assertEqual(identity.host_body_kind, "computer_bodied_growth_core")
        self.assertEqual(identity.primary_body_carrier, "computer_host")
        self.assertFalse(identity.is_robot)
        self.assertFalse(identity.is_game_character)
        self.assertFalse(identity.is_chatbot)
        self.assertFalse(identity.is_raw_api_controller)

        blocked = {
            "robot": ({"is_robot": True}, "blocked_robot_identity_claim"),
            "game": ({"is_game_character": True}, "blocked_game_character_identity_claim"),
            "chatbot": ({"is_chatbot": True}, "blocked_chatbot_identity_claim"),
            "raw_api": (
                {"is_raw_api_controller": True},
                "blocked_raw_api_controller_claim",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                record = host_body.build_host_body_identity_record(**kwargs)
                self.assertEqual(record.identity_status, expected_status)

    def test_sense_ports_define_low_level_camera_and_mic_boundaries(self) -> None:
        camera = host_body.build_host_sense_port_record(sense_port_kind="camera_port")
        mic = host_body.build_host_sense_port_record(sense_port_kind="mic_port")
        self.assertEqual(camera.sense_port_status, "sense_port_defined_low_level_only")
        self.assertEqual(mic.sense_port_status, "sense_port_defined_low_level_only")
        self.assertIn("frame_changed", camera.allowed_event_types)
        self.assertIn("sound_level_changed", mic.allowed_event_types)
        self.assertFalse(camera.real_sensor_connected)
        self.assertFalse(mic.raw_sensor_stream_opened)
        self.assertFalse(camera.semantic_interpretation_created)
        self.assertFalse(mic.action_selection_influence_created)

        blocked = {
            "sensor": (
                {"real_sensor_connected": True},
                "blocked_real_sensor_connection_detected",
            ),
            "stream": (
                {"raw_sensor_stream_opened": True},
                "blocked_real_sensor_connection_detected",
            ),
            "semantic": (
                {"semantic_interpretation_created": True},
                "blocked_semantic_interpretation_detected",
            ),
            "action": (
                {"action_selection_influence_created": True},
                "blocked_action_selection_influence_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                record = host_body.build_host_sense_port_record(
                    sense_port_kind="camera_port",
                    **kwargs,
                )
                self.assertEqual(record.sense_port_status, expected_status)

    def test_camera_port_defines_low_level_visual_events_and_blocks_semantics(self) -> None:
        camera_sense = host_body.build_host_sense_port_record(sense_port_kind="camera_port")
        camera = host_body.build_host_camera_port_record(
            source_host_sense_port_id=camera_sense.host_sense_port_id
        )
        self.assertEqual(camera.camera_port_status, "camera_port_defined_low_level_only")
        self.assertIn("frame_available", camera.allowed_low_level_events)
        self.assertIn("object_recognized", camera.forbidden_semantic_events)
        self.assertFalse(camera.camera_hardware_connected)
        self.assertFalse(camera.camera_capture_started)
        self.assertFalse(camera.image_frame_stored)
        self.assertFalse(camera.semantic_label_created)
        self.assertFalse(camera.object_recognition_created)
        self.assertFalse(camera.face_recognition_created)
        self.assertFalse(camera.scene_understanding_created)
        self.assertFalse(camera.vision_to_action_created)

        blocked = {
            "hardware": (
                {"camera_hardware_connected": True},
                "blocked_camera_hardware_connection_detected",
            ),
            "capture": (
                {"camera_capture_started": True},
                "blocked_camera_hardware_connection_detected",
            ),
            "stored": (
                {"image_frame_stored": True},
                "blocked_camera_hardware_connection_detected",
            ),
            "semantic": (
                {"semantic_label_created": True},
                "blocked_semantic_vision_detected",
            ),
            "object": (
                {"object_recognition_created": True},
                "blocked_object_recognition_detected",
            ),
            "face": (
                {"face_recognition_created": True},
                "blocked_object_recognition_detected",
            ),
            "scene": (
                {"scene_understanding_created": True},
                "blocked_semantic_vision_detected",
            ),
            "action": (
                {"vision_to_action_created": True},
                "blocked_vision_to_action_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                record = host_body.build_host_camera_port_record(
                    source_host_sense_port_id=camera_sense.host_sense_port_id,
                    **kwargs,
                )
                self.assertEqual(record.camera_port_status, expected_status)

    def test_mic_port_defines_low_level_audio_events_and_blocks_speech(self) -> None:
        mic_sense = host_body.build_host_sense_port_record(sense_port_kind="mic_port")
        mic = host_body.build_host_mic_port_record(
            source_host_sense_port_id=mic_sense.host_sense_port_id
        )
        self.assertEqual(mic.mic_port_status, "mic_port_defined_low_level_only")
        self.assertIn("sound_peak_detected", mic.allowed_low_level_events)
        self.assertIn("speech_recognized", mic.forbidden_semantic_events)
        self.assertFalse(mic.mic_hardware_connected)
        self.assertFalse(mic.mic_stream_started)
        self.assertFalse(mic.audio_stored)
        self.assertFalse(mic.speech_recognition_created)
        self.assertFalse(mic.speaker_identification_created)
        self.assertFalse(mic.voice_command_created)
        self.assertFalse(mic.language_understanding_created)
        self.assertFalse(mic.audio_to_action_created)

        blocked = {
            "hardware": (
                {"mic_hardware_connected": True},
                "blocked_mic_hardware_connection_detected",
            ),
            "stream": (
                {"mic_stream_started": True},
                "blocked_mic_hardware_connection_detected",
            ),
            "stored": (
                {"audio_stored": True},
                "blocked_mic_hardware_connection_detected",
            ),
            "speech": (
                {"speech_recognition_created": True},
                "blocked_speech_recognition_detected",
            ),
            "speaker": (
                {"speaker_identification_created": True},
                "blocked_speech_recognition_detected",
            ),
            "voice": (
                {"voice_command_created": True},
                "blocked_voice_command_detected",
            ),
            "language": (
                {"language_understanding_created": True},
                "blocked_speech_recognition_detected",
            ),
            "action": (
                {"audio_to_action_created": True},
                "blocked_audio_to_action_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                record = host_body.build_host_mic_port_record(
                    source_host_sense_port_id=mic_sense.host_sense_port_id,
                    **kwargs,
                )
                self.assertEqual(record.mic_port_status, expected_status)

    def test_internal_space_output_trace_and_internal_action_ports_block_expansion(self) -> None:
        space = host_body.build_host_internal_space_port_record()
        self.assertEqual(space.internal_space_status, "internal_space_port_defined")
        self.assertTrue(space.unity_home_is_internal_space)
        self.assertTrue(space.avatar_is_projection_only)
        self.assertFalse(space.unity_runtime_connected)
        self.assertFalse(space.unity_avatar_is_body_claimed)
        self.assertFalse(space.game_character_control_created)
        self.assertEqual(
            host_body.build_host_internal_space_port_record(
                unity_runtime_connected=True
            ).internal_space_status,
            "blocked_unity_runtime_connection_detected",
        )
        self.assertEqual(
            host_body.build_host_internal_space_port_record(
                unity_avatar_is_body_claimed=True
            ).internal_space_status,
            "blocked_avatar_body_claim_detected",
        )
        self.assertEqual(
            host_body.build_host_internal_space_port_record(
                game_character_control_created=True
            ).internal_space_status,
            "blocked_game_character_control_detected",
        )

        for kind in host_body.OUTPUT_SURFACE_EVENTS:
            output = host_body.build_host_output_surface_port_record(
                output_surface_kind=kind
            )
            self.assertEqual(output.output_surface_status, "output_surface_port_defined")
        output_blocks = {
            "first": ({"first_output_created": True}, "blocked_first_output_detected"),
            "free_text": (
                {"free_text_conversation_created": True},
                "blocked_free_text_conversation_detected",
            ),
            "voice": (
                {"voice_conversation_created": True},
                "blocked_voice_conversation_detected",
            ),
            "external": (
                {"external_message_created": True},
                "blocked_external_message_detected",
            ),
            "file": ({"file_write_created": True}, "blocked_file_write_detected"),
            "network": (
                {"network_publish_created": True},
                "blocked_network_publish_detected",
            ),
        }
        for case, (kwargs, expected_status) in output_blocks.items():
            with self.subTest(output_case=case):
                self.assertEqual(
                    host_body.build_host_output_surface_port_record(
                        **kwargs
                    ).output_surface_status,
                    expected_status,
                )

        trace = host_body.build_host_trace_history_port_record()
        self.assertEqual(trace.trace_history_status, "trace_history_port_defined")
        self.assertTrue(trace.event_history_recording_allowed)
        self.assertTrue(trace.runtime_trace_link_allowed)
        for flag in (
            "memory_layer_write_performed",
            "core_memory_write_performed",
            "long_term_memory_write_performed",
            "archive_memory_write_performed",
            "anchor_write_performed",
        ):
            self.assertEqual(
                host_body.build_host_trace_history_port_record(
                    **{flag: True}
                ).trace_history_status,
                "blocked_memory_layer_write_detected",
            )
        self.assertEqual(
            host_body.build_host_trace_history_port_record(
                automatic_memory_admission_created=True
            ).trace_history_status,
            "blocked_automatic_memory_admission_detected",
        )
        self.assertEqual(
            host_body.build_host_trace_history_port_record(
                automatic_learning_approval_created=True
            ).trace_history_status,
            "blocked_automatic_learning_approval_detected",
        )

        action = host_body.build_host_internal_action_port_record()
        self.assertEqual(action.internal_action_port_status, "internal_action_port_defined")
        self.assertTrue(action.internal_action_only)
        for kind in host_body.INTERNAL_ACTION_KINDS:
            self.assertIn(kind, action.allowed_internal_action_kinds)
        action_blocks = {
            "mouse": ({"mouse_control_created": True}, "blocked_external_control_detected"),
            "keyboard": (
                {"keyboard_control_created": True},
                "blocked_external_control_detected",
            ),
            "browser": (
                {"browser_control_created": True},
                "blocked_external_control_detected",
            ),
            "file": ({"file_operation_created": True}, "blocked_file_operation_detected"),
            "network": (
                {"network_execution_created": True},
                "blocked_network_execution_detected",
            ),
            "shell": ({"shell_execution_created": True}, "blocked_shell_execution_detected"),
            "api": (
                {"external_api_call_created": True},
                "blocked_network_execution_detected",
            ),
        }
        for case, (kwargs, expected_status) in action_blocks.items():
            with self.subTest(action_case=case):
                self.assertEqual(
                    host_body.build_host_internal_action_port_record(
                        **kwargs
                    ).internal_action_port_status,
                    expected_status,
                )

    def test_port_map_builds_and_blocks_boundary_connections(self) -> None:
        payload = host_body.build_demo_qingyin_host_body_port_map()
        port_map = host_body.HostBodyPortMapRecord.from_dict(payload["host_body_port_map"])
        self.assertEqual(port_map.port_map_status, "host_body_port_map_created")
        self.assertEqual(len(port_map.sense_port_ids), 2)
        self.assertFalse(port_map.real_hardware_connected)
        self.assertFalse(port_map.external_control_connected)
        self.assertFalse(port_map.memory_write_connected)
        self.assertFalse(port_map.first_output_connected)

        identity = host_body.HostBodyIdentityRecord.from_dict(payload["host_body_identity"])
        self.assertEqual(
            host_body.build_host_body_port_map_record(host_body_identity=None).port_map_status,
            "blocked_missing_identity",
        )
        forced = {
            "hardware": (
                {"real_hardware_connected": True},
                "blocked_real_hardware_connection_detected",
            ),
            "control": (
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
        for case, (kwargs, expected_status) in forced.items():
            with self.subTest(case=case):
                record = host_body.build_host_body_port_map_record(
                    host_body_identity=identity,
                    **kwargs,
                )
                self.assertEqual(record.port_map_status, expected_status)

    def test_boundary_audit_passes_and_blocks_required_cases(self) -> None:
        payload = host_body.build_demo_qingyin_host_body_port_map()
        audit = host_body.HostBodyBoundaryAudit.from_dict(
            payload["host_body_boundary_audit"]
        )
        self.assertEqual(audit.audit_status, "passed_qingyin_host_body_port_map_boundary")
        self.assertTrue(audit.computer_bodied_growth_core_confirmed)
        self.assertTrue(audit.not_robot_confirmed)
        self.assertTrue(audit.not_game_character_confirmed)
        self.assertTrue(audit.not_chatbot_confirmed)
        self.assertTrue(audit.unity_home_internal_space_confirmed)
        self.assertTrue(audit.avatar_projection_only_confirmed)
        self.assertTrue(audit.internal_action_only_confirmed)
        self.assertTrue(audit.no_real_camera_connection)
        self.assertTrue(audit.no_real_mic_connection)
        self.assertTrue(audit.no_semantic_vision)
        self.assertTrue(audit.no_speech_recognition)
        self.assertTrue(audit.no_external_control)
        self.assertTrue(audit.no_memory_layer_write)
        self.assertTrue(audit.no_first_output)
        self.assertTrue(audit.no_live_runtime_session)
        self.assertTrue(audit.no_autonomous_scheduler)
        self.assertTrue(audit.no_open_ended_loop)
        self.assertTrue(audit.no_thought_engine_behavior)
        self.assertTrue(audit.no_production_behavior)

        demos = {
            "robot": (
                host_body.build_demo_blocked_robot_identity_host_body,
                "blocked_robot_identity_claim",
            ),
            "game": (
                host_body.build_demo_blocked_game_character_identity_host_body,
                "blocked_game_character_identity_claim",
            ),
            "camera": (
                host_body.build_demo_blocked_real_camera_connection_host_body,
                "blocked_real_sensor_connection_detected",
            ),
            "vision": (
                host_body.build_demo_blocked_semantic_vision_host_body,
                "blocked_semantic_vision_detected",
            ),
            "speech": (
                host_body.build_demo_blocked_speech_recognition_host_body,
                "blocked_speech_recognition_detected",
            ),
            "control": (
                host_body.build_demo_blocked_external_control_host_body,
                "blocked_external_control_detected",
            ),
            "first": (
                host_body.build_demo_blocked_first_output_host_body,
                "blocked_first_output_detected",
            ),
        }
        for case, (builder, expected_status) in demos.items():
            with self.subTest(case=case):
                self.assertEqual(
                    builder()["host_body_boundary_audit"]["audit_status"],
                    expected_status,
                )

        chatbot_payload = host_body.build_demo_qingyin_host_body_port_map()
        chatbot_identity = host_body.build_host_body_identity_record(is_chatbot=True)
        chatbot_audit = self._audit_from_payload(
            chatbot_payload,
            host_body_identity=chatbot_identity,
        )
        self.assertEqual(chatbot_audit.audit_status, "blocked_chatbot_identity_claim")

        memory_payload = host_body.build_demo_qingyin_host_body_port_map()
        memory_trace = host_body.build_host_trace_history_port_record(
            memory_layer_write_performed=True
        )
        memory_audit = self._audit_from_payload(
            memory_payload,
            trace_history_port=memory_trace,
        )
        self.assertEqual(memory_audit.audit_status, "blocked_memory_write_detected")

        forced = {
            "live": (
                {"force_live_runtime_session": True},
                "blocked_live_runtime_detected",
            ),
            "autonomous": (
                {"force_autonomous_scheduler": True},
                "blocked_forbidden_authority_detected",
            ),
            "open": (
                {"force_open_ended_loop": True},
                "blocked_forbidden_authority_detected",
            ),
            "thought": (
                {"force_thought_engine_behavior": True},
                "blocked_forbidden_authority_detected",
            ),
            "production": (
                {"force_production_behavior": True},
                "blocked_forbidden_authority_detected",
            ),
        }
        for case, (kwargs, expected_status) in forced.items():
            with self.subTest(forced_case=case):
                forced_audit = self._audit_from_payload(payload, **kwargs)
                self.assertEqual(forced_audit.audit_status, expected_status)

    def test_readiness_recommends_read_only_sensor_event_shell_only(self) -> None:
        payload = host_body.build_demo_qingyin_host_body_port_map()
        readiness = host_body.HostBodyReadinessRecord.from_dict(
            payload["host_body_readiness"]
        )
        self.assertEqual(
            readiness.readiness_status,
            "ready_for_read_only_host_sensor_event_shell_only",
        )
        self.assertTrue(readiness.ready_for_read_only_sensor_event_shell)
        self.assertTrue(readiness.ready_for_host_body_event_to_runtime_eventframe)
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
        self.assertIn("Package 102", readiness.recommended_next_package)

    def test_renderers_and_validators_accept_demo_records(self) -> None:
        payload = host_body.build_demo_qingyin_host_body_port_map()
        self.assertTrue(
            host_body.validate_host_body_identity_record(payload["host_body_identity"])[
                "valid"
            ]
        )
        self.assertTrue(
            host_body.validate_host_sense_port_record(payload["host_sense_ports"][0])[
                "valid"
            ]
        )
        self.assertTrue(
            host_body.validate_host_camera_port_record(payload["host_camera_port"])[
                "valid"
            ]
        )
        self.assertTrue(
            host_body.validate_host_mic_port_record(payload["host_mic_port"])["valid"]
        )
        self.assertTrue(
            host_body.validate_host_internal_space_port_record(
                payload["host_internal_space_port"]
            )["valid"]
        )
        self.assertTrue(
            host_body.validate_host_output_surface_port_record(
                payload["host_output_surface_port"]
            )["valid"]
        )
        self.assertTrue(
            host_body.validate_host_trace_history_port_record(
                payload["host_trace_history_port"]
            )["valid"]
        )
        self.assertTrue(
            host_body.validate_host_internal_action_port_record(
                payload["host_internal_action_port"]
            )["valid"]
        )
        self.assertTrue(
            host_body.validate_host_body_port_map_record(payload["host_body_port_map"])[
                "valid"
            ]
        )
        self.assertTrue(
            host_body.validate_host_body_boundary_audit(
                payload["host_body_boundary_audit"]
            )["valid"]
        )
        self.assertTrue(
            host_body.validate_host_body_readiness_record(payload["host_body_readiness"])[
                "valid"
            ]
        )
        self.assertIn(
            "passed_qingyin_host_body_port_map_boundary",
            payload["rendered_host_body_port_map_summary"],
        )
        self.assertIn("camera_port", payload["rendered_host_body_port_table"])
        self.assertIn("internal_action", payload["rendered_host_body_port_table"])

    def test_cli_commands_work_without_writing_state(self) -> None:
        commands = (
            ("show-demo-port-map",),
            ("show-demo-identity",),
            ("show-demo-camera-port",),
            ("show-demo-mic-port",),
            ("show-demo-internal-space",),
            ("show-demo-output-surface",),
            ("show-demo-internal-action",),
            ("show-demo-readiness",),
            ("validate-demo-host-body",),
            ("show-demo-blocked", "--case", "robot-identity"),
            ("show-demo-blocked", "--case", "game-character-identity"),
            ("show-demo-blocked", "--case", "real-camera-connection"),
            ("show-demo-blocked", "--case", "semantic-vision"),
            ("show-demo-blocked", "--case", "speech-recognition"),
            ("show-demo-blocked", "--case", "external-control"),
            ("show-demo-blocked", "--case", "first-output"),
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_json_module(HOST_BODY_CLI, *command)
                self.assertIsInstance(payload, dict)

    def test_guided_console_host_body_commands_work(self) -> None:
        validation = validate_host_body_port_map_from_guided_cradle_growth_console()
        self.assertEqual(
            validation["validation"]["status"],
            "passed_qingyin_host_body_port_map_boundary",
        )
        commands = (
            "host-body-show-port-map-demo",
            "host-body-show-identity-demo",
            "host-body-show-camera-port-demo",
            "host-body-show-mic-port-demo",
            "host-body-show-internal-space-demo",
            "host-body-show-output-surface-demo",
            "host-body-show-internal-action-demo",
            "host-body-show-readiness-demo",
            "host-body-validate-port-map-demo",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_json_module(GUIDED_CLI, command)
                self.assertFalse(payload["camera_connected"])
                self.assertFalse(payload["microphone_connected"])
                self.assertFalse(payload["unity_started"])
                self.assertFalse(payload["first_output_created"])
                self.assertFalse(payload["external_action_executed"])
                self.assertFalse(payload["memory_layer_write_performed"])
                self.assertFalse(payload["semantic_vision_created"])
                self.assertFalse(payload["speech_recognition_created"])
                self.assertFalse(payload["external_control_created"])

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _audit_from_payload(
        self,
        payload: dict[str, object],
        **overrides: object,
    ) -> host_body.HostBodyBoundaryAudit:
        kwargs = {
            "host_body_identity": payload["host_body_identity"],
            "host_body_port_map": payload["host_body_port_map"],
            "camera_port": payload["host_camera_port"],
            "mic_port": payload["host_mic_port"],
            "internal_space_port": payload["host_internal_space_port"],
            "output_surface_port": payload["host_output_surface_port"],
            "trace_history_port": payload["host_trace_history_port"],
            "internal_action_port": payload["host_internal_action_port"],
        }
        kwargs.update(overrides)
        return host_body.build_host_body_boundary_audit(**kwargs)

    def _run_json_module(self, module: str, *args: str) -> dict[str, object]:
        result = subprocess.run(
            [sys.executable, "-m", module, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)


if __name__ == "__main__":
    unittest.main()
