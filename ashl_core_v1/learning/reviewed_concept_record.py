"""Record-only ReviewedConcept creation for Learning Engine v0."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.concept_candidate_schema import SOURCE_ENGINE, ConceptEvidenceRef
from ashl_core_v1.learning.reviewed_concept_preparation import (
    ReviewedConceptEvidenceBundle,
    ReviewedConceptPreparationPacket,
    ReviewedConceptPreparationReadinessAudit,
    ReviewedConceptScopeBundle,
    build_demo_blocked_missing_support_preparation as _build_missing_support_preparation,
    build_demo_blocked_overbroad_scope_preparation as _build_overbroad_scope_preparation,
    build_demo_blocked_unhandled_counterexample_preparation as _build_unhandled_counterexample_preparation,
    build_demo_reviewed_concept_preparation_packet,
)


REVIEWED_CONCEPT_SCHEMA_VERSION = "learning_engine_reviewed_concept_record_v0"
LINEAGE_SCHEMA_VERSION = "learning_engine_reviewed_concept_lineage_v0"
SAFETY_AUDIT_SCHEMA_VERSION = "learning_engine_reviewed_concept_safety_audit_v0"

SAFE_CLAIM = (
    "This is a Learning Engine reviewed concept record with source evidence, "
    "counterexample handling, scope, teacher review lineage, and safety audit. "
    "It is not memory admission, memory write, behavior authority, or long-term "
    "concept promotion."
)
BLOCKED_CLAIMS = (
    "no_memory_write",
    "no_memory_application",
    "no_task_behavior_change",
    "no_automatic_learning_approval",
    "no_core_longterm_archive_anchor_write",
    "no_concept_promotion",
    "no_general_learning_claim",
)

ALLOWED_REVIEW_STATUSES = {
    "reviewed",
    "blocked_invalid_preparation_packet",
    "blocked_readiness_audit_failed",
    "blocked_unhandled_counterexamples",
    "blocked_invalid_scope",
    "blocked_forbidden_authority_detected",
}
ALLOWED_REVIEWED_CONCEPT_STATUSES = {
    "reviewed_record_only",
    "held_for_memory_routing_review",
    "blocked",
}
ALLOWED_LINEAGE_STATUSES = {
    "lineage_complete",
    "blocked_missing_task_source",
    "blocked_missing_concept_candidate",
    "blocked_missing_teacher_review",
    "blocked_missing_refinement",
    "blocked_missing_preparation_packet",
}
ALLOWED_SAFETY_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_preparation_packet",
    "blocked_readiness_audit_failed",
    "blocked_incomplete_lineage",
    "blocked_missing_support_evidence",
    "blocked_unhandled_counterexamples",
    "blocked_invalid_scope",
    "blocked_forbidden_authority_detected",
}
REVIEWED_CONCEPT_COUNTEREXAMPLE_STATUSES = {
    "no_counterexamples",
    "scope_narrowed",
    "split_required",
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
class ReviewedConceptRecord:
    reviewed_concept_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_preparation_packet_id: str
    source_concept_candidate_id: str
    source_concept_candidate_draft_id: str
    source_review_task_id: str
    source_review_decision_id: str
    source_refinement_id: str
    source_preparation_marker_id: str
    concept_label: str
    concept_summary: str
    scope_text: str
    applies_when: tuple[str, ...]
    does_not_apply_when: tuple[str, ...]
    known_limits: tuple[str, ...]
    uncertainty_notes: tuple[str, ...]
    support_evidence_refs: tuple[str, ...]
    counterexample_evidence_refs: tuple[str, ...]
    support_evidence_count: int
    counterexample_evidence_count: int
    counterexample_handling_status: str
    counterexample_handling_summary: str
    generalization_level: str
    generalization_status: str
    teacher_actor: str
    teacher_role: str
    teacher_note: str
    review_status: str
    reviewed_concept_status: str
    memory_write_allowed: bool
    memory_write_performed: bool
    memory_application_candidate_allowed: bool
    task_behavior_change_allowed: bool
    task_behavior_changed: bool
    promotion_candidate_allowed: bool
    automatic_learning_approval_created: bool
    safe_claim: str
    blocked_claims: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REVIEWED_CONCEPT_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_record_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.review_status not in ALLOWED_REVIEW_STATUSES:
            raise ValueError(f"unknown review_status: {self.review_status}")
        if self.reviewed_concept_status not in ALLOWED_REVIEWED_CONCEPT_STATUSES:
            raise ValueError(
                f"unknown reviewed_concept_status: {self.reviewed_concept_status}"
            )
        for name in (
            "applies_when",
            "does_not_apply_when",
            "known_limits",
            "uncertainty_notes",
            "support_evidence_refs",
            "counterexample_evidence_refs",
            "blocked_claims",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptLineageRecord:
    lineage_id: str
    schema_version: str
    created_at: str
    source_engine: str
    reviewed_concept_id: str
    source_task_ids: tuple[str, ...]
    source_case_ids: tuple[str, ...]
    source_state_action_outcome_refs: tuple[str, ...]
    source_concept_candidate_id: str
    source_concept_candidate_draft_id: str
    source_review_decision_id: str
    source_refinement_id: str
    source_preparation_packet_id: str
    lineage_summary: str
    lineage_complete: bool
    lineage_status: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != LINEAGE_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_lineage_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.lineage_status not in ALLOWED_LINEAGE_STATUSES:
            raise ValueError(f"unknown lineage_status: {self.lineage_status}")
        for name in (
            "source_task_ids",
            "source_case_ids",
            "source_state_action_outcome_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptLineageRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptSafetyAuditRecord:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str | None
    source_preparation_packet_id: str
    preparation_packet_valid: bool
    readiness_audit_passed: bool
    lineage_complete: bool
    support_evidence_present: bool
    counterexample_handling_valid: bool
    scope_valid: bool
    no_memory_write_allowed: bool
    no_memory_write_performed: bool
    no_memory_application_candidate_allowed: bool
    no_task_behavior_change_allowed: bool
    no_task_behavior_changed: bool
    no_promotion_candidate_allowed: bool
    no_automatic_learning_approval: bool
    no_core_longterm_archive_anchor_write: bool
    audit_status: str
    blocked_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_safety_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.audit_status not in ALLOWED_SAFETY_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        object.__setattr__(
            self,
            "blocked_reasons",
            _tuple_of_str("blocked_reasons", self.blocked_reasons),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptSafetyAuditRecord":
        return cls(**dict(data))


def build_reviewed_concept_record(
    *,
    preparation_packet: ReviewedConceptPreparationPacket | dict[str, object],
    evidence_bundle: ReviewedConceptEvidenceBundle | dict[str, object],
    scope_bundle: ReviewedConceptScopeBundle | dict[str, object],
    readiness_audit: ReviewedConceptPreparationReadinessAudit | dict[str, object],
) -> ReviewedConceptRecord:
    packet = _packet(preparation_packet)
    evidence = _evidence_bundle(evidence_bundle)
    scope = _scope_bundle(scope_bundle)
    readiness = _readiness_audit(readiness_audit)
    review_status = _review_status(packet, evidence, scope, readiness)
    reviewed_concept_status = (
        "reviewed_record_only" if review_status == "reviewed" else "blocked"
    )
    support_refs = tuple(item.evidence_ref_id for item in evidence.support_evidence_refs)
    counterexample_refs = tuple(
        item.evidence_ref_id for item in evidence.counterexample_evidence_refs
    )
    return ReviewedConceptRecord(
        reviewed_concept_id=f"reviewed_concept:{packet.source_concept_candidate_id}",
        schema_version=REVIEWED_CONCEPT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_preparation_packet_id=packet.preparation_packet_id,
        source_concept_candidate_id=packet.source_concept_candidate_id,
        source_concept_candidate_draft_id=packet.source_concept_candidate_draft_id,
        source_review_task_id=packet.source_review_task_id,
        source_review_decision_id=packet.source_review_decision_id,
        source_refinement_id=packet.source_refinement_id,
        source_preparation_marker_id=packet.source_preparation_marker_id,
        concept_label=packet.concept_label,
        concept_summary=packet.concept_summary,
        scope_text=scope.scope_text,
        applies_when=scope.applies_when,
        does_not_apply_when=scope.does_not_apply_when,
        known_limits=scope.known_limits,
        uncertainty_notes=scope.uncertainty_notes,
        support_evidence_refs=support_refs,
        counterexample_evidence_refs=counterexample_refs,
        support_evidence_count=evidence.support_evidence_count,
        counterexample_evidence_count=evidence.counterexample_evidence_count,
        counterexample_handling_status=evidence.counterexample_handling_status,
        counterexample_handling_summary=evidence.counterexample_handling_summary,
        generalization_level=scope.generalization_level,
        generalization_status=scope.generalization_status,
        teacher_actor=packet.teacher_actor,
        teacher_role=packet.teacher_role,
        teacher_note=packet.teacher_note,
        review_status=review_status,
        reviewed_concept_status=reviewed_concept_status,
        memory_write_allowed=False,
        memory_write_performed=False,
        memory_application_candidate_allowed=False,
        task_behavior_change_allowed=False,
        task_behavior_changed=False,
        promotion_candidate_allowed=False,
        automatic_learning_approval_created=False,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        source_trace_refs=_combined_trace_refs(
            packet.source_trace_refs,
            evidence.source_trace_refs,
            scope.source_trace_refs,
            readiness.source_trace_refs,
        ),
    )


def validate_reviewed_concept_record(
    record: ReviewedConceptRecord | dict[str, object],
) -> dict[str, object]:
    try:
        reviewed = _reviewed_concept(record)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_reviewed_concept:{error}"]}
    errors: list[str] = []
    if reviewed.review_status != "reviewed":
        errors.append(reviewed.review_status)
    if reviewed.reviewed_concept_status != "reviewed_record_only":
        errors.append("reviewed_concept_status_not_record_only")
    if not reviewed.reviewed_concept_id:
        errors.append("missing_reviewed_concept_id")
    if not reviewed.source_preparation_packet_id:
        errors.append("missing_source_preparation_packet_id")
    if not reviewed.support_evidence_refs:
        errors.append("missing_support_evidence_refs")
    if not reviewed.scope_text:
        errors.append("missing_scope_text")
    if not reviewed.teacher_note:
        errors.append("missing_teacher_note")
    if not _counterexample_status_valid(reviewed.counterexample_handling_status):
        errors.append("unhandled_counterexamples")
    if not _scope_is_valid(reviewed):
        errors.append("invalid_scope")
    errors.extend(_forbidden_reviewed_flags(reviewed))
    if SAFE_CLAIM != reviewed.safe_claim:
        errors.append("safe_claim_mismatch")
    if not set(BLOCKED_CLAIMS).issubset(set(reviewed.blocked_claims)):
        errors.append("blocked_claims_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "reviewed_concept_id": reviewed.reviewed_concept_id,
        "review_status": reviewed.review_status,
        "reviewed_concept_status": reviewed.reviewed_concept_status,
        "memory_write_allowed": reviewed.memory_write_allowed,
        "memory_write_performed": reviewed.memory_write_performed,
        "task_behavior_changed": reviewed.task_behavior_changed,
    }


def build_reviewed_concept_lineage_record(
    *,
    reviewed_concept: ReviewedConceptRecord | dict[str, object],
    preparation_packet: ReviewedConceptPreparationPacket | dict[str, object],
    evidence_bundle: ReviewedConceptEvidenceBundle | dict[str, object],
) -> ReviewedConceptLineageRecord:
    reviewed = _reviewed_concept(reviewed_concept)
    packet = _packet(preparation_packet)
    evidence = _evidence_bundle(evidence_bundle)
    evidence_refs = (*evidence.support_evidence_refs, *evidence.counterexample_evidence_refs)
    source_task_ids = _unique(
        item.source_task_id for item in evidence_refs if item.source_task_id
    )
    source_case_ids = _unique(
        item.source_case_id for item in evidence_refs if item.source_case_id
    )
    source_state_action_outcome_refs = _unique(
        item.source_record_id for item in evidence_refs if item.source_record_id
    )
    lineage_status = _lineage_status(
        packet=packet,
        source_task_ids=source_task_ids,
    )
    return ReviewedConceptLineageRecord(
        lineage_id=f"reviewed_concept_lineage:{reviewed.reviewed_concept_id}",
        schema_version=LINEAGE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        reviewed_concept_id=reviewed.reviewed_concept_id,
        source_task_ids=source_task_ids,
        source_case_ids=source_case_ids,
        source_state_action_outcome_refs=source_state_action_outcome_refs,
        source_concept_candidate_id=packet.source_concept_candidate_id,
        source_concept_candidate_draft_id=packet.source_concept_candidate_draft_id,
        source_review_decision_id=packet.source_review_decision_id,
        source_refinement_id=packet.source_refinement_id,
        source_preparation_packet_id=packet.preparation_packet_id,
        lineage_summary=(
            "Reviewed concept lineage links task evidence, concept candidate, "
            "teacher review, refinement, and preparation packet."
            if lineage_status == "lineage_complete"
            else f"Reviewed concept lineage blocked: {lineage_status}."
        ),
        lineage_complete=lineage_status == "lineage_complete",
        lineage_status=lineage_status,
        source_trace_refs=_combined_trace_refs(
            reviewed.source_trace_refs,
            packet.source_trace_refs,
            evidence.source_trace_refs,
        ),
    )


def validate_reviewed_concept_lineage_record(
    record: ReviewedConceptLineageRecord | dict[str, object],
) -> dict[str, object]:
    try:
        lineage = _lineage(record)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_lineage:{error}"]}
    errors: list[str] = []
    if not lineage.lineage_complete:
        errors.append("lineage_incomplete")
    if lineage.lineage_status != "lineage_complete":
        errors.append(lineage.lineage_status)
    if not lineage.source_task_ids:
        errors.append("missing_source_task_ids")
    if not lineage.source_concept_candidate_id:
        errors.append("missing_source_concept_candidate_id")
    if not lineage.source_review_decision_id:
        errors.append("missing_source_review_decision_id")
    if not lineage.source_refinement_id:
        errors.append("missing_source_refinement_id")
    if not lineage.source_preparation_packet_id:
        errors.append("missing_source_preparation_packet_id")
    return {
        "valid": not errors,
        "error_codes": errors,
        "lineage_id": lineage.lineage_id,
        "lineage_status": lineage.lineage_status,
        "lineage_complete": lineage.lineage_complete,
    }


def build_reviewed_concept_safety_audit(
    *,
    reviewed_concept: ReviewedConceptRecord | dict[str, object],
    lineage_record: ReviewedConceptLineageRecord | dict[str, object],
    preparation_packet: ReviewedConceptPreparationPacket | dict[str, object],
    readiness_audit: ReviewedConceptPreparationReadinessAudit | dict[str, object],
) -> ReviewedConceptSafetyAuditRecord:
    reviewed = _reviewed_concept(reviewed_concept)
    lineage = _lineage(lineage_record)
    packet = _packet(preparation_packet)
    readiness = _readiness_audit(readiness_audit)
    preparation_packet_valid = (
        packet.packet_status == "packet_ready"
        and packet.ready_for_future_reviewed_concept_package is True
    )
    readiness_audit_passed = (
        readiness.readiness_status == "ready_for_future_reviewed_concept_package"
    )
    support_evidence_present = reviewed.support_evidence_count > 0
    counterexample_handling_valid = _counterexample_status_valid(
        reviewed.counterexample_handling_status
    )
    scope_valid = _scope_is_valid(reviewed)
    no_memory_write_allowed = reviewed.memory_write_allowed is False
    no_memory_write_performed = reviewed.memory_write_performed is False
    no_memory_application_candidate_allowed = (
        reviewed.memory_application_candidate_allowed is False
    )
    no_task_behavior_change_allowed = reviewed.task_behavior_change_allowed is False
    no_task_behavior_changed = reviewed.task_behavior_changed is False
    no_promotion_candidate_allowed = reviewed.promotion_candidate_allowed is False
    no_automatic_learning_approval = (
        reviewed.automatic_learning_approval_created is False
    )
    no_core_longterm_archive_anchor_write = True
    blocked_reasons = _safety_blocked_reasons(
        preparation_packet_valid=preparation_packet_valid,
        readiness_audit_passed=readiness_audit_passed,
        lineage_complete=lineage.lineage_complete,
        support_evidence_present=support_evidence_present,
        counterexample_handling_valid=counterexample_handling_valid,
        scope_valid=scope_valid,
        no_memory_write_allowed=no_memory_write_allowed,
        no_memory_write_performed=no_memory_write_performed,
        no_memory_application_candidate_allowed=no_memory_application_candidate_allowed,
        no_task_behavior_change_allowed=no_task_behavior_change_allowed,
        no_task_behavior_changed=no_task_behavior_changed,
        no_promotion_candidate_allowed=no_promotion_candidate_allowed,
        no_automatic_learning_approval=no_automatic_learning_approval,
        no_core_longterm_archive_anchor_write=no_core_longterm_archive_anchor_write,
    )
    return ReviewedConceptSafetyAuditRecord(
        safety_audit_id=f"reviewed_concept_safety_audit:{reviewed.reviewed_concept_id}",
        schema_version=SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=reviewed.reviewed_concept_id,
        source_preparation_packet_id=packet.preparation_packet_id,
        preparation_packet_valid=preparation_packet_valid,
        readiness_audit_passed=readiness_audit_passed,
        lineage_complete=lineage.lineage_complete,
        support_evidence_present=support_evidence_present,
        counterexample_handling_valid=counterexample_handling_valid,
        scope_valid=scope_valid,
        no_memory_write_allowed=no_memory_write_allowed,
        no_memory_write_performed=no_memory_write_performed,
        no_memory_application_candidate_allowed=no_memory_application_candidate_allowed,
        no_task_behavior_change_allowed=no_task_behavior_change_allowed,
        no_task_behavior_changed=no_task_behavior_changed,
        no_promotion_candidate_allowed=no_promotion_candidate_allowed,
        no_automatic_learning_approval=no_automatic_learning_approval,
        no_core_longterm_archive_anchor_write=no_core_longterm_archive_anchor_write,
        audit_status=_safety_status(blocked_reasons),
        blocked_reasons=blocked_reasons,
    )


def validate_reviewed_concept_safety_audit(
    record: ReviewedConceptSafetyAuditRecord | dict[str, object],
) -> dict[str, object]:
    try:
        audit = _safety_audit(record)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_safety_audit:{error}"]}
    errors: list[str] = []
    if audit.audit_status != "passed":
        errors.append(audit.audit_status)
    for name in (
        "preparation_packet_valid",
        "readiness_audit_passed",
        "lineage_complete",
        "support_evidence_present",
        "counterexample_handling_valid",
        "scope_valid",
        "no_memory_write_allowed",
        "no_memory_write_performed",
        "no_memory_application_candidate_allowed",
        "no_task_behavior_change_allowed",
        "no_task_behavior_changed",
        "no_promotion_candidate_allowed",
        "no_automatic_learning_approval",
        "no_core_longterm_archive_anchor_write",
    ):
        if getattr(audit, name) is not True:
            errors.append(f"{name}_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "safety_audit_id": audit.safety_audit_id,
        "audit_status": audit.audit_status,
        "blocked_reasons": audit.blocked_reasons,
    }


def build_reviewed_concept_record_bundle(
    preparation_payload: dict[str, object],
) -> dict[str, object]:
    packet = _packet(preparation_payload["preparation_packet"])
    evidence = _evidence_bundle(preparation_payload["evidence_bundle"])
    scope = _scope_bundle(preparation_payload["scope_bundle"])
    readiness = _readiness_audit(preparation_payload["readiness_audit"])
    reviewed = build_reviewed_concept_record(
        preparation_packet=packet,
        evidence_bundle=evidence,
        scope_bundle=scope,
        readiness_audit=readiness,
    )
    lineage = build_reviewed_concept_lineage_record(
        reviewed_concept=reviewed,
        preparation_packet=packet,
        evidence_bundle=evidence,
    )
    safety = build_reviewed_concept_safety_audit(
        reviewed_concept=reviewed,
        lineage_record=lineage,
        preparation_packet=packet,
        readiness_audit=readiness,
    )
    return {
        "reviewed_concept": reviewed.to_dict(),
        "lineage_record": lineage.to_dict(),
        "safety_audit": safety.to_dict(),
        "reviewed_concept_validation": validate_reviewed_concept_record(reviewed),
        "lineage_validation": validate_reviewed_concept_lineage_record(lineage),
        "safety_audit_validation": validate_reviewed_concept_safety_audit(safety),
        "memory_write_performed": reviewed.memory_write_performed,
        "task_behavior_changed": reviewed.task_behavior_changed,
        "automatic_learning_approval_created": (
            reviewed.automatic_learning_approval_created
        ),
    }


def build_demo_reviewed_concept_record() -> dict[str, object]:
    return build_reviewed_concept_record_bundle(
        build_demo_reviewed_concept_preparation_packet()
    )


def build_demo_blocked_invalid_preparation_packet() -> dict[str, object]:
    return build_reviewed_concept_record_bundle(_build_missing_support_preparation())


def build_demo_blocked_unhandled_counterexample() -> dict[str, object]:
    return build_reviewed_concept_record_bundle(_build_unhandled_counterexample_preparation())


def build_demo_blocked_invalid_scope() -> dict[str, object]:
    return build_reviewed_concept_record_bundle(_build_overbroad_scope_preparation())


def build_demo_blocked_reviewed_concept(case: str) -> dict[str, object]:
    cases = {
        "invalid-preparation": build_demo_blocked_invalid_preparation_packet,
        "unhandled-counterexample": build_demo_blocked_unhandled_counterexample,
        "invalid-scope": build_demo_blocked_invalid_scope,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked reviewed concept case: {case}") from error


def _review_status(
    packet: ReviewedConceptPreparationPacket,
    evidence: ReviewedConceptEvidenceBundle,
    scope: ReviewedConceptScopeBundle,
    readiness: ReviewedConceptPreparationReadinessAudit,
) -> str:
    if _preparation_forbidden_authority_detected(packet):
        return "blocked_forbidden_authority_detected"
    if evidence.evidence_bundle_status == "blocked_unhandled_counterexamples":
        return "blocked_unhandled_counterexamples"
    if not _scope_bundle_ready(scope):
        return "blocked_invalid_scope"
    if packet.packet_status != "packet_ready" or not packet.ready_for_future_reviewed_concept_package:
        return "blocked_invalid_preparation_packet"
    if readiness.readiness_status != "ready_for_future_reviewed_concept_package":
        return "blocked_readiness_audit_failed"
    if evidence.support_evidence_count < 1:
        return "blocked_invalid_preparation_packet"
    if not _counterexample_status_valid(evidence.counterexample_handling_status):
        return "blocked_unhandled_counterexamples"
    return "reviewed"


def _preparation_forbidden_authority_detected(
    packet: ReviewedConceptPreparationPacket,
) -> bool:
    return any(
        getattr(packet, name) is not False
        for name in (
            "reviewed_concept_created",
            "concept_approved",
            "memory_write_performed",
            "task_behavior_changed",
            "automatic_learning_approval_created",
        )
    )


def _scope_bundle_ready(scope: ReviewedConceptScopeBundle) -> bool:
    if scope.scope_bundle_status != "scope_ready":
        return False
    if not scope.scope_text:
        return False
    if scope.scope_confidence < 0.0 or scope.scope_confidence > 1.0:
        return False
    if scope.generalization_level == "overgeneralized":
        return False
    if scope.scope_statement is not None and scope.scope_statement.scope_status == "overbroad_needs_split":
        return False
    return True


def _scope_is_valid(reviewed: ReviewedConceptRecord) -> bool:
    if not reviewed.scope_text:
        return False
    if reviewed.generalization_level == "overgeneralized":
        return False
    return reviewed.review_status != "blocked_invalid_scope"


def _counterexample_status_valid(status: str) -> bool:
    return status in REVIEWED_CONCEPT_COUNTEREXAMPLE_STATUSES


def _forbidden_reviewed_flags(reviewed: ReviewedConceptRecord) -> list[str]:
    errors: list[str] = []
    false_flags = (
        "memory_write_allowed",
        "memory_write_performed",
        "memory_application_candidate_allowed",
        "task_behavior_change_allowed",
        "task_behavior_changed",
        "promotion_candidate_allowed",
        "automatic_learning_approval_created",
    )
    for flag in false_flags:
        if getattr(reviewed, flag) is not False:
            errors.append(f"{flag}_true")
    return errors


def _lineage_status(
    *,
    packet: ReviewedConceptPreparationPacket,
    source_task_ids: tuple[str, ...],
) -> str:
    if not source_task_ids:
        return "blocked_missing_task_source"
    if not packet.source_concept_candidate_id:
        return "blocked_missing_concept_candidate"
    if not packet.source_review_decision_id:
        return "blocked_missing_teacher_review"
    if not packet.source_refinement_id:
        return "blocked_missing_refinement"
    if not packet.preparation_packet_id:
        return "blocked_missing_preparation_packet"
    return "lineage_complete"


def _safety_blocked_reasons(
    *,
    preparation_packet_valid: bool,
    readiness_audit_passed: bool,
    lineage_complete: bool,
    support_evidence_present: bool,
    counterexample_handling_valid: bool,
    scope_valid: bool,
    no_memory_write_allowed: bool,
    no_memory_write_performed: bool,
    no_memory_application_candidate_allowed: bool,
    no_task_behavior_change_allowed: bool,
    no_task_behavior_changed: bool,
    no_promotion_candidate_allowed: bool,
    no_automatic_learning_approval: bool,
    no_core_longterm_archive_anchor_write: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    forbidden_flags = (
        no_memory_write_allowed,
        no_memory_write_performed,
        no_memory_application_candidate_allowed,
        no_task_behavior_change_allowed,
        no_task_behavior_changed,
        no_promotion_candidate_allowed,
        no_automatic_learning_approval,
        no_core_longterm_archive_anchor_write,
    )
    if not all(forbidden_flags):
        reasons.append("blocked_forbidden_authority_detected")
    if not support_evidence_present:
        reasons.append("blocked_missing_support_evidence")
    if not counterexample_handling_valid:
        reasons.append("blocked_unhandled_counterexamples")
    if not scope_valid:
        reasons.append("blocked_invalid_scope")
    if not preparation_packet_valid:
        reasons.append("blocked_invalid_preparation_packet")
    if not readiness_audit_passed:
        reasons.append("blocked_readiness_audit_failed")
    if not lineage_complete:
        reasons.append("blocked_incomplete_lineage")
    return tuple(dict.fromkeys(reasons))


def _safety_status(blocked_reasons: tuple[str, ...]) -> str:
    if not blocked_reasons:
        return "passed"
    for status in (
        "blocked_forbidden_authority_detected",
        "blocked_missing_support_evidence",
        "blocked_unhandled_counterexamples",
        "blocked_invalid_scope",
        "blocked_invalid_preparation_packet",
        "blocked_readiness_audit_failed",
        "blocked_incomplete_lineage",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_forbidden_authority_detected"


def _unique(values: Any) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(value) for value in values if value))


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return _unique(item for group in groups for item in group)


def _packet(
    packet: ReviewedConceptPreparationPacket | dict[str, object],
) -> ReviewedConceptPreparationPacket:
    return (
        packet
        if isinstance(packet, ReviewedConceptPreparationPacket)
        else ReviewedConceptPreparationPacket.from_dict(dict(packet))
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


def _readiness_audit(
    audit: ReviewedConceptPreparationReadinessAudit | dict[str, object],
) -> ReviewedConceptPreparationReadinessAudit:
    return (
        audit
        if isinstance(audit, ReviewedConceptPreparationReadinessAudit)
        else ReviewedConceptPreparationReadinessAudit.from_dict(dict(audit))
    )


def _reviewed_concept(
    record: ReviewedConceptRecord | dict[str, object],
) -> ReviewedConceptRecord:
    return (
        record
        if isinstance(record, ReviewedConceptRecord)
        else ReviewedConceptRecord.from_dict(dict(record))
    )


def _lineage(
    record: ReviewedConceptLineageRecord | dict[str, object],
) -> ReviewedConceptLineageRecord:
    return (
        record
        if isinstance(record, ReviewedConceptLineageRecord)
        else ReviewedConceptLineageRecord.from_dict(dict(record))
    )


def _safety_audit(
    record: ReviewedConceptSafetyAuditRecord | dict[str, object],
) -> ReviewedConceptSafetyAuditRecord:
    return (
        record
        if isinstance(record, ReviewedConceptSafetyAuditRecord)
        else ReviewedConceptSafetyAuditRecord.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
