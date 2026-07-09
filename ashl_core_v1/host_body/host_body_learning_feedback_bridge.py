"""Host Body evidence to LearningFeedbackCandidate bridge records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    build_demo_camera_change_marks_interesting,
    build_demo_deferred_dispatch_requests_teacher_review,
    build_demo_host_idle_observe_again,
    build_demo_unknown_event_marks_uncertain,
    build_demo_update_home_status_choice,
)
from ashl_core_v1.host_body.host_body_runtime_bridge import (
    build_demo_deferred_dispatch_host_body_runtime_bridge,
    build_demo_mixed_host_body_runtime_bridge,
)
from ashl_core_v1.host_body.host_body_trace_history_lane import (
    build_demo_full_host_body_trace_history_lane,
)
from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
    build_demo_qingyin_home_internal_space_surface,
)
from ashl_core_v1.host_body.qingyin_host_body_v0_milestone_audit import (
    build_demo_qingyin_host_body_v0_milestone_pass,
)


SOURCE_ENGINE = "host_body"

PLAN_SCHEMA_VERSION = "qingyin_host_body_learning_bridge_plan_v0"
EVIDENCE_SCHEMA_VERSION = "qingyin_host_body_learning_evidence_packet_v0"
MAPPING_SCHEMA_VERSION = "qingyin_host_body_learning_feedback_candidate_mapping_v0"
BRIDGE_SCHEMA_VERSION = "qingyin_host_body_learning_feedback_bridge_v0"
SET_SCHEMA_VERSION = "qingyin_host_body_learning_feedback_candidate_set_v0"
AUDIT_SCHEMA_VERSION = "qingyin_host_body_learning_bridge_audit_v0"
READINESS_SCHEMA_VERSION = "qingyin_host_body_learning_bridge_readiness_v0"

BRIDGE_NAME = "host_body_evidence_to_learning_feedback_candidate_bridge"
BRIDGE_KIND = "teacher_reviewable_evidence_bridge"

ALLOWED_EVIDENCE_SOURCES = (
    "host_body_trace_history_readback",
    "host_body_internal_action_choice",
    "host_body_internal_action_result",
    "host_body_runtime_bridge_trace",
    "qingyin_home_teacher_observed_surface",
    "qingyin_home_status_light",
)
ALLOWED_FEEDBACK_CANDIDATE_KINDS = (
    "host_body_feedback_candidate",
    "host_body_uncertainty_feedback_candidate",
    "host_body_interesting_event_feedback_candidate",
    "host_body_teacher_review_feedback_candidate",
    "host_body_runtime_bridge_feedback_candidate",
)
FORBIDDEN_LEARNING_OUTPUTS = (
    "ConceptCandidate",
    "ReviewedConcept",
    "MemoryLearningTrace",
    "MemoryRoutingTrace",
    "MemoryApplicationData",
    "CoreMemoryWrite",
    "LongTermMemoryWrite",
    "ArchiveMemoryWrite",
    "AnchorWrite",
)
ALLOWED_EVIDENCE_THEMES = (
    "uncertainty_detected",
    "interesting_event_marked",
    "observe_again_requested",
    "teacher_review_requested",
    "event_processing_paused",
    "home_status_updated",
    "runtime_bridge_deferred",
    "unknown_event_seen",
    "repeated_host_event_seen",
    "none",
)

SAFE_CLAIM = (
    "ASHL Core v1 can convert read-only Qingyin Host Body v0 evidence into "
    "teacher-reviewable Host Body LearningFeedbackCandidate bridge records."
)
BLOCKED_CLAIMS = (
    "no_concept_candidate_created",
    "no_reviewed_concept_created",
    "no_memory_layer_write",
    "no_automatic_learning_approval",
    "no_teacher_approval_created",
    "no_task_action_selection_influence",
    "no_external_control",
    "no_first_output",
    "no_live_runtime_session",
)
READINESS_NEXT_PACKAGE = (
    "Package 109 / ASHL Core v1 Host Body Feedback Candidate Teacher Review Minimal v0"
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


def _slug(text: str | None) -> str:
    safe = [char.lower() if char.isalnum() else "_" for char in str(text or "none")]
    return "_".join("".join(safe).split("_"))[:100] or "empty"


@dataclass(frozen=True)
class HostBodyLearningBridgePlanRecord:
    host_body_learning_bridge_plan_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_v0_audit_id: str | None
    source_trace_history_audit_id: str | None
    source_internal_action_choice_audit_id: str | None
    bridge_name: str
    bridge_kind: str
    allowed_evidence_sources: tuple[str, ...]
    allowed_feedback_candidate_kinds: tuple[str, ...]
    forbidden_learning_outputs: tuple[str, ...]
    learning_feedback_candidate_allowed: bool
    concept_candidate_allowed: bool
    reviewed_concept_allowed: bool
    memory_write_allowed: bool
    automatic_learning_approval_allowed: bool
    teacher_approval_creation_allowed: bool
    task_action_selection_allowed: bool
    external_control_allowed: bool
    first_output_allowed: bool
    live_runtime_session_allowed: bool
    bridge_plan_status: str
    bridge_plan_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PLAN_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_learning_bridge_plan_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.bridge_name != BRIDGE_NAME:
            raise ValueError("bridge_name must be host_body_evidence_to_learning_feedback_candidate_bridge")
        if self.bridge_kind != BRIDGE_KIND:
            raise ValueError("bridge_kind must be teacher_reviewable_evidence_bridge")
        if self.bridge_plan_status not in {
            "host_body_learning_bridge_plan_created",
            "blocked_missing_host_body_v0_audit",
            "blocked_missing_trace_history_audit",
            "blocked_missing_internal_action_choice_audit",
            "blocked_concept_candidate_allowed",
            "blocked_reviewed_concept_allowed",
            "blocked_memory_write_allowed",
            "blocked_action_selection_allowed",
            "blocked_first_output_allowed",
            "blocked_live_runtime_allowed",
            "blocked_forbidden_authority_detected",
        }:
            raise ValueError(f"unknown bridge_plan_status: {self.bridge_plan_status}")
        for name in (
            "allowed_evidence_sources",
            "allowed_feedback_candidate_kinds",
            "forbidden_learning_outputs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyLearningBridgePlanRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyLearningEvidencePacketRecord:
    host_body_learning_evidence_packet_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_bridge_plan_id: str
    source_trace_history_readback_id: str | None
    source_internal_action_choice_id: str | None
    source_internal_action_result_id: str | None
    source_runtime_bridge_trace_id: str | None
    source_teacher_observed_surface_id: str | None
    evidence_kind: str
    evidence_theme: str
    evidence_summary: str
    observed_event_refs: tuple[str, ...]
    internal_action_refs: tuple[str, ...]
    surface_refs: tuple[str, ...]
    evidence_payload: dict[str, Any]
    teacher_review_required: bool
    safe_for_learning_feedback_candidate: bool
    semantic_interpretation_created: bool
    speech_recognition_created: bool
    task_action_selection_influence_created: bool
    external_control_created: bool
    memory_write_performed: bool
    concept_candidate_created: bool
    reviewed_concept_created: bool
    automatic_learning_approval_created: bool
    teacher_approval_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVIDENCE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_learning_evidence_packet_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.evidence_kind not in {
            "host_body_uncertainty_evidence",
            "host_body_interesting_event_evidence",
            "host_body_observe_again_evidence",
            "host_body_teacher_review_request_evidence",
            "host_body_pause_event_processing_evidence",
            "host_body_home_status_update_evidence",
            "host_body_runtime_bridge_deferred_evidence",
            "host_body_unknown_event_evidence",
            "blocked_evidence",
        }:
            raise ValueError(f"unknown evidence_kind: {self.evidence_kind}")
        if self.evidence_theme not in ALLOWED_EVIDENCE_THEMES:
            raise ValueError(f"unknown evidence_theme: {self.evidence_theme}")
        for name in (
            "observed_event_refs",
            "internal_action_refs",
            "surface_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))
        object.__setattr__(self, "evidence_payload", dict(self.evidence_payload))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyLearningEvidencePacketRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyLearningFeedbackCandidateMappingRecord:
    host_body_learning_feedback_mapping_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_evidence_packet_id: str
    target_learning_feedback_candidate_id: str | None
    mapping_kind: str
    mapping_status: str
    mapping_summary: str
    feedback_candidate_kind: str
    feedback_candidate_scope: str
    candidate_created: bool
    candidate_bridge_ready: bool
    concept_candidate_created: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    teacher_approval_created: bool
    action_selection_influence_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MAPPING_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be qingyin_host_body_learning_feedback_candidate_mapping_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.mapping_kind not in {
            "host_body_evidence_to_learning_feedback_candidate",
            "host_body_evidence_to_bridge_compatible_candidate",
            "blocked_mapping",
        }:
            raise ValueError(f"unknown mapping_kind: {self.mapping_kind}")
        if self.feedback_candidate_kind not in ALLOWED_FEEDBACK_CANDIDATE_KINDS:
            raise ValueError(f"unknown feedback_candidate_kind: {self.feedback_candidate_kind}")
        if self.feedback_candidate_scope not in {
            "host_body_only",
            "host_body_trace_history_only",
            "host_body_internal_action_only",
            "host_body_runtime_bridge_only",
            "blocked",
        }:
            raise ValueError(f"unknown feedback_candidate_scope: {self.feedback_candidate_scope}")
        if self.mapping_status not in {
            "host_body_evidence_mapped_to_learning_feedback_candidate",
            "host_body_evidence_mapped_to_bridge_compatible_candidate",
            "blocked_invalid_evidence_packet",
            "blocked_concept_candidate_creation_detected",
            "blocked_reviewed_concept_creation_detected",
            "blocked_memory_write_detected",
            "blocked_action_selection_influence_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown mapping_status: {self.mapping_status}")
        object.__setattr__(
            self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs)
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyLearningFeedbackCandidateMappingRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyLearningFeedbackCandidateBridgeRecord:
    host_body_learning_feedback_bridge_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_bridge_plan_id: str
    source_evidence_packet_id: str
    source_mapping_id: str
    bridge_status: str
    bridge_summary: str
    learning_feedback_candidate_created: bool
    learning_feedback_candidate_bridge_ready: bool
    teacher_review_required: bool
    teacher_approval_created: bool
    concept_candidate_created: bool
    reviewed_concept_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    task_action_selection_influence_created: bool
    external_control_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BRIDGE_SCHEMA_VERSION:
            raise ValueError("schema_version must be qingyin_host_body_learning_feedback_bridge_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.bridge_status not in {
            "host_body_learning_feedback_candidate_bridge_created",
            "host_body_learning_feedback_candidate_created",
            "host_body_learning_feedback_candidate_bridge_ready",
            "blocked_invalid_mapping",
            "blocked_teacher_approval_created",
            "blocked_concept_candidate_created",
            "blocked_reviewed_concept_created",
            "blocked_memory_write_detected",
            "blocked_action_selection_influence_detected",
            "blocked_first_output_detected",
            "blocked_live_runtime_detected",
        }:
            raise ValueError(f"unknown bridge_status: {self.bridge_status}")
        object.__setattr__(
            self, "source_trace_refs", _tuple_of_str("source_trace_refs", self.source_trace_refs)
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyLearningFeedbackCandidateBridgeRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyLearningFeedbackCandidateSetRecord:
    host_body_learning_feedback_candidate_set_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_bridge_plan_id: str
    evidence_packet_ids: tuple[str, ...]
    mapping_ids: tuple[str, ...]
    bridge_ids: tuple[str, ...]
    candidate_set_kind: str
    candidate_set_status: str
    candidate_set_summary: str
    evidence_packet_count: int
    mapping_count: int
    bridge_count: int
    learning_feedback_candidate_count: int
    teacher_review_required_count: int
    concept_candidate_created: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    teacher_approval_created: bool
    action_selection_influence_created: bool
    first_output_created: bool
    live_runtime_session_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SET_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be qingyin_host_body_learning_feedback_candidate_set_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.candidate_set_kind not in {
            "single_host_body_feedback_candidate_demo",
            "mixed_host_body_feedback_candidate_demo",
            "blocked_host_body_feedback_candidate_demo",
            "empty_host_body_feedback_candidate_demo",
        }:
            raise ValueError(f"unknown candidate_set_kind: {self.candidate_set_kind}")
        if self.candidate_set_status not in {
            "host_body_learning_feedback_candidate_set_recorded",
            "host_body_learning_feedback_candidate_set_recorded_empty",
            "host_body_learning_feedback_candidate_set_blocked_concept_candidate_created",
            "host_body_learning_feedback_candidate_set_blocked_reviewed_concept_created",
            "host_body_learning_feedback_candidate_set_blocked_memory_write",
            "host_body_learning_feedback_candidate_set_blocked_first_output",
            "host_body_learning_feedback_candidate_set_blocked_live_runtime",
        }:
            raise ValueError(f"unknown candidate_set_status: {self.candidate_set_status}")
        for name in ("evidence_packet_ids", "mapping_ids", "bridge_ids", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "HostBodyLearningFeedbackCandidateSetRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyLearningBridgeAudit:
    host_body_learning_bridge_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_bridge_plan_id: str | None
    source_candidate_set_id: str | None
    bridge_plan_valid: bool
    evidence_packets_valid: bool
    mappings_valid: bool
    bridges_valid: bool
    candidate_set_valid: bool
    host_body_v0_confirmed: bool
    learning_feedback_candidate_stage_only_confirmed: bool
    teacher_review_required_confirmed: bool
    no_concept_candidate_created: bool
    no_reviewed_concept_created: bool
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
            raise ValueError("schema_version must be qingyin_host_body_learning_bridge_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.audit_status not in {
            "passed_host_body_evidence_to_learning_feedback_candidate_bridge",
            "passed_host_body_uncertainty_feedback_candidate_bridge",
            "passed_host_body_interesting_event_feedback_candidate_bridge",
            "passed_host_body_teacher_review_feedback_candidate_bridge",
            "passed_host_body_runtime_bridge_feedback_candidate_bridge",
            "blocked_missing_bridge_plan",
            "blocked_invalid_evidence_packet",
            "blocked_invalid_mapping",
            "blocked_invalid_bridge",
            "blocked_invalid_candidate_set",
            "blocked_concept_candidate_created",
            "blocked_reviewed_concept_created",
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
    def from_dict(cls, data: dict[str, object]) -> "HostBodyLearningBridgeAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class HostBodyLearningBridgeReadinessRecord:
    host_body_learning_bridge_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_host_body_learning_bridge_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_teacher_review_of_host_body_feedback: bool
    ready_for_host_body_feedback_to_concept_candidate_review: bool
    ready_for_host_body_feedback_closed_loop_replay: bool
    ready_for_concept_candidate_auto_creation: bool
    ready_for_reviewed_concept_creation_without_teacher: bool
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
            raise ValueError("schema_version must be qingyin_host_body_learning_bridge_readiness_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be host_body")
        if self.readiness_status not in {
            "ready_for_teacher_review_of_host_body_feedback_only",
            "ready_for_host_body_feedback_to_concept_candidate_review_only",
            "ready_for_host_body_feedback_closed_loop_replay_only",
            "not_ready_missing_host_body_learning_bridge_audit",
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
    def from_dict(cls, data: dict[str, object]) -> "HostBodyLearningBridgeReadinessRecord":
        return cls(**dict(data))


def build_host_body_learning_bridge_plan(
    *,
    host_body_v0_audit: dict[str, object] | None,
    trace_history_audit: dict[str, object] | None,
    internal_action_choice_audit: dict[str, object] | None,
    learning_feedback_candidate_allowed: bool = True,
    concept_candidate_allowed: bool = False,
    reviewed_concept_allowed: bool = False,
    memory_write_allowed: bool = False,
    automatic_learning_approval_allowed: bool = False,
    teacher_approval_creation_allowed: bool = False,
    task_action_selection_allowed: bool = False,
    external_control_allowed: bool = False,
    first_output_allowed: bool = False,
    live_runtime_session_allowed: bool = False,
) -> HostBodyLearningBridgePlanRecord:
    status = _plan_status(
        host_body_v0_audit=host_body_v0_audit,
        trace_history_audit=trace_history_audit,
        internal_action_choice_audit=internal_action_choice_audit,
        concept_candidate_allowed=concept_candidate_allowed,
        reviewed_concept_allowed=reviewed_concept_allowed,
        memory_write_allowed=memory_write_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        teacher_approval_creation_allowed=teacher_approval_creation_allowed,
        task_action_selection_allowed=task_action_selection_allowed,
        external_control_allowed=external_control_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
    )
    refs = _refs_from(host_body_v0_audit, trace_history_audit, internal_action_choice_audit)
    return HostBodyLearningBridgePlanRecord(
        host_body_learning_bridge_plan_id=f"host_body_learning_bridge_plan:{_slug(status)}",
        schema_version=PLAN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_v0_audit_id=_id(host_body_v0_audit, "host_body_v0_milestone_audit_id"),
        source_trace_history_audit_id=_id(trace_history_audit, "trace_history_audit_id"),
        source_internal_action_choice_audit_id=_id(
            internal_action_choice_audit, "internal_action_choice_audit_id"
        ),
        bridge_name=BRIDGE_NAME,
        bridge_kind=BRIDGE_KIND,
        allowed_evidence_sources=ALLOWED_EVIDENCE_SOURCES,
        allowed_feedback_candidate_kinds=ALLOWED_FEEDBACK_CANDIDATE_KINDS,
        forbidden_learning_outputs=FORBIDDEN_LEARNING_OUTPUTS,
        learning_feedback_candidate_allowed=learning_feedback_candidate_allowed,
        concept_candidate_allowed=concept_candidate_allowed,
        reviewed_concept_allowed=reviewed_concept_allowed,
        memory_write_allowed=memory_write_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        teacher_approval_creation_allowed=teacher_approval_creation_allowed,
        task_action_selection_allowed=task_action_selection_allowed,
        external_control_allowed=external_control_allowed,
        first_output_allowed=first_output_allowed,
        live_runtime_session_allowed=live_runtime_session_allowed,
        bridge_plan_status=status,
        bridge_plan_summary=_plan_summary(status),
        source_trace_refs=refs,
    )


def validate_host_body_learning_bridge_plan(
    record: HostBodyLearningBridgePlanRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _plan(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.bridge_plan_status == "host_body_learning_bridge_plan_created"
    valid = valid and item.learning_feedback_candidate_allowed
    valid = valid and not any(
        (
            item.concept_candidate_allowed,
            item.reviewed_concept_allowed,
            item.memory_write_allowed,
            item.automatic_learning_approval_allowed,
            item.teacher_approval_creation_allowed,
            item.task_action_selection_allowed,
            item.external_control_allowed,
            item.first_output_allowed,
            item.live_runtime_session_allowed,
        )
    )
    return {"valid": valid, "status": item.bridge_plan_status, "reasons": [] if valid else [item.bridge_plan_status]}


def build_host_body_learning_evidence_packet(
    *,
    bridge_plan: HostBodyLearningBridgePlanRecord | dict[str, object],
    trace_history_readback: dict[str, object] | None = None,
    internal_action_choice: dict[str, object] | None = None,
    internal_action_result: dict[str, object] | None = None,
    runtime_bridge_trace: dict[str, object] | None = None,
    teacher_observed_surface: dict[str, object] | None = None,
    evidence_theme: str | None = None,
    semantic_interpretation_created: bool = False,
    speech_recognition_created: bool = False,
    task_action_selection_influence_created: bool = False,
    external_control_created: bool = False,
    memory_write_performed: bool = False,
    concept_candidate_created: bool = False,
    reviewed_concept_created: bool = False,
    automatic_learning_approval_created: bool = False,
    teacher_approval_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyLearningEvidencePacketRecord:
    plan = _plan(bridge_plan)
    theme = evidence_theme or _derive_evidence_theme(
        internal_action_choice=internal_action_choice,
        internal_action_result=internal_action_result,
        runtime_bridge_trace=runtime_bridge_trace,
    )
    forbidden = any(
        (
            semantic_interpretation_created,
            speech_recognition_created,
            task_action_selection_influence_created,
            external_control_created,
            memory_write_performed,
            concept_candidate_created,
            reviewed_concept_created,
            automatic_learning_approval_created,
            teacher_approval_created,
            first_output_created,
            live_runtime_session_created,
        )
    )
    kind = "blocked_evidence" if forbidden else _evidence_kind(theme)
    safe = not forbidden and plan.bridge_plan_status == "host_body_learning_bridge_plan_created"
    observed_refs = tuple(_filter_none((_id(trace_history_readback, "trace_history_readback_id"),)))
    internal_refs = tuple(
        _filter_none(
            (
                _id(internal_action_choice, "internal_action_choice_id"),
                _id(internal_action_result, "internal_action_result_id"),
            )
        )
    )
    surface_refs = tuple(_filter_none((_id(teacher_observed_surface, "home_teacher_observed_surface_id"),)))
    payload = {
        "evidence_theme": theme,
        "selected_internal_action_kind": _value(
            internal_action_choice, "selected_internal_action_kind"
        ),
        "result_kind": _value(internal_action_result, "result_kind"),
        "runtime_bridge_status": _value(runtime_bridge_trace, "bridge_trace_status"),
        "teacher_surface_status": _value(teacher_observed_surface, "teacher_surface_status"),
    }
    return HostBodyLearningEvidencePacketRecord(
        host_body_learning_evidence_packet_id=f"host_body_learning_evidence_packet:{_slug(theme)}:{_slug(kind)}",
        schema_version=EVIDENCE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_bridge_plan_id=plan.host_body_learning_bridge_plan_id,
        source_trace_history_readback_id=_id(trace_history_readback, "trace_history_readback_id"),
        source_internal_action_choice_id=_id(internal_action_choice, "internal_action_choice_id"),
        source_internal_action_result_id=_id(internal_action_result, "internal_action_result_id"),
        source_runtime_bridge_trace_id=_id(runtime_bridge_trace, "host_runtime_bridge_trace_id"),
        source_teacher_observed_surface_id=_id(
            teacher_observed_surface, "home_teacher_observed_surface_id"
        ),
        evidence_kind=kind,
        evidence_theme=theme,
        evidence_summary=_evidence_summary(theme, safe),
        observed_event_refs=observed_refs,
        internal_action_refs=internal_refs,
        surface_refs=surface_refs,
        evidence_payload=payload,
        teacher_review_required=True,
        safe_for_learning_feedback_candidate=safe,
        semantic_interpretation_created=semantic_interpretation_created,
        speech_recognition_created=speech_recognition_created,
        task_action_selection_influence_created=task_action_selection_influence_created,
        external_control_created=external_control_created,
        memory_write_performed=memory_write_performed,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        teacher_approval_created=teacher_approval_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=tuple(dict.fromkeys(plan.source_trace_refs + internal_refs + observed_refs + surface_refs)),
    )


def validate_host_body_learning_evidence_packet(
    record: HostBodyLearningEvidencePacketRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _evidence(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.safe_for_learning_feedback_candidate and item.evidence_kind != "blocked_evidence"
    valid = valid and item.teacher_review_required and not _evidence_has_forbidden(item)
    return {"valid": valid, "status": item.evidence_kind, "reasons": [] if valid else [_evidence_block_reason(item)]}


def map_host_body_evidence_to_learning_feedback_candidate(
    *,
    evidence_packet: HostBodyLearningEvidencePacketRecord | dict[str, object],
    candidate_created: bool = False,
    candidate_bridge_ready: bool = True,
    concept_candidate_created: bool = False,
    reviewed_concept_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    teacher_approval_created: bool = False,
    action_selection_influence_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyLearningFeedbackCandidateMappingRecord:
    evidence = _evidence(evidence_packet)
    status = _mapping_status(
        evidence=evidence,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        teacher_approval_created=teacher_approval_created,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    kind = (
        "blocked_mapping"
        if status.startswith("blocked")
        else (
            "host_body_evidence_to_learning_feedback_candidate"
            if candidate_created
            else "host_body_evidence_to_bridge_compatible_candidate"
        )
    )
    feedback_kind = _feedback_candidate_kind(evidence.evidence_theme)
    return HostBodyLearningFeedbackCandidateMappingRecord(
        host_body_learning_feedback_mapping_id=f"host_body_learning_feedback_mapping:{_slug(evidence.evidence_theme)}:{_slug(status)}",
        schema_version=MAPPING_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_evidence_packet_id=evidence.host_body_learning_evidence_packet_id,
        target_learning_feedback_candidate_id=(
            f"learning_feedback_candidate:host_body:{_slug(evidence.evidence_theme)}"
            if candidate_created and not status.startswith("blocked")
            else None
        ),
        mapping_kind=kind,
        mapping_status=status,
        mapping_summary=_mapping_summary(status, feedback_kind),
        feedback_candidate_kind=feedback_kind,
        feedback_candidate_scope=_feedback_candidate_scope(evidence.evidence_theme, status),
        candidate_created=candidate_created and not status.startswith("blocked"),
        candidate_bridge_ready=candidate_bridge_ready and not status.startswith("blocked"),
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed or automatic_learning_approval_created or teacher_approval_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        teacher_approval_created=teacher_approval_created,
        action_selection_influence_created=action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=evidence.source_trace_refs,
    )


def validate_host_body_learning_feedback_candidate_mapping(
    record: HostBodyLearningFeedbackCandidateMappingRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _mapping(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.mapping_status.startswith("host_body_evidence_mapped_to_")
    valid = valid and not _mapping_has_forbidden(item)
    return {"valid": valid, "status": item.mapping_status, "reasons": [] if valid else [item.mapping_status]}


def build_host_body_learning_feedback_candidate_bridge(
    *,
    bridge_plan: HostBodyLearningBridgePlanRecord | dict[str, object],
    evidence_packet: HostBodyLearningEvidencePacketRecord | dict[str, object],
    mapping: HostBodyLearningFeedbackCandidateMappingRecord | dict[str, object],
    teacher_approval_created: bool = False,
    concept_candidate_created: bool = False,
    reviewed_concept_created: bool = False,
    memory_layer_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    task_action_selection_influence_created: bool = False,
    external_control_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> HostBodyLearningFeedbackCandidateBridgeRecord:
    plan = _plan(bridge_plan)
    evidence = _evidence(evidence_packet)
    mapping_item = _mapping(mapping)
    status = _bridge_status(
        mapping=mapping_item,
        teacher_approval_created=teacher_approval_created,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        task_action_selection_influence_created=task_action_selection_influence_created,
        external_control_created=external_control_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    return HostBodyLearningFeedbackCandidateBridgeRecord(
        host_body_learning_feedback_bridge_id=f"host_body_learning_feedback_bridge:{_slug(evidence.evidence_theme)}:{_slug(status)}",
        schema_version=BRIDGE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_bridge_plan_id=plan.host_body_learning_bridge_plan_id,
        source_evidence_packet_id=evidence.host_body_learning_evidence_packet_id,
        source_mapping_id=mapping_item.host_body_learning_feedback_mapping_id,
        bridge_status=status,
        bridge_summary=_bridge_summary(status),
        learning_feedback_candidate_created=mapping_item.candidate_created and not status.startswith("blocked"),
        learning_feedback_candidate_bridge_ready=mapping_item.candidate_bridge_ready and not status.startswith("blocked"),
        teacher_review_required=True,
        teacher_approval_created=teacher_approval_created,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_layer_write_performed=memory_layer_write_performed or automatic_learning_approval_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        task_action_selection_influence_created=task_action_selection_influence_created,
        external_control_created=external_control_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
        source_trace_refs=evidence.source_trace_refs,
    )


def validate_host_body_learning_feedback_candidate_bridge(
    record: HostBodyLearningFeedbackCandidateBridgeRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _bridge(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.bridge_status.startswith("host_body_learning_feedback_candidate")
    valid = valid and item.teacher_review_required and not _bridge_has_forbidden(item)
    return {"valid": valid, "status": item.bridge_status, "reasons": [] if valid else [item.bridge_status]}


def build_host_body_learning_feedback_candidate_set(
    *,
    bridge_plan: HostBodyLearningBridgePlanRecord | dict[str, object],
    evidence_packets: tuple[HostBodyLearningEvidencePacketRecord | dict[str, object], ...] | list[HostBodyLearningEvidencePacketRecord | dict[str, object]],
    mappings: tuple[HostBodyLearningFeedbackCandidateMappingRecord | dict[str, object], ...] | list[HostBodyLearningFeedbackCandidateMappingRecord | dict[str, object]],
    bridges: tuple[HostBodyLearningFeedbackCandidateBridgeRecord | dict[str, object], ...] | list[HostBodyLearningFeedbackCandidateBridgeRecord | dict[str, object]],
) -> HostBodyLearningFeedbackCandidateSetRecord:
    plan = _plan(bridge_plan)
    evidence_items = tuple(_evidence(item) for item in evidence_packets)
    mapping_items = tuple(_mapping(item) for item in mappings)
    bridge_items = tuple(_bridge(item) for item in bridges)
    status = _set_status(evidence_items, mapping_items, bridge_items)
    kind = _set_kind(evidence_items, status)
    refs = tuple(
        dict.fromkeys(
            ref
            for group in (evidence_items, mapping_items, bridge_items)
            for item in group
            for ref in item.source_trace_refs
        )
    )
    return HostBodyLearningFeedbackCandidateSetRecord(
        host_body_learning_feedback_candidate_set_id=f"host_body_learning_feedback_candidate_set:{_slug(kind)}:{_slug(status)}",
        schema_version=SET_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_bridge_plan_id=plan.host_body_learning_bridge_plan_id,
        evidence_packet_ids=tuple(item.host_body_learning_evidence_packet_id for item in evidence_items),
        mapping_ids=tuple(item.host_body_learning_feedback_mapping_id for item in mapping_items),
        bridge_ids=tuple(item.host_body_learning_feedback_bridge_id for item in bridge_items),
        candidate_set_kind=kind,
        candidate_set_status=status,
        candidate_set_summary=_set_summary(status),
        evidence_packet_count=len(evidence_items),
        mapping_count=len(mapping_items),
        bridge_count=len(bridge_items),
        learning_feedback_candidate_count=sum(1 for item in bridge_items if item.learning_feedback_candidate_created),
        teacher_review_required_count=sum(1 for item in bridge_items if item.teacher_review_required),
        concept_candidate_created=any(item.concept_candidate_created for item in mapping_items + bridge_items),
        reviewed_concept_created=any(item.reviewed_concept_created for item in mapping_items + bridge_items),
        memory_write_performed=any(
            item.memory_write_performed for item in mapping_items
        )
        or any(item.memory_layer_write_performed for item in bridge_items),
        automatic_learning_approval_created=any(
            item.automatic_learning_approval_created for item in mapping_items + bridge_items
        ),
        teacher_approval_created=any(item.teacher_approval_created for item in mapping_items + bridge_items),
        action_selection_influence_created=any(
            item.action_selection_influence_created for item in mapping_items
        )
        or any(item.task_action_selection_influence_created for item in bridge_items),
        first_output_created=any(item.first_output_created for item in mapping_items + bridge_items),
        live_runtime_session_created=any(item.live_runtime_session_created for item in mapping_items + bridge_items),
        source_trace_refs=refs,
    )


def validate_host_body_learning_feedback_candidate_set(
    record: HostBodyLearningFeedbackCandidateSetRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _candidate_set(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.candidate_set_status.startswith("host_body_learning_feedback_candidate_set_recorded")
    valid = valid and not _set_has_forbidden(item)
    return {"valid": valid, "status": item.candidate_set_status, "reasons": [] if valid else [item.candidate_set_status]}


def build_host_body_learning_bridge_audit(
    *,
    bridge_plan: HostBodyLearningBridgePlanRecord | dict[str, object] | None,
    evidence_packets: tuple[HostBodyLearningEvidencePacketRecord | dict[str, object], ...] | list[HostBodyLearningEvidencePacketRecord | dict[str, object]] = tuple(),
    mappings: tuple[HostBodyLearningFeedbackCandidateMappingRecord | dict[str, object], ...] | list[HostBodyLearningFeedbackCandidateMappingRecord | dict[str, object]] = tuple(),
    bridges: tuple[HostBodyLearningFeedbackCandidateBridgeRecord | dict[str, object], ...] | list[HostBodyLearningFeedbackCandidateBridgeRecord | dict[str, object]] = tuple(),
    candidate_set: HostBodyLearningFeedbackCandidateSetRecord | dict[str, object] | None = None,
    force_external_control: bool = False,
    force_thought_engine_behavior: bool = False,
    force_production_behavior: bool = False,
) -> HostBodyLearningBridgeAudit:
    plan = _plan(bridge_plan) if bridge_plan is not None else None
    evidence_items = tuple(_evidence(item) for item in evidence_packets)
    mapping_items = tuple(_mapping(item) for item in mappings)
    bridge_items = tuple(_bridge(item) for item in bridges)
    candidate_set_item = _candidate_set(candidate_set) if candidate_set is not None else None
    reasons = _audit_reasons(
        plan=plan,
        evidence_items=evidence_items,
        mapping_items=mapping_items,
        bridge_items=bridge_items,
        candidate_set=candidate_set_item,
        force_external_control=force_external_control,
        force_thought_engine_behavior=force_thought_engine_behavior,
        force_production_behavior=force_production_behavior,
    )
    status = _audit_status(reasons, evidence_items)
    refs = tuple(
        dict.fromkeys(
            ref
            for group in (evidence_items, mapping_items, bridge_items)
            for item in group
            for ref in item.source_trace_refs
        )
    )
    return HostBodyLearningBridgeAudit(
        host_body_learning_bridge_audit_id=f"host_body_learning_bridge_audit:{_slug(status)}",
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_bridge_plan_id=plan.host_body_learning_bridge_plan_id if plan else None,
        source_candidate_set_id=(
            candidate_set_item.host_body_learning_feedback_candidate_set_id if candidate_set_item else None
        ),
        bridge_plan_valid=plan is not None and plan.bridge_plan_status == "host_body_learning_bridge_plan_created",
        evidence_packets_valid=all(validate_host_body_learning_evidence_packet(item)["valid"] for item in evidence_items),
        mappings_valid=all(validate_host_body_learning_feedback_candidate_mapping(item)["valid"] for item in mapping_items),
        bridges_valid=all(validate_host_body_learning_feedback_candidate_bridge(item)["valid"] for item in bridge_items),
        candidate_set_valid=(
            candidate_set_item is not None
            and candidate_set_item.candidate_set_status.startswith(
                "host_body_learning_feedback_candidate_set_recorded"
            )
        ),
        host_body_v0_confirmed=True,
        learning_feedback_candidate_stage_only_confirmed=True,
        teacher_review_required_confirmed=all(item.teacher_review_required for item in evidence_items + bridge_items),
        no_concept_candidate_created="concept_candidate" not in reasons,
        no_reviewed_concept_created="reviewed_concept" not in reasons,
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
        source_trace_refs=refs,
    )


def validate_host_body_learning_bridge_audit(
    record: HostBodyLearningBridgeAudit | dict[str, object],
) -> dict[str, object]:
    try:
        item = _audit(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.audit_status.startswith("passed_")
    return {"valid": valid, "status": item.audit_status, "reasons": [] if valid else list(item.blocked_reasons)}


def build_host_body_learning_bridge_readiness(
    host_body_learning_bridge_audit: HostBodyLearningBridgeAudit | dict[str, object] | None,
) -> HostBodyLearningBridgeReadinessRecord:
    audit = _audit(host_body_learning_bridge_audit) if host_body_learning_bridge_audit is not None else None
    passed = audit is not None and audit.audit_status.startswith("passed_")
    if audit is None:
        status = "not_ready_missing_host_body_learning_bridge_audit"
    elif passed:
        status = "ready_for_teacher_review_of_host_body_feedback_only"
    elif audit.audit_status.startswith("blocked_"):
        status = "blocked_forbidden_authority_detected"
    else:
        status = "not_ready_boundary_failure"
    return HostBodyLearningBridgeReadinessRecord(
        host_body_learning_bridge_readiness_id=(
            f"host_body_learning_bridge_readiness:{audit.host_body_learning_bridge_audit_id}"
            if audit
            else "host_body_learning_bridge_readiness:missing_audit"
        ),
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_host_body_learning_bridge_audit_id=(
            audit.host_body_learning_bridge_audit_id if audit else "missing_host_body_learning_bridge_audit"
        ),
        current_verified_capability=SAFE_CLAIM if passed else "Host Body learning bridge audit did not pass.",
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason=(
            "Teacher-review Host Body LearningFeedbackCandidate bridge records and convert approved ones into ConceptCandidate drafts."
        ),
        ready_for_teacher_review_of_host_body_feedback=passed,
        ready_for_host_body_feedback_to_concept_candidate_review=passed,
        ready_for_host_body_feedback_closed_loop_replay=passed,
        ready_for_concept_candidate_auto_creation=False,
        ready_for_reviewed_concept_creation_without_teacher=False,
        ready_for_memory_layer_write=False,
        ready_for_action_selection_influence=False,
        ready_for_external_control=False,
        ready_for_first_output=False,
        ready_for_live_runtime_session=False,
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=audit.source_trace_refs if audit else tuple(),
    )


def validate_host_body_learning_bridge_readiness(
    record: HostBodyLearningBridgeReadinessRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _readiness(record)
    except Exception as error:
        return {"valid": False, "error": str(error)}
    valid = item.readiness_status.startswith("ready_for_")
    valid = valid and all(
        (
            item.ready_for_teacher_review_of_host_body_feedback,
            item.ready_for_host_body_feedback_to_concept_candidate_review,
            item.ready_for_host_body_feedback_closed_loop_replay,
        )
    )
    valid = valid and not any(
        (
            item.ready_for_concept_candidate_auto_creation,
            item.ready_for_reviewed_concept_creation_without_teacher,
            item.ready_for_memory_layer_write,
            item.ready_for_action_selection_influence,
            item.ready_for_external_control,
            item.ready_for_first_output,
            item.ready_for_live_runtime_session,
        )
    )
    return {"valid": valid, "status": item.readiness_status, "reasons": [] if valid else [item.readiness_status]}


def build_demo_uncertainty_to_learning_feedback_candidate() -> dict[str, object]:
    return _build_demo_bundle(action_payload=build_demo_unknown_event_marks_uncertain())


def build_demo_interesting_event_to_learning_feedback_candidate() -> dict[str, object]:
    return _build_demo_bundle(action_payload=build_demo_camera_change_marks_interesting())


def build_demo_teacher_review_request_to_learning_feedback_candidate() -> dict[str, object]:
    return _build_demo_bundle(action_payload=build_demo_deferred_dispatch_requests_teacher_review())


def build_demo_deferred_runtime_bridge_to_learning_feedback_candidate() -> dict[str, object]:
    return _build_demo_bundle(
        action_payload=build_demo_deferred_dispatch_requests_teacher_review(),
        runtime_payload=build_demo_deferred_dispatch_host_body_runtime_bridge(),
    )


def build_demo_blocked_concept_candidate_creation() -> dict[str, object]:
    return _build_demo_bundle(concept_candidate_created=True)


def build_demo_blocked_reviewed_concept_creation() -> dict[str, object]:
    return _build_demo_bundle(reviewed_concept_created=True)


def build_demo_blocked_memory_write_learning_bridge() -> dict[str, object]:
    return _build_demo_bundle(memory_write_performed=True)


def build_demo_blocked_action_influence_learning_bridge() -> dict[str, object]:
    return _build_demo_bundle(task_action_selection_influence_created=True)


def build_demo_blocked_first_output_learning_bridge() -> dict[str, object]:
    return _build_demo_bundle(first_output_created=True)


def build_demo_blocked_live_runtime_learning_bridge() -> dict[str, object]:
    return _build_demo_bundle(live_runtime_session_created=True)


def build_demo_host_body_learning_feedback_candidate_set() -> dict[str, object]:
    base = _demo_sources(build_demo_camera_change_marks_interesting(), build_demo_mixed_host_body_runtime_bridge())
    plan = base["plan"]
    packets = []
    mappings = []
    bridges = []
    for action_payload, runtime_payload in (
        (build_demo_unknown_event_marks_uncertain(), build_demo_mixed_host_body_runtime_bridge()),
        (build_demo_camera_change_marks_interesting(), build_demo_mixed_host_body_runtime_bridge()),
        (build_demo_deferred_dispatch_requests_teacher_review(), build_demo_deferred_dispatch_host_body_runtime_bridge()),
    ):
        sources = _demo_sources(action_payload, runtime_payload, plan=plan)
        packet = build_host_body_learning_evidence_packet(
            bridge_plan=plan,
            trace_history_readback=sources["trace_readback"],
            internal_action_choice=sources["action_choice"],
            internal_action_result=sources["action_result"],
            runtime_bridge_trace=sources["runtime_trace"],
            teacher_observed_surface=sources["teacher_surface"],
        )
        mapping = map_host_body_evidence_to_learning_feedback_candidate(evidence_packet=packet)
        bridge = build_host_body_learning_feedback_candidate_bridge(
            bridge_plan=plan,
            evidence_packet=packet,
            mapping=mapping,
        )
        packets.append(packet)
        mappings.append(mapping)
        bridges.append(bridge)
    candidate_set = build_host_body_learning_feedback_candidate_set(
        bridge_plan=plan,
        evidence_packets=tuple(packets),
        mappings=tuple(mappings),
        bridges=tuple(bridges),
    )
    audit = build_host_body_learning_bridge_audit(
        bridge_plan=plan,
        evidence_packets=tuple(packets),
        mappings=tuple(mappings),
        bridges=tuple(bridges),
        candidate_set=candidate_set,
    )
    readiness = build_host_body_learning_bridge_readiness(audit)
    return _payload(plan, tuple(packets), tuple(mappings), tuple(bridges), candidate_set, audit, readiness)


def render_host_body_learning_bridge_summary_text(
    audit: HostBodyLearningBridgeAudit | dict[str, object],
    readiness: HostBodyLearningBridgeReadinessRecord | dict[str, object] | None = None,
) -> str:
    item = _audit(audit)
    readiness_item = _readiness(readiness) if readiness is not None else None
    lines = [
        "Host Body Evidence To LearningFeedbackCandidate Bridge",
        f"audit_status: {item.audit_status}",
        f"no_concept_candidate_created: {item.no_concept_candidate_created}",
        f"no_memory_layer_write: {item.no_memory_layer_write}",
        f"no_action_selection_influence: {item.no_task_action_selection_influence}",
        f"no_first_output: {item.no_first_output}",
        f"no_live_runtime_session: {item.no_live_runtime_session}",
    ]
    if readiness_item is not None:
        lines.append(f"readiness_status: {readiness_item.readiness_status}")
    return "\n".join(lines)


def render_host_body_learning_feedback_candidate_table(
    candidate_set: HostBodyLearningFeedbackCandidateSetRecord | dict[str, object],
    evidence_packets: tuple[HostBodyLearningEvidencePacketRecord | dict[str, object], ...] | list[HostBodyLearningEvidencePacketRecord | dict[str, object]] = tuple(),
    mappings: tuple[HostBodyLearningFeedbackCandidateMappingRecord | dict[str, object], ...] | list[HostBodyLearningFeedbackCandidateMappingRecord | dict[str, object]] = tuple(),
) -> str:
    item = _candidate_set(candidate_set)
    evidence_items = tuple(_evidence(packet) for packet in evidence_packets)
    mapping_items = tuple(_mapping(mapping) for mapping in mappings)
    lines = ["theme | feedback_candidate_kind | bridge_ready"]
    for packet, mapping in zip(evidence_items, mapping_items):
        lines.append(
            f"{packet.evidence_theme} | {mapping.feedback_candidate_kind} | {mapping.candidate_bridge_ready}"
        )
    if not evidence_items:
        lines.append(f"empty | {item.candidate_set_status} | False")
    return "\n".join(lines)


def _build_demo_bundle(
    *,
    action_payload: dict[str, object] | None = None,
    runtime_payload: dict[str, object] | None = None,
    concept_candidate_created: bool = False,
    reviewed_concept_created: bool = False,
    memory_write_performed: bool = False,
    task_action_selection_influence_created: bool = False,
    first_output_created: bool = False,
    live_runtime_session_created: bool = False,
) -> dict[str, object]:
    action_payload = action_payload or build_demo_camera_change_marks_interesting()
    runtime_payload = runtime_payload or build_demo_mixed_host_body_runtime_bridge()
    sources = _demo_sources(action_payload, runtime_payload)
    plan = sources["plan"]
    packet = build_host_body_learning_evidence_packet(
        bridge_plan=plan,
        trace_history_readback=sources["trace_readback"],
        internal_action_choice=sources["action_choice"],
        internal_action_result=sources["action_result"],
        runtime_bridge_trace=sources["runtime_trace"],
        teacher_observed_surface=sources["teacher_surface"],
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed,
        task_action_selection_influence_created=task_action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    mapping = map_host_body_evidence_to_learning_feedback_candidate(
        evidence_packet=packet,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed,
        action_selection_influence_created=task_action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    bridge = build_host_body_learning_feedback_candidate_bridge(
        bridge_plan=plan,
        evidence_packet=packet,
        mapping=mapping,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_layer_write_performed=memory_write_performed,
        task_action_selection_influence_created=task_action_selection_influence_created,
        first_output_created=first_output_created,
        live_runtime_session_created=live_runtime_session_created,
    )
    candidate_set = build_host_body_learning_feedback_candidate_set(
        bridge_plan=plan,
        evidence_packets=(packet,),
        mappings=(mapping,),
        bridges=(bridge,),
    )
    audit = build_host_body_learning_bridge_audit(
        bridge_plan=plan,
        evidence_packets=(packet,),
        mappings=(mapping,),
        bridges=(bridge,),
        candidate_set=candidate_set,
    )
    readiness = build_host_body_learning_bridge_readiness(audit)
    return _payload(plan, (packet,), (mapping,), (bridge,), candidate_set, audit, readiness)


def _demo_sources(
    action_payload: dict[str, object],
    runtime_payload: dict[str, object],
    *,
    plan: HostBodyLearningBridgePlanRecord | None = None,
) -> dict[str, Any]:
    trace_payload = build_demo_full_host_body_trace_history_lane()
    home_payload = build_demo_qingyin_home_internal_space_surface()
    v0_payload = build_demo_qingyin_host_body_v0_milestone_pass()
    plan = plan or build_host_body_learning_bridge_plan(
        host_body_v0_audit=v0_payload["host_body_v0_milestone_audit"],
        trace_history_audit=trace_payload["trace_history_audit"],
        internal_action_choice_audit=action_payload["internal_action_choice_audit"],
    )
    return {
        "plan": plan,
        "trace_readback": trace_payload["trace_history_readback"],
        "action_choice": action_payload["internal_action_choice"],
        "action_result": action_payload["internal_action_result"],
        "runtime_trace": runtime_payload["host_body_runtime_bridge_trace"],
        "teacher_surface": home_payload["home_teacher_observed_surface"],
    }


def _payload(
    plan: HostBodyLearningBridgePlanRecord,
    evidence_packets: tuple[HostBodyLearningEvidencePacketRecord, ...],
    mappings: tuple[HostBodyLearningFeedbackCandidateMappingRecord, ...],
    bridges: tuple[HostBodyLearningFeedbackCandidateBridgeRecord, ...],
    candidate_set: HostBodyLearningFeedbackCandidateSetRecord,
    audit: HostBodyLearningBridgeAudit,
    readiness: HostBodyLearningBridgeReadinessRecord,
) -> dict[str, object]:
    return {
        "host_body_learning_bridge_plan": plan.to_dict(),
        "host_body_learning_evidence_packets": tuple(packet.to_dict() for packet in evidence_packets),
        "host_body_learning_feedback_mappings": tuple(mapping.to_dict() for mapping in mappings),
        "host_body_learning_feedback_bridges": tuple(bridge.to_dict() for bridge in bridges),
        "host_body_learning_feedback_candidate_set": candidate_set.to_dict(),
        "host_body_learning_bridge_audit": audit.to_dict(),
        "host_body_learning_bridge_readiness": readiness.to_dict(),
        "rendered_host_body_learning_bridge_summary": render_host_body_learning_bridge_summary_text(
            audit, readiness
        ),
        "rendered_host_body_learning_feedback_candidate_table": render_host_body_learning_feedback_candidate_table(
            candidate_set, evidence_packets, mappings
        ),
    }


def _plan(record: HostBodyLearningBridgePlanRecord | dict[str, object]) -> HostBodyLearningBridgePlanRecord:
    if isinstance(record, HostBodyLearningBridgePlanRecord):
        return record
    return HostBodyLearningBridgePlanRecord.from_dict(record)


def _evidence(record: HostBodyLearningEvidencePacketRecord | dict[str, object]) -> HostBodyLearningEvidencePacketRecord:
    if isinstance(record, HostBodyLearningEvidencePacketRecord):
        return record
    return HostBodyLearningEvidencePacketRecord.from_dict(record)


def _mapping(record: HostBodyLearningFeedbackCandidateMappingRecord | dict[str, object]) -> HostBodyLearningFeedbackCandidateMappingRecord:
    if isinstance(record, HostBodyLearningFeedbackCandidateMappingRecord):
        return record
    return HostBodyLearningFeedbackCandidateMappingRecord.from_dict(record)


def _bridge(record: HostBodyLearningFeedbackCandidateBridgeRecord | dict[str, object]) -> HostBodyLearningFeedbackCandidateBridgeRecord:
    if isinstance(record, HostBodyLearningFeedbackCandidateBridgeRecord):
        return record
    return HostBodyLearningFeedbackCandidateBridgeRecord.from_dict(record)


def _candidate_set(record: HostBodyLearningFeedbackCandidateSetRecord | dict[str, object]) -> HostBodyLearningFeedbackCandidateSetRecord:
    if isinstance(record, HostBodyLearningFeedbackCandidateSetRecord):
        return record
    return HostBodyLearningFeedbackCandidateSetRecord.from_dict(record)


def _audit(record: HostBodyLearningBridgeAudit | dict[str, object]) -> HostBodyLearningBridgeAudit:
    if isinstance(record, HostBodyLearningBridgeAudit):
        return record
    return HostBodyLearningBridgeAudit.from_dict(record)


def _readiness(record: HostBodyLearningBridgeReadinessRecord | dict[str, object]) -> HostBodyLearningBridgeReadinessRecord:
    if isinstance(record, HostBodyLearningBridgeReadinessRecord):
        return record
    return HostBodyLearningBridgeReadinessRecord.from_dict(record)


def _id(record: dict[str, object] | None, key: str) -> str | None:
    return str(record[key]) if record and record.get(key) is not None else None


def _value(record: dict[str, object] | None, key: str) -> object | None:
    return record.get(key) if record else None


def _refs_from(*records: dict[str, object] | None) -> tuple[str, ...]:
    refs: list[str] = []
    for record in records:
        if not record:
            continue
        value = record.get("source_trace_refs", ())
        if isinstance(value, list | tuple):
            refs.extend(str(item) for item in value)
    return tuple(dict.fromkeys(refs))


def _filter_none(values: tuple[str | None, ...]) -> tuple[str, ...]:
    return tuple(value for value in values if value)


def _status_passed(record: dict[str, object] | None, key: str) -> bool:
    return bool(record and str(record.get(key, "")).startswith("passed_"))


def _plan_status(**kwargs: Any) -> str:
    if not _status_passed(kwargs["host_body_v0_audit"], "audit_status"):
        return "blocked_missing_host_body_v0_audit"
    if not _status_passed(kwargs["trace_history_audit"], "audit_status"):
        return "blocked_missing_trace_history_audit"
    if not _status_passed(kwargs["internal_action_choice_audit"], "audit_status"):
        return "blocked_missing_internal_action_choice_audit"
    if kwargs["concept_candidate_allowed"]:
        return "blocked_concept_candidate_allowed"
    if kwargs["reviewed_concept_allowed"]:
        return "blocked_reviewed_concept_allowed"
    if (
        kwargs["memory_write_allowed"]
        or kwargs["automatic_learning_approval_allowed"]
        or kwargs["teacher_approval_creation_allowed"]
    ):
        return "blocked_memory_write_allowed"
    if kwargs["task_action_selection_allowed"] or kwargs["external_control_allowed"]:
        return "blocked_action_selection_allowed"
    if kwargs["first_output_allowed"]:
        return "blocked_first_output_allowed"
    if kwargs["live_runtime_session_allowed"]:
        return "blocked_live_runtime_allowed"
    return "host_body_learning_bridge_plan_created"


def _plan_summary(status: str) -> str:
    if status == "host_body_learning_bridge_plan_created":
        return "Host Body evidence may be bridged to teacher-reviewable LearningFeedbackCandidate material."
    return "Host Body learning bridge plan is blocked by missing evidence or forbidden authority."


def _derive_evidence_theme(
    *,
    internal_action_choice: dict[str, object] | None,
    internal_action_result: dict[str, object] | None,
    runtime_bridge_trace: dict[str, object] | None,
) -> str:
    if runtime_bridge_trace and str(runtime_bridge_trace.get("bridge_trace_status", "")).endswith("deferred_dispatch"):
        return "runtime_bridge_deferred"
    selected = str((internal_action_choice or {}).get("selected_internal_action_kind", ""))
    result_kind = str((internal_action_result or {}).get("result_kind", ""))
    if selected == "mark_uncertain":
        return "uncertainty_detected"
    if selected == "mark_event_interesting":
        return "interesting_event_marked"
    if selected == "observe_again":
        return "observe_again_requested"
    if selected == "request_teacher_review" or result_kind == "teacher_review_request_record":
        return "teacher_review_requested"
    if selected == "pause_event_processing":
        return "event_processing_paused"
    if selected == "update_home_status":
        return "home_status_updated"
    return "none"


def _evidence_kind(theme: str) -> str:
    return {
        "uncertainty_detected": "host_body_uncertainty_evidence",
        "interesting_event_marked": "host_body_interesting_event_evidence",
        "observe_again_requested": "host_body_observe_again_evidence",
        "teacher_review_requested": "host_body_teacher_review_request_evidence",
        "event_processing_paused": "host_body_pause_event_processing_evidence",
        "home_status_updated": "host_body_home_status_update_evidence",
        "runtime_bridge_deferred": "host_body_runtime_bridge_deferred_evidence",
        "unknown_event_seen": "host_body_unknown_event_evidence",
    }.get(theme, "host_body_unknown_event_evidence")


def _evidence_summary(theme: str, safe: bool) -> str:
    if not safe:
        return "Host Body learning evidence packet is blocked by forbidden authority."
    return f"Host Body learning evidence packet records {theme} for teacher review."


def _evidence_has_forbidden(item: HostBodyLearningEvidencePacketRecord) -> bool:
    return any(
        (
            item.semantic_interpretation_created,
            item.speech_recognition_created,
            item.task_action_selection_influence_created,
            item.external_control_created,
            item.memory_write_performed,
            item.concept_candidate_created,
            item.reviewed_concept_created,
            item.automatic_learning_approval_created,
            item.teacher_approval_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _evidence_block_reason(item: HostBodyLearningEvidencePacketRecord) -> str:
    if item.concept_candidate_created:
        return "concept_candidate_created"
    if item.reviewed_concept_created:
        return "reviewed_concept_created"
    if item.memory_write_performed:
        return "memory_write_performed"
    if item.task_action_selection_influence_created:
        return "action_selection_influence_created"
    if item.first_output_created:
        return "first_output_created"
    if item.live_runtime_session_created:
        return "live_runtime_session_created"
    return "invalid_evidence_packet"


def _feedback_candidate_kind(theme: str) -> str:
    return {
        "uncertainty_detected": "host_body_uncertainty_feedback_candidate",
        "interesting_event_marked": "host_body_interesting_event_feedback_candidate",
        "teacher_review_requested": "host_body_teacher_review_feedback_candidate",
        "runtime_bridge_deferred": "host_body_runtime_bridge_feedback_candidate",
    }.get(theme, "host_body_feedback_candidate")


def _feedback_candidate_scope(theme: str, status: str) -> str:
    if status.startswith("blocked"):
        return "blocked"
    if theme == "runtime_bridge_deferred":
        return "host_body_runtime_bridge_only"
    if theme in {"uncertainty_detected", "interesting_event_marked", "teacher_review_requested"}:
        return "host_body_internal_action_only"
    return "host_body_trace_history_only"


def _mapping_status(
    *,
    evidence: HostBodyLearningEvidencePacketRecord,
    concept_candidate_created: bool,
    reviewed_concept_created: bool,
    memory_write_performed: bool,
    automatic_learning_approval_created: bool,
    teacher_approval_created: bool,
    action_selection_influence_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
) -> str:
    if not validate_host_body_learning_evidence_packet(evidence)["valid"]:
        if concept_candidate_created or evidence.concept_candidate_created:
            return "blocked_concept_candidate_creation_detected"
        if reviewed_concept_created or evidence.reviewed_concept_created:
            return "blocked_reviewed_concept_creation_detected"
        if memory_write_performed or automatic_learning_approval_created or teacher_approval_created or evidence.memory_write_performed:
            return "blocked_memory_write_detected"
        if action_selection_influence_created or evidence.task_action_selection_influence_created:
            return "blocked_action_selection_influence_detected"
        if first_output_created or evidence.first_output_created:
            return "blocked_first_output_detected"
        if live_runtime_session_created or evidence.live_runtime_session_created:
            return "blocked_live_runtime_detected"
        return "blocked_invalid_evidence_packet"
    if concept_candidate_created:
        return "blocked_concept_candidate_creation_detected"
    if reviewed_concept_created:
        return "blocked_reviewed_concept_creation_detected"
    if memory_write_performed or automatic_learning_approval_created or teacher_approval_created:
        return "blocked_memory_write_detected"
    if action_selection_influence_created:
        return "blocked_action_selection_influence_detected"
    if first_output_created:
        return "blocked_first_output_detected"
    if live_runtime_session_created:
        return "blocked_live_runtime_detected"
    return "host_body_evidence_mapped_to_bridge_compatible_candidate"


def _mapping_summary(status: str, feedback_kind: str) -> str:
    if status.startswith("host_body_evidence_mapped"):
        return f"Host Body evidence mapped to {feedback_kind} bridge-compatible candidate."
    return "Host Body evidence mapping is blocked by forbidden authority."


def _mapping_has_forbidden(item: HostBodyLearningFeedbackCandidateMappingRecord) -> bool:
    return any(
        (
            item.concept_candidate_created,
            item.reviewed_concept_created,
            item.memory_write_performed,
            item.automatic_learning_approval_created,
            item.teacher_approval_created,
            item.action_selection_influence_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _bridge_status(
    *,
    mapping: HostBodyLearningFeedbackCandidateMappingRecord,
    teacher_approval_created: bool,
    concept_candidate_created: bool,
    reviewed_concept_created: bool,
    memory_layer_write_performed: bool,
    automatic_learning_approval_created: bool,
    task_action_selection_influence_created: bool,
    external_control_created: bool,
    first_output_created: bool,
    live_runtime_session_created: bool,
) -> str:
    if not validate_host_body_learning_feedback_candidate_mapping(mapping)["valid"]:
        return "blocked_invalid_mapping"
    if teacher_approval_created:
        return "blocked_teacher_approval_created"
    if concept_candidate_created:
        return "blocked_concept_candidate_created"
    if reviewed_concept_created:
        return "blocked_reviewed_concept_created"
    if memory_layer_write_performed or automatic_learning_approval_created:
        return "blocked_memory_write_detected"
    if task_action_selection_influence_created or external_control_created:
        return "blocked_action_selection_influence_detected"
    if first_output_created:
        return "blocked_first_output_detected"
    if live_runtime_session_created:
        return "blocked_live_runtime_detected"
    if mapping.candidate_created:
        return "host_body_learning_feedback_candidate_created"
    if mapping.candidate_bridge_ready:
        return "host_body_learning_feedback_candidate_bridge_ready"
    return "host_body_learning_feedback_candidate_bridge_created"


def _bridge_summary(status: str) -> str:
    if status.startswith("host_body_learning_feedback_candidate"):
        return "Host Body LearningFeedbackCandidate bridge record is ready for teacher review."
    return "Host Body LearningFeedbackCandidate bridge is blocked by forbidden authority."


def _bridge_has_forbidden(item: HostBodyLearningFeedbackCandidateBridgeRecord) -> bool:
    return any(
        (
            item.teacher_approval_created,
            item.concept_candidate_created,
            item.reviewed_concept_created,
            item.memory_layer_write_performed,
            item.automatic_learning_approval_created,
            item.task_action_selection_influence_created,
            item.external_control_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _set_status(
    evidence_items: tuple[HostBodyLearningEvidencePacketRecord, ...],
    mapping_items: tuple[HostBodyLearningFeedbackCandidateMappingRecord, ...],
    bridge_items: tuple[HostBodyLearningFeedbackCandidateBridgeRecord, ...],
) -> str:
    if any(item.concept_candidate_created for item in evidence_items + mapping_items + bridge_items):
        return "host_body_learning_feedback_candidate_set_blocked_concept_candidate_created"
    if any(item.reviewed_concept_created for item in evidence_items + mapping_items + bridge_items):
        return "host_body_learning_feedback_candidate_set_blocked_reviewed_concept_created"
    if any(getattr(item, "memory_write_performed", False) or getattr(item, "memory_layer_write_performed", False) for item in evidence_items + mapping_items + bridge_items):
        return "host_body_learning_feedback_candidate_set_blocked_memory_write"
    if any(getattr(item, "teacher_approval_created", False) for item in evidence_items + mapping_items + bridge_items):
        return "host_body_learning_feedback_candidate_set_blocked_memory_write"
    if any(item.first_output_created for item in evidence_items + mapping_items + bridge_items):
        return "host_body_learning_feedback_candidate_set_blocked_first_output"
    if any(item.live_runtime_session_created for item in evidence_items + mapping_items + bridge_items):
        return "host_body_learning_feedback_candidate_set_blocked_live_runtime"
    if not evidence_items and not mapping_items and not bridge_items:
        return "host_body_learning_feedback_candidate_set_recorded_empty"
    return "host_body_learning_feedback_candidate_set_recorded"


def _set_kind(evidence_items: tuple[HostBodyLearningEvidencePacketRecord, ...], status: str) -> str:
    if status.startswith("host_body_learning_feedback_candidate_set_blocked"):
        return "blocked_host_body_feedback_candidate_demo"
    if not evidence_items:
        return "empty_host_body_feedback_candidate_demo"
    if len(evidence_items) == 1:
        return "single_host_body_feedback_candidate_demo"
    return "mixed_host_body_feedback_candidate_demo"


def _set_summary(status: str) -> str:
    if status.startswith("host_body_learning_feedback_candidate_set_recorded"):
        return "Host Body learning feedback candidate set recorded for teacher review."
    return "Host Body learning feedback candidate set is blocked by forbidden authority."


def _set_has_forbidden(item: HostBodyLearningFeedbackCandidateSetRecord) -> bool:
    return any(
        (
            item.concept_candidate_created,
            item.reviewed_concept_created,
            item.memory_write_performed,
            item.automatic_learning_approval_created,
            item.teacher_approval_created,
            item.action_selection_influence_created,
            item.first_output_created,
            item.live_runtime_session_created,
        )
    )


def _audit_reasons(
    *,
    plan: HostBodyLearningBridgePlanRecord | None,
    evidence_items: tuple[HostBodyLearningEvidencePacketRecord, ...],
    mapping_items: tuple[HostBodyLearningFeedbackCandidateMappingRecord, ...],
    bridge_items: tuple[HostBodyLearningFeedbackCandidateBridgeRecord, ...],
    candidate_set: HostBodyLearningFeedbackCandidateSetRecord | None,
    force_external_control: bool,
    force_thought_engine_behavior: bool,
    force_production_behavior: bool,
) -> list[str]:
    reasons: list[str] = []
    if plan is None or plan.bridge_plan_status != "host_body_learning_bridge_plan_created":
        reasons.append("missing_plan")
    if any(not validate_host_body_learning_evidence_packet(item)["valid"] for item in evidence_items):
        reasons.append("invalid_evidence")
    if any(not validate_host_body_learning_feedback_candidate_mapping(item)["valid"] for item in mapping_items):
        reasons.append("invalid_mapping")
    if any(not validate_host_body_learning_feedback_candidate_bridge(item)["valid"] for item in bridge_items):
        reasons.append("invalid_bridge")
    if candidate_set is None or not candidate_set.candidate_set_status.startswith("host_body_learning_feedback_candidate_set_recorded"):
        reasons.append("invalid_candidate_set")
    groups = evidence_items + mapping_items + bridge_items + ((candidate_set,) if candidate_set else tuple())
    if any(getattr(item, "concept_candidate_created", False) for item in groups):
        reasons.append("concept_candidate")
    if any(getattr(item, "reviewed_concept_created", False) for item in groups):
        reasons.append("reviewed_concept")
    if any(getattr(item, "memory_write_performed", False) or getattr(item, "memory_layer_write_performed", False) for item in groups):
        reasons.append("memory_write")
    if any(getattr(item, "automatic_learning_approval_created", False) for item in groups):
        reasons.append("automatic_learning_approval")
    if any(getattr(item, "teacher_approval_created", False) for item in groups):
        reasons.append("teacher_approval")
    if any(getattr(item, "action_selection_influence_created", False) or getattr(item, "task_action_selection_influence_created", False) for item in groups):
        reasons.append("action_influence")
    if force_external_control or any(getattr(item, "external_control_created", False) for item in groups):
        reasons.append("external_control")
    if any(getattr(item, "first_output_created", False) for item in groups):
        reasons.append("first_output")
    if any(getattr(item, "live_runtime_session_created", False) for item in groups):
        reasons.append("live_runtime")
    if force_thought_engine_behavior:
        reasons.append("thought_engine")
    if force_production_behavior:
        reasons.append("production_behavior")
    return list(dict.fromkeys(reasons))


def _audit_status(
    reasons: list[str],
    evidence_items: tuple[HostBodyLearningEvidencePacketRecord, ...],
) -> str:
    priority = (
        ("missing_plan", "blocked_missing_bridge_plan"),
        ("concept_candidate", "blocked_concept_candidate_created"),
        ("reviewed_concept", "blocked_reviewed_concept_created"),
        ("automatic_learning_approval", "blocked_automatic_learning_approval_detected"),
        ("teacher_approval", "blocked_teacher_approval_created"),
        ("memory_write", "blocked_memory_write_detected"),
        ("action_influence", "blocked_action_selection_influence_detected"),
        ("external_control", "blocked_external_control_detected"),
        ("first_output", "blocked_first_output_detected"),
        ("live_runtime", "blocked_live_runtime_detected"),
        ("production_behavior", "blocked_production_behavior_detected"),
        ("thought_engine", "blocked_production_behavior_detected"),
        ("invalid_evidence", "blocked_invalid_evidence_packet"),
        ("invalid_mapping", "blocked_invalid_mapping"),
        ("invalid_bridge", "blocked_invalid_bridge"),
        ("invalid_candidate_set", "blocked_invalid_candidate_set"),
    )
    for reason, status in priority:
        if reason in reasons:
            return status
    themes = {item.evidence_theme for item in evidence_items}
    if themes == {"uncertainty_detected"}:
        return "passed_host_body_uncertainty_feedback_candidate_bridge"
    if themes == {"interesting_event_marked"}:
        return "passed_host_body_interesting_event_feedback_candidate_bridge"
    if themes == {"teacher_review_requested"}:
        return "passed_host_body_teacher_review_feedback_candidate_bridge"
    if themes == {"runtime_bridge_deferred"}:
        return "passed_host_body_runtime_bridge_feedback_candidate_bridge"
    return "passed_host_body_evidence_to_learning_feedback_candidate_bridge"


def _readiness_summary(status: str) -> str:
    if status.startswith("ready_for_"):
        return "Host Body learning bridge is ready for teacher review of Host Body feedback."
    if status == "not_ready_missing_host_body_learning_bridge_audit":
        return "Host Body learning bridge readiness is missing an audit."
    return "Host Body learning bridge readiness is blocked by forbidden authority."
