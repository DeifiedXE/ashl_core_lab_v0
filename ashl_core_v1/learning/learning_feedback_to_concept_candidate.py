"""Teacher-gated LearningFeedbackCandidate to ConceptCandidate draft records."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.task_closure_learning_feedback_candidate import (
    LearningFeedbackCandidateEvidencePacket,
    LearningFeedbackCandidateRecord,
    LearningFeedbackCandidateSafetyAudit,
    LearningFeedbackCandidateSet,
    build_demo_expected_effect_failed_learning_feedback_candidate,
    build_demo_goal_reached_learning_feedback_candidate,
    build_demo_no_progress_learning_feedback_candidate,
    build_demo_observation_only_learning_feedback_candidate,
    build_demo_progress_learning_feedback_candidate,
    build_demo_system_fault_learning_feedback_candidate,
    build_demo_unknown_outcome_learning_feedback_candidate,
    validate_learning_feedback_candidate_evidence_packet,
    validate_learning_feedback_candidate_record,
    validate_learning_feedback_candidate_safety_audit,
    validate_learning_feedback_candidate_set,
)


SOURCE_ENGINE = "learning_engine"

TEACHER_REVIEW_SCHEMA_VERSION = "learning_engine_learning_feedback_teacher_review_v0"
TEACHER_REVIEW_SET_SCHEMA_VERSION = (
    "learning_engine_learning_feedback_teacher_review_set_v0"
)
DRAFT_SCHEMA_VERSION = "learning_engine_feedback_to_concept_candidate_draft_v0"
ROLLBACK_SCHEMA_VERSION = "learning_engine_feedback_to_concept_candidate_rollback_v0"
SAFETY_AUDIT_SCHEMA_VERSION = (
    "learning_engine_feedback_to_concept_candidate_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Learning Engine can teacher-review LearningFeedbackCandidates "
    "from task closure and convert approved feedback into ConceptCandidate draft "
    "records, while avoiding ReviewedConcept creation, memory writes, behavior "
    "changes, action authority changes, or automatic learning approval."
)
BLOCKED_CLAIMS = (
    "no_reviewed_concept_creation",
    "no_memory_write",
    "no_behavior_change",
    "no_action_authority_change",
    "no_automatic_learning_approval",
)

PASSING_FEEDBACK_AUDIT_STATUSES = {
    "passed_learning_feedback_candidate_only",
    "passed_candidate_created_with_partial_evidence",
}

ALLOWED_TEACHER_REVIEW_STATUSES = {
    "approved_for_concept_candidate_draft",
    "held_for_more_evidence",
    "rejected",
    "needs_more_evidence",
    "conflict_detected",
    "blocked_invalid_learning_feedback_candidate",
    "blocked_invalid_evidence_packet",
    "blocked_forbidden_authority_detected",
}
ALLOWED_REVIEW_ACTOR_ROLES = {"teacher", "project_owner", "system_demo"}
ALLOWED_REVIEW_SOURCES = {"explicit_teacher_review", "demo_review"}
ALLOWED_SET_REVIEW_STATUSES = {
    "review_set_created_with_approved_feedback",
    "review_set_created_all_held_or_rejected",
    "needs_more_evidence",
    "conflict_detected",
    "blocked_invalid_review_records",
    "blocked_forbidden_authority_detected",
}
ALLOWED_CONCEPT_CANDIDATE_KINDS = {
    "positive_affordance_concept_candidate",
    "negative_affordance_concept_candidate",
    "goal_completion_concept_candidate",
    "no_progress_concept_candidate",
    "observation_context_concept_candidate",
    "unknown_outcome_concept_candidate",
    "system_fault_diagnostic_candidate",
}
ALLOWED_CONCEPT_CANDIDATE_STATUSES = {
    "concept_candidate_draft_created",
    "held_for_more_evidence",
    "rejected_by_teacher",
    "blocked_conflict_detected",
    "blocked_invalid_learning_feedback",
    "blocked_invalid_teacher_review",
    "blocked_forbidden_authority_detected",
    "rollback_applied",
}
ALLOWED_CONCEPT_CANDIDATE_CONFIDENCE = {"low", "normal", "high", "blocked"}
ALLOWED_ROLLBACK_STATUSES = {
    "rollback_record_created",
    "rollback_applied_to_withdraw_concept_candidate_draft",
    "blocked_invalid_concept_candidate_draft",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_concept_candidate_draft_only",
    "passed_no_concept_candidate_created",
    "blocked_invalid_learning_feedback_candidate",
    "blocked_invalid_teacher_review",
    "blocked_invalid_concept_candidate_draft",
    "blocked_missing_rollback",
    "blocked_reviewed_concept_creation_detected",
    "blocked_memory_write_detected",
    "blocked_action_authority_detected",
    "blocked_behavior_change_detected",
    "blocked_automatic_learning_approval_detected",
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
class LearningFeedbackTeacherReviewRecord:
    learning_feedback_teacher_review_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_learning_feedback_candidate_id: str
    source_learning_feedback_evidence_packet_id: str | None
    source_learning_feedback_candidate_safety_audit_id: str | None
    feedback_candidate_kind: str
    learning_signal_class: str
    review_priority: str
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
    approved_for_concept_candidate_draft: bool
    approved_for_reviewed_concept: bool
    approved_for_memory_write: bool
    approved_for_behavior_change: bool
    approved_for_action_authority: bool
    approved_for_automatic_learning_approval: bool
    requires_concept_candidate_review_later: bool
    requires_counterexample_check_later: bool
    requires_reviewed_concept_gate_later: bool
    requires_memory_write_gate_later: bool
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
        if self.schema_version != TEACHER_REVIEW_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_learning_feedback_teacher_review_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
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
    def from_dict(cls, data: dict[str, object]) -> "LearningFeedbackTeacherReviewRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class LearningFeedbackTeacherReviewSet:
    learning_feedback_teacher_review_set_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_learning_feedback_candidate_set_id: str | None
    candidate_review_records: tuple[LearningFeedbackTeacherReviewRecord, ...]
    approved_candidate_ids: tuple[str, ...]
    held_candidate_ids: tuple[str, ...]
    rejected_candidate_ids: tuple[str, ...]
    needs_more_evidence_candidate_ids: tuple[str, ...]
    conflict_detected_candidate_ids: tuple[str, ...]
    review_count: int
    approved_count: int
    held_count: int
    rejected_count: int
    blocked_count: int
    set_review_status: str
    set_review_summary: str
    has_approved_feedback_for_concept_candidate_draft: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    task_behavior_changed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TEACHER_REVIEW_SET_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_learning_feedback_teacher_review_set_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.set_review_status not in ALLOWED_SET_REVIEW_STATUSES:
            raise ValueError(f"unknown set_review_status: {self.set_review_status}")
        object.__setattr__(
            self,
            "candidate_review_records",
            tuple(
                review
                if isinstance(review, LearningFeedbackTeacherReviewRecord)
                else LearningFeedbackTeacherReviewRecord.from_dict(dict(review))
                for review in self.candidate_review_records
            ),
        )
        for name in (
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
    def from_dict(cls, data: dict[str, object]) -> "LearningFeedbackTeacherReviewSet":
        return cls(**dict(data))


@dataclass(frozen=True)
class LearningFeedbackToConceptCandidateDraftRecord:
    concept_candidate_draft_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_learning_feedback_candidate_id: str
    source_learning_feedback_evidence_packet_id: str | None
    source_learning_feedback_teacher_review_id: str
    source_learning_feedback_teacher_review_set_id: str | None
    source_task_closure_id: str | None
    source_outcome_evaluation_id: str | None
    source_goal_delta_evaluation_id: str | None
    source_expected_effect_reference_id: str | None
    source_sense_handoff_id: str | None
    source_sandbox_execution_id: str | None
    direct_command: str | None
    expected_effect: str | None
    outcome_class: str
    goal_delta_class: str
    closure_status: str
    feedback_candidate_kind: str
    learning_signal_class: str
    concept_candidate_kind: str
    concept_candidate_status: str
    concept_candidate_confidence: str
    concept_candidate_summary: str
    concept_candidate_reason: str
    proposed_concept_label: str
    proposed_concept_scope: str
    proposed_support_evidence_refs: tuple[str, ...]
    proposed_counterexample_refs: tuple[str, ...]
    proposed_counterexample_notes: tuple[str, ...]
    requires_teacher_review_before_concept_acceptance: bool
    requires_counterexample_check_later: bool
    requires_refinement_later: bool
    requires_reviewed_concept_gate_later: bool
    requires_memory_write_gate_later: bool
    actual_existing_concept_candidate_created: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_created: bool
    execution_created: bool
    task_behavior_changed: bool
    rollback_available: bool
    rollback_record_id: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DRAFT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_feedback_to_concept_candidate_draft_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.concept_candidate_kind not in ALLOWED_CONCEPT_CANDIDATE_KINDS:
            raise ValueError(f"unknown concept_candidate_kind: {self.concept_candidate_kind}")
        if self.concept_candidate_status not in ALLOWED_CONCEPT_CANDIDATE_STATUSES:
            raise ValueError(
                f"unknown concept_candidate_status: {self.concept_candidate_status}"
            )
        if self.concept_candidate_confidence not in ALLOWED_CONCEPT_CANDIDATE_CONFIDENCE:
            raise ValueError(
                f"unknown concept_candidate_confidence: {self.concept_candidate_confidence}"
            )
        for name in (
            "proposed_support_evidence_refs",
            "proposed_counterexample_refs",
            "proposed_counterexample_notes",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "LearningFeedbackToConceptCandidateDraftRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class LearningFeedbackToConceptCandidateRollbackRecord:
    concept_candidate_rollback_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_draft_id: str
    source_learning_feedback_candidate_id: str
    concept_candidate_draft_created_before_rollback: bool
    concept_candidate_draft_available_after_rollback: bool
    rollback_available: bool
    rollback_applied: bool
    rollback_reason: str
    rollback_status: str
    rollback_summary: str
    reviewed_concept_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    task_behavior_changed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ROLLBACK_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be learning_engine_feedback_to_concept_candidate_rollback_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
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
    def from_dict(cls, data: dict[str, object]) -> "LearningFeedbackToConceptCandidateRollbackRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class LearningFeedbackToConceptCandidateSafetyAudit:
    concept_candidate_safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_learning_feedback_teacher_review_set_id: str | None
    source_concept_candidate_draft_ids: tuple[str, ...]
    learning_feedback_candidate_valid: bool
    evidence_packet_valid: bool
    teacher_review_valid: bool
    concept_candidate_draft_valid: bool
    rollback_available: bool
    concept_candidate_draft_only_confirmed: bool
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
                "schema_version must be learning_engine_feedback_to_concept_candidate_safety_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in (
            "source_concept_candidate_draft_ids",
            "blocked_claims",
            "blocked_reasons",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "LearningFeedbackToConceptCandidateSafetyAudit":
        return cls(**dict(data))


def build_learning_feedback_teacher_review_record(
    *,
    candidate: LearningFeedbackCandidateRecord | dict[str, object],
    evidence_packet: LearningFeedbackCandidateEvidencePacket | dict[str, object] | None = None,
    candidate_safety_audit: LearningFeedbackCandidateSafetyAudit | dict[str, object] | None = None,
    teacher_review_status: str = "approved_for_concept_candidate_draft",
    teacher_review_reason: str | None = None,
    teacher_review_text: str = "Demo teacher gate approves concept candidate draft only.",
    review_actor: str = "system_demo",
    review_actor_role: str = "system_demo",
    review_source: str = "demo_review",
    created_at: str | None = None,
) -> LearningFeedbackTeacherReviewRecord:
    candidate_record = _candidate_record(candidate)
    packet_record = _packet_record(evidence_packet)
    audit_record = _candidate_audit_record(candidate_safety_audit)
    status = teacher_review_status
    if _forbidden_feedback_candidate_authority(candidate_record):
        status = "blocked_forbidden_authority_detected"
    elif not validate_learning_feedback_candidate_record(candidate_record)["valid"]:
        status = "blocked_invalid_learning_feedback_candidate"
    elif packet_record is not None and not validate_learning_feedback_candidate_evidence_packet(
        packet_record
    )["valid"]:
        status = "blocked_invalid_evidence_packet"
    elif audit_record is not None and not _feedback_audit_passed(audit_record):
        status = "blocked_invalid_learning_feedback_candidate"
    if status == "approved_for_concept_candidate_draft" and not _candidate_can_be_teacher_approved_for_draft(
        candidate_record
    ):
        status = "held_for_more_evidence"

    approved = status == "approved_for_concept_candidate_draft"
    reason = teacher_review_reason or _review_reason(status, candidate_record)
    return LearningFeedbackTeacherReviewRecord(
        learning_feedback_teacher_review_id=(
            f"learning_feedback_teacher_review:{candidate_record.learning_feedback_candidate_id}"
        ),
        schema_version=TEACHER_REVIEW_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_learning_feedback_candidate_id=candidate_record.learning_feedback_candidate_id,
        source_learning_feedback_evidence_packet_id=(
            packet_record.learning_feedback_evidence_packet_id if packet_record else None
        ),
        source_learning_feedback_candidate_safety_audit_id=(
            audit_record.learning_feedback_candidate_safety_audit_id if audit_record else None
        ),
        feedback_candidate_kind=candidate_record.feedback_candidate_kind,
        learning_signal_class=candidate_record.learning_signal_class,
        review_priority=candidate_record.review_priority,
        direct_command=candidate_record.direct_command,
        expected_effect=candidate_record.expected_effect,
        outcome_class=candidate_record.outcome_class,
        goal_delta_class=candidate_record.goal_delta_class,
        closure_status=candidate_record.closure_status,
        teacher_review_status=status,
        teacher_review_reason=reason,
        teacher_review_text=teacher_review_text,
        review_actor=review_actor,
        review_actor_role=review_actor_role,
        review_source=review_source,
        approved_for_concept_candidate_draft=approved,
        approved_for_reviewed_concept=False,
        approved_for_memory_write=False,
        approved_for_behavior_change=False,
        approved_for_action_authority=False,
        approved_for_automatic_learning_approval=False,
        requires_concept_candidate_review_later=True,
        requires_counterexample_check_later=True,
        requires_reviewed_concept_gate_later=True,
        requires_memory_write_gate_later=True,
        learning_feedback_approved=False,
        learning_feedback_applied=False,
        concept_candidate_created=False,
        reviewed_concept_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        candidate_ordering_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_created=False,
        execution_created=False,
        task_behavior_changed=False,
        source_trace_refs=_combined_trace_refs(
            candidate_record.source_trace_refs,
            packet_record.source_trace_refs if packet_record else (),
            audit_record.source_trace_refs if audit_record else (),
        ),
    )


def validate_learning_feedback_teacher_review_record(
    review: LearningFeedbackTeacherReviewRecord | dict[str, object],
) -> dict[str, object]:
    record = _review_record(review)
    errors: list[str] = []
    if not record.learning_feedback_teacher_review_id:
        errors.append("missing_learning_feedback_teacher_review_id")
    if record.teacher_review_status not in ALLOWED_TEACHER_REVIEW_STATUSES:
        errors.append("invalid_teacher_review_status")
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
    if record.approved_for_concept_candidate_draft != (
        record.teacher_review_status == "approved_for_concept_candidate_draft"
    ):
        errors.append("approval_flag_does_not_match_review_status")
    if _review_forbidden_authority(record):
        errors.append("forbidden_authority_detected")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "learning_feedback_teacher_review_id": record.learning_feedback_teacher_review_id,
        "teacher_review_status": record.teacher_review_status,
    }


def build_learning_feedback_teacher_review_set(
    *,
    reviews: tuple[LearningFeedbackTeacherReviewRecord | dict[str, object], ...],
    candidate_set: LearningFeedbackCandidateSet | dict[str, object] | None = None,
    created_at: str | None = None,
) -> LearningFeedbackTeacherReviewSet:
    review_records = tuple(_review_record(review) for review in reviews)
    candidate_set_record = _candidate_set_record(candidate_set)
    approved = tuple(
        review.source_learning_feedback_candidate_id
        for review in review_records
        if review.teacher_review_status == "approved_for_concept_candidate_draft"
    )
    held = tuple(
        review.source_learning_feedback_candidate_id
        for review in review_records
        if review.teacher_review_status == "held_for_more_evidence"
    )
    rejected = tuple(
        review.source_learning_feedback_candidate_id
        for review in review_records
        if review.teacher_review_status == "rejected"
    )
    needs_more = tuple(
        review.source_learning_feedback_candidate_id
        for review in review_records
        if review.teacher_review_status == "needs_more_evidence"
    )
    conflicts = tuple(
        review.source_learning_feedback_candidate_id
        for review in review_records
        if review.teacher_review_status == "conflict_detected"
    )
    blocked = tuple(
        review.source_learning_feedback_candidate_id
        for review in review_records
        if review.teacher_review_status.startswith("blocked_")
    )
    if any(_review_forbidden_authority(review) for review in review_records):
        set_status = "blocked_forbidden_authority_detected"
    elif any(not validate_learning_feedback_teacher_review_record(review)["valid"] for review in review_records):
        set_status = "blocked_invalid_review_records"
    elif approved:
        set_status = "review_set_created_with_approved_feedback"
    elif conflicts:
        set_status = "conflict_detected"
    elif needs_more:
        set_status = "needs_more_evidence"
    else:
        set_status = "review_set_created_all_held_or_rejected"
    trace_refs = _combined_trace_refs(
        *(review.source_trace_refs for review in review_records),
        candidate_set_record.source_trace_refs if candidate_set_record else (),
    )
    return LearningFeedbackTeacherReviewSet(
        learning_feedback_teacher_review_set_id=_teacher_review_set_id(
            tuple(review.learning_feedback_teacher_review_id for review in review_records)
        ),
        schema_version=TEACHER_REVIEW_SET_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_learning_feedback_candidate_set_id=(
            candidate_set_record.learning_feedback_candidate_set_id if candidate_set_record else None
        ),
        candidate_review_records=review_records,
        approved_candidate_ids=approved,
        held_candidate_ids=held,
        rejected_candidate_ids=rejected,
        needs_more_evidence_candidate_ids=needs_more,
        conflict_detected_candidate_ids=conflicts,
        review_count=len(review_records),
        approved_count=len(approved),
        held_count=len(held) + len(needs_more),
        rejected_count=len(rejected),
        blocked_count=len(blocked) + len(conflicts),
        set_review_status=set_status,
        set_review_summary=_set_review_summary(set_status, len(approved), len(review_records)),
        has_approved_feedback_for_concept_candidate_draft=bool(approved),
        reviewed_concept_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        task_behavior_changed=False,
        source_trace_refs=trace_refs,
    )


def validate_learning_feedback_teacher_review_set(
    review_set: LearningFeedbackTeacherReviewSet | dict[str, object],
) -> dict[str, object]:
    record = _review_set_record(review_set)
    errors: list[str] = []
    if not record.learning_feedback_teacher_review_set_id:
        errors.append("missing_learning_feedback_teacher_review_set_id")
    if record.review_count != len(record.candidate_review_records):
        errors.append("review_count_mismatch")
    if record.approved_count != len(record.approved_candidate_ids):
        errors.append("approved_count_mismatch")
    if any(
        not validate_learning_feedback_teacher_review_record(review)["valid"]
        for review in record.candidate_review_records
    ):
        errors.append("invalid_review_record")
    if record.has_approved_feedback_for_concept_candidate_draft != bool(record.approved_candidate_ids):
        errors.append("approved_set_flag_mismatch")
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
        "learning_feedback_teacher_review_set_id": record.learning_feedback_teacher_review_set_id,
        "set_review_status": record.set_review_status,
    }


def map_learning_feedback_to_concept_candidate_kind(
    feedback_candidate_kind: str,
    learning_signal_class: str,
) -> tuple[str, str, str]:
    mapping = {
        "successful_expected_effect_candidate": (
            "positive_affordance_concept_candidate",
            "normal",
            "positive_affordance_from_expected_effect",
        ),
        "failed_expected_effect_candidate": (
            "negative_affordance_concept_candidate",
            "normal",
            "failed_affordance_from_expected_effect",
        ),
        "goal_reached_candidate": (
            "goal_completion_concept_candidate",
            "high",
            "goal_completion_from_action_outcome",
        ),
        "no_progress_candidate": (
            "no_progress_concept_candidate",
            "low",
            "no_progress_from_action_outcome",
        ),
        "observation_only_candidate": (
            "observation_context_concept_candidate",
            "low",
            "observation_context_from_sense_handoff",
        ),
        "unknown_outcome_candidate": (
            "unknown_outcome_concept_candidate",
            "blocked",
            "unknown_outcome_requires_more_evidence",
        ),
        "system_fault_candidate": (
            "system_fault_diagnostic_candidate",
            "blocked",
            "system_fault_requires_diagnostic_review",
        ),
    }
    if feedback_candidate_kind not in mapping:
        return (
            "unknown_outcome_concept_candidate",
            "blocked",
            "unknown_feedback_candidate_kind",
        )
    return mapping[feedback_candidate_kind]


def build_learning_feedback_to_concept_candidate_draft_record(
    *,
    candidate: LearningFeedbackCandidateRecord | dict[str, object],
    evidence_packet: LearningFeedbackCandidateEvidencePacket | dict[str, object] | None,
    teacher_review: LearningFeedbackTeacherReviewRecord | dict[str, object] | None,
    teacher_review_set: LearningFeedbackTeacherReviewSet | dict[str, object] | None = None,
    created_at: str | None = None,
) -> LearningFeedbackToConceptCandidateDraftRecord:
    candidate_record = _candidate_record(candidate)
    packet_record = _packet_record(evidence_packet)
    review_record = _review_record(teacher_review) if teacher_review is not None else None
    review_set_record = _review_set_record(teacher_review_set)
    concept_kind, confidence, label = map_learning_feedback_to_concept_candidate_kind(
        candidate_record.feedback_candidate_kind,
        candidate_record.learning_signal_class,
    )
    status = _draft_status(candidate_record, packet_record, review_record)
    draft_created = status == "concept_candidate_draft_created"
    draft_id = f"learning_feedback_concept_candidate_draft:{candidate_record.learning_feedback_candidate_id}"
    rollback_id = f"learning_feedback_concept_candidate_rollback:{draft_id}" if draft_created else None
    return LearningFeedbackToConceptCandidateDraftRecord(
        concept_candidate_draft_id=draft_id,
        schema_version=DRAFT_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_learning_feedback_candidate_id=candidate_record.learning_feedback_candidate_id,
        source_learning_feedback_evidence_packet_id=(
            packet_record.learning_feedback_evidence_packet_id if packet_record else None
        ),
        source_learning_feedback_teacher_review_id=(
            review_record.learning_feedback_teacher_review_id if review_record else ""
        ),
        source_learning_feedback_teacher_review_set_id=(
            review_set_record.learning_feedback_teacher_review_set_id if review_set_record else None
        ),
        source_task_closure_id=candidate_record.source_task_closure_id,
        source_outcome_evaluation_id=candidate_record.source_outcome_evaluation_id,
        source_goal_delta_evaluation_id=candidate_record.source_goal_delta_evaluation_id,
        source_expected_effect_reference_id=candidate_record.source_expected_effect_reference_id,
        source_sense_handoff_id=candidate_record.source_sense_handoff_id,
        source_sandbox_execution_id=candidate_record.source_sandbox_execution_id,
        direct_command=candidate_record.direct_command,
        expected_effect=candidate_record.expected_effect,
        outcome_class=candidate_record.outcome_class,
        goal_delta_class=candidate_record.goal_delta_class,
        closure_status=candidate_record.closure_status,
        feedback_candidate_kind=candidate_record.feedback_candidate_kind,
        learning_signal_class=candidate_record.learning_signal_class,
        concept_candidate_kind=concept_kind,
        concept_candidate_status=status,
        concept_candidate_confidence=confidence if draft_created else "blocked",
        concept_candidate_summary=_draft_summary(status, candidate_record, label),
        concept_candidate_reason=_draft_reason(status, candidate_record),
        proposed_concept_label=label,
        proposed_concept_scope=_proposed_scope(candidate_record),
        proposed_support_evidence_refs=_support_refs(candidate_record, packet_record),
        proposed_counterexample_refs=(),
        proposed_counterexample_notes=candidate_record.counterexample_relevance_notes,
        requires_teacher_review_before_concept_acceptance=True,
        requires_counterexample_check_later=True,
        requires_refinement_later=True,
        requires_reviewed_concept_gate_later=True,
        requires_memory_write_gate_later=True,
        actual_existing_concept_candidate_created=False,
        reviewed_concept_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        candidate_ordering_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_created=False,
        execution_created=False,
        task_behavior_changed=False,
        rollback_available=draft_created,
        rollback_record_id=rollback_id,
        source_trace_refs=_combined_trace_refs(
            candidate_record.source_trace_refs,
            packet_record.source_trace_refs if packet_record else (),
            review_record.source_trace_refs if review_record else (),
            review_set_record.source_trace_refs if review_set_record else (),
        ),
    )


def validate_learning_feedback_to_concept_candidate_draft_record(
    draft: LearningFeedbackToConceptCandidateDraftRecord | dict[str, object],
) -> dict[str, object]:
    record = _draft_record(draft)
    errors: list[str] = []
    if not record.concept_candidate_draft_id:
        errors.append("missing_concept_candidate_draft_id")
    if record.concept_candidate_status not in ALLOWED_CONCEPT_CANDIDATE_STATUSES:
        errors.append("invalid_concept_candidate_status")
    if record.concept_candidate_status == "concept_candidate_draft_created":
        if not record.rollback_available or not record.rollback_record_id:
            errors.append("successful_draft_requires_rollback_record")
        if record.concept_candidate_confidence == "blocked":
            errors.append("successful_draft_confidence_blocked")
    if _draft_forbidden_authority(record):
        errors.append("forbidden_authority_detected")
    if not record.requires_teacher_review_before_concept_acceptance:
        errors.append("must_require_teacher_review_before_concept_acceptance")
    if not record.requires_counterexample_check_later:
        errors.append("must_require_counterexample_check_later")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "concept_candidate_draft_id": record.concept_candidate_draft_id,
        "concept_candidate_status": record.concept_candidate_status,
    }


def build_learning_feedback_to_concept_candidate_rollback_record(
    *,
    draft: LearningFeedbackToConceptCandidateDraftRecord | dict[str, object],
    rollback_reason: str = "Rollback data prepared to withdraw draft availability.",
    created_at: str | None = None,
) -> LearningFeedbackToConceptCandidateRollbackRecord:
    draft_record = _draft_record(draft)
    valid = validate_learning_feedback_to_concept_candidate_draft_record(draft_record)["valid"]
    created = draft_record.concept_candidate_status == "concept_candidate_draft_created"
    status = (
        "rollback_record_created"
        if valid and created and not _draft_forbidden_authority(draft_record)
        else "blocked_invalid_concept_candidate_draft"
    )
    if _draft_forbidden_authority(draft_record):
        status = "blocked_forbidden_authority_detected"
    return LearningFeedbackToConceptCandidateRollbackRecord(
        concept_candidate_rollback_id=(
            draft_record.rollback_record_id
            or f"learning_feedback_concept_candidate_rollback:{draft_record.concept_candidate_draft_id}"
        ),
        schema_version=ROLLBACK_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_draft_id=draft_record.concept_candidate_draft_id,
        source_learning_feedback_candidate_id=draft_record.source_learning_feedback_candidate_id,
        concept_candidate_draft_created_before_rollback=created,
        concept_candidate_draft_available_after_rollback=created,
        rollback_available=True,
        rollback_applied=False,
        rollback_reason=rollback_reason,
        rollback_status=status,
        rollback_summary=_rollback_summary(status, draft_record),
        reviewed_concept_created=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        task_behavior_changed=False,
        source_trace_refs=draft_record.source_trace_refs,
    )


def apply_learning_feedback_to_concept_candidate_rollback(
    rollback: LearningFeedbackToConceptCandidateRollbackRecord | dict[str, object],
) -> LearningFeedbackToConceptCandidateRollbackRecord:
    record = _rollback_record(rollback)
    if record.rollback_status != "rollback_record_created":
        return record
    return replace(
        record,
        concept_candidate_draft_available_after_rollback=False,
        rollback_applied=True,
        rollback_status="rollback_applied_to_withdraw_concept_candidate_draft",
        rollback_summary="Concept candidate draft availability withdrawn; no memory or behavior changed.",
    )


def validate_learning_feedback_to_concept_candidate_rollback_record(
    rollback: LearningFeedbackToConceptCandidateRollbackRecord | dict[str, object],
) -> dict[str, object]:
    record = _rollback_record(rollback)
    errors: list[str] = []
    if not record.concept_candidate_rollback_id:
        errors.append("missing_concept_candidate_rollback_id")
    if record.rollback_status not in ALLOWED_ROLLBACK_STATUSES:
        errors.append("invalid_rollback_status")
    if not record.rollback_available:
        errors.append("rollback_must_be_available")
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
        "concept_candidate_rollback_id": record.concept_candidate_rollback_id,
        "rollback_status": record.rollback_status,
    }


def build_learning_feedback_to_concept_candidate_safety_audit(
    *,
    teacher_review_set: LearningFeedbackTeacherReviewSet | dict[str, object] | None,
    drafts: tuple[LearningFeedbackToConceptCandidateDraftRecord | dict[str, object], ...],
    rollbacks: tuple[LearningFeedbackToConceptCandidateRollbackRecord | dict[str, object], ...] = (),
    created_at: str | None = None,
) -> LearningFeedbackToConceptCandidateSafetyAudit:
    review_set_record = _review_set_record(teacher_review_set)
    draft_records = tuple(_draft_record(draft) for draft in drafts)
    rollback_records = tuple(_rollback_record(rollback) for rollback in rollbacks)
    blocked_reasons = _safety_blocked_reasons(review_set_record, draft_records, rollback_records)
    status = _safety_status(blocked_reasons, draft_records)
    return LearningFeedbackToConceptCandidateSafetyAudit(
        concept_candidate_safety_audit_id=_safety_audit_id(
            tuple(draft.concept_candidate_draft_id for draft in draft_records)
        ),
        schema_version=SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_learning_feedback_teacher_review_set_id=(
            review_set_record.learning_feedback_teacher_review_set_id if review_set_record else None
        ),
        source_concept_candidate_draft_ids=tuple(
            draft.concept_candidate_draft_id for draft in draft_records
        ),
        learning_feedback_candidate_valid="invalid_learning_feedback_candidate"
        not in blocked_reasons,
        evidence_packet_valid="invalid_learning_feedback_candidate" not in blocked_reasons,
        teacher_review_valid="invalid_teacher_review" not in blocked_reasons,
        concept_candidate_draft_valid="invalid_concept_candidate_draft" not in blocked_reasons,
        rollback_available="missing_rollback" not in blocked_reasons,
        concept_candidate_draft_only_confirmed=True,
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
        source_trace_refs=_combined_trace_refs(
            *(draft.source_trace_refs for draft in draft_records),
            *(rollback.source_trace_refs for rollback in rollback_records),
            review_set_record.source_trace_refs if review_set_record else (),
        ),
    )


def validate_learning_feedback_to_concept_candidate_safety_audit(
    audit: LearningFeedbackToConceptCandidateSafetyAudit | dict[str, object],
) -> dict[str, object]:
    record = _safety_audit_record(audit)
    errors: list[str] = []
    if not record.concept_candidate_safety_audit_id:
        errors.append("missing_concept_candidate_safety_audit_id")
    if record.audit_status not in ALLOWED_AUDIT_STATUSES:
        errors.append("invalid_audit_status")
    if record.audit_status.startswith("passed_") and record.blocked_reasons:
        errors.append("passing_audit_has_blocked_reasons")
    if not record.concept_candidate_draft_only_confirmed:
        errors.append("concept_candidate_draft_only_not_confirmed")
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
        "concept_candidate_safety_audit_id": record.concept_candidate_safety_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def build_demo_goal_reached_to_concept_candidate() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_goal_reached_learning_feedback_candidate(),
        "approved_for_concept_candidate_draft",
    )


def build_demo_successful_expected_effect_to_concept_candidate() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_progress_learning_feedback_candidate(),
        "approved_for_concept_candidate_draft",
    )


def build_demo_failed_expected_effect_to_concept_candidate() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_expected_effect_failed_learning_feedback_candidate(),
        "approved_for_concept_candidate_draft",
    )


def build_demo_no_progress_to_concept_candidate() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_no_progress_learning_feedback_candidate(),
        "approved_for_concept_candidate_draft",
    )


def build_demo_observation_only_to_concept_candidate() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_observation_only_learning_feedback_candidate(),
        "approved_for_concept_candidate_draft",
    )


def build_demo_unknown_outcome_held_feedback_review() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_unknown_outcome_learning_feedback_candidate(),
        "held_for_more_evidence",
    )


def build_demo_system_fault_blocked_feedback_review() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_system_fault_learning_feedback_candidate(),
        "conflict_detected",
    )


def build_demo_blocked_invalid_learning_feedback_to_concept_candidate() -> dict[str, object]:
    payload = build_demo_progress_learning_feedback_candidate()
    candidate = _candidate_record(payload["learning_feedback_candidate"])
    payload["learning_feedback_candidate"] = replace(
        candidate,
        requires_teacher_review_before_learning=False,
    ).to_dict()
    return _build_demo_bundle(payload, "approved_for_concept_candidate_draft")


def build_demo_blocked_invalid_feedback_safety_audit() -> dict[str, object]:
    payload = build_demo_progress_learning_feedback_candidate()
    audit = _candidate_audit_record(payload["learning_feedback_candidate_safety_audit"])
    payload["learning_feedback_candidate_safety_audit"] = replace(
        audit,
        audit_status="blocked_memory_write_detected",
        no_memory_write=False,
        blocked_reasons=("memory_write",),
    ).to_dict()
    return _build_demo_bundle(payload, "approved_for_concept_candidate_draft")


def build_demo_blocked_missing_teacher_review() -> dict[str, object]:
    payload = build_demo_progress_learning_feedback_candidate()
    candidate = _candidate_record(payload["learning_feedback_candidate"])
    packet = _packet_record(payload["learning_feedback_evidence_packet"])
    draft = build_learning_feedback_to_concept_candidate_draft_record(
        candidate=candidate,
        evidence_packet=packet,
        teacher_review=None,
    )
    audit = build_learning_feedback_to_concept_candidate_safety_audit(
        teacher_review_set=None,
        drafts=(draft,),
        rollbacks=(),
    )
    return _bundle_payload(payload, None, None, draft, None, audit)


def build_demo_blocked_teacher_rejected() -> dict[str, object]:
    return _build_demo_bundle(build_demo_progress_learning_feedback_candidate(), "rejected")


def build_demo_blocked_teacher_held() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_progress_learning_feedback_candidate(),
        "held_for_more_evidence",
    )


def build_demo_blocked_conflict_detected() -> dict[str, object]:
    return _build_demo_bundle(
        build_demo_progress_learning_feedback_candidate(),
        "conflict_detected",
    )


def build_demo_blocked_reviewed_concept_created() -> dict[str, object]:
    return _mutated_successful_demo(reviewed_concept_created=True)


def build_demo_blocked_memory_write() -> dict[str, object]:
    return _mutated_successful_demo(memory_write_performed=True)


def build_demo_blocked_automatic_learning_approval() -> dict[str, object]:
    return _mutated_successful_demo(automatic_learning_approval_created=True)


def build_demo_blocked_action_authority() -> dict[str, object]:
    return _mutated_successful_demo(selected_action_changed=True)


def build_demo_blocked_behavior_change() -> dict[str, object]:
    return _mutated_successful_demo(task_behavior_changed=True)


def build_demo_blocked_missing_rollback() -> dict[str, object]:
    payload = _build_demo_bundle(
        build_demo_progress_learning_feedback_candidate(),
        "approved_for_concept_candidate_draft",
    )
    review_set = _review_set_record(payload["learning_feedback_teacher_review_set"])
    draft = _draft_record(payload["learning_feedback_to_concept_candidate_draft"])
    audit = build_learning_feedback_to_concept_candidate_safety_audit(
        teacher_review_set=review_set,
        drafts=(draft,),
        rollbacks=(),
    )
    payload["learning_feedback_to_concept_candidate_rollback"] = None
    payload["learning_feedback_to_concept_candidate_safety_audit"] = audit.to_dict()
    return payload


def build_demo_learning_feedback_to_concept_candidate_case(case: str) -> dict[str, object]:
    cases = {
        "goal-reached": build_demo_goal_reached_to_concept_candidate,
        "successful-expected-effect": build_demo_successful_expected_effect_to_concept_candidate,
        "failed-expected-effect": build_demo_failed_expected_effect_to_concept_candidate,
        "no-progress": build_demo_no_progress_to_concept_candidate,
        "observation-only": build_demo_observation_only_to_concept_candidate,
        "unknown-outcome": build_demo_unknown_outcome_held_feedback_review,
        "system-fault": build_demo_system_fault_blocked_feedback_review,
    }
    if case not in cases:
        raise ValueError(f"unknown demo case: {case}")
    return cases[case]()


def build_demo_blocked_learning_feedback_to_concept_candidate(case: str) -> dict[str, object]:
    cases = {
        "invalid-learning-feedback-candidate": build_demo_blocked_invalid_learning_feedback_to_concept_candidate,
        "invalid-feedback-safety-audit": build_demo_blocked_invalid_feedback_safety_audit,
        "missing-teacher-review": build_demo_blocked_missing_teacher_review,
        "teacher-rejected": build_demo_blocked_teacher_rejected,
        "teacher-held": build_demo_blocked_teacher_held,
        "conflict-detected": build_demo_blocked_conflict_detected,
        "reviewed-concept-created": build_demo_blocked_reviewed_concept_created,
        "memory-write-detected": build_demo_blocked_memory_write,
        "automatic-learning-approval": build_demo_blocked_automatic_learning_approval,
        "action-authority-detected": build_demo_blocked_action_authority,
        "behavior-change-detected": build_demo_blocked_behavior_change,
        "missing-rollback": build_demo_blocked_missing_rollback,
    }
    if case not in cases:
        raise ValueError(f"unknown blocked demo case: {case}")
    return cases[case]()


def _build_demo_bundle(
    feedback_payload: dict[str, object],
    teacher_review_status: str,
) -> dict[str, object]:
    candidate = _candidate_record(feedback_payload["learning_feedback_candidate"])
    packet = _packet_record(feedback_payload["learning_feedback_evidence_packet"])
    feedback_audit = _candidate_audit_record(
        feedback_payload["learning_feedback_candidate_safety_audit"]
    )
    review = build_learning_feedback_teacher_review_record(
        candidate=candidate,
        evidence_packet=packet,
        candidate_safety_audit=feedback_audit,
        teacher_review_status=teacher_review_status,
    )
    review_set = build_learning_feedback_teacher_review_set(reviews=(review,))
    draft = build_learning_feedback_to_concept_candidate_draft_record(
        candidate=candidate,
        evidence_packet=packet,
        teacher_review=review,
        teacher_review_set=review_set,
    )
    rollback = (
        build_learning_feedback_to_concept_candidate_rollback_record(draft=draft)
        if draft.concept_candidate_status == "concept_candidate_draft_created"
        else None
    )
    audit = build_learning_feedback_to_concept_candidate_safety_audit(
        teacher_review_set=review_set,
        drafts=(draft,),
        rollbacks=(rollback,) if rollback is not None else (),
    )
    return _bundle_payload(feedback_payload, review, review_set, draft, rollback, audit)


def _bundle_payload(
    feedback_payload: dict[str, object],
    review: LearningFeedbackTeacherReviewRecord | None,
    review_set: LearningFeedbackTeacherReviewSet | None,
    draft: LearningFeedbackToConceptCandidateDraftRecord,
    rollback: LearningFeedbackToConceptCandidateRollbackRecord | None,
    audit: LearningFeedbackToConceptCandidateSafetyAudit,
) -> dict[str, object]:
    payload = dict(feedback_payload)
    payload.update(
        {
            "learning_feedback_teacher_review": review.to_dict() if review else None,
            "learning_feedback_teacher_review_set": review_set.to_dict()
            if review_set
            else None,
            "learning_feedback_to_concept_candidate_draft": draft.to_dict(),
            "learning_feedback_to_concept_candidate_rollback": rollback.to_dict()
            if rollback
            else None,
            "learning_feedback_to_concept_candidate_safety_audit": audit.to_dict(),
        }
    )
    return payload


def _mutated_successful_demo(**changes: object) -> dict[str, object]:
    payload = _build_demo_bundle(
        build_demo_progress_learning_feedback_candidate(),
        "approved_for_concept_candidate_draft",
    )
    review_set = _review_set_record(payload["learning_feedback_teacher_review_set"])
    draft = replace(_draft_record(payload["learning_feedback_to_concept_candidate_draft"]), **changes)
    rollback = _rollback_record(payload["learning_feedback_to_concept_candidate_rollback"])
    audit = build_learning_feedback_to_concept_candidate_safety_audit(
        teacher_review_set=review_set,
        drafts=(draft,),
        rollbacks=(rollback,),
    )
    payload["learning_feedback_to_concept_candidate_draft"] = draft.to_dict()
    payload["learning_feedback_to_concept_candidate_safety_audit"] = audit.to_dict()
    return payload


def _draft_status(
    candidate: LearningFeedbackCandidateRecord,
    packet: LearningFeedbackCandidateEvidencePacket | None,
    review: LearningFeedbackTeacherReviewRecord | None,
) -> str:
    if _forbidden_feedback_candidate_authority(candidate):
        return "blocked_forbidden_authority_detected"
    if not validate_learning_feedback_candidate_record(candidate)["valid"]:
        return "blocked_invalid_learning_feedback"
    if packet is not None and not validate_learning_feedback_candidate_evidence_packet(packet)["valid"]:
        return "blocked_invalid_learning_feedback"
    if review is None:
        return "blocked_invalid_teacher_review"
    if not validate_learning_feedback_teacher_review_record(review)["valid"]:
        return "blocked_invalid_teacher_review"
    if _review_forbidden_authority(review):
        return "blocked_forbidden_authority_detected"
    if review.teacher_review_status == "approved_for_concept_candidate_draft":
        if not _candidate_can_be_teacher_approved_for_draft(candidate):
            return "held_for_more_evidence"
        return "concept_candidate_draft_created"
    if review.teacher_review_status in {"held_for_more_evidence", "needs_more_evidence"}:
        return "held_for_more_evidence"
    if review.teacher_review_status == "rejected":
        return "rejected_by_teacher"
    if review.teacher_review_status == "conflict_detected":
        return "blocked_conflict_detected"
    if review.teacher_review_status in {
        "blocked_invalid_learning_feedback_candidate",
        "blocked_invalid_evidence_packet",
    }:
        return "blocked_invalid_learning_feedback"
    if review.teacher_review_status.startswith("blocked_"):
        return "blocked_invalid_teacher_review"
    return "blocked_invalid_teacher_review"


def _review_reason(status: str, candidate: LearningFeedbackCandidateRecord) -> str:
    if status == "approved_for_concept_candidate_draft":
        return f"{candidate.feedback_candidate_kind} is approved only for ConceptCandidate draft creation."
    if status == "held_for_more_evidence":
        return "More evidence is required before creating a ConceptCandidate draft."
    if status == "rejected":
        return "Teacher rejected this feedback for ConceptCandidate drafting."
    if status == "conflict_detected":
        return "Conflict detected; no ConceptCandidate draft may be created."
    return "Learning feedback cannot be reviewed for ConceptCandidate drafting."


def _set_review_summary(status: str, approved_count: int, review_count: int) -> str:
    if status == "review_set_created_with_approved_feedback":
        return f"{approved_count} of {review_count} feedback candidates approved for draft creation only."
    if status == "review_set_created_all_held_or_rejected":
        return "No feedback candidates approved for ConceptCandidate draft creation."
    return "Feedback review set blocked or requires more evidence."


def _draft_summary(
    status: str,
    candidate: LearningFeedbackCandidateRecord,
    label: str,
) -> str:
    if status == "concept_candidate_draft_created":
        return (
            f"{candidate.direct_command or 'observed action'} with outcome "
            f"{candidate.outcome_class} drafted as {label}."
        )
    if status == "held_for_more_evidence":
        return "Feedback held for more evidence; no ConceptCandidate draft created."
    if status == "rejected_by_teacher":
        return "Teacher rejected feedback; no ConceptCandidate draft created."
    if status == "blocked_conflict_detected":
        return "Conflict detected; ConceptCandidate draft blocked."
    return "ConceptCandidate draft blocked."


def _draft_reason(status: str, candidate: LearningFeedbackCandidateRecord) -> str:
    if status == "concept_candidate_draft_created":
        return (
            f"Teacher gate approved {candidate.feedback_candidate_kind} for draft creation only; "
            "ReviewedConcept and memory gates remain closed."
        )
    if status == "held_for_more_evidence":
        return "Evidence is insufficient for a review-ready ConceptCandidate draft."
    if status == "rejected_by_teacher":
        return "Teacher review rejected the feedback candidate."
    if status == "blocked_conflict_detected":
        return "Teacher review marked a conflict."
    return "Required feedback or teacher review boundary failed."


def _proposed_scope(candidate: LearningFeedbackCandidateRecord) -> str:
    if candidate.direct_command and candidate.expected_effect:
        return (
            f"single task-closure case where direct_command={candidate.direct_command} "
            f"and expected_effect={candidate.expected_effect}"
        )
    return "single task-closure observation context only"


def _support_refs(
    candidate: LearningFeedbackCandidateRecord,
    packet: LearningFeedbackCandidateEvidencePacket | None,
) -> tuple[str, ...]:
    refs = [
        candidate.source_task_closure_id,
        candidate.source_outcome_evaluation_id,
        candidate.source_goal_delta_evaluation_id,
        candidate.source_expected_effect_reference_id,
        candidate.source_sense_handoff_id,
        candidate.source_sandbox_execution_id,
    ]
    if packet is not None:
        refs.append(packet.learning_feedback_evidence_packet_id)
    return tuple(ref for ref in refs if ref)


def _rollback_summary(
    status: str,
    draft: LearningFeedbackToConceptCandidateDraftRecord,
) -> str:
    if status == "rollback_record_created":
        return f"Rollback can withdraw draft {draft.concept_candidate_draft_id} availability."
    if status == "blocked_forbidden_authority_detected":
        return "Rollback blocked because draft contains forbidden authority."
    return "Rollback blocked because ConceptCandidate draft is invalid or not created."


def _safety_blocked_reasons(
    review_set: LearningFeedbackTeacherReviewSet | None,
    drafts: tuple[LearningFeedbackToConceptCandidateDraftRecord, ...],
    rollbacks: tuple[LearningFeedbackToConceptCandidateRollbackRecord, ...],
) -> list[str]:
    reasons: list[str] = []
    if review_set is not None and not validate_learning_feedback_teacher_review_set(review_set)["valid"]:
        reasons.append("invalid_teacher_review")
    rollback_ids = {rollback.source_concept_candidate_draft_id for rollback in rollbacks}
    for draft in drafts:
        validation = validate_learning_feedback_to_concept_candidate_draft_record(draft)
        if not validation["valid"]:
            if draft.concept_candidate_status == "blocked_invalid_learning_feedback":
                reasons.append("invalid_learning_feedback_candidate")
            elif draft.concept_candidate_status == "blocked_invalid_teacher_review":
                reasons.append("invalid_teacher_review")
            elif draft.concept_candidate_status == "blocked_forbidden_authority_detected":
                reasons.append("action_authority")
            elif "forbidden_authority_detected" in validation["error_codes"]:
                pass
            else:
                reasons.append("invalid_concept_candidate_draft")
        elif draft.concept_candidate_status == "blocked_invalid_learning_feedback":
            reasons.append("invalid_learning_feedback_candidate")
        elif draft.concept_candidate_status == "blocked_invalid_teacher_review":
            reasons.append("invalid_teacher_review")
        elif draft.concept_candidate_status == "blocked_forbidden_authority_detected":
            reasons.append("action_authority")
        if (
            draft.concept_candidate_status == "concept_candidate_draft_created"
            and draft.concept_candidate_draft_id not in rollback_ids
        ):
            reasons.append("missing_rollback")
        if draft.reviewed_concept_created:
            reasons.append("reviewed_concept_created")
        if draft.memory_write_performed:
            reasons.append("memory_write")
        if draft.automatic_learning_approval_created:
            reasons.append("automatic_learning_approval")
        if (
            draft.candidate_ordering_changed
            or draft.selected_action_changed
            or draft.final_action_changed
            or draft.direct_command_created
            or draft.execution_created
        ):
            reasons.append("action_authority")
        if draft.task_behavior_changed:
            reasons.append("behavior_change")
    for rollback in rollbacks:
        if not validate_learning_feedback_to_concept_candidate_rollback_record(rollback)["valid"]:
            reasons.append("missing_rollback")
        if (
            rollback.reviewed_concept_created
            or rollback.memory_write_performed
            or rollback.automatic_learning_approval_created
        ):
            reasons.append("memory_write")
        if rollback.task_behavior_changed:
            reasons.append("behavior_change")
    return tuple(dict.fromkeys(reasons))  # type: ignore[return-value]


def _safety_status(
    blocked_reasons: list[str],
    drafts: tuple[LearningFeedbackToConceptCandidateDraftRecord, ...],
) -> str:
    if "reviewed_concept_created" in blocked_reasons:
        return "blocked_reviewed_concept_creation_detected"
    if "memory_write" in blocked_reasons:
        return "blocked_memory_write_detected"
    if "automatic_learning_approval" in blocked_reasons:
        return "blocked_automatic_learning_approval_detected"
    if "action_authority" in blocked_reasons:
        return "blocked_action_authority_detected"
    if "behavior_change" in blocked_reasons:
        return "blocked_behavior_change_detected"
    if "missing_rollback" in blocked_reasons:
        return "blocked_missing_rollback"
    if "invalid_teacher_review" in blocked_reasons:
        return "blocked_invalid_teacher_review"
    if "invalid_learning_feedback_candidate" in blocked_reasons:
        return "blocked_invalid_learning_feedback_candidate"
    if "invalid_concept_candidate_draft" in blocked_reasons:
        return "blocked_invalid_concept_candidate_draft"
    if any(draft.concept_candidate_status == "concept_candidate_draft_created" for draft in drafts):
        return "passed_concept_candidate_draft_only"
    return "passed_no_concept_candidate_created"


def _forbidden_feedback_candidate_authority(candidate: LearningFeedbackCandidateRecord) -> bool:
    return (
        candidate.learning_feedback_approved
        or candidate.learning_feedback_applied
        or candidate.concept_candidate_created
        or candidate.reviewed_concept_created
        or candidate.memory_write_performed
        or candidate.automatic_learning_approval_created
        or candidate.candidate_ordering_changed
        or candidate.selected_action_changed
        or candidate.final_action_changed
        or candidate.direct_command_created
        or candidate.execution_created
        or candidate.task_behavior_changed
    )


def _review_forbidden_authority(review: LearningFeedbackTeacherReviewRecord) -> bool:
    return (
        review.approved_for_reviewed_concept
        or review.approved_for_memory_write
        or review.approved_for_behavior_change
        or review.approved_for_action_authority
        or review.approved_for_automatic_learning_approval
        or review.learning_feedback_approved
        or review.learning_feedback_applied
        or review.concept_candidate_created
        or review.reviewed_concept_created
        or review.memory_write_performed
        or review.automatic_learning_approval_created
        or review.candidate_ordering_changed
        or review.selected_action_changed
        or review.final_action_changed
        or review.direct_command_created
        or review.execution_created
        or review.task_behavior_changed
    )


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


def _feedback_audit_passed(audit: LearningFeedbackCandidateSafetyAudit) -> bool:
    validation = validate_learning_feedback_candidate_safety_audit(audit)
    return validation["valid"] is True and audit.audit_status in PASSING_FEEDBACK_AUDIT_STATUSES


def _candidate_can_be_teacher_approved_for_draft(
    candidate: LearningFeedbackCandidateRecord,
) -> bool:
    return (
        candidate.available_for_teacher_review
        or candidate.feedback_candidate_kind == "observation_only_candidate"
    )


def _teacher_review_set_id(review_ids: tuple[str, ...]) -> str:
    if not review_ids:
        return "learning_feedback_teacher_review_set:empty"
    seed = review_ids[0].replace(":", "_")
    return f"learning_feedback_teacher_review_set:{len(review_ids)}:{seed}"


def _safety_audit_id(draft_ids: tuple[str, ...]) -> str:
    if not draft_ids:
        return "learning_feedback_to_concept_candidate_safety_audit:empty"
    return "learning_feedback_to_concept_candidate_safety_audit:" + draft_ids[0].replace(
        ":",
        "_",
    )


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    refs: list[str] = []
    for group in groups:
        for ref in group:
            if ref and ref not in refs:
                refs.append(ref)
    return tuple(refs)


def _candidate_record(
    candidate: LearningFeedbackCandidateRecord | dict[str, object],
) -> LearningFeedbackCandidateRecord:
    return (
        candidate
        if isinstance(candidate, LearningFeedbackCandidateRecord)
        else LearningFeedbackCandidateRecord.from_dict(dict(candidate))
    )


def _packet_record(
    packet: LearningFeedbackCandidateEvidencePacket | dict[str, object] | None,
) -> LearningFeedbackCandidateEvidencePacket | None:
    if packet is None:
        return None
    return (
        packet
        if isinstance(packet, LearningFeedbackCandidateEvidencePacket)
        else LearningFeedbackCandidateEvidencePacket.from_dict(dict(packet))
    )


def _candidate_audit_record(
    audit: LearningFeedbackCandidateSafetyAudit | dict[str, object] | None,
) -> LearningFeedbackCandidateSafetyAudit | None:
    if audit is None:
        return None
    return (
        audit
        if isinstance(audit, LearningFeedbackCandidateSafetyAudit)
        else LearningFeedbackCandidateSafetyAudit.from_dict(dict(audit))
    )


def _candidate_set_record(
    candidate_set: LearningFeedbackCandidateSet | dict[str, object] | None,
) -> LearningFeedbackCandidateSet | None:
    if candidate_set is None:
        return None
    return (
        candidate_set
        if isinstance(candidate_set, LearningFeedbackCandidateSet)
        else LearningFeedbackCandidateSet.from_dict(dict(candidate_set))
    )


def _review_record(
    review: LearningFeedbackTeacherReviewRecord | dict[str, object],
) -> LearningFeedbackTeacherReviewRecord:
    return (
        review
        if isinstance(review, LearningFeedbackTeacherReviewRecord)
        else LearningFeedbackTeacherReviewRecord.from_dict(dict(review))
    )


def _review_set_record(
    review_set: LearningFeedbackTeacherReviewSet | dict[str, object] | None,
) -> LearningFeedbackTeacherReviewSet | None:
    if review_set is None:
        return None
    return (
        review_set
        if isinstance(review_set, LearningFeedbackTeacherReviewSet)
        else LearningFeedbackTeacherReviewSet.from_dict(dict(review_set))
    )


def _draft_record(
    draft: LearningFeedbackToConceptCandidateDraftRecord | dict[str, object],
) -> LearningFeedbackToConceptCandidateDraftRecord:
    return (
        draft
        if isinstance(draft, LearningFeedbackToConceptCandidateDraftRecord)
        else LearningFeedbackToConceptCandidateDraftRecord.from_dict(dict(draft))
    )


def _rollback_record(
    rollback: LearningFeedbackToConceptCandidateRollbackRecord | dict[str, object],
) -> LearningFeedbackToConceptCandidateRollbackRecord:
    return (
        rollback
        if isinstance(rollback, LearningFeedbackToConceptCandidateRollbackRecord)
        else LearningFeedbackToConceptCandidateRollbackRecord.from_dict(dict(rollback))
    )


def _safety_audit_record(
    audit: LearningFeedbackToConceptCandidateSafetyAudit | dict[str, object],
) -> LearningFeedbackToConceptCandidateSafetyAudit:
    return (
        audit
        if isinstance(audit, LearningFeedbackToConceptCandidateSafetyAudit)
        else LearningFeedbackToConceptCandidateSafetyAudit.from_dict(dict(audit))
    )


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
