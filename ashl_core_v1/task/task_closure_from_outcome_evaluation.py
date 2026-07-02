"""Task closure records built from deterministic outcome evaluation."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.task.outcome_evaluation_from_sense_observation import (
    TaskExpectedEffectReferenceRecord,
    TaskExecutionOutcomeEvaluationRecord,
    TaskGoalDeltaEvaluationRecord,
    TaskOutcomeEvaluationSafetyAudit,
    build_demo_observe_outcome_evaluation,
    build_demo_push_right_matched_outcome_evaluation,
    build_demo_push_right_not_matched_outcome_evaluation,
    build_demo_step_forward_matched_outcome_evaluation,
    build_demo_step_forward_not_matched_outcome_evaluation,
    build_demo_unknown_expected_effect_outcome_evaluation,
    validate_task_execution_outcome_evaluation_record,
    validate_task_goal_delta_evaluation_record,
    validate_task_outcome_evaluation_safety_audit,
)


SOURCE_ENGINE = "task_engine"

CLOSURE_SCHEMA_VERSION = "task_engine_task_closure_from_outcome_evaluation_v0"
SUMMARY_SCHEMA_VERSION = "task_engine_task_closure_summary_v0"
ROLLBACK_SCHEMA_VERSION = "task_engine_task_closure_rollback_v0"
SAFETY_AUDIT_SCHEMA_VERSION = "task_engine_task_closure_safety_audit_v0"

SAFE_CLAIM = (
    "ASHL Core v1 Task Engine can create task closure records from deterministic "
    "outcome evaluation, preserving traceability from expected effect, Sense "
    "observation, sandbox execution, and goal delta, while avoiding learning "
    "feedback, memory writes, action authority changes, behavior changes, or "
    "automatic learning approval."
)
BLOCKED_CLAIMS = (
    "no_learning_feedback",
    "no_memory_write",
    "no_action_authority_change",
    "no_behavior_change",
    "no_automatic_learning_approval",
)

ALLOWED_CLOSURE_CLASSES = {
    "goal_reached_closure",
    "progress_closure",
    "no_progress_closure",
    "expected_effect_failed_closure",
    "observation_only_closure",
    "unknown_outcome_closure",
    "system_fault_closure",
}
ALLOWED_CLOSURE_STATUSES = {
    "task_closed_goal_reached",
    "task_closed_with_progress",
    "task_closed_no_progress",
    "task_closed_expected_effect_failed",
    "task_closed_observation_only",
    "task_closed_unknown",
    "task_closed_system_fault",
    "blocked_invalid_outcome_evaluation",
    "blocked_invalid_goal_delta_evaluation",
    "blocked_forbidden_authority_detected",
}
ALLOWED_ROLLBACK_STATUSES = {
    "rollback_record_created",
    "rollback_applied_to_reopen_task_closure_record",
    "blocked_invalid_task_closure",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_task_closure_only",
    "passed_task_closed_unknown",
    "blocked_invalid_outcome_evaluation",
    "blocked_invalid_goal_delta_evaluation",
    "blocked_invalid_task_closure",
    "blocked_missing_rollback",
    "blocked_learning_feedback_detected",
    "blocked_memory_write_detected",
    "blocked_action_authority_detected",
    "blocked_behavior_change_detected",
}
PASSING_OUTCOME_AUDIT_STATUSES = {
    "passed_outcome_evaluation_only",
    "passed_outcome_unknown",
}
ALLOWED_OUTCOME_STATUSES_FOR_CLOSURE = {
    "outcome_evaluated",
    "outcome_evaluated_no_visible_delta",
    "outcome_unknown_missing_expected_effect",
    "outcome_unknown_missing_observation",
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
class TaskClosureFromOutcomeEvaluationRecord:
    task_closure_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_task_initialization_id: str | None
    source_expected_effect_reference_id: str
    source_outcome_evaluation_id: str
    source_goal_delta_evaluation_id: str
    source_outcome_evaluation_safety_audit_id: str | None
    source_sense_handoff_id: str | None
    source_sandbox_execution_id: str | None
    source_direct_command_application_id: str | None
    direct_command: str | None
    expected_effect: str
    outcome_class: str
    outcome_summary: str
    goal_delta_class: str
    goal_delta_summary: str
    task_goal_id: str | None
    task_goal_summary: str | None
    closure_class: str
    closure_status: str
    closure_reason: str
    closure_summary: str
    task_closed: bool
    task_closed_at: str | None
    available_for_learning_feedback_candidate_later: bool
    available_for_memory_write: bool
    learning_feedback_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created_by_closure: bool
    task_behavior_changed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CLOSURE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_task_closure_from_outcome_evaluation_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.closure_class not in ALLOWED_CLOSURE_CLASSES:
            raise ValueError(f"unknown closure_class: {self.closure_class}")
        if self.closure_status not in ALLOWED_CLOSURE_STATUSES:
            raise ValueError(f"unknown closure_status: {self.closure_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TaskClosureFromOutcomeEvaluationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskClosureSummaryRecord:
    task_closure_summary_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_closure_id: str
    source_task_working_memory_id: str
    task_closed: bool
    closure_status: str
    closure_class: str
    direct_command: str | None
    expected_effect: str
    outcome_class: str
    goal_delta_class: str
    short_summary: str
    evidence_summary: str
    source_sense_handoff_id: str | None
    source_sandbox_execution_id: str | None
    available_for_learning_feedback_candidate_later: bool
    learning_feedback_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SUMMARY_SCHEMA_VERSION:
            raise ValueError("schema_version must be task_engine_task_closure_summary_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.closure_class not in ALLOWED_CLOSURE_CLASSES:
            raise ValueError(f"unknown closure_class: {self.closure_class}")
        if self.closure_status not in ALLOWED_CLOSURE_STATUSES:
            raise ValueError(f"unknown closure_status: {self.closure_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TaskClosureSummaryRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskClosureRollbackRecord:
    task_closure_rollback_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_closure_id: str
    source_task_working_memory_id: str
    task_closed_before_rollback: bool
    task_closed_after_rollback: bool
    closure_status_before_rollback: str
    closure_status_after_rollback: str | None
    rollback_available: bool
    rollback_applied: bool
    rollback_reason: str
    rollback_status: str
    rollback_summary: str
    learning_feedback_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created_by_rollback: bool
    task_behavior_changed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ROLLBACK_SCHEMA_VERSION:
            raise ValueError("schema_version must be task_engine_task_closure_rollback_v0")
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
    def from_dict(cls, data: dict[str, object]) -> "TaskClosureRollbackRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskClosureSafetyAudit:
    task_closure_safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_closure_id: str | None
    source_task_closure_summary_id: str | None
    source_task_closure_rollback_id: str | None
    source_outcome_evaluation_id: str | None
    source_goal_delta_evaluation_id: str | None
    outcome_evaluation_valid: bool
    goal_delta_evaluation_valid: bool
    task_closure_valid: bool
    task_closure_summary_valid: bool
    rollback_available: bool
    closure_only_confirmed: bool
    no_learning_feedback: bool
    no_memory_write: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_automatic_learning_approval: bool
    no_candidate_ordering_change: bool
    no_selected_action_change: bool
    no_final_action_change: bool
    no_direct_command_change: bool
    no_execution_created_by_closure: bool
    no_task_behavior_change: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be task_engine_task_closure_safety_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        object.__setattr__(
            self,
            "blocked_claims",
            _tuple_of_str("blocked_claims", self.blocked_claims),
        )
        object.__setattr__(
            self,
            "blocked_reasons",
            _tuple_of_str("blocked_reasons", self.blocked_reasons),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TaskClosureSafetyAudit":
        return cls(**dict(data))


def build_task_closure_from_outcome_evaluation_record(
    *,
    expected_effect_reference: TaskExpectedEffectReferenceRecord | dict[str, object],
    outcome_evaluation: TaskExecutionOutcomeEvaluationRecord | dict[str, object],
    goal_delta_evaluation: TaskGoalDeltaEvaluationRecord | dict[str, object],
    outcome_evaluation_safety_audit: TaskOutcomeEvaluationSafetyAudit | dict[str, object] | None,
    learning_feedback_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    candidate_ordering_changed: bool = False,
    selected_action_changed: bool = False,
    final_action_changed: bool = False,
    direct_command_changed: bool = False,
    execution_created_by_closure: bool = False,
    task_behavior_changed: bool = False,
) -> TaskClosureFromOutcomeEvaluationRecord:
    reference = _reference_record(expected_effect_reference)
    outcome = _outcome_record(outcome_evaluation)
    goal_delta = _goal_delta_record(goal_delta_evaluation)
    outcome_audit = (
        _outcome_audit_record(outcome_evaluation_safety_audit)
        if outcome_evaluation_safety_audit is not None
        else None
    )
    forbidden_authority = any(
        (
            learning_feedback_created,
            memory_write_performed,
            automatic_learning_approval_created,
            candidate_ordering_changed,
            selected_action_changed,
            final_action_changed,
            direct_command_changed,
            execution_created_by_closure,
            task_behavior_changed,
        )
    )
    outcome_valid = _outcome_valid_for_closure(outcome)
    goal_delta_valid = validate_task_goal_delta_evaluation_record(goal_delta)["valid"]
    outcome_audit_passed = _outcome_audit_passed(outcome_audit)
    now = _now()
    if forbidden_authority:
        closure_class = "system_fault_closure"
        closure_status = "blocked_forbidden_authority_detected"
        task_closed = False
        learning_available = False
    elif not outcome_valid or not outcome_audit_passed:
        closure_class = "system_fault_closure"
        closure_status = "blocked_invalid_outcome_evaluation"
        task_closed = False
        learning_available = False
    elif not goal_delta_valid:
        closure_class = "system_fault_closure"
        closure_status = "blocked_invalid_goal_delta_evaluation"
        task_closed = False
        learning_available = False
    else:
        closure_class, closure_status, learning_available = _closure_policy(
            outcome_class=outcome.outcome_class,
            goal_delta_class=goal_delta.goal_delta_class,
        )
        task_closed = True
    return TaskClosureFromOutcomeEvaluationRecord(
        task_closure_id=f"task_closure:{outcome.outcome_evaluation_id}",
        schema_version=CLOSURE_SCHEMA_VERSION,
        created_at=now,
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=outcome.source_task_working_memory_id,
        source_task_initialization_id=_task_initialization_id(outcome),
        source_expected_effect_reference_id=reference.expected_effect_reference_id,
        source_outcome_evaluation_id=outcome.outcome_evaluation_id,
        source_goal_delta_evaluation_id=goal_delta.goal_delta_evaluation_id,
        source_outcome_evaluation_safety_audit_id=(
            outcome_audit.outcome_evaluation_safety_audit_id if outcome_audit else None
        ),
        source_sense_handoff_id=outcome.source_sense_handoff_id,
        source_sandbox_execution_id=outcome.source_sandbox_execution_id,
        source_direct_command_application_id=outcome.source_direct_command_application_id,
        direct_command=outcome.direct_command,
        expected_effect=outcome.expected_effect,
        outcome_class=outcome.outcome_class,
        outcome_summary=outcome.outcome_summary,
        goal_delta_class=goal_delta.goal_delta_class,
        goal_delta_summary=goal_delta.goal_delta_summary,
        task_goal_id=goal_delta.task_goal_id,
        task_goal_summary=goal_delta.task_goal_summary,
        closure_class=closure_class,
        closure_status=closure_status,
        closure_reason=_closure_reason(outcome, goal_delta, closure_status),
        closure_summary=_closure_summary(closure_class, closure_status),
        task_closed=task_closed,
        task_closed_at=now if task_closed else None,
        available_for_learning_feedback_candidate_later=learning_available,
        available_for_memory_write=False,
        learning_feedback_created=learning_feedback_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        candidate_ordering_changed=candidate_ordering_changed,
        selected_action_changed=selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_changed=direct_command_changed,
        execution_created_by_closure=execution_created_by_closure,
        task_behavior_changed=task_behavior_changed,
        source_trace_refs=_combined_trace_refs(
            reference.source_trace_refs,
            outcome.source_trace_refs,
            goal_delta.source_trace_refs,
            outcome_audit.source_trace_refs if outcome_audit else (),
        ),
    )


def validate_task_closure_from_outcome_evaluation_record(
    task_closure: TaskClosureFromOutcomeEvaluationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _closure_record(task_closure)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_task_closure:{error}"]}
    errors: list[str] = []
    if record.closure_status.startswith("blocked_"):
        errors.append(record.closure_status)
    if record.task_closed and record.task_closed_at is None:
        errors.append("task_closed_without_timestamp")
    if record.available_for_memory_write is not False:
        errors.append("available_for_memory_write_true")
    for flag in (
        "learning_feedback_created",
        "memory_write_performed",
        "automatic_learning_approval_created",
        "candidate_ordering_changed",
        "selected_action_changed",
        "final_action_changed",
        "direct_command_changed",
        "execution_created_by_closure",
        "task_behavior_changed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "task_closure_id": record.task_closure_id,
        "closure_status": record.closure_status,
        "closure_class": record.closure_class,
    }


def build_task_closure_summary_record(
    *,
    task_closure: TaskClosureFromOutcomeEvaluationRecord | dict[str, object],
) -> TaskClosureSummaryRecord:
    closure = _closure_record(task_closure)
    short_summary = (
        f"Closure {closure.closure_status} for direct_command {closure.direct_command}."
    )
    evidence_summary = (
        f"direct_command {closure.direct_command} expected {closure.expected_effect}; "
        f"outcome {closure.outcome_class} and goal_delta {closure.goal_delta_class}. "
        f"Closure: {closure.closure_class}."
    )
    return TaskClosureSummaryRecord(
        task_closure_summary_id=f"task_closure_summary:{closure.task_closure_id}",
        schema_version=SUMMARY_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_closure_id=closure.task_closure_id,
        source_task_working_memory_id=closure.source_task_working_memory_id,
        task_closed=closure.task_closed,
        closure_status=closure.closure_status,
        closure_class=closure.closure_class,
        direct_command=closure.direct_command,
        expected_effect=closure.expected_effect,
        outcome_class=closure.outcome_class,
        goal_delta_class=closure.goal_delta_class,
        short_summary=short_summary,
        evidence_summary=evidence_summary,
        source_sense_handoff_id=closure.source_sense_handoff_id,
        source_sandbox_execution_id=closure.source_sandbox_execution_id,
        available_for_learning_feedback_candidate_later=(
            closure.available_for_learning_feedback_candidate_later
        ),
        learning_feedback_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=closure.source_trace_refs,
    )


def validate_task_closure_summary_record(
    summary: TaskClosureSummaryRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _summary_record(summary)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_task_closure_summary:{error}"]}
    errors: list[str] = []
    for flag in (
        "learning_feedback_created",
        "memory_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    if not record.short_summary or not record.evidence_summary:
        errors.append("summary_text_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "task_closure_summary_id": record.task_closure_summary_id,
        "closure_status": record.closure_status,
    }


def build_task_closure_rollback_record(
    *,
    task_closure: TaskClosureFromOutcomeEvaluationRecord | dict[str, object],
    rollback_reason: str = "Rollback record is available to reopen the closure record.",
) -> TaskClosureRollbackRecord:
    closure = _closure_record(task_closure)
    closure_valid = validate_task_closure_from_outcome_evaluation_record(closure)["valid"]
    status = "rollback_record_created" if closure_valid else "blocked_invalid_task_closure"
    return TaskClosureRollbackRecord(
        task_closure_rollback_id=f"task_closure_rollback:{closure.task_closure_id}",
        schema_version=ROLLBACK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_closure_id=closure.task_closure_id,
        source_task_working_memory_id=closure.source_task_working_memory_id,
        task_closed_before_rollback=closure.task_closed,
        task_closed_after_rollback=closure.task_closed,
        closure_status_before_rollback=closure.closure_status,
        closure_status_after_rollback=closure.closure_status,
        rollback_available=True,
        rollback_applied=False,
        rollback_reason=rollback_reason,
        rollback_status=status,
        rollback_summary=_rollback_summary(status),
        learning_feedback_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        candidate_ordering_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_changed=False,
        execution_created_by_rollback=False,
        task_behavior_changed=False,
        source_trace_refs=closure.source_trace_refs,
    )


def apply_task_closure_rollback(
    *,
    task_closure: TaskClosureFromOutcomeEvaluationRecord | dict[str, object],
    rollback_reason: str = "Rollback applied to reopen closure record.",
) -> TaskClosureRollbackRecord:
    closure = _closure_record(task_closure)
    closure_valid = validate_task_closure_from_outcome_evaluation_record(closure)["valid"]
    status = (
        "rollback_applied_to_reopen_task_closure_record"
        if closure_valid
        else "blocked_invalid_task_closure"
    )
    return TaskClosureRollbackRecord(
        task_closure_rollback_id=f"task_closure_rollback:{closure.task_closure_id}:applied",
        schema_version=ROLLBACK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_closure_id=closure.task_closure_id,
        source_task_working_memory_id=closure.source_task_working_memory_id,
        task_closed_before_rollback=closure.task_closed,
        task_closed_after_rollback=False if closure_valid else closure.task_closed,
        closure_status_before_rollback=closure.closure_status,
        closure_status_after_rollback=None if closure_valid else closure.closure_status,
        rollback_available=True,
        rollback_applied=closure_valid,
        rollback_reason=rollback_reason,
        rollback_status=status,
        rollback_summary=_rollback_summary(status),
        learning_feedback_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        candidate_ordering_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_changed=False,
        execution_created_by_rollback=False,
        task_behavior_changed=False,
        source_trace_refs=closure.source_trace_refs,
    )


def validate_task_closure_rollback_record(
    rollback: TaskClosureRollbackRecord | dict[str, object],
) -> dict[str, object]:
    return _validate_task_closure_rollback_record(rollback)


def build_task_closure_safety_audit(
    *,
    outcome_evaluation: TaskExecutionOutcomeEvaluationRecord | dict[str, object] | None,
    goal_delta_evaluation: TaskGoalDeltaEvaluationRecord | dict[str, object] | None,
    task_closure: TaskClosureFromOutcomeEvaluationRecord | dict[str, object] | None,
    task_closure_summary: TaskClosureSummaryRecord | dict[str, object] | None,
    task_closure_rollback: TaskClosureRollbackRecord | dict[str, object] | None,
    outcome_evaluation_safety_audit: TaskOutcomeEvaluationSafetyAudit | dict[str, object] | None = None,
) -> TaskClosureSafetyAudit:
    outcome = _outcome_record(outcome_evaluation) if outcome_evaluation is not None else None
    goal_delta = (
        _goal_delta_record(goal_delta_evaluation)
        if goal_delta_evaluation is not None
        else None
    )
    closure = _closure_record(task_closure) if task_closure is not None else None
    summary = (
        _summary_record(task_closure_summary)
        if task_closure_summary is not None
        else None
    )
    rollback = (
        _rollback_record(task_closure_rollback)
        if task_closure_rollback is not None
        else None
    )
    outcome_audit = (
        _outcome_audit_record(outcome_evaluation_safety_audit)
        if outcome_evaluation_safety_audit is not None
        else None
    )
    outcome_valid = outcome is not None and _outcome_valid_for_closure(outcome)
    if outcome_audit is not None and not _outcome_audit_passed(outcome_audit):
        outcome_valid = False
    goal_valid = (
        goal_delta is not None
        and validate_task_goal_delta_evaluation_record(goal_delta)["valid"]
    )
    closure_valid = (
        closure is not None
        and validate_task_closure_from_outcome_evaluation_record(closure)["valid"]
    )
    summary_valid = (
        summary is not None
        and validate_task_closure_summary_record(summary)["valid"]
    )
    rollback_available = rollback is not None and rollback.rollback_available is True
    no_learning = not _learning_feedback_created(closure, summary, rollback)
    no_memory = not _memory_write_performed(closure, summary, rollback)
    no_auto = not _automatic_learning_approval_created(closure, summary, rollback)
    no_action = not _action_authority_changed(closure, rollback)
    no_behavior = not _behavior_changed(closure, rollback)
    blocked_reasons = _audit_blocked_reasons(
        outcome_valid=outcome_valid,
        goal_valid=goal_valid,
        closure_valid=closure_valid,
        summary_valid=summary_valid,
        rollback_available=rollback_available,
        no_learning=no_learning,
        no_memory=no_memory,
        no_action=no_action,
        no_behavior=no_behavior,
    )
    return TaskClosureSafetyAudit(
        task_closure_safety_audit_id=(
            f"task_closure_safety_audit:{closure.task_closure_id}"
            if closure
            else "task_closure_safety_audit:unknown"
        ),
        schema_version=SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_closure_id=closure.task_closure_id if closure else None,
        source_task_closure_summary_id=summary.task_closure_summary_id if summary else None,
        source_task_closure_rollback_id=rollback.task_closure_rollback_id if rollback else None,
        source_outcome_evaluation_id=outcome.outcome_evaluation_id if outcome else None,
        source_goal_delta_evaluation_id=goal_delta.goal_delta_evaluation_id if goal_delta else None,
        outcome_evaluation_valid=outcome_valid,
        goal_delta_evaluation_valid=goal_valid,
        task_closure_valid=closure_valid,
        task_closure_summary_valid=summary_valid,
        rollback_available=rollback_available,
        closure_only_confirmed=True,
        no_learning_feedback=no_learning,
        no_memory_write=no_memory,
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_automatic_learning_approval=no_auto,
        no_candidate_ordering_change=not (closure.candidate_ordering_changed if closure else False),
        no_selected_action_change=not (
            (closure.selected_action_changed if closure else False)
            or (rollback.selected_action_changed if rollback else False)
        ),
        no_final_action_change=not (
            (closure.final_action_changed if closure else False)
            or (rollback.final_action_changed if rollback else False)
        ),
        no_direct_command_change=not (
            (closure.direct_command_changed if closure else False)
            or (rollback.direct_command_changed if rollback else False)
        ),
        no_execution_created_by_closure=not (
            (closure.execution_created_by_closure if closure else False)
            or (rollback.execution_created_by_rollback if rollback else False)
        ),
        no_task_behavior_change=no_behavior,
        audit_status=_audit_status(blocked_reasons, closure=closure),
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(blocked_reasons),
        source_trace_refs=_combined_trace_refs(
            outcome.source_trace_refs if outcome else (),
            goal_delta.source_trace_refs if goal_delta else (),
            closure.source_trace_refs if closure else (),
            summary.source_trace_refs if summary else (),
            rollback.source_trace_refs if rollback else (),
        ),
    )


def validate_task_closure_safety_audit(
    audit: TaskClosureSafetyAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _audit_record(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_task_closure_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status not in {"passed_task_closure_only", "passed_task_closed_unknown"}:
        errors.append(record.audit_status)
    for flag in (
        "closure_only_confirmed",
        "no_learning_feedback",
        "no_memory_write",
        "no_core_memory_write",
        "no_long_term_memory_write",
        "no_archive_memory_write",
        "no_anchor_write",
        "no_automatic_learning_approval",
        "no_candidate_ordering_change",
        "no_selected_action_change",
        "no_final_action_change",
        "no_direct_command_change",
        "no_execution_created_by_closure",
        "no_task_behavior_change",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    if not set(BLOCKED_CLAIMS).issubset(set(record.blocked_claims)):
        errors.append("blocked_claims_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "task_closure_safety_audit_id": record.task_closure_safety_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_demo_observe_task_closure() -> dict[str, object]:
    return _build_task_closure_bundle(build_demo_observe_outcome_evaluation())


def build_demo_step_forward_matched_task_closure() -> dict[str, object]:
    return _build_task_closure_bundle(build_demo_step_forward_matched_outcome_evaluation())


def build_demo_step_forward_not_matched_task_closure() -> dict[str, object]:
    return _build_task_closure_bundle(build_demo_step_forward_not_matched_outcome_evaluation())


def build_demo_push_right_matched_task_closure() -> dict[str, object]:
    return _build_task_closure_bundle(build_demo_push_right_matched_outcome_evaluation())


def build_demo_push_right_not_matched_task_closure() -> dict[str, object]:
    return _build_task_closure_bundle(build_demo_push_right_not_matched_outcome_evaluation())


def build_demo_unknown_outcome_task_closure() -> dict[str, object]:
    return _build_task_closure_bundle(build_demo_unknown_expected_effect_outcome_evaluation())


def build_demo_blocked_invalid_outcome_evaluation_task_closure() -> dict[str, object]:
    payload = build_demo_observe_outcome_evaluation()
    outcome = dict(payload["task_execution_outcome_evaluation"])
    outcome["evaluation_status"] = "blocked_invalid_sense_handoff"
    return _build_task_closure_bundle({**payload, "task_execution_outcome_evaluation": outcome})


def build_demo_blocked_invalid_goal_delta_task_closure() -> dict[str, object]:
    payload = build_demo_observe_outcome_evaluation()
    goal_delta = dict(payload["task_goal_delta_evaluation"])
    goal_delta["goal_delta_status"] = "blocked_invalid_outcome_evaluation"
    goal_delta["goal_delta_class"] = "system_fault"
    return _build_task_closure_bundle({**payload, "task_goal_delta_evaluation": goal_delta})


def build_demo_blocked_invalid_outcome_audit_task_closure() -> dict[str, object]:
    payload = build_demo_observe_outcome_evaluation()
    outcome_audit = dict(payload["task_outcome_evaluation_safety_audit"])
    outcome_audit["audit_status"] = "blocked_invalid_outcome_evaluation"
    outcome_audit["blocked_reasons"] = ["invalid_outcome_evaluation"]
    return _build_task_closure_bundle(
        {**payload, "task_outcome_evaluation_safety_audit": outcome_audit}
    )


def build_demo_blocked_learning_feedback_created_task_closure() -> dict[str, object]:
    return _build_task_closure_bundle(
        build_demo_observe_outcome_evaluation(),
        learning_feedback_created=True,
    )


def build_demo_blocked_memory_write_task_closure() -> dict[str, object]:
    return _build_task_closure_bundle(
        build_demo_observe_outcome_evaluation(),
        memory_write_performed=True,
    )


def build_demo_blocked_action_authority_task_closure() -> dict[str, object]:
    return _build_task_closure_bundle(
        build_demo_observe_outcome_evaluation(),
        selected_action_changed=True,
    )


def build_demo_blocked_behavior_change_task_closure() -> dict[str, object]:
    return _build_task_closure_bundle(
        build_demo_observe_outcome_evaluation(),
        task_behavior_changed=True,
    )


def build_demo_blocked_missing_rollback_task_closure() -> dict[str, object]:
    return _build_task_closure_bundle(
        build_demo_observe_outcome_evaluation(),
        include_rollback=False,
    )


def build_demo_task_closure_case(case: str) -> dict[str, object]:
    builders = {
        "observe": build_demo_observe_task_closure,
        "step-forward-matched": build_demo_step_forward_matched_task_closure,
        "step-forward-not-matched": build_demo_step_forward_not_matched_task_closure,
        "push-right-matched": build_demo_push_right_matched_task_closure,
        "push-right-not-matched": build_demo_push_right_not_matched_task_closure,
        "unknown-outcome": build_demo_unknown_outcome_task_closure,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown task closure demo case: {case}") from error


def build_demo_blocked_task_closure(case: str) -> dict[str, object]:
    builders = {
        "invalid-outcome-evaluation": build_demo_blocked_invalid_outcome_evaluation_task_closure,
        "invalid-goal-delta": build_demo_blocked_invalid_goal_delta_task_closure,
        "invalid-outcome-audit": build_demo_blocked_invalid_outcome_audit_task_closure,
        "learning-feedback-created": build_demo_blocked_learning_feedback_created_task_closure,
        "memory-write-detected": build_demo_blocked_memory_write_task_closure,
        "action-authority-detected": build_demo_blocked_action_authority_task_closure,
        "behavior-change-detected": build_demo_blocked_behavior_change_task_closure,
        "missing-rollback": build_demo_blocked_missing_rollback_task_closure,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown task closure blocked case: {case}") from error


def _build_task_closure_bundle(
    package87_payload: dict[str, object],
    *,
    include_rollback: bool = True,
    learning_feedback_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    candidate_ordering_changed: bool = False,
    selected_action_changed: bool = False,
    final_action_changed: bool = False,
    direct_command_changed: bool = False,
    execution_created_by_closure: bool = False,
    task_behavior_changed: bool = False,
) -> dict[str, object]:
    reference = TaskExpectedEffectReferenceRecord.from_dict(
        package87_payload["task_expected_effect_reference"]
    )
    outcome = TaskExecutionOutcomeEvaluationRecord.from_dict(
        package87_payload["task_execution_outcome_evaluation"]
    )
    goal_delta = TaskGoalDeltaEvaluationRecord.from_dict(
        package87_payload["task_goal_delta_evaluation"]
    )
    outcome_audit = TaskOutcomeEvaluationSafetyAudit.from_dict(
        package87_payload["task_outcome_evaluation_safety_audit"]
    )
    closure = build_task_closure_from_outcome_evaluation_record(
        expected_effect_reference=reference,
        outcome_evaluation=outcome,
        goal_delta_evaluation=goal_delta,
        outcome_evaluation_safety_audit=outcome_audit,
        learning_feedback_created=learning_feedback_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        candidate_ordering_changed=candidate_ordering_changed,
        selected_action_changed=selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_changed=direct_command_changed,
        execution_created_by_closure=execution_created_by_closure,
        task_behavior_changed=task_behavior_changed,
    )
    summary = build_task_closure_summary_record(task_closure=closure)
    rollback = (
        build_task_closure_rollback_record(task_closure=closure)
        if include_rollback
        else None
    )
    audit = build_task_closure_safety_audit(
        outcome_evaluation=outcome,
        goal_delta_evaluation=goal_delta,
        task_closure=closure,
        task_closure_summary=summary,
        task_closure_rollback=rollback,
        outcome_evaluation_safety_audit=outcome_audit,
    )
    payload = {
        "task_closure_from_outcome_evaluation": closure.to_dict(),
        "task_closure_summary": summary.to_dict(),
        "task_closure_safety_audit": audit.to_dict(),
        "task_closure_from_outcome_evaluation_validation": (
            validate_task_closure_from_outcome_evaluation_record(closure)
        ),
        "task_closure_summary_validation": validate_task_closure_summary_record(summary),
        "task_closure_safety_audit_validation": validate_task_closure_safety_audit(audit),
        "source_package87_expected_effect_reference": reference.to_dict(),
        "source_package87_outcome_evaluation": outcome.to_dict(),
        "source_package87_goal_delta_evaluation": goal_delta.to_dict(),
        "source_package87_outcome_evaluation_safety_audit": outcome_audit.to_dict(),
        "safe_claim": SAFE_CLAIM,
    }
    if rollback is not None:
        payload["task_closure_rollback"] = rollback.to_dict()
        payload["task_closure_rollback_validation"] = _validate_task_closure_rollback_record(
            rollback
        )
    else:
        payload["task_closure_rollback"] = None
        payload["task_closure_rollback_validation"] = {
            "valid": False,
            "error_codes": ["missing_rollback"],
        }
    return payload


def _closure_policy(
    *,
    outcome_class: str,
    goal_delta_class: str,
) -> tuple[str, str, bool]:
    if goal_delta_class == "goal_reached":
        return ("goal_reached_closure", "task_closed_goal_reached", True)
    if goal_delta_class == "closer_to_goal":
        return ("progress_closure", "task_closed_with_progress", True)
    if outcome_class == "expected_effect_matched":
        return ("progress_closure", "task_closed_with_progress", True)
    if outcome_class == "expected_effect_not_matched":
        return (
            "expected_effect_failed_closure",
            "task_closed_expected_effect_failed",
            True,
        )
    if goal_delta_class == "no_progress":
        return ("no_progress_closure", "task_closed_no_progress", True)
    if outcome_class == "observation_only":
        return ("observation_only_closure", "task_closed_observation_only", False)
    if outcome_class in {"unknown_expected_effect", "unknown_observation"}:
        return ("unknown_outcome_closure", "task_closed_unknown", False)
    if outcome_class == "system_fault":
        return ("system_fault_closure", "task_closed_system_fault", False)
    return ("no_progress_closure", "task_closed_no_progress", True)


def _closure_reason(
    outcome: TaskExecutionOutcomeEvaluationRecord,
    goal_delta: TaskGoalDeltaEvaluationRecord,
    closure_status: str,
) -> str:
    return (
        f"closure_status={closure_status}; outcome_class={outcome.outcome_class}; "
        f"goal_delta_class={goal_delta.goal_delta_class}"
    )


def _closure_summary(closure_class: str, closure_status: str) -> str:
    return f"Task closure record created as {closure_class} with status {closure_status}."


def _rollback_summary(status: str) -> str:
    if status == "rollback_applied_to_reopen_task_closure_record":
        return "Rollback reopened the closure record only."
    if status == "blocked_invalid_task_closure":
        return "Rollback blocked because the task closure record is invalid."
    return "Rollback record created for the task closure record."


def _audit_blocked_reasons(
    *,
    outcome_valid: bool,
    goal_valid: bool,
    closure_valid: bool,
    summary_valid: bool,
    rollback_available: bool,
    no_learning: bool,
    no_memory: bool,
    no_action: bool,
    no_behavior: bool,
) -> list[str]:
    reasons: list[str] = []
    if not outcome_valid:
        reasons.append("invalid_outcome_evaluation")
    if not goal_valid:
        reasons.append("invalid_goal_delta_evaluation")
    if not closure_valid:
        reasons.append("invalid_task_closure")
    if not summary_valid:
        reasons.append("invalid_task_closure_summary")
    if not rollback_available:
        reasons.append("missing_rollback")
    if not no_learning:
        reasons.append("learning_feedback_created")
    if not no_memory:
        reasons.append("memory_write_performed")
    if not no_action:
        reasons.append("action_authority_changed")
    if not no_behavior:
        reasons.append("task_behavior_changed")
    return reasons


def _audit_status(
    blocked_reasons: list[str],
    *,
    closure: TaskClosureFromOutcomeEvaluationRecord | None,
) -> str:
    if "learning_feedback_created" in blocked_reasons:
        return "blocked_learning_feedback_detected"
    if "memory_write_performed" in blocked_reasons:
        return "blocked_memory_write_detected"
    if "action_authority_changed" in blocked_reasons:
        return "blocked_action_authority_detected"
    if "task_behavior_changed" in blocked_reasons:
        return "blocked_behavior_change_detected"
    if "invalid_outcome_evaluation" in blocked_reasons:
        return "blocked_invalid_outcome_evaluation"
    if "invalid_goal_delta_evaluation" in blocked_reasons:
        return "blocked_invalid_goal_delta_evaluation"
    if "invalid_task_closure" in blocked_reasons or "invalid_task_closure_summary" in blocked_reasons:
        return "blocked_invalid_task_closure"
    if "missing_rollback" in blocked_reasons:
        return "blocked_missing_rollback"
    if closure and closure.closure_status == "task_closed_unknown":
        return "passed_task_closed_unknown"
    return "passed_task_closure_only"


def _outcome_valid_for_closure(outcome: TaskExecutionOutcomeEvaluationRecord) -> bool:
    validation = validate_task_execution_outcome_evaluation_record(outcome)
    return (
        validation["valid"] is True
        and outcome.evaluation_status in ALLOWED_OUTCOME_STATUSES_FOR_CLOSURE
        and not outcome.task_closure_created
        and not outcome.learning_feedback_created
        and not outcome.memory_write_performed
        and not outcome.automatic_learning_approval_created
    )


def _outcome_audit_passed(
    outcome_audit: TaskOutcomeEvaluationSafetyAudit | None,
) -> bool:
    if outcome_audit is None:
        return False
    validation = validate_task_outcome_evaluation_safety_audit(outcome_audit)
    return (
        validation["valid"] is True
        and outcome_audit.audit_status in PASSING_OUTCOME_AUDIT_STATUSES
    )


def _validate_task_closure_rollback_record(
    rollback: TaskClosureRollbackRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _rollback_record(rollback)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_task_closure_rollback:{error}"]}
    errors: list[str] = []
    if record.rollback_status.startswith("blocked_"):
        errors.append(record.rollback_status)
    for flag in (
        "learning_feedback_created",
        "memory_write_performed",
        "automatic_learning_approval_created",
        "candidate_ordering_changed",
        "selected_action_changed",
        "final_action_changed",
        "direct_command_changed",
        "execution_created_by_rollback",
        "task_behavior_changed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    if record.rollback_available is not True:
        errors.append("rollback_available_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "task_closure_rollback_id": record.task_closure_rollback_id,
        "rollback_status": record.rollback_status,
    }


def _task_initialization_id(outcome: TaskExecutionOutcomeEvaluationRecord) -> str | None:
    marker = "task_initialization:"
    source = outcome.source_sandbox_execution_id or ""
    if marker in source:
        return marker + source.split(marker, 1)[1]
    if outcome.source_task_working_memory_id.startswith("task_working_memory:"):
        return outcome.source_task_working_memory_id.replace(
            "task_working_memory:",
            "task_initialization:",
            1,
        )
    return None


def _learning_feedback_created(
    closure: TaskClosureFromOutcomeEvaluationRecord | None,
    summary: TaskClosureSummaryRecord | None,
    rollback: TaskClosureRollbackRecord | None,
) -> bool:
    return bool(
        (closure.learning_feedback_created if closure else False)
        or (summary.learning_feedback_created if summary else False)
        or (rollback.learning_feedback_created if rollback else False)
    )


def _memory_write_performed(
    closure: TaskClosureFromOutcomeEvaluationRecord | None,
    summary: TaskClosureSummaryRecord | None,
    rollback: TaskClosureRollbackRecord | None,
) -> bool:
    return bool(
        (closure.memory_write_performed if closure else False)
        or (summary.memory_write_performed if summary else False)
        or (rollback.memory_write_performed if rollback else False)
    )


def _automatic_learning_approval_created(
    closure: TaskClosureFromOutcomeEvaluationRecord | None,
    summary: TaskClosureSummaryRecord | None,
    rollback: TaskClosureRollbackRecord | None,
) -> bool:
    return bool(
        (closure.automatic_learning_approval_created if closure else False)
        or (summary.automatic_learning_approval_created if summary else False)
        or (rollback.automatic_learning_approval_created if rollback else False)
    )


def _action_authority_changed(
    closure: TaskClosureFromOutcomeEvaluationRecord | None,
    rollback: TaskClosureRollbackRecord | None,
) -> bool:
    return bool(
        (closure.candidate_ordering_changed if closure else False)
        or (closure.selected_action_changed if closure else False)
        or (closure.final_action_changed if closure else False)
        or (closure.direct_command_changed if closure else False)
        or (closure.execution_created_by_closure if closure else False)
        or (rollback.candidate_ordering_changed if rollback else False)
        or (rollback.selected_action_changed if rollback else False)
        or (rollback.final_action_changed if rollback else False)
        or (rollback.direct_command_changed if rollback else False)
        or (rollback.execution_created_by_rollback if rollback else False)
    )


def _behavior_changed(
    closure: TaskClosureFromOutcomeEvaluationRecord | None,
    rollback: TaskClosureRollbackRecord | None,
) -> bool:
    return bool(
        (closure.task_behavior_changed if closure else False)
        or (rollback.task_behavior_changed if rollback else False)
    )


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _reference_record(
    record: TaskExpectedEffectReferenceRecord | dict[str, object],
) -> TaskExpectedEffectReferenceRecord:
    return (
        record
        if isinstance(record, TaskExpectedEffectReferenceRecord)
        else TaskExpectedEffectReferenceRecord.from_dict(dict(record))
    )


def _outcome_record(
    record: TaskExecutionOutcomeEvaluationRecord | dict[str, object],
) -> TaskExecutionOutcomeEvaluationRecord:
    return (
        record
        if isinstance(record, TaskExecutionOutcomeEvaluationRecord)
        else TaskExecutionOutcomeEvaluationRecord.from_dict(dict(record))
    )


def _goal_delta_record(
    record: TaskGoalDeltaEvaluationRecord | dict[str, object],
) -> TaskGoalDeltaEvaluationRecord:
    return (
        record
        if isinstance(record, TaskGoalDeltaEvaluationRecord)
        else TaskGoalDeltaEvaluationRecord.from_dict(dict(record))
    )


def _outcome_audit_record(
    record: TaskOutcomeEvaluationSafetyAudit | dict[str, object],
) -> TaskOutcomeEvaluationSafetyAudit:
    return (
        record
        if isinstance(record, TaskOutcomeEvaluationSafetyAudit)
        else TaskOutcomeEvaluationSafetyAudit.from_dict(dict(record))
    )


def _closure_record(
    record: TaskClosureFromOutcomeEvaluationRecord | dict[str, object],
) -> TaskClosureFromOutcomeEvaluationRecord:
    return (
        record
        if isinstance(record, TaskClosureFromOutcomeEvaluationRecord)
        else TaskClosureFromOutcomeEvaluationRecord.from_dict(dict(record))
    )


def _summary_record(
    record: TaskClosureSummaryRecord | dict[str, object],
) -> TaskClosureSummaryRecord:
    return (
        record
        if isinstance(record, TaskClosureSummaryRecord)
        else TaskClosureSummaryRecord.from_dict(dict(record))
    )


def _rollback_record(
    record: TaskClosureRollbackRecord | dict[str, object],
) -> TaskClosureRollbackRecord:
    return (
        record
        if isinstance(record, TaskClosureRollbackRecord)
        else TaskClosureRollbackRecord.from_dict(dict(record))
    )


def _audit_record(
    record: TaskClosureSafetyAudit | dict[str, object],
) -> TaskClosureSafetyAudit:
    return (
        record
        if isinstance(record, TaskClosureSafetyAudit)
        else TaskClosureSafetyAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
