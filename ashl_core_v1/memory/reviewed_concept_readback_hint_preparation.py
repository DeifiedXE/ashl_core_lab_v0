"""Prepare teacher-approved ReviewedConcept readback hint candidates."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.memory.reviewed_concept_readback_hint_candidate import (
    ReviewedConceptReadbackHintCandidate,
    ReviewedConceptReadbackHintCandidateSet,
    build_demo_reviewed_concept_readback_hint_candidate_set,
    validate_reviewed_concept_readback_hint_candidate,
    validate_reviewed_concept_readback_hint_candidate_set,
)
from ashl_core_v1.memory.reviewed_concept_readback_hint_teacher_review import (
    ReviewedConceptReadbackHintCandidateSetTeacherReview,
    ReviewedConceptReadbackHintCandidateTeacherReview,
    ReviewedConceptReadbackHintTeacherReviewSafetyAudit,
    build_demo_all_held_readback_hint_teacher_review,
    build_demo_conflict_detected_readback_hint_teacher_review,
    build_demo_rejected_readback_hint_teacher_review,
    build_demo_reviewed_concept_readback_hint_teacher_review,
    validate_reviewed_concept_readback_hint_candidate_set_teacher_review,
    validate_reviewed_concept_readback_hint_candidate_teacher_review,
    validate_reviewed_concept_readback_hint_teacher_review_safety_audit,
)


SOURCE_ENGINE = "memory_engine"
READBACK_HINT_PREPARATION_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_readback_hint_preparation_v0"
)
READBACK_HINT_PREPARATION_SET_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_readback_hint_preparation_set_v0"
)
READBACK_HINT_PREPARATION_SAFETY_AUDIT_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_readback_hint_preparation_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Memory Engine can convert teacher-approved ReviewedConcept "
    "readback hint candidates into actual-hint preparation records for future "
    "TaskWorkingMemoryReadbackHint creation review, without creating actual "
    "hints, mutating Working Memory, changing task behavior, selecting actions, "
    "executing actions, or writing memory layers."
)
BLOCKED_CLAIMS = (
    "no_actual_task_working_memory_hint",
    "no_working_memory_mutation",
    "no_task_behavior_change",
    "no_candidate_ordering_change",
    "no_action_selection",
    "no_action_execution",
    "no_core_longterm_archive_anchor_write",
    "no_automatic_learning_approval",
)

ALLOWED_PREPARATION_STATUSES = {
    "prepared_for_future_hint_creation_review",
    "held_for_more_evidence",
    "blocked_not_teacher_approved",
    "blocked_candidate_rejected",
    "blocked_conflict_detected",
    "blocked_invalid_teacher_review",
    "blocked_invalid_candidate",
    "blocked_forbidden_authority_detected",
}
ALLOWED_SET_PREPARATION_STATUSES = {
    "preparation_set_created_with_ready_records",
    "preparation_set_created_all_held_or_blocked",
    "blocked_invalid_teacher_review_set",
    "blocked_invalid_preparation_records",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_teacher_review_set",
    "blocked_teacher_review_safety_audit_failed",
    "blocked_invalid_preparation_set",
    "blocked_invalid_preparation_records",
    "blocked_forbidden_hint_creation_detected",
    "blocked_forbidden_working_memory_mutation_detected",
    "blocked_forbidden_behavior_change_detected",
    "blocked_forbidden_action_authority_detected",
    "blocked_forbidden_memory_write_detected",
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
class ReviewedConceptReadbackHintPreparationRecord:
    readback_hint_preparation_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_candidate_id: str
    source_hint_candidate_set_id: str
    source_hint_candidate_teacher_review_id: str
    source_hint_candidate_set_teacher_review_id: str
    source_teacher_review_safety_audit_id: str
    concept_label: str
    hint_label: str
    hint_kind: str
    hint_priority: int
    hint_summary: str
    prepared_task_handling_note: str
    prepared_scope_warning: str | None
    prepared_counterexample_warning: str | None
    preparation_status: str
    preparation_summary: str
    ready_for_future_task_working_memory_hint_creation_review: bool
    requires_task_engine_hint_creation_package: bool
    requires_teacher_review_before_application: bool
    requires_counterexample_monitoring: bool
    actual_task_working_memory_hint_created: bool
    applied_to_working_memory: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    candidate_ordering_changed: bool
    action_selection_created: bool
    action_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READBACK_HINT_PREPARATION_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_readback_hint_preparation_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.preparation_status not in ALLOWED_PREPARATION_STATUSES:
            raise ValueError(f"unknown preparation_status: {self.preparation_status}")
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
    ) -> "ReviewedConceptReadbackHintPreparationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptReadbackHintPreparationSet:
    readback_hint_preparation_set_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_candidate_set_id: str
    source_hint_candidate_set_teacher_review_id: str
    source_teacher_review_safety_audit_id: str
    concept_label: str
    preparation_records: tuple[ReviewedConceptReadbackHintPreparationRecord, ...]
    prepared_record_ids: tuple[str, ...]
    held_record_ids: tuple[str, ...]
    blocked_record_ids: tuple[str, ...]
    prepared_hint_labels: tuple[str, ...]
    prepared_count: int
    held_count: int
    blocked_count: int
    set_preparation_status: str
    set_preparation_summary: str
    has_prepared_records_for_future_hint_creation_review: bool
    actual_task_working_memory_hint_created: bool
    applied_to_working_memory: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READBACK_HINT_PREPARATION_SET_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_readback_hint_preparation_set_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.set_preparation_status not in ALLOWED_SET_PREPARATION_STATUSES:
            raise ValueError(
                f"unknown set_preparation_status: {self.set_preparation_status}"
            )
        object.__setattr__(
            self,
            "preparation_records",
            tuple(
                item
                if isinstance(item, ReviewedConceptReadbackHintPreparationRecord)
                else ReviewedConceptReadbackHintPreparationRecord.from_dict(dict(item))
                for item in self.preparation_records
            ),
        )
        for name in (
            "prepared_record_ids",
            "held_record_ids",
            "blocked_record_ids",
            "prepared_hint_labels",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptReadbackHintPreparationSet":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptReadbackHintPreparationSafetyAudit:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_candidate_set_teacher_review_id: str | None
    source_preparation_set_id: str | None
    teacher_review_set_valid: bool
    teacher_review_safety_audit_passed: bool
    preparation_records_valid: bool
    preparation_scope_valid: bool
    no_actual_task_working_memory_hint_created: bool
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
        if self.schema_version != READBACK_HINT_PREPARATION_SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_readback_hint_preparation_safety_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptReadbackHintPreparationSafetyAudit":
        return cls(**dict(data))


def build_reviewed_concept_readback_hint_preparation_record(
    *,
    hint_candidate: ReviewedConceptReadbackHintCandidate | dict[str, object],
    hint_candidate_set: ReviewedConceptReadbackHintCandidateSet | dict[str, object],
    hint_candidate_teacher_review: (
        ReviewedConceptReadbackHintCandidateTeacherReview | dict[str, object]
    ),
    hint_candidate_set_teacher_review: (
        ReviewedConceptReadbackHintCandidateSetTeacherReview | dict[str, object]
    ),
    teacher_review_safety_audit: (
        ReviewedConceptReadbackHintTeacherReviewSafetyAudit | dict[str, object]
    ),
) -> ReviewedConceptReadbackHintPreparationRecord:
    candidate = _candidate(hint_candidate)
    candidate_set = _candidate_set(hint_candidate_set)
    candidate_review = _candidate_review(hint_candidate_teacher_review)
    set_review = _candidate_set_review(hint_candidate_set_teacher_review)
    teacher_safety = _teacher_review_safety_audit(teacher_review_safety_audit)
    status = _preparation_status(candidate, candidate_review)
    return ReviewedConceptReadbackHintPreparationRecord(
        readback_hint_preparation_id=(
            "reviewed_concept_readback_hint_preparation:"
            f"{candidate.readback_hint_candidate_id}"
        ),
        schema_version=READBACK_HINT_PREPARATION_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=candidate.source_reviewed_concept_id,
        source_hint_candidate_id=candidate.readback_hint_candidate_id,
        source_hint_candidate_set_id=candidate_set.hint_candidate_set_id,
        source_hint_candidate_teacher_review_id=(
            candidate_review.hint_candidate_teacher_review_id
        ),
        source_hint_candidate_set_teacher_review_id=(
            set_review.hint_candidate_set_teacher_review_id
        ),
        source_teacher_review_safety_audit_id=teacher_safety.safety_audit_id,
        concept_label=candidate.concept_label,
        hint_label=candidate.hint_label,
        hint_kind=candidate.hint_kind,
        hint_priority=candidate.hint_priority,
        hint_summary=candidate.hint_summary,
        prepared_task_handling_note=candidate.task_handling_note,
        prepared_scope_warning=candidate.scope_warning,
        prepared_counterexample_warning=candidate.counterexample_warning,
        preparation_status=status,
        preparation_summary=_preparation_summary(status),
        ready_for_future_task_working_memory_hint_creation_review=(
            status == "prepared_for_future_hint_creation_review"
        ),
        requires_task_engine_hint_creation_package=True,
        requires_teacher_review_before_application=True,
        requires_counterexample_monitoring=True,
        actual_task_working_memory_hint_created=False,
        applied_to_working_memory=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        candidate_ordering_changed=False,
        action_selection_created=False,
        action_execution_created=False,
        memory_layer_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_combined_trace_refs(
            candidate.source_trace_refs,
            candidate_set.source_trace_refs,
            candidate_review.source_trace_refs,
            set_review.source_trace_refs,
            teacher_safety.source_trace_refs,
        ),
    )


def validate_reviewed_concept_readback_hint_preparation_record(
    record: ReviewedConceptReadbackHintPreparationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        preparation = _preparation_record(record)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_preparation_record:{error}"]}
    errors: list[str] = []
    if preparation.preparation_status in {
        "blocked_invalid_teacher_review",
        "blocked_invalid_candidate",
        "blocked_forbidden_authority_detected",
    }:
        errors.append(preparation.preparation_status)
    expected_ready = (
        preparation.preparation_status == "prepared_for_future_hint_creation_review"
    )
    if preparation.ready_for_future_task_working_memory_hint_creation_review is not expected_ready:
        errors.append("ready_flag_mismatch")
    for flag in (
        "requires_task_engine_hint_creation_package",
        "requires_teacher_review_before_application",
        "requires_counterexample_monitoring",
    ):
        if getattr(preparation, flag) is not True:
            errors.append(f"{flag}_false")
    for flag in (
        "actual_task_working_memory_hint_created",
        "applied_to_working_memory",
        "working_memory_mutated",
        "task_behavior_changed",
        "candidate_ordering_changed",
        "action_selection_created",
        "action_execution_created",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(preparation, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "readback_hint_preparation_id": preparation.readback_hint_preparation_id,
        "preparation_status": preparation.preparation_status,
        "source_hint_candidate_id": preparation.source_hint_candidate_id,
    }


def build_reviewed_concept_readback_hint_preparation_set(
    *,
    hint_candidate_set: ReviewedConceptReadbackHintCandidateSet | dict[str, object],
    hint_candidate_set_teacher_review: (
        ReviewedConceptReadbackHintCandidateSetTeacherReview | dict[str, object]
    ),
    teacher_review_safety_audit: (
        ReviewedConceptReadbackHintTeacherReviewSafetyAudit | dict[str, object]
    ),
) -> ReviewedConceptReadbackHintPreparationSet:
    candidate_set = _candidate_set(hint_candidate_set)
    set_review = _candidate_set_review(hint_candidate_set_teacher_review)
    teacher_safety = _teacher_review_safety_audit(teacher_review_safety_audit)
    candidates_by_id = {
        candidate.readback_hint_candidate_id: candidate
        for candidate in candidate_set.hint_candidates
    }
    records = tuple(
        build_reviewed_concept_readback_hint_preparation_record(
            hint_candidate=candidates_by_id.get(
                review.source_hint_candidate_id,
                _missing_candidate(review),
            ),
            hint_candidate_set=candidate_set,
            hint_candidate_teacher_review=review,
            hint_candidate_set_teacher_review=set_review,
            teacher_review_safety_audit=teacher_safety,
        )
        for review in set_review.candidate_reviews
    )
    status = _set_preparation_status(set_review, records)
    prepared_records = tuple(
        record
        for record in records
        if record.preparation_status == "prepared_for_future_hint_creation_review"
    )
    held_records = tuple(
        record
        for record in records
        if record.preparation_status == "held_for_more_evidence"
    )
    blocked_records = tuple(
        record
        for record in records
        if record.preparation_status.startswith("blocked_")
    )
    return ReviewedConceptReadbackHintPreparationSet(
        readback_hint_preparation_set_id=(
            "reviewed_concept_readback_hint_preparation_set:"
            f"{candidate_set.source_reviewed_concept_id}"
        ),
        schema_version=READBACK_HINT_PREPARATION_SET_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=candidate_set.source_reviewed_concept_id,
        source_hint_candidate_set_id=candidate_set.hint_candidate_set_id,
        source_hint_candidate_set_teacher_review_id=(
            set_review.hint_candidate_set_teacher_review_id
        ),
        source_teacher_review_safety_audit_id=teacher_safety.safety_audit_id,
        concept_label=candidate_set.concept_label,
        preparation_records=records,
        prepared_record_ids=tuple(
            record.readback_hint_preparation_id for record in prepared_records
        ),
        held_record_ids=tuple(record.readback_hint_preparation_id for record in held_records),
        blocked_record_ids=tuple(
            record.readback_hint_preparation_id for record in blocked_records
        ),
        prepared_hint_labels=tuple(record.hint_label for record in prepared_records),
        prepared_count=len(prepared_records),
        held_count=len(held_records),
        blocked_count=len(blocked_records),
        set_preparation_status=status,
        set_preparation_summary=_set_preparation_summary(status),
        has_prepared_records_for_future_hint_creation_review=bool(prepared_records)
        and status == "preparation_set_created_with_ready_records",
        actual_task_working_memory_hint_created=False,
        applied_to_working_memory=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        memory_layer_write_performed=False,
        source_trace_refs=_combined_trace_refs(
            candidate_set.source_trace_refs,
            set_review.source_trace_refs,
            teacher_safety.source_trace_refs,
            *(record.source_trace_refs for record in records),
        ),
    )


def validate_reviewed_concept_readback_hint_preparation_set(
    preparation_set: ReviewedConceptReadbackHintPreparationSet | dict[str, object],
) -> dict[str, object]:
    try:
        record = _preparation_set(preparation_set)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_preparation_set:{error}"]}
    errors: list[str] = []
    if record.set_preparation_status.startswith("blocked_"):
        errors.append(record.set_preparation_status)
    record_validations = [
        validate_reviewed_concept_readback_hint_preparation_record(item)
        for item in record.preparation_records
    ]
    if any(not validation["valid"] for validation in record_validations):
        errors.append("preparation_record_invalid")
    prepared_records = tuple(
        item
        for item in record.preparation_records
        if item.preparation_status == "prepared_for_future_hint_creation_review"
    )
    held_records = tuple(
        item
        for item in record.preparation_records
        if item.preparation_status == "held_for_more_evidence"
    )
    blocked_records = tuple(
        item for item in record.preparation_records if item.preparation_status.startswith("blocked_")
    )
    if record.prepared_count != len(prepared_records):
        errors.append("prepared_count_mismatch")
    if record.held_count != len(held_records):
        errors.append("held_count_mismatch")
    if record.blocked_count != len(blocked_records):
        errors.append("blocked_count_mismatch")
    if record.has_prepared_records_for_future_hint_creation_review != bool(
        record.prepared_record_ids
    ):
        errors.append("has_prepared_records_flag_mismatch")
    for flag in (
        "actual_task_working_memory_hint_created",
        "applied_to_working_memory",
        "working_memory_mutated",
        "task_behavior_changed",
        "memory_layer_write_performed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "readback_hint_preparation_set_id": record.readback_hint_preparation_set_id,
        "set_preparation_status": record.set_preparation_status,
        "prepared_count": record.prepared_count,
        "held_count": record.held_count,
        "blocked_count": record.blocked_count,
    }


def build_reviewed_concept_readback_hint_preparation_safety_audit(
    *,
    hint_candidate_set_teacher_review: (
        ReviewedConceptReadbackHintCandidateSetTeacherReview | dict[str, object]
    ),
    teacher_review_safety_audit: (
        ReviewedConceptReadbackHintTeacherReviewSafetyAudit | dict[str, object]
    ),
    preparation_set: ReviewedConceptReadbackHintPreparationSet | dict[str, object],
) -> ReviewedConceptReadbackHintPreparationSafetyAudit:
    set_review = _candidate_set_review(hint_candidate_set_teacher_review)
    teacher_safety = _teacher_review_safety_audit(teacher_review_safety_audit)
    prep_set = _preparation_set(preparation_set)
    teacher_review_set_valid = bool(
        validate_reviewed_concept_readback_hint_candidate_set_teacher_review(
            set_review
        )["valid"]
    )
    teacher_review_safety_audit_passed = bool(
        validate_reviewed_concept_readback_hint_teacher_review_safety_audit(
            teacher_safety
        )["valid"]
    )
    preparation_records_valid = all(
        validate_reviewed_concept_readback_hint_preparation_record(record)["valid"]
        for record in prep_set.preparation_records
    )
    preparation_set_valid = bool(
        validate_reviewed_concept_readback_hint_preparation_set(prep_set)["valid"]
    )
    preparation_scope_valid = _preparation_scope_valid(set_review, prep_set)
    no_actual_hint = (
        prep_set.actual_task_working_memory_hint_created is False
        and all(
            record.actual_task_working_memory_hint_created is False
            for record in prep_set.preparation_records
        )
    )
    no_working_memory_mutation = (
        prep_set.applied_to_working_memory is False
        and prep_set.working_memory_mutated is False
        and all(
            record.applied_to_working_memory is False
            and record.working_memory_mutated is False
            for record in prep_set.preparation_records
        )
    )
    no_task_behavior_change = (
        prep_set.task_behavior_changed is False
        and all(
            record.task_behavior_changed is False
            for record in prep_set.preparation_records
        )
    )
    no_candidate_ordering_change = all(
        record.candidate_ordering_changed is False
        for record in prep_set.preparation_records
    )
    no_action_selection = all(
        record.action_selection_created is False for record in prep_set.preparation_records
    )
    no_action_execution = all(
        record.action_execution_created is False for record in prep_set.preparation_records
    )
    no_memory_layer_write = (
        prep_set.memory_layer_write_performed is False
        and all(
            record.memory_layer_write_performed is False
            for record in prep_set.preparation_records
        )
    )
    no_automatic_learning_approval = all(
        record.automatic_learning_approval_created is False
        for record in prep_set.preparation_records
    )
    blocked_reasons = _safety_blocked_reasons(
        teacher_review_set_valid=teacher_review_set_valid,
        teacher_review_safety_audit_passed=teacher_review_safety_audit_passed,
        preparation_set_valid=preparation_set_valid,
        preparation_records_valid=preparation_records_valid,
        preparation_scope_valid=preparation_scope_valid,
        no_actual_task_working_memory_hint_created=no_actual_hint,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_candidate_ordering_change=no_candidate_ordering_change,
        no_action_selection=no_action_selection,
        no_action_execution=no_action_execution,
        no_memory_layer_write=no_memory_layer_write,
        no_automatic_learning_approval=no_automatic_learning_approval,
    )
    return ReviewedConceptReadbackHintPreparationSafetyAudit(
        safety_audit_id=(
            "reviewed_concept_readback_hint_preparation_safety_audit:"
            f"{prep_set.source_reviewed_concept_id}"
        ),
        schema_version=READBACK_HINT_PREPARATION_SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=prep_set.source_reviewed_concept_id,
        source_hint_candidate_set_teacher_review_id=(
            set_review.hint_candidate_set_teacher_review_id
        ),
        source_preparation_set_id=prep_set.readback_hint_preparation_set_id,
        teacher_review_set_valid=teacher_review_set_valid,
        teacher_review_safety_audit_passed=teacher_review_safety_audit_passed,
        preparation_records_valid=preparation_records_valid,
        preparation_scope_valid=preparation_scope_valid,
        no_actual_task_working_memory_hint_created=no_actual_hint,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_candidate_ordering_change=no_candidate_ordering_change,
        no_action_selection=no_action_selection,
        no_action_execution=no_action_execution,
        no_memory_layer_write=no_memory_layer_write,
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_automatic_learning_approval=no_automatic_learning_approval,
        audit_status=_audit_status(blocked_reasons),
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=blocked_reasons,
        source_trace_refs=_combined_trace_refs(
            set_review.source_trace_refs,
            teacher_safety.source_trace_refs,
            prep_set.source_trace_refs,
        ),
    )


def validate_reviewed_concept_readback_hint_preparation_safety_audit(
    audit: ReviewedConceptReadbackHintPreparationSafetyAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _preparation_safety_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed":
        errors.append(record.audit_status)
    for flag in (
        "teacher_review_set_valid",
        "teacher_review_safety_audit_passed",
        "preparation_records_valid",
        "preparation_scope_valid",
        "no_actual_task_working_memory_hint_created",
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


def build_reviewed_concept_readback_hint_preparation_bundle(
    *,
    candidate_payload: dict[str, object],
    teacher_review_payload: dict[str, object],
) -> dict[str, object]:
    candidate_set = _candidate_set(candidate_payload["hint_candidate_set"])
    set_review = _candidate_set_review(
        teacher_review_payload["hint_candidate_set_teacher_review"]
    )
    teacher_safety = _teacher_review_safety_audit(
        teacher_review_payload["hint_teacher_review_safety_audit"]
    )
    preparation_set = build_reviewed_concept_readback_hint_preparation_set(
        hint_candidate_set=candidate_set,
        hint_candidate_set_teacher_review=set_review,
        teacher_review_safety_audit=teacher_safety,
    )
    safety = build_reviewed_concept_readback_hint_preparation_safety_audit(
        hint_candidate_set_teacher_review=set_review,
        teacher_review_safety_audit=teacher_safety,
        preparation_set=preparation_set,
    )
    return {
        "readback_hint_preparation_records": [
            record.to_dict() for record in preparation_set.preparation_records
        ],
        "readback_hint_preparation_set": preparation_set.to_dict(),
        "readback_hint_preparation_safety_audit": safety.to_dict(),
        "readback_hint_preparation_set_validation": (
            validate_reviewed_concept_readback_hint_preparation_set(preparation_set)
        ),
        "readback_hint_preparation_safety_audit_validation": (
            validate_reviewed_concept_readback_hint_preparation_safety_audit(safety)
        ),
        "safe_claim": SAFE_CLAIM,
    }


def build_demo_reviewed_concept_readback_hint_preparation_set() -> dict[str, object]:
    return build_reviewed_concept_readback_hint_preparation_bundle(
        candidate_payload=build_demo_reviewed_concept_readback_hint_candidate_set(),
        teacher_review_payload=build_demo_reviewed_concept_readback_hint_teacher_review(),
    )


def build_demo_reviewed_concept_readback_hint_preparation_safety_audit() -> (
    ReviewedConceptReadbackHintPreparationSafetyAudit
):
    payload = build_demo_reviewed_concept_readback_hint_preparation_set()
    return ReviewedConceptReadbackHintPreparationSafetyAudit.from_dict(
        payload["readback_hint_preparation_safety_audit"]
    )


def build_demo_all_held_readback_hint_preparation_set() -> dict[str, object]:
    return build_reviewed_concept_readback_hint_preparation_bundle(
        candidate_payload=build_demo_reviewed_concept_readback_hint_candidate_set(),
        teacher_review_payload=build_demo_all_held_readback_hint_teacher_review(),
    )


def build_demo_rejected_readback_hint_preparation_set() -> dict[str, object]:
    return build_reviewed_concept_readback_hint_preparation_bundle(
        candidate_payload=build_demo_reviewed_concept_readback_hint_candidate_set(),
        teacher_review_payload=build_demo_rejected_readback_hint_teacher_review(),
    )


def build_demo_conflict_detected_readback_hint_preparation_set() -> dict[str, object]:
    return build_reviewed_concept_readback_hint_preparation_bundle(
        candidate_payload=build_demo_reviewed_concept_readback_hint_candidate_set(),
        teacher_review_payload=build_demo_conflict_detected_readback_hint_teacher_review(),
    )


def build_demo_blocked_forbidden_authority_preparation_set() -> dict[str, object]:
    payload = build_demo_reviewed_concept_readback_hint_preparation_set()
    preparation_set = ReviewedConceptReadbackHintPreparationSet.from_dict(
        payload["readback_hint_preparation_set"]
    )
    records = list(preparation_set.preparation_records)
    first = dict(records[0].to_dict())
    first["actual_task_working_memory_hint_created"] = True
    records[0] = ReviewedConceptReadbackHintPreparationRecord.from_dict(first)
    preparation_set = ReviewedConceptReadbackHintPreparationSet.from_dict(
        {
            **preparation_set.to_dict(),
            "preparation_records": [record.to_dict() for record in records],
        }
    )
    teacher_payload = build_demo_reviewed_concept_readback_hint_teacher_review()
    safety = build_reviewed_concept_readback_hint_preparation_safety_audit(
        hint_candidate_set_teacher_review=teacher_payload[
            "hint_candidate_set_teacher_review"
        ],
        teacher_review_safety_audit=teacher_payload[
            "hint_teacher_review_safety_audit"
        ],
        preparation_set=preparation_set,
    )
    return {
        **payload,
        "readback_hint_preparation_records": [
            record.to_dict() for record in records
        ],
        "readback_hint_preparation_set": preparation_set.to_dict(),
        "readback_hint_preparation_set_validation": (
            validate_reviewed_concept_readback_hint_preparation_set(preparation_set)
        ),
        "readback_hint_preparation_safety_audit": safety.to_dict(),
        "readback_hint_preparation_safety_audit_validation": (
            validate_reviewed_concept_readback_hint_preparation_safety_audit(safety)
        ),
    }


def build_demo_blocked_readback_hint_preparation_set(case: str) -> dict[str, object]:
    cases = {
        "rejected": build_demo_rejected_readback_hint_preparation_set,
        "conflict": build_demo_conflict_detected_readback_hint_preparation_set,
        "forbidden-authority": build_demo_blocked_forbidden_authority_preparation_set,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked preparation case: {case}") from error


def _preparation_status(
    candidate: ReviewedConceptReadbackHintCandidate,
    review: ReviewedConceptReadbackHintCandidateTeacherReview,
) -> str:
    if (
        not validate_reviewed_concept_readback_hint_candidate(candidate)["valid"]
        or candidate.readback_hint_candidate_id != review.source_hint_candidate_id
    ):
        return "blocked_invalid_candidate"
    if not validate_reviewed_concept_readback_hint_candidate_teacher_review(review)[
        "valid"
    ]:
        return "blocked_invalid_teacher_review"
    if any(
        (
            candidate.actual_task_working_memory_hint_created,
            candidate.applied_to_working_memory,
            candidate.working_memory_mutated,
            candidate.task_behavior_changed,
            candidate.candidate_ordering_changed,
            candidate.action_selection_created,
            candidate.action_execution_created,
            candidate.memory_layer_write_performed,
            review.actual_task_working_memory_hint_created,
            review.applied_to_working_memory,
            review.working_memory_mutated,
            review.task_behavior_changed,
            review.candidate_ordering_changed,
            review.action_selection_created,
            review.action_execution_created,
            review.memory_layer_write_performed,
        )
    ):
        return "blocked_forbidden_authority_detected"
    if review.teacher_review_status == "approved_for_future_hint_preparation":
        return "prepared_for_future_hint_creation_review"
    if review.teacher_review_status in {"held_for_more_evidence", "needs_more_evidence"}:
        return "held_for_more_evidence"
    if review.teacher_review_status == "rejected":
        return "blocked_candidate_rejected"
    if review.teacher_review_status == "conflict_detected":
        return "blocked_conflict_detected"
    return "blocked_not_teacher_approved"


def _preparation_summary(status: str) -> str:
    if status == "prepared_for_future_hint_creation_review":
        return "Teacher-approved candidate prepared for a future actual-hint creation review."
    if status == "held_for_more_evidence":
        return "Hint preparation held until more evidence or scope review is available."
    if status == "blocked_candidate_rejected":
        return "Hint preparation blocked because the teacher rejected the candidate."
    if status == "blocked_conflict_detected":
        return "Hint preparation blocked because teacher review detected a conflict."
    return f"Hint preparation blocked: {status}."


def _set_preparation_status(
    set_review: ReviewedConceptReadbackHintCandidateSetTeacherReview,
    records: tuple[ReviewedConceptReadbackHintPreparationRecord, ...],
) -> str:
    if not validate_reviewed_concept_readback_hint_candidate_set_teacher_review(
        set_review
    )["valid"]:
        return "blocked_invalid_teacher_review_set"
    if any(
        record.preparation_status == "blocked_forbidden_authority_detected"
        for record in records
    ):
        return "blocked_forbidden_authority_detected"
    if any(
        not validate_reviewed_concept_readback_hint_preparation_record(record)["valid"]
        for record in records
    ):
        return "blocked_invalid_preparation_records"
    if any(
        record.preparation_status == "prepared_for_future_hint_creation_review"
        for record in records
    ):
        return "preparation_set_created_with_ready_records"
    return "preparation_set_created_all_held_or_blocked"


def _set_preparation_summary(status: str) -> str:
    if status == "preparation_set_created_with_ready_records":
        return "Preparation set includes records ready for future hint creation review."
    if status == "preparation_set_created_all_held_or_blocked":
        return "Preparation set contains only held or blocked records."
    return f"Preparation set blocked: {status}."


def _preparation_scope_valid(
    set_review: ReviewedConceptReadbackHintCandidateSetTeacherReview,
    preparation_set: ReviewedConceptReadbackHintPreparationSet,
) -> bool:
    approved_ids = set(set_review.approved_candidate_ids)
    ready_ids = {
        record.source_hint_candidate_id
        for record in preparation_set.preparation_records
        if record.ready_for_future_task_working_memory_hint_creation_review
    }
    return ready_ids == approved_ids


def _safety_blocked_reasons(
    *,
    teacher_review_set_valid: bool,
    teacher_review_safety_audit_passed: bool,
    preparation_set_valid: bool,
    preparation_records_valid: bool,
    preparation_scope_valid: bool,
    no_actual_task_working_memory_hint_created: bool,
    no_working_memory_mutation: bool,
    no_task_behavior_change: bool,
    no_candidate_ordering_change: bool,
    no_action_selection: bool,
    no_action_execution: bool,
    no_memory_layer_write: bool,
    no_automatic_learning_approval: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not no_actual_task_working_memory_hint_created:
        reasons.append("blocked_forbidden_hint_creation_detected")
    if not no_working_memory_mutation:
        reasons.append("blocked_forbidden_working_memory_mutation_detected")
    if not (no_task_behavior_change and no_candidate_ordering_change):
        reasons.append("blocked_forbidden_behavior_change_detected")
    if not (no_action_selection and no_action_execution):
        reasons.append("blocked_forbidden_action_authority_detected")
    if not (no_memory_layer_write and no_automatic_learning_approval):
        reasons.append("blocked_forbidden_memory_write_detected")
    if not teacher_review_set_valid:
        reasons.append("blocked_invalid_teacher_review_set")
    if not teacher_review_safety_audit_passed:
        reasons.append("blocked_teacher_review_safety_audit_failed")
    if not preparation_set_valid:
        reasons.append("blocked_invalid_preparation_set")
    if not preparation_records_valid:
        reasons.append("blocked_invalid_preparation_records")
    if not preparation_scope_valid:
        reasons.append("blocked_invalid_preparation_records")
    return tuple(dict.fromkeys(reasons))


def _audit_status(blocked_reasons: tuple[str, ...]) -> str:
    if not blocked_reasons:
        return "passed"
    for status in (
        "blocked_forbidden_hint_creation_detected",
        "blocked_forbidden_working_memory_mutation_detected",
        "blocked_forbidden_behavior_change_detected",
        "blocked_forbidden_action_authority_detected",
        "blocked_forbidden_memory_write_detected",
        "blocked_invalid_teacher_review_set",
        "blocked_teacher_review_safety_audit_failed",
        "blocked_invalid_preparation_set",
        "blocked_invalid_preparation_records",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_invalid_preparation_records"


def _missing_candidate(
    review: ReviewedConceptReadbackHintCandidateTeacherReview,
) -> ReviewedConceptReadbackHintCandidate:
    return ReviewedConceptReadbackHintCandidate(
        readback_hint_candidate_id=f"missing:{review.source_hint_candidate_id}",
        schema_version="memory_engine_reviewed_concept_readback_hint_candidate_v0",
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=review.source_reviewed_concept_id,
        source_working_readback_preview_id="missing",
        source_working_readback_hint_preview_id="missing",
        source_memory_application_data_id="missing",
        concept_label=review.concept_label,
        hint_label=review.hint_label,
        hint_summary=review.hint_summary,
        hint_kind=review.hint_kind,
        hint_priority=0,
        task_handling_note="",
        scope_warning=review.scope_warning,
        counterexample_warning=review.counterexample_warning,
        candidate_status="blocked_invalid_preview",
        candidate_summary="Missing source candidate.",
        requires_teacher_review_before_application=True,
        requires_task_engine_application_package=True,
        requires_counterexample_monitoring=True,
        actual_task_working_memory_hint_created=False,
        applied_to_working_memory=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        candidate_ordering_changed=False,
        action_selection_created=False,
        action_execution_created=False,
        memory_layer_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=review.source_trace_refs,
    )


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _candidate(
    record: ReviewedConceptReadbackHintCandidate | dict[str, object],
) -> ReviewedConceptReadbackHintCandidate:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintCandidate)
        else ReviewedConceptReadbackHintCandidate.from_dict(dict(record))
    )


def _candidate_set(
    record: ReviewedConceptReadbackHintCandidateSet | dict[str, object],
) -> ReviewedConceptReadbackHintCandidateSet:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintCandidateSet)
        else ReviewedConceptReadbackHintCandidateSet.from_dict(dict(record))
    )


def _candidate_review(
    record: ReviewedConceptReadbackHintCandidateTeacherReview | dict[str, object],
) -> ReviewedConceptReadbackHintCandidateTeacherReview:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintCandidateTeacherReview)
        else ReviewedConceptReadbackHintCandidateTeacherReview.from_dict(dict(record))
    )


def _candidate_set_review(
    record: ReviewedConceptReadbackHintCandidateSetTeacherReview | dict[str, object],
) -> ReviewedConceptReadbackHintCandidateSetTeacherReview:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintCandidateSetTeacherReview)
        else ReviewedConceptReadbackHintCandidateSetTeacherReview.from_dict(dict(record))
    )


def _teacher_review_safety_audit(
    record: ReviewedConceptReadbackHintTeacherReviewSafetyAudit | dict[str, object],
) -> ReviewedConceptReadbackHintTeacherReviewSafetyAudit:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintTeacherReviewSafetyAudit)
        else ReviewedConceptReadbackHintTeacherReviewSafetyAudit.from_dict(dict(record))
    )


def _preparation_record(
    record: ReviewedConceptReadbackHintPreparationRecord | dict[str, object],
) -> ReviewedConceptReadbackHintPreparationRecord:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintPreparationRecord)
        else ReviewedConceptReadbackHintPreparationRecord.from_dict(dict(record))
    )


def _preparation_set(
    record: ReviewedConceptReadbackHintPreparationSet | dict[str, object],
) -> ReviewedConceptReadbackHintPreparationSet:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintPreparationSet)
        else ReviewedConceptReadbackHintPreparationSet.from_dict(dict(record))
    )


def _preparation_safety_audit(
    record: ReviewedConceptReadbackHintPreparationSafetyAudit | dict[str, object],
) -> ReviewedConceptReadbackHintPreparationSafetyAudit:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintPreparationSafetyAudit)
        else ReviewedConceptReadbackHintPreparationSafetyAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
