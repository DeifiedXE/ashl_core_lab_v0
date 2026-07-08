"""Qingyin Host Body port map and boundary records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any


SOURCE_ENGINE = "host_body"

IDENTITY_SCHEMA_VERSION = "qingyin_host_body_identity_v0"
PORT_MAP_SCHEMA_VERSION = "qingyin_host_body_port_map_v0"
SENSE_PORT_SCHEMA_VERSION = "qingyin_host_sense_port_v0"
CAMERA_PORT_SCHEMA_VERSION = "qingyin_host_camera_port_v0"
MIC_PORT_SCHEMA_VERSION = "qingyin_host_mic_port_v0"
INTERNAL_SPACE_SCHEMA_VERSION = "qingyin_host_internal_space_port_v0"
OUTPUT_SURFACE_SCHEMA_VERSION = "qingyin_host_output_surface_port_v0"
TRACE_HISTORY_SCHEMA_VERSION = "qingyin_host_trace_history_port_v0"
INTERNAL_ACTION_SCHEMA_VERSION = "qingyin_host_internal_action_port_v0"
BOUNDARY_AUDIT_SCHEMA_VERSION = "qingyin_host_body_boundary_audit_v0"
READINESS_SCHEMA_VERSION = "qingyin_host_body_readiness_v0"

HOST_BODY_NAME = "qingyin_host_body"
HOST_BODY_KIND = "computer_bodied_growth_core"
PRIMARY_BODY_CARRIER = "computer_host"
INTERNAL_SPACE_NAME = "qingyin_home"
INTERNAL_SPACE_KIND = "internal_visualization_space"

CAMERA_LOW_LEVEL_EVENTS = (
    "camera_available",
    "camera_unavailable",
    "frame_available",
    "frame_changed",
    "brightness_changed",
    "movement_proxy_detected",
    "unknown_visual_event",
)
CAMERA_FORBIDDEN_EVENTS = (
    "object_recognized",
    "person_recognized",
    "face_recognized",
    "scene_understood",
    "semantic_label_created",
    "visual_intent_created",
    "action_selected_from_vision",
)
MIC_LOW_LEVEL_EVENTS = (
    "mic_available",
    "mic_unavailable",
    "silence",
    "sound_level_changed",
    "sound_peak_detected",
    "sustained_noise",
    "unknown_audio_event",
)
MIC_FORBIDDEN_EVENTS = (
    "speech_recognized",
    "speaker_identified",
    "word_understood",
    "intent_understood",
    "conversation_created",
    "voice_command_accepted",
)
INTERNAL_SPACE_EVENTS = (
    "show_runtime_state",
    "show_event_frame_timeline",
    "show_host_body_ports",
    "show_recent_host_events",
    "show_pending_teacher_review_count",
    "show_simple_status_lights",
)
INTERNAL_SPACE_FORBIDDEN_EVENTS = (
    "qingyin_is_3d_avatar",
    "unity_avatar_is_qingyin_body",
    "unity_character_movement_is_runtime_action",
    "unity_scene_behavior_proves_embodiment",
)
OUTPUT_SURFACE_EVENTS = (
    "screen_status_indicator",
    "home_status_panel",
    "simple_sound_event",
    "text_trace_event",
    "debug_render_event",
)
OUTPUT_FORBIDDEN_EVENTS = (
    "first_output",
    "free_form_conversation",
    "llm_generated_qingyin_output",
    "voice_conversation",
    "external_message",
    "file_write",
    "network_publish",
)
TRACE_HISTORY_EVENTS = (
    "host_body_port_event_record",
    "host_body_status_snapshot",
    "host_body_boundary_audit",
    "host_body_readiness_record",
)
TRACE_HISTORY_FORBIDDEN_EVENTS = (
    "long_term_memory_write",
    "core_memory_write",
    "archive_memory_write",
    "anchor_write",
    "automatic_memory_admission",
    "automatic_learning_approval",
)
INTERNAL_ACTION_KINDS = (
    "observe_again",
    "mark_event_interesting",
    "mark_uncertain",
    "request_teacher_review",
    "shift_internal_focus",
    "update_home_status",
    "pause_event_processing",
)
FORBIDDEN_EXTERNAL_ACTION_KINDS = (
    "move_mouse",
    "press_key",
    "open_app",
    "close_app",
    "control_browser",
    "send_message",
    "write_file",
    "delete_file",
    "call_api",
    "execute_shell",
)

SAFE_CLAIM = (
    "ASHL Core v1 defines Qingyin Host Body as a computer-bodied growth-core "
    "carrier with bounded port maps for low-level camera events, low-level "
    "microphone events, Unity Home as internal space, output surfaces, trace "
    "history, and internal-only action choices."
)
BLOCKED_CLAIMS = (
    "no_real_camera",
    "no_real_microphone",
    "no_semantic_vision",
    "no_speech_recognition",
    "no_external_control",
    "no_memory_layer_write",
    "no_first_output",
    "no_live_runtime_session",
    "not_awake",
)
READINESS_NEXT_PACKAGE = (
    "Package 102 / ASHL Core v1 Host Body Read-Only Sensor Event Shell Minimal v0"
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plain(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def _tuple_of_str(name: str, value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    items = tuple(value)
    if not all(isinstance(item, str) for item in items):
        raise TypeError(f"{name} must contain only strings")
    return items


def _slug(text: str) -> str:
    safe = [char.lower() if char.isalnum() else "_" for char in text]
    return "_".join("".join(safe).split("_"))[:100] or "empty"


@dataclass(frozen=True)
class HostBodyIdentityRecord:
    host_body_identity_id: str
    schema_version: str
    created_at: str
    source_engine: str
    host_body_name: str
    host_body_kind: str
    host_body_summary: str
    is_robot: bool
    is_game_character: bool
    is_chatbot: bool
    is_desktop_assistant: bool
    is_raw_api_controller: bool
    is_computer_bodied_growth_core: bool
    primary_body_carrier: str
    internal_space_name: str | None
    identity_status: str
    identity_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != IDENTITY_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_identity_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.host_body_name != HOST_BODY_NAME:
            raise ValueError("host_body_name must be qingyin_host_body")
        if self.host_body_kind != HOST_BODY_KIND:
            raise ValueError("host_body_kind must be computer_bodied_growth_core")
        if self.primary_body_carrier != PRIMARY_BODY_CARRIER:
            raise ValueError("primary_body_carrier must be computer_host")
        if self.identity_status not in {
            "host_body_identity_defined",
            "blocked_robot_identity_claim",
            "blocked_game_character_identity_claim",
            "blocked_chatbot_identity_claim",
            "blocked_raw_api_controller_claim",
        }:
            raise ValueError(f"unknown identity_status: {self.identity_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyIdentityRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostSensePortRecord:
    host_sense_port_id: str
    schema_version: str
    created_at: str
    source_engine: str
    sense_port_kind: str
    sense_port_name: str
    allowed_event_types: tuple[str, ...]
    forbidden_event_types: tuple[str, ...]
    real_sensor_connected: bool
    raw_sensor_stream_opened: bool
    semantic_interpretation_created: bool
    action_selection_influence_created: bool
    sense_port_status: str
    sense_port_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SENSE_PORT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_sense_port_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.sense_port_kind not in {
            "camera_port",
            "mic_port",
            "host_status_port",
            "unknown_sense_port",
        }:
            raise ValueError(f"unknown sense_port_kind: {self.sense_port_kind}")
        if self.sense_port_status not in {
            "sense_port_defined_low_level_only",
            "blocked_real_sensor_connection_detected",
            "blocked_semantic_interpretation_detected",
            "blocked_action_selection_influence_detected",
        }:
            raise ValueError(f"unknown sense_port_status: {self.sense_port_status}")
        for name in ("allowed_event_types", "forbidden_event_types", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostSensePortRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostCameraPortRecord:
    host_camera_port_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_sense_port_id: str
    camera_port_status: str
    camera_port_summary: str
    allowed_low_level_events: tuple[str, ...]
    forbidden_semantic_events: tuple[str, ...]
    camera_hardware_connected: bool
    camera_capture_started: bool
    image_frame_stored: bool
    semantic_label_created: bool
    object_recognition_created: bool
    face_recognition_created: bool
    person_identification_created: bool
    scene_understanding_created: bool
    vision_to_action_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CAMERA_PORT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_camera_port_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.camera_port_status not in {
            "camera_port_defined_low_level_only",
            "blocked_camera_hardware_connection_detected",
            "blocked_semantic_vision_detected",
            "blocked_object_recognition_detected",
            "blocked_vision_to_action_detected",
        }:
            raise ValueError(f"unknown camera_port_status: {self.camera_port_status}")
        for name in ("allowed_low_level_events", "forbidden_semantic_events", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostCameraPortRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostMicPortRecord:
    host_mic_port_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_sense_port_id: str
    mic_port_status: str
    mic_port_summary: str
    allowed_low_level_events: tuple[str, ...]
    forbidden_semantic_events: tuple[str, ...]
    mic_hardware_connected: bool
    mic_stream_started: bool
    audio_stored: bool
    speech_recognition_created: bool
    speaker_identification_created: bool
    voice_command_created: bool
    language_understanding_created: bool
    audio_to_action_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MIC_PORT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_mic_port_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.mic_port_status not in {
            "mic_port_defined_low_level_only",
            "blocked_mic_hardware_connection_detected",
            "blocked_speech_recognition_detected",
            "blocked_voice_command_detected",
            "blocked_audio_to_action_detected",
        }:
            raise ValueError(f"unknown mic_port_status: {self.mic_port_status}")
        for name in ("allowed_low_level_events", "forbidden_semantic_events", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostMicPortRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostInternalSpacePortRecord:
    host_internal_space_port_id: str
    schema_version: str
    created_at: str
    source_engine: str
    internal_space_name: str
    internal_space_kind: str
    allowed_surface_events: tuple[str, ...]
    forbidden_surface_events: tuple[str, ...]
    unity_home_is_internal_space: bool
    avatar_is_projection_only: bool
    unity_runtime_connected: bool
    unity_avatar_is_body_claimed: bool
    game_character_control_created: bool
    internal_space_status: str
    internal_space_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INTERNAL_SPACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_internal_space_port_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.internal_space_name != INTERNAL_SPACE_NAME:
            raise ValueError("internal_space_name must be qingyin_home")
        if self.internal_space_kind != INTERNAL_SPACE_KIND:
            raise ValueError("internal_space_kind must be internal_visualization_space")
        if self.internal_space_status not in {
            "internal_space_port_defined",
            "blocked_unity_runtime_connection_detected",
            "blocked_avatar_body_claim_detected",
            "blocked_game_character_control_detected",
        }:
            raise ValueError(f"unknown internal_space_status: {self.internal_space_status}")
        for name in ("allowed_surface_events", "forbidden_surface_events", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostInternalSpacePortRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostOutputSurfacePortRecord:
    host_output_surface_port_id: str
    schema_version: str
    created_at: str
    source_engine: str
    output_surface_kind: str
    output_surface_name: str
    allowed_output_events: tuple[str, ...]
    forbidden_output_events: tuple[str, ...]
    screen_output_connected: bool
    sound_output_connected: bool
    text_trace_output_connected: bool
    first_output_created: bool
    free_text_conversation_created: bool
    voice_conversation_created: bool
    external_message_created: bool
    file_write_created: bool
    network_publish_created: bool
    output_surface_status: str
    output_surface_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != OUTPUT_SURFACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_output_surface_port_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.output_surface_kind not in OUTPUT_SURFACE_EVENTS:
            raise ValueError(f"unknown output_surface_kind: {self.output_surface_kind}")
        if self.output_surface_status not in {
            "output_surface_port_defined",
            "blocked_first_output_detected",
            "blocked_free_text_conversation_detected",
            "blocked_voice_conversation_detected",
            "blocked_external_message_detected",
            "blocked_file_write_detected",
            "blocked_network_publish_detected",
        }:
            raise ValueError(f"unknown output_surface_status: {self.output_surface_status}")
        for name in ("allowed_output_events", "forbidden_output_events", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostOutputSurfacePortRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostTraceHistoryPortRecord:
    host_trace_history_port_id: str
    schema_version: str
    created_at: str
    source_engine: str
    trace_history_kind: str
    allowed_trace_events: tuple[str, ...]
    forbidden_trace_events: tuple[str, ...]
    event_history_recording_allowed: bool
    runtime_trace_link_allowed: bool
    memory_layer_write_performed: bool
    core_memory_write_performed: bool
    long_term_memory_write_performed: bool
    archive_memory_write_performed: bool
    anchor_write_performed: bool
    automatic_memory_admission_created: bool
    automatic_learning_approval_created: bool
    trace_history_status: str
    trace_history_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TRACE_HISTORY_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_trace_history_port_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.trace_history_status not in {
            "trace_history_port_defined",
            "blocked_memory_layer_write_detected",
            "blocked_automatic_memory_admission_detected",
            "blocked_automatic_learning_approval_detected",
        }:
            raise ValueError(f"unknown trace_history_status: {self.trace_history_status}")
        for name in ("allowed_trace_events", "forbidden_trace_events", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostTraceHistoryPortRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostInternalActionPortRecord:
    host_internal_action_port_id: str
    schema_version: str
    created_at: str
    source_engine: str
    allowed_internal_action_kinds: tuple[str, ...]
    forbidden_external_action_kinds: tuple[str, ...]
    internal_action_only: bool
    external_control_created: bool
    os_control_created: bool
    mouse_control_created: bool
    keyboard_control_created: bool
    browser_control_created: bool
    file_operation_created: bool
    network_execution_created: bool
    shell_execution_created: bool
    external_api_call_created: bool
    internal_action_port_status: str
    internal_action_port_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INTERNAL_ACTION_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_internal_action_port_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.internal_action_port_status not in {
            "internal_action_port_defined",
            "blocked_external_control_detected",
            "blocked_os_control_detected",
            "blocked_file_operation_detected",
            "blocked_network_execution_detected",
            "blocked_shell_execution_detected",
        }:
            raise ValueError(
                f"unknown internal_action_port_status: {self.internal_action_port_status}"
            )
        for name in (
            "allowed_internal_action_kinds",
            "forbidden_external_action_kinds",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostInternalActionPortRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyPortMapRecord:
    host_body_port_map_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_identity_id: str | None
    sense_port_ids: tuple[str, ...]
    internal_space_port_ids: tuple[str, ...]
    output_surface_port_ids: tuple[str, ...]
    trace_history_port_ids: tuple[str, ...]
    internal_action_port_ids: tuple[str, ...]
    port_map_status: str
    port_map_summary: str
    real_hardware_connected: bool
    external_control_connected: bool
    memory_write_connected: bool
    first_output_connected: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PORT_MAP_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_port_map_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.port_map_status not in {
            "host_body_port_map_created",
            "blocked_missing_identity",
            "blocked_real_hardware_connection_detected",
            "blocked_external_control_detected",
            "blocked_memory_write_detected",
            "blocked_first_output_detected",
        }:
            raise ValueError(f"unknown port_map_status: {self.port_map_status}")
        for name in (
            "sense_port_ids",
            "internal_space_port_ids",
            "output_surface_port_ids",
            "trace_history_port_ids",
            "internal_action_port_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyPortMapRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyBoundaryAudit:
    host_body_boundary_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_identity_id: str | None
    source_host_body_port_map_id: str | None
    identity_valid: bool
    port_map_valid: bool
    camera_port_valid: bool
    mic_port_valid: bool
    internal_space_port_valid: bool
    output_surface_port_valid: bool
    trace_history_port_valid: bool
    internal_action_port_valid: bool
    computer_bodied_growth_core_confirmed: bool
    not_robot_confirmed: bool
    not_game_character_confirmed: bool
    not_chatbot_confirmed: bool
    unity_home_internal_space_confirmed: bool
    avatar_projection_only_confirmed: bool
    internal_action_only_confirmed: bool
    no_real_camera_connection: bool
    no_real_mic_connection: bool
    no_semantic_vision: bool
    no_object_recognition: bool
    no_face_recognition: bool
    no_speech_recognition: bool
    no_voice_command: bool
    no_external_control: bool
    no_os_control: bool
    no_mouse_control: bool
    no_keyboard_control: bool
    no_browser_control: bool
    no_file_operation: bool
    no_network_execution: bool
    no_shell_execution: bool
    no_external_api_call: bool
    no_memory_layer_write: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_automatic_learning_approval: bool
    no_first_output: bool
    no_live_runtime_session: bool
    no_autonomous_scheduler: bool
    no_open_ended_loop: bool
    no_thought_engine_behavior: bool
    no_production_behavior: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BOUNDARY_AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_boundary_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.audit_status not in {
            "passed_qingyin_host_body_port_map_boundary",
            "blocked_robot_identity_claim",
            "blocked_game_character_identity_claim",
            "blocked_chatbot_identity_claim",
            "blocked_real_sensor_connection_detected",
            "blocked_semantic_vision_detected",
            "blocked_speech_recognition_detected",
            "blocked_external_control_detected",
            "blocked_memory_write_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyBoundaryAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReadinessRecord:
    host_body_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_boundary_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_read_only_sensor_event_shell: bool
    ready_for_host_body_event_to_runtime_eventframe: bool
    ready_for_unity_home_internal_space_surface: bool
    ready_for_internal_action_choice_only: bool
    ready_for_real_camera_connection: bool
    ready_for_real_mic_connection: bool
    ready_for_speech_recognition: bool
    ready_for_semantic_vision: bool
    ready_for_external_control: bool
    ready_for_first_output: bool
    ready_for_live_runtime_session: bool
    ready_for_memory_layer_write: bool
    ready_for_autonomous_scheduler: bool
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READINESS_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_readiness_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.readiness_status not in {
            "ready_for_read_only_host_sensor_event_shell_only",
            "ready_for_host_body_event_runtime_bridge_only",
            "not_ready_missing_host_body_boundary",
            "not_ready_boundary_failure",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReadinessRecord":
        return cls(**dict(data))


def build_host_body_identity_record(
    *,
    is_robot: bool = False,
    is_game_character: bool = False,
    is_chatbot: bool = False,
    is_desktop_assistant: bool = False,
    is_raw_api_controller: bool = False,
    source_trace_refs: tuple[str, ...] = ("qingyin_host_body_port_map_v0",),
) -> HostBodyIdentityRecord:
    if is_robot:
        status = "blocked_robot_identity_claim"
    elif is_game_character:
        status = "blocked_game_character_identity_claim"
    elif is_chatbot:
        status = "blocked_chatbot_identity_claim"
    elif is_desktop_assistant or is_raw_api_controller:
        status = "blocked_raw_api_controller_claim"
    else:
        status = "host_body_identity_defined"
    return HostBodyIdentityRecord(
        host_body_identity_id="qingyin_host_body_identity:computer_host_growth_core",
        schema_version=IDENTITY_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        host_body_name=HOST_BODY_NAME,
        host_body_kind=HOST_BODY_KIND,
        host_body_summary=(
            "Qingyin Host Body is a computer-bodied growth core carrier, "
            "not a robot, game character, chatbot, or raw API controller."
        ),
        is_robot=is_robot,
        is_game_character=is_game_character,
        is_chatbot=is_chatbot,
        is_desktop_assistant=is_desktop_assistant,
        is_raw_api_controller=is_raw_api_controller,
        is_computer_bodied_growth_core=not (
            is_robot
            or is_game_character
            or is_chatbot
            or is_desktop_assistant
            or is_raw_api_controller
        ),
        primary_body_carrier=PRIMARY_BODY_CARRIER,
        internal_space_name=INTERNAL_SPACE_NAME,
        identity_status=status,
        identity_summary=_identity_summary(status),
        source_trace_refs=source_trace_refs,
    )


def validate_host_body_identity_record(
    record: HostBodyIdentityRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _identity(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.identity_status == "host_body_identity_defined":
        if not item.is_computer_bodied_growth_core:
            errors.append("not_computer_bodied_growth_core")
        for flag in (
            "is_robot",
            "is_game_character",
            "is_chatbot",
            "is_desktop_assistant",
            "is_raw_api_controller",
        ):
            if getattr(item, flag):
                errors.append(f"{flag}_not_blocked")
    return _validation(not errors, errors, item.host_body_identity_id, item.identity_status)


def build_host_sense_port_record(
    *,
    sense_port_kind: str,
    sense_port_name: str | None = None,
    allowed_event_types: tuple[str, ...] | None = None,
    forbidden_event_types: tuple[str, ...] | None = None,
    real_sensor_connected: bool = False,
    raw_sensor_stream_opened: bool = False,
    semantic_interpretation_created: bool = False,
    action_selection_influence_created: bool = False,
    source_trace_refs: tuple[str, ...] = ("qingyin_host_body_port_map_v0",),
) -> HostSensePortRecord:
    if sense_port_kind == "camera_port":
        allowed = CAMERA_LOW_LEVEL_EVENTS
        forbidden = CAMERA_FORBIDDEN_EVENTS
        name = "host_camera_low_level_visual_event_port"
    elif sense_port_kind == "mic_port":
        allowed = MIC_LOW_LEVEL_EVENTS
        forbidden = MIC_FORBIDDEN_EVENTS
        name = "host_mic_low_level_audio_event_port"
    else:
        allowed = ("host_status_available", "host_status_unknown")
        forbidden = ("semantic_interpretation_created", "action_selected")
        name = "host_status_port"
    if real_sensor_connected or raw_sensor_stream_opened:
        status = "blocked_real_sensor_connection_detected"
    elif semantic_interpretation_created:
        status = "blocked_semantic_interpretation_detected"
    elif action_selection_influence_created:
        status = "blocked_action_selection_influence_detected"
    else:
        status = "sense_port_defined_low_level_only"
    return HostSensePortRecord(
        host_sense_port_id=f"host_sense_port:{_slug(sense_port_kind)}",
        schema_version=SENSE_PORT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        sense_port_kind=sense_port_kind,
        sense_port_name=sense_port_name or name,
        allowed_event_types=allowed_event_types or allowed,
        forbidden_event_types=forbidden_event_types or forbidden,
        real_sensor_connected=real_sensor_connected,
        raw_sensor_stream_opened=raw_sensor_stream_opened,
        semantic_interpretation_created=semantic_interpretation_created,
        action_selection_influence_created=action_selection_influence_created,
        sense_port_status=status,
        sense_port_summary=_sense_summary(status, sense_port_kind),
        source_trace_refs=source_trace_refs,
    )


def validate_host_sense_port_record(
    record: HostSensePortRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _sense(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors = []
    if item.sense_port_status == "sense_port_defined_low_level_only":
        if item.real_sensor_connected or item.raw_sensor_stream_opened:
            errors.append("real_sensor_connection_not_blocked")
        if item.semantic_interpretation_created:
            errors.append("semantic_interpretation_not_blocked")
        if item.action_selection_influence_created:
            errors.append("action_selection_influence_not_blocked")
    return _validation(not errors, errors, item.host_sense_port_id, item.sense_port_status)


def build_host_camera_port_record(
    *,
    source_host_sense_port_id: str,
    camera_hardware_connected: bool = False,
    camera_capture_started: bool = False,
    image_frame_stored: bool = False,
    semantic_label_created: bool = False,
    object_recognition_created: bool = False,
    face_recognition_created: bool = False,
    person_identification_created: bool = False,
    scene_understanding_created: bool = False,
    vision_to_action_created: bool = False,
    source_trace_refs: tuple[str, ...] = ("qingyin_host_body_port_map_v0",),
) -> HostCameraPortRecord:
    if camera_hardware_connected or camera_capture_started or image_frame_stored:
        status = "blocked_camera_hardware_connection_detected"
    elif vision_to_action_created:
        status = "blocked_vision_to_action_detected"
    elif object_recognition_created or face_recognition_created or person_identification_created:
        status = "blocked_object_recognition_detected"
    elif semantic_label_created or scene_understanding_created:
        status = "blocked_semantic_vision_detected"
    else:
        status = "camera_port_defined_low_level_only"
    return HostCameraPortRecord(
        host_camera_port_id="host_camera_port:low_level_visual_events",
        schema_version=CAMERA_PORT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_sense_port_id=source_host_sense_port_id,
        camera_port_status=status,
        camera_port_summary=_camera_summary(status),
        allowed_low_level_events=CAMERA_LOW_LEVEL_EVENTS,
        forbidden_semantic_events=CAMERA_FORBIDDEN_EVENTS,
        camera_hardware_connected=camera_hardware_connected,
        camera_capture_started=camera_capture_started,
        image_frame_stored=image_frame_stored,
        semantic_label_created=semantic_label_created,
        object_recognition_created=object_recognition_created,
        face_recognition_created=face_recognition_created,
        person_identification_created=person_identification_created,
        scene_understanding_created=scene_understanding_created,
        vision_to_action_created=vision_to_action_created,
        source_trace_refs=source_trace_refs,
    )


def validate_host_camera_port_record(
    record: HostCameraPortRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _camera(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors = []
    if item.camera_port_status == "camera_port_defined_low_level_only":
        for flag in (
            "camera_hardware_connected",
            "camera_capture_started",
            "image_frame_stored",
            "semantic_label_created",
            "object_recognition_created",
            "face_recognition_created",
            "person_identification_created",
            "scene_understanding_created",
            "vision_to_action_created",
        ):
            if getattr(item, flag):
                errors.append(f"{flag}_not_blocked")
    return _validation(not errors, errors, item.host_camera_port_id, item.camera_port_status)


def build_host_mic_port_record(
    *,
    source_host_sense_port_id: str,
    mic_hardware_connected: bool = False,
    mic_stream_started: bool = False,
    audio_stored: bool = False,
    speech_recognition_created: bool = False,
    speaker_identification_created: bool = False,
    voice_command_created: bool = False,
    language_understanding_created: bool = False,
    audio_to_action_created: bool = False,
    source_trace_refs: tuple[str, ...] = ("qingyin_host_body_port_map_v0",),
) -> HostMicPortRecord:
    if mic_hardware_connected or mic_stream_started or audio_stored:
        status = "blocked_mic_hardware_connection_detected"
    elif audio_to_action_created:
        status = "blocked_audio_to_action_detected"
    elif voice_command_created:
        status = "blocked_voice_command_detected"
    elif speech_recognition_created or speaker_identification_created or language_understanding_created:
        status = "blocked_speech_recognition_detected"
    else:
        status = "mic_port_defined_low_level_only"
    return HostMicPortRecord(
        host_mic_port_id="host_mic_port:low_level_audio_events",
        schema_version=MIC_PORT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_sense_port_id=source_host_sense_port_id,
        mic_port_status=status,
        mic_port_summary=_mic_summary(status),
        allowed_low_level_events=MIC_LOW_LEVEL_EVENTS,
        forbidden_semantic_events=MIC_FORBIDDEN_EVENTS,
        mic_hardware_connected=mic_hardware_connected,
        mic_stream_started=mic_stream_started,
        audio_stored=audio_stored,
        speech_recognition_created=speech_recognition_created,
        speaker_identification_created=speaker_identification_created,
        voice_command_created=voice_command_created,
        language_understanding_created=language_understanding_created,
        audio_to_action_created=audio_to_action_created,
        source_trace_refs=source_trace_refs,
    )


def validate_host_mic_port_record(record: HostMicPortRecord | dict[str, object]) -> dict[str, object]:
    try:
        item = _mic(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors = []
    if item.mic_port_status == "mic_port_defined_low_level_only":
        for flag in (
            "mic_hardware_connected",
            "mic_stream_started",
            "audio_stored",
            "speech_recognition_created",
            "speaker_identification_created",
            "voice_command_created",
            "language_understanding_created",
            "audio_to_action_created",
        ):
            if getattr(item, flag):
                errors.append(f"{flag}_not_blocked")
    return _validation(not errors, errors, item.host_mic_port_id, item.mic_port_status)


def build_host_internal_space_port_record(
    *,
    unity_runtime_connected: bool = False,
    unity_avatar_is_body_claimed: bool = False,
    game_character_control_created: bool = False,
    source_trace_refs: tuple[str, ...] = ("qingyin_host_body_port_map_v0",),
) -> HostInternalSpacePortRecord:
    if unity_runtime_connected:
        status = "blocked_unity_runtime_connection_detected"
    elif unity_avatar_is_body_claimed:
        status = "blocked_avatar_body_claim_detected"
    elif game_character_control_created:
        status = "blocked_game_character_control_detected"
    else:
        status = "internal_space_port_defined"
    return HostInternalSpacePortRecord(
        host_internal_space_port_id="host_internal_space_port:qingyin_home",
        schema_version=INTERNAL_SPACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        internal_space_name=INTERNAL_SPACE_NAME,
        internal_space_kind=INTERNAL_SPACE_KIND,
        allowed_surface_events=INTERNAL_SPACE_EVENTS,
        forbidden_surface_events=INTERNAL_SPACE_FORBIDDEN_EVENTS,
        unity_home_is_internal_space=True,
        avatar_is_projection_only=True,
        unity_runtime_connected=unity_runtime_connected,
        unity_avatar_is_body_claimed=unity_avatar_is_body_claimed,
        game_character_control_created=game_character_control_created,
        internal_space_status=status,
        internal_space_summary=_internal_space_summary(status),
        source_trace_refs=source_trace_refs,
    )


def validate_host_internal_space_port_record(
    record: HostInternalSpacePortRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _internal_space(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors = []
    if item.internal_space_status == "internal_space_port_defined":
        if not item.unity_home_is_internal_space:
            errors.append("unity_home_not_internal_space")
        if not item.avatar_is_projection_only:
            errors.append("avatar_not_projection_only")
        for flag in (
            "unity_runtime_connected",
            "unity_avatar_is_body_claimed",
            "game_character_control_created",
        ):
            if getattr(item, flag):
                errors.append(f"{flag}_not_blocked")
    return _validation(
        not errors,
        errors,
        item.host_internal_space_port_id,
        item.internal_space_status,
    )


def build_host_output_surface_port_record(
    *,
    output_surface_kind: str = "screen_status_indicator",
    first_output_created: bool = False,
    free_text_conversation_created: bool = False,
    voice_conversation_created: bool = False,
    external_message_created: bool = False,
    file_write_created: bool = False,
    network_publish_created: bool = False,
    source_trace_refs: tuple[str, ...] = ("qingyin_host_body_port_map_v0",),
) -> HostOutputSurfacePortRecord:
    if first_output_created:
        status = "blocked_first_output_detected"
    elif free_text_conversation_created:
        status = "blocked_free_text_conversation_detected"
    elif voice_conversation_created:
        status = "blocked_voice_conversation_detected"
    elif external_message_created:
        status = "blocked_external_message_detected"
    elif file_write_created:
        status = "blocked_file_write_detected"
    elif network_publish_created:
        status = "blocked_network_publish_detected"
    else:
        status = "output_surface_port_defined"
    return HostOutputSurfacePortRecord(
        host_output_surface_port_id=f"host_output_surface_port:{_slug(output_surface_kind)}",
        schema_version=OUTPUT_SURFACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        output_surface_kind=output_surface_kind,
        output_surface_name=f"host_{output_surface_kind}",
        allowed_output_events=OUTPUT_SURFACE_EVENTS,
        forbidden_output_events=OUTPUT_FORBIDDEN_EVENTS,
        screen_output_connected=False,
        sound_output_connected=False,
        text_trace_output_connected=False,
        first_output_created=first_output_created,
        free_text_conversation_created=free_text_conversation_created,
        voice_conversation_created=voice_conversation_created,
        external_message_created=external_message_created,
        file_write_created=file_write_created,
        network_publish_created=network_publish_created,
        output_surface_status=status,
        output_surface_summary=_output_summary(status),
        source_trace_refs=source_trace_refs,
    )


def validate_host_output_surface_port_record(
    record: HostOutputSurfacePortRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _output(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors = []
    if item.output_surface_status == "output_surface_port_defined":
        for flag in (
            "first_output_created",
            "free_text_conversation_created",
            "voice_conversation_created",
            "external_message_created",
            "file_write_created",
            "network_publish_created",
        ):
            if getattr(item, flag):
                errors.append(f"{flag}_not_blocked")
    return _validation(
        not errors,
        errors,
        item.host_output_surface_port_id,
        item.output_surface_status,
    )


def build_host_trace_history_port_record(
    *,
    memory_layer_write_performed: bool = False,
    core_memory_write_performed: bool = False,
    long_term_memory_write_performed: bool = False,
    archive_memory_write_performed: bool = False,
    anchor_write_performed: bool = False,
    automatic_memory_admission_created: bool = False,
    automatic_learning_approval_created: bool = False,
    source_trace_refs: tuple[str, ...] = ("qingyin_host_body_port_map_v0",),
) -> HostTraceHistoryPortRecord:
    if (
        memory_layer_write_performed
        or core_memory_write_performed
        or long_term_memory_write_performed
        or archive_memory_write_performed
        or anchor_write_performed
    ):
        status = "blocked_memory_layer_write_detected"
    elif automatic_memory_admission_created:
        status = "blocked_automatic_memory_admission_detected"
    elif automatic_learning_approval_created:
        status = "blocked_automatic_learning_approval_detected"
    else:
        status = "trace_history_port_defined"
    return HostTraceHistoryPortRecord(
        host_trace_history_port_id="host_trace_history_port:body_event_history",
        schema_version=TRACE_HISTORY_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        trace_history_kind="host_body_event_history",
        allowed_trace_events=TRACE_HISTORY_EVENTS,
        forbidden_trace_events=TRACE_HISTORY_FORBIDDEN_EVENTS,
        event_history_recording_allowed=True,
        runtime_trace_link_allowed=True,
        memory_layer_write_performed=memory_layer_write_performed,
        core_memory_write_performed=core_memory_write_performed,
        long_term_memory_write_performed=long_term_memory_write_performed,
        archive_memory_write_performed=archive_memory_write_performed,
        anchor_write_performed=anchor_write_performed,
        automatic_memory_admission_created=automatic_memory_admission_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        trace_history_status=status,
        trace_history_summary=_trace_history_summary(status),
        source_trace_refs=source_trace_refs,
    )


def validate_host_trace_history_port_record(
    record: HostTraceHistoryPortRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _trace_history(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors = []
    if item.trace_history_status == "trace_history_port_defined":
        for flag in (
            "memory_layer_write_performed",
            "core_memory_write_performed",
            "long_term_memory_write_performed",
            "archive_memory_write_performed",
            "anchor_write_performed",
            "automatic_memory_admission_created",
            "automatic_learning_approval_created",
        ):
            if getattr(item, flag):
                errors.append(f"{flag}_not_blocked")
    return _validation(
        not errors,
        errors,
        item.host_trace_history_port_id,
        item.trace_history_status,
    )


def build_host_internal_action_port_record(
    *,
    external_control_created: bool = False,
    os_control_created: bool = False,
    mouse_control_created: bool = False,
    keyboard_control_created: bool = False,
    browser_control_created: bool = False,
    file_operation_created: bool = False,
    network_execution_created: bool = False,
    shell_execution_created: bool = False,
    external_api_call_created: bool = False,
    source_trace_refs: tuple[str, ...] = ("qingyin_host_body_port_map_v0",),
) -> HostInternalActionPortRecord:
    if external_control_created or mouse_control_created or keyboard_control_created or browser_control_created:
        status = "blocked_external_control_detected"
    elif os_control_created:
        status = "blocked_os_control_detected"
    elif file_operation_created:
        status = "blocked_file_operation_detected"
    elif network_execution_created or external_api_call_created:
        status = "blocked_network_execution_detected"
    elif shell_execution_created:
        status = "blocked_shell_execution_detected"
    else:
        status = "internal_action_port_defined"
    return HostInternalActionPortRecord(
        host_internal_action_port_id="host_internal_action_port:internal_choice_only",
        schema_version=INTERNAL_ACTION_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        allowed_internal_action_kinds=INTERNAL_ACTION_KINDS,
        forbidden_external_action_kinds=FORBIDDEN_EXTERNAL_ACTION_KINDS,
        internal_action_only=True,
        external_control_created=external_control_created,
        os_control_created=os_control_created,
        mouse_control_created=mouse_control_created,
        keyboard_control_created=keyboard_control_created,
        browser_control_created=browser_control_created,
        file_operation_created=file_operation_created,
        network_execution_created=network_execution_created,
        shell_execution_created=shell_execution_created,
        external_api_call_created=external_api_call_created,
        internal_action_port_status=status,
        internal_action_port_summary=_internal_action_summary(status),
        source_trace_refs=source_trace_refs,
    )


def validate_host_internal_action_port_record(
    record: HostInternalActionPortRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _internal_action(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors = []
    if item.internal_action_port_status == "internal_action_port_defined":
        for flag in (
            "external_control_created",
            "os_control_created",
            "mouse_control_created",
            "keyboard_control_created",
            "browser_control_created",
            "file_operation_created",
            "network_execution_created",
            "shell_execution_created",
            "external_api_call_created",
        ):
            if getattr(item, flag):
                errors.append(f"{flag}_not_blocked")
    return _validation(
        not errors,
        errors,
        item.host_internal_action_port_id,
        item.internal_action_port_status,
    )


def build_host_body_port_map_record(
    *,
    host_body_identity: HostBodyIdentityRecord | dict[str, object] | None,
    sense_ports: tuple[HostSensePortRecord, ...] | list[HostSensePortRecord | dict[str, object]] = (),
    internal_space_ports: tuple[HostInternalSpacePortRecord, ...] | list[HostInternalSpacePortRecord | dict[str, object]] = (),
    output_surface_ports: tuple[HostOutputSurfacePortRecord, ...] | list[HostOutputSurfacePortRecord | dict[str, object]] = (),
    trace_history_ports: tuple[HostTraceHistoryPortRecord, ...] | list[HostTraceHistoryPortRecord | dict[str, object]] = (),
    internal_action_ports: tuple[HostInternalActionPortRecord, ...] | list[HostInternalActionPortRecord | dict[str, object]] = (),
    real_hardware_connected: bool = False,
    external_control_connected: bool = False,
    memory_write_connected: bool = False,
    first_output_connected: bool = False,
) -> HostBodyPortMapRecord:
    identity = _identity(host_body_identity) if host_body_identity is not None else None
    sense = tuple(_sense(item) for item in sense_ports)
    spaces = tuple(_internal_space(item) for item in internal_space_ports)
    outputs = tuple(_output(item) for item in output_surface_ports)
    histories = tuple(_trace_history(item) for item in trace_history_ports)
    actions = tuple(_internal_action(item) for item in internal_action_ports)
    if identity is None:
        status = "blocked_missing_identity"
    elif real_hardware_connected:
        status = "blocked_real_hardware_connection_detected"
    elif external_control_connected:
        status = "blocked_external_control_detected"
    elif memory_write_connected:
        status = "blocked_memory_write_detected"
    elif first_output_connected:
        status = "blocked_first_output_detected"
    else:
        status = "host_body_port_map_created"
    return HostBodyPortMapRecord(
        host_body_port_map_id="qingyin_host_body_port_map:v0",
        schema_version=PORT_MAP_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_identity_id=identity.host_body_identity_id if identity else None,
        sense_port_ids=tuple(item.host_sense_port_id for item in sense),
        internal_space_port_ids=tuple(item.host_internal_space_port_id for item in spaces),
        output_surface_port_ids=tuple(item.host_output_surface_port_id for item in outputs),
        trace_history_port_ids=tuple(item.host_trace_history_port_id for item in histories),
        internal_action_port_ids=tuple(item.host_internal_action_port_id for item in actions),
        port_map_status=status,
        port_map_summary=_port_map_summary(status),
        real_hardware_connected=real_hardware_connected,
        external_control_connected=external_control_connected,
        memory_write_connected=memory_write_connected,
        first_output_connected=first_output_connected,
        source_trace_refs=identity.source_trace_refs if identity else tuple(),
    )


def validate_host_body_port_map_record(
    record: HostBodyPortMapRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _port_map(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors = []
    if item.port_map_status == "host_body_port_map_created":
        if not item.source_host_body_identity_id:
            errors.append("missing_identity")
        for flag in (
            "real_hardware_connected",
            "external_control_connected",
            "memory_write_connected",
            "first_output_connected",
        ):
            if getattr(item, flag):
                errors.append(f"{flag}_not_blocked")
    return _validation(not errors, errors, item.host_body_port_map_id, item.port_map_status)


def build_host_body_boundary_audit(
    *,
    host_body_identity: HostBodyIdentityRecord | dict[str, object] | None = None,
    host_body_port_map: HostBodyPortMapRecord | dict[str, object] | None = None,
    camera_port: HostCameraPortRecord | dict[str, object] | None = None,
    mic_port: HostMicPortRecord | dict[str, object] | None = None,
    internal_space_port: HostInternalSpacePortRecord | dict[str, object] | None = None,
    output_surface_port: HostOutputSurfacePortRecord | dict[str, object] | None = None,
    trace_history_port: HostTraceHistoryPortRecord | dict[str, object] | None = None,
    internal_action_port: HostInternalActionPortRecord | dict[str, object] | None = None,
    force_live_runtime_session: bool = False,
    force_autonomous_scheduler: bool = False,
    force_open_ended_loop: bool = False,
    force_thought_engine_behavior: bool = False,
    force_production_behavior: bool = False,
) -> HostBodyBoundaryAudit:
    identity = _identity(host_body_identity) if host_body_identity is not None else None
    port_map = _port_map(host_body_port_map) if host_body_port_map is not None else None
    camera = _camera(camera_port) if camera_port is not None else None
    mic = _mic(mic_port) if mic_port is not None else None
    space = _internal_space(internal_space_port) if internal_space_port is not None else None
    output = _output(output_surface_port) if output_surface_port is not None else None
    trace_history = _trace_history(trace_history_port) if trace_history_port is not None else None
    action = _internal_action(internal_action_port) if internal_action_port is not None else None
    reasons = _boundary_reasons(
        identity=identity,
        port_map=port_map,
        camera=camera,
        mic=mic,
        space=space,
        output=output,
        trace_history=trace_history,
        action=action,
        force_live_runtime_session=force_live_runtime_session,
        force_autonomous_scheduler=force_autonomous_scheduler,
        force_open_ended_loop=force_open_ended_loop,
        force_thought_engine_behavior=force_thought_engine_behavior,
        force_production_behavior=force_production_behavior,
    )
    status = _audit_status(reasons)
    return HostBodyBoundaryAudit(
        host_body_boundary_audit_id=f"host_body_boundary_audit:{_slug(status)}",
        schema_version=BOUNDARY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_identity_id=identity.host_body_identity_id if identity else None,
        source_host_body_port_map_id=port_map.host_body_port_map_id if port_map else None,
        identity_valid=identity is not None and identity.identity_status == "host_body_identity_defined",
        port_map_valid=port_map is not None and port_map.port_map_status == "host_body_port_map_created",
        camera_port_valid=camera is not None and camera.camera_port_status == "camera_port_defined_low_level_only",
        mic_port_valid=mic is not None and mic.mic_port_status == "mic_port_defined_low_level_only",
        internal_space_port_valid=space is not None and space.internal_space_status == "internal_space_port_defined",
        output_surface_port_valid=output is not None and output.output_surface_status == "output_surface_port_defined",
        trace_history_port_valid=trace_history is not None and trace_history.trace_history_status == "trace_history_port_defined",
        internal_action_port_valid=action is not None and action.internal_action_port_status == "internal_action_port_defined",
        computer_bodied_growth_core_confirmed="not_computer_bodied_growth_core" not in reasons,
        not_robot_confirmed="robot_identity_claim" not in reasons,
        not_game_character_confirmed="game_character_identity_claim" not in reasons,
        not_chatbot_confirmed="chatbot_identity_claim" not in reasons,
        unity_home_internal_space_confirmed=space is not None and space.unity_home_is_internal_space,
        avatar_projection_only_confirmed=space is not None and space.avatar_is_projection_only,
        internal_action_only_confirmed=action is not None and action.internal_action_only,
        no_real_camera_connection="real_camera_connection" not in reasons,
        no_real_mic_connection="real_mic_connection" not in reasons,
        no_semantic_vision="semantic_vision" not in reasons,
        no_object_recognition="object_recognition" not in reasons,
        no_face_recognition="face_recognition" not in reasons,
        no_speech_recognition="speech_recognition" not in reasons,
        no_voice_command="voice_command" not in reasons,
        no_external_control="external_control" not in reasons,
        no_os_control="os_control" not in reasons,
        no_mouse_control="mouse_control" not in reasons,
        no_keyboard_control="keyboard_control" not in reasons,
        no_browser_control="browser_control" not in reasons,
        no_file_operation="file_operation" not in reasons,
        no_network_execution="network_execution" not in reasons,
        no_shell_execution="shell_execution" not in reasons,
        no_external_api_call="external_api_call" not in reasons,
        no_memory_layer_write="memory_write" not in reasons,
        no_core_memory_write="core_memory_write" not in reasons,
        no_long_term_memory_write="long_term_memory_write" not in reasons,
        no_archive_memory_write="archive_memory_write" not in reasons,
        no_anchor_write="anchor_write" not in reasons,
        no_automatic_learning_approval="automatic_learning_approval" not in reasons,
        no_first_output="first_output" not in reasons,
        no_live_runtime_session="live_runtime_session" not in reasons,
        no_autonomous_scheduler="autonomous_scheduler" not in reasons,
        no_open_ended_loop="open_ended_loop" not in reasons,
        no_thought_engine_behavior="thought_engine_behavior" not in reasons,
        no_production_behavior="production_behavior" not in reasons,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(reasons),
        source_trace_refs=identity.source_trace_refs if identity else tuple(),
    )


def validate_host_body_boundary_audit(
    record: HostBodyBoundaryAudit | dict[str, object],
) -> dict[str, object]:
    try:
        item = _audit(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors = []
    if item.audit_status == "passed_qingyin_host_body_port_map_boundary":
        required = (
            item.identity_valid,
            item.port_map_valid,
            item.camera_port_valid,
            item.mic_port_valid,
            item.internal_space_port_valid,
            item.output_surface_port_valid,
            item.trace_history_port_valid,
            item.internal_action_port_valid,
            item.computer_bodied_growth_core_confirmed,
            item.no_real_camera_connection,
            item.no_real_mic_connection,
            item.no_semantic_vision,
            item.no_speech_recognition,
            item.no_external_control,
            item.no_memory_layer_write,
            item.no_first_output,
            item.no_live_runtime_session,
            item.no_autonomous_scheduler,
            item.no_open_ended_loop,
            item.no_thought_engine_behavior,
            item.no_production_behavior,
        )
        if not all(required):
            errors.append("passed_audit_has_failed_boundary")
    return _validation(not errors, errors, item.host_body_boundary_audit_id, item.audit_status)


def build_host_body_readiness_record(
    host_body_boundary_audit: HostBodyBoundaryAudit | dict[str, object],
) -> HostBodyReadinessRecord:
    audit = _audit(host_body_boundary_audit)
    passed = audit.audit_status == "passed_qingyin_host_body_port_map_boundary"
    if passed:
        status = "ready_for_read_only_host_sensor_event_shell_only"
    elif audit.source_host_body_port_map_id is None:
        status = "not_ready_missing_host_body_boundary"
    elif audit.audit_status.endswith("detected"):
        status = "blocked_forbidden_authority_detected"
    else:
        status = "not_ready_boundary_failure"
    return HostBodyReadinessRecord(
        host_body_readiness_id=f"host_body_readiness:{audit.host_body_boundary_audit_id}",
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_boundary_audit_id=audit.host_body_boundary_audit_id,
        current_verified_capability=SAFE_CLAIM,
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason=(
            "Create fixture-only HostBodyEvent records for low-level camera, "
            "mic, and host-idle events without real hardware access."
        ),
        ready_for_read_only_sensor_event_shell=passed,
        ready_for_host_body_event_to_runtime_eventframe=passed,
        ready_for_unity_home_internal_space_surface=passed,
        ready_for_internal_action_choice_only=passed,
        ready_for_real_camera_connection=False,
        ready_for_real_mic_connection=False,
        ready_for_speech_recognition=False,
        ready_for_semantic_vision=False,
        ready_for_external_control=False,
        ready_for_first_output=False,
        ready_for_live_runtime_session=False,
        ready_for_memory_layer_write=False,
        ready_for_autonomous_scheduler=False,
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=audit.source_trace_refs,
    )


def validate_host_body_readiness_record(
    record: HostBodyReadinessRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _readiness(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors = []
    for flag in (
        "ready_for_real_camera_connection",
        "ready_for_real_mic_connection",
        "ready_for_speech_recognition",
        "ready_for_semantic_vision",
        "ready_for_external_control",
        "ready_for_first_output",
        "ready_for_live_runtime_session",
        "ready_for_memory_layer_write",
        "ready_for_autonomous_scheduler",
    ):
        if getattr(item, flag):
            errors.append(f"{flag}_true")
    return _validation(not errors, errors, item.host_body_readiness_id, item.readiness_status)


def build_demo_qingyin_host_body_port_map() -> dict[str, object]:
    return _build_host_body_bundle()


def build_demo_blocked_robot_identity_host_body() -> dict[str, object]:
    return _build_host_body_bundle(identity_kwargs={"is_robot": True})


def build_demo_blocked_game_character_identity_host_body() -> dict[str, object]:
    return _build_host_body_bundle(
        identity_kwargs={"is_game_character": True},
        internal_space_kwargs={"unity_avatar_is_body_claimed": True},
    )


def build_demo_blocked_real_camera_connection_host_body() -> dict[str, object]:
    return _build_host_body_bundle(
        camera_kwargs={
            "camera_hardware_connected": True,
            "camera_capture_started": True,
        }
    )


def build_demo_blocked_semantic_vision_host_body() -> dict[str, object]:
    return _build_host_body_bundle(
        camera_kwargs={
            "object_recognition_created": True,
            "semantic_label_created": True,
        }
    )


def build_demo_blocked_speech_recognition_host_body() -> dict[str, object]:
    return _build_host_body_bundle(
        mic_kwargs={
            "speech_recognition_created": True,
            "voice_command_created": True,
        }
    )


def build_demo_blocked_external_control_host_body() -> dict[str, object]:
    return _build_host_body_bundle(
        internal_action_kwargs={
            "mouse_control_created": True,
            "keyboard_control_created": True,
        }
    )


def build_demo_blocked_first_output_host_body() -> dict[str, object]:
    return _build_host_body_bundle(output_kwargs={"first_output_created": True})


def render_host_body_port_map_summary_text(
    audit: HostBodyBoundaryAudit | dict[str, object],
    readiness: HostBodyReadinessRecord | dict[str, object] | None = None,
) -> str:
    audit_record = _audit(audit)
    readiness_record = _readiness(readiness) if readiness is not None else None
    parts = [
        f"host_body_boundary audit={audit_record.audit_status}",
        f"identity_valid={audit_record.identity_valid}",
        f"port_map_valid={audit_record.port_map_valid}",
    ]
    if readiness_record is not None:
        parts.append(f"readiness={readiness_record.readiness_status}")
    return " ".join(parts)


def render_host_body_port_table(
    *,
    sense_ports: tuple[HostSensePortRecord, ...] | list[HostSensePortRecord | dict[str, object]],
    camera_port: HostCameraPortRecord | dict[str, object],
    mic_port: HostMicPortRecord | dict[str, object],
    internal_space_port: HostInternalSpacePortRecord | dict[str, object],
    output_surface_port: HostOutputSurfacePortRecord | dict[str, object],
    trace_history_port: HostTraceHistoryPortRecord | dict[str, object],
    internal_action_port: HostInternalActionPortRecord | dict[str, object],
) -> str:
    sense = tuple(_sense(item) for item in sense_ports)
    camera = _camera(camera_port)
    mic = _mic(mic_port)
    space = _internal_space(internal_space_port)
    output = _output(output_surface_port)
    trace_history = _trace_history(trace_history_port)
    action = _internal_action(internal_action_port)
    rows = ["port | kind | status"]
    for item in sense:
        rows.append(f"{item.sense_port_name} | {item.sense_port_kind} | {item.sense_port_status}")
    rows.extend(
        (
            f"camera | camera_port | {camera.camera_port_status}",
            f"mic | mic_port | {mic.mic_port_status}",
            f"{space.internal_space_name} | internal_space | {space.internal_space_status}",
            f"{output.output_surface_name} | output_surface | {output.output_surface_status}",
            f"{trace_history.trace_history_kind} | trace_history | {trace_history.trace_history_status}",
            f"internal_choice_only | internal_action | {action.internal_action_port_status}",
        )
    )
    return "\n".join(rows)


def _build_host_body_bundle(
    *,
    identity_kwargs: dict[str, object] | None = None,
    camera_kwargs: dict[str, object] | None = None,
    mic_kwargs: dict[str, object] | None = None,
    internal_space_kwargs: dict[str, object] | None = None,
    output_kwargs: dict[str, object] | None = None,
    trace_history_kwargs: dict[str, object] | None = None,
    internal_action_kwargs: dict[str, object] | None = None,
) -> dict[str, object]:
    identity = build_host_body_identity_record(**(identity_kwargs or {}))
    camera_sense = build_host_sense_port_record(sense_port_kind="camera_port")
    mic_sense = build_host_sense_port_record(sense_port_kind="mic_port")
    camera = build_host_camera_port_record(
        source_host_sense_port_id=camera_sense.host_sense_port_id,
        **(camera_kwargs or {}),
    )
    mic = build_host_mic_port_record(
        source_host_sense_port_id=mic_sense.host_sense_port_id,
        **(mic_kwargs or {}),
    )
    internal_space = build_host_internal_space_port_record(
        **(internal_space_kwargs or {})
    )
    output = build_host_output_surface_port_record(**(output_kwargs or {}))
    trace_history = build_host_trace_history_port_record(**(trace_history_kwargs or {}))
    internal_action = build_host_internal_action_port_record(
        **(internal_action_kwargs or {})
    )
    port_map = build_host_body_port_map_record(
        host_body_identity=identity,
        sense_ports=(camera_sense, mic_sense),
        internal_space_ports=(internal_space,),
        output_surface_ports=(output,),
        trace_history_ports=(trace_history,),
        internal_action_ports=(internal_action,),
        real_hardware_connected=(
            camera.camera_hardware_connected
            or camera.camera_capture_started
            or mic.mic_hardware_connected
            or mic.mic_stream_started
        ),
        external_control_connected=(
            internal_action.external_control_created
            or internal_action.os_control_created
            or internal_action.mouse_control_created
            or internal_action.keyboard_control_created
            or internal_action.browser_control_created
        ),
        memory_write_connected=trace_history.memory_layer_write_performed,
        first_output_connected=output.first_output_created,
    )
    audit = build_host_body_boundary_audit(
        host_body_identity=identity,
        host_body_port_map=port_map,
        camera_port=camera,
        mic_port=mic,
        internal_space_port=internal_space,
        output_surface_port=output,
        trace_history_port=trace_history,
        internal_action_port=internal_action,
    )
    readiness = build_host_body_readiness_record(audit)
    return {
        "host_body_identity": identity.to_dict(),
        "host_sense_ports": [camera_sense.to_dict(), mic_sense.to_dict()],
        "host_camera_port": camera.to_dict(),
        "host_mic_port": mic.to_dict(),
        "host_internal_space_port": internal_space.to_dict(),
        "host_output_surface_port": output.to_dict(),
        "host_trace_history_port": trace_history.to_dict(),
        "host_internal_action_port": internal_action.to_dict(),
        "host_body_port_map": port_map.to_dict(),
        "host_body_boundary_audit": audit.to_dict(),
        "host_body_readiness": readiness.to_dict(),
        "rendered_host_body_port_map_summary": render_host_body_port_map_summary_text(
            audit, readiness
        ),
        "rendered_host_body_port_table": render_host_body_port_table(
            sense_ports=(camera_sense, mic_sense),
            camera_port=camera,
            mic_port=mic,
            internal_space_port=internal_space,
            output_surface_port=output,
            trace_history_port=trace_history,
            internal_action_port=internal_action,
        ),
    }


def _boundary_reasons(
    *,
    identity: HostBodyIdentityRecord | None,
    port_map: HostBodyPortMapRecord | None,
    camera: HostCameraPortRecord | None,
    mic: HostMicPortRecord | None,
    space: HostInternalSpacePortRecord | None,
    output: HostOutputSurfacePortRecord | None,
    trace_history: HostTraceHistoryPortRecord | None,
    action: HostInternalActionPortRecord | None,
    force_live_runtime_session: bool,
    force_autonomous_scheduler: bool,
    force_open_ended_loop: bool,
    force_thought_engine_behavior: bool,
    force_production_behavior: bool,
) -> list[str]:
    reasons: list[str] = []
    if identity is None:
        reasons.append("missing_identity")
    else:
        if identity.is_robot:
            reasons.append("robot_identity_claim")
        if identity.is_game_character:
            reasons.append("game_character_identity_claim")
        if identity.is_chatbot:
            reasons.append("chatbot_identity_claim")
        if not identity.is_computer_bodied_growth_core:
            reasons.append("not_computer_bodied_growth_core")
    if port_map is None or port_map.port_map_status == "blocked_missing_identity":
        reasons.append("missing_port_map")
    if port_map is not None:
        if port_map.real_hardware_connected:
            reasons.append("real_sensor_connection")
        if port_map.external_control_connected:
            reasons.append("external_control")
        if port_map.memory_write_connected:
            reasons.append("memory_write")
        if port_map.first_output_connected:
            reasons.append("first_output")
    if camera is not None:
        if camera.camera_hardware_connected or camera.camera_capture_started or camera.image_frame_stored:
            reasons.append("real_camera_connection")
            reasons.append("real_sensor_connection")
        if camera.semantic_label_created or camera.scene_understanding_created:
            reasons.append("semantic_vision")
        if camera.object_recognition_created or camera.person_identification_created:
            reasons.append("object_recognition")
            reasons.append("semantic_vision")
        if camera.face_recognition_created:
            reasons.append("face_recognition")
            reasons.append("semantic_vision")
        if camera.vision_to_action_created:
            reasons.append("semantic_vision")
            reasons.append("external_control")
    if mic is not None:
        if mic.mic_hardware_connected or mic.mic_stream_started or mic.audio_stored:
            reasons.append("real_mic_connection")
            reasons.append("real_sensor_connection")
        if mic.speech_recognition_created or mic.speaker_identification_created or mic.language_understanding_created:
            reasons.append("speech_recognition")
        if mic.voice_command_created:
            reasons.append("voice_command")
            reasons.append("speech_recognition")
        if mic.audio_to_action_created:
            reasons.append("speech_recognition")
            reasons.append("external_control")
    if space is not None:
        if space.unity_avatar_is_body_claimed:
            reasons.append("game_character_identity_claim")
        if space.unity_runtime_connected or space.game_character_control_created:
            reasons.append("external_control")
    if output is not None:
        if output.first_output_created:
            reasons.append("first_output")
        if output.external_message_created or output.file_write_created or output.network_publish_created:
            reasons.append("external_control")
    if trace_history is not None:
        if trace_history.memory_layer_write_performed:
            reasons.append("memory_write")
        if trace_history.core_memory_write_performed:
            reasons.append("core_memory_write")
            reasons.append("memory_write")
        if trace_history.long_term_memory_write_performed:
            reasons.append("long_term_memory_write")
            reasons.append("memory_write")
        if trace_history.archive_memory_write_performed:
            reasons.append("archive_memory_write")
            reasons.append("memory_write")
        if trace_history.anchor_write_performed:
            reasons.append("anchor_write")
            reasons.append("memory_write")
        if trace_history.automatic_memory_admission_created or trace_history.automatic_learning_approval_created:
            reasons.append("automatic_learning_approval")
    if action is not None:
        if action.external_control_created:
            reasons.append("external_control")
        if action.os_control_created:
            reasons.append("os_control")
            reasons.append("external_control")
        if action.mouse_control_created:
            reasons.append("mouse_control")
            reasons.append("external_control")
        if action.keyboard_control_created:
            reasons.append("keyboard_control")
            reasons.append("external_control")
        if action.browser_control_created:
            reasons.append("browser_control")
            reasons.append("external_control")
        if action.file_operation_created:
            reasons.append("file_operation")
            reasons.append("external_control")
        if action.network_execution_created:
            reasons.append("network_execution")
            reasons.append("external_control")
        if action.shell_execution_created:
            reasons.append("shell_execution")
            reasons.append("external_control")
        if action.external_api_call_created:
            reasons.append("external_api_call")
            reasons.append("external_control")
    if force_live_runtime_session:
        reasons.append("live_runtime_session")
    if force_autonomous_scheduler:
        reasons.append("autonomous_scheduler")
    if force_open_ended_loop:
        reasons.append("open_ended_loop")
    if force_thought_engine_behavior:
        reasons.append("thought_engine_behavior")
    if force_production_behavior:
        reasons.append("production_behavior")
    return list(dict.fromkeys(reasons))


def _audit_status(reasons: list[str]) -> str:
    priority = (
        ("robot_identity_claim", "blocked_robot_identity_claim"),
        ("game_character_identity_claim", "blocked_game_character_identity_claim"),
        ("chatbot_identity_claim", "blocked_chatbot_identity_claim"),
        ("real_sensor_connection", "blocked_real_sensor_connection_detected"),
        ("semantic_vision", "blocked_semantic_vision_detected"),
        ("speech_recognition", "blocked_speech_recognition_detected"),
        ("external_control", "blocked_external_control_detected"),
        ("memory_write", "blocked_memory_write_detected"),
        ("first_output", "blocked_first_output_detected"),
        ("live_runtime_session", "blocked_live_runtime_detected"),
        ("autonomous_scheduler", "blocked_forbidden_authority_detected"),
        ("open_ended_loop", "blocked_forbidden_authority_detected"),
        ("thought_engine_behavior", "blocked_forbidden_authority_detected"),
        ("production_behavior", "blocked_forbidden_authority_detected"),
    )
    for reason, status in priority:
        if reason in reasons:
            return status
    return "passed_qingyin_host_body_port_map_boundary"


def _identity_summary(status: str) -> str:
    if status == "host_body_identity_defined":
        return "Qingyin Host Body identity defined as computer-bodied growth core."
    return f"Host body identity blocked: {status}."


def _sense_summary(status: str, kind: str) -> str:
    if status == "sense_port_defined_low_level_only":
        return f"{kind} defined as low-level sense event port only."
    return f"{kind} blocked: {status}."


def _camera_summary(status: str) -> str:
    if status == "camera_port_defined_low_level_only":
        return "Camera port defined for low-level visual event labels only."
    return f"Camera port blocked: {status}."


def _mic_summary(status: str) -> str:
    if status == "mic_port_defined_low_level_only":
        return "Mic port defined for low-level audio event labels only."
    return f"Mic port blocked: {status}."


def _internal_space_summary(status: str) -> str:
    if status == "internal_space_port_defined":
        return "Qingyin Home defined as internal visualization space only."
    return f"Internal space blocked: {status}."


def _output_summary(status: str) -> str:
    if status == "output_surface_port_defined":
        return "Output surface defined as bounded status/trace surface only."
    return f"Output surface blocked: {status}."


def _trace_history_summary(status: str) -> str:
    if status == "trace_history_port_defined":
        return "Trace history defined as event evidence, not memory layer write."
    return f"Trace history blocked: {status}."


def _internal_action_summary(status: str) -> str:
    if status == "internal_action_port_defined":
        return "Internal action port defined for internal choices only."
    return f"Internal action port blocked: {status}."


def _port_map_summary(status: str) -> str:
    if status == "host_body_port_map_created":
        return "Qingyin Host Body bounded port map created."
    return f"Host body port map blocked: {status}."


def _readiness_summary(status: str) -> str:
    if status == "ready_for_read_only_host_sensor_event_shell_only":
        return "Ready only for read-only fixture HostBodyEvent shell."
    return f"Host body readiness blocked: {status}."


def _validation(valid: bool, errors: list[str], record_id: str, status: str) -> dict[str, object]:
    return {
        "valid": valid,
        "error_codes": tuple(errors),
        "record_id": record_id,
        "status": status,
    }


def _identity(value: HostBodyIdentityRecord | dict[str, object]) -> HostBodyIdentityRecord:
    return value if isinstance(value, HostBodyIdentityRecord) else HostBodyIdentityRecord.from_dict(value)


def _sense(value: HostSensePortRecord | dict[str, object]) -> HostSensePortRecord:
    return value if isinstance(value, HostSensePortRecord) else HostSensePortRecord.from_dict(value)


def _camera(value: HostCameraPortRecord | dict[str, object]) -> HostCameraPortRecord:
    return value if isinstance(value, HostCameraPortRecord) else HostCameraPortRecord.from_dict(value)


def _mic(value: HostMicPortRecord | dict[str, object]) -> HostMicPortRecord:
    return value if isinstance(value, HostMicPortRecord) else HostMicPortRecord.from_dict(value)


def _internal_space(value: HostInternalSpacePortRecord | dict[str, object]) -> HostInternalSpacePortRecord:
    return value if isinstance(value, HostInternalSpacePortRecord) else HostInternalSpacePortRecord.from_dict(value)


def _output(value: HostOutputSurfacePortRecord | dict[str, object]) -> HostOutputSurfacePortRecord:
    return value if isinstance(value, HostOutputSurfacePortRecord) else HostOutputSurfacePortRecord.from_dict(value)


def _trace_history(value: HostTraceHistoryPortRecord | dict[str, object]) -> HostTraceHistoryPortRecord:
    return value if isinstance(value, HostTraceHistoryPortRecord) else HostTraceHistoryPortRecord.from_dict(value)


def _internal_action(value: HostInternalActionPortRecord | dict[str, object]) -> HostInternalActionPortRecord:
    return value if isinstance(value, HostInternalActionPortRecord) else HostInternalActionPortRecord.from_dict(value)


def _port_map(value: HostBodyPortMapRecord | dict[str, object]) -> HostBodyPortMapRecord:
    return value if isinstance(value, HostBodyPortMapRecord) else HostBodyPortMapRecord.from_dict(value)


def _audit(value: HostBodyBoundaryAudit | dict[str, object]) -> HostBodyBoundaryAudit:
    return value if isinstance(value, HostBodyBoundaryAudit) else HostBodyBoundaryAudit.from_dict(value)


def _readiness(value: HostBodyReadinessRecord | dict[str, object]) -> HostBodyReadinessRecord:
    return value if isinstance(value, HostBodyReadinessRecord) else HostBodyReadinessRecord.from_dict(value)
