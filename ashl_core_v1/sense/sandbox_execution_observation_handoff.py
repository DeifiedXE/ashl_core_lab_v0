"""Sense Interface handoff from bounded sandbox execution records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.task.teacher_gated_direct_command_sandbox_execution import (
    DirectCommandApplicationRecord,
    DirectCommandSandboxExecutionAudit,
    SandboxExecutionRecord,
    SandboxPreExecutionSnapshot,
    build_demo_blocked_direct_command_sandbox_execution,
    build_demo_direct_command_sandbox_execution,
    validate_sandbox_execution_record,
    validate_sandbox_pre_execution_snapshot,
)


SOURCE_ENGINE = "sense_interface"
TARGET_ENGINE = "task_engine"

OBSERVATION_SCHEMA_VERSION = "sense_interface_sandbox_execution_observation_v0"
STATE_DELTA_SCHEMA_VERSION = "sense_interface_sandbox_state_delta_observation_v0"
HANDOFF_SCHEMA_VERSION = "sense_interface_sandbox_observation_handoff_v0"
SAFETY_AUDIT_SCHEMA_VERSION = "sense_interface_sandbox_observation_safety_audit_v0"

SAFE_CLAIM = (
    "ASHL Core v1 Sense Interface can create descriptive observation and "
    "handoff records from bounded sandbox execution, making execution results "
    "available to future Task Engine outcome evaluation while avoiding task "
    "closure, learning feedback, memory writes, action authority changes, or "
    "automatic learning approval."
)
BLOCKED_CLAIMS = (
    "no_task_outcome_evaluation",
    "no_task_closure",
    "no_learning_feedback",
    "no_memory_write",
    "no_action_authority_change",
    "no_automatic_learning_approval",
)
FORBIDDEN_INTERPRETIVE_LABELS = {
    "success",
    "failure",
    "goal_reached",
    "useful_progress",
    "bad_action",
    "learnable",
    "blocked_as_task_failure",
    "task_completed",
    "goal_progress",
}

ALLOWED_OBSERVATION_STATUSES = {
    "observation_record_created",
    "observation_created_no_visible_delta",
    "blocked_invalid_sandbox_execution",
    "blocked_missing_pre_execution_snapshot",
    "blocked_external_execution_record",
    "blocked_forbidden_authority_detected",
}
ALLOWED_DELTA_STATUSES = {
    "state_delta_observed",
    "state_delta_observed_no_change",
    "state_delta_unknown",
    "blocked_invalid_observation",
    "blocked_forbidden_authority_detected",
}
ALLOWED_HANDOFF_STATUSES = {
    "handoff_ready_for_task_outcome_evaluation",
    "handoff_created_no_visible_delta",
    "blocked_invalid_sense_observation",
    "blocked_invalid_state_delta_observation",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_sense_observation_handoff",
    "passed_observation_created_no_visible_delta",
    "blocked_invalid_sandbox_execution",
    "blocked_missing_pre_execution_snapshot",
    "blocked_invalid_sense_observation",
    "blocked_invalid_state_delta_observation",
    "blocked_invalid_handoff",
    "blocked_outcome_evaluation_detected",
    "blocked_task_closure_detected",
    "blocked_learning_feedback_detected",
    "blocked_memory_write_detected",
    "blocked_action_authority_detected",
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


def _position(value: object) -> tuple[int, int] | None:
    if isinstance(value, tuple) and len(value) == 2:
        return (int(value[0]), int(value[1]))
    if isinstance(value, list) and len(value) == 2:
        return (int(value[0]), int(value[1]))
    return None


def _optional_position(value: object) -> tuple[int, int] | None:
    if value is None:
        return None
    return _position(value)


def _tuple_positions(value: object) -> tuple[tuple[int, int], ...]:
    if value is None:
        return ()
    if isinstance(value, tuple) and len(value) == 2 and all(
        isinstance(item, int) for item in value
    ):
        return ((int(value[0]), int(value[1])),)
    if isinstance(value, list):
        positions: list[tuple[int, int]] = []
        for item in value:
            position = _position(item)
            if position is not None:
                positions.append(position)
        return tuple(positions)
    if isinstance(value, tuple):
        positions = []
        for item in value:
            position = _position(item)
            if position is not None:
                positions.append(position)
        return tuple(positions)
    return ()


@dataclass(frozen=True)
class SenseSandboxExecutionObservationRecord:
    sense_observation_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_sandbox_execution_id: str
    source_direct_command_application_id: str
    source_pre_execution_snapshot_id: str
    source_execution_audit_id: str | None
    sandbox_id: str
    direct_command: str
    sense_observation_status: str
    sense_observation_summary: str
    observed_actor_position_before: tuple[int, int] | None
    observed_actor_position_after: tuple[int, int] | None
    observed_actor_position_changed: bool | None
    observed_box_positions_before: tuple[tuple[int, int], ...]
    observed_box_positions_after: tuple[tuple[int, int], ...]
    observed_box_position_changed: bool | None
    observed_goal_positions: tuple[tuple[int, int], ...]
    observed_wall_positions: tuple[tuple[int, int], ...]
    observed_contact: bool | None
    observed_contact_target: str | None
    visible_state_delta_labels: tuple[str, ...]
    raw_observation_notes: tuple[str, ...]
    outcome_evaluation_created: bool
    task_closure_created: bool
    learning_feedback_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created_by_sense: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != OBSERVATION_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be sense_interface_sandbox_execution_observation_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be sense_interface")
        if self.sense_observation_status not in ALLOWED_OBSERVATION_STATUSES:
            raise ValueError(
                f"unknown sense_observation_status: {self.sense_observation_status}"
            )
        object.__setattr__(
            self,
            "observed_actor_position_before",
            _optional_position(self.observed_actor_position_before),
        )
        object.__setattr__(
            self,
            "observed_actor_position_after",
            _optional_position(self.observed_actor_position_after),
        )
        for name in (
            "observed_box_positions_before",
            "observed_box_positions_after",
            "observed_goal_positions",
            "observed_wall_positions",
        ):
            object.__setattr__(self, name, _tuple_positions(getattr(self, name)))
        for name in ("visible_state_delta_labels", "raw_observation_notes", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SenseSandboxExecutionObservationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class SenseSandboxStateDeltaObservationRecord:
    state_delta_observation_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_sense_observation_id: str
    source_sandbox_execution_id: str
    sandbox_id: str
    direct_command: str
    raw_state_before: dict
    raw_state_after: dict
    observed_delta_keys: tuple[str, ...]
    observed_delta_summary: str
    actor_delta: dict | None
    box_delta: dict | None
    contact_delta: dict | None
    visibility_delta: dict | None
    state_delta_status: str
    outcome_evaluation_created: bool
    task_closure_created: bool
    learning_feedback_created: bool
    memory_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != STATE_DELTA_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be sense_interface_sandbox_state_delta_observation_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be sense_interface")
        if self.state_delta_status not in ALLOWED_DELTA_STATUSES:
            raise ValueError(f"unknown state_delta_status: {self.state_delta_status}")
        for name in ("observed_delta_keys", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SenseSandboxStateDeltaObservationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class SenseSandboxObservationHandoffRecord:
    sense_handoff_id: str
    schema_version: str
    created_at: str
    source_engine: str
    target_engine: str
    source_sense_observation_id: str
    source_state_delta_observation_id: str
    source_sandbox_execution_id: str
    source_direct_command_application_id: str
    sandbox_id: str
    direct_command: str
    handoff_status: str
    handoff_summary: str
    observation_available_for_task_outcome_evaluation: bool
    observation_available_for_learning_feedback: bool
    sense_observation_payload: dict
    outcome_evaluation_created: bool
    task_closure_created: bool
    learning_feedback_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HANDOFF_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be sense_interface_sandbox_observation_handoff_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be sense_interface")
        if self.target_engine != TARGET_ENGINE:
            raise ValueError("target_engine must be task_engine")
        if self.handoff_status not in ALLOWED_HANDOFF_STATUSES:
            raise ValueError(f"unknown handoff_status: {self.handoff_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SenseSandboxObservationHandoffRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class SenseSandboxObservationSafetyAudit:
    sense_observation_safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_sense_observation_id: str | None
    source_state_delta_observation_id: str | None
    source_sense_handoff_id: str | None
    source_sandbox_execution_id: str | None
    sandbox_execution_valid: bool
    pre_execution_snapshot_valid: bool
    sense_observation_valid: bool
    state_delta_observation_valid: bool
    handoff_valid: bool
    sense_only_observation_confirmed: bool
    no_outcome_evaluation: bool
    no_task_closure: bool
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
    no_execution_created_by_sense: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be sense_interface_sandbox_observation_safety_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be sense_interface")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SenseSandboxObservationSafetyAudit":
        return cls(**dict(data))


def build_sense_sandbox_execution_observation_record(
    *,
    sandbox_execution: SandboxExecutionRecord | dict[str, object],
    pre_execution_snapshot: SandboxPreExecutionSnapshot | dict[str, object] | None,
    direct_command_application: DirectCommandApplicationRecord | dict[str, object] | None = None,
    execution_audit: DirectCommandSandboxExecutionAudit | dict[str, object] | None = None,
    outcome_evaluation_created: bool = False,
    task_closure_created: bool = False,
    learning_feedback_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    candidate_ordering_changed: bool = False,
    selected_action_changed: bool = False,
    final_action_changed: bool = False,
    direct_command_changed: bool = False,
    execution_created_by_sense: bool = False,
) -> SenseSandboxExecutionObservationRecord:
    execution = _execution_record(sandbox_execution)
    snapshot = _snapshot_record(pre_execution_snapshot) if pre_execution_snapshot is not None else None
    command = (
        _direct_command_record(direct_command_application)
        if direct_command_application is not None
        else None
    )
    audit = _execution_audit_record(execution_audit) if execution_audit is not None else None
    forbidden_authority = any(
        (
            outcome_evaluation_created,
            task_closure_created,
            learning_feedback_created,
            memory_write_performed,
            automatic_learning_approval_created,
            candidate_ordering_changed,
            selected_action_changed,
            final_action_changed,
            direct_command_changed,
            execution_created_by_sense,
        )
    )
    if _external_execution_record(execution):
        status = "blocked_external_execution_record"
    elif not _sandbox_execution_valid(execution):
        status = "blocked_invalid_sandbox_execution"
    elif snapshot is None or not _snapshot_valid(snapshot):
        status = "blocked_missing_pre_execution_snapshot"
    elif forbidden_authority:
        status = "blocked_forbidden_authority_detected"
    else:
        status = "observation_record_created"
    before_state = dict(snapshot.sandbox_state_before_execution if snapshot else {})
    after_state = dict(execution.sandbox_state_after_execution)
    actor_before = _actor_position(before_state)
    actor_after = _actor_position(after_state)
    actor_changed = (
        None
        if actor_before is None or actor_after is None
        else actor_before != actor_after
    )
    boxes_before = _box_positions(before_state)
    boxes_after = _box_positions(after_state)
    box_changed = boxes_before != boxes_after
    contact = _observed_contact(execution.direct_command)
    contact_target = "box" if contact else None
    labels = (
        _visible_delta_labels(
            actor_changed=actor_changed,
            box_changed=box_changed,
            contact=contact,
        )
        if status == "observation_record_created"
        else ("unknown_visible_delta",)
    )
    return SenseSandboxExecutionObservationRecord(
        sense_observation_id=f"sense_sandbox_observation:{execution.sandbox_execution_id}",
        schema_version=OBSERVATION_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_sandbox_execution_id=execution.sandbox_execution_id,
        source_direct_command_application_id=execution.source_direct_command_application_id
        if command is None
        else command.direct_command_application_id,
        source_pre_execution_snapshot_id=(
            snapshot.pre_execution_snapshot_id if snapshot else execution.source_pre_execution_snapshot_id
        ),
        source_execution_audit_id=audit.direct_command_sandbox_execution_audit_id if audit else None,
        sandbox_id=execution.sandbox_id,
        direct_command=execution.direct_command,
        sense_observation_status=status,
        sense_observation_summary=_observation_summary(status),
        observed_actor_position_before=actor_before,
        observed_actor_position_after=actor_after,
        observed_actor_position_changed=actor_changed,
        observed_box_positions_before=boxes_before,
        observed_box_positions_after=boxes_after,
        observed_box_position_changed=box_changed,
        observed_goal_positions=_positions_from_state(before_state, "goal_positions"),
        observed_wall_positions=_positions_from_state(before_state, "wall_positions"),
        observed_contact=contact if status == "observation_record_created" else None,
        observed_contact_target=contact_target if status == "observation_record_created" else None,
        visible_state_delta_labels=labels,
        raw_observation_notes=_raw_observation_notes(execution, before_state, after_state),
        outcome_evaluation_created=outcome_evaluation_created,
        task_closure_created=task_closure_created,
        learning_feedback_created=learning_feedback_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        candidate_ordering_changed=candidate_ordering_changed,
        selected_action_changed=selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_changed=direct_command_changed,
        execution_created_by_sense=execution_created_by_sense,
        source_trace_refs=_combined_trace_refs(
            execution.source_trace_refs,
            snapshot.source_trace_refs if snapshot else (),
            command.source_trace_refs if command else (),
            audit.source_trace_refs if audit else (),
        ),
    )


def validate_sense_sandbox_execution_observation_record(
    observation: SenseSandboxExecutionObservationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _observation_record(observation)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_observation:{error}"]}
    errors: list[str] = []
    if record.sense_observation_status.startswith("blocked_"):
        errors.append(record.sense_observation_status)
    if any(label in FORBIDDEN_INTERPRETIVE_LABELS for label in record.visible_state_delta_labels):
        errors.append("forbidden_interpretive_label")
    for flag in (
        "outcome_evaluation_created",
        "task_closure_created",
        "learning_feedback_created",
        "memory_write_performed",
        "automatic_learning_approval_created",
        "candidate_ordering_changed",
        "selected_action_changed",
        "final_action_changed",
        "direct_command_changed",
        "execution_created_by_sense",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "sense_observation_id": record.sense_observation_id,
        "sense_observation_status": record.sense_observation_status,
    }


def build_sense_sandbox_state_delta_observation_record(
    *,
    sense_observation: SenseSandboxExecutionObservationRecord | dict[str, object],
    sandbox_execution: SandboxExecutionRecord | dict[str, object],
    pre_execution_snapshot: SandboxPreExecutionSnapshot | dict[str, object] | None,
    outcome_evaluation_created: bool = False,
    task_closure_created: bool = False,
    learning_feedback_created: bool = False,
    memory_write_performed: bool = False,
) -> SenseSandboxStateDeltaObservationRecord:
    observation = _observation_record(sense_observation)
    execution = _execution_record(sandbox_execution)
    snapshot = _snapshot_record(pre_execution_snapshot) if pre_execution_snapshot is not None else None
    observation_valid = validate_sense_sandbox_execution_observation_record(observation)[
        "valid"
    ]
    forbidden_authority = any(
        (
            outcome_evaluation_created,
            task_closure_created,
            learning_feedback_created,
            memory_write_performed,
        )
    )
    before_state = dict(snapshot.sandbox_state_before_execution if snapshot else {})
    after_state = dict(execution.sandbox_state_after_execution)
    delta_keys = _delta_keys(before_state, after_state)
    if forbidden_authority:
        status = "blocked_forbidden_authority_detected"
    elif not observation_valid:
        status = "blocked_invalid_observation"
    elif delta_keys:
        status = "state_delta_observed"
    else:
        status = "state_delta_observed_no_change"
    return SenseSandboxStateDeltaObservationRecord(
        state_delta_observation_id=f"sense_sandbox_state_delta:{observation.sense_observation_id}",
        schema_version=STATE_DELTA_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_sense_observation_id=observation.sense_observation_id,
        source_sandbox_execution_id=execution.sandbox_execution_id,
        sandbox_id=execution.sandbox_id,
        direct_command=execution.direct_command,
        raw_state_before=before_state,
        raw_state_after=after_state,
        observed_delta_keys=delta_keys,
        observed_delta_summary=_delta_summary(delta_keys),
        actor_delta={
            "before": _plain(observation.observed_actor_position_before),
            "after": _plain(observation.observed_actor_position_after),
            "changed": observation.observed_actor_position_changed,
        },
        box_delta={
            "before": _plain(observation.observed_box_positions_before),
            "after": _plain(observation.observed_box_positions_after),
            "changed": observation.observed_box_position_changed,
        },
        contact_delta={
            "contact_detected": observation.observed_contact,
            "contact_target": observation.observed_contact_target,
        },
        visibility_delta={"labels": _plain(observation.visible_state_delta_labels)},
        state_delta_status=status,
        outcome_evaluation_created=outcome_evaluation_created,
        task_closure_created=task_closure_created,
        learning_feedback_created=learning_feedback_created,
        memory_write_performed=memory_write_performed,
        source_trace_refs=_combined_trace_refs(
            observation.source_trace_refs,
            execution.source_trace_refs,
            snapshot.source_trace_refs if snapshot else (),
        ),
    )


def validate_sense_sandbox_state_delta_observation_record(
    state_delta: SenseSandboxStateDeltaObservationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _delta_record(state_delta)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_state_delta:{error}"]}
    errors: list[str] = []
    if record.state_delta_status.startswith("blocked_"):
        errors.append(record.state_delta_status)
    text = " ".join((record.observed_delta_summary, *record.observed_delta_keys))
    if any(label in text for label in FORBIDDEN_INTERPRETIVE_LABELS):
        errors.append("forbidden_interpretive_label")
    for flag in (
        "outcome_evaluation_created",
        "task_closure_created",
        "learning_feedback_created",
        "memory_write_performed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "state_delta_observation_id": record.state_delta_observation_id,
        "state_delta_status": record.state_delta_status,
    }


def build_sense_sandbox_observation_handoff_record(
    *,
    sense_observation: SenseSandboxExecutionObservationRecord | dict[str, object],
    state_delta_observation: SenseSandboxStateDeltaObservationRecord | dict[str, object],
    outcome_evaluation_created: bool = False,
    task_closure_created: bool = False,
    learning_feedback_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
) -> SenseSandboxObservationHandoffRecord:
    observation = _observation_record(sense_observation)
    delta = _delta_record(state_delta_observation)
    observation_valid = validate_sense_sandbox_execution_observation_record(observation)[
        "valid"
    ]
    delta_valid = validate_sense_sandbox_state_delta_observation_record(delta)["valid"]
    forbidden_authority = any(
        (
            outcome_evaluation_created,
            task_closure_created,
            learning_feedback_created,
            memory_write_performed,
            automatic_learning_approval_created,
        )
    )
    if forbidden_authority:
        status = "blocked_forbidden_authority_detected"
    elif not observation_valid:
        status = "blocked_invalid_sense_observation"
    elif not delta_valid:
        status = "blocked_invalid_state_delta_observation"
    elif observation.sense_observation_status == "observation_created_no_visible_delta":
        status = "handoff_created_no_visible_delta"
    else:
        status = "handoff_ready_for_task_outcome_evaluation"
    ready = status in {
        "handoff_ready_for_task_outcome_evaluation",
        "handoff_created_no_visible_delta",
    }
    return SenseSandboxObservationHandoffRecord(
        sense_handoff_id=f"sense_sandbox_handoff:{observation.sense_observation_id}",
        schema_version=HANDOFF_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        target_engine=TARGET_ENGINE,
        source_sense_observation_id=observation.sense_observation_id,
        source_state_delta_observation_id=delta.state_delta_observation_id,
        source_sandbox_execution_id=observation.source_sandbox_execution_id,
        source_direct_command_application_id=observation.source_direct_command_application_id,
        sandbox_id=observation.sandbox_id,
        direct_command=observation.direct_command,
        handoff_status=status,
        handoff_summary=_handoff_summary(status),
        observation_available_for_task_outcome_evaluation=ready,
        observation_available_for_learning_feedback=False,
        sense_observation_payload={
            "sense_observation": observation.to_dict(),
            "state_delta_observation": delta.to_dict(),
        },
        outcome_evaluation_created=outcome_evaluation_created,
        task_closure_created=task_closure_created,
        learning_feedback_created=learning_feedback_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        source_trace_refs=_combined_trace_refs(
            observation.source_trace_refs,
            delta.source_trace_refs,
        ),
    )


def validate_sense_sandbox_observation_handoff_record(
    handoff: SenseSandboxObservationHandoffRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _handoff_record(handoff)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_handoff:{error}"]}
    errors: list[str] = []
    ready = record.handoff_status in {
        "handoff_ready_for_task_outcome_evaluation",
        "handoff_created_no_visible_delta",
    }
    if record.handoff_status.startswith("blocked_"):
        errors.append(record.handoff_status)
    if record.observation_available_for_task_outcome_evaluation is not ready:
        errors.append("task_outcome_availability_mismatch")
    if record.observation_available_for_learning_feedback:
        errors.append("learning_feedback_availability_true")
    for flag in (
        "outcome_evaluation_created",
        "task_closure_created",
        "learning_feedback_created",
        "memory_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "sense_handoff_id": record.sense_handoff_id,
        "handoff_status": record.handoff_status,
    }


def build_sense_sandbox_observation_safety_audit(
    *,
    sandbox_execution: SandboxExecutionRecord | dict[str, object] | None,
    pre_execution_snapshot: SandboxPreExecutionSnapshot | dict[str, object] | None,
    sense_observation: SenseSandboxExecutionObservationRecord | dict[str, object] | None,
    state_delta_observation: SenseSandboxStateDeltaObservationRecord | dict[str, object] | None,
    handoff: SenseSandboxObservationHandoffRecord | dict[str, object] | None,
) -> SenseSandboxObservationSafetyAudit:
    execution = _execution_record(sandbox_execution) if sandbox_execution is not None else None
    snapshot = _snapshot_record(pre_execution_snapshot) if pre_execution_snapshot is not None else None
    observation = _observation_record(sense_observation) if sense_observation is not None else None
    delta = _delta_record(state_delta_observation) if state_delta_observation is not None else None
    handoff_record = _handoff_record(handoff) if handoff is not None else None
    sandbox_execution_valid = execution is not None and _sandbox_execution_valid(execution)
    snapshot_valid = snapshot is not None and _snapshot_valid(snapshot)
    observation_valid = (
        observation is not None
        and validate_sense_sandbox_execution_observation_record(observation)["valid"]
    )
    delta_valid = (
        delta is not None
        and validate_sense_sandbox_state_delta_observation_record(delta)["valid"]
    )
    handoff_valid = (
        handoff_record is not None
        and validate_sense_sandbox_observation_handoff_record(handoff_record)["valid"]
    )
    blocked_reasons = _safety_blocked_reasons(
        execution=execution,
        snapshot=snapshot,
        observation=observation,
        delta=delta,
        handoff=handoff_record,
        sandbox_execution_valid=sandbox_execution_valid,
        snapshot_valid=snapshot_valid,
        observation_valid=observation_valid,
        delta_valid=delta_valid,
        handoff_valid=handoff_valid,
    )
    return SenseSandboxObservationSafetyAudit(
        sense_observation_safety_audit_id=(
            "sense_sandbox_observation_safety_audit:"
            f"{observation.sense_observation_id if observation else 'unknown'}"
        ),
        schema_version=SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_sense_observation_id=observation.sense_observation_id if observation else None,
        source_state_delta_observation_id=delta.state_delta_observation_id if delta else None,
        source_sense_handoff_id=handoff_record.sense_handoff_id if handoff_record else None,
        source_sandbox_execution_id=execution.sandbox_execution_id if execution else None,
        sandbox_execution_valid=sandbox_execution_valid,
        pre_execution_snapshot_valid=snapshot_valid,
        sense_observation_valid=observation_valid,
        state_delta_observation_valid=delta_valid,
        handoff_valid=handoff_valid,
        sense_only_observation_confirmed=True,
        no_outcome_evaluation=not _outcome_evaluation_created(
            observation,
            delta,
            handoff_record,
        ),
        no_task_closure=not _task_closure_created(observation, delta, handoff_record),
        no_learning_feedback=not _learning_feedback_created(
            observation,
            delta,
            handoff_record,
        ),
        no_memory_write=not _memory_write_performed(observation, delta, handoff_record),
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_automatic_learning_approval=not (
            (observation.automatic_learning_approval_created if observation else False)
            or (
                handoff_record.automatic_learning_approval_created
                if handoff_record
                else False
            )
        ),
        no_candidate_ordering_change=not (
            observation.candidate_ordering_changed if observation else False
        ),
        no_selected_action_change=not (
            observation.selected_action_changed if observation else False
        ),
        no_final_action_change=not (
            observation.final_action_changed if observation else False
        ),
        no_direct_command_change=not (
            observation.direct_command_changed if observation else False
        ),
        no_execution_created_by_sense=not (
            observation.execution_created_by_sense if observation else False
        ),
        audit_status=_safety_audit_status(blocked_reasons, observation=observation),
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(blocked_reasons),
        source_trace_refs=_combined_trace_refs(
            execution.source_trace_refs if execution else (),
            snapshot.source_trace_refs if snapshot else (),
            observation.source_trace_refs if observation else (),
            delta.source_trace_refs if delta else (),
            handoff_record.source_trace_refs if handoff_record else (),
        ),
    )


def validate_sense_sandbox_observation_safety_audit(
    audit: SenseSandboxObservationSafetyAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _safety_audit_record(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status not in {
        "passed_sense_observation_handoff",
        "passed_observation_created_no_visible_delta",
    }:
        errors.append(record.audit_status)
    for flag in (
        "sense_only_observation_confirmed",
        "no_outcome_evaluation",
        "no_task_closure",
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
        "no_execution_created_by_sense",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    if not set(BLOCKED_CLAIMS).issubset(set(record.blocked_claims)):
        errors.append("blocked_claims_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "sense_observation_safety_audit_id": record.sense_observation_safety_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_demo_sense_sandbox_observation_handoff() -> dict[str, object]:
    return _build_observation_bundle()


def build_demo_sense_sandbox_observation_safety_audit() -> SenseSandboxObservationSafetyAudit:
    payload = build_demo_sense_sandbox_observation_handoff()
    return SenseSandboxObservationSafetyAudit.from_dict(
        payload["sense_sandbox_observation_safety_audit"]
    )


def build_demo_blocked_invalid_sandbox_execution_observation() -> dict[str, object]:
    return _build_observation_bundle(
        package85_payload=build_demo_blocked_direct_command_sandbox_execution(
            "teacher-rejected"
        )
    )


def build_demo_blocked_missing_pre_execution_snapshot_observation() -> dict[str, object]:
    return _build_observation_bundle(missing_snapshot=True)


def build_demo_blocked_external_execution_observation() -> dict[str, object]:
    return _build_observation_bundle(
        package85_payload=build_demo_blocked_direct_command_sandbox_execution(
            "external-execution"
        )
    )


def build_demo_blocked_outcome_evaluation_created_observation() -> dict[str, object]:
    return _build_observation_bundle(outcome_evaluation_created=True)


def build_demo_blocked_task_closure_created_observation() -> dict[str, object]:
    return _build_observation_bundle(task_closure_created=True)


def build_demo_blocked_learning_feedback_created_observation() -> dict[str, object]:
    return _build_observation_bundle(learning_feedback_created=True)


def build_demo_blocked_memory_write_observation() -> dict[str, object]:
    return _build_observation_bundle(memory_write_performed=True)


def build_demo_blocked_action_authority_observation() -> dict[str, object]:
    return _build_observation_bundle(candidate_ordering_changed=True)


def build_demo_blocked_sense_sandbox_observation(case: str) -> dict[str, object]:
    builders = {
        "invalid-sandbox-execution": build_demo_blocked_invalid_sandbox_execution_observation,
        "missing-pre-execution-snapshot": build_demo_blocked_missing_pre_execution_snapshot_observation,
        "external-execution-record": build_demo_blocked_external_execution_observation,
        "outcome-evaluation-created": build_demo_blocked_outcome_evaluation_created_observation,
        "task-closure-created": build_demo_blocked_task_closure_created_observation,
        "learning-feedback-created": build_demo_blocked_learning_feedback_created_observation,
        "memory-write-detected": build_demo_blocked_memory_write_observation,
        "action-authority-detected": build_demo_blocked_action_authority_observation,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown sense sandbox observation blocked case: {case}") from error


def _build_observation_bundle(
    *,
    package85_payload: dict[str, object] | None = None,
    missing_snapshot: bool = False,
    outcome_evaluation_created: bool = False,
    task_closure_created: bool = False,
    learning_feedback_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    candidate_ordering_changed: bool = False,
    selected_action_changed: bool = False,
    final_action_changed: bool = False,
    direct_command_changed: bool = False,
    execution_created_by_sense: bool = False,
) -> dict[str, object]:
    package85_payload = package85_payload or build_demo_direct_command_sandbox_execution()
    execution = SandboxExecutionRecord.from_dict(package85_payload["sandbox_execution"])
    snapshot = (
        None
        if missing_snapshot
        else SandboxPreExecutionSnapshot.from_dict(
            package85_payload["sandbox_pre_execution_snapshot"]
        )
        if package85_payload.get("sandbox_pre_execution_snapshot") is not None
        else None
    )
    direct_command = DirectCommandApplicationRecord.from_dict(
        package85_payload["direct_command_application"]
    )
    execution_audit = DirectCommandSandboxExecutionAudit.from_dict(
        package85_payload["direct_command_sandbox_execution_audit"]
    )
    observation = build_sense_sandbox_execution_observation_record(
        sandbox_execution=execution,
        pre_execution_snapshot=snapshot,
        direct_command_application=direct_command,
        execution_audit=execution_audit,
        outcome_evaluation_created=outcome_evaluation_created,
        task_closure_created=task_closure_created,
        learning_feedback_created=learning_feedback_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        candidate_ordering_changed=candidate_ordering_changed,
        selected_action_changed=selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_changed=direct_command_changed,
        execution_created_by_sense=execution_created_by_sense,
    )
    state_delta = build_sense_sandbox_state_delta_observation_record(
        sense_observation=observation,
        sandbox_execution=execution,
        pre_execution_snapshot=snapshot,
        outcome_evaluation_created=outcome_evaluation_created,
        task_closure_created=task_closure_created,
        learning_feedback_created=learning_feedback_created,
        memory_write_performed=memory_write_performed,
    )
    handoff = build_sense_sandbox_observation_handoff_record(
        sense_observation=observation,
        state_delta_observation=state_delta,
        outcome_evaluation_created=outcome_evaluation_created,
        task_closure_created=task_closure_created,
        learning_feedback_created=learning_feedback_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
    )
    safety_audit = build_sense_sandbox_observation_safety_audit(
        sandbox_execution=execution,
        pre_execution_snapshot=snapshot,
        sense_observation=observation,
        state_delta_observation=state_delta,
        handoff=handoff,
    )
    return {
        "sense_sandbox_execution_observation": observation.to_dict(),
        "sense_sandbox_state_delta_observation": state_delta.to_dict(),
        "sense_sandbox_observation_handoff": handoff.to_dict(),
        "sense_sandbox_observation_safety_audit": safety_audit.to_dict(),
        "sense_sandbox_execution_observation_validation": (
            validate_sense_sandbox_execution_observation_record(observation)
        ),
        "sense_sandbox_state_delta_observation_validation": (
            validate_sense_sandbox_state_delta_observation_record(state_delta)
        ),
        "sense_sandbox_observation_handoff_validation": (
            validate_sense_sandbox_observation_handoff_record(handoff)
        ),
        "sense_sandbox_observation_safety_audit_validation": (
            validate_sense_sandbox_observation_safety_audit(safety_audit)
        ),
        "source_package85_execution": execution.to_dict(),
        "safe_claim": SAFE_CLAIM,
    }


def _sandbox_execution_valid(execution: SandboxExecutionRecord) -> bool:
    return (
        execution.execution_status == "bounded_sandbox_execution_completed"
        and execution.bounded_sandbox_execution_created
        and not execution.external_execution_created
        and not execution.unity_execution_created
        and not execution.bridge_execution_created
        and not execution.network_execution_created
        and not execution.filesystem_execution_created
        and not execution.memory_layer_write_performed
        and validate_sandbox_execution_record(execution)["valid"]
    )


def _snapshot_valid(snapshot: SandboxPreExecutionSnapshot) -> bool:
    return (
        snapshot.snapshot_status == "snapshot_created"
        and snapshot.restore_possible
        and validate_sandbox_pre_execution_snapshot(snapshot)["valid"]
    )


def _external_execution_record(execution: SandboxExecutionRecord) -> bool:
    return any(
        (
            execution.external_execution_created,
            execution.unity_execution_created,
            execution.bridge_execution_created,
            execution.network_execution_created,
            execution.filesystem_execution_created,
        )
    )


def _actor_position(state: dict[str, object]) -> tuple[int, int] | None:
    actor_position = _position(state.get("actor_position"))
    if actor_position is not None:
        return actor_position
    if isinstance(state.get("position"), int):
        return (int(state["position"]), 0)
    if isinstance(state.get("x"), int) and isinstance(state.get("y"), int):
        return (int(state["x"]), int(state["y"]))
    return None


def _box_positions(state: dict[str, object]) -> tuple[tuple[int, int], ...]:
    positions = _positions_from_state(state, "box_positions")
    if positions:
        return positions
    return _tuple_positions(state.get("box_position"))


def _positions_from_state(state: dict[str, object], key: str) -> tuple[tuple[int, int], ...]:
    return _tuple_positions(state.get(key))


def _observed_contact(direct_command: str) -> bool:
    return direct_command.startswith("push_")


def _visible_delta_labels(
    *,
    actor_changed: bool | None,
    box_changed: bool,
    contact: bool,
) -> tuple[str, ...]:
    labels: list[str] = []
    if actor_changed is True:
        labels.append("actor_position_changed")
    elif actor_changed is False:
        labels.append("actor_position_unchanged")
    if box_changed:
        labels.append("box_position_changed")
    else:
        labels.append("box_position_unchanged")
    labels.append("contact_detected" if contact else "no_contact_detected")
    if actor_changed is not True and not box_changed and not contact:
        labels.append("visible_no_change")
    if not labels:
        labels.append("unknown_visible_delta")
    return tuple(labels)


def _raw_observation_notes(
    execution: SandboxExecutionRecord,
    before_state: dict[str, object],
    after_state: dict[str, object],
) -> tuple[str, ...]:
    return (
        f"direct_command={execution.direct_command}",
        f"observed_raw_delta_keys={','.join(_delta_keys(before_state, after_state))}",
        "sense_observation_only_no_outcome_evaluation",
    )


def _delta_keys(before_state: dict[str, object], after_state: dict[str, object]) -> tuple[str, ...]:
    keys = sorted(set(before_state) | set(after_state))
    return tuple(key for key in keys if before_state.get(key) != after_state.get(key))


def _delta_summary(delta_keys: tuple[str, ...]) -> str:
    if not delta_keys:
        return "No raw sandbox state keys changed."
    return "Raw sandbox state keys changed: " + ", ".join(delta_keys) + "."


def _observation_summary(status: str) -> str:
    if status == "observation_record_created":
        return "Sense Interface created descriptive sandbox execution observation."
    if status == "observation_created_no_visible_delta":
        return "Sense Interface created observation with no visible delta."
    return f"Sense observation blocked: {status}."


def _handoff_summary(status: str) -> str:
    if status == "handoff_ready_for_task_outcome_evaluation":
        return "Sense observation handoff is ready for later Task Engine outcome evaluation."
    if status == "handoff_created_no_visible_delta":
        return "Sense observation handoff created for no-visible-delta observation."
    return f"Sense observation handoff blocked: {status}."


def _safety_blocked_reasons(
    *,
    execution: SandboxExecutionRecord | None,
    snapshot: SandboxPreExecutionSnapshot | None,
    observation: SenseSandboxExecutionObservationRecord | None,
    delta: SenseSandboxStateDeltaObservationRecord | None,
    handoff: SenseSandboxObservationHandoffRecord | None,
    sandbox_execution_valid: bool,
    snapshot_valid: bool,
    observation_valid: bool,
    delta_valid: bool,
    handoff_valid: bool,
) -> list[str]:
    reasons: list[str] = []
    if not sandbox_execution_valid:
        reasons.append("invalid_sandbox_execution")
    if snapshot is None or not snapshot_valid:
        reasons.append("missing_pre_execution_snapshot")
    if observation is None or not observation_valid:
        reasons.append("invalid_sense_observation")
    if delta is None or not delta_valid:
        reasons.append("invalid_state_delta_observation")
    if handoff is None or not handoff_valid:
        reasons.append("invalid_handoff")
    if _outcome_evaluation_created(observation, delta, handoff):
        reasons.append("outcome_evaluation_created")
    if _task_closure_created(observation, delta, handoff):
        reasons.append("task_closure_created")
    if _learning_feedback_created(observation, delta, handoff):
        reasons.append("learning_feedback_created")
    if _memory_write_performed(observation, delta, handoff):
        reasons.append("memory_write_performed")
    if observation is not None and any(
        (
            observation.candidate_ordering_changed,
            observation.selected_action_changed,
            observation.final_action_changed,
            observation.direct_command_changed,
            observation.execution_created_by_sense,
        )
    ):
        reasons.append("action_authority_changed")
    return reasons


def _safety_audit_status(
    blocked_reasons: list[str],
    *,
    observation: SenseSandboxExecutionObservationRecord | None,
) -> str:
    if "outcome_evaluation_created" in blocked_reasons:
        return "blocked_outcome_evaluation_detected"
    if "task_closure_created" in blocked_reasons:
        return "blocked_task_closure_detected"
    if "learning_feedback_created" in blocked_reasons:
        return "blocked_learning_feedback_detected"
    if "memory_write_performed" in blocked_reasons:
        return "blocked_memory_write_detected"
    if "action_authority_changed" in blocked_reasons:
        return "blocked_action_authority_detected"
    if "invalid_sandbox_execution" in blocked_reasons:
        return "blocked_invalid_sandbox_execution"
    if "missing_pre_execution_snapshot" in blocked_reasons:
        return "blocked_missing_pre_execution_snapshot"
    if "invalid_sense_observation" in blocked_reasons:
        return "blocked_invalid_sense_observation"
    if "invalid_state_delta_observation" in blocked_reasons:
        return "blocked_invalid_state_delta_observation"
    if "invalid_handoff" in blocked_reasons:
        return "blocked_invalid_handoff"
    if (
        observation is not None
        and observation.sense_observation_status == "observation_created_no_visible_delta"
    ):
        return "passed_observation_created_no_visible_delta"
    return "passed_sense_observation_handoff"


def _outcome_evaluation_created(
    observation: SenseSandboxExecutionObservationRecord | None,
    delta: SenseSandboxStateDeltaObservationRecord | None,
    handoff: SenseSandboxObservationHandoffRecord | None,
) -> bool:
    return bool(
        (observation.outcome_evaluation_created if observation else False)
        or (delta.outcome_evaluation_created if delta else False)
        or (handoff.outcome_evaluation_created if handoff else False)
    )


def _task_closure_created(
    observation: SenseSandboxExecutionObservationRecord | None,
    delta: SenseSandboxStateDeltaObservationRecord | None,
    handoff: SenseSandboxObservationHandoffRecord | None,
) -> bool:
    return bool(
        (observation.task_closure_created if observation else False)
        or (delta.task_closure_created if delta else False)
        or (handoff.task_closure_created if handoff else False)
    )


def _learning_feedback_created(
    observation: SenseSandboxExecutionObservationRecord | None,
    delta: SenseSandboxStateDeltaObservationRecord | None,
    handoff: SenseSandboxObservationHandoffRecord | None,
) -> bool:
    return bool(
        (observation.learning_feedback_created if observation else False)
        or (delta.learning_feedback_created if delta else False)
        or (handoff.learning_feedback_created if handoff else False)
    )


def _memory_write_performed(
    observation: SenseSandboxExecutionObservationRecord | None,
    delta: SenseSandboxStateDeltaObservationRecord | None,
    handoff: SenseSandboxObservationHandoffRecord | None,
) -> bool:
    return bool(
        (observation.memory_write_performed if observation else False)
        or (delta.memory_write_performed if delta else False)
        or (handoff.memory_write_performed if handoff else False)
    )


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _execution_record(record: SandboxExecutionRecord | dict[str, object]) -> SandboxExecutionRecord:
    return (
        record
        if isinstance(record, SandboxExecutionRecord)
        else SandboxExecutionRecord.from_dict(dict(record))
    )


def _snapshot_record(
    record: SandboxPreExecutionSnapshot | dict[str, object],
) -> SandboxPreExecutionSnapshot:
    return (
        record
        if isinstance(record, SandboxPreExecutionSnapshot)
        else SandboxPreExecutionSnapshot.from_dict(dict(record))
    )


def _direct_command_record(
    record: DirectCommandApplicationRecord | dict[str, object],
) -> DirectCommandApplicationRecord:
    return (
        record
        if isinstance(record, DirectCommandApplicationRecord)
        else DirectCommandApplicationRecord.from_dict(dict(record))
    )


def _execution_audit_record(
    record: DirectCommandSandboxExecutionAudit | dict[str, object],
) -> DirectCommandSandboxExecutionAudit:
    return (
        record
        if isinstance(record, DirectCommandSandboxExecutionAudit)
        else DirectCommandSandboxExecutionAudit.from_dict(dict(record))
    )


def _observation_record(
    record: SenseSandboxExecutionObservationRecord | dict[str, object],
) -> SenseSandboxExecutionObservationRecord:
    return (
        record
        if isinstance(record, SenseSandboxExecutionObservationRecord)
        else SenseSandboxExecutionObservationRecord.from_dict(dict(record))
    )


def _delta_record(
    record: SenseSandboxStateDeltaObservationRecord | dict[str, object],
) -> SenseSandboxStateDeltaObservationRecord:
    return (
        record
        if isinstance(record, SenseSandboxStateDeltaObservationRecord)
        else SenseSandboxStateDeltaObservationRecord.from_dict(dict(record))
    )


def _handoff_record(
    record: SenseSandboxObservationHandoffRecord | dict[str, object],
) -> SenseSandboxObservationHandoffRecord:
    return (
        record
        if isinstance(record, SenseSandboxObservationHandoffRecord)
        else SenseSandboxObservationHandoffRecord.from_dict(dict(record))
    )


def _safety_audit_record(
    record: SenseSandboxObservationSafetyAudit | dict[str, object],
) -> SenseSandboxObservationSafetyAudit:
    return (
        record
        if isinstance(record, SenseSandboxObservationSafetyAudit)
        else SenseSandboxObservationSafetyAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
