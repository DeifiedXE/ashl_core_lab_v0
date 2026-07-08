"""Read-only Qingyin Home internal-space event surface records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.host_body.host_body_port_map import (
    HostBodyIdentityRecord,
    HostBodyPortMapRecord,
    HostInternalSpacePortRecord,
    build_demo_qingyin_host_body_port_map,
)
from ashl_core_v1.host_body.host_body_runtime_bridge import (
    HostBodyEventToRuntimeFrameMappingRecord,
    HostBodyRuntimeBridgeAudit,
    HostBodyRuntimeBridgeTraceRecord,
    HostBodyRuntimeDispatchLinkRecord,
    build_demo_deferred_dispatch_host_body_runtime_bridge,
    build_demo_mixed_host_body_runtime_bridge,
)
from ashl_core_v1.host_body.host_body_sensor_events import (
    HostBodySensorEventSetRecord,
    build_demo_mixed_host_sensor_event_set,
)


SOURCE_ENGINE = "host_body"

PLAN_SCHEMA_VERSION = "qingyin_home_internal_space_surface_plan_v0"
PORT_SURFACE_SCHEMA_VERSION = "qingyin_home_port_surface_v0"
HOST_EVENT_SURFACE_SCHEMA_VERSION = "qingyin_home_host_event_surface_v0"
RUNTIME_BRIDGE_SURFACE_SCHEMA_VERSION = "qingyin_home_runtime_bridge_surface_v0"
STATUS_LIGHT_SCHEMA_VERSION = "qingyin_home_status_light_v0"
TEACHER_SURFACE_SCHEMA_VERSION = "qingyin_home_teacher_observed_surface_v0"
RENDER_SCHEMA_VERSION = "qingyin_home_internal_space_render_v0"
AUDIT_SCHEMA_VERSION = "qingyin_home_internal_space_surface_audit_v0"
READINESS_SCHEMA_VERSION = "qingyin_home_internal_space_surface_readiness_v0"

SURFACE_NAME = "qingyin_home"
SURFACE_KIND = "internal_space_event_surface"

ALLOWED_SURFACE_SECTIONS = (
    "host_body_identity",
    "host_body_ports",
    "recent_host_events",
    "runtime_eventframe_bridge",
    "status_lights",
    "teacher_observed_summary",
    "readiness_summary",
)
BLOCKED_SURFACE_SECTIONS = (
    "avatar_body_control_surface",
    "game_character_control_surface",
    "desktop_control_surface",
    "external_tool_control_surface",
    "first_output_surface",
    "free_chat_surface",
    "voice_conversation_surface",
)
TEACHER_OBSERVED_SECTIONS = (
    "host_body_identity",
    "host_body_ports",
    "recent_host_events",
    "runtime_bridge_status",
    "status_lights",
    "readiness",
    "boundary_warnings",
)

SAFE_CLAIM = (
    "ASHL Core v1 can represent Qingyin Home as a read-only internal-space "
    "event surface for the Qingyin Host Body."
)
BLOCKED_CLAIMS = (
    "no_unity_runtime_connection",
    "no_avatar_control",
    "no_real_sensor_access",
    "no_semantic_vision",
    "no_speech_recognition",
    "no_action_selection_influence",
    "no_external_control",
    "no_memory_layer_write",
    "no_teacher_approval_created",
    "no_first_output",
    "no_live_runtime_session",
    "not_awake",
)
READINESS_NEXT_PACKAGE = "Package 105 / ASHL Core v1 Host Body Trace History Lane Minimal v0"


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


def _tuple_of_dict(name: str, value: tuple[dict[str, Any], ...] | list[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    items = tuple(dict(item) for item in value)
    return items


def _slug(text: str) -> str:
    safe = [char.lower() if char.isalnum() else "_" for char in text]
    return "_".join("".join(safe).split("_"))[:100] or "empty"


@dataclass(frozen=True)
class QingyinHomeInternalSpaceSurfacePlanRecord:
    home_surface_plan_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_identity_id: str | None
    source_host_body_port_map_id: str | None
    source_internal_space_port_id: str | None
    source_host_runtime_bridge_audit_id: str | None
    surface_name: str
    surface_kind: str
    allowed_surface_sections: tuple[str, ...]
    blocked_surface_sections: tuple[str, ...]
    read_only_surface: bool
    internal_space_only: bool
    teacher_observed_only: bool
    unity_runtime_connection_allowed: bool
    unity_scene_mutation_allowed: bool
    avatar_control_allowed: bool
    game_character_control_allowed: bool
    real_camera_access_allowed: bool
    real_mic_access_allowed: bool
    semantic_interpretation_allowed: bool
    speech_recognition_allowed: bool
    action_selection_allowed: bool
    external_control_allowed: bool
    memory_write_allowed: bool
    automatic_learning_approval_allowed: bool
    first_output_allowed: bool
    live_runtime_session_allowed: bool
    surface_plan_status: str
    surface_plan_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PLAN_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_home_internal_space_surface_plan_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.surface_name != SURFACE_NAME:
            raise ValueError("surface_name must be qingyin_home")
        if self.surface_kind != SURFACE_KIND:
            raise ValueError("surface_kind must be internal_space_event_surface")
        if self.surface_plan_status not in {
            "surface_plan_created",
            "blocked_missing_host_body_port_map",
            "blocked_missing_runtime_bridge_audit",
            "blocked_unity_runtime_connection_requested",
            "blocked_avatar_control_requested",
            "blocked_external_control_requested",
            "blocked_first_output_requested",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown surface_plan_status: {self.surface_plan_status}")
        for name in ("allowed_surface_sections", "blocked_surface_sections", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHomeInternalSpaceSurfacePlanRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class QingyinHomePortSurfaceRecord:
    home_port_surface_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_plan_id: str
    source_host_body_port_map_id: str
    port_surface_kind: str
    port_surface_status: str
    port_surface_summary: str
    camera_port_visible: bool
    mic_port_visible: bool
    internal_space_port_visible: bool
    output_surface_port_visible: bool
    trace_history_port_visible: bool
    internal_action_port_visible: bool
    camera_port_label: str
    mic_port_label: str
    internal_space_label: str
    output_surface_label: str
    trace_history_label: str
    internal_action_label: str
    real_camera_connected: bool
    real_mic_connected: bool
    external_control_connected: bool
    memory_write_connected: bool
    first_output_connected: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PORT_SURFACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_home_port_surface_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.port_surface_kind not in {"read_only_port_map_surface", "blocked_port_map_surface"}:
            raise ValueError(f"unknown port_surface_kind: {self.port_surface_kind}")
        if self.port_surface_status not in {
            "port_surface_created",
            "blocked_missing_port_map",
            "blocked_real_hardware_connection_detected",
            "blocked_external_control_detected",
            "blocked_memory_write_detected",
            "blocked_first_output_detected",
        }:
            raise ValueError(f"unknown port_surface_status: {self.port_surface_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHomePortSurfaceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class QingyinHomeHostEventSurfaceRecord:
    home_host_event_surface_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_plan_id: str
    source_host_sensor_event_set_id: str | None
    source_host_runtime_bridge_trace_id: str | None
    surface_event_rows: tuple[dict[str, Any], ...]
    camera_event_count: int
    mic_event_count: int
    idle_event_count: int
    total_event_count: int
    host_event_surface_status: str
    host_event_surface_summary: str
    fixture_only_confirmed: bool
    read_only_confirmed: bool
    semantic_label_created: bool
    semantic_vision_created: bool
    speech_recognition_created: bool
    action_selection_influence_created: bool
    external_control_created: bool
    memory_write_performed: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HOST_EVENT_SURFACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_home_host_event_surface_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.host_event_surface_status not in {
            "host_event_surface_created",
            "host_event_surface_created_empty",
            "blocked_missing_host_sensor_event_set",
            "blocked_semantic_interpretation_detected",
            "blocked_action_selection_influence_detected",
            "blocked_external_control_detected",
            "blocked_first_output_detected",
        }:
            raise ValueError(f"unknown host_event_surface_status: {self.host_event_surface_status}")
        object.__setattr__(self, "surface_event_rows", _tuple_of_dict("surface_event_rows", self.surface_event_rows))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHomeHostEventSurfaceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class QingyinHomeRuntimeBridgeSurfaceRecord:
    home_runtime_bridge_surface_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_plan_id: str
    source_host_runtime_bridge_trace_id: str
    bridge_surface_rows: tuple[dict[str, Any], ...]
    bridged_event_count: int
    sense_eventframe_count: int
    runtime_eventframe_count: int
    state_eventframe_count: int
    deferred_dispatch_count: int
    runtime_bridge_surface_status: str
    runtime_bridge_surface_summary: str
    runtime_eventframe_bridge_visible: bool
    dispatch_adapter_status_visible: bool
    return_payload_status_visible: bool
    live_runtime_session_created: bool
    live_engine_invocation_created: bool
    dynamic_scheduling_created: bool
    external_execution_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    first_output_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RUNTIME_BRIDGE_SURFACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_home_runtime_bridge_surface_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.runtime_bridge_surface_status not in {
            "runtime_bridge_surface_created",
            "runtime_bridge_surface_created_with_deferred_dispatch",
            "blocked_missing_runtime_bridge_trace",
            "blocked_live_runtime_detected",
            "blocked_live_engine_invocation_detected",
            "blocked_dynamic_scheduling_detected",
            "blocked_memory_write_detected",
            "blocked_first_output_detected",
        }:
            raise ValueError(f"unknown runtime_bridge_surface_status: {self.runtime_bridge_surface_status}")
        object.__setattr__(self, "bridge_surface_rows", _tuple_of_dict("bridge_surface_rows", self.bridge_surface_rows))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHomeRuntimeBridgeSurfaceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class QingyinHomeStatusLightRecord:
    home_status_light_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_plan_id: str
    status_light_kind: str
    status_light_label: str
    status_light_state: str
    status_light_reason: str
    status_light_summary: str
    source_event_refs: tuple[str, ...]
    status_light_surface_status: str
    first_output_created: bool
    external_message_created: bool
    sound_output_played: bool
    screen_output_mutated: bool
    unity_runtime_mutated: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != STATUS_LIGHT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_home_status_light_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.status_light_kind not in {
            "host_body_ready",
            "sensor_event_seen",
            "runtime_bridge_ready",
            "teacher_review_pending",
            "boundary_warning",
            "idle",
            "unknown",
        }:
            raise ValueError(f"unknown status_light_kind: {self.status_light_kind}")
        if self.status_light_state not in {"off", "dim", "on", "warning", "blocked", "unknown"}:
            raise ValueError(f"unknown status_light_state: {self.status_light_state}")
        if self.status_light_surface_status not in {
            "status_light_recorded",
            "blocked_output_side_effect_detected",
            "blocked_first_output_detected",
            "blocked_unity_runtime_mutation_detected",
        }:
            raise ValueError(f"unknown status_light_surface_status: {self.status_light_surface_status}")
        for name in ("source_event_refs", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHomeStatusLightRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class QingyinHomeTeacherObservedSurfaceRecord:
    home_teacher_observed_surface_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_plan_id: str
    teacher_observed_sections: tuple[str, ...]
    observed_host_event_count: int
    observed_runtime_bridge_count: int
    observed_status_light_count: int
    teacher_review_prompt_created: bool
    teacher_action_required: bool
    teacher_surface_status: str
    teacher_surface_summary: str
    approval_created: bool
    learning_approval_created: bool
    memory_write_approval_created: bool
    first_output_created: bool
    external_control_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TEACHER_SURFACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_home_teacher_observed_surface_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.teacher_surface_status not in {
            "teacher_observed_surface_created",
            "teacher_observed_surface_created_empty",
            "blocked_approval_created",
            "blocked_learning_approval_created",
            "blocked_memory_write_approval_created",
            "blocked_first_output_detected",
            "blocked_external_control_detected",
        }:
            raise ValueError(f"unknown teacher_surface_status: {self.teacher_surface_status}")
        for name in ("teacher_observed_sections", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHomeTeacherObservedSurfaceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class QingyinHomeInternalSpaceRenderRecord:
    home_internal_space_render_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_plan_id: str
    source_port_surface_id: str | None
    source_host_event_surface_id: str | None
    source_runtime_bridge_surface_id: str | None
    source_teacher_surface_id: str | None
    status_light_ids: tuple[str, ...]
    render_kind: str
    render_payload: dict[str, Any]
    render_text: str
    render_status: str
    render_summary: str
    read_only_render: bool
    unity_runtime_started: bool
    unity_scene_mutated: bool
    avatar_control_created: bool
    game_character_control_created: bool
    file_written: bool
    network_output_created: bool
    first_output_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RENDER_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_home_internal_space_render_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.render_kind not in {
            "text_summary_render",
            "json_snapshot_render",
            "read_only_card_render",
            "status_light_render",
            "blocked_render",
        }:
            raise ValueError(f"unknown render_kind: {self.render_kind}")
        if self.render_status not in {
            "home_internal_space_render_created",
            "home_internal_space_render_created_empty",
            "blocked_unity_runtime_started",
            "blocked_unity_scene_mutation",
            "blocked_avatar_control",
            "blocked_file_write",
            "blocked_network_output",
            "blocked_first_output",
            "blocked_production_behavior",
        }:
            raise ValueError(f"unknown render_status: {self.render_status}")
        for name in ("status_light_ids", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHomeInternalSpaceRenderRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class QingyinHomeInternalSpaceSurfaceAudit:
    home_surface_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_plan_id: str | None
    source_port_surface_id: str | None
    source_host_event_surface_id: str | None
    source_runtime_bridge_surface_id: str | None
    source_teacher_surface_id: str | None
    source_render_id: str | None
    surface_plan_valid: bool
    port_surface_valid: bool
    host_event_surface_valid: bool
    runtime_bridge_surface_valid: bool
    status_lights_valid: bool
    teacher_surface_valid: bool
    render_valid: bool
    qingyin_home_internal_space_confirmed: bool
    avatar_projection_only_confirmed: bool
    read_only_surface_confirmed: bool
    teacher_observed_only_confirmed: bool
    no_unity_runtime_connection: bool
    no_unity_scene_mutation: bool
    no_avatar_control: bool
    no_game_character_control: bool
    no_real_camera_access: bool
    no_real_mic_access: bool
    no_semantic_vision: bool
    no_speech_recognition: bool
    no_action_selection_influence: bool
    no_external_control: bool
    no_os_control: bool
    no_mouse_control: bool
    no_keyboard_control: bool
    no_browser_control: bool
    no_file_operation: bool
    no_network_execution: bool
    no_shell_execution: bool
    no_memory_layer_write: bool
    no_automatic_learning_approval: bool
    no_teacher_approval_created: bool
    no_first_output: bool
    no_live_runtime_session: bool
    no_live_engine_invocation: bool
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
            raise ValueError("schema_version must be qingyin_home_internal_space_surface_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.audit_status not in {
            "passed_qingyin_home_internal_space_event_surface",
            "passed_home_surface_with_empty_events",
            "passed_home_surface_with_deferred_dispatch",
            "blocked_missing_home_surface_plan",
            "blocked_invalid_port_surface",
            "blocked_invalid_host_event_surface",
            "blocked_invalid_runtime_bridge_surface",
            "blocked_invalid_teacher_surface",
            "blocked_invalid_render",
            "blocked_unity_runtime_connection_detected",
            "blocked_unity_scene_mutation_detected",
            "blocked_avatar_control_detected",
            "blocked_external_control_detected",
            "blocked_memory_write_detected",
            "blocked_teacher_approval_created",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
            "blocked_production_behavior_detected",
        }:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHomeInternalSpaceSurfaceAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class QingyinHomeInternalSpaceSurfaceReadinessRecord:
    home_surface_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_host_body_trace_history_lane: bool
    ready_for_internal_action_choice_only: bool
    ready_for_teacher_observed_host_body_cli: bool
    ready_for_unity_runtime_connection: bool
    ready_for_avatar_control: bool
    ready_for_real_camera_connection: bool
    ready_for_real_mic_connection: bool
    ready_for_semantic_vision: bool
    ready_for_speech_recognition: bool
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
            raise ValueError("schema_version must be qingyin_home_internal_space_surface_readiness_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.readiness_status not in {
            "ready_for_host_body_trace_history_lane_only",
            "ready_for_internal_action_choice_only",
            "ready_for_teacher_observed_host_body_cli_only",
            "not_ready_missing_home_surface_audit",
            "not_ready_boundary_failure",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHomeInternalSpaceSurfaceReadinessRecord":
        return cls(**dict(data))


def build_qingyin_home_internal_space_surface_plan(
    *,
    host_body_identity: HostBodyIdentityRecord | dict[str, object] | None,
    host_body_port_map: HostBodyPortMapRecord | dict[str, object] | None,
    internal_space_port: HostInternalSpacePortRecord | dict[str, object] | None,
    host_runtime_bridge_audit: HostBodyRuntimeBridgeAudit | dict[str, object] | None,
    unity_runtime_connection_allowed: bool = False,
    unity_scene_mutation_allowed: bool = False,
    avatar_control_allowed: bool = False,
    game_character_control_allowed: bool = False,
    real_camera_access_allowed: bool = False,
    real_mic_access_allowed: bool = False,
    semantic_interpretation_allowed: bool = False,
    speech_recognition_allowed: bool = False,
    action_selection_allowed: bool = False,
    external_control_allowed: bool = False,
    memory_write_allowed: bool = False,
    automatic_learning_approval_allowed: bool = False,
    first_output_allowed: bool = False,
    live_runtime_session_allowed: bool = False,
) -> QingyinHomeInternalSpaceSurfacePlanRecord:
    identity = _identity(host_body_identity) if host_body_identity is not None else None
    port_map = _port_map(host_body_port_map) if host_body_port_map is not None else None
    internal_space = _internal_space(internal_space_port) if internal_space_port is not None else None
    bridge_audit = _bridge_audit(host_runtime_bridge_audit) if host_runtime_bridge_audit is not None else None
    status = _plan_status(
        port_map=port_map,
        internal_space=internal_space,
        bridge_audit=bridge_audit,
        unity_runtime_connection_allowed=unity_runtime_connection_allowed,
        unity_scene_mutation_allowed=unity_scene_mutation_allowed,
        avatar_control_allowed=avatar_control_allowed,
        game_character_control_allowed=game_character_control_allowed,
        real_camera_access_allowed=real_camera_access_allowed,
        real_mic_access_allowed=real_mic_access_allowed,
        semantic_interpretation_allowed=semantic_interpretation_allowed,
        speech_recognition_allowed=speech_recognition_allowed,
        action_selection_allowed=action_selection_allowed,
        external_control_allowed=external_control_allowed,
        memory_write_allowed=memory_write_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
    )
    return QingyinHomeInternalSpaceSurfacePlanRecord(
        home_surface_plan_id=f"qingyin_home_surface_plan:{_slug(status)}",
        schema_version=PLAN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_identity_id=identity.host_body_identity_id if identity else None,
        source_host_body_port_map_id=port_map.host_body_port_map_id if port_map else None,
        source_internal_space_port_id=internal_space.host_internal_space_port_id if internal_space else None,
        source_host_runtime_bridge_audit_id=bridge_audit.host_runtime_bridge_audit_id if bridge_audit else None,
        surface_name=SURFACE_NAME,
        surface_kind=SURFACE_KIND,
        allowed_surface_sections=ALLOWED_SURFACE_SECTIONS,
        blocked_surface_sections=BLOCKED_SURFACE_SECTIONS,
        read_only_surface=True,
        internal_space_only=True,
        teacher_observed_only=True,
        unity_runtime_connection_allowed=unity_runtime_connection_allowed,
        unity_scene_mutation_allowed=unity_scene_mutation_allowed,
        avatar_control_allowed=avatar_control_allowed,
        game_character_control_allowed=game_character_control_allowed,
        real_camera_access_allowed=real_camera_access_allowed,
        real_mic_access_allowed=real_mic_access_allowed,
        semantic_interpretation_allowed=semantic_interpretation_allowed,
        speech_recognition_allowed=speech_recognition_allowed,
        action_selection_allowed=action_selection_allowed,
        external_control_allowed=external_control_allowed,
        memory_write_allowed=memory_write_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
        surface_plan_status=status,
        surface_plan_summary=_plan_summary(status),
        source_trace_refs=bridge_audit.source_trace_refs if bridge_audit else tuple(),
    )


def validate_qingyin_home_internal_space_surface_plan(record: QingyinHomeInternalSpaceSurfacePlanRecord | dict[str, object]) -> dict[str, object]:
    try:
        item = _plan(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.surface_plan_status == "surface_plan_created":
        if item.source_host_body_port_map_id is None or item.source_internal_space_port_id is None:
            errors.append("missing_host_body_port_map_or_internal_space")
        if item.source_host_runtime_bridge_audit_id is None:
            errors.append("missing_runtime_bridge_audit")
        if _plan_has_forbidden_boundary(item):
            errors.append("plan_has_forbidden_boundary")
    return _validation(not errors, errors, item.home_surface_plan_id, item.surface_plan_status)


def build_qingyin_home_port_surface(
    *,
    home_surface_plan: QingyinHomeInternalSpaceSurfacePlanRecord | dict[str, object],
    host_body_port_map: HostBodyPortMapRecord | dict[str, object] | None,
    real_camera_connected: bool = False,
    real_mic_connected: bool = False,
    external_control_connected: bool = False,
    memory_write_connected: bool = False,
    first_output_connected: bool = False,
) -> QingyinHomePortSurfaceRecord:
    plan = _plan(home_surface_plan)
    port_map = _port_map(host_body_port_map) if host_body_port_map is not None else None
    if port_map is None:
        status = "blocked_missing_port_map"
    elif real_camera_connected or real_mic_connected or port_map.real_hardware_connected:
        status = "blocked_real_hardware_connection_detected"
    elif external_control_connected or port_map.external_control_connected:
        status = "blocked_external_control_detected"
    elif memory_write_connected or port_map.memory_write_connected:
        status = "blocked_memory_write_detected"
    elif first_output_connected or port_map.first_output_connected:
        status = "blocked_first_output_detected"
    else:
        status = "port_surface_created"
    return QingyinHomePortSurfaceRecord(
        home_port_surface_id=f"qingyin_home_port_surface:{_slug(status)}",
        schema_version=PORT_SURFACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_plan_id=plan.home_surface_plan_id,
        source_host_body_port_map_id=port_map.host_body_port_map_id if port_map else "missing_host_body_port_map",
        port_surface_kind="read_only_port_map_surface" if status == "port_surface_created" else "blocked_port_map_surface",
        port_surface_status=status,
        port_surface_summary=_port_surface_summary(status),
        camera_port_visible=True,
        mic_port_visible=True,
        internal_space_port_visible=True,
        output_surface_port_visible=True,
        trace_history_port_visible=True,
        internal_action_port_visible=True,
        camera_port_label="camera_port_low_level_only",
        mic_port_label="mic_port_low_level_only",
        internal_space_label="qingyin_home_internal_space",
        output_surface_label="bounded_output_surface",
        trace_history_label="trace_history_no_memory_write",
        internal_action_label="internal_action_choice_only_no_runtime",
        real_camera_connected=real_camera_connected or (port_map.real_hardware_connected if port_map else False),
        real_mic_connected=real_mic_connected,
        external_control_connected=external_control_connected or (port_map.external_control_connected if port_map else False),
        memory_write_connected=memory_write_connected or (port_map.memory_write_connected if port_map else False),
        first_output_connected=first_output_connected or (port_map.first_output_connected if port_map else False),
        source_trace_refs=plan.source_trace_refs,
    )


def validate_qingyin_home_port_surface(record: QingyinHomePortSurfaceRecord | dict[str, object]) -> dict[str, object]:
    try:
        item = _port_surface(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.port_surface_status == "port_surface_created":
        if not all((item.camera_port_visible, item.mic_port_visible, item.internal_space_port_visible, item.output_surface_port_visible, item.trace_history_port_visible, item.internal_action_port_visible)):
            errors.append("not_all_ports_visible")
        if item.real_camera_connected or item.real_mic_connected or item.external_control_connected or item.memory_write_connected or item.first_output_connected:
            errors.append("port_surface_has_forbidden_boundary")
    return _validation(not errors, errors, item.home_port_surface_id, item.port_surface_status)


def build_qingyin_home_host_event_surface(
    *,
    home_surface_plan: QingyinHomeInternalSpaceSurfacePlanRecord | dict[str, object],
    host_sensor_event_set: HostBodySensorEventSetRecord | dict[str, object] | None = None,
    host_runtime_bridge_trace: HostBodyRuntimeBridgeTraceRecord | dict[str, object] | None = None,
    event_mappings: tuple[HostBodyEventToRuntimeFrameMappingRecord | dict[str, object], ...] | list[HostBodyEventToRuntimeFrameMappingRecord | dict[str, object]] = tuple(),
    dispatch_links: tuple[HostBodyRuntimeDispatchLinkRecord | dict[str, object], ...] | list[HostBodyRuntimeDispatchLinkRecord | dict[str, object]] = tuple(),
    raw_image_data_included: bool = False,
    raw_audio_data_included: bool = False,
    semantic_label_created: bool = False,
    semantic_vision_created: bool = False,
    speech_recognition_created: bool = False,
    action_selection_influence_created: bool = False,
    external_control_created: bool = False,
    memory_write_performed: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> QingyinHomeHostEventSurfaceRecord:
    plan = _plan(home_surface_plan)
    event_set = _event_set(host_sensor_event_set) if host_sensor_event_set is not None else None
    bridge_trace = _bridge_trace(host_runtime_bridge_trace) if host_runtime_bridge_trace is not None else None
    mappings = tuple(_mapping(item) for item in event_mappings)
    links = tuple(_dispatch_link(item) for item in dispatch_links)
    rows = _host_event_rows(mappings, links)
    if event_set is None and not rows:
        status = "host_event_surface_created_empty"
    elif raw_image_data_included or raw_audio_data_included or semantic_label_created or semantic_vision_created or speech_recognition_created:
        status = "blocked_semantic_interpretation_detected"
    elif action_selection_influence_created:
        status = "blocked_action_selection_influence_detected"
    elif external_control_created or memory_write_performed:
        status = "blocked_external_control_detected"
    elif first_output_created or live_runtime_session_created:
        status = "blocked_first_output_detected"
    else:
        status = "host_event_surface_created"
    camera_count = event_set.camera_event_count if event_set else sum(1 for row in rows if row.get("event_family") == "camera_low_level_event")
    mic_count = event_set.mic_event_count if event_set else sum(1 for row in rows if row.get("event_family") == "mic_low_level_event")
    idle_count = event_set.idle_event_count if event_set else sum(1 for row in rows if row.get("event_family") in {"host_idle_event", "host_status_event"})
    total_count = event_set.total_event_count if event_set else len(rows)
    return QingyinHomeHostEventSurfaceRecord(
        home_host_event_surface_id=f"qingyin_home_host_event_surface:{_slug(status)}",
        schema_version=HOST_EVENT_SURFACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_plan_id=plan.home_surface_plan_id,
        source_host_sensor_event_set_id=event_set.host_sensor_event_set_id if event_set else None,
        source_host_runtime_bridge_trace_id=bridge_trace.host_runtime_bridge_trace_id if bridge_trace else None,
        surface_event_rows=tuple(rows),
        camera_event_count=camera_count,
        mic_event_count=mic_count,
        idle_event_count=idle_count,
        total_event_count=total_count,
        host_event_surface_status=status,
        host_event_surface_summary=_host_event_surface_summary(status, total_count),
        fixture_only_confirmed=True,
        read_only_confirmed=True,
        semantic_label_created=semantic_label_created,
        semantic_vision_created=semantic_vision_created or raw_image_data_included or raw_audio_data_included,
        speech_recognition_created=speech_recognition_created,
        action_selection_influence_created=action_selection_influence_created,
        external_control_created=external_control_created,
        memory_write_performed=memory_write_performed,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=plan.source_trace_refs,
    )


def validate_qingyin_home_host_event_surface(record: QingyinHomeHostEventSurfaceRecord | dict[str, object]) -> dict[str, object]:
    try:
        item = _host_event_surface(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.host_event_surface_status.startswith("host_event_surface_created"):
        forbidden_keys = {"raw_image_data", "raw_audio_data", "semantic_label"}
        for row in item.surface_event_rows:
            if any(key in row for key in forbidden_keys):
                errors.append("row_contains_forbidden_raw_or_semantic_data")
        if item.semantic_label_created or item.semantic_vision_created or item.speech_recognition_created or item.action_selection_influence_created or item.external_control_created or item.memory_write_performed or item.first_output_created or item.live_runtime_session_created:
            errors.append("host_event_surface_has_forbidden_boundary")
    return _validation(not errors, errors, item.home_host_event_surface_id, item.host_event_surface_status)


def build_qingyin_home_runtime_bridge_surface(
    *,
    home_surface_plan: QingyinHomeInternalSpaceSurfacePlanRecord | dict[str, object],
    host_runtime_bridge_trace: HostBodyRuntimeBridgeTraceRecord | dict[str, object] | None,
    event_mappings: tuple[HostBodyEventToRuntimeFrameMappingRecord | dict[str, object], ...] | list[HostBodyEventToRuntimeFrameMappingRecord | dict[str, object]] = tuple(),
    dispatch_links: tuple[HostBodyRuntimeDispatchLinkRecord | dict[str, object], ...] | list[HostBodyRuntimeDispatchLinkRecord | dict[str, object]] = tuple(),
    live_runtime_session_created: bool = False,
    live_engine_invocation_created: bool = False,
    dynamic_scheduling_created: bool = False,
    external_execution_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    first_output_created: bool = False,
    production_behavior_created: bool = False,
) -> QingyinHomeRuntimeBridgeSurfaceRecord:
    plan = _plan(home_surface_plan)
    trace = _bridge_trace(host_runtime_bridge_trace) if host_runtime_bridge_trace is not None else None
    mappings = tuple(_mapping(item) for item in event_mappings)
    links = tuple(_dispatch_link(item) for item in dispatch_links)
    rows = _runtime_bridge_rows(mappings, links)
    if trace is None:
        status = "blocked_missing_runtime_bridge_trace"
    elif live_runtime_session_created or trace.live_runtime_session_created:
        status = "blocked_live_runtime_detected"
    elif live_engine_invocation_created or trace.live_engine_invocation_created:
        status = "blocked_live_engine_invocation_detected"
    elif dynamic_scheduling_created:
        status = "blocked_dynamic_scheduling_detected"
    elif memory_write_performed or automatic_learning_approval_created or trace.memory_layer_write_performed:
        status = "blocked_memory_write_detected"
    elif first_output_created or trace.first_output_created:
        status = "blocked_first_output_detected"
    elif production_behavior_created or trace.production_behavior_created:
        status = "blocked_first_output_detected"
    elif any(link.dispatch_link_status == "dispatch_link_deferred_missing_dispatch_adapter" for link in links) or trace.bridge_trace_status.endswith("deferred_dispatch"):
        status = "runtime_bridge_surface_created_with_deferred_dispatch"
    else:
        status = "runtime_bridge_surface_created"
    return QingyinHomeRuntimeBridgeSurfaceRecord(
        home_runtime_bridge_surface_id=f"qingyin_home_runtime_bridge_surface:{_slug(status)}",
        schema_version=RUNTIME_BRIDGE_SURFACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_plan_id=plan.home_surface_plan_id,
        source_host_runtime_bridge_trace_id=trace.host_runtime_bridge_trace_id if trace else "missing_runtime_bridge_trace",
        bridge_surface_rows=tuple(rows),
        bridged_event_count=trace.bridged_event_count if trace else 0,
        sense_eventframe_count=sum(1 for item in mappings if item.target_event_family == "sense_event"),
        runtime_eventframe_count=sum(1 for item in mappings if item.target_event_family == "runtime_event"),
        state_eventframe_count=sum(1 for item in mappings if item.target_event_family == "state_event"),
        deferred_dispatch_count=sum(1 for item in links if item.dispatch_link_status == "dispatch_link_deferred_missing_dispatch_adapter"),
        runtime_bridge_surface_status=status,
        runtime_bridge_surface_summary=_runtime_bridge_surface_summary(status),
        runtime_eventframe_bridge_visible=True,
        dispatch_adapter_status_visible=True,
        return_payload_status_visible=True,
        live_runtime_session_created=live_runtime_session_created,
        live_engine_invocation_created=live_engine_invocation_created,
        dynamic_scheduling_created=dynamic_scheduling_created,
        external_execution_created=external_execution_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        production_behavior_created=production_behavior_created,
        source_trace_refs=plan.source_trace_refs,
    )


def validate_qingyin_home_runtime_bridge_surface(record: QingyinHomeRuntimeBridgeSurfaceRecord | dict[str, object]) -> dict[str, object]:
    try:
        item = _runtime_bridge_surface(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.runtime_bridge_surface_status.startswith("runtime_bridge_surface_created"):
        if not (item.runtime_eventframe_bridge_visible and item.dispatch_adapter_status_visible and item.return_payload_status_visible):
            errors.append("runtime_bridge_status_not_visible")
        if item.live_runtime_session_created or item.live_engine_invocation_created or item.dynamic_scheduling_created or item.memory_write_performed or item.automatic_learning_approval_created or item.first_output_created or item.production_behavior_created:
            errors.append("runtime_bridge_surface_has_forbidden_boundary")
    return _validation(not errors, errors, item.home_runtime_bridge_surface_id, item.runtime_bridge_surface_status)


def build_qingyin_home_status_light(
    *,
    home_surface_plan: QingyinHomeInternalSpaceSurfacePlanRecord | dict[str, object],
    status_light_kind: str,
    status_light_state: str = "on",
    status_light_label: str | None = None,
    status_light_reason: str = "read_only_status",
    source_event_refs: tuple[str, ...] = tuple(),
    first_output_created: bool = False,
    external_message_created: bool = False,
    sound_output_played: bool = False,
    screen_output_mutated: bool = False,
    unity_runtime_mutated: bool = False,
) -> QingyinHomeStatusLightRecord:
    plan = _plan(home_surface_plan)
    if first_output_created:
        status = "blocked_first_output_detected"
    elif unity_runtime_mutated:
        status = "blocked_unity_runtime_mutation_detected"
    elif external_message_created or sound_output_played or screen_output_mutated:
        status = "blocked_output_side_effect_detected"
    else:
        status = "status_light_recorded"
    return QingyinHomeStatusLightRecord(
        home_status_light_id=f"qingyin_home_status_light:{_slug(status_light_kind)}:{_slug(status)}",
        schema_version=STATUS_LIGHT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_plan_id=plan.home_surface_plan_id,
        status_light_kind=status_light_kind,
        status_light_label=status_light_label or status_light_kind,
        status_light_state="blocked" if status.startswith("blocked") else status_light_state,
        status_light_reason=status_light_reason,
        status_light_summary=_status_light_summary(status, status_light_kind),
        source_event_refs=source_event_refs,
        status_light_surface_status=status,
        first_output_created=first_output_created,
        external_message_created=external_message_created,
        sound_output_played=sound_output_played,
        screen_output_mutated=screen_output_mutated,
        unity_runtime_mutated=unity_runtime_mutated,
        source_trace_refs=plan.source_trace_refs,
    )


def validate_qingyin_home_status_light(record: QingyinHomeStatusLightRecord | dict[str, object]) -> dict[str, object]:
    try:
        item = _status_light(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.status_light_surface_status == "status_light_recorded":
        if item.first_output_created or item.external_message_created or item.sound_output_played or item.screen_output_mutated or item.unity_runtime_mutated:
            errors.append("status_light_has_output_side_effect")
    return _validation(not errors, errors, item.home_status_light_id, item.status_light_surface_status)


def build_qingyin_home_teacher_observed_surface(
    *,
    home_surface_plan: QingyinHomeInternalSpaceSurfacePlanRecord | dict[str, object],
    host_event_surface: QingyinHomeHostEventSurfaceRecord | dict[str, object] | None = None,
    runtime_bridge_surface: QingyinHomeRuntimeBridgeSurfaceRecord | dict[str, object] | None = None,
    status_lights: tuple[QingyinHomeStatusLightRecord | dict[str, object], ...] | list[QingyinHomeStatusLightRecord | dict[str, object]] = tuple(),
    approval_created: bool = False,
    learning_approval_created: bool = False,
    memory_write_approval_created: bool = False,
    first_output_created: bool = False,
    external_control_created: bool = False,
) -> QingyinHomeTeacherObservedSurfaceRecord:
    plan = _plan(home_surface_plan)
    host_surface = _host_event_surface(host_event_surface) if host_event_surface is not None else None
    bridge_surface = _runtime_bridge_surface(runtime_bridge_surface) if runtime_bridge_surface is not None else None
    lights = tuple(_status_light(item) for item in status_lights)
    if approval_created:
        status = "blocked_approval_created"
    elif learning_approval_created:
        status = "blocked_learning_approval_created"
    elif memory_write_approval_created:
        status = "blocked_memory_write_approval_created"
    elif first_output_created:
        status = "blocked_first_output_detected"
    elif external_control_created:
        status = "blocked_external_control_detected"
    elif host_surface is None and bridge_surface is None and not lights:
        status = "teacher_observed_surface_created_empty"
    else:
        status = "teacher_observed_surface_created"
    return QingyinHomeTeacherObservedSurfaceRecord(
        home_teacher_observed_surface_id=f"qingyin_home_teacher_surface:{_slug(status)}",
        schema_version=TEACHER_SURFACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_plan_id=plan.home_surface_plan_id,
        teacher_observed_sections=TEACHER_OBSERVED_SECTIONS,
        observed_host_event_count=host_surface.total_event_count if host_surface else 0,
        observed_runtime_bridge_count=bridge_surface.bridged_event_count if bridge_surface else 0,
        observed_status_light_count=len(lights),
        teacher_review_prompt_created=False,
        teacher_action_required=False,
        teacher_surface_status=status,
        teacher_surface_summary=_teacher_surface_summary(status),
        approval_created=approval_created,
        learning_approval_created=learning_approval_created,
        memory_write_approval_created=memory_write_approval_created,
        first_output_created=first_output_created,
        external_control_created=external_control_created,
        source_trace_refs=plan.source_trace_refs,
    )


def validate_qingyin_home_teacher_observed_surface(record: QingyinHomeTeacherObservedSurfaceRecord | dict[str, object]) -> dict[str, object]:
    try:
        item = _teacher_surface(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.teacher_surface_status.startswith("teacher_observed_surface_created"):
        if item.approval_created or item.learning_approval_created or item.memory_write_approval_created or item.first_output_created or item.external_control_created:
            errors.append("teacher_surface_has_forbidden_boundary")
    return _validation(not errors, errors, item.home_teacher_observed_surface_id, item.teacher_surface_status)


def build_qingyin_home_internal_space_render(
    *,
    home_surface_plan: QingyinHomeInternalSpaceSurfacePlanRecord | dict[str, object],
    port_surface: QingyinHomePortSurfaceRecord | dict[str, object] | None = None,
    host_event_surface: QingyinHomeHostEventSurfaceRecord | dict[str, object] | None = None,
    runtime_bridge_surface: QingyinHomeRuntimeBridgeSurfaceRecord | dict[str, object] | None = None,
    teacher_surface: QingyinHomeTeacherObservedSurfaceRecord | dict[str, object] | None = None,
    status_lights: tuple[QingyinHomeStatusLightRecord | dict[str, object], ...] | list[QingyinHomeStatusLightRecord | dict[str, object]] = tuple(),
    render_kind: str = "text_summary_render",
    unity_runtime_started: bool = False,
    unity_scene_mutated: bool = False,
    avatar_control_created: bool = False,
    game_character_control_created: bool = False,
    file_written: bool = False,
    network_output_created: bool = False,
    first_output_created: bool = False,
    production_behavior_created: bool = False,
) -> QingyinHomeInternalSpaceRenderRecord:
    plan = _plan(home_surface_plan)
    port = _port_surface(port_surface) if port_surface is not None else None
    host_surface = _host_event_surface(host_event_surface) if host_event_surface is not None else None
    bridge_surface = _runtime_bridge_surface(runtime_bridge_surface) if runtime_bridge_surface is not None else None
    teacher = _teacher_surface(teacher_surface) if teacher_surface is not None else None
    lights = tuple(_status_light(item) for item in status_lights)
    if unity_runtime_started:
        status = "blocked_unity_runtime_started"
    elif unity_scene_mutated:
        status = "blocked_unity_scene_mutation"
    elif avatar_control_created or game_character_control_created:
        status = "blocked_avatar_control"
    elif file_written:
        status = "blocked_file_write"
    elif network_output_created:
        status = "blocked_network_output"
    elif first_output_created:
        status = "blocked_first_output"
    elif production_behavior_created:
        status = "blocked_production_behavior"
    elif port is None and host_surface is None and bridge_surface is None and teacher is None and not lights:
        status = "home_internal_space_render_created_empty"
    else:
        status = "home_internal_space_render_created"
    payload = {
        "surface_name": plan.surface_name,
        "port_surface_status": port.port_surface_status if port else None,
        "host_event_surface_status": host_surface.host_event_surface_status if host_surface else None,
        "runtime_bridge_surface_status": bridge_surface.runtime_bridge_surface_status if bridge_surface else None,
        "teacher_surface_status": teacher.teacher_surface_status if teacher else None,
        "status_light_count": len(lights),
    }
    return QingyinHomeInternalSpaceRenderRecord(
        home_internal_space_render_id=f"qingyin_home_render:{_slug(render_kind)}:{_slug(status)}",
        schema_version=RENDER_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_plan_id=plan.home_surface_plan_id,
        source_port_surface_id=port.home_port_surface_id if port else None,
        source_host_event_surface_id=host_surface.home_host_event_surface_id if host_surface else None,
        source_runtime_bridge_surface_id=bridge_surface.home_runtime_bridge_surface_id if bridge_surface else None,
        source_teacher_surface_id=teacher.home_teacher_observed_surface_id if teacher else None,
        status_light_ids=tuple(light.home_status_light_id for light in lights),
        render_kind="blocked_render" if status.startswith("blocked") else render_kind,
        render_payload=payload,
        render_text=render_qingyin_home_surface_summary_text_from_parts(payload),
        render_status=status,
        render_summary=_render_summary(status),
        read_only_render=True,
        unity_runtime_started=unity_runtime_started,
        unity_scene_mutated=unity_scene_mutated,
        avatar_control_created=avatar_control_created,
        game_character_control_created=game_character_control_created,
        file_written=file_written,
        network_output_created=network_output_created,
        first_output_created=first_output_created,
        production_behavior_created=production_behavior_created,
        source_trace_refs=plan.source_trace_refs,
    )


def validate_qingyin_home_internal_space_render(record: QingyinHomeInternalSpaceRenderRecord | dict[str, object]) -> dict[str, object]:
    try:
        item = _render(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.render_status.startswith("home_internal_space_render_created"):
        if not item.read_only_render:
            errors.append("read_only_render_false")
        if item.unity_runtime_started or item.unity_scene_mutated or item.avatar_control_created or item.game_character_control_created or item.file_written or item.network_output_created or item.first_output_created or item.production_behavior_created:
            errors.append("render_has_forbidden_boundary")
    return _validation(not errors, errors, item.home_internal_space_render_id, item.render_status)


def build_qingyin_home_internal_space_surface_audit(
    *,
    home_surface_plan: QingyinHomeInternalSpaceSurfacePlanRecord | dict[str, object] | None,
    port_surface: QingyinHomePortSurfaceRecord | dict[str, object] | None = None,
    host_event_surface: QingyinHomeHostEventSurfaceRecord | dict[str, object] | None = None,
    runtime_bridge_surface: QingyinHomeRuntimeBridgeSurfaceRecord | dict[str, object] | None = None,
    status_lights: tuple[QingyinHomeStatusLightRecord | dict[str, object], ...] | list[QingyinHomeStatusLightRecord | dict[str, object]] = tuple(),
    teacher_surface: QingyinHomeTeacherObservedSurfaceRecord | dict[str, object] | None = None,
    render: QingyinHomeInternalSpaceRenderRecord | dict[str, object] | None = None,
    force_live_runtime_session: bool = False,
    force_autonomous_scheduler: bool = False,
    force_open_ended_loop: bool = False,
    force_thought_engine_behavior: bool = False,
) -> QingyinHomeInternalSpaceSurfaceAudit:
    plan = _plan(home_surface_plan) if home_surface_plan is not None else None
    port = _port_surface(port_surface) if port_surface is not None else None
    host_surface = _host_event_surface(host_event_surface) if host_event_surface is not None else None
    bridge_surface = _runtime_bridge_surface(runtime_bridge_surface) if runtime_bridge_surface is not None else None
    lights = tuple(_status_light(item) for item in status_lights)
    teacher = _teacher_surface(teacher_surface) if teacher_surface is not None else None
    render_record = _render(render) if render is not None else None
    reasons = _audit_reasons(
        plan=plan,
        port=port,
        host_surface=host_surface,
        bridge_surface=bridge_surface,
        lights=lights,
        teacher=teacher,
        render=render_record,
        force_live_runtime_session=force_live_runtime_session,
        force_autonomous_scheduler=force_autonomous_scheduler,
        force_open_ended_loop=force_open_ended_loop,
        force_thought_engine_behavior=force_thought_engine_behavior,
    )
    status = _audit_status(reasons, host_surface, bridge_surface)
    return QingyinHomeInternalSpaceSurfaceAudit(
        home_surface_audit_id=f"qingyin_home_surface_audit:{_slug(status)}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_plan_id=plan.home_surface_plan_id if plan else None,
        source_port_surface_id=port.home_port_surface_id if port else None,
        source_host_event_surface_id=host_surface.home_host_event_surface_id if host_surface else None,
        source_runtime_bridge_surface_id=bridge_surface.home_runtime_bridge_surface_id if bridge_surface else None,
        source_teacher_surface_id=teacher.home_teacher_observed_surface_id if teacher else None,
        source_render_id=render_record.home_internal_space_render_id if render_record else None,
        surface_plan_valid=plan is not None and plan.surface_plan_status == "surface_plan_created",
        port_surface_valid=port is not None and port.port_surface_status == "port_surface_created",
        host_event_surface_valid=host_surface is not None and host_surface.host_event_surface_status.startswith("host_event_surface_created"),
        runtime_bridge_surface_valid=bridge_surface is not None and bridge_surface.runtime_bridge_surface_status.startswith("runtime_bridge_surface_created"),
        status_lights_valid=all(light.status_light_surface_status == "status_light_recorded" for light in lights),
        teacher_surface_valid=teacher is not None and teacher.teacher_surface_status.startswith("teacher_observed_surface_created"),
        render_valid=render_record is not None and render_record.render_status.startswith("home_internal_space_render_created"),
        qingyin_home_internal_space_confirmed="invalid_plan" not in reasons,
        avatar_projection_only_confirmed="avatar_control" not in reasons,
        read_only_surface_confirmed="not_read_only" not in reasons,
        teacher_observed_only_confirmed="teacher_approval" not in reasons,
        no_unity_runtime_connection="unity_runtime" not in reasons,
        no_unity_scene_mutation="unity_scene" not in reasons,
        no_avatar_control="avatar_control" not in reasons,
        no_game_character_control="avatar_control" not in reasons,
        no_real_camera_access="real_sensor" not in reasons,
        no_real_mic_access="real_sensor" not in reasons,
        no_semantic_vision="semantic" not in reasons,
        no_speech_recognition="semantic" not in reasons,
        no_action_selection_influence="action_selection" not in reasons,
        no_external_control="external_control" not in reasons,
        no_os_control=True,
        no_mouse_control=True,
        no_keyboard_control=True,
        no_browser_control=True,
        no_file_operation="file_write" not in reasons,
        no_network_execution="network_output" not in reasons,
        no_shell_execution=True,
        no_memory_layer_write="memory_write" not in reasons,
        no_automatic_learning_approval="automatic_learning_approval" not in reasons,
        no_teacher_approval_created="teacher_approval" not in reasons,
        no_first_output="first_output" not in reasons,
        no_live_runtime_session="live_runtime" not in reasons,
        no_live_engine_invocation="live_engine" not in reasons,
        no_autonomous_scheduler="autonomous_scheduler" not in reasons,
        no_open_ended_loop="open_ended_loop" not in reasons,
        no_thought_engine_behavior="thought_engine_behavior" not in reasons,
        no_production_behavior="production_behavior" not in reasons,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(reasons),
        source_trace_refs=plan.source_trace_refs if plan else tuple(),
    )


def validate_qingyin_home_internal_space_surface_audit(record: QingyinHomeInternalSpaceSurfaceAudit | dict[str, object]) -> dict[str, object]:
    try:
        item = _audit(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.audit_status.startswith("passed_"):
        required = (
            item.surface_plan_valid,
            item.port_surface_valid,
            item.host_event_surface_valid,
            item.runtime_bridge_surface_valid,
            item.status_lights_valid,
            item.teacher_surface_valid,
            item.render_valid,
            item.qingyin_home_internal_space_confirmed,
            item.avatar_projection_only_confirmed,
            item.read_only_surface_confirmed,
            item.teacher_observed_only_confirmed,
            item.no_unity_runtime_connection,
            item.no_avatar_control,
            item.no_real_camera_access,
            item.no_real_mic_access,
            item.no_semantic_vision,
            item.no_speech_recognition,
            item.no_action_selection_influence,
            item.no_external_control,
            item.no_memory_layer_write,
            item.no_teacher_approval_created,
            item.no_first_output,
            item.no_live_runtime_session,
            item.no_production_behavior,
        )
        if not all(required):
            errors.append("passed_audit_has_failed_boundary")
    return _validation(not errors, errors, item.home_surface_audit_id, item.audit_status)


def build_qingyin_home_internal_space_surface_readiness(
    home_surface_audit: QingyinHomeInternalSpaceSurfaceAudit | dict[str, object],
) -> QingyinHomeInternalSpaceSurfaceReadinessRecord:
    audit = _audit(home_surface_audit)
    passed = audit.audit_status.startswith("passed_")
    if passed:
        status = "ready_for_host_body_trace_history_lane_only"
    elif audit.source_home_surface_plan_id is None:
        status = "not_ready_missing_home_surface_audit"
    elif audit.audit_status.endswith("detected") or audit.audit_status.startswith("blocked_"):
        status = "blocked_forbidden_authority_detected"
    else:
        status = "not_ready_boundary_failure"
    return QingyinHomeInternalSpaceSurfaceReadinessRecord(
        home_surface_readiness_id=f"qingyin_home_surface_readiness:{audit.home_surface_audit_id}",
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_audit_id=audit.home_surface_audit_id,
        current_verified_capability=SAFE_CLAIM,
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason="Create a read-only trace history lane for Host Body events and Home surface renders.",
        ready_for_host_body_trace_history_lane=passed,
        ready_for_internal_action_choice_only=passed,
        ready_for_teacher_observed_host_body_cli=passed,
        ready_for_unity_runtime_connection=False,
        ready_for_avatar_control=False,
        ready_for_real_camera_connection=False,
        ready_for_real_mic_connection=False,
        ready_for_semantic_vision=False,
        ready_for_speech_recognition=False,
        ready_for_external_control=False,
        ready_for_first_output=False,
        ready_for_live_runtime_session=False,
        ready_for_memory_layer_write=False,
        ready_for_autonomous_scheduler=False,
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=audit.source_trace_refs,
    )


def validate_qingyin_home_internal_space_surface_readiness(record: QingyinHomeInternalSpaceSurfaceReadinessRecord | dict[str, object]) -> dict[str, object]:
    try:
        item = _readiness(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    for flag in (
        "ready_for_unity_runtime_connection",
        "ready_for_avatar_control",
        "ready_for_real_camera_connection",
        "ready_for_real_mic_connection",
        "ready_for_semantic_vision",
        "ready_for_speech_recognition",
        "ready_for_external_control",
        "ready_for_first_output",
        "ready_for_live_runtime_session",
        "ready_for_memory_layer_write",
        "ready_for_autonomous_scheduler",
    ):
        if getattr(item, flag):
            errors.append(f"{flag}_true")
    return _validation(not errors, errors, item.home_surface_readiness_id, item.readiness_status)


def build_demo_qingyin_home_internal_space_surface() -> dict[str, object]:
    return _build_home_surface_bundle()


def build_demo_empty_qingyin_home_surface() -> dict[str, object]:
    return _build_home_surface_bundle(empty_events=True)


def build_demo_deferred_dispatch_qingyin_home_surface() -> dict[str, object]:
    return _build_home_surface_bundle(deferred_dispatch=True)


def build_demo_blocked_avatar_body_claim_home_surface() -> dict[str, object]:
    return _build_home_surface_bundle(
        plan_kwargs={"avatar_control_allowed": True},
        render_kwargs={"avatar_control_created": True, "game_character_control_created": True},
    )


def build_demo_blocked_unity_runtime_connection_home_surface() -> dict[str, object]:
    return _build_home_surface_bundle(
        plan_kwargs={"unity_runtime_connection_allowed": True},
        render_kwargs={"unity_runtime_started": True, "unity_scene_mutated": True},
    )


def build_demo_blocked_teacher_approval_home_surface() -> dict[str, object]:
    return _build_home_surface_bundle(
        teacher_kwargs={"approval_created": True, "learning_approval_created": True},
    )


def build_demo_blocked_first_output_home_surface() -> dict[str, object]:
    return _build_home_surface_bundle(
        render_kwargs={"first_output_created": True},
    )


def build_demo_blocked_external_control_home_surface() -> dict[str, object]:
    return _build_home_surface_bundle(
        teacher_kwargs={"external_control_created": True},
    )


def render_qingyin_home_surface_summary_text(
    audit: QingyinHomeInternalSpaceSurfaceAudit | dict[str, object],
    readiness: QingyinHomeInternalSpaceSurfaceReadinessRecord | dict[str, object] | None = None,
) -> str:
    audit_item = _audit(audit)
    readiness_item = _readiness(readiness) if readiness is not None else None
    parts = [
        f"qingyin_home_surface_audit={audit_item.audit_status}",
        f"read_only={audit_item.read_only_surface_confirmed}",
        f"teacher_observed={audit_item.teacher_observed_only_confirmed}",
    ]
    if readiness_item is not None:
        parts.append(f"readiness={readiness_item.readiness_status}")
    return " ".join(parts)


def render_qingyin_home_status_light_table(
    status_lights: tuple[QingyinHomeStatusLightRecord | dict[str, object], ...] | list[QingyinHomeStatusLightRecord | dict[str, object]],
) -> str:
    rows = ["light | state | status"]
    for light in tuple(_status_light(item) for item in status_lights):
        rows.append(f"{light.status_light_kind} | {light.status_light_state} | {light.status_light_surface_status}")
    return "\n".join(rows)


def render_qingyin_home_event_surface_table(
    host_event_surface: QingyinHomeHostEventSurfaceRecord | dict[str, object],
) -> str:
    surface = _host_event_surface(host_event_surface)
    rows = ["event | family | bridge | engine"]
    for row in surface.surface_event_rows:
        rows.append(
            f"{row.get('event_type')} | {row.get('event_family')} | "
            f"{row.get('bridge_status')} | {row.get('target_engine_lane')}"
        )
    return "\n".join(rows)


def render_qingyin_home_surface_summary_text_from_parts(payload: dict[str, Any]) -> str:
    return (
        f"qingyin_home render ports={payload.get('port_surface_status')} "
        f"events={payload.get('host_event_surface_status')} "
        f"bridge={payload.get('runtime_bridge_surface_status')} "
        f"lights={payload.get('status_light_count')}"
    )


def _build_home_surface_bundle(
    *,
    empty_events: bool = False,
    deferred_dispatch: bool = False,
    plan_kwargs: dict[str, object] | None = None,
    port_kwargs: dict[str, object] | None = None,
    event_kwargs: dict[str, object] | None = None,
    bridge_surface_kwargs: dict[str, object] | None = None,
    light_kwargs: dict[str, object] | None = None,
    teacher_kwargs: dict[str, object] | None = None,
    render_kwargs: dict[str, object] | None = None,
) -> dict[str, object]:
    port_payload = build_demo_qingyin_host_body_port_map()
    runtime_payload = (
        build_demo_deferred_dispatch_host_body_runtime_bridge()
        if deferred_dispatch
        else build_demo_mixed_host_body_runtime_bridge()
    )
    sensor_payload = build_demo_mixed_host_sensor_event_set()
    identity = HostBodyIdentityRecord.from_dict(port_payload["host_body_identity"])
    port_map = HostBodyPortMapRecord.from_dict(port_payload["host_body_port_map"])
    internal_space = HostInternalSpacePortRecord.from_dict(port_payload["host_internal_space_port"])
    bridge_audit = HostBodyRuntimeBridgeAudit.from_dict(runtime_payload["host_body_runtime_bridge_audit"])
    bridge_trace = HostBodyRuntimeBridgeTraceRecord.from_dict(runtime_payload["host_body_runtime_bridge_trace"])
    event_set = HostBodySensorEventSetRecord.from_dict(sensor_payload["host_body_sensor_event_set"])
    mappings = tuple(
        HostBodyEventToRuntimeFrameMappingRecord.from_dict(item)
        for item in runtime_payload["host_body_event_runtime_mappings"]
    )
    links = tuple(
        HostBodyRuntimeDispatchLinkRecord.from_dict(item)
        for item in runtime_payload["host_body_runtime_dispatch_links"]
    )
    plan = build_qingyin_home_internal_space_surface_plan(
        host_body_identity=identity,
        host_body_port_map=port_map,
        internal_space_port=internal_space,
        host_runtime_bridge_audit=bridge_audit,
        **(plan_kwargs or {}),
    )
    port_surface = build_qingyin_home_port_surface(
        home_surface_plan=plan,
        host_body_port_map=port_map,
        **(port_kwargs or {}),
    )
    host_event_surface = build_qingyin_home_host_event_surface(
        home_surface_plan=plan,
        host_sensor_event_set=None if empty_events else event_set,
        host_runtime_bridge_trace=None if empty_events else bridge_trace,
        event_mappings=tuple() if empty_events else mappings,
        dispatch_links=tuple() if empty_events else links,
        **(event_kwargs or {}),
    )
    runtime_bridge_surface = build_qingyin_home_runtime_bridge_surface(
        home_surface_plan=plan,
        host_runtime_bridge_trace=bridge_trace,
        event_mappings=mappings,
        dispatch_links=links,
        **(bridge_surface_kwargs or {}),
    )
    status_lights = (
        build_qingyin_home_status_light(home_surface_plan=plan, status_light_kind="host_body_ready"),
        build_qingyin_home_status_light(home_surface_plan=plan, status_light_kind="sensor_event_seen"),
        build_qingyin_home_status_light(home_surface_plan=plan, status_light_kind="runtime_bridge_ready"),
        build_qingyin_home_status_light(home_surface_plan=plan, status_light_kind="teacher_review_pending", status_light_state="dim"),
        build_qingyin_home_status_light(home_surface_plan=plan, status_light_kind="idle", status_light_state="dim", **(light_kwargs or {})),
    )
    teacher_surface = build_qingyin_home_teacher_observed_surface(
        home_surface_plan=plan,
        host_event_surface=host_event_surface,
        runtime_bridge_surface=runtime_bridge_surface,
        status_lights=status_lights,
        **(teacher_kwargs or {}),
    )
    render = build_qingyin_home_internal_space_render(
        home_surface_plan=plan,
        port_surface=port_surface,
        host_event_surface=host_event_surface,
        runtime_bridge_surface=runtime_bridge_surface,
        teacher_surface=teacher_surface,
        status_lights=status_lights,
        **(render_kwargs or {}),
    )
    audit = build_qingyin_home_internal_space_surface_audit(
        home_surface_plan=plan,
        port_surface=port_surface,
        host_event_surface=host_event_surface,
        runtime_bridge_surface=runtime_bridge_surface,
        status_lights=status_lights,
        teacher_surface=teacher_surface,
        render=render,
    )
    readiness = build_qingyin_home_internal_space_surface_readiness(audit)
    return {
        "home_surface_plan": plan.to_dict(),
        "home_port_surface": port_surface.to_dict(),
        "home_host_event_surface": host_event_surface.to_dict(),
        "home_runtime_bridge_surface": runtime_bridge_surface.to_dict(),
        "home_status_lights": [item.to_dict() for item in status_lights],
        "home_teacher_observed_surface": teacher_surface.to_dict(),
        "home_internal_space_render": render.to_dict(),
        "home_internal_space_surface_audit": audit.to_dict(),
        "home_internal_space_surface_readiness": readiness.to_dict(),
        "rendered_qingyin_home_surface_summary": render_qingyin_home_surface_summary_text(audit, readiness),
        "rendered_qingyin_home_status_light_table": render_qingyin_home_status_light_table(status_lights),
        "rendered_qingyin_home_event_surface_table": render_qingyin_home_event_surface_table(host_event_surface),
    }


def _plan_status(
    *,
    port_map: HostBodyPortMapRecord | None,
    internal_space: HostInternalSpacePortRecord | None,
    bridge_audit: HostBodyRuntimeBridgeAudit | None,
    unity_runtime_connection_allowed: bool,
    unity_scene_mutation_allowed: bool,
    avatar_control_allowed: bool,
    game_character_control_allowed: bool,
    real_camera_access_allowed: bool,
    real_mic_access_allowed: bool,
    semantic_interpretation_allowed: bool,
    speech_recognition_allowed: bool,
    action_selection_allowed: bool,
    external_control_allowed: bool,
    memory_write_allowed: bool,
    automatic_learning_approval_allowed: bool,
    first_output_allowed: bool,
    live_runtime_session_allowed: bool,
) -> str:
    if port_map is None or internal_space is None:
        return "blocked_missing_host_body_port_map"
    if bridge_audit is None:
        return "blocked_missing_runtime_bridge_audit"
    if unity_runtime_connection_allowed or unity_scene_mutation_allowed:
        return "blocked_unity_runtime_connection_requested"
    if avatar_control_allowed or game_character_control_allowed:
        return "blocked_avatar_control_requested"
    if external_control_allowed:
        return "blocked_external_control_requested"
    if first_output_allowed:
        return "blocked_first_output_requested"
    if real_camera_access_allowed or real_mic_access_allowed or semantic_interpretation_allowed or speech_recognition_allowed or action_selection_allowed or memory_write_allowed or automatic_learning_approval_allowed or live_runtime_session_allowed:
        return "blocked_forbidden_authority_detected"
    return "surface_plan_created"


def _audit_reasons(
    *,
    plan: QingyinHomeInternalSpaceSurfacePlanRecord | None,
    port: QingyinHomePortSurfaceRecord | None,
    host_surface: QingyinHomeHostEventSurfaceRecord | None,
    bridge_surface: QingyinHomeRuntimeBridgeSurfaceRecord | None,
    lights: tuple[QingyinHomeStatusLightRecord, ...],
    teacher: QingyinHomeTeacherObservedSurfaceRecord | None,
    render: QingyinHomeInternalSpaceRenderRecord | None,
    force_live_runtime_session: bool,
    force_autonomous_scheduler: bool,
    force_open_ended_loop: bool,
    force_thought_engine_behavior: bool,
) -> list[str]:
    reasons: list[str] = []
    if plan is None or plan.surface_plan_status != "surface_plan_created":
        reasons.append("missing_plan" if plan is None else "invalid_plan")
    elif _plan_has_forbidden_boundary(plan):
        reasons.append("invalid_plan")
    if port is None or port.port_surface_status != "port_surface_created":
        reasons.append("invalid_port_surface")
        if port is not None:
            if port.real_camera_connected or port.real_mic_connected:
                reasons.append("real_sensor")
            if port.external_control_connected:
                reasons.append("external_control")
            if port.memory_write_connected:
                reasons.append("memory_write")
            if port.first_output_connected:
                reasons.append("first_output")
    if host_surface is None or not host_surface.host_event_surface_status.startswith("host_event_surface_created"):
        reasons.append("invalid_host_event_surface")
    if host_surface is not None:
        if host_surface.semantic_label_created or host_surface.semantic_vision_created or host_surface.speech_recognition_created:
            reasons.append("semantic")
        if host_surface.action_selection_influence_created:
            reasons.append("action_selection")
        if host_surface.external_control_created:
            reasons.append("external_control")
        if host_surface.memory_write_performed:
            reasons.append("memory_write")
        if host_surface.first_output_created:
            reasons.append("first_output")
        if host_surface.live_runtime_session_created:
            reasons.append("live_runtime")
    if bridge_surface is None or not bridge_surface.runtime_bridge_surface_status.startswith("runtime_bridge_surface_created"):
        reasons.append("invalid_runtime_bridge_surface")
    if bridge_surface is not None:
        if bridge_surface.live_runtime_session_created:
            reasons.append("live_runtime")
        if bridge_surface.live_engine_invocation_created:
            reasons.append("live_engine")
        if bridge_surface.dynamic_scheduling_created:
            reasons.append("dynamic_scheduling")
        if bridge_surface.external_execution_created:
            reasons.append("external_control")
        if bridge_surface.memory_write_performed or bridge_surface.automatic_learning_approval_created:
            reasons.append("memory_write")
        if bridge_surface.first_output_created:
            reasons.append("first_output")
        if bridge_surface.production_behavior_created:
            reasons.append("production_behavior")
    if any(light.status_light_surface_status != "status_light_recorded" for light in lights):
        for light in lights:
            if light.first_output_created:
                reasons.append("first_output")
            if light.external_message_created or light.sound_output_played or light.screen_output_mutated:
                reasons.append("external_control")
            if light.unity_runtime_mutated:
                reasons.append("unity_runtime")
    if teacher is None or not teacher.teacher_surface_status.startswith("teacher_observed_surface_created"):
        reasons.append("invalid_teacher_surface")
    if teacher is not None:
        if teacher.approval_created or teacher.learning_approval_created or teacher.memory_write_approval_created:
            reasons.append("teacher_approval")
        if teacher.learning_approval_created:
            reasons.append("automatic_learning_approval")
        if teacher.memory_write_approval_created:
            reasons.append("memory_write")
        if teacher.first_output_created:
            reasons.append("first_output")
        if teacher.external_control_created:
            reasons.append("external_control")
    if render is None or not render.render_status.startswith("home_internal_space_render_created"):
        reasons.append("invalid_render")
    if render is not None:
        if render.unity_runtime_started:
            reasons.append("unity_runtime")
        if render.unity_scene_mutated:
            reasons.append("unity_scene")
        if render.avatar_control_created or render.game_character_control_created:
            reasons.append("avatar_control")
        if render.file_written:
            reasons.append("file_write")
        if render.network_output_created:
            reasons.append("network_output")
        if render.first_output_created:
            reasons.append("first_output")
        if render.production_behavior_created:
            reasons.append("production_behavior")
    if force_live_runtime_session:
        reasons.append("live_runtime")
    if force_autonomous_scheduler:
        reasons.append("autonomous_scheduler")
    if force_open_ended_loop:
        reasons.append("open_ended_loop")
    if force_thought_engine_behavior:
        reasons.append("thought_engine_behavior")
    return list(dict.fromkeys(reasons))


def _audit_status(
    reasons: list[str],
    host_surface: QingyinHomeHostEventSurfaceRecord | None,
    bridge_surface: QingyinHomeRuntimeBridgeSurfaceRecord | None,
) -> str:
    priority = (
        ("missing_plan", "blocked_missing_home_surface_plan"),
        ("unity_runtime", "blocked_unity_runtime_connection_detected"),
        ("unity_scene", "blocked_unity_scene_mutation_detected"),
        ("avatar_control", "blocked_avatar_control_detected"),
        ("external_control", "blocked_external_control_detected"),
        ("memory_write", "blocked_memory_write_detected"),
        ("teacher_approval", "blocked_teacher_approval_created"),
        ("first_output", "blocked_first_output_detected"),
        ("live_runtime", "blocked_live_runtime_detected"),
        ("production_behavior", "blocked_production_behavior_detected"),
        ("invalid_plan", "blocked_missing_home_surface_plan"),
        ("invalid_port_surface", "blocked_invalid_port_surface"),
        ("invalid_host_event_surface", "blocked_invalid_host_event_surface"),
        ("invalid_runtime_bridge_surface", "blocked_invalid_runtime_bridge_surface"),
        ("invalid_teacher_surface", "blocked_invalid_teacher_surface"),
        ("invalid_render", "blocked_invalid_render"),
    )
    for reason, status in priority:
        if reason in reasons:
            return status
    if bridge_surface is not None and bridge_surface.runtime_bridge_surface_status == "runtime_bridge_surface_created_with_deferred_dispatch":
        return "passed_home_surface_with_deferred_dispatch"
    if host_surface is not None and host_surface.host_event_surface_status == "host_event_surface_created_empty":
        return "passed_home_surface_with_empty_events"
    return "passed_qingyin_home_internal_space_event_surface"


def _plan_has_forbidden_boundary(item: QingyinHomeInternalSpaceSurfacePlanRecord) -> bool:
    return (
        item.unity_runtime_connection_allowed
        or item.unity_scene_mutation_allowed
        or item.avatar_control_allowed
        or item.game_character_control_allowed
        or item.real_camera_access_allowed
        or item.real_mic_access_allowed
        or item.semantic_interpretation_allowed
        or item.speech_recognition_allowed
        or item.action_selection_allowed
        or item.external_control_allowed
        or item.memory_write_allowed
        or item.automatic_learning_approval_allowed
        or item.first_output_allowed
        or item.live_runtime_session_allowed
    )


def _host_event_rows(
    mappings: tuple[HostBodyEventToRuntimeFrameMappingRecord, ...],
    links: tuple[HostBodyRuntimeDispatchLinkRecord, ...],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, mapping in enumerate(mappings):
        link = links[index] if index < len(links) else None
        rows.append(
            {
                "event_id": mapping.source_host_body_event_id,
                "event_type": mapping.source_event_type,
                "event_family": mapping.source_event_family,
                "source_port_kind": mapping.source_port_kind,
                "bridge_status": mapping.mapping_status,
                "target_event_family": mapping.target_event_family,
                "target_engine_lane": mapping.target_engine_lane,
                "return_payload_status": link.return_payload_status if link else None,
                "read_only": mapping.mapping_is_read_only,
                "fixture_only": mapping.mapping_is_fixture_only,
            }
        )
    return rows


def _runtime_bridge_rows(
    mappings: tuple[HostBodyEventToRuntimeFrameMappingRecord, ...],
    links: tuple[HostBodyRuntimeDispatchLinkRecord, ...],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, mapping in enumerate(mappings):
        link = links[index] if index < len(links) else None
        rows.append(
            {
                "runtime_event_type": mapping.target_event_type,
                "target_event_family": mapping.target_event_family,
                "target_engine_lane": mapping.target_engine_lane,
                "dispatch_link_status": link.dispatch_link_status if link else None,
                "return_payload_status": link.return_payload_status if link else None,
            }
        )
    return rows


def _plan_summary(status: str) -> str:
    if status == "surface_plan_created":
        return "Qingyin Home internal-space surface plan created."
    return f"Qingyin Home surface plan blocked: {status}."


def _port_surface_summary(status: str) -> str:
    if status == "port_surface_created":
        return "Host Body ports visible as read-only internal-space surface."
    return f"Port surface blocked: {status}."


def _host_event_surface_summary(status: str, count: int) -> str:
    if status.startswith("host_event_surface_created"):
        return f"{count} Host Body event rows visible as read-only display rows."
    return f"Host event surface blocked: {status}."


def _runtime_bridge_surface_summary(status: str) -> str:
    if status.startswith("runtime_bridge_surface_created"):
        return "Runtime EventFrame bridge status visible as read-only rows."
    return f"Runtime bridge surface blocked: {status}."


def _status_light_summary(status: str, kind: str) -> str:
    if status == "status_light_recorded":
        return f"{kind} status light recorded as data only."
    return f"{kind} status light blocked: {status}."


def _teacher_surface_summary(status: str) -> str:
    if status.startswith("teacher_observed_surface_created"):
        return "Teacher-observed surface created without approval."
    return f"Teacher-observed surface blocked: {status}."


def _render_summary(status: str) -> str:
    if status.startswith("home_internal_space_render_created"):
        return "Read-only Qingyin Home render snapshot created."
    return f"Qingyin Home render blocked: {status}."


def _readiness_summary(status: str) -> str:
    if status == "ready_for_host_body_trace_history_lane_only":
        return "Ready only for read-only Host Body trace history lane."
    return f"Qingyin Home surface readiness blocked: {status}."


def _validation(valid: bool, errors: list[str], record_id: str, status: str) -> dict[str, object]:
    return {"valid": valid, "error_codes": tuple(errors), "record_id": record_id, "status": status}


def _identity(value: HostBodyIdentityRecord | dict[str, object]) -> HostBodyIdentityRecord:
    return value if isinstance(value, HostBodyIdentityRecord) else HostBodyIdentityRecord.from_dict(value)


def _port_map(value: HostBodyPortMapRecord | dict[str, object]) -> HostBodyPortMapRecord:
    return value if isinstance(value, HostBodyPortMapRecord) else HostBodyPortMapRecord.from_dict(value)


def _internal_space(value: HostInternalSpacePortRecord | dict[str, object]) -> HostInternalSpacePortRecord:
    return value if isinstance(value, HostInternalSpacePortRecord) else HostInternalSpacePortRecord.from_dict(value)


def _event_set(value: HostBodySensorEventSetRecord | dict[str, object]) -> HostBodySensorEventSetRecord:
    return value if isinstance(value, HostBodySensorEventSetRecord) else HostBodySensorEventSetRecord.from_dict(value)


def _bridge_audit(value: HostBodyRuntimeBridgeAudit | dict[str, object]) -> HostBodyRuntimeBridgeAudit:
    return value if isinstance(value, HostBodyRuntimeBridgeAudit) else HostBodyRuntimeBridgeAudit.from_dict(value)


def _bridge_trace(value: HostBodyRuntimeBridgeTraceRecord | dict[str, object]) -> HostBodyRuntimeBridgeTraceRecord:
    return value if isinstance(value, HostBodyRuntimeBridgeTraceRecord) else HostBodyRuntimeBridgeTraceRecord.from_dict(value)


def _mapping(value: HostBodyEventToRuntimeFrameMappingRecord | dict[str, object]) -> HostBodyEventToRuntimeFrameMappingRecord:
    return value if isinstance(value, HostBodyEventToRuntimeFrameMappingRecord) else HostBodyEventToRuntimeFrameMappingRecord.from_dict(value)


def _dispatch_link(value: HostBodyRuntimeDispatchLinkRecord | dict[str, object]) -> HostBodyRuntimeDispatchLinkRecord:
    return value if isinstance(value, HostBodyRuntimeDispatchLinkRecord) else HostBodyRuntimeDispatchLinkRecord.from_dict(value)


def _plan(value: QingyinHomeInternalSpaceSurfacePlanRecord | dict[str, object]) -> QingyinHomeInternalSpaceSurfacePlanRecord:
    return value if isinstance(value, QingyinHomeInternalSpaceSurfacePlanRecord) else QingyinHomeInternalSpaceSurfacePlanRecord.from_dict(value)


def _port_surface(value: QingyinHomePortSurfaceRecord | dict[str, object]) -> QingyinHomePortSurfaceRecord:
    return value if isinstance(value, QingyinHomePortSurfaceRecord) else QingyinHomePortSurfaceRecord.from_dict(value)


def _host_event_surface(value: QingyinHomeHostEventSurfaceRecord | dict[str, object]) -> QingyinHomeHostEventSurfaceRecord:
    return value if isinstance(value, QingyinHomeHostEventSurfaceRecord) else QingyinHomeHostEventSurfaceRecord.from_dict(value)


def _runtime_bridge_surface(value: QingyinHomeRuntimeBridgeSurfaceRecord | dict[str, object]) -> QingyinHomeRuntimeBridgeSurfaceRecord:
    return value if isinstance(value, QingyinHomeRuntimeBridgeSurfaceRecord) else QingyinHomeRuntimeBridgeSurfaceRecord.from_dict(value)


def _status_light(value: QingyinHomeStatusLightRecord | dict[str, object]) -> QingyinHomeStatusLightRecord:
    return value if isinstance(value, QingyinHomeStatusLightRecord) else QingyinHomeStatusLightRecord.from_dict(value)


def _teacher_surface(value: QingyinHomeTeacherObservedSurfaceRecord | dict[str, object]) -> QingyinHomeTeacherObservedSurfaceRecord:
    return value if isinstance(value, QingyinHomeTeacherObservedSurfaceRecord) else QingyinHomeTeacherObservedSurfaceRecord.from_dict(value)


def _render(value: QingyinHomeInternalSpaceRenderRecord | dict[str, object]) -> QingyinHomeInternalSpaceRenderRecord:
    return value if isinstance(value, QingyinHomeInternalSpaceRenderRecord) else QingyinHomeInternalSpaceRenderRecord.from_dict(value)


def _audit(value: QingyinHomeInternalSpaceSurfaceAudit | dict[str, object]) -> QingyinHomeInternalSpaceSurfaceAudit:
    return value if isinstance(value, QingyinHomeInternalSpaceSurfaceAudit) else QingyinHomeInternalSpaceSurfaceAudit.from_dict(value)


def _readiness(value: QingyinHomeInternalSpaceSurfaceReadinessRecord | dict[str, object]) -> QingyinHomeInternalSpaceSurfaceReadinessRecord:
    return value if isinstance(value, QingyinHomeInternalSpaceSurfaceReadinessRecord) else QingyinHomeInternalSpaceSurfaceReadinessRecord.from_dict(value)
