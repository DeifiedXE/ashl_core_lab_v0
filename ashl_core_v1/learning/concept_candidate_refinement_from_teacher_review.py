"""Refine drafted ConceptCandidate records from teacher review decisions."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.concept_candidate_from_task_closure_draft import (
    ConceptCandidateDraftRecord,
    build_demo_draft,
)
from ashl_core_v1.learning.concept_candidate_schema import (
    BLOCKED_CLAIMS as CANDIDATE_BLOCKED_CLAIMS,
    SAFE_CLAIM as CANDIDATE_SAFE_CLAIM,
    SCHEMA_VERSION as CONCEPT_CANDIDATE_SCHEMA_VERSION,
    SOURCE_ENGINE,
    ConceptCandidate,
    ConceptScopeStatement,
    validate_concept_candidate,
)
from ashl_core_v1.learning.concept_candidate_teacher_review import (
    ConceptCandidateTeacherReviewDecision,
    ConceptCandidateTeacherReviewSummary,
    ConceptCandidateTeacherReviewTask,
    build_demo_needs_more_support_review,
    build_demo_rejected_review,
    build_demo_scope_narrowed_review,
    build_demo_split_required_review,
    build_demo_teacher_review_ready_review,
    validate_concept_candidate_teacher_review_decision,
    validate_concept_candidate_teacher_review_summary,
    validate_concept_candidate_teacher_review_task,
)


REFINEMENT_SCHEMA_VERSION = "learning_engine_concept_candidate_refinement_v0"
EVIDENCE_REQUEST_SCHEMA_VERSION = "learning_engine_concept_evidence_request_v0"
SCOPE_NARROWED_SCHEMA_VERSION = "learning_engine_scope_narrowed_concept_draft_v0"
SPLIT_DRAFT_SET_SCHEMA_VERSION = "learning_engine_split_concept_draft_set_v0"
STOP_SCHEMA_VERSION = "learning_engine_concept_candidate_stop_v0"
PREPARATION_MARKER_SCHEMA_VERSION = (
    "learning_engine_future_reviewed_concept_preparation_marker_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Learning Engine can transform teacher review decisions on "
    "drafted ConceptCandidate records into refinement outputs without "
    "approving concepts, writing memory, or changing task behavior."
)
BLOCKED_CLAIMS = (
    "no_reviewed_concept",
    "no_concept_approval",
    "no_memory_write",
    "no_task_behavior_change",
    "no_automatic_learning_approval",
    "no_core_longterm_archive_anchor_write",
)

REFINEMENT_KIND_BY_DECISION = {
    "needs_more_support": "more_support_request",
    "scope_narrowed": "scope_narrowed_draft",
    "split_required": "split_draft_set",
    "teacher_review_ready": "future_reviewed_concept_preparation",
    "rejected": "stopped_candidate",
}
ALLOWED_REFINEMENT_KINDS = set(REFINEMENT_KIND_BY_DECISION.values())
ALLOWED_REFINEMENT_STATUSES = {
    "refinement_created",
    "blocked_invalid_review_decision",
    "blocked_missing_teacher_decision",
    "blocked_missing_required_scope_change",
    "blocked_missing_required_split_labels",
    "blocked_missing_required_evidence_request",
    "blocked_unsupported_decision",
}
ALLOWED_EVIDENCE_REQUEST_STATUSES = {
    "request_created",
    "blocked_missing_teacher_note",
    "blocked_missing_requested_evidence",
}
ALLOWED_SCOPE_NARROWED_STATUSES = {
    "narrowed_draft_created",
    "blocked_missing_scope_change",
    "blocked_invalid_narrowed_candidate",
}
ALLOWED_SPLIT_STATUSES = {
    "split_drafts_created",
    "blocked_missing_split_labels",
    "blocked_invalid_split_candidate",
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
class ConceptCandidateRefinementRecord:
    refinement_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_draft_id: str
    source_concept_candidate_id: str
    source_review_task_id: str
    source_review_decision_id: str
    source_review_summary_id: str | None
    teacher_decision: str
    refinement_kind: str
    refinement_status: str
    refinement_summary: str
    evidence_request_id: str | None
    scope_narrowed_draft_id: str | None
    split_draft_set_id: str | None
    stop_record_id: str | None
    future_reviewed_concept_preparation_marker_id: str | None
    reviewed_concept_created: bool
    concept_approved: bool
    memory_write_performed: bool
    task_behavior_changed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REFINEMENT_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_concept_candidate_refinement_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.refinement_kind not in ALLOWED_REFINEMENT_KINDS:
            raise ValueError(f"unknown refinement_kind: {self.refinement_kind}")
        if self.refinement_status not in ALLOWED_REFINEMENT_STATUSES:
            raise ValueError(f"unknown refinement_status: {self.refinement_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ConceptCandidateRefinementRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ConceptEvidenceRequestRecord:
    evidence_request_id: str
    schema_version: str
    created_at: str
    source_refinement_id: str
    source_concept_candidate_id: str
    source_review_decision_id: str
    requested_evidence_kinds: tuple[str, ...]
    requested_case_kinds: tuple[str, ...]
    requested_state_action_outcome_patterns: tuple[str, ...]
    teacher_note: str
    request_status: str
    does_not_run_task: bool
    does_not_collect_evidence_automatically: bool
    does_not_write_memory: bool

    def __post_init__(self) -> None:
        if self.schema_version != EVIDENCE_REQUEST_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_concept_evidence_request_v0")
        if self.request_status not in ALLOWED_EVIDENCE_REQUEST_STATUSES:
            raise ValueError(f"unknown request_status: {self.request_status}")
        for name in (
            "requested_evidence_kinds",
            "requested_case_kinds",
            "requested_state_action_outcome_patterns",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ConceptEvidenceRequestRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ScopeNarrowedConceptDraftRecord:
    scope_narrowed_draft_id: str
    schema_version: str
    created_at: str
    source_refinement_id: str
    source_concept_candidate_id: str
    source_review_decision_id: str
    original_concept_label: str
    narrowed_concept_label: str
    original_scope_text: str
    narrowed_scope_text: str
    requested_scope_changes: tuple[str, ...]
    narrowed_concept_candidate: ConceptCandidate
    narrowed_status: str
    reviewed_concept_created: bool
    memory_write_performed: bool
    task_behavior_changed: bool

    def __post_init__(self) -> None:
        if self.schema_version != SCOPE_NARROWED_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_scope_narrowed_concept_draft_v0")
        if self.narrowed_status not in ALLOWED_SCOPE_NARROWED_STATUSES:
            raise ValueError(f"unknown narrowed_status: {self.narrowed_status}")
        object.__setattr__(
            self,
            "requested_scope_changes",
            _tuple_of_str("requested_scope_changes", self.requested_scope_changes),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ScopeNarrowedConceptDraftRecord":
        values = dict(data)
        if not isinstance(values.get("narrowed_concept_candidate"), ConceptCandidate):
            values["narrowed_concept_candidate"] = ConceptCandidate.from_dict(
                dict(values["narrowed_concept_candidate"])
            )
        return cls(**values)


@dataclass(frozen=True)
class SplitConceptDraftSetRecord:
    split_draft_set_id: str
    schema_version: str
    created_at: str
    source_refinement_id: str
    source_concept_candidate_id: str
    source_review_decision_id: str
    original_concept_label: str
    requested_split_labels: tuple[str, ...]
    split_concept_candidates: tuple[ConceptCandidate, ...]
    split_status: str
    reviewed_concept_created: bool
    memory_write_performed: bool
    task_behavior_changed: bool

    def __post_init__(self) -> None:
        if self.schema_version != SPLIT_DRAFT_SET_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_split_concept_draft_set_v0")
        if self.split_status not in ALLOWED_SPLIT_STATUSES:
            raise ValueError(f"unknown split_status: {self.split_status}")
        object.__setattr__(
            self,
            "requested_split_labels",
            _tuple_of_str("requested_split_labels", self.requested_split_labels),
        )
        object.__setattr__(
            self,
            "split_concept_candidates",
            tuple(self.split_concept_candidates),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SplitConceptDraftSetRecord":
        values = dict(data)
        values["split_concept_candidates"] = tuple(
            candidate
            if isinstance(candidate, ConceptCandidate)
            else ConceptCandidate.from_dict(dict(candidate))
            for candidate in values.get("split_concept_candidates", ())
        )
        return cls(**values)


@dataclass(frozen=True)
class ConceptCandidateStopRecord:
    stop_record_id: str
    schema_version: str
    created_at: str
    source_refinement_id: str
    source_concept_candidate_id: str
    source_review_decision_id: str
    stop_reason: str
    teacher_note: str
    candidate_stopped: bool
    can_be_reopened_by_teacher: bool
    reviewed_concept_created: bool
    memory_write_performed: bool
    task_behavior_changed: bool

    def __post_init__(self) -> None:
        if self.schema_version != STOP_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_concept_candidate_stop_v0")

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ConceptCandidateStopRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FutureReviewedConceptPreparationMarker:
    preparation_marker_id: str
    schema_version: str
    created_at: str
    source_refinement_id: str
    source_concept_candidate_id: str
    source_review_decision_id: str
    candidate_ready_for_future_reviewed_concept_package: bool
    future_package_required: bool
    teacher_note: str
    reviewed_concept_created: bool
    concept_approved: bool
    memory_write_performed: bool
    task_behavior_changed: bool

    def __post_init__(self) -> None:
        if self.schema_version != PREPARATION_MARKER_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_future_reviewed_concept_preparation_marker_v0")

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FutureReviewedConceptPreparationMarker":
        return cls(**dict(data))


def refine_concept_candidate_from_teacher_review(
    *,
    task: ConceptCandidateTeacherReviewTask | dict[str, object],
    decision: ConceptCandidateTeacherReviewDecision | dict[str, object],
    summary: ConceptCandidateTeacherReviewSummary | dict[str, object] | None = None,
    draft: ConceptCandidateDraftRecord | dict[str, object] | None = None,
) -> dict[str, object]:
    task_record = _task(task)
    decision_record = _decision(decision)
    summary_record = _summary(summary) if summary is not None else None
    draft_record = _draft(draft) if draft is not None else None
    blocked_status = _blocked_refinement_status(decision_record)
    refinement_id = _refinement_id(decision_record)
    child: dict[str, object | None] = {
        "evidence_request": None,
        "scope_narrowed_draft": None,
        "split_draft_set": None,
        "stop_record": None,
        "future_reviewed_concept_preparation_marker": None,
    }
    if blocked_status is None:
        if decision_record.teacher_decision == "needs_more_support":
            child["evidence_request"] = build_concept_evidence_request(
                refinement_id=refinement_id,
                decision=decision_record,
            )
        elif decision_record.teacher_decision == "scope_narrowed":
            child["scope_narrowed_draft"] = build_scope_narrowed_concept_draft(
                refinement_id=refinement_id,
                task=task_record,
                decision=decision_record,
                draft=draft_record,
            )
        elif decision_record.teacher_decision == "split_required":
            child["split_draft_set"] = build_split_concept_draft_set(
                refinement_id=refinement_id,
                task=task_record,
                decision=decision_record,
                draft=draft_record,
            )
        elif decision_record.teacher_decision == "teacher_review_ready":
            child["future_reviewed_concept_preparation_marker"] = (
                build_future_reviewed_concept_preparation_marker(
                    refinement_id=refinement_id,
                    decision=decision_record,
                )
            )
        elif decision_record.teacher_decision == "rejected":
            child["stop_record"] = build_concept_candidate_stop_record(
                refinement_id=refinement_id,
                decision=decision_record,
            )
    refinement = ConceptCandidateRefinementRecord(
        refinement_id=refinement_id,
        schema_version=REFINEMENT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_draft_id=decision_record.source_concept_candidate_draft_id,
        source_concept_candidate_id=decision_record.source_concept_candidate_id,
        source_review_task_id=decision_record.source_review_task_id,
        source_review_decision_id=decision_record.review_decision_id,
        source_review_summary_id=(
            summary_record.review_summary_id if summary_record is not None else None
        ),
        teacher_decision=decision_record.teacher_decision,
        refinement_kind=REFINEMENT_KIND_BY_DECISION.get(
            decision_record.teacher_decision,
            "stopped_candidate",
        ),
        refinement_status=blocked_status or "refinement_created",
        refinement_summary=_refinement_summary(decision_record, blocked_status),
        evidence_request_id=_record_id(child["evidence_request"], "evidence_request_id"),
        scope_narrowed_draft_id=_record_id(
            child["scope_narrowed_draft"],
            "scope_narrowed_draft_id",
        ),
        split_draft_set_id=_record_id(child["split_draft_set"], "split_draft_set_id"),
        stop_record_id=_record_id(child["stop_record"], "stop_record_id"),
        future_reviewed_concept_preparation_marker_id=_record_id(
            child["future_reviewed_concept_preparation_marker"],
            "preparation_marker_id",
        ),
        reviewed_concept_created=False,
        concept_approved=False,
        memory_write_performed=False,
        task_behavior_changed=False,
        automatic_learning_approval_created=False,
        source_trace_refs=task_record.source_trace_refs,
    )
    return {
        "refinement_record": refinement.to_dict(),
        "evidence_request": _plain(child["evidence_request"]),
        "scope_narrowed_draft": _plain(child["scope_narrowed_draft"]),
        "split_draft_set": _plain(child["split_draft_set"]),
        "stop_record": _plain(child["stop_record"]),
        "future_reviewed_concept_preparation_marker": _plain(
            child["future_reviewed_concept_preparation_marker"]
        ),
        "refinement_validation": validate_concept_candidate_refinement_record(
            refinement,
        ),
        "reviewed_concept_created": False,
        "concept_approved": False,
        "memory_write_performed": False,
        "task_behavior_changed": False,
        "automatic_learning_approval_created": False,
    }


def validate_concept_candidate_refinement_record(
    refinement: ConceptCandidateRefinementRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _refinement(refinement)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_refinement:{error}"]}
    errors: list[str] = []
    if not record.refinement_id:
        errors.append("missing_refinement_id")
    if record.teacher_decision not in REFINEMENT_KIND_BY_DECISION:
        errors.append("unsupported_teacher_decision")
    elif record.refinement_kind != REFINEMENT_KIND_BY_DECISION[record.teacher_decision]:
        errors.append("refinement_kind_mismatch")
    if record.refinement_status == "refinement_created":
        errors.extend(_missing_child_errors(record))
    for flag in (
        "reviewed_concept_created",
        "concept_approved",
        "memory_write_performed",
        "task_behavior_changed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "refinement_id": record.refinement_id,
        "teacher_decision": record.teacher_decision,
        "refinement_kind": record.refinement_kind,
        "refinement_status": record.refinement_status,
        "reviewed_concept_created": record.reviewed_concept_created,
        "concept_approved": record.concept_approved,
        "memory_write_performed": record.memory_write_performed,
        "task_behavior_changed": record.task_behavior_changed,
    }


def build_concept_evidence_request(
    *,
    refinement_id: str,
    decision: ConceptCandidateTeacherReviewDecision | dict[str, object],
) -> ConceptEvidenceRequestRecord:
    decision_record = _decision(decision)
    requested = decision_record.requested_more_evidence
    status = "request_created"
    if not decision_record.teacher_note:
        status = "blocked_missing_teacher_note"
    elif not requested and "insufficient_support" not in decision_record.decision_reason_codes:
        status = "blocked_missing_requested_evidence"
    return ConceptEvidenceRequestRecord(
        evidence_request_id=f"concept_evidence_request:{decision_record.review_decision_id}",
        schema_version=EVIDENCE_REQUEST_SCHEMA_VERSION,
        created_at=_now(),
        source_refinement_id=refinement_id,
        source_concept_candidate_id=decision_record.source_concept_candidate_id,
        source_review_decision_id=decision_record.review_decision_id,
        requested_evidence_kinds=("support", "counterexample_check"),
        requested_case_kinds=requested or ("additional_bounded_support_case",),
        requested_state_action_outcome_patterns=requested
        or ("same_state_action_outcome_support",),
        teacher_note=decision_record.teacher_note,
        request_status=status,
        does_not_run_task=True,
        does_not_collect_evidence_automatically=True,
        does_not_write_memory=True,
    )


def validate_concept_evidence_request(
    request: ConceptEvidenceRequestRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _evidence_request(request)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_request:{error}"]}
    errors: list[str] = []
    if not record.teacher_note:
        errors.append("missing_teacher_note")
    if not record.requested_state_action_outcome_patterns:
        errors.append("missing_requested_evidence")
    if record.does_not_run_task is not True:
        errors.append("does_not_run_task_false")
    if record.does_not_collect_evidence_automatically is not True:
        errors.append("does_not_collect_evidence_automatically_false")
    if record.does_not_write_memory is not True:
        errors.append("does_not_write_memory_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "evidence_request_id": record.evidence_request_id,
        "request_status": record.request_status,
        "does_not_run_task": record.does_not_run_task,
        "does_not_collect_evidence_automatically": (
            record.does_not_collect_evidence_automatically
        ),
        "does_not_write_memory": record.does_not_write_memory,
    }


def build_scope_narrowed_concept_draft(
    *,
    refinement_id: str,
    task: ConceptCandidateTeacherReviewTask | dict[str, object],
    decision: ConceptCandidateTeacherReviewDecision | dict[str, object],
    draft: ConceptCandidateDraftRecord | dict[str, object] | None = None,
) -> ScopeNarrowedConceptDraftRecord:
    task_record = _task(task)
    decision_record = _decision(decision)
    original = _original_candidate(task_record, draft)
    narrowed_label = _narrowed_label(original.concept_label, decision_record.requested_scope_changes)
    narrowed_scope_text = _narrowed_scope_text(
        original.scope_statement.scope_text,
        decision_record.requested_scope_changes,
    )
    narrowed_candidate = _candidate_from_original(
        original,
        concept_candidate_id=f"{original.concept_candidate_id}:scope_narrowed",
        concept_label=narrowed_label,
        concept_summary=f"Scope-narrowed draft from {original.concept_label}.",
        scope_text=narrowed_scope_text,
        scope_status="narrow",
        candidate_status="scope_narrowed",
        generalization_status="scope_narrowed",
        counterexample_handling_status="scope_narrowed",
    )
    status = "narrowed_draft_created"
    if not decision_record.requested_scope_changes:
        status = "blocked_missing_scope_change"
    elif not validate_concept_candidate(narrowed_candidate)["valid"]:
        status = "blocked_invalid_narrowed_candidate"
    return ScopeNarrowedConceptDraftRecord(
        scope_narrowed_draft_id=f"scope_narrowed_draft:{decision_record.review_decision_id}",
        schema_version=SCOPE_NARROWED_SCHEMA_VERSION,
        created_at=_now(),
        source_refinement_id=refinement_id,
        source_concept_candidate_id=decision_record.source_concept_candidate_id,
        source_review_decision_id=decision_record.review_decision_id,
        original_concept_label=original.concept_label,
        narrowed_concept_label=narrowed_label,
        original_scope_text=original.scope_statement.scope_text,
        narrowed_scope_text=narrowed_scope_text,
        requested_scope_changes=decision_record.requested_scope_changes,
        narrowed_concept_candidate=narrowed_candidate,
        narrowed_status=status,
        reviewed_concept_created=False,
        memory_write_performed=False,
        task_behavior_changed=False,
    )


def validate_scope_narrowed_concept_draft(
    draft: ScopeNarrowedConceptDraftRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _scope_narrowed(draft)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_scope_narrowed:{error}"]}
    errors: list[str] = []
    if not record.requested_scope_changes:
        errors.append("missing_scope_change")
    candidate_validation = validate_concept_candidate(record.narrowed_concept_candidate)
    errors.extend(f"candidate:{code}" for code in candidate_validation["error_codes"])
    if record.narrowed_concept_candidate.teacher_review_required is not True:
        errors.append("teacher_review_required_false")
    if record.narrowed_concept_candidate.memory_application_candidate_allowed is not False:
        errors.append("memory_application_candidate_allowed_true")
    if record.narrowed_concept_candidate.promotion_candidate_allowed is not False:
        errors.append("promotion_candidate_allowed_true")
    for flag in ("reviewed_concept_created", "memory_write_performed", "task_behavior_changed"):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "scope_narrowed_draft_id": record.scope_narrowed_draft_id,
        "narrowed_status": record.narrowed_status,
        "teacher_review_required": (
            record.narrowed_concept_candidate.teacher_review_required
        ),
        "memory_application_candidate_allowed": (
            record.narrowed_concept_candidate.memory_application_candidate_allowed
        ),
    }


def build_split_concept_draft_set(
    *,
    refinement_id: str,
    task: ConceptCandidateTeacherReviewTask | dict[str, object],
    decision: ConceptCandidateTeacherReviewDecision | dict[str, object],
    draft: ConceptCandidateDraftRecord | dict[str, object] | None = None,
) -> SplitConceptDraftSetRecord:
    task_record = _task(task)
    decision_record = _decision(decision)
    original = _original_candidate(task_record, draft)
    candidates = tuple(
        _split_candidate(original, label, decision_record.review_decision_id)
        for label in decision_record.requested_split_labels
    )
    status = "split_drafts_created"
    if not decision_record.requested_split_labels:
        status = "blocked_missing_split_labels"
    elif any(not validate_concept_candidate(candidate)["valid"] for candidate in candidates):
        status = "blocked_invalid_split_candidate"
    return SplitConceptDraftSetRecord(
        split_draft_set_id=f"split_concept_draft_set:{decision_record.review_decision_id}",
        schema_version=SPLIT_DRAFT_SET_SCHEMA_VERSION,
        created_at=_now(),
        source_refinement_id=refinement_id,
        source_concept_candidate_id=decision_record.source_concept_candidate_id,
        source_review_decision_id=decision_record.review_decision_id,
        original_concept_label=original.concept_label,
        requested_split_labels=decision_record.requested_split_labels,
        split_concept_candidates=candidates,
        split_status=status,
        reviewed_concept_created=False,
        memory_write_performed=False,
        task_behavior_changed=False,
    )


def validate_split_concept_draft_set(
    split_set: SplitConceptDraftSetRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _split_set(split_set)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_split_set:{error}"]}
    errors: list[str] = []
    if not record.requested_split_labels:
        errors.append("missing_split_labels")
    if len(record.split_concept_candidates) < 2 and record.split_status == "split_drafts_created":
        errors.append("missing_multiple_split_candidates")
    for candidate in record.split_concept_candidates:
        candidate_validation = validate_concept_candidate(candidate)
        errors.extend(f"candidate:{code}" for code in candidate_validation["error_codes"])
        if candidate.teacher_review_required is not True:
            errors.append("teacher_review_required_false")
        if candidate.memory_application_candidate_allowed is not False:
            errors.append("memory_application_candidate_allowed_true")
        if candidate.promotion_candidate_allowed is not False:
            errors.append("promotion_candidate_allowed_true")
    for flag in ("reviewed_concept_created", "memory_write_performed", "task_behavior_changed"):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "split_draft_set_id": record.split_draft_set_id,
        "split_status": record.split_status,
        "split_candidate_count": len(record.split_concept_candidates),
    }


def build_concept_candidate_stop_record(
    *,
    refinement_id: str,
    decision: ConceptCandidateTeacherReviewDecision | dict[str, object],
) -> ConceptCandidateStopRecord:
    decision_record = _decision(decision)
    return ConceptCandidateStopRecord(
        stop_record_id=f"concept_candidate_stop:{decision_record.review_decision_id}",
        schema_version=STOP_SCHEMA_VERSION,
        created_at=_now(),
        source_refinement_id=refinement_id,
        source_concept_candidate_id=decision_record.source_concept_candidate_id,
        source_review_decision_id=decision_record.review_decision_id,
        stop_reason="teacher_rejected_candidate",
        teacher_note=decision_record.teacher_note,
        candidate_stopped=True,
        can_be_reopened_by_teacher=True,
        reviewed_concept_created=False,
        memory_write_performed=False,
        task_behavior_changed=False,
    )


def validate_concept_candidate_stop_record(
    stop: ConceptCandidateStopRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _stop(stop)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_stop:{error}"]}
    errors: list[str] = []
    if not record.teacher_note:
        errors.append("missing_teacher_note")
    if record.candidate_stopped is not True:
        errors.append("candidate_stopped_false")
    if record.can_be_reopened_by_teacher is not True:
        errors.append("can_be_reopened_by_teacher_false")
    for flag in ("reviewed_concept_created", "memory_write_performed", "task_behavior_changed"):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "stop_record_id": record.stop_record_id,
        "candidate_stopped": record.candidate_stopped,
        "can_be_reopened_by_teacher": record.can_be_reopened_by_teacher,
    }


def build_future_reviewed_concept_preparation_marker(
    *,
    refinement_id: str,
    decision: ConceptCandidateTeacherReviewDecision | dict[str, object],
) -> FutureReviewedConceptPreparationMarker:
    decision_record = _decision(decision)
    return FutureReviewedConceptPreparationMarker(
        preparation_marker_id=f"future_reviewed_concept_marker:{decision_record.review_decision_id}",
        schema_version=PREPARATION_MARKER_SCHEMA_VERSION,
        created_at=_now(),
        source_refinement_id=refinement_id,
        source_concept_candidate_id=decision_record.source_concept_candidate_id,
        source_review_decision_id=decision_record.review_decision_id,
        candidate_ready_for_future_reviewed_concept_package=True,
        future_package_required=True,
        teacher_note=decision_record.teacher_note,
        reviewed_concept_created=False,
        concept_approved=False,
        memory_write_performed=False,
        task_behavior_changed=False,
    )


def validate_future_reviewed_concept_preparation_marker(
    marker: FutureReviewedConceptPreparationMarker | dict[str, object],
) -> dict[str, object]:
    try:
        record = _marker(marker)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_marker:{error}"]}
    errors: list[str] = []
    if record.candidate_ready_for_future_reviewed_concept_package is not True:
        errors.append("candidate_ready_false")
    if record.future_package_required is not True:
        errors.append("future_package_required_false")
    if not record.teacher_note:
        errors.append("missing_teacher_note")
    for flag in (
        "reviewed_concept_created",
        "concept_approved",
        "memory_write_performed",
        "task_behavior_changed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "preparation_marker_id": record.preparation_marker_id,
        "candidate_ready_for_future_reviewed_concept_package": (
            record.candidate_ready_for_future_reviewed_concept_package
        ),
        "reviewed_concept_created": record.reviewed_concept_created,
        "concept_approved": record.concept_approved,
    }


def build_demo_more_support_refinement() -> dict[str, object]:
    return _demo_refinement("needs_more_support", build_demo_needs_more_support_review)


def build_demo_scope_narrowed_refinement() -> dict[str, object]:
    return _demo_refinement("scope_narrowed", build_demo_scope_narrowed_review)


def build_demo_split_required_refinement() -> dict[str, object]:
    return _demo_refinement("split_required", build_demo_split_required_review)


def build_demo_teacher_review_ready_refinement() -> dict[str, object]:
    return _demo_refinement("teacher_review_ready", build_demo_teacher_review_ready_review)


def build_demo_rejected_refinement() -> dict[str, object]:
    return _demo_refinement("rejected", build_demo_rejected_review)


def build_demo_refinement(decision: str) -> dict[str, object]:
    builders = {
        "needs_more_support": build_demo_more_support_refinement,
        "scope_narrowed": build_demo_scope_narrowed_refinement,
        "split_required": build_demo_split_required_refinement,
        "teacher_review_ready": build_demo_teacher_review_ready_refinement,
        "rejected": build_demo_rejected_refinement,
    }
    try:
        return builders[decision]()
    except KeyError as error:
        raise ValueError(f"unknown decision: {decision}") from error


def _demo_refinement(
    decision: str,
    review_builder,
) -> dict[str, object]:
    review_payload = review_builder()
    demo = "unknown" if decision == "teacher_review_ready" else "blocked"
    draft = build_demo_draft(demo)
    return refine_concept_candidate_from_teacher_review(
        task=review_payload["review_task"],
        decision=review_payload["review_decision"],
        summary=review_payload["review_summary"],
        draft=draft,
    )


def _blocked_refinement_status(
    decision: ConceptCandidateTeacherReviewDecision,
) -> str | None:
    validation = validate_concept_candidate_teacher_review_decision(decision)
    if not decision.teacher_decision:
        return "blocked_missing_teacher_decision"
    if decision.teacher_decision not in REFINEMENT_KIND_BY_DECISION:
        return "blocked_unsupported_decision"
    if not validation["valid"] or not decision.decision_valid:
        if decision.decision_blocked_reason == "scope_change_required_but_missing":
            return "blocked_missing_required_scope_change"
        if decision.decision_blocked_reason == "split_labels_required_but_missing":
            return "blocked_missing_required_split_labels"
        if decision.decision_blocked_reason == "missing_counterexample_handling":
            return "blocked_missing_required_evidence_request"
        return "blocked_invalid_review_decision"
    return None


def _missing_child_errors(record: ConceptCandidateRefinementRecord) -> list[str]:
    child_field = {
        "more_support_request": "evidence_request_id",
        "scope_narrowed_draft": "scope_narrowed_draft_id",
        "split_draft_set": "split_draft_set_id",
        "future_reviewed_concept_preparation": (
            "future_reviewed_concept_preparation_marker_id"
        ),
        "stopped_candidate": "stop_record_id",
    }[record.refinement_kind]
    if getattr(record, child_field) is None:
        return [f"missing_{child_field}"]
    return []


def _refinement_id(decision: ConceptCandidateTeacherReviewDecision) -> str:
    return f"concept_refinement:{decision.review_decision_id}"


def _refinement_summary(
    decision: ConceptCandidateTeacherReviewDecision,
    blocked_status: str | None,
) -> str:
    if blocked_status:
        return f"Refinement blocked for {decision.teacher_decision}: {blocked_status}."
    return (
        f"Teacher decision {decision.teacher_decision} was transformed into "
        f"{REFINEMENT_KIND_BY_DECISION[decision.teacher_decision]} output."
    )


def _record_id(record: object | None, field_name: str) -> str | None:
    if record is None:
        return None
    return str(getattr(record, field_name))


def _original_candidate(
    task: ConceptCandidateTeacherReviewTask,
    draft: ConceptCandidateDraftRecord | dict[str, object] | None,
) -> ConceptCandidate:
    draft_record = _draft(draft) if draft is not None else None
    if draft_record is not None and draft_record.drafted_concept_candidate is not None:
        return draft_record.drafted_concept_candidate
    scope = ConceptScopeStatement(
        scope_id=f"concept_scope:{task.concept_label}:fallback",
        scope_text=f"Fallback scope for {task.concept_label}.",
        applies_when=("teacher_review_task_context",),
        does_not_apply_when=("outside_demo_context",),
        known_limits=("fallback candidate from review task only",),
        uncertainty_notes=("source draft not provided",),
        scope_confidence=0.2,
        scope_status="provisional",
    )
    return ConceptCandidate(
        concept_candidate_id=task.source_concept_candidate_id,
        schema_version=CONCEPT_CANDIDATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        concept_label=task.concept_label,
        concept_summary=task.concept_summary,
        source_task_ids=(task.source_review_task_id,),
        source_case_ids=("review_task_fallback",),
        source_state_action_outcome_refs=(task.source_review_task_id,),
        support_evidence_refs=(),
        counterexample_evidence_refs=(),
        scope_statement=scope,
        generalization_level=task.generalization_level,
        generalization_status="needs_more_support",
        teacher_review_required=True,
        teacher_review_ready=False,
        memory_application_candidate_allowed=False,
        promotion_candidate_allowed=False,
        candidate_status="needs_more_support",
        counterexample_handling_status="not_checked",
        safe_claim=CANDIDATE_SAFE_CLAIM,
        blocked_claims=CANDIDATE_BLOCKED_CLAIMS,
        source_trace_refs=task.source_trace_refs,
    )


def _candidate_from_original(
    original: ConceptCandidate,
    *,
    concept_candidate_id: str,
    concept_label: str,
    concept_summary: str,
    scope_text: str,
    scope_status: str,
    candidate_status: str,
    generalization_status: str,
    counterexample_handling_status: str,
) -> ConceptCandidate:
    scope = ConceptScopeStatement(
        scope_id=f"{original.scope_statement.scope_id}:{concept_label}:refined",
        scope_text=scope_text,
        applies_when=original.scope_statement.applies_when,
        does_not_apply_when=original.scope_statement.does_not_apply_when,
        known_limits=(
            *original.scope_statement.known_limits,
            "refined draft only",
            "not teacher approved",
        ),
        uncertainty_notes=(
            *original.scope_statement.uncertainty_notes,
            "requires future teacher review",
        ),
        scope_confidence=min(1.0, original.scope_statement.scope_confidence + 0.05),
        scope_status=scope_status,
    )
    return ConceptCandidate(
        concept_candidate_id=concept_candidate_id,
        schema_version=CONCEPT_CANDIDATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        concept_label=concept_label,
        concept_summary=concept_summary,
        source_task_ids=original.source_task_ids,
        source_case_ids=original.source_case_ids,
        source_state_action_outcome_refs=original.source_state_action_outcome_refs,
        support_evidence_refs=original.support_evidence_refs,
        counterexample_evidence_refs=(),
        scope_statement=scope,
        generalization_level=original.generalization_level,
        generalization_status=generalization_status,
        teacher_review_required=True,
        teacher_review_ready=False,
        memory_application_candidate_allowed=False,
        promotion_candidate_allowed=False,
        candidate_status=candidate_status,
        counterexample_handling_status=counterexample_handling_status,
        safe_claim=CANDIDATE_SAFE_CLAIM,
        blocked_claims=CANDIDATE_BLOCKED_CLAIMS,
        source_trace_refs=original.source_trace_refs,
    )


def _split_candidate(
    original: ConceptCandidate,
    label: str,
    source_review_decision_id: str,
) -> ConceptCandidate:
    scope = ConceptScopeStatement(
        scope_id=f"concept_scope:{label}:split_draft_v0",
        scope_text=f"Split draft candidate {label} from {original.concept_label}.",
        applies_when=(f"candidate_label={label}",),
        does_not_apply_when=("outside_split_scope",),
        known_limits=("split draft only", "needs support evidence"),
        uncertainty_notes=("not checked against counterexamples yet",),
        scope_confidence=0.25,
        scope_status="provisional",
    )
    return ConceptCandidate(
        concept_candidate_id=f"concept_candidate:{label}:split_draft_v0",
        schema_version=CONCEPT_CANDIDATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        concept_label=label,
        concept_summary=f"Split draft candidate {label} from {original.concept_label}.",
        source_task_ids=original.source_task_ids,
        source_case_ids=original.source_case_ids,
        source_state_action_outcome_refs=(source_review_decision_id,),
        support_evidence_refs=(),
        counterexample_evidence_refs=(),
        scope_statement=scope,
        generalization_level="same_context",
        generalization_status="needs_more_support",
        teacher_review_required=True,
        teacher_review_ready=False,
        memory_application_candidate_allowed=False,
        promotion_candidate_allowed=False,
        candidate_status="needs_more_support",
        counterexample_handling_status="not_checked",
        safe_claim=CANDIDATE_SAFE_CLAIM,
        blocked_claims=CANDIDATE_BLOCKED_CLAIMS,
        source_trace_refs=(source_review_decision_id,),
    )


def _narrowed_label(
    original_label: str,
    requested_scope_changes: tuple[str, ...],
) -> str:
    if not requested_scope_changes:
        return f"{original_label}_narrowed"
    first = requested_scope_changes[0]
    if "->" in first:
        return first.split("->", 1)[1].strip().replace(" ", "_")
    return f"{original_label}_narrowed"


def _narrowed_scope_text(
    original_scope_text: str,
    requested_scope_changes: tuple[str, ...],
) -> str:
    if not requested_scope_changes:
        return original_scope_text
    return f"{original_scope_text} Narrowing requested: {requested_scope_changes[0]}"


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


def _draft(
    draft: ConceptCandidateDraftRecord | dict[str, object],
) -> ConceptCandidateDraftRecord:
    return (
        draft
        if isinstance(draft, ConceptCandidateDraftRecord)
        else ConceptCandidateDraftRecord.from_dict(dict(draft))
    )


def _refinement(
    refinement: ConceptCandidateRefinementRecord | dict[str, object],
) -> ConceptCandidateRefinementRecord:
    return (
        refinement
        if isinstance(refinement, ConceptCandidateRefinementRecord)
        else ConceptCandidateRefinementRecord.from_dict(dict(refinement))
    )


def _evidence_request(
    request: ConceptEvidenceRequestRecord | dict[str, object],
) -> ConceptEvidenceRequestRecord:
    return (
        request
        if isinstance(request, ConceptEvidenceRequestRecord)
        else ConceptEvidenceRequestRecord.from_dict(dict(request))
    )


def _scope_narrowed(
    draft: ScopeNarrowedConceptDraftRecord | dict[str, object],
) -> ScopeNarrowedConceptDraftRecord:
    return (
        draft
        if isinstance(draft, ScopeNarrowedConceptDraftRecord)
        else ScopeNarrowedConceptDraftRecord.from_dict(dict(draft))
    )


def _split_set(
    split_set: SplitConceptDraftSetRecord | dict[str, object],
) -> SplitConceptDraftSetRecord:
    return (
        split_set
        if isinstance(split_set, SplitConceptDraftSetRecord)
        else SplitConceptDraftSetRecord.from_dict(dict(split_set))
    )


def _stop(
    stop: ConceptCandidateStopRecord | dict[str, object],
) -> ConceptCandidateStopRecord:
    return (
        stop
        if isinstance(stop, ConceptCandidateStopRecord)
        else ConceptCandidateStopRecord.from_dict(dict(stop))
    )


def _marker(
    marker: FutureReviewedConceptPreparationMarker | dict[str, object],
) -> FutureReviewedConceptPreparationMarker:
    return (
        marker
        if isinstance(marker, FutureReviewedConceptPreparationMarker)
        else FutureReviewedConceptPreparationMarker.from_dict(dict(marker))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
