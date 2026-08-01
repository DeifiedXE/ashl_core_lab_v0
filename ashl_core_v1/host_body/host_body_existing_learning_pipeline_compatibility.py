"""Host Body feedback compatibility with the existing learning pipeline."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.host_body.host_body_learning_feedback_bridge import (
    build_demo_deferred_runtime_bridge_to_learning_feedback_candidate,
    build_demo_host_body_learning_feedback_candidate_set,
    build_demo_interesting_event_to_learning_feedback_candidate,
    build_demo_teacher_review_request_to_learning_feedback_candidate,
    build_demo_uncertainty_to_learning_feedback_candidate,
)


SOURCE_ENGINE = "host_body"

PLAN_SCHEMA_VERSION = "qingyin_host_body_existing_learning_pipeline_compatibility_plan_v0"
NORMALIZATION_SCHEMA_VERSION = "qingyin_host_body_feedback_candidate_normalization_v0"
ADAPTER_SCHEMA_VERSION = "qingyin_host_body_feedback_existing_review_adapter_v0"
REPLAY_SCHEMA_VERSION = "qingyin_host_body_feedback_existing_review_replay_v0"
CONCEPT_COMPAT_SCHEMA_VERSION = "qingyin_host_body_feedback_concept_candidate_compatibility_v0"
TRACE_SCHEMA_VERSION = "qingyin_host_body_existing_learning_pipeline_trace_v0"
AUDIT_SCHEMA_VERSION = "qingyin_host_body_existing_learning_pipeline_compatibility_audit_v0"
READINESS_SCHEMA_VERSION = "qingyin_host_body_existing_learning_pipeline_readiness_v0"

COMPATIBILITY_NAME = "host_body_feedback_existing_learning_pipeline_compatibility"
COMPATIBILITY_KIND = "adapter_and_replay_compatibility"

EXISTING_PIPELINE_PACKAGES = ("Package 90", "Package 91", "Package 92")
EXISTING_PIPELINE_STAGES = (
    "existing_learning_feedback_candidate_review",
    "existing_concept_candidate_draft",
    "existing_concept_candidate_refinement_readiness",
    "existing_reviewed_concept_path_readiness",
)
ALLOWED_HOST_BODY_CANDIDATE_KINDS = (
    "host_body_feedback_candidate",
    "host_body_uncertainty_feedback_candidate",
    "host_body_interesting_event_feedback_candidate",
    "host_body_teacher_review_feedback_candidate",
    "host_body_runtime_bridge_feedback_candidate",
    "host_body_active_perception_feedback_candidate",
    "host_body_auditory_grounding_feedback_candidate",
)
FORBIDDEN_PARALLEL_PIPELINE_OUTPUTS = (
    "parallel_teacher_review",
    "parallel_concept_candidate_system",
    "direct_reviewed_concept_creation",
    "direct_memory_write",
    "automatic_learning_approval",
    "action_selection_influence",
)
ALLOWED_REVIEW_RESULTS = (
    "approved",
    "rejected",
    "deferred",
    "needs_more_evidence",
    "conflict_detected",
    "blocked",
)

SAFE_CLAIM = (
    "ASHL Core v1 can normalize Host Body LearningFeedbackCandidate bridge records "
    "and verify compatibility with the existing Package 90 to 92 learning pipeline."
)
BLOCKED_CLAIMS = (
    "no_parallel_teacher_review",
    "no_parallel_concept_system",
    "no_concept_candidate_created_by_this_package",
    "no_reviewed_concept_created_by_this_package",
    "no_memory_layer_write",
    "no_automatic_learning_approval",
    "no_teacher_approval_created",
    "no_task_action_selection_influence",
    "no_external_control",
    "no_first_output",
    "no_live_runtime_session",
)
READINESS_NEXT_PACKAGE = (
    "Package 110 / ASHL Core v1 Host Body Feedback Through ReviewedConcept Replay Minimal v0"
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


def _tuple_of_dict(
    name: str, value: tuple[dict[str, Any], ...] | list[dict[str, Any]]
) -> tuple[dict[str, Any], ...]:
    items = tuple(dict(item) for item in value)
    if not all(isinstance(item, dict) for item in items):
        raise TypeError(f"{name} must contain only dictionaries")
    return items


def _slug(text: str | None) -> str:
    safe = [char.lower() if char.isalnum() else "_" for char in str(text or "none")]
    return "_".join("".join(safe).split("_"))[:100] or "empty"


@dataclass(frozen=True)
class HostBodyExistingLearningPipelineCompatibilityPlanRecord:
    compatibility_plan_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_learning_bridge_audit_id: str | None
    source_host_body_learning_candidate_set_id: str | None
    compatibility_name: str
    compatibility_kind: str
    existing_pipeline_packages: tuple[str, ...]
    existing_pipeline_stages: tuple[str, ...]
    allowed_host_body_candidate_kinds: tuple[str, ...]
    forbidden_parallel_pipeline_outputs: tuple[str, ...]
    reuse_existing_teacher_review_required: bool
    new_teacher_review_system_allowed: bool
    new_concept_system_allowed: bool
    direct_reviewed_concept_allowed: bool
    memory_write_allowed: bool
    automatic_learning_approval_allowed: bool
    action_selection_influence_allowed: bool
    first_output_allowed: bool
    live_runtime_session_allowed: bool
    plan_status: str
    plan_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PLAN_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_existing_learning_pipeline_compatibility_plan_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.compatibility_name != COMPATIBILITY_NAME:
            raise ValueError("compatibility_name must be host_body_feedback_existing_learning_pipeline_compatibility")
        if self.compatibility_kind != COMPATIBILITY_KIND:
            raise ValueError("compatibility_kind must be adapter_and_replay_compatibility")
        if self.plan_status not in {
            "compatibility_plan_created",
            "blocked_missing_host_body_learning_bridge_audit",
            "blocked_missing_candidate_set",
            "blocked_new_teacher_review_system_allowed",
            "blocked_new_concept_system_allowed",
            "blocked_direct_reviewed_concept_allowed",
            "blocked_memory_write_allowed",
            "blocked_action_selection_influence_allowed",
            "blocked_first_output_allowed",
            "blocked_live_runtime_allowed",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown plan_status: {self.plan_status}")
        for name in (
            "existing_pipeline_packages",
            "existing_pipeline_stages",
            "allowed_host_body_candidate_kinds",
            "forbidden_parallel_pipeline_outputs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyExistingLearningPipelineCompatibilityPlanRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyFeedbackCandidateNormalizationRecord:
    normalization_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_compatibility_plan_id: str
    source_host_body_feedback_candidate_id: str | None
    source_evidence_packet_id: str | None
    source_mapping_id: str | None
    source_bridge_id: str | None
    source_candidate_kind: str
    normalized_learning_feedback_kind: str
    normalized_evidence_scope: str
    normalized_evidence_summary: str
    normalized_payload: dict[str, Any]
    host_body_source_preserved: bool
    teacher_review_required_preserved: bool
    safe_for_existing_learning_review: bool
    semantic_vision_created: bool
    speech_recognition_created: bool
    new_teacher_review_system_created: bool
    new_concept_system_created: bool
    concept_candidate_created: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    action_selection_influence_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    normalization_status: str
    normalization_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != NORMALIZATION_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_feedback_candidate_normalization_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.source_candidate_kind not in ALLOWED_HOST_BODY_CANDIDATE_KINDS + ("unknown",):
            raise ValueError(f"unknown source_candidate_kind: {self.source_candidate_kind}")
        if self.normalized_learning_feedback_kind not in {
            "host_body_feedback_evidence",
            "host_body_uncertainty_evidence",
            "host_body_interesting_event_evidence",
            "host_body_teacher_review_request_evidence",
            "host_body_runtime_bridge_evidence",
            "host_body_active_perception_evidence",
            "host_body_auditory_grounding_evidence",
            "blocked",
        }:
            raise ValueError(f"unknown normalized_learning_feedback_kind: {self.normalized_learning_feedback_kind}")
        if self.normalization_status not in {
            "host_body_feedback_candidate_normalized_for_existing_review",
            "blocked_unknown_host_body_feedback_candidate_kind",
            "blocked_semantic_vision_detected",
            "blocked_speech_recognition_detected",
            "blocked_new_teacher_review_system_detected",
            "blocked_concept_candidate_created",
            "blocked_reviewed_concept_created",
            "blocked_memory_write_detected",
            "blocked_action_selection_influence_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown normalization_status: {self.normalization_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyFeedbackCandidateNormalizationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyFeedbackExistingReviewAdapterRecord:
    existing_review_adapter_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_normalization_id: str
    adapter_kind: str
    adapter_status: str
    adapter_summary: str
    existing_review_pipeline_target: str
    existing_review_input_payload: dict[str, Any]
    uses_existing_package_90_review_path: bool
    creates_parallel_review_path: bool
    teacher_review_required: bool
    teacher_approval_created: bool
    concept_candidate_created: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    action_selection_influence_created: bool
    external_control_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ADAPTER_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_feedback_existing_review_adapter_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.adapter_kind not in {
            "existing_learning_feedback_candidate_review_adapter",
            "existing_learning_feedback_candidate_review_payload",
            "blocked_adapter",
        }:
            raise ValueError(f"unknown adapter_kind: {self.adapter_kind}")
        if self.adapter_status not in {
            "existing_review_adapter_created",
            "existing_review_adapter_created_for_uncertainty",
            "existing_review_adapter_created_for_interesting_event",
            "existing_review_adapter_created_for_teacher_review_request",
            "existing_review_adapter_created_for_runtime_bridge",
            "blocked_invalid_normalization",
            "blocked_parallel_review_path_detected",
            "blocked_teacher_approval_created",
            "blocked_concept_candidate_created",
            "blocked_reviewed_concept_created",
            "blocked_memory_write_detected",
            "blocked_action_selection_influence_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown adapter_status: {self.adapter_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyFeedbackExistingReviewAdapterRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyFeedbackExistingReviewReplayRecord:
    existing_review_replay_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_existing_review_adapter_id: str
    replay_kind: str
    replay_status: str
    replay_summary: str
    simulated_existing_review_result: str
    review_result_reason_codes: tuple[str, ...]
    approved_for_existing_concept_candidate_draft: bool
    rejected_by_existing_review: bool
    deferred_by_existing_review: bool
    needs_more_evidence_by_existing_review: bool
    conflict_detected_by_existing_review: bool
    uses_existing_review_result_types: bool
    creates_new_review_result_types: bool
    teacher_approval_created: bool
    concept_candidate_created: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REPLAY_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_feedback_existing_review_replay_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.simulated_existing_review_result not in ALLOWED_REVIEW_RESULTS:
            raise ValueError(f"unknown simulated_existing_review_result: {self.simulated_existing_review_result}")
        if self.replay_kind not in {
            "existing_review_compatibility_replay",
            "existing_review_approved_replay",
            "existing_review_rejected_replay",
            "existing_review_deferred_replay",
            "existing_review_needs_more_evidence_replay",
            "existing_review_conflict_replay",
            "blocked_replay",
        }:
            raise ValueError(f"unknown replay_kind: {self.replay_kind}")
        if self.replay_status not in {
            "existing_review_replay_recorded",
            "existing_review_replay_recorded_approved",
            "existing_review_replay_recorded_rejected",
            "existing_review_replay_recorded_deferred",
            "existing_review_replay_recorded_needs_more_evidence",
            "existing_review_replay_recorded_conflict_detected",
            "blocked_invalid_adapter",
            "blocked_new_review_result_type_detected",
            "blocked_teacher_approval_created",
            "blocked_concept_candidate_created",
            "blocked_reviewed_concept_created",
            "blocked_memory_write_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown replay_status: {self.replay_status}")
        for name in ("review_result_reason_codes", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyFeedbackExistingReviewReplayRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyFeedbackConceptCandidateCompatibilityRecord:
    concept_candidate_compatibility_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_existing_review_replay_id: str
    compatibility_kind: str
    compatibility_status: str
    compatibility_summary: str
    existing_concept_candidate_draft_path_available: bool
    safe_for_existing_concept_candidate_draft: bool
    host_body_scope_preserved: bool
    counterexample_scope_required: bool
    teacher_review_result_required: bool
    concept_candidate_created_by_this_package: bool
    reviewed_concept_created_by_this_package: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    action_selection_influence_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONCEPT_COMPAT_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_feedback_concept_candidate_compatibility_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.compatibility_kind not in {
            "approved_host_body_feedback_to_existing_concept_candidate_path",
            "rejected_host_body_feedback_no_concept_path",
            "deferred_host_body_feedback_no_concept_path",
            "needs_more_evidence_host_body_feedback_no_concept_path",
            "conflict_host_body_feedback_no_concept_path",
            "blocked_compatibility",
        }:
            raise ValueError(f"unknown compatibility_kind: {self.compatibility_kind}")
        if self.compatibility_status not in {
            "host_body_feedback_compatible_with_existing_concept_candidate_path",
            "host_body_feedback_review_result_not_approved_no_concept_path",
            "blocked_invalid_review_replay",
            "blocked_concept_candidate_created_by_this_package",
            "blocked_reviewed_concept_created_by_this_package",
            "blocked_memory_write_detected",
            "blocked_action_selection_influence_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown compatibility_status: {self.compatibility_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyFeedbackConceptCandidateCompatibilityRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyFeedbackExistingLearningPipelineTraceRecord:
    existing_learning_pipeline_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_compatibility_plan_id: str
    normalization_ids: tuple[str, ...]
    adapter_ids: tuple[str, ...]
    replay_ids: tuple[str, ...]
    concept_candidate_compatibility_ids: tuple[str, ...]
    trace_kind: str
    trace_status: str
    trace_summary: str
    normalized_candidate_count: int
    existing_review_adapter_count: int
    existing_review_replay_count: int
    concept_candidate_compatibility_count: int
    approved_replay_count: int
    rejected_replay_count: int
    deferred_replay_count: int
    needs_more_evidence_replay_count: int
    conflict_detected_replay_count: int
    uses_existing_learning_pipeline_only: bool
    parallel_learning_pipeline_created: bool
    concept_candidate_created_by_this_package: bool
    reviewed_concept_created_by_this_package: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    action_selection_influence_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TRACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_existing_learning_pipeline_trace_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.trace_kind not in {
            "single_host_body_feedback_existing_pipeline_trace",
            "mixed_host_body_feedback_existing_pipeline_trace",
            "blocked_existing_pipeline_trace",
            "empty_existing_pipeline_trace",
        }:
            raise ValueError(f"unknown trace_kind: {self.trace_kind}")
        if self.trace_status not in {
            "host_body_feedback_existing_learning_pipeline_trace_recorded",
            "host_body_feedback_existing_learning_pipeline_trace_recorded_empty",
            "blocked_invalid_normalization",
            "blocked_invalid_adapter",
            "blocked_invalid_replay",
            "blocked_invalid_concept_candidate_compatibility",
            "blocked_parallel_learning_pipeline_detected",
            "blocked_concept_candidate_created_by_this_package",
            "blocked_reviewed_concept_created_by_this_package",
            "blocked_memory_write_detected",
            "blocked_action_selection_influence_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown trace_status: {self.trace_status}")
        for name in (
            "normalization_ids",
            "adapter_ids",
            "replay_ids",
            "concept_candidate_compatibility_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyFeedbackExistingLearningPipelineTraceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyExistingLearningPipelineCompatibilityAudit:
    existing_learning_pipeline_compatibility_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_compatibility_plan_id: str | None
    source_existing_learning_pipeline_trace_id: str | None
    compatibility_plan_valid: bool
    normalizations_valid: bool
    adapters_valid: bool
    review_replays_valid: bool
    concept_candidate_compatibility_valid: bool
    pipeline_trace_valid: bool
    host_body_learning_bridge_confirmed: bool
    existing_learning_pipeline_reuse_confirmed: bool
    no_parallel_teacher_review_confirmed: bool
    no_parallel_concept_system_confirmed: bool
    no_concept_candidate_created_by_this_package: bool
    no_reviewed_concept_created_by_this_package: bool
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
            raise ValueError("schema_version must be qingyin_host_body_existing_learning_pipeline_compatibility_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.audit_status not in {
            "passed_host_body_feedback_existing_learning_pipeline_compatibility",
            "passed_existing_review_adapter_compatibility",
            "passed_existing_concept_candidate_path_compatibility",
            "passed_existing_learning_pipeline_replay",
            "blocked_missing_compatibility_plan",
            "blocked_invalid_normalization",
            "blocked_invalid_adapter",
            "blocked_invalid_review_replay",
            "blocked_invalid_concept_candidate_compatibility",
            "blocked_invalid_pipeline_trace",
            "blocked_parallel_teacher_review_detected",
            "blocked_parallel_concept_system_detected",
            "blocked_concept_candidate_created_by_this_package",
            "blocked_reviewed_concept_created_by_this_package",
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
    def from_dict(cls, data: dict[str, object]) -> "HostBodyExistingLearningPipelineCompatibilityAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyExistingLearningPipelineReadinessRecord:
    existing_learning_pipeline_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_existing_learning_pipeline_compatibility_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_host_body_feedback_through_reviewed_concept_replay: bool
    ready_for_host_body_reviewed_concept_working_readback: bool
    ready_for_host_body_readback_internal_action_influence: bool
    ready_for_host_body_closed_loop_milestone_audit: bool
    ready_for_parallel_teacher_review: bool
    ready_for_concept_candidate_creation_by_adapter: bool
    ready_for_reviewed_concept_without_existing_pipeline: bool
    ready_for_memory_layer_write: bool
    ready_for_action_selection_influence: bool
    ready_for_external_control: bool
    ready_for_first_output: bool
    ready_for_live_runtime_session: bool
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READINESS_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_existing_learning_pipeline_readiness_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.readiness_status not in {
            "ready_for_host_body_feedback_through_reviewed_concept_replay_only",
            "ready_for_host_body_reviewed_concept_working_readback_only",
            "ready_for_host_body_readback_internal_action_influence_only",
            "ready_for_host_body_closed_loop_milestone_audit_only",
            "not_ready_missing_existing_learning_pipeline_compatibility_audit",
            "not_ready_boundary_failure",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyExistingLearningPipelineReadinessRecord":
        return cls(**dict(data))


def build_host_body_existing_learning_pipeline_compatibility_plan(
    *,
    host_body_learning_bridge_audit: dict[str, object] | Any | None,
    host_body_learning_candidate_set: dict[str, object] | Any | None,
    existing_pipeline_packages: tuple[str, ...] | list[str] = EXISTING_PIPELINE_PACKAGES,
    existing_pipeline_stages: tuple[str, ...] | list[str] = EXISTING_PIPELINE_STAGES,
    reuse_existing_teacher_review_required: bool = True,
    new_teacher_review_system_allowed: bool = False,
    new_concept_system_allowed: bool = False,
    direct_reviewed_concept_allowed: bool = False,
    memory_write_allowed: bool = False,
    automatic_learning_approval_allowed: bool = False,
    action_selection_influence_allowed: bool = False,
    first_output_allowed: bool = False,
    live_runtime_session_allowed: bool = False,
) -> HostBodyExistingLearningPipelineCompatibilityPlanRecord:
    audit = _record(host_body_learning_bridge_audit)
    candidate_set = _record(host_body_learning_candidate_set)
    stages = _tuple_of_str("existing_pipeline_stages", existing_pipeline_stages)
    packages = _tuple_of_str("existing_pipeline_packages", existing_pipeline_packages)
    status = _plan_status(
        audit=audit,
        candidate_set=candidate_set,
        packages=packages,
        stages=stages,
        reuse_existing_teacher_review_required=reuse_existing_teacher_review_required,
        new_teacher_review_system_allowed=new_teacher_review_system_allowed,
        new_concept_system_allowed=new_concept_system_allowed,
        direct_reviewed_concept_allowed=direct_reviewed_concept_allowed,
        memory_write_allowed=memory_write_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        action_selection_influence_allowed=action_selection_influence_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
    )
    return HostBodyExistingLearningPipelineCompatibilityPlanRecord(
        compatibility_plan_id=f"host_body_existing_learning_pipeline_compatibility_plan:{_slug(status)}",
        schema_version=PLAN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_learning_bridge_audit_id=_value(audit, "host_body_learning_bridge_audit_id"),
        source_host_body_learning_candidate_set_id=_value(
            candidate_set, "host_body_learning_feedback_candidate_set_id"
        ),
        compatibility_name=COMPATIBILITY_NAME,
        compatibility_kind=COMPATIBILITY_KIND,
        existing_pipeline_packages=packages,
        existing_pipeline_stages=stages,
        allowed_host_body_candidate_kinds=ALLOWED_HOST_BODY_CANDIDATE_KINDS,
        forbidden_parallel_pipeline_outputs=FORBIDDEN_PARALLEL_PIPELINE_OUTPUTS,
        reuse_existing_teacher_review_required=reuse_existing_teacher_review_required,
        new_teacher_review_system_allowed=new_teacher_review_system_allowed,
        new_concept_system_allowed=new_concept_system_allowed,
        direct_reviewed_concept_allowed=direct_reviewed_concept_allowed,
        memory_write_allowed=memory_write_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        action_selection_influence_allowed=action_selection_influence_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
        plan_status=status,
        plan_summary=_plan_summary(status),
        source_trace_refs=_refs_from(audit, candidate_set),
    )


def validate_host_body_existing_learning_pipeline_compatibility_plan(
    record: HostBodyExistingLearningPipelineCompatibilityPlanRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _plan(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.plan_status == "compatibility_plan_created"
    valid = valid and item.reuse_existing_teacher_review_required
    valid = valid and set(EXISTING_PIPELINE_PACKAGES).issubset(set(item.existing_pipeline_packages))
    valid = valid and set(EXISTING_PIPELINE_STAGES).issubset(set(item.existing_pipeline_stages))
    valid = valid and not any(
        (
            item.new_teacher_review_system_allowed,
            item.new_concept_system_allowed,
            item.direct_reviewed_concept_allowed,
            item.memory_write_allowed,
            item.automatic_learning_approval_allowed,
            item.action_selection_influence_allowed,
            item.first_output_allowed,
            item.live_runtime_session_allowed,
        )
    )
    return {"valid": valid, "status": item.plan_status, "reasons": [] if valid else [item.plan_status]}


def build_host_body_feedback_candidate_normalization(
    *,
    compatibility_plan: HostBodyExistingLearningPipelineCompatibilityPlanRecord | dict[str, object],
    evidence_packet: dict[str, object] | Any | None = None,
    mapping: dict[str, object] | Any | None = None,
    bridge: dict[str, object] | Any | None = None,
    source_candidate_kind: str | None = None,
    semantic_vision_created: bool = False,
    speech_recognition_created: bool = False,
    new_teacher_review_system_created: bool = False,
    new_concept_system_created: bool = False,
    concept_candidate_created: bool = False,
    reviewed_concept_created: bool = False,
    memory_write_performed: bool = False,
    action_selection_influence_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyFeedbackCandidateNormalizationRecord:
    plan = _plan(compatibility_plan)
    evidence = _record(evidence_packet)
    mapping_item = _record(mapping)
    bridge_item = _record(bridge)
    kind = source_candidate_kind or str(_value(mapping_item, "feedback_candidate_kind") or "unknown")
    normalized_kind = _normalized_learning_feedback_kind(kind)
    status = _normalization_status(
        kind=kind,
        semantic_vision_created=semantic_vision_created,
        speech_recognition_created=speech_recognition_created,
        new_teacher_review_system_created=new_teacher_review_system_created,
        new_concept_system_created=new_concept_system_created,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    payload = {
        "source_engine": SOURCE_ENGINE,
        "source_candidate_kind": kind,
        "evidence_theme": _value(evidence, "evidence_theme"),
        "evidence_kind": _value(evidence, "evidence_kind"),
        "feedback_candidate_scope": _value(mapping_item, "feedback_candidate_scope"),
        "teacher_review_required": bool(_value(evidence, "teacher_review_required") or _value(bridge_item, "teacher_review_required")),
        "existing_pipeline_target": "existing_learning_feedback_candidate_review",
        "host_body_source_refs": list(_refs_from(evidence, mapping_item, bridge_item)),
    }
    return HostBodyFeedbackCandidateNormalizationRecord(
        normalization_id=f"host_body_feedback_candidate_normalization:{_slug(kind)}:{_slug(status)}",
        schema_version=NORMALIZATION_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_compatibility_plan_id=plan.compatibility_plan_id,
        source_host_body_feedback_candidate_id=_value(mapping_item, "target_learning_feedback_candidate_id"),
        source_evidence_packet_id=_value(evidence, "host_body_learning_evidence_packet_id"),
        source_mapping_id=_value(mapping_item, "host_body_learning_feedback_mapping_id"),
        source_bridge_id=_value(bridge_item, "host_body_learning_feedback_bridge_id"),
        source_candidate_kind=kind,
        normalized_learning_feedback_kind=normalized_kind if not status.startswith("blocked") else "blocked",
        normalized_evidence_scope=_normalized_evidence_scope(kind),
        normalized_evidence_summary=_normalization_summary(status, kind),
        normalized_payload=payload,
        host_body_source_preserved=True,
        teacher_review_required_preserved=True,
        safe_for_existing_learning_review=not status.startswith("blocked"),
        semantic_vision_created=semantic_vision_created,
        speech_recognition_created=speech_recognition_created,
        new_teacher_review_system_created=new_teacher_review_system_created,
        new_concept_system_created=new_concept_system_created,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        normalization_status=status,
        normalization_summary=_normalization_summary(status, kind),
        source_trace_refs=_refs_from(evidence, mapping_item, bridge_item, {"source_trace_refs": plan.source_trace_refs}),
    )


def validate_host_body_feedback_candidate_normalization(
    record: HostBodyFeedbackCandidateNormalizationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _normalization(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.normalization_status == "host_body_feedback_candidate_normalized_for_existing_review"
    valid = valid and item.host_body_source_preserved and item.teacher_review_required_preserved
    valid = valid and item.safe_for_existing_learning_review
    valid = valid and not _normalization_has_forbidden(item)
    return {"valid": valid, "status": item.normalization_status, "reasons": [] if valid else [item.normalization_status]}


def build_host_body_feedback_existing_review_adapter(
    *,
    normalization: HostBodyFeedbackCandidateNormalizationRecord | dict[str, object],
    existing_review_pipeline_target: str = "existing_learning_feedback_candidate_review",
    uses_existing_package_90_review_path: bool = True,
    creates_parallel_review_path: bool = False,
    teacher_approval_created: bool = False,
    concept_candidate_created: bool = False,
    reviewed_concept_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    action_selection_influence_created: bool = False,
    external_control_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyFeedbackExistingReviewAdapterRecord:
    item = _normalization(normalization)
    status = _adapter_status(
        item,
        uses_existing_package_90_review_path=uses_existing_package_90_review_path,
        creates_parallel_review_path=creates_parallel_review_path,
        teacher_approval_created=teacher_approval_created,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        action_selection_influence_created=action_selection_influence_created,
        external_control_created=external_control_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    return HostBodyFeedbackExistingReviewAdapterRecord(
        existing_review_adapter_id=f"host_body_feedback_existing_review_adapter:{_slug(item.normalized_learning_feedback_kind)}:{_slug(status)}",
        schema_version=ADAPTER_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_normalization_id=item.normalization_id,
        adapter_kind="blocked_adapter" if status.startswith("blocked") else "existing_learning_feedback_candidate_review_adapter",
        adapter_status=status,
        adapter_summary=_adapter_summary(status),
        existing_review_pipeline_target=existing_review_pipeline_target,
        existing_review_input_payload={
            "adapter_authority": "existing_package_90_review_path",
            "normalized_learning_feedback_kind": item.normalized_learning_feedback_kind,
            "normalized_evidence_scope": item.normalized_evidence_scope,
            "normalized_evidence_summary": item.normalized_evidence_summary,
            "normalized_payload": _plain(item.normalized_payload),
        },
        uses_existing_package_90_review_path=uses_existing_package_90_review_path,
        creates_parallel_review_path=creates_parallel_review_path,
        teacher_review_required=True,
        teacher_approval_created=teacher_approval_created,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed or automatic_learning_approval_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        action_selection_influence_created=action_selection_influence_created,
        external_control_created=external_control_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=item.source_trace_refs,
    )


def validate_host_body_feedback_existing_review_adapter(
    record: HostBodyFeedbackExistingReviewAdapterRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _adapter(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.adapter_status.startswith("existing_review_adapter_created")
    valid = valid and item.uses_existing_package_90_review_path and not item.creates_parallel_review_path
    valid = valid and item.teacher_review_required and not _adapter_has_forbidden(item)
    return {"valid": valid, "status": item.adapter_status, "reasons": [] if valid else [item.adapter_status]}


def build_host_body_feedback_existing_review_replay(
    *,
    existing_review_adapter: HostBodyFeedbackExistingReviewAdapterRecord | dict[str, object],
    simulated_existing_review_result: str = "approved",
    creates_new_review_result_types: bool = False,
    teacher_approval_created: bool = False,
    concept_candidate_created: bool = False,
    reviewed_concept_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyFeedbackExistingReviewReplayRecord:
    adapter = _adapter(existing_review_adapter)
    result = simulated_existing_review_result
    if result not in ALLOWED_REVIEW_RESULTS:
        result = "blocked"
        creates_new_review_result_types = True
    status = _replay_status(
        adapter,
        result=result,
        creates_new_review_result_types=creates_new_review_result_types,
        teacher_approval_created=teacher_approval_created,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    replay_kind = _replay_kind(status, result)
    approved = status == "existing_review_replay_recorded_approved"
    return HostBodyFeedbackExistingReviewReplayRecord(
        existing_review_replay_id=f"host_body_feedback_existing_review_replay:{_slug(result)}:{_slug(status)}",
        schema_version=REPLAY_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_existing_review_adapter_id=adapter.existing_review_adapter_id,
        replay_kind=replay_kind,
        replay_status=status,
        replay_summary=_replay_summary(status, result),
        simulated_existing_review_result=result,
        review_result_reason_codes=_review_result_reason_codes(result, status),
        approved_for_existing_concept_candidate_draft=approved,
        rejected_by_existing_review=status == "existing_review_replay_recorded_rejected",
        deferred_by_existing_review=status == "existing_review_replay_recorded_deferred",
        needs_more_evidence_by_existing_review=status == "existing_review_replay_recorded_needs_more_evidence",
        conflict_detected_by_existing_review=status == "existing_review_replay_recorded_conflict_detected",
        uses_existing_review_result_types=not creates_new_review_result_types,
        creates_new_review_result_types=creates_new_review_result_types,
        teacher_approval_created=teacher_approval_created,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed or automatic_learning_approval_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=adapter.source_trace_refs,
    )


def validate_host_body_feedback_existing_review_replay(
    record: HostBodyFeedbackExistingReviewReplayRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _replay(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.replay_status.startswith("existing_review_replay_recorded")
    valid = valid and item.uses_existing_review_result_types and not item.creates_new_review_result_types
    valid = valid and not _replay_has_forbidden(item)
    return {"valid": valid, "status": item.replay_status, "reasons": [] if valid else [item.replay_status]}


def build_host_body_feedback_concept_candidate_compatibility(
    *,
    existing_review_replay: HostBodyFeedbackExistingReviewReplayRecord | dict[str, object],
    concept_candidate_created_by_this_package: bool = False,
    reviewed_concept_created_by_this_package: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    action_selection_influence_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyFeedbackConceptCandidateCompatibilityRecord:
    replay = _replay(existing_review_replay)
    status = _concept_compat_status(
        replay,
        concept_candidate_created_by_this_package=concept_candidate_created_by_this_package,
        reviewed_concept_created_by_this_package=reviewed_concept_created_by_this_package,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    kind = _concept_compat_kind(replay, status)
    return HostBodyFeedbackConceptCandidateCompatibilityRecord(
        concept_candidate_compatibility_id=f"host_body_feedback_concept_candidate_compatibility:{_slug(kind)}:{_slug(status)}",
        schema_version=CONCEPT_COMPAT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_existing_review_replay_id=replay.existing_review_replay_id,
        compatibility_kind=kind,
        compatibility_status=status,
        compatibility_summary=_concept_compat_summary(status),
        existing_concept_candidate_draft_path_available=True,
        safe_for_existing_concept_candidate_draft=(
            status == "host_body_feedback_compatible_with_existing_concept_candidate_path"
        ),
        host_body_scope_preserved=True,
        counterexample_scope_required=True,
        teacher_review_result_required=True,
        concept_candidate_created_by_this_package=concept_candidate_created_by_this_package,
        reviewed_concept_created_by_this_package=reviewed_concept_created_by_this_package,
        memory_write_performed=memory_write_performed or automatic_learning_approval_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=replay.source_trace_refs,
    )


def validate_host_body_feedback_concept_candidate_compatibility(
    record: HostBodyFeedbackConceptCandidateCompatibilityRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _concept_compat(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.compatibility_status in {
        "host_body_feedback_compatible_with_existing_concept_candidate_path",
        "host_body_feedback_review_result_not_approved_no_concept_path",
    }
    valid = valid and item.host_body_scope_preserved and item.counterexample_scope_required
    valid = valid and item.teacher_review_result_required and not _concept_compat_has_forbidden(item)
    return {"valid": valid, "status": item.compatibility_status, "reasons": [] if valid else [item.compatibility_status]}


def build_host_body_feedback_existing_learning_pipeline_trace(
    *,
    compatibility_plan: HostBodyExistingLearningPipelineCompatibilityPlanRecord | dict[str, object],
    normalizations: tuple[HostBodyFeedbackCandidateNormalizationRecord | dict[str, object], ...] | list[HostBodyFeedbackCandidateNormalizationRecord | dict[str, object]] = tuple(),
    adapters: tuple[HostBodyFeedbackExistingReviewAdapterRecord | dict[str, object], ...] | list[HostBodyFeedbackExistingReviewAdapterRecord | dict[str, object]] = tuple(),
    review_replays: tuple[HostBodyFeedbackExistingReviewReplayRecord | dict[str, object], ...] | list[HostBodyFeedbackExistingReviewReplayRecord | dict[str, object]] = tuple(),
    concept_candidate_compatibilities: tuple[HostBodyFeedbackConceptCandidateCompatibilityRecord | dict[str, object], ...] | list[HostBodyFeedbackConceptCandidateCompatibilityRecord | dict[str, object]] = tuple(),
    parallel_learning_pipeline_created: bool = False,
    concept_candidate_created_by_this_package: bool = False,
    reviewed_concept_created_by_this_package: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    action_selection_influence_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyFeedbackExistingLearningPipelineTraceRecord:
    plan = _plan(compatibility_plan)
    normalization_items = tuple(_normalization(item) for item in normalizations)
    adapter_items = tuple(_adapter(item) for item in adapters)
    replay_items = tuple(_replay(item) for item in review_replays)
    compat_items = tuple(_concept_compat(item) for item in concept_candidate_compatibilities)
    concept_created = concept_candidate_created_by_this_package or any(
        item.concept_candidate_created for item in adapter_items + replay_items
    ) or any(item.concept_candidate_created_by_this_package for item in compat_items)
    reviewed_created = reviewed_concept_created_by_this_package or any(
        item.reviewed_concept_created for item in adapter_items + replay_items
    ) or any(item.reviewed_concept_created_by_this_package for item in compat_items)
    memory_written = (
        memory_write_performed
        or automatic_learning_approval_created
        or any(item.memory_write_performed for item in normalization_items)
        or any(item.memory_write_performed for item in adapter_items + replay_items)
        or any(item.memory_write_performed for item in compat_items)
    )
    action_influence = action_selection_influence_created or any(
        item.action_selection_influence_created for item in normalization_items + adapter_items
    ) or any(item.action_selection_influence_created for item in compat_items)
    status = _trace_status(
        normalizations=normalization_items,
        adapters=adapter_items,
        review_replays=replay_items,
        concept_candidate_compatibilities=compat_items,
        parallel_learning_pipeline_created=parallel_learning_pipeline_created,
        concept_candidate_created_by_this_package=concept_created,
        reviewed_concept_created_by_this_package=reviewed_created,
        memory_write_performed=memory_written,
        action_selection_influence_created=action_influence,
        first_output_created=first_output_created or any(item.first_output_created for item in replay_items + compat_items),
        live_runtime_session_created=live_runtime_session_created or any(item.live_runtime_session_created for item in replay_items + compat_items),
    )
    refs = tuple(
        dict.fromkeys(
            ref
            for group in (normalization_items, adapter_items, replay_items, compat_items)
            for item in group
            for ref in item.source_trace_refs
        )
    )
    return HostBodyFeedbackExistingLearningPipelineTraceRecord(
        existing_learning_pipeline_trace_id=f"host_body_existing_learning_pipeline_trace:{_slug(status)}:{len(normalization_items)}",
        schema_version=TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_compatibility_plan_id=plan.compatibility_plan_id,
        normalization_ids=tuple(item.normalization_id for item in normalization_items),
        adapter_ids=tuple(item.existing_review_adapter_id for item in adapter_items),
        replay_ids=tuple(item.existing_review_replay_id for item in replay_items),
        concept_candidate_compatibility_ids=tuple(item.concept_candidate_compatibility_id for item in compat_items),
        trace_kind=_trace_kind(len(normalization_items), status),
        trace_status=status,
        trace_summary=_trace_summary(status, len(normalization_items)),
        normalized_candidate_count=len(normalization_items),
        existing_review_adapter_count=len(adapter_items),
        existing_review_replay_count=len(replay_items),
        concept_candidate_compatibility_count=len(compat_items),
        approved_replay_count=sum(1 for item in replay_items if item.approved_for_existing_concept_candidate_draft),
        rejected_replay_count=sum(1 for item in replay_items if item.rejected_by_existing_review),
        deferred_replay_count=sum(1 for item in replay_items if item.deferred_by_existing_review),
        needs_more_evidence_replay_count=sum(1 for item in replay_items if item.needs_more_evidence_by_existing_review),
        conflict_detected_replay_count=sum(1 for item in replay_items if item.conflict_detected_by_existing_review),
        uses_existing_learning_pipeline_only=not parallel_learning_pipeline_created,
        parallel_learning_pipeline_created=parallel_learning_pipeline_created,
        concept_candidate_created_by_this_package=concept_created,
        reviewed_concept_created_by_this_package=reviewed_created,
        memory_write_performed=memory_written,
        automatic_learning_approval_created=automatic_learning_approval_created
        or any(item.automatic_learning_approval_created for item in adapter_items + replay_items + compat_items),
        action_selection_influence_created=action_influence,
        first_output_created=first_output_created or any(item.first_output_created for item in replay_items + compat_items),
        live_runtime_session_created=live_runtime_session_created or any(item.live_runtime_session_created for item in replay_items + compat_items),
        source_trace_refs=refs,
    )


def validate_host_body_feedback_existing_learning_pipeline_trace(
    record: HostBodyFeedbackExistingLearningPipelineTraceRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _trace(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.trace_status.startswith("host_body_feedback_existing_learning_pipeline_trace_recorded")
    valid = valid and item.uses_existing_learning_pipeline_only and not item.parallel_learning_pipeline_created
    valid = valid and not _trace_has_forbidden(item)
    return {"valid": valid, "status": item.trace_status, "reasons": [] if valid else [item.trace_status]}


def build_host_body_existing_learning_pipeline_compatibility_audit(
    *,
    compatibility_plan: HostBodyExistingLearningPipelineCompatibilityPlanRecord | dict[str, object] | None,
    existing_learning_pipeline_trace: HostBodyFeedbackExistingLearningPipelineTraceRecord | dict[str, object] | None,
    normalizations: tuple[HostBodyFeedbackCandidateNormalizationRecord | dict[str, object], ...] | list[HostBodyFeedbackCandidateNormalizationRecord | dict[str, object]] = tuple(),
    adapters: tuple[HostBodyFeedbackExistingReviewAdapterRecord | dict[str, object], ...] | list[HostBodyFeedbackExistingReviewAdapterRecord | dict[str, object]] = tuple(),
    review_replays: tuple[HostBodyFeedbackExistingReviewReplayRecord | dict[str, object], ...] | list[HostBodyFeedbackExistingReviewReplayRecord | dict[str, object]] = tuple(),
    concept_candidate_compatibilities: tuple[HostBodyFeedbackConceptCandidateCompatibilityRecord | dict[str, object], ...] | list[HostBodyFeedbackConceptCandidateCompatibilityRecord | dict[str, object]] = tuple(),
    preferred_pass_status: str | None = None,
    force_external_control: bool = False,
    force_thought_engine_behavior: bool = False,
    force_production_behavior: bool = False,
) -> HostBodyExistingLearningPipelineCompatibilityAudit:
    plan = _plan(compatibility_plan) if compatibility_plan is not None else None
    trace = _trace(existing_learning_pipeline_trace) if existing_learning_pipeline_trace is not None else None
    normalization_items = tuple(_normalization(item) for item in normalizations)
    adapter_items = tuple(_adapter(item) for item in adapters)
    replay_items = tuple(_replay(item) for item in review_replays)
    compat_items = tuple(_concept_compat(item) for item in concept_candidate_compatibilities)
    reasons = _audit_reasons(
        plan=plan,
        trace=trace,
        normalizations=normalization_items,
        adapters=adapter_items,
        review_replays=replay_items,
        concept_candidate_compatibilities=compat_items,
        force_external_control=force_external_control,
        force_thought_engine_behavior=force_thought_engine_behavior,
        force_production_behavior=force_production_behavior,
    )
    status = _audit_status(reasons, preferred_pass_status)
    return HostBodyExistingLearningPipelineCompatibilityAudit(
        existing_learning_pipeline_compatibility_audit_id=f"host_body_existing_learning_pipeline_compatibility_audit:{_slug(status)}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_compatibility_plan_id=plan.compatibility_plan_id if plan else None,
        source_existing_learning_pipeline_trace_id=trace.existing_learning_pipeline_trace_id if trace else None,
        compatibility_plan_valid=plan is not None and validate_host_body_existing_learning_pipeline_compatibility_plan(plan)["valid"],
        normalizations_valid=all(validate_host_body_feedback_candidate_normalization(item)["valid"] for item in normalization_items),
        adapters_valid=all(validate_host_body_feedback_existing_review_adapter(item)["valid"] for item in adapter_items),
        review_replays_valid=all(validate_host_body_feedback_existing_review_replay(item)["valid"] for item in replay_items),
        concept_candidate_compatibility_valid=all(
            validate_host_body_feedback_concept_candidate_compatibility(item)["valid"] for item in compat_items
        ),
        pipeline_trace_valid=trace is not None and validate_host_body_feedback_existing_learning_pipeline_trace(trace)["valid"],
        host_body_learning_bridge_confirmed=plan is not None,
        existing_learning_pipeline_reuse_confirmed="parallel_teacher_review" not in reasons
        and "parallel_concept_system" not in reasons,
        no_parallel_teacher_review_confirmed="parallel_teacher_review" not in reasons,
        no_parallel_concept_system_confirmed="parallel_concept_system" not in reasons,
        no_concept_candidate_created_by_this_package="concept_candidate_by_package" not in reasons,
        no_reviewed_concept_created_by_this_package="reviewed_concept_by_package" not in reasons,
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


def validate_host_body_existing_learning_pipeline_compatibility_audit(
    record: HostBodyExistingLearningPipelineCompatibilityAudit | dict[str, object],
) -> dict[str, object]:
    try:
        item = _audit(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.audit_status.startswith("passed_")
    return {"valid": valid, "status": item.audit_status, "reasons": [] if valid else list(item.blocked_reasons)}


def build_host_body_existing_learning_pipeline_readiness(
    existing_learning_pipeline_compatibility_audit: HostBodyExistingLearningPipelineCompatibilityAudit | dict[str, object] | None,
) -> HostBodyExistingLearningPipelineReadinessRecord:
    audit = _audit(existing_learning_pipeline_compatibility_audit) if existing_learning_pipeline_compatibility_audit is not None else None
    passed = audit is not None and audit.audit_status.startswith("passed_")
    if audit is None:
        status = "not_ready_missing_existing_learning_pipeline_compatibility_audit"
    elif passed:
        status = "ready_for_host_body_feedback_through_reviewed_concept_replay_only"
    elif audit.audit_status.startswith("blocked_"):
        status = "blocked_forbidden_authority_detected"
    else:
        status = "not_ready_boundary_failure"
    return HostBodyExistingLearningPipelineReadinessRecord(
        existing_learning_pipeline_readiness_id=(
            f"host_body_existing_learning_pipeline_readiness:{audit.existing_learning_pipeline_compatibility_audit_id}"
            if audit
            else "host_body_existing_learning_pipeline_readiness:missing_audit"
        ),
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_existing_learning_pipeline_compatibility_audit_id=(
            audit.existing_learning_pipeline_compatibility_audit_id if audit else "missing_existing_learning_pipeline_compatibility_audit"
        ),
        current_verified_capability=SAFE_CLAIM if passed else "Host Body existing learning pipeline compatibility audit did not pass.",
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason=(
            "Replay one approved Host Body feedback candidate through the existing Package 90 to 92 path."
        ),
        ready_for_host_body_feedback_through_reviewed_concept_replay=passed,
        ready_for_host_body_reviewed_concept_working_readback=passed,
        ready_for_host_body_readback_internal_action_influence=passed,
        ready_for_host_body_closed_loop_milestone_audit=passed,
        ready_for_parallel_teacher_review=False,
        ready_for_concept_candidate_creation_by_adapter=False,
        ready_for_reviewed_concept_without_existing_pipeline=False,
        ready_for_memory_layer_write=False,
        ready_for_action_selection_influence=False,
        ready_for_external_control=False,
        ready_for_first_output=False,
        ready_for_live_runtime_session=False,
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=audit.source_trace_refs if audit else tuple(),
    )


def validate_host_body_existing_learning_pipeline_readiness(
    record: HostBodyExistingLearningPipelineReadinessRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _readiness(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.readiness_status.startswith("ready_for_")
    valid = valid and all(
        (
            item.ready_for_host_body_feedback_through_reviewed_concept_replay,
            item.ready_for_host_body_reviewed_concept_working_readback,
            item.ready_for_host_body_readback_internal_action_influence,
            item.ready_for_host_body_closed_loop_milestone_audit,
        )
    )
    valid = valid and not any(
        (
            item.ready_for_parallel_teacher_review,
            item.ready_for_concept_candidate_creation_by_adapter,
            item.ready_for_reviewed_concept_without_existing_pipeline,
            item.ready_for_memory_layer_write,
            item.ready_for_action_selection_influence,
            item.ready_for_external_control,
            item.ready_for_first_output,
            item.ready_for_live_runtime_session,
        )
    )
    return {"valid": valid, "status": item.readiness_status, "reasons": [] if valid else [item.readiness_status]}


def build_demo_uncertainty_existing_pipeline_compatibility() -> dict[str, object]:
    return _build_demo_bundle(build_demo_uncertainty_to_learning_feedback_candidate())


def build_demo_interesting_existing_pipeline_compatibility() -> dict[str, object]:
    return _build_demo_bundle(build_demo_interesting_event_to_learning_feedback_candidate())


def build_demo_teacher_review_existing_pipeline_compatibility() -> dict[str, object]:
    return _build_demo_bundle(build_demo_teacher_review_request_to_learning_feedback_candidate())


def build_demo_existing_review_approved_replay() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_uncertainty_to_learning_feedback_candidate(),
        simulated_existing_review_result="approved",
        preferred_pass_status="passed_existing_concept_candidate_path_compatibility",
    )


def build_demo_existing_review_needs_more_evidence_replay() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_uncertainty_to_learning_feedback_candidate(),
        simulated_existing_review_result="needs_more_evidence",
        preferred_pass_status="passed_existing_learning_pipeline_replay",
    )


def build_demo_mixed_existing_pipeline_compatibility() -> dict[str, object]:
    source = build_demo_host_body_learning_feedback_candidate_set()
    return _build_demo_bundle(source, use_all=True)


def build_demo_blocked_parallel_teacher_review() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_uncertainty_to_learning_feedback_candidate(),
        creates_parallel_review_path=True,
    )


def build_demo_blocked_parallel_concept_system() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_uncertainty_to_learning_feedback_candidate(),
        plan_new_concept_system_allowed=True,
    )


def build_demo_blocked_concept_candidate_created_by_adapter() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_uncertainty_to_learning_feedback_candidate(),
        adapter_concept_candidate_created=True,
    )


def build_demo_blocked_reviewed_concept_created_by_adapter() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_uncertainty_to_learning_feedback_candidate(),
        adapter_reviewed_concept_created=True,
    )


def build_demo_blocked_memory_write_existing_pipeline() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_uncertainty_to_learning_feedback_candidate(),
        adapter_memory_write_performed=True,
    )


def build_demo_blocked_first_output_existing_pipeline() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_uncertainty_to_learning_feedback_candidate(),
        adapter_first_output_created=True,
    )


def build_demo_blocked_live_runtime_existing_pipeline() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_uncertainty_to_learning_feedback_candidate(),
        adapter_live_runtime_session_created=True,
    )


def render_host_body_existing_learning_pipeline_summary_text(
    audit: HostBodyExistingLearningPipelineCompatibilityAudit | dict[str, object],
    readiness: HostBodyExistingLearningPipelineReadinessRecord | dict[str, object] | None = None,
) -> str:
    item = _audit(audit)
    readiness_item = _readiness(readiness) if readiness is not None else None
    lines = [
        "Host Body Existing Learning Pipeline Compatibility",
        f"audit_status: {item.audit_status}",
        f"existing_learning_pipeline_reuse_confirmed: {item.existing_learning_pipeline_reuse_confirmed}",
        f"no_parallel_teacher_review: {item.no_parallel_teacher_review_confirmed}",
        f"no_concept_candidate_created_by_this_package: {item.no_concept_candidate_created_by_this_package}",
        f"no_memory_layer_write: {item.no_memory_layer_write}",
        f"no_first_output: {item.no_first_output}",
        f"no_live_runtime_session: {item.no_live_runtime_session}",
    ]
    if readiness_item is not None:
        lines.append(f"readiness_status: {readiness_item.readiness_status}")
    return "\n".join(lines)


def render_host_body_existing_learning_pipeline_table(
    trace: HostBodyFeedbackExistingLearningPipelineTraceRecord | dict[str, object],
    normalizations: tuple[HostBodyFeedbackCandidateNormalizationRecord | dict[str, object], ...] | list[HostBodyFeedbackCandidateNormalizationRecord | dict[str, object]] = tuple(),
    adapters: tuple[HostBodyFeedbackExistingReviewAdapterRecord | dict[str, object], ...] | list[HostBodyFeedbackExistingReviewAdapterRecord | dict[str, object]] = tuple(),
    review_replays: tuple[HostBodyFeedbackExistingReviewReplayRecord | dict[str, object], ...] | list[HostBodyFeedbackExistingReviewReplayRecord | dict[str, object]] = tuple(),
) -> str:
    trace_item = _trace(trace)
    normalization_items = tuple(_normalization(item) for item in normalizations)
    adapter_items = tuple(_adapter(item) for item in adapters)
    replay_items = tuple(_replay(item) for item in review_replays)
    lines = ["candidate_kind | adapter_status | replay_result"]
    for normalization, adapter, replay in zip(normalization_items, adapter_items, replay_items):
        lines.append(
            f"{normalization.source_candidate_kind} | {adapter.adapter_status} | {replay.simulated_existing_review_result}"
        )
    if not normalization_items:
        lines.append(f"empty | {trace_item.trace_status} | none")
    return "\n".join(lines)


def _build_demo_bundle(
    source_payload: dict[str, object],
    *,
    simulated_existing_review_result: str = "approved",
    use_all: bool = False,
    preferred_pass_status: str | None = None,
    plan_new_concept_system_allowed: bool = False,
    creates_parallel_review_path: bool = False,
    adapter_concept_candidate_created: bool = False,
    adapter_reviewed_concept_created: bool = False,
    adapter_memory_write_performed: bool = False,
    adapter_first_output_created: bool = False,
    adapter_live_runtime_session_created: bool = False,
) -> dict[str, object]:
    learning_audit = source_payload["host_body_learning_bridge_audit"]
    candidate_set = source_payload["host_body_learning_feedback_candidate_set"]
    plan = build_host_body_existing_learning_pipeline_compatibility_plan(
        host_body_learning_bridge_audit=learning_audit,
        host_body_learning_candidate_set=candidate_set,
        new_concept_system_allowed=plan_new_concept_system_allowed,
    )
    evidence_packets = tuple(source_payload.get("host_body_learning_evidence_packets", ()))
    mappings = tuple(source_payload.get("host_body_learning_feedback_mappings", ()))
    bridges = tuple(source_payload.get("host_body_learning_feedback_bridges", ()))
    if not use_all:
        evidence_packets = evidence_packets[:1]
        mappings = mappings[:1]
        bridges = bridges[:1]
    normalizations: list[HostBodyFeedbackCandidateNormalizationRecord] = []
    adapters: list[HostBodyFeedbackExistingReviewAdapterRecord] = []
    replays: list[HostBodyFeedbackExistingReviewReplayRecord] = []
    compatibilities: list[HostBodyFeedbackConceptCandidateCompatibilityRecord] = []
    for evidence, mapping, bridge in zip(evidence_packets, mappings, bridges):
        normalization = build_host_body_feedback_candidate_normalization(
            compatibility_plan=plan,
            evidence_packet=evidence,
            mapping=mapping,
            bridge=bridge,
        )
        adapter = build_host_body_feedback_existing_review_adapter(
            normalization=normalization,
            creates_parallel_review_path=creates_parallel_review_path,
            concept_candidate_created=adapter_concept_candidate_created,
            reviewed_concept_created=adapter_reviewed_concept_created,
            memory_write_performed=adapter_memory_write_performed,
            first_output_created=adapter_first_output_created,
            live_runtime_session_created=adapter_live_runtime_session_created,
        )
        replay = build_host_body_feedback_existing_review_replay(
            existing_review_adapter=adapter,
            simulated_existing_review_result=simulated_existing_review_result,
        )
        compatibility = build_host_body_feedback_concept_candidate_compatibility(
            existing_review_replay=replay,
        )
        normalizations.append(normalization)
        adapters.append(adapter)
        replays.append(replay)
        compatibilities.append(compatibility)
    trace = build_host_body_feedback_existing_learning_pipeline_trace(
        compatibility_plan=plan,
        normalizations=tuple(normalizations),
        adapters=tuple(adapters),
        review_replays=tuple(replays),
        concept_candidate_compatibilities=tuple(compatibilities),
    )
    audit = build_host_body_existing_learning_pipeline_compatibility_audit(
        compatibility_plan=plan,
        existing_learning_pipeline_trace=trace,
        normalizations=tuple(normalizations),
        adapters=tuple(adapters),
        review_replays=tuple(replays),
        concept_candidate_compatibilities=tuple(compatibilities),
        preferred_pass_status=preferred_pass_status,
    )
    readiness = build_host_body_existing_learning_pipeline_readiness(audit)
    return _payload(plan, tuple(normalizations), tuple(adapters), tuple(replays), tuple(compatibilities), trace, audit, readiness)


def _payload(
    plan: HostBodyExistingLearningPipelineCompatibilityPlanRecord,
    normalizations: tuple[HostBodyFeedbackCandidateNormalizationRecord, ...],
    adapters: tuple[HostBodyFeedbackExistingReviewAdapterRecord, ...],
    replays: tuple[HostBodyFeedbackExistingReviewReplayRecord, ...],
    compatibilities: tuple[HostBodyFeedbackConceptCandidateCompatibilityRecord, ...],
    trace: HostBodyFeedbackExistingLearningPipelineTraceRecord,
    audit: HostBodyExistingLearningPipelineCompatibilityAudit,
    readiness: HostBodyExistingLearningPipelineReadinessRecord,
) -> dict[str, object]:
    return {
        "host_body_existing_learning_pipeline_compatibility_plan": plan.to_dict(),
        "host_body_feedback_candidate_normalizations": tuple(item.to_dict() for item in normalizations),
        "host_body_feedback_existing_review_adapters": tuple(item.to_dict() for item in adapters),
        "host_body_feedback_existing_review_replays": tuple(item.to_dict() for item in replays),
        "host_body_feedback_concept_candidate_compatibilities": tuple(item.to_dict() for item in compatibilities),
        "host_body_feedback_existing_learning_pipeline_trace": trace.to_dict(),
        "host_body_existing_learning_pipeline_compatibility_audit": audit.to_dict(),
        "host_body_existing_learning_pipeline_readiness": readiness.to_dict(),
        "rendered_host_body_existing_learning_pipeline_summary": render_host_body_existing_learning_pipeline_summary_text(
            audit, readiness
        ),
        "rendered_host_body_existing_learning_pipeline_table": render_host_body_existing_learning_pipeline_table(
            trace, normalizations, adapters, replays
        ),
    }


def _plan(record: HostBodyExistingLearningPipelineCompatibilityPlanRecord | dict[str, object]) -> HostBodyExistingLearningPipelineCompatibilityPlanRecord:
    if isinstance(record, HostBodyExistingLearningPipelineCompatibilityPlanRecord):
        return record
    return HostBodyExistingLearningPipelineCompatibilityPlanRecord.from_dict(record)


def _normalization(record: HostBodyFeedbackCandidateNormalizationRecord | dict[str, object]) -> HostBodyFeedbackCandidateNormalizationRecord:
    if isinstance(record, HostBodyFeedbackCandidateNormalizationRecord):
        return record
    return HostBodyFeedbackCandidateNormalizationRecord.from_dict(record)


def _adapter(record: HostBodyFeedbackExistingReviewAdapterRecord | dict[str, object]) -> HostBodyFeedbackExistingReviewAdapterRecord:
    if isinstance(record, HostBodyFeedbackExistingReviewAdapterRecord):
        return record
    return HostBodyFeedbackExistingReviewAdapterRecord.from_dict(record)


def _replay(record: HostBodyFeedbackExistingReviewReplayRecord | dict[str, object]) -> HostBodyFeedbackExistingReviewReplayRecord:
    if isinstance(record, HostBodyFeedbackExistingReviewReplayRecord):
        return record
    return HostBodyFeedbackExistingReviewReplayRecord.from_dict(record)


def _concept_compat(record: HostBodyFeedbackConceptCandidateCompatibilityRecord | dict[str, object]) -> HostBodyFeedbackConceptCandidateCompatibilityRecord:
    if isinstance(record, HostBodyFeedbackConceptCandidateCompatibilityRecord):
        return record
    return HostBodyFeedbackConceptCandidateCompatibilityRecord.from_dict(record)


def _trace(record: HostBodyFeedbackExistingLearningPipelineTraceRecord | dict[str, object]) -> HostBodyFeedbackExistingLearningPipelineTraceRecord:
    if isinstance(record, HostBodyFeedbackExistingLearningPipelineTraceRecord):
        return record
    return HostBodyFeedbackExistingLearningPipelineTraceRecord.from_dict(record)


def _audit(record: HostBodyExistingLearningPipelineCompatibilityAudit | dict[str, object]) -> HostBodyExistingLearningPipelineCompatibilityAudit:
    if isinstance(record, HostBodyExistingLearningPipelineCompatibilityAudit):
        return record
    return HostBodyExistingLearningPipelineCompatibilityAudit.from_dict(record)


def _readiness(record: HostBodyExistingLearningPipelineReadinessRecord | dict[str, object]) -> HostBodyExistingLearningPipelineReadinessRecord:
    if isinstance(record, HostBodyExistingLearningPipelineReadinessRecord):
        return record
    return HostBodyExistingLearningPipelineReadinessRecord.from_dict(record)


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
    return bool(record and str(record.get(key, "")).startswith("host_body_learning_feedback_candidate_set_recorded"))


def _plan_status(**kwargs: Any) -> str:
    if not _status_passed(kwargs["audit"], "audit_status"):
        return "blocked_missing_host_body_learning_bridge_audit"
    if not _status_recorded(kwargs["candidate_set"], "candidate_set_status"):
        return "blocked_missing_candidate_set"
    if not set(EXISTING_PIPELINE_PACKAGES).issubset(set(kwargs["packages"])):
        return "blocked_forbidden_authority_detected"
    if not set(EXISTING_PIPELINE_STAGES).issubset(set(kwargs["stages"])):
        return "blocked_forbidden_authority_detected"
    if not kwargs["reuse_existing_teacher_review_required"]:
        return "blocked_new_teacher_review_system_allowed"
    if kwargs["new_teacher_review_system_allowed"]:
        return "blocked_new_teacher_review_system_allowed"
    if kwargs["new_concept_system_allowed"]:
        return "blocked_new_concept_system_allowed"
    if kwargs["direct_reviewed_concept_allowed"]:
        return "blocked_direct_reviewed_concept_allowed"
    if kwargs["memory_write_allowed"] or kwargs["automatic_learning_approval_allowed"]:
        return "blocked_memory_write_allowed"
    if kwargs["action_selection_influence_allowed"]:
        return "blocked_action_selection_influence_allowed"
    if kwargs["first_output_allowed"]:
        return "blocked_first_output_allowed"
    if kwargs["live_runtime_session_allowed"]:
        return "blocked_live_runtime_allowed"
    return "compatibility_plan_created"


def _plan_summary(status: str) -> str:
    if status == "compatibility_plan_created":
        return "Host Body feedback bridge records may be adapted to the existing Package 90 to 92 pipeline."
    return "Host Body existing learning pipeline compatibility plan is blocked."


def _normalized_learning_feedback_kind(candidate_kind: str) -> str:
    return {
        "host_body_feedback_candidate": "host_body_feedback_evidence",
        "host_body_uncertainty_feedback_candidate": "host_body_uncertainty_evidence",
        "host_body_interesting_event_feedback_candidate": "host_body_interesting_event_evidence",
        "host_body_teacher_review_feedback_candidate": "host_body_teacher_review_request_evidence",
        "host_body_runtime_bridge_feedback_candidate": "host_body_runtime_bridge_evidence",
        "host_body_active_perception_feedback_candidate": "host_body_active_perception_evidence",
        "host_body_auditory_grounding_feedback_candidate": "host_body_auditory_grounding_evidence",
    }.get(candidate_kind, "blocked")


def _normalized_evidence_scope(candidate_kind: str) -> str:
    if candidate_kind == "host_body_runtime_bridge_feedback_candidate":
        return "host_body_runtime_bridge_only"
    if candidate_kind in {
        "host_body_teacher_review_feedback_candidate",
        "host_body_active_perception_feedback_candidate",
        "host_body_auditory_grounding_feedback_candidate",
    }:
        return "host_body_internal_action_only"
    if candidate_kind in ALLOWED_HOST_BODY_CANDIDATE_KINDS:
        return "host_body_trace_history_only"
    return "blocked"


def _normalization_status(**kwargs: Any) -> str:
    if kwargs["kind"] not in ALLOWED_HOST_BODY_CANDIDATE_KINDS:
        return "blocked_unknown_host_body_feedback_candidate_kind"
    if kwargs["semantic_vision_created"]:
        return "blocked_semantic_vision_detected"
    if kwargs["speech_recognition_created"]:
        return "blocked_speech_recognition_detected"
    if kwargs["new_teacher_review_system_created"] or kwargs["new_concept_system_created"]:
        return "blocked_new_teacher_review_system_detected"
    if kwargs["concept_candidate_created"]:
        return "blocked_concept_candidate_created"
    if kwargs["reviewed_concept_created"]:
        return "blocked_reviewed_concept_created"
    if kwargs["memory_write_performed"]:
        return "blocked_memory_write_detected"
    if kwargs["action_selection_influence_created"]:
        return "blocked_action_selection_influence_detected"
    if kwargs["first_output_created"]:
        return "blocked_first_output_detected"
    if kwargs["live_runtime_session_created"]:
        return "blocked_live_runtime_detected"
    return "host_body_feedback_candidate_normalized_for_existing_review"


def _normalization_summary(status: str, candidate_kind: str) -> str:
    if status == "host_body_feedback_candidate_normalized_for_existing_review":
        return f"{candidate_kind} normalized for the existing LearningFeedbackCandidate review path."
    return "Host Body feedback candidate normalization is blocked."


def _normalization_has_forbidden(item: HostBodyFeedbackCandidateNormalizationRecord) -> bool:
    return any(
        (
            item.semantic_vision_created,
            item.speech_recognition_created,
            item.new_teacher_review_system_created,
            item.new_concept_system_created,
            item.concept_candidate_created,
            item.reviewed_concept_created,
            item.memory_write_performed,
            item.action_selection_influence_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _adapter_status(
    item: HostBodyFeedbackCandidateNormalizationRecord,
    *,
    uses_existing_package_90_review_path: bool,
    creates_parallel_review_path: bool,
    teacher_approval_created: bool,
    concept_candidate_created: bool,
    reviewed_concept_created: bool,
    memory_write_performed: bool,
    automatic_learning_approval_created: bool,
    action_selection_influence_created: bool,
    external_control_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
) -> str:
    if not validate_host_body_feedback_candidate_normalization(item)["valid"]:
        return "blocked_invalid_normalization"
    if not uses_existing_package_90_review_path or creates_parallel_review_path:
        return "blocked_parallel_review_path_detected"
    if teacher_approval_created:
        return "blocked_teacher_approval_created"
    if concept_candidate_created:
        return "blocked_concept_candidate_created"
    if reviewed_concept_created:
        return "blocked_reviewed_concept_created"
    if memory_write_performed or automatic_learning_approval_created:
        return "blocked_memory_write_detected"
    if action_selection_influence_created or external_control_created:
        return "blocked_action_selection_influence_detected"
    if first_output_created:
        return "blocked_first_output_detected"
    if live_runtime_session_created:
        return "blocked_live_runtime_detected"
    return {
        "host_body_uncertainty_evidence": "existing_review_adapter_created_for_uncertainty",
        "host_body_interesting_event_evidence": "existing_review_adapter_created_for_interesting_event",
        "host_body_teacher_review_request_evidence": "existing_review_adapter_created_for_teacher_review_request",
        "host_body_runtime_bridge_evidence": "existing_review_adapter_created_for_runtime_bridge",
    }.get(item.normalized_learning_feedback_kind, "existing_review_adapter_created")


def _adapter_summary(status: str) -> str:
    if status.startswith("existing_review_adapter_created"):
        return "Adapter payload targets the existing Package 90 LearningFeedbackCandidate review path."
    return "Existing learning review adapter is blocked."


def _adapter_has_forbidden(item: HostBodyFeedbackExistingReviewAdapterRecord) -> bool:
    return any(
        (
            item.creates_parallel_review_path,
            item.teacher_approval_created,
            item.concept_candidate_created,
            item.reviewed_concept_created,
            item.memory_write_performed,
            item.automatic_learning_approval_created,
            item.action_selection_influence_created,
            item.external_control_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _replay_status(
    adapter: HostBodyFeedbackExistingReviewAdapterRecord,
    *,
    result: str,
    creates_new_review_result_types: bool,
    teacher_approval_created: bool,
    concept_candidate_created: bool,
    reviewed_concept_created: bool,
    memory_write_performed: bool,
    automatic_learning_approval_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
) -> str:
    if not validate_host_body_feedback_existing_review_adapter(adapter)["valid"]:
        return "blocked_invalid_adapter"
    if creates_new_review_result_types:
        return "blocked_new_review_result_type_detected"
    if teacher_approval_created:
        return "blocked_teacher_approval_created"
    if concept_candidate_created:
        return "blocked_concept_candidate_created"
    if reviewed_concept_created:
        return "blocked_reviewed_concept_created"
    if memory_write_performed or automatic_learning_approval_created:
        return "blocked_memory_write_detected"
    if first_output_created:
        return "blocked_first_output_detected"
    if live_runtime_session_created:
        return "blocked_live_runtime_detected"
    return {
        "approved": "existing_review_replay_recorded_approved",
        "rejected": "existing_review_replay_recorded_rejected",
        "deferred": "existing_review_replay_recorded_deferred",
        "needs_more_evidence": "existing_review_replay_recorded_needs_more_evidence",
        "conflict_detected": "existing_review_replay_recorded_conflict_detected",
    }.get(result, "existing_review_replay_recorded")


def _replay_kind(status: str, result: str) -> str:
    if status.startswith("blocked_"):
        return "blocked_replay"
    return {
        "approved": "existing_review_approved_replay",
        "rejected": "existing_review_rejected_replay",
        "deferred": "existing_review_deferred_replay",
        "needs_more_evidence": "existing_review_needs_more_evidence_replay",
        "conflict_detected": "existing_review_conflict_replay",
    }.get(result, "existing_review_compatibility_replay")


def _replay_summary(status: str, result: str) -> str:
    if status.startswith("existing_review_replay_recorded"):
        return f"Existing learning review result replayed as {result}."
    return "Existing learning review replay is blocked."


def _review_result_reason_codes(result: str, status: str) -> tuple[str, ...]:
    if status.startswith("blocked_"):
        return (status,)
    return (f"existing_review_result:{result}", "package_90_result_type_reused")


def _replay_has_forbidden(item: HostBodyFeedbackExistingReviewReplayRecord) -> bool:
    return any(
        (
            item.creates_new_review_result_types,
            item.teacher_approval_created,
            item.concept_candidate_created,
            item.reviewed_concept_created,
            item.memory_write_performed,
            item.automatic_learning_approval_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _concept_compat_status(
    replay: HostBodyFeedbackExistingReviewReplayRecord,
    *,
    concept_candidate_created_by_this_package: bool,
    reviewed_concept_created_by_this_package: bool,
    memory_write_performed: bool,
    automatic_learning_approval_created: bool,
    action_selection_influence_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
) -> str:
    if not validate_host_body_feedback_existing_review_replay(replay)["valid"]:
        return "blocked_invalid_review_replay"
    if concept_candidate_created_by_this_package:
        return "blocked_concept_candidate_created_by_this_package"
    if reviewed_concept_created_by_this_package:
        return "blocked_reviewed_concept_created_by_this_package"
    if memory_write_performed or automatic_learning_approval_created:
        return "blocked_memory_write_detected"
    if action_selection_influence_created:
        return "blocked_action_selection_influence_detected"
    if first_output_created:
        return "blocked_first_output_detected"
    if live_runtime_session_created:
        return "blocked_live_runtime_detected"
    if replay.approved_for_existing_concept_candidate_draft:
        return "host_body_feedback_compatible_with_existing_concept_candidate_path"
    return "host_body_feedback_review_result_not_approved_no_concept_path"


def _concept_compat_kind(replay: HostBodyFeedbackExistingReviewReplayRecord, status: str) -> str:
    if status.startswith("blocked_"):
        return "blocked_compatibility"
    if replay.approved_for_existing_concept_candidate_draft:
        return "approved_host_body_feedback_to_existing_concept_candidate_path"
    if replay.rejected_by_existing_review:
        return "rejected_host_body_feedback_no_concept_path"
    if replay.deferred_by_existing_review:
        return "deferred_host_body_feedback_no_concept_path"
    if replay.needs_more_evidence_by_existing_review:
        return "needs_more_evidence_host_body_feedback_no_concept_path"
    if replay.conflict_detected_by_existing_review:
        return "conflict_host_body_feedback_no_concept_path"
    return "deferred_host_body_feedback_no_concept_path"


def _concept_compat_summary(status: str) -> str:
    if status == "host_body_feedback_compatible_with_existing_concept_candidate_path":
        return "Approved existing review replay is compatible with the existing ConceptCandidate draft path."
    if status == "host_body_feedback_review_result_not_approved_no_concept_path":
        return "Non-approved existing review replay creates no ConceptCandidate path in this package."
    return "ConceptCandidate compatibility is blocked."


def _concept_compat_has_forbidden(item: HostBodyFeedbackConceptCandidateCompatibilityRecord) -> bool:
    return any(
        (
            item.concept_candidate_created_by_this_package,
            item.reviewed_concept_created_by_this_package,
            item.memory_write_performed,
            item.automatic_learning_approval_created,
            item.action_selection_influence_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _trace_status(
    *,
    normalizations: tuple[HostBodyFeedbackCandidateNormalizationRecord, ...],
    adapters: tuple[HostBodyFeedbackExistingReviewAdapterRecord, ...],
    review_replays: tuple[HostBodyFeedbackExistingReviewReplayRecord, ...],
    concept_candidate_compatibilities: tuple[HostBodyFeedbackConceptCandidateCompatibilityRecord, ...],
    parallel_learning_pipeline_created: bool,
    concept_candidate_created_by_this_package: bool,
    reviewed_concept_created_by_this_package: bool,
    memory_write_performed: bool,
    action_selection_influence_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
) -> str:
    if any(not validate_host_body_feedback_candidate_normalization(item)["valid"] for item in normalizations):
        return "blocked_invalid_normalization"
    if any(not validate_host_body_feedback_existing_review_adapter(item)["valid"] for item in adapters):
        return "blocked_invalid_adapter"
    if any(not validate_host_body_feedback_existing_review_replay(item)["valid"] for item in review_replays):
        return "blocked_invalid_replay"
    if any(not validate_host_body_feedback_concept_candidate_compatibility(item)["valid"] for item in concept_candidate_compatibilities):
        return "blocked_invalid_concept_candidate_compatibility"
    if parallel_learning_pipeline_created:
        return "blocked_parallel_learning_pipeline_detected"
    if concept_candidate_created_by_this_package:
        return "blocked_concept_candidate_created_by_this_package"
    if reviewed_concept_created_by_this_package:
        return "blocked_reviewed_concept_created_by_this_package"
    if memory_write_performed:
        return "blocked_memory_write_detected"
    if action_selection_influence_created:
        return "blocked_action_selection_influence_detected"
    if first_output_created:
        return "blocked_first_output_detected"
    if live_runtime_session_created:
        return "blocked_live_runtime_detected"
    if not normalizations:
        return "host_body_feedback_existing_learning_pipeline_trace_recorded_empty"
    return "host_body_feedback_existing_learning_pipeline_trace_recorded"


def _trace_kind(count: int, status: str) -> str:
    if status.startswith("blocked_"):
        return "blocked_existing_pipeline_trace"
    if count == 0:
        return "empty_existing_pipeline_trace"
    if count > 1:
        return "mixed_host_body_feedback_existing_pipeline_trace"
    return "single_host_body_feedback_existing_pipeline_trace"


def _trace_summary(status: str, count: int) -> str:
    if status == "host_body_feedback_existing_learning_pipeline_trace_recorded":
        return f"{count} Host Body feedback compatibility record(s) use the existing learning pipeline only."
    if status == "host_body_feedback_existing_learning_pipeline_trace_recorded_empty":
        return "Empty existing learning pipeline compatibility trace recorded."
    return "Existing learning pipeline compatibility trace is blocked."


def _trace_has_forbidden(item: HostBodyFeedbackExistingLearningPipelineTraceRecord) -> bool:
    return any(
        (
            item.parallel_learning_pipeline_created,
            item.concept_candidate_created_by_this_package,
            item.reviewed_concept_created_by_this_package,
            item.memory_write_performed,
            item.automatic_learning_approval_created,
            item.action_selection_influence_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _audit_reasons(
    *,
    plan: HostBodyExistingLearningPipelineCompatibilityPlanRecord | None,
    trace: HostBodyFeedbackExistingLearningPipelineTraceRecord | None,
    normalizations: tuple[HostBodyFeedbackCandidateNormalizationRecord, ...],
    adapters: tuple[HostBodyFeedbackExistingReviewAdapterRecord, ...],
    review_replays: tuple[HostBodyFeedbackExistingReviewReplayRecord, ...],
    concept_candidate_compatibilities: tuple[HostBodyFeedbackConceptCandidateCompatibilityRecord, ...],
    force_external_control: bool,
    force_thought_engine_behavior: bool,
    force_production_behavior: bool,
) -> list[str]:
    reasons: list[str] = []
    if plan is None or plan.plan_status == "blocked_missing_host_body_learning_bridge_audit":
        reasons.append("missing_plan")
    elif plan.plan_status == "blocked_new_teacher_review_system_allowed":
        reasons.append("parallel_teacher_review")
    elif plan.plan_status == "blocked_new_concept_system_allowed":
        reasons.append("parallel_concept_system")
    elif plan.plan_status == "blocked_direct_reviewed_concept_allowed":
        reasons.append("reviewed_concept_by_package")
    elif plan.plan_status == "blocked_memory_write_allowed":
        reasons.append("memory_write")
    elif plan.plan_status == "blocked_action_selection_influence_allowed":
        reasons.append("action_influence")
    elif plan.plan_status == "blocked_first_output_allowed":
        reasons.append("first_output")
    elif plan.plan_status == "blocked_live_runtime_allowed":
        reasons.append("live_runtime")
    if any(item.creates_parallel_review_path for item in adapters):
        reasons.append("parallel_teacher_review")
    if any(item.new_concept_system_created for item in normalizations):
        reasons.append("parallel_concept_system")
    if any(item.concept_candidate_created for item in adapters + review_replays) or (
        trace and trace.concept_candidate_created_by_this_package
    ) or any(item.concept_candidate_created_by_this_package for item in concept_candidate_compatibilities):
        reasons.append("concept_candidate_by_package")
    if any(item.reviewed_concept_created for item in adapters + review_replays) or (
        trace and trace.reviewed_concept_created_by_this_package
    ) or any(item.reviewed_concept_created_by_this_package for item in concept_candidate_compatibilities):
        reasons.append("reviewed_concept_by_package")
    if any(item.memory_write_performed for item in normalizations + adapters + review_replays) or (
        trace and trace.memory_write_performed
    ) or any(item.memory_write_performed for item in concept_candidate_compatibilities):
        reasons.append("memory_write")
    if any(item.automatic_learning_approval_created for item in adapters + review_replays) or (
        trace and trace.automatic_learning_approval_created
    ) or any(item.automatic_learning_approval_created for item in concept_candidate_compatibilities):
        reasons.append("automatic_learning_approval")
    if any(item.teacher_approval_created for item in adapters + review_replays):
        reasons.append("teacher_approval")
    if any(item.action_selection_influence_created for item in normalizations + adapters) or (
        trace and trace.action_selection_influence_created
    ) or any(item.action_selection_influence_created for item in concept_candidate_compatibilities):
        reasons.append("action_influence")
    if force_external_control or any(item.external_control_created for item in adapters):
        reasons.append("external_control")
    if any(item.first_output_created for item in normalizations + adapters + review_replays) or (
        trace and trace.first_output_created
    ) or any(item.first_output_created for item in concept_candidate_compatibilities):
        reasons.append("first_output")
    if any(item.live_runtime_session_created for item in normalizations + adapters + review_replays) or (
        trace and trace.live_runtime_session_created
    ) or any(item.live_runtime_session_created for item in concept_candidate_compatibilities):
        reasons.append("live_runtime")
    if force_thought_engine_behavior:
        reasons.append("thought_engine")
    if force_production_behavior:
        reasons.append("production_behavior")
    if any(not validate_host_body_feedback_candidate_normalization(item)["valid"] for item in normalizations):
        reasons.append("invalid_normalization")
    if any(not validate_host_body_feedback_existing_review_adapter(item)["valid"] for item in adapters):
        reasons.append("invalid_adapter")
    if any(not validate_host_body_feedback_existing_review_replay(item)["valid"] for item in review_replays):
        reasons.append("invalid_review_replay")
    if any(not validate_host_body_feedback_concept_candidate_compatibility(item)["valid"] for item in concept_candidate_compatibilities):
        reasons.append("invalid_concept_compatibility")
    if trace is None or not validate_host_body_feedback_existing_learning_pipeline_trace(trace)["valid"]:
        reasons.append("invalid_trace")
    return list(dict.fromkeys(reasons))


def _audit_status(reasons: list[str], preferred_pass_status: str | None) -> str:
    priority = (
        ("missing_plan", "blocked_missing_compatibility_plan"),
        ("parallel_teacher_review", "blocked_parallel_teacher_review_detected"),
        ("parallel_concept_system", "blocked_parallel_concept_system_detected"),
        ("concept_candidate_by_package", "blocked_concept_candidate_created_by_this_package"),
        ("reviewed_concept_by_package", "blocked_reviewed_concept_created_by_this_package"),
        ("memory_write", "blocked_memory_write_detected"),
        ("automatic_learning_approval", "blocked_automatic_learning_approval_detected"),
        ("teacher_approval", "blocked_teacher_approval_created"),
        ("action_influence", "blocked_action_selection_influence_detected"),
        ("external_control", "blocked_external_control_detected"),
        ("first_output", "blocked_first_output_detected"),
        ("live_runtime", "blocked_live_runtime_detected"),
        ("production_behavior", "blocked_production_behavior_detected"),
        ("invalid_normalization", "blocked_invalid_normalization"),
        ("invalid_adapter", "blocked_invalid_adapter"),
        ("invalid_review_replay", "blocked_invalid_review_replay"),
        ("invalid_concept_compatibility", "blocked_invalid_concept_candidate_compatibility"),
        ("invalid_trace", "blocked_invalid_pipeline_trace"),
    )
    for reason, status in priority:
        if reason in reasons:
            return status
    if preferred_pass_status:
        return preferred_pass_status
    return "passed_host_body_feedback_existing_learning_pipeline_compatibility"


def _readiness_summary(status: str) -> str:
    if status.startswith("ready_for_"):
        return "Host Body feedback compatibility is ready for the next bounded replay stage."
    if status.startswith("blocked_"):
        return "Host Body feedback compatibility readiness is blocked by forbidden authority."
    return "Host Body feedback compatibility readiness is not established."
