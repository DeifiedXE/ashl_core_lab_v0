"""Host Body feedback replay through existing ReviewedConcept readiness path."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.host_body.host_body_existing_learning_pipeline_compatibility import (
    build_host_body_existing_learning_pipeline_compatibility_audit,
    build_host_body_existing_learning_pipeline_compatibility_plan,
    build_host_body_feedback_candidate_normalization,
    build_host_body_feedback_concept_candidate_compatibility,
    build_host_body_feedback_existing_learning_pipeline_trace,
    build_host_body_feedback_existing_review_adapter,
    build_host_body_feedback_existing_review_replay,
)
from ashl_core_v1.host_body.host_body_learning_feedback_bridge import (
    build_demo_deferred_runtime_bridge_to_learning_feedback_candidate,
    build_demo_interesting_event_to_learning_feedback_candidate,
    build_demo_uncertainty_to_learning_feedback_candidate,
)


SOURCE_ENGINE = "host_body"

PLAN_SCHEMA_VERSION = "qingyin_host_body_reviewed_concept_replay_plan_v0"
INPUT_SCHEMA_VERSION = "qingyin_host_body_approved_feedback_replay_input_v0"
DRAFT_SCHEMA_VERSION = "qingyin_host_body_existing_concept_candidate_draft_replay_v0"
REFINEMENT_SCHEMA_VERSION = "qingyin_host_body_existing_concept_candidate_refinement_replay_v0"
READINESS_REPLAY_SCHEMA_VERSION = "qingyin_host_body_reviewed_concept_readiness_replay_v0"
TRACE_SCHEMA_VERSION = "qingyin_host_body_reviewed_concept_replay_trace_v0"
AUDIT_SCHEMA_VERSION = "qingyin_host_body_reviewed_concept_replay_audit_v0"
READINESS_SCHEMA_VERSION = "qingyin_host_body_reviewed_concept_replay_readiness_v0"

REPLAY_NAME = "host_body_feedback_through_reviewed_concept_replay"
REPLAY_KIND = "existing_pipeline_replay_only"
EXISTING_PIPELINE_PACKAGES = ("Package 90", "Package 91", "Package 92")
REQUIRED_EXISTING_STAGES = (
    "existing_learning_feedback_candidate_review",
    "existing_concept_candidate_draft",
    "existing_concept_candidate_refinement",
    "existing_reviewed_concept_readiness",
)
ALLOWED_INPUT_CANDIDATE_KINDS = (
    "host_body_uncertainty_feedback_candidate",
    "host_body_interesting_event_feedback_candidate",
    "host_body_teacher_review_feedback_candidate",
    "host_body_runtime_bridge_feedback_candidate",
)
ALLOWED_REVIEW_RESULTS = ("approved",)
FORBIDDEN_OUTPUTS = (
    "memory_trace",
    "memory_application_data",
    "working_readback_hint",
    "action_ordering_change",
    "first_output",
    "live_runtime_event",
)

SAFE_CLAIM = (
    "ASHL Core v1 can replay approved Host Body feedback candidates through the "
    "existing Package 90 to 92 learning pipeline up to ReviewedConcept readiness."
)
BLOCKED_CLAIMS = (
    "no_parallel_teacher_review",
    "no_parallel_concept_system",
    "no_reviewed_concept_created_by_this_package",
    "no_working_readback_created",
    "no_memory_application_data_created",
    "no_memory_layer_write",
    "no_automatic_learning_approval",
    "no_teacher_approval_created",
    "no_action_selection_influence",
    "no_external_control",
    "no_first_output",
    "no_live_runtime_session",
)
READINESS_NEXT_PACKAGE = (
    "Package 111 / ASHL Core v1 Host Body ReviewedConcept Working Readback Integration Minimal v0"
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
    return "_".join("".join(safe).split("_"))[:100] or "empty"


@dataclass(frozen=True)
class HostBodyReviewedConceptReplayPlanRecord:
    reviewed_concept_replay_plan_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_existing_learning_pipeline_compatibility_audit_id: str | None
    source_existing_learning_pipeline_trace_id: str | None
    replay_name: str
    replay_kind: str
    existing_pipeline_packages: tuple[str, ...]
    required_existing_stages: tuple[str, ...]
    allowed_input_candidate_kinds: tuple[str, ...]
    allowed_review_results: tuple[str, ...]
    forbidden_outputs: tuple[str, ...]
    reuse_existing_review_path_required: bool
    reuse_existing_concept_path_required: bool
    reuse_existing_refinement_path_required: bool
    reuse_existing_reviewed_concept_path_required: bool
    parallel_teacher_review_allowed: bool
    parallel_concept_system_allowed: bool
    automatic_learning_approval_allowed: bool
    memory_write_allowed: bool
    working_readback_mutation_allowed: bool
    action_selection_influence_allowed: bool
    first_output_allowed: bool
    live_runtime_session_allowed: bool
    plan_status: str
    plan_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PLAN_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_reviewed_concept_replay_plan_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.replay_name != REPLAY_NAME:
            raise ValueError("replay_name must be host_body_feedback_through_reviewed_concept_replay")
        if self.replay_kind != REPLAY_KIND:
            raise ValueError("replay_kind must be existing_pipeline_replay_only")
        if self.plan_status not in {
            "reviewed_concept_replay_plan_created",
            "blocked_missing_existing_learning_pipeline_compatibility_audit",
            "blocked_missing_existing_learning_pipeline_trace",
            "blocked_parallel_teacher_review_allowed",
            "blocked_parallel_concept_system_allowed",
            "blocked_automatic_learning_approval_allowed",
            "blocked_memory_write_allowed",
            "blocked_working_readback_mutation_allowed",
            "blocked_action_selection_influence_allowed",
            "blocked_first_output_allowed",
            "blocked_live_runtime_allowed",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown plan_status: {self.plan_status}")
        for name in (
            "existing_pipeline_packages",
            "required_existing_stages",
            "allowed_input_candidate_kinds",
            "allowed_review_results",
            "forbidden_outputs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReviewedConceptReplayPlanRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyApprovedFeedbackReplayInputRecord:
    approved_feedback_replay_input_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_replay_plan_id: str
    source_host_body_feedback_candidate_id: str | None
    source_normalization_id: str | None
    source_existing_review_adapter_id: str | None
    source_existing_review_replay_id: str | None
    input_candidate_kind: str
    existing_review_result: str
    review_result_reason_codes: tuple[str, ...]
    approved_for_replay: bool
    teacher_review_required: bool
    teacher_approval_created: bool
    host_body_scope_preserved: bool
    counterexample_scope_required: bool
    safe_for_concept_candidate_draft_replay: bool
    automatic_learning_approval_created: bool
    concept_candidate_created_by_this_record: bool
    reviewed_concept_created_by_this_record: bool
    memory_write_performed: bool
    working_readback_mutation_performed: bool
    action_selection_influence_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    input_status: str
    input_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INPUT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_approved_feedback_replay_input_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.input_candidate_kind not in ALLOWED_INPUT_CANDIDATE_KINDS + ("unknown",):
            raise ValueError(f"unknown input_candidate_kind: {self.input_candidate_kind}")
        if self.input_status not in {
            "approved_host_body_feedback_replay_input_recorded",
            "blocked_non_approved_review_result",
            "blocked_missing_review_adapter",
            "blocked_teacher_approval_created",
            "blocked_automatic_learning_approval_detected",
            "blocked_concept_candidate_created_by_input",
            "blocked_reviewed_concept_created_by_input",
            "blocked_memory_write_detected",
            "blocked_action_selection_influence_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown input_status: {self.input_status}")
        for name in ("review_result_reason_codes", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyApprovedFeedbackReplayInputRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyExistingConceptCandidateDraftReplayRecord:
    concept_candidate_draft_replay_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_approved_feedback_replay_input_id: str
    draft_replay_kind: str
    draft_replay_status: str
    draft_replay_summary: str
    uses_existing_package_90_draft_path: bool
    creates_parallel_concept_system: bool
    host_body_source_preserved: bool
    concept_scope: str
    concept_seed_summary: str
    counterexample_scope_required: bool
    concept_candidate_draft_ready: bool
    concept_candidate_created_by_this_package: bool
    teacher_review_result_required: bool
    teacher_approval_created: bool
    automatic_learning_approval_created: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    working_readback_mutation_performed: bool
    action_selection_influence_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DRAFT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_existing_concept_candidate_draft_replay_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.draft_replay_kind not in {
            "host_body_uncertainty_concept_candidate_draft_replay",
            "host_body_interesting_event_concept_candidate_draft_replay",
            "host_body_teacher_review_concept_candidate_draft_replay",
            "host_body_runtime_bridge_concept_candidate_draft_replay",
            "blocked_draft_replay",
        }:
            raise ValueError(f"unknown draft_replay_kind: {self.draft_replay_kind}")
        if self.draft_replay_status not in {
            "existing_concept_candidate_draft_replay_ready",
            "blocked_invalid_approved_feedback_input",
            "blocked_parallel_concept_system_detected",
            "blocked_concept_candidate_created_by_this_package",
            "blocked_teacher_approval_created",
            "blocked_automatic_learning_approval_detected",
            "blocked_reviewed_concept_created",
            "blocked_memory_write_detected",
            "blocked_action_selection_influence_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown draft_replay_status: {self.draft_replay_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyExistingConceptCandidateDraftReplayRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyExistingConceptCandidateRefinementReplayRecord:
    concept_candidate_refinement_replay_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_draft_replay_id: str
    refinement_replay_kind: str
    refinement_replay_status: str
    refinement_replay_summary: str
    uses_existing_package_91_refinement_path: bool
    creates_parallel_refinement_system: bool
    refined_scope_summary: str
    counterexample_scope_checked: bool
    host_body_scope_preserved: bool
    refined_concept_candidate_ready: bool
    refined_concept_candidate_created_by_this_package: bool
    teacher_review_required: bool
    teacher_approval_created: bool
    automatic_learning_approval_created: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    working_readback_mutation_performed: bool
    action_selection_influence_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REFINEMENT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_existing_concept_candidate_refinement_replay_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.refinement_replay_kind not in {
            "host_body_concept_candidate_existing_refinement_replay",
            "host_body_uncertainty_existing_refinement_replay",
            "host_body_interesting_event_existing_refinement_replay",
            "host_body_runtime_bridge_existing_refinement_replay",
            "blocked_refinement_replay",
        }:
            raise ValueError(f"unknown refinement_replay_kind: {self.refinement_replay_kind}")
        if self.refinement_replay_status not in {
            "existing_concept_candidate_refinement_replay_ready",
            "blocked_invalid_draft_replay",
            "blocked_parallel_refinement_system_detected",
            "blocked_counterexample_scope_missing",
            "blocked_refined_concept_candidate_created_by_this_package",
            "blocked_teacher_approval_created",
            "blocked_automatic_learning_approval_detected",
            "blocked_reviewed_concept_created",
            "blocked_memory_write_detected",
            "blocked_action_selection_influence_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown refinement_replay_status: {self.refinement_replay_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyExistingConceptCandidateRefinementReplayRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReviewedConceptReadinessReplayRecord:
    reviewed_concept_readiness_replay_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_refinement_replay_id: str
    reviewed_concept_replay_kind: str
    reviewed_concept_replay_status: str
    reviewed_concept_replay_summary: str
    uses_existing_package_92_reviewed_concept_path: bool
    creates_parallel_reviewed_concept_system: bool
    reviewed_concept_ready: bool
    reviewed_concept_created_by_this_package: bool
    reviewed_concept_record_id: str | None
    host_body_scope_preserved: bool
    teacher_review_result_preserved: bool
    counterexample_scope_preserved: bool
    safe_for_working_readback_integration_later: bool
    working_readback_created: bool
    memory_application_data_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    teacher_approval_created: bool
    action_selection_influence_created: bool
    external_control_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READINESS_REPLAY_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_reviewed_concept_readiness_replay_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.reviewed_concept_replay_kind not in {
            "host_body_feedback_reviewed_concept_readiness_replay",
            "host_body_uncertainty_reviewed_concept_readiness_replay",
            "host_body_interesting_event_reviewed_concept_readiness_replay",
            "host_body_runtime_bridge_reviewed_concept_readiness_replay",
            "blocked_reviewed_concept_replay",
        }:
            raise ValueError(f"unknown reviewed_concept_replay_kind: {self.reviewed_concept_replay_kind}")
        if self.reviewed_concept_replay_status not in {
            "host_body_reviewed_concept_readiness_replay_ready",
            "blocked_invalid_refinement_replay",
            "blocked_parallel_reviewed_concept_system_detected",
            "blocked_reviewed_concept_created_by_this_package",
            "blocked_working_readback_created",
            "blocked_memory_application_data_created",
            "blocked_memory_write_detected",
            "blocked_automatic_learning_approval_detected",
            "blocked_teacher_approval_created",
            "blocked_action_selection_influence_detected",
            "blocked_external_control_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown reviewed_concept_replay_status: {self.reviewed_concept_replay_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReviewedConceptReadinessReplayRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReviewedConceptReplayTraceRecord:
    reviewed_concept_replay_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_replay_plan_id: str
    approved_feedback_input_ids: tuple[str, ...]
    draft_replay_ids: tuple[str, ...]
    refinement_replay_ids: tuple[str, ...]
    reviewed_concept_readiness_replay_ids: tuple[str, ...]
    trace_kind: str
    trace_status: str
    trace_summary: str
    approved_feedback_input_count: int
    draft_replay_count: int
    refinement_replay_count: int
    reviewed_concept_readiness_count: int
    uses_existing_pipeline_only: bool
    parallel_learning_pipeline_created: bool
    reviewed_concept_ready_count: int
    reviewed_concept_created_by_this_package: bool
    working_readback_created: bool
    memory_application_data_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    teacher_approval_created: bool
    action_selection_influence_created: bool
    external_control_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TRACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_reviewed_concept_replay_trace_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.trace_kind not in {
            "single_host_body_feedback_reviewed_concept_replay",
            "mixed_host_body_feedback_reviewed_concept_replay",
            "empty_host_body_feedback_reviewed_concept_replay",
            "blocked_reviewed_concept_replay_trace",
        }:
            raise ValueError(f"unknown trace_kind: {self.trace_kind}")
        if self.trace_status not in {
            "host_body_feedback_reviewed_concept_replay_trace_recorded",
            "host_body_feedback_reviewed_concept_replay_trace_recorded_empty",
            "blocked_invalid_approved_feedback_input",
            "blocked_invalid_draft_replay",
            "blocked_invalid_refinement_replay",
            "blocked_invalid_reviewed_concept_readiness_replay",
            "blocked_parallel_learning_pipeline_detected",
            "blocked_reviewed_concept_created_by_this_package",
            "blocked_working_readback_created",
            "blocked_memory_application_data_created",
            "blocked_memory_write_detected",
            "blocked_action_selection_influence_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown trace_status: {self.trace_status}")
        for name in (
            "approved_feedback_input_ids",
            "draft_replay_ids",
            "refinement_replay_ids",
            "reviewed_concept_readiness_replay_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReviewedConceptReplayTraceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReviewedConceptReplayAudit:
    reviewed_concept_replay_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_replay_plan_id: str | None
    source_reviewed_concept_replay_trace_id: str | None
    replay_plan_valid: bool
    approved_inputs_valid: bool
    draft_replays_valid: bool
    refinement_replays_valid: bool
    reviewed_concept_readiness_replays_valid: bool
    replay_trace_valid: bool
    host_body_feedback_pipeline_compatibility_confirmed: bool
    existing_package_90_review_path_confirmed: bool
    existing_package_91_refinement_path_confirmed: bool
    existing_package_92_reviewed_concept_path_confirmed: bool
    reviewed_concept_readiness_confirmed: bool
    no_parallel_teacher_review: bool
    no_parallel_concept_system: bool
    no_parallel_refinement_system: bool
    no_parallel_reviewed_concept_system: bool
    no_reviewed_concept_created_by_this_package: bool
    no_working_readback_created: bool
    no_memory_application_data_created: bool
    no_memory_layer_write: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_state_persistence_write: bool
    no_automatic_learning_approval: bool
    no_teacher_approval_created: bool
    no_task_action_selection_influence: bool
    no_task_selected_action: bool
    no_final_action: bool
    no_direct_command: bool
    no_sandbox_execution: bool
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
            raise ValueError("schema_version must be qingyin_host_body_reviewed_concept_replay_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.audit_status not in {
            "passed_host_body_feedback_through_reviewed_concept_replay",
            "passed_host_body_uncertainty_reviewed_concept_replay",
            "passed_host_body_interesting_event_reviewed_concept_replay",
            "passed_host_body_runtime_bridge_reviewed_concept_replay",
            "blocked_missing_replay_plan",
            "blocked_invalid_approved_feedback_input",
            "blocked_invalid_concept_candidate_draft_replay",
            "blocked_invalid_concept_candidate_refinement_replay",
            "blocked_invalid_reviewed_concept_readiness_replay",
            "blocked_invalid_replay_trace",
            "blocked_parallel_teacher_review_detected",
            "blocked_parallel_concept_system_detected",
            "blocked_reviewed_concept_created_by_this_package",
            "blocked_working_readback_created",
            "blocked_memory_application_data_created",
            "blocked_memory_write_detected",
            "blocked_automatic_learning_approval_detected",
            "blocked_teacher_approval_created",
            "blocked_action_selection_influence_detected",
            "blocked_external_control_detected",
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
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReviewedConceptReplayAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyReviewedConceptReplayReadinessRecord:
    reviewed_concept_replay_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_replay_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_host_body_reviewed_concept_working_readback: bool
    ready_for_host_body_readback_internal_action_influence: bool
    ready_for_host_body_closed_loop_milestone_audit: bool
    ready_for_memory_layer_write: bool
    ready_for_memory_application_data_creation_by_this_package: bool
    ready_for_working_readback_mutation_by_this_package: bool
    ready_for_automatic_learning_approval: bool
    ready_for_action_selection_influence: bool
    ready_for_external_control: bool
    ready_for_first_output: bool
    ready_for_live_runtime_session: bool
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READINESS_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_reviewed_concept_replay_readiness_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.readiness_status not in {
            "ready_for_host_body_reviewed_concept_working_readback_only",
            "ready_for_host_body_readback_internal_action_influence_only",
            "ready_for_host_body_closed_loop_milestone_audit_only",
            "not_ready_missing_reviewed_concept_replay_audit",
            "not_ready_boundary_failure",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyReviewedConceptReplayReadinessRecord":
        return cls(**dict(data))


def build_host_body_reviewed_concept_replay_plan(
    *,
    existing_learning_pipeline_compatibility_audit: dict[str, object] | Any | None,
    existing_learning_pipeline_trace: dict[str, object] | Any | None,
    reuse_existing_review_path_required: bool = True,
    reuse_existing_concept_path_required: bool = True,
    reuse_existing_refinement_path_required: bool = True,
    reuse_existing_reviewed_concept_path_required: bool = True,
    parallel_teacher_review_allowed: bool = False,
    parallel_concept_system_allowed: bool = False,
    automatic_learning_approval_allowed: bool = False,
    memory_write_allowed: bool = False,
    working_readback_mutation_allowed: bool = False,
    action_selection_influence_allowed: bool = False,
    first_output_allowed: bool = False,
    live_runtime_session_allowed: bool = False,
) -> HostBodyReviewedConceptReplayPlanRecord:
    audit = _record(existing_learning_pipeline_compatibility_audit)
    trace = _record(existing_learning_pipeline_trace)
    status = _plan_status(
        audit=audit,
        trace=trace,
        reuse_existing_review_path_required=reuse_existing_review_path_required,
        reuse_existing_concept_path_required=reuse_existing_concept_path_required,
        reuse_existing_refinement_path_required=reuse_existing_refinement_path_required,
        reuse_existing_reviewed_concept_path_required=reuse_existing_reviewed_concept_path_required,
        parallel_teacher_review_allowed=parallel_teacher_review_allowed,
        parallel_concept_system_allowed=parallel_concept_system_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        memory_write_allowed=memory_write_allowed,
        working_readback_mutation_allowed=working_readback_mutation_allowed,
        action_selection_influence_allowed=action_selection_influence_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
    )
    return HostBodyReviewedConceptReplayPlanRecord(
        reviewed_concept_replay_plan_id=f"host_body_reviewed_concept_replay_plan:{_slug(status)}",
        schema_version=PLAN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_existing_learning_pipeline_compatibility_audit_id=_value(
            audit, "existing_learning_pipeline_compatibility_audit_id"
        ),
        source_existing_learning_pipeline_trace_id=_value(
            trace, "existing_learning_pipeline_trace_id"
        ),
        replay_name=REPLAY_NAME,
        replay_kind=REPLAY_KIND,
        existing_pipeline_packages=EXISTING_PIPELINE_PACKAGES,
        required_existing_stages=REQUIRED_EXISTING_STAGES,
        allowed_input_candidate_kinds=ALLOWED_INPUT_CANDIDATE_KINDS,
        allowed_review_results=ALLOWED_REVIEW_RESULTS,
        forbidden_outputs=FORBIDDEN_OUTPUTS,
        reuse_existing_review_path_required=reuse_existing_review_path_required,
        reuse_existing_concept_path_required=reuse_existing_concept_path_required,
        reuse_existing_refinement_path_required=reuse_existing_refinement_path_required,
        reuse_existing_reviewed_concept_path_required=reuse_existing_reviewed_concept_path_required,
        parallel_teacher_review_allowed=parallel_teacher_review_allowed,
        parallel_concept_system_allowed=parallel_concept_system_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        memory_write_allowed=memory_write_allowed,
        working_readback_mutation_allowed=working_readback_mutation_allowed,
        action_selection_influence_allowed=action_selection_influence_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
        plan_status=status,
        plan_summary=_plan_summary(status),
        source_trace_refs=_refs_from(audit, trace),
    )


def validate_host_body_reviewed_concept_replay_plan(
    record: HostBodyReviewedConceptReplayPlanRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _plan(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.plan_status == "reviewed_concept_replay_plan_created"
    valid = valid and all(
        (
            item.reuse_existing_review_path_required,
            item.reuse_existing_concept_path_required,
            item.reuse_existing_refinement_path_required,
            item.reuse_existing_reviewed_concept_path_required,
        )
    )
    valid = valid and not any(
        (
            item.parallel_teacher_review_allowed,
            item.parallel_concept_system_allowed,
            item.automatic_learning_approval_allowed,
            item.memory_write_allowed,
            item.working_readback_mutation_allowed,
            item.action_selection_influence_allowed,
            item.first_output_allowed,
            item.live_runtime_session_allowed,
        )
    )
    return {"valid": valid, "status": item.plan_status, "reasons": [] if valid else [item.plan_status]}


def build_host_body_approved_feedback_replay_input(
    *,
    reviewed_concept_replay_plan: HostBodyReviewedConceptReplayPlanRecord | dict[str, object],
    normalization: dict[str, object] | Any | None,
    existing_review_adapter: dict[str, object] | Any | None,
    existing_review_replay: dict[str, object] | Any | None,
    existing_review_result: str | None = None,
    teacher_approval_created: bool = False,
    automatic_learning_approval_created: bool = False,
    concept_candidate_created_by_this_record: bool = False,
    reviewed_concept_created_by_this_record: bool = False,
    memory_write_performed: bool = False,
    working_readback_mutation_performed: bool = False,
    action_selection_influence_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyApprovedFeedbackReplayInputRecord:
    plan = _plan(reviewed_concept_replay_plan)
    normalization_record = _record(normalization)
    adapter = _record(existing_review_adapter)
    replay = _record(existing_review_replay)
    candidate_kind = str(_value(normalization_record, "source_candidate_kind") or "unknown")
    result = existing_review_result or str(_value(replay, "simulated_existing_review_result") or "blocked")
    status = _input_status(
        adapter=adapter,
        result=result,
        teacher_approval_created=teacher_approval_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        concept_candidate_created_by_this_record=concept_candidate_created_by_this_record,
        reviewed_concept_created_by_this_record=reviewed_concept_created_by_this_record,
        memory_write_performed=memory_write_performed,
        working_readback_mutation_performed=working_readback_mutation_performed,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    approved = status == "approved_host_body_feedback_replay_input_recorded"
    return HostBodyApprovedFeedbackReplayInputRecord(
        approved_feedback_replay_input_id=f"host_body_approved_feedback_replay_input:{_slug(candidate_kind)}:{_slug(status)}",
        schema_version=INPUT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_replay_plan_id=plan.reviewed_concept_replay_plan_id,
        source_host_body_feedback_candidate_id=_value(normalization_record, "source_host_body_feedback_candidate_id"),
        source_normalization_id=_value(normalization_record, "normalization_id"),
        source_existing_review_adapter_id=_value(adapter, "existing_review_adapter_id"),
        source_existing_review_replay_id=_value(replay, "existing_review_replay_id"),
        input_candidate_kind=candidate_kind,
        existing_review_result=result,
        review_result_reason_codes=_tuple_of_str(
            "review_result_reason_codes",
            tuple(replay.get("review_result_reason_codes", ())) if replay else tuple(),
        ),
        approved_for_replay=approved,
        teacher_review_required=True,
        teacher_approval_created=teacher_approval_created,
        host_body_scope_preserved=True,
        counterexample_scope_required=True,
        safe_for_concept_candidate_draft_replay=approved,
        automatic_learning_approval_created=automatic_learning_approval_created,
        concept_candidate_created_by_this_record=concept_candidate_created_by_this_record,
        reviewed_concept_created_by_this_record=reviewed_concept_created_by_this_record,
        memory_write_performed=memory_write_performed or automatic_learning_approval_created,
        working_readback_mutation_performed=working_readback_mutation_performed,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        input_status=status,
        input_summary=_input_summary(status, candidate_kind),
        source_trace_refs=_refs_from(normalization_record, adapter, replay),
    )


def validate_host_body_approved_feedback_replay_input(
    record: HostBodyApprovedFeedbackReplayInputRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _input(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.input_status == "approved_host_body_feedback_replay_input_recorded"
    valid = valid and item.existing_review_result == "approved" and item.approved_for_replay
    valid = valid and item.teacher_review_required and item.host_body_scope_preserved
    valid = valid and item.counterexample_scope_required and item.safe_for_concept_candidate_draft_replay
    valid = valid and not _input_has_forbidden(item)
    return {"valid": valid, "status": item.input_status, "reasons": [] if valid else [item.input_status]}


def build_host_body_existing_concept_candidate_draft_replay(
    *,
    approved_feedback_replay_input: HostBodyApprovedFeedbackReplayInputRecord | dict[str, object],
    creates_parallel_concept_system: bool = False,
    concept_candidate_created_by_this_package: bool = False,
    teacher_approval_created: bool = False,
    automatic_learning_approval_created: bool = False,
    reviewed_concept_created: bool = False,
    memory_write_performed: bool = False,
    working_readback_mutation_performed: bool = False,
    action_selection_influence_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyExistingConceptCandidateDraftReplayRecord:
    item = _input(approved_feedback_replay_input)
    status = _draft_status(
        item,
        creates_parallel_concept_system=creates_parallel_concept_system,
        concept_candidate_created_by_this_package=concept_candidate_created_by_this_package,
        teacher_approval_created=teacher_approval_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed,
        working_readback_mutation_performed=working_readback_mutation_performed,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    return HostBodyExistingConceptCandidateDraftReplayRecord(
        concept_candidate_draft_replay_id=f"host_body_concept_candidate_draft_replay:{_slug(item.input_candidate_kind)}:{_slug(status)}",
        schema_version=DRAFT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_approved_feedback_replay_input_id=item.approved_feedback_replay_input_id,
        draft_replay_kind=_draft_kind(item.input_candidate_kind, status),
        draft_replay_status=status,
        draft_replay_summary=_draft_summary(status, item.input_candidate_kind),
        uses_existing_package_90_draft_path=True,
        creates_parallel_concept_system=creates_parallel_concept_system,
        host_body_source_preserved=True,
        concept_scope=_concept_scope(item.input_candidate_kind),
        concept_seed_summary=f"Replay seed for {item.input_candidate_kind} via existing Package 90 draft path.",
        counterexample_scope_required=True,
        concept_candidate_draft_ready=status == "existing_concept_candidate_draft_replay_ready",
        concept_candidate_created_by_this_package=concept_candidate_created_by_this_package,
        teacher_review_result_required=True,
        teacher_approval_created=teacher_approval_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed or automatic_learning_approval_created,
        working_readback_mutation_performed=working_readback_mutation_performed,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=item.source_trace_refs,
    )


def validate_host_body_existing_concept_candidate_draft_replay(
    record: HostBodyExistingConceptCandidateDraftReplayRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _draft(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.draft_replay_status == "existing_concept_candidate_draft_replay_ready"
    valid = valid and item.uses_existing_package_90_draft_path and not item.creates_parallel_concept_system
    valid = valid and item.host_body_source_preserved and item.counterexample_scope_required
    valid = valid and item.concept_candidate_draft_ready and not _draft_has_forbidden(item)
    return {"valid": valid, "status": item.draft_replay_status, "reasons": [] if valid else [item.draft_replay_status]}


def build_host_body_existing_concept_candidate_refinement_replay(
    *,
    concept_candidate_draft_replay: HostBodyExistingConceptCandidateDraftReplayRecord | dict[str, object],
    creates_parallel_refinement_system: bool = False,
    counterexample_scope_checked: bool = True,
    refined_concept_candidate_created_by_this_package: bool = False,
    teacher_approval_created: bool = False,
    automatic_learning_approval_created: bool = False,
    reviewed_concept_created: bool = False,
    memory_write_performed: bool = False,
    working_readback_mutation_performed: bool = False,
    action_selection_influence_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyExistingConceptCandidateRefinementReplayRecord:
    draft = _draft(concept_candidate_draft_replay)
    status = _refinement_status(
        draft,
        creates_parallel_refinement_system=creates_parallel_refinement_system,
        counterexample_scope_checked=counterexample_scope_checked,
        refined_concept_candidate_created_by_this_package=refined_concept_candidate_created_by_this_package,
        teacher_approval_created=teacher_approval_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed,
        working_readback_mutation_performed=working_readback_mutation_performed,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    return HostBodyExistingConceptCandidateRefinementReplayRecord(
        concept_candidate_refinement_replay_id=f"host_body_concept_candidate_refinement_replay:{_slug(draft.draft_replay_kind)}:{_slug(status)}",
        schema_version=REFINEMENT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_draft_replay_id=draft.concept_candidate_draft_replay_id,
        refinement_replay_kind=_refinement_kind(draft.draft_replay_kind, status),
        refinement_replay_status=status,
        refinement_replay_summary=_refinement_summary(status),
        uses_existing_package_91_refinement_path=True,
        creates_parallel_refinement_system=creates_parallel_refinement_system,
        refined_scope_summary=f"Existing Package 91 refinement replay for {draft.concept_scope}.",
        counterexample_scope_checked=counterexample_scope_checked,
        host_body_scope_preserved=True,
        refined_concept_candidate_ready=status == "existing_concept_candidate_refinement_replay_ready",
        refined_concept_candidate_created_by_this_package=refined_concept_candidate_created_by_this_package,
        teacher_review_required=True,
        teacher_approval_created=teacher_approval_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed or automatic_learning_approval_created,
        working_readback_mutation_performed=working_readback_mutation_performed,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=draft.source_trace_refs,
    )


def validate_host_body_existing_concept_candidate_refinement_replay(
    record: HostBodyExistingConceptCandidateRefinementReplayRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _refinement(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.refinement_replay_status == "existing_concept_candidate_refinement_replay_ready"
    valid = valid and item.uses_existing_package_91_refinement_path and not item.creates_parallel_refinement_system
    valid = valid and item.host_body_scope_preserved and item.counterexample_scope_checked
    valid = valid and item.refined_concept_candidate_ready and not _refinement_has_forbidden(item)
    return {"valid": valid, "status": item.refinement_replay_status, "reasons": [] if valid else [item.refinement_replay_status]}


def build_host_body_reviewed_concept_readiness_replay(
    *,
    concept_candidate_refinement_replay: HostBodyExistingConceptCandidateRefinementReplayRecord | dict[str, object],
    creates_parallel_reviewed_concept_system: bool = False,
    reviewed_concept_created_by_this_package: bool = False,
    working_readback_created: bool = False,
    memory_application_data_created: bool = False,
    memory_layer_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    teacher_approval_created: bool = False,
    action_selection_influence_created: bool = False,
    external_control_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyReviewedConceptReadinessReplayRecord:
    refinement = _refinement(concept_candidate_refinement_replay)
    status = _readiness_replay_status(
        refinement,
        creates_parallel_reviewed_concept_system=creates_parallel_reviewed_concept_system,
        reviewed_concept_created_by_this_package=reviewed_concept_created_by_this_package,
        working_readback_created=working_readback_created,
        memory_application_data_created=memory_application_data_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        teacher_approval_created=teacher_approval_created,
        action_selection_influence_created=action_selection_influence_created,
        external_control_created=external_control_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    return HostBodyReviewedConceptReadinessReplayRecord(
        reviewed_concept_readiness_replay_id=f"host_body_reviewed_concept_readiness_replay:{_slug(refinement.refinement_replay_kind)}:{_slug(status)}",
        schema_version=READINESS_REPLAY_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_refinement_replay_id=refinement.concept_candidate_refinement_replay_id,
        reviewed_concept_replay_kind=_readiness_replay_kind(refinement.refinement_replay_kind, status),
        reviewed_concept_replay_status=status,
        reviewed_concept_replay_summary=_readiness_replay_summary(status),
        uses_existing_package_92_reviewed_concept_path=True,
        creates_parallel_reviewed_concept_system=creates_parallel_reviewed_concept_system,
        reviewed_concept_ready=status == "host_body_reviewed_concept_readiness_replay_ready",
        reviewed_concept_created_by_this_package=reviewed_concept_created_by_this_package,
        reviewed_concept_record_id=None,
        host_body_scope_preserved=True,
        teacher_review_result_preserved=True,
        counterexample_scope_preserved=True,
        safe_for_working_readback_integration_later=status == "host_body_reviewed_concept_readiness_replay_ready",
        working_readback_created=working_readback_created,
        memory_application_data_created=memory_application_data_created,
        memory_layer_write_performed=memory_layer_write_performed or automatic_learning_approval_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        teacher_approval_created=teacher_approval_created,
        action_selection_influence_created=action_selection_influence_created,
        external_control_created=external_control_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=refinement.source_trace_refs,
    )


def validate_host_body_reviewed_concept_readiness_replay(
    record: HostBodyReviewedConceptReadinessReplayRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _readiness_replay(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.reviewed_concept_replay_status == "host_body_reviewed_concept_readiness_replay_ready"
    valid = valid and item.uses_existing_package_92_reviewed_concept_path
    valid = valid and not item.creates_parallel_reviewed_concept_system
    valid = valid and item.reviewed_concept_ready and not item.reviewed_concept_created_by_this_package
    valid = valid and item.host_body_scope_preserved and item.teacher_review_result_preserved
    valid = valid and item.counterexample_scope_preserved and item.safe_for_working_readback_integration_later
    valid = valid and not _readiness_replay_has_forbidden(item)
    return {"valid": valid, "status": item.reviewed_concept_replay_status, "reasons": [] if valid else [item.reviewed_concept_replay_status]}


def build_host_body_reviewed_concept_replay_trace(
    *,
    reviewed_concept_replay_plan: HostBodyReviewedConceptReplayPlanRecord | dict[str, object],
    approved_feedback_inputs: tuple[HostBodyApprovedFeedbackReplayInputRecord | dict[str, object], ...] | list[HostBodyApprovedFeedbackReplayInputRecord | dict[str, object]] = tuple(),
    draft_replays: tuple[HostBodyExistingConceptCandidateDraftReplayRecord | dict[str, object], ...] | list[HostBodyExistingConceptCandidateDraftReplayRecord | dict[str, object]] = tuple(),
    refinement_replays: tuple[HostBodyExistingConceptCandidateRefinementReplayRecord | dict[str, object], ...] | list[HostBodyExistingConceptCandidateRefinementReplayRecord | dict[str, object]] = tuple(),
    reviewed_concept_readiness_replays: tuple[HostBodyReviewedConceptReadinessReplayRecord | dict[str, object], ...] | list[HostBodyReviewedConceptReadinessReplayRecord | dict[str, object]] = tuple(),
    parallel_learning_pipeline_created: bool = False,
    reviewed_concept_created_by_this_package: bool = False,
    working_readback_created: bool = False,
    memory_application_data_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    teacher_approval_created: bool = False,
    action_selection_influence_created: bool = False,
    external_control_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyReviewedConceptReplayTraceRecord:
    plan = _plan(reviewed_concept_replay_plan)
    inputs = tuple(_input(item) for item in approved_feedback_inputs)
    drafts = tuple(_draft(item) for item in draft_replays)
    refinements = tuple(_refinement(item) for item in refinement_replays)
    readinesses = tuple(_readiness_replay(item) for item in reviewed_concept_readiness_replays)
    reviewed_created = reviewed_concept_created_by_this_package or any(
        item.reviewed_concept_created_by_this_package for item in readinesses
    )
    working_created = working_readback_created or any(item.working_readback_created for item in readinesses)
    memory_data_created = memory_application_data_created or any(
        item.memory_application_data_created for item in readinesses
    )
    memory_written = memory_write_performed or automatic_learning_approval_created or any(
        item.memory_write_performed for item in inputs + drafts + refinements
    ) or any(item.memory_layer_write_performed for item in readinesses)
    action_influence = action_selection_influence_created or any(
        item.action_selection_influence_created for item in inputs + drafts + refinements + readinesses
    )
    status = _trace_status(
        inputs=inputs,
        drafts=drafts,
        refinements=refinements,
        readinesses=readinesses,
        parallel_learning_pipeline_created=parallel_learning_pipeline_created,
        reviewed_concept_created_by_this_package=reviewed_created,
        working_readback_created=working_created,
        memory_application_data_created=memory_data_created,
        memory_write_performed=memory_written,
        action_selection_influence_created=action_influence,
        first_output_created=first_output_created or any(
            item.first_output_created for item in inputs + drafts + refinements + readinesses
        ),
        live_runtime_session_created=live_runtime_session_created or any(
            item.live_runtime_session_created for item in inputs + drafts + refinements + readinesses
        ),
    )
    refs = tuple(
        dict.fromkeys(
            ref
            for group in (inputs, drafts, refinements, readinesses)
            for item in group
            for ref in item.source_trace_refs
        )
    )
    return HostBodyReviewedConceptReplayTraceRecord(
        reviewed_concept_replay_trace_id=f"host_body_reviewed_concept_replay_trace:{_slug(status)}:{len(inputs)}",
        schema_version=TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_replay_plan_id=plan.reviewed_concept_replay_plan_id,
        approved_feedback_input_ids=tuple(item.approved_feedback_replay_input_id for item in inputs),
        draft_replay_ids=tuple(item.concept_candidate_draft_replay_id for item in drafts),
        refinement_replay_ids=tuple(item.concept_candidate_refinement_replay_id for item in refinements),
        reviewed_concept_readiness_replay_ids=tuple(item.reviewed_concept_readiness_replay_id for item in readinesses),
        trace_kind=_trace_kind(len(inputs), status),
        trace_status=status,
        trace_summary=_trace_summary(status, len(inputs)),
        approved_feedback_input_count=len(inputs),
        draft_replay_count=len(drafts),
        refinement_replay_count=len(refinements),
        reviewed_concept_readiness_count=len(readinesses),
        uses_existing_pipeline_only=not parallel_learning_pipeline_created,
        parallel_learning_pipeline_created=parallel_learning_pipeline_created,
        reviewed_concept_ready_count=sum(1 for item in readinesses if item.reviewed_concept_ready),
        reviewed_concept_created_by_this_package=reviewed_created,
        working_readback_created=working_created,
        memory_application_data_created=memory_data_created,
        memory_write_performed=memory_written,
        automatic_learning_approval_created=automatic_learning_approval_created
        or any(item.automatic_learning_approval_created for item in inputs + drafts + refinements + readinesses),
        teacher_approval_created=teacher_approval_created
        or any(item.teacher_approval_created for item in inputs + drafts + refinements + readinesses),
        action_selection_influence_created=action_influence,
        external_control_created=external_control_created or any(item.external_control_created for item in readinesses),
        first_output_created=first_output_created or any(
            item.first_output_created for item in inputs + drafts + refinements + readinesses
        ),
        live_runtime_session_created=live_runtime_session_created or any(
            item.live_runtime_session_created for item in inputs + drafts + refinements + readinesses
        ),
        source_trace_refs=refs,
    )


def validate_host_body_reviewed_concept_replay_trace(
    record: HostBodyReviewedConceptReplayTraceRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _trace(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.trace_status.startswith("host_body_feedback_reviewed_concept_replay_trace_recorded")
    valid = valid and item.uses_existing_pipeline_only and not item.parallel_learning_pipeline_created
    valid = valid and not _trace_has_forbidden(item)
    return {"valid": valid, "status": item.trace_status, "reasons": [] if valid else [item.trace_status]}


def build_host_body_reviewed_concept_replay_audit(
    *,
    reviewed_concept_replay_plan: HostBodyReviewedConceptReplayPlanRecord | dict[str, object] | None,
    reviewed_concept_replay_trace: HostBodyReviewedConceptReplayTraceRecord | dict[str, object] | None,
    approved_feedback_inputs: tuple[HostBodyApprovedFeedbackReplayInputRecord | dict[str, object], ...] | list[HostBodyApprovedFeedbackReplayInputRecord | dict[str, object]] = tuple(),
    draft_replays: tuple[HostBodyExistingConceptCandidateDraftReplayRecord | dict[str, object], ...] | list[HostBodyExistingConceptCandidateDraftReplayRecord | dict[str, object]] = tuple(),
    refinement_replays: tuple[HostBodyExistingConceptCandidateRefinementReplayRecord | dict[str, object], ...] | list[HostBodyExistingConceptCandidateRefinementReplayRecord | dict[str, object]] = tuple(),
    reviewed_concept_readiness_replays: tuple[HostBodyReviewedConceptReadinessReplayRecord | dict[str, object], ...] | list[HostBodyReviewedConceptReadinessReplayRecord | dict[str, object]] = tuple(),
    preferred_pass_status: str | None = None,
    force_external_control: bool = False,
    force_thought_engine_behavior: bool = False,
    force_production_behavior: bool = False,
) -> HostBodyReviewedConceptReplayAudit:
    plan = _plan(reviewed_concept_replay_plan) if reviewed_concept_replay_plan is not None else None
    trace = _trace(reviewed_concept_replay_trace) if reviewed_concept_replay_trace is not None else None
    inputs = tuple(_input(item) for item in approved_feedback_inputs)
    drafts = tuple(_draft(item) for item in draft_replays)
    refinements = tuple(_refinement(item) for item in refinement_replays)
    readinesses = tuple(_readiness_replay(item) for item in reviewed_concept_readiness_replays)
    reasons = _audit_reasons(
        plan=plan,
        trace=trace,
        inputs=inputs,
        drafts=drafts,
        refinements=refinements,
        readinesses=readinesses,
        force_external_control=force_external_control,
        force_thought_engine_behavior=force_thought_engine_behavior,
        force_production_behavior=force_production_behavior,
    )
    status = _audit_status(reasons, preferred_pass_status)
    return HostBodyReviewedConceptReplayAudit(
        reviewed_concept_replay_audit_id=f"host_body_reviewed_concept_replay_audit:{_slug(status)}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_replay_plan_id=plan.reviewed_concept_replay_plan_id if plan else None,
        source_reviewed_concept_replay_trace_id=trace.reviewed_concept_replay_trace_id if trace else None,
        replay_plan_valid=plan is not None and validate_host_body_reviewed_concept_replay_plan(plan)["valid"],
        approved_inputs_valid=all(validate_host_body_approved_feedback_replay_input(item)["valid"] for item in inputs),
        draft_replays_valid=all(validate_host_body_existing_concept_candidate_draft_replay(item)["valid"] for item in drafts),
        refinement_replays_valid=all(validate_host_body_existing_concept_candidate_refinement_replay(item)["valid"] for item in refinements),
        reviewed_concept_readiness_replays_valid=all(validate_host_body_reviewed_concept_readiness_replay(item)["valid"] for item in readinesses),
        replay_trace_valid=trace is not None and validate_host_body_reviewed_concept_replay_trace(trace)["valid"],
        host_body_feedback_pipeline_compatibility_confirmed=plan is not None,
        existing_package_90_review_path_confirmed="parallel_teacher_review" not in reasons,
        existing_package_91_refinement_path_confirmed="parallel_refinement_system" not in reasons,
        existing_package_92_reviewed_concept_path_confirmed="parallel_reviewed_concept_system" not in reasons,
        reviewed_concept_readiness_confirmed=bool(readinesses) and not reasons,
        no_parallel_teacher_review="parallel_teacher_review" not in reasons,
        no_parallel_concept_system="parallel_concept_system" not in reasons,
        no_parallel_refinement_system="parallel_refinement_system" not in reasons,
        no_parallel_reviewed_concept_system="parallel_reviewed_concept_system" not in reasons,
        no_reviewed_concept_created_by_this_package="reviewed_concept_by_package" not in reasons,
        no_working_readback_created="working_readback" not in reasons,
        no_memory_application_data_created="memory_application_data" not in reasons,
        no_memory_layer_write="memory_write" not in reasons,
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_state_persistence_write=True,
        no_automatic_learning_approval="automatic_learning_approval" not in reasons,
        no_teacher_approval_created="teacher_approval" not in reasons,
        no_task_action_selection_influence="action_influence" not in reasons,
        no_task_selected_action=True,
        no_final_action=True,
        no_direct_command=True,
        no_sandbox_execution=True,
        no_external_control="external_control" not in reasons,
        no_real_hardware_access=True,
        no_semantic_vision=True,
        no_speech_recognition=True,
        no_first_output="first_output" not in reasons,
        no_live_runtime_session="live_runtime" not in reasons,
        no_thought_engine_behavior="thought_engine" not in reasons,
        no_production_behavior="production_behavior" not in reasons,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(reasons),
        source_trace_refs=trace.source_trace_refs if trace else tuple(),
    )


def validate_host_body_reviewed_concept_replay_audit(
    record: HostBodyReviewedConceptReplayAudit | dict[str, object],
) -> dict[str, object]:
    try:
        item = _audit(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.audit_status.startswith("passed_")
    return {"valid": valid, "status": item.audit_status, "reasons": [] if valid else list(item.blocked_reasons)}


def build_host_body_reviewed_concept_replay_readiness(
    reviewed_concept_replay_audit: HostBodyReviewedConceptReplayAudit | dict[str, object] | None,
) -> HostBodyReviewedConceptReplayReadinessRecord:
    audit = _audit(reviewed_concept_replay_audit) if reviewed_concept_replay_audit is not None else None
    passed = audit is not None and audit.audit_status.startswith("passed_")
    if audit is None:
        status = "not_ready_missing_reviewed_concept_replay_audit"
    elif passed:
        status = "ready_for_host_body_reviewed_concept_working_readback_only"
    elif audit.audit_status.startswith("blocked_"):
        status = "blocked_forbidden_authority_detected"
    else:
        status = "not_ready_boundary_failure"
    return HostBodyReviewedConceptReplayReadinessRecord(
        reviewed_concept_replay_readiness_id=(
            f"host_body_reviewed_concept_replay_readiness:{audit.reviewed_concept_replay_audit_id}"
            if audit
            else "host_body_reviewed_concept_replay_readiness:missing_audit"
        ),
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_replay_audit_id=(
            audit.reviewed_concept_replay_audit_id if audit else "missing_reviewed_concept_replay_audit"
        ),
        current_verified_capability=SAFE_CLAIM if passed else "Host Body ReviewedConcept replay audit did not pass.",
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason=(
            "Integrate Host Body-derived ReviewedConcept readiness into the existing working readback path."
        ),
        ready_for_host_body_reviewed_concept_working_readback=passed,
        ready_for_host_body_readback_internal_action_influence=passed,
        ready_for_host_body_closed_loop_milestone_audit=passed,
        ready_for_memory_layer_write=False,
        ready_for_memory_application_data_creation_by_this_package=False,
        ready_for_working_readback_mutation_by_this_package=False,
        ready_for_automatic_learning_approval=False,
        ready_for_action_selection_influence=False,
        ready_for_external_control=False,
        ready_for_first_output=False,
        ready_for_live_runtime_session=False,
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=audit.source_trace_refs if audit else tuple(),
    )


def validate_host_body_reviewed_concept_replay_readiness(
    record: HostBodyReviewedConceptReplayReadinessRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _replay_readiness(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.readiness_status.startswith("ready_for_")
    valid = valid and all(
        (
            item.ready_for_host_body_reviewed_concept_working_readback,
            item.ready_for_host_body_readback_internal_action_influence,
            item.ready_for_host_body_closed_loop_milestone_audit,
        )
    )
    valid = valid and not any(
        (
            item.ready_for_memory_layer_write,
            item.ready_for_memory_application_data_creation_by_this_package,
            item.ready_for_working_readback_mutation_by_this_package,
            item.ready_for_automatic_learning_approval,
            item.ready_for_action_selection_influence,
            item.ready_for_external_control,
            item.ready_for_first_output,
            item.ready_for_live_runtime_session,
        )
    )
    return {"valid": valid, "status": item.readiness_status, "reasons": [] if valid else [item.readiness_status]}


def build_demo_uncertainty_feedback_reviewed_concept_replay() -> dict[str, object]:
    return _build_demo_bundle(
        _compatibility_payload_from_bridge_source(build_demo_uncertainty_to_learning_feedback_candidate()),
        preferred_pass_status="passed_host_body_uncertainty_reviewed_concept_replay",
    )


def build_demo_interesting_event_feedback_reviewed_concept_replay() -> dict[str, object]:
    return _build_demo_bundle(
        _compatibility_payload_from_bridge_source(build_demo_interesting_event_to_learning_feedback_candidate()),
        preferred_pass_status="passed_host_body_interesting_event_reviewed_concept_replay",
    )


def build_demo_runtime_bridge_feedback_reviewed_concept_replay() -> dict[str, object]:
    return _build_demo_bundle(
        _compatibility_payload_from_bridge_source(build_demo_deferred_runtime_bridge_to_learning_feedback_candidate()),
        preferred_pass_status="passed_host_body_runtime_bridge_reviewed_concept_replay",
    )


def build_demo_mixed_feedback_reviewed_concept_replay() -> dict[str, object]:
    return _build_mixed_demo_bundle()


def build_demo_blocked_non_approved_review_result() -> dict[str, object]:
    return _build_demo_bundle(
        _compatibility_payload_from_bridge_source(
            build_demo_uncertainty_to_learning_feedback_candidate(),
            simulated_existing_review_result="needs_more_evidence",
        )
    )


def build_demo_blocked_parallel_concept_system_reviewed_concept_replay() -> dict[str, object]:
    return _build_demo_bundle(
        _compatibility_payload_from_bridge_source(build_demo_uncertainty_to_learning_feedback_candidate()),
        creates_parallel_concept_system=True,
    )


def build_demo_blocked_reviewed_concept_created_by_this_package() -> dict[str, object]:
    return _build_demo_bundle(
        _compatibility_payload_from_bridge_source(build_demo_uncertainty_to_learning_feedback_candidate()),
        reviewed_concept_created_by_this_package=True,
    )


def build_demo_blocked_working_readback_created() -> dict[str, object]:
    return _build_demo_bundle(
        _compatibility_payload_from_bridge_source(build_demo_uncertainty_to_learning_feedback_candidate()),
        working_readback_created=True,
    )


def build_demo_blocked_memory_write_reviewed_concept_replay() -> dict[str, object]:
    return _build_demo_bundle(
        _compatibility_payload_from_bridge_source(build_demo_uncertainty_to_learning_feedback_candidate()),
        memory_write_performed=True,
    )


def build_demo_blocked_first_output_reviewed_concept_replay() -> dict[str, object]:
    return _build_demo_bundle(
        _compatibility_payload_from_bridge_source(build_demo_uncertainty_to_learning_feedback_candidate()),
        first_output_created=True,
    )


def build_demo_blocked_live_runtime_reviewed_concept_replay() -> dict[str, object]:
    return _build_demo_bundle(
        _compatibility_payload_from_bridge_source(build_demo_uncertainty_to_learning_feedback_candidate()),
        live_runtime_session_created=True,
    )


def render_host_body_reviewed_concept_replay_summary_text(
    audit: HostBodyReviewedConceptReplayAudit | dict[str, object],
    readiness: HostBodyReviewedConceptReplayReadinessRecord | dict[str, object] | None = None,
) -> str:
    item = _audit(audit)
    readiness_item = _replay_readiness(readiness) if readiness is not None else None
    lines = [
        "Host Body Feedback Through ReviewedConcept Replay",
        f"audit_status: {item.audit_status}",
        f"reviewed_concept_readiness_confirmed: {item.reviewed_concept_readiness_confirmed}",
        f"no_reviewed_concept_created_by_this_package: {item.no_reviewed_concept_created_by_this_package}",
        f"no_working_readback_created: {item.no_working_readback_created}",
        f"no_memory_application_data_created: {item.no_memory_application_data_created}",
        f"no_memory_layer_write: {item.no_memory_layer_write}",
        f"no_first_output: {item.no_first_output}",
        f"no_live_runtime_session: {item.no_live_runtime_session}",
    ]
    if readiness_item is not None:
        lines.append(f"readiness_status: {readiness_item.readiness_status}")
    return "\n".join(lines)


def render_host_body_reviewed_concept_replay_table(
    trace: HostBodyReviewedConceptReplayTraceRecord | dict[str, object],
    approved_feedback_inputs: tuple[HostBodyApprovedFeedbackReplayInputRecord | dict[str, object], ...] | list[HostBodyApprovedFeedbackReplayInputRecord | dict[str, object]] = tuple(),
    readiness_replays: tuple[HostBodyReviewedConceptReadinessReplayRecord | dict[str, object], ...] | list[HostBodyReviewedConceptReadinessReplayRecord | dict[str, object]] = tuple(),
) -> str:
    trace_item = _trace(trace)
    inputs = tuple(_input(item) for item in approved_feedback_inputs)
    readinesses = tuple(_readiness_replay(item) for item in readiness_replays)
    lines = ["candidate_kind | input_status | reviewed_concept_ready"]
    for item, readiness in zip(inputs, readinesses):
        lines.append(
            f"{item.input_candidate_kind} | {item.input_status} | {readiness.reviewed_concept_ready}"
        )
    if not inputs:
        lines.append(f"empty | {trace_item.trace_status} | False")
    return "\n".join(lines)


def _compatibility_payload_from_bridge_source(
    source_payload: dict[str, object],
    *,
    simulated_existing_review_result: str = "approved",
) -> dict[str, object]:
    plan = build_host_body_existing_learning_pipeline_compatibility_plan(
        host_body_learning_bridge_audit=source_payload["host_body_learning_bridge_audit"],
        host_body_learning_candidate_set=source_payload["host_body_learning_feedback_candidate_set"],
    )
    evidence = source_payload["host_body_learning_evidence_packets"][0]
    mapping = source_payload["host_body_learning_feedback_mappings"][0]
    bridge = source_payload["host_body_learning_feedback_bridges"][0]
    normalization = build_host_body_feedback_candidate_normalization(
        compatibility_plan=plan,
        evidence_packet=evidence,
        mapping=mapping,
        bridge=bridge,
    )
    adapter = build_host_body_feedback_existing_review_adapter(normalization=normalization)
    replay = build_host_body_feedback_existing_review_replay(
        existing_review_adapter=adapter,
        simulated_existing_review_result=simulated_existing_review_result,
    )
    compatibility = build_host_body_feedback_concept_candidate_compatibility(
        existing_review_replay=replay
    )
    trace = build_host_body_feedback_existing_learning_pipeline_trace(
        compatibility_plan=plan,
        normalizations=(normalization,),
        adapters=(adapter,),
        review_replays=(replay,),
        concept_candidate_compatibilities=(compatibility,),
    )
    audit = build_host_body_existing_learning_pipeline_compatibility_audit(
        compatibility_plan=plan,
        existing_learning_pipeline_trace=trace,
        normalizations=(normalization,),
        adapters=(adapter,),
        review_replays=(replay,),
        concept_candidate_compatibilities=(compatibility,),
    )
    return {
        "host_body_existing_learning_pipeline_compatibility_plan": plan.to_dict(),
        "host_body_feedback_candidate_normalizations": (normalization.to_dict(),),
        "host_body_feedback_existing_review_adapters": (adapter.to_dict(),),
        "host_body_feedback_existing_review_replays": (replay.to_dict(),),
        "host_body_feedback_concept_candidate_compatibilities": (compatibility.to_dict(),),
        "host_body_feedback_existing_learning_pipeline_trace": trace.to_dict(),
        "host_body_existing_learning_pipeline_compatibility_audit": audit.to_dict(),
    }


def _build_demo_bundle(
    compatibility_payload: dict[str, object],
    *,
    preferred_pass_status: str | None = None,
    creates_parallel_concept_system: bool = False,
    reviewed_concept_created_by_this_package: bool = False,
    working_readback_created: bool = False,
    memory_application_data_created: bool = False,
    memory_write_performed: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> dict[str, object]:
    plan = build_host_body_reviewed_concept_replay_plan(
        existing_learning_pipeline_compatibility_audit=compatibility_payload[
            "host_body_existing_learning_pipeline_compatibility_audit"
        ],
        existing_learning_pipeline_trace=compatibility_payload[
            "host_body_feedback_existing_learning_pipeline_trace"
        ],
    )
    source_normalization = compatibility_payload["host_body_feedback_candidate_normalizations"][0]
    source_adapter = compatibility_payload["host_body_feedback_existing_review_adapters"][0]
    source_replay = compatibility_payload["host_body_feedback_existing_review_replays"][0]
    replay_input = build_host_body_approved_feedback_replay_input(
        reviewed_concept_replay_plan=plan,
        normalization=source_normalization,
        existing_review_adapter=source_adapter,
        existing_review_replay=source_replay,
    )
    draft = build_host_body_existing_concept_candidate_draft_replay(
        approved_feedback_replay_input=replay_input,
        creates_parallel_concept_system=creates_parallel_concept_system,
    )
    refinement = build_host_body_existing_concept_candidate_refinement_replay(
        concept_candidate_draft_replay=draft
    )
    readiness_replay = build_host_body_reviewed_concept_readiness_replay(
        concept_candidate_refinement_replay=refinement,
        reviewed_concept_created_by_this_package=reviewed_concept_created_by_this_package,
        working_readback_created=working_readback_created,
        memory_application_data_created=memory_application_data_created,
        memory_layer_write_performed=memory_write_performed,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    trace = build_host_body_reviewed_concept_replay_trace(
        reviewed_concept_replay_plan=plan,
        approved_feedback_inputs=(replay_input,),
        draft_replays=(draft,),
        refinement_replays=(refinement,),
        reviewed_concept_readiness_replays=(readiness_replay,),
    )
    audit = build_host_body_reviewed_concept_replay_audit(
        reviewed_concept_replay_plan=plan,
        reviewed_concept_replay_trace=trace,
        approved_feedback_inputs=(replay_input,),
        draft_replays=(draft,),
        refinement_replays=(refinement,),
        reviewed_concept_readiness_replays=(readiness_replay,),
        preferred_pass_status=preferred_pass_status,
    )
    readiness = build_host_body_reviewed_concept_replay_readiness(audit)
    return _payload(plan, (replay_input,), (draft,), (refinement,), (readiness_replay,), trace, audit, readiness)


def _build_mixed_demo_bundle() -> dict[str, object]:
    source_payloads = (
        _compatibility_payload_from_bridge_source(build_demo_uncertainty_to_learning_feedback_candidate()),
        _compatibility_payload_from_bridge_source(build_demo_interesting_event_to_learning_feedback_candidate()),
        _compatibility_payload_from_bridge_source(build_demo_deferred_runtime_bridge_to_learning_feedback_candidate()),
    )
    plan = build_host_body_reviewed_concept_replay_plan(
        existing_learning_pipeline_compatibility_audit=source_payloads[0][
            "host_body_existing_learning_pipeline_compatibility_audit"
        ],
        existing_learning_pipeline_trace=source_payloads[0][
            "host_body_feedback_existing_learning_pipeline_trace"
        ],
    )
    inputs = []
    drafts = []
    refinements = []
    readinesses = []
    for payload in source_payloads:
        replay_input = build_host_body_approved_feedback_replay_input(
            reviewed_concept_replay_plan=plan,
            normalization=payload["host_body_feedback_candidate_normalizations"][0],
            existing_review_adapter=payload["host_body_feedback_existing_review_adapters"][0],
            existing_review_replay=payload["host_body_feedback_existing_review_replays"][0],
        )
        draft = build_host_body_existing_concept_candidate_draft_replay(
            approved_feedback_replay_input=replay_input
        )
        refinement = build_host_body_existing_concept_candidate_refinement_replay(
            concept_candidate_draft_replay=draft
        )
        readiness_replay = build_host_body_reviewed_concept_readiness_replay(
            concept_candidate_refinement_replay=refinement
        )
        inputs.append(replay_input)
        drafts.append(draft)
        refinements.append(refinement)
        readinesses.append(readiness_replay)
    trace = build_host_body_reviewed_concept_replay_trace(
        reviewed_concept_replay_plan=plan,
        approved_feedback_inputs=tuple(inputs),
        draft_replays=tuple(drafts),
        refinement_replays=tuple(refinements),
        reviewed_concept_readiness_replays=tuple(readinesses),
    )
    audit = build_host_body_reviewed_concept_replay_audit(
        reviewed_concept_replay_plan=plan,
        reviewed_concept_replay_trace=trace,
        approved_feedback_inputs=tuple(inputs),
        draft_replays=tuple(drafts),
        refinement_replays=tuple(refinements),
        reviewed_concept_readiness_replays=tuple(readinesses),
    )
    readiness = build_host_body_reviewed_concept_replay_readiness(audit)
    return _payload(plan, tuple(inputs), tuple(drafts), tuple(refinements), tuple(readinesses), trace, audit, readiness)


def _payload(
    plan: HostBodyReviewedConceptReplayPlanRecord,
    inputs: tuple[HostBodyApprovedFeedbackReplayInputRecord, ...],
    drafts: tuple[HostBodyExistingConceptCandidateDraftReplayRecord, ...],
    refinements: tuple[HostBodyExistingConceptCandidateRefinementReplayRecord, ...],
    readinesses: tuple[HostBodyReviewedConceptReadinessReplayRecord, ...],
    trace: HostBodyReviewedConceptReplayTraceRecord,
    audit: HostBodyReviewedConceptReplayAudit,
    readiness: HostBodyReviewedConceptReplayReadinessRecord,
) -> dict[str, object]:
    return {
        "host_body_reviewed_concept_replay_plan": plan.to_dict(),
        "host_body_approved_feedback_replay_inputs": tuple(item.to_dict() for item in inputs),
        "host_body_existing_concept_candidate_draft_replays": tuple(item.to_dict() for item in drafts),
        "host_body_existing_concept_candidate_refinement_replays": tuple(item.to_dict() for item in refinements),
        "host_body_reviewed_concept_readiness_replays": tuple(item.to_dict() for item in readinesses),
        "host_body_reviewed_concept_replay_trace": trace.to_dict(),
        "host_body_reviewed_concept_replay_audit": audit.to_dict(),
        "host_body_reviewed_concept_replay_readiness": readiness.to_dict(),
        "rendered_host_body_reviewed_concept_replay_summary": render_host_body_reviewed_concept_replay_summary_text(
            audit, readiness
        ),
        "rendered_host_body_reviewed_concept_replay_table": render_host_body_reviewed_concept_replay_table(
            trace, inputs, readinesses
        ),
    }


def _plan(record: HostBodyReviewedConceptReplayPlanRecord | dict[str, object]) -> HostBodyReviewedConceptReplayPlanRecord:
    if isinstance(record, HostBodyReviewedConceptReplayPlanRecord):
        return record
    return HostBodyReviewedConceptReplayPlanRecord.from_dict(record)


def _input(record: HostBodyApprovedFeedbackReplayInputRecord | dict[str, object]) -> HostBodyApprovedFeedbackReplayInputRecord:
    if isinstance(record, HostBodyApprovedFeedbackReplayInputRecord):
        return record
    return HostBodyApprovedFeedbackReplayInputRecord.from_dict(record)


def _draft(record: HostBodyExistingConceptCandidateDraftReplayRecord | dict[str, object]) -> HostBodyExistingConceptCandidateDraftReplayRecord:
    if isinstance(record, HostBodyExistingConceptCandidateDraftReplayRecord):
        return record
    return HostBodyExistingConceptCandidateDraftReplayRecord.from_dict(record)


def _refinement(record: HostBodyExistingConceptCandidateRefinementReplayRecord | dict[str, object]) -> HostBodyExistingConceptCandidateRefinementReplayRecord:
    if isinstance(record, HostBodyExistingConceptCandidateRefinementReplayRecord):
        return record
    return HostBodyExistingConceptCandidateRefinementReplayRecord.from_dict(record)


def _readiness_replay(record: HostBodyReviewedConceptReadinessReplayRecord | dict[str, object]) -> HostBodyReviewedConceptReadinessReplayRecord:
    if isinstance(record, HostBodyReviewedConceptReadinessReplayRecord):
        return record
    return HostBodyReviewedConceptReadinessReplayRecord.from_dict(record)


def _trace(record: HostBodyReviewedConceptReplayTraceRecord | dict[str, object]) -> HostBodyReviewedConceptReplayTraceRecord:
    if isinstance(record, HostBodyReviewedConceptReplayTraceRecord):
        return record
    return HostBodyReviewedConceptReplayTraceRecord.from_dict(record)


def _audit(record: HostBodyReviewedConceptReplayAudit | dict[str, object]) -> HostBodyReviewedConceptReplayAudit:
    if isinstance(record, HostBodyReviewedConceptReplayAudit):
        return record
    return HostBodyReviewedConceptReplayAudit.from_dict(record)


def _replay_readiness(record: HostBodyReviewedConceptReplayReadinessRecord | dict[str, object]) -> HostBodyReviewedConceptReplayReadinessRecord:
    if isinstance(record, HostBodyReviewedConceptReplayReadinessRecord):
        return record
    return HostBodyReviewedConceptReplayReadinessRecord.from_dict(record)


def _value(record: dict[str, Any] | None, key: str) -> str | None:
    value = record.get(key) if record else None
    return str(value) if value is not None else None


def _refs_from(*records: dict[str, Any] | None) -> tuple[str, ...]:
    refs: list[str] = []
    for record in records:
        if not record:
            continue
        value = record.get("source_trace_refs", ())
        if isinstance(value, list | tuple):
            refs.extend(str(item) for item in value)
    return tuple(dict.fromkeys(refs))


def _status_passed(record: dict[str, Any] | None, key: str) -> bool:
    return bool(record and str(record.get(key, "")).startswith("passed_"))


def _status_recorded(record: dict[str, Any] | None, key: str) -> bool:
    return bool(record and str(record.get(key, "")).startswith("host_body_feedback_existing_learning_pipeline_trace_recorded"))


def _plan_status(**kwargs: Any) -> str:
    if not _status_passed(kwargs["audit"], "audit_status"):
        return "blocked_missing_existing_learning_pipeline_compatibility_audit"
    if not _status_recorded(kwargs["trace"], "trace_status"):
        return "blocked_missing_existing_learning_pipeline_trace"
    if not all(
        (
            kwargs["reuse_existing_review_path_required"],
            kwargs["reuse_existing_concept_path_required"],
            kwargs["reuse_existing_refinement_path_required"],
            kwargs["reuse_existing_reviewed_concept_path_required"],
        )
    ):
        return "blocked_forbidden_authority_detected"
    if kwargs["parallel_teacher_review_allowed"]:
        return "blocked_parallel_teacher_review_allowed"
    if kwargs["parallel_concept_system_allowed"]:
        return "blocked_parallel_concept_system_allowed"
    if kwargs["automatic_learning_approval_allowed"]:
        return "blocked_automatic_learning_approval_allowed"
    if kwargs["memory_write_allowed"]:
        return "blocked_memory_write_allowed"
    if kwargs["working_readback_mutation_allowed"]:
        return "blocked_working_readback_mutation_allowed"
    if kwargs["action_selection_influence_allowed"]:
        return "blocked_action_selection_influence_allowed"
    if kwargs["first_output_allowed"]:
        return "blocked_first_output_allowed"
    if kwargs["live_runtime_session_allowed"]:
        return "blocked_live_runtime_allowed"
    return "reviewed_concept_replay_plan_created"


def _plan_summary(status: str) -> str:
    if status == "reviewed_concept_replay_plan_created":
        return "Approved Host Body feedback may be replayed through existing Package 90 to 92 readiness."
    return "Host Body ReviewedConcept replay plan is blocked."


def _input_status(**kwargs: Any) -> str:
    if kwargs["adapter"] is None:
        return "blocked_missing_review_adapter"
    if kwargs["result"] != "approved":
        return "blocked_non_approved_review_result"
    if kwargs["teacher_approval_created"]:
        return "blocked_teacher_approval_created"
    if kwargs["automatic_learning_approval_created"]:
        return "blocked_automatic_learning_approval_detected"
    if kwargs["concept_candidate_created_by_this_record"]:
        return "blocked_concept_candidate_created_by_input"
    if kwargs["reviewed_concept_created_by_this_record"]:
        return "blocked_reviewed_concept_created_by_input"
    if kwargs["memory_write_performed"]:
        return "blocked_memory_write_detected"
    if kwargs["working_readback_mutation_performed"] or kwargs["action_selection_influence_created"]:
        return "blocked_action_selection_influence_detected"
    if kwargs["first_output_created"]:
        return "blocked_first_output_detected"
    if kwargs["live_runtime_session_created"]:
        return "blocked_live_runtime_detected"
    return "approved_host_body_feedback_replay_input_recorded"


def _input_summary(status: str, candidate_kind: str) -> str:
    if status == "approved_host_body_feedback_replay_input_recorded":
        return f"Approved {candidate_kind} is ready for existing ConceptCandidate draft replay."
    return "Host Body approved feedback replay input is blocked."


def _input_has_forbidden(item: HostBodyApprovedFeedbackReplayInputRecord) -> bool:
    return any(
        (
            item.teacher_approval_created,
            item.automatic_learning_approval_created,
            item.concept_candidate_created_by_this_record,
            item.reviewed_concept_created_by_this_record,
            item.memory_write_performed,
            item.working_readback_mutation_performed,
            item.action_selection_influence_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _draft_status(item: HostBodyApprovedFeedbackReplayInputRecord, **kwargs: Any) -> str:
    if not validate_host_body_approved_feedback_replay_input(item)["valid"]:
        return "blocked_invalid_approved_feedback_input"
    if kwargs["creates_parallel_concept_system"]:
        return "blocked_parallel_concept_system_detected"
    if kwargs["concept_candidate_created_by_this_package"]:
        return "blocked_concept_candidate_created_by_this_package"
    if kwargs["teacher_approval_created"]:
        return "blocked_teacher_approval_created"
    if kwargs["automatic_learning_approval_created"]:
        return "blocked_automatic_learning_approval_detected"
    if kwargs["reviewed_concept_created"]:
        return "blocked_reviewed_concept_created"
    if kwargs["memory_write_performed"]:
        return "blocked_memory_write_detected"
    if kwargs["working_readback_mutation_performed"] or kwargs["action_selection_influence_created"]:
        return "blocked_action_selection_influence_detected"
    if kwargs["first_output_created"]:
        return "blocked_first_output_detected"
    if kwargs["live_runtime_session_created"]:
        return "blocked_live_runtime_detected"
    return "existing_concept_candidate_draft_replay_ready"


def _draft_kind(candidate_kind: str, status: str) -> str:
    if status.startswith("blocked_"):
        return "blocked_draft_replay"
    return {
        "host_body_uncertainty_feedback_candidate": "host_body_uncertainty_concept_candidate_draft_replay",
        "host_body_interesting_event_feedback_candidate": "host_body_interesting_event_concept_candidate_draft_replay",
        "host_body_teacher_review_feedback_candidate": "host_body_teacher_review_concept_candidate_draft_replay",
        "host_body_runtime_bridge_feedback_candidate": "host_body_runtime_bridge_concept_candidate_draft_replay",
    }.get(candidate_kind, "blocked_draft_replay")


def _draft_summary(status: str, candidate_kind: str) -> str:
    if status == "existing_concept_candidate_draft_replay_ready":
        return f"{candidate_kind} is replay-ready for the existing Package 90 draft path."
    return "Host Body ConceptCandidate draft replay is blocked."


def _concept_scope(candidate_kind: str) -> str:
    return {
        "host_body_uncertainty_feedback_candidate": "host_body_uncertainty_only",
        "host_body_interesting_event_feedback_candidate": "host_body_interesting_event_only",
        "host_body_teacher_review_feedback_candidate": "host_body_teacher_review_request_only",
        "host_body_runtime_bridge_feedback_candidate": "host_body_runtime_bridge_only",
    }.get(candidate_kind, "host_body_only")


def _draft_has_forbidden(item: HostBodyExistingConceptCandidateDraftReplayRecord) -> bool:
    return any(
        (
            item.creates_parallel_concept_system,
            item.concept_candidate_created_by_this_package,
            item.teacher_approval_created,
            item.automatic_learning_approval_created,
            item.reviewed_concept_created,
            item.memory_write_performed,
            item.working_readback_mutation_performed,
            item.action_selection_influence_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _refinement_status(draft: HostBodyExistingConceptCandidateDraftReplayRecord, **kwargs: Any) -> str:
    if not validate_host_body_existing_concept_candidate_draft_replay(draft)["valid"]:
        return "blocked_invalid_draft_replay"
    if kwargs["creates_parallel_refinement_system"]:
        return "blocked_parallel_refinement_system_detected"
    if not kwargs["counterexample_scope_checked"]:
        return "blocked_counterexample_scope_missing"
    if kwargs["refined_concept_candidate_created_by_this_package"]:
        return "blocked_refined_concept_candidate_created_by_this_package"
    if kwargs["teacher_approval_created"]:
        return "blocked_teacher_approval_created"
    if kwargs["automatic_learning_approval_created"]:
        return "blocked_automatic_learning_approval_detected"
    if kwargs["reviewed_concept_created"]:
        return "blocked_reviewed_concept_created"
    if kwargs["memory_write_performed"]:
        return "blocked_memory_write_detected"
    if kwargs["working_readback_mutation_performed"] or kwargs["action_selection_influence_created"]:
        return "blocked_action_selection_influence_detected"
    if kwargs["first_output_created"]:
        return "blocked_first_output_detected"
    if kwargs["live_runtime_session_created"]:
        return "blocked_live_runtime_detected"
    return "existing_concept_candidate_refinement_replay_ready"


def _refinement_kind(draft_kind: str, status: str) -> str:
    if status.startswith("blocked_"):
        return "blocked_refinement_replay"
    if "uncertainty" in draft_kind:
        return "host_body_uncertainty_existing_refinement_replay"
    if "interesting_event" in draft_kind:
        return "host_body_interesting_event_existing_refinement_replay"
    if "runtime_bridge" in draft_kind:
        return "host_body_runtime_bridge_existing_refinement_replay"
    return "host_body_concept_candidate_existing_refinement_replay"


def _refinement_summary(status: str) -> str:
    if status == "existing_concept_candidate_refinement_replay_ready":
        return "Host Body draft replay is ready for existing Package 91 refinement replay."
    return "Host Body ConceptCandidate refinement replay is blocked."


def _refinement_has_forbidden(item: HostBodyExistingConceptCandidateRefinementReplayRecord) -> bool:
    return any(
        (
            item.creates_parallel_refinement_system,
            item.refined_concept_candidate_created_by_this_package,
            item.teacher_approval_created,
            item.automatic_learning_approval_created,
            item.reviewed_concept_created,
            item.memory_write_performed,
            item.working_readback_mutation_performed,
            item.action_selection_influence_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _readiness_replay_status(refinement: HostBodyExistingConceptCandidateRefinementReplayRecord, **kwargs: Any) -> str:
    if not validate_host_body_existing_concept_candidate_refinement_replay(refinement)["valid"]:
        return "blocked_invalid_refinement_replay"
    if kwargs["creates_parallel_reviewed_concept_system"]:
        return "blocked_parallel_reviewed_concept_system_detected"
    if kwargs["reviewed_concept_created_by_this_package"]:
        return "blocked_reviewed_concept_created_by_this_package"
    if kwargs["working_readback_created"]:
        return "blocked_working_readback_created"
    if kwargs["memory_application_data_created"]:
        return "blocked_memory_application_data_created"
    if kwargs["memory_layer_write_performed"]:
        return "blocked_memory_write_detected"
    if kwargs["automatic_learning_approval_created"]:
        return "blocked_automatic_learning_approval_detected"
    if kwargs["teacher_approval_created"]:
        return "blocked_teacher_approval_created"
    if kwargs["action_selection_influence_created"]:
        return "blocked_action_selection_influence_detected"
    if kwargs["external_control_created"]:
        return "blocked_external_control_detected"
    if kwargs["first_output_created"]:
        return "blocked_first_output_detected"
    if kwargs["live_runtime_session_created"]:
        return "blocked_live_runtime_detected"
    return "host_body_reviewed_concept_readiness_replay_ready"


def _readiness_replay_kind(refinement_kind: str, status: str) -> str:
    if status.startswith("blocked_"):
        return "blocked_reviewed_concept_replay"
    if "uncertainty" in refinement_kind:
        return "host_body_uncertainty_reviewed_concept_readiness_replay"
    if "interesting_event" in refinement_kind:
        return "host_body_interesting_event_reviewed_concept_readiness_replay"
    if "runtime_bridge" in refinement_kind:
        return "host_body_runtime_bridge_reviewed_concept_readiness_replay"
    return "host_body_feedback_reviewed_concept_readiness_replay"


def _readiness_replay_summary(status: str) -> str:
    if status == "host_body_reviewed_concept_readiness_replay_ready":
        return "Host Body refined ConceptCandidate replay is ready for existing Package 92 ReviewedConcept path."
    return "Host Body ReviewedConcept readiness replay is blocked."


def _readiness_replay_has_forbidden(item: HostBodyReviewedConceptReadinessReplayRecord) -> bool:
    return any(
        (
            item.creates_parallel_reviewed_concept_system,
            item.reviewed_concept_created_by_this_package,
            item.working_readback_created,
            item.memory_application_data_created,
            item.memory_layer_write_performed,
            item.automatic_learning_approval_created,
            item.teacher_approval_created,
            item.action_selection_influence_created,
            item.external_control_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _trace_status(
    *,
    inputs: tuple[HostBodyApprovedFeedbackReplayInputRecord, ...],
    drafts: tuple[HostBodyExistingConceptCandidateDraftReplayRecord, ...],
    refinements: tuple[HostBodyExistingConceptCandidateRefinementReplayRecord, ...],
    readinesses: tuple[HostBodyReviewedConceptReadinessReplayRecord, ...],
    parallel_learning_pipeline_created: bool,
    reviewed_concept_created_by_this_package: bool,
    working_readback_created: bool,
    memory_application_data_created: bool,
    memory_write_performed: bool,
    action_selection_influence_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
) -> str:
    if any(not validate_host_body_approved_feedback_replay_input(item)["valid"] for item in inputs):
        return "blocked_invalid_approved_feedback_input"
    if any(not validate_host_body_existing_concept_candidate_draft_replay(item)["valid"] for item in drafts):
        return "blocked_invalid_draft_replay"
    if any(not validate_host_body_existing_concept_candidate_refinement_replay(item)["valid"] for item in refinements):
        return "blocked_invalid_refinement_replay"
    if any(not validate_host_body_reviewed_concept_readiness_replay(item)["valid"] for item in readinesses):
        return "blocked_invalid_reviewed_concept_readiness_replay"
    if parallel_learning_pipeline_created:
        return "blocked_parallel_learning_pipeline_detected"
    if reviewed_concept_created_by_this_package:
        return "blocked_reviewed_concept_created_by_this_package"
    if working_readback_created:
        return "blocked_working_readback_created"
    if memory_application_data_created:
        return "blocked_memory_application_data_created"
    if memory_write_performed:
        return "blocked_memory_write_detected"
    if action_selection_influence_created:
        return "blocked_action_selection_influence_detected"
    if first_output_created:
        return "blocked_first_output_detected"
    if live_runtime_session_created:
        return "blocked_live_runtime_detected"
    if not inputs:
        return "host_body_feedback_reviewed_concept_replay_trace_recorded_empty"
    return "host_body_feedback_reviewed_concept_replay_trace_recorded"


def _trace_kind(count: int, status: str) -> str:
    if status.startswith("blocked_"):
        return "blocked_reviewed_concept_replay_trace"
    if count == 0:
        return "empty_host_body_feedback_reviewed_concept_replay"
    if count > 1:
        return "mixed_host_body_feedback_reviewed_concept_replay"
    return "single_host_body_feedback_reviewed_concept_replay"


def _trace_summary(status: str, count: int) -> str:
    if status == "host_body_feedback_reviewed_concept_replay_trace_recorded":
        return f"{count} Host Body feedback item(s) replayed through existing ReviewedConcept readiness path."
    if status == "host_body_feedback_reviewed_concept_replay_trace_recorded_empty":
        return "Empty Host Body ReviewedConcept replay trace recorded."
    return "Host Body ReviewedConcept replay trace is blocked."


def _trace_has_forbidden(item: HostBodyReviewedConceptReplayTraceRecord) -> bool:
    return any(
        (
            item.parallel_learning_pipeline_created,
            item.reviewed_concept_created_by_this_package,
            item.working_readback_created,
            item.memory_application_data_created,
            item.memory_write_performed,
            item.automatic_learning_approval_created,
            item.teacher_approval_created,
            item.action_selection_influence_created,
            item.external_control_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _audit_reasons(
    *,
    plan: HostBodyReviewedConceptReplayPlanRecord | None,
    trace: HostBodyReviewedConceptReplayTraceRecord | None,
    inputs: tuple[HostBodyApprovedFeedbackReplayInputRecord, ...],
    drafts: tuple[HostBodyExistingConceptCandidateDraftReplayRecord, ...],
    refinements: tuple[HostBodyExistingConceptCandidateRefinementReplayRecord, ...],
    readinesses: tuple[HostBodyReviewedConceptReadinessReplayRecord, ...],
    force_external_control: bool,
    force_thought_engine_behavior: bool,
    force_production_behavior: bool,
) -> list[str]:
    reasons: list[str] = []
    if plan is None:
        reasons.append("missing_plan")
    elif plan.plan_status == "blocked_parallel_teacher_review_allowed":
        reasons.append("parallel_teacher_review")
    elif plan.plan_status == "blocked_parallel_concept_system_allowed":
        reasons.append("parallel_concept_system")
    elif plan.plan_status == "blocked_automatic_learning_approval_allowed":
        reasons.append("automatic_learning_approval")
    elif plan.plan_status == "blocked_memory_write_allowed":
        reasons.append("memory_write")
    elif plan.plan_status == "blocked_working_readback_mutation_allowed":
        reasons.append("working_readback")
    elif plan.plan_status == "blocked_action_selection_influence_allowed":
        reasons.append("action_influence")
    elif plan.plan_status == "blocked_first_output_allowed":
        reasons.append("first_output")
    elif plan.plan_status == "blocked_live_runtime_allowed":
        reasons.append("live_runtime")
    if any(item.creates_parallel_concept_system for item in drafts):
        reasons.append("parallel_concept_system")
    if any(item.creates_parallel_refinement_system for item in refinements):
        reasons.append("parallel_refinement_system")
    if any(item.creates_parallel_reviewed_concept_system for item in readinesses):
        reasons.append("parallel_reviewed_concept_system")
    if any(item.reviewed_concept_created_by_this_record for item in inputs) or any(
        item.reviewed_concept_created for item in drafts + refinements
    ) or any(item.reviewed_concept_created_by_this_package for item in readinesses) or (
        trace and trace.reviewed_concept_created_by_this_package
    ):
        reasons.append("reviewed_concept_by_package")
    if any(item.working_readback_mutation_performed for item in inputs + drafts + refinements) or any(
        item.working_readback_created for item in readinesses
    ) or (trace and trace.working_readback_created):
        reasons.append("working_readback")
    if any(item.memory_application_data_created for item in readinesses) or (
        trace and trace.memory_application_data_created
    ):
        reasons.append("memory_application_data")
    if any(item.memory_write_performed for item in inputs + drafts + refinements) or any(
        item.memory_layer_write_performed for item in readinesses
    ) or (trace and trace.memory_write_performed):
        reasons.append("memory_write")
    if any(item.automatic_learning_approval_created for item in inputs + drafts + refinements + readinesses) or (
        trace and trace.automatic_learning_approval_created
    ):
        reasons.append("automatic_learning_approval")
    if any(item.teacher_approval_created for item in inputs + drafts + refinements + readinesses) or (
        trace and trace.teacher_approval_created
    ):
        reasons.append("teacher_approval")
    if any(item.action_selection_influence_created for item in inputs + drafts + refinements + readinesses) or (
        trace and trace.action_selection_influence_created
    ):
        reasons.append("action_influence")
    if force_external_control or any(item.external_control_created for item in readinesses) or (
        trace and trace.external_control_created
    ):
        reasons.append("external_control")
    if any(item.first_output_created for item in inputs + drafts + refinements + readinesses) or (
        trace and trace.first_output_created
    ):
        reasons.append("first_output")
    if any(item.live_runtime_session_created for item in inputs + drafts + refinements + readinesses) or (
        trace and trace.live_runtime_session_created
    ):
        reasons.append("live_runtime")
    if force_thought_engine_behavior:
        reasons.append("thought_engine")
    if force_production_behavior:
        reasons.append("production_behavior")
    if any(not validate_host_body_approved_feedback_replay_input(item)["valid"] for item in inputs):
        reasons.append("invalid_input")
    if any(not validate_host_body_existing_concept_candidate_draft_replay(item)["valid"] for item in drafts):
        reasons.append("invalid_draft")
    if any(not validate_host_body_existing_concept_candidate_refinement_replay(item)["valid"] for item in refinements):
        reasons.append("invalid_refinement")
    if any(not validate_host_body_reviewed_concept_readiness_replay(item)["valid"] for item in readinesses):
        reasons.append("invalid_readiness")
    if trace is None or not validate_host_body_reviewed_concept_replay_trace(trace)["valid"]:
        reasons.append("invalid_trace")
    return list(dict.fromkeys(reasons))


def _audit_status(reasons: list[str], preferred_pass_status: str | None) -> str:
    priority = (
        ("missing_plan", "blocked_missing_replay_plan"),
        ("parallel_teacher_review", "blocked_parallel_teacher_review_detected"),
        ("parallel_concept_system", "blocked_parallel_concept_system_detected"),
        ("reviewed_concept_by_package", "blocked_reviewed_concept_created_by_this_package"),
        ("working_readback", "blocked_working_readback_created"),
        ("memory_application_data", "blocked_memory_application_data_created"),
        ("memory_write", "blocked_memory_write_detected"),
        ("automatic_learning_approval", "blocked_automatic_learning_approval_detected"),
        ("teacher_approval", "blocked_teacher_approval_created"),
        ("action_influence", "blocked_action_selection_influence_detected"),
        ("external_control", "blocked_external_control_detected"),
        ("first_output", "blocked_first_output_detected"),
        ("live_runtime", "blocked_live_runtime_detected"),
        ("production_behavior", "blocked_production_behavior_detected"),
        ("invalid_input", "blocked_invalid_approved_feedback_input"),
        ("invalid_draft", "blocked_invalid_concept_candidate_draft_replay"),
        ("invalid_refinement", "blocked_invalid_concept_candidate_refinement_replay"),
        ("invalid_readiness", "blocked_invalid_reviewed_concept_readiness_replay"),
        ("invalid_trace", "blocked_invalid_replay_trace"),
    )
    for reason, status in priority:
        if reason in reasons:
            return status
    return preferred_pass_status or "passed_host_body_feedback_through_reviewed_concept_replay"


def _readiness_summary(status: str) -> str:
    if status.startswith("ready_for_"):
        return "Host Body ReviewedConcept replay is ready for the next working readback package."
    if status.startswith("blocked_"):
        return "Host Body ReviewedConcept replay readiness is blocked by forbidden authority."
    return "Host Body ReviewedConcept replay readiness is not established."
