"""ConceptCandidate schema and checker for Learning Engine v0."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any


SCHEMA_VERSION = "learning_engine_concept_candidate_v0"
SOURCE_ENGINE = "learning_engine"
CONCEPT_DEFINITION = (
    "Concept = a teacher-reviewed experience difference that changes future task "
    "handling and has passed counterexample-aware scope checks."
)
CONCEPT_DEFINITION_ZH = "概念 = 會改變下一次任務處理的、被審查過、且經過反例檢查的經驗差異。"
SAFE_CLAIM = (
    "ASHL Core v1 Learning Engine has a ConceptCandidate schema and checker that "
    "can represent support evidence, counterexample evidence, scope status, and "
    "refinement needs without extracting concepts, writing memory, or changing "
    "task behavior."
)
BLOCKED_CLAIMS = (
    "no_concept_extraction_runtime",
    "no_memory_write",
    "no_task_behavior_change",
    "no_teacher_review_decision",
    "no_concept_promotion",
    "no_core_longterm_archive_anchor_write",
)

ALLOWED_EVIDENCE_KINDS = {
    "support",
    "counterexample",
    "neutral_context",
    "needs_review",
}
ALLOWED_SCOPE_STATUSES = {
    "unknown",
    "narrow",
    "provisional",
    "broad",
    "overbroad_needs_split",
    "blocked_by_counterexample",
}
ALLOWED_GENERALIZATION_LEVELS = {
    "single_case",
    "same_context",
    "similar_context",
    "bounded_generalization_candidate",
    "overgeneralized",
}
ALLOWED_GENERALIZATION_STATUSES = {
    "not_generalized",
    "needs_more_support",
    "counterexample_check_required",
    "scope_narrowed",
    "split_required",
    "teacher_review_ready",
    "blocked",
}
ALLOWED_CANDIDATE_STATUSES = {
    "candidate",
    "needs_more_support",
    "blocked_by_counterexample",
    "scope_narrowed",
    "split_required",
    "teacher_review_ready",
    "reviewed",
    "retired",
    "invalid",
}
ALLOWED_COUNTEREXAMPLE_HANDLING_STATUSES = {
    "not_checked",
    "no_counterexamples",
    "counterexamples_present",
    "scope_narrowed",
    "split_required",
    "candidate_invalidated",
}
COUNTEREXAMPLE_REFINEMENT_STATUSES = {
    "scope_narrowed",
    "split_required",
    "blocked_by_counterexample",
}
COUNTEREXAMPLE_REFINEMENT_GENERALIZATION_STATUSES = {
    "scope_narrowed",
    "split_required",
    "blocked",
}
COUNTEREXAMPLE_REFINEMENT_HANDLING_STATUSES = {
    "scope_narrowed",
    "split_required",
    "candidate_invalidated",
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
class ConceptEvidenceRef:
    evidence_ref_id: str
    evidence_kind: str
    source_engine: str
    source_record_id: str
    source_task_id: str | None
    source_case_id: str | None
    source_tick_refs: tuple[str, ...]
    state_summary: str
    action_summary: str
    outcome_summary: str
    expected_outcome: str | None
    actual_outcome: str | None
    difference_label: str | None
    supports_candidate: bool
    counterexample_to_candidate: bool
    teacher_visible: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.evidence_kind not in ALLOWED_EVIDENCE_KINDS:
            raise ValueError(f"unknown evidence_kind: {self.evidence_kind}")
        object.__setattr__(
            self,
            "source_tick_refs",
            _tuple_of_str("source_tick_refs", self.source_tick_refs),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ConceptEvidenceRef":
        return cls(**dict(data))


@dataclass(frozen=True)
class ConceptScopeStatement:
    scope_id: str
    scope_text: str
    applies_when: tuple[str, ...]
    does_not_apply_when: tuple[str, ...]
    known_limits: tuple[str, ...]
    uncertainty_notes: tuple[str, ...]
    scope_confidence: float
    scope_status: str

    def __post_init__(self) -> None:
        if self.scope_status not in ALLOWED_SCOPE_STATUSES:
            raise ValueError(f"unknown scope_status: {self.scope_status}")
        object.__setattr__(
            self,
            "applies_when",
            _tuple_of_str("applies_when", self.applies_when),
        )
        object.__setattr__(
            self,
            "does_not_apply_when",
            _tuple_of_str("does_not_apply_when", self.does_not_apply_when),
        )
        object.__setattr__(
            self,
            "known_limits",
            _tuple_of_str("known_limits", self.known_limits),
        )
        object.__setattr__(
            self,
            "uncertainty_notes",
            _tuple_of_str("uncertainty_notes", self.uncertainty_notes),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ConceptScopeStatement":
        return cls(**dict(data))


@dataclass(frozen=True)
class ConceptCandidate:
    concept_candidate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    concept_label: str
    concept_summary: str
    source_task_ids: tuple[str, ...]
    source_case_ids: tuple[str, ...]
    source_state_action_outcome_refs: tuple[str, ...]
    support_evidence_refs: tuple[ConceptEvidenceRef, ...]
    counterexample_evidence_refs: tuple[ConceptEvidenceRef, ...]
    scope_statement: ConceptScopeStatement
    generalization_level: str
    generalization_status: str
    teacher_review_required: bool
    teacher_review_ready: bool
    memory_application_candidate_allowed: bool
    promotion_candidate_allowed: bool
    candidate_status: str
    counterexample_handling_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("schema_version must be learning_engine_concept_candidate_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be learning_engine")
        if self.generalization_level not in ALLOWED_GENERALIZATION_LEVELS:
            raise ValueError(f"unknown generalization_level: {self.generalization_level}")
        if self.generalization_status not in ALLOWED_GENERALIZATION_STATUSES:
            raise ValueError(f"unknown generalization_status: {self.generalization_status}")
        if self.candidate_status not in ALLOWED_CANDIDATE_STATUSES:
            raise ValueError(f"unknown candidate_status: {self.candidate_status}")
        if self.counterexample_handling_status not in ALLOWED_COUNTEREXAMPLE_HANDLING_STATUSES:
            raise ValueError(
                f"unknown counterexample_handling_status: {self.counterexample_handling_status}"
            )
        object.__setattr__(
            self,
            "source_task_ids",
            _tuple_of_str("source_task_ids", self.source_task_ids),
        )
        object.__setattr__(
            self,
            "source_case_ids",
            _tuple_of_str("source_case_ids", self.source_case_ids),
        )
        object.__setattr__(
            self,
            "source_state_action_outcome_refs",
            _tuple_of_str(
                "source_state_action_outcome_refs",
                self.source_state_action_outcome_refs,
            ),
        )
        object.__setattr__(
            self,
            "support_evidence_refs",
            tuple(self.support_evidence_refs),
        )
        object.__setattr__(
            self,
            "counterexample_evidence_refs",
            tuple(self.counterexample_evidence_refs),
        )
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
    def from_dict(cls, data: dict[str, object]) -> "ConceptCandidate":
        values = dict(data)
        values["support_evidence_refs"] = tuple(
            evidence
            if isinstance(evidence, ConceptEvidenceRef)
            else ConceptEvidenceRef.from_dict(dict(evidence))
            for evidence in values.get("support_evidence_refs", ())
        )
        values["counterexample_evidence_refs"] = tuple(
            evidence
            if isinstance(evidence, ConceptEvidenceRef)
            else ConceptEvidenceRef.from_dict(dict(evidence))
            for evidence in values.get("counterexample_evidence_refs", ())
        )
        if not isinstance(values.get("scope_statement"), ConceptScopeStatement):
            values["scope_statement"] = ConceptScopeStatement.from_dict(
                dict(values["scope_statement"])
            )
        return cls(**values)


@dataclass(frozen=True)
class ConceptCandidateValidationResult:
    valid: bool
    error_codes: tuple[str, ...]
    concept_candidate_id: str | None = None
    concept_label: str | None = None
    candidate_status: str | None = None
    counterexample_refinement_required: bool = False
    teacher_review_required: bool = True
    memory_application_candidate_allowed: bool = False
    promotion_candidate_allowed: bool = False
    safe_claim_candidate_only: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "error_codes",
            _tuple_of_str("error_codes", self.error_codes),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}


def validate_concept_evidence_ref(
    evidence: ConceptEvidenceRef | dict[str, object],
) -> dict[str, object]:
    try:
        record = (
            evidence
            if isinstance(evidence, ConceptEvidenceRef)
            else ConceptEvidenceRef.from_dict(dict(evidence))
        )
    except (TypeError, ValueError, KeyError) as error:
        return _validation_result(False, [f"invalid_evidence:{error}"]).to_dict()
    errors: list[str] = []
    if not record.evidence_ref_id:
        errors.append("missing_evidence_ref_id")
    if not record.source_record_id:
        errors.append("missing_source_record_id")
    if record.evidence_kind == "support" and record.supports_candidate is not True:
        errors.append("support_evidence_not_marked_supporting")
    if record.evidence_kind == "counterexample" and record.counterexample_to_candidate is not True:
        errors.append("counterexample_evidence_not_marked_counterexample")
    if record.supports_candidate and record.counterexample_to_candidate:
        errors.append("evidence_cannot_be_support_and_counterexample")
    if record.teacher_visible is not True:
        errors.append("teacher_visible_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "evidence_ref_id": record.evidence_ref_id,
        "evidence_kind": record.evidence_kind,
        "supports_candidate": record.supports_candidate,
        "counterexample_to_candidate": record.counterexample_to_candidate,
    }


def validate_concept_scope_statement(
    scope: ConceptScopeStatement | dict[str, object],
    *,
    counterexamples_present: bool = False,
) -> dict[str, object]:
    try:
        record = (
            scope
            if isinstance(scope, ConceptScopeStatement)
            else ConceptScopeStatement.from_dict(dict(scope))
        )
    except (TypeError, ValueError, KeyError) as error:
        return _validation_result(False, [f"invalid_scope:{error}"]).to_dict()
    errors: list[str] = []
    if not record.scope_id:
        errors.append("missing_scope_id")
    if not record.scope_text:
        errors.append("missing_scope_text")
    if record.scope_confidence < 0.0:
        errors.append("scope_confidence_below_zero")
    if record.scope_confidence > 1.0:
        errors.append("scope_confidence_above_one")
    if (
        counterexamples_present
        and record.scope_status == "broad"
    ):
        errors.append("broad_scope_with_counterexample_requires_refinement")
    return {
        "valid": not errors,
        "error_codes": errors,
        "scope_id": record.scope_id,
        "scope_status": record.scope_status,
        "scope_confidence": record.scope_confidence,
    }


def validate_concept_candidate(
    candidate: ConceptCandidate | dict[str, object],
) -> dict[str, object]:
    try:
        record = (
            candidate
            if isinstance(candidate, ConceptCandidate)
            else ConceptCandidate.from_dict(dict(candidate))
        )
    except (TypeError, ValueError, KeyError) as error:
        return _validation_result(False, [f"invalid_candidate:{error}"]).to_dict()
    errors: list[str] = []
    if not record.concept_candidate_id:
        errors.append("missing_concept_candidate_id")
    if not record.concept_label:
        errors.append("missing_concept_label")
    if not record.concept_summary:
        errors.append("missing_concept_summary")
    if not record.source_task_ids:
        errors.append("missing_source_task_ids")
    if not record.source_state_action_outcome_refs:
        errors.append("missing_source_state_action_outcome_refs")
    if not record.support_evidence_refs and record.candidate_status != "needs_more_support":
        errors.append("missing_support_evidence_refs")
    errors.extend(_evidence_errors(record.support_evidence_refs, "support"))
    errors.extend(_evidence_errors(record.counterexample_evidence_refs, "counterexample"))
    if _evidence_ids_overlap(record.support_evidence_refs, record.counterexample_evidence_refs):
        errors.append("support_counterexample_refs_overlap")
    scope_validation = validate_concept_scope_statement(
        record.scope_statement,
        counterexamples_present=bool(record.counterexample_evidence_refs),
    )
    errors.extend(f"scope:{code}" for code in scope_validation["error_codes"])
    if record.teacher_review_required is not True:
        errors.append("teacher_review_required_false")
    if record.memory_application_candidate_allowed is not False:
        errors.append("memory_application_candidate_allowed_true")
    if record.promotion_candidate_allowed is not False:
        errors.append("promotion_candidate_allowed_true")
    if not set(BLOCKED_CLAIMS).issubset(set(record.blocked_claims)):
        errors.append("blocked_claims_missing")
    safe_claim_lower = record.safe_claim.lower()
    if (
        "concept candidate" not in safe_claim_lower
        and "conceptcandidate" not in safe_claim_lower
    ) or "without extracting concepts" not in safe_claim_lower:
        errors.append("safe_claim_overclaims_or_missing_candidate_only")
    counterexamples_present = bool(record.counterexample_evidence_refs)
    if counterexamples_present and record.candidate_status not in COUNTEREXAMPLE_REFINEMENT_STATUSES:
        errors.append("counterexample_requires_refinement_candidate_status")
    if (
        counterexamples_present
        and record.generalization_status not in COUNTEREXAMPLE_REFINEMENT_GENERALIZATION_STATUSES
    ):
        errors.append("counterexample_requires_refinement_generalization_status")
    if (
        counterexamples_present
        and record.counterexample_handling_status not in COUNTEREXAMPLE_REFINEMENT_HANDLING_STATUSES
    ):
        errors.append("counterexample_requires_refinement_handling_status")
    result = ConceptCandidateValidationResult(
        valid=not errors,
        error_codes=tuple(errors),
        concept_candidate_id=record.concept_candidate_id,
        concept_label=record.concept_label,
        candidate_status=record.candidate_status,
        counterexample_refinement_required=counterexamples_present,
        teacher_review_required=record.teacher_review_required,
        memory_application_candidate_allowed=record.memory_application_candidate_allowed,
        promotion_candidate_allowed=record.promotion_candidate_allowed,
        safe_claim_candidate_only="ConceptCandidate schema and checker" in record.safe_claim,
    )
    return result.to_dict()


def build_demo_front_blocked_concept_candidate() -> ConceptCandidate:
    support = ConceptEvidenceRef(
        evidence_ref_id="concept_evidence:front_blocked_support_001",
        evidence_kind="support",
        source_engine="task_engine",
        source_record_id="task_run_closure:front_blocked_support_001",
        source_task_id="task:front_blocked_demo",
        source_case_id="blocked_front_obstacle",
        source_tick_refs=("tick:front_blocked:001",),
        state_summary="front_blocked",
        action_summary="step_forward",
        outcome_summary="blocked",
        expected_outcome="move_forward",
        actual_outcome="blocked",
        difference_label="expected_forward_but_blocked",
        supports_candidate=True,
        counterexample_to_candidate=False,
        teacher_visible=True,
        source_trace_refs=("task_run_closure:front_blocked_support_001",),
    )
    scope = ConceptScopeStatement(
        scope_id="concept_scope:front_blocked_affordance_v0",
        scope_text="Within the blocked_front_obstacle toy case, direct forward retry tends to stay blocked.",
        applies_when=("front_state=blocked", "action=step_forward"),
        does_not_apply_when=("front_state=unknown", "front_object=pushable_box"),
        known_limits=("single toy support case", "no real environment claim"),
        uncertainty_notes=("needs more support before broad use",),
        scope_confidence=0.45,
        scope_status="provisional",
    )
    return _candidate(
        concept_candidate_id="concept_candidate:front_blocked_affordance:v0",
        concept_label="front_blocked_affordance",
        concept_summary=(
            "Candidate that a front blocked state plus step_forward may produce a blocked outcome "
            "in the same toy context."
        ),
        support_evidence_refs=(support,),
        counterexample_evidence_refs=(),
        scope_statement=scope,
        generalization_level="same_context",
        generalization_status="needs_more_support",
        teacher_review_ready=False,
        candidate_status="needs_more_support",
        counterexample_handling_status="no_counterexamples",
    )


def build_demo_counterexample_split_required_candidate() -> ConceptCandidate:
    support = ConceptEvidenceRef(
        evidence_ref_id="concept_evidence:front_blocked_support_001",
        evidence_kind="support",
        source_engine="task_engine",
        source_record_id="task_run_closure:front_blocked_support_001",
        source_task_id="task:front_blocked_demo",
        source_case_id="blocked_front_obstacle",
        source_tick_refs=("tick:front_blocked:001",),
        state_summary="front_blocked",
        action_summary="step_forward",
        outcome_summary="blocked",
        expected_outcome="move_forward",
        actual_outcome="blocked",
        difference_label="expected_forward_but_blocked",
        supports_candidate=True,
        counterexample_to_candidate=False,
        teacher_visible=True,
        source_trace_refs=("task_run_closure:front_blocked_support_001",),
    )
    counterexample = ConceptEvidenceRef(
        evidence_ref_id="concept_evidence:front_blocked_counterexample_001",
        evidence_kind="counterexample",
        source_engine="task_engine",
        source_record_id="task_run_closure:front_blocked_counterexample_001",
        source_task_id="task:front_blocked_counterexample_demo",
        source_case_id="front_box_pushable",
        source_tick_refs=("tick:front_blocked:counterexample:001",),
        state_summary="front_blocked",
        action_summary="step_forward",
        outcome_summary="success",
        expected_outcome="blocked",
        actual_outcome="success",
        difference_label="front_blocked_can_be_pushable_or_temporary",
        supports_candidate=False,
        counterexample_to_candidate=True,
        teacher_visible=True,
        source_trace_refs=("task_run_closure:front_blocked_counterexample_001",),
    )
    scope = ConceptScopeStatement(
        scope_id="concept_scope:front_blocked_affordance_split_required_v0",
        scope_text=(
            "The label front_blocked is too broad; split into front_wall_blocked, "
            "front_box_pushable, front_temporary_blocked, or front_unknown_obstacle."
        ),
        applies_when=("front_state=blocked",),
        does_not_apply_when=("front_object=pushable_box", "temporary_block_removed=true"),
        known_limits=("counterexample present", "candidate must not be promoted as broad"),
        uncertainty_notes=("needs teacher review and narrower labels",),
        scope_confidence=0.35,
        scope_status="overbroad_needs_split",
    )
    return _candidate(
        concept_candidate_id="concept_candidate:front_blocked_affordance:split_required_v0",
        concept_label="front_blocked_affordance",
        concept_summary=(
            "Candidate remains present but must split because front_blocked + step_forward "
            "can produce both blocked and success outcomes."
        ),
        support_evidence_refs=(support,),
        counterexample_evidence_refs=(counterexample,),
        scope_statement=scope,
        generalization_level="same_context",
        generalization_status="split_required",
        teacher_review_ready=False,
        candidate_status="split_required",
        counterexample_handling_status="split_required",
    )


def summarize_concept_candidate(
    candidate: ConceptCandidate | dict[str, object],
) -> dict[str, object]:
    record = (
        candidate
        if isinstance(candidate, ConceptCandidate)
        else ConceptCandidate.from_dict(dict(candidate))
    )
    return {
        "concept_candidate_id": record.concept_candidate_id,
        "concept_label": record.concept_label,
        "candidate_status": record.candidate_status,
        "generalization_status": record.generalization_status,
        "support_evidence_count": len(record.support_evidence_refs),
        "counterexample_evidence_count": len(record.counterexample_evidence_refs),
        "scope_status": record.scope_statement.scope_status,
        "teacher_review_required": record.teacher_review_required,
        "memory_application_candidate_allowed": record.memory_application_candidate_allowed,
        "promotion_candidate_allowed": record.promotion_candidate_allowed,
    }


def _candidate(
    *,
    concept_candidate_id: str,
    concept_label: str,
    concept_summary: str,
    support_evidence_refs: tuple[ConceptEvidenceRef, ...],
    counterexample_evidence_refs: tuple[ConceptEvidenceRef, ...],
    scope_statement: ConceptScopeStatement,
    generalization_level: str,
    generalization_status: str,
    teacher_review_ready: bool,
    candidate_status: str,
    counterexample_handling_status: str,
) -> ConceptCandidate:
    return ConceptCandidate(
        concept_candidate_id=concept_candidate_id,
        schema_version=SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        concept_label=concept_label,
        concept_summary=concept_summary,
        source_task_ids=tuple(
            dict.fromkeys(
                evidence.source_task_id
                for evidence in (*support_evidence_refs, *counterexample_evidence_refs)
                if evidence.source_task_id
            )
        ),
        source_case_ids=tuple(
            dict.fromkeys(
                evidence.source_case_id
                for evidence in (*support_evidence_refs, *counterexample_evidence_refs)
                if evidence.source_case_id
            )
        ),
        source_state_action_outcome_refs=tuple(
            evidence.source_record_id
            for evidence in (*support_evidence_refs, *counterexample_evidence_refs)
        ),
        support_evidence_refs=support_evidence_refs,
        counterexample_evidence_refs=counterexample_evidence_refs,
        scope_statement=scope_statement,
        generalization_level=generalization_level,
        generalization_status=generalization_status,
        teacher_review_required=True,
        teacher_review_ready=teacher_review_ready,
        memory_application_candidate_allowed=False,
        promotion_candidate_allowed=False,
        candidate_status=candidate_status,
        counterexample_handling_status=counterexample_handling_status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        source_trace_refs=tuple(
            evidence.source_record_id
            for evidence in (*support_evidence_refs, *counterexample_evidence_refs)
        ),
    )


def _evidence_errors(
    evidence_refs: tuple[ConceptEvidenceRef, ...],
    expected_kind: str,
) -> list[str]:
    errors: list[str] = []
    for evidence in evidence_refs:
        validation = validate_concept_evidence_ref(evidence)
        if not validation["valid"]:
            errors.extend(f"{expected_kind}_evidence:{code}" for code in validation["error_codes"])
        if evidence.evidence_kind != expected_kind:
            errors.append(f"{expected_kind}_evidence_wrong_kind")
    return errors


def _evidence_ids_overlap(
    support_refs: tuple[ConceptEvidenceRef, ...],
    counterexample_refs: tuple[ConceptEvidenceRef, ...],
) -> bool:
    support_ids = {item.evidence_ref_id for item in support_refs}
    counterexample_ids = {item.evidence_ref_id for item in counterexample_refs}
    return bool(support_ids & counterexample_ids)


def _validation_result(
    valid: bool,
    error_codes: list[str],
) -> ConceptCandidateValidationResult:
    return ConceptCandidateValidationResult(valid=valid, error_codes=tuple(error_codes))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
