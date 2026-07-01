"""Teacher-gated selected_action proposal records from candidate ordering."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.task.advisory_readback_candidate_ordering_application import (
    APPLIED_STATUS as ORDERING_APPLIED_STATUS,
    AdvisoryReadbackCandidateOrderingApplicationAudit,
    AdvisoryReadbackCandidateOrderingApplicationRecord,
    build_demo_blocked_advisory_readback_candidate_ordering_application,
    build_demo_teacher_gated_ordering_application,
    validate_advisory_readback_candidate_ordering_application_audit,
    validate_advisory_readback_candidate_ordering_application_record,
)


SOURCE_ENGINE = "task_engine"
PROPOSAL_GATE_SCHEMA_VERSION = (
    "task_engine_teacher_gated_selected_action_proposal_gate_v0"
)
PROPOSAL_RECORD_SCHEMA_VERSION = "task_engine_selected_action_proposal_record_v0"
PROPOSAL_ROLLBACK_SCHEMA_VERSION = "task_engine_selected_action_proposal_rollback_v0"
PROPOSAL_AUDIT_SCHEMA_VERSION = "task_engine_selected_action_proposal_audit_v0"

SAFE_CLAIM = (
    "ASHL Core v1 Task Engine can create teacher-gated selected_action "
    "proposal records from teacher-gated candidate ordering, with rollback "
    "and audit, while preserving actual selected_action, final_action, "
    "direct_command, execution, task behavior, candidate ordering, and "
    "memory-layer boundaries unchanged."
)
BLOCKED_CLAIMS = (
    "no_actual_selected_action",
    "no_final_action",
    "no_direct_command",
    "no_action_execution",
    "no_task_behavior_change",
    "no_candidate_ordering_change_by_this_package",
    "no_core_longterm_archive_anchor_write",
    "no_automatic_learning_approval",
)

APPROVED_GATE_STATUS = "approved_for_selected_action_proposal"
PROPOSAL_CREATED_STATUS = "selected_action_proposal_created"

ALLOWED_PROPOSAL_GATE_STATUSES = {
    "approved_for_selected_action_proposal",
    "held_for_more_evidence",
    "rejected",
    "conflict_detected",
    "blocked_invalid_ordering_application",
    "blocked_invalid_ordering_audit",
    "blocked_empty_candidate_ordering",
    "blocked_forbidden_authority_detected",
}
ALLOWED_PROPOSAL_STATUSES = {
    "selected_action_proposal_created",
    "held_for_more_evidence",
    "rejected_by_teacher_gate",
    "blocked_conflict_detected",
    "blocked_invalid_teacher_gate",
    "blocked_empty_candidate_ordering",
    "blocked_forbidden_authority_detected",
    "rollback_applied",
}
ALLOWED_ROLLBACK_STATUSES = {
    "rollback_record_created",
    "rollback_applied_to_withdraw_proposal",
    "blocked_invalid_proposal_record",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_selected_action_proposal_created",
    "passed_no_proposal_created",
    "failed_missing_rollback",
    "blocked_invalid_ordering_application",
    "blocked_invalid_teacher_gate",
    "blocked_actual_selected_action_change_detected",
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
class TeacherGatedSelectedActionProposalGate:
    selected_action_proposal_gate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str
    source_ordering_application_id: str
    source_ordering_application_audit_id: str
    candidate_ordering: tuple[str, ...]
    top_candidate_id: str | None
    proposal_request_summary: str
    proposal_basis: str
    teacher_gate_status: str
    teacher_gate_reason: str
    teacher_gate_text: str
    approval_actor: str
    approval_actor_role: str
    approval_source: str
    approved_for_selected_action_proposal: bool
    approved_for_actual_selected_action: bool
    approved_for_final_action: bool
    approved_for_direct_command: bool
    approved_for_execution: bool
    approved_for_task_behavior_change: bool
    approved_for_memory_layer_write: bool
    requires_proposal_rollback_record: bool
    requires_post_proposal_audit: bool
    requires_teacher_gate_before_selected_action_application: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PROPOSAL_GATE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_teacher_gated_selected_action_proposal_gate_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.teacher_gate_status not in ALLOWED_PROPOSAL_GATE_STATUSES:
            raise ValueError(f"unknown teacher_gate_status: {self.teacher_gate_status}")
        for name in ("candidate_ordering", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TeacherGatedSelectedActionProposalGate":
        return cls(**dict(data))


@dataclass(frozen=True)
class SelectedActionProposalRecord:
    selected_action_proposal_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str
    source_selected_action_proposal_gate_id: str
    source_ordering_application_id: str
    source_ordering_application_audit_id: str
    candidate_ordering: tuple[str, ...]
    proposed_selected_action_candidate_id: str | None
    proposal_rank: int | None
    proposal_status: str
    proposal_summary: str
    proposal_reason: str
    selected_action_proposal_created: bool
    actual_selected_action_changed: bool
    final_action_changed: bool
    direct_command_created: bool
    execution_created: bool
    task_behavior_changed: bool
    candidate_ordering_changed_by_this_package: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    available_for_future_selected_action_application_review: bool
    requires_teacher_gate_before_selected_action_application: bool
    rollback_available: bool
    rollback_record_id: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PROPOSAL_RECORD_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_selected_action_proposal_record_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.proposal_status not in ALLOWED_PROPOSAL_STATUSES:
            raise ValueError(f"unknown proposal_status: {self.proposal_status}")
        for name in ("candidate_ordering", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SelectedActionProposalRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class SelectedActionProposalRollbackRecord:
    selected_action_proposal_rollback_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_selected_action_proposal_id: str
    source_task_working_memory_id: str
    proposal_created_before_rollback: bool
    proposal_available_after_rollback: bool
    original_proposed_selected_action_candidate_id: str | None
    rollback_proposed_selected_action_candidate_id: str | None
    rollback_available: bool
    rollback_applied: bool
    rollback_reason: str
    rollback_status: str
    rollback_summary: str
    actual_selected_action_changed: bool
    final_action_changed: bool
    direct_command_created: bool
    execution_created: bool
    task_behavior_changed: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PROPOSAL_ROLLBACK_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_selected_action_proposal_rollback_v0"
            )
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
    def from_dict(cls, data: dict[str, object]) -> "SelectedActionProposalRollbackRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class SelectedActionProposalAudit:
    selected_action_proposal_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_selected_action_proposal_gate_id: str | None
    source_selected_action_proposal_id: str | None
    source_selected_action_proposal_rollback_id: str | None
    source_ordering_application_id: str | None
    source_ordering_application_audit_id: str | None
    ordering_application_valid: bool
    ordering_application_audit_passed: bool
    teacher_gate_valid: bool
    proposal_record_valid: bool
    rollback_available: bool
    selected_action_proposal_created: bool
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
        if self.schema_version != PROPOSAL_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_selected_action_proposal_audit_v0"
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
    def from_dict(cls, data: dict[str, object]) -> "SelectedActionProposalAudit":
        return cls(**dict(data))


def build_teacher_gated_selected_action_proposal_gate(
    *,
    ordering_application: AdvisoryReadbackCandidateOrderingApplicationRecord
    | dict[str, object],
    ordering_application_audit: AdvisoryReadbackCandidateOrderingApplicationAudit
    | dict[str, object],
    teacher_gate_status: str = APPROVED_GATE_STATUS,
    teacher_gate_reason: str = "teacher approved proposal creation from ordered top candidate",
    teacher_gate_text: str = "Demo teacher gate approves selected_action proposal only.",
    approval_actor: str = "system_demo",
    approval_actor_role: str = "system_demo",
    approval_source: str = "demo_review",
    approved_for_actual_selected_action: bool = False,
    approved_for_final_action: bool = False,
    approved_for_direct_command: bool = False,
    approved_for_execution: bool = False,
    approved_for_task_behavior_change: bool = False,
    approved_for_memory_layer_write: bool = False,
) -> TeacherGatedSelectedActionProposalGate:
    application = _ordering_application(ordering_application)
    application_audit = _ordering_application_audit(ordering_application_audit)
    candidate_ordering = application.applied_candidate_ordering
    forbidden_authority = any(
        (
            approved_for_actual_selected_action,
            approved_for_final_action,
            approved_for_direct_command,
            approved_for_execution,
            approved_for_task_behavior_change,
            approved_for_memory_layer_write,
        )
    )
    ordering_valid = _ordering_application_valid(application)
    audit_passed = (
        application_audit.audit_status
        == "passed_teacher_gated_candidate_ordering_change"
    )
    if not candidate_ordering:
        status = "blocked_empty_candidate_ordering"
    elif not ordering_valid:
        status = "blocked_invalid_ordering_application"
    elif not audit_passed:
        status = "blocked_invalid_ordering_audit"
    elif forbidden_authority or not _approval_source_valid(
        approval_source,
        approval_actor_role,
        teacher_gate_text,
    ):
        status = "blocked_forbidden_authority_detected"
    else:
        status = teacher_gate_status
    return TeacherGatedSelectedActionProposalGate(
        selected_action_proposal_gate_id=(
            "teacher_gated_selected_action_proposal_gate:"
            f"{application.source_task_initialization_id}"
        ),
        schema_version=PROPOSAL_GATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=application.source_task_working_memory_id,
        source_task_initialization_id=application.source_task_initialization_id,
        source_ordering_application_id=application.ordering_application_id,
        source_ordering_application_audit_id=(
            application_audit.ordering_application_audit_id
        ),
        candidate_ordering=candidate_ordering,
        top_candidate_id=candidate_ordering[0] if candidate_ordering else None,
        proposal_request_summary=(
            "Create a selected_action proposal from the top teacher-gated ordered candidate."
        ),
        proposal_basis="teacher_gated_candidate_ordering_top_candidate",
        teacher_gate_status=status,
        teacher_gate_reason=teacher_gate_reason,
        teacher_gate_text=teacher_gate_text,
        approval_actor=approval_actor,
        approval_actor_role=approval_actor_role,
        approval_source=approval_source,
        approved_for_selected_action_proposal=(
            status == APPROVED_GATE_STATUS
        ),
        approved_for_actual_selected_action=False,
        approved_for_final_action=False,
        approved_for_direct_command=False,
        approved_for_execution=False,
        approved_for_task_behavior_change=False,
        approved_for_memory_layer_write=False,
        requires_proposal_rollback_record=True,
        requires_post_proposal_audit=True,
        requires_teacher_gate_before_selected_action_application=True,
        source_trace_refs=_combined_trace_refs(
            application.source_trace_refs,
            application_audit.source_trace_refs,
        ),
    )


def validate_teacher_gated_selected_action_proposal_gate(
    proposal_gate: TeacherGatedSelectedActionProposalGate | dict[str, object],
) -> dict[str, object]:
    try:
        gate = _proposal_gate(proposal_gate)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_proposal_gate:{error}"]}
    errors: list[str] = []
    if gate.approved_for_selected_action_proposal is not (
        gate.teacher_gate_status == APPROVED_GATE_STATUS
    ):
        errors.append("proposal_approval_mismatch")
    if gate.candidate_ordering and gate.top_candidate_id != gate.candidate_ordering[0]:
        errors.append("top_candidate_mismatch")
    if gate.approval_source == "explicit_teacher_review":
        if gate.approval_actor_role not in {"teacher", "project_owner"}:
            errors.append("invalid_explicit_actor_role")
        if not gate.teacher_gate_text.strip():
            errors.append("teacher_gate_text_required")
    if gate.approval_source == "demo_review" and gate.approval_actor_role != "system_demo":
        errors.append("demo_review_requires_system_demo_role")
    for flag in (
        "approved_for_actual_selected_action",
        "approved_for_final_action",
        "approved_for_direct_command",
        "approved_for_execution",
        "approved_for_task_behavior_change",
        "approved_for_memory_layer_write",
    ):
        if getattr(gate, flag) is not False:
            errors.append(f"{flag}_true")
    for flag in (
        "requires_proposal_rollback_record",
        "requires_post_proposal_audit",
        "requires_teacher_gate_before_selected_action_application",
    ):
        if getattr(gate, flag) is not True:
            errors.append(f"{flag}_false")
    if gate.teacher_gate_status.startswith("blocked_"):
        errors.append(gate.teacher_gate_status)
    return {
        "valid": not errors,
        "error_codes": errors,
        "selected_action_proposal_gate_id": gate.selected_action_proposal_gate_id,
        "teacher_gate_status": gate.teacher_gate_status,
    }


def build_selected_action_proposal_record(
    *,
    proposal_gate: TeacherGatedSelectedActionProposalGate | dict[str, object] | None,
    actual_selected_action_changed: bool = False,
    final_action_changed: bool = False,
    direct_command_created: bool = False,
    execution_created: bool = False,
    task_behavior_changed: bool = False,
    memory_layer_write_performed: bool = False,
    rollback_record_id: str | None = None,
) -> SelectedActionProposalRecord:
    gate = _proposal_gate(proposal_gate) if proposal_gate is not None else _missing_gate()
    forbidden_authority = any(
        (
            actual_selected_action_changed,
            final_action_changed,
            direct_command_created,
            execution_created,
            task_behavior_changed,
            memory_layer_write_performed,
        )
    )
    if forbidden_authority:
        status = "blocked_forbidden_authority_detected"
    elif gate.teacher_gate_status == APPROVED_GATE_STATUS:
        status = PROPOSAL_CREATED_STATUS if gate.candidate_ordering else "blocked_empty_candidate_ordering"
    elif gate.teacher_gate_status == "held_for_more_evidence":
        status = "held_for_more_evidence"
    elif gate.teacher_gate_status == "rejected":
        status = "rejected_by_teacher_gate"
    elif gate.teacher_gate_status == "conflict_detected":
        status = "blocked_conflict_detected"
    elif gate.teacher_gate_status == "blocked_empty_candidate_ordering":
        status = "blocked_empty_candidate_ordering"
    else:
        status = "blocked_invalid_teacher_gate"
    proposal_created = status == PROPOSAL_CREATED_STATUS
    proposed_candidate = gate.candidate_ordering[0] if proposal_created else None
    return SelectedActionProposalRecord(
        selected_action_proposal_id=(
            "selected_action_proposal:"
            f"{gate.source_task_initialization_id}"
        ),
        schema_version=PROPOSAL_RECORD_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=gate.source_task_working_memory_id,
        source_task_initialization_id=gate.source_task_initialization_id,
        source_selected_action_proposal_gate_id=gate.selected_action_proposal_gate_id,
        source_ordering_application_id=gate.source_ordering_application_id,
        source_ordering_application_audit_id=gate.source_ordering_application_audit_id,
        candidate_ordering=gate.candidate_ordering,
        proposed_selected_action_candidate_id=proposed_candidate,
        proposal_rank=0 if proposal_created else None,
        proposal_status=status,
        proposal_summary=_proposal_summary(status),
        proposal_reason=_proposal_reason(status, proposed_candidate),
        selected_action_proposal_created=proposal_created,
        actual_selected_action_changed=actual_selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_created=direct_command_created,
        execution_created=execution_created,
        task_behavior_changed=task_behavior_changed,
        candidate_ordering_changed_by_this_package=False,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=False,
        available_for_future_selected_action_application_review=proposal_created,
        requires_teacher_gate_before_selected_action_application=True,
        rollback_available=proposal_created,
        rollback_record_id=rollback_record_id,
        source_trace_refs=gate.source_trace_refs,
    )


def validate_selected_action_proposal_record(
    proposal_record: SelectedActionProposalRecord | dict[str, object],
) -> dict[str, object]:
    try:
        proposal = _proposal_record(proposal_record)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_proposal_record:{error}"]}
    errors: list[str] = []
    proposal_created = proposal.proposal_status == PROPOSAL_CREATED_STATUS
    if proposal.selected_action_proposal_created is not proposal_created:
        errors.append("proposal_created_flag_mismatch")
    if proposal_created:
        if proposal.proposed_selected_action_candidate_id != proposal.candidate_ordering[0]:
            errors.append("proposed_candidate_not_top_candidate")
        if proposal.proposal_rank != 0:
            errors.append("proposal_rank_not_zero")
    for flag in (
        "actual_selected_action_changed",
        "final_action_changed",
        "direct_command_created",
        "execution_created",
        "task_behavior_changed",
        "candidate_ordering_changed_by_this_package",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(proposal, flag) is not False:
            errors.append(f"{flag}_true")
    if proposal.requires_teacher_gate_before_selected_action_application is not True:
        errors.append("requires_teacher_gate_before_selected_action_application_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "selected_action_proposal_id": proposal.selected_action_proposal_id,
        "proposal_status": proposal.proposal_status,
    }


def build_selected_action_proposal_rollback_record(
    *,
    proposal_record: SelectedActionProposalRecord | dict[str, object],
    rollback_applied: bool = False,
    rollback_reason: str = "rollback data available to withdraw selected_action proposal",
) -> SelectedActionProposalRollbackRecord:
    proposal = _proposal_record(proposal_record)
    valid_proposal = proposal.proposal_status == PROPOSAL_CREATED_STATUS
    rollback_status = (
        "rollback_applied_to_withdraw_proposal"
        if rollback_applied and valid_proposal
        else "rollback_record_created"
        if valid_proposal
        else "blocked_invalid_proposal_record"
    )
    return SelectedActionProposalRollbackRecord(
        selected_action_proposal_rollback_id=(
            "selected_action_proposal_rollback:"
            f"{proposal.selected_action_proposal_id}"
        ),
        schema_version=PROPOSAL_ROLLBACK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_selected_action_proposal_id=proposal.selected_action_proposal_id,
        source_task_working_memory_id=proposal.source_task_working_memory_id,
        proposal_created_before_rollback=valid_proposal,
        proposal_available_after_rollback=not (
            rollback_applied and valid_proposal
        ),
        original_proposed_selected_action_candidate_id=(
            proposal.proposed_selected_action_candidate_id
        ),
        rollback_proposed_selected_action_candidate_id=(
            None if rollback_applied and valid_proposal else proposal.proposed_selected_action_candidate_id
        ),
        rollback_available=valid_proposal,
        rollback_applied=rollback_applied and valid_proposal,
        rollback_reason=rollback_reason,
        rollback_status=rollback_status,
        rollback_summary=_rollback_summary(rollback_status),
        actual_selected_action_changed=False,
        final_action_changed=False,
        direct_command_created=False,
        execution_created=False,
        task_behavior_changed=False,
        memory_layer_write_performed=False,
        source_trace_refs=proposal.source_trace_refs,
    )


def apply_selected_action_proposal_rollback(
    rollback_record: SelectedActionProposalRollbackRecord | dict[str, object],
) -> dict[str, object]:
    rollback = _rollback_record(rollback_record)
    return {
        "rollback_status": "rollback_applied_to_withdraw_proposal"
        if rollback.rollback_available
        else "blocked_invalid_proposal_record",
        "proposal_available_after_rollback": False if rollback.rollback_available else None,
        "proposed_selected_action_candidate_id": None,
        "actual_selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_created": False,
        "execution_created": False,
        "task_behavior_changed": False,
        "memory_layer_write_performed": False,
    }


def build_selected_action_proposal_audit(
    *,
    ordering_application: AdvisoryReadbackCandidateOrderingApplicationRecord
    | dict[str, object]
    | None,
    ordering_application_audit: AdvisoryReadbackCandidateOrderingApplicationAudit
    | dict[str, object]
    | None,
    proposal_gate: TeacherGatedSelectedActionProposalGate | dict[str, object] | None,
    proposal_record: SelectedActionProposalRecord | dict[str, object] | None,
    rollback_record: SelectedActionProposalRollbackRecord | dict[str, object] | None,
) -> SelectedActionProposalAudit:
    application = (
        _ordering_application(ordering_application)
        if ordering_application is not None
        else None
    )
    ordering_audit = (
        _ordering_application_audit(ordering_application_audit)
        if ordering_application_audit is not None
        else None
    )
    gate = _proposal_gate(proposal_gate) if proposal_gate is not None else None
    proposal = (
        _proposal_record(proposal_record) if proposal_record is not None else None
    )
    rollback = (
        _rollback_record(rollback_record) if rollback_record is not None else None
    )
    ordering_valid = bool(application and _ordering_application_valid(application))
    ordering_audit_passed = bool(
        ordering_audit
        and ordering_audit.audit_status
        == "passed_teacher_gated_candidate_ordering_change"
    )
    teacher_gate_valid = bool(
        gate
        and gate.teacher_gate_status
        in {APPROVED_GATE_STATUS, "held_for_more_evidence", "rejected", "conflict_detected"}
        and not validate_teacher_gated_selected_action_proposal_gate(gate)["error_codes"]
    )
    proposal_valid = bool(
        proposal and not validate_selected_action_proposal_record(proposal)["error_codes"]
    )
    rollback_available = bool(rollback and rollback.rollback_available)
    proposal_created = bool(proposal and proposal.selected_action_proposal_created)
    blocked = _audit_blocked_reasons(
        ordering_valid=ordering_valid,
        ordering_audit_passed=ordering_audit_passed,
        teacher_gate_valid=teacher_gate_valid,
        proposal=proposal,
        rollback=rollback,
    )
    status = _audit_status(blocked, proposal_created)
    task_working_memory_id = (
        proposal.source_task_working_memory_id
        if proposal is not None
        else gate.source_task_working_memory_id
        if gate is not None
        else application.source_task_working_memory_id
        if application is not None
        else "unknown"
    )
    return SelectedActionProposalAudit(
        selected_action_proposal_audit_id=(
            "selected_action_proposal_audit:"
            f"{task_working_memory_id}"
        ),
        schema_version=PROPOSAL_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=task_working_memory_id,
        source_selected_action_proposal_gate_id=(
            gate.selected_action_proposal_gate_id if gate is not None else None
        ),
        source_selected_action_proposal_id=(
            proposal.selected_action_proposal_id if proposal is not None else None
        ),
        source_selected_action_proposal_rollback_id=(
            rollback.selected_action_proposal_rollback_id
            if rollback is not None
            else None
        ),
        source_ordering_application_id=(
            application.ordering_application_id if application is not None else None
        ),
        source_ordering_application_audit_id=(
            ordering_audit.ordering_application_audit_id
            if ordering_audit is not None
            else None
        ),
        ordering_application_valid=ordering_valid,
        ordering_application_audit_passed=ordering_audit_passed,
        teacher_gate_valid=teacher_gate_valid,
        proposal_record_valid=proposal_valid,
        rollback_available=rollback_available,
        selected_action_proposal_created=proposal_created,
        actual_selected_action_changed=bool(
            proposal and proposal.actual_selected_action_changed
        ),
        final_action_changed=bool(proposal and proposal.final_action_changed),
        direct_command_created=bool(proposal and proposal.direct_command_created),
        execution_created=bool(proposal and proposal.execution_created),
        task_behavior_changed=bool(proposal and proposal.task_behavior_changed),
        candidate_ordering_changed_by_this_package=bool(
            proposal and proposal.candidate_ordering_changed_by_this_package
        ),
        no_memory_layer_write=not (
            proposal and proposal.memory_layer_write_performed
        ),
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_automatic_learning_approval=True,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=blocked,
        source_trace_refs=_combined_trace_refs(
            application.source_trace_refs if application is not None else (),
            ordering_audit.source_trace_refs if ordering_audit is not None else (),
            gate.source_trace_refs if gate is not None else (),
            proposal.source_trace_refs if proposal is not None else (),
            rollback.source_trace_refs if rollback is not None else (),
        ),
    )


def validate_selected_action_proposal_audit(
    audit: SelectedActionProposalAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _proposal_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_proposal_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed_selected_action_proposal_created":
        errors.append(record.audit_status)
    if record.selected_action_proposal_created and not record.rollback_available:
        errors.append("rollback_missing")
    for flag in (
        "actual_selected_action_changed",
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
        "selected_action_proposal_audit_id": record.selected_action_proposal_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_demo_selected_action_proposal() -> dict[str, object]:
    return _build_proposal_bundle()


def build_demo_selected_action_proposal_audit() -> SelectedActionProposalAudit:
    payload = build_demo_selected_action_proposal()
    return SelectedActionProposalAudit.from_dict(payload["selected_action_proposal_audit"])


def build_demo_selected_action_proposal_rollback() -> SelectedActionProposalRollbackRecord:
    payload = build_demo_selected_action_proposal()
    return SelectedActionProposalRollbackRecord.from_dict(
        payload["selected_action_proposal_rollback"]
    )


def build_demo_blocked_invalid_ordering_application_selected_action_proposal() -> dict[str, object]:
    return _build_proposal_bundle(
        ordering_payload=build_demo_blocked_advisory_readback_candidate_ordering_application(
            "teacher-rejected"
        )
    )


def build_demo_blocked_invalid_ordering_audit_selected_action_proposal() -> dict[str, object]:
    return _build_proposal_bundle(
        ordering_payload=build_demo_blocked_advisory_readback_candidate_ordering_application(
            "missing-rollback"
        )
    )


def build_demo_blocked_missing_teacher_gate_selected_action_proposal() -> dict[str, object]:
    return _build_proposal_bundle(proposal_gate_missing=True)


def build_demo_blocked_teacher_rejected_selected_action_proposal() -> dict[str, object]:
    return _build_proposal_bundle(teacher_gate_status="rejected")


def build_demo_blocked_empty_candidate_ordering_selected_action_proposal() -> dict[str, object]:
    return _build_proposal_bundle(empty_candidate_ordering=True)


def build_demo_blocked_selected_action_mutated_selected_action_proposal() -> dict[str, object]:
    return _build_proposal_bundle(actual_selected_action_changed=True)


def build_demo_blocked_final_action_mutated_selected_action_proposal() -> dict[str, object]:
    return _build_proposal_bundle(final_action_changed=True)


def build_demo_blocked_direct_command_created_selected_action_proposal() -> dict[str, object]:
    return _build_proposal_bundle(direct_command_created=True)


def build_demo_blocked_execution_created_selected_action_proposal() -> dict[str, object]:
    return _build_proposal_bundle(execution_created=True)


def build_demo_blocked_task_behavior_changed_selected_action_proposal() -> dict[str, object]:
    return _build_proposal_bundle(task_behavior_changed=True)


def build_demo_blocked_missing_rollback_selected_action_proposal() -> dict[str, object]:
    return _build_proposal_bundle(rollback_missing=True)


def build_demo_blocked_memory_write_selected_action_proposal() -> dict[str, object]:
    return _build_proposal_bundle(memory_layer_write_performed=True)


def build_demo_blocked_teacher_gated_selected_action_proposal(
    case: str,
) -> dict[str, object]:
    builders = {
        "invalid-ordering-application": (
            build_demo_blocked_invalid_ordering_application_selected_action_proposal
        ),
        "invalid-ordering-audit": (
            build_demo_blocked_invalid_ordering_audit_selected_action_proposal
        ),
        "missing-teacher-gate": (
            build_demo_blocked_missing_teacher_gate_selected_action_proposal
        ),
        "teacher-rejected": build_demo_blocked_teacher_rejected_selected_action_proposal,
        "empty-candidate-ordering": (
            build_demo_blocked_empty_candidate_ordering_selected_action_proposal
        ),
        "selected-action-mutated": (
            build_demo_blocked_selected_action_mutated_selected_action_proposal
        ),
        "final-action-mutated": (
            build_demo_blocked_final_action_mutated_selected_action_proposal
        ),
        "direct-command-created": (
            build_demo_blocked_direct_command_created_selected_action_proposal
        ),
        "execution-created": (
            build_demo_blocked_execution_created_selected_action_proposal
        ),
        "task-behavior-changed": (
            build_demo_blocked_task_behavior_changed_selected_action_proposal
        ),
        "missing-rollback": build_demo_blocked_missing_rollback_selected_action_proposal,
        "memory-write-detected": build_demo_blocked_memory_write_selected_action_proposal,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown selected_action proposal blocked case: {case}") from error


def _build_proposal_bundle(
    *,
    ordering_payload: dict[str, object] | None = None,
    proposal_gate_missing: bool = False,
    teacher_gate_status: str = APPROVED_GATE_STATUS,
    empty_candidate_ordering: bool = False,
    actual_selected_action_changed: bool = False,
    final_action_changed: bool = False,
    direct_command_created: bool = False,
    execution_created: bool = False,
    task_behavior_changed: bool = False,
    memory_layer_write_performed: bool = False,
    rollback_missing: bool = False,
) -> dict[str, object]:
    ordering_payload = ordering_payload or build_demo_teacher_gated_ordering_application()
    ordering_application = AdvisoryReadbackCandidateOrderingApplicationRecord.from_dict(
        ordering_payload["ordering_application"]
    )
    ordering_audit = AdvisoryReadbackCandidateOrderingApplicationAudit.from_dict(
        ordering_payload["ordering_application_audit"]
    )
    if empty_candidate_ordering:
        ordering_application = AdvisoryReadbackCandidateOrderingApplicationRecord.from_dict(
            {
                **ordering_application.to_dict(),
                "applied_candidate_ordering": [],
            }
        )
    proposal_gate = (
        None
        if proposal_gate_missing
        else build_teacher_gated_selected_action_proposal_gate(
            ordering_application=ordering_application,
            ordering_application_audit=ordering_audit,
            teacher_gate_status=teacher_gate_status,
        )
    )
    proposal_record = build_selected_action_proposal_record(
        proposal_gate=proposal_gate,
        actual_selected_action_changed=actual_selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_created=direct_command_created,
        execution_created=execution_created,
        task_behavior_changed=task_behavior_changed,
        memory_layer_write_performed=memory_layer_write_performed,
    )
    rollback = (
        None
        if rollback_missing
        else build_selected_action_proposal_rollback_record(
            proposal_record=proposal_record
        )
    )
    if rollback is not None and proposal_record.proposal_status == PROPOSAL_CREATED_STATUS:
        proposal_record = SelectedActionProposalRecord.from_dict(
            {
                **proposal_record.to_dict(),
                "rollback_available": True,
                "rollback_record_id": rollback.selected_action_proposal_rollback_id,
            }
        )
    audit = build_selected_action_proposal_audit(
        ordering_application=ordering_application,
        ordering_application_audit=ordering_audit,
        proposal_gate=proposal_gate,
        proposal_record=proposal_record,
        rollback_record=rollback,
    )
    return {
        "selected_action_proposal_gate": proposal_gate.to_dict()
        if proposal_gate
        else None,
        "selected_action_proposal": proposal_record.to_dict(),
        "selected_action_proposal_rollback": rollback.to_dict() if rollback else None,
        "selected_action_proposal_audit": audit.to_dict(),
        "selected_action_proposal_gate_validation": (
            validate_teacher_gated_selected_action_proposal_gate(proposal_gate)
            if proposal_gate
            else {"valid": False, "error_codes": ["missing_teacher_gate"]}
        ),
        "selected_action_proposal_validation": validate_selected_action_proposal_record(
            proposal_record
        ),
        "selected_action_proposal_audit_validation": (
            validate_selected_action_proposal_audit(audit)
        ),
        "safe_claim": SAFE_CLAIM,
    }


def _ordering_application_valid(
    application: AdvisoryReadbackCandidateOrderingApplicationRecord,
) -> bool:
    return (
        application.application_status == ORDERING_APPLIED_STATUS
        and application.candidate_ordering_changed
        and not application.selected_action_changed
        and not application.final_action_changed
        and not application.direct_command_changed
        and not application.execution_created
        and not application.task_behavior_changed
        and not application.memory_layer_write_performed
        and validate_advisory_readback_candidate_ordering_application_record(
            application
        )["valid"]
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


def _proposal_summary(status: str) -> str:
    if status == PROPOSAL_CREATED_STATUS:
        return "Selected_action proposal created from top teacher-gated ordered candidate."
    if status == "held_for_more_evidence":
        return "Selected_action proposal held for more evidence."
    if status == "rejected_by_teacher_gate":
        return "Selected_action proposal rejected by teacher gate."
    return f"Selected_action proposal blocked: {status}."


def _proposal_reason(status: str, proposed_candidate: str | None) -> str:
    if status == PROPOSAL_CREATED_STATUS:
        return (
            f"Top ordered candidate {proposed_candidate} is proposed only; actual "
            "selected_action remains unchanged."
        )
    return status


def _rollback_summary(status: str) -> str:
    if status == "rollback_record_created":
        return "Rollback record can withdraw selected_action proposal availability."
    if status == "rollback_applied_to_withdraw_proposal":
        return "Rollback withdrew selected_action proposal availability."
    return "Rollback blocked because proposal record was not successful."


def _audit_blocked_reasons(
    *,
    ordering_valid: bool,
    ordering_audit_passed: bool,
    teacher_gate_valid: bool,
    proposal: SelectedActionProposalRecord | None,
    rollback: SelectedActionProposalRollbackRecord | None,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not ordering_valid:
        reasons.append("invalid_ordering_application")
    if not ordering_audit_passed:
        reasons.append("invalid_ordering_audit")
    if not teacher_gate_valid:
        reasons.append("invalid_teacher_gate")
    if proposal is None:
        reasons.append("invalid_teacher_gate")
        return tuple(dict.fromkeys(reasons))
    if proposal.actual_selected_action_changed:
        reasons.append("actual_selected_action_changed")
    if proposal.final_action_changed:
        reasons.append("final_action_changed")
    if proposal.direct_command_created:
        reasons.append("direct_command_created")
    if proposal.execution_created:
        reasons.append("execution_created")
    if proposal.task_behavior_changed:
        reasons.append("task_behavior_changed")
    if proposal.memory_layer_write_performed:
        reasons.append("memory_layer_write_performed")
    if proposal.selected_action_proposal_created and not (
        rollback is not None and rollback.rollback_available
    ):
        reasons.append("missing_rollback")
    return tuple(dict.fromkeys(reasons))


def _audit_status(
    blocked_reasons: tuple[str, ...],
    proposal_created: bool,
) -> str:
    if "invalid_ordering_application" in blocked_reasons:
        return "blocked_invalid_ordering_application"
    if "invalid_ordering_audit" in blocked_reasons:
        return "blocked_invalid_ordering_application"
    if "invalid_teacher_gate" in blocked_reasons:
        return "blocked_invalid_teacher_gate"
    if "actual_selected_action_changed" in blocked_reasons:
        return "blocked_actual_selected_action_change_detected"
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
    if proposal_created:
        return "passed_selected_action_proposal_created"
    return "passed_no_proposal_created"


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _ordering_application(
    record: AdvisoryReadbackCandidateOrderingApplicationRecord | dict[str, object],
) -> AdvisoryReadbackCandidateOrderingApplicationRecord:
    return (
        record
        if isinstance(record, AdvisoryReadbackCandidateOrderingApplicationRecord)
        else AdvisoryReadbackCandidateOrderingApplicationRecord.from_dict(dict(record))
    )


def _ordering_application_audit(
    record: AdvisoryReadbackCandidateOrderingApplicationAudit | dict[str, object],
) -> AdvisoryReadbackCandidateOrderingApplicationAudit:
    return (
        record
        if isinstance(record, AdvisoryReadbackCandidateOrderingApplicationAudit)
        else AdvisoryReadbackCandidateOrderingApplicationAudit.from_dict(dict(record))
    )


def _proposal_gate(
    record: TeacherGatedSelectedActionProposalGate | dict[str, object],
) -> TeacherGatedSelectedActionProposalGate:
    return (
        record
        if isinstance(record, TeacherGatedSelectedActionProposalGate)
        else TeacherGatedSelectedActionProposalGate.from_dict(dict(record))
    )


def _missing_gate() -> TeacherGatedSelectedActionProposalGate:
    return TeacherGatedSelectedActionProposalGate(
        selected_action_proposal_gate_id="missing:selected_action_proposal_gate",
        schema_version=PROPOSAL_GATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id="unknown",
        source_task_initialization_id="unknown",
        source_ordering_application_id="unknown",
        source_ordering_application_audit_id="unknown",
        candidate_ordering=(),
        top_candidate_id=None,
        proposal_request_summary="missing teacher gate",
        proposal_basis="missing",
        teacher_gate_status="blocked_forbidden_authority_detected",
        teacher_gate_reason="teacher gate missing",
        teacher_gate_text="",
        approval_actor="",
        approval_actor_role="",
        approval_source="",
        approved_for_selected_action_proposal=False,
        approved_for_actual_selected_action=False,
        approved_for_final_action=False,
        approved_for_direct_command=False,
        approved_for_execution=False,
        approved_for_task_behavior_change=False,
        approved_for_memory_layer_write=False,
        requires_proposal_rollback_record=True,
        requires_post_proposal_audit=True,
        requires_teacher_gate_before_selected_action_application=True,
        source_trace_refs=(),
    )


def _proposal_record(
    record: SelectedActionProposalRecord | dict[str, object],
) -> SelectedActionProposalRecord:
    return (
        record
        if isinstance(record, SelectedActionProposalRecord)
        else SelectedActionProposalRecord.from_dict(dict(record))
    )


def _rollback_record(
    record: SelectedActionProposalRollbackRecord | dict[str, object],
) -> SelectedActionProposalRollbackRecord:
    return (
        record
        if isinstance(record, SelectedActionProposalRollbackRecord)
        else SelectedActionProposalRollbackRecord.from_dict(dict(record))
    )


def _proposal_audit(
    record: SelectedActionProposalAudit | dict[str, object],
) -> SelectedActionProposalAudit:
    return (
        record
        if isinstance(record, SelectedActionProposalAudit)
        else SelectedActionProposalAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
