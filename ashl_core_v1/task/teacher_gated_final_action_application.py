"""Teacher-gated final_action application records from selected_action."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.task.teacher_gated_selected_action_application import (
    SelectedActionApplicationAudit,
    SelectedActionApplicationRecord,
    build_demo_blocked_teacher_gated_selected_action_application,
    build_demo_selected_action_application,
    validate_selected_action_application_audit,
    validate_selected_action_application_record,
)


SOURCE_ENGINE = "task_engine"
FINAL_ACTION_GATE_SCHEMA_VERSION = (
    "task_engine_teacher_gated_final_action_application_gate_v0"
)
FINAL_ACTION_RECORD_SCHEMA_VERSION = "task_engine_final_action_application_record_v0"
FINAL_ACTION_ROLLBACK_SCHEMA_VERSION = "task_engine_final_action_rollback_v0"
FINAL_ACTION_AUDIT_SCHEMA_VERSION = "task_engine_final_action_application_audit_v0"

SAFE_CLAIM = (
    "ASHL Core v1 Task Engine can apply a teacher-gated final_action from an "
    "actual selected_action, with rollback and audit, while preserving "
    "direct_command, execution, task behavior, selected_action, candidate "
    "ordering, and memory-layer boundaries unchanged."
)
BLOCKED_CLAIMS = (
    "no_direct_command",
    "no_action_execution",
    "no_task_behavior_execution",
    "no_selected_action_change_by_this_package",
    "no_candidate_ordering_change_by_this_package",
    "no_core_longterm_archive_anchor_write",
    "no_automatic_learning_approval",
)

APPROVED_GATE_STATUS = "approved_for_actual_final_action"
FINAL_ACTION_APPLIED_STATUS = "final_action_applied"

ALLOWED_GATE_STATUSES = {
    "approved_for_actual_final_action",
    "held_for_more_evidence",
    "rejected",
    "conflict_detected",
    "blocked_invalid_selected_action",
    "blocked_invalid_selected_action_audit",
    "blocked_empty_selected_action",
    "blocked_forbidden_authority_detected",
}
ALLOWED_APPLICATION_STATUSES = {
    "final_action_applied",
    "held_for_more_evidence",
    "rejected_by_teacher_gate",
    "blocked_conflict_detected",
    "blocked_invalid_teacher_gate",
    "blocked_invalid_selected_action",
    "blocked_running_task_mutation_attempt",
    "blocked_forbidden_authority_detected",
    "rollback_applied",
}
ALLOWED_ROLLBACK_STATUSES = {
    "rollback_record_created",
    "rollback_applied_to_restore_previous_final_action",
    "blocked_invalid_final_action_application",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_final_action_applied",
    "passed_no_final_action_applied",
    "failed_missing_rollback",
    "blocked_invalid_selected_action",
    "blocked_invalid_teacher_gate",
    "blocked_running_task_mutation_detected",
    "blocked_direct_command_detected",
    "blocked_execution_detected",
    "blocked_task_behavior_change_detected",
    "blocked_memory_write_detected",
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
class TeacherGatedFinalActionApplicationGate:
    final_action_application_gate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str
    source_selected_action_application_id: str
    source_selected_action_application_audit_id: str
    selected_action_candidate_id: str | None
    candidate_ordering: tuple[str, ...]
    final_action_request_summary: str
    final_action_basis: str
    teacher_gate_status: str
    teacher_gate_reason: str
    teacher_gate_text: str
    approval_actor: str
    approval_actor_role: str
    approval_source: str
    approved_for_actual_final_action: bool
    approved_for_direct_command: bool
    approved_for_execution: bool
    approved_for_task_behavior_change: bool
    approved_for_memory_layer_write: bool
    requires_final_action_rollback_record: bool
    requires_post_application_audit: bool
    requires_teacher_gate_before_direct_command: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != FINAL_ACTION_GATE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_teacher_gated_final_action_application_gate_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.teacher_gate_status not in ALLOWED_GATE_STATUSES:
            raise ValueError(f"unknown teacher_gate_status: {self.teacher_gate_status}")
        for name in ("candidate_ordering", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TeacherGatedFinalActionApplicationGate":
        return cls(**dict(data))


@dataclass(frozen=True)
class FinalActionApplicationRecord:
    final_action_application_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str
    source_final_action_application_gate_id: str
    source_selected_action_application_id: str
    source_selected_action_application_audit_id: str
    selected_action_candidate_id: str | None
    applied_final_action_candidate_id: str | None
    previous_final_action_candidate_id: str | None
    final_action_application_status: str
    final_action_application_summary: str
    final_action_application_reason: str
    actual_final_action_changed: bool
    direct_command_created: bool
    execution_created: bool
    task_behavior_changed: bool
    selected_action_changed_by_this_package: bool
    candidate_ordering_changed_by_this_package: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    applied_to_bounded_task_path: bool
    applied_to_running_task: bool
    available_for_future_direct_command_review: bool
    requires_teacher_gate_before_direct_command: bool
    rollback_available: bool
    rollback_record_id: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != FINAL_ACTION_RECORD_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_final_action_application_record_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.final_action_application_status not in ALLOWED_APPLICATION_STATUSES:
            raise ValueError(
                "unknown final_action_application_status: "
                f"{self.final_action_application_status}"
            )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FinalActionApplicationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FinalActionRollbackRecord:
    final_action_rollback_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_final_action_application_id: str
    source_task_working_memory_id: str
    final_action_before_application: str | None
    final_action_after_application: str | None
    final_action_after_rollback: str | None
    rollback_available: bool
    rollback_applied: bool
    rollback_reason: str
    rollback_status: str
    rollback_summary: str
    direct_command_created: bool
    execution_created: bool
    task_behavior_changed: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != FINAL_ACTION_ROLLBACK_SCHEMA_VERSION:
            raise ValueError("schema_version must be task_engine_final_action_rollback_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.rollback_status not in ALLOWED_ROLLBACK_STATUSES:
            raise ValueError(f"unknown rollback_status: {self.rollback_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FinalActionRollbackRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FinalActionApplicationAudit:
    final_action_application_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_final_action_application_gate_id: str | None
    source_final_action_application_id: str | None
    source_final_action_rollback_id: str | None
    source_selected_action_application_id: str | None
    source_selected_action_application_audit_id: str | None
    selected_action_valid: bool
    selected_action_application_audit_passed: bool
    teacher_gate_valid: bool
    final_action_application_valid: bool
    rollback_available: bool
    actual_final_action_changed: bool
    direct_command_created: bool
    execution_created: bool
    task_behavior_changed: bool
    selected_action_changed_by_this_package: bool
    candidate_ordering_changed_by_this_package: bool
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
        if self.schema_version != FINAL_ACTION_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_final_action_application_audit_v0"
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
    def from_dict(cls, data: dict[str, object]) -> "FinalActionApplicationAudit":
        return cls(**dict(data))


def build_teacher_gated_final_action_application_gate(
    *,
    selected_action_application: SelectedActionApplicationRecord | dict[str, object],
    selected_action_application_audit: SelectedActionApplicationAudit | dict[str, object],
    teacher_gate_status: str = APPROVED_GATE_STATUS,
    teacher_gate_reason: str = "teacher approved actual final_action application",
    teacher_gate_text: str = "Demo teacher gate approves actual final_action only.",
    approval_actor: str = "system_demo",
    approval_actor_role: str = "system_demo",
    approval_source: str = "demo_review",
    approved_for_direct_command: bool = False,
    approved_for_execution: bool = False,
    approved_for_task_behavior_change: bool = False,
    approved_for_memory_layer_write: bool = False,
) -> TeacherGatedFinalActionApplicationGate:
    selected_action = _selected_action_record(selected_action_application)
    selected_action_audit = _selected_action_audit(selected_action_application_audit)
    selected_action_candidate_id = selected_action.applied_selected_action_candidate_id
    forbidden_authority = any(
        (
            approved_for_direct_command,
            approved_for_execution,
            approved_for_task_behavior_change,
            approved_for_memory_layer_write,
        )
    )
    selected_action_valid = _selected_action_valid(selected_action)
    audit_passed = (
        selected_action_audit.audit_status == "passed_selected_action_applied"
    )
    if not selected_action_candidate_id:
        status = "blocked_empty_selected_action"
    elif not selected_action_valid:
        status = "blocked_invalid_selected_action"
    elif not audit_passed:
        status = "blocked_invalid_selected_action_audit"
    elif forbidden_authority or not _approval_source_valid(
        approval_source,
        approval_actor_role,
        teacher_gate_text,
    ):
        status = "blocked_forbidden_authority_detected"
    else:
        status = teacher_gate_status
    return TeacherGatedFinalActionApplicationGate(
        final_action_application_gate_id=(
            "teacher_gated_final_action_application_gate:"
            f"{selected_action.source_task_initialization_id}"
        ),
        schema_version=FINAL_ACTION_GATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=selected_action.source_task_working_memory_id,
        source_task_initialization_id=selected_action.source_task_initialization_id,
        source_selected_action_application_id=(
            selected_action.selected_action_application_id
        ),
        source_selected_action_application_audit_id=(
            selected_action_audit.selected_action_application_audit_id
        ),
        selected_action_candidate_id=selected_action_candidate_id,
        candidate_ordering=selected_action.candidate_ordering,
        final_action_request_summary=(
            "Apply the teacher-gated selected_action as actual final_action."
        ),
        final_action_basis="teacher_gated_selected_action_application",
        teacher_gate_status=status,
        teacher_gate_reason=teacher_gate_reason,
        teacher_gate_text=teacher_gate_text,
        approval_actor=approval_actor,
        approval_actor_role=approval_actor_role,
        approval_source=approval_source,
        approved_for_actual_final_action=status == APPROVED_GATE_STATUS,
        approved_for_direct_command=False,
        approved_for_execution=False,
        approved_for_task_behavior_change=False,
        approved_for_memory_layer_write=False,
        requires_final_action_rollback_record=True,
        requires_post_application_audit=True,
        requires_teacher_gate_before_direct_command=True,
        source_trace_refs=_combined_trace_refs(
            selected_action.source_trace_refs,
            selected_action_audit.source_trace_refs,
        ),
    )


def validate_teacher_gated_final_action_application_gate(
    final_action_gate: TeacherGatedFinalActionApplicationGate | dict[str, object],
) -> dict[str, object]:
    try:
        gate = _final_action_gate(final_action_gate)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_final_action_gate:{error}"]}
    errors: list[str] = []
    if gate.approved_for_actual_final_action is not (
        gate.teacher_gate_status == APPROVED_GATE_STATUS
    ):
        errors.append("actual_final_action_approval_mismatch")
    if gate.approval_source == "explicit_teacher_review":
        if gate.approval_actor_role not in {"teacher", "project_owner"}:
            errors.append("invalid_explicit_actor_role")
        if not gate.teacher_gate_text.strip():
            errors.append("teacher_gate_text_required")
    if gate.approval_source == "demo_review" and gate.approval_actor_role != "system_demo":
        errors.append("demo_review_requires_system_demo_role")
    for flag in (
        "approved_for_direct_command",
        "approved_for_execution",
        "approved_for_task_behavior_change",
        "approved_for_memory_layer_write",
    ):
        if getattr(gate, flag) is not False:
            errors.append(f"{flag}_true")
    for flag in (
        "requires_final_action_rollback_record",
        "requires_post_application_audit",
        "requires_teacher_gate_before_direct_command",
    ):
        if getattr(gate, flag) is not True:
            errors.append(f"{flag}_false")
    if gate.teacher_gate_status.startswith("blocked_"):
        errors.append(gate.teacher_gate_status)
    return {
        "valid": not errors,
        "error_codes": errors,
        "final_action_application_gate_id": gate.final_action_application_gate_id,
        "teacher_gate_status": gate.teacher_gate_status,
    }


def apply_teacher_gated_final_action(
    *,
    final_action_gate: TeacherGatedFinalActionApplicationGate | dict[str, object] | None,
    previous_final_action_candidate_id: str | None = None,
    applied_to_running_task: bool = False,
    final_action_candidate_override: str | None = None,
    direct_command_created: bool = False,
    execution_created: bool = False,
    task_behavior_changed: bool = False,
    memory_layer_write_performed: bool = False,
    rollback_record_id: str | None = None,
) -> FinalActionApplicationRecord:
    gate = _final_action_gate(final_action_gate) if final_action_gate is not None else _missing_gate()
    forbidden_authority = any(
        (
            direct_command_created,
            execution_created,
            task_behavior_changed,
            memory_layer_write_performed,
        )
    )
    requested_candidate = (
        final_action_candidate_override
        if final_action_candidate_override is not None
        else gate.selected_action_candidate_id
    )
    mismatch = (
        gate.teacher_gate_status == APPROVED_GATE_STATUS
        and requested_candidate != gate.selected_action_candidate_id
    )
    if applied_to_running_task:
        status = "blocked_running_task_mutation_attempt"
    elif forbidden_authority or mismatch:
        status = "blocked_forbidden_authority_detected"
    elif gate.teacher_gate_status == APPROVED_GATE_STATUS:
        status = FINAL_ACTION_APPLIED_STATUS
    elif gate.teacher_gate_status == "held_for_more_evidence":
        status = "held_for_more_evidence"
    elif gate.teacher_gate_status == "rejected":
        status = "rejected_by_teacher_gate"
    elif gate.teacher_gate_status == "conflict_detected":
        status = "blocked_conflict_detected"
    elif gate.teacher_gate_status in {
        "blocked_empty_selected_action",
        "blocked_invalid_selected_action",
        "blocked_invalid_selected_action_audit",
    }:
        status = "blocked_invalid_selected_action"
    else:
        status = "blocked_invalid_teacher_gate"
    applied = status == FINAL_ACTION_APPLIED_STATUS
    return FinalActionApplicationRecord(
        final_action_application_id=(
            "final_action_application:"
            f"{gate.source_task_initialization_id}"
        ),
        schema_version=FINAL_ACTION_RECORD_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=gate.source_task_working_memory_id,
        source_task_initialization_id=gate.source_task_initialization_id,
        source_final_action_application_gate_id=gate.final_action_application_gate_id,
        source_selected_action_application_id=gate.source_selected_action_application_id,
        source_selected_action_application_audit_id=(
            gate.source_selected_action_application_audit_id
        ),
        selected_action_candidate_id=gate.selected_action_candidate_id,
        applied_final_action_candidate_id=requested_candidate if applied else None,
        previous_final_action_candidate_id=previous_final_action_candidate_id,
        final_action_application_status=status,
        final_action_application_summary=_application_summary(status),
        final_action_application_reason=_application_reason(status, requested_candidate),
        actual_final_action_changed=applied,
        direct_command_created=direct_command_created,
        execution_created=execution_created,
        task_behavior_changed=task_behavior_changed,
        selected_action_changed_by_this_package=False,
        candidate_ordering_changed_by_this_package=False,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=False,
        applied_to_bounded_task_path=applied,
        applied_to_running_task=applied_to_running_task,
        available_for_future_direct_command_review=applied,
        requires_teacher_gate_before_direct_command=True,
        rollback_available=applied,
        rollback_record_id=rollback_record_id,
        source_trace_refs=gate.source_trace_refs,
    )


def validate_final_action_application_record(
    final_action_application: FinalActionApplicationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        application = _final_action_application(final_action_application)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_final_action_record:{error}"]}
    errors: list[str] = []
    applied = application.final_action_application_status == FINAL_ACTION_APPLIED_STATUS
    if application.actual_final_action_changed is not applied:
        errors.append("actual_final_action_changed_mismatch")
    if applied:
        if not application.applied_final_action_candidate_id:
            errors.append("applied_final_action_missing")
        if application.applied_final_action_candidate_id != application.selected_action_candidate_id:
            errors.append("final_action_candidate_mismatch")
        if not application.available_for_future_direct_command_review:
            errors.append("available_for_future_direct_command_review_false")
    for flag in (
        "direct_command_created",
        "execution_created",
        "task_behavior_changed",
        "selected_action_changed_by_this_package",
        "candidate_ordering_changed_by_this_package",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
        "applied_to_running_task",
    ):
        if getattr(application, flag) is not False:
            errors.append(f"{flag}_true")
    if application.requires_teacher_gate_before_direct_command is not True:
        errors.append("requires_teacher_gate_before_direct_command_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "final_action_application_id": application.final_action_application_id,
        "final_action_application_status": application.final_action_application_status,
    }


def build_final_action_rollback_record(
    *,
    final_action_application: FinalActionApplicationRecord | dict[str, object],
    rollback_applied: bool = False,
    rollback_reason: str = "rollback data available to restore previous final_action",
) -> FinalActionRollbackRecord:
    application = _final_action_application(final_action_application)
    valid_application = (
        application.final_action_application_status == FINAL_ACTION_APPLIED_STATUS
    )
    rollback_status = (
        "rollback_applied_to_restore_previous_final_action"
        if rollback_applied and valid_application
        else "rollback_record_created"
        if valid_application
        else "blocked_invalid_final_action_application"
    )
    return FinalActionRollbackRecord(
        final_action_rollback_id=(
            "final_action_rollback:"
            f"{application.final_action_application_id}"
        ),
        schema_version=FINAL_ACTION_ROLLBACK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_final_action_application_id=application.final_action_application_id,
        source_task_working_memory_id=application.source_task_working_memory_id,
        final_action_before_application=application.previous_final_action_candidate_id,
        final_action_after_application=application.applied_final_action_candidate_id,
        final_action_after_rollback=(
            application.previous_final_action_candidate_id
            if rollback_applied and valid_application
            else application.applied_final_action_candidate_id
        ),
        rollback_available=valid_application,
        rollback_applied=rollback_applied and valid_application,
        rollback_reason=rollback_reason,
        rollback_status=rollback_status,
        rollback_summary=_rollback_summary(rollback_status),
        direct_command_created=False,
        execution_created=False,
        task_behavior_changed=False,
        memory_layer_write_performed=False,
        source_trace_refs=application.source_trace_refs,
    )


def apply_final_action_rollback(
    rollback_record: FinalActionRollbackRecord | dict[str, object],
) -> dict[str, object]:
    rollback = _final_action_rollback(rollback_record)
    return {
        "rollback_status": "rollback_applied_to_restore_previous_final_action"
        if rollback.rollback_available
        else "blocked_invalid_final_action_application",
        "final_action_after_rollback": (
            rollback.final_action_before_application if rollback.rollback_available else None
        ),
        "direct_command_created": False,
        "execution_created": False,
        "task_behavior_changed": False,
        "memory_layer_write_performed": False,
    }


def build_final_action_application_audit(
    *,
    selected_action_application: SelectedActionApplicationRecord | dict[str, object] | None,
    selected_action_application_audit: SelectedActionApplicationAudit | dict[str, object] | None,
    final_action_gate: TeacherGatedFinalActionApplicationGate | dict[str, object] | None,
    final_action_application: FinalActionApplicationRecord | dict[str, object] | None,
    rollback_record: FinalActionRollbackRecord | dict[str, object] | None,
) -> FinalActionApplicationAudit:
    selected_action = _selected_action_record(selected_action_application) if selected_action_application is not None else None
    selected_action_audit = _selected_action_audit(selected_action_application_audit) if selected_action_application_audit is not None else None
    gate = _final_action_gate(final_action_gate) if final_action_gate is not None else None
    application = _final_action_application(final_action_application) if final_action_application is not None else None
    rollback = _final_action_rollback(rollback_record) if rollback_record is not None else None
    selected_action_valid = selected_action is not None and _selected_action_valid(selected_action)
    selected_action_audit_passed = (
        selected_action_audit is not None
        and selected_action_audit.audit_status == "passed_selected_action_applied"
    )
    gate_valid = (
        gate is not None
        and validate_teacher_gated_final_action_application_gate(gate)["valid"]
    )
    application_valid = (
        application is not None
        and validate_final_action_application_record(application)["valid"]
    )
    rollback_available = rollback is not None and rollback.rollback_available
    blocked_reasons = _audit_blocked_reasons(
        selected_action_valid=selected_action_valid,
        selected_action_audit_passed=selected_action_audit_passed,
        gate_valid=gate_valid,
        application=application,
        rollback_available=rollback_available,
    )
    actual_final_action_changed = (
        application.actual_final_action_changed if application is not None else False
    )
    return FinalActionApplicationAudit(
        final_action_application_audit_id=(
            "final_action_application_audit:"
            f"{(application.source_task_working_memory_id if application else 'unknown')}"
        ),
        schema_version=FINAL_ACTION_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=(
            application.source_task_working_memory_id if application else "unknown"
        ),
        source_final_action_application_gate_id=(
            gate.final_action_application_gate_id if gate is not None else None
        ),
        source_final_action_application_id=(
            application.final_action_application_id if application is not None else None
        ),
        source_final_action_rollback_id=(
            rollback.final_action_rollback_id if rollback is not None else None
        ),
        source_selected_action_application_id=(
            selected_action.selected_action_application_id if selected_action is not None else None
        ),
        source_selected_action_application_audit_id=(
            selected_action_audit.selected_action_application_audit_id
            if selected_action_audit is not None
            else None
        ),
        selected_action_valid=selected_action_valid,
        selected_action_application_audit_passed=selected_action_audit_passed,
        teacher_gate_valid=gate_valid,
        final_action_application_valid=application_valid,
        rollback_available=rollback_available,
        actual_final_action_changed=actual_final_action_changed,
        direct_command_created=application.direct_command_created if application else False,
        execution_created=application.execution_created if application else False,
        task_behavior_changed=application.task_behavior_changed if application else False,
        selected_action_changed_by_this_package=(
            application.selected_action_changed_by_this_package if application else False
        ),
        candidate_ordering_changed_by_this_package=(
            application.candidate_ordering_changed_by_this_package
            if application
            else False
        ),
        no_memory_layer_write=not (
            application.memory_layer_write_performed if application else False
        ),
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_automatic_learning_approval=True,
        audit_status=_audit_status(
            blocked_reasons,
            actual_final_action_changed=actual_final_action_changed,
        ),
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(blocked_reasons),
        source_trace_refs=_combined_trace_refs(
            selected_action.source_trace_refs if selected_action else (),
            selected_action_audit.source_trace_refs if selected_action_audit else (),
            gate.source_trace_refs if gate else (),
            application.source_trace_refs if application else (),
            rollback.source_trace_refs if rollback else (),
        ),
    )


def validate_final_action_application_audit(
    audit: FinalActionApplicationAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _final_action_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_final_action_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed_final_action_applied":
        errors.append(record.audit_status)
    if record.actual_final_action_changed and not record.rollback_available:
        errors.append("rollback_missing")
    for flag in (
        "direct_command_created",
        "execution_created",
        "task_behavior_changed",
        "selected_action_changed_by_this_package",
        "candidate_ordering_changed_by_this_package",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    for flag in (
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
        "final_action_application_audit_id": record.final_action_application_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_demo_final_action_application() -> dict[str, object]:
    return _build_final_action_bundle()


def build_demo_final_action_application_audit() -> FinalActionApplicationAudit:
    payload = build_demo_final_action_application()
    return FinalActionApplicationAudit.from_dict(payload["final_action_application_audit"])


def build_demo_final_action_rollback() -> FinalActionRollbackRecord:
    payload = build_demo_final_action_application()
    return FinalActionRollbackRecord.from_dict(payload["final_action_rollback"])


def build_demo_blocked_invalid_selected_action_final_action_application() -> dict[str, object]:
    return _build_final_action_bundle(
        selected_action_payload=build_demo_blocked_teacher_gated_selected_action_application(
            "teacher-rejected"
        )
    )


def build_demo_blocked_invalid_selected_action_audit_final_action_application() -> dict[str, object]:
    return _build_final_action_bundle(
        selected_action_payload=build_demo_blocked_teacher_gated_selected_action_application(
            "missing-rollback"
        )
    )


def build_demo_blocked_missing_teacher_gate_final_action_application() -> dict[str, object]:
    return _build_final_action_bundle(final_action_gate_missing=True)


def build_demo_blocked_teacher_rejected_final_action_application() -> dict[str, object]:
    return _build_final_action_bundle(teacher_gate_status="rejected")


def build_demo_blocked_running_task_mutation_final_action_application() -> dict[str, object]:
    return _build_final_action_bundle(applied_to_running_task=True)


def build_demo_blocked_final_action_mismatch_application() -> dict[str, object]:
    return _build_final_action_bundle(final_action_candidate_override="turn_left")


def build_demo_blocked_direct_command_created_application() -> dict[str, object]:
    return _build_final_action_bundle(direct_command_created=True)


def build_demo_blocked_execution_created_application() -> dict[str, object]:
    return _build_final_action_bundle(execution_created=True)


def build_demo_blocked_task_behavior_changed_application() -> dict[str, object]:
    return _build_final_action_bundle(task_behavior_changed=True)


def build_demo_blocked_missing_rollback_final_action_application() -> dict[str, object]:
    return _build_final_action_bundle(rollback_missing=True)


def build_demo_blocked_memory_write_final_action_application() -> dict[str, object]:
    return _build_final_action_bundle(memory_layer_write_performed=True)


def build_demo_blocked_teacher_gated_final_action_application(
    case: str,
) -> dict[str, object]:
    builders = {
        "invalid-selected-action": (
            build_demo_blocked_invalid_selected_action_final_action_application
        ),
        "invalid-selected-action-audit": (
            build_demo_blocked_invalid_selected_action_audit_final_action_application
        ),
        "missing-teacher-gate": build_demo_blocked_missing_teacher_gate_final_action_application,
        "teacher-rejected": build_demo_blocked_teacher_rejected_final_action_application,
        "running-task-mutation": (
            build_demo_blocked_running_task_mutation_final_action_application
        ),
        "final-action-mismatch": build_demo_blocked_final_action_mismatch_application,
        "direct-command-created": build_demo_blocked_direct_command_created_application,
        "execution-created": build_demo_blocked_execution_created_application,
        "task-behavior-changed": build_demo_blocked_task_behavior_changed_application,
        "missing-rollback": build_demo_blocked_missing_rollback_final_action_application,
        "memory-write-detected": build_demo_blocked_memory_write_final_action_application,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown final_action application blocked case: {case}") from error


def _build_final_action_bundle(
    *,
    selected_action_payload: dict[str, object] | None = None,
    final_action_gate_missing: bool = False,
    teacher_gate_status: str = APPROVED_GATE_STATUS,
    previous_final_action_candidate_id: str | None = None,
    applied_to_running_task: bool = False,
    final_action_candidate_override: str | None = None,
    direct_command_created: bool = False,
    execution_created: bool = False,
    task_behavior_changed: bool = False,
    memory_layer_write_performed: bool = False,
    rollback_missing: bool = False,
) -> dict[str, object]:
    selected_action_payload = selected_action_payload or build_demo_selected_action_application()
    selected_action = SelectedActionApplicationRecord.from_dict(
        selected_action_payload["selected_action_application"]
    )
    selected_action_audit = SelectedActionApplicationAudit.from_dict(
        selected_action_payload["selected_action_application_audit"]
    )
    final_action_gate = (
        None
        if final_action_gate_missing
        else build_teacher_gated_final_action_application_gate(
            selected_action_application=selected_action,
            selected_action_application_audit=selected_action_audit,
            teacher_gate_status=teacher_gate_status,
        )
    )
    final_action_application = apply_teacher_gated_final_action(
        final_action_gate=final_action_gate,
        previous_final_action_candidate_id=previous_final_action_candidate_id,
        applied_to_running_task=applied_to_running_task,
        final_action_candidate_override=final_action_candidate_override,
        direct_command_created=direct_command_created,
        execution_created=execution_created,
        task_behavior_changed=task_behavior_changed,
        memory_layer_write_performed=memory_layer_write_performed,
    )
    rollback = (
        None
        if rollback_missing
        else build_final_action_rollback_record(
            final_action_application=final_action_application
        )
    )
    if rollback is not None and final_action_application.final_action_application_status == FINAL_ACTION_APPLIED_STATUS:
        final_action_application = FinalActionApplicationRecord.from_dict(
            {
                **final_action_application.to_dict(),
                "rollback_available": True,
                "rollback_record_id": rollback.final_action_rollback_id,
            }
        )
    audit = build_final_action_application_audit(
        selected_action_application=selected_action,
        selected_action_application_audit=selected_action_audit,
        final_action_gate=final_action_gate,
        final_action_application=final_action_application,
        rollback_record=rollback,
    )
    return {
        "final_action_application_gate": (
            final_action_gate.to_dict() if final_action_gate else None
        ),
        "final_action_application": final_action_application.to_dict(),
        "final_action_rollback": rollback.to_dict() if rollback else None,
        "final_action_application_audit": audit.to_dict(),
        "final_action_application_gate_validation": (
            validate_teacher_gated_final_action_application_gate(final_action_gate)
            if final_action_gate
            else {"valid": False, "error_codes": ["missing_teacher_gate"]}
        ),
        "final_action_application_validation": (
            validate_final_action_application_record(final_action_application)
        ),
        "final_action_application_audit_validation": (
            validate_final_action_application_audit(audit)
        ),
        "safe_claim": SAFE_CLAIM,
    }


def _selected_action_valid(selected_action: SelectedActionApplicationRecord) -> bool:
    return (
        selected_action.selected_action_application_status == "selected_action_applied"
        and selected_action.actual_selected_action_changed
        and not selected_action.final_action_changed
        and not selected_action.direct_command_created
        and not selected_action.execution_created
        and not selected_action.task_behavior_changed
        and not selected_action.memory_layer_write_performed
        and validate_selected_action_application_record(selected_action)["valid"]
    )


def _approval_source_valid(
    approval_source: str,
    approval_actor_role: str,
    teacher_gate_text: str,
) -> bool:
    if approval_source == "demo_review":
        return approval_actor_role == "system_demo"
    if approval_source == "explicit_teacher_review":
        return approval_actor_role in {"teacher", "project_owner"} and bool(
            teacher_gate_text.strip()
        )
    return False


def _audit_blocked_reasons(
    *,
    selected_action_valid: bool,
    selected_action_audit_passed: bool,
    gate_valid: bool,
    application: FinalActionApplicationRecord | None,
    rollback_available: bool,
) -> list[str]:
    reasons: list[str] = []
    if not selected_action_valid:
        reasons.append("invalid_selected_action")
    if not selected_action_audit_passed:
        reasons.append("invalid_selected_action_audit")
    if not gate_valid:
        reasons.append("invalid_teacher_gate")
    if application is None:
        reasons.append("missing_final_action_application")
        return reasons
    if application.applied_to_running_task:
        reasons.append("running_task_mutation")
    if application.direct_command_created:
        reasons.append("direct_command_created")
    if application.execution_created:
        reasons.append("execution_created")
    if application.task_behavior_changed:
        reasons.append("task_behavior_changed")
    if application.memory_layer_write_performed:
        reasons.append("memory_layer_write_performed")
    if (
        application.final_action_application_status == "blocked_forbidden_authority_detected"
        and not any(
            reason
            in {
                "direct_command_created",
                "execution_created",
                "task_behavior_changed",
                "memory_layer_write_performed",
            }
            for reason in reasons
        )
    ):
        reasons.append("invalid_teacher_gate")
    if (
        application.final_action_application_status == FINAL_ACTION_APPLIED_STATUS
        and not rollback_available
    ):
        reasons.append("missing_rollback")
    return reasons


def _audit_status(
    blocked_reasons: list[str],
    *,
    actual_final_action_changed: bool,
) -> str:
    if "running_task_mutation" in blocked_reasons:
        return "blocked_running_task_mutation_detected"
    if "direct_command_created" in blocked_reasons:
        return "blocked_direct_command_detected"
    if "execution_created" in blocked_reasons:
        return "blocked_execution_detected"
    if "task_behavior_changed" in blocked_reasons:
        return "blocked_task_behavior_change_detected"
    if "memory_layer_write_performed" in blocked_reasons:
        return "blocked_memory_write_detected"
    if "missing_rollback" in blocked_reasons:
        return "failed_missing_rollback"
    if "invalid_selected_action" in blocked_reasons:
        return "blocked_invalid_selected_action"
    if "invalid_teacher_gate" in blocked_reasons:
        return "blocked_invalid_teacher_gate"
    if actual_final_action_changed:
        return "passed_final_action_applied"
    return "passed_no_final_action_applied"


def _application_summary(status: str) -> str:
    if status == FINAL_ACTION_APPLIED_STATUS:
        return "Actual final_action applied from teacher-gated selected_action."
    if status == "held_for_more_evidence":
        return "Final_action application held for more evidence."
    if status == "rejected_by_teacher_gate":
        return "Final_action application rejected by teacher gate."
    return f"Final_action application blocked: {status}."


def _application_reason(status: str, candidate: str | None) -> str:
    if status == FINAL_ACTION_APPLIED_STATUS:
        return (
            f"Teacher gate approved selected_action candidate {candidate} as final_action; "
            "direct_command and execution remain unavailable."
        )
    return status


def _rollback_summary(status: str) -> str:
    if status == "rollback_record_created":
        return "Rollback record can restore previous final_action."
    if status == "rollback_applied_to_restore_previous_final_action":
        return "Rollback restored previous final_action."
    return "Rollback blocked because final_action application was not successful."


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _selected_action_record(
    record: SelectedActionApplicationRecord | dict[str, object],
) -> SelectedActionApplicationRecord:
    return (
        record
        if isinstance(record, SelectedActionApplicationRecord)
        else SelectedActionApplicationRecord.from_dict(dict(record))
    )


def _selected_action_audit(
    record: SelectedActionApplicationAudit | dict[str, object],
) -> SelectedActionApplicationAudit:
    return (
        record
        if isinstance(record, SelectedActionApplicationAudit)
        else SelectedActionApplicationAudit.from_dict(dict(record))
    )


def _final_action_gate(
    record: TeacherGatedFinalActionApplicationGate | dict[str, object],
) -> TeacherGatedFinalActionApplicationGate:
    return (
        record
        if isinstance(record, TeacherGatedFinalActionApplicationGate)
        else TeacherGatedFinalActionApplicationGate.from_dict(dict(record))
    )


def _missing_gate() -> TeacherGatedFinalActionApplicationGate:
    return TeacherGatedFinalActionApplicationGate(
        final_action_application_gate_id="missing:final_action_application_gate",
        schema_version=FINAL_ACTION_GATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id="unknown",
        source_task_initialization_id="unknown",
        source_selected_action_application_id="unknown",
        source_selected_action_application_audit_id="unknown",
        selected_action_candidate_id=None,
        candidate_ordering=(),
        final_action_request_summary="missing final_action application gate",
        final_action_basis="missing",
        teacher_gate_status="blocked_forbidden_authority_detected",
        teacher_gate_reason="teacher gate missing",
        teacher_gate_text="",
        approval_actor="",
        approval_actor_role="",
        approval_source="",
        approved_for_actual_final_action=False,
        approved_for_direct_command=False,
        approved_for_execution=False,
        approved_for_task_behavior_change=False,
        approved_for_memory_layer_write=False,
        requires_final_action_rollback_record=True,
        requires_post_application_audit=True,
        requires_teacher_gate_before_direct_command=True,
        source_trace_refs=(),
    )


def _final_action_application(
    record: FinalActionApplicationRecord | dict[str, object],
) -> FinalActionApplicationRecord:
    return (
        record
        if isinstance(record, FinalActionApplicationRecord)
        else FinalActionApplicationRecord.from_dict(dict(record))
    )


def _final_action_rollback(
    record: FinalActionRollbackRecord | dict[str, object],
) -> FinalActionRollbackRecord:
    return (
        record
        if isinstance(record, FinalActionRollbackRecord)
        else FinalActionRollbackRecord.from_dict(dict(record))
    )


def _final_action_audit(
    record: FinalActionApplicationAudit | dict[str, object],
) -> FinalActionApplicationAudit:
    return (
        record
        if isinstance(record, FinalActionApplicationAudit)
        else FinalActionApplicationAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
