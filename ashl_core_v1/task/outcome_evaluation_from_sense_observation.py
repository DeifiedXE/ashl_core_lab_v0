"""Task outcome evaluation from Sense Interface sandbox observation handoff."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

SOURCE_ENGINE = "task_engine"

EXPECTED_EFFECT_SCHEMA_VERSION = "task_engine_expected_effect_reference_v0"
OUTCOME_EVALUATION_SCHEMA_VERSION = (
    "task_engine_outcome_evaluation_from_sense_observation_v0"
)
GOAL_DELTA_SCHEMA_VERSION = "task_engine_goal_delta_evaluation_v0"
SAFETY_AUDIT_SCHEMA_VERSION = "task_engine_outcome_evaluation_safety_audit_v0"

SAFE_CLAIM = (
    "ASHL Core v1 Task Engine can evaluate bounded sandbox execution outcomes "
    "from Sense Interface observation handoff by comparing deterministic expected "
    "effects, observed state deltas, and task goal context, while avoiding task "
    "closure, learning feedback, memory writes, action authority changes, or "
    "automatic learning approval."
)
BLOCKED_CLAIMS = (
    "no_task_closure",
    "no_learning_feedback",
    "no_memory_write",
    "no_action_authority_change",
    "no_automatic_learning_approval",
)

DIRECT_COMMAND_EXPECTED_EFFECTS = {
    "observe": "observe_environment",
    "step_forward": "actor_moves_forward",
    "turn_left": "actor_turns_left",
    "turn_right": "actor_turns_right",
    "push_right": "box_moves_right",
    "push_left": "box_moves_left",
    "wait": "wait_no_required_delta",
}
ALLOWED_EXPECTED_EFFECTS = {
    "observe_environment",
    "actor_moves_forward",
    "actor_turns_left",
    "actor_turns_right",
    "box_moves_right",
    "box_moves_left",
    "wait_no_required_delta",
    "unknown_expected_effect",
}
ALLOWED_EXPECTED_EFFECT_SOURCES = {
    "task_working_memory_explicit",
    "deterministic_direct_command_mapping",
    "unknown",
}
ALLOWED_EXPECTED_EFFECT_STATUSES = {
    "expected_effect_resolved",
    "expected_effect_unknown",
    "blocked_invalid_direct_command",
    "blocked_invalid_sense_handoff",
}
ALLOWED_OUTCOME_CLASSES = {
    "expected_effect_matched",
    "expected_effect_not_matched",
    "observation_only",
    "no_visible_change",
    "unknown_expected_effect",
    "unknown_observation",
    "system_fault",
}
ALLOWED_EVALUATION_STATUSES = {
    "outcome_evaluated",
    "outcome_evaluated_no_visible_delta",
    "outcome_unknown_missing_expected_effect",
    "outcome_unknown_missing_observation",
    "blocked_invalid_sense_handoff",
    "blocked_invalid_expected_effect",
    "blocked_forbidden_authority_detected",
}
ALLOWED_GOAL_DELTA_CLASSES = {
    "closer_to_goal",
    "goal_reached",
    "no_progress",
    "regressed",
    "not_applicable",
    "unknown",
    "system_fault",
}
ALLOWED_GOAL_DELTA_STATUSES = {
    "goal_delta_evaluated",
    "goal_delta_not_applicable",
    "goal_delta_unknown_missing_goal",
    "goal_delta_unknown_missing_observation",
    "blocked_invalid_outcome_evaluation",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_outcome_evaluation_only",
    "passed_outcome_unknown",
    "blocked_invalid_sense_handoff",
    "blocked_invalid_expected_effect_reference",
    "blocked_invalid_outcome_evaluation",
    "blocked_invalid_goal_delta_evaluation",
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


@dataclass(frozen=True)
class TaskExpectedEffectReferenceRecord:
    expected_effect_reference_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_final_action_application_id: str | None
    source_direct_command_application_id: str | None
    source_sense_handoff_id: str
    direct_command: str | None
    final_action_candidate_id: str | None
    expected_effect: str
    expected_effect_source: str
    expected_effect_summary: str
    expected_effect_status: str
    task_goal_id: str | None
    task_goal_summary: str | None
    outcome_evaluation_created: bool
    task_closure_created: bool
    learning_feedback_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EXPECTED_EFFECT_SCHEMA_VERSION:
            raise ValueError("schema_version must be task_engine_expected_effect_reference_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.expected_effect not in ALLOWED_EXPECTED_EFFECTS:
            raise ValueError(f"unknown expected_effect: {self.expected_effect}")
        if self.expected_effect_source not in ALLOWED_EXPECTED_EFFECT_SOURCES:
            raise ValueError(f"unknown expected_effect_source: {self.expected_effect_source}")
        if self.expected_effect_status not in ALLOWED_EXPECTED_EFFECT_STATUSES:
            raise ValueError(f"unknown expected_effect_status: {self.expected_effect_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TaskExpectedEffectReferenceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskExecutionOutcomeEvaluationRecord:
    outcome_evaluation_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_sense_observation_id: str
    source_state_delta_observation_id: str
    source_sense_handoff_id: str
    source_expected_effect_reference_id: str
    source_sandbox_execution_id: str
    source_direct_command_application_id: str | None
    direct_command: str | None
    expected_effect: str
    observed_delta_labels: tuple[str, ...]
    observed_actor_position_changed: bool | None
    observed_box_position_changed: bool | None
    observed_contact: bool | None
    observed_contact_target: str | None
    expected_effect_matched: bool | None
    expected_effect_failed: bool | None
    outcome_class: str
    outcome_summary: str
    outcome_reason: str
    evaluation_status: str
    available_for_task_closure: bool
    available_for_learning_feedback_candidate_later: bool
    task_closure_created: bool
    learning_feedback_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created_by_evaluation: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != OUTCOME_EVALUATION_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_outcome_evaluation_from_sense_observation_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.outcome_class not in ALLOWED_OUTCOME_CLASSES:
            raise ValueError(f"unknown outcome_class: {self.outcome_class}")
        if self.evaluation_status not in ALLOWED_EVALUATION_STATUSES:
            raise ValueError(f"unknown evaluation_status: {self.evaluation_status}")
        for name in ("observed_delta_labels", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TaskExecutionOutcomeEvaluationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskGoalDeltaEvaluationRecord:
    goal_delta_evaluation_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_working_memory_id: str
    source_outcome_evaluation_id: str
    source_sense_handoff_id: str
    task_goal_id: str | None
    task_goal_summary: str | None
    goal_delta_status: str
    goal_delta_class: str
    goal_delta_summary: str
    goal_delta_reason: str
    goal_reached: bool | None
    progress_toward_goal_detected: bool | None
    regression_from_goal_detected: bool | None
    available_for_task_closure: bool
    available_for_learning_feedback_candidate_later: bool
    task_closure_created: bool
    learning_feedback_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != GOAL_DELTA_SCHEMA_VERSION:
            raise ValueError("schema_version must be task_engine_goal_delta_evaluation_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.goal_delta_class not in ALLOWED_GOAL_DELTA_CLASSES:
            raise ValueError(f"unknown goal_delta_class: {self.goal_delta_class}")
        if self.goal_delta_status not in ALLOWED_GOAL_DELTA_STATUSES:
            raise ValueError(f"unknown goal_delta_status: {self.goal_delta_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TaskGoalDeltaEvaluationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskOutcomeEvaluationSafetyAudit:
    outcome_evaluation_safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_outcome_evaluation_id: str | None
    source_goal_delta_evaluation_id: str | None
    source_expected_effect_reference_id: str | None
    source_sense_handoff_id: str | None
    sense_handoff_valid: bool
    expected_effect_reference_valid: bool
    outcome_evaluation_valid: bool
    goal_delta_evaluation_valid: bool
    evaluation_only_confirmed: bool
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
    no_execution_created_by_evaluation: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be task_engine_outcome_evaluation_safety_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TaskOutcomeEvaluationSafetyAudit":
        return cls(**dict(data))


def expected_effect_for_direct_command(direct_command: str | None) -> str:
    return DIRECT_COMMAND_EXPECTED_EFFECTS.get(
        direct_command or "",
        "unknown_expected_effect",
    )


def build_task_expected_effect_reference_record(
    *,
    sense_handoff: SenseSandboxObservationHandoffRecord | dict[str, object],
    explicit_expected_effect: str | None = None,
    task_goal_id: str | None = None,
    task_goal_summary: str | None = None,
    source_final_action_application_id: str | None = None,
) -> TaskExpectedEffectReferenceRecord:
    handoff = _handoff_record(sense_handoff)
    handoff_valid = _handoff_valid(handoff)
    if not handoff_valid:
        effect = "unknown_expected_effect"
        source = "unknown"
        status = "blocked_invalid_sense_handoff"
    elif explicit_expected_effect is not None:
        effect = explicit_expected_effect if explicit_expected_effect in ALLOWED_EXPECTED_EFFECTS else "unknown_expected_effect"
        source = "task_working_memory_explicit" if effect != "unknown_expected_effect" else "unknown"
        status = "expected_effect_resolved" if effect != "unknown_expected_effect" else "expected_effect_unknown"
    else:
        effect = expected_effect_for_direct_command(handoff.direct_command)
        source = (
            "deterministic_direct_command_mapping"
            if effect != "unknown_expected_effect"
            else "unknown"
        )
        status = (
            "expected_effect_resolved"
            if effect != "unknown_expected_effect"
            else "expected_effect_unknown"
        )
    return TaskExpectedEffectReferenceRecord(
        expected_effect_reference_id=f"task_expected_effect:{handoff.sense_handoff_id}",
        schema_version=EXPECTED_EFFECT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=_task_working_memory_id_from_handoff(handoff),
        source_final_action_application_id=source_final_action_application_id,
        source_direct_command_application_id=handoff.source_direct_command_application_id,
        source_sense_handoff_id=handoff.sense_handoff_id,
        direct_command=handoff.direct_command,
        final_action_candidate_id=None,
        expected_effect=effect,
        expected_effect_source=source,
        expected_effect_summary=_expected_effect_summary(effect, source),
        expected_effect_status=status,
        task_goal_id=task_goal_id,
        task_goal_summary=task_goal_summary,
        outcome_evaluation_created=False,
        task_closure_created=False,
        learning_feedback_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=handoff.source_trace_refs,
    )


def validate_task_expected_effect_reference_record(
    reference: TaskExpectedEffectReferenceRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _reference_record(reference)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_expected_effect:{error}"]}
    errors: list[str] = []
    if record.expected_effect_status.startswith("blocked_"):
        errors.append(record.expected_effect_status)
    if record.expected_effect_status == "expected_effect_resolved" and record.expected_effect == "unknown_expected_effect":
        errors.append("resolved_effect_unknown")
    if record.expected_effect_status == "expected_effect_unknown" and record.expected_effect != "unknown_expected_effect":
        errors.append("unknown_status_with_known_effect")
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
        "expected_effect_reference_id": record.expected_effect_reference_id,
        "expected_effect_status": record.expected_effect_status,
    }


def build_task_execution_outcome_evaluation_record(
    *,
    sense_handoff: SenseSandboxObservationHandoffRecord | dict[str, object],
    expected_effect_reference: TaskExpectedEffectReferenceRecord | dict[str, object],
    task_closure_created: bool = False,
    learning_feedback_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    candidate_ordering_changed: bool = False,
    selected_action_changed: bool = False,
    final_action_changed: bool = False,
    direct_command_changed: bool = False,
    execution_created_by_evaluation: bool = False,
) -> TaskExecutionOutcomeEvaluationRecord:
    handoff = _handoff_record(sense_handoff)
    reference = _reference_record(expected_effect_reference)
    handoff_valid = _handoff_valid(handoff)
    reference_valid = validate_task_expected_effect_reference_record(reference)["valid"]
    observation = _observation_from_handoff(handoff)
    delta = _delta_from_handoff(handoff)
    forbidden_authority = any(
        (
            task_closure_created,
            learning_feedback_created,
            memory_write_performed,
            automatic_learning_approval_created,
            candidate_ordering_changed,
            selected_action_changed,
            final_action_changed,
            direct_command_changed,
            execution_created_by_evaluation,
        )
    )
    if forbidden_authority:
        outcome_class = "system_fault"
        matched = None
        failed = None
        status = "blocked_forbidden_authority_detected"
    elif not handoff_valid:
        outcome_class = "unknown_observation"
        matched = None
        failed = None
        status = "blocked_invalid_sense_handoff"
    elif not reference_valid:
        outcome_class = "unknown_expected_effect"
        matched = None
        failed = None
        status = "blocked_invalid_expected_effect"
    elif observation is None:
        outcome_class = "unknown_observation"
        matched = None
        failed = None
        status = "outcome_unknown_missing_observation"
    else:
        outcome_class, matched, failed, status = _evaluate_observation(
            expected_effect=reference.expected_effect,
            observation=observation,
        )
    available = status in {"outcome_evaluated", "outcome_evaluated_no_visible_delta"}
    return TaskExecutionOutcomeEvaluationRecord(
        outcome_evaluation_id=f"task_outcome_evaluation:{handoff.sense_handoff_id}",
        schema_version=OUTCOME_EVALUATION_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=reference.source_task_working_memory_id,
        source_sense_observation_id=observation.sense_observation_id if observation else "missing:sense_observation",
        source_state_delta_observation_id=delta.state_delta_observation_id if delta else "missing:state_delta",
        source_sense_handoff_id=handoff.sense_handoff_id,
        source_expected_effect_reference_id=reference.expected_effect_reference_id,
        source_sandbox_execution_id=handoff.source_sandbox_execution_id,
        source_direct_command_application_id=handoff.source_direct_command_application_id,
        direct_command=handoff.direct_command,
        expected_effect=reference.expected_effect,
        observed_delta_labels=observation.visible_state_delta_labels if observation else (),
        observed_actor_position_changed=observation.observed_actor_position_changed if observation else None,
        observed_box_position_changed=observation.observed_box_position_changed if observation else None,
        observed_contact=observation.observed_contact if observation else None,
        observed_contact_target=observation.observed_contact_target if observation else None,
        expected_effect_matched=matched,
        expected_effect_failed=failed,
        outcome_class=outcome_class,
        outcome_summary=_outcome_summary(outcome_class),
        outcome_reason=_outcome_reason(reference.expected_effect, observation),
        evaluation_status=status,
        available_for_task_closure=available,
        available_for_learning_feedback_candidate_later=available,
        task_closure_created=task_closure_created,
        learning_feedback_created=learning_feedback_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        candidate_ordering_changed=candidate_ordering_changed,
        selected_action_changed=selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_changed=direct_command_changed,
        execution_created_by_evaluation=execution_created_by_evaluation,
        source_trace_refs=_combined_trace_refs(
            handoff.source_trace_refs,
            reference.source_trace_refs,
            observation.source_trace_refs if observation else (),
            delta.source_trace_refs if delta else (),
        ),
    )


def validate_task_execution_outcome_evaluation_record(
    outcome: TaskExecutionOutcomeEvaluationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _outcome_record(outcome)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_outcome_evaluation:{error}"]}
    errors: list[str] = []
    if record.evaluation_status.startswith("blocked_"):
        errors.append(record.evaluation_status)
    if record.outcome_class == "expected_effect_matched" and record.expected_effect_matched is not True:
        errors.append("matched_class_without_match")
    if record.outcome_class == "expected_effect_not_matched" and record.expected_effect_failed is not True:
        errors.append("not_matched_class_without_failure")
    for flag in (
        "task_closure_created",
        "learning_feedback_created",
        "memory_write_performed",
        "automatic_learning_approval_created",
        "candidate_ordering_changed",
        "selected_action_changed",
        "final_action_changed",
        "direct_command_changed",
        "execution_created_by_evaluation",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "outcome_evaluation_id": record.outcome_evaluation_id,
        "evaluation_status": record.evaluation_status,
        "outcome_class": record.outcome_class,
    }


def build_task_goal_delta_evaluation_record(
    *,
    outcome_evaluation: TaskExecutionOutcomeEvaluationRecord | dict[str, object],
    sense_handoff: SenseSandboxObservationHandoffRecord | dict[str, object],
    task_goal_id: str | None = None,
    task_goal_summary: str | None = None,
    deterministic_goal_progress: bool | None = None,
    deterministic_goal_reached: bool | None = None,
    deterministic_goal_regressed: bool | None = None,
    task_closure_created: bool = False,
    learning_feedback_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
) -> TaskGoalDeltaEvaluationRecord:
    outcome = _outcome_record(outcome_evaluation)
    handoff = _handoff_record(sense_handoff)
    outcome_valid = validate_task_execution_outcome_evaluation_record(outcome)["valid"]
    forbidden_authority = any(
        (
            task_closure_created,
            learning_feedback_created,
            memory_write_performed,
            automatic_learning_approval_created,
        )
    )
    if forbidden_authority:
        status = "blocked_forbidden_authority_detected"
        klass = "system_fault"
        goal_reached = None
        progress = None
        regression = None
    elif not outcome_valid:
        status = "blocked_invalid_outcome_evaluation"
        klass = "system_fault"
        goal_reached = None
        progress = None
        regression = None
    elif outcome.outcome_class == "unknown_observation":
        status = "goal_delta_unknown_missing_observation"
        klass = "unknown"
        goal_reached = None
        progress = None
        regression = None
    elif task_goal_id is None and outcome.outcome_class == "observation_only":
        status = "goal_delta_not_applicable"
        klass = "not_applicable"
        goal_reached = False
        progress = False
        regression = False
    elif task_goal_id is None:
        status = "goal_delta_unknown_missing_goal"
        klass = "unknown"
        goal_reached = None
        progress = None
        regression = None
    elif deterministic_goal_reached:
        status = "goal_delta_evaluated"
        klass = "goal_reached"
        goal_reached = True
        progress = True
        regression = False
    elif deterministic_goal_regressed:
        status = "goal_delta_evaluated"
        klass = "regressed"
        goal_reached = False
        progress = False
        regression = True
    elif deterministic_goal_progress and outcome.outcome_class == "expected_effect_matched":
        status = "goal_delta_evaluated"
        klass = "closer_to_goal"
        goal_reached = False
        progress = True
        regression = False
    elif outcome.outcome_class == "expected_effect_not_matched":
        status = "goal_delta_evaluated"
        klass = "no_progress"
        goal_reached = False
        progress = False
        regression = False
    else:
        status = "goal_delta_not_applicable"
        klass = "not_applicable"
        goal_reached = False
        progress = False
        regression = False
    available = status in {"goal_delta_evaluated", "goal_delta_not_applicable"}
    return TaskGoalDeltaEvaluationRecord(
        goal_delta_evaluation_id=f"task_goal_delta:{outcome.outcome_evaluation_id}",
        schema_version=GOAL_DELTA_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_working_memory_id=outcome.source_task_working_memory_id,
        source_outcome_evaluation_id=outcome.outcome_evaluation_id,
        source_sense_handoff_id=handoff.sense_handoff_id,
        task_goal_id=task_goal_id,
        task_goal_summary=task_goal_summary,
        goal_delta_status=status,
        goal_delta_class=klass,
        goal_delta_summary=_goal_delta_summary(klass),
        goal_delta_reason=_goal_delta_reason(klass, outcome.outcome_class),
        goal_reached=goal_reached,
        progress_toward_goal_detected=progress,
        regression_from_goal_detected=regression,
        available_for_task_closure=available,
        available_for_learning_feedback_candidate_later=available,
        task_closure_created=task_closure_created,
        learning_feedback_created=learning_feedback_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        source_trace_refs=_combined_trace_refs(outcome.source_trace_refs, handoff.source_trace_refs),
    )


def validate_task_goal_delta_evaluation_record(
    goal_delta: TaskGoalDeltaEvaluationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _goal_delta_record(goal_delta)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_goal_delta:{error}"]}
    errors: list[str] = []
    if record.goal_delta_status.startswith("blocked_"):
        errors.append(record.goal_delta_status)
    if record.goal_delta_class == "goal_reached" and record.goal_reached is not True:
        errors.append("goal_reached_class_without_flag")
    for flag in (
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
        "goal_delta_evaluation_id": record.goal_delta_evaluation_id,
        "goal_delta_status": record.goal_delta_status,
        "goal_delta_class": record.goal_delta_class,
    }


def build_task_outcome_evaluation_safety_audit(
    *,
    sense_handoff: SenseSandboxObservationHandoffRecord | dict[str, object] | None,
    expected_effect_reference: TaskExpectedEffectReferenceRecord | dict[str, object] | None,
    outcome_evaluation: TaskExecutionOutcomeEvaluationRecord | dict[str, object] | None,
    goal_delta_evaluation: TaskGoalDeltaEvaluationRecord | dict[str, object] | None,
) -> TaskOutcomeEvaluationSafetyAudit:
    handoff = _handoff_record(sense_handoff) if sense_handoff is not None else None
    reference = (
        _reference_record(expected_effect_reference)
        if expected_effect_reference is not None
        else None
    )
    outcome = _outcome_record(outcome_evaluation) if outcome_evaluation is not None else None
    goal_delta = (
        _goal_delta_record(goal_delta_evaluation)
        if goal_delta_evaluation is not None
        else None
    )
    handoff_valid = handoff is not None and _handoff_valid(handoff)
    reference_valid = (
        reference is not None
        and validate_task_expected_effect_reference_record(reference)["valid"]
    )
    outcome_valid = (
        outcome is not None
        and validate_task_execution_outcome_evaluation_record(outcome)["valid"]
    )
    goal_delta_valid = (
        goal_delta is not None
        and validate_task_goal_delta_evaluation_record(goal_delta)["valid"]
    )
    blocked_reasons = _audit_blocked_reasons(
        handoff_valid=handoff_valid,
        reference_valid=reference_valid,
        outcome_valid=outcome_valid,
        goal_delta_valid=goal_delta_valid,
        reference=reference,
        outcome=outcome,
        goal_delta=goal_delta,
    )
    return TaskOutcomeEvaluationSafetyAudit(
        outcome_evaluation_safety_audit_id=(
            "task_outcome_evaluation_safety_audit:"
            f"{outcome.outcome_evaluation_id if outcome else 'unknown'}"
        ),
        schema_version=SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_outcome_evaluation_id=outcome.outcome_evaluation_id if outcome else None,
        source_goal_delta_evaluation_id=goal_delta.goal_delta_evaluation_id if goal_delta else None,
        source_expected_effect_reference_id=reference.expected_effect_reference_id if reference else None,
        source_sense_handoff_id=handoff.sense_handoff_id if handoff else None,
        sense_handoff_valid=handoff_valid,
        expected_effect_reference_valid=reference_valid,
        outcome_evaluation_valid=outcome_valid,
        goal_delta_evaluation_valid=goal_delta_valid,
        evaluation_only_confirmed=True,
        no_task_closure=not _task_closure_created(reference, outcome, goal_delta),
        no_learning_feedback=not _learning_feedback_created(reference, outcome, goal_delta),
        no_memory_write=not _memory_write_performed(reference, outcome, goal_delta),
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_automatic_learning_approval=not _automatic_learning_approval_created(
            reference,
            outcome,
            goal_delta,
        ),
        no_candidate_ordering_change=not (
            outcome.candidate_ordering_changed if outcome else False
        ),
        no_selected_action_change=not (
            outcome.selected_action_changed if outcome else False
        ),
        no_final_action_change=not (outcome.final_action_changed if outcome else False),
        no_direct_command_change=not (outcome.direct_command_changed if outcome else False),
        no_execution_created_by_evaluation=not (
            outcome.execution_created_by_evaluation if outcome else False
        ),
        audit_status=_audit_status(blocked_reasons, outcome=outcome),
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(blocked_reasons),
        source_trace_refs=_combined_trace_refs(
            handoff.source_trace_refs if handoff else (),
            reference.source_trace_refs if reference else (),
            outcome.source_trace_refs if outcome else (),
            goal_delta.source_trace_refs if goal_delta else (),
        ),
    )


def validate_task_outcome_evaluation_safety_audit(
    audit: TaskOutcomeEvaluationSafetyAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _audit_record(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_outcome_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status not in {"passed_outcome_evaluation_only", "passed_outcome_unknown"}:
        errors.append(record.audit_status)
    for flag in (
        "evaluation_only_confirmed",
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
        "no_execution_created_by_evaluation",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    if not set(BLOCKED_CLAIMS).issubset(set(record.blocked_claims)):
        errors.append("blocked_claims_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "outcome_evaluation_safety_audit_id": record.outcome_evaluation_safety_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_demo_observe_outcome_evaluation() -> dict[str, object]:
    return _build_outcome_bundle()


def build_demo_step_forward_matched_outcome_evaluation() -> dict[str, object]:
    return _build_outcome_bundle(
        handoff_payload=_custom_sense_handoff_payload(
            direct_command="step_forward",
            labels=("actor_position_changed", "box_position_unchanged", "no_contact_detected"),
            actor_changed=True,
            box_changed=False,
        )
    )


def build_demo_step_forward_not_matched_outcome_evaluation() -> dict[str, object]:
    return _build_outcome_bundle(
        handoff_payload=_custom_sense_handoff_payload(
            direct_command="step_forward",
            labels=("actor_position_unchanged", "box_position_unchanged", "no_contact_detected", "visible_no_change"),
            actor_changed=False,
            box_changed=False,
        )
    )


def build_demo_push_right_matched_outcome_evaluation() -> dict[str, object]:
    return _build_outcome_bundle(
        handoff_payload=_custom_sense_handoff_payload(
            direct_command="push_right",
            labels=("actor_position_unchanged", "box_position_changed", "contact_detected"),
            actor_changed=False,
            box_changed=True,
            contact=True,
            contact_target="box",
        ),
        task_goal_id="goal:move_box_right",
        task_goal_summary="Move the box right.",
        deterministic_goal_progress=True,
    )


def build_demo_push_right_not_matched_outcome_evaluation() -> dict[str, object]:
    return _build_outcome_bundle(
        handoff_payload=_custom_sense_handoff_payload(
            direct_command="push_right",
            labels=("actor_position_unchanged", "box_position_unchanged", "contact_detected"),
            actor_changed=False,
            box_changed=False,
            contact=True,
            contact_target="box",
        ),
        task_goal_id="goal:move_box_right",
        task_goal_summary="Move the box right.",
    )


def build_demo_unknown_expected_effect_outcome_evaluation() -> dict[str, object]:
    return _build_outcome_bundle(
        handoff_payload=_custom_sense_handoff_payload(
            direct_command="unsupported_command",
            labels=("unknown_visible_delta",),
            actor_changed=None,
            box_changed=False,
        )
    )


def build_demo_missing_observation_outcome_evaluation() -> dict[str, object]:
    from ashl_core_v1.sense.sandbox_execution_observation_handoff import (
        build_demo_sense_sandbox_observation_handoff,
    )

    payload = build_demo_sense_sandbox_observation_handoff()
    handoff = dict(payload["sense_sandbox_observation_handoff"])
    handoff["sense_observation_payload"] = {}
    return _build_outcome_bundle(handoff_payload={"sense_sandbox_observation_handoff": handoff})


def build_demo_blocked_invalid_sense_handoff_outcome_evaluation() -> dict[str, object]:
    from ashl_core_v1.sense.sandbox_execution_observation_handoff import (
        build_demo_blocked_sense_sandbox_observation,
    )

    return _build_outcome_bundle(
        handoff_payload=build_demo_blocked_sense_sandbox_observation(
            "invalid-sandbox-execution"
        )
    )


def build_demo_blocked_task_closure_created_outcome_evaluation() -> dict[str, object]:
    return _build_outcome_bundle(task_closure_created=True)


def build_demo_blocked_learning_feedback_created_outcome_evaluation() -> dict[str, object]:
    return _build_outcome_bundle(learning_feedback_created=True)


def build_demo_blocked_memory_write_outcome_evaluation() -> dict[str, object]:
    return _build_outcome_bundle(memory_write_performed=True)


def build_demo_blocked_action_authority_outcome_evaluation() -> dict[str, object]:
    return _build_outcome_bundle(candidate_ordering_changed=True)


def build_demo_blocked_outcome_evaluation(case: str) -> dict[str, object]:
    builders = {
        "invalid-sense-handoff": build_demo_blocked_invalid_sense_handoff_outcome_evaluation,
        "task-closure-created": build_demo_blocked_task_closure_created_outcome_evaluation,
        "learning-feedback-created": build_demo_blocked_learning_feedback_created_outcome_evaluation,
        "memory-write-detected": build_demo_blocked_memory_write_outcome_evaluation,
        "action-authority-detected": build_demo_blocked_action_authority_outcome_evaluation,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown outcome evaluation blocked case: {case}") from error


def build_demo_outcome_evaluation_case(case: str) -> dict[str, object]:
    builders = {
        "observe": build_demo_observe_outcome_evaluation,
        "step-forward-matched": build_demo_step_forward_matched_outcome_evaluation,
        "step-forward-not-matched": build_demo_step_forward_not_matched_outcome_evaluation,
        "push-right-matched": build_demo_push_right_matched_outcome_evaluation,
        "push-right-not-matched": build_demo_push_right_not_matched_outcome_evaluation,
        "unknown-expected-effect": build_demo_unknown_expected_effect_outcome_evaluation,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown outcome evaluation demo case: {case}") from error


def _build_outcome_bundle(
    *,
    handoff_payload: dict[str, object] | None = None,
    explicit_expected_effect: str | None = None,
    task_goal_id: str | None = None,
    task_goal_summary: str | None = None,
    deterministic_goal_progress: bool | None = None,
    deterministic_goal_reached: bool | None = None,
    deterministic_goal_regressed: bool | None = None,
    task_closure_created: bool = False,
    learning_feedback_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    candidate_ordering_changed: bool = False,
    selected_action_changed: bool = False,
    final_action_changed: bool = False,
    direct_command_changed: bool = False,
    execution_created_by_evaluation: bool = False,
) -> dict[str, object]:
    from ashl_core_v1.sense.sandbox_execution_observation_handoff import (
        SenseSandboxObservationHandoffRecord,
        build_demo_sense_sandbox_observation_handoff,
    )

    handoff_payload = handoff_payload or build_demo_sense_sandbox_observation_handoff()
    handoff_data = handoff_payload.get("sense_sandbox_observation_handoff")
    if handoff_data is None:
        handoff_data = handoff_payload["sense_sandbox_observation_handoff"]
    handoff = SenseSandboxObservationHandoffRecord.from_dict(handoff_data)
    expected_effect = build_task_expected_effect_reference_record(
        sense_handoff=handoff,
        explicit_expected_effect=explicit_expected_effect,
        task_goal_id=task_goal_id,
        task_goal_summary=task_goal_summary,
    )
    outcome = build_task_execution_outcome_evaluation_record(
        sense_handoff=handoff,
        expected_effect_reference=expected_effect,
        task_closure_created=task_closure_created,
        learning_feedback_created=learning_feedback_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        candidate_ordering_changed=candidate_ordering_changed,
        selected_action_changed=selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_changed=direct_command_changed,
        execution_created_by_evaluation=execution_created_by_evaluation,
    )
    goal_delta = build_task_goal_delta_evaluation_record(
        outcome_evaluation=outcome,
        sense_handoff=handoff,
        task_goal_id=task_goal_id,
        task_goal_summary=task_goal_summary,
        deterministic_goal_progress=deterministic_goal_progress,
        deterministic_goal_reached=deterministic_goal_reached,
        deterministic_goal_regressed=deterministic_goal_regressed,
        task_closure_created=task_closure_created,
        learning_feedback_created=learning_feedback_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
    )
    audit = build_task_outcome_evaluation_safety_audit(
        sense_handoff=handoff,
        expected_effect_reference=expected_effect,
        outcome_evaluation=outcome,
        goal_delta_evaluation=goal_delta,
    )
    return {
        "task_expected_effect_reference": expected_effect.to_dict(),
        "task_execution_outcome_evaluation": outcome.to_dict(),
        "task_goal_delta_evaluation": goal_delta.to_dict(),
        "task_outcome_evaluation_safety_audit": audit.to_dict(),
        "task_expected_effect_reference_validation": (
            validate_task_expected_effect_reference_record(expected_effect)
        ),
        "task_execution_outcome_evaluation_validation": (
            validate_task_execution_outcome_evaluation_record(outcome)
        ),
        "task_goal_delta_evaluation_validation": (
            validate_task_goal_delta_evaluation_record(goal_delta)
        ),
        "task_outcome_evaluation_safety_audit_validation": (
            validate_task_outcome_evaluation_safety_audit(audit)
        ),
        "source_sense_handoff": handoff.to_dict(),
        "safe_claim": SAFE_CLAIM,
    }


def _custom_sense_handoff_payload(
    *,
    direct_command: str,
    labels: tuple[str, ...],
    actor_changed: bool | None,
    box_changed: bool,
    contact: bool = False,
    contact_target: str | None = None,
) -> dict[str, object]:
    from ashl_core_v1.sense.sandbox_execution_observation_handoff import (
        build_demo_sense_sandbox_observation_handoff,
    )

    payload = build_demo_sense_sandbox_observation_handoff()
    observation = dict(payload["sense_sandbox_execution_observation"])
    observation.update(
        {
            "direct_command": direct_command,
            "observed_actor_position_changed": actor_changed,
            "observed_box_position_changed": box_changed,
            "observed_contact": contact,
            "observed_contact_target": contact_target,
            "visible_state_delta_labels": labels,
        }
    )
    delta = dict(payload["sense_sandbox_state_delta_observation"])
    delta.update(
        {
            "direct_command": direct_command,
            "visibility_delta": {"labels": list(labels)},
        }
    )
    handoff = dict(payload["sense_sandbox_observation_handoff"])
    handoff.update(
        {
            "direct_command": direct_command,
            "sense_observation_payload": {
                "sense_observation": observation,
                "state_delta_observation": delta,
            },
        }
    )
    return {"sense_sandbox_observation_handoff": handoff}


def _evaluate_observation(
    *,
    expected_effect: str,
    observation: SenseSandboxExecutionObservationRecord,
) -> tuple[str, bool | None, bool | None, str]:
    if expected_effect == "unknown_expected_effect":
        return (
            "unknown_expected_effect",
            None,
            None,
            "outcome_unknown_missing_expected_effect",
        )
    if expected_effect == "observe_environment":
        return ("observation_only", True, False, "outcome_evaluated")
    if expected_effect == "wait_no_required_delta":
        return ("no_visible_change", True, False, "outcome_evaluated_no_visible_delta")
    if expected_effect in {"actor_moves_forward", "actor_turns_left", "actor_turns_right"}:
        matched = observation.observed_actor_position_changed is True
        failed = observation.observed_actor_position_changed is False
        return (
            "expected_effect_matched" if matched else "expected_effect_not_matched",
            matched,
            failed,
            "outcome_evaluated" if matched else "outcome_evaluated_no_visible_delta",
        )
    if expected_effect in {"box_moves_right", "box_moves_left"}:
        matched = observation.observed_box_position_changed is True
        failed = observation.observed_box_position_changed is False
        return (
            "expected_effect_matched" if matched else "expected_effect_not_matched",
            matched,
            failed,
            "outcome_evaluated" if matched else "outcome_evaluated_no_visible_delta",
        )
    return ("unknown_expected_effect", None, None, "outcome_unknown_missing_expected_effect")


def _handoff_valid(handoff: SenseSandboxObservationHandoffRecord) -> bool:
    from ashl_core_v1.sense.sandbox_execution_observation_handoff import (
        validate_sense_sandbox_observation_handoff_record,
    )

    return (
        handoff.handoff_status == "handoff_ready_for_task_outcome_evaluation"
        and handoff.observation_available_for_task_outcome_evaluation
        and not handoff.outcome_evaluation_created
        and not handoff.task_closure_created
        and not handoff.learning_feedback_created
        and not handoff.memory_write_performed
        and validate_sense_sandbox_observation_handoff_record(handoff)["valid"]
    )


def _observation_from_handoff(
    handoff: SenseSandboxObservationHandoffRecord,
) -> SenseSandboxExecutionObservationRecord | None:
    from ashl_core_v1.sense.sandbox_execution_observation_handoff import (
        SenseSandboxExecutionObservationRecord,
    )

    try:
        payload = handoff.sense_observation_payload["sense_observation"]
        return SenseSandboxExecutionObservationRecord.from_dict(dict(payload))
    except (KeyError, TypeError, ValueError):
        return None


def _delta_from_handoff(
    handoff: SenseSandboxObservationHandoffRecord,
) -> SenseSandboxStateDeltaObservationRecord | None:
    from ashl_core_v1.sense.sandbox_execution_observation_handoff import (
        SenseSandboxStateDeltaObservationRecord,
    )

    try:
        payload = handoff.sense_observation_payload["state_delta_observation"]
        return SenseSandboxStateDeltaObservationRecord.from_dict(dict(payload))
    except (KeyError, TypeError, ValueError):
        return None


def _task_working_memory_id_from_handoff(handoff: SenseSandboxObservationHandoffRecord) -> str:
    observation = _observation_from_handoff(handoff)
    if observation is not None:
        return observation.source_sandbox_execution_id.split(":")[-1]
    return handoff.source_sandbox_execution_id.split(":")[-1]


def _expected_effect_summary(effect: str, source: str) -> str:
    if effect == "unknown_expected_effect":
        return "Expected effect is unknown."
    return f"Expected effect {effect} resolved from {source}."


def _outcome_summary(outcome_class: str) -> str:
    summaries = {
        "expected_effect_matched": "Observed Sense data matched deterministic expected effect.",
        "expected_effect_not_matched": "Observed Sense data did not match deterministic expected effect.",
        "observation_only": "Execution produced an observation-only outcome.",
        "no_visible_change": "Expected effect requires no visible delta.",
        "unknown_expected_effect": "Outcome cannot be evaluated because expected effect is unknown.",
        "unknown_observation": "Outcome cannot be evaluated because observation is missing.",
        "system_fault": "Outcome evaluation blocked by forbidden authority.",
    }
    return summaries[outcome_class]


def _outcome_reason(
    expected_effect: str,
    observation: SenseSandboxExecutionObservationRecord | None,
) -> str:
    labels = ", ".join(observation.visible_state_delta_labels) if observation else "missing"
    return f"expected_effect={expected_effect}; observed_delta_labels={labels}"


def _goal_delta_summary(klass: str) -> str:
    summaries = {
        "closer_to_goal": "Deterministic goal context indicates progress.",
        "goal_reached": "Deterministic goal context indicates goal reached.",
        "no_progress": "Outcome did not match expected effect, so no progress is recorded.",
        "regressed": "Deterministic goal context indicates regression.",
        "not_applicable": "Goal delta is not applicable for this outcome.",
        "unknown": "Goal delta is unknown without deterministic goal data.",
        "system_fault": "Goal delta blocked by invalid or forbidden input.",
    }
    return summaries[klass]


def _goal_delta_reason(klass: str, outcome_class: str) -> str:
    return f"goal_delta_class={klass}; source_outcome_class={outcome_class}"


def _audit_blocked_reasons(
    *,
    handoff_valid: bool,
    reference_valid: bool,
    outcome_valid: bool,
    goal_delta_valid: bool,
    reference: TaskExpectedEffectReferenceRecord | None,
    outcome: TaskExecutionOutcomeEvaluationRecord | None,
    goal_delta: TaskGoalDeltaEvaluationRecord | None,
) -> list[str]:
    reasons: list[str] = []
    if not handoff_valid:
        reasons.append("invalid_sense_handoff")
    if not reference_valid:
        reasons.append("invalid_expected_effect_reference")
    if not outcome_valid:
        reasons.append("invalid_outcome_evaluation")
    if not goal_delta_valid:
        reasons.append("invalid_goal_delta_evaluation")
    if _task_closure_created(reference, outcome, goal_delta):
        reasons.append("task_closure_created")
    if _learning_feedback_created(reference, outcome, goal_delta):
        reasons.append("learning_feedback_created")
    if _memory_write_performed(reference, outcome, goal_delta):
        reasons.append("memory_write_performed")
    if outcome is not None and any(
        (
            outcome.candidate_ordering_changed,
            outcome.selected_action_changed,
            outcome.final_action_changed,
            outcome.direct_command_changed,
            outcome.execution_created_by_evaluation,
        )
    ):
        reasons.append("action_authority_changed")
    return reasons


def _audit_status(
    blocked_reasons: list[str],
    *,
    outcome: TaskExecutionOutcomeEvaluationRecord | None,
) -> str:
    if "task_closure_created" in blocked_reasons:
        return "blocked_task_closure_detected"
    if "learning_feedback_created" in blocked_reasons:
        return "blocked_learning_feedback_detected"
    if "memory_write_performed" in blocked_reasons:
        return "blocked_memory_write_detected"
    if "action_authority_changed" in blocked_reasons:
        return "blocked_action_authority_detected"
    if "invalid_sense_handoff" in blocked_reasons:
        return "blocked_invalid_sense_handoff"
    if "invalid_expected_effect_reference" in blocked_reasons:
        return "blocked_invalid_expected_effect_reference"
    if "invalid_outcome_evaluation" in blocked_reasons:
        return "blocked_invalid_outcome_evaluation"
    if "invalid_goal_delta_evaluation" in blocked_reasons:
        return "blocked_invalid_goal_delta_evaluation"
    if outcome and outcome.outcome_class in {"unknown_expected_effect", "unknown_observation"}:
        return "passed_outcome_unknown"
    return "passed_outcome_evaluation_only"


def _task_closure_created(
    reference: TaskExpectedEffectReferenceRecord | None,
    outcome: TaskExecutionOutcomeEvaluationRecord | None,
    goal_delta: TaskGoalDeltaEvaluationRecord | None,
) -> bool:
    return bool(
        (reference.task_closure_created if reference else False)
        or (outcome.task_closure_created if outcome else False)
        or (goal_delta.task_closure_created if goal_delta else False)
    )


def _learning_feedback_created(
    reference: TaskExpectedEffectReferenceRecord | None,
    outcome: TaskExecutionOutcomeEvaluationRecord | None,
    goal_delta: TaskGoalDeltaEvaluationRecord | None,
) -> bool:
    return bool(
        (reference.learning_feedback_created if reference else False)
        or (outcome.learning_feedback_created if outcome else False)
        or (goal_delta.learning_feedback_created if goal_delta else False)
    )


def _memory_write_performed(
    reference: TaskExpectedEffectReferenceRecord | None,
    outcome: TaskExecutionOutcomeEvaluationRecord | None,
    goal_delta: TaskGoalDeltaEvaluationRecord | None,
) -> bool:
    return bool(
        (reference.memory_write_performed if reference else False)
        or (outcome.memory_write_performed if outcome else False)
        or (goal_delta.memory_write_performed if goal_delta else False)
    )


def _automatic_learning_approval_created(
    reference: TaskExpectedEffectReferenceRecord | None,
    outcome: TaskExecutionOutcomeEvaluationRecord | None,
    goal_delta: TaskGoalDeltaEvaluationRecord | None,
) -> bool:
    return bool(
        (reference.automatic_learning_approval_created if reference else False)
        or (outcome.automatic_learning_approval_created if outcome else False)
        or (goal_delta.automatic_learning_approval_created if goal_delta else False)
    )


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _handoff_record(
    record: SenseSandboxObservationHandoffRecord | dict[str, object],
) -> SenseSandboxObservationHandoffRecord:
    from ashl_core_v1.sense.sandbox_execution_observation_handoff import (
        SenseSandboxObservationHandoffRecord,
    )

    return (
        record
        if isinstance(record, SenseSandboxObservationHandoffRecord)
        else SenseSandboxObservationHandoffRecord.from_dict(dict(record))
    )


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


def _audit_record(
    record: TaskOutcomeEvaluationSafetyAudit | dict[str, object],
) -> TaskOutcomeEvaluationSafetyAudit:
    return (
        record
        if isinstance(record, TaskOutcomeEvaluationSafetyAudit)
        else TaskOutcomeEvaluationSafetyAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
