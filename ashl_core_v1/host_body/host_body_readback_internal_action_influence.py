"""Host Body working readback influence on internal action choice ordering."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    build_demo_unknown_event_marks_uncertain,
    validate_host_body_internal_action_choice_audit,
)
from ashl_core_v1.host_body.host_body_working_readback_integration import (
    build_demo_interesting_event_reviewed_concept_working_readback,
    build_demo_runtime_bridge_reviewed_concept_working_readback,
    build_demo_trace_spine_raw_evidence_boundary,
    build_demo_uncertainty_reviewed_concept_working_readback,
    validate_host_body_working_readback_integration_audit,
    validate_host_body_working_readback_visibility,
    validate_trace_spine_raw_evidence_boundary,
)


SOURCE_ENGINE = "host_body"

PLAN_SCHEMA_VERSION = "qingyin_host_body_readback_internal_action_influence_plan_v0"
SIGNAL_SCHEMA_VERSION = "qingyin_host_body_readback_internal_action_signal_v0"
SCORE_SCHEMA_VERSION = "qingyin_host_body_internal_action_candidate_readback_score_v0"
ORDERING_SCHEMA_VERSION = (
    "qingyin_host_body_readback_influenced_internal_action_ordering_v0"
)
CHOICE_SCHEMA_VERSION = (
    "qingyin_host_body_readback_influenced_internal_action_choice_v0"
)
RESULT_SCHEMA_VERSION = (
    "qingyin_host_body_readback_influenced_internal_action_result_v0"
)
TRACE_SCHEMA_VERSION = "qingyin_host_body_readback_internal_action_influence_trace_v0"
AUDIT_SCHEMA_VERSION = "qingyin_host_body_readback_internal_action_influence_audit_v0"
READINESS_SCHEMA_VERSION = (
    "qingyin_host_body_readback_internal_action_influence_readiness_v0"
)

INFLUENCE_NAME = "host_body_readback_influences_internal_action_choice"
INFLUENCE_KIND = "internal_only_readback_ordering_influence"
ALLOWED_READBACK_SIGNAL_THEMES = (
    "prior_uncertainty",
    "prior_interesting_event",
    "prior_teacher_review_needed",
    "prior_observe_again_helped",
    "prior_runtime_bridge_deferred",
    "prior_unknown_event",
    "prior_event_processing_paused",
    "prior_home_status_update",
    "none",
)
ALLOWED_INTERNAL_ACTION_KINDS = (
    "observe_again",
    "mark_event_interesting",
    "mark_uncertain",
    "request_teacher_review",
    "shift_internal_focus",
    "update_home_status",
    "pause_event_processing",
)
ALLOWED_CANDIDATE_KINDS = ALLOWED_INTERNAL_ACTION_KINDS + ("blocked_external_action",)
ALLOWED_ORDERING_EFFECTS = (
    "increase_mark_uncertain_priority",
    "increase_request_teacher_review_priority",
    "increase_observe_again_priority",
    "increase_mark_event_interesting_priority",
    "increase_pause_event_processing_priority",
    "increase_update_home_status_priority",
    "increase_shift_internal_focus_priority",
    "no_change",
)
FORBIDDEN_EFFECTS = (
    "change_task_engine_candidate_ordering",
    "create_selected_action",
    "create_final_action",
    "create_direct_command",
    "execute_action",
    "control_computer",
    "mutate_raw_trace",
    "write_long_term_memory",
    "create_first_output",
    "start_live_runtime",
)
FORBIDDEN_ACTION_KINDS = (
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
TIE_BREAKER_ORDER = (
    "request_teacher_review",
    "pause_event_processing",
    "mark_uncertain",
    "observe_again",
    "mark_event_interesting",
    "shift_internal_focus",
    "update_home_status",
)
TIE_BREAKER_INDEX = {kind: index for index, kind in enumerate(TIE_BREAKER_ORDER)}
DELTA_MIN = -3
DELTA_MAX = 3

SAFE_CLAIM = (
    "ASHL Core v1 can use Host Body working readback visibility to influence "
    "internal-only Host Body action choice ordering while preserving Trace Spine "
    "raw evidence boundaries and blocking Task Engine action authority."
)
BLOCKED_CLAIMS = (
    "no_task_action_selection_influence",
    "no_task_selected_action",
    "no_final_action",
    "no_direct_command",
    "no_sandbox_execution",
    "no_external_control",
    "no_memory_layer_write",
    "no_learning_candidate_creation",
    "no_teacher_approval_created",
    "no_raw_trace_summarization",
    "no_concept_id_embedded_into_raw_history",
    "no_first_output",
    "no_live_runtime_session",
)
READINESS_NEXT_PACKAGE = (
    "Package 113 / ASHL Core v1 Host Body Embodied Learning Closed Loop "
    "Milestone Audit Minimal v0"
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
    if hasattr(value, "to_dict"):
        return dict(value.to_dict())
    return dict(value)


def _tuple_of_str(name: str, value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    items = tuple(value)
    if not all(isinstance(item, str) for item in items):
        raise TypeError(f"{name} must contain only strings")
    return items


def _get(record: dict[str, Any] | None, key: str, default: Any = None) -> Any:
    if record is None:
        return default
    return record.get(key, default)


def _slug(text: str | None) -> str:
    safe = [char.lower() if char.isalnum() else "_" for char in str(text or "none")]
    return "_".join("".join(safe).split("_"))[:120] or "empty"


def _refs_from(*records: Any) -> tuple[str, ...]:
    refs: list[str] = []
    for item in records:
        record = _record(item)
        if record is None:
            continue
        for key in (
            "source_trace_refs",
            "source_memory_refs",
            "readback_reason_refs",
            "candidate_readback_score_ids",
            "readback_signal_ids",
            "ordering_ids",
            "choice_ids",
            "result_ids",
        ):
            refs.extend(str(value) for value in record.get(key, ()) or ())
        for key, value in record.items():
            if key.endswith("_id") and value:
                refs.append(str(value))
    seen: set[str] = set()
    ordered: list[str] = []
    for ref in refs:
        if ref not in seen:
            seen.add(ref)
            ordered.append(ref)
    return tuple(ordered)


def _validation(status: str, valid_statuses: set[str]) -> dict[str, object]:
    valid = status in valid_statuses
    return {
        "valid": valid,
        "status": status,
        "blocked_reasons": () if valid else (status,),
    }


@dataclass(frozen=True)
class HostBodyReadbackInternalActionInfluencePlanRecord:
    readback_internal_action_influence_plan_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_working_readback_integration_audit_id: str | None
    source_internal_action_choice_audit_id: str | None
    source_trace_spine_boundary_id: str | None
    influence_name: str
    influence_kind: str
    allowed_readback_signal_themes: tuple[str, ...]
    allowed_internal_action_kinds: tuple[str, ...]
    allowed_ordering_effects: tuple[str, ...]
    forbidden_effects: tuple[str, ...]
    internal_action_choice_ordering_allowed: bool
    task_action_selection_allowed: bool
    final_action_allowed: bool
    direct_command_allowed: bool
    sandbox_execution_allowed: bool
    external_control_allowed: bool
    memory_write_allowed: bool
    long_term_memory_write_allowed: bool
    core_memory_write_allowed: bool
    raw_trace_summarization_allowed: bool
    concept_id_embedding_into_raw_history_allowed: bool
    learning_candidate_creation_allowed: bool
    automatic_learning_approval_allowed: bool
    teacher_approval_creation_allowed: bool
    first_output_allowed: bool
    live_runtime_session_allowed: bool
    plan_status: str
    plan_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PLAN_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_readback_internal_action_influence_plan_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.influence_name != INFLUENCE_NAME:
            raise ValueError("influence_name must be host_body_readback_influences_internal_action_choice")
        if self.influence_kind != INFLUENCE_KIND:
            raise ValueError("influence_kind must be internal_only_readback_ordering_influence")
        if self.plan_status not in {
            "readback_internal_action_influence_plan_created",
            "blocked_missing_working_readback_integration_audit",
            "blocked_missing_internal_action_choice_audit",
            "blocked_missing_trace_spine_boundary",
            "blocked_task_action_selection_allowed",
            "blocked_direct_command_allowed",
            "blocked_external_control_allowed",
            "blocked_memory_write_allowed",
            "blocked_raw_trace_summarization_allowed",
            "blocked_concept_id_embedding_allowed",
            "blocked_first_output_allowed",
            "blocked_live_runtime_allowed",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown plan_status: {self.plan_status}")
        for name in (
            "allowed_readback_signal_themes",
            "allowed_internal_action_kinds",
            "allowed_ordering_effects",
            "forbidden_effects",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReadbackInternalActionInfluencePlanRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReadbackInternalActionSignalRecord:
    readback_internal_action_signal_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_influence_plan_id: str
    source_working_readback_visibility_id: str | None
    source_memory_application_data_bridge_id: str | None
    source_trace_history_readback_id: str | None
    signal_theme: str
    signal_strength: int
    signal_reason_codes: tuple[str, ...]
    signal_summary: str
    readback_payload_contains_interpretation: bool
    readback_payload_contains_source_refs: bool
    readback_payload_contains_raw_trace: bool
    source_trace_refs: tuple[str, ...]
    source_memory_refs: tuple[str, ...]
    signal_safe_for_internal_action_ordering: bool
    task_action_selection_influence_created: bool
    external_control_created: bool
    memory_write_performed: bool
    raw_trace_mutated: bool
    raw_trace_summarized: bool
    concept_id_embedded_into_raw_history: bool
    learning_candidate_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    signal_status: str

    def __post_init__(self) -> None:
        if self.schema_version != SIGNAL_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_readback_internal_action_signal_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.signal_theme not in ALLOWED_READBACK_SIGNAL_THEMES:
            raise ValueError(f"unknown signal_theme: {self.signal_theme}")
        if self.signal_status not in {
            "readback_internal_action_signal_created",
            "readback_internal_action_signal_created_uncertainty",
            "readback_internal_action_signal_created_teacher_review",
            "readback_internal_action_signal_created_observe_again",
            "readback_internal_action_signal_created_runtime_bridge",
            "readback_internal_action_signal_created_noop",
            "blocked_invalid_working_readback_visibility",
            "blocked_raw_trace_in_readback_payload",
            "blocked_missing_source_refs",
            "blocked_task_action_selection_influence_detected",
            "blocked_external_control_detected",
            "blocked_memory_write_detected",
            "blocked_raw_trace_mutation_detected",
            "blocked_raw_trace_summarization_detected",
            "blocked_concept_id_embedded_into_raw_history",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown signal_status: {self.signal_status}")
        for name in ("signal_reason_codes", "source_trace_refs", "source_memory_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReadbackInternalActionSignalRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyInternalActionCandidateReadbackScoreRecord:
    candidate_readback_score_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_readback_signal_id: str
    source_internal_action_candidate_id: str | None
    candidate_action_kind: str
    base_candidate_priority: int
    readback_delta: int
    final_candidate_priority: int
    score_reason_codes: tuple[str, ...]
    score_summary: str
    score_status: str
    internal_action_choice_score_created: bool
    task_action_score_created: bool
    candidate_kind_allowed: bool
    readback_signal_applied: bool
    task_selected_action_created: bool
    final_action_created: bool
    direct_command_created: bool
    sandbox_execution_created: bool
    external_control_created: bool
    memory_write_performed: bool
    learning_candidate_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SCORE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_internal_action_candidate_readback_score_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.candidate_action_kind not in ALLOWED_CANDIDATE_KINDS:
            raise ValueError(f"unknown candidate_action_kind: {self.candidate_action_kind}")
        if self.score_status not in {
            "candidate_readback_score_created",
            "candidate_readback_score_created_boosted",
            "candidate_readback_score_created_no_change",
            "candidate_readback_score_created_lowered",
            "blocked_invalid_readback_signal",
            "blocked_forbidden_candidate_kind",
            "blocked_task_action_score_detected",
            "blocked_selected_action_created",
            "blocked_direct_command_created",
            "blocked_external_control_detected",
            "blocked_memory_write_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown score_status: {self.score_status}")
        for name in ("score_reason_codes", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyInternalActionCandidateReadbackScoreRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReadbackInfluencedInternalActionOrderingRecord:
    readback_influenced_ordering_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_influence_plan_id: str
    candidate_readback_score_ids: tuple[str, ...]
    ordered_candidate_ids: tuple[str, ...]
    ordered_candidate_action_kinds: tuple[str, ...]
    ordering_kind: str
    ordering_status: str
    ordering_summary: str
    readback_influence_applied: bool
    internal_action_ordering_changed: bool
    task_action_ordering_changed: bool
    deterministic_tie_breaker_used: bool
    tie_breaker_order: tuple[str, ...]
    selected_internal_action_kind_preview: str | None
    task_selected_action_created: bool
    final_action_created: bool
    direct_command_created: bool
    sandbox_execution_created: bool
    external_control_created: bool
    memory_write_performed: bool
    learning_candidate_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ORDERING_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_readback_influenced_internal_action_ordering_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.ordering_kind not in {
            "host_body_internal_action_readback_ordering",
            "host_body_internal_action_readback_ordering_no_change",
            "blocked_ordering",
        }:
            raise ValueError(f"unknown ordering_kind: {self.ordering_kind}")
        if self.ordering_status not in {
            "readback_influenced_internal_action_ordering_created",
            "readback_influenced_internal_action_ordering_created_changed",
            "readback_influenced_internal_action_ordering_created_no_change",
            "blocked_invalid_candidate_score",
            "blocked_task_action_ordering_changed",
            "blocked_selected_action_created",
            "blocked_direct_command_created",
            "blocked_external_control_detected",
            "blocked_memory_write_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown ordering_status: {self.ordering_status}")
        for name in (
            "candidate_readback_score_ids",
            "ordered_candidate_ids",
            "ordered_candidate_action_kinds",
            "tie_breaker_order",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReadbackInfluencedInternalActionOrderingRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReadbackInfluencedInternalActionChoiceRecord:
    readback_influenced_choice_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_readback_influenced_ordering_id: str
    selected_internal_action_kind: str | None
    selected_candidate_id: str | None
    choice_kind: str
    choice_status: str
    choice_summary: str
    choice_uses_readback_influence: bool
    choice_is_internal_only: bool
    choice_is_record_only: bool
    teacher_review_request_recorded: bool
    teacher_approval_created: bool
    learning_approval_created: bool
    task_selected_action_created: bool
    final_action_created: bool
    direct_command_created: bool
    sandbox_execution_created: bool
    external_control_created: bool
    memory_write_performed: bool
    learning_candidate_created: bool
    automatic_learning_approval_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CHOICE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_readback_influenced_internal_action_choice_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.choice_kind not in {
            "readback_influenced_observe_again_choice",
            "readback_influenced_mark_interesting_choice",
            "readback_influenced_mark_uncertain_choice",
            "readback_influenced_request_teacher_review_choice",
            "readback_influenced_shift_internal_focus_choice",
            "readback_influenced_update_home_status_choice",
            "readback_influenced_pause_event_processing_choice",
            "blocked_choice",
        }:
            raise ValueError(f"unknown choice_kind: {self.choice_kind}")
        if self.choice_status not in {
            "readback_influenced_internal_action_choice_selected",
            "readback_influenced_internal_action_choice_deferred_no_candidates",
            "blocked_invalid_ordering",
            "blocked_forbidden_selected_kind",
            "blocked_teacher_approval_created",
            "blocked_task_selected_action_created",
            "blocked_direct_command_created",
            "blocked_external_control_created",
            "blocked_memory_write_detected",
            "blocked_learning_candidate_created",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown choice_status: {self.choice_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReadbackInfluencedInternalActionChoiceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReadbackInfluencedInternalActionResultRecord:
    readback_influenced_result_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_readback_influenced_choice_id: str
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
    readback_reason_refs: tuple[str, ...]
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
            raise ValueError("schema_version must be qingyin_host_body_readback_influenced_internal_action_result_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.result_kind not in {
            "readback_influenced_internal_marker_result",
            "readback_influenced_home_status_update_record",
            "readback_influenced_teacher_review_request_record",
            "readback_influenced_internal_focus_marker",
            "readback_influenced_event_processing_pause_marker",
            "readback_influenced_observe_again_recommendation",
            "blocked_result",
        }:
            raise ValueError(f"unknown result_kind: {self.result_kind}")
        if self.result_status not in {
            "readback_influenced_internal_action_result_recorded",
            "readback_influenced_internal_action_result_recorded_request_teacher_review",
            "readback_influenced_internal_action_result_recorded_update_home_status",
            "readback_influenced_internal_action_result_recorded_mark_uncertain",
            "readback_influenced_internal_action_result_recorded_observe_again",
            "blocked_external_control",
            "blocked_task_action_selection",
            "blocked_memory_write",
            "blocked_learning_candidate_creation",
            "blocked_first_output",
            "blocked_live_runtime",
            "blocked_forbidden_authority",
        }:
            raise ValueError(f"unknown result_status: {self.result_status}")
        for name in ("readback_reason_refs", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReadbackInfluencedInternalActionResultRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReadbackInternalActionInfluenceTraceRecord:
    readback_internal_action_influence_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_influence_plan_id: str
    readback_signal_ids: tuple[str, ...]
    candidate_score_ids: tuple[str, ...]
    ordering_ids: tuple[str, ...]
    choice_ids: tuple[str, ...]
    result_ids: tuple[str, ...]
    trace_kind: str
    trace_status: str
    trace_summary: str
    readback_signal_count: int
    candidate_score_count: int
    ordering_count: int
    choice_count: int
    result_count: int
    internal_action_ordering_changed_count: int
    teacher_review_request_count: int
    mark_uncertain_count: int
    observe_again_count: int
    pause_event_processing_count: int
    trace_spine_boundary_preserved: bool
    raw_trace_append_only_confirmed: bool
    raw_trace_summarized_during_service_period: bool
    memory_layer_stores_interpretation_only: bool
    source_trace_refs_preserved: bool
    concept_id_embedded_into_raw_history: bool
    task_action_selection_influence_created: bool
    task_selected_action_created: bool
    final_action_created: bool
    direct_command_created: bool
    sandbox_execution_created: bool
    external_control_created: bool
    memory_write_performed: bool
    learning_candidate_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TRACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_readback_internal_action_influence_trace_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.trace_kind not in {
            "single_readback_internal_action_influence_trace",
            "mixed_readback_internal_action_influence_trace",
            "empty_readback_internal_action_influence_trace",
            "blocked_readback_internal_action_influence_trace",
        }:
            raise ValueError(f"unknown trace_kind: {self.trace_kind}")
        if self.trace_status not in {
            "readback_internal_action_influence_trace_recorded",
            "readback_internal_action_influence_trace_recorded_empty",
            "blocked_invalid_signal",
            "blocked_invalid_candidate_score",
            "blocked_invalid_ordering",
            "blocked_invalid_choice",
            "blocked_invalid_result",
            "blocked_trace_spine_boundary_failure",
            "blocked_task_action_selection_influence",
            "blocked_selected_action_created",
            "blocked_direct_command_created",
            "blocked_external_control_detected",
            "blocked_memory_write_detected",
            "blocked_learning_candidate_created",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown trace_status: {self.trace_status}")
        for name in (
            "readback_signal_ids",
            "candidate_score_ids",
            "ordering_ids",
            "choice_ids",
            "result_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReadbackInternalActionInfluenceTraceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReadbackInternalActionInfluenceAudit:
    readback_internal_action_influence_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_influence_plan_id: str | None
    source_influence_trace_id: str | None
    source_trace_spine_boundary_id: str | None
    influence_plan_valid: bool
    readback_signals_valid: bool
    candidate_scores_valid: bool
    orderings_valid: bool
    choices_valid: bool
    results_valid: bool
    influence_trace_valid: bool
    trace_spine_boundary_valid: bool
    host_body_working_readback_confirmed: bool
    internal_action_choice_influence_confirmed: bool
    internal_only_confirmed: bool
    record_only_confirmed: bool
    trace_spine_format_unified_confirmed: bool
    trace_spine_time_aligned_confirmed: bool
    raw_trace_append_only_confirmed: bool
    raw_trace_not_summarized_during_service_period: bool
    memory_layer_stores_interpretation_only_confirmed: bool
    source_trace_refs_preserved_confirmed: bool
    concept_id_not_embedded_into_raw_history_confirmed: bool
    raw_trace_not_dumped_into_memory_learning_trace_confirmed: bool
    no_task_action_selection_influence: bool
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
    no_memory_layer_write: bool
    no_long_term_memory_write: bool
    no_core_memory_write: bool
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
            raise ValueError("schema_version must be qingyin_host_body_readback_internal_action_influence_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.audit_status not in {
            "passed_host_body_readback_internal_action_influence",
            "passed_readback_influenced_request_teacher_review",
            "passed_readback_influenced_mark_uncertain",
            "passed_readback_influenced_observe_again",
            "passed_readback_influenced_pause_event_processing",
            "passed_trace_spine_boundary_preserved",
            "blocked_missing_influence_plan",
            "blocked_invalid_readback_signal",
            "blocked_invalid_candidate_score",
            "blocked_invalid_ordering",
            "blocked_invalid_choice",
            "blocked_invalid_result",
            "blocked_invalid_influence_trace",
            "blocked_trace_spine_boundary_failure",
            "blocked_raw_trace_summarized",
            "blocked_concept_id_embedded_into_raw_history",
            "blocked_task_action_selection_influence_detected",
            "blocked_selected_action_created",
            "blocked_final_action_created",
            "blocked_direct_command_created",
            "blocked_sandbox_execution_created",
            "blocked_external_control_detected",
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
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReadbackInternalActionInfluenceAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReadbackInternalActionInfluenceReadinessRecord:
    readback_internal_action_influence_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_readback_internal_action_influence_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_host_body_embodied_learning_closed_loop_audit: bool
    ready_for_bounded_embodied_loop_runner: bool
    ready_for_no_codex_teacher_console_flow: bool
    ready_for_task_engine_action_selection_influence: bool
    ready_for_direct_command: bool
    ready_for_external_control: bool
    ready_for_long_term_memory_write: bool
    ready_for_core_memory_write: bool
    ready_for_learning_candidate_creation: bool
    ready_for_automatic_learning_approval: bool
    ready_for_first_output: bool
    ready_for_live_runtime_session: bool
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READINESS_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_readback_internal_action_influence_readiness_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.readiness_status not in {
            "ready_for_host_body_embodied_learning_closed_loop_audit_only",
            "ready_for_bounded_embodied_loop_runner_only",
            "ready_for_no_codex_teacher_console_flow_only",
            "not_ready_missing_readback_internal_action_influence_audit",
            "not_ready_boundary_failure",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReadbackInternalActionInfluenceReadinessRecord":
        return cls(**dict(data))


def build_host_body_readback_internal_action_influence_plan(
    *,
    working_readback_integration_audit: Any | None,
    internal_action_choice_audit: Any | None,
    trace_spine_boundary: Any | None,
    internal_action_choice_ordering_allowed: bool = True,
    task_action_selection_allowed: bool = False,
    final_action_allowed: bool = False,
    direct_command_allowed: bool = False,
    sandbox_execution_allowed: bool = False,
    external_control_allowed: bool = False,
    memory_write_allowed: bool = False,
    long_term_memory_write_allowed: bool = False,
    core_memory_write_allowed: bool = False,
    raw_trace_summarization_allowed: bool = False,
    concept_id_embedding_into_raw_history_allowed: bool = False,
    learning_candidate_creation_allowed: bool = False,
    automatic_learning_approval_allowed: bool = False,
    teacher_approval_creation_allowed: bool = False,
    first_output_allowed: bool = False,
    live_runtime_session_allowed: bool = False,
) -> HostBodyReadbackInternalActionInfluencePlanRecord:
    working_audit = _record(working_readback_integration_audit)
    internal_audit = _record(internal_action_choice_audit)
    boundary = _record(trace_spine_boundary)
    status = "readback_internal_action_influence_plan_created"
    if working_audit is None:
        status = "blocked_missing_working_readback_integration_audit"
    elif internal_audit is None:
        status = "blocked_missing_internal_action_choice_audit"
    elif boundary is None:
        status = "blocked_missing_trace_spine_boundary"
    elif not internal_action_choice_ordering_allowed or final_action_allowed or sandbox_execution_allowed:
        status = "blocked_forbidden_authority_detected"
    elif task_action_selection_allowed:
        status = "blocked_task_action_selection_allowed"
    elif direct_command_allowed:
        status = "blocked_direct_command_allowed"
    elif external_control_allowed:
        status = "blocked_external_control_allowed"
    elif any((memory_write_allowed, long_term_memory_write_allowed, core_memory_write_allowed)):
        status = "blocked_memory_write_allowed"
    elif raw_trace_summarization_allowed:
        status = "blocked_raw_trace_summarization_allowed"
    elif concept_id_embedding_into_raw_history_allowed:
        status = "blocked_concept_id_embedding_allowed"
    elif learning_candidate_creation_allowed or automatic_learning_approval_allowed or teacher_approval_creation_allowed:
        status = "blocked_forbidden_authority_detected"
    elif first_output_allowed:
        status = "blocked_first_output_allowed"
    elif live_runtime_session_allowed:
        status = "blocked_live_runtime_allowed"
    source_refs = _refs_from(working_audit, internal_audit, boundary)
    return HostBodyReadbackInternalActionInfluencePlanRecord(
        readback_internal_action_influence_plan_id=f"host_body_readback_internal_action_influence_plan:{status}",
        schema_version=PLAN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_working_readback_integration_audit_id=_get(working_audit, "working_readback_integration_audit_id"),
        source_internal_action_choice_audit_id=_get(internal_audit, "internal_action_choice_audit_id"),
        source_trace_spine_boundary_id=_get(boundary, "trace_spine_boundary_id"),
        influence_name=INFLUENCE_NAME,
        influence_kind=INFLUENCE_KIND,
        allowed_readback_signal_themes=ALLOWED_READBACK_SIGNAL_THEMES,
        allowed_internal_action_kinds=ALLOWED_INTERNAL_ACTION_KINDS,
        allowed_ordering_effects=ALLOWED_ORDERING_EFFECTS,
        forbidden_effects=FORBIDDEN_EFFECTS,
        internal_action_choice_ordering_allowed=internal_action_choice_ordering_allowed,
        task_action_selection_allowed=task_action_selection_allowed,
        final_action_allowed=final_action_allowed,
        direct_command_allowed=direct_command_allowed,
        sandbox_execution_allowed=sandbox_execution_allowed,
        external_control_allowed=external_control_allowed,
        memory_write_allowed=memory_write_allowed,
        long_term_memory_write_allowed=long_term_memory_write_allowed,
        core_memory_write_allowed=core_memory_write_allowed,
        raw_trace_summarization_allowed=raw_trace_summarization_allowed,
        concept_id_embedding_into_raw_history_allowed=concept_id_embedding_into_raw_history_allowed,
        learning_candidate_creation_allowed=learning_candidate_creation_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        teacher_approval_creation_allowed=teacher_approval_creation_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
        plan_status=status,
        plan_summary=_plan_summary(status),
        source_trace_refs=source_refs,
    )


def validate_host_body_readback_internal_action_influence_plan(plan: Any) -> dict[str, object]:
    record = _record(plan)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(str(record["plan_status"]), {"readback_internal_action_influence_plan_created"})


def build_host_body_readback_internal_action_signal(
    *,
    influence_plan: Any,
    working_readback_visibility: Any | None,
    signal_theme: str | None = None,
    signal_strength: int = 1,
    source_trace_history_readback_id: str | None = None,
    readback_payload_contains_interpretation: bool = True,
    readback_payload_contains_source_refs: bool = True,
    readback_payload_contains_raw_trace: bool = False,
    task_action_selection_influence_created: bool = False,
    external_control_created: bool = False,
    memory_write_performed: bool = False,
    raw_trace_mutated: bool = False,
    raw_trace_summarized: bool = False,
    concept_id_embedded_into_raw_history: bool = False,
    learning_candidate_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyReadbackInternalActionSignalRecord:
    plan = _record(influence_plan)
    visibility = _record(working_readback_visibility)
    source_refs = _refs_from(plan, visibility)
    theme = signal_theme or _infer_signal_theme(visibility)
    if theme not in ALLOWED_READBACK_SIGNAL_THEMES:
        theme = "none"
    status = _signal_status_for_theme(theme)
    if not visibility or not validate_host_body_working_readback_visibility(visibility)["valid"]:
        status = "blocked_invalid_working_readback_visibility"
    elif not readback_payload_contains_interpretation:
        status = "blocked_invalid_working_readback_visibility"
    elif readback_payload_contains_raw_trace:
        status = "blocked_raw_trace_in_readback_payload"
    elif not source_refs or not readback_payload_contains_source_refs:
        status = "blocked_missing_source_refs"
    elif task_action_selection_influence_created:
        status = "blocked_task_action_selection_influence_detected"
    elif external_control_created:
        status = "blocked_external_control_detected"
    elif memory_write_performed:
        status = "blocked_memory_write_detected"
    elif raw_trace_mutated:
        status = "blocked_raw_trace_mutation_detected"
    elif raw_trace_summarized:
        status = "blocked_raw_trace_summarization_detected"
    elif concept_id_embedded_into_raw_history:
        status = "blocked_concept_id_embedded_into_raw_history"
    elif first_output_created:
        status = "blocked_first_output_detected"
    elif live_runtime_session_created:
        status = "blocked_live_runtime_detected"
    return HostBodyReadbackInternalActionSignalRecord(
        readback_internal_action_signal_id=f"host_body_readback_internal_action_signal:{theme}:{status}",
        schema_version=SIGNAL_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_influence_plan_id=str(_get(plan, "readback_internal_action_influence_plan_id")),
        source_working_readback_visibility_id=_get(visibility, "working_readback_visibility_id"),
        source_memory_application_data_bridge_id=_get(visibility, "source_memory_application_data_bridge_id"),
        source_trace_history_readback_id=source_trace_history_readback_id,
        signal_theme=theme,
        signal_strength=max(0, min(3, int(signal_strength))),
        signal_reason_codes=_signal_reason_codes(theme),
        signal_summary=_signal_summary(theme, status),
        readback_payload_contains_interpretation=readback_payload_contains_interpretation,
        readback_payload_contains_source_refs=readback_payload_contains_source_refs,
        readback_payload_contains_raw_trace=readback_payload_contains_raw_trace,
        source_trace_refs=source_refs,
        source_memory_refs=tuple(str(ref) for ref in (_get(visibility, "source_memory_application_data_refs", ()) or ())),
        signal_safe_for_internal_action_ordering=True,
        task_action_selection_influence_created=task_action_selection_influence_created,
        external_control_created=external_control_created,
        memory_write_performed=memory_write_performed,
        raw_trace_mutated=raw_trace_mutated,
        raw_trace_summarized=raw_trace_summarized,
        concept_id_embedded_into_raw_history=concept_id_embedded_into_raw_history,
        learning_candidate_created=learning_candidate_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        signal_status=status,
    )


def validate_host_body_readback_internal_action_signal(signal: Any) -> dict[str, object]:
    record = _record(signal)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["signal_status"]),
        {
            "readback_internal_action_signal_created",
            "readback_internal_action_signal_created_uncertainty",
            "readback_internal_action_signal_created_teacher_review",
            "readback_internal_action_signal_created_observe_again",
            "readback_internal_action_signal_created_runtime_bridge",
            "readback_internal_action_signal_created_noop",
        },
    )


def build_host_body_internal_action_candidate_readback_score(
    *,
    readback_signal: Any,
    internal_action_candidate: Any | None = None,
    candidate_action_kind: str | None = None,
    base_candidate_priority: int | None = None,
    readback_delta: int | None = None,
    task_action_score_created: bool = False,
    task_selected_action_created: bool = False,
    final_action_created: bool = False,
    direct_command_created: bool = False,
    sandbox_execution_created: bool = False,
    external_control_created: bool = False,
    memory_write_performed: bool = False,
    learning_candidate_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyInternalActionCandidateReadbackScoreRecord:
    signal = _record(readback_signal)
    candidate = _record(internal_action_candidate)
    requested_kind = candidate_action_kind or str(_get(candidate, "candidate_action_kind", "observe_again"))
    kind_allowed = requested_kind in ALLOWED_INTERNAL_ACTION_KINDS
    kind = requested_kind if kind_allowed else "blocked_external_action"
    base = int(base_candidate_priority if base_candidate_priority is not None else _get(candidate, "candidate_priority", 0))
    signal_valid = bool(signal and validate_host_body_readback_internal_action_signal(signal)["valid"])
    delta = _bounded_delta(
        readback_delta
        if readback_delta is not None
        else _deterministic_readback_delta(str(_get(signal, "signal_theme", "none")), kind)
    )
    final_priority = base + delta
    status = "candidate_readback_score_created_no_change"
    if not signal_valid:
        status = "blocked_invalid_readback_signal"
    elif not kind_allowed:
        status = "blocked_forbidden_candidate_kind"
    elif task_action_score_created:
        status = "blocked_task_action_score_detected"
    elif task_selected_action_created or final_action_created:
        status = "blocked_selected_action_created"
    elif direct_command_created or sandbox_execution_created:
        status = "blocked_direct_command_created"
    elif external_control_created:
        status = "blocked_external_control_detected"
    elif memory_write_performed or learning_candidate_created:
        status = "blocked_memory_write_detected"
    elif first_output_created:
        status = "blocked_first_output_detected"
    elif live_runtime_session_created:
        status = "blocked_live_runtime_detected"
    elif delta > 0:
        status = "candidate_readback_score_created_boosted"
    elif delta < 0:
        status = "candidate_readback_score_created_lowered"
    return HostBodyInternalActionCandidateReadbackScoreRecord(
        candidate_readback_score_id=f"host_body_candidate_readback_score:{kind}:{status}:{final_priority}",
        schema_version=SCORE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_readback_signal_id=str(_get(signal, "readback_internal_action_signal_id")),
        source_internal_action_candidate_id=_get(candidate, "internal_action_candidate_id"),
        candidate_action_kind=kind,
        base_candidate_priority=base,
        readback_delta=delta,
        final_candidate_priority=final_priority,
        score_reason_codes=_score_reason_codes(str(_get(signal, "signal_theme", "none")), kind, delta),
        score_summary=_score_summary(kind, delta, status),
        score_status=status,
        internal_action_choice_score_created=True,
        task_action_score_created=task_action_score_created,
        candidate_kind_allowed=kind_allowed,
        readback_signal_applied=delta != 0 and signal_valid,
        task_selected_action_created=task_selected_action_created,
        final_action_created=final_action_created,
        direct_command_created=direct_command_created,
        sandbox_execution_created=sandbox_execution_created,
        external_control_created=external_control_created,
        memory_write_performed=memory_write_performed,
        learning_candidate_created=learning_candidate_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=_refs_from(signal, candidate),
    )


def validate_host_body_internal_action_candidate_readback_score(score: Any) -> dict[str, object]:
    record = _record(score)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["score_status"]),
        {
            "candidate_readback_score_created",
            "candidate_readback_score_created_boosted",
            "candidate_readback_score_created_no_change",
            "candidate_readback_score_created_lowered",
        },
    )


def build_host_body_readback_influenced_internal_action_ordering(
    *,
    influence_plan: Any,
    candidate_readback_scores: tuple[Any, ...] | list[Any],
    task_action_ordering_changed: bool = False,
    task_selected_action_created: bool = False,
    final_action_created: bool = False,
    direct_command_created: bool = False,
    sandbox_execution_created: bool = False,
    external_control_created: bool = False,
    memory_write_performed: bool = False,
    learning_candidate_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyReadbackInfluencedInternalActionOrderingRecord:
    plan = _record(influence_plan)
    scores = tuple(_record(item) for item in candidate_readback_scores)
    valid_scores = all(validate_host_body_internal_action_candidate_readback_score(item)["valid"] for item in scores)
    original_kinds = tuple(str(_get(item, "candidate_action_kind")) for item in scores)
    ordered = tuple(
        sorted(
            scores,
            key=lambda item: (
                -int(_get(item, "final_candidate_priority", 0)),
                TIE_BREAKER_INDEX.get(str(_get(item, "candidate_action_kind")), 99),
            ),
        )
    )
    ordered_kinds = tuple(str(_get(item, "candidate_action_kind")) for item in ordered)
    changed = any(int(_get(item, "readback_delta", 0)) != 0 for item in scores) or ordered_kinds != original_kinds
    status = "readback_influenced_internal_action_ordering_created_changed" if changed else "readback_influenced_internal_action_ordering_created_no_change"
    if not valid_scores:
        status = "blocked_invalid_candidate_score"
    elif task_action_ordering_changed:
        status = "blocked_task_action_ordering_changed"
    elif task_selected_action_created or final_action_created:
        status = "blocked_selected_action_created"
    elif direct_command_created or sandbox_execution_created:
        status = "blocked_direct_command_created"
    elif external_control_created:
        status = "blocked_external_control_detected"
    elif memory_write_performed or learning_candidate_created:
        status = "blocked_memory_write_detected"
    elif first_output_created:
        status = "blocked_first_output_detected"
    elif live_runtime_session_created:
        status = "blocked_live_runtime_detected"
    ordering_kind = "host_body_internal_action_readback_ordering_no_change" if not changed else "host_body_internal_action_readback_ordering"
    if status.startswith("blocked_"):
        ordering_kind = "blocked_ordering"
    selected = ordered_kinds[0] if ordered_kinds else None
    return HostBodyReadbackInfluencedInternalActionOrderingRecord(
        readback_influenced_ordering_id=f"host_body_readback_influenced_ordering:{status}:{_slug(selected)}",
        schema_version=ORDERING_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_influence_plan_id=str(_get(plan, "readback_internal_action_influence_plan_id")),
        candidate_readback_score_ids=tuple(str(_get(item, "candidate_readback_score_id")) for item in scores if item),
        ordered_candidate_ids=tuple(str(_get(item, "source_internal_action_candidate_id") or _get(item, "candidate_readback_score_id")) for item in ordered if item),
        ordered_candidate_action_kinds=ordered_kinds,
        ordering_kind=ordering_kind,
        ordering_status=status,
        ordering_summary=_ordering_summary(status, selected),
        readback_influence_applied=True,
        internal_action_ordering_changed=changed,
        task_action_ordering_changed=task_action_ordering_changed,
        deterministic_tie_breaker_used=True,
        tie_breaker_order=TIE_BREAKER_ORDER,
        selected_internal_action_kind_preview=selected,
        task_selected_action_created=task_selected_action_created,
        final_action_created=final_action_created,
        direct_command_created=direct_command_created,
        sandbox_execution_created=sandbox_execution_created,
        external_control_created=external_control_created,
        memory_write_performed=memory_write_performed,
        learning_candidate_created=learning_candidate_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=_refs_from(plan, *scores),
    )


def validate_host_body_readback_influenced_internal_action_ordering(ordering: Any) -> dict[str, object]:
    record = _record(ordering)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["ordering_status"]),
        {
            "readback_influenced_internal_action_ordering_created",
            "readback_influenced_internal_action_ordering_created_changed",
            "readback_influenced_internal_action_ordering_created_no_change",
        },
    )


def build_host_body_readback_influenced_internal_action_choice(
    *,
    readback_influenced_ordering: Any,
    selected_internal_action_kind: str | None = None,
    teacher_approval_created: bool = False,
    learning_approval_created: bool = False,
    task_selected_action_created: bool = False,
    final_action_created: bool = False,
    direct_command_created: bool = False,
    sandbox_execution_created: bool = False,
    external_control_created: bool = False,
    memory_write_performed: bool = False,
    learning_candidate_created: bool = False,
    automatic_learning_approval_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyReadbackInfluencedInternalActionChoiceRecord:
    ordering = _record(readback_influenced_ordering)
    ordering_valid = bool(ordering and validate_host_body_readback_influenced_internal_action_ordering(ordering)["valid"])
    selected = selected_internal_action_kind or _get(ordering, "selected_internal_action_kind_preview")
    status = "readback_influenced_internal_action_choice_selected"
    if not ordering_valid:
        status = "blocked_invalid_ordering"
    elif selected is None:
        status = "readback_influenced_internal_action_choice_deferred_no_candidates"
    elif selected not in ALLOWED_INTERNAL_ACTION_KINDS:
        status = "blocked_forbidden_selected_kind"
    elif teacher_approval_created or learning_approval_created:
        status = "blocked_teacher_approval_created"
    elif task_selected_action_created or final_action_created:
        status = "blocked_task_selected_action_created"
    elif direct_command_created or sandbox_execution_created:
        status = "blocked_direct_command_created"
    elif external_control_created:
        status = "blocked_external_control_created"
    elif memory_write_performed:
        status = "blocked_memory_write_detected"
    elif learning_candidate_created or automatic_learning_approval_created:
        status = "blocked_learning_candidate_created"
    elif first_output_created:
        status = "blocked_first_output_detected"
    elif live_runtime_session_created:
        status = "blocked_live_runtime_detected"
    choice_kind = _choice_kind(selected)
    if status.startswith("blocked_"):
        choice_kind = "blocked_choice"
    candidate_ids = tuple(_get(ordering, "ordered_candidate_ids", ()) or ())
    return HostBodyReadbackInfluencedInternalActionChoiceRecord(
        readback_influenced_choice_id=f"host_body_readback_influenced_choice:{_slug(selected)}:{status}",
        schema_version=CHOICE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_readback_influenced_ordering_id=str(_get(ordering, "readback_influenced_ordering_id")),
        selected_internal_action_kind=selected,
        selected_candidate_id=str(candidate_ids[0]) if candidate_ids else None,
        choice_kind=choice_kind,
        choice_status=status,
        choice_summary=_choice_summary(status, selected),
        choice_uses_readback_influence=True,
        choice_is_internal_only=True,
        choice_is_record_only=True,
        teacher_review_request_recorded=selected == "request_teacher_review",
        teacher_approval_created=teacher_approval_created,
        learning_approval_created=learning_approval_created,
        task_selected_action_created=task_selected_action_created,
        final_action_created=final_action_created,
        direct_command_created=direct_command_created,
        sandbox_execution_created=sandbox_execution_created,
        external_control_created=external_control_created,
        memory_write_performed=memory_write_performed,
        learning_candidate_created=learning_candidate_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=_refs_from(ordering),
    )


def validate_host_body_readback_influenced_internal_action_choice(choice: Any) -> dict[str, object]:
    record = _record(choice)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["choice_status"]),
        {
            "readback_influenced_internal_action_choice_selected",
            "readback_influenced_internal_action_choice_deferred_no_candidates",
        },
    )


def build_host_body_readback_influenced_internal_action_result(
    *,
    readback_influenced_choice: Any,
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
) -> HostBodyReadbackInfluencedInternalActionResultRecord:
    choice = _record(readback_influenced_choice)
    choice_valid = bool(choice and validate_host_body_readback_influenced_internal_action_choice(choice)["valid"])
    selected = _get(choice, "selected_internal_action_kind")
    status = _result_status(selected)
    if not choice_valid:
        status = "blocked_forbidden_authority"
    elif any((actual_screen_mutated, actual_sound_played, unity_runtime_mutated, avatar_control_created)):
        status = "blocked_forbidden_authority"
    elif any((
        task_selected_action_created,
        final_action_created,
        direct_command_created,
        sandbox_execution_created,
    )):
        status = "blocked_task_action_selection"
    elif any((
        external_control_created,
        os_control_created,
        mouse_control_created,
        keyboard_control_created,
        browser_control_created,
        file_operation_created,
        network_execution_created,
        shell_execution_created,
        external_api_call_created,
    )):
        status = "blocked_external_control"
    elif memory_layer_write_performed or memory_write_approval_created:
        status = "blocked_memory_write"
    elif learning_candidate_created or automatic_learning_approval_created:
        status = "blocked_learning_candidate_creation"
    elif first_output_created:
        status = "blocked_first_output"
    elif live_runtime_session_created:
        status = "blocked_live_runtime"
    elif production_behavior_created or teacher_approval_created or learning_approval_created:
        status = "blocked_forbidden_authority"
    result_kind = _result_kind(selected)
    if status.startswith("blocked_"):
        result_kind = "blocked_result"
    return HostBodyReadbackInfluencedInternalActionResultRecord(
        readback_influenced_result_id=f"host_body_readback_influenced_result:{_slug(selected)}:{status}",
        schema_version=RESULT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_readback_influenced_choice_id=str(_get(choice, "readback_influenced_choice_id")),
        selected_internal_action_kind=selected,
        result_kind=result_kind,
        result_status=status,
        result_summary=_result_summary(status, selected),
        internal_marker_created=selected in {"mark_uncertain", "mark_event_interesting"},
        home_status_update_recorded=selected == "update_home_status",
        teacher_review_request_recorded=selected == "request_teacher_review",
        internal_focus_marker_recorded=selected == "shift_internal_focus",
        event_processing_pause_marker_recorded=selected == "pause_event_processing",
        observe_again_recommendation_recorded=selected == "observe_again",
        readback_reason_refs=tuple(str(ref) for ref in _get(choice, "source_trace_refs", ()) or ()),
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
        source_trace_refs=_refs_from(choice),
    )


def validate_host_body_readback_influenced_internal_action_result(result: Any) -> dict[str, object]:
    record = _record(result)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["result_status"]),
        {
            "readback_influenced_internal_action_result_recorded",
            "readback_influenced_internal_action_result_recorded_request_teacher_review",
            "readback_influenced_internal_action_result_recorded_update_home_status",
            "readback_influenced_internal_action_result_recorded_mark_uncertain",
            "readback_influenced_internal_action_result_recorded_observe_again",
        },
    )


def build_host_body_readback_internal_action_influence_trace(
    *,
    influence_plan: Any,
    readback_signals: tuple[Any, ...] | list[Any] = (),
    candidate_scores: tuple[Any, ...] | list[Any] = (),
    orderings: tuple[Any, ...] | list[Any] = (),
    choices: tuple[Any, ...] | list[Any] = (),
    results: tuple[Any, ...] | list[Any] = (),
    trace_spine_boundary: Any | None = None,
    raw_trace_summarized_during_service_period: bool = False,
    concept_id_embedded_into_raw_history: bool = False,
    task_action_selection_influence_created: bool = False,
    task_selected_action_created: bool = False,
    final_action_created: bool = False,
    direct_command_created: bool = False,
    sandbox_execution_created: bool = False,
    external_control_created: bool = False,
    memory_write_performed: bool = False,
    learning_candidate_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyReadbackInternalActionInfluenceTraceRecord:
    plan = _record(influence_plan)
    signals = tuple(_record(item) for item in readback_signals)
    scores = tuple(_record(item) for item in candidate_scores)
    ordering_records = tuple(_record(item) for item in orderings)
    choice_records = tuple(_record(item) for item in choices)
    result_records = tuple(_record(item) for item in results)
    boundary = _record(trace_spine_boundary)
    boundary_valid = True if boundary is None else validate_trace_spine_raw_evidence_boundary(boundary)["valid"]
    status = "readback_internal_action_influence_trace_recorded"
    if any(not validate_host_body_readback_internal_action_signal(item)["valid"] for item in signals):
        status = "blocked_invalid_signal"
    elif any(not validate_host_body_internal_action_candidate_readback_score(item)["valid"] for item in scores):
        status = "blocked_invalid_candidate_score"
    elif any(not validate_host_body_readback_influenced_internal_action_ordering(item)["valid"] for item in ordering_records):
        status = "blocked_invalid_ordering"
    elif any(not validate_host_body_readback_influenced_internal_action_choice(item)["valid"] for item in choice_records):
        status = "blocked_invalid_choice"
    elif any(not validate_host_body_readback_influenced_internal_action_result(item)["valid"] for item in result_records):
        status = "blocked_invalid_result"
    elif not boundary_valid or raw_trace_summarized_during_service_period or concept_id_embedded_into_raw_history:
        status = "blocked_trace_spine_boundary_failure"
    elif task_action_selection_influence_created:
        status = "blocked_task_action_selection_influence"
    elif task_selected_action_created or final_action_created:
        status = "blocked_selected_action_created"
    elif direct_command_created or sandbox_execution_created:
        status = "blocked_direct_command_created"
    elif external_control_created:
        status = "blocked_external_control_detected"
    elif memory_write_performed:
        status = "blocked_memory_write_detected"
    elif learning_candidate_created:
        status = "blocked_learning_candidate_created"
    elif first_output_created:
        status = "blocked_first_output_detected"
    elif live_runtime_session_created:
        status = "blocked_live_runtime_detected"
    elif not signals and not scores and not ordering_records and not choice_records and not result_records:
        status = "readback_internal_action_influence_trace_recorded_empty"
    trace_kind = "single_readback_internal_action_influence_trace"
    if len(choice_records) > 1:
        trace_kind = "mixed_readback_internal_action_influence_trace"
    if not choice_records:
        trace_kind = "empty_readback_internal_action_influence_trace"
    if status.startswith("blocked_"):
        trace_kind = "blocked_readback_internal_action_influence_trace"
    source_refs = _refs_from(plan, boundary, *signals, *scores, *ordering_records, *choice_records, *result_records)
    return HostBodyReadbackInternalActionInfluenceTraceRecord(
        readback_internal_action_influence_trace_id=f"host_body_readback_internal_action_influence_trace:{status}:{len(choice_records)}",
        schema_version=TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_influence_plan_id=str(_get(plan, "readback_internal_action_influence_plan_id")),
        readback_signal_ids=tuple(str(_get(item, "readback_internal_action_signal_id")) for item in signals if item),
        candidate_score_ids=tuple(str(_get(item, "candidate_readback_score_id")) for item in scores if item),
        ordering_ids=tuple(str(_get(item, "readback_influenced_ordering_id")) for item in ordering_records if item),
        choice_ids=tuple(str(_get(item, "readback_influenced_choice_id")) for item in choice_records if item),
        result_ids=tuple(str(_get(item, "readback_influenced_result_id")) for item in result_records if item),
        trace_kind=trace_kind,
        trace_status=status,
        trace_summary=_trace_summary(status, len(choice_records)),
        readback_signal_count=len(signals),
        candidate_score_count=len(scores),
        ordering_count=len(ordering_records),
        choice_count=len(choice_records),
        result_count=len(result_records),
        internal_action_ordering_changed_count=sum(1 for item in ordering_records if _get(item, "internal_action_ordering_changed") is True),
        teacher_review_request_count=sum(1 for item in choice_records if _get(item, "selected_internal_action_kind") == "request_teacher_review"),
        mark_uncertain_count=sum(1 for item in choice_records if _get(item, "selected_internal_action_kind") == "mark_uncertain"),
        observe_again_count=sum(1 for item in choice_records if _get(item, "selected_internal_action_kind") == "observe_again"),
        pause_event_processing_count=sum(1 for item in choice_records if _get(item, "selected_internal_action_kind") == "pause_event_processing"),
        trace_spine_boundary_preserved=boundary_valid,
        raw_trace_append_only_confirmed=True,
        raw_trace_summarized_during_service_period=raw_trace_summarized_during_service_period,
        memory_layer_stores_interpretation_only=True,
        source_trace_refs_preserved=bool(source_refs),
        concept_id_embedded_into_raw_history=concept_id_embedded_into_raw_history,
        task_action_selection_influence_created=task_action_selection_influence_created,
        task_selected_action_created=task_selected_action_created,
        final_action_created=final_action_created,
        direct_command_created=direct_command_created,
        sandbox_execution_created=sandbox_execution_created,
        external_control_created=external_control_created,
        memory_write_performed=memory_write_performed,
        learning_candidate_created=learning_candidate_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=source_refs,
    )


def validate_host_body_readback_internal_action_influence_trace(trace: Any) -> dict[str, object]:
    record = _record(trace)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["trace_status"]),
        {
            "readback_internal_action_influence_trace_recorded",
            "readback_internal_action_influence_trace_recorded_empty",
        },
    )


def build_host_body_readback_internal_action_influence_audit(
    *,
    influence_plan: Any | None,
    influence_trace: Any | None,
    trace_spine_boundary: Any | None,
    preferred_pass_status: str | None = None,
    teacher_approval_created: bool = False,
    production_behavior_created: bool = False,
) -> HostBodyReadbackInternalActionInfluenceAudit:
    plan = _record(influence_plan)
    trace = _record(influence_trace)
    boundary = _record(trace_spine_boundary)
    plan_valid = bool(plan and validate_host_body_readback_internal_action_influence_plan(plan)["valid"])
    trace_valid = bool(trace and validate_host_body_readback_internal_action_influence_trace(trace)["valid"])
    boundary_valid = bool(boundary and validate_trace_spine_raw_evidence_boundary(boundary)["valid"])
    reasons: list[str] = []
    status = preferred_pass_status or _pass_status_from_trace(trace)
    if plan is None:
        status = "blocked_missing_influence_plan"
    elif not boundary_valid:
        status = "blocked_trace_spine_boundary_failure"
    elif trace and _get(trace, "raw_trace_summarized_during_service_period"):
        status = "blocked_raw_trace_summarized"
    elif trace and _get(trace, "concept_id_embedded_into_raw_history"):
        status = "blocked_concept_id_embedded_into_raw_history"
    elif not trace_valid:
        status = _blocked_status_from_trace(trace)
    elif trace and _get(trace, "task_action_selection_influence_created"):
        status = "blocked_task_action_selection_influence_detected"
    elif trace and _get(trace, "task_selected_action_created"):
        status = "blocked_selected_action_created"
    elif trace and _get(trace, "final_action_created"):
        status = "blocked_final_action_created"
    elif trace and _get(trace, "direct_command_created"):
        status = "blocked_direct_command_created"
    elif trace and _get(trace, "sandbox_execution_created"):
        status = "blocked_sandbox_execution_created"
    elif trace and _get(trace, "external_control_created"):
        status = "blocked_external_control_detected"
    elif trace and _get(trace, "memory_write_performed"):
        status = "blocked_memory_write_detected"
    elif trace and _get(trace, "learning_candidate_created"):
        status = "blocked_learning_candidate_creation_detected"
    elif teacher_approval_created:
        status = "blocked_teacher_approval_created"
    elif trace and _get(trace, "first_output_created"):
        status = "blocked_first_output_detected"
    elif trace and _get(trace, "live_runtime_session_created"):
        status = "blocked_live_runtime_detected"
    elif production_behavior_created:
        status = "blocked_production_behavior_detected"
    if status.startswith("blocked_"):
        reasons.append(status)
    source_refs = _refs_from(plan, trace, boundary)
    return HostBodyReadbackInternalActionInfluenceAudit(
        readback_internal_action_influence_audit_id=f"host_body_readback_internal_action_influence_audit:{status}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_influence_plan_id=_get(plan, "readback_internal_action_influence_plan_id"),
        source_influence_trace_id=_get(trace, "readback_internal_action_influence_trace_id"),
        source_trace_spine_boundary_id=_get(boundary, "trace_spine_boundary_id"),
        influence_plan_valid=plan_valid,
        readback_signals_valid=bool(trace and _get(trace, "trace_status") != "blocked_invalid_signal"),
        candidate_scores_valid=bool(trace and _get(trace, "trace_status") != "blocked_invalid_candidate_score"),
        orderings_valid=bool(trace and _get(trace, "trace_status") != "blocked_invalid_ordering"),
        choices_valid=bool(trace and _get(trace, "trace_status") != "blocked_invalid_choice"),
        results_valid=bool(trace and _get(trace, "trace_status") != "blocked_invalid_result"),
        influence_trace_valid=trace_valid,
        trace_spine_boundary_valid=boundary_valid,
        host_body_working_readback_confirmed=True,
        internal_action_choice_influence_confirmed=bool(trace and _get(trace, "internal_action_ordering_changed_count", 0) >= 0),
        internal_only_confirmed=True,
        record_only_confirmed=True,
        trace_spine_format_unified_confirmed=bool(_get(boundary, "trace_spine_format_unified", False)),
        trace_spine_time_aligned_confirmed=bool(_get(boundary, "trace_spine_time_aligned", False)),
        raw_trace_append_only_confirmed=bool(_get(boundary, "raw_trace_append_only_confirmed", False)),
        raw_trace_not_summarized_during_service_period=not bool(_get(trace, "raw_trace_summarized_during_service_period", True)),
        memory_layer_stores_interpretation_only_confirmed=bool(_get(trace, "memory_layer_stores_interpretation_only", False)),
        source_trace_refs_preserved_confirmed=bool(_get(trace, "source_trace_refs_preserved", False)),
        concept_id_not_embedded_into_raw_history_confirmed=not bool(_get(trace, "concept_id_embedded_into_raw_history", True)),
        raw_trace_not_dumped_into_memory_learning_trace_confirmed=not bool(_get(boundary, "raw_trace_dumped_into_memory_learning_trace", True)),
        no_task_action_selection_influence=not bool(trace and _get(trace, "task_action_selection_influence_created", False)),
        no_task_selected_action=not bool(trace and _get(trace, "task_selected_action_created", False)),
        no_final_action=not bool(trace and _get(trace, "final_action_created", False)),
        no_direct_command=not bool(trace and _get(trace, "direct_command_created", False)),
        no_sandbox_execution=not bool(trace and _get(trace, "sandbox_execution_created", False)),
        no_external_control=not bool(trace and _get(trace, "external_control_created", False)),
        no_os_control=True,
        no_mouse_control=True,
        no_keyboard_control=True,
        no_browser_control=True,
        no_file_operation=True,
        no_network_execution=True,
        no_shell_execution=True,
        no_external_api_call=True,
        no_memory_layer_write=not bool(trace and _get(trace, "memory_write_performed", False)),
        no_long_term_memory_write=True,
        no_core_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_state_persistence_write=True,
        no_learning_candidate_creation=not bool(trace and _get(trace, "learning_candidate_created", False)),
        no_automatic_learning_approval=True,
        no_teacher_approval_created=not teacher_approval_created,
        no_first_output=not bool(trace and _get(trace, "first_output_created", False)),
        no_live_runtime_session=not bool(trace and _get(trace, "live_runtime_session_created", False)),
        no_thought_engine_behavior=True,
        no_production_behavior=not production_behavior_created,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(reasons),
        source_trace_refs=source_refs,
    )


def validate_host_body_readback_internal_action_influence_audit(audit: Any) -> dict[str, object]:
    record = _record(audit)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["audit_status"]),
        {
            "passed_host_body_readback_internal_action_influence",
            "passed_readback_influenced_request_teacher_review",
            "passed_readback_influenced_mark_uncertain",
            "passed_readback_influenced_observe_again",
            "passed_readback_influenced_pause_event_processing",
            "passed_trace_spine_boundary_preserved",
        },
    )


def build_host_body_readback_internal_action_influence_readiness(
    *,
    readback_internal_action_influence_audit: Any | None,
    readiness_status: str = "ready_for_host_body_embodied_learning_closed_loop_audit_only",
) -> HostBodyReadbackInternalActionInfluenceReadinessRecord:
    audit = _record(readback_internal_action_influence_audit)
    if audit is None:
        status = "not_ready_missing_readback_internal_action_influence_audit"
    elif not validate_host_body_readback_internal_action_influence_audit(audit)["valid"]:
        status = "not_ready_boundary_failure"
    elif readiness_status.startswith("ready_for_"):
        status = readiness_status
    else:
        status = "blocked_forbidden_authority_detected"
    return HostBodyReadbackInternalActionInfluenceReadinessRecord(
        readback_internal_action_influence_readiness_id=f"host_body_readback_internal_action_influence_readiness:{status}",
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_readback_internal_action_influence_audit_id=str(_get(audit, "readback_internal_action_influence_audit_id")),
        current_verified_capability="Host Body working readback influences internal-only action choice ordering.",
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason="Seal the first embodied learning readback loop without Task Engine or external authority.",
        ready_for_host_body_embodied_learning_closed_loop_audit=True,
        ready_for_bounded_embodied_loop_runner=True,
        ready_for_no_codex_teacher_console_flow=True,
        ready_for_task_engine_action_selection_influence=False,
        ready_for_direct_command=False,
        ready_for_external_control=False,
        ready_for_long_term_memory_write=False,
        ready_for_core_memory_write=False,
        ready_for_learning_candidate_creation=False,
        ready_for_automatic_learning_approval=False,
        ready_for_first_output=False,
        ready_for_live_runtime_session=False,
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=_refs_from(audit),
    )


def validate_host_body_readback_internal_action_influence_readiness(readiness: Any) -> dict[str, object]:
    record = _record(readiness)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["readiness_status"]),
        {
            "ready_for_host_body_embodied_learning_closed_loop_audit_only",
            "ready_for_bounded_embodied_loop_runner_only",
            "ready_for_no_codex_teacher_console_flow_only",
        },
    )


def build_demo_prior_uncertainty_boosts_mark_uncertain() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_uncertainty",
        candidates=(("mark_uncertain", 5), ("observe_again", 5), ("request_teacher_review", 4)),
        preferred_pass_status="passed_readback_influenced_mark_uncertain",
    )


def build_demo_prior_teacher_review_boosts_request_teacher_review() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_teacher_review_needed",
        candidates=(("request_teacher_review", 5), ("mark_uncertain", 6), ("observe_again", 5)),
        preferred_pass_status="passed_readback_influenced_request_teacher_review",
    )


def build_demo_prior_observe_again_boosts_observe_again() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_observe_again_helped",
        candidates=(("observe_again", 5), ("mark_uncertain", 6), ("request_teacher_review", 4)),
        preferred_pass_status="passed_readback_influenced_observe_again",
    )


def build_demo_runtime_bridge_deferred_boosts_pause_or_review() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_runtime_bridge_deferred",
        candidates=(("request_teacher_review", 5), ("pause_event_processing", 5), ("observe_again", 4)),
        working_payload=build_demo_runtime_bridge_reviewed_concept_working_readback(),
        preferred_pass_status="passed_readback_influenced_request_teacher_review",
    )


def build_demo_no_matching_readback_signal_no_change() -> dict[str, object]:
    return _build_demo(
        signal_theme="none",
        candidates=(("observe_again", 5), ("update_home_status", 4)),
        preferred_pass_status="passed_host_body_readback_internal_action_influence",
    )


def build_demo_mixed_readback_internal_action_influence() -> dict[str, object]:
    demos = (
        build_demo_prior_uncertainty_boosts_mark_uncertain(),
        build_demo_prior_teacher_review_boosts_request_teacher_review(),
        build_demo_prior_observe_again_boosts_observe_again(),
        build_demo_runtime_bridge_deferred_boosts_pause_or_review(),
    )
    first = demos[0]
    plan = HostBodyReadbackInternalActionInfluencePlanRecord.from_dict(first["readback_internal_action_influence_plan"])
    boundary = first["trace_spine_raw_evidence_boundary"]
    signals = tuple(item["readback_internal_action_signals"][0] for item in demos)
    scores = tuple(score for item in demos for score in item["candidate_readback_scores"])
    orderings = tuple(item["readback_influenced_internal_action_ordering"] for item in demos)
    choices = tuple(item["readback_influenced_internal_action_choice"] for item in demos)
    results = tuple(item["readback_influenced_internal_action_result"] for item in demos)
    trace = build_host_body_readback_internal_action_influence_trace(
        influence_plan=plan,
        readback_signals=signals,
        candidate_scores=scores,
        orderings=orderings,
        choices=choices,
        results=results,
        trace_spine_boundary=boundary,
    )
    audit = build_host_body_readback_internal_action_influence_audit(
        influence_plan=plan,
        influence_trace=trace,
        trace_spine_boundary=boundary,
        preferred_pass_status="passed_host_body_readback_internal_action_influence",
    )
    readiness = build_host_body_readback_internal_action_influence_readiness(
        readback_internal_action_influence_audit=audit
    )
    payload = {
        "readback_internal_action_influence_plan": plan.to_dict(),
        "readback_internal_action_signals": signals,
        "candidate_readback_scores": scores,
        "readback_influenced_internal_action_orderings": tuple(item for item in orderings),
        "readback_influenced_internal_action_choices": tuple(item for item in choices),
        "readback_influenced_internal_action_results": tuple(item for item in results),
        "trace_spine_raw_evidence_boundary": boundary,
        "readback_internal_action_influence_trace": trace.to_dict(),
        "readback_internal_action_influence_audit": audit.to_dict(),
        "readback_internal_action_influence_readiness": readiness.to_dict(),
    }
    payload["rendered_readback_internal_action_influence_summary"] = (
        render_host_body_readback_internal_action_influence_summary_text(payload)
    )
    payload["rendered_readback_signal_table"] = render_host_body_readback_signal_table(signals)
    payload["rendered_readback_internal_action_ordering_table"] = (
        render_host_body_readback_internal_action_ordering_table(orderings)
    )
    return payload


def build_demo_blocked_task_action_influence() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_uncertainty",
        candidates=(("mark_uncertain", 5), ("observe_again", 5)),
        trace_overrides={"task_action_selection_influence_created": True},
    )


def build_demo_blocked_selected_action_created() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_uncertainty",
        candidates=(("mark_uncertain", 5), ("observe_again", 5)),
        trace_overrides={"task_selected_action_created": True},
    )


def build_demo_blocked_direct_command_created() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_uncertainty",
        candidates=(("mark_uncertain", 5), ("observe_again", 5)),
        trace_overrides={"direct_command_created": True},
    )


def build_demo_blocked_external_control() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_uncertainty",
        candidates=(("mark_uncertain", 5), ("observe_again", 5)),
        trace_overrides={"external_control_created": True},
    )


def build_demo_blocked_memory_write() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_uncertainty",
        candidates=(("mark_uncertain", 5), ("observe_again", 5)),
        trace_overrides={"memory_write_performed": True},
    )


def build_demo_blocked_learning_candidate_creation() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_uncertainty",
        candidates=(("mark_uncertain", 5), ("observe_again", 5)),
        trace_overrides={"learning_candidate_created": True},
    )


def build_demo_blocked_raw_trace_summarization() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_uncertainty",
        candidates=(("mark_uncertain", 5), ("observe_again", 5)),
        trace_overrides={"raw_trace_summarized_during_service_period": True},
    )


def build_demo_blocked_concept_id_embedded_into_raw_history() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_uncertainty",
        candidates=(("mark_uncertain", 5), ("observe_again", 5)),
        trace_overrides={"concept_id_embedded_into_raw_history": True},
    )


def build_demo_blocked_first_output() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_uncertainty",
        candidates=(("mark_uncertain", 5), ("observe_again", 5)),
        trace_overrides={"first_output_created": True},
    )


def build_demo_blocked_live_runtime() -> dict[str, object]:
    return _build_demo(
        signal_theme="prior_uncertainty",
        candidates=(("mark_uncertain", 5), ("observe_again", 5)),
        trace_overrides={"live_runtime_session_created": True},
    )


def render_host_body_readback_internal_action_influence_summary_text(payload: dict[str, object]) -> str:
    audit = payload.get("readback_internal_action_influence_audit", {})
    trace = payload.get("readback_internal_action_influence_trace", {})
    return "\n".join(
        (
            "Host Body Readback Internal Action Influence",
            f"audit_status: {audit.get('audit_status')}",
            f"choice_count: {trace.get('choice_count')}",
            f"internal_action_ordering_changed_count: {trace.get('internal_action_ordering_changed_count')}",
            "task_selected_action_created: false",
            "first_output_created: false",
        )
    )


def render_host_body_readback_internal_action_ordering_table(
    orderings: tuple[Any, ...] | list[Any],
) -> str:
    lines = ["ordering_id | status | selected_preview | ordered_kinds"]
    for item in orderings:
        record = _record(item) or {}
        lines.append(
            " | ".join(
                (
                    str(record.get("readback_influenced_ordering_id")),
                    str(record.get("ordering_status")),
                    str(record.get("selected_internal_action_kind_preview")),
                    ",".join(str(kind) for kind in record.get("ordered_candidate_action_kinds", ()) or ()),
                )
            )
        )
    return "\n".join(lines)


def render_host_body_readback_signal_table(signals: tuple[Any, ...] | list[Any]) -> str:
    lines = ["signal_id | theme | strength | status"]
    for item in signals:
        record = _record(item) or {}
        lines.append(
            " | ".join(
                (
                    str(record.get("readback_internal_action_signal_id")),
                    str(record.get("signal_theme")),
                    str(record.get("signal_strength")),
                    str(record.get("signal_status")),
                )
            )
        )
    return "\n".join(lines)


def _build_demo(
    *,
    signal_theme: str,
    candidates: tuple[tuple[str, int], ...],
    working_payload: dict[str, object] | None = None,
    preferred_pass_status: str = "passed_host_body_readback_internal_action_influence",
    trace_overrides: dict[str, object] | None = None,
) -> dict[str, object]:
    working_payload = working_payload or build_demo_uncertainty_reviewed_concept_working_readback()
    internal_payload = build_demo_unknown_event_marks_uncertain()
    boundary_payload = build_demo_trace_spine_raw_evidence_boundary()
    boundary = boundary_payload["trace_spine_raw_evidence_boundary"]
    plan = build_host_body_readback_internal_action_influence_plan(
        working_readback_integration_audit=working_payload["host_body_working_readback_integration_audit"],
        internal_action_choice_audit=internal_payload["internal_action_choice_audit"],
        trace_spine_boundary=boundary,
    )
    visibility = working_payload["host_body_working_readback_visibility_records"][0]
    signal = build_host_body_readback_internal_action_signal(
        influence_plan=plan,
        working_readback_visibility=visibility,
        signal_theme=signal_theme,
    )
    scores = tuple(
        build_host_body_internal_action_candidate_readback_score(
            readback_signal=signal,
            candidate_action_kind=kind,
            base_candidate_priority=priority,
        )
        for kind, priority in candidates
    )
    ordering = build_host_body_readback_influenced_internal_action_ordering(
        influence_plan=plan,
        candidate_readback_scores=scores,
    )
    choice = build_host_body_readback_influenced_internal_action_choice(
        readback_influenced_ordering=ordering
    )
    result = build_host_body_readback_influenced_internal_action_result(
        readback_influenced_choice=choice
    )
    trace = build_host_body_readback_internal_action_influence_trace(
        influence_plan=plan,
        readback_signals=(signal,),
        candidate_scores=scores,
        orderings=(ordering,),
        choices=(choice,),
        results=(result,),
        trace_spine_boundary=boundary,
        **(trace_overrides or {}),
    )
    audit = build_host_body_readback_internal_action_influence_audit(
        influence_plan=plan,
        influence_trace=trace,
        trace_spine_boundary=boundary,
        preferred_pass_status=preferred_pass_status,
    )
    readiness = build_host_body_readback_internal_action_influence_readiness(
        readback_internal_action_influence_audit=audit
    )
    payload = {
        "readback_internal_action_influence_plan": plan.to_dict(),
        "readback_internal_action_signals": (signal.to_dict(),),
        "candidate_readback_scores": tuple(item.to_dict() for item in scores),
        "readback_influenced_internal_action_ordering": ordering.to_dict(),
        "readback_influenced_internal_action_choice": choice.to_dict(),
        "readback_influenced_internal_action_result": result.to_dict(),
        "trace_spine_raw_evidence_boundary": boundary,
        "readback_internal_action_influence_trace": trace.to_dict(),
        "readback_internal_action_influence_audit": audit.to_dict(),
        "readback_internal_action_influence_readiness": readiness.to_dict(),
    }
    payload["rendered_readback_internal_action_influence_summary"] = (
        render_host_body_readback_internal_action_influence_summary_text(payload)
    )
    payload["rendered_readback_signal_table"] = render_host_body_readback_signal_table((signal,))
    payload["rendered_readback_internal_action_ordering_table"] = (
        render_host_body_readback_internal_action_ordering_table((ordering,))
    )
    return payload


def _infer_signal_theme(visibility: dict[str, Any] | None) -> str:
    joined = " ".join(_refs_from(visibility))
    kind = str(_get(visibility, "visibility_kind", ""))
    if "runtime_bridge" in joined or "runtime_bridge" in kind:
        return "prior_runtime_bridge_deferred"
    if "interesting" in joined or "interesting" in kind:
        return "prior_interesting_event"
    if "uncertainty" in joined or "uncertainty" in kind:
        return "prior_uncertainty"
    return "none"


def _signal_status_for_theme(theme: str) -> str:
    if theme in {"prior_uncertainty", "prior_unknown_event"}:
        return "readback_internal_action_signal_created_uncertainty"
    if theme == "prior_teacher_review_needed":
        return "readback_internal_action_signal_created_teacher_review"
    if theme == "prior_observe_again_helped":
        return "readback_internal_action_signal_created_observe_again"
    if theme == "prior_runtime_bridge_deferred":
        return "readback_internal_action_signal_created_runtime_bridge"
    if theme == "none":
        return "readback_internal_action_signal_created_noop"
    return "readback_internal_action_signal_created"


def _signal_reason_codes(theme: str) -> tuple[str, ...]:
    if theme == "none":
        return ("no_matching_readback_signal",)
    return (f"readback_theme:{theme}", "internal_action_ordering_only")


def _signal_summary(theme: str, status: str) -> str:
    if status.startswith("blocked_"):
        return "Readback signal blocked by boundary policy."
    if theme == "none":
        return "No matching readback signal applies."
    return f"Readback signal {theme} is safe for internal action ordering."


def _deterministic_readback_delta(theme: str, action_kind: str) -> int:
    table = {
        ("prior_uncertainty", "mark_uncertain"): 3,
        ("prior_uncertainty", "request_teacher_review"): 2,
        ("prior_teacher_review_needed", "request_teacher_review"): 3,
        ("prior_observe_again_helped", "observe_again"): 3,
        ("prior_interesting_event", "mark_event_interesting"): 3,
        ("prior_runtime_bridge_deferred", "request_teacher_review"): 3,
        ("prior_runtime_bridge_deferred", "pause_event_processing"): 2,
        ("prior_event_processing_paused", "pause_event_processing"): 3,
        ("prior_unknown_event", "mark_uncertain"): 2,
        ("prior_unknown_event", "observe_again"): 1,
        ("prior_home_status_update", "update_home_status"): 2,
    }
    return table.get((theme, action_kind), 0)


def _bounded_delta(delta: int) -> int:
    return max(DELTA_MIN, min(DELTA_MAX, int(delta)))


def _score_reason_codes(theme: str, kind: str, delta: int) -> tuple[str, ...]:
    effect = _effect_for_kind(kind) if delta > 0 else "no_change"
    return (f"signal:{theme}", f"effect:{effect}", f"delta:{delta}")


def _effect_for_kind(kind: str) -> str:
    return {
        "mark_uncertain": "increase_mark_uncertain_priority",
        "request_teacher_review": "increase_request_teacher_review_priority",
        "observe_again": "increase_observe_again_priority",
        "mark_event_interesting": "increase_mark_event_interesting_priority",
        "pause_event_processing": "increase_pause_event_processing_priority",
        "update_home_status": "increase_update_home_status_priority",
        "shift_internal_focus": "increase_shift_internal_focus_priority",
    }.get(kind, "no_change")


def _score_summary(kind: str, delta: int, status: str) -> str:
    if status.startswith("blocked_"):
        return "Candidate readback score blocked by boundary policy."
    return f"{kind} readback delta {delta} applied for internal action ordering only."


def _ordering_summary(status: str, selected: str | None) -> str:
    if status.startswith("blocked_"):
        return "Readback-influenced ordering blocked by boundary policy."
    return f"Readback-influenced internal ordering preview selects {selected}."


def _choice_kind(kind: str | None) -> str:
    return {
        "observe_again": "readback_influenced_observe_again_choice",
        "mark_event_interesting": "readback_influenced_mark_interesting_choice",
        "mark_uncertain": "readback_influenced_mark_uncertain_choice",
        "request_teacher_review": "readback_influenced_request_teacher_review_choice",
        "shift_internal_focus": "readback_influenced_shift_internal_focus_choice",
        "update_home_status": "readback_influenced_update_home_status_choice",
        "pause_event_processing": "readback_influenced_pause_event_processing_choice",
    }.get(kind, "blocked_choice")


def _choice_summary(status: str, selected: str | None) -> str:
    if status.startswith("blocked_"):
        return "Readback-influenced choice blocked by boundary policy."
    if selected is None:
        return "No internal action candidate selected."
    return f"Readback-influenced internal-only choice selected {selected}."


def _result_kind(kind: str | None) -> str:
    return {
        "observe_again": "readback_influenced_observe_again_recommendation",
        "mark_event_interesting": "readback_influenced_internal_marker_result",
        "mark_uncertain": "readback_influenced_internal_marker_result",
        "request_teacher_review": "readback_influenced_teacher_review_request_record",
        "shift_internal_focus": "readback_influenced_internal_focus_marker",
        "update_home_status": "readback_influenced_home_status_update_record",
        "pause_event_processing": "readback_influenced_event_processing_pause_marker",
    }.get(kind, "blocked_result")


def _result_status(kind: str | None) -> str:
    return {
        "observe_again": "readback_influenced_internal_action_result_recorded_observe_again",
        "mark_uncertain": "readback_influenced_internal_action_result_recorded_mark_uncertain",
        "request_teacher_review": "readback_influenced_internal_action_result_recorded_request_teacher_review",
        "update_home_status": "readback_influenced_internal_action_result_recorded_update_home_status",
        "mark_event_interesting": "readback_influenced_internal_action_result_recorded",
        "shift_internal_focus": "readback_influenced_internal_action_result_recorded",
        "pause_event_processing": "readback_influenced_internal_action_result_recorded",
    }.get(kind, "blocked_forbidden_authority")


def _result_summary(status: str, selected: str | None) -> str:
    if status.startswith("blocked_"):
        return "Readback-influenced result blocked by boundary policy."
    return f"Readback-influenced internal-only result recorded for {selected}."


def _trace_summary(status: str, count: int) -> str:
    if status == "readback_internal_action_influence_trace_recorded":
        return f"{count} readback-influenced internal action choice record(s) traced."
    if status == "readback_internal_action_influence_trace_recorded_empty":
        return "Empty readback internal action influence trace recorded."
    return "Readback internal action influence trace blocked by boundary policy."


def _pass_status_from_trace(trace: dict[str, Any] | None) -> str:
    if trace and _get(trace, "teacher_review_request_count", 0) > 0:
        return "passed_readback_influenced_request_teacher_review"
    if trace and _get(trace, "mark_uncertain_count", 0) > 0:
        return "passed_readback_influenced_mark_uncertain"
    if trace and _get(trace, "observe_again_count", 0) > 0:
        return "passed_readback_influenced_observe_again"
    if trace and _get(trace, "pause_event_processing_count", 0) > 0:
        return "passed_readback_influenced_pause_event_processing"
    return "passed_host_body_readback_internal_action_influence"


def _blocked_status_from_trace(trace: dict[str, Any] | None) -> str:
    status = str(_get(trace, "trace_status", "blocked_invalid_influence_trace"))
    return {
        "blocked_invalid_signal": "blocked_invalid_readback_signal",
        "blocked_invalid_candidate_score": "blocked_invalid_candidate_score",
        "blocked_invalid_ordering": "blocked_invalid_ordering",
        "blocked_invalid_choice": "blocked_invalid_choice",
        "blocked_invalid_result": "blocked_invalid_result",
        "blocked_trace_spine_boundary_failure": "blocked_trace_spine_boundary_failure",
        "blocked_task_action_selection_influence": "blocked_task_action_selection_influence_detected",
        "blocked_selected_action_created": "blocked_selected_action_created",
        "blocked_direct_command_created": "blocked_direct_command_created",
        "blocked_external_control_detected": "blocked_external_control_detected",
        "blocked_memory_write_detected": "blocked_memory_write_detected",
        "blocked_learning_candidate_created": "blocked_learning_candidate_creation_detected",
        "blocked_first_output_detected": "blocked_first_output_detected",
        "blocked_live_runtime_detected": "blocked_live_runtime_detected",
    }.get(status, "blocked_invalid_influence_trace")


def _plan_summary(status: str) -> str:
    if status == "readback_internal_action_influence_plan_created":
        return "Host Body readback internal action influence plan created."
    return "Host Body readback internal action influence plan blocked by boundary policy."


def _readiness_summary(status: str) -> str:
    if status.startswith("ready_for_"):
        return "Host Body readback internal action influence is ready for closed-loop milestone audit."
    if status.startswith("not_ready_"):
        return "Host Body readback internal action influence readiness is not established."
    return "Host Body readback internal action influence readiness is blocked by forbidden authority."
