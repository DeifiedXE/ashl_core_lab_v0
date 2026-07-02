"""Review and refine feedback-derived ConceptCandidate draft records."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.learning_feedback_to_concept_candidate import (
    LearningFeedbackToConceptCandidateDraftRecord,
    LearningFeedbackToConceptCandidateSafetyAudit,
    build_demo_failed_expected_effect_to_concept_candidate,
    build_demo_goal_reached_to_concept_candidate,
    build_demo_no_progress_to_concept_candidate,
    build_demo_observation_only_to_concept_candidate,
    build_demo_successful_expected_effect_to_concept_candidate,
    build_demo_system_fault_blocked_feedback_review,
    build_demo_unknown_outcome_held_feedback_review,
    validate_learning_feedback_to_concept_candidate_draft_record,
    validate_learning_feedback_to_concept_candidate_safety_audit,
)


SOURCE_ENGINE = "learning_engine"

REVIEW_SCHEMA_VERSION = "learning_engine_feedback_concept_candidate_review_v0"
SCOPE_CHECK_SCHEMA_VERSION = (
    "learning_engine_feedback_concept_candidate_scope_check_v0"
)
COUNTEREXAMPLE_CHECK_SCHEMA_VERSION = (
    "learning_engine_feedback_concept_candidate_counterexample_check_v0"
)
REFINEMENT_SCHEMA_VERSION = (
    "learning_engine_feedback_concept_candidate_refinement_v0"
)
REVIEW_SET_SCHEMA_VERSION = "learning_engine_feedback_concept_candidate_review_set_v0"
SAFETY_AUDIT_SCHEMA_VERSION = (
    "learning_engine_feedback_concept_candidate_refinement_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Learning Engine can review and refine feedback-derived "
    "ConceptCandidate drafts from LearningFeedbackCandidates, including scope "
    "narrowing and counterexample checks, while avoiding ReviewedConcept "
    "creation, memory writes, behavior changes, action authority changes, or "
    "automatic learning approval."
)
BLOCKED_CLAIMS = (
    "no_reviewed_concept_creation",
    "no_memory_write",
    "no_behavior_change",
    "no_action_authority_change",
    "no_automatic_learning_approval",
)

PASSING_PACKAGE90_AUDIT_STATUSES = {
    "passed_concept_candidate_draft_only",
    "passed_no_concept_candidate_created",
}

ALLOWED_REVIEW_STATUSES = {
    "approved_for_refinement",
    "held_for_more_evidence",
    "rejected",
    "needs_scope_narrowing",
    "needs_counterexample_check",
    "needs_split",
    "conflict_detected",
    "blocked_invalid_feedback_concept_candidate_draft",
    "blocked_forbidden_authority_detected",
}
ALLOWED_REVIEW_SOURCES = {"explicit_teacher_review", "demo_review"}
ALLOWED_REVIEW_ACTOR_ROLES = {"teacher", "project_owner", "system_demo"}
ALLOWED_SCOPE_CHECK_STATUSES = {
    "scope_valid_for_refinement",
    "scope_narrowing_required",
    "scope_too_broad",
    "scope_needs_more_evidence",
    "scope_context_bound_to_sandbox",
    "blocked_invalid_review",
    "blocked_forbidden_authority_detected",
}
ALLOWED_COUNTEREXAMPLE_STATUSES = {
    "counterexample_check_passed",
    "counterexample_check_passed_no_counterexamples",
    "counterexample_check_requires_scope_narrowing",
    "counterexample_check_requires_split",
    "counterexample_check_blocked_unhandled_counterexamples",
    "blocked_invalid_scope_check",
    "blocked_forbidden_authority_detected",
}
ALLOWED_REFINEMENT_STATUSES = {
    "refined_concept_candidate_created",
    "held_for_more_evidence",
    "split_recommended",
    "conflict_detected",
    "rejected_by_review",
    "blocked_unhandled_counterexamples",
    "blocked_invalid_scope",
    "blocked_invalid_review",
    "blocked_forbidden_authority_detected",
    "rollback_applied",
}
ALLOWED_CONFIDENCE = {"low", "normal", "high", "blocked"}
ALLOWED_REVIEW_SET_STATUSES = {
    "review_set_created_with_refined_candidates",
    "review_set_created_all_held_or_blocked",
    "review_set_created_with_split_recommendations",
    "blocked_invalid_review_records",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_feedback_concept_candidate_refinement_only",
    "passed_all_held_or_blocked",
    "blocked_invalid_feedback_concept_candidate_draft",
    "blocked_invalid_review",
    "blocked_invalid_scope_check",
    "blocked_invalid_counterexample_check",
    "blocked_invalid_refinement",
    "blocked_reviewed_concept_creation_detected",
    "blocked_memory_write_detected",
    "blocked_automatic_learning_approval_detected",
    "blocked_action_authority_detected",
    "blocked_behavior_change_detected",
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
class FeedbackConceptCandidateReviewRecord:
    feedback_concept_candidate_review_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_draft_id: str
    source_learning_feedback_candidate_id: str
    source_evidence_packet_id: str | None
    source_feedback_teacher_review_id: str | None
    source_feedback_to_concept_candidate_safety_audit_id: str | None
    concept_candidate_kind: str
    proposed_concept_label: str
    proposed_concept_scope: str
    concept_candidate_summary: str
    concept_candidate_reason: str
    direct_command: str | None
    expected_effect: str | None
    outcome_class: str
    goal_delta_class: str
    closure_status: str
    teacher_review_status: str
    teacher_review_reason: str
    teacher_review_text: str
    review_actor: str
    review_actor_role: str
    review_source: str
    approved_for_refinement: bool
    approved_for_reviewed_concept: bool
    approved_for_memory_write: bool
    approved_for_behavior_change: bool
    approved_for_action_authority: bool
    approved_for_automatic_learning_approval: bool
    requires_scope_check: bool
    requires_counterexample_check: bool
    requires_refinement: bool
    requires_reviewed_concept_gate_later: bool
    requires_memory_write_gate_later: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    task_behavior_changed: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_created: bool
    execution_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REVIEW_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_feedback_concept_candidate_review_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.teacher_review_status not in ALLOWED_REVIEW_STATUSES:
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
    def from_dict(cls, data: dict[str, object]) -> "FeedbackConceptCandidateReviewRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackConceptCandidateScopeCheckRecord:
    scope_check_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_draft_id: str
    source_feedback_concept_candidate_review_id: str
    original_proposed_concept_label: str
    original_proposed_concept_scope: str
    scope_check_status: str
    scope_check_summary: str
    scope_is_too_broad: bool
    scope_is_too_narrow: bool
    scope_is_context_bound: bool
    scope_requires_sandbox_context: bool
    scope_requires_more_evidence: bool
    refined_scope_suggestion: str
    scope_warning_labels: tuple[str, ...]
    reviewed_concept_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SCOPE_CHECK_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_feedback_concept_candidate_scope_check_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.scope_check_status not in ALLOWED_SCOPE_CHECK_STATUSES:
            raise ValueError(f"unknown scope_check_status: {self.scope_check_status}")
        object.__setattr__(
            self,
            "scope_warning_labels",
            _tuple_of_str("scope_warning_labels", self.scope_warning_labels),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FeedbackConceptCandidateScopeCheckRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackConceptCandidateCounterexampleCheckRecord:
    counterexample_check_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_draft_id: str
    source_feedback_concept_candidate_review_id: str
    source_scope_check_id: str
    proposed_concept_label: str
    proposed_concept_scope: str
    support_evidence_refs: tuple[str, ...]
    counterexample_refs: tuple[str, ...]
    counterexample_notes: tuple[str, ...]
    counterexample_check_status: str
    counterexample_check_summary: str
    has_support_evidence: bool
    has_counterexamples: bool
    counterexamples_handled: bool
    counterexamples_require_scope_narrowing: bool
    counterexamples_require_split: bool
    counterexamples_block_refinement: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != COUNTEREXAMPLE_CHECK_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_feedback_concept_candidate_counterexample_check_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.counterexample_check_status not in ALLOWED_COUNTEREXAMPLE_STATUSES:
            raise ValueError(
                f"unknown counterexample_check_status: {self.counterexample_check_status}"
            )
        for name in (
            "support_evidence_refs",
            "counterexample_refs",
            "counterexample_notes",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "FeedbackConceptCandidateCounterexampleCheckRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackConceptCandidateRefinementRecord:
    feedback_concept_candidate_refinement_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_draft_id: str
    source_feedback_concept_candidate_review_id: str
    source_scope_check_id: str
    source_counterexample_check_id: str
    original_concept_label: str
    original_concept_scope: str
    original_concept_candidate_kind: str
    refined_concept_label: str
    refined_concept_scope: str
    refined_concept_candidate_kind: str
    refined_concept_confidence: str
    refinement_status: str
    refinement_summary: str
    refinement_reason: str
    support_evidence_refs: tuple[str, ...]
    counterexample_refs: tuple[str, ...]
    counterexample_handling_notes: tuple[str, ...]
    split_recommended: bool
    split_candidate_labels: tuple[str, ...]
    split_reason: str | None
    available_for_reviewed_concept_preparation_later: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    task_behavior_changed: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_created: bool
    execution_created: bool
    rollback_available: bool
    rollback_record_id: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REFINEMENT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_feedback_concept_candidate_refinement_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.refinement_status not in ALLOWED_REFINEMENT_STATUSES:
            raise ValueError(f"unknown refinement_status: {self.refinement_status}")
        if self.refined_concept_confidence not in ALLOWED_CONFIDENCE:
            raise ValueError(f"unknown refined_concept_confidence: {self.refined_concept_confidence}")
        for name in (
            "support_evidence_refs",
            "counterexample_refs",
            "counterexample_handling_notes",
            "split_candidate_labels",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FeedbackConceptCandidateRefinementRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackConceptCandidateReviewSet:
    feedback_concept_candidate_review_set_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_draft_ids: tuple[str, ...]
    review_records: tuple[FeedbackConceptCandidateReviewRecord, ...]
    scope_check_records: tuple[FeedbackConceptCandidateScopeCheckRecord, ...]
    counterexample_check_records: tuple[FeedbackConceptCandidateCounterexampleCheckRecord, ...]
    refinement_records: tuple[FeedbackConceptCandidateRefinementRecord, ...]
    refined_candidate_ids: tuple[str, ...]
    held_candidate_ids: tuple[str, ...]
    split_recommended_candidate_ids: tuple[str, ...]
    rejected_candidate_ids: tuple[str, ...]
    blocked_candidate_ids: tuple[str, ...]
    review_count: int
    refined_count: int
    held_count: int
    split_recommended_count: int
    blocked_count: int
    review_set_status: str
    review_set_summary: str
    has_refined_candidates_for_reviewed_concept_preparation_later: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    task_behavior_changed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REVIEW_SET_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_feedback_concept_candidate_review_set_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.review_set_status not in ALLOWED_REVIEW_SET_STATUSES:
            raise ValueError(f"unknown review_set_status: {self.review_set_status}")
        object.__setattr__(
            self,
            "review_records",
            tuple(_review_record(review) for review in self.review_records),
        )
        object.__setattr__(
            self,
            "scope_check_records",
            tuple(_scope_record(scope) for scope in self.scope_check_records),
        )
        object.__setattr__(
            self,
            "counterexample_check_records",
            tuple(
                _counterexample_record(check)
                for check in self.counterexample_check_records
            ),
        )
        object.__setattr__(
            self,
            "refinement_records",
            tuple(_refinement_record(item) for item in self.refinement_records),
        )
        for name in (
            "source_concept_candidate_draft_ids",
            "refined_candidate_ids",
            "held_candidate_ids",
            "split_recommended_candidate_ids",
            "rejected_candidate_ids",
            "blocked_candidate_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FeedbackConceptCandidateReviewSet":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackConceptCandidateRefinementSafetyAudit:
    feedback_concept_candidate_refinement_safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_review_set_id: str | None
    source_refinement_ids: tuple[str, ...]
    feedback_concept_candidate_drafts_valid: bool
    review_records_valid: bool
    scope_checks_valid: bool
    counterexample_checks_valid: bool
    refinement_records_valid: bool
    rollback_available: bool
    refinement_only_confirmed: bool
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
                "schema_version must be learning_engine_feedback_concept_candidate_refinement_safety_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in (
            "source_refinement_ids",
            "blocked_claims",
            "blocked_reasons",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "FeedbackConceptCandidateRefinementSafetyAudit":
        return cls(**dict(data))


def build_feedback_concept_candidate_review_record(
    *,
    draft: LearningFeedbackToConceptCandidateDraftRecord | dict[str, object],
    feedback_to_concept_candidate_safety_audit: LearningFeedbackToConceptCandidateSafetyAudit
    | dict[str, object]
    | None = None,
    teacher_review_status: str = "approved_for_refinement",
    teacher_review_reason: str | None = None,
    teacher_review_text: str = "Demo review approves refinement only.",
    review_actor: str = "system_demo",
    review_actor_role: str = "system_demo",
    review_source: str = "demo_review",
    created_at: str | None = None,
) -> FeedbackConceptCandidateReviewRecord:
    draft_record = _draft_record(draft)
    package90_audit = _package90_audit_record(feedback_to_concept_candidate_safety_audit)
    status = teacher_review_status
    if _draft_forbidden_authority(draft_record):
        status = "blocked_forbidden_authority_detected"
    elif (
        status == "approved_for_refinement"
        and not _draft_valid_for_refinement(draft_record)
    ):
        status = "blocked_invalid_feedback_concept_candidate_draft"
    elif (
        status == "approved_for_refinement"
        and package90_audit is not None
        and not _package90_audit_passed(package90_audit)
    ):
        status = "blocked_invalid_feedback_concept_candidate_draft"
    approved = status == "approved_for_refinement"
    return FeedbackConceptCandidateReviewRecord(
        feedback_concept_candidate_review_id=(
            f"feedback_concept_candidate_review:{draft_record.concept_candidate_draft_id}"
        ),
        schema_version=REVIEW_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_draft_id=draft_record.concept_candidate_draft_id,
        source_learning_feedback_candidate_id=draft_record.source_learning_feedback_candidate_id,
        source_evidence_packet_id=draft_record.source_learning_feedback_evidence_packet_id,
        source_feedback_teacher_review_id=draft_record.source_learning_feedback_teacher_review_id,
        source_feedback_to_concept_candidate_safety_audit_id=(
            package90_audit.concept_candidate_safety_audit_id if package90_audit else None
        ),
        concept_candidate_kind=draft_record.concept_candidate_kind,
        proposed_concept_label=draft_record.proposed_concept_label,
        proposed_concept_scope=draft_record.proposed_concept_scope,
        concept_candidate_summary=draft_record.concept_candidate_summary,
        concept_candidate_reason=draft_record.concept_candidate_reason,
        direct_command=draft_record.direct_command,
        expected_effect=draft_record.expected_effect,
        outcome_class=draft_record.outcome_class,
        goal_delta_class=draft_record.goal_delta_class,
        closure_status=draft_record.closure_status,
        teacher_review_status=status,
        teacher_review_reason=teacher_review_reason or _review_reason(status, draft_record),
        teacher_review_text=teacher_review_text,
        review_actor=review_actor,
        review_actor_role=review_actor_role,
        review_source=review_source,
        approved_for_refinement=approved,
        approved_for_reviewed_concept=False,
        approved_for_memory_write=False,
        approved_for_behavior_change=False,
        approved_for_action_authority=False,
        approved_for_automatic_learning_approval=False,
        requires_scope_check=True,
        requires_counterexample_check=True,
        requires_refinement=True,
        requires_reviewed_concept_gate_later=True,
        requires_memory_write_gate_later=True,
        reviewed_concept_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        task_behavior_changed=False,
        candidate_ordering_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_created=False,
        execution_created=False,
        source_trace_refs=_combined_trace_refs(
            draft_record.source_trace_refs,
            package90_audit.source_trace_refs if package90_audit else (),
        ),
    )


def validate_feedback_concept_candidate_review_record(
    review: FeedbackConceptCandidateReviewRecord | dict[str, object],
) -> dict[str, object]:
    record = _review_record(review)
    errors: list[str] = []
    if not record.feedback_concept_candidate_review_id:
        errors.append("missing_feedback_concept_candidate_review_id")
    if record.review_source == "explicit_teacher_review":
        if record.review_actor_role not in {"teacher", "project_owner"}:
            errors.append("explicit_review_requires_teacher_or_project_owner")
        if not record.teacher_review_text.strip():
            errors.append("explicit_review_requires_teacher_review_text")
    elif record.review_source == "demo_review":
        if record.review_actor_role != "system_demo":
            errors.append("demo_review_requires_system_demo_role")
    else:
        errors.append("invalid_review_source")
    if record.approved_for_refinement != (
        record.teacher_review_status == "approved_for_refinement"
    ):
        errors.append("approval_flag_does_not_match_review_status")
    if _review_forbidden_authority(record):
        errors.append("forbidden_authority_detected")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "feedback_concept_candidate_review_id": record.feedback_concept_candidate_review_id,
        "teacher_review_status": record.teacher_review_status,
    }


def build_feedback_concept_candidate_scope_check_record(
    *,
    draft: LearningFeedbackToConceptCandidateDraftRecord | dict[str, object],
    review: FeedbackConceptCandidateReviewRecord | dict[str, object] | None,
    force_scope_too_broad: bool = False,
    created_at: str | None = None,
) -> FeedbackConceptCandidateScopeCheckRecord:
    draft_record = _draft_record(draft)
    review_record = _review_record(review) if review is not None else None
    invalid_review = review_record is None or not validate_feedback_concept_candidate_review_record(
        review_record
    )["valid"]
    too_broad = force_scope_too_broad or _scope_text_too_broad(
        draft_record.proposed_concept_scope
    )
    warnings = ["single_closure_sandbox_bound"]
    if too_broad:
        warnings.append("scope_too_broad")
    if invalid_review:
        status = "blocked_invalid_review"
    elif _review_forbidden_authority(review_record):
        status = "blocked_forbidden_authority_detected"
    elif too_broad:
        status = "scope_too_broad"
    elif review_record.teacher_review_status == "needs_scope_narrowing":
        status = "scope_narrowing_required"
    else:
        status = "scope_valid_for_refinement"
    return FeedbackConceptCandidateScopeCheckRecord(
        scope_check_id=f"feedback_concept_candidate_scope_check:{draft_record.concept_candidate_draft_id}",
        schema_version=SCOPE_CHECK_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_draft_id=draft_record.concept_candidate_draft_id,
        source_feedback_concept_candidate_review_id=(
            review_record.feedback_concept_candidate_review_id if review_record else ""
        ),
        original_proposed_concept_label=draft_record.proposed_concept_label,
        original_proposed_concept_scope=draft_record.proposed_concept_scope,
        scope_check_status=status,
        scope_check_summary=_scope_summary(status, draft_record),
        scope_is_too_broad=too_broad,
        scope_is_too_narrow=False,
        scope_is_context_bound=True,
        scope_requires_sandbox_context=True,
        scope_requires_more_evidence=status in {"scope_needs_more_evidence", "scope_too_broad"},
        refined_scope_suggestion=_refined_scope_suggestion(draft_record, too_broad),
        scope_warning_labels=tuple(warnings),
        reviewed_concept_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_combined_trace_refs(
            draft_record.source_trace_refs,
            review_record.source_trace_refs if review_record else (),
        ),
    )


def validate_feedback_concept_candidate_scope_check_record(
    scope_check: FeedbackConceptCandidateScopeCheckRecord | dict[str, object],
) -> dict[str, object]:
    record = _scope_record(scope_check)
    errors: list[str] = []
    if not record.scope_check_id:
        errors.append("missing_scope_check_id")
    if record.scope_check_status not in ALLOWED_SCOPE_CHECK_STATUSES:
        errors.append("invalid_scope_check_status")
    if not record.scope_requires_sandbox_context:
        errors.append("single_closure_scope_must_remain_sandbox_bound")
    if record.scope_is_too_broad and "scope_too_broad" not in record.scope_warning_labels:
        errors.append("scope_too_broad_missing_warning")
    if (
        record.reviewed_concept_created
        or record.memory_write_performed
        or record.automatic_learning_approval_created
    ):
        errors.append("forbidden_authority_detected")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "scope_check_id": record.scope_check_id,
        "scope_check_status": record.scope_check_status,
    }


def build_feedback_concept_candidate_counterexample_check_record(
    *,
    draft: LearningFeedbackToConceptCandidateDraftRecord | dict[str, object],
    review: FeedbackConceptCandidateReviewRecord | dict[str, object] | None,
    scope_check: FeedbackConceptCandidateScopeCheckRecord | dict[str, object],
    counterexample_refs: tuple[str, ...] = (),
    counterexample_notes: tuple[str, ...] = (),
    requires_split: bool = False,
    created_at: str | None = None,
) -> FeedbackConceptCandidateCounterexampleCheckRecord:
    draft_record = _draft_record(draft)
    review_record = _review_record(review) if review is not None else None
    scope_record = _scope_record(scope_check)
    support_refs = tuple(draft_record.proposed_support_evidence_refs)
    has_counterexamples = bool(counterexample_refs)
    if not validate_feedback_concept_candidate_scope_check_record(scope_record)["valid"]:
        status = "blocked_invalid_scope_check"
    elif scope_record.scope_check_status in {"blocked_invalid_review", "blocked_forbidden_authority_detected"}:
        status = "blocked_invalid_scope_check"
    elif not support_refs:
        status = "counterexample_check_blocked_unhandled_counterexamples"
    elif has_counterexamples and not counterexample_notes:
        status = "counterexample_check_blocked_unhandled_counterexamples"
    elif requires_split or (review_record and review_record.teacher_review_status == "needs_split"):
        status = "counterexample_check_requires_split"
    elif has_counterexamples:
        status = "counterexample_check_requires_scope_narrowing"
    else:
        status = "counterexample_check_passed_no_counterexamples"
    return FeedbackConceptCandidateCounterexampleCheckRecord(
        counterexample_check_id=(
            f"feedback_concept_candidate_counterexample_check:{draft_record.concept_candidate_draft_id}"
        ),
        schema_version=COUNTEREXAMPLE_CHECK_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_draft_id=draft_record.concept_candidate_draft_id,
        source_feedback_concept_candidate_review_id=(
            review_record.feedback_concept_candidate_review_id if review_record else ""
        ),
        source_scope_check_id=scope_record.scope_check_id,
        proposed_concept_label=draft_record.proposed_concept_label,
        proposed_concept_scope=scope_record.refined_scope_suggestion,
        support_evidence_refs=support_refs,
        counterexample_refs=counterexample_refs,
        counterexample_notes=counterexample_notes,
        counterexample_check_status=status,
        counterexample_check_summary=_counterexample_summary(status),
        has_support_evidence=bool(support_refs),
        has_counterexamples=has_counterexamples,
        counterexamples_handled=not status.endswith("unhandled_counterexamples"),
        counterexamples_require_scope_narrowing=status
        == "counterexample_check_requires_scope_narrowing",
        counterexamples_require_split=status == "counterexample_check_requires_split",
        counterexamples_block_refinement=status
        == "counterexample_check_blocked_unhandled_counterexamples",
        reviewed_concept_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_combined_trace_refs(
            draft_record.source_trace_refs,
            scope_record.source_trace_refs,
        ),
    )


def validate_feedback_concept_candidate_counterexample_check_record(
    counterexample_check: FeedbackConceptCandidateCounterexampleCheckRecord | dict[str, object],
) -> dict[str, object]:
    record = _counterexample_record(counterexample_check)
    errors: list[str] = []
    if not record.counterexample_check_id:
        errors.append("missing_counterexample_check_id")
    if not record.has_support_evidence:
        errors.append("missing_support_evidence")
    if record.has_counterexamples and not record.counterexample_notes:
        errors.append("counterexamples_missing_notes")
    if record.counterexamples_block_refinement and record.counterexamples_handled:
        errors.append("blocked_counterexamples_marked_handled")
    if (
        record.reviewed_concept_created
        or record.memory_write_performed
        or record.automatic_learning_approval_created
    ):
        errors.append("forbidden_authority_detected")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "counterexample_check_id": record.counterexample_check_id,
        "counterexample_check_status": record.counterexample_check_status,
    }


def build_feedback_concept_candidate_refinement_record(
    *,
    draft: LearningFeedbackToConceptCandidateDraftRecord | dict[str, object],
    review: FeedbackConceptCandidateReviewRecord | dict[str, object] | None,
    scope_check: FeedbackConceptCandidateScopeCheckRecord | dict[str, object],
    counterexample_check: FeedbackConceptCandidateCounterexampleCheckRecord | dict[str, object],
    created_at: str | None = None,
) -> FeedbackConceptCandidateRefinementRecord:
    draft_record = _draft_record(draft)
    review_record = _review_record(review) if review is not None else None
    scope_record = _scope_record(scope_check)
    counterexample_record = _counterexample_record(counterexample_check)
    status = _refinement_status(draft_record, review_record, scope_record, counterexample_record)
    refined = status == "refined_concept_candidate_created"
    split = status == "split_recommended"
    label, confidence = _refined_label_and_confidence(draft_record, status)
    return FeedbackConceptCandidateRefinementRecord(
        feedback_concept_candidate_refinement_id=(
            f"feedback_concept_candidate_refinement:{draft_record.concept_candidate_draft_id}"
        ),
        schema_version=REFINEMENT_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_draft_id=draft_record.concept_candidate_draft_id,
        source_feedback_concept_candidate_review_id=(
            review_record.feedback_concept_candidate_review_id if review_record else ""
        ),
        source_scope_check_id=scope_record.scope_check_id,
        source_counterexample_check_id=counterexample_record.counterexample_check_id,
        original_concept_label=draft_record.proposed_concept_label,
        original_concept_scope=draft_record.proposed_concept_scope,
        original_concept_candidate_kind=draft_record.concept_candidate_kind,
        refined_concept_label=label,
        refined_concept_scope=scope_record.refined_scope_suggestion,
        refined_concept_candidate_kind=draft_record.concept_candidate_kind,
        refined_concept_confidence=confidence,
        refinement_status=status,
        refinement_summary=_refinement_summary(status, label),
        refinement_reason=_refinement_reason(status),
        support_evidence_refs=counterexample_record.support_evidence_refs,
        counterexample_refs=counterexample_record.counterexample_refs,
        counterexample_handling_notes=counterexample_record.counterexample_notes,
        split_recommended=split,
        split_candidate_labels=_split_labels(draft_record) if split else (),
        split_reason="counterexamples require narrower candidate split" if split else None,
        available_for_reviewed_concept_preparation_later=refined,
        reviewed_concept_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        task_behavior_changed=False,
        candidate_ordering_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_created=False,
        execution_created=False,
        rollback_available=refined,
        rollback_record_id=None,
        source_trace_refs=_combined_trace_refs(
            draft_record.source_trace_refs,
            review_record.source_trace_refs if review_record else (),
            scope_record.source_trace_refs,
            counterexample_record.source_trace_refs,
        ),
    )


def validate_feedback_concept_candidate_refinement_record(
    refinement: FeedbackConceptCandidateRefinementRecord | dict[str, object],
) -> dict[str, object]:
    record = _refinement_record(refinement)
    errors: list[str] = []
    if not record.feedback_concept_candidate_refinement_id:
        errors.append("missing_feedback_concept_candidate_refinement_id")
    if record.refinement_status not in ALLOWED_REFINEMENT_STATUSES:
        errors.append("invalid_refinement_status")
    if record.refinement_status == "refined_concept_candidate_created":
        if not record.available_for_reviewed_concept_preparation_later:
            errors.append("refined_candidate_not_available_for_later_preparation")
        if not record.rollback_available:
            errors.append("refined_candidate_missing_rollback_availability")
    if record.split_recommended and not record.split_candidate_labels:
        errors.append("split_recommended_missing_candidate_labels")
    if _refinement_forbidden_authority(record):
        errors.append("forbidden_authority_detected")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "feedback_concept_candidate_refinement_id": record.feedback_concept_candidate_refinement_id,
        "refinement_status": record.refinement_status,
    }


def build_feedback_concept_candidate_review_set(
    *,
    reviews: tuple[FeedbackConceptCandidateReviewRecord | dict[str, object], ...],
    scope_checks: tuple[FeedbackConceptCandidateScopeCheckRecord | dict[str, object], ...],
    counterexample_checks: tuple[
        FeedbackConceptCandidateCounterexampleCheckRecord | dict[str, object], ...
    ],
    refinements: tuple[FeedbackConceptCandidateRefinementRecord | dict[str, object], ...],
    created_at: str | None = None,
) -> FeedbackConceptCandidateReviewSet:
    review_records = tuple(_review_record(review) for review in reviews)
    scope_records = tuple(_scope_record(scope) for scope in scope_checks)
    counterexample_records = tuple(_counterexample_record(item) for item in counterexample_checks)
    refinement_records = tuple(_refinement_record(item) for item in refinements)
    refined_ids = tuple(
        item.source_concept_candidate_draft_id
        for item in refinement_records
        if item.refinement_status == "refined_concept_candidate_created"
    )
    held_ids = tuple(
        item.source_concept_candidate_draft_id
        for item in refinement_records
        if item.refinement_status == "held_for_more_evidence"
    )
    split_ids = tuple(
        item.source_concept_candidate_draft_id
        for item in refinement_records
        if item.refinement_status == "split_recommended"
    )
    rejected_ids = tuple(
        item.source_concept_candidate_draft_id
        for item in refinement_records
        if item.refinement_status == "rejected_by_review"
    )
    blocked_ids = tuple(
        item.source_concept_candidate_draft_id
        for item in refinement_records
        if item.refinement_status.startswith("blocked_")
        or item.refinement_status == "conflict_detected"
    )
    if any(
        _review_forbidden_authority(review) for review in review_records
    ) or any(_refinement_forbidden_authority(item) for item in refinement_records):
        status = "blocked_forbidden_authority_detected"
    elif any(
        not validate_feedback_concept_candidate_review_record(review)["valid"]
        for review in review_records
    ) or any(
        not validate_feedback_concept_candidate_refinement_record(item)["valid"]
        for item in refinement_records
    ):
        status = "blocked_invalid_review_records"
    elif refined_ids:
        status = "review_set_created_with_refined_candidates"
    elif split_ids:
        status = "review_set_created_with_split_recommendations"
    else:
        status = "review_set_created_all_held_or_blocked"
    return FeedbackConceptCandidateReviewSet(
        feedback_concept_candidate_review_set_id=_review_set_id(
            tuple(item.feedback_concept_candidate_refinement_id for item in refinement_records)
        ),
        schema_version=REVIEW_SET_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_draft_ids=tuple(
            item.source_concept_candidate_draft_id for item in refinement_records
        ),
        review_records=review_records,
        scope_check_records=scope_records,
        counterexample_check_records=counterexample_records,
        refinement_records=refinement_records,
        refined_candidate_ids=refined_ids,
        held_candidate_ids=held_ids,
        split_recommended_candidate_ids=split_ids,
        rejected_candidate_ids=rejected_ids,
        blocked_candidate_ids=blocked_ids,
        review_count=len(review_records),
        refined_count=len(refined_ids),
        held_count=len(held_ids),
        split_recommended_count=len(split_ids),
        blocked_count=len(blocked_ids),
        review_set_status=status,
        review_set_summary=_review_set_summary(status, len(refined_ids), len(refinement_records)),
        has_refined_candidates_for_reviewed_concept_preparation_later=bool(refined_ids),
        reviewed_concept_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        task_behavior_changed=False,
        source_trace_refs=_combined_trace_refs(
            *(item.source_trace_refs for item in review_records),
            *(item.source_trace_refs for item in scope_records),
            *(item.source_trace_refs for item in counterexample_records),
            *(item.source_trace_refs for item in refinement_records),
        ),
    )


def validate_feedback_concept_candidate_review_set(
    review_set: FeedbackConceptCandidateReviewSet | dict[str, object],
) -> dict[str, object]:
    record = _review_set_record(review_set)
    errors: list[str] = []
    if not record.feedback_concept_candidate_review_set_id:
        errors.append("missing_feedback_concept_candidate_review_set_id")
    if record.review_count != len(record.review_records):
        errors.append("review_count_mismatch")
    if record.refined_count != len(record.refined_candidate_ids):
        errors.append("refined_count_mismatch")
    if record.has_refined_candidates_for_reviewed_concept_preparation_later != bool(
        record.refined_candidate_ids
    ):
        errors.append("refined_flag_mismatch")
    if (
        record.reviewed_concept_created
        or record.memory_write_performed
        or record.automatic_learning_approval_created
        or record.task_behavior_changed
    ):
        errors.append("forbidden_authority_detected")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "feedback_concept_candidate_review_set_id": record.feedback_concept_candidate_review_set_id,
        "review_set_status": record.review_set_status,
    }


def build_feedback_concept_candidate_refinement_safety_audit(
    *,
    review_set: FeedbackConceptCandidateReviewSet | dict[str, object] | None,
    created_at: str | None = None,
) -> FeedbackConceptCandidateRefinementSafetyAudit:
    review_set_record = _review_set_record(review_set) if review_set is not None else None
    blocked_reasons = _safety_blocked_reasons(review_set_record)
    status = _safety_status(blocked_reasons, review_set_record)
    return FeedbackConceptCandidateRefinementSafetyAudit(
        feedback_concept_candidate_refinement_safety_audit_id=_safety_audit_id(
            tuple(
                item.feedback_concept_candidate_refinement_id
                for item in review_set_record.refinement_records
            )
            if review_set_record
            else ()
        ),
        schema_version=SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_review_set_id=(
            review_set_record.feedback_concept_candidate_review_set_id
            if review_set_record
            else None
        ),
        source_refinement_ids=tuple(
            item.feedback_concept_candidate_refinement_id
            for item in review_set_record.refinement_records
        )
        if review_set_record
        else (),
        feedback_concept_candidate_drafts_valid="invalid_draft" not in blocked_reasons,
        review_records_valid="invalid_review" not in blocked_reasons,
        scope_checks_valid="invalid_scope" not in blocked_reasons,
        counterexample_checks_valid="invalid_counterexample" not in blocked_reasons,
        refinement_records_valid="invalid_refinement" not in blocked_reasons,
        rollback_available="missing_rollback" not in blocked_reasons,
        refinement_only_confirmed=True,
        no_reviewed_concept_creation="reviewed_concept_created" not in blocked_reasons,
        no_memory_write="memory_write" not in blocked_reasons,
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_automatic_learning_approval="automatic_learning_approval" not in blocked_reasons,
        no_candidate_ordering_change="action_authority" not in blocked_reasons,
        no_selected_action_change="action_authority" not in blocked_reasons,
        no_final_action_change="action_authority" not in blocked_reasons,
        no_direct_command_creation="action_authority" not in blocked_reasons,
        no_execution_creation="action_authority" not in blocked_reasons,
        no_task_behavior_change="behavior_change" not in blocked_reasons,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(blocked_reasons),
        source_trace_refs=review_set_record.source_trace_refs if review_set_record else (),
    )


def validate_feedback_concept_candidate_refinement_safety_audit(
    audit: FeedbackConceptCandidateRefinementSafetyAudit | dict[str, object],
) -> dict[str, object]:
    record = _safety_audit_record(audit)
    errors: list[str] = []
    if not record.feedback_concept_candidate_refinement_safety_audit_id:
        errors.append("missing_feedback_concept_candidate_refinement_safety_audit_id")
    if record.audit_status not in ALLOWED_AUDIT_STATUSES:
        errors.append("invalid_audit_status")
    if record.audit_status.startswith("passed_") and record.blocked_reasons:
        errors.append("passing_audit_has_blocked_reasons")
    if not record.refinement_only_confirmed:
        errors.append("refinement_only_not_confirmed")
    if (
        not record.no_reviewed_concept_creation
        or not record.no_memory_write
        or not record.no_automatic_learning_approval
        or not record.no_candidate_ordering_change
        or not record.no_selected_action_change
        or not record.no_final_action_change
        or not record.no_direct_command_creation
        or not record.no_execution_creation
        or not record.no_task_behavior_change
    ):
        errors.append("forbidden_authority_detected")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "feedback_concept_candidate_refinement_safety_audit_id": record.feedback_concept_candidate_refinement_safety_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_demo_successful_expected_effect_refinement() -> dict[str, object]:
    return _build_demo_bundle(build_demo_successful_expected_effect_to_concept_candidate())


def build_demo_failed_expected_effect_refinement() -> dict[str, object]:
    return _build_demo_bundle(build_demo_failed_expected_effect_to_concept_candidate())


def build_demo_goal_reached_refinement() -> dict[str, object]:
    return _build_demo_bundle(build_demo_goal_reached_to_concept_candidate())


def build_demo_no_progress_refinement() -> dict[str, object]:
    return _build_demo_bundle(build_demo_no_progress_to_concept_candidate())


def build_demo_observation_only_refinement() -> dict[str, object]:
    return _build_demo_bundle(build_demo_observation_only_to_concept_candidate())


def build_demo_unknown_outcome_held_refinement() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_unknown_outcome_held_feedback_review(),
        teacher_review_status="held_for_more_evidence",
    )


def build_demo_system_fault_blocked_refinement() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_system_fault_blocked_feedback_review(),
        teacher_review_status="conflict_detected",
    )


def build_demo_blocked_invalid_concept_candidate_draft_refinement() -> dict[str, object]:
    payload = build_demo_successful_expected_effect_to_concept_candidate()
    draft = _draft_record(payload["learning_feedback_to_concept_candidate_draft"])
    payload["learning_feedback_to_concept_candidate_draft"] = replace(
        draft,
        concept_candidate_status="blocked_invalid_learning_feedback",
    ).to_dict()
    return _build_demo_bundle(payload)


def build_demo_blocked_missing_teacher_review_refinement() -> dict[str, object]:
    payload = build_demo_successful_expected_effect_to_concept_candidate()
    return _build_demo_bundle(payload, missing_review=True)


def build_demo_blocked_teacher_rejected_refinement() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_successful_expected_effect_to_concept_candidate(),
        teacher_review_status="rejected",
    )


def build_demo_blocked_scope_too_broad_refinement() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_successful_expected_effect_to_concept_candidate(),
        force_scope_too_broad=True,
    )


def build_demo_blocked_unhandled_counterexample_refinement() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_successful_expected_effect_to_concept_candidate(),
        counterexample_refs=("counterexample:contradicts_scope",),
        counterexample_notes=(),
    )


def build_demo_blocked_reviewed_concept_created_refinement() -> dict[str, object]:
    return _mutated_successful_demo(reviewed_concept_created=True)


def build_demo_blocked_memory_write_refinement() -> dict[str, object]:
    return _mutated_successful_demo(memory_write_performed=True)


def build_demo_blocked_automatic_learning_approval_refinement() -> dict[str, object]:
    return _mutated_successful_demo(automatic_learning_approval_created=True)


def build_demo_blocked_action_authority_refinement() -> dict[str, object]:
    return _mutated_successful_demo(selected_action_changed=True)


def build_demo_blocked_behavior_change_refinement() -> dict[str, object]:
    return _mutated_successful_demo(task_behavior_changed=True)


def build_demo_feedback_concept_candidate_refinement_case(case: str) -> dict[str, object]:
    cases = {
        "successful-expected-effect": build_demo_successful_expected_effect_refinement,
        "failed-expected-effect": build_demo_failed_expected_effect_refinement,
        "goal-reached": build_demo_goal_reached_refinement,
        "no-progress": build_demo_no_progress_refinement,
        "observation-only": build_demo_observation_only_refinement,
        "unknown-outcome": build_demo_unknown_outcome_held_refinement,
        "system-fault": build_demo_system_fault_blocked_refinement,
    }
    if case not in cases:
        raise ValueError(f"unknown demo case: {case}")
    return cases[case]()


def build_demo_blocked_feedback_concept_candidate_refinement(case: str) -> dict[str, object]:
    cases = {
        "invalid-concept-candidate-draft": build_demo_blocked_invalid_concept_candidate_draft_refinement,
        "missing-teacher-review": build_demo_blocked_missing_teacher_review_refinement,
        "teacher-rejected": build_demo_blocked_teacher_rejected_refinement,
        "scope-too-broad": build_demo_blocked_scope_too_broad_refinement,
        "unhandled-counterexample": build_demo_blocked_unhandled_counterexample_refinement,
        "reviewed-concept-created": build_demo_blocked_reviewed_concept_created_refinement,
        "memory-write-detected": build_demo_blocked_memory_write_refinement,
        "automatic-learning-approval": build_demo_blocked_automatic_learning_approval_refinement,
        "action-authority-detected": build_demo_blocked_action_authority_refinement,
        "behavior-change-detected": build_demo_blocked_behavior_change_refinement,
    }
    if case not in cases:
        raise ValueError(f"unknown blocked demo case: {case}")
    return cases[case]()


def _build_demo_bundle(
    package90_payload: dict[str, object],
    *,
    teacher_review_status: str = "approved_for_refinement",
    missing_review: bool = False,
    force_scope_too_broad: bool = False,
    counterexample_refs: tuple[str, ...] = (),
    counterexample_notes: tuple[str, ...] = (),
    requires_split: bool = False,
) -> dict[str, object]:
    draft = _draft_record(package90_payload["learning_feedback_to_concept_candidate_draft"])
    package90_audit = _package90_audit_record(
        package90_payload["learning_feedback_to_concept_candidate_safety_audit"]
    )
    review = None
    if not missing_review:
        review = build_feedback_concept_candidate_review_record(
            draft=draft,
            feedback_to_concept_candidate_safety_audit=package90_audit,
            teacher_review_status=teacher_review_status,
        )
    scope = build_feedback_concept_candidate_scope_check_record(
        draft=draft,
        review=review,
        force_scope_too_broad=force_scope_too_broad,
    )
    counterexample = build_feedback_concept_candidate_counterexample_check_record(
        draft=draft,
        review=review,
        scope_check=scope,
        counterexample_refs=counterexample_refs,
        counterexample_notes=counterexample_notes,
        requires_split=requires_split,
    )
    refinement = build_feedback_concept_candidate_refinement_record(
        draft=draft,
        review=review,
        scope_check=scope,
        counterexample_check=counterexample,
    )
    review_set = build_feedback_concept_candidate_review_set(
        reviews=(review,) if review is not None else (),
        scope_checks=(scope,),
        counterexample_checks=(counterexample,),
        refinements=(refinement,),
    )
    audit = build_feedback_concept_candidate_refinement_safety_audit(
        review_set=review_set
    )
    payload = dict(package90_payload)
    payload.update(
        {
            "feedback_concept_candidate_review": review.to_dict() if review else None,
            "feedback_concept_candidate_scope_check": scope.to_dict(),
            "feedback_concept_candidate_counterexample_check": counterexample.to_dict(),
            "feedback_concept_candidate_refinement": refinement.to_dict(),
            "feedback_concept_candidate_review_set": review_set.to_dict(),
            "feedback_concept_candidate_refinement_safety_audit": audit.to_dict(),
        }
    )
    return payload


def _mutated_successful_demo(**changes: object) -> dict[str, object]:
    payload = _build_demo_bundle(build_demo_successful_expected_effect_to_concept_candidate())
    review_set = _review_set_record(payload["feedback_concept_candidate_review_set"])
    refinement = replace(
        _refinement_record(payload["feedback_concept_candidate_refinement"]),
        **changes,
    )
    review_set = replace(review_set, refinement_records=(refinement,))
    audit = build_feedback_concept_candidate_refinement_safety_audit(
        review_set=review_set
    )
    payload["feedback_concept_candidate_refinement"] = refinement.to_dict()
    payload["feedback_concept_candidate_review_set"] = review_set.to_dict()
    payload["feedback_concept_candidate_refinement_safety_audit"] = audit.to_dict()
    return payload


def _review_reason(
    status: str,
    draft: LearningFeedbackToConceptCandidateDraftRecord,
) -> str:
    if status == "approved_for_refinement":
        return f"{draft.proposed_concept_label} approved for refinement only."
    if status == "held_for_more_evidence":
        return "More evidence is required before refinement."
    if status == "rejected":
        return "Teacher rejected this feedback-derived draft."
    if status == "conflict_detected":
        return "Conflict detected; no refinement may proceed."
    if status == "needs_split":
        return "Teacher requested split consideration."
    return "Draft cannot be reviewed for refinement."


def _scope_text_too_broad(scope: str) -> bool:
    lowered = scope.lower()
    return "all blocked states" in lowered or "all push actions" in lowered


def _scope_summary(
    status: str,
    draft: LearningFeedbackToConceptCandidateDraftRecord,
) -> str:
    if status == "scope_valid_for_refinement":
        return "Scope remains sandbox-bound and valid for refinement."
    if status == "scope_too_broad":
        return "Scope is too broad for a single task closure evidence point."
    if status == "blocked_invalid_review":
        return "Scope check blocked because review is invalid or missing."
    return f"Scope check status {status} for {draft.proposed_concept_label}."


def _refined_scope_suggestion(
    draft: LearningFeedbackToConceptCandidateDraftRecord,
    too_broad: bool,
) -> str:
    base = (
        f"in bounded sandbox context, direct_command={draft.direct_command}, "
        f"expected_effect={draft.expected_effect}, outcome={draft.outcome_class}, "
        f"goal_delta={draft.goal_delta_class}"
    )
    if too_broad:
        return f"narrowed single-case scope: {base}"
    return base


def _counterexample_summary(status: str) -> str:
    if status == "counterexample_check_passed_no_counterexamples":
        return "No counterexamples supplied; support evidence preserved."
    if status == "counterexample_check_requires_scope_narrowing":
        return "Counterexamples require scope narrowing."
    if status == "counterexample_check_requires_split":
        return "Counterexamples require split recommendation."
    if status == "counterexample_check_blocked_unhandled_counterexamples":
        return "Unhandled counterexamples block refinement."
    return f"Counterexample check status {status}."


def _refinement_status(
    draft: LearningFeedbackToConceptCandidateDraftRecord,
    review: FeedbackConceptCandidateReviewRecord | None,
    scope: FeedbackConceptCandidateScopeCheckRecord,
    counterexample: FeedbackConceptCandidateCounterexampleCheckRecord,
) -> str:
    if _draft_forbidden_authority(draft):
        return "blocked_forbidden_authority_detected"
    if review is None or not validate_feedback_concept_candidate_review_record(review)["valid"]:
        return "blocked_invalid_review"
    if _review_forbidden_authority(review):
        return "blocked_forbidden_authority_detected"
    if review.teacher_review_status == "rejected":
        return "rejected_by_review"
    if review.teacher_review_status in {
        "held_for_more_evidence",
        "needs_scope_narrowing",
        "needs_counterexample_check",
    }:
        return "held_for_more_evidence"
    if review.teacher_review_status == "conflict_detected":
        return "conflict_detected"
    if not _draft_valid_for_refinement(draft):
        return "blocked_invalid_review"
    if scope.scope_check_status in {"scope_too_broad", "blocked_invalid_review"}:
        return "blocked_invalid_scope"
    if counterexample.counterexample_check_status == "counterexample_check_requires_split":
        return "split_recommended"
    if counterexample.counterexample_check_status == "counterexample_check_requires_scope_narrowing":
        return "held_for_more_evidence"
    if counterexample.counterexample_check_status == "counterexample_check_blocked_unhandled_counterexamples":
        return "blocked_unhandled_counterexamples"
    if counterexample.counterexample_check_status == "blocked_invalid_scope_check":
        return "blocked_invalid_scope"
    if review.teacher_review_status == "needs_split":
        return "split_recommended"
    if review.teacher_review_status == "approved_for_refinement":
        return "refined_concept_candidate_created"
    return "held_for_more_evidence"


def _refined_label_and_confidence(
    draft: LearningFeedbackToConceptCandidateDraftRecord,
    status: str,
) -> tuple[str, str]:
    command = (draft.direct_command or "unknown").replace(" ", "_")
    if status != "refined_concept_candidate_created":
        return draft.proposed_concept_label, "blocked"
    if draft.concept_candidate_kind == "positive_affordance_concept_candidate":
        return f"sandbox_positive_affordance_{command}", "normal"
    if draft.concept_candidate_kind == "negative_affordance_concept_candidate":
        return f"sandbox_negative_affordance_{command}", "normal"
    if draft.concept_candidate_kind == "goal_completion_concept_candidate":
        confidence = "high" if draft.goal_delta_class == "goal_reached" else "normal"
        return f"sandbox_goal_completion_by_{command}", confidence
    if draft.concept_candidate_kind == "no_progress_concept_candidate":
        return f"sandbox_no_progress_{command}", "low"
    if draft.concept_candidate_kind == "observation_context_concept_candidate":
        return f"sandbox_observation_context_{command}", "low"
    return draft.proposed_concept_label, "blocked"


def _refinement_summary(status: str, label: str) -> str:
    if status == "refined_concept_candidate_created":
        return f"Refined feedback-derived ConceptCandidate {label} created."
    if status == "split_recommended":
        return "ConceptCandidate split recommended; no ReviewedConcept preparation readiness."
    if status == "held_for_more_evidence":
        return "ConceptCandidate held for more evidence."
    return f"Refinement status {status}; no ReviewedConcept created."


def _refinement_reason(status: str) -> str:
    if status == "refined_concept_candidate_created":
        return "Teacher review, sandbox-bound scope check, and counterexample check passed."
    if status == "split_recommended":
        return "Counterexample check requested split before further preparation."
    if status == "blocked_unhandled_counterexamples":
        return "Unhandled counterexamples block refinement."
    if status == "blocked_invalid_scope":
        return "Scope is invalid or too broad for refinement."
    return "Review or evidence does not permit refined candidate creation."


def _split_labels(draft: LearningFeedbackToConceptCandidateDraftRecord) -> tuple[str, ...]:
    command = (draft.direct_command or "unknown").replace(" ", "_")
    return (f"{draft.proposed_concept_label}_{command}_context_a", f"{draft.proposed_concept_label}_{command}_context_b")


def _review_set_summary(status: str, refined_count: int, total_count: int) -> str:
    if status == "review_set_created_with_refined_candidates":
        return f"{refined_count} of {total_count} feedback ConceptCandidate drafts refined."
    if status == "review_set_created_with_split_recommendations":
        return "Review set created with split recommendations and no refined candidate readiness."
    if status == "review_set_created_all_held_or_blocked":
        return "All feedback ConceptCandidate drafts held, rejected, or blocked."
    return "Feedback ConceptCandidate review set blocked."


def _safety_blocked_reasons(
    review_set: FeedbackConceptCandidateReviewSet | None,
) -> tuple[str, ...]:
    if review_set is None:
        return ("invalid_review",)
    reasons: list[str] = []
    if not validate_feedback_concept_candidate_review_set(review_set)["valid"]:
        reasons.append("invalid_review")
    for review in review_set.review_records:
        if review.teacher_review_status == "blocked_invalid_feedback_concept_candidate_draft":
            reasons.append("invalid_draft")
        if _review_forbidden_authority(review):
            reasons.append("action_authority")
    for scope in review_set.scope_check_records:
        if scope.scope_check_status in {"scope_too_broad", "blocked_invalid_review"}:
            reasons.append("invalid_scope")
        if (
            scope.reviewed_concept_created
            or scope.memory_write_performed
            or scope.automatic_learning_approval_created
        ):
            reasons.append("memory_write")
    for counterexample in review_set.counterexample_check_records:
        if counterexample.counterexample_check_status in {
            "counterexample_check_blocked_unhandled_counterexamples",
            "blocked_invalid_scope_check",
        }:
            reasons.append("invalid_counterexample")
        if (
            counterexample.reviewed_concept_created
            or counterexample.memory_write_performed
            or counterexample.automatic_learning_approval_created
        ):
            reasons.append("memory_write")
    for refinement in review_set.refinement_records:
        if not validate_feedback_concept_candidate_refinement_record(refinement)["valid"]:
            reasons.append("invalid_refinement")
        if refinement.refinement_status == "blocked_invalid_review":
            reasons.append("invalid_review")
        if refinement.refinement_status == "blocked_invalid_scope":
            reasons.append("invalid_scope")
        if refinement.refinement_status == "blocked_unhandled_counterexamples":
            reasons.append("invalid_counterexample")
        if (
            refinement.refinement_status == "refined_concept_candidate_created"
            and not refinement.rollback_available
        ):
            reasons.append("missing_rollback")
        if refinement.reviewed_concept_created:
            reasons.append("reviewed_concept_created")
        if refinement.memory_write_performed:
            reasons.append("memory_write")
        if refinement.automatic_learning_approval_created:
            reasons.append("automatic_learning_approval")
        if (
            refinement.candidate_ordering_changed
            or refinement.selected_action_changed
            or refinement.final_action_changed
            or refinement.direct_command_created
            or refinement.execution_created
        ):
            reasons.append("action_authority")
        if refinement.task_behavior_changed:
            reasons.append("behavior_change")
    return tuple(dict.fromkeys(reasons))


def _safety_status(
    reasons: tuple[str, ...],
    review_set: FeedbackConceptCandidateReviewSet | None,
) -> str:
    if "reviewed_concept_created" in reasons:
        return "blocked_reviewed_concept_creation_detected"
    if "memory_write" in reasons:
        return "blocked_memory_write_detected"
    if "automatic_learning_approval" in reasons:
        return "blocked_automatic_learning_approval_detected"
    if "action_authority" in reasons:
        return "blocked_action_authority_detected"
    if "behavior_change" in reasons:
        return "blocked_behavior_change_detected"
    if "invalid_draft" in reasons:
        return "blocked_invalid_feedback_concept_candidate_draft"
    if "invalid_review" in reasons:
        return "blocked_invalid_review"
    if "invalid_scope" in reasons:
        return "blocked_invalid_scope_check"
    if "invalid_counterexample" in reasons:
        return "blocked_invalid_counterexample_check"
    if "invalid_refinement" in reasons or "missing_rollback" in reasons:
        return "blocked_invalid_refinement"
    if review_set and review_set.refined_candidate_ids:
        return "passed_feedback_concept_candidate_refinement_only"
    return "passed_all_held_or_blocked"


def _draft_valid_for_refinement(draft: LearningFeedbackToConceptCandidateDraftRecord) -> bool:
    validation = validate_learning_feedback_to_concept_candidate_draft_record(draft)
    return (
        validation["valid"] is True
        and draft.concept_candidate_status == "concept_candidate_draft_created"
        and not _draft_forbidden_authority(draft)
    )


def _package90_audit_passed(audit: LearningFeedbackToConceptCandidateSafetyAudit) -> bool:
    validation = validate_learning_feedback_to_concept_candidate_safety_audit(audit)
    return validation["valid"] is True and audit.audit_status in PASSING_PACKAGE90_AUDIT_STATUSES


def _draft_forbidden_authority(draft: LearningFeedbackToConceptCandidateDraftRecord) -> bool:
    return (
        draft.reviewed_concept_created
        or draft.memory_write_performed
        or draft.automatic_learning_approval_created
        or draft.candidate_ordering_changed
        or draft.selected_action_changed
        or draft.final_action_changed
        or draft.direct_command_created
        or draft.execution_created
        or draft.task_behavior_changed
    )


def _review_forbidden_authority(review: FeedbackConceptCandidateReviewRecord) -> bool:
    return (
        review.approved_for_reviewed_concept
        or review.approved_for_memory_write
        or review.approved_for_behavior_change
        or review.approved_for_action_authority
        or review.approved_for_automatic_learning_approval
        or review.reviewed_concept_created
        or review.memory_write_performed
        or review.automatic_learning_approval_created
        or review.task_behavior_changed
        or review.candidate_ordering_changed
        or review.selected_action_changed
        or review.final_action_changed
        or review.direct_command_created
        or review.execution_created
    )


def _refinement_forbidden_authority(refinement: FeedbackConceptCandidateRefinementRecord) -> bool:
    return (
        refinement.reviewed_concept_created
        or refinement.memory_write_performed
        or refinement.automatic_learning_approval_created
        or refinement.task_behavior_changed
        or refinement.candidate_ordering_changed
        or refinement.selected_action_changed
        or refinement.final_action_changed
        or refinement.direct_command_created
        or refinement.execution_created
    )


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    refs: list[str] = []
    for group in groups:
        for ref in group:
            if ref and ref not in refs:
                refs.append(ref)
    return tuple(refs)


def _review_set_id(refinement_ids: tuple[str, ...]) -> str:
    if not refinement_ids:
        return "feedback_concept_candidate_review_set:empty"
    return "feedback_concept_candidate_review_set:" + refinement_ids[0].replace(":", "_")


def _safety_audit_id(refinement_ids: tuple[str, ...]) -> str:
    if not refinement_ids:
        return "feedback_concept_candidate_refinement_safety_audit:empty"
    return "feedback_concept_candidate_refinement_safety_audit:" + refinement_ids[0].replace(
        ":",
        "_",
    )


def _draft_record(
    draft: LearningFeedbackToConceptCandidateDraftRecord | dict[str, object],
) -> LearningFeedbackToConceptCandidateDraftRecord:
    return (
        draft
        if isinstance(draft, LearningFeedbackToConceptCandidateDraftRecord)
        else LearningFeedbackToConceptCandidateDraftRecord.from_dict(dict(draft))
    )


def _package90_audit_record(
    audit: LearningFeedbackToConceptCandidateSafetyAudit | dict[str, object] | None,
) -> LearningFeedbackToConceptCandidateSafetyAudit | None:
    if audit is None:
        return None
    return (
        audit
        if isinstance(audit, LearningFeedbackToConceptCandidateSafetyAudit)
        else LearningFeedbackToConceptCandidateSafetyAudit.from_dict(dict(audit))
    )


def _review_record(
    review: FeedbackConceptCandidateReviewRecord | dict[str, object],
) -> FeedbackConceptCandidateReviewRecord:
    return (
        review
        if isinstance(review, FeedbackConceptCandidateReviewRecord)
        else FeedbackConceptCandidateReviewRecord.from_dict(dict(review))
    )


def _scope_record(
    scope: FeedbackConceptCandidateScopeCheckRecord | dict[str, object],
) -> FeedbackConceptCandidateScopeCheckRecord:
    return (
        scope
        if isinstance(scope, FeedbackConceptCandidateScopeCheckRecord)
        else FeedbackConceptCandidateScopeCheckRecord.from_dict(dict(scope))
    )


def _counterexample_record(
    counterexample: FeedbackConceptCandidateCounterexampleCheckRecord | dict[str, object],
) -> FeedbackConceptCandidateCounterexampleCheckRecord:
    return (
        counterexample
        if isinstance(counterexample, FeedbackConceptCandidateCounterexampleCheckRecord)
        else FeedbackConceptCandidateCounterexampleCheckRecord.from_dict(dict(counterexample))
    )


def _refinement_record(
    refinement: FeedbackConceptCandidateRefinementRecord | dict[str, object],
) -> FeedbackConceptCandidateRefinementRecord:
    return (
        refinement
        if isinstance(refinement, FeedbackConceptCandidateRefinementRecord)
        else FeedbackConceptCandidateRefinementRecord.from_dict(dict(refinement))
    )


def _review_set_record(
    review_set: FeedbackConceptCandidateReviewSet | dict[str, object],
) -> FeedbackConceptCandidateReviewSet:
    return (
        review_set
        if isinstance(review_set, FeedbackConceptCandidateReviewSet)
        else FeedbackConceptCandidateReviewSet.from_dict(dict(review_set))
    )


def _safety_audit_record(
    audit: FeedbackConceptCandidateRefinementSafetyAudit | dict[str, object],
) -> FeedbackConceptCandidateRefinementSafetyAudit:
    return (
        audit
        if isinstance(audit, FeedbackConceptCandidateRefinementSafetyAudit)
        else FeedbackConceptCandidateRefinementSafetyAudit.from_dict(dict(audit))
    )


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
