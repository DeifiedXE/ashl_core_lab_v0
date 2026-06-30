"""Inactive TaskWorkingMemoryReadbackHint records from reviewed concept preparations."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.memory.reviewed_concept_readback_hint_preparation import (
    ReviewedConceptReadbackHintPreparationRecord,
    ReviewedConceptReadbackHintPreparationSafetyAudit,
    ReviewedConceptReadbackHintPreparationSet,
    build_demo_all_held_readback_hint_preparation_set,
    build_demo_blocked_forbidden_authority_preparation_set,
    build_demo_rejected_readback_hint_preparation_set,
    build_demo_reviewed_concept_readback_hint_preparation_set,
    validate_reviewed_concept_readback_hint_preparation_record,
    validate_reviewed_concept_readback_hint_preparation_safety_audit,
    validate_reviewed_concept_readback_hint_preparation_set,
)


SOURCE_ENGINE = "task_engine"
TASK_WORKING_MEMORY_READBACK_HINT_SCHEMA_VERSION = (
    "task_engine_reviewed_concept_working_memory_readback_hint_v0"
)
TASK_WORKING_MEMORY_READBACK_HINT_RECORD_SET_SCHEMA_VERSION = (
    "task_engine_reviewed_concept_working_memory_readback_hint_record_set_v0"
)
TASK_WORKING_MEMORY_READBACK_HINT_RECORD_SAFETY_AUDIT_SCHEMA_VERSION = (
    "task_engine_reviewed_concept_readback_hint_record_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Task Engine can create inactive TaskWorkingMemoryReadbackHint "
    "records from teacher-approved ReviewedConcept readback hint preparation "
    "records, without applying those hints to Working Memory, mutating Working "
    "Memory, changing task behavior, selecting actions, executing actions, or "
    "writing memory layers."
)
BLOCKED_CLAIMS = (
    "no_working_memory_mutation",
    "no_active_readback_hint_application",
    "no_task_behavior_change",
    "no_candidate_ordering_change",
    "no_selected_action_change",
    "no_final_action_change",
    "no_direct_command_change",
    "no_action_execution",
    "no_core_longterm_archive_anchor_write",
    "no_automatic_learning_approval",
)

ALLOWED_HINT_RECORD_STATUSES = {
    "hint_record_created_inactive",
    "held_for_more_evidence",
    "blocked_invalid_preparation",
    "blocked_preparation_not_ready",
    "blocked_conflict_detected",
    "blocked_forbidden_authority_detected",
}
ALLOWED_RECORD_SET_STATUSES = {
    "record_set_created_with_inactive_hints",
    "record_set_created_all_held_or_blocked",
    "blocked_invalid_preparation_set",
    "blocked_invalid_hint_records",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_preparation_set",
    "blocked_preparation_safety_audit_failed",
    "blocked_invalid_hint_record_set",
    "blocked_invalid_hint_records",
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
class TaskWorkingMemoryReadbackHint:
    task_working_memory_readback_hint_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_readback_hint_preparation_id: str
    source_readback_hint_preparation_set_id: str
    source_preparation_safety_audit_id: str
    concept_label: str
    hint_label: str
    hint_kind: str
    hint_priority: int
    hint_summary: str
    task_handling_note: str
    scope_warning: str | None
    counterexample_warning: str | None
    hint_record_status: str
    hint_record_summary: str
    available_for_future_working_memory_application_review: bool
    requires_teacher_review_before_application: bool
    requires_task_engine_application_package: bool
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
        if self.schema_version != TASK_WORKING_MEMORY_READBACK_HINT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_reviewed_concept_working_memory_readback_hint_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.hint_record_status not in ALLOWED_HINT_RECORD_STATUSES:
            raise ValueError(f"unknown hint_record_status: {self.hint_record_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TaskWorkingMemoryReadbackHint":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskWorkingMemoryReadbackHintRecordSet:
    task_working_memory_readback_hint_record_set_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_readback_hint_preparation_set_id: str
    source_preparation_safety_audit_id: str
    concept_label: str
    hint_records: tuple[TaskWorkingMemoryReadbackHint, ...]
    created_hint_record_ids: tuple[str, ...]
    held_hint_record_ids: tuple[str, ...]
    blocked_hint_record_ids: tuple[str, ...]
    created_hint_labels: tuple[str, ...]
    created_count: int
    held_count: int
    blocked_count: int
    record_set_status: str
    record_set_summary: str
    has_inactive_hints_for_future_application_review: bool
    applied_to_working_memory: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    candidate_ordering_changed: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TASK_WORKING_MEMORY_READBACK_HINT_RECORD_SET_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_reviewed_concept_working_memory_readback_hint_record_set_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.record_set_status not in ALLOWED_RECORD_SET_STATUSES:
            raise ValueError(f"unknown record_set_status: {self.record_set_status}")
        object.__setattr__(
            self,
            "hint_records",
            tuple(
                item
                if isinstance(item, TaskWorkingMemoryReadbackHint)
                else TaskWorkingMemoryReadbackHint.from_dict(dict(item))
                for item in self.hint_records
            ),
        )
        for name in (
            "created_hint_record_ids",
            "held_hint_record_ids",
            "blocked_hint_record_ids",
            "created_hint_labels",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "TaskWorkingMemoryReadbackHintRecordSet":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskWorkingMemoryReadbackHintRecordSafetyAudit:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_readback_hint_preparation_set_id: str | None
    source_task_working_memory_readback_hint_record_set_id: str | None
    preparation_set_valid: bool
    preparation_safety_audit_passed: bool
    hint_records_valid: bool
    hint_record_scope_valid: bool
    actual_task_working_memory_readback_hint_records_created: bool
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
        if self.schema_version != TASK_WORKING_MEMORY_READBACK_HINT_RECORD_SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_reviewed_concept_readback_hint_record_safety_audit_v0"
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
    ) -> "TaskWorkingMemoryReadbackHintRecordSafetyAudit":
        return cls(**dict(data))


def build_task_working_memory_readback_hint(
    *,
    readback_hint_preparation: (
        ReviewedConceptReadbackHintPreparationRecord | dict[str, object]
    ),
    readback_hint_preparation_set: (
        ReviewedConceptReadbackHintPreparationSet | dict[str, object]
    ),
    preparation_safety_audit: (
        ReviewedConceptReadbackHintPreparationSafetyAudit | dict[str, object]
    ),
) -> TaskWorkingMemoryReadbackHint:
    preparation = _preparation_record(readback_hint_preparation)
    preparation_set = _preparation_set(readback_hint_preparation_set)
    safety = _preparation_safety_audit(preparation_safety_audit)
    status = _hint_record_status(preparation)
    return TaskWorkingMemoryReadbackHint(
        task_working_memory_readback_hint_id=(
            "task_working_memory_readback_hint:"
            f"{preparation.readback_hint_preparation_id}"
        ),
        schema_version=TASK_WORKING_MEMORY_READBACK_HINT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=preparation.source_reviewed_concept_id,
        source_readback_hint_preparation_id=preparation.readback_hint_preparation_id,
        source_readback_hint_preparation_set_id=(
            preparation_set.readback_hint_preparation_set_id
        ),
        source_preparation_safety_audit_id=safety.safety_audit_id,
        concept_label=preparation.concept_label,
        hint_label=preparation.hint_label,
        hint_kind=preparation.hint_kind,
        hint_priority=preparation.hint_priority,
        hint_summary=preparation.hint_summary,
        task_handling_note=preparation.prepared_task_handling_note,
        scope_warning=preparation.prepared_scope_warning,
        counterexample_warning=preparation.prepared_counterexample_warning,
        hint_record_status=status,
        hint_record_summary=_hint_record_summary(status),
        available_for_future_working_memory_application_review=(
            status == "hint_record_created_inactive"
        ),
        requires_teacher_review_before_application=True,
        requires_task_engine_application_package=True,
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
            preparation.source_trace_refs,
            preparation_set.source_trace_refs,
            safety.source_trace_refs,
        ),
    )


def validate_task_working_memory_readback_hint(
    hint: TaskWorkingMemoryReadbackHint | dict[str, object],
) -> dict[str, object]:
    try:
        record = _hint_record(hint)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_hint_record:{error}"]}
    errors: list[str] = []
    if record.hint_record_status == "blocked_forbidden_authority_detected":
        errors.append(record.hint_record_status)
    expected_available = record.hint_record_status == "hint_record_created_inactive"
    if record.available_for_future_working_memory_application_review is not expected_available:
        errors.append("available_for_future_application_flag_mismatch")
    for flag in (
        "requires_teacher_review_before_application",
        "requires_task_engine_application_package",
        "requires_counterexample_monitoring",
    ):
        if getattr(record, flag) is not True:
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
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "task_working_memory_readback_hint_id": record.task_working_memory_readback_hint_id,
        "hint_record_status": record.hint_record_status,
    }


def build_task_working_memory_readback_hint_record_set(
    *,
    readback_hint_preparation_set: (
        ReviewedConceptReadbackHintPreparationSet | dict[str, object]
    ),
    preparation_safety_audit: (
        ReviewedConceptReadbackHintPreparationSafetyAudit | dict[str, object]
    ),
) -> TaskWorkingMemoryReadbackHintRecordSet:
    preparation_set = _preparation_set(readback_hint_preparation_set)
    safety = _preparation_safety_audit(preparation_safety_audit)
    records = tuple(
        build_task_working_memory_readback_hint(
            readback_hint_preparation=preparation,
            readback_hint_preparation_set=preparation_set,
            preparation_safety_audit=safety,
        )
        for preparation in preparation_set.preparation_records
    )
    status = _record_set_status(preparation_set, safety, records)
    created_records = tuple(
        record
        for record in records
        if record.hint_record_status == "hint_record_created_inactive"
    )
    held_records = tuple(
        record for record in records if record.hint_record_status == "held_for_more_evidence"
    )
    blocked_records = tuple(
        record for record in records if record.hint_record_status.startswith("blocked_")
    )
    return TaskWorkingMemoryReadbackHintRecordSet(
        task_working_memory_readback_hint_record_set_id=(
            "task_working_memory_readback_hint_record_set:"
            f"{preparation_set.source_reviewed_concept_id}"
        ),
        schema_version=TASK_WORKING_MEMORY_READBACK_HINT_RECORD_SET_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=preparation_set.source_reviewed_concept_id,
        source_readback_hint_preparation_set_id=(
            preparation_set.readback_hint_preparation_set_id
        ),
        source_preparation_safety_audit_id=safety.safety_audit_id,
        concept_label=preparation_set.concept_label,
        hint_records=records,
        created_hint_record_ids=tuple(
            record.task_working_memory_readback_hint_id for record in created_records
        ),
        held_hint_record_ids=tuple(
            record.task_working_memory_readback_hint_id for record in held_records
        ),
        blocked_hint_record_ids=tuple(
            record.task_working_memory_readback_hint_id for record in blocked_records
        ),
        created_hint_labels=tuple(record.hint_label for record in created_records),
        created_count=len(created_records),
        held_count=len(held_records),
        blocked_count=len(blocked_records),
        record_set_status=status,
        record_set_summary=_record_set_summary(status),
        has_inactive_hints_for_future_application_review=bool(created_records)
        and status == "record_set_created_with_inactive_hints",
        applied_to_working_memory=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        candidate_ordering_changed=False,
        memory_layer_write_performed=False,
        source_trace_refs=_combined_trace_refs(
            preparation_set.source_trace_refs,
            safety.source_trace_refs,
            *(record.source_trace_refs for record in records),
        ),
    )


def validate_task_working_memory_readback_hint_record_set(
    record_set: TaskWorkingMemoryReadbackHintRecordSet | dict[str, object],
) -> dict[str, object]:
    try:
        record = _hint_record_set(record_set)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_hint_record_set:{error}"]}
    errors: list[str] = []
    if record.record_set_status.startswith("blocked_"):
        errors.append(record.record_set_status)
    record_validations = [
        validate_task_working_memory_readback_hint(item) for item in record.hint_records
    ]
    if any(not validation["valid"] for validation in record_validations):
        errors.append("hint_record_invalid")
    created_records = tuple(
        item for item in record.hint_records if item.hint_record_status == "hint_record_created_inactive"
    )
    held_records = tuple(
        item for item in record.hint_records if item.hint_record_status == "held_for_more_evidence"
    )
    blocked_records = tuple(
        item for item in record.hint_records if item.hint_record_status.startswith("blocked_")
    )
    if record.created_count != len(created_records):
        errors.append("created_count_mismatch")
    if record.held_count != len(held_records):
        errors.append("held_count_mismatch")
    if record.blocked_count != len(blocked_records):
        errors.append("blocked_count_mismatch")
    if record.has_inactive_hints_for_future_application_review != bool(
        record.created_hint_record_ids
    ):
        errors.append("has_inactive_hints_flag_mismatch")
    for flag in (
        "applied_to_working_memory",
        "working_memory_mutated",
        "task_behavior_changed",
        "candidate_ordering_changed",
        "memory_layer_write_performed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "task_working_memory_readback_hint_record_set_id": (
            record.task_working_memory_readback_hint_record_set_id
        ),
        "record_set_status": record.record_set_status,
        "created_count": record.created_count,
        "held_count": record.held_count,
        "blocked_count": record.blocked_count,
    }


def build_task_working_memory_readback_hint_record_safety_audit(
    *,
    readback_hint_preparation_set: (
        ReviewedConceptReadbackHintPreparationSet | dict[str, object]
    ),
    preparation_safety_audit: (
        ReviewedConceptReadbackHintPreparationSafetyAudit | dict[str, object]
    ),
    hint_record_set: TaskWorkingMemoryReadbackHintRecordSet | dict[str, object],
) -> TaskWorkingMemoryReadbackHintRecordSafetyAudit:
    preparation_set = _preparation_set(readback_hint_preparation_set)
    preparation_safety = _preparation_safety_audit(preparation_safety_audit)
    record_set = _hint_record_set(hint_record_set)
    preparation_set_valid = bool(
        validate_reviewed_concept_readback_hint_preparation_set(
            preparation_set
        )["valid"]
    )
    preparation_safety_audit_passed = bool(
        validate_reviewed_concept_readback_hint_preparation_safety_audit(
            preparation_safety
        )["valid"]
    )
    hint_records_valid = all(
        validate_task_working_memory_readback_hint(record)["valid"]
        for record in record_set.hint_records
    )
    hint_record_set_valid = bool(
        validate_task_working_memory_readback_hint_record_set(record_set)["valid"]
    )
    hint_record_scope_valid = _hint_record_scope_valid(preparation_set, record_set)
    no_working_memory_mutation = (
        record_set.applied_to_working_memory is False
        and record_set.working_memory_mutated is False
        and all(
            record.applied_to_working_memory is False
            and record.working_memory_mutated is False
            for record in record_set.hint_records
        )
    )
    no_task_behavior_change = (
        record_set.task_behavior_changed is False
        and all(record.task_behavior_changed is False for record in record_set.hint_records)
    )
    no_candidate_ordering_change = (
        record_set.candidate_ordering_changed is False
        and all(
            record.candidate_ordering_changed is False
            for record in record_set.hint_records
        )
    )
    no_selected_action_change = all(
        record.selected_action_changed is False for record in record_set.hint_records
    )
    no_final_action_change = all(
        record.final_action_changed is False for record in record_set.hint_records
    )
    no_direct_command_change = all(
        record.direct_command_changed is False for record in record_set.hint_records
    )
    no_action_execution = all(
        record.execution_created is False for record in record_set.hint_records
    )
    no_memory_layer_write = (
        record_set.memory_layer_write_performed is False
        and all(
            record.memory_layer_write_performed is False
            for record in record_set.hint_records
        )
    )
    no_automatic_learning_approval = all(
        record.automatic_learning_approval_created is False
        for record in record_set.hint_records
    )
    blocked_reasons = _safety_blocked_reasons(
        preparation_set_valid=preparation_set_valid,
        preparation_safety_audit_passed=preparation_safety_audit_passed,
        hint_record_set_valid=hint_record_set_valid,
        hint_records_valid=hint_records_valid,
        hint_record_scope_valid=hint_record_scope_valid,
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
    return TaskWorkingMemoryReadbackHintRecordSafetyAudit(
        safety_audit_id=(
            "task_working_memory_readback_hint_record_safety_audit:"
            f"{record_set.source_reviewed_concept_id}"
        ),
        schema_version=TASK_WORKING_MEMORY_READBACK_HINT_RECORD_SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=record_set.source_reviewed_concept_id,
        source_readback_hint_preparation_set_id=(
            preparation_set.readback_hint_preparation_set_id
        ),
        source_task_working_memory_readback_hint_record_set_id=(
            record_set.task_working_memory_readback_hint_record_set_id
        ),
        preparation_set_valid=preparation_set_valid,
        preparation_safety_audit_passed=preparation_safety_audit_passed,
        hint_records_valid=hint_records_valid,
        hint_record_scope_valid=hint_record_scope_valid,
        actual_task_working_memory_readback_hint_records_created=bool(
            record_set.created_hint_record_ids
        ),
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
            preparation_set.source_trace_refs,
            preparation_safety.source_trace_refs,
            record_set.source_trace_refs,
        ),
    )


def validate_task_working_memory_readback_hint_record_safety_audit(
    audit: TaskWorkingMemoryReadbackHintRecordSafetyAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _hint_record_safety_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed":
        errors.append(record.audit_status)
    for flag in (
        "preparation_set_valid",
        "preparation_safety_audit_passed",
        "hint_records_valid",
        "hint_record_scope_valid",
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
        "actual_task_working_memory_readback_hint_records_created": (
            record.actual_task_working_memory_readback_hint_records_created
        ),
    }


def build_task_working_memory_readback_hint_record_bundle(
    preparation_payload: dict[str, object],
) -> dict[str, object]:
    preparation_set = _preparation_set(preparation_payload["readback_hint_preparation_set"])
    preparation_safety = _preparation_safety_audit(
        preparation_payload["readback_hint_preparation_safety_audit"]
    )
    record_set = build_task_working_memory_readback_hint_record_set(
        readback_hint_preparation_set=preparation_set,
        preparation_safety_audit=preparation_safety,
    )
    safety = build_task_working_memory_readback_hint_record_safety_audit(
        readback_hint_preparation_set=preparation_set,
        preparation_safety_audit=preparation_safety,
        hint_record_set=record_set,
    )
    return {
        "task_working_memory_readback_hint_records": [
            record.to_dict() for record in record_set.hint_records
        ],
        "task_working_memory_readback_hint_record_set": record_set.to_dict(),
        "task_working_memory_readback_hint_record_safety_audit": safety.to_dict(),
        "task_working_memory_readback_hint_record_set_validation": (
            validate_task_working_memory_readback_hint_record_set(record_set)
        ),
        "task_working_memory_readback_hint_record_safety_audit_validation": (
            validate_task_working_memory_readback_hint_record_safety_audit(safety)
        ),
        "safe_claim": SAFE_CLAIM,
    }


def build_demo_task_working_memory_readback_hint_record_set() -> dict[str, object]:
    return build_task_working_memory_readback_hint_record_bundle(
        build_demo_reviewed_concept_readback_hint_preparation_set()
    )


def build_demo_task_working_memory_readback_hint_record_safety_audit() -> (
    TaskWorkingMemoryReadbackHintRecordSafetyAudit
):
    payload = build_demo_task_working_memory_readback_hint_record_set()
    return TaskWorkingMemoryReadbackHintRecordSafetyAudit.from_dict(
        payload["task_working_memory_readback_hint_record_safety_audit"]
    )


def build_demo_all_held_task_working_memory_readback_hint_record_set() -> dict[str, object]:
    return build_task_working_memory_readback_hint_record_bundle(
        build_demo_all_held_readback_hint_preparation_set()
    )


def build_demo_blocked_invalid_preparation_hint_record_set() -> dict[str, object]:
    return build_task_working_memory_readback_hint_record_bundle(
        build_demo_rejected_readback_hint_preparation_set()
    )


def build_demo_blocked_forbidden_authority_hint_record_set() -> dict[str, object]:
    payload = build_demo_task_working_memory_readback_hint_record_set()
    record_set = TaskWorkingMemoryReadbackHintRecordSet.from_dict(
        payload["task_working_memory_readback_hint_record_set"]
    )
    records = list(record_set.hint_records)
    first = dict(records[0].to_dict())
    first["working_memory_mutated"] = True
    records[0] = TaskWorkingMemoryReadbackHint.from_dict(first)
    record_set = TaskWorkingMemoryReadbackHintRecordSet.from_dict(
        {
            **record_set.to_dict(),
            "hint_records": [record.to_dict() for record in records],
        }
    )
    preparation_payload = build_demo_reviewed_concept_readback_hint_preparation_set()
    safety = build_task_working_memory_readback_hint_record_safety_audit(
        readback_hint_preparation_set=preparation_payload[
            "readback_hint_preparation_set"
        ],
        preparation_safety_audit=preparation_payload[
            "readback_hint_preparation_safety_audit"
        ],
        hint_record_set=record_set,
    )
    return {
        **payload,
        "task_working_memory_readback_hint_records": [
            record.to_dict() for record in records
        ],
        "task_working_memory_readback_hint_record_set": record_set.to_dict(),
        "task_working_memory_readback_hint_record_set_validation": (
            validate_task_working_memory_readback_hint_record_set(record_set)
        ),
        "task_working_memory_readback_hint_record_safety_audit": safety.to_dict(),
        "task_working_memory_readback_hint_record_safety_audit_validation": (
            validate_task_working_memory_readback_hint_record_safety_audit(safety)
        ),
    }


def build_demo_blocked_task_working_memory_readback_hint_record_set(
    case: str,
) -> dict[str, object]:
    cases = {
        "invalid-preparation": build_demo_blocked_invalid_preparation_hint_record_set,
        "forbidden-authority": build_demo_blocked_forbidden_authority_hint_record_set,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked hint record case: {case}") from error


def _hint_record_status(preparation: ReviewedConceptReadbackHintPreparationRecord) -> str:
    if not validate_reviewed_concept_readback_hint_preparation_record(preparation)[
        "valid"
    ]:
        return "blocked_invalid_preparation"
    if any(
        (
            preparation.actual_task_working_memory_hint_created,
            preparation.applied_to_working_memory,
            preparation.working_memory_mutated,
            preparation.task_behavior_changed,
            preparation.candidate_ordering_changed,
            preparation.action_selection_created,
            preparation.action_execution_created,
            preparation.memory_layer_write_performed,
        )
    ):
        return "blocked_forbidden_authority_detected"
    if preparation.preparation_status == "prepared_for_future_hint_creation_review":
        return "hint_record_created_inactive"
    if preparation.preparation_status == "held_for_more_evidence":
        return "held_for_more_evidence"
    if preparation.preparation_status == "blocked_conflict_detected":
        return "blocked_conflict_detected"
    if preparation.preparation_status.startswith("blocked_"):
        return "blocked_invalid_preparation"
    return "blocked_preparation_not_ready"


def _hint_record_summary(status: str) -> str:
    if status == "hint_record_created_inactive":
        return "Inactive TaskWorkingMemoryReadbackHint record created for future application review."
    if status == "held_for_more_evidence":
        return "Hint record held because preparation needs more evidence."
    if status == "blocked_conflict_detected":
        return "Hint record blocked because preparation contains a conflict."
    return f"Hint record not created as active Working Memory state: {status}."


def _record_set_status(
    preparation_set: ReviewedConceptReadbackHintPreparationSet,
    preparation_safety: ReviewedConceptReadbackHintPreparationSafetyAudit,
    records: tuple[TaskWorkingMemoryReadbackHint, ...],
) -> str:
    if (
        not validate_reviewed_concept_readback_hint_preparation_set(preparation_set)[
            "valid"
        ]
        or not validate_reviewed_concept_readback_hint_preparation_safety_audit(
            preparation_safety
        )["valid"]
    ):
        return "blocked_invalid_preparation_set"
    if any(record.hint_record_status == "blocked_forbidden_authority_detected" for record in records):
        return "blocked_forbidden_authority_detected"
    if any(
        not validate_task_working_memory_readback_hint(record)["valid"]
        for record in records
    ):
        return "blocked_invalid_hint_records"
    if any(record.hint_record_status == "hint_record_created_inactive" for record in records):
        return "record_set_created_with_inactive_hints"
    return "record_set_created_all_held_or_blocked"


def _record_set_summary(status: str) -> str:
    if status == "record_set_created_with_inactive_hints":
        return "Record set includes inactive hints for future Working Memory application review."
    if status == "record_set_created_all_held_or_blocked":
        return "Record set contains only held or blocked hint records."
    return f"Hint record set blocked: {status}."


def _hint_record_scope_valid(
    preparation_set: ReviewedConceptReadbackHintPreparationSet,
    record_set: TaskWorkingMemoryReadbackHintRecordSet,
) -> bool:
    prepared_ids = set(preparation_set.prepared_record_ids)
    inactive_source_ids = {
        record.source_readback_hint_preparation_id
        for record in record_set.hint_records
        if record.hint_record_status == "hint_record_created_inactive"
    }
    return prepared_ids == inactive_source_ids


def _safety_blocked_reasons(
    *,
    preparation_set_valid: bool,
    preparation_safety_audit_passed: bool,
    hint_record_set_valid: bool,
    hint_records_valid: bool,
    hint_record_scope_valid: bool,
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
    if not preparation_set_valid:
        reasons.append("blocked_invalid_preparation_set")
    if not preparation_safety_audit_passed:
        reasons.append("blocked_preparation_safety_audit_failed")
    if not hint_record_set_valid:
        reasons.append("blocked_invalid_hint_record_set")
    if not hint_records_valid:
        reasons.append("blocked_invalid_hint_records")
    if not hint_record_scope_valid:
        reasons.append("blocked_invalid_hint_records")
    return tuple(dict.fromkeys(reasons))


def _audit_status(blocked_reasons: tuple[str, ...]) -> str:
    if not blocked_reasons:
        return "passed"
    for status in (
        "blocked_forbidden_working_memory_mutation_detected",
        "blocked_forbidden_behavior_change_detected",
        "blocked_forbidden_action_authority_detected",
        "blocked_forbidden_memory_write_detected",
        "blocked_invalid_preparation_set",
        "blocked_preparation_safety_audit_failed",
        "blocked_invalid_hint_record_set",
        "blocked_invalid_hint_records",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_invalid_hint_records"


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


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


def _hint_record(
    record: TaskWorkingMemoryReadbackHint | dict[str, object],
) -> TaskWorkingMemoryReadbackHint:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHint)
        else TaskWorkingMemoryReadbackHint.from_dict(dict(record))
    )


def _hint_record_set(
    record: TaskWorkingMemoryReadbackHintRecordSet | dict[str, object],
) -> TaskWorkingMemoryReadbackHintRecordSet:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintRecordSet)
        else TaskWorkingMemoryReadbackHintRecordSet.from_dict(dict(record))
    )


def _hint_record_safety_audit(
    record: TaskWorkingMemoryReadbackHintRecordSafetyAudit | dict[str, object],
) -> TaskWorkingMemoryReadbackHintRecordSafetyAudit:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintRecordSafetyAudit)
        else TaskWorkingMemoryReadbackHintRecordSafetyAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
