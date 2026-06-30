"""Apply prepared readback hints to future Task Working Memory initialization."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.task.reviewed_concept_readback_hint_application_preparation import (
    TaskWorkingMemoryReadbackHintApplicationPreparationRecord,
    TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit,
    TaskWorkingMemoryReadbackHintApplicationPreparationSet,
    build_demo_all_held_task_working_memory_readback_hint_application_preparation_set,
    build_demo_task_working_memory_readback_hint_application_preparation_set,
    validate_task_working_memory_readback_hint_application_preparation_record,
    validate_task_working_memory_readback_hint_application_preparation_safety_audit,
    validate_task_working_memory_readback_hint_application_preparation_set,
)


SOURCE_ENGINE = "task_engine"
APPLICATION_SCHEMA_VERSION = (
    "task_engine_future_task_working_memory_readback_hint_application_v0"
)
APPLICATION_SET_SCHEMA_VERSION = (
    "task_engine_future_task_working_memory_readback_hint_application_set_v0"
)
READBACK_SNAPSHOT_SCHEMA_VERSION = (
    "task_engine_future_task_working_memory_initialization_readback_snapshot_v0"
)
APPLICATION_SAFETY_AUDIT_SCHEMA_VERSION = (
    "task_engine_future_task_working_memory_readback_hint_application_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Task Engine can apply prepared reviewed-concept readback "
    "hints into newly initialized future Task Working Memory as advisory-only, "
    "single-task readback hints, without mutating running tasks, changing "
    "candidate ordering, changing task behavior, selecting actions, executing "
    "actions, or writing memory layers."
)
BLOCKED_CLAIMS = (
    "no_running_task_mutation",
    "no_candidate_ordering_change",
    "no_task_behavior_change",
    "no_selected_action_change",
    "no_final_action_change",
    "no_direct_command_change",
    "no_action_execution",
    "no_core_longterm_archive_anchor_write",
    "no_automatic_learning_approval",
)

ALLOWED_APPLICATION_STATUSES = {
    "applied_to_new_task_working_memory_initialization",
    "held_for_more_evidence",
    "blocked_invalid_preparation",
    "blocked_preparation_not_ready",
    "blocked_running_task_mutation_attempt",
    "blocked_forbidden_authority_detected",
}
ALLOWED_APPLICATION_SET_STATUSES = {
    "application_set_created_with_advisory_hints",
    "application_set_created_all_held_or_blocked",
    "blocked_invalid_preparation_set",
    "blocked_invalid_application_records",
    "blocked_running_task_mutation_attempt",
    "blocked_forbidden_authority_detected",
}
ALLOWED_SNAPSHOT_STATUSES = {
    "snapshot_created_with_advisory_readback_hints",
    "snapshot_created_empty",
    "blocked_invalid_application_set",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_application_preparation_set",
    "blocked_application_preparation_safety_audit_failed",
    "blocked_invalid_application_set",
    "blocked_invalid_readback_snapshot",
    "blocked_running_task_mutation_detected",
    "blocked_non_advisory_hint_detected",
    "blocked_persistent_hint_lifetime_detected",
    "blocked_forbidden_ordering_change_detected",
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
class FutureTaskWorkingMemoryReadbackHintApplicationRecord:
    future_task_readback_hint_application_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_application_preparation_id: str
    source_hint_application_preparation_set_id: str
    source_application_preparation_safety_audit_id: str
    source_task_working_memory_readback_hint_id: str
    target_task_working_memory_id: str
    target_task_initialization_id: str
    concept_label: str
    hint_label: str
    hint_kind: str
    hint_priority: int
    hint_summary: str
    applied_working_memory_slot: str
    application_scope: str
    visibility: str
    lifetime: str
    task_handling_note: str
    scope_warning: str | None
    counterexample_warning: str | None
    application_status: str
    application_summary: str
    applied_to_new_task_working_memory_initialization: bool
    applied_to_running_task: bool
    working_memory_mutated: bool
    advisory_only: bool
    candidate_ordering_changed: bool
    task_behavior_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != APPLICATION_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_future_task_working_memory_readback_hint_application_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.application_status not in ALLOWED_APPLICATION_STATUSES:
            raise ValueError(f"unknown application_status: {self.application_status}")
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
    ) -> "FutureTaskWorkingMemoryReadbackHintApplicationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FutureTaskWorkingMemoryReadbackHintApplicationSet:
    future_task_readback_hint_application_set_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_application_preparation_set_id: str
    source_application_preparation_safety_audit_id: str
    target_task_working_memory_id: str
    target_task_initialization_id: str
    concept_label: str
    application_records: tuple[
        FutureTaskWorkingMemoryReadbackHintApplicationRecord,
        ...,
    ]
    applied_record_ids: tuple[str, ...]
    held_record_ids: tuple[str, ...]
    blocked_record_ids: tuple[str, ...]
    applied_hint_labels: tuple[str, ...]
    applied_count: int
    held_count: int
    blocked_count: int
    application_set_status: str
    application_set_summary: str
    has_advisory_readback_hints_applied_to_new_task_initialization: bool
    applied_to_running_task: bool
    working_memory_mutated: bool
    candidate_ordering_changed: bool
    task_behavior_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != APPLICATION_SET_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_future_task_working_memory_readback_hint_application_set_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.application_set_status not in ALLOWED_APPLICATION_SET_STATUSES:
            raise ValueError(
                f"unknown application_set_status: {self.application_set_status}"
            )
        object.__setattr__(
            self,
            "application_records",
            tuple(
                item
                if isinstance(
                    item,
                    FutureTaskWorkingMemoryReadbackHintApplicationRecord,
                )
                else FutureTaskWorkingMemoryReadbackHintApplicationRecord.from_dict(
                    dict(item)
                )
                for item in self.application_records
            ),
        )
        for name in (
            "applied_record_ids",
            "held_record_ids",
            "blocked_record_ids",
            "applied_hint_labels",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "FutureTaskWorkingMemoryReadbackHintApplicationSet":
        return cls(**dict(data))


@dataclass(frozen=True)
class FutureTaskWorkingMemoryInitializationReadbackSnapshot:
    readback_snapshot_id: str
    schema_version: str
    created_at: str
    source_engine: str
    target_task_working_memory_id: str
    target_task_initialization_id: str
    source_application_set_id: str
    source_reviewed_concept_ids: tuple[str, ...]
    readback_hints: tuple[dict[str, object], ...]
    readback_hint_ids: tuple[str, ...]
    readback_hint_labels: tuple[str, ...]
    hint_count: int
    snapshot_status: str
    snapshot_summary: str
    advisory_only: bool
    single_task_lifetime: bool
    future_task_initialization_only: bool
    candidate_ordering_changed: bool
    task_behavior_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READBACK_SNAPSHOT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_future_task_working_memory_initialization_readback_snapshot_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.snapshot_status not in ALLOWED_SNAPSHOT_STATUSES:
            raise ValueError(f"unknown snapshot_status: {self.snapshot_status}")
        object.__setattr__(
            self,
            "source_reviewed_concept_ids",
            _tuple_of_str(
                "source_reviewed_concept_ids",
                self.source_reviewed_concept_ids,
            ),
        )
        object.__setattr__(
            self,
            "readback_hints",
            tuple(dict(item) for item in self.readback_hints),
        )
        for name in ("readback_hint_ids", "readback_hint_labels", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "FutureTaskWorkingMemoryInitializationReadbackSnapshot":
        return cls(**dict(data))


@dataclass(frozen=True)
class FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str | None
    source_hint_application_preparation_set_id: str | None
    source_application_set_id: str | None
    source_readback_snapshot_id: str | None
    application_preparation_set_valid: bool
    application_preparation_safety_audit_passed: bool
    application_records_valid: bool
    readback_snapshot_valid: bool
    working_memory_mutation_allowed_only_for_new_task_initialization: bool
    no_running_task_mutation: bool
    readback_hints_advisory_only: bool
    readback_hints_single_task_lifetime: bool
    no_candidate_ordering_change: bool
    no_task_behavior_change: bool
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
        if self.schema_version != APPLICATION_SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_future_task_working_memory_readback_hint_application_safety_audit_v0"
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
    ) -> "FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit":
        return cls(**dict(data))


def build_future_task_working_memory_readback_hint_application_record(
    *,
    application_preparation_record: (
        TaskWorkingMemoryReadbackHintApplicationPreparationRecord | dict[str, object]
    ),
    application_preparation_set: (
        TaskWorkingMemoryReadbackHintApplicationPreparationSet | dict[str, object]
    ),
    application_preparation_safety_audit: (
        TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit
        | dict[str, object]
    ),
    target_task_working_memory_id: str,
    target_task_initialization_id: str,
    target_task_is_running: bool = False,
) -> FutureTaskWorkingMemoryReadbackHintApplicationRecord:
    preparation = _preparation_record(application_preparation_record)
    preparation_set = _preparation_set(application_preparation_set)
    preparation_safety = _preparation_safety_audit(application_preparation_safety_audit)
    status = _application_status(preparation, target_task_is_running)
    applied = status == "applied_to_new_task_working_memory_initialization"
    return FutureTaskWorkingMemoryReadbackHintApplicationRecord(
        future_task_readback_hint_application_id=(
            "future_task_working_memory_readback_hint_application:"
            f"{target_task_initialization_id}:"
            f"{preparation.hint_application_preparation_id}"
        ),
        schema_version=APPLICATION_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=preparation.source_reviewed_concept_id,
        source_hint_application_preparation_id=(
            preparation.hint_application_preparation_id
        ),
        source_hint_application_preparation_set_id=(
            preparation_set.hint_application_preparation_set_id
        ),
        source_application_preparation_safety_audit_id=(
            preparation_safety.safety_audit_id
        ),
        source_task_working_memory_readback_hint_id=(
            preparation.source_task_working_memory_readback_hint_id
        ),
        target_task_working_memory_id=target_task_working_memory_id,
        target_task_initialization_id=target_task_initialization_id,
        concept_label=preparation.concept_label,
        hint_label=preparation.hint_label,
        hint_kind=preparation.hint_kind,
        hint_priority=preparation.hint_priority,
        hint_summary=preparation.hint_summary,
        applied_working_memory_slot=preparation.prepared_working_memory_slot,
        application_scope=preparation.prepared_application_scope,
        visibility=preparation.prepared_visibility,
        lifetime=preparation.prepared_lifetime,
        task_handling_note=preparation.prepared_task_handling_note,
        scope_warning=preparation.prepared_scope_warning,
        counterexample_warning=preparation.prepared_counterexample_warning,
        application_status=status,
        application_summary=_application_summary(status),
        applied_to_new_task_working_memory_initialization=applied,
        applied_to_running_task=False,
        working_memory_mutated=applied,
        advisory_only=True,
        candidate_ordering_changed=False,
        task_behavior_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_changed=False,
        execution_created=False,
        memory_layer_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_combined_trace_refs(
            preparation.source_trace_refs,
            preparation_set.source_trace_refs,
            preparation_safety.source_trace_refs,
        ),
    )


def validate_future_task_working_memory_readback_hint_application_record(
    record: FutureTaskWorkingMemoryReadbackHintApplicationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        application = _application_record(record)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_application_record:{error}"]}
    errors: list[str] = []
    if application.application_status in {
        "blocked_invalid_preparation",
        "blocked_preparation_not_ready",
        "blocked_running_task_mutation_attempt",
        "blocked_forbidden_authority_detected",
    }:
        errors.append(application.application_status)
    applied = (
        application.application_status
        == "applied_to_new_task_working_memory_initialization"
    )
    if application.applied_to_new_task_working_memory_initialization is not applied:
        errors.append("applied_flag_mismatch")
    if application.working_memory_mutated is not applied:
        errors.append("working_memory_mutation_flag_mismatch")
    if application.applied_to_running_task is not False:
        errors.append("applied_to_running_task_true")
    if applied:
        if application.applied_working_memory_slot != "readback_hints":
            errors.append("applied_working_memory_slot_not_readback_hints")
        if application.application_scope != "future_task_initialization":
            errors.append("application_scope_not_future_task_initialization")
        if application.visibility != "advisory_only":
            errors.append("visibility_not_advisory_only")
        if application.lifetime != "single_task":
            errors.append("lifetime_not_single_task")
    if application.advisory_only is not True:
        errors.append("advisory_only_false")
    for flag in (
        "candidate_ordering_changed",
        "task_behavior_changed",
        "selected_action_changed",
        "final_action_changed",
        "direct_command_changed",
        "execution_created",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(application, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "future_task_readback_hint_application_id": (
            application.future_task_readback_hint_application_id
        ),
        "application_status": application.application_status,
        "source_hint_application_preparation_id": (
            application.source_hint_application_preparation_id
        ),
    }


def build_future_task_working_memory_readback_hint_application_set(
    *,
    application_preparation_set: (
        TaskWorkingMemoryReadbackHintApplicationPreparationSet | dict[str, object]
    ),
    application_preparation_safety_audit: (
        TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit
        | dict[str, object]
    ),
    target_task_working_memory_id: str,
    target_task_initialization_id: str,
    target_task_is_running: bool = False,
) -> FutureTaskWorkingMemoryReadbackHintApplicationSet:
    preparation_set = _preparation_set(application_preparation_set)
    preparation_safety = _preparation_safety_audit(application_preparation_safety_audit)
    records = tuple(
        build_future_task_working_memory_readback_hint_application_record(
            application_preparation_record=record,
            application_preparation_set=preparation_set,
            application_preparation_safety_audit=preparation_safety,
            target_task_working_memory_id=target_task_working_memory_id,
            target_task_initialization_id=target_task_initialization_id,
            target_task_is_running=target_task_is_running,
        )
        for record in preparation_set.application_preparation_records
    )
    status = _application_set_status(
        preparation_set,
        preparation_safety,
        records,
        target_task_is_running,
    )
    applied_records = tuple(
        record
        for record in records
        if record.application_status
        == "applied_to_new_task_working_memory_initialization"
    )
    held_records = tuple(
        record for record in records if record.application_status == "held_for_more_evidence"
    )
    blocked_records = tuple(
        record
        for record in records
        if record.application_status.startswith("blocked_")
    )
    return FutureTaskWorkingMemoryReadbackHintApplicationSet(
        future_task_readback_hint_application_set_id=(
            "future_task_working_memory_readback_hint_application_set:"
            f"{target_task_initialization_id}:"
            f"{preparation_set.source_reviewed_concept_id}"
        ),
        schema_version=APPLICATION_SET_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=preparation_set.source_reviewed_concept_id,
        source_hint_application_preparation_set_id=(
            preparation_set.hint_application_preparation_set_id
        ),
        source_application_preparation_safety_audit_id=(
            preparation_safety.safety_audit_id
        ),
        target_task_working_memory_id=target_task_working_memory_id,
        target_task_initialization_id=target_task_initialization_id,
        concept_label=preparation_set.concept_label,
        application_records=records,
        applied_record_ids=tuple(
            record.future_task_readback_hint_application_id
            for record in applied_records
        ),
        held_record_ids=tuple(
            record.future_task_readback_hint_application_id for record in held_records
        ),
        blocked_record_ids=tuple(
            record.future_task_readback_hint_application_id for record in blocked_records
        ),
        applied_hint_labels=tuple(record.hint_label for record in applied_records),
        applied_count=len(applied_records),
        held_count=len(held_records),
        blocked_count=len(blocked_records),
        application_set_status=status,
        application_set_summary=_application_set_summary(status),
        has_advisory_readback_hints_applied_to_new_task_initialization=(
            bool(applied_records)
            and status == "application_set_created_with_advisory_hints"
        ),
        applied_to_running_task=False,
        working_memory_mutated=(
            bool(applied_records)
            and status == "application_set_created_with_advisory_hints"
        ),
        candidate_ordering_changed=False,
        task_behavior_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_changed=False,
        execution_created=False,
        memory_layer_write_performed=False,
        source_trace_refs=_combined_trace_refs(
            preparation_set.source_trace_refs,
            preparation_safety.source_trace_refs,
            *(record.source_trace_refs for record in records),
        ),
    )


def validate_future_task_working_memory_readback_hint_application_set(
    application_set: FutureTaskWorkingMemoryReadbackHintApplicationSet
    | dict[str, object],
) -> dict[str, object]:
    try:
        record = _application_set(application_set)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_application_set:{error}"]}
    errors: list[str] = []
    if record.application_set_status.startswith("blocked_"):
        errors.append(record.application_set_status)
    validations = [
        validate_future_task_working_memory_readback_hint_application_record(item)
        for item in record.application_records
    ]
    if any(not validation["valid"] for validation in validations):
        errors.append("application_record_invalid")
    applied_records = tuple(
        item
        for item in record.application_records
        if item.application_status
        == "applied_to_new_task_working_memory_initialization"
    )
    held_records = tuple(
        item
        for item in record.application_records
        if item.application_status == "held_for_more_evidence"
    )
    blocked_records = tuple(
        item
        for item in record.application_records
        if item.application_status.startswith("blocked_")
    )
    if record.applied_count != len(applied_records):
        errors.append("applied_count_mismatch")
    if record.held_count != len(held_records):
        errors.append("held_count_mismatch")
    if record.blocked_count != len(blocked_records):
        errors.append("blocked_count_mismatch")
    expected_has = bool(applied_records)
    if (
        record.has_advisory_readback_hints_applied_to_new_task_initialization
        is not expected_has
    ):
        errors.append("has_applied_hints_flag_mismatch")
    if record.working_memory_mutated is not expected_has:
        errors.append("working_memory_mutated_flag_mismatch")
    for flag in (
        "applied_to_running_task",
        "candidate_ordering_changed",
        "task_behavior_changed",
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
        "future_task_readback_hint_application_set_id": (
            record.future_task_readback_hint_application_set_id
        ),
        "application_set_status": record.application_set_status,
        "applied_count": record.applied_count,
        "held_count": record.held_count,
        "blocked_count": record.blocked_count,
    }


def build_future_task_working_memory_initialization_readback_snapshot(
    *,
    application_set: FutureTaskWorkingMemoryReadbackHintApplicationSet
    | dict[str, object],
) -> FutureTaskWorkingMemoryInitializationReadbackSnapshot:
    app_set = _application_set(application_set)
    app_set_validation = validate_future_task_working_memory_readback_hint_application_set(
        app_set
    )
    applied_records = tuple(
        record
        for record in app_set.application_records
        if record.application_status
        == "applied_to_new_task_working_memory_initialization"
    )
    if not app_set_validation["valid"]:
        status = (
            "blocked_forbidden_authority_detected"
            if app_set.application_set_status
            == "blocked_forbidden_authority_detected"
            else "blocked_invalid_application_set"
        )
    elif applied_records:
        status = "snapshot_created_with_advisory_readback_hints"
    else:
        status = "snapshot_created_empty"
    readback_hints = tuple(_readback_hint_from_application(record) for record in applied_records)
    return FutureTaskWorkingMemoryInitializationReadbackSnapshot(
        readback_snapshot_id=(
            "future_task_working_memory_initialization_readback_snapshot:"
            f"{app_set.target_task_initialization_id}"
        ),
        schema_version=READBACK_SNAPSHOT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        target_task_working_memory_id=app_set.target_task_working_memory_id,
        target_task_initialization_id=app_set.target_task_initialization_id,
        source_application_set_id=app_set.future_task_readback_hint_application_set_id,
        source_reviewed_concept_ids=tuple(
            dict.fromkeys(
                record.source_reviewed_concept_id
                for record in app_set.application_records
            )
        )
        or (app_set.source_reviewed_concept_id,),
        readback_hints=readback_hints if status.startswith("snapshot_created") else (),
        readback_hint_ids=tuple(
            str(hint["hint_id"])
            for hint in readback_hints
            if status.startswith("snapshot_created")
        ),
        readback_hint_labels=tuple(
            str(hint["hint_label"])
            for hint in readback_hints
            if status.startswith("snapshot_created")
        ),
        hint_count=len(readback_hints) if status.startswith("snapshot_created") else 0,
        snapshot_status=status,
        snapshot_summary=_snapshot_summary(status),
        advisory_only=True,
        single_task_lifetime=True,
        future_task_initialization_only=True,
        candidate_ordering_changed=False,
        task_behavior_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_changed=False,
        execution_created=False,
        memory_layer_write_performed=False,
        source_trace_refs=app_set.source_trace_refs,
    )


def validate_future_task_working_memory_initialization_readback_snapshot(
    snapshot: FutureTaskWorkingMemoryInitializationReadbackSnapshot | dict[str, object],
) -> dict[str, object]:
    try:
        record = _readback_snapshot(snapshot)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_readback_snapshot:{error}"]}
    errors: list[str] = []
    if record.snapshot_status.startswith("blocked_"):
        errors.append(record.snapshot_status)
    if record.hint_count != len(record.readback_hints):
        errors.append("hint_count_mismatch")
    if len(record.readback_hint_ids) != record.hint_count:
        errors.append("readback_hint_ids_mismatch")
    if len(record.readback_hint_labels) != record.hint_count:
        errors.append("readback_hint_labels_mismatch")
    if (
        record.snapshot_status == "snapshot_created_with_advisory_readback_hints"
        and record.hint_count == 0
    ):
        errors.append("snapshot_created_without_hints")
    if record.snapshot_status == "snapshot_created_empty" and record.hint_count != 0:
        errors.append("empty_snapshot_has_hints")
    for flag in (
        "advisory_only",
        "single_task_lifetime",
        "future_task_initialization_only",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    for flag in (
        "candidate_ordering_changed",
        "task_behavior_changed",
        "selected_action_changed",
        "final_action_changed",
        "direct_command_changed",
        "execution_created",
        "memory_layer_write_performed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    for hint in record.readback_hints:
        if set(hint) != _READBACK_HINT_KEYS:
            errors.append("readback_hint_contains_non_inert_fields")
        if hint.get("visibility") != "advisory_only":
            errors.append("readback_hint_not_advisory_only")
        if hint.get("lifetime") != "single_task":
            errors.append("readback_hint_not_single_task")
    return {
        "valid": not errors,
        "error_codes": errors,
        "readback_snapshot_id": record.readback_snapshot_id,
        "snapshot_status": record.snapshot_status,
        "hint_count": record.hint_count,
    }


def build_future_task_working_memory_readback_hint_application_safety_audit(
    *,
    application_preparation_set: (
        TaskWorkingMemoryReadbackHintApplicationPreparationSet | dict[str, object]
    ),
    application_preparation_safety_audit: (
        TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit
        | dict[str, object]
    ),
    application_set: FutureTaskWorkingMemoryReadbackHintApplicationSet
    | dict[str, object],
    readback_snapshot: FutureTaskWorkingMemoryInitializationReadbackSnapshot
    | dict[str, object],
) -> FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit:
    preparation_set = _preparation_set(application_preparation_set)
    preparation_safety = _preparation_safety_audit(application_preparation_safety_audit)
    app_set = _application_set(application_set)
    snapshot = _readback_snapshot(readback_snapshot)
    preparation_set_valid = bool(
        validate_task_working_memory_readback_hint_application_preparation_set(
            preparation_set
        )["valid"]
    )
    preparation_safety_passed = bool(
        validate_task_working_memory_readback_hint_application_preparation_safety_audit(
            preparation_safety
        )["valid"]
    )
    application_records_valid = all(
        validate_future_task_working_memory_readback_hint_application_record(record)[
            "valid"
        ]
        for record in app_set.application_records
    )
    application_set_valid = bool(
        validate_future_task_working_memory_readback_hint_application_set(app_set)[
            "valid"
        ]
    )
    snapshot_valid = bool(
        validate_future_task_working_memory_initialization_readback_snapshot(snapshot)[
            "valid"
        ]
    )
    running_task_attempt = (
        app_set.application_set_status == "blocked_running_task_mutation_attempt"
        or any(
            record.application_status == "blocked_running_task_mutation_attempt"
            or record.applied_to_running_task
            for record in app_set.application_records
        )
    )
    non_advisory = (
        any(
            (
                record.application_status
                == "applied_to_new_task_working_memory_initialization"
                and record.visibility != "advisory_only"
            )
            or record.advisory_only is not True
            for record in app_set.application_records
        )
        or any(
            hint.get("visibility") != "advisory_only"
            for hint in snapshot.readback_hints
        )
        or snapshot.advisory_only is not True
    )
    persistent_lifetime = (
        any(
            record.application_status
            == "applied_to_new_task_working_memory_initialization"
            and record.lifetime != "single_task"
            for record in app_set.application_records
        )
        or any(hint.get("lifetime") != "single_task" for hint in snapshot.readback_hints)
        or snapshot.single_task_lifetime is not True
    )
    mutation_allowed = (
        not running_task_attempt
        and all(
            not record.working_memory_mutated
            or (
                record.application_status
                == "applied_to_new_task_working_memory_initialization"
                and record.applied_working_memory_slot == "readback_hints"
                and record.application_scope == "future_task_initialization"
                and record.visibility == "advisory_only"
                and record.lifetime == "single_task"
            )
            for record in app_set.application_records
        )
        and (
            not app_set.working_memory_mutated
            or app_set.application_set_status
            == "application_set_created_with_advisory_hints"
        )
    )
    no_ordering = (
        app_set.candidate_ordering_changed is False
        and snapshot.candidate_ordering_changed is False
        and all(
            record.candidate_ordering_changed is False
            for record in app_set.application_records
        )
    )
    no_behavior = (
        app_set.task_behavior_changed is False
        and snapshot.task_behavior_changed is False
        and all(
            record.task_behavior_changed is False for record in app_set.application_records
        )
    )
    no_selected = (
        app_set.selected_action_changed is False
        and snapshot.selected_action_changed is False
        and all(
            record.selected_action_changed is False
            for record in app_set.application_records
        )
    )
    no_final = (
        app_set.final_action_changed is False
        and snapshot.final_action_changed is False
        and all(
            record.final_action_changed is False for record in app_set.application_records
        )
    )
    no_direct = (
        app_set.direct_command_changed is False
        and snapshot.direct_command_changed is False
        and all(
            record.direct_command_changed is False for record in app_set.application_records
        )
    )
    no_execution = (
        app_set.execution_created is False
        and snapshot.execution_created is False
        and all(record.execution_created is False for record in app_set.application_records)
    )
    no_memory_write = (
        app_set.memory_layer_write_performed is False
        and snapshot.memory_layer_write_performed is False
        and all(
            record.memory_layer_write_performed is False
            for record in app_set.application_records
        )
    )
    no_automatic_learning = all(
        record.automatic_learning_approval_created is False
        for record in app_set.application_records
    )
    blocked_reasons = _safety_blocked_reasons(
        preparation_set_valid=preparation_set_valid,
        preparation_safety_passed=preparation_safety_passed,
        application_set_valid=application_set_valid,
        application_records_valid=application_records_valid,
        snapshot_valid=snapshot_valid,
        mutation_allowed=mutation_allowed,
        running_task_attempt=running_task_attempt,
        non_advisory=non_advisory,
        persistent_lifetime=persistent_lifetime,
        no_ordering=no_ordering,
        no_behavior=no_behavior,
        no_selected=no_selected,
        no_final=no_final,
        no_direct=no_direct,
        no_execution=no_execution,
        no_memory_write=no_memory_write,
        no_automatic_learning=no_automatic_learning,
    )
    return FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit(
        safety_audit_id=(
            "future_task_working_memory_readback_hint_application_safety_audit:"
            f"{app_set.target_task_initialization_id}"
        ),
        schema_version=APPLICATION_SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=app_set.source_reviewed_concept_id,
        source_hint_application_preparation_set_id=(
            preparation_set.hint_application_preparation_set_id
        ),
        source_application_set_id=app_set.future_task_readback_hint_application_set_id,
        source_readback_snapshot_id=snapshot.readback_snapshot_id,
        application_preparation_set_valid=preparation_set_valid,
        application_preparation_safety_audit_passed=preparation_safety_passed,
        application_records_valid=application_records_valid,
        readback_snapshot_valid=snapshot_valid,
        working_memory_mutation_allowed_only_for_new_task_initialization=(
            mutation_allowed
        ),
        no_running_task_mutation=not running_task_attempt,
        readback_hints_advisory_only=not non_advisory,
        readback_hints_single_task_lifetime=not persistent_lifetime,
        no_candidate_ordering_change=no_ordering,
        no_task_behavior_change=no_behavior,
        no_selected_action_change=no_selected,
        no_final_action_change=no_final,
        no_direct_command_change=no_direct,
        no_action_execution=no_execution,
        no_memory_layer_write=no_memory_write,
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_automatic_learning_approval=no_automatic_learning,
        audit_status=_audit_status(blocked_reasons),
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=blocked_reasons,
        source_trace_refs=_combined_trace_refs(
            preparation_set.source_trace_refs,
            preparation_safety.source_trace_refs,
            app_set.source_trace_refs,
            snapshot.source_trace_refs,
        ),
    )


def validate_future_task_working_memory_readback_hint_application_safety_audit(
    audit: FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit
    | dict[str, object],
) -> dict[str, object]:
    try:
        record = _application_safety_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed":
        errors.append(record.audit_status)
    for flag in (
        "application_preparation_set_valid",
        "application_preparation_safety_audit_passed",
        "application_records_valid",
        "readback_snapshot_valid",
        "working_memory_mutation_allowed_only_for_new_task_initialization",
        "no_running_task_mutation",
        "readback_hints_advisory_only",
        "readback_hints_single_task_lifetime",
        "no_candidate_ordering_change",
        "no_task_behavior_change",
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


def initialize_future_task_working_memory_with_advisory_readback_hints(
    *,
    application_set: FutureTaskWorkingMemoryReadbackHintApplicationSet
    | dict[str, object],
    readback_snapshot: FutureTaskWorkingMemoryInitializationReadbackSnapshot
    | dict[str, object]
    | None = None,
    target_task_is_running: bool = False,
    current_goal: str = "future task initialized with advisory readback hints",
) -> dict[str, object]:
    app_set = _application_set(application_set)
    if target_task_is_running:
        return {
            "future_task_working_memory_created": False,
            "initialization_status": "blocked_running_task_mutation_attempt",
            "running_task_mutation_rejected": True,
            "target_task_working_memory_id": app_set.target_task_working_memory_id,
            "target_task_initialization_id": app_set.target_task_initialization_id,
            "readback_hints": [],
            "readback_hint_application_records": [],
            "working_memory_mutated": False,
            "candidate_ordering_changed": False,
            "task_behavior_changed": False,
            "selected_action_changed": False,
            "final_action_changed": False,
            "direct_command_changed": False,
            "execution_created": False,
            "memory_layer_write_performed": False,
        }
    snapshot = (
        _readback_snapshot(readback_snapshot)
        if readback_snapshot is not None
        else build_future_task_working_memory_initialization_readback_snapshot(
            application_set=app_set
        )
    )
    snapshot_validation = (
        validate_future_task_working_memory_initialization_readback_snapshot(snapshot)
    )
    if not snapshot_validation["valid"]:
        return {
            "future_task_working_memory_created": False,
            "initialization_status": "blocked_invalid_readback_snapshot",
            "target_task_working_memory_id": app_set.target_task_working_memory_id,
            "target_task_initialization_id": app_set.target_task_initialization_id,
            "readback_hints": [],
            "readback_hint_application_records": [],
            "working_memory_mutated": False,
            "candidate_ordering_changed": False,
            "task_behavior_changed": False,
            "selected_action_changed": False,
            "final_action_changed": False,
            "direct_command_changed": False,
            "execution_created": False,
            "memory_layer_write_performed": False,
        }
    applied_records = tuple(
        record
        for record in app_set.application_records
        if record.application_status
        == "applied_to_new_task_working_memory_initialization"
    )
    return {
        "future_task_working_memory_created": True,
        "initialization_status": "future_task_working_memory_initialized",
        "task_working_memory": {
            "task_working_memory_id": app_set.target_task_working_memory_id,
            "task_initialization_id": app_set.target_task_initialization_id,
            "memory_layer": "working",
            "task_status": "initialized",
            "current_goal": current_goal,
            "readback_hints": _plain(snapshot.readback_hints),
            "readback_hint_application_records": [
                record.to_dict() for record in applied_records
            ],
            "working_memory_mutation_scope": "readback_hints_only",
            "candidate_ordering": [],
            "selected_action": None,
            "final_action": None,
            "direct_command": None,
            "execution": None,
            "advisory_only": True,
            "single_task_lifetime": True,
            "future_task_initialization_only": True,
            "candidate_ordering_changed": False,
            "task_behavior_changed": False,
            "selected_action_changed": False,
            "final_action_changed": False,
            "direct_command_changed": False,
            "execution_created": False,
            "memory_layer_write_performed": False,
        },
        "target_task_working_memory_id": app_set.target_task_working_memory_id,
        "target_task_initialization_id": app_set.target_task_initialization_id,
        "readback_hints": _plain(snapshot.readback_hints),
        "readback_hint_application_records": [
            record.future_task_readback_hint_application_id
            for record in applied_records
        ],
        "working_memory_mutated": bool(snapshot.readback_hints),
        "candidate_ordering_changed": False,
        "task_behavior_changed": False,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "memory_layer_write_performed": False,
    }


def build_future_task_working_memory_readback_hint_application_bundle(
    preparation_payload: dict[str, object],
    *,
    target_task_working_memory_id: str = "task_working_memory:future_demo",
    target_task_initialization_id: str = "task_initialization:future_demo",
    target_task_is_running: bool = False,
) -> dict[str, object]:
    preparation_set = _preparation_set(
        preparation_payload["hint_application_preparation_set"]
    )
    preparation_safety = _preparation_safety_audit(
        preparation_payload["hint_application_preparation_safety_audit"]
    )
    application_set = build_future_task_working_memory_readback_hint_application_set(
        application_preparation_set=preparation_set,
        application_preparation_safety_audit=preparation_safety,
        target_task_working_memory_id=target_task_working_memory_id,
        target_task_initialization_id=target_task_initialization_id,
        target_task_is_running=target_task_is_running,
    )
    snapshot = build_future_task_working_memory_initialization_readback_snapshot(
        application_set=application_set
    )
    safety = build_future_task_working_memory_readback_hint_application_safety_audit(
        application_preparation_set=preparation_set,
        application_preparation_safety_audit=preparation_safety,
        application_set=application_set,
        readback_snapshot=snapshot,
    )
    initialized = initialize_future_task_working_memory_with_advisory_readback_hints(
        application_set=application_set,
        readback_snapshot=snapshot,
        target_task_is_running=target_task_is_running,
    )
    return {
        "future_task_readback_hint_application_records": [
            record.to_dict() for record in application_set.application_records
        ],
        "future_task_readback_hint_application_set": application_set.to_dict(),
        "future_task_working_memory_initialization_readback_snapshot": (
            snapshot.to_dict()
        ),
        "future_task_working_memory_readback_hint_application_safety_audit": (
            safety.to_dict()
        ),
        "initialized_future_task_working_memory": initialized,
        "future_task_readback_hint_application_set_validation": (
            validate_future_task_working_memory_readback_hint_application_set(
                application_set
            )
        ),
        "future_task_working_memory_initialization_readback_snapshot_validation": (
            validate_future_task_working_memory_initialization_readback_snapshot(
                snapshot
            )
        ),
        "future_task_working_memory_readback_hint_application_safety_audit_validation": (
            validate_future_task_working_memory_readback_hint_application_safety_audit(
                safety
            )
        ),
        "safe_claim": SAFE_CLAIM,
    }


def build_demo_future_task_working_memory_readback_hint_application_set() -> (
    dict[str, object]
):
    return build_future_task_working_memory_readback_hint_application_bundle(
        build_demo_task_working_memory_readback_hint_application_preparation_set()
    )


def build_demo_future_task_working_memory_initialization_readback_snapshot() -> (
    FutureTaskWorkingMemoryInitializationReadbackSnapshot
):
    payload = build_demo_future_task_working_memory_readback_hint_application_set()
    return FutureTaskWorkingMemoryInitializationReadbackSnapshot.from_dict(
        payload["future_task_working_memory_initialization_readback_snapshot"]
    )


def build_demo_future_task_working_memory_readback_hint_application_safety_audit() -> (
    FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit
):
    payload = build_demo_future_task_working_memory_readback_hint_application_set()
    return FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit.from_dict(
        payload["future_task_working_memory_readback_hint_application_safety_audit"]
    )


def build_demo_all_held_future_task_working_memory_readback_hint_application_set() -> (
    dict[str, object]
):
    return build_future_task_working_memory_readback_hint_application_bundle(
        build_demo_all_held_task_working_memory_readback_hint_application_preparation_set()
    )


def build_demo_blocked_running_task_mutation_application_set() -> dict[str, object]:
    return build_future_task_working_memory_readback_hint_application_bundle(
        build_demo_task_working_memory_readback_hint_application_preparation_set(),
        target_task_is_running=True,
    )


def build_demo_blocked_non_advisory_hint_application_set() -> dict[str, object]:
    payload = build_demo_future_task_working_memory_readback_hint_application_set()
    app_set = FutureTaskWorkingMemoryReadbackHintApplicationSet.from_dict(
        payload["future_task_readback_hint_application_set"]
    )
    records = list(app_set.application_records)
    first = records[0].to_dict()
    first["visibility"] = "warning_only"
    first["advisory_only"] = False
    records[0] = FutureTaskWorkingMemoryReadbackHintApplicationRecord.from_dict(first)
    app_set = FutureTaskWorkingMemoryReadbackHintApplicationSet.from_dict(
        {
            **app_set.to_dict(),
            "application_records": [record.to_dict() for record in records],
            "application_set_status": "blocked_invalid_application_records",
            "working_memory_mutated": False,
        }
    )
    preparation_payload = (
        build_demo_task_working_memory_readback_hint_application_preparation_set()
    )
    preparation_set = _preparation_set(
        preparation_payload["hint_application_preparation_set"]
    )
    preparation_safety = _preparation_safety_audit(
        preparation_payload["hint_application_preparation_safety_audit"]
    )
    snapshot = build_future_task_working_memory_initialization_readback_snapshot(
        application_set=app_set
    )
    safety = build_future_task_working_memory_readback_hint_application_safety_audit(
        application_preparation_set=preparation_set,
        application_preparation_safety_audit=preparation_safety,
        application_set=app_set,
        readback_snapshot=snapshot,
    )
    return _application_payload(app_set, snapshot, safety)


def build_demo_blocked_forbidden_authority_application_set() -> dict[str, object]:
    payload = build_demo_future_task_working_memory_readback_hint_application_set()
    app_set = FutureTaskWorkingMemoryReadbackHintApplicationSet.from_dict(
        payload["future_task_readback_hint_application_set"]
    )
    records = list(app_set.application_records)
    first = records[0].to_dict()
    first["candidate_ordering_changed"] = True
    records[0] = FutureTaskWorkingMemoryReadbackHintApplicationRecord.from_dict(first)
    app_set = FutureTaskWorkingMemoryReadbackHintApplicationSet.from_dict(
        {
            **app_set.to_dict(),
            "application_records": [record.to_dict() for record in records],
            "application_set_status": "blocked_forbidden_authority_detected",
            "candidate_ordering_changed": True,
            "working_memory_mutated": False,
        }
    )
    preparation_payload = (
        build_demo_task_working_memory_readback_hint_application_preparation_set()
    )
    preparation_set = _preparation_set(
        preparation_payload["hint_application_preparation_set"]
    )
    preparation_safety = _preparation_safety_audit(
        preparation_payload["hint_application_preparation_safety_audit"]
    )
    snapshot = build_future_task_working_memory_initialization_readback_snapshot(
        application_set=app_set
    )
    safety = build_future_task_working_memory_readback_hint_application_safety_audit(
        application_preparation_set=preparation_set,
        application_preparation_safety_audit=preparation_safety,
        application_set=app_set,
        readback_snapshot=snapshot,
    )
    return _application_payload(app_set, snapshot, safety)


def build_demo_blocked_future_task_working_memory_readback_hint_application_set(
    case: str,
) -> dict[str, object]:
    builders = {
        "running-task-mutation": build_demo_blocked_running_task_mutation_application_set,
        "non-advisory-hint": build_demo_blocked_non_advisory_hint_application_set,
        "forbidden-authority": build_demo_blocked_forbidden_authority_application_set,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked readback hint application case: {case}") from error


def _application_payload(
    app_set: FutureTaskWorkingMemoryReadbackHintApplicationSet,
    snapshot: FutureTaskWorkingMemoryInitializationReadbackSnapshot,
    safety: FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit,
) -> dict[str, object]:
    initialized = initialize_future_task_working_memory_with_advisory_readback_hints(
        application_set=app_set,
        readback_snapshot=snapshot,
    )
    return {
        "future_task_readback_hint_application_records": [
            record.to_dict() for record in app_set.application_records
        ],
        "future_task_readback_hint_application_set": app_set.to_dict(),
        "future_task_working_memory_initialization_readback_snapshot": (
            snapshot.to_dict()
        ),
        "future_task_working_memory_readback_hint_application_safety_audit": (
            safety.to_dict()
        ),
        "initialized_future_task_working_memory": initialized,
        "future_task_readback_hint_application_set_validation": (
            validate_future_task_working_memory_readback_hint_application_set(app_set)
        ),
        "future_task_working_memory_initialization_readback_snapshot_validation": (
            validate_future_task_working_memory_initialization_readback_snapshot(
                snapshot
            )
        ),
        "future_task_working_memory_readback_hint_application_safety_audit_validation": (
            validate_future_task_working_memory_readback_hint_application_safety_audit(
                safety
            )
        ),
        "safe_claim": SAFE_CLAIM,
    }


def _application_status(
    preparation: TaskWorkingMemoryReadbackHintApplicationPreparationRecord,
    target_task_is_running: bool,
) -> str:
    if target_task_is_running:
        return "blocked_running_task_mutation_attempt"
    if any(
        (
            preparation.applied_to_working_memory,
            preparation.working_memory_mutated,
            preparation.task_behavior_changed,
            preparation.candidate_ordering_changed,
            preparation.selected_action_changed,
            preparation.final_action_changed,
            preparation.direct_command_changed,
            preparation.execution_created,
            preparation.memory_layer_write_performed,
            preparation.automatic_learning_approval_created,
        )
    ):
        return "blocked_forbidden_authority_detected"
    if not validate_task_working_memory_readback_hint_application_preparation_record(
        preparation
    )["valid"]:
        return "blocked_invalid_preparation"
    if (
        preparation.preparation_status
        == "prepared_for_future_working_memory_initialization_application"
    ):
        return "applied_to_new_task_working_memory_initialization"
    if preparation.preparation_status == "held_for_more_evidence":
        return "held_for_more_evidence"
    if preparation.preparation_status.startswith("blocked_"):
        return "blocked_invalid_preparation"
    return "blocked_preparation_not_ready"


def _application_summary(status: str) -> str:
    if status == "applied_to_new_task_working_memory_initialization":
        return "Advisory readback hint applied to new Task Working Memory initialization."
    if status == "held_for_more_evidence":
        return "Readback hint application held for more evidence."
    if status == "blocked_running_task_mutation_attempt":
        return "Readback hint application blocked because target task was already running."
    return f"Readback hint application not performed: {status}."


def _application_set_status(
    preparation_set: TaskWorkingMemoryReadbackHintApplicationPreparationSet,
    preparation_safety: TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit,
    records: tuple[FutureTaskWorkingMemoryReadbackHintApplicationRecord, ...],
    target_task_is_running: bool,
) -> str:
    if target_task_is_running:
        return "blocked_running_task_mutation_attempt"
    if not validate_task_working_memory_readback_hint_application_preparation_set(
        preparation_set
    )["valid"]:
        return "blocked_invalid_preparation_set"
    if not validate_task_working_memory_readback_hint_application_preparation_safety_audit(
        preparation_safety
    )["valid"]:
        return "blocked_invalid_preparation_set"
    if any(
        record.application_status == "blocked_forbidden_authority_detected"
        for record in records
    ):
        return "blocked_forbidden_authority_detected"
    if any(
        not validate_future_task_working_memory_readback_hint_application_record(
            record
        )["valid"]
        for record in records
    ):
        return "blocked_invalid_application_records"
    if any(
        record.application_status
        == "applied_to_new_task_working_memory_initialization"
        for record in records
    ):
        return "application_set_created_with_advisory_hints"
    return "application_set_created_all_held_or_blocked"


def _application_set_summary(status: str) -> str:
    if status == "application_set_created_with_advisory_hints":
        return "Application set placed advisory readback hints into new task initialization."
    if status == "application_set_created_all_held_or_blocked":
        return "Application set contains only held or blocked readback hints."
    return f"Future task readback hint application set blocked: {status}."


def _snapshot_summary(status: str) -> str:
    if status == "snapshot_created_with_advisory_readback_hints":
        return "Readback snapshot contains advisory-only, single-task hints."
    if status == "snapshot_created_empty":
        return "Readback snapshot created without advisory hints."
    return f"Readback snapshot blocked: {status}."


def _readback_hint_from_application(
    record: FutureTaskWorkingMemoryReadbackHintApplicationRecord,
) -> dict[str, object]:
    return {
        "hint_id": record.source_task_working_memory_readback_hint_id,
        "concept_label": record.concept_label,
        "hint_label": record.hint_label,
        "hint_kind": record.hint_kind,
        "hint_priority": record.hint_priority,
        "hint_summary": record.hint_summary,
        "task_handling_note": record.task_handling_note,
        "scope_warning": record.scope_warning,
        "counterexample_warning": record.counterexample_warning,
        "visibility": "advisory_only",
        "lifetime": "single_task",
        "source_trace_refs": list(record.source_trace_refs),
    }


_READBACK_HINT_KEYS = {
    "hint_id",
    "concept_label",
    "hint_label",
    "hint_kind",
    "hint_priority",
    "hint_summary",
    "task_handling_note",
    "scope_warning",
    "counterexample_warning",
    "visibility",
    "lifetime",
    "source_trace_refs",
}


def _safety_blocked_reasons(
    *,
    preparation_set_valid: bool,
    preparation_safety_passed: bool,
    application_set_valid: bool,
    application_records_valid: bool,
    snapshot_valid: bool,
    mutation_allowed: bool,
    running_task_attempt: bool,
    non_advisory: bool,
    persistent_lifetime: bool,
    no_ordering: bool,
    no_behavior: bool,
    no_selected: bool,
    no_final: bool,
    no_direct: bool,
    no_execution: bool,
    no_memory_write: bool,
    no_automatic_learning: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if running_task_attempt:
        reasons.append("blocked_running_task_mutation_detected")
    if non_advisory:
        reasons.append("blocked_non_advisory_hint_detected")
    if persistent_lifetime:
        reasons.append("blocked_persistent_hint_lifetime_detected")
    if not no_ordering:
        reasons.append("blocked_forbidden_ordering_change_detected")
    if not no_behavior:
        reasons.append("blocked_forbidden_behavior_change_detected")
    if not (no_selected and no_final and no_direct and no_execution):
        reasons.append("blocked_forbidden_action_authority_detected")
    if not (no_memory_write and no_automatic_learning):
        reasons.append("blocked_forbidden_memory_write_detected")
    if not preparation_set_valid:
        reasons.append("blocked_invalid_application_preparation_set")
    if not preparation_safety_passed:
        reasons.append("blocked_application_preparation_safety_audit_failed")
    if not application_set_valid or not application_records_valid:
        reasons.append("blocked_invalid_application_set")
    if not snapshot_valid:
        reasons.append("blocked_invalid_readback_snapshot")
    return tuple(dict.fromkeys(reasons))


def _audit_status(blocked_reasons: tuple[str, ...]) -> str:
    if not blocked_reasons:
        return "passed"
    for status in (
        "blocked_running_task_mutation_detected",
        "blocked_non_advisory_hint_detected",
        "blocked_persistent_hint_lifetime_detected",
        "blocked_forbidden_ordering_change_detected",
        "blocked_forbidden_behavior_change_detected",
        "blocked_forbidden_action_authority_detected",
        "blocked_forbidden_memory_write_detected",
        "blocked_invalid_application_preparation_set",
        "blocked_application_preparation_safety_audit_failed",
        "blocked_invalid_application_set",
        "blocked_invalid_readback_snapshot",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_invalid_application_set"


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


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


def _application_record(
    record: FutureTaskWorkingMemoryReadbackHintApplicationRecord | dict[str, object],
) -> FutureTaskWorkingMemoryReadbackHintApplicationRecord:
    return (
        record
        if isinstance(record, FutureTaskWorkingMemoryReadbackHintApplicationRecord)
        else FutureTaskWorkingMemoryReadbackHintApplicationRecord.from_dict(dict(record))
    )


def _application_set(
    record: FutureTaskWorkingMemoryReadbackHintApplicationSet | dict[str, object],
) -> FutureTaskWorkingMemoryReadbackHintApplicationSet:
    return (
        record
        if isinstance(record, FutureTaskWorkingMemoryReadbackHintApplicationSet)
        else FutureTaskWorkingMemoryReadbackHintApplicationSet.from_dict(dict(record))
    )


def _readback_snapshot(
    record: FutureTaskWorkingMemoryInitializationReadbackSnapshot | dict[str, object],
) -> FutureTaskWorkingMemoryInitializationReadbackSnapshot:
    return (
        record
        if isinstance(record, FutureTaskWorkingMemoryInitializationReadbackSnapshot)
        else FutureTaskWorkingMemoryInitializationReadbackSnapshot.from_dict(
            dict(record)
        )
    )


def _application_safety_audit(
    record: FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit
    | dict[str, object],
) -> FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit:
    return (
        record
        if isinstance(record, FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit)
        else FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit.from_dict(
            dict(record)
        )
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
