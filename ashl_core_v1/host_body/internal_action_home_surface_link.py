"""Read-only links from Host Body internal action results to Qingyin Home surface records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit import (
    build_demo_host_body_embodied_learning_closed_loop_pass,
    validate_host_body_embodied_learning_closed_loop_milestone_audit,
)
from ashl_core_v1.host_body.host_body_working_readback_integration import (
    build_demo_trace_spine_raw_evidence_boundary,
    validate_trace_spine_raw_evidence_boundary,
)
from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
    build_demo_qingyin_home_internal_space_surface,
    validate_qingyin_home_internal_space_surface_audit,
)


SOURCE_ENGINE = "host_body"

PLAN_SCHEMA_VERSION = "qingyin_internal_action_home_surface_link_plan_v0"
MAPPING_SCHEMA_VERSION = "qingyin_internal_action_home_surface_mapping_v0"
STATUS_LIGHT_LINK_SCHEMA_VERSION = "qingyin_internal_action_home_status_light_link_v0"
TEACHER_OBSERVED_LINK_SCHEMA_VERSION = (
    "qingyin_internal_action_home_teacher_observed_link_v0"
)
RENDER_SNAPSHOT_LINK_SCHEMA_VERSION = (
    "qingyin_internal_action_home_render_snapshot_link_v0"
)
TRACE_SCHEMA_VERSION = "qingyin_internal_action_home_surface_link_trace_v0"
AUDIT_SCHEMA_VERSION = "qingyin_internal_action_home_surface_link_audit_v0"
READINESS_SCHEMA_VERSION = "qingyin_internal_action_home_surface_link_readiness_v0"

LINK_NAME = "internal_action_home_surface_link"
LINK_KIND = "read_only_home_surface_record_link"

ALLOWED_INTERNAL_ACTION_KINDS = (
    "observe_again",
    "mark_event_interesting",
    "mark_uncertain",
    "request_teacher_review",
    "shift_internal_focus",
    "update_home_status",
    "pause_event_processing",
)
ALLOWED_SURFACE_TARGETS = (
    "home_status_light_record",
    "teacher_observed_surface_record",
    "home_render_snapshot_record",
    "home_read_only_card_record",
)
FORBIDDEN_SURFACE_TARGETS = (
    "live_unity_scene",
    "real_screen",
    "real_sound_output",
    "external_chat_message",
    "voice_output",
    "desktop_notification",
    "browser_ui",
    "file_output",
    "network_dashboard",
)

ALLOWED_STATUS_LIGHT_KINDS = (
    "uncertainty",
    "interesting_event",
    "teacher_review_requested",
    "observe_again",
    "internal_focus_shifted",
    "home_status_updated",
    "event_processing_paused",
    "idle",
    "boundary_warning",
    "none",
)

ACTION_SURFACE_RULES: dict[str, dict[str, str | None]] = {
    "mark_uncertain": {
        "mapping_kind": "mark_uncertain_to_home_surface",
        "mapping_status": "home_surface_mapping_created_uncertainty",
        "status_light_kind": "uncertainty",
        "teacher_observed_update_kind": "uncertainty_marker_visible",
        "render_snapshot_kind": "uncertainty_render_snapshot",
        "audit_status": "passed_uncertainty_home_surface_link",
    },
    "request_teacher_review": {
        "mapping_kind": "request_teacher_review_to_home_surface",
        "mapping_status": "home_surface_mapping_created_teacher_review",
        "status_light_kind": "teacher_review_requested",
        "teacher_observed_update_kind": "teacher_review_request_visible",
        "render_snapshot_kind": "teacher_review_request_render_snapshot",
        "audit_status": "passed_teacher_review_home_surface_link",
    },
    "observe_again": {
        "mapping_kind": "observe_again_to_home_surface",
        "mapping_status": "home_surface_mapping_created_observe_again",
        "status_light_kind": "observe_again",
        "teacher_observed_update_kind": "observe_again_recommendation_visible",
        "render_snapshot_kind": "observe_again_render_snapshot",
        "audit_status": "passed_observe_again_home_surface_link",
    },
    "mark_event_interesting": {
        "mapping_kind": "mark_interesting_to_home_surface",
        "mapping_status": "home_surface_mapping_created_interesting_event",
        "status_light_kind": "interesting_event",
        "teacher_observed_update_kind": "interesting_event_marker_visible",
        "render_snapshot_kind": "internal_action_status_render_snapshot",
        "audit_status": "passed_internal_action_home_surface_link",
    },
    "pause_event_processing": {
        "mapping_kind": "pause_event_processing_to_home_surface",
        "mapping_status": "home_surface_mapping_created_pause_event_processing",
        "status_light_kind": "event_processing_paused",
        "teacher_observed_update_kind": "pause_event_processing_marker_visible",
        "render_snapshot_kind": "pause_event_processing_render_snapshot",
        "audit_status": "passed_pause_event_processing_home_surface_link",
    },
    "shift_internal_focus": {
        "mapping_kind": "shift_internal_focus_to_home_surface",
        "mapping_status": "home_surface_mapping_created",
        "status_light_kind": "internal_focus_shifted",
        "teacher_observed_update_kind": "readback_reason_visible",
        "render_snapshot_kind": "internal_action_status_render_snapshot",
        "audit_status": "passed_internal_action_home_surface_link",
    },
    "update_home_status": {
        "mapping_kind": "update_home_status_to_home_surface",
        "mapping_status": "home_surface_mapping_created_update_home_status",
        "status_light_kind": "home_status_updated",
        "teacher_observed_update_kind": "no_teacher_surface_update",
        "render_snapshot_kind": "home_status_update_render_snapshot",
        "audit_status": "passed_internal_action_home_surface_link",
    },
}

SAFE_CLAIM = (
    "ASHL Core v1 can link internal-only Host Body action results to Qingyin Home "
    "read-only status light, teacher-observed surface, and render snapshot records."
)
BLOCKED_CLAIMS = (
    "real_screen_update",
    "unity_operation",
    "avatar_control",
    "external_message",
    "voice_output",
    "computer_control",
    "task_engine_action_selection",
    "memory_write",
    "first_output",
    "live_runtime_session",
    "awake_claim",
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


def _record(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return None


def _get(value: Any, key: str, default: Any = None) -> Any:
    record = _record(value)
    if record is None:
        return default
    return record.get(key, default)


def _tuple_of_str(value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(str(item) for item in value)


def _validation(status: str, pass_statuses: set[str]) -> dict[str, object]:
    valid = status in pass_statuses
    return {"valid": valid, "status": status, "reasons": [] if valid else [status]}


@dataclass(frozen=True)
class InternalActionHomeSurfaceLinkPlanRecord:
    home_surface_link_plan_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_closed_loop_milestone_audit_id: str | None
    source_home_surface_audit_id: str | None
    source_trace_spine_boundary_id: str | None
    link_name: str
    link_kind: str
    allowed_internal_action_kinds: tuple[str, ...]
    allowed_surface_targets: tuple[str, ...]
    forbidden_surface_targets: tuple[str, ...]
    read_only_surface_link_allowed: bool
    teacher_observed_surface_link_allowed: bool
    status_light_link_allowed: bool
    render_snapshot_link_allowed: bool
    unity_runtime_mutation_allowed: bool
    actual_screen_mutation_allowed: bool
    actual_sound_output_allowed: bool
    external_message_allowed: bool
    file_write_allowed: bool
    network_output_allowed: bool
    task_action_selection_allowed: bool
    direct_command_allowed: bool
    external_control_allowed: bool
    memory_write_allowed: bool
    first_output_allowed: bool
    live_runtime_session_allowed: bool
    plan_status: str
    plan_summary: str
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class InternalActionHomeSurfaceMappingRecord:
    home_surface_mapping_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_link_plan_id: str
    source_internal_action_result_id: str | None
    source_readback_influenced_result_id: str | None
    selected_internal_action_kind: str
    mapping_kind: str
    mapping_status: str
    mapping_summary: str
    target_status_light_kind: str | None
    target_teacher_observed_update_kind: str | None
    target_render_snapshot_kind: str | None
    readback_reason_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    read_only_mapping: bool
    record_only_mapping: bool
    actual_surface_mutated: bool
    unity_runtime_mutated: bool
    screen_mutated: bool
    sound_played: bool
    external_message_created: bool
    file_written: bool
    network_output_created: bool
    task_selected_action_created: bool
    direct_command_created: bool
    external_control_created: bool
    memory_write_performed: bool
    first_output_created: bool
    live_runtime_session_created: bool

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class InternalActionHomeStatusLightLinkRecord:
    home_status_light_link_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_mapping_id: str
    status_light_kind: str
    status_light_state: str
    status_light_label: str
    status_light_reason: str
    existing_home_status_light_schema_reused: bool
    target_home_status_light_id: str | None
    status_light_link_status: str
    status_light_link_summary: str
    read_only_status_record: bool
    record_only_status_link: bool
    actual_status_light_mutated: bool
    actual_screen_mutated: bool
    unity_runtime_mutated: bool
    sound_played: bool
    external_message_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class InternalActionHomeTeacherObservedLinkRecord:
    home_teacher_observed_link_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_mapping_id: str
    teacher_observed_update_kind: str
    teacher_observed_sections: tuple[str, ...]
    teacher_observed_summary: str
    existing_teacher_observed_schema_reused: bool
    target_teacher_observed_surface_id: str | None
    teacher_observed_link_status: str
    teacher_review_request_visible: bool
    teacher_action_required_visible: bool
    teacher_approval_created: bool
    learning_approval_created: bool
    memory_write_approval_created: bool
    actual_surface_mutated: bool
    external_message_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class InternalActionHomeRenderSnapshotLinkRecord:
    home_render_snapshot_link_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_mapping_id: str
    render_snapshot_kind: str
    render_snapshot_text: str
    render_snapshot_payload: dict[str, Any]
    existing_home_render_schema_reused: bool
    target_home_render_id: str | None
    render_snapshot_link_status: str
    render_snapshot_link_summary: str
    read_only_render_snapshot: bool
    record_only_render_link: bool
    unity_runtime_started: bool
    unity_scene_mutated: bool
    avatar_control_created: bool
    actual_screen_mutated: bool
    file_written: bool
    network_output_created: bool
    first_output_created: bool
    production_behavior_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class InternalActionHomeSurfaceLinkTraceRecord:
    home_surface_link_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_link_plan_id: str
    mapping_ids: tuple[str, ...]
    status_light_link_ids: tuple[str, ...]
    teacher_observed_link_ids: tuple[str, ...]
    render_snapshot_link_ids: tuple[str, ...]
    trace_kind: str
    trace_status: str
    trace_summary: str
    mapping_count: int
    status_light_link_count: int
    teacher_observed_link_count: int
    render_snapshot_link_count: int
    read_only_surface_links_confirmed: bool
    record_only_links_confirmed: bool
    trace_spine_boundary_preserved: bool
    raw_trace_append_only_confirmed: bool
    raw_trace_summarized_during_service_period: bool
    memory_layer_stores_interpretation_only: bool
    source_trace_refs_preserved: bool
    concept_id_embedded_into_raw_history: bool
    actual_surface_mutated: bool
    unity_runtime_mutated: bool
    screen_mutated: bool
    sound_played: bool
    external_message_created: bool
    file_written: bool
    network_output_created: bool
    task_selected_action_created: bool
    direct_command_created: bool
    external_control_created: bool
    memory_write_performed: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class InternalActionHomeSurfaceLinkAudit:
    home_surface_link_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_link_plan_id: str | None
    source_home_surface_link_trace_id: str | None
    source_closed_loop_milestone_audit_id: str | None
    source_trace_spine_boundary_id: str | None
    plan_valid: bool
    mappings_valid: bool
    status_light_links_valid: bool
    teacher_observed_links_valid: bool
    render_snapshot_links_valid: bool
    link_trace_valid: bool
    closed_loop_milestone_valid: bool
    trace_spine_boundary_valid: bool
    internal_action_home_surface_link_confirmed: bool
    read_only_surface_confirmed: bool
    record_only_link_confirmed: bool
    trace_spine_format_unified_confirmed: bool
    trace_spine_time_aligned_confirmed: bool
    raw_trace_append_only_confirmed: bool
    raw_trace_not_summarized_during_service_period: bool
    memory_layer_stores_interpretation_only_confirmed: bool
    source_trace_refs_preserved_confirmed: bool
    concept_id_not_embedded_into_raw_history_confirmed: bool
    no_unity_runtime_mutation: bool
    no_unity_scene_mutation: bool
    no_avatar_control: bool
    no_actual_screen_mutation: bool
    no_actual_sound_output: bool
    no_external_message_output: bool
    no_file_write: bool
    no_network_output: bool
    no_task_selected_action: bool
    no_final_action: bool
    no_direct_command: bool
    no_sandbox_execution: bool
    no_external_control: bool
    no_memory_layer_write: bool
    no_long_term_memory_write: bool
    no_core_memory_write: bool
    no_learning_candidate_creation: bool
    no_concept_candidate_creation: bool
    no_reviewed_concept_creation: bool
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

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class InternalActionHomeSurfaceLinkReadinessRecord:
    home_surface_link_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_home_surface_link_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_runtime_state_summary_session_shell: bool
    ready_for_bounded_embodied_loop_runner: bool
    ready_for_no_codex_teacher_console_flow: bool
    ready_for_session_end_review_promote_gate: bool
    ready_for_no_codex_fixture_growth_loop_milestone_audit: bool
    ready_for_unity_runtime_connection: bool
    ready_for_actual_screen_mutation: bool
    ready_for_external_control: bool
    ready_for_task_engine_action_selection: bool
    ready_for_long_term_memory_write: bool
    ready_for_core_memory_write: bool
    ready_for_first_output: bool
    ready_for_live_runtime_session: bool
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


def _demo_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    closed_payload = build_demo_host_body_embodied_learning_closed_loop_pass()
    home_payload = build_demo_qingyin_home_internal_space_surface()
    boundary_payload = build_demo_trace_spine_raw_evidence_boundary()
    return (
        closed_payload["host_body_embodied_learning_closed_loop_milestone_audit"],
        home_payload["home_internal_space_surface_audit"],
        boundary_payload["trace_spine_raw_evidence_boundary"],
    )


def build_internal_action_home_surface_link_plan(
    *,
    closed_loop_milestone_audit: Any | None,
    home_surface_audit: Any | None,
    trace_spine_boundary: Any | None,
    read_only_surface_link_allowed: bool = True,
    teacher_observed_surface_link_allowed: bool = True,
    status_light_link_allowed: bool = True,
    render_snapshot_link_allowed: bool = True,
    unity_runtime_mutation_allowed: bool = False,
    actual_screen_mutation_allowed: bool = False,
    actual_sound_output_allowed: bool = False,
    external_message_allowed: bool = False,
    file_write_allowed: bool = False,
    network_output_allowed: bool = False,
    task_action_selection_allowed: bool = False,
    direct_command_allowed: bool = False,
    external_control_allowed: bool = False,
    memory_write_allowed: bool = False,
    first_output_allowed: bool = False,
    live_runtime_session_allowed: bool = False,
) -> InternalActionHomeSurfaceLinkPlanRecord:
    closed_loop = _record(closed_loop_milestone_audit)
    home_audit = _record(home_surface_audit)
    boundary = _record(trace_spine_boundary)
    if closed_loop is None:
        status = "blocked_missing_closed_loop_milestone_audit"
    elif home_audit is None:
        status = "blocked_missing_home_surface_audit"
    elif boundary is None:
        status = "blocked_missing_trace_spine_boundary"
    elif not all(
        (
            read_only_surface_link_allowed,
            teacher_observed_surface_link_allowed,
            status_light_link_allowed,
            render_snapshot_link_allowed,
        )
    ):
        status = "blocked_forbidden_authority_detected"
    elif unity_runtime_mutation_allowed:
        status = "blocked_unity_runtime_mutation_allowed"
    elif actual_screen_mutation_allowed:
        status = "blocked_actual_screen_mutation_allowed"
    elif external_message_allowed:
        status = "blocked_external_message_allowed"
    elif task_action_selection_allowed:
        status = "blocked_task_action_selection_allowed"
    elif direct_command_allowed:
        status = "blocked_direct_command_allowed"
    elif external_control_allowed:
        status = "blocked_external_control_allowed"
    elif memory_write_allowed:
        status = "blocked_memory_write_allowed"
    elif first_output_allowed:
        status = "blocked_first_output_allowed"
    elif live_runtime_session_allowed:
        status = "blocked_live_runtime_allowed"
    elif any((actual_sound_output_allowed, file_write_allowed, network_output_allowed)):
        status = "blocked_forbidden_authority_detected"
    else:
        status = "home_surface_link_plan_created"
    return InternalActionHomeSurfaceLinkPlanRecord(
        home_surface_link_plan_id=f"internal_action_home_surface_link_plan:{status}",
        schema_version=PLAN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_closed_loop_milestone_audit_id=_get(
            closed_loop, "closed_loop_milestone_audit_id"
        ),
        source_home_surface_audit_id=_get(home_audit, "home_surface_audit_id"),
        source_trace_spine_boundary_id=_get(boundary, "trace_spine_boundary_id"),
        link_name=LINK_NAME,
        link_kind=LINK_KIND,
        allowed_internal_action_kinds=ALLOWED_INTERNAL_ACTION_KINDS,
        allowed_surface_targets=ALLOWED_SURFACE_TARGETS,
        forbidden_surface_targets=FORBIDDEN_SURFACE_TARGETS,
        read_only_surface_link_allowed=read_only_surface_link_allowed,
        teacher_observed_surface_link_allowed=teacher_observed_surface_link_allowed,
        status_light_link_allowed=status_light_link_allowed,
        render_snapshot_link_allowed=render_snapshot_link_allowed,
        unity_runtime_mutation_allowed=unity_runtime_mutation_allowed,
        actual_screen_mutation_allowed=actual_screen_mutation_allowed,
        actual_sound_output_allowed=actual_sound_output_allowed,
        external_message_allowed=external_message_allowed,
        file_write_allowed=file_write_allowed,
        network_output_allowed=network_output_allowed,
        task_action_selection_allowed=task_action_selection_allowed,
        direct_command_allowed=direct_command_allowed,
        external_control_allowed=external_control_allowed,
        memory_write_allowed=memory_write_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
        plan_status=status,
        plan_summary=(
            "Plan allows read-only, record-only links from internal Host Body action "
            "results to Qingyin Home status, teacher-observed, and render records."
        ),
        source_trace_refs=(
            str(_get(closed_loop, "closed_loop_milestone_audit_id", "")),
            str(_get(home_audit, "home_surface_audit_id", "")),
            str(_get(boundary, "trace_spine_boundary_id", "")),
        ),
    )


def validate_internal_action_home_surface_link_plan(record: Any) -> dict[str, object]:
    data = _record(record)
    if data is None:
        return {"valid": False, "status": "missing", "reasons": ["missing"]}
    valid = data.get("plan_status") == "home_surface_link_plan_created"
    valid = valid and all(
        bool(data.get(name))
        for name in (
            "read_only_surface_link_allowed",
            "teacher_observed_surface_link_allowed",
            "status_light_link_allowed",
            "render_snapshot_link_allowed",
        )
    )
    valid = valid and not any(
        bool(data.get(name))
        for name in (
            "unity_runtime_mutation_allowed",
            "actual_screen_mutation_allowed",
            "actual_sound_output_allowed",
            "external_message_allowed",
            "file_write_allowed",
            "network_output_allowed",
            "task_action_selection_allowed",
            "direct_command_allowed",
            "external_control_allowed",
            "memory_write_allowed",
            "first_output_allowed",
            "live_runtime_session_allowed",
        )
    )
    return {
        "valid": valid,
        "status": data.get("plan_status"),
        "reasons": [] if valid else [str(data.get("plan_status"))],
    }


def build_internal_action_home_surface_mapping(
    *,
    home_surface_link_plan: Any,
    selected_internal_action_kind: str,
    internal_action_result_valid: bool = True,
    source_internal_action_result_id: str | None = "host_body_internal_action_result:demo",
    source_readback_influenced_result_id: str | None = (
        "host_body_readback_influenced_internal_action_result:demo"
    ),
    readback_reason_refs: tuple[str, ...] = ("readback_reason:demo",),
    source_trace_refs: tuple[str, ...] = ("host_body_trace:demo",),
    actual_surface_mutated: bool = False,
    unity_runtime_mutated: bool = False,
    screen_mutated: bool = False,
    sound_played: bool = False,
    external_message_created: bool = False,
    file_written: bool = False,
    network_output_created: bool = False,
    task_selected_action_created: bool = False,
    direct_command_created: bool = False,
    external_control_created: bool = False,
    memory_write_performed: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> InternalActionHomeSurfaceMappingRecord:
    plan = _record(home_surface_link_plan) or {}
    rule = ACTION_SURFACE_RULES.get(selected_internal_action_kind)
    if not validate_internal_action_home_surface_link_plan(plan)["valid"]:
        status = "blocked_invalid_internal_action_result"
    elif not internal_action_result_valid:
        status = "blocked_invalid_internal_action_result"
    elif rule is None:
        status = "blocked_forbidden_internal_action_kind"
    elif actual_surface_mutated:
        status = "blocked_actual_surface_mutation_detected"
    elif unity_runtime_mutated:
        status = "blocked_unity_runtime_mutation_detected"
    elif screen_mutated:
        status = "blocked_screen_mutation_detected"
    elif external_message_created:
        status = "blocked_external_message_detected"
    elif first_output_created:
        status = "blocked_first_output_detected"
    elif live_runtime_session_created:
        status = "blocked_live_runtime_detected"
    elif any(
        (
            sound_played,
            file_written,
            network_output_created,
            task_selected_action_created,
            direct_command_created,
            external_control_created,
            memory_write_performed,
        )
    ):
        status = "blocked_actual_surface_mutation_detected"
    else:
        status = str(rule["mapping_status"])
    mapping_kind = str(rule["mapping_kind"]) if rule else "blocked_mapping"
    return InternalActionHomeSurfaceMappingRecord(
        home_surface_mapping_id=f"internal_action_home_surface_mapping:{selected_internal_action_kind}:{status}",
        schema_version=MAPPING_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_link_plan_id=str(_get(plan, "home_surface_link_plan_id", "")),
        source_internal_action_result_id=source_internal_action_result_id,
        source_readback_influenced_result_id=source_readback_influenced_result_id,
        selected_internal_action_kind=selected_internal_action_kind,
        mapping_kind=mapping_kind,
        mapping_status=status,
        mapping_summary=(
            f"{selected_internal_action_kind} maps to read-only Qingyin Home surface records."
        ),
        target_status_light_kind=str(rule["status_light_kind"]) if rule else None,
        target_teacher_observed_update_kind=(
            str(rule["teacher_observed_update_kind"]) if rule else None
        ),
        target_render_snapshot_kind=str(rule["render_snapshot_kind"]) if rule else None,
        readback_reason_refs=_tuple_of_str(readback_reason_refs),
        source_trace_refs=_tuple_of_str(source_trace_refs),
        read_only_mapping=True,
        record_only_mapping=True,
        actual_surface_mutated=actual_surface_mutated,
        unity_runtime_mutated=unity_runtime_mutated,
        screen_mutated=screen_mutated,
        sound_played=sound_played,
        external_message_created=external_message_created,
        file_written=file_written,
        network_output_created=network_output_created,
        task_selected_action_created=task_selected_action_created,
        direct_command_created=direct_command_created,
        external_control_created=external_control_created,
        memory_write_performed=memory_write_performed,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )


def validate_internal_action_home_surface_mapping(record: Any) -> dict[str, object]:
    return _validation(
        str(_get(record, "mapping_status", "missing")),
        {
            "home_surface_mapping_created",
            "home_surface_mapping_created_uncertainty",
            "home_surface_mapping_created_teacher_review",
            "home_surface_mapping_created_observe_again",
            "home_surface_mapping_created_interesting_event",
            "home_surface_mapping_created_pause_event_processing",
            "home_surface_mapping_created_update_home_status",
        },
    )


def build_internal_action_home_status_light_link(
    *,
    home_surface_mapping: Any,
    actual_status_light_mutated: bool = False,
    actual_screen_mutated: bool = False,
    unity_runtime_mutated: bool = False,
    sound_played: bool = False,
    external_message_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> InternalActionHomeStatusLightLinkRecord:
    mapping = _record(home_surface_mapping)
    mapping_valid = validate_internal_action_home_surface_mapping(mapping)["valid"]
    kind = str(_get(mapping, "target_status_light_kind", "none"))
    if not mapping_valid:
        status = "blocked_invalid_mapping"
    elif actual_status_light_mutated:
        status = "blocked_actual_status_light_mutation"
    elif actual_screen_mutated:
        status = "blocked_screen_mutation"
    elif unity_runtime_mutated:
        status = "blocked_unity_runtime_mutation"
    elif sound_played:
        status = "blocked_sound_output"
    elif first_output_created:
        status = "blocked_first_output"
    elif live_runtime_session_created:
        status = "blocked_live_runtime"
    else:
        status = {
            "uncertainty": "home_status_light_link_created_uncertainty",
            "teacher_review_requested": "home_status_light_link_created_teacher_review",
            "observe_again": "home_status_light_link_created_observe_again",
            "event_processing_paused": "home_status_light_link_created_pause",
            "none": "home_status_light_link_created_noop",
        }.get(kind, "home_status_light_link_created")
    state = "warning" if kind in {"uncertainty", "event_processing_paused"} else "on"
    if kind == "none":
        state = "off"
    return InternalActionHomeStatusLightLinkRecord(
        home_status_light_link_id=f"internal_action_home_status_light_link:{kind}:{status}",
        schema_version=STATUS_LIGHT_LINK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_mapping_id=str(_get(mapping, "home_surface_mapping_id", "")),
        status_light_kind=kind,
        status_light_state=state,
        status_light_label=kind.replace("_", " "),
        status_light_reason=f"Internal action mapped to Home status light: {kind}.",
        existing_home_status_light_schema_reused=False,
        target_home_status_light_id=f"home_status_light:{kind}",
        status_light_link_status=status,
        status_light_link_summary="Read-only Home status light link recorded.",
        read_only_status_record=True,
        record_only_status_link=True,
        actual_status_light_mutated=actual_status_light_mutated,
        actual_screen_mutated=actual_screen_mutated,
        unity_runtime_mutated=unity_runtime_mutated,
        sound_played=sound_played,
        external_message_created=external_message_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=_tuple_of_str(_get(mapping, "source_trace_refs", ())),
    )


def validate_internal_action_home_status_light_link(record: Any) -> dict[str, object]:
    return _validation(
        str(_get(record, "status_light_link_status", "missing")),
        {
            "home_status_light_link_created",
            "home_status_light_link_created_uncertainty",
            "home_status_light_link_created_teacher_review",
            "home_status_light_link_created_observe_again",
            "home_status_light_link_created_pause",
            "home_status_light_link_created_noop",
        },
    )


def build_internal_action_home_teacher_observed_link(
    *,
    home_surface_mapping: Any,
    teacher_approval_created: bool = False,
    learning_approval_created: bool = False,
    memory_write_approval_created: bool = False,
    actual_surface_mutated: bool = False,
    external_message_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> InternalActionHomeTeacherObservedLinkRecord:
    mapping = _record(home_surface_mapping)
    mapping_valid = validate_internal_action_home_surface_mapping(mapping)["valid"]
    kind = str(_get(mapping, "target_teacher_observed_update_kind", "no_teacher_surface_update"))
    if not mapping_valid:
        status = "blocked_invalid_mapping"
    elif teacher_approval_created:
        status = "blocked_teacher_approval_created"
    elif learning_approval_created:
        status = "blocked_learning_approval_created"
    elif memory_write_approval_created:
        status = "blocked_memory_write_approval_created"
    elif actual_surface_mutated:
        status = "blocked_actual_surface_mutation"
    elif external_message_created:
        status = "blocked_external_message_created"
    elif first_output_created:
        status = "blocked_first_output"
    elif live_runtime_session_created:
        status = "blocked_live_runtime"
    else:
        status = {
            "teacher_review_request_visible": "home_teacher_observed_link_created_review_request",
            "uncertainty_marker_visible": "home_teacher_observed_link_created_uncertainty",
            "interesting_event_marker_visible": "home_teacher_observed_link_created_interesting_event",
            "observe_again_recommendation_visible": "home_teacher_observed_link_created_observe_again",
            "pause_event_processing_marker_visible": "home_teacher_observed_link_created_pause",
            "no_teacher_surface_update": "home_teacher_observed_link_created_noop",
        }.get(kind, "home_teacher_observed_link_created")
    return InternalActionHomeTeacherObservedLinkRecord(
        home_teacher_observed_link_id=f"internal_action_home_teacher_observed_link:{kind}:{status}",
        schema_version=TEACHER_OBSERVED_LINK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_mapping_id=str(_get(mapping, "home_surface_mapping_id", "")),
        teacher_observed_update_kind=kind,
        teacher_observed_sections=("internal_action_result", "readback_reason", "status_light"),
        teacher_observed_summary=f"Teacher-observed Home surface records {kind}.",
        existing_teacher_observed_schema_reused=False,
        target_teacher_observed_surface_id=f"home_teacher_observed:{kind}",
        teacher_observed_link_status=status,
        teacher_review_request_visible=kind == "teacher_review_request_visible",
        teacher_action_required_visible=kind == "teacher_review_request_visible",
        teacher_approval_created=teacher_approval_created,
        learning_approval_created=learning_approval_created,
        memory_write_approval_created=memory_write_approval_created,
        actual_surface_mutated=actual_surface_mutated,
        external_message_created=external_message_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=_tuple_of_str(_get(mapping, "source_trace_refs", ())),
    )


def validate_internal_action_home_teacher_observed_link(record: Any) -> dict[str, object]:
    return _validation(
        str(_get(record, "teacher_observed_link_status", "missing")),
        {
            "home_teacher_observed_link_created",
            "home_teacher_observed_link_created_review_request",
            "home_teacher_observed_link_created_uncertainty",
            "home_teacher_observed_link_created_interesting_event",
            "home_teacher_observed_link_created_observe_again",
            "home_teacher_observed_link_created_pause",
            "home_teacher_observed_link_created_noop",
        },
    )


def build_internal_action_home_render_snapshot_link(
    *,
    home_surface_mapping: Any,
    unity_runtime_started: bool = False,
    unity_scene_mutated: bool = False,
    avatar_control_created: bool = False,
    actual_screen_mutated: bool = False,
    file_written: bool = False,
    network_output_created: bool = False,
    first_output_created: bool = False,
    production_behavior_created: bool = False,
    live_runtime_session_created: bool = False,
) -> InternalActionHomeRenderSnapshotLinkRecord:
    mapping = _record(home_surface_mapping)
    mapping_valid = validate_internal_action_home_surface_mapping(mapping)["valid"]
    kind = str(_get(mapping, "target_render_snapshot_kind", "no_render_snapshot"))
    if not mapping_valid:
        status = "blocked_invalid_mapping"
    elif unity_runtime_started:
        status = "blocked_unity_runtime_started"
    elif unity_scene_mutated:
        status = "blocked_unity_scene_mutation"
    elif avatar_control_created:
        status = "blocked_avatar_control"
    elif actual_screen_mutated:
        status = "blocked_screen_mutation"
    elif file_written:
        status = "blocked_file_write"
    elif network_output_created:
        status = "blocked_network_output"
    elif first_output_created:
        status = "blocked_first_output"
    elif production_behavior_created:
        status = "blocked_production_behavior"
    elif live_runtime_session_created:
        status = "blocked_live_runtime"
    else:
        status = {
            "teacher_review_request_render_snapshot": "home_render_snapshot_link_created_teacher_review",
            "uncertainty_render_snapshot": "home_render_snapshot_link_created_uncertainty",
            "observe_again_render_snapshot": "home_render_snapshot_link_created_observe_again",
            "pause_event_processing_render_snapshot": "home_render_snapshot_link_created_pause",
            "home_status_update_render_snapshot": "home_render_snapshot_link_created_status",
            "no_render_snapshot": "home_render_snapshot_link_created_noop",
        }.get(kind, "home_render_snapshot_link_created_status")
    return InternalActionHomeRenderSnapshotLinkRecord(
        home_render_snapshot_link_id=f"internal_action_home_render_snapshot_link:{kind}:{status}",
        schema_version=RENDER_SNAPSHOT_LINK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_mapping_id=str(_get(mapping, "home_surface_mapping_id", "")),
        render_snapshot_kind=kind,
        render_snapshot_text=f"Read-only Home render snapshot for {kind}.",
        render_snapshot_payload={
            "selected_internal_action_kind": _get(mapping, "selected_internal_action_kind"),
            "status_light_kind": _get(mapping, "target_status_light_kind"),
            "teacher_observed_update_kind": _get(mapping, "target_teacher_observed_update_kind"),
        },
        existing_home_render_schema_reused=False,
        target_home_render_id=f"home_render_snapshot:{kind}",
        render_snapshot_link_status=status,
        render_snapshot_link_summary="Read-only Home render snapshot link recorded.",
        read_only_render_snapshot=True,
        record_only_render_link=True,
        unity_runtime_started=unity_runtime_started,
        unity_scene_mutated=unity_scene_mutated,
        avatar_control_created=avatar_control_created,
        actual_screen_mutated=actual_screen_mutated,
        file_written=file_written,
        network_output_created=network_output_created,
        first_output_created=first_output_created,
        production_behavior_created=production_behavior_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=_tuple_of_str(_get(mapping, "source_trace_refs", ())),
    )


def validate_internal_action_home_render_snapshot_link(record: Any) -> dict[str, object]:
    return _validation(
        str(_get(record, "render_snapshot_link_status", "missing")),
        {
            "home_render_snapshot_link_created",
            "home_render_snapshot_link_created_status",
            "home_render_snapshot_link_created_teacher_review",
            "home_render_snapshot_link_created_uncertainty",
            "home_render_snapshot_link_created_observe_again",
            "home_render_snapshot_link_created_pause",
            "home_render_snapshot_link_created_noop",
        },
    )


def _all_valid(records: tuple[Any, ...], validator: Any) -> bool:
    return all(bool(validator(record)["valid"]) for record in records)


def build_internal_action_home_surface_link_trace(
    *,
    home_surface_link_plan: Any,
    mappings: tuple[Any, ...] | list[Any] = (),
    status_light_links: tuple[Any, ...] | list[Any] = (),
    teacher_observed_links: tuple[Any, ...] | list[Any] = (),
    render_snapshot_links: tuple[Any, ...] | list[Any] = (),
    trace_spine_boundary_preserved: bool = True,
    raw_trace_append_only_confirmed: bool = True,
    raw_trace_summarized_during_service_period: bool = False,
    memory_layer_stores_interpretation_only: bool = True,
    source_trace_refs_preserved: bool = True,
    concept_id_embedded_into_raw_history: bool = False,
    actual_surface_mutated: bool | None = None,
    unity_runtime_mutated: bool | None = None,
    screen_mutated: bool | None = None,
    sound_played: bool | None = None,
    external_message_created: bool | None = None,
    file_written: bool | None = None,
    network_output_created: bool | None = None,
    task_selected_action_created: bool | None = None,
    direct_command_created: bool | None = None,
    external_control_created: bool | None = None,
    memory_write_performed: bool | None = None,
    first_output_created: bool | None = None,
    live_runtime_session_created: bool | None = None,
) -> InternalActionHomeSurfaceLinkTraceRecord:
    plan = _record(home_surface_link_plan) or {}
    mapping_records = tuple(_record(item) or {} for item in mappings)
    status_records = tuple(_record(item) or {} for item in status_light_links)
    teacher_records = tuple(_record(item) or {} for item in teacher_observed_links)
    render_records = tuple(_record(item) or {} for item in render_snapshot_links)

    def any_field(records: tuple[dict[str, Any], ...], *names: str) -> bool:
        return any(bool(record.get(name)) for record in records for name in names)

    actual_surface = (
        any_field(mapping_records, "actual_surface_mutated")
        or any_field(teacher_records, "actual_surface_mutated")
        if actual_surface_mutated is None
        else actual_surface_mutated
    )
    unity_mutated = (
        any_field(mapping_records, "unity_runtime_mutated")
        or any_field(status_records, "unity_runtime_mutated")
        or any_field(render_records, "unity_scene_mutated", "unity_runtime_started")
        if unity_runtime_mutated is None
        else unity_runtime_mutated
    )
    screen = (
        any_field(mapping_records, "screen_mutated")
        or any_field(status_records, "actual_screen_mutated")
        or any_field(render_records, "actual_screen_mutated")
        if screen_mutated is None
        else screen_mutated
    )
    sound = (
        any_field(mapping_records, "sound_played")
        or any_field(status_records, "sound_played")
        if sound_played is None
        else sound_played
    )
    external_message = (
        any_field(mapping_records, "external_message_created")
        or any_field(status_records, "external_message_created")
        or any_field(teacher_records, "external_message_created")
        if external_message_created is None
        else external_message_created
    )
    file_out = (
        any_field(mapping_records, "file_written")
        or any_field(render_records, "file_written")
        if file_written is None
        else file_written
    )
    network_out = (
        any_field(mapping_records, "network_output_created")
        or any_field(render_records, "network_output_created")
        if network_output_created is None
        else network_output_created
    )
    task_selected = (
        any_field(mapping_records, "task_selected_action_created")
        if task_selected_action_created is None
        else task_selected_action_created
    )
    direct = (
        any_field(mapping_records, "direct_command_created")
        if direct_command_created is None
        else direct_command_created
    )
    external_control = (
        any_field(mapping_records, "external_control_created")
        if external_control_created is None
        else external_control_created
    )
    memory = (
        any_field(mapping_records, "memory_write_performed")
        if memory_write_performed is None
        else memory_write_performed
    )
    first = (
        any_field(mapping_records, "first_output_created")
        or any_field(status_records, "first_output_created")
        or any_field(teacher_records, "first_output_created")
        or any_field(render_records, "first_output_created")
        if first_output_created is None
        else first_output_created
    )
    live = (
        any_field(mapping_records, "live_runtime_session_created")
        or any_field(status_records, "live_runtime_session_created")
        or any_field(teacher_records, "live_runtime_session_created")
        or any_field(render_records, "live_runtime_session_created")
        if live_runtime_session_created is None
        else live_runtime_session_created
    )

    if not trace_spine_boundary_preserved or raw_trace_summarized_during_service_period or concept_id_embedded_into_raw_history:
        status = "blocked_trace_spine_boundary_failure"
    elif actual_surface:
        status = "blocked_actual_surface_mutation"
    elif unity_mutated:
        status = "blocked_unity_runtime_mutation"
    elif screen:
        status = "blocked_screen_mutation"
    elif sound:
        status = "blocked_sound_output"
    elif external_message:
        status = "blocked_external_message"
    elif file_out:
        status = "blocked_file_write"
    elif network_out:
        status = "blocked_network_output"
    elif task_selected:
        status = "blocked_task_selected_action"
    elif direct:
        status = "blocked_direct_command"
    elif external_control:
        status = "blocked_external_control"
    elif memory:
        status = "blocked_memory_write"
    elif first:
        status = "blocked_first_output"
    elif live:
        status = "blocked_live_runtime"
    elif not _all_valid(mapping_records, validate_internal_action_home_surface_mapping):
        status = "blocked_invalid_mapping"
    elif not _all_valid(status_records, validate_internal_action_home_status_light_link):
        status = "blocked_invalid_status_light_link"
    elif not _all_valid(teacher_records, validate_internal_action_home_teacher_observed_link):
        status = "blocked_invalid_teacher_observed_link"
    elif not _all_valid(render_records, validate_internal_action_home_render_snapshot_link):
        status = "blocked_invalid_render_snapshot_link"
    elif not mapping_records and not status_records and not teacher_records and not render_records:
        status = "home_surface_link_trace_recorded_empty"
    else:
        status = "home_surface_link_trace_recorded"
    trace_kind = (
        "empty_internal_action_home_surface_link_trace"
        if status == "home_surface_link_trace_recorded_empty"
        else "blocked_home_surface_link_trace"
        if status.startswith("blocked_")
        else "single_internal_action_home_surface_link_trace"
        if len(mapping_records) == 1
        else "mixed_internal_action_home_surface_link_trace"
    )
    return InternalActionHomeSurfaceLinkTraceRecord(
        home_surface_link_trace_id=f"internal_action_home_surface_link_trace:{status}",
        schema_version=TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_link_plan_id=str(_get(plan, "home_surface_link_plan_id", "")),
        mapping_ids=tuple(str(_get(item, "home_surface_mapping_id", "")) for item in mapping_records),
        status_light_link_ids=tuple(str(_get(item, "home_status_light_link_id", "")) for item in status_records),
        teacher_observed_link_ids=tuple(str(_get(item, "home_teacher_observed_link_id", "")) for item in teacher_records),
        render_snapshot_link_ids=tuple(str(_get(item, "home_render_snapshot_link_id", "")) for item in render_records),
        trace_kind=trace_kind,
        trace_status=status,
        trace_summary="Read-only internal action to Qingyin Home surface link trace recorded.",
        mapping_count=len(mapping_records),
        status_light_link_count=len(status_records),
        teacher_observed_link_count=len(teacher_records),
        render_snapshot_link_count=len(render_records),
        read_only_surface_links_confirmed=True,
        record_only_links_confirmed=True,
        trace_spine_boundary_preserved=trace_spine_boundary_preserved,
        raw_trace_append_only_confirmed=raw_trace_append_only_confirmed,
        raw_trace_summarized_during_service_period=raw_trace_summarized_during_service_period,
        memory_layer_stores_interpretation_only=memory_layer_stores_interpretation_only,
        source_trace_refs_preserved=source_trace_refs_preserved,
        concept_id_embedded_into_raw_history=concept_id_embedded_into_raw_history,
        actual_surface_mutated=actual_surface,
        unity_runtime_mutated=unity_mutated,
        screen_mutated=screen,
        sound_played=sound,
        external_message_created=external_message,
        file_written=file_out,
        network_output_created=network_out,
        task_selected_action_created=task_selected,
        direct_command_created=direct,
        external_control_created=external_control,
        memory_write_performed=memory,
        first_output_created=first,
        live_runtime_session_created=live,
        source_trace_refs=("internal_action_home_surface_link_trace",),
    )


def validate_internal_action_home_surface_link_trace(record: Any) -> dict[str, object]:
    return _validation(
        str(_get(record, "trace_status", "missing")),
        {"home_surface_link_trace_recorded", "home_surface_link_trace_recorded_empty"},
    )


def _audit_status(
    *,
    plan: dict[str, Any] | None,
    trace: dict[str, Any] | None,
    closed_loop_milestone_audit: dict[str, Any] | None,
    trace_spine_boundary: dict[str, Any] | None,
    plan_valid: bool,
    trace_valid: bool,
    closed_loop_valid: bool,
    boundary_valid: bool,
) -> str:
    if plan is None:
        return "blocked_missing_plan"
    if not plan_valid:
        return "blocked_missing_plan"
    if closed_loop_milestone_audit is None or not closed_loop_valid:
        return "blocked_closed_loop_milestone_missing"
    if trace_spine_boundary is None or not boundary_valid:
        return "blocked_trace_spine_boundary_failure"
    if trace is None:
        return "blocked_invalid_link_trace"
    if trace.get("teacher_approval_created", False):
        return "blocked_teacher_approval_created"
    if trace.get("production_behavior_created", False):
        return "blocked_production_behavior_detected"
    if not trace_valid:
        return {
            "blocked_invalid_mapping": "blocked_invalid_mapping",
            "blocked_invalid_status_light_link": "blocked_invalid_status_light_link",
            "blocked_invalid_teacher_observed_link": "blocked_invalid_teacher_observed_link",
            "blocked_invalid_render_snapshot_link": "blocked_invalid_render_snapshot_link",
            "blocked_trace_spine_boundary_failure": "blocked_trace_spine_boundary_failure",
            "blocked_actual_surface_mutation": "blocked_screen_mutation_detected",
            "blocked_unity_runtime_mutation": "blocked_unity_runtime_mutation_detected",
            "blocked_screen_mutation": "blocked_screen_mutation_detected",
            "blocked_sound_output": "blocked_sound_output_detected",
            "blocked_external_message": "blocked_external_message_detected",
            "blocked_file_write": "blocked_file_write_detected",
            "blocked_network_output": "blocked_network_output_detected",
            "blocked_task_selected_action": "blocked_task_selected_action_created",
            "blocked_direct_command": "blocked_direct_command_created",
            "blocked_external_control": "blocked_external_control_detected",
            "blocked_memory_write": "blocked_memory_write_detected",
            "blocked_first_output": "blocked_first_output_detected",
            "blocked_live_runtime": "blocked_live_runtime_detected",
        }.get(str(trace.get("trace_status")), "blocked_invalid_link_trace")
    if trace.get("unity_runtime_mutated", False):
        return "blocked_unity_runtime_mutation_detected"
    if trace.get("screen_mutated", False) or trace.get("actual_surface_mutated", False):
        return "blocked_screen_mutation_detected"
    if trace.get("sound_played", False):
        return "blocked_sound_output_detected"
    if trace.get("external_message_created", False):
        return "blocked_external_message_detected"
    if trace.get("file_written", False):
        return "blocked_file_write_detected"
    if trace.get("network_output_created", False):
        return "blocked_network_output_detected"
    if trace.get("task_selected_action_created", False):
        return "blocked_task_selected_action_created"
    if trace.get("direct_command_created", False):
        return "blocked_direct_command_created"
    if trace.get("external_control_created", False):
        return "blocked_external_control_detected"
    if trace.get("memory_write_performed", False):
        return "blocked_memory_write_detected"
    if trace.get("first_output_created", False):
        return "blocked_first_output_detected"
    if trace.get("live_runtime_session_created", False):
        return "blocked_live_runtime_detected"
    mapping_ids = trace.get("mapping_ids", [])
    first_mapping = str(mapping_ids[0]) if mapping_ids else ""
    if "mark_uncertain" in first_mapping:
        return "passed_uncertainty_home_surface_link"
    if "request_teacher_review" in first_mapping:
        return "passed_teacher_review_home_surface_link"
    if "observe_again" in first_mapping:
        return "passed_observe_again_home_surface_link"
    if "pause_event_processing" in first_mapping:
        return "passed_pause_event_processing_home_surface_link"
    return "passed_internal_action_home_surface_link"


def build_internal_action_home_surface_link_audit(
    *,
    home_surface_link_plan: Any | None,
    home_surface_link_trace: Any | None,
    closed_loop_milestone_audit: Any | None,
    trace_spine_boundary: Any | None,
) -> InternalActionHomeSurfaceLinkAudit:
    plan = _record(home_surface_link_plan)
    trace = _record(home_surface_link_trace)
    closed_loop = _record(closed_loop_milestone_audit)
    boundary = _record(trace_spine_boundary)
    plan_valid = bool(validate_internal_action_home_surface_link_plan(plan)["valid"])
    trace_valid = bool(validate_internal_action_home_surface_link_trace(trace)["valid"])
    closed_loop_valid = bool(
        validate_host_body_embodied_learning_closed_loop_milestone_audit(closed_loop)[
            "valid"
        ]
    )
    boundary_valid = bool(validate_trace_spine_raw_evidence_boundary(boundary)["valid"])
    status = _audit_status(
        plan=plan,
        trace=trace,
        closed_loop_milestone_audit=closed_loop,
        trace_spine_boundary=boundary,
        plan_valid=plan_valid,
        trace_valid=trace_valid,
        closed_loop_valid=closed_loop_valid,
        boundary_valid=boundary_valid,
    )
    passed = status.startswith("passed_")
    reasons = () if passed else (status,)
    return InternalActionHomeSurfaceLinkAudit(
        home_surface_link_audit_id=f"internal_action_home_surface_link_audit:{status}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_link_plan_id=_get(plan, "home_surface_link_plan_id"),
        source_home_surface_link_trace_id=_get(trace, "home_surface_link_trace_id"),
        source_closed_loop_milestone_audit_id=_get(
            closed_loop, "closed_loop_milestone_audit_id"
        ),
        source_trace_spine_boundary_id=_get(boundary, "trace_spine_boundary_id"),
        plan_valid=plan_valid,
        mappings_valid=trace_valid,
        status_light_links_valid=trace_valid,
        teacher_observed_links_valid=trace_valid,
        render_snapshot_links_valid=trace_valid,
        link_trace_valid=trace_valid,
        closed_loop_milestone_valid=closed_loop_valid,
        trace_spine_boundary_valid=boundary_valid,
        internal_action_home_surface_link_confirmed=passed,
        read_only_surface_confirmed=passed,
        record_only_link_confirmed=passed,
        trace_spine_format_unified_confirmed=bool(
            _get(trace, "trace_spine_boundary_preserved", False)
        ),
        trace_spine_time_aligned_confirmed=bool(
            _get(trace, "trace_spine_boundary_preserved", False)
        ),
        raw_trace_append_only_confirmed=bool(
            _get(trace, "raw_trace_append_only_confirmed", False)
        ),
        raw_trace_not_summarized_during_service_period=not bool(
            _get(trace, "raw_trace_summarized_during_service_period", True)
        ),
        memory_layer_stores_interpretation_only_confirmed=bool(
            _get(trace, "memory_layer_stores_interpretation_only", False)
        ),
        source_trace_refs_preserved_confirmed=bool(
            _get(trace, "source_trace_refs_preserved", False)
        ),
        concept_id_not_embedded_into_raw_history_confirmed=not bool(
            _get(trace, "concept_id_embedded_into_raw_history", True)
        ),
        no_unity_runtime_mutation=not bool(_get(trace, "unity_runtime_mutated", True)),
        no_unity_scene_mutation=not bool(_get(trace, "unity_runtime_mutated", True)),
        no_avatar_control=True,
        no_actual_screen_mutation=not bool(_get(trace, "screen_mutated", True)),
        no_actual_sound_output=not bool(_get(trace, "sound_played", True)),
        no_external_message_output=not bool(_get(trace, "external_message_created", True)),
        no_file_write=not bool(_get(trace, "file_written", True)),
        no_network_output=not bool(_get(trace, "network_output_created", True)),
        no_task_selected_action=not bool(_get(trace, "task_selected_action_created", True)),
        no_final_action=True,
        no_direct_command=not bool(_get(trace, "direct_command_created", True)),
        no_sandbox_execution=True,
        no_external_control=not bool(_get(trace, "external_control_created", True)),
        no_memory_layer_write=not bool(_get(trace, "memory_write_performed", True)),
        no_long_term_memory_write=True,
        no_core_memory_write=True,
        no_learning_candidate_creation=True,
        no_concept_candidate_creation=True,
        no_reviewed_concept_creation=True,
        no_automatic_learning_approval=True,
        no_teacher_approval_created=not bool(_get(trace, "teacher_approval_created", False)),
        no_first_output=not bool(_get(trace, "first_output_created", True)),
        no_live_runtime_session=not bool(_get(trace, "live_runtime_session_created", True)),
        no_thought_engine_behavior=True,
        no_production_behavior=not bool(_get(trace, "production_behavior_created", False)),
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=reasons,
        source_trace_refs=("internal_action_home_surface_link_audit",),
    )


def validate_internal_action_home_surface_link_audit(record: Any) -> dict[str, object]:
    return _validation(
        str(_get(record, "audit_status", "missing")),
        {
            "passed_internal_action_home_surface_link",
            "passed_uncertainty_home_surface_link",
            "passed_teacher_review_home_surface_link",
            "passed_observe_again_home_surface_link",
            "passed_pause_event_processing_home_surface_link",
            "passed_trace_spine_boundary_preserved",
        },
    )


def build_internal_action_home_surface_link_readiness(
    *,
    home_surface_link_audit: Any | None,
    readiness_status: str = "ready_for_runtime_state_summary_session_shell_only",
) -> InternalActionHomeSurfaceLinkReadinessRecord:
    audit = _record(home_surface_link_audit)
    if audit is None:
        status = "not_ready_missing_home_surface_link_audit"
    elif not validate_internal_action_home_surface_link_audit(audit)["valid"]:
        status = "not_ready_boundary_failure"
    elif readiness_status.startswith("ready_for_"):
        status = readiness_status
    else:
        status = "blocked_forbidden_authority_detected"
    return InternalActionHomeSurfaceLinkReadinessRecord(
        home_surface_link_readiness_id=f"internal_action_home_surface_link_readiness:{status}",
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_home_surface_link_audit_id=str(_get(audit, "home_surface_link_audit_id", "")),
        current_verified_capability=(
            "Internal-only Host Body action results can link to Qingyin Home "
            "read-only status, teacher-observed, and render snapshot records."
        ),
        recommended_next_package=(
            "Package 115 / ASHL Core v1 Runtime State Summary And Session Shell Minimal v0"
        ),
        recommended_next_reason=(
            "Create a read-only session shell summarizing Host Body, learning, "
            "readback, Home surface, and boundary state for a no-Codex run."
        ),
        ready_for_runtime_state_summary_session_shell=True,
        ready_for_bounded_embodied_loop_runner=True,
        ready_for_no_codex_teacher_console_flow=True,
        ready_for_session_end_review_promote_gate=True,
        ready_for_no_codex_fixture_growth_loop_milestone_audit=True,
        ready_for_unity_runtime_connection=False,
        ready_for_actual_screen_mutation=False,
        ready_for_external_control=False,
        ready_for_task_engine_action_selection=False,
        ready_for_long_term_memory_write=False,
        ready_for_core_memory_write=False,
        ready_for_first_output=False,
        ready_for_live_runtime_session=False,
        readiness_status=status,
        readiness_summary=(
            "Ready for read-only runtime state summary/session shell work only; "
            "not ready for Unity, real screen mutation, external control, memory "
            "write, first_output, or live runtime."
        ),
        source_trace_refs=("internal_action_home_surface_link_readiness",),
    )


def validate_internal_action_home_surface_link_readiness(record: Any) -> dict[str, object]:
    data = _record(record)
    if data is None:
        return {"valid": False, "status": "missing", "reasons": ["missing"]}
    valid = data.get("readiness_status") in {
        "ready_for_runtime_state_summary_session_shell_only",
        "ready_for_bounded_embodied_loop_runner_only",
        "ready_for_no_codex_teacher_console_flow_only",
        "ready_for_session_end_review_promote_gate_only",
        "ready_for_no_codex_fixture_growth_loop_milestone_audit_only",
    }
    valid = valid and all(
        bool(data.get(name))
        for name in (
            "ready_for_runtime_state_summary_session_shell",
            "ready_for_bounded_embodied_loop_runner",
            "ready_for_no_codex_teacher_console_flow",
            "ready_for_session_end_review_promote_gate",
            "ready_for_no_codex_fixture_growth_loop_milestone_audit",
        )
    )
    valid = valid and not any(
        bool(data.get(name))
        for name in (
            "ready_for_unity_runtime_connection",
            "ready_for_actual_screen_mutation",
            "ready_for_external_control",
            "ready_for_task_engine_action_selection",
            "ready_for_long_term_memory_write",
            "ready_for_core_memory_write",
            "ready_for_first_output",
            "ready_for_live_runtime_session",
        )
    )
    return {
        "valid": valid,
        "status": data.get("readiness_status"),
        "reasons": [] if valid else [str(data.get("readiness_status"))],
    }


def _build_link_payload(
    *,
    selected_internal_action_kind: str,
    mapping_kwargs: dict[str, Any] | None = None,
    status_kwargs: dict[str, Any] | None = None,
    teacher_kwargs: dict[str, Any] | None = None,
    render_kwargs: dict[str, Any] | None = None,
    trace_kwargs: dict[str, Any] | None = None,
    include_links: bool = True,
) -> dict[str, Any]:
    closed_loop, home_audit, boundary = _demo_sources()
    plan = build_internal_action_home_surface_link_plan(
        closed_loop_milestone_audit=closed_loop,
        home_surface_audit=home_audit,
        trace_spine_boundary=boundary,
    )
    mapping = build_internal_action_home_surface_mapping(
        home_surface_link_plan=plan,
        selected_internal_action_kind=selected_internal_action_kind,
        **(mapping_kwargs or {}),
    )
    status_link = build_internal_action_home_status_light_link(
        home_surface_mapping=mapping, **(status_kwargs or {})
    )
    teacher_link = build_internal_action_home_teacher_observed_link(
        home_surface_mapping=mapping, **(teacher_kwargs or {})
    )
    render_link = build_internal_action_home_render_snapshot_link(
        home_surface_mapping=mapping, **(render_kwargs or {})
    )
    trace = build_internal_action_home_surface_link_trace(
        home_surface_link_plan=plan,
        mappings=(mapping,) if include_links else (),
        status_light_links=(status_link,) if include_links else (),
        teacher_observed_links=(teacher_link,) if include_links else (),
        render_snapshot_links=(render_link,) if include_links else (),
        **(trace_kwargs or {}),
    )
    audit = build_internal_action_home_surface_link_audit(
        home_surface_link_plan=plan,
        home_surface_link_trace=trace,
        closed_loop_milestone_audit=closed_loop,
        trace_spine_boundary=boundary,
    )
    readiness = build_internal_action_home_surface_link_readiness(
        home_surface_link_audit=audit
    )
    return {
        "internal_action_home_surface_link_plan": plan.to_dict(),
        "internal_action_home_surface_mapping": mapping.to_dict(),
        "internal_action_home_status_light_link": status_link.to_dict(),
        "internal_action_home_teacher_observed_link": teacher_link.to_dict(),
        "internal_action_home_render_snapshot_link": render_link.to_dict(),
        "internal_action_home_surface_link_trace": trace.to_dict(),
        "internal_action_home_surface_link_audit": audit.to_dict(),
        "internal_action_home_surface_link_readiness": readiness.to_dict(),
    }


def build_demo_mark_uncertain_home_surface_link() -> dict[str, Any]:
    return _build_link_payload(selected_internal_action_kind="mark_uncertain")


def build_demo_request_teacher_review_home_surface_link() -> dict[str, Any]:
    return _build_link_payload(selected_internal_action_kind="request_teacher_review")


def build_demo_observe_again_home_surface_link() -> dict[str, Any]:
    return _build_link_payload(selected_internal_action_kind="observe_again")


def build_demo_mark_interesting_home_surface_link() -> dict[str, Any]:
    return _build_link_payload(selected_internal_action_kind="mark_event_interesting")


def build_demo_pause_event_processing_home_surface_link() -> dict[str, Any]:
    return _build_link_payload(selected_internal_action_kind="pause_event_processing")


def build_demo_update_home_status_surface_link() -> dict[str, Any]:
    return _build_link_payload(selected_internal_action_kind="update_home_status")


def build_demo_mixed_internal_action_home_surface_link() -> dict[str, Any]:
    closed_loop, home_audit, boundary = _demo_sources()
    plan = build_internal_action_home_surface_link_plan(
        closed_loop_milestone_audit=closed_loop,
        home_surface_audit=home_audit,
        trace_spine_boundary=boundary,
    )
    mappings = tuple(
        build_internal_action_home_surface_mapping(
            home_surface_link_plan=plan, selected_internal_action_kind=action
        )
        for action in (
            "mark_uncertain",
            "request_teacher_review",
            "observe_again",
            "pause_event_processing",
        )
    )
    status_links = tuple(
        build_internal_action_home_status_light_link(home_surface_mapping=mapping)
        for mapping in mappings
    )
    teacher_links = tuple(
        build_internal_action_home_teacher_observed_link(home_surface_mapping=mapping)
        for mapping in mappings
    )
    render_links = tuple(
        build_internal_action_home_render_snapshot_link(home_surface_mapping=mapping)
        for mapping in mappings
    )
    trace = build_internal_action_home_surface_link_trace(
        home_surface_link_plan=plan,
        mappings=mappings,
        status_light_links=status_links,
        teacher_observed_links=teacher_links,
        render_snapshot_links=render_links,
    )
    audit = build_internal_action_home_surface_link_audit(
        home_surface_link_plan=plan,
        home_surface_link_trace=trace,
        closed_loop_milestone_audit=closed_loop,
        trace_spine_boundary=boundary,
    )
    readiness = build_internal_action_home_surface_link_readiness(
        home_surface_link_audit=audit
    )
    return {
        "internal_action_home_surface_link_plan": plan.to_dict(),
        "internal_action_home_surface_mappings": [mapping.to_dict() for mapping in mappings],
        "internal_action_home_status_light_links": [
            link.to_dict() for link in status_links
        ],
        "internal_action_home_teacher_observed_links": [
            link.to_dict() for link in teacher_links
        ],
        "internal_action_home_render_snapshot_links": [
            link.to_dict() for link in render_links
        ],
        "internal_action_home_surface_link_trace": trace.to_dict(),
        "internal_action_home_surface_link_audit": audit.to_dict(),
        "internal_action_home_surface_link_readiness": readiness.to_dict(),
    }


def build_demo_empty_internal_action_home_surface_link() -> dict[str, Any]:
    return _build_link_payload(
        selected_internal_action_kind="mark_uncertain",
        include_links=False,
    )


def build_demo_blocked_unity_runtime_mutation() -> dict[str, Any]:
    return _build_link_payload(
        selected_internal_action_kind="mark_uncertain",
        mapping_kwargs={"unity_runtime_mutated": True},
    )


def build_demo_blocked_screen_mutation() -> dict[str, Any]:
    return _build_link_payload(
        selected_internal_action_kind="mark_uncertain",
        mapping_kwargs={"screen_mutated": True},
    )


def build_demo_blocked_sound_output() -> dict[str, Any]:
    return _build_link_payload(
        selected_internal_action_kind="mark_uncertain",
        status_kwargs={"sound_played": True},
    )


def build_demo_blocked_external_message() -> dict[str, Any]:
    return _build_link_payload(
        selected_internal_action_kind="request_teacher_review",
        mapping_kwargs={"external_message_created": True},
    )


def build_demo_blocked_file_write() -> dict[str, Any]:
    return _build_link_payload(
        selected_internal_action_kind="update_home_status",
        render_kwargs={"file_written": True},
    )


def build_demo_blocked_network_output() -> dict[str, Any]:
    return _build_link_payload(
        selected_internal_action_kind="update_home_status",
        render_kwargs={"network_output_created": True},
    )


def build_demo_blocked_task_selected_action() -> dict[str, Any]:
    return _build_link_payload(
        selected_internal_action_kind="mark_uncertain",
        mapping_kwargs={"task_selected_action_created": True},
    )


def build_demo_blocked_direct_command() -> dict[str, Any]:
    return _build_link_payload(
        selected_internal_action_kind="mark_uncertain",
        mapping_kwargs={"direct_command_created": True},
    )


def build_demo_blocked_memory_write() -> dict[str, Any]:
    return _build_link_payload(
        selected_internal_action_kind="mark_uncertain",
        mapping_kwargs={"memory_write_performed": True},
    )


def build_demo_blocked_first_output() -> dict[str, Any]:
    return _build_link_payload(
        selected_internal_action_kind="mark_uncertain",
        mapping_kwargs={"first_output_created": True},
    )


def build_demo_blocked_live_runtime() -> dict[str, Any]:
    return _build_link_payload(
        selected_internal_action_kind="mark_uncertain",
        mapping_kwargs={"live_runtime_session_created": True},
    )


def render_internal_action_home_surface_link_summary_text(record: Any) -> str:
    data = _record(record) or {}
    audit = data.get("internal_action_home_surface_link_audit", data)
    return "\n".join(
        (
            "Internal Action Home Surface Link",
            f"audit_status: {_get(audit, 'audit_status', 'unknown')}",
            f"safe_claim: {_get(audit, 'safe_claim', SAFE_CLAIM)}",
        )
    )


def render_internal_action_home_surface_link_table(record: Any) -> str:
    data = _record(record) or {}
    mappings = data.get("internal_action_home_surface_mappings")
    if mappings is None and "internal_action_home_surface_mapping" in data:
        mappings = [data["internal_action_home_surface_mapping"]]
    mappings = mappings or []
    lines = ["action | status_light | teacher_update | render_snapshot"]
    for mapping in mappings:
        lines.append(
            f"{mapping.get('selected_internal_action_kind')} | "
            f"{mapping.get('target_status_light_kind')} | "
            f"{mapping.get('target_teacher_observed_update_kind')} | "
            f"{mapping.get('target_render_snapshot_kind')}"
        )
    return "\n".join(lines)


def render_internal_action_home_status_light_table(record: Any) -> str:
    data = _record(record) or {}
    links = data.get("internal_action_home_status_light_links")
    if links is None and "internal_action_home_status_light_link" in data:
        links = [data["internal_action_home_status_light_link"]]
    links = links or []
    lines = ["status_light_kind | state | status"]
    for link in links:
        lines.append(
            f"{link.get('status_light_kind')} | "
            f"{link.get('status_light_state')} | "
            f"{link.get('status_light_link_status')}"
        )
    return "\n".join(lines)
