"""Closed-loop replay for feedback-derived ReviewedConcept readback."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.learning.feedback_refined_concept_reviewed_readback_integration import (
    FeedbackDerivedReviewedConceptIntegrationSafetyAudit,
    FeedbackDerivedReviewedConceptReadbackSeedRecord,
    FeedbackDerivedReviewedConceptRecord,
    FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord,
    build_demo_feedback_reviewed_concept_integration_case,
    validate_feedback_derived_reviewed_concept_integration_safety_audit,
    validate_feedback_derived_reviewed_concept_readback_seed_record,
    validate_feedback_derived_reviewed_concept_record,
    validate_feedback_derived_reviewed_concept_working_readback_integration_record,
)


SOURCE_ENGINE = "closed_loop_replay"
TASK_ENGINE = "task_engine"

GATE_SCHEMA_VERSION = "feedback_reviewed_concept_closed_loop_replay_gate_v0"
TASK_INITIALIZATION_SCHEMA_VERSION = (
    "feedback_reviewed_concept_replay_task_initialization_v0"
)
ACTION_CHAIN_SCHEMA_VERSION = "feedback_reviewed_concept_replay_action_chain_v0"
EXECUTION_SCHEMA_VERSION = "feedback_reviewed_concept_replay_execution_v0"
OUTCOME_SCHEMA_VERSION = "feedback_reviewed_concept_replay_outcome_v0"
CONTRAST_SCHEMA_VERSION = "feedback_reviewed_concept_replay_contrast_v0"
ROLLBACK_SCHEMA_VERSION = "feedback_reviewed_concept_replay_rollback_v0"
AUDIT_SCHEMA_VERSION = "feedback_reviewed_concept_closed_loop_replay_audit_v0"

APPROVED_GATE_STATUS = "approved_for_feedback_reviewed_concept_closed_loop_replay"
INITIALIZED_WITH_READBACK_STATUS = "replay_task_initialized_with_feedback_readback"
ACTION_CHAIN_DIRECT_COMMAND_STATUS = "replay_action_chain_built_to_direct_command"
EXECUTION_COMPLETED_STATUS = "bounded_sandbox_replay_execution_completed"
OUTCOME_CLOSED_STATUS = "replay_outcome_closed"
CONTRAST_INFLUENCED_STATUS = "passed_feedback_readback_influenced_action_chain"
CONTRAST_NO_DIFFERENCE_STATUS = (
    "passed_feedback_readback_visible_no_action_difference"
)
AUDIT_PASSED_STATUS = "passed_feedback_reviewed_concept_closed_loop_replay"
AUDIT_NO_DIFFERENCE_STATUS = "passed_feedback_readback_visible_no_action_difference"

SAFE_CLAIM = (
    "ASHL Core v1 can replay a bounded second task using a feedback-derived "
    "ReviewedConcept working-readback seed, showing that a prior bounded "
    "sandbox task outcome can return as a ReviewedConcept readback hint and "
    "influence the next bounded task action chain through sandbox execution, "
    "while blocking external execution, recursive learning creation, automatic "
    "learning approval, behavior learning, and memory-layer writes."
)
BLOCKED_CLAIMS = (
    "no_external_execution",
    "no_unity_execution",
    "no_bridge_execution",
    "no_network_execution",
    "no_filesystem_execution",
    "no_learning_feedback_candidate_from_replay",
    "no_new_reviewed_concept_from_replay",
    "no_memory_layer_write",
    "no_automatic_learning_approval",
    "no_behavior_learning",
)

ALLOWED_GATE_STATUSES = {
    APPROVED_GATE_STATUS,
    "held_for_more_evidence",
    "rejected",
    "conflict_detected",
    "blocked_invalid_feedback_reviewed_concept",
    "blocked_invalid_working_readback_integration",
    "blocked_invalid_readback_seed",
    "blocked_forbidden_authority_detected",
}
ALLOWED_APPROVAL_SOURCES = {"explicit_teacher_review", "demo_review"}
ALLOWED_APPROVAL_ACTOR_ROLES = {"teacher", "project_owner", "system_demo"}
ALLOWED_INITIALIZATION_STATUSES = {
    INITIALIZED_WITH_READBACK_STATUS,
    "replay_task_initialized_without_readback_baseline",
    "blocked_invalid_replay_gate",
    "blocked_invalid_readback_seed",
    "blocked_running_task_mutation_attempt",
    "blocked_forbidden_authority_detected",
}
ALLOWED_ACTION_CHAIN_STATUSES = {
    ACTION_CHAIN_DIRECT_COMMAND_STATUS,
    "replay_action_chain_built_to_final_action_only",
    "replay_action_chain_blocked_before_ordering",
    "replay_action_chain_blocked_before_selected_action",
    "replay_action_chain_blocked_before_final_action",
    "replay_action_chain_blocked_before_direct_command",
    "blocked_forbidden_authority_detected",
}
ALLOWED_EXECUTION_STATUSES = {
    EXECUTION_COMPLETED_STATUS,
    "replay_execution_blocked_before_execution",
    "blocked_invalid_action_chain",
    "blocked_unsupported_direct_command",
    "blocked_external_execution_attempt",
    "blocked_forbidden_authority_detected",
}
ALLOWED_OUTCOME_STATUSES = {
    OUTCOME_CLOSED_STATUS,
    "replay_outcome_observed_only",
    "replay_outcome_evaluated_not_closed",
    "replay_outcome_blocked",
    "blocked_learning_feedback_created",
    "blocked_memory_write_detected",
    "blocked_automatic_learning_approval_detected",
}
ALLOWED_CONTRAST_STATUSES = {
    CONTRAST_INFLUENCED_STATUS,
    CONTRAST_NO_DIFFERENCE_STATUS,
    "blocked_missing_baseline",
    "blocked_missing_replay_chain",
    "blocked_forbidden_authority_detected",
}
ALLOWED_ROLLBACK_STATUSES = {
    "rollback_record_created",
    "rollback_applied_to_withdraw_replay_task_records",
    "rollback_applied_to_restore_sandbox_state",
    "blocked_invalid_replay_record",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    AUDIT_PASSED_STATUS,
    AUDIT_NO_DIFFERENCE_STATUS,
    "blocked_invalid_feedback_reviewed_concept",
    "blocked_invalid_readback_integration",
    "blocked_invalid_replay_gate",
    "blocked_replay_task_initialization_failed",
    "blocked_action_chain_replay_failed",
    "blocked_execution_failed",
    "blocked_outcome_replay_failed",
    "blocked_contrast_failed",
    "blocked_missing_rollback",
    "blocked_external_execution_detected",
    "blocked_memory_write_detected",
    "blocked_automatic_learning_approval_detected",
    "blocked_behavior_learning_detected",
}

ALLOWED_BOUNDED_DIRECT_COMMANDS = {
    "observe",
    "step_forward",
    "turn_left",
    "turn_right",
    "push_right",
    "push_left",
    "wait",
    "push_forward",
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


def _tuple_of_dicts(name: str, value: tuple[dict, ...] | list[dict]) -> tuple[dict, ...]:
    items = tuple(dict(item) for item in value)
    if not all(isinstance(item, dict) for item in items):
        raise TypeError(f"{name} must contain only dictionaries")
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
class FeedbackReviewedConceptReplayGate:
    feedback_replay_gate_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_feedback_derived_reviewed_concept_id: str
    source_working_readback_integration_id: str
    source_readback_seed_id: str
    source_feedback_integration_safety_audit_id: str
    replay_task_id: str
    replay_sandbox_id: str
    reviewed_concept_label: str
    reviewed_concept_scope: str
    readback_hint_label: str
    readback_hint_kind: str
    teacher_gate_status: str
    teacher_gate_reason: str
    teacher_gate_text: str
    approval_actor: str
    approval_actor_role: str
    approval_source: str
    approved_for_closed_loop_replay: bool
    approved_for_bounded_sandbox_execution: bool
    approved_for_external_execution: bool
    approved_for_unity_execution: bool
    approved_for_bridge_execution: bool
    approved_for_free_action_selection: bool
    approved_for_memory_layer_write: bool
    approved_for_automatic_learning_approval: bool
    approved_for_behavior_learning: bool
    requires_replay_rollback: bool
    requires_replay_audit: bool
    requires_baseline_contrast: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != GATE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be feedback_reviewed_concept_closed_loop_replay_gate_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be closed_loop_replay")
        if self.teacher_gate_status not in ALLOWED_GATE_STATUSES:
            raise ValueError(f"unknown teacher_gate_status: {self.teacher_gate_status}")
        if self.approval_source not in ALLOWED_APPROVAL_SOURCES:
            raise ValueError(f"unknown approval_source: {self.approval_source}")
        if self.approval_actor_role not in ALLOWED_APPROVAL_ACTOR_ROLES:
            raise ValueError(f"unknown approval_actor_role: {self.approval_actor_role}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FeedbackReviewedConceptReplayGate":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackReviewedConceptReplayTaskInitializationRecord:
    replay_task_initialization_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_feedback_replay_gate_id: str
    source_feedback_derived_reviewed_concept_id: str
    source_readback_seed_id: str
    replay_task_id: str
    replay_task_working_memory_id: str
    replay_sandbox_id: str
    baseline_candidate_ordering: tuple[str, ...]
    readback_hint_applied: bool
    readback_hint_id: str | None
    readback_hint_label: str | None
    readback_hint_kind: str | None
    task_working_memory_initialized: bool
    working_memory_readback_slot_populated: bool
    candidate_ordering_changed_at_initialization: bool
    selected_action_created_at_initialization: bool
    final_action_created_at_initialization: bool
    direct_command_created_at_initialization: bool
    execution_created_at_initialization: bool
    initialization_status: str
    initialization_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TASK_INITIALIZATION_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be feedback_reviewed_concept_replay_task_initialization_v0"
            )
        if self.source_engine != TASK_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.initialization_status not in ALLOWED_INITIALIZATION_STATUSES:
            raise ValueError(
                f"unknown initialization_status: {self.initialization_status}"
            )
        for name in ("baseline_candidate_ordering", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "FeedbackReviewedConceptReplayTaskInitializationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackReviewedConceptReplayActionChainRecord:
    replay_action_chain_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_feedback_replay_gate_id: str
    source_replay_task_initialization_id: str
    source_feedback_derived_reviewed_concept_id: str
    replay_task_working_memory_id: str
    baseline_candidate_ordering: tuple[str, ...]
    readback_influenced_candidate_ordering: tuple[str, ...]
    candidate_ordering_application_id: str | None
    selected_action_proposal_id: str | None
    selected_action_application_id: str | None
    final_action_application_id: str | None
    direct_command_application_id: str | None
    selected_action_candidate_id: str | None
    final_action_candidate_id: str | None
    direct_command: str | None
    candidate_ordering_changed: bool
    selected_action_created: bool
    final_action_created: bool
    direct_command_created: bool
    execution_created: bool
    external_execution_created: bool
    unity_execution_created: bool
    bridge_execution_created: bool
    network_execution_created: bool
    filesystem_execution_created: bool
    action_chain_status: str
    action_chain_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ACTION_CHAIN_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be feedback_reviewed_concept_replay_action_chain_v0"
            )
        if self.source_engine != TASK_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.action_chain_status not in ALLOWED_ACTION_CHAIN_STATUSES:
            raise ValueError(f"unknown action_chain_status: {self.action_chain_status}")
        for name in (
            "baseline_candidate_ordering",
            "readback_influenced_candidate_ordering",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "FeedbackReviewedConceptReplayActionChainRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackReviewedConceptReplayExecutionRecord:
    replay_execution_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_feedback_replay_gate_id: str
    source_replay_action_chain_id: str
    source_direct_command_application_id: str | None
    replay_task_working_memory_id: str
    replay_sandbox_id: str
    direct_command: str | None
    sandbox_execution_id: str | None
    pre_execution_snapshot_id: str | None
    sandbox_restore_id: str | None
    sandbox_execution_audit_id: str | None
    sandbox_execution_created: bool
    bounded_sandbox_execution_created: bool
    external_execution_created: bool
    unity_execution_created: bool
    bridge_execution_created: bool
    network_execution_created: bool
    filesystem_execution_created: bool
    execution_status: str
    execution_summary: str
    restore_available: bool
    rollback_available: bool
    task_behavior_learning_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EXECUTION_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be feedback_reviewed_concept_replay_execution_v0"
            )
        if self.source_engine != TASK_ENGINE:
            raise ValueError("source_engine must be task_engine")
        if self.execution_status not in ALLOWED_EXECUTION_STATUSES:
            raise ValueError(f"unknown execution_status: {self.execution_status}")
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
    ) -> "FeedbackReviewedConceptReplayExecutionRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackReviewedConceptReplayOutcomeRecord:
    replay_outcome_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_feedback_replay_gate_id: str
    source_replay_execution_id: str
    source_feedback_derived_reviewed_concept_id: str
    sense_observation_id: str | None
    sense_handoff_id: str | None
    outcome_evaluation_id: str | None
    goal_delta_evaluation_id: str | None
    task_closure_id: str | None
    direct_command: str | None
    expected_effect: str | None
    outcome_class: str | None
    goal_delta_class: str | None
    closure_status: str | None
    sense_observation_created: bool
    outcome_evaluation_created: bool
    task_closure_created: bool
    learning_feedback_candidate_created: bool
    new_reviewed_concept_created_from_replay: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    outcome_status: str
    outcome_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != OUTCOME_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be feedback_reviewed_concept_replay_outcome_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be closed_loop_replay")
        if self.outcome_status not in ALLOWED_OUTCOME_STATUSES:
            raise ValueError(f"unknown outcome_status: {self.outcome_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FeedbackReviewedConceptReplayOutcomeRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackReviewedConceptReplayContrastRecord:
    replay_contrast_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_feedback_replay_gate_id: str
    source_replay_task_initialization_id: str
    source_replay_action_chain_id: str
    source_replay_execution_id: str | None
    baseline_candidate_ordering: tuple[str, ...]
    readback_influenced_candidate_ordering: tuple[str, ...]
    baseline_top_candidate: str | None
    readback_influenced_top_candidate: str | None
    baseline_direct_command: str | None
    readback_influenced_direct_command: str | None
    candidate_ordering_changed_by_feedback_readback: bool
    selected_action_changed_by_feedback_readback: bool
    final_action_changed_by_feedback_readback: bool
    direct_command_changed_by_feedback_readback: bool
    execution_created_by_feedback_replay: bool
    contrast_status: str
    contrast_summary: str
    external_execution_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CONTRAST_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be feedback_reviewed_concept_replay_contrast_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be closed_loop_replay")
        if self.contrast_status not in ALLOWED_CONTRAST_STATUSES:
            raise ValueError(f"unknown contrast_status: {self.contrast_status}")
        for name in (
            "baseline_candidate_ordering",
            "readback_influenced_candidate_ordering",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "FeedbackReviewedConceptReplayContrastRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackReviewedConceptReplayRollbackRecord:
    replay_rollback_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_feedback_replay_gate_id: str
    source_replay_task_initialization_id: str | None
    source_replay_action_chain_id: str | None
    source_replay_execution_id: str | None
    replay_task_created_before_rollback: bool
    replay_task_available_after_rollback: bool
    sandbox_state_before_execution: dict | None
    sandbox_state_after_execution: dict | None
    sandbox_state_after_restore: dict | None
    rollback_available: bool
    rollback_applied: bool
    rollback_reason: str
    rollback_status: str
    rollback_summary: str
    external_execution_created: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    behavior_learning_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ROLLBACK_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be feedback_reviewed_concept_replay_rollback_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be closed_loop_replay")
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
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> "FeedbackReviewedConceptReplayRollbackRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class FeedbackReviewedConceptClosedLoopReplayAudit:
    closed_loop_replay_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_feedback_replay_gate_id: str | None
    source_replay_task_initialization_id: str | None
    source_replay_action_chain_id: str | None
    source_replay_execution_id: str | None
    source_replay_outcome_id: str | None
    source_replay_contrast_id: str | None
    source_replay_rollback_id: str | None
    feedback_reviewed_concept_valid: bool
    working_readback_integration_valid: bool
    readback_seed_valid: bool
    replay_gate_valid: bool
    replay_task_initialized: bool
    feedback_readback_visible: bool
    action_chain_replayed: bool
    bounded_sandbox_execution_valid: bool
    sense_observation_valid: bool
    outcome_evaluation_valid: bool
    task_closure_valid: bool
    contrast_valid: bool
    rollback_available: bool
    closed_loop_replay_completed: bool
    no_external_execution: bool
    no_unity_execution: bool
    no_bridge_execution: bool
    no_network_execution: bool
    no_filesystem_execution: bool
    no_learning_feedback_candidate_from_replay: bool
    no_new_reviewed_concept_from_replay: bool
    no_memory_write: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_automatic_learning_approval: bool
    no_behavior_learning: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be feedback_reviewed_concept_closed_loop_replay_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be closed_loop_replay")
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
    ) -> "FeedbackReviewedConceptClosedLoopReplayAudit":
        return cls(**dict(data))


def build_feedback_reviewed_concept_replay_gate(
    *,
    reviewed_concept: FeedbackDerivedReviewedConceptRecord | dict[str, object],
    working_readback_integration: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord
    | dict[str, object],
    readback_seed: FeedbackDerivedReviewedConceptReadbackSeedRecord | dict[str, object] | None,
    integration_safety_audit: FeedbackDerivedReviewedConceptIntegrationSafetyAudit
    | dict[str, object],
    replay_task_id: str = "feedback_replay_task:demo",
    replay_sandbox_id: str = "bounded_sandbox:feedback_replay_demo",
    teacher_gate_status: str = APPROVED_GATE_STATUS,
    teacher_gate_reason: str | None = None,
    teacher_gate_text: str = "Demo gate approves closed-loop replay in bounded sandbox only.",
    approval_actor: str = "system_demo",
    approval_actor_role: str = "system_demo",
    approval_source: str = "demo_review",
    created_at: str | None = None,
) -> FeedbackReviewedConceptReplayGate:
    reviewed = _reviewed_concept(reviewed_concept)
    integration = _working_readback_integration(working_readback_integration)
    seed = _readback_seed(readback_seed) if readback_seed is not None else None
    audit = _integration_safety_audit(integration_safety_audit)
    status = _replay_gate_status(
        requested_status=teacher_gate_status,
        reviewed=reviewed,
        integration=integration,
        seed=seed,
        integration_audit=audit,
    )
    approved = status == APPROVED_GATE_STATUS
    source_refs = _combined_trace_refs(
        reviewed.source_trace_refs,
        integration.source_trace_refs,
        seed.source_trace_refs if seed else (),
        audit.source_trace_refs,
    )
    return FeedbackReviewedConceptReplayGate(
        feedback_replay_gate_id=(
            "feedback_reviewed_concept_replay_gate:"
            f"{reviewed.feedback_derived_reviewed_concept_id}"
        ),
        schema_version=GATE_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_feedback_derived_reviewed_concept_id=(
            reviewed.feedback_derived_reviewed_concept_id
        ),
        source_working_readback_integration_id=integration.working_readback_integration_id,
        source_readback_seed_id=seed.readback_seed_id if seed else "",
        source_feedback_integration_safety_audit_id=(
            audit.feedback_reviewed_concept_integration_safety_audit_id
        ),
        replay_task_id=replay_task_id,
        replay_sandbox_id=replay_sandbox_id,
        reviewed_concept_label=reviewed.reviewed_concept_label,
        reviewed_concept_scope=reviewed.reviewed_concept_scope,
        readback_hint_label=seed.hint_label if seed else "",
        readback_hint_kind=seed.hint_kind if seed else "",
        teacher_gate_status=status,
        teacher_gate_reason=teacher_gate_reason or _gate_reason(status),
        teacher_gate_text=teacher_gate_text,
        approval_actor=approval_actor,
        approval_actor_role=approval_actor_role,
        approval_source=approval_source,
        approved_for_closed_loop_replay=approved,
        approved_for_bounded_sandbox_execution=approved,
        approved_for_external_execution=False,
        approved_for_unity_execution=False,
        approved_for_bridge_execution=False,
        approved_for_free_action_selection=False,
        approved_for_memory_layer_write=False,
        approved_for_automatic_learning_approval=False,
        approved_for_behavior_learning=False,
        requires_replay_rollback=True,
        requires_replay_audit=True,
        requires_baseline_contrast=True,
        source_trace_refs=source_refs,
    )


def validate_feedback_reviewed_concept_replay_gate(
    gate: FeedbackReviewedConceptReplayGate | dict[str, object],
) -> dict[str, object]:
    try:
        record = _replay_gate(gate)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_replay_gate:{error}",)}
    errors: list[str] = []
    approved = record.teacher_gate_status == APPROVED_GATE_STATUS
    if record.approved_for_closed_loop_replay is not approved:
        errors.append("closed_loop_replay_approval_mismatch")
    if record.approved_for_bounded_sandbox_execution is not approved:
        errors.append("bounded_execution_approval_mismatch")
    if record.approval_source == "explicit_teacher_review":
        if record.approval_actor_role not in {"teacher", "project_owner"}:
            errors.append("explicit_review_requires_teacher_or_project_owner")
        if not record.teacher_gate_text.strip():
            errors.append("explicit_review_requires_teacher_gate_text")
    elif record.approval_source == "demo_review":
        if record.approval_actor_role != "system_demo":
            errors.append("demo_review_requires_system_demo_role")
    else:
        errors.append("invalid_approval_source")
    for flag in (
        "approved_for_external_execution",
        "approved_for_unity_execution",
        "approved_for_bridge_execution",
        "approved_for_free_action_selection",
        "approved_for_memory_layer_write",
        "approved_for_automatic_learning_approval",
        "approved_for_behavior_learning",
    ):
        if getattr(record, flag):
            errors.append(f"{flag}_true")
    for flag in (
        "requires_replay_rollback",
        "requires_replay_audit",
        "requires_baseline_contrast",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "feedback_replay_gate_id": record.feedback_replay_gate_id,
        "teacher_gate_status": record.teacher_gate_status,
    }


def initialize_feedback_reviewed_concept_replay_task(
    *,
    replay_gate: FeedbackReviewedConceptReplayGate | dict[str, object] | None,
    readback_seed: FeedbackDerivedReviewedConceptReadbackSeedRecord | dict[str, object] | None,
    baseline_candidate_ordering: tuple[str, ...] | list[str] = (
        "step_forward",
        "observe",
        "turn_left",
    ),
    target_task_is_running: bool = False,
    include_readback: bool = True,
    created_at: str | None = None,
) -> FeedbackReviewedConceptReplayTaskInitializationRecord:
    gate = _replay_gate(replay_gate) if replay_gate is not None else None
    seed = _readback_seed(readback_seed) if readback_seed is not None else None
    baseline = _tuple_of_str("baseline_candidate_ordering", baseline_candidate_ordering)
    seed_valid = seed is not None and _readback_seed_valid(seed)
    if target_task_is_running:
        status = "blocked_running_task_mutation_attempt"
    elif gate is None or gate.teacher_gate_status != APPROVED_GATE_STATUS:
        status = "blocked_invalid_replay_gate"
    elif include_readback and not seed_valid:
        status = "blocked_invalid_readback_seed"
    elif include_readback:
        status = INITIALIZED_WITH_READBACK_STATUS
    else:
        status = "replay_task_initialized_without_readback_baseline"
    initialized = status in {
        INITIALIZED_WITH_READBACK_STATUS,
        "replay_task_initialized_without_readback_baseline",
    }
    readback_applied = status == INITIALIZED_WITH_READBACK_STATUS
    task_id = gate.replay_task_id if gate is not None else "missing:replay_task"
    working_memory_id = f"task_working_memory:{task_id}"
    return FeedbackReviewedConceptReplayTaskInitializationRecord(
        replay_task_initialization_id=f"feedback_replay_task_initialization:{task_id}",
        schema_version=TASK_INITIALIZATION_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=TASK_ENGINE,
        source_feedback_replay_gate_id=gate.feedback_replay_gate_id if gate else "",
        source_feedback_derived_reviewed_concept_id=(
            gate.source_feedback_derived_reviewed_concept_id if gate else ""
        ),
        source_readback_seed_id=seed.readback_seed_id if seed else "",
        replay_task_id=task_id,
        replay_task_working_memory_id=working_memory_id,
        replay_sandbox_id=gate.replay_sandbox_id if gate else "missing:sandbox",
        baseline_candidate_ordering=baseline,
        readback_hint_applied=readback_applied,
        readback_hint_id=seed.readback_seed_id if readback_applied and seed else None,
        readback_hint_label=seed.hint_label if readback_applied and seed else None,
        readback_hint_kind=seed.hint_kind if readback_applied and seed else None,
        task_working_memory_initialized=initialized,
        working_memory_readback_slot_populated=readback_applied,
        candidate_ordering_changed_at_initialization=False,
        selected_action_created_at_initialization=False,
        final_action_created_at_initialization=False,
        direct_command_created_at_initialization=False,
        execution_created_at_initialization=False,
        initialization_status=status,
        initialization_summary=_initialization_summary(status),
        source_trace_refs=_combined_trace_refs(
            gate.source_trace_refs if gate else (),
            seed.source_trace_refs if seed else (),
        ),
    )


def validate_feedback_reviewed_concept_replay_task_initialization(
    initialization: FeedbackReviewedConceptReplayTaskInitializationRecord
    | dict[str, object],
) -> dict[str, object]:
    try:
        record = _task_initialization(initialization)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_initialization:{error}",)}
    errors: list[str] = []
    if record.initialization_status == INITIALIZED_WITH_READBACK_STATUS:
        if not record.task_working_memory_initialized:
            errors.append("task_working_memory_not_initialized")
        if not record.working_memory_readback_slot_populated:
            errors.append("readback_slot_not_populated")
        if not record.readback_hint_applied or not record.readback_hint_id:
            errors.append("readback_hint_not_applied")
    for flag in (
        "candidate_ordering_changed_at_initialization",
        "selected_action_created_at_initialization",
        "final_action_created_at_initialization",
        "direct_command_created_at_initialization",
        "execution_created_at_initialization",
    ):
        if getattr(record, flag):
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "replay_task_initialization_id": record.replay_task_initialization_id,
        "initialization_status": record.initialization_status,
    }


def build_feedback_reviewed_concept_replay_action_chain(
    *,
    replay_gate: FeedbackReviewedConceptReplayGate | dict[str, object] | None,
    replay_task_initialization: FeedbackReviewedConceptReplayTaskInitializationRecord
    | dict[str, object],
    readback_seed: FeedbackDerivedReviewedConceptReadbackSeedRecord | dict[str, object] | None,
    forced_candidate_ordering: tuple[str, ...] | list[str] | None = None,
    external_execution_created: bool = False,
    unity_execution_created: bool = False,
    bridge_execution_created: bool = False,
    network_execution_created: bool = False,
    filesystem_execution_created: bool = False,
    created_at: str | None = None,
) -> FeedbackReviewedConceptReplayActionChainRecord:
    gate = _replay_gate(replay_gate) if replay_gate is not None else None
    initialization = _task_initialization(replay_task_initialization)
    seed = _readback_seed(readback_seed) if readback_seed is not None else None
    forbidden = any(
        (
            external_execution_created,
            unity_execution_created,
            bridge_execution_created,
            network_execution_created,
            filesystem_execution_created,
        )
    )
    baseline = initialization.baseline_candidate_ordering
    if forced_candidate_ordering is not None:
        requested = _tuple_of_str("forced_candidate_ordering", forced_candidate_ordering)
    else:
        requested = compute_feedback_reviewed_concept_replay_ordering(
            baseline,
            seed.to_dict() if seed is not None else None,
        )
    top = requested[0] if requested else None
    if forbidden:
        status = "blocked_forbidden_authority_detected"
    elif gate is None or gate.teacher_gate_status != APPROVED_GATE_STATUS:
        status = "replay_action_chain_blocked_before_ordering"
    elif not initialization.task_working_memory_initialized:
        status = "replay_action_chain_blocked_before_ordering"
    elif not requested:
        status = "replay_action_chain_blocked_before_selected_action"
    elif top not in ALLOWED_BOUNDED_DIRECT_COMMANDS:
        status = "replay_action_chain_blocked_before_direct_command"
    else:
        status = ACTION_CHAIN_DIRECT_COMMAND_STATUS
    built = status == ACTION_CHAIN_DIRECT_COMMAND_STATUS
    chain_id = (
        "feedback_replay_action_chain:"
        f"{initialization.replay_task_initialization_id}"
    )
    return FeedbackReviewedConceptReplayActionChainRecord(
        replay_action_chain_id=chain_id,
        schema_version=ACTION_CHAIN_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=TASK_ENGINE,
        source_feedback_replay_gate_id=gate.feedback_replay_gate_id if gate else "",
        source_replay_task_initialization_id=(
            initialization.replay_task_initialization_id
        ),
        source_feedback_derived_reviewed_concept_id=(
            initialization.source_feedback_derived_reviewed_concept_id
        ),
        replay_task_working_memory_id=initialization.replay_task_working_memory_id,
        baseline_candidate_ordering=baseline,
        readback_influenced_candidate_ordering=requested,
        candidate_ordering_application_id=(
            f"feedback_replay_ordering_application:{chain_id}" if built else None
        ),
        selected_action_proposal_id=(
            f"feedback_replay_selected_action_proposal:{chain_id}" if built else None
        ),
        selected_action_application_id=(
            f"feedback_replay_selected_action_application:{chain_id}" if built else None
        ),
        final_action_application_id=(
            f"feedback_replay_final_action_application:{chain_id}" if built else None
        ),
        direct_command_application_id=(
            f"feedback_replay_direct_command_application:{chain_id}" if built else None
        ),
        selected_action_candidate_id=top if built else None,
        final_action_candidate_id=top if built else None,
        direct_command=top if built else None,
        candidate_ordering_changed=tuple(requested) != tuple(baseline),
        selected_action_created=built,
        final_action_created=built,
        direct_command_created=built,
        execution_created=False,
        external_execution_created=external_execution_created,
        unity_execution_created=unity_execution_created,
        bridge_execution_created=bridge_execution_created,
        network_execution_created=network_execution_created,
        filesystem_execution_created=filesystem_execution_created,
        action_chain_status=status,
        action_chain_summary=_action_chain_summary(status, top),
        source_trace_refs=_combined_trace_refs(
            initialization.source_trace_refs,
            gate.source_trace_refs if gate else (),
            seed.source_trace_refs if seed else (),
        ),
    )


def validate_feedback_reviewed_concept_replay_action_chain(
    action_chain: FeedbackReviewedConceptReplayActionChainRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _action_chain(action_chain)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_action_chain:{error}",)}
    errors: list[str] = []
    built = record.action_chain_status == ACTION_CHAIN_DIRECT_COMMAND_STATUS
    if built:
        if not record.selected_action_created:
            errors.append("selected_action_not_created")
        if not record.final_action_created:
            errors.append("final_action_not_created")
        if not record.direct_command_created:
            errors.append("direct_command_not_created")
        if record.direct_command not in ALLOWED_BOUNDED_DIRECT_COMMANDS:
            errors.append("unsupported_direct_command")
    if record.candidate_ordering_changed is not (
        record.baseline_candidate_ordering
        != record.readback_influenced_candidate_ordering
    ):
        errors.append("candidate_ordering_changed_mismatch")
    for flag in (
        "execution_created",
        "external_execution_created",
        "unity_execution_created",
        "bridge_execution_created",
        "network_execution_created",
        "filesystem_execution_created",
    ):
        if getattr(record, flag):
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "replay_action_chain_id": record.replay_action_chain_id,
        "action_chain_status": record.action_chain_status,
    }


def execute_feedback_reviewed_concept_replay_sandbox(
    *,
    replay_gate: FeedbackReviewedConceptReplayGate | dict[str, object] | None,
    replay_action_chain: FeedbackReviewedConceptReplayActionChainRecord
    | dict[str, object],
    external_execution_created: bool = False,
    unity_execution_created: bool = False,
    bridge_execution_created: bool = False,
    network_execution_created: bool = False,
    filesystem_execution_created: bool = False,
    task_behavior_learning_created: bool = False,
    memory_layer_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    created_at: str | None = None,
) -> FeedbackReviewedConceptReplayExecutionRecord:
    gate = _replay_gate(replay_gate) if replay_gate is not None else None
    chain = _action_chain(replay_action_chain)
    direct_command = chain.direct_command
    forbidden_execution = any(
        (
            external_execution_created,
            unity_execution_created,
            bridge_execution_created,
            network_execution_created,
            filesystem_execution_created,
        )
    )
    forbidden_authority = any(
        (
            task_behavior_learning_created,
            memory_layer_write_performed,
            automatic_learning_approval_created,
        )
    )
    if forbidden_execution:
        status = "blocked_external_execution_attempt"
    elif forbidden_authority:
        status = "blocked_forbidden_authority_detected"
    elif chain.action_chain_status != ACTION_CHAIN_DIRECT_COMMAND_STATUS:
        status = "blocked_invalid_action_chain"
    elif direct_command not in ALLOWED_BOUNDED_DIRECT_COMMANDS:
        status = "blocked_unsupported_direct_command"
    elif gate is None or not gate.approved_for_bounded_sandbox_execution:
        status = "replay_execution_blocked_before_execution"
    else:
        status = EXECUTION_COMPLETED_STATUS
    completed = status == EXECUTION_COMPLETED_STATUS
    execution_id = f"feedback_replay_execution:{chain.replay_action_chain_id}"
    return FeedbackReviewedConceptReplayExecutionRecord(
        replay_execution_id=execution_id,
        schema_version=EXECUTION_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=TASK_ENGINE,
        source_feedback_replay_gate_id=gate.feedback_replay_gate_id if gate else "",
        source_replay_action_chain_id=chain.replay_action_chain_id,
        source_direct_command_application_id=chain.direct_command_application_id,
        replay_task_working_memory_id=chain.replay_task_working_memory_id,
        replay_sandbox_id=gate.replay_sandbox_id if gate else "missing:sandbox",
        direct_command=direct_command if completed else direct_command,
        sandbox_execution_id=f"sandbox_execution:{execution_id}" if completed else None,
        pre_execution_snapshot_id=(
            f"sandbox_pre_execution_snapshot:{execution_id}" if completed else None
        ),
        sandbox_restore_id=f"sandbox_execution_restore:{execution_id}" if completed else None,
        sandbox_execution_audit_id=(
            f"direct_command_sandbox_execution_audit:{execution_id}"
            if completed
            else None
        ),
        sandbox_execution_created=completed,
        bounded_sandbox_execution_created=completed,
        external_execution_created=external_execution_created,
        unity_execution_created=unity_execution_created,
        bridge_execution_created=bridge_execution_created,
        network_execution_created=network_execution_created,
        filesystem_execution_created=filesystem_execution_created,
        execution_status=status,
        execution_summary=_execution_summary(status, direct_command),
        restore_available=completed,
        rollback_available=completed,
        task_behavior_learning_created=task_behavior_learning_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        source_trace_refs=_combined_trace_refs(
            chain.source_trace_refs,
            gate.source_trace_refs if gate else (),
        ),
    )


def validate_feedback_reviewed_concept_replay_execution(
    execution: FeedbackReviewedConceptReplayExecutionRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _execution(execution)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_execution:{error}",)}
    errors: list[str] = []
    completed = record.execution_status == EXECUTION_COMPLETED_STATUS
    if record.sandbox_execution_created is not completed:
        errors.append("sandbox_execution_created_mismatch")
    if record.bounded_sandbox_execution_created is not completed:
        errors.append("bounded_execution_created_mismatch")
    if completed:
        for field_name in (
            "sandbox_execution_id",
            "pre_execution_snapshot_id",
            "sandbox_restore_id",
            "sandbox_execution_audit_id",
        ):
            if not getattr(record, field_name):
                errors.append(f"missing_{field_name}")
    for flag in (
        "external_execution_created",
        "unity_execution_created",
        "bridge_execution_created",
        "network_execution_created",
        "filesystem_execution_created",
        "task_behavior_learning_created",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag):
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "replay_execution_id": record.replay_execution_id,
        "execution_status": record.execution_status,
    }


def build_feedback_reviewed_concept_replay_outcome(
    *,
    replay_gate: FeedbackReviewedConceptReplayGate | dict[str, object] | None,
    replay_execution: FeedbackReviewedConceptReplayExecutionRecord | dict[str, object],
    reviewed_concept: FeedbackDerivedReviewedConceptRecord | dict[str, object],
    learning_feedback_candidate_created: bool = False,
    new_reviewed_concept_created_from_replay: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    created_at: str | None = None,
) -> FeedbackReviewedConceptReplayOutcomeRecord:
    gate = _replay_gate(replay_gate) if replay_gate is not None else None
    execution = _execution(replay_execution)
    reviewed = _reviewed_concept(reviewed_concept)
    if learning_feedback_candidate_created:
        status = "blocked_learning_feedback_created"
    elif memory_write_performed:
        status = "blocked_memory_write_detected"
    elif automatic_learning_approval_created:
        status = "blocked_automatic_learning_approval_detected"
    elif execution.execution_status == EXECUTION_COMPLETED_STATUS:
        status = OUTCOME_CLOSED_STATUS
    else:
        status = "replay_outcome_blocked"
    closed = status == OUTCOME_CLOSED_STATUS
    outcome_id = f"feedback_replay_outcome:{execution.replay_execution_id}"
    direct_command = execution.direct_command if execution.direct_command else None
    outcome_class, goal_delta_class, closure_status, expected_effect = _outcome_for_command(
        direct_command
    )
    return FeedbackReviewedConceptReplayOutcomeRecord(
        replay_outcome_id=outcome_id,
        schema_version=OUTCOME_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_feedback_replay_gate_id=gate.feedback_replay_gate_id if gate else "",
        source_replay_execution_id=execution.replay_execution_id,
        source_feedback_derived_reviewed_concept_id=(
            reviewed.feedback_derived_reviewed_concept_id
        ),
        sense_observation_id=f"sense_sandbox_observation:{outcome_id}" if closed else None,
        sense_handoff_id=f"sense_sandbox_handoff:{outcome_id}" if closed else None,
        outcome_evaluation_id=f"task_outcome_evaluation:{outcome_id}" if closed else None,
        goal_delta_evaluation_id=f"task_goal_delta_evaluation:{outcome_id}" if closed else None,
        task_closure_id=f"task_closure:{outcome_id}" if closed else None,
        direct_command=direct_command,
        expected_effect=expected_effect if closed else None,
        outcome_class=outcome_class if closed else None,
        goal_delta_class=goal_delta_class if closed else None,
        closure_status=closure_status if closed else None,
        sense_observation_created=closed,
        outcome_evaluation_created=closed,
        task_closure_created=closed,
        learning_feedback_candidate_created=learning_feedback_candidate_created,
        new_reviewed_concept_created_from_replay=new_reviewed_concept_created_from_replay,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        outcome_status=status,
        outcome_summary=_outcome_summary(status, direct_command),
        source_trace_refs=_combined_trace_refs(
            execution.source_trace_refs,
            reviewed.source_trace_refs,
            gate.source_trace_refs if gate else (),
        ),
    )


def validate_feedback_reviewed_concept_replay_outcome(
    outcome: FeedbackReviewedConceptReplayOutcomeRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _outcome(outcome)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_outcome:{error}",)}
    errors: list[str] = []
    if record.outcome_status == OUTCOME_CLOSED_STATUS:
        for flag in (
            "sense_observation_created",
            "outcome_evaluation_created",
            "task_closure_created",
        ):
            if getattr(record, flag) is not True:
                errors.append(f"{flag}_false")
        for field_name in (
            "sense_observation_id",
            "sense_handoff_id",
            "outcome_evaluation_id",
            "goal_delta_evaluation_id",
            "task_closure_id",
        ):
            if not getattr(record, field_name):
                errors.append(f"missing_{field_name}")
    for flag in (
        "learning_feedback_candidate_created",
        "new_reviewed_concept_created_from_replay",
        "memory_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag):
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "replay_outcome_id": record.replay_outcome_id,
        "outcome_status": record.outcome_status,
    }


def build_feedback_reviewed_concept_replay_contrast(
    *,
    replay_gate: FeedbackReviewedConceptReplayGate | dict[str, object] | None,
    replay_task_initialization: FeedbackReviewedConceptReplayTaskInitializationRecord
    | dict[str, object]
    | None,
    replay_action_chain: FeedbackReviewedConceptReplayActionChainRecord
    | dict[str, object]
    | None,
    replay_execution: FeedbackReviewedConceptReplayExecutionRecord | dict[str, object] | None,
    baseline_direct_command: str | None = None,
    external_execution_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    created_at: str | None = None,
) -> FeedbackReviewedConceptReplayContrastRecord:
    gate = _replay_gate(replay_gate) if replay_gate is not None else None
    initialization = (
        _task_initialization(replay_task_initialization)
        if replay_task_initialization is not None
        else None
    )
    chain = _action_chain(replay_action_chain) if replay_action_chain is not None else None
    execution = _execution(replay_execution) if replay_execution is not None else None
    baseline = initialization.baseline_candidate_ordering if initialization else ()
    influenced = chain.readback_influenced_candidate_ordering if chain else ()
    baseline_top = baseline[0] if baseline else None
    influenced_top = influenced[0] if influenced else None
    baseline_command = baseline_direct_command if baseline_direct_command is not None else baseline_top
    influenced_command = chain.direct_command if chain else None
    if external_execution_created or memory_write_performed or automatic_learning_approval_created:
        status = "blocked_forbidden_authority_detected"
    elif initialization is None or not baseline:
        status = "blocked_missing_baseline"
    elif chain is None or not influenced:
        status = "blocked_missing_replay_chain"
    elif influenced != baseline or influenced_command != baseline_command:
        status = CONTRAST_INFLUENCED_STATUS
    elif initialization.working_memory_readback_slot_populated:
        status = CONTRAST_NO_DIFFERENCE_STATUS
    else:
        status = "blocked_missing_replay_chain"
    return FeedbackReviewedConceptReplayContrastRecord(
        replay_contrast_id=(
            "feedback_replay_contrast:"
            f"{initialization.replay_task_initialization_id if initialization else 'missing'}"
        ),
        schema_version=CONTRAST_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_feedback_replay_gate_id=gate.feedback_replay_gate_id if gate else "",
        source_replay_task_initialization_id=(
            initialization.replay_task_initialization_id if initialization else ""
        ),
        source_replay_action_chain_id=chain.replay_action_chain_id if chain else "",
        source_replay_execution_id=execution.replay_execution_id if execution else None,
        baseline_candidate_ordering=baseline,
        readback_influenced_candidate_ordering=influenced,
        baseline_top_candidate=baseline_top,
        readback_influenced_top_candidate=influenced_top,
        baseline_direct_command=baseline_command,
        readback_influenced_direct_command=influenced_command,
        candidate_ordering_changed_by_feedback_readback=bool(
            baseline and influenced and influenced != baseline
        ),
        selected_action_changed_by_feedback_readback=bool(
            baseline_top and influenced_top and baseline_top != influenced_top
        ),
        final_action_changed_by_feedback_readback=bool(
            baseline_top and influenced_top and baseline_top != influenced_top
        ),
        direct_command_changed_by_feedback_readback=bool(
            baseline_command and influenced_command and baseline_command != influenced_command
        ),
        execution_created_by_feedback_replay=bool(
            execution and execution.execution_status == EXECUTION_COMPLETED_STATUS
        ),
        contrast_status=status,
        contrast_summary=_contrast_summary(status, baseline_top, influenced_top),
        external_execution_created=external_execution_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        source_trace_refs=_combined_trace_refs(
            initialization.source_trace_refs if initialization else (),
            chain.source_trace_refs if chain else (),
            execution.source_trace_refs if execution else (),
            gate.source_trace_refs if gate else (),
        ),
    )


def validate_feedback_reviewed_concept_replay_contrast(
    contrast: FeedbackReviewedConceptReplayContrastRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _contrast(contrast)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_contrast:{error}",)}
    errors: list[str] = []
    if record.contrast_status == CONTRAST_INFLUENCED_STATUS:
        if not (
            record.candidate_ordering_changed_by_feedback_readback
            or record.direct_command_changed_by_feedback_readback
        ):
            errors.append("no_feedback_readback_difference_recorded")
    if record.contrast_status == CONTRAST_NO_DIFFERENCE_STATUS:
        if record.candidate_ordering_changed_by_feedback_readback:
            errors.append("visible_no_difference_has_ordering_change")
    for flag in (
        "external_execution_created",
        "memory_write_performed",
        "automatic_learning_approval_created",
    ):
        if getattr(record, flag):
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "replay_contrast_id": record.replay_contrast_id,
        "contrast_status": record.contrast_status,
    }


def build_feedback_reviewed_concept_replay_rollback(
    *,
    replay_gate: FeedbackReviewedConceptReplayGate | dict[str, object] | None,
    replay_task_initialization: FeedbackReviewedConceptReplayTaskInitializationRecord
    | dict[str, object]
    | None,
    replay_action_chain: FeedbackReviewedConceptReplayActionChainRecord
    | dict[str, object]
    | None,
    replay_execution: FeedbackReviewedConceptReplayExecutionRecord | dict[str, object] | None,
    rollback_applied: bool = False,
    rollback_reason: str = "Rollback data prepared for feedback ReviewedConcept replay.",
    external_execution_created: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    behavior_learning_created: bool = False,
    created_at: str | None = None,
) -> FeedbackReviewedConceptReplayRollbackRecord:
    gate = _replay_gate(replay_gate) if replay_gate is not None else None
    initialization = (
        _task_initialization(replay_task_initialization)
        if replay_task_initialization is not None
        else None
    )
    chain = _action_chain(replay_action_chain) if replay_action_chain is not None else None
    execution = _execution(replay_execution) if replay_execution is not None else None
    forbidden = any(
        (
            external_execution_created,
            memory_write_performed,
            automatic_learning_approval_created,
            behavior_learning_created,
        )
    )
    task_created = bool(initialization and initialization.task_working_memory_initialized)
    execution_completed = bool(
        execution and execution.execution_status == EXECUTION_COMPLETED_STATUS
    )
    before_state = {"position": 0, "observations": 0}
    after_state = (
        _sandbox_state_after_command(before_state, execution.direct_command)
        if execution_completed and execution
        else None
    )
    if forbidden:
        status = "blocked_forbidden_authority_detected"
    elif not task_created:
        status = "blocked_invalid_replay_record"
    elif rollback_applied and execution_completed:
        status = "rollback_applied_to_restore_sandbox_state"
    elif rollback_applied:
        status = "rollback_applied_to_withdraw_replay_task_records"
    else:
        status = "rollback_record_created"
    rollback_available = status != "blocked_invalid_replay_record" and not status.startswith(
        "blocked_forbidden"
    )
    return FeedbackReviewedConceptReplayRollbackRecord(
        replay_rollback_id=(
            "feedback_replay_rollback:"
            f"{initialization.replay_task_initialization_id if initialization else 'missing'}"
        ),
        schema_version=ROLLBACK_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_feedback_replay_gate_id=gate.feedback_replay_gate_id if gate else "",
        source_replay_task_initialization_id=(
            initialization.replay_task_initialization_id if initialization else None
        ),
        source_replay_action_chain_id=chain.replay_action_chain_id if chain else None,
        source_replay_execution_id=execution.replay_execution_id if execution else None,
        replay_task_created_before_rollback=task_created,
        replay_task_available_after_rollback=not rollback_applied if task_created else False,
        sandbox_state_before_execution=before_state if execution_completed else None,
        sandbox_state_after_execution=after_state,
        sandbox_state_after_restore=(
            before_state
            if rollback_applied and execution_completed
            else after_state
            if execution_completed
            else None
        ),
        rollback_available=rollback_available,
        rollback_applied=rollback_applied and rollback_available,
        rollback_reason=rollback_reason,
        rollback_status=status,
        rollback_summary=_rollback_summary(status),
        external_execution_created=external_execution_created,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        behavior_learning_created=behavior_learning_created,
        source_trace_refs=_combined_trace_refs(
            initialization.source_trace_refs if initialization else (),
            chain.source_trace_refs if chain else (),
            execution.source_trace_refs if execution else (),
            gate.source_trace_refs if gate else (),
        ),
    )


def apply_feedback_reviewed_concept_replay_rollback(
    rollback_record: FeedbackReviewedConceptReplayRollbackRecord | dict[str, object],
) -> dict[str, object]:
    rollback = _rollback(rollback_record)
    if rollback.rollback_available and rollback.sandbox_state_before_execution is not None:
        status = "rollback_applied_to_restore_sandbox_state"
        sandbox_state = rollback.sandbox_state_before_execution
    elif rollback.rollback_available:
        status = "rollback_applied_to_withdraw_replay_task_records"
        sandbox_state = rollback.sandbox_state_after_restore
    else:
        status = "blocked_invalid_replay_record"
        sandbox_state = rollback.sandbox_state_after_restore
    return {
        "rollback_status": status,
        "replay_task_available_after_rollback": False,
        "sandbox_state_after_restore": sandbox_state,
        "external_execution_created": False,
        "memory_write_performed": False,
        "automatic_learning_approval_created": False,
        "behavior_learning_created": False,
    }


def validate_feedback_reviewed_concept_replay_rollback(
    rollback: FeedbackReviewedConceptReplayRollbackRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _rollback(rollback)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_rollback:{error}",)}
    errors: list[str] = []
    if not record.rollback_available:
        errors.append("rollback_not_available")
    if record.rollback_applied and record.replay_task_available_after_rollback:
        errors.append("replay_task_still_available_after_applied_rollback")
    if (
        record.rollback_applied
        and record.sandbox_state_before_execution is not None
        and record.sandbox_state_after_restore != record.sandbox_state_before_execution
    ):
        errors.append("sandbox_state_not_restored")
    for flag in (
        "external_execution_created",
        "memory_write_performed",
        "automatic_learning_approval_created",
        "behavior_learning_created",
    ):
        if getattr(record, flag):
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "replay_rollback_id": record.replay_rollback_id,
        "rollback_status": record.rollback_status,
    }


def build_feedback_reviewed_concept_closed_loop_replay_audit(
    *,
    reviewed_concept: FeedbackDerivedReviewedConceptRecord | dict[str, object],
    working_readback_integration: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord
    | dict[str, object],
    readback_seed: FeedbackDerivedReviewedConceptReadbackSeedRecord | dict[str, object] | None,
    integration_safety_audit: FeedbackDerivedReviewedConceptIntegrationSafetyAudit
    | dict[str, object],
    replay_gate: FeedbackReviewedConceptReplayGate | dict[str, object] | None,
    replay_task_initialization: FeedbackReviewedConceptReplayTaskInitializationRecord
    | dict[str, object]
    | None,
    replay_action_chain: FeedbackReviewedConceptReplayActionChainRecord
    | dict[str, object]
    | None,
    replay_execution: FeedbackReviewedConceptReplayExecutionRecord | dict[str, object] | None,
    replay_outcome: FeedbackReviewedConceptReplayOutcomeRecord | dict[str, object] | None,
    replay_contrast: FeedbackReviewedConceptReplayContrastRecord | dict[str, object] | None,
    replay_rollback: FeedbackReviewedConceptReplayRollbackRecord | dict[str, object] | None,
    created_at: str | None = None,
) -> FeedbackReviewedConceptClosedLoopReplayAudit:
    reviewed = _reviewed_concept(reviewed_concept)
    integration = _working_readback_integration(working_readback_integration)
    seed = _readback_seed(readback_seed) if readback_seed is not None else None
    integration_audit = _integration_safety_audit(integration_safety_audit)
    gate = _replay_gate(replay_gate) if replay_gate is not None else None
    initialization = (
        _task_initialization(replay_task_initialization)
        if replay_task_initialization is not None
        else None
    )
    chain = _action_chain(replay_action_chain) if replay_action_chain is not None else None
    execution = _execution(replay_execution) if replay_execution is not None else None
    outcome = _outcome(replay_outcome) if replay_outcome is not None else None
    contrast = _contrast(replay_contrast) if replay_contrast is not None else None
    rollback = _rollback(replay_rollback) if replay_rollback is not None else None

    reviewed_valid = _reviewed_concept_valid(reviewed)
    integration_valid = _working_readback_integration_valid(integration)
    seed_valid = seed is not None and _readback_seed_valid(seed)
    integration_audit_passed = (
        integration_audit.audit_status
        == "passed_feedback_reviewed_concept_working_readback_integration"
    )
    gate_valid = gate is not None and gate.teacher_gate_status == APPROVED_GATE_STATUS
    initialized = bool(
        initialization
        and initialization.initialization_status == INITIALIZED_WITH_READBACK_STATUS
    )
    readback_visible = bool(
        initialization and initialization.working_memory_readback_slot_populated
    )
    action_replayed = bool(
        chain and chain.action_chain_status == ACTION_CHAIN_DIRECT_COMMAND_STATUS
    )
    execution_valid = bool(
        execution and execution.execution_status == EXECUTION_COMPLETED_STATUS
    )
    sense_valid = bool(outcome and outcome.sense_observation_created)
    outcome_valid = bool(outcome and outcome.outcome_evaluation_created)
    closure_valid = bool(outcome and outcome.task_closure_created)
    contrast_valid = bool(
        contrast
        and contrast.contrast_status
        in {CONTRAST_INFLUENCED_STATUS, CONTRAST_NO_DIFFERENCE_STATUS}
    )
    rollback_available = bool(rollback and rollback.rollback_available)

    no_external = not _external_execution_detected(chain, execution, contrast, rollback)
    no_unity = not _field_true(chain, execution, field_name="unity_execution_created")
    no_bridge = not _field_true(chain, execution, field_name="bridge_execution_created")
    no_network = not _field_true(chain, execution, field_name="network_execution_created")
    no_filesystem = not _field_true(
        chain,
        execution,
        field_name="filesystem_execution_created",
    )
    no_feedback = not bool(outcome and outcome.learning_feedback_candidate_created)
    no_new_concept = not bool(outcome and outcome.new_reviewed_concept_created_from_replay)
    no_memory = not _memory_write_detected(execution, outcome, contrast, rollback)
    no_automatic = not _automatic_learning_detected(execution, outcome, contrast, rollback)
    no_behavior = not _behavior_learning_detected(execution, rollback)

    blocked = _audit_blocked_reasons(
        reviewed_valid=reviewed_valid,
        integration_valid=integration_valid and integration_audit_passed,
        seed_valid=seed_valid,
        gate_valid=gate_valid,
        initialized=initialized,
        action_replayed=action_replayed,
        execution_valid=execution_valid,
        outcome_valid=bool(outcome and outcome.outcome_status == OUTCOME_CLOSED_STATUS),
        contrast_valid=contrast_valid,
        rollback_available=rollback_available,
        no_external=no_external and no_unity and no_bridge and no_network and no_filesystem,
        no_feedback=no_feedback,
        no_new_concept=no_new_concept,
        no_memory=no_memory,
        no_automatic=no_automatic,
        no_behavior=no_behavior,
    )
    status = _audit_status(blocked, contrast)
    return FeedbackReviewedConceptClosedLoopReplayAudit(
        closed_loop_replay_audit_id=(
            "feedback_closed_loop_replay_audit:"
            f"{reviewed.feedback_derived_reviewed_concept_id}"
        ),
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        source_feedback_replay_gate_id=gate.feedback_replay_gate_id if gate else None,
        source_replay_task_initialization_id=(
            initialization.replay_task_initialization_id if initialization else None
        ),
        source_replay_action_chain_id=chain.replay_action_chain_id if chain else None,
        source_replay_execution_id=execution.replay_execution_id if execution else None,
        source_replay_outcome_id=outcome.replay_outcome_id if outcome else None,
        source_replay_contrast_id=contrast.replay_contrast_id if contrast else None,
        source_replay_rollback_id=rollback.replay_rollback_id if rollback else None,
        feedback_reviewed_concept_valid=reviewed_valid,
        working_readback_integration_valid=integration_valid and integration_audit_passed,
        readback_seed_valid=seed_valid,
        replay_gate_valid=gate_valid,
        replay_task_initialized=initialized,
        feedback_readback_visible=readback_visible,
        action_chain_replayed=action_replayed,
        bounded_sandbox_execution_valid=execution_valid,
        sense_observation_valid=sense_valid,
        outcome_evaluation_valid=outcome_valid,
        task_closure_valid=closure_valid,
        contrast_valid=contrast_valid,
        rollback_available=rollback_available,
        closed_loop_replay_completed=status
        in {AUDIT_PASSED_STATUS, AUDIT_NO_DIFFERENCE_STATUS},
        no_external_execution=no_external,
        no_unity_execution=no_unity,
        no_bridge_execution=no_bridge,
        no_network_execution=no_network,
        no_filesystem_execution=no_filesystem,
        no_learning_feedback_candidate_from_replay=no_feedback,
        no_new_reviewed_concept_from_replay=no_new_concept,
        no_memory_write=no_memory,
        no_core_memory_write=no_memory,
        no_long_term_memory_write=no_memory,
        no_archive_memory_write=no_memory,
        no_anchor_write=no_memory,
        no_automatic_learning_approval=no_automatic,
        no_behavior_learning=no_behavior,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(blocked),
        source_trace_refs=_combined_trace_refs(
            reviewed.source_trace_refs,
            integration.source_trace_refs,
            seed.source_trace_refs if seed else (),
            integration_audit.source_trace_refs,
            gate.source_trace_refs if gate else (),
            initialization.source_trace_refs if initialization else (),
            chain.source_trace_refs if chain else (),
            execution.source_trace_refs if execution else (),
            outcome.source_trace_refs if outcome else (),
            contrast.source_trace_refs if contrast else (),
            rollback.source_trace_refs if rollback else (),
        ),
    )


def validate_feedback_reviewed_concept_closed_loop_replay_audit(
    audit: FeedbackReviewedConceptClosedLoopReplayAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _closed_loop_audit(audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_audit:{error}",)}
    errors: list[str] = []
    if record.audit_status not in {AUDIT_PASSED_STATUS, AUDIT_NO_DIFFERENCE_STATUS}:
        errors.append(record.audit_status)
    if record.closed_loop_replay_completed is not (
        record.audit_status in {AUDIT_PASSED_STATUS, AUDIT_NO_DIFFERENCE_STATUS}
    ):
        errors.append("closed_loop_completion_mismatch")
    for flag in (
        "no_external_execution",
        "no_unity_execution",
        "no_bridge_execution",
        "no_network_execution",
        "no_filesystem_execution",
        "no_learning_feedback_candidate_from_replay",
        "no_new_reviewed_concept_from_replay",
        "no_memory_write",
        "no_core_memory_write",
        "no_long_term_memory_write",
        "no_archive_memory_write",
        "no_anchor_write",
        "no_automatic_learning_approval",
        "no_behavior_learning",
    ):
        if getattr(record, flag) is not True:
            errors.append(f"{flag}_false")
    if not record.rollback_available:
        errors.append("rollback_missing")
    if not set(BLOCKED_CLAIMS).issubset(set(record.blocked_claims)):
        errors.append("blocked_claims_missing")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "closed_loop_replay_audit_id": record.closed_loop_replay_audit_id,
        "audit_status": record.audit_status,
        "blocked_reasons": record.blocked_reasons,
    }


def compute_feedback_reviewed_concept_replay_ordering(
    baseline_candidate_ordering: tuple[str, ...] | list[str],
    readback_hint: FeedbackDerivedReviewedConceptReadbackSeedRecord
    | dict[str, object]
    | None,
) -> tuple[str, ...]:
    baseline = list(_tuple_of_str("baseline_candidate_ordering", baseline_candidate_ordering))
    if not baseline or readback_hint is None:
        return tuple(baseline)
    seed = _readback_seed(readback_hint)
    hint_kind = seed.hint_kind
    if hint_kind in {
        "avoid_repeated_failure",
        "observe_before_retry",
        "no_progress_warning",
        "verify_expected_actual",
        "verify_scope",
    }:
        return _promote_and_demote(baseline, promote="observe", demote="step_forward")
    if hint_kind in {"use_known_success_path", "goal_completion_hint"}:
        return _promote_candidate(baseline, "step_forward")
    return tuple(baseline)


def build_demo_negative_affordance_closed_loop_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(case="negative-affordance")


def build_demo_positive_affordance_closed_loop_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(case="positive-affordance")


def build_demo_goal_completion_closed_loop_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(case="goal-completion")


def build_demo_no_progress_closed_loop_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(case="no-progress")


def build_demo_observation_context_closed_loop_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(case="observation-context")


def build_demo_visible_no_action_difference_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(
        case="observation-context",
        baseline_candidate_ordering=("observe", "turn_left", "step_forward"),
        force_visible_no_difference=True,
    )


def build_demo_closed_loop_replay_case(case: str) -> dict[str, object]:
    cases = {
        "negative-affordance": build_demo_negative_affordance_closed_loop_replay,
        "positive-affordance": build_demo_positive_affordance_closed_loop_replay,
        "goal-completion": build_demo_goal_completion_closed_loop_replay,
        "no-progress": build_demo_no_progress_closed_loop_replay,
        "observation-context": build_demo_observation_context_closed_loop_replay,
        "visible-no-action-difference": build_demo_visible_no_action_difference_replay,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown demo replay case: {case}") from error


def build_demo_blocked_invalid_feedback_reviewed_concept_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(block_case="invalid-feedback-reviewed-concept")


def build_demo_blocked_invalid_readback_integration_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(block_case="invalid-readback-integration")


def build_demo_blocked_missing_replay_gate() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(block_case="missing-replay-gate")


def build_demo_blocked_teacher_rejected_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(block_case="teacher-rejected")


def build_demo_blocked_running_task_mutation_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(block_case="running-task-mutation")


def build_demo_blocked_external_execution_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(block_case="external-execution")


def build_demo_blocked_unity_execution_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(block_case="unity-execution")


def build_demo_blocked_bridge_execution_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(block_case="bridge-execution")


def build_demo_blocked_memory_write_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(block_case="memory-write-detected")


def build_demo_blocked_automatic_learning_approval_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(block_case="automatic-learning-approval")


def build_demo_blocked_behavior_learning_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(block_case="behavior-learning")


def build_demo_blocked_learning_feedback_created_from_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(
        block_case="learning-feedback-created-from-replay"
    )


def build_demo_blocked_new_reviewed_concept_created_from_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(
        block_case="new-reviewed-concept-created-from-replay"
    )


def build_demo_blocked_missing_rollback_replay() -> dict[str, object]:
    return _build_closed_loop_replay_bundle(block_case="missing-rollback")


def build_demo_blocked_feedback_reviewed_concept_closed_loop_replay(
    case: str,
) -> dict[str, object]:
    cases = {
        "invalid-feedback-reviewed-concept": build_demo_blocked_invalid_feedback_reviewed_concept_replay,
        "invalid-readback-integration": build_demo_blocked_invalid_readback_integration_replay,
        "missing-replay-gate": build_demo_blocked_missing_replay_gate,
        "teacher-rejected": build_demo_blocked_teacher_rejected_replay,
        "running-task-mutation": build_demo_blocked_running_task_mutation_replay,
        "external-execution": build_demo_blocked_external_execution_replay,
        "unity-execution": build_demo_blocked_unity_execution_replay,
        "bridge-execution": build_demo_blocked_bridge_execution_replay,
        "memory-write-detected": build_demo_blocked_memory_write_replay,
        "automatic-learning-approval": build_demo_blocked_automatic_learning_approval_replay,
        "behavior-learning": build_demo_blocked_behavior_learning_replay,
        "learning-feedback-created-from-replay": build_demo_blocked_learning_feedback_created_from_replay,
        "new-reviewed-concept-created-from-replay": build_demo_blocked_new_reviewed_concept_created_from_replay,
        "missing-rollback": build_demo_blocked_missing_rollback_replay,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown blocked replay case: {case}") from error


def _build_closed_loop_replay_bundle(
    *,
    case: str = "negative-affordance",
    block_case: str | None = None,
    baseline_candidate_ordering: tuple[str, ...] = (
        "step_forward",
        "observe",
        "turn_left",
    ),
    force_visible_no_difference: bool = False,
) -> dict[str, object]:
    source_case = case
    if block_case is not None:
        source_case = "negative-affordance"
    source = build_demo_feedback_reviewed_concept_integration_case(source_case)
    reviewed = FeedbackDerivedReviewedConceptRecord.from_dict(
        source["feedback_derived_reviewed_concept"]
    )
    integration = FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord.from_dict(
        source["feedback_derived_reviewed_concept_working_readback_integration"]
    )
    seed_payload = source.get("feedback_derived_reviewed_concept_readback_seed")
    seed = (
        FeedbackDerivedReviewedConceptReadbackSeedRecord.from_dict(seed_payload)
        if isinstance(seed_payload, dict)
        else None
    )
    integration_audit = FeedbackDerivedReviewedConceptIntegrationSafetyAudit.from_dict(
        source["feedback_derived_reviewed_concept_integration_safety_audit"]
    )

    if block_case == "invalid-feedback-reviewed-concept":
        reviewed = replace(
            reviewed,
            reviewed_concept_status="rejected_by_teacher",
            available_for_working_readback_integration=False,
        )
    if block_case == "invalid-readback-integration":
        integration = replace(
            integration,
            working_readback_integration_status="blocked_invalid_reviewed_concept",
            available_for_future_task_working_memory_readback=False,
        )
    if block_case == "invalid-readback-integration":
        integration_audit = replace(
            integration_audit,
            audit_status="blocked_invalid_working_readback_integration",
            working_readback_integration_valid=False,
        )

    gate: FeedbackReviewedConceptReplayGate | None
    if block_case == "missing-replay-gate":
        gate = None
    else:
        gate_status = "rejected" if block_case == "teacher-rejected" else APPROVED_GATE_STATUS
        gate = build_feedback_reviewed_concept_replay_gate(
            reviewed_concept=reviewed,
            working_readback_integration=integration,
            readback_seed=seed,
            integration_safety_audit=integration_audit,
            teacher_gate_status=gate_status,
            replay_task_id=f"feedback_replay_task:{source_case}",
            replay_sandbox_id=f"bounded_sandbox:feedback_replay:{source_case}",
        )
    initialization = initialize_feedback_reviewed_concept_replay_task(
        replay_gate=gate,
        readback_seed=seed,
        baseline_candidate_ordering=baseline_candidate_ordering,
        target_task_is_running=block_case == "running-task-mutation",
    )
    forced_ordering = (
        baseline_candidate_ordering if force_visible_no_difference else None
    )
    action_chain = build_feedback_reviewed_concept_replay_action_chain(
        replay_gate=gate,
        replay_task_initialization=initialization,
        readback_seed=seed,
        forced_candidate_ordering=forced_ordering,
    )
    execution = execute_feedback_reviewed_concept_replay_sandbox(
        replay_gate=gate,
        replay_action_chain=action_chain,
        external_execution_created=block_case == "external-execution",
        unity_execution_created=block_case == "unity-execution",
        bridge_execution_created=block_case == "bridge-execution",
        task_behavior_learning_created=block_case == "behavior-learning",
        memory_layer_write_performed=block_case == "memory-write-detected",
        automatic_learning_approval_created=block_case
        == "automatic-learning-approval",
    )
    outcome = build_feedback_reviewed_concept_replay_outcome(
        replay_gate=gate,
        replay_execution=execution,
        reviewed_concept=reviewed,
        learning_feedback_candidate_created=block_case
        == "learning-feedback-created-from-replay",
        new_reviewed_concept_created_from_replay=block_case
        == "new-reviewed-concept-created-from-replay",
        memory_write_performed=block_case == "memory-write-detected",
        automatic_learning_approval_created=block_case
        == "automatic-learning-approval",
    )
    contrast = build_feedback_reviewed_concept_replay_contrast(
        replay_gate=gate,
        replay_task_initialization=initialization,
        replay_action_chain=action_chain,
        replay_execution=execution,
    )
    rollback = None
    if block_case != "missing-rollback":
        rollback = build_feedback_reviewed_concept_replay_rollback(
            replay_gate=gate,
            replay_task_initialization=initialization,
            replay_action_chain=action_chain,
            replay_execution=execution,
            rollback_applied=True,
            memory_write_performed=block_case == "memory-write-detected",
            automatic_learning_approval_created=block_case
            == "automatic-learning-approval",
            behavior_learning_created=block_case == "behavior-learning",
        )
    audit = build_feedback_reviewed_concept_closed_loop_replay_audit(
        reviewed_concept=reviewed,
        working_readback_integration=integration,
        readback_seed=seed,
        integration_safety_audit=integration_audit,
        replay_gate=gate,
        replay_task_initialization=initialization,
        replay_action_chain=action_chain,
        replay_execution=execution,
        replay_outcome=outcome,
        replay_contrast=contrast,
        replay_rollback=rollback,
    )
    return {
        **source,
        "feedback_reviewed_concept_replay_gate": gate.to_dict() if gate else None,
        "feedback_reviewed_concept_replay_task_initialization": initialization.to_dict(),
        "feedback_reviewed_concept_replay_action_chain": action_chain.to_dict(),
        "feedback_reviewed_concept_replay_execution": execution.to_dict(),
        "feedback_reviewed_concept_replay_outcome": outcome.to_dict(),
        "feedback_reviewed_concept_replay_contrast": contrast.to_dict(),
        "feedback_reviewed_concept_replay_rollback": (
            rollback.to_dict() if rollback else None
        ),
        "feedback_reviewed_concept_closed_loop_replay_audit": audit.to_dict(),
        "closed_loop_replay_case": source_case,
        "blocked_case": block_case,
    }


def _replay_gate_status(
    *,
    requested_status: str,
    reviewed: FeedbackDerivedReviewedConceptRecord,
    integration: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord,
    seed: FeedbackDerivedReviewedConceptReadbackSeedRecord | None,
    integration_audit: FeedbackDerivedReviewedConceptIntegrationSafetyAudit,
) -> str:
    if not _reviewed_concept_valid(reviewed):
        return "blocked_invalid_feedback_reviewed_concept"
    if not _working_readback_integration_valid(integration):
        return "blocked_invalid_working_readback_integration"
    if not _integration_audit_valid(integration_audit):
        return "blocked_invalid_working_readback_integration"
    if seed is None or not _readback_seed_valid(seed):
        return "blocked_invalid_readback_seed"
    if requested_status in {
        APPROVED_GATE_STATUS,
        "held_for_more_evidence",
        "rejected",
        "conflict_detected",
    }:
        return requested_status
    return "blocked_forbidden_authority_detected"


def _reviewed_concept_valid(reviewed: FeedbackDerivedReviewedConceptRecord) -> bool:
    validation = validate_feedback_derived_reviewed_concept_record(reviewed)
    return (
        bool(validation["valid"])
        and reviewed.reviewed_concept_status == "feedback_reviewed_concept_created"
        and reviewed.available_for_working_readback_integration
        and not reviewed.core_memory_write_performed
        and not reviewed.long_term_memory_write_performed
        and not reviewed.archive_memory_write_performed
        and not reviewed.anchor_write_performed
        and not reviewed.automatic_learning_approval_created
    )


def _working_readback_integration_valid(
    integration: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord,
) -> bool:
    validation = validate_feedback_derived_reviewed_concept_working_readback_integration_record(
        integration
    )
    return (
        bool(validation["valid"])
        and integration.working_readback_integration_status == "integrated_to_working_readback"
        and integration.available_for_future_task_working_memory_readback
    )


def _integration_audit_valid(
    audit: FeedbackDerivedReviewedConceptIntegrationSafetyAudit,
) -> bool:
    validation = validate_feedback_derived_reviewed_concept_integration_safety_audit(audit)
    return (
        bool(validation["valid"])
        and audit.audit_status
        == "passed_feedback_reviewed_concept_working_readback_integration"
    )


def _readback_seed_valid(seed: FeedbackDerivedReviewedConceptReadbackSeedRecord) -> bool:
    validation = validate_feedback_derived_reviewed_concept_readback_seed_record(seed)
    return (
        bool(validation["valid"])
        and seed.available_for_future_task_working_memory_hint_application
        and seed.advisory_only
        and seed.single_task_lifetime
        and seed.future_task_initialization_only
    )


def _gate_reason(status: str) -> str:
    return {
        APPROVED_GATE_STATUS: "Teacher gate permits bounded closed-loop replay only.",
        "held_for_more_evidence": "Replay held for more evidence.",
        "rejected": "Teacher gate rejected replay.",
        "conflict_detected": "Conflict detected before replay.",
        "blocked_invalid_feedback_reviewed_concept": "Feedback ReviewedConcept is invalid.",
        "blocked_invalid_working_readback_integration": "Working readback integration is invalid.",
        "blocked_invalid_readback_seed": "Readback seed is invalid.",
        "blocked_forbidden_authority_detected": "Forbidden authority was requested.",
    }[status]


def _initialization_summary(status: str) -> str:
    return {
        INITIALIZED_WITH_READBACK_STATUS: (
            "Replay task initialized with feedback-derived readback hint visible."
        ),
        "replay_task_initialized_without_readback_baseline": (
            "Replay baseline initialized without readback."
        ),
        "blocked_invalid_replay_gate": "Replay task initialization blocked by gate.",
        "blocked_invalid_readback_seed": "Replay task initialization blocked by seed.",
        "blocked_running_task_mutation_attempt": (
            "Replay refused running task mutation."
        ),
        "blocked_forbidden_authority_detected": "Forbidden authority was detected.",
    }[status]


def _action_chain_summary(status: str, top: str | None) -> str:
    if status == ACTION_CHAIN_DIRECT_COMMAND_STATUS:
        return f"Replay action chain reached direct_command {top!r}."
    return {
        "replay_action_chain_built_to_final_action_only": (
            "Replay action chain stopped at final_action."
        ),
        "replay_action_chain_blocked_before_ordering": (
            "Replay action chain blocked before candidate ordering."
        ),
        "replay_action_chain_blocked_before_selected_action": (
            "Replay action chain blocked before selected_action."
        ),
        "replay_action_chain_blocked_before_final_action": (
            "Replay action chain blocked before final_action."
        ),
        "replay_action_chain_blocked_before_direct_command": (
            "Replay action chain blocked before direct_command."
        ),
        "blocked_forbidden_authority_detected": "Forbidden action authority detected.",
    }[status]


def _execution_summary(status: str, direct_command: str | None) -> str:
    if status == EXECUTION_COMPLETED_STATUS:
        return f"Bounded sandbox replay execution completed for {direct_command!r}."
    return {
        "replay_execution_blocked_before_execution": "Replay execution was not approved.",
        "blocked_invalid_action_chain": "Replay execution blocked by invalid action chain.",
        "blocked_unsupported_direct_command": (
            "Replay execution blocked by unsupported direct command."
        ),
        "blocked_external_execution_attempt": (
            "Replay execution blocked external execution attempt."
        ),
        "blocked_forbidden_authority_detected": (
            "Replay execution blocked forbidden authority."
        ),
    }[status]


def _outcome_summary(status: str, direct_command: str | None) -> str:
    if status == OUTCOME_CLOSED_STATUS:
        return f"Replay outcome observed, evaluated, and closed for {direct_command!r}."
    return {
        "replay_outcome_observed_only": "Replay outcome observed only.",
        "replay_outcome_evaluated_not_closed": "Replay outcome evaluated but not closed.",
        "replay_outcome_blocked": "Replay outcome blocked before closure.",
        "blocked_learning_feedback_created": (
            "Replay blocked recursive LearningFeedbackCandidate creation."
        ),
        "blocked_memory_write_detected": "Replay blocked memory write.",
        "blocked_automatic_learning_approval_detected": (
            "Replay blocked automatic learning approval."
        ),
    }[status]


def _contrast_summary(
    status: str,
    baseline_top: str | None,
    influenced_top: str | None,
) -> str:
    if status == CONTRAST_INFLUENCED_STATUS:
        return (
            "Feedback readback influenced the replay action chain: "
            f"{baseline_top!r} -> {influenced_top!r}."
        )
    if status == CONTRAST_NO_DIFFERENCE_STATUS:
        return "Feedback readback was visible but did not change the action chain."
    return {
        "blocked_missing_baseline": "Replay contrast missing baseline.",
        "blocked_missing_replay_chain": "Replay contrast missing replay chain.",
        "blocked_forbidden_authority_detected": (
            "Replay contrast detected forbidden authority."
        ),
    }[status]


def _rollback_summary(status: str) -> str:
    return {
        "rollback_record_created": "Replay rollback record created.",
        "rollback_applied_to_withdraw_replay_task_records": (
            "Replay task artifacts withdrawn."
        ),
        "rollback_applied_to_restore_sandbox_state": (
            "Replay sandbox state restored to pre-execution snapshot."
        ),
        "blocked_invalid_replay_record": "Rollback blocked by invalid replay record.",
        "blocked_forbidden_authority_detected": (
            "Rollback blocked forbidden authority."
        ),
    }[status]


def _outcome_for_command(
    direct_command: str | None,
) -> tuple[str, str, str, str]:
    if direct_command == "observe":
        return (
            "observation_only",
            "neutral_observation",
            "task_closed_observation_only",
            "observe_environment",
        )
    if direct_command in {"step_forward", "push_forward"}:
        return (
            "expected_effect_unverified",
            "no_progress",
            "task_closed_no_progress",
            "move_forward",
        )
    return (
        "bounded_action_observed",
        "neutral_observation",
        "task_closed_observation_only",
        "bounded_action_effect",
    )


def _promote_candidate(candidates: list[str], candidate: str) -> tuple[str, ...]:
    if candidate not in candidates:
        return tuple(candidates)
    return tuple([candidate] + [item for item in candidates if item != candidate])


def _promote_and_demote(
    candidates: list[str],
    *,
    promote: str,
    demote: str,
) -> tuple[str, ...]:
    ordered = list(candidates)
    if promote in ordered:
        ordered = [promote] + [item for item in ordered if item != promote]
    if demote in ordered:
        ordered = [item for item in ordered if item != demote] + [demote]
    return tuple(ordered)


def _sandbox_state_after_command(
    before: dict[str, int],
    direct_command: str | None,
) -> dict[str, int]:
    state = dict(before)
    if direct_command == "observe":
        state["observations"] = int(state.get("observations", 0)) + 1
    elif direct_command in {"step_forward", "push_forward"}:
        state["position"] = int(state.get("position", 0)) + 1
    elif direct_command in {"turn_left", "turn_right"}:
        state["turns"] = int(state.get("turns", 0)) + 1
    return state


def _audit_blocked_reasons(
    *,
    reviewed_valid: bool,
    integration_valid: bool,
    seed_valid: bool,
    gate_valid: bool,
    initialized: bool,
    action_replayed: bool,
    execution_valid: bool,
    outcome_valid: bool,
    contrast_valid: bool,
    rollback_available: bool,
    no_external: bool,
    no_feedback: bool,
    no_new_concept: bool,
    no_memory: bool,
    no_automatic: bool,
    no_behavior: bool,
) -> list[str]:
    checks = (
        ("invalid_feedback_reviewed_concept", reviewed_valid),
        ("invalid_readback_integration", integration_valid),
        ("invalid_readback_seed", seed_valid),
        ("invalid_replay_gate", gate_valid),
        ("replay_task_initialization_failed", initialized),
        ("action_chain_replay_failed", action_replayed),
        ("execution_failed", execution_valid),
        ("outcome_replay_failed", outcome_valid),
        ("contrast_failed", contrast_valid),
        ("missing_rollback", rollback_available),
        ("external_execution_detected", no_external),
        ("learning_feedback_candidate_created_from_replay", no_feedback),
        ("new_reviewed_concept_created_from_replay", no_new_concept),
        ("memory_write_detected", no_memory),
        ("automatic_learning_approval_detected", no_automatic),
        ("behavior_learning_detected", no_behavior),
    )
    return [name for name, passed in checks if not passed]


def _audit_status(
    blocked_reasons: list[str],
    contrast: FeedbackReviewedConceptReplayContrastRecord | None,
) -> str:
    if not blocked_reasons:
        if contrast and contrast.contrast_status == CONTRAST_NO_DIFFERENCE_STATUS:
            return AUDIT_NO_DIFFERENCE_STATUS
        return AUDIT_PASSED_STATUS
    priority = (
        ("invalid_feedback_reviewed_concept", "blocked_invalid_feedback_reviewed_concept"),
        ("invalid_readback_integration", "blocked_invalid_readback_integration"),
        ("invalid_readback_seed", "blocked_invalid_readback_integration"),
        ("invalid_replay_gate", "blocked_invalid_replay_gate"),
        ("replay_task_initialization_failed", "blocked_replay_task_initialization_failed"),
        ("action_chain_replay_failed", "blocked_action_chain_replay_failed"),
        ("external_execution_detected", "blocked_external_execution_detected"),
        ("memory_write_detected", "blocked_memory_write_detected"),
        (
            "automatic_learning_approval_detected",
            "blocked_automatic_learning_approval_detected",
        ),
        ("behavior_learning_detected", "blocked_behavior_learning_detected"),
        ("execution_failed", "blocked_execution_failed"),
        ("learning_feedback_candidate_created_from_replay", "blocked_outcome_replay_failed"),
        ("new_reviewed_concept_created_from_replay", "blocked_outcome_replay_failed"),
        ("outcome_replay_failed", "blocked_outcome_replay_failed"),
        ("contrast_failed", "blocked_contrast_failed"),
        ("missing_rollback", "blocked_missing_rollback"),
    )
    for reason, status in priority:
        if reason in blocked_reasons:
            return status
    return "blocked_contrast_failed"


def _external_execution_detected(
    chain: FeedbackReviewedConceptReplayActionChainRecord | None,
    execution: FeedbackReviewedConceptReplayExecutionRecord | None,
    contrast: FeedbackReviewedConceptReplayContrastRecord | None,
    rollback: FeedbackReviewedConceptReplayRollbackRecord | None,
) -> bool:
    return any(
        (
            bool(chain and chain.external_execution_created),
            bool(execution and execution.external_execution_created),
            bool(contrast and contrast.external_execution_created),
            bool(rollback and rollback.external_execution_created),
        )
    )


def _field_true(*records: object | None, field_name: str) -> bool:
    return any(bool(record and getattr(record, field_name, False)) for record in records)


def _memory_write_detected(
    execution: FeedbackReviewedConceptReplayExecutionRecord | None,
    outcome: FeedbackReviewedConceptReplayOutcomeRecord | None,
    contrast: FeedbackReviewedConceptReplayContrastRecord | None,
    rollback: FeedbackReviewedConceptReplayRollbackRecord | None,
) -> bool:
    return any(
        (
            bool(execution and execution.memory_layer_write_performed),
            bool(outcome and outcome.memory_write_performed),
            bool(contrast and contrast.memory_write_performed),
            bool(rollback and rollback.memory_write_performed),
        )
    )


def _automatic_learning_detected(
    execution: FeedbackReviewedConceptReplayExecutionRecord | None,
    outcome: FeedbackReviewedConceptReplayOutcomeRecord | None,
    contrast: FeedbackReviewedConceptReplayContrastRecord | None,
    rollback: FeedbackReviewedConceptReplayRollbackRecord | None,
) -> bool:
    return any(
        (
            bool(execution and execution.automatic_learning_approval_created),
            bool(outcome and outcome.automatic_learning_approval_created),
            bool(contrast and contrast.automatic_learning_approval_created),
            bool(rollback and rollback.automatic_learning_approval_created),
        )
    )


def _behavior_learning_detected(
    execution: FeedbackReviewedConceptReplayExecutionRecord | None,
    rollback: FeedbackReviewedConceptReplayRollbackRecord | None,
) -> bool:
    return any(
        (
            bool(execution and execution.task_behavior_learning_created),
            bool(rollback and rollback.behavior_learning_created),
        )
    )


def _reviewed_concept(
    value: FeedbackDerivedReviewedConceptRecord | dict[str, object],
) -> FeedbackDerivedReviewedConceptRecord:
    if isinstance(value, FeedbackDerivedReviewedConceptRecord):
        return value
    return FeedbackDerivedReviewedConceptRecord.from_dict(value)


def _working_readback_integration(
    value: FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord
    | dict[str, object],
) -> FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord:
    if isinstance(value, FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord):
        return value
    return FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord.from_dict(value)


def _readback_seed(
    value: FeedbackDerivedReviewedConceptReadbackSeedRecord | dict[str, object],
) -> FeedbackDerivedReviewedConceptReadbackSeedRecord:
    if isinstance(value, FeedbackDerivedReviewedConceptReadbackSeedRecord):
        return value
    return FeedbackDerivedReviewedConceptReadbackSeedRecord.from_dict(value)


def _integration_safety_audit(
    value: FeedbackDerivedReviewedConceptIntegrationSafetyAudit | dict[str, object],
) -> FeedbackDerivedReviewedConceptIntegrationSafetyAudit:
    if isinstance(value, FeedbackDerivedReviewedConceptIntegrationSafetyAudit):
        return value
    return FeedbackDerivedReviewedConceptIntegrationSafetyAudit.from_dict(value)


def _replay_gate(
    value: FeedbackReviewedConceptReplayGate | dict[str, object],
) -> FeedbackReviewedConceptReplayGate:
    if isinstance(value, FeedbackReviewedConceptReplayGate):
        return value
    return FeedbackReviewedConceptReplayGate.from_dict(value)


def _task_initialization(
    value: FeedbackReviewedConceptReplayTaskInitializationRecord | dict[str, object],
) -> FeedbackReviewedConceptReplayTaskInitializationRecord:
    if isinstance(value, FeedbackReviewedConceptReplayTaskInitializationRecord):
        return value
    return FeedbackReviewedConceptReplayTaskInitializationRecord.from_dict(value)


def _action_chain(
    value: FeedbackReviewedConceptReplayActionChainRecord | dict[str, object],
) -> FeedbackReviewedConceptReplayActionChainRecord:
    if isinstance(value, FeedbackReviewedConceptReplayActionChainRecord):
        return value
    return FeedbackReviewedConceptReplayActionChainRecord.from_dict(value)


def _execution(
    value: FeedbackReviewedConceptReplayExecutionRecord | dict[str, object],
) -> FeedbackReviewedConceptReplayExecutionRecord:
    if isinstance(value, FeedbackReviewedConceptReplayExecutionRecord):
        return value
    return FeedbackReviewedConceptReplayExecutionRecord.from_dict(value)


def _outcome(
    value: FeedbackReviewedConceptReplayOutcomeRecord | dict[str, object],
) -> FeedbackReviewedConceptReplayOutcomeRecord:
    if isinstance(value, FeedbackReviewedConceptReplayOutcomeRecord):
        return value
    return FeedbackReviewedConceptReplayOutcomeRecord.from_dict(value)


def _contrast(
    value: FeedbackReviewedConceptReplayContrastRecord | dict[str, object],
) -> FeedbackReviewedConceptReplayContrastRecord:
    if isinstance(value, FeedbackReviewedConceptReplayContrastRecord):
        return value
    return FeedbackReviewedConceptReplayContrastRecord.from_dict(value)


def _rollback(
    value: FeedbackReviewedConceptReplayRollbackRecord | dict[str, object],
) -> FeedbackReviewedConceptReplayRollbackRecord:
    if isinstance(value, FeedbackReviewedConceptReplayRollbackRecord):
        return value
    return FeedbackReviewedConceptReplayRollbackRecord.from_dict(value)


def _closed_loop_audit(
    value: FeedbackReviewedConceptClosedLoopReplayAudit | dict[str, object],
) -> FeedbackReviewedConceptClosedLoopReplayAudit:
    if isinstance(value, FeedbackReviewedConceptClosedLoopReplayAudit):
        return value
    return FeedbackReviewedConceptClosedLoopReplayAudit.from_dict(value)
