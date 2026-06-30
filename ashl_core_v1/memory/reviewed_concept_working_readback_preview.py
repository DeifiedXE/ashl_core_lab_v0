"""Preview ReviewedConcept MemoryApplicationData as Working Memory readback labels."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.memory.reviewed_concept_candidate_admission_review import (
    ReviewedConceptMemoryAdmissionReviewRecord,
    ReviewedConceptMemoryAdmissionSafetyAudit,
    ReviewedConceptMemoryApplicationData,
    ReviewedConceptMemoryLearningTrace,
    ReviewedConceptMemoryRoutingTrace,
    build_demo_held_for_more_evidence_admission,
    build_demo_reviewed_concept_memory_admission,
    validate_reviewed_concept_memory_admission_safety_audit,
    validate_reviewed_concept_memory_application_data,
)


SOURCE_ENGINE = "memory_engine"
WORKING_READBACK_PREVIEW_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_working_readback_preview_v0"
)
WORKING_READBACK_HINT_PREVIEW_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_working_readback_hint_preview_v0"
)
WORKING_READBACK_PREVIEW_SAFETY_AUDIT_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_working_readback_preview_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Memory Engine can preview how ReviewedConcept "
    "MemoryApplicationData would become future Working Memory readback hint "
    "labels and task handling notes, without creating actual readback hints, "
    "mutating Working Memory, changing task behavior, or writing memory layers."
)
BLOCKED_CLAIMS = (
    "no_actual_readback_hint",
    "no_task_working_memory_hint",
    "no_working_memory_mutation",
    "no_task_behavior_change",
    "no_candidate_ordering_change",
    "no_action_selection",
    "no_action_execution",
    "no_core_longterm_archive_anchor_write",
    "no_automatic_learning_approval",
)

ALLOWED_PREVIEW_STATUSES = {
    "preview_ready",
    "held_for_more_evidence",
    "blocked_invalid_memory_application_data",
    "blocked_invalid_routing",
    "blocked_safety_audit_failed",
    "blocked_counterexample_unhandled",
    "blocked_forbidden_authority_detected",
}
ALLOWED_HINT_PREVIEW_KINDS = {
    "working_memory_hint_preview",
    "held_for_more_evidence",
    "blocked",
}
ALLOWED_HINT_PREVIEW_STATUSES = {
    "hint_preview_ready",
    "held_for_more_evidence",
    "blocked_invalid_readback_preview",
    "blocked_no_hint_labels",
    "blocked_forbidden_authority_detected",
}
ALLOWED_SAFETY_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_memory_application_data",
    "blocked_invalid_readback_preview",
    "blocked_invalid_hint_preview",
    "blocked_forbidden_readback_hint_detected",
    "blocked_forbidden_working_memory_mutation_detected",
    "blocked_forbidden_behavior_change_detected",
    "blocked_forbidden_memory_write_detected",
}
HANDLED_COUNTEREXAMPLE_STATUSES = {
    "no_counterexamples",
    "scope_narrowed",
    "split_required",
    "candidate_invalidated",
}

HINT_LABELS_BY_CONCEPT = {
    "front_blocked_affordance": (
        "observe_before_direct_retry",
        "avoid_same_failed_direct_retry",
        "verify_obstacle_type_before_generalizing",
    ),
    "unknown_front_state_requires_observe": (
        "observe_or_adjust",
        "gather_context_first",
        "avoid_direct_retry_under_unknown",
    ),
    "expected_actual_mismatch_requires_verification": (
        "verify_expected_actual_before_reuse",
        "do_not_reuse_unverified_prediction",
        "prefer_low_risk_verification",
    ),
    "visible_front_item_reachable": (
        "known_success_path_available",
        "verify_reachability_context",
    ),
}
TASK_NOTES_BY_CONCEPT = {
    "front_blocked_affordance": (
        "Do not treat all front_blocked cases as identical.",
        "Check whether obstacle type is wall, box, temporary, or unknown.",
    ),
}
SCOPE_WARNINGS_BY_CONCEPT = {
    "front_blocked_affordance": (
        "front_blocked may be too broad without obstacle type.",
    ),
}
COUNTEREXAMPLE_WARNINGS_BY_CONCEPT = {
    "front_blocked_affordance": (
        "If front_blocked + step_forward succeeds, narrow or split the concept.",
    ),
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
class ReviewedConceptWorkingReadbackPreview:
    working_readback_preview_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_memory_learning_trace_id: str
    source_memory_routing_trace_id: str
    source_memory_application_data_id: str
    source_admission_review_id: str
    source_admission_safety_audit_id: str
    concept_label: str
    concept_summary: str
    application_summary: str
    application_status: str
    routing_target_layer: str
    preview_status: str
    preview_summary: str
    suggested_hint_labels: tuple[str, ...]
    suggested_task_handling_notes: tuple[str, ...]
    suggested_scope_warnings: tuple[str, ...]
    suggested_counterexample_warnings: tuple[str, ...]
    available_for_future_working_memory_hint_package: bool
    actual_readback_hint_created: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != WORKING_READBACK_PREVIEW_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_working_readback_preview_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.preview_status not in ALLOWED_PREVIEW_STATUSES:
            raise ValueError(f"unknown preview_status: {self.preview_status}")
        for name in (
            "suggested_hint_labels",
            "suggested_task_handling_notes",
            "suggested_scope_warnings",
            "suggested_counterexample_warnings",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptWorkingReadbackPreview":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptWorkingReadbackHintPreview:
    working_readback_hint_preview_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_working_readback_preview_id: str
    source_reviewed_concept_id: str
    source_memory_application_data_id: str
    concept_label: str
    hint_preview_kind: str
    hint_labels: tuple[str, ...]
    task_handling_notes: tuple[str, ...]
    scope_warnings: tuple[str, ...]
    counterexample_warnings: tuple[str, ...]
    hint_preview_status: str
    actual_task_working_memory_hint_created: bool
    applied_to_working_memory: bool
    task_behavior_changed: bool
    candidate_ordering_changed: bool
    action_selection_created: bool
    action_execution_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != WORKING_READBACK_HINT_PREVIEW_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_working_readback_hint_preview_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.hint_preview_kind not in ALLOWED_HINT_PREVIEW_KINDS:
            raise ValueError(f"unknown hint_preview_kind: {self.hint_preview_kind}")
        if self.hint_preview_status not in ALLOWED_HINT_PREVIEW_STATUSES:
            raise ValueError(f"unknown hint_preview_status: {self.hint_preview_status}")
        for name in (
            "hint_labels",
            "task_handling_notes",
            "scope_warnings",
            "counterexample_warnings",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptWorkingReadbackHintPreview":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptWorkingReadbackPreviewSafetyAudit:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_working_readback_preview_id: str | None
    source_working_readback_hint_preview_id: str | None
    source_memory_application_data_id: str | None
    memory_application_data_valid: bool
    routing_target_valid: bool
    admission_safety_audit_passed: bool
    readback_preview_valid: bool
    hint_preview_valid: bool
    no_actual_readback_hint_created: bool
    no_task_working_memory_hint_created: bool
    no_working_memory_mutation: bool
    no_task_behavior_change: bool
    no_candidate_ordering_change: bool
    no_action_selection: bool
    no_action_execution: bool
    no_memory_layer_write: bool
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
        if self.schema_version != WORKING_READBACK_PREVIEW_SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_working_readback_preview_safety_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.audit_status not in ALLOWED_SAFETY_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptWorkingReadbackPreviewSafetyAudit":
        return cls(**dict(data))


def build_reviewed_concept_working_readback_preview(
    *,
    memory_learning_trace: ReviewedConceptMemoryLearningTrace | dict[str, object],
    memory_routing_trace: ReviewedConceptMemoryRoutingTrace | dict[str, object],
    memory_application_data: ReviewedConceptMemoryApplicationData | dict[str, object],
    admission_review: ReviewedConceptMemoryAdmissionReviewRecord | dict[str, object],
    admission_safety_audit: ReviewedConceptMemoryAdmissionSafetyAudit | dict[str, object],
) -> ReviewedConceptWorkingReadbackPreview:
    learning_trace = _memory_learning_trace(memory_learning_trace)
    routing_trace = _memory_routing_trace(memory_routing_trace)
    application_data = _memory_application_data(memory_application_data)
    admission = _admission_review(admission_review)
    safety = _admission_safety_audit(admission_safety_audit)
    status = _preview_status(learning_trace, routing_trace, application_data, safety)
    return ReviewedConceptWorkingReadbackPreview(
        working_readback_preview_id=f"reviewed_concept_working_readback_preview:{application_data.source_reviewed_concept_id}",
        schema_version=WORKING_READBACK_PREVIEW_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=application_data.source_reviewed_concept_id,
        source_memory_learning_trace_id=learning_trace.memory_learning_trace_id,
        source_memory_routing_trace_id=routing_trace.memory_routing_trace_id,
        source_memory_application_data_id=application_data.memory_application_data_id,
        source_admission_review_id=admission.admission_review_id,
        source_admission_safety_audit_id=safety.safety_audit_id,
        concept_label=application_data.concept_label,
        concept_summary=learning_trace.concept_summary,
        application_summary=application_data.application_summary,
        application_status=application_data.application_status,
        routing_target_layer=routing_trace.target_layer,
        preview_status=status,
        preview_summary=_preview_summary(status),
        suggested_hint_labels=(
            _hint_labels(application_data) if status == "preview_ready" else ()
        ),
        suggested_task_handling_notes=(
            _task_notes(application_data) if status == "preview_ready" else ()
        ),
        suggested_scope_warnings=(
            _scope_warnings(application_data, learning_trace)
            if status == "preview_ready"
            else ()
        ),
        suggested_counterexample_warnings=(
            _counterexample_warnings(application_data, learning_trace)
            if status == "preview_ready"
            else ()
        ),
        available_for_future_working_memory_hint_package=status == "preview_ready",
        actual_readback_hint_created=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        memory_layer_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_combined_trace_refs(
            learning_trace.source_trace_refs,
            routing_trace.source_trace_refs,
            application_data.source_trace_refs,
            admission.source_trace_refs,
        ),
    )


def validate_reviewed_concept_working_readback_preview(
    preview: ReviewedConceptWorkingReadbackPreview | dict[str, object],
) -> dict[str, object]:
    try:
        record = _readback_preview(preview)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_readback_preview:{error}"]}
    errors: list[str] = []
    if record.preview_status.startswith("blocked_"):
        errors.append(record.preview_status)
    if record.preview_status == "preview_ready":
        if not record.available_for_future_working_memory_hint_package:
            errors.append("future_hint_package_unavailable")
        if not record.suggested_hint_labels:
            errors.append("missing_hint_labels")
    for flag in (
        "actual_readback_hint_created",
        "working_memory_mutated",
        "task_behavior_changed",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "working_readback_preview_id": record.working_readback_preview_id,
        "preview_status": record.preview_status,
        "actual_readback_hint_created": record.actual_readback_hint_created,
        "working_memory_mutated": record.working_memory_mutated,
        "task_behavior_changed": record.task_behavior_changed,
    }


def build_reviewed_concept_working_readback_hint_preview(
    readback_preview: ReviewedConceptWorkingReadbackPreview | dict[str, object],
) -> ReviewedConceptWorkingReadbackHintPreview:
    preview = _readback_preview(readback_preview)
    kind, status = _hint_kind_and_status(preview)
    return ReviewedConceptWorkingReadbackHintPreview(
        working_readback_hint_preview_id=f"reviewed_concept_working_readback_hint_preview:{preview.source_reviewed_concept_id}",
        schema_version=WORKING_READBACK_HINT_PREVIEW_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_working_readback_preview_id=preview.working_readback_preview_id,
        source_reviewed_concept_id=preview.source_reviewed_concept_id,
        source_memory_application_data_id=preview.source_memory_application_data_id,
        concept_label=preview.concept_label,
        hint_preview_kind=kind,
        hint_labels=preview.suggested_hint_labels if status == "hint_preview_ready" else (),
        task_handling_notes=(
            preview.suggested_task_handling_notes
            if status == "hint_preview_ready"
            else ()
        ),
        scope_warnings=preview.suggested_scope_warnings,
        counterexample_warnings=preview.suggested_counterexample_warnings,
        hint_preview_status=status,
        actual_task_working_memory_hint_created=False,
        applied_to_working_memory=False,
        task_behavior_changed=False,
        candidate_ordering_changed=False,
        action_selection_created=False,
        action_execution_created=False,
        source_trace_refs=preview.source_trace_refs,
    )


def validate_reviewed_concept_working_readback_hint_preview(
    hint_preview: ReviewedConceptWorkingReadbackHintPreview | dict[str, object],
) -> dict[str, object]:
    try:
        record = _hint_preview(hint_preview)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_hint_preview:{error}"]}
    errors: list[str] = []
    if record.hint_preview_status.startswith("blocked_"):
        errors.append(record.hint_preview_status)
    if record.hint_preview_status == "hint_preview_ready" and not record.hint_labels:
        errors.append("missing_hint_labels")
    for flag in (
        "actual_task_working_memory_hint_created",
        "applied_to_working_memory",
        "task_behavior_changed",
        "candidate_ordering_changed",
        "action_selection_created",
        "action_execution_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "working_readback_hint_preview_id": record.working_readback_hint_preview_id,
        "hint_preview_status": record.hint_preview_status,
        "actual_task_working_memory_hint_created": (
            record.actual_task_working_memory_hint_created
        ),
        "applied_to_working_memory": record.applied_to_working_memory,
        "task_behavior_changed": record.task_behavior_changed,
    }


def build_reviewed_concept_working_readback_preview_safety_audit(
    *,
    memory_application_data: ReviewedConceptMemoryApplicationData | dict[str, object],
    admission_safety_audit: ReviewedConceptMemoryAdmissionSafetyAudit | dict[str, object],
    readback_preview: ReviewedConceptWorkingReadbackPreview | dict[str, object],
    hint_preview: ReviewedConceptWorkingReadbackHintPreview | dict[str, object],
) -> ReviewedConceptWorkingReadbackPreviewSafetyAudit:
    application_data = _memory_application_data(memory_application_data)
    admission_safety = _admission_safety_audit(admission_safety_audit)
    preview = _readback_preview(readback_preview)
    hint = _hint_preview(hint_preview)
    memory_application_data_valid = bool(
        validate_reviewed_concept_memory_application_data(application_data)["valid"]
    )
    routing_target_valid = preview.routing_target_layer in {
        "working_readback",
        "held_for_more_evidence",
        "blocked",
    }
    admission_safety_passed = admission_safety.audit_status == "passed"
    readback_preview_valid = bool(
        validate_reviewed_concept_working_readback_preview(preview)["valid"]
    )
    hint_preview_valid = bool(
        validate_reviewed_concept_working_readback_hint_preview(hint)["valid"]
    )
    no_actual_readback_hint_created = (
        application_data.actual_readback_hint_created is False
        and preview.actual_readback_hint_created is False
    )
    no_task_working_memory_hint_created = (
        hint.actual_task_working_memory_hint_created is False
    )
    no_working_memory_mutation = (
        application_data.working_memory_mutated is False
        and preview.working_memory_mutated is False
        and hint.applied_to_working_memory is False
    )
    no_task_behavior_change = (
        application_data.task_behavior_changed is False
        and preview.task_behavior_changed is False
        and hint.task_behavior_changed is False
    )
    no_candidate_ordering_change = hint.candidate_ordering_changed is False
    no_action_selection = hint.action_selection_created is False
    no_action_execution = hint.action_execution_created is False
    no_memory_layer_write = (
        application_data.memory_layer_write_performed is False
        and preview.memory_layer_write_performed is False
        and admission_safety.no_memory_layer_write is True
    )
    no_core_memory_write = admission_safety.no_core_memory_write is True
    no_long_term_memory_write = admission_safety.no_long_term_memory_write is True
    no_archive_memory_write = admission_safety.no_archive_memory_write is True
    no_anchor_write = admission_safety.no_anchor_write is True
    no_automatic_learning_approval = (
        preview.automatic_learning_approval_created is False
        and admission_safety.no_automatic_learning_approval is True
    )
    blocked_reasons = _safety_blocked_reasons(
        memory_application_data_valid=memory_application_data_valid,
        readback_preview_valid=readback_preview_valid,
        hint_preview_valid=hint_preview_valid,
        no_actual_readback_hint_created=no_actual_readback_hint_created,
        no_task_working_memory_hint_created=no_task_working_memory_hint_created,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_candidate_ordering_change=no_candidate_ordering_change,
        no_action_selection=no_action_selection,
        no_action_execution=no_action_execution,
        no_memory_layer_write=no_memory_layer_write,
        no_core_memory_write=no_core_memory_write,
        no_long_term_memory_write=no_long_term_memory_write,
        no_archive_memory_write=no_archive_memory_write,
        no_anchor_write=no_anchor_write,
        no_automatic_learning_approval=no_automatic_learning_approval,
    )
    return ReviewedConceptWorkingReadbackPreviewSafetyAudit(
        safety_audit_id=f"reviewed_concept_working_readback_preview_safety_audit:{application_data.source_reviewed_concept_id}",
        schema_version=WORKING_READBACK_PREVIEW_SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=application_data.source_reviewed_concept_id,
        source_working_readback_preview_id=preview.working_readback_preview_id,
        source_working_readback_hint_preview_id=hint.working_readback_hint_preview_id,
        source_memory_application_data_id=application_data.memory_application_data_id,
        memory_application_data_valid=memory_application_data_valid,
        routing_target_valid=routing_target_valid,
        admission_safety_audit_passed=admission_safety_passed,
        readback_preview_valid=readback_preview_valid,
        hint_preview_valid=hint_preview_valid,
        no_actual_readback_hint_created=no_actual_readback_hint_created,
        no_task_working_memory_hint_created=no_task_working_memory_hint_created,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_candidate_ordering_change=no_candidate_ordering_change,
        no_action_selection=no_action_selection,
        no_action_execution=no_action_execution,
        no_memory_layer_write=no_memory_layer_write,
        no_core_memory_write=no_core_memory_write,
        no_long_term_memory_write=no_long_term_memory_write,
        no_archive_memory_write=no_archive_memory_write,
        no_anchor_write=no_anchor_write,
        no_automatic_learning_approval=no_automatic_learning_approval,
        audit_status=_safety_audit_status(blocked_reasons),
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=blocked_reasons,
        source_trace_refs=_combined_trace_refs(
            application_data.source_trace_refs,
            preview.source_trace_refs,
            hint.source_trace_refs,
        ),
    )


def validate_reviewed_concept_working_readback_preview_safety_audit(
    audit: ReviewedConceptWorkingReadbackPreviewSafetyAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _safety_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed":
        errors.append(record.audit_status)
    for flag in (
        "memory_application_data_valid",
        "routing_target_valid",
        "admission_safety_audit_passed",
        "readback_preview_valid",
        "hint_preview_valid",
        "no_actual_readback_hint_created",
        "no_task_working_memory_hint_created",
        "no_working_memory_mutation",
        "no_task_behavior_change",
        "no_candidate_ordering_change",
        "no_action_selection",
        "no_action_execution",
        "no_memory_layer_write",
        "no_core_memory_write",
        "no_long_term_memory_write",
        "no_archive_memory_write",
        "no_anchor_write",
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


def build_reviewed_concept_working_readback_preview_bundle(
    admission_payload: dict[str, object],
) -> dict[str, object]:
    preview = build_reviewed_concept_working_readback_preview(
        memory_learning_trace=admission_payload["memory_learning_trace"],
        memory_routing_trace=admission_payload["memory_routing_trace"],
        memory_application_data=admission_payload["memory_application_data"],
        admission_review=admission_payload["admission_review"],
        admission_safety_audit=admission_payload["admission_safety_audit"],
    )
    hint = build_reviewed_concept_working_readback_hint_preview(preview)
    safety = build_reviewed_concept_working_readback_preview_safety_audit(
        memory_application_data=admission_payload["memory_application_data"],
        admission_safety_audit=admission_payload["admission_safety_audit"],
        readback_preview=preview,
        hint_preview=hint,
    )
    return {
        "working_readback_preview": preview.to_dict(),
        "working_readback_hint_preview": hint.to_dict(),
        "working_readback_preview_safety_audit": safety.to_dict(),
        "working_readback_preview_validation": (
            validate_reviewed_concept_working_readback_preview(preview)
        ),
        "working_readback_hint_preview_validation": (
            validate_reviewed_concept_working_readback_hint_preview(hint)
        ),
        "working_readback_preview_safety_audit_validation": (
            validate_reviewed_concept_working_readback_preview_safety_audit(safety)
        ),
        "safe_claim": SAFE_CLAIM,
    }


def build_demo_reviewed_concept_working_readback_preview() -> (
    ReviewedConceptWorkingReadbackPreview
):
    payload = build_reviewed_concept_working_readback_preview_bundle(
        _front_blocked_admission_payload()
    )
    return ReviewedConceptWorkingReadbackPreview.from_dict(
        payload["working_readback_preview"]
    )


def build_demo_reviewed_concept_working_readback_hint_preview() -> (
    ReviewedConceptWorkingReadbackHintPreview
):
    payload = build_reviewed_concept_working_readback_preview_bundle(
        _front_blocked_admission_payload()
    )
    return ReviewedConceptWorkingReadbackHintPreview.from_dict(
        payload["working_readback_hint_preview"]
    )


def build_demo_reviewed_concept_working_readback_preview_safety_audit() -> (
    ReviewedConceptWorkingReadbackPreviewSafetyAudit
):
    payload = build_demo_reviewed_concept_working_readback_preview_bundle()
    return ReviewedConceptWorkingReadbackPreviewSafetyAudit.from_dict(
        payload["working_readback_preview_safety_audit"]
    )


def build_demo_reviewed_concept_working_readback_preview_bundle() -> dict[str, object]:
    return build_reviewed_concept_working_readback_preview_bundle(
        _front_blocked_admission_payload()
    )


def build_demo_held_for_more_evidence_readback_preview() -> dict[str, object]:
    return build_reviewed_concept_working_readback_preview_bundle(
        build_demo_held_for_more_evidence_admission()
    )


def build_demo_blocked_invalid_application_data_readback_preview() -> dict[str, object]:
    payload = _front_blocked_admission_payload()
    data = dict(payload["memory_application_data"])
    data["application_status"] = "blocked"
    data["application_kind"] = "blocked"
    data["available_for_future_readback_preview"] = False
    data["working_memory_hint_label_candidates"] = []
    data["task_handling_note_candidates"] = []
    payload["memory_application_data"] = data
    return build_reviewed_concept_working_readback_preview_bundle(payload)


def build_demo_blocked_forbidden_readback_hint_preview() -> dict[str, object]:
    payload = build_demo_reviewed_concept_working_readback_preview_bundle()
    hint_data = dict(payload["working_readback_hint_preview"])
    hint_data["actual_task_working_memory_hint_created"] = True
    hint = ReviewedConceptWorkingReadbackHintPreview.from_dict(hint_data)
    admission_payload = _front_blocked_admission_payload()
    safety = build_reviewed_concept_working_readback_preview_safety_audit(
        memory_application_data=admission_payload["memory_application_data"],
        admission_safety_audit=admission_payload["admission_safety_audit"],
        readback_preview=payload["working_readback_preview"],
        hint_preview=hint,
    )
    return {
        **payload,
        "working_readback_hint_preview": hint.to_dict(),
        "working_readback_hint_preview_validation": (
            validate_reviewed_concept_working_readback_hint_preview(hint)
        ),
        "working_readback_preview_safety_audit": safety.to_dict(),
        "working_readback_preview_safety_audit_validation": (
            validate_reviewed_concept_working_readback_preview_safety_audit(safety)
        ),
    }


def build_demo_blocked_forbidden_working_memory_mutation_preview() -> dict[str, object]:
    payload = build_demo_reviewed_concept_working_readback_preview_bundle()
    preview_data = dict(payload["working_readback_preview"])
    preview_data["working_memory_mutated"] = True
    preview = ReviewedConceptWorkingReadbackPreview.from_dict(preview_data)
    hint = build_reviewed_concept_working_readback_hint_preview(preview)
    admission_payload = _front_blocked_admission_payload()
    safety = build_reviewed_concept_working_readback_preview_safety_audit(
        memory_application_data=admission_payload["memory_application_data"],
        admission_safety_audit=admission_payload["admission_safety_audit"],
        readback_preview=preview,
        hint_preview=hint,
    )
    return {
        **payload,
        "working_readback_preview": preview.to_dict(),
        "working_readback_hint_preview": hint.to_dict(),
        "working_readback_preview_validation": (
            validate_reviewed_concept_working_readback_preview(preview)
        ),
        "working_readback_hint_preview_validation": (
            validate_reviewed_concept_working_readback_hint_preview(hint)
        ),
        "working_readback_preview_safety_audit": safety.to_dict(),
        "working_readback_preview_safety_audit_validation": (
            validate_reviewed_concept_working_readback_preview_safety_audit(safety)
        ),
    }


def build_demo_blocked_readback_preview(case: str) -> dict[str, object]:
    cases = {
        "invalid-application-data": (
            build_demo_blocked_invalid_application_data_readback_preview
        ),
        "forbidden-readback-hint": (
            build_demo_blocked_forbidden_readback_hint_preview
        ),
        "forbidden-working-memory-mutation": (
            build_demo_blocked_forbidden_working_memory_mutation_preview
        ),
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked readback preview case: {case}") from error


def _preview_status(
    learning_trace: ReviewedConceptMemoryLearningTrace,
    routing_trace: ReviewedConceptMemoryRoutingTrace,
    application_data: ReviewedConceptMemoryApplicationData,
    safety: ReviewedConceptMemoryAdmissionSafetyAudit,
) -> str:
    if (
        application_data.actual_readback_hint_created
        or application_data.working_memory_mutated
        or application_data.task_behavior_changed
        or application_data.memory_layer_write_performed
        or not safety.no_readback_hint_created
        or not safety.no_working_memory_mutation
        or not safety.no_task_behavior_change
        or not safety.no_memory_layer_write
    ):
        return "blocked_forbidden_authority_detected"
    if application_data.application_status == "held_for_more_evidence":
        return "held_for_more_evidence"
    if application_data.application_status == "blocked":
        return "blocked_invalid_memory_application_data"
    if (
        routing_trace.target_layer != "working_readback"
        or routing_trace.routing_status != "routed_to_working_readback_trace"
        or routing_trace.allowed_for_working_readback is not True
        or routing_trace.allowed_for_memory_layer_write is not False
    ):
        return "blocked_invalid_routing"
    if safety.audit_status != "passed":
        return "blocked_safety_audit_failed"
    if not _counterexamples_handled(learning_trace):
        return "blocked_counterexample_unhandled"
    if (
        application_data.application_status == "application_data_created_for_working_readback"
        and application_data.available_for_future_readback_preview is True
    ):
        return "preview_ready"
    return "blocked_invalid_memory_application_data"


def _preview_summary(status: str) -> str:
    if status == "preview_ready":
        return (
            "ReviewedConcept MemoryApplicationData can be previewed as future "
            "Working Memory readback hint labels only."
        )
    if status == "held_for_more_evidence":
        return "ReviewedConcept readback preview held for more evidence."
    return f"ReviewedConcept readback preview blocked: {status}."


def _hint_kind_and_status(
    preview: ReviewedConceptWorkingReadbackPreview,
) -> tuple[str, str]:
    if (
        preview.actual_readback_hint_created
        or preview.working_memory_mutated
        or preview.task_behavior_changed
        or preview.memory_layer_write_performed
        or preview.automatic_learning_approval_created
    ):
        return "blocked", "blocked_forbidden_authority_detected"
    if preview.preview_status == "preview_ready":
        if not preview.suggested_hint_labels:
            return "blocked", "blocked_no_hint_labels"
        return "working_memory_hint_preview", "hint_preview_ready"
    if preview.preview_status == "held_for_more_evidence":
        return "held_for_more_evidence", "held_for_more_evidence"
    return "blocked", "blocked_invalid_readback_preview"


def _hint_labels(application_data: ReviewedConceptMemoryApplicationData) -> tuple[str, ...]:
    mapped = HINT_LABELS_BY_CONCEPT.get(application_data.concept_label, ())
    return _combined_trace_refs(
        mapped,
        application_data.working_memory_hint_label_candidates,
    )


def _task_notes(application_data: ReviewedConceptMemoryApplicationData) -> tuple[str, ...]:
    mapped = TASK_NOTES_BY_CONCEPT.get(application_data.concept_label, ())
    return _combined_trace_refs(mapped, application_data.task_handling_note_candidates)


def _scope_warnings(
    application_data: ReviewedConceptMemoryApplicationData,
    learning_trace: ReviewedConceptMemoryLearningTrace,
) -> tuple[str, ...]:
    warnings = list(SCOPE_WARNINGS_BY_CONCEPT.get(application_data.concept_label, ()))
    if learning_trace.generalization_level == "overgeneralized":
        warnings.append("generalization level is overgeneralized")
    return tuple(dict.fromkeys(warnings))


def _counterexample_warnings(
    application_data: ReviewedConceptMemoryApplicationData,
    learning_trace: ReviewedConceptMemoryLearningTrace,
) -> tuple[str, ...]:
    warnings = list(
        COUNTEREXAMPLE_WARNINGS_BY_CONCEPT.get(application_data.concept_label, ())
    )
    if (
        learning_trace.counterexample_evidence_refs
        or learning_trace.counterexample_handling_status != "no_counterexamples"
    ):
        warnings.append("preserve counterexample handling before future readback use")
    return tuple(dict.fromkeys(warnings))


def _counterexamples_handled(learning_trace: ReviewedConceptMemoryLearningTrace) -> bool:
    if not learning_trace.counterexample_evidence_refs:
        return learning_trace.counterexample_handling_status in HANDLED_COUNTEREXAMPLE_STATUSES
    return learning_trace.counterexample_handling_status in HANDLED_COUNTEREXAMPLE_STATUSES


def _safety_blocked_reasons(
    *,
    memory_application_data_valid: bool,
    readback_preview_valid: bool,
    hint_preview_valid: bool,
    no_actual_readback_hint_created: bool,
    no_task_working_memory_hint_created: bool,
    no_working_memory_mutation: bool,
    no_task_behavior_change: bool,
    no_candidate_ordering_change: bool,
    no_action_selection: bool,
    no_action_execution: bool,
    no_memory_layer_write: bool,
    no_core_memory_write: bool,
    no_long_term_memory_write: bool,
    no_archive_memory_write: bool,
    no_anchor_write: bool,
    no_automatic_learning_approval: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not (
        no_memory_layer_write
        and no_core_memory_write
        and no_long_term_memory_write
        and no_archive_memory_write
        and no_anchor_write
        and no_automatic_learning_approval
    ):
        reasons.append("blocked_forbidden_memory_write_detected")
    if not (no_actual_readback_hint_created and no_task_working_memory_hint_created):
        reasons.append("blocked_forbidden_readback_hint_detected")
    if not no_working_memory_mutation:
        reasons.append("blocked_forbidden_working_memory_mutation_detected")
    if not (
        no_task_behavior_change
        and no_candidate_ordering_change
        and no_action_selection
        and no_action_execution
    ):
        reasons.append("blocked_forbidden_behavior_change_detected")
    if not memory_application_data_valid:
        reasons.append("blocked_invalid_memory_application_data")
    if not readback_preview_valid:
        reasons.append("blocked_invalid_readback_preview")
    if not hint_preview_valid:
        reasons.append("blocked_invalid_hint_preview")
    return tuple(dict.fromkeys(reasons))


def _safety_audit_status(blocked_reasons: tuple[str, ...]) -> str:
    if not blocked_reasons:
        return "passed"
    for status in (
        "blocked_forbidden_memory_write_detected",
        "blocked_forbidden_readback_hint_detected",
        "blocked_forbidden_working_memory_mutation_detected",
        "blocked_forbidden_behavior_change_detected",
        "blocked_invalid_memory_application_data",
        "blocked_invalid_readback_preview",
        "blocked_invalid_hint_preview",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_invalid_readback_preview"


def _front_blocked_admission_payload() -> dict[str, object]:
    payload = build_demo_reviewed_concept_memory_admission()
    concept_label = "front_blocked_affordance"
    concept_summary = "front blocked state tends to make direct forward movement fail"
    for key in ("admission_review", "memory_learning_trace"):
        record = dict(payload[key])
        record["concept_label"] = concept_label
        record["concept_summary"] = concept_summary
        payload[key] = record
    application_label = dict(payload["memory_application_data"])
    application_label["concept_label"] = concept_label
    payload["memory_application_data"] = application_label
    learning = dict(payload["memory_learning_trace"])
    learning["scope_text"] = (
        "When the front obstacle is wall-like or non-pushable, direct forward "
        "movement should not be repeated without observation."
    )
    learning["generalization_level"] = "same_context"
    learning["counterexample_handling_status"] = "no_counterexamples"
    payload["memory_learning_trace"] = learning
    application = dict(payload["memory_application_data"])
    application["application_summary"] = (
        "Preview front_blocked_affordance as future Working Memory hint labels."
    )
    application["working_memory_hint_label_candidates"] = list(
        HINT_LABELS_BY_CONCEPT[concept_label]
    )
    application["task_handling_note_candidates"] = list(
        TASK_NOTES_BY_CONCEPT[concept_label]
    )
    payload["memory_application_data"] = application
    return payload


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


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


def _admission_review(
    record: ReviewedConceptMemoryAdmissionReviewRecord | dict[str, object],
) -> ReviewedConceptMemoryAdmissionReviewRecord:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryAdmissionReviewRecord)
        else ReviewedConceptMemoryAdmissionReviewRecord.from_dict(dict(record))
    )


def _admission_safety_audit(
    record: ReviewedConceptMemoryAdmissionSafetyAudit | dict[str, object],
) -> ReviewedConceptMemoryAdmissionSafetyAudit:
    return (
        record
        if isinstance(record, ReviewedConceptMemoryAdmissionSafetyAudit)
        else ReviewedConceptMemoryAdmissionSafetyAudit.from_dict(dict(record))
    )


def _readback_preview(
    record: ReviewedConceptWorkingReadbackPreview | dict[str, object],
) -> ReviewedConceptWorkingReadbackPreview:
    return (
        record
        if isinstance(record, ReviewedConceptWorkingReadbackPreview)
        else ReviewedConceptWorkingReadbackPreview.from_dict(dict(record))
    )


def _hint_preview(
    record: ReviewedConceptWorkingReadbackHintPreview | dict[str, object],
) -> ReviewedConceptWorkingReadbackHintPreview:
    return (
        record
        if isinstance(record, ReviewedConceptWorkingReadbackHintPreview)
        else ReviewedConceptWorkingReadbackHintPreview.from_dict(dict(record))
    )


def _safety_audit(
    record: ReviewedConceptWorkingReadbackPreviewSafetyAudit | dict[str, object],
) -> ReviewedConceptWorkingReadbackPreviewSafetyAudit:
    return (
        record
        if isinstance(record, ReviewedConceptWorkingReadbackPreviewSafetyAudit)
        else ReviewedConceptWorkingReadbackPreviewSafetyAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
