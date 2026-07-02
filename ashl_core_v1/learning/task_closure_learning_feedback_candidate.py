"""Learning feedback candidates built from Task closure records."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from typing import Any

SOURCE_ENGINE = "learning_engine"

CANDIDATE_SCHEMA_VERSION = "learning_engine_task_closure_learning_feedback_candidate_v0"
EVIDENCE_PACKET_SCHEMA_VERSION = (
    "learning_engine_task_closure_learning_feedback_evidence_packet_v0"
)
CANDIDATE_SET_SCHEMA_VERSION = (
    "learning_engine_task_closure_learning_feedback_candidate_set_v0"
)
SAFETY_AUDIT_SCHEMA_VERSION = (
    "learning_engine_task_closure_learning_feedback_candidate_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Learning Engine can convert deterministic Task closure records "
    "into Learning Feedback Candidate evidence packets for later teacher review, "
    "while avoiding learning approval, ConceptCandidate creation, memory writes, "
    "behavior changes, action authority changes, or automatic learning approval."
)
BLOCKED_CLAIMS = (
    "no_learning_feedback_approval",
    "no_learning_feedback_application",
    "no_concept_candidate_creation",
    "no_memory_write",
    "no_action_authority_change",
    "no_behavior_change",
    "no_automatic_learning_approval",
)

ALLOWED_FEEDBACK_CANDIDATE_KINDS = {
    "successful_expected_effect_candidate",
    "failed_expected_effect_candidate",
    "no_progress_candidate",
    "goal_reached_candidate",
    "observation_only_candidate",
    "unknown_outcome_candidate",
    "system_fault_candidate",
}
ALLOWED_LEARNING_SIGNAL_CLASSES = {
    "positive_affordance_signal",
    "negative_affordance_signal",
    "goal_completion_signal",
    "no_progress_signal",
    "observation_context_signal",
    "unknown_signal",
    "system_fault_signal",
}
ALLOWED_REVIEW_PRIORITIES = {"low", "normal", "high", "blocked"}
ALLOWED_EVIDENCE_PACKET_STATUSES = {
    "evidence_packet_complete",
    "evidence_packet_partial",
    "blocked_invalid_task_closure",
    "blocked_missing_required_outcome_evaluation",
    "blocked_forbidden_authority_detected",
}
ALLOWED_CANDIDATE_SET_STATUSES = {
    "candidate_set_created",
    "candidate_set_created_with_partial_evidence",
    "candidate_set_created_all_blocked",
    "blocked_invalid_task_closure_set",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_learning_feedback_candidate_only",
    "passed_candidate_created_with_partial_evidence",
    "blocked_invalid_task_closure",
    "blocked_invalid_evidence_packet",
    "blocked_invalid_candidate_set",
    "blocked_learning_feedback_approval_detected",
    "blocked_concept_candidate_creation_detected",
    "blocked_memory_write_detected",
    "blocked_action_authority_detected",
    "blocked_behavior_change_detected",
}
PASSING_CLOSURE_AUDIT_STATUSES = {
    "passed_task_closure_only",
    "passed_task_closed_unknown",
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
class LearningFeedbackCandidateRecord:
    learning_feedback_candidate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_closure_id: str
    source_task_closure_summary_id: str | None
    source_task_closure_safety_audit_id: str | None
    source_outcome_evaluation_id: str
    source_goal_delta_evaluation_id: str
    source_expected_effect_reference_id: str
    source_sense_observation_id: str | None
    source_state_delta_observation_id: str | None
    source_sense_handoff_id: str | None
    source_sandbox_execution_id: str | None
    source_direct_command_application_id: str | None
    task_working_memory_id: str | None
    task_initialization_id: str | None
    direct_command: str | None
    expected_effect: str | None
    outcome_class: str
    goal_delta_class: str
    closure_status: str
    closure_class: str
    feedback_candidate_kind: str
    learning_signal_class: str
    review_priority: str
    candidate_summary: str
    candidate_reason: str
    candidate_evidence_labels: tuple[str, ...]
    candidate_risk_warnings: tuple[str, ...]
    counterexample_relevance_notes: tuple[str, ...]
    available_for_teacher_review: bool
    requires_teacher_review_before_learning: bool
    requires_concept_candidate_package: bool
    requires_memory_write_gate: bool
    learning_feedback_approved: bool
    learning_feedback_applied: bool
    concept_candidate_created: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_created: bool
    execution_created: bool
    task_behavior_changed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CANDIDATE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_task_closure_learning_feedback_candidate_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.feedback_candidate_kind not in ALLOWED_FEEDBACK_CANDIDATE_KINDS:
            raise ValueError(f"unknown feedback_candidate_kind: {self.feedback_candidate_kind}")
        if self.learning_signal_class not in ALLOWED_LEARNING_SIGNAL_CLASSES:
            raise ValueError(f"unknown learning_signal_class: {self.learning_signal_class}")
        if self.review_priority not in ALLOWED_REVIEW_PRIORITIES:
            raise ValueError(f"unknown review_priority: {self.review_priority}")
        object.__setattr__(
            self,
            "candidate_evidence_labels",
            _tuple_of_str("candidate_evidence_labels", self.candidate_evidence_labels),
        )
        object.__setattr__(
            self,
            "candidate_risk_warnings",
            _tuple_of_str("candidate_risk_warnings", self.candidate_risk_warnings),
        )
        object.__setattr__(
            self,
            "counterexample_relevance_notes",
            _tuple_of_str(
                "counterexample_relevance_notes",
                self.counterexample_relevance_notes,
            ),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "LearningFeedbackCandidateRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class LearningFeedbackCandidateEvidencePacket:
    learning_feedback_evidence_packet_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_learning_feedback_candidate_id: str
    source_task_closure_id: str
    evidence_chain_complete: bool
    task_closure_ref: str
    outcome_evaluation_ref: str
    goal_delta_evaluation_ref: str
    expected_effect_ref: str
    sense_observation_ref: str | None
    state_delta_observation_ref: str | None
    sandbox_execution_ref: str | None
    direct_command_ref: str | None
    expected_effect: str | None
    direct_command: str | None
    observed_delta_labels: tuple[str, ...]
    outcome_class: str
    goal_delta_class: str
    closure_status: str
    evidence_summary: str
    missing_evidence_refs: tuple[str, ...]
    evidence_packet_status: str
    learning_feedback_approved: bool
    concept_candidate_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVIDENCE_PACKET_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_task_closure_learning_feedback_evidence_packet_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.evidence_packet_status not in ALLOWED_EVIDENCE_PACKET_STATUSES:
            raise ValueError(f"unknown evidence_packet_status: {self.evidence_packet_status}")
        object.__setattr__(
            self,
            "observed_delta_labels",
            _tuple_of_str("observed_delta_labels", self.observed_delta_labels),
        )
        object.__setattr__(
            self,
            "missing_evidence_refs",
            _tuple_of_str("missing_evidence_refs", self.missing_evidence_refs),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "LearningFeedbackCandidateEvidencePacket":
        return cls(**dict(data))


@dataclass(frozen=True)
class LearningFeedbackCandidateSet:
    learning_feedback_candidate_set_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_closure_ids: tuple[str, ...]
    candidates: tuple[LearningFeedbackCandidateRecord, ...]
    evidence_packets: tuple[LearningFeedbackCandidateEvidencePacket, ...]
    candidate_ids: tuple[str, ...]
    candidate_kinds: tuple[str, ...]
    candidate_count: int
    available_for_teacher_review_count: int
    blocked_count: int
    set_status: str
    set_summary: str
    available_for_teacher_review: bool
    learning_feedback_approved: bool
    concept_candidate_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CANDIDATE_SET_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_task_closure_learning_feedback_candidate_set_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.set_status not in ALLOWED_CANDIDATE_SET_STATUSES:
            raise ValueError(f"unknown set_status: {self.set_status}")
        object.__setattr__(
            self,
            "source_task_closure_ids",
            _tuple_of_str("source_task_closure_ids", self.source_task_closure_ids),
        )
        object.__setattr__(
            self,
            "candidates",
            tuple(
                item
                if isinstance(item, LearningFeedbackCandidateRecord)
                else LearningFeedbackCandidateRecord.from_dict(dict(item))
                for item in self.candidates
            ),
        )
        object.__setattr__(
            self,
            "evidence_packets",
            tuple(
                item
                if isinstance(item, LearningFeedbackCandidateEvidencePacket)
                else LearningFeedbackCandidateEvidencePacket.from_dict(dict(item))
                for item in self.evidence_packets
            ),
        )
        object.__setattr__(
            self,
            "candidate_ids",
            _tuple_of_str("candidate_ids", self.candidate_ids),
        )
        object.__setattr__(
            self,
            "candidate_kinds",
            _tuple_of_str("candidate_kinds", self.candidate_kinds),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "LearningFeedbackCandidateSet":
        return cls(**dict(data))


@dataclass(frozen=True)
class LearningFeedbackCandidateSafetyAudit:
    learning_feedback_candidate_safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_learning_feedback_candidate_set_id: str | None
    source_task_closure_ids: tuple[str, ...]
    task_closure_valid: bool
    task_closure_safety_audit_passed: bool
    evidence_packet_valid: bool
    learning_feedback_candidates_valid: bool
    candidate_only_confirmed: bool
    no_learning_feedback_approval: bool
    no_learning_feedback_application: bool
    no_concept_candidate_creation: bool
    no_reviewed_concept_creation: bool
    no_memory_write: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_automatic_learning_approval: bool
    no_candidate_ordering_change: bool
    no_selected_action_change: bool
    no_final_action_change: bool
    no_direct_command_creation: bool
    no_execution_creation: bool
    no_task_behavior_change: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_task_closure_learning_feedback_candidate_safety_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        object.__setattr__(
            self,
            "source_task_closure_ids",
            _tuple_of_str("source_task_closure_ids", self.source_task_closure_ids),
        )
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
    def from_dict(cls, data: dict[str, object]) -> "LearningFeedbackCandidateSafetyAudit":
        return cls(**dict(data))


def build_learning_feedback_candidate_from_task_closure(
    *,
    task_closure: TaskClosureFromOutcomeEvaluationRecord | dict[str, object],
    task_closure_summary: TaskClosureSummaryRecord | dict[str, object] | None,
    task_closure_safety_audit: TaskClosureSafetyAudit | dict[str, object] | None,
    outcome_evaluation: TaskExecutionOutcomeEvaluationRecord | dict[str, object],
    goal_delta_evaluation: TaskGoalDeltaEvaluationRecord | dict[str, object],
    expected_effect_reference: TaskExpectedEffectReferenceRecord | dict[str, object],
    learning_feedback_approved: bool = False,
    learning_feedback_applied: bool = False,
    concept_candidate_created: bool = False,
    reviewed_concept_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    candidate_ordering_changed: bool = False,
    selected_action_changed: bool = False,
    final_action_changed: bool = False,
    direct_command_created: bool = False,
    execution_created: bool = False,
    task_behavior_changed: bool = False,
) -> LearningFeedbackCandidateRecord:
    closure = _closure_record(task_closure)
    summary = _summary_record(task_closure_summary) if task_closure_summary else None
    closure_audit = (
        _closure_audit_record(task_closure_safety_audit)
        if task_closure_safety_audit
        else None
    )
    outcome = _outcome_record(outcome_evaluation)
    goal_delta = _goal_delta_record(goal_delta_evaluation)
    reference = _reference_record(expected_effect_reference)
    closure_valid = _closure_valid_for_candidate(closure)
    closure_audit_passed = _closure_audit_passed(closure_audit)
    forbidden_authority = any(
        (
            learning_feedback_approved,
            learning_feedback_applied,
            concept_candidate_created,
            reviewed_concept_created,
            memory_write_performed,
            automatic_learning_approval_created,
            candidate_ordering_changed,
            selected_action_changed,
            final_action_changed,
            direct_command_created,
            execution_created,
            task_behavior_changed,
        )
    )
    if forbidden_authority:
        kind = "system_fault_candidate"
        signal = "system_fault_signal"
        priority = "blocked"
        review_ready = False
    elif not closure_valid or not closure_audit_passed:
        kind = "system_fault_candidate"
        signal = "system_fault_signal"
        priority = "blocked"
        review_ready = False
    else:
        kind, signal, priority, review_ready = _candidate_policy(closure)
    evidence_labels = _evidence_labels(closure, outcome, goal_delta)
    return LearningFeedbackCandidateRecord(
        learning_feedback_candidate_id=f"learning_feedback_candidate:{closure.task_closure_id}",
        schema_version=CANDIDATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_closure_id=closure.task_closure_id,
        source_task_closure_summary_id=summary.task_closure_summary_id if summary else None,
        source_task_closure_safety_audit_id=(
            closure_audit.task_closure_safety_audit_id if closure_audit else None
        ),
        source_outcome_evaluation_id=closure.source_outcome_evaluation_id,
        source_goal_delta_evaluation_id=closure.source_goal_delta_evaluation_id,
        source_expected_effect_reference_id=closure.source_expected_effect_reference_id,
        source_sense_observation_id=outcome.source_sense_observation_id,
        source_state_delta_observation_id=outcome.source_state_delta_observation_id,
        source_sense_handoff_id=closure.source_sense_handoff_id,
        source_sandbox_execution_id=closure.source_sandbox_execution_id,
        source_direct_command_application_id=closure.source_direct_command_application_id,
        task_working_memory_id=closure.source_task_working_memory_id,
        task_initialization_id=closure.source_task_initialization_id,
        direct_command=closure.direct_command,
        expected_effect=closure.expected_effect or reference.expected_effect,
        outcome_class=closure.outcome_class,
        goal_delta_class=closure.goal_delta_class,
        closure_status=closure.closure_status,
        closure_class=closure.closure_class,
        feedback_candidate_kind=kind,
        learning_signal_class=signal,
        review_priority=priority,
        candidate_summary=_candidate_summary(kind, closure),
        candidate_reason=_candidate_reason(closure, outcome, goal_delta),
        candidate_evidence_labels=evidence_labels,
        candidate_risk_warnings=_risk_warnings(closure),
        counterexample_relevance_notes=_counterexample_notes(closure),
        available_for_teacher_review=review_ready,
        requires_teacher_review_before_learning=True,
        requires_concept_candidate_package=True,
        requires_memory_write_gate=True,
        learning_feedback_approved=learning_feedback_approved,
        learning_feedback_applied=learning_feedback_applied,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        candidate_ordering_changed=candidate_ordering_changed,
        selected_action_changed=selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_created=direct_command_created,
        execution_created=execution_created,
        task_behavior_changed=task_behavior_changed,
        source_trace_refs=_combined_trace_refs(
            closure.source_trace_refs,
            summary.source_trace_refs if summary else (),
            closure_audit.source_trace_refs if closure_audit else (),
            outcome.source_trace_refs,
            goal_delta.source_trace_refs,
            reference.source_trace_refs,
        ),
    )


def validate_learning_feedback_candidate_record(
    candidate: LearningFeedbackCandidateRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _candidate_record(candidate)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_learning_feedback_candidate:{error}"]}
    errors: list[str] = []
    for flag in (
        "requires_teacher_review_before_learning",
        "requires_concept_candidate_package",
        "requires_memory_write_gate",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    for flag in (
        "learning_feedback_approved",
        "learning_feedback_applied",
        "concept_candidate_created",
        "reviewed_concept_created",
        "memory_write_performed",
        "automatic_learning_approval_created",
        "candidate_ordering_changed",
        "selected_action_changed",
        "final_action_changed",
        "direct_command_created",
        "execution_created",
        "task_behavior_changed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    if record.feedback_candidate_kind in {"unknown_outcome_candidate", "system_fault_candidate"}:
        if record.available_for_teacher_review is not False:
            errors.append("diagnostic_candidate_marked_review_ready")
    return {
        "valid": not errors,
        "error_codes": errors,
        "learning_feedback_candidate_id": record.learning_feedback_candidate_id,
        "feedback_candidate_kind": record.feedback_candidate_kind,
        "available_for_teacher_review": record.available_for_teacher_review,
    }


def build_learning_feedback_candidate_evidence_packet(
    *,
    candidate: LearningFeedbackCandidateRecord | dict[str, object],
    task_closure: TaskClosureFromOutcomeEvaluationRecord | dict[str, object],
    outcome_evaluation: TaskExecutionOutcomeEvaluationRecord | dict[str, object] | None,
    goal_delta_evaluation: TaskGoalDeltaEvaluationRecord | dict[str, object] | None,
    expected_effect_reference: TaskExpectedEffectReferenceRecord | dict[str, object] | None,
    learning_feedback_approved: bool = False,
    concept_candidate_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
) -> LearningFeedbackCandidateEvidencePacket:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        validate_task_closure_from_outcome_evaluation_record,
    )

    record = _candidate_record(candidate)
    closure = _closure_record(task_closure)
    outcome = _outcome_record(outcome_evaluation) if outcome_evaluation is not None else None
    goal_delta = _goal_delta_record(goal_delta_evaluation) if goal_delta_evaluation is not None else None
    reference = (
        _reference_record(expected_effect_reference)
        if expected_effect_reference is not None
        else None
    )
    forbidden_authority = any(
        (
            learning_feedback_approved,
            concept_candidate_created,
            memory_write_performed,
            automatic_learning_approval_created,
        )
    )
    missing = _missing_evidence_refs(
        closure=closure,
        outcome=outcome,
        goal_delta=goal_delta,
        reference=reference,
    )
    allowed_partial = closure.closure_status in {
        "task_closed_unknown",
        "task_closed_system_fault",
    }
    if forbidden_authority:
        status = "blocked_forbidden_authority_detected"
        complete = False
    elif not validate_task_closure_from_outcome_evaluation_record(closure)["valid"]:
        status = "blocked_invalid_task_closure"
        complete = False
    elif "outcome_evaluation" in missing:
        status = "blocked_missing_required_outcome_evaluation"
        complete = False
    elif missing and allowed_partial:
        status = "evidence_packet_partial"
        complete = False
    elif missing:
        status = "blocked_missing_required_outcome_evaluation"
        complete = False
    else:
        status = "evidence_packet_complete"
        complete = True
    return LearningFeedbackCandidateEvidencePacket(
        learning_feedback_evidence_packet_id=(
            f"learning_feedback_evidence_packet:{record.learning_feedback_candidate_id}"
        ),
        schema_version=EVIDENCE_PACKET_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_learning_feedback_candidate_id=record.learning_feedback_candidate_id,
        source_task_closure_id=closure.task_closure_id,
        evidence_chain_complete=complete,
        task_closure_ref=closure.task_closure_id,
        outcome_evaluation_ref=outcome.outcome_evaluation_id if outcome else "missing:outcome_evaluation",
        goal_delta_evaluation_ref=(
            goal_delta.goal_delta_evaluation_id if goal_delta else "missing:goal_delta_evaluation"
        ),
        expected_effect_ref=(
            reference.expected_effect_reference_id if reference else "missing:expected_effect_reference"
        ),
        sense_observation_ref=outcome.source_sense_observation_id if outcome else None,
        state_delta_observation_ref=outcome.source_state_delta_observation_id if outcome else None,
        sandbox_execution_ref=closure.source_sandbox_execution_id,
        direct_command_ref=closure.source_direct_command_application_id,
        expected_effect=closure.expected_effect,
        direct_command=closure.direct_command,
        observed_delta_labels=outcome.observed_delta_labels if outcome else (),
        outcome_class=closure.outcome_class,
        goal_delta_class=closure.goal_delta_class,
        closure_status=closure.closure_status,
        evidence_summary=_evidence_summary(record, closure, outcome, goal_delta, reference),
        missing_evidence_refs=tuple(missing),
        evidence_packet_status=status,
        learning_feedback_approved=learning_feedback_approved,
        concept_candidate_created=concept_candidate_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        source_trace_refs=_combined_trace_refs(
            record.source_trace_refs,
            closure.source_trace_refs,
            outcome.source_trace_refs if outcome else (),
            goal_delta.source_trace_refs if goal_delta else (),
            reference.source_trace_refs if reference else (),
        ),
    )


def validate_learning_feedback_candidate_evidence_packet(
    evidence_packet: LearningFeedbackCandidateEvidencePacket | dict[str, object],
) -> dict[str, object]:
    try:
        packet = _packet_record(evidence_packet)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_evidence_packet:{error}"]}
    errors: list[str] = []
    if packet.evidence_packet_status.startswith("blocked_"):
        errors.append(packet.evidence_packet_status)
    for flag in (
        "learning_feedback_approved",
        "concept_candidate_created",
        "memory_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(packet, flag) is not False:
            errors.append(f"{flag}_true")
    if packet.evidence_packet_status == "evidence_packet_complete" and packet.missing_evidence_refs:
        errors.append("complete_packet_has_missing_refs")
    return {
        "valid": not errors,
        "error_codes": errors,
        "learning_feedback_evidence_packet_id": packet.learning_feedback_evidence_packet_id,
        "evidence_packet_status": packet.evidence_packet_status,
    }


def build_learning_feedback_candidate_set(
    *,
    candidates: tuple[LearningFeedbackCandidateRecord | dict[str, object], ...],
    evidence_packets: tuple[
        LearningFeedbackCandidateEvidencePacket | dict[str, object],
        ...
    ],
) -> LearningFeedbackCandidateSet:
    candidate_records = tuple(_candidate_record(item) for item in candidates)
    packet_records = tuple(_packet_record(item) for item in evidence_packets)
    candidate_ids = tuple(item.learning_feedback_candidate_id for item in candidate_records)
    candidate_kinds = tuple(item.feedback_candidate_kind for item in candidate_records)
    closure_ids = tuple(dict.fromkeys(item.source_task_closure_id for item in candidate_records))
    ready_count = sum(1 for item in candidate_records if item.available_for_teacher_review)
    blocked_count = sum(
        1
        for item in candidate_records
        if item.review_priority == "blocked" or not item.available_for_teacher_review
    )
    partial = any(item.evidence_packet_status == "evidence_packet_partial" for item in packet_records)
    invalid = any(
        item.evidence_packet_status.startswith("blocked_") for item in packet_records
    )
    if not candidate_records:
        status = "blocked_invalid_task_closure_set"
    elif _candidate_set_forbidden_authority(candidate_records, packet_records):
        status = "blocked_forbidden_authority_detected"
    elif invalid:
        status = "blocked_invalid_task_closure_set"
    elif partial:
        status = "candidate_set_created_with_partial_evidence"
    elif ready_count == 0:
        status = "candidate_set_created_all_blocked"
    else:
        status = "candidate_set_created"
    return LearningFeedbackCandidateSet(
        learning_feedback_candidate_set_id=_candidate_set_id(candidate_ids),
        schema_version=CANDIDATE_SET_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_closure_ids=closure_ids,
        candidates=candidate_records,
        evidence_packets=packet_records,
        candidate_ids=candidate_ids,
        candidate_kinds=candidate_kinds,
        candidate_count=len(candidate_records),
        available_for_teacher_review_count=ready_count,
        blocked_count=blocked_count,
        set_status=status,
        set_summary=f"Learning feedback candidate set created with {len(candidate_records)} candidates.",
        available_for_teacher_review=ready_count > 0 and not status.startswith("blocked_"),
        learning_feedback_approved=False,
        concept_candidate_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_combined_trace_refs(
            *(item.source_trace_refs for item in candidate_records),
            *(item.source_trace_refs for item in packet_records),
        ),
    )


def validate_learning_feedback_candidate_set(
    candidate_set: LearningFeedbackCandidateSet | dict[str, object],
) -> dict[str, object]:
    try:
        record = _set_record(candidate_set)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_candidate_set:{error}"]}
    errors: list[str] = []
    if record.set_status.startswith("blocked_"):
        errors.append(record.set_status)
    if record.candidate_count != len(record.candidates):
        errors.append("candidate_count_mismatch")
    if record.available_for_teacher_review_count != sum(
        1 for item in record.candidates if item.available_for_teacher_review
    ):
        errors.append("available_count_mismatch")
    for flag in (
        "learning_feedback_approved",
        "concept_candidate_created",
        "memory_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "learning_feedback_candidate_set_id": record.learning_feedback_candidate_set_id,
        "set_status": record.set_status,
    }


def build_learning_feedback_candidate_safety_audit(
    *,
    candidate_set: LearningFeedbackCandidateSet | dict[str, object] | None,
    task_closures: tuple[TaskClosureFromOutcomeEvaluationRecord | dict[str, object], ...],
    task_closure_safety_audits: tuple[TaskClosureSafetyAudit | dict[str, object], ...],
) -> LearningFeedbackCandidateSafetyAudit:
    record_set = _set_record(candidate_set) if candidate_set is not None else None
    closure_records = tuple(_closure_record(item) for item in task_closures)
    closure_audits = tuple(_closure_audit_record(item) for item in task_closure_safety_audits)
    candidates = record_set.candidates if record_set else ()
    packets = record_set.evidence_packets if record_set else ()
    closure_valid = bool(closure_records) and all(
        _closure_valid_for_candidate(item) for item in closure_records
    )
    closure_audit_passed = bool(closure_audits) and all(
        _closure_audit_passed(item) for item in closure_audits
    )
    packet_valid = bool(packets) and all(
        validate_learning_feedback_candidate_evidence_packet(item)["valid"]
        or item.evidence_packet_status == "evidence_packet_partial"
        for item in packets
    )
    candidates_valid = bool(candidates) and all(
        validate_learning_feedback_candidate_record(item)["valid"] for item in candidates
    )
    set_valid = (
        record_set is not None
        and validate_learning_feedback_candidate_set(record_set)["valid"]
    )
    no_approval = not any(
        item.learning_feedback_approved or item.learning_feedback_applied
        for item in candidates
    ) and not any(item.learning_feedback_approved for item in packets)
    no_concept = not any(
        item.concept_candidate_created or item.reviewed_concept_created
        for item in candidates
    ) and not any(item.concept_candidate_created for item in packets)
    no_memory = not any(item.memory_write_performed for item in candidates) and not any(
        item.memory_write_performed for item in packets
    )
    no_action = not any(
        item.candidate_ordering_changed
        or item.selected_action_changed
        or item.final_action_changed
        or item.direct_command_created
        or item.execution_created
        for item in candidates
    )
    no_behavior = not any(item.task_behavior_changed for item in candidates)
    blocked_reasons = _audit_blocked_reasons(
        closure_valid=closure_valid,
        closure_audit_passed=closure_audit_passed,
        packet_valid=packet_valid,
        candidates_valid=candidates_valid,
        set_valid=set_valid,
        no_approval=no_approval,
        no_concept=no_concept,
        no_memory=no_memory,
        no_action=no_action,
        no_behavior=no_behavior,
    )
    return LearningFeedbackCandidateSafetyAudit(
        learning_feedback_candidate_safety_audit_id=(
            f"learning_feedback_candidate_safety_audit:{record_set.learning_feedback_candidate_set_id}"
            if record_set
            else "learning_feedback_candidate_safety_audit:unknown"
        ),
        schema_version=SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_learning_feedback_candidate_set_id=(
            record_set.learning_feedback_candidate_set_id if record_set else None
        ),
        source_task_closure_ids=tuple(item.task_closure_id for item in closure_records),
        task_closure_valid=closure_valid,
        task_closure_safety_audit_passed=closure_audit_passed,
        evidence_packet_valid=packet_valid,
        learning_feedback_candidates_valid=candidates_valid,
        candidate_only_confirmed=True,
        no_learning_feedback_approval=no_approval,
        no_learning_feedback_application=no_approval,
        no_concept_candidate_creation=no_concept,
        no_reviewed_concept_creation=no_concept,
        no_memory_write=no_memory,
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_automatic_learning_approval=not any(
            item.automatic_learning_approval_created for item in candidates
        )
        and not any(item.automatic_learning_approval_created for item in packets),
        no_candidate_ordering_change=not any(
            item.candidate_ordering_changed for item in candidates
        ),
        no_selected_action_change=not any(item.selected_action_changed for item in candidates),
        no_final_action_change=not any(item.final_action_changed for item in candidates),
        no_direct_command_creation=not any(item.direct_command_created for item in candidates),
        no_execution_creation=not any(item.execution_created for item in candidates),
        no_task_behavior_change=no_behavior,
        audit_status=_audit_status(blocked_reasons, record_set=record_set),
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(blocked_reasons),
        source_trace_refs=_combined_trace_refs(
            *(item.source_trace_refs for item in closure_records),
            *(item.source_trace_refs for item in closure_audits),
            *(item.source_trace_refs for item in candidates),
            *(item.source_trace_refs for item in packets),
        ),
    )


def validate_learning_feedback_candidate_safety_audit(
    audit: LearningFeedbackCandidateSafetyAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _audit_record(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_candidate_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status not in {
        "passed_learning_feedback_candidate_only",
        "passed_candidate_created_with_partial_evidence",
    }:
        errors.append(record.audit_status)
    for flag in (
        "candidate_only_confirmed",
        "no_learning_feedback_approval",
        "no_learning_feedback_application",
        "no_concept_candidate_creation",
        "no_reviewed_concept_creation",
        "no_memory_write",
        "no_core_memory_write",
        "no_long_term_memory_write",
        "no_archive_memory_write",
        "no_anchor_write",
        "no_automatic_learning_approval",
        "no_candidate_ordering_change",
        "no_selected_action_change",
        "no_final_action_change",
        "no_direct_command_creation",
        "no_execution_creation",
        "no_task_behavior_change",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    if not set(BLOCKED_CLAIMS).issubset(set(record.blocked_claims)):
        errors.append("blocked_claims_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "learning_feedback_candidate_safety_audit_id": (
            record.learning_feedback_candidate_safety_audit_id
        ),
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_demo_goal_reached_learning_feedback_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        TaskClosureFromOutcomeEvaluationRecord,
        build_demo_push_right_matched_task_closure,
    )

    payload = build_demo_push_right_matched_task_closure()
    closure = TaskClosureFromOutcomeEvaluationRecord.from_dict(
        payload["task_closure_from_outcome_evaluation"]
    )
    closure = replace(
        closure,
        closure_class="goal_reached_closure",
        closure_status="task_closed_goal_reached",
        goal_delta_class="goal_reached",
        available_for_learning_feedback_candidate_later=True,
    )
    return _build_candidate_bundle(payload, task_closure=closure)


def build_demo_progress_learning_feedback_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        build_demo_step_forward_matched_task_closure,
    )

    return _build_candidate_bundle(build_demo_step_forward_matched_task_closure())


def build_demo_expected_effect_failed_learning_feedback_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        build_demo_step_forward_not_matched_task_closure,
    )

    return _build_candidate_bundle(build_demo_step_forward_not_matched_task_closure())


def build_demo_no_progress_learning_feedback_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        TaskClosureFromOutcomeEvaluationRecord,
        build_demo_push_right_not_matched_task_closure,
    )

    payload = build_demo_push_right_not_matched_task_closure()
    closure = TaskClosureFromOutcomeEvaluationRecord.from_dict(
        payload["task_closure_from_outcome_evaluation"]
    )
    closure = replace(
        closure,
        closure_class="no_progress_closure",
        closure_status="task_closed_no_progress",
        outcome_class="expected_effect_matched",
        goal_delta_class="no_progress",
        available_for_learning_feedback_candidate_later=True,
    )
    return _build_candidate_bundle(payload, task_closure=closure)


def build_demo_observation_only_learning_feedback_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        build_demo_observe_task_closure,
    )

    return _build_candidate_bundle(build_demo_observe_task_closure())


def build_demo_unknown_outcome_learning_feedback_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        build_demo_unknown_outcome_task_closure,
    )

    return _build_candidate_bundle(build_demo_unknown_outcome_task_closure())


def build_demo_system_fault_learning_feedback_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        TaskClosureFromOutcomeEvaluationRecord,
        build_demo_unknown_outcome_task_closure,
    )

    payload = build_demo_unknown_outcome_task_closure()
    closure = TaskClosureFromOutcomeEvaluationRecord.from_dict(
        payload["task_closure_from_outcome_evaluation"]
    )
    closure = replace(
        closure,
        closure_class="system_fault_closure",
        closure_status="task_closed_system_fault",
        outcome_class="system_fault",
        goal_delta_class="system_fault",
        available_for_learning_feedback_candidate_later=False,
    )
    return _build_candidate_bundle(payload, task_closure=closure)


def build_demo_blocked_invalid_task_closure_learning_feedback_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        TaskClosureFromOutcomeEvaluationRecord,
        build_demo_observe_task_closure,
    )

    payload = build_demo_observe_task_closure()
    closure = TaskClosureFromOutcomeEvaluationRecord.from_dict(
        payload["task_closure_from_outcome_evaluation"]
    )
    closure = replace(closure, task_closed=False)
    return _build_candidate_bundle(payload, task_closure=closure)


def build_demo_blocked_invalid_closure_audit_learning_feedback_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        TaskClosureSafetyAudit,
        build_demo_observe_task_closure,
    )

    payload = build_demo_observe_task_closure()
    closure_audit = TaskClosureSafetyAudit.from_dict(payload["task_closure_safety_audit"])
    closure_audit = replace(
        closure_audit,
        audit_status="blocked_invalid_task_closure",
        blocked_reasons=("invalid_task_closure",),
    )
    return _build_candidate_bundle(payload, task_closure_safety_audit=closure_audit)


def build_demo_blocked_learning_feedback_approved_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        build_demo_observe_task_closure,
    )

    return _build_candidate_bundle(
        build_demo_observe_task_closure(),
        learning_feedback_approved=True,
    )


def build_demo_blocked_concept_candidate_created() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        build_demo_observe_task_closure,
    )

    return _build_candidate_bundle(
        build_demo_observe_task_closure(),
        concept_candidate_created=True,
    )


def build_demo_blocked_memory_write_learning_feedback_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        build_demo_observe_task_closure,
    )

    return _build_candidate_bundle(
        build_demo_observe_task_closure(),
        memory_write_performed=True,
    )


def build_demo_blocked_action_authority_learning_feedback_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        build_demo_observe_task_closure,
    )

    return _build_candidate_bundle(
        build_demo_observe_task_closure(),
        selected_action_changed=True,
    )


def build_demo_blocked_behavior_change_learning_feedback_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        build_demo_observe_task_closure,
    )

    return _build_candidate_bundle(
        build_demo_observe_task_closure(),
        task_behavior_changed=True,
    )


def build_demo_blocked_missing_required_evidence_learning_feedback_candidate() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        build_demo_observe_task_closure,
    )

    return _build_candidate_bundle(
        build_demo_observe_task_closure(),
        include_outcome_evaluation=False,
    )


def build_demo_learning_feedback_candidate_case(case: str) -> dict[str, object]:
    builders = {
        "goal-reached": build_demo_goal_reached_learning_feedback_candidate,
        "progress": build_demo_progress_learning_feedback_candidate,
        "expected-effect-failed": build_demo_expected_effect_failed_learning_feedback_candidate,
        "no-progress": build_demo_no_progress_learning_feedback_candidate,
        "observation-only": build_demo_observation_only_learning_feedback_candidate,
        "unknown-outcome": build_demo_unknown_outcome_learning_feedback_candidate,
        "system-fault": build_demo_system_fault_learning_feedback_candidate,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown learning feedback candidate demo case: {case}") from error


def build_demo_blocked_learning_feedback_candidate(case: str) -> dict[str, object]:
    builders = {
        "invalid-task-closure": build_demo_blocked_invalid_task_closure_learning_feedback_candidate,
        "invalid-closure-audit": build_demo_blocked_invalid_closure_audit_learning_feedback_candidate,
        "learning-feedback-approved": build_demo_blocked_learning_feedback_approved_candidate,
        "concept-candidate-created": build_demo_blocked_concept_candidate_created,
        "memory-write-detected": build_demo_blocked_memory_write_learning_feedback_candidate,
        "action-authority-detected": build_demo_blocked_action_authority_learning_feedback_candidate,
        "behavior-change-detected": build_demo_blocked_behavior_change_learning_feedback_candidate,
        "missing-required-evidence": build_demo_blocked_missing_required_evidence_learning_feedback_candidate,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown learning feedback candidate blocked case: {case}") from error


def build_demo_learning_feedback_candidate_set() -> dict[str, object]:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        TaskClosureFromOutcomeEvaluationRecord,
        TaskClosureSafetyAudit,
    )

    payloads = (
        build_demo_progress_learning_feedback_candidate(),
        build_demo_expected_effect_failed_learning_feedback_candidate(),
        build_demo_unknown_outcome_learning_feedback_candidate(),
    )
    candidates = tuple(
        LearningFeedbackCandidateRecord.from_dict(payload["learning_feedback_candidate"])
        for payload in payloads
    )
    packets = tuple(
        LearningFeedbackCandidateEvidencePacket.from_dict(
            payload["learning_feedback_evidence_packet"]
        )
        for payload in payloads
    )
    candidate_set = build_learning_feedback_candidate_set(
        candidates=candidates,
        evidence_packets=packets,
    )
    audit = build_learning_feedback_candidate_safety_audit(
        candidate_set=candidate_set,
        task_closures=tuple(
            TaskClosureFromOutcomeEvaluationRecord.from_dict(
                payload["source_task_closure"]
            )
            for payload in payloads
        ),
        task_closure_safety_audits=tuple(
            TaskClosureSafetyAudit.from_dict(payload["source_task_closure_safety_audit"])
            for payload in payloads
        ),
    )
    return {
        "learning_feedback_candidate_set": candidate_set.to_dict(),
        "learning_feedback_candidate_safety_audit": audit.to_dict(),
        "learning_feedback_candidate_set_validation": validate_learning_feedback_candidate_set(
            candidate_set
        ),
        "learning_feedback_candidate_safety_audit_validation": (
            validate_learning_feedback_candidate_safety_audit(audit)
        ),
        "safe_claim": SAFE_CLAIM,
    }


def _build_candidate_bundle(
    package88_payload: dict[str, object],
    *,
    task_closure: TaskClosureFromOutcomeEvaluationRecord | None = None,
    task_closure_safety_audit: TaskClosureSafetyAudit | None = None,
    include_outcome_evaluation: bool = True,
    learning_feedback_approved: bool = False,
    learning_feedback_applied: bool = False,
    concept_candidate_created: bool = False,
    reviewed_concept_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    candidate_ordering_changed: bool = False,
    selected_action_changed: bool = False,
    final_action_changed: bool = False,
    direct_command_created: bool = False,
    execution_created: bool = False,
    task_behavior_changed: bool = False,
) -> dict[str, object]:
    from ashl_core_v1.task.outcome_evaluation_from_sense_observation import (
        TaskExpectedEffectReferenceRecord,
        TaskExecutionOutcomeEvaluationRecord,
        TaskGoalDeltaEvaluationRecord,
    )
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        TaskClosureFromOutcomeEvaluationRecord,
        TaskClosureSafetyAudit,
        TaskClosureSummaryRecord,
    )

    closure = task_closure or TaskClosureFromOutcomeEvaluationRecord.from_dict(
        package88_payload["task_closure_from_outcome_evaluation"]
    )
    summary = TaskClosureSummaryRecord.from_dict(package88_payload["task_closure_summary"])
    closure_audit = task_closure_safety_audit or TaskClosureSafetyAudit.from_dict(
        package88_payload["task_closure_safety_audit"]
    )
    outcome = (
        TaskExecutionOutcomeEvaluationRecord.from_dict(
            package88_payload["source_package87_outcome_evaluation"]
        )
        if include_outcome_evaluation
        else None
    )
    goal_delta = TaskGoalDeltaEvaluationRecord.from_dict(
        package88_payload["source_package87_goal_delta_evaluation"]
    )
    reference = TaskExpectedEffectReferenceRecord.from_dict(
        package88_payload["source_package87_expected_effect_reference"]
    )
    candidate = build_learning_feedback_candidate_from_task_closure(
        task_closure=closure,
        task_closure_summary=summary,
        task_closure_safety_audit=closure_audit,
        outcome_evaluation=outcome or package88_payload["source_package87_outcome_evaluation"],
        goal_delta_evaluation=goal_delta,
        expected_effect_reference=reference,
        learning_feedback_approved=learning_feedback_approved,
        learning_feedback_applied=learning_feedback_applied,
        concept_candidate_created=concept_candidate_created,
        reviewed_concept_created=reviewed_concept_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        candidate_ordering_changed=candidate_ordering_changed,
        selected_action_changed=selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_created=direct_command_created,
        execution_created=execution_created,
        task_behavior_changed=task_behavior_changed,
    )
    packet = build_learning_feedback_candidate_evidence_packet(
        candidate=candidate,
        task_closure=closure,
        outcome_evaluation=outcome,
        goal_delta_evaluation=goal_delta,
        expected_effect_reference=reference,
        learning_feedback_approved=learning_feedback_approved,
        concept_candidate_created=concept_candidate_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
    )
    candidate_set = build_learning_feedback_candidate_set(
        candidates=(candidate,),
        evidence_packets=(packet,),
    )
    safety_audit = build_learning_feedback_candidate_safety_audit(
        candidate_set=candidate_set,
        task_closures=(closure,),
        task_closure_safety_audits=(closure_audit,),
    )
    return {
        "learning_feedback_candidate": candidate.to_dict(),
        "learning_feedback_evidence_packet": packet.to_dict(),
        "learning_feedback_candidate_set": candidate_set.to_dict(),
        "learning_feedback_candidate_safety_audit": safety_audit.to_dict(),
        "learning_feedback_candidate_validation": validate_learning_feedback_candidate_record(
            candidate
        ),
        "learning_feedback_evidence_packet_validation": (
            validate_learning_feedback_candidate_evidence_packet(packet)
        ),
        "learning_feedback_candidate_set_validation": validate_learning_feedback_candidate_set(
            candidate_set
        ),
        "learning_feedback_candidate_safety_audit_validation": (
            validate_learning_feedback_candidate_safety_audit(safety_audit)
        ),
        "source_task_closure": closure.to_dict(),
        "source_task_closure_summary": summary.to_dict(),
        "source_task_closure_safety_audit": closure_audit.to_dict(),
        "source_package87_outcome_evaluation": (
            outcome.to_dict() if outcome is not None else None
        ),
        "source_package87_goal_delta_evaluation": goal_delta.to_dict(),
        "source_package87_expected_effect_reference": reference.to_dict(),
        "safe_claim": SAFE_CLAIM,
    }


def _candidate_policy(
    closure: TaskClosureFromOutcomeEvaluationRecord,
) -> tuple[str, str, str, bool]:
    if closure.closure_status == "task_closed_goal_reached":
        return ("goal_reached_candidate", "goal_completion_signal", "high", True)
    if closure.closure_status == "task_closed_with_progress":
        return (
            "successful_expected_effect_candidate",
            "positive_affordance_signal",
            "normal",
            True,
        )
    if closure.closure_status == "task_closed_expected_effect_failed":
        return (
            "failed_expected_effect_candidate",
            "negative_affordance_signal",
            "high",
            True,
        )
    if closure.closure_status == "task_closed_no_progress":
        return ("no_progress_candidate", "no_progress_signal", "normal", True)
    if closure.closure_status == "task_closed_observation_only":
        return (
            "observation_only_candidate",
            "observation_context_signal",
            "low",
            closure.available_for_learning_feedback_candidate_later,
        )
    if closure.closure_status == "task_closed_unknown":
        return ("unknown_outcome_candidate", "unknown_signal", "low", False)
    if closure.closure_status == "task_closed_system_fault":
        return ("system_fault_candidate", "system_fault_signal", "blocked", False)
    return ("system_fault_candidate", "system_fault_signal", "blocked", False)


def _candidate_summary(
    kind: str,
    closure: TaskClosureFromOutcomeEvaluationRecord,
) -> str:
    return (
        f"Learning feedback candidate {kind} from closure "
        f"{closure.closure_status}."
    )


def _candidate_reason(
    closure: TaskClosureFromOutcomeEvaluationRecord,
    outcome: TaskExecutionOutcomeEvaluationRecord,
    goal_delta: TaskGoalDeltaEvaluationRecord,
) -> str:
    return (
        f"closure={closure.closure_status}; outcome={outcome.outcome_class}; "
        f"goal_delta={goal_delta.goal_delta_class}; direct_command={closure.direct_command}"
    )


def _evidence_labels(
    closure: TaskClosureFromOutcomeEvaluationRecord,
    outcome: TaskExecutionOutcomeEvaluationRecord,
    goal_delta: TaskGoalDeltaEvaluationRecord,
) -> tuple[str, ...]:
    return _combined_trace_refs(
        (
            f"closure_status:{closure.closure_status}",
            f"outcome_class:{outcome.outcome_class}",
            f"goal_delta_class:{goal_delta.goal_delta_class}",
        ),
        tuple(f"observed_delta:{label}" for label in outcome.observed_delta_labels),
    )


def _risk_warnings(closure: TaskClosureFromOutcomeEvaluationRecord) -> tuple[str, ...]:
    warnings: list[str] = []
    if closure.closure_status == "task_closed_unknown":
        warnings.append("unknown_outcome_not_learning_ready")
    if closure.closure_status == "task_closed_system_fault":
        warnings.append("system_fault_not_learning_ready")
    if closure.closure_status == "task_closed_observation_only":
        warnings.append("observation_only_requires_goal_context_before_learning")
    return tuple(warnings)


def _counterexample_notes(
    closure: TaskClosureFromOutcomeEvaluationRecord,
) -> tuple[str, ...]:
    if closure.closure_status == "task_closed_expected_effect_failed":
        return ("counterexample_relevant_expected_effect_failed",)
    if closure.closure_status == "task_closed_no_progress":
        return ("counterexample_relevant_no_progress",)
    return ("counterexample_review_required_before_learning",)


def _missing_evidence_refs(
    *,
    closure: TaskClosureFromOutcomeEvaluationRecord,
    outcome: TaskExecutionOutcomeEvaluationRecord | None,
    goal_delta: TaskGoalDeltaEvaluationRecord | None,
    reference: TaskExpectedEffectReferenceRecord | None,
) -> list[str]:
    missing: list[str] = []
    if not closure.task_closure_id:
        missing.append("task_closure")
    if outcome is None:
        missing.append("outcome_evaluation")
    if goal_delta is None:
        missing.append("goal_delta_evaluation")
    if reference is None:
        missing.append("expected_effect_reference")
    if not closure.source_trace_refs:
        missing.append("source_trace_refs")
    if outcome is not None and not outcome.source_sense_observation_id:
        missing.append("sense_observation")
    if outcome is not None and not outcome.source_state_delta_observation_id:
        missing.append("state_delta_observation")
    return missing


def _evidence_summary(
    candidate: LearningFeedbackCandidateRecord,
    closure: TaskClosureFromOutcomeEvaluationRecord,
    outcome: TaskExecutionOutcomeEvaluationRecord | None,
    goal_delta: TaskGoalDeltaEvaluationRecord | None,
    reference: TaskExpectedEffectReferenceRecord | None,
) -> str:
    return (
        f"candidate={candidate.feedback_candidate_kind}; "
        f"closure={closure.closure_status}; "
        f"outcome={outcome.outcome_class if outcome else 'missing'}; "
        f"goal_delta={goal_delta.goal_delta_class if goal_delta else 'missing'}; "
        f"expected_effect={reference.expected_effect if reference else closure.expected_effect}"
    )


def _audit_blocked_reasons(
    *,
    closure_valid: bool,
    closure_audit_passed: bool,
    packet_valid: bool,
    candidates_valid: bool,
    set_valid: bool,
    no_approval: bool,
    no_concept: bool,
    no_memory: bool,
    no_action: bool,
    no_behavior: bool,
) -> list[str]:
    reasons: list[str] = []
    if not closure_valid or not closure_audit_passed:
        reasons.append("invalid_task_closure")
    if not packet_valid:
        reasons.append("invalid_evidence_packet")
    if not candidates_valid or not set_valid:
        reasons.append("invalid_candidate_set")
    if not no_approval:
        reasons.append("learning_feedback_approval_created")
    if not no_concept:
        reasons.append("concept_candidate_created")
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
    record_set: LearningFeedbackCandidateSet | None,
) -> str:
    if "learning_feedback_approval_created" in blocked_reasons:
        return "blocked_learning_feedback_approval_detected"
    if "concept_candidate_created" in blocked_reasons:
        return "blocked_concept_candidate_creation_detected"
    if "memory_write_performed" in blocked_reasons:
        return "blocked_memory_write_detected"
    if "action_authority_changed" in blocked_reasons:
        return "blocked_action_authority_detected"
    if "task_behavior_changed" in blocked_reasons:
        return "blocked_behavior_change_detected"
    if "invalid_task_closure" in blocked_reasons:
        return "blocked_invalid_task_closure"
    if "invalid_evidence_packet" in blocked_reasons:
        return "blocked_invalid_evidence_packet"
    if "invalid_candidate_set" in blocked_reasons:
        return "blocked_invalid_candidate_set"
    if record_set and record_set.set_status == "candidate_set_created_with_partial_evidence":
        return "passed_candidate_created_with_partial_evidence"
    return "passed_learning_feedback_candidate_only"


def _closure_valid_for_candidate(closure: TaskClosureFromOutcomeEvaluationRecord) -> bool:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        validate_task_closure_from_outcome_evaluation_record,
    )

    validation = validate_task_closure_from_outcome_evaluation_record(closure)
    return (
        validation["valid"] is True
        and closure.task_closed is True
        and not closure.learning_feedback_created
        and not closure.memory_write_performed
        and not closure.automatic_learning_approval_created
    )


def _closure_audit_passed(audit: TaskClosureSafetyAudit | None) -> bool:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        validate_task_closure_safety_audit,
    )

    if audit is None:
        return False
    validation = validate_task_closure_safety_audit(audit)
    return validation["valid"] is True and audit.audit_status in PASSING_CLOSURE_AUDIT_STATUSES


def _candidate_set_forbidden_authority(
    candidates: tuple[LearningFeedbackCandidateRecord, ...],
    packets: tuple[LearningFeedbackCandidateEvidencePacket, ...],
) -> bool:
    return bool(
        any(
            item.learning_feedback_approved
            or item.learning_feedback_applied
            or item.concept_candidate_created
            or item.reviewed_concept_created
            or item.memory_write_performed
            or item.automatic_learning_approval_created
            or item.candidate_ordering_changed
            or item.selected_action_changed
            or item.final_action_changed
            or item.direct_command_created
            or item.execution_created
            or item.task_behavior_changed
            for item in candidates
        )
        or any(
            item.learning_feedback_approved
            or item.concept_candidate_created
            or item.memory_write_performed
            or item.automatic_learning_approval_created
            for item in packets
        )
    )


def _candidate_set_id(candidate_ids: tuple[str, ...]) -> str:
    if not candidate_ids:
        return "learning_feedback_candidate_set:empty"
    seed = candidate_ids[0].replace(":", "_")
    return f"learning_feedback_candidate_set:{len(candidate_ids)}:{seed}"


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _candidate_record(
    record: LearningFeedbackCandidateRecord | dict[str, object],
) -> LearningFeedbackCandidateRecord:
    return (
        record
        if isinstance(record, LearningFeedbackCandidateRecord)
        else LearningFeedbackCandidateRecord.from_dict(dict(record))
    )


def _packet_record(
    record: LearningFeedbackCandidateEvidencePacket | dict[str, object],
) -> LearningFeedbackCandidateEvidencePacket:
    return (
        record
        if isinstance(record, LearningFeedbackCandidateEvidencePacket)
        else LearningFeedbackCandidateEvidencePacket.from_dict(dict(record))
    )


def _set_record(
    record: LearningFeedbackCandidateSet | dict[str, object],
) -> LearningFeedbackCandidateSet:
    return (
        record
        if isinstance(record, LearningFeedbackCandidateSet)
        else LearningFeedbackCandidateSet.from_dict(dict(record))
    )


def _audit_record(
    record: LearningFeedbackCandidateSafetyAudit | dict[str, object],
) -> LearningFeedbackCandidateSafetyAudit:
    return (
        record
        if isinstance(record, LearningFeedbackCandidateSafetyAudit)
        else LearningFeedbackCandidateSafetyAudit.from_dict(dict(record))
    )


def _closure_record(
    record: TaskClosureFromOutcomeEvaluationRecord | dict[str, object],
) -> TaskClosureFromOutcomeEvaluationRecord:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        TaskClosureFromOutcomeEvaluationRecord,
    )

    return (
        record
        if isinstance(record, TaskClosureFromOutcomeEvaluationRecord)
        else TaskClosureFromOutcomeEvaluationRecord.from_dict(dict(record))
    )


def _summary_record(
    record: TaskClosureSummaryRecord | dict[str, object],
) -> TaskClosureSummaryRecord:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        TaskClosureSummaryRecord,
    )

    return (
        record
        if isinstance(record, TaskClosureSummaryRecord)
        else TaskClosureSummaryRecord.from_dict(dict(record))
    )


def _closure_audit_record(
    record: TaskClosureSafetyAudit | dict[str, object],
) -> TaskClosureSafetyAudit:
    from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
        TaskClosureSafetyAudit,
    )

    return (
        record
        if isinstance(record, TaskClosureSafetyAudit)
        else TaskClosureSafetyAudit.from_dict(dict(record))
    )


def _outcome_record(
    record: TaskExecutionOutcomeEvaluationRecord | dict[str, object],
) -> TaskExecutionOutcomeEvaluationRecord:
    from ashl_core_v1.task.outcome_evaluation_from_sense_observation import (
        TaskExecutionOutcomeEvaluationRecord,
    )

    return (
        record
        if isinstance(record, TaskExecutionOutcomeEvaluationRecord)
        else TaskExecutionOutcomeEvaluationRecord.from_dict(dict(record))
    )


def _goal_delta_record(
    record: TaskGoalDeltaEvaluationRecord | dict[str, object],
) -> TaskGoalDeltaEvaluationRecord:
    from ashl_core_v1.task.outcome_evaluation_from_sense_observation import (
        TaskGoalDeltaEvaluationRecord,
    )

    return (
        record
        if isinstance(record, TaskGoalDeltaEvaluationRecord)
        else TaskGoalDeltaEvaluationRecord.from_dict(dict(record))
    )


def _reference_record(
    record: TaskExpectedEffectReferenceRecord | dict[str, object],
) -> TaskExpectedEffectReferenceRecord:
    from ashl_core_v1.task.outcome_evaluation_from_sense_observation import (
        TaskExpectedEffectReferenceRecord,
    )

    return (
        record
        if isinstance(record, TaskExpectedEffectReferenceRecord)
        else TaskExpectedEffectReferenceRecord.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
