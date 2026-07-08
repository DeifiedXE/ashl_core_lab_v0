"""Read-only Qingyin Host Body fixture sensor event records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.host_body.host_body_port_map import (
    HostBodyPortMapRecord,
    build_demo_qingyin_host_body_port_map,
)


SOURCE_ENGINE = "host_body"

EVENT_SCHEMA_VERSION = "qingyin_host_body_event_v0"
CAMERA_EVENT_SCHEMA_VERSION = "qingyin_host_camera_event_v0"
MIC_EVENT_SCHEMA_VERSION = "qingyin_host_mic_event_v0"
IDLE_EVENT_SCHEMA_VERSION = "qingyin_host_idle_event_v0"
EVENT_SET_SCHEMA_VERSION = "qingyin_host_sensor_event_set_v0"
SUMMARY_SCHEMA_VERSION = "qingyin_host_sensor_event_summary_v0"
AUDIT_SCHEMA_VERSION = "qingyin_host_sensor_event_audit_v0"
READINESS_SCHEMA_VERSION = "qingyin_host_sensor_event_readiness_v0"

CAMERA_EVENT_TYPES = (
    "camera_available",
    "camera_unavailable",
    "camera_frame_available",
    "camera_frame_changed",
    "camera_brightness_changed",
    "camera_motion_proxy_changed",
    "camera_unknown_low_level_event",
)
CAMERA_FORBIDDEN_EVENT_TYPES = (
    "object_detected",
    "face_detected",
    "person_detected",
    "scene_understood",
    "semantic_label_created",
    "camera_action_intent",
    "vision_command",
)
MIC_EVENT_TYPES = (
    "mic_available",
    "mic_unavailable",
    "mic_silence",
    "mic_level_changed",
    "mic_peak_detected",
    "mic_sustained_noise",
    "mic_unknown_low_level_event",
)
MIC_FORBIDDEN_EVENT_TYPES = (
    "speech_recognized",
    "word_recognized",
    "speaker_identified",
    "voice_command_detected",
    "language_understood",
    "audio_action_intent",
)
IDLE_EVENT_TYPES = (
    "host_idle",
    "host_power_on_observed",
    "host_low_activity_tick",
    "host_status_available",
    "host_unknown_status_event",
)
IDLE_FORBIDDEN_EVENT_TYPES = (
    "autonomous_scheduler_tick",
    "open_ended_runtime_tick",
    "background_daemon_tick",
    "live_qingyin_runtime_tick",
)
LOW_LEVEL_BUCKETS = ("low", "medium", "high", "unknown", "none")
SOUND_LEVEL_BUCKETS = ("silent", "low", "medium", "high", "unknown", "none")
HOST_POWER_STATES = ("host_power_on_fixture", "host_power_off_fixture", "unknown")
HOST_ACTIVITY_BUCKETS = ("idle", "low_activity", "active_fixture", "unknown")

SAFE_CLAIM = (
    "ASHL Core v1 can create fixture-only read-only HostBodyEvent records "
    "for low-level camera, microphone, and host-idle events."
)
BLOCKED_CLAIMS = (
    "no_real_camera_access",
    "no_real_microphone_access",
    "no_semantic_vision",
    "no_speech_recognition",
    "no_action_selection_influence",
    "no_external_control",
    "no_memory_layer_write",
    "no_first_output",
    "no_live_runtime_session",
    "no_runtime_eventframe_bridge",
)
READINESS_NEXT_PACKAGE = (
    "Package 103 / ASHL Core v1 Host Body Event Into Runtime EventFrame Bridge Minimal v0"
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
class HostBodyEventRecord:
    host_body_event_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_port_map_id: str
    source_port_id: str | None
    source_port_kind: str
    event_type: str
    event_family: str
    event_kind: str
    fixture_only: bool
    read_only_event: bool
    real_hardware_event: bool
    event_payload: dict[str, Any]
    event_status: str
    event_summary: str
    semantic_label: str | None
    real_camera_accessed: bool
    real_mic_accessed: bool
    camera_capture_started: bool
    mic_stream_started: bool
    image_frame_stored: bool
    audio_stored: bool
    semantic_vision_created: bool
    object_recognition_created: bool
    face_recognition_created: bool
    speech_recognition_created: bool
    speaker_identification_created: bool
    voice_command_created: bool
    language_understanding_created: bool
    action_selection_influence_created: bool
    external_control_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVENT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_event_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.event_family not in {
            "camera_low_level_event",
            "mic_low_level_event",
            "host_idle_event",
            "host_status_event",
            "unknown_host_body_event",
        }:
            raise ValueError(f"unknown event_family: {self.event_family}")
        if self.event_status not in {
            "host_body_event_recorded",
            "host_body_event_recorded_fixture_only",
            "host_body_event_blocked_real_hardware",
            "host_body_event_blocked_semantic_interpretation",
            "host_body_event_blocked_external_control",
            "host_body_event_blocked_memory_write",
            "host_body_event_blocked_first_output",
        }:
            raise ValueError(f"unknown event_status: {self.event_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyEventRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyCameraEventRecord:
    host_camera_event_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_event_id: str
    source_camera_port_id: str
    camera_event_type: str
    camera_event_kind: str
    fixture_frame_id: str | None
    frame_available: bool
    frame_changed: bool
    brightness_changed: bool
    motion_proxy_changed: bool
    brightness_bucket: str | None
    motion_proxy_bucket: str | None
    change_bucket: str | None
    semantic_label: str | None
    camera_event_status: str
    camera_event_summary: str
    real_camera_accessed: bool
    camera_capture_started: bool
    image_frame_stored: bool
    semantic_vision_created: bool
    object_recognition_created: bool
    face_recognition_created: bool
    person_identification_created: bool
    scene_understanding_created: bool
    vision_to_action_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CAMERA_EVENT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_camera_event_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.camera_event_type not in CAMERA_EVENT_TYPES:
            raise ValueError(f"unknown camera_event_type: {self.camera_event_type}")
        if self.camera_event_status not in {
            "camera_event_recorded_fixture_only",
            "camera_event_blocked_real_camera",
            "camera_event_blocked_semantic_vision",
            "camera_event_blocked_object_recognition",
            "camera_event_blocked_vision_to_action",
        }:
            raise ValueError(f"unknown camera_event_status: {self.camera_event_status}")
        for name in ("brightness_bucket", "motion_proxy_bucket", "change_bucket"):
            bucket = getattr(self, name)
            if bucket is not None and bucket not in LOW_LEVEL_BUCKETS:
                raise ValueError(f"unknown {name}: {bucket}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyCameraEventRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyMicEventRecord:
    host_mic_event_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_event_id: str
    source_mic_port_id: str
    mic_event_type: str
    mic_event_kind: str
    fixture_audio_event_id: str | None
    sound_level_bucket: str | None
    peak_detected: bool
    silence_detected: bool
    sustained_noise_detected: bool
    speech_text: str | None
    speaker_id: str | None
    mic_event_status: str
    mic_event_summary: str
    real_mic_accessed: bool
    mic_stream_started: bool
    audio_stored: bool
    speech_recognition_created: bool
    speaker_identification_created: bool
    voice_command_created: bool
    language_understanding_created: bool
    audio_to_action_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MIC_EVENT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_mic_event_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.mic_event_type not in MIC_EVENT_TYPES:
            raise ValueError(f"unknown mic_event_type: {self.mic_event_type}")
        if self.sound_level_bucket is not None and self.sound_level_bucket not in SOUND_LEVEL_BUCKETS:
            raise ValueError(f"unknown sound_level_bucket: {self.sound_level_bucket}")
        if self.mic_event_status not in {
            "mic_event_recorded_fixture_only",
            "mic_event_blocked_real_mic",
            "mic_event_blocked_speech_recognition",
            "mic_event_blocked_voice_command",
            "mic_event_blocked_audio_to_action",
        }:
            raise ValueError(f"unknown mic_event_status: {self.mic_event_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyMicEventRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyIdleEventRecord:
    host_idle_event_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_event_id: str | None
    idle_event_type: str
    idle_event_kind: str
    host_power_state: str
    host_activity_bucket: str
    idle_event_status: str
    idle_event_summary: str
    runtime_tick_created: bool
    live_runtime_session_created: bool
    autonomous_scheduler_created: bool
    open_ended_loop_created: bool
    background_daemon_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != IDLE_EVENT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_idle_event_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.idle_event_type not in IDLE_EVENT_TYPES:
            raise ValueError(f"unknown idle_event_type: {self.idle_event_type}")
        if self.host_power_state not in HOST_POWER_STATES:
            raise ValueError(f"unknown host_power_state: {self.host_power_state}")
        if self.host_activity_bucket not in HOST_ACTIVITY_BUCKETS:
            raise ValueError(f"unknown host_activity_bucket: {self.host_activity_bucket}")
        if self.idle_event_status not in {
            "host_idle_event_recorded_fixture_only",
            "host_idle_event_blocked_live_runtime_tick",
            "host_idle_event_blocked_autonomous_scheduler",
            "host_idle_event_blocked_open_ended_loop",
        }:
            raise ValueError(f"unknown idle_event_status: {self.idle_event_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyIdleEventRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodySensorEventSetRecord:
    host_sensor_event_set_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_port_map_id: str
    host_body_event_ids: tuple[str, ...]
    camera_event_ids: tuple[str, ...]
    mic_event_ids: tuple[str, ...]
    idle_event_ids: tuple[str, ...]
    event_set_kind: str
    event_set_status: str
    event_set_summary: str
    fixture_only: bool
    read_only: bool
    camera_event_count: int
    mic_event_count: int
    idle_event_count: int
    total_event_count: int
    real_hardware_accessed: bool
    semantic_interpretation_created: bool
    external_control_created: bool
    memory_layer_write_performed: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVENT_SET_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_sensor_event_set_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.event_set_kind not in {
            "single_camera_event_demo",
            "single_mic_event_demo",
            "single_idle_event_demo",
            "mixed_host_sensor_event_demo",
            "blocked_event_demo",
        }:
            raise ValueError(f"unknown event_set_kind: {self.event_set_kind}")
        if self.event_set_status not in {
            "host_sensor_event_set_recorded",
            "host_sensor_event_set_recorded_fixture_only",
            "host_sensor_event_set_blocked_real_hardware",
            "host_sensor_event_set_blocked_semantic_interpretation",
            "host_sensor_event_set_blocked_external_control",
            "host_sensor_event_set_blocked_memory_write",
            "host_sensor_event_set_blocked_first_output",
        }:
            raise ValueError(f"unknown event_set_status: {self.event_set_status}")
        for name in (
            "host_body_event_ids",
            "camera_event_ids",
            "mic_event_ids",
            "idle_event_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodySensorEventSetRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodySensorEventSummaryRecord:
    host_sensor_event_summary_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_sensor_event_set_id: str
    summary_kind: str
    camera_summary: str
    mic_summary: str
    idle_summary: str
    overall_summary: str
    low_level_event_count: int
    blocked_event_count: int
    semantic_interpretation_created: bool
    action_selection_influence_created: bool
    memory_layer_write_performed: bool
    first_output_created: bool
    external_control_created: bool
    summary_status: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SUMMARY_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_sensor_event_summary_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.summary_kind not in {
            "fixture_sensor_event_summary",
            "blocked_sensor_event_summary",
            "mixed_sensor_event_summary",
        }:
            raise ValueError(f"unknown summary_kind: {self.summary_kind}")
        if self.summary_status not in {
            "host_sensor_event_summary_recorded",
            "host_sensor_event_summary_blocked_forbidden_authority",
        }:
            raise ValueError(f"unknown summary_status: {self.summary_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodySensorEventSummaryRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodySensorEventAudit:
    host_sensor_event_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_sensor_event_set_id: str | None
    source_host_sensor_event_summary_id: str | None
    host_body_port_map_valid: bool
    camera_events_valid: bool
    mic_events_valid: bool
    idle_events_valid: bool
    event_set_valid: bool
    summary_valid: bool
    fixture_only_confirmed: bool
    read_only_confirmed: bool
    no_real_camera_access: bool
    no_real_mic_access: bool
    no_camera_capture: bool
    no_mic_stream: bool
    no_image_storage: bool
    no_audio_storage: bool
    no_semantic_vision: bool
    no_object_recognition: bool
    no_face_recognition: bool
    no_speech_recognition: bool
    no_speaker_identification: bool
    no_voice_command: bool
    no_language_understanding: bool
    no_action_selection_influence: bool
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
    no_runtime_eventframe_bridge: bool
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
        if self.schema_version != AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_sensor_event_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.audit_status not in {
            "passed_host_body_read_only_sensor_event_shell",
            "passed_camera_fixture_event_only",
            "passed_mic_fixture_event_only",
            "passed_idle_fixture_event_only",
            "blocked_real_camera_access_detected",
            "blocked_real_mic_access_detected",
            "blocked_semantic_vision_detected",
            "blocked_speech_recognition_detected",
            "blocked_action_selection_influence_detected",
            "blocked_external_control_detected",
            "blocked_memory_write_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
            "blocked_runtime_eventframe_bridge_detected",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodySensorEventAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodySensorEventReadinessRecord:
    host_sensor_event_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_sensor_event_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_host_body_event_to_runtime_eventframe: bool
    ready_for_runtime_eventframe_fixture_bridge: bool
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
            raise ValueError("schema_version must be qingyin_host_sensor_event_readiness_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.readiness_status not in {
            "ready_for_host_body_event_runtime_eventframe_bridge_only",
            "ready_for_unity_home_internal_space_surface_only",
            "not_ready_missing_sensor_event_audit",
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
    def from_dict(cls, data: dict[str, object]) -> "HostBodySensorEventReadinessRecord":
        return cls(**dict(data))


def build_host_body_event_record(
    *,
    source_host_body_port_map_id: str,
    source_port_id: str | None,
    source_port_kind: str,
    event_type: str,
    event_payload: dict[str, Any] | None = None,
    semantic_label: str | None = None,
    real_hardware_event: bool = False,
    real_camera_accessed: bool = False,
    real_mic_accessed: bool = False,
    camera_capture_started: bool = False,
    mic_stream_started: bool = False,
    image_frame_stored: bool = False,
    audio_stored: bool = False,
    semantic_vision_created: bool = False,
    object_recognition_created: bool = False,
    face_recognition_created: bool = False,
    speech_recognition_created: bool = False,
    speaker_identification_created: bool = False,
    voice_command_created: bool = False,
    language_understanding_created: bool = False,
    action_selection_influence_created: bool = False,
    external_control_created: bool = False,
    memory_layer_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
    source_trace_refs: tuple[str, ...] = tuple(),
) -> HostBodyEventRecord:
    event_family = classify_host_body_event_type(event_type)
    status = _event_status(
        semantic_label_requested=semantic_label is not None,
        real_hardware_event=real_hardware_event,
        real_camera_accessed=real_camera_accessed,
        real_mic_accessed=real_mic_accessed,
        camera_capture_started=camera_capture_started,
        mic_stream_started=mic_stream_started,
        image_frame_stored=image_frame_stored,
        audio_stored=audio_stored,
        semantic_vision_created=semantic_vision_created,
        object_recognition_created=object_recognition_created,
        face_recognition_created=face_recognition_created,
        speech_recognition_created=speech_recognition_created,
        speaker_identification_created=speaker_identification_created,
        voice_command_created=voice_command_created,
        language_understanding_created=language_understanding_created,
        action_selection_influence_created=action_selection_influence_created,
        external_control_created=external_control_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    return HostBodyEventRecord(
        host_body_event_id=f"host_body_event:{_slug(event_type)}:{_slug(status)}",
        schema_version=EVENT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_port_map_id=source_host_body_port_map_id,
        source_port_id=source_port_id,
        source_port_kind=source_port_kind,
        event_type=event_type,
        event_family=event_family,
        event_kind="fixture_low_level_sensor_event",
        fixture_only=True,
        read_only_event=True,
        real_hardware_event=real_hardware_event,
        event_payload=event_payload or {},
        event_status=status,
        event_summary=_event_summary(status, event_type),
        semantic_label=None,
        real_camera_accessed=real_camera_accessed,
        real_mic_accessed=real_mic_accessed,
        camera_capture_started=camera_capture_started,
        mic_stream_started=mic_stream_started,
        image_frame_stored=image_frame_stored,
        audio_stored=audio_stored,
        semantic_vision_created=semantic_vision_created,
        object_recognition_created=object_recognition_created,
        face_recognition_created=face_recognition_created,
        speech_recognition_created=speech_recognition_created,
        speaker_identification_created=speaker_identification_created,
        voice_command_created=voice_command_created,
        language_understanding_created=language_understanding_created,
        action_selection_influence_created=action_selection_influence_created,
        external_control_created=external_control_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=source_trace_refs,
    )


def validate_host_body_event_record(
    record: HostBodyEventRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _event(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if not item.fixture_only:
        errors.append("fixture_only_false")
    if not item.read_only_event:
        errors.append("read_only_event_false")
    if item.semantic_label is not None:
        errors.append("semantic_label_present")
    if item.event_status == "host_body_event_recorded_fixture_only":
        if _host_body_event_has_forbidden_boundary(item):
            errors.append("recorded_event_has_forbidden_boundary")
    return _validation(not errors, errors, item.host_body_event_id, item.event_status)


def build_host_body_camera_event_record(
    *,
    host_body_event: HostBodyEventRecord | dict[str, object],
    source_camera_port_id: str,
    camera_event_type: str,
    fixture_frame_id: str | None = None,
    brightness_bucket: str | None = None,
    motion_proxy_bucket: str | None = None,
    change_bucket: str | None = None,
    semantic_label: str | None = None,
    real_camera_accessed: bool = False,
    camera_capture_started: bool = False,
    image_frame_stored: bool = False,
    semantic_vision_created: bool = False,
    object_recognition_created: bool = False,
    face_recognition_created: bool = False,
    person_identification_created: bool = False,
    scene_understanding_created: bool = False,
    vision_to_action_created: bool = False,
    source_trace_refs: tuple[str, ...] = tuple(),
) -> HostBodyCameraEventRecord:
    event = _event(host_body_event)
    status = _camera_event_status(
        semantic_label_requested=semantic_label is not None,
        real_camera_accessed=real_camera_accessed,
        camera_capture_started=camera_capture_started,
        image_frame_stored=image_frame_stored,
        semantic_vision_created=semantic_vision_created,
        object_recognition_created=object_recognition_created,
        face_recognition_created=face_recognition_created,
        person_identification_created=person_identification_created,
        scene_understanding_created=scene_understanding_created,
        vision_to_action_created=vision_to_action_created,
    )
    return HostBodyCameraEventRecord(
        host_camera_event_id=f"host_camera_event:{_slug(camera_event_type)}:{_slug(status)}",
        schema_version=CAMERA_EVENT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_event_id=event.host_body_event_id,
        source_camera_port_id=source_camera_port_id,
        camera_event_type=camera_event_type,
        camera_event_kind="fixture_low_level_camera_event",
        fixture_frame_id=fixture_frame_id,
        frame_available=camera_event_type == "camera_frame_available",
        frame_changed=camera_event_type == "camera_frame_changed",
        brightness_changed=camera_event_type == "camera_brightness_changed",
        motion_proxy_changed=camera_event_type == "camera_motion_proxy_changed",
        brightness_bucket=brightness_bucket,
        motion_proxy_bucket=motion_proxy_bucket,
        change_bucket=change_bucket,
        semantic_label=None,
        camera_event_status=status,
        camera_event_summary=_camera_event_summary(status, camera_event_type),
        real_camera_accessed=real_camera_accessed,
        camera_capture_started=camera_capture_started,
        image_frame_stored=image_frame_stored,
        semantic_vision_created=semantic_vision_created,
        object_recognition_created=object_recognition_created,
        face_recognition_created=face_recognition_created,
        person_identification_created=person_identification_created,
        scene_understanding_created=scene_understanding_created,
        vision_to_action_created=vision_to_action_created,
        source_trace_refs=source_trace_refs or event.source_trace_refs,
    )


def validate_host_body_camera_event_record(
    record: HostBodyCameraEventRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _camera_event(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.semantic_label is not None:
        errors.append("semantic_label_present")
    if item.camera_event_status == "camera_event_recorded_fixture_only":
        if (
            item.real_camera_accessed
            or item.camera_capture_started
            or item.image_frame_stored
            or item.semantic_vision_created
            or item.object_recognition_created
            or item.face_recognition_created
            or item.person_identification_created
            or item.scene_understanding_created
            or item.vision_to_action_created
        ):
            errors.append("recorded_camera_event_has_forbidden_boundary")
    return _validation(not errors, errors, item.host_camera_event_id, item.camera_event_status)


def build_host_body_mic_event_record(
    *,
    host_body_event: HostBodyEventRecord | dict[str, object],
    source_mic_port_id: str,
    mic_event_type: str,
    fixture_audio_event_id: str | None = None,
    sound_level_bucket: str | None = None,
    peak_detected: bool = False,
    silence_detected: bool = False,
    sustained_noise_detected: bool = False,
    speech_text: str | None = None,
    speaker_id: str | None = None,
    real_mic_accessed: bool = False,
    mic_stream_started: bool = False,
    audio_stored: bool = False,
    speech_recognition_created: bool = False,
    speaker_identification_created: bool = False,
    voice_command_created: bool = False,
    language_understanding_created: bool = False,
    audio_to_action_created: bool = False,
    source_trace_refs: tuple[str, ...] = tuple(),
) -> HostBodyMicEventRecord:
    event = _event(host_body_event)
    status = _mic_event_status(
        speech_text_requested=speech_text is not None,
        speaker_id_requested=speaker_id is not None,
        real_mic_accessed=real_mic_accessed,
        mic_stream_started=mic_stream_started,
        audio_stored=audio_stored,
        speech_recognition_created=speech_recognition_created,
        speaker_identification_created=speaker_identification_created,
        voice_command_created=voice_command_created,
        language_understanding_created=language_understanding_created,
        audio_to_action_created=audio_to_action_created,
    )
    return HostBodyMicEventRecord(
        host_mic_event_id=f"host_mic_event:{_slug(mic_event_type)}:{_slug(status)}",
        schema_version=MIC_EVENT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_event_id=event.host_body_event_id,
        source_mic_port_id=source_mic_port_id,
        mic_event_type=mic_event_type,
        mic_event_kind="fixture_low_level_mic_event",
        fixture_audio_event_id=fixture_audio_event_id,
        sound_level_bucket=sound_level_bucket,
        peak_detected=peak_detected or mic_event_type == "mic_peak_detected",
        silence_detected=silence_detected or mic_event_type == "mic_silence",
        sustained_noise_detected=sustained_noise_detected or mic_event_type == "mic_sustained_noise",
        speech_text=None,
        speaker_id=None,
        mic_event_status=status,
        mic_event_summary=_mic_event_summary(status, mic_event_type),
        real_mic_accessed=real_mic_accessed,
        mic_stream_started=mic_stream_started,
        audio_stored=audio_stored,
        speech_recognition_created=speech_recognition_created,
        speaker_identification_created=speaker_identification_created,
        voice_command_created=voice_command_created,
        language_understanding_created=language_understanding_created,
        audio_to_action_created=audio_to_action_created,
        source_trace_refs=source_trace_refs or event.source_trace_refs,
    )


def validate_host_body_mic_event_record(
    record: HostBodyMicEventRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _mic_event(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.speech_text is not None:
        errors.append("speech_text_present")
    if item.speaker_id is not None:
        errors.append("speaker_id_present")
    if item.mic_event_status == "mic_event_recorded_fixture_only":
        if (
            item.real_mic_accessed
            or item.mic_stream_started
            or item.audio_stored
            or item.speech_recognition_created
            or item.speaker_identification_created
            or item.voice_command_created
            or item.language_understanding_created
            or item.audio_to_action_created
        ):
            errors.append("recorded_mic_event_has_forbidden_boundary")
    return _validation(not errors, errors, item.host_mic_event_id, item.mic_event_status)


def build_host_body_idle_event_record(
    *,
    host_body_event: HostBodyEventRecord | dict[str, object] | None = None,
    idle_event_type: str,
    host_power_state: str = "host_power_on_fixture",
    host_activity_bucket: str = "idle",
    runtime_tick_created: bool = False,
    live_runtime_session_created: bool = False,
    autonomous_scheduler_created: bool = False,
    open_ended_loop_created: bool = False,
    background_daemon_created: bool = False,
    memory_layer_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    production_behavior_created: bool = False,
    source_trace_refs: tuple[str, ...] = tuple(),
) -> HostBodyIdleEventRecord:
    event = _event(host_body_event) if host_body_event is not None else None
    status = _idle_event_status(
        runtime_tick_created=runtime_tick_created,
        live_runtime_session_created=live_runtime_session_created,
        autonomous_scheduler_created=autonomous_scheduler_created,
        open_ended_loop_created=open_ended_loop_created,
        background_daemon_created=background_daemon_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        production_behavior_created=production_behavior_created,
    )
    return HostBodyIdleEventRecord(
        host_idle_event_id=f"host_idle_event:{_slug(idle_event_type)}:{_slug(status)}",
        schema_version=IDLE_EVENT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_event_id=event.host_body_event_id if event else None,
        idle_event_type=idle_event_type,
        idle_event_kind="fixture_host_idle_event",
        host_power_state=host_power_state,
        host_activity_bucket=host_activity_bucket,
        idle_event_status=status,
        idle_event_summary=_idle_event_summary(status, idle_event_type),
        runtime_tick_created=runtime_tick_created,
        live_runtime_session_created=live_runtime_session_created,
        autonomous_scheduler_created=autonomous_scheduler_created,
        open_ended_loop_created=open_ended_loop_created,
        background_daemon_created=background_daemon_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        production_behavior_created=production_behavior_created,
        source_trace_refs=source_trace_refs or (event.source_trace_refs if event else tuple()),
    )


def validate_host_body_idle_event_record(
    record: HostBodyIdleEventRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _idle_event(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.idle_event_status == "host_idle_event_recorded_fixture_only":
        if (
            item.runtime_tick_created
            or item.live_runtime_session_created
            or item.autonomous_scheduler_created
            or item.open_ended_loop_created
            or item.background_daemon_created
            or item.memory_layer_write_performed
            or item.automatic_learning_approval_created
            or item.production_behavior_created
        ):
            errors.append("recorded_idle_event_has_forbidden_boundary")
    return _validation(not errors, errors, item.host_idle_event_id, item.idle_event_status)


def build_host_body_sensor_event_set_record(
    *,
    source_host_body_port_map_id: str,
    host_body_events: tuple[HostBodyEventRecord | dict[str, object], ...] | list[HostBodyEventRecord | dict[str, object]],
    camera_events: tuple[HostBodyCameraEventRecord | dict[str, object], ...] | list[HostBodyCameraEventRecord | dict[str, object]] = tuple(),
    mic_events: tuple[HostBodyMicEventRecord | dict[str, object], ...] | list[HostBodyMicEventRecord | dict[str, object]] = tuple(),
    idle_events: tuple[HostBodyIdleEventRecord | dict[str, object], ...] | list[HostBodyIdleEventRecord | dict[str, object]] = tuple(),
    event_set_kind: str | None = None,
    runtime_eventframe_bridge_created: bool = False,
    source_trace_refs: tuple[str, ...] = tuple(),
) -> HostBodySensorEventSetRecord:
    host_items = tuple(_event(item) for item in host_body_events)
    camera_items = tuple(_camera_event(item) for item in camera_events)
    mic_items = tuple(_mic_event(item) for item in mic_events)
    idle_items = tuple(_idle_event(item) for item in idle_events)
    if event_set_kind is None:
        event_set_kind = _event_set_kind(camera_items, mic_items, idle_items)
    status = _event_set_status(
        host_items=host_items,
        camera_items=camera_items,
        mic_items=mic_items,
        idle_items=idle_items,
        runtime_eventframe_bridge_created=runtime_eventframe_bridge_created,
    )
    return HostBodySensorEventSetRecord(
        host_sensor_event_set_id=f"host_sensor_event_set:{_slug(event_set_kind)}:{_slug(status)}",
        schema_version=EVENT_SET_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_port_map_id=source_host_body_port_map_id,
        host_body_event_ids=tuple(item.host_body_event_id for item in host_items),
        camera_event_ids=tuple(item.host_camera_event_id for item in camera_items),
        mic_event_ids=tuple(item.host_mic_event_id for item in mic_items),
        idle_event_ids=tuple(item.host_idle_event_id for item in idle_items),
        event_set_kind=event_set_kind,
        event_set_status=status,
        event_set_summary=_event_set_summary(status),
        fixture_only=True,
        read_only=True,
        camera_event_count=len(camera_items),
        mic_event_count=len(mic_items),
        idle_event_count=len(idle_items),
        total_event_count=len(host_items),
        real_hardware_accessed=_event_set_has_real_hardware(host_items, camera_items, mic_items),
        semantic_interpretation_created=_event_set_has_semantic(host_items, camera_items, mic_items),
        external_control_created=_event_set_has_external_control(host_items),
        memory_layer_write_performed=_event_set_has_memory_write(host_items, idle_items),
        first_output_created=_event_set_has_first_output(host_items),
        live_runtime_session_created=_event_set_has_live_runtime(host_items, idle_items),
        source_trace_refs=source_trace_refs or _first_trace_refs(host_items),
    )


def validate_host_body_sensor_event_set_record(
    record: HostBodySensorEventSetRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _event_set(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if not item.fixture_only:
        errors.append("fixture_only_false")
    if not item.read_only:
        errors.append("read_only_false")
    if item.total_event_count != (
        item.camera_event_count + item.mic_event_count + item.idle_event_count
    ):
        errors.append("total_event_count_mismatch")
    if item.event_set_status == "host_sensor_event_set_recorded_fixture_only":
        if (
            item.real_hardware_accessed
            or item.semantic_interpretation_created
            or item.external_control_created
            or item.memory_layer_write_performed
            or item.first_output_created
            or item.live_runtime_session_created
        ):
            errors.append("recorded_event_set_has_forbidden_boundary")
    return _validation(not errors, errors, item.host_sensor_event_set_id, item.event_set_status)


def build_host_body_sensor_event_summary_record(
    *,
    host_sensor_event_set: HostBodySensorEventSetRecord | dict[str, object],
    blocked_event_count: int | None = None,
    semantic_interpretation_created: bool = False,
    action_selection_influence_created: bool = False,
    memory_layer_write_performed: bool = False,
    first_output_created: bool = False,
    external_control_created: bool = False,
) -> HostBodySensorEventSummaryRecord:
    event_set = _event_set(host_sensor_event_set)
    blocked_count = blocked_event_count
    if blocked_count is None:
        blocked_count = 0 if event_set.event_set_status == "host_sensor_event_set_recorded_fixture_only" else event_set.total_event_count
    status = (
        "host_sensor_event_summary_blocked_forbidden_authority"
        if (
            semantic_interpretation_created
            or action_selection_influence_created
            or memory_layer_write_performed
            or first_output_created
            or external_control_created
            or event_set.event_set_status != "host_sensor_event_set_recorded_fixture_only"
        )
        else "host_sensor_event_summary_recorded"
    )
    summary_kind = (
        "blocked_sensor_event_summary"
        if status == "host_sensor_event_summary_blocked_forbidden_authority"
        else (
            "mixed_sensor_event_summary"
            if event_set.event_set_kind == "mixed_host_sensor_event_demo"
            else "fixture_sensor_event_summary"
        )
    )
    return HostBodySensorEventSummaryRecord(
        host_sensor_event_summary_id=f"host_sensor_event_summary:{event_set.host_sensor_event_set_id}",
        schema_version=SUMMARY_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_sensor_event_set_id=event_set.host_sensor_event_set_id,
        summary_kind=summary_kind,
        camera_summary=f"camera_events={event_set.camera_event_count}",
        mic_summary=f"mic_events={event_set.mic_event_count}",
        idle_summary=f"idle_events={event_set.idle_event_count}",
        overall_summary=_summary_text(event_set, status),
        low_level_event_count=event_set.total_event_count,
        blocked_event_count=blocked_count,
        semantic_interpretation_created=semantic_interpretation_created
        or event_set.semantic_interpretation_created,
        action_selection_influence_created=action_selection_influence_created,
        memory_layer_write_performed=memory_layer_write_performed
        or event_set.memory_layer_write_performed,
        first_output_created=first_output_created or event_set.first_output_created,
        external_control_created=external_control_created
        or event_set.external_control_created,
        summary_status=status,
        source_trace_refs=event_set.source_trace_refs,
    )


def validate_host_body_sensor_event_summary_record(
    record: HostBodySensorEventSummaryRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _summary(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.summary_status == "host_sensor_event_summary_recorded":
        if (
            item.semantic_interpretation_created
            or item.action_selection_influence_created
            or item.memory_layer_write_performed
            or item.first_output_created
            or item.external_control_created
        ):
            errors.append("recorded_summary_has_forbidden_boundary")
    return _validation(not errors, errors, item.host_sensor_event_summary_id, item.summary_status)


def build_host_body_sensor_event_audit(
    *,
    host_sensor_event_set: HostBodySensorEventSetRecord | dict[str, object] | None,
    host_sensor_event_summary: HostBodySensorEventSummaryRecord | dict[str, object] | None,
    host_body_port_map: HostBodyPortMapRecord | dict[str, object] | None = None,
    host_body_events: tuple[HostBodyEventRecord | dict[str, object], ...] | list[HostBodyEventRecord | dict[str, object]] = tuple(),
    camera_events: tuple[HostBodyCameraEventRecord | dict[str, object], ...] | list[HostBodyCameraEventRecord | dict[str, object]] = tuple(),
    mic_events: tuple[HostBodyMicEventRecord | dict[str, object], ...] | list[HostBodyMicEventRecord | dict[str, object]] = tuple(),
    idle_events: tuple[HostBodyIdleEventRecord | dict[str, object], ...] | list[HostBodyIdleEventRecord | dict[str, object]] = tuple(),
    runtime_eventframe_bridge_created: bool = False,
    force_autonomous_scheduler: bool = False,
    force_open_ended_loop: bool = False,
    force_thought_engine_behavior: bool = False,
    force_production_behavior: bool = False,
) -> HostBodySensorEventAudit:
    event_set = _event_set(host_sensor_event_set) if host_sensor_event_set is not None else None
    summary = _summary(host_sensor_event_summary) if host_sensor_event_summary is not None else None
    port_map = _port_map(host_body_port_map) if host_body_port_map is not None else None
    host_items = tuple(_event(item) for item in host_body_events)
    camera_items = tuple(_camera_event(item) for item in camera_events)
    mic_items = tuple(_mic_event(item) for item in mic_events)
    idle_items = tuple(_idle_event(item) for item in idle_events)
    reasons = _audit_reasons(
        port_map=port_map,
        event_set=event_set,
        summary=summary,
        host_items=host_items,
        camera_items=camera_items,
        mic_items=mic_items,
        idle_items=idle_items,
        runtime_eventframe_bridge_created=runtime_eventframe_bridge_created,
        force_autonomous_scheduler=force_autonomous_scheduler,
        force_open_ended_loop=force_open_ended_loop,
        force_thought_engine_behavior=force_thought_engine_behavior,
        force_production_behavior=force_production_behavior,
    )
    status = _audit_status(reasons, event_set)
    return HostBodySensorEventAudit(
        host_sensor_event_audit_id=f"host_sensor_event_audit:{_slug(status)}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_sensor_event_set_id=event_set.host_sensor_event_set_id if event_set else None,
        source_host_sensor_event_summary_id=summary.host_sensor_event_summary_id if summary else None,
        host_body_port_map_valid=port_map is not None and port_map.port_map_status == "host_body_port_map_created",
        camera_events_valid=all(item.camera_event_status == "camera_event_recorded_fixture_only" for item in camera_items),
        mic_events_valid=all(item.mic_event_status == "mic_event_recorded_fixture_only" for item in mic_items),
        idle_events_valid=all(item.idle_event_status == "host_idle_event_recorded_fixture_only" for item in idle_items),
        event_set_valid=event_set is not None and event_set.event_set_status == "host_sensor_event_set_recorded_fixture_only",
        summary_valid=summary is not None and summary.summary_status == "host_sensor_event_summary_recorded",
        fixture_only_confirmed="not_fixture_only" not in reasons,
        read_only_confirmed="not_read_only" not in reasons,
        no_real_camera_access="real_camera_access" not in reasons,
        no_real_mic_access="real_mic_access" not in reasons,
        no_camera_capture="camera_capture" not in reasons,
        no_mic_stream="mic_stream" not in reasons,
        no_image_storage="image_storage" not in reasons,
        no_audio_storage="audio_storage" not in reasons,
        no_semantic_vision="semantic_vision" not in reasons,
        no_object_recognition="object_recognition" not in reasons,
        no_face_recognition="face_recognition" not in reasons,
        no_speech_recognition="speech_recognition" not in reasons,
        no_speaker_identification="speaker_identification" not in reasons,
        no_voice_command="voice_command" not in reasons,
        no_language_understanding="language_understanding" not in reasons,
        no_action_selection_influence="action_selection_influence" not in reasons,
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
        no_runtime_eventframe_bridge="runtime_eventframe_bridge" not in reasons,
        no_autonomous_scheduler="autonomous_scheduler" not in reasons,
        no_open_ended_loop="open_ended_loop" not in reasons,
        no_thought_engine_behavior="thought_engine_behavior" not in reasons,
        no_production_behavior="production_behavior" not in reasons,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(reasons),
        source_trace_refs=event_set.source_trace_refs if event_set else tuple(),
    )


def validate_host_body_sensor_event_audit(
    record: HostBodySensorEventAudit | dict[str, object],
) -> dict[str, object]:
    try:
        item = _audit(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.audit_status.startswith("passed_"):
        required = (
            item.host_body_port_map_valid,
            item.event_set_valid,
            item.summary_valid,
            item.fixture_only_confirmed,
            item.read_only_confirmed,
            item.no_real_camera_access,
            item.no_real_mic_access,
            item.no_camera_capture,
            item.no_mic_stream,
            item.no_image_storage,
            item.no_audio_storage,
            item.no_semantic_vision,
            item.no_speech_recognition,
            item.no_action_selection_influence,
            item.no_external_control,
            item.no_memory_layer_write,
            item.no_first_output,
            item.no_live_runtime_session,
            item.no_runtime_eventframe_bridge,
            item.no_autonomous_scheduler,
            item.no_open_ended_loop,
            item.no_thought_engine_behavior,
            item.no_production_behavior,
        )
        if not all(required):
            errors.append("passed_audit_has_failed_boundary")
    return _validation(not errors, errors, item.host_sensor_event_audit_id, item.audit_status)


def build_host_body_sensor_event_readiness(
    host_sensor_event_audit: HostBodySensorEventAudit | dict[str, object],
) -> HostBodySensorEventReadinessRecord:
    audit = _audit(host_sensor_event_audit)
    passed = audit.audit_status.startswith("passed_")
    if passed:
        status = "ready_for_host_body_event_runtime_eventframe_bridge_only"
    elif audit.source_host_sensor_event_set_id is None:
        status = "not_ready_missing_sensor_event_audit"
    elif audit.audit_status.endswith("detected"):
        status = "blocked_forbidden_authority_detected"
    else:
        status = "not_ready_boundary_failure"
    return HostBodySensorEventReadinessRecord(
        host_sensor_event_readiness_id=f"host_sensor_event_readiness:{audit.host_sensor_event_audit_id}",
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_sensor_event_audit_id=audit.host_sensor_event_audit_id,
        current_verified_capability=SAFE_CLAIM,
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason=(
            "Map fixture-only HostBodyEvent records into bounded Runtime "
            "EventFrames without real sensors or live runtime."
        ),
        ready_for_host_body_event_to_runtime_eventframe=passed,
        ready_for_runtime_eventframe_fixture_bridge=passed,
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


def validate_host_body_sensor_event_readiness(
    record: HostBodySensorEventReadinessRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _readiness(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
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
    return _validation(not errors, errors, item.host_sensor_event_readiness_id, item.readiness_status)


def build_demo_camera_frame_available_event() -> dict[str, object]:
    return _build_sensor_event_bundle(camera_specs=(("camera_frame_available", {}),))


def build_demo_camera_frame_changed_event() -> dict[str, object]:
    return _build_sensor_event_bundle(
        camera_specs=(("camera_frame_changed", {"change_bucket": "medium"}),)
    )


def build_demo_mic_level_changed_event() -> dict[str, object]:
    return _build_sensor_event_bundle(
        mic_specs=(("mic_level_changed", {"sound_level_bucket": "medium"}),)
    )


def build_demo_mic_peak_detected_event() -> dict[str, object]:
    return _build_sensor_event_bundle(
        mic_specs=(("mic_peak_detected", {"sound_level_bucket": "high", "peak_detected": True}),)
    )


def build_demo_host_idle_event() -> dict[str, object]:
    return _build_sensor_event_bundle(idle_specs=(("host_idle", {}),))


def build_demo_mixed_host_sensor_event_set() -> dict[str, object]:
    return _build_sensor_event_bundle(
        camera_specs=(
            ("camera_frame_available", {}),
            ("camera_frame_changed", {"change_bucket": "medium"}),
        ),
        mic_specs=(
            ("mic_level_changed", {"sound_level_bucket": "medium"}),
            ("mic_peak_detected", {"sound_level_bucket": "high", "peak_detected": True}),
        ),
        idle_specs=(("host_idle", {}),),
    )


def build_demo_blocked_real_camera_event() -> dict[str, object]:
    return _build_sensor_event_bundle(
        camera_specs=(
            (
                "camera_frame_available",
                {"real_camera_accessed": True, "camera_capture_started": True},
            ),
        ),
    )


def build_demo_blocked_speech_recognition_event() -> dict[str, object]:
    return _build_sensor_event_bundle(
        mic_specs=(
            (
                "mic_level_changed",
                {"speech_recognition_created": True, "speech_text": "hello"},
            ),
        ),
    )


def build_demo_blocked_runtime_eventframe_bridge_event() -> dict[str, object]:
    return _build_sensor_event_bundle(
        idle_specs=(("host_idle", {}),),
        runtime_eventframe_bridge_created=True,
    )


def build_demo_blocked_external_control_sensor_event() -> dict[str, object]:
    return _build_sensor_event_bundle(
        camera_specs=(("camera_frame_changed", {"external_control_created": True}),)
    )


def build_demo_blocked_first_output_sensor_event() -> dict[str, object]:
    return _build_sensor_event_bundle(
        idle_specs=(("host_status_available", {"first_output_created": True}),)
    )


def render_host_sensor_event_summary_text(
    audit: HostBodySensorEventAudit | dict[str, object],
    readiness: HostBodySensorEventReadinessRecord | dict[str, object] | None = None,
) -> str:
    audit_record = _audit(audit)
    readiness_record = _readiness(readiness) if readiness is not None else None
    parts = [
        f"host_sensor_event_audit={audit_record.audit_status}",
        f"fixture_only={audit_record.fixture_only_confirmed}",
        f"read_only={audit_record.read_only_confirmed}",
    ]
    if readiness_record is not None:
        parts.append(f"readiness={readiness_record.readiness_status}")
    return " ".join(parts)


def render_host_sensor_event_table(
    *,
    camera_events: tuple[HostBodyCameraEventRecord | dict[str, object], ...] | list[HostBodyCameraEventRecord | dict[str, object]] = tuple(),
    mic_events: tuple[HostBodyMicEventRecord | dict[str, object], ...] | list[HostBodyMicEventRecord | dict[str, object]] = tuple(),
    idle_events: tuple[HostBodyIdleEventRecord | dict[str, object], ...] | list[HostBodyIdleEventRecord | dict[str, object]] = tuple(),
) -> str:
    rows = ["event | family | status"]
    for item in tuple(_camera_event(event) for event in camera_events):
        rows.append(f"{item.camera_event_type} | camera_low_level_event | {item.camera_event_status}")
    for item in tuple(_mic_event(event) for event in mic_events):
        rows.append(f"{item.mic_event_type} | mic_low_level_event | {item.mic_event_status}")
    for item in tuple(_idle_event(event) for event in idle_events):
        rows.append(f"{item.idle_event_type} | host_idle_event | {item.idle_event_status}")
    return "\n".join(rows)


def classify_host_body_event_type(event_type: str) -> str:
    if event_type in CAMERA_EVENT_TYPES:
        return "camera_low_level_event"
    if event_type in MIC_EVENT_TYPES:
        return "mic_low_level_event"
    if event_type in {"host_idle", "host_low_activity_tick"}:
        return "host_idle_event"
    if event_type in {"host_power_on_observed", "host_status_available", "host_unknown_status_event"}:
        return "host_status_event"
    return "unknown_host_body_event"


def _build_sensor_event_bundle(
    *,
    camera_specs: tuple[tuple[str, dict[str, Any]], ...] = tuple(),
    mic_specs: tuple[tuple[str, dict[str, Any]], ...] = tuple(),
    idle_specs: tuple[tuple[str, dict[str, Any]], ...] = tuple(),
    runtime_eventframe_bridge_created: bool = False,
) -> dict[str, object]:
    port_payload = build_demo_qingyin_host_body_port_map()
    port_map = HostBodyPortMapRecord.from_dict(port_payload["host_body_port_map"])
    camera_port_id = str(port_payload["host_camera_port"]["host_camera_port_id"])
    mic_port_id = str(port_payload["host_mic_port"]["host_mic_port_id"])
    host_events: list[HostBodyEventRecord] = []
    camera_events: list[HostBodyCameraEventRecord] = []
    mic_events: list[HostBodyMicEventRecord] = []
    idle_events: list[HostBodyIdleEventRecord] = []

    for event_type, kwargs in camera_specs:
        event = build_host_body_event_record(
            source_host_body_port_map_id=port_map.host_body_port_map_id,
            source_port_id=camera_port_id,
            source_port_kind="camera_port",
            event_type=event_type,
            event_payload={"fixture": event_type},
            semantic_label=kwargs.get("semantic_label"),
            real_hardware_event=bool(kwargs.get("real_hardware_event", False)),
            real_camera_accessed=bool(kwargs.get("real_camera_accessed", False)),
            camera_capture_started=bool(kwargs.get("camera_capture_started", False)),
            image_frame_stored=bool(kwargs.get("image_frame_stored", False)),
            semantic_vision_created=bool(kwargs.get("semantic_vision_created", False)),
            object_recognition_created=bool(kwargs.get("object_recognition_created", False)),
            face_recognition_created=bool(kwargs.get("face_recognition_created", False)),
            action_selection_influence_created=bool(kwargs.get("action_selection_influence_created", False)),
            external_control_created=bool(kwargs.get("external_control_created", False)),
            memory_layer_write_performed=bool(kwargs.get("memory_layer_write_performed", False)),
            automatic_learning_approval_created=bool(kwargs.get("automatic_learning_approval_created", False)),
            first_output_created=bool(kwargs.get("first_output_created", False)),
            live_runtime_session_created=bool(kwargs.get("live_runtime_session_created", False)),
            source_trace_refs=(port_map.host_body_port_map_id,),
        )
        camera = build_host_body_camera_event_record(
            host_body_event=event,
            source_camera_port_id=camera_port_id,
            camera_event_type=event_type,
            fixture_frame_id=f"fixture_frame:{_slug(event_type)}",
            brightness_bucket=kwargs.get("brightness_bucket"),
            motion_proxy_bucket=kwargs.get("motion_proxy_bucket"),
            change_bucket=kwargs.get("change_bucket"),
            semantic_label=kwargs.get("semantic_label"),
            real_camera_accessed=bool(kwargs.get("real_camera_accessed", False)),
            camera_capture_started=bool(kwargs.get("camera_capture_started", False)),
            image_frame_stored=bool(kwargs.get("image_frame_stored", False)),
            semantic_vision_created=bool(kwargs.get("semantic_vision_created", False)),
            object_recognition_created=bool(kwargs.get("object_recognition_created", False)),
            face_recognition_created=bool(kwargs.get("face_recognition_created", False)),
            person_identification_created=bool(kwargs.get("person_identification_created", False)),
            scene_understanding_created=bool(kwargs.get("scene_understanding_created", False)),
            vision_to_action_created=bool(kwargs.get("vision_to_action_created", False)),
        )
        host_events.append(event)
        camera_events.append(camera)

    for event_type, kwargs in mic_specs:
        event = build_host_body_event_record(
            source_host_body_port_map_id=port_map.host_body_port_map_id,
            source_port_id=mic_port_id,
            source_port_kind="mic_port",
            event_type=event_type,
            event_payload={"fixture": event_type},
            real_hardware_event=bool(kwargs.get("real_hardware_event", False)),
            real_mic_accessed=bool(kwargs.get("real_mic_accessed", False)),
            mic_stream_started=bool(kwargs.get("mic_stream_started", False)),
            audio_stored=bool(kwargs.get("audio_stored", False)),
            speech_recognition_created=bool(kwargs.get("speech_recognition_created", False)),
            speaker_identification_created=bool(kwargs.get("speaker_identification_created", False)),
            voice_command_created=bool(kwargs.get("voice_command_created", False)),
            language_understanding_created=bool(kwargs.get("language_understanding_created", False)),
            action_selection_influence_created=bool(kwargs.get("action_selection_influence_created", False)),
            external_control_created=bool(kwargs.get("external_control_created", False)),
            memory_layer_write_performed=bool(kwargs.get("memory_layer_write_performed", False)),
            automatic_learning_approval_created=bool(kwargs.get("automatic_learning_approval_created", False)),
            first_output_created=bool(kwargs.get("first_output_created", False)),
            live_runtime_session_created=bool(kwargs.get("live_runtime_session_created", False)),
            source_trace_refs=(port_map.host_body_port_map_id,),
        )
        mic = build_host_body_mic_event_record(
            host_body_event=event,
            source_mic_port_id=mic_port_id,
            mic_event_type=event_type,
            fixture_audio_event_id=f"fixture_audio:{_slug(event_type)}",
            sound_level_bucket=kwargs.get("sound_level_bucket"),
            peak_detected=bool(kwargs.get("peak_detected", False)),
            silence_detected=bool(kwargs.get("silence_detected", False)),
            sustained_noise_detected=bool(kwargs.get("sustained_noise_detected", False)),
            speech_text=kwargs.get("speech_text"),
            speaker_id=kwargs.get("speaker_id"),
            real_mic_accessed=bool(kwargs.get("real_mic_accessed", False)),
            mic_stream_started=bool(kwargs.get("mic_stream_started", False)),
            audio_stored=bool(kwargs.get("audio_stored", False)),
            speech_recognition_created=bool(kwargs.get("speech_recognition_created", False)),
            speaker_identification_created=bool(kwargs.get("speaker_identification_created", False)),
            voice_command_created=bool(kwargs.get("voice_command_created", False)),
            language_understanding_created=bool(kwargs.get("language_understanding_created", False)),
            audio_to_action_created=bool(kwargs.get("audio_to_action_created", False)),
        )
        host_events.append(event)
        mic_events.append(mic)

    for event_type, kwargs in idle_specs:
        event = build_host_body_event_record(
            source_host_body_port_map_id=port_map.host_body_port_map_id,
            source_port_id=None,
            source_port_kind="host_status_port",
            event_type=event_type,
            event_payload={"fixture": event_type},
            external_control_created=bool(kwargs.get("external_control_created", False)),
            memory_layer_write_performed=bool(kwargs.get("memory_layer_write_performed", False)),
            automatic_learning_approval_created=bool(kwargs.get("automatic_learning_approval_created", False)),
            first_output_created=bool(kwargs.get("first_output_created", False)),
            live_runtime_session_created=bool(kwargs.get("live_runtime_session_created", False)),
            source_trace_refs=(port_map.host_body_port_map_id,),
        )
        idle = build_host_body_idle_event_record(
            host_body_event=event,
            idle_event_type=event_type,
            host_power_state=kwargs.get("host_power_state", "host_power_on_fixture"),
            host_activity_bucket=kwargs.get("host_activity_bucket", "idle"),
            runtime_tick_created=bool(kwargs.get("runtime_tick_created", False)),
            live_runtime_session_created=bool(kwargs.get("live_runtime_session_created", False)),
            autonomous_scheduler_created=bool(kwargs.get("autonomous_scheduler_created", False)),
            open_ended_loop_created=bool(kwargs.get("open_ended_loop_created", False)),
            background_daemon_created=bool(kwargs.get("background_daemon_created", False)),
            memory_layer_write_performed=bool(kwargs.get("memory_layer_write_performed", False)),
            automatic_learning_approval_created=bool(kwargs.get("automatic_learning_approval_created", False)),
            production_behavior_created=bool(kwargs.get("production_behavior_created", False)),
        )
        host_events.append(event)
        idle_events.append(idle)

    event_set = build_host_body_sensor_event_set_record(
        source_host_body_port_map_id=port_map.host_body_port_map_id,
        host_body_events=tuple(host_events),
        camera_events=tuple(camera_events),
        mic_events=tuple(mic_events),
        idle_events=tuple(idle_events),
        runtime_eventframe_bridge_created=runtime_eventframe_bridge_created,
    )
    summary = build_host_body_sensor_event_summary_record(
        host_sensor_event_set=event_set,
    )
    audit = build_host_body_sensor_event_audit(
        host_sensor_event_set=event_set,
        host_sensor_event_summary=summary,
        host_body_port_map=port_map,
        host_body_events=tuple(host_events),
        camera_events=tuple(camera_events),
        mic_events=tuple(mic_events),
        idle_events=tuple(idle_events),
        runtime_eventframe_bridge_created=runtime_eventframe_bridge_created,
    )
    readiness = build_host_body_sensor_event_readiness(audit)
    return {
        "host_body_port_map": port_map.to_dict(),
        "host_body_events": [item.to_dict() for item in host_events],
        "host_body_camera_events": [item.to_dict() for item in camera_events],
        "host_body_mic_events": [item.to_dict() for item in mic_events],
        "host_body_idle_events": [item.to_dict() for item in idle_events],
        "host_body_sensor_event_set": event_set.to_dict(),
        "host_body_sensor_event_summary": summary.to_dict(),
        "host_body_sensor_event_audit": audit.to_dict(),
        "host_body_sensor_event_readiness": readiness.to_dict(),
        "rendered_host_sensor_event_summary": render_host_sensor_event_summary_text(
            audit, readiness
        ),
        "rendered_host_sensor_event_table": render_host_sensor_event_table(
            camera_events=tuple(camera_events),
            mic_events=tuple(mic_events),
            idle_events=tuple(idle_events),
        ),
    }


def _event_status(
    *,
    semantic_label_requested: bool,
    real_hardware_event: bool,
    real_camera_accessed: bool,
    real_mic_accessed: bool,
    camera_capture_started: bool,
    mic_stream_started: bool,
    image_frame_stored: bool,
    audio_stored: bool,
    semantic_vision_created: bool,
    object_recognition_created: bool,
    face_recognition_created: bool,
    speech_recognition_created: bool,
    speaker_identification_created: bool,
    voice_command_created: bool,
    language_understanding_created: bool,
    action_selection_influence_created: bool,
    external_control_created: bool,
    memory_layer_write_performed: bool,
    automatic_learning_approval_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
) -> str:
    if (
        real_hardware_event
        or real_camera_accessed
        or real_mic_accessed
        or camera_capture_started
        or mic_stream_started
        or image_frame_stored
        or audio_stored
    ):
        return "host_body_event_blocked_real_hardware"
    if (
        semantic_label_requested
        or semantic_vision_created
        or object_recognition_created
        or face_recognition_created
        or speech_recognition_created
        or speaker_identification_created
        or voice_command_created
        or language_understanding_created
        or action_selection_influence_created
    ):
        return "host_body_event_blocked_semantic_interpretation"
    if external_control_created:
        return "host_body_event_blocked_external_control"
    if memory_layer_write_performed or automatic_learning_approval_created:
        return "host_body_event_blocked_memory_write"
    if first_output_created or live_runtime_session_created:
        return "host_body_event_blocked_first_output"
    return "host_body_event_recorded_fixture_only"


def _camera_event_status(
    *,
    semantic_label_requested: bool,
    real_camera_accessed: bool,
    camera_capture_started: bool,
    image_frame_stored: bool,
    semantic_vision_created: bool,
    object_recognition_created: bool,
    face_recognition_created: bool,
    person_identification_created: bool,
    scene_understanding_created: bool,
    vision_to_action_created: bool,
) -> str:
    if real_camera_accessed or camera_capture_started or image_frame_stored:
        return "camera_event_blocked_real_camera"
    if object_recognition_created or face_recognition_created or person_identification_created:
        return "camera_event_blocked_object_recognition"
    if semantic_label_requested or semantic_vision_created or scene_understanding_created:
        return "camera_event_blocked_semantic_vision"
    if vision_to_action_created:
        return "camera_event_blocked_vision_to_action"
    return "camera_event_recorded_fixture_only"


def _mic_event_status(
    *,
    speech_text_requested: bool,
    speaker_id_requested: bool,
    real_mic_accessed: bool,
    mic_stream_started: bool,
    audio_stored: bool,
    speech_recognition_created: bool,
    speaker_identification_created: bool,
    voice_command_created: bool,
    language_understanding_created: bool,
    audio_to_action_created: bool,
) -> str:
    if real_mic_accessed or mic_stream_started or audio_stored:
        return "mic_event_blocked_real_mic"
    if voice_command_created:
        return "mic_event_blocked_voice_command"
    if (
        speech_text_requested
        or speaker_id_requested
        or speech_recognition_created
        or speaker_identification_created
        or language_understanding_created
    ):
        return "mic_event_blocked_speech_recognition"
    if audio_to_action_created:
        return "mic_event_blocked_audio_to_action"
    return "mic_event_recorded_fixture_only"


def _idle_event_status(
    *,
    runtime_tick_created: bool,
    live_runtime_session_created: bool,
    autonomous_scheduler_created: bool,
    open_ended_loop_created: bool,
    background_daemon_created: bool,
    memory_layer_write_performed: bool,
    automatic_learning_approval_created: bool,
    production_behavior_created: bool,
) -> str:
    if runtime_tick_created or live_runtime_session_created:
        return "host_idle_event_blocked_live_runtime_tick"
    if autonomous_scheduler_created or background_daemon_created:
        return "host_idle_event_blocked_autonomous_scheduler"
    if open_ended_loop_created:
        return "host_idle_event_blocked_open_ended_loop"
    if memory_layer_write_performed or automatic_learning_approval_created or production_behavior_created:
        return "host_idle_event_blocked_live_runtime_tick"
    return "host_idle_event_recorded_fixture_only"


def _event_set_status(
    *,
    host_items: tuple[HostBodyEventRecord, ...],
    camera_items: tuple[HostBodyCameraEventRecord, ...],
    mic_items: tuple[HostBodyMicEventRecord, ...],
    idle_items: tuple[HostBodyIdleEventRecord, ...],
    runtime_eventframe_bridge_created: bool,
) -> str:
    if _event_set_has_real_hardware(host_items, camera_items, mic_items):
        return "host_sensor_event_set_blocked_real_hardware"
    if _event_set_has_semantic(host_items, camera_items, mic_items):
        return "host_sensor_event_set_blocked_semantic_interpretation"
    if _event_set_has_external_control(host_items):
        return "host_sensor_event_set_blocked_external_control"
    if _event_set_has_memory_write(host_items, idle_items):
        return "host_sensor_event_set_blocked_memory_write"
    if _event_set_has_first_output(host_items) or runtime_eventframe_bridge_created:
        return "host_sensor_event_set_blocked_first_output"
    if _event_set_has_live_runtime(host_items, idle_items):
        return "host_sensor_event_set_blocked_first_output"
    return "host_sensor_event_set_recorded_fixture_only"


def _event_set_kind(
    camera_items: tuple[HostBodyCameraEventRecord, ...],
    mic_items: tuple[HostBodyMicEventRecord, ...],
    idle_items: tuple[HostBodyIdleEventRecord, ...],
) -> str:
    counts = (len(camera_items), len(mic_items), len(idle_items))
    if counts[0] and not counts[1] and not counts[2]:
        return "single_camera_event_demo"
    if counts[1] and not counts[0] and not counts[2]:
        return "single_mic_event_demo"
    if counts[2] and not counts[0] and not counts[1]:
        return "single_idle_event_demo"
    return "mixed_host_sensor_event_demo"


def _audit_reasons(
    *,
    port_map: HostBodyPortMapRecord | None,
    event_set: HostBodySensorEventSetRecord | None,
    summary: HostBodySensorEventSummaryRecord | None,
    host_items: tuple[HostBodyEventRecord, ...],
    camera_items: tuple[HostBodyCameraEventRecord, ...],
    mic_items: tuple[HostBodyMicEventRecord, ...],
    idle_items: tuple[HostBodyIdleEventRecord, ...],
    runtime_eventframe_bridge_created: bool,
    force_autonomous_scheduler: bool,
    force_open_ended_loop: bool,
    force_thought_engine_behavior: bool,
    force_production_behavior: bool,
) -> list[str]:
    reasons: list[str] = []
    if port_map is None or port_map.port_map_status != "host_body_port_map_created":
        reasons.append("missing_or_invalid_port_map")
    if event_set is None:
        reasons.append("missing_event_set")
    if summary is None:
        reasons.append("missing_summary")
    for item in host_items:
        if not item.fixture_only:
            reasons.append("not_fixture_only")
        if not item.read_only_event:
            reasons.append("not_read_only")
        if item.real_camera_accessed:
            reasons.append("real_camera_access")
        if item.real_mic_accessed:
            reasons.append("real_mic_access")
        if item.camera_capture_started:
            reasons.append("camera_capture")
        if item.mic_stream_started:
            reasons.append("mic_stream")
        if item.image_frame_stored:
            reasons.append("image_storage")
        if item.audio_stored:
            reasons.append("audio_storage")
        if item.semantic_vision_created:
            reasons.append("semantic_vision")
        if item.object_recognition_created:
            reasons.append("object_recognition")
            reasons.append("semantic_vision")
        if item.face_recognition_created:
            reasons.append("face_recognition")
            reasons.append("semantic_vision")
        if item.speech_recognition_created:
            reasons.append("speech_recognition")
        if item.speaker_identification_created:
            reasons.append("speaker_identification")
            reasons.append("speech_recognition")
        if item.voice_command_created:
            reasons.append("voice_command")
            reasons.append("speech_recognition")
        if item.language_understanding_created:
            reasons.append("language_understanding")
            reasons.append("speech_recognition")
        if item.action_selection_influence_created:
            reasons.append("action_selection_influence")
        if item.external_control_created:
            reasons.append("external_control")
        if item.memory_layer_write_performed:
            reasons.append("memory_write")
        if item.automatic_learning_approval_created:
            reasons.append("automatic_learning_approval")
            reasons.append("memory_write")
        if item.first_output_created:
            reasons.append("first_output")
        if item.live_runtime_session_created:
            reasons.append("live_runtime_session")
    for item in camera_items:
        if item.real_camera_accessed:
            reasons.append("real_camera_access")
        if item.camera_capture_started:
            reasons.append("camera_capture")
        if item.image_frame_stored:
            reasons.append("image_storage")
        if item.semantic_vision_created or item.scene_understanding_created:
            reasons.append("semantic_vision")
        if item.object_recognition_created or item.person_identification_created:
            reasons.append("object_recognition")
            reasons.append("semantic_vision")
        if item.face_recognition_created:
            reasons.append("face_recognition")
            reasons.append("semantic_vision")
        if item.vision_to_action_created:
            reasons.append("action_selection_influence")
    for item in mic_items:
        if item.real_mic_accessed:
            reasons.append("real_mic_access")
        if item.mic_stream_started:
            reasons.append("mic_stream")
        if item.audio_stored:
            reasons.append("audio_storage")
        if item.speech_recognition_created:
            reasons.append("speech_recognition")
        if item.speaker_identification_created:
            reasons.append("speaker_identification")
            reasons.append("speech_recognition")
        if item.voice_command_created:
            reasons.append("voice_command")
            reasons.append("speech_recognition")
        if item.language_understanding_created:
            reasons.append("language_understanding")
            reasons.append("speech_recognition")
        if item.audio_to_action_created:
            reasons.append("action_selection_influence")
    for item in idle_items:
        if item.runtime_tick_created or item.live_runtime_session_created:
            reasons.append("live_runtime_session")
        if item.autonomous_scheduler_created or item.background_daemon_created:
            reasons.append("autonomous_scheduler")
        if item.open_ended_loop_created:
            reasons.append("open_ended_loop")
        if item.memory_layer_write_performed:
            reasons.append("memory_write")
        if item.automatic_learning_approval_created:
            reasons.append("automatic_learning_approval")
            reasons.append("memory_write")
        if item.production_behavior_created:
            reasons.append("production_behavior")
    if event_set is not None:
        if event_set.external_control_created:
            reasons.append("external_control")
        if event_set.memory_layer_write_performed:
            reasons.append("memory_write")
        if event_set.first_output_created:
            reasons.append("first_output")
        if event_set.live_runtime_session_created:
            reasons.append("live_runtime_session")
    if summary is not None:
        if summary.semantic_interpretation_created:
            reasons.append("semantic_interpretation")
        if summary.action_selection_influence_created:
            reasons.append("action_selection_influence")
        if summary.memory_layer_write_performed:
            reasons.append("memory_write")
        if summary.first_output_created:
            reasons.append("first_output")
        if summary.external_control_created:
            reasons.append("external_control")
    if runtime_eventframe_bridge_created:
        reasons.append("runtime_eventframe_bridge")
    if force_autonomous_scheduler:
        reasons.append("autonomous_scheduler")
    if force_open_ended_loop:
        reasons.append("open_ended_loop")
    if force_thought_engine_behavior:
        reasons.append("thought_engine_behavior")
    if force_production_behavior:
        reasons.append("production_behavior")
    return list(dict.fromkeys(reasons))


def _audit_status(
    reasons: list[str],
    event_set: HostBodySensorEventSetRecord | None,
) -> str:
    priority = (
        ("real_camera_access", "blocked_real_camera_access_detected"),
        ("camera_capture", "blocked_real_camera_access_detected"),
        ("real_mic_access", "blocked_real_mic_access_detected"),
        ("mic_stream", "blocked_real_mic_access_detected"),
        ("semantic_vision", "blocked_semantic_vision_detected"),
        ("object_recognition", "blocked_semantic_vision_detected"),
        ("face_recognition", "blocked_semantic_vision_detected"),
        ("speech_recognition", "blocked_speech_recognition_detected"),
        ("speaker_identification", "blocked_speech_recognition_detected"),
        ("voice_command", "blocked_speech_recognition_detected"),
        ("language_understanding", "blocked_speech_recognition_detected"),
        ("action_selection_influence", "blocked_action_selection_influence_detected"),
        ("external_control", "blocked_external_control_detected"),
        ("memory_write", "blocked_memory_write_detected"),
        ("first_output", "blocked_first_output_detected"),
        ("runtime_eventframe_bridge", "blocked_runtime_eventframe_bridge_detected"),
        ("live_runtime_session", "blocked_live_runtime_detected"),
        ("autonomous_scheduler", "blocked_forbidden_authority_detected"),
        ("open_ended_loop", "blocked_forbidden_authority_detected"),
        ("thought_engine_behavior", "blocked_forbidden_authority_detected"),
        ("production_behavior", "blocked_forbidden_authority_detected"),
    )
    for reason, status in priority:
        if reason in reasons:
            return status
    if event_set is not None:
        if event_set.event_set_kind == "single_camera_event_demo":
            return "passed_camera_fixture_event_only"
        if event_set.event_set_kind == "single_mic_event_demo":
            return "passed_mic_fixture_event_only"
        if event_set.event_set_kind == "single_idle_event_demo":
            return "passed_idle_fixture_event_only"
    return "passed_host_body_read_only_sensor_event_shell"


def _event_set_has_real_hardware(
    host_items: tuple[HostBodyEventRecord, ...],
    camera_items: tuple[HostBodyCameraEventRecord, ...],
    mic_items: tuple[HostBodyMicEventRecord, ...],
) -> bool:
    return any(
        item.real_hardware_event
        or item.real_camera_accessed
        or item.real_mic_accessed
        or item.camera_capture_started
        or item.mic_stream_started
        or item.image_frame_stored
        or item.audio_stored
        for item in host_items
    ) or any(
        item.real_camera_accessed or item.camera_capture_started or item.image_frame_stored
        for item in camera_items
    ) or any(
        item.real_mic_accessed or item.mic_stream_started or item.audio_stored
        for item in mic_items
    )


def _event_set_has_semantic(
    host_items: tuple[HostBodyEventRecord, ...],
    camera_items: tuple[HostBodyCameraEventRecord, ...],
    mic_items: tuple[HostBodyMicEventRecord, ...],
) -> bool:
    return any(
        item.semantic_vision_created
        or item.object_recognition_created
        or item.face_recognition_created
        or item.speech_recognition_created
        or item.speaker_identification_created
        or item.voice_command_created
        or item.language_understanding_created
        or item.action_selection_influence_created
        for item in host_items
    ) or any(
        item.semantic_vision_created
        or item.object_recognition_created
        or item.face_recognition_created
        or item.person_identification_created
        or item.scene_understanding_created
        or item.vision_to_action_created
        for item in camera_items
    ) or any(
        item.speech_recognition_created
        or item.speaker_identification_created
        or item.voice_command_created
        or item.language_understanding_created
        or item.audio_to_action_created
        for item in mic_items
    )


def _event_set_has_external_control(host_items: tuple[HostBodyEventRecord, ...]) -> bool:
    return any(item.external_control_created for item in host_items)


def _event_set_has_memory_write(
    host_items: tuple[HostBodyEventRecord, ...],
    idle_items: tuple[HostBodyIdleEventRecord, ...],
) -> bool:
    return any(
        item.memory_layer_write_performed
        or item.automatic_learning_approval_created
        for item in host_items
    ) or any(
        item.memory_layer_write_performed or item.automatic_learning_approval_created
        for item in idle_items
    )


def _event_set_has_first_output(host_items: tuple[HostBodyEventRecord, ...]) -> bool:
    return any(item.first_output_created for item in host_items)


def _event_set_has_live_runtime(
    host_items: tuple[HostBodyEventRecord, ...],
    idle_items: tuple[HostBodyIdleEventRecord, ...],
) -> bool:
    return any(item.live_runtime_session_created for item in host_items) or any(
        item.runtime_tick_created or item.live_runtime_session_created for item in idle_items
    )


def _host_body_event_has_forbidden_boundary(item: HostBodyEventRecord) -> bool:
    return (
        item.real_hardware_event
        or item.real_camera_accessed
        or item.real_mic_accessed
        or item.camera_capture_started
        or item.mic_stream_started
        or item.image_frame_stored
        or item.audio_stored
        or item.semantic_vision_created
        or item.object_recognition_created
        or item.face_recognition_created
        or item.speech_recognition_created
        or item.speaker_identification_created
        or item.voice_command_created
        or item.language_understanding_created
        or item.action_selection_influence_created
        or item.external_control_created
        or item.memory_layer_write_performed
        or item.automatic_learning_approval_created
        or item.first_output_created
        or item.live_runtime_session_created
    )


def _event_summary(status: str, event_type: str) -> str:
    if status == "host_body_event_recorded_fixture_only":
        return f"{event_type} recorded as fixture-only read-only HostBodyEvent."
    return f"{event_type} blocked by HostBodyEvent boundary: {status}."


def _camera_event_summary(status: str, event_type: str) -> str:
    if status == "camera_event_recorded_fixture_only":
        return f"{event_type} recorded as low-level camera fixture event only."
    return f"{event_type} camera fixture blocked: {status}."


def _mic_event_summary(status: str, event_type: str) -> str:
    if status == "mic_event_recorded_fixture_only":
        return f"{event_type} recorded as low-level mic fixture event only."
    return f"{event_type} mic fixture blocked: {status}."


def _idle_event_summary(status: str, event_type: str) -> str:
    if status == "host_idle_event_recorded_fixture_only":
        return f"{event_type} recorded as host idle/status fixture event only."
    return f"{event_type} idle fixture blocked: {status}."


def _event_set_summary(status: str) -> str:
    if status == "host_sensor_event_set_recorded_fixture_only":
        return "Fixture-only read-only Host Body sensor event set recorded."
    return f"Host Body sensor event set blocked: {status}."


def _summary_text(event_set: HostBodySensorEventSetRecord, status: str) -> str:
    if status == "host_sensor_event_summary_recorded":
        return (
            f"{event_set.total_event_count} low-level fixture HostBodyEvent records "
            "summarized without interpretation."
        )
    return f"Host Body sensor event summary blocked for {event_set.event_set_status}."


def _readiness_summary(status: str) -> str:
    if status == "ready_for_host_body_event_runtime_eventframe_bridge_only":
        return "Ready only for fixture HostBodyEvent to Runtime EventFrame bridge."
    if status == "ready_for_unity_home_internal_space_surface_only":
        return "Ready only for Unity Home internal-space surface."
    return f"Host Body sensor event readiness blocked: {status}."


def _first_trace_refs(items: tuple[HostBodyEventRecord, ...]) -> tuple[str, ...]:
    return items[0].source_trace_refs if items else tuple()


def _validation(valid: bool, errors: list[str], record_id: str, status: str) -> dict[str, object]:
    return {
        "valid": valid,
        "error_codes": tuple(errors),
        "record_id": record_id,
        "status": status,
    }


def _port_map(value: HostBodyPortMapRecord | dict[str, object]) -> HostBodyPortMapRecord:
    return value if isinstance(value, HostBodyPortMapRecord) else HostBodyPortMapRecord.from_dict(value)


def _event(value: HostBodyEventRecord | dict[str, object]) -> HostBodyEventRecord:
    return value if isinstance(value, HostBodyEventRecord) else HostBodyEventRecord.from_dict(value)


def _camera_event(
    value: HostBodyCameraEventRecord | dict[str, object],
) -> HostBodyCameraEventRecord:
    return value if isinstance(value, HostBodyCameraEventRecord) else HostBodyCameraEventRecord.from_dict(value)


def _mic_event(value: HostBodyMicEventRecord | dict[str, object]) -> HostBodyMicEventRecord:
    return value if isinstance(value, HostBodyMicEventRecord) else HostBodyMicEventRecord.from_dict(value)


def _idle_event(
    value: HostBodyIdleEventRecord | dict[str, object],
) -> HostBodyIdleEventRecord:
    return value if isinstance(value, HostBodyIdleEventRecord) else HostBodyIdleEventRecord.from_dict(value)


def _event_set(
    value: HostBodySensorEventSetRecord | dict[str, object],
) -> HostBodySensorEventSetRecord:
    return value if isinstance(value, HostBodySensorEventSetRecord) else HostBodySensorEventSetRecord.from_dict(value)


def _summary(
    value: HostBodySensorEventSummaryRecord | dict[str, object],
) -> HostBodySensorEventSummaryRecord:
    return value if isinstance(value, HostBodySensorEventSummaryRecord) else HostBodySensorEventSummaryRecord.from_dict(value)


def _audit(value: HostBodySensorEventAudit | dict[str, object]) -> HostBodySensorEventAudit:
    return value if isinstance(value, HostBodySensorEventAudit) else HostBodySensorEventAudit.from_dict(value)


def _readiness(
    value: HostBodySensorEventReadinessRecord | dict[str, object],
) -> HostBodySensorEventReadinessRecord:
    return value if isinstance(value, HostBodySensorEventReadinessRecord) else HostBodySensorEventReadinessRecord.from_dict(value)
