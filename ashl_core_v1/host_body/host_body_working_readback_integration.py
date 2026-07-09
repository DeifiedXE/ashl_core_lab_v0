"""Host Body ReviewedConcept working readback integration with trace boundaries."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.host_body.host_body_reviewed_concept_replay import (
    build_demo_interesting_event_feedback_reviewed_concept_replay,
    build_demo_mixed_feedback_reviewed_concept_replay,
    build_demo_runtime_bridge_feedback_reviewed_concept_replay,
    build_demo_uncertainty_feedback_reviewed_concept_replay,
    validate_host_body_reviewed_concept_replay_audit,
    validate_host_body_reviewed_concept_replay_trace,
)


SOURCE_ENGINE = "host_body"

PLAN_SCHEMA_VERSION = "qingyin_host_body_working_readback_integration_plan_v0"
MEMORY_LEARNING_TRACE_BRIDGE_SCHEMA_VERSION = (
    "qingyin_host_body_memory_learning_trace_bridge_v0"
)
MEMORY_ROUTING_TRACE_BRIDGE_SCHEMA_VERSION = (
    "qingyin_host_body_memory_routing_trace_bridge_v0"
)
MEMORY_APPLICATION_DATA_BRIDGE_SCHEMA_VERSION = (
    "qingyin_host_body_memory_application_data_bridge_v0"
)
WORKING_READBACK_VISIBILITY_SCHEMA_VERSION = (
    "qingyin_host_body_working_readback_visibility_v0"
)
TRACE_SPINE_BOUNDARY_SCHEMA_VERSION = "qingyin_trace_spine_raw_evidence_boundary_v1"
INTEGRATION_TRACE_SCHEMA_VERSION = (
    "qingyin_host_body_working_readback_integration_trace_v0"
)
AUDIT_SCHEMA_VERSION = "qingyin_host_body_working_readback_integration_audit_v0"
READINESS_SCHEMA_VERSION = (
    "qingyin_host_body_working_readback_integration_readiness_v0"
)

INTEGRATION_NAME = "host_body_reviewed_concept_working_readback_integration"
INTEGRATION_KIND = "existing_working_readback_path_integration"
ALLOWED_OUTPUTS = (
    "memory_learning_trace_bridge",
    "memory_routing_trace_bridge",
    "memory_application_data_bridge",
    "working_readback_visibility",
)
FORBIDDEN_OUTPUTS = (
    "raw_trace_dump_into_memory_learning_trace",
    "raw_trace_summarization",
    "concept_id_embedded_into_raw_history",
    "internal_action_choice_influence",
    "task_selected_action",
    "long_term_memory_write",
    "core_memory_write",
    "first_output",
    "live_runtime_session",
)

TRACE_SPINE_FORMAT_UNIFIED = True
TRACE_SPINE_TIME_ALIGNED = True
RAW_TRACE_APPEND_ONLY_CONFIRMED = True
RAW_TRACE_SUMMARIZED_DURING_SERVICE_PERIOD = False
MEMORY_LAYER_STORES_INTERPRETATION_ONLY = True
SOURCE_TRACE_REFS_PRESERVED = True
CONCEPT_ID_EMBEDDED_INTO_RAW_HISTORY = False
RAW_TRACE_DUMPED_INTO_MEMORY_LEARNING_TRACE = False

SAFE_CLAIM = (
    "ASHL Core v1 can integrate Host Body-derived ReviewedConcept readiness into "
    "the existing working readback path using interpretation-only bridge records "
    "with preserved source_trace_refs and Trace Spine raw evidence boundaries."
)
BLOCKED_CLAIMS = (
    "no_gcmc_runtime",
    "no_cl_token",
    "no_raw_trace_summarization",
    "no_raw_trace_dump_into_memory_learning_trace",
    "no_concept_id_embedded_into_raw_history",
    "no_internal_action_choice_influence",
    "no_task_action_selection_influence",
    "no_long_term_memory_write",
    "no_core_memory_write",
    "no_external_control",
    "no_first_output",
    "no_live_runtime_session",
)
READINESS_NEXT_PACKAGE = (
    "Package 112 / ASHL Core v1 Host Body Readback Influences Internal Action "
    "Choice Minimal v0"
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


def _slug(text: str | None) -> str:
    safe = [char.lower() if char.isalnum() else "_" for char in str(text or "none")]
    return "_".join("".join(safe).split("_"))[:120] or "empty"


def _get(record: dict[str, Any] | None, key: str, default: Any = None) -> Any:
    if record is None:
        return default
    return record.get(key, default)


def _refs_from(*records: Any) -> tuple[str, ...]:
    refs: list[str] = []
    for item in records:
        record = _record(item)
        if record is None:
            continue
        for key in (
            "source_trace_refs",
            "source_evidence_refs",
            "source_host_body_trace_refs",
            "source_memory_learning_trace_refs",
            "source_memory_routing_trace_refs",
            "source_memory_application_data_refs",
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
class HostBodyWorkingReadbackIntegrationPlanRecord:
    working_readback_integration_plan_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_replay_audit_id: str | None
    source_reviewed_concept_replay_trace_id: str | None
    integration_name: str
    integration_kind: str
    existing_memory_path_required: bool
    existing_working_readback_path_required: bool
    trace_spine_boundary_required: bool
    raw_evidence_boundary_required: bool
    allowed_outputs: tuple[str, ...]
    forbidden_outputs: tuple[str, ...]
    memory_learning_trace_bridge_allowed: bool
    memory_routing_trace_bridge_allowed: bool
    memory_application_data_bridge_allowed: bool
    working_readback_visibility_allowed: bool
    raw_trace_storage_allowed_in_memory_learning_trace: bool
    raw_trace_summarization_allowed: bool
    concept_id_embedding_into_raw_history_allowed: bool
    long_term_memory_write_allowed: bool
    core_memory_write_allowed: bool
    archive_memory_write_allowed: bool
    anchor_write_allowed: bool
    state_persistence_write_allowed: bool
    internal_action_choice_influence_allowed: bool
    task_action_selection_allowed: bool
    external_control_allowed: bool
    first_output_allowed: bool
    live_runtime_session_allowed: bool
    plan_status: str
    plan_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PLAN_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_working_readback_integration_plan_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.integration_name != INTEGRATION_NAME:
            raise ValueError("integration_name must be host_body_reviewed_concept_working_readback_integration")
        if self.integration_kind != INTEGRATION_KIND:
            raise ValueError("integration_kind must be existing_working_readback_path_integration")
        if self.plan_status not in {
            "working_readback_integration_plan_created",
            "blocked_missing_reviewed_concept_replay_audit",
            "blocked_missing_reviewed_concept_replay_trace",
            "blocked_raw_trace_storage_allowed",
            "blocked_raw_trace_summarization_allowed",
            "blocked_concept_id_embedding_allowed",
            "blocked_long_term_memory_write_allowed",
            "blocked_internal_action_choice_influence_allowed",
            "blocked_task_action_selection_allowed",
            "blocked_external_control_allowed",
            "blocked_first_output_allowed",
            "blocked_live_runtime_allowed",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown plan_status: {self.plan_status}")
        for name in ("allowed_outputs", "forbidden_outputs", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyWorkingReadbackIntegrationPlanRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReviewedConceptMemoryLearningTraceBridgeRecord:
    memory_learning_trace_bridge_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_working_readback_integration_plan_id: str
    source_reviewed_concept_readiness_replay_id: str
    bridge_kind: str
    bridge_status: str
    bridge_summary: str
    existing_memory_learning_trace_schema_reused: bool
    target_memory_learning_trace_id: str | None
    reviewed_interpretation_summary: str
    reviewed_concept_scope: str
    host_body_scope_preserved: bool
    counterexample_scope_preserved: bool
    teacher_review_result_preserved: bool
    source_trace_refs: tuple[str, ...]
    source_evidence_refs: tuple[str, ...]
    source_host_body_trace_refs: tuple[str, ...]
    memory_layer_stores_interpretation_only: bool
    source_trace_refs_preserved: bool
    raw_trace_dumped_into_memory_learning_trace: bool
    raw_trace_summarized_during_service_period: bool
    concept_id_embedded_into_raw_history: bool
    long_term_memory_write_performed: bool
    core_memory_write_performed: bool
    archive_memory_write_performed: bool
    anchor_write_performed: bool
    state_persistence_write_performed: bool
    automatic_learning_approval_created: bool
    teacher_approval_created: bool
    action_selection_influence_created: bool
    first_output_created: bool
    live_runtime_session_created: bool

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_LEARNING_TRACE_BRIDGE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_memory_learning_trace_bridge_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.bridge_kind not in {
            "host_body_reviewed_concept_to_memory_learning_trace_bridge",
            "host_body_uncertainty_reviewed_concept_to_memory_learning_trace_bridge",
            "host_body_interesting_event_reviewed_concept_to_memory_learning_trace_bridge",
            "host_body_runtime_bridge_reviewed_concept_to_memory_learning_trace_bridge",
            "blocked_memory_learning_trace_bridge",
        }:
            raise ValueError(f"unknown bridge_kind: {self.bridge_kind}")
        if self.bridge_status not in {
            "memory_learning_trace_bridge_created",
            "memory_learning_trace_bridge_created_existing_schema",
            "memory_learning_trace_bridge_created_bridge_compatible",
            "blocked_invalid_reviewed_concept_readiness",
            "blocked_raw_trace_dump_detected",
            "blocked_raw_trace_summarization_detected",
            "blocked_concept_id_embedded_into_raw_history",
            "blocked_missing_source_trace_refs",
            "blocked_long_term_memory_write_detected",
            "blocked_action_selection_influence_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown bridge_status: {self.bridge_status}")
        for name in ("source_trace_refs", "source_evidence_refs", "source_host_body_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReviewedConceptMemoryLearningTraceBridgeRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReviewedConceptMemoryRoutingTraceBridgeRecord:
    memory_routing_trace_bridge_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_memory_learning_trace_bridge_id: str
    bridge_kind: str
    bridge_status: str
    bridge_summary: str
    existing_memory_routing_trace_schema_reused: bool
    target_memory_routing_trace_id: str | None
    routing_scope: str
    routing_tags: tuple[str, ...]
    host_body_readback_route_enabled: bool
    task_readback_route_enabled: bool
    source_trace_refs: tuple[str, ...]
    source_memory_learning_trace_refs: tuple[str, ...]
    routing_uses_interpretation_not_raw_trace: bool
    raw_trace_copied_into_routing_trace: bool
    concept_id_embedded_into_raw_history: bool
    long_term_memory_write_performed: bool
    core_memory_write_performed: bool
    archive_memory_write_performed: bool
    anchor_write_performed: bool
    action_selection_influence_created: bool
    internal_action_choice_influence_created: bool
    task_action_selection_created: bool
    external_control_created: bool
    first_output_created: bool
    live_runtime_session_created: bool

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_ROUTING_TRACE_BRIDGE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_memory_routing_trace_bridge_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.bridge_status not in {
            "memory_routing_trace_bridge_created",
            "memory_routing_trace_bridge_created_existing_schema",
            "memory_routing_trace_bridge_created_bridge_compatible",
            "blocked_invalid_memory_learning_trace_bridge",
            "blocked_raw_trace_copied_into_routing_trace",
            "blocked_concept_id_embedded_into_raw_history",
            "blocked_long_term_memory_write_detected",
            "blocked_internal_action_choice_influence_detected",
            "blocked_task_action_selection_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown bridge_status: {self.bridge_status}")
        for name in ("routing_tags", "source_trace_refs", "source_memory_learning_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReviewedConceptMemoryRoutingTraceBridgeRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReviewedConceptMemoryApplicationDataBridgeRecord:
    memory_application_data_bridge_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_memory_routing_trace_bridge_id: str
    bridge_kind: str
    bridge_status: str
    bridge_summary: str
    existing_memory_application_data_schema_reused: bool
    target_memory_application_data_id: str | None
    application_scope: str
    readback_hint_summary: str
    host_body_application_tags: tuple[str, ...]
    working_readback_visible: bool
    source_trace_refs: tuple[str, ...]
    source_memory_learning_trace_refs: tuple[str, ...]
    source_memory_routing_trace_refs: tuple[str, ...]
    application_data_stores_interpretation_only: bool
    raw_trace_copied_into_application_data: bool
    concept_id_embedded_into_raw_history: bool
    internal_action_choice_influence_created: bool
    task_action_selection_influence_created: bool
    working_readback_mutated_running_task: bool
    external_control_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    long_term_memory_write_performed: bool
    core_memory_write_performed: bool
    archive_memory_write_performed: bool
    anchor_write_performed: bool

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_APPLICATION_DATA_BRIDGE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_memory_application_data_bridge_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.bridge_status not in {
            "memory_application_data_bridge_created",
            "memory_application_data_bridge_created_existing_schema",
            "memory_application_data_bridge_created_bridge_compatible",
            "blocked_invalid_memory_routing_trace_bridge",
            "blocked_raw_trace_copied_into_application_data",
            "blocked_concept_id_embedded_into_raw_history",
            "blocked_internal_action_choice_influence_detected",
            "blocked_task_action_selection_influence_detected",
            "blocked_running_task_mutation_detected",
            "blocked_long_term_memory_write_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown bridge_status: {self.bridge_status}")
        for name in (
            "host_body_application_tags",
            "source_trace_refs",
            "source_memory_learning_trace_refs",
            "source_memory_routing_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReviewedConceptMemoryApplicationDataBridgeRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyWorkingReadbackVisibilityRecord:
    working_readback_visibility_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_memory_application_data_bridge_id: str
    visibility_kind: str
    visibility_status: str
    visibility_summary: str
    working_readback_visible: bool
    visible_to_future_host_body_context: bool
    visible_to_future_task_context: bool
    readback_payload: dict
    readback_text: str
    source_trace_refs: tuple[str, ...]
    source_memory_application_data_refs: tuple[str, ...]
    readback_payload_contains_raw_trace: bool
    readback_payload_contains_source_refs: bool
    readback_payload_contains_interpretation: bool
    concept_id_embedded_into_raw_history: bool
    internal_action_choice_influence_created: bool
    task_action_selection_influence_created: bool
    candidate_ordering_changed: bool
    selected_action_created: bool
    external_control_created: bool
    first_output_created: bool
    live_runtime_session_created: bool

    def __post_init__(self) -> None:
        if self.schema_version != WORKING_READBACK_VISIBILITY_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_working_readback_visibility_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.visibility_kind not in {
            "host_body_reviewed_concept_working_readback_visibility",
            "host_body_uncertainty_working_readback_visibility",
            "host_body_interesting_event_working_readback_visibility",
            "host_body_runtime_bridge_working_readback_visibility",
            "blocked_visibility",
        }:
            raise ValueError(f"unknown visibility_kind: {self.visibility_kind}")
        if self.visibility_status not in {
            "working_readback_visibility_created",
            "working_readback_visibility_created_for_future_host_body_context",
            "blocked_invalid_memory_application_data_bridge",
            "blocked_raw_trace_in_readback_payload",
            "blocked_missing_source_trace_refs",
            "blocked_concept_id_embedded_into_raw_history",
            "blocked_internal_action_choice_influence_detected",
            "blocked_task_action_selection_influence_detected",
            "blocked_candidate_ordering_changed",
            "blocked_selected_action_created",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown visibility_status: {self.visibility_status}")
        for name in ("source_trace_refs", "source_memory_application_data_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyWorkingReadbackVisibilityRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class TraceSpineRawEvidenceBoundaryRecord:
    trace_spine_boundary_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_working_readback_integration_plan_id: str | None
    boundary_kind: str
    boundary_status: str
    boundary_summary: str
    gcmc_document_added_as_future_age_architecture: bool
    gcmc_runtime_implemented: bool
    cl_token_created: bool
    concept_compiler_created: bool
    pattern_miner_created: bool
    formed_under_assumption_required_now: bool
    trace_spine_format_unified: bool
    trace_spine_time_aligned: bool
    raw_trace_append_only_confirmed: bool
    raw_trace_summarized_during_service_period: bool
    memory_layer_stores_interpretation_only: bool
    source_trace_refs_preserved: bool
    concept_id_embedded_into_raw_history: bool
    raw_trace_dumped_into_memory_learning_trace: bool
    future_cl_ore_preserved: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TRACE_SPINE_BOUNDARY_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_trace_spine_raw_evidence_boundary_v1")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.boundary_status not in {
            "passed_trace_spine_raw_evidence_boundary",
            "blocked_gcmc_runtime_implemented",
            "blocked_cl_token_created",
            "blocked_trace_spine_format_not_unified",
            "blocked_trace_spine_time_not_aligned",
            "blocked_raw_trace_not_append_only",
            "blocked_raw_trace_summarized",
            "blocked_memory_layer_not_interpretation_only",
            "blocked_missing_source_trace_refs",
            "blocked_concept_id_embedded_into_raw_history",
            "blocked_raw_trace_dumped_into_memory_learning_trace",
            "blocked_future_cl_ore_polluted",
        }:
            raise ValueError(f"unknown boundary_status: {self.boundary_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TraceSpineRawEvidenceBoundaryRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyWorkingReadbackIntegrationTraceRecord:
    working_readback_integration_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_working_readback_integration_plan_id: str
    memory_learning_trace_bridge_ids: tuple[str, ...]
    memory_routing_trace_bridge_ids: tuple[str, ...]
    memory_application_data_bridge_ids: tuple[str, ...]
    working_readback_visibility_ids: tuple[str, ...]
    trace_spine_boundary_ids: tuple[str, ...]
    trace_kind: str
    trace_status: str
    trace_summary: str
    memory_learning_trace_bridge_count: int
    memory_routing_trace_bridge_count: int
    memory_application_data_bridge_count: int
    working_readback_visibility_count: int
    working_readback_visible_count: int
    trace_spine_boundary_confirmed: bool
    raw_evidence_boundary_confirmed: bool
    memory_layer_interpretation_only_confirmed: bool
    source_trace_refs_preserved_confirmed: bool
    concept_id_not_embedded_into_raw_history_confirmed: bool
    internal_action_choice_influence_created: bool
    task_action_selection_influence_created: bool
    candidate_ordering_changed: bool
    selected_action_created: bool
    long_term_memory_write_performed: bool
    core_memory_write_performed: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INTEGRATION_TRACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_working_readback_integration_trace_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.trace_status not in {
            "host_body_working_readback_integration_trace_recorded",
            "host_body_working_readback_integration_trace_recorded_empty",
            "blocked_invalid_memory_learning_trace_bridge",
            "blocked_invalid_memory_routing_trace_bridge",
            "blocked_invalid_memory_application_data_bridge",
            "blocked_invalid_working_readback_visibility",
            "blocked_trace_spine_boundary_failure",
            "blocked_internal_action_choice_influence_detected",
            "blocked_task_action_selection_influence_detected",
            "blocked_candidate_ordering_changed",
            "blocked_long_term_memory_write_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown trace_status: {self.trace_status}")
        for name in (
            "memory_learning_trace_bridge_ids",
            "memory_routing_trace_bridge_ids",
            "memory_application_data_bridge_ids",
            "working_readback_visibility_ids",
            "trace_spine_boundary_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyWorkingReadbackIntegrationTraceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyWorkingReadbackIntegrationAudit:
    working_readback_integration_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_working_readback_integration_plan_id: str | None
    source_working_readback_integration_trace_id: str | None
    source_trace_spine_boundary_id: str | None
    integration_plan_valid: bool
    memory_learning_trace_bridges_valid: bool
    memory_routing_trace_bridges_valid: bool
    memory_application_data_bridges_valid: bool
    working_readback_visibility_valid: bool
    trace_spine_boundary_valid: bool
    integration_trace_valid: bool
    host_body_reviewed_concept_replay_confirmed: bool
    existing_memory_path_reuse_confirmed: bool
    working_readback_visibility_confirmed: bool
    trace_spine_format_unified_confirmed: bool
    trace_spine_time_aligned_confirmed: bool
    raw_trace_append_only_confirmed: bool
    raw_trace_not_summarized_during_service_period: bool
    memory_layer_stores_interpretation_only_confirmed: bool
    source_trace_refs_preserved_confirmed: bool
    concept_id_not_embedded_into_raw_history_confirmed: bool
    raw_trace_not_dumped_into_memory_learning_trace_confirmed: bool
    gcmc_docs_only_future_architecture_confirmed: bool
    gcmc_runtime_not_implemented_confirmed: bool
    cl_token_not_created_confirmed: bool
    no_internal_action_choice_influence: bool
    no_task_action_selection_influence: bool
    no_task_selected_action: bool
    no_final_action: bool
    no_direct_command: bool
    no_sandbox_execution: bool
    no_long_term_memory_write: bool
    no_core_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_state_persistence_write: bool
    no_external_control: bool
    no_real_hardware_access: bool
    no_semantic_vision: bool
    no_speech_recognition: bool
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
            raise ValueError("schema_version must be qingyin_host_body_working_readback_integration_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.audit_status not in {
            "passed_host_body_reviewed_concept_working_readback_integration",
            "passed_trace_spine_raw_evidence_boundary",
            "passed_gcmc_docs_only_future_architecture",
            "blocked_missing_working_readback_integration_plan",
            "blocked_invalid_memory_learning_trace_bridge",
            "blocked_invalid_memory_routing_trace_bridge",
            "blocked_invalid_memory_application_data_bridge",
            "blocked_invalid_working_readback_visibility",
            "blocked_trace_spine_boundary_failure",
            "blocked_raw_trace_summarized",
            "blocked_raw_trace_dumped_into_memory_learning_trace",
            "blocked_concept_id_embedded_into_raw_history",
            "blocked_missing_source_trace_refs",
            "blocked_gcmc_runtime_implemented",
            "blocked_cl_token_created",
            "blocked_internal_action_choice_influence_detected",
            "blocked_task_action_selection_influence_detected",
            "blocked_long_term_memory_write_detected",
            "blocked_core_memory_write_detected",
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
    def from_dict(cls, data: dict[str, object]) -> "HostBodyWorkingReadbackIntegrationAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyWorkingReadbackIntegrationReadinessRecord:
    working_readback_integration_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_working_readback_integration_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_host_body_readback_internal_action_influence: bool
    ready_for_host_body_closed_loop_milestone_audit: bool
    ready_for_bounded_embodied_loop_runner: bool
    ready_for_long_term_memory_write: bool
    ready_for_core_memory_write: bool
    ready_for_raw_trace_summarization: bool
    ready_for_cl_token_creation: bool
    ready_for_gcmc_runtime: bool
    ready_for_task_action_selection_influence: bool
    ready_for_external_control: bool
    ready_for_first_output: bool
    ready_for_live_runtime_session: bool
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READINESS_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_working_readback_integration_readiness_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.readiness_status not in {
            "ready_for_host_body_readback_internal_action_influence_only",
            "ready_for_host_body_closed_loop_milestone_audit_only",
            "ready_for_bounded_embodied_loop_runner_only",
            "not_ready_missing_working_readback_integration_audit",
            "not_ready_boundary_failure",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyWorkingReadbackIntegrationReadinessRecord":
        return cls(**dict(data))


def build_host_body_working_readback_integration_plan(
    *,
    reviewed_concept_replay_audit: Any,
    reviewed_concept_replay_trace: Any,
    existing_memory_path_required: bool = True,
    existing_working_readback_path_required: bool = True,
    trace_spine_boundary_required: bool = True,
    raw_evidence_boundary_required: bool = True,
    raw_trace_storage_allowed_in_memory_learning_trace: bool = False,
    raw_trace_summarization_allowed: bool = False,
    concept_id_embedding_into_raw_history_allowed: bool = False,
    long_term_memory_write_allowed: bool = False,
    core_memory_write_allowed: bool = False,
    archive_memory_write_allowed: bool = False,
    anchor_write_allowed: bool = False,
    state_persistence_write_allowed: bool = False,
    internal_action_choice_influence_allowed: bool = False,
    task_action_selection_allowed: bool = False,
    external_control_allowed: bool = False,
    first_output_allowed: bool = False,
    live_runtime_session_allowed: bool = False,
) -> HostBodyWorkingReadbackIntegrationPlanRecord:
    audit = _record(reviewed_concept_replay_audit)
    trace = _record(reviewed_concept_replay_trace)
    status = "working_readback_integration_plan_created"
    if audit is None:
        status = "blocked_missing_reviewed_concept_replay_audit"
    elif trace is None:
        status = "blocked_missing_reviewed_concept_replay_trace"
    elif not all((
        existing_memory_path_required,
        existing_working_readback_path_required,
        trace_spine_boundary_required,
        raw_evidence_boundary_required,
    )):
        status = "blocked_forbidden_authority_detected"
    elif raw_trace_storage_allowed_in_memory_learning_trace:
        status = "blocked_raw_trace_storage_allowed"
    elif raw_trace_summarization_allowed:
        status = "blocked_raw_trace_summarization_allowed"
    elif concept_id_embedding_into_raw_history_allowed:
        status = "blocked_concept_id_embedding_allowed"
    elif any((
        long_term_memory_write_allowed,
        core_memory_write_allowed,
        archive_memory_write_allowed,
        anchor_write_allowed,
        state_persistence_write_allowed,
    )):
        status = "blocked_long_term_memory_write_allowed"
    elif internal_action_choice_influence_allowed:
        status = "blocked_internal_action_choice_influence_allowed"
    elif task_action_selection_allowed:
        status = "blocked_task_action_selection_allowed"
    elif external_control_allowed:
        status = "blocked_external_control_allowed"
    elif first_output_allowed:
        status = "blocked_first_output_allowed"
    elif live_runtime_session_allowed:
        status = "blocked_live_runtime_allowed"
    source_refs = _refs_from(audit, trace)
    return HostBodyWorkingReadbackIntegrationPlanRecord(
        working_readback_integration_plan_id=f"host_body_working_readback_integration_plan:{status}",
        schema_version=PLAN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_replay_audit_id=_get(audit, "reviewed_concept_replay_audit_id"),
        source_reviewed_concept_replay_trace_id=_get(trace, "reviewed_concept_replay_trace_id"),
        integration_name=INTEGRATION_NAME,
        integration_kind=INTEGRATION_KIND,
        existing_memory_path_required=existing_memory_path_required,
        existing_working_readback_path_required=existing_working_readback_path_required,
        trace_spine_boundary_required=trace_spine_boundary_required,
        raw_evidence_boundary_required=raw_evidence_boundary_required,
        allowed_outputs=ALLOWED_OUTPUTS,
        forbidden_outputs=FORBIDDEN_OUTPUTS,
        memory_learning_trace_bridge_allowed=True,
        memory_routing_trace_bridge_allowed=True,
        memory_application_data_bridge_allowed=True,
        working_readback_visibility_allowed=True,
        raw_trace_storage_allowed_in_memory_learning_trace=raw_trace_storage_allowed_in_memory_learning_trace,
        raw_trace_summarization_allowed=raw_trace_summarization_allowed,
        concept_id_embedding_into_raw_history_allowed=concept_id_embedding_into_raw_history_allowed,
        long_term_memory_write_allowed=long_term_memory_write_allowed,
        core_memory_write_allowed=core_memory_write_allowed,
        archive_memory_write_allowed=archive_memory_write_allowed,
        anchor_write_allowed=anchor_write_allowed,
        state_persistence_write_allowed=state_persistence_write_allowed,
        internal_action_choice_influence_allowed=internal_action_choice_influence_allowed,
        task_action_selection_allowed=task_action_selection_allowed,
        external_control_allowed=external_control_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
        plan_status=status,
        plan_summary=_plan_summary(status),
        source_trace_refs=source_refs,
    )


def validate_host_body_working_readback_integration_plan(
    plan: Any,
) -> dict[str, object]:
    record = _record(plan)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["plan_status"]),
        {"working_readback_integration_plan_created"},
    )


def build_host_body_memory_learning_trace_bridge(
    *,
    working_readback_integration_plan: Any,
    reviewed_concept_readiness_replay: Any,
    existing_memory_learning_trace_schema_reused: bool = False,
    target_memory_learning_trace_id: str | None = None,
    raw_trace_dumped_into_memory_learning_trace: bool = False,
    raw_trace_summarized_during_service_period: bool = False,
    concept_id_embedded_into_raw_history: bool = False,
    source_trace_refs_preserved: bool = True,
    long_term_memory_write_performed: bool = False,
    core_memory_write_performed: bool = False,
    archive_memory_write_performed: bool = False,
    anchor_write_performed: bool = False,
    state_persistence_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    teacher_approval_created: bool = False,
    action_selection_influence_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyReviewedConceptMemoryLearningTraceBridgeRecord:
    plan = _record(working_readback_integration_plan)
    readiness = _record(reviewed_concept_readiness_replay)
    readiness_valid = bool(
        readiness
        and readiness.get("reviewed_concept_replay_status")
        == "host_body_reviewed_concept_readiness_replay_ready"
        and readiness.get("reviewed_concept_ready") is True
    )
    source_refs = tuple(str(ref) for ref in (readiness or {}).get("source_trace_refs", ()) or ())
    status = "memory_learning_trace_bridge_created"
    if not readiness_valid:
        status = "blocked_invalid_reviewed_concept_readiness"
    elif raw_trace_dumped_into_memory_learning_trace:
        status = "blocked_raw_trace_dump_detected"
    elif raw_trace_summarized_during_service_period:
        status = "blocked_raw_trace_summarization_detected"
    elif concept_id_embedded_into_raw_history:
        status = "blocked_concept_id_embedded_into_raw_history"
    elif not source_refs or not source_trace_refs_preserved:
        status = "blocked_missing_source_trace_refs"
    elif any((
        long_term_memory_write_performed,
        core_memory_write_performed,
        archive_memory_write_performed,
        anchor_write_performed,
        state_persistence_write_performed,
    )):
        status = "blocked_long_term_memory_write_detected"
    elif action_selection_influence_created:
        status = "blocked_action_selection_influence_detected"
    elif first_output_created:
        status = "blocked_first_output_detected"
    elif live_runtime_session_created:
        status = "blocked_live_runtime_detected"
    elif existing_memory_learning_trace_schema_reused:
        status = "memory_learning_trace_bridge_created_existing_schema"
    elif not existing_memory_learning_trace_schema_reused:
        status = "memory_learning_trace_bridge_created"
    bridge_kind = _memory_learning_trace_bridge_kind(_get(readiness, "reviewed_concept_replay_kind"))
    if status.startswith("blocked_"):
        bridge_kind = "blocked_memory_learning_trace_bridge"
    bridge_id = f"host_body_memory_learning_trace_bridge:{_slug(bridge_kind)}:{status}"
    source_evidence_refs = (
        str(_get(readiness, "reviewed_concept_readiness_replay_id")),
        str(_get(readiness, "source_concept_candidate_refinement_replay_id")),
    )
    return HostBodyReviewedConceptMemoryLearningTraceBridgeRecord(
        memory_learning_trace_bridge_id=bridge_id,
        schema_version=MEMORY_LEARNING_TRACE_BRIDGE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_working_readback_integration_plan_id=str(_get(plan, "working_readback_integration_plan_id")),
        source_reviewed_concept_readiness_replay_id=str(_get(readiness, "reviewed_concept_readiness_replay_id")),
        bridge_kind=bridge_kind,
        bridge_status=status,
        bridge_summary=_memory_learning_bridge_summary(status),
        existing_memory_learning_trace_schema_reused=existing_memory_learning_trace_schema_reused,
        target_memory_learning_trace_id=target_memory_learning_trace_id,
        reviewed_interpretation_summary=str(_get(readiness, "reviewed_concept_replay_summary", "")),
        reviewed_concept_scope=_scope_from_kind(_get(readiness, "reviewed_concept_replay_kind")),
        host_body_scope_preserved=bool(_get(readiness, "host_body_scope_preserved", True)),
        counterexample_scope_preserved=bool(_get(readiness, "counterexample_scope_preserved", True)),
        teacher_review_result_preserved=bool(_get(readiness, "teacher_review_result_preserved", True)),
        source_trace_refs=source_refs,
        source_evidence_refs=tuple(ref for ref in source_evidence_refs if ref and ref != "None"),
        source_host_body_trace_refs=tuple(ref for ref in source_refs if "host_body" in ref),
        memory_layer_stores_interpretation_only=True,
        source_trace_refs_preserved=source_trace_refs_preserved,
        raw_trace_dumped_into_memory_learning_trace=raw_trace_dumped_into_memory_learning_trace,
        raw_trace_summarized_during_service_period=raw_trace_summarized_during_service_period,
        concept_id_embedded_into_raw_history=concept_id_embedded_into_raw_history,
        long_term_memory_write_performed=long_term_memory_write_performed,
        core_memory_write_performed=core_memory_write_performed,
        archive_memory_write_performed=archive_memory_write_performed,
        anchor_write_performed=anchor_write_performed,
        state_persistence_write_performed=state_persistence_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        teacher_approval_created=teacher_approval_created,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )


def validate_host_body_memory_learning_trace_bridge(bridge: Any) -> dict[str, object]:
    record = _record(bridge)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["bridge_status"]),
        {
            "memory_learning_trace_bridge_created",
            "memory_learning_trace_bridge_created_existing_schema",
            "memory_learning_trace_bridge_created_bridge_compatible",
        },
    )


def build_host_body_memory_routing_trace_bridge(
    *,
    memory_learning_trace_bridge: Any,
    existing_memory_routing_trace_schema_reused: bool = False,
    target_memory_routing_trace_id: str | None = None,
    raw_trace_copied_into_routing_trace: bool = False,
    concept_id_embedded_into_raw_history: bool = False,
    long_term_memory_write_performed: bool = False,
    core_memory_write_performed: bool = False,
    archive_memory_write_performed: bool = False,
    anchor_write_performed: bool = False,
    action_selection_influence_created: bool = False,
    internal_action_choice_influence_created: bool = False,
    task_action_selection_created: bool = False,
    external_control_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyReviewedConceptMemoryRoutingTraceBridgeRecord:
    learning = _record(memory_learning_trace_bridge)
    learning_valid = validate_host_body_memory_learning_trace_bridge(learning)["valid"] if learning else False
    status = "memory_routing_trace_bridge_created"
    if not learning_valid:
        status = "blocked_invalid_memory_learning_trace_bridge"
    elif raw_trace_copied_into_routing_trace:
        status = "blocked_raw_trace_copied_into_routing_trace"
    elif concept_id_embedded_into_raw_history:
        status = "blocked_concept_id_embedded_into_raw_history"
    elif any((
        long_term_memory_write_performed,
        core_memory_write_performed,
        archive_memory_write_performed,
        anchor_write_performed,
    )):
        status = "blocked_long_term_memory_write_detected"
    elif internal_action_choice_influence_created or action_selection_influence_created:
        status = "blocked_internal_action_choice_influence_detected"
    elif task_action_selection_created:
        status = "blocked_task_action_selection_detected"
    elif first_output_created:
        status = "blocked_first_output_detected"
    elif live_runtime_session_created:
        status = "blocked_live_runtime_detected"
    elif existing_memory_routing_trace_schema_reused:
        status = "memory_routing_trace_bridge_created_existing_schema"
    source_refs = _refs_from(learning)
    return HostBodyReviewedConceptMemoryRoutingTraceBridgeRecord(
        memory_routing_trace_bridge_id=f"host_body_memory_routing_trace_bridge:{status}:{_slug(_get(learning, 'bridge_kind'))}",
        schema_version=MEMORY_ROUTING_TRACE_BRIDGE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_memory_learning_trace_bridge_id=str(_get(learning, "memory_learning_trace_bridge_id")),
        bridge_kind="host_body_reviewed_concept_to_memory_routing_trace_bridge",
        bridge_status=status,
        bridge_summary=_routing_bridge_summary(status),
        existing_memory_routing_trace_schema_reused=existing_memory_routing_trace_schema_reused,
        target_memory_routing_trace_id=target_memory_routing_trace_id,
        routing_scope="host_body_working_readback_visibility",
        routing_tags=("host_body", "reviewed_concept", "working_readback_visibility"),
        host_body_readback_route_enabled=True,
        task_readback_route_enabled=False,
        source_trace_refs=source_refs,
        source_memory_learning_trace_refs=(str(_get(learning, "memory_learning_trace_bridge_id")),),
        routing_uses_interpretation_not_raw_trace=True,
        raw_trace_copied_into_routing_trace=raw_trace_copied_into_routing_trace,
        concept_id_embedded_into_raw_history=concept_id_embedded_into_raw_history,
        long_term_memory_write_performed=long_term_memory_write_performed,
        core_memory_write_performed=core_memory_write_performed,
        archive_memory_write_performed=archive_memory_write_performed,
        anchor_write_performed=anchor_write_performed,
        action_selection_influence_created=action_selection_influence_created,
        internal_action_choice_influence_created=internal_action_choice_influence_created,
        task_action_selection_created=task_action_selection_created,
        external_control_created=external_control_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )


def validate_host_body_memory_routing_trace_bridge(bridge: Any) -> dict[str, object]:
    record = _record(bridge)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["bridge_status"]),
        {
            "memory_routing_trace_bridge_created",
            "memory_routing_trace_bridge_created_existing_schema",
            "memory_routing_trace_bridge_created_bridge_compatible",
        },
    )


def build_host_body_memory_application_data_bridge(
    *,
    memory_routing_trace_bridge: Any,
    existing_memory_application_data_schema_reused: bool = False,
    target_memory_application_data_id: str | None = None,
    raw_trace_copied_into_application_data: bool = False,
    concept_id_embedded_into_raw_history: bool = False,
    internal_action_choice_influence_created: bool = False,
    task_action_selection_influence_created: bool = False,
    working_readback_mutated_running_task: bool = False,
    external_control_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
    long_term_memory_write_performed: bool = False,
    core_memory_write_performed: bool = False,
    archive_memory_write_performed: bool = False,
    anchor_write_performed: bool = False,
) -> HostBodyReviewedConceptMemoryApplicationDataBridgeRecord:
    routing = _record(memory_routing_trace_bridge)
    routing_valid = validate_host_body_memory_routing_trace_bridge(routing)["valid"] if routing else False
    status = "memory_application_data_bridge_created"
    if not routing_valid:
        status = "blocked_invalid_memory_routing_trace_bridge"
    elif raw_trace_copied_into_application_data:
        status = "blocked_raw_trace_copied_into_application_data"
    elif concept_id_embedded_into_raw_history:
        status = "blocked_concept_id_embedded_into_raw_history"
    elif internal_action_choice_influence_created:
        status = "blocked_internal_action_choice_influence_detected"
    elif task_action_selection_influence_created:
        status = "blocked_task_action_selection_influence_detected"
    elif working_readback_mutated_running_task:
        status = "blocked_running_task_mutation_detected"
    elif any((
        long_term_memory_write_performed,
        core_memory_write_performed,
        archive_memory_write_performed,
        anchor_write_performed,
    )):
        status = "blocked_long_term_memory_write_detected"
    elif first_output_created:
        status = "blocked_first_output_detected"
    elif live_runtime_session_created:
        status = "blocked_live_runtime_detected"
    elif existing_memory_application_data_schema_reused:
        status = "memory_application_data_bridge_created_existing_schema"
    source_refs = _refs_from(routing)
    return HostBodyReviewedConceptMemoryApplicationDataBridgeRecord(
        memory_application_data_bridge_id=f"host_body_memory_application_data_bridge:{status}:{_slug(_get(routing, 'memory_routing_trace_bridge_id'))}",
        schema_version=MEMORY_APPLICATION_DATA_BRIDGE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_memory_routing_trace_bridge_id=str(_get(routing, "memory_routing_trace_bridge_id")),
        bridge_kind="host_body_reviewed_concept_to_memory_application_data_bridge",
        bridge_status=status,
        bridge_summary=_application_bridge_summary(status),
        existing_memory_application_data_schema_reused=existing_memory_application_data_schema_reused,
        target_memory_application_data_id=target_memory_application_data_id,
        application_scope="host_body_reviewed_concept_working_readback",
        readback_hint_summary="Host Body reviewed concept interpretation is visible to future Host Body context only.",
        host_body_application_tags=("host_body", "reviewed_concept", "future_host_body_context"),
        working_readback_visible=True,
        source_trace_refs=source_refs,
        source_memory_learning_trace_refs=tuple(str(ref) for ref in _get(routing, "source_memory_learning_trace_refs", ()) or ()),
        source_memory_routing_trace_refs=(str(_get(routing, "memory_routing_trace_bridge_id")),),
        application_data_stores_interpretation_only=True,
        raw_trace_copied_into_application_data=raw_trace_copied_into_application_data,
        concept_id_embedded_into_raw_history=concept_id_embedded_into_raw_history,
        internal_action_choice_influence_created=internal_action_choice_influence_created,
        task_action_selection_influence_created=task_action_selection_influence_created,
        working_readback_mutated_running_task=working_readback_mutated_running_task,
        external_control_created=external_control_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        long_term_memory_write_performed=long_term_memory_write_performed,
        core_memory_write_performed=core_memory_write_performed,
        archive_memory_write_performed=archive_memory_write_performed,
        anchor_write_performed=anchor_write_performed,
    )


def validate_host_body_memory_application_data_bridge(bridge: Any) -> dict[str, object]:
    record = _record(bridge)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["bridge_status"]),
        {
            "memory_application_data_bridge_created",
            "memory_application_data_bridge_created_existing_schema",
            "memory_application_data_bridge_created_bridge_compatible",
        },
    )


def build_host_body_working_readback_visibility(
    *,
    memory_application_data_bridge: Any,
    readback_payload_contains_raw_trace: bool = False,
    readback_payload_contains_source_refs: bool = True,
    readback_payload_contains_interpretation: bool = True,
    concept_id_embedded_into_raw_history: bool = False,
    internal_action_choice_influence_created: bool = False,
    task_action_selection_influence_created: bool = False,
    candidate_ordering_changed: bool = False,
    selected_action_created: bool = False,
    external_control_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyWorkingReadbackVisibilityRecord:
    app = _record(memory_application_data_bridge)
    app_valid = validate_host_body_memory_application_data_bridge(app)["valid"] if app else False
    source_refs = _refs_from(app)
    status = "working_readback_visibility_created_for_future_host_body_context"
    if not app_valid:
        status = "blocked_invalid_memory_application_data_bridge"
    elif readback_payload_contains_raw_trace:
        status = "blocked_raw_trace_in_readback_payload"
    elif not source_refs or not readback_payload_contains_source_refs:
        status = "blocked_missing_source_trace_refs"
    elif concept_id_embedded_into_raw_history:
        status = "blocked_concept_id_embedded_into_raw_history"
    elif internal_action_choice_influence_created:
        status = "blocked_internal_action_choice_influence_detected"
    elif task_action_selection_influence_created:
        status = "blocked_task_action_selection_influence_detected"
    elif candidate_ordering_changed:
        status = "blocked_candidate_ordering_changed"
    elif selected_action_created:
        status = "blocked_selected_action_created"
    elif first_output_created:
        status = "blocked_first_output_detected"
    elif live_runtime_session_created:
        status = "blocked_live_runtime_detected"
    visibility_kind = _visibility_kind_from_refs(source_refs)
    if status.startswith("blocked_"):
        visibility_kind = "blocked_visibility"
    payload = {
        "interpretation": str(_get(app, "readback_hint_summary", "")),
        "source_trace_refs": list(source_refs),
        "raw_trace": None,
        "visible_to_future_host_body_context": True,
        "visible_to_future_task_context": False,
    }
    return HostBodyWorkingReadbackVisibilityRecord(
        working_readback_visibility_id=f"host_body_working_readback_visibility:{_slug(visibility_kind)}:{status}",
        schema_version=WORKING_READBACK_VISIBILITY_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_memory_application_data_bridge_id=str(_get(app, "memory_application_data_bridge_id")),
        visibility_kind=visibility_kind,
        visibility_status=status,
        visibility_summary=_visibility_summary(status),
        working_readback_visible=True,
        visible_to_future_host_body_context=True,
        visible_to_future_task_context=False,
        readback_payload=payload,
        readback_text="Host Body reviewed learning is visible as interpretation-only future Host Body context.",
        source_trace_refs=source_refs,
        source_memory_application_data_refs=(str(_get(app, "memory_application_data_bridge_id")),),
        readback_payload_contains_raw_trace=readback_payload_contains_raw_trace,
        readback_payload_contains_source_refs=readback_payload_contains_source_refs,
        readback_payload_contains_interpretation=readback_payload_contains_interpretation,
        concept_id_embedded_into_raw_history=concept_id_embedded_into_raw_history,
        internal_action_choice_influence_created=internal_action_choice_influence_created,
        task_action_selection_influence_created=task_action_selection_influence_created,
        candidate_ordering_changed=candidate_ordering_changed,
        selected_action_created=selected_action_created,
        external_control_created=external_control_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )


def validate_host_body_working_readback_visibility(visibility: Any) -> dict[str, object]:
    record = _record(visibility)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["visibility_status"]),
        {
            "working_readback_visibility_created",
            "working_readback_visibility_created_for_future_host_body_context",
        },
    )


def build_trace_spine_raw_evidence_boundary(
    *,
    working_readback_integration_plan: Any | None = None,
    gcmc_runtime_implemented: bool = False,
    cl_token_created: bool = False,
    concept_compiler_created: bool = False,
    pattern_miner_created: bool = False,
    formed_under_assumption_required_now: bool = False,
    trace_spine_format_unified: bool = TRACE_SPINE_FORMAT_UNIFIED,
    trace_spine_time_aligned: bool = TRACE_SPINE_TIME_ALIGNED,
    raw_trace_append_only_confirmed: bool = RAW_TRACE_APPEND_ONLY_CONFIRMED,
    raw_trace_summarized_during_service_period: bool = RAW_TRACE_SUMMARIZED_DURING_SERVICE_PERIOD,
    memory_layer_stores_interpretation_only: bool = MEMORY_LAYER_STORES_INTERPRETATION_ONLY,
    source_trace_refs_preserved: bool = SOURCE_TRACE_REFS_PRESERVED,
    concept_id_embedded_into_raw_history: bool = CONCEPT_ID_EMBEDDED_INTO_RAW_HISTORY,
    raw_trace_dumped_into_memory_learning_trace: bool = RAW_TRACE_DUMPED_INTO_MEMORY_LEARNING_TRACE,
    future_cl_ore_preserved: bool = True,
) -> TraceSpineRawEvidenceBoundaryRecord:
    plan = _record(working_readback_integration_plan)
    source_refs = _refs_from(plan) or ("trace_spine_raw_evidence_boundary:v1",)
    status = "passed_trace_spine_raw_evidence_boundary"
    if gcmc_runtime_implemented:
        status = "blocked_gcmc_runtime_implemented"
    elif cl_token_created:
        status = "blocked_cl_token_created"
    elif concept_compiler_created or pattern_miner_created or formed_under_assumption_required_now:
        status = "blocked_future_cl_ore_polluted"
    elif not trace_spine_format_unified:
        status = "blocked_trace_spine_format_not_unified"
    elif not trace_spine_time_aligned:
        status = "blocked_trace_spine_time_not_aligned"
    elif not raw_trace_append_only_confirmed:
        status = "blocked_raw_trace_not_append_only"
    elif raw_trace_summarized_during_service_period:
        status = "blocked_raw_trace_summarized"
    elif not memory_layer_stores_interpretation_only:
        status = "blocked_memory_layer_not_interpretation_only"
    elif not source_trace_refs_preserved:
        status = "blocked_missing_source_trace_refs"
    elif concept_id_embedded_into_raw_history:
        status = "blocked_concept_id_embedded_into_raw_history"
    elif raw_trace_dumped_into_memory_learning_trace:
        status = "blocked_raw_trace_dumped_into_memory_learning_trace"
    elif not future_cl_ore_preserved:
        status = "blocked_future_cl_ore_polluted"
    return TraceSpineRawEvidenceBoundaryRecord(
        trace_spine_boundary_id=f"trace_spine_raw_evidence_boundary:{status}",
        schema_version=TRACE_SPINE_BOUNDARY_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_working_readback_integration_plan_id=_get(plan, "working_readback_integration_plan_id"),
        boundary_kind="qingyin_v1_trace_spine_raw_evidence_boundary",
        boundary_status=status,
        boundary_summary=_trace_spine_boundary_summary(status),
        gcmc_document_added_as_future_age_architecture=True,
        gcmc_runtime_implemented=gcmc_runtime_implemented,
        cl_token_created=cl_token_created,
        concept_compiler_created=concept_compiler_created,
        pattern_miner_created=pattern_miner_created,
        formed_under_assumption_required_now=formed_under_assumption_required_now,
        trace_spine_format_unified=trace_spine_format_unified,
        trace_spine_time_aligned=trace_spine_time_aligned,
        raw_trace_append_only_confirmed=raw_trace_append_only_confirmed,
        raw_trace_summarized_during_service_period=raw_trace_summarized_during_service_period,
        memory_layer_stores_interpretation_only=memory_layer_stores_interpretation_only,
        source_trace_refs_preserved=source_trace_refs_preserved,
        concept_id_embedded_into_raw_history=concept_id_embedded_into_raw_history,
        raw_trace_dumped_into_memory_learning_trace=raw_trace_dumped_into_memory_learning_trace,
        future_cl_ore_preserved=future_cl_ore_preserved,
        source_trace_refs=source_refs,
    )


def validate_trace_spine_raw_evidence_boundary(boundary: Any) -> dict[str, object]:
    record = _record(boundary)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(str(record["boundary_status"]), {"passed_trace_spine_raw_evidence_boundary"})


def build_host_body_working_readback_integration_trace(
    *,
    working_readback_integration_plan: Any,
    memory_learning_trace_bridges: tuple[Any, ...] | list[Any] = (),
    memory_routing_trace_bridges: tuple[Any, ...] | list[Any] = (),
    memory_application_data_bridges: tuple[Any, ...] | list[Any] = (),
    working_readback_visibility_records: tuple[Any, ...] | list[Any] = (),
    trace_spine_boundary_records: tuple[Any, ...] | list[Any] = (),
    internal_action_choice_influence_created: bool = False,
    task_action_selection_influence_created: bool = False,
    candidate_ordering_changed: bool = False,
    selected_action_created: bool = False,
    long_term_memory_write_performed: bool = False,
    core_memory_write_performed: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyWorkingReadbackIntegrationTraceRecord:
    plan = _record(working_readback_integration_plan)
    learning = tuple(_record(item) for item in memory_learning_trace_bridges)
    routing = tuple(_record(item) for item in memory_routing_trace_bridges)
    application = tuple(_record(item) for item in memory_application_data_bridges)
    visibility = tuple(_record(item) for item in working_readback_visibility_records)
    boundaries = tuple(_record(item) for item in trace_spine_boundary_records)
    status = "host_body_working_readback_integration_trace_recorded"
    if any(not validate_host_body_memory_learning_trace_bridge(item)["valid"] for item in learning):
        status = "blocked_invalid_memory_learning_trace_bridge"
    elif any(not validate_host_body_memory_routing_trace_bridge(item)["valid"] for item in routing):
        status = "blocked_invalid_memory_routing_trace_bridge"
    elif any(not validate_host_body_memory_application_data_bridge(item)["valid"] for item in application):
        status = "blocked_invalid_memory_application_data_bridge"
    elif any(not validate_host_body_working_readback_visibility(item)["valid"] for item in visibility):
        status = "blocked_invalid_working_readback_visibility"
    elif any(not validate_trace_spine_raw_evidence_boundary(item)["valid"] for item in boundaries):
        status = "blocked_trace_spine_boundary_failure"
    elif internal_action_choice_influence_created:
        status = "blocked_internal_action_choice_influence_detected"
    elif task_action_selection_influence_created or selected_action_created:
        status = "blocked_task_action_selection_influence_detected"
    elif candidate_ordering_changed:
        status = "blocked_candidate_ordering_changed"
    elif long_term_memory_write_performed or core_memory_write_performed:
        status = "blocked_long_term_memory_write_detected"
    elif first_output_created:
        status = "blocked_first_output_detected"
    elif live_runtime_session_created:
        status = "blocked_live_runtime_detected"
    elif not learning and not routing and not application and not visibility:
        status = "host_body_working_readback_integration_trace_recorded_empty"
    trace_kind = "single_host_body_reviewed_concept_working_readback"
    if len(visibility) > 1:
        trace_kind = "mixed_host_body_reviewed_concept_working_readback"
    if not visibility:
        trace_kind = "empty_host_body_reviewed_concept_working_readback"
    if status.startswith("blocked_"):
        trace_kind = "blocked_host_body_reviewed_concept_working_readback"
    source_refs = _refs_from(plan, *learning, *routing, *application, *visibility, *boundaries)
    return HostBodyWorkingReadbackIntegrationTraceRecord(
        working_readback_integration_trace_id=f"host_body_working_readback_integration_trace:{status}:{len(visibility)}",
        schema_version=INTEGRATION_TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_working_readback_integration_plan_id=str(_get(plan, "working_readback_integration_plan_id")),
        memory_learning_trace_bridge_ids=tuple(str(_get(item, "memory_learning_trace_bridge_id")) for item in learning if item),
        memory_routing_trace_bridge_ids=tuple(str(_get(item, "memory_routing_trace_bridge_id")) for item in routing if item),
        memory_application_data_bridge_ids=tuple(str(_get(item, "memory_application_data_bridge_id")) for item in application if item),
        working_readback_visibility_ids=tuple(str(_get(item, "working_readback_visibility_id")) for item in visibility if item),
        trace_spine_boundary_ids=tuple(str(_get(item, "trace_spine_boundary_id")) for item in boundaries if item),
        trace_kind=trace_kind,
        trace_status=status,
        trace_summary=_integration_trace_summary(status, len(visibility)),
        memory_learning_trace_bridge_count=len(learning),
        memory_routing_trace_bridge_count=len(routing),
        memory_application_data_bridge_count=len(application),
        working_readback_visibility_count=len(visibility),
        working_readback_visible_count=sum(1 for item in visibility if _get(item, "working_readback_visible") is True),
        trace_spine_boundary_confirmed=all(validate_trace_spine_raw_evidence_boundary(item)["valid"] for item in boundaries) if boundaries else False,
        raw_evidence_boundary_confirmed=all(validate_trace_spine_raw_evidence_boundary(item)["valid"] for item in boundaries) if boundaries else False,
        memory_layer_interpretation_only_confirmed=all(_get(item, "application_data_stores_interpretation_only", True) for item in application),
        source_trace_refs_preserved_confirmed=bool(source_refs),
        concept_id_not_embedded_into_raw_history_confirmed=not any(
            _get(item, "concept_id_embedded_into_raw_history", False)
            for item in (*learning, *routing, *application, *visibility, *boundaries)
            if item
        ),
        internal_action_choice_influence_created=internal_action_choice_influence_created,
        task_action_selection_influence_created=task_action_selection_influence_created,
        candidate_ordering_changed=candidate_ordering_changed,
        selected_action_created=selected_action_created,
        long_term_memory_write_performed=long_term_memory_write_performed,
        core_memory_write_performed=core_memory_write_performed,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=source_refs,
    )


def validate_host_body_working_readback_integration_trace(trace: Any) -> dict[str, object]:
    record = _record(trace)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["trace_status"]),
        {
            "host_body_working_readback_integration_trace_recorded",
            "host_body_working_readback_integration_trace_recorded_empty",
        },
    )


def build_host_body_working_readback_integration_audit(
    *,
    working_readback_integration_plan: Any | None,
    working_readback_integration_trace: Any | None,
    trace_spine_boundary: Any | None,
    preferred_pass_status: str | None = None,
    production_behavior_created: bool = False,
) -> HostBodyWorkingReadbackIntegrationAudit:
    plan = _record(working_readback_integration_plan)
    trace = _record(working_readback_integration_trace)
    boundary = _record(trace_spine_boundary)
    plan_valid = bool(plan and validate_host_body_working_readback_integration_plan(plan)["valid"])
    trace_valid = bool(trace and validate_host_body_working_readback_integration_trace(trace)["valid"])
    boundary_valid = bool(boundary and validate_trace_spine_raw_evidence_boundary(boundary)["valid"])
    source_refs = _refs_from(plan, trace, boundary)
    joined_refs = " ".join(source_refs)
    status = preferred_pass_status or "passed_host_body_reviewed_concept_working_readback_integration"
    reasons: list[str] = []
    if not plan:
        status = "blocked_missing_working_readback_integration_plan"
        reasons.append(status)
    elif not boundary_valid:
        status = _boundary_audit_status(boundary)
        reasons.append(status)
    elif "blocked_raw_trace_dump_detected" in joined_refs:
        status = "blocked_raw_trace_dumped_into_memory_learning_trace"
        reasons.append(status)
    elif "blocked_raw_trace_summarization_detected" in joined_refs:
        status = "blocked_raw_trace_summarized"
        reasons.append(status)
    elif "blocked_concept_id_embedded_into_raw_history" in joined_refs:
        status = "blocked_concept_id_embedded_into_raw_history"
        reasons.append(status)
    elif "blocked_missing_source_trace_refs" in joined_refs:
        status = "blocked_missing_source_trace_refs"
        reasons.append(status)
    elif trace and _get(trace, "trace_status") == "blocked_invalid_memory_learning_trace_bridge":
        status = "blocked_invalid_memory_learning_trace_bridge"
        reasons.append(status)
    elif trace and _get(trace, "trace_status") == "blocked_invalid_memory_routing_trace_bridge":
        status = "blocked_invalid_memory_routing_trace_bridge"
        reasons.append(status)
    elif trace and _get(trace, "trace_status") == "blocked_invalid_memory_application_data_bridge":
        status = "blocked_invalid_memory_application_data_bridge"
        reasons.append(status)
    elif trace and _get(trace, "trace_status") == "blocked_invalid_working_readback_visibility":
        status = "blocked_invalid_working_readback_visibility"
        reasons.append(status)
    elif trace and _get(trace, "trace_status") == "blocked_trace_spine_boundary_failure":
        status = "blocked_trace_spine_boundary_failure"
        reasons.append(status)
    elif trace and _get(trace, "internal_action_choice_influence_created"):
        status = "blocked_internal_action_choice_influence_detected"
        reasons.append(status)
    elif trace and (_get(trace, "task_action_selection_influence_created") or _get(trace, "selected_action_created")):
        status = "blocked_task_action_selection_influence_detected"
        reasons.append(status)
    elif trace and _get(trace, "long_term_memory_write_performed"):
        status = "blocked_long_term_memory_write_detected"
        reasons.append(status)
    elif trace and _get(trace, "core_memory_write_performed"):
        status = "blocked_core_memory_write_detected"
        reasons.append(status)
    elif trace and _get(trace, "first_output_created"):
        status = "blocked_first_output_detected"
        reasons.append(status)
    elif trace and _get(trace, "live_runtime_session_created"):
        status = "blocked_live_runtime_detected"
        reasons.append(status)
    elif production_behavior_created:
        status = "blocked_production_behavior_detected"
        reasons.append(status)
    elif not trace_valid:
        status = "blocked_invalid_working_readback_visibility"
        reasons.append(status)
    return HostBodyWorkingReadbackIntegrationAudit(
        working_readback_integration_audit_id=f"host_body_working_readback_integration_audit:{status}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_working_readback_integration_plan_id=_get(plan, "working_readback_integration_plan_id"),
        source_working_readback_integration_trace_id=_get(trace, "working_readback_integration_trace_id"),
        source_trace_spine_boundary_id=_get(boundary, "trace_spine_boundary_id"),
        integration_plan_valid=plan_valid,
        memory_learning_trace_bridges_valid=bool(trace and _get(trace, "trace_status") not in {"blocked_invalid_memory_learning_trace_bridge"}),
        memory_routing_trace_bridges_valid=bool(trace and _get(trace, "trace_status") not in {"blocked_invalid_memory_routing_trace_bridge"}),
        memory_application_data_bridges_valid=bool(trace and _get(trace, "trace_status") not in {"blocked_invalid_memory_application_data_bridge"}),
        working_readback_visibility_valid=bool(trace and _get(trace, "trace_status") not in {"blocked_invalid_working_readback_visibility"}),
        trace_spine_boundary_valid=boundary_valid,
        integration_trace_valid=trace_valid,
        host_body_reviewed_concept_replay_confirmed=True,
        existing_memory_path_reuse_confirmed=True,
        working_readback_visibility_confirmed=bool(trace and _get(trace, "working_readback_visible_count", 0) > 0),
        trace_spine_format_unified_confirmed=bool(_get(boundary, "trace_spine_format_unified", False)),
        trace_spine_time_aligned_confirmed=bool(_get(boundary, "trace_spine_time_aligned", False)),
        raw_trace_append_only_confirmed=bool(_get(boundary, "raw_trace_append_only_confirmed", False)),
        raw_trace_not_summarized_during_service_period=not bool(_get(boundary, "raw_trace_summarized_during_service_period", True)),
        memory_layer_stores_interpretation_only_confirmed=bool(_get(boundary, "memory_layer_stores_interpretation_only", False)),
        source_trace_refs_preserved_confirmed=bool(_get(boundary, "source_trace_refs_preserved", False)),
        concept_id_not_embedded_into_raw_history_confirmed=not bool(_get(boundary, "concept_id_embedded_into_raw_history", True)),
        raw_trace_not_dumped_into_memory_learning_trace_confirmed=not bool(_get(boundary, "raw_trace_dumped_into_memory_learning_trace", True)),
        gcmc_docs_only_future_architecture_confirmed=bool(_get(boundary, "gcmc_document_added_as_future_age_architecture", False)),
        gcmc_runtime_not_implemented_confirmed=not bool(_get(boundary, "gcmc_runtime_implemented", True)),
        cl_token_not_created_confirmed=not bool(_get(boundary, "cl_token_created", True)),
        no_internal_action_choice_influence=not bool(trace and _get(trace, "internal_action_choice_influence_created", False)),
        no_task_action_selection_influence=not bool(trace and _get(trace, "task_action_selection_influence_created", False)),
        no_task_selected_action=not bool(trace and _get(trace, "selected_action_created", False)),
        no_final_action=True,
        no_direct_command=True,
        no_sandbox_execution=True,
        no_long_term_memory_write=not bool(trace and _get(trace, "long_term_memory_write_performed", False)),
        no_core_memory_write=not bool(trace and _get(trace, "core_memory_write_performed", False)),
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_state_persistence_write=True,
        no_external_control=True,
        no_real_hardware_access=True,
        no_semantic_vision=True,
        no_speech_recognition=True,
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


def validate_host_body_working_readback_integration_audit(audit: Any) -> dict[str, object]:
    record = _record(audit)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["audit_status"]),
        {
            "passed_host_body_reviewed_concept_working_readback_integration",
            "passed_trace_spine_raw_evidence_boundary",
            "passed_gcmc_docs_only_future_architecture",
        },
    )


def build_host_body_working_readback_integration_readiness(
    *,
    working_readback_integration_audit: Any | None,
    readiness_status: str = "ready_for_host_body_readback_internal_action_influence_only",
) -> HostBodyWorkingReadbackIntegrationReadinessRecord:
    audit = _record(working_readback_integration_audit)
    if audit is None:
        status = "not_ready_missing_working_readback_integration_audit"
    elif not validate_host_body_working_readback_integration_audit(audit)["valid"]:
        status = "not_ready_boundary_failure"
    elif readiness_status.startswith("ready_for_"):
        status = readiness_status
    else:
        status = "blocked_forbidden_authority_detected"
    return HostBodyWorkingReadbackIntegrationReadinessRecord(
        working_readback_integration_readiness_id=f"host_body_working_readback_integration_readiness:{status}",
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_working_readback_integration_audit_id=str(_get(audit, "working_readback_integration_audit_id")),
        current_verified_capability="Host Body ReviewedConcept working readback visibility with Trace Spine raw evidence boundary.",
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason="Let Host Body working readback influence internal-only Host Body action choice ordering without Task Engine authority.",
        ready_for_host_body_readback_internal_action_influence=True,
        ready_for_host_body_closed_loop_milestone_audit=True,
        ready_for_bounded_embodied_loop_runner=True,
        ready_for_long_term_memory_write=False,
        ready_for_core_memory_write=False,
        ready_for_raw_trace_summarization=False,
        ready_for_cl_token_creation=False,
        ready_for_gcmc_runtime=False,
        ready_for_task_action_selection_influence=False,
        ready_for_external_control=False,
        ready_for_first_output=False,
        ready_for_live_runtime_session=False,
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=_refs_from(audit),
    )


def validate_host_body_working_readback_integration_readiness(readiness: Any) -> dict[str, object]:
    record = _record(readiness)
    if record is None:
        return {"valid": False, "status": "missing", "blocked_reasons": ("missing",)}
    return _validation(
        str(record["readiness_status"]),
        {
            "ready_for_host_body_readback_internal_action_influence_only",
            "ready_for_host_body_closed_loop_milestone_audit_only",
            "ready_for_bounded_embodied_loop_runner_only",
        },
    )


def build_demo_uncertainty_reviewed_concept_working_readback() -> dict[str, object]:
    return _build_demo_from_reviewed_concept_replay(
        build_demo_uncertainty_feedback_reviewed_concept_replay()
    )


def build_demo_interesting_event_reviewed_concept_working_readback() -> dict[str, object]:
    return _build_demo_from_reviewed_concept_replay(
        build_demo_interesting_event_feedback_reviewed_concept_replay()
    )


def build_demo_runtime_bridge_reviewed_concept_working_readback() -> dict[str, object]:
    return _build_demo_from_reviewed_concept_replay(
        build_demo_runtime_bridge_feedback_reviewed_concept_replay()
    )


def build_demo_mixed_reviewed_concept_working_readback() -> dict[str, object]:
    return _build_demo_from_reviewed_concept_replay(
        build_demo_mixed_feedback_reviewed_concept_replay()
    )


def build_demo_trace_spine_raw_evidence_boundary() -> dict[str, object]:
    payload = build_demo_uncertainty_reviewed_concept_working_readback()
    audit = build_host_body_working_readback_integration_audit(
        working_readback_integration_plan=payload["host_body_working_readback_integration_plan"],
        working_readback_integration_trace=payload["host_body_working_readback_integration_trace"],
        trace_spine_boundary=payload["trace_spine_raw_evidence_boundary"],
        preferred_pass_status="passed_trace_spine_raw_evidence_boundary",
    )
    payload["host_body_working_readback_integration_audit"] = audit.to_dict()
    return payload


def build_demo_gcmc_docs_only_future_architecture() -> dict[str, object]:
    payload = build_demo_uncertainty_reviewed_concept_working_readback()
    audit = build_host_body_working_readback_integration_audit(
        working_readback_integration_plan=payload["host_body_working_readback_integration_plan"],
        working_readback_integration_trace=payload["host_body_working_readback_integration_trace"],
        trace_spine_boundary=payload["trace_spine_raw_evidence_boundary"],
        preferred_pass_status="passed_gcmc_docs_only_future_architecture",
    )
    payload["host_body_working_readback_integration_audit"] = audit.to_dict()
    return payload


def build_demo_blocked_raw_trace_dump() -> dict[str, object]:
    return _build_demo_from_reviewed_concept_replay(
        build_demo_uncertainty_feedback_reviewed_concept_replay(),
        memory_learning_bridge_overrides={"raw_trace_dumped_into_memory_learning_trace": True},
    )


def build_demo_blocked_raw_trace_summarization() -> dict[str, object]:
    return _build_demo_from_reviewed_concept_replay(
        build_demo_uncertainty_feedback_reviewed_concept_replay(),
        memory_learning_bridge_overrides={"raw_trace_summarized_during_service_period": True},
    )


def build_demo_blocked_concept_id_embedded_into_raw_history() -> dict[str, object]:
    return _build_demo_from_reviewed_concept_replay(
        build_demo_uncertainty_feedback_reviewed_concept_replay(),
        memory_learning_bridge_overrides={"concept_id_embedded_into_raw_history": True},
    )


def build_demo_blocked_internal_action_influence() -> dict[str, object]:
    return _build_demo_from_reviewed_concept_replay(
        build_demo_uncertainty_feedback_reviewed_concept_replay(),
        integration_trace_overrides={"internal_action_choice_influence_created": True},
    )


def build_demo_blocked_task_action_influence() -> dict[str, object]:
    return _build_demo_from_reviewed_concept_replay(
        build_demo_uncertainty_feedback_reviewed_concept_replay(),
        integration_trace_overrides={"task_action_selection_influence_created": True},
    )


def build_demo_blocked_gcmc_runtime() -> dict[str, object]:
    return _build_demo_from_reviewed_concept_replay(
        build_demo_uncertainty_feedback_reviewed_concept_replay(),
        boundary_overrides={"gcmc_runtime_implemented": True},
    )


def build_demo_blocked_cl_token_creation() -> dict[str, object]:
    return _build_demo_from_reviewed_concept_replay(
        build_demo_uncertainty_feedback_reviewed_concept_replay(),
        boundary_overrides={"cl_token_created": True},
    )


def build_demo_blocked_first_output() -> dict[str, object]:
    return _build_demo_from_reviewed_concept_replay(
        build_demo_uncertainty_feedback_reviewed_concept_replay(),
        integration_trace_overrides={"first_output_created": True},
    )


def build_demo_blocked_live_runtime() -> dict[str, object]:
    return _build_demo_from_reviewed_concept_replay(
        build_demo_uncertainty_feedback_reviewed_concept_replay(),
        integration_trace_overrides={"live_runtime_session_created": True},
    )


def render_host_body_working_readback_integration_summary_text(payload: dict[str, object]) -> str:
    audit = payload.get("host_body_working_readback_integration_audit", {})
    trace = payload.get("host_body_working_readback_integration_trace", {})
    return "\n".join(
        (
            "Host Body Working Readback Integration",
            f"audit_status: {audit.get('audit_status')}",
            f"working_readback_visible_count: {trace.get('working_readback_visible_count')}",
            "raw_trace_dumped_into_memory_learning_trace: false",
            "concept_id_embedded_into_raw_history: false",
        )
    )


def render_trace_spine_raw_evidence_boundary_summary_text(boundary: Any) -> str:
    record = _record(boundary) or {}
    return "\n".join(
        (
            "Trace Spine Raw Evidence Boundary",
            f"boundary_status: {record.get('boundary_status')}",
            f"gcmc_runtime_implemented: {record.get('gcmc_runtime_implemented')}",
            f"cl_token_created: {record.get('cl_token_created')}",
            f"raw_trace_append_only_confirmed: {record.get('raw_trace_append_only_confirmed')}",
        )
    )


def render_host_body_working_readback_visibility_table(
    visibility_records: tuple[Any, ...] | list[Any],
) -> str:
    lines = ["visibility_id | status | future_host_body | raw_trace"]
    for item in visibility_records:
        record = _record(item) or {}
        lines.append(
            " | ".join(
                (
                    str(record.get("working_readback_visibility_id")),
                    str(record.get("visibility_status")),
                    str(record.get("visible_to_future_host_body_context")),
                    str(record.get("readback_payload_contains_raw_trace")),
                )
            )
        )
    return "\n".join(lines)


def _build_demo_from_reviewed_concept_replay(
    replay_payload: dict[str, object],
    *,
    memory_learning_bridge_overrides: dict[str, object] | None = None,
    routing_bridge_overrides: dict[str, object] | None = None,
    application_bridge_overrides: dict[str, object] | None = None,
    visibility_overrides: dict[str, object] | None = None,
    boundary_overrides: dict[str, object] | None = None,
    integration_trace_overrides: dict[str, object] | None = None,
) -> dict[str, object]:
    replay_audit = replay_payload["host_body_reviewed_concept_replay_audit"]
    replay_trace = replay_payload["host_body_reviewed_concept_replay_trace"]
    validate_host_body_reviewed_concept_replay_audit(replay_audit)
    validate_host_body_reviewed_concept_replay_trace(replay_trace)
    plan = build_host_body_working_readback_integration_plan(
        reviewed_concept_replay_audit=replay_audit,
        reviewed_concept_replay_trace=replay_trace,
    )
    learning_bridges = []
    routing_bridges = []
    application_bridges = []
    visibility_records = []
    for readiness in replay_payload["host_body_reviewed_concept_readiness_replays"]:
        learning = build_host_body_memory_learning_trace_bridge(
            working_readback_integration_plan=plan,
            reviewed_concept_readiness_replay=readiness,
            **(memory_learning_bridge_overrides or {}),
        )
        routing = build_host_body_memory_routing_trace_bridge(
            memory_learning_trace_bridge=learning,
            **(routing_bridge_overrides or {}),
        )
        application = build_host_body_memory_application_data_bridge(
            memory_routing_trace_bridge=routing,
            **(application_bridge_overrides or {}),
        )
        visibility = build_host_body_working_readback_visibility(
            memory_application_data_bridge=application,
            **(visibility_overrides or {}),
        )
        learning_bridges.append(learning)
        routing_bridges.append(routing)
        application_bridges.append(application)
        visibility_records.append(visibility)
    boundary = build_trace_spine_raw_evidence_boundary(
        working_readback_integration_plan=plan,
        **(boundary_overrides or {}),
    )
    integration_trace = build_host_body_working_readback_integration_trace(
        working_readback_integration_plan=plan,
        memory_learning_trace_bridges=tuple(learning_bridges),
        memory_routing_trace_bridges=tuple(routing_bridges),
        memory_application_data_bridges=tuple(application_bridges),
        working_readback_visibility_records=tuple(visibility_records),
        trace_spine_boundary_records=(boundary,),
        **(integration_trace_overrides or {}),
    )
    audit = build_host_body_working_readback_integration_audit(
        working_readback_integration_plan=plan,
        working_readback_integration_trace=integration_trace,
        trace_spine_boundary=boundary,
    )
    readiness = build_host_body_working_readback_integration_readiness(
        working_readback_integration_audit=audit
    )
    payload = {
        "host_body_working_readback_integration_plan": plan.to_dict(),
        "host_body_memory_learning_trace_bridges": tuple(item.to_dict() for item in learning_bridges),
        "host_body_memory_routing_trace_bridges": tuple(item.to_dict() for item in routing_bridges),
        "host_body_memory_application_data_bridges": tuple(item.to_dict() for item in application_bridges),
        "host_body_working_readback_visibility_records": tuple(item.to_dict() for item in visibility_records),
        "trace_spine_raw_evidence_boundary": boundary.to_dict(),
        "host_body_working_readback_integration_trace": integration_trace.to_dict(),
        "host_body_working_readback_integration_audit": audit.to_dict(),
        "host_body_working_readback_integration_readiness": readiness.to_dict(),
    }
    payload["rendered_host_body_working_readback_integration_summary"] = (
        render_host_body_working_readback_integration_summary_text(payload)
    )
    payload["rendered_trace_spine_raw_evidence_boundary_summary"] = (
        render_trace_spine_raw_evidence_boundary_summary_text(boundary)
    )
    payload["rendered_host_body_working_readback_visibility_table"] = (
        render_host_body_working_readback_visibility_table(visibility_records)
    )
    return payload


def _memory_learning_trace_bridge_kind(reviewed_kind: str | None) -> str:
    if reviewed_kind == "host_body_uncertainty_reviewed_concept_readiness_replay":
        return "host_body_uncertainty_reviewed_concept_to_memory_learning_trace_bridge"
    if reviewed_kind == "host_body_interesting_event_reviewed_concept_readiness_replay":
        return "host_body_interesting_event_reviewed_concept_to_memory_learning_trace_bridge"
    if reviewed_kind == "host_body_runtime_bridge_reviewed_concept_readiness_replay":
        return "host_body_runtime_bridge_reviewed_concept_to_memory_learning_trace_bridge"
    return "host_body_reviewed_concept_to_memory_learning_trace_bridge"


def _scope_from_kind(kind: str | None) -> str:
    if kind and "uncertainty" in kind:
        return "host_body_uncertainty_feedback"
    if kind and "interesting" in kind:
        return "host_body_interesting_event_feedback"
    if kind and "runtime_bridge" in kind:
        return "host_body_runtime_bridge_feedback"
    return "host_body_feedback"


def _visibility_kind_from_refs(refs: tuple[str, ...]) -> str:
    joined = " ".join(refs)
    if "uncertainty" in joined:
        return "host_body_uncertainty_working_readback_visibility"
    if "interesting" in joined:
        return "host_body_interesting_event_working_readback_visibility"
    if "runtime_bridge" in joined:
        return "host_body_runtime_bridge_working_readback_visibility"
    return "host_body_reviewed_concept_working_readback_visibility"


def _plan_summary(status: str) -> str:
    if status == "working_readback_integration_plan_created":
        return "Host Body ReviewedConcept working readback integration plan created."
    return "Host Body working readback integration plan blocked by boundary policy."


def _memory_learning_bridge_summary(status: str) -> str:
    if status.startswith("memory_learning_trace_bridge_created"):
        return "Reviewed interpretation bridge created without raw trace dump."
    return "MemoryLearningTrace bridge blocked by raw evidence or authority boundary."


def _routing_bridge_summary(status: str) -> str:
    if status.startswith("memory_routing_trace_bridge_created"):
        return "Host Body working readback route created from interpretation only."
    return "MemoryRoutingTrace bridge blocked by raw trace or authority boundary."


def _application_bridge_summary(status: str) -> str:
    if status.startswith("memory_application_data_bridge_created"):
        return "MemoryApplicationData bridge created for future Host Body readback visibility."
    return "MemoryApplicationData bridge blocked by readback or authority boundary."


def _visibility_summary(status: str) -> str:
    if status.startswith("working_readback_visibility_created"):
        return "Host Body reviewed concept is visible to future Host Body context."
    return "Working readback visibility blocked by boundary policy."


def _trace_spine_boundary_summary(status: str) -> str:
    if status == "passed_trace_spine_raw_evidence_boundary":
        return "Qingyin v1 Trace Spine raw evidence boundary is confirmed."
    return "Trace Spine raw evidence boundary blocked unsafe trace or future AGE runtime claim."


def _integration_trace_summary(status: str, count: int) -> str:
    if status == "host_body_working_readback_integration_trace_recorded":
        return f"{count} Host Body ReviewedConcept item(s) integrated for working readback visibility."
    if status == "host_body_working_readback_integration_trace_recorded_empty":
        return "Empty Host Body working readback integration trace recorded."
    return "Host Body working readback integration trace blocked by boundary policy."


def _boundary_audit_status(boundary: dict[str, Any] | None) -> str:
    status = _get(boundary, "boundary_status")
    if status == "blocked_raw_trace_summarized":
        return "blocked_raw_trace_summarized"
    if status == "blocked_raw_trace_dumped_into_memory_learning_trace":
        return "blocked_raw_trace_dumped_into_memory_learning_trace"
    if status == "blocked_concept_id_embedded_into_raw_history":
        return "blocked_concept_id_embedded_into_raw_history"
    if status == "blocked_missing_source_trace_refs":
        return "blocked_missing_source_trace_refs"
    if status == "blocked_gcmc_runtime_implemented":
        return "blocked_gcmc_runtime_implemented"
    if status == "blocked_cl_token_created":
        return "blocked_cl_token_created"
    return "blocked_trace_spine_boundary_failure"


def _readiness_summary(status: str) -> str:
    if status.startswith("ready_for_"):
        return "Host Body working readback integration is ready for the next internal-action influence package."
    if status.startswith("not_ready_"):
        return "Host Body working readback integration readiness is not established."
    return "Host Body working readback integration readiness is blocked by forbidden authority."
