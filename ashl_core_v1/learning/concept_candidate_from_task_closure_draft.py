"""Draft ConceptCandidate records from deterministic task closure sources."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.concept_candidate_schema import (
    BLOCKED_CLAIMS,
    SAFE_CLAIM,
    SCHEMA_VERSION as CONCEPT_CANDIDATE_SCHEMA_VERSION,
    SOURCE_ENGINE as LEARNING_ENGINE,
    ConceptCandidate,
    ConceptEvidenceRef,
    ConceptScopeStatement,
    validate_concept_candidate,
)


SOURCE_SCHEMA_VERSION = "learning_engine_task_closure_concept_draft_source_v0"
DRAFT_SCHEMA_VERSION = "learning_engine_concept_candidate_draft_v0"
TEACHING_TEST_SCHEMA_VERSION = "learning_engine_simple_concept_teaching_test_seed_v0"
SOURCE_ENGINE = LEARNING_ENGINE

ALLOWED_DRAFT_BLOCKED_REASONS = {
    "none",
    "missing_task_id",
    "missing_case_id",
    "missing_closure",
    "missing_learning_candidate",
    "unknown_vs_unknown_not_valid",
    "no_state_action_outcome_difference",
    "unsupported_candidate_kind",
}
ALLOWED_DRAFT_STATUSES = {
    "draft_created",
    "blocked_invalid_source",
    "blocked_unknown_vs_unknown",
    "blocked_no_difference",
    "blocked_invalid_concept_candidate",
}
ALLOWED_TEACHING_TEST_STATUSES = {
    "seed_created",
    "blocked_missing_concept_candidate_draft",
    "blocked_invalid_concept_candidate_draft",
}
SUPPORTED_CANDIDATE_KINDS = {
    "blocked_front_obstacle",
    "repeated_blocked",
    "successful_path",
    "success_simple_reach",
    "unknown_resolved",
    "needs_observe",
    "expected_vs_actual_mismatch",
    "conflict_detected",
    "teacher_stopped",
    "suspended",
    "waiting_for_teacher",
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
class TaskClosureConceptDraftSourceRecord:
    draft_source_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_task_id: str
    source_case_id: str
    source_run_id: str | None
    source_closure_id: str | None
    source_learning_candidate_id: str | None
    task_status: str
    closure_status: str
    candidate_kind: str | None
    state_summary: str
    action_summary: str
    outcome_summary: str
    expected_outcome: str | None
    actual_outcome: str | None
    difference_label: str | None
    draftable_as_concept_candidate: bool
    draft_blocked_reason: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SOURCE_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_task_closure_concept_draft_source_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        reason = self.draft_blocked_reason or "none"
        if reason not in ALLOWED_DRAFT_BLOCKED_REASONS:
            raise ValueError(f"unknown draft_blocked_reason: {reason}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TaskClosureConceptDraftSourceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ConceptCandidateDraftRecord:
    concept_candidate_draft_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_draft_source_id: str
    source_task_id: str
    source_case_id: str
    source_closure_id: str | None
    source_learning_candidate_id: str | None
    drafted_concept_candidate: ConceptCandidate | None
    draft_status: str
    draft_summary: str
    teacher_review_required: bool
    teacher_review_ready: bool
    automatic_approval_created: bool
    memory_write_performed: bool
    task_behavior_changed: bool
    concept_extraction_runtime_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DRAFT_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_concept_candidate_draft_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.draft_status not in ALLOWED_DRAFT_STATUSES:
            raise ValueError(f"unknown draft_status: {self.draft_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ConceptCandidateDraftRecord":
        values = dict(data)
        candidate = values.get("drafted_concept_candidate")
        if candidate is not None and not isinstance(candidate, ConceptCandidate):
            values["drafted_concept_candidate"] = ConceptCandidate.from_dict(dict(candidate))
        return cls(**values)


@dataclass(frozen=True)
class SimpleConceptTeachingTestSeedRecord:
    teaching_test_seed_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_concept_candidate_draft_id: str
    teaching_test_name: str
    teaching_test_goal: str
    teacher_visible_prompt: str
    teacher_expected_questions: tuple[str, ...]
    teacher_possible_decisions: tuple[str, ...]
    support_case_summary: str
    counterexample_case_summary: str | None
    expected_teacher_focus: tuple[str, ...]
    test_status: str
    does_not_approve_concept: bool
    does_not_write_memory: bool
    does_not_change_task_behavior: bool
    does_not_create_review_decision: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TEACHING_TEST_SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_simple_concept_teaching_test_seed_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.test_status not in ALLOWED_TEACHING_TEST_STATUSES:
            raise ValueError(f"unknown test_status: {self.test_status}")
        object.__setattr__(
            self,
            "teacher_expected_questions",
            _tuple_of_str("teacher_expected_questions", self.teacher_expected_questions),
        )
        object.__setattr__(
            self,
            "teacher_possible_decisions",
            _tuple_of_str("teacher_possible_decisions", self.teacher_possible_decisions),
        )
        object.__setattr__(
            self,
            "expected_teacher_focus",
            _tuple_of_str("expected_teacher_focus", self.expected_teacher_focus),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SimpleConceptTeachingTestSeedRecord":
        return cls(**dict(data))


def build_task_closure_concept_draft_source(
    *,
    source_task_id: str,
    source_case_id: str,
    candidate_kind: str | None,
    state_summary: str,
    action_summary: str,
    outcome_summary: str,
    expected_outcome: str | None = None,
    actual_outcome: str | None = None,
    difference_label: str | None = None,
    source_run_id: str | None = None,
    source_closure_id: str | None = None,
    source_learning_candidate_id: str | None = None,
    task_status: str = "closed",
    closure_status: str = "closed",
    source_trace_refs: tuple[str, ...] = (),
) -> TaskClosureConceptDraftSourceRecord:
    reason = _draft_blocked_reason(
        source_task_id=source_task_id,
        source_case_id=source_case_id,
        source_closure_id=source_closure_id,
        source_learning_candidate_id=source_learning_candidate_id,
        candidate_kind=candidate_kind,
        expected_outcome=expected_outcome,
        actual_outcome=actual_outcome,
        difference_label=difference_label,
    )
    refs = source_trace_refs or tuple(
        ref
        for ref in (
            source_run_id,
            source_closure_id,
            source_learning_candidate_id,
        )
        if ref
    )
    return TaskClosureConceptDraftSourceRecord(
        draft_source_id=f"task_closure_concept_draft_source:{source_task_id}:{candidate_kind or 'none'}",
        schema_version=SOURCE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_task_id=source_task_id,
        source_case_id=source_case_id,
        source_run_id=source_run_id,
        source_closure_id=source_closure_id,
        source_learning_candidate_id=source_learning_candidate_id,
        task_status=task_status,
        closure_status=closure_status,
        candidate_kind=candidate_kind,
        state_summary=state_summary,
        action_summary=action_summary,
        outcome_summary=outcome_summary,
        expected_outcome=expected_outcome,
        actual_outcome=actual_outcome,
        difference_label=difference_label,
        draftable_as_concept_candidate=reason == "none",
        draft_blocked_reason=reason,
        source_trace_refs=refs,
    )


def draft_concept_candidate_from_task_closure_source(
    source: TaskClosureConceptDraftSourceRecord | dict[str, object],
) -> ConceptCandidateDraftRecord:
    source_record = _source(source)
    source_validation = validate_task_closure_concept_draft_source(source_record)
    if not source_validation["valid"]:
        return _blocked_draft(source_record, "blocked_invalid_source", source_validation["error_codes"])
    if source_record.draft_blocked_reason == "unknown_vs_unknown_not_valid":
        return _blocked_draft(source_record, "blocked_unknown_vs_unknown", ("unknown_vs_unknown_not_valid",))
    if source_record.draft_blocked_reason == "no_state_action_outcome_difference":
        return _blocked_draft(source_record, "blocked_no_difference", ("no_state_action_outcome_difference",))
    if source_record.draft_blocked_reason != "none":
        return _blocked_draft(source_record, "blocked_invalid_source", (source_record.draft_blocked_reason or "invalid_source",))

    candidate = _draft_concept_candidate(source_record)
    candidate_validation = validate_concept_candidate(candidate)
    if not candidate_validation["valid"]:
        return ConceptCandidateDraftRecord(
            concept_candidate_draft_id=f"concept_candidate_draft:{source_record.source_task_id}:blocked_invalid_candidate",
            schema_version=DRAFT_SCHEMA_VERSION,
            created_at=_now(),
            source_engine=SOURCE_ENGINE,
            source_draft_source_id=source_record.draft_source_id,
            source_task_id=source_record.source_task_id,
            source_case_id=source_record.source_case_id,
            source_closure_id=source_record.source_closure_id,
            source_learning_candidate_id=source_record.source_learning_candidate_id,
            drafted_concept_candidate=candidate,
            draft_status="blocked_invalid_concept_candidate",
            draft_summary="ConceptCandidate validation failed: "
            + ", ".join(str(code) for code in candidate_validation["error_codes"]),
            teacher_review_required=True,
            teacher_review_ready=False,
            automatic_approval_created=False,
            memory_write_performed=False,
            task_behavior_changed=False,
            concept_extraction_runtime_created=False,
            source_trace_refs=source_record.source_trace_refs,
        )
    return ConceptCandidateDraftRecord(
        concept_candidate_draft_id=f"concept_candidate_draft:{source_record.source_task_id}:{candidate.concept_label}",
        schema_version=DRAFT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_draft_source_id=source_record.draft_source_id,
        source_task_id=source_record.source_task_id,
        source_case_id=source_record.source_case_id,
        source_closure_id=source_record.source_closure_id,
        source_learning_candidate_id=source_record.source_learning_candidate_id,
        drafted_concept_candidate=candidate,
        draft_status="draft_created",
        draft_summary=(
            f"Drafted {candidate.concept_label} from task closure material; "
            "teacher review is still required."
        ),
        teacher_review_required=True,
        teacher_review_ready=candidate.teacher_review_ready,
        automatic_approval_created=False,
        memory_write_performed=False,
        task_behavior_changed=False,
        concept_extraction_runtime_created=False,
        source_trace_refs=source_record.source_trace_refs,
    )


def build_simple_concept_teaching_test_seed(
    draft: ConceptCandidateDraftRecord | dict[str, object],
) -> SimpleConceptTeachingTestSeedRecord:
    draft_record = _draft(draft)
    draft_validation = validate_concept_candidate_draft_record(draft_record)
    if not draft_validation["valid"] or draft_record.drafted_concept_candidate is None:
        return SimpleConceptTeachingTestSeedRecord(
            teaching_test_seed_id=f"concept_teaching_seed:{draft_record.concept_candidate_draft_id}:blocked",
            schema_version=TEACHING_TEST_SCHEMA_VERSION,
            created_at=_now(),
            source_engine=SOURCE_ENGINE,
            source_concept_candidate_draft_id=draft_record.concept_candidate_draft_id,
            teaching_test_name="blocked_concept_candidate_draft_seed",
            teaching_test_goal="Inspect why the concept candidate draft was blocked.",
            teacher_visible_prompt="This concept draft is blocked; inspect the source and do not approve it.",
            teacher_expected_questions=_teacher_questions(),
            teacher_possible_decisions=_teacher_decisions(),
            support_case_summary="none",
            counterexample_case_summary=None,
            expected_teacher_focus=_teacher_focus(),
            test_status="blocked_invalid_concept_candidate_draft",
            does_not_approve_concept=True,
            does_not_write_memory=True,
            does_not_change_task_behavior=True,
            does_not_create_review_decision=True,
            source_trace_refs=draft_record.source_trace_refs,
        )

    candidate = draft_record.drafted_concept_candidate
    support_summary = _support_summary(candidate)
    counterexample_summary = _counterexample_summary(candidate)
    return SimpleConceptTeachingTestSeedRecord(
        teaching_test_seed_id=f"concept_teaching_seed:{draft_record.concept_candidate_draft_id}",
        schema_version=TEACHING_TEST_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_concept_candidate_draft_id=draft_record.concept_candidate_draft_id,
        teaching_test_name=f"inspect_{candidate.concept_label}",
        teaching_test_goal=(
            "Ask the teacher whether this concept candidate should stay broad, "
            "narrow, split, gather more support, or move toward review readiness."
        ),
        teacher_visible_prompt=(
            "Is this concept candidate too broad? Should it be kept, narrowed, "
            "split, or given more evidence before teacher review?"
        ),
        teacher_expected_questions=_teacher_questions(),
        teacher_possible_decisions=_teacher_decisions(),
        support_case_summary=support_summary,
        counterexample_case_summary=counterexample_summary,
        expected_teacher_focus=_teacher_focus(),
        test_status="seed_created",
        does_not_approve_concept=True,
        does_not_write_memory=True,
        does_not_change_task_behavior=True,
        does_not_create_review_decision=True,
        source_trace_refs=draft_record.source_trace_refs,
    )


def validate_task_closure_concept_draft_source(
    source: TaskClosureConceptDraftSourceRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _source(source)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_source:{error}"]}
    errors: list[str] = []
    if not record.draft_source_id:
        errors.append("missing_draft_source_id")
    if not record.source_task_id:
        errors.append("missing_task_id")
    if not record.source_case_id:
        errors.append("missing_case_id")
    if not record.source_closure_id:
        errors.append("missing_closure")
    if not record.source_learning_candidate_id:
        errors.append("missing_learning_candidate")
    if record.candidate_kind not in SUPPORTED_CANDIDATE_KINDS:
        errors.append("unsupported_candidate_kind")
    if record.draftable_as_concept_candidate and record.draft_blocked_reason != "none":
        errors.append("draftable_source_has_blocked_reason")
    if not record.draftable_as_concept_candidate and record.draft_blocked_reason == "none":
        errors.append("blocked_source_missing_blocked_reason")
    if (
        record.draftable_as_concept_candidate
        and not record.difference_label
        and record.expected_outcome == record.actual_outcome
    ):
        errors.append("no_state_action_outcome_difference")
    return {
        "valid": not errors,
        "error_codes": errors,
        "draft_source_id": record.draft_source_id,
        "candidate_kind": record.candidate_kind,
        "draftable_as_concept_candidate": record.draftable_as_concept_candidate,
        "draft_blocked_reason": record.draft_blocked_reason,
    }


def validate_concept_candidate_draft_record(
    draft: ConceptCandidateDraftRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _draft(draft)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_draft:{error}"]}
    errors: list[str] = []
    if not record.concept_candidate_draft_id:
        errors.append("missing_concept_candidate_draft_id")
    if not record.source_draft_source_id:
        errors.append("missing_source_draft_source_id")
    if record.teacher_review_required is not True:
        errors.append("teacher_review_required_false")
    if record.automatic_approval_created is not False:
        errors.append("automatic_approval_created_true")
    if record.memory_write_performed is not False:
        errors.append("memory_write_performed_true")
    if record.task_behavior_changed is not False:
        errors.append("task_behavior_changed_true")
    if record.concept_extraction_runtime_created is not False:
        errors.append("concept_extraction_runtime_created_true")
    if record.draft_status == "draft_created":
        if record.drafted_concept_candidate is None:
            errors.append("missing_drafted_concept_candidate")
        else:
            candidate_validation = validate_concept_candidate(record.drafted_concept_candidate)
            errors.extend(
                f"concept_candidate:{code}" for code in candidate_validation["error_codes"]
            )
    return {
        "valid": not errors,
        "error_codes": errors,
        "concept_candidate_draft_id": record.concept_candidate_draft_id,
        "draft_status": record.draft_status,
        "teacher_review_required": record.teacher_review_required,
        "automatic_approval_created": record.automatic_approval_created,
        "memory_write_performed": record.memory_write_performed,
        "task_behavior_changed": record.task_behavior_changed,
        "concept_extraction_runtime_created": record.concept_extraction_runtime_created,
    }


def validate_simple_concept_teaching_test_seed(
    seed: SimpleConceptTeachingTestSeedRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = (
            seed
            if isinstance(seed, SimpleConceptTeachingTestSeedRecord)
            else SimpleConceptTeachingTestSeedRecord.from_dict(dict(seed))
        )
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_seed:{error}"]}
    errors: list[str] = []
    if not record.teaching_test_seed_id:
        errors.append("missing_teaching_test_seed_id")
    if not record.source_concept_candidate_draft_id:
        errors.append("missing_source_concept_candidate_draft_id")
    if "support evidence" not in " ".join(record.teacher_expected_questions).lower():
        errors.append("missing_support_evidence_question")
    if "counterexample" not in " ".join(record.teacher_expected_questions).lower():
        errors.append("missing_counterexample_question")
    if "too broad" not in record.teacher_visible_prompt.lower():
        errors.append("missing_overbroad_scope_prompt")
    if record.does_not_approve_concept is not True:
        errors.append("does_not_approve_concept_false")
    if record.does_not_write_memory is not True:
        errors.append("does_not_write_memory_false")
    if record.does_not_change_task_behavior is not True:
        errors.append("does_not_change_task_behavior_false")
    if record.does_not_create_review_decision is not True:
        errors.append("does_not_create_review_decision_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "teaching_test_seed_id": record.teaching_test_seed_id,
        "test_status": record.test_status,
        "does_not_approve_concept": record.does_not_approve_concept,
        "does_not_write_memory": record.does_not_write_memory,
        "does_not_change_task_behavior": record.does_not_change_task_behavior,
        "does_not_create_review_decision": record.does_not_create_review_decision,
    }


def build_demo_blocked_task_closure_source() -> TaskClosureConceptDraftSourceRecord:
    return build_task_closure_concept_draft_source(
        source_task_id="task:blocked_front_obstacle",
        source_case_id="blocked_front_obstacle",
        source_run_id="bounded_run:blocked_front_obstacle",
        source_closure_id="task_closure:blocked_front_obstacle",
        source_learning_candidate_id="learning_candidate:blocked_front_obstacle",
        task_status="failed",
        closure_status="closed",
        candidate_kind="blocked_front_obstacle",
        state_summary="front_blocked",
        action_summary="step_forward",
        outcome_summary="blocked",
        expected_outcome="move_forward",
        actual_outcome="blocked",
        difference_label="expected_forward_but_blocked",
    )


def build_demo_success_task_closure_source() -> TaskClosureConceptDraftSourceRecord:
    return build_task_closure_concept_draft_source(
        source_task_id="task:success_simple_reach",
        source_case_id="success_simple_reach",
        source_run_id="bounded_run:success_simple_reach",
        source_closure_id="task_closure:success_simple_reach",
        source_learning_candidate_id="learning_candidate:success_simple_reach",
        task_status="completed",
        closure_status="closed",
        candidate_kind="successful_path",
        state_summary="visible_front_item",
        action_summary="reach_front",
        outcome_summary="success",
        expected_outcome="success",
        actual_outcome="success",
        difference_label="successful_reach_path_observed",
    )


def build_demo_unknown_task_closure_source() -> TaskClosureConceptDraftSourceRecord:
    return build_task_closure_concept_draft_source(
        source_task_id="task:unknown_needs_observe",
        source_case_id="unknown_needs_observe",
        source_run_id="bounded_run:unknown_needs_observe",
        source_closure_id="task_closure:unknown_needs_observe",
        source_learning_candidate_id="learning_candidate:unknown_needs_observe",
        task_status="completed",
        closure_status="closed",
        candidate_kind="needs_observe",
        state_summary="unknown_front_state",
        action_summary="observe_or_adjust",
        outcome_summary="context_observed",
        expected_outcome="unknown",
        actual_outcome="context_observed",
        difference_label="unknown_resolved_by_observe",
    )


def build_demo_conflict_task_closure_source() -> TaskClosureConceptDraftSourceRecord:
    return build_task_closure_concept_draft_source(
        source_task_id="task:conflict_expected_vs_actual",
        source_case_id="conflict_expected_vs_actual",
        source_run_id="bounded_run:conflict_expected_vs_actual",
        source_closure_id="task_closure:conflict_expected_vs_actual",
        source_learning_candidate_id="learning_candidate:conflict_expected_vs_actual",
        task_status="failed",
        closure_status="closed",
        candidate_kind="expected_vs_actual_mismatch",
        state_summary="expected_path_available",
        action_summary="reuse_expected_path",
        outcome_summary="blocked",
        expected_outcome="success",
        actual_outcome="blocked",
        difference_label="expected_success_but_blocked",
    )


def build_demo_teacher_stopped_source() -> TaskClosureConceptDraftSourceRecord:
    return build_task_closure_concept_draft_source(
        source_task_id="task:teacher_stopped",
        source_case_id="teacher_stopped",
        source_run_id="bounded_run:teacher_stopped",
        source_closure_id="task_closure:teacher_stopped",
        source_learning_candidate_id="learning_candidate:teacher_stopped",
        task_status="teacher_stopped",
        closure_status="closed",
        candidate_kind="teacher_stopped",
        state_summary="teacher_stop_signal",
        action_summary="continue_task_attempt",
        outcome_summary="teacher_stopped",
        expected_outcome="continue",
        actual_outcome="teacher_stopped",
        difference_label="teacher_boundary_requires_stop",
    )


def build_demo_unknown_vs_unknown_blocked_source() -> TaskClosureConceptDraftSourceRecord:
    return build_task_closure_concept_draft_source(
        source_task_id="task:unknown_vs_unknown",
        source_case_id="unknown_needs_observe",
        source_run_id="bounded_run:unknown_vs_unknown",
        source_closure_id="task_closure:unknown_vs_unknown",
        source_learning_candidate_id="learning_candidate:unknown_vs_unknown",
        task_status="unknown",
        closure_status="closed",
        candidate_kind="needs_observe",
        state_summary="unknown_front_state",
        action_summary="unknown_action",
        outcome_summary="unknown",
        expected_outcome="unknown",
        actual_outcome="unknown",
        difference_label=None,
    )


def build_demo_draft(demo: str) -> ConceptCandidateDraftRecord:
    return draft_concept_candidate_from_task_closure_source(build_demo_source(demo))


def build_demo_teaching_test_seed(demo: str) -> SimpleConceptTeachingTestSeedRecord:
    return build_simple_concept_teaching_test_seed(build_demo_draft(demo))


def build_demo_source(demo: str) -> TaskClosureConceptDraftSourceRecord:
    builders = {
        "blocked": build_demo_blocked_task_closure_source,
        "success": build_demo_success_task_closure_source,
        "unknown": build_demo_unknown_task_closure_source,
        "conflict": build_demo_conflict_task_closure_source,
        "teacher-stopped": build_demo_teacher_stopped_source,
        "unknown-vs-unknown": build_demo_unknown_vs_unknown_blocked_source,
    }
    try:
        return builders[demo]()
    except KeyError as error:
        raise ValueError(f"unknown demo: {demo}") from error


def _draft_concept_candidate(source: TaskClosureConceptDraftSourceRecord) -> ConceptCandidate:
    mapping = _concept_mapping(source)
    support = ConceptEvidenceRef(
        evidence_ref_id=f"concept_evidence:{source.source_task_id}:{mapping['concept_label']}:support",
        evidence_kind="support",
        source_engine="task_engine",
        source_record_id=source.source_closure_id or source.draft_source_id,
        source_task_id=source.source_task_id,
        source_case_id=source.source_case_id,
        source_tick_refs=tuple(ref for ref in source.source_trace_refs if "tick" in ref),
        state_summary=source.state_summary,
        action_summary=source.action_summary,
        outcome_summary=source.outcome_summary,
        expected_outcome=source.expected_outcome,
        actual_outcome=source.actual_outcome,
        difference_label=source.difference_label,
        supports_candidate=True,
        counterexample_to_candidate=False,
        teacher_visible=True,
        source_trace_refs=source.source_trace_refs or (source.draft_source_id,),
    )
    scope = ConceptScopeStatement(
        scope_id=f"concept_scope:{mapping['concept_label']}:draft_v0",
        scope_text=str(mapping["scope_text"]),
        applies_when=tuple(mapping["applies_when"]),
        does_not_apply_when=tuple(mapping["does_not_apply_when"]),
        known_limits=(
            "deterministic demo source only",
            "not teacher approved",
            "not memory applicable",
            "no task behavior change",
        ),
        uncertainty_notes=("needs teacher inspection", "needs counterexample check"),
        scope_confidence=float(mapping["scope_confidence"]),
        scope_status=str(mapping["scope_status"]),
    )
    return ConceptCandidate(
        concept_candidate_id=f"concept_candidate:{mapping['concept_label']}:{source.source_task_id}:draft_v0",
        schema_version=CONCEPT_CANDIDATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        concept_label=str(mapping["concept_label"]),
        concept_summary=str(mapping["concept_summary"]),
        source_task_ids=(source.source_task_id,),
        source_case_ids=(source.source_case_id,),
        source_state_action_outcome_refs=(source.source_closure_id or source.draft_source_id,),
        support_evidence_refs=(support,),
        counterexample_evidence_refs=(),
        scope_statement=scope,
        generalization_level=str(mapping["generalization_level"]),
        generalization_status=str(mapping["generalization_status"]),
        teacher_review_required=True,
        teacher_review_ready=bool(mapping["teacher_review_ready"]),
        memory_application_candidate_allowed=False,
        promotion_candidate_allowed=False,
        candidate_status=str(mapping["candidate_status"]),
        counterexample_handling_status="no_counterexamples",
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        source_trace_refs=source.source_trace_refs or (source.draft_source_id,),
    )


def _concept_mapping(source: TaskClosureConceptDraftSourceRecord) -> dict[str, object]:
    kind = source.candidate_kind
    if kind in {"blocked_front_obstacle", "repeated_blocked"}:
        return {
            "concept_label": "front_blocked_affordance",
            "concept_summary": (
                "front blocked state tends to make direct forward movement fail"
            ),
            "scope_text": "In the blocked front obstacle toy case, direct forward movement tends to fail.",
            "applies_when": ("front_state=blocked", "action=step_forward"),
            "does_not_apply_when": ("front_state=unknown", "front_object=pushable"),
            "scope_confidence": 0.45,
            "scope_status": "provisional",
            "generalization_level": "same_context",
            "generalization_status": "needs_more_support",
            "candidate_status": "needs_more_support",
            "teacher_review_ready": False,
        }
    if kind in {"successful_path", "success_simple_reach"}:
        return {
            "concept_label": "visible_front_item_reachable",
            "concept_summary": (
                "visible reachable front item can be successfully reached in this bounded context"
            ),
            "scope_text": "In the success_simple_reach toy case, reach_front can succeed when the front item is visible.",
            "applies_when": ("front_item=visible", "action=reach_front"),
            "does_not_apply_when": ("front_state=blocked", "front_item=unknown"),
            "scope_confidence": 0.45,
            "scope_status": "provisional",
            "generalization_level": "same_context",
            "generalization_status": "needs_more_support",
            "candidate_status": "needs_more_support",
            "teacher_review_ready": False,
        }
    if kind in {"unknown_resolved", "needs_observe"}:
        return {
            "concept_label": "unknown_front_state_requires_observe",
            "concept_summary": (
                "unknown front state should be observed before direct retry in this bounded context"
            ),
            "scope_text": "When front state is unknown, observe_or_adjust can resolve local context before direct retry.",
            "applies_when": ("front_state=unknown", "action=observe_or_adjust"),
            "does_not_apply_when": ("front_state=known_clear",),
            "scope_confidence": 0.55,
            "scope_status": "provisional",
            "generalization_level": "same_context",
            "generalization_status": "teacher_review_ready",
            "candidate_status": "teacher_review_ready",
            "teacher_review_ready": True,
        }
    if kind in {"expected_vs_actual_mismatch", "conflict_detected"}:
        return {
            "concept_label": "expected_actual_mismatch_requires_verification",
            "concept_summary": (
                "mismatch between expected and actual outcome should trigger verification before reuse"
            ),
            "scope_text": "When expected and actual outcomes differ, verify before reusing the same handling path.",
            "applies_when": ("expected_outcome!=actual_outcome",),
            "does_not_apply_when": ("expected_outcome=actual_outcome",),
            "scope_confidence": 0.55,
            "scope_status": "provisional",
            "generalization_level": "same_context",
            "generalization_status": "teacher_review_ready",
            "candidate_status": "teacher_review_ready",
            "teacher_review_ready": True,
        }
    if kind in {"teacher_stopped", "suspended", "waiting_for_teacher"}:
        return {
            "concept_label": "teacher_boundary_requires_stop_or_wait",
            "concept_summary": (
                "teacher stop or wait signal should be treated as a boundary/control concept candidate"
            ),
            "scope_text": "Teacher stop or wait signals require stopping or waiting within teacher-gated control.",
            "applies_when": ("teacher_signal=stop_or_wait",),
            "does_not_apply_when": ("no_teacher_boundary_signal",),
            "scope_confidence": 0.4,
            "scope_status": "narrow",
            "generalization_level": "single_case",
            "generalization_status": "needs_more_support",
            "candidate_status": "needs_more_support",
            "teacher_review_ready": False,
        }
    raise ValueError(f"unsupported candidate kind: {kind}")


def _draft_blocked_reason(
    *,
    source_task_id: str,
    source_case_id: str,
    source_closure_id: str | None,
    source_learning_candidate_id: str | None,
    candidate_kind: str | None,
    expected_outcome: str | None,
    actual_outcome: str | None,
    difference_label: str | None,
) -> str:
    if not source_task_id:
        return "missing_task_id"
    if not source_case_id:
        return "missing_case_id"
    if not source_closure_id:
        return "missing_closure"
    if not source_learning_candidate_id:
        return "missing_learning_candidate"
    if candidate_kind not in SUPPORTED_CANDIDATE_KINDS:
        return "unsupported_candidate_kind"
    if expected_outcome == "unknown" and actual_outcome == "unknown":
        return "unknown_vs_unknown_not_valid"
    if not difference_label and expected_outcome == actual_outcome:
        return "no_state_action_outcome_difference"
    return "none"


def _blocked_draft(
    source: TaskClosureConceptDraftSourceRecord,
    status: str,
    reasons: tuple[str, ...] | list[str],
) -> ConceptCandidateDraftRecord:
    return ConceptCandidateDraftRecord(
        concept_candidate_draft_id=f"concept_candidate_draft:{source.source_task_id}:{status}",
        schema_version=DRAFT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_draft_source_id=source.draft_source_id,
        source_task_id=source.source_task_id,
        source_case_id=source.source_case_id,
        source_closure_id=source.source_closure_id,
        source_learning_candidate_id=source.source_learning_candidate_id,
        drafted_concept_candidate=None,
        draft_status=status,
        draft_summary="Draft blocked: " + ", ".join(str(reason) for reason in reasons),
        teacher_review_required=True,
        teacher_review_ready=False,
        automatic_approval_created=False,
        memory_write_performed=False,
        task_behavior_changed=False,
        concept_extraction_runtime_created=False,
        source_trace_refs=source.source_trace_refs,
    )


def _source(
    source: TaskClosureConceptDraftSourceRecord | dict[str, object],
) -> TaskClosureConceptDraftSourceRecord:
    return (
        source
        if isinstance(source, TaskClosureConceptDraftSourceRecord)
        else TaskClosureConceptDraftSourceRecord.from_dict(dict(source))
    )


def _draft(
    draft: ConceptCandidateDraftRecord | dict[str, object],
) -> ConceptCandidateDraftRecord:
    return (
        draft
        if isinstance(draft, ConceptCandidateDraftRecord)
        else ConceptCandidateDraftRecord.from_dict(dict(draft))
    )


def _teacher_questions() -> tuple[str, ...]:
    return (
        "What support evidence does this concept candidate have?",
        "Are there counterexample evidence cases?",
        "Does a counterexample invalidate it or show the scope is too broad?",
        "Should the candidate be kept, narrowed, split, or given more support?",
        "Can this candidate move toward teacher review readiness?",
    )


def _teacher_decisions() -> tuple[str, ...]:
    return (
        "needs_more_support",
        "scope_narrowed",
        "split_required",
        "teacher_review_ready",
        "blocked_by_counterexample",
    )


def _teacher_focus() -> tuple[str, ...]:
    return (
        "support_evidence",
        "counterexample_evidence",
        "scope_statement",
        "overbroad_scope",
        "split_or_more_support",
    )


def _support_summary(candidate: ConceptCandidate) -> str:
    if not candidate.support_evidence_refs:
        return "none"
    evidence = candidate.support_evidence_refs[0]
    return (
        f"{evidence.state_summary} + {evidence.action_summary} -> "
        f"{evidence.outcome_summary}"
    )


def _counterexample_summary(candidate: ConceptCandidate) -> str | None:
    if not candidate.counterexample_evidence_refs:
        return None
    evidence = candidate.counterexample_evidence_refs[0]
    return (
        f"{evidence.state_summary} + {evidence.action_summary} -> "
        f"{evidence.outcome_summary}"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
