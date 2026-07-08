"""Fixture-only HostBodyEvent to Runtime EventFrame bridge records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.host_body.host_body_sensor_events import (
    HostBodyEventRecord,
    HostBodySensorEventAudit,
    HostBodySensorEventSetRecord,
    build_demo_blocked_real_camera_event,
    build_demo_camera_frame_available_event,
    build_demo_host_idle_event,
    build_demo_mic_peak_detected_event,
    build_demo_mixed_host_sensor_event_set,
)
from ashl_core_v1.runtime.continuous_event_loop import (
    EVENT_FRAME_SCHEMA_VERSION,
    RuntimeEventFrameRecord,
)


SOURCE_ENGINE = "host_body"
RUNTIME_SOURCE_ENGINE = "runtime"

BRIDGE_PLAN_SCHEMA_VERSION = "qingyin_host_body_runtime_bridge_plan_v0"
MAPPING_SCHEMA_VERSION = "qingyin_host_body_event_to_runtime_frame_mapping_v0"
EVENTFRAME_BRIDGE_SCHEMA_VERSION = "qingyin_host_body_runtime_eventframe_bridge_v0"
DISPATCH_LINK_SCHEMA_VERSION = "qingyin_host_body_runtime_dispatch_link_v0"
BRIDGE_TRACE_SCHEMA_VERSION = "qingyin_host_body_runtime_bridge_trace_v0"
BRIDGE_AUDIT_SCHEMA_VERSION = "qingyin_host_body_runtime_bridge_audit_v0"
BRIDGE_READINESS_SCHEMA_VERSION = "qingyin_host_body_runtime_bridge_readiness_v0"

BRIDGE_NAME = "host_body_event_to_runtime_eventframe_bridge"
BRIDGE_KIND = "fixture_only_runtime_eventframe_bridge"

ALLOWED_SOURCE_EVENT_FAMILIES = (
    "camera_low_level_event",
    "mic_low_level_event",
    "host_idle_event",
    "host_status_event",
)
ALLOWED_TARGET_EVENT_TYPES = (
    "host_camera_event",
    "host_mic_event",
    "host_idle_event",
    "host_status_event",
)
ALLOWED_TARGET_EVENT_FAMILIES = ("sense_event", "runtime_event", "state_event")
ALLOWED_TARGET_ENGINE_LANES = ("runtime", "state_engine", "sense_interface")
FORBIDDEN_TARGET_ENGINE_LANES = (
    "learning_engine",
    "memory_engine",
    "task_engine",
    "selected_action",
    "final_action",
    "direct_command",
    "execution",
)

SAFE_CLAIM = (
    "ASHL Core v1 can map fixture-only read-only HostBodyEvent records into "
    "bounded Runtime EventFrame bridge records and adapter-only dispatch links."
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
    "no_live_engine_invocation",
    "no_dynamic_scheduling",
)
READINESS_NEXT_PACKAGE = (
    "Package 104 / ASHL Core v1 Qingyin Home Internal Space Event Surface Minimal v0"
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
class HostBodyRuntimeBridgePlanRecord:
    host_runtime_bridge_plan_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_port_map_id: str | None
    source_host_sensor_event_audit_id: str | None
    bridge_name: str
    bridge_kind: str
    allowed_source_event_families: tuple[str, ...]
    allowed_target_event_types: tuple[str, ...]
    allowed_target_event_families: tuple[str, ...]
    allowed_target_engine_lanes: tuple[str, ...]
    fixture_only_required: bool
    read_only_required: bool
    runtime_eventframe_only: bool
    real_hardware_allowed: bool
    semantic_interpretation_allowed: bool
    action_selection_allowed: bool
    external_control_allowed: bool
    memory_write_allowed: bool
    automatic_learning_approval_allowed: bool
    first_output_allowed: bool
    live_runtime_session_allowed: bool
    dynamic_scheduling_allowed: bool
    live_engine_invocation_allowed: bool
    bridge_plan_status: str
    bridge_plan_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BRIDGE_PLAN_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_runtime_bridge_plan_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.bridge_name != BRIDGE_NAME:
            raise ValueError("bridge_name must be host_body_event_to_runtime_eventframe_bridge")
        if self.bridge_kind != BRIDGE_KIND:
            raise ValueError("bridge_kind must be fixture_only_runtime_eventframe_bridge")
        if self.bridge_plan_status not in {
            "bridge_plan_created",
            "blocked_missing_host_sensor_event_audit",
            "blocked_unapproved_source_event_family",
            "blocked_unapproved_target_event_family",
            "blocked_real_hardware_allowed",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown bridge_plan_status: {self.bridge_plan_status}")
        for name in (
            "allowed_source_event_families",
            "allowed_target_event_types",
            "allowed_target_event_families",
            "allowed_target_engine_lanes",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyRuntimeBridgePlanRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyEventToRuntimeFrameMappingRecord:
    host_event_runtime_mapping_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_bridge_plan_id: str
    source_host_body_event_id: str
    source_event_type: str
    source_event_family: str
    source_port_kind: str
    target_runtime_event_frame_id: str
    target_event_type: str
    target_event_family: str
    target_engine_lane: str
    mapping_status: str
    mapping_summary: str
    mapping_is_fixture_only: bool
    mapping_is_read_only: bool
    semantic_label_preserved_null: bool
    semantic_interpretation_created: bool
    action_selection_influence_created: bool
    external_control_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MAPPING_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_event_to_runtime_frame_mapping_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.target_engine_lane not in {
            "runtime",
            "state_engine",
            "sense_interface",
            "none",
            *FORBIDDEN_TARGET_ENGINE_LANES,
        }:
            raise ValueError(f"unknown target_engine_lane: {self.target_engine_lane}")
        if self.mapping_status not in {
            "host_event_mapped_to_runtime_eventframe",
            "host_event_mapped_to_sense_eventframe",
            "host_event_mapped_to_runtime_eventframe_idle",
            "host_event_mapped_to_state_eventframe",
            "blocked_unknown_host_event_family",
            "blocked_forbidden_target_engine",
            "blocked_semantic_interpretation_detected",
            "blocked_action_selection_influence_detected",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown mapping_status: {self.mapping_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyEventToRuntimeFrameMappingRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyRuntimeEventFrameBridgeRecord:
    host_runtime_eventframe_bridge_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_event_runtime_mapping_id: str
    source_host_body_event_id: str
    source_runtime_event_frame_id: str
    source_runtime_tick_id: str | None
    source_power_window_id: str | None
    bridge_status: str
    bridge_summary: str
    runtime_eventframe_created: bool
    runtime_eventframe_fixture_only: bool
    runtime_eventframe_read_only: bool
    event_frame_depth: int
    event_frame_parent_id: str | None
    event_type: str
    event_family: str
    target_engine_lane: str
    dispatch_required: bool
    parent_resume_required: bool
    dynamic_child_event_created: bool
    live_runtime_session_created: bool
    live_engine_invocation_created: bool
    external_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    first_output_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVENTFRAME_BRIDGE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_runtime_eventframe_bridge_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.bridge_status not in {
            "runtime_eventframe_bridge_created",
            "runtime_eventframe_bridge_created_for_sense_event",
            "runtime_eventframe_bridge_created_for_idle_event",
            "runtime_eventframe_bridge_created_for_state_event",
            "blocked_invalid_mapping",
            "blocked_live_runtime_detected",
            "blocked_dynamic_child_event_detected",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown bridge_status: {self.bridge_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyRuntimeEventFrameBridgeRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyRuntimeDispatchLinkRecord:
    host_runtime_dispatch_link_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_runtime_eventframe_bridge_id: str
    source_runtime_event_frame_id: str
    source_dispatch_request_id: str | None
    source_dispatch_route_id: str | None
    source_handler_adapter_id: str | None
    source_dispatch_result_id: str | None
    source_dispatch_return_payload_id: str | None
    dispatch_link_status: str
    dispatch_link_summary: str
    dispatch_adapter_only: bool
    handler_invoked: bool
    live_engine_invocation_created: bool
    target_engine_lane: str
    return_payload_status: str | None
    external_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    first_output_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DISPATCH_LINK_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_runtime_dispatch_link_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.dispatch_link_status not in {
            "dispatch_link_created_adapter_only",
            "dispatch_link_created_sense_adapter_only",
            "dispatch_link_created_runtime_adapter_only",
            "dispatch_link_created_state_adapter_only",
            "dispatch_link_deferred_missing_dispatch_adapter",
            "blocked_missing_eventframe_bridge",
            "blocked_live_engine_invocation_detected",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown dispatch_link_status: {self.dispatch_link_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyRuntimeDispatchLinkRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyRuntimeBridgeTraceRecord:
    host_runtime_bridge_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_bridge_plan_id: str
    host_body_event_ids: tuple[str, ...]
    event_mapping_ids: tuple[str, ...]
    eventframe_bridge_ids: tuple[str, ...]
    dispatch_link_ids: tuple[str, ...]
    bridged_event_count: int
    camera_event_bridge_count: int
    mic_event_bridge_count: int
    idle_event_bridge_count: int
    state_event_bridge_count: int
    all_events_fixture_only: bool
    all_events_read_only: bool
    all_events_mapped_to_allowed_eventframes: bool
    all_bridged_eventframes_dispatchable: bool
    bridge_trace_status: str
    bridge_trace_summary: str
    real_hardware_accessed: bool
    semantic_interpretation_created: bool
    action_selection_influence_created: bool
    external_control_created: bool
    live_runtime_session_created: bool
    live_engine_invocation_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    first_output_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BRIDGE_TRACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_runtime_bridge_trace_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.bridge_trace_status not in {
            "host_body_runtime_bridge_trace_complete",
            "host_body_runtime_bridge_trace_complete_with_deferred_dispatch",
            "host_body_runtime_bridge_trace_blocked_missing_plan",
            "host_body_runtime_bridge_trace_blocked_missing_mapping",
            "host_body_runtime_bridge_trace_blocked_missing_eventframe_bridge",
            "host_body_runtime_bridge_trace_blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown bridge_trace_status: {self.bridge_trace_status}")
        for name in (
            "host_body_event_ids",
            "event_mapping_ids",
            "eventframe_bridge_ids",
            "dispatch_link_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyRuntimeBridgeTraceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyRuntimeBridgeAudit:
    host_runtime_bridge_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_bridge_plan_id: str | None
    source_bridge_trace_id: str | None
    host_sensor_event_audit_valid: bool
    bridge_plan_valid: bool
    event_mappings_valid: bool
    eventframe_bridges_valid: bool
    dispatch_links_valid: bool
    bridge_trace_valid: bool
    fixture_only_confirmed: bool
    read_only_confirmed: bool
    runtime_eventframe_bridge_confirmed: bool
    dispatch_adapter_only_confirmed: bool
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
    no_live_engine_invocation: bool
    no_autonomous_scheduler: bool
    no_open_ended_loop: bool
    no_dynamic_child_event_scheduling: bool
    no_thought_engine_behavior: bool
    no_production_behavior: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BRIDGE_AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_runtime_bridge_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.audit_status not in {
            "passed_host_body_event_runtime_eventframe_bridge",
            "passed_camera_event_to_sense_eventframe_bridge",
            "passed_mic_event_to_sense_eventframe_bridge",
            "passed_idle_event_to_runtime_eventframe_bridge",
            "passed_host_body_runtime_bridge_with_deferred_dispatch",
            "blocked_missing_sensor_event_audit",
            "blocked_invalid_bridge_plan",
            "blocked_invalid_event_mapping",
            "blocked_invalid_eventframe_bridge",
            "blocked_invalid_dispatch_link",
            "blocked_real_hardware_access_detected",
            "blocked_semantic_interpretation_detected",
            "blocked_action_selection_influence_detected",
            "blocked_external_control_detected",
            "blocked_memory_write_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
            "blocked_live_engine_invocation_detected",
            "blocked_dynamic_scheduling_detected",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyRuntimeBridgeAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyRuntimeBridgeReadinessRecord:
    host_runtime_bridge_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_runtime_bridge_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_unity_home_internal_space_surface: bool
    ready_for_host_body_trace_history_lane: bool
    ready_for_internal_action_choice_only: bool
    ready_for_teacher_observed_host_event_cli: bool
    ready_for_real_camera_connection: bool
    ready_for_real_mic_connection: bool
    ready_for_speech_recognition: bool
    ready_for_semantic_vision: bool
    ready_for_external_control: bool
    ready_for_first_output: bool
    ready_for_live_runtime_session: bool
    ready_for_memory_layer_write: bool
    ready_for_autonomous_scheduler: bool
    ready_for_live_engine_invocation: bool
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BRIDGE_READINESS_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_runtime_bridge_readiness_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.readiness_status not in {
            "ready_for_unity_home_internal_space_surface_only",
            "ready_for_host_body_trace_history_lane_only",
            "ready_for_internal_action_choice_only",
            "not_ready_missing_host_runtime_bridge_audit",
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
    def from_dict(cls, data: dict[str, object]) -> "HostBodyRuntimeBridgeReadinessRecord":
        return cls(**dict(data))


def build_host_body_runtime_bridge_plan(
    *,
    host_sensor_event_audit: HostBodySensorEventAudit | dict[str, object] | None,
    source_host_body_port_map_id: str | None = None,
    allowed_source_event_families: tuple[str, ...] = ALLOWED_SOURCE_EVENT_FAMILIES,
    allowed_target_event_families: tuple[str, ...] = ALLOWED_TARGET_EVENT_FAMILIES,
    allowed_target_engine_lanes: tuple[str, ...] = ALLOWED_TARGET_ENGINE_LANES,
    real_hardware_allowed: bool = False,
    semantic_interpretation_allowed: bool = False,
    action_selection_allowed: bool = False,
    external_control_allowed: bool = False,
    memory_write_allowed: bool = False,
    automatic_learning_approval_allowed: bool = False,
    first_output_allowed: bool = False,
    live_runtime_session_allowed: bool = False,
    dynamic_scheduling_allowed: bool = False,
    live_engine_invocation_allowed: bool = False,
) -> HostBodyRuntimeBridgePlanRecord:
    audit = _sensor_audit(host_sensor_event_audit) if host_sensor_event_audit is not None else None
    status = _bridge_plan_status(
        audit=audit,
        allowed_source_event_families=allowed_source_event_families,
        allowed_target_event_families=allowed_target_event_families,
        allowed_target_engine_lanes=allowed_target_engine_lanes,
        real_hardware_allowed=real_hardware_allowed,
        semantic_interpretation_allowed=semantic_interpretation_allowed,
        action_selection_allowed=action_selection_allowed,
        external_control_allowed=external_control_allowed,
        memory_write_allowed=memory_write_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
        dynamic_scheduling_allowed=dynamic_scheduling_allowed,
        live_engine_invocation_allowed=live_engine_invocation_allowed,
    )
    return HostBodyRuntimeBridgePlanRecord(
        host_runtime_bridge_plan_id=f"host_runtime_bridge_plan:{_slug(status)}",
        schema_version=BRIDGE_PLAN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_port_map_id=source_host_body_port_map_id,
        source_host_sensor_event_audit_id=audit.host_sensor_event_audit_id if audit else None,
        bridge_name=BRIDGE_NAME,
        bridge_kind=BRIDGE_KIND,
        allowed_source_event_families=allowed_source_event_families,
        allowed_target_event_types=ALLOWED_TARGET_EVENT_TYPES,
        allowed_target_event_families=allowed_target_event_families,
        allowed_target_engine_lanes=allowed_target_engine_lanes,
        fixture_only_required=True,
        read_only_required=True,
        runtime_eventframe_only=True,
        real_hardware_allowed=real_hardware_allowed,
        semantic_interpretation_allowed=semantic_interpretation_allowed,
        action_selection_allowed=action_selection_allowed,
        external_control_allowed=external_control_allowed,
        memory_write_allowed=memory_write_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
        dynamic_scheduling_allowed=dynamic_scheduling_allowed,
        live_engine_invocation_allowed=live_engine_invocation_allowed,
        bridge_plan_status=status,
        bridge_plan_summary=_bridge_plan_summary(status),
        source_trace_refs=audit.source_trace_refs if audit else tuple(),
    )


def validate_host_body_runtime_bridge_plan(
    record: HostBodyRuntimeBridgePlanRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _plan(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.bridge_plan_status == "bridge_plan_created":
        if item.source_host_sensor_event_audit_id is None:
            errors.append("missing_sensor_event_audit")
        for flag in (
            "real_hardware_allowed",
            "semantic_interpretation_allowed",
            "action_selection_allowed",
            "external_control_allowed",
            "memory_write_allowed",
            "automatic_learning_approval_allowed",
            "first_output_allowed",
            "live_runtime_session_allowed",
            "dynamic_scheduling_allowed",
            "live_engine_invocation_allowed",
        ):
            if getattr(item, flag):
                errors.append(f"{flag}_true")
    return _validation(not errors, errors, item.host_runtime_bridge_plan_id, item.bridge_plan_status)


def map_host_body_event_to_runtime_eventframe(
    *,
    bridge_plan: HostBodyRuntimeBridgePlanRecord | dict[str, object],
    host_body_event: HostBodyEventRecord | dict[str, object],
    target_engine_lane: str | None = None,
    semantic_interpretation_created: bool = False,
    action_selection_influence_created: bool = False,
    external_control_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyEventToRuntimeFrameMappingRecord:
    plan = _plan(bridge_plan)
    event = _host_event(host_body_event)
    default_event_type, default_family, default_lane = _target_for_host_family(event.event_family)
    lane = target_engine_lane or default_lane
    target_event_family = _family_for_lane(default_family, lane)
    status = _mapping_status(
        plan=plan,
        event=event,
        target_engine_lane=lane,
        target_event_family=target_event_family,
        semantic_interpretation_created=semantic_interpretation_created,
        action_selection_influence_created=action_selection_influence_created,
        external_control_created=external_control_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    frame_id = f"runtime_event_frame:host_body_bridge:{_slug(event.host_body_event_id)}"
    return HostBodyEventToRuntimeFrameMappingRecord(
        host_event_runtime_mapping_id=f"host_event_runtime_mapping:{_slug(event.host_body_event_id)}:{_slug(status)}",
        schema_version=MAPPING_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_bridge_plan_id=plan.host_runtime_bridge_plan_id,
        source_host_body_event_id=event.host_body_event_id,
        source_event_type=event.event_type,
        source_event_family=event.event_family,
        source_port_kind=event.source_port_kind,
        target_runtime_event_frame_id=frame_id,
        target_event_type=default_event_type if status != "blocked_unknown_host_event_family" else "unknown_host_event",
        target_event_family=target_event_family,
        target_engine_lane=lane,
        mapping_status=status,
        mapping_summary=_mapping_summary(status, event.event_family, lane),
        mapping_is_fixture_only=event.fixture_only,
        mapping_is_read_only=event.read_only_event,
        semantic_label_preserved_null=event.semantic_label is None,
        semantic_interpretation_created=semantic_interpretation_created
        or event.semantic_vision_created
        or event.object_recognition_created
        or event.face_recognition_created
        or event.speech_recognition_created
        or event.speaker_identification_created
        or event.voice_command_created
        or event.language_understanding_created,
        action_selection_influence_created=action_selection_influence_created
        or event.action_selection_influence_created,
        external_control_created=external_control_created or event.external_control_created,
        memory_write_performed=memory_write_performed or event.memory_layer_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created
        or event.automatic_learning_approval_created,
        first_output_created=first_output_created or event.first_output_created,
        live_runtime_session_created=live_runtime_session_created
        or event.live_runtime_session_created,
        source_trace_refs=event.source_trace_refs,
    )


def validate_host_body_event_to_runtime_frame_mapping(
    record: HostBodyEventToRuntimeFrameMappingRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _mapping(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.mapping_status.startswith("host_event_mapped"):
        if item.target_engine_lane not in ALLOWED_TARGET_ENGINE_LANES:
            errors.append("mapped_to_forbidden_engine")
        if item.target_event_family not in ALLOWED_TARGET_EVENT_FAMILIES:
            errors.append("mapped_to_forbidden_family")
        if not item.mapping_is_fixture_only:
            errors.append("fixture_only_false")
        if not item.mapping_is_read_only:
            errors.append("read_only_false")
        if not item.semantic_label_preserved_null:
            errors.append("semantic_label_not_null")
        if _mapping_has_forbidden_boundary(item):
            errors.append("mapped_record_has_forbidden_boundary")
    return _validation(not errors, errors, item.host_event_runtime_mapping_id, item.mapping_status)


def build_host_body_runtime_eventframe_bridge(
    *,
    mapping: HostBodyEventToRuntimeFrameMappingRecord | dict[str, object],
    source_runtime_tick_id: str | None = None,
    source_power_window_id: str | None = "runtime_power_window:host_body_fixture_bridge",
    event_frame_depth: int = 1,
    event_frame_parent_id: str | None = None,
    dynamic_child_event_created: bool = False,
    live_runtime_session_created: bool = False,
    live_engine_invocation_created: bool = False,
    external_execution_created: bool = False,
    memory_layer_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    first_output_created: bool = False,
    production_behavior_created: bool = False,
) -> tuple[HostBodyRuntimeEventFrameBridgeRecord, RuntimeEventFrameRecord | None]:
    item = _mapping(mapping)
    status = _eventframe_bridge_status(
        mapping=item,
        dynamic_child_event_created=dynamic_child_event_created,
        live_runtime_session_created=live_runtime_session_created,
        live_engine_invocation_created=live_engine_invocation_created,
        external_execution_created=external_execution_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        production_behavior_created=production_behavior_created,
    )
    frame = None
    if status.startswith("runtime_eventframe_bridge_created"):
        frame = RuntimeEventFrameRecord(
            event_frame_id=item.target_runtime_event_frame_id,
            schema_version=EVENT_FRAME_SCHEMA_VERSION,
            created_at=_now(),
            source_engine=RUNTIME_SOURCE_ENGINE,
            source_power_window_id=source_power_window_id or "runtime_power_window:host_body_fixture_bridge",
            event_type=item.target_event_type,
            event_label=f"host_body_bridge_{_slug(item.source_event_type)}",
            event_depth=event_frame_depth,
            parent_event_frame_id=event_frame_parent_id,
            child_event_frame_ids=tuple(),
            opened_at_tick_index=0,
            closed_at_tick_index=1,
            event_scope="host_body_fixture_bridge",
            event_budget_ticks=16,
            event_ticks_used=1,
            event_status="event_closed_returned",
            event_summary=f"Fixture-only HostBodyEvent bridge for {item.source_event_type}.",
            return_payload_id=None,
            return_payload_status="none",
            child_scope_expansion_detected=False,
            budget_exceeded=False,
            unclosed_frame_detected=False,
            memory_write_performed=False,
            automatic_learning_approval_created=False,
            free_action_selection_created=False,
            external_execution_created=False,
            production_behavior_created=False,
            source_trace_refs=(item.host_event_runtime_mapping_id,),
        )
    bridge = HostBodyRuntimeEventFrameBridgeRecord(
        host_runtime_eventframe_bridge_id=f"host_runtime_eventframe_bridge:{_slug(item.host_event_runtime_mapping_id)}:{_slug(status)}",
        schema_version=EVENTFRAME_BRIDGE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_event_runtime_mapping_id=item.host_event_runtime_mapping_id,
        source_host_body_event_id=item.source_host_body_event_id,
        source_runtime_event_frame_id=item.target_runtime_event_frame_id,
        source_runtime_tick_id=source_runtime_tick_id,
        source_power_window_id=source_power_window_id,
        bridge_status=status,
        bridge_summary=_eventframe_bridge_summary(status, item.target_engine_lane),
        runtime_eventframe_created=status.startswith("runtime_eventframe_bridge_created"),
        runtime_eventframe_fixture_only=True,
        runtime_eventframe_read_only=True,
        event_frame_depth=event_frame_depth,
        event_frame_parent_id=event_frame_parent_id,
        event_type=item.target_event_type,
        event_family=item.target_event_family,
        target_engine_lane=item.target_engine_lane,
        dispatch_required=True,
        parent_resume_required=event_frame_parent_id is not None,
        dynamic_child_event_created=dynamic_child_event_created,
        live_runtime_session_created=live_runtime_session_created,
        live_engine_invocation_created=live_engine_invocation_created,
        external_execution_created=external_execution_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        production_behavior_created=production_behavior_created,
        source_trace_refs=item.source_trace_refs,
    )
    return bridge, frame


def validate_host_body_runtime_eventframe_bridge(
    record: HostBodyRuntimeEventFrameBridgeRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _eventframe_bridge(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.bridge_status.startswith("runtime_eventframe_bridge_created"):
        if not item.runtime_eventframe_created:
            errors.append("runtime_eventframe_not_created")
        if not item.runtime_eventframe_fixture_only:
            errors.append("fixture_only_false")
        if not item.runtime_eventframe_read_only:
            errors.append("read_only_false")
        if not item.dispatch_required:
            errors.append("dispatch_required_false")
        if _eventframe_bridge_has_forbidden_boundary(item):
            errors.append("eventframe_bridge_has_forbidden_boundary")
    return _validation(not errors, errors, item.host_runtime_eventframe_bridge_id, item.bridge_status)


def build_host_body_runtime_dispatch_link(
    *,
    eventframe_bridge: HostBodyRuntimeEventFrameBridgeRecord | dict[str, object] | None,
    defer_dispatch_adapter: bool = False,
    live_engine_invocation_created: bool = False,
    external_execution_created: bool = False,
    memory_layer_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    first_output_created: bool = False,
    production_behavior_created: bool = False,
) -> HostBodyRuntimeDispatchLinkRecord:
    bridge = _eventframe_bridge(eventframe_bridge) if eventframe_bridge is not None else None
    status = _dispatch_link_status(
        bridge=bridge,
        defer_dispatch_adapter=defer_dispatch_adapter,
        live_engine_invocation_created=live_engine_invocation_created,
        external_execution_created=external_execution_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        production_behavior_created=production_behavior_created,
    )
    frame_id = bridge.source_runtime_event_frame_id if bridge else "missing_runtime_event_frame"
    link_id = f"host_runtime_dispatch_link:{_slug(frame_id)}:{_slug(status)}"
    synthetic_prefix = f"host_runtime_dispatch:{_slug(frame_id)}"
    ids_available = status not in {
        "dispatch_link_deferred_missing_dispatch_adapter",
        "blocked_missing_eventframe_bridge",
        "blocked_live_engine_invocation_detected",
        "blocked_forbidden_authority_detected",
    }
    return HostBodyRuntimeDispatchLinkRecord(
        host_runtime_dispatch_link_id=link_id,
        schema_version=DISPATCH_LINK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_runtime_eventframe_bridge_id=bridge.host_runtime_eventframe_bridge_id if bridge else "missing_eventframe_bridge",
        source_runtime_event_frame_id=frame_id,
        source_dispatch_request_id=f"{synthetic_prefix}:request" if ids_available else None,
        source_dispatch_route_id=f"{synthetic_prefix}:route" if ids_available else None,
        source_handler_adapter_id=f"{synthetic_prefix}:handler_adapter" if ids_available else None,
        source_dispatch_result_id=f"{synthetic_prefix}:result" if ids_available else None,
        source_dispatch_return_payload_id=f"{synthetic_prefix}:return_payload" if ids_available else None,
        dispatch_link_status=status,
        dispatch_link_summary=_dispatch_link_summary(status),
        dispatch_adapter_only=True,
        handler_invoked=False,
        live_engine_invocation_created=live_engine_invocation_created,
        target_engine_lane=bridge.target_engine_lane if bridge else "none",
        return_payload_status="returned_success" if ids_available else None,
        external_execution_created=external_execution_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        production_behavior_created=production_behavior_created,
        source_trace_refs=bridge.source_trace_refs if bridge else tuple(),
    )


def validate_host_body_runtime_dispatch_link(
    record: HostBodyRuntimeDispatchLinkRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _dispatch_link(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.dispatch_link_status.startswith("dispatch_link_created"):
        if not item.dispatch_adapter_only:
            errors.append("dispatch_adapter_only_false")
        if item.handler_invoked:
            errors.append("handler_invoked")
        if item.live_engine_invocation_created:
            errors.append("live_engine_invocation")
        if _dispatch_link_has_forbidden_boundary(item):
            errors.append("dispatch_link_has_forbidden_boundary")
        required_ids = (
            item.source_dispatch_request_id,
            item.source_dispatch_route_id,
            item.source_handler_adapter_id,
            item.source_dispatch_result_id,
            item.source_dispatch_return_payload_id,
        )
        if not all(required_ids):
            errors.append("missing_adapter_link_ids")
    return _validation(not errors, errors, item.host_runtime_dispatch_link_id, item.dispatch_link_status)


def build_host_body_runtime_bridge_trace(
    *,
    bridge_plan: HostBodyRuntimeBridgePlanRecord | dict[str, object] | None,
    host_body_events: tuple[HostBodyEventRecord | dict[str, object], ...] | list[HostBodyEventRecord | dict[str, object]],
    event_mappings: tuple[HostBodyEventToRuntimeFrameMappingRecord | dict[str, object], ...] | list[HostBodyEventToRuntimeFrameMappingRecord | dict[str, object]],
    eventframe_bridges: tuple[HostBodyRuntimeEventFrameBridgeRecord | dict[str, object], ...] | list[HostBodyRuntimeEventFrameBridgeRecord | dict[str, object]],
    dispatch_links: tuple[HostBodyRuntimeDispatchLinkRecord | dict[str, object], ...] | list[HostBodyRuntimeDispatchLinkRecord | dict[str, object]],
) -> HostBodyRuntimeBridgeTraceRecord:
    plan = _plan(bridge_plan) if bridge_plan is not None else None
    host_items = tuple(_host_event(item) for item in host_body_events)
    mappings = tuple(_mapping(item) for item in event_mappings)
    bridges = tuple(_eventframe_bridge(item) for item in eventframe_bridges)
    links = tuple(_dispatch_link(item) for item in dispatch_links)
    blocked = _trace_forbidden(host_items, mappings, bridges, links)
    status = _trace_status(plan, mappings, bridges, links, blocked)
    return HostBodyRuntimeBridgeTraceRecord(
        host_runtime_bridge_trace_id=f"host_runtime_bridge_trace:{_slug(status)}",
        schema_version=BRIDGE_TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_bridge_plan_id=plan.host_runtime_bridge_plan_id if plan else "missing_bridge_plan",
        host_body_event_ids=tuple(item.host_body_event_id for item in host_items),
        event_mapping_ids=tuple(item.host_event_runtime_mapping_id for item in mappings),
        eventframe_bridge_ids=tuple(item.host_runtime_eventframe_bridge_id for item in bridges),
        dispatch_link_ids=tuple(item.host_runtime_dispatch_link_id for item in links),
        bridged_event_count=len(bridges),
        camera_event_bridge_count=sum(1 for item in mappings if item.target_event_type == "host_camera_event"),
        mic_event_bridge_count=sum(1 for item in mappings if item.target_event_type == "host_mic_event"),
        idle_event_bridge_count=sum(1 for item in mappings if item.target_event_type == "host_idle_event"),
        state_event_bridge_count=sum(1 for item in mappings if item.target_event_type == "host_status_event"),
        all_events_fixture_only=all(item.fixture_only for item in host_items),
        all_events_read_only=all(item.read_only_event for item in host_items),
        all_events_mapped_to_allowed_eventframes=all(
            item.mapping_status.startswith("host_event_mapped") for item in mappings
        ),
        all_bridged_eventframes_dispatchable=all(
            item.bridge_status.startswith("runtime_eventframe_bridge_created") for item in bridges
        ),
        bridge_trace_status=status,
        bridge_trace_summary=_trace_summary(status),
        real_hardware_accessed="real_hardware" in blocked,
        semantic_interpretation_created="semantic" in blocked,
        action_selection_influence_created="action_selection" in blocked,
        external_control_created="external_control" in blocked,
        live_runtime_session_created="live_runtime" in blocked,
        live_engine_invocation_created="live_engine" in blocked,
        memory_layer_write_performed="memory_write" in blocked,
        automatic_learning_approval_created="automatic_learning_approval" in blocked,
        first_output_created="first_output" in blocked,
        production_behavior_created="production_behavior" in blocked,
        source_trace_refs=host_items[0].source_trace_refs if host_items else tuple(),
    )


def validate_host_body_runtime_bridge_trace(
    record: HostBodyRuntimeBridgeTraceRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _trace(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.bridge_trace_status.startswith("host_body_runtime_bridge_trace_complete"):
        if not item.all_events_fixture_only:
            errors.append("fixture_only_false")
        if not item.all_events_read_only:
            errors.append("read_only_false")
        if not item.all_events_mapped_to_allowed_eventframes:
            errors.append("mapping_not_allowed")
        if not item.all_bridged_eventframes_dispatchable:
            errors.append("eventframes_not_dispatchable")
        if _trace_has_forbidden_boundary(item):
            errors.append("trace_has_forbidden_boundary")
    return _validation(not errors, errors, item.host_runtime_bridge_trace_id, item.bridge_trace_status)


def build_host_body_runtime_bridge_audit(
    *,
    host_sensor_event_audit: HostBodySensorEventAudit | dict[str, object] | None,
    bridge_plan: HostBodyRuntimeBridgePlanRecord | dict[str, object] | None,
    bridge_trace: HostBodyRuntimeBridgeTraceRecord | dict[str, object] | None,
    event_mappings: tuple[HostBodyEventToRuntimeFrameMappingRecord | dict[str, object], ...] | list[HostBodyEventToRuntimeFrameMappingRecord | dict[str, object]] = tuple(),
    eventframe_bridges: tuple[HostBodyRuntimeEventFrameBridgeRecord | dict[str, object], ...] | list[HostBodyRuntimeEventFrameBridgeRecord | dict[str, object]] = tuple(),
    dispatch_links: tuple[HostBodyRuntimeDispatchLinkRecord | dict[str, object], ...] | list[HostBodyRuntimeDispatchLinkRecord | dict[str, object]] = tuple(),
    force_dynamic_scheduling: bool = False,
    force_autonomous_scheduler: bool = False,
    force_open_ended_loop: bool = False,
    force_thought_engine_behavior: bool = False,
) -> HostBodyRuntimeBridgeAudit:
    sensor_audit = _sensor_audit(host_sensor_event_audit) if host_sensor_event_audit is not None else None
    plan = _plan(bridge_plan) if bridge_plan is not None else None
    trace = _trace(bridge_trace) if bridge_trace is not None else None
    mappings = tuple(_mapping(item) for item in event_mappings)
    bridges = tuple(_eventframe_bridge(item) for item in eventframe_bridges)
    links = tuple(_dispatch_link(item) for item in dispatch_links)
    reasons = _audit_reasons(
        sensor_audit=sensor_audit,
        plan=plan,
        trace=trace,
        mappings=mappings,
        bridges=bridges,
        links=links,
        force_dynamic_scheduling=force_dynamic_scheduling,
        force_autonomous_scheduler=force_autonomous_scheduler,
        force_open_ended_loop=force_open_ended_loop,
        force_thought_engine_behavior=force_thought_engine_behavior,
    )
    status = _bridge_audit_status(reasons, mappings, links)
    return HostBodyRuntimeBridgeAudit(
        host_runtime_bridge_audit_id=f"host_runtime_bridge_audit:{_slug(status)}",
        schema_version=BRIDGE_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_bridge_plan_id=plan.host_runtime_bridge_plan_id if plan else None,
        source_bridge_trace_id=trace.host_runtime_bridge_trace_id if trace else None,
        host_sensor_event_audit_valid=sensor_audit is not None and sensor_audit.audit_status.startswith("passed_"),
        bridge_plan_valid=plan is not None and plan.bridge_plan_status == "bridge_plan_created",
        event_mappings_valid=bool(mappings) and all(item.mapping_status.startswith("host_event_mapped") for item in mappings),
        eventframe_bridges_valid=bool(bridges) and all(item.bridge_status.startswith("runtime_eventframe_bridge_created") for item in bridges),
        dispatch_links_valid=bool(links) and all(item.dispatch_link_status.startswith("dispatch_link_created") or item.dispatch_link_status == "dispatch_link_deferred_missing_dispatch_adapter" for item in links),
        bridge_trace_valid=trace is not None and trace.bridge_trace_status.startswith("host_body_runtime_bridge_trace_complete"),
        fixture_only_confirmed="not_fixture_only" not in reasons,
        read_only_confirmed="not_read_only" not in reasons,
        runtime_eventframe_bridge_confirmed=bool(bridges) and "invalid_eventframe_bridge" not in reasons,
        dispatch_adapter_only_confirmed=bool(links) and "invalid_dispatch_link" not in reasons,
        no_real_camera_access="real_hardware" not in reasons,
        no_real_mic_access="real_hardware" not in reasons,
        no_camera_capture="real_hardware" not in reasons,
        no_mic_stream="real_hardware" not in reasons,
        no_image_storage="real_hardware" not in reasons,
        no_audio_storage="real_hardware" not in reasons,
        no_semantic_vision="semantic" not in reasons,
        no_object_recognition="semantic" not in reasons,
        no_face_recognition="semantic" not in reasons,
        no_speech_recognition="semantic" not in reasons,
        no_speaker_identification="semantic" not in reasons,
        no_voice_command="semantic" not in reasons,
        no_language_understanding="semantic" not in reasons,
        no_action_selection_influence="action_selection" not in reasons,
        no_external_control="external_control" not in reasons,
        no_os_control=True,
        no_mouse_control=True,
        no_keyboard_control=True,
        no_browser_control=True,
        no_file_operation=True,
        no_network_execution=True,
        no_shell_execution=True,
        no_external_api_call=True,
        no_memory_layer_write="memory_write" not in reasons,
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_automatic_learning_approval="automatic_learning_approval" not in reasons,
        no_first_output="first_output" not in reasons,
        no_live_runtime_session="live_runtime" not in reasons,
        no_live_engine_invocation="live_engine" not in reasons,
        no_autonomous_scheduler="autonomous_scheduler" not in reasons,
        no_open_ended_loop="open_ended_loop" not in reasons,
        no_dynamic_child_event_scheduling="dynamic_scheduling" not in reasons,
        no_thought_engine_behavior="thought_engine_behavior" not in reasons,
        no_production_behavior="production_behavior" not in reasons,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(reasons),
        source_trace_refs=trace.source_trace_refs if trace else tuple(),
    )


def validate_host_body_runtime_bridge_audit(
    record: HostBodyRuntimeBridgeAudit | dict[str, object],
) -> dict[str, object]:
    try:
        item = _audit(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.audit_status.startswith("passed_"):
        required = (
            item.host_sensor_event_audit_valid,
            item.bridge_plan_valid,
            item.event_mappings_valid,
            item.eventframe_bridges_valid,
            item.dispatch_links_valid,
            item.bridge_trace_valid,
            item.fixture_only_confirmed,
            item.read_only_confirmed,
            item.runtime_eventframe_bridge_confirmed,
            item.dispatch_adapter_only_confirmed,
            item.no_real_camera_access,
            item.no_real_mic_access,
            item.no_semantic_vision,
            item.no_speech_recognition,
            item.no_action_selection_influence,
            item.no_external_control,
            item.no_memory_layer_write,
            item.no_first_output,
            item.no_live_runtime_session,
            item.no_live_engine_invocation,
            item.no_dynamic_child_event_scheduling,
            item.no_production_behavior,
        )
        if not all(required):
            errors.append("passed_audit_has_failed_boundary")
    return _validation(not errors, errors, item.host_runtime_bridge_audit_id, item.audit_status)


def build_host_body_runtime_bridge_readiness(
    host_runtime_bridge_audit: HostBodyRuntimeBridgeAudit | dict[str, object],
) -> HostBodyRuntimeBridgeReadinessRecord:
    audit = _audit(host_runtime_bridge_audit)
    passed = audit.audit_status.startswith("passed_")
    if passed:
        status = "ready_for_unity_home_internal_space_surface_only"
    elif audit.source_bridge_trace_id is None:
        status = "not_ready_missing_host_runtime_bridge_audit"
    elif audit.audit_status.endswith("detected"):
        status = "blocked_forbidden_authority_detected"
    else:
        status = "not_ready_boundary_failure"
    return HostBodyRuntimeBridgeReadinessRecord(
        host_runtime_bridge_readiness_id=f"host_runtime_bridge_readiness:{audit.host_runtime_bridge_audit_id}",
        schema_version=BRIDGE_READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_runtime_bridge_audit_id=audit.host_runtime_bridge_audit_id,
        current_verified_capability=SAFE_CLAIM,
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason=(
            "Create a read-only internal-space surface model for Unity Home / "
            "Host Body visualization without Unity runtime control."
        ),
        ready_for_unity_home_internal_space_surface=passed,
        ready_for_host_body_trace_history_lane=passed,
        ready_for_internal_action_choice_only=passed,
        ready_for_teacher_observed_host_event_cli=passed,
        ready_for_real_camera_connection=False,
        ready_for_real_mic_connection=False,
        ready_for_speech_recognition=False,
        ready_for_semantic_vision=False,
        ready_for_external_control=False,
        ready_for_first_output=False,
        ready_for_live_runtime_session=False,
        ready_for_memory_layer_write=False,
        ready_for_autonomous_scheduler=False,
        ready_for_live_engine_invocation=False,
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=audit.source_trace_refs,
    )


def validate_host_body_runtime_bridge_readiness(
    record: HostBodyRuntimeBridgeReadinessRecord | dict[str, object],
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
        "ready_for_live_engine_invocation",
    ):
        if getattr(item, flag):
            errors.append(f"{flag}_true")
    return _validation(not errors, errors, item.host_runtime_bridge_readiness_id, item.readiness_status)


def build_demo_camera_event_to_sense_eventframe_bridge() -> dict[str, object]:
    return _build_bridge_bundle(build_demo_camera_frame_available_event())


def build_demo_mic_event_to_sense_eventframe_bridge() -> dict[str, object]:
    return _build_bridge_bundle(build_demo_mic_peak_detected_event())


def build_demo_idle_event_to_runtime_eventframe_bridge() -> dict[str, object]:
    return _build_bridge_bundle(build_demo_host_idle_event())


def build_demo_mixed_host_body_runtime_bridge() -> dict[str, object]:
    return _build_bridge_bundle(build_demo_mixed_host_sensor_event_set())


def build_demo_deferred_dispatch_host_body_runtime_bridge() -> dict[str, object]:
    return _build_bridge_bundle(
        build_demo_mixed_host_sensor_event_set(),
        defer_dispatch_adapter=True,
    )


def build_demo_blocked_direct_learning_mapping_bridge() -> dict[str, object]:
    return _build_bridge_bundle(
        build_demo_camera_frame_available_event(),
        target_engine_lane="learning_engine",
    )


def build_demo_blocked_action_selection_influence_bridge() -> dict[str, object]:
    return _build_bridge_bundle(
        build_demo_camera_frame_available_event(),
        mapping_kwargs={"action_selection_influence_created": True},
    )


def build_demo_blocked_live_runtime_bridge() -> dict[str, object]:
    return _build_bridge_bundle(
        build_demo_host_idle_event(),
        bridge_kwargs={"live_runtime_session_created": True},
    )


def build_demo_blocked_first_output_bridge() -> dict[str, object]:
    return _build_bridge_bundle(
        build_demo_camera_frame_available_event(),
        bridge_kwargs={"first_output_created": True},
    )


def build_demo_blocked_real_hardware_bridge() -> dict[str, object]:
    return _build_bridge_bundle(build_demo_blocked_real_camera_event())


def render_host_body_runtime_bridge_summary_text(
    audit: HostBodyRuntimeBridgeAudit | dict[str, object],
    readiness: HostBodyRuntimeBridgeReadinessRecord | dict[str, object] | None = None,
) -> str:
    audit_item = _audit(audit)
    readiness_item = _readiness(readiness) if readiness is not None else None
    parts = [
        f"host_runtime_bridge_audit={audit_item.audit_status}",
        f"runtime_eventframe_bridge={audit_item.runtime_eventframe_bridge_confirmed}",
        f"dispatch_adapter_only={audit_item.dispatch_adapter_only_confirmed}",
    ]
    if readiness_item is not None:
        parts.append(f"readiness={readiness_item.readiness_status}")
    return " ".join(parts)


def render_host_body_runtime_bridge_table(
    mappings: tuple[HostBodyEventToRuntimeFrameMappingRecord | dict[str, object], ...] | list[HostBodyEventToRuntimeFrameMappingRecord | dict[str, object]],
    dispatch_links: tuple[HostBodyRuntimeDispatchLinkRecord | dict[str, object], ...] | list[HostBodyRuntimeDispatchLinkRecord | dict[str, object]],
) -> str:
    rows = ["host_event | runtime_event_type | target_engine | dispatch_status"]
    links = tuple(_dispatch_link(item) for item in dispatch_links)
    for index, mapping in enumerate(tuple(_mapping(item) for item in mappings)):
        link_status = links[index].dispatch_link_status if index < len(links) else "missing"
        rows.append(
            f"{mapping.source_event_type} | {mapping.target_event_type} | "
            f"{mapping.target_engine_lane} | {link_status}"
        )
    return "\n".join(rows)


def _build_bridge_bundle(
    sensor_payload: dict[str, object],
    *,
    target_engine_lane: str | None = None,
    mapping_kwargs: dict[str, object] | None = None,
    bridge_kwargs: dict[str, object] | None = None,
    dispatch_kwargs: dict[str, object] | None = None,
    defer_dispatch_adapter: bool = False,
) -> dict[str, object]:
    sensor_audit = HostBodySensorEventAudit.from_dict(
        sensor_payload["host_body_sensor_event_audit"]
    )
    event_set = HostBodySensorEventSetRecord.from_dict(
        sensor_payload["host_body_sensor_event_set"]
    )
    plan = build_host_body_runtime_bridge_plan(
        host_sensor_event_audit=sensor_audit,
        source_host_body_port_map_id=event_set.source_host_body_port_map_id,
    )
    host_events = tuple(
        HostBodyEventRecord.from_dict(item)
        for item in sensor_payload["host_body_events"]
    )
    mappings: list[HostBodyEventToRuntimeFrameMappingRecord] = []
    bridges: list[HostBodyRuntimeEventFrameBridgeRecord] = []
    runtime_frames: list[RuntimeEventFrameRecord] = []
    links: list[HostBodyRuntimeDispatchLinkRecord] = []
    for event in host_events:
        mapping = map_host_body_event_to_runtime_eventframe(
            bridge_plan=plan,
            host_body_event=event,
            target_engine_lane=target_engine_lane,
            **(mapping_kwargs or {}),
        )
        bridge, runtime_frame = build_host_body_runtime_eventframe_bridge(
            mapping=mapping,
            **(bridge_kwargs or {}),
        )
        link = build_host_body_runtime_dispatch_link(
            eventframe_bridge=bridge,
            defer_dispatch_adapter=defer_dispatch_adapter,
            **(dispatch_kwargs or {}),
        )
        mappings.append(mapping)
        bridges.append(bridge)
        if runtime_frame is not None:
            runtime_frames.append(runtime_frame)
        links.append(link)
    trace = build_host_body_runtime_bridge_trace(
        bridge_plan=plan,
        host_body_events=host_events,
        event_mappings=tuple(mappings),
        eventframe_bridges=tuple(bridges),
        dispatch_links=tuple(links),
    )
    audit = build_host_body_runtime_bridge_audit(
        host_sensor_event_audit=sensor_audit,
        bridge_plan=plan,
        bridge_trace=trace,
        event_mappings=tuple(mappings),
        eventframe_bridges=tuple(bridges),
        dispatch_links=tuple(links),
    )
    readiness = build_host_body_runtime_bridge_readiness(audit)
    return {
        "host_body_sensor_event_audit": sensor_audit.to_dict(),
        "host_body_runtime_bridge_plan": plan.to_dict(),
        "host_body_event_runtime_mappings": [item.to_dict() for item in mappings],
        "host_body_runtime_eventframe_bridges": [item.to_dict() for item in bridges],
        "runtime_event_frames": [item.to_dict() for item in runtime_frames],
        "host_body_runtime_dispatch_links": [item.to_dict() for item in links],
        "host_body_runtime_bridge_trace": trace.to_dict(),
        "host_body_runtime_bridge_audit": audit.to_dict(),
        "host_body_runtime_bridge_readiness": readiness.to_dict(),
        "rendered_host_body_runtime_bridge_summary": render_host_body_runtime_bridge_summary_text(
            audit, readiness
        ),
        "rendered_host_body_runtime_bridge_table": render_host_body_runtime_bridge_table(
            tuple(mappings),
            tuple(links),
        ),
    }


def _bridge_plan_status(
    *,
    audit: HostBodySensorEventAudit | None,
    allowed_source_event_families: tuple[str, ...],
    allowed_target_event_families: tuple[str, ...],
    allowed_target_engine_lanes: tuple[str, ...],
    real_hardware_allowed: bool,
    semantic_interpretation_allowed: bool,
    action_selection_allowed: bool,
    external_control_allowed: bool,
    memory_write_allowed: bool,
    automatic_learning_approval_allowed: bool,
    first_output_allowed: bool,
    live_runtime_session_allowed: bool,
    dynamic_scheduling_allowed: bool,
    live_engine_invocation_allowed: bool,
) -> str:
    if audit is None:
        return "blocked_missing_host_sensor_event_audit"
    if not set(allowed_source_event_families).issubset(ALLOWED_SOURCE_EVENT_FAMILIES):
        return "blocked_unapproved_source_event_family"
    if not set(allowed_target_event_families).issubset(ALLOWED_TARGET_EVENT_FAMILIES):
        return "blocked_unapproved_target_event_family"
    if not set(allowed_target_engine_lanes).issubset(ALLOWED_TARGET_ENGINE_LANES):
        return "blocked_forbidden_authority_detected"
    if real_hardware_allowed:
        return "blocked_real_hardware_allowed"
    if (
        semantic_interpretation_allowed
        or action_selection_allowed
        or external_control_allowed
        or memory_write_allowed
        or automatic_learning_approval_allowed
        or first_output_allowed
        or live_runtime_session_allowed
        or dynamic_scheduling_allowed
        or live_engine_invocation_allowed
    ):
        return "blocked_forbidden_authority_detected"
    return "bridge_plan_created"


def _target_for_host_family(event_family: str) -> tuple[str, str, str]:
    if event_family == "camera_low_level_event":
        return "host_camera_event", "sense_event", "sense_interface"
    if event_family == "mic_low_level_event":
        return "host_mic_event", "sense_event", "sense_interface"
    if event_family == "host_idle_event":
        return "host_idle_event", "runtime_event", "runtime"
    if event_family == "host_status_event":
        return "host_status_event", "state_event", "state_engine"
    return "unknown_host_event", "unknown_event", "none"


def _family_for_lane(default_family: str, lane: str) -> str:
    if lane == "sense_interface":
        return "sense_event"
    if lane == "runtime":
        return "runtime_event"
    if lane == "state_engine":
        return "state_event"
    return default_family


def _mapping_status(
    *,
    plan: HostBodyRuntimeBridgePlanRecord,
    event: HostBodyEventRecord,
    target_engine_lane: str,
    target_event_family: str,
    semantic_interpretation_created: bool,
    action_selection_influence_created: bool,
    external_control_created: bool,
    memory_write_performed: bool,
    automatic_learning_approval_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
) -> str:
    if event.event_family not in plan.allowed_source_event_families:
        return "blocked_unknown_host_event_family"
    if target_engine_lane in FORBIDDEN_TARGET_ENGINE_LANES or target_engine_lane not in (*ALLOWED_TARGET_ENGINE_LANES, "none"):
        return "blocked_forbidden_target_engine"
    if target_event_family not in plan.allowed_target_event_families:
        return "blocked_forbidden_target_engine"
    if (
        semantic_interpretation_created
        or event.semantic_vision_created
        or event.object_recognition_created
        or event.face_recognition_created
        or event.speech_recognition_created
        or event.speaker_identification_created
        or event.voice_command_created
        or event.language_understanding_created
    ):
        return "blocked_semantic_interpretation_detected"
    if action_selection_influence_created or event.action_selection_influence_created:
        return "blocked_action_selection_influence_detected"
    if (
        external_control_created
        or memory_write_performed
        or automatic_learning_approval_created
        or first_output_created
        or live_runtime_session_created
        or event.external_control_created
        or event.memory_layer_write_performed
        or event.automatic_learning_approval_created
        or event.first_output_created
        or event.live_runtime_session_created
    ):
        return "blocked_forbidden_authority_detected"
    if event.event_family == "camera_low_level_event" or event.event_family == "mic_low_level_event":
        return "host_event_mapped_to_sense_eventframe"
    if event.event_family == "host_idle_event":
        return "host_event_mapped_to_runtime_eventframe_idle"
    if event.event_family == "host_status_event":
        return "host_event_mapped_to_state_eventframe"
    return "host_event_mapped_to_runtime_eventframe"


def _eventframe_bridge_status(
    *,
    mapping: HostBodyEventToRuntimeFrameMappingRecord,
    dynamic_child_event_created: bool,
    live_runtime_session_created: bool,
    live_engine_invocation_created: bool,
    external_execution_created: bool,
    memory_layer_write_performed: bool,
    automatic_learning_approval_created: bool,
    first_output_created: bool,
    production_behavior_created: bool,
) -> str:
    if not mapping.mapping_status.startswith("host_event_mapped"):
        return "blocked_invalid_mapping"
    if live_runtime_session_created:
        return "blocked_live_runtime_detected"
    if dynamic_child_event_created:
        return "blocked_dynamic_child_event_detected"
    if (
        live_engine_invocation_created
        or external_execution_created
        or memory_layer_write_performed
        or automatic_learning_approval_created
        or first_output_created
        or production_behavior_created
    ):
        return "blocked_forbidden_authority_detected"
    if mapping.target_event_family == "sense_event":
        return "runtime_eventframe_bridge_created_for_sense_event"
    if mapping.target_event_family == "runtime_event":
        return "runtime_eventframe_bridge_created_for_idle_event"
    if mapping.target_event_family == "state_event":
        return "runtime_eventframe_bridge_created_for_state_event"
    return "runtime_eventframe_bridge_created"


def _dispatch_link_status(
    *,
    bridge: HostBodyRuntimeEventFrameBridgeRecord | None,
    defer_dispatch_adapter: bool,
    live_engine_invocation_created: bool,
    external_execution_created: bool,
    memory_layer_write_performed: bool,
    automatic_learning_approval_created: bool,
    first_output_created: bool,
    production_behavior_created: bool,
) -> str:
    if bridge is None or not bridge.bridge_status.startswith("runtime_eventframe_bridge_created"):
        return "blocked_missing_eventframe_bridge"
    if live_engine_invocation_created:
        return "blocked_live_engine_invocation_detected"
    if (
        external_execution_created
        or memory_layer_write_performed
        or automatic_learning_approval_created
        or first_output_created
        or production_behavior_created
    ):
        return "blocked_forbidden_authority_detected"
    if defer_dispatch_adapter:
        return "dispatch_link_deferred_missing_dispatch_adapter"
    if bridge.target_engine_lane == "sense_interface":
        return "dispatch_link_created_sense_adapter_only"
    if bridge.target_engine_lane == "runtime":
        return "dispatch_link_created_runtime_adapter_only"
    if bridge.target_engine_lane == "state_engine":
        return "dispatch_link_created_state_adapter_only"
    return "dispatch_link_created_adapter_only"


def _trace_status(
    plan: HostBodyRuntimeBridgePlanRecord | None,
    mappings: tuple[HostBodyEventToRuntimeFrameMappingRecord, ...],
    bridges: tuple[HostBodyRuntimeEventFrameBridgeRecord, ...],
    links: tuple[HostBodyRuntimeDispatchLinkRecord, ...],
    blocked: set[str],
) -> str:
    if plan is None or plan.bridge_plan_status != "bridge_plan_created":
        return "host_body_runtime_bridge_trace_blocked_missing_plan"
    if not mappings or any(not item.mapping_status.startswith("host_event_mapped") for item in mappings):
        return "host_body_runtime_bridge_trace_blocked_missing_mapping"
    if not bridges or any(not item.bridge_status.startswith("runtime_eventframe_bridge_created") for item in bridges):
        return "host_body_runtime_bridge_trace_blocked_missing_eventframe_bridge"
    if blocked:
        return "host_body_runtime_bridge_trace_blocked_forbidden_authority_detected"
    if any(item.dispatch_link_status == "dispatch_link_deferred_missing_dispatch_adapter" for item in links):
        return "host_body_runtime_bridge_trace_complete_with_deferred_dispatch"
    return "host_body_runtime_bridge_trace_complete"


def _trace_forbidden(
    host_items: tuple[HostBodyEventRecord, ...],
    mappings: tuple[HostBodyEventToRuntimeFrameMappingRecord, ...],
    bridges: tuple[HostBodyRuntimeEventFrameBridgeRecord, ...],
    links: tuple[HostBodyRuntimeDispatchLinkRecord, ...],
) -> set[str]:
    blocked: set[str] = set()
    for item in host_items:
        if not item.fixture_only:
            blocked.add("not_fixture_only")
        if not item.read_only_event:
            blocked.add("not_read_only")
        if item.real_hardware_event or item.real_camera_accessed or item.real_mic_accessed or item.camera_capture_started or item.mic_stream_started or item.image_frame_stored or item.audio_stored:
            blocked.add("real_hardware")
        if item.semantic_vision_created or item.object_recognition_created or item.face_recognition_created or item.speech_recognition_created or item.speaker_identification_created or item.voice_command_created or item.language_understanding_created:
            blocked.add("semantic")
        if item.action_selection_influence_created:
            blocked.add("action_selection")
        if item.external_control_created:
            blocked.add("external_control")
        if item.memory_layer_write_performed:
            blocked.add("memory_write")
        if item.automatic_learning_approval_created:
            blocked.add("automatic_learning_approval")
        if item.first_output_created:
            blocked.add("first_output")
        if item.live_runtime_session_created:
            blocked.add("live_runtime")
    for item in mappings:
        if item.semantic_interpretation_created:
            blocked.add("semantic")
        if item.action_selection_influence_created:
            blocked.add("action_selection")
        if item.external_control_created:
            blocked.add("external_control")
        if item.memory_write_performed:
            blocked.add("memory_write")
        if item.automatic_learning_approval_created:
            blocked.add("automatic_learning_approval")
        if item.first_output_created:
            blocked.add("first_output")
        if item.live_runtime_session_created:
            blocked.add("live_runtime")
    for item in bridges:
        if item.dynamic_child_event_created:
            blocked.add("dynamic_scheduling")
        if item.live_runtime_session_created:
            blocked.add("live_runtime")
        if item.live_engine_invocation_created:
            blocked.add("live_engine")
        if item.external_execution_created:
            blocked.add("external_control")
        if item.memory_layer_write_performed:
            blocked.add("memory_write")
        if item.automatic_learning_approval_created:
            blocked.add("automatic_learning_approval")
        if item.first_output_created:
            blocked.add("first_output")
        if item.production_behavior_created:
            blocked.add("production_behavior")
    for item in links:
        if item.live_engine_invocation_created:
            blocked.add("live_engine")
        if item.external_execution_created:
            blocked.add("external_control")
        if item.memory_layer_write_performed:
            blocked.add("memory_write")
        if item.automatic_learning_approval_created:
            blocked.add("automatic_learning_approval")
        if item.first_output_created:
            blocked.add("first_output")
        if item.production_behavior_created:
            blocked.add("production_behavior")
    return blocked


def _audit_reasons(
    *,
    sensor_audit: HostBodySensorEventAudit | None,
    plan: HostBodyRuntimeBridgePlanRecord | None,
    trace: HostBodyRuntimeBridgeTraceRecord | None,
    mappings: tuple[HostBodyEventToRuntimeFrameMappingRecord, ...],
    bridges: tuple[HostBodyRuntimeEventFrameBridgeRecord, ...],
    links: tuple[HostBodyRuntimeDispatchLinkRecord, ...],
    force_dynamic_scheduling: bool,
    force_autonomous_scheduler: bool,
    force_open_ended_loop: bool,
    force_thought_engine_behavior: bool,
) -> list[str]:
    reasons: list[str] = []
    if sensor_audit is None:
        reasons.append("missing_sensor_event_audit")
    elif not sensor_audit.audit_status.startswith("passed_"):
        if not sensor_audit.no_real_camera_access or not sensor_audit.no_real_mic_access:
            reasons.append("real_hardware")
        if not sensor_audit.no_semantic_vision or not sensor_audit.no_speech_recognition:
            reasons.append("semantic")
        if not sensor_audit.no_action_selection_influence:
            reasons.append("action_selection")
        if not sensor_audit.no_external_control:
            reasons.append("external_control")
        if not sensor_audit.no_memory_layer_write:
            reasons.append("memory_write")
        if not sensor_audit.no_first_output:
            reasons.append("first_output")
        if not sensor_audit.no_live_runtime_session:
            reasons.append("live_runtime")
    if plan is None or plan.bridge_plan_status != "bridge_plan_created":
        reasons.append("invalid_bridge_plan")
    for item in mappings:
        if not item.mapping_status.startswith("host_event_mapped"):
            reasons.append("invalid_event_mapping")
        if item.semantic_interpretation_created:
            reasons.append("semantic")
        if item.action_selection_influence_created:
            reasons.append("action_selection")
        if item.external_control_created:
            reasons.append("external_control")
        if item.memory_write_performed:
            reasons.append("memory_write")
        if item.automatic_learning_approval_created:
            reasons.append("automatic_learning_approval")
        if item.first_output_created:
            reasons.append("first_output")
        if item.live_runtime_session_created:
            reasons.append("live_runtime")
    for item in bridges:
        if not item.bridge_status.startswith("runtime_eventframe_bridge_created"):
            reasons.append("invalid_eventframe_bridge")
        if item.live_runtime_session_created:
            reasons.append("live_runtime")
        if item.dynamic_child_event_created:
            reasons.append("dynamic_scheduling")
        if item.live_engine_invocation_created:
            reasons.append("live_engine")
        if item.external_execution_created:
            reasons.append("external_control")
        if item.memory_layer_write_performed:
            reasons.append("memory_write")
        if item.automatic_learning_approval_created:
            reasons.append("automatic_learning_approval")
        if item.first_output_created:
            reasons.append("first_output")
        if item.production_behavior_created:
            reasons.append("production_behavior")
    for item in links:
        if not (
            item.dispatch_link_status.startswith("dispatch_link_created")
            or item.dispatch_link_status == "dispatch_link_deferred_missing_dispatch_adapter"
        ):
            reasons.append("invalid_dispatch_link")
        if item.live_engine_invocation_created:
            reasons.append("live_engine")
        if item.external_execution_created:
            reasons.append("external_control")
        if item.memory_layer_write_performed:
            reasons.append("memory_write")
        if item.automatic_learning_approval_created:
            reasons.append("automatic_learning_approval")
        if item.first_output_created:
            reasons.append("first_output")
        if item.production_behavior_created:
            reasons.append("production_behavior")
    if trace is None or not trace.bridge_trace_status.startswith("host_body_runtime_bridge_trace_complete"):
        reasons.append("invalid_bridge_trace")
    elif _trace_has_forbidden_boundary(trace):
        reasons.append("forbidden_trace")
    if force_dynamic_scheduling:
        reasons.append("dynamic_scheduling")
    if force_autonomous_scheduler:
        reasons.append("autonomous_scheduler")
    if force_open_ended_loop:
        reasons.append("open_ended_loop")
    if force_thought_engine_behavior:
        reasons.append("thought_engine_behavior")
    return list(dict.fromkeys(reasons))


def _bridge_audit_status(
    reasons: list[str],
    mappings: tuple[HostBodyEventToRuntimeFrameMappingRecord, ...],
    links: tuple[HostBodyRuntimeDispatchLinkRecord, ...],
) -> str:
    priority = (
        ("missing_sensor_event_audit", "blocked_missing_sensor_event_audit"),
        ("real_hardware", "blocked_real_hardware_access_detected"),
        ("semantic", "blocked_semantic_interpretation_detected"),
        ("action_selection", "blocked_action_selection_influence_detected"),
        ("external_control", "blocked_external_control_detected"),
        ("memory_write", "blocked_memory_write_detected"),
        ("first_output", "blocked_first_output_detected"),
        ("live_runtime", "blocked_live_runtime_detected"),
        ("live_engine", "blocked_live_engine_invocation_detected"),
        ("dynamic_scheduling", "blocked_dynamic_scheduling_detected"),
        ("invalid_bridge_plan", "blocked_invalid_bridge_plan"),
        ("invalid_event_mapping", "blocked_invalid_event_mapping"),
        ("invalid_eventframe_bridge", "blocked_invalid_eventframe_bridge"),
        ("invalid_dispatch_link", "blocked_invalid_dispatch_link"),
        ("autonomous_scheduler", "blocked_forbidden_authority_detected"),
        ("open_ended_loop", "blocked_forbidden_authority_detected"),
        ("thought_engine_behavior", "blocked_forbidden_authority_detected"),
        ("production_behavior", "blocked_forbidden_authority_detected"),
    )
    for reason, status in priority:
        if reason in reasons:
            return status
    if any(item.dispatch_link_status == "dispatch_link_deferred_missing_dispatch_adapter" for item in links):
        return "passed_host_body_runtime_bridge_with_deferred_dispatch"
    if len(mappings) == 1:
        only = mappings[0]
        if only.target_event_type == "host_camera_event":
            return "passed_camera_event_to_sense_eventframe_bridge"
        if only.target_event_type == "host_mic_event":
            return "passed_mic_event_to_sense_eventframe_bridge"
        if only.target_event_type == "host_idle_event":
            return "passed_idle_event_to_runtime_eventframe_bridge"
    return "passed_host_body_event_runtime_eventframe_bridge"


def _mapping_has_forbidden_boundary(item: HostBodyEventToRuntimeFrameMappingRecord) -> bool:
    return (
        item.semantic_interpretation_created
        or item.action_selection_influence_created
        or item.external_control_created
        or item.memory_write_performed
        or item.automatic_learning_approval_created
        or item.first_output_created
        or item.live_runtime_session_created
    )


def _eventframe_bridge_has_forbidden_boundary(item: HostBodyRuntimeEventFrameBridgeRecord) -> bool:
    return (
        item.dynamic_child_event_created
        or item.live_runtime_session_created
        or item.live_engine_invocation_created
        or item.external_execution_created
        or item.memory_layer_write_performed
        or item.automatic_learning_approval_created
        or item.first_output_created
        or item.production_behavior_created
    )


def _dispatch_link_has_forbidden_boundary(item: HostBodyRuntimeDispatchLinkRecord) -> bool:
    return (
        item.handler_invoked
        or item.live_engine_invocation_created
        or item.external_execution_created
        or item.memory_layer_write_performed
        or item.automatic_learning_approval_created
        or item.first_output_created
        or item.production_behavior_created
    )


def _trace_has_forbidden_boundary(item: HostBodyRuntimeBridgeTraceRecord) -> bool:
    return (
        item.real_hardware_accessed
        or item.semantic_interpretation_created
        or item.action_selection_influence_created
        or item.external_control_created
        or item.live_runtime_session_created
        or item.live_engine_invocation_created
        or item.memory_layer_write_performed
        or item.automatic_learning_approval_created
        or item.first_output_created
        or item.production_behavior_created
    )


def _bridge_plan_summary(status: str) -> str:
    if status == "bridge_plan_created":
        return "HostBodyEvent to Runtime EventFrame bridge plan created."
    return f"HostBodyEvent runtime bridge plan blocked: {status}."


def _mapping_summary(status: str, event_family: str, lane: str) -> str:
    if status.startswith("host_event_mapped"):
        return f"{event_family} mapped to bounded Runtime EventFrame lane {lane}."
    return f"{event_family} mapping blocked: {status}."


def _eventframe_bridge_summary(status: str, lane: str) -> str:
    if status.startswith("runtime_eventframe_bridge_created"):
        return f"Runtime EventFrame bridge created for {lane} lane."
    return f"Runtime EventFrame bridge blocked: {status}."


def _dispatch_link_summary(status: str) -> str:
    if status.startswith("dispatch_link_created"):
        return "Adapter-only dispatch link recorded for HostBodyEvent bridge."
    if status == "dispatch_link_deferred_missing_dispatch_adapter":
        return "Dispatch adapter helper deferred; no live handler invoked."
    return f"Dispatch link blocked: {status}."


def _trace_summary(status: str) -> str:
    if status == "host_body_runtime_bridge_trace_complete":
        return "HostBodyEvent runtime bridge trace complete."
    if status == "host_body_runtime_bridge_trace_complete_with_deferred_dispatch":
        return "HostBodyEvent runtime bridge trace complete with deferred dispatch links."
    return f"HostBodyEvent runtime bridge trace blocked: {status}."


def _readiness_summary(status: str) -> str:
    if status == "ready_for_unity_home_internal_space_surface_only":
        return "Ready only for read-only Unity Home internal-space event surface."
    return f"HostBody runtime bridge readiness blocked: {status}."


def _validation(valid: bool, errors: list[str], record_id: str, status: str) -> dict[str, object]:
    return {
        "valid": valid,
        "error_codes": tuple(errors),
        "record_id": record_id,
        "status": status,
    }


def _sensor_audit(value: HostBodySensorEventAudit | dict[str, object]) -> HostBodySensorEventAudit:
    return value if isinstance(value, HostBodySensorEventAudit) else HostBodySensorEventAudit.from_dict(value)


def _host_event(value: HostBodyEventRecord | dict[str, object]) -> HostBodyEventRecord:
    return value if isinstance(value, HostBodyEventRecord) else HostBodyEventRecord.from_dict(value)


def _plan(value: HostBodyRuntimeBridgePlanRecord | dict[str, object]) -> HostBodyRuntimeBridgePlanRecord:
    return value if isinstance(value, HostBodyRuntimeBridgePlanRecord) else HostBodyRuntimeBridgePlanRecord.from_dict(value)


def _mapping(
    value: HostBodyEventToRuntimeFrameMappingRecord | dict[str, object],
) -> HostBodyEventToRuntimeFrameMappingRecord:
    return value if isinstance(value, HostBodyEventToRuntimeFrameMappingRecord) else HostBodyEventToRuntimeFrameMappingRecord.from_dict(value)


def _eventframe_bridge(
    value: HostBodyRuntimeEventFrameBridgeRecord | dict[str, object],
) -> HostBodyRuntimeEventFrameBridgeRecord:
    return value if isinstance(value, HostBodyRuntimeEventFrameBridgeRecord) else HostBodyRuntimeEventFrameBridgeRecord.from_dict(value)


def _dispatch_link(
    value: HostBodyRuntimeDispatchLinkRecord | dict[str, object],
) -> HostBodyRuntimeDispatchLinkRecord:
    return value if isinstance(value, HostBodyRuntimeDispatchLinkRecord) else HostBodyRuntimeDispatchLinkRecord.from_dict(value)


def _trace(value: HostBodyRuntimeBridgeTraceRecord | dict[str, object]) -> HostBodyRuntimeBridgeTraceRecord:
    return value if isinstance(value, HostBodyRuntimeBridgeTraceRecord) else HostBodyRuntimeBridgeTraceRecord.from_dict(value)


def _audit(value: HostBodyRuntimeBridgeAudit | dict[str, object]) -> HostBodyRuntimeBridgeAudit:
    return value if isinstance(value, HostBodyRuntimeBridgeAudit) else HostBodyRuntimeBridgeAudit.from_dict(value)


def _readiness(
    value: HostBodyRuntimeBridgeReadinessRecord | dict[str, object],
) -> HostBodyRuntimeBridgeReadinessRecord:
    return value if isinstance(value, HostBodyRuntimeBridgeReadinessRecord) else HostBodyRuntimeBridgeReadinessRecord.from_dict(value)
