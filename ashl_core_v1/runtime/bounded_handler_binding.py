"""Bounded handler binding for fixed closed-loop Runtime playback."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
import hashlib
import json
from typing import Any

from ashl_core_v1.runtime.fixed_closed_loop_playback import (
    RuntimeClosedLoopStageToEventFrameMappingRecord,
    RuntimeFixedClosedLoopPlaybackAudit,
    RuntimeFixedClosedLoopPlaybackStepRecord,
    RuntimeFixedClosedLoopPlaybackTrace,
    build_demo_full_fixed_closed_loop_playback,
)


SOURCE_ENGINE = "runtime"

BINDING_PLAN_SCHEMA_VERSION = "runtime_bounded_handler_binding_plan_v0"
STAGE_BINDING_SCHEMA_VERSION = "runtime_fixed_stage_handler_binding_v0"
HANDLER_INVOCATION_SCHEMA_VERSION = "runtime_bounded_handler_invocation_v0"
OUTPUT_SNAPSHOT_SCHEMA_VERSION = "runtime_bounded_handler_output_snapshot_v0"
HANDLER_RETURN_SCHEMA_VERSION = "runtime_bounded_handler_return_payload_v0"
BINDING_TRACE_SCHEMA_VERSION = "runtime_bounded_handler_binding_trace_v0"
BINDING_AUDIT_SCHEMA_VERSION = "runtime_bounded_handler_binding_audit_v0"
BINDING_READINESS_SCHEMA_VERSION = "runtime_bounded_handler_binding_readiness_v0"

BINDING_PLAN_NAME = "package_99_fixed_playback_bounded_handler_binding"
BINDING_PLAN_KIND = "fixed_playback_handler_binding"
DEFAULT_HANDLER_BINDING_MODE = "record_only_snapshot"

SELECTED_BINDABLE_STAGES = (
    "sense_observation",
    "outcome_evaluation",
    "task_closure",
    "learning_feedback_candidate",
    "working_readback_integration",
    "closed_loop_milestone_audit",
)

BLOCKED_STAGE_NAMES = ("first_task_action_chain",)

HANDLER_CONFIG = {
    "sense_observation": {
        "handler_id": "package_86_demo_sense_observation_handoff_snapshot",
        "handler_name": "Package 86 demo sense observation handoff snapshot",
        "handler_module": "ashl_core_v1.sense",
        "handler_kind": "snapshot_adapter",
        "snapshot_kind": "sense_observation_snapshot",
        "available": True,
    },
    "outcome_evaluation": {
        "handler_id": "package_87_demo_outcome_evaluation_snapshot",
        "handler_name": "Package 87 demo outcome evaluation snapshot",
        "handler_module": "ashl_core_v1.task",
        "handler_kind": "snapshot_adapter",
        "snapshot_kind": "outcome_evaluation_snapshot",
        "available": True,
    },
    "task_closure": {
        "handler_id": "package_88_demo_task_closure_snapshot",
        "handler_name": "Package 88 demo task closure snapshot",
        "handler_module": "ashl_core_v1.task",
        "handler_kind": "snapshot_adapter",
        "snapshot_kind": "task_closure_snapshot",
        "available": True,
    },
    "learning_feedback_candidate": {
        "handler_id": "package_89_demo_learning_feedback_candidate_snapshot",
        "handler_name": "Package 89 demo learning feedback candidate snapshot",
        "handler_module": "ashl_core_v1.learning",
        "handler_kind": "snapshot_adapter",
        "snapshot_kind": "learning_feedback_candidate_snapshot",
        "available": True,
    },
    "concept_candidate_draft": {
        "handler_id": "package_90_demo_concept_candidate_draft_snapshot",
        "handler_name": "Package 90 demo concept candidate draft snapshot",
        "handler_module": "ashl_core_v1.learning",
        "handler_kind": "deferred_unavailable",
        "snapshot_kind": "deferred_unavailable_snapshot",
        "available": False,
    },
    "feedback_concept_refinement": {
        "handler_id": "package_91_demo_feedback_refinement_snapshot",
        "handler_name": "Package 91 demo feedback refinement snapshot",
        "handler_module": "ashl_core_v1.learning",
        "handler_kind": "deferred_unavailable",
        "snapshot_kind": "deferred_unavailable_snapshot",
        "available": False,
    },
    "feedback_derived_reviewed_concept": {
        "handler_id": "package_92_demo_feedback_reviewed_concept_snapshot",
        "handler_name": "Package 92 demo feedback reviewed concept snapshot",
        "handler_module": "ashl_core_v1.learning",
        "handler_kind": "deferred_unavailable",
        "snapshot_kind": "deferred_unavailable_snapshot",
        "available": False,
    },
    "working_readback_integration": {
        "handler_id": "package_92_demo_working_readback_integration_snapshot",
        "handler_name": "Package 92 demo working readback integration snapshot",
        "handler_module": "ashl_core_v1.memory",
        "handler_kind": "snapshot_adapter",
        "snapshot_kind": "working_readback_snapshot",
        "available": True,
    },
    "second_task_replay": {
        "handler_id": "package_93_demo_closed_loop_replay_snapshot",
        "handler_name": "Package 93 demo closed-loop replay snapshot",
        "handler_module": "ashl_core_v1.task",
        "handler_kind": "deferred_unavailable",
        "snapshot_kind": "deferred_unavailable_snapshot",
        "available": False,
    },
    "closed_loop_milestone_audit": {
        "handler_id": "package_94_demo_milestone_audit_snapshot",
        "handler_name": "Package 94 demo milestone audit snapshot",
        "handler_module": "ashl_core_v1.audit",
        "handler_kind": "snapshot_adapter",
        "snapshot_kind": "milestone_audit_snapshot",
        "available": True,
    },
}

ALLOWED_HANDLER_BINDING_MODES = {
    "record_only_snapshot",
    "bounded_demo_builder_snapshot",
    "deferred_handler_unavailable",
    "blocked_handler",
}
ALLOWED_PLAN_STATUSES = {
    "binding_plan_created",
    "blocked_missing_fixed_playback_trace",
    "blocked_missing_fixed_playback_audit",
    "blocked_unbounded_binding_plan",
    "blocked_live_engine_invocation_requested",
    "blocked_forbidden_authority_detected",
}
ALLOWED_HANDLER_KINDS = {
    "pure_demo_builder",
    "pure_record_builder",
    "pure_validator_builder",
    "snapshot_adapter",
    "deferred_unavailable",
    "blocked_unsafe",
}
ALLOWED_BINDING_STATUSES = {
    "handler_bound_to_fixed_stage",
    "handler_bound_as_snapshot_only",
    "handler_deferred_unavailable",
    "handler_blocked_not_side_effect_free",
    "handler_blocked_not_deterministic",
    "handler_blocked_not_fixture_bounded",
    "handler_blocked_stage_not_allowed",
    "handler_blocked_forbidden_authority_detected",
}
ALLOWED_INVOCATION_MODES = {
    "snapshot_only_no_call",
    "pure_demo_builder_call",
    "pure_validator_call",
    "deferred_not_called",
    "blocked_not_called",
}
ALLOWED_INVOCATION_STATUSES = {
    "handler_invocation_snapshot_recorded",
    "handler_invocation_pure_demo_completed",
    "handler_invocation_pure_validator_completed",
    "handler_invocation_deferred_unavailable",
    "handler_invocation_blocked_not_side_effect_free",
    "handler_invocation_blocked_not_deterministic",
    "handler_invocation_blocked_live_engine_invocation",
    "handler_invocation_blocked_forbidden_authority_detected",
}
ALLOWED_OUTPUT_KINDS = {
    "sense_observation_snapshot",
    "outcome_evaluation_snapshot",
    "task_closure_snapshot",
    "learning_feedback_candidate_snapshot",
    "concept_candidate_draft_snapshot",
    "feedback_refinement_snapshot",
    "feedback_reviewed_concept_snapshot",
    "working_readback_snapshot",
    "second_task_replay_snapshot",
    "milestone_audit_snapshot",
    "deferred_unavailable_snapshot",
    "blocked_snapshot",
}
ALLOWED_OUTPUT_STATUSES = {
    "output_snapshot_recorded",
    "output_snapshot_recorded_from_pure_builder",
    "output_snapshot_deferred_unavailable",
    "output_snapshot_blocked_invalid_shape",
    "output_snapshot_blocked_forbidden_authority_detected",
}
ALLOWED_RETURN_STATUSES = {
    "returned_success",
    "returned_blocked",
    "returned_unknown",
    "returned_deferred",
    "returned_fault",
    "blocked_forbidden_authority_detected",
}
ALLOWED_TRACE_STATUSES = {
    "bounded_handler_binding_trace_complete",
    "bounded_handler_binding_trace_complete_with_deferred_handlers",
    "bounded_handler_binding_trace_blocked_missing_playback",
    "bounded_handler_binding_trace_blocked_missing_binding",
    "bounded_handler_binding_trace_blocked_invalid_invocation",
    "bounded_handler_binding_trace_blocked_invalid_output",
    "bounded_handler_binding_trace_blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_bounded_handler_binding_for_fixed_playback",
    "passed_bounded_handler_binding_with_deferred_handlers",
    "blocked_missing_fixed_playback",
    "blocked_invalid_binding_plan",
    "blocked_invalid_stage_binding",
    "blocked_invalid_handler_invocation",
    "blocked_invalid_output_snapshot",
    "blocked_live_engine_invocation_detected",
    "blocked_dynamic_handler_selection_detected",
    "blocked_dynamic_child_event_scheduling_detected",
    "blocked_autonomous_scheduler_detected",
    "blocked_open_ended_loop_detected",
    "blocked_external_execution_detected",
    "blocked_memory_write_detected",
    "blocked_automatic_learning_approval_detected",
    "blocked_recursive_learning_detected",
    "blocked_new_learning_artifact_detected",
    "blocked_new_sandbox_execution_detected",
    "blocked_thought_engine_fake_detected",
    "blocked_first_output_detected",
    "blocked_production_behavior_detected",
}
ALLOWED_READINESS_STATUSES = {
    "ready_for_handler_bound_fixed_playback_audit_milestone_only",
    "ready_for_runtime_state_persistence_binding_only",
    "ready_for_teacher_observed_playback_cli_only",
    "not_ready_missing_handler_binding_trace",
    "not_ready_boundary_failure",
    "blocked_forbidden_authority_detected",
}

SAFE_CLAIM = (
    "ASHL Core v1 can bind selected fixed closed-loop playback EventFrame "
    "stages to deterministic side-effect-free handler builders or snapshot "
    "adapters, produce bounded handler output snapshots and safe return "
    "payloads, and audit the binding trace."
)
BLOCKED_CLAIMS = (
    "no_live_qingyin_runtime_session",
    "no_dynamic_handler_selection",
    "no_dynamic_child_event_scheduling",
    "no_autonomous_scheduler",
    "no_open_ended_loop",
    "no_live_engine_invocation",
    "no_external_execution",
    "no_memory_layer_write",
    "no_automatic_learning_approval",
    "no_recursive_learning",
    "no_new_learning_artifacts",
    "no_new_sandbox_execution",
    "no_thought_engine_behavior",
    "no_first_output",
    "not_awake",
)
READINESS_NEXT_PACKAGE = (
    "Package 101 / ASHL Core v1 Runtime Handler-Bound Fixed Playback "
    "Milestone Audit Minimal v0"
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
        else:
            safe.append("_")
    return "_".join("".join(safe).split("_"))[:100] or "empty"


def _fixture_hash(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class RuntimeBoundedHandlerBindingPlanRecord:
    bounded_handler_binding_plan_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_fixed_playback_trace_id: str | None
    source_fixed_playback_audit_id: str | None
    binding_plan_name: str
    binding_plan_kind: str
    allowed_stage_names: tuple[str, ...]
    blocked_stage_names: tuple[str, ...]
    handler_binding_mode: str
    bounded_fixture_only: bool
    fixed_sequence_only: bool
    side_effect_free_required: bool
    deterministic_required: bool
    record_output_snapshot_only: bool
    dynamic_handler_discovery_allowed: bool
    dynamic_child_event_scheduling_allowed: bool
    live_engine_invocation_allowed: bool
    external_execution_allowed: bool
    memory_layer_write_allowed: bool
    automatic_learning_approval_allowed: bool
    recursive_learning_allowed: bool
    thought_engine_runtime_allowed: bool
    first_output_allowed: bool
    production_behavior_allowed: bool
    binding_plan_status: str
    binding_plan_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BINDING_PLAN_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_bounded_handler_binding_plan_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.binding_plan_name != BINDING_PLAN_NAME:
            raise ValueError("binding_plan_name must be package_99_fixed_playback_bounded_handler_binding")
        if self.binding_plan_kind != BINDING_PLAN_KIND:
            raise ValueError("binding_plan_kind must be fixed_playback_handler_binding")
        if self.handler_binding_mode not in ALLOWED_HANDLER_BINDING_MODES:
            raise ValueError(f"unknown handler_binding_mode: {self.handler_binding_mode}")
        if self.binding_plan_status not in ALLOWED_PLAN_STATUSES:
            raise ValueError(f"unknown binding_plan_status: {self.binding_plan_status}")
        for name in ("allowed_stage_names", "blocked_stage_names", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "RuntimeBoundedHandlerBindingPlanRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeFixedStageHandlerBindingRecord:
    fixed_stage_handler_binding_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_binding_plan_id: str
    source_playback_step_id: str
    source_stage_event_mapping_id: str
    closed_loop_stage_name: str
    event_frame_id: str
    event_type: str
    event_family: str
    target_engine_lane: str
    handler_id: str
    handler_name: str
    handler_module: str | None
    handler_kind: str
    handler_available: bool
    handler_side_effect_free_declared: bool
    handler_deterministic_declared: bool
    handler_fixture_bounded: bool
    binding_status: str
    binding_summary: str
    handler_invocation_allowed: bool
    live_engine_invocation_allowed: bool
    record_output_snapshot_only: bool
    creates_new_learning_artifact: bool
    creates_new_memory_write: bool
    creates_new_sandbox_execution: bool
    creates_external_execution: bool
    creates_first_output: bool
    creates_thought_engine_behavior: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != STAGE_BINDING_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_fixed_stage_handler_binding_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.handler_kind not in ALLOWED_HANDLER_KINDS:
            raise ValueError(f"unknown handler_kind: {self.handler_kind}")
        if self.binding_status not in ALLOWED_BINDING_STATUSES:
            raise ValueError(f"unknown binding_status: {self.binding_status}")
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
    ) -> "RuntimeFixedStageHandlerBindingRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeBoundedHandlerInvocationRecord:
    bounded_handler_invocation_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_fixed_stage_handler_binding_id: str
    source_playback_step_id: str
    handler_id: str
    handler_name: str
    handler_kind: str
    invocation_mode: str
    invocation_status: str
    invocation_summary: str
    fixed_fixture_input: dict[str, object]
    input_fixture_hash: str | None
    handler_called: bool
    handler_call_side_effect_free: bool
    handler_call_deterministic: bool
    handler_call_bounded: bool
    output_snapshot_id: str | None
    live_engine_invocation_created: bool
    dynamic_handler_selection_created: bool
    dynamic_child_event_created: bool
    new_learning_feedback_candidate_created: bool
    new_concept_candidate_created: bool
    new_reviewed_concept_created: bool
    new_memory_application_data_created: bool
    new_memory_write_performed: bool
    new_sandbox_execution_performed: bool
    external_execution_created: bool
    automatic_learning_approval_created: bool
    recursive_learning_created: bool
    thought_engine_behavior_created: bool
    first_output_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HANDLER_INVOCATION_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_bounded_handler_invocation_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.invocation_mode not in ALLOWED_INVOCATION_MODES:
            raise ValueError(f"unknown invocation_mode: {self.invocation_mode}")
        if self.invocation_status not in ALLOWED_INVOCATION_STATUSES:
            raise ValueError(f"unknown invocation_status: {self.invocation_status}")
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
    ) -> "RuntimeBoundedHandlerInvocationRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeBoundedHandlerOutputSnapshotRecord:
    bounded_handler_output_snapshot_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_bounded_handler_invocation_id: str
    source_fixed_stage_handler_binding_id: str
    closed_loop_stage_name: str
    handler_id: str
    target_engine_lane: str
    output_snapshot_kind: str
    output_snapshot_payload: dict[str, object]
    output_matches_expected_stage_shape: bool
    output_trace_refs_preserved: bool
    output_safe_for_return_payload: bool
    output_snapshot_status: str
    output_snapshot_summary: str
    creates_new_engine_state: bool
    creates_new_memory_write: bool
    creates_new_learning_approval: bool
    creates_new_execution: bool
    creates_external_side_effect: bool
    creates_first_output: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != OUTPUT_SNAPSHOT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_bounded_handler_output_snapshot_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.output_snapshot_kind not in ALLOWED_OUTPUT_KINDS:
            raise ValueError(f"unknown output_snapshot_kind: {self.output_snapshot_kind}")
        if self.output_snapshot_status not in ALLOWED_OUTPUT_STATUSES:
            raise ValueError(
                f"unknown output_snapshot_status: {self.output_snapshot_status}"
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
        cls, data: dict[str, object]
    ) -> "RuntimeBoundedHandlerOutputSnapshotRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeBoundedHandlerReturnPayloadRecord:
    bounded_handler_return_payload_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_output_snapshot_id: str
    source_bounded_handler_invocation_id: str
    closed_loop_stage_name: str
    event_frame_id: str
    handler_id: str
    return_status: str
    return_reason: str
    return_summary: str
    return_payload: dict[str, object]
    safe_for_dispatch_return_payload: bool
    safe_for_parent_resume: bool
    requires_parent_resume: bool
    requires_followup_event: bool
    creates_followup_event: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    recursive_learning_created: bool
    external_execution_created: bool
    first_output_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HANDLER_RETURN_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_bounded_handler_return_payload_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.return_status not in ALLOWED_RETURN_STATUSES:
            raise ValueError(f"unknown return_status: {self.return_status}")
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
    ) -> "RuntimeBoundedHandlerReturnPayloadRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeBoundedHandlerBindingTrace:
    bounded_handler_binding_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_binding_plan_id: str
    source_fixed_playback_trace_id: str | None
    stage_binding_ids: tuple[str, ...]
    handler_invocation_ids: tuple[str, ...]
    output_snapshot_ids: tuple[str, ...]
    handler_return_payload_ids: tuple[str, ...]
    bound_stage_names: tuple[str, ...]
    deferred_stage_names: tuple[str, ...]
    blocked_stage_names: tuple[str, ...]
    handler_binding_count: int
    handler_invocation_count: int
    output_snapshot_count: int
    return_payload_count: int
    all_allowed_stages_bound_or_deferred: bool
    all_invocations_side_effect_free: bool
    all_outputs_safe_for_return: bool
    all_returns_safe_for_parent_resume: bool
    binding_trace_status: str
    binding_trace_summary: str
    live_engine_invocation_created: bool
    dynamic_handler_selection_created: bool
    dynamic_child_event_created: bool
    external_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    recursive_learning_created: bool
    new_learning_artifact_created: bool
    new_sandbox_execution_performed: bool
    thought_engine_behavior_created: bool
    first_output_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BINDING_TRACE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_bounded_handler_binding_trace_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.binding_trace_status not in ALLOWED_TRACE_STATUSES:
            raise ValueError(f"unknown binding_trace_status: {self.binding_trace_status}")
        for name in (
            "stage_binding_ids",
            "handler_invocation_ids",
            "output_snapshot_ids",
            "handler_return_payload_ids",
            "bound_stage_names",
            "deferred_stage_names",
            "blocked_stage_names",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeBoundedHandlerBindingTrace":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeBoundedHandlerBindingAudit:
    bounded_handler_binding_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_binding_plan_id: str | None
    source_binding_trace_id: str | None
    fixed_playback_valid: bool
    binding_plan_valid: bool
    stage_bindings_valid: bool
    handler_invocations_valid: bool
    output_snapshots_valid: bool
    handler_return_payloads_valid: bool
    binding_trace_valid: bool
    fixed_sequence_confirmed: bool
    bounded_fixture_confirmed: bool
    side_effect_free_confirmed: bool
    deterministic_confirmed: bool
    snapshot_only_confirmed: bool
    no_live_engine_invocation: bool
    no_dynamic_handler_selection: bool
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
    no_new_learning_artifacts: bool
    no_new_sandbox_execution: bool
    no_thought_engine_behavior: bool
    no_first_output: bool
    no_production_behavior: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != BINDING_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_bounded_handler_binding_audit_v0"
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
    def from_dict(cls, data: dict[str, object]) -> "RuntimeBoundedHandlerBindingAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeBoundedHandlerBindingReadinessRecord:
    bounded_handler_binding_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_bounded_handler_binding_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_handler_bound_fixed_playback_audit_milestone: bool
    ready_for_runtime_state_persistence_binding: bool
    ready_for_teacher_observed_playback_cli: bool
    ready_for_live_runtime_session: bool
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
        if self.schema_version != BINDING_READINESS_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_bounded_handler_binding_readiness_v0"
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
    ) -> "RuntimeBoundedHandlerBindingReadinessRecord":
        return cls(**dict(data))


def build_runtime_bounded_handler_binding_plan(
    *,
    fixed_playback_trace: RuntimeFixedClosedLoopPlaybackTrace | dict[str, object] | None,
    fixed_playback_audit: RuntimeFixedClosedLoopPlaybackAudit | dict[str, object] | None,
    allowed_stage_names: tuple[str, ...] | list[str] = SELECTED_BINDABLE_STAGES,
    blocked_stage_names: tuple[str, ...] | list[str] = BLOCKED_STAGE_NAMES,
    handler_binding_mode: str = DEFAULT_HANDLER_BINDING_MODE,
    dynamic_handler_discovery_allowed: bool = False,
    dynamic_child_event_scheduling_allowed: bool = False,
    live_engine_invocation_allowed: bool = False,
    external_execution_allowed: bool = False,
    memory_layer_write_allowed: bool = False,
    automatic_learning_approval_allowed: bool = False,
    recursive_learning_allowed: bool = False,
    thought_engine_runtime_allowed: bool = False,
    first_output_allowed: bool = False,
    production_behavior_allowed: bool = False,
) -> RuntimeBoundedHandlerBindingPlanRecord:
    trace = _fixed_trace(fixed_playback_trace) if fixed_playback_trace is not None else None
    audit = _fixed_audit(fixed_playback_audit) if fixed_playback_audit is not None else None
    allowed = tuple(allowed_stage_names)
    blocked = tuple(blocked_stage_names)
    forbidden = any(
        (
            dynamic_handler_discovery_allowed,
            dynamic_child_event_scheduling_allowed,
            external_execution_allowed,
            memory_layer_write_allowed,
            automatic_learning_approval_allowed,
            recursive_learning_allowed,
            thought_engine_runtime_allowed,
            first_output_allowed,
            production_behavior_allowed,
        )
    )
    if trace is None:
        status = "blocked_missing_fixed_playback_trace"
    elif audit is None:
        status = "blocked_missing_fixed_playback_audit"
    elif not allowed or handler_binding_mode not in ALLOWED_HANDLER_BINDING_MODES:
        status = "blocked_unbounded_binding_plan"
    elif live_engine_invocation_allowed:
        status = "blocked_live_engine_invocation_requested"
    elif forbidden:
        status = "blocked_forbidden_authority_detected"
    else:
        status = "binding_plan_created"
    return RuntimeBoundedHandlerBindingPlanRecord(
        bounded_handler_binding_plan_id=(
            f"runtime_bounded_handler_binding_plan:{BINDING_PLAN_NAME}:"
            f"{_slug('_'.join(allowed))}"
        ),
        schema_version=BINDING_PLAN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_fixed_playback_trace_id=trace.fixed_playback_trace_id if trace else None,
        source_fixed_playback_audit_id=audit.fixed_playback_audit_id if audit else None,
        binding_plan_name=BINDING_PLAN_NAME,
        binding_plan_kind=BINDING_PLAN_KIND,
        allowed_stage_names=allowed,
        blocked_stage_names=blocked,
        handler_binding_mode=handler_binding_mode,
        bounded_fixture_only=True,
        fixed_sequence_only=True,
        side_effect_free_required=True,
        deterministic_required=True,
        record_output_snapshot_only=True,
        dynamic_handler_discovery_allowed=dynamic_handler_discovery_allowed,
        dynamic_child_event_scheduling_allowed=dynamic_child_event_scheduling_allowed,
        live_engine_invocation_allowed=live_engine_invocation_allowed,
        external_execution_allowed=external_execution_allowed,
        memory_layer_write_allowed=memory_layer_write_allowed,
        automatic_learning_approval_allowed=automatic_learning_approval_allowed,
        recursive_learning_allowed=recursive_learning_allowed,
        thought_engine_runtime_allowed=thought_engine_runtime_allowed,
        first_output_allowed=first_output_allowed,
        production_behavior_allowed=production_behavior_allowed,
        binding_plan_status=status,
        binding_plan_summary=_plan_summary(status),
        source_trace_refs=trace.source_trace_refs if trace else tuple(),
    )


def validate_runtime_bounded_handler_binding_plan(
    record: RuntimeBoundedHandlerBindingPlanRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _plan(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.binding_plan_status == "binding_plan_created":
        if not item.source_fixed_playback_trace_id:
            errors.append("missing_fixed_playback_trace")
        if not item.source_fixed_playback_audit_id:
            errors.append("missing_fixed_playback_audit")
        if not item.allowed_stage_names:
            errors.append("missing_allowed_stage_names")
    for flag in (
        "dynamic_handler_discovery_allowed",
        "dynamic_child_event_scheduling_allowed",
        "live_engine_invocation_allowed",
        "external_execution_allowed",
        "memory_layer_write_allowed",
        "automatic_learning_approval_allowed",
        "recursive_learning_allowed",
        "thought_engine_runtime_allowed",
        "first_output_allowed",
        "production_behavior_allowed",
    ):
        if getattr(item, flag) and not item.binding_plan_status.startswith("blocked_"):
            errors.append(f"{flag}_not_blocked")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "bounded_handler_binding_plan_id": item.bounded_handler_binding_plan_id,
        "binding_plan_status": item.binding_plan_status,
    }


def build_runtime_fixed_stage_handler_binding(
    *,
    binding_plan: RuntimeBoundedHandlerBindingPlanRecord | dict[str, object],
    playback_step: RuntimeFixedClosedLoopPlaybackStepRecord | dict[str, object],
    stage_event_mapping: RuntimeClosedLoopStageToEventFrameMappingRecord | dict[str, object],
    handler_side_effect_free_declared: bool = True,
    handler_deterministic_declared: bool = True,
    handler_fixture_bounded: bool = True,
    handler_available: bool | None = None,
    force_forbidden_authority: bool = False,
    creates_new_learning_artifact: bool = False,
    creates_new_memory_write: bool = False,
    creates_new_sandbox_execution: bool = False,
    creates_external_execution: bool = False,
    creates_first_output: bool = False,
    creates_thought_engine_behavior: bool = False,
) -> RuntimeFixedStageHandlerBindingRecord:
    plan = _plan(binding_plan)
    step = _playback_step(playback_step)
    mapping = _stage_mapping(stage_event_mapping)
    config = HANDLER_CONFIG.get(step.closed_loop_stage_name)
    if config is None:
        config = {
            "handler_id": f"unavailable_handler:{_slug(step.closed_loop_stage_name)}",
            "handler_name": f"Unavailable handler for {step.closed_loop_stage_name}",
            "handler_module": None,
            "handler_kind": "deferred_unavailable",
            "available": False,
        }
    available = bool(config["available"]) if handler_available is None else handler_available
    forbidden = any(
        (
            force_forbidden_authority,
            creates_new_learning_artifact,
            creates_new_memory_write,
            creates_new_sandbox_execution,
            creates_external_execution,
            creates_first_output,
            creates_thought_engine_behavior,
        )
    )
    if step.closed_loop_stage_name not in plan.allowed_stage_names:
        status = "handler_blocked_stage_not_allowed"
        handler_kind = "blocked_unsafe"
    elif forbidden:
        status = "handler_blocked_forbidden_authority_detected"
        handler_kind = "blocked_unsafe"
    elif not handler_side_effect_free_declared:
        status = "handler_blocked_not_side_effect_free"
        handler_kind = "blocked_unsafe"
    elif not handler_deterministic_declared:
        status = "handler_blocked_not_deterministic"
        handler_kind = "blocked_unsafe"
    elif not handler_fixture_bounded:
        status = "handler_blocked_not_fixture_bounded"
        handler_kind = "blocked_unsafe"
    elif not available:
        status = "handler_deferred_unavailable"
        handler_kind = "deferred_unavailable"
    else:
        handler_kind = str(config["handler_kind"])
        status = (
            "handler_bound_as_snapshot_only"
            if handler_kind == "snapshot_adapter"
            else "handler_bound_to_fixed_stage"
        )
    return RuntimeFixedStageHandlerBindingRecord(
        fixed_stage_handler_binding_id=(
            f"runtime_fixed_stage_handler_binding:{plan.bounded_handler_binding_plan_id}:"
            f"{step.step_index}:{_slug(step.closed_loop_stage_name)}"
        ),
        schema_version=STAGE_BINDING_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_binding_plan_id=plan.bounded_handler_binding_plan_id,
        source_playback_step_id=step.playback_step_id,
        source_stage_event_mapping_id=mapping.stage_event_mapping_id,
        closed_loop_stage_name=step.closed_loop_stage_name,
        event_frame_id=step.event_frame_id,
        event_type=step.event_type,
        event_family=step.event_family,
        target_engine_lane=step.target_engine_lane,
        handler_id=str(config["handler_id"]),
        handler_name=str(config["handler_name"]),
        handler_module=config.get("handler_module"),
        handler_kind=handler_kind,
        handler_available=available,
        handler_side_effect_free_declared=handler_side_effect_free_declared,
        handler_deterministic_declared=handler_deterministic_declared,
        handler_fixture_bounded=handler_fixture_bounded,
        binding_status=status,
        binding_summary=_binding_summary(status, step.closed_loop_stage_name),
        handler_invocation_allowed=status in {
            "handler_bound_to_fixed_stage",
            "handler_bound_as_snapshot_only",
        },
        live_engine_invocation_allowed=False,
        record_output_snapshot_only=True,
        creates_new_learning_artifact=creates_new_learning_artifact,
        creates_new_memory_write=creates_new_memory_write,
        creates_new_sandbox_execution=creates_new_sandbox_execution,
        creates_external_execution=creates_external_execution,
        creates_first_output=creates_first_output,
        creates_thought_engine_behavior=creates_thought_engine_behavior,
        source_trace_refs=plan.source_trace_refs,
    )


def validate_runtime_fixed_stage_handler_binding(
    record: RuntimeFixedStageHandlerBindingRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _stage_binding(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.binding_status in {
        "handler_bound_to_fixed_stage",
        "handler_bound_as_snapshot_only",
    }:
        if not item.handler_available:
            errors.append("handler_unavailable")
        if not item.handler_side_effect_free_declared:
            errors.append("handler_not_side_effect_free")
        if not item.handler_deterministic_declared:
            errors.append("handler_not_deterministic")
        if not item.handler_fixture_bounded:
            errors.append("handler_not_fixture_bounded")
    for flag in (
        "creates_new_learning_artifact",
        "creates_new_memory_write",
        "creates_new_sandbox_execution",
        "creates_external_execution",
        "creates_first_output",
        "creates_thought_engine_behavior",
    ):
        if getattr(item, flag) and item.binding_status != "handler_blocked_forbidden_authority_detected":
            errors.append(f"{flag}_not_blocked")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "fixed_stage_handler_binding_id": item.fixed_stage_handler_binding_id,
        "binding_status": item.binding_status,
    }


def build_runtime_bounded_handler_invocation(
    *,
    fixed_stage_handler_binding: RuntimeFixedStageHandlerBindingRecord | dict[str, object],
    playback_step: RuntimeFixedClosedLoopPlaybackStepRecord | dict[str, object],
    fixed_fixture_input: dict[str, object] | None = None,
    invocation_mode: str = "snapshot_only_no_call",
    live_engine_invocation_created: bool = False,
    dynamic_handler_selection_created: bool = False,
    dynamic_child_event_created: bool = False,
    new_learning_feedback_candidate_created: bool = False,
    new_concept_candidate_created: bool = False,
    new_reviewed_concept_created: bool = False,
    new_memory_application_data_created: bool = False,
    new_memory_write_performed: bool = False,
    new_sandbox_execution_performed: bool = False,
    external_execution_created: bool = False,
    automatic_learning_approval_created: bool = False,
    recursive_learning_created: bool = False,
    thought_engine_behavior_created: bool = False,
    first_output_created: bool = False,
    production_behavior_created: bool = False,
) -> RuntimeBoundedHandlerInvocationRecord:
    binding = _stage_binding(fixed_stage_handler_binding)
    step = _playback_step(playback_step)
    fixture = fixed_fixture_input or _fixed_fixture_for_binding(binding, step)
    learning_artifact = any(
        (
            new_learning_feedback_candidate_created,
            new_concept_candidate_created,
            new_reviewed_concept_created,
            new_memory_application_data_created,
        )
    )
    forbidden = any(
        (
            dynamic_handler_selection_created,
            dynamic_child_event_created,
            learning_artifact,
            new_memory_write_performed,
            new_sandbox_execution_performed,
            external_execution_created,
            automatic_learning_approval_created,
            recursive_learning_created,
            thought_engine_behavior_created,
            first_output_created,
            production_behavior_created,
        )
    )
    if binding.binding_status == "handler_deferred_unavailable":
        mode = "deferred_not_called"
        status = "handler_invocation_deferred_unavailable"
    elif binding.binding_status == "handler_blocked_not_side_effect_free":
        mode = "blocked_not_called"
        status = "handler_invocation_blocked_not_side_effect_free"
    elif binding.binding_status == "handler_blocked_not_deterministic":
        mode = "blocked_not_called"
        status = "handler_invocation_blocked_not_deterministic"
    elif live_engine_invocation_created:
        mode = "blocked_not_called"
        status = "handler_invocation_blocked_live_engine_invocation"
    elif forbidden or binding.binding_status.startswith("handler_blocked"):
        mode = "blocked_not_called"
        status = "handler_invocation_blocked_forbidden_authority_detected"
    elif invocation_mode == "pure_demo_builder_call":
        mode = "pure_demo_builder_call"
        status = "handler_invocation_pure_demo_completed"
    elif invocation_mode == "pure_validator_call":
        mode = "pure_validator_call"
        status = "handler_invocation_pure_validator_completed"
    else:
        mode = "snapshot_only_no_call"
        status = "handler_invocation_snapshot_recorded"
    called = mode in {"pure_demo_builder_call", "pure_validator_call"}
    invocation_id = (
        f"runtime_bounded_handler_invocation:{binding.fixed_stage_handler_binding_id}"
    )
    return RuntimeBoundedHandlerInvocationRecord(
        bounded_handler_invocation_id=invocation_id,
        schema_version=HANDLER_INVOCATION_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_fixed_stage_handler_binding_id=binding.fixed_stage_handler_binding_id,
        source_playback_step_id=step.playback_step_id,
        handler_id=binding.handler_id,
        handler_name=binding.handler_name,
        handler_kind=binding.handler_kind,
        invocation_mode=mode,
        invocation_status=status,
        invocation_summary=_invocation_summary(status, binding.closed_loop_stage_name),
        fixed_fixture_input=fixture,
        input_fixture_hash=_fixture_hash(fixture),
        handler_called=called,
        handler_call_side_effect_free=not status.startswith("handler_invocation_blocked"),
        handler_call_deterministic=not status.startswith("handler_invocation_blocked"),
        handler_call_bounded=not status.startswith("handler_invocation_blocked"),
        output_snapshot_id=f"runtime_bounded_handler_output_snapshot:{invocation_id}",
        live_engine_invocation_created=live_engine_invocation_created,
        dynamic_handler_selection_created=dynamic_handler_selection_created,
        dynamic_child_event_created=dynamic_child_event_created,
        new_learning_feedback_candidate_created=new_learning_feedback_candidate_created,
        new_concept_candidate_created=new_concept_candidate_created,
        new_reviewed_concept_created=new_reviewed_concept_created,
        new_memory_application_data_created=new_memory_application_data_created,
        new_memory_write_performed=new_memory_write_performed,
        new_sandbox_execution_performed=new_sandbox_execution_performed,
        external_execution_created=external_execution_created,
        automatic_learning_approval_created=automatic_learning_approval_created,
        recursive_learning_created=recursive_learning_created or learning_artifact,
        thought_engine_behavior_created=thought_engine_behavior_created,
        first_output_created=first_output_created,
        production_behavior_created=production_behavior_created,
        source_trace_refs=binding.source_trace_refs,
    )


def validate_runtime_bounded_handler_invocation(
    record: RuntimeBoundedHandlerInvocationRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _invocation(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.invocation_status in {
        "handler_invocation_snapshot_recorded",
        "handler_invocation_pure_demo_completed",
        "handler_invocation_pure_validator_completed",
    }:
        if item.live_engine_invocation_created:
            errors.append("live_engine_invocation_created")
        if not item.handler_call_side_effect_free:
            errors.append("handler_call_not_side_effect_free")
        if not item.handler_call_deterministic:
            errors.append("handler_call_not_deterministic")
        if not item.handler_call_bounded:
            errors.append("handler_call_not_bounded")
    for flag in _INVOCATION_FORBIDDEN_FLAGS:
        if getattr(item, flag) and not item.invocation_status.startswith(
            "handler_invocation_blocked"
        ):
            errors.append(f"{flag}_not_blocked")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "bounded_handler_invocation_id": item.bounded_handler_invocation_id,
        "invocation_status": item.invocation_status,
    }


def build_runtime_bounded_handler_output_snapshot(
    *,
    bounded_handler_invocation: RuntimeBoundedHandlerInvocationRecord | dict[str, object],
    fixed_stage_handler_binding: RuntimeFixedStageHandlerBindingRecord | dict[str, object],
    output_snapshot_payload: dict[str, object] | None = None,
    force_invalid_shape: bool = False,
    creates_new_engine_state: bool = False,
    creates_new_memory_write: bool = False,
    creates_new_learning_approval: bool = False,
    creates_new_execution: bool = False,
    creates_external_side_effect: bool = False,
    creates_first_output: bool = False,
) -> RuntimeBoundedHandlerOutputSnapshotRecord:
    invocation = _invocation(bounded_handler_invocation)
    binding = _stage_binding(fixed_stage_handler_binding)
    config = HANDLER_CONFIG.get(binding.closed_loop_stage_name, {})
    forbidden = any(
        (
            creates_new_engine_state,
            creates_new_memory_write,
            creates_new_learning_approval,
            creates_new_execution,
            creates_external_side_effect,
            creates_first_output,
        )
    )
    payload = output_snapshot_payload or _output_payload_for_binding(binding, invocation)
    shape_valid = _snapshot_shape_valid(payload, binding) and not force_invalid_shape
    if forbidden:
        status = "output_snapshot_blocked_forbidden_authority_detected"
        kind = "blocked_snapshot"
    elif invocation.invocation_status == "handler_invocation_deferred_unavailable":
        status = "output_snapshot_deferred_unavailable"
        kind = "deferred_unavailable_snapshot"
    elif invocation.invocation_status.startswith("handler_invocation_blocked"):
        status = "output_snapshot_blocked_forbidden_authority_detected"
        kind = "blocked_snapshot"
    elif not shape_valid:
        status = "output_snapshot_blocked_invalid_shape"
        kind = "blocked_snapshot"
    elif invocation.handler_called:
        status = "output_snapshot_recorded_from_pure_builder"
        kind = str(config.get("snapshot_kind", "blocked_snapshot"))
    else:
        status = "output_snapshot_recorded"
        kind = str(config.get("snapshot_kind", "blocked_snapshot"))
    return RuntimeBoundedHandlerOutputSnapshotRecord(
        bounded_handler_output_snapshot_id=(
            invocation.output_snapshot_id
            or f"runtime_bounded_handler_output_snapshot:{invocation.bounded_handler_invocation_id}"
        ),
        schema_version=OUTPUT_SNAPSHOT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_bounded_handler_invocation_id=invocation.bounded_handler_invocation_id,
        source_fixed_stage_handler_binding_id=binding.fixed_stage_handler_binding_id,
        closed_loop_stage_name=binding.closed_loop_stage_name,
        handler_id=binding.handler_id,
        target_engine_lane=binding.target_engine_lane,
        output_snapshot_kind=kind,
        output_snapshot_payload=payload,
        output_matches_expected_stage_shape=shape_valid,
        output_trace_refs_preserved=True,
        output_safe_for_return_payload=not status.startswith("output_snapshot_blocked"),
        output_snapshot_status=status,
        output_snapshot_summary=_output_summary(status, binding.closed_loop_stage_name),
        creates_new_engine_state=creates_new_engine_state,
        creates_new_memory_write=creates_new_memory_write,
        creates_new_learning_approval=creates_new_learning_approval,
        creates_new_execution=creates_new_execution,
        creates_external_side_effect=creates_external_side_effect,
        creates_first_output=creates_first_output,
        source_trace_refs=binding.source_trace_refs,
    )


def validate_runtime_bounded_handler_output_snapshot(
    record: RuntimeBoundedHandlerOutputSnapshotRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _snapshot(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.output_snapshot_status in {
        "output_snapshot_recorded",
        "output_snapshot_recorded_from_pure_builder",
    }:
        if not item.output_matches_expected_stage_shape:
            errors.append("invalid_stage_shape")
        if not item.output_trace_refs_preserved:
            errors.append("trace_refs_not_preserved")
        if not item.output_safe_for_return_payload:
            errors.append("not_safe_for_return")
    for flag in (
        "creates_new_engine_state",
        "creates_new_memory_write",
        "creates_new_learning_approval",
        "creates_new_execution",
        "creates_external_side_effect",
        "creates_first_output",
    ):
        if getattr(item, flag) and item.output_snapshot_status != "output_snapshot_blocked_forbidden_authority_detected":
            errors.append(f"{flag}_not_blocked")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "bounded_handler_output_snapshot_id": item.bounded_handler_output_snapshot_id,
        "output_snapshot_status": item.output_snapshot_status,
    }


def build_runtime_bounded_handler_return_payload(
    *,
    bounded_handler_output_snapshot: RuntimeBoundedHandlerOutputSnapshotRecord | dict[str, object],
    bounded_handler_invocation: RuntimeBoundedHandlerInvocationRecord | dict[str, object],
    fixed_stage_handler_binding: RuntimeFixedStageHandlerBindingRecord | dict[str, object],
    requires_followup_event: bool = False,
    memory_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    recursive_learning_created: bool = False,
    external_execution_created: bool = False,
    first_output_created: bool = False,
    production_behavior_created: bool = False,
) -> RuntimeBoundedHandlerReturnPayloadRecord:
    snapshot = _snapshot(bounded_handler_output_snapshot)
    invocation = _invocation(bounded_handler_invocation)
    binding = _stage_binding(fixed_stage_handler_binding)
    forbidden = any(
        (
            memory_write_performed,
            automatic_learning_approval_created,
            recursive_learning_created,
            external_execution_created,
            first_output_created,
            production_behavior_created,
        )
    )
    if forbidden:
        status = "blocked_forbidden_authority_detected"
    elif snapshot.output_snapshot_status == "output_snapshot_deferred_unavailable":
        status = "returned_deferred"
    elif snapshot.output_snapshot_status == "output_snapshot_blocked_invalid_shape":
        status = "returned_fault"
    elif snapshot.output_snapshot_status.startswith("output_snapshot_blocked"):
        status = "returned_blocked"
    else:
        status = "returned_success"
    return RuntimeBoundedHandlerReturnPayloadRecord(
        bounded_handler_return_payload_id=(
            f"runtime_bounded_handler_return_payload:{snapshot.bounded_handler_output_snapshot_id}"
        ),
        schema_version=HANDLER_RETURN_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_output_snapshot_id=snapshot.bounded_handler_output_snapshot_id,
        source_bounded_handler_invocation_id=invocation.bounded_handler_invocation_id,
        closed_loop_stage_name=binding.closed_loop_stage_name,
        event_frame_id=binding.event_frame_id,
        handler_id=binding.handler_id,
        return_status=status,
        return_reason=_return_reason(status),
        return_summary=_return_summary(status, binding.closed_loop_stage_name),
        return_payload={
            "closed_loop_stage_name": binding.closed_loop_stage_name,
            "handler_id": binding.handler_id,
            "output_snapshot_id": snapshot.bounded_handler_output_snapshot_id,
            "output_snapshot_status": snapshot.output_snapshot_status,
            "requires_followup_event": requires_followup_event,
        },
        safe_for_dispatch_return_payload=True,
        safe_for_parent_resume=True,
        requires_parent_resume=True,
        requires_followup_event=requires_followup_event,
        creates_followup_event=False,
        memory_write_performed=memory_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        recursive_learning_created=recursive_learning_created,
        external_execution_created=external_execution_created,
        first_output_created=first_output_created,
        production_behavior_created=production_behavior_created,
        source_trace_refs=binding.source_trace_refs,
    )


def validate_runtime_bounded_handler_return_payload(
    record: RuntimeBoundedHandlerReturnPayloadRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _return_payload(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if not item.safe_for_dispatch_return_payload:
        errors.append("not_safe_for_dispatch_return")
    if not item.safe_for_parent_resume:
        errors.append("not_safe_for_parent_resume")
    if item.creates_followup_event:
        errors.append("creates_followup_event")
    for flag in (
        "memory_write_performed",
        "automatic_learning_approval_created",
        "recursive_learning_created",
        "external_execution_created",
        "first_output_created",
        "production_behavior_created",
    ):
        if getattr(item, flag) and item.return_status != "blocked_forbidden_authority_detected":
            errors.append(f"{flag}_not_blocked")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "bounded_handler_return_payload_id": item.bounded_handler_return_payload_id,
        "return_status": item.return_status,
    }


def build_runtime_bounded_handler_binding_trace(
    *,
    binding_plan: RuntimeBoundedHandlerBindingPlanRecord | dict[str, object],
    fixed_playback_trace: RuntimeFixedClosedLoopPlaybackTrace | dict[str, object] | None,
    stage_bindings: tuple[RuntimeFixedStageHandlerBindingRecord, ...] | list[RuntimeFixedStageHandlerBindingRecord | dict[str, object]],
    handler_invocations: tuple[RuntimeBoundedHandlerInvocationRecord, ...] | list[RuntimeBoundedHandlerInvocationRecord | dict[str, object]],
    output_snapshots: tuple[RuntimeBoundedHandlerOutputSnapshotRecord, ...] | list[RuntimeBoundedHandlerOutputSnapshotRecord | dict[str, object]],
    handler_return_payloads: tuple[RuntimeBoundedHandlerReturnPayloadRecord, ...] | list[RuntimeBoundedHandlerReturnPayloadRecord | dict[str, object]],
    force_missing_playback: bool = False,
    force_missing_binding: bool = False,
    force_invalid_invocation: bool = False,
    force_invalid_output: bool = False,
    force_live_engine_invocation: bool = False,
    force_dynamic_handler_selection: bool = False,
    force_dynamic_child_event: bool = False,
    force_autonomous_scheduler: bool = False,
    force_open_ended_loop: bool = False,
    force_external_execution: bool = False,
    force_memory_write: bool = False,
    force_automatic_learning_approval: bool = False,
    force_recursive_learning: bool = False,
    force_new_learning_artifact: bool = False,
    force_new_sandbox_execution: bool = False,
    force_thought_engine_behavior: bool = False,
    force_first_output: bool = False,
    force_production_behavior: bool = False,
) -> RuntimeBoundedHandlerBindingTrace:
    plan = _plan(binding_plan)
    fixed_trace = _fixed_trace(fixed_playback_trace) if fixed_playback_trace is not None else None
    bindings = tuple(_stage_binding(item) for item in stage_bindings)
    invocations = tuple(_invocation(item) for item in handler_invocations)
    snapshots = tuple(_snapshot(item) for item in output_snapshots)
    returns = tuple(_return_payload(item) for item in handler_return_payloads)
    bound_names = tuple(
        item.closed_loop_stage_name
        for item in bindings
        if item.binding_status in {
            "handler_bound_to_fixed_stage",
            "handler_bound_as_snapshot_only",
        }
    )
    deferred_names = tuple(
        item.closed_loop_stage_name
        for item in bindings
        if item.binding_status == "handler_deferred_unavailable"
    )
    blocked_names = tuple(
        item.closed_loop_stage_name
        for item in bindings
        if item.binding_status.startswith("handler_blocked")
    )
    expected = set(plan.allowed_stage_names)
    covered = set(bound_names) | set(deferred_names)
    missing_playback = force_missing_playback or fixed_trace is None
    missing_binding = force_missing_binding or bool(expected - covered) or not bindings
    invalid_invocation = force_invalid_invocation or any(
        item.invocation_status.startswith("handler_invocation_blocked")
        for item in invocations
    )
    invalid_output = force_invalid_output or any(
        item.output_snapshot_status.startswith("output_snapshot_blocked")
        for item in snapshots
    )
    live = force_live_engine_invocation or any(
        item.live_engine_invocation_created for item in invocations
    )
    dynamic_handler = force_dynamic_handler_selection or any(
        item.dynamic_handler_selection_created for item in invocations
    )
    dynamic_child = force_dynamic_child_event or any(
        item.dynamic_child_event_created for item in invocations
    )
    external = force_external_execution or any(
        item.external_execution_created for item in invocations
    ) or any(item.external_execution_created for item in returns)
    memory = force_memory_write or any(
        item.new_memory_write_performed for item in invocations
    ) or any(item.creates_new_memory_write for item in snapshots) or any(
        item.memory_write_performed for item in returns
    )
    automatic = force_automatic_learning_approval or any(
        item.automatic_learning_approval_created for item in invocations
    ) or any(item.creates_new_learning_approval for item in snapshots) or any(
        item.automatic_learning_approval_created for item in returns
    )
    recursive = force_recursive_learning or any(
        item.recursive_learning_created for item in invocations
    ) or any(item.recursive_learning_created for item in returns)
    learning_artifact = force_new_learning_artifact or any(
        item.new_learning_feedback_candidate_created
        or item.new_concept_candidate_created
        or item.new_reviewed_concept_created
        or item.new_memory_application_data_created
        for item in invocations
    )
    sandbox = force_new_sandbox_execution or any(
        item.new_sandbox_execution_performed for item in invocations
    ) or any(item.creates_new_execution for item in snapshots)
    thought = force_thought_engine_behavior or any(
        item.thought_engine_behavior_created for item in invocations
    )
    first_output = force_first_output or any(
        item.first_output_created for item in invocations
    ) or any(item.creates_first_output for item in snapshots) or any(
        item.first_output_created for item in returns
    )
    production = force_production_behavior or any(
        item.production_behavior_created for item in invocations
    ) or any(item.production_behavior_created for item in returns)
    forbidden = any(
        (
            live,
            dynamic_handler,
            dynamic_child,
            force_autonomous_scheduler,
            force_open_ended_loop,
            external,
            memory,
            automatic,
            recursive,
            learning_artifact,
            sandbox,
            thought,
            first_output,
            production,
        )
    )
    if forbidden:
        status = "bounded_handler_binding_trace_blocked_forbidden_authority_detected"
    elif missing_playback:
        status = "bounded_handler_binding_trace_blocked_missing_playback"
    elif missing_binding:
        status = "bounded_handler_binding_trace_blocked_missing_binding"
    elif invalid_invocation:
        status = "bounded_handler_binding_trace_blocked_invalid_invocation"
    elif invalid_output:
        status = "bounded_handler_binding_trace_blocked_invalid_output"
    elif deferred_names:
        status = "bounded_handler_binding_trace_complete_with_deferred_handlers"
    else:
        status = "bounded_handler_binding_trace_complete"
    return RuntimeBoundedHandlerBindingTrace(
        bounded_handler_binding_trace_id=(
            f"runtime_bounded_handler_binding_trace:{plan.bounded_handler_binding_plan_id}"
        ),
        schema_version=BINDING_TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_binding_plan_id=plan.bounded_handler_binding_plan_id,
        source_fixed_playback_trace_id=(
            fixed_trace.fixed_playback_trace_id if fixed_trace else None
        ),
        stage_binding_ids=tuple(item.fixed_stage_handler_binding_id for item in bindings),
        handler_invocation_ids=tuple(
            item.bounded_handler_invocation_id for item in invocations
        ),
        output_snapshot_ids=tuple(
            item.bounded_handler_output_snapshot_id for item in snapshots
        ),
        handler_return_payload_ids=tuple(
            item.bounded_handler_return_payload_id for item in returns
        ),
        bound_stage_names=bound_names,
        deferred_stage_names=deferred_names,
        blocked_stage_names=blocked_names,
        handler_binding_count=len(bindings),
        handler_invocation_count=len(invocations),
        output_snapshot_count=len(snapshots),
        return_payload_count=len(returns),
        all_allowed_stages_bound_or_deferred=not missing_binding,
        all_invocations_side_effect_free=not invalid_invocation and not forbidden,
        all_outputs_safe_for_return=not invalid_output and all(
            item.output_safe_for_return_payload for item in snapshots
        ),
        all_returns_safe_for_parent_resume=all(
            item.safe_for_parent_resume for item in returns
        ),
        binding_trace_status=status,
        binding_trace_summary=_trace_summary(status),
        live_engine_invocation_created=live,
        dynamic_handler_selection_created=dynamic_handler,
        dynamic_child_event_created=dynamic_child,
        external_execution_created=external,
        memory_layer_write_performed=memory,
        automatic_learning_approval_created=automatic,
        recursive_learning_created=recursive,
        new_learning_artifact_created=learning_artifact,
        new_sandbox_execution_performed=sandbox,
        thought_engine_behavior_created=thought,
        first_output_created=first_output,
        production_behavior_created=production,
        source_trace_refs=plan.source_trace_refs,
    )


def validate_runtime_bounded_handler_binding_trace(
    record: RuntimeBoundedHandlerBindingTrace | dict[str, object],
) -> dict[str, object]:
    try:
        item = _binding_trace(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.binding_trace_status.startswith("bounded_handler_binding_trace_complete"):
        if not item.all_allowed_stages_bound_or_deferred:
            errors.append("missing_binding")
        if not item.all_invocations_side_effect_free:
            errors.append("invalid_invocation")
        if not item.all_outputs_safe_for_return:
            errors.append("invalid_output")
        if not item.all_returns_safe_for_parent_resume:
            errors.append("return_not_safe_for_parent")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "bounded_handler_binding_trace_id": item.bounded_handler_binding_trace_id,
        "binding_trace_status": item.binding_trace_status,
    }


def build_runtime_bounded_handler_binding_audit(
    *,
    binding_plan: RuntimeBoundedHandlerBindingPlanRecord | dict[str, object] | None = None,
    binding_trace: RuntimeBoundedHandlerBindingTrace | dict[str, object] | None = None,
    fixed_playback_audit: RuntimeFixedClosedLoopPlaybackAudit | dict[str, object] | None = None,
    force_invalid_binding_plan: bool = False,
    force_invalid_stage_binding: bool = False,
    force_invalid_handler_invocation: bool = False,
    force_invalid_output_snapshot: bool = False,
    force_autonomous_scheduler: bool = False,
    force_open_ended_loop: bool = False,
) -> RuntimeBoundedHandlerBindingAudit:
    plan = _plan(binding_plan) if binding_plan is not None else None
    trace = _binding_trace(binding_trace) if binding_trace is not None else None
    fixed_audit = (
        _fixed_audit(fixed_playback_audit)
        if fixed_playback_audit is not None
        else None
    )
    reasons = _audit_reasons(
        plan=plan,
        trace=trace,
        fixed_audit=fixed_audit,
        force_invalid_binding_plan=force_invalid_binding_plan,
        force_invalid_stage_binding=force_invalid_stage_binding,
        force_invalid_handler_invocation=force_invalid_handler_invocation,
        force_invalid_output_snapshot=force_invalid_output_snapshot,
        force_autonomous_scheduler=force_autonomous_scheduler,
        force_open_ended_loop=force_open_ended_loop,
    )
    status = _audit_status(trace, reasons)
    return RuntimeBoundedHandlerBindingAudit(
        bounded_handler_binding_audit_id=f"runtime_bounded_handler_binding_audit:{_slug(status)}",
        schema_version=BINDING_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_binding_plan_id=plan.bounded_handler_binding_plan_id if plan else None,
        source_binding_trace_id=trace.bounded_handler_binding_trace_id if trace else None,
        fixed_playback_valid="missing_fixed_playback" not in reasons,
        binding_plan_valid="invalid_binding_plan" not in reasons,
        stage_bindings_valid="invalid_stage_binding" not in reasons,
        handler_invocations_valid="invalid_handler_invocation" not in reasons,
        output_snapshots_valid="invalid_output_snapshot" not in reasons,
        handler_return_payloads_valid="invalid_return_payload" not in reasons,
        binding_trace_valid=trace is not None
        and not trace.binding_trace_status.endswith("forbidden_authority_detected"),
        fixed_sequence_confirmed=True,
        bounded_fixture_confirmed=True,
        side_effect_free_confirmed=True,
        deterministic_confirmed=True,
        snapshot_only_confirmed=True,
        no_live_engine_invocation="live_engine_invocation_detected" not in reasons,
        no_dynamic_handler_selection="dynamic_handler_selection_detected" not in reasons,
        no_dynamic_child_event_scheduling=(
            "dynamic_child_event_scheduling_detected" not in reasons
        ),
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
        no_new_learning_artifacts="new_learning_artifact_detected" not in reasons,
        no_new_sandbox_execution="new_sandbox_execution_detected" not in reasons,
        no_thought_engine_behavior="thought_engine_fake_detected" not in reasons,
        no_first_output="first_output_detected" not in reasons,
        no_production_behavior="production_behavior_detected" not in reasons,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(reasons),
        source_trace_refs=trace.source_trace_refs if trace else tuple(),
    )


def validate_runtime_bounded_handler_binding_audit(
    record: RuntimeBoundedHandlerBindingAudit | dict[str, object],
) -> dict[str, object]:
    try:
        item = _audit(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.audit_status.startswith("passed_"):
        required = (
            item.fixed_playback_valid,
            item.binding_plan_valid,
            item.stage_bindings_valid,
            item.handler_invocations_valid,
            item.output_snapshots_valid,
            item.handler_return_payloads_valid,
            item.binding_trace_valid,
            item.fixed_sequence_confirmed,
            item.bounded_fixture_confirmed,
            item.side_effect_free_confirmed,
            item.deterministic_confirmed,
            item.snapshot_only_confirmed,
            item.no_live_engine_invocation,
            item.no_dynamic_handler_selection,
            item.no_dynamic_child_event_scheduling,
            item.no_external_execution,
            item.no_memory_layer_write,
            item.no_automatic_learning_approval,
            item.no_recursive_learning,
            item.no_new_learning_artifacts,
            item.no_new_sandbox_execution,
            item.no_thought_engine_behavior,
            item.no_first_output,
            item.no_production_behavior,
        )
        if not all(required):
            errors.append("passed_audit_has_failed_boundary")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "bounded_handler_binding_audit_id": item.bounded_handler_binding_audit_id,
        "audit_status": item.audit_status,
    }


def build_runtime_bounded_handler_binding_readiness(
    bounded_handler_binding_audit: RuntimeBoundedHandlerBindingAudit | dict[str, object],
) -> RuntimeBoundedHandlerBindingReadinessRecord:
    audit = _audit(bounded_handler_binding_audit)
    passed = audit.audit_status.startswith("passed_")
    if passed:
        status = "ready_for_handler_bound_fixed_playback_audit_milestone_only"
    elif "detected" in audit.audit_status:
        status = "blocked_forbidden_authority_detected"
    elif audit.source_binding_trace_id is None:
        status = "not_ready_missing_handler_binding_trace"
    else:
        status = "not_ready_boundary_failure"
    return RuntimeBoundedHandlerBindingReadinessRecord(
        bounded_handler_binding_readiness_id=(
            f"runtime_bounded_handler_binding_readiness:{audit.bounded_handler_binding_audit_id}"
        ),
        schema_version=BINDING_READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_bounded_handler_binding_audit_id=audit.bounded_handler_binding_audit_id,
        current_verified_capability=SAFE_CLAIM,
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason=(
            "Seal the milestone that the verified closed loop can be played "
            "over Runtime EventFrames with bounded handler bindings for selected stages."
        ),
        ready_for_handler_bound_fixed_playback_audit_milestone=passed,
        ready_for_runtime_state_persistence_binding=passed,
        ready_for_teacher_observed_playback_cli=passed,
        ready_for_live_runtime_session=False,
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


def validate_runtime_bounded_handler_binding_readiness(
    record: RuntimeBoundedHandlerBindingReadinessRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _readiness(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    for flag in (
        "ready_for_live_runtime_session",
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
        "bounded_handler_binding_readiness_id": item.bounded_handler_binding_readiness_id,
        "readiness_status": item.readiness_status,
    }


def build_demo_sense_handler_binding() -> dict[str, object]:
    return _build_binding_bundle(("sense_observation",))


def build_demo_outcome_evaluation_handler_binding() -> dict[str, object]:
    return _build_binding_bundle(("outcome_evaluation",))


def build_demo_learning_feedback_handler_binding() -> dict[str, object]:
    return _build_binding_bundle(("learning_feedback_candidate",))


def build_demo_working_readback_handler_binding() -> dict[str, object]:
    return _build_binding_bundle(("working_readback_integration",))


def build_demo_selected_handler_binding_trace() -> dict[str, object]:
    return _build_binding_bundle(SELECTED_BINDABLE_STAGES)


def build_demo_deferred_missing_handler_binding() -> dict[str, object]:
    return _build_binding_bundle(("concept_candidate_draft",))


def build_demo_blocked_live_handler_invocation_binding() -> dict[str, object]:
    return _build_binding_bundle(
        SELECTED_BINDABLE_STAGES,
        force_live_engine_invocation=True,
    )


def build_demo_blocked_new_learning_artifact_binding() -> dict[str, object]:
    return _build_binding_bundle(
        SELECTED_BINDABLE_STAGES,
        force_new_learning_artifact=True,
    )


def build_demo_blocked_memory_write_binding() -> dict[str, object]:
    return _build_binding_bundle(SELECTED_BINDABLE_STAGES, force_memory_write=True)


def build_demo_blocked_new_sandbox_execution_binding() -> dict[str, object]:
    return _build_binding_bundle(
        SELECTED_BINDABLE_STAGES,
        force_new_sandbox_execution=True,
    )


def render_bounded_handler_binding_summary_text(
    binding_trace: RuntimeBoundedHandlerBindingTrace | dict[str, object],
    audit: RuntimeBoundedHandlerBindingAudit | dict[str, object] | None = None,
    readiness: RuntimeBoundedHandlerBindingReadinessRecord | dict[str, object] | None = None,
) -> str:
    trace = _binding_trace(binding_trace)
    audit_record = _audit(audit) if audit is not None else None
    readiness_record = _readiness(readiness) if readiness is not None else None
    parts = [
        f"bounded_handler_binding status={trace.binding_trace_status}",
        f"bound={trace.handler_binding_count}",
        f"deferred={len(trace.deferred_stage_names)}",
        f"blocked={len(trace.blocked_stage_names)}",
    ]
    if audit_record is not None:
        parts.append(f"audit={audit_record.audit_status}")
    if readiness_record is not None:
        parts.append(f"readiness={readiness_record.readiness_status}")
    return " ".join(parts)


def render_bounded_handler_binding_stage_table(
    stage_bindings: tuple[RuntimeFixedStageHandlerBindingRecord, ...]
    | list[RuntimeFixedStageHandlerBindingRecord | dict[str, object]],
    handler_invocations: tuple[RuntimeBoundedHandlerInvocationRecord, ...]
    | list[RuntimeBoundedHandlerInvocationRecord | dict[str, object]] = (),
    output_snapshots: tuple[RuntimeBoundedHandlerOutputSnapshotRecord, ...]
    | list[RuntimeBoundedHandlerOutputSnapshotRecord | dict[str, object]] = (),
) -> str:
    bindings = tuple(_stage_binding(item) for item in stage_bindings)
    invocation_by_binding = {
        item.source_fixed_stage_handler_binding_id: item
        for item in tuple(_invocation(item) for item in handler_invocations)
    }
    snapshot_by_binding = {
        item.source_fixed_stage_handler_binding_id: item
        for item in tuple(_snapshot(item) for item in output_snapshots)
    }
    lines = ["stage | handler | binding | invocation | snapshot"]
    for binding in bindings:
        invocation = invocation_by_binding.get(binding.fixed_stage_handler_binding_id)
        snapshot = snapshot_by_binding.get(binding.fixed_stage_handler_binding_id)
        lines.append(
            " | ".join(
                (
                    binding.closed_loop_stage_name,
                    binding.handler_id,
                    binding.binding_status,
                    invocation.invocation_status if invocation else "missing_invocation",
                    snapshot.output_snapshot_status if snapshot else "missing_snapshot",
                )
            )
        )
    return "\n".join(lines)


def _build_binding_bundle(
    stage_names: tuple[str, ...],
    *,
    force_live_engine_invocation: bool = False,
    force_new_learning_artifact: bool = False,
    force_memory_write: bool = False,
    force_new_sandbox_execution: bool = False,
) -> dict[str, object]:
    playback_payload = build_demo_full_fixed_closed_loop_playback()
    fixed_trace = RuntimeFixedClosedLoopPlaybackTrace.from_dict(
        playback_payload["runtime_fixed_closed_loop_playback_trace"]
    )
    fixed_audit = RuntimeFixedClosedLoopPlaybackAudit.from_dict(
        playback_payload["runtime_fixed_closed_loop_playback_audit"]
    )
    playback_steps = [
        RuntimeFixedClosedLoopPlaybackStepRecord.from_dict(item)
        for item in playback_payload["runtime_fixed_closed_loop_playback_steps"]
    ]
    mappings = [
        RuntimeClosedLoopStageToEventFrameMappingRecord.from_dict(item)
        for item in playback_payload["runtime_closed_loop_stage_event_mappings"]
    ]
    step_by_stage = {item.closed_loop_stage_name: item for item in playback_steps}
    mapping_by_stage = {item.closed_loop_stage_name: item for item in mappings}
    plan = build_runtime_bounded_handler_binding_plan(
        fixed_playback_trace=fixed_trace,
        fixed_playback_audit=fixed_audit,
        allowed_stage_names=stage_names,
    )
    stage_bindings: list[RuntimeFixedStageHandlerBindingRecord] = []
    invocations: list[RuntimeBoundedHandlerInvocationRecord] = []
    snapshots: list[RuntimeBoundedHandlerOutputSnapshotRecord] = []
    returns: list[RuntimeBoundedHandlerReturnPayloadRecord] = []
    for index, stage in enumerate(stage_names, start=1):
        step = step_by_stage[stage]
        mapping = mapping_by_stage[stage]
        binding = build_runtime_fixed_stage_handler_binding(
            binding_plan=plan,
            playback_step=step,
            stage_event_mapping=mapping,
        )
        stage_bindings.append(binding)
        invocation = build_runtime_bounded_handler_invocation(
            fixed_stage_handler_binding=binding,
            playback_step=step,
            live_engine_invocation_created=force_live_engine_invocation and index == 1,
            new_reviewed_concept_created=(
                force_new_learning_artifact and index == 1
            ),
            new_memory_write_performed=force_memory_write and index == 1,
            new_sandbox_execution_performed=(
                force_new_sandbox_execution and index == 1
            ),
        )
        invocations.append(invocation)
        snapshot = build_runtime_bounded_handler_output_snapshot(
            bounded_handler_invocation=invocation,
            fixed_stage_handler_binding=binding,
        )
        snapshots.append(snapshot)
        returns.append(
            build_runtime_bounded_handler_return_payload(
                bounded_handler_output_snapshot=snapshot,
                bounded_handler_invocation=invocation,
                fixed_stage_handler_binding=binding,
            )
        )
    trace = build_runtime_bounded_handler_binding_trace(
        binding_plan=plan,
        fixed_playback_trace=fixed_trace,
        stage_bindings=tuple(stage_bindings),
        handler_invocations=tuple(invocations),
        output_snapshots=tuple(snapshots),
        handler_return_payloads=tuple(returns),
    )
    audit = build_runtime_bounded_handler_binding_audit(
        binding_plan=plan,
        binding_trace=trace,
        fixed_playback_audit=fixed_audit,
    )
    readiness = build_runtime_bounded_handler_binding_readiness(audit)
    return {
        **playback_payload,
        "runtime_bounded_handler_binding_plan": plan.to_dict(),
        "runtime_fixed_stage_handler_bindings": [
            item.to_dict() for item in stage_bindings
        ],
        "runtime_bounded_handler_invocations": [
            item.to_dict() for item in invocations
        ],
        "runtime_bounded_handler_output_snapshots": [
            item.to_dict() for item in snapshots
        ],
        "runtime_bounded_handler_return_payloads": [
            item.to_dict() for item in returns
        ],
        "runtime_bounded_handler_binding_trace": trace.to_dict(),
        "runtime_bounded_handler_binding_audit": audit.to_dict(),
        "runtime_bounded_handler_binding_readiness": readiness.to_dict(),
        "rendered_bounded_handler_binding_summary": (
            render_bounded_handler_binding_summary_text(trace, audit, readiness)
        ),
        "rendered_bounded_handler_binding_stage_table": (
            render_bounded_handler_binding_stage_table(
                tuple(stage_bindings),
                tuple(invocations),
                tuple(snapshots),
            )
        ),
    }


def _fixed_fixture_for_binding(
    binding: RuntimeFixedStageHandlerBindingRecord,
    step: RuntimeFixedClosedLoopPlaybackStepRecord,
) -> dict[str, object]:
    return {
        "fixture_kind": "fixed_playback_stage_handler_fixture",
        "closed_loop_stage_name": binding.closed_loop_stage_name,
        "playback_step_id": step.playback_step_id,
        "event_frame_id": binding.event_frame_id,
        "handler_id": binding.handler_id,
        "target_engine_lane": binding.target_engine_lane,
        "record_output_snapshot_only": True,
    }


def _output_payload_for_binding(
    binding: RuntimeFixedStageHandlerBindingRecord,
    invocation: RuntimeBoundedHandlerInvocationRecord,
) -> dict[str, object]:
    return {
        "snapshot_payload_kind": "bounded_handler_stage_output_snapshot",
        "closed_loop_stage_name": binding.closed_loop_stage_name,
        "event_frame_id": binding.event_frame_id,
        "handler_id": binding.handler_id,
        "handler_called": invocation.handler_called,
        "source_fixture_hash": invocation.input_fixture_hash,
        "target_engine_lane": binding.target_engine_lane,
        "record_only_snapshot": True,
        "creates_new_engine_state": False,
        "creates_new_memory_write": False,
        "creates_new_learning_approval": False,
        "creates_new_execution": False,
        "creates_first_output": False,
    }


def _snapshot_shape_valid(
    payload: dict[str, object],
    binding: RuntimeFixedStageHandlerBindingRecord,
) -> bool:
    return (
        payload.get("closed_loop_stage_name") == binding.closed_loop_stage_name
        and payload.get("handler_id") == binding.handler_id
        and payload.get("record_only_snapshot") is True
    )


def _plan_summary(status: str) -> str:
    if status == "binding_plan_created":
        return "Bounded handler binding plan created for fixed playback stages."
    return f"Bounded handler binding plan blocked: {status}."


def _binding_summary(status: str, stage: str) -> str:
    if status in {"handler_bound_to_fixed_stage", "handler_bound_as_snapshot_only"}:
        return f"{stage} bound to a deterministic snapshot handler."
    if status == "handler_deferred_unavailable":
        return f"{stage} handler deferred because no safe builder is available."
    return f"{stage} handler binding blocked: {status}."


def _invocation_summary(status: str, stage: str) -> str:
    if status == "handler_invocation_snapshot_recorded":
        return f"{stage} handler invocation recorded as snapshot-only no-call."
    if status == "handler_invocation_pure_demo_completed":
        return f"{stage} pure demo builder completed inside bounded fixture."
    if status == "handler_invocation_deferred_unavailable":
        return f"{stage} handler invocation deferred."
    return f"{stage} handler invocation blocked: {status}."


def _output_summary(status: str, stage: str) -> str:
    if status in {
        "output_snapshot_recorded",
        "output_snapshot_recorded_from_pure_builder",
    }:
        return f"{stage} bounded handler output snapshot recorded."
    if status == "output_snapshot_deferred_unavailable":
        return f"{stage} output snapshot deferred."
    return f"{stage} output snapshot blocked: {status}."


def _return_reason(status: str) -> str:
    if status == "returned_success":
        return "bounded_handler_snapshot_safe"
    if status == "returned_deferred":
        return "handler_deferred_unavailable"
    if status == "returned_fault":
        return "handler_snapshot_invalid_shape"
    if status == "returned_blocked":
        return "handler_snapshot_blocked"
    if status == "blocked_forbidden_authority_detected":
        return "forbidden_authority_detected"
    return "handler_return_unknown"


def _return_summary(status: str, stage: str) -> str:
    if status == "returned_success":
        return f"{stage} bounded handler return payload is safe for parent resume."
    return f"{stage} bounded handler return payload status: {status}."


def _trace_summary(status: str) -> str:
    if status == "bounded_handler_binding_trace_complete":
        return "Bounded handler binding trace complete for selected fixed playback stages."
    if status == "bounded_handler_binding_trace_complete_with_deferred_handlers":
        return "Bounded handler binding trace complete with deferred handlers."
    return f"Bounded handler binding trace blocked: {status}."


def _readiness_summary(status: str) -> str:
    if status == "ready_for_handler_bound_fixed_playback_audit_milestone_only":
        return "Ready only for handler-bound fixed playback milestone audit."
    return f"Bounded handler binding readiness blocked: {status}."


def _audit_reasons(
    *,
    plan: RuntimeBoundedHandlerBindingPlanRecord | None,
    trace: RuntimeBoundedHandlerBindingTrace | None,
    fixed_audit: RuntimeFixedClosedLoopPlaybackAudit | None,
    force_invalid_binding_plan: bool,
    force_invalid_stage_binding: bool,
    force_invalid_handler_invocation: bool,
    force_invalid_output_snapshot: bool,
    force_autonomous_scheduler: bool,
    force_open_ended_loop: bool,
) -> list[str]:
    reasons: list[str] = []
    if fixed_audit is None or not fixed_audit.audit_status.startswith("passed_"):
        reasons.append("missing_fixed_playback")
    if plan is None or plan.binding_plan_status != "binding_plan_created" or force_invalid_binding_plan:
        reasons.append("invalid_binding_plan")
    if trace is None:
        reasons.append("missing_handler_binding_trace")
        return reasons
    if trace.binding_trace_status == "bounded_handler_binding_trace_blocked_missing_playback":
        reasons.append("missing_fixed_playback")
    if trace.binding_trace_status == "bounded_handler_binding_trace_blocked_missing_binding":
        reasons.append("invalid_stage_binding")
    if force_invalid_stage_binding:
        reasons.append("invalid_stage_binding")
    if trace.binding_trace_status == "bounded_handler_binding_trace_blocked_invalid_invocation":
        reasons.append("invalid_handler_invocation")
    if force_invalid_handler_invocation:
        reasons.append("invalid_handler_invocation")
    if trace.binding_trace_status == "bounded_handler_binding_trace_blocked_invalid_output":
        reasons.append("invalid_output_snapshot")
    if force_invalid_output_snapshot:
        reasons.append("invalid_output_snapshot")
    if trace.live_engine_invocation_created:
        reasons.append("live_engine_invocation_detected")
    if trace.dynamic_handler_selection_created:
        reasons.append("dynamic_handler_selection_detected")
    if trace.dynamic_child_event_created:
        reasons.append("dynamic_child_event_scheduling_detected")
    if force_autonomous_scheduler:
        reasons.append("autonomous_scheduler_detected")
    if force_open_ended_loop:
        reasons.append("open_ended_loop_detected")
    if trace.external_execution_created:
        reasons.append("external_execution_detected")
    if trace.memory_layer_write_performed:
        reasons.append("memory_write_detected")
    if trace.automatic_learning_approval_created:
        reasons.append("automatic_learning_approval_detected")
    if trace.recursive_learning_created:
        reasons.append("recursive_learning_detected")
    if trace.new_learning_artifact_created:
        reasons.append("new_learning_artifact_detected")
    if trace.new_sandbox_execution_performed:
        reasons.append("new_sandbox_execution_detected")
    if trace.thought_engine_behavior_created:
        reasons.append("thought_engine_fake_detected")
    if trace.first_output_created:
        reasons.append("first_output_detected")
    if trace.production_behavior_created:
        reasons.append("production_behavior_detected")
    return list(dict.fromkeys(reasons))


def _audit_status(
    trace: RuntimeBoundedHandlerBindingTrace | None,
    blocked_reasons: list[str],
) -> str:
    priority = (
        ("missing_fixed_playback", "blocked_missing_fixed_playback"),
        ("invalid_binding_plan", "blocked_invalid_binding_plan"),
        ("invalid_stage_binding", "blocked_invalid_stage_binding"),
        ("invalid_handler_invocation", "blocked_invalid_handler_invocation"),
        ("invalid_output_snapshot", "blocked_invalid_output_snapshot"),
        ("live_engine_invocation_detected", "blocked_live_engine_invocation_detected"),
        (
            "dynamic_handler_selection_detected",
            "blocked_dynamic_handler_selection_detected",
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
        ("new_learning_artifact_detected", "blocked_new_learning_artifact_detected"),
        ("recursive_learning_detected", "blocked_recursive_learning_detected"),
        ("new_sandbox_execution_detected", "blocked_new_sandbox_execution_detected"),
        ("thought_engine_fake_detected", "blocked_thought_engine_fake_detected"),
        ("first_output_detected", "blocked_first_output_detected"),
        ("production_behavior_detected", "blocked_production_behavior_detected"),
    )
    for reason, status in priority:
        if reason in blocked_reasons:
            return status
    if trace and trace.binding_trace_status.endswith("with_deferred_handlers"):
        return "passed_bounded_handler_binding_with_deferred_handlers"
    return "passed_bounded_handler_binding_for_fixed_playback"


_INVOCATION_FORBIDDEN_FLAGS = (
    "live_engine_invocation_created",
    "dynamic_handler_selection_created",
    "dynamic_child_event_created",
    "new_learning_feedback_candidate_created",
    "new_concept_candidate_created",
    "new_reviewed_concept_created",
    "new_memory_application_data_created",
    "new_memory_write_performed",
    "new_sandbox_execution_performed",
    "external_execution_created",
    "automatic_learning_approval_created",
    "recursive_learning_created",
    "thought_engine_behavior_created",
    "first_output_created",
    "production_behavior_created",
)


def _plan(
    value: RuntimeBoundedHandlerBindingPlanRecord | dict[str, object],
) -> RuntimeBoundedHandlerBindingPlanRecord:
    return (
        value
        if isinstance(value, RuntimeBoundedHandlerBindingPlanRecord)
        else RuntimeBoundedHandlerBindingPlanRecord.from_dict(value)
    )


def _stage_binding(
    value: RuntimeFixedStageHandlerBindingRecord | dict[str, object],
) -> RuntimeFixedStageHandlerBindingRecord:
    return (
        value
        if isinstance(value, RuntimeFixedStageHandlerBindingRecord)
        else RuntimeFixedStageHandlerBindingRecord.from_dict(value)
    )


def _invocation(
    value: RuntimeBoundedHandlerInvocationRecord | dict[str, object],
) -> RuntimeBoundedHandlerInvocationRecord:
    return (
        value
        if isinstance(value, RuntimeBoundedHandlerInvocationRecord)
        else RuntimeBoundedHandlerInvocationRecord.from_dict(value)
    )


def _snapshot(
    value: RuntimeBoundedHandlerOutputSnapshotRecord | dict[str, object],
) -> RuntimeBoundedHandlerOutputSnapshotRecord:
    return (
        value
        if isinstance(value, RuntimeBoundedHandlerOutputSnapshotRecord)
        else RuntimeBoundedHandlerOutputSnapshotRecord.from_dict(value)
    )


def _return_payload(
    value: RuntimeBoundedHandlerReturnPayloadRecord | dict[str, object],
) -> RuntimeBoundedHandlerReturnPayloadRecord:
    return (
        value
        if isinstance(value, RuntimeBoundedHandlerReturnPayloadRecord)
        else RuntimeBoundedHandlerReturnPayloadRecord.from_dict(value)
    )


def _binding_trace(
    value: RuntimeBoundedHandlerBindingTrace | dict[str, object],
) -> RuntimeBoundedHandlerBindingTrace:
    return (
        value
        if isinstance(value, RuntimeBoundedHandlerBindingTrace)
        else RuntimeBoundedHandlerBindingTrace.from_dict(value)
    )


def _audit(
    value: RuntimeBoundedHandlerBindingAudit | dict[str, object],
) -> RuntimeBoundedHandlerBindingAudit:
    return (
        value
        if isinstance(value, RuntimeBoundedHandlerBindingAudit)
        else RuntimeBoundedHandlerBindingAudit.from_dict(value)
    )


def _readiness(
    value: RuntimeBoundedHandlerBindingReadinessRecord | dict[str, object],
) -> RuntimeBoundedHandlerBindingReadinessRecord:
    return (
        value
        if isinstance(value, RuntimeBoundedHandlerBindingReadinessRecord)
        else RuntimeBoundedHandlerBindingReadinessRecord.from_dict(value)
    )


def _fixed_trace(
    value: RuntimeFixedClosedLoopPlaybackTrace | dict[str, object],
) -> RuntimeFixedClosedLoopPlaybackTrace:
    return (
        value
        if isinstance(value, RuntimeFixedClosedLoopPlaybackTrace)
        else RuntimeFixedClosedLoopPlaybackTrace.from_dict(value)
    )


def _fixed_audit(
    value: RuntimeFixedClosedLoopPlaybackAudit | dict[str, object],
) -> RuntimeFixedClosedLoopPlaybackAudit:
    return (
        value
        if isinstance(value, RuntimeFixedClosedLoopPlaybackAudit)
        else RuntimeFixedClosedLoopPlaybackAudit.from_dict(value)
    )


def _playback_step(
    value: RuntimeFixedClosedLoopPlaybackStepRecord | dict[str, object],
) -> RuntimeFixedClosedLoopPlaybackStepRecord:
    return (
        value
        if isinstance(value, RuntimeFixedClosedLoopPlaybackStepRecord)
        else RuntimeFixedClosedLoopPlaybackStepRecord.from_dict(value)
    )


def _stage_mapping(
    value: RuntimeClosedLoopStageToEventFrameMappingRecord | dict[str, object],
) -> RuntimeClosedLoopStageToEventFrameMappingRecord:
    return (
        value
        if isinstance(value, RuntimeClosedLoopStageToEventFrameMappingRecord)
        else RuntimeClosedLoopStageToEventFrameMappingRecord.from_dict(value)
    )
