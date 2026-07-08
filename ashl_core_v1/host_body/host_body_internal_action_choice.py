"""Internal-only Host Body action choice records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.host_body.host_body_runtime_bridge import (
    HostBodyRuntimeBridgeTraceRecord,
    build_demo_deferred_dispatch_host_body_runtime_bridge,
)
from ashl_core_v1.host_body.host_body_trace_history_lane import (
    HostBodyTraceHistoryAudit,
    HostBodyTraceHistoryEntryRecord,
    HostBodyTraceHistoryLaneRecord,
    HostBodyTraceHistoryReadbackRecord,
    build_demo_full_host_body_trace_history_lane,
)
from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
    QingyinHomeInternalSpaceRenderRecord,
    QingyinHomeInternalSpaceSurfaceAudit,
    QingyinHomeStatusLightRecord,
    QingyinHomeTeacherObservedSurfaceRecord,
    build_demo_qingyin_home_internal_space_surface,
)


SOURCE_ENGINE = "host_body"

PLAN_SCHEMA_VERSION = "qingyin_host_body_internal_action_choice_plan_v0"
CANDIDATE_SCHEMA_VERSION = "qingyin_host_body_internal_action_candidate_v0"
CHOICE_SCHEMA_VERSION = "qingyin_host_body_internal_action_choice_v0"
RESULT_SCHEMA_VERSION = "qingyin_host_body_internal_action_result_v0"
SURFACE_EFFECT_SCHEMA_VERSION = "qingyin_host_body_internal_action_surface_effect_v0"
CHOICE_SET_SCHEMA_VERSION = "qingyin_host_body_internal_action_choice_set_v0"
AUDIT_SCHEMA_VERSION = "qingyin_host_body_internal_action_choice_audit_v0"
READINESS_SCHEMA_VERSION = "qingyin_host_body_internal_action_choice_readiness_v0"

PLAN_NAME = "host_body_internal_action_choice"
PLAN_KIND = "deterministic_internal_only_choice"
RULE_SET_NAME = "host_body_internal_action_choice_rules"
RULE_SET_VERSION = "v0"

ALLOWED_INTERNAL_ACTION_KINDS = (
    "observe_again",
    "mark_event_interesting",
    "mark_uncertain",
    "request_teacher_review",
    "shift_internal_focus",
    "update_home_status",
    "pause_event_processing",
)
FORBIDDEN_EXTERNAL_ACTION_KINDS = (
    "task_selected_action",
    "task_final_action",
    "direct_command",
    "sandbox_execution",
    "mouse_control",
    "keyboard_control",
    "browser_control",
    "os_control",
    "file_operation",
    "network_execution",
    "shell_execution",
    "external_api_call",
    "unity_avatar_control",
    "first_output",
    "voice_output",
    "free_text_conversation",
    "memory_write",
    "learning_approval",
)
CHOICE_TIE_ORDER = {
    "request_teacher_review": 0,
    "pause_event_processing": 1,
    "mark_uncertain": 2,
    "mark_event_interesting": 3,
    "observe_again": 4,
    "shift_internal_focus": 5,
    "update_home_status": 6,
}

SAFE_CLAIM = (
    "ASHL Core v1 can create internal-only Host Body action choice records "
    "from read-only Host Body trace history and Home surface evidence."
)
BLOCKED_CLAIMS = (
    "no_task_selected_action",
    "no_final_action",
    "no_direct_command",
    "no_sandbox_execution",
    "no_external_control",
    "no_memory_layer_write",
    "no_learning_candidate_creation",
    "no_teacher_approval_created",
    "no_first_output",
    "no_live_runtime_session",
)
READINESS_NEXT_PACKAGE = (
    "Package 107 / ASHL Core v1 Qingyin Host Body v0 Milestone Audit Minimal v0"
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
class HostBodyInternalActionChoicePlanRecord:
    internal_action_choice_plan_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_trace_history_audit_id: str | None
    source_trace_history_readback_id: str | None
    source_home_surface_audit_id: str | None
    plan_name: str
    plan_kind: str
    allowed_internal_action_kinds: tuple[str, ...]
    forbidden_external_action_kinds: tuple[str, ...]
    deterministic_rule_set_name: str
    deterministic_rule_set_version: str
    internal_only: bool
    record_only: bool
    read_only_source_required: bool
    task_engine_action_selection_allowed: bool
    final_action_allowed: bool
    direct_command_allowed: bool
    sandbox_execution_allowed: bool
    external_control_allowed: bool
    memory_write_allowed: bool
    learning_candidate_creation_allowed: bool
    automatic_learning_approval_allowed: bool
    first_output_allowed: bool
    live_runtime_session_allowed: bool
    plan_status: str
    plan_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PLAN_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_internal_action_choice_plan_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.plan_name != PLAN_NAME:
            raise ValueError("plan_name must be host_body_internal_action_choice")
        if self.plan_kind != PLAN_KIND:
            raise ValueError("plan_kind must be deterministic_internal_only_choice")
        if self.deterministic_rule_set_name != RULE_SET_NAME:
            raise ValueError("deterministic_rule_set_name must be host_body_internal_action_choice_rules")
        if self.deterministic_rule_set_version != RULE_SET_VERSION:
            raise ValueError("deterministic_rule_set_version must be v0")
        if self.plan_status not in {
            "internal_action_choice_plan_created",
            "blocked_missing_trace_history_audit",
            "blocked_task_action_selection_allowed",
            "blocked_external_control_allowed",
            "blocked_memory_write_allowed",
            "blocked_first_output_allowed",
            "blocked_live_runtime_allowed",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown plan_status: {self.plan_status}")
        for name in (
            "allowed_internal_action_kinds",
            "forbidden_external_action_kinds",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyInternalActionChoicePlanRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyInternalActionCandidateRecord:
    internal_action_candidate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_internal_action_choice_plan_id: str
    source_trace_history_readback_id: str | None
    source_trace_history_entry_id: str | None
    source_home_status_light_id: str | None
    source_runtime_bridge_trace_id: str | None
    candidate_action_kind: str
    candidate_reason_codes: tuple[str, ...]
    candidate_priority: int
    candidate_status: str
    candidate_summary: str
    internal_only: bool
    record_only: bool
    task_selected_action_created: bool
    final_action_created: bool
    direct_command_created: bool
    sandbox_execution_created: bool
    external_control_created: bool
    os_control_created: bool
    mouse_control_created: bool
    keyboard_control_created: bool
    browser_control_created: bool
    file_operation_created: bool
    network_execution_created: bool
    shell_execution_created: bool
    external_api_call_created: bool
    memory_layer_write_performed: bool
    learning_candidate_created: bool
    automatic_learning_approval_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CANDIDATE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_internal_action_candidate_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.candidate_action_kind not in ALLOWED_INTERNAL_ACTION_KINDS + ("blocked_external_action",):
            raise ValueError(f"unknown candidate_action_kind: {self.candidate_action_kind}")
        if self.candidate_status not in {
            "internal_action_candidate_created",
            "internal_action_candidate_created_from_trace_history",
            "internal_action_candidate_created_from_status_light",
            "internal_action_candidate_blocked_forbidden_kind",
            "internal_action_candidate_blocked_external_control",
            "internal_action_candidate_blocked_task_action_selection",
            "internal_action_candidate_blocked_first_output",
            "internal_action_candidate_blocked_forbidden_authority",
        }:
            raise ValueError(f"unknown candidate_status: {self.candidate_status}")
        for name in ("candidate_reason_codes", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyInternalActionCandidateRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyInternalActionChoiceRecord:
    internal_action_choice_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_internal_action_choice_plan_id: str
    candidate_ids: tuple[str, ...]
    selected_candidate_id: str | None
    selected_internal_action_kind: str | None
    selection_rule: str
    selection_reason: str
    choice_status: str
    choice_summary: str
    choice_created: bool
    internal_only: bool
    record_only: bool
    teacher_approval_created: bool
    learning_approval_created: bool
    memory_write_approval_created: bool
    task_selected_action_created: bool
    final_action_created: bool
    direct_command_created: bool
    sandbox_execution_created: bool
    external_control_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CHOICE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_internal_action_choice_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.selected_internal_action_kind is not None and self.selected_internal_action_kind not in ALLOWED_INTERNAL_ACTION_KINDS:
            raise ValueError(f"unknown selected_internal_action_kind: {self.selected_internal_action_kind}")
        if self.choice_status not in {
            "internal_action_choice_selected",
            "internal_action_choice_deferred_no_candidates",
            "internal_action_choice_blocked_invalid_candidate",
            "internal_action_choice_blocked_external_control",
            "internal_action_choice_blocked_task_action_selection",
            "internal_action_choice_blocked_teacher_approval_created",
            "internal_action_choice_blocked_first_output",
            "internal_action_choice_blocked_forbidden_authority",
        }:
            raise ValueError(f"unknown choice_status: {self.choice_status}")
        for name in ("candidate_ids", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyInternalActionChoiceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyInternalActionResultRecord:
    internal_action_result_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_internal_action_choice_id: str
    selected_internal_action_kind: str | None
    result_kind: str
    result_status: str
    result_summary: str
    internal_marker_created: bool
    home_status_update_recorded: bool
    teacher_review_request_recorded: bool
    internal_focus_marker_recorded: bool
    event_processing_pause_marker_recorded: bool
    observe_again_recommendation_recorded: bool
    actual_screen_mutated: bool
    actual_sound_played: bool
    unity_runtime_mutated: bool
    avatar_control_created: bool
    teacher_approval_created: bool
    learning_approval_created: bool
    memory_write_approval_created: bool
    task_selected_action_created: bool
    final_action_created: bool
    direct_command_created: bool
    sandbox_execution_created: bool
    external_control_created: bool
    os_control_created: bool
    mouse_control_created: bool
    keyboard_control_created: bool
    browser_control_created: bool
    file_operation_created: bool
    network_execution_created: bool
    shell_execution_created: bool
    external_api_call_created: bool
    memory_layer_write_performed: bool
    learning_candidate_created: bool
    automatic_learning_approval_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RESULT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_internal_action_result_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.result_kind not in {
            "internal_marker_result",
            "home_status_update_record",
            "teacher_review_request_record",
            "internal_focus_marker",
            "event_processing_pause_marker",
            "observe_again_recommendation",
            "blocked_result",
        }:
            raise ValueError(f"unknown result_kind: {self.result_kind}")
        if self.result_status not in {
            "internal_action_result_recorded",
            "internal_action_result_recorded_request_teacher_review",
            "internal_action_result_recorded_update_home_status",
            "internal_action_result_recorded_mark_uncertain",
            "internal_action_result_blocked_external_control",
            "internal_action_result_blocked_task_action_selection",
            "internal_action_result_blocked_memory_write",
            "internal_action_result_blocked_first_output",
            "internal_action_result_blocked_forbidden_authority",
        }:
            raise ValueError(f"unknown result_status: {self.result_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyInternalActionResultRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyInternalActionSurfaceEffectRecord:
    internal_action_surface_effect_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_internal_action_result_id: str
    surface_effect_kind: str
    surface_effect_status: str
    surface_effect_summary: str
    target_surface: str
    status_light_update_recorded: bool
    teacher_observed_surface_update_recorded: bool
    home_render_update_recorded: bool
    actual_status_light_mutated: bool
    actual_home_surface_mutated: bool
    actual_unity_runtime_mutated: bool
    actual_screen_mutated: bool
    actual_sound_played: bool
    first_output_created: bool
    external_message_created: bool
    file_written: bool
    network_output_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SURFACE_EFFECT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_internal_action_surface_effect_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.surface_effect_kind not in {
            "status_light_update_record",
            "teacher_observed_update_record",
            "home_render_update_record",
            "no_surface_effect",
            "blocked_surface_effect",
        }:
            raise ValueError(f"unknown surface_effect_kind: {self.surface_effect_kind}")
        if self.surface_effect_status not in {
            "surface_effect_recorded",
            "surface_effect_recorded_status_light",
            "surface_effect_recorded_teacher_observed",
            "surface_effect_recorded_home_render",
            "surface_effect_none",
            "surface_effect_blocked_actual_mutation",
            "surface_effect_blocked_first_output",
            "surface_effect_blocked_external_output",
        }:
            raise ValueError(f"unknown surface_effect_status: {self.surface_effect_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyInternalActionSurfaceEffectRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyInternalActionChoiceSetRecord:
    internal_action_choice_set_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_internal_action_choice_plan_id: str
    candidate_ids: tuple[str, ...]
    choice_ids: tuple[str, ...]
    result_ids: tuple[str, ...]
    surface_effect_ids: tuple[str, ...]
    choice_set_kind: str
    choice_set_status: str
    choice_set_summary: str
    candidate_count: int
    choice_count: int
    result_count: int
    surface_effect_count: int
    internal_only_confirmed: bool
    record_only_confirmed: bool
    external_control_created: bool
    task_action_selection_created: bool
    memory_write_performed: bool
    learning_candidate_created: bool
    automatic_learning_approval_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CHOICE_SET_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_internal_action_choice_set_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.choice_set_kind not in {
            "single_internal_action_choice_demo",
            "mixed_internal_action_choice_demo",
            "blocked_internal_action_choice_demo",
            "empty_internal_action_choice_demo",
        }:
            raise ValueError(f"unknown choice_set_kind: {self.choice_set_kind}")
        if self.choice_set_status not in {
            "internal_action_choice_set_recorded",
            "internal_action_choice_set_recorded_empty",
            "internal_action_choice_set_blocked_external_control",
            "internal_action_choice_set_blocked_task_action_selection",
            "internal_action_choice_set_blocked_memory_write",
            "internal_action_choice_set_blocked_first_output",
            "internal_action_choice_set_blocked_forbidden_authority",
        }:
            raise ValueError(f"unknown choice_set_status: {self.choice_set_status}")
        for name in ("candidate_ids", "choice_ids", "result_ids", "surface_effect_ids", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyInternalActionChoiceSetRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyInternalActionChoiceAudit:
    internal_action_choice_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_internal_action_choice_plan_id: str | None
    source_internal_action_choice_set_id: str | None
    plan_valid: bool
    candidates_valid: bool
    choices_valid: bool
    results_valid: bool
    surface_effects_valid: bool
    choice_set_valid: bool
    internal_only_confirmed: bool
    record_only_confirmed: bool
    read_only_source_confirmed: bool
    allowed_internal_action_kinds_only: bool
    no_task_selected_action: bool
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
    no_actual_screen_mutation: bool
    no_actual_sound_output: bool
    no_unity_runtime_mutation: bool
    no_avatar_control: bool
    no_memory_layer_write: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_state_persistence_write: bool
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
        if self.schema_version != AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_internal_action_choice_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.audit_status not in {
            "passed_host_body_internal_action_choice",
            "passed_internal_action_choice_request_teacher_review",
            "passed_internal_action_choice_update_home_status",
            "passed_internal_action_choice_mark_uncertain",
            "passed_internal_action_choice_observe_again",
            "blocked_invalid_plan",
            "blocked_invalid_candidate",
            "blocked_invalid_choice",
            "blocked_invalid_result",
            "blocked_invalid_surface_effect",
            "blocked_task_action_selection_detected",
            "blocked_external_control_detected",
            "blocked_os_control_detected",
            "blocked_file_operation_detected",
            "blocked_network_execution_detected",
            "blocked_memory_write_detected",
            "blocked_learning_candidate_creation_detected",
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
    def from_dict(cls, data: dict[str, object]) -> "HostBodyInternalActionChoiceAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyInternalActionChoiceReadinessRecord:
    internal_action_choice_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_internal_action_choice_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_host_body_internal_action_home_surface_link: bool
    ready_for_teacher_observed_host_body_cli: bool
    ready_for_host_body_v0_milestone_audit: bool
    ready_for_runtime_state_persistence_binding: bool
    ready_for_task_engine_action_selection: bool
    ready_for_external_control: bool
    ready_for_os_control: bool
    ready_for_file_operation: bool
    ready_for_network_execution: bool
    ready_for_memory_layer_write: bool
    ready_for_learning_candidate_creation: bool
    ready_for_automatic_learning_approval: bool
    ready_for_first_output: bool
    ready_for_live_runtime_session: bool
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READINESS_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_internal_action_choice_readiness_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.readiness_status not in {
            "ready_for_host_body_v0_milestone_audit_only",
            "ready_for_internal_action_home_surface_link_only",
            "ready_for_teacher_observed_host_body_cli_only",
            "ready_for_runtime_state_persistence_binding_only",
            "not_ready_missing_internal_action_choice_audit",
            "not_ready_boundary_failure",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyInternalActionChoiceReadinessRecord":
        return cls(**dict(data))


def build_host_body_internal_action_choice_plan(
    *,
    trace_history_audit: HostBodyTraceHistoryAudit | dict[str, object] | None,
    trace_history_readback: HostBodyTraceHistoryReadbackRecord | dict[str, object] | None = None,
    home_surface_audit: QingyinHomeInternalSpaceSurfaceAudit | dict[str, object] | None = None,
    task_engine_action_selection_allowed: bool = False,
    final_action_allowed: bool = False,
    direct_command_allowed: bool = False,
    sandbox_execution_allowed: bool = False,
    external_control_allowed: bool = False,
    memory_write_allowed: bool = False,
    learning_candidate_creation_allowed: bool = False,
    automatic_learning_approval_allowed: bool = False,
    first_output_allowed: bool = False,
    live_runtime_session_allowed: bool = False,
) -> HostBodyInternalActionChoicePlanRecord:
    trace_audit = _trace_audit(trace_history_audit) if trace_history_audit is not None else None
    readback = _trace_readback(trace_history_readback) if trace_history_readback is not None else None
    home_audit = _home_audit(home_surface_audit) if home_surface_audit is not None else None
    status = _plan_status(
        trace_audit=trace_audit,
        task_engine_action_selection_allowed=task_engine_action_selection_allowed,
        final_action_allowed=final_action_allowed,
        direct_command_allowed=direct_command_allowed,
        sandbox_execution_allowed=sandbox_execution_allowed,
        external_control_allowed=external_control_allowed,
        memory_write_allowed=memory_write_allowed,
        learning_candidate_creation_allowed=learning_candidate_creation_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
    )
    return HostBodyInternalActionChoicePlanRecord(
        internal_action_choice_plan_id=f"host_body_internal_action_choice_plan:{_slug(status)}",
        schema_version=PLAN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_trace_history_audit_id=trace_audit.trace_history_audit_id if trace_audit else None,
        source_trace_history_readback_id=readback.trace_history_readback_id if readback else None,
        source_home_surface_audit_id=home_audit.home_surface_audit_id if home_audit else None,
        plan_name=PLAN_NAME,
        plan_kind=PLAN_KIND,
        allowed_internal_action_kinds=ALLOWED_INTERNAL_ACTION_KINDS,
        forbidden_external_action_kinds=FORBIDDEN_EXTERNAL_ACTION_KINDS,
        deterministic_rule_set_name=RULE_SET_NAME,
        deterministic_rule_set_version=RULE_SET_VERSION,
        internal_only=True,
        record_only=True,
        read_only_source_required=True,
        task_engine_action_selection_allowed=task_engine_action_selection_allowed,
        final_action_allowed=final_action_allowed,
        direct_command_allowed=direct_command_allowed,
        sandbox_execution_allowed=sandbox_execution_allowed,
        external_control_allowed=external_control_allowed,
        memory_write_allowed=memory_write_allowed,
        learning_candidate_creation_allowed=learning_candidate_creation_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
        plan_status=status,
        plan_summary=_plan_summary(status),
        source_trace_refs=trace_audit.source_trace_refs if trace_audit else tuple(),
    )


def validate_host_body_internal_action_choice_plan(
    record: HostBodyInternalActionChoicePlanRecord | dict[str, object],
) -> dict[str, object]:
    item = _plan(record)
    valid = item.plan_status == "internal_action_choice_plan_created" and _plan_constants_safe(item)
    return {"valid": valid, "status": item.plan_status, "reasons": [] if valid else [item.plan_status]}


def build_host_body_internal_action_candidate(
    *,
    choice_plan: HostBodyInternalActionChoicePlanRecord | dict[str, object],
    trace_history_readback: HostBodyTraceHistoryReadbackRecord | dict[str, object] | None = None,
    trace_history_entry: HostBodyTraceHistoryEntryRecord | dict[str, object] | None = None,
    home_status_light: QingyinHomeStatusLightRecord | dict[str, object] | None = None,
    runtime_bridge_trace: HostBodyRuntimeBridgeTraceRecord | dict[str, object] | None = None,
    candidate_action_kind: str | None = None,
    candidate_reason_codes: tuple[str, ...] | list[str] = tuple(),
    candidate_priority: int | None = None,
    task_selected_action_created: bool = False,
    final_action_created: bool = False,
    direct_command_created: bool = False,
    sandbox_execution_created: bool = False,
    external_control_created: bool = False,
    os_control_created: bool = False,
    mouse_control_created: bool = False,
    keyboard_control_created: bool = False,
    browser_control_created: bool = False,
    file_operation_created: bool = False,
    network_execution_created: bool = False,
    shell_execution_created: bool = False,
    external_api_call_created: bool = False,
    memory_layer_write_performed: bool = False,
    learning_candidate_created: bool = False,
    automatic_learning_approval_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
    production_behavior_created: bool = False,
) -> HostBodyInternalActionCandidateRecord:
    plan = _plan(choice_plan)
    readback = _trace_readback(trace_history_readback) if trace_history_readback is not None else None
    entry = _trace_entry(trace_history_entry) if trace_history_entry is not None else None
    light = _status_light(home_status_light) if home_status_light is not None else None
    bridge_trace = _bridge_trace(runtime_bridge_trace) if runtime_bridge_trace is not None else None
    inferred = _infer_candidate_action(
        readback=readback,
        entry=entry,
        light=light,
        bridge_trace=bridge_trace,
        requested_kind=candidate_action_kind,
    )
    reason_codes = tuple(candidate_reason_codes) or inferred["reasons"]
    requested_kind = str(candidate_action_kind or inferred["kind"])
    kind = requested_kind if requested_kind in ALLOWED_INTERNAL_ACTION_KINDS else "blocked_external_action"
    priority = int(candidate_priority if candidate_priority is not None else inferred["priority"])
    status = _candidate_status(
        requested_kind=requested_kind,
        task_selected_action_created=task_selected_action_created,
        final_action_created=final_action_created,
        direct_command_created=direct_command_created,
        sandbox_execution_created=sandbox_execution_created,
        external_control_created=external_control_created,
        os_control_created=os_control_created,
        mouse_control_created=mouse_control_created,
        keyboard_control_created=keyboard_control_created,
        browser_control_created=browser_control_created,
        file_operation_created=file_operation_created,
        network_execution_created=network_execution_created,
        shell_execution_created=shell_execution_created,
        external_api_call_created=external_api_call_created,
        memory_layer_write_performed=memory_layer_write_performed,
        learning_candidate_created=learning_candidate_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        production_behavior_created=production_behavior_created,
        light=light,
        entry=entry,
    )
    source_refs = _source_refs(readback, entry, light, bridge_trace)
    return HostBodyInternalActionCandidateRecord(
        internal_action_candidate_id=f"host_body_internal_action_candidate:{_slug(kind)}:{_slug(status)}:{priority}",
        schema_version=CANDIDATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_internal_action_choice_plan_id=plan.internal_action_choice_plan_id,
        source_trace_history_readback_id=readback.trace_history_readback_id if readback else None,
        source_trace_history_entry_id=entry.trace_history_entry_id if entry else None,
        source_home_status_light_id=light.home_status_light_id if light else None,
        source_runtime_bridge_trace_id=bridge_trace.host_runtime_bridge_trace_id if bridge_trace else None,
        candidate_action_kind=kind,
        candidate_reason_codes=reason_codes,
        candidate_priority=priority,
        candidate_status=status,
        candidate_summary=_candidate_summary(status, kind),
        internal_only=True,
        record_only=True,
        task_selected_action_created=task_selected_action_created,
        final_action_created=final_action_created,
        direct_command_created=direct_command_created,
        sandbox_execution_created=sandbox_execution_created,
        external_control_created=external_control_created,
        os_control_created=os_control_created,
        mouse_control_created=mouse_control_created,
        keyboard_control_created=keyboard_control_created,
        browser_control_created=browser_control_created,
        file_operation_created=file_operation_created,
        network_execution_created=network_execution_created,
        shell_execution_created=shell_execution_created,
        external_api_call_created=external_api_call_created,
        memory_layer_write_performed=memory_layer_write_performed,
        learning_candidate_created=learning_candidate_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        production_behavior_created=production_behavior_created,
        source_trace_refs=source_refs,
    )


def validate_host_body_internal_action_candidate(
    record: HostBodyInternalActionCandidateRecord | dict[str, object],
) -> dict[str, object]:
    item = _candidate(record)
    valid = item.candidate_status.startswith("internal_action_candidate_created") and not _candidate_has_forbidden(item)
    return {"valid": valid, "status": item.candidate_status, "reasons": [] if valid else [item.candidate_status]}


def build_host_body_internal_action_choice(
    *,
    choice_plan: HostBodyInternalActionChoicePlanRecord | dict[str, object],
    candidates: tuple[HostBodyInternalActionCandidateRecord | dict[str, object], ...] | list[HostBodyInternalActionCandidateRecord | dict[str, object]],
    teacher_approval_created: bool = False,
    learning_approval_created: bool = False,
    memory_write_approval_created: bool = False,
    task_selected_action_created: bool = False,
    final_action_created: bool = False,
    direct_command_created: bool = False,
    sandbox_execution_created: bool = False,
    external_control_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyInternalActionChoiceRecord:
    plan = _plan(choice_plan)
    items = tuple(_candidate(item) for item in candidates)
    status = _choice_status(
        candidates=items,
        teacher_approval_created=teacher_approval_created,
        learning_approval_created=learning_approval_created,
        memory_write_approval_created=memory_write_approval_created,
        task_selected_action_created=task_selected_action_created,
        final_action_created=final_action_created,
        direct_command_created=direct_command_created,
        sandbox_execution_created=sandbox_execution_created,
        external_control_created=external_control_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    selected = _select_candidate(items) if status == "internal_action_choice_selected" else None
    return HostBodyInternalActionChoiceRecord(
        internal_action_choice_id=f"host_body_internal_action_choice:{_slug(status)}:{_slug(selected.candidate_action_kind if selected else 'none')}",
        schema_version=CHOICE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_internal_action_choice_plan_id=plan.internal_action_choice_plan_id,
        candidate_ids=tuple(item.internal_action_candidate_id for item in items),
        selected_candidate_id=selected.internal_action_candidate_id if selected else None,
        selected_internal_action_kind=selected.candidate_action_kind if selected else None,
        selection_rule="highest_priority_then_deterministic_internal_order",
        selection_reason=_choice_reason(status, selected),
        choice_status=status,
        choice_summary=_choice_summary(status, selected),
        choice_created=True,
        internal_only=True,
        record_only=True,
        teacher_approval_created=teacher_approval_created,
        learning_approval_created=learning_approval_created,
        memory_write_approval_created=memory_write_approval_created,
        task_selected_action_created=task_selected_action_created,
        final_action_created=final_action_created,
        direct_command_created=direct_command_created,
        sandbox_execution_created=sandbox_execution_created,
        external_control_created=external_control_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=tuple(dict.fromkeys(ref for item in items for ref in item.source_trace_refs)),
    )


def validate_host_body_internal_action_choice(
    record: HostBodyInternalActionChoiceRecord | dict[str, object],
) -> dict[str, object]:
    item = _choice(record)
    valid = item.choice_status in {
        "internal_action_choice_selected",
        "internal_action_choice_deferred_no_candidates",
    } and not _choice_has_forbidden(item)
    return {"valid": valid, "status": item.choice_status, "reasons": [] if valid else [item.choice_status]}


def build_host_body_internal_action_result(
    *,
    internal_action_choice: HostBodyInternalActionChoiceRecord | dict[str, object],
    actual_screen_mutated: bool = False,
    actual_sound_played: bool = False,
    unity_runtime_mutated: bool = False,
    avatar_control_created: bool = False,
    teacher_approval_created: bool = False,
    learning_approval_created: bool = False,
    memory_write_approval_created: bool = False,
    task_selected_action_created: bool = False,
    final_action_created: bool = False,
    direct_command_created: bool = False,
    sandbox_execution_created: bool = False,
    external_control_created: bool = False,
    os_control_created: bool = False,
    mouse_control_created: bool = False,
    keyboard_control_created: bool = False,
    browser_control_created: bool = False,
    file_operation_created: bool = False,
    network_execution_created: bool = False,
    shell_execution_created: bool = False,
    external_api_call_created: bool = False,
    memory_layer_write_performed: bool = False,
    learning_candidate_created: bool = False,
    automatic_learning_approval_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
    production_behavior_created: bool = False,
) -> HostBodyInternalActionResultRecord:
    choice = _choice(internal_action_choice)
    status = _result_status(
        choice=choice,
        actual_screen_mutated=actual_screen_mutated,
        actual_sound_played=actual_sound_played,
        unity_runtime_mutated=unity_runtime_mutated,
        avatar_control_created=avatar_control_created,
        teacher_approval_created=teacher_approval_created,
        learning_approval_created=learning_approval_created,
        memory_write_approval_created=memory_write_approval_created,
        task_selected_action_created=task_selected_action_created,
        final_action_created=final_action_created,
        direct_command_created=direct_command_created,
        sandbox_execution_created=sandbox_execution_created,
        external_control_created=external_control_created,
        os_control_created=os_control_created,
        mouse_control_created=mouse_control_created,
        keyboard_control_created=keyboard_control_created,
        browser_control_created=browser_control_created,
        file_operation_created=file_operation_created,
        network_execution_created=network_execution_created,
        shell_execution_created=shell_execution_created,
        external_api_call_created=external_api_call_created,
        memory_layer_write_performed=memory_layer_write_performed,
        learning_candidate_created=learning_candidate_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        production_behavior_created=production_behavior_created,
    )
    kind = _result_kind(choice.selected_internal_action_kind, status)
    return HostBodyInternalActionResultRecord(
        internal_action_result_id=f"host_body_internal_action_result:{_slug(kind)}:{_slug(status)}",
        schema_version=RESULT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_internal_action_choice_id=choice.internal_action_choice_id,
        selected_internal_action_kind=choice.selected_internal_action_kind,
        result_kind=kind,
        result_status=status,
        result_summary=_result_summary(status, choice.selected_internal_action_kind),
        internal_marker_created=choice.selected_internal_action_kind in {"mark_event_interesting", "mark_uncertain"} and status.startswith("internal_action_result_recorded"),
        home_status_update_recorded=choice.selected_internal_action_kind == "update_home_status" and status.startswith("internal_action_result_recorded"),
        teacher_review_request_recorded=choice.selected_internal_action_kind == "request_teacher_review" and status.startswith("internal_action_result_recorded"),
        internal_focus_marker_recorded=choice.selected_internal_action_kind == "shift_internal_focus" and status.startswith("internal_action_result_recorded"),
        event_processing_pause_marker_recorded=choice.selected_internal_action_kind == "pause_event_processing" and status.startswith("internal_action_result_recorded"),
        observe_again_recommendation_recorded=choice.selected_internal_action_kind == "observe_again" and status.startswith("internal_action_result_recorded"),
        actual_screen_mutated=actual_screen_mutated,
        actual_sound_played=actual_sound_played,
        unity_runtime_mutated=unity_runtime_mutated,
        avatar_control_created=avatar_control_created,
        teacher_approval_created=teacher_approval_created,
        learning_approval_created=learning_approval_created,
        memory_write_approval_created=memory_write_approval_created,
        task_selected_action_created=task_selected_action_created,
        final_action_created=final_action_created,
        direct_command_created=direct_command_created,
        sandbox_execution_created=sandbox_execution_created,
        external_control_created=external_control_created,
        os_control_created=os_control_created,
        mouse_control_created=mouse_control_created,
        keyboard_control_created=keyboard_control_created,
        browser_control_created=browser_control_created,
        file_operation_created=file_operation_created,
        network_execution_created=network_execution_created,
        shell_execution_created=shell_execution_created,
        external_api_call_created=external_api_call_created,
        memory_layer_write_performed=memory_layer_write_performed,
        learning_candidate_created=learning_candidate_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        production_behavior_created=production_behavior_created,
        source_trace_refs=choice.source_trace_refs,
    )


def validate_host_body_internal_action_result(
    record: HostBodyInternalActionResultRecord | dict[str, object],
) -> dict[str, object]:
    item = _result(record)
    valid = item.result_status.startswith("internal_action_result_recorded") and not _result_has_forbidden(item)
    return {"valid": valid, "status": item.result_status, "reasons": [] if valid else [item.result_status]}


def build_host_body_internal_action_surface_effect(
    *,
    internal_action_result: HostBodyInternalActionResultRecord | dict[str, object],
    target_surface: str = "qingyin_home",
    actual_status_light_mutated: bool = False,
    actual_home_surface_mutated: bool = False,
    actual_unity_runtime_mutated: bool = False,
    actual_screen_mutated: bool = False,
    actual_sound_played: bool = False,
    first_output_created: bool = False,
    external_message_created: bool = False,
    file_written: bool = False,
    network_output_created: bool = False,
) -> HostBodyInternalActionSurfaceEffectRecord:
    result = _result(internal_action_result)
    status = _surface_effect_status(
        result=result,
        actual_status_light_mutated=actual_status_light_mutated,
        actual_home_surface_mutated=actual_home_surface_mutated,
        actual_unity_runtime_mutated=actual_unity_runtime_mutated,
        actual_screen_mutated=actual_screen_mutated,
        actual_sound_played=actual_sound_played,
        first_output_created=first_output_created,
        external_message_created=external_message_created,
        file_written=file_written,
        network_output_created=network_output_created,
    )
    kind = _surface_effect_kind(result, status)
    return HostBodyInternalActionSurfaceEffectRecord(
        internal_action_surface_effect_id=f"host_body_internal_action_surface_effect:{_slug(kind)}:{_slug(status)}",
        schema_version=SURFACE_EFFECT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_internal_action_result_id=result.internal_action_result_id,
        surface_effect_kind=kind,
        surface_effect_status=status,
        surface_effect_summary=_surface_effect_summary(status, kind),
        target_surface=target_surface,
        status_light_update_recorded=kind == "status_light_update_record" and status.startswith("surface_effect_recorded"),
        teacher_observed_surface_update_recorded=kind == "teacher_observed_update_record" and status.startswith("surface_effect_recorded"),
        home_render_update_recorded=kind == "home_render_update_record" and status.startswith("surface_effect_recorded"),
        actual_status_light_mutated=actual_status_light_mutated,
        actual_home_surface_mutated=actual_home_surface_mutated,
        actual_unity_runtime_mutated=actual_unity_runtime_mutated,
        actual_screen_mutated=actual_screen_mutated,
        actual_sound_played=actual_sound_played,
        first_output_created=first_output_created,
        external_message_created=external_message_created,
        file_written=file_written,
        network_output_created=network_output_created,
        source_trace_refs=result.source_trace_refs,
    )


def validate_host_body_internal_action_surface_effect(
    record: HostBodyInternalActionSurfaceEffectRecord | dict[str, object],
) -> dict[str, object]:
    item = _surface_effect(record)
    valid = item.surface_effect_status.startswith("surface_effect_recorded") or item.surface_effect_status == "surface_effect_none"
    valid = valid and not _surface_effect_has_forbidden(item)
    return {"valid": valid, "status": item.surface_effect_status, "reasons": [] if valid else [item.surface_effect_status]}


def build_host_body_internal_action_choice_set(
    *,
    choice_plan: HostBodyInternalActionChoicePlanRecord | dict[str, object],
    candidates: tuple[HostBodyInternalActionCandidateRecord | dict[str, object], ...] | list[HostBodyInternalActionCandidateRecord | dict[str, object]],
    choices: tuple[HostBodyInternalActionChoiceRecord | dict[str, object], ...] | list[HostBodyInternalActionChoiceRecord | dict[str, object]],
    results: tuple[HostBodyInternalActionResultRecord | dict[str, object], ...] | list[HostBodyInternalActionResultRecord | dict[str, object]],
    surface_effects: tuple[HostBodyInternalActionSurfaceEffectRecord | dict[str, object], ...] | list[HostBodyInternalActionSurfaceEffectRecord | dict[str, object]],
    choice_set_kind: str | None = None,
) -> HostBodyInternalActionChoiceSetRecord:
    plan = _plan(choice_plan)
    candidate_items = tuple(_candidate(item) for item in candidates)
    choice_items = tuple(_choice(item) for item in choices)
    result_items = tuple(_result(item) for item in results)
    effect_items = tuple(_surface_effect(item) for item in surface_effects)
    status = _choice_set_status(candidate_items, choice_items, result_items, effect_items)
    kind = choice_set_kind or _choice_set_kind(candidate_items, choice_items, result_items, effect_items, status)
    refs = tuple(
        dict.fromkeys(
            ref
            for group in (candidate_items, choice_items, result_items, effect_items)
            for item in group
            for ref in item.source_trace_refs
        )
    )
    return HostBodyInternalActionChoiceSetRecord(
        internal_action_choice_set_id=f"host_body_internal_action_choice_set:{_slug(kind)}:{_slug(status)}",
        schema_version=CHOICE_SET_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_internal_action_choice_plan_id=plan.internal_action_choice_plan_id,
        candidate_ids=tuple(item.internal_action_candidate_id for item in candidate_items),
        choice_ids=tuple(item.internal_action_choice_id for item in choice_items),
        result_ids=tuple(item.internal_action_result_id for item in result_items),
        surface_effect_ids=tuple(item.internal_action_surface_effect_id for item in effect_items),
        choice_set_kind=kind,
        choice_set_status=status,
        choice_set_summary=_choice_set_summary(status),
        candidate_count=len(candidate_items),
        choice_count=len(choice_items),
        result_count=len(result_items),
        surface_effect_count=len(effect_items),
        internal_only_confirmed=True,
        record_only_confirmed=True,
        external_control_created=any(_external_forbidden(item) for item in candidate_items + choice_items + result_items + effect_items),
        task_action_selection_created=any(_task_forbidden(item) for item in candidate_items + choice_items + result_items),
        memory_write_performed=any(_memory_forbidden(item) for item in candidate_items + result_items),
        learning_candidate_created=any(getattr(item, "learning_candidate_created", False) for item in candidate_items + result_items),
        automatic_learning_approval_created=any(
            getattr(item, "automatic_learning_approval_created", False) for item in candidate_items + result_items
        ),
        first_output_created=any(getattr(item, "first_output_created", False) for item in candidate_items + choice_items + result_items + effect_items),
        live_runtime_session_created=any(getattr(item, "live_runtime_session_created", False) for item in candidate_items + choice_items + result_items),
        production_behavior_created=any(getattr(item, "production_behavior_created", False) for item in candidate_items + result_items),
        source_trace_refs=refs,
    )


def validate_host_body_internal_action_choice_set(
    record: HostBodyInternalActionChoiceSetRecord | dict[str, object],
) -> dict[str, object]:
    item = _choice_set(record)
    valid = item.choice_set_status.startswith("internal_action_choice_set_recorded") and not _choice_set_has_forbidden(item)
    return {"valid": valid, "status": item.choice_set_status, "reasons": [] if valid else [item.choice_set_status]}


def build_host_body_internal_action_choice_audit(
    *,
    choice_plan: HostBodyInternalActionChoicePlanRecord | dict[str, object] | None,
    candidates: tuple[HostBodyInternalActionCandidateRecord | dict[str, object], ...] | list[HostBodyInternalActionCandidateRecord | dict[str, object]] = tuple(),
    choices: tuple[HostBodyInternalActionChoiceRecord | dict[str, object], ...] | list[HostBodyInternalActionChoiceRecord | dict[str, object]] = tuple(),
    results: tuple[HostBodyInternalActionResultRecord | dict[str, object], ...] | list[HostBodyInternalActionResultRecord | dict[str, object]] = tuple(),
    surface_effects: tuple[HostBodyInternalActionSurfaceEffectRecord | dict[str, object], ...] | list[HostBodyInternalActionSurfaceEffectRecord | dict[str, object]] = tuple(),
    choice_set: HostBodyInternalActionChoiceSetRecord | dict[str, object] | None = None,
    force_thought_engine_behavior: bool = False,
    force_production_behavior: bool = False,
) -> HostBodyInternalActionChoiceAudit:
    plan = _plan(choice_plan) if choice_plan is not None else None
    candidate_items = tuple(_candidate(item) for item in candidates)
    choice_items = tuple(_choice(item) for item in choices)
    result_items = tuple(_result(item) for item in results)
    effect_items = tuple(_surface_effect(item) for item in surface_effects)
    choice_set_item = _choice_set(choice_set) if choice_set is not None else None
    reasons = _audit_reasons(
        plan=plan,
        candidates=candidate_items,
        choices=choice_items,
        results=result_items,
        effects=effect_items,
        choice_set=choice_set_item,
        force_thought_engine_behavior=force_thought_engine_behavior,
        force_production_behavior=force_production_behavior,
    )
    status = _audit_status(reasons, choice_items, result_items)
    refs = tuple(
        dict.fromkeys(
            ref
            for group in (candidate_items, choice_items, result_items, effect_items)
            for item in group
            for ref in item.source_trace_refs
        )
    )
    return HostBodyInternalActionChoiceAudit(
        internal_action_choice_audit_id=f"host_body_internal_action_choice_audit:{_slug(status)}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_internal_action_choice_plan_id=plan.internal_action_choice_plan_id if plan else None,
        source_internal_action_choice_set_id=choice_set_item.internal_action_choice_set_id if choice_set_item else None,
        plan_valid=plan is not None and plan.plan_status == "internal_action_choice_plan_created",
        candidates_valid=all(item.candidate_status.startswith("internal_action_candidate_created") for item in candidate_items),
        choices_valid=all(item.choice_status in {"internal_action_choice_selected", "internal_action_choice_deferred_no_candidates"} for item in choice_items),
        results_valid=all(item.result_status.startswith("internal_action_result_recorded") for item in result_items),
        surface_effects_valid=all(
            item.surface_effect_status.startswith("surface_effect_recorded") or item.surface_effect_status == "surface_effect_none"
            for item in effect_items
        ),
        choice_set_valid=choice_set_item is not None and choice_set_item.choice_set_status.startswith("internal_action_choice_set_recorded"),
        internal_only_confirmed=True,
        record_only_confirmed=True,
        read_only_source_confirmed=True,
        allowed_internal_action_kinds_only="forbidden_kind" not in reasons,
        no_task_selected_action="task_action" not in reasons,
        no_final_action="final_action" not in reasons,
        no_direct_command="direct_command" not in reasons,
        no_sandbox_execution="sandbox_execution" not in reasons,
        no_external_control="external_control" not in reasons,
        no_os_control="os_control" not in reasons,
        no_mouse_control="mouse_control" not in reasons,
        no_keyboard_control="keyboard_control" not in reasons,
        no_browser_control="browser_control" not in reasons,
        no_file_operation="file_operation" not in reasons,
        no_network_execution="network_execution" not in reasons,
        no_shell_execution="shell_execution" not in reasons,
        no_external_api_call="external_api_call" not in reasons,
        no_actual_screen_mutation="actual_screen_mutation" not in reasons,
        no_actual_sound_output="actual_sound_output" not in reasons,
        no_unity_runtime_mutation="unity_runtime_mutation" not in reasons,
        no_avatar_control="avatar_control" not in reasons,
        no_memory_layer_write="memory_write" not in reasons,
        no_core_memory_write="core_memory_write" not in reasons,
        no_long_term_memory_write="long_term_memory_write" not in reasons,
        no_archive_memory_write="archive_memory_write" not in reasons,
        no_anchor_write="anchor_write" not in reasons,
        no_state_persistence_write="state_persistence" not in reasons,
        no_learning_candidate_creation="learning_candidate" not in reasons,
        no_automatic_learning_approval="automatic_learning_approval" not in reasons,
        no_teacher_approval_created="teacher_approval" not in reasons,
        no_first_output="first_output" not in reasons,
        no_live_runtime_session="live_runtime" not in reasons,
        no_thought_engine_behavior="thought_engine" not in reasons,
        no_production_behavior="production_behavior" not in reasons,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(reasons),
        source_trace_refs=refs,
    )


def validate_host_body_internal_action_choice_audit(
    record: HostBodyInternalActionChoiceAudit | dict[str, object],
) -> dict[str, object]:
    item = _audit(record)
    valid = item.audit_status.startswith("passed_")
    return {"valid": valid, "status": item.audit_status, "reasons": [] if valid else list(item.blocked_reasons)}


def build_host_body_internal_action_choice_readiness(
    internal_action_choice_audit: HostBodyInternalActionChoiceAudit | dict[str, object],
) -> HostBodyInternalActionChoiceReadinessRecord:
    audit = _audit(internal_action_choice_audit)
    passed = audit.audit_status.startswith("passed_")
    if passed:
        status = "ready_for_host_body_v0_milestone_audit_only"
    elif audit.source_internal_action_choice_plan_id is None:
        status = "not_ready_missing_internal_action_choice_audit"
    elif audit.audit_status.startswith("blocked_"):
        status = "blocked_forbidden_authority_detected"
    else:
        status = "not_ready_boundary_failure"
    return HostBodyInternalActionChoiceReadinessRecord(
        internal_action_choice_readiness_id=f"host_body_internal_action_choice_readiness:{audit.internal_action_choice_audit_id}",
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_internal_action_choice_audit_id=audit.internal_action_choice_audit_id,
        current_verified_capability=SAFE_CLAIM,
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason="Seal Host Body v0 with port map, fixture events, bridge, Home surface, trace history, and internal-only action choice.",
        ready_for_host_body_internal_action_home_surface_link=passed,
        ready_for_teacher_observed_host_body_cli=passed,
        ready_for_host_body_v0_milestone_audit=passed,
        ready_for_runtime_state_persistence_binding=passed,
        ready_for_task_engine_action_selection=False,
        ready_for_external_control=False,
        ready_for_os_control=False,
        ready_for_file_operation=False,
        ready_for_network_execution=False,
        ready_for_memory_layer_write=False,
        ready_for_learning_candidate_creation=False,
        ready_for_automatic_learning_approval=False,
        ready_for_first_output=False,
        ready_for_live_runtime_session=False,
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=audit.source_trace_refs,
    )


def validate_host_body_internal_action_choice_readiness(
    record: HostBodyInternalActionChoiceReadinessRecord | dict[str, object],
) -> dict[str, object]:
    item = _readiness(record)
    valid = item.readiness_status.startswith("ready_for_")
    return {"valid": valid, "status": item.readiness_status, "reasons": [] if valid else [item.readiness_status]}


def build_demo_camera_change_marks_interesting() -> dict[str, object]:
    return _build_internal_action_bundle(source_kind="camera_frame_changed")


def build_demo_unknown_event_marks_uncertain() -> dict[str, object]:
    return _build_internal_action_bundle(source_kind="camera_unknown_low_level_event")


def build_demo_deferred_dispatch_requests_teacher_review() -> dict[str, object]:
    return _build_internal_action_bundle(source_kind="deferred_dispatch")


def build_demo_host_idle_observe_again() -> dict[str, object]:
    return _build_internal_action_bundle(source_kind="host_idle")


def build_demo_update_home_status_choice() -> dict[str, object]:
    return _build_internal_action_bundle(source_kind="sensor_event_seen_status_light")


def build_demo_internal_action_choice_set() -> dict[str, object]:
    return _build_internal_action_bundle(source_kind="choice_set")


def build_demo_blocked_external_control_internal_action() -> dict[str, object]:
    return _build_internal_action_bundle(candidate_kwargs={"candidate_action_kind": "mouse_control"})


def build_demo_blocked_task_action_selection_internal_action() -> dict[str, object]:
    return _build_internal_action_bundle(candidate_kwargs={"task_selected_action_created": True})


def build_demo_blocked_teacher_approval_internal_action() -> dict[str, object]:
    return _build_internal_action_bundle(choice_kwargs={"teacher_approval_created": True})


def build_demo_blocked_first_output_internal_action() -> dict[str, object]:
    return _build_internal_action_bundle(result_kwargs={"first_output_created": True})


def build_demo_blocked_memory_write_internal_action() -> dict[str, object]:
    return _build_internal_action_bundle(result_kwargs={"memory_layer_write_performed": True})


def render_host_body_internal_action_choice_summary_text(
    audit: HostBodyInternalActionChoiceAudit | dict[str, object],
    readiness: HostBodyInternalActionChoiceReadinessRecord | dict[str, object] | None = None,
) -> str:
    audit_item = _audit(audit)
    readiness_item = _readiness(readiness) if readiness is not None else None
    parts = [
        f"host_body_internal_action_choice_audit={audit_item.audit_status}",
        f"internal_only={audit_item.internal_only_confirmed}",
        f"record_only={audit_item.record_only_confirmed}",
    ]
    if readiness_item is not None:
        parts.append(f"readiness={readiness_item.readiness_status}")
    return " ".join(parts)


def render_host_body_internal_action_choice_table(
    candidates: tuple[HostBodyInternalActionCandidateRecord | dict[str, object], ...] | list[HostBodyInternalActionCandidateRecord | dict[str, object]],
) -> str:
    lines = ["candidate | action | priority | status"]
    for item in tuple(_candidate(candidate) for candidate in candidates):
        lines.append(
            f"{item.internal_action_candidate_id} | {item.candidate_action_kind} | "
            f"{item.candidate_priority} | {item.candidate_status}"
        )
    return "\n".join(lines)


def _build_internal_action_bundle(
    *,
    source_kind: str = "camera_frame_changed",
    candidate_kwargs: dict[str, object] | None = None,
    choice_kwargs: dict[str, object] | None = None,
    result_kwargs: dict[str, object] | None = None,
    surface_effect_kwargs: dict[str, object] | None = None,
    audit_kwargs: dict[str, object] | None = None,
) -> dict[str, object]:
    trace_payload = build_demo_full_host_body_trace_history_lane()
    home_payload = build_demo_qingyin_home_internal_space_surface()
    trace_audit = HostBodyTraceHistoryAudit.from_dict(trace_payload["trace_history_audit"])
    trace_readback = HostBodyTraceHistoryReadbackRecord.from_dict(trace_payload["trace_history_readback"])
    home_audit = QingyinHomeInternalSpaceSurfaceAudit.from_dict(home_payload["home_internal_space_surface_audit"])
    plan = build_host_body_internal_action_choice_plan(
        trace_history_audit=trace_audit,
        trace_history_readback=trace_readback,
        home_surface_audit=home_audit,
    )
    source = _demo_source_for_kind(source_kind, trace_payload, home_payload)
    candidate = build_host_body_internal_action_candidate(
        choice_plan=plan,
        trace_history_readback=trace_readback,
        **source,
        **(candidate_kwargs or {}),
    )
    extra_candidates = []
    if source_kind == "choice_set":
        for kind in ("observe_again", "mark_uncertain", "request_teacher_review"):
            extra_candidates.append(
                build_host_body_internal_action_candidate(
                    choice_plan=plan,
                    trace_history_readback=trace_readback,
                    candidate_action_kind=kind,
                )
            )
    candidates = (candidate, *extra_candidates)
    choice = build_host_body_internal_action_choice(
        choice_plan=plan,
        candidates=candidates,
        **(choice_kwargs or {}),
    )
    result = build_host_body_internal_action_result(
        internal_action_choice=choice,
        **(result_kwargs or {}),
    )
    effect = build_host_body_internal_action_surface_effect(
        internal_action_result=result,
        **(surface_effect_kwargs or {}),
    )
    choice_set = build_host_body_internal_action_choice_set(
        choice_plan=plan,
        candidates=candidates,
        choices=(choice,),
        results=(result,),
        surface_effects=(effect,),
        choice_set_kind="mixed_internal_action_choice_demo" if extra_candidates else None,
    )
    audit = build_host_body_internal_action_choice_audit(
        choice_plan=plan,
        candidates=candidates,
        choices=(choice,),
        results=(result,),
        surface_effects=(effect,),
        choice_set=choice_set,
        **(audit_kwargs or {}),
    )
    readiness = build_host_body_internal_action_choice_readiness(audit)
    return {
        "internal_action_choice_plan": plan.to_dict(),
        "internal_action_candidates": [item.to_dict() for item in candidates],
        "internal_action_choice": choice.to_dict(),
        "internal_action_result": result.to_dict(),
        "internal_action_surface_effect": effect.to_dict(),
        "internal_action_choice_set": choice_set.to_dict(),
        "internal_action_choice_audit": audit.to_dict(),
        "internal_action_choice_readiness": readiness.to_dict(),
        "rendered_internal_action_choice_summary": render_host_body_internal_action_choice_summary_text(audit, readiness),
        "rendered_internal_action_choice_table": render_host_body_internal_action_choice_table(candidates),
    }


def _demo_source_for_kind(
    source_kind: str,
    trace_payload: dict[str, object],
    home_payload: dict[str, object],
) -> dict[str, object]:
    entries = [HostBodyTraceHistoryEntryRecord.from_dict(item) for item in trace_payload["trace_history_entries"]]
    if source_kind == "camera_frame_changed":
        return {"trace_history_entry": _find_entry(entries, "camera_frame_changed")}
    if source_kind == "host_idle":
        return {"trace_history_entry": _find_entry(entries, "host_idle")}
    if source_kind == "camera_unknown_low_level_event":
        unknown = _synthetic_trace_entry(trace_payload["trace_history_lane_plan"], "camera_unknown_low_level_event")
        return {"trace_history_entry": unknown}
    if source_kind == "deferred_dispatch":
        deferred_payload = build_demo_deferred_dispatch_host_body_runtime_bridge()
        bridge_trace = HostBodyRuntimeBridgeTraceRecord.from_dict(deferred_payload["host_body_runtime_bridge_trace"])
        return {"runtime_bridge_trace": bridge_trace}
    if source_kind == "sensor_event_seen_status_light":
        lights = [QingyinHomeStatusLightRecord.from_dict(item) for item in home_payload["home_status_lights"]]
        return {"home_status_light": next(item for item in lights if item.status_light_kind == "sensor_event_seen")}
    if source_kind == "choice_set":
        return {"trace_history_entry": _find_entry(entries, "camera_frame_changed")}
    return {"trace_history_entry": entries[0]}


def _find_entry(entries: list[HostBodyTraceHistoryEntryRecord], event_type: str) -> HostBodyTraceHistoryEntryRecord:
    return next(item for item in entries if item.source_event_type == event_type)


def _synthetic_trace_entry(
    plan: dict[str, object],
    event_type: str,
) -> HostBodyTraceHistoryEntryRecord:
    return HostBodyTraceHistoryEntryRecord(
        trace_history_entry_id=f"host_body_trace_entry:synthetic:{event_type}",
        schema_version="qingyin_host_body_trace_history_entry_v0",
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_trace_history_lane_plan_id=str(plan["trace_history_lane_plan_id"]),
        sequence_index=999,
        source_record_id=f"host_body_event:synthetic:{event_type}",
        source_record_family="host_body_event",
        source_record_kind="camera_low_level_event",
        source_event_type=event_type,
        source_event_family="camera_low_level_event",
        source_port_kind="camera_port",
        source_surface_kind=None,
        source_bridge_status=None,
        entry_kind="sensor_event_entry",
        entry_status="trace_history_entry_recorded_fixture_only",
        entry_summary=f"Synthetic fixture trace entry for {event_type}.",
        entry_payload={"event_type": event_type, "fixture_only": True, "read_only": True},
        read_only_entry=True,
        fixture_only_source=True,
        semantic_interpretation_created=False,
        action_selection_influence_created=False,
        memory_layer_write_performed=False,
        state_persistence_write_performed=False,
        file_write_performed=False,
        learning_candidate_created=False,
        first_output_created=False,
        live_runtime_session_created=False,
        production_behavior_created=False,
        source_trace_refs=tuple(),
    )


def _plan_status(
    *,
    trace_audit: HostBodyTraceHistoryAudit | None,
    task_engine_action_selection_allowed: bool,
    final_action_allowed: bool,
    direct_command_allowed: bool,
    sandbox_execution_allowed: bool,
    external_control_allowed: bool,
    memory_write_allowed: bool,
    learning_candidate_creation_allowed: bool,
    automatic_learning_approval_allowed: bool,
    first_output_allowed: bool,
    live_runtime_session_allowed: bool,
) -> str:
    if trace_audit is None:
        return "blocked_missing_trace_history_audit"
    if task_engine_action_selection_allowed or final_action_allowed or direct_command_allowed or sandbox_execution_allowed:
        return "blocked_task_action_selection_allowed"
    if external_control_allowed:
        return "blocked_external_control_allowed"
    if memory_write_allowed or learning_candidate_creation_allowed or automatic_learning_approval_allowed:
        return "blocked_memory_write_allowed"
    if first_output_allowed:
        return "blocked_first_output_allowed"
    if live_runtime_session_allowed:
        return "blocked_live_runtime_allowed"
    if not trace_audit.audit_status.startswith("passed_"):
        return "blocked_forbidden_authority_detected"
    return "internal_action_choice_plan_created"


def _infer_candidate_action(
    *,
    readback: HostBodyTraceHistoryReadbackRecord | None,
    entry: HostBodyTraceHistoryEntryRecord | None,
    light: QingyinHomeStatusLightRecord | None,
    bridge_trace: HostBodyRuntimeBridgeTraceRecord | None,
    requested_kind: str | None,
) -> dict[str, Any]:
    if requested_kind:
        return {"kind": requested_kind, "priority": _default_priority(requested_kind), "reasons": ("explicit_fixture_candidate",)}
    if bridge_trace is not None and "deferred" in bridge_trace.bridge_trace_status:
        return {"kind": "request_teacher_review", "priority": 90, "reasons": ("runtime_bridge_deferred_dispatch",)}
    if light is not None:
        if light.status_light_kind == "boundary_warning":
            return {"kind": "request_teacher_review", "priority": 90, "reasons": ("boundary_warning_status_light",)}
        if light.status_light_kind == "sensor_event_seen":
            return {"kind": "update_home_status", "priority": 50, "reasons": ("sensor_event_seen_status_light",)}
    event_type = entry.source_event_type if entry else None
    if event_type in {"camera_frame_changed", "mic_peak_detected"}:
        return {"kind": "mark_event_interesting", "priority": 70, "reasons": (f"{event_type}_interesting",)}
    if event_type in {"camera_unknown_low_level_event", "mic_unknown_low_level_event"}:
        return {"kind": "mark_uncertain", "priority": 80, "reasons": (f"{event_type}_uncertain",)}
    if event_type == "host_idle":
        return {"kind": "observe_again", "priority": 30, "reasons": ("host_idle_observe_again",)}
    if readback is not None and readback.readback_mode == "recent_n_entries" and readback.matched_entry_count == 0:
        return {"kind": "observe_again", "priority": 20, "reasons": ("empty_recent_readback",)}
    return {"kind": "shift_internal_focus", "priority": 10, "reasons": ("default_internal_focus",)}


def _candidate_status(
    *,
    requested_kind: str,
    task_selected_action_created: bool,
    final_action_created: bool,
    direct_command_created: bool,
    sandbox_execution_created: bool,
    external_control_created: bool,
    os_control_created: bool,
    mouse_control_created: bool,
    keyboard_control_created: bool,
    browser_control_created: bool,
    file_operation_created: bool,
    network_execution_created: bool,
    shell_execution_created: bool,
    external_api_call_created: bool,
    memory_layer_write_performed: bool,
    learning_candidate_created: bool,
    automatic_learning_approval_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
    production_behavior_created: bool,
    light: QingyinHomeStatusLightRecord | None,
    entry: HostBodyTraceHistoryEntryRecord | None,
) -> str:
    if requested_kind not in ALLOWED_INTERNAL_ACTION_KINDS:
        if requested_kind in FORBIDDEN_EXTERNAL_ACTION_KINDS:
            return "internal_action_candidate_blocked_external_control"
        return "internal_action_candidate_blocked_forbidden_kind"
    if task_selected_action_created or final_action_created or direct_command_created or sandbox_execution_created:
        return "internal_action_candidate_blocked_task_action_selection"
    if external_control_created or os_control_created or mouse_control_created or keyboard_control_created or browser_control_created or file_operation_created or network_execution_created or shell_execution_created or external_api_call_created:
        return "internal_action_candidate_blocked_external_control"
    if first_output_created:
        return "internal_action_candidate_blocked_first_output"
    if memory_layer_write_performed or learning_candidate_created or automatic_learning_approval_created or live_runtime_session_created or production_behavior_created:
        return "internal_action_candidate_blocked_forbidden_authority"
    if light is not None:
        return "internal_action_candidate_created_from_status_light"
    if entry is not None:
        return "internal_action_candidate_created_from_trace_history"
    return "internal_action_candidate_created"


def _choice_status(
    *,
    candidates: tuple[HostBodyInternalActionCandidateRecord, ...],
    teacher_approval_created: bool,
    learning_approval_created: bool,
    memory_write_approval_created: bool,
    task_selected_action_created: bool,
    final_action_created: bool,
    direct_command_created: bool,
    sandbox_execution_created: bool,
    external_control_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
) -> str:
    if not candidates:
        return "internal_action_choice_deferred_no_candidates"
    if any(not item.candidate_status.startswith("internal_action_candidate_created") for item in candidates):
        return "internal_action_choice_blocked_invalid_candidate"
    if teacher_approval_created or learning_approval_created or memory_write_approval_created:
        return "internal_action_choice_blocked_teacher_approval_created"
    if task_selected_action_created or final_action_created or direct_command_created or sandbox_execution_created:
        return "internal_action_choice_blocked_task_action_selection"
    if external_control_created:
        return "internal_action_choice_blocked_external_control"
    if first_output_created:
        return "internal_action_choice_blocked_first_output"
    if live_runtime_session_created:
        return "internal_action_choice_blocked_forbidden_authority"
    return "internal_action_choice_selected"


def _select_candidate(
    candidates: tuple[HostBodyInternalActionCandidateRecord, ...]
) -> HostBodyInternalActionCandidateRecord:
    return sorted(
        candidates,
        key=lambda item: (-item.candidate_priority, CHOICE_TIE_ORDER[item.candidate_action_kind]),
    )[0]


def _result_status(
    *,
    choice: HostBodyInternalActionChoiceRecord,
    actual_screen_mutated: bool,
    actual_sound_played: bool,
    unity_runtime_mutated: bool,
    avatar_control_created: bool,
    teacher_approval_created: bool,
    learning_approval_created: bool,
    memory_write_approval_created: bool,
    task_selected_action_created: bool,
    final_action_created: bool,
    direct_command_created: bool,
    sandbox_execution_created: bool,
    external_control_created: bool,
    os_control_created: bool,
    mouse_control_created: bool,
    keyboard_control_created: bool,
    browser_control_created: bool,
    file_operation_created: bool,
    network_execution_created: bool,
    shell_execution_created: bool,
    external_api_call_created: bool,
    memory_layer_write_performed: bool,
    learning_candidate_created: bool,
    automatic_learning_approval_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
    production_behavior_created: bool,
) -> str:
    if choice.choice_status != "internal_action_choice_selected":
        return "internal_action_result_blocked_forbidden_authority"
    if actual_screen_mutated or actual_sound_played or unity_runtime_mutated or avatar_control_created:
        return "internal_action_result_blocked_external_control"
    if teacher_approval_created or learning_approval_created or memory_write_approval_created:
        return "internal_action_result_blocked_forbidden_authority"
    if task_selected_action_created or final_action_created or direct_command_created or sandbox_execution_created:
        return "internal_action_result_blocked_task_action_selection"
    if external_control_created or os_control_created or mouse_control_created or keyboard_control_created or browser_control_created or file_operation_created or network_execution_created or shell_execution_created or external_api_call_created:
        return "internal_action_result_blocked_external_control"
    if memory_layer_write_performed or learning_candidate_created or automatic_learning_approval_created:
        return "internal_action_result_blocked_memory_write"
    if first_output_created:
        return "internal_action_result_blocked_first_output"
    if live_runtime_session_created or production_behavior_created:
        return "internal_action_result_blocked_forbidden_authority"
    if choice.selected_internal_action_kind == "request_teacher_review":
        return "internal_action_result_recorded_request_teacher_review"
    if choice.selected_internal_action_kind == "update_home_status":
        return "internal_action_result_recorded_update_home_status"
    if choice.selected_internal_action_kind == "mark_uncertain":
        return "internal_action_result_recorded_mark_uncertain"
    return "internal_action_result_recorded"


def _surface_effect_status(
    *,
    result: HostBodyInternalActionResultRecord,
    actual_status_light_mutated: bool,
    actual_home_surface_mutated: bool,
    actual_unity_runtime_mutated: bool,
    actual_screen_mutated: bool,
    actual_sound_played: bool,
    first_output_created: bool,
    external_message_created: bool,
    file_written: bool,
    network_output_created: bool,
) -> str:
    if actual_status_light_mutated or actual_home_surface_mutated or actual_unity_runtime_mutated or actual_screen_mutated or actual_sound_played:
        return "surface_effect_blocked_actual_mutation"
    if first_output_created:
        return "surface_effect_blocked_first_output"
    if external_message_created or file_written or network_output_created:
        return "surface_effect_blocked_external_output"
    if not result.result_status.startswith("internal_action_result_recorded"):
        return "surface_effect_none"
    if result.home_status_update_recorded:
        return "surface_effect_recorded_status_light"
    if result.teacher_review_request_recorded:
        return "surface_effect_recorded_teacher_observed"
    if result.internal_marker_created or result.observe_again_recommendation_recorded or result.event_processing_pause_marker_recorded or result.internal_focus_marker_recorded:
        return "surface_effect_recorded_home_render"
    return "surface_effect_none"


def _choice_set_status(
    candidates: tuple[HostBodyInternalActionCandidateRecord, ...],
    choices: tuple[HostBodyInternalActionChoiceRecord, ...],
    results: tuple[HostBodyInternalActionResultRecord, ...],
    effects: tuple[HostBodyInternalActionSurfaceEffectRecord, ...],
) -> str:
    if not candidates and not choices and not results and not effects:
        return "internal_action_choice_set_recorded_empty"
    all_records = candidates + choices + results + effects
    if any(_task_forbidden(item) for item in all_records):
        return "internal_action_choice_set_blocked_task_action_selection"
    if any(_external_forbidden(item) for item in all_records):
        return "internal_action_choice_set_blocked_external_control"
    if any(_memory_forbidden(item) for item in all_records):
        return "internal_action_choice_set_blocked_memory_write"
    if any(getattr(item, "first_output_created", False) for item in all_records):
        return "internal_action_choice_set_blocked_first_output"
    if any(getattr(item, "production_behavior_created", False) or getattr(item, "live_runtime_session_created", False) for item in all_records):
        return "internal_action_choice_set_blocked_forbidden_authority"
    if any(
        getattr(item, "candidate_status", "").startswith("internal_action_candidate_blocked")
        or getattr(item, "choice_status", "").startswith("internal_action_choice_blocked")
        or getattr(item, "result_status", "").startswith("internal_action_result_blocked")
        or getattr(item, "surface_effect_status", "").startswith("surface_effect_blocked")
        for item in all_records
    ):
        return "internal_action_choice_set_blocked_forbidden_authority"
    return "internal_action_choice_set_recorded"


def _audit_reasons(
    *,
    plan: HostBodyInternalActionChoicePlanRecord | None,
    candidates: tuple[HostBodyInternalActionCandidateRecord, ...],
    choices: tuple[HostBodyInternalActionChoiceRecord, ...],
    results: tuple[HostBodyInternalActionResultRecord, ...],
    effects: tuple[HostBodyInternalActionSurfaceEffectRecord, ...],
    choice_set: HostBodyInternalActionChoiceSetRecord | None,
    force_thought_engine_behavior: bool,
    force_production_behavior: bool,
) -> list[str]:
    reasons: list[str] = []
    if plan is None or plan.plan_status != "internal_action_choice_plan_created":
        reasons.append("invalid_plan")
        if plan is not None:
            _append_plan_forbidden_reasons(reasons, plan)
    for item in candidates:
        if not item.candidate_status.startswith("internal_action_candidate_created"):
            reasons.append("invalid_candidate")
        _append_candidate_forbidden_reasons(reasons, item)
    for item in choices:
        if item.choice_status not in {"internal_action_choice_selected", "internal_action_choice_deferred_no_candidates"}:
            reasons.append("invalid_choice")
        _append_choice_forbidden_reasons(reasons, item)
    for item in results:
        if not item.result_status.startswith("internal_action_result_recorded"):
            reasons.append("invalid_result")
        _append_result_forbidden_reasons(reasons, item)
    for item in effects:
        if not (item.surface_effect_status.startswith("surface_effect_recorded") or item.surface_effect_status == "surface_effect_none"):
            reasons.append("invalid_surface_effect")
        _append_surface_effect_forbidden_reasons(reasons, item)
    if choice_set is None or not choice_set.choice_set_status.startswith("internal_action_choice_set_recorded"):
        reasons.append("invalid_choice_set")
        if choice_set is not None:
            _append_choice_set_forbidden_reasons(reasons, choice_set)
    if force_thought_engine_behavior:
        reasons.append("thought_engine")
    if force_production_behavior:
        reasons.append("production_behavior")
    return list(dict.fromkeys(reasons))


def _audit_status(
    reasons: list[str],
    choices: tuple[HostBodyInternalActionChoiceRecord, ...],
    results: tuple[HostBodyInternalActionResultRecord, ...],
) -> str:
    if "task_action" in reasons or "final_action" in reasons or "direct_command" in reasons or "sandbox_execution" in reasons:
        return "blocked_task_action_selection_detected"
    if "os_control" in reasons or "mouse_control" in reasons or "keyboard_control" in reasons or "browser_control" in reasons:
        return "blocked_os_control_detected"
    if "file_operation" in reasons:
        return "blocked_file_operation_detected"
    if "network_execution" in reasons or "shell_execution" in reasons or "external_api_call" in reasons:
        return "blocked_network_execution_detected"
    if "external_control" in reasons or "actual_screen_mutation" in reasons or "actual_sound_output" in reasons or "unity_runtime_mutation" in reasons or "avatar_control" in reasons:
        return "blocked_external_control_detected"
    if "memory_write" in reasons:
        return "blocked_memory_write_detected"
    if "learning_candidate" in reasons or "automatic_learning_approval" in reasons:
        return "blocked_learning_candidate_creation_detected"
    if "teacher_approval" in reasons:
        return "blocked_teacher_approval_created"
    if "first_output" in reasons:
        return "blocked_first_output_detected"
    if "live_runtime" in reasons:
        return "blocked_live_runtime_detected"
    if "production_behavior" in reasons or "thought_engine" in reasons:
        return "blocked_production_behavior_detected"
    if "invalid_plan" in reasons:
        return "blocked_invalid_plan"
    if "invalid_candidate" in reasons:
        return "blocked_invalid_candidate"
    if "invalid_choice" in reasons:
        return "blocked_invalid_choice"
    if "invalid_result" in reasons:
        return "blocked_invalid_result"
    if "invalid_surface_effect" in reasons:
        return "blocked_invalid_surface_effect"
    selected = choices[0].selected_internal_action_kind if choices else None
    if selected == "request_teacher_review":
        return "passed_internal_action_choice_request_teacher_review"
    if selected == "update_home_status":
        return "passed_internal_action_choice_update_home_status"
    if selected == "mark_uncertain":
        return "passed_internal_action_choice_mark_uncertain"
    if selected == "observe_again":
        return "passed_internal_action_choice_observe_again"
    return "passed_host_body_internal_action_choice"


def _append_plan_forbidden_reasons(reasons: list[str], plan: HostBodyInternalActionChoicePlanRecord) -> None:
    if plan.task_engine_action_selection_allowed:
        reasons.append("task_action")
    if plan.final_action_allowed:
        reasons.append("final_action")
    if plan.direct_command_allowed:
        reasons.append("direct_command")
    if plan.sandbox_execution_allowed:
        reasons.append("sandbox_execution")
    if plan.external_control_allowed:
        reasons.append("external_control")
    if plan.memory_write_allowed:
        reasons.append("memory_write")
    if plan.learning_candidate_creation_allowed:
        reasons.append("learning_candidate")
    if plan.automatic_learning_approval_allowed:
        reasons.append("automatic_learning_approval")
    if plan.first_output_allowed:
        reasons.append("first_output")
    if plan.live_runtime_session_allowed:
        reasons.append("live_runtime")


def _append_candidate_forbidden_reasons(reasons: list[str], item: HostBodyInternalActionCandidateRecord) -> None:
    if item.candidate_status == "internal_action_candidate_blocked_external_control":
        reasons.append("external_control")
    if item.candidate_status == "internal_action_candidate_blocked_task_action_selection":
        reasons.append("task_action")
    if item.candidate_status == "internal_action_candidate_blocked_first_output":
        reasons.append("first_output")
    if item.task_selected_action_created:
        reasons.append("task_action")
    if item.final_action_created:
        reasons.append("final_action")
    if item.direct_command_created:
        reasons.append("direct_command")
    if item.sandbox_execution_created:
        reasons.append("sandbox_execution")
    if item.external_control_created:
        reasons.append("external_control")
    if item.os_control_created:
        reasons.append("os_control")
    if item.mouse_control_created:
        reasons.append("mouse_control")
    if item.keyboard_control_created:
        reasons.append("keyboard_control")
    if item.browser_control_created:
        reasons.append("browser_control")
    if item.file_operation_created:
        reasons.append("file_operation")
    if item.network_execution_created:
        reasons.append("network_execution")
    if item.shell_execution_created:
        reasons.append("shell_execution")
    if item.external_api_call_created:
        reasons.append("external_api_call")
    if item.memory_layer_write_performed:
        reasons.append("memory_write")
    if item.learning_candidate_created:
        reasons.append("learning_candidate")
    if item.automatic_learning_approval_created:
        reasons.append("automatic_learning_approval")
    if item.first_output_created:
        reasons.append("first_output")
    if item.live_runtime_session_created:
        reasons.append("live_runtime")
    if item.production_behavior_created:
        reasons.append("production_behavior")


def _append_choice_forbidden_reasons(reasons: list[str], item: HostBodyInternalActionChoiceRecord) -> None:
    if item.teacher_approval_created or item.learning_approval_created or item.memory_write_approval_created:
        reasons.append("teacher_approval")
    if item.task_selected_action_created:
        reasons.append("task_action")
    if item.final_action_created:
        reasons.append("final_action")
    if item.direct_command_created:
        reasons.append("direct_command")
    if item.sandbox_execution_created:
        reasons.append("sandbox_execution")
    if item.external_control_created:
        reasons.append("external_control")
    if item.first_output_created:
        reasons.append("first_output")
    if item.live_runtime_session_created:
        reasons.append("live_runtime")


def _append_result_forbidden_reasons(reasons: list[str], item: HostBodyInternalActionResultRecord) -> None:
    if item.actual_screen_mutated:
        reasons.append("actual_screen_mutation")
    if item.actual_sound_played:
        reasons.append("actual_sound_output")
    if item.unity_runtime_mutated:
        reasons.append("unity_runtime_mutation")
    if item.avatar_control_created:
        reasons.append("avatar_control")
    if item.teacher_approval_created or item.learning_approval_created or item.memory_write_approval_created:
        reasons.append("teacher_approval")
    if item.task_selected_action_created:
        reasons.append("task_action")
    if item.final_action_created:
        reasons.append("final_action")
    if item.direct_command_created:
        reasons.append("direct_command")
    if item.sandbox_execution_created:
        reasons.append("sandbox_execution")
    if item.external_control_created:
        reasons.append("external_control")
    if item.os_control_created:
        reasons.append("os_control")
    if item.mouse_control_created:
        reasons.append("mouse_control")
    if item.keyboard_control_created:
        reasons.append("keyboard_control")
    if item.browser_control_created:
        reasons.append("browser_control")
    if item.file_operation_created:
        reasons.append("file_operation")
    if item.network_execution_created:
        reasons.append("network_execution")
    if item.shell_execution_created:
        reasons.append("shell_execution")
    if item.external_api_call_created:
        reasons.append("external_api_call")
    if item.memory_layer_write_performed:
        reasons.append("memory_write")
    if item.learning_candidate_created:
        reasons.append("learning_candidate")
    if item.automatic_learning_approval_created:
        reasons.append("automatic_learning_approval")
    if item.first_output_created:
        reasons.append("first_output")
    if item.live_runtime_session_created:
        reasons.append("live_runtime")
    if item.production_behavior_created:
        reasons.append("production_behavior")


def _append_surface_effect_forbidden_reasons(reasons: list[str], item: HostBodyInternalActionSurfaceEffectRecord) -> None:
    if item.actual_status_light_mutated or item.actual_home_surface_mutated or item.actual_screen_mutated:
        reasons.append("actual_screen_mutation")
    if item.actual_sound_played:
        reasons.append("actual_sound_output")
    if item.actual_unity_runtime_mutated:
        reasons.append("unity_runtime_mutation")
    if item.first_output_created:
        reasons.append("first_output")
    if item.external_message_created:
        reasons.append("external_control")
    if item.file_written:
        reasons.append("file_operation")
    if item.network_output_created:
        reasons.append("network_execution")


def _append_choice_set_forbidden_reasons(reasons: list[str], item: HostBodyInternalActionChoiceSetRecord) -> None:
    if item.external_control_created:
        reasons.append("external_control")
    if item.task_action_selection_created:
        reasons.append("task_action")
    if item.memory_write_performed:
        reasons.append("memory_write")
    if item.learning_candidate_created:
        reasons.append("learning_candidate")
    if item.automatic_learning_approval_created:
        reasons.append("automatic_learning_approval")
    if item.first_output_created:
        reasons.append("first_output")
    if item.live_runtime_session_created:
        reasons.append("live_runtime")
    if item.production_behavior_created:
        reasons.append("production_behavior")


def _result_kind(action_kind: str | None, status: str) -> str:
    if status.startswith("internal_action_result_blocked") or action_kind is None:
        return "blocked_result"
    return {
        "request_teacher_review": "teacher_review_request_record",
        "update_home_status": "home_status_update_record",
        "shift_internal_focus": "internal_focus_marker",
        "pause_event_processing": "event_processing_pause_marker",
        "observe_again": "observe_again_recommendation",
    }.get(action_kind, "internal_marker_result")


def _surface_effect_kind(result: HostBodyInternalActionResultRecord, status: str) -> str:
    if status.startswith("surface_effect_blocked"):
        return "blocked_surface_effect"
    if result.home_status_update_recorded:
        return "status_light_update_record"
    if result.teacher_review_request_recorded:
        return "teacher_observed_update_record"
    if result.internal_marker_created or result.observe_again_recommendation_recorded or result.event_processing_pause_marker_recorded or result.internal_focus_marker_recorded:
        return "home_render_update_record"
    return "no_surface_effect"


def _choice_set_kind(
    candidates: tuple[HostBodyInternalActionCandidateRecord, ...],
    choices: tuple[HostBodyInternalActionChoiceRecord, ...],
    results: tuple[HostBodyInternalActionResultRecord, ...],
    effects: tuple[HostBodyInternalActionSurfaceEffectRecord, ...],
    status: str,
) -> str:
    if status.startswith("internal_action_choice_set_blocked"):
        return "blocked_internal_action_choice_demo"
    if not candidates and not choices and not results and not effects:
        return "empty_internal_action_choice_demo"
    return "single_internal_action_choice_demo" if len(candidates) == 1 else "mixed_internal_action_choice_demo"


def _default_priority(kind: str) -> int:
    return {
        "request_teacher_review": 90,
        "pause_event_processing": 85,
        "mark_uncertain": 80,
        "mark_event_interesting": 70,
        "update_home_status": 50,
        "observe_again": 30,
        "shift_internal_focus": 10,
    }.get(kind, 0)


def _plan_constants_safe(item: HostBodyInternalActionChoicePlanRecord) -> bool:
    return (
        item.internal_only
        and item.record_only
        and item.read_only_source_required
        and not item.task_engine_action_selection_allowed
        and not item.final_action_allowed
        and not item.direct_command_allowed
        and not item.sandbox_execution_allowed
        and not item.external_control_allowed
        and not item.memory_write_allowed
        and not item.learning_candidate_creation_allowed
        and not item.automatic_learning_approval_allowed
        and not item.first_output_allowed
        and not item.live_runtime_session_allowed
    )


def _candidate_has_forbidden(item: HostBodyInternalActionCandidateRecord) -> bool:
    return any(
        (
            item.task_selected_action_created,
            item.final_action_created,
            item.direct_command_created,
            item.sandbox_execution_created,
            item.external_control_created,
            item.os_control_created,
            item.mouse_control_created,
            item.keyboard_control_created,
            item.browser_control_created,
            item.file_operation_created,
            item.network_execution_created,
            item.shell_execution_created,
            item.external_api_call_created,
            item.memory_layer_write_performed,
            item.learning_candidate_created,
            item.automatic_learning_approval_created,
            item.first_output_created,
            item.live_runtime_session_created,
            item.production_behavior_created,
        )
    )


def _choice_has_forbidden(item: HostBodyInternalActionChoiceRecord) -> bool:
    return any(
        (
            item.teacher_approval_created,
            item.learning_approval_created,
            item.memory_write_approval_created,
            item.task_selected_action_created,
            item.final_action_created,
            item.direct_command_created,
            item.sandbox_execution_created,
            item.external_control_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _result_has_forbidden(item: HostBodyInternalActionResultRecord) -> bool:
    return any(
        (
            item.actual_screen_mutated,
            item.actual_sound_played,
            item.unity_runtime_mutated,
            item.avatar_control_created,
            item.teacher_approval_created,
            item.learning_approval_created,
            item.memory_write_approval_created,
            item.task_selected_action_created,
            item.final_action_created,
            item.direct_command_created,
            item.sandbox_execution_created,
            item.external_control_created,
            item.os_control_created,
            item.mouse_control_created,
            item.keyboard_control_created,
            item.browser_control_created,
            item.file_operation_created,
            item.network_execution_created,
            item.shell_execution_created,
            item.external_api_call_created,
            item.memory_layer_write_performed,
            item.learning_candidate_created,
            item.automatic_learning_approval_created,
            item.first_output_created,
            item.live_runtime_session_created,
            item.production_behavior_created,
        )
    )


def _surface_effect_has_forbidden(item: HostBodyInternalActionSurfaceEffectRecord) -> bool:
    return any(
        (
            item.actual_status_light_mutated,
            item.actual_home_surface_mutated,
            item.actual_unity_runtime_mutated,
            item.actual_screen_mutated,
            item.actual_sound_played,
            item.first_output_created,
            item.external_message_created,
            item.file_written,
            item.network_output_created,
        )
    )


def _choice_set_has_forbidden(item: HostBodyInternalActionChoiceSetRecord) -> bool:
    return any(
        (
            item.external_control_created,
            item.task_action_selection_created,
            item.memory_write_performed,
            item.learning_candidate_created,
            item.automatic_learning_approval_created,
            item.first_output_created,
            item.live_runtime_session_created,
            item.production_behavior_created,
        )
    )


def _task_forbidden(item: object) -> bool:
    return any(
        getattr(item, field, False)
        for field in ("task_selected_action_created", "final_action_created", "direct_command_created", "sandbox_execution_created", "task_action_selection_created")
    )


def _external_forbidden(item: object) -> bool:
    return any(
        getattr(item, field, False)
        for field in (
            "external_control_created",
            "os_control_created",
            "mouse_control_created",
            "keyboard_control_created",
            "browser_control_created",
            "file_operation_created",
            "network_execution_created",
            "shell_execution_created",
            "external_api_call_created",
            "actual_screen_mutated",
            "actual_sound_played",
            "unity_runtime_mutated",
            "avatar_control_created",
            "actual_status_light_mutated",
            "actual_home_surface_mutated",
            "actual_unity_runtime_mutated",
            "external_message_created",
            "file_written",
            "network_output_created",
        )
    )


def _memory_forbidden(item: object) -> bool:
    return any(
        getattr(item, field, False)
        for field in (
            "memory_layer_write_performed",
            "memory_write_performed",
            "learning_candidate_created",
            "automatic_learning_approval_created",
            "teacher_approval_created",
            "learning_approval_created",
            "memory_write_approval_created",
        )
    )


def _source_refs(*items: object | None) -> tuple[str, ...]:
    refs: list[str] = []
    for item in items:
        if item is not None:
            refs.extend(getattr(item, "source_trace_refs", tuple()))
    return tuple(dict.fromkeys(refs))


def _plan_summary(status: str) -> str:
    if status == "internal_action_choice_plan_created":
        return "Internal-only deterministic Host Body action choice plan created."
    return f"Internal action choice plan blocked: {status}."


def _candidate_summary(status: str, kind: str) -> str:
    if status.startswith("internal_action_candidate_created"):
        return f"Internal-only action candidate recorded: {kind}."
    return f"Internal action candidate blocked: {status}."


def _choice_reason(status: str, selected: HostBodyInternalActionCandidateRecord | None) -> str:
    if selected is None:
        return status
    return f"selected {selected.candidate_action_kind} from deterministic priority rule"


def _choice_summary(status: str, selected: HostBodyInternalActionCandidateRecord | None) -> str:
    if status == "internal_action_choice_selected" and selected is not None:
        return f"Internal-only action choice selected {selected.candidate_action_kind}."
    return f"Internal action choice status: {status}."


def _result_summary(status: str, kind: str | None) -> str:
    if status.startswith("internal_action_result_recorded"):
        return f"Internal-only action result recorded for {kind}."
    return f"Internal action result blocked: {status}."


def _surface_effect_summary(status: str, kind: str) -> str:
    if status.startswith("surface_effect_recorded") or status == "surface_effect_none":
        return f"Read-only surface effect record created: {kind}."
    return f"Surface effect blocked: {status}."


def _choice_set_summary(status: str) -> str:
    if status.startswith("internal_action_choice_set_recorded"):
        return "Internal-only action choice set recorded."
    return f"Internal action choice set blocked: {status}."


def _readiness_summary(status: str) -> str:
    if status.startswith("ready_for_"):
        return "Host Body internal action choice is ready for the next milestone audit package."
    return f"Host Body internal action choice readiness blocked: {status}."


def _trace_audit(record: HostBodyTraceHistoryAudit | dict[str, object]) -> HostBodyTraceHistoryAudit:
    return record if isinstance(record, HostBodyTraceHistoryAudit) else HostBodyTraceHistoryAudit.from_dict(record)


def _trace_readback(record: HostBodyTraceHistoryReadbackRecord | dict[str, object]) -> HostBodyTraceHistoryReadbackRecord:
    return record if isinstance(record, HostBodyTraceHistoryReadbackRecord) else HostBodyTraceHistoryReadbackRecord.from_dict(record)


def _trace_entry(record: HostBodyTraceHistoryEntryRecord | dict[str, object]) -> HostBodyTraceHistoryEntryRecord:
    return record if isinstance(record, HostBodyTraceHistoryEntryRecord) else HostBodyTraceHistoryEntryRecord.from_dict(record)


def _home_audit(record: QingyinHomeInternalSpaceSurfaceAudit | dict[str, object]) -> QingyinHomeInternalSpaceSurfaceAudit:
    return record if isinstance(record, QingyinHomeInternalSpaceSurfaceAudit) else QingyinHomeInternalSpaceSurfaceAudit.from_dict(record)


def _status_light(record: QingyinHomeStatusLightRecord | dict[str, object]) -> QingyinHomeStatusLightRecord:
    return record if isinstance(record, QingyinHomeStatusLightRecord) else QingyinHomeStatusLightRecord.from_dict(record)


def _bridge_trace(record: HostBodyRuntimeBridgeTraceRecord | dict[str, object]) -> HostBodyRuntimeBridgeTraceRecord:
    return record if isinstance(record, HostBodyRuntimeBridgeTraceRecord) else HostBodyRuntimeBridgeTraceRecord.from_dict(record)


def _plan(record: HostBodyInternalActionChoicePlanRecord | dict[str, object]) -> HostBodyInternalActionChoicePlanRecord:
    return record if isinstance(record, HostBodyInternalActionChoicePlanRecord) else HostBodyInternalActionChoicePlanRecord.from_dict(record)


def _candidate(record: HostBodyInternalActionCandidateRecord | dict[str, object]) -> HostBodyInternalActionCandidateRecord:
    return record if isinstance(record, HostBodyInternalActionCandidateRecord) else HostBodyInternalActionCandidateRecord.from_dict(record)


def _choice(record: HostBodyInternalActionChoiceRecord | dict[str, object]) -> HostBodyInternalActionChoiceRecord:
    return record if isinstance(record, HostBodyInternalActionChoiceRecord) else HostBodyInternalActionChoiceRecord.from_dict(record)


def _result(record: HostBodyInternalActionResultRecord | dict[str, object]) -> HostBodyInternalActionResultRecord:
    return record if isinstance(record, HostBodyInternalActionResultRecord) else HostBodyInternalActionResultRecord.from_dict(record)


def _surface_effect(record: HostBodyInternalActionSurfaceEffectRecord | dict[str, object]) -> HostBodyInternalActionSurfaceEffectRecord:
    return record if isinstance(record, HostBodyInternalActionSurfaceEffectRecord) else HostBodyInternalActionSurfaceEffectRecord.from_dict(record)


def _choice_set(record: HostBodyInternalActionChoiceSetRecord | dict[str, object]) -> HostBodyInternalActionChoiceSetRecord:
    return record if isinstance(record, HostBodyInternalActionChoiceSetRecord) else HostBodyInternalActionChoiceSetRecord.from_dict(record)


def _audit(record: HostBodyInternalActionChoiceAudit | dict[str, object]) -> HostBodyInternalActionChoiceAudit:
    return record if isinstance(record, HostBodyInternalActionChoiceAudit) else HostBodyInternalActionChoiceAudit.from_dict(record)


def _readiness(record: HostBodyInternalActionChoiceReadinessRecord | dict[str, object]) -> HostBodyInternalActionChoiceReadinessRecord:
    return record if isinstance(record, HostBodyInternalActionChoiceReadinessRecord) else HostBodyInternalActionChoiceReadinessRecord.from_dict(record)
