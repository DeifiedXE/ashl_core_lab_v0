"""Audit-only Qingyin Host Body v0 milestone records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    build_demo_camera_change_marks_interesting,
)
from ashl_core_v1.host_body.host_body_port_map import (
    build_demo_qingyin_host_body_port_map,
)
from ashl_core_v1.host_body.host_body_runtime_bridge import (
    build_demo_mixed_host_body_runtime_bridge,
)
from ashl_core_v1.host_body.host_body_sensor_events import (
    build_demo_mixed_host_sensor_event_set,
)
from ashl_core_v1.host_body.host_body_trace_history_lane import (
    build_demo_full_host_body_trace_history_lane,
)
from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
    build_demo_qingyin_home_internal_space_surface,
)


SOURCE_ENGINE = "host_body"

SCOPE_SCHEMA_VERSION = "qingyin_host_body_v0_milestone_scope_v0"
CAPABILITY_LEDGER_SCHEMA_VERSION = "qingyin_host_body_v0_capability_ledger_v0"
BOUNDARY_LEDGER_SCHEMA_VERSION = "qingyin_host_body_v0_boundary_ledger_v0"
INTEGRATED_TRACE_SCHEMA_VERSION = "qingyin_host_body_v0_integrated_trace_v0"
MILESTONE_AUDIT_SCHEMA_VERSION = "qingyin_host_body_v0_milestone_audit_v0"
READINESS_SCHEMA_VERSION = "qingyin_host_body_v0_readiness_v0"

MILESTONE_NAME = "qingyin_host_body_v0"
MILESTONE_KIND = "bounded_host_body_substrate_milestone"

INCLUDED_PACKAGES = (
    "Package 101",
    "Package 102",
    "Package 103",
    "Package 104",
    "Package 105",
    "Package 106",
)
INCLUDED_COMMITS = (
    "f2ed68b",
    "9d7f66b",
    "0676341",
    "2b655b3",
    "8f94de6",
    "86f1192",
)
INCLUDED_PILLARS = (
    "host_body_identity_and_port_map",
    "fixture_sensor_events",
    "runtime_eventframe_bridge",
    "qingyin_home_surface",
    "trace_history_lane",
    "internal_action_choice",
)
EXCLUDED_CAPABILITIES = (
    "real_hardware_access",
    "semantic_vision",
    "speech_recognition",
    "task_engine_action_selection",
    "external_control",
    "unity_runtime_connection",
    "memory_layer_write",
    "learning_candidate_creation",
    "automatic_learning_approval",
    "teacher_approval_creation",
    "first_output",
    "live_runtime_session",
    "thought_engine_behavior",
    "production_behavior",
)

SAFE_CLAIM = (
    "ASHL Core v1 has established Qingyin Host Body v0 as a bounded "
    "computer-bodied Host Body substrate, including Host Body identity and "
    "ports, fixture-only read-only sensor events, HostBodyEvent to Runtime "
    "EventFrame bridge, Qingyin Home internal-space surface, read-only Host "
    "Body trace history lane, and internal-only Host Body action choice records."
)
BLOCKED_CLAIMS = (
    "qingyin_host_body_v0_is_awake",
    "real_camera_or_microphone_access",
    "semantic_vision_or_speech_understanding",
    "computer_control",
    "unity_operation",
    "task_engine_action_selection_from_host_body_history",
    "memory_write_from_host_body_history",
    "first_output",
    "live_runtime_session",
)
READINESS_NEXT_PACKAGE = (
    "Package 108 / ASHL Core v1 Host Body Internal Action Home Surface Link Minimal v0"
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


def _tuple_of_dict(
    name: str, value: tuple[dict[str, Any], ...] | list[dict[str, Any]]
) -> tuple[dict[str, Any], ...]:
    items = tuple(dict(item) for item in value)
    if not all(isinstance(item, dict) for item in items):
        raise TypeError(f"{name} must contain only dictionaries")
    return items


def _slug(text: str) -> str:
    safe = [char.lower() if char.isalnum() else "_" for char in text]
    return "_".join("".join(safe).split("_"))[:100] or "empty"


@dataclass(frozen=True)
class QingyinHostBodyV0MilestoneScopeRecord:
    host_body_v0_scope_id: str
    schema_version: str
    created_at: str
    source_engine: str
    milestone_name: str
    milestone_kind: str
    included_packages: tuple[str, ...]
    included_commits: tuple[str, ...]
    included_pillars: tuple[str, ...]
    excluded_capabilities: tuple[str, ...]
    scope_status: str
    scope_summary: str
    host_body_identity_required: bool
    sensor_event_shell_required: bool
    runtime_eventframe_bridge_required: bool
    qingyin_home_surface_required: bool
    trace_history_lane_required: bool
    internal_action_choice_required: bool
    real_hardware_allowed: bool
    external_control_allowed: bool
    memory_write_allowed: bool
    first_output_allowed: bool
    live_runtime_allowed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SCOPE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_v0_milestone_scope_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.milestone_name != MILESTONE_NAME:
            raise ValueError("milestone_name must be qingyin_host_body_v0")
        if self.milestone_kind != MILESTONE_KIND:
            raise ValueError("milestone_kind must be bounded_host_body_substrate_milestone")
        if self.scope_status not in {
            "host_body_v0_scope_created",
            "blocked_missing_required_pillar",
            "blocked_forbidden_capability_in_scope",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown scope_status: {self.scope_status}")
        for name in (
            "included_packages",
            "included_commits",
            "included_pillars",
            "excluded_capabilities",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHostBodyV0MilestoneScopeRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class QingyinHostBodyV0CapabilityLedgerRecord:
    host_body_v0_capability_ledger_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_v0_scope_id: str
    capability_entries: tuple[dict[str, Any], ...]
    host_body_identity_capability_confirmed: bool
    host_body_port_map_capability_confirmed: bool
    fixture_sensor_event_capability_confirmed: bool
    runtime_eventframe_bridge_capability_confirmed: bool
    home_internal_space_surface_capability_confirmed: bool
    trace_history_lane_capability_confirmed: bool
    internal_action_choice_capability_confirmed: bool
    capability_count: int
    capability_ledger_status: str
    capability_ledger_summary: str
    new_capability_created_by_this_package: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CAPABILITY_LEDGER_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_v0_capability_ledger_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.capability_ledger_status not in {
            "host_body_v0_capability_ledger_recorded",
            "blocked_missing_host_body_identity_capability",
            "blocked_missing_sensor_event_capability",
            "blocked_missing_runtime_bridge_capability",
            "blocked_missing_home_surface_capability",
            "blocked_missing_trace_history_capability",
            "blocked_missing_internal_action_choice_capability",
            "blocked_unexpected_new_capability_detected",
        }:
            raise ValueError(f"unknown capability_ledger_status: {self.capability_ledger_status}")
        object.__setattr__(
            self,
            "capability_entries",
            _tuple_of_dict("capability_entries", self.capability_entries),
        )
        object.__setattr__(
            self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs)
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHostBodyV0CapabilityLedgerRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class QingyinHostBodyV0BoundaryLedgerRecord:
    host_body_v0_boundary_ledger_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_v0_scope_id: str
    boundary_entries: tuple[dict[str, Any], ...]
    no_real_camera_access: bool
    no_real_microphone_access: bool
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
    no_task_engine_selected_action: bool
    no_final_action: bool
    no_direct_command: bool
    no_sandbox_execution: bool
    no_external_control: bool
    no_os_control: bool
    no_mouse_control: bool
    no_keyboard_control: bool
    no_browser_control: bool
    no_file_operation: bool
    no_network_execution: bool
    no_shell_execution: bool
    no_external_api_call: bool
    no_unity_runtime_connection: bool
    no_unity_scene_mutation: bool
    no_avatar_control: bool
    no_memory_layer_write: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_state_persistence_write: bool
    no_file_persistence: bool
    no_learning_candidate_creation: bool
    no_automatic_learning_approval: bool
    no_teacher_approval_created: bool
    no_first_output: bool
    no_free_text_conversation: bool
    no_voice_output: bool
    no_live_runtime_session: bool
    no_live_engine_invocation: bool
    no_autonomous_scheduler: bool
    no_open_ended_loop: bool
    no_dynamic_child_event_scheduling: bool
    no_thought_engine_behavior: bool
    no_production_behavior: bool
    boundary_ledger_status: str
    boundary_ledger_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BOUNDARY_LEDGER_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_v0_boundary_ledger_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.boundary_ledger_status not in {
            "host_body_v0_boundary_ledger_recorded",
            "blocked_real_hardware_detected",
            "blocked_semantic_interpretation_detected",
            "blocked_task_action_detected",
            "blocked_external_control_detected",
            "blocked_unity_runtime_detected",
            "blocked_memory_write_detected",
            "blocked_learning_creation_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
            "blocked_production_behavior_detected",
        }:
            raise ValueError(f"unknown boundary_ledger_status: {self.boundary_ledger_status}")
        object.__setattr__(
            self,
            "boundary_entries",
            _tuple_of_dict("boundary_entries", self.boundary_entries),
        )
        object.__setattr__(
            self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs)
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHostBodyV0BoundaryLedgerRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class QingyinHostBodyV0IntegratedTraceRecord:
    host_body_v0_integrated_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_v0_scope_id: str
    source_host_body_port_map_id: str | None
    source_host_sensor_event_set_id: str | None
    source_host_runtime_bridge_trace_id: str | None
    source_qingyin_home_render_id: str | None
    source_trace_history_lane_id: str | None
    source_internal_action_choice_set_id: str | None
    integrated_trace_steps: tuple[dict[str, Any], ...]
    step_count: int
    port_map_step_confirmed: bool
    sensor_event_step_confirmed: bool
    runtime_bridge_step_confirmed: bool
    home_surface_step_confirmed: bool
    trace_history_step_confirmed: bool
    internal_action_choice_step_confirmed: bool
    integrated_trace_status: str
    integrated_trace_summary: str
    new_runtime_behavior_created: bool
    new_external_control_created: bool
    new_memory_write_created: bool
    new_first_output_created: bool
    new_live_runtime_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INTEGRATED_TRACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_v0_integrated_trace_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.integrated_trace_status not in {
            "host_body_v0_integrated_trace_recorded",
            "blocked_missing_port_map_step",
            "blocked_missing_sensor_event_step",
            "blocked_missing_runtime_bridge_step",
            "blocked_missing_home_surface_step",
            "blocked_missing_trace_history_step",
            "blocked_missing_internal_action_choice_step",
            "blocked_forbidden_runtime_behavior_detected",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown integrated_trace_status: {self.integrated_trace_status}")
        object.__setattr__(
            self,
            "integrated_trace_steps",
            _tuple_of_dict("integrated_trace_steps", self.integrated_trace_steps),
        )
        object.__setattr__(
            self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs)
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHostBodyV0IntegratedTraceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class QingyinHostBodyV0MilestoneAuditRecord:
    host_body_v0_milestone_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_v0_scope_id: str | None
    source_capability_ledger_id: str | None
    source_boundary_ledger_id: str | None
    source_integrated_trace_id: str | None
    scope_valid: bool
    capability_ledger_valid: bool
    boundary_ledger_valid: bool
    integrated_trace_valid: bool
    package_101_verified: bool
    package_102_verified: bool
    package_103_verified: bool
    package_104_verified: bool
    package_105_verified: bool
    package_106_verified: bool
    host_body_v0_established: bool
    new_capability_created_by_this_package: bool
    audit_only_package_confirmed: bool
    no_real_hardware: bool
    no_semantic_vision: bool
    no_speech_recognition: bool
    no_task_action_selection: bool
    no_external_control: bool
    no_unity_runtime_connection: bool
    no_memory_layer_write: bool
    no_learning_candidate_creation: bool
    no_automatic_learning_approval: bool
    no_teacher_approval_created: bool
    no_first_output: bool
    no_live_runtime_session: bool
    no_thought_engine_behavior: bool
    no_production_behavior: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MILESTONE_AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_v0_milestone_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.audit_status not in {
            "passed_qingyin_host_body_v0_milestone",
            "blocked_missing_scope",
            "blocked_missing_capability_ledger",
            "blocked_missing_boundary_ledger",
            "blocked_missing_integrated_trace",
            "blocked_package_101_unverified",
            "blocked_package_102_unverified",
            "blocked_package_103_unverified",
            "blocked_package_104_unverified",
            "blocked_package_105_unverified",
            "blocked_package_106_unverified",
            "blocked_unexpected_new_capability_detected",
            "blocked_real_hardware_detected",
            "blocked_semantic_interpretation_detected",
            "blocked_speech_recognition_detected",
            "blocked_task_action_selection_detected",
            "blocked_external_control_detected",
            "blocked_unity_runtime_detected",
            "blocked_memory_write_detected",
            "blocked_learning_candidate_creation_detected",
            "blocked_teacher_approval_created",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
            "blocked_production_behavior_detected",
        }:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        object.__setattr__(
            self, "blocked_claims", _tuple_of_str("blocked_claims", self.blocked_claims)
        )
        object.__setattr__(
            self, "blocked_reasons", _tuple_of_str("blocked_reasons", self.blocked_reasons)
        )
        object.__setattr__(
            self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs)
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHostBodyV0MilestoneAuditRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class QingyinHostBodyV0ReadinessRecord:
    host_body_v0_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_v0_milestone_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_internal_action_home_surface_link: bool
    ready_for_teacher_observed_host_body_cli: bool
    ready_for_runtime_state_persistence_binding: bool
    ready_for_host_body_v0_to_runtime_state_summary: bool
    ready_for_real_camera_connection: bool
    ready_for_real_microphone_connection: bool
    ready_for_semantic_vision: bool
    ready_for_speech_recognition: bool
    ready_for_task_engine_action_selection: bool
    ready_for_external_control: bool
    ready_for_unity_runtime_connection: bool
    ready_for_memory_layer_write: bool
    ready_for_learning_candidate_creation: bool
    ready_for_first_output: bool
    ready_for_live_runtime_session: bool
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READINESS_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_v0_readiness_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.readiness_status not in {
            "ready_for_internal_action_home_surface_link_only",
            "ready_for_teacher_observed_host_body_cli_only",
            "ready_for_runtime_state_persistence_binding_only",
            "ready_for_host_body_v0_to_runtime_state_summary_only",
            "not_ready_missing_host_body_v0_audit",
            "not_ready_boundary_failure",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        object.__setattr__(
            self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs)
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "QingyinHostBodyV0ReadinessRecord":
        return cls(**dict(data))


def build_qingyin_host_body_v0_milestone_scope(
    *,
    included_packages: tuple[str, ...] = INCLUDED_PACKAGES,
    included_commits: tuple[str, ...] = INCLUDED_COMMITS,
    included_pillars: tuple[str, ...] = INCLUDED_PILLARS,
    excluded_capabilities: tuple[str, ...] = EXCLUDED_CAPABILITIES,
    real_hardware_allowed: bool = False,
    external_control_allowed: bool = False,
    memory_write_allowed: bool = False,
    first_output_allowed: bool = False,
    live_runtime_allowed: bool = False,
    source_trace_refs: tuple[str, ...] = tuple(),
) -> QingyinHostBodyV0MilestoneScopeRecord:
    missing_pillar = any(pillar not in included_pillars for pillar in INCLUDED_PILLARS)
    forbidden = any(
        (
            real_hardware_allowed,
            external_control_allowed,
            memory_write_allowed,
            first_output_allowed,
            live_runtime_allowed,
        )
    )
    if missing_pillar:
        status = "blocked_missing_required_pillar"
    elif forbidden:
        status = "blocked_forbidden_capability_in_scope"
    else:
        status = "host_body_v0_scope_created"
    return QingyinHostBodyV0MilestoneScopeRecord(
        host_body_v0_scope_id=f"qingyin_host_body_v0_scope:{_slug(status)}",
        schema_version=SCOPE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        milestone_name=MILESTONE_NAME,
        milestone_kind=MILESTONE_KIND,
        included_packages=included_packages,
        included_commits=included_commits,
        included_pillars=included_pillars,
        excluded_capabilities=excluded_capabilities,
        scope_status=status,
        scope_summary=_scope_summary(status),
        host_body_identity_required=True,
        sensor_event_shell_required=True,
        runtime_eventframe_bridge_required=True,
        qingyin_home_surface_required=True,
        trace_history_lane_required=True,
        internal_action_choice_required=True,
        real_hardware_allowed=real_hardware_allowed,
        external_control_allowed=external_control_allowed,
        memory_write_allowed=memory_write_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_allowed=live_runtime_allowed,
        source_trace_refs=source_trace_refs,
    )


def validate_qingyin_host_body_v0_milestone_scope(
    record: QingyinHostBodyV0MilestoneScopeRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _scope(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.scope_status == "host_body_v0_scope_created" and all(
        pillar in item.included_pillars for pillar in INCLUDED_PILLARS
    )
    valid = valid and not any(
        (
            item.real_hardware_allowed,
            item.external_control_allowed,
            item.memory_write_allowed,
            item.first_output_allowed,
            item.live_runtime_allowed,
        )
    )
    return {
        "valid": valid,
        "status": item.scope_status,
        "reasons": [] if valid else [item.scope_status],
    }


def build_qingyin_host_body_v0_capability_ledger(
    *,
    milestone_scope: QingyinHostBodyV0MilestoneScopeRecord | dict[str, object],
    host_body_identity_capability_confirmed: bool = True,
    host_body_port_map_capability_confirmed: bool = True,
    fixture_sensor_event_capability_confirmed: bool = True,
    runtime_eventframe_bridge_capability_confirmed: bool = True,
    home_internal_space_surface_capability_confirmed: bool = True,
    trace_history_lane_capability_confirmed: bool = True,
    internal_action_choice_capability_confirmed: bool = True,
    new_capability_created_by_this_package: bool = False,
) -> QingyinHostBodyV0CapabilityLedgerRecord:
    scope = _scope(milestone_scope)
    capability_entries = _capability_entries(
        host_body_identity_capability_confirmed=host_body_identity_capability_confirmed,
        host_body_port_map_capability_confirmed=host_body_port_map_capability_confirmed,
        fixture_sensor_event_capability_confirmed=fixture_sensor_event_capability_confirmed,
        runtime_eventframe_bridge_capability_confirmed=runtime_eventframe_bridge_capability_confirmed,
        home_internal_space_surface_capability_confirmed=home_internal_space_surface_capability_confirmed,
        trace_history_lane_capability_confirmed=trace_history_lane_capability_confirmed,
        internal_action_choice_capability_confirmed=internal_action_choice_capability_confirmed,
    )
    status = _capability_ledger_status(
        host_body_identity_capability_confirmed=host_body_identity_capability_confirmed,
        host_body_port_map_capability_confirmed=host_body_port_map_capability_confirmed,
        fixture_sensor_event_capability_confirmed=fixture_sensor_event_capability_confirmed,
        runtime_eventframe_bridge_capability_confirmed=runtime_eventframe_bridge_capability_confirmed,
        home_internal_space_surface_capability_confirmed=home_internal_space_surface_capability_confirmed,
        trace_history_lane_capability_confirmed=trace_history_lane_capability_confirmed,
        internal_action_choice_capability_confirmed=internal_action_choice_capability_confirmed,
        new_capability_created_by_this_package=new_capability_created_by_this_package,
    )
    return QingyinHostBodyV0CapabilityLedgerRecord(
        host_body_v0_capability_ledger_id=f"qingyin_host_body_v0_capability_ledger:{_slug(status)}",
        schema_version=CAPABILITY_LEDGER_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_v0_scope_id=scope.host_body_v0_scope_id,
        capability_entries=capability_entries,
        host_body_identity_capability_confirmed=host_body_identity_capability_confirmed,
        host_body_port_map_capability_confirmed=host_body_port_map_capability_confirmed,
        fixture_sensor_event_capability_confirmed=fixture_sensor_event_capability_confirmed,
        runtime_eventframe_bridge_capability_confirmed=runtime_eventframe_bridge_capability_confirmed,
        home_internal_space_surface_capability_confirmed=home_internal_space_surface_capability_confirmed,
        trace_history_lane_capability_confirmed=trace_history_lane_capability_confirmed,
        internal_action_choice_capability_confirmed=internal_action_choice_capability_confirmed,
        capability_count=sum(1 for entry in capability_entries if entry["verified"]),
        capability_ledger_status=status,
        capability_ledger_summary=_capability_ledger_summary(status),
        new_capability_created_by_this_package=new_capability_created_by_this_package,
        source_trace_refs=scope.source_trace_refs,
    )


def validate_qingyin_host_body_v0_capability_ledger(
    record: QingyinHostBodyV0CapabilityLedgerRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _capability_ledger(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.capability_ledger_status == "host_body_v0_capability_ledger_recorded"
    valid = valid and item.capability_count >= 7
    valid = valid and not item.new_capability_created_by_this_package
    return {
        "valid": valid,
        "status": item.capability_ledger_status,
        "reasons": [] if valid else [item.capability_ledger_status],
    }


def build_qingyin_host_body_v0_boundary_ledger(
    *,
    milestone_scope: QingyinHostBodyV0MilestoneScopeRecord | dict[str, object],
    no_real_camera_access: bool = True,
    no_real_microphone_access: bool = True,
    no_camera_capture: bool = True,
    no_mic_stream: bool = True,
    no_image_storage: bool = True,
    no_audio_storage: bool = True,
    no_semantic_vision: bool = True,
    no_object_recognition: bool = True,
    no_face_recognition: bool = True,
    no_speech_recognition: bool = True,
    no_speaker_identification: bool = True,
    no_voice_command: bool = True,
    no_language_understanding: bool = True,
    no_task_engine_selected_action: bool = True,
    no_final_action: bool = True,
    no_direct_command: bool = True,
    no_sandbox_execution: bool = True,
    no_external_control: bool = True,
    no_os_control: bool = True,
    no_mouse_control: bool = True,
    no_keyboard_control: bool = True,
    no_browser_control: bool = True,
    no_file_operation: bool = True,
    no_network_execution: bool = True,
    no_shell_execution: bool = True,
    no_external_api_call: bool = True,
    no_unity_runtime_connection: bool = True,
    no_unity_scene_mutation: bool = True,
    no_avatar_control: bool = True,
    no_memory_layer_write: bool = True,
    no_core_memory_write: bool = True,
    no_long_term_memory_write: bool = True,
    no_archive_memory_write: bool = True,
    no_anchor_write: bool = True,
    no_state_persistence_write: bool = True,
    no_file_persistence: bool = True,
    no_learning_candidate_creation: bool = True,
    no_automatic_learning_approval: bool = True,
    no_teacher_approval_created: bool = True,
    no_first_output: bool = True,
    no_free_text_conversation: bool = True,
    no_voice_output: bool = True,
    no_live_runtime_session: bool = True,
    no_live_engine_invocation: bool = True,
    no_autonomous_scheduler: bool = True,
    no_open_ended_loop: bool = True,
    no_dynamic_child_event_scheduling: bool = True,
    no_thought_engine_behavior: bool = True,
    no_production_behavior: bool = True,
) -> QingyinHostBodyV0BoundaryLedgerRecord:
    scope = _scope(milestone_scope)
    values = {
        "no_real_camera_access": no_real_camera_access,
        "no_real_microphone_access": no_real_microphone_access,
        "no_camera_capture": no_camera_capture,
        "no_mic_stream": no_mic_stream,
        "no_image_storage": no_image_storage,
        "no_audio_storage": no_audio_storage,
        "no_semantic_vision": no_semantic_vision,
        "no_object_recognition": no_object_recognition,
        "no_face_recognition": no_face_recognition,
        "no_speech_recognition": no_speech_recognition,
        "no_speaker_identification": no_speaker_identification,
        "no_voice_command": no_voice_command,
        "no_language_understanding": no_language_understanding,
        "no_task_engine_selected_action": no_task_engine_selected_action,
        "no_final_action": no_final_action,
        "no_direct_command": no_direct_command,
        "no_sandbox_execution": no_sandbox_execution,
        "no_external_control": no_external_control,
        "no_os_control": no_os_control,
        "no_mouse_control": no_mouse_control,
        "no_keyboard_control": no_keyboard_control,
        "no_browser_control": no_browser_control,
        "no_file_operation": no_file_operation,
        "no_network_execution": no_network_execution,
        "no_shell_execution": no_shell_execution,
        "no_external_api_call": no_external_api_call,
        "no_unity_runtime_connection": no_unity_runtime_connection,
        "no_unity_scene_mutation": no_unity_scene_mutation,
        "no_avatar_control": no_avatar_control,
        "no_memory_layer_write": no_memory_layer_write,
        "no_core_memory_write": no_core_memory_write,
        "no_long_term_memory_write": no_long_term_memory_write,
        "no_archive_memory_write": no_archive_memory_write,
        "no_anchor_write": no_anchor_write,
        "no_state_persistence_write": no_state_persistence_write,
        "no_file_persistence": no_file_persistence,
        "no_learning_candidate_creation": no_learning_candidate_creation,
        "no_automatic_learning_approval": no_automatic_learning_approval,
        "no_teacher_approval_created": no_teacher_approval_created,
        "no_first_output": no_first_output,
        "no_free_text_conversation": no_free_text_conversation,
        "no_voice_output": no_voice_output,
        "no_live_runtime_session": no_live_runtime_session,
        "no_live_engine_invocation": no_live_engine_invocation,
        "no_autonomous_scheduler": no_autonomous_scheduler,
        "no_open_ended_loop": no_open_ended_loop,
        "no_dynamic_child_event_scheduling": no_dynamic_child_event_scheduling,
        "no_thought_engine_behavior": no_thought_engine_behavior,
        "no_production_behavior": no_production_behavior,
    }
    status = _boundary_ledger_status(values)
    return QingyinHostBodyV0BoundaryLedgerRecord(
        host_body_v0_boundary_ledger_id=f"qingyin_host_body_v0_boundary_ledger:{_slug(status)}",
        schema_version=BOUNDARY_LEDGER_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_v0_scope_id=scope.host_body_v0_scope_id,
        boundary_entries=_boundary_entries(values),
        boundary_ledger_status=status,
        boundary_ledger_summary=_boundary_ledger_summary(status),
        source_trace_refs=scope.source_trace_refs,
        **values,
    )


def validate_qingyin_host_body_v0_boundary_ledger(
    record: QingyinHostBodyV0BoundaryLedgerRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _boundary_ledger(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.boundary_ledger_status == "host_body_v0_boundary_ledger_recorded"
    valid = valid and all(getattr(item, field.name) is True for field in fields(item) if field.name.startswith("no_"))
    return {
        "valid": valid,
        "status": item.boundary_ledger_status,
        "reasons": [] if valid else [item.boundary_ledger_status],
    }


def build_qingyin_host_body_v0_integrated_trace(
    *,
    milestone_scope: QingyinHostBodyV0MilestoneScopeRecord | dict[str, object],
    source_host_body_port_map_id: str | None = None,
    source_host_sensor_event_set_id: str | None = None,
    source_host_runtime_bridge_trace_id: str | None = None,
    source_qingyin_home_render_id: str | None = None,
    source_trace_history_lane_id: str | None = None,
    source_internal_action_choice_set_id: str | None = None,
    port_map_step_confirmed: bool = True,
    sensor_event_step_confirmed: bool = True,
    runtime_bridge_step_confirmed: bool = True,
    home_surface_step_confirmed: bool = True,
    trace_history_step_confirmed: bool = True,
    internal_action_choice_step_confirmed: bool = True,
    new_runtime_behavior_created: bool = False,
    new_external_control_created: bool = False,
    new_memory_write_created: bool = False,
    new_first_output_created: bool = False,
    new_live_runtime_created: bool = False,
) -> QingyinHostBodyV0IntegratedTraceRecord:
    scope = _scope(milestone_scope)
    status = _integrated_trace_status(
        port_map_step_confirmed=port_map_step_confirmed,
        sensor_event_step_confirmed=sensor_event_step_confirmed,
        runtime_bridge_step_confirmed=runtime_bridge_step_confirmed,
        home_surface_step_confirmed=home_surface_step_confirmed,
        trace_history_step_confirmed=trace_history_step_confirmed,
        internal_action_choice_step_confirmed=internal_action_choice_step_confirmed,
        new_runtime_behavior_created=new_runtime_behavior_created,
        new_external_control_created=new_external_control_created,
        new_memory_write_created=new_memory_write_created,
        new_first_output_created=new_first_output_created,
        new_live_runtime_created=new_live_runtime_created,
    )
    steps = _integrated_trace_steps(
        port_map_step_confirmed=port_map_step_confirmed,
        sensor_event_step_confirmed=sensor_event_step_confirmed,
        runtime_bridge_step_confirmed=runtime_bridge_step_confirmed,
        home_surface_step_confirmed=home_surface_step_confirmed,
        trace_history_step_confirmed=trace_history_step_confirmed,
        internal_action_choice_step_confirmed=internal_action_choice_step_confirmed,
    )
    return QingyinHostBodyV0IntegratedTraceRecord(
        host_body_v0_integrated_trace_id=f"qingyin_host_body_v0_integrated_trace:{_slug(status)}",
        schema_version=INTEGRATED_TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_v0_scope_id=scope.host_body_v0_scope_id,
        source_host_body_port_map_id=source_host_body_port_map_id,
        source_host_sensor_event_set_id=source_host_sensor_event_set_id,
        source_host_runtime_bridge_trace_id=source_host_runtime_bridge_trace_id,
        source_qingyin_home_render_id=source_qingyin_home_render_id,
        source_trace_history_lane_id=source_trace_history_lane_id,
        source_internal_action_choice_set_id=source_internal_action_choice_set_id,
        integrated_trace_steps=steps,
        step_count=len(steps),
        port_map_step_confirmed=port_map_step_confirmed,
        sensor_event_step_confirmed=sensor_event_step_confirmed,
        runtime_bridge_step_confirmed=runtime_bridge_step_confirmed,
        home_surface_step_confirmed=home_surface_step_confirmed,
        trace_history_step_confirmed=trace_history_step_confirmed,
        internal_action_choice_step_confirmed=internal_action_choice_step_confirmed,
        integrated_trace_status=status,
        integrated_trace_summary=_integrated_trace_summary(status),
        new_runtime_behavior_created=new_runtime_behavior_created,
        new_external_control_created=new_external_control_created,
        new_memory_write_created=new_memory_write_created,
        new_first_output_created=new_first_output_created,
        new_live_runtime_created=new_live_runtime_created,
        source_trace_refs=scope.source_trace_refs,
    )


def validate_qingyin_host_body_v0_integrated_trace(
    record: QingyinHostBodyV0IntegratedTraceRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _integrated_trace(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.integrated_trace_status == "host_body_v0_integrated_trace_recorded"
    valid = valid and item.step_count == 6
    valid = valid and all(step.get("verified") is True for step in item.integrated_trace_steps)
    valid = valid and not any(
        (
            item.new_runtime_behavior_created,
            item.new_external_control_created,
            item.new_memory_write_created,
            item.new_first_output_created,
            item.new_live_runtime_created,
        )
    )
    return {
        "valid": valid,
        "status": item.integrated_trace_status,
        "reasons": [] if valid else [item.integrated_trace_status],
    }


def build_qingyin_host_body_v0_milestone_audit(
    *,
    milestone_scope: QingyinHostBodyV0MilestoneScopeRecord | dict[str, object] | None,
    capability_ledger: QingyinHostBodyV0CapabilityLedgerRecord | dict[str, object] | None,
    boundary_ledger: QingyinHostBodyV0BoundaryLedgerRecord | dict[str, object] | None,
    integrated_trace: QingyinHostBodyV0IntegratedTraceRecord | dict[str, object] | None,
    new_capability_created_by_this_package: bool | None = None,
    audit_only_package_confirmed: bool = True,
    force_thought_engine_behavior: bool = False,
    force_production_behavior: bool = False,
) -> QingyinHostBodyV0MilestoneAuditRecord:
    scope = _scope(milestone_scope) if milestone_scope is not None else None
    capability = _capability_ledger(capability_ledger) if capability_ledger is not None else None
    boundary = _boundary_ledger(boundary_ledger) if boundary_ledger is not None else None
    trace = _integrated_trace(integrated_trace) if integrated_trace is not None else None
    package_flags = _package_flags(capability, trace)
    new_capability = (
        capability.new_capability_created_by_this_package
        if capability is not None and new_capability_created_by_this_package is None
        else bool(new_capability_created_by_this_package)
    )
    no_flags = _audit_no_flags(boundary, trace, force_thought_engine_behavior, force_production_behavior)
    reasons = _audit_reasons(
        scope=scope,
        capability=capability,
        boundary=boundary,
        trace=trace,
        package_flags=package_flags,
        no_flags=no_flags,
        new_capability=new_capability,
        audit_only_package_confirmed=audit_only_package_confirmed,
    )
    status = _milestone_audit_status(reasons)
    return QingyinHostBodyV0MilestoneAuditRecord(
        host_body_v0_milestone_audit_id=f"qingyin_host_body_v0_milestone_audit:{_slug(status)}",
        schema_version=MILESTONE_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_v0_scope_id=scope.host_body_v0_scope_id if scope else None,
        source_capability_ledger_id=capability.host_body_v0_capability_ledger_id if capability else None,
        source_boundary_ledger_id=boundary.host_body_v0_boundary_ledger_id if boundary else None,
        source_integrated_trace_id=trace.host_body_v0_integrated_trace_id if trace else None,
        scope_valid=scope is not None and scope.scope_status == "host_body_v0_scope_created",
        capability_ledger_valid=capability is not None and capability.capability_ledger_status == "host_body_v0_capability_ledger_recorded",
        boundary_ledger_valid=boundary is not None and boundary.boundary_ledger_status == "host_body_v0_boundary_ledger_recorded",
        integrated_trace_valid=trace is not None and trace.integrated_trace_status == "host_body_v0_integrated_trace_recorded",
        package_101_verified=package_flags["package_101_verified"],
        package_102_verified=package_flags["package_102_verified"],
        package_103_verified=package_flags["package_103_verified"],
        package_104_verified=package_flags["package_104_verified"],
        package_105_verified=package_flags["package_105_verified"],
        package_106_verified=package_flags["package_106_verified"],
        host_body_v0_established=status == "passed_qingyin_host_body_v0_milestone",
        new_capability_created_by_this_package=new_capability,
        audit_only_package_confirmed=audit_only_package_confirmed,
        no_real_hardware=no_flags["no_real_hardware"],
        no_semantic_vision=no_flags["no_semantic_vision"],
        no_speech_recognition=no_flags["no_speech_recognition"],
        no_task_action_selection=no_flags["no_task_action_selection"],
        no_external_control=no_flags["no_external_control"],
        no_unity_runtime_connection=no_flags["no_unity_runtime_connection"],
        no_memory_layer_write=no_flags["no_memory_layer_write"],
        no_learning_candidate_creation=no_flags["no_learning_candidate_creation"],
        no_automatic_learning_approval=no_flags["no_automatic_learning_approval"],
        no_teacher_approval_created=no_flags["no_teacher_approval_created"],
        no_first_output=no_flags["no_first_output"],
        no_live_runtime_session=no_flags["no_live_runtime_session"],
        no_thought_engine_behavior=no_flags["no_thought_engine_behavior"],
        no_production_behavior=no_flags["no_production_behavior"],
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(reasons),
        source_trace_refs=tuple(
            dict.fromkeys(
                ref
                for record in (scope, capability, boundary, trace)
                if record is not None
                for ref in record.source_trace_refs
            )
        ),
    )


def validate_qingyin_host_body_v0_milestone_audit(
    record: QingyinHostBodyV0MilestoneAuditRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _milestone_audit(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.audit_status == "passed_qingyin_host_body_v0_milestone"
    valid = valid and item.host_body_v0_established
    valid = valid and item.audit_only_package_confirmed
    valid = valid and not item.new_capability_created_by_this_package
    valid = valid and all(
        (
            item.package_101_verified,
            item.package_102_verified,
            item.package_103_verified,
            item.package_104_verified,
            item.package_105_verified,
            item.package_106_verified,
            item.no_real_hardware,
            item.no_semantic_vision,
            item.no_speech_recognition,
            item.no_task_action_selection,
            item.no_external_control,
            item.no_unity_runtime_connection,
            item.no_memory_layer_write,
            item.no_learning_candidate_creation,
            item.no_automatic_learning_approval,
            item.no_teacher_approval_created,
            item.no_first_output,
            item.no_live_runtime_session,
            item.no_thought_engine_behavior,
            item.no_production_behavior,
        )
    )
    return {
        "valid": valid,
        "status": item.audit_status,
        "reasons": [] if valid else list(item.blocked_reasons),
    }


def build_qingyin_host_body_v0_readiness(
    milestone_audit: QingyinHostBodyV0MilestoneAuditRecord | dict[str, object] | None,
) -> QingyinHostBodyV0ReadinessRecord:
    audit = _milestone_audit(milestone_audit) if milestone_audit is not None else None
    passed = audit is not None and audit.audit_status == "passed_qingyin_host_body_v0_milestone"
    if audit is None:
        status = "not_ready_missing_host_body_v0_audit"
    elif passed:
        status = "ready_for_internal_action_home_surface_link_only"
    elif audit.audit_status.startswith("blocked_"):
        status = "blocked_forbidden_authority_detected"
    else:
        status = "not_ready_boundary_failure"
    return QingyinHostBodyV0ReadinessRecord(
        host_body_v0_readiness_id=(
            f"qingyin_host_body_v0_readiness:{audit.host_body_v0_milestone_audit_id}"
            if audit
            else "qingyin_host_body_v0_readiness:missing_audit"
        ),
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_v0_milestone_audit_id=(
            audit.host_body_v0_milestone_audit_id if audit else "missing_host_body_v0_audit"
        ),
        current_verified_capability=SAFE_CLAIM if passed else "Host Body v0 milestone audit did not pass.",
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason=(
            "Connect internal-only Host Body action results to Qingyin Home read-only surface records."
        ),
        ready_for_internal_action_home_surface_link=passed,
        ready_for_teacher_observed_host_body_cli=passed,
        ready_for_runtime_state_persistence_binding=passed,
        ready_for_host_body_v0_to_runtime_state_summary=passed,
        ready_for_real_camera_connection=False,
        ready_for_real_microphone_connection=False,
        ready_for_semantic_vision=False,
        ready_for_speech_recognition=False,
        ready_for_task_engine_action_selection=False,
        ready_for_external_control=False,
        ready_for_unity_runtime_connection=False,
        ready_for_memory_layer_write=False,
        ready_for_learning_candidate_creation=False,
        ready_for_first_output=False,
        ready_for_live_runtime_session=False,
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=audit.source_trace_refs if audit else tuple(),
    )


def validate_qingyin_host_body_v0_readiness(
    record: QingyinHostBodyV0ReadinessRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _readiness(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.readiness_status.startswith("ready_for_")
    valid = valid and all(
        (
            item.ready_for_internal_action_home_surface_link,
            item.ready_for_teacher_observed_host_body_cli,
            item.ready_for_runtime_state_persistence_binding,
            item.ready_for_host_body_v0_to_runtime_state_summary,
        )
    )
    valid = valid and not any(
        (
            item.ready_for_real_camera_connection,
            item.ready_for_real_microphone_connection,
            item.ready_for_semantic_vision,
            item.ready_for_speech_recognition,
            item.ready_for_task_engine_action_selection,
            item.ready_for_external_control,
            item.ready_for_unity_runtime_connection,
            item.ready_for_memory_layer_write,
            item.ready_for_learning_candidate_creation,
            item.ready_for_first_output,
            item.ready_for_live_runtime_session,
        )
    )
    return {
        "valid": valid,
        "status": item.readiness_status,
        "reasons": [] if valid else [item.readiness_status],
    }


def build_demo_qingyin_host_body_v0_milestone_pass() -> dict[str, object]:
    return _build_demo_host_body_v0()


def build_demo_missing_sensor_event_pillar() -> dict[str, object]:
    return _build_demo_host_body_v0(
        fixture_sensor_event_capability_confirmed=False,
        sensor_event_step_confirmed=False,
    )


def build_demo_missing_runtime_bridge_pillar() -> dict[str, object]:
    return _build_demo_host_body_v0(
        runtime_eventframe_bridge_capability_confirmed=False,
        runtime_bridge_step_confirmed=False,
    )


def build_demo_missing_home_surface_pillar() -> dict[str, object]:
    return _build_demo_host_body_v0(
        home_internal_space_surface_capability_confirmed=False,
        home_surface_step_confirmed=False,
    )


def build_demo_missing_trace_history_pillar() -> dict[str, object]:
    return _build_demo_host_body_v0(
        trace_history_lane_capability_confirmed=False,
        trace_history_step_confirmed=False,
    )


def build_demo_missing_internal_action_choice_pillar() -> dict[str, object]:
    return _build_demo_host_body_v0(
        internal_action_choice_capability_confirmed=False,
        internal_action_choice_step_confirmed=False,
    )


def build_demo_blocked_unexpected_new_capability() -> dict[str, object]:
    return _build_demo_host_body_v0(new_capability_created_by_this_package=True)


def build_demo_blocked_external_control_host_body_v0() -> dict[str, object]:
    return _build_demo_host_body_v0(no_external_control=False)


def build_demo_blocked_memory_write_host_body_v0() -> dict[str, object]:
    return _build_demo_host_body_v0(no_memory_layer_write=False)


def build_demo_blocked_first_output_host_body_v0() -> dict[str, object]:
    return _build_demo_host_body_v0(no_first_output=False)


def build_demo_blocked_live_runtime_host_body_v0() -> dict[str, object]:
    return _build_demo_host_body_v0(no_live_runtime_session=False)


def render_qingyin_host_body_v0_milestone_summary_text(
    audit: QingyinHostBodyV0MilestoneAuditRecord | dict[str, object],
    readiness: QingyinHostBodyV0ReadinessRecord | dict[str, object] | None = None,
) -> str:
    item = _milestone_audit(audit)
    readiness_item = _readiness(readiness) if readiness is not None else None
    lines = [
        "Qingyin Host Body v0 Milestone",
        f"audit_status: {item.audit_status}",
        f"host_body_v0_established: {item.host_body_v0_established}",
        f"new_capability_created_by_this_package: {item.new_capability_created_by_this_package}",
        f"no_real_hardware: {item.no_real_hardware}",
        f"no_external_control: {item.no_external_control}",
        f"no_memory_layer_write: {item.no_memory_layer_write}",
        f"no_first_output: {item.no_first_output}",
        f"no_live_runtime_session: {item.no_live_runtime_session}",
    ]
    if readiness_item is not None:
        lines.append(f"readiness_status: {readiness_item.readiness_status}")
    return "\n".join(lines)


def render_qingyin_host_body_v0_capability_table(
    capability_ledger: QingyinHostBodyV0CapabilityLedgerRecord | dict[str, object],
) -> str:
    ledger = _capability_ledger(capability_ledger)
    lines = ["package | capability | verified | commit"]
    for entry in ledger.capability_entries:
        lines.append(
            f"{entry['package']} | {entry['capability']} | {entry['verified']} | {entry['commit']}"
        )
    return "\n".join(lines)


def render_qingyin_host_body_v0_boundary_table(
    boundary_ledger: QingyinHostBodyV0BoundaryLedgerRecord | dict[str, object],
) -> str:
    ledger = _boundary_ledger(boundary_ledger)
    lines = ["boundary | confirmed"]
    for entry in ledger.boundary_entries:
        lines.append(f"{entry['boundary']} | {entry['confirmed']}")
    return "\n".join(lines)


def _scope(record: QingyinHostBodyV0MilestoneScopeRecord | dict[str, object]) -> QingyinHostBodyV0MilestoneScopeRecord:
    if isinstance(record, QingyinHostBodyV0MilestoneScopeRecord):
        return record
    return QingyinHostBodyV0MilestoneScopeRecord.from_dict(record)


def _capability_ledger(
    record: QingyinHostBodyV0CapabilityLedgerRecord | dict[str, object],
) -> QingyinHostBodyV0CapabilityLedgerRecord:
    if isinstance(record, QingyinHostBodyV0CapabilityLedgerRecord):
        return record
    return QingyinHostBodyV0CapabilityLedgerRecord.from_dict(record)


def _boundary_ledger(
    record: QingyinHostBodyV0BoundaryLedgerRecord | dict[str, object],
) -> QingyinHostBodyV0BoundaryLedgerRecord:
    if isinstance(record, QingyinHostBodyV0BoundaryLedgerRecord):
        return record
    return QingyinHostBodyV0BoundaryLedgerRecord.from_dict(record)


def _integrated_trace(
    record: QingyinHostBodyV0IntegratedTraceRecord | dict[str, object],
) -> QingyinHostBodyV0IntegratedTraceRecord:
    if isinstance(record, QingyinHostBodyV0IntegratedTraceRecord):
        return record
    return QingyinHostBodyV0IntegratedTraceRecord.from_dict(record)


def _milestone_audit(
    record: QingyinHostBodyV0MilestoneAuditRecord | dict[str, object],
) -> QingyinHostBodyV0MilestoneAuditRecord:
    if isinstance(record, QingyinHostBodyV0MilestoneAuditRecord):
        return record
    return QingyinHostBodyV0MilestoneAuditRecord.from_dict(record)


def _readiness(record: QingyinHostBodyV0ReadinessRecord | dict[str, object]) -> QingyinHostBodyV0ReadinessRecord:
    if isinstance(record, QingyinHostBodyV0ReadinessRecord):
        return record
    return QingyinHostBodyV0ReadinessRecord.from_dict(record)


def _scope_summary(status: str) -> str:
    if status == "host_body_v0_scope_created":
        return "Host Body v0 scope includes the six required bounded pillars."
    if status == "blocked_missing_required_pillar":
        return "Host Body v0 scope is missing a required pillar."
    return "Host Body v0 scope requested a forbidden capability."


def _capability_entries(**flags: bool) -> tuple[dict[str, Any], ...]:
    entries = [
        {
            "package": "Package 101",
            "capability": "Host Body identity and port map",
            "verified": flags["host_body_identity_capability_confirmed"]
            and flags["host_body_port_map_capability_confirmed"],
            "commit": "f2ed68b",
            "safe_claim": "Defines Qingyin Host Body identity, ports, and boundaries.",
            "forbidden_claims": [
                "real camera access",
                "real microphone access",
                "external control",
            ],
        },
        {
            "package": "Package 102",
            "capability": "Fixture-only read-only sensor event shell",
            "verified": flags["fixture_sensor_event_capability_confirmed"],
            "commit": "9d7f66b",
            "safe_claim": "Creates fixture-only low-level HostBodyEvent records.",
            "forbidden_claims": ["real sensor access", "semantic vision", "speech recognition"],
        },
        {
            "package": "Package 103",
            "capability": "HostBodyEvent to Runtime EventFrame bridge",
            "verified": flags["runtime_eventframe_bridge_capability_confirmed"],
            "commit": "0676341",
            "safe_claim": "Maps fixture-only HostBodyEvents into bounded Runtime EventFrame bridge records.",
            "forbidden_claims": ["live runtime", "live engine invocation", "dynamic scheduling"],
        },
        {
            "package": "Package 104",
            "capability": "Qingyin Home internal-space surface",
            "verified": flags["home_internal_space_surface_capability_confirmed"],
            "commit": "2b655b3",
            "safe_claim": "Represents Qingyin Home as a read-only internal-space event surface.",
            "forbidden_claims": ["Unity runtime connection", "avatar control", "first_output"],
        },
        {
            "package": "Package 105",
            "capability": "Read-only Host Body trace history lane",
            "verified": flags["trace_history_lane_capability_confirmed"],
            "commit": "8f94de6",
            "safe_claim": "Creates read-only in-memory/demo trace history lane records.",
            "forbidden_claims": ["Memory Layer write", "State Persistence write", "file persistence"],
        },
        {
            "package": "Package 106",
            "capability": "Internal-only Host Body action choice",
            "verified": flags["internal_action_choice_capability_confirmed"],
            "commit": "86f1192",
            "safe_claim": "Creates internal-only action choice records.",
            "forbidden_claims": ["Task Engine selected_action", "external control", "teacher approval"],
        },
    ]
    entries.insert(
        1,
        {
            "package": "Package 101",
            "capability": "Host Body port map",
            "verified": flags["host_body_port_map_capability_confirmed"],
            "commit": "f2ed68b",
            "safe_claim": "Defines bounded Host Body port map records.",
            "forbidden_claims": ["real hardware connection", "memory write", "first_output"],
        },
    )
    return tuple(entries)


def _capability_ledger_status(**flags: bool) -> str:
    if not flags["host_body_identity_capability_confirmed"] or not flags["host_body_port_map_capability_confirmed"]:
        return "blocked_missing_host_body_identity_capability"
    if not flags["fixture_sensor_event_capability_confirmed"]:
        return "blocked_missing_sensor_event_capability"
    if not flags["runtime_eventframe_bridge_capability_confirmed"]:
        return "blocked_missing_runtime_bridge_capability"
    if not flags["home_internal_space_surface_capability_confirmed"]:
        return "blocked_missing_home_surface_capability"
    if not flags["trace_history_lane_capability_confirmed"]:
        return "blocked_missing_trace_history_capability"
    if not flags["internal_action_choice_capability_confirmed"]:
        return "blocked_missing_internal_action_choice_capability"
    if flags["new_capability_created_by_this_package"]:
        return "blocked_unexpected_new_capability_detected"
    return "host_body_v0_capability_ledger_recorded"


def _capability_ledger_summary(status: str) -> str:
    if status == "host_body_v0_capability_ledger_recorded":
        return "Host Body v0 capability ledger confirms Packages 101 through 106."
    return "Host Body v0 capability ledger blocked a missing or unexpected capability."


def _boundary_entries(values: dict[str, bool]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {"boundary": key.removeprefix("no_"), "confirmed": value}
        for key, value in sorted(values.items())
    )


def _boundary_ledger_status(values: dict[str, bool]) -> str:
    if not all(
        values[name]
        for name in (
            "no_real_camera_access",
            "no_real_microphone_access",
            "no_camera_capture",
            "no_mic_stream",
            "no_image_storage",
            "no_audio_storage",
        )
    ):
        return "blocked_real_hardware_detected"
    if not all(
        values[name]
        for name in (
            "no_semantic_vision",
            "no_object_recognition",
            "no_face_recognition",
            "no_speech_recognition",
            "no_speaker_identification",
            "no_voice_command",
            "no_language_understanding",
        )
    ):
        return "blocked_semantic_interpretation_detected"
    if not all(
        values[name]
        for name in (
            "no_task_engine_selected_action",
            "no_final_action",
            "no_direct_command",
            "no_sandbox_execution",
        )
    ):
        return "blocked_task_action_detected"
    if not all(
        values[name]
        for name in (
            "no_external_control",
            "no_os_control",
            "no_mouse_control",
            "no_keyboard_control",
            "no_browser_control",
            "no_file_operation",
            "no_network_execution",
            "no_shell_execution",
            "no_external_api_call",
        )
    ):
        return "blocked_external_control_detected"
    if not all(
        values[name]
        for name in (
            "no_unity_runtime_connection",
            "no_unity_scene_mutation",
            "no_avatar_control",
        )
    ):
        return "blocked_unity_runtime_detected"
    if not all(
        values[name]
        for name in (
            "no_memory_layer_write",
            "no_core_memory_write",
            "no_long_term_memory_write",
            "no_archive_memory_write",
            "no_anchor_write",
            "no_state_persistence_write",
            "no_file_persistence",
        )
    ):
        return "blocked_memory_write_detected"
    if not all(
        values[name]
        for name in (
            "no_learning_candidate_creation",
            "no_automatic_learning_approval",
            "no_teacher_approval_created",
        )
    ):
        return "blocked_learning_creation_detected"
    if not all(
        values[name]
        for name in ("no_first_output", "no_free_text_conversation", "no_voice_output")
    ):
        return "blocked_first_output_detected"
    if not all(
        values[name]
        for name in (
            "no_live_runtime_session",
            "no_live_engine_invocation",
            "no_autonomous_scheduler",
            "no_open_ended_loop",
            "no_dynamic_child_event_scheduling",
            "no_thought_engine_behavior",
        )
    ):
        return "blocked_live_runtime_detected"
    if not values["no_production_behavior"]:
        return "blocked_production_behavior_detected"
    return "host_body_v0_boundary_ledger_recorded"


def _boundary_ledger_summary(status: str) -> str:
    if status == "host_body_v0_boundary_ledger_recorded":
        return "Host Body v0 boundary ledger confirms all forbidden capabilities remain absent."
    return "Host Body v0 boundary ledger blocked a forbidden capability."


def _integrated_trace_steps(**flags: bool) -> tuple[dict[str, Any], ...]:
    rows = (
        ("port_map_step_confirmed", 1, "host_body_port_map", "Package 101"),
        ("sensor_event_step_confirmed", 2, "fixture_sensor_events", "Package 102"),
        ("runtime_bridge_step_confirmed", 3, "runtime_eventframe_bridge", "Package 103"),
        ("home_surface_step_confirmed", 4, "qingyin_home_surface", "Package 104"),
        ("trace_history_step_confirmed", 5, "trace_history_lane", "Package 105"),
        ("internal_action_choice_step_confirmed", 6, "internal_action_choice", "Package 106"),
    )
    return tuple(
        {
            "step": step,
            "name": name,
            "source_package": package,
            "verified": flags[key],
        }
        for key, step, name, package in rows
    )


def _integrated_trace_status(**flags: bool) -> str:
    if not flags["port_map_step_confirmed"]:
        return "blocked_missing_port_map_step"
    if not flags["sensor_event_step_confirmed"]:
        return "blocked_missing_sensor_event_step"
    if not flags["runtime_bridge_step_confirmed"]:
        return "blocked_missing_runtime_bridge_step"
    if not flags["home_surface_step_confirmed"]:
        return "blocked_missing_home_surface_step"
    if not flags["trace_history_step_confirmed"]:
        return "blocked_missing_trace_history_step"
    if not flags["internal_action_choice_step_confirmed"]:
        return "blocked_missing_internal_action_choice_step"
    if flags["new_runtime_behavior_created"] or flags["new_live_runtime_created"]:
        return "blocked_forbidden_runtime_behavior_detected"
    if (
        flags["new_external_control_created"]
        or flags["new_memory_write_created"]
        or flags["new_first_output_created"]
    ):
        return "blocked_forbidden_authority_detected"
    return "host_body_v0_integrated_trace_recorded"


def _integrated_trace_summary(status: str) -> str:
    if status == "host_body_v0_integrated_trace_recorded":
        return "Integrated Host Body v0 trace records all six milestone steps."
    return "Integrated Host Body v0 trace is blocked by a missing step or forbidden authority."


def _package_flags(
    capability: QingyinHostBodyV0CapabilityLedgerRecord | None,
    trace: QingyinHostBodyV0IntegratedTraceRecord | None,
) -> dict[str, bool]:
    return {
        "package_101_verified": bool(
            capability
            and trace
            and capability.host_body_identity_capability_confirmed
            and capability.host_body_port_map_capability_confirmed
            and trace.port_map_step_confirmed
        ),
        "package_102_verified": bool(
            capability and trace and capability.fixture_sensor_event_capability_confirmed and trace.sensor_event_step_confirmed
        ),
        "package_103_verified": bool(
            capability and trace and capability.runtime_eventframe_bridge_capability_confirmed and trace.runtime_bridge_step_confirmed
        ),
        "package_104_verified": bool(
            capability and trace and capability.home_internal_space_surface_capability_confirmed and trace.home_surface_step_confirmed
        ),
        "package_105_verified": bool(
            capability and trace and capability.trace_history_lane_capability_confirmed and trace.trace_history_step_confirmed
        ),
        "package_106_verified": bool(
            capability and trace and capability.internal_action_choice_capability_confirmed and trace.internal_action_choice_step_confirmed
        ),
    }


def _audit_no_flags(
    boundary: QingyinHostBodyV0BoundaryLedgerRecord | None,
    trace: QingyinHostBodyV0IntegratedTraceRecord | None,
    force_thought_engine_behavior: bool,
    force_production_behavior: bool,
) -> dict[str, bool]:
    if boundary is None:
        return {
            "no_real_hardware": False,
            "no_semantic_vision": False,
            "no_speech_recognition": False,
            "no_task_action_selection": False,
            "no_external_control": False,
            "no_unity_runtime_connection": False,
            "no_memory_layer_write": False,
            "no_learning_candidate_creation": False,
            "no_automatic_learning_approval": False,
            "no_teacher_approval_created": False,
            "no_first_output": False,
            "no_live_runtime_session": False,
            "no_thought_engine_behavior": not force_thought_engine_behavior,
            "no_production_behavior": not force_production_behavior,
        }
    return {
        "no_real_hardware": all(
            (
                boundary.no_real_camera_access,
                boundary.no_real_microphone_access,
                boundary.no_camera_capture,
                boundary.no_mic_stream,
                boundary.no_image_storage,
                boundary.no_audio_storage,
            )
        ),
        "no_semantic_vision": all(
            (
                boundary.no_semantic_vision,
                boundary.no_object_recognition,
                boundary.no_face_recognition,
                boundary.no_language_understanding,
            )
        ),
        "no_speech_recognition": all(
            (
                boundary.no_speech_recognition,
                boundary.no_speaker_identification,
                boundary.no_voice_command,
            )
        ),
        "no_task_action_selection": all(
            (
                boundary.no_task_engine_selected_action,
                boundary.no_final_action,
                boundary.no_direct_command,
                boundary.no_sandbox_execution,
            )
        ),
        "no_external_control": all(
            (
                boundary.no_external_control,
                boundary.no_os_control,
                boundary.no_mouse_control,
                boundary.no_keyboard_control,
                boundary.no_browser_control,
                boundary.no_file_operation,
                boundary.no_network_execution,
                boundary.no_shell_execution,
                boundary.no_external_api_call,
            )
        ),
        "no_unity_runtime_connection": all(
            (
                boundary.no_unity_runtime_connection,
                boundary.no_unity_scene_mutation,
                boundary.no_avatar_control,
            )
        ),
        "no_memory_layer_write": all(
            (
                boundary.no_memory_layer_write,
                boundary.no_core_memory_write,
                boundary.no_long_term_memory_write,
                boundary.no_archive_memory_write,
                boundary.no_anchor_write,
                boundary.no_state_persistence_write,
                boundary.no_file_persistence,
            )
        ),
        "no_learning_candidate_creation": boundary.no_learning_candidate_creation,
        "no_automatic_learning_approval": boundary.no_automatic_learning_approval,
        "no_teacher_approval_created": boundary.no_teacher_approval_created,
        "no_first_output": all(
            (
                boundary.no_first_output,
                boundary.no_free_text_conversation,
                boundary.no_voice_output,
                not (trace and trace.new_first_output_created),
            )
        ),
        "no_live_runtime_session": all(
            (
                boundary.no_live_runtime_session,
                boundary.no_live_engine_invocation,
                boundary.no_autonomous_scheduler,
                boundary.no_open_ended_loop,
                boundary.no_dynamic_child_event_scheduling,
                not (trace and trace.new_runtime_behavior_created),
                not (trace and trace.new_live_runtime_created),
            )
        ),
        "no_thought_engine_behavior": boundary.no_thought_engine_behavior and not force_thought_engine_behavior,
        "no_production_behavior": boundary.no_production_behavior and not force_production_behavior,
    }


def _audit_reasons(
    *,
    scope: QingyinHostBodyV0MilestoneScopeRecord | None,
    capability: QingyinHostBodyV0CapabilityLedgerRecord | None,
    boundary: QingyinHostBodyV0BoundaryLedgerRecord | None,
    trace: QingyinHostBodyV0IntegratedTraceRecord | None,
    package_flags: dict[str, bool],
    no_flags: dict[str, bool],
    new_capability: bool,
    audit_only_package_confirmed: bool,
) -> list[str]:
    reasons: list[str] = []
    if scope is None:
        reasons.append("missing_scope")
    elif scope.scope_status != "host_body_v0_scope_created":
        reasons.append("missing_scope")
    if capability is None:
        reasons.append("missing_capability_ledger")
    if boundary is None:
        reasons.append("missing_boundary_ledger")
    if trace is None:
        reasons.append("missing_integrated_trace")
    for package_key, reason in (
        ("package_101_verified", "package_101_unverified"),
        ("package_102_verified", "package_102_unverified"),
        ("package_103_verified", "package_103_unverified"),
        ("package_104_verified", "package_104_unverified"),
        ("package_105_verified", "package_105_unverified"),
        ("package_106_verified", "package_106_unverified"),
    ):
        if not package_flags[package_key]:
            reasons.append(reason)
    if new_capability or not audit_only_package_confirmed:
        reasons.append("unexpected_new_capability")
    for flag, reason in (
        ("no_real_hardware", "real_hardware"),
        ("no_semantic_vision", "semantic_interpretation"),
        ("no_speech_recognition", "speech_recognition"),
        ("no_task_action_selection", "task_action_selection"),
        ("no_external_control", "external_control"),
        ("no_unity_runtime_connection", "unity_runtime"),
        ("no_memory_layer_write", "memory_write"),
        ("no_learning_candidate_creation", "learning_candidate_creation"),
        ("no_automatic_learning_approval", "learning_candidate_creation"),
        ("no_teacher_approval_created", "teacher_approval"),
        ("no_first_output", "first_output"),
        ("no_live_runtime_session", "live_runtime"),
        ("no_thought_engine_behavior", "production_behavior"),
        ("no_production_behavior", "production_behavior"),
    ):
        if not no_flags[flag]:
            reasons.append(reason)
    return list(dict.fromkeys(reasons))


def _milestone_audit_status(reasons: list[str]) -> str:
    priority = (
        ("missing_scope", "blocked_missing_scope"),
        ("missing_capability_ledger", "blocked_missing_capability_ledger"),
        ("missing_boundary_ledger", "blocked_missing_boundary_ledger"),
        ("missing_integrated_trace", "blocked_missing_integrated_trace"),
        ("package_101_unverified", "blocked_package_101_unverified"),
        ("package_102_unverified", "blocked_package_102_unverified"),
        ("package_103_unverified", "blocked_package_103_unverified"),
        ("package_104_unverified", "blocked_package_104_unverified"),
        ("package_105_unverified", "blocked_package_105_unverified"),
        ("package_106_unverified", "blocked_package_106_unverified"),
        ("unexpected_new_capability", "blocked_unexpected_new_capability_detected"),
        ("real_hardware", "blocked_real_hardware_detected"),
        ("semantic_interpretation", "blocked_semantic_interpretation_detected"),
        ("speech_recognition", "blocked_speech_recognition_detected"),
        ("task_action_selection", "blocked_task_action_selection_detected"),
        ("external_control", "blocked_external_control_detected"),
        ("unity_runtime", "blocked_unity_runtime_detected"),
        ("memory_write", "blocked_memory_write_detected"),
        ("learning_candidate_creation", "blocked_learning_candidate_creation_detected"),
        ("teacher_approval", "blocked_teacher_approval_created"),
        ("first_output", "blocked_first_output_detected"),
        ("live_runtime", "blocked_live_runtime_detected"),
        ("production_behavior", "blocked_production_behavior_detected"),
    )
    for reason, status in priority:
        if reason in reasons:
            return status
    return "passed_qingyin_host_body_v0_milestone"


def _readiness_summary(status: str) -> str:
    if status.startswith("ready_for_"):
        return "Host Body v0 milestone is ready for the next bounded Host Body package."
    if status == "not_ready_missing_host_body_v0_audit":
        return "Host Body v0 readiness is missing the milestone audit."
    return "Host Body v0 readiness is blocked by the milestone audit boundary."


def _build_demo_host_body_v0(
    *,
    host_body_identity_capability_confirmed: bool = True,
    host_body_port_map_capability_confirmed: bool = True,
    fixture_sensor_event_capability_confirmed: bool = True,
    runtime_eventframe_bridge_capability_confirmed: bool = True,
    home_internal_space_surface_capability_confirmed: bool = True,
    trace_history_lane_capability_confirmed: bool = True,
    internal_action_choice_capability_confirmed: bool = True,
    port_map_step_confirmed: bool = True,
    sensor_event_step_confirmed: bool = True,
    runtime_bridge_step_confirmed: bool = True,
    home_surface_step_confirmed: bool = True,
    trace_history_step_confirmed: bool = True,
    internal_action_choice_step_confirmed: bool = True,
    new_capability_created_by_this_package: bool = False,
    no_external_control: bool = True,
    no_memory_layer_write: bool = True,
    no_first_output: bool = True,
    no_live_runtime_session: bool = True,
) -> dict[str, object]:
    source_ids = _demo_source_ids()
    scope = build_qingyin_host_body_v0_milestone_scope(
        source_trace_refs=("package_107_demo",)
    )
    capability = build_qingyin_host_body_v0_capability_ledger(
        milestone_scope=scope,
        host_body_identity_capability_confirmed=host_body_identity_capability_confirmed,
        host_body_port_map_capability_confirmed=host_body_port_map_capability_confirmed,
        fixture_sensor_event_capability_confirmed=fixture_sensor_event_capability_confirmed,
        runtime_eventframe_bridge_capability_confirmed=runtime_eventframe_bridge_capability_confirmed,
        home_internal_space_surface_capability_confirmed=home_internal_space_surface_capability_confirmed,
        trace_history_lane_capability_confirmed=trace_history_lane_capability_confirmed,
        internal_action_choice_capability_confirmed=internal_action_choice_capability_confirmed,
        new_capability_created_by_this_package=new_capability_created_by_this_package,
    )
    boundary = build_qingyin_host_body_v0_boundary_ledger(
        milestone_scope=scope,
        no_external_control=no_external_control,
        no_memory_layer_write=no_memory_layer_write,
        no_first_output=no_first_output,
        no_live_runtime_session=no_live_runtime_session,
    )
    trace = build_qingyin_host_body_v0_integrated_trace(
        milestone_scope=scope,
        source_host_body_port_map_id=source_ids["source_host_body_port_map_id"],
        source_host_sensor_event_set_id=source_ids["source_host_sensor_event_set_id"],
        source_host_runtime_bridge_trace_id=source_ids["source_host_runtime_bridge_trace_id"],
        source_qingyin_home_render_id=source_ids["source_qingyin_home_render_id"],
        source_trace_history_lane_id=source_ids["source_trace_history_lane_id"],
        source_internal_action_choice_set_id=source_ids["source_internal_action_choice_set_id"],
        port_map_step_confirmed=port_map_step_confirmed,
        sensor_event_step_confirmed=sensor_event_step_confirmed,
        runtime_bridge_step_confirmed=runtime_bridge_step_confirmed,
        home_surface_step_confirmed=home_surface_step_confirmed,
        trace_history_step_confirmed=trace_history_step_confirmed,
        internal_action_choice_step_confirmed=internal_action_choice_step_confirmed,
    )
    audit = build_qingyin_host_body_v0_milestone_audit(
        milestone_scope=scope,
        capability_ledger=capability,
        boundary_ledger=boundary,
        integrated_trace=trace,
    )
    readiness = build_qingyin_host_body_v0_readiness(audit)
    return {
        "host_body_v0_scope": scope.to_dict(),
        "host_body_v0_capability_ledger": capability.to_dict(),
        "host_body_v0_boundary_ledger": boundary.to_dict(),
        "host_body_v0_integrated_trace": trace.to_dict(),
        "host_body_v0_milestone_audit": audit.to_dict(),
        "host_body_v0_readiness": readiness.to_dict(),
        "rendered_host_body_v0_milestone_summary": render_qingyin_host_body_v0_milestone_summary_text(
            audit, readiness
        ),
        "rendered_host_body_v0_capability_table": render_qingyin_host_body_v0_capability_table(
            capability
        ),
        "rendered_host_body_v0_boundary_table": render_qingyin_host_body_v0_boundary_table(
            boundary
        ),
    }


def _demo_source_ids() -> dict[str, str]:
    port = build_demo_qingyin_host_body_port_map()
    sensor = build_demo_mixed_host_sensor_event_set()
    bridge = build_demo_mixed_host_body_runtime_bridge()
    home = build_demo_qingyin_home_internal_space_surface()
    trace = build_demo_full_host_body_trace_history_lane()
    action = build_demo_camera_change_marks_interesting()
    return {
        "source_host_body_port_map_id": port["host_body_port_map"]["host_body_port_map_id"],
        "source_host_sensor_event_set_id": sensor["host_body_sensor_event_set"]["host_sensor_event_set_id"],
        "source_host_runtime_bridge_trace_id": bridge["host_body_runtime_bridge_trace"]["host_runtime_bridge_trace_id"],
        "source_qingyin_home_render_id": home["home_internal_space_render"]["home_internal_space_render_id"],
        "source_trace_history_lane_id": trace["trace_history_lane"]["trace_history_lane_id"],
        "source_internal_action_choice_set_id": action["internal_action_choice_set"]["internal_action_choice_set_id"],
    }
