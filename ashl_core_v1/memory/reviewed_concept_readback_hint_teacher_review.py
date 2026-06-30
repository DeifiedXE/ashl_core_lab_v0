"""Teacher review records for ReviewedConcept readback hint candidates."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.memory.reviewed_concept_readback_hint_candidate import (
    ReviewedConceptReadbackHintCandidate,
    ReviewedConceptReadbackHintCandidateSafetyAudit,
    ReviewedConceptReadbackHintCandidateSet,
    build_demo_reviewed_concept_readback_hint_candidate_set,
    validate_reviewed_concept_readback_hint_candidate,
    validate_reviewed_concept_readback_hint_candidate_safety_audit,
    validate_reviewed_concept_readback_hint_candidate_set,
)


SOURCE_ENGINE = "memory_engine"
HINT_CANDIDATE_TEACHER_REVIEW_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_readback_hint_teacher_review_v0"
)
HINT_CANDIDATE_SET_TEACHER_REVIEW_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_readback_hint_candidate_set_teacher_review_v0"
)
HINT_TEACHER_REVIEW_SAFETY_AUDIT_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_readback_hint_teacher_review_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Memory Engine can perform teacher review over ReviewedConcept "
    "readback hint candidates and mark them approved, held, rejected, needing "
    "more evidence, or conflict-detected for future hint preparation, without "
    "creating actual TaskWorkingMemoryReadbackHint records, mutating Working "
    "Memory, changing task behavior, selecting actions, executing actions, or "
    "writing memory layers."
)
BLOCKED_CLAIMS = (
    "no_actual_task_working_memory_hint",
    "no_working_memory_mutation",
    "no_task_behavior_change",
    "no_candidate_ordering_change",
    "no_action_selection",
    "no_action_execution",
    "no_core_longterm_archive_anchor_write",
    "no_automatic_learning_approval",
)

ALLOWED_TEACHER_REVIEW_STATUSES = {
    "approved_for_future_hint_preparation",
    "held_for_more_evidence",
    "rejected",
    "needs_more_evidence",
    "conflict_detected",
    "blocked_invalid_candidate",
    "blocked_forbidden_authority_detected",
}
ALLOWED_REVIEW_ACTOR_ROLES = {"teacher", "project_owner", "system_demo"}
ALLOWED_REVIEW_SOURCES = {"explicit_teacher_review", "demo_review"}
ALLOWED_SET_REVIEW_STATUSES = {
    "reviewed_with_approved_candidates",
    "reviewed_all_held_or_rejected",
    "needs_more_evidence",
    "conflict_detected",
    "blocked_invalid_candidate_set",
    "blocked_invalid_candidate_reviews",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_hint_candidate_set",
    "blocked_invalid_candidate_reviews",
    "blocked_invalid_teacher_review_source",
    "blocked_invalid_approval_scope",
    "blocked_forbidden_hint_creation_detected",
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
class ReviewedConceptReadbackHintCandidateTeacherReview:
    hint_candidate_teacher_review_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_candidate_id: str
    source_hint_candidate_set_id: str
    source_hint_candidate_safety_audit_id: str
    concept_label: str
    hint_label: str
    hint_kind: str
    hint_summary: str
    scope_warning: str | None
    counterexample_warning: str | None
    teacher_review_status: str
    teacher_review_reason: str
    teacher_review_text: str
    review_actor: str
    review_actor_role: str
    review_source: str
    approved_for_future_hint_preparation: bool
    approved_for_actual_hint_creation: bool
    approved_for_working_memory_application: bool
    approved_for_task_behavior_change: bool
    approved_for_candidate_ordering_change: bool
    approved_for_action_selection: bool
    approved_for_action_execution: bool
    approved_for_memory_layer_write: bool
    requires_next_stage_hint_preparation_package: bool
    requires_task_engine_application_package: bool
    requires_counterexample_monitoring: bool
    actual_task_working_memory_hint_created: bool
    applied_to_working_memory: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    candidate_ordering_changed: bool
    action_selection_created: bool
    action_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HINT_CANDIDATE_TEACHER_REVIEW_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_readback_hint_teacher_review_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.teacher_review_status not in ALLOWED_TEACHER_REVIEW_STATUSES:
            raise ValueError(f"unknown teacher_review_status: {self.teacher_review_status}")
        if self.review_actor_role not in ALLOWED_REVIEW_ACTOR_ROLES:
            raise ValueError(f"unknown review_actor_role: {self.review_actor_role}")
        if self.review_source not in ALLOWED_REVIEW_SOURCES:
            raise ValueError(f"unknown review_source: {self.review_source}")
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
    ) -> "ReviewedConceptReadbackHintCandidateTeacherReview":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptReadbackHintCandidateSetTeacherReview:
    hint_candidate_set_teacher_review_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_candidate_set_id: str
    source_hint_candidate_safety_audit_id: str
    concept_label: str
    candidate_count: int
    candidate_labels: tuple[str, ...]
    candidate_reviews: tuple[ReviewedConceptReadbackHintCandidateTeacherReview, ...]
    approved_candidate_ids: tuple[str, ...]
    held_candidate_ids: tuple[str, ...]
    rejected_candidate_ids: tuple[str, ...]
    needs_more_evidence_candidate_ids: tuple[str, ...]
    conflict_detected_candidate_ids: tuple[str, ...]
    set_review_status: str
    set_review_summary: str
    has_approved_candidates_for_future_preparation: bool
    approved_for_actual_hint_creation: bool
    approved_for_working_memory_application: bool
    approved_for_task_behavior_change: bool
    actual_task_working_memory_hint_created: bool
    applied_to_working_memory: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HINT_CANDIDATE_SET_TEACHER_REVIEW_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_readback_hint_candidate_set_teacher_review_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.set_review_status not in ALLOWED_SET_REVIEW_STATUSES:
            raise ValueError(f"unknown set_review_status: {self.set_review_status}")
        object.__setattr__(
            self,
            "candidate_reviews",
            tuple(
                item
                if isinstance(item, ReviewedConceptReadbackHintCandidateTeacherReview)
                else ReviewedConceptReadbackHintCandidateTeacherReview.from_dict(dict(item))
                for item in self.candidate_reviews
            ),
        )
        for name in (
            "candidate_labels",
            "approved_candidate_ids",
            "held_candidate_ids",
            "rejected_candidate_ids",
            "needs_more_evidence_candidate_ids",
            "conflict_detected_candidate_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptReadbackHintCandidateSetTeacherReview":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptReadbackHintTeacherReviewSafetyAudit:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_candidate_set_id: str | None
    source_hint_candidate_set_teacher_review_id: str | None
    hint_candidate_set_valid: bool
    candidate_reviews_valid: bool
    teacher_review_source_valid: bool
    approval_scope_valid: bool
    no_actual_task_working_memory_hint_created: bool
    no_working_memory_mutation: bool
    no_task_behavior_change: bool
    no_candidate_ordering_change: bool
    no_action_selection: bool
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
        if self.schema_version != HINT_TEACHER_REVIEW_SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_readback_hint_teacher_review_safety_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
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
    ) -> "ReviewedConceptReadbackHintTeacherReviewSafetyAudit":
        return cls(**dict(data))


def build_reviewed_concept_readback_hint_candidate_teacher_review(
    *,
    hint_candidate: ReviewedConceptReadbackHintCandidate | dict[str, object],
    hint_candidate_set: ReviewedConceptReadbackHintCandidateSet | dict[str, object],
    hint_candidate_safety_audit: ReviewedConceptReadbackHintCandidateSafetyAudit | dict[str, object],
    teacher_review_status: str,
    teacher_review_reason: str = "",
    teacher_review_text: str = "",
    review_actor: str = "system_demo",
    review_actor_role: str = "system_demo",
    review_source: str = "demo_review",
) -> ReviewedConceptReadbackHintCandidateTeacherReview:
    candidate = _candidate(hint_candidate)
    candidate_set = _candidate_set(hint_candidate_set)
    candidate_safety = _candidate_safety_audit(hint_candidate_safety_audit)
    status = _review_status(candidate, teacher_review_status)
    return ReviewedConceptReadbackHintCandidateTeacherReview(
        hint_candidate_teacher_review_id=(
            f"reviewed_concept_readback_hint_candidate_teacher_review:"
            f"{candidate.readback_hint_candidate_id}:{status}"
        ),
        schema_version=HINT_CANDIDATE_TEACHER_REVIEW_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=candidate.source_reviewed_concept_id,
        source_hint_candidate_id=candidate.readback_hint_candidate_id,
        source_hint_candidate_set_id=candidate_set.hint_candidate_set_id,
        source_hint_candidate_safety_audit_id=candidate_safety.safety_audit_id,
        concept_label=candidate.concept_label,
        hint_label=candidate.hint_label,
        hint_kind=candidate.hint_kind,
        hint_summary=candidate.hint_summary,
        scope_warning=candidate.scope_warning,
        counterexample_warning=candidate.counterexample_warning,
        teacher_review_status=status,
        teacher_review_reason=teacher_review_reason or _review_reason(status),
        teacher_review_text=teacher_review_text or _review_text(status, review_source),
        review_actor=review_actor,
        review_actor_role=review_actor_role,
        review_source=review_source,
        approved_for_future_hint_preparation=status
        == "approved_for_future_hint_preparation",
        approved_for_actual_hint_creation=False,
        approved_for_working_memory_application=False,
        approved_for_task_behavior_change=False,
        approved_for_candidate_ordering_change=False,
        approved_for_action_selection=False,
        approved_for_action_execution=False,
        approved_for_memory_layer_write=False,
        requires_next_stage_hint_preparation_package=True,
        requires_task_engine_application_package=True,
        requires_counterexample_monitoring=True,
        actual_task_working_memory_hint_created=False,
        applied_to_working_memory=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        candidate_ordering_changed=False,
        action_selection_created=False,
        action_execution_created=False,
        memory_layer_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_combined_trace_refs(
            candidate.source_trace_refs,
            candidate_set.source_trace_refs,
            candidate_safety.source_trace_refs,
        ),
    )


def validate_reviewed_concept_readback_hint_candidate_teacher_review(
    review: ReviewedConceptReadbackHintCandidateTeacherReview | dict[str, object],
) -> dict[str, object]:
    try:
        record = _candidate_review(review)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_candidate_review:{error}"]}
    errors: list[str] = []
    if record.teacher_review_status.startswith("blocked_"):
        errors.append(record.teacher_review_status)
    if record.review_source == "demo_review" and record.review_actor_role != "system_demo":
        errors.append("invalid_demo_review_actor_role")
    if record.review_source == "explicit_teacher_review":
        if record.review_actor_role not in {"teacher", "project_owner"}:
            errors.append("invalid_explicit_review_actor_role")
        if not record.teacher_review_text.strip():
            errors.append("missing_teacher_review_text")
    if not _approval_scope_valid_for_review(record):
        errors.append("invalid_approval_scope")
    for flag in (
        "requires_next_stage_hint_preparation_package",
        "requires_task_engine_application_package",
        "requires_counterexample_monitoring",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    for flag in (
        "actual_task_working_memory_hint_created",
        "applied_to_working_memory",
        "working_memory_mutated",
        "task_behavior_changed",
        "candidate_ordering_changed",
        "action_selection_created",
        "action_execution_created",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "hint_candidate_teacher_review_id": record.hint_candidate_teacher_review_id,
        "teacher_review_status": record.teacher_review_status,
        "source_hint_candidate_id": record.source_hint_candidate_id,
    }


def build_reviewed_concept_readback_hint_candidate_set_teacher_review(
    *,
    hint_candidate_set: ReviewedConceptReadbackHintCandidateSet | dict[str, object],
    hint_candidate_safety_audit: ReviewedConceptReadbackHintCandidateSafetyAudit | dict[str, object],
    review_decisions: dict[str, str] | None = None,
    review_actor: str = "system_demo",
    review_actor_role: str = "system_demo",
    review_source: str = "demo_review",
    teacher_review_text: str = "",
) -> ReviewedConceptReadbackHintCandidateSetTeacherReview:
    candidate_set = _candidate_set(hint_candidate_set)
    candidate_safety = _candidate_safety_audit(hint_candidate_safety_audit)
    candidate_set_valid = bool(
        validate_reviewed_concept_readback_hint_candidate_set(candidate_set)["valid"]
    ) and candidate_set.set_status == "candidate_set_created"
    decisions = review_decisions or _demo_review_decisions(candidate_set)
    candidate_reviews = tuple(
        build_reviewed_concept_readback_hint_candidate_teacher_review(
            hint_candidate=candidate,
            hint_candidate_set=candidate_set,
            hint_candidate_safety_audit=candidate_safety,
            teacher_review_status=decisions.get(
                candidate.readback_hint_candidate_id,
                decisions.get(candidate.hint_label, "held_for_more_evidence"),
            ),
            teacher_review_reason=_decision_reason(
                decisions.get(
                    candidate.readback_hint_candidate_id,
                    decisions.get(candidate.hint_label, "held_for_more_evidence"),
                )
            ),
            teacher_review_text=teacher_review_text,
            review_actor=review_actor,
            review_actor_role=review_actor_role,
            review_source=review_source,
        )
        for candidate in candidate_set.hint_candidates
    )
    candidate_reviews_valid = all(
        validate_reviewed_concept_readback_hint_candidate_teacher_review(review)["valid"]
        for review in candidate_reviews
    )
    status = _set_review_status(
        candidate_set_valid=candidate_set_valid,
        candidate_reviews=candidate_reviews,
        candidate_reviews_valid=candidate_reviews_valid,
    )
    approved_ids = tuple(
        review.source_hint_candidate_id
        for review in candidate_reviews
        if review.teacher_review_status == "approved_for_future_hint_preparation"
    )
    held_ids = tuple(
        review.source_hint_candidate_id
        for review in candidate_reviews
        if review.teacher_review_status == "held_for_more_evidence"
    )
    rejected_ids = tuple(
        review.source_hint_candidate_id
        for review in candidate_reviews
        if review.teacher_review_status == "rejected"
    )
    needs_more_ids = tuple(
        review.source_hint_candidate_id
        for review in candidate_reviews
        if review.teacher_review_status == "needs_more_evidence"
    )
    conflict_ids = tuple(
        review.source_hint_candidate_id
        for review in candidate_reviews
        if review.teacher_review_status == "conflict_detected"
    )
    return ReviewedConceptReadbackHintCandidateSetTeacherReview(
        hint_candidate_set_teacher_review_id=(
            "reviewed_concept_readback_hint_candidate_set_teacher_review:"
            f"{candidate_set.source_reviewed_concept_id}"
        ),
        schema_version=HINT_CANDIDATE_SET_TEACHER_REVIEW_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=candidate_set.source_reviewed_concept_id,
        source_hint_candidate_set_id=candidate_set.hint_candidate_set_id,
        source_hint_candidate_safety_audit_id=candidate_safety.safety_audit_id,
        concept_label=candidate_set.concept_label,
        candidate_count=candidate_set.candidate_count,
        candidate_labels=candidate_set.candidate_labels,
        candidate_reviews=candidate_reviews,
        approved_candidate_ids=approved_ids,
        held_candidate_ids=held_ids,
        rejected_candidate_ids=rejected_ids,
        needs_more_evidence_candidate_ids=needs_more_ids,
        conflict_detected_candidate_ids=conflict_ids,
        set_review_status=status,
        set_review_summary=_set_review_summary(status),
        has_approved_candidates_for_future_preparation=bool(approved_ids)
        and status == "reviewed_with_approved_candidates",
        approved_for_actual_hint_creation=False,
        approved_for_working_memory_application=False,
        approved_for_task_behavior_change=False,
        actual_task_working_memory_hint_created=False,
        applied_to_working_memory=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        memory_layer_write_performed=False,
        source_trace_refs=_combined_trace_refs(
            candidate_set.source_trace_refs,
            candidate_safety.source_trace_refs,
            *(review.source_trace_refs for review in candidate_reviews),
        ),
    )


def validate_reviewed_concept_readback_hint_candidate_set_teacher_review(
    review: ReviewedConceptReadbackHintCandidateSetTeacherReview | dict[str, object],
) -> dict[str, object]:
    try:
        record = _candidate_set_review(review)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_candidate_set_review:{error}"]}
    errors: list[str] = []
    if record.set_review_status.startswith("blocked_"):
        errors.append(record.set_review_status)
    if record.candidate_count != len(record.candidate_reviews):
        errors.append("candidate_review_count_mismatch")
    if record.candidate_labels != tuple(review.hint_label for review in record.candidate_reviews):
        errors.append("candidate_labels_mismatch")
    candidate_review_validations = [
        validate_reviewed_concept_readback_hint_candidate_teacher_review(item)
        for item in record.candidate_reviews
    ]
    if any(not validation["valid"] for validation in candidate_review_validations):
        errors.append("candidate_review_invalid")
    if record.has_approved_candidates_for_future_preparation != bool(
        record.approved_candidate_ids
    ):
        errors.append("approved_candidate_flag_mismatch")
    if record.approved_candidate_ids and record.set_review_status != "reviewed_with_approved_candidates":
        errors.append("approved_status_mismatch")
    if not record.approved_candidate_ids and record.set_review_status == "reviewed_with_approved_candidates":
        errors.append("missing_approved_candidates")
    for flag in (
        "approved_for_actual_hint_creation",
        "approved_for_working_memory_application",
        "approved_for_task_behavior_change",
        "actual_task_working_memory_hint_created",
        "applied_to_working_memory",
        "working_memory_mutated",
        "task_behavior_changed",
        "memory_layer_write_performed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "hint_candidate_set_teacher_review_id": (
            record.hint_candidate_set_teacher_review_id
        ),
        "set_review_status": record.set_review_status,
        "approved_candidate_ids": record.approved_candidate_ids,
    }


def build_reviewed_concept_readback_hint_teacher_review_safety_audit(
    *,
    hint_candidate_set: ReviewedConceptReadbackHintCandidateSet | dict[str, object],
    hint_candidate_safety_audit: ReviewedConceptReadbackHintCandidateSafetyAudit | dict[str, object],
    set_teacher_review: ReviewedConceptReadbackHintCandidateSetTeacherReview | dict[str, object],
) -> ReviewedConceptReadbackHintTeacherReviewSafetyAudit:
    candidate_set = _candidate_set(hint_candidate_set)
    candidate_safety = _candidate_safety_audit(hint_candidate_safety_audit)
    set_review = _candidate_set_review(set_teacher_review)
    hint_candidate_set_valid = bool(
        validate_reviewed_concept_readback_hint_candidate_set(candidate_set)["valid"]
    ) and candidate_set.set_status == "candidate_set_created" and bool(
        validate_reviewed_concept_readback_hint_candidate_safety_audit(
            candidate_safety
        )["valid"]
    )
    candidate_reviews_valid = bool(
        validate_reviewed_concept_readback_hint_candidate_set_teacher_review(
            set_review
        )["valid"]
    )
    teacher_review_source_valid = all(
        _teacher_review_source_valid(review) for review in set_review.candidate_reviews
    )
    approval_scope_valid = _approval_scope_valid_for_set_review(set_review)
    no_actual_hint = (
        set_review.actual_task_working_memory_hint_created is False
        and all(
            review.actual_task_working_memory_hint_created is False
            and review.approved_for_actual_hint_creation is False
            for review in set_review.candidate_reviews
        )
    )
    no_working_memory_mutation = (
        set_review.applied_to_working_memory is False
        and set_review.working_memory_mutated is False
        and all(
            review.applied_to_working_memory is False
            and review.working_memory_mutated is False
            and review.approved_for_working_memory_application is False
            for review in set_review.candidate_reviews
        )
    )
    no_task_behavior_change = (
        set_review.task_behavior_changed is False
        and all(
            review.task_behavior_changed is False
            and review.approved_for_task_behavior_change is False
            for review in set_review.candidate_reviews
        )
    )
    no_candidate_ordering_change = all(
        review.candidate_ordering_changed is False
        and review.approved_for_candidate_ordering_change is False
        for review in set_review.candidate_reviews
    )
    no_action_selection = all(
        review.action_selection_created is False
        and review.approved_for_action_selection is False
        for review in set_review.candidate_reviews
    )
    no_action_execution = all(
        review.action_execution_created is False
        and review.approved_for_action_execution is False
        for review in set_review.candidate_reviews
    )
    no_memory_layer_write = (
        set_review.memory_layer_write_performed is False
        and all(
            review.memory_layer_write_performed is False
            and review.approved_for_memory_layer_write is False
            for review in set_review.candidate_reviews
        )
    )
    no_automatic_learning_approval = all(
        review.automatic_learning_approval_created is False
        for review in set_review.candidate_reviews
    )
    blocked_reasons = _safety_blocked_reasons(
        hint_candidate_set_valid=hint_candidate_set_valid,
        candidate_reviews_valid=candidate_reviews_valid,
        teacher_review_source_valid=teacher_review_source_valid,
        approval_scope_valid=approval_scope_valid,
        no_actual_task_working_memory_hint_created=no_actual_hint,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_candidate_ordering_change=no_candidate_ordering_change,
        no_action_selection=no_action_selection,
        no_action_execution=no_action_execution,
        no_memory_layer_write=no_memory_layer_write,
        no_automatic_learning_approval=no_automatic_learning_approval,
    )
    return ReviewedConceptReadbackHintTeacherReviewSafetyAudit(
        safety_audit_id=(
            "reviewed_concept_readback_hint_teacher_review_safety_audit:"
            f"{candidate_set.source_reviewed_concept_id}"
        ),
        schema_version=HINT_TEACHER_REVIEW_SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=candidate_set.source_reviewed_concept_id,
        source_hint_candidate_set_id=candidate_set.hint_candidate_set_id,
        source_hint_candidate_set_teacher_review_id=(
            set_review.hint_candidate_set_teacher_review_id
        ),
        hint_candidate_set_valid=hint_candidate_set_valid,
        candidate_reviews_valid=candidate_reviews_valid,
        teacher_review_source_valid=teacher_review_source_valid,
        approval_scope_valid=approval_scope_valid,
        no_actual_task_working_memory_hint_created=no_actual_hint,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_candidate_ordering_change=no_candidate_ordering_change,
        no_action_selection=no_action_selection,
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
            candidate_set.source_trace_refs,
            candidate_safety.source_trace_refs,
            set_review.source_trace_refs,
        ),
    )


def validate_reviewed_concept_readback_hint_teacher_review_safety_audit(
    audit: ReviewedConceptReadbackHintTeacherReviewSafetyAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _safety_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed":
        errors.append(record.audit_status)
    for flag in (
        "hint_candidate_set_valid",
        "candidate_reviews_valid",
        "teacher_review_source_valid",
        "approval_scope_valid",
        "no_actual_task_working_memory_hint_created",
        "no_working_memory_mutation",
        "no_task_behavior_change",
        "no_candidate_ordering_change",
        "no_action_selection",
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


def build_reviewed_concept_readback_hint_teacher_review_bundle(
    candidate_payload: dict[str, object],
    *,
    review_decisions: dict[str, str] | None = None,
    review_actor: str = "system_demo",
    review_actor_role: str = "system_demo",
    review_source: str = "demo_review",
    teacher_review_text: str = "",
) -> dict[str, object]:
    candidate_set = _candidate_set(candidate_payload["hint_candidate_set"])
    candidate_safety = _candidate_safety_audit(
        candidate_payload["hint_candidate_safety_audit"]
    )
    set_review = build_reviewed_concept_readback_hint_candidate_set_teacher_review(
        hint_candidate_set=candidate_set,
        hint_candidate_safety_audit=candidate_safety,
        review_decisions=review_decisions,
        review_actor=review_actor,
        review_actor_role=review_actor_role,
        review_source=review_source,
        teacher_review_text=teacher_review_text,
    )
    safety = build_reviewed_concept_readback_hint_teacher_review_safety_audit(
        hint_candidate_set=candidate_set,
        hint_candidate_safety_audit=candidate_safety,
        set_teacher_review=set_review,
    )
    return {
        "hint_candidate_teacher_reviews": [
            review.to_dict() for review in set_review.candidate_reviews
        ],
        "hint_candidate_set_teacher_review": set_review.to_dict(),
        "hint_teacher_review_safety_audit": safety.to_dict(),
        "hint_candidate_set_teacher_review_validation": (
            validate_reviewed_concept_readback_hint_candidate_set_teacher_review(
                set_review
            )
        ),
        "hint_teacher_review_safety_audit_validation": (
            validate_reviewed_concept_readback_hint_teacher_review_safety_audit(safety)
        ),
        "safe_claim": SAFE_CLAIM,
    }


def build_demo_reviewed_concept_readback_hint_teacher_review() -> dict[str, object]:
    return build_reviewed_concept_readback_hint_teacher_review_bundle(
        build_demo_reviewed_concept_readback_hint_candidate_set()
    )


def build_demo_reviewed_concept_readback_hint_teacher_review_safety_audit() -> (
    ReviewedConceptReadbackHintTeacherReviewSafetyAudit
):
    payload = build_demo_reviewed_concept_readback_hint_teacher_review()
    return ReviewedConceptReadbackHintTeacherReviewSafetyAudit.from_dict(
        payload["hint_teacher_review_safety_audit"]
    )


def build_demo_all_held_readback_hint_teacher_review() -> dict[str, object]:
    candidate_payload = build_demo_reviewed_concept_readback_hint_candidate_set()
    decisions = {
        label: "held_for_more_evidence"
        for label in candidate_payload["hint_candidate_set"]["candidate_labels"]
    }
    return build_reviewed_concept_readback_hint_teacher_review_bundle(
        candidate_payload,
        review_decisions=decisions,
    )


def build_demo_rejected_readback_hint_teacher_review() -> dict[str, object]:
    candidate_payload = build_demo_reviewed_concept_readback_hint_candidate_set()
    decisions = {
        label: "rejected"
        for label in candidate_payload["hint_candidate_set"]["candidate_labels"]
    }
    return build_reviewed_concept_readback_hint_teacher_review_bundle(
        candidate_payload,
        review_decisions=decisions,
    )


def build_demo_conflict_detected_readback_hint_teacher_review() -> dict[str, object]:
    candidate_payload = build_demo_reviewed_concept_readback_hint_candidate_set()
    labels = tuple(candidate_payload["hint_candidate_set"]["candidate_labels"])
    decisions = {label: "held_for_more_evidence" for label in labels}
    if labels:
        decisions[labels[0]] = "conflict_detected"
    return build_reviewed_concept_readback_hint_teacher_review_bundle(
        candidate_payload,
        review_decisions=decisions,
    )


def build_demo_blocked_invalid_review_source() -> dict[str, object]:
    return build_reviewed_concept_readback_hint_teacher_review_bundle(
        build_demo_reviewed_concept_readback_hint_candidate_set(),
        review_actor="teacher_demo",
        review_actor_role="teacher",
        review_source="demo_review",
    )


def build_demo_blocked_forbidden_authority_review() -> dict[str, object]:
    payload = build_demo_reviewed_concept_readback_hint_teacher_review()
    set_review = ReviewedConceptReadbackHintCandidateSetTeacherReview.from_dict(
        payload["hint_candidate_set_teacher_review"]
    )
    reviews = list(set_review.candidate_reviews)
    first = dict(reviews[0].to_dict())
    first["actual_task_working_memory_hint_created"] = True
    reviews[0] = ReviewedConceptReadbackHintCandidateTeacherReview.from_dict(first)
    set_review = ReviewedConceptReadbackHintCandidateSetTeacherReview.from_dict(
        {
            **set_review.to_dict(),
            "candidate_reviews": [review.to_dict() for review in reviews],
        }
    )
    candidate_payload = build_demo_reviewed_concept_readback_hint_candidate_set()
    safety = build_reviewed_concept_readback_hint_teacher_review_safety_audit(
        hint_candidate_set=candidate_payload["hint_candidate_set"],
        hint_candidate_safety_audit=candidate_payload["hint_candidate_safety_audit"],
        set_teacher_review=set_review,
    )
    return {
        **payload,
        "hint_candidate_teacher_reviews": [review.to_dict() for review in reviews],
        "hint_candidate_set_teacher_review": set_review.to_dict(),
        "hint_candidate_set_teacher_review_validation": (
            validate_reviewed_concept_readback_hint_candidate_set_teacher_review(
                set_review
            )
        ),
        "hint_teacher_review_safety_audit": safety.to_dict(),
        "hint_teacher_review_safety_audit_validation": (
            validate_reviewed_concept_readback_hint_teacher_review_safety_audit(safety)
        ),
    }


def build_demo_blocked_hint_teacher_review(case: str) -> dict[str, object]:
    cases = {
        "invalid-review-source": build_demo_blocked_invalid_review_source,
        "forbidden-authority": build_demo_blocked_forbidden_authority_review,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked teacher review case: {case}") from error


def _review_status(
    candidate: ReviewedConceptReadbackHintCandidate,
    requested_status: str,
) -> str:
    if (
        candidate.candidate_status != "candidate_ready_for_teacher_review"
        or not validate_reviewed_concept_readback_hint_candidate(candidate)["valid"]
    ):
        return "blocked_invalid_candidate"
    if requested_status not in ALLOWED_TEACHER_REVIEW_STATUSES:
        return "blocked_invalid_candidate"
    return requested_status


def _review_reason(status: str) -> str:
    reasons = {
        "approved_for_future_hint_preparation": "candidate is low-authority and ready for future preparation",
        "held_for_more_evidence": "candidate should wait for more evidence or scope review",
        "rejected": "candidate should not proceed",
        "needs_more_evidence": "candidate needs more support before preparation",
        "conflict_detected": "candidate has a conflict that blocks future preparation",
    }
    return reasons.get(status, status)


def _decision_reason(status: str) -> str:
    return _review_reason(status)


def _review_text(status: str, review_source: str) -> str:
    if review_source == "demo_review":
        return f"Demo-only review mark: {status}."
    return ""


def _demo_review_decisions(
    candidate_set: ReviewedConceptReadbackHintCandidateSet,
) -> dict[str, str]:
    decisions = {
        "observe_before_direct_retry": "approved_for_future_hint_preparation",
        "avoid_same_failed_direct_retry": "approved_for_future_hint_preparation",
        "verify_obstacle_type_before_generalizing": "held_for_more_evidence",
    }
    return {
        label: decisions.get(label, "held_for_more_evidence")
        for label in candidate_set.candidate_labels
    }


def _set_review_status(
    *,
    candidate_set_valid: bool,
    candidate_reviews: tuple[ReviewedConceptReadbackHintCandidateTeacherReview, ...],
    candidate_reviews_valid: bool,
) -> str:
    if not candidate_set_valid:
        return "blocked_invalid_candidate_set"
    if not candidate_reviews_valid:
        return "blocked_invalid_candidate_reviews"
    if any(review.teacher_review_status == "conflict_detected" for review in candidate_reviews):
        return "conflict_detected"
    if any(
        review.teacher_review_status == "approved_for_future_hint_preparation"
        for review in candidate_reviews
    ):
        return "reviewed_with_approved_candidates"
    if all(
        review.teacher_review_status
        in {"held_for_more_evidence", "rejected", "needs_more_evidence"}
        for review in candidate_reviews
    ):
        return "reviewed_all_held_or_rejected"
    return "blocked_invalid_candidate_reviews"


def _set_review_summary(status: str) -> str:
    if status == "reviewed_with_approved_candidates":
        return "Teacher review marked at least one hint candidate for future preparation."
    if status == "reviewed_all_held_or_rejected":
        return "Teacher review produced no future-preparation candidates."
    if status == "conflict_detected":
        return "Teacher review found a conflict; no automatic preparation authority is created."
    return f"Teacher review blocked: {status}."


def _approval_scope_valid_for_review(
    review: ReviewedConceptReadbackHintCandidateTeacherReview,
) -> bool:
    if review.teacher_review_status == "approved_for_future_hint_preparation":
        if review.approved_for_future_hint_preparation is not True:
            return False
    elif review.approved_for_future_hint_preparation is not False:
        return False
    return all(
        getattr(review, flag) is False
        for flag in (
            "approved_for_actual_hint_creation",
            "approved_for_working_memory_application",
            "approved_for_task_behavior_change",
            "approved_for_candidate_ordering_change",
            "approved_for_action_selection",
            "approved_for_action_execution",
            "approved_for_memory_layer_write",
        )
    )


def _approval_scope_valid_for_set_review(
    review: ReviewedConceptReadbackHintCandidateSetTeacherReview,
) -> bool:
    if any(
        getattr(review, flag) is not False
        for flag in (
            "approved_for_actual_hint_creation",
            "approved_for_working_memory_application",
            "approved_for_task_behavior_change",
        )
    ):
        return False
    return all(
        _approval_scope_valid_for_review(candidate_review)
        for candidate_review in review.candidate_reviews
    )


def _teacher_review_source_valid(
    review: ReviewedConceptReadbackHintCandidateTeacherReview,
) -> bool:
    if review.review_source == "demo_review":
        return review.review_actor_role == "system_demo"
    if review.review_source == "explicit_teacher_review":
        return (
            review.review_actor_role in {"teacher", "project_owner"}
            and bool(review.teacher_review_text.strip())
        )
    return False


def _safety_blocked_reasons(
    *,
    hint_candidate_set_valid: bool,
    candidate_reviews_valid: bool,
    teacher_review_source_valid: bool,
    approval_scope_valid: bool,
    no_actual_task_working_memory_hint_created: bool,
    no_working_memory_mutation: bool,
    no_task_behavior_change: bool,
    no_candidate_ordering_change: bool,
    no_action_selection: bool,
    no_action_execution: bool,
    no_memory_layer_write: bool,
    no_automatic_learning_approval: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not no_actual_task_working_memory_hint_created:
        reasons.append("blocked_forbidden_hint_creation_detected")
    if not no_working_memory_mutation:
        reasons.append("blocked_forbidden_working_memory_mutation_detected")
    if not (no_task_behavior_change and no_candidate_ordering_change):
        reasons.append("blocked_forbidden_behavior_change_detected")
    if not (no_action_selection and no_action_execution):
        reasons.append("blocked_forbidden_action_authority_detected")
    if not (no_memory_layer_write and no_automatic_learning_approval):
        reasons.append("blocked_forbidden_memory_write_detected")
    if not hint_candidate_set_valid:
        reasons.append("blocked_invalid_hint_candidate_set")
    if not candidate_reviews_valid:
        reasons.append("blocked_invalid_candidate_reviews")
    if not teacher_review_source_valid:
        reasons.append("blocked_invalid_teacher_review_source")
    if not approval_scope_valid:
        reasons.append("blocked_invalid_approval_scope")
    return tuple(dict.fromkeys(reasons))


def _audit_status(blocked_reasons: tuple[str, ...]) -> str:
    if not blocked_reasons:
        return "passed"
    for status in (
        "blocked_forbidden_hint_creation_detected",
        "blocked_forbidden_working_memory_mutation_detected",
        "blocked_forbidden_behavior_change_detected",
        "blocked_forbidden_action_authority_detected",
        "blocked_forbidden_memory_write_detected",
        "blocked_invalid_hint_candidate_set",
        "blocked_invalid_teacher_review_source",
        "blocked_invalid_approval_scope",
        "blocked_invalid_candidate_reviews",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_invalid_candidate_reviews"


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _candidate(
    record: ReviewedConceptReadbackHintCandidate | dict[str, object],
) -> ReviewedConceptReadbackHintCandidate:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintCandidate)
        else ReviewedConceptReadbackHintCandidate.from_dict(dict(record))
    )


def _candidate_set(
    record: ReviewedConceptReadbackHintCandidateSet | dict[str, object],
) -> ReviewedConceptReadbackHintCandidateSet:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintCandidateSet)
        else ReviewedConceptReadbackHintCandidateSet.from_dict(dict(record))
    )


def _candidate_safety_audit(
    record: ReviewedConceptReadbackHintCandidateSafetyAudit | dict[str, object],
) -> ReviewedConceptReadbackHintCandidateSafetyAudit:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintCandidateSafetyAudit)
        else ReviewedConceptReadbackHintCandidateSafetyAudit.from_dict(dict(record))
    )


def _candidate_review(
    record: ReviewedConceptReadbackHintCandidateTeacherReview | dict[str, object],
) -> ReviewedConceptReadbackHintCandidateTeacherReview:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintCandidateTeacherReview)
        else ReviewedConceptReadbackHintCandidateTeacherReview.from_dict(dict(record))
    )


def _candidate_set_review(
    record: ReviewedConceptReadbackHintCandidateSetTeacherReview | dict[str, object],
) -> ReviewedConceptReadbackHintCandidateSetTeacherReview:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintCandidateSetTeacherReview)
        else ReviewedConceptReadbackHintCandidateSetTeacherReview.from_dict(dict(record))
    )


def _safety_audit(
    record: ReviewedConceptReadbackHintTeacherReviewSafetyAudit | dict[str, object],
) -> ReviewedConceptReadbackHintTeacherReviewSafetyAudit:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintTeacherReviewSafetyAudit)
        else ReviewedConceptReadbackHintTeacherReviewSafetyAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
