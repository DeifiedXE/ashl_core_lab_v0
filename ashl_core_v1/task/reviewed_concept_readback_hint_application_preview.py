"""Application previews for inactive TaskWorkingMemoryReadbackHint records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.task.reviewed_concept_readback_hint_record import (
    TaskWorkingMemoryReadbackHint,
    TaskWorkingMemoryReadbackHintRecordSafetyAudit,
    TaskWorkingMemoryReadbackHintRecordSet,
    build_demo_all_held_task_working_memory_readback_hint_record_set,
    build_demo_blocked_forbidden_authority_hint_record_set,
    build_demo_blocked_invalid_preparation_hint_record_set,
    build_demo_task_working_memory_readback_hint_record_set,
    validate_task_working_memory_readback_hint,
    validate_task_working_memory_readback_hint_record_safety_audit,
    validate_task_working_memory_readback_hint_record_set,
)


SOURCE_ENGINE = "task_engine"
TASK_WORKING_MEMORY_READBACK_HINT_APPLICATION_PREVIEW_SCHEMA_VERSION = (
    "task_engine_reviewed_concept_readback_hint_application_preview_v0"
)
TASK_WORKING_MEMORY_READBACK_HINT_APPLICATION_PREVIEW_SET_SCHEMA_VERSION = (
    "task_engine_reviewed_concept_readback_hint_application_preview_set_v0"
)
TASK_WORKING_MEMORY_READBACK_HINT_APPLICATION_PREVIEW_SAFETY_AUDIT_SCHEMA_VERSION = (
    "task_engine_reviewed_concept_readback_hint_application_preview_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Task Engine can preview how inactive "
    "TaskWorkingMemoryReadbackHint records would be applied to future Task "
    "Working Memory initialization, without applying those hints, mutating "
    "Working Memory, changing task behavior, changing candidate ordering, "
    "selecting actions, executing actions, or writing memory layers."
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

ALLOWED_WORKING_MEMORY_SLOTS = {
    "readback_hints",
    "task_handling_notes",
    "scope_warnings",
    "counterexample_warnings",
    "blocked",
}
ALLOWED_APPLICATION_SCOPES = {
    "current_task_only",
    "future_task_initialization",
    "blocked",
}
ALLOWED_VISIBILITIES = {"advisory_only", "warning_only", "blocked"}
ALLOWED_LIFETIMES = {"single_task", "until_task_closure", "blocked"}
ALLOWED_PREVIEW_STATUSES = {
    "application_preview_ready",
    "held_for_more_evidence",
    "blocked_invalid_hint_record",
    "blocked_hint_not_inactive",
    "blocked_forbidden_authority_detected",
}
ALLOWED_PREVIEW_SET_STATUSES = {
    "preview_set_created_with_ready_previews",
    "preview_set_created_all_held_or_blocked",
    "blocked_invalid_hint_record_set",
    "blocked_invalid_application_previews",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_hint_record_set",
    "blocked_hint_record_safety_audit_failed",
    "blocked_invalid_application_preview_set",
    "blocked_invalid_application_previews",
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
class TaskWorkingMemoryReadbackHintApplicationPreview:
    hint_application_preview_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_task_working_memory_readback_hint_id: str
    source_task_working_memory_readback_hint_record_set_id: str
    source_hint_record_safety_audit_id: str
    concept_label: str
    hint_label: str
    hint_kind: str
    hint_priority: int
    hint_summary: str
    task_handling_note: str
    scope_warning: str | None
    counterexample_warning: str | None
    proposed_working_memory_slot: str
    proposed_application_scope: str
    proposed_visibility: str
    proposed_lifetime: str
    preview_status: str
    preview_summary: str
    ready_for_teacher_application_review: bool
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
        if (
            self.schema_version
            != TASK_WORKING_MEMORY_READBACK_HINT_APPLICATION_PREVIEW_SCHEMA_VERSION
        ):
            raise ValueError(
                "schema_version must be task_engine_reviewed_concept_readback_hint_application_preview_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.proposed_working_memory_slot not in ALLOWED_WORKING_MEMORY_SLOTS:
            raise ValueError(
                f"unknown proposed_working_memory_slot: {self.proposed_working_memory_slot}"
            )
        if self.proposed_application_scope not in ALLOWED_APPLICATION_SCOPES:
            raise ValueError(
                f"unknown proposed_application_scope: {self.proposed_application_scope}"
            )
        if self.proposed_visibility not in ALLOWED_VISIBILITIES:
            raise ValueError(f"unknown proposed_visibility: {self.proposed_visibility}")
        if self.proposed_lifetime not in ALLOWED_LIFETIMES:
            raise ValueError(f"unknown proposed_lifetime: {self.proposed_lifetime}")
        if self.preview_status not in ALLOWED_PREVIEW_STATUSES:
            raise ValueError(f"unknown preview_status: {self.preview_status}")
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
    ) -> "TaskWorkingMemoryReadbackHintApplicationPreview":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskWorkingMemoryReadbackHintApplicationPreviewSet:
    hint_application_preview_set_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_task_working_memory_readback_hint_record_set_id: str
    source_hint_record_safety_audit_id: str
    concept_label: str
    application_previews: tuple[TaskWorkingMemoryReadbackHintApplicationPreview, ...]
    ready_preview_ids: tuple[str, ...]
    held_preview_ids: tuple[str, ...]
    blocked_preview_ids: tuple[str, ...]
    ready_hint_labels: tuple[str, ...]
    ready_count: int
    held_count: int
    blocked_count: int
    preview_set_status: str
    preview_set_summary: str
    has_ready_previews_for_teacher_application_review: bool
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
        if (
            self.schema_version
            != TASK_WORKING_MEMORY_READBACK_HINT_APPLICATION_PREVIEW_SET_SCHEMA_VERSION
        ):
            raise ValueError(
                "schema_version must be task_engine_reviewed_concept_readback_hint_application_preview_set_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.preview_set_status not in ALLOWED_PREVIEW_SET_STATUSES:
            raise ValueError(f"unknown preview_set_status: {self.preview_set_status}")
        object.__setattr__(
            self,
            "application_previews",
            tuple(
                item
                if isinstance(item, TaskWorkingMemoryReadbackHintApplicationPreview)
                else TaskWorkingMemoryReadbackHintApplicationPreview.from_dict(dict(item))
                for item in self.application_previews
            ),
        )
        for name in (
            "ready_preview_ids",
            "held_preview_ids",
            "blocked_preview_ids",
            "ready_hint_labels",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "TaskWorkingMemoryReadbackHintApplicationPreviewSet":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_task_working_memory_readback_hint_record_set_id: str | None
    source_hint_application_preview_set_id: str | None
    hint_record_set_valid: bool
    hint_record_safety_audit_passed: bool
    application_previews_valid: bool
    application_preview_scope_valid: bool
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
        if (
            self.schema_version
            != TASK_WORKING_MEMORY_READBACK_HINT_APPLICATION_PREVIEW_SAFETY_AUDIT_SCHEMA_VERSION
        ):
            raise ValueError(
                "schema_version must be task_engine_reviewed_concept_readback_hint_application_preview_safety_audit_v0"
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
    ) -> "TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit":
        return cls(**dict(data))


def build_task_working_memory_readback_hint_application_preview(
    *,
    task_working_memory_readback_hint: TaskWorkingMemoryReadbackHint | dict[str, object],
    task_working_memory_readback_hint_record_set: (
        TaskWorkingMemoryReadbackHintRecordSet | dict[str, object]
    ),
    hint_record_safety_audit: (
        TaskWorkingMemoryReadbackHintRecordSafetyAudit | dict[str, object]
    ),
) -> TaskWorkingMemoryReadbackHintApplicationPreview:
    hint = _hint_record(task_working_memory_readback_hint)
    record_set = _hint_record_set(task_working_memory_readback_hint_record_set)
    safety = _hint_record_safety_audit(hint_record_safety_audit)
    status = _preview_status(hint)
    (
        proposed_working_memory_slot,
        proposed_application_scope,
        proposed_visibility,
        proposed_lifetime,
    ) = _preview_proposals(status)
    return TaskWorkingMemoryReadbackHintApplicationPreview(
        hint_application_preview_id=(
            "task_working_memory_readback_hint_application_preview:"
            f"{hint.task_working_memory_readback_hint_id}"
        ),
        schema_version=TASK_WORKING_MEMORY_READBACK_HINT_APPLICATION_PREVIEW_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=hint.source_reviewed_concept_id,
        source_task_working_memory_readback_hint_id=(
            hint.task_working_memory_readback_hint_id
        ),
        source_task_working_memory_readback_hint_record_set_id=(
            record_set.task_working_memory_readback_hint_record_set_id
        ),
        source_hint_record_safety_audit_id=safety.safety_audit_id,
        concept_label=hint.concept_label,
        hint_label=hint.hint_label,
        hint_kind=hint.hint_kind,
        hint_priority=hint.hint_priority,
        hint_summary=hint.hint_summary,
        task_handling_note=hint.task_handling_note,
        scope_warning=hint.scope_warning,
        counterexample_warning=hint.counterexample_warning,
        proposed_working_memory_slot=proposed_working_memory_slot,
        proposed_application_scope=proposed_application_scope,
        proposed_visibility=proposed_visibility,
        proposed_lifetime=proposed_lifetime,
        preview_status=status,
        preview_summary=_preview_summary(status),
        ready_for_teacher_application_review=status == "application_preview_ready",
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
            hint.source_trace_refs,
            record_set.source_trace_refs,
            safety.source_trace_refs,
        ),
    )


def validate_task_working_memory_readback_hint_application_preview(
    preview: TaskWorkingMemoryReadbackHintApplicationPreview | dict[str, object],
) -> dict[str, object]:
    try:
        record = _application_preview(preview)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_application_preview:{error}"]}
    errors: list[str] = []
    if record.preview_status == "blocked_forbidden_authority_detected":
        errors.append(record.preview_status)
    expected_ready = record.preview_status == "application_preview_ready"
    if record.ready_for_teacher_application_review is not expected_ready:
        errors.append("ready_for_teacher_application_review_flag_mismatch")
    expected_proposals = _preview_proposals(record.preview_status)
    actual_proposals = (
        record.proposed_working_memory_slot,
        record.proposed_application_scope,
        record.proposed_visibility,
        record.proposed_lifetime,
    )
    if actual_proposals != expected_proposals:
        errors.append("proposal_fields_mismatch")
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
        "hint_application_preview_id": record.hint_application_preview_id,
        "preview_status": record.preview_status,
    }


def build_task_working_memory_readback_hint_application_preview_set(
    *,
    task_working_memory_readback_hint_record_set: (
        TaskWorkingMemoryReadbackHintRecordSet | dict[str, object]
    ),
    hint_record_safety_audit: (
        TaskWorkingMemoryReadbackHintRecordSafetyAudit | dict[str, object]
    ),
) -> TaskWorkingMemoryReadbackHintApplicationPreviewSet:
    record_set = _hint_record_set(task_working_memory_readback_hint_record_set)
    safety = _hint_record_safety_audit(hint_record_safety_audit)
    previews = tuple(
        build_task_working_memory_readback_hint_application_preview(
            task_working_memory_readback_hint=hint,
            task_working_memory_readback_hint_record_set=record_set,
            hint_record_safety_audit=safety,
        )
        for hint in record_set.hint_records
    )
    status = _preview_set_status(record_set, safety, previews)
    ready_previews = tuple(
        preview
        for preview in previews
        if preview.preview_status == "application_preview_ready"
    )
    held_previews = tuple(
        preview
        for preview in previews
        if preview.preview_status == "held_for_more_evidence"
    )
    blocked_previews = tuple(
        preview for preview in previews if preview.preview_status.startswith("blocked_")
    )
    return TaskWorkingMemoryReadbackHintApplicationPreviewSet(
        hint_application_preview_set_id=(
            "task_working_memory_readback_hint_application_preview_set:"
            f"{record_set.source_reviewed_concept_id}"
        ),
        schema_version=(
            TASK_WORKING_MEMORY_READBACK_HINT_APPLICATION_PREVIEW_SET_SCHEMA_VERSION
        ),
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=record_set.source_reviewed_concept_id,
        source_task_working_memory_readback_hint_record_set_id=(
            record_set.task_working_memory_readback_hint_record_set_id
        ),
        source_hint_record_safety_audit_id=safety.safety_audit_id,
        concept_label=record_set.concept_label,
        application_previews=previews,
        ready_preview_ids=tuple(
            preview.hint_application_preview_id for preview in ready_previews
        ),
        held_preview_ids=tuple(
            preview.hint_application_preview_id for preview in held_previews
        ),
        blocked_preview_ids=tuple(
            preview.hint_application_preview_id for preview in blocked_previews
        ),
        ready_hint_labels=tuple(preview.hint_label for preview in ready_previews),
        ready_count=len(ready_previews),
        held_count=len(held_previews),
        blocked_count=len(blocked_previews),
        preview_set_status=status,
        preview_set_summary=_preview_set_summary(status),
        has_ready_previews_for_teacher_application_review=bool(ready_previews)
        and status == "preview_set_created_with_ready_previews",
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
            record_set.source_trace_refs,
            safety.source_trace_refs,
            *(preview.source_trace_refs for preview in previews),
        ),
    )


def validate_task_working_memory_readback_hint_application_preview_set(
    preview_set: TaskWorkingMemoryReadbackHintApplicationPreviewSet | dict[str, object],
) -> dict[str, object]:
    try:
        record = _application_preview_set(preview_set)
    except (TypeError, ValueError, KeyError) as error:
        return {
            "valid": False,
            "error_codes": [f"invalid_application_preview_set:{error}"],
        }
    errors: list[str] = []
    if record.preview_set_status.startswith("blocked_"):
        errors.append(record.preview_set_status)
    preview_validations = [
        validate_task_working_memory_readback_hint_application_preview(item)
        for item in record.application_previews
    ]
    if any(not validation["valid"] for validation in preview_validations):
        errors.append("application_preview_invalid")
    ready_previews = tuple(
        item
        for item in record.application_previews
        if item.preview_status == "application_preview_ready"
    )
    held_previews = tuple(
        item
        for item in record.application_previews
        if item.preview_status == "held_for_more_evidence"
    )
    blocked_previews = tuple(
        item for item in record.application_previews if item.preview_status.startswith("blocked_")
    )
    if record.ready_count != len(ready_previews):
        errors.append("ready_count_mismatch")
    if record.held_count != len(held_previews):
        errors.append("held_count_mismatch")
    if record.blocked_count != len(blocked_previews):
        errors.append("blocked_count_mismatch")
    if record.has_ready_previews_for_teacher_application_review != bool(
        record.ready_preview_ids
    ):
        errors.append("has_ready_previews_flag_mismatch")
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
        "hint_application_preview_set_id": record.hint_application_preview_set_id,
        "preview_set_status": record.preview_set_status,
        "ready_count": record.ready_count,
        "held_count": record.held_count,
        "blocked_count": record.blocked_count,
    }


def build_task_working_memory_readback_hint_application_preview_safety_audit(
    *,
    task_working_memory_readback_hint_record_set: (
        TaskWorkingMemoryReadbackHintRecordSet | dict[str, object]
    ),
    hint_record_safety_audit: (
        TaskWorkingMemoryReadbackHintRecordSafetyAudit | dict[str, object]
    ),
    application_preview_set: (
        TaskWorkingMemoryReadbackHintApplicationPreviewSet | dict[str, object]
    ),
) -> TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit:
    record_set = _hint_record_set(task_working_memory_readback_hint_record_set)
    hint_record_safety = _hint_record_safety_audit(hint_record_safety_audit)
    preview_set = _application_preview_set(application_preview_set)
    hint_record_set_valid = bool(
        validate_task_working_memory_readback_hint_record_set(record_set)["valid"]
    )
    hint_record_safety_audit_passed = bool(
        validate_task_working_memory_readback_hint_record_safety_audit(
            hint_record_safety
        )["valid"]
    )
    application_previews_valid = all(
        validate_task_working_memory_readback_hint_application_preview(preview)[
            "valid"
        ]
        for preview in preview_set.application_previews
    )
    application_preview_set_valid = bool(
        validate_task_working_memory_readback_hint_application_preview_set(
            preview_set
        )["valid"]
    )
    application_preview_scope_valid = _application_preview_scope_valid(
        record_set,
        preview_set,
    )
    no_active_hint_application = (
        preview_set.applied_to_working_memory is False
        and all(
            preview.applied_to_working_memory is False
            for preview in preview_set.application_previews
        )
    )
    no_working_memory_mutation = (
        preview_set.working_memory_mutated is False
        and all(
            preview.working_memory_mutated is False
            for preview in preview_set.application_previews
        )
    )
    no_task_behavior_change = (
        preview_set.task_behavior_changed is False
        and all(
            preview.task_behavior_changed is False
            for preview in preview_set.application_previews
        )
    )
    no_candidate_ordering_change = (
        preview_set.candidate_ordering_changed is False
        and all(
            preview.candidate_ordering_changed is False
            for preview in preview_set.application_previews
        )
    )
    no_selected_action_change = (
        preview_set.selected_action_changed is False
        and all(
            preview.selected_action_changed is False
            for preview in preview_set.application_previews
        )
    )
    no_final_action_change = (
        preview_set.final_action_changed is False
        and all(
            preview.final_action_changed is False
            for preview in preview_set.application_previews
        )
    )
    no_direct_command_change = (
        preview_set.direct_command_changed is False
        and all(
            preview.direct_command_changed is False
            for preview in preview_set.application_previews
        )
    )
    no_action_execution = (
        preview_set.execution_created is False
        and all(
            preview.execution_created is False
            for preview in preview_set.application_previews
        )
    )
    no_memory_layer_write = (
        preview_set.memory_layer_write_performed is False
        and all(
            preview.memory_layer_write_performed is False
            for preview in preview_set.application_previews
        )
    )
    no_automatic_learning_approval = all(
        preview.automatic_learning_approval_created is False
        for preview in preview_set.application_previews
    )
    blocked_reasons = _safety_blocked_reasons(
        hint_record_set_valid=hint_record_set_valid,
        hint_record_safety_audit_passed=hint_record_safety_audit_passed,
        application_preview_set_valid=application_preview_set_valid,
        application_previews_valid=application_previews_valid,
        application_preview_scope_valid=application_preview_scope_valid,
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
    return TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit(
        safety_audit_id=(
            "task_working_memory_readback_hint_application_preview_safety_audit:"
            f"{preview_set.source_reviewed_concept_id}"
        ),
        schema_version=(
            TASK_WORKING_MEMORY_READBACK_HINT_APPLICATION_PREVIEW_SAFETY_AUDIT_SCHEMA_VERSION
        ),
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=preview_set.source_reviewed_concept_id,
        source_task_working_memory_readback_hint_record_set_id=(
            record_set.task_working_memory_readback_hint_record_set_id
        ),
        source_hint_application_preview_set_id=(
            preview_set.hint_application_preview_set_id
        ),
        hint_record_set_valid=hint_record_set_valid,
        hint_record_safety_audit_passed=hint_record_safety_audit_passed,
        application_previews_valid=application_previews_valid,
        application_preview_scope_valid=application_preview_scope_valid,
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
            record_set.source_trace_refs,
            hint_record_safety.source_trace_refs,
            preview_set.source_trace_refs,
        ),
    )


def validate_task_working_memory_readback_hint_application_preview_safety_audit(
    audit: TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _safety_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed":
        errors.append(record.audit_status)
    for flag in (
        "hint_record_set_valid",
        "hint_record_safety_audit_passed",
        "application_previews_valid",
        "application_preview_scope_valid",
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


def build_task_working_memory_readback_hint_application_preview_bundle(
    hint_record_payload: dict[str, object],
) -> dict[str, object]:
    record_set = _hint_record_set(
        hint_record_payload["task_working_memory_readback_hint_record_set"]
    )
    hint_record_safety = _hint_record_safety_audit(
        hint_record_payload["task_working_memory_readback_hint_record_safety_audit"]
    )
    preview_set = build_task_working_memory_readback_hint_application_preview_set(
        task_working_memory_readback_hint_record_set=record_set,
        hint_record_safety_audit=hint_record_safety,
    )
    safety = build_task_working_memory_readback_hint_application_preview_safety_audit(
        task_working_memory_readback_hint_record_set=record_set,
        hint_record_safety_audit=hint_record_safety,
        application_preview_set=preview_set,
    )
    return {
        "task_working_memory_readback_hint_application_previews": [
            preview.to_dict() for preview in preview_set.application_previews
        ],
        "task_working_memory_readback_hint_application_preview_set": (
            preview_set.to_dict()
        ),
        "task_working_memory_readback_hint_application_preview_safety_audit": (
            safety.to_dict()
        ),
        "task_working_memory_readback_hint_application_preview_set_validation": (
            validate_task_working_memory_readback_hint_application_preview_set(
                preview_set
            )
        ),
        "task_working_memory_readback_hint_application_preview_safety_audit_validation": (
            validate_task_working_memory_readback_hint_application_preview_safety_audit(
                safety
            )
        ),
        "safe_claim": SAFE_CLAIM,
    }


def build_demo_task_working_memory_readback_hint_application_preview_set() -> (
    dict[str, object]
):
    return build_task_working_memory_readback_hint_application_preview_bundle(
        build_demo_task_working_memory_readback_hint_record_set()
    )


def build_demo_task_working_memory_readback_hint_application_preview_safety_audit() -> (
    TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit
):
    payload = build_demo_task_working_memory_readback_hint_application_preview_set()
    return TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit.from_dict(
        payload["task_working_memory_readback_hint_application_preview_safety_audit"]
    )


def build_demo_all_held_task_working_memory_readback_hint_application_preview_set() -> (
    dict[str, object]
):
    return build_task_working_memory_readback_hint_application_preview_bundle(
        build_demo_all_held_task_working_memory_readback_hint_record_set()
    )


def build_demo_blocked_invalid_hint_record_application_preview_set() -> dict[str, object]:
    return build_task_working_memory_readback_hint_application_preview_bundle(
        build_demo_blocked_invalid_preparation_hint_record_set()
    )


def build_demo_blocked_forbidden_authority_application_preview_set() -> dict[str, object]:
    return build_task_working_memory_readback_hint_application_preview_bundle(
        build_demo_blocked_forbidden_authority_hint_record_set()
    )


def build_demo_blocked_task_working_memory_readback_hint_application_preview_set(
    case: str,
) -> dict[str, object]:
    cases = {
        "invalid-hint-record": build_demo_blocked_invalid_hint_record_application_preview_set,
        "forbidden-authority": build_demo_blocked_forbidden_authority_application_preview_set,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked application preview case: {case}") from error


def _preview_status(hint: TaskWorkingMemoryReadbackHint) -> str:
    if any(
        (
            hint.applied_to_working_memory,
            hint.working_memory_mutated,
            hint.task_behavior_changed,
            hint.candidate_ordering_changed,
            hint.selected_action_changed,
            hint.final_action_changed,
            hint.direct_command_changed,
            hint.execution_created,
            hint.memory_layer_write_performed,
            hint.automatic_learning_approval_created,
        )
    ):
        return "blocked_forbidden_authority_detected"
    if not validate_task_working_memory_readback_hint(hint)["valid"]:
        if hint.hint_record_status == "blocked_forbidden_authority_detected":
            return "blocked_forbidden_authority_detected"
        return "blocked_invalid_hint_record"
    if hint.hint_record_status == "hint_record_created_inactive":
        return "application_preview_ready"
    if hint.hint_record_status == "held_for_more_evidence":
        return "held_for_more_evidence"
    if hint.hint_record_status.startswith("blocked_"):
        return "blocked_invalid_hint_record"
    return "blocked_hint_not_inactive"


def _preview_proposals(status: str) -> tuple[str, str, str, str]:
    if status == "application_preview_ready":
        return (
            "readback_hints",
            "future_task_initialization",
            "advisory_only",
            "single_task",
        )
    return ("blocked", "blocked", "blocked", "blocked")


def _preview_summary(status: str) -> str:
    if status == "application_preview_ready":
        return (
            "Inactive hint has a future Task Working Memory initialization "
            "placement preview."
        )
    if status == "held_for_more_evidence":
        return "Hint application preview held because the hint record needs more evidence."
    return f"Hint application preview blocked or not ready: {status}."


def _preview_set_status(
    record_set: TaskWorkingMemoryReadbackHintRecordSet,
    safety: TaskWorkingMemoryReadbackHintRecordSafetyAudit,
    previews: tuple[TaskWorkingMemoryReadbackHintApplicationPreview, ...],
) -> str:
    record_set_valid = validate_task_working_memory_readback_hint_record_set(record_set)[
        "valid"
    ]
    safety_valid = validate_task_working_memory_readback_hint_record_safety_audit(
        safety
    )["valid"]
    if any(
        preview.preview_status == "blocked_forbidden_authority_detected"
        for preview in previews
    ) or safety.audit_status in {
        "blocked_forbidden_working_memory_mutation_detected",
        "blocked_forbidden_behavior_change_detected",
        "blocked_forbidden_action_authority_detected",
        "blocked_forbidden_memory_write_detected",
    }:
        return "blocked_forbidden_authority_detected"
    if (
        not record_set_valid
        or (
            not safety_valid
            and safety.audit_status
            not in {
                "blocked_forbidden_working_memory_mutation_detected",
                "blocked_forbidden_behavior_change_detected",
                "blocked_forbidden_action_authority_detected",
                "blocked_forbidden_memory_write_detected",
            }
        )
    ):
        return "blocked_invalid_hint_record_set"
    if any(
        not validate_task_working_memory_readback_hint_application_preview(preview)[
            "valid"
        ]
        for preview in previews
    ):
        return "blocked_invalid_application_previews"
    if any(preview.preview_status == "application_preview_ready" for preview in previews):
        return "preview_set_created_with_ready_previews"
    return "preview_set_created_all_held_or_blocked"


def _preview_set_summary(status: str) -> str:
    if status == "preview_set_created_with_ready_previews":
        return "Preview set includes inactive hints ready for teacher application review."
    if status == "preview_set_created_all_held_or_blocked":
        return "Preview set contains only held or blocked application previews."
    return f"Application preview set blocked: {status}."


def _application_preview_scope_valid(
    record_set: TaskWorkingMemoryReadbackHintRecordSet,
    preview_set: TaskWorkingMemoryReadbackHintApplicationPreviewSet,
) -> bool:
    inactive_hint_ids = {
        hint.task_working_memory_readback_hint_id
        for hint in record_set.hint_records
        if hint.hint_record_status == "hint_record_created_inactive"
    }
    ready_source_hint_ids = {
        preview.source_task_working_memory_readback_hint_id
        for preview in preview_set.application_previews
        if preview.preview_status == "application_preview_ready"
    }
    return inactive_hint_ids == ready_source_hint_ids


def _safety_blocked_reasons(
    *,
    hint_record_set_valid: bool,
    hint_record_safety_audit_passed: bool,
    application_preview_set_valid: bool,
    application_previews_valid: bool,
    application_preview_scope_valid: bool,
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
    if not hint_record_set_valid:
        reasons.append("blocked_invalid_hint_record_set")
    if not hint_record_safety_audit_passed:
        reasons.append("blocked_hint_record_safety_audit_failed")
    if not application_preview_set_valid:
        reasons.append("blocked_invalid_application_preview_set")
    if not application_previews_valid:
        reasons.append("blocked_invalid_application_previews")
    if not application_preview_scope_valid:
        reasons.append("blocked_invalid_application_previews")
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
        "blocked_invalid_hint_record_set",
        "blocked_hint_record_safety_audit_failed",
        "blocked_invalid_application_preview_set",
        "blocked_invalid_application_previews",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_invalid_application_previews"


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


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


def _application_preview(
    record: TaskWorkingMemoryReadbackHintApplicationPreview | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationPreview:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationPreview)
        else TaskWorkingMemoryReadbackHintApplicationPreview.from_dict(dict(record))
    )


def _application_preview_set(
    record: TaskWorkingMemoryReadbackHintApplicationPreviewSet | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationPreviewSet:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationPreviewSet)
        else TaskWorkingMemoryReadbackHintApplicationPreviewSet.from_dict(dict(record))
    )


def _safety_audit(
    record: TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit
    | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit)
        else TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit.from_dict(
            dict(record)
        )
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
