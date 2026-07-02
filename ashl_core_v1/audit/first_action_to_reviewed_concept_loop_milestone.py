"""Milestone audit for the first action-to-ReviewedConcept-to-next-task loop."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.audit.feedback_reviewed_concept_closed_loop_replay import (
    build_demo_blocked_feedback_reviewed_concept_closed_loop_replay,
    build_demo_negative_affordance_closed_loop_replay,
    build_demo_visible_no_action_difference_replay,
)


SOURCE_ENGINE = "milestone_audit"
EVIDENCE_SCHEMA_VERSION = "first_action_to_reviewed_concept_loop_evidence_chain_v0"
BOUNDARY_SCHEMA_VERSION = "first_action_to_reviewed_concept_loop_boundary_audit_v0"
REPLAY_VERIFICATION_SCHEMA_VERSION = (
    "first_action_to_reviewed_concept_loop_replay_verification_v0"
)
MILESTONE_SCHEMA_VERSION = (
    "first_action_to_reviewed_concept_to_next_task_loop_milestone_v0"
)
READINESS_SCHEMA_VERSION = "first_closed_loop_next_stage_readiness_v0"

MILESTONE_NAME = "first_bounded_action_to_reviewed_concept_to_next_task_loop"
MILESTONE_VERSION = "v0"
PASSED_MILESTONE_STATUS = (
    "passed_first_bounded_action_to_reviewed_concept_to_next_task_loop_v0"
)
VISIBLE_NO_DIFFERENCE_MILESTONE_STATUS = "passed_replay_visible_no_action_difference"
PASSED_REPLAY_AUDIT_STATUSES = {
    "passed_feedback_reviewed_concept_closed_loop_replay",
    "passed_feedback_readback_visible_no_action_difference",
}

SAFE_CLAIM = (
    "ASHL Core v1 has demonstrated a bounded teacher-gated "
    "action-to-feedback-derived-ReviewedConcept-to-next-task replay loop v0."
)
FORBIDDEN_CLAIMS = (
    "no_autonomous_learning",
    "no_automatic_learning_approval",
    "no_long_term_memory_write",
    "no_free_action_selection",
    "no_external_execution",
    "no_thought_engine_cognition",
    "no_persistent_cross_session_growth",
)
REMAINING_MISSING_CAPABILITIES = (
    "recursive_learning_without_teacher_gate",
    "memory_promotion",
    "long_term_memory_write",
    "automatic_learning_approval",
    "free_action_selection",
    "external_execution",
    "autonomous_scheduler",
    "thought_engine_cognition",
)
RECOMMENDED_NEXT_STAGE = (
    "Package 95 / ASHL Core v1 Bounded Multi-Trial Feedback Loop Planning Minimal v0"
)

ALLOWED_EVIDENCE_STATUSES = {
    "chain_complete",
    "chain_incomplete_missing_first_action_path",
    "chain_incomplete_missing_sense_task_path",
    "chain_incomplete_missing_learning_feedback_path",
    "chain_incomplete_missing_reviewed_concept_path",
    "chain_incomplete_missing_replay_path",
    "blocked_invalid_trace_lineage",
}
ALLOWED_BOUNDARY_STATUSES = {
    "passed_bounded_teacher_gated_loop_boundaries",
    "failed_external_execution_detected",
    "failed_memory_layer_write_detected",
    "failed_automatic_learning_approval_detected",
    "failed_behavior_learning_detected",
    "failed_recursive_learning_detected",
    "failed_free_action_selection_detected",
    "blocked_invalid_evidence_chain",
}
ALLOWED_REPLAY_VERIFICATION_STATUSES = {
    "replay_verified_with_action_chain_influence",
    "replay_verified_visible_no_action_difference",
    "blocked_missing_feedback_reviewed_concept",
    "blocked_missing_readback_seed",
    "blocked_missing_second_task_replay",
    "blocked_invalid_replay_audit",
}
ALLOWED_MILESTONE_STATUSES = {
    PASSED_MILESTONE_STATUS,
    VISIBLE_NO_DIFFERENCE_MILESTONE_STATUS,
    "failed_incomplete_evidence_chain",
    "failed_boundary_audit",
    "failed_replay_verification",
    "blocked_invalid_source_records",
}
ALLOWED_READINESS_STATUSES = {
    "ready_for_bounded_multi_trial_loop_preview_only",
    "ready_for_recursive_replay_planning_only",
    "not_ready_missing_closed_loop_evidence",
    "not_ready_boundary_failure",
    "blocked_forbidden_authority_detected",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def _combined_trace_refs(*refs: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    combined: list[str] = []
    for group in refs:
        if not group:
            continue
        for item in group:
            if item not in combined:
                combined.append(str(item))
    return tuple(combined)


@dataclass(frozen=True)
class FirstClosedLoopEvidenceChainRecord:
    evidence_chain_id: str
    schema_version: str
    created_at: str
    source_engine: str
    first_task_selected_action_id: str | None
    first_task_final_action_id: str | None
    first_task_direct_command_id: str | None
    first_task_sandbox_execution_id: str | None
    first_task_execution_audit_id: str | None
    sense_observation_id: str | None
    sense_handoff_id: str | None
    outcome_evaluation_id: str | None
    goal_delta_evaluation_id: str | None
    task_closure_id: str | None
    learning_feedback_candidate_id: str | None
    learning_feedback_evidence_packet_id: str | None
    concept_candidate_draft_id: str | None
    feedback_refinement_id: str | None
    feedback_scope_check_id: str | None
    feedback_counterexample_check_id: str | None
    feedback_derived_reviewed_concept_id: str | None
    working_readback_integration_id: str | None
    readback_seed_id: str | None
    replay_gate_id: str | None
    replay_task_initialization_id: str | None
    replay_action_chain_id: str | None
    replay_execution_id: str | None
    replay_outcome_id: str | None
    replay_contrast_id: str | None
    replay_audit_id: str | None
    chain_complete: bool
    missing_links: tuple[str, ...]
    evidence_chain_status: str
    evidence_chain_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVIDENCE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be first_action_to_reviewed_concept_loop_evidence_chain_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be milestone_audit")
        if self.evidence_chain_status not in ALLOWED_EVIDENCE_STATUSES:
            raise ValueError(
                f"unknown evidence_chain_status: {self.evidence_chain_status}"
            )
        for name in ("missing_links", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FirstClosedLoopEvidenceChainRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FirstClosedLoopBoundaryAuditRecord:
    boundary_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_evidence_chain_id: str
    bounded_sandbox_only_confirmed: bool
    teacher_gated_path_confirmed: bool
    working_readback_only_confirmed: bool
    single_task_readback_scope_confirmed: bool
    no_external_execution: bool
    no_unity_execution: bool
    no_bridge_execution: bool
    no_network_execution: bool
    no_filesystem_execution: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_automatic_learning_approval: bool
    no_behavior_learning: bool
    no_free_action_selection: bool
    no_scheduler: bool
    no_open_ended_loop: bool
    no_recursive_learning_from_replay: bool
    no_new_reviewed_concept_from_replay: bool
    boundary_status: str
    boundary_summary: str
    failed_boundaries: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BOUNDARY_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be first_action_to_reviewed_concept_loop_boundary_audit_v0"
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
    def from_dict(cls, data: dict[str, object]) -> "FirstClosedLoopBoundaryAuditRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FirstClosedLoopReplayVerificationRecord:
    replay_verification_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_evidence_chain_id: str
    source_replay_audit_id: str | None
    source_replay_contrast_id: str | None
    feedback_reviewed_concept_used: bool
    working_readback_seed_used: bool
    second_task_initialized: bool
    readback_hint_visible_in_second_task: bool
    second_task_action_chain_replayed: bool
    second_task_bounded_execution_completed: bool
    second_task_outcome_closed: bool
    candidate_ordering_influenced: bool
    selected_action_replayed: bool
    final_action_replayed: bool
    direct_command_replayed: bool
    visible_no_action_difference: bool
    replay_verification_status: str
    replay_verification_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REPLAY_VERIFICATION_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be first_action_to_reviewed_concept_loop_replay_verification_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be milestone_audit")
        if self.replay_verification_status not in ALLOWED_REPLAY_VERIFICATION_STATUSES:
            raise ValueError(
                "unknown replay_verification_status: "
                f"{self.replay_verification_status}"
            )
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
    ) -> "FirstClosedLoopReplayVerificationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FirstClosedLoopMilestoneRecord:
    milestone_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_evidence_chain_id: str
    source_boundary_audit_id: str
    source_replay_verification_id: str
    milestone_name: str
    milestone_version: str
    first_action_path_verified: bool
    sense_task_evaluation_verified: bool
    learning_feedback_candidate_verified: bool
    feedback_concept_candidate_refinement_verified: bool
    feedback_reviewed_concept_verified: bool
    working_readback_integration_verified: bool
    second_task_replay_verified: bool
    boundary_audit_verified: bool
    milestone_status: str
    milestone_summary: str
    safe_claim: str
    forbidden_claims: tuple[str, ...]
    remaining_missing_capabilities: tuple[str, ...]
    recommended_next_stage: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != MILESTONE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be first_action_to_reviewed_concept_to_next_task_loop_milestone_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be milestone_audit")
        if self.milestone_name != MILESTONE_NAME:
            raise ValueError(
                "milestone_name must be first_bounded_action_to_reviewed_concept_to_next_task_loop"
            )
        if self.milestone_version != MILESTONE_VERSION:
            raise ValueError("milestone_version must be v0")
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
    def from_dict(cls, data: dict[str, object]) -> "FirstClosedLoopMilestoneRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FirstClosedLoopNextStageReadinessRecord:
    next_stage_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_milestone_id: str
    current_verified_capability: str
    recommended_next_stage: str
    recommended_next_stage_reason: str
    ready_for_recursive_replay_planning: bool
    ready_for_bounded_multi_trial_loop_preview: bool
    ready_for_memory_promotion: bool
    ready_for_long_term_memory: bool
    ready_for_autonomous_scheduler: bool
    ready_for_free_action_selection: bool
    ready_for_external_execution: bool
    ready_for_thought_engine: bool
    required_next_boundaries: tuple[str, ...]
    required_next_tests: tuple[str, ...]
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READINESS_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be first_closed_loop_next_stage_readiness_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be milestone_audit")
        if self.readiness_status not in ALLOWED_READINESS_STATUSES:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        for name in ("required_next_boundaries", "required_next_tests", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "FirstClosedLoopNextStageReadinessRecord":
        return cls(**dict(data))


def build_first_closed_loop_evidence_chain_record(
    *,
    replay_payload: dict[str, object],
    missing_links: tuple[str, ...] | list[str] = (),
    created_at: str | None = None,
) -> FirstClosedLoopEvidenceChainRecord:
    data = _extract_evidence(replay_payload)
    missing = list(missing_links)
    for link_name, field_names in _REQUIRED_LINK_GROUPS:
        for field_name in field_names:
            if not data.get(field_name) and link_name not in missing:
                missing.append(link_name)
    status = _evidence_status(missing)
    chain_complete = not missing
    return FirstClosedLoopEvidenceChainRecord(
        evidence_chain_id="first_closed_loop_evidence_chain:package_85_93_demo",
        schema_version=EVIDENCE_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        chain_complete=chain_complete,
        missing_links=tuple(missing),
        evidence_chain_status=status,
        evidence_chain_summary=_evidence_summary(status, missing),
        source_trace_refs=_collect_trace_refs(replay_payload),
        **data,
    )


def validate_first_closed_loop_evidence_chain_record(
    evidence_chain: FirstClosedLoopEvidenceChainRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _evidence(evidence_chain)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_evidence_chain:{error}",)}
    errors: list[str] = []
    if record.chain_complete != (not record.missing_links):
        errors.append("chain_complete_mismatch")
    if record.chain_complete and record.evidence_chain_status != "chain_complete":
        errors.append("complete_chain_status_mismatch")
    if not record.chain_complete and record.evidence_chain_status == "chain_complete":
        errors.append("incomplete_chain_status_mismatch")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "evidence_chain_id": record.evidence_chain_id,
        "evidence_chain_status": record.evidence_chain_status,
        "missing_links": record.missing_links,
    }


def build_first_closed_loop_boundary_audit_record(
    *,
    evidence_chain: FirstClosedLoopEvidenceChainRecord | dict[str, object],
    replay_payload: dict[str, object] | None = None,
    external_execution_created: bool = False,
    unity_execution_created: bool = False,
    bridge_execution_created: bool = False,
    network_execution_created: bool = False,
    filesystem_execution_created: bool = False,
    core_memory_write_performed: bool = False,
    long_term_memory_write_performed: bool = False,
    archive_memory_write_performed: bool = False,
    anchor_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    behavior_learning_created: bool = False,
    recursive_learning_from_replay_created: bool = False,
    new_reviewed_concept_from_replay_created: bool = False,
    free_action_selection_created: bool = False,
    scheduler_created: bool = False,
    open_ended_loop_created: bool = False,
    created_at: str | None = None,
) -> FirstClosedLoopBoundaryAuditRecord:
    chain = _evidence(evidence_chain)
    replay_audit = (
        dict(replay_payload.get("feedback_reviewed_concept_closed_loop_replay_audit", {}))
        if replay_payload
        else {}
    )
    no_external = not (
        external_execution_created
        or unity_execution_created
        or bridge_execution_created
        or network_execution_created
        or filesystem_execution_created
        or replay_audit.get("no_external_execution") is False
        or replay_audit.get("no_unity_execution") is False
        or replay_audit.get("no_bridge_execution") is False
        or replay_audit.get("no_network_execution") is False
        or replay_audit.get("no_filesystem_execution") is False
    )
    no_memory = not (
        core_memory_write_performed
        or long_term_memory_write_performed
        or archive_memory_write_performed
        or anchor_write_performed
        or replay_audit.get("no_memory_write") is False
    )
    no_recursive = not (
        recursive_learning_from_replay_created
        or replay_audit.get("no_learning_feedback_candidate_from_replay") is False
    )
    no_new_concept = not (
        new_reviewed_concept_from_replay_created
        or replay_audit.get("no_new_reviewed_concept_from_replay") is False
    )
    failed = _boundary_failed(
        chain_complete=chain.chain_complete,
        no_external=no_external,
        no_memory=no_memory,
        no_automatic=not automatic_learning_approval_created
        and replay_audit.get("no_automatic_learning_approval", True) is True,
        no_behavior=not behavior_learning_created
        and replay_audit.get("no_behavior_learning", True) is True,
        no_recursive=no_recursive and no_new_concept,
        no_free=not (
            free_action_selection_created or scheduler_created or open_ended_loop_created
        ),
    )
    status = _boundary_status(failed)
    return FirstClosedLoopBoundaryAuditRecord(
        boundary_audit_id=f"first_closed_loop_boundary_audit:{chain.evidence_chain_id}",
        schema_version=BOUNDARY_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_evidence_chain_id=chain.evidence_chain_id,
        bounded_sandbox_only_confirmed=chain.chain_complete and no_external,
        teacher_gated_path_confirmed=chain.chain_complete,
        working_readback_only_confirmed=bool(chain.working_readback_integration_id),
        single_task_readback_scope_confirmed=bool(chain.readback_seed_id),
        no_external_execution=not external_execution_created
        and replay_audit.get("no_external_execution", True) is True,
        no_unity_execution=not unity_execution_created
        and replay_audit.get("no_unity_execution", True) is True,
        no_bridge_execution=not bridge_execution_created
        and replay_audit.get("no_bridge_execution", True) is True,
        no_network_execution=not network_execution_created
        and replay_audit.get("no_network_execution", True) is True,
        no_filesystem_execution=not filesystem_execution_created
        and replay_audit.get("no_filesystem_execution", True) is True,
        no_core_memory_write=not core_memory_write_performed,
        no_long_term_memory_write=not long_term_memory_write_performed,
        no_archive_memory_write=not archive_memory_write_performed,
        no_anchor_write=not anchor_write_performed,
        no_automatic_learning_approval=not automatic_learning_approval_created
        and replay_audit.get("no_automatic_learning_approval", True) is True,
        no_behavior_learning=not behavior_learning_created
        and replay_audit.get("no_behavior_learning", True) is True,
        no_free_action_selection=not free_action_selection_created,
        no_scheduler=not scheduler_created,
        no_open_ended_loop=not open_ended_loop_created,
        no_recursive_learning_from_replay=no_recursive,
        no_new_reviewed_concept_from_replay=no_new_concept,
        boundary_status=status,
        boundary_summary=_boundary_summary(status),
        failed_boundaries=tuple(failed),
        blocked_reasons=tuple(failed),
        source_trace_refs=chain.source_trace_refs,
    )


def validate_first_closed_loop_boundary_audit_record(
    boundary_audit: FirstClosedLoopBoundaryAuditRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _boundary(boundary_audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_boundary_audit:{error}",)}
    errors: list[str] = []
    if record.boundary_status == "passed_bounded_teacher_gated_loop_boundaries":
        for flag in (
            "bounded_sandbox_only_confirmed",
            "teacher_gated_path_confirmed",
            "working_readback_only_confirmed",
            "single_task_readback_scope_confirmed",
            "no_external_execution",
            "no_unity_execution",
            "no_bridge_execution",
            "no_network_execution",
            "no_filesystem_execution",
            "no_core_memory_write",
            "no_long_term_memory_write",
            "no_archive_memory_write",
            "no_anchor_write",
            "no_automatic_learning_approval",
            "no_behavior_learning",
            "no_free_action_selection",
            "no_scheduler",
            "no_open_ended_loop",
            "no_recursive_learning_from_replay",
            "no_new_reviewed_concept_from_replay",
        ):
            if getattr(record, flag) is not True:
                errors.append(f"{flag}_false")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "boundary_audit_id": record.boundary_audit_id,
        "boundary_status": record.boundary_status,
        "failed_boundaries": record.failed_boundaries,
    }


def build_first_closed_loop_replay_verification_record(
    *,
    evidence_chain: FirstClosedLoopEvidenceChainRecord | dict[str, object],
    replay_payload: dict[str, object],
    created_at: str | None = None,
) -> FirstClosedLoopReplayVerificationRecord:
    chain = _evidence(evidence_chain)
    replay_audit = dict(
        replay_payload.get("feedback_reviewed_concept_closed_loop_replay_audit", {})
    )
    replay_contrast = dict(replay_payload.get("feedback_reviewed_concept_replay_contrast", {}))
    replay_init = dict(
        replay_payload.get("feedback_reviewed_concept_replay_task_initialization", {})
    )
    replay_action = dict(
        replay_payload.get("feedback_reviewed_concept_replay_action_chain", {})
    )
    replay_execution = dict(replay_payload.get("feedback_reviewed_concept_replay_execution", {}))
    replay_outcome = dict(replay_payload.get("feedback_reviewed_concept_replay_outcome", {}))
    replay_audit_passed = replay_audit.get("audit_status") in PASSED_REPLAY_AUDIT_STATUSES
    feedback_used = bool(chain.feedback_derived_reviewed_concept_id)
    seed_used = bool(chain.readback_seed_id)
    second_init = bool(chain.replay_task_initialization_id)
    visible = bool(replay_init.get("working_memory_readback_slot_populated"))
    action_replayed = bool(chain.replay_action_chain_id)
    execution_completed = (
        replay_execution.get("execution_status")
        == "bounded_sandbox_replay_execution_completed"
    )
    outcome_closed = replay_outcome.get("outcome_status") == "replay_outcome_closed"
    influenced = bool(
        replay_contrast.get("candidate_ordering_changed_by_feedback_readback")
        or replay_contrast.get("direct_command_changed_by_feedback_readback")
    )
    visible_no_difference = (
        replay_contrast.get("contrast_status")
        == "passed_feedback_readback_visible_no_action_difference"
        or replay_audit.get("audit_status")
        == "passed_feedback_readback_visible_no_action_difference"
    )
    status = _replay_verification_status(
        feedback_used=feedback_used,
        seed_used=seed_used,
        second_init=second_init,
        visible=visible,
        action_replayed=action_replayed,
        replay_audit_passed=replay_audit_passed,
        influenced=influenced,
        visible_no_difference=visible_no_difference,
    )
    return FirstClosedLoopReplayVerificationRecord(
        replay_verification_id=f"first_closed_loop_replay_verification:{chain.evidence_chain_id}",
        schema_version=REPLAY_VERIFICATION_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_evidence_chain_id=chain.evidence_chain_id,
        source_replay_audit_id=chain.replay_audit_id,
        source_replay_contrast_id=chain.replay_contrast_id,
        feedback_reviewed_concept_used=feedback_used,
        working_readback_seed_used=seed_used,
        second_task_initialized=second_init,
        readback_hint_visible_in_second_task=visible,
        second_task_action_chain_replayed=action_replayed,
        second_task_bounded_execution_completed=execution_completed,
        second_task_outcome_closed=outcome_closed,
        candidate_ordering_influenced=influenced,
        selected_action_replayed=bool(replay_action.get("selected_action_created")),
        final_action_replayed=bool(replay_action.get("final_action_created")),
        direct_command_replayed=bool(replay_action.get("direct_command_created")),
        visible_no_action_difference=visible_no_difference,
        replay_verification_status=status,
        replay_verification_summary=_replay_verification_summary(status),
        source_trace_refs=chain.source_trace_refs,
    )


def validate_first_closed_loop_replay_verification_record(
    replay_verification: FirstClosedLoopReplayVerificationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _replay_verification(replay_verification)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_replay_verification:{error}",)}
    errors: list[str] = []
    if record.replay_verification_status.startswith("replay_verified"):
        for flag in (
            "feedback_reviewed_concept_used",
            "working_readback_seed_used",
            "second_task_initialized",
            "readback_hint_visible_in_second_task",
            "second_task_action_chain_replayed",
        ):
            if getattr(record, flag) is not True:
                errors.append(f"{flag}_false")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "replay_verification_id": record.replay_verification_id,
        "replay_verification_status": record.replay_verification_status,
    }


def build_first_closed_loop_milestone_record(
    *,
    evidence_chain: FirstClosedLoopEvidenceChainRecord | dict[str, object],
    boundary_audit: FirstClosedLoopBoundaryAuditRecord | dict[str, object],
    replay_verification: FirstClosedLoopReplayVerificationRecord | dict[str, object],
    created_at: str | None = None,
) -> FirstClosedLoopMilestoneRecord:
    chain = _evidence(evidence_chain)
    boundary = _boundary(boundary_audit)
    verification = _replay_verification(replay_verification)
    boundary_passed = boundary.boundary_status == "passed_bounded_teacher_gated_loop_boundaries"
    replay_passed = verification.replay_verification_status.startswith("replay_verified")
    if not chain.chain_complete:
        status = "failed_incomplete_evidence_chain"
    elif not boundary_passed:
        status = "failed_boundary_audit"
    elif not replay_passed:
        status = "failed_replay_verification"
    elif (
        verification.replay_verification_status
        == "replay_verified_visible_no_action_difference"
    ):
        status = VISIBLE_NO_DIFFERENCE_MILESTONE_STATUS
    else:
        status = PASSED_MILESTONE_STATUS
    return FirstClosedLoopMilestoneRecord(
        milestone_id=f"first_closed_loop_milestone:{chain.evidence_chain_id}",
        schema_version=MILESTONE_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_evidence_chain_id=chain.evidence_chain_id,
        source_boundary_audit_id=boundary.boundary_audit_id,
        source_replay_verification_id=verification.replay_verification_id,
        milestone_name=MILESTONE_NAME,
        milestone_version=MILESTONE_VERSION,
        first_action_path_verified=chain.first_task_selected_action_id is not None
        and chain.first_task_final_action_id is not None
        and chain.first_task_direct_command_id is not None
        and chain.first_task_sandbox_execution_id is not None,
        sense_task_evaluation_verified=chain.sense_observation_id is not None
        and chain.outcome_evaluation_id is not None
        and chain.task_closure_id is not None,
        learning_feedback_candidate_verified=chain.learning_feedback_candidate_id
        is not None
        and chain.learning_feedback_evidence_packet_id is not None,
        feedback_concept_candidate_refinement_verified=chain.concept_candidate_draft_id
        is not None
        and chain.feedback_refinement_id is not None
        and chain.feedback_scope_check_id is not None
        and chain.feedback_counterexample_check_id is not None,
        feedback_reviewed_concept_verified=chain.feedback_derived_reviewed_concept_id
        is not None,
        working_readback_integration_verified=chain.working_readback_integration_id
        is not None
        and chain.readback_seed_id is not None,
        second_task_replay_verified=replay_passed,
        boundary_audit_verified=boundary_passed,
        milestone_status=status,
        milestone_summary=_milestone_summary(status),
        safe_claim=SAFE_CLAIM,
        forbidden_claims=FORBIDDEN_CLAIMS,
        remaining_missing_capabilities=REMAINING_MISSING_CAPABILITIES,
        recommended_next_stage=RECOMMENDED_NEXT_STAGE,
        source_trace_refs=_combined_trace_refs(
            chain.source_trace_refs,
            boundary.source_trace_refs,
            verification.source_trace_refs,
        ),
    )


def validate_first_closed_loop_milestone_record(
    milestone: FirstClosedLoopMilestoneRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _milestone(milestone)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_milestone:{error}",)}
    errors: list[str] = []
    if record.milestone_status in {
        PASSED_MILESTONE_STATUS,
        VISIBLE_NO_DIFFERENCE_MILESTONE_STATUS,
    }:
        for flag in (
            "first_action_path_verified",
            "sense_task_evaluation_verified",
            "learning_feedback_candidate_verified",
            "feedback_concept_candidate_refinement_verified",
            "feedback_reviewed_concept_verified",
            "working_readback_integration_verified",
            "second_task_replay_verified",
            "boundary_audit_verified",
        ):
            if getattr(record, flag) is not True:
                errors.append(f"{flag}_false")
    for required in (
        "no_autonomous_learning",
        "no_long_term_memory_write",
        "no_free_action_selection",
    ):
        if required not in record.forbidden_claims:
            errors.append(f"missing_forbidden_claim:{required}")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "milestone_id": record.milestone_id,
        "milestone_status": record.milestone_status,
    }


def build_first_closed_loop_next_stage_readiness_record(
    *,
    milestone: FirstClosedLoopMilestoneRecord | dict[str, object],
    created_at: str | None = None,
) -> FirstClosedLoopNextStageReadinessRecord:
    record = _milestone(milestone)
    pass_status = record.milestone_status in {
        PASSED_MILESTONE_STATUS,
        VISIBLE_NO_DIFFERENCE_MILESTONE_STATUS,
    }
    if pass_status:
        readiness_status = "ready_for_bounded_multi_trial_loop_preview_only"
    elif record.milestone_status == "failed_boundary_audit":
        readiness_status = "not_ready_boundary_failure"
    elif record.milestone_status == "failed_incomplete_evidence_chain":
        readiness_status = "not_ready_missing_closed_loop_evidence"
    else:
        readiness_status = "not_ready_missing_closed_loop_evidence"
    return FirstClosedLoopNextStageReadinessRecord(
        next_stage_readiness_id=f"first_closed_loop_next_stage_readiness:{record.milestone_id}",
        schema_version=READINESS_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_milestone_id=record.milestone_id,
        current_verified_capability=(
            "bounded teacher-gated action-to-feedback-derived-ReviewedConcept-to-next-task replay loop v0"
            if pass_status
            else "closed loop milestone not verified"
        ),
        recommended_next_stage=RECOMMENDED_NEXT_STAGE,
        recommended_next_stage_reason=(
            "Only bounded multi-trial planning can extend the verified loop while preserving teacher gates."
            if pass_status
            else "Milestone must pass before next-stage planning."
        ),
        ready_for_recursive_replay_planning=False,
        ready_for_bounded_multi_trial_loop_preview=pass_status,
        ready_for_memory_promotion=False,
        ready_for_long_term_memory=False,
        ready_for_autonomous_scheduler=False,
        ready_for_free_action_selection=False,
        ready_for_external_execution=False,
        ready_for_thought_engine=False,
        required_next_boundaries=(
            "teacher_gate_required",
            "bounded_sandbox_only",
            "no_automatic_learning_approval",
            "no_memory_layer_write",
            "no_external_execution",
            "no_free_action_selection",
        ),
        required_next_tests=(
            "multi_trial_plan_does_not_execute",
            "teacher_gates_preserved",
            "memory_promotion_blocked",
            "scheduler_not_created",
            "external_execution_blocked",
        ),
        readiness_status=readiness_status,
        readiness_summary=_readiness_summary(readiness_status),
        source_trace_refs=record.source_trace_refs,
    )


def validate_first_closed_loop_next_stage_readiness_record(
    readiness: FirstClosedLoopNextStageReadinessRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _readiness(readiness)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_readiness:{error}",)}
    errors: list[str] = []
    if record.readiness_status == "ready_for_bounded_multi_trial_loop_preview_only":
        if not record.ready_for_bounded_multi_trial_loop_preview:
            errors.append("bounded_multi_trial_preview_not_ready")
    for flag in (
        "ready_for_memory_promotion",
        "ready_for_long_term_memory",
        "ready_for_autonomous_scheduler",
        "ready_for_free_action_selection",
        "ready_for_external_execution",
        "ready_for_thought_engine",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "next_stage_readiness_id": record.next_stage_readiness_id,
        "readiness_status": record.readiness_status,
    }


def build_demo_first_closed_loop_milestone() -> dict[str, object]:
    return _build_demo_milestone()


def build_demo_first_closed_loop_visible_no_action_difference_milestone() -> dict[str, object]:
    return _build_demo_milestone(visible_no_action_difference=True)


def build_demo_blocked_missing_first_action_path_milestone() -> dict[str, object]:
    return _build_demo_milestone(missing_links=("first_action_path",))


def build_demo_blocked_missing_sense_observation_milestone() -> dict[str, object]:
    return _build_demo_milestone(missing_links=("sense_task_path",))


def build_demo_blocked_missing_task_closure_milestone() -> dict[str, object]:
    return _build_demo_milestone(missing_links=("sense_task_path",))


def build_demo_blocked_missing_learning_feedback_candidate_milestone() -> dict[str, object]:
    return _build_demo_milestone(missing_links=("learning_feedback_path",))


def build_demo_blocked_missing_feedback_reviewed_concept_milestone() -> dict[str, object]:
    return _build_demo_milestone(missing_links=("reviewed_concept_path",))


def build_demo_blocked_missing_working_readback_milestone() -> dict[str, object]:
    return _build_demo_milestone(
        missing_links=("reviewed_concept_path",),
        remove_working_readback=True,
    )


def build_demo_blocked_missing_second_task_replay_milestone() -> dict[str, object]:
    return _build_demo_milestone(missing_links=("replay_path",))


def build_demo_blocked_invalid_replay_audit_milestone() -> dict[str, object]:
    return _build_demo_milestone(replay_block_case="missing-rollback")


def build_demo_blocked_external_execution_milestone() -> dict[str, object]:
    return _build_demo_milestone(external_execution_created=True)


def build_demo_blocked_memory_write_milestone() -> dict[str, object]:
    return _build_demo_milestone(core_memory_write_performed=True)


def build_demo_blocked_automatic_learning_approval_milestone() -> dict[str, object]:
    return _build_demo_milestone(automatic_learning_approval_created=True)


def build_demo_blocked_behavior_learning_milestone() -> dict[str, object]:
    return _build_demo_milestone(behavior_learning_created=True)


def build_demo_blocked_recursive_learning_from_replay_milestone() -> dict[str, object]:
    return _build_demo_milestone(recursive_learning_from_replay_created=True)


def build_demo_blocked_free_action_selection_milestone() -> dict[str, object]:
    return _build_demo_milestone(free_action_selection_created=True)


def build_demo_first_closed_loop_milestone_case(case: str) -> dict[str, object]:
    if case == "normal":
        return build_demo_first_closed_loop_milestone()
    if case == "visible-no-action-difference":
        return build_demo_first_closed_loop_visible_no_action_difference_milestone()
    raise ValueError(f"unknown first loop milestone case: {case}")


def build_demo_blocked_first_closed_loop_milestone(case: str) -> dict[str, object]:
    cases = {
        "missing-first-action-path": build_demo_blocked_missing_first_action_path_milestone,
        "missing-sense-observation": build_demo_blocked_missing_sense_observation_milestone,
        "missing-task-closure": build_demo_blocked_missing_task_closure_milestone,
        "missing-learning-feedback-candidate": build_demo_blocked_missing_learning_feedback_candidate_milestone,
        "missing-feedback-reviewed-concept": build_demo_blocked_missing_feedback_reviewed_concept_milestone,
        "missing-working-readback": build_demo_blocked_missing_working_readback_milestone,
        "missing-second-task-replay": build_demo_blocked_missing_second_task_replay_milestone,
        "invalid-replay-audit": build_demo_blocked_invalid_replay_audit_milestone,
        "external-execution-detected": build_demo_blocked_external_execution_milestone,
        "memory-write-detected": build_demo_blocked_memory_write_milestone,
        "automatic-learning-approval": build_demo_blocked_automatic_learning_approval_milestone,
        "behavior-learning": build_demo_blocked_behavior_learning_milestone,
        "recursive-learning-from-replay": build_demo_blocked_recursive_learning_from_replay_milestone,
        "free-action-selection": build_demo_blocked_free_action_selection_milestone,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked milestone case: {case}") from error


def _build_demo_milestone(
    *,
    visible_no_action_difference: bool = False,
    replay_block_case: str | None = None,
    missing_links: tuple[str, ...] = (),
    remove_working_readback: bool = False,
    external_execution_created: bool = False,
    core_memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    behavior_learning_created: bool = False,
    recursive_learning_from_replay_created: bool = False,
    free_action_selection_created: bool = False,
) -> dict[str, object]:
    if replay_block_case is not None:
        replay_payload = build_demo_blocked_feedback_reviewed_concept_closed_loop_replay(
            replay_block_case
        )
    elif visible_no_action_difference:
        replay_payload = build_demo_visible_no_action_difference_replay()
    else:
        replay_payload = build_demo_negative_affordance_closed_loop_replay()
    if remove_working_readback:
        replay_payload = {
            **replay_payload,
            "feedback_derived_reviewed_concept_working_readback_integration": {
                **dict(
                    replay_payload[
                        "feedback_derived_reviewed_concept_working_readback_integration"
                    ]
                ),
                "working_readback_integration_id": None,
            },
        }
    evidence_chain = build_first_closed_loop_evidence_chain_record(
        replay_payload=replay_payload,
        missing_links=missing_links,
    )
    boundary_audit = build_first_closed_loop_boundary_audit_record(
        evidence_chain=evidence_chain,
        replay_payload=replay_payload,
        external_execution_created=external_execution_created,
        core_memory_write_performed=core_memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        behavior_learning_created=behavior_learning_created,
        recursive_learning_from_replay_created=recursive_learning_from_replay_created,
        free_action_selection_created=free_action_selection_created,
    )
    replay_verification = build_first_closed_loop_replay_verification_record(
        evidence_chain=evidence_chain,
        replay_payload=replay_payload,
    )
    milestone = build_first_closed_loop_milestone_record(
        evidence_chain=evidence_chain,
        boundary_audit=boundary_audit,
        replay_verification=replay_verification,
    )
    readiness = build_first_closed_loop_next_stage_readiness_record(
        milestone=milestone,
    )
    return {
        "source_package93_replay": replay_payload,
        "first_closed_loop_evidence_chain": evidence_chain.to_dict(),
        "first_closed_loop_boundary_audit": boundary_audit.to_dict(),
        "first_closed_loop_replay_verification": replay_verification.to_dict(),
        "first_closed_loop_milestone": milestone.to_dict(),
        "first_closed_loop_next_stage_readiness": readiness.to_dict(),
    }


def _extract_evidence(replay_payload: dict[str, object]) -> dict[str, object]:
    closure = dict(replay_payload.get("source_task_closure", {}))
    feedback = dict(replay_payload.get("learning_feedback_candidate", {}))
    evidence = dict(replay_payload.get("learning_feedback_evidence_packet", {}))
    draft = dict(replay_payload.get("learning_feedback_to_concept_candidate_draft", {}))
    refinement = dict(replay_payload.get("feedback_concept_candidate_refinement", {}))
    scope = dict(replay_payload.get("feedback_concept_candidate_scope_check", {}))
    counterexample = dict(
        replay_payload.get("feedback_concept_candidate_counterexample_check", {})
    )
    reviewed = dict(replay_payload.get("feedback_derived_reviewed_concept", {}))
    readback = dict(
        replay_payload.get("feedback_derived_reviewed_concept_working_readback_integration", {})
    )
    seed = dict(replay_payload.get("feedback_derived_reviewed_concept_readback_seed", {}))
    replay_gate = dict(replay_payload.get("feedback_reviewed_concept_replay_gate") or {})
    replay_init = dict(
        replay_payload.get("feedback_reviewed_concept_replay_task_initialization", {})
    )
    replay_action = dict(replay_payload.get("feedback_reviewed_concept_replay_action_chain", {}))
    replay_execution = dict(
        replay_payload.get("feedback_reviewed_concept_replay_execution", {})
    )
    replay_outcome = dict(replay_payload.get("feedback_reviewed_concept_replay_outcome", {}))
    replay_contrast = dict(replay_payload.get("feedback_reviewed_concept_replay_contrast", {}))
    replay_audit = dict(
        replay_payload.get("feedback_reviewed_concept_closed_loop_replay_audit", {})
    )
    direct_command_id = _value(
        closure,
        "source_direct_command_application_id",
        feedback,
        "source_direct_command_application_id",
    )
    task_initialization_id = _value(
        closure,
        "source_task_initialization_id",
        feedback,
        "task_initialization_id",
    )
    return {
        "first_task_selected_action_id": _derived_id(
            "selected_action_application",
            task_initialization_id,
            direct_command_id,
        ),
        "first_task_final_action_id": _derived_id(
            "final_action_application",
            task_initialization_id,
            direct_command_id,
        ),
        "first_task_direct_command_id": direct_command_id,
        "first_task_sandbox_execution_id": _value(
            closure,
            "source_sandbox_execution_id",
            feedback,
            "source_sandbox_execution_id",
        ),
        "first_task_execution_audit_id": _derived_id(
            "direct_command_sandbox_execution_audit",
            task_initialization_id,
            direct_command_id,
        ),
        "sense_observation_id": feedback.get("source_sense_observation_id"),
        "sense_handoff_id": _value(
            closure,
            "source_sense_handoff_id",
            feedback,
            "source_sense_handoff_id",
        ),
        "outcome_evaluation_id": _value(
            closure,
            "source_outcome_evaluation_id",
            feedback,
            "source_outcome_evaluation_id",
        ),
        "goal_delta_evaluation_id": _value(
            closure,
            "source_goal_delta_evaluation_id",
            feedback,
            "source_goal_delta_evaluation_id",
        ),
        "task_closure_id": closure.get("task_closure_id"),
        "learning_feedback_candidate_id": feedback.get("learning_feedback_candidate_id"),
        "learning_feedback_evidence_packet_id": evidence.get(
            "learning_feedback_evidence_packet_id"
        ),
        "concept_candidate_draft_id": draft.get("concept_candidate_draft_id"),
        "feedback_refinement_id": refinement.get("feedback_concept_candidate_refinement_id"),
        "feedback_scope_check_id": scope.get("scope_check_id"),
        "feedback_counterexample_check_id": counterexample.get("counterexample_check_id"),
        "feedback_derived_reviewed_concept_id": reviewed.get(
            "feedback_derived_reviewed_concept_id"
        ),
        "working_readback_integration_id": readback.get("working_readback_integration_id"),
        "readback_seed_id": seed.get("readback_seed_id"),
        "replay_gate_id": replay_gate.get("feedback_replay_gate_id"),
        "replay_task_initialization_id": replay_init.get("replay_task_initialization_id"),
        "replay_action_chain_id": replay_action.get("replay_action_chain_id"),
        "replay_execution_id": replay_execution.get("replay_execution_id"),
        "replay_outcome_id": replay_outcome.get("replay_outcome_id"),
        "replay_contrast_id": replay_contrast.get("replay_contrast_id"),
        "replay_audit_id": replay_audit.get("closed_loop_replay_audit_id"),
    }


_REQUIRED_LINK_GROUPS = (
    (
        "first_action_path",
        (
            "first_task_selected_action_id",
            "first_task_final_action_id",
            "first_task_direct_command_id",
            "first_task_sandbox_execution_id",
            "first_task_execution_audit_id",
        ),
    ),
    (
        "sense_task_path",
        (
            "sense_observation_id",
            "sense_handoff_id",
            "outcome_evaluation_id",
            "goal_delta_evaluation_id",
            "task_closure_id",
        ),
    ),
    (
        "learning_feedback_path",
        (
            "learning_feedback_candidate_id",
            "learning_feedback_evidence_packet_id",
            "concept_candidate_draft_id",
            "feedback_refinement_id",
            "feedback_scope_check_id",
            "feedback_counterexample_check_id",
        ),
    ),
    (
        "reviewed_concept_path",
        (
            "feedback_derived_reviewed_concept_id",
            "working_readback_integration_id",
            "readback_seed_id",
        ),
    ),
    (
        "replay_path",
        (
            "replay_gate_id",
            "replay_task_initialization_id",
            "replay_action_chain_id",
            "replay_execution_id",
            "replay_outcome_id",
            "replay_contrast_id",
            "replay_audit_id",
        ),
    ),
)


def _evidence_status(missing: list[str]) -> str:
    if not missing:
        return "chain_complete"
    priority = (
        ("first_action_path", "chain_incomplete_missing_first_action_path"),
        ("sense_task_path", "chain_incomplete_missing_sense_task_path"),
        ("learning_feedback_path", "chain_incomplete_missing_learning_feedback_path"),
        ("reviewed_concept_path", "chain_incomplete_missing_reviewed_concept_path"),
        ("replay_path", "chain_incomplete_missing_replay_path"),
    )
    for link, status in priority:
        if link in missing:
            return status
    return "blocked_invalid_trace_lineage"


def _evidence_summary(status: str, missing: list[str]) -> str:
    if status == "chain_complete":
        return "First bounded action-to-ReviewedConcept-to-next-task evidence chain is complete."
    return f"First closed-loop evidence chain missing: {', '.join(missing)}."


def _boundary_failed(
    *,
    chain_complete: bool,
    no_external: bool,
    no_memory: bool,
    no_automatic: bool,
    no_behavior: bool,
    no_recursive: bool,
    no_free: bool,
) -> list[str]:
    failed: list[str] = []
    if not chain_complete:
        failed.append("invalid_evidence_chain")
    if not no_external:
        failed.append("external_execution_detected")
    if not no_memory:
        failed.append("memory_layer_write_detected")
    if not no_automatic:
        failed.append("automatic_learning_approval_detected")
    if not no_behavior:
        failed.append("behavior_learning_detected")
    if not no_recursive:
        failed.append("recursive_learning_detected")
    if not no_free:
        failed.append("free_action_selection_detected")
    return failed


def _boundary_status(failed: list[str]) -> str:
    if not failed:
        return "passed_bounded_teacher_gated_loop_boundaries"
    priority = (
        ("invalid_evidence_chain", "blocked_invalid_evidence_chain"),
        ("external_execution_detected", "failed_external_execution_detected"),
        ("memory_layer_write_detected", "failed_memory_layer_write_detected"),
        (
            "automatic_learning_approval_detected",
            "failed_automatic_learning_approval_detected",
        ),
        ("behavior_learning_detected", "failed_behavior_learning_detected"),
        ("recursive_learning_detected", "failed_recursive_learning_detected"),
        ("free_action_selection_detected", "failed_free_action_selection_detected"),
    )
    for reason, status in priority:
        if reason in failed:
            return status
    return "failed_free_action_selection_detected"


def _boundary_summary(status: str) -> str:
    return {
        "passed_bounded_teacher_gated_loop_boundaries": (
            "First closed-loop boundaries passed: bounded sandbox, teacher gates, no memory write, no recursive learning."
        ),
        "failed_external_execution_detected": "External execution boundary failed.",
        "failed_memory_layer_write_detected": "Memory layer write boundary failed.",
        "failed_automatic_learning_approval_detected": (
            "Automatic learning approval boundary failed."
        ),
        "failed_behavior_learning_detected": "Behavior learning boundary failed.",
        "failed_recursive_learning_detected": "Recursive replay learning boundary failed.",
        "failed_free_action_selection_detected": "Free action selection boundary failed.",
        "blocked_invalid_evidence_chain": "Boundary audit blocked by incomplete evidence.",
    }[status]


def _replay_verification_status(
    *,
    feedback_used: bool,
    seed_used: bool,
    second_init: bool,
    visible: bool,
    action_replayed: bool,
    replay_audit_passed: bool,
    influenced: bool,
    visible_no_difference: bool,
) -> str:
    if not feedback_used:
        return "blocked_missing_feedback_reviewed_concept"
    if not seed_used:
        return "blocked_missing_readback_seed"
    if not second_init or not visible or not action_replayed:
        return "blocked_missing_second_task_replay"
    if not replay_audit_passed:
        return "blocked_invalid_replay_audit"
    if influenced:
        return "replay_verified_with_action_chain_influence"
    if visible_no_difference:
        return "replay_verified_visible_no_action_difference"
    return "blocked_invalid_replay_audit"


def _replay_verification_summary(status: str) -> str:
    return {
        "replay_verified_with_action_chain_influence": (
            "Replay verified: feedback readback influenced the second task action chain."
        ),
        "replay_verified_visible_no_action_difference": (
            "Replay verified: feedback readback was visible with no action difference."
        ),
        "blocked_missing_feedback_reviewed_concept": (
            "Replay verification missing feedback-derived ReviewedConcept."
        ),
        "blocked_missing_readback_seed": "Replay verification missing readback seed.",
        "blocked_missing_second_task_replay": "Replay verification missing second task replay.",
        "blocked_invalid_replay_audit": "Replay verification blocked by invalid replay audit.",
    }[status]


def _milestone_summary(status: str) -> str:
    return {
        PASSED_MILESTONE_STATUS: (
            "First bounded teacher-gated action-to-feedback-derived-ReviewedConcept-to-next-task loop v0 sealed."
        ),
        VISIBLE_NO_DIFFERENCE_MILESTONE_STATUS: (
            "First loop sealed with visible readback and no action difference."
        ),
        "failed_incomplete_evidence_chain": "Milestone failed: incomplete evidence chain.",
        "failed_boundary_audit": "Milestone failed: boundary audit did not pass.",
        "failed_replay_verification": "Milestone failed: replay verification did not pass.",
        "blocked_invalid_source_records": "Milestone blocked by invalid source records.",
    }[status]


def _readiness_summary(status: str) -> str:
    return {
        "ready_for_bounded_multi_trial_loop_preview_only": (
            "Ready only for bounded multi-trial loop planning preview."
        ),
        "ready_for_recursive_replay_planning_only": (
            "Ready only for recursive replay planning."
        ),
        "not_ready_missing_closed_loop_evidence": (
            "Not ready because closed-loop evidence is incomplete."
        ),
        "not_ready_boundary_failure": "Not ready because loop boundary audit failed.",
        "blocked_forbidden_authority_detected": (
            "Readiness blocked by forbidden authority."
        ),
    }[status]


def _collect_trace_refs(replay_payload: dict[str, object]) -> tuple[str, ...]:
    refs: list[str] = []
    for value in replay_payload.values():
        if isinstance(value, dict):
            for item in value.get("source_trace_refs", ()) or ():
                if item not in refs:
                    refs.append(str(item))
    return tuple(refs)


def _value(
    first: dict[str, object],
    first_key: str,
    second: dict[str, object],
    second_key: str,
) -> str | None:
    value = first.get(first_key) or second.get(second_key)
    return str(value) if value else None


def _derived_id(prefix: str, task_initialization_id: str | None, fallback: str | None) -> str | None:
    if task_initialization_id:
        return f"{prefix}:{task_initialization_id}"
    if fallback:
        return f"{prefix}:{fallback}"
    return None


def _evidence(
    value: FirstClosedLoopEvidenceChainRecord | dict[str, object],
) -> FirstClosedLoopEvidenceChainRecord:
    if isinstance(value, FirstClosedLoopEvidenceChainRecord):
        return value
    return FirstClosedLoopEvidenceChainRecord.from_dict(value)


def _boundary(
    value: FirstClosedLoopBoundaryAuditRecord | dict[str, object],
) -> FirstClosedLoopBoundaryAuditRecord:
    if isinstance(value, FirstClosedLoopBoundaryAuditRecord):
        return value
    return FirstClosedLoopBoundaryAuditRecord.from_dict(value)


def _replay_verification(
    value: FirstClosedLoopReplayVerificationRecord | dict[str, object],
) -> FirstClosedLoopReplayVerificationRecord:
    if isinstance(value, FirstClosedLoopReplayVerificationRecord):
        return value
    return FirstClosedLoopReplayVerificationRecord.from_dict(value)


def _milestone(
    value: FirstClosedLoopMilestoneRecord | dict[str, object],
) -> FirstClosedLoopMilestoneRecord:
    if isinstance(value, FirstClosedLoopMilestoneRecord):
        return value
    return FirstClosedLoopMilestoneRecord.from_dict(value)


def _readiness(
    value: FirstClosedLoopNextStageReadinessRecord | dict[str, object],
) -> FirstClosedLoopNextStageReadinessRecord:
    if isinstance(value, FirstClosedLoopNextStageReadinessRecord):
        return value
    return FirstClosedLoopNextStageReadinessRecord.from_dict(value)
