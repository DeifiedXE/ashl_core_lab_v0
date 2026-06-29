"""Prepare reviewed-concept candidate packets without creating ReviewedConcept."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.concept_candidate_from_task_closure_draft import (
    ConceptCandidateDraftRecord,
    build_demo_draft,
)
from ashl_core_v1.learning.concept_candidate_refinement_from_teacher_review import (
    ConceptCandidateRefinementRecord,
    FutureReviewedConceptPreparationMarker,
    build_demo_teacher_review_ready_refinement,
)
from ashl_core_v1.learning.concept_candidate_schema import (
    SOURCE_ENGINE,
    ConceptCandidate,
    ConceptEvidenceRef,
    ConceptScopeStatement,
    validate_concept_evidence_ref,
    validate_concept_scope_statement,
)
from ashl_core_v1.learning.concept_candidate_teacher_review import (
    ConceptCandidateTeacherReviewDecision,
    ConceptCandidateTeacherReviewSummary,
    ConceptCandidateTeacherReviewTask,
    build_demo_teacher_review_ready_review,
    validate_concept_candidate_teacher_review_decision,
)


EVIDENCE_BUNDLE_SCHEMA_VERSION = "learning_engine_reviewed_concept_evidence_bundle_v0"
SCOPE_BUNDLE_SCHEMA_VERSION = "learning_engine_reviewed_concept_scope_bundle_v0"
READINESS_AUDIT_SCHEMA_VERSION = (
    "learning_engine_reviewed_concept_preparation_readiness_audit_v0"
)
PREPARATION_PACKET_SCHEMA_VERSION = (
    "learning_engine_reviewed_concept_preparation_packet_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Learning Engine can prepare a reviewed-concept candidate packet "
    "from a teacher_review_ready concept refinement marker, including support "
    "evidence, counterexample handling, scope bundle, and readiness audit, "
    "without creating a reviewed concept, approving the concept, writing memory, "
    "or changing task behavior."
)
BLOCKED_CLAIMS = (
    "no_reviewed_concept",
    "no_concept_approval",
    "no_memory_write",
    "no_task_behavior_change",
    "no_automatic_learning_approval",
    "no_core_longterm_archive_anchor_write",
)

ALLOWED_EVIDENCE_BUNDLE_STATUSES = {
    "bundle_ready",
    "blocked_no_support_evidence",
    "blocked_unhandled_counterexamples",
    "blocked_invalid_evidence_refs",
}
ALLOWED_SCOPE_BUNDLE_STATUSES = {
    "scope_ready",
    "blocked_missing_scope",
    "blocked_scope_overbroad",
    "blocked_invalid_generalization_status",
    "blocked_invalid_scope_confidence",
}
ALLOWED_READINESS_STATUSES = {
    "ready_for_future_reviewed_concept_package",
    "blocked_missing_teacher_review_ready_marker",
    "blocked_invalid_teacher_review_decision",
    "blocked_missing_support_evidence",
    "blocked_unhandled_counterexamples",
    "blocked_scope_not_ready",
    "blocked_evidence_bundle_not_ready",
    "blocked_forbidden_authority_detected",
}
ALLOWED_PACKET_STATUSES = {
    "packet_ready",
    "blocked_missing_preparation_marker",
    "blocked_invalid_evidence_bundle",
    "blocked_invalid_scope_bundle",
    "blocked_readiness_audit_failed",
    "blocked_forbidden_authority_detected",
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
class ReviewedConceptEvidenceBundle:
    evidence_bundle_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_id: str
    source_concept_candidate_draft_id: str
    source_preparation_marker_id: str
    support_evidence_refs: tuple[ConceptEvidenceRef, ...]
    counterexample_evidence_refs: tuple[ConceptEvidenceRef, ...]
    support_evidence_count: int
    counterexample_evidence_count: int
    support_summary: str
    counterexample_summary: str
    counterexample_handling_status: str
    counterexample_handling_summary: str
    evidence_bundle_status: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVIDENCE_BUNDLE_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_evidence_bundle_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.evidence_bundle_status not in ALLOWED_EVIDENCE_BUNDLE_STATUSES:
            raise ValueError(f"unknown evidence_bundle_status: {self.evidence_bundle_status}")
        object.__setattr__(self, "support_evidence_refs", tuple(self.support_evidence_refs))
        object.__setattr__(
            self,
            "counterexample_evidence_refs",
            tuple(self.counterexample_evidence_refs),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptEvidenceBundle":
        values = dict(data)
        values["support_evidence_refs"] = tuple(
            evidence
            if isinstance(evidence, ConceptEvidenceRef)
            else ConceptEvidenceRef.from_dict(dict(evidence))
            for evidence in values.get("support_evidence_refs", ())
        )
        values["counterexample_evidence_refs"] = tuple(
            evidence
            if isinstance(evidence, ConceptEvidenceRef)
            else ConceptEvidenceRef.from_dict(dict(evidence))
            for evidence in values.get("counterexample_evidence_refs", ())
        )
        return cls(**values)


@dataclass(frozen=True)
class ReviewedConceptScopeBundle:
    scope_bundle_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_id: str
    source_preparation_marker_id: str
    concept_label: str
    concept_summary: str
    scope_statement: ConceptScopeStatement | None
    scope_text: str
    applies_when: tuple[str, ...]
    does_not_apply_when: tuple[str, ...]
    known_limits: tuple[str, ...]
    uncertainty_notes: tuple[str, ...]
    scope_confidence: float
    generalization_level: str
    generalization_status: str
    scope_bundle_status: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SCOPE_BUNDLE_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_scope_bundle_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.scope_bundle_status not in ALLOWED_SCOPE_BUNDLE_STATUSES:
            raise ValueError(f"unknown scope_bundle_status: {self.scope_bundle_status}")
        for name in (
            "applies_when",
            "does_not_apply_when",
            "known_limits",
            "uncertainty_notes",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptScopeBundle":
        values = dict(data)
        if values.get("scope_statement") is not None and not isinstance(
            values.get("scope_statement"),
            ConceptScopeStatement,
        ):
            values["scope_statement"] = ConceptScopeStatement.from_dict(
                dict(values["scope_statement"])
            )
        return cls(**values)


@dataclass(frozen=True)
class ReviewedConceptPreparationReadinessAudit:
    readiness_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_id: str
    source_concept_candidate_draft_id: str
    source_review_decision_id: str
    source_refinement_id: str
    source_preparation_marker_id: str
    teacher_review_ready_marker_present: bool
    teacher_review_decision_valid: bool
    support_evidence_present: bool
    counterexample_handling_valid: bool
    scope_bundle_ready: bool
    evidence_bundle_ready: bool
    no_reviewed_concept_created: bool
    no_concept_approval_created: bool
    no_memory_write: bool
    no_task_behavior_change: bool
    no_automatic_learning_approval: bool
    no_core_longterm_archive_anchor_write: bool
    readiness_status: str
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READINESS_AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_preparation_readiness_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.readiness_status not in ALLOWED_READINESS_STATUSES:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        object.__setattr__(
            self,
            "blocked_reasons",
            _tuple_of_str("blocked_reasons", self.blocked_reasons),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptPreparationReadinessAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptPreparationPacket:
    preparation_packet_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_id: str
    source_concept_candidate_draft_id: str
    source_review_task_id: str
    source_review_decision_id: str
    source_review_summary_id: str | None
    source_refinement_id: str
    source_preparation_marker_id: str
    concept_label: str
    concept_summary: str
    evidence_bundle_id: str
    scope_bundle_id: str
    readiness_audit_id: str
    teacher_actor: str
    teacher_role: str
    teacher_note: str
    packet_status: str
    packet_summary: str
    ready_for_future_reviewed_concept_package: bool
    reviewed_concept_created: bool
    concept_approved: bool
    memory_write_performed: bool
    task_behavior_changed: bool
    automatic_learning_approval_created: bool
    safe_claim: str
    blocked_claims: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PREPARATION_PACKET_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_preparation_packet_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.packet_status not in ALLOWED_PACKET_STATUSES:
            raise ValueError(f"unknown packet_status: {self.packet_status}")
        object.__setattr__(
            self,
            "blocked_claims",
            _tuple_of_str("blocked_claims", self.blocked_claims),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptPreparationPacket":
        return cls(**dict(data))


def build_reviewed_concept_evidence_bundle(
    *,
    candidate: ConceptCandidate | dict[str, object],
    draft: ConceptCandidateDraftRecord | dict[str, object],
    marker: FutureReviewedConceptPreparationMarker | dict[str, object] | None,
    teacher_note: str = "",
) -> ReviewedConceptEvidenceBundle:
    candidate_record = _candidate(candidate)
    draft_record = _draft(draft)
    marker_record = _marker(marker) if marker is not None else None
    support_refs = candidate_record.support_evidence_refs
    counterexample_refs = candidate_record.counterexample_evidence_refs
    evidence_errors = _evidence_validation_errors(support_refs, counterexample_refs)
    status = "bundle_ready"
    if not support_refs:
        status = "blocked_no_support_evidence"
    elif evidence_errors:
        status = "blocked_invalid_evidence_refs"
    elif not _counterexamples_handled(candidate_record, teacher_note):
        status = "blocked_unhandled_counterexamples"
    return ReviewedConceptEvidenceBundle(
        evidence_bundle_id=f"reviewed_concept_evidence_bundle:{candidate_record.concept_candidate_id}",
        schema_version=EVIDENCE_BUNDLE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_id=candidate_record.concept_candidate_id,
        source_concept_candidate_draft_id=draft_record.concept_candidate_draft_id,
        source_preparation_marker_id=(
            marker_record.preparation_marker_id if marker_record is not None else ""
        ),
        support_evidence_refs=support_refs,
        counterexample_evidence_refs=counterexample_refs,
        support_evidence_count=len(support_refs),
        counterexample_evidence_count=len(counterexample_refs),
        support_summary=_evidence_summary(support_refs),
        counterexample_summary=_evidence_summary(counterexample_refs),
        counterexample_handling_status=candidate_record.counterexample_handling_status,
        counterexample_handling_summary=_counterexample_handling_summary(
            candidate_record,
            teacher_note,
        ),
        evidence_bundle_status=status,
        source_trace_refs=candidate_record.source_trace_refs,
    )


def validate_reviewed_concept_evidence_bundle(
    bundle: ReviewedConceptEvidenceBundle | dict[str, object],
) -> dict[str, object]:
    try:
        record = _evidence_bundle(bundle)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_evidence_bundle:{error}"]}
    errors: list[str] = []
    if not record.support_evidence_refs:
        errors.append("missing_support_evidence")
    errors.extend(_evidence_validation_errors(record.support_evidence_refs, record.counterexample_evidence_refs))
    if record.evidence_bundle_status != "bundle_ready":
        errors.append(record.evidence_bundle_status)
    return {
        "valid": not errors,
        "error_codes": errors,
        "evidence_bundle_id": record.evidence_bundle_id,
        "evidence_bundle_status": record.evidence_bundle_status,
        "support_evidence_count": record.support_evidence_count,
        "counterexample_evidence_count": record.counterexample_evidence_count,
    }


def build_reviewed_concept_scope_bundle(
    *,
    candidate: ConceptCandidate | dict[str, object],
    marker: FutureReviewedConceptPreparationMarker | dict[str, object] | None,
) -> ReviewedConceptScopeBundle:
    candidate_record = _candidate(candidate)
    marker_record = _marker(marker) if marker is not None else None
    scope = candidate_record.scope_statement
    status = "scope_ready"
    scope_validation = validate_concept_scope_statement(
        scope,
        counterexamples_present=bool(candidate_record.counterexample_evidence_refs),
    )
    if scope is None:
        status = "blocked_missing_scope"
    elif not scope_validation["valid"]:
        if "scope_confidence_below_zero" in scope_validation["error_codes"] or "scope_confidence_above_one" in scope_validation["error_codes"]:
            status = "blocked_invalid_scope_confidence"
        else:
            status = "blocked_missing_scope"
    elif scope.scope_status == "overbroad_needs_split":
        status = "blocked_scope_overbroad"
    elif candidate_record.generalization_level == "overgeneralized":
        status = "blocked_invalid_generalization_status"
    return ReviewedConceptScopeBundle(
        scope_bundle_id=f"reviewed_concept_scope_bundle:{candidate_record.concept_candidate_id}",
        schema_version=SCOPE_BUNDLE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_id=candidate_record.concept_candidate_id,
        source_preparation_marker_id=(
            marker_record.preparation_marker_id if marker_record is not None else ""
        ),
        concept_label=candidate_record.concept_label,
        concept_summary=candidate_record.concept_summary,
        scope_statement=scope,
        scope_text=scope.scope_text,
        applies_when=scope.applies_when,
        does_not_apply_when=scope.does_not_apply_when,
        known_limits=scope.known_limits,
        uncertainty_notes=scope.uncertainty_notes,
        scope_confidence=scope.scope_confidence,
        generalization_level=candidate_record.generalization_level,
        generalization_status=candidate_record.generalization_status,
        scope_bundle_status=status,
        source_trace_refs=candidate_record.source_trace_refs,
    )


def validate_reviewed_concept_scope_bundle(
    bundle: ReviewedConceptScopeBundle | dict[str, object],
) -> dict[str, object]:
    try:
        record = _scope_bundle(bundle)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_scope_bundle:{error}"]}
    errors: list[str] = []
    if record.scope_statement is None:
        errors.append("missing_scope")
    if not record.scope_text:
        errors.append("missing_scope_text")
    if record.scope_confidence < 0.0 or record.scope_confidence > 1.0:
        errors.append("invalid_scope_confidence")
    if record.generalization_level == "overgeneralized":
        errors.append("overgeneralized_scope")
    if record.scope_bundle_status != "scope_ready":
        errors.append(record.scope_bundle_status)
    return {
        "valid": not errors,
        "error_codes": errors,
        "scope_bundle_id": record.scope_bundle_id,
        "scope_bundle_status": record.scope_bundle_status,
        "scope_confidence": record.scope_confidence,
        "generalization_level": record.generalization_level,
    }


def build_reviewed_concept_preparation_readiness_audit(
    *,
    candidate: ConceptCandidate | dict[str, object],
    draft: ConceptCandidateDraftRecord | dict[str, object],
    decision: ConceptCandidateTeacherReviewDecision | dict[str, object],
    refinement: ConceptCandidateRefinementRecord | dict[str, object],
    marker: FutureReviewedConceptPreparationMarker | dict[str, object] | None,
    evidence_bundle: ReviewedConceptEvidenceBundle | dict[str, object],
    scope_bundle: ReviewedConceptScopeBundle | dict[str, object],
) -> ReviewedConceptPreparationReadinessAudit:
    candidate_record = _candidate(candidate)
    draft_record = _draft(draft)
    decision_record = _decision(decision)
    refinement_record = _refinement(refinement)
    marker_record = _marker(marker) if marker is not None else None
    evidence_record = _evidence_bundle(evidence_bundle)
    scope_record = _scope_bundle(scope_bundle)
    teacher_review_ready_marker_present = (
        marker_record is not None
        and marker_record.candidate_ready_for_future_reviewed_concept_package is True
    )
    teacher_review_decision_valid = (
        decision_record.teacher_decision == "teacher_review_ready"
        and validate_concept_candidate_teacher_review_decision(decision_record)["valid"]
    )
    evidence_validation = validate_reviewed_concept_evidence_bundle(evidence_record)
    scope_validation = validate_reviewed_concept_scope_bundle(scope_record)
    blocked_reasons = _readiness_blocked_reasons(
        marker_present=teacher_review_ready_marker_present,
        decision_valid=teacher_review_decision_valid,
        evidence_validation=evidence_validation,
        scope_validation=scope_validation,
    )
    return ReviewedConceptPreparationReadinessAudit(
        readiness_audit_id=f"reviewed_concept_preparation_audit:{candidate_record.concept_candidate_id}",
        schema_version=READINESS_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_id=candidate_record.concept_candidate_id,
        source_concept_candidate_draft_id=draft_record.concept_candidate_draft_id,
        source_review_decision_id=decision_record.review_decision_id,
        source_refinement_id=refinement_record.refinement_id,
        source_preparation_marker_id=(
            marker_record.preparation_marker_id if marker_record is not None else ""
        ),
        teacher_review_ready_marker_present=teacher_review_ready_marker_present,
        teacher_review_decision_valid=teacher_review_decision_valid,
        support_evidence_present=bool(candidate_record.support_evidence_refs),
        counterexample_handling_valid=evidence_record.evidence_bundle_status != "blocked_unhandled_counterexamples",
        scope_bundle_ready=scope_record.scope_bundle_status == "scope_ready",
        evidence_bundle_ready=evidence_record.evidence_bundle_status == "bundle_ready",
        no_reviewed_concept_created=True,
        no_concept_approval_created=True,
        no_memory_write=True,
        no_task_behavior_change=True,
        no_automatic_learning_approval=True,
        no_core_longterm_archive_anchor_write=True,
        readiness_status=_readiness_status(blocked_reasons),
        blocked_reasons=tuple(blocked_reasons),
        source_trace_refs=candidate_record.source_trace_refs,
    )


def validate_reviewed_concept_preparation_readiness_audit(
    audit: ReviewedConceptPreparationReadinessAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_readiness_audit:{error}"]}
    errors: list[str] = []
    if record.readiness_status != "ready_for_future_reviewed_concept_package":
        errors.append(record.readiness_status)
    for name in (
        "no_reviewed_concept_created",
        "no_concept_approval_created",
        "no_memory_write",
        "no_task_behavior_change",
        "no_automatic_learning_approval",
        "no_core_longterm_archive_anchor_write",
    ):
        if getattr(record, name) is not True:
            errors.append(f"{name}_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "readiness_audit_id": record.readiness_audit_id,
        "readiness_status": record.readiness_status,
        "teacher_review_ready_marker_present": record.teacher_review_ready_marker_present,
        "support_evidence_present": record.support_evidence_present,
        "counterexample_handling_valid": record.counterexample_handling_valid,
    }


def build_reviewed_concept_preparation_packet(
    *,
    candidate: ConceptCandidate | dict[str, object],
    draft: ConceptCandidateDraftRecord | dict[str, object],
    task: ConceptCandidateTeacherReviewTask | dict[str, object],
    decision: ConceptCandidateTeacherReviewDecision | dict[str, object],
    summary: ConceptCandidateTeacherReviewSummary | dict[str, object] | None,
    refinement: ConceptCandidateRefinementRecord | dict[str, object],
    marker: FutureReviewedConceptPreparationMarker | dict[str, object] | None,
) -> dict[str, object]:
    candidate_record = _candidate(candidate)
    draft_record = _draft(draft)
    task_record = _task(task)
    decision_record = _decision(decision)
    summary_record = _summary(summary) if summary is not None else None
    refinement_record = _refinement(refinement)
    marker_record = _marker(marker) if marker is not None else None
    evidence_bundle = build_reviewed_concept_evidence_bundle(
        candidate=candidate_record,
        draft=draft_record,
        marker=marker_record,
        teacher_note=decision_record.teacher_note,
    )
    scope_bundle = build_reviewed_concept_scope_bundle(
        candidate=candidate_record,
        marker=marker_record,
    )
    audit = build_reviewed_concept_preparation_readiness_audit(
        candidate=candidate_record,
        draft=draft_record,
        decision=decision_record,
        refinement=refinement_record,
        marker=marker_record,
        evidence_bundle=evidence_bundle,
        scope_bundle=scope_bundle,
    )
    packet_status = _packet_status(marker_record, evidence_bundle, scope_bundle, audit)
    packet = ReviewedConceptPreparationPacket(
        preparation_packet_id=f"reviewed_concept_preparation_packet:{candidate_record.concept_candidate_id}",
        schema_version=PREPARATION_PACKET_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_id=candidate_record.concept_candidate_id,
        source_concept_candidate_draft_id=draft_record.concept_candidate_draft_id,
        source_review_task_id=task_record.review_task_id,
        source_review_decision_id=decision_record.review_decision_id,
        source_review_summary_id=(
            summary_record.review_summary_id if summary_record is not None else None
        ),
        source_refinement_id=refinement_record.refinement_id,
        source_preparation_marker_id=(
            marker_record.preparation_marker_id if marker_record is not None else ""
        ),
        concept_label=candidate_record.concept_label,
        concept_summary=candidate_record.concept_summary,
        evidence_bundle_id=evidence_bundle.evidence_bundle_id,
        scope_bundle_id=scope_bundle.scope_bundle_id,
        readiness_audit_id=audit.readiness_audit_id,
        teacher_actor=decision_record.teacher_actor,
        teacher_role=decision_record.teacher_role,
        teacher_note=decision_record.teacher_note,
        packet_status=packet_status,
        packet_summary=(
            "Reviewed-concept preparation packet is ready for a future package."
            if packet_status == "packet_ready"
            else f"Reviewed-concept preparation packet blocked: {packet_status}."
        ),
        ready_for_future_reviewed_concept_package=packet_status == "packet_ready",
        reviewed_concept_created=False,
        concept_approved=False,
        memory_write_performed=False,
        task_behavior_changed=False,
        automatic_learning_approval_created=False,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        source_trace_refs=candidate_record.source_trace_refs,
    )
    return {
        "preparation_packet": packet.to_dict(),
        "evidence_bundle": evidence_bundle.to_dict(),
        "scope_bundle": scope_bundle.to_dict(),
        "readiness_audit": audit.to_dict(),
        "packet_validation": validate_reviewed_concept_preparation_packet(packet),
        "reviewed_concept_created": False,
        "concept_approved": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
        "automatic_learning_approval_created": False,
    }


def validate_reviewed_concept_preparation_packet(
    packet: ReviewedConceptPreparationPacket | dict[str, object],
) -> dict[str, object]:
    try:
        record = _packet(packet)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_packet:{error}"]}
    errors: list[str] = []
    if record.packet_status != "packet_ready":
        errors.append(record.packet_status)
    if record.ready_for_future_reviewed_concept_package != (record.packet_status == "packet_ready"):
        errors.append("ready_flag_mismatch")
    for flag in (
        "reviewed_concept_created",
        "concept_approved",
        "memory_write_performed",
        "task_behavior_changed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    if not set(BLOCKED_CLAIMS).issubset(set(record.blocked_claims)):
        errors.append("blocked_claims_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "preparation_packet_id": record.preparation_packet_id,
        "packet_status": record.packet_status,
        "ready_for_future_reviewed_concept_package": (
            record.ready_for_future_reviewed_concept_package
        ),
        "reviewed_concept_created": record.reviewed_concept_created,
        "concept_approved": record.concept_approved,
        "memory_write_performed": record.memory_write_performed,
        "task_behavior_changed": record.task_behavior_changed,
        "automatic_learning_approval_created": record.automatic_learning_approval_created,
    }


def build_demo_reviewed_concept_preparation_packet() -> dict[str, object]:
    review_payload = build_demo_teacher_review_ready_review()
    refinement_payload = build_demo_teacher_review_ready_refinement()
    draft = build_demo_draft("unknown")
    candidate = draft.drafted_concept_candidate
    return build_reviewed_concept_preparation_packet(
        candidate=candidate,
        draft=draft,
        task=review_payload["review_task"],
        decision=review_payload["review_decision"],
        summary=review_payload["review_summary"],
        refinement=refinement_payload["refinement_record"],
        marker=refinement_payload["future_reviewed_concept_preparation_marker"],
    )


def build_demo_blocked_missing_support_preparation() -> dict[str, object]:
    return _blocked_packet(_candidate_without_support())


def build_demo_blocked_unhandled_counterexample_preparation() -> dict[str, object]:
    return _blocked_packet(_candidate_with_unhandled_counterexample())


def build_demo_blocked_overbroad_scope_preparation() -> dict[str, object]:
    return _blocked_packet(_candidate_with_overbroad_scope())


def build_demo_blocked_preparation(case: str) -> dict[str, object]:
    cases = {
        "missing-support": build_demo_blocked_missing_support_preparation,
        "unhandled-counterexample": build_demo_blocked_unhandled_counterexample_preparation,
        "overbroad-scope": build_demo_blocked_overbroad_scope_preparation,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked preparation case: {case}") from error


def _blocked_packet(candidate: ConceptCandidate) -> dict[str, object]:
    review_payload = build_demo_teacher_review_ready_review()
    refinement_payload = build_demo_teacher_review_ready_refinement()
    draft = build_demo_draft("unknown")
    return build_reviewed_concept_preparation_packet(
        candidate=candidate,
        draft=draft,
        task=review_payload["review_task"],
        decision=review_payload["review_decision"],
        summary=review_payload["review_summary"],
        refinement=refinement_payload["refinement_record"],
        marker=refinement_payload["future_reviewed_concept_preparation_marker"],
    )


def _candidate_without_support() -> ConceptCandidate:
    candidate = build_demo_draft("unknown").drafted_concept_candidate
    data = candidate.to_dict()
    data["support_evidence_refs"] = []
    data["candidate_status"] = "needs_more_support"
    return ConceptCandidate.from_dict(data)


def _candidate_with_unhandled_counterexample() -> ConceptCandidate:
    candidate = build_demo_draft("unknown").drafted_concept_candidate
    counterexample = ConceptEvidenceRef(
        evidence_ref_id="concept_evidence:unhandled_counterexample_001",
        evidence_kind="counterexample",
        source_engine="task_engine",
        source_record_id="task_closure:unhandled_counterexample",
        source_task_id="task:unknown_needs_observe",
        source_case_id="unknown_needs_observe",
        source_tick_refs=("tick:counterexample:001",),
        state_summary="unknown_front_state",
        action_summary="observe_or_adjust",
        outcome_summary="no_context_change",
        expected_outcome="context_observed",
        actual_outcome="no_context_change",
        difference_label="observe_did_not_resolve_unknown",
        supports_candidate=False,
        counterexample_to_candidate=True,
        teacher_visible=True,
        source_trace_refs=("task_closure:unhandled_counterexample",),
    )
    data = candidate.to_dict()
    data["counterexample_evidence_refs"] = [counterexample.to_dict()]
    data["counterexample_handling_status"] = "counterexamples_present"
    data["candidate_status"] = "teacher_review_ready"
    data["generalization_status"] = "teacher_review_ready"
    return ConceptCandidate.from_dict(data)


def _candidate_with_overbroad_scope() -> ConceptCandidate:
    candidate = build_demo_draft("unknown").drafted_concept_candidate
    data = candidate.to_dict()
    scope = dict(data["scope_statement"])
    scope["scope_status"] = "overbroad_needs_split"
    data["scope_statement"] = scope
    return ConceptCandidate.from_dict(data)


def _evidence_validation_errors(
    support_refs: tuple[ConceptEvidenceRef, ...],
    counterexample_refs: tuple[ConceptEvidenceRef, ...],
) -> list[str]:
    errors: list[str] = []
    for evidence in (*support_refs, *counterexample_refs):
        validation = validate_concept_evidence_ref(evidence)
        errors.extend(str(code) for code in validation["error_codes"])
    return errors


def _counterexamples_handled(candidate: ConceptCandidate, teacher_note: str) -> bool:
    if not candidate.counterexample_evidence_refs:
        return True
    if candidate.counterexample_handling_status in {"scope_narrowed", "split_required"}:
        return True
    if "scope remains valid" in teacher_note.lower():
        return True
    return False


def _counterexample_handling_summary(
    candidate: ConceptCandidate,
    teacher_note: str,
) -> str:
    if not candidate.counterexample_evidence_refs:
        return "No counterexamples are attached to this candidate."
    if _counterexamples_handled(candidate, teacher_note):
        return "Counterexamples are present and have an explicit handling path."
    return "Counterexamples are present but not handled for preparation."


def _evidence_summary(evidence_refs: tuple[ConceptEvidenceRef, ...]) -> str:
    if not evidence_refs:
        return "none"
    return "; ".join(
        f"{evidence.state_summary} + {evidence.action_summary} -> {evidence.outcome_summary}"
        for evidence in evidence_refs
    )


def _readiness_blocked_reasons(
    *,
    marker_present: bool,
    decision_valid: bool,
    evidence_validation: dict[str, object],
    scope_validation: dict[str, object],
) -> list[str]:
    reasons: list[str] = []
    if not marker_present:
        reasons.append("blocked_missing_teacher_review_ready_marker")
    if not decision_valid:
        reasons.append("blocked_invalid_teacher_review_decision")
    if "missing_support_evidence" in evidence_validation["error_codes"]:
        reasons.append("blocked_missing_support_evidence")
    if "blocked_unhandled_counterexamples" in evidence_validation["error_codes"]:
        reasons.append("blocked_unhandled_counterexamples")
    if not evidence_validation["valid"]:
        reasons.append("blocked_evidence_bundle_not_ready")
    if not scope_validation["valid"]:
        reasons.append("blocked_scope_not_ready")
    return tuple(dict.fromkeys(reasons))


def _readiness_status(blocked_reasons: list[str]) -> str:
    if not blocked_reasons:
        return "ready_for_future_reviewed_concept_package"
    for status in (
        "blocked_missing_teacher_review_ready_marker",
        "blocked_invalid_teacher_review_decision",
        "blocked_missing_support_evidence",
        "blocked_unhandled_counterexamples",
        "blocked_scope_not_ready",
        "blocked_evidence_bundle_not_ready",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_forbidden_authority_detected"


def _packet_status(
    marker: FutureReviewedConceptPreparationMarker | None,
    evidence_bundle: ReviewedConceptEvidenceBundle,
    scope_bundle: ReviewedConceptScopeBundle,
    audit: ReviewedConceptPreparationReadinessAudit,
) -> str:
    if marker is None or not marker.candidate_ready_for_future_reviewed_concept_package:
        return "blocked_missing_preparation_marker"
    if evidence_bundle.evidence_bundle_status != "bundle_ready":
        return "blocked_invalid_evidence_bundle"
    if scope_bundle.scope_bundle_status != "scope_ready":
        return "blocked_invalid_scope_bundle"
    if audit.readiness_status != "ready_for_future_reviewed_concept_package":
        return "blocked_readiness_audit_failed"
    return "packet_ready"


def _candidate(candidate: ConceptCandidate | dict[str, object]) -> ConceptCandidate:
    return candidate if isinstance(candidate, ConceptCandidate) else ConceptCandidate.from_dict(dict(candidate))


def _draft(draft: ConceptCandidateDraftRecord | dict[str, object]) -> ConceptCandidateDraftRecord:
    return draft if isinstance(draft, ConceptCandidateDraftRecord) else ConceptCandidateDraftRecord.from_dict(dict(draft))


def _task(task: ConceptCandidateTeacherReviewTask | dict[str, object]) -> ConceptCandidateTeacherReviewTask:
    return task if isinstance(task, ConceptCandidateTeacherReviewTask) else ConceptCandidateTeacherReviewTask.from_dict(dict(task))


def _decision(
    decision: ConceptCandidateTeacherReviewDecision | dict[str, object],
) -> ConceptCandidateTeacherReviewDecision:
    return (
        decision
        if isinstance(decision, ConceptCandidateTeacherReviewDecision)
        else ConceptCandidateTeacherReviewDecision.from_dict(dict(decision))
    )


def _summary(
    summary: ConceptCandidateTeacherReviewSummary | dict[str, object],
) -> ConceptCandidateTeacherReviewSummary:
    return (
        summary
        if isinstance(summary, ConceptCandidateTeacherReviewSummary)
        else ConceptCandidateTeacherReviewSummary.from_dict(dict(summary))
    )


def _refinement(
    refinement: ConceptCandidateRefinementRecord | dict[str, object],
) -> ConceptCandidateRefinementRecord:
    return (
        refinement
        if isinstance(refinement, ConceptCandidateRefinementRecord)
        else ConceptCandidateRefinementRecord.from_dict(dict(refinement))
    )


def _marker(
    marker: FutureReviewedConceptPreparationMarker | dict[str, object] | None,
) -> FutureReviewedConceptPreparationMarker | None:
    if marker is None:
        return None
    return (
        marker
        if isinstance(marker, FutureReviewedConceptPreparationMarker)
        else FutureReviewedConceptPreparationMarker.from_dict(dict(marker))
    )


def _evidence_bundle(
    bundle: ReviewedConceptEvidenceBundle | dict[str, object],
) -> ReviewedConceptEvidenceBundle:
    return (
        bundle
        if isinstance(bundle, ReviewedConceptEvidenceBundle)
        else ReviewedConceptEvidenceBundle.from_dict(dict(bundle))
    )


def _scope_bundle(
    bundle: ReviewedConceptScopeBundle | dict[str, object],
) -> ReviewedConceptScopeBundle:
    return (
        bundle
        if isinstance(bundle, ReviewedConceptScopeBundle)
        else ReviewedConceptScopeBundle.from_dict(dict(bundle))
    )


def _audit(
    audit: ReviewedConceptPreparationReadinessAudit | dict[str, object],
) -> ReviewedConceptPreparationReadinessAudit:
    return (
        audit
        if isinstance(audit, ReviewedConceptPreparationReadinessAudit)
        else ReviewedConceptPreparationReadinessAudit.from_dict(dict(audit))
    )


def _packet(
    packet: ReviewedConceptPreparationPacket | dict[str, object],
) -> ReviewedConceptPreparationPacket:
    return (
        packet
        if isinstance(packet, ReviewedConceptPreparationPacket)
        else ReviewedConceptPreparationPacket.from_dict(dict(packet))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
