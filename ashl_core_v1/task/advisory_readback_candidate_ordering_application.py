"""Teacher-gated advisory readback influence over candidate ordering."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.task.future_task_working_memory_readback_hint_application import (
    FutureTaskWorkingMemoryInitializationReadbackSnapshot,
    build_demo_future_task_working_memory_readback_hint_application_set,
    validate_future_task_working_memory_initialization_readback_snapshot,
)


SOURCE_ENGINE = "task_engine"
TEACHER_GATE_SCHEMA_VERSION = (
    "task_engine_advisory_readback_candidate_ordering_teacher_gate_v0"
)
APPLICATION_SCHEMA_VERSION = (
    "task_engine_advisory_readback_candidate_ordering_application_v0"
)
ROLLBACK_SCHEMA_VERSION = (
    "task_engine_advisory_readback_candidate_ordering_rollback_v0"
)
AUDIT_SCHEMA_VERSION = (
    "task_engine_advisory_readback_candidate_ordering_application_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Task Engine can apply teacher-gated advisory readback "
    "hint influence to candidate ordering in a newly initialized Task Working "
    "Memory, with rollback and audit, while preserving selected_action, "
    "final_action, direct_command, execution, task behavior, and memory-layer "
    "boundaries unchanged."
)
BLOCKED_CLAIMS = (
    "no_action_choice_from_reviewed_concepts",
    "no_execution_from_reviewed_concepts",
    "no_autonomous_behavior_changing_concept_learning",
    "no_automatic_learning_approval",
    "no_persistent_cross_session_concept_growth",
    "no_core_longterm_archive_anchor_write",
)

ALLOWED_TEACHER_GATE_STATUSES = {
    "approved_for_candidate_ordering_change",
    "held_for_more_evidence",
    "rejected",
    "conflict_detected",
    "blocked_invalid_milestone",
    "blocked_invalid_readback_hints",
    "blocked_invalid_ordering_request",
    "blocked_forbidden_authority_detected",
}
ALLOWED_APPLICATION_STATUSES = {
    "candidate_ordering_changed_by_teacher_gated_readback_hints",
    "held_for_more_evidence",
    "rejected_by_teacher_gate",
    "blocked_conflict_detected",
    "blocked_invalid_teacher_gate",
    "blocked_running_task_mutation_attempt",
    "blocked_forbidden_authority_detected",
    "rollback_applied",
}
ALLOWED_ROLLBACK_STATUSES = {
    "rollback_record_created",
    "rollback_applied_to_restore_baseline_ordering",
    "blocked_invalid_application_record",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_teacher_gated_candidate_ordering_change",
    "passed_no_ordering_change",
    "failed_missing_rollback",
    "blocked_invalid_milestone",
    "blocked_invalid_teacher_gate",
    "blocked_running_task_mutation_detected",
    "blocked_selected_action_change_detected",
    "blocked_final_action_change_detected",
    "blocked_direct_command_detected",
    "blocked_execution_detected",
    "blocked_task_behavior_change_detected",
    "blocked_memory_write_detected",
}

APPROVED_GATE_STATUS = "approved_for_candidate_ordering_change"
APPLIED_STATUS = "candidate_ordering_changed_by_teacher_gated_readback_hints"
DEMO_BASELINE_CANDIDATE_ORDERING = ("step_forward", "observe", "turn_left")


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
class AdvisoryReadbackCandidateOrderingTeacherGate:
    ordering_teacher_gate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str
    source_readback_snapshot_id: str
    source_milestone_audit_id: str
    baseline_candidate_ordering: tuple[str, ...]
    requested_candidate_ordering: tuple[str, ...]
    readback_hint_ids: tuple[str, ...]
    readback_hint_labels: tuple[str, ...]
    readback_hint_kinds: tuple[str, ...]
    teacher_gate_status: str
    teacher_gate_reason: str
    teacher_gate_text: str
    approval_actor: str
    approval_actor_role: str
    approval_source: str
    approved_for_candidate_ordering_change: bool
    approved_for_selected_action_change: bool
    approved_for_final_action_change: bool
    approved_for_direct_command: bool
    approved_for_execution: bool
    approved_for_task_behavior_change: bool
    approved_for_memory_layer_write: bool
    requires_rollback_record: bool
    requires_post_application_audit: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TEACHER_GATE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_advisory_readback_candidate_ordering_teacher_gate_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.teacher_gate_status not in ALLOWED_TEACHER_GATE_STATUSES:
            raise ValueError(f"unknown teacher_gate_status: {self.teacher_gate_status}")
        for name in (
            "baseline_candidate_ordering",
            "requested_candidate_ordering",
            "readback_hint_ids",
            "readback_hint_labels",
            "readback_hint_kinds",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "AdvisoryReadbackCandidateOrderingTeacherGate":
        return cls(**dict(data))


@dataclass(frozen=True)
class AdvisoryReadbackCandidateOrderingApplicationRecord:
    ordering_application_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str
    source_ordering_teacher_gate_id: str
    source_readback_snapshot_id: str
    source_milestone_audit_id: str
    baseline_candidate_ordering: tuple[str, ...]
    applied_candidate_ordering: tuple[str, ...]
    readback_hint_ids: tuple[str, ...]
    readback_hint_labels: tuple[str, ...]
    readback_hint_kinds: tuple[str, ...]
    ordering_change_summary: str
    ordering_change_reason: str
    application_status: str
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created: bool
    task_behavior_changed: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    applied_to_new_task_initialization: bool
    applied_to_running_task: bool
    rollback_available: bool
    rollback_record_id: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != APPLICATION_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_advisory_readback_candidate_ordering_application_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.application_status not in ALLOWED_APPLICATION_STATUSES:
            raise ValueError(f"unknown application_status: {self.application_status}")
        for name in (
            "baseline_candidate_ordering",
            "applied_candidate_ordering",
            "readback_hint_ids",
            "readback_hint_labels",
            "readback_hint_kinds",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "AdvisoryReadbackCandidateOrderingApplicationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class AdvisoryReadbackCandidateOrderingRollbackRecord:
    ordering_rollback_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_ordering_application_id: str
    source_task_working_memory_id: str
    baseline_candidate_ordering: tuple[str, ...]
    applied_candidate_ordering: tuple[str, ...]
    rollback_candidate_ordering: tuple[str, ...]
    rollback_available: bool
    rollback_applied: bool
    rollback_reason: str
    rollback_status: str
    rollback_summary: str
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created: bool
    task_behavior_changed: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ROLLBACK_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_advisory_readback_candidate_ordering_rollback_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.rollback_status not in ALLOWED_ROLLBACK_STATUSES:
            raise ValueError(f"unknown rollback_status: {self.rollback_status}")
        for name in (
            "baseline_candidate_ordering",
            "applied_candidate_ordering",
            "rollback_candidate_ordering",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "AdvisoryReadbackCandidateOrderingRollbackRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class AdvisoryReadbackCandidateOrderingApplicationAudit:
    ordering_application_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_ordering_teacher_gate_id: str | None
    source_ordering_application_id: str | None
    source_ordering_rollback_id: str | None
    milestone_audit_passed: bool
    teacher_gate_valid: bool
    readback_hints_valid: bool
    candidate_ordering_change_allowed: bool
    candidate_ordering_changed: bool
    rollback_available: bool
    new_task_initialization_only: bool
    no_running_task_mutation: bool
    no_selected_action_change: bool
    no_final_action_change: bool
    no_direct_command_change: bool
    no_action_execution: bool
    no_task_behavior_change: bool
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
                "schema_version must be task_engine_advisory_readback_candidate_ordering_application_audit_v0"
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
    ) -> "AdvisoryReadbackCandidateOrderingApplicationAudit":
        return cls(**dict(data))


def compute_advisory_readback_ordering(
    baseline_candidate_ordering: tuple[str, ...] | list[str],
    readback_hints: tuple[dict[str, object], ...] | list[dict[str, object]],
) -> tuple[str, ...]:
    baseline = _tuple_of_str("baseline_candidate_ordering", baseline_candidate_ordering)
    scores = {candidate_id: 0 for candidate_id in baseline}
    for hint in readback_hints:
        hint_kind = str(hint.get("hint_kind", ""))
        if hint_kind == "observe_before_retry":
            _promote(scores, ("observe", "verify"))
        elif hint_kind == "avoid_repeated_failure":
            _demote(scores, ("step_forward", "direct_retry", "retry"))
        elif hint_kind == "verify_scope":
            _promote(scores, ("observe", "verify"))
            _demote(scores, ("step_forward", "direct_retry"))
        elif hint_kind == "verify_expected_actual":
            _promote(scores, ("observe", "verify", "check"))
            _demote(scores, ("step_forward", "direct_retry"))
        elif hint_kind == "use_known_success_path":
            _promote(scores, ("known_success", "success_path"))
        elif hint_kind == "gather_context":
            _promote(scores, ("observe", "scan", "context"))
    return tuple(
        candidate_id
        for _, candidate_id in sorted(
            enumerate(baseline),
            key=lambda item: (-scores[item[1]], item[0]),
        )
    )


def build_advisory_readback_candidate_ordering_teacher_gate(
    *,
    milestone_audit: ReviewedConceptReadbackLoopMilestoneAudit | dict[str, object],
    readback_snapshot: FutureTaskWorkingMemoryInitializationReadbackSnapshot
    | dict[str, object],
    baseline_candidate_ordering: tuple[str, ...] | list[str],
    requested_candidate_ordering: tuple[str, ...] | list[str] | None = None,
    teacher_gate_status: str = APPROVED_GATE_STATUS,
    teacher_gate_reason: str = "teacher approved bounded advisory ordering influence",
    teacher_gate_text: str = "Demo teacher gate approves candidate ordering only.",
    approval_actor: str = "system_demo",
    approval_actor_role: str = "system_demo",
    approval_source: str = "demo_review",
    approved_for_selected_action_change: bool = False,
    approved_for_final_action_change: bool = False,
    approved_for_direct_command: bool = False,
    approved_for_execution: bool = False,
    approved_for_task_behavior_change: bool = False,
    approved_for_memory_layer_write: bool = False,
) -> AdvisoryReadbackCandidateOrderingTeacherGate:
    milestone = _milestone_audit(milestone_audit)
    snapshot = _readback_snapshot(readback_snapshot)
    baseline = _tuple_of_str("baseline_candidate_ordering", baseline_candidate_ordering)
    hints = tuple(dict(hint) for hint in snapshot.readback_hints)
    requested = (
        _tuple_of_str("requested_candidate_ordering", requested_candidate_ordering)
        if requested_candidate_ordering is not None
        else compute_advisory_readback_ordering(baseline, hints)
    )
    forbidden_authority = any(
        (
            approved_for_selected_action_change,
            approved_for_final_action_change,
            approved_for_direct_command,
            approved_for_execution,
            approved_for_task_behavior_change,
            approved_for_memory_layer_write,
        )
    )
    milestone_passed = (
        milestone.milestone_status
        == "passed_reviewed_concept_advisory_readback_loop_v0"
    )
    hints_valid = _readback_hints_valid(snapshot)
    ordering_valid = _candidate_set_preserved(baseline, requested)
    if not milestone_passed:
        status = "blocked_invalid_milestone"
    elif not hints_valid:
        status = "blocked_invalid_readback_hints"
    elif not ordering_valid:
        status = "blocked_invalid_ordering_request"
    elif forbidden_authority or not _approval_source_valid(
        approval_source,
        approval_actor_role,
        teacher_gate_text,
    ):
        status = "blocked_forbidden_authority_detected"
    else:
        status = teacher_gate_status
    approved_for_ordering = status == APPROVED_GATE_STATUS
    return AdvisoryReadbackCandidateOrderingTeacherGate(
        ordering_teacher_gate_id=(
            "advisory_readback_candidate_ordering_teacher_gate:"
            f"{snapshot.target_task_initialization_id}"
        ),
        schema_version=TEACHER_GATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=snapshot.target_task_working_memory_id,
        source_task_initialization_id=snapshot.target_task_initialization_id,
        source_readback_snapshot_id=snapshot.readback_snapshot_id,
        source_milestone_audit_id=milestone.milestone_audit_id,
        baseline_candidate_ordering=baseline,
        requested_candidate_ordering=requested,
        readback_hint_ids=snapshot.readback_hint_ids,
        readback_hint_labels=snapshot.readback_hint_labels,
        readback_hint_kinds=tuple(str(hint.get("hint_kind", "")) for hint in hints),
        teacher_gate_status=status,
        teacher_gate_reason=teacher_gate_reason,
        teacher_gate_text=teacher_gate_text,
        approval_actor=approval_actor,
        approval_actor_role=approval_actor_role,
        approval_source=approval_source,
        approved_for_candidate_ordering_change=approved_for_ordering,
        approved_for_selected_action_change=False,
        approved_for_final_action_change=False,
        approved_for_direct_command=False,
        approved_for_execution=False,
        approved_for_task_behavior_change=False,
        approved_for_memory_layer_write=False,
        requires_rollback_record=True,
        requires_post_application_audit=True,
        source_trace_refs=_combined_trace_refs(
            milestone.source_trace_refs,
            snapshot.source_trace_refs,
        ),
    )


def validate_advisory_readback_candidate_ordering_teacher_gate(
    teacher_gate: AdvisoryReadbackCandidateOrderingTeacherGate | dict[str, object],
) -> dict[str, object]:
    try:
        gate = _teacher_gate(teacher_gate)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_teacher_gate:{error}"]}
    errors: list[str] = []
    if gate.approved_for_candidate_ordering_change is not (
        gate.teacher_gate_status == APPROVED_GATE_STATUS
    ):
        errors.append("candidate_ordering_approval_mismatch")
    if not _candidate_set_preserved(
        gate.baseline_candidate_ordering,
        gate.requested_candidate_ordering,
    ):
        errors.append("candidate_id_set_changed")
    if gate.approval_source == "explicit_teacher_review":
        if gate.approval_actor_role not in {"teacher", "project_owner"}:
            errors.append("invalid_explicit_actor_role")
        if not gate.teacher_gate_text.strip():
            errors.append("teacher_gate_text_required")
    if gate.approval_source == "demo_review" and gate.approval_actor_role != "system_demo":
        errors.append("demo_review_requires_system_demo_role")
    for flag in (
        "approved_for_selected_action_change",
        "approved_for_final_action_change",
        "approved_for_direct_command",
        "approved_for_execution",
        "approved_for_task_behavior_change",
        "approved_for_memory_layer_write",
    ):
        if getattr(gate, flag) is not False:
            errors.append(f"{flag}_true")
    for flag in ("requires_rollback_record", "requires_post_application_audit"):
        if getattr(gate, flag) is not True:
            errors.append(f"{flag}_false")
    if gate.teacher_gate_status.startswith("blocked_"):
        errors.append(gate.teacher_gate_status)
    return {
        "valid": not errors,
        "error_codes": errors,
        "ordering_teacher_gate_id": gate.ordering_teacher_gate_id,
        "teacher_gate_status": gate.teacher_gate_status,
    }


def apply_teacher_gated_advisory_readback_candidate_ordering(
    *,
    teacher_gate: AdvisoryReadbackCandidateOrderingTeacherGate | dict[str, object] | None,
    target_task_is_running: bool = False,
    selected_action_changed: bool = False,
    final_action_changed: bool = False,
    direct_command_changed: bool = False,
    execution_created: bool = False,
    task_behavior_changed: bool = False,
    memory_layer_write_performed: bool = False,
    rollback_record_id: str | None = None,
) -> AdvisoryReadbackCandidateOrderingApplicationRecord:
    if teacher_gate is None:
        gate = _missing_teacher_gate()
    else:
        gate = _teacher_gate(teacher_gate)
    forbidden_authority = any(
        (
            selected_action_changed,
            final_action_changed,
            direct_command_changed,
            execution_created,
            task_behavior_changed,
            memory_layer_write_performed,
        )
    )
    if target_task_is_running:
        status = "blocked_running_task_mutation_attempt"
    elif forbidden_authority:
        status = "blocked_forbidden_authority_detected"
    elif gate.teacher_gate_status == APPROVED_GATE_STATUS:
        status = APPLIED_STATUS
    elif gate.teacher_gate_status == "held_for_more_evidence":
        status = "held_for_more_evidence"
    elif gate.teacher_gate_status == "rejected":
        status = "rejected_by_teacher_gate"
    elif gate.teacher_gate_status == "conflict_detected":
        status = "blocked_conflict_detected"
    else:
        status = "blocked_invalid_teacher_gate"
    applied = status == APPLIED_STATUS
    applied_ordering = (
        gate.requested_candidate_ordering if applied else gate.baseline_candidate_ordering
    )
    return AdvisoryReadbackCandidateOrderingApplicationRecord(
        ordering_application_id=(
            "advisory_readback_candidate_ordering_application:"
            f"{gate.source_task_initialization_id}"
        ),
        schema_version=APPLICATION_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=gate.source_task_working_memory_id,
        source_task_initialization_id=gate.source_task_initialization_id,
        source_ordering_teacher_gate_id=gate.ordering_teacher_gate_id,
        source_readback_snapshot_id=gate.source_readback_snapshot_id,
        source_milestone_audit_id=gate.source_milestone_audit_id,
        baseline_candidate_ordering=gate.baseline_candidate_ordering,
        applied_candidate_ordering=applied_ordering,
        readback_hint_ids=gate.readback_hint_ids,
        readback_hint_labels=gate.readback_hint_labels,
        readback_hint_kinds=gate.readback_hint_kinds,
        ordering_change_summary=_application_summary(status),
        ordering_change_reason=_application_reason(status),
        application_status=status,
        candidate_ordering_changed=applied,
        selected_action_changed=selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_changed=direct_command_changed,
        execution_created=execution_created,
        task_behavior_changed=task_behavior_changed,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=False,
        applied_to_new_task_initialization=applied,
        applied_to_running_task=target_task_is_running,
        rollback_available=applied,
        rollback_record_id=rollback_record_id,
        source_trace_refs=gate.source_trace_refs,
    )


def validate_advisory_readback_candidate_ordering_application_record(
    record: AdvisoryReadbackCandidateOrderingApplicationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        application = _application_record(record)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_application_record:{error}"]}
    errors: list[str] = []
    applied = application.application_status == APPLIED_STATUS
    if application.candidate_ordering_changed is not applied:
        errors.append("candidate_ordering_changed_mismatch")
    if applied:
        if not _candidate_set_preserved(
            application.baseline_candidate_ordering,
            application.applied_candidate_ordering,
        ):
            errors.append("candidate_id_set_changed")
        if application.applied_to_new_task_initialization is not True:
            errors.append("not_applied_to_new_task_initialization")
    for flag in (
        "selected_action_changed",
        "final_action_changed",
        "direct_command_changed",
        "execution_created",
        "task_behavior_changed",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
        "applied_to_running_task",
    ):
        if getattr(application, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "ordering_application_id": application.ordering_application_id,
        "application_status": application.application_status,
    }


def build_advisory_readback_candidate_ordering_rollback_record(
    *,
    application_record: AdvisoryReadbackCandidateOrderingApplicationRecord
    | dict[str, object],
    rollback_applied: bool = False,
    rollback_reason: str = "rollback data available to restore baseline ordering",
) -> AdvisoryReadbackCandidateOrderingRollbackRecord:
    application = _application_record(application_record)
    valid_application = application.application_status == APPLIED_STATUS
    rollback_status = (
        "rollback_applied_to_restore_baseline_ordering"
        if rollback_applied and valid_application
        else "rollback_record_created"
        if valid_application
        else "blocked_invalid_application_record"
    )
    return AdvisoryReadbackCandidateOrderingRollbackRecord(
        ordering_rollback_id=(
            "advisory_readback_candidate_ordering_rollback:"
            f"{application.ordering_application_id}"
        ),
        schema_version=ROLLBACK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_ordering_application_id=application.ordering_application_id,
        source_task_working_memory_id=application.source_task_working_memory_id,
        baseline_candidate_ordering=application.baseline_candidate_ordering,
        applied_candidate_ordering=application.applied_candidate_ordering,
        rollback_candidate_ordering=application.baseline_candidate_ordering,
        rollback_available=valid_application,
        rollback_applied=rollback_applied and valid_application,
        rollback_reason=rollback_reason,
        rollback_status=rollback_status,
        rollback_summary=_rollback_summary(rollback_status),
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_changed=False,
        execution_created=False,
        task_behavior_changed=False,
        memory_layer_write_performed=False,
        source_trace_refs=application.source_trace_refs,
    )


def apply_advisory_readback_candidate_ordering_rollback(
    rollback_record: AdvisoryReadbackCandidateOrderingRollbackRecord | dict[str, object],
) -> dict[str, object]:
    rollback = _rollback_record(rollback_record)
    return {
        "rollback_status": "rollback_applied_to_restore_baseline_ordering"
        if rollback.rollback_available
        else "blocked_invalid_application_record",
        "candidate_ordering": rollback.rollback_candidate_ordering,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "task_behavior_changed": False,
        "memory_layer_write_performed": False,
    }


def build_advisory_readback_candidate_ordering_application_audit(
    *,
    milestone_audit: ReviewedConceptReadbackLoopMilestoneAudit | dict[str, object],
    teacher_gate: AdvisoryReadbackCandidateOrderingTeacherGate | dict[str, object] | None,
    application_record: AdvisoryReadbackCandidateOrderingApplicationRecord
    | dict[str, object]
    | None,
    rollback_record: AdvisoryReadbackCandidateOrderingRollbackRecord
    | dict[str, object]
    | None,
) -> AdvisoryReadbackCandidateOrderingApplicationAudit:
    milestone = _milestone_audit(milestone_audit)
    gate = _teacher_gate(teacher_gate) if teacher_gate is not None else None
    application = (
        _application_record(application_record)
        if application_record is not None
        else None
    )
    rollback = _rollback_record(rollback_record) if rollback_record is not None else None
    milestone_passed = (
        milestone.milestone_status
        == "passed_reviewed_concept_advisory_readback_loop_v0"
    )
    gate_valid = (
        gate is not None
        and gate.teacher_gate_status in {
            APPROVED_GATE_STATUS,
            "held_for_more_evidence",
            "rejected",
            "conflict_detected",
        }
        and not validate_advisory_readback_candidate_ordering_teacher_gate(gate)[
            "error_codes"
        ]
    )
    app_present = application is not None
    rollback_available = rollback is not None and rollback.rollback_available
    candidate_ordering_changed = bool(
        application and application.candidate_ordering_changed
    )
    blocked = _audit_blocked_reasons(
        milestone_passed=milestone_passed,
        gate_valid=gate_valid,
        application=application,
        rollback=rollback,
    )
    status = _audit_status(blocked, candidate_ordering_changed)
    task_working_memory_id = (
        application.source_task_working_memory_id
        if application is not None
        else gate.source_task_working_memory_id
        if gate is not None
        else "unknown"
    )
    source_refs = _combined_trace_refs(
        milestone.source_trace_refs,
        gate.source_trace_refs if gate is not None else (),
        application.source_trace_refs if application is not None else (),
        rollback.source_trace_refs if rollback is not None else (),
    )
    return AdvisoryReadbackCandidateOrderingApplicationAudit(
        ordering_application_audit_id=(
            "advisory_readback_candidate_ordering_application_audit:"
            f"{task_working_memory_id}"
        ),
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=task_working_memory_id,
        source_ordering_teacher_gate_id=(
            gate.ordering_teacher_gate_id if gate is not None else None
        ),
        source_ordering_application_id=(
            application.ordering_application_id if application is not None else None
        ),
        source_ordering_rollback_id=(
            rollback.ordering_rollback_id if rollback is not None else None
        ),
        milestone_audit_passed=milestone_passed,
        teacher_gate_valid=gate_valid,
        readback_hints_valid=gate is not None and bool(gate.readback_hint_ids),
        candidate_ordering_change_allowed=gate is not None
        and gate.teacher_gate_status == APPROVED_GATE_STATUS,
        candidate_ordering_changed=candidate_ordering_changed,
        rollback_available=rollback_available,
        new_task_initialization_only=not (
            application and application.applied_to_running_task
        ),
        no_running_task_mutation=not (
            application and application.applied_to_running_task
        ),
        no_selected_action_change=not (
            application and application.selected_action_changed
        ),
        no_final_action_change=not (
            application and application.final_action_changed
        ),
        no_direct_command_change=not (
            application and application.direct_command_changed
        ),
        no_action_execution=not (application and application.execution_created),
        no_task_behavior_change=not (
            application and application.task_behavior_changed
        ),
        no_memory_layer_write=not (
            application and application.memory_layer_write_performed
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
        source_trace_refs=source_refs,
    )


def validate_advisory_readback_candidate_ordering_application_audit(
    audit: AdvisoryReadbackCandidateOrderingApplicationAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _application_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_application_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed_teacher_gated_candidate_ordering_change":
        errors.append(record.audit_status)
    if record.candidate_ordering_changed and not record.rollback_available:
        errors.append("rollback_missing")
    for flag in (
        "new_task_initialization_only",
        "no_running_task_mutation",
        "no_selected_action_change",
        "no_final_action_change",
        "no_direct_command_change",
        "no_action_execution",
        "no_task_behavior_change",
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
        "ordering_application_audit_id": record.ordering_application_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_demo_teacher_gated_ordering_application() -> dict[str, object]:
    return _build_ordering_bundle()


def build_demo_teacher_gated_ordering_application_audit() -> (
    AdvisoryReadbackCandidateOrderingApplicationAudit
):
    payload = build_demo_teacher_gated_ordering_application()
    return AdvisoryReadbackCandidateOrderingApplicationAudit.from_dict(
        payload["ordering_application_audit"]
    )


def build_demo_ordering_rollback() -> AdvisoryReadbackCandidateOrderingRollbackRecord:
    payload = build_demo_teacher_gated_ordering_application()
    return AdvisoryReadbackCandidateOrderingRollbackRecord.from_dict(
        payload["ordering_rollback"]
    )


def build_demo_blocked_invalid_milestone_ordering_application() -> dict[str, object]:
    from ashl_core_v1.audit.reviewed_concept_readback_loop_milestone_audit import (
        build_demo_blocked_missing_influence_audit_milestone,
    )

    return _build_ordering_bundle(
        milestone_payload=build_demo_blocked_missing_influence_audit_milestone(),
    )


def build_demo_blocked_missing_teacher_gate_ordering_application() -> dict[str, object]:
    return _build_ordering_bundle(teacher_gate_missing=True)


def build_demo_blocked_teacher_rejected_ordering_application() -> dict[str, object]:
    return _build_ordering_bundle(teacher_gate_status="rejected")


def build_demo_blocked_running_task_mutation_ordering_application() -> dict[str, object]:
    return _build_ordering_bundle(target_task_is_running=True)


def build_demo_blocked_candidate_deleted_ordering_application() -> dict[str, object]:
    return _build_ordering_bundle(requested_candidate_ordering=("observe", "turn_left"))


def build_demo_blocked_candidate_created_ordering_application() -> dict[str, object]:
    return _build_ordering_bundle(
        requested_candidate_ordering=(
            "observe",
            "turn_left",
            "step_forward",
            "new_candidate",
        )
    )


def build_demo_blocked_selected_action_changed_ordering_application() -> dict[str, object]:
    return _build_ordering_bundle(selected_action_changed=True)


def build_demo_blocked_final_action_changed_ordering_application() -> dict[str, object]:
    return _build_ordering_bundle(final_action_changed=True)


def build_demo_blocked_direct_command_created_ordering_application() -> dict[str, object]:
    return _build_ordering_bundle(direct_command_changed=True)


def build_demo_blocked_execution_created_ordering_application() -> dict[str, object]:
    return _build_ordering_bundle(execution_created=True)


def build_demo_blocked_task_behavior_changed_ordering_application() -> dict[str, object]:
    return _build_ordering_bundle(task_behavior_changed=True)


def build_demo_blocked_missing_rollback_ordering_application() -> dict[str, object]:
    return _build_ordering_bundle(rollback_missing=True)


def build_demo_blocked_memory_write_ordering_application() -> dict[str, object]:
    return _build_ordering_bundle(memory_layer_write_performed=True)


def build_demo_blocked_advisory_readback_candidate_ordering_application(
    case: str,
) -> dict[str, object]:
    builders = {
        "invalid-milestone": build_demo_blocked_invalid_milestone_ordering_application,
        "missing-teacher-gate": (
            build_demo_blocked_missing_teacher_gate_ordering_application
        ),
        "teacher-rejected": build_demo_blocked_teacher_rejected_ordering_application,
        "running-task-mutation": (
            build_demo_blocked_running_task_mutation_ordering_application
        ),
        "candidate-deleted": build_demo_blocked_candidate_deleted_ordering_application,
        "candidate-created": build_demo_blocked_candidate_created_ordering_application,
        "selected-action-changed": (
            build_demo_blocked_selected_action_changed_ordering_application
        ),
        "final-action-changed": (
            build_demo_blocked_final_action_changed_ordering_application
        ),
        "direct-command-created": (
            build_demo_blocked_direct_command_created_ordering_application
        ),
        "execution-created": build_demo_blocked_execution_created_ordering_application,
        "task-behavior-changed": (
            build_demo_blocked_task_behavior_changed_ordering_application
        ),
        "missing-rollback": build_demo_blocked_missing_rollback_ordering_application,
        "memory-write-detected": build_demo_blocked_memory_write_ordering_application,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown advisory ordering blocked case: {case}") from error


def _build_ordering_bundle(
    *,
    milestone_payload: dict[str, object] | None = None,
    teacher_gate_missing: bool = False,
    teacher_gate_status: str = APPROVED_GATE_STATUS,
    requested_candidate_ordering: tuple[str, ...] | None = None,
    target_task_is_running: bool = False,
    selected_action_changed: bool = False,
    final_action_changed: bool = False,
    direct_command_changed: bool = False,
    execution_created: bool = False,
    task_behavior_changed: bool = False,
    memory_layer_write_performed: bool = False,
    rollback_missing: bool = False,
) -> dict[str, object]:
    from ashl_core_v1.audit.reviewed_concept_readback_loop_milestone_audit import (
        ReviewedConceptReadbackLoopMilestoneAudit,
        build_demo_reviewed_concept_readback_loop_milestone,
    )

    milestone_payload = milestone_payload or build_demo_reviewed_concept_readback_loop_milestone()
    future_payload = build_demo_future_task_working_memory_readback_hint_application_set()
    milestone = ReviewedConceptReadbackLoopMilestoneAudit.from_dict(
        milestone_payload["milestone_audit"]
    )
    snapshot = FutureTaskWorkingMemoryInitializationReadbackSnapshot.from_dict(
        future_payload["future_task_working_memory_initialization_readback_snapshot"]
    )
    teacher_gate = (
        None
        if teacher_gate_missing
        else build_advisory_readback_candidate_ordering_teacher_gate(
            milestone_audit=milestone,
            readback_snapshot=snapshot,
            baseline_candidate_ordering=DEMO_BASELINE_CANDIDATE_ORDERING,
            requested_candidate_ordering=requested_candidate_ordering,
            teacher_gate_status=teacher_gate_status,
        )
    )
    application = apply_teacher_gated_advisory_readback_candidate_ordering(
        teacher_gate=teacher_gate,
        target_task_is_running=target_task_is_running,
        selected_action_changed=selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_changed=direct_command_changed,
        execution_created=execution_created,
        task_behavior_changed=task_behavior_changed,
        memory_layer_write_performed=memory_layer_write_performed,
    )
    rollback = (
        None
        if rollback_missing
        else build_advisory_readback_candidate_ordering_rollback_record(
            application_record=application
        )
    )
    if rollback is not None and application.application_status == APPLIED_STATUS:
        application = AdvisoryReadbackCandidateOrderingApplicationRecord.from_dict(
            {
                **application.to_dict(),
                "rollback_available": True,
                "rollback_record_id": rollback.ordering_rollback_id,
            }
        )
    audit = build_advisory_readback_candidate_ordering_application_audit(
        milestone_audit=milestone,
        teacher_gate=teacher_gate,
        application_record=application,
        rollback_record=rollback,
    )
    task_working_memory_after = _task_working_memory_after_application(
        future_payload["initialized_future_task_working_memory"],
        application,
    )
    return {
        "ordering_teacher_gate": teacher_gate.to_dict() if teacher_gate else None,
        "ordering_application": application.to_dict(),
        "ordering_rollback": rollback.to_dict() if rollback else None,
        "ordering_application_audit": audit.to_dict(),
        "task_working_memory_after_application": task_working_memory_after,
        "ordering_teacher_gate_validation": (
            validate_advisory_readback_candidate_ordering_teacher_gate(teacher_gate)
            if teacher_gate
            else {"valid": False, "error_codes": ["missing_teacher_gate"]}
        ),
        "ordering_application_validation": (
            validate_advisory_readback_candidate_ordering_application_record(
                application
            )
        ),
        "ordering_application_audit_validation": (
            validate_advisory_readback_candidate_ordering_application_audit(audit)
        ),
        "safe_claim": SAFE_CLAIM,
    }


def _task_working_memory_after_application(
    initialized_payload: dict[str, object],
    application: AdvisoryReadbackCandidateOrderingApplicationRecord,
) -> dict[str, object]:
    task_working_memory = dict(initialized_payload.get("task_working_memory", {}))
    if application.application_status == APPLIED_STATUS:
        task_working_memory["candidate_ordering"] = list(
            application.applied_candidate_ordering
        )
        task_working_memory["candidate_ordering_source"] = (
            "teacher_gated_advisory_readback_hints"
        )
        task_working_memory["candidate_ordering_changed"] = True
    else:
        task_working_memory["candidate_ordering"] = list(
            application.baseline_candidate_ordering
        )
        task_working_memory["candidate_ordering_changed"] = False
    task_working_memory["selected_action"] = None
    task_working_memory["final_action"] = None
    task_working_memory["direct_command"] = None
    task_working_memory["execution"] = None
    task_working_memory["task_behavior_changed"] = False
    task_working_memory["memory_layer_write_performed"] = False
    return {
        **dict(initialized_payload),
        "task_working_memory": task_working_memory,
        "candidate_ordering_changed": application.candidate_ordering_changed,
        "selected_action_changed": False,
        "final_action_changed": False,
        "direct_command_changed": False,
        "execution_created": False,
        "task_behavior_changed": False,
        "memory_layer_write_performed": False,
    }


def _promote(scores: dict[str, int], tokens: tuple[str, ...]) -> None:
    for candidate_id in scores:
        if any(token in candidate_id for token in tokens):
            scores[candidate_id] += 10


def _demote(scores: dict[str, int], tokens: tuple[str, ...]) -> None:
    for candidate_id in scores:
        if any(token in candidate_id for token in tokens):
            scores[candidate_id] -= 10


def _readback_hints_valid(
    snapshot: FutureTaskWorkingMemoryInitializationReadbackSnapshot,
) -> bool:
    if snapshot.snapshot_status != "snapshot_created_with_advisory_readback_hints":
        return False
    if not (
        snapshot.advisory_only
        and snapshot.single_task_lifetime
        and snapshot.future_task_initialization_only
    ):
        return False
    if not snapshot.readback_hints:
        return False
    for hint in snapshot.readback_hints:
        if hint.get("visibility") != "advisory_only":
            return False
        if hint.get("lifetime") != "single_task":
            return False
        if not hint.get("hint_kind") or not hint.get("hint_label"):
            return False
    return validate_future_task_working_memory_initialization_readback_snapshot(
        snapshot
    )["valid"]


def _candidate_set_preserved(
    baseline: tuple[str, ...] | list[str],
    candidate_ordering: tuple[str, ...] | list[str],
) -> bool:
    return sorted(tuple(baseline)) == sorted(tuple(candidate_ordering))


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


def _application_summary(status: str) -> str:
    if status == APPLIED_STATUS:
        return "Teacher-gated advisory readback hints changed candidate ordering."
    if status == "held_for_more_evidence":
        return "Teacher gate held advisory ordering influence for more evidence."
    if status == "rejected_by_teacher_gate":
        return "Teacher gate rejected advisory ordering influence."
    return f"Candidate ordering application blocked: {status}."


def _application_reason(status: str) -> str:
    if status == APPLIED_STATUS:
        return (
            "observe_before_retry promotes observe; avoid_repeated_failure demotes "
            "step_forward; no action path authority is granted."
        )
    return status


def _rollback_summary(status: str) -> str:
    if status == "rollback_record_created":
        return "Rollback record can restore baseline candidate ordering."
    if status == "rollback_applied_to_restore_baseline_ordering":
        return "Rollback restored baseline candidate ordering."
    return "Rollback blocked because application record was not a successful ordering change."


def _audit_blocked_reasons(
    *,
    milestone_passed: bool,
    gate_valid: bool,
    application: AdvisoryReadbackCandidateOrderingApplicationRecord | None,
    rollback: AdvisoryReadbackCandidateOrderingRollbackRecord | None,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not milestone_passed:
        reasons.append("invalid_milestone")
    if not gate_valid:
        reasons.append("invalid_teacher_gate")
    if application is None:
        reasons.append("invalid_teacher_gate")
        return tuple(dict.fromkeys(reasons))
    if application.applied_to_running_task:
        reasons.append("running_task_mutation")
    if application.selected_action_changed:
        reasons.append("selected_action_changed")
    if application.final_action_changed:
        reasons.append("final_action_changed")
    if application.direct_command_changed:
        reasons.append("direct_command_changed")
    if application.execution_created:
        reasons.append("execution_created")
    if application.task_behavior_changed:
        reasons.append("task_behavior_changed")
    if application.memory_layer_write_performed:
        reasons.append("memory_layer_write_performed")
    if application.candidate_ordering_changed and not (
        rollback is not None and rollback.rollback_available
    ):
        reasons.append("missing_rollback")
    return tuple(dict.fromkeys(reasons))


def _audit_status(
    blocked_reasons: tuple[str, ...],
    candidate_ordering_changed: bool,
) -> str:
    if "invalid_milestone" in blocked_reasons:
        return "blocked_invalid_milestone"
    if "invalid_teacher_gate" in blocked_reasons:
        return "blocked_invalid_teacher_gate"
    if "running_task_mutation" in blocked_reasons:
        return "blocked_running_task_mutation_detected"
    if "selected_action_changed" in blocked_reasons:
        return "blocked_selected_action_change_detected"
    if "final_action_changed" in blocked_reasons:
        return "blocked_final_action_change_detected"
    if "direct_command_changed" in blocked_reasons:
        return "blocked_direct_command_detected"
    if "execution_created" in blocked_reasons:
        return "blocked_execution_detected"
    if "task_behavior_changed" in blocked_reasons:
        return "blocked_task_behavior_change_detected"
    if "memory_layer_write_performed" in blocked_reasons:
        return "blocked_memory_write_detected"
    if "missing_rollback" in blocked_reasons:
        return "failed_missing_rollback"
    if candidate_ordering_changed:
        return "passed_teacher_gated_candidate_ordering_change"
    return "passed_no_ordering_change"


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _teacher_gate(
    record: AdvisoryReadbackCandidateOrderingTeacherGate | dict[str, object],
) -> AdvisoryReadbackCandidateOrderingTeacherGate:
    return (
        record
        if isinstance(record, AdvisoryReadbackCandidateOrderingTeacherGate)
        else AdvisoryReadbackCandidateOrderingTeacherGate.from_dict(dict(record))
    )


def _missing_teacher_gate() -> AdvisoryReadbackCandidateOrderingTeacherGate:
    return AdvisoryReadbackCandidateOrderingTeacherGate(
        ordering_teacher_gate_id="missing:ordering_teacher_gate",
        schema_version=TEACHER_GATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id="unknown",
        source_task_initialization_id="unknown",
        source_readback_snapshot_id="unknown",
        source_milestone_audit_id="unknown",
        baseline_candidate_ordering=(),
        requested_candidate_ordering=(),
        readback_hint_ids=(),
        readback_hint_labels=(),
        readback_hint_kinds=(),
        teacher_gate_status="blocked_forbidden_authority_detected",
        teacher_gate_reason="teacher gate missing",
        teacher_gate_text="",
        approval_actor="",
        approval_actor_role="",
        approval_source="",
        approved_for_candidate_ordering_change=False,
        approved_for_selected_action_change=False,
        approved_for_final_action_change=False,
        approved_for_direct_command=False,
        approved_for_execution=False,
        approved_for_task_behavior_change=False,
        approved_for_memory_layer_write=False,
        requires_rollback_record=True,
        requires_post_application_audit=True,
        source_trace_refs=(),
    )


def _application_record(
    record: AdvisoryReadbackCandidateOrderingApplicationRecord | dict[str, object],
) -> AdvisoryReadbackCandidateOrderingApplicationRecord:
    return (
        record
        if isinstance(record, AdvisoryReadbackCandidateOrderingApplicationRecord)
        else AdvisoryReadbackCandidateOrderingApplicationRecord.from_dict(dict(record))
    )


def _rollback_record(
    record: AdvisoryReadbackCandidateOrderingRollbackRecord | dict[str, object],
) -> AdvisoryReadbackCandidateOrderingRollbackRecord:
    return (
        record
        if isinstance(record, AdvisoryReadbackCandidateOrderingRollbackRecord)
        else AdvisoryReadbackCandidateOrderingRollbackRecord.from_dict(dict(record))
    )


def _application_audit(
    record: AdvisoryReadbackCandidateOrderingApplicationAudit | dict[str, object],
) -> AdvisoryReadbackCandidateOrderingApplicationAudit:
    return (
        record
        if isinstance(record, AdvisoryReadbackCandidateOrderingApplicationAudit)
        else AdvisoryReadbackCandidateOrderingApplicationAudit.from_dict(dict(record))
    )


def _milestone_audit(
    record: ReviewedConceptReadbackLoopMilestoneAudit | dict[str, object],
) -> ReviewedConceptReadbackLoopMilestoneAudit:
    from ashl_core_v1.audit.reviewed_concept_readback_loop_milestone_audit import (
        ReviewedConceptReadbackLoopMilestoneAudit,
    )

    return (
        record
        if isinstance(record, ReviewedConceptReadbackLoopMilestoneAudit)
        else ReviewedConceptReadbackLoopMilestoneAudit.from_dict(dict(record))
    )


def _readback_snapshot(
    record: FutureTaskWorkingMemoryInitializationReadbackSnapshot | dict[str, object],
) -> FutureTaskWorkingMemoryInitializationReadbackSnapshot:
    return (
        record
        if isinstance(record, FutureTaskWorkingMemoryInitializationReadbackSnapshot)
        else FutureTaskWorkingMemoryInitializationReadbackSnapshot.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
