"""Teacher-gated feedback refined ConceptCandidate to working readback integration."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.feedback_concept_candidate_review_refinement import (
    FeedbackConceptCandidateCounterexampleCheckRecord,
    FeedbackConceptCandidateRefinementRecord,
    FeedbackConceptCandidateRefinementSafetyAudit,
    FeedbackConceptCandidateReviewRecord,
    FeedbackConceptCandidateScopeCheckRecord,
    build_demo_blocked_invalid_concept_candidate_draft_refinement,
    build_demo_blocked_unhandled_counterexample_refinement,
    build_demo_failed_expected_effect_refinement,
    build_demo_goal_reached_refinement,
    build_demo_no_progress_refinement,
    build_demo_observation_only_refinement,
    build_demo_successful_expected_effect_refinement,
    build_demo_system_fault_blocked_refinement,
    build_demo_unknown_outcome_held_refinement,
    validate_feedback_concept_candidate_counterexample_check_record,
    validate_feedback_concept_candidate_refinement_record,
    validate_feedback_concept_candidate_refinement_safety_audit,
    validate_feedback_concept_candidate_review_record,
    validate_feedback_concept_candidate_scope_check_record,
)


SOURCE_ENGINE = "learning_engine"
MEMORY_TARGET_ENGINE = "memory_engine"
TASK_SEED_ENGINE = "task_engine"
WORKING_READBACK_LAYER = "working_readback"

GATE_SCHEMA_VERSION = "learning_engine_feedback_refined_concept_reviewed_concept_gate_v0"
REVIEWED_CONCEPT_SCHEMA_VERSION = "learning_engine_feedback_derived_reviewed_concept_v0"
WORKING_READBACK_INTEGRATION_SCHEMA_VERSION = (
    "memory_engine_feedback_reviewed_concept_working_readback_integration_v0"
)
READBACK_SEED_SCHEMA_VERSION = "task_engine_feedback_reviewed_concept_readback_seed_v0"
ROLLBACK_SCHEMA_VERSION = "learning_engine_feedback_reviewed_concept_rollback_v0"
SAFETY_AUDIT_SCHEMA_VERSION = (
    "learning_engine_feedback_reviewed_concept_integration_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 can convert teacher-gated safe refined feedback-derived "
    "ConceptCandidate records into feedback-derived ReviewedConcept records and "
    "integrate them into the working readback path for future Task Working "
    "Memory advisory hints, while blocking Core/Long-term/Archive/Anchor memory "
    "writes, automatic learning approval, external execution, behavior change, "
    "and action authority changes."
)
BLOCKED_CLAIMS = (
    "no_core_memory_write",
    "no_long_term_memory_write",
    "no_archive_memory_write",
    "no_anchor_write",
    "no_automatic_learning_approval",
    "no_action_authority_change",
    "no_behavior_change",
)

PASSING_REFINEMENT_AUDIT_STATUSES = {
    "passed_feedback_concept_candidate_refinement_only",
}

ALLOWED_GATE_STATUSES = {
    "approved_for_feedback_reviewed_concept_and_working_readback",
    "held_for_more_evidence",
    "rejected",
    "conflict_detected",
    "blocked_invalid_refinement",
    "blocked_invalid_scope",
    "blocked_unhandled_counterexamples",
    "blocked_forbidden_authority_detected",
}
ALLOWED_APPROVAL_SOURCES = {"explicit_teacher_review", "demo_review"}
ALLOWED_APPROVAL_ACTOR_ROLES = {"teacher", "project_owner", "system_demo"}
ALLOWED_REVIEWED_CONCEPT_STATUSES = {
    "feedback_reviewed_concept_created",
    "held_for_more_evidence",
    "rejected_by_teacher",
    "blocked_conflict_detected",
    "blocked_invalid_refinement",
    "blocked_unhandled_counterexamples",
    "blocked_forbidden_authority_detected",
    "rollback_applied",
}
ALLOWED_CONFIDENCE = {"low", "normal", "high", "blocked"}
ALLOWED_WORKING_READBACK_STATUSES = {
    "integrated_to_working_readback",
    "held_for_more_evidence",
    "blocked_invalid_reviewed_concept",
    "blocked_unhandled_counterexamples",
    "blocked_forbidden_memory_layer",
    "blocked_forbidden_authority_detected",
    "rollback_applied",
}
ALLOWED_HINT_KINDS = {
    "observe_before_retry",
    "avoid_repeated_failure",
    "verify_scope",
    "verify_expected_actual",
    "use_known_success_path",
    "goal_completion_hint",
    "no_progress_warning",
}
ALLOWED_ROLLBACK_STATUSES = {
    "rollback_record_created",
    "rollback_applied_to_withdraw_feedback_reviewed_concept",
    "rollback_applied_to_withdraw_working_readback_integration",
    "blocked_invalid_feedback_reviewed_concept",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_feedback_reviewed_concept_working_readback_integration",
    "passed_feedback_reviewed_concept_created_no_readback_seed",
    "held_for_more_evidence",
    "blocked_invalid_refinement",
    "blocked_invalid_teacher_gate",
    "blocked_invalid_reviewed_concept",
    "blocked_invalid_working_readback_integration",
    "blocked_missing_rollback",
    "blocked_core_memory_write_detected",
    "blocked_long_term_memory_write_detected",
    "blocked_archive_memory_write_detected",
    "blocked_anchor_write_detected",
    "blocked_automatic_learning_approval_detected",
    "blocked_action_authority_detected",
    "blocked_behavior_change_detected",
}
FORBIDDEN_MEMORY_LAYERS = {
    "core_memory",
    "long_term_memory",
    "archive_memory",
    "anchor_layer",
}


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


@dataclass(frozen=True)
class FeedbackRefinedConceptReviewedConceptGate:
    feedback_reviewed_concept_gate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_feedback_refinement_id: str
    source_feedback_review_id: str
    source_scope_check_id: str
    source_counterexample_check_id: str
    source_refinement_safety_audit_id: str
    source_learning_feedback_candidate_id: str | None
    source_task_closure_id: str | None
    source_outcome_evaluation_id: str | None
    source_sense_handoff_id: str | None
    source_sandbox_execution_id: str | None
    refined_concept_label: str
    refined_concept_scope: str
    refined_concept_candidate_kind: str
    refined_concept_confidence: str
    support_evidence_refs: tuple[str, ...]
    counterexample_refs: tuple[str, ...]
    counterexample_handling_notes: tuple[str, ...]
    teacher_gate_status: str
    teacher_gate_reason: str
    teacher_gate_text: str
    approval_actor: str
    approval_actor_role: str
    approval_source: str
    approved_for_feedback_reviewed_concept: bool
    approved_for_working_readback_integration: bool
    approved_for_core_memory_write: bool
    approved_for_long_term_memory_write: bool
    approved_for_archive_memory_write: bool
    approved_for_anchor_write: bool
    approved_for_automatic_learning_approval: bool
    approved_for_behavior_change: bool
    approved_for_action_authority: bool
    requires_working_readback_integration_audit: bool
    requires_memory_promotion_gate_later: bool
    requires_counterexample_monitoring: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != GATE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_feedback_refined_concept_reviewed_concept_gate_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.teacher_gate_status not in ALLOWED_GATE_STATUSES:
            raise ValueError(f"unknown teacher_gate_status: {self.teacher_gate_status}")
        if self.approval_source not in ALLOWED_APPROVAL_SOURCES:
            raise ValueError(f"unknown approval_source: {self.approval_source}")
        if self.approval_actor_role not in ALLOWED_APPROVAL_ACTOR_ROLES:
            raise ValueError(f"unknown approval_actor_role: {self.approval_actor_role}")
        for name in (
            "support_evidence_refs",
            "counterexample_refs",
            "counterexample_handling_notes",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FeedbackRefinedConceptReviewedConceptGate":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackDerivedReviewedConceptRecord:
    feedback_derived_reviewed_concept_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_feedback_reviewed_concept_gate_id: str
    source_feedback_refinement_id: str
    source_feedback_review_id: str
    source_scope_check_id: str
    source_counterexample_check_id: str
    source_learning_feedback_candidate_id: str | None
    source_task_closure_id: str | None
    source_outcome_evaluation_id: str | None
    source_sense_handoff_id: str | None
    source_sandbox_execution_id: str | None
    reviewed_concept_label: str
    reviewed_concept_scope: str
    reviewed_concept_kind: str
    reviewed_concept_summary: str
    reviewed_concept_reason: str
    support_evidence_refs: tuple[str, ...]
    counterexample_refs: tuple[str, ...]
    counterexample_handling_notes: tuple[str, ...]
    reviewed_concept_status: str
    reviewed_concept_confidence: str
    origin_type: str
    origin_task_closure_based: bool
    origin_feedback_derived: bool
    available_for_working_readback_integration: bool
    available_for_core_memory_write: bool
    available_for_long_term_memory_write: bool
    available_for_archive_memory_write: bool
    available_for_anchor_write: bool
    memory_write_performed: bool
    core_memory_write_performed: bool
    long_term_memory_write_performed: bool
    archive_memory_write_performed: bool
    anchor_write_performed: bool
    automatic_learning_approval_created: bool
    task_behavior_changed: bool
    action_authority_changed: bool
    rollback_available: bool
    rollback_record_id: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REVIEWED_CONCEPT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_feedback_derived_reviewed_concept_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.reviewed_concept_status not in ALLOWED_REVIEWED_CONCEPT_STATUSES:
            raise ValueError(
                f"unknown reviewed_concept_status: {self.reviewed_concept_status}"
            )
        if self.reviewed_concept_confidence not in ALLOWED_CONFIDENCE:
            raise ValueError(
                f"unknown reviewed_concept_confidence: {self.reviewed_concept_confidence}"
            )
        for name in (
            "support_evidence_refs",
            "counterexample_refs",
            "counterexample_handling_notes",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FeedbackDerivedReviewedConceptRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord:
    working_readback_integration_id: str
    schema_version: str
    created_at: str
    source_engine: str
    target_engine: str
    source_feedback_derived_reviewed_concept_id: str
    source_feedback_reviewed_concept_gate_id: str
    reviewed_concept_label: str
    reviewed_concept_scope: str
    reviewed_concept_kind: str
    memory_learning_trace_id: str | None
    memory_routing_trace_id: str | None
    memory_application_data_id: str | None
    task_working_memory_readback_hint_id: str | None
    working_readback_integration_status: str
    working_readback_integration_summary: str
    target_memory_layer: str
    available_for_future_task_working_memory_readback: bool
    created_memory_learning_trace: bool
    created_memory_routing_trace: bool
    created_memory_application_data: bool
    created_inactive_task_working_memory_readback_hint: bool
    core_memory_write_performed: bool
    long_term_memory_write_performed: bool
    archive_memory_write_performed: bool
    anchor_write_performed: bool
    automatic_learning_approval_created: bool
    task_behavior_changed: bool
    action_authority_changed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != WORKING_READBACK_INTEGRATION_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_feedback_reviewed_concept_working_readback_integration_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.target_engine != MEMORY_TARGET_ENGINE:
            raise ValueError("target_engine must be memory_engine")
        if self.working_readback_integration_status not in ALLOWED_WORKING_READBACK_STATUSES:
            raise ValueError(
                "unknown working_readback_integration_status: "
                f"{self.working_readback_integration_status}"
            )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackDerivedReviewedConceptReadbackSeedRecord:
    readback_seed_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_working_readback_integration_id: str
    source_feedback_derived_reviewed_concept_id: str
    reviewed_concept_label: str
    reviewed_concept_scope: str
    reviewed_concept_kind: str
    hint_label: str
    hint_kind: str
    hint_priority: int
    hint_summary: str
    task_handling_note: str
    scope_warning: str | None
    counterexample_warning: str | None
    advisory_only: bool
    single_task_lifetime: bool
    future_task_initialization_only: bool
    available_for_future_task_working_memory_hint_application: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_created: bool
    execution_created: bool
    task_behavior_changed: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READBACK_SEED_SCHEMA_VERSION:
            raise ValueError("schema_version must be task_engine_feedback_reviewed_concept_readback_seed_v0")
        if self.source_engine != TASK_SEED_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.hint_kind not in ALLOWED_HINT_KINDS:
            raise ValueError(f"unknown hint_kind: {self.hint_kind}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FeedbackDerivedReviewedConceptReadbackSeedRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackDerivedReviewedConceptRollbackRecord:
    feedback_reviewed_concept_rollback_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_feedback_derived_reviewed_concept_id: str | None
    source_working_readback_integration_id: str | None
    source_readback_seed_id: str | None
    reviewed_concept_created_before_rollback: bool
    reviewed_concept_available_after_rollback: bool
    working_readback_integrated_before_rollback: bool
    working_readback_available_after_rollback: bool
    rollback_available: bool
    rollback_applied: bool
    rollback_reason: str
    rollback_status: str
    rollback_summary: str
    core_memory_write_performed: bool
    long_term_memory_write_performed: bool
    archive_memory_write_performed: bool
    anchor_write_performed: bool
    automatic_learning_approval_created: bool
    task_behavior_changed: bool
    action_authority_changed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ROLLBACK_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_feedback_reviewed_concept_rollback_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.rollback_status not in ALLOWED_ROLLBACK_STATUSES:
            raise ValueError(f"unknown rollback_status: {self.rollback_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FeedbackDerivedReviewedConceptRollbackRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackDerivedReviewedConceptIntegrationSafetyAudit:
    feedback_reviewed_concept_integration_safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_feedback_reviewed_concept_gate_id: str | None
    source_feedback_derived_reviewed_concept_id: str | None
    source_working_readback_integration_id: str | None
    source_readback_seed_id: str | None
    source_rollback_id: str | None
    refinement_valid: bool
    scope_check_valid: bool
    counterexample_check_valid: bool
    teacher_gate_valid: bool
    feedback_reviewed_concept_valid: bool
    working_readback_integration_valid: bool
    readback_seed_valid: bool
    rollback_available: bool
    feedback_reviewed_concept_created: bool
    working_readback_integration_created: bool
    future_task_readback_available: bool
    working_readback_only_confirmed: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_automatic_learning_approval: bool
    no_candidate_ordering_change: bool
    no_selected_action_change: bool
    no_final_action_change: bool
    no_direct_command_creation: bool
    no_execution_creation: bool
    no_task_behavior_change: bool
    no_action_authority_change: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_feedback_reviewed_concept_integration_safety_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FeedbackDerivedReviewedConceptIntegrationSafetyAudit":
        return cls(**dict(data))


def build_feedback_refined_concept_reviewed_concept_gate(
    *,
    refinement: FeedbackConceptCandidateRefinementRecord | dict[str, object],
    review: FeedbackConceptCandidateReviewRecord | dict[str, object],
    scope_check: FeedbackConceptCandidateScopeCheckRecord | dict[str, object],
    counterexample_check: FeedbackConceptCandidateCounterexampleCheckRecord | dict[str, object],
    refinement_safety_audit: FeedbackConceptCandidateRefinementSafetyAudit | dict[str, object],
    teacher_gate_status: str = "approved_for_feedback_reviewed_concept_and_working_readback",
    teacher_gate_text: str = "Demo gate approves feedback ReviewedConcept and working readback only.",
    teacher_gate_reason: str | None = None,
    approval_actor: str = "system_demo",
    approval_actor_role: str = "system_demo",
    approval_source: str = "demo_review",
    created_at: str | None = None,
) -> FeedbackRefinedConceptReviewedConceptGate:
    refinement_record = _refinement_record(refinement)
    review_record = _review_record(review)
    scope_record = _scope_record(scope_check)
    counterexample_record = _counterexample_record(counterexample_check)
    audit_record = _refinement_audit_record(refinement_safety_audit)
    status = _gate_status(
        requested_status=teacher_gate_status,
        refinement=refinement_record,
        review=review_record,
        scope=scope_record,
        counterexample=counterexample_record,
        audit=audit_record,
    )
    approved = status == "approved_for_feedback_reviewed_concept_and_working_readback"
    return FeedbackRefinedConceptReviewedConceptGate(
        feedback_reviewed_concept_gate_id=(
            f"feedback_reviewed_concept_gate:{refinement_record.feedback_concept_candidate_refinement_id}"
        ),
        schema_version=GATE_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_feedback_refinement_id=refinement_record.feedback_concept_candidate_refinement_id,
        source_feedback_review_id=review_record.feedback_concept_candidate_review_id,
        source_scope_check_id=scope_record.scope_check_id,
        source_counterexample_check_id=counterexample_record.counterexample_check_id,
        source_refinement_safety_audit_id=(
            audit_record.feedback_concept_candidate_refinement_safety_audit_id
        ),
        source_learning_feedback_candidate_id=review_record.source_learning_feedback_candidate_id,
        source_task_closure_id=_find_ref("task_closure:", refinement_record.support_evidence_refs),
        source_outcome_evaluation_id=_find_ref(
            "task_outcome_evaluation:",
            refinement_record.support_evidence_refs,
        ),
        source_sense_handoff_id=_find_ref(
            "sense_sandbox_handoff:",
            refinement_record.support_evidence_refs,
        ),
        source_sandbox_execution_id=_find_ref(
            "sandbox_execution:",
            refinement_record.support_evidence_refs,
        ),
        refined_concept_label=refinement_record.refined_concept_label,
        refined_concept_scope=refinement_record.refined_concept_scope,
        refined_concept_candidate_kind=refinement_record.refined_concept_candidate_kind,
        refined_concept_confidence=(
            refinement_record.refined_concept_confidence if approved else "blocked"
        ),
        support_evidence_refs=refinement_record.support_evidence_refs,
        counterexample_refs=refinement_record.counterexample_refs,
        counterexample_handling_notes=refinement_record.counterexample_handling_notes,
        teacher_gate_status=status,
        teacher_gate_reason=teacher_gate_reason or _gate_reason(status),
        teacher_gate_text=teacher_gate_text,
        approval_actor=approval_actor,
        approval_actor_role=approval_actor_role,
        approval_source=approval_source,
        approved_for_feedback_reviewed_concept=approved,
        approved_for_working_readback_integration=approved,
        approved_for_core_memory_write=False,
        approved_for_long_term_memory_write=False,
        approved_for_archive_memory_write=False,
        approved_for_anchor_write=False,
        approved_for_automatic_learning_approval=False,
        approved_for_behavior_change=False,
        approved_for_action_authority=False,
        requires_working_readback_integration_audit=True,
        requires_memory_promotion_gate_later=True,
        requires_counterexample_monitoring=True,
        source_trace_refs=_combined_trace_refs(
            refinement_record.source_trace_refs,
            review_record.source_trace_refs,
            scope_record.source_trace_refs,
            counterexample_record.source_trace_refs,
            audit_record.source_trace_refs,
        ),
    )


def validate_feedback_refined_concept_reviewed_concept_gate(
    gate: FeedbackRefinedConceptReviewedConceptGate | dict[str, object],
) -> dict[str, object]:
    record = _gate_record(gate)
    errors: list[str] = []
    if not record.feedback_reviewed_concept_gate_id:
        errors.append("missing_feedback_reviewed_concept_gate_id")
    if record.approval_source == "explicit_teacher_review":
        if record.approval_actor_role not in {"teacher", "project_owner"}:
            errors.append("explicit_review_requires_teacher_or_project_owner")
        if not record.teacher_gate_text.strip():
            errors.append("explicit_review_requires_teacher_gate_text")
    elif record.approval_source == "demo_review":
        if record.approval_actor_role != "system_demo":
            errors.append("demo_review_requires_system_demo_role")
    else:
        errors.append("invalid_approval_source")
    approved = record.teacher_gate_status == "approved_for_feedback_reviewed_concept_and_working_readback"
    if record.approved_for_feedback_reviewed_concept != approved:
        errors.append("reviewed_concept_approval_flag_mismatch")
    if record.approved_for_working_readback_integration != approved:
        errors.append("working_readback_approval_flag_mismatch")
    if _gate_forbidden_authority(record):
        errors.append("forbidden_authority_detected")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "feedback_reviewed_concept_gate_id": record.feedback_reviewed_concept_gate_id,
        "teacher_gate_status": record.teacher_gate_status,
    }


def build_feedback_derived_reviewed_concept_record(
    *,
    gate: FeedbackRefinedConceptReviewedConceptGate | dict[str, object] | None,
    refinement: FeedbackConceptCandidateRefinementRecord | dict[str, object],
    review: FeedbackConceptCandidateReviewRecord | dict[str, object],
    scope_check: FeedbackConceptCandidateScopeCheckRecord | dict[str, object],
    counterexample_check: FeedbackConceptCandidateCounterexampleCheckRecord | dict[str, object],
    created_at: str | None = None,
) -> FeedbackDerivedReviewedConceptRecord:
    refinement_record = _refinement_record(refinement)
    review_record = _review_record(review)
    scope_record = _scope_record(scope_check)
    counterexample_record = _counterexample_record(counterexample_check)
    gate_record = _gate_record(gate) if gate is not None else None
    status = _reviewed_concept_status(gate_record, refinement_record)
    created = status == "feedback_reviewed_concept_created"
    return FeedbackDerivedReviewedConceptRecord(
        feedback_derived_reviewed_concept_id=(
            f"feedback_derived_reviewed_concept:{refinement_record.feedback_concept_candidate_refinement_id}"
        ),
        schema_version=REVIEWED_CONCEPT_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_feedback_reviewed_concept_gate_id=(
            gate_record.feedback_reviewed_concept_gate_id if gate_record else ""
        ),
        source_feedback_refinement_id=refinement_record.feedback_concept_candidate_refinement_id,
        source_feedback_review_id=review_record.feedback_concept_candidate_review_id,
        source_scope_check_id=scope_record.scope_check_id,
        source_counterexample_check_id=counterexample_record.counterexample_check_id,
        source_learning_feedback_candidate_id=review_record.source_learning_feedback_candidate_id,
        source_task_closure_id=_find_ref("task_closure:", refinement_record.support_evidence_refs),
        source_outcome_evaluation_id=_find_ref(
            "task_outcome_evaluation:",
            refinement_record.support_evidence_refs,
        ),
        source_sense_handoff_id=_find_ref(
            "sense_sandbox_handoff:",
            refinement_record.support_evidence_refs,
        ),
        source_sandbox_execution_id=_find_ref(
            "sandbox_execution:",
            refinement_record.support_evidence_refs,
        ),
        reviewed_concept_label=refinement_record.refined_concept_label,
        reviewed_concept_scope=refinement_record.refined_concept_scope,
        reviewed_concept_kind=refinement_record.refined_concept_candidate_kind,
        reviewed_concept_summary=_reviewed_concept_summary(status, refinement_record),
        reviewed_concept_reason=_reviewed_concept_reason(status),
        support_evidence_refs=refinement_record.support_evidence_refs,
        counterexample_refs=refinement_record.counterexample_refs,
        counterexample_handling_notes=refinement_record.counterexample_handling_notes,
        reviewed_concept_status=status,
        reviewed_concept_confidence=(
            refinement_record.refined_concept_confidence if created else "blocked"
        ),
        origin_type="feedback_task_closure",
        origin_task_closure_based=True,
        origin_feedback_derived=True,
        available_for_working_readback_integration=created,
        available_for_core_memory_write=False,
        available_for_long_term_memory_write=False,
        available_for_archive_memory_write=False,
        available_for_anchor_write=False,
        memory_write_performed=False,
        core_memory_write_performed=False,
        long_term_memory_write_performed=False,
        archive_memory_write_performed=False,
        anchor_write_performed=False,
        automatic_learning_approval_created=False,
        task_behavior_changed=False,
        action_authority_changed=False,
        rollback_available=created,
        rollback_record_id=None,
        source_trace_refs=_combined_trace_refs(
            refinement_record.source_trace_refs,
            review_record.source_trace_refs,
            scope_record.source_trace_refs,
            counterexample_record.source_trace_refs,
            gate_record.source_trace_refs if gate_record else (),
        ),
    )


def validate_feedback_derived_reviewed_concept_record(
    reviewed_concept: FeedbackDerivedReviewedConceptRecord | dict[str, object],
) -> dict[str, object]:
    record = _reviewed_concept_record(reviewed_concept)
    errors: list[str] = []
    if not record.feedback_derived_reviewed_concept_id:
        errors.append("missing_feedback_derived_reviewed_concept_id")
    if record.origin_type != "feedback_task_closure":
        errors.append("invalid_origin_type")
    if not record.origin_task_closure_based or not record.origin_feedback_derived:
        errors.append("origin_flags_not_feedback_task_closure")
    if record.reviewed_concept_status == "feedback_reviewed_concept_created":
        if not record.available_for_working_readback_integration:
            errors.append("created_concept_not_available_for_working_readback")
        if not record.rollback_available:
            errors.append("created_concept_missing_rollback")
    if (
        record.available_for_core_memory_write
        or record.available_for_long_term_memory_write
        or record.available_for_archive_memory_write
        or record.available_for_anchor_write
    ):
        errors.append("forbidden_memory_availability_detected")
    if _reviewed_concept_forbidden_authority(record):
        errors.append("forbidden_authority_detected")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "feedback_derived_reviewed_concept_id": record.feedback_derived_reviewed_concept_id,
        "reviewed_concept_status": record.reviewed_concept_status,
    }


def build_feedback_derived_reviewed_concept_working_readback_integration_record(
    *,
    reviewed_concept: FeedbackDerivedReviewedConceptRecord | dict[str, object],
    gate: FeedbackRefinedConceptReviewedConceptGate | dict[str, object] | None = None,
    target_memory_layer: str = WORKING_READBACK_LAYER,
    created_at: str | None = None,
) -> FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord:
    reviewed_record = _reviewed_concept_record(reviewed_concept)
    gate_record = _gate_record(gate) if gate is not None else None
    status = _working_readback_status(reviewed_record, target_memory_layer)
    integrated = status == "integrated_to_working_readback"
    integration_id = (
        f"feedback_reviewed_concept_working_readback:{reviewed_record.feedback_derived_reviewed_concept_id}"
    )
    return FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord(
        working_readback_integration_id=integration_id,
        schema_version=WORKING_READBACK_INTEGRATION_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        target_engine=MEMORY_TARGET_ENGINE,
        source_feedback_derived_reviewed_concept_id=(
            reviewed_record.feedback_derived_reviewed_concept_id
        ),
        source_feedback_reviewed_concept_gate_id=(
            gate_record.feedback_reviewed_concept_gate_id
            if gate_record
            else reviewed_record.source_feedback_reviewed_concept_gate_id
        ),
        reviewed_concept_label=reviewed_record.reviewed_concept_label,
        reviewed_concept_scope=reviewed_record.reviewed_concept_scope,
        reviewed_concept_kind=reviewed_record.reviewed_concept_kind,
        memory_learning_trace_id=(
            f"feedback_memory_learning_trace:{reviewed_record.feedback_derived_reviewed_concept_id}"
            if integrated
            else None
        ),
        memory_routing_trace_id=(
            f"feedback_memory_routing_trace:{reviewed_record.feedback_derived_reviewed_concept_id}"
            if integrated
            else None
        ),
        memory_application_data_id=(
            f"feedback_memory_application_data:{reviewed_record.feedback_derived_reviewed_concept_id}"
            if integrated
            else None
        ),
        task_working_memory_readback_hint_id=(
            f"feedback_task_working_memory_readback_hint:{reviewed_record.feedback_derived_reviewed_concept_id}"
            if integrated
            else None
        ),
        working_readback_integration_status=status,
        working_readback_integration_summary=_working_readback_summary(status),
        target_memory_layer=target_memory_layer,
        available_for_future_task_working_memory_readback=integrated,
        created_memory_learning_trace=integrated,
        created_memory_routing_trace=integrated,
        created_memory_application_data=integrated,
        created_inactive_task_working_memory_readback_hint=integrated,
        core_memory_write_performed=False,
        long_term_memory_write_performed=False,
        archive_memory_write_performed=False,
        anchor_write_performed=False,
        automatic_learning_approval_created=False,
        task_behavior_changed=False,
        action_authority_changed=False,
        source_trace_refs=reviewed_record.source_trace_refs,
    )


def validate_feedback_derived_reviewed_concept_working_readback_integration_record(
    integration: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord
    | dict[str, object],
) -> dict[str, object]:
    record = _integration_record(integration)
    errors: list[str] = []
    if not record.working_readback_integration_id:
        errors.append("missing_working_readback_integration_id")
    if record.target_memory_layer != WORKING_READBACK_LAYER:
        errors.append("forbidden_memory_layer")
    if record.working_readback_integration_status == "integrated_to_working_readback":
        if not record.available_for_future_task_working_memory_readback:
            errors.append("integrated_record_not_available_for_future_readback")
        if (
            not record.memory_learning_trace_id
            or not record.memory_routing_trace_id
            or not record.memory_application_data_id
            or not record.task_working_memory_readback_hint_id
        ):
            errors.append("missing_readback_compatible_ids")
    if _integration_forbidden_authority(record):
        errors.append("forbidden_authority_detected")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "working_readback_integration_id": record.working_readback_integration_id,
        "working_readback_integration_status": record.working_readback_integration_status,
    }


def map_feedback_reviewed_concept_to_readback_hint_seed(
    reviewed_concept: FeedbackDerivedReviewedConceptRecord | dict[str, object],
) -> tuple[str, int] | None:
    record = _reviewed_concept_record(reviewed_concept)
    if record.reviewed_concept_status != "feedback_reviewed_concept_created":
        return None
    if record.reviewed_concept_kind == "positive_affordance_concept_candidate":
        return ("use_known_success_path", 1)
    if record.reviewed_concept_kind == "negative_affordance_concept_candidate":
        return ("avoid_repeated_failure", 1)
    if record.reviewed_concept_kind == "goal_completion_concept_candidate":
        return ("goal_completion_hint", 1)
    if record.reviewed_concept_kind == "no_progress_concept_candidate":
        return ("no_progress_warning", 2)
    if record.reviewed_concept_kind == "observation_context_concept_candidate":
        return ("observe_before_retry", 0)
    return None


def build_feedback_derived_reviewed_concept_readback_seed_record(
    *,
    integration: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord
    | dict[str, object],
    reviewed_concept: FeedbackDerivedReviewedConceptRecord | dict[str, object],
    created_at: str | None = None,
) -> FeedbackDerivedReviewedConceptReadbackSeedRecord | None:
    integration_record = _integration_record(integration)
    reviewed_record = _reviewed_concept_record(reviewed_concept)
    mapping = map_feedback_reviewed_concept_to_readback_hint_seed(reviewed_record)
    if (
        mapping is None
        or integration_record.working_readback_integration_status
        != "integrated_to_working_readback"
    ):
        return None
    hint_kind, priority = mapping
    label = reviewed_record.reviewed_concept_label
    warning = (
        "counterexamples preserved; monitor before applying broadly"
        if reviewed_record.counterexample_refs
        else None
    )
    return FeedbackDerivedReviewedConceptReadbackSeedRecord(
        readback_seed_id=(
            f"feedback_reviewed_concept_readback_seed:{reviewed_record.feedback_derived_reviewed_concept_id}"
        ),
        schema_version=READBACK_SEED_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=TASK_SEED_ENGINE,
        source_working_readback_integration_id=integration_record.working_readback_integration_id,
        source_feedback_derived_reviewed_concept_id=(
            reviewed_record.feedback_derived_reviewed_concept_id
        ),
        reviewed_concept_label=label,
        reviewed_concept_scope=reviewed_record.reviewed_concept_scope,
        reviewed_concept_kind=reviewed_record.reviewed_concept_kind,
        hint_label=f"feedback_readback:{label}",
        hint_kind=hint_kind,
        hint_priority=priority,
        hint_summary=_hint_summary(hint_kind, label),
        task_handling_note=_task_handling_note(hint_kind, label),
        scope_warning=reviewed_record.reviewed_concept_scope,
        counterexample_warning=warning,
        advisory_only=True,
        single_task_lifetime=True,
        future_task_initialization_only=True,
        available_for_future_task_working_memory_hint_application=True,
        candidate_ordering_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_created=False,
        execution_created=False,
        task_behavior_changed=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_combined_trace_refs(
            reviewed_record.source_trace_refs,
            integration_record.source_trace_refs,
        ),
    )


def validate_feedback_derived_reviewed_concept_readback_seed_record(
    seed: FeedbackDerivedReviewedConceptReadbackSeedRecord | dict[str, object] | None,
) -> dict[str, object]:
    if seed is None:
        return {
            "valid": True,
            "error_codes": (),
            "readback_seed_id": None,
            "hint_kind": None,
        }
    record = _seed_record(seed)
    errors: list[str] = []
    if not record.readback_seed_id:
        errors.append("missing_readback_seed_id")
    if record.hint_kind not in ALLOWED_HINT_KINDS:
        errors.append("invalid_hint_kind")
    if not record.advisory_only:
        errors.append("seed_not_advisory_only")
    if not record.single_task_lifetime:
        errors.append("seed_not_single_task_lifetime")
    if not record.future_task_initialization_only:
        errors.append("seed_not_future_task_initialization_only")
    if _seed_forbidden_authority(record):
        errors.append("forbidden_authority_detected")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "readback_seed_id": record.readback_seed_id,
        "hint_kind": record.hint_kind,
    }


def build_feedback_derived_reviewed_concept_rollback_record(
    *,
    reviewed_concept: FeedbackDerivedReviewedConceptRecord | dict[str, object] | None,
    integration: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord
    | dict[str, object]
    | None,
    readback_seed: FeedbackDerivedReviewedConceptReadbackSeedRecord
    | dict[str, object]
    | None,
    rollback_applied: bool = False,
    rollback_reason: str = "Rollback data prepared for feedback ReviewedConcept integration.",
    created_at: str | None = None,
) -> FeedbackDerivedReviewedConceptRollbackRecord:
    reviewed_record = _reviewed_concept_record(reviewed_concept) if reviewed_concept else None
    integration_record = _integration_record(integration) if integration else None
    seed_record = _seed_record(readback_seed) if readback_seed else None
    created = (
        reviewed_record is not None
        and reviewed_record.reviewed_concept_status == "feedback_reviewed_concept_created"
    )
    integrated = (
        integration_record is not None
        and integration_record.working_readback_integration_status
        == "integrated_to_working_readback"
    )
    if _rollback_forbidden_authority(reviewed_record, integration_record, seed_record):
        status = "blocked_forbidden_authority_detected"
    elif not created and not integrated:
        status = "blocked_invalid_feedback_reviewed_concept"
    elif rollback_applied and integrated:
        status = "rollback_applied_to_withdraw_working_readback_integration"
    elif rollback_applied:
        status = "rollback_applied_to_withdraw_feedback_reviewed_concept"
    else:
        status = "rollback_record_created"
    return FeedbackDerivedReviewedConceptRollbackRecord(
        feedback_reviewed_concept_rollback_id=(
            f"feedback_reviewed_concept_rollback:{reviewed_record.feedback_derived_reviewed_concept_id}"
            if reviewed_record
            else "feedback_reviewed_concept_rollback:missing"
        ),
        schema_version=ROLLBACK_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_feedback_derived_reviewed_concept_id=(
            reviewed_record.feedback_derived_reviewed_concept_id if reviewed_record else None
        ),
        source_working_readback_integration_id=(
            integration_record.working_readback_integration_id if integration_record else None
        ),
        source_readback_seed_id=seed_record.readback_seed_id if seed_record else None,
        reviewed_concept_created_before_rollback=created,
        reviewed_concept_available_after_rollback=created and not rollback_applied,
        working_readback_integrated_before_rollback=integrated,
        working_readback_available_after_rollback=integrated and not rollback_applied,
        rollback_available=True,
        rollback_applied=rollback_applied,
        rollback_reason=rollback_reason,
        rollback_status=status,
        rollback_summary=_rollback_summary(status),
        core_memory_write_performed=False,
        long_term_memory_write_performed=False,
        archive_memory_write_performed=False,
        anchor_write_performed=False,
        automatic_learning_approval_created=False,
        task_behavior_changed=False,
        action_authority_changed=False,
        source_trace_refs=_combined_trace_refs(
            reviewed_record.source_trace_refs if reviewed_record else (),
            integration_record.source_trace_refs if integration_record else (),
            seed_record.source_trace_refs if seed_record else (),
        ),
    )


def apply_feedback_derived_reviewed_concept_rollback(
    rollback: FeedbackDerivedReviewedConceptRollbackRecord | dict[str, object],
) -> FeedbackDerivedReviewedConceptRollbackRecord:
    record = _rollback_record(rollback)
    if record.rollback_status.startswith("blocked_"):
        return record
    status = (
        "rollback_applied_to_withdraw_working_readback_integration"
        if record.working_readback_integrated_before_rollback
        else "rollback_applied_to_withdraw_feedback_reviewed_concept"
    )
    return replace(
        record,
        rollback_applied=True,
        rollback_status=status,
        reviewed_concept_available_after_rollback=False,
        working_readback_available_after_rollback=False,
        rollback_summary=_rollback_summary(status),
    )


def validate_feedback_derived_reviewed_concept_rollback_record(
    rollback: FeedbackDerivedReviewedConceptRollbackRecord | dict[str, object],
) -> dict[str, object]:
    record = _rollback_record(rollback)
    errors: list[str] = []
    if not record.feedback_reviewed_concept_rollback_id:
        errors.append("missing_feedback_reviewed_concept_rollback_id")
    if not record.rollback_available:
        errors.append("rollback_not_available")
    if _rollback_record_forbidden_authority(record):
        errors.append("forbidden_authority_detected")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "feedback_reviewed_concept_rollback_id": record.feedback_reviewed_concept_rollback_id,
        "rollback_status": record.rollback_status,
    }


def build_feedback_derived_reviewed_concept_integration_safety_audit(
    *,
    refinement: FeedbackConceptCandidateRefinementRecord | dict[str, object] | None,
    scope_check: FeedbackConceptCandidateScopeCheckRecord | dict[str, object] | None,
    counterexample_check: FeedbackConceptCandidateCounterexampleCheckRecord
    | dict[str, object]
    | None,
    gate: FeedbackRefinedConceptReviewedConceptGate | dict[str, object] | None,
    reviewed_concept: FeedbackDerivedReviewedConceptRecord | dict[str, object] | None,
    integration: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord
    | dict[str, object]
    | None,
    readback_seed: FeedbackDerivedReviewedConceptReadbackSeedRecord
    | dict[str, object]
    | None,
    rollback: FeedbackDerivedReviewedConceptRollbackRecord | dict[str, object] | None,
    created_at: str | None = None,
) -> FeedbackDerivedReviewedConceptIntegrationSafetyAudit:
    refinement_record = _refinement_record(refinement) if refinement else None
    scope_record = _scope_record(scope_check) if scope_check else None
    counterexample_record = _counterexample_record(counterexample_check) if counterexample_check else None
    gate_record = _gate_record(gate) if gate else None
    reviewed_record = _reviewed_concept_record(reviewed_concept) if reviewed_concept else None
    integration_record = _integration_record(integration) if integration else None
    seed_record = _seed_record(readback_seed) if readback_seed else None
    rollback_record = _rollback_record(rollback) if rollback else None
    reasons = _safety_blocked_reasons(
        refinement_record,
        scope_record,
        counterexample_record,
        gate_record,
        reviewed_record,
        integration_record,
        seed_record,
        rollback_record,
    )
    status = _safety_status(reasons, gate_record, reviewed_record, integration_record, seed_record)
    return FeedbackDerivedReviewedConceptIntegrationSafetyAudit(
        feedback_reviewed_concept_integration_safety_audit_id=_safety_audit_id(
            reviewed_record,
            integration_record,
        ),
        schema_version=SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_feedback_reviewed_concept_gate_id=(
            gate_record.feedback_reviewed_concept_gate_id if gate_record else None
        ),
        source_feedback_derived_reviewed_concept_id=(
            reviewed_record.feedback_derived_reviewed_concept_id if reviewed_record else None
        ),
        source_working_readback_integration_id=(
            integration_record.working_readback_integration_id if integration_record else None
        ),
        source_readback_seed_id=seed_record.readback_seed_id if seed_record else None,
        source_rollback_id=(
            rollback_record.feedback_reviewed_concept_rollback_id if rollback_record else None
        ),
        refinement_valid="invalid_refinement" not in reasons,
        scope_check_valid="invalid_scope" not in reasons,
        counterexample_check_valid="unhandled_counterexamples" not in reasons,
        teacher_gate_valid="invalid_teacher_gate" not in reasons,
        feedback_reviewed_concept_valid="invalid_reviewed_concept" not in reasons,
        working_readback_integration_valid="invalid_working_readback_integration"
        not in reasons,
        readback_seed_valid="invalid_readback_seed" not in reasons,
        rollback_available="missing_rollback" not in reasons,
        feedback_reviewed_concept_created=(
            reviewed_record is not None
            and reviewed_record.reviewed_concept_status == "feedback_reviewed_concept_created"
        ),
        working_readback_integration_created=(
            integration_record is not None
            and integration_record.working_readback_integration_status
            == "integrated_to_working_readback"
        ),
        future_task_readback_available=(
            integration_record is not None
            and integration_record.available_for_future_task_working_memory_readback
        ),
        working_readback_only_confirmed="forbidden_memory_layer" not in reasons,
        no_core_memory_write="core_memory_write" not in reasons,
        no_long_term_memory_write="long_term_memory_write" not in reasons,
        no_archive_memory_write="archive_memory_write" not in reasons,
        no_anchor_write="anchor_write" not in reasons,
        no_automatic_learning_approval="automatic_learning_approval" not in reasons,
        no_candidate_ordering_change="action_authority" not in reasons,
        no_selected_action_change="action_authority" not in reasons,
        no_final_action_change="action_authority" not in reasons,
        no_direct_command_creation="action_authority" not in reasons,
        no_execution_creation="action_authority" not in reasons,
        no_task_behavior_change="behavior_change" not in reasons,
        no_action_authority_change="action_authority" not in reasons,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(reasons),
        source_trace_refs=_combined_trace_refs(
            refinement_record.source_trace_refs if refinement_record else (),
            scope_record.source_trace_refs if scope_record else (),
            counterexample_record.source_trace_refs if counterexample_record else (),
            gate_record.source_trace_refs if gate_record else (),
            reviewed_record.source_trace_refs if reviewed_record else (),
            integration_record.source_trace_refs if integration_record else (),
            seed_record.source_trace_refs if seed_record else (),
            rollback_record.source_trace_refs if rollback_record else (),
        ),
    )


def validate_feedback_derived_reviewed_concept_integration_safety_audit(
    audit: FeedbackDerivedReviewedConceptIntegrationSafetyAudit | dict[str, object],
) -> dict[str, object]:
    record = _safety_audit_record(audit)
    errors: list[str] = []
    if not record.feedback_reviewed_concept_integration_safety_audit_id:
        errors.append("missing_feedback_reviewed_concept_integration_safety_audit_id")
    if record.audit_status.startswith("passed_") and record.blocked_reasons:
        errors.append("passing_audit_has_blocked_reasons")
    if not record.working_readback_only_confirmed:
        errors.append("working_readback_only_not_confirmed")
    if (
        not record.no_core_memory_write
        or not record.no_long_term_memory_write
        or not record.no_archive_memory_write
        or not record.no_anchor_write
        or not record.no_automatic_learning_approval
        or not record.no_action_authority_change
        or not record.no_task_behavior_change
    ):
        errors.append("forbidden_authority_detected")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "feedback_reviewed_concept_integration_safety_audit_id": (
            record.feedback_reviewed_concept_integration_safety_audit_id
        ),
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_demo_positive_affordance_feedback_reviewed_concept_integration() -> dict[str, object]:
    return _build_demo_bundle(build_demo_successful_expected_effect_refinement())


def build_demo_negative_affordance_feedback_reviewed_concept_integration() -> dict[str, object]:
    return _build_demo_bundle(build_demo_failed_expected_effect_refinement())


def build_demo_goal_completion_feedback_reviewed_concept_integration() -> dict[str, object]:
    return _build_demo_bundle(build_demo_goal_reached_refinement())


def build_demo_no_progress_feedback_reviewed_concept_integration() -> dict[str, object]:
    return _build_demo_bundle(build_demo_no_progress_refinement())


def build_demo_observation_context_feedback_reviewed_concept_integration() -> dict[str, object]:
    return _build_demo_bundle(build_demo_observation_only_refinement())


def build_demo_unknown_held_feedback_reviewed_concept_integration() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_unknown_outcome_held_refinement(),
        teacher_gate_status="held_for_more_evidence",
        create_rollback=False,
    )


def build_demo_system_fault_held_feedback_reviewed_concept_integration() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_system_fault_blocked_refinement(),
        teacher_gate_status="conflict_detected",
        create_rollback=False,
    )


def build_demo_blocked_invalid_refinement_feedback_reviewed_concept() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_blocked_invalid_concept_candidate_draft_refinement(),
        create_rollback=False,
    )


def build_demo_blocked_invalid_refinement_audit_feedback_reviewed_concept() -> dict[str, object]:
    payload = build_demo_successful_expected_effect_refinement()
    audit = FeedbackConceptCandidateRefinementSafetyAudit.from_dict(
        payload["feedback_concept_candidate_refinement_safety_audit"]
    )
    payload["feedback_concept_candidate_refinement_safety_audit"] = replace(
        audit,
        audit_status="blocked_invalid_refinement",
        blocked_reasons=("invalid_refinement",),
    ).to_dict()
    return _build_demo_bundle(payload, create_rollback=False)


def build_demo_blocked_missing_teacher_gate_feedback_reviewed_concept() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_successful_expected_effect_refinement(),
        missing_gate=True,
        create_rollback=False,
    )


def build_demo_blocked_teacher_rejected_feedback_reviewed_concept() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_successful_expected_effect_refinement(),
        teacher_gate_status="rejected",
        create_rollback=False,
    )


def build_demo_blocked_unhandled_counterexamples_feedback_reviewed_concept() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_blocked_unhandled_counterexample_refinement(),
        create_rollback=False,
    )


def build_demo_blocked_target_core_memory_feedback_reviewed_concept() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_successful_expected_effect_refinement(),
        target_memory_layer="core_memory",
        create_rollback=False,
    )


def build_demo_blocked_target_long_term_memory_feedback_reviewed_concept() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_successful_expected_effect_refinement(),
        target_memory_layer="long_term_memory",
        create_rollback=False,
    )


def build_demo_blocked_target_archive_memory_feedback_reviewed_concept() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_successful_expected_effect_refinement(),
        target_memory_layer="archive_memory",
        create_rollback=False,
    )


def build_demo_blocked_target_anchor_feedback_reviewed_concept() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_successful_expected_effect_refinement(),
        target_memory_layer="anchor_layer",
        create_rollback=False,
    )


def build_demo_blocked_automatic_learning_approval_feedback_reviewed_concept() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_successful_expected_effect_refinement(),
        mutate_reviewed={"automatic_learning_approval_created": True},
    )


def build_demo_blocked_action_authority_feedback_reviewed_concept() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_successful_expected_effect_refinement(),
        mutate_reviewed={"action_authority_changed": True},
    )


def build_demo_blocked_behavior_change_feedback_reviewed_concept() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_successful_expected_effect_refinement(),
        mutate_reviewed={"task_behavior_changed": True},
    )


def build_demo_blocked_missing_rollback_feedback_reviewed_concept() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_successful_expected_effect_refinement(),
        create_rollback=False,
    )


def build_demo_feedback_reviewed_concept_integration_case(case: str) -> dict[str, object]:
    cases = {
        "positive-affordance": build_demo_positive_affordance_feedback_reviewed_concept_integration,
        "negative-affordance": build_demo_negative_affordance_feedback_reviewed_concept_integration,
        "goal-completion": build_demo_goal_completion_feedback_reviewed_concept_integration,
        "no-progress": build_demo_no_progress_feedback_reviewed_concept_integration,
        "observation-context": build_demo_observation_context_feedback_reviewed_concept_integration,
        "unknown-held": build_demo_unknown_held_feedback_reviewed_concept_integration,
        "system-fault-held": build_demo_system_fault_held_feedback_reviewed_concept_integration,
    }
    if case not in cases:
        raise ValueError(f"unknown demo case: {case}")
    return cases[case]()


def build_demo_blocked_feedback_reviewed_concept_integration(case: str) -> dict[str, object]:
    cases = {
        "invalid-refinement": build_demo_blocked_invalid_refinement_feedback_reviewed_concept,
        "invalid-refinement-audit": build_demo_blocked_invalid_refinement_audit_feedback_reviewed_concept,
        "missing-teacher-gate": build_demo_blocked_missing_teacher_gate_feedback_reviewed_concept,
        "teacher-rejected": build_demo_blocked_teacher_rejected_feedback_reviewed_concept,
        "unhandled-counterexamples": build_demo_blocked_unhandled_counterexamples_feedback_reviewed_concept,
        "target-core-memory": build_demo_blocked_target_core_memory_feedback_reviewed_concept,
        "target-long-term-memory": build_demo_blocked_target_long_term_memory_feedback_reviewed_concept,
        "target-archive-memory": build_demo_blocked_target_archive_memory_feedback_reviewed_concept,
        "target-anchor": build_demo_blocked_target_anchor_feedback_reviewed_concept,
        "automatic-learning-approval": build_demo_blocked_automatic_learning_approval_feedback_reviewed_concept,
        "action-authority-detected": build_demo_blocked_action_authority_feedback_reviewed_concept,
        "behavior-change-detected": build_demo_blocked_behavior_change_feedback_reviewed_concept,
        "missing-rollback": build_demo_blocked_missing_rollback_feedback_reviewed_concept,
    }
    if case not in cases:
        raise ValueError(f"unknown blocked demo case: {case}")
    return cases[case]()


def _build_demo_bundle(
    package91_payload: dict[str, object],
    *,
    teacher_gate_status: str = "approved_for_feedback_reviewed_concept_and_working_readback",
    target_memory_layer: str = WORKING_READBACK_LAYER,
    missing_gate: bool = False,
    create_rollback: bool = True,
    mutate_reviewed: dict[str, object] | None = None,
) -> dict[str, object]:
    refinement_record = _refinement_record(
        package91_payload["feedback_concept_candidate_refinement"]
    )
    review_record = _review_record(package91_payload["feedback_concept_candidate_review"])
    scope_record = _scope_record(package91_payload["feedback_concept_candidate_scope_check"])
    counterexample_record = _counterexample_record(
        package91_payload["feedback_concept_candidate_counterexample_check"]
    )
    p91_audit_record = _refinement_audit_record(
        package91_payload["feedback_concept_candidate_refinement_safety_audit"]
    )
    gate = None
    if not missing_gate:
        gate = build_feedback_refined_concept_reviewed_concept_gate(
            refinement=refinement_record,
            review=review_record,
            scope_check=scope_record,
            counterexample_check=counterexample_record,
            refinement_safety_audit=p91_audit_record,
            teacher_gate_status=teacher_gate_status,
        )
    reviewed = build_feedback_derived_reviewed_concept_record(
        gate=gate,
        refinement=refinement_record,
        review=review_record,
        scope_check=scope_record,
        counterexample_check=counterexample_record,
    )
    if mutate_reviewed:
        reviewed = replace(reviewed, **mutate_reviewed)
    integration = build_feedback_derived_reviewed_concept_working_readback_integration_record(
        reviewed_concept=reviewed,
        gate=gate,
        target_memory_layer=target_memory_layer,
    )
    readback_seed = build_feedback_derived_reviewed_concept_readback_seed_record(
        integration=integration,
        reviewed_concept=reviewed,
    )
    rollback = None
    if create_rollback:
        rollback = build_feedback_derived_reviewed_concept_rollback_record(
            reviewed_concept=reviewed,
            integration=integration,
            readback_seed=readback_seed,
        )
    audit = build_feedback_derived_reviewed_concept_integration_safety_audit(
        refinement=refinement_record,
        scope_check=scope_record,
        counterexample_check=counterexample_record,
        gate=gate,
        reviewed_concept=reviewed,
        integration=integration,
        readback_seed=readback_seed,
        rollback=rollback,
    )
    payload = dict(package91_payload)
    payload.update(
        {
            "feedback_reviewed_concept_gate": gate.to_dict() if gate else None,
            "feedback_derived_reviewed_concept": reviewed.to_dict(),
            "feedback_derived_reviewed_concept_working_readback_integration": (
                integration.to_dict()
            ),
            "feedback_derived_reviewed_concept_readback_seed": (
                readback_seed.to_dict() if readback_seed else None
            ),
            "feedback_derived_reviewed_concept_rollback": (
                rollback.to_dict() if rollback else None
            ),
            "feedback_derived_reviewed_concept_integration_safety_audit": (
                audit.to_dict()
            ),
        }
    )
    return payload


def _gate_status(
    *,
    requested_status: str,
    refinement: FeedbackConceptCandidateRefinementRecord,
    review: FeedbackConceptCandidateReviewRecord,
    scope: FeedbackConceptCandidateScopeCheckRecord,
    counterexample: FeedbackConceptCandidateCounterexampleCheckRecord,
    audit: FeedbackConceptCandidateRefinementSafetyAudit,
) -> str:
    if _refinement_forbidden_authority(refinement) or _review_forbidden_authority(review):
        return "blocked_forbidden_authority_detected"
    if not validate_feedback_concept_candidate_refinement_record(refinement)["valid"]:
        return "blocked_invalid_refinement"
    if not validate_feedback_concept_candidate_review_record(review)["valid"]:
        return "blocked_invalid_refinement"
    if not validate_feedback_concept_candidate_scope_check_record(scope)["valid"]:
        return "blocked_invalid_scope"
    if not validate_feedback_concept_candidate_counterexample_check_record(counterexample)[
        "valid"
    ]:
        return "blocked_unhandled_counterexamples"
    if refinement.refinement_status != "refined_concept_candidate_created":
        if refinement.refinement_status == "held_for_more_evidence":
            return "held_for_more_evidence"
        if refinement.refinement_status == "rejected_by_review":
            return "rejected"
        if refinement.refinement_status == "conflict_detected":
            return "conflict_detected"
        if refinement.refinement_status == "blocked_invalid_scope":
            return "blocked_invalid_scope"
        if refinement.refinement_status == "blocked_unhandled_counterexamples":
            return "blocked_unhandled_counterexamples"
        return "blocked_invalid_refinement"
    if not validate_feedback_concept_candidate_refinement_safety_audit(audit)["valid"]:
        return "blocked_invalid_refinement"
    if audit.audit_status not in PASSING_REFINEMENT_AUDIT_STATUSES:
        if audit.audit_status == "blocked_invalid_scope_check":
            return "blocked_invalid_scope"
        if audit.audit_status == "blocked_invalid_counterexample_check":
            return "blocked_unhandled_counterexamples"
        return "blocked_invalid_refinement"
    return requested_status


def _reviewed_concept_status(
    gate: FeedbackRefinedConceptReviewedConceptGate | None,
    refinement: FeedbackConceptCandidateRefinementRecord,
) -> str:
    if gate is None or not validate_feedback_refined_concept_reviewed_concept_gate(gate)["valid"]:
        return "blocked_invalid_refinement"
    if _gate_forbidden_authority(gate) or _refinement_forbidden_authority(refinement):
        return "blocked_forbidden_authority_detected"
    if gate.teacher_gate_status == "approved_for_feedback_reviewed_concept_and_working_readback":
        return "feedback_reviewed_concept_created"
    if gate.teacher_gate_status == "held_for_more_evidence":
        return "held_for_more_evidence"
    if gate.teacher_gate_status == "rejected":
        return "rejected_by_teacher"
    if gate.teacher_gate_status == "conflict_detected":
        return "blocked_conflict_detected"
    if gate.teacher_gate_status == "blocked_unhandled_counterexamples":
        return "blocked_unhandled_counterexamples"
    return "blocked_invalid_refinement"


def _working_readback_status(
    reviewed_concept: FeedbackDerivedReviewedConceptRecord,
    target_memory_layer: str,
) -> str:
    if target_memory_layer != WORKING_READBACK_LAYER:
        return "blocked_forbidden_memory_layer"
    if _reviewed_concept_forbidden_authority(reviewed_concept):
        return "blocked_forbidden_authority_detected"
    if reviewed_concept.reviewed_concept_status == "feedback_reviewed_concept_created":
        return "integrated_to_working_readback"
    if reviewed_concept.reviewed_concept_status == "held_for_more_evidence":
        return "held_for_more_evidence"
    if reviewed_concept.reviewed_concept_status == "blocked_unhandled_counterexamples":
        return "blocked_unhandled_counterexamples"
    return "blocked_invalid_reviewed_concept"


def _safety_blocked_reasons(
    refinement: FeedbackConceptCandidateRefinementRecord | None,
    scope: FeedbackConceptCandidateScopeCheckRecord | None,
    counterexample: FeedbackConceptCandidateCounterexampleCheckRecord | None,
    gate: FeedbackRefinedConceptReviewedConceptGate | None,
    reviewed: FeedbackDerivedReviewedConceptRecord | None,
    integration: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord | None,
    seed: FeedbackDerivedReviewedConceptReadbackSeedRecord | None,
    rollback: FeedbackDerivedReviewedConceptRollbackRecord | None,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if refinement is None or not validate_feedback_concept_candidate_refinement_record(refinement)["valid"]:
        reasons.append("invalid_refinement")
    elif refinement.refinement_status in {
        "blocked_invalid_review",
        "blocked_invalid_scope",
        "split_recommended",
    }:
        reasons.append("invalid_refinement")
    elif refinement.refinement_status == "blocked_unhandled_counterexamples":
        reasons.append("unhandled_counterexamples")
    if scope is None or not validate_feedback_concept_candidate_scope_check_record(scope)["valid"]:
        reasons.append("invalid_scope")
    if (
        counterexample is None
        or not validate_feedback_concept_candidate_counterexample_check_record(counterexample)[
            "valid"
        ]
    ):
        reasons.append("unhandled_counterexamples")
    if gate is None or not validate_feedback_refined_concept_reviewed_concept_gate(gate)["valid"]:
        reasons.append("invalid_teacher_gate")
    elif gate.teacher_gate_status.startswith("blocked_"):
        if gate.teacher_gate_status == "blocked_unhandled_counterexamples":
            reasons.append("unhandled_counterexamples")
        elif gate.teacher_gate_status in {
            "blocked_invalid_scope",
            "blocked_invalid_refinement",
        }:
            reasons.append("invalid_refinement")
        elif gate.teacher_gate_status == "blocked_forbidden_authority_detected":
            reasons.append("action_authority")
        else:
            reasons.append("invalid_teacher_gate")
    if reviewed is None or not validate_feedback_derived_reviewed_concept_record(reviewed)[
        "valid"
    ]:
        reasons.append("invalid_reviewed_concept")
    elif reviewed.reviewed_concept_status.startswith("blocked_"):
        if reviewed.reviewed_concept_status == "blocked_unhandled_counterexamples":
            reasons.append("unhandled_counterexamples")
        else:
            reasons.append("invalid_reviewed_concept")
    if integration is None:
        reasons.append("invalid_working_readback_integration")
    elif integration.working_readback_integration_status == "blocked_forbidden_memory_layer":
        reasons.append("forbidden_memory_layer")
    elif not validate_feedback_derived_reviewed_concept_working_readback_integration_record(
        integration
    )["valid"]:
        reasons.append("invalid_working_readback_integration")
    seed_validation = validate_feedback_derived_reviewed_concept_readback_seed_record(seed)
    if not seed_validation["valid"]:
        reasons.append("invalid_readback_seed")
    successful = (
        reviewed is not None
        and reviewed.reviewed_concept_status == "feedback_reviewed_concept_created"
        and integration is not None
        and integration.working_readback_integration_status == "integrated_to_working_readback"
    )
    if successful and rollback is None:
        reasons.append("missing_rollback")
    elif rollback is not None and not validate_feedback_derived_reviewed_concept_rollback_record(
        rollback
    )["valid"]:
        reasons.append("missing_rollback")
    for item in (reviewed, integration, seed, rollback):
        if item is None:
            continue
        if getattr(item, "core_memory_write_performed", False):
            reasons.append("core_memory_write")
        if getattr(item, "long_term_memory_write_performed", False):
            reasons.append("long_term_memory_write")
        if getattr(item, "archive_memory_write_performed", False):
            reasons.append("archive_memory_write")
        if getattr(item, "anchor_write_performed", False):
            reasons.append("anchor_write")
        if getattr(item, "memory_write_performed", False):
            reasons.append("core_memory_write")
        if getattr(item, "automatic_learning_approval_created", False):
            reasons.append("automatic_learning_approval")
        if getattr(item, "action_authority_changed", False):
            reasons.append("action_authority")
        if getattr(item, "candidate_ordering_changed", False):
            reasons.append("action_authority")
        if getattr(item, "selected_action_changed", False):
            reasons.append("action_authority")
        if getattr(item, "final_action_changed", False):
            reasons.append("action_authority")
        if getattr(item, "direct_command_created", False):
            reasons.append("action_authority")
        if getattr(item, "execution_created", False):
            reasons.append("action_authority")
        if getattr(item, "task_behavior_changed", False):
            reasons.append("behavior_change")
    return tuple(dict.fromkeys(reasons))


def _safety_status(
    reasons: tuple[str, ...],
    gate: FeedbackRefinedConceptReviewedConceptGate | None,
    reviewed: FeedbackDerivedReviewedConceptRecord | None,
    integration: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord | None,
    seed: FeedbackDerivedReviewedConceptReadbackSeedRecord | None,
) -> str:
    if "core_memory_write" in reasons:
        return "blocked_core_memory_write_detected"
    if "long_term_memory_write" in reasons:
        return "blocked_long_term_memory_write_detected"
    if "archive_memory_write" in reasons:
        return "blocked_archive_memory_write_detected"
    if "anchor_write" in reasons:
        return "blocked_anchor_write_detected"
    if "automatic_learning_approval" in reasons:
        return "blocked_automatic_learning_approval_detected"
    if "action_authority" in reasons:
        return "blocked_action_authority_detected"
    if "behavior_change" in reasons:
        return "blocked_behavior_change_detected"
    if "missing_rollback" in reasons:
        return "blocked_missing_rollback"
    if "invalid_teacher_gate" in reasons:
        return "blocked_invalid_teacher_gate"
    if "unhandled_counterexamples" in reasons:
        return "blocked_invalid_refinement"
    if "invalid_refinement" in reasons or "invalid_scope" in reasons:
        return "blocked_invalid_refinement"
    if "forbidden_memory_layer" in reasons or "invalid_working_readback_integration" in reasons:
        return "blocked_invalid_working_readback_integration"
    if "invalid_reviewed_concept" in reasons:
        return "blocked_invalid_reviewed_concept"
    if gate and gate.teacher_gate_status == "held_for_more_evidence":
        return "held_for_more_evidence"
    if reviewed and reviewed.reviewed_concept_status == "held_for_more_evidence":
        return "held_for_more_evidence"
    if (
        reviewed
        and reviewed.reviewed_concept_status == "feedback_reviewed_concept_created"
        and integration
        and integration.working_readback_integration_status == "integrated_to_working_readback"
    ):
        if seed is None:
            return "passed_feedback_reviewed_concept_created_no_readback_seed"
        return "passed_feedback_reviewed_concept_working_readback_integration"
    return "blocked_invalid_reviewed_concept"


def _gate_reason(status: str) -> str:
    if status == "approved_for_feedback_reviewed_concept_and_working_readback":
        return "Teacher gate approved feedback ReviewedConcept and working readback only."
    if status == "held_for_more_evidence":
        return "More feedback evidence is required before ReviewedConcept creation."
    if status == "rejected":
        return "Teacher gate rejected feedback ReviewedConcept creation."
    if status == "conflict_detected":
        return "Conflict detected; no feedback ReviewedConcept may be created."
    return "Input refinement cannot be promoted into feedback ReviewedConcept integration."


def _reviewed_concept_summary(
    status: str,
    refinement: FeedbackConceptCandidateRefinementRecord,
) -> str:
    if status == "feedback_reviewed_concept_created":
        return f"Feedback-derived ReviewedConcept {refinement.refined_concept_label} created."
    return f"Feedback-derived ReviewedConcept status {status}; no memory-layer write."


def _reviewed_concept_reason(status: str) -> str:
    if status == "feedback_reviewed_concept_created":
        return "Safe Package 91 refinement and explicit Package 92 gate passed."
    return "Package 92 gate did not permit feedback ReviewedConcept creation."


def _working_readback_summary(status: str) -> str:
    if status == "integrated_to_working_readback":
        return "Feedback-derived ReviewedConcept integrated to working_readback only."
    if status == "blocked_forbidden_memory_layer":
        return "Integration blocked because target memory layer is forbidden."
    if status == "held_for_more_evidence":
        return "Integration held for more evidence."
    return f"Working readback integration status {status}."


def _hint_summary(kind: str, label: str) -> str:
    return f"{kind} seed prepared from feedback ReviewedConcept {label}."


def _task_handling_note(kind: str, label: str) -> str:
    if kind == "avoid_repeated_failure":
        return f"Avoid repeating a failed pattern associated with {label}."
    if kind == "observe_before_retry":
        return f"Observe before retrying in the scope of {label}."
    if kind == "goal_completion_hint":
        return f"Prefer the known goal-completion context for {label}."
    if kind == "no_progress_warning":
        return f"Treat {label} as a no-progress warning."
    return f"Use {label} as advisory working-readback context only."


def _rollback_summary(status: str) -> str:
    if status == "rollback_record_created":
        return "Rollback can withdraw feedback ReviewedConcept and working readback availability."
    if status == "rollback_applied_to_withdraw_working_readback_integration":
        return "Rollback withdrew working readback integration availability."
    if status == "rollback_applied_to_withdraw_feedback_reviewed_concept":
        return "Rollback withdrew feedback ReviewedConcept availability."
    return "Rollback blocked."


def _find_ref(prefix: str, refs: tuple[str, ...]) -> str | None:
    for ref in refs:
        if ref.startswith(prefix):
            return ref
    return None


def _safety_audit_id(
    reviewed: FeedbackDerivedReviewedConceptRecord | None,
    integration: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord | None,
) -> str:
    if reviewed:
        return (
            "feedback_reviewed_concept_integration_safety_audit:"
            + reviewed.feedback_derived_reviewed_concept_id.replace(":", "_")
        )
    if integration:
        return (
            "feedback_reviewed_concept_integration_safety_audit:"
            + integration.working_readback_integration_id.replace(":", "_")
        )
    return "feedback_reviewed_concept_integration_safety_audit:missing"


def _gate_forbidden_authority(record: FeedbackRefinedConceptReviewedConceptGate) -> bool:
    return (
        record.approved_for_core_memory_write
        or record.approved_for_long_term_memory_write
        or record.approved_for_archive_memory_write
        or record.approved_for_anchor_write
        or record.approved_for_automatic_learning_approval
        or record.approved_for_behavior_change
        or record.approved_for_action_authority
    )


def _review_forbidden_authority(record: FeedbackConceptCandidateReviewRecord) -> bool:
    return (
        record.approved_for_reviewed_concept
        or record.approved_for_memory_write
        or record.approved_for_behavior_change
        or record.approved_for_action_authority
        or record.approved_for_automatic_learning_approval
        or record.reviewed_concept_created
        or record.memory_write_performed
        or record.automatic_learning_approval_created
        or record.task_behavior_changed
        or record.candidate_ordering_changed
        or record.selected_action_changed
        or record.final_action_changed
        or record.direct_command_created
        or record.execution_created
    )


def _refinement_forbidden_authority(record: FeedbackConceptCandidateRefinementRecord) -> bool:
    return (
        record.reviewed_concept_created
        or record.memory_write_performed
        or record.automatic_learning_approval_created
        or record.task_behavior_changed
        or record.candidate_ordering_changed
        or record.selected_action_changed
        or record.final_action_changed
        or record.direct_command_created
        or record.execution_created
    )


def _reviewed_concept_forbidden_authority(
    record: FeedbackDerivedReviewedConceptRecord,
) -> bool:
    return (
        record.available_for_core_memory_write
        or record.available_for_long_term_memory_write
        or record.available_for_archive_memory_write
        or record.available_for_anchor_write
        or record.memory_write_performed
        or record.core_memory_write_performed
        or record.long_term_memory_write_performed
        or record.archive_memory_write_performed
        or record.anchor_write_performed
        or record.automatic_learning_approval_created
        or record.task_behavior_changed
        or record.action_authority_changed
    )


def _integration_forbidden_authority(
    record: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord,
) -> bool:
    return (
        record.core_memory_write_performed
        or record.long_term_memory_write_performed
        or record.archive_memory_write_performed
        or record.anchor_write_performed
        or record.automatic_learning_approval_created
        or record.task_behavior_changed
        or record.action_authority_changed
    )


def _seed_forbidden_authority(
    record: FeedbackDerivedReviewedConceptReadbackSeedRecord,
) -> bool:
    return (
        record.candidate_ordering_changed
        or record.selected_action_changed
        or record.final_action_changed
        or record.direct_command_created
        or record.execution_created
        or record.task_behavior_changed
        or record.memory_write_performed
        or record.automatic_learning_approval_created
    )


def _rollback_record_forbidden_authority(
    record: FeedbackDerivedReviewedConceptRollbackRecord,
) -> bool:
    return (
        record.core_memory_write_performed
        or record.long_term_memory_write_performed
        or record.archive_memory_write_performed
        or record.anchor_write_performed
        or record.automatic_learning_approval_created
        or record.task_behavior_changed
        or record.action_authority_changed
    )


def _rollback_forbidden_authority(
    reviewed: FeedbackDerivedReviewedConceptRecord | None,
    integration: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord | None,
    seed: FeedbackDerivedReviewedConceptReadbackSeedRecord | None,
) -> bool:
    return (
        (reviewed is not None and _reviewed_concept_forbidden_authority(reviewed))
        or (integration is not None and _integration_forbidden_authority(integration))
        or (seed is not None and _seed_forbidden_authority(seed))
    )


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    refs: list[str] = []
    for group in groups:
        for ref in group:
            if ref and ref not in refs:
                refs.append(ref)
    return tuple(refs)


def _refinement_record(
    refinement: FeedbackConceptCandidateRefinementRecord | dict[str, object],
) -> FeedbackConceptCandidateRefinementRecord:
    return (
        refinement
        if isinstance(refinement, FeedbackConceptCandidateRefinementRecord)
        else FeedbackConceptCandidateRefinementRecord.from_dict(dict(refinement))
    )


def _review_record(
    review: FeedbackConceptCandidateReviewRecord | dict[str, object],
) -> FeedbackConceptCandidateReviewRecord:
    return (
        review
        if isinstance(review, FeedbackConceptCandidateReviewRecord)
        else FeedbackConceptCandidateReviewRecord.from_dict(dict(review))
    )


def _scope_record(
    scope: FeedbackConceptCandidateScopeCheckRecord | dict[str, object],
) -> FeedbackConceptCandidateScopeCheckRecord:
    return (
        scope
        if isinstance(scope, FeedbackConceptCandidateScopeCheckRecord)
        else FeedbackConceptCandidateScopeCheckRecord.from_dict(dict(scope))
    )


def _counterexample_record(
    counterexample: FeedbackConceptCandidateCounterexampleCheckRecord | dict[str, object],
) -> FeedbackConceptCandidateCounterexampleCheckRecord:
    return (
        counterexample
        if isinstance(counterexample, FeedbackConceptCandidateCounterexampleCheckRecord)
        else FeedbackConceptCandidateCounterexampleCheckRecord.from_dict(dict(counterexample))
    )


def _refinement_audit_record(
    audit: FeedbackConceptCandidateRefinementSafetyAudit | dict[str, object],
) -> FeedbackConceptCandidateRefinementSafetyAudit:
    return (
        audit
        if isinstance(audit, FeedbackConceptCandidateRefinementSafetyAudit)
        else FeedbackConceptCandidateRefinementSafetyAudit.from_dict(dict(audit))
    )


def _gate_record(
    gate: FeedbackRefinedConceptReviewedConceptGate | dict[str, object],
) -> FeedbackRefinedConceptReviewedConceptGate:
    return (
        gate
        if isinstance(gate, FeedbackRefinedConceptReviewedConceptGate)
        else FeedbackRefinedConceptReviewedConceptGate.from_dict(dict(gate))
    )


def _reviewed_concept_record(
    reviewed_concept: FeedbackDerivedReviewedConceptRecord | dict[str, object],
) -> FeedbackDerivedReviewedConceptRecord:
    return (
        reviewed_concept
        if isinstance(reviewed_concept, FeedbackDerivedReviewedConceptRecord)
        else FeedbackDerivedReviewedConceptRecord.from_dict(dict(reviewed_concept))
    )


def _integration_record(
    integration: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord
    | dict[str, object],
) -> FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord:
    return (
        integration
        if isinstance(integration, FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord)
        else FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord.from_dict(
            dict(integration)
        )
    )


def _seed_record(
    seed: FeedbackDerivedReviewedConceptReadbackSeedRecord | dict[str, object],
) -> FeedbackDerivedReviewedConceptReadbackSeedRecord:
    return (
        seed
        if isinstance(seed, FeedbackDerivedReviewedConceptReadbackSeedRecord)
        else FeedbackDerivedReviewedConceptReadbackSeedRecord.from_dict(dict(seed))
    )


def _rollback_record(
    rollback: FeedbackDerivedReviewedConceptRollbackRecord | dict[str, object],
) -> FeedbackDerivedReviewedConceptRollbackRecord:
    return (
        rollback
        if isinstance(rollback, FeedbackDerivedReviewedConceptRollbackRecord)
        else FeedbackDerivedReviewedConceptRollbackRecord.from_dict(dict(rollback))
    )


def _safety_audit_record(
    audit: FeedbackDerivedReviewedConceptIntegrationSafetyAudit | dict[str, object],
) -> FeedbackDerivedReviewedConceptIntegrationSafetyAudit:
    return (
        audit
        if isinstance(audit, FeedbackDerivedReviewedConceptIntegrationSafetyAudit)
        else FeedbackDerivedReviewedConceptIntegrationSafetyAudit.from_dict(dict(audit))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
