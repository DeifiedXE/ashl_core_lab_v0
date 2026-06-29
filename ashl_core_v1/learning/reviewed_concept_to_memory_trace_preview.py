"""Preview ReviewedConcept routing toward Memory Engine without writing memory."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.concept_candidate_schema import SOURCE_ENGINE
from ashl_core_v1.learning.reviewed_concept_record import (
    ReviewedConceptLineageRecord,
    ReviewedConceptRecord,
    ReviewedConceptSafetyAuditRecord,
    build_demo_blocked_invalid_scope,
    build_demo_blocked_unhandled_counterexample,
    build_demo_reviewed_concept_record,
    validate_reviewed_concept_lineage_record,
    validate_reviewed_concept_record,
    validate_reviewed_concept_safety_audit,
)


MEMORY_TRACE_PREVIEW_SCHEMA_VERSION = (
    "learning_engine_reviewed_concept_memory_trace_preview_v0"
)
MEMORY_ROUTING_PREVIEW_SCHEMA_VERSION = (
    "learning_engine_reviewed_concept_memory_routing_preview_v0"
)
MEMORY_APPLICATION_DATA_PREVIEW_SCHEMA_VERSION = (
    "learning_engine_reviewed_concept_memory_application_data_preview_v0"
)
MEMORY_PREVIEW_SAFETY_AUDIT_SCHEMA_VERSION = (
    "learning_engine_reviewed_concept_memory_preview_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 can preview how a record-only ReviewedConcept would become "
    "MemoryLearningTrace, MemoryRoutingTrace, and MemoryApplicationData "
    "candidates for conservative Working Memory readback routing, without "
    "creating actual memory traces, writing memory, creating readback hints, "
    "mutating Working Memory, or changing task behavior."
)

ALLOWED_TRACE_PREVIEW_STATUSES = {
    "preview_ready",
    "blocked_invalid_reviewed_concept",
    "blocked_incomplete_lineage",
    "blocked_safety_audit_failed",
    "blocked_unhandled_counterexamples",
    "blocked_invalid_scope",
}
ALLOWED_TARGET_LAYER_PREVIEWS = {
    "working_readback_candidate",
    "held_for_more_evidence",
    "blocked_from_routing",
}
FORBIDDEN_TARGET_LAYER_PREVIEWS = {
    "core_memory",
    "long_term_memory",
    "archive_memory",
    "anchor_layer",
}
ALLOWED_ROUTING_STATUSES = {
    "preview_routed_to_working_readback_candidate",
    "preview_held_for_more_evidence",
    "preview_blocked_from_routing",
    "blocked_invalid_memory_trace_preview",
    "blocked_forbidden_target_layer",
}
ALLOWED_APPLICATION_KINDS = {
    "working_memory_hint_preview",
    "held_for_more_evidence",
    "blocked",
}
ALLOWED_SAFETY_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_reviewed_concept",
    "blocked_invalid_trace_preview",
    "blocked_forbidden_target_layer",
    "blocked_forbidden_memory_write_detected",
    "blocked_forbidden_readback_detected",
    "blocked_forbidden_behavior_change_detected",
}
HANDLED_COUNTEREXAMPLE_STATUSES = {
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
class ReviewedConceptMemoryTracePreview:
    memory_trace_preview_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_reviewed_concept_lineage_id: str
    source_reviewed_concept_safety_audit_id: str
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
    trace_preview_status: str
    trace_preview_summary: str
    actual_memory_learning_trace_created: bool
    memory_write_performed: bool
    task_behavior_changed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_TRACE_PREVIEW_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_memory_trace_preview_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.trace_preview_status not in ALLOWED_TRACE_PREVIEW_STATUSES:
            raise ValueError(f"unknown trace_preview_status: {self.trace_preview_status}")
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
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptMemoryTracePreview":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptMemoryRoutingPreview:
    routing_preview_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_memory_trace_preview_id: str
    target_layer_preview: str
    routing_reason: str
    routing_status: str
    allowed_future_memory_trace: bool
    allowed_future_working_readback_candidate: bool
    allowed_core_memory_write: bool
    allowed_long_term_memory_write: bool
    allowed_archive_memory_write: bool
    allowed_anchor_write: bool
    requires_more_support_before_promotion: bool
    requires_counterexample_monitoring: bool
    requires_teacher_review_before_memory_write: bool
    actual_memory_routing_trace_created: bool
    memory_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_ROUTING_PREVIEW_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_memory_routing_preview_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.target_layer_preview not in ALLOWED_TARGET_LAYER_PREVIEWS:
            raise ValueError(f"unknown target_layer_preview: {self.target_layer_preview}")
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
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptMemoryRoutingPreview":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptMemoryApplicationDataPreview:
    application_data_preview_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_memory_trace_preview_id: str
    source_routing_preview_id: str
    concept_label: str
    application_summary: str
    preview_application_kind: str
    suggested_working_memory_hint_labels: tuple[str, ...]
    suggested_task_handling_notes: tuple[str, ...]
    preview_only: bool
    actual_memory_application_data_created: bool
    readback_hint_created: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_APPLICATION_DATA_PREVIEW_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_memory_application_data_preview_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.preview_application_kind not in ALLOWED_APPLICATION_KINDS:
            raise ValueError(
                f"unknown preview_application_kind: {self.preview_application_kind}"
            )
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
    ) -> "ReviewedConceptMemoryApplicationDataPreview":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptMemoryPreviewSafetyAudit:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_memory_trace_preview_id: str
    source_routing_preview_id: str
    source_application_data_preview_id: str | None
    reviewed_concept_valid: bool
    lineage_complete: bool
    counterexample_handling_valid: bool
    scope_valid: bool
    no_actual_memory_learning_trace: bool
    no_actual_memory_routing_trace: bool
    no_actual_memory_application_data: bool
    no_readback_hint_created: bool
    no_working_memory_mutation: bool
    no_task_behavior_change: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_automatic_learning_approval: bool
    audit_status: str
    blocked_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MEMORY_PREVIEW_SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_reviewed_concept_memory_preview_safety_audit_v0")
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
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptMemoryPreviewSafetyAudit":
        return cls(**dict(data))


def build_reviewed_concept_memory_trace_preview(
    *,
    reviewed_concept: ReviewedConceptRecord | dict[str, object],
    lineage_record: ReviewedConceptLineageRecord | dict[str, object],
    reviewed_concept_safety_audit: ReviewedConceptSafetyAuditRecord | dict[str, object],
) -> ReviewedConceptMemoryTracePreview:
    concept = _reviewed_concept(reviewed_concept)
    lineage = _lineage(lineage_record)
    safety = _reviewed_safety(reviewed_concept_safety_audit)
    status = _trace_preview_status(concept, lineage, safety)
    return ReviewedConceptMemoryTracePreview(
        memory_trace_preview_id=f"reviewed_concept_memory_trace_preview:{concept.reviewed_concept_id}",
        schema_version=MEMORY_TRACE_PREVIEW_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=concept.reviewed_concept_id,
        source_reviewed_concept_lineage_id=lineage.lineage_id,
        source_reviewed_concept_safety_audit_id=safety.safety_audit_id,
        concept_label=concept.concept_label,
        concept_summary=concept.concept_summary,
        source_task_ids=lineage.source_task_ids,
        source_case_ids=lineage.source_case_ids,
        source_state_action_outcome_refs=lineage.source_state_action_outcome_refs,
        support_evidence_refs=concept.support_evidence_refs,
        counterexample_evidence_refs=concept.counterexample_evidence_refs,
        scope_text=concept.scope_text,
        generalization_level=concept.generalization_level,
        counterexample_handling_status=concept.counterexample_handling_status,
        trace_preview_status=status,
        trace_preview_summary=(
            "ReviewedConcept can be previewed as a future memory learning trace candidate."
            if status == "preview_ready"
            else f"ReviewedConcept memory trace preview blocked: {status}."
        ),
        actual_memory_learning_trace_created=False,
        memory_write_performed=False,
        task_behavior_changed=False,
        source_trace_refs=_combined_trace_refs(
            concept.source_trace_refs,
            lineage.source_trace_refs,
        ),
    )


def validate_reviewed_concept_memory_trace_preview(
    preview: ReviewedConceptMemoryTracePreview | dict[str, object],
) -> dict[str, object]:
    try:
        record = _trace_preview(preview)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_trace_preview:{error}"]}
    errors: list[str] = []
    if record.trace_preview_status != "preview_ready":
        errors.append(record.trace_preview_status)
    if not record.source_reviewed_concept_id:
        errors.append("missing_reviewed_concept_id")
    if not record.source_reviewed_concept_lineage_id:
        errors.append("missing_lineage_id")
    if not record.support_evidence_refs:
        errors.append("missing_support_evidence_refs")
    if not record.scope_text:
        errors.append("missing_scope_text")
    for flag in (
        "actual_memory_learning_trace_created",
        "memory_write_performed",
        "task_behavior_changed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "memory_trace_preview_id": record.memory_trace_preview_id,
        "trace_preview_status": record.trace_preview_status,
        "actual_memory_learning_trace_created": (
            record.actual_memory_learning_trace_created
        ),
        "memory_write_performed": record.memory_write_performed,
        "task_behavior_changed": record.task_behavior_changed,
    }


def build_reviewed_concept_memory_routing_preview(
    *,
    memory_trace_preview: ReviewedConceptMemoryTracePreview | dict[str, object],
    requested_target_layer_preview: str | None = None,
) -> ReviewedConceptMemoryRoutingPreview:
    trace = _trace_preview(memory_trace_preview)
    target, status, reason = _routing_decision(trace, requested_target_layer_preview)
    allowed_working = status == "preview_routed_to_working_readback_candidate"
    allowed_future_trace = status in {
        "preview_routed_to_working_readback_candidate",
        "preview_held_for_more_evidence",
    }
    return ReviewedConceptMemoryRoutingPreview(
        routing_preview_id=f"reviewed_concept_memory_routing_preview:{trace.source_reviewed_concept_id}",
        schema_version=MEMORY_ROUTING_PREVIEW_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=trace.source_reviewed_concept_id,
        source_memory_trace_preview_id=trace.memory_trace_preview_id,
        target_layer_preview=target,
        routing_reason=reason,
        routing_status=status,
        allowed_future_memory_trace=allowed_future_trace,
        allowed_future_working_readback_candidate=allowed_working,
        allowed_core_memory_write=False,
        allowed_long_term_memory_write=False,
        allowed_archive_memory_write=False,
        allowed_anchor_write=False,
        requires_more_support_before_promotion=True,
        requires_counterexample_monitoring=True,
        requires_teacher_review_before_memory_write=True,
        actual_memory_routing_trace_created=False,
        memory_write_performed=False,
        source_trace_refs=trace.source_trace_refs,
    )


def validate_reviewed_concept_memory_routing_preview(
    preview: ReviewedConceptMemoryRoutingPreview | dict[str, object],
) -> dict[str, object]:
    try:
        record = _routing_preview(preview)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_routing_preview:{error}"]}
    errors: list[str] = []
    if record.routing_status not in {
        "preview_routed_to_working_readback_candidate",
        "preview_held_for_more_evidence",
        "preview_blocked_from_routing",
    }:
        errors.append(record.routing_status)
    if record.target_layer_preview not in ALLOWED_TARGET_LAYER_PREVIEWS:
        errors.append("target_layer_preview_invalid")
    for flag in (
        "allowed_core_memory_write",
        "allowed_long_term_memory_write",
        "allowed_archive_memory_write",
        "allowed_anchor_write",
        "actual_memory_routing_trace_created",
        "memory_write_performed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    for flag in (
        "requires_more_support_before_promotion",
        "requires_counterexample_monitoring",
        "requires_teacher_review_before_memory_write",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "routing_preview_id": record.routing_preview_id,
        "target_layer_preview": record.target_layer_preview,
        "routing_status": record.routing_status,
        "memory_write_performed": record.memory_write_performed,
    }


def build_reviewed_concept_memory_application_data_preview(
    *,
    reviewed_concept: ReviewedConceptRecord | dict[str, object],
    memory_trace_preview: ReviewedConceptMemoryTracePreview | dict[str, object],
    routing_preview: ReviewedConceptMemoryRoutingPreview | dict[str, object],
) -> ReviewedConceptMemoryApplicationDataPreview:
    concept = _reviewed_concept(reviewed_concept)
    trace = _trace_preview(memory_trace_preview)
    routing = _routing_preview(routing_preview)
    application_kind = _application_kind(routing)
    hints = _hint_labels(concept.concept_label) if application_kind == "working_memory_hint_preview" else ()
    notes = _task_handling_notes(concept.concept_label) if hints else ()
    return ReviewedConceptMemoryApplicationDataPreview(
        application_data_preview_id=f"reviewed_concept_memory_application_data_preview:{concept.reviewed_concept_id}",
        schema_version=MEMORY_APPLICATION_DATA_PREVIEW_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=concept.reviewed_concept_id,
        source_memory_trace_preview_id=trace.memory_trace_preview_id,
        source_routing_preview_id=routing.routing_preview_id,
        concept_label=concept.concept_label,
        application_summary=(
            "ReviewedConcept can be previewed as Working Memory hint labels."
            if application_kind == "working_memory_hint_preview"
            else f"ReviewedConcept application data preview is {application_kind}."
        ),
        preview_application_kind=application_kind,
        suggested_working_memory_hint_labels=hints,
        suggested_task_handling_notes=notes,
        preview_only=True,
        actual_memory_application_data_created=False,
        readback_hint_created=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        source_trace_refs=_combined_trace_refs(
            concept.source_trace_refs,
            trace.source_trace_refs,
            routing.source_trace_refs,
        ),
    )


def validate_reviewed_concept_memory_application_data_preview(
    preview: ReviewedConceptMemoryApplicationDataPreview | dict[str, object],
) -> dict[str, object]:
    try:
        record = _application_preview(preview)
    except (TypeError, ValueError, KeyError) as error:
        return {
            "valid": False,
            "error_codes": [f"invalid_application_data_preview:{error}"],
        }
    errors: list[str] = []
    if record.preview_only is not True:
        errors.append("preview_only_false")
    for flag in (
        "actual_memory_application_data_created",
        "readback_hint_created",
        "working_memory_mutated",
        "task_behavior_changed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    if (
        record.preview_application_kind == "working_memory_hint_preview"
        and not record.suggested_working_memory_hint_labels
    ):
        errors.append("missing_hint_labels")
    return {
        "valid": not errors,
        "error_codes": errors,
        "application_data_preview_id": record.application_data_preview_id,
        "preview_application_kind": record.preview_application_kind,
        "preview_only": record.preview_only,
        "actual_memory_application_data_created": (
            record.actual_memory_application_data_created
        ),
        "readback_hint_created": record.readback_hint_created,
        "working_memory_mutated": record.working_memory_mutated,
        "task_behavior_changed": record.task_behavior_changed,
    }


def build_reviewed_concept_memory_preview_safety_audit(
    *,
    reviewed_concept: ReviewedConceptRecord | dict[str, object],
    memory_trace_preview: ReviewedConceptMemoryTracePreview | dict[str, object],
    routing_preview: ReviewedConceptMemoryRoutingPreview | dict[str, object],
    application_data_preview: ReviewedConceptMemoryApplicationDataPreview
    | dict[str, object]
    | None,
) -> ReviewedConceptMemoryPreviewSafetyAudit:
    concept = _reviewed_concept(reviewed_concept)
    trace = _trace_preview(memory_trace_preview)
    routing = _routing_preview(routing_preview)
    application = _application_preview(application_data_preview) if application_data_preview is not None else None
    reviewed_validation = validate_reviewed_concept_record(concept)
    lineage_complete = bool(trace.source_reviewed_concept_lineage_id)
    counterexample_handling_valid = trace.counterexample_handling_status in HANDLED_COUNTEREXAMPLE_STATUSES
    scope_valid = bool(trace.scope_text) and trace.generalization_level != "overgeneralized"
    no_actual_memory_learning_trace = trace.actual_memory_learning_trace_created is False
    no_actual_memory_routing_trace = routing.actual_memory_routing_trace_created is False
    no_actual_memory_application_data = (
        application is None
        or application.actual_memory_application_data_created is False
    )
    no_readback_hint_created = application is None or application.readback_hint_created is False
    no_working_memory_mutation = application is None or application.working_memory_mutated is False
    no_task_behavior_change = (
        trace.task_behavior_changed is False
        and (application is None or application.task_behavior_changed is False)
    )
    no_core_memory_write = routing.allowed_core_memory_write is False
    no_long_term_memory_write = routing.allowed_long_term_memory_write is False
    no_archive_memory_write = routing.allowed_archive_memory_write is False
    no_anchor_write = routing.allowed_anchor_write is False
    no_automatic_learning_approval = True
    blocked_reasons = _preview_safety_blocked_reasons(
        reviewed_concept_valid=bool(reviewed_validation["valid"]),
        trace_preview_valid=trace.trace_preview_status == "preview_ready",
        routing_preview=routing,
        no_actual_memory_learning_trace=no_actual_memory_learning_trace,
        no_actual_memory_routing_trace=no_actual_memory_routing_trace,
        no_actual_memory_application_data=no_actual_memory_application_data,
        no_readback_hint_created=no_readback_hint_created,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_core_memory_write=no_core_memory_write,
        no_long_term_memory_write=no_long_term_memory_write,
        no_archive_memory_write=no_archive_memory_write,
        no_anchor_write=no_anchor_write,
    )
    return ReviewedConceptMemoryPreviewSafetyAudit(
        safety_audit_id=f"reviewed_concept_memory_preview_safety_audit:{concept.reviewed_concept_id}",
        schema_version=MEMORY_PREVIEW_SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=concept.reviewed_concept_id,
        source_memory_trace_preview_id=trace.memory_trace_preview_id,
        source_routing_preview_id=routing.routing_preview_id,
        source_application_data_preview_id=(
            application.application_data_preview_id if application is not None else None
        ),
        reviewed_concept_valid=bool(reviewed_validation["valid"]),
        lineage_complete=lineage_complete,
        counterexample_handling_valid=counterexample_handling_valid,
        scope_valid=scope_valid,
        no_actual_memory_learning_trace=no_actual_memory_learning_trace,
        no_actual_memory_routing_trace=no_actual_memory_routing_trace,
        no_actual_memory_application_data=no_actual_memory_application_data,
        no_readback_hint_created=no_readback_hint_created,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_core_memory_write=no_core_memory_write,
        no_long_term_memory_write=no_long_term_memory_write,
        no_archive_memory_write=no_archive_memory_write,
        no_anchor_write=no_anchor_write,
        no_automatic_learning_approval=no_automatic_learning_approval,
        audit_status=_preview_safety_status(blocked_reasons),
        blocked_reasons=blocked_reasons,
    )


def validate_reviewed_concept_memory_preview_safety_audit(
    audit: ReviewedConceptMemoryPreviewSafetyAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _memory_preview_safety_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_preview_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed":
        errors.append(record.audit_status)
    for name in (
        "reviewed_concept_valid",
        "lineage_complete",
        "counterexample_handling_valid",
        "scope_valid",
        "no_actual_memory_learning_trace",
        "no_actual_memory_routing_trace",
        "no_actual_memory_application_data",
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
    return {
        "valid": not errors,
        "error_codes": errors,
        "safety_audit_id": record.safety_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_reviewed_concept_memory_preview_bundle(
    reviewed_concept_payload: dict[str, object],
) -> dict[str, object]:
    concept = _reviewed_concept(reviewed_concept_payload["reviewed_concept"])
    lineage = _lineage(reviewed_concept_payload["lineage_record"])
    reviewed_safety = _reviewed_safety(reviewed_concept_payload["safety_audit"])
    trace = build_reviewed_concept_memory_trace_preview(
        reviewed_concept=concept,
        lineage_record=lineage,
        reviewed_concept_safety_audit=reviewed_safety,
    )
    routing = build_reviewed_concept_memory_routing_preview(
        memory_trace_preview=trace,
    )
    application = build_reviewed_concept_memory_application_data_preview(
        reviewed_concept=concept,
        memory_trace_preview=trace,
        routing_preview=routing,
    )
    safety = build_reviewed_concept_memory_preview_safety_audit(
        reviewed_concept=concept,
        memory_trace_preview=trace,
        routing_preview=routing,
        application_data_preview=application,
    )
    return {
        "memory_trace_preview": trace.to_dict(),
        "routing_preview": routing.to_dict(),
        "application_data_preview": application.to_dict(),
        "preview_safety_audit": safety.to_dict(),
        "trace_validation": validate_reviewed_concept_memory_trace_preview(trace),
        "routing_validation": validate_reviewed_concept_memory_routing_preview(routing),
        "application_data_validation": (
            validate_reviewed_concept_memory_application_data_preview(application)
        ),
        "preview_safety_audit_validation": (
            validate_reviewed_concept_memory_preview_safety_audit(safety)
        ),
        "safe_claim": SAFE_CLAIM,
    }


def build_demo_reviewed_concept_memory_trace_preview() -> ReviewedConceptMemoryTracePreview:
    payload = build_demo_reviewed_concept_record()
    return build_reviewed_concept_memory_trace_preview(
        reviewed_concept=payload["reviewed_concept"],
        lineage_record=payload["lineage_record"],
        reviewed_concept_safety_audit=payload["safety_audit"],
    )


def build_demo_reviewed_concept_memory_routing_preview() -> ReviewedConceptMemoryRoutingPreview:
    return build_reviewed_concept_memory_routing_preview(
        memory_trace_preview=build_demo_reviewed_concept_memory_trace_preview()
    )


def build_demo_reviewed_concept_memory_application_data_preview() -> ReviewedConceptMemoryApplicationDataPreview:
    payload = build_demo_reviewed_concept_record()
    trace = build_reviewed_concept_memory_trace_preview(
        reviewed_concept=payload["reviewed_concept"],
        lineage_record=payload["lineage_record"],
        reviewed_concept_safety_audit=payload["safety_audit"],
    )
    routing = build_reviewed_concept_memory_routing_preview(
        memory_trace_preview=trace,
    )
    return build_reviewed_concept_memory_application_data_preview(
        reviewed_concept=payload["reviewed_concept"],
        memory_trace_preview=trace,
        routing_preview=routing,
    )


def build_demo_reviewed_concept_memory_preview_safety_audit() -> ReviewedConceptMemoryPreviewSafetyAudit:
    payload = build_reviewed_concept_memory_preview_bundle(
        build_demo_reviewed_concept_record()
    )
    return ReviewedConceptMemoryPreviewSafetyAudit.from_dict(
        payload["preview_safety_audit"]
    )


def build_demo_reviewed_concept_memory_preview_bundle() -> dict[str, object]:
    return build_reviewed_concept_memory_preview_bundle(
        build_demo_reviewed_concept_record()
    )


def build_demo_blocked_unhandled_counterexample_routing_preview() -> ReviewedConceptMemoryRoutingPreview:
    payload = build_demo_blocked_unhandled_counterexample()
    trace = build_reviewed_concept_memory_trace_preview(
        reviewed_concept=payload["reviewed_concept"],
        lineage_record=payload["lineage_record"],
        reviewed_concept_safety_audit=payload["safety_audit"],
    )
    return build_reviewed_concept_memory_routing_preview(memory_trace_preview=trace)


def build_demo_held_for_more_evidence_overbroad_scope_preview() -> ReviewedConceptMemoryRoutingPreview:
    payload = build_demo_blocked_invalid_scope()
    trace = build_reviewed_concept_memory_trace_preview(
        reviewed_concept=payload["reviewed_concept"],
        lineage_record=payload["lineage_record"],
        reviewed_concept_safety_audit=payload["safety_audit"],
    )
    return build_reviewed_concept_memory_routing_preview(memory_trace_preview=trace)


def build_demo_blocked_forbidden_target_layer_preview(
    target_layer_preview: str = "core_memory",
) -> ReviewedConceptMemoryRoutingPreview:
    return build_reviewed_concept_memory_routing_preview(
        memory_trace_preview=build_demo_reviewed_concept_memory_trace_preview(),
        requested_target_layer_preview=target_layer_preview,
    )


def build_demo_blocked_preview(case: str) -> dict[str, object]:
    cases = {
        "unhandled-counterexample": build_demo_blocked_unhandled_counterexample_routing_preview,
        "forbidden-target-layer": build_demo_blocked_forbidden_target_layer_preview,
    }
    try:
        routing = cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked preview case: {case}") from error
    return {"routing_preview": routing.to_dict()}


def build_demo_held_preview(case: str) -> dict[str, object]:
    if case != "overbroad-scope":
        raise ValueError(f"unknown held preview case: {case}")
    routing = build_demo_held_for_more_evidence_overbroad_scope_preview()
    return {"routing_preview": routing.to_dict()}


def _trace_preview_status(
    concept: ReviewedConceptRecord,
    lineage: ReviewedConceptLineageRecord,
    safety: ReviewedConceptSafetyAuditRecord,
) -> str:
    if concept.review_status == "blocked_unhandled_counterexamples":
        return "blocked_unhandled_counterexamples"
    if concept.review_status == "blocked_invalid_scope":
        return "blocked_invalid_scope"
    if not validate_reviewed_concept_record(concept)["valid"]:
        return "blocked_invalid_reviewed_concept"
    if not validate_reviewed_concept_lineage_record(lineage)["valid"]:
        return "blocked_incomplete_lineage"
    if not validate_reviewed_concept_safety_audit(safety)["valid"]:
        return "blocked_safety_audit_failed"
    if concept.counterexample_handling_status not in HANDLED_COUNTEREXAMPLE_STATUSES:
        return "blocked_unhandled_counterexamples"
    if not concept.scope_text or concept.generalization_level == "overgeneralized":
        return "blocked_invalid_scope"
    return "preview_ready"


def _routing_decision(
    trace: ReviewedConceptMemoryTracePreview,
    requested_target_layer_preview: str | None,
) -> tuple[str, str, str]:
    if requested_target_layer_preview in FORBIDDEN_TARGET_LAYER_PREVIEWS:
        return (
            "blocked_from_routing",
            "blocked_forbidden_target_layer",
            f"v0 blocks direct routing preview to {requested_target_layer_preview}.",
        )
    if requested_target_layer_preview is not None and requested_target_layer_preview not in ALLOWED_TARGET_LAYER_PREVIEWS:
        return (
            "blocked_from_routing",
            "blocked_forbidden_target_layer",
            f"v0 blocks unknown routing preview target {requested_target_layer_preview}.",
        )
    if trace.trace_preview_status == "blocked_unhandled_counterexamples":
        return (
            "blocked_from_routing",
            "preview_blocked_from_routing",
            "Counterexamples are unhandled, so routing is blocked.",
        )
    if (
        trace.trace_preview_status == "blocked_invalid_scope"
        or trace.generalization_level == "overgeneralized"
    ):
        return (
            "held_for_more_evidence",
            "preview_held_for_more_evidence",
            "Scope is not bounded enough for Working Memory readback preview.",
        )
    if trace.trace_preview_status != "preview_ready":
        return (
            "blocked_from_routing",
            "blocked_invalid_memory_trace_preview",
            f"Trace preview is not ready: {trace.trace_preview_status}.",
        )
    if not trace.support_evidence_refs:
        return (
            "held_for_more_evidence",
            "preview_held_for_more_evidence",
            "Support evidence is too weak for Working Memory readback preview.",
        )
    return (
        "working_readback_candidate",
        "preview_routed_to_working_readback_candidate",
        "ReviewedConcept is valid but conservative v0 only allows Working Memory readback candidate preview.",
    )


def _application_kind(routing: ReviewedConceptMemoryRoutingPreview) -> str:
    if routing.routing_status == "preview_routed_to_working_readback_candidate":
        return "working_memory_hint_preview"
    if routing.routing_status == "preview_held_for_more_evidence":
        return "held_for_more_evidence"
    return "blocked"


def _hint_labels(concept_label: str) -> tuple[str, ...]:
    mapping = {
        "front_blocked_affordance": (
            "observe_before_direct_retry",
            "avoid_same_failed_direct_retry",
            "verify_obstacle_type_before_generalizing",
        ),
        "unknown_front_state_requires_observe": (
            "observe_or_adjust",
            "gather_context_first",
        ),
        "expected_actual_mismatch_requires_verification": (
            "verify_expected_actual_before_reuse",
            "do_not_reuse_unverified_prediction",
        ),
    }
    return mapping.get(concept_label, ("reviewed_concept_available_for_context",))


def _task_handling_notes(concept_label: str) -> tuple[str, ...]:
    if concept_label == "front_blocked_affordance":
        return (
            "Treat direct retry as questionable until obstacle type is verified.",
            "Use this only as advisory Working Memory context.",
        )
    if concept_label == "unknown_front_state_requires_observe":
        return (
            "Observe or gather context before repeating a direct attempt.",
            "Use this only as advisory Working Memory context.",
        )
    if concept_label == "expected_actual_mismatch_requires_verification":
        return (
            "Verify expected versus actual before reusing a prediction.",
            "Use this only as advisory Working Memory context.",
        )
    return ("Use this only as advisory Working Memory context.",)


def _preview_safety_blocked_reasons(
    *,
    reviewed_concept_valid: bool,
    trace_preview_valid: bool,
    routing_preview: ReviewedConceptMemoryRoutingPreview,
    no_actual_memory_learning_trace: bool,
    no_actual_memory_routing_trace: bool,
    no_actual_memory_application_data: bool,
    no_readback_hint_created: bool,
    no_working_memory_mutation: bool,
    no_task_behavior_change: bool,
    no_core_memory_write: bool,
    no_long_term_memory_write: bool,
    no_archive_memory_write: bool,
    no_anchor_write: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not reviewed_concept_valid:
        reasons.append("blocked_invalid_reviewed_concept")
    if not trace_preview_valid:
        reasons.append("blocked_invalid_trace_preview")
    if routing_preview.routing_status == "blocked_forbidden_target_layer":
        reasons.append("blocked_forbidden_target_layer")
    if not (
        no_actual_memory_learning_trace
        and no_actual_memory_routing_trace
        and no_actual_memory_application_data
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
    return tuple(dict.fromkeys(reasons))


def _preview_safety_status(blocked_reasons: tuple[str, ...]) -> str:
    if not blocked_reasons:
        return "passed"
    for status in (
        "blocked_forbidden_memory_write_detected",
        "blocked_forbidden_readback_detected",
        "blocked_forbidden_behavior_change_detected",
        "blocked_forbidden_target_layer",
        "blocked_invalid_reviewed_concept",
        "blocked_invalid_trace_preview",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_invalid_trace_preview"


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


def _memory_preview_safety_audit(
    record: ReviewedConceptMemoryPreviewSafetyAudit | dict[str, object],
) -> ReviewedConceptMemoryPreviewSafetyAudit:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryPreviewSafetyAudit)
        else ReviewedConceptMemoryPreviewSafetyAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
