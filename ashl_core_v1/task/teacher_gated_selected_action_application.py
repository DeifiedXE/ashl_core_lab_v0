"""Teacher-gated selected_action application records from proposals."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.task.teacher_gated_selected_action_proposal import (
    SelectedActionProposalAudit,
    SelectedActionProposalRecord,
    build_demo_blocked_teacher_gated_selected_action_proposal,
    build_demo_selected_action_proposal,
    validate_selected_action_proposal_audit,
    validate_selected_action_proposal_record,
)


SOURCE_ENGINE = "task_engine"
APPLICATION_GATE_SCHEMA_VERSION = (
    "task_engine_teacher_gated_selected_action_application_gate_v0"
)
APPLICATION_RECORD_SCHEMA_VERSION = "task_engine_selected_action_application_record_v0"
ROLLBACK_SCHEMA_VERSION = "task_engine_selected_action_rollback_v0"
AUDIT_SCHEMA_VERSION = "task_engine_selected_action_application_audit_v0"

SAFE_CLAIM = (
    "ASHL Core v1 Task Engine can apply a teacher-gated selected_action from "
    "a teacher-gated selected_action proposal, with rollback and audit, while "
    "preserving final_action, direct_command, execution, task behavior, "
    "candidate ordering, and memory-layer boundaries unchanged."
)
BLOCKED_CLAIMS = (
    "no_final_action",
    "no_direct_command",
    "no_action_execution",
    "no_task_behavior_execution",
    "no_candidate_ordering_change_by_this_package",
    "no_core_longterm_archive_anchor_write",
    "no_automatic_learning_approval",
)

APPROVED_GATE_STATUS = "approved_for_actual_selected_action"
APPLICATION_APPLIED_STATUS = "selected_action_applied"

ALLOWED_GATE_STATUSES = {
    "approved_for_actual_selected_action",
    "held_for_more_evidence",
    "rejected",
    "conflict_detected",
    "blocked_invalid_selected_action_proposal",
    "blocked_invalid_selected_action_proposal_audit",
    "blocked_empty_proposal",
    "blocked_forbidden_authority_detected",
}
ALLOWED_APPLICATION_STATUSES = {
    "selected_action_applied",
    "held_for_more_evidence",
    "rejected_by_teacher_gate",
    "blocked_conflict_detected",
    "blocked_invalid_teacher_gate",
    "blocked_invalid_selected_action_proposal",
    "blocked_running_task_mutation_attempt",
    "blocked_forbidden_authority_detected",
    "rollback_applied",
}
ALLOWED_ROLLBACK_STATUSES = {
    "rollback_record_created",
    "rollback_applied_to_restore_previous_selected_action",
    "blocked_invalid_selected_action_application",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_selected_action_applied",
    "passed_no_selected_action_applied",
    "failed_missing_rollback",
    "blocked_invalid_selected_action_proposal",
    "blocked_invalid_teacher_gate",
    "blocked_running_task_mutation_detected",
    "blocked_final_action_change_detected",
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
class TeacherGatedSelectedActionApplicationGate:
    selected_action_application_gate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str
    source_selected_action_proposal_id: str
    source_selected_action_proposal_audit_id: str
    candidate_ordering: tuple[str, ...]
    proposed_selected_action_candidate_id: str | None
    application_request_summary: str
    application_basis: str
    teacher_gate_status: str
    teacher_gate_reason: str
    teacher_gate_text: str
    approval_actor: str
    approval_actor_role: str
    approval_source: str
    approved_for_actual_selected_action: bool
    approved_for_final_action: bool
    approved_for_direct_command: bool
    approved_for_execution: bool
    approved_for_task_behavior_change: bool
    approved_for_memory_layer_write: bool
    requires_selected_action_rollback_record: bool
    requires_post_application_audit: bool
    requires_teacher_gate_before_final_action: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != APPLICATION_GATE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_teacher_gated_selected_action_application_gate_v0"
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
    def from_dict(cls, data: dict[str, object]) -> "TeacherGatedSelectedActionApplicationGate":
        return cls(**dict(data))


@dataclass(frozen=True)
class SelectedActionApplicationRecord:
    selected_action_application_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str
    source_selected_action_application_gate_id: str
    source_selected_action_proposal_id: str
    source_selected_action_proposal_audit_id: str
    candidate_ordering: tuple[str, ...]
    applied_selected_action_candidate_id: str | None
    previous_selected_action_candidate_id: str | None
    selected_action_application_status: str
    selected_action_application_summary: str
    selected_action_application_reason: str
    actual_selected_action_changed: bool
    final_action_changed: bool
    direct_command_created: bool
    execution_created: bool
    task_behavior_changed: bool
    candidate_ordering_changed_by_this_package: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    applied_to_new_task_initialization: bool
    applied_to_running_task: bool
    available_for_future_final_action_review: bool
    requires_teacher_gate_before_final_action: bool
    rollback_available: bool
    rollback_record_id: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != APPLICATION_RECORD_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_selected_action_application_record_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.selected_action_application_status not in ALLOWED_APPLICATION_STATUSES:
            raise ValueError(
                "unknown selected_action_application_status: "
                f"{self.selected_action_application_status}"
            )
        for name in ("candidate_ordering", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SelectedActionApplicationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class SelectedActionRollbackRecord:
    selected_action_rollback_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_selected_action_application_id: str
    source_task_working_memory_id: str
    selected_action_before_application: str | None
    selected_action_after_application: str | None
    selected_action_after_rollback: str | None
    rollback_available: bool
    rollback_applied: bool
    rollback_reason: str
    rollback_status: str
    rollback_summary: str
    final_action_changed: bool
    direct_command_created: bool
    execution_created: bool
    task_behavior_changed: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ROLLBACK_SCHEMA_VERSION:
            raise ValueError("schema_version must be task_engine_selected_action_rollback_v0")
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
    def from_dict(cls, data: dict[str, object]) -> "SelectedActionRollbackRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class SelectedActionApplicationAudit:
    selected_action_application_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_selected_action_application_gate_id: str | None
    source_selected_action_application_id: str | None
    source_selected_action_rollback_id: str | None
    source_selected_action_proposal_id: str | None
    source_selected_action_proposal_audit_id: str | None
    selected_action_proposal_valid: bool
    selected_action_proposal_audit_passed: bool
    teacher_gate_valid: bool
    selected_action_application_valid: bool
    rollback_available: bool
    actual_selected_action_changed: bool
    final_action_changed: bool
    direct_command_created: bool
    execution_created: bool
    task_behavior_changed: bool
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
        if self.schema_version != AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_selected_action_application_audit_v0"
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
    def from_dict(cls, data: dict[str, object]) -> "SelectedActionApplicationAudit":
        return cls(**dict(data))


def build_teacher_gated_selected_action_application_gate(
    *,
    selected_action_proposal: SelectedActionProposalRecord | dict[str, object],
    selected_action_proposal_audit: SelectedActionProposalAudit | dict[str, object],
    teacher_gate_status: str = APPROVED_GATE_STATUS,
    teacher_gate_reason: str = "teacher approved actual selected_action application",
    teacher_gate_text: str = "Demo teacher gate approves actual selected_action only.",
    approval_actor: str = "system_demo",
    approval_actor_role: str = "system_demo",
    approval_source: str = "demo_review",
    approved_for_final_action: bool = False,
    approved_for_direct_command: bool = False,
    approved_for_execution: bool = False,
    approved_for_task_behavior_change: bool = False,
    approved_for_memory_layer_write: bool = False,
) -> TeacherGatedSelectedActionApplicationGate:
    proposal = _proposal_record(selected_action_proposal)
    proposal_audit = _proposal_audit(selected_action_proposal_audit)
    forbidden_authority = any(
        (
            approved_for_final_action,
            approved_for_direct_command,
            approved_for_execution,
            approved_for_task_behavior_change,
            approved_for_memory_layer_write,
        )
    )
    proposal_valid = _proposal_valid(proposal)
    audit_passed = proposal_audit.audit_status == "passed_selected_action_proposal_created"
    if not proposal.proposed_selected_action_candidate_id:
        status = "blocked_empty_proposal"
    elif not proposal_valid:
        status = "blocked_invalid_selected_action_proposal"
    elif not audit_passed:
        status = "blocked_invalid_selected_action_proposal_audit"
    elif forbidden_authority or not _approval_source_valid(
        approval_source,
        approval_actor_role,
        teacher_gate_text,
    ):
        status = "blocked_forbidden_authority_detected"
    else:
        status = teacher_gate_status
    return TeacherGatedSelectedActionApplicationGate(
        selected_action_application_gate_id=(
            "teacher_gated_selected_action_application_gate:"
            f"{proposal.source_task_initialization_id}"
        ),
        schema_version=APPLICATION_GATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=proposal.source_task_working_memory_id,
        source_task_initialization_id=proposal.source_task_initialization_id,
        source_selected_action_proposal_id=proposal.selected_action_proposal_id,
        source_selected_action_proposal_audit_id=(
            proposal_audit.selected_action_proposal_audit_id
        ),
        candidate_ordering=proposal.candidate_ordering,
        proposed_selected_action_candidate_id=proposal.proposed_selected_action_candidate_id,
        application_request_summary=(
            "Apply the teacher-gated selected_action proposal as actual selected_action."
        ),
        application_basis="teacher_gated_selected_action_proposal",
        teacher_gate_status=status,
        teacher_gate_reason=teacher_gate_reason,
        teacher_gate_text=teacher_gate_text,
        approval_actor=approval_actor,
        approval_actor_role=approval_actor_role,
        approval_source=approval_source,
        approved_for_actual_selected_action=status == APPROVED_GATE_STATUS,
        approved_for_final_action=False,
        approved_for_direct_command=False,
        approved_for_execution=False,
        approved_for_task_behavior_change=False,
        approved_for_memory_layer_write=False,
        requires_selected_action_rollback_record=True,
        requires_post_application_audit=True,
        requires_teacher_gate_before_final_action=True,
        source_trace_refs=_combined_trace_refs(
            proposal.source_trace_refs,
            proposal_audit.source_trace_refs,
        ),
    )


def validate_teacher_gated_selected_action_application_gate(
    application_gate: TeacherGatedSelectedActionApplicationGate | dict[str, object],
) -> dict[str, object]:
    try:
        gate = _application_gate(application_gate)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_application_gate:{error}"]}
    errors: list[str] = []
    if gate.approved_for_actual_selected_action is not (
        gate.teacher_gate_status == APPROVED_GATE_STATUS
    ):
        errors.append("actual_selected_action_approval_mismatch")
    if gate.approval_source == "explicit_teacher_review":
        if gate.approval_actor_role not in {"teacher", "project_owner"}:
            errors.append("invalid_explicit_actor_role")
        if not gate.teacher_gate_text.strip():
            errors.append("teacher_gate_text_required")
    if gate.approval_source == "demo_review" and gate.approval_actor_role != "system_demo":
        errors.append("demo_review_requires_system_demo_role")
    for flag in (
        "approved_for_final_action",
        "approved_for_direct_command",
        "approved_for_execution",
        "approved_for_task_behavior_change",
        "approved_for_memory_layer_write",
    ):
        if getattr(gate, flag) is not False:
            errors.append(f"{flag}_true")
    for flag in (
        "requires_selected_action_rollback_record",
        "requires_post_application_audit",
        "requires_teacher_gate_before_final_action",
    ):
        if getattr(gate, flag) is not True:
            errors.append(f"{flag}_false")
    if gate.teacher_gate_status.startswith("blocked_"):
        errors.append(gate.teacher_gate_status)
    return {
        "valid": not errors,
        "error_codes": errors,
        "selected_action_application_gate_id": gate.selected_action_application_gate_id,
        "teacher_gate_status": gate.teacher_gate_status,
    }


def apply_teacher_gated_selected_action(
    *,
    application_gate: TeacherGatedSelectedActionApplicationGate | dict[str, object] | None,
    previous_selected_action_candidate_id: str | None = None,
    applied_to_running_task: bool = False,
    selected_action_candidate_override: str | None = None,
    final_action_changed: bool = False,
    direct_command_created: bool = False,
    execution_created: bool = False,
    task_behavior_changed: bool = False,
    memory_layer_write_performed: bool = False,
    rollback_record_id: str | None = None,
) -> SelectedActionApplicationRecord:
    gate = _application_gate(application_gate) if application_gate is not None else _missing_gate()
    forbidden_authority = any(
        (
            final_action_changed,
            direct_command_created,
            execution_created,
            task_behavior_changed,
            memory_layer_write_performed,
        )
    )
    requested_candidate = (
        selected_action_candidate_override
        if selected_action_candidate_override is not None
        else gate.proposed_selected_action_candidate_id
    )
    mismatch = (
        gate.teacher_gate_status == APPROVED_GATE_STATUS
        and requested_candidate != gate.proposed_selected_action_candidate_id
    )
    if applied_to_running_task:
        status = "blocked_running_task_mutation_attempt"
    elif forbidden_authority or mismatch:
        status = "blocked_forbidden_authority_detected"
    elif gate.teacher_gate_status == APPROVED_GATE_STATUS:
        status = APPLICATION_APPLIED_STATUS
    elif gate.teacher_gate_status == "held_for_more_evidence":
        status = "held_for_more_evidence"
    elif gate.teacher_gate_status == "rejected":
        status = "rejected_by_teacher_gate"
    elif gate.teacher_gate_status == "conflict_detected":
        status = "blocked_conflict_detected"
    elif gate.teacher_gate_status in {
        "blocked_empty_proposal",
        "blocked_invalid_selected_action_proposal",
        "blocked_invalid_selected_action_proposal_audit",
    }:
        status = "blocked_invalid_selected_action_proposal"
    else:
        status = "blocked_invalid_teacher_gate"
    applied = status == APPLICATION_APPLIED_STATUS
    return SelectedActionApplicationRecord(
        selected_action_application_id=(
            "selected_action_application:"
            f"{gate.source_task_initialization_id}"
        ),
        schema_version=APPLICATION_RECORD_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=gate.source_task_working_memory_id,
        source_task_initialization_id=gate.source_task_initialization_id,
        source_selected_action_application_gate_id=gate.selected_action_application_gate_id,
        source_selected_action_proposal_id=gate.source_selected_action_proposal_id,
        source_selected_action_proposal_audit_id=gate.source_selected_action_proposal_audit_id,
        candidate_ordering=gate.candidate_ordering,
        applied_selected_action_candidate_id=requested_candidate if applied else None,
        previous_selected_action_candidate_id=previous_selected_action_candidate_id,
        selected_action_application_status=status,
        selected_action_application_summary=_application_summary(status),
        selected_action_application_reason=_application_reason(status, requested_candidate),
        actual_selected_action_changed=applied,
        final_action_changed=final_action_changed,
        direct_command_created=direct_command_created,
        execution_created=execution_created,
        task_behavior_changed=task_behavior_changed,
        candidate_ordering_changed_by_this_package=False,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=False,
        applied_to_new_task_initialization=applied,
        applied_to_running_task=applied_to_running_task,
        available_for_future_final_action_review=applied,
        requires_teacher_gate_before_final_action=True,
        rollback_available=applied,
        rollback_record_id=rollback_record_id,
        source_trace_refs=gate.source_trace_refs,
    )


def validate_selected_action_application_record(
    application_record: SelectedActionApplicationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        application = _application_record(application_record)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_application_record:{error}"]}
    errors: list[str] = []
    applied = application.selected_action_application_status == APPLICATION_APPLIED_STATUS
    if application.actual_selected_action_changed is not applied:
        errors.append("actual_selected_action_changed_mismatch")
    if applied:
        if not application.applied_selected_action_candidate_id:
            errors.append("applied_selected_action_missing")
        if not application.available_for_future_final_action_review:
            errors.append("available_for_future_final_action_review_false")
    for flag in (
        "final_action_changed",
        "direct_command_created",
        "execution_created",
        "task_behavior_changed",
        "candidate_ordering_changed_by_this_package",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
        "applied_to_running_task",
    ):
        if getattr(application, flag) is not False:
            errors.append(f"{flag}_true")
    if application.requires_teacher_gate_before_final_action is not True:
        errors.append("requires_teacher_gate_before_final_action_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "selected_action_application_id": application.selected_action_application_id,
        "selected_action_application_status": application.selected_action_application_status,
    }


def build_selected_action_rollback_record(
    *,
    selected_action_application: SelectedActionApplicationRecord | dict[str, object],
    rollback_applied: bool = False,
    rollback_reason: str = "rollback data available to restore previous selected_action",
) -> SelectedActionRollbackRecord:
    application = _application_record(selected_action_application)
    valid_application = (
        application.selected_action_application_status == APPLICATION_APPLIED_STATUS
    )
    rollback_status = (
        "rollback_applied_to_restore_previous_selected_action"
        if rollback_applied and valid_application
        else "rollback_record_created"
        if valid_application
        else "blocked_invalid_selected_action_application"
    )
    return SelectedActionRollbackRecord(
        selected_action_rollback_id=(
            "selected_action_rollback:"
            f"{application.selected_action_application_id}"
        ),
        schema_version=ROLLBACK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_selected_action_application_id=application.selected_action_application_id,
        source_task_working_memory_id=application.source_task_working_memory_id,
        selected_action_before_application=application.previous_selected_action_candidate_id,
        selected_action_after_application=application.applied_selected_action_candidate_id,
        selected_action_after_rollback=(
            application.previous_selected_action_candidate_id
            if rollback_applied and valid_application
            else application.applied_selected_action_candidate_id
        ),
        rollback_available=valid_application,
        rollback_applied=rollback_applied and valid_application,
        rollback_reason=rollback_reason,
        rollback_status=rollback_status,
        rollback_summary=_rollback_summary(rollback_status),
        final_action_changed=False,
        direct_command_created=False,
        execution_created=False,
        task_behavior_changed=False,
        memory_layer_write_performed=False,
        source_trace_refs=application.source_trace_refs,
    )


def apply_selected_action_rollback(
    rollback_record: SelectedActionRollbackRecord | dict[str, object],
) -> dict[str, object]:
    rollback = _rollback_record(rollback_record)
    return {
        "rollback_status": "rollback_applied_to_restore_previous_selected_action"
        if rollback.rollback_available
        else "blocked_invalid_selected_action_application",
        "selected_action_after_rollback": (
            rollback.selected_action_before_application
            if rollback.rollback_available
            else None
        ),
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
        "task_behavior_changed": False,
        "memory_layer_write_performed": False,
    }


def build_selected_action_application_audit(
    *,
    selected_action_proposal: SelectedActionProposalRecord | dict[str, object] | None,
    selected_action_proposal_audit: SelectedActionProposalAudit | dict[str, object] | None,
    application_gate: TeacherGatedSelectedActionApplicationGate | dict[str, object] | None,
    selected_action_application: SelectedActionApplicationRecord | dict[str, object] | None,
    rollback_record: SelectedActionRollbackRecord | dict[str, object] | None,
) -> SelectedActionApplicationAudit:
    proposal = _proposal_record(selected_action_proposal) if selected_action_proposal is not None else None
    proposal_audit = _proposal_audit(selected_action_proposal_audit) if selected_action_proposal_audit is not None else None
    gate = _application_gate(application_gate) if application_gate is not None else None
    application = _application_record(selected_action_application) if selected_action_application is not None else None
    rollback = _rollback_record(rollback_record) if rollback_record is not None else None
    proposal_valid = proposal is not None and _proposal_valid(proposal)
    proposal_audit_passed = (
        proposal_audit is not None
        and proposal_audit.audit_status == "passed_selected_action_proposal_created"
    )
    gate_valid = (
        gate is not None
        and validate_teacher_gated_selected_action_application_gate(gate)["valid"]
    )
    application_valid = (
        application is not None
        and validate_selected_action_application_record(application)["valid"]
    )
    rollback_available = rollback is not None and rollback.rollback_available
    blocked_reasons = _audit_blocked_reasons(
        proposal_valid=proposal_valid,
        proposal_audit_passed=proposal_audit_passed,
        gate_valid=gate_valid,
        application=application,
        rollback_available=rollback_available,
    )
    actual_selected_action_changed = (
        application.actual_selected_action_changed if application is not None else False
    )
    return SelectedActionApplicationAudit(
        selected_action_application_audit_id=(
            "selected_action_application_audit:"
            f"{(application.source_task_working_memory_id if application else 'unknown')}"
        ),
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=(
            application.source_task_working_memory_id if application else "unknown"
        ),
        source_selected_action_application_gate_id=(
            gate.selected_action_application_gate_id if gate is not None else None
        ),
        source_selected_action_application_id=(
            application.selected_action_application_id if application is not None else None
        ),
        source_selected_action_rollback_id=(
            rollback.selected_action_rollback_id if rollback is not None else None
        ),
        source_selected_action_proposal_id=(
            proposal.selected_action_proposal_id if proposal is not None else None
        ),
        source_selected_action_proposal_audit_id=(
            proposal_audit.selected_action_proposal_audit_id
            if proposal_audit is not None
            else None
        ),
        selected_action_proposal_valid=proposal_valid,
        selected_action_proposal_audit_passed=proposal_audit_passed,
        teacher_gate_valid=gate_valid,
        selected_action_application_valid=application_valid,
        rollback_available=rollback_available,
        actual_selected_action_changed=actual_selected_action_changed,
        final_action_changed=application.final_action_changed if application else False,
        direct_command_created=application.direct_command_created if application else False,
        execution_created=application.execution_created if application else False,
        task_behavior_changed=application.task_behavior_changed if application else False,
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
            actual_selected_action_changed=actual_selected_action_changed,
        ),
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(blocked_reasons),
        source_trace_refs=_combined_trace_refs(
            proposal.source_trace_refs if proposal else (),
            proposal_audit.source_trace_refs if proposal_audit else (),
            gate.source_trace_refs if gate else (),
            application.source_trace_refs if application else (),
            rollback.source_trace_refs if rollback else (),
        ),
    )


def validate_selected_action_application_audit(
    audit: SelectedActionApplicationAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _application_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_application_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed_selected_action_applied":
        errors.append(record.audit_status)
    if record.actual_selected_action_changed and not record.rollback_available:
        errors.append("rollback_missing")
    for flag in (
        "final_action_changed",
        "direct_command_created",
        "execution_created",
        "task_behavior_changed",
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
        "selected_action_application_audit_id": record.selected_action_application_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_demo_selected_action_application() -> dict[str, object]:
    return _build_application_bundle()


def build_demo_selected_action_application_audit() -> SelectedActionApplicationAudit:
    payload = build_demo_selected_action_application()
    return SelectedActionApplicationAudit.from_dict(payload["selected_action_application_audit"])


def build_demo_selected_action_rollback() -> SelectedActionRollbackRecord:
    payload = build_demo_selected_action_application()
    return SelectedActionRollbackRecord.from_dict(payload["selected_action_rollback"])


def build_demo_blocked_invalid_proposal_selected_action_application() -> dict[str, object]:
    return _build_application_bundle(
        proposal_payload=build_demo_blocked_teacher_gated_selected_action_proposal(
            "teacher-rejected"
        )
    )


def build_demo_blocked_invalid_proposal_audit_selected_action_application() -> dict[str, object]:
    return _build_application_bundle(
        proposal_payload=build_demo_blocked_teacher_gated_selected_action_proposal(
            "missing-rollback"
        )
    )


def build_demo_blocked_missing_teacher_gate_selected_action_application() -> dict[str, object]:
    return _build_application_bundle(application_gate_missing=True)


def build_demo_blocked_teacher_rejected_selected_action_application() -> dict[str, object]:
    return _build_application_bundle(teacher_gate_status="rejected")


def build_demo_blocked_running_task_mutation_selected_action_application() -> dict[str, object]:
    return _build_application_bundle(applied_to_running_task=True)


def build_demo_blocked_selected_action_mismatch_application() -> dict[str, object]:
    return _build_application_bundle(selected_action_candidate_override="turn_left")


def build_demo_blocked_final_action_mutated_application() -> dict[str, object]:
    return _build_application_bundle(final_action_changed=True)


def build_demo_blocked_direct_command_created_application() -> dict[str, object]:
    return _build_application_bundle(direct_command_created=True)


def build_demo_blocked_execution_created_application() -> dict[str, object]:
    return _build_application_bundle(execution_created=True)


def build_demo_blocked_task_behavior_changed_application() -> dict[str, object]:
    return _build_application_bundle(task_behavior_changed=True)


def build_demo_blocked_missing_rollback_selected_action_application() -> dict[str, object]:
    return _build_application_bundle(rollback_missing=True)


def build_demo_blocked_memory_write_selected_action_application() -> dict[str, object]:
    return _build_application_bundle(memory_layer_write_performed=True)


def build_demo_blocked_teacher_gated_selected_action_application(
    case: str,
) -> dict[str, object]:
    builders = {
        "invalid-proposal": build_demo_blocked_invalid_proposal_selected_action_application,
        "invalid-proposal-audit": (
            build_demo_blocked_invalid_proposal_audit_selected_action_application
        ),
        "missing-teacher-gate": (
            build_demo_blocked_missing_teacher_gate_selected_action_application
        ),
        "teacher-rejected": build_demo_blocked_teacher_rejected_selected_action_application,
        "running-task-mutation": (
            build_demo_blocked_running_task_mutation_selected_action_application
        ),
        "selected-action-mismatch": build_demo_blocked_selected_action_mismatch_application,
        "final-action-mutated": build_demo_blocked_final_action_mutated_application,
        "direct-command-created": build_demo_blocked_direct_command_created_application,
        "execution-created": build_demo_blocked_execution_created_application,
        "task-behavior-changed": build_demo_blocked_task_behavior_changed_application,
        "missing-rollback": build_demo_blocked_missing_rollback_selected_action_application,
        "memory-write-detected": build_demo_blocked_memory_write_selected_action_application,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown selected_action application blocked case: {case}") from error


def _build_application_bundle(
    *,
    proposal_payload: dict[str, object] | None = None,
    application_gate_missing: bool = False,
    teacher_gate_status: str = APPROVED_GATE_STATUS,
    previous_selected_action_candidate_id: str | None = None,
    applied_to_running_task: bool = False,
    selected_action_candidate_override: str | None = None,
    final_action_changed: bool = False,
    direct_command_created: bool = False,
    execution_created: bool = False,
    task_behavior_changed: bool = False,
    memory_layer_write_performed: bool = False,
    rollback_missing: bool = False,
) -> dict[str, object]:
    proposal_payload = proposal_payload or build_demo_selected_action_proposal()
    proposal = SelectedActionProposalRecord.from_dict(
        proposal_payload["selected_action_proposal"]
    )
    proposal_audit = SelectedActionProposalAudit.from_dict(
        proposal_payload["selected_action_proposal_audit"]
    )
    application_gate = (
        None
        if application_gate_missing
        else build_teacher_gated_selected_action_application_gate(
            selected_action_proposal=proposal,
            selected_action_proposal_audit=proposal_audit,
            teacher_gate_status=teacher_gate_status,
        )
    )
    application = apply_teacher_gated_selected_action(
        application_gate=application_gate,
        previous_selected_action_candidate_id=previous_selected_action_candidate_id,
        applied_to_running_task=applied_to_running_task,
        selected_action_candidate_override=selected_action_candidate_override,
        final_action_changed=final_action_changed,
        direct_command_created=direct_command_created,
        execution_created=execution_created,
        task_behavior_changed=task_behavior_changed,
        memory_layer_write_performed=memory_layer_write_performed,
    )
    rollback = (
        None
        if rollback_missing
        else build_selected_action_rollback_record(selected_action_application=application)
    )
    if rollback is not None and application.selected_action_application_status == APPLICATION_APPLIED_STATUS:
        application = SelectedActionApplicationRecord.from_dict(
            {
                **application.to_dict(),
                "rollback_available": True,
                "rollback_record_id": rollback.selected_action_rollback_id,
            }
        )
    audit = build_selected_action_application_audit(
        selected_action_proposal=proposal,
        selected_action_proposal_audit=proposal_audit,
        application_gate=application_gate,
        selected_action_application=application,
        rollback_record=rollback,
    )
    return {
        "selected_action_application_gate": (
            application_gate.to_dict() if application_gate else None
        ),
        "selected_action_application": application.to_dict(),
        "selected_action_rollback": rollback.to_dict() if rollback else None,
        "selected_action_application_audit": audit.to_dict(),
        "selected_action_application_gate_validation": (
            validate_teacher_gated_selected_action_application_gate(application_gate)
            if application_gate
            else {"valid": False, "error_codes": ["missing_teacher_gate"]}
        ),
        "selected_action_application_validation": (
            validate_selected_action_application_record(application)
        ),
        "selected_action_application_audit_validation": (
            validate_selected_action_application_audit(audit)
        ),
        "safe_claim": SAFE_CLAIM,
    }


def _proposal_valid(proposal: SelectedActionProposalRecord) -> bool:
    return (
        proposal.proposal_status == "selected_action_proposal_created"
        and proposal.selected_action_proposal_created
        and not proposal.actual_selected_action_changed
        and not proposal.final_action_changed
        and not proposal.direct_command_created
        and not proposal.execution_created
        and not proposal.task_behavior_changed
        and not proposal.memory_layer_write_performed
        and validate_selected_action_proposal_record(proposal)["valid"]
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
    proposal_valid: bool,
    proposal_audit_passed: bool,
    gate_valid: bool,
    application: SelectedActionApplicationRecord | None,
    rollback_available: bool,
) -> list[str]:
    reasons: list[str] = []
    if not proposal_valid:
        reasons.append("invalid_selected_action_proposal")
    if not proposal_audit_passed:
        reasons.append("invalid_selected_action_proposal_audit")
    if not gate_valid:
        reasons.append("invalid_teacher_gate")
    if application is None:
        reasons.append("missing_selected_action_application")
        return reasons
    if application.applied_to_running_task:
        reasons.append("running_task_mutation")
    if application.final_action_changed:
        reasons.append("final_action_changed")
    if application.direct_command_created:
        reasons.append("direct_command_created")
    if application.execution_created:
        reasons.append("execution_created")
    if application.task_behavior_changed:
        reasons.append("task_behavior_changed")
    if application.memory_layer_write_performed:
        reasons.append("memory_layer_write_performed")
    if (
        application.selected_action_application_status == APPLICATION_APPLIED_STATUS
        and not rollback_available
    ):
        reasons.append("missing_rollback")
    return reasons


def _audit_status(
    blocked_reasons: list[str],
    *,
    actual_selected_action_changed: bool,
) -> str:
    if "running_task_mutation" in blocked_reasons:
        return "blocked_running_task_mutation_detected"
    if "final_action_changed" in blocked_reasons:
        return "blocked_final_action_change_detected"
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
    if "invalid_selected_action_proposal" in blocked_reasons:
        return "blocked_invalid_selected_action_proposal"
    if "invalid_teacher_gate" in blocked_reasons:
        return "blocked_invalid_teacher_gate"
    if actual_selected_action_changed:
        return "passed_selected_action_applied"
    return "passed_no_selected_action_applied"


def _application_summary(status: str) -> str:
    if status == APPLICATION_APPLIED_STATUS:
        return "Actual selected_action applied from teacher-gated proposal."
    if status == "held_for_more_evidence":
        return "Selected_action application held for more evidence."
    if status == "rejected_by_teacher_gate":
        return "Selected_action application rejected by teacher gate."
    return f"Selected_action application blocked: {status}."


def _application_reason(status: str, candidate: str | None) -> str:
    if status == APPLICATION_APPLIED_STATUS:
        return (
            f"Teacher gate approved proposal candidate {candidate}; final_action "
            "and execution remain unavailable."
        )
    return status


def _rollback_summary(status: str) -> str:
    if status == "rollback_record_created":
        return "Rollback record can restore previous selected_action."
    if status == "rollback_applied_to_restore_previous_selected_action":
        return "Rollback restored previous selected_action."
    return "Rollback blocked because selected_action application was not successful."


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _proposal_record(
    record: SelectedActionProposalRecord | dict[str, object],
) -> SelectedActionProposalRecord:
    return (
        record
        if isinstance(record, SelectedActionProposalRecord)
        else SelectedActionProposalRecord.from_dict(dict(record))
    )


def _proposal_audit(
    record: SelectedActionProposalAudit | dict[str, object],
) -> SelectedActionProposalAudit:
    return (
        record
        if isinstance(record, SelectedActionProposalAudit)
        else SelectedActionProposalAudit.from_dict(dict(record))
    )


def _application_gate(
    record: TeacherGatedSelectedActionApplicationGate | dict[str, object],
) -> TeacherGatedSelectedActionApplicationGate:
    return (
        record
        if isinstance(record, TeacherGatedSelectedActionApplicationGate)
        else TeacherGatedSelectedActionApplicationGate.from_dict(dict(record))
    )


def _missing_gate() -> TeacherGatedSelectedActionApplicationGate:
    return TeacherGatedSelectedActionApplicationGate(
        selected_action_application_gate_id="missing:selected_action_application_gate",
        schema_version=APPLICATION_GATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id="unknown",
        source_task_initialization_id="unknown",
        source_selected_action_proposal_id="unknown",
        source_selected_action_proposal_audit_id="unknown",
        candidate_ordering=(),
        proposed_selected_action_candidate_id=None,
        application_request_summary="missing selected_action application gate",
        application_basis="missing",
        teacher_gate_status="blocked_forbidden_authority_detected",
        teacher_gate_reason="teacher gate missing",
        teacher_gate_text="",
        approval_actor="",
        approval_actor_role="",
        approval_source="",
        approved_for_actual_selected_action=False,
        approved_for_final_action=False,
        approved_for_direct_command=False,
        approved_for_execution=False,
        approved_for_task_behavior_change=False,
        approved_for_memory_layer_write=False,
        requires_selected_action_rollback_record=True,
        requires_post_application_audit=True,
        requires_teacher_gate_before_final_action=True,
        source_trace_refs=(),
    )


def _application_record(
    record: SelectedActionApplicationRecord | dict[str, object],
) -> SelectedActionApplicationRecord:
    return (
        record
        if isinstance(record, SelectedActionApplicationRecord)
        else SelectedActionApplicationRecord.from_dict(dict(record))
    )


def _rollback_record(
    record: SelectedActionRollbackRecord | dict[str, object],
) -> SelectedActionRollbackRecord:
    return (
        record
        if isinstance(record, SelectedActionRollbackRecord)
        else SelectedActionRollbackRecord.from_dict(dict(record))
    )


def _application_audit(
    record: SelectedActionApplicationAudit | dict[str, object],
) -> SelectedActionApplicationAudit:
    return (
        record
        if isinstance(record, SelectedActionApplicationAudit)
        else SelectedActionApplicationAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
