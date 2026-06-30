"""Bridge ReviewedConcept memory previews into Memory Engine candidate records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.concept_candidate_schema import SOURCE_ENGINE
from ashl_core_v1.learning.reviewed_concept_record import (
    ReviewedConceptLineageRecord,
    ReviewedConceptRecord,
    ReviewedConceptSafetyAuditRecord,
    build_demo_reviewed_concept_record,
    validate_reviewed_concept_record,
)
from ashl_core_v1.learning.reviewed_concept_to_memory_trace_preview import (
    ReviewedConceptMemoryApplicationDataPreview,
    ReviewedConceptMemoryPreviewSafetyAudit,
    ReviewedConceptMemoryRoutingPreview,
    ReviewedConceptMemoryTracePreview,
    build_demo_blocked_forbidden_target_layer_preview,
    build_demo_blocked_unhandled_counterexample_routing_preview,
    build_demo_held_for_more_evidence_overbroad_scope_preview,
    build_demo_reviewed_concept_memory_preview_bundle,
    build_reviewed_concept_memory_application_data_preview,
    build_reviewed_concept_memory_preview_safety_audit,
    build_reviewed_concept_memory_routing_preview,
    build_reviewed_concept_memory_trace_preview,
    validate_reviewed_concept_memory_application_data_preview,
    validate_reviewed_concept_memory_preview_safety_audit,
    validate_reviewed_concept_memory_routing_preview,
    validate_reviewed_concept_memory_trace_preview,
)


MEMORY_LEARNING_TRACE_CANDIDATE_SCHEMA_VERSION = (
    "learning_engine_reviewed_concept_memory_learning_trace_candidate_v0"
)
MEMORY_ROUTING_TRACE_CANDIDATE_SCHEMA_VERSION = (
    "learning_engine_reviewed_concept_memory_routing_trace_candidate_v0"
)
MEMORY_APPLICATION_DATA_CANDIDATE_SCHEMA_VERSION = (
    "learning_engine_reviewed_concept_memory_application_data_candidate_v0"
)
MEMORY_TRACE_BRIDGE_AUDIT_SCHEMA_VERSION = (
    "learning_engine_reviewed_concept_memory_trace_bridge_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 can convert a valid ReviewedConcept memory preview into "
    "MemoryLearningTrace, MemoryRoutingTrace, and MemoryApplicationData "
    "candidate records for Memory Engine review, without creating actual memory "
    "traces, writing memory layers, creating readback hints, mutating Working "
    "Memory, or changing task behavior."
)
BLOCKED_CLAIMS = (
    "no_actual_memory_learning_trace",
    "no_actual_memory_routing_trace",
    "no_actual_memory_application_data",
    "no_memory_layer_write",
    "no_readback_hint",
    "no_working_memory_mutation",
    "no_task_behavior_change",
    "no_core_longterm_archive_anchor_write",
    "no_automatic_learning_approval",
)

ALLOWED_LEARNING_TRACE_CANDIDATE_STATUSES = {
    "candidate_ready_for_memory_engine_review",
    "blocked_invalid_reviewed_concept",
    "blocked_invalid_trace_preview",
    "blocked_safety_audit_failed",
    "blocked_unhandled_counterexamples",
    "blocked_invalid_scope",
}
ALLOWED_TARGET_LAYER_CANDIDATES = {
    "working_readback_candidate",
    "held_for_more_evidence",
    "blocked_from_routing",
}
ALLOWED_ROUTING_CANDIDATE_STATUSES = {
    "candidate_routed_to_working_readback_review",
    "candidate_held_for_more_evidence",
    "candidate_blocked_from_routing",
    "blocked_invalid_learning_trace_candidate",
    "blocked_invalid_routing_preview",
    "blocked_forbidden_target_layer",
}
ALLOWED_APPLICATION_CANDIDATE_KINDS = {
    "working_memory_hint_candidate",
    "held_for_more_evidence",
    "blocked",
}
ALLOWED_APPLICATION_CANDIDATE_STATUSES = {
    "candidate_ready_for_memory_engine_review",
    "candidate_held_for_more_evidence",
    "candidate_blocked",
    "blocked_invalid_routing_candidate",
    "blocked_invalid_application_preview",
    "blocked_forbidden_readback_or_behavior_flag",
}
ALLOWED_BRIDGE_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_reviewed_concept",
    "blocked_invalid_preview_chain",
    "blocked_invalid_learning_trace_candidate",
    "blocked_invalid_routing_trace_candidate",
    "blocked_invalid_application_data_candidate",
    "blocked_forbidden_memory_write_detected",
    "blocked_forbidden_readback_detected",
    "blocked_forbidden_behavior_change_detected",
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
class ReviewedConceptMemoryLearningTraceCandidate:
    memory_learning_trace_candidate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_reviewed_concept_lineage_id: str
    source_reviewed_concept_safety_audit_id: str
    source_memory_trace_preview_id: str
    source_memory_preview_safety_audit_id: str
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
    candidate_status: str
    candidate_summary: str
    actual_memory_learning_trace_created: bool
    memory_layer_write_performed: bool
    task_behavior_changed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_LEARNING_TRACE_CANDIDATE_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_memory_learning_trace_candidate_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.candidate_status not in ALLOWED_LEARNING_TRACE_CANDIDATE_STATUSES:
            raise ValueError(f"unknown candidate_status: {self.candidate_status}")
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
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptMemoryLearningTraceCandidate":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptMemoryRoutingTraceCandidate:
    memory_routing_trace_candidate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_memory_learning_trace_candidate_id: str
    source_routing_preview_id: str
    target_layer_candidate: str
    routing_reason: str
    routing_candidate_status: str
    allowed_future_memory_trace: bool
    allowed_future_working_readback_candidate: bool
    allowed_core_memory_write: bool
    allowed_long_term_memory_write: bool
    allowed_archive_memory_write: bool
    allowed_anchor_write: bool
    requires_memory_engine_review: bool
    requires_teacher_review_before_memory_write: bool
    requires_counterexample_monitoring: bool
    requires_more_support_before_promotion: bool
    actual_memory_routing_trace_created: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_ROUTING_TRACE_CANDIDATE_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_memory_routing_trace_candidate_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.target_layer_candidate not in ALLOWED_TARGET_LAYER_CANDIDATES:
            raise ValueError(f"unknown target_layer_candidate: {self.target_layer_candidate}")
        if self.routing_candidate_status not in ALLOWED_ROUTING_CANDIDATE_STATUSES:
            raise ValueError(
                f"unknown routing_candidate_status: {self.routing_candidate_status}"
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
    ) -> "ReviewedConceptMemoryRoutingTraceCandidate":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptMemoryApplicationDataCandidate:
    memory_application_data_candidate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_memory_learning_trace_candidate_id: str
    source_memory_routing_trace_candidate_id: str
    source_application_data_preview_id: str
    concept_label: str
    application_summary: str
    application_candidate_kind: str
    suggested_working_memory_hint_labels: tuple[str, ...]
    suggested_task_handling_notes: tuple[str, ...]
    candidate_status: str
    actual_memory_application_data_created: bool
    readback_hint_created: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_APPLICATION_DATA_CANDIDATE_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_memory_application_data_candidate_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.application_candidate_kind not in ALLOWED_APPLICATION_CANDIDATE_KINDS:
            raise ValueError(
                f"unknown application_candidate_kind: {self.application_candidate_kind}"
            )
        if self.candidate_status not in ALLOWED_APPLICATION_CANDIDATE_STATUSES:
            raise ValueError(f"unknown candidate_status: {self.candidate_status}")
        for name in (
            "suggested_working_memory_hint_labels",
            "suggested_task_handling_notes",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptMemoryApplicationDataCandidate":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptMemoryTraceBridgeAudit:
    bridge_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_memory_trace_preview_id: str
    source_routing_preview_id: str
    source_application_data_preview_id: str | None
    memory_learning_trace_candidate_id: str | None
    memory_routing_trace_candidate_id: str | None
    memory_application_data_candidate_id: str | None
    reviewed_concept_valid: bool
    preview_chain_valid: bool
    learning_trace_candidate_valid: bool
    routing_trace_candidate_valid: bool
    application_data_candidate_valid: bool
    no_actual_memory_learning_trace: bool
    no_actual_memory_routing_trace: bool
    no_actual_memory_application_data: bool
    no_memory_layer_write: bool
    no_readback_hint_created: bool
    no_working_memory_mutation: bool
    no_task_behavior_change: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_automatic_learning_approval: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_TRACE_BRIDGE_AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_memory_trace_bridge_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.audit_status not in ALLOWED_BRIDGE_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptMemoryTraceBridgeAudit":
        return cls(**dict(data))


def build_reviewed_concept_memory_learning_trace_candidate(
    *,
    reviewed_concept: ReviewedConceptRecord | dict[str, object],
    lineage_record: ReviewedConceptLineageRecord | dict[str, object],
    reviewed_concept_safety_audit: ReviewedConceptSafetyAuditRecord | dict[str, object],
    memory_trace_preview: ReviewedConceptMemoryTracePreview | dict[str, object],
    memory_preview_safety_audit: ReviewedConceptMemoryPreviewSafetyAudit
    | dict[str, object],
) -> ReviewedConceptMemoryLearningTraceCandidate:
    concept = _reviewed_concept(reviewed_concept)
    lineage = _lineage(lineage_record)
    reviewed_safety = _reviewed_safety(reviewed_concept_safety_audit)
    trace = _trace_preview(memory_trace_preview)
    preview_safety = _preview_safety(memory_preview_safety_audit)
    status = _learning_candidate_status(concept, trace, preview_safety)
    return ReviewedConceptMemoryLearningTraceCandidate(
        memory_learning_trace_candidate_id=f"reviewed_concept_memory_learning_trace_candidate:{concept.reviewed_concept_id}",
        schema_version=MEMORY_LEARNING_TRACE_CANDIDATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=concept.reviewed_concept_id,
        source_reviewed_concept_lineage_id=lineage.lineage_id,
        source_reviewed_concept_safety_audit_id=reviewed_safety.safety_audit_id,
        source_memory_trace_preview_id=trace.memory_trace_preview_id,
        source_memory_preview_safety_audit_id=preview_safety.safety_audit_id,
        concept_label=concept.concept_label,
        concept_summary=concept.concept_summary,
        source_task_ids=lineage.source_task_ids,
        source_case_ids=lineage.source_case_ids,
        source_state_action_outcome_refs=lineage.source_state_action_outcome_refs,
        support_evidence_refs=trace.support_evidence_refs,
        counterexample_evidence_refs=trace.counterexample_evidence_refs,
        scope_text=trace.scope_text,
        generalization_level=trace.generalization_level,
        counterexample_handling_status=trace.counterexample_handling_status,
        candidate_status=status,
        candidate_summary=(
            "ReviewedConcept is ready as a MemoryLearningTrace candidate for Memory Engine review."
            if status == "candidate_ready_for_memory_engine_review"
            else f"MemoryLearningTrace candidate blocked: {status}."
        ),
        actual_memory_learning_trace_created=False,
        memory_layer_write_performed=False,
        task_behavior_changed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_combined_trace_refs(
            concept.source_trace_refs,
            lineage.source_trace_refs,
            trace.source_trace_refs,
        ),
    )


def validate_reviewed_concept_memory_learning_trace_candidate(
    candidate: ReviewedConceptMemoryLearningTraceCandidate | dict[str, object],
) -> dict[str, object]:
    try:
        record = _learning_candidate(candidate)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_learning_trace_candidate:{error}"]}
    errors: list[str] = []
    if record.candidate_status != "candidate_ready_for_memory_engine_review":
        errors.append(record.candidate_status)
    if not record.source_reviewed_concept_id:
        errors.append("missing_reviewed_concept_id")
    if not record.source_memory_trace_preview_id:
        errors.append("missing_trace_preview_id")
    if not record.support_evidence_refs:
        errors.append("missing_support_evidence_refs")
    for flag in (
        "actual_memory_learning_trace_created",
        "memory_layer_write_performed",
        "task_behavior_changed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "memory_learning_trace_candidate_id": record.memory_learning_trace_candidate_id,
        "candidate_status": record.candidate_status,
        "actual_memory_learning_trace_created": (
            record.actual_memory_learning_trace_created
        ),
        "memory_layer_write_performed": record.memory_layer_write_performed,
    }


def build_reviewed_concept_memory_routing_trace_candidate(
    *,
    memory_learning_trace_candidate: ReviewedConceptMemoryLearningTraceCandidate
    | dict[str, object],
    routing_preview: ReviewedConceptMemoryRoutingPreview | dict[str, object],
) -> ReviewedConceptMemoryRoutingTraceCandidate:
    learning = _learning_candidate(memory_learning_trace_candidate)
    routing = _routing_preview(routing_preview)
    status = _routing_candidate_status(learning, routing)
    target = (
        routing.target_layer_preview
        if routing.target_layer_preview in ALLOWED_TARGET_LAYER_CANDIDATES
        else "blocked_from_routing"
    )
    return ReviewedConceptMemoryRoutingTraceCandidate(
        memory_routing_trace_candidate_id=f"reviewed_concept_memory_routing_trace_candidate:{learning.source_reviewed_concept_id}",
        schema_version=MEMORY_ROUTING_TRACE_CANDIDATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=learning.source_reviewed_concept_id,
        source_memory_learning_trace_candidate_id=learning.memory_learning_trace_candidate_id,
        source_routing_preview_id=routing.routing_preview_id,
        target_layer_candidate=target,
        routing_reason=routing.routing_reason,
        routing_candidate_status=status,
        allowed_future_memory_trace=routing.allowed_future_memory_trace,
        allowed_future_working_readback_candidate=(
            routing.allowed_future_working_readback_candidate
        ),
        allowed_core_memory_write=False,
        allowed_long_term_memory_write=False,
        allowed_archive_memory_write=False,
        allowed_anchor_write=False,
        requires_memory_engine_review=True,
        requires_teacher_review_before_memory_write=True,
        requires_counterexample_monitoring=True,
        requires_more_support_before_promotion=True,
        actual_memory_routing_trace_created=False,
        memory_layer_write_performed=False,
        source_trace_refs=_combined_trace_refs(
            learning.source_trace_refs,
            routing.source_trace_refs,
        ),
    )


def validate_reviewed_concept_memory_routing_trace_candidate(
    candidate: ReviewedConceptMemoryRoutingTraceCandidate | dict[str, object],
) -> dict[str, object]:
    try:
        record = _routing_candidate(candidate)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_routing_trace_candidate:{error}"]}
    errors: list[str] = []
    if record.routing_candidate_status.startswith("blocked_"):
        errors.append(record.routing_candidate_status)
    for flag in (
        "allowed_core_memory_write",
        "allowed_long_term_memory_write",
        "allowed_archive_memory_write",
        "allowed_anchor_write",
        "actual_memory_routing_trace_created",
        "memory_layer_write_performed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    for flag in (
        "requires_memory_engine_review",
        "requires_teacher_review_before_memory_write",
        "requires_counterexample_monitoring",
        "requires_more_support_before_promotion",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "memory_routing_trace_candidate_id": record.memory_routing_trace_candidate_id,
        "target_layer_candidate": record.target_layer_candidate,
        "routing_candidate_status": record.routing_candidate_status,
    }


def build_reviewed_concept_memory_application_data_candidate(
    *,
    memory_learning_trace_candidate: ReviewedConceptMemoryLearningTraceCandidate
    | dict[str, object],
    memory_routing_trace_candidate: ReviewedConceptMemoryRoutingTraceCandidate
    | dict[str, object],
    application_data_preview: ReviewedConceptMemoryApplicationDataPreview
    | dict[str, object],
) -> ReviewedConceptMemoryApplicationDataCandidate:
    learning = _learning_candidate(memory_learning_trace_candidate)
    routing = _routing_candidate(memory_routing_trace_candidate)
    application_preview = _application_preview(application_data_preview)
    kind, status = _application_candidate_kind_and_status(routing, application_preview)
    return ReviewedConceptMemoryApplicationDataCandidate(
        memory_application_data_candidate_id=f"reviewed_concept_memory_application_data_candidate:{learning.source_reviewed_concept_id}",
        schema_version=MEMORY_APPLICATION_DATA_CANDIDATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=learning.source_reviewed_concept_id,
        source_memory_learning_trace_candidate_id=learning.memory_learning_trace_candidate_id,
        source_memory_routing_trace_candidate_id=routing.memory_routing_trace_candidate_id,
        source_application_data_preview_id=application_preview.application_data_preview_id,
        concept_label=application_preview.concept_label,
        application_summary=application_preview.application_summary,
        application_candidate_kind=kind,
        suggested_working_memory_hint_labels=(
            application_preview.suggested_working_memory_hint_labels
        ),
        suggested_task_handling_notes=application_preview.suggested_task_handling_notes,
        candidate_status=status,
        actual_memory_application_data_created=False,
        readback_hint_created=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        memory_layer_write_performed=False,
        source_trace_refs=_combined_trace_refs(
            learning.source_trace_refs,
            routing.source_trace_refs,
            application_preview.source_trace_refs,
        ),
    )


def validate_reviewed_concept_memory_application_data_candidate(
    candidate: ReviewedConceptMemoryApplicationDataCandidate | dict[str, object],
) -> dict[str, object]:
    try:
        record = _application_candidate(candidate)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_application_data_candidate:{error}"]}
    errors: list[str] = []
    if record.candidate_status.startswith("blocked_"):
        errors.append(record.candidate_status)
    if (
        record.application_candidate_kind == "working_memory_hint_candidate"
        and not record.suggested_working_memory_hint_labels
    ):
        errors.append("missing_hint_labels")
    for flag in (
        "actual_memory_application_data_created",
        "readback_hint_created",
        "working_memory_mutated",
        "task_behavior_changed",
        "memory_layer_write_performed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "memory_application_data_candidate_id": (
            record.memory_application_data_candidate_id
        ),
        "application_candidate_kind": record.application_candidate_kind,
        "candidate_status": record.candidate_status,
        "actual_memory_application_data_created": (
            record.actual_memory_application_data_created
        ),
        "readback_hint_created": record.readback_hint_created,
        "working_memory_mutated": record.working_memory_mutated,
        "task_behavior_changed": record.task_behavior_changed,
    }


def build_reviewed_concept_memory_trace_bridge_audit(
    *,
    reviewed_concept: ReviewedConceptRecord | dict[str, object],
    memory_trace_preview: ReviewedConceptMemoryTracePreview | dict[str, object],
    routing_preview: ReviewedConceptMemoryRoutingPreview | dict[str, object],
    application_data_preview: ReviewedConceptMemoryApplicationDataPreview
    | dict[str, object]
    | None,
    memory_learning_trace_candidate: ReviewedConceptMemoryLearningTraceCandidate
    | dict[str, object],
    memory_routing_trace_candidate: ReviewedConceptMemoryRoutingTraceCandidate
    | dict[str, object],
    memory_application_data_candidate: ReviewedConceptMemoryApplicationDataCandidate
    | dict[str, object]
    | None,
    memory_preview_safety_audit: ReviewedConceptMemoryPreviewSafetyAudit
    | dict[str, object],
) -> ReviewedConceptMemoryTraceBridgeAudit:
    concept = _reviewed_concept(reviewed_concept)
    trace = _trace_preview(memory_trace_preview)
    routing = _routing_preview(routing_preview)
    application_preview = (
        _application_preview(application_data_preview)
        if application_data_preview is not None
        else None
    )
    learning_candidate = _learning_candidate(memory_learning_trace_candidate)
    routing_candidate = _routing_candidate(memory_routing_trace_candidate)
    application_candidate = (
        _application_candidate(memory_application_data_candidate)
        if memory_application_data_candidate is not None
        else None
    )
    preview_safety = _preview_safety(memory_preview_safety_audit)
    reviewed_concept_valid = bool(validate_reviewed_concept_record(concept)["valid"])
    preview_chain_valid = _preview_chain_valid(trace, routing, preview_safety)
    learning_trace_candidate_valid = bool(
        validate_reviewed_concept_memory_learning_trace_candidate(learning_candidate)[
            "valid"
        ]
    )
    routing_trace_candidate_valid = bool(
        validate_reviewed_concept_memory_routing_trace_candidate(routing_candidate)[
            "valid"
        ]
    )
    application_data_candidate_valid = (
        application_candidate is not None
        and bool(
            validate_reviewed_concept_memory_application_data_candidate(
                application_candidate
            )["valid"]
        )
    )
    no_actual_memory_learning_trace = (
        learning_candidate.actual_memory_learning_trace_created is False
    )
    no_actual_memory_routing_trace = (
        routing_candidate.actual_memory_routing_trace_created is False
    )
    no_actual_memory_application_data = (
        application_candidate is None
        or application_candidate.actual_memory_application_data_created is False
    )
    no_memory_layer_write = (
        learning_candidate.memory_layer_write_performed is False
        and routing_candidate.memory_layer_write_performed is False
        and (
            application_candidate is None
            or application_candidate.memory_layer_write_performed is False
        )
    )
    no_readback_hint_created = (
        application_candidate is None
        or application_candidate.readback_hint_created is False
    )
    no_working_memory_mutation = (
        application_candidate is None
        or application_candidate.working_memory_mutated is False
    )
    no_task_behavior_change = (
        learning_candidate.task_behavior_changed is False
        and (
            application_candidate is None
            or application_candidate.task_behavior_changed is False
        )
    )
    no_core_memory_write = routing_candidate.allowed_core_memory_write is False
    no_long_term_memory_write = routing_candidate.allowed_long_term_memory_write is False
    no_archive_memory_write = routing_candidate.allowed_archive_memory_write is False
    no_anchor_write = routing_candidate.allowed_anchor_write is False
    no_automatic_learning_approval = (
        learning_candidate.automatic_learning_approval_created is False
    )
    blocked_reasons = _bridge_blocked_reasons(
        reviewed_concept_valid=reviewed_concept_valid,
        preview_chain_valid=preview_chain_valid,
        learning_trace_candidate_valid=learning_trace_candidate_valid,
        routing_trace_candidate_valid=routing_trace_candidate_valid,
        application_data_candidate_valid=application_data_candidate_valid,
        no_actual_memory_learning_trace=no_actual_memory_learning_trace,
        no_actual_memory_routing_trace=no_actual_memory_routing_trace,
        no_actual_memory_application_data=no_actual_memory_application_data,
        no_memory_layer_write=no_memory_layer_write,
        no_readback_hint_created=no_readback_hint_created,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_core_memory_write=no_core_memory_write,
        no_long_term_memory_write=no_long_term_memory_write,
        no_archive_memory_write=no_archive_memory_write,
        no_anchor_write=no_anchor_write,
        no_automatic_learning_approval=no_automatic_learning_approval,
    )
    return ReviewedConceptMemoryTraceBridgeAudit(
        bridge_audit_id=f"reviewed_concept_memory_trace_bridge_audit:{concept.reviewed_concept_id}",
        schema_version=MEMORY_TRACE_BRIDGE_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=concept.reviewed_concept_id,
        source_memory_trace_preview_id=trace.memory_trace_preview_id,
        source_routing_preview_id=routing.routing_preview_id,
        source_application_data_preview_id=(
            application_preview.application_data_preview_id
            if application_preview is not None
            else None
        ),
        memory_learning_trace_candidate_id=(
            learning_candidate.memory_learning_trace_candidate_id
        ),
        memory_routing_trace_candidate_id=(
            routing_candidate.memory_routing_trace_candidate_id
        ),
        memory_application_data_candidate_id=(
            application_candidate.memory_application_data_candidate_id
            if application_candidate is not None
            else None
        ),
        reviewed_concept_valid=reviewed_concept_valid,
        preview_chain_valid=preview_chain_valid,
        learning_trace_candidate_valid=learning_trace_candidate_valid,
        routing_trace_candidate_valid=routing_trace_candidate_valid,
        application_data_candidate_valid=application_data_candidate_valid,
        no_actual_memory_learning_trace=no_actual_memory_learning_trace,
        no_actual_memory_routing_trace=no_actual_memory_routing_trace,
        no_actual_memory_application_data=no_actual_memory_application_data,
        no_memory_layer_write=no_memory_layer_write,
        no_readback_hint_created=no_readback_hint_created,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_core_memory_write=no_core_memory_write,
        no_long_term_memory_write=no_long_term_memory_write,
        no_archive_memory_write=no_archive_memory_write,
        no_anchor_write=no_anchor_write,
        no_automatic_learning_approval=no_automatic_learning_approval,
        audit_status=_bridge_audit_status(blocked_reasons),
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=blocked_reasons,
        source_trace_refs=_combined_trace_refs(
            concept.source_trace_refs,
            trace.source_trace_refs,
            routing.source_trace_refs,
            learning_candidate.source_trace_refs,
            routing_candidate.source_trace_refs,
            application_candidate.source_trace_refs if application_candidate else (),
        ),
    )


def validate_reviewed_concept_memory_trace_bridge_audit(
    audit: ReviewedConceptMemoryTraceBridgeAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _bridge_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_bridge_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed":
        errors.append(record.audit_status)
    for name in (
        "reviewed_concept_valid",
        "preview_chain_valid",
        "learning_trace_candidate_valid",
        "routing_trace_candidate_valid",
        "application_data_candidate_valid",
        "no_actual_memory_learning_trace",
        "no_actual_memory_routing_trace",
        "no_actual_memory_application_data",
        "no_memory_layer_write",
        "no_readback_hint_created",
        "no_working_memory_mutation",
        "no_task_behavior_change",
        "no_core_memory_write",
        "no_long_term_memory_write",
        "no_archive_memory_write",
        "no_anchor_write",
        "no_automatic_learning_approval",
    ):
        if getattr(record, name) is not True:
            errors.append(f"{name}_false")
    if not set(BLOCKED_CLAIMS).issubset(set(record.blocked_claims)):
        errors.append("blocked_claims_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "bridge_audit_id": record.bridge_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_reviewed_concept_memory_trace_bridge(
    *,
    reviewed_concept_payload: dict[str, object],
    preview_payload: dict[str, object],
) -> dict[str, object]:
    concept = _reviewed_concept(reviewed_concept_payload["reviewed_concept"])
    lineage = _lineage(reviewed_concept_payload["lineage_record"])
    reviewed_safety = _reviewed_safety(reviewed_concept_payload["safety_audit"])
    trace = _trace_preview(preview_payload["memory_trace_preview"])
    routing = _routing_preview(preview_payload["routing_preview"])
    application_preview = _application_preview(preview_payload["application_data_preview"])
    preview_safety = _preview_safety(preview_payload["preview_safety_audit"])
    learning_candidate = build_reviewed_concept_memory_learning_trace_candidate(
        reviewed_concept=concept,
        lineage_record=lineage,
        reviewed_concept_safety_audit=reviewed_safety,
        memory_trace_preview=trace,
        memory_preview_safety_audit=preview_safety,
    )
    routing_candidate = build_reviewed_concept_memory_routing_trace_candidate(
        memory_learning_trace_candidate=learning_candidate,
        routing_preview=routing,
    )
    application_candidate = build_reviewed_concept_memory_application_data_candidate(
        memory_learning_trace_candidate=learning_candidate,
        memory_routing_trace_candidate=routing_candidate,
        application_data_preview=application_preview,
    )
    audit = build_reviewed_concept_memory_trace_bridge_audit(
        reviewed_concept=concept,
        memory_trace_preview=trace,
        routing_preview=routing,
        application_data_preview=application_preview,
        memory_learning_trace_candidate=learning_candidate,
        memory_routing_trace_candidate=routing_candidate,
        memory_application_data_candidate=application_candidate,
        memory_preview_safety_audit=preview_safety,
    )
    return {
        "memory_learning_trace_candidate": learning_candidate.to_dict(),
        "memory_routing_trace_candidate": routing_candidate.to_dict(),
        "memory_application_data_candidate": application_candidate.to_dict(),
        "bridge_audit": audit.to_dict(),
        "learning_trace_candidate_validation": (
            validate_reviewed_concept_memory_learning_trace_candidate(
                learning_candidate
            )
        ),
        "routing_trace_candidate_validation": (
            validate_reviewed_concept_memory_routing_trace_candidate(
                routing_candidate
            )
        ),
        "application_data_candidate_validation": (
            validate_reviewed_concept_memory_application_data_candidate(
                application_candidate
            )
        ),
        "bridge_audit_validation": validate_reviewed_concept_memory_trace_bridge_audit(
            audit
        ),
        "safe_claim": SAFE_CLAIM,
    }


def build_demo_reviewed_concept_memory_trace_bridge() -> dict[str, object]:
    return build_reviewed_concept_memory_trace_bridge(
        reviewed_concept_payload=build_demo_reviewed_concept_record(),
        preview_payload=build_demo_reviewed_concept_memory_preview_bundle(),
    )


def build_demo_held_for_more_evidence_bridge() -> dict[str, object]:
    concept_payload = build_demo_reviewed_concept_record()
    trace = build_reviewed_concept_memory_trace_preview(
        reviewed_concept=concept_payload["reviewed_concept"],
        lineage_record=concept_payload["lineage_record"],
        reviewed_concept_safety_audit=concept_payload["safety_audit"],
    )
    routing = build_demo_held_for_more_evidence_overbroad_scope_preview()
    application = build_reviewed_concept_memory_application_data_preview(
        reviewed_concept=concept_payload["reviewed_concept"],
        memory_trace_preview=trace,
        routing_preview=routing,
    )
    preview_safety = build_reviewed_concept_memory_preview_safety_audit(
        reviewed_concept=concept_payload["reviewed_concept"],
        memory_trace_preview=trace,
        routing_preview=routing,
        application_data_preview=application,
    )
    return build_reviewed_concept_memory_trace_bridge(
        reviewed_concept_payload=concept_payload,
        preview_payload={
            "memory_trace_preview": trace.to_dict(),
            "routing_preview": routing.to_dict(),
            "application_data_preview": application.to_dict(),
            "preview_safety_audit": preview_safety.to_dict(),
        },
    )


def build_demo_blocked_from_routing_bridge() -> dict[str, object]:
    concept_payload = build_demo_reviewed_concept_record()
    trace = build_reviewed_concept_memory_trace_preview(
        reviewed_concept=concept_payload["reviewed_concept"],
        lineage_record=concept_payload["lineage_record"],
        reviewed_concept_safety_audit=concept_payload["safety_audit"],
    )
    routing = build_demo_blocked_unhandled_counterexample_routing_preview()
    application = build_reviewed_concept_memory_application_data_preview(
        reviewed_concept=concept_payload["reviewed_concept"],
        memory_trace_preview=trace,
        routing_preview=routing,
    )
    preview_safety = build_reviewed_concept_memory_preview_safety_audit(
        reviewed_concept=concept_payload["reviewed_concept"],
        memory_trace_preview=trace,
        routing_preview=routing,
        application_data_preview=application,
    )
    return build_reviewed_concept_memory_trace_bridge(
        reviewed_concept_payload=concept_payload,
        preview_payload={
            "memory_trace_preview": trace.to_dict(),
            "routing_preview": routing.to_dict(),
            "application_data_preview": application.to_dict(),
            "preview_safety_audit": preview_safety.to_dict(),
        },
    )


def build_demo_blocked_forbidden_target_layer_bridge() -> dict[str, object]:
    concept_payload = build_demo_reviewed_concept_record()
    trace = build_reviewed_concept_memory_trace_preview(
        reviewed_concept=concept_payload["reviewed_concept"],
        lineage_record=concept_payload["lineage_record"],
        reviewed_concept_safety_audit=concept_payload["safety_audit"],
    )
    routing = build_demo_blocked_forbidden_target_layer_preview()
    application = build_reviewed_concept_memory_application_data_preview(
        reviewed_concept=concept_payload["reviewed_concept"],
        memory_trace_preview=trace,
        routing_preview=routing,
    )
    preview_safety = build_reviewed_concept_memory_preview_safety_audit(
        reviewed_concept=concept_payload["reviewed_concept"],
        memory_trace_preview=trace,
        routing_preview=routing,
        application_data_preview=application,
    )
    return build_reviewed_concept_memory_trace_bridge(
        reviewed_concept_payload=concept_payload,
        preview_payload={
            "memory_trace_preview": trace.to_dict(),
            "routing_preview": routing.to_dict(),
            "application_data_preview": application.to_dict(),
            "preview_safety_audit": preview_safety.to_dict(),
        },
    )


def build_demo_blocked_forbidden_memory_write_bridge() -> dict[str, object]:
    payload = build_demo_reviewed_concept_memory_trace_bridge()
    learning_data = dict(payload["memory_learning_trace_candidate"])
    learning_data["memory_layer_write_performed"] = True
    learning_candidate = ReviewedConceptMemoryLearningTraceCandidate.from_dict(
        learning_data
    )
    concept_payload = build_demo_reviewed_concept_record()
    preview_payload = build_demo_reviewed_concept_memory_preview_bundle()
    routing_candidate = ReviewedConceptMemoryRoutingTraceCandidate.from_dict(
        payload["memory_routing_trace_candidate"]
    )
    application_candidate = ReviewedConceptMemoryApplicationDataCandidate.from_dict(
        payload["memory_application_data_candidate"]
    )
    audit = build_reviewed_concept_memory_trace_bridge_audit(
        reviewed_concept=concept_payload["reviewed_concept"],
        memory_trace_preview=preview_payload["memory_trace_preview"],
        routing_preview=preview_payload["routing_preview"],
        application_data_preview=preview_payload["application_data_preview"],
        memory_learning_trace_candidate=learning_candidate,
        memory_routing_trace_candidate=routing_candidate,
        memory_application_data_candidate=application_candidate,
        memory_preview_safety_audit=preview_payload["preview_safety_audit"],
    )
    return {
        **payload,
        "memory_learning_trace_candidate": learning_candidate.to_dict(),
        "bridge_audit": audit.to_dict(),
        "bridge_audit_validation": validate_reviewed_concept_memory_trace_bridge_audit(
            audit
        ),
    }


def build_demo_blocked_bridge(case: str) -> dict[str, object]:
    cases = {
        "forbidden-target-layer": build_demo_blocked_forbidden_target_layer_bridge,
        "forbidden-memory-write": build_demo_blocked_forbidden_memory_write_bridge,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked bridge case: {case}") from error


def _learning_candidate_status(
    concept: ReviewedConceptRecord,
    trace: ReviewedConceptMemoryTracePreview,
    preview_safety: ReviewedConceptMemoryPreviewSafetyAudit,
) -> str:
    if not validate_reviewed_concept_record(concept)["valid"]:
        if concept.review_status == "blocked_unhandled_counterexamples":
            return "blocked_unhandled_counterexamples"
        if concept.review_status == "blocked_invalid_scope":
            return "blocked_invalid_scope"
        return "blocked_invalid_reviewed_concept"
    if trace.trace_preview_status == "blocked_unhandled_counterexamples":
        return "blocked_unhandled_counterexamples"
    if trace.trace_preview_status == "blocked_invalid_scope":
        return "blocked_invalid_scope"
    if trace.trace_preview_status != "preview_ready":
        return "blocked_invalid_trace_preview"
    if preview_safety.audit_status != "passed":
        return "blocked_safety_audit_failed"
    return "candidate_ready_for_memory_engine_review"


def _routing_candidate_status(
    learning: ReviewedConceptMemoryLearningTraceCandidate,
    routing: ReviewedConceptMemoryRoutingPreview,
) -> str:
    if routing.routing_status == "blocked_forbidden_target_layer":
        return "blocked_forbidden_target_layer"
    if routing.routing_status == "blocked_invalid_memory_trace_preview":
        return "blocked_invalid_routing_preview"
    if routing.routing_status == "preview_held_for_more_evidence":
        return "candidate_held_for_more_evidence"
    if routing.routing_status == "preview_blocked_from_routing":
        return "candidate_blocked_from_routing"
    if learning.candidate_status != "candidate_ready_for_memory_engine_review":
        return "blocked_invalid_learning_trace_candidate"
    if routing.routing_status == "preview_routed_to_working_readback_candidate":
        return "candidate_routed_to_working_readback_review"
    return "blocked_invalid_routing_preview"


def _application_candidate_kind_and_status(
    routing: ReviewedConceptMemoryRoutingTraceCandidate,
    application_preview: ReviewedConceptMemoryApplicationDataPreview,
) -> tuple[str, str]:
    if (
        application_preview.actual_memory_application_data_created
        or application_preview.readback_hint_created
        or application_preview.working_memory_mutated
        or application_preview.task_behavior_changed
    ):
        return "blocked", "blocked_forbidden_readback_or_behavior_flag"
    if routing.routing_candidate_status == "candidate_routed_to_working_readback_review":
        return "working_memory_hint_candidate", "candidate_ready_for_memory_engine_review"
    if routing.routing_candidate_status == "candidate_held_for_more_evidence":
        return "held_for_more_evidence", "candidate_held_for_more_evidence"
    if routing.routing_candidate_status == "candidate_blocked_from_routing":
        return "blocked", "candidate_blocked"
    if routing.routing_candidate_status.startswith("blocked_"):
        return "blocked", "blocked_invalid_routing_candidate"
    if not validate_reviewed_concept_memory_application_data_preview(application_preview)["valid"]:
        return "blocked", "blocked_invalid_application_preview"
    return "blocked", "blocked_invalid_application_preview"


def _preview_chain_valid(
    trace: ReviewedConceptMemoryTracePreview,
    routing: ReviewedConceptMemoryRoutingPreview,
    preview_safety: ReviewedConceptMemoryPreviewSafetyAudit,
) -> bool:
    return (
        trace.trace_preview_status == "preview_ready"
        and routing.routing_status
        in {
            "preview_routed_to_working_readback_candidate",
            "preview_held_for_more_evidence",
            "preview_blocked_from_routing",
        }
        and preview_safety.audit_status == "passed"
    )


def _bridge_blocked_reasons(
    *,
    reviewed_concept_valid: bool,
    preview_chain_valid: bool,
    learning_trace_candidate_valid: bool,
    routing_trace_candidate_valid: bool,
    application_data_candidate_valid: bool,
    no_actual_memory_learning_trace: bool,
    no_actual_memory_routing_trace: bool,
    no_actual_memory_application_data: bool,
    no_memory_layer_write: bool,
    no_readback_hint_created: bool,
    no_working_memory_mutation: bool,
    no_task_behavior_change: bool,
    no_core_memory_write: bool,
    no_long_term_memory_write: bool,
    no_archive_memory_write: bool,
    no_anchor_write: bool,
    no_automatic_learning_approval: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not (
        no_actual_memory_learning_trace
        and no_actual_memory_routing_trace
        and no_actual_memory_application_data
        and no_memory_layer_write
        and no_core_memory_write
        and no_long_term_memory_write
        and no_archive_memory_write
        and no_anchor_write
    ):
        reasons.append("blocked_forbidden_memory_write_detected")
    if not (no_readback_hint_created and no_working_memory_mutation):
        reasons.append("blocked_forbidden_readback_detected")
    if not no_task_behavior_change:
        reasons.append("blocked_forbidden_behavior_change_detected")
    if not no_automatic_learning_approval:
        reasons.append("blocked_forbidden_memory_write_detected")
    if not reviewed_concept_valid:
        reasons.append("blocked_invalid_reviewed_concept")
    if not preview_chain_valid:
        reasons.append("blocked_invalid_preview_chain")
    if not learning_trace_candidate_valid:
        reasons.append("blocked_invalid_learning_trace_candidate")
    if not routing_trace_candidate_valid:
        reasons.append("blocked_invalid_routing_trace_candidate")
    if not application_data_candidate_valid:
        reasons.append("blocked_invalid_application_data_candidate")
    return tuple(dict.fromkeys(reasons))


def _bridge_audit_status(blocked_reasons: tuple[str, ...]) -> str:
    if not blocked_reasons:
        return "passed"
    for status in (
        "blocked_forbidden_memory_write_detected",
        "blocked_forbidden_readback_detected",
        "blocked_forbidden_behavior_change_detected",
        "blocked_invalid_reviewed_concept",
        "blocked_invalid_preview_chain",
        "blocked_invalid_learning_trace_candidate",
        "blocked_invalid_routing_trace_candidate",
        "blocked_invalid_application_data_candidate",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_invalid_preview_chain"


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


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


def _reviewed_safety(
    record: ReviewedConceptSafetyAuditRecord | dict[str, object],
) -> ReviewedConceptSafetyAuditRecord:
    return (
        record
        if isinstance(record, ReviewedConceptSafetyAuditRecord)
        else ReviewedConceptSafetyAuditRecord.from_dict(dict(record))
    )


def _trace_preview(
    record: ReviewedConceptMemoryTracePreview | dict[str, object],
) -> ReviewedConceptMemoryTracePreview:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryTracePreview)
        else ReviewedConceptMemoryTracePreview.from_dict(dict(record))
    )


def _routing_preview(
    record: ReviewedConceptMemoryRoutingPreview | dict[str, object],
) -> ReviewedConceptMemoryRoutingPreview:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryRoutingPreview)
        else ReviewedConceptMemoryRoutingPreview.from_dict(dict(record))
    )


def _application_preview(
    record: ReviewedConceptMemoryApplicationDataPreview | dict[str, object],
) -> ReviewedConceptMemoryApplicationDataPreview:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryApplicationDataPreview)
        else ReviewedConceptMemoryApplicationDataPreview.from_dict(dict(record))
    )


def _preview_safety(
    record: ReviewedConceptMemoryPreviewSafetyAudit | dict[str, object],
) -> ReviewedConceptMemoryPreviewSafetyAudit:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryPreviewSafetyAudit)
        else ReviewedConceptMemoryPreviewSafetyAudit.from_dict(dict(record))
    )


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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
