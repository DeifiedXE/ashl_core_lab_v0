"""Teacher review records for TaskWorkingMemoryReadbackHint application previews."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.task.reviewed_concept_readback_hint_application_preview import (
    TaskWorkingMemoryReadbackHintApplicationPreview,
    TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit,
    TaskWorkingMemoryReadbackHintApplicationPreviewSet,
    build_demo_task_working_memory_readback_hint_application_preview_set,
    validate_task_working_memory_readback_hint_application_preview,
    validate_task_working_memory_readback_hint_application_preview_safety_audit,
    validate_task_working_memory_readback_hint_application_preview_set,
)


SOURCE_ENGINE = "task_engine"
HINT_APPLICATION_TEACHER_REVIEW_SCHEMA_VERSION = (
    "task_engine_reviewed_concept_readback_hint_application_teacher_review_v0"
)
HINT_APPLICATION_PREVIEW_SET_TEACHER_REVIEW_SCHEMA_VERSION = (
    "task_engine_reviewed_concept_readback_hint_application_preview_set_teacher_review_v0"
)
HINT_APPLICATION_TEACHER_REVIEW_SAFETY_AUDIT_SCHEMA_VERSION = (
    "task_engine_reviewed_concept_readback_hint_application_teacher_review_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Task Engine can perform teacher review over "
    "TaskWorkingMemoryReadbackHint application previews and mark them approved, "
    "held, rejected, needing more evidence, or conflict-detected for future "
    "Working Memory application preparation, without applying hints, mutating "
    "Working Memory, changing task behavior, changing candidate ordering, "
    "selecting actions, executing actions, or writing memory layers."
)
BLOCKED_CLAIMS = (
    "no_active_readback_hint_application",
    "no_working_memory_mutation",
    "no_task_behavior_change",
    "no_candidate_ordering_change",
    "no_selected_action_change",
    "no_final_action_change",
    "no_direct_command_change",
    "no_action_execution",
    "no_core_longterm_archive_anchor_write",
    "no_automatic_learning_approval",
)

ALLOWED_TEACHER_REVIEW_STATUSES = {
    "approved_for_future_working_memory_application_preparation",
    "held_for_more_evidence",
    "rejected",
    "needs_more_evidence",
    "conflict_detected",
    "blocked_invalid_application_preview",
    "blocked_forbidden_authority_detected",
}
ALLOWED_REVIEW_ACTOR_ROLES = {"teacher", "project_owner", "system_demo"}
ALLOWED_REVIEW_SOURCES = {"explicit_teacher_review", "demo_review"}
ALLOWED_SET_REVIEW_STATUSES = {
    "reviewed_with_approved_application_previews",
    "reviewed_all_held_or_rejected",
    "needs_more_evidence",
    "conflict_detected",
    "blocked_invalid_application_preview_set",
    "blocked_invalid_application_reviews",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_application_preview_set",
    "blocked_invalid_application_reviews",
    "blocked_invalid_teacher_review_source",
    "blocked_invalid_approval_scope",
    "blocked_forbidden_active_hint_application_detected",
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
class TaskWorkingMemoryReadbackHintApplicationTeacherReview:
    hint_application_teacher_review_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_application_preview_id: str
    source_hint_application_preview_set_id: str
    source_hint_application_preview_safety_audit_id: str
    source_task_working_memory_readback_hint_id: str
    concept_label: str
    hint_label: str
    hint_kind: str
    hint_priority: int
    hint_summary: str
    proposed_working_memory_slot: str
    proposed_application_scope: str
    proposed_visibility: str
    proposed_lifetime: str
    task_handling_note: str
    scope_warning: str | None
    counterexample_warning: str | None
    teacher_review_status: str
    teacher_review_reason: str
    teacher_review_text: str
    review_actor: str
    review_actor_role: str
    review_source: str
    approved_for_future_working_memory_application_preparation: bool
    approved_for_active_hint_application: bool
    approved_for_working_memory_mutation: bool
    approved_for_candidate_ordering_change: bool
    approved_for_task_behavior_change: bool
    approved_for_selected_action_change: bool
    approved_for_final_action_change: bool
    approved_for_direct_command_change: bool
    approved_for_execution: bool
    approved_for_memory_layer_write: bool
    requires_next_stage_application_preparation_package: bool
    requires_teacher_review_before_active_application: bool
    requires_counterexample_monitoring: bool
    applied_to_working_memory: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HINT_APPLICATION_TEACHER_REVIEW_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be task_engine_reviewed_concept_readback_hint_application_teacher_review_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
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
    ) -> "TaskWorkingMemoryReadbackHintApplicationTeacherReview":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview:
    hint_application_preview_set_teacher_review_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_application_preview_set_id: str
    source_hint_application_preview_safety_audit_id: str
    source_task_working_memory_readback_hint_record_set_id: str
    concept_label: str
    preview_count: int
    preview_hint_labels: tuple[str, ...]
    application_preview_reviews: tuple[
        TaskWorkingMemoryReadbackHintApplicationTeacherReview,
        ...,
    ]
    approved_preview_ids: tuple[str, ...]
    held_preview_ids: tuple[str, ...]
    rejected_preview_ids: tuple[str, ...]
    needs_more_evidence_preview_ids: tuple[str, ...]
    conflict_detected_preview_ids: tuple[str, ...]
    set_review_status: str
    set_review_summary: str
    has_approved_previews_for_future_application_preparation: bool
    approved_for_active_hint_application: bool
    approved_for_working_memory_mutation: bool
    approved_for_candidate_ordering_change: bool
    approved_for_task_behavior_change: bool
    approved_for_selected_action_change: bool
    approved_for_final_action_change: bool
    approved_for_direct_command_change: bool
    approved_for_execution: bool
    applied_to_working_memory: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    candidate_ordering_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created: bool
    memory_layer_write_performed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.schema_version
            != HINT_APPLICATION_PREVIEW_SET_TEACHER_REVIEW_SCHEMA_VERSION
        ):
            raise ValueError(
                "schema_version must be task_engine_reviewed_concept_readback_hint_application_preview_set_teacher_review_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.set_review_status not in ALLOWED_SET_REVIEW_STATUSES:
            raise ValueError(f"unknown set_review_status: {self.set_review_status}")
        object.__setattr__(
            self,
            "application_preview_reviews",
            tuple(
                item
                if isinstance(item, TaskWorkingMemoryReadbackHintApplicationTeacherReview)
                else TaskWorkingMemoryReadbackHintApplicationTeacherReview.from_dict(
                    dict(item)
                )
                for item in self.application_preview_reviews
            ),
        )
        for name in (
            "preview_hint_labels",
            "approved_preview_ids",
            "held_preview_ids",
            "rejected_preview_ids",
            "needs_more_evidence_preview_ids",
            "conflict_detected_preview_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_application_preview_set_id: str | None
    source_hint_application_preview_set_teacher_review_id: str | None
    application_preview_set_valid: bool
    application_reviews_valid: bool
    teacher_review_source_valid: bool
    approval_scope_valid: bool
    no_active_hint_application: bool
    no_working_memory_mutation: bool
    no_task_behavior_change: bool
    no_candidate_ordering_change: bool
    no_selected_action_change: bool
    no_final_action_change: bool
    no_direct_command_change: bool
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
        if (
            self.schema_version
            != HINT_APPLICATION_TEACHER_REVIEW_SAFETY_AUDIT_SCHEMA_VERSION
        ):
            raise ValueError(
                "schema_version must be task_engine_reviewed_concept_readback_hint_application_teacher_review_safety_audit_v0"
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
    ) -> "TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit":
        return cls(**dict(data))


def build_task_working_memory_readback_hint_application_teacher_review(
    *,
    application_preview: TaskWorkingMemoryReadbackHintApplicationPreview | dict[str, object],
    application_preview_set: TaskWorkingMemoryReadbackHintApplicationPreviewSet
    | dict[str, object],
    application_preview_safety_audit: (
        TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit | dict[str, object]
    ),
    teacher_review_status: str,
    teacher_review_reason: str = "",
    teacher_review_text: str = "",
    review_actor: str = "system_demo",
    review_actor_role: str = "system_demo",
    review_source: str = "demo_review",
) -> TaskWorkingMemoryReadbackHintApplicationTeacherReview:
    preview = _application_preview(application_preview)
    preview_set = _application_preview_set(application_preview_set)
    preview_safety = _application_preview_safety_audit(
        application_preview_safety_audit
    )
    status = _review_status(preview, teacher_review_status)
    return TaskWorkingMemoryReadbackHintApplicationTeacherReview(
        hint_application_teacher_review_id=(
            "task_working_memory_readback_hint_application_teacher_review:"
            f"{preview.hint_application_preview_id}:{status}"
        ),
        schema_version=HINT_APPLICATION_TEACHER_REVIEW_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=preview.source_reviewed_concept_id,
        source_hint_application_preview_id=preview.hint_application_preview_id,
        source_hint_application_preview_set_id=(
            preview_set.hint_application_preview_set_id
        ),
        source_hint_application_preview_safety_audit_id=preview_safety.safety_audit_id,
        source_task_working_memory_readback_hint_id=(
            preview.source_task_working_memory_readback_hint_id
        ),
        concept_label=preview.concept_label,
        hint_label=preview.hint_label,
        hint_kind=preview.hint_kind,
        hint_priority=preview.hint_priority,
        hint_summary=preview.hint_summary,
        proposed_working_memory_slot=preview.proposed_working_memory_slot,
        proposed_application_scope=preview.proposed_application_scope,
        proposed_visibility=preview.proposed_visibility,
        proposed_lifetime=preview.proposed_lifetime,
        task_handling_note=preview.task_handling_note,
        scope_warning=preview.scope_warning,
        counterexample_warning=preview.counterexample_warning,
        teacher_review_status=status,
        teacher_review_reason=teacher_review_reason or _review_reason(status),
        teacher_review_text=teacher_review_text or _review_text(status, review_source),
        review_actor=review_actor,
        review_actor_role=review_actor_role,
        review_source=review_source,
        approved_for_future_working_memory_application_preparation=(
            status == "approved_for_future_working_memory_application_preparation"
        ),
        approved_for_active_hint_application=False,
        approved_for_working_memory_mutation=False,
        approved_for_candidate_ordering_change=False,
        approved_for_task_behavior_change=False,
        approved_for_selected_action_change=False,
        approved_for_final_action_change=False,
        approved_for_direct_command_change=False,
        approved_for_execution=False,
        approved_for_memory_layer_write=False,
        requires_next_stage_application_preparation_package=True,
        requires_teacher_review_before_active_application=True,
        requires_counterexample_monitoring=True,
        applied_to_working_memory=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        candidate_ordering_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_changed=False,
        execution_created=False,
        memory_layer_write_performed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=_combined_trace_refs(
            preview.source_trace_refs,
            preview_set.source_trace_refs,
            preview_safety.source_trace_refs,
        ),
    )


def validate_task_working_memory_readback_hint_application_teacher_review(
    review: TaskWorkingMemoryReadbackHintApplicationTeacherReview | dict[str, object],
) -> dict[str, object]:
    try:
        record = _application_review(review)
    except (TypeError, ValueError, KeyError) as error:
        return {
            "valid": False,
            "error_codes": [f"invalid_application_review:{error}"],
        }
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
        "requires_next_stage_application_preparation_package",
        "requires_teacher_review_before_active_application",
        "requires_counterexample_monitoring",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    for flag in (
        "applied_to_working_memory",
        "working_memory_mutated",
        "task_behavior_changed",
        "candidate_ordering_changed",
        "selected_action_changed",
        "final_action_changed",
        "direct_command_changed",
        "execution_created",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "hint_application_teacher_review_id": record.hint_application_teacher_review_id,
        "teacher_review_status": record.teacher_review_status,
        "source_hint_application_preview_id": record.source_hint_application_preview_id,
    }


def build_task_working_memory_readback_hint_application_preview_set_teacher_review(
    *,
    application_preview_set: TaskWorkingMemoryReadbackHintApplicationPreviewSet
    | dict[str, object],
    application_preview_safety_audit: (
        TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit | dict[str, object]
    ),
    review_decisions: dict[str, str] | None = None,
    review_actor: str = "system_demo",
    review_actor_role: str = "system_demo",
    review_source: str = "demo_review",
    teacher_review_text: str = "",
) -> TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview:
    preview_set = _application_preview_set(application_preview_set)
    preview_safety = _application_preview_safety_audit(application_preview_safety_audit)
    preview_set_valid = _source_preview_set_valid(preview_set, preview_safety)
    decisions = review_decisions or _demo_review_decisions(preview_set)
    preview_reviews = tuple(
        build_task_working_memory_readback_hint_application_teacher_review(
            application_preview=preview,
            application_preview_set=preview_set,
            application_preview_safety_audit=preview_safety,
            teacher_review_status=decisions.get(
                preview.hint_application_preview_id,
                decisions.get(preview.hint_label, "held_for_more_evidence"),
            ),
            teacher_review_reason=_decision_reason(
                decisions.get(
                    preview.hint_application_preview_id,
                    decisions.get(preview.hint_label, "held_for_more_evidence"),
                )
            ),
            teacher_review_text=teacher_review_text,
            review_actor=review_actor,
            review_actor_role=review_actor_role,
            review_source=review_source,
        )
        for preview in preview_set.application_previews
    )
    preview_reviews_valid = all(
        validate_task_working_memory_readback_hint_application_teacher_review(
            review
        )["valid"]
        for review in preview_reviews
    )
    status = _set_review_status(
        preview_set_valid=preview_set_valid,
        preview_reviews=preview_reviews,
        preview_reviews_valid=preview_reviews_valid,
    )
    approved_ids = tuple(
        review.source_hint_application_preview_id
        for review in preview_reviews
        if review.teacher_review_status
        == "approved_for_future_working_memory_application_preparation"
    )
    held_ids = tuple(
        review.source_hint_application_preview_id
        for review in preview_reviews
        if review.teacher_review_status == "held_for_more_evidence"
    )
    rejected_ids = tuple(
        review.source_hint_application_preview_id
        for review in preview_reviews
        if review.teacher_review_status == "rejected"
    )
    needs_more_ids = tuple(
        review.source_hint_application_preview_id
        for review in preview_reviews
        if review.teacher_review_status == "needs_more_evidence"
    )
    conflict_ids = tuple(
        review.source_hint_application_preview_id
        for review in preview_reviews
        if review.teacher_review_status == "conflict_detected"
    )
    preview_labels = tuple(preview.hint_label for preview in preview_set.application_previews)
    return TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview(
        hint_application_preview_set_teacher_review_id=(
            "task_working_memory_readback_hint_application_preview_set_teacher_review:"
            f"{preview_set.source_reviewed_concept_id}"
        ),
        schema_version=HINT_APPLICATION_PREVIEW_SET_TEACHER_REVIEW_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=preview_set.source_reviewed_concept_id,
        source_hint_application_preview_set_id=(
            preview_set.hint_application_preview_set_id
        ),
        source_hint_application_preview_safety_audit_id=preview_safety.safety_audit_id,
        source_task_working_memory_readback_hint_record_set_id=(
            preview_set.source_task_working_memory_readback_hint_record_set_id
        ),
        concept_label=preview_set.concept_label,
        preview_count=len(preview_set.application_previews),
        preview_hint_labels=preview_labels,
        application_preview_reviews=preview_reviews,
        approved_preview_ids=approved_ids,
        held_preview_ids=held_ids,
        rejected_preview_ids=rejected_ids,
        needs_more_evidence_preview_ids=needs_more_ids,
        conflict_detected_preview_ids=conflict_ids,
        set_review_status=status,
        set_review_summary=_set_review_summary(status),
        has_approved_previews_for_future_application_preparation=bool(approved_ids)
        and status == "reviewed_with_approved_application_previews",
        approved_for_active_hint_application=False,
        approved_for_working_memory_mutation=False,
        approved_for_candidate_ordering_change=False,
        approved_for_task_behavior_change=False,
        approved_for_selected_action_change=False,
        approved_for_final_action_change=False,
        approved_for_direct_command_change=False,
        approved_for_execution=False,
        applied_to_working_memory=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        candidate_ordering_changed=False,
        selected_action_changed=False,
        final_action_changed=False,
        direct_command_changed=False,
        execution_created=False,
        memory_layer_write_performed=False,
        source_trace_refs=_combined_trace_refs(
            preview_set.source_trace_refs,
            preview_safety.source_trace_refs,
            *(review.source_trace_refs for review in preview_reviews),
        ),
    )


def validate_task_working_memory_readback_hint_application_preview_set_teacher_review(
    review: TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview
    | dict[str, object],
) -> dict[str, object]:
    try:
        record = _application_set_review(review)
    except (TypeError, ValueError, KeyError) as error:
        return {
            "valid": False,
            "error_codes": [f"invalid_application_set_review:{error}"],
        }
    errors: list[str] = []
    if record.set_review_status.startswith("blocked_"):
        errors.append(record.set_review_status)
    if record.preview_count != len(record.application_preview_reviews):
        errors.append("application_review_count_mismatch")
    if record.preview_hint_labels != tuple(
        review_item.hint_label for review_item in record.application_preview_reviews
    ):
        errors.append("preview_hint_labels_mismatch")
    review_validations = [
        validate_task_working_memory_readback_hint_application_teacher_review(item)
        for item in record.application_preview_reviews
    ]
    if any(not validation["valid"] for validation in review_validations):
        errors.append("application_review_invalid")
    if record.has_approved_previews_for_future_application_preparation != bool(
        record.approved_preview_ids
    ):
        errors.append("approved_preview_flag_mismatch")
    if (
        record.approved_preview_ids
        and record.set_review_status
        != "reviewed_with_approved_application_previews"
    ):
        errors.append("approved_status_mismatch")
    if (
        not record.approved_preview_ids
        and record.set_review_status == "reviewed_with_approved_application_previews"
    ):
        errors.append("missing_approved_previews")
    for flag in (
        "approved_for_active_hint_application",
        "approved_for_working_memory_mutation",
        "approved_for_candidate_ordering_change",
        "approved_for_task_behavior_change",
        "approved_for_selected_action_change",
        "approved_for_final_action_change",
        "approved_for_direct_command_change",
        "approved_for_execution",
        "applied_to_working_memory",
        "working_memory_mutated",
        "task_behavior_changed",
        "candidate_ordering_changed",
        "selected_action_changed",
        "final_action_changed",
        "direct_command_changed",
        "execution_created",
        "memory_layer_write_performed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "hint_application_preview_set_teacher_review_id": (
            record.hint_application_preview_set_teacher_review_id
        ),
        "set_review_status": record.set_review_status,
        "approved_preview_ids": record.approved_preview_ids,
    }


def build_task_working_memory_readback_hint_application_teacher_review_safety_audit(
    *,
    application_preview_set: TaskWorkingMemoryReadbackHintApplicationPreviewSet
    | dict[str, object],
    application_preview_safety_audit: (
        TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit | dict[str, object]
    ),
    set_teacher_review: TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview
    | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit:
    preview_set = _application_preview_set(application_preview_set)
    preview_safety = _application_preview_safety_audit(application_preview_safety_audit)
    set_review = _application_set_review(set_teacher_review)
    application_preview_set_valid = _source_preview_set_valid(
        preview_set,
        preview_safety,
    )
    application_reviews_valid = bool(
        validate_task_working_memory_readback_hint_application_preview_set_teacher_review(
            set_review
        )["valid"]
    )
    teacher_review_source_valid = all(
        _teacher_review_source_valid(review)
        for review in set_review.application_preview_reviews
    )
    approval_scope_valid = _approval_scope_valid_for_set_review(set_review)
    no_active_hint_application = (
        set_review.applied_to_working_memory is False
        and all(
            review.applied_to_working_memory is False
            and review.approved_for_active_hint_application is False
            for review in set_review.application_preview_reviews
        )
    )
    no_working_memory_mutation = (
        set_review.working_memory_mutated is False
        and all(
            review.working_memory_mutated is False
            and review.approved_for_working_memory_mutation is False
            for review in set_review.application_preview_reviews
        )
    )
    no_task_behavior_change = (
        set_review.task_behavior_changed is False
        and all(
            review.task_behavior_changed is False
            and review.approved_for_task_behavior_change is False
            for review in set_review.application_preview_reviews
        )
    )
    no_candidate_ordering_change = (
        set_review.candidate_ordering_changed is False
        and all(
            review.candidate_ordering_changed is False
            and review.approved_for_candidate_ordering_change is False
            for review in set_review.application_preview_reviews
        )
    )
    no_selected_action_change = (
        set_review.selected_action_changed is False
        and all(
            review.selected_action_changed is False
            and review.approved_for_selected_action_change is False
            for review in set_review.application_preview_reviews
        )
    )
    no_final_action_change = (
        set_review.final_action_changed is False
        and all(
            review.final_action_changed is False
            and review.approved_for_final_action_change is False
            for review in set_review.application_preview_reviews
        )
    )
    no_direct_command_change = (
        set_review.direct_command_changed is False
        and all(
            review.direct_command_changed is False
            and review.approved_for_direct_command_change is False
            for review in set_review.application_preview_reviews
        )
    )
    no_action_execution = (
        set_review.execution_created is False
        and all(
            review.execution_created is False
            and review.approved_for_execution is False
            for review in set_review.application_preview_reviews
        )
    )
    no_memory_layer_write = (
        set_review.memory_layer_write_performed is False
        and all(
            review.memory_layer_write_performed is False
            and review.approved_for_memory_layer_write is False
            for review in set_review.application_preview_reviews
        )
    )
    no_automatic_learning_approval = all(
        review.automatic_learning_approval_created is False
        for review in set_review.application_preview_reviews
    )
    blocked_reasons = _safety_blocked_reasons(
        application_preview_set_valid=application_preview_set_valid,
        application_reviews_valid=application_reviews_valid,
        teacher_review_source_valid=teacher_review_source_valid,
        approval_scope_valid=approval_scope_valid,
        no_active_hint_application=no_active_hint_application,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_candidate_ordering_change=no_candidate_ordering_change,
        no_selected_action_change=no_selected_action_change,
        no_final_action_change=no_final_action_change,
        no_direct_command_change=no_direct_command_change,
        no_action_execution=no_action_execution,
        no_memory_layer_write=no_memory_layer_write,
        no_automatic_learning_approval=no_automatic_learning_approval,
    )
    return TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit(
        safety_audit_id=(
            "task_working_memory_readback_hint_application_teacher_review_safety_audit:"
            f"{preview_set.source_reviewed_concept_id}"
        ),
        schema_version=HINT_APPLICATION_TEACHER_REVIEW_SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=preview_set.source_reviewed_concept_id,
        source_hint_application_preview_set_id=(
            preview_set.hint_application_preview_set_id
        ),
        source_hint_application_preview_set_teacher_review_id=(
            set_review.hint_application_preview_set_teacher_review_id
        ),
        application_preview_set_valid=application_preview_set_valid,
        application_reviews_valid=application_reviews_valid,
        teacher_review_source_valid=teacher_review_source_valid,
        approval_scope_valid=approval_scope_valid,
        no_active_hint_application=no_active_hint_application,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_candidate_ordering_change=no_candidate_ordering_change,
        no_selected_action_change=no_selected_action_change,
        no_final_action_change=no_final_action_change,
        no_direct_command_change=no_direct_command_change,
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
            preview_set.source_trace_refs,
            preview_safety.source_trace_refs,
            set_review.source_trace_refs,
        ),
    )


def validate_task_working_memory_readback_hint_application_teacher_review_safety_audit(
    audit: TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit
    | dict[str, object],
) -> dict[str, object]:
    try:
        record = _safety_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed":
        errors.append(record.audit_status)
    for flag in (
        "application_preview_set_valid",
        "application_reviews_valid",
        "teacher_review_source_valid",
        "approval_scope_valid",
        "no_active_hint_application",
        "no_working_memory_mutation",
        "no_task_behavior_change",
        "no_candidate_ordering_change",
        "no_selected_action_change",
        "no_final_action_change",
        "no_direct_command_change",
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


def build_task_working_memory_readback_hint_application_teacher_review_bundle(
    application_preview_payload: dict[str, object],
    *,
    review_decisions: dict[str, str] | None = None,
    review_actor: str = "system_demo",
    review_actor_role: str = "system_demo",
    review_source: str = "demo_review",
    teacher_review_text: str = "",
) -> dict[str, object]:
    preview_set = _application_preview_set(
        application_preview_payload[
            "task_working_memory_readback_hint_application_preview_set"
        ]
    )
    preview_safety = _application_preview_safety_audit(
        application_preview_payload[
            "task_working_memory_readback_hint_application_preview_safety_audit"
        ]
    )
    set_review = build_task_working_memory_readback_hint_application_preview_set_teacher_review(
        application_preview_set=preview_set,
        application_preview_safety_audit=preview_safety,
        review_decisions=review_decisions,
        review_actor=review_actor,
        review_actor_role=review_actor_role,
        review_source=review_source,
        teacher_review_text=teacher_review_text,
    )
    safety = build_task_working_memory_readback_hint_application_teacher_review_safety_audit(
        application_preview_set=preview_set,
        application_preview_safety_audit=preview_safety,
        set_teacher_review=set_review,
    )
    return {
        "hint_application_teacher_reviews": [
            review.to_dict() for review in set_review.application_preview_reviews
        ],
        "hint_application_preview_set_teacher_review": set_review.to_dict(),
        "hint_application_teacher_review_safety_audit": safety.to_dict(),
        "hint_application_preview_set_teacher_review_validation": (
            validate_task_working_memory_readback_hint_application_preview_set_teacher_review(
                set_review
            )
        ),
        "hint_application_teacher_review_safety_audit_validation": (
            validate_task_working_memory_readback_hint_application_teacher_review_safety_audit(
                safety
            )
        ),
        "safe_claim": SAFE_CLAIM,
    }


def build_demo_task_working_memory_readback_hint_application_teacher_review() -> (
    dict[str, object]
):
    return build_task_working_memory_readback_hint_application_teacher_review_bundle(
        build_demo_task_working_memory_readback_hint_application_preview_set()
    )


def build_demo_task_working_memory_readback_hint_application_teacher_review_safety_audit() -> (
    TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit
):
    payload = build_demo_task_working_memory_readback_hint_application_teacher_review()
    return TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit.from_dict(
        payload["hint_application_teacher_review_safety_audit"]
    )


def build_demo_all_held_task_working_memory_readback_hint_application_teacher_review() -> (
    dict[str, object]
):
    payload = build_demo_task_working_memory_readback_hint_application_preview_set()
    labels = tuple(
        payload["task_working_memory_readback_hint_application_preview_set"][
            "ready_hint_labels"
        ]
    )
    all_labels = tuple(
        preview["hint_label"]
        for preview in payload[
            "task_working_memory_readback_hint_application_previews"
        ]
    )
    decisions = {label: "held_for_more_evidence" for label in (*labels, *all_labels)}
    return build_task_working_memory_readback_hint_application_teacher_review_bundle(
        payload,
        review_decisions=decisions,
    )


def build_demo_rejected_task_working_memory_readback_hint_application_teacher_review() -> (
    dict[str, object]
):
    payload = build_demo_task_working_memory_readback_hint_application_preview_set()
    decisions = {
        preview["hint_label"]: "rejected"
        for preview in payload[
            "task_working_memory_readback_hint_application_previews"
        ]
    }
    return build_task_working_memory_readback_hint_application_teacher_review_bundle(
        payload,
        review_decisions=decisions,
    )


def build_demo_conflict_detected_task_working_memory_readback_hint_application_teacher_review() -> (
    dict[str, object]
):
    payload = build_demo_task_working_memory_readback_hint_application_preview_set()
    labels = tuple(
        preview["hint_label"]
        for preview in payload[
            "task_working_memory_readback_hint_application_previews"
        ]
    )
    decisions = {label: "held_for_more_evidence" for label in labels}
    if labels:
        decisions[labels[0]] = "conflict_detected"
    return build_task_working_memory_readback_hint_application_teacher_review_bundle(
        payload,
        review_decisions=decisions,
    )


def build_demo_blocked_invalid_review_source() -> dict[str, object]:
    return build_task_working_memory_readback_hint_application_teacher_review_bundle(
        build_demo_task_working_memory_readback_hint_application_preview_set(),
        review_actor="teacher_demo",
        review_actor_role="teacher",
        review_source="demo_review",
    )


def build_demo_blocked_forbidden_authority_application_review() -> dict[str, object]:
    payload = build_demo_task_working_memory_readback_hint_application_teacher_review()
    set_review = TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview.from_dict(
        payload["hint_application_preview_set_teacher_review"]
    )
    reviews = list(set_review.application_preview_reviews)
    first = dict(reviews[0].to_dict())
    first["applied_to_working_memory"] = True
    reviews[0] = TaskWorkingMemoryReadbackHintApplicationTeacherReview.from_dict(first)
    set_review = TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview.from_dict(
        {
            **set_review.to_dict(),
            "application_preview_reviews": [review.to_dict() for review in reviews],
        }
    )
    preview_payload = build_demo_task_working_memory_readback_hint_application_preview_set()
    safety = build_task_working_memory_readback_hint_application_teacher_review_safety_audit(
        application_preview_set=preview_payload[
            "task_working_memory_readback_hint_application_preview_set"
        ],
        application_preview_safety_audit=preview_payload[
            "task_working_memory_readback_hint_application_preview_safety_audit"
        ],
        set_teacher_review=set_review,
    )
    return {
        **payload,
        "hint_application_teacher_reviews": [review.to_dict() for review in reviews],
        "hint_application_preview_set_teacher_review": set_review.to_dict(),
        "hint_application_preview_set_teacher_review_validation": (
            validate_task_working_memory_readback_hint_application_preview_set_teacher_review(
                set_review
            )
        ),
        "hint_application_teacher_review_safety_audit": safety.to_dict(),
        "hint_application_teacher_review_safety_audit_validation": (
            validate_task_working_memory_readback_hint_application_teacher_review_safety_audit(
                safety
            )
        ),
    }


def build_demo_blocked_task_working_memory_readback_hint_application_teacher_review(
    case: str,
) -> dict[str, object]:
    cases = {
        "invalid-review-source": build_demo_blocked_invalid_review_source,
        "forbidden-authority": build_demo_blocked_forbidden_authority_application_review,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked application teacher review case: {case}") from error


def _review_status(
    preview: TaskWorkingMemoryReadbackHintApplicationPreview,
    requested_status: str,
) -> str:
    if preview.preview_status == "blocked_forbidden_authority_detected":
        return "blocked_forbidden_authority_detected"
    if requested_status not in ALLOWED_TEACHER_REVIEW_STATUSES:
        return "blocked_invalid_application_preview"
    if preview.preview_status == "application_preview_ready":
        if not validate_task_working_memory_readback_hint_application_preview(preview)[
            "valid"
        ]:
            return "blocked_invalid_application_preview"
        return requested_status
    if preview.preview_status == "held_for_more_evidence":
        if requested_status in {
            "held_for_more_evidence",
            "rejected",
            "needs_more_evidence",
            "conflict_detected",
        }:
            return requested_status
        return "blocked_invalid_application_preview"
    return "blocked_invalid_application_preview"


def _review_reason(status: str) -> str:
    reasons = {
        "approved_for_future_working_memory_application_preparation": (
            "application preview is advisory-only and ready for future preparation"
        ),
        "held_for_more_evidence": "application preview should wait for more evidence or scope review",
        "rejected": "application preview should not proceed",
        "needs_more_evidence": "application preview needs more support before preparation",
        "conflict_detected": "application preview has a conflict that blocks future preparation",
    }
    return reasons.get(status, status)


def _decision_reason(status: str) -> str:
    return _review_reason(status)


def _review_text(status: str, review_source: str) -> str:
    if review_source == "demo_review":
        return f"Demo-only application review mark: {status}."
    return ""


def _demo_review_decisions(
    preview_set: TaskWorkingMemoryReadbackHintApplicationPreviewSet,
) -> dict[str, str]:
    decisions = {
        "observe_before_direct_retry": (
            "approved_for_future_working_memory_application_preparation"
        ),
        "avoid_same_failed_direct_retry": (
            "approved_for_future_working_memory_application_preparation"
        ),
        "verify_obstacle_type_before_generalizing": "held_for_more_evidence",
    }
    return {
        preview.hint_label: decisions.get(preview.hint_label, "held_for_more_evidence")
        for preview in preview_set.application_previews
    }


def _source_preview_set_valid(
    preview_set: TaskWorkingMemoryReadbackHintApplicationPreviewSet,
    preview_safety: TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit,
) -> bool:
    return (
        validate_task_working_memory_readback_hint_application_preview_set(
            preview_set
        )["valid"]
        and preview_set.preview_set_status == "preview_set_created_with_ready_previews"
        and preview_set.has_ready_previews_for_teacher_application_review is True
        and validate_task_working_memory_readback_hint_application_preview_safety_audit(
            preview_safety
        )["valid"]
    )


def _set_review_status(
    *,
    preview_set_valid: bool,
    preview_reviews: tuple[TaskWorkingMemoryReadbackHintApplicationTeacherReview, ...],
    preview_reviews_valid: bool,
) -> str:
    if not preview_set_valid:
        return "blocked_invalid_application_preview_set"
    if not preview_reviews_valid:
        return "blocked_invalid_application_reviews"
    if any(review.teacher_review_status == "conflict_detected" for review in preview_reviews):
        return "conflict_detected"
    if any(
        review.teacher_review_status
        == "approved_for_future_working_memory_application_preparation"
        for review in preview_reviews
    ):
        return "reviewed_with_approved_application_previews"
    if all(
        review.teacher_review_status
        in {"held_for_more_evidence", "rejected", "needs_more_evidence"}
        for review in preview_reviews
    ):
        return "reviewed_all_held_or_rejected"
    return "blocked_invalid_application_reviews"


def _set_review_summary(status: str) -> str:
    if status == "reviewed_with_approved_application_previews":
        return "Teacher review marked at least one application preview for future preparation."
    if status == "reviewed_all_held_or_rejected":
        return "Teacher review produced no future application preparation previews."
    if status == "conflict_detected":
        return "Teacher review found a conflict; no application preparation authority is created."
    return f"Application preview teacher review blocked: {status}."


def _approval_scope_valid_for_review(
    review: TaskWorkingMemoryReadbackHintApplicationTeacherReview,
) -> bool:
    if (
        review.teacher_review_status
        == "approved_for_future_working_memory_application_preparation"
    ):
        if review.approved_for_future_working_memory_application_preparation is not True:
            return False
    elif review.approved_for_future_working_memory_application_preparation is not False:
        return False
    return all(
        getattr(review, flag) is False
        for flag in (
            "approved_for_active_hint_application",
            "approved_for_working_memory_mutation",
            "approved_for_candidate_ordering_change",
            "approved_for_task_behavior_change",
            "approved_for_selected_action_change",
            "approved_for_final_action_change",
            "approved_for_direct_command_change",
            "approved_for_execution",
            "approved_for_memory_layer_write",
        )
    )


def _approval_scope_valid_for_set_review(
    review: TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview,
) -> bool:
    if any(
        getattr(review, flag) is not False
        for flag in (
            "approved_for_active_hint_application",
            "approved_for_working_memory_mutation",
            "approved_for_candidate_ordering_change",
            "approved_for_task_behavior_change",
            "approved_for_selected_action_change",
            "approved_for_final_action_change",
            "approved_for_direct_command_change",
            "approved_for_execution",
        )
    ):
        return False
    return all(
        _approval_scope_valid_for_review(application_review)
        for application_review in review.application_preview_reviews
    )


def _teacher_review_source_valid(
    review: TaskWorkingMemoryReadbackHintApplicationTeacherReview,
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
    application_preview_set_valid: bool,
    application_reviews_valid: bool,
    teacher_review_source_valid: bool,
    approval_scope_valid: bool,
    no_active_hint_application: bool,
    no_working_memory_mutation: bool,
    no_task_behavior_change: bool,
    no_candidate_ordering_change: bool,
    no_selected_action_change: bool,
    no_final_action_change: bool,
    no_direct_command_change: bool,
    no_action_execution: bool,
    no_memory_layer_write: bool,
    no_automatic_learning_approval: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not no_active_hint_application:
        reasons.append("blocked_forbidden_active_hint_application_detected")
    if not no_working_memory_mutation:
        reasons.append("blocked_forbidden_working_memory_mutation_detected")
    if not (no_task_behavior_change and no_candidate_ordering_change):
        reasons.append("blocked_forbidden_behavior_change_detected")
    if not (
        no_selected_action_change
        and no_final_action_change
        and no_direct_command_change
        and no_action_execution
    ):
        reasons.append("blocked_forbidden_action_authority_detected")
    if not (no_memory_layer_write and no_automatic_learning_approval):
        reasons.append("blocked_forbidden_memory_write_detected")
    if not application_preview_set_valid:
        reasons.append("blocked_invalid_application_preview_set")
    if not application_reviews_valid:
        reasons.append("blocked_invalid_application_reviews")
    if not teacher_review_source_valid:
        reasons.append("blocked_invalid_teacher_review_source")
    if not approval_scope_valid:
        reasons.append("blocked_invalid_approval_scope")
    return tuple(dict.fromkeys(reasons))


def _audit_status(blocked_reasons: tuple[str, ...]) -> str:
    if not blocked_reasons:
        return "passed"
    for status in (
        "blocked_forbidden_active_hint_application_detected",
        "blocked_forbidden_working_memory_mutation_detected",
        "blocked_forbidden_behavior_change_detected",
        "blocked_forbidden_action_authority_detected",
        "blocked_forbidden_memory_write_detected",
        "blocked_invalid_application_preview_set",
        "blocked_invalid_teacher_review_source",
        "blocked_invalid_approval_scope",
        "blocked_invalid_application_reviews",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_invalid_application_reviews"


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _application_preview(
    record: TaskWorkingMemoryReadbackHintApplicationPreview | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationPreview:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationPreview)
        else TaskWorkingMemoryReadbackHintApplicationPreview.from_dict(dict(record))
    )


def _application_preview_set(
    record: TaskWorkingMemoryReadbackHintApplicationPreviewSet | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationPreviewSet:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationPreviewSet)
        else TaskWorkingMemoryReadbackHintApplicationPreviewSet.from_dict(dict(record))
    )


def _application_preview_safety_audit(
    record: TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit
    | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit)
        else TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit.from_dict(
            dict(record)
        )
    )


def _application_review(
    record: TaskWorkingMemoryReadbackHintApplicationTeacherReview | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationTeacherReview:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationTeacherReview)
        else TaskWorkingMemoryReadbackHintApplicationTeacherReview.from_dict(dict(record))
    )


def _application_set_review(
    record: TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview
    | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview)
        else TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview.from_dict(
            dict(record)
        )
    )


def _safety_audit(
    record: TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit
    | dict[str, object],
) -> TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit:
    return (
        record
        if isinstance(record, TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit)
        else TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit.from_dict(
            dict(record)
        )
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
