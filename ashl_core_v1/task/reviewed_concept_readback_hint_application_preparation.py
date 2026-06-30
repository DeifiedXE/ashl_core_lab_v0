"""Prepare teacher-approved TaskWorkingMemoryReadbackHint applications."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.task.reviewed_concept_readback_hint_application_teacher_review import (
    TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview,
    TaskWorkingMemoryReadbackHintApplicationTeacherReview,
    TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit,
    build_demo_all_held_task_working_memory_readback_hint_application_teacher_review,
    build_demo_conflict_detected_task_working_memory_readback_hint_application_teacher_review,
    build_demo_rejected_task_working_memory_readback_hint_application_teacher_review,
    build_demo_task_working_memory_readback_hint_application_teacher_review,
    validate_task_working_memory_readback_hint_application_preview_set_teacher_review,
    validate_task_working_memory_readback_hint_application_teacher_review,
    validate_task_working_memory_readback_hint_application_teacher_review_safety_audit,
)


SOURCE_ENGINE = "task_engine"
HINT_APPLICATION_PREPARATION_SCHEMA_VERSION = (
    "task_engine_reviewed_concept_readback_hint_application_preparation_v0"
)
HINT_APPLICATION_PREPARATION_SET_SCHEMA_VERSION = (
    "task_engine_reviewed_concept_readback_hint_application_preparation_set_v0"
)
HINT_APPLICATION_PREPARATION_SAFETY_AUDIT_SCHEMA_VERSION = (
    "task_engine_reviewed_concept_readback_hint_application_preparation_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Task Engine can convert teacher-approved "
    "TaskWorkingMemoryReadbackHint application previews into Working Memory "
    "application preparation records, without applying hints, mutating Working "
    "Memory, changing task behavior, changing candidate ordering, selecting "
    "actions, executing actions, or writing memory layers."
)
BLOCKED_CLAIMS = (
    "no_active_readback_hint_application",
    "no_working_memory_mutation",
    "no_task_behavior_change",
    "no_candidate_ordering_change",
    "no_selected_action_change",
    "no_final_action_change",
    "no_direct_command_change",
    "no_action_execution",
    "no_core_longterm_archive_anchor_write",
    "no_automatic_learning_approval",
)

ALLOWED_PREPARATION_STATUSES = {
    "prepared_for_future_working_memory_initialization_application",
    "held_for_more_evidence",
    "blocked_not_teacher_approved",
    "blocked_application_preview_rejected",
    "blocked_conflict_detected",
    "blocked_invalid_teacher_review",
    "blocked_invalid_application_preview",
    "blocked_forbidden_authority_detected",
}
ALLOWED_SET_PREPARATION_STATUSES = {
    "preparation_set_created_with_ready_application_records",
    "preparation_set_created_all_held_or_blocked",
    "blocked_invalid_teacher_review_set",
    "blocked_invalid_preparation_records",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_application_teacher_review_set",
    "blocked_application_teacher_review_safety_audit_failed",
    "blocked_invalid_application_preparation_set",
    "blocked_invalid_application_preparation_records",
    "blocked_forbidden_active_hint_application_detected",
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
class TaskWorkingMemoryReadbackHintApplicationPreparationRecord:
    hint_application_preparation_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_application_preview_id: str
    source_hint_application_preview_set_id: str
    source_hint_application_teacher_review_id: str
    source_hint_application_preview_set_teacher_review_id: str
    source_application_teacher_review_safety_audit_id: str
    source_task_working_memory_readback_hint_id: str
    concept_label: str
    hint_label: str
    hint_kind: str
    hint_priority: int
    hint_summary: str
    prepared_working_memory_slot: str
    prepared_application_scope: str
    prepared_visibility: str
    prepared_lifetime: str
    prepared_task_handling_note: str
    prepared_scope_warning: str | None
    prepared_counterexample_warning: str | None
    preparation_status: str
    preparation_summary: str
    ready_for_future_working_memory_initialization_application: bool
    requires_task_engine_application_package: bool
    requires_teacher_review_before_active_application: bool
    requires_counterexample_monitoring: bool
    applied_to_working_memory: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HINT_APPLICATION_PREPARATION_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_reviewed_concept_readback_hint_application_preparation_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
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
    ) -> "TaskWorkingMemoryReadbackHintApplicationPreparationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskWorkingMemoryReadbackHintApplicationPreparationSet:
    hint_application_preparation_set_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_application_preview_set_id: str
    source_hint_application_preview_set_teacher_review_id: str
    source_application_teacher_review_safety_audit_id: str
    source_task_working_memory_readback_hint_record_set_id: str
    concept_label: str
    application_preparation_records: tuple[
        TaskWorkingMemoryReadbackHintApplicationPreparationRecord,
        ...,
    ]
    prepared_record_ids: tuple[str, ...]
    held_record_ids: tuple[str, ...]
    blocked_record_ids: tuple[str, ...]
    prepared_hint_labels: tuple[str, ...]
    prepared_count: int
    held_count: int
    blocked_count: int
    set_preparation_status: str
    set_preparation_summary: str
    has_prepared_records_for_future_working_memory_initialization_application: bool
    applied_to_working_memory: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HINT_APPLICATION_PREPARATION_SET_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_reviewed_concept_readback_hint_application_preparation_set_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.set_preparation_status not in ALLOWED_SET_PREPARATION_STATUSES:
            raise ValueError(
                f"unknown set_preparation_status: {self.set_preparation_status}"
            )
        object.__setattr__(
            self,
            "application_preparation_records",
            tuple(
                item
                if isinstance(
                    item,
                    TaskWorkingMemoryReadbackHintApplicationPreparationRecord,
                )
                else TaskWorkingMemoryReadbackHintApplicationPreparationRecord.from_dict(
                    dict(item)
                )
                for item in self.application_preparation_records
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
    ) -> "TaskWorkingMemoryReadbackHintApplicationPreparationSet":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_application_preview_set_teacher_review_id: str | None
    source_hint_application_preparation_set_id: str | None
    application_teacher_review_set_valid: bool
    application_teacher_review_safety_audit_passed: bool
    application_preparation_records_valid: bool
    application_preparation_scope_valid: bool
    no_active_hint_application: bool
    no_working_memory_mutation: bool
    no_task_behavior_change: bool
    no_candidate_ordering_change: bool
    no_selected_action_change: bool
    no_final_action_change: bool
    no_direct_command_change: bool
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
        if self.schema_version != HINT_APPLICATION_PREPARATION_SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_reviewed_concept_readback_hint_application_preparation_safety_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
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
    ) -> "TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit":
        return cls(**dict(data))


def build_task_working_memory_readback_hint_application_preparation_record(
    *,
    application_teacher_review: (
        TaskWorkingMemoryReadbackHintApplicationTeacherReview | dict[str, object]
    ),
    application_preview_set_teacher_review: (
        TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview
        | dict[str, object]
    ),
    application_teacher_review_safety_audit: (
        TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit
        | dict[str, object]
    ),
) -> TaskWorkingMemoryReadbackHintApplicationPreparationRecord:
    review = _application_review(application_teacher_review)
    set_review = _application_set_review(application_preview_set_teacher_review)
    teacher_safety = _teacher_review_safety_audit(
        application_teacher_review_safety_audit
    )
    status = _preparation_status(review)
    return TaskWorkingMemoryReadbackHintApplicationPreparationRecord(
        hint_application_preparation_id=(
            "task_working_memory_readback_hint_application_preparation:"
            f"{review.source_hint_application_preview_id}"
        ),
        schema_version=HINT_APPLICATION_PREPARATION_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=review.source_reviewed_concept_id,
        source_hint_application_preview_id=review.source_hint_application_preview_id,
        source_hint_application_preview_set_id=review.source_hint_application_preview_set_id,
        source_hint_application_teacher_review_id=(
            review.hint_application_teacher_review_id
        ),
        source_hint_application_preview_set_teacher_review_id=(
            set_review.hint_application_preview_set_teacher_review_id
        ),
        source_application_teacher_review_safety_audit_id=teacher_safety.safety_audit_id,
        source_task_working_memory_readback_hint_id=(
            review.source_task_working_memory_readback_hint_id
        ),
        concept_label=review.concept_label,
        hint_label=review.hint_label,
        hint_kind=review.hint_kind,
        hint_priority=review.hint_priority,
        hint_summary=review.hint_summary,
        prepared_working_memory_slot=review.proposed_working_memory_slot,
        prepared_application_scope=review.proposed_application_scope,
        prepared_visibility=review.proposed_visibility,
        prepared_lifetime=review.proposed_lifetime,
        prepared_task_handling_note=review.task_handling_note,
        prepared_scope_warning=review.scope_warning,
        prepared_counterexample_warning=review.counterexample_warning,
        preparation_status=status,
        preparation_summary=_preparation_summary(status),
        ready_for_future_working_memory_initialization_application=(
            status == "prepared_for_future_working_memory_initialization_application"
        ),
        requires_task_engine_application_package=True,
        requires_teacher_review_before_active_application=True,
        requires_counterexample_monitoring=True,
        applied_to_working_memory=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        candidate_ordering_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_changed=False,
        execution_created=False,
        memory_layer_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_combined_trace_refs(
            review.source_trace_refs,
            set_review.source_trace_refs,
            teacher_safety.source_trace_refs,
        ),
    )


def validate_task_working_memory_readback_hint_application_preparation_record(
    record: TaskWorkingMemoryReadbackHintApplicationPreparationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        preparation = _preparation_record(record)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_preparation_record:{error}"]}
    errors: list[str] = []
    if preparation.preparation_status in {
        "blocked_invalid_teacher_review",
        "blocked_invalid_application_preview",
        "blocked_forbidden_authority_detected",
    }:
        errors.append(preparation.preparation_status)
    expected_ready = (
        preparation.preparation_status
        == "prepared_for_future_working_memory_initialization_application"
    )
    if (
        preparation.ready_for_future_working_memory_initialization_application
        is not expected_ready
    ):
        errors.append("ready_flag_mismatch")
    if expected_ready:
        if preparation.prepared_visibility != "advisory_only":
            errors.append("prepared_visibility_not_advisory_only")
        if preparation.prepared_application_scope != "future_task_initialization":
            errors.append("prepared_application_scope_not_future_task_initialization")
        if preparation.prepared_lifetime != "single_task":
            errors.append("prepared_lifetime_not_single_task")
    for flag in (
        "requires_task_engine_application_package",
        "requires_teacher_review_before_active_application",
        "requires_counterexample_monitoring",
    ):
        if getattr(preparation, flag) is not True:
            errors.append(f"{flag}_false")
    for flag in (
        "applied_to_working_memory",
        "working_memory_mutated",
        "task_behavior_changed",
        "candidate_ordering_changed",
        "selected_action_changed",
        "final_action_changed",
        "direct_command_changed",
        "execution_created",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(preparation, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "hint_application_preparation_id": preparation.hint_application_preparation_id,
        "preparation_status": preparation.preparation_status,
        "source_hint_application_preview_id": preparation.source_hint_application_preview_id,
    }


def build_task_working_memory_readback_hint_application_preparation_set(
    *,
    application_preview_set_teacher_review: (
        TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview
        | dict[str, object]
    ),
    application_teacher_review_safety_audit: (
        TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit
        | dict[str, object]
    ),
) -> TaskWorkingMemoryReadbackHintApplicationPreparationSet:
    set_review = _application_set_review(application_preview_set_teacher_review)
    teacher_safety = _teacher_review_safety_audit(
        application_teacher_review_safety_audit
    )
    records = tuple(
        build_task_working_memory_readback_hint_application_preparation_record(
            application_teacher_review=review,
            application_preview_set_teacher_review=set_review,
            application_teacher_review_safety_audit=teacher_safety,
        )
        for review in set_review.application_preview_reviews
    )
    status = _set_preparation_status(set_review, records)
    prepared_records = tuple(
        record
        for record in records
        if record.preparation_status
        == "prepared_for_future_working_memory_initialization_application"
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
    return TaskWorkingMemoryReadbackHintApplicationPreparationSet(
        hint_application_preparation_set_id=(
            "task_working_memory_readback_hint_application_preparation_set:"
            f"{set_review.source_reviewed_concept_id}"
        ),
        schema_version=HINT_APPLICATION_PREPARATION_SET_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=set_review.source_reviewed_concept_id,
        source_hint_application_preview_set_id=(
            set_review.source_hint_application_preview_set_id
        ),
        source_hint_application_preview_set_teacher_review_id=(
            set_review.hint_application_preview_set_teacher_review_id
        ),
        source_application_teacher_review_safety_audit_id=(
            teacher_safety.safety_audit_id
        ),
        source_task_working_memory_readback_hint_record_set_id=(
            set_review.source_task_working_memory_readback_hint_record_set_id
        ),
        concept_label=set_review.concept_label,
        application_preparation_records=records,
        prepared_record_ids=tuple(
            record.hint_application_preparation_id for record in prepared_records
        ),
        held_record_ids=tuple(
            record.hint_application_preparation_id for record in held_records
        ),
        blocked_record_ids=tuple(
            record.hint_application_preparation_id for record in blocked_records
        ),
        prepared_hint_labels=tuple(record.hint_label for record in prepared_records),
        prepared_count=len(prepared_records),
        held_count=len(held_records),
        blocked_count=len(blocked_records),
        set_preparation_status=status,
        set_preparation_summary=_set_preparation_summary(status),
        has_prepared_records_for_future_working_memory_initialization_application=bool(
            prepared_records
        )
        and status == "preparation_set_created_with_ready_application_records",
        applied_to_working_memory=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        candidate_ordering_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_changed=False,
        execution_created=False,
        memory_layer_write_performed=False,
        source_trace_refs=_combined_trace_refs(
            set_review.source_trace_refs,
            teacher_safety.source_trace_refs,
            *(record.source_trace_refs for record in records),
        ),
    )


def validate_task_working_memory_readback_hint_application_preparation_set(
    preparation_set: TaskWorkingMemoryReadbackHintApplicationPreparationSet
    | dict[str, object],
) -> dict[str, object]:
    try:
        record = _preparation_set(preparation_set)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_preparation_set:{error}"]}
    errors: list[str] = []
    if record.set_preparation_status.startswith("blocked_"):
        errors.append(record.set_preparation_status)
    record_validations = [
        validate_task_working_memory_readback_hint_application_preparation_record(item)
        for item in record.application_preparation_records
    ]
    if any(not validation["valid"] for validation in record_validations):
        errors.append("application_preparation_record_invalid")
    prepared_records = tuple(
        item
        for item in record.application_preparation_records
        if item.preparation_status
        == "prepared_for_future_working_memory_initialization_application"
    )
    held_records = tuple(
        item
        for item in record.application_preparation_records
        if item.preparation_status == "held_for_more_evidence"
    )
    blocked_records = tuple(
        item
        for item in record.application_preparation_records
        if item.preparation_status.startswith("blocked_")
    )
    if record.prepared_count != len(prepared_records):
        errors.append("prepared_count_mismatch")
    if record.held_count != len(held_records):
        errors.append("held_count_mismatch")
    if record.blocked_count != len(blocked_records):
        errors.append("blocked_count_mismatch")
    if (
        record.has_prepared_records_for_future_working_memory_initialization_application
        != bool(record.prepared_record_ids)
    ):
        errors.append("has_prepared_records_flag_mismatch")
    for flag in (
        "applied_to_working_memory",
        "working_memory_mutated",
        "task_behavior_changed",
        "candidate_ordering_changed",
        "selected_action_changed",
        "final_action_changed",
        "direct_command_changed",
        "execution_created",
        "memory_layer_write_performed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "hint_application_preparation_set_id": (
            record.hint_application_preparation_set_id
        ),
        "set_preparation_status": record.set_preparation_status,
        "prepared_count": record.prepared_count,
        "held_count": record.held_count,
        "blocked_count": record.blocked_count,
    }


def build_task_working_memory_readback_hint_application_preparation_safety_audit(
    *,
    application_preview_set_teacher_review: (
        TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview
        | dict[str, object]
    ),
    application_teacher_review_safety_audit: (
        TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit
        | dict[str, object]
    ),
    application_preparation_set: (
        TaskWorkingMemoryReadbackHintApplicationPreparationSet | dict[str, object]
    ),
) -> TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit:
    set_review = _application_set_review(application_preview_set_teacher_review)
    teacher_safety = _teacher_review_safety_audit(
        application_teacher_review_safety_audit
    )
    prep_set = _preparation_set(application_preparation_set)
    teacher_review_set_valid = bool(
        validate_task_working_memory_readback_hint_application_preview_set_teacher_review(
            set_review
        )["valid"]
    )
    teacher_review_safety_audit_passed = bool(
        validate_task_working_memory_readback_hint_application_teacher_review_safety_audit(
            teacher_safety
        )["valid"]
    )
    preparation_records_valid = all(
        validate_task_working_memory_readback_hint_application_preparation_record(
            record
        )["valid"]
        for record in prep_set.application_preparation_records
    )
    preparation_set_valid = bool(
        validate_task_working_memory_readback_hint_application_preparation_set(
            prep_set
        )["valid"]
    )
    preparation_scope_valid = _preparation_scope_valid(set_review, prep_set)
    no_active_hint_application = (
        prep_set.applied_to_working_memory is False
        and all(
            record.applied_to_working_memory is False
            for record in prep_set.application_preparation_records
        )
    )
    no_working_memory_mutation = (
        prep_set.working_memory_mutated is False
        and all(
            record.working_memory_mutated is False
            for record in prep_set.application_preparation_records
        )
    )
    no_task_behavior_change = (
        prep_set.task_behavior_changed is False
        and all(
            record.task_behavior_changed is False
            for record in prep_set.application_preparation_records
        )
    )
    no_candidate_ordering_change = (
        prep_set.candidate_ordering_changed is False
        and all(
            record.candidate_ordering_changed is False
            for record in prep_set.application_preparation_records
        )
    )
    no_selected_action_change = (
        prep_set.selected_action_changed is False
        and all(
            record.selected_action_changed is False
            for record in prep_set.application_preparation_records
        )
    )
    no_final_action_change = (
        prep_set.final_action_changed is False
        and all(
            record.final_action_changed is False
            for record in prep_set.application_preparation_records
        )
    )
    no_direct_command_change = (
        prep_set.direct_command_changed is False
        and all(
            record.direct_command_changed is False
            for record in prep_set.application_preparation_records
        )
    )
    no_action_execution = (
        prep_set.execution_created is False
        and all(
            record.execution_created is False
            for record in prep_set.application_preparation_records
        )
    )
    no_memory_layer_write = (
        prep_set.memory_layer_write_performed is False
        and all(
            record.memory_layer_write_performed is False
            for record in prep_set.application_preparation_records
        )
    )
    no_automatic_learning_approval = all(
        record.automatic_learning_approval_created is False
        for record in prep_set.application_preparation_records
    )
    blocked_reasons = _safety_blocked_reasons(
        application_teacher_review_set_valid=teacher_review_set_valid,
        application_teacher_review_safety_audit_passed=(
            teacher_review_safety_audit_passed
        ),
        application_preparation_set_valid=preparation_set_valid,
        application_preparation_records_valid=preparation_records_valid,
        application_preparation_scope_valid=preparation_scope_valid,
        no_active_hint_application=no_active_hint_application,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_candidate_ordering_change=no_candidate_ordering_change,
        no_selected_action_change=no_selected_action_change,
        no_final_action_change=no_final_action_change,
        no_direct_command_change=no_direct_command_change,
        no_action_execution=no_action_execution,
        no_memory_layer_write=no_memory_layer_write,
        no_automatic_learning_approval=no_automatic_learning_approval,
    )
    return TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit(
        safety_audit_id=(
            "task_working_memory_readback_hint_application_preparation_safety_audit:"
            f"{prep_set.source_reviewed_concept_id}"
        ),
        schema_version=HINT_APPLICATION_PREPARATION_SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=prep_set.source_reviewed_concept_id,
        source_hint_application_preview_set_teacher_review_id=(
            set_review.hint_application_preview_set_teacher_review_id
        ),
        source_hint_application_preparation_set_id=(
            prep_set.hint_application_preparation_set_id
        ),
        application_teacher_review_set_valid=teacher_review_set_valid,
        application_teacher_review_safety_audit_passed=(
            teacher_review_safety_audit_passed
        ),
        application_preparation_records_valid=preparation_records_valid,
        application_preparation_scope_valid=preparation_scope_valid,
        no_active_hint_application=no_active_hint_application,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_candidate_ordering_change=no_candidate_ordering_change,
        no_selected_action_change=no_selected_action_change,
        no_final_action_change=no_final_action_change,
        no_direct_command_change=no_direct_command_change,
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


def validate_task_working_memory_readback_hint_application_preparation_safety_audit(
    audit: TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit
    | dict[str, object],
) -> dict[str, object]:
    try:
        record = _preparation_safety_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed":
        errors.append(record.audit_status)
    for flag in (
        "application_teacher_review_set_valid",
        "application_teacher_review_safety_audit_passed",
        "application_preparation_records_valid",
        "application_preparation_scope_valid",
        "no_active_hint_application",
        "no_working_memory_mutation",
        "no_task_behavior_change",
        "no_candidate_ordering_change",
        "no_selected_action_change",
        "no_final_action_change",
        "no_direct_command_change",
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


def build_task_working_memory_readback_hint_application_preparation_bundle(
    teacher_review_payload: dict[str, object],
) -> dict[str, object]:
    set_review = _application_set_review(
        teacher_review_payload["hint_application_preview_set_teacher_review"]
    )
    teacher_safety = _teacher_review_safety_audit(
        teacher_review_payload["hint_application_teacher_review_safety_audit"]
    )
    preparation_set = build_task_working_memory_readback_hint_application_preparation_set(
        application_preview_set_teacher_review=set_review,
        application_teacher_review_safety_audit=teacher_safety,
    )
    safety = build_task_working_memory_readback_hint_application_preparation_safety_audit(
        application_preview_set_teacher_review=set_review,
        application_teacher_review_safety_audit=teacher_safety,
        application_preparation_set=preparation_set,
    )
    return {
        "hint_application_preparation_records": [
            record.to_dict()
            for record in preparation_set.application_preparation_records
        ],
        "hint_application_preparation_set": preparation_set.to_dict(),
        "hint_application_preparation_safety_audit": safety.to_dict(),
        "hint_application_preparation_set_validation": (
            validate_task_working_memory_readback_hint_application_preparation_set(
                preparation_set
            )
        ),
        "hint_application_preparation_safety_audit_validation": (
            validate_task_working_memory_readback_hint_application_preparation_safety_audit(
                safety
            )
        ),
        "safe_claim": SAFE_CLAIM,
    }


def build_demo_task_working_memory_readback_hint_application_preparation_set() -> (
    dict[str, object]
):
    return build_task_working_memory_readback_hint_application_preparation_bundle(
        build_demo_task_working_memory_readback_hint_application_teacher_review()
    )


def build_demo_task_working_memory_readback_hint_application_preparation_safety_audit() -> (
    TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit
):
    payload = build_demo_task_working_memory_readback_hint_application_preparation_set()
    return TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit.from_dict(
        payload["hint_application_preparation_safety_audit"]
    )


def build_demo_all_held_task_working_memory_readback_hint_application_preparation_set() -> (
    dict[str, object]
):
    return build_task_working_memory_readback_hint_application_preparation_bundle(
        build_demo_all_held_task_working_memory_readback_hint_application_teacher_review()
    )


def build_demo_rejected_task_working_memory_readback_hint_application_preparation_set() -> (
    dict[str, object]
):
    return build_task_working_memory_readback_hint_application_preparation_bundle(
        build_demo_rejected_task_working_memory_readback_hint_application_teacher_review()
    )


def build_demo_conflict_detected_task_working_memory_readback_hint_application_preparation_set() -> (
    dict[str, object]
):
    return build_task_working_memory_readback_hint_application_preparation_bundle(
        build_demo_conflict_detected_task_working_memory_readback_hint_application_teacher_review()
    )


def build_demo_blocked_forbidden_authority_application_preparation_set() -> (
    dict[str, object]
):
    payload = build_demo_task_working_memory_readback_hint_application_preparation_set()
    preparation_set = TaskWorkingMemoryReadbackHintApplicationPreparationSet.from_dict(
        payload["hint_application_preparation_set"]
    )
    records = list(preparation_set.application_preparation_records)
    first = dict(records[0].to_dict())
    first["applied_to_working_memory"] = True
    records[0] = TaskWorkingMemoryReadbackHintApplicationPreparationRecord.from_dict(
        first
    )
    preparation_set = TaskWorkingMemoryReadbackHintApplicationPreparationSet.from_dict(
        {
            **preparation_set.to_dict(),
            "application_preparation_records": [
                record.to_dict() for record in records
            ],
        }
    )
    teacher_payload = (
        build_demo_task_working_memory_readback_hint_application_teacher_review()
    )
    safety = build_task_working_memory_readback_hint_application_preparation_safety_audit(
        application_preview_set_teacher_review=teacher_payload[
            "hint_application_preview_set_teacher_review"
        ],
        application_teacher_review_safety_audit=teacher_payload[
            "hint_application_teacher_review_safety_audit"
        ],
        application_preparation_set=preparation_set,
    )
    return {
        **payload,
        "hint_application_preparation_records": [
            record.to_dict() for record in records
        ],
        "hint_application_preparation_set": preparation_set.to_dict(),
        "hint_application_preparation_set_validation": (
            validate_task_working_memory_readback_hint_application_preparation_set(
                preparation_set
            )
        ),
        "hint_application_preparation_safety_audit": safety.to_dict(),
        "hint_application_preparation_safety_audit_validation": (
            validate_task_working_memory_readback_hint_application_preparation_safety_audit(
                safety
            )
        ),
    }


def build_demo_blocked_task_working_memory_readback_hint_application_preparation_set(
    case: str,
) -> dict[str, object]:
    cases = {
        "rejected": build_demo_rejected_task_working_memory_readback_hint_application_preparation_set,
        "conflict": build_demo_conflict_detected_task_working_memory_readback_hint_application_preparation_set,
        "forbidden-authority": build_demo_blocked_forbidden_authority_application_preparation_set,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked application preparation case: {case}") from error


def _preparation_status(
    review: TaskWorkingMemoryReadbackHintApplicationTeacherReview,
) -> str:
    if any(
        (
            review.approved_for_active_hint_application,
            review.approved_for_working_memory_mutation,
            review.approved_for_candidate_ordering_change,
            review.approved_for_task_behavior_change,
            review.approved_for_selected_action_change,
            review.approved_for_final_action_change,
            review.approved_for_direct_command_change,
            review.approved_for_execution,
            review.approved_for_memory_layer_write,
            review.applied_to_working_memory,
            review.working_memory_mutated,
            review.task_behavior_changed,
            review.candidate_ordering_changed,
            review.selected_action_changed,
            review.final_action_changed,
            review.direct_command_changed,
            review.execution_created,
            review.memory_layer_write_performed,
            review.automatic_learning_approval_created,
        )
    ):
        return "blocked_forbidden_authority_detected"
    if not validate_task_working_memory_readback_hint_application_teacher_review(
        review
    )["valid"]:
        if review.teacher_review_status == "blocked_invalid_application_preview":
            return "blocked_invalid_application_preview"
        if review.teacher_review_status == "blocked_forbidden_authority_detected":
            return "blocked_forbidden_authority_detected"
        return "blocked_invalid_teacher_review"
    if (
        review.teacher_review_status
        == "approved_for_future_working_memory_application_preparation"
    ):
        return "prepared_for_future_working_memory_initialization_application"
    if review.teacher_review_status in {"held_for_more_evidence", "needs_more_evidence"}:
        return "held_for_more_evidence"
    if review.teacher_review_status == "rejected":
        return "blocked_application_preview_rejected"
    if review.teacher_review_status == "conflict_detected":
        return "blocked_conflict_detected"
    if review.teacher_review_status == "blocked_invalid_application_preview":
        return "blocked_invalid_application_preview"
    return "blocked_not_teacher_approved"


def _preparation_summary(status: str) -> str:
    if status == "prepared_for_future_working_memory_initialization_application":
        return "Application preview prepared as a future Working Memory initialization work order."
    if status == "held_for_more_evidence":
        return "Application preparation held for more evidence or scope review."
    if status == "blocked_application_preview_rejected":
        return "Application preparation blocked because the preview was rejected."
    if status == "blocked_conflict_detected":
        return "Application preparation blocked because the review found a conflict."
    return f"Application preparation not ready: {status}."


def _set_preparation_status(
    set_review: TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview,
    records: tuple[TaskWorkingMemoryReadbackHintApplicationPreparationRecord, ...],
) -> str:
    if (
        not validate_task_working_memory_readback_hint_application_preview_set_teacher_review(
            set_review
        )["valid"]
    ):
        return "blocked_invalid_teacher_review_set"
    if any(
        record.preparation_status == "blocked_forbidden_authority_detected"
        for record in records
    ):
        return "blocked_forbidden_authority_detected"
    if any(
        not validate_task_working_memory_readback_hint_application_preparation_record(
            record
        )["valid"]
        for record in records
    ):
        return "blocked_invalid_preparation_records"
    if any(
        record.preparation_status
        == "prepared_for_future_working_memory_initialization_application"
        for record in records
    ):
        return "preparation_set_created_with_ready_application_records"
    return "preparation_set_created_all_held_or_blocked"


def _set_preparation_summary(status: str) -> str:
    if status == "preparation_set_created_with_ready_application_records":
        return "Preparation set includes ready future Working Memory initialization records."
    if status == "preparation_set_created_all_held_or_blocked":
        return "Preparation set contains only held or blocked application records."
    return f"Application preparation set blocked: {status}."


def _preparation_scope_valid(
    set_review: TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview,
    preparation_set: TaskWorkingMemoryReadbackHintApplicationPreparationSet,
) -> bool:
    ready_source_ids = {
        record.source_hint_application_preview_id
        for record in preparation_set.application_preparation_records
        if record.preparation_status
        == "prepared_for_future_working_memory_initialization_application"
    }
    return set(set_review.approved_preview_ids) == ready_source_ids


def _safety_blocked_reasons(
    *,
    application_teacher_review_set_valid: bool,
    application_teacher_review_safety_audit_passed: bool,
    application_preparation_set_valid: bool,
    application_preparation_records_valid: bool,
    application_preparation_scope_valid: bool,
    no_active_hint_application: bool,
    no_working_memory_mutation: bool,
    no_task_behavior_change: bool,
    no_candidate_ordering_change: bool,
    no_selected_action_change: bool,
    no_final_action_change: bool,
    no_direct_command_change: bool,
    no_action_execution: bool,
    no_memory_layer_write: bool,
    no_automatic_learning_approval: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not no_active_hint_application:
        reasons.append("blocked_forbidden_active_hint_application_detected")
    if not no_working_memory_mutation:
        reasons.append("blocked_forbidden_working_memory_mutation_detected")
    if not (no_task_behavior_change and no_candidate_ordering_change):
        reasons.append("blocked_forbidden_behavior_change_detected")
    if not (
        no_selected_action_change
        and no_final_action_change
        and no_direct_command_change
        and no_action_execution
    ):
        reasons.append("blocked_forbidden_action_authority_detected")
    if not (no_memory_layer_write and no_automatic_learning_approval):
        reasons.append("blocked_forbidden_memory_write_detected")
    if not application_teacher_review_set_valid:
        reasons.append("blocked_invalid_application_teacher_review_set")
    if not application_teacher_review_safety_audit_passed:
        reasons.append("blocked_application_teacher_review_safety_audit_failed")
    if not application_preparation_set_valid:
        reasons.append("blocked_invalid_application_preparation_set")
    if not application_preparation_records_valid:
        reasons.append("blocked_invalid_application_preparation_records")
    if not application_preparation_scope_valid:
        reasons.append("blocked_invalid_application_preparation_records")
    return tuple(dict.fromkeys(reasons))


def _audit_status(blocked_reasons: tuple[str, ...]) -> str:
    if not blocked_reasons:
        return "passed"
    for status in (
        "blocked_forbidden_active_hint_application_detected",
        "blocked_forbidden_working_memory_mutation_detected",
        "blocked_forbidden_behavior_change_detected",
        "blocked_forbidden_action_authority_detected",
        "blocked_forbidden_memory_write_detected",
        "blocked_invalid_application_teacher_review_set",
        "blocked_application_teacher_review_safety_audit_failed",
        "blocked_invalid_application_preparation_set",
        "blocked_invalid_application_preparation_records",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_invalid_application_preparation_records"


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _application_review(
    record: TaskWorkingMemoryReadbackHintApplicationTeacherReview | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationTeacherReview:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationTeacherReview)
        else TaskWorkingMemoryReadbackHintApplicationTeacherReview.from_dict(dict(record))
    )


def _application_set_review(
    record: TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview
    | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview)
        else TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview.from_dict(
            dict(record)
        )
    )


def _teacher_review_safety_audit(
    record: TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit
    | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit)
        else TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit.from_dict(
            dict(record)
        )
    )


def _preparation_record(
    record: TaskWorkingMemoryReadbackHintApplicationPreparationRecord
    | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationPreparationRecord:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationPreparationRecord)
        else TaskWorkingMemoryReadbackHintApplicationPreparationRecord.from_dict(
            dict(record)
        )
    )


def _preparation_set(
    record: TaskWorkingMemoryReadbackHintApplicationPreparationSet
    | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationPreparationSet:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationPreparationSet)
        else TaskWorkingMemoryReadbackHintApplicationPreparationSet.from_dict(
            dict(record)
        )
    )


def _preparation_safety_audit(
    record: TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit
    | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit)
        else TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit.from_dict(
            dict(record)
        )
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
