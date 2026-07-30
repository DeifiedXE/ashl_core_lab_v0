"""Immutable records for Package 128 structural evidence sufficiency."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain


BASELINE_COMMIT = "8da7facb9195a8ae753789835bb05674cd917e6d"
PACKAGE_128_PASS_STATUS = (
    "passed_structural_evidence_sufficiency_and_observation_stop_policy_v0"
)
PACKAGE_128_BLOCKED_STATUS = (
    "blocked_structural_evidence_sufficiency_and_observation_stop_policy_v0"
)
CONTRACT_KIND = "focused_visual_event_closure_with_post_context"
STOP_ACTION_KIND = "stop_observation"
REQUIRED_LANES = ("screen", "host_state")
MINIMUM_ELAPSED_NS = 1_000_000_000
MINIMUM_COMPLETE_ALIGNMENT_WINDOWS = 3
MINIMUM_POST_EVENT_COVERAGE_NS = 500_000_000
CHECKPOINT_INTERVAL_NS = 250_000_000
MAXIMUM_CHECKPOINT_COUNT = 8
CHILD_HARD_WINDOW_NS = 3_000_000_000


def _record_dict(record: Any) -> dict[str, object]:
    return {
        field.name: plain(getattr(record, field.name))
        for field in fields(record)
    }


def _tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def _normalize_refs(record: Any, *names: str) -> None:
    for name in names:
        object.__setattr__(
            record,
            name,
            _tuple_of_str(getattr(record, name)),
        )


def _require_lineage(*values: str) -> None:
    if not all(str(value) for value in values):
        raise ValueError("Package 128 source lineage is incomplete")


def _reject_stimulus_provenance(*ref_groups: tuple[str, ...]) -> None:
    forbidden = (
        "stimulus",
        "fixture",
        "schedule",
        "expected_stop",
        "expected_focus",
    )
    for ref in (item for group in ref_groups for item in group):
        lowered = str(ref).lower()
        if any(token in lowered for token in forbidden):
            raise ValueError(
                "stimulus ground truth is forbidden from runtime provenance"
            )


@dataclass(frozen=True)
class StructuralEvidenceSufficiencyContract:
    contract_id: str
    schema_version: str
    created_at: str
    runtime_session_id: str
    perception_session_id: str
    observation_window_id: str
    contract_kind: str
    authorization_source: str
    authorized_by: str
    required_lanes: tuple[str, ...]
    required_focus_context_id: str
    minimum_elapsed_ns: int
    minimum_complete_alignment_windows: int
    minimum_post_event_coverage_ns: int
    require_focused_region_evidence: bool
    require_closed_visual_regions: bool
    require_no_open_visual_regions: bool
    require_full_frame_preserved: bool
    checkpoint_interval_ns: int
    maximum_checkpoint_count: int
    hard_deadline_event_time_ns: int
    contract_expires_at_window_end: bool
    semantic_goal: None
    expected_object: None
    expected_label: None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "required_lanes",
            "source_record_refs",
            "source_trace_refs",
        )
        if self.contract_kind != CONTRACT_KIND:
            raise ValueError("Package 128 supports one contract kind")
        if (
            self.authorization_source
            != "explicit_session_configuration"
            or self.authorized_by != "local_operator"
        ):
            raise ValueError("invalid Package 128 contract authorization")
        if self.required_lanes != REQUIRED_LANES:
            raise ValueError("Package 128 contract requires screen and host_state")
        if (
            self.minimum_elapsed_ns != MINIMUM_ELAPSED_NS
            or self.minimum_complete_alignment_windows
            != MINIMUM_COMPLETE_ALIGNMENT_WINDOWS
            or self.minimum_post_event_coverage_ns
            != MINIMUM_POST_EVENT_COVERAGE_NS
            or self.checkpoint_interval_ns != CHECKPOINT_INTERVAL_NS
            or self.maximum_checkpoint_count != MAXIMUM_CHECKPOINT_COUNT
        ):
            raise ValueError("Package 128 v0 contract bounds are fixed")
        if not all(
            (
                self.require_focused_region_evidence,
                self.require_closed_visual_regions,
                self.require_no_open_visual_regions,
                self.require_full_frame_preserved,
                self.contract_expires_at_window_end,
            )
        ):
            raise ValueError("Package 128 contract must preserve every bound")
        if any(
            value is not None
            for value in (
                self.semantic_goal,
                self.expected_object,
                self.expected_label,
            )
        ):
            raise ValueError("Package 128 contract cannot contain semantics")
        if self.hard_deadline_event_time_ns <= 0:
            raise ValueError("contract hard deadline must be positive")
        _require_lineage(
            self.contract_id,
            self.runtime_session_id,
            self.perception_session_id,
            self.observation_window_id,
            self.required_focus_context_id,
        )
        if not self.source_record_refs:
            raise ValueError("Package 128 contract requires source references")
        _reject_stimulus_provenance(
            self.source_record_refs,
            self.source_trace_refs,
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class StructuralEvidenceCheckpoint:
    checkpoint_id: str
    schema_version: str
    created_at: str
    contract_id: str
    runtime_session_id: str
    perception_session_id: str
    observation_window_id: str
    checkpoint_index: int
    evaluated_at_event_time_ns: int
    evaluated_at_processing_time_ns: int
    elapsed_observation_ns: int
    remaining_to_hard_deadline_ns: int
    complete_alignment_window_count: int
    partial_alignment_window_count: int
    focused_region_view_id: str
    full_frame_perception_readable_data_refs: tuple[str, ...]
    focused_region_evidence_record_count: int
    observed_visual_region_refs: tuple[str, ...]
    open_visual_region_refs: tuple[str, ...]
    closed_visual_span_refs: tuple[str, ...]
    latest_visual_closure_event_time_ns: int | None
    post_event_coverage_ns: int
    screen_source_coverage_present: bool
    host_state_source_coverage_present: bool
    required_lane_drop_count: int
    backpressure_fault_count: int
    capture_failure_count: int
    compile_failure_count: int
    semantic_label: None
    uncertainty_score: None
    confidence_score: None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "full_frame_perception_readable_data_refs",
            "observed_visual_region_refs",
            "open_visual_region_refs",
            "closed_visual_span_refs",
            "source_record_refs",
            "source_trace_refs",
        )
        if not 0 <= self.checkpoint_index < MAXIMUM_CHECKPOINT_COUNT:
            raise ValueError("checkpoint index exceeds Package 128 bounds")
        if self.evaluated_at_event_time_ns <= 0:
            raise ValueError("checkpoint event time must be positive")
        if self.evaluated_at_processing_time_ns <= 0:
            raise ValueError("checkpoint processing time must be positive")
        if any(
            value < 0
            for value in (
                self.elapsed_observation_ns,
                self.remaining_to_hard_deadline_ns,
                self.complete_alignment_window_count,
                self.partial_alignment_window_count,
                self.focused_region_evidence_record_count,
                self.post_event_coverage_ns,
                self.required_lane_drop_count,
                self.backpressure_fault_count,
                self.capture_failure_count,
                self.compile_failure_count,
            )
        ):
            raise ValueError("checkpoint counts and durations cannot be negative")
        if any(
            value is not None
            for value in (
                self.semantic_label,
                self.uncertainty_score,
                self.confidence_score,
            )
        ):
            raise ValueError("checkpoint cannot contain semantic or confidence data")
        if self.latest_visual_closure_event_time_ns is None:
            if self.post_event_coverage_ns != 0:
                raise ValueError("post-event coverage requires a closure")
        elif (
            self.latest_visual_closure_event_time_ns
            > self.evaluated_at_event_time_ns
        ):
            raise ValueError("visual closure cannot occur after checkpoint")
        _require_lineage(
            self.checkpoint_id,
            self.contract_id,
            self.runtime_session_id,
            self.perception_session_id,
            self.observation_window_id,
            self.focused_region_view_id,
        )
        if not self.full_frame_perception_readable_data_refs:
            raise ValueError("checkpoint must preserve full-frame readable data")
        if not self.source_record_refs:
            raise ValueError("checkpoint requires actual source references")
        _reject_stimulus_provenance(
            self.source_record_refs,
            self.source_trace_refs,
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class StructuralEvidenceSufficiencyAssessment:
    assessment_id: str
    schema_version: str
    created_at: str
    contract_id: str
    checkpoint_id: str
    assessment_status: str
    minimum_elapsed_met: bool
    minimum_complete_windows_met: bool
    focused_region_evidence_present: bool
    full_frame_preserved: bool
    observed_visual_region_present: bool
    all_visual_regions_closed: bool
    no_open_visual_region_remaining: bool
    post_event_coverage_met: bool
    required_lane_coverage_complete: bool
    transport_integrity_valid: bool
    clock_integrity_valid: bool
    lineage_integrity_valid: bool
    contract_satisfied: bool
    semantic_understanding_claimed: bool
    recognition_claimed: bool
    certainty_claimed: bool
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "failure_reasons",
            "source_record_refs",
            "source_trace_refs",
        )
        allowed = {
            "sufficient",
            "insufficient_continue",
            "inconclusive_at_hard_deadline",
            "blocked_transport_failure",
            "blocked_invalid_lineage",
            "cancelled",
        }
        if self.assessment_status not in allowed:
            raise ValueError("invalid structural assessment status")
        if any(
            (
                self.semantic_understanding_claimed,
                self.recognition_claimed,
                self.certainty_claimed,
            )
        ):
            raise ValueError("structural assessment cannot make semantic claims")
        gates = (
            self.minimum_elapsed_met,
            self.minimum_complete_windows_met,
            self.focused_region_evidence_present,
            self.full_frame_preserved,
            self.observed_visual_region_present,
            self.all_visual_regions_closed,
            self.no_open_visual_region_remaining,
            self.post_event_coverage_met,
            self.required_lane_coverage_complete,
            self.transport_integrity_valid,
            self.clock_integrity_valid,
            self.lineage_integrity_valid,
        )
        if self.contract_satisfied != all(gates):
            raise ValueError("contract_satisfied must equal every structural gate")
        if self.assessment_status == "sufficient":
            if not self.contract_satisfied or self.failure_reasons:
                raise ValueError("sufficient assessment requires every gate")
        elif self.contract_satisfied:
            raise ValueError("non-sufficient assessment cannot satisfy contract")
        _require_lineage(
            self.assessment_id,
            self.contract_id,
            self.checkpoint_id,
        )
        _reject_stimulus_provenance(
            self.source_record_refs,
            self.source_trace_refs,
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class ObservationStopPolicyDecision:
    policy_decision_id: str
    schema_version: str
    created_at: str
    assessment_id: str
    contract_id: str
    decision: str
    contract_authorized: bool
    contract_satisfied: bool
    active_window_identity_valid: bool
    stop_budget_available: bool
    operator_stop_absent: bool
    transport_integrity_valid: bool
    stop_reason: str | None
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(
            self,
            "failure_reasons",
            "source_record_refs",
            "source_trace_refs",
        )
        allowed = {
            "allow_policy_stop",
            "continue_current_window",
            "hard_deadline_inconclusive_stop",
            "operator_stop_precedence",
            "fail_session",
            "cancelled",
        }
        if self.decision not in allowed:
            raise ValueError("invalid observation stop policy decision")
        if self.decision == "allow_policy_stop":
            if not all(
                (
                    self.contract_authorized,
                    self.contract_satisfied,
                    self.active_window_identity_valid,
                    self.stop_budget_available,
                    self.operator_stop_absent,
                    self.transport_integrity_valid,
                )
            ):
                raise ValueError("policy stop requires every authorization gate")
            if (
                self.stop_reason
                != "structural_evidence_contract_satisfied"
                or self.failure_reasons
            ):
                raise ValueError("allowed policy stop reason is fixed")
        _require_lineage(
            self.policy_decision_id,
            self.assessment_id,
            self.contract_id,
        )
        _reject_stimulus_provenance(
            self.source_record_refs,
            self.source_trace_refs,
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class StopObservationInternalAction:
    internal_action_id: str
    schema_version: str
    created_at: str
    action_kind: str
    policy_decision_id: str
    contract_id: str
    observation_window_id: str
    internal_only: bool
    external_side_effect: bool
    stops_current_window_only: bool
    opens_new_window: bool
    extends_deadline: bool
    changes_focus: bool
    selected_action_created: bool
    final_action_created: bool
    direct_command_created: bool
    action_source: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs", "source_trace_refs")
        if (
            self.action_kind != STOP_ACTION_KIND
            or self.action_source
            != "bounded_structural_evidence_sufficiency_policy"
            or not self.internal_only
            or not self.stops_current_window_only
        ):
            raise ValueError("invalid Package 128 internal stop action")
        if any(
            (
                self.external_side_effect,
                self.opens_new_window,
                self.extends_deadline,
                self.changes_focus,
                self.selected_action_created,
                self.final_action_created,
                self.direct_command_created,
            )
        ):
            raise ValueError("stop_observation cannot create other authority")
        _require_lineage(
            self.internal_action_id,
            self.policy_decision_id,
            self.contract_id,
            self.observation_window_id,
        )
        _reject_stimulus_provenance(
            self.source_record_refs,
            self.source_trace_refs,
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class ObservationStopExecution:
    stop_execution_id: str
    schema_version: str
    created_at: str
    internal_action_id: str
    observation_window_id: str
    stop_requested_at_event_time_ns: int
    stop_applied_at_processing_time_ns: int
    original_hard_deadline_event_time_ns: int
    final_observation_end_event_time_ns: int
    stopped_before_hard_deadline: bool
    screen_stop_signal_applied: bool
    host_state_stop_signal_applied: bool
    audio_stop_signal_applied: bool | None
    camera_stop_signal_applied: bool | None
    all_required_lanes_received_stop: bool
    source_sessions_reopened: bool
    alignment_origin_changed: bool
    focus_context_changed: bool
    producers_stopped: bool
    artifacts_finalized: bool
    compilers_drained: bool
    ingress_queues_drained: bool
    alignment_finalized: bool
    execution_status: str
    failure_kind: str | None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs", "source_trace_refs")
        if self.execution_status not in {
            "completed_policy_stop",
            "failed",
            "blocked_duplicate",
        }:
            raise ValueError("invalid observation stop execution status")
        if self.execution_status == "completed_policy_stop":
            if not all(
                (
                    self.stopped_before_hard_deadline,
                    self.screen_stop_signal_applied,
                    self.host_state_stop_signal_applied,
                    self.all_required_lanes_received_stop,
                    self.producers_stopped,
                    self.artifacts_finalized,
                    self.compilers_drained,
                    self.ingress_queues_drained,
                    self.alignment_finalized,
                )
            ):
                raise ValueError("completed stop execution requires all flush gates")
            if any(
                (
                    self.source_sessions_reopened,
                    self.alignment_origin_changed,
                    self.focus_context_changed,
                )
            ):
                raise ValueError("policy stop cannot alter active capture identity")
            if self.failure_kind is not None:
                raise ValueError("completed policy stop cannot contain failure")
        if (
            self.final_observation_end_event_time_ns
            > self.original_hard_deadline_event_time_ns
        ):
            raise ValueError("observation end cannot exceed hard deadline")
        _require_lineage(
            self.stop_execution_id,
            self.internal_action_id,
            self.observation_window_id,
        )
        _reject_stimulus_provenance(
            self.source_record_refs,
            self.source_trace_refs,
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class ObservationCompletionRecord:
    completion_record_id: str
    schema_version: str
    created_at: str
    observation_window_id: str
    contract_id: str
    completion_kind: str
    final_assessment_id: str | None
    policy_decision_id: str
    stop_execution_id: str | None
    final_event_time_ns: int
    original_hard_deadline_event_time_ns: int
    ended_before_hard_deadline: bool
    final_temporal_bundle_id: str
    final_focus_context_id: str
    complete_alignment_window_count: int
    required_lane_drop_count: int
    backpressure_fault_count: int
    capture_failure_count: int
    compile_failure_count: int
    flush_remaining_count: int
    contract_satisfied: bool
    semantic_understanding_created: bool
    recognition_result_created: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs", "source_trace_refs")
        allowed = {
            "policy_sufficient_stop",
            "hard_deadline_inconclusive",
            "operator_interrupted",
            "transport_failed",
            "cancelled",
        }
        if self.completion_kind not in allowed:
            raise ValueError("invalid observation completion kind")
        if any(
            (
                self.semantic_understanding_created,
                self.recognition_result_created,
            )
        ):
            raise ValueError("observation completion cannot create semantics")
        if any(
            value < 0
            for value in (
                self.complete_alignment_window_count,
                self.required_lane_drop_count,
                self.backpressure_fault_count,
                self.capture_failure_count,
                self.compile_failure_count,
                self.flush_remaining_count,
            )
        ):
            raise ValueError("completion counts cannot be negative")
        if self.completion_kind == "policy_sufficient_stop":
            if not (
                self.contract_satisfied
                and self.ended_before_hard_deadline
                and self.final_assessment_id
                and self.stop_execution_id
            ):
                raise ValueError("policy completion requires sufficient early stop")
        _require_lineage(
            self.completion_record_id,
            self.observation_window_id,
            self.contract_id,
            self.policy_decision_id,
            self.final_temporal_bundle_id,
            self.final_focus_context_id,
        )
        _reject_stimulus_provenance(
            self.source_record_refs,
            self.source_trace_refs,
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package128ScoreEquivalenceRecord:
    score_equivalence_record_id: str
    schema_version: str
    created_at: str
    observation_window_id: str
    authoritative_score_before: int
    authoritative_score_after: int
    package_128_score_contribution: int
    package_112_score_changed: bool
    context_read_only: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "source_record_refs", "source_trace_refs")
        if (
            self.package_128_score_contribution != 0
            or self.package_112_score_changed
            or self.authoritative_score_before
            != self.authoritative_score_after
            or not self.context_read_only
        ):
            raise ValueError("Package 128 cannot affect Package 112 scoring")

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package128StructuralEvidenceSufficiencyStopAudit:
    audit_id: str
    schema_version: str
    created_at: str
    baseline_commit: str
    package_127_baseline_verified: bool
    package_126_baseline_verified: bool
    package_125_baseline_verified: bool
    qm0_baseline_verified: bool
    real_focused_child_window_verified: bool
    full_frame_preserved: bool
    focused_region_evidence_verified: bool
    explicit_contract_authorization_verified: bool
    contract_kind_verified: bool
    checkpoint_count: int
    checkpoints_from_actual_runtime_evidence: bool
    final_assessment_sufficient: bool
    all_structural_criteria_verified: bool
    policy_stop_allowed: bool
    stop_observation_action_created: bool
    stop_action_kind_verified: bool
    stopped_before_hard_deadline: bool
    all_required_lanes_stopped: bool
    source_sessions_reopened: bool
    alignment_origin_changed: bool
    focus_context_changed_before_completion: bool
    flush_completed: bool
    focus_released_at_completion: bool
    required_lane_drop_count: int
    backpressure_fault_count: int
    capture_failure_count: int
    compile_failure_count: int
    flush_remaining_count: int
    open_event_control_passed: bool
    insufficient_post_context_control_passed: bool
    no_event_control_passed: bool
    authorization_off_control_passed: bool
    wrong_window_control_passed: bool
    stale_checkpoint_control_passed: bool
    transport_fault_control_passed: bool
    operator_stop_control_passed: bool
    duplicate_stop_control_passed: bool
    stimulus_injection_control_passed: bool
    semantic_injection_control_passed: bool
    incomplete_focus_control_passed: bool
    package_112_score_changed: bool
    memory_write_created: bool
    working_readback_created: bool
    extension_action_created: bool
    reacquisition_action_created: bool
    focus_shift_action_created: bool
    uncertainty_signal_created: bool
    novelty_signal_created: bool
    thought_engine_used: bool
    endocrine_signal_used: bool
    output_created: bool
    external_control_created: bool
    semantic_understanding_claimed: bool
    recognition_claimed: bool
    certainty_claimed: bool
    subjective_time_claimed: bool
    package_129_implemented: bool
    package_130_implemented: bool
    package_131_implemented: bool
    d_laplace_component_used: bool
    dlm_1_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    audit_status: str
    failure_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_refs(self, "failure_reasons", "source_trace_refs")
        if self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("Package 128 baseline commit mismatch")
        if self.audit_status not in {
            PACKAGE_128_PASS_STATUS,
            PACKAGE_128_BLOCKED_STATUS,
        }:
            raise ValueError("invalid Package 128 audit status")
        if (
            self.audit_status == PACKAGE_128_PASS_STATUS
            and self.failure_reasons
        ):
            raise ValueError("passing Package 128 audit cannot contain failures")

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)
