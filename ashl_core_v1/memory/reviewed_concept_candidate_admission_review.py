"""Admit ReviewedConcept memory candidates into working-readback trace records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.reviewed_concept_memory_trace_bridge import (
    ReviewedConceptMemoryApplicationDataCandidate,
    ReviewedConceptMemoryLearningTraceCandidate,
    ReviewedConceptMemoryRoutingTraceCandidate,
    ReviewedConceptMemoryTraceBridgeAudit,
    build_demo_blocked_forbidden_memory_write_bridge,
    build_demo_blocked_forbidden_target_layer_bridge,
    build_demo_blocked_from_routing_bridge,
    build_demo_held_for_more_evidence_bridge,
    build_demo_reviewed_concept_memory_trace_bridge,
    validate_reviewed_concept_memory_application_data_candidate,
    validate_reviewed_concept_memory_learning_trace_candidate,
    validate_reviewed_concept_memory_routing_trace_candidate,
    validate_reviewed_concept_memory_trace_bridge_audit,
)


SOURCE_ENGINE = "memory_engine"
ADMISSION_REVIEW_SCHEMA_VERSION = "memory_engine_reviewed_concept_admission_review_v0"
MEMORY_LEARNING_TRACE_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_memory_learning_trace_v0"
)
MEMORY_ROUTING_TRACE_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_memory_routing_trace_v0"
)
MEMORY_APPLICATION_DATA_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_memory_application_data_v0"
)
ADMISSION_SAFETY_AUDIT_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_admission_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Memory Engine can review ReviewedConcept memory candidate "
    "records and admit valid ones as actual MemoryLearningTrace, "
    "MemoryRoutingTrace, and MemoryApplicationData records for future "
    "working-readback preview, without writing Core/Long-term/Archive/Anchor "
    "memory layers, creating readback hints, mutating Working Memory, or "
    "changing task behavior."
)
BLOCKED_CLAIMS = (
    "no_core_longterm_archive_anchor_write",
    "no_readback_hint",
    "no_working_memory_mutation",
    "no_task_behavior_change",
    "no_automatic_learning_approval",
    "no_concept_promotion",
)

ALLOWED_ADMISSION_STATUSES = {
    "admitted_for_working_readback_trace_only",
    "held_for_more_evidence",
    "blocked_invalid_candidates",
    "blocked_bridge_audit_failed",
    "blocked_forbidden_target_layer",
    "blocked_unhandled_counterexamples",
    "blocked_invalid_scope",
    "blocked_forbidden_authority_detected",
}
ALLOWED_ADMITTED_TARGET_LAYERS = {
    "working_readback",
    "held_for_more_evidence",
    "blocked",
}
ALLOWED_TRACE_STATUSES = {
    "trace_created_for_working_readback",
    "held_for_more_evidence",
    "blocked",
}
ALLOWED_ROUTING_TARGET_LAYERS = {
    "working_readback",
    "held_for_more_evidence",
    "blocked",
}
ALLOWED_ROUTING_STATUSES = {
    "routed_to_working_readback_trace",
    "held_for_more_evidence",
    "blocked_from_routing",
}
ALLOWED_APPLICATION_KINDS = {
    "working_memory_hint_material",
    "held_for_more_evidence",
    "blocked",
}
ALLOWED_APPLICATION_STATUSES = {
    "application_data_created_for_working_readback",
    "held_for_more_evidence",
    "blocked",
}
ALLOWED_SAFETY_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_admission_review",
    "blocked_invalid_memory_learning_trace",
    "blocked_invalid_memory_routing_trace",
    "blocked_invalid_memory_application_data",
    "blocked_forbidden_memory_layer_write_detected",
    "blocked_forbidden_readback_detected",
    "blocked_forbidden_behavior_change_detected",
}
HANDLED_COUNTEREXAMPLE_STATUSES = {
    "no_counterexamples",
    "scope_narrowed",
    "split_required",
    "candidate_invalidated",
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
class ReviewedConceptMemoryAdmissionReviewRecord:
    admission_review_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_learning_trace_candidate_id: str
    source_routing_trace_candidate_id: str
    source_application_data_candidate_id: str
    source_bridge_audit_id: str
    concept_label: str
    concept_summary: str
    candidate_lineage_valid: bool
    bridge_audit_passed: bool
    support_evidence_present: bool
    counterexample_handling_valid: bool
    scope_valid: bool
    target_layer_allowed: bool
    admission_status: str
    admission_summary: str
    admitted_for_memory_trace: bool
    admitted_for_routing_trace: bool
    admitted_for_application_data: bool
    admitted_target_layer: str
    requires_teacher_review_before_memory_layer_write: bool
    requires_counterexample_monitoring: bool
    requires_more_support_before_promotion: bool
    memory_layer_write_performed: bool
    core_memory_write_performed: bool
    long_term_memory_write_performed: bool
    archive_memory_write_performed: bool
    anchor_write_performed: bool
    readback_hint_created: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ADMISSION_REVIEW_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_admission_review_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.admission_status not in ALLOWED_ADMISSION_STATUSES:
            raise ValueError(f"unknown admission_status: {self.admission_status}")
        if self.admitted_target_layer not in ALLOWED_ADMITTED_TARGET_LAYERS:
            raise ValueError(
                f"unknown admitted_target_layer: {self.admitted_target_layer}"
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
    ) -> "ReviewedConceptMemoryAdmissionReviewRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptMemoryLearningTrace:
    memory_learning_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_admission_review_id: str
    source_reviewed_concept_id: str
    source_learning_trace_candidate_id: str
    concept_label: str
    concept_summary: str
    source_task_ids: tuple[str, ...]
    source_case_ids: tuple[str, ...]
    source_state_action_outcome_refs: tuple[str, ...]
    support_evidence_refs: tuple[str, ...]
    counterexample_evidence_refs: tuple[str, ...]
    scope_text: str
    generalization_level: str
    counterexample_handling_status: str
    trace_status: str
    trace_summary: str
    memory_layer_write_performed: bool
    task_behavior_changed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_LEARNING_TRACE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_memory_learning_trace_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.trace_status not in ALLOWED_TRACE_STATUSES:
            raise ValueError(f"unknown trace_status: {self.trace_status}")
        for name in (
            "source_task_ids",
            "source_case_ids",
            "source_state_action_outcome_refs",
            "support_evidence_refs",
            "counterexample_evidence_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptMemoryLearningTrace":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptMemoryRoutingTrace:
    memory_routing_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_admission_review_id: str
    source_reviewed_concept_id: str
    source_memory_learning_trace_id: str
    source_routing_trace_candidate_id: str
    target_layer: str
    routing_status: str
    routing_reason: str
    allowed_for_working_readback: bool
    allowed_for_memory_layer_write: bool
    allowed_for_core_memory: bool
    allowed_for_long_term_memory: bool
    allowed_for_archive_memory: bool
    allowed_for_anchor_layer: bool
    requires_teacher_review_before_memory_layer_write: bool
    requires_counterexample_monitoring: bool
    requires_more_support_before_promotion: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_ROUTING_TRACE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_memory_routing_trace_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.target_layer not in ALLOWED_ROUTING_TARGET_LAYERS:
            raise ValueError(f"unknown target_layer: {self.target_layer}")
        if self.routing_status not in ALLOWED_ROUTING_STATUSES:
            raise ValueError(f"unknown routing_status: {self.routing_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptMemoryRoutingTrace":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptMemoryApplicationData:
    memory_application_data_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_admission_review_id: str
    source_reviewed_concept_id: str
    source_memory_learning_trace_id: str
    source_memory_routing_trace_id: str
    source_application_data_candidate_id: str
    concept_label: str
    application_summary: str
    application_kind: str
    working_memory_hint_label_candidates: tuple[str, ...]
    task_handling_note_candidates: tuple[str, ...]
    application_status: str
    available_for_future_readback_preview: bool
    actual_readback_hint_created: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_APPLICATION_DATA_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_memory_application_data_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.application_kind not in ALLOWED_APPLICATION_KINDS:
            raise ValueError(f"unknown application_kind: {self.application_kind}")
        if self.application_status not in ALLOWED_APPLICATION_STATUSES:
            raise ValueError(f"unknown application_status: {self.application_status}")
        for name in (
            "working_memory_hint_label_candidates",
            "task_handling_note_candidates",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptMemoryApplicationData":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptMemoryAdmissionSafetyAudit:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_admission_review_id: str | None
    source_reviewed_concept_id: str
    source_memory_learning_trace_id: str | None
    source_memory_routing_trace_id: str | None
    source_memory_application_data_id: str | None
    admission_review_valid: bool
    memory_learning_trace_valid: bool
    memory_routing_trace_valid: bool
    memory_application_data_valid: bool
    no_memory_layer_write: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_readback_hint_created: bool
    no_working_memory_mutation: bool
    no_task_behavior_change: bool
    no_automatic_learning_approval: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ADMISSION_SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_admission_safety_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.audit_status not in ALLOWED_SAFETY_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptMemoryAdmissionSafetyAudit":
        return cls(**dict(data))


def build_reviewed_concept_memory_admission_review(
    *,
    memory_learning_trace_candidate: ReviewedConceptMemoryLearningTraceCandidate
    | dict[str, object],
    memory_routing_trace_candidate: ReviewedConceptMemoryRoutingTraceCandidate
    | dict[str, object],
    memory_application_data_candidate: ReviewedConceptMemoryApplicationDataCandidate
    | dict[str, object],
    bridge_audit: ReviewedConceptMemoryTraceBridgeAudit | dict[str, object],
) -> ReviewedConceptMemoryAdmissionReviewRecord:
    learning = _learning_candidate(memory_learning_trace_candidate)
    routing = _routing_candidate(memory_routing_trace_candidate)
    application = _application_candidate(memory_application_data_candidate)
    audit = _bridge_audit(bridge_audit)
    lineage_valid = _candidate_lineage_valid(learning, routing, application, audit)
    bridge_passed = audit.audit_status == "passed"
    support_present = bool(learning.support_evidence_refs)
    counterexamples_valid = _counterexample_handling_valid(learning)
    scope_valid = _scope_valid(learning)
    target_allowed = _target_layer_allowed(routing)
    status = _admission_status(
        learning=learning,
        routing=routing,
        application=application,
        audit=audit,
        lineage_valid=lineage_valid,
        bridge_passed=bridge_passed,
        support_present=support_present,
        counterexamples_valid=counterexamples_valid,
        scope_valid=scope_valid,
        target_allowed=target_allowed,
    )
    target = _admitted_target_layer(status, routing)
    admitted = status == "admitted_for_working_readback_trace_only"
    return ReviewedConceptMemoryAdmissionReviewRecord(
        admission_review_id=f"reviewed_concept_memory_admission_review:{learning.source_reviewed_concept_id}",
        schema_version=ADMISSION_REVIEW_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=learning.source_reviewed_concept_id,
        source_learning_trace_candidate_id=learning.memory_learning_trace_candidate_id,
        source_routing_trace_candidate_id=routing.memory_routing_trace_candidate_id,
        source_application_data_candidate_id=application.memory_application_data_candidate_id,
        source_bridge_audit_id=audit.bridge_audit_id,
        concept_label=learning.concept_label,
        concept_summary=learning.concept_summary,
        candidate_lineage_valid=lineage_valid,
        bridge_audit_passed=bridge_passed,
        support_evidence_present=support_present,
        counterexample_handling_valid=counterexamples_valid,
        scope_valid=scope_valid,
        target_layer_allowed=target_allowed,
        admission_status=status,
        admission_summary=_admission_summary(status, target),
        admitted_for_memory_trace=admitted,
        admitted_for_routing_trace=admitted,
        admitted_for_application_data=admitted,
        admitted_target_layer=target,
        requires_teacher_review_before_memory_layer_write=True,
        requires_counterexample_monitoring=True,
        requires_more_support_before_promotion=True,
        memory_layer_write_performed=False,
        core_memory_write_performed=False,
        long_term_memory_write_performed=False,
        archive_memory_write_performed=False,
        anchor_write_performed=False,
        readback_hint_created=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_combined_trace_refs(
            learning.source_trace_refs,
            routing.source_trace_refs,
            application.source_trace_refs,
            audit.source_trace_refs,
        ),
    )


def validate_reviewed_concept_memory_admission_review(
    review: ReviewedConceptMemoryAdmissionReviewRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _admission_review(review)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_admission_review:{error}"]}
    errors: list[str] = []
    if record.admission_status.startswith("blocked_"):
        errors.append(record.admission_status)
    if not record.source_reviewed_concept_id:
        errors.append("missing_reviewed_concept_id")
    if not record.source_learning_trace_candidate_id:
        errors.append("missing_learning_trace_candidate_id")
    if not record.source_routing_trace_candidate_id:
        errors.append("missing_routing_trace_candidate_id")
    if not record.source_application_data_candidate_id:
        errors.append("missing_application_data_candidate_id")
    if not record.candidate_lineage_valid:
        errors.append("candidate_lineage_invalid")
    if record.admission_status == "admitted_for_working_readback_trace_only":
        if not (
            record.bridge_audit_passed
            and record.support_evidence_present
            and record.counterexample_handling_valid
            and record.scope_valid
            and record.target_layer_allowed
        ):
            errors.append("admitted_but_gate_false")
        if record.admitted_target_layer != "working_readback":
            errors.append("admitted_target_not_working_readback")
        if not (
            record.admitted_for_memory_trace
            and record.admitted_for_routing_trace
            and record.admitted_for_application_data
        ):
            errors.append("admitted_flags_false")
    for flag in (
        "requires_teacher_review_before_memory_layer_write",
        "requires_counterexample_monitoring",
        "requires_more_support_before_promotion",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    for flag in (
        "memory_layer_write_performed",
        "core_memory_write_performed",
        "long_term_memory_write_performed",
        "archive_memory_write_performed",
        "anchor_write_performed",
        "readback_hint_created",
        "working_memory_mutated",
        "task_behavior_changed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "admission_review_id": record.admission_review_id,
        "admission_status": record.admission_status,
        "admitted_target_layer": record.admitted_target_layer,
        "memory_layer_write_performed": record.memory_layer_write_performed,
        "readback_hint_created": record.readback_hint_created,
        "working_memory_mutated": record.working_memory_mutated,
        "task_behavior_changed": record.task_behavior_changed,
    }


def build_reviewed_concept_memory_learning_trace(
    *,
    admission_review: ReviewedConceptMemoryAdmissionReviewRecord | dict[str, object],
    memory_learning_trace_candidate: ReviewedConceptMemoryLearningTraceCandidate
    | dict[str, object],
) -> ReviewedConceptMemoryLearningTrace:
    review = _admission_review(admission_review)
    candidate = _learning_candidate(memory_learning_trace_candidate)
    status = _trace_status(review)
    return ReviewedConceptMemoryLearningTrace(
        memory_learning_trace_id=f"reviewed_concept_memory_learning_trace:{review.source_reviewed_concept_id}",
        schema_version=MEMORY_LEARNING_TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_admission_review_id=review.admission_review_id,
        source_reviewed_concept_id=review.source_reviewed_concept_id,
        source_learning_trace_candidate_id=candidate.memory_learning_trace_candidate_id,
        concept_label=candidate.concept_label,
        concept_summary=candidate.concept_summary,
        source_task_ids=candidate.source_task_ids,
        source_case_ids=candidate.source_case_ids,
        source_state_action_outcome_refs=candidate.source_state_action_outcome_refs,
        support_evidence_refs=candidate.support_evidence_refs,
        counterexample_evidence_refs=candidate.counterexample_evidence_refs,
        scope_text=candidate.scope_text,
        generalization_level=candidate.generalization_level,
        counterexample_handling_status=candidate.counterexample_handling_status,
        trace_status=status,
        trace_summary=_trace_summary(status),
        memory_layer_write_performed=False,
        task_behavior_changed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_combined_trace_refs(
            review.source_trace_refs,
            candidate.source_trace_refs,
        ),
    )


def validate_reviewed_concept_memory_learning_trace(
    trace: ReviewedConceptMemoryLearningTrace | dict[str, object],
) -> dict[str, object]:
    try:
        record = _memory_learning_trace(trace)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_memory_learning_trace:{error}"]}
    errors: list[str] = []
    if not record.source_admission_review_id:
        errors.append("missing_admission_review_id")
    if record.trace_status == "trace_created_for_working_readback":
        if not record.support_evidence_refs:
            errors.append("missing_support_evidence_refs")
    for flag in (
        "memory_layer_write_performed",
        "task_behavior_changed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "memory_learning_trace_id": record.memory_learning_trace_id,
        "trace_status": record.trace_status,
        "memory_layer_write_performed": record.memory_layer_write_performed,
    }


def build_reviewed_concept_memory_routing_trace(
    *,
    admission_review: ReviewedConceptMemoryAdmissionReviewRecord | dict[str, object],
    memory_learning_trace: ReviewedConceptMemoryLearningTrace | dict[str, object],
    memory_routing_trace_candidate: ReviewedConceptMemoryRoutingTraceCandidate
    | dict[str, object],
) -> ReviewedConceptMemoryRoutingTrace:
    review = _admission_review(admission_review)
    learning_trace = _memory_learning_trace(memory_learning_trace)
    candidate = _routing_candidate(memory_routing_trace_candidate)
    target, status = _routing_target_and_status(review)
    return ReviewedConceptMemoryRoutingTrace(
        memory_routing_trace_id=f"reviewed_concept_memory_routing_trace:{review.source_reviewed_concept_id}",
        schema_version=MEMORY_ROUTING_TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_admission_review_id=review.admission_review_id,
        source_reviewed_concept_id=review.source_reviewed_concept_id,
        source_memory_learning_trace_id=learning_trace.memory_learning_trace_id,
        source_routing_trace_candidate_id=candidate.memory_routing_trace_candidate_id,
        target_layer=target,
        routing_status=status,
        routing_reason=candidate.routing_reason,
        allowed_for_working_readback=target == "working_readback",
        allowed_for_memory_layer_write=False,
        allowed_for_core_memory=False,
        allowed_for_long_term_memory=False,
        allowed_for_archive_memory=False,
        allowed_for_anchor_layer=False,
        requires_teacher_review_before_memory_layer_write=True,
        requires_counterexample_monitoring=True,
        requires_more_support_before_promotion=True,
        memory_layer_write_performed=False,
        source_trace_refs=_combined_trace_refs(
            review.source_trace_refs,
            learning_trace.source_trace_refs,
            candidate.source_trace_refs,
        ),
    )


def validate_reviewed_concept_memory_routing_trace(
    trace: ReviewedConceptMemoryRoutingTrace | dict[str, object],
) -> dict[str, object]:
    try:
        record = _memory_routing_trace(trace)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_memory_routing_trace:{error}"]}
    errors: list[str] = []
    if not record.source_memory_learning_trace_id:
        errors.append("missing_memory_learning_trace_id")
    if record.target_layer == "working_readback" and not record.allowed_for_working_readback:
        errors.append("working_readback_not_allowed")
    for flag in (
        "allowed_for_memory_layer_write",
        "allowed_for_core_memory",
        "allowed_for_long_term_memory",
        "allowed_for_archive_memory",
        "allowed_for_anchor_layer",
        "memory_layer_write_performed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    for flag in (
        "requires_teacher_review_before_memory_layer_write",
        "requires_counterexample_monitoring",
        "requires_more_support_before_promotion",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "memory_routing_trace_id": record.memory_routing_trace_id,
        "target_layer": record.target_layer,
        "routing_status": record.routing_status,
        "allowed_for_memory_layer_write": record.allowed_for_memory_layer_write,
    }


def build_reviewed_concept_memory_application_data(
    *,
    admission_review: ReviewedConceptMemoryAdmissionReviewRecord | dict[str, object],
    memory_learning_trace: ReviewedConceptMemoryLearningTrace | dict[str, object],
    memory_routing_trace: ReviewedConceptMemoryRoutingTrace | dict[str, object],
    memory_application_data_candidate: ReviewedConceptMemoryApplicationDataCandidate
    | dict[str, object],
) -> ReviewedConceptMemoryApplicationData:
    review = _admission_review(admission_review)
    learning_trace = _memory_learning_trace(memory_learning_trace)
    routing_trace = _memory_routing_trace(memory_routing_trace)
    candidate = _application_candidate(memory_application_data_candidate)
    kind, status = _application_kind_and_status(review)
    return ReviewedConceptMemoryApplicationData(
        memory_application_data_id=f"reviewed_concept_memory_application_data:{review.source_reviewed_concept_id}",
        schema_version=MEMORY_APPLICATION_DATA_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_admission_review_id=review.admission_review_id,
        source_reviewed_concept_id=review.source_reviewed_concept_id,
        source_memory_learning_trace_id=learning_trace.memory_learning_trace_id,
        source_memory_routing_trace_id=routing_trace.memory_routing_trace_id,
        source_application_data_candidate_id=candidate.memory_application_data_candidate_id,
        concept_label=candidate.concept_label,
        application_summary=candidate.application_summary,
        application_kind=kind,
        working_memory_hint_label_candidates=(
            candidate.suggested_working_memory_hint_labels
            if kind == "working_memory_hint_material"
            else ()
        ),
        task_handling_note_candidates=(
            candidate.suggested_task_handling_notes
            if kind == "working_memory_hint_material"
            else ()
        ),
        application_status=status,
        available_for_future_readback_preview=(
            status == "application_data_created_for_working_readback"
        ),
        actual_readback_hint_created=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        memory_layer_write_performed=False,
        source_trace_refs=_combined_trace_refs(
            review.source_trace_refs,
            learning_trace.source_trace_refs,
            routing_trace.source_trace_refs,
            candidate.source_trace_refs,
        ),
    )


def validate_reviewed_concept_memory_application_data(
    data: ReviewedConceptMemoryApplicationData | dict[str, object],
) -> dict[str, object]:
    try:
        record = _memory_application_data(data)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_memory_application_data:{error}"]}
    errors: list[str] = []
    expected_available = (
        record.application_status == "application_data_created_for_working_readback"
    )
    if record.available_for_future_readback_preview is not expected_available:
        errors.append("available_for_future_readback_preview_mismatch")
    if (
        record.application_status == "application_data_created_for_working_readback"
        and not record.working_memory_hint_label_candidates
    ):
        errors.append("missing_working_memory_hint_label_candidates")
    for flag in (
        "actual_readback_hint_created",
        "working_memory_mutated",
        "task_behavior_changed",
        "memory_layer_write_performed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "memory_application_data_id": record.memory_application_data_id,
        "application_status": record.application_status,
        "available_for_future_readback_preview": (
            record.available_for_future_readback_preview
        ),
        "actual_readback_hint_created": record.actual_readback_hint_created,
        "working_memory_mutated": record.working_memory_mutated,
        "task_behavior_changed": record.task_behavior_changed,
    }


def build_reviewed_concept_memory_admission_safety_audit(
    *,
    admission_review: ReviewedConceptMemoryAdmissionReviewRecord | dict[str, object],
    memory_learning_trace: ReviewedConceptMemoryLearningTrace | dict[str, object],
    memory_routing_trace: ReviewedConceptMemoryRoutingTrace | dict[str, object],
    memory_application_data: ReviewedConceptMemoryApplicationData | dict[str, object],
) -> ReviewedConceptMemoryAdmissionSafetyAudit:
    review = _admission_review(admission_review)
    learning_trace = _memory_learning_trace(memory_learning_trace)
    routing_trace = _memory_routing_trace(memory_routing_trace)
    application_data = _memory_application_data(memory_application_data)
    admission_valid = bool(validate_reviewed_concept_memory_admission_review(review)["valid"])
    learning_valid = bool(
        validate_reviewed_concept_memory_learning_trace(learning_trace)["valid"]
    )
    routing_valid = bool(
        validate_reviewed_concept_memory_routing_trace(routing_trace)["valid"]
    )
    application_valid = bool(
        validate_reviewed_concept_memory_application_data(application_data)["valid"]
    )
    no_memory_layer_write = (
        review.memory_layer_write_performed is False
        and learning_trace.memory_layer_write_performed is False
        and routing_trace.memory_layer_write_performed is False
        and application_data.memory_layer_write_performed is False
    )
    no_core_memory_write = review.core_memory_write_performed is False
    no_long_term_memory_write = review.long_term_memory_write_performed is False
    no_archive_memory_write = review.archive_memory_write_performed is False
    no_anchor_write = review.anchor_write_performed is False
    no_readback_hint_created = (
        review.readback_hint_created is False
        and application_data.actual_readback_hint_created is False
    )
    no_working_memory_mutation = (
        review.working_memory_mutated is False
        and application_data.working_memory_mutated is False
    )
    no_task_behavior_change = (
        review.task_behavior_changed is False
        and learning_trace.task_behavior_changed is False
        and application_data.task_behavior_changed is False
    )
    no_automatic_learning_approval = (
        review.automatic_learning_approval_created is False
        and learning_trace.automatic_learning_approval_created is False
    )
    blocked_reasons = _safety_blocked_reasons(
        admission_review_valid=admission_valid,
        memory_learning_trace_valid=learning_valid,
        memory_routing_trace_valid=routing_valid,
        memory_application_data_valid=application_valid,
        no_memory_layer_write=no_memory_layer_write,
        no_core_memory_write=no_core_memory_write,
        no_long_term_memory_write=no_long_term_memory_write,
        no_archive_memory_write=no_archive_memory_write,
        no_anchor_write=no_anchor_write,
        no_readback_hint_created=no_readback_hint_created,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_automatic_learning_approval=no_automatic_learning_approval,
    )
    return ReviewedConceptMemoryAdmissionSafetyAudit(
        safety_audit_id=f"reviewed_concept_memory_admission_safety_audit:{review.source_reviewed_concept_id}",
        schema_version=ADMISSION_SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_admission_review_id=review.admission_review_id,
        source_reviewed_concept_id=review.source_reviewed_concept_id,
        source_memory_learning_trace_id=learning_trace.memory_learning_trace_id,
        source_memory_routing_trace_id=routing_trace.memory_routing_trace_id,
        source_memory_application_data_id=application_data.memory_application_data_id,
        admission_review_valid=admission_valid,
        memory_learning_trace_valid=learning_valid,
        memory_routing_trace_valid=routing_valid,
        memory_application_data_valid=application_valid,
        no_memory_layer_write=no_memory_layer_write,
        no_core_memory_write=no_core_memory_write,
        no_long_term_memory_write=no_long_term_memory_write,
        no_archive_memory_write=no_archive_memory_write,
        no_anchor_write=no_anchor_write,
        no_readback_hint_created=no_readback_hint_created,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_automatic_learning_approval=no_automatic_learning_approval,
        audit_status=_safety_audit_status(blocked_reasons),
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=blocked_reasons,
    )


def validate_reviewed_concept_memory_admission_safety_audit(
    audit: ReviewedConceptMemoryAdmissionSafetyAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _admission_safety_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_admission_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed":
        errors.append(record.audit_status)
    for flag in (
        "admission_review_valid",
        "memory_learning_trace_valid",
        "memory_routing_trace_valid",
        "memory_application_data_valid",
        "no_memory_layer_write",
        "no_core_memory_write",
        "no_long_term_memory_write",
        "no_archive_memory_write",
        "no_anchor_write",
        "no_readback_hint_created",
        "no_working_memory_mutation",
        "no_task_behavior_change",
        "no_automatic_learning_approval",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    if not set(BLOCKED_CLAIMS).issubset(set(record.blocked_claims)):
        errors.append("blocked_claims_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "safety_audit_id": record.safety_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_reviewed_concept_memory_admission(
    bridge_payload: dict[str, object],
) -> dict[str, object]:
    learning = _learning_candidate(bridge_payload["memory_learning_trace_candidate"])
    routing = _routing_candidate(bridge_payload["memory_routing_trace_candidate"])
    application = _application_candidate(bridge_payload["memory_application_data_candidate"])
    bridge_audit = _bridge_audit(bridge_payload["bridge_audit"])
    admission_review = build_reviewed_concept_memory_admission_review(
        memory_learning_trace_candidate=learning,
        memory_routing_trace_candidate=routing,
        memory_application_data_candidate=application,
        bridge_audit=bridge_audit,
    )
    memory_learning_trace = build_reviewed_concept_memory_learning_trace(
        admission_review=admission_review,
        memory_learning_trace_candidate=learning,
    )
    memory_routing_trace = build_reviewed_concept_memory_routing_trace(
        admission_review=admission_review,
        memory_learning_trace=memory_learning_trace,
        memory_routing_trace_candidate=routing,
    )
    memory_application_data = build_reviewed_concept_memory_application_data(
        admission_review=admission_review,
        memory_learning_trace=memory_learning_trace,
        memory_routing_trace=memory_routing_trace,
        memory_application_data_candidate=application,
    )
    safety_audit = build_reviewed_concept_memory_admission_safety_audit(
        admission_review=admission_review,
        memory_learning_trace=memory_learning_trace,
        memory_routing_trace=memory_routing_trace,
        memory_application_data=memory_application_data,
    )
    return {
        "admission_review": admission_review.to_dict(),
        "memory_learning_trace": memory_learning_trace.to_dict(),
        "memory_routing_trace": memory_routing_trace.to_dict(),
        "memory_application_data": memory_application_data.to_dict(),
        "admission_safety_audit": safety_audit.to_dict(),
        "admission_review_validation": (
            validate_reviewed_concept_memory_admission_review(admission_review)
        ),
        "memory_learning_trace_validation": (
            validate_reviewed_concept_memory_learning_trace(memory_learning_trace)
        ),
        "memory_routing_trace_validation": (
            validate_reviewed_concept_memory_routing_trace(memory_routing_trace)
        ),
        "memory_application_data_validation": (
            validate_reviewed_concept_memory_application_data(memory_application_data)
        ),
        "admission_safety_audit_validation": (
            validate_reviewed_concept_memory_admission_safety_audit(safety_audit)
        ),
        "safe_claim": SAFE_CLAIM,
    }


def build_demo_reviewed_concept_memory_admission() -> dict[str, object]:
    return build_reviewed_concept_memory_admission(
        build_demo_reviewed_concept_memory_trace_bridge()
    )


def build_demo_held_for_more_evidence_admission() -> dict[str, object]:
    return build_reviewed_concept_memory_admission(
        build_demo_held_for_more_evidence_bridge()
    )


def build_demo_blocked_invalid_candidates_admission() -> dict[str, object]:
    return build_reviewed_concept_memory_admission(build_demo_blocked_from_routing_bridge())


def build_demo_blocked_forbidden_target_layer_admission() -> dict[str, object]:
    return build_reviewed_concept_memory_admission(
        build_demo_blocked_forbidden_target_layer_bridge()
    )


def build_demo_blocked_forbidden_memory_write_admission() -> dict[str, object]:
    return build_reviewed_concept_memory_admission(
        build_demo_blocked_forbidden_memory_write_bridge()
    )


def build_demo_blocked_admission(case: str) -> dict[str, object]:
    cases = {
        "forbidden-target-layer": build_demo_blocked_forbidden_target_layer_admission,
        "forbidden-memory-write": build_demo_blocked_forbidden_memory_write_admission,
        "invalid-candidates": build_demo_blocked_invalid_candidates_admission,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked admission case: {case}") from error


def _admission_status(
    *,
    learning: ReviewedConceptMemoryLearningTraceCandidate,
    routing: ReviewedConceptMemoryRoutingTraceCandidate,
    application: ReviewedConceptMemoryApplicationDataCandidate,
    audit: ReviewedConceptMemoryTraceBridgeAudit,
    lineage_valid: bool,
    bridge_passed: bool,
    support_present: bool,
    counterexamples_valid: bool,
    scope_valid: bool,
    target_allowed: bool,
) -> str:
    if _forbidden_authority_detected(learning, routing, application, audit):
        return "blocked_forbidden_authority_detected"
    if routing.routing_candidate_status == "blocked_forbidden_target_layer":
        return "blocked_forbidden_target_layer"
    if not target_allowed:
        return "blocked_forbidden_target_layer"
    if not bridge_passed:
        return "blocked_bridge_audit_failed"
    if not lineage_valid or not support_present:
        return "blocked_invalid_candidates"
    if not counterexamples_valid:
        return "blocked_unhandled_counterexamples"
    if not scope_valid:
        return "blocked_invalid_scope"
    if (
        learning.candidate_status.startswith("blocked_")
        or routing.routing_candidate_status.startswith("blocked_")
        or application.candidate_status.startswith("blocked_")
    ):
        return "blocked_invalid_candidates"
    if routing.target_layer_candidate == "held_for_more_evidence":
        return "held_for_more_evidence"
    if routing.target_layer_candidate == "blocked_from_routing":
        return "blocked_invalid_candidates"
    if (
        routing.target_layer_candidate == "working_readback_candidate"
        and application.application_candidate_kind == "working_memory_hint_candidate"
    ):
        return "admitted_for_working_readback_trace_only"
    return "blocked_invalid_candidates"


def _forbidden_authority_detected(
    learning: ReviewedConceptMemoryLearningTraceCandidate,
    routing: ReviewedConceptMemoryRoutingTraceCandidate,
    application: ReviewedConceptMemoryApplicationDataCandidate,
    audit: ReviewedConceptMemoryTraceBridgeAudit,
) -> bool:
    return any(
        (
            learning.memory_layer_write_performed,
            learning.actual_memory_learning_trace_created,
            learning.task_behavior_changed,
            learning.automatic_learning_approval_created,
            routing.memory_layer_write_performed,
            routing.actual_memory_routing_trace_created,
            routing.allowed_core_memory_write,
            routing.allowed_long_term_memory_write,
            routing.allowed_archive_memory_write,
            routing.allowed_anchor_write,
            application.memory_layer_write_performed,
            application.actual_memory_application_data_created,
            application.readback_hint_created,
            application.working_memory_mutated,
            application.task_behavior_changed,
            audit.audit_status
            in {
                "blocked_forbidden_memory_write_detected",
                "blocked_forbidden_readback_detected",
                "blocked_forbidden_behavior_change_detected",
            },
        )
    )


def _candidate_lineage_valid(
    learning: ReviewedConceptMemoryLearningTraceCandidate,
    routing: ReviewedConceptMemoryRoutingTraceCandidate,
    application: ReviewedConceptMemoryApplicationDataCandidate,
    audit: ReviewedConceptMemoryTraceBridgeAudit,
) -> bool:
    return (
        learning.source_reviewed_concept_id == routing.source_reviewed_concept_id
        == application.source_reviewed_concept_id
        == audit.source_reviewed_concept_id
        and routing.source_memory_learning_trace_candidate_id
        == learning.memory_learning_trace_candidate_id
        and application.source_memory_learning_trace_candidate_id
        == learning.memory_learning_trace_candidate_id
        and application.source_memory_routing_trace_candidate_id
        == routing.memory_routing_trace_candidate_id
        and audit.memory_learning_trace_candidate_id
        == learning.memory_learning_trace_candidate_id
        and audit.memory_routing_trace_candidate_id
        == routing.memory_routing_trace_candidate_id
        and audit.memory_application_data_candidate_id
        == application.memory_application_data_candidate_id
    )


def _counterexample_handling_valid(
    learning: ReviewedConceptMemoryLearningTraceCandidate,
) -> bool:
    if not learning.counterexample_evidence_refs:
        return learning.counterexample_handling_status in HANDLED_COUNTEREXAMPLE_STATUSES
    return learning.counterexample_handling_status in HANDLED_COUNTEREXAMPLE_STATUSES


def _scope_valid(learning: ReviewedConceptMemoryLearningTraceCandidate) -> bool:
    return bool(learning.scope_text) and learning.generalization_level != "overgeneralized"


def _target_layer_allowed(routing: ReviewedConceptMemoryRoutingTraceCandidate) -> bool:
    return (
        routing.target_layer_candidate
        in {"working_readback_candidate", "held_for_more_evidence", "blocked_from_routing"}
        and routing.routing_candidate_status != "blocked_forbidden_target_layer"
    )


def _admitted_target_layer(
    status: str,
    routing: ReviewedConceptMemoryRoutingTraceCandidate,
) -> str:
    if status == "admitted_for_working_readback_trace_only":
        return "working_readback"
    if status == "held_for_more_evidence":
        return "held_for_more_evidence"
    if routing.target_layer_candidate == "held_for_more_evidence":
        return "held_for_more_evidence"
    return "blocked"


def _admission_summary(status: str, target: str) -> str:
    if status == "admitted_for_working_readback_trace_only":
        return (
            "ReviewedConcept memory candidates admitted as actual Memory Engine "
            "trace/application records for future working-readback preview only."
        )
    if status == "held_for_more_evidence":
        return "ReviewedConcept memory candidates held for more evidence before routing."
    return f"ReviewedConcept memory admission blocked: {status}; target={target}."


def _trace_status(review: ReviewedConceptMemoryAdmissionReviewRecord) -> str:
    if review.admission_status == "admitted_for_working_readback_trace_only":
        return "trace_created_for_working_readback"
    if review.admission_status == "held_for_more_evidence":
        return "held_for_more_evidence"
    return "blocked"


def _trace_summary(status: str) -> str:
    if status == "trace_created_for_working_readback":
        return (
            "Actual MemoryLearningTrace created for reviewed-concept "
            "working-readback route only."
        )
    if status == "held_for_more_evidence":
        return "MemoryLearningTrace record held for more evidence."
    return "MemoryLearningTrace record blocked by admission review."


def _routing_target_and_status(
    review: ReviewedConceptMemoryAdmissionReviewRecord,
) -> tuple[str, str]:
    if review.admission_status == "admitted_for_working_readback_trace_only":
        return "working_readback", "routed_to_working_readback_trace"
    if review.admission_status == "held_for_more_evidence":
        return "held_for_more_evidence", "held_for_more_evidence"
    return "blocked", "blocked_from_routing"


def _application_kind_and_status(
    review: ReviewedConceptMemoryAdmissionReviewRecord,
) -> tuple[str, str]:
    if review.admission_status == "admitted_for_working_readback_trace_only":
        return "working_memory_hint_material", "application_data_created_for_working_readback"
    if review.admission_status == "held_for_more_evidence":
        return "held_for_more_evidence", "held_for_more_evidence"
    return "blocked", "blocked"


def _safety_blocked_reasons(
    *,
    admission_review_valid: bool,
    memory_learning_trace_valid: bool,
    memory_routing_trace_valid: bool,
    memory_application_data_valid: bool,
    no_memory_layer_write: bool,
    no_core_memory_write: bool,
    no_long_term_memory_write: bool,
    no_archive_memory_write: bool,
    no_anchor_write: bool,
    no_readback_hint_created: bool,
    no_working_memory_mutation: bool,
    no_task_behavior_change: bool,
    no_automatic_learning_approval: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not (
        no_memory_layer_write
        and no_core_memory_write
        and no_long_term_memory_write
        and no_archive_memory_write
        and no_anchor_write
    ):
        reasons.append("blocked_forbidden_memory_layer_write_detected")
    if not (no_readback_hint_created and no_working_memory_mutation):
        reasons.append("blocked_forbidden_readback_detected")
    if not no_task_behavior_change:
        reasons.append("blocked_forbidden_behavior_change_detected")
    if not no_automatic_learning_approval:
        reasons.append("blocked_forbidden_memory_layer_write_detected")
    if not admission_review_valid:
        reasons.append("blocked_invalid_admission_review")
    if not memory_learning_trace_valid:
        reasons.append("blocked_invalid_memory_learning_trace")
    if not memory_routing_trace_valid:
        reasons.append("blocked_invalid_memory_routing_trace")
    if not memory_application_data_valid:
        reasons.append("blocked_invalid_memory_application_data")
    return tuple(dict.fromkeys(reasons))


def _safety_audit_status(blocked_reasons: tuple[str, ...]) -> str:
    if not blocked_reasons:
        return "passed"
    for status in (
        "blocked_forbidden_memory_layer_write_detected",
        "blocked_forbidden_readback_detected",
        "blocked_forbidden_behavior_change_detected",
        "blocked_invalid_admission_review",
        "blocked_invalid_memory_learning_trace",
        "blocked_invalid_memory_routing_trace",
        "blocked_invalid_memory_application_data",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_invalid_admission_review"


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _learning_candidate(
    record: ReviewedConceptMemoryLearningTraceCandidate | dict[str, object],
) -> ReviewedConceptMemoryLearningTraceCandidate:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryLearningTraceCandidate)
        else ReviewedConceptMemoryLearningTraceCandidate.from_dict(dict(record))
    )


def _routing_candidate(
    record: ReviewedConceptMemoryRoutingTraceCandidate | dict[str, object],
) -> ReviewedConceptMemoryRoutingTraceCandidate:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryRoutingTraceCandidate)
        else ReviewedConceptMemoryRoutingTraceCandidate.from_dict(dict(record))
    )


def _application_candidate(
    record: ReviewedConceptMemoryApplicationDataCandidate | dict[str, object],
) -> ReviewedConceptMemoryApplicationDataCandidate:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryApplicationDataCandidate)
        else ReviewedConceptMemoryApplicationDataCandidate.from_dict(dict(record))
    )


def _bridge_audit(
    record: ReviewedConceptMemoryTraceBridgeAudit | dict[str, object],
) -> ReviewedConceptMemoryTraceBridgeAudit:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryTraceBridgeAudit)
        else ReviewedConceptMemoryTraceBridgeAudit.from_dict(dict(record))
    )


def _admission_review(
    record: ReviewedConceptMemoryAdmissionReviewRecord | dict[str, object],
) -> ReviewedConceptMemoryAdmissionReviewRecord:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryAdmissionReviewRecord)
        else ReviewedConceptMemoryAdmissionReviewRecord.from_dict(dict(record))
    )


def _memory_learning_trace(
    record: ReviewedConceptMemoryLearningTrace | dict[str, object],
) -> ReviewedConceptMemoryLearningTrace:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryLearningTrace)
        else ReviewedConceptMemoryLearningTrace.from_dict(dict(record))
    )


def _memory_routing_trace(
    record: ReviewedConceptMemoryRoutingTrace | dict[str, object],
) -> ReviewedConceptMemoryRoutingTrace:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryRoutingTrace)
        else ReviewedConceptMemoryRoutingTrace.from_dict(dict(record))
    )


def _memory_application_data(
    record: ReviewedConceptMemoryApplicationData | dict[str, object],
) -> ReviewedConceptMemoryApplicationData:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryApplicationData)
        else ReviewedConceptMemoryApplicationData.from_dict(dict(record))
    )


def _admission_safety_audit(
    record: ReviewedConceptMemoryAdmissionSafetyAudit | dict[str, object],
) -> ReviewedConceptMemoryAdmissionSafetyAudit:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryAdmissionSafetyAudit)
        else ReviewedConceptMemoryAdmissionSafetyAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
