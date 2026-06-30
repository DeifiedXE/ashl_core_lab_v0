"""Build ReviewedConcept readback hint candidates from Working Memory previews."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.memory.reviewed_concept_working_readback_preview import (
    ReviewedConceptWorkingReadbackHintPreview,
    ReviewedConceptWorkingReadbackPreview,
    ReviewedConceptWorkingReadbackPreviewSafetyAudit,
    build_demo_held_for_more_evidence_readback_preview,
    build_demo_reviewed_concept_working_readback_preview_bundle,
    validate_reviewed_concept_working_readback_hint_preview,
    validate_reviewed_concept_working_readback_preview,
    validate_reviewed_concept_working_readback_preview_safety_audit,
)


SOURCE_ENGINE = "memory_engine"
READBACK_HINT_CANDIDATE_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_readback_hint_candidate_v0"
)
READBACK_HINT_CANDIDATE_SET_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_readback_hint_candidate_set_v0"
)
READBACK_HINT_CANDIDATE_SAFETY_AUDIT_SCHEMA_VERSION = (
    "memory_engine_reviewed_concept_readback_hint_candidate_safety_audit_v0"
)

SAFE_CLAIM = (
    "ASHL Core v1 Memory Engine can convert ReviewedConcept Working Readback "
    "Preview records into TaskWorkingMemoryReadbackHint candidate records for "
    "teacher review, without creating actual readback hints, mutating Working "
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

ALLOWED_HINT_KINDS = {
    "observe_before_retry",
    "avoid_repeated_failure",
    "verify_scope",
    "verify_expected_actual",
    "use_known_success_path",
    "gather_context",
}
ALLOWED_CANDIDATE_STATUSES = {
    "candidate_ready_for_teacher_review",
    "held_for_more_evidence",
    "blocked_invalid_preview",
    "blocked_no_hint_label",
    "blocked_forbidden_authority_detected",
}
ALLOWED_SET_STATUSES = {
    "candidate_set_created",
    "held_for_more_evidence",
    "blocked_invalid_hint_preview",
    "blocked_empty_candidate_set",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed",
    "blocked_invalid_readback_preview",
    "blocked_invalid_hint_preview",
    "blocked_invalid_candidate_set",
    "blocked_forbidden_hint_creation_detected",
    "blocked_forbidden_working_memory_mutation_detected",
    "blocked_forbidden_behavior_change_detected",
    "blocked_forbidden_action_authority_detected",
    "blocked_forbidden_memory_write_detected",
}
HINT_KIND_BY_LABEL = {
    "observe_before_direct_retry": "observe_before_retry",
    "avoid_same_failed_direct_retry": "avoid_repeated_failure",
    "verify_obstacle_type_before_generalizing": "verify_scope",
    "observe_or_adjust": "gather_context",
    "gather_context_first": "gather_context",
    "avoid_direct_retry_under_unknown": "avoid_repeated_failure",
    "verify_expected_actual_before_reuse": "verify_expected_actual",
    "do_not_reuse_unverified_prediction": "verify_expected_actual",
    "prefer_low_risk_verification": "verify_expected_actual",
    "known_success_path_available": "use_known_success_path",
    "verify_reachability_context": "verify_scope",
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
class ReviewedConceptReadbackHintCandidate:
    readback_hint_candidate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_working_readback_preview_id: str
    source_working_readback_hint_preview_id: str
    source_memory_application_data_id: str
    concept_label: str
    hint_label: str
    hint_summary: str
    hint_kind: str
    hint_priority: int
    task_handling_note: str
    scope_warning: str | None
    counterexample_warning: str | None
    candidate_status: str
    candidate_summary: str
    requires_teacher_review_before_application: bool
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
        if self.schema_version != READBACK_HINT_CANDIDATE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_readback_hint_candidate_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.hint_kind not in ALLOWED_HINT_KINDS:
            raise ValueError(f"unknown hint_kind: {self.hint_kind}")
        if self.candidate_status not in ALLOWED_CANDIDATE_STATUSES:
            raise ValueError(f"unknown candidate_status: {self.candidate_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReviewedConceptReadbackHintCandidate":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptReadbackHintCandidateSet:
    hint_candidate_set_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_working_readback_preview_id: str
    source_working_readback_hint_preview_id: str
    concept_label: str
    hint_candidates: tuple[ReviewedConceptReadbackHintCandidate, ...]
    candidate_count: int
    candidate_labels: tuple[str, ...]
    set_status: str
    set_summary: str
    requires_teacher_review_before_application: bool
    actual_task_working_memory_hint_created: bool
    applied_to_working_memory: bool
    working_memory_mutated: bool
    task_behavior_changed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READBACK_HINT_CANDIDATE_SET_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_readback_hint_candidate_set_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be memory_engine")
        if self.set_status not in ALLOWED_SET_STATUSES:
            raise ValueError(f"unknown set_status: {self.set_status}")
        object.__setattr__(
            self,
            "hint_candidates",
            tuple(
                item
                if isinstance(item, ReviewedConceptReadbackHintCandidate)
                else ReviewedConceptReadbackHintCandidate.from_dict(dict(item))
                for item in self.hint_candidates
            ),
        )
        for name in ("candidate_labels", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptReadbackHintCandidateSet":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptReadbackHintCandidateSafetyAudit:
    safety_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_hint_candidate_set_id: str | None
    source_working_readback_preview_id: str | None
    source_working_readback_hint_preview_id: str | None
    readback_preview_valid: bool
    hint_preview_valid: bool
    candidate_set_valid: bool
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
        if self.schema_version != READBACK_HINT_CANDIDATE_SAFETY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be memory_engine_reviewed_concept_readback_hint_candidate_safety_audit_v0"
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
    ) -> "ReviewedConceptReadbackHintCandidateSafetyAudit":
        return cls(**dict(data))


def build_reviewed_concept_readback_hint_candidate(
    *,
    readback_preview: ReviewedConceptWorkingReadbackPreview | dict[str, object],
    hint_preview: ReviewedConceptWorkingReadbackHintPreview | dict[str, object],
    hint_label: str,
    hint_priority: int = 1,
) -> ReviewedConceptReadbackHintCandidate:
    readback = _readback_preview(readback_preview)
    hint = _hint_preview(hint_preview)
    status = _candidate_status(readback, hint, hint_label)
    hint_kind = HINT_KIND_BY_LABEL.get(hint_label, "verify_scope")
    return ReviewedConceptReadbackHintCandidate(
        readback_hint_candidate_id=(
            f"reviewed_concept_readback_hint_candidate:"
            f"{readback.source_reviewed_concept_id}:{hint_label or 'missing'}"
        ),
        schema_version=READBACK_HINT_CANDIDATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=readback.source_reviewed_concept_id,
        source_working_readback_preview_id=readback.working_readback_preview_id,
        source_working_readback_hint_preview_id=hint.working_readback_hint_preview_id,
        source_memory_application_data_id=readback.source_memory_application_data_id,
        concept_label=readback.concept_label,
        hint_label=hint_label,
        hint_summary=_hint_summary(hint_label, status),
        hint_kind=hint_kind,
        hint_priority=hint_priority,
        task_handling_note=_task_note_for_priority(hint, hint_priority),
        scope_warning=_warning_for_priority(hint.scope_warnings, hint_priority),
        counterexample_warning=_warning_for_priority(
            hint.counterexample_warnings,
            hint_priority,
        ),
        candidate_status=status,
        candidate_summary=_candidate_summary(status),
        requires_teacher_review_before_application=True,
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
            readback.source_trace_refs,
            hint.source_trace_refs,
        ),
    )


def validate_reviewed_concept_readback_hint_candidate(
    candidate: ReviewedConceptReadbackHintCandidate | dict[str, object],
) -> dict[str, object]:
    try:
        record = _candidate(candidate)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_hint_candidate:{error}"]}
    errors: list[str] = []
    if record.candidate_status.startswith("blocked_"):
        errors.append(record.candidate_status)
    if record.candidate_status == "candidate_ready_for_teacher_review":
        if not record.hint_label:
            errors.append("missing_hint_label")
        if record.hint_kind not in ALLOWED_HINT_KINDS:
            errors.append("invalid_hint_kind")
    for flag in (
        "requires_teacher_review_before_application",
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
        "readback_hint_candidate_id": record.readback_hint_candidate_id,
        "candidate_status": record.candidate_status,
        "hint_label": record.hint_label,
        "hint_kind": record.hint_kind,
    }


def build_reviewed_concept_readback_hint_candidate_set(
    *,
    readback_preview: ReviewedConceptWorkingReadbackPreview | dict[str, object],
    hint_preview: ReviewedConceptWorkingReadbackHintPreview | dict[str, object],
) -> ReviewedConceptReadbackHintCandidateSet:
    readback = _readback_preview(readback_preview)
    hint = _hint_preview(hint_preview)
    labels = tuple(hint.hint_labels)
    candidates = tuple(
        build_reviewed_concept_readback_hint_candidate(
            readback_preview=readback,
            hint_preview=hint,
            hint_label=label,
            hint_priority=index + 1,
        )
        for index, label in enumerate(labels)
    )
    status = _candidate_set_status(readback, hint, candidates)
    return ReviewedConceptReadbackHintCandidateSet(
        hint_candidate_set_id=f"reviewed_concept_readback_hint_candidate_set:{readback.source_reviewed_concept_id}",
        schema_version=READBACK_HINT_CANDIDATE_SET_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=readback.source_reviewed_concept_id,
        source_working_readback_preview_id=readback.working_readback_preview_id,
        source_working_readback_hint_preview_id=hint.working_readback_hint_preview_id,
        concept_label=readback.concept_label,
        hint_candidates=candidates,
        candidate_count=len(candidates),
        candidate_labels=tuple(candidate.hint_label for candidate in candidates),
        set_status=status,
        set_summary=_set_summary(status),
        requires_teacher_review_before_application=True,
        actual_task_working_memory_hint_created=False,
        applied_to_working_memory=False,
        working_memory_mutated=False,
        task_behavior_changed=False,
        source_trace_refs=_combined_trace_refs(
            readback.source_trace_refs,
            hint.source_trace_refs,
        ),
    )


def validate_reviewed_concept_readback_hint_candidate_set(
    candidate_set: ReviewedConceptReadbackHintCandidateSet | dict[str, object],
) -> dict[str, object]:
    try:
        record = _candidate_set(candidate_set)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_candidate_set:{error}"]}
    errors: list[str] = []
    if record.set_status.startswith("blocked_"):
        errors.append(record.set_status)
    if record.set_status == "candidate_set_created" and not record.hint_candidates:
        errors.append("empty_candidate_set")
    if record.candidate_count != len(record.hint_candidates):
        errors.append("candidate_count_mismatch")
    if record.candidate_labels != tuple(candidate.hint_label for candidate in record.hint_candidates):
        errors.append("candidate_labels_mismatch")
    if record.requires_teacher_review_before_application is not True:
        errors.append("requires_teacher_review_before_application_false")
    for flag in (
        "actual_task_working_memory_hint_created",
        "applied_to_working_memory",
        "working_memory_mutated",
        "task_behavior_changed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    candidate_errors = [
        validation
        for validation in (
            validate_reviewed_concept_readback_hint_candidate(candidate)
            for candidate in record.hint_candidates
        )
        if not validation["valid"]
    ]
    if candidate_errors and record.set_status == "candidate_set_created":
        errors.append("candidate_invalid")
    return {
        "valid": not errors,
        "error_codes": errors,
        "hint_candidate_set_id": record.hint_candidate_set_id,
        "set_status": record.set_status,
        "candidate_count": record.candidate_count,
        "candidate_labels": record.candidate_labels,
    }


def build_reviewed_concept_readback_hint_candidate_safety_audit(
    *,
    readback_preview: ReviewedConceptWorkingReadbackPreview | dict[str, object],
    hint_preview: ReviewedConceptWorkingReadbackHintPreview | dict[str, object],
    candidate_set: ReviewedConceptReadbackHintCandidateSet | dict[str, object],
) -> ReviewedConceptReadbackHintCandidateSafetyAudit:
    readback = _readback_preview(readback_preview)
    hint = _hint_preview(hint_preview)
    candidates = _candidate_set(candidate_set)
    readback_preview_valid = bool(
        validate_reviewed_concept_working_readback_preview(readback)["valid"]
    )
    hint_preview_valid = bool(
        validate_reviewed_concept_working_readback_hint_preview(hint)["valid"]
    )
    candidate_set_valid = bool(
        validate_reviewed_concept_readback_hint_candidate_set(candidates)["valid"]
    )
    no_actual_hint = (
        hint.actual_task_working_memory_hint_created is False
        and candidates.actual_task_working_memory_hint_created is False
        and all(
            candidate.actual_task_working_memory_hint_created is False
            for candidate in candidates.hint_candidates
        )
    )
    no_working_memory_mutation = (
        hint.applied_to_working_memory is False
        and candidates.applied_to_working_memory is False
        and candidates.working_memory_mutated is False
        and all(
            candidate.applied_to_working_memory is False
            and candidate.working_memory_mutated is False
            for candidate in candidates.hint_candidates
        )
    )
    no_task_behavior_change = (
        hint.task_behavior_changed is False
        and candidates.task_behavior_changed is False
        and all(
            candidate.task_behavior_changed is False
            for candidate in candidates.hint_candidates
        )
    )
    no_candidate_ordering_change = (
        hint.candidate_ordering_changed is False
        and all(
            candidate.candidate_ordering_changed is False
            for candidate in candidates.hint_candidates
        )
    )
    no_action_selection = (
        hint.action_selection_created is False
        and all(
            candidate.action_selection_created is False
            for candidate in candidates.hint_candidates
        )
    )
    no_action_execution = (
        hint.action_execution_created is False
        and all(
            candidate.action_execution_created is False
            for candidate in candidates.hint_candidates
        )
    )
    no_memory_layer_write = all(
        candidate.memory_layer_write_performed is False
        for candidate in candidates.hint_candidates
    )
    no_automatic_learning_approval = all(
        candidate.automatic_learning_approval_created is False
        for candidate in candidates.hint_candidates
    )
    blocked_reasons = _safety_blocked_reasons(
        readback_preview_valid=readback_preview_valid,
        hint_preview_valid=hint_preview_valid,
        candidate_set_valid=candidate_set_valid,
        no_actual_task_working_memory_hint_created=no_actual_hint,
        no_working_memory_mutation=no_working_memory_mutation,
        no_task_behavior_change=no_task_behavior_change,
        no_candidate_ordering_change=no_candidate_ordering_change,
        no_action_selection=no_action_selection,
        no_action_execution=no_action_execution,
        no_memory_layer_write=no_memory_layer_write,
        no_automatic_learning_approval=no_automatic_learning_approval,
    )
    return ReviewedConceptReadbackHintCandidateSafetyAudit(
        safety_audit_id=f"reviewed_concept_readback_hint_candidate_safety_audit:{readback.source_reviewed_concept_id}",
        schema_version=READBACK_HINT_CANDIDATE_SAFETY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=readback.source_reviewed_concept_id,
        source_hint_candidate_set_id=candidates.hint_candidate_set_id,
        source_working_readback_preview_id=readback.working_readback_preview_id,
        source_working_readback_hint_preview_id=hint.working_readback_hint_preview_id,
        readback_preview_valid=readback_preview_valid,
        hint_preview_valid=hint_preview_valid,
        candidate_set_valid=candidate_set_valid,
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
        audit_status=_safety_audit_status(blocked_reasons),
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=blocked_reasons,
        source_trace_refs=_combined_trace_refs(
            readback.source_trace_refs,
            hint.source_trace_refs,
            candidates.source_trace_refs,
        ),
    )


def validate_reviewed_concept_readback_hint_candidate_safety_audit(
    audit: ReviewedConceptReadbackHintCandidateSafetyAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _safety_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_safety_audit:{error}"]}
    errors: list[str] = []
    if record.audit_status != "passed":
        errors.append(record.audit_status)
    for flag in (
        "readback_preview_valid",
        "hint_preview_valid",
        "candidate_set_valid",
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


def build_reviewed_concept_readback_hint_candidate_bundle(
    readback_payload: dict[str, object],
) -> dict[str, object]:
    readback = _readback_preview(readback_payload["working_readback_preview"])
    hint = _hint_preview(readback_payload["working_readback_hint_preview"])
    candidate_set = build_reviewed_concept_readback_hint_candidate_set(
        readback_preview=readback,
        hint_preview=hint,
    )
    safety = build_reviewed_concept_readback_hint_candidate_safety_audit(
        readback_preview=readback,
        hint_preview=hint,
        candidate_set=candidate_set,
    )
    return {
        "hint_candidate_set": candidate_set.to_dict(),
        "hint_candidates": [candidate.to_dict() for candidate in candidate_set.hint_candidates],
        "hint_candidate_safety_audit": safety.to_dict(),
        "hint_candidate_set_validation": (
            validate_reviewed_concept_readback_hint_candidate_set(candidate_set)
        ),
        "hint_candidate_safety_audit_validation": (
            validate_reviewed_concept_readback_hint_candidate_safety_audit(safety)
        ),
        "safe_claim": SAFE_CLAIM,
    }


def build_demo_reviewed_concept_readback_hint_candidate_set() -> dict[str, object]:
    return build_reviewed_concept_readback_hint_candidate_bundle(
        build_demo_reviewed_concept_working_readback_preview_bundle()
    )


def build_demo_reviewed_concept_readback_hint_candidate_safety_audit() -> (
    ReviewedConceptReadbackHintCandidateSafetyAudit
):
    payload = build_demo_reviewed_concept_readback_hint_candidate_set()
    return ReviewedConceptReadbackHintCandidateSafetyAudit.from_dict(
        payload["hint_candidate_safety_audit"]
    )


def build_demo_held_for_more_evidence_hint_candidate_set() -> dict[str, object]:
    return build_reviewed_concept_readback_hint_candidate_bundle(
        build_demo_held_for_more_evidence_readback_preview()
    )


def build_demo_blocked_invalid_hint_preview_candidate_set() -> dict[str, object]:
    payload = build_demo_reviewed_concept_working_readback_preview_bundle()
    hint_data = dict(payload["working_readback_hint_preview"])
    hint_data["hint_preview_status"] = "blocked_invalid_readback_preview"
    hint_data["hint_preview_kind"] = "blocked"
    hint_data["hint_labels"] = []
    hint = ReviewedConceptWorkingReadbackHintPreview.from_dict(hint_data)
    return build_reviewed_concept_readback_hint_candidate_bundle(
        {**payload, "working_readback_hint_preview": hint.to_dict()}
    )


def build_demo_blocked_forbidden_working_memory_mutation_candidate_set() -> dict[str, object]:
    payload = build_demo_reviewed_concept_readback_hint_candidate_set()
    candidate_set = ReviewedConceptReadbackHintCandidateSet.from_dict(
        payload["hint_candidate_set"]
    )
    data = dict(candidate_set.to_dict())
    data["working_memory_mutated"] = True
    candidate_set = ReviewedConceptReadbackHintCandidateSet.from_dict(data)
    readback_payload = build_demo_reviewed_concept_working_readback_preview_bundle()
    safety = build_reviewed_concept_readback_hint_candidate_safety_audit(
        readback_preview=readback_payload["working_readback_preview"],
        hint_preview=readback_payload["working_readback_hint_preview"],
        candidate_set=candidate_set,
    )
    return {
        **payload,
        "hint_candidate_set": candidate_set.to_dict(),
        "hint_candidate_set_validation": (
            validate_reviewed_concept_readback_hint_candidate_set(candidate_set)
        ),
        "hint_candidate_safety_audit": safety.to_dict(),
        "hint_candidate_safety_audit_validation": (
            validate_reviewed_concept_readback_hint_candidate_safety_audit(safety)
        ),
    }


def build_demo_blocked_forbidden_behavior_change_candidate_set() -> dict[str, object]:
    payload = build_demo_reviewed_concept_readback_hint_candidate_set()
    candidates = [
        ReviewedConceptReadbackHintCandidate.from_dict(item)
        for item in payload["hint_candidates"]
    ]
    first = dict(candidates[0].to_dict())
    first["task_behavior_changed"] = True
    candidates[0] = ReviewedConceptReadbackHintCandidate.from_dict(first)
    candidate_set = ReviewedConceptReadbackHintCandidateSet.from_dict(
        {
            **payload["hint_candidate_set"],
            "hint_candidates": [candidate.to_dict() for candidate in candidates],
        }
    )
    readback_payload = build_demo_reviewed_concept_working_readback_preview_bundle()
    safety = build_reviewed_concept_readback_hint_candidate_safety_audit(
        readback_preview=readback_payload["working_readback_preview"],
        hint_preview=readback_payload["working_readback_hint_preview"],
        candidate_set=candidate_set,
    )
    return {
        **payload,
        "hint_candidates": [candidate.to_dict() for candidate in candidates],
        "hint_candidate_set": candidate_set.to_dict(),
        "hint_candidate_set_validation": (
            validate_reviewed_concept_readback_hint_candidate_set(candidate_set)
        ),
        "hint_candidate_safety_audit": safety.to_dict(),
        "hint_candidate_safety_audit_validation": (
            validate_reviewed_concept_readback_hint_candidate_safety_audit(safety)
        ),
    }


def build_demo_blocked_hint_candidate_set(case: str) -> dict[str, object]:
    cases = {
        "invalid-hint-preview": build_demo_blocked_invalid_hint_preview_candidate_set,
        "forbidden-working-memory-mutation": (
            build_demo_blocked_forbidden_working_memory_mutation_candidate_set
        ),
        "forbidden-behavior-change": (
            build_demo_blocked_forbidden_behavior_change_candidate_set
        ),
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked hint candidate case: {case}") from error


def _candidate_status(
    readback: ReviewedConceptWorkingReadbackPreview,
    hint: ReviewedConceptWorkingReadbackHintPreview,
    hint_label: str,
) -> str:
    if (
        readback.actual_readback_hint_created
        or readback.working_memory_mutated
        or readback.task_behavior_changed
        or readback.memory_layer_write_performed
        or readback.automatic_learning_approval_created
        or hint.actual_task_working_memory_hint_created
        or hint.applied_to_working_memory
        or hint.task_behavior_changed
        or hint.candidate_ordering_changed
        or hint.action_selection_created
        or hint.action_execution_created
    ):
        return "blocked_forbidden_authority_detected"
    if hint.hint_preview_status == "held_for_more_evidence":
        return "held_for_more_evidence"
    if hint.hint_preview_status != "hint_preview_ready":
        return "blocked_invalid_preview"
    if not hint_label:
        return "blocked_no_hint_label"
    return "candidate_ready_for_teacher_review"


def _candidate_set_status(
    readback: ReviewedConceptWorkingReadbackPreview,
    hint: ReviewedConceptWorkingReadbackHintPreview,
    candidates: tuple[ReviewedConceptReadbackHintCandidate, ...],
) -> str:
    if any(
        (
            readback.actual_readback_hint_created,
            readback.working_memory_mutated,
            readback.task_behavior_changed,
            readback.memory_layer_write_performed,
            hint.actual_task_working_memory_hint_created,
            hint.applied_to_working_memory,
            hint.task_behavior_changed,
            hint.candidate_ordering_changed,
            hint.action_selection_created,
            hint.action_execution_created,
        )
    ):
        return "blocked_forbidden_authority_detected"
    if hint.hint_preview_status == "held_for_more_evidence":
        return "held_for_more_evidence"
    if hint.hint_preview_status != "hint_preview_ready":
        return "blocked_invalid_hint_preview"
    if not candidates:
        return "blocked_empty_candidate_set"
    if any(candidate.candidate_status.startswith("blocked_") for candidate in candidates):
        return "blocked_invalid_hint_preview"
    return "candidate_set_created"


def _hint_summary(hint_label: str, status: str) -> str:
    if status == "candidate_ready_for_teacher_review":
        return f"Preview hint label {hint_label} is available as a teacher-review candidate."
    if status == "held_for_more_evidence":
        return f"Preview hint label {hint_label or 'missing'} is held for more evidence."
    return f"Preview hint label {hint_label or 'missing'} is blocked: {status}."


def _candidate_summary(status: str) -> str:
    if status == "candidate_ready_for_teacher_review":
        return "Candidate card created for teacher review only."
    if status == "held_for_more_evidence":
        return "Candidate card held for more evidence."
    return f"Candidate card blocked: {status}."


def _set_summary(status: str) -> str:
    if status == "candidate_set_created":
        return "ReviewedConcept readback hint candidate set created for teacher review."
    if status == "held_for_more_evidence":
        return "ReviewedConcept readback hint candidate set held for more evidence."
    return f"ReviewedConcept readback hint candidate set blocked: {status}."


def _task_note_for_priority(
    hint: ReviewedConceptWorkingReadbackHintPreview,
    hint_priority: int,
) -> str:
    if not hint.task_handling_notes:
        return ""
    return hint.task_handling_notes[(hint_priority - 1) % len(hint.task_handling_notes)]


def _warning_for_priority(items: tuple[str, ...], hint_priority: int) -> str | None:
    if not items:
        return None
    return items[(hint_priority - 1) % len(items)]


def _safety_blocked_reasons(
    *,
    readback_preview_valid: bool,
    hint_preview_valid: bool,
    candidate_set_valid: bool,
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
    if not readback_preview_valid:
        reasons.append("blocked_invalid_readback_preview")
    if not hint_preview_valid:
        reasons.append("blocked_invalid_hint_preview")
    if not candidate_set_valid:
        reasons.append("blocked_invalid_candidate_set")
    return tuple(dict.fromkeys(reasons))


def _safety_audit_status(blocked_reasons: tuple[str, ...]) -> str:
    if not blocked_reasons:
        return "passed"
    for status in (
        "blocked_forbidden_hint_creation_detected",
        "blocked_forbidden_working_memory_mutation_detected",
        "blocked_forbidden_behavior_change_detected",
        "blocked_forbidden_action_authority_detected",
        "blocked_forbidden_memory_write_detected",
        "blocked_invalid_readback_preview",
        "blocked_invalid_hint_preview",
        "blocked_invalid_candidate_set",
    ):
        if status in blocked_reasons:
            return status
    return "blocked_invalid_candidate_set"


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _readback_preview(
    record: ReviewedConceptWorkingReadbackPreview | dict[str, object],
) -> ReviewedConceptWorkingReadbackPreview:
    return (
        record
        if isinstance(record, ReviewedConceptWorkingReadbackPreview)
        else ReviewedConceptWorkingReadbackPreview.from_dict(dict(record))
    )


def _hint_preview(
    record: ReviewedConceptWorkingReadbackHintPreview | dict[str, object],
) -> ReviewedConceptWorkingReadbackHintPreview:
    return (
        record
        if isinstance(record, ReviewedConceptWorkingReadbackHintPreview)
        else ReviewedConceptWorkingReadbackHintPreview.from_dict(dict(record))
    )


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


def _safety_audit(
    record: ReviewedConceptReadbackHintCandidateSafetyAudit | dict[str, object],
) -> ReviewedConceptReadbackHintCandidateSafetyAudit:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackHintCandidateSafetyAudit)
        else ReviewedConceptReadbackHintCandidateSafetyAudit.from_dict(dict(record))
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
