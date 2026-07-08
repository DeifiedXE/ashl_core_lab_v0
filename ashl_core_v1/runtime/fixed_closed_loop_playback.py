"""Fixed Package 94 closed-loop playback over Runtime EventFrames."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.audit.first_action_to_reviewed_concept_loop_milestone import (
    FirstClosedLoopEvidenceChainRecord,
    FirstClosedLoopMilestoneRecord,
    build_demo_first_closed_loop_milestone,
)
from ashl_core_v1.runtime.continuous_event_loop import (
    RuntimeContinuousLoopAudit,
    RuntimeContinuousLoopTrace,
    RuntimeEventFrameRecord,
    RuntimeEventReturnRecord,
    RuntimeEventStackRecord,
    RuntimeEventTreeRecord,
    RuntimePowerWindowRecord,
    RuntimeTickRecord,
    build_runtime_continuous_loop_audit,
    build_runtime_continuous_loop_trace,
    build_runtime_event_frames_from_timeline,
    build_runtime_event_return_records,
    build_runtime_event_stack_records,
    build_runtime_event_tree_record,
    build_runtime_power_window_record,
    build_runtime_tick_records_from_timeline,
    normalize_runtime_timeline_text,
)
from ashl_core_v1.runtime.event_frame_dispatch_adapter import (
    RuntimeEventDispatchAudit,
    RuntimeEventDispatchRequestRecord,
    RuntimeEventDispatchResultRecord,
    RuntimeEventDispatchReturnPayloadRecord,
    RuntimeEventDispatchRouteRecord,
    RuntimeEventHandlerAdapterRecord,
    dispatch_event_frame_adapter_only,
)
from ashl_core_v1.runtime.event_return_parent_resume import (
    RuntimeParentFrameResumeAudit,
    RuntimeParentFrameResumeDecisionRecord,
    RuntimeParentFrameResumeRecord,
    RuntimeParentFrameResumeRequestRecord,
    RuntimeParentFrameResumeStackUpdateRecord,
    resume_parent_frame_from_child_return,
)
from ashl_core_v1.runtime.integrated_event_loop_trace import (
    RuntimeIntegratedEventDispatchResumeLinkRecord,
    RuntimeIntegratedEventLoopAudit,
    RuntimeIntegratedEventLoopReadinessRecord,
    RuntimeIntegratedEventLoopTimelineRenderRecord,
    RuntimeIntegratedEventLoopTrace,
    RuntimeIntegratedEventStepRecord,
    build_runtime_integrated_dispatch_resume_link_record,
    build_runtime_integrated_event_loop_audit,
    build_runtime_integrated_event_loop_readiness,
    build_runtime_integrated_event_loop_timeline_render,
    build_runtime_integrated_event_loop_trace,
    build_runtime_integrated_event_step_record,
)


SOURCE_ENGINE = "runtime"
PLAYBACK_PLAN_SCHEMA_VERSION = "runtime_fixed_closed_loop_playback_plan_v0"
STAGE_MAPPING_SCHEMA_VERSION = "runtime_closed_loop_stage_to_event_frame_mapping_v0"
PLAYBACK_STEP_SCHEMA_VERSION = "runtime_fixed_closed_loop_playback_step_v0"
PLAYBACK_TRACE_SCHEMA_VERSION = "runtime_fixed_closed_loop_playback_trace_v0"
PLAYBACK_RENDER_SCHEMA_VERSION = "runtime_fixed_closed_loop_playback_render_v0"
PLAYBACK_AUDIT_SCHEMA_VERSION = "runtime_fixed_closed_loop_playback_audit_v0"
PLAYBACK_READINESS_SCHEMA_VERSION = "runtime_fixed_closed_loop_playback_readiness_v0"

PLAYBACK_NAME = "package_94_closed_loop_fixed_playback"
PLAYBACK_KIND = "fixed_bounded_record_playback"
PLAYBACK_WINDOW_KIND = "bounded_demo_window"
FIXED_PLAYBACK_TIMELINE = "....12121212121212121212121"

REQUIRED_CLOSED_LOOP_STAGES = (
    "first_task_action_chain",
    "sense_observation",
    "outcome_evaluation",
    "task_closure",
    "learning_feedback_candidate",
    "concept_candidate_draft",
    "feedback_concept_refinement",
    "feedback_derived_reviewed_concept",
    "working_readback_integration",
    "second_task_replay",
    "closed_loop_milestone_audit",
)
GROUPED_STAGE_MEMBERS = {
    "outcome_evaluation": ("outcome_evaluation", "task_closure"),
    "task_closure": ("outcome_evaluation", "task_closure"),
    "learning_feedback_candidate": (
        "learning_feedback_candidate",
        "concept_candidate_draft",
    ),
    "concept_candidate_draft": (
        "learning_feedback_candidate",
        "concept_candidate_draft",
    ),
    "feedback_derived_reviewed_concept": (
        "feedback_derived_reviewed_concept",
        "working_readback_integration",
    ),
    "working_readback_integration": (
        "feedback_derived_reviewed_concept",
        "working_readback_integration",
    ),
}
STAGE_CONFIG = {
    "first_task_action_chain": {
        "event_type": "fixed_playback_first_task_action_chain",
        "dispatch_event_type": "action_chain",
        "event_family": "task_event",
        "target_engine": "task_engine",
        "source_field": "first_task_sandbox_execution_id",
        "source_kind": "first_task_action_path",
    },
    "sense_observation": {
        "event_type": "fixed_playback_sense_observation",
        "dispatch_event_type": "sense_observation",
        "event_family": "sense_event",
        "target_engine": "sense_interface",
        "source_field": "sense_observation_id",
        "source_kind": "sense_observation",
    },
    "outcome_evaluation": {
        "event_type": "fixed_playback_outcome_evaluation",
        "dispatch_event_type": "outcome_evaluation",
        "event_family": "task_event",
        "target_engine": "task_engine",
        "source_field": "outcome_evaluation_id",
        "source_kind": "outcome_evaluation",
    },
    "task_closure": {
        "event_type": "fixed_playback_task_closure",
        "dispatch_event_type": "task_closure",
        "event_family": "task_event",
        "target_engine": "task_engine",
        "source_field": "task_closure_id",
        "source_kind": "task_closure",
    },
    "learning_feedback_candidate": {
        "event_type": "fixed_playback_learning_feedback_candidate",
        "dispatch_event_type": "learning_feedback_intake",
        "event_family": "learning_event",
        "target_engine": "learning_engine",
        "source_field": "learning_feedback_candidate_id",
        "source_kind": "learning_feedback_candidate",
    },
    "concept_candidate_draft": {
        "event_type": "fixed_playback_concept_candidate_draft",
        "dispatch_event_type": "concept_candidate_review",
        "event_family": "learning_event",
        "target_engine": "learning_engine",
        "source_field": "concept_candidate_draft_id",
        "source_kind": "concept_candidate_draft",
    },
    "feedback_concept_refinement": {
        "event_type": "fixed_playback_feedback_refinement",
        "dispatch_event_type": "concept_candidate_review",
        "event_family": "learning_event",
        "target_engine": "learning_engine",
        "source_field": "feedback_refinement_id",
        "source_kind": "feedback_concept_refinement",
    },
    "feedback_derived_reviewed_concept": {
        "event_type": "fixed_playback_feedback_reviewed_concept",
        "dispatch_event_type": "reviewed_concept_creation",
        "event_family": "learning_event",
        "target_engine": "learning_engine",
        "source_field": "feedback_derived_reviewed_concept_id",
        "source_kind": "feedback_derived_reviewed_concept",
    },
    "working_readback_integration": {
        "event_type": "fixed_playback_working_readback",
        "dispatch_event_type": "working_readback_integration",
        "event_family": "memory_event",
        "target_engine": "memory_engine",
        "source_field": "working_readback_integration_id",
        "source_kind": "working_readback_integration",
    },
    "second_task_replay": {
        "event_type": "fixed_playback_second_task_replay",
        "dispatch_event_type": "action_chain",
        "event_family": "task_event",
        "target_engine": "task_engine",
        "source_field": "replay_action_chain_id",
        "source_kind": "second_task_replay",
    },
    "closed_loop_milestone_audit": {
        "event_type": "fixed_playback_closed_loop_milestone_audit",
        "dispatch_event_type": "loop_audit",
        "event_family": "audit_event",
        "target_engine": "audit_layer",
        "source_field": None,
        "source_kind": "closed_loop_milestone_audit",
    },
}

ALLOWED_PLAN_STATUSES = {
    "playback_plan_created",
    "blocked_missing_closed_loop_milestone",
    "blocked_missing_integrated_event_loop_trace",
    "blocked_unbounded_playback",
    "blocked_forbidden_authority_detected",
}
ALLOWED_MAPPING_STATUSES = {
    "stage_mapped_to_event_frame",
    "stage_mapped_as_group_member",
    "blocked_unknown_closed_loop_stage",
    "blocked_missing_source_record",
    "blocked_invalid_event_frame_mapping",
    "blocked_forbidden_authority_detected",
}
ALLOWED_STEP_STATUSES = {
    "playback_step_recorded",
    "playback_step_recorded_with_grouped_stage",
    "playback_step_deferred_thought_not_available",
    "blocked_missing_stage_mapping",
    "blocked_missing_dispatch_resume_link",
    "blocked_live_handler_invocation_detected",
    "blocked_new_engine_behavior_detected",
    "blocked_forbidden_authority_detected",
}
ALLOWED_TRACE_STATUSES = {
    "fixed_closed_loop_playback_complete",
    "fixed_closed_loop_playback_complete_with_grouped_stages",
    "fixed_closed_loop_playback_blocked_missing_required_stage",
    "fixed_closed_loop_playback_blocked_missing_event_frame",
    "fixed_closed_loop_playback_blocked_missing_dispatch_lineage",
    "fixed_closed_loop_playback_blocked_missing_return_payload",
    "fixed_closed_loop_playback_blocked_missing_parent_resume",
    "fixed_closed_loop_playback_blocked_unclosed_root_frame",
    "fixed_closed_loop_playback_blocked_forbidden_authority_detected",
}
ALLOWED_RENDER_STATUSES = {
    "fixed_playback_render_created",
    "fixed_playback_render_created_with_grouped_stages",
    "fixed_playback_render_blocked_invalid_trace",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_fixed_closed_loop_playback_over_event_frames",
    "passed_fixed_closed_loop_playback_with_grouped_stages",
    "blocked_missing_closed_loop_milestone",
    "blocked_missing_required_stage",
    "blocked_missing_integrated_event_loop_trace",
    "blocked_missing_event_frame_mapping",
    "blocked_missing_dispatch_lineage",
    "blocked_missing_return_payload",
    "blocked_missing_parent_resume",
    "blocked_unclosed_root_event",
    "blocked_live_engine_invocation_detected",
    "blocked_dynamic_child_event_scheduling_detected",
    "blocked_autonomous_scheduler_detected",
    "blocked_open_ended_loop_detected",
    "blocked_external_execution_detected",
    "blocked_memory_write_detected",
    "blocked_automatic_learning_approval_detected",
    "blocked_recursive_learning_detected",
    "blocked_thought_engine_fake_detected",
    "blocked_first_output_detected",
    "blocked_production_behavior_detected",
}
ALLOWED_READINESS_STATUSES = {
    "ready_for_bounded_handler_binding_only",
    "ready_for_runtime_state_persistence_binding_only",
    "ready_for_teacher_observed_playback_cli_only",
    "not_ready_missing_fixed_playback",
    "not_ready_boundary_failure",
    "blocked_forbidden_authority_detected",
}

SAFE_CLAIM = (
    "ASHL Core v1 can represent its milestone-verified first bounded "
    "action-to-feedback-derived-ReviewedConcept-to-next-task loop as a fixed "
    "playback over Runtime EventFrames, linking each closed-loop stage to "
    "adapter-only dispatch, safe return payloads, parent resume, stack updates, "
    "render output, audit, and readiness records."
)
BLOCKED_CLAIMS = (
    "no_live_qingyin_runtime_session",
    "no_dynamic_child_event_scheduling",
    "no_autonomous_scheduler",
    "no_open_ended_loop",
    "no_live_engine_invocation",
    "no_external_execution",
    "no_memory_layer_write",
    "no_automatic_learning_approval",
    "no_recursive_learning",
    "no_new_learning_artifacts_from_playback",
    "no_thought_engine_cognition",
    "no_first_output",
    "not_awake",
)
READINESS_NEXT_PACKAGE = (
    "Package 100 / ASHL Core v1 Runtime Bounded Handler Binding For Fixed "
    "Closed Loop Playback Minimal v0"
)


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


def _slug(text: str) -> str:
    safe = []
    for char in text:
        if char.isalnum():
            safe.append(char.lower())
        elif char == ".":
            safe.append("dot")
        elif char == " ":
            safe.append("off")
        else:
            safe.append("_")
    value = "_".join("".join(safe).split("_"))[:90]
    return value or "empty"


@dataclass(frozen=True)
class RuntimeFixedClosedLoopPlaybackPlanRecord:
    playback_plan_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_closed_loop_milestone_id: str | None
    source_package_94_audit_id: str | None
    source_integrated_event_loop_trace_id: str | None
    playback_name: str
    playback_kind: str
    fixed_stage_sequence: tuple[str, ...]
    fixed_timeline_text: str
    canonical_timeline_text: str
    playback_window_kind: str
    bounded_tick_budget: int
    bounded_event_frame_budget: int
    playback_plan_status: str
    playback_plan_summary: str
    dynamic_child_event_scheduling_allowed: bool
    autonomous_scheduler_allowed: bool
    open_ended_loop_allowed: bool
    live_engine_invocation_allowed: bool
    external_execution_allowed: bool
    memory_layer_write_allowed: bool
    automatic_learning_approval_allowed: bool
    recursive_learning_allowed: bool
    thought_engine_runtime_allowed: bool
    first_output_allowed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PLAYBACK_PLAN_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_fixed_closed_loop_playback_plan_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.playback_name != PLAYBACK_NAME:
            raise ValueError("playback_name must be package_94_closed_loop_fixed_playback")
        if self.playback_kind != PLAYBACK_KIND:
            raise ValueError("playback_kind must be fixed_bounded_record_playback")
        if self.playback_window_kind != PLAYBACK_WINDOW_KIND:
            raise ValueError("playback_window_kind must be bounded_demo_window")
        if self.playback_plan_status not in ALLOWED_PLAN_STATUSES:
            raise ValueError(f"unknown playback_plan_status: {self.playback_plan_status}")
        for name in ("fixed_stage_sequence", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "RuntimeFixedClosedLoopPlaybackPlanRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeClosedLoopStageToEventFrameMappingRecord:
    stage_event_mapping_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_playback_plan_id: str
    closed_loop_stage_name: str
    closed_loop_stage_index: int
    source_closed_loop_record_id: str | None
    source_closed_loop_record_kind: str | None
    target_event_frame_id: str
    target_event_type: str
    target_event_family: str
    target_engine_lane: str
    mapping_status: str
    mapping_summary: str
    stage_represented: bool
    stage_grouped: bool
    stage_group_members: tuple[str, ...]
    dispatch_required: bool
    return_payload_required: bool
    parent_resume_required: bool
    live_engine_invocation_allowed: bool
    dynamic_child_event_scheduling_allowed: bool
    memory_layer_write_allowed: bool
    automatic_learning_approval_allowed: bool
    external_execution_allowed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != STAGE_MAPPING_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_closed_loop_stage_to_event_frame_mapping_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.mapping_status not in ALLOWED_MAPPING_STATUSES:
            raise ValueError(f"unknown mapping_status: {self.mapping_status}")
        for name in ("stage_group_members", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "RuntimeClosedLoopStageToEventFrameMappingRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeFixedClosedLoopPlaybackStepRecord:
    playback_step_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_playback_plan_id: str
    source_stage_event_mapping_id: str | None
    source_integrated_event_step_id: str | None
    source_dispatch_resume_link_id: str | None
    step_index: int
    closed_loop_stage_name: str
    event_frame_id: str
    event_type: str
    event_family: str
    target_engine_lane: str
    dispatch_status: str
    return_status: str
    parent_resume_status: str | None
    playback_step_status: str
    playback_step_summary: str
    stage_evidence_referenced: bool
    stage_replayed_as_record: bool
    live_handler_invoked: bool
    new_engine_behavior_created: bool
    new_learning_feedback_candidate_created: bool
    new_concept_candidate_created: bool
    new_reviewed_concept_created: bool
    new_memory_write_performed: bool
    new_sandbox_execution_performed: bool
    dynamic_child_event_created: bool
    external_execution_created: bool
    automatic_learning_approval_created: bool
    recursive_learning_created: bool
    thought_engine_behavior_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PLAYBACK_STEP_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_fixed_closed_loop_playback_step_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.playback_step_status not in ALLOWED_STEP_STATUSES:
            raise ValueError(f"unknown playback_step_status: {self.playback_step_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "RuntimeFixedClosedLoopPlaybackStepRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeFixedClosedLoopPlaybackTrace:
    fixed_playback_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_playback_plan_id: str
    source_integrated_event_loop_trace_id: str | None
    source_closed_loop_milestone_id: str | None
    stage_event_mapping_ids: tuple[str, ...]
    playback_step_ids: tuple[str, ...]
    fixed_stage_sequence: tuple[str, ...]
    represented_stage_sequence: tuple[str, ...]
    missing_required_stages: tuple[str, ...]
    timeline_text: str
    canonical_timeline_text: str
    playback_stage_count: int
    represented_stage_count: int
    all_required_stages_represented: bool
    all_steps_have_event_frames: bool
    all_steps_have_dispatch_lineage: bool
    all_steps_have_return_payloads: bool
    all_child_returns_resumed: bool
    root_frame_closed: bool
    fixed_playback_status: str
    fixed_playback_summary: str
    live_engine_invocation_created: bool
    dynamic_child_event_created: bool
    autonomous_scheduler_created: bool
    open_ended_loop_created: bool
    external_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    recursive_learning_created: bool
    thought_engine_behavior_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PLAYBACK_TRACE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_fixed_closed_loop_playback_trace_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.fixed_playback_status not in ALLOWED_TRACE_STATUSES:
            raise ValueError(f"unknown fixed_playback_status: {self.fixed_playback_status}")
        for name in (
            "stage_event_mapping_ids",
            "playback_step_ids",
            "fixed_stage_sequence",
            "represented_stage_sequence",
            "missing_required_stages",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeFixedClosedLoopPlaybackTrace":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeFixedClosedLoopPlaybackRenderRecord:
    fixed_playback_render_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_fixed_playback_trace_id: str
    timeline_text: str
    canonical_timeline_text: str
    human_readable_playback_text: str
    stage_summary_lines: tuple[str, ...]
    legend: dict[str, str]
    render_status: str
    render_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PLAYBACK_RENDER_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_fixed_closed_loop_playback_render_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.render_status not in ALLOWED_RENDER_STATUSES:
            raise ValueError(f"unknown render_status: {self.render_status}")
        for name in ("stage_summary_lines", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "RuntimeFixedClosedLoopPlaybackRenderRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeFixedClosedLoopPlaybackAudit:
    fixed_playback_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_playback_plan_id: str | None
    source_fixed_playback_trace_id: str | None
    source_fixed_playback_render_id: str | None
    closed_loop_milestone_valid: bool
    integrated_event_loop_trace_valid: bool
    playback_plan_valid: bool
    stage_mapping_valid: bool
    playback_steps_valid: bool
    playback_trace_valid: bool
    playback_render_valid: bool
    all_required_closed_loop_stages_represented: bool
    all_stages_mapped_to_event_frames: bool
    all_event_frames_dispatched: bool
    all_dispatches_returned: bool
    all_child_returns_resumed: bool
    root_event_closed: bool
    fixed_playback_only_confirmed: bool
    record_only_confirmed: bool
    adapter_only_confirmed: bool
    no_live_engine_invocation: bool
    no_dynamic_child_event_scheduling: bool
    no_autonomous_scheduler: bool
    no_open_ended_loop: bool
    no_background_daemon: bool
    no_external_execution: bool
    no_unity_execution: bool
    no_bridge_execution: bool
    no_network_execution: bool
    no_filesystem_execution: bool
    no_memory_layer_write: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_automatic_learning_approval: bool
    no_free_action_selection: bool
    no_recursive_learning: bool
    no_thought_engine_behavior: bool
    no_first_output: bool
    no_production_behavior: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PLAYBACK_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_fixed_closed_loop_playback_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeFixedClosedLoopPlaybackAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeFixedClosedLoopPlaybackReadinessRecord:
    fixed_playback_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_fixed_playback_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_bounded_handler_binding: bool
    ready_for_runtime_state_persistence_binding: bool
    ready_for_teacher_observed_playback_cli: bool
    ready_for_dynamic_child_event_scheduling: bool
    ready_for_autonomous_scheduler: bool
    ready_for_open_ended_loop: bool
    ready_for_live_engine_invocation: bool
    ready_for_external_execution: bool
    ready_for_memory_layer_write: bool
    ready_for_automatic_learning_approval: bool
    ready_for_recursive_learning: bool
    ready_for_thought_engine_runtime: bool
    ready_for_first_output: bool
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PLAYBACK_READINESS_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_fixed_closed_loop_playback_readiness_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.readiness_status not in ALLOWED_READINESS_STATUSES:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "RuntimeFixedClosedLoopPlaybackReadinessRecord":
        return cls(**dict(data))


def build_runtime_fixed_closed_loop_playback_plan(
    *,
    closed_loop_milestone: FirstClosedLoopMilestoneRecord | dict[str, object] | None,
    integrated_event_loop_trace: RuntimeIntegratedEventLoopTrace | dict[str, object] | None,
    fixed_stage_sequence: tuple[str, ...] | list[str] = REQUIRED_CLOSED_LOOP_STAGES,
    fixed_timeline_text: str = FIXED_PLAYBACK_TIMELINE,
    bounded_tick_budget: int = 64,
    bounded_event_frame_budget: int = 16,
    dynamic_child_event_scheduling_allowed: bool = False,
    autonomous_scheduler_allowed: bool = False,
    open_ended_loop_allowed: bool = False,
    live_engine_invocation_allowed: bool = False,
    external_execution_allowed: bool = False,
    memory_layer_write_allowed: bool = False,
    automatic_learning_approval_allowed: bool = False,
    recursive_learning_allowed: bool = False,
    thought_engine_runtime_allowed: bool = False,
    first_output_allowed: bool = False,
) -> RuntimeFixedClosedLoopPlaybackPlanRecord:
    milestone = _milestone(closed_loop_milestone) if closed_loop_milestone is not None else None
    integrated_trace = (
        _integrated_trace(integrated_event_loop_trace)
        if integrated_event_loop_trace is not None
        else None
    )
    sequence = tuple(fixed_stage_sequence)
    forbidden = any(
        (
            dynamic_child_event_scheduling_allowed,
            autonomous_scheduler_allowed,
            open_ended_loop_allowed,
            live_engine_invocation_allowed,
            external_execution_allowed,
            memory_layer_write_allowed,
            automatic_learning_approval_allowed,
            recursive_learning_allowed,
            thought_engine_runtime_allowed,
            first_output_allowed,
        )
    )
    if milestone is None:
        status = "blocked_missing_closed_loop_milestone"
    elif integrated_trace is None:
        status = "blocked_missing_integrated_event_loop_trace"
    elif not sequence or bounded_tick_budget <= 0 or bounded_event_frame_budget <= 0:
        status = "blocked_unbounded_playback"
    elif forbidden:
        status = "blocked_forbidden_authority_detected"
    else:
        status = "playback_plan_created"
    return RuntimeFixedClosedLoopPlaybackPlanRecord(
        playback_plan_id=f"runtime_fixed_closed_loop_playback_plan:{PLAYBACK_NAME}",
        schema_version=PLAYBACK_PLAN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_closed_loop_milestone_id=milestone.milestone_id if milestone else None,
        source_package_94_audit_id=milestone.source_boundary_audit_id if milestone else None,
        source_integrated_event_loop_trace_id=(
            integrated_trace.integrated_loop_trace_id if integrated_trace else None
        ),
        playback_name=PLAYBACK_NAME,
        playback_kind=PLAYBACK_KIND,
        fixed_stage_sequence=sequence,
        fixed_timeline_text=fixed_timeline_text,
        canonical_timeline_text=normalize_runtime_timeline_text(fixed_timeline_text),
        playback_window_kind=PLAYBACK_WINDOW_KIND,
        bounded_tick_budget=bounded_tick_budget,
        bounded_event_frame_budget=bounded_event_frame_budget,
        playback_plan_status=status,
        playback_plan_summary=_plan_summary(status),
        dynamic_child_event_scheduling_allowed=dynamic_child_event_scheduling_allowed,
        autonomous_scheduler_allowed=autonomous_scheduler_allowed,
        open_ended_loop_allowed=open_ended_loop_allowed,
        live_engine_invocation_allowed=live_engine_invocation_allowed,
        external_execution_allowed=external_execution_allowed,
        memory_layer_write_allowed=memory_layer_write_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        recursive_learning_allowed=recursive_learning_allowed,
        thought_engine_runtime_allowed=thought_engine_runtime_allowed,
        first_output_allowed=first_output_allowed,
        source_trace_refs=milestone.source_trace_refs if milestone else tuple(),
    )


def validate_runtime_fixed_closed_loop_playback_plan(
    record: RuntimeFixedClosedLoopPlaybackPlanRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _plan(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.playback_plan_status == "playback_plan_created":
        if not item.source_closed_loop_milestone_id:
            errors.append("missing_closed_loop_milestone")
        if not item.source_integrated_event_loop_trace_id:
            errors.append("missing_integrated_trace")
        if not item.fixed_stage_sequence:
            errors.append("missing_fixed_stage_sequence")
    for flag in (
        "dynamic_child_event_scheduling_allowed",
        "autonomous_scheduler_allowed",
        "open_ended_loop_allowed",
        "live_engine_invocation_allowed",
        "external_execution_allowed",
        "memory_layer_write_allowed",
        "automatic_learning_approval_allowed",
        "recursive_learning_allowed",
        "thought_engine_runtime_allowed",
        "first_output_allowed",
    ):
        if getattr(item, flag) and item.playback_plan_status != "blocked_forbidden_authority_detected":
            errors.append(f"{flag}_not_blocked")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "playback_plan_id": item.playback_plan_id,
        "playback_plan_status": item.playback_plan_status,
    }


def build_runtime_closed_loop_stage_to_event_frame_mapping(
    *,
    playback_plan: RuntimeFixedClosedLoopPlaybackPlanRecord | dict[str, object],
    closed_loop_stage_name: str,
    closed_loop_stage_index: int,
    target_event_frame: RuntimeEventFrameRecord | dict[str, object] | None,
    source_closed_loop_record_id: str | None,
    source_closed_loop_record_kind: str | None,
    stage_group_members: tuple[str, ...] | list[str] = (),
    force_missing_source_record: bool = False,
    force_forbidden_authority: bool = False,
) -> RuntimeClosedLoopStageToEventFrameMappingRecord:
    plan = _plan(playback_plan)
    frame = _event_frame(target_event_frame) if target_event_frame is not None else None
    config = STAGE_CONFIG.get(closed_loop_stage_name)
    grouped = bool(stage_group_members)
    if config is None:
        status = "blocked_unknown_closed_loop_stage"
        event_type = "unknown_event"
        event_family = "unknown_event"
        target_engine = "none"
    elif force_forbidden_authority:
        status = "blocked_forbidden_authority_detected"
        event_type = str(config["event_type"])
        event_family = str(config["event_family"])
        target_engine = str(config["target_engine"])
    elif force_missing_source_record or not source_closed_loop_record_id:
        status = "blocked_missing_source_record"
        event_type = str(config["event_type"])
        event_family = str(config["event_family"])
        target_engine = str(config["target_engine"])
    elif frame is None:
        status = "blocked_invalid_event_frame_mapping"
        event_type = str(config["event_type"])
        event_family = str(config["event_family"])
        target_engine = str(config["target_engine"])
    else:
        status = "stage_mapped_as_group_member" if grouped else "stage_mapped_to_event_frame"
        event_type = str(config["event_type"])
        event_family = str(config["event_family"])
        target_engine = str(config["target_engine"])
    return RuntimeClosedLoopStageToEventFrameMappingRecord(
        stage_event_mapping_id=(
            f"runtime_closed_loop_stage_event_mapping:{plan.playback_plan_id}:"
            f"{closed_loop_stage_index}:{_slug(closed_loop_stage_name)}"
        ),
        schema_version=STAGE_MAPPING_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_playback_plan_id=plan.playback_plan_id,
        closed_loop_stage_name=closed_loop_stage_name,
        closed_loop_stage_index=closed_loop_stage_index,
        source_closed_loop_record_id=source_closed_loop_record_id,
        source_closed_loop_record_kind=source_closed_loop_record_kind,
        target_event_frame_id=frame.event_frame_id if frame else "",
        target_event_type=event_type,
        target_event_family=event_family,
        target_engine_lane=target_engine,
        mapping_status=status,
        mapping_summary=_mapping_summary(status, closed_loop_stage_name, target_engine),
        stage_represented=status in {
            "stage_mapped_to_event_frame",
            "stage_mapped_as_group_member",
        },
        stage_grouped=grouped,
        stage_group_members=tuple(stage_group_members),
        dispatch_required=True,
        return_payload_required=True,
        parent_resume_required=frame.event_depth > 1 if frame else True,
        live_engine_invocation_allowed=False,
        dynamic_child_event_scheduling_allowed=False,
        memory_layer_write_allowed=False,
        automatic_learning_approval_allowed=False,
        external_execution_allowed=False,
        source_trace_refs=plan.source_trace_refs,
    )


def validate_runtime_closed_loop_stage_to_event_frame_mapping(
    record: RuntimeClosedLoopStageToEventFrameMappingRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _mapping(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.mapping_status in {"stage_mapped_to_event_frame", "stage_mapped_as_group_member"}:
        if not item.target_event_frame_id:
            errors.append("missing_event_frame")
        if not item.source_closed_loop_record_id:
            errors.append("missing_source_record")
    for flag in (
        "live_engine_invocation_allowed",
        "dynamic_child_event_scheduling_allowed",
        "memory_layer_write_allowed",
        "automatic_learning_approval_allowed",
        "external_execution_allowed",
    ):
        if getattr(item, flag):
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "stage_event_mapping_id": item.stage_event_mapping_id,
        "mapping_status": item.mapping_status,
    }


def build_runtime_fixed_closed_loop_playback_step(
    *,
    playback_plan: RuntimeFixedClosedLoopPlaybackPlanRecord | dict[str, object],
    stage_event_mapping: RuntimeClosedLoopStageToEventFrameMappingRecord | dict[str, object] | None,
    integrated_event_step: RuntimeIntegratedEventStepRecord | dict[str, object] | None = None,
    dispatch_resume_link: RuntimeIntegratedEventDispatchResumeLinkRecord | dict[str, object] | None = None,
    live_handler_invoked: bool = False,
    new_engine_behavior_created: bool = False,
    new_learning_feedback_candidate_created: bool = False,
    new_concept_candidate_created: bool = False,
    new_reviewed_concept_created: bool = False,
    new_memory_write_performed: bool = False,
    new_sandbox_execution_performed: bool = False,
    dynamic_child_event_created: bool = False,
    external_execution_created: bool = False,
    automatic_learning_approval_created: bool = False,
    recursive_learning_created: bool = False,
    thought_engine_behavior_created: bool = False,
    production_behavior_created: bool = False,
) -> RuntimeFixedClosedLoopPlaybackStepRecord:
    plan = _plan(playback_plan)
    mapping = _mapping(stage_event_mapping) if stage_event_mapping is not None else None
    step = _integrated_step(integrated_event_step) if integrated_event_step is not None else None
    link = _dispatch_resume_link(dispatch_resume_link) if dispatch_resume_link is not None else None
    learning_artifact = any(
        (
            new_learning_feedback_candidate_created,
            new_concept_candidate_created,
            new_reviewed_concept_created,
        )
    )
    forbidden = any(
        (
            learning_artifact,
            new_memory_write_performed,
            new_sandbox_execution_performed,
            dynamic_child_event_created,
            external_execution_created,
            automatic_learning_approval_created,
            recursive_learning_created,
            thought_engine_behavior_created,
            production_behavior_created,
        )
    )
    if mapping is None or not mapping.stage_represented:
        status = "blocked_missing_stage_mapping"
    elif link is None:
        status = "blocked_missing_dispatch_resume_link"
    elif live_handler_invoked:
        status = "blocked_live_handler_invocation_detected"
    elif new_engine_behavior_created:
        status = "blocked_new_engine_behavior_detected"
    elif forbidden:
        status = "blocked_forbidden_authority_detected"
    elif link.link_status == "dispatch_resume_link_deferred_thought_engine":
        status = "playback_step_deferred_thought_not_available"
    elif mapping.stage_grouped:
        status = "playback_step_recorded_with_grouped_stage"
    else:
        status = "playback_step_recorded"
    return RuntimeFixedClosedLoopPlaybackStepRecord(
        playback_step_id=(
            f"runtime_fixed_closed_loop_playback_step:{plan.playback_plan_id}:"
            f"{mapping.closed_loop_stage_index if mapping else 0}:"
            f"{_slug(mapping.closed_loop_stage_name if mapping else 'missing_mapping')}"
        ),
        schema_version=PLAYBACK_STEP_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_playback_plan_id=plan.playback_plan_id,
        source_stage_event_mapping_id=mapping.stage_event_mapping_id if mapping else None,
        source_integrated_event_step_id=step.integrated_event_step_id if step else None,
        source_dispatch_resume_link_id=link.dispatch_resume_link_id if link else None,
        step_index=mapping.closed_loop_stage_index if mapping else 0,
        closed_loop_stage_name=mapping.closed_loop_stage_name if mapping else "missing_mapping",
        event_frame_id=mapping.target_event_frame_id if mapping else "",
        event_type=mapping.target_event_type if mapping else "unknown_event",
        event_family=mapping.target_event_family if mapping else "unknown_event",
        target_engine_lane=mapping.target_engine_lane if mapping else "none",
        dispatch_status=link.link_status if link else "missing_dispatch_resume_link",
        return_status=link.return_status if link else "missing_return_payload",
        parent_resume_status=link.parent_resume_status if link else None,
        playback_step_status=status,
        playback_step_summary=_step_summary(status, mapping.closed_loop_stage_name if mapping else "missing_mapping"),
        stage_evidence_referenced=bool(mapping and mapping.source_closed_loop_record_id),
        stage_replayed_as_record=True,
        live_handler_invoked=live_handler_invoked,
        new_engine_behavior_created=new_engine_behavior_created,
        new_learning_feedback_candidate_created=new_learning_feedback_candidate_created,
        new_concept_candidate_created=new_concept_candidate_created,
        new_reviewed_concept_created=new_reviewed_concept_created,
        new_memory_write_performed=new_memory_write_performed,
        new_sandbox_execution_performed=new_sandbox_execution_performed,
        dynamic_child_event_created=dynamic_child_event_created,
        external_execution_created=external_execution_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        recursive_learning_created=recursive_learning_created or learning_artifact,
        thought_engine_behavior_created=thought_engine_behavior_created,
        production_behavior_created=production_behavior_created,
        source_trace_refs=plan.source_trace_refs,
    )


def validate_runtime_fixed_closed_loop_playback_step(
    record: RuntimeFixedClosedLoopPlaybackStepRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _step(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.playback_step_status in {
        "playback_step_recorded",
        "playback_step_recorded_with_grouped_stage",
    }:
        if not item.source_stage_event_mapping_id:
            errors.append("missing_stage_mapping")
        if not item.source_dispatch_resume_link_id:
            errors.append("missing_dispatch_resume_link")
        if item.live_handler_invoked:
            errors.append("live_handler_invoked")
    for flag in (
        "new_learning_feedback_candidate_created",
        "new_concept_candidate_created",
        "new_reviewed_concept_created",
        "new_memory_write_performed",
        "new_sandbox_execution_performed",
        "dynamic_child_event_created",
        "external_execution_created",
        "automatic_learning_approval_created",
        "recursive_learning_created",
        "thought_engine_behavior_created",
        "production_behavior_created",
    ):
        if getattr(item, flag) and item.playback_step_status != "blocked_forbidden_authority_detected":
            errors.append(f"{flag}_not_blocked")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "playback_step_id": item.playback_step_id,
        "playback_step_status": item.playback_step_status,
    }


def build_runtime_fixed_closed_loop_playback_trace(
    *,
    playback_plan: RuntimeFixedClosedLoopPlaybackPlanRecord | dict[str, object],
    stage_mappings: tuple[RuntimeClosedLoopStageToEventFrameMappingRecord, ...] | list[RuntimeClosedLoopStageToEventFrameMappingRecord | dict[str, object]],
    playback_steps: tuple[RuntimeFixedClosedLoopPlaybackStepRecord, ...] | list[RuntimeFixedClosedLoopPlaybackStepRecord | dict[str, object]],
    integrated_event_loop_trace: RuntimeIntegratedEventLoopTrace | dict[str, object] | None,
    closed_loop_milestone: FirstClosedLoopMilestoneRecord | dict[str, object] | None,
    force_missing_event_frame: bool = False,
    force_missing_dispatch: bool = False,
    force_missing_return_payload: bool = False,
    force_missing_parent_resume: bool = False,
    force_unclosed_root_frame: bool = False,
    force_live_engine_invocation: bool = False,
    force_dynamic_child_event: bool = False,
    force_autonomous_scheduler: bool = False,
    force_open_ended_loop: bool = False,
    force_external_execution: bool = False,
    force_memory_write: bool = False,
    force_automatic_learning_approval: bool = False,
    force_recursive_learning: bool = False,
    force_thought_engine_behavior: bool = False,
    force_production_behavior: bool = False,
) -> RuntimeFixedClosedLoopPlaybackTrace:
    plan = _plan(playback_plan)
    mappings = tuple(_mapping(item) for item in stage_mappings)
    steps = tuple(_step(item) for item in playback_steps)
    integrated_trace = (
        _integrated_trace(integrated_event_loop_trace)
        if integrated_event_loop_trace is not None
        else None
    )
    milestone = _milestone(closed_loop_milestone) if closed_loop_milestone is not None else None
    represented = tuple(
        mapping.closed_loop_stage_name
        for mapping in mappings
        if mapping.closed_loop_stage_name in REQUIRED_CLOSED_LOOP_STAGES
    )
    missing = tuple(stage for stage in REQUIRED_CLOSED_LOOP_STAGES if stage not in represented)
    missing_event_frame = force_missing_event_frame or any(
        not mapping.target_event_frame_id or mapping.mapping_status.startswith("blocked_")
        for mapping in mappings
    )
    missing_dispatch = force_missing_dispatch or any(
        step.playback_step_status == "blocked_missing_dispatch_resume_link"
        or not step.source_dispatch_resume_link_id
        for step in steps
    )
    missing_return = force_missing_return_payload or any(
        step.return_status == "missing_return_payload" for step in steps
    )
    missing_parent = force_missing_parent_resume or any(
        step.parent_resume_status is None for step in steps
    )
    unclosed_root = force_unclosed_root_frame or not (
        integrated_trace is not None
        and integrated_trace.all_event_frames_closed_or_validly_deferred
    )
    live = force_live_engine_invocation or any(step.live_handler_invoked for step in steps)
    dynamic = force_dynamic_child_event or any(step.dynamic_child_event_created for step in steps)
    external = force_external_execution or any(step.external_execution_created for step in steps)
    memory = force_memory_write or any(
        step.new_memory_write_performed for step in steps
    )
    automatic = force_automatic_learning_approval or any(
        step.automatic_learning_approval_created for step in steps
    )
    recursive = force_recursive_learning or any(
        step.recursive_learning_created
        or step.new_learning_feedback_candidate_created
        or step.new_concept_candidate_created
        or step.new_reviewed_concept_created
        for step in steps
    )
    thought = force_thought_engine_behavior or any(
        step.thought_engine_behavior_created for step in steps
    )
    production = force_production_behavior or any(step.production_behavior_created for step in steps)
    forbidden = any(
        (
            live,
            dynamic,
            force_autonomous_scheduler,
            force_open_ended_loop,
            external,
            memory,
            automatic,
            recursive,
            thought,
            production,
        )
    )
    if forbidden:
        status = "fixed_closed_loop_playback_blocked_forbidden_authority_detected"
    elif missing:
        status = "fixed_closed_loop_playback_blocked_missing_required_stage"
    elif missing_event_frame:
        status = "fixed_closed_loop_playback_blocked_missing_event_frame"
    elif missing_dispatch:
        status = "fixed_closed_loop_playback_blocked_missing_dispatch_lineage"
    elif missing_return:
        status = "fixed_closed_loop_playback_blocked_missing_return_payload"
    elif missing_parent:
        status = "fixed_closed_loop_playback_blocked_missing_parent_resume"
    elif unclosed_root:
        status = "fixed_closed_loop_playback_blocked_unclosed_root_frame"
    elif any(mapping.stage_grouped for mapping in mappings):
        status = "fixed_closed_loop_playback_complete_with_grouped_stages"
    else:
        status = "fixed_closed_loop_playback_complete"
    return RuntimeFixedClosedLoopPlaybackTrace(
        fixed_playback_trace_id=f"runtime_fixed_closed_loop_playback_trace:{plan.playback_plan_id}",
        schema_version=PLAYBACK_TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_playback_plan_id=plan.playback_plan_id,
        source_integrated_event_loop_trace_id=(
            integrated_trace.integrated_loop_trace_id if integrated_trace else None
        ),
        source_closed_loop_milestone_id=milestone.milestone_id if milestone else None,
        stage_event_mapping_ids=tuple(mapping.stage_event_mapping_id for mapping in mappings),
        playback_step_ids=tuple(step.playback_step_id for step in steps),
        fixed_stage_sequence=plan.fixed_stage_sequence,
        represented_stage_sequence=represented,
        missing_required_stages=missing,
        timeline_text=plan.fixed_timeline_text,
        canonical_timeline_text=plan.canonical_timeline_text,
        playback_stage_count=len(plan.fixed_stage_sequence),
        represented_stage_count=len(represented),
        all_required_stages_represented=not missing,
        all_steps_have_event_frames=not missing_event_frame,
        all_steps_have_dispatch_lineage=not missing_dispatch,
        all_steps_have_return_payloads=not missing_return,
        all_child_returns_resumed=not missing_parent,
        root_frame_closed=not unclosed_root,
        fixed_playback_status=status,
        fixed_playback_summary=_trace_summary(status),
        live_engine_invocation_created=live,
        dynamic_child_event_created=dynamic,
        autonomous_scheduler_created=force_autonomous_scheduler,
        open_ended_loop_created=force_open_ended_loop,
        external_execution_created=external,
        memory_layer_write_performed=memory,
        automatic_learning_approval_created=automatic,
        recursive_learning_created=recursive,
        thought_engine_behavior_created=thought,
        production_behavior_created=production,
        source_trace_refs=plan.source_trace_refs,
    )


def validate_runtime_fixed_closed_loop_playback_trace(
    record: RuntimeFixedClosedLoopPlaybackTrace | dict[str, object],
) -> dict[str, object]:
    try:
        item = _trace(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.fixed_playback_status.startswith("fixed_closed_loop_playback_complete"):
        if not item.all_required_stages_represented:
            errors.append("missing_required_stage")
        if not item.all_steps_have_event_frames:
            errors.append("missing_event_frame")
        if not item.all_steps_have_dispatch_lineage:
            errors.append("missing_dispatch_lineage")
        if not item.all_steps_have_return_payloads:
            errors.append("missing_return_payload")
        if not item.all_child_returns_resumed:
            errors.append("missing_parent_resume")
        if not item.root_frame_closed:
            errors.append("root_frame_unclosed")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "fixed_playback_trace_id": item.fixed_playback_trace_id,
        "fixed_playback_status": item.fixed_playback_status,
    }


def build_runtime_fixed_closed_loop_playback_render(
    fixed_playback_trace: RuntimeFixedClosedLoopPlaybackTrace | dict[str, object],
    playback_steps: tuple[RuntimeFixedClosedLoopPlaybackStepRecord, ...] | list[RuntimeFixedClosedLoopPlaybackStepRecord | dict[str, object]] = (),
) -> RuntimeFixedClosedLoopPlaybackRenderRecord:
    trace = _trace(fixed_playback_trace)
    steps = tuple(_step(item) for item in playback_steps)
    if trace.fixed_playback_status.startswith("fixed_closed_loop_playback_blocked"):
        status = "fixed_playback_render_blocked_invalid_trace"
    elif trace.fixed_playback_status == "fixed_closed_loop_playback_complete_with_grouped_stages":
        status = "fixed_playback_render_created_with_grouped_stages"
    else:
        status = "fixed_playback_render_created"
    summary_lines = tuple(
        f"{step.step_index:02d} {step.closed_loop_stage_name} -> EventFrame "
        f"{step.event_family} -> dispatch {step.target_engine_lane} -> {step.return_status}"
        for step in sorted(steps, key=lambda item: item.step_index)
    )
    human = render_fixed_closed_loop_playback_timeline_text(trace, steps)
    return RuntimeFixedClosedLoopPlaybackRenderRecord(
        fixed_playback_render_id=f"runtime_fixed_closed_loop_playback_render:{trace.fixed_playback_trace_id}",
        schema_version=PLAYBACK_RENDER_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_fixed_playback_trace_id=trace.fixed_playback_trace_id,
        timeline_text=trace.timeline_text,
        canonical_timeline_text=trace.canonical_timeline_text,
        human_readable_playback_text=human,
        stage_summary_lines=summary_lines,
        legend={
            "space": "power_off_gap",
            ".": "idle_heartbeat",
            "1": "root_closed_loop_playback_event",
            "2": "action_sense_outcome_stage_events",
            "3": "learning_memory_stage_events",
            "4": "replay_audit_stage_events",
            "D": "dispatch",
            "R": "return",
            "P": "parent_resume",
            "S": "stack_update",
        },
        render_status=status,
        render_summary=_render_summary(status),
        source_trace_refs=trace.source_trace_refs,
    )


def validate_runtime_fixed_closed_loop_playback_render(
    record: RuntimeFixedClosedLoopPlaybackRenderRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _render(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    for key in ("space", ".", "1", "2", "3", "4", "D", "R", "P", "S"):
        if key not in item.legend:
            errors.append(f"missing_legend:{key}")
    if item.render_status != "fixed_playback_render_blocked_invalid_trace" and not item.stage_summary_lines:
        errors.append("missing_stage_summary_lines")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "fixed_playback_render_id": item.fixed_playback_render_id,
        "render_status": item.render_status,
    }


def build_runtime_fixed_closed_loop_playback_audit(
    *,
    playback_plan: RuntimeFixedClosedLoopPlaybackPlanRecord | dict[str, object] | None = None,
    fixed_playback_trace: RuntimeFixedClosedLoopPlaybackTrace | dict[str, object] | None = None,
    fixed_playback_render: RuntimeFixedClosedLoopPlaybackRenderRecord | dict[str, object] | None = None,
    closed_loop_milestone: FirstClosedLoopMilestoneRecord | dict[str, object] | None = None,
    integrated_event_loop_trace: RuntimeIntegratedEventLoopTrace | dict[str, object] | None = None,
    force_missing_closed_loop_milestone: bool = False,
    force_missing_integrated_event_loop_trace: bool = False,
    force_first_output: bool = False,
) -> RuntimeFixedClosedLoopPlaybackAudit:
    plan = _plan(playback_plan) if playback_plan is not None else None
    trace = _trace(fixed_playback_trace) if fixed_playback_trace is not None else None
    render = _render(fixed_playback_render) if fixed_playback_render is not None else None
    milestone = _milestone(closed_loop_milestone) if closed_loop_milestone is not None else None
    integrated_trace = (
        _integrated_trace(integrated_event_loop_trace)
        if integrated_event_loop_trace is not None
        else None
    )
    reasons = _audit_blocked_reasons(
        plan=plan,
        trace=trace,
        milestone=milestone,
        integrated_trace=integrated_trace,
        force_missing_closed_loop_milestone=force_missing_closed_loop_milestone,
        force_missing_integrated_event_loop_trace=force_missing_integrated_event_loop_trace,
        force_first_output=force_first_output,
    )
    status = _audit_status(trace, reasons)
    return RuntimeFixedClosedLoopPlaybackAudit(
        fixed_playback_audit_id=f"runtime_fixed_closed_loop_playback_audit:{_slug(status)}",
        schema_version=PLAYBACK_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_playback_plan_id=plan.playback_plan_id if plan else None,
        source_fixed_playback_trace_id=trace.fixed_playback_trace_id if trace else None,
        source_fixed_playback_render_id=render.fixed_playback_render_id if render else None,
        closed_loop_milestone_valid="missing_closed_loop_milestone" not in reasons,
        integrated_event_loop_trace_valid="missing_integrated_event_loop_trace" not in reasons,
        playback_plan_valid=plan is not None and plan.playback_plan_status == "playback_plan_created",
        stage_mapping_valid="missing_event_frame_mapping" not in reasons,
        playback_steps_valid="missing_dispatch_lineage" not in reasons,
        playback_trace_valid=trace is not None and not trace.fixed_playback_status.endswith("forbidden_authority_detected"),
        playback_render_valid=render is not None and render.render_status != "fixed_playback_render_blocked_invalid_trace",
        all_required_closed_loop_stages_represented=trace is not None
        and trace.all_required_stages_represented,
        all_stages_mapped_to_event_frames=trace is not None
        and trace.all_steps_have_event_frames,
        all_event_frames_dispatched=trace is not None
        and trace.all_steps_have_dispatch_lineage,
        all_dispatches_returned=trace is not None
        and trace.all_steps_have_return_payloads,
        all_child_returns_resumed=trace is not None and trace.all_child_returns_resumed,
        root_event_closed=trace is not None and trace.root_frame_closed,
        fixed_playback_only_confirmed=True,
        record_only_confirmed=True,
        adapter_only_confirmed=True,
        no_live_engine_invocation="live_engine_invocation_detected" not in reasons,
        no_dynamic_child_event_scheduling="dynamic_child_event_scheduling_detected" not in reasons,
        no_autonomous_scheduler="autonomous_scheduler_detected" not in reasons,
        no_open_ended_loop="open_ended_loop_detected" not in reasons,
        no_background_daemon=True,
        no_external_execution="external_execution_detected" not in reasons,
        no_unity_execution=True,
        no_bridge_execution=True,
        no_network_execution=True,
        no_filesystem_execution=True,
        no_memory_layer_write="memory_write_detected" not in reasons,
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_automatic_learning_approval=(
            "automatic_learning_approval_detected" not in reasons
        ),
        no_free_action_selection=True,
        no_recursive_learning="recursive_learning_detected" not in reasons,
        no_thought_engine_behavior="thought_engine_fake_detected" not in reasons,
        no_first_output="first_output_detected" not in reasons,
        no_production_behavior="production_behavior_detected" not in reasons,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(reasons),
        source_trace_refs=trace.source_trace_refs if trace else tuple(),
    )


def validate_runtime_fixed_closed_loop_playback_audit(
    record: RuntimeFixedClosedLoopPlaybackAudit | dict[str, object],
) -> dict[str, object]:
    try:
        item = _audit(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.audit_status.startswith("passed_"):
        required = (
            item.closed_loop_milestone_valid,
            item.integrated_event_loop_trace_valid,
            item.playback_plan_valid,
            item.stage_mapping_valid,
            item.playback_steps_valid,
            item.all_required_closed_loop_stages_represented,
            item.all_stages_mapped_to_event_frames,
            item.all_event_frames_dispatched,
            item.all_dispatches_returned,
            item.all_child_returns_resumed,
            item.root_event_closed,
            item.no_live_engine_invocation,
            item.no_dynamic_child_event_scheduling,
            item.no_external_execution,
            item.no_memory_layer_write,
            item.no_automatic_learning_approval,
            item.no_recursive_learning,
            item.no_thought_engine_behavior,
            item.no_first_output,
            item.no_production_behavior,
        )
        if not all(required):
            errors.append("passed_audit_has_failed_boundary")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "fixed_playback_audit_id": item.fixed_playback_audit_id,
        "audit_status": item.audit_status,
    }


def build_runtime_fixed_closed_loop_playback_readiness(
    fixed_playback_audit: RuntimeFixedClosedLoopPlaybackAudit | dict[str, object],
) -> RuntimeFixedClosedLoopPlaybackReadinessRecord:
    audit = _audit(fixed_playback_audit)
    passed = audit.audit_status.startswith("passed_")
    if passed:
        status = "ready_for_bounded_handler_binding_only"
    elif "detected" in audit.audit_status:
        status = "blocked_forbidden_authority_detected"
    elif audit.source_fixed_playback_trace_id is None:
        status = "not_ready_missing_fixed_playback"
    else:
        status = "not_ready_boundary_failure"
    return RuntimeFixedClosedLoopPlaybackReadinessRecord(
        fixed_playback_readiness_id=f"runtime_fixed_closed_loop_playback_readiness:{audit.fixed_playback_audit_id}",
        schema_version=PLAYBACK_READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_fixed_playback_audit_id=audit.fixed_playback_audit_id,
        current_verified_capability=SAFE_CLAIM,
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason=(
            "Bind selected fixed playback EventFrame stages to existing "
            "deterministic side-effect-free handler builders, one fixed stage at a time."
        ),
        ready_for_bounded_handler_binding=passed,
        ready_for_runtime_state_persistence_binding=passed,
        ready_for_teacher_observed_playback_cli=passed,
        ready_for_dynamic_child_event_scheduling=False,
        ready_for_autonomous_scheduler=False,
        ready_for_open_ended_loop=False,
        ready_for_live_engine_invocation=False,
        ready_for_external_execution=False,
        ready_for_memory_layer_write=False,
        ready_for_automatic_learning_approval=False,
        ready_for_recursive_learning=False,
        ready_for_thought_engine_runtime=False,
        ready_for_first_output=False,
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=audit.source_trace_refs,
    )


def validate_runtime_fixed_closed_loop_playback_readiness(
    record: RuntimeFixedClosedLoopPlaybackReadinessRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _readiness(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    for flag in (
        "ready_for_dynamic_child_event_scheduling",
        "ready_for_autonomous_scheduler",
        "ready_for_open_ended_loop",
        "ready_for_live_engine_invocation",
        "ready_for_external_execution",
        "ready_for_memory_layer_write",
        "ready_for_automatic_learning_approval",
        "ready_for_recursive_learning",
        "ready_for_thought_engine_runtime",
        "ready_for_first_output",
    ):
        if getattr(item, flag):
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "fixed_playback_readiness_id": item.fixed_playback_readiness_id,
        "readiness_status": item.readiness_status,
    }


def build_demo_full_fixed_closed_loop_playback() -> dict[str, object]:
    return _build_fixed_playback_bundle()


def build_demo_grouped_stage_fixed_closed_loop_playback() -> dict[str, object]:
    return _build_fixed_playback_bundle(grouped=True)


def build_demo_blocked_missing_stage_fixed_playback() -> dict[str, object]:
    sequence = tuple(
        stage for stage in REQUIRED_CLOSED_LOOP_STAGES if stage != "working_readback_integration"
    )
    return _build_fixed_playback_bundle(stage_sequence=sequence)


def build_demo_blocked_missing_event_frame_mapping_fixed_playback() -> dict[str, object]:
    return _build_fixed_playback_bundle(force_missing_event_mapping=True)


def build_demo_blocked_missing_dispatch_lineage_fixed_playback() -> dict[str, object]:
    return _build_fixed_playback_bundle(force_missing_dispatch_lineage=True)


def build_demo_blocked_live_handler_invocation_fixed_playback() -> dict[str, object]:
    return _build_fixed_playback_bundle(force_live_handler_invocation=True)


def build_demo_blocked_new_learning_artifact_fixed_playback() -> dict[str, object]:
    return _build_fixed_playback_bundle(force_new_learning_artifact=True)


def build_demo_blocked_forbidden_authority_fixed_playback() -> dict[str, object]:
    return _build_fixed_playback_bundle(force_memory_write=True)


def render_fixed_closed_loop_playback_summary_text(
    trace: RuntimeFixedClosedLoopPlaybackTrace | dict[str, object],
    audit: RuntimeFixedClosedLoopPlaybackAudit | dict[str, object] | None = None,
    readiness: RuntimeFixedClosedLoopPlaybackReadinessRecord | dict[str, object] | None = None,
) -> str:
    trace_record = _trace(trace)
    audit_record = _audit(audit) if audit is not None else None
    readiness_record = _readiness(readiness) if readiness is not None else None
    parts = [
        f"fixed_playback status={trace_record.fixed_playback_status}",
        f"stages={trace_record.playback_stage_count}",
        f"represented={trace_record.represented_stage_count}",
        f"missing={len(trace_record.missing_required_stages)}",
    ]
    if audit_record is not None:
        parts.append(f"audit={audit_record.audit_status}")
    if readiness_record is not None:
        parts.append(f"readiness={readiness_record.readiness_status}")
    return " ".join(parts)


def render_fixed_closed_loop_playback_timeline_text(
    trace: RuntimeFixedClosedLoopPlaybackTrace | dict[str, object],
    playback_steps: tuple[RuntimeFixedClosedLoopPlaybackStepRecord, ...] | list[RuntimeFixedClosedLoopPlaybackStepRecord | dict[str, object]] = (),
) -> str:
    trace_record = _trace(trace)
    steps = tuple(_step(item) for item in playback_steps)
    lines = [f"timeline {trace_record.canonical_timeline_text}"]
    for step in sorted(steps, key=lambda item: item.step_index):
        lines.append(
            f"{step.step_index:02d} {step.closed_loop_stage_name} -> "
            f"{step.event_family} -> {step.target_engine_lane} -> "
            f"{step.return_status}"
        )
    return "\n".join(lines)


def _build_fixed_playback_bundle(
    *,
    grouped: bool = False,
    stage_sequence: tuple[str, ...] = REQUIRED_CLOSED_LOOP_STAGES,
    force_missing_event_mapping: bool = False,
    force_missing_dispatch_lineage: bool = False,
    force_live_handler_invocation: bool = False,
    force_new_learning_artifact: bool = False,
    force_memory_write: bool = False,
) -> dict[str, object]:
    milestone_payload = build_demo_first_closed_loop_milestone()
    milestone = FirstClosedLoopMilestoneRecord.from_dict(
        milestone_payload["first_closed_loop_milestone"]
    )
    evidence = FirstClosedLoopEvidenceChainRecord.from_dict(
        milestone_payload["first_closed_loop_evidence_chain"]
    )
    integrated_payload = _build_stage_specific_integrated_trace(stage_sequence)
    integrated_trace = RuntimeIntegratedEventLoopTrace.from_dict(
        integrated_payload["runtime_integrated_event_loop_trace"]
    )
    plan = build_runtime_fixed_closed_loop_playback_plan(
        closed_loop_milestone=milestone,
        integrated_event_loop_trace=integrated_trace,
        fixed_stage_sequence=stage_sequence,
    )
    child_frames = tuple(
        RuntimeEventFrameRecord.from_dict(item)
        for item in integrated_payload["runtime_event_frames"]
        if item["event_depth"] == 2
    )
    frame_by_stage = dict(zip(stage_sequence, child_frames))
    steps_by_frame = {
        item["source_event_frame_id"]: RuntimeIntegratedEventStepRecord.from_dict(item)
        for item in integrated_payload["runtime_integrated_event_steps"]
        if item["source_event_frame_id"]
    }
    links_by_frame = {
        item["source_event_frame_id"]: RuntimeIntegratedEventDispatchResumeLinkRecord.from_dict(item)
        for item in integrated_payload["runtime_integrated_dispatch_resume_links"]
    }
    mappings: list[RuntimeClosedLoopStageToEventFrameMappingRecord] = []
    playback_steps: list[RuntimeFixedClosedLoopPlaybackStepRecord] = []
    for index, stage in enumerate(stage_sequence, start=1):
        frame = None if (force_missing_event_mapping and index == 1) else frame_by_stage.get(stage)
        source_id = _source_record_id_for_stage(stage, evidence, milestone)
        group_members = GROUPED_STAGE_MEMBERS.get(stage, tuple()) if grouped else tuple()
        mapping = build_runtime_closed_loop_stage_to_event_frame_mapping(
            playback_plan=plan,
            closed_loop_stage_name=stage,
            closed_loop_stage_index=index,
            target_event_frame=frame,
            source_closed_loop_record_id=source_id,
            source_closed_loop_record_kind=str(STAGE_CONFIG[stage]["source_kind"]),
            stage_group_members=group_members,
        )
        mappings.append(mapping)
        link = None
        integrated_step = None
        if frame is not None and not (force_missing_dispatch_lineage and index == 1):
            link = links_by_frame.get(frame.event_frame_id)
            integrated_step = steps_by_frame.get(frame.event_frame_id)
        playback_steps.append(
            build_runtime_fixed_closed_loop_playback_step(
                playback_plan=plan,
                stage_event_mapping=mapping,
                integrated_event_step=integrated_step,
                dispatch_resume_link=link,
                live_handler_invoked=force_live_handler_invocation and index == 1,
                new_reviewed_concept_created=(
                    force_new_learning_artifact
                    and stage == "feedback_derived_reviewed_concept"
                ),
                new_memory_write_performed=force_memory_write and index == 1,
            )
        )
    trace = build_runtime_fixed_closed_loop_playback_trace(
        playback_plan=plan,
        stage_mappings=tuple(mappings),
        playback_steps=tuple(playback_steps),
        integrated_event_loop_trace=integrated_trace,
        closed_loop_milestone=milestone,
    )
    render = build_runtime_fixed_closed_loop_playback_render(
        trace,
        playback_steps=tuple(playback_steps),
    )
    audit = build_runtime_fixed_closed_loop_playback_audit(
        playback_plan=plan,
        fixed_playback_trace=trace,
        fixed_playback_render=render,
        closed_loop_milestone=milestone,
        integrated_event_loop_trace=integrated_trace,
    )
    readiness = build_runtime_fixed_closed_loop_playback_readiness(audit)
    return {
        "source_package94_milestone": milestone_payload,
        **integrated_payload,
        "runtime_fixed_closed_loop_playback_plan": plan.to_dict(),
        "runtime_closed_loop_stage_event_mappings": [
            mapping.to_dict() for mapping in mappings
        ],
        "runtime_fixed_closed_loop_playback_steps": [
            step.to_dict() for step in playback_steps
        ],
        "runtime_fixed_closed_loop_playback_trace": trace.to_dict(),
        "runtime_fixed_closed_loop_playback_render": render.to_dict(),
        "runtime_fixed_closed_loop_playback_audit": audit.to_dict(),
        "runtime_fixed_closed_loop_playback_readiness": readiness.to_dict(),
        "rendered_fixed_closed_loop_playback_summary": (
            render_fixed_closed_loop_playback_summary_text(trace, audit, readiness)
        ),
        "rendered_fixed_closed_loop_playback_timeline": (
            render.human_readable_playback_text
        ),
    }


def _build_stage_specific_integrated_trace(
    stage_sequence: tuple[str, ...],
) -> dict[str, object]:
    timeline = "...." + ("12" * len(stage_sequence)) + "1"
    power_window = build_runtime_power_window_record(
        timeline_text=timeline,
        source_trace_refs=("runtime_fixed_closed_loop_playback_demo",),
    )
    ticks = build_runtime_tick_records_from_timeline(power_window=power_window)
    raw_frames = build_runtime_event_frames_from_timeline(power_window=power_window)
    child_stage_by_order = tuple(stage_sequence)
    child_index = 0
    frames: list[RuntimeEventFrameRecord] = []
    for frame in raw_frames:
        if frame.event_depth == 1:
            frames.append(
                replace(
                    frame,
                    event_type="task_trial",
                    event_label="event_1_fixed_closed_loop_playback_root",
                )
            )
            continue
        stage = child_stage_by_order[child_index]
        child_index += 1
        frames.append(
            replace(
                frame,
                event_type=str(STAGE_CONFIG[stage]["dispatch_event_type"]),
                event_label=f"event_2_{stage}",
            )
        )
    event_returns = build_runtime_event_return_records(power_window=power_window)
    stacks = build_runtime_event_stack_records(power_window=power_window)
    tree = build_runtime_event_tree_record(
        power_window=power_window,
        event_frames=tuple(frames),
        event_returns=event_returns,
    )
    loop_trace = build_runtime_continuous_loop_trace(
        power_window=power_window,
        ticks=ticks,
        event_frames=tuple(frames),
        event_stacks=stacks,
        event_returns=event_returns,
        event_tree=tree,
    )
    loop_audit = build_runtime_continuous_loop_audit(
        loop_trace=loop_trace,
        event_tree=tree,
        ticks=ticks,
        event_frames=tuple(frames),
        event_stacks=stacks,
        event_returns=event_returns,
    )
    frame_by_id = {frame.event_frame_id: frame for frame in frames}
    root = next(frame for frame in frames if frame.event_depth == 1)
    dispatch_requests: list[RuntimeEventDispatchRequestRecord] = []
    dispatch_routes: list[RuntimeEventDispatchRouteRecord] = []
    handler_adapters: list[RuntimeEventHandlerAdapterRecord] = []
    dispatch_results: list[RuntimeEventDispatchResultRecord] = []
    return_payloads: list[RuntimeEventDispatchReturnPayloadRecord] = []
    dispatch_audits: list[RuntimeEventDispatchAudit] = []
    return_payload_by_frame: dict[str, RuntimeEventDispatchReturnPayloadRecord] = {}
    for frame in frames:
        payload = dispatch_event_frame_adapter_only(frame)
        request = RuntimeEventDispatchRequestRecord.from_dict(
            payload["runtime_event_dispatch_request"]
        )
        route = RuntimeEventDispatchRouteRecord.from_dict(
            payload["runtime_event_dispatch_route"]
        )
        adapter = RuntimeEventHandlerAdapterRecord.from_dict(
            payload["runtime_event_handler_adapter"]
        )
        result = RuntimeEventDispatchResultRecord.from_dict(
            payload["runtime_event_dispatch_result"]
        )
        return_payload = RuntimeEventDispatchReturnPayloadRecord.from_dict(
            payload["runtime_event_dispatch_return_payload"]
        )
        audit = RuntimeEventDispatchAudit.from_dict(payload["runtime_event_dispatch_audit"])
        dispatch_requests.append(request)
        dispatch_routes.append(route)
        handler_adapters.append(adapter)
        dispatch_results.append(result)
        return_payloads.append(return_payload)
        dispatch_audits.append(audit)
        return_payload_by_frame[frame.event_frame_id] = return_payload
    resume_requests: list[RuntimeParentFrameResumeRequestRecord] = []
    resume_decisions: list[RuntimeParentFrameResumeDecisionRecord] = []
    parent_resumes: list[RuntimeParentFrameResumeRecord] = []
    stack_updates: list[RuntimeParentFrameResumeStackUpdateRecord] = []
    parent_resume_audits: list[RuntimeParentFrameResumeAudit] = []
    parent_resume_by_frame: dict[str, RuntimeParentFrameResumeRecord] = {}
    stack_update_by_frame: dict[str, RuntimeParentFrameResumeStackUpdateRecord] = {}
    for frame in sorted(frames, key=lambda item: (item.event_depth, item.opened_at_tick_index), reverse=True):
        parent = frame_by_id.get(frame.parent_event_frame_id) if frame.parent_event_frame_id else None
        stack_before = (root.event_frame_id, frame.event_frame_id) if parent else (frame.event_frame_id,)
        payload = resume_parent_frame_from_child_return(
            frame,
            parent_event_frame=parent,
            dispatch_return_payload=return_payload_by_frame[frame.event_frame_id],
            stack_before_resume=stack_before,
        )
        request = RuntimeParentFrameResumeRequestRecord.from_dict(
            payload["runtime_parent_frame_resume_request"]
        )
        decision = RuntimeParentFrameResumeDecisionRecord.from_dict(
            payload["runtime_parent_frame_resume_decision"]
        )
        resume = RuntimeParentFrameResumeRecord.from_dict(
            payload["runtime_parent_frame_resume"]
        )
        stack_update = RuntimeParentFrameResumeStackUpdateRecord.from_dict(
            payload["runtime_parent_frame_resume_stack_update"]
        )
        audit = RuntimeParentFrameResumeAudit.from_dict(
            payload["runtime_parent_frame_resume_audit"]
        )
        resume_requests.append(request)
        resume_decisions.append(decision)
        parent_resumes.append(resume)
        stack_updates.append(stack_update)
        parent_resume_audits.append(audit)
        parent_resume_by_frame[frame.event_frame_id] = resume
        stack_update_by_frame[frame.event_frame_id] = stack_update
    requests_by_frame = {item.source_event_frame_id: item for item in dispatch_requests}
    routes_by_frame = {item.source_event_frame_id: item for item in dispatch_routes}
    adapters_by_frame = {item.source_event_frame_id: item for item in handler_adapters}
    results_by_frame = {item.source_event_frame_id: item for item in dispatch_results}
    returns_by_frame = {item.source_event_frame_id: item for item in return_payloads}
    stacks_by_tick = {item.tick_index: item for item in stacks}
    links: list[RuntimeIntegratedEventDispatchResumeLinkRecord] = []
    steps: list[RuntimeIntegratedEventStepRecord] = []
    for frame in frames:
        link = build_runtime_integrated_dispatch_resume_link_record(
            event_frame=frame,
            dispatch_request=requests_by_frame[frame.event_frame_id],
            dispatch_route=routes_by_frame[frame.event_frame_id],
            dispatch_result=results_by_frame[frame.event_frame_id],
            dispatch_return_payload=returns_by_frame[frame.event_frame_id],
            parent_resume=parent_resume_by_frame[frame.event_frame_id],
            resume_stack_update=stack_update_by_frame[frame.event_frame_id],
        )
        links.append(link)
        tick = next(
            item for item in ticks if item.active_event_frame_id == frame.event_frame_id
        )
        steps.append(
            build_runtime_integrated_event_step_record(
                power_window=power_window,
                tick=tick,
                event_frame=frame,
                event_stack=stacks_by_tick.get(tick.tick_index),
                dispatch_request=requests_by_frame[frame.event_frame_id],
                dispatch_route=routes_by_frame[frame.event_frame_id],
                handler_adapter=adapters_by_frame[frame.event_frame_id],
                dispatch_result=results_by_frame[frame.event_frame_id],
                dispatch_return_payload=returns_by_frame[frame.event_frame_id],
                parent_resume=parent_resume_by_frame[frame.event_frame_id],
                resume_stack_update=stack_update_by_frame[frame.event_frame_id],
            )
        )
    integrated_trace = build_runtime_integrated_event_loop_trace(
        power_window=power_window,
        ticks=ticks,
        event_frames=tuple(frames),
        event_stacks=stacks,
        event_tree=tree,
        continuous_loop_trace=loop_trace,
        continuous_loop_audit=loop_audit,
        integrated_event_steps=tuple(steps),
        dispatch_resume_links=tuple(links),
        dispatch_audits=tuple(dispatch_audits),
        parent_resume_audits=tuple(parent_resume_audits),
        parent_resumes=tuple(parent_resumes),
        resume_stack_updates=tuple(stack_updates),
    )
    integrated_render = build_runtime_integrated_event_loop_timeline_render(integrated_trace)
    integrated_audit = build_runtime_integrated_event_loop_audit(
        integrated_loop_trace=integrated_trace,
        timeline_render=integrated_render,
        power_window=power_window,
        ticks=ticks,
        event_frames=tuple(frames),
        event_stacks=stacks,
        event_tree=tree,
        dispatch_resume_links=tuple(links),
    )
    integrated_readiness = build_runtime_integrated_event_loop_readiness(integrated_audit)
    return {
        "runtime_power_window": power_window.to_dict(),
        "runtime_ticks": [tick.to_dict() for tick in ticks],
        "runtime_event_frames": [frame.to_dict() for frame in frames],
        "runtime_event_stacks": [stack.to_dict() for stack in stacks],
        "runtime_event_returns": [item.to_dict() for item in event_returns],
        "runtime_event_tree": tree.to_dict(),
        "runtime_continuous_loop_trace": loop_trace.to_dict(),
        "runtime_continuous_loop_audit": loop_audit.to_dict(),
        "runtime_event_dispatch_requests": [item.to_dict() for item in dispatch_requests],
        "runtime_event_dispatch_routes": [item.to_dict() for item in dispatch_routes],
        "runtime_event_handler_adapters": [item.to_dict() for item in handler_adapters],
        "runtime_event_dispatch_results": [item.to_dict() for item in dispatch_results],
        "runtime_event_dispatch_return_payloads": [
            item.to_dict() for item in return_payloads
        ],
        "runtime_event_dispatch_audits": [item.to_dict() for item in dispatch_audits],
        "runtime_parent_frame_resume_requests": [
            item.to_dict() for item in resume_requests
        ],
        "runtime_parent_frame_resume_decisions": [
            item.to_dict() for item in resume_decisions
        ],
        "runtime_parent_frame_resumes": [item.to_dict() for item in parent_resumes],
        "runtime_parent_frame_resume_stack_updates": [
            item.to_dict() for item in stack_updates
        ],
        "runtime_parent_frame_resume_audits": [
            item.to_dict() for item in parent_resume_audits
        ],
        "runtime_integrated_event_steps": [item.to_dict() for item in steps],
        "runtime_integrated_dispatch_resume_links": [item.to_dict() for item in links],
        "runtime_integrated_event_loop_trace": integrated_trace.to_dict(),
        "runtime_integrated_event_loop_timeline_render": integrated_render.to_dict(),
        "runtime_integrated_event_loop_audit": integrated_audit.to_dict(),
        "runtime_integrated_event_loop_readiness": integrated_readiness.to_dict(),
    }


def _source_record_id_for_stage(
    stage: str,
    evidence: FirstClosedLoopEvidenceChainRecord,
    milestone: FirstClosedLoopMilestoneRecord,
) -> str | None:
    config = STAGE_CONFIG[stage]
    field_name = config["source_field"]
    if field_name is None:
        return milestone.milestone_id
    return getattr(evidence, str(field_name))


def _plan_summary(status: str) -> str:
    if status == "playback_plan_created":
        return "Fixed Package 94 closed-loop playback plan created."
    return f"Fixed playback plan blocked: {status}."


def _mapping_summary(status: str, stage: str, target_engine: str) -> str:
    if status == "stage_mapped_to_event_frame":
        return f"{stage} mapped to EventFrame dispatch lane {target_engine}."
    if status == "stage_mapped_as_group_member":
        return f"{stage} mapped as represented grouped EventFrame stage."
    return f"{stage} mapping blocked: {status}."


def _step_summary(status: str, stage: str) -> str:
    if status in {"playback_step_recorded", "playback_step_recorded_with_grouped_stage"}:
        return f"{stage} replayed as fixed record-only EventFrame playback."
    return f"{stage} playback step blocked: {status}."


def _trace_summary(status: str) -> str:
    if status == "fixed_closed_loop_playback_complete":
        return "Fixed closed-loop playback over Runtime EventFrames complete."
    if status == "fixed_closed_loop_playback_complete_with_grouped_stages":
        return "Fixed closed-loop playback complete with grouped stage evidence."
    return f"Fixed closed-loop playback blocked: {status}."


def _render_summary(status: str) -> str:
    if status == "fixed_playback_render_created":
        return "Fixed playback render created."
    if status == "fixed_playback_render_created_with_grouped_stages":
        return "Fixed playback render created with grouped stages."
    return "Fixed playback render blocked because trace is invalid."


def _readiness_summary(status: str) -> str:
    if status == "ready_for_bounded_handler_binding_only":
        return "Ready only for bounded fixed-stage handler binding."
    if status == "ready_for_runtime_state_persistence_binding_only":
        return "Ready only for runtime state persistence binding."
    if status == "ready_for_teacher_observed_playback_cli_only":
        return "Ready only for teacher-observed playback CLI."
    return f"Fixed playback readiness blocked: {status}."


def _audit_blocked_reasons(
    *,
    plan: RuntimeFixedClosedLoopPlaybackPlanRecord | None,
    trace: RuntimeFixedClosedLoopPlaybackTrace | None,
    milestone: FirstClosedLoopMilestoneRecord | None,
    integrated_trace: RuntimeIntegratedEventLoopTrace | None,
    force_missing_closed_loop_milestone: bool,
    force_missing_integrated_event_loop_trace: bool,
    force_first_output: bool,
) -> list[str]:
    reasons: list[str] = []
    if force_missing_closed_loop_milestone or milestone is None:
        reasons.append("missing_closed_loop_milestone")
    if force_missing_integrated_event_loop_trace or integrated_trace is None:
        reasons.append("missing_integrated_event_loop_trace")
    if plan is None or plan.playback_plan_status == "blocked_missing_closed_loop_milestone":
        if "missing_closed_loop_milestone" not in reasons:
            reasons.append("missing_closed_loop_milestone")
    if plan is None or plan.playback_plan_status == "blocked_missing_integrated_event_loop_trace":
        if "missing_integrated_event_loop_trace" not in reasons:
            reasons.append("missing_integrated_event_loop_trace")
    if trace is None:
        reasons.append("missing_fixed_playback_trace")
        return reasons
    if not trace.all_required_stages_represented:
        reasons.append("missing_required_stage")
    if not trace.all_steps_have_event_frames:
        reasons.append("missing_event_frame_mapping")
    if not trace.all_steps_have_dispatch_lineage:
        reasons.append("missing_dispatch_lineage")
    if not trace.all_steps_have_return_payloads:
        reasons.append("missing_return_payload")
    if not trace.all_child_returns_resumed:
        reasons.append("missing_parent_resume")
    if not trace.root_frame_closed:
        reasons.append("unclosed_root_event")
    if trace.live_engine_invocation_created:
        reasons.append("live_engine_invocation_detected")
    if trace.dynamic_child_event_created:
        reasons.append("dynamic_child_event_scheduling_detected")
    if trace.autonomous_scheduler_created:
        reasons.append("autonomous_scheduler_detected")
    if trace.open_ended_loop_created:
        reasons.append("open_ended_loop_detected")
    if trace.external_execution_created:
        reasons.append("external_execution_detected")
    if trace.memory_layer_write_performed:
        reasons.append("memory_write_detected")
    if trace.automatic_learning_approval_created:
        reasons.append("automatic_learning_approval_detected")
    if trace.recursive_learning_created:
        reasons.append("recursive_learning_detected")
    if trace.thought_engine_behavior_created:
        reasons.append("thought_engine_fake_detected")
    if force_first_output:
        reasons.append("first_output_detected")
    if trace.production_behavior_created:
        reasons.append("production_behavior_detected")
    return reasons


def _audit_status(
    trace: RuntimeFixedClosedLoopPlaybackTrace | None,
    blocked_reasons: list[str],
) -> str:
    priority = (
        ("missing_closed_loop_milestone", "blocked_missing_closed_loop_milestone"),
        ("missing_required_stage", "blocked_missing_required_stage"),
        (
            "missing_integrated_event_loop_trace",
            "blocked_missing_integrated_event_loop_trace",
        ),
        ("missing_event_frame_mapping", "blocked_missing_event_frame_mapping"),
        ("missing_dispatch_lineage", "blocked_missing_dispatch_lineage"),
        ("missing_return_payload", "blocked_missing_return_payload"),
        ("missing_parent_resume", "blocked_missing_parent_resume"),
        ("unclosed_root_event", "blocked_unclosed_root_event"),
        (
            "live_engine_invocation_detected",
            "blocked_live_engine_invocation_detected",
        ),
        (
            "dynamic_child_event_scheduling_detected",
            "blocked_dynamic_child_event_scheduling_detected",
        ),
        ("autonomous_scheduler_detected", "blocked_autonomous_scheduler_detected"),
        ("open_ended_loop_detected", "blocked_open_ended_loop_detected"),
        ("external_execution_detected", "blocked_external_execution_detected"),
        ("memory_write_detected", "blocked_memory_write_detected"),
        (
            "automatic_learning_approval_detected",
            "blocked_automatic_learning_approval_detected",
        ),
        ("recursive_learning_detected", "blocked_recursive_learning_detected"),
        ("thought_engine_fake_detected", "blocked_thought_engine_fake_detected"),
        ("first_output_detected", "blocked_first_output_detected"),
        ("production_behavior_detected", "blocked_production_behavior_detected"),
    )
    for reason, status in priority:
        if reason in blocked_reasons:
            return status
    if trace and trace.fixed_playback_status == "fixed_closed_loop_playback_complete_with_grouped_stages":
        return "passed_fixed_closed_loop_playback_with_grouped_stages"
    return "passed_fixed_closed_loop_playback_over_event_frames"


def _plan(value: RuntimeFixedClosedLoopPlaybackPlanRecord | dict[str, object]) -> RuntimeFixedClosedLoopPlaybackPlanRecord:
    return value if isinstance(value, RuntimeFixedClosedLoopPlaybackPlanRecord) else RuntimeFixedClosedLoopPlaybackPlanRecord.from_dict(value)


def _mapping(value: RuntimeClosedLoopStageToEventFrameMappingRecord | dict[str, object]) -> RuntimeClosedLoopStageToEventFrameMappingRecord:
    return value if isinstance(value, RuntimeClosedLoopStageToEventFrameMappingRecord) else RuntimeClosedLoopStageToEventFrameMappingRecord.from_dict(value)


def _step(value: RuntimeFixedClosedLoopPlaybackStepRecord | dict[str, object]) -> RuntimeFixedClosedLoopPlaybackStepRecord:
    return value if isinstance(value, RuntimeFixedClosedLoopPlaybackStepRecord) else RuntimeFixedClosedLoopPlaybackStepRecord.from_dict(value)


def _trace(value: RuntimeFixedClosedLoopPlaybackTrace | dict[str, object]) -> RuntimeFixedClosedLoopPlaybackTrace:
    return value if isinstance(value, RuntimeFixedClosedLoopPlaybackTrace) else RuntimeFixedClosedLoopPlaybackTrace.from_dict(value)


def _render(value: RuntimeFixedClosedLoopPlaybackRenderRecord | dict[str, object]) -> RuntimeFixedClosedLoopPlaybackRenderRecord:
    return value if isinstance(value, RuntimeFixedClosedLoopPlaybackRenderRecord) else RuntimeFixedClosedLoopPlaybackRenderRecord.from_dict(value)


def _audit(value: RuntimeFixedClosedLoopPlaybackAudit | dict[str, object]) -> RuntimeFixedClosedLoopPlaybackAudit:
    return value if isinstance(value, RuntimeFixedClosedLoopPlaybackAudit) else RuntimeFixedClosedLoopPlaybackAudit.from_dict(value)


def _readiness(value: RuntimeFixedClosedLoopPlaybackReadinessRecord | dict[str, object]) -> RuntimeFixedClosedLoopPlaybackReadinessRecord:
    return value if isinstance(value, RuntimeFixedClosedLoopPlaybackReadinessRecord) else RuntimeFixedClosedLoopPlaybackReadinessRecord.from_dict(value)


def _milestone(value: FirstClosedLoopMilestoneRecord | dict[str, object]) -> FirstClosedLoopMilestoneRecord:
    return value if isinstance(value, FirstClosedLoopMilestoneRecord) else FirstClosedLoopMilestoneRecord.from_dict(value)


def _event_frame(value: RuntimeEventFrameRecord | dict[str, object]) -> RuntimeEventFrameRecord:
    return value if isinstance(value, RuntimeEventFrameRecord) else RuntimeEventFrameRecord.from_dict(value)


def _integrated_trace(value: RuntimeIntegratedEventLoopTrace | dict[str, object]) -> RuntimeIntegratedEventLoopTrace:
    return value if isinstance(value, RuntimeIntegratedEventLoopTrace) else RuntimeIntegratedEventLoopTrace.from_dict(value)


def _integrated_step(value: RuntimeIntegratedEventStepRecord | dict[str, object]) -> RuntimeIntegratedEventStepRecord:
    return value if isinstance(value, RuntimeIntegratedEventStepRecord) else RuntimeIntegratedEventStepRecord.from_dict(value)


def _dispatch_resume_link(value: RuntimeIntegratedEventDispatchResumeLinkRecord | dict[str, object]) -> RuntimeIntegratedEventDispatchResumeLinkRecord:
    return value if isinstance(value, RuntimeIntegratedEventDispatchResumeLinkRecord) else RuntimeIntegratedEventDispatchResumeLinkRecord.from_dict(value)
