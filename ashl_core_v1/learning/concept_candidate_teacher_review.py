"""Teacher review marks for drafted ConceptCandidate records."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.concept_candidate_from_task_closure_draft import (
    ConceptCandidateDraftRecord,
    SimpleConceptTeachingTestSeedRecord,
    build_demo_draft,
    build_demo_teaching_test_seed,
    validate_concept_candidate_draft_record,
    validate_simple_concept_teaching_test_seed,
)
from ashl_core_v1.learning.concept_candidate_schema import (
    SOURCE_ENGINE,
    validate_concept_candidate,
)


REVIEW_TASK_SCHEMA_VERSION = "learning_engine_concept_candidate_teacher_review_task_v0"
REVIEW_DECISION_SCHEMA_VERSION = "learning_engine_concept_candidate_teacher_review_decision_v0"
REVIEW_SUMMARY_SCHEMA_VERSION = "learning_engine_concept_candidate_teacher_review_summary_v0"

SAFE_CLAIM = (
    "ASHL Core v1 Learning Engine can create teacher review tasks and teacher "
    "review decisions for drafted ConceptCandidate records without approving "
    "concepts, writing memory, or changing task behavior."
)
BLOCKED_CLAIMS = (
    "no_reviewed_concept",
    "no_concept_approval",
    "no_memory_write",
    "no_task_behavior_change",
    "no_automatic_learning_approval",
    "no_core_longterm_archive_anchor_write",
)

ALLOWED_TEACHER_DECISIONS = (
    "needs_more_support",
    "scope_narrowed",
    "split_required",
    "teacher_review_ready",
    "rejected",
)
ALLOWED_REVIEW_TASK_STATUSES = {
    "pending_teacher_review",
    "blocked_invalid_draft",
    "blocked_missing_concept_candidate",
    "blocked_missing_teaching_seed",
}
ALLOWED_TEACHER_ACTORS = {"user", "teacher", "project_owner"}
ALLOWED_TEACHER_ROLES = {"project_owner", "teacher", "mentor"}
ALLOWED_DECISION_BLOCKED_REASONS = {
    "none",
    "missing_teacher_note",
    "invalid_teacher_decision",
    "invalid_review_task",
    "invalid_concept_candidate",
    "missing_counterexample_handling",
    "scope_change_required_but_missing",
    "split_labels_required_but_missing",
}
NEXT_STEP_BY_DECISION = {
    "needs_more_support": "collect_more_support_evidence",
    "scope_narrowed": "prepare_scope_narrowed_candidate",
    "split_required": "prepare_split_candidates",
    "teacher_review_ready": "prepare_future_reviewed_concept_candidate",
    "rejected": "stop_candidate",
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
class ConceptCandidateTeacherReviewTask:
    review_task_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_draft_id: str
    source_concept_candidate_id: str
    source_teaching_test_seed_id: str | None
    concept_label: str
    concept_summary: str
    support_evidence_count: int
    counterexample_evidence_count: int
    scope_status: str
    generalization_level: str
    candidate_status: str
    counterexample_handling_status: str
    teacher_visible_prompt: str
    teacher_expected_questions: tuple[str, ...]
    allowed_teacher_decisions: tuple[str, ...]
    review_required: bool
    review_task_status: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REVIEW_TASK_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_concept_candidate_teacher_review_task_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.review_task_status not in ALLOWED_REVIEW_TASK_STATUSES:
            raise ValueError(f"unknown review_task_status: {self.review_task_status}")
        object.__setattr__(
            self,
            "teacher_expected_questions",
            _tuple_of_str("teacher_expected_questions", self.teacher_expected_questions),
        )
        object.__setattr__(
            self,
            "allowed_teacher_decisions",
            _tuple_of_str("allowed_teacher_decisions", self.allowed_teacher_decisions),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ConceptCandidateTeacherReviewTask":
        return cls(**dict(data))


@dataclass(frozen=True)
class ConceptCandidateTeacherReviewDecision:
    review_decision_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_review_task_id: str
    source_concept_candidate_draft_id: str
    source_concept_candidate_id: str
    teacher_actor: str
    teacher_role: str
    teacher_decision: str
    teacher_note: str
    decision_reason_codes: tuple[str, ...]
    support_evidence_refs_confirmed: tuple[str, ...]
    counterexample_evidence_refs_confirmed: tuple[str, ...]
    requested_scope_changes: tuple[str, ...]
    requested_split_labels: tuple[str, ...]
    requested_more_evidence: tuple[str, ...]
    concept_approved: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    task_behavior_changed: bool
    automatic_approval_created: bool
    decision_valid: bool
    decision_blocked_reason: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REVIEW_DECISION_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_concept_candidate_teacher_review_decision_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.teacher_actor not in ALLOWED_TEACHER_ACTORS:
            raise ValueError(f"unknown teacher_actor: {self.teacher_actor}")
        if self.teacher_role not in ALLOWED_TEACHER_ROLES:
            raise ValueError(f"unknown teacher_role: {self.teacher_role}")
        reason = self.decision_blocked_reason or "none"
        if reason not in ALLOWED_DECISION_BLOCKED_REASONS:
            raise ValueError(f"unknown decision_blocked_reason: {reason}")
        for name in (
            "decision_reason_codes",
            "support_evidence_refs_confirmed",
            "counterexample_evidence_refs_confirmed",
            "requested_scope_changes",
            "requested_split_labels",
            "requested_more_evidence",
            "source_trace_refs",
        ):
            object.__setattr__(
                self,
                name,
                _tuple_of_str(name, getattr(self, name)),
            )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ConceptCandidateTeacherReviewDecision":
        return cls(**dict(data))


@dataclass(frozen=True)
class ConceptCandidateTeacherReviewSummary:
    review_summary_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_review_task_id: str
    source_review_decision_id: str
    source_concept_candidate_draft_id: str
    source_concept_candidate_id: str
    concept_label: str
    teacher_decision: str
    summary_text: str
    next_learning_engine_step: str
    concept_approved: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    task_behavior_changed: bool
    safe_claim: str
    blocked_claims: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REVIEW_SUMMARY_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_concept_candidate_teacher_review_summary_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.next_learning_engine_step not in set(NEXT_STEP_BY_DECISION.values()):
            raise ValueError(f"unknown next_learning_engine_step: {self.next_learning_engine_step}")
        object.__setattr__(
            self,
            "blocked_claims",
            _tuple_of_str("blocked_claims", self.blocked_claims),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ConceptCandidateTeacherReviewSummary":
        return cls(**dict(data))


def build_concept_candidate_teacher_review_task(
    draft: ConceptCandidateDraftRecord | dict[str, object],
    teaching_seed: SimpleConceptTeachingTestSeedRecord | dict[str, object] | None = None,
) -> ConceptCandidateTeacherReviewTask:
    draft_record = _draft(draft)
    draft_validation = validate_concept_candidate_draft_record(draft_record)
    seed_record = _seed(teaching_seed) if teaching_seed is not None else None
    seed_validation = (
        validate_simple_concept_teaching_test_seed(seed_record)
        if seed_record is not None
        else {"valid": True, "error_codes": []}
    )
    if not draft_validation["valid"]:
        return _blocked_review_task(draft_record, seed_record, "blocked_invalid_draft")
    if draft_record.drafted_concept_candidate is None:
        return _blocked_review_task(draft_record, seed_record, "blocked_missing_concept_candidate")
    if seed_record is not None and not seed_validation["valid"]:
        return _blocked_review_task(draft_record, seed_record, "blocked_missing_teaching_seed")

    candidate = draft_record.drafted_concept_candidate
    return ConceptCandidateTeacherReviewTask(
        review_task_id=f"concept_review_task:{draft_record.concept_candidate_draft_id}",
        schema_version=REVIEW_TASK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_draft_id=draft_record.concept_candidate_draft_id,
        source_concept_candidate_id=candidate.concept_candidate_id,
        source_teaching_test_seed_id=(
            seed_record.teaching_test_seed_id if seed_record is not None else None
        ),
        concept_label=candidate.concept_label,
        concept_summary=candidate.concept_summary,
        support_evidence_count=len(candidate.support_evidence_refs),
        counterexample_evidence_count=len(candidate.counterexample_evidence_refs),
        scope_status=candidate.scope_statement.scope_status,
        generalization_level=candidate.generalization_level,
        candidate_status=candidate.candidate_status,
        counterexample_handling_status=candidate.counterexample_handling_status,
        teacher_visible_prompt=(
            seed_record.teacher_visible_prompt
            if seed_record is not None
            else "Inspect this drafted concept candidate before any later review package."
        ),
        teacher_expected_questions=(
            seed_record.teacher_expected_questions
            if seed_record is not None
            else ("What support evidence does this concept candidate have?",)
        ),
        allowed_teacher_decisions=ALLOWED_TEACHER_DECISIONS,
        review_required=True,
        review_task_status="pending_teacher_review",
        source_trace_refs=draft_record.source_trace_refs,
    )


def validate_concept_candidate_teacher_review_task(
    task: ConceptCandidateTeacherReviewTask | dict[str, object],
) -> dict[str, object]:
    try:
        record = _task(task)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_review_task:{error}"]}
    errors: list[str] = []
    if not record.review_task_id:
        errors.append("missing_review_task_id")
    if not record.source_concept_candidate_draft_id:
        errors.append("missing_source_concept_candidate_draft_id")
    if record.review_task_status == "pending_teacher_review":
        if not record.source_concept_candidate_id:
            errors.append("missing_source_concept_candidate_id")
        if not record.concept_label:
            errors.append("missing_concept_label")
    if tuple(record.allowed_teacher_decisions) != ALLOWED_TEACHER_DECISIONS:
        errors.append("allowed_teacher_decisions_mismatch")
    if record.review_required is not True:
        errors.append("review_required_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "review_task_id": record.review_task_id,
        "review_task_status": record.review_task_status,
        "support_evidence_count": record.support_evidence_count,
        "counterexample_evidence_count": record.counterexample_evidence_count,
        "allowed_teacher_decisions": record.allowed_teacher_decisions,
    }


def build_concept_candidate_teacher_review_decision(
    task: ConceptCandidateTeacherReviewTask | dict[str, object],
    *,
    teacher_decision: str,
    teacher_note: str,
    teacher_actor: str = "user",
    teacher_role: str = "project_owner",
    decision_reason_codes: tuple[str, ...] = (),
    support_evidence_refs_confirmed: tuple[str, ...] = (),
    counterexample_evidence_refs_confirmed: tuple[str, ...] = (),
    requested_scope_changes: tuple[str, ...] = (),
    requested_split_labels: tuple[str, ...] = (),
    requested_more_evidence: tuple[str, ...] = (),
) -> ConceptCandidateTeacherReviewDecision:
    task_record = _task(task)
    blocked_reason = _decision_blocked_reason(
        task_record,
        teacher_decision=teacher_decision,
        teacher_note=teacher_note,
        decision_reason_codes=decision_reason_codes,
        support_evidence_refs_confirmed=support_evidence_refs_confirmed,
        counterexample_evidence_refs_confirmed=counterexample_evidence_refs_confirmed,
        requested_scope_changes=requested_scope_changes,
        requested_split_labels=requested_split_labels,
        requested_more_evidence=requested_more_evidence,
    )
    return ConceptCandidateTeacherReviewDecision(
        review_decision_id=f"concept_review_decision:{task_record.review_task_id}:{teacher_decision}",
        schema_version=REVIEW_DECISION_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_review_task_id=task_record.review_task_id,
        source_concept_candidate_draft_id=task_record.source_concept_candidate_draft_id,
        source_concept_candidate_id=task_record.source_concept_candidate_id,
        teacher_actor=teacher_actor,
        teacher_role=teacher_role,
        teacher_decision=teacher_decision,
        teacher_note=teacher_note,
        decision_reason_codes=decision_reason_codes,
        support_evidence_refs_confirmed=support_evidence_refs_confirmed,
        counterexample_evidence_refs_confirmed=counterexample_evidence_refs_confirmed,
        requested_scope_changes=requested_scope_changes,
        requested_split_labels=requested_split_labels,
        requested_more_evidence=requested_more_evidence,
        concept_approved=False,
        reviewed_concept_created=False,
        memory_write_performed=False,
        task_behavior_changed=False,
        automatic_approval_created=False,
        decision_valid=blocked_reason == "none",
        decision_blocked_reason=blocked_reason,
        source_trace_refs=task_record.source_trace_refs,
    )


def validate_concept_candidate_teacher_review_decision(
    decision: ConceptCandidateTeacherReviewDecision | dict[str, object],
) -> dict[str, object]:
    try:
        record = _decision(decision)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_review_decision:{error}"]}
    errors: list[str] = []
    if not record.review_decision_id:
        errors.append("missing_review_decision_id")
    if not record.source_review_task_id:
        errors.append("missing_source_review_task_id")
    if record.teacher_decision not in ALLOWED_TEACHER_DECISIONS:
        errors.append("invalid_teacher_decision")
    if not record.teacher_note:
        errors.append("missing_teacher_note")
    expected_reason = "none" if not errors else record.decision_blocked_reason
    if record.decision_valid and record.decision_blocked_reason != "none":
        errors.append("decision_valid_with_blocked_reason")
    if not record.decision_valid and record.decision_blocked_reason == "none":
        errors.append("decision_invalid_without_blocked_reason")
    if expected_reason == "none" and record.decision_blocked_reason != "none":
        errors.append("unexpected_decision_blocked_reason")
    if record.concept_approved is not False:
        errors.append("concept_approved_true")
    if record.reviewed_concept_created is not False:
        errors.append("reviewed_concept_created_true")
    if record.memory_write_performed is not False:
        errors.append("memory_write_performed_true")
    if record.task_behavior_changed is not False:
        errors.append("task_behavior_changed_true")
    if record.automatic_approval_created is not False:
        errors.append("automatic_approval_created_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "review_decision_id": record.review_decision_id,
        "teacher_decision": record.teacher_decision,
        "decision_valid": record.decision_valid,
        "decision_blocked_reason": record.decision_blocked_reason,
        "concept_approved": record.concept_approved,
        "reviewed_concept_created": record.reviewed_concept_created,
        "memory_write_performed": record.memory_write_performed,
        "task_behavior_changed": record.task_behavior_changed,
        "automatic_approval_created": record.automatic_approval_created,
    }


def build_concept_candidate_teacher_review_summary(
    task: ConceptCandidateTeacherReviewTask | dict[str, object],
    decision: ConceptCandidateTeacherReviewDecision | dict[str, object],
) -> ConceptCandidateTeacherReviewSummary:
    task_record = _task(task)
    decision_record = _decision(decision)
    next_step = (
        NEXT_STEP_BY_DECISION.get(decision_record.teacher_decision, "stop_candidate")
        if decision_record.decision_valid
        else "stop_candidate"
    )
    return ConceptCandidateTeacherReviewSummary(
        review_summary_id=f"concept_review_summary:{decision_record.review_decision_id}",
        schema_version=REVIEW_SUMMARY_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_review_task_id=task_record.review_task_id,
        source_review_decision_id=decision_record.review_decision_id,
        source_concept_candidate_draft_id=task_record.source_concept_candidate_draft_id,
        source_concept_candidate_id=task_record.source_concept_candidate_id,
        concept_label=task_record.concept_label,
        teacher_decision=decision_record.teacher_decision,
        summary_text=(
            f"Teacher marked {task_record.concept_label} as "
            f"{decision_record.teacher_decision}; no concept approval or memory write occurred."
        ),
        next_learning_engine_step=next_step,
        concept_approved=False,
        reviewed_concept_created=False,
        memory_write_performed=False,
        task_behavior_changed=False,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        source_trace_refs=task_record.source_trace_refs,
    )


def validate_concept_candidate_teacher_review_summary(
    summary: ConceptCandidateTeacherReviewSummary | dict[str, object],
) -> dict[str, object]:
    try:
        record = _summary(summary)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_review_summary:{error}"]}
    errors: list[str] = []
    if not record.review_summary_id:
        errors.append("missing_review_summary_id")
    if not record.source_review_task_id:
        errors.append("missing_source_review_task_id")
    if record.teacher_decision in NEXT_STEP_BY_DECISION:
        expected = NEXT_STEP_BY_DECISION[record.teacher_decision]
        if record.next_learning_engine_step != expected:
            errors.append("next_learning_engine_step_mismatch")
    if record.concept_approved is not False:
        errors.append("concept_approved_true")
    if record.reviewed_concept_created is not False:
        errors.append("reviewed_concept_created_true")
    if record.memory_write_performed is not False:
        errors.append("memory_write_performed_true")
    if record.task_behavior_changed is not False:
        errors.append("task_behavior_changed_true")
    if not set(BLOCKED_CLAIMS).issubset(set(record.blocked_claims)):
        errors.append("blocked_claims_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "review_summary_id": record.review_summary_id,
        "teacher_decision": record.teacher_decision,
        "next_learning_engine_step": record.next_learning_engine_step,
        "concept_approved": record.concept_approved,
        "reviewed_concept_created": record.reviewed_concept_created,
        "memory_write_performed": record.memory_write_performed,
        "task_behavior_changed": record.task_behavior_changed,
    }


def build_demo_needs_more_support_review() -> dict[str, object]:
    return build_demo_review(
        demo="blocked",
        decision="needs_more_support",
        teacher_note="Support is too thin; gather another blocked-front support case.",
        decision_reason_codes=("insufficient_support",),
        requested_more_evidence=("another blocked front direct-forward attempt",),
    )


def build_demo_scope_narrowed_review() -> dict[str, object]:
    return build_demo_review(
        demo="blocked",
        decision="scope_narrowed",
        teacher_note="Narrow front_blocked_affordance to wall-like blocked fronts only.",
        requested_scope_changes=("front_blocked_affordance -> front_wall_blocked_affordance",),
    )


def build_demo_split_required_review() -> dict[str, object]:
    return build_demo_review(
        demo="blocked",
        decision="split_required",
        teacher_note="Counterexample means the broad front_blocked label must split.",
        counterexample_evidence_refs_confirmed=("teacher_counterexample:front_blocked_step_forward_success",),
        requested_split_labels=(
            "front_wall_blocked",
            "front_box_pushable",
            "front_temporary_blocked",
            "front_unknown_obstacle",
        ),
    )


def build_demo_teacher_review_ready_review() -> dict[str, object]:
    return build_demo_review(
        demo="unknown",
        decision="teacher_review_ready",
        teacher_note="Support is sufficient for future reviewed-concept preparation in this bounded context.",
        support_evidence_refs_confirmed=("task_closure:unknown_needs_observe",),
    )


def build_demo_rejected_review() -> dict[str, object]:
    return build_demo_review(
        demo="blocked",
        decision="rejected",
        teacher_note="Reject this candidate because the label is not useful enough.",
    )


def build_demo_review(
    *,
    demo: str,
    decision: str,
    teacher_note: str,
    decision_reason_codes: tuple[str, ...] = (),
    support_evidence_refs_confirmed: tuple[str, ...] = (),
    counterexample_evidence_refs_confirmed: tuple[str, ...] = (),
    requested_scope_changes: tuple[str, ...] = (),
    requested_split_labels: tuple[str, ...] = (),
    requested_more_evidence: tuple[str, ...] = (),
) -> dict[str, object]:
    draft = build_demo_draft(demo)
    seed = build_demo_teaching_test_seed(demo)
    task = build_concept_candidate_teacher_review_task(draft, seed)
    decision_record = build_concept_candidate_teacher_review_decision(
        task,
        teacher_decision=decision,
        teacher_note=teacher_note,
        decision_reason_codes=decision_reason_codes,
        support_evidence_refs_confirmed=support_evidence_refs_confirmed
        or _default_support_refs(task, decision),
        counterexample_evidence_refs_confirmed=counterexample_evidence_refs_confirmed
        or _default_counterexample_refs(decision),
        requested_scope_changes=requested_scope_changes,
        requested_split_labels=requested_split_labels,
        requested_more_evidence=requested_more_evidence,
    )
    summary = build_concept_candidate_teacher_review_summary(task, decision_record)
    return {
        "review_task": task.to_dict(),
        "review_decision": decision_record.to_dict(),
        "review_summary": summary.to_dict(),
        "review_task_validation": validate_concept_candidate_teacher_review_task(task),
        "review_decision_validation": validate_concept_candidate_teacher_review_decision(decision_record),
        "review_summary_validation": validate_concept_candidate_teacher_review_summary(summary),
    }


def _decision_blocked_reason(
    task: ConceptCandidateTeacherReviewTask,
    *,
    teacher_decision: str,
    teacher_note: str,
    decision_reason_codes: tuple[str, ...],
    support_evidence_refs_confirmed: tuple[str, ...],
    counterexample_evidence_refs_confirmed: tuple[str, ...],
    requested_scope_changes: tuple[str, ...],
    requested_split_labels: tuple[str, ...],
    requested_more_evidence: tuple[str, ...],
) -> str:
    task_validation = validate_concept_candidate_teacher_review_task(task)
    if not task_validation["valid"] or task.review_task_status != "pending_teacher_review":
        return "invalid_review_task"
    if teacher_decision not in ALLOWED_TEACHER_DECISIONS:
        return "invalid_teacher_decision"
    if not teacher_note:
        return "missing_teacher_note"
    if teacher_decision == "needs_more_support":
        if not requested_more_evidence and "insufficient_support" not in decision_reason_codes:
            return "missing_counterexample_handling"
    if teacher_decision == "scope_narrowed" and not requested_scope_changes:
        return "scope_change_required_but_missing"
    if teacher_decision == "split_required":
        if not requested_split_labels:
            return "split_labels_required_but_missing"
        if not counterexample_evidence_refs_confirmed and task.counterexample_evidence_count <= 0:
            return "missing_counterexample_handling"
    if teacher_decision == "teacher_review_ready":
        if not support_evidence_refs_confirmed:
            return "missing_counterexample_handling"
        if task.counterexample_evidence_count > 0 and "counterexample_scope_accepted" not in decision_reason_codes:
            return "missing_counterexample_handling"
    return "none"


def _blocked_review_task(
    draft: ConceptCandidateDraftRecord,
    seed: SimpleConceptTeachingTestSeedRecord | None,
    status: str,
) -> ConceptCandidateTeacherReviewTask:
    return ConceptCandidateTeacherReviewTask(
        review_task_id=f"concept_review_task:{draft.concept_candidate_draft_id}:{status}",
        schema_version=REVIEW_TASK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_draft_id=draft.concept_candidate_draft_id,
        source_concept_candidate_id="",
        source_teaching_test_seed_id=seed.teaching_test_seed_id if seed else None,
        concept_label="",
        concept_summary="",
        support_evidence_count=0,
        counterexample_evidence_count=0,
        scope_status="unknown",
        generalization_level="single_case",
        candidate_status="invalid",
        counterexample_handling_status="not_checked",
        teacher_visible_prompt="Concept candidate draft is blocked and cannot be reviewed.",
        teacher_expected_questions=(),
        allowed_teacher_decisions=ALLOWED_TEACHER_DECISIONS,
        review_required=True,
        review_task_status=status,
        source_trace_refs=draft.source_trace_refs,
    )


def _default_support_refs(
    task: ConceptCandidateTeacherReviewTask,
    decision: str,
) -> tuple[str, ...]:
    if decision == "teacher_review_ready" and task.source_trace_refs:
        return (task.source_trace_refs[0],)
    return ()


def _default_counterexample_refs(decision: str) -> tuple[str, ...]:
    if decision == "split_required":
        return ("teacher_counterexample:front_blocked_step_forward_success",)
    return ()


def _draft(
    draft: ConceptCandidateDraftRecord | dict[str, object],
) -> ConceptCandidateDraftRecord:
    return (
        draft
        if isinstance(draft, ConceptCandidateDraftRecord)
        else ConceptCandidateDraftRecord.from_dict(dict(draft))
    )


def _seed(
    seed: SimpleConceptTeachingTestSeedRecord | dict[str, object] | None,
) -> SimpleConceptTeachingTestSeedRecord | None:
    if seed is None:
        return None
    return (
        seed
        if isinstance(seed, SimpleConceptTeachingTestSeedRecord)
        else SimpleConceptTeachingTestSeedRecord.from_dict(dict(seed))
    )


def _task(
    task: ConceptCandidateTeacherReviewTask | dict[str, object],
) -> ConceptCandidateTeacherReviewTask:
    return (
        task
        if isinstance(task, ConceptCandidateTeacherReviewTask)
        else ConceptCandidateTeacherReviewTask.from_dict(dict(task))
    )


def _decision(
    decision: ConceptCandidateTeacherReviewDecision | dict[str, object],
) -> ConceptCandidateTeacherReviewDecision:
    return (
        decision
        if isinstance(decision, ConceptCandidateTeacherReviewDecision)
        else ConceptCandidateTeacherReviewDecision.from_dict(dict(decision))
    )


def _summary(
    summary: ConceptCandidateTeacherReviewSummary | dict[str, object],
) -> ConceptCandidateTeacherReviewSummary:
    return (
        summary
        if isinstance(summary, ConceptCandidateTeacherReviewSummary)
        else ConceptCandidateTeacherReviewSummary.from_dict(dict(summary))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
