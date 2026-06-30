"""Milestone audit for the reviewed-concept advisory readback loop."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.reviewed_concept_record import (
    build_demo_reviewed_concept_record,
)
from ashl_core_v1.memory.reviewed_concept_candidate_admission_review import (
    build_demo_reviewed_concept_memory_admission,
)
from ashl_core_v1.memory.reviewed_concept_readback_hint_candidate import (
    build_demo_reviewed_concept_readback_hint_candidate_set,
)
from ashl_core_v1.memory.reviewed_concept_readback_hint_preparation import (
    build_demo_reviewed_concept_readback_hint_preparation_set,
)
from ashl_core_v1.memory.reviewed_concept_readback_hint_teacher_review import (
    build_demo_reviewed_concept_readback_hint_teacher_review,
)
from ashl_core_v1.memory.reviewed_concept_working_readback_preview import (
    build_demo_reviewed_concept_working_readback_preview_bundle,
)
from ashl_core_v1.task.future_task_working_memory_readback_hint_application import (
    build_demo_future_task_working_memory_readback_hint_application_set,
)
from ashl_core_v1.task.readback_hint_influence_audit import (
    build_demo_candidate_ordering_changed_audit_report,
    build_demo_execution_created_audit_report,
    build_demo_missing_visible_hints_audit_report,
    build_demo_selected_action_changed_audit_report,
    build_demo_task_working_memory_readback_hint_influence_audit_report,
)
from ashl_core_v1.task.reviewed_concept_readback_hint_application_preparation import (
    build_demo_task_working_memory_readback_hint_application_preparation_set,
)
from ashl_core_v1.task.reviewed_concept_readback_hint_application_preview import (
    build_demo_task_working_memory_readback_hint_application_preview_set,
)
from ashl_core_v1.task.reviewed_concept_readback_hint_application_teacher_review import (
    build_demo_task_working_memory_readback_hint_application_teacher_review,
)
from ashl_core_v1.task.reviewed_concept_readback_hint_record import (
    build_demo_task_working_memory_readback_hint_record_set,
)


SOURCE_ENGINE = "milestone_audit"
EVIDENCE_CHAIN_SCHEMA_VERSION = "reviewed_concept_readback_loop_evidence_chain_v0"
BOUNDARY_AUDIT_SCHEMA_VERSION = "reviewed_concept_readback_loop_boundary_audit_v0"
MILESTONE_AUDIT_SCHEMA_VERSION = "reviewed_concept_readback_loop_milestone_audit_v0"
NEXT_STAGE_REPORT_SCHEMA_VERSION = (
    "reviewed_concept_readback_loop_next_stage_readiness_report_v0"
)
LOOP_NAME = "reviewed_concept_advisory_readback_loop"
LOOP_VERSION = "v0"

SAFE_CLAIM = (
    "ASHL Core v1 can milestone-audit the full ReviewedConcept advisory "
    "readback loop from ReviewedConcept through MemoryApplicationData, "
    "TaskWorkingMemoryReadbackHint, future Task Working Memory initialization, "
    "and influence audit, confirming the loop is complete, advisory-only, "
    "single-task, visible, and inert with no candidate ordering, behavior, "
    "action, execution, or memory-layer authority."
)
FORBIDDEN_CLAIMS = (
    "no_action_choice_from_reviewed_concepts",
    "no_behavior-changing_concept_readback",
    "no_autonomous_behavior_update_from_concepts",
    "no_persistent_cross_session_concept_growth",
    "no_core_longterm_archive_anchor_write",
)
REMAINING_MISSING_CAPABILITIES = (
    "candidate_ordering_influence",
    "candidate_ordering_change",
    "task_behavior_change",
    "automatic_learning_approval",
    "free_action_selection",
    "action_execution",
    "core_longterm_archive_anchor_write",
)

ALLOWED_CHAIN_STATUSES = {
    "chain_complete",
    "chain_incomplete_missing_learning_source",
    "chain_incomplete_missing_memory_records",
    "chain_incomplete_missing_hint_records",
    "chain_incomplete_missing_application_records",
    "chain_incomplete_missing_influence_audit",
    "blocked_invalid_lineage",
}
ALLOWED_BOUNDARY_STATUSES = {
    "passed_advisory_readback_only",
    "failed_candidate_ordering_change_detected",
    "failed_task_behavior_change_detected",
    "failed_action_authority_detected",
    "failed_running_task_mutation_detected",
    "failed_memory_layer_write_detected",
    "failed_automatic_learning_approval_detected",
    "blocked_invalid_evidence_chain",
}
ALLOWED_MILESTONE_STATUSES = {
    "passed_reviewed_concept_advisory_readback_loop_v0",
    "failed_incomplete_evidence_chain",
    "failed_boundary_audit",
    "failed_influence_audit",
    "blocked_invalid_source_records",
}
ALLOWED_READINESS_STATUSES = {
    "ready_for_candidate_ordering_influence_preview_only",
    "not_ready_missing_loop_evidence",
    "not_ready_boundary_failure",
    "not_ready_influence_audit_failure",
    "blocked_forbidden_authority_detected",
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
class ReviewedConceptReadbackLoopEvidenceChain:
    evidence_chain_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    reviewed_concept_record_id: str | None
    reviewed_concept_lineage_id: str | None
    reviewed_concept_safety_audit_id: str | None
    memory_learning_trace_id: str | None
    memory_routing_trace_id: str | None
    memory_application_data_id: str | None
    working_readback_preview_id: str | None
    readback_hint_candidate_set_id: str | None
    readback_hint_teacher_review_id: str | None
    readback_hint_preparation_set_id: str | None
    task_working_memory_readback_hint_record_set_id: str | None
    application_preview_set_id: str | None
    application_teacher_review_id: str | None
    application_preparation_set_id: str | None
    future_task_application_set_id: str | None
    future_task_readback_snapshot_id: str | None
    visibility_audit_id: str | None
    non_influence_audit_id: str | None
    influence_audit_report_id: str | None
    chain_complete: bool
    missing_links: tuple[str, ...]
    chain_status: str
    chain_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVIDENCE_CHAIN_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be reviewed_concept_readback_loop_evidence_chain_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be milestone_audit")
        if self.chain_status not in ALLOWED_CHAIN_STATUSES:
            raise ValueError(f"unknown chain_status: {self.chain_status}")
        for name in ("missing_links", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptReadbackLoopEvidenceChain":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptReadbackLoopBoundaryAudit:
    boundary_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_evidence_chain_id: str
    source_reviewed_concept_id: str
    working_memory_mutation_limited_to_new_task_initialization: bool
    advisory_only_confirmed: bool
    single_task_lifetime_confirmed: bool
    no_running_task_mutation: bool
    candidate_ordering_changed: bool
    task_behavior_changed: bool
    selected_action_changed: bool
    final_action_changed: bool
    direct_command_changed: bool
    execution_created: bool
    automatic_learning_approval_created: bool
    memory_layer_write_performed: bool
    core_memory_write_performed: bool
    long_term_memory_write_performed: bool
    archive_memory_write_performed: bool
    anchor_write_performed: bool
    boundary_status: str
    boundary_summary: str
    failed_boundaries: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BOUNDARY_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be reviewed_concept_readback_loop_boundary_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be milestone_audit")
        if self.boundary_status not in ALLOWED_BOUNDARY_STATUSES:
            raise ValueError(f"unknown boundary_status: {self.boundary_status}")
        for name in ("failed_boundaries", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptReadbackLoopBoundaryAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptReadbackLoopMilestoneAudit:
    milestone_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_reviewed_concept_id: str
    source_evidence_chain_id: str
    source_boundary_audit_id: str
    loop_name: str
    loop_version: str
    reviewed_concept_source_verified: bool
    memory_engine_records_verified: bool
    readback_hint_records_verified: bool
    future_task_working_memory_application_verified: bool
    influence_audit_verified: bool
    boundary_audit_verified: bool
    milestone_status: str
    milestone_summary: str
    safe_claim: str
    forbidden_claims: tuple[str, ...]
    remaining_missing_capabilities: tuple[str, ...]
    ready_for_next_stage_candidate_ordering_influence_preview: bool
    ready_for_behavior_change: bool
    ready_for_action_selection: bool
    ready_for_execution: bool
    ready_for_memory_layer_write: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MILESTONE_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be reviewed_concept_readback_loop_milestone_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be milestone_audit")
        if self.loop_name != LOOP_NAME:
            raise ValueError("loop_name must be reviewed_concept_advisory_readback_loop")
        if self.loop_version != LOOP_VERSION:
            raise ValueError("loop_version must be v0")
        if self.milestone_status not in ALLOWED_MILESTONE_STATUSES:
            raise ValueError(f"unknown milestone_status: {self.milestone_status}")
        for name in (
            "forbidden_claims",
            "remaining_missing_capabilities",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptReadbackLoopMilestoneAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedConceptReadbackLoopNextStageReadinessReport:
    next_stage_readiness_report_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_milestone_audit_id: str
    source_reviewed_concept_id: str
    current_verified_capability: str
    recommended_next_stage: str
    recommended_next_stage_reason: str
    candidate_ordering_influence_preview_allowed: bool
    candidate_ordering_change_allowed: bool
    task_behavior_change_allowed: bool
    action_selection_allowed: bool
    execution_allowed: bool
    memory_layer_write_allowed: bool
    required_next_stage_boundaries: tuple[str, ...]
    required_next_stage_tests: tuple[str, ...]
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != NEXT_STAGE_REPORT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be reviewed_concept_readback_loop_next_stage_readiness_report_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be milestone_audit")
        if self.readiness_status not in ALLOWED_READINESS_STATUSES:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        for name in (
            "required_next_stage_boundaries",
            "required_next_stage_tests",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "ReviewedConceptReadbackLoopNextStageReadinessReport":
        return cls(**dict(data))


def build_reviewed_concept_readback_loop_evidence_chain(
    *,
    source_records: dict[str, object],
) -> ReviewedConceptReadbackLoopEvidenceChain:
    ids = _extract_chain_ids(source_records)
    reviewed_refs = _reviewed_concept_refs(source_records, ids)
    invalid_lineage = len(set(reviewed_refs)) > 1
    missing_links = _missing_chain_links(ids)
    status = (
        "blocked_invalid_lineage"
        if invalid_lineage
        else _chain_status(missing_links)
    )
    source_reviewed_concept_id = (
        reviewed_refs[0]
        if reviewed_refs
        else "reviewed_concept:missing"
    )
    return ReviewedConceptReadbackLoopEvidenceChain(
        evidence_chain_id=(
            "reviewed_concept_readback_loop_evidence_chain:"
            f"{source_reviewed_concept_id}"
        ),
        schema_version=EVIDENCE_CHAIN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=source_reviewed_concept_id,
        chain_complete=status == "chain_complete",
        missing_links=missing_links,
        chain_status=status,
        chain_summary=_chain_summary(status, missing_links),
        source_trace_refs=_source_trace_refs(source_records),
        **ids,
    )


def validate_reviewed_concept_readback_loop_evidence_chain(
    evidence_chain: ReviewedConceptReadbackLoopEvidenceChain | dict[str, object],
) -> dict[str, object]:
    try:
        chain = _evidence_chain(evidence_chain)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_evidence_chain:{error}"]}
    errors: list[str] = []
    if chain.chain_status != "chain_complete":
        errors.append(chain.chain_status)
    if chain.chain_complete is not (chain.chain_status == "chain_complete"):
        errors.append("chain_complete_flag_mismatch")
    if chain.chain_status == "chain_complete" and chain.missing_links:
        errors.append("complete_chain_has_missing_links")
    return {
        "valid": not errors,
        "error_codes": errors,
        "evidence_chain_id": chain.evidence_chain_id,
        "chain_status": chain.chain_status,
        "missing_links": chain.missing_links,
    }


def build_reviewed_concept_readback_loop_boundary_audit(
    *,
    evidence_chain: ReviewedConceptReadbackLoopEvidenceChain | dict[str, object],
    source_records: dict[str, object],
) -> ReviewedConceptReadbackLoopBoundaryAudit:
    chain = _evidence_chain(evidence_chain)
    application_safety = _record(
        source_records,
        "future_application",
        "future_task_working_memory_readback_hint_application_safety_audit",
    )
    snapshot = _record(
        source_records,
        "future_application",
        "future_task_working_memory_initialization_readback_snapshot",
    )
    influence_report = _record(
        source_records,
        "influence_audit",
        "readback_hint_influence_audit_report",
    )
    mutation_limited = bool(
        application_safety.get(
            "working_memory_mutation_allowed_only_for_new_task_initialization",
            False,
        )
    )
    advisory_only = bool(
        snapshot.get("advisory_only", False)
        and influence_report.get("readback_hints_advisory_only", False)
    )
    single_task = bool(
        snapshot.get("single_task_lifetime", False)
        and influence_report.get("readback_hints_single_task_lifetime", False)
    )
    no_running = bool(application_safety.get("no_running_task_mutation", False))
    candidate_ordering_changed = bool(
        influence_report.get("candidate_ordering_changed", False)
    )
    task_behavior_changed = bool(
        influence_report.get("task_behavior_changed", False)
    )
    selected_action_changed = bool(
        influence_report.get("selected_action_changed", False)
    )
    final_action_changed = bool(influence_report.get("final_action_changed", False))
    direct_command_changed = bool(
        influence_report.get("direct_command_changed", False)
    )
    execution_created = bool(influence_report.get("execution_created", False))
    auto_learning = bool(
        influence_report.get("automatic_learning_approval_created", False)
    )
    memory_write = bool(influence_report.get("memory_layer_write_performed", False))
    core_write = bool(influence_report.get("core_memory_write_performed", False))
    long_write = bool(influence_report.get("long_term_memory_write_performed", False))
    archive_write = bool(influence_report.get("archive_memory_write_performed", False))
    anchor_write = bool(influence_report.get("anchor_write_performed", False))
    failed = _failed_boundaries(
        chain=chain,
        mutation_limited=mutation_limited,
        advisory_only=advisory_only,
        single_task=single_task,
        no_running=no_running,
        candidate_ordering_changed=candidate_ordering_changed,
        task_behavior_changed=task_behavior_changed,
        selected_action_changed=selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_changed=direct_command_changed,
        execution_created=execution_created,
        auto_learning=auto_learning,
        memory_write=memory_write,
        core_write=core_write,
        long_write=long_write,
        archive_write=archive_write,
        anchor_write=anchor_write,
    )
    status = _boundary_status(chain, failed)
    return ReviewedConceptReadbackLoopBoundaryAudit(
        boundary_audit_id=(
            "reviewed_concept_readback_loop_boundary_audit:"
            f"{chain.source_reviewed_concept_id}"
        ),
        schema_version=BOUNDARY_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_evidence_chain_id=chain.evidence_chain_id,
        source_reviewed_concept_id=chain.source_reviewed_concept_id,
        working_memory_mutation_limited_to_new_task_initialization=mutation_limited,
        advisory_only_confirmed=advisory_only,
        single_task_lifetime_confirmed=single_task,
        no_running_task_mutation=no_running,
        candidate_ordering_changed=candidate_ordering_changed,
        task_behavior_changed=task_behavior_changed,
        selected_action_changed=selected_action_changed,
        final_action_changed=final_action_changed,
        direct_command_changed=direct_command_changed,
        execution_created=execution_created,
        automatic_learning_approval_created=auto_learning,
        memory_layer_write_performed=memory_write,
        core_memory_write_performed=core_write,
        long_term_memory_write_performed=long_write,
        archive_memory_write_performed=archive_write,
        anchor_write_performed=anchor_write,
        boundary_status=status,
        boundary_summary=_boundary_summary(status),
        failed_boundaries=failed,
        blocked_reasons=(
            ("blocked_invalid_evidence_chain",)
            if status == "blocked_invalid_evidence_chain"
            else ()
        ),
        source_trace_refs=chain.source_trace_refs,
    )


def validate_reviewed_concept_readback_loop_boundary_audit(
    boundary_audit: ReviewedConceptReadbackLoopBoundaryAudit | dict[str, object],
) -> dict[str, object]:
    try:
        audit = _boundary_audit(boundary_audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_boundary_audit:{error}"]}
    errors: list[str] = []
    if audit.boundary_status != "passed_advisory_readback_only":
        errors.append(audit.boundary_status)
    if audit.failed_boundaries and audit.boundary_status == "passed_advisory_readback_only":
        errors.append("passed_boundary_has_failed_boundaries")
    for flag in (
        "working_memory_mutation_limited_to_new_task_initialization",
        "advisory_only_confirmed",
        "single_task_lifetime_confirmed",
        "no_running_task_mutation",
    ):
        if getattr(audit, flag) is not True:
            errors.append(f"{flag}_false")
    for flag in (
        "candidate_ordering_changed",
        "task_behavior_changed",
        "selected_action_changed",
        "final_action_changed",
        "direct_command_changed",
        "execution_created",
        "automatic_learning_approval_created",
        "memory_layer_write_performed",
        "core_memory_write_performed",
        "long_term_memory_write_performed",
        "archive_memory_write_performed",
        "anchor_write_performed",
    ):
        if getattr(audit, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "boundary_audit_id": audit.boundary_audit_id,
        "boundary_status": audit.boundary_status,
        "failed_boundaries": audit.failed_boundaries,
    }


def build_reviewed_concept_readback_loop_milestone_audit(
    *,
    evidence_chain: ReviewedConceptReadbackLoopEvidenceChain | dict[str, object],
    boundary_audit: ReviewedConceptReadbackLoopBoundaryAudit | dict[str, object],
    source_records: dict[str, object],
) -> ReviewedConceptReadbackLoopMilestoneAudit:
    chain = _evidence_chain(evidence_chain)
    boundary = _boundary_audit(boundary_audit)
    influence_report = _record(
        source_records,
        "influence_audit",
        "readback_hint_influence_audit_report",
    )
    influence_passed = (
        influence_report.get("audit_report_status") == "passed_visible_and_inert"
    )
    status = _milestone_status(chain, boundary, influence_passed)
    return ReviewedConceptReadbackLoopMilestoneAudit(
        milestone_audit_id=(
            "reviewed_concept_readback_loop_milestone_audit:"
            f"{chain.source_reviewed_concept_id}"
        ),
        schema_version=MILESTONE_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_reviewed_concept_id=chain.source_reviewed_concept_id,
        source_evidence_chain_id=chain.evidence_chain_id,
        source_boundary_audit_id=boundary.boundary_audit_id,
        loop_name=LOOP_NAME,
        loop_version=LOOP_VERSION,
        reviewed_concept_source_verified=_learning_source_complete(chain),
        memory_engine_records_verified=_memory_records_complete(chain),
        readback_hint_records_verified=_hint_records_complete(chain),
        future_task_working_memory_application_verified=_application_records_complete(
            chain
        ),
        influence_audit_verified=influence_passed,
        boundary_audit_verified=(
            boundary.boundary_status == "passed_advisory_readback_only"
        ),
        milestone_status=status,
        milestone_summary=_milestone_summary(status),
        safe_claim=SAFE_CLAIM,
        forbidden_claims=FORBIDDEN_CLAIMS,
        remaining_missing_capabilities=REMAINING_MISSING_CAPABILITIES,
        ready_for_next_stage_candidate_ordering_influence_preview=(
            status == "passed_reviewed_concept_advisory_readback_loop_v0"
        ),
        ready_for_behavior_change=False,
        ready_for_action_selection=False,
        ready_for_execution=False,
        ready_for_memory_layer_write=False,
        source_trace_refs=_combined_trace_refs(
            chain.source_trace_refs,
            boundary.source_trace_refs,
        ),
    )


def validate_reviewed_concept_readback_loop_milestone_audit(
    milestone_audit: ReviewedConceptReadbackLoopMilestoneAudit | dict[str, object],
) -> dict[str, object]:
    try:
        audit = _milestone_audit(milestone_audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_milestone_audit:{error}"]}
    errors: list[str] = []
    if audit.milestone_status != "passed_reviewed_concept_advisory_readback_loop_v0":
        errors.append(audit.milestone_status)
    if audit.ready_for_next_stage_candidate_ordering_influence_preview is not (
        audit.milestone_status == "passed_reviewed_concept_advisory_readback_loop_v0"
    ):
        errors.append("next_stage_preview_readiness_mismatch")
    for flag in (
        "ready_for_behavior_change",
        "ready_for_action_selection",
        "ready_for_execution",
        "ready_for_memory_layer_write",
    ):
        if getattr(audit, flag) is not False:
            errors.append(f"{flag}_true")
    if not set(FORBIDDEN_CLAIMS).issubset(set(audit.forbidden_claims)):
        errors.append("forbidden_claims_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "milestone_audit_id": audit.milestone_audit_id,
        "milestone_status": audit.milestone_status,
    }


def build_reviewed_concept_readback_loop_next_stage_readiness_report(
    *,
    milestone_audit: ReviewedConceptReadbackLoopMilestoneAudit | dict[str, object],
) -> ReviewedConceptReadbackLoopNextStageReadinessReport:
    milestone = _milestone_audit(milestone_audit)
    status = _readiness_status(milestone)
    preview_allowed = (
        status == "ready_for_candidate_ordering_influence_preview_only"
    )
    return ReviewedConceptReadbackLoopNextStageReadinessReport(
        next_stage_readiness_report_id=(
            "reviewed_concept_readback_loop_next_stage_readiness_report:"
            f"{milestone.source_reviewed_concept_id}"
        ),
        schema_version=NEXT_STAGE_REPORT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_milestone_audit_id=milestone.milestone_audit_id,
        source_reviewed_concept_id=milestone.source_reviewed_concept_id,
        current_verified_capability=(
            "complete advisory reviewed-concept readback loop"
        ),
        recommended_next_stage=(
            "Package 81 / ASHL Core v1 Task Engine Advisory Readback "
            "Candidate Ordering Influence Preview Minimal v0"
        ),
        recommended_next_stage_reason=(
            "The loop is visible and inert, so the next safe step is preview-only "
            "candidate ordering influence without changing ordering."
        ),
        candidate_ordering_influence_preview_allowed=preview_allowed,
        candidate_ordering_change_allowed=False,
        task_behavior_change_allowed=False,
        action_selection_allowed=False,
        execution_allowed=False,
        memory_layer_write_allowed=False,
        required_next_stage_boundaries=(
            "preview_only",
            "no_candidate_ordering_change",
            "no_selected_action_change",
            "no_final_action_change",
            "no_direct_command_change",
            "no_execution",
            "no_memory_layer_write",
        ),
        required_next_stage_tests=(
            "candidate_ordering_preview_does_not_change_order",
            "selected_action_unchanged",
            "final_action_unchanged",
            "direct_command_unchanged",
            "execution_not_created",
            "memory_layer_write_not_performed",
        ),
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=milestone.source_trace_refs,
    )


def validate_reviewed_concept_readback_loop_next_stage_readiness_report(
    report: ReviewedConceptReadbackLoopNextStageReadinessReport | dict[str, object],
) -> dict[str, object]:
    try:
        record = _next_stage_report(report)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": [f"invalid_readiness_report:{error}"]}
    errors: list[str] = []
    if (
        record.readiness_status
        != "ready_for_candidate_ordering_influence_preview_only"
    ):
        errors.append(record.readiness_status)
    if record.candidate_ordering_influence_preview_allowed is not (
        record.readiness_status
        == "ready_for_candidate_ordering_influence_preview_only"
    ):
        errors.append("preview_allowed_flag_mismatch")
    for flag in (
        "candidate_ordering_change_allowed",
        "task_behavior_change_allowed",
        "action_selection_allowed",
        "execution_allowed",
        "memory_layer_write_allowed",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "next_stage_readiness_report_id": record.next_stage_readiness_report_id,
        "readiness_status": record.readiness_status,
    }


def build_demo_reviewed_concept_readback_loop_milestone() -> dict[str, object]:
    return _build_milestone_bundle(_demo_source_records())


def build_demo_reviewed_concept_readback_loop_next_stage_readiness_report() -> (
    ReviewedConceptReadbackLoopNextStageReadinessReport
):
    payload = build_demo_reviewed_concept_readback_loop_milestone()
    return ReviewedConceptReadbackLoopNextStageReadinessReport.from_dict(
        payload["next_stage_readiness_report"]
    )


def build_demo_blocked_missing_reviewed_concept_milestone() -> dict[str, object]:
    records = _demo_source_records()
    records["reviewed_concept"]["reviewed_concept"] = {}
    return _build_milestone_bundle(records)


def build_demo_blocked_missing_memory_application_data_milestone() -> dict[str, object]:
    records = _demo_source_records()
    records["memory_admission"]["memory_application_data"] = {}
    return _build_milestone_bundle(records)


def build_demo_blocked_missing_hint_record_milestone() -> dict[str, object]:
    records = _demo_source_records()
    records["hint_record"]["task_working_memory_readback_hint_record_set"] = {}
    return _build_milestone_bundle(records)


def build_demo_blocked_missing_working_memory_application_milestone() -> dict[str, object]:
    records = _demo_source_records()
    records["future_application"]["future_task_readback_hint_application_set"] = {}
    records["future_application"][
        "future_task_working_memory_initialization_readback_snapshot"
    ] = {}
    return _build_milestone_bundle(records)


def build_demo_blocked_missing_influence_audit_milestone() -> dict[str, object]:
    records = _demo_source_records()
    records["influence_audit"]["readback_hint_influence_audit_report"] = {}
    return _build_milestone_bundle(records)


def build_demo_blocked_influence_audit_failure_milestone() -> dict[str, object]:
    records = _demo_source_records()
    records["influence_audit"] = build_demo_missing_visible_hints_audit_report()
    return _build_milestone_bundle(records)


def build_demo_blocked_candidate_ordering_changed_milestone() -> dict[str, object]:
    records = _demo_source_records()
    records["influence_audit"] = build_demo_candidate_ordering_changed_audit_report()
    return _build_milestone_bundle(records)


def build_demo_blocked_selected_action_changed_milestone() -> dict[str, object]:
    records = _demo_source_records()
    records["influence_audit"] = build_demo_selected_action_changed_audit_report()
    return _build_milestone_bundle(records)


def build_demo_blocked_execution_created_milestone() -> dict[str, object]:
    records = _demo_source_records()
    records["influence_audit"] = build_demo_execution_created_audit_report()
    return _build_milestone_bundle(records)


def build_demo_blocked_memory_layer_write_milestone() -> dict[str, object]:
    records = _demo_source_records()
    report = dict(records["influence_audit"]["readback_hint_influence_audit_report"])
    report["memory_layer_write_performed"] = True
    records["influence_audit"]["readback_hint_influence_audit_report"] = report
    return _build_milestone_bundle(records)


def build_demo_blocked_reviewed_concept_readback_loop_milestone(
    case: str,
) -> dict[str, object]:
    builders = {
        "missing-reviewed-concept": build_demo_blocked_missing_reviewed_concept_milestone,
        "missing-memory-application-data": (
            build_demo_blocked_missing_memory_application_data_milestone
        ),
        "missing-hint-record": build_demo_blocked_missing_hint_record_milestone,
        "missing-working-memory-application": (
            build_demo_blocked_missing_working_memory_application_milestone
        ),
        "missing-influence-audit": build_demo_blocked_missing_influence_audit_milestone,
        "influence-audit-failed": build_demo_blocked_influence_audit_failure_milestone,
        "candidate-ordering-changed": (
            build_demo_blocked_candidate_ordering_changed_milestone
        ),
        "selected-action-changed": build_demo_blocked_selected_action_changed_milestone,
        "execution-created": build_demo_blocked_execution_created_milestone,
        "memory-layer-write-detected": build_demo_blocked_memory_layer_write_milestone,
    }
    try:
        return builders[case]()
    except KeyError as error:
        raise ValueError(f"unknown readback loop milestone case: {case}") from error


def _build_milestone_bundle(source_records: dict[str, object]) -> dict[str, object]:
    chain = build_reviewed_concept_readback_loop_evidence_chain(
        source_records=source_records
    )
    boundary = build_reviewed_concept_readback_loop_boundary_audit(
        evidence_chain=chain,
        source_records=source_records,
    )
    milestone = build_reviewed_concept_readback_loop_milestone_audit(
        evidence_chain=chain,
        boundary_audit=boundary,
        source_records=source_records,
    )
    readiness = build_reviewed_concept_readback_loop_next_stage_readiness_report(
        milestone_audit=milestone,
    )
    return {
        "evidence_chain": chain.to_dict(),
        "boundary_audit": boundary.to_dict(),
        "milestone_audit": milestone.to_dict(),
        "next_stage_readiness_report": readiness.to_dict(),
        "evidence_chain_validation": (
            validate_reviewed_concept_readback_loop_evidence_chain(chain)
        ),
        "boundary_audit_validation": (
            validate_reviewed_concept_readback_loop_boundary_audit(boundary)
        ),
        "milestone_audit_validation": (
            validate_reviewed_concept_readback_loop_milestone_audit(milestone)
        ),
        "next_stage_readiness_report_validation": (
            validate_reviewed_concept_readback_loop_next_stage_readiness_report(
                readiness
            )
        ),
        "safe_claim": SAFE_CLAIM,
    }


def _demo_source_records() -> dict[str, object]:
    return {
        "reviewed_concept": build_demo_reviewed_concept_record(),
        "memory_admission": build_demo_reviewed_concept_memory_admission(),
        "working_readback": build_demo_reviewed_concept_working_readback_preview_bundle(),
        "hint_candidate": build_demo_reviewed_concept_readback_hint_candidate_set(),
        "hint_teacher_review": build_demo_reviewed_concept_readback_hint_teacher_review(),
        "hint_preparation": build_demo_reviewed_concept_readback_hint_preparation_set(),
        "hint_record": build_demo_task_working_memory_readback_hint_record_set(),
        "application_preview": build_demo_task_working_memory_readback_hint_application_preview_set(),
        "application_teacher_review": build_demo_task_working_memory_readback_hint_application_teacher_review(),
        "application_preparation": build_demo_task_working_memory_readback_hint_application_preparation_set(),
        "future_application": build_demo_future_task_working_memory_readback_hint_application_set(),
        "influence_audit": build_demo_task_working_memory_readback_hint_influence_audit_report(),
    }


def _extract_chain_ids(records: dict[str, object]) -> dict[str, str | None]:
    return {
        "reviewed_concept_record_id": _id(records, "reviewed_concept", "reviewed_concept", "reviewed_concept_id"),
        "reviewed_concept_lineage_id": _id(records, "reviewed_concept", "lineage_record", "lineage_id"),
        "reviewed_concept_safety_audit_id": _id(records, "reviewed_concept", "safety_audit", "safety_audit_id"),
        "memory_learning_trace_id": _id(records, "memory_admission", "memory_learning_trace", "memory_learning_trace_id"),
        "memory_routing_trace_id": _id(records, "memory_admission", "memory_routing_trace", "memory_routing_trace_id"),
        "memory_application_data_id": _id(records, "memory_admission", "memory_application_data", "memory_application_data_id"),
        "working_readback_preview_id": _id(records, "working_readback", "working_readback_preview", "working_readback_preview_id"),
        "readback_hint_candidate_set_id": _id(records, "hint_candidate", "hint_candidate_set", "hint_candidate_set_id"),
        "readback_hint_teacher_review_id": _id(records, "hint_teacher_review", "hint_candidate_set_teacher_review", "hint_candidate_set_teacher_review_id"),
        "readback_hint_preparation_set_id": _id(records, "hint_preparation", "readback_hint_preparation_set", "readback_hint_preparation_set_id"),
        "task_working_memory_readback_hint_record_set_id": _id(records, "hint_record", "task_working_memory_readback_hint_record_set", "task_working_memory_readback_hint_record_set_id"),
        "application_preview_set_id": _id(records, "application_preview", "task_working_memory_readback_hint_application_preview_set", "hint_application_preview_set_id"),
        "application_teacher_review_id": _id(records, "application_teacher_review", "hint_application_preview_set_teacher_review", "hint_application_preview_set_teacher_review_id"),
        "application_preparation_set_id": _id(records, "application_preparation", "hint_application_preparation_set", "hint_application_preparation_set_id"),
        "future_task_application_set_id": _id(records, "future_application", "future_task_readback_hint_application_set", "future_task_readback_hint_application_set_id"),
        "future_task_readback_snapshot_id": _id(records, "future_application", "future_task_working_memory_initialization_readback_snapshot", "readback_snapshot_id"),
        "visibility_audit_id": _id(records, "influence_audit", "readback_hint_visibility_audit", "visibility_audit_id"),
        "non_influence_audit_id": _id(records, "influence_audit", "readback_hint_non_influence_audit", "non_influence_audit_id"),
        "influence_audit_report_id": _id(records, "influence_audit", "readback_hint_influence_audit_report", "influence_audit_report_id"),
    }


def _missing_chain_links(ids: dict[str, str | None]) -> tuple[str, ...]:
    return tuple(key for key, value in ids.items() if not value)


def _chain_status(missing_links: tuple[str, ...]) -> str:
    if not missing_links:
        return "chain_complete"
    if any(link.startswith("reviewed_concept_") for link in missing_links):
        return "chain_incomplete_missing_learning_source"
    if any(link.startswith("memory_") for link in missing_links):
        return "chain_incomplete_missing_memory_records"
    if any(
        link
        in {
            "working_readback_preview_id",
            "readback_hint_candidate_set_id",
            "readback_hint_teacher_review_id",
            "readback_hint_preparation_set_id",
            "task_working_memory_readback_hint_record_set_id",
        }
        for link in missing_links
    ):
        return "chain_incomplete_missing_hint_records"
    if any(
        link
        in {
            "application_preview_set_id",
            "application_teacher_review_id",
            "application_preparation_set_id",
            "future_task_application_set_id",
            "future_task_readback_snapshot_id",
        }
        for link in missing_links
    ):
        return "chain_incomplete_missing_application_records"
    return "chain_incomplete_missing_influence_audit"


def _chain_summary(status: str, missing_links: tuple[str, ...]) -> str:
    if status == "chain_complete":
        return "Reviewed concept advisory readback loop evidence chain is complete."
    if status == "blocked_invalid_lineage":
        return "Evidence chain has inconsistent reviewed concept lineage."
    return f"Evidence chain incomplete: {', '.join(missing_links)}."


def _failed_boundaries(
    *,
    chain: ReviewedConceptReadbackLoopEvidenceChain,
    mutation_limited: bool,
    advisory_only: bool,
    single_task: bool,
    no_running: bool,
    candidate_ordering_changed: bool,
    task_behavior_changed: bool,
    selected_action_changed: bool,
    final_action_changed: bool,
    direct_command_changed: bool,
    execution_created: bool,
    auto_learning: bool,
    memory_write: bool,
    core_write: bool,
    long_write: bool,
    archive_write: bool,
    anchor_write: bool,
) -> tuple[str, ...]:
    failed: list[str] = []
    if not chain.chain_complete:
        failed.append("invalid_evidence_chain")
    if not (mutation_limited and no_running):
        failed.append("running_task_mutation")
    if not advisory_only:
        failed.append("not_advisory_only")
    if not single_task:
        failed.append("not_single_task_lifetime")
    if candidate_ordering_changed:
        failed.append("candidate_ordering_changed")
    if task_behavior_changed:
        failed.append("task_behavior_changed")
    if selected_action_changed:
        failed.append("selected_action_changed")
    if final_action_changed:
        failed.append("final_action_changed")
    if direct_command_changed:
        failed.append("direct_command_changed")
    if execution_created:
        failed.append("execution_created")
    if auto_learning:
        failed.append("automatic_learning_approval_created")
    if memory_write or core_write or long_write or archive_write or anchor_write:
        failed.append("memory_layer_write_performed")
    return tuple(dict.fromkeys(failed))


def _boundary_status(
    chain: ReviewedConceptReadbackLoopEvidenceChain,
    failed: tuple[str, ...],
) -> str:
    if not chain.chain_complete:
        return "blocked_invalid_evidence_chain"
    if "candidate_ordering_changed" in failed:
        return "failed_candidate_ordering_change_detected"
    if "task_behavior_changed" in failed:
        return "failed_task_behavior_change_detected"
    if any(
        item in failed
        for item in (
            "selected_action_changed",
            "final_action_changed",
            "direct_command_changed",
            "execution_created",
        )
    ):
        return "failed_action_authority_detected"
    if "running_task_mutation" in failed:
        return "failed_running_task_mutation_detected"
    if "memory_layer_write_performed" in failed:
        return "failed_memory_layer_write_detected"
    if "automatic_learning_approval_created" in failed:
        return "failed_automatic_learning_approval_detected"
    return "passed_advisory_readback_only"


def _boundary_summary(status: str) -> str:
    if status == "passed_advisory_readback_only":
        return "Loop boundary passed as advisory-only, single-task, visible and inert."
    return f"Loop boundary failed: {status}."


def _milestone_status(
    chain: ReviewedConceptReadbackLoopEvidenceChain,
    boundary: ReviewedConceptReadbackLoopBoundaryAudit,
    influence_passed: bool,
) -> str:
    if chain.chain_status != "chain_complete":
        return "failed_incomplete_evidence_chain"
    if boundary.boundary_status != "passed_advisory_readback_only":
        return "failed_boundary_audit"
    if not influence_passed:
        return "failed_influence_audit"
    return "passed_reviewed_concept_advisory_readback_loop_v0"


def _milestone_summary(status: str) -> str:
    if status == "passed_reviewed_concept_advisory_readback_loop_v0":
        return "ReviewedConcept advisory readback loop v0 milestone passed."
    return f"ReviewedConcept readback loop milestone failed: {status}."


def _readiness_status(
    milestone: ReviewedConceptReadbackLoopMilestoneAudit,
) -> str:
    if milestone.milestone_status == "passed_reviewed_concept_advisory_readback_loop_v0":
        return "ready_for_candidate_ordering_influence_preview_only"
    if milestone.milestone_status == "failed_incomplete_evidence_chain":
        return "not_ready_missing_loop_evidence"
    if milestone.milestone_status == "failed_boundary_audit":
        return "not_ready_boundary_failure"
    if milestone.milestone_status == "failed_influence_audit":
        return "not_ready_influence_audit_failure"
    return "blocked_forbidden_authority_detected"


def _readiness_summary(status: str) -> str:
    if status == "ready_for_candidate_ordering_influence_preview_only":
        return "Ready only for previewing candidate ordering influence; no ordering change allowed."
    return f"Next stage not ready: {status}."


def _learning_source_complete(chain: ReviewedConceptReadbackLoopEvidenceChain) -> bool:
    return all(
        (
            chain.reviewed_concept_record_id,
            chain.reviewed_concept_lineage_id,
            chain.reviewed_concept_safety_audit_id,
        )
    )


def _memory_records_complete(chain: ReviewedConceptReadbackLoopEvidenceChain) -> bool:
    return all(
        (
            chain.memory_learning_trace_id,
            chain.memory_routing_trace_id,
            chain.memory_application_data_id,
        )
    )


def _hint_records_complete(chain: ReviewedConceptReadbackLoopEvidenceChain) -> bool:
    return all(
        (
            chain.working_readback_preview_id,
            chain.readback_hint_candidate_set_id,
            chain.readback_hint_teacher_review_id,
            chain.readback_hint_preparation_set_id,
            chain.task_working_memory_readback_hint_record_set_id,
        )
    )


def _application_records_complete(chain: ReviewedConceptReadbackLoopEvidenceChain) -> bool:
    return all(
        (
            chain.application_preview_set_id,
            chain.application_teacher_review_id,
            chain.application_preparation_set_id,
            chain.future_task_application_set_id,
            chain.future_task_readback_snapshot_id,
        )
    )


def _reviewed_concept_refs(
    records: dict[str, object],
    ids: dict[str, str | None],
) -> tuple[str, ...]:
    refs: list[str] = []
    for value in ids.values():
        if value and "reviewed_concept:" in value:
            start = value.find("reviewed_concept:")
            refs.append(value[start:].split(":observe_before", 1)[0].split(":avoid_same", 1)[0])
    explicit = _id(records, "reviewed_concept", "reviewed_concept", "reviewed_concept_id")
    if explicit:
        refs.append(explicit)
    return tuple(dict.fromkeys(refs))


def _source_trace_refs(records: dict[str, object]) -> tuple[str, ...]:
    refs: list[str] = []
    for payload in records.values():
        if isinstance(payload, dict):
            for value in payload.values():
                if isinstance(value, dict):
                    refs.extend(str(item) for item in value.get("source_trace_refs", ()))
    return tuple(dict.fromkeys(refs))


def _id(
    records: dict[str, object],
    group: str,
    record_key: str,
    id_key: str,
) -> str | None:
    payload = records.get(group)
    if not isinstance(payload, dict):
        return None
    record = payload.get(record_key)
    if not isinstance(record, dict):
        return None
    value = record.get(id_key)
    return str(value) if value else None


def _record(records: dict[str, object], group: str, record_key: str) -> dict[str, object]:
    payload = records.get(group)
    if not isinstance(payload, dict):
        return {}
    record = payload.get(record_key)
    return dict(record) if isinstance(record, dict) else {}


def _evidence_chain(
    record: ReviewedConceptReadbackLoopEvidenceChain | dict[str, object],
) -> ReviewedConceptReadbackLoopEvidenceChain:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackLoopEvidenceChain)
        else ReviewedConceptReadbackLoopEvidenceChain.from_dict(dict(record))
    )


def _boundary_audit(
    record: ReviewedConceptReadbackLoopBoundaryAudit | dict[str, object],
) -> ReviewedConceptReadbackLoopBoundaryAudit:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackLoopBoundaryAudit)
        else ReviewedConceptReadbackLoopBoundaryAudit.from_dict(dict(record))
    )


def _milestone_audit(
    record: ReviewedConceptReadbackLoopMilestoneAudit | dict[str, object],
) -> ReviewedConceptReadbackLoopMilestoneAudit:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackLoopMilestoneAudit)
        else ReviewedConceptReadbackLoopMilestoneAudit.from_dict(dict(record))
    )


def _next_stage_report(
    record: ReviewedConceptReadbackLoopNextStageReadinessReport | dict[str, object],
) -> ReviewedConceptReadbackLoopNextStageReadinessReport:
    return (
        record
        if isinstance(record, ReviewedConceptReadbackLoopNextStageReadinessReport)
        else ReviewedConceptReadbackLoopNextStageReadinessReport.from_dict(dict(record))
    )


def _combined_trace_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group if item))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
