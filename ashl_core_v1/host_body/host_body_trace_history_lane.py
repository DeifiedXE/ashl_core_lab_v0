"""Read-only Host Body trace history lane records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.host_body.host_body_port_map import HostBodyPortMapRecord
from ashl_core_v1.host_body.host_body_runtime_bridge import (
    HostBodyEventToRuntimeFrameMappingRecord,
    HostBodyRuntimeBridgeAudit,
    HostBodyRuntimeBridgeTraceRecord,
    HostBodyRuntimeDispatchLinkRecord,
    HostBodyRuntimeEventFrameBridgeRecord,
    build_demo_mixed_host_body_runtime_bridge,
)
from ashl_core_v1.host_body.host_body_sensor_events import (
    HostBodyCameraEventRecord,
    HostBodyEventRecord,
    HostBodyIdleEventRecord,
    HostBodyMicEventRecord,
    HostBodySensorEventSetRecord,
    build_demo_mixed_host_sensor_event_set,
)
from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
    QingyinHomeHostEventSurfaceRecord,
    QingyinHomeInternalSpaceRenderRecord,
    QingyinHomeInternalSpaceSurfaceAudit,
    QingyinHomePortSurfaceRecord,
    QingyinHomeRuntimeBridgeSurfaceRecord,
    QingyinHomeStatusLightRecord,
    QingyinHomeTeacherObservedSurfaceRecord,
    build_demo_qingyin_home_internal_space_surface,
)


SOURCE_ENGINE = "host_body"

LANE_PLAN_SCHEMA_VERSION = "qingyin_host_body_trace_history_lane_plan_v0"
ENTRY_SCHEMA_VERSION = "qingyin_host_body_trace_history_entry_v0"
LANE_SCHEMA_VERSION = "qingyin_host_body_trace_history_lane_v0"
INDEX_SCHEMA_VERSION = "qingyin_host_body_trace_history_index_v0"
READBACK_SCHEMA_VERSION = "qingyin_host_body_trace_history_readback_v0"
RENDER_SCHEMA_VERSION = "qingyin_host_body_trace_history_render_v0"
AUDIT_SCHEMA_VERSION = "qingyin_host_body_trace_history_audit_v0"
READINESS_SCHEMA_VERSION = "qingyin_host_body_trace_history_readiness_v0"

LANE_NAME = "qingyin_host_body_trace_history_lane"
LANE_KIND = "read_only_host_body_history_lane"

ALLOWED_SOURCE_FAMILIES = (
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
)
ALLOWED_QUERY_MODES = (
    "recent_n_entries",
    "by_source_family",
    "by_event_type",
    "by_surface_kind",
    "by_bridge_status",
)
ALLOWED_RENDER_MODES = (
    "timeline_text_render",
    "compact_table_render",
    "json_snapshot_render",
    "recent_history_card_render",
)

SAFE_CLAIM = (
    "ASHL Core v1 can create a read-only Host Body trace history lane from "
    "existing HostBodyEvent, Runtime EventFrame bridge, Qingyin Home surface, "
    "status-light, teacher-observed, and render records."
)
BLOCKED_CLAIMS = (
    "no_memory_layer_write",
    "no_state_persistence_write",
    "no_file_persistence",
    "no_learning_candidate_creation",
    "no_action_selection_influence",
    "no_external_control",
    "no_first_output",
    "no_live_runtime_session",
    "not_memory",
)
READINESS_NEXT_PACKAGE = (
    "Package 106 / ASHL Core v1 Host Body Internal Action Choice Minimal v0"
)

FORBIDDEN_PAYLOAD_KEYS = (
    "raw_image",
    "raw_image_bytes",
    "image_bytes",
    "raw_audio",
    "raw_audio_bytes",
    "audio_bytes",
    "free_form_qingyin_output",
    "qingyin_output",
    "first_output",
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
class HostBodyTraceHistoryLanePlanRecord:
    trace_history_lane_plan_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_port_map_id: str | None
    source_home_surface_audit_id: str | None
    source_host_runtime_bridge_audit_id: str | None
    lane_name: str
    lane_kind: str
    allowed_source_families: tuple[str, ...]
    allowed_query_modes: tuple[str, ...]
    allowed_render_modes: tuple[str, ...]
    read_only_lane: bool
    demo_record_only: bool
    in_memory_only: bool
    memory_layer_write_allowed: bool
    long_term_memory_write_allowed: bool
    core_memory_write_allowed: bool
    archive_memory_write_allowed: bool
    anchor_write_allowed: bool
    state_persistence_write_allowed: bool
    retained_jsonl_write_allowed: bool
    file_write_allowed: bool
    learning_candidate_creation_allowed: bool
    action_selection_allowed: bool
    internal_action_choice_allowed: bool
    first_output_allowed: bool
    live_runtime_session_allowed: bool
    lane_plan_status: str
    lane_plan_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != LANE_PLAN_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_trace_history_lane_plan_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.lane_name != LANE_NAME:
            raise ValueError("lane_name must be qingyin_host_body_trace_history_lane")
        if self.lane_kind != LANE_KIND:
            raise ValueError("lane_kind must be read_only_host_body_history_lane")
        if self.lane_plan_status not in {
            "lane_plan_created",
            "blocked_missing_home_surface_audit",
            "blocked_missing_host_runtime_bridge_audit",
            "blocked_memory_write_allowed",
            "blocked_state_persistence_write_allowed",
            "blocked_file_write_allowed",
            "blocked_learning_candidate_creation_allowed",
            "blocked_action_selection_allowed",
            "blocked_first_output_allowed",
            "blocked_live_runtime_allowed",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown lane_plan_status: {self.lane_plan_status}")
        for name in (
            "allowed_source_families",
            "allowed_query_modes",
            "allowed_render_modes",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyTraceHistoryLanePlanRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyTraceHistoryEntryRecord:
    trace_history_entry_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_trace_history_lane_plan_id: str
    sequence_index: int
    source_record_id: str
    source_record_family: str
    source_record_kind: str
    source_event_type: str | None
    source_event_family: str | None
    source_port_kind: str | None
    source_surface_kind: str | None
    source_bridge_status: str | None
    entry_kind: str
    entry_status: str
    entry_summary: str
    entry_payload: dict[str, Any]
    read_only_entry: bool
    fixture_only_source: bool
    semantic_interpretation_created: bool
    action_selection_influence_created: bool
    memory_layer_write_performed: bool
    state_persistence_write_performed: bool
    file_write_performed: bool
    learning_candidate_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ENTRY_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_trace_history_entry_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.source_record_family not in ALLOWED_SOURCE_FAMILIES:
            if self.entry_status != "trace_history_entry_blocked_unknown_source_family":
                raise ValueError(f"unknown source_record_family: {self.source_record_family}")
        if self.entry_kind not in {
            "sensor_event_entry",
            "runtime_bridge_entry",
            "home_surface_entry",
            "status_light_entry",
            "teacher_observed_entry",
            "render_entry",
            "blocked_entry",
        }:
            raise ValueError(f"unknown entry_kind: {self.entry_kind}")
        if self.entry_status not in {
            "trace_history_entry_recorded",
            "trace_history_entry_recorded_fixture_only",
            "trace_history_entry_blocked_unknown_source_family",
            "trace_history_entry_blocked_semantic_interpretation",
            "trace_history_entry_blocked_action_selection",
            "trace_history_entry_blocked_memory_write",
            "trace_history_entry_blocked_file_write",
            "trace_history_entry_blocked_first_output",
            "trace_history_entry_blocked_live_runtime",
        }:
            raise ValueError(f"unknown entry_status: {self.entry_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyTraceHistoryEntryRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyTraceHistoryLaneRecord:
    trace_history_lane_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_trace_history_lane_plan_id: str
    trace_history_entry_ids: tuple[str, ...]
    lane_sequence_kind: str
    lane_status: str
    lane_summary: str
    entry_count: int
    sensor_event_entry_count: int
    runtime_bridge_entry_count: int
    home_surface_entry_count: int
    status_light_entry_count: int
    teacher_observed_entry_count: int
    render_entry_count: int
    entries_sorted_by_sequence: bool
    duplicate_sequence_detected: bool
    unknown_source_family_detected: bool
    read_only_lane: bool
    memory_layer_write_performed: bool
    state_persistence_write_performed: bool
    file_write_performed: bool
    learning_candidate_created: bool
    action_selection_influence_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != LANE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_trace_history_lane_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.lane_sequence_kind not in {
            "sequence_index_order",
            "created_at_order",
            "demo_fixture_order",
        }:
            raise ValueError(f"unknown lane_sequence_kind: {self.lane_sequence_kind}")
        if self.lane_status not in {
            "trace_history_lane_recorded",
            "trace_history_lane_recorded_empty",
            "trace_history_lane_blocked_duplicate_sequence",
            "trace_history_lane_blocked_unknown_source_family",
            "trace_history_lane_blocked_memory_write",
            "trace_history_lane_blocked_file_write",
            "trace_history_lane_blocked_first_output",
            "trace_history_lane_blocked_live_runtime",
        }:
            raise ValueError(f"unknown lane_status: {self.lane_status}")
        for name in ("trace_history_entry_ids", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyTraceHistoryLaneRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyTraceHistoryIndexRecord:
    trace_history_index_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_trace_history_lane_id: str
    index_kind: str
    entries_by_source_family: dict[str, list[str]]
    entries_by_event_type: dict[str, list[str]]
    entries_by_port_kind: dict[str, list[str]]
    entries_by_surface_kind: dict[str, list[str]]
    entries_by_bridge_status: dict[str, list[str]]
    index_status: str
    index_summary: str
    read_only_index: bool
    memory_layer_write_performed: bool
    file_write_performed: bool
    learning_candidate_created: bool
    action_selection_influence_created: bool
    first_output_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INDEX_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_trace_history_index_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.index_kind not in {
            "host_body_trace_history_read_only_index",
            "empty_trace_history_index",
            "blocked_index",
        }:
            raise ValueError(f"unknown index_kind: {self.index_kind}")
        if self.index_status not in {
            "trace_history_index_recorded",
            "trace_history_index_recorded_empty",
            "trace_history_index_blocked_invalid_lane",
            "trace_history_index_blocked_memory_write",
            "trace_history_index_blocked_file_write",
            "trace_history_index_blocked_first_output",
        }:
            raise ValueError(f"unknown index_status: {self.index_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyTraceHistoryIndexRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyTraceHistoryReadbackRecord:
    trace_history_readback_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_trace_history_lane_id: str
    source_trace_history_index_id: str | None
    readback_mode: str
    readback_query: dict[str, Any]
    matched_entry_ids: tuple[str, ...]
    matched_entry_count: int
    readback_status: str
    readback_summary: str
    read_only_readback: bool
    readback_is_memory_retrieval: bool
    readback_can_influence_action: bool
    readback_can_create_learning: bool
    readback_can_create_first_output: bool
    memory_layer_write_performed: bool
    state_persistence_write_performed: bool
    file_write_performed: bool
    learning_candidate_created: bool
    action_selection_influence_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READBACK_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_trace_history_readback_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.readback_mode not in {
            "recent_n_entries",
            "by_source_family",
            "by_event_type",
            "by_surface_kind",
            "by_bridge_status",
            "empty_readback",
        }:
            raise ValueError(f"unknown readback_mode: {self.readback_mode}")
        if self.readback_status not in {
            "trace_history_readback_recorded",
            "trace_history_readback_recorded_empty",
            "trace_history_readback_blocked_invalid_query",
            "trace_history_readback_blocked_memory_retrieval_claim",
            "trace_history_readback_blocked_action_influence",
            "trace_history_readback_blocked_learning_creation",
            "trace_history_readback_blocked_first_output",
        }:
            raise ValueError(f"unknown readback_status: {self.readback_status}")
        for name in ("matched_entry_ids", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyTraceHistoryReadbackRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyTraceHistoryRenderRecord:
    trace_history_render_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_trace_history_lane_id: str
    source_trace_history_readback_id: str | None
    render_kind: str
    render_payload: dict[str, Any]
    render_text: str
    render_entry_ids: tuple[str, ...]
    render_status: str
    render_summary: str
    read_only_render: bool
    file_written: bool
    network_output_created: bool
    screen_mutated: bool
    unity_runtime_mutated: bool
    first_output_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RENDER_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_trace_history_render_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.render_kind not in {
            "timeline_text_render",
            "compact_table_render",
            "json_snapshot_render",
            "recent_history_card_render",
            "empty_render",
            "blocked_render",
        }:
            raise ValueError(f"unknown render_kind: {self.render_kind}")
        if self.render_status not in {
            "trace_history_render_created",
            "trace_history_render_created_empty",
            "trace_history_render_blocked_invalid_lane",
            "trace_history_render_blocked_file_write",
            "trace_history_render_blocked_network_output",
            "trace_history_render_blocked_screen_mutation",
            "trace_history_render_blocked_first_output",
            "trace_history_render_blocked_production_behavior",
        }:
            raise ValueError(f"unknown render_status: {self.render_status}")
        for name in ("render_entry_ids", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyTraceHistoryRenderRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyTraceHistoryAudit:
    trace_history_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_trace_history_lane_plan_id: str | None
    source_trace_history_lane_id: str | None
    source_trace_history_index_id: str | None
    source_trace_history_readback_id: str | None
    source_trace_history_render_id: str | None
    lane_plan_valid: bool
    entries_valid: bool
    lane_valid: bool
    index_valid: bool
    readback_valid: bool
    render_valid: bool
    read_only_lane_confirmed: bool
    trace_history_not_memory_confirmed: bool
    in_memory_demo_only_confirmed: bool
    no_memory_layer_write: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_state_persistence_write: bool
    no_retained_jsonl_write: bool
    no_file_write: bool
    no_learning_candidate_creation: bool
    no_action_selection_influence: bool
    no_internal_action_choice_runtime: bool
    no_external_control: bool
    no_first_output: bool
    no_live_runtime_session: bool
    no_unity_runtime_mutation: bool
    no_production_behavior: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_trace_history_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.audit_status not in {
            "passed_host_body_trace_history_lane",
            "passed_empty_host_body_trace_history_lane",
            "passed_trace_history_readback_only",
            "blocked_missing_lane_plan",
            "blocked_invalid_entry",
            "blocked_invalid_lane",
            "blocked_invalid_index",
            "blocked_invalid_readback",
            "blocked_invalid_render",
            "blocked_memory_write_detected",
            "blocked_state_persistence_write_detected",
            "blocked_file_write_detected",
            "blocked_learning_candidate_creation_detected",
            "blocked_action_selection_influence_detected",
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
    def from_dict(cls, data: dict[str, object]) -> "HostBodyTraceHistoryAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyTraceHistoryReadinessRecord:
    trace_history_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_trace_history_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_internal_action_choice_only: bool
    ready_for_teacher_observed_host_body_cli: bool
    ready_for_runtime_state_persistence_binding: bool
    ready_for_memory_layer_write: bool
    ready_for_long_term_memory: bool
    ready_for_state_persistence_write: bool
    ready_for_file_persistence: bool
    ready_for_learning_candidate_creation: bool
    ready_for_action_selection_influence: bool
    ready_for_external_control: bool
    ready_for_first_output: bool
    ready_for_live_runtime_session: bool
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READINESS_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_trace_history_readiness_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.readiness_status not in {
            "ready_for_internal_action_choice_only",
            "ready_for_teacher_observed_host_body_cli_only",
            "ready_for_runtime_state_persistence_binding_only",
            "not_ready_missing_trace_history_audit",
            "not_ready_boundary_failure",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyTraceHistoryReadinessRecord":
        return cls(**dict(data))


def build_host_body_trace_history_lane_plan(
    *,
    host_body_port_map: HostBodyPortMapRecord | dict[str, object] | None,
    home_surface_audit: QingyinHomeInternalSpaceSurfaceAudit | dict[str, object] | None,
    host_runtime_bridge_audit: HostBodyRuntimeBridgeAudit | dict[str, object] | None,
    memory_layer_write_allowed: bool = False,
    long_term_memory_write_allowed: bool = False,
    core_memory_write_allowed: bool = False,
    archive_memory_write_allowed: bool = False,
    anchor_write_allowed: bool = False,
    state_persistence_write_allowed: bool = False,
    retained_jsonl_write_allowed: bool = False,
    file_write_allowed: bool = False,
    learning_candidate_creation_allowed: bool = False,
    action_selection_allowed: bool = False,
    internal_action_choice_allowed: bool = False,
    first_output_allowed: bool = False,
    live_runtime_session_allowed: bool = False,
) -> HostBodyTraceHistoryLanePlanRecord:
    port_map = _port_map(host_body_port_map) if host_body_port_map is not None else None
    home_audit = _home_audit(home_surface_audit) if home_surface_audit is not None else None
    bridge_audit = _bridge_audit(host_runtime_bridge_audit) if host_runtime_bridge_audit is not None else None
    status = _lane_plan_status(
        home_audit=home_audit,
        bridge_audit=bridge_audit,
        memory_layer_write_allowed=memory_layer_write_allowed,
        long_term_memory_write_allowed=long_term_memory_write_allowed,
        core_memory_write_allowed=core_memory_write_allowed,
        archive_memory_write_allowed=archive_memory_write_allowed,
        anchor_write_allowed=anchor_write_allowed,
        state_persistence_write_allowed=state_persistence_write_allowed,
        retained_jsonl_write_allowed=retained_jsonl_write_allowed,
        file_write_allowed=file_write_allowed,
        learning_candidate_creation_allowed=learning_candidate_creation_allowed,
        action_selection_allowed=action_selection_allowed,
        internal_action_choice_allowed=internal_action_choice_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
    )
    return HostBodyTraceHistoryLanePlanRecord(
        trace_history_lane_plan_id=f"host_body_trace_history_lane_plan:{_slug(status)}",
        schema_version=LANE_PLAN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_port_map_id=port_map.host_body_port_map_id if port_map else None,
        source_home_surface_audit_id=home_audit.home_surface_audit_id if home_audit else None,
        source_host_runtime_bridge_audit_id=bridge_audit.host_runtime_bridge_audit_id if bridge_audit else None,
        lane_name=LANE_NAME,
        lane_kind=LANE_KIND,
        allowed_source_families=ALLOWED_SOURCE_FAMILIES,
        allowed_query_modes=ALLOWED_QUERY_MODES,
        allowed_render_modes=ALLOWED_RENDER_MODES,
        read_only_lane=True,
        demo_record_only=True,
        in_memory_only=True,
        memory_layer_write_allowed=memory_layer_write_allowed,
        long_term_memory_write_allowed=long_term_memory_write_allowed,
        core_memory_write_allowed=core_memory_write_allowed,
        archive_memory_write_allowed=archive_memory_write_allowed,
        anchor_write_allowed=anchor_write_allowed,
        state_persistence_write_allowed=state_persistence_write_allowed,
        retained_jsonl_write_allowed=retained_jsonl_write_allowed,
        file_write_allowed=file_write_allowed,
        learning_candidate_creation_allowed=learning_candidate_creation_allowed,
        action_selection_allowed=action_selection_allowed,
        internal_action_choice_allowed=internal_action_choice_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
        lane_plan_status=status,
        lane_plan_summary=_lane_plan_summary(status),
        source_trace_refs=home_audit.source_trace_refs if home_audit else tuple(),
    )


def validate_host_body_trace_history_lane_plan(
    record: HostBodyTraceHistoryLanePlanRecord | dict[str, object],
) -> dict[str, object]:
    item = _plan(record)
    valid = item.lane_plan_status == "lane_plan_created" and _plan_constants_safe(item)
    reasons = [] if valid else [item.lane_plan_status]
    return {"valid": valid, "status": item.lane_plan_status, "reasons": reasons}


def build_host_body_trace_history_entry(
    *,
    lane_plan: HostBodyTraceHistoryLanePlanRecord | dict[str, object],
    sequence_index: int,
    source_record: object,
    source_record_family: str | None = None,
    source_record_kind: str | None = None,
    entry_payload: dict[str, Any] | None = None,
    semantic_interpretation_created: bool = False,
    action_selection_influence_created: bool = False,
    memory_layer_write_performed: bool = False,
    state_persistence_write_performed: bool = False,
    file_write_performed: bool = False,
    learning_candidate_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
    production_behavior_created: bool = False,
) -> HostBodyTraceHistoryEntryRecord:
    plan = _plan(lane_plan)
    metadata = _source_metadata(source_record, source_record_family, source_record_kind)
    payload = {
        "source_record_id": metadata["source_record_id"],
        "source_record_family": metadata["source_record_family"],
        "source_record_kind": metadata["source_record_kind"],
        "event_type": metadata["source_event_type"],
        "event_family": metadata["source_event_family"],
        "port_kind": metadata["source_port_kind"],
        "surface_kind": metadata["source_surface_kind"],
        "bridge_status": metadata["source_bridge_status"],
        "read_only": True,
        "fixture_only": metadata["fixture_only_source"],
    }
    if entry_payload:
        payload.update(dict(entry_payload))
    raw_payload_detected = _payload_has_forbidden_content(payload)
    status = _entry_status(
        source_family=metadata["source_record_family"],
        raw_payload_detected=raw_payload_detected,
        semantic_interpretation_created=semantic_interpretation_created,
        action_selection_influence_created=action_selection_influence_created,
        memory_layer_write_performed=memory_layer_write_performed,
        state_persistence_write_performed=state_persistence_write_performed,
        file_write_performed=file_write_performed,
        learning_candidate_created=learning_candidate_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        production_behavior_created=production_behavior_created,
        fixture_only_source=metadata["fixture_only_source"],
    )
    entry_kind = _entry_kind(metadata["source_record_family"], status)
    return HostBodyTraceHistoryEntryRecord(
        trace_history_entry_id=(
            f"host_body_trace_entry:{sequence_index:04d}:"
            f"{_slug(metadata['source_record_family'])}:{_slug(metadata['source_record_id'])}"
        ),
        schema_version=ENTRY_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_trace_history_lane_plan_id=plan.trace_history_lane_plan_id,
        sequence_index=sequence_index,
        source_record_id=metadata["source_record_id"],
        source_record_family=metadata["source_record_family"],
        source_record_kind=metadata["source_record_kind"],
        source_event_type=metadata["source_event_type"],
        source_event_family=metadata["source_event_family"],
        source_port_kind=metadata["source_port_kind"],
        source_surface_kind=metadata["source_surface_kind"],
        source_bridge_status=metadata["source_bridge_status"],
        entry_kind=entry_kind,
        entry_status=status,
        entry_summary=_entry_summary(status, metadata["source_record_family"]),
        entry_payload=payload,
        read_only_entry=True,
        fixture_only_source=metadata["fixture_only_source"],
        semantic_interpretation_created=semantic_interpretation_created or raw_payload_detected,
        action_selection_influence_created=action_selection_influence_created,
        memory_layer_write_performed=memory_layer_write_performed,
        state_persistence_write_performed=state_persistence_write_performed,
        file_write_performed=file_write_performed,
        learning_candidate_created=learning_candidate_created,
        first_output_created=first_output_created or _payload_has_qingyin_output(payload),
        live_runtime_session_created=live_runtime_session_created,
        production_behavior_created=production_behavior_created,
        source_trace_refs=metadata["source_trace_refs"],
    )


def validate_host_body_trace_history_entry(
    record: HostBodyTraceHistoryEntryRecord | dict[str, object],
) -> dict[str, object]:
    item = _entry(record)
    valid = item.entry_status.startswith("trace_history_entry_recorded") and not _entry_has_forbidden(item)
    reasons = [] if valid else [item.entry_status]
    return {"valid": valid, "status": item.entry_status, "reasons": reasons}


def build_host_body_trace_history_lane(
    *,
    lane_plan: HostBodyTraceHistoryLanePlanRecord | dict[str, object] | None,
    entries: tuple[HostBodyTraceHistoryEntryRecord | dict[str, object], ...] | list[HostBodyTraceHistoryEntryRecord | dict[str, object]],
    lane_sequence_kind: str = "sequence_index_order",
    sort_entries: bool = True,
    memory_layer_write_performed: bool = False,
    state_persistence_write_performed: bool = False,
    file_write_performed: bool = False,
    learning_candidate_created: bool = False,
    action_selection_influence_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyTraceHistoryLaneRecord:
    plan = _plan(lane_plan) if lane_plan is not None else None
    items = tuple(_entry(item) for item in entries)
    ordered = tuple(sorted(items, key=lambda item: item.sequence_index)) if sort_entries else items
    duplicate = len({item.sequence_index for item in items}) != len(items)
    unknown = any(
        item.source_record_family not in ALLOWED_SOURCE_FAMILIES
        or item.entry_status == "trace_history_entry_blocked_unknown_source_family"
        for item in items
    )
    entry_forbidden = _entries_have_forbidden(items)
    status = _lane_status(
        plan=plan,
        entries=items,
        duplicate=duplicate,
        unknown=unknown,
        memory_layer_write_performed=memory_layer_write_performed or entry_forbidden["memory"],
        state_persistence_write_performed=state_persistence_write_performed or entry_forbidden["state"],
        file_write_performed=file_write_performed or entry_forbidden["file"],
        learning_candidate_created=learning_candidate_created or entry_forbidden["learning"],
        action_selection_influence_created=action_selection_influence_created or entry_forbidden["action"],
        first_output_created=first_output_created or entry_forbidden["first_output"],
        live_runtime_session_created=live_runtime_session_created or entry_forbidden["live_runtime"],
    )
    source_refs = tuple(ref for item in ordered for ref in item.source_trace_refs)
    return HostBodyTraceHistoryLaneRecord(
        trace_history_lane_id=f"host_body_trace_history_lane:{_slug(status)}",
        schema_version=LANE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_trace_history_lane_plan_id=plan.trace_history_lane_plan_id if plan else "missing_lane_plan",
        trace_history_entry_ids=tuple(item.trace_history_entry_id for item in ordered),
        lane_sequence_kind=lane_sequence_kind,
        lane_status=status,
        lane_summary=_lane_summary(status),
        entry_count=len(items),
        sensor_event_entry_count=sum(1 for item in items if item.entry_kind == "sensor_event_entry"),
        runtime_bridge_entry_count=sum(1 for item in items if item.entry_kind == "runtime_bridge_entry"),
        home_surface_entry_count=sum(1 for item in items if item.entry_kind == "home_surface_entry"),
        status_light_entry_count=sum(1 for item in items if item.entry_kind == "status_light_entry"),
        teacher_observed_entry_count=sum(1 for item in items if item.entry_kind == "teacher_observed_entry"),
        render_entry_count=sum(1 for item in items if item.entry_kind == "render_entry"),
        entries_sorted_by_sequence=tuple(item.sequence_index for item in ordered) == tuple(sorted(item.sequence_index for item in items)),
        duplicate_sequence_detected=duplicate,
        unknown_source_family_detected=unknown,
        read_only_lane=True,
        memory_layer_write_performed=memory_layer_write_performed or entry_forbidden["memory"],
        state_persistence_write_performed=state_persistence_write_performed or entry_forbidden["state"],
        file_write_performed=file_write_performed or entry_forbidden["file"],
        learning_candidate_created=learning_candidate_created or entry_forbidden["learning"],
        action_selection_influence_created=action_selection_influence_created or entry_forbidden["action"],
        first_output_created=first_output_created or entry_forbidden["first_output"],
        live_runtime_session_created=live_runtime_session_created or entry_forbidden["live_runtime"],
        source_trace_refs=tuple(dict.fromkeys(source_refs)),
    )


def validate_host_body_trace_history_lane(
    record: HostBodyTraceHistoryLaneRecord | dict[str, object],
) -> dict[str, object]:
    item = _lane(record)
    valid = item.lane_status.startswith("trace_history_lane_recorded") and not _lane_has_forbidden(item)
    reasons = [] if valid else [item.lane_status]
    return {"valid": valid, "status": item.lane_status, "reasons": reasons}


def build_host_body_trace_history_index(
    *,
    lane: HostBodyTraceHistoryLaneRecord | dict[str, object],
    entries: tuple[HostBodyTraceHistoryEntryRecord | dict[str, object], ...] | list[HostBodyTraceHistoryEntryRecord | dict[str, object]] = tuple(),
    memory_layer_write_performed: bool = False,
    file_write_performed: bool = False,
    learning_candidate_created: bool = False,
    action_selection_influence_created: bool = False,
    first_output_created: bool = False,
) -> HostBodyTraceHistoryIndexRecord:
    lane_item = _lane(lane)
    entry_items = tuple(_entry(item) for item in entries)
    if not lane_item.lane_status.startswith("trace_history_lane_recorded"):
        status = "trace_history_index_blocked_invalid_lane"
    elif memory_layer_write_performed or learning_candidate_created or action_selection_influence_created:
        status = "trace_history_index_blocked_memory_write"
    elif file_write_performed:
        status = "trace_history_index_blocked_file_write"
    elif first_output_created:
        status = "trace_history_index_blocked_first_output"
    elif not entry_items:
        status = "trace_history_index_recorded_empty"
    else:
        status = "trace_history_index_recorded"
    return HostBodyTraceHistoryIndexRecord(
        trace_history_index_id=f"host_body_trace_history_index:{_slug(status)}",
        schema_version=INDEX_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_trace_history_lane_id=lane_item.trace_history_lane_id,
        index_kind="blocked_index" if status.startswith("trace_history_index_blocked") else (
            "empty_trace_history_index" if not entry_items else "host_body_trace_history_read_only_index"
        ),
        entries_by_source_family=_index_entries(entry_items, "source_record_family"),
        entries_by_event_type=_index_entries(entry_items, "source_event_type"),
        entries_by_port_kind=_index_entries(entry_items, "source_port_kind"),
        entries_by_surface_kind=_index_entries(entry_items, "source_surface_kind"),
        entries_by_bridge_status=_index_entries(entry_items, "source_bridge_status"),
        index_status=status,
        index_summary=_index_summary(status),
        read_only_index=True,
        memory_layer_write_performed=memory_layer_write_performed,
        file_write_performed=file_write_performed,
        learning_candidate_created=learning_candidate_created,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        source_trace_refs=lane_item.source_trace_refs,
    )


def validate_host_body_trace_history_index(
    record: HostBodyTraceHistoryIndexRecord | dict[str, object],
) -> dict[str, object]:
    item = _index(record)
    valid = item.index_status.startswith("trace_history_index_recorded") and not _index_has_forbidden(item)
    reasons = [] if valid else [item.index_status]
    return {"valid": valid, "status": item.index_status, "reasons": reasons}


def build_host_body_trace_history_readback(
    *,
    lane: HostBodyTraceHistoryLaneRecord | dict[str, object],
    entries: tuple[HostBodyTraceHistoryEntryRecord | dict[str, object], ...] | list[HostBodyTraceHistoryEntryRecord | dict[str, object]],
    index: HostBodyTraceHistoryIndexRecord | dict[str, object] | None = None,
    readback_mode: str = "recent_n_entries",
    readback_query: dict[str, Any] | None = None,
    readback_is_memory_retrieval: bool = False,
    readback_can_influence_action: bool = False,
    readback_can_create_learning: bool = False,
    readback_can_create_first_output: bool = False,
    memory_layer_write_performed: bool = False,
    state_persistence_write_performed: bool = False,
    file_write_performed: bool = False,
    learning_candidate_created: bool = False,
    action_selection_influence_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyTraceHistoryReadbackRecord:
    lane_item = _lane(lane)
    entry_items = tuple(sorted((_entry(item) for item in entries), key=lambda item: item.sequence_index))
    index_item = _index(index) if index is not None else None
    query = dict(readback_query or {})
    matched, invalid_query = _readback_matches(readback_mode, query, entry_items)
    status = _readback_status(
        lane=lane_item,
        invalid_query=invalid_query,
        matched=matched,
        readback_is_memory_retrieval=readback_is_memory_retrieval,
        readback_can_influence_action=readback_can_influence_action,
        readback_can_create_learning=readback_can_create_learning,
        readback_can_create_first_output=readback_can_create_first_output,
        memory_layer_write_performed=memory_layer_write_performed,
        state_persistence_write_performed=state_persistence_write_performed,
        file_write_performed=file_write_performed,
        learning_candidate_created=learning_candidate_created,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    return HostBodyTraceHistoryReadbackRecord(
        trace_history_readback_id=f"host_body_trace_history_readback:{_slug(readback_mode)}:{_slug(status)}",
        schema_version=READBACK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_trace_history_lane_id=lane_item.trace_history_lane_id,
        source_trace_history_index_id=index_item.trace_history_index_id if index_item else None,
        readback_mode=readback_mode if readback_mode in {
            "recent_n_entries",
            "by_source_family",
            "by_event_type",
            "by_surface_kind",
            "by_bridge_status",
            "empty_readback",
        } else "empty_readback",
        readback_query=query,
        matched_entry_ids=tuple(item.trace_history_entry_id for item in matched),
        matched_entry_count=len(matched),
        readback_status=status,
        readback_summary=_readback_summary(status, readback_mode, len(matched)),
        read_only_readback=True,
        readback_is_memory_retrieval=readback_is_memory_retrieval,
        readback_can_influence_action=readback_can_influence_action,
        readback_can_create_learning=readback_can_create_learning,
        readback_can_create_first_output=readback_can_create_first_output,
        memory_layer_write_performed=memory_layer_write_performed,
        state_persistence_write_performed=state_persistence_write_performed,
        file_write_performed=file_write_performed,
        learning_candidate_created=learning_candidate_created or readback_can_create_learning,
        action_selection_influence_created=action_selection_influence_created or readback_can_influence_action,
        first_output_created=first_output_created or readback_can_create_first_output,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=lane_item.source_trace_refs,
    )


def validate_host_body_trace_history_readback(
    record: HostBodyTraceHistoryReadbackRecord | dict[str, object],
) -> dict[str, object]:
    item = _readback(record)
    valid = item.readback_status.startswith("trace_history_readback_recorded") and not _readback_has_forbidden(item)
    reasons = [] if valid else [item.readback_status]
    return {"valid": valid, "status": item.readback_status, "reasons": reasons}


def build_host_body_trace_history_render(
    *,
    lane: HostBodyTraceHistoryLaneRecord | dict[str, object],
    entries: tuple[HostBodyTraceHistoryEntryRecord | dict[str, object], ...] | list[HostBodyTraceHistoryEntryRecord | dict[str, object]] = tuple(),
    readback: HostBodyTraceHistoryReadbackRecord | dict[str, object] | None = None,
    render_kind: str = "timeline_text_render",
    file_written: bool = False,
    network_output_created: bool = False,
    screen_mutated: bool = False,
    unity_runtime_mutated: bool = False,
    first_output_created: bool = False,
    production_behavior_created: bool = False,
) -> HostBodyTraceHistoryRenderRecord:
    lane_item = _lane(lane)
    entry_items = tuple(sorted((_entry(item) for item in entries), key=lambda item: item.sequence_index))
    readback_item = _readback(readback) if readback is not None else None
    selected = _render_selected_entries(entry_items, readback_item)
    status = _render_status(
        lane=lane_item,
        selected=selected,
        file_written=file_written,
        network_output_created=network_output_created,
        screen_mutated=screen_mutated,
        unity_runtime_mutated=unity_runtime_mutated,
        first_output_created=first_output_created,
        production_behavior_created=production_behavior_created,
    )
    actual_kind = render_kind if status.startswith("trace_history_render_created") else "blocked_render"
    if status == "trace_history_render_created_empty":
        actual_kind = "empty_render"
    rows = [_entry_render_row(item) for item in selected]
    text = _render_text(actual_kind, rows)
    return HostBodyTraceHistoryRenderRecord(
        trace_history_render_id=f"host_body_trace_history_render:{_slug(actual_kind)}:{_slug(status)}",
        schema_version=RENDER_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_trace_history_lane_id=lane_item.trace_history_lane_id,
        source_trace_history_readback_id=readback_item.trace_history_readback_id if readback_item else None,
        render_kind=actual_kind,
        render_payload={"rows": rows, "entry_count": len(rows), "read_only": True},
        render_text=text,
        render_entry_ids=tuple(item.trace_history_entry_id for item in selected),
        render_status=status,
        render_summary=_render_summary(status),
        read_only_render=True,
        file_written=file_written,
        network_output_created=network_output_created,
        screen_mutated=screen_mutated,
        unity_runtime_mutated=unity_runtime_mutated,
        first_output_created=first_output_created,
        production_behavior_created=production_behavior_created,
        source_trace_refs=lane_item.source_trace_refs,
    )


def validate_host_body_trace_history_render(
    record: HostBodyTraceHistoryRenderRecord | dict[str, object],
) -> dict[str, object]:
    item = _render(record)
    valid = item.render_status.startswith("trace_history_render_created") and not _render_has_forbidden(item)
    reasons = [] if valid else [item.render_status]
    return {"valid": valid, "status": item.render_status, "reasons": reasons}


def build_host_body_trace_history_audit(
    *,
    lane_plan: HostBodyTraceHistoryLanePlanRecord | dict[str, object] | None,
    entries: tuple[HostBodyTraceHistoryEntryRecord | dict[str, object], ...] | list[HostBodyTraceHistoryEntryRecord | dict[str, object]] = tuple(),
    lane: HostBodyTraceHistoryLaneRecord | dict[str, object] | None = None,
    index: HostBodyTraceHistoryIndexRecord | dict[str, object] | None = None,
    readback: HostBodyTraceHistoryReadbackRecord | dict[str, object] | None = None,
    render: HostBodyTraceHistoryRenderRecord | dict[str, object] | None = None,
    force_memory_layer_write: bool = False,
    force_core_memory_write: bool = False,
    force_long_term_memory_write: bool = False,
    force_archive_memory_write: bool = False,
    force_anchor_write: bool = False,
    force_state_persistence_write: bool = False,
    force_retained_jsonl_write: bool = False,
    force_file_write: bool = False,
    force_learning_candidate_creation: bool = False,
    force_action_selection_influence: bool = False,
    force_internal_action_choice_runtime: bool = False,
    force_external_control: bool = False,
    force_first_output: bool = False,
    force_live_runtime_session: bool = False,
    force_unity_runtime_mutation: bool = False,
    force_production_behavior: bool = False,
) -> HostBodyTraceHistoryAudit:
    plan = _plan(lane_plan) if lane_plan is not None else None
    entry_items = tuple(_entry(item) for item in entries)
    lane_item = _lane(lane) if lane is not None else None
    index_item = _index(index) if index is not None else None
    readback_item = _readback(readback) if readback is not None else None
    render_item = _render(render) if render is not None else None
    reasons = _audit_reasons(
        plan=plan,
        entries=entry_items,
        lane=lane_item,
        index=index_item,
        readback=readback_item,
        render=render_item,
        force_memory_layer_write=force_memory_layer_write,
        force_core_memory_write=force_core_memory_write,
        force_long_term_memory_write=force_long_term_memory_write,
        force_archive_memory_write=force_archive_memory_write,
        force_anchor_write=force_anchor_write,
        force_state_persistence_write=force_state_persistence_write,
        force_retained_jsonl_write=force_retained_jsonl_write,
        force_file_write=force_file_write,
        force_learning_candidate_creation=force_learning_candidate_creation,
        force_action_selection_influence=force_action_selection_influence,
        force_internal_action_choice_runtime=force_internal_action_choice_runtime,
        force_external_control=force_external_control,
        force_first_output=force_first_output,
        force_live_runtime_session=force_live_runtime_session,
        force_unity_runtime_mutation=force_unity_runtime_mutation,
        force_production_behavior=force_production_behavior,
    )
    status = _audit_status(reasons, lane_item, readback_item, render_item)
    return HostBodyTraceHistoryAudit(
        trace_history_audit_id=f"host_body_trace_history_audit:{_slug(status)}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_trace_history_lane_plan_id=plan.trace_history_lane_plan_id if plan else None,
        source_trace_history_lane_id=lane_item.trace_history_lane_id if lane_item else None,
        source_trace_history_index_id=index_item.trace_history_index_id if index_item else None,
        source_trace_history_readback_id=readback_item.trace_history_readback_id if readback_item else None,
        source_trace_history_render_id=render_item.trace_history_render_id if render_item else None,
        lane_plan_valid=plan is not None and plan.lane_plan_status == "lane_plan_created",
        entries_valid=all(item.entry_status.startswith("trace_history_entry_recorded") for item in entry_items),
        lane_valid=lane_item is not None and lane_item.lane_status.startswith("trace_history_lane_recorded"),
        index_valid=index_item is None or index_item.index_status.startswith("trace_history_index_recorded"),
        readback_valid=readback_item is None or readback_item.readback_status.startswith("trace_history_readback_recorded"),
        render_valid=render_item is None or render_item.render_status.startswith("trace_history_render_created"),
        read_only_lane_confirmed=True,
        trace_history_not_memory_confirmed=True,
        in_memory_demo_only_confirmed=True,
        no_memory_layer_write="memory_write" not in reasons,
        no_core_memory_write="core_memory_write" not in reasons,
        no_long_term_memory_write="long_term_memory_write" not in reasons,
        no_archive_memory_write="archive_memory_write" not in reasons,
        no_anchor_write="anchor_write" not in reasons,
        no_state_persistence_write="state_persistence" not in reasons,
        no_retained_jsonl_write="retained_jsonl" not in reasons,
        no_file_write="file_write" not in reasons,
        no_learning_candidate_creation="learning_candidate" not in reasons,
        no_action_selection_influence="action_selection" not in reasons,
        no_internal_action_choice_runtime="internal_action_choice" not in reasons,
        no_external_control="external_control" not in reasons,
        no_first_output="first_output" not in reasons,
        no_live_runtime_session="live_runtime" not in reasons,
        no_unity_runtime_mutation="unity_runtime_mutation" not in reasons,
        no_production_behavior="production_behavior" not in reasons,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(reasons),
        source_trace_refs=lane_item.source_trace_refs if lane_item else tuple(),
    )


def validate_host_body_trace_history_audit(
    record: HostBodyTraceHistoryAudit | dict[str, object],
) -> dict[str, object]:
    item = _audit(record)
    valid = item.audit_status.startswith("passed_")
    reasons = [] if valid else list(item.blocked_reasons or (item.audit_status,))
    return {"valid": valid, "status": item.audit_status, "reasons": reasons}


def build_host_body_trace_history_readiness(
    trace_history_audit: HostBodyTraceHistoryAudit | dict[str, object],
) -> HostBodyTraceHistoryReadinessRecord:
    audit = _audit(trace_history_audit)
    passed = audit.audit_status.startswith("passed_")
    if passed:
        status = "ready_for_internal_action_choice_only"
    elif audit.source_trace_history_lane_plan_id is None:
        status = "not_ready_missing_trace_history_audit"
    elif audit.audit_status.startswith("blocked_"):
        status = "blocked_forbidden_authority_detected"
    else:
        status = "not_ready_boundary_failure"
    return HostBodyTraceHistoryReadinessRecord(
        trace_history_readiness_id=f"host_body_trace_history_readiness:{audit.trace_history_audit_id}",
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_trace_history_audit_id=audit.trace_history_audit_id,
        current_verified_capability=SAFE_CLAIM,
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason="Create internal-only Host Body action choice records.",
        ready_for_internal_action_choice_only=passed,
        ready_for_teacher_observed_host_body_cli=passed,
        ready_for_runtime_state_persistence_binding=passed,
        ready_for_memory_layer_write=False,
        ready_for_long_term_memory=False,
        ready_for_state_persistence_write=False,
        ready_for_file_persistence=False,
        ready_for_learning_candidate_creation=False,
        ready_for_action_selection_influence=False,
        ready_for_external_control=False,
        ready_for_first_output=False,
        ready_for_live_runtime_session=False,
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=audit.source_trace_refs,
    )


def validate_host_body_trace_history_readiness(
    record: HostBodyTraceHistoryReadinessRecord | dict[str, object],
) -> dict[str, object]:
    item = _readiness(record)
    valid = item.readiness_status.startswith("ready_for_")
    reasons = [] if valid else [item.readiness_status]
    return {"valid": valid, "status": item.readiness_status, "reasons": reasons}


def build_demo_full_host_body_trace_history_lane() -> dict[str, object]:
    return _build_trace_history_bundle()


def build_demo_empty_host_body_trace_history_lane() -> dict[str, object]:
    return _build_trace_history_bundle(empty=True)


def build_demo_recent_n_trace_history_readback() -> dict[str, object]:
    return _build_trace_history_bundle(
        readback_mode="recent_n_entries",
        readback_query={"n": 3},
        readback_only=True,
    )


def build_demo_source_family_trace_history_readback() -> dict[str, object]:
    return _build_trace_history_bundle(
        readback_mode="by_source_family",
        readback_query={"source_family": "host_body_event"},
        readback_only=True,
    )


def build_demo_blocked_memory_write_trace_history() -> dict[str, object]:
    return _build_trace_history_bundle(entry_kwargs={"memory_layer_write_performed": True})


def build_demo_blocked_state_persistence_write_trace_history() -> dict[str, object]:
    return _build_trace_history_bundle(entry_kwargs={"state_persistence_write_performed": True})


def build_demo_blocked_first_output_trace_history() -> dict[str, object]:
    return _build_trace_history_bundle(render_kwargs={"first_output_created": True})


def build_demo_blocked_action_influence_trace_history() -> dict[str, object]:
    return _build_trace_history_bundle(entry_kwargs={"action_selection_influence_created": True})


def build_demo_blocked_file_write_trace_history() -> dict[str, object]:
    return _build_trace_history_bundle(render_kwargs={"file_written": True})


def render_host_body_trace_history_summary_text(
    audit: HostBodyTraceHistoryAudit | dict[str, object],
    readiness: HostBodyTraceHistoryReadinessRecord | dict[str, object] | None = None,
) -> str:
    audit_item = _audit(audit)
    readiness_item = _readiness(readiness) if readiness is not None else None
    parts = [
        f"host_body_trace_history_audit={audit_item.audit_status}",
        f"read_only={audit_item.read_only_lane_confirmed}",
        f"not_memory={audit_item.trace_history_not_memory_confirmed}",
    ]
    if readiness_item is not None:
        parts.append(f"readiness={readiness_item.readiness_status}")
    return " ".join(parts)


def render_host_body_trace_history_timeline_text(
    entries: tuple[HostBodyTraceHistoryEntryRecord | dict[str, object], ...] | list[HostBodyTraceHistoryEntryRecord | dict[str, object]],
) -> str:
    lines = ["seq | source_family | event_type | surface_kind | bridge_status"]
    for item in sorted((_entry(entry) for entry in entries), key=lambda entry: entry.sequence_index):
        lines.append(
            f"{item.sequence_index:03d} | {item.source_record_family} | "
            f"{item.source_event_type or '-'} | {item.source_surface_kind or '-'} | "
            f"{item.source_bridge_status or '-'}"
        )
    return "\n".join(lines)


def render_host_body_trace_history_table(
    entries: tuple[HostBodyTraceHistoryEntryRecord | dict[str, object], ...] | list[HostBodyTraceHistoryEntryRecord | dict[str, object]],
) -> str:
    lines = ["entry_id | kind | status"]
    for item in sorted((_entry(entry) for entry in entries), key=lambda entry: entry.sequence_index):
        lines.append(f"{item.trace_history_entry_id} | {item.entry_kind} | {item.entry_status}")
    return "\n".join(lines)


def _build_trace_history_bundle(
    *,
    empty: bool = False,
    readback_mode: str = "recent_n_entries",
    readback_query: dict[str, Any] | None = None,
    readback_only: bool = False,
    plan_kwargs: dict[str, object] | None = None,
    entry_kwargs: dict[str, object] | None = None,
    lane_kwargs: dict[str, object] | None = None,
    index_kwargs: dict[str, object] | None = None,
    readback_kwargs: dict[str, object] | None = None,
    render_kwargs: dict[str, object] | None = None,
    audit_kwargs: dict[str, object] | None = None,
) -> dict[str, object]:
    sensor_payload = build_demo_mixed_host_sensor_event_set()
    bridge_payload = build_demo_mixed_host_body_runtime_bridge()
    home_payload = build_demo_qingyin_home_internal_space_surface()
    port_map = HostBodyPortMapRecord.from_dict(sensor_payload["host_body_port_map"])
    bridge_audit = HostBodyRuntimeBridgeAudit.from_dict(bridge_payload["host_body_runtime_bridge_audit"])
    home_audit = QingyinHomeInternalSpaceSurfaceAudit.from_dict(home_payload["home_internal_space_surface_audit"])
    plan = build_host_body_trace_history_lane_plan(
        host_body_port_map=port_map,
        home_surface_audit=home_audit,
        host_runtime_bridge_audit=bridge_audit,
        **(plan_kwargs or {}),
    )
    source_records = [] if empty else _demo_source_records(sensor_payload, bridge_payload, home_payload)
    entries = []
    for index, source_record in enumerate(source_records):
        kwargs = entry_kwargs if index == 0 and entry_kwargs else {}
        entries.append(
            build_host_body_trace_history_entry(
                lane_plan=plan,
                sequence_index=index,
                source_record=source_record,
                **kwargs,
            )
        )
    lane = build_host_body_trace_history_lane(
        lane_plan=plan,
        entries=entries,
        **(lane_kwargs or {}),
    )
    index_record = build_host_body_trace_history_index(
        lane=lane,
        entries=entries,
        **(index_kwargs or {}),
    )
    readback = build_host_body_trace_history_readback(
        lane=lane,
        entries=entries,
        index=index_record,
        readback_mode="empty_readback" if empty else readback_mode,
        readback_query=readback_query or {"n": 5},
        **(readback_kwargs or {}),
    )
    render = None
    if not readback_only:
        render = build_host_body_trace_history_render(
            lane=lane,
            entries=entries,
            readback=readback,
            **(render_kwargs or {}),
        )
    audit = build_host_body_trace_history_audit(
        lane_plan=plan,
        entries=entries,
        lane=lane,
        index=index_record,
        readback=readback,
        render=render,
        **(audit_kwargs or {}),
    )
    readiness = build_host_body_trace_history_readiness(audit)
    payload: dict[str, object] = {
        "trace_history_lane_plan": plan.to_dict(),
        "trace_history_entries": [item.to_dict() for item in entries],
        "trace_history_lane": lane.to_dict(),
        "trace_history_index": index_record.to_dict(),
        "trace_history_readback": readback.to_dict(),
        "trace_history_audit": audit.to_dict(),
        "trace_history_readiness": readiness.to_dict(),
        "rendered_trace_history_summary": render_host_body_trace_history_summary_text(audit, readiness),
        "rendered_trace_history_timeline": render_host_body_trace_history_timeline_text(entries),
        "rendered_trace_history_table": render_host_body_trace_history_table(entries),
    }
    if render is not None:
        payload["trace_history_render"] = render.to_dict()
    return payload


def _demo_source_records(
    sensor_payload: dict[str, object],
    bridge_payload: dict[str, object],
    home_payload: dict[str, object],
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    records.extend(sensor_payload["host_body_events"])
    records.extend(sensor_payload["host_body_camera_events"])
    records.extend(sensor_payload["host_body_mic_events"])
    records.extend(sensor_payload["host_body_idle_events"])
    records.append(sensor_payload["host_body_sensor_event_set"])
    records.append(bridge_payload["host_body_runtime_bridge_trace"])
    records.extend(bridge_payload["host_body_runtime_eventframe_bridges"])
    records.extend(bridge_payload["host_body_runtime_dispatch_links"])
    records.append(home_payload["home_port_surface"])
    records.append(home_payload["home_host_event_surface"])
    records.append(home_payload["home_runtime_bridge_surface"])
    records.extend(home_payload["home_status_lights"])
    records.append(home_payload["home_teacher_observed_surface"])
    records.append(home_payload["home_internal_space_render"])
    return records


def _lane_plan_status(
    *,
    home_audit: QingyinHomeInternalSpaceSurfaceAudit | None,
    bridge_audit: HostBodyRuntimeBridgeAudit | None,
    memory_layer_write_allowed: bool,
    long_term_memory_write_allowed: bool,
    core_memory_write_allowed: bool,
    archive_memory_write_allowed: bool,
    anchor_write_allowed: bool,
    state_persistence_write_allowed: bool,
    retained_jsonl_write_allowed: bool,
    file_write_allowed: bool,
    learning_candidate_creation_allowed: bool,
    action_selection_allowed: bool,
    internal_action_choice_allowed: bool,
    first_output_allowed: bool,
    live_runtime_session_allowed: bool,
) -> str:
    if home_audit is None:
        return "blocked_missing_home_surface_audit"
    if bridge_audit is None:
        return "blocked_missing_host_runtime_bridge_audit"
    if memory_layer_write_allowed or long_term_memory_write_allowed or core_memory_write_allowed or archive_memory_write_allowed or anchor_write_allowed:
        return "blocked_memory_write_allowed"
    if state_persistence_write_allowed:
        return "blocked_state_persistence_write_allowed"
    if retained_jsonl_write_allowed or file_write_allowed:
        return "blocked_file_write_allowed"
    if learning_candidate_creation_allowed:
        return "blocked_learning_candidate_creation_allowed"
    if action_selection_allowed:
        return "blocked_action_selection_allowed"
    if first_output_allowed:
        return "blocked_first_output_allowed"
    if live_runtime_session_allowed:
        return "blocked_live_runtime_allowed"
    if internal_action_choice_allowed:
        return "blocked_forbidden_authority_detected"
    return "lane_plan_created"


def _entry_status(
    *,
    source_family: str,
    raw_payload_detected: bool,
    semantic_interpretation_created: bool,
    action_selection_influence_created: bool,
    memory_layer_write_performed: bool,
    state_persistence_write_performed: bool,
    file_write_performed: bool,
    learning_candidate_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
    production_behavior_created: bool,
    fixture_only_source: bool,
) -> str:
    if source_family not in ALLOWED_SOURCE_FAMILIES:
        return "trace_history_entry_blocked_unknown_source_family"
    if raw_payload_detected or semantic_interpretation_created:
        return "trace_history_entry_blocked_semantic_interpretation"
    if action_selection_influence_created:
        return "trace_history_entry_blocked_action_selection"
    if memory_layer_write_performed or state_persistence_write_performed or learning_candidate_created:
        return "trace_history_entry_blocked_memory_write"
    if file_write_performed:
        return "trace_history_entry_blocked_file_write"
    if first_output_created or production_behavior_created:
        return "trace_history_entry_blocked_first_output"
    if live_runtime_session_created:
        return "trace_history_entry_blocked_live_runtime"
    return "trace_history_entry_recorded_fixture_only" if fixture_only_source else "trace_history_entry_recorded"


def _lane_status(
    *,
    plan: HostBodyTraceHistoryLanePlanRecord | None,
    entries: tuple[HostBodyTraceHistoryEntryRecord, ...],
    duplicate: bool,
    unknown: bool,
    memory_layer_write_performed: bool,
    state_persistence_write_performed: bool,
    file_write_performed: bool,
    learning_candidate_created: bool,
    action_selection_influence_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
) -> str:
    if duplicate:
        return "trace_history_lane_blocked_duplicate_sequence"
    if unknown:
        return "trace_history_lane_blocked_unknown_source_family"
    if memory_layer_write_performed or state_persistence_write_performed or learning_candidate_created or action_selection_influence_created:
        return "trace_history_lane_blocked_memory_write"
    if file_write_performed:
        return "trace_history_lane_blocked_file_write"
    if first_output_created:
        return "trace_history_lane_blocked_first_output"
    if live_runtime_session_created:
        return "trace_history_lane_blocked_live_runtime"
    if plan is None or plan.lane_plan_status != "lane_plan_created":
        return "trace_history_lane_blocked_unknown_source_family"
    return "trace_history_lane_recorded_empty" if not entries else "trace_history_lane_recorded"


def _readback_matches(
    readback_mode: str,
    query: dict[str, Any],
    entries: tuple[HostBodyTraceHistoryEntryRecord, ...],
) -> tuple[tuple[HostBodyTraceHistoryEntryRecord, ...], bool]:
    if readback_mode == "empty_readback":
        return tuple(), False
    if readback_mode == "recent_n_entries":
        n = query.get("n", 3)
        if not isinstance(n, int) or n < 0:
            return tuple(), True
        return tuple(entries[-n:] if n else tuple()), False
    if readback_mode == "by_source_family":
        value = query.get("source_family")
        if not isinstance(value, str):
            return tuple(), True
        return tuple(item for item in entries if item.source_record_family == value), False
    if readback_mode == "by_event_type":
        value = query.get("event_type")
        if not isinstance(value, str):
            return tuple(), True
        return tuple(item for item in entries if item.source_event_type == value), False
    if readback_mode == "by_surface_kind":
        value = query.get("surface_kind")
        if not isinstance(value, str):
            return tuple(), True
        return tuple(item for item in entries if item.source_surface_kind == value), False
    if readback_mode == "by_bridge_status":
        value = query.get("bridge_status")
        if not isinstance(value, str):
            return tuple(), True
        return tuple(item for item in entries if item.source_bridge_status == value), False
    return tuple(), True


def _readback_status(
    *,
    lane: HostBodyTraceHistoryLaneRecord,
    invalid_query: bool,
    matched: tuple[HostBodyTraceHistoryEntryRecord, ...],
    readback_is_memory_retrieval: bool,
    readback_can_influence_action: bool,
    readback_can_create_learning: bool,
    readback_can_create_first_output: bool,
    memory_layer_write_performed: bool,
    state_persistence_write_performed: bool,
    file_write_performed: bool,
    learning_candidate_created: bool,
    action_selection_influence_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
) -> str:
    if not lane.lane_status.startswith("trace_history_lane_recorded") or invalid_query:
        return "trace_history_readback_blocked_invalid_query"
    if readback_is_memory_retrieval or memory_layer_write_performed or state_persistence_write_performed or file_write_performed or live_runtime_session_created:
        return "trace_history_readback_blocked_memory_retrieval_claim"
    if readback_can_influence_action or action_selection_influence_created:
        return "trace_history_readback_blocked_action_influence"
    if readback_can_create_learning or learning_candidate_created:
        return "trace_history_readback_blocked_learning_creation"
    if readback_can_create_first_output or first_output_created:
        return "trace_history_readback_blocked_first_output"
    return "trace_history_readback_recorded_empty" if not matched else "trace_history_readback_recorded"


def _render_status(
    *,
    lane: HostBodyTraceHistoryLaneRecord,
    selected: tuple[HostBodyTraceHistoryEntryRecord, ...],
    file_written: bool,
    network_output_created: bool,
    screen_mutated: bool,
    unity_runtime_mutated: bool,
    first_output_created: bool,
    production_behavior_created: bool,
) -> str:
    if not lane.lane_status.startswith("trace_history_lane_recorded"):
        return "trace_history_render_blocked_invalid_lane"
    if file_written:
        return "trace_history_render_blocked_file_write"
    if network_output_created:
        return "trace_history_render_blocked_network_output"
    if screen_mutated or unity_runtime_mutated:
        return "trace_history_render_blocked_screen_mutation"
    if first_output_created:
        return "trace_history_render_blocked_first_output"
    if production_behavior_created:
        return "trace_history_render_blocked_production_behavior"
    return "trace_history_render_created_empty" if not selected else "trace_history_render_created"


def _audit_reasons(
    *,
    plan: HostBodyTraceHistoryLanePlanRecord | None,
    entries: tuple[HostBodyTraceHistoryEntryRecord, ...],
    lane: HostBodyTraceHistoryLaneRecord | None,
    index: HostBodyTraceHistoryIndexRecord | None,
    readback: HostBodyTraceHistoryReadbackRecord | None,
    render: HostBodyTraceHistoryRenderRecord | None,
    force_memory_layer_write: bool,
    force_core_memory_write: bool,
    force_long_term_memory_write: bool,
    force_archive_memory_write: bool,
    force_anchor_write: bool,
    force_state_persistence_write: bool,
    force_retained_jsonl_write: bool,
    force_file_write: bool,
    force_learning_candidate_creation: bool,
    force_action_selection_influence: bool,
    force_internal_action_choice_runtime: bool,
    force_external_control: bool,
    force_first_output: bool,
    force_live_runtime_session: bool,
    force_unity_runtime_mutation: bool,
    force_production_behavior: bool,
) -> list[str]:
    reasons: list[str] = []
    if plan is None:
        reasons.append("missing_plan")
    elif plan.lane_plan_status != "lane_plan_created":
        reasons.append("invalid_plan")
        _append_plan_forbidden_reasons(reasons, plan)
    for entry in entries:
        if not entry.entry_status.startswith("trace_history_entry_recorded"):
            reasons.append("invalid_entry")
        _append_entry_forbidden_reasons(reasons, entry)
    if lane is None or not lane.lane_status.startswith("trace_history_lane_recorded"):
        reasons.append("invalid_lane")
        if lane is not None:
            _append_lane_forbidden_reasons(reasons, lane)
    if index is not None and not index.index_status.startswith("trace_history_index_recorded"):
        reasons.append("invalid_index")
        _append_index_forbidden_reasons(reasons, index)
    if readback is not None and not readback.readback_status.startswith("trace_history_readback_recorded"):
        reasons.append("invalid_readback")
        _append_readback_forbidden_reasons(reasons, readback)
    if render is not None and not render.render_status.startswith("trace_history_render_created"):
        reasons.append("invalid_render")
        _append_render_forbidden_reasons(reasons, render)
    forced = {
        "memory_write": force_memory_layer_write,
        "core_memory_write": force_core_memory_write,
        "long_term_memory_write": force_long_term_memory_write,
        "archive_memory_write": force_archive_memory_write,
        "anchor_write": force_anchor_write,
        "state_persistence": force_state_persistence_write,
        "retained_jsonl": force_retained_jsonl_write,
        "file_write": force_file_write,
        "learning_candidate": force_learning_candidate_creation,
        "action_selection": force_action_selection_influence,
        "internal_action_choice": force_internal_action_choice_runtime,
        "external_control": force_external_control,
        "first_output": force_first_output,
        "live_runtime": force_live_runtime_session,
        "unity_runtime_mutation": force_unity_runtime_mutation,
        "production_behavior": force_production_behavior,
    }
    for reason, present in forced.items():
        if present:
            reasons.append(reason)
    return list(dict.fromkeys(reasons))


def _audit_status(
    reasons: list[str],
    lane: HostBodyTraceHistoryLaneRecord | None,
    readback: HostBodyTraceHistoryReadbackRecord | None,
    render: HostBodyTraceHistoryRenderRecord | None,
) -> str:
    if "missing_plan" in reasons:
        return "blocked_missing_lane_plan"
    if any(reason in reasons for reason in ("memory_write", "core_memory_write", "long_term_memory_write", "archive_memory_write", "anchor_write")):
        return "blocked_memory_write_detected"
    if any(reason in reasons for reason in ("state_persistence", "retained_jsonl")):
        return "blocked_state_persistence_write_detected"
    if "file_write" in reasons:
        return "blocked_file_write_detected"
    if "learning_candidate" in reasons:
        return "blocked_learning_candidate_creation_detected"
    if "action_selection" in reasons:
        return "blocked_action_selection_influence_detected"
    if "first_output" in reasons:
        return "blocked_first_output_detected"
    if "live_runtime" in reasons:
        return "blocked_live_runtime_detected"
    if "production_behavior" in reasons or "unity_runtime_mutation" in reasons:
        return "blocked_production_behavior_detected"
    if "invalid_entry" in reasons:
        return "blocked_invalid_entry"
    if "invalid_lane" in reasons:
        return "blocked_invalid_lane"
    if "invalid_index" in reasons:
        return "blocked_invalid_index"
    if "invalid_readback" in reasons:
        return "blocked_invalid_readback"
    if "invalid_render" in reasons:
        return "blocked_invalid_render"
    if "invalid_plan" in reasons:
        return "blocked_missing_lane_plan"
    if lane is not None and lane.lane_status == "trace_history_lane_recorded_empty":
        return "passed_empty_host_body_trace_history_lane"
    if readback is not None and render is None:
        return "passed_trace_history_readback_only"
    return "passed_host_body_trace_history_lane"


def _source_metadata(
    source_record: object,
    source_record_family: str | None,
    source_record_kind: str | None,
) -> dict[str, Any]:
    data = _source_data(source_record)
    family = source_record_family or _infer_source_family(data)
    kind = source_record_kind or _infer_source_kind(data, family)
    record_id = _infer_source_id(data, family)
    return {
        "source_record_id": record_id,
        "source_record_family": family,
        "source_record_kind": kind,
        "source_event_type": _infer_event_type(data, family),
        "source_event_family": _infer_event_family(data, family),
        "source_port_kind": _infer_port_kind(data, family),
        "source_surface_kind": _infer_surface_kind(data, family),
        "source_bridge_status": _infer_bridge_status(data, family),
        "fixture_only_source": bool(data.get("fixture_only", data.get("read_only_event", True))),
        "source_trace_refs": tuple(data.get("source_trace_refs", tuple()) or tuple()),
    }


def _source_data(source_record: object) -> dict[str, Any]:
    if hasattr(source_record, "to_dict"):
        return dict(source_record.to_dict())
    if isinstance(source_record, dict):
        return dict(source_record)
    raise TypeError("source_record must be a record object or dict")


def _infer_source_family(data: dict[str, Any]) -> str:
    if "host_body_event_id" in data:
        return "host_body_event"
    if "host_camera_event_id" in data:
        return "host_body_camera_event"
    if "host_mic_event_id" in data:
        return "host_body_mic_event"
    if "host_idle_event_id" in data:
        return "host_body_idle_event"
    if "host_sensor_event_set_id" in data:
        return "host_body_sensor_event_set"
    if any(key in data for key in ("host_runtime_bridge_trace_id", "host_runtime_eventframe_bridge_id", "host_runtime_dispatch_link_id", "host_event_runtime_mapping_id")):
        return "host_body_runtime_bridge"
    if "home_port_surface_id" in data:
        return "qingyin_home_port_surface"
    if "home_host_event_surface_id" in data:
        return "qingyin_home_host_event_surface"
    if "home_runtime_bridge_surface_id" in data:
        return "qingyin_home_runtime_bridge_surface"
    if "home_status_light_id" in data:
        return "qingyin_home_status_light"
    if "home_teacher_observed_surface_id" in data:
        return "qingyin_home_teacher_observed_surface"
    if "home_internal_space_render_id" in data:
        return "qingyin_home_render"
    return "unknown_source_family"


def _infer_source_id(data: dict[str, Any], family: str) -> str:
    key_by_family = {
        "host_body_event": "host_body_event_id",
        "host_body_camera_event": "host_camera_event_id",
        "host_body_mic_event": "host_mic_event_id",
        "host_body_idle_event": "host_idle_event_id",
        "host_body_sensor_event_set": "host_sensor_event_set_id",
        "qingyin_home_port_surface": "home_port_surface_id",
        "qingyin_home_host_event_surface": "home_host_event_surface_id",
        "qingyin_home_runtime_bridge_surface": "home_runtime_bridge_surface_id",
        "qingyin_home_status_light": "home_status_light_id",
        "qingyin_home_teacher_observed_surface": "home_teacher_observed_surface_id",
        "qingyin_home_render": "home_internal_space_render_id",
    }
    if family == "host_body_runtime_bridge":
        for key in (
            "host_runtime_bridge_trace_id",
            "host_runtime_eventframe_bridge_id",
            "host_runtime_dispatch_link_id",
            "host_event_runtime_mapping_id",
        ):
            if key in data:
                return str(data[key])
    key = key_by_family.get(family)
    if key and key in data:
        return str(data[key])
    return str(data.get("source_record_id", "unknown_source_record"))


def _infer_source_kind(data: dict[str, Any], family: str) -> str:
    if family == "host_body_event":
        return str(data.get("event_kind", "host_body_event"))
    if family == "host_body_camera_event":
        return str(data.get("camera_event_kind", "camera_event"))
    if family == "host_body_mic_event":
        return str(data.get("mic_event_kind", "mic_event"))
    if family == "host_body_idle_event":
        return str(data.get("idle_event_kind", "idle_event"))
    if family == "host_body_sensor_event_set":
        return str(data.get("event_set_kind", "sensor_event_set"))
    if family == "host_body_runtime_bridge":
        if "host_runtime_dispatch_link_id" in data:
            return "runtime_dispatch_link"
        if "host_runtime_eventframe_bridge_id" in data:
            return "runtime_eventframe_bridge"
        if "host_event_runtime_mapping_id" in data:
            return "host_event_runtime_mapping"
        return "runtime_bridge_trace"
    if family == "qingyin_home_status_light":
        return str(data.get("status_light_kind", "status_light"))
    if family == "qingyin_home_render":
        return str(data.get("render_kind", "home_render"))
    return str(data.get("source_record_kind", family))


def _infer_event_type(data: dict[str, Any], family: str) -> str | None:
    if family == "host_body_event":
        return data.get("event_type")
    if family == "host_body_camera_event":
        return data.get("camera_event_type")
    if family == "host_body_mic_event":
        return data.get("mic_event_type")
    if family == "host_body_idle_event":
        return data.get("idle_event_type")
    if family == "host_body_runtime_bridge":
        return data.get("event_type") or data.get("target_event_type")
    return None


def _infer_event_family(data: dict[str, Any], family: str) -> str | None:
    if family == "host_body_event":
        return data.get("event_family")
    if family == "host_body_camera_event":
        return "camera_low_level_event"
    if family == "host_body_mic_event":
        return "mic_low_level_event"
    if family == "host_body_idle_event":
        return "host_idle_event"
    if family == "host_body_runtime_bridge":
        return data.get("event_family") or data.get("target_event_family")
    return None


def _infer_port_kind(data: dict[str, Any], family: str) -> str | None:
    if family == "host_body_event":
        return data.get("source_port_kind")
    if family == "host_body_camera_event":
        return "camera_port"
    if family == "host_body_mic_event":
        return "mic_port"
    if family == "host_body_idle_event":
        return "host_status_port"
    return None


def _infer_surface_kind(data: dict[str, Any], family: str) -> str | None:
    if family == "qingyin_home_port_surface":
        return data.get("port_surface_kind")
    if family == "qingyin_home_host_event_surface":
        return "recent_host_event_surface"
    if family == "qingyin_home_runtime_bridge_surface":
        return "runtime_eventframe_bridge_surface"
    if family == "qingyin_home_status_light":
        return data.get("status_light_kind")
    if family == "qingyin_home_teacher_observed_surface":
        return "teacher_observed_surface"
    if family == "qingyin_home_render":
        return data.get("render_kind")
    return None


def _infer_bridge_status(data: dict[str, Any], family: str) -> str | None:
    if family != "host_body_runtime_bridge":
        return data.get("runtime_bridge_surface_status") if family == "qingyin_home_runtime_bridge_surface" else None
    return (
        data.get("bridge_trace_status")
        or data.get("bridge_status")
        or data.get("dispatch_link_status")
        or data.get("mapping_status")
    )


def _entry_kind(source_family: str, status: str) -> str:
    if status.startswith("trace_history_entry_blocked"):
        return "blocked_entry"
    if source_family in {
        "host_body_event",
        "host_body_camera_event",
        "host_body_mic_event",
        "host_body_idle_event",
        "host_body_sensor_event_set",
    }:
        return "sensor_event_entry"
    if source_family == "host_body_runtime_bridge":
        return "runtime_bridge_entry"
    if source_family == "qingyin_home_status_light":
        return "status_light_entry"
    if source_family == "qingyin_home_teacher_observed_surface":
        return "teacher_observed_entry"
    if source_family == "qingyin_home_render":
        return "render_entry"
    return "home_surface_entry"


def _payload_has_forbidden_content(payload: dict[str, Any]) -> bool:
    for key, value in payload.items():
        lowered = str(key).lower()
        if any(token in lowered for token in FORBIDDEN_PAYLOAD_KEYS):
            return True
        if isinstance(value, (bytes, bytearray)):
            return True
    return False


def _payload_has_qingyin_output(payload: dict[str, Any]) -> bool:
    keys = {str(key).lower() for key in payload}
    return bool({"free_form_qingyin_output", "qingyin_output", "first_output"} & keys)


def _entries_have_forbidden(entries: tuple[HostBodyTraceHistoryEntryRecord, ...]) -> dict[str, bool]:
    return {
        "memory": any(item.memory_layer_write_performed for item in entries),
        "state": any(item.state_persistence_write_performed for item in entries),
        "file": any(item.file_write_performed for item in entries),
        "learning": any(item.learning_candidate_created for item in entries),
        "action": any(item.action_selection_influence_created for item in entries),
        "first_output": any(item.first_output_created for item in entries),
        "live_runtime": any(item.live_runtime_session_created for item in entries),
    }


def _render_selected_entries(
    entries: tuple[HostBodyTraceHistoryEntryRecord, ...],
    readback: HostBodyTraceHistoryReadbackRecord | None,
) -> tuple[HostBodyTraceHistoryEntryRecord, ...]:
    if readback is None:
        return entries
    selected = set(readback.matched_entry_ids)
    return tuple(item for item in entries if item.trace_history_entry_id in selected)


def _entry_render_row(item: HostBodyTraceHistoryEntryRecord) -> dict[str, Any]:
    return {
        "sequence_index": item.sequence_index,
        "entry_id": item.trace_history_entry_id,
        "source_family": item.source_record_family,
        "event_type": item.source_event_type,
        "surface_kind": item.source_surface_kind,
        "bridge_status": item.source_bridge_status,
        "entry_status": item.entry_status,
    }


def _render_text(render_kind: str, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "host body trace history is empty"
    if render_kind == "json_snapshot_render":
        return f"json_snapshot rows={len(rows)} read_only=true"
    if render_kind == "recent_history_card_render":
        return "\n".join(f"{row['sequence_index']:03d} {row['source_family']}" for row in rows)
    return "\n".join(
        f"{row['sequence_index']:03d} | {row['source_family']} | "
        f"{row.get('event_type') or row.get('surface_kind') or row.get('bridge_status')}"
        for row in rows
    )


def _index_entries(entries: tuple[HostBodyTraceHistoryEntryRecord, ...], field_name: str) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for item in entries:
        value = getattr(item, field_name)
        if value is None:
            continue
        index.setdefault(str(value), []).append(item.trace_history_entry_id)
    return index


def _plan_constants_safe(item: HostBodyTraceHistoryLanePlanRecord) -> bool:
    return (
        item.read_only_lane
        and item.demo_record_only
        and item.in_memory_only
        and not item.memory_layer_write_allowed
        and not item.long_term_memory_write_allowed
        and not item.core_memory_write_allowed
        and not item.archive_memory_write_allowed
        and not item.anchor_write_allowed
        and not item.state_persistence_write_allowed
        and not item.retained_jsonl_write_allowed
        and not item.file_write_allowed
        and not item.learning_candidate_creation_allowed
        and not item.action_selection_allowed
        and not item.internal_action_choice_allowed
        and not item.first_output_allowed
        and not item.live_runtime_session_allowed
    )


def _entry_has_forbidden(item: HostBodyTraceHistoryEntryRecord) -> bool:
    return any(
        (
            item.semantic_interpretation_created,
            item.action_selection_influence_created,
            item.memory_layer_write_performed,
            item.state_persistence_write_performed,
            item.file_write_performed,
            item.learning_candidate_created,
            item.first_output_created,
            item.live_runtime_session_created,
            item.production_behavior_created,
        )
    )


def _lane_has_forbidden(item: HostBodyTraceHistoryLaneRecord) -> bool:
    return any(
        (
            item.memory_layer_write_performed,
            item.state_persistence_write_performed,
            item.file_write_performed,
            item.learning_candidate_created,
            item.action_selection_influence_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _index_has_forbidden(item: HostBodyTraceHistoryIndexRecord) -> bool:
    return any(
        (
            item.memory_layer_write_performed,
            item.file_write_performed,
            item.learning_candidate_created,
            item.action_selection_influence_created,
            item.first_output_created,
        )
    )


def _readback_has_forbidden(item: HostBodyTraceHistoryReadbackRecord) -> bool:
    return any(
        (
            item.readback_is_memory_retrieval,
            item.readback_can_influence_action,
            item.readback_can_create_learning,
            item.readback_can_create_first_output,
            item.memory_layer_write_performed,
            item.state_persistence_write_performed,
            item.file_write_performed,
            item.learning_candidate_created,
            item.action_selection_influence_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _render_has_forbidden(item: HostBodyTraceHistoryRenderRecord) -> bool:
    return any(
        (
            item.file_written,
            item.network_output_created,
            item.screen_mutated,
            item.unity_runtime_mutated,
            item.first_output_created,
            item.production_behavior_created,
        )
    )


def _append_plan_forbidden_reasons(reasons: list[str], plan: HostBodyTraceHistoryLanePlanRecord) -> None:
    if plan.memory_layer_write_allowed or plan.core_memory_write_allowed or plan.long_term_memory_write_allowed or plan.archive_memory_write_allowed or plan.anchor_write_allowed:
        reasons.append("memory_write")
    if plan.state_persistence_write_allowed or plan.retained_jsonl_write_allowed:
        reasons.append("state_persistence")
    if plan.file_write_allowed:
        reasons.append("file_write")
    if plan.learning_candidate_creation_allowed:
        reasons.append("learning_candidate")
    if plan.action_selection_allowed:
        reasons.append("action_selection")
    if plan.internal_action_choice_allowed:
        reasons.append("internal_action_choice")
    if plan.first_output_allowed:
        reasons.append("first_output")
    if plan.live_runtime_session_allowed:
        reasons.append("live_runtime")


def _append_entry_forbidden_reasons(reasons: list[str], entry: HostBodyTraceHistoryEntryRecord) -> None:
    if entry.memory_layer_write_performed:
        reasons.append("memory_write")
    if entry.state_persistence_write_performed:
        reasons.append("state_persistence")
    if entry.file_write_performed:
        reasons.append("file_write")
    if entry.learning_candidate_created:
        reasons.append("learning_candidate")
    if entry.action_selection_influence_created:
        reasons.append("action_selection")
    if entry.first_output_created:
        reasons.append("first_output")
    if entry.live_runtime_session_created:
        reasons.append("live_runtime")
    if entry.production_behavior_created:
        reasons.append("production_behavior")


def _append_lane_forbidden_reasons(reasons: list[str], lane: HostBodyTraceHistoryLaneRecord) -> None:
    if lane.memory_layer_write_performed:
        reasons.append("memory_write")
    if lane.state_persistence_write_performed:
        reasons.append("state_persistence")
    if lane.file_write_performed:
        reasons.append("file_write")
    if lane.learning_candidate_created:
        reasons.append("learning_candidate")
    if lane.action_selection_influence_created:
        reasons.append("action_selection")
    if lane.first_output_created:
        reasons.append("first_output")
    if lane.live_runtime_session_created:
        reasons.append("live_runtime")


def _append_index_forbidden_reasons(reasons: list[str], index: HostBodyTraceHistoryIndexRecord) -> None:
    if index.memory_layer_write_performed:
        reasons.append("memory_write")
    if index.file_write_performed:
        reasons.append("file_write")
    if index.learning_candidate_created:
        reasons.append("learning_candidate")
    if index.action_selection_influence_created:
        reasons.append("action_selection")
    if index.first_output_created:
        reasons.append("first_output")


def _append_readback_forbidden_reasons(reasons: list[str], readback: HostBodyTraceHistoryReadbackRecord) -> None:
    if readback.readback_is_memory_retrieval or readback.memory_layer_write_performed:
        reasons.append("memory_write")
    if readback.state_persistence_write_performed:
        reasons.append("state_persistence")
    if readback.file_write_performed:
        reasons.append("file_write")
    if readback.readback_can_create_learning or readback.learning_candidate_created:
        reasons.append("learning_candidate")
    if readback.readback_can_influence_action or readback.action_selection_influence_created:
        reasons.append("action_selection")
    if readback.readback_can_create_first_output or readback.first_output_created:
        reasons.append("first_output")
    if readback.live_runtime_session_created:
        reasons.append("live_runtime")


def _append_render_forbidden_reasons(reasons: list[str], render: HostBodyTraceHistoryRenderRecord) -> None:
    if render.file_written:
        reasons.append("file_write")
    if render.network_output_created:
        reasons.append("file_write")
    if render.screen_mutated:
        reasons.append("file_write")
    if render.unity_runtime_mutated:
        reasons.append("unity_runtime_mutation")
    if render.first_output_created:
        reasons.append("first_output")
    if render.production_behavior_created:
        reasons.append("production_behavior")


def _lane_plan_summary(status: str) -> str:
    return {
        "lane_plan_created": "Read-only in-memory Host Body trace history lane plan created.",
        "blocked_missing_home_surface_audit": "Home surface audit is required before trace history lane planning.",
        "blocked_missing_host_runtime_bridge_audit": "Host runtime bridge audit is required before trace history lane planning.",
        "blocked_memory_write_allowed": "Trace history lane cannot allow memory writes.",
        "blocked_state_persistence_write_allowed": "Trace history lane cannot allow State Persistence writes.",
        "blocked_file_write_allowed": "Trace history lane cannot allow file or retained JSONL writes.",
        "blocked_learning_candidate_creation_allowed": "Trace history lane cannot create learning candidates.",
        "blocked_action_selection_allowed": "Trace history lane cannot influence action selection.",
        "blocked_first_output_allowed": "Trace history lane cannot create first_output.",
        "blocked_live_runtime_allowed": "Trace history lane cannot create a live runtime session.",
        "blocked_forbidden_authority_detected": "Trace history lane requested forbidden authority.",
    }[status]


def _entry_summary(status: str, family: str) -> str:
    if status.startswith("trace_history_entry_recorded"):
        return f"Read-only trace history entry recorded for {family}."
    return f"Trace history entry blocked for {family}: {status}."


def _lane_summary(status: str) -> str:
    if status == "trace_history_lane_recorded":
        return "Read-only Host Body trace history lane recorded."
    if status == "trace_history_lane_recorded_empty":
        return "Read-only Host Body trace history lane recorded with no entries."
    return f"Trace history lane blocked: {status}."


def _index_summary(status: str) -> str:
    if status.startswith("trace_history_index_recorded"):
        return "Read-only trace history index recorded."
    return f"Trace history index blocked: {status}."


def _readback_summary(status: str, mode: str, count: int) -> str:
    if status.startswith("trace_history_readback_recorded"):
        return f"Read-only trace history readback recorded for {mode} with {count} matches."
    return f"Trace history readback blocked: {status}."


def _render_summary(status: str) -> str:
    if status.startswith("trace_history_render_created"):
        return "Read-only trace history render created."
    return f"Trace history render blocked: {status}."


def _readiness_summary(status: str) -> str:
    if status.startswith("ready_for_"):
        return "Host Body trace history lane is ready for the next read-only/internal-only package."
    return f"Host Body trace history lane readiness blocked: {status}."


def _port_map(record: HostBodyPortMapRecord | dict[str, object]) -> HostBodyPortMapRecord:
    return record if isinstance(record, HostBodyPortMapRecord) else HostBodyPortMapRecord.from_dict(record)


def _home_audit(record: QingyinHomeInternalSpaceSurfaceAudit | dict[str, object]) -> QingyinHomeInternalSpaceSurfaceAudit:
    return record if isinstance(record, QingyinHomeInternalSpaceSurfaceAudit) else QingyinHomeInternalSpaceSurfaceAudit.from_dict(record)


def _bridge_audit(record: HostBodyRuntimeBridgeAudit | dict[str, object]) -> HostBodyRuntimeBridgeAudit:
    return record if isinstance(record, HostBodyRuntimeBridgeAudit) else HostBodyRuntimeBridgeAudit.from_dict(record)


def _plan(record: HostBodyTraceHistoryLanePlanRecord | dict[str, object]) -> HostBodyTraceHistoryLanePlanRecord:
    return record if isinstance(record, HostBodyTraceHistoryLanePlanRecord) else HostBodyTraceHistoryLanePlanRecord.from_dict(record)


def _entry(record: HostBodyTraceHistoryEntryRecord | dict[str, object]) -> HostBodyTraceHistoryEntryRecord:
    return record if isinstance(record, HostBodyTraceHistoryEntryRecord) else HostBodyTraceHistoryEntryRecord.from_dict(record)


def _lane(record: HostBodyTraceHistoryLaneRecord | dict[str, object]) -> HostBodyTraceHistoryLaneRecord:
    return record if isinstance(record, HostBodyTraceHistoryLaneRecord) else HostBodyTraceHistoryLaneRecord.from_dict(record)


def _index(record: HostBodyTraceHistoryIndexRecord | dict[str, object]) -> HostBodyTraceHistoryIndexRecord:
    return record if isinstance(record, HostBodyTraceHistoryIndexRecord) else HostBodyTraceHistoryIndexRecord.from_dict(record)


def _readback(record: HostBodyTraceHistoryReadbackRecord | dict[str, object]) -> HostBodyTraceHistoryReadbackRecord:
    return record if isinstance(record, HostBodyTraceHistoryReadbackRecord) else HostBodyTraceHistoryReadbackRecord.from_dict(record)


def _render(record: HostBodyTraceHistoryRenderRecord | dict[str, object]) -> HostBodyTraceHistoryRenderRecord:
    return record if isinstance(record, HostBodyTraceHistoryRenderRecord) else HostBodyTraceHistoryRenderRecord.from_dict(record)


def _audit(record: HostBodyTraceHistoryAudit | dict[str, object]) -> HostBodyTraceHistoryAudit:
    return record if isinstance(record, HostBodyTraceHistoryAudit) else HostBodyTraceHistoryAudit.from_dict(record)


def _readiness(record: HostBodyTraceHistoryReadinessRecord | dict[str, object]) -> HostBodyTraceHistoryReadinessRecord:
    return record if isinstance(record, HostBodyTraceHistoryReadinessRecord) else HostBodyTraceHistoryReadinessRecord.from_dict(record)
