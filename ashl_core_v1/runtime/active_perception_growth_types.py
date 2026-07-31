"""Immutable records for Package 129 active-perception growth proof."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain


EXPERIMENT_ID = "host_internal_active_perception_growth_sequence_v0"
BASELINE_COMMIT = "6feaf9c5122adb63c10616f4acfaa1f93c2b6b62"
PASS_STATUS = "passed_active_perception_real_two_cycle_growth_run_v0"
BLOCKED_STATUS = "blocked_active_perception_real_two_cycle_growth_run_v0"

STAGE_SCHEMA_VERSION = "ashl_package_129_active_perception_stage_v0"
CYCLE_SCHEMA_VERSION = "ashl_package_129_active_perception_growth_cycle_v0"
READBACK_TIMING_SCHEMA_VERSION = (
    "ashl_package_129_active_perception_readback_load_timing_v0"
)
READBACK_INFLUENCE_SCHEMA_VERSION = (
    "ashl_package_129_active_perception_readback_influence_v0"
)
CYCLE_2_PRESERVATION_SCHEMA_VERSION = (
    "ashl_package_129_cycle_2_pending_review_preservation_v0"
)
COMPARISON_SCHEMA_VERSION = (
    "ashl_package_129_active_perception_two_cycle_comparison_v0"
)
AUDIT_SCHEMA_VERSION = "ashl_package_129_active_perception_growth_audit_v0"

STAGE_KINDS = (
    "late_event_extension",
    "focus_selection",
    "fresh_child_reacquisition",
    "structural_sufficiency_stop",
)
STAGE_ACTION_KINDS = {
    "late_event_extension": "extend_observation_window",
    "focus_selection": "shift_internal_perception_focus",
    "fresh_child_reacquisition": "capture_again",
    "structural_sufficiency_stop": "stop_observation",
}
FORBIDDEN_CONTEXT_KEYS = {
    "stimulus_schedule",
    "expected_selected_grid",
    "expected_stop_checkpoint",
    "expected_stop_time",
    "object_identity",
    "object_class",
    "semantic_label",
    "event_meaning",
    "causal_claim",
    "curiosity",
    "uncertainty",
    "recognition",
    "subjective_attention",
}


def _tuple(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def _record(record: Any) -> dict[str, object]:
    return {field.name: plain(getattr(record, field.name)) for field in fields(record)}


def _nonnegative_counts(record: Any, names: tuple[str, ...]) -> None:
    if any(int(getattr(record, name)) < 0 for name in names):
        raise ValueError("transport counts cannot be negative")


@dataclass(frozen=True)
class ActivePerceptionStageRecord:
    stage_record_id: str
    schema_version: str
    created_at: str
    cycle_index: int
    stage_index: int
    stage_kind: str
    runtime_session_id: str
    perception_session_id: str
    observation_window_id: str
    source_evidence_refs: tuple[str, ...]
    policy_decision_refs: tuple[str, ...]
    internal_action_kind: str | None
    internal_action_id: str | None
    execution_record_id: str | None
    stage_status: str
    required_lane_drop_count: int
    backpressure_fault_count: int
    capture_failure_count: int
    compile_failure_count: int
    flush_remaining_count: int
    semantic_label: None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != STAGE_SCHEMA_VERSION:
            raise ValueError("invalid Package 129 stage schema_version")
        if self.cycle_index not in {1, 2}:
            raise ValueError("cycle_index must be 1 or 2")
        if self.stage_index not in {1, 2, 3, 4}:
            raise ValueError("stage_index must be between 1 and 4")
        if self.stage_kind not in STAGE_KINDS:
            raise ValueError("invalid active-perception stage kind")
        if self.internal_action_kind != STAGE_ACTION_KINDS[self.stage_kind]:
            raise ValueError("stage action kind does not match stage kind")
        if not self.internal_action_id or not self.execution_record_id:
            raise ValueError("stage must reference actual action and execution records")
        if self.semantic_label is not None:
            raise ValueError("Package 129 stage semantic_label must be null")
        if self.stage_status != "completed":
            raise ValueError("persisted Package 129 stage must be completed")
        _nonnegative_counts(
            self,
            (
                "required_lane_drop_count",
                "backpressure_fault_count",
                "capture_failure_count",
                "compile_failure_count",
                "flush_remaining_count",
            ),
        )
        for name in (
            "source_evidence_refs",
            "policy_decision_refs",
            "source_record_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple(getattr(self, name)))
        if not self.source_evidence_refs or not self.source_record_refs:
            raise ValueError("stage requires evidence and record lineage")

    def to_dict(self) -> dict[str, object]:
        return _record(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ActivePerceptionStageRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ActivePerceptionGrowthCycleRecord:
    cycle_record_id: str
    schema_version: str
    created_at: str
    experiment_id: str
    experiment_run_id: str
    cycle_index: int
    process_instance_id: str
    operating_system_process_id: int
    stimulus_config_hash: str
    source_plan_hash: str
    stage_record_ids: tuple[str, ...]
    parent_runtime_session_id: str
    parent_perception_session_id: str
    parent_observation_window_id: str
    child_runtime_session_id: str
    child_perception_session_id: str
    child_observation_window_id: str
    bounded_embodied_session_id: str
    final_session_state: str
    pending_teacher_review_id: str | None
    evidence_snapshot_id: str | None
    evidence_identity_hash: str | None
    readback_loaded_before_event: bool
    loaded_readback_refs: tuple[str, ...]
    parent_screen_artifact_refs: tuple[str, ...]
    parent_host_state_artifact_refs: tuple[str, ...]
    child_screen_artifact_refs: tuple[str, ...]
    child_host_state_artifact_refs: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CYCLE_SCHEMA_VERSION:
            raise ValueError("invalid Package 129 cycle schema_version")
        if self.experiment_id != EXPERIMENT_ID:
            raise ValueError("invalid Package 129 experiment_id")
        if self.cycle_index not in {1, 2}:
            raise ValueError("cycle_index must be 1 or 2")
        if self.operating_system_process_id <= 0:
            raise ValueError("operating_system_process_id must be positive")
        if len(self.stage_record_ids) != 4:
            raise ValueError("Package 129 requires exactly four stage records")
        if self.final_session_state != "WAITING_TEACHER_REVIEW":
            raise ValueError("each Package 129 cycle must stop at teacher review")
        if not (
            self.pending_teacher_review_id
            and self.evidence_snapshot_id
            and self.evidence_identity_hash
        ):
            raise ValueError("cycle requires exact pending review evidence identity")
        if self.cycle_index == 1 and (
            self.readback_loaded_before_event or self.loaded_readback_refs
        ):
            raise ValueError("Cycle 1 must not preload working readback")
        if self.cycle_index == 2 and (
            not self.readback_loaded_before_event or not self.loaded_readback_refs
        ):
            raise ValueError("Cycle 2 must preload approved working readback")
        for name in (
            "stage_record_ids",
            "loaded_readback_refs",
            "parent_screen_artifact_refs",
            "parent_host_state_artifact_refs",
            "child_screen_artifact_refs",
            "child_host_state_artifact_refs",
            "source_record_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple(getattr(self, name)))
        if not (
            self.parent_screen_artifact_refs
            and self.parent_host_state_artifact_refs
            and self.child_screen_artifact_refs
            and self.child_host_state_artifact_refs
        ):
            raise ValueError("cycle requires fresh real screen and host-state artifacts")

    def to_dict(self) -> dict[str, object]:
        return _record(self)

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "ActivePerceptionGrowthCycleRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ActivePerceptionReadbackLoadTiming:
    timing_record_id: str
    schema_version: str
    created_at: str
    cycle_2_record_id: str
    working_readback_refs: tuple[str, ...]
    readback_loaded_monotonic_ns: int
    parent_capture_started_monotonic_ns: int
    parent_late_event_candidate_evaluated_monotonic_ns: int
    first_internal_action_scored_monotonic_ns: int
    first_internal_action_executed_monotonic_ns: int
    loaded_before_parent_capture: bool
    loaded_before_candidate_evaluation: bool
    loaded_before_action_scoring: bool
    loaded_before_action_execution: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READBACK_TIMING_SCHEMA_VERSION:
            raise ValueError("invalid Package 129 readback timing schema_version")
        if not self.working_readback_refs:
            raise ValueError("readback timing requires approved readback refs")
        if not (
            self.readback_loaded_monotonic_ns
            <= self.parent_capture_started_monotonic_ns
            <= self.parent_late_event_candidate_evaluated_monotonic_ns
            <= self.first_internal_action_executed_monotonic_ns
        ):
            raise ValueError("readback/capture/action timing order is invalid")
        if not (
            self.readback_loaded_monotonic_ns
            <= self.first_internal_action_scored_monotonic_ns
            <= self.first_internal_action_executed_monotonic_ns
        ):
            raise ValueError("readback must be loaded before scoring and execution")
        if not all(
            (
                self.loaded_before_parent_capture,
                self.loaded_before_candidate_evaluation,
                self.loaded_before_action_scoring,
                self.loaded_before_action_execution,
            )
        ):
            raise ValueError("Package 129 readback must be preloaded")
        object.__setattr__(
            self, "working_readback_refs", _tuple(self.working_readback_refs)
        )
        object.__setattr__(
            self, "source_record_refs", _tuple(self.source_record_refs)
        )
        object.__setattr__(
            self, "source_trace_refs", _tuple(self.source_trace_refs)
        )

    def to_dict(self) -> dict[str, object]:
        return _record(self)

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "ActivePerceptionReadbackLoadTiming":
        return cls(**dict(data))


@dataclass(frozen=True)
class ActivePerceptionReadbackInfluenceRecord:
    influence_record_id: str
    schema_version: str
    created_at: str
    cycle_1_working_readback_id: str
    cycle_2_stage_record_id: str
    cycle_2_internal_action_candidate_id: str
    cycle_2_action_kind: str
    package_112_scorer_id: str
    package_112_scorer_version: str
    score_without_readback: float
    score_with_readback: float
    readback_contribution: float
    influencing_readback_refs: tuple[str, ...]
    matching_evidence_refs: tuple[str, ...]
    actual_runtime_hot_path: bool
    hard_policy_gate_bypassed: bool
    hard_coded_experiment_match_used: bool
    stimulus_ground_truth_used: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != READBACK_INFLUENCE_SCHEMA_VERSION:
            raise ValueError("invalid Package 129 influence schema_version")
        if self.cycle_2_action_kind != "extend_observation_window":
            raise ValueError("Package 129 v0 influences the extension candidate")
        if self.readback_contribution <= 0:
            raise ValueError("Package 129 requires a nonzero readback contribution")
        if abs(
            (self.score_with_readback - self.score_without_readback)
            - self.readback_contribution
        ) > 1e-9:
            raise ValueError("readback score arithmetic mismatch")
        if not self.actual_runtime_hot_path:
            raise ValueError("readback influence must occur in the actual runtime hot path")
        if (
            self.hard_policy_gate_bypassed
            or self.hard_coded_experiment_match_used
            or self.stimulus_ground_truth_used
        ):
            raise ValueError("readback influence cannot bypass policy or use fixture truth")
        for name in (
            "influencing_readback_refs",
            "matching_evidence_refs",
            "source_record_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple(getattr(self, name)))
        if not self.influencing_readback_refs or not self.matching_evidence_refs:
            raise ValueError("readback influence requires provenance")

    def to_dict(self) -> dict[str, object]:
        return _record(self)

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "ActivePerceptionReadbackInfluenceRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ActivePerceptionCycle2PendingReviewPreservation:
    preservation_record_id: str
    schema_version: str
    created_at: str
    cycle_2_session_id: str
    pending_review_id: str
    evidence_identity_hash: str
    preservation_reason: str
    teacher_decision_count: int
    reviewed_memory_commit_count: int
    preserved_unresolved: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != CYCLE_2_PRESERVATION_SCHEMA_VERSION:
            raise ValueError("invalid Cycle 2 preservation schema_version")
        if (
            self.preservation_reason
            != "cycle_2_teacher_gate_is_growth_evidence_not_required_second_commit"
        ):
            raise ValueError("invalid Cycle 2 preservation reason")
        if (
            self.teacher_decision_count != 0
            or self.reviewed_memory_commit_count != 0
            or not self.preserved_unresolved
        ):
            raise ValueError("Cycle 2 review must remain unresolved and uncommitted")
        object.__setattr__(
            self, "source_record_refs", _tuple(self.source_record_refs)
        )
        object.__setattr__(
            self, "source_trace_refs", _tuple(self.source_trace_refs)
        )

    def to_dict(self) -> dict[str, object]:
        return _record(self)

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "ActivePerceptionCycle2PendingReviewPreservation":
        return cls(**dict(data))


@dataclass(frozen=True)
class ActivePerceptionTwoCycleComparison:
    comparison_id: str
    schema_version: str
    created_at: str
    experiment_id: str
    cycle_1_record_id: str
    cycle_2_record_id: str
    cycle_1_process_instance_id: str
    cycle_2_process_instance_id: str
    process_instances_distinct: bool
    operating_system_processes_distinct: bool
    parent_sessions_distinct: bool
    child_sessions_distinct: bool
    raw_artifacts_distinct: bool
    stimulus_config_hash_equal: bool
    source_plan_hash_equal: bool
    cycle_1_approved_commit_present: bool
    cycle_2_readback_loaded_before_event: bool
    cycle_2_readback_influence_record_id: str
    cycle_2_readback_contribution_nonzero: bool
    cycle_2_completed_active_perception_sequence: bool
    cycle_2_final_state: str
    policy_gate_bypass_detected: bool
    semantic_recognition_created: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != COMPARISON_SCHEMA_VERSION:
            raise ValueError("invalid Package 129 comparison schema_version")
        if self.experiment_id != EXPERIMENT_ID:
            raise ValueError("invalid Package 129 comparison experiment_id")
        if not all(
            (
                self.process_instances_distinct,
                self.operating_system_processes_distinct,
                self.parent_sessions_distinct,
                self.child_sessions_distinct,
                self.raw_artifacts_distinct,
                self.stimulus_config_hash_equal,
                self.source_plan_hash_equal,
                self.cycle_1_approved_commit_present,
                self.cycle_2_readback_loaded_before_event,
                self.cycle_2_readback_contribution_nonzero,
                self.cycle_2_completed_active_perception_sequence,
            )
        ):
            raise ValueError("two-cycle growth comparison is incomplete")
        if self.cycle_2_final_state != "WAITING_TEACHER_REVIEW":
            raise ValueError("Cycle 2 must remain waiting for teacher review")
        if self.policy_gate_bypass_detected or self.semantic_recognition_created:
            raise ValueError("growth comparison cannot bypass policy or claim recognition")
        if any(
            (
                self.llm_runtime_calls,
                self.codex_runtime_calls,
                self.network_runtime_calls,
            )
        ):
            raise ValueError("Package 129 runtime cannot call models or network")
        object.__setattr__(
            self, "source_record_refs", _tuple(self.source_record_refs)
        )
        object.__setattr__(
            self, "source_trace_refs", _tuple(self.source_trace_refs)
        )

    def to_dict(self) -> dict[str, object]:
        return _record(self)

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "ActivePerceptionTwoCycleComparison":
        return cls(**dict(data))


@dataclass(frozen=True)
class Package129ActivePerceptionGrowthAudit:
    audit_id: str
    schema_version: str
    created_at: str
    baseline_commit: str
    package_128_baseline_verified: bool
    package_127_baseline_verified: bool
    package_126_baseline_verified: bool
    package_125_baseline_verified: bool
    qm0_baseline_verified: bool
    new_perception_action_kind_created: bool
    new_sensor_source_created: bool
    new_primitive_compiler_created: bool
    new_focus_mode_created: bool
    new_sufficiency_contract_kind_created: bool
    cycle_1_real_capture_verified: bool
    cycle_1_extension_verified: bool
    cycle_1_focus_shift_verified: bool
    cycle_1_capture_again_verified: bool
    cycle_1_stop_observation_verified: bool
    cycle_1_transport_integrity_verified: bool
    cycle_1_waiting_teacher_review_verified: bool
    cycle_1_exact_approval_verified: bool
    cycle_1_reviewed_memory_chain_verified: bool
    cycle_1_working_readback_verified: bool
    cycle_process_separation_verified: bool
    cycle_2_fresh_capture_verified: bool
    cycle_2_readback_preloaded_verified: bool
    cycle_2_readback_influence_verified: bool
    cycle_2_readback_contribution: float
    cycle_2_actual_runtime_hot_path_verified: bool
    cycle_2_policy_gate_bypass_detected: bool
    cycle_2_extension_verified: bool
    cycle_2_focus_shift_verified: bool
    cycle_2_capture_again_verified: bool
    cycle_2_stop_observation_verified: bool
    cycle_2_transport_integrity_verified: bool
    cycle_2_waiting_teacher_review_verified: bool
    cycle_2_auto_approval_detected: bool
    cycle_2_additional_memory_commit_detected: bool
    empty_readback_control_passed: bool
    mismatched_context_control_passed: bool
    authorization_off_control_passed: bool
    transport_fault_control_passed: bool
    wrong_readback_lineage_control_passed: bool
    readback_loaded_late_control_passed: bool
    same_process_control_passed: bool
    reused_artifact_control_passed: bool
    stimulus_match_control_passed: bool
    auto_approval_control_passed: bool
    fabricated_sequence_control_passed: bool
    semantic_injection_control_passed: bool
    stimulus_ground_truth_used_for_runtime_decision: bool
    hard_coded_experiment_match_used: bool
    semantic_vision_created: bool
    object_recognition_created: bool
    auditory_concept_created: bool
    auditory_prediction_created: bool
    uncertainty_signal_created: bool
    novelty_signal_created: bool
    curiosity_signal_created: bool
    thought_engine_used: bool
    endocrine_signal_used: bool
    qingyin_output_created: bool
    external_control_created: bool
    package_130_implemented: bool
    package_131_implemented: bool
    package_132_milestone_claimed: bool
    d_laplace_component_used: bool
    dlm_1_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    audit_status: str
    failure_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != AUDIT_SCHEMA_VERSION:
            raise ValueError("invalid Package 129 audit schema_version")
        if self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("invalid Package 129 baseline commit")
        if self.audit_status not in {PASS_STATUS, BLOCKED_STATUS}:
            raise ValueError("invalid Package 129 audit status")
        object.__setattr__(self, "failure_reasons", _tuple(self.failure_reasons))
        object.__setattr__(
            self, "source_trace_refs", _tuple(self.source_trace_refs)
        )

    def to_dict(self) -> dict[str, object]:
        return _record(self)

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "Package129ActivePerceptionGrowthAudit":
        return cls(**dict(data))
