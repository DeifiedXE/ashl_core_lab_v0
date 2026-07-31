"""Package 125 bounded observation-window extension record types."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain


OBSERVATION_WINDOW_STATE_SCHEMA_VERSION = "ashl_observation_window_state_v0"
OBSERVATION_WINDOW_AUTHORIZATION_SCHEMA_VERSION = "ashl_observation_window_extension_authorization_v0"
TEMPORAL_TAIL_EVIDENCE_SCHEMA_VERSION = "ashl_temporal_tail_evidence_v0"
OPEN_TEMPORAL_REGION_SCHEMA_VERSION = "ashl_open_temporal_region_observation_v0"
TEMPORAL_REGION_CLOSURE_LINK_SCHEMA_VERSION = "ashl_temporal_region_closure_link_v0"
OBSERVATION_EXTENSION_CANDIDATE_SCHEMA_VERSION = "ashl_observation_window_extension_candidate_v0"
OBSERVATION_EXTENSION_POLICY_SCHEMA_VERSION = "ashl_observation_extension_policy_decision_v0"
OBSERVATION_EXTENSION_INTERNAL_ACTION_SCHEMA_VERSION = "ashl_bounded_observation_extension_internal_action_v0"
DEADLINE_EXTENSION_RESULT_SCHEMA_VERSION = "ashl_deadline_extension_result_v0"
OBSERVATION_EXTENSION_EXECUTION_SCHEMA_VERSION = "ashl_observation_window_extension_execution_v0"
OBSERVATION_EXTENSION_CANCELLATION_SCHEMA_VERSION = "ashl_observation_extension_cancellation_v0"
OBSERVATION_EXTENSION_OUTCOME_SCHEMA_VERSION = "ashl_observation_window_extension_outcome_v0"
OBSERVATION_EXTENSION_COMPARISON_SCHEMA_VERSION = "ashl_observation_extension_effect_comparison_v0"
PACKAGE_125_AUDIT_SCHEMA_VERSION = "ashl_package_125_bounded_observation_extension_audit_v0"
ACTIVE_CAPTURE_SESSION_IDENTITY_SCHEMA_VERSION = "ashl_active_capture_session_identity_v0"
OPERATOR_EVENT_DELIVERY_FAILURE_SCHEMA_VERSION = "ashl_observation_operator_event_delivery_failure_v0"
PACKAGE_112_SCORE_EQUIVALENCE_SCHEMA_VERSION = "ashl_package_125_package_112_score_equivalence_v0"
PACKAGE_125_STIMULUS_AUDIT_MANIFEST_SCHEMA_VERSION = "ashl_package_125_stimulus_audit_manifest_v0"

PACKAGE_125_STORE_SCHEMA_NAME = "ashl_package_125_observation_extension_store"
PACKAGE_125_STORE_SCHEMA_VERSION = "v0"

REQUIRED_LANES = ("screen", "microphone", "host_state")
DEFAULT_BASE_OBSERVATION_NS = 5_000_000_000
DEFAULT_TAIL_GUARD_NS = 750_000_000
DEFAULT_EXTENSION_NS = 1_500_000_000
DEFAULT_HARD_SESSION_NS = 7_000_000_000
DEFAULT_FINAL_DEADLINE_NS = DEFAULT_BASE_OBSERVATION_NS + DEFAULT_EXTENSION_NS

OBSERVATION_WINDOW_STATUSES = (
    "initializing",
    "observing_base_window",
    "extension_candidate_pending",
    "observing_extended_window",
    "operator_interrupted",
    "completed",
    "failed",
)
ALLOWED_EXTENSION_REASON_CODES = (
    "visual_region_open_near_window_boundary",
    "audio_region_open_near_window_boundary",
    "recent_visual_onset_without_observed_offset",
    "recent_audio_onset_without_observed_offset",
    "insufficient_post_change_source_coverage",
)
FORBIDDEN_EXTENSION_REASON_CODES = {
    "uncertain",
    "interesting",
    "novel",
    "important",
    "curious",
    "waiting_for_more",
    "probably_meaningful",
    "teacher_might_care",
    "memory_match",
    "high_reward",
}
CANDIDATE_STATUSES = ("proposed", "expired", "blocked", "authorized", "executed")
POLICY_DECISIONS = ("allow", "block", "expired", "cancelled")
EXECUTION_STATUSES = ("applied", "blocked", "stale_deadline", "exceeds_hard_deadline", "operator_interrupted", "failed")
OUTCOME_STATUSES = (
    "event_closure_observed",
    "additional_context_observed",
    "event_remained_open_at_hard_deadline",
    "operator_interrupted",
    "transport_failed",
    "no_material_extension_effect",
)
PACKAGE_125_PASS_STATUS = "passed_bounded_observation_window_extension_internal_action_v0"


def tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def record_dict(record: Any) -> dict[str, object]:
    return {field.name: plain(getattr(record, field.name)) for field in fields(record)}


def _require_schema(actual: str, expected: str) -> None:
    if actual != expected:
        raise ValueError(f"invalid schema_version: {actual}")


def _require_null(name: str, value: Any) -> None:
    if value is not None:
        raise ValueError(f"{name} must be null")


@dataclass(frozen=True)
class ObservationWindowState:
    observation_window_id: str
    observation_window_state_id: str
    schema_version: str
    created_at: str
    runtime_session_id: str
    perception_session_id: str
    participating_lanes: tuple[str, ...]
    required_lanes: tuple[str, ...]
    base_start_event_time_ns: int
    base_deadline_event_time_ns: int
    current_deadline_event_time_ns: int
    hard_deadline_event_time_ns: int
    extension_count: int
    total_extension_ns: int
    window_status: str
    operator_stop_requested: bool
    operator_pause_requested: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str
    capture_mode: str
    active_capture_identity_id: str
    alignment_origin_monotonic_ns: int
    clock_domain_ids: tuple[str, ...]
    transport_flush_record_id: str | None

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, OBSERVATION_WINDOW_STATE_SCHEMA_VERSION)
        if self.window_status not in OBSERVATION_WINDOW_STATUSES:
            raise ValueError("invalid observation window status")
        if self.base_deadline_event_time_ns <= self.base_start_event_time_ns:
            raise ValueError("base deadline must be after base start")
        if self.current_deadline_event_time_ns < self.base_deadline_event_time_ns:
            raise ValueError("current deadline cannot precede base deadline")
        if self.hard_deadline_event_time_ns < self.current_deadline_event_time_ns:
            raise ValueError("hard deadline cannot precede current deadline")
        if self.extension_count < 0 or self.total_extension_ns < 0:
            raise ValueError("extension counters cannot be negative")
        if not self.observation_window_state_id:
            raise ValueError("observation_window_state_id is required")
        if self.capture_mode not in {"synthetic_test", "real_active_capture"}:
            raise ValueError("invalid Package 125 capture_mode")
        if self.alignment_origin_monotonic_ns < 0:
            raise ValueError("alignment origin cannot be negative")
        object.__setattr__(self, "participating_lanes", tuple_of_str(self.participating_lanes))
        object.__setattr__(self, "required_lanes", tuple_of_str(self.required_lanes))
        object.__setattr__(self, "clock_domain_ids", tuple_of_str(self.clock_domain_ids))
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class ObservationWindowExtensionAuthorization:
    authorization_id: str
    schema_version: str
    created_at: str
    runtime_session_id: str
    perception_session_id: str
    authorization_source: str
    authorized_by: str
    bounded_extension_allowed: bool
    maximum_extension_count: int
    maximum_single_extension_ns: int
    maximum_total_extension_ns: int
    hard_session_duration_ns: int
    allowed_reason_codes: tuple[str, ...]
    expires_at_session_end: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, OBSERVATION_WINDOW_AUTHORIZATION_SCHEMA_VERSION)
        if self.authorization_source != "explicit_session_configuration":
            raise ValueError("authorization_source must be explicit_session_configuration")
        if self.authorized_by != "local_operator":
            raise ValueError("authorized_by must be local_operator")
        if self.maximum_extension_count < 0:
            raise ValueError("maximum_extension_count cannot be negative")
        if self.maximum_single_extension_ns < 0 or self.maximum_total_extension_ns < 0 or self.hard_session_duration_ns <= 0:
            raise ValueError("invalid extension budget")
        allowed = tuple_of_str(self.allowed_reason_codes)
        invalid = set(allowed) - set(ALLOWED_EXTENSION_REASON_CODES)
        if invalid:
            raise ValueError(f"invalid allowed reason codes: {sorted(invalid)}")
        if not self.expires_at_session_end:
            raise ValueError("Package 125 authorization expires at session end")
        object.__setattr__(self, "allowed_reason_codes", allowed)
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class TemporalTailEvidenceRecord:
    temporal_tail_evidence_id: str
    schema_version: str
    created_at: str
    observation_window_id: str
    temporal_bundle_or_context_id: str
    evaluated_at_event_time_ns: int
    current_deadline_event_time_ns: int
    remaining_window_ns: int
    open_visual_region_refs: tuple[str, ...]
    open_audio_region_refs: tuple[str, ...]
    recent_onset_anchor_refs: tuple[str, ...]
    continuous_source_coverage: bool
    required_lane_delivery_complete: bool
    capture_failure_count: int
    compile_failure_count: int
    dropped_required_record_count: int
    backpressure_fault_count: int
    semantic_label: None
    structural_tail_only: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    runtime_session_id: str
    perception_session_id: str
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str
    active_capture_identity_id: str

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, TEMPORAL_TAIL_EVIDENCE_SCHEMA_VERSION)
        _require_null("semantic_label", self.semantic_label)
        if not self.structural_tail_only:
            raise ValueError("temporal tail evidence must be structural_tail_only")
        if self.remaining_window_ns < 0:
            raise ValueError("remaining_window_ns cannot be negative")
        for name in (
            "open_visual_region_refs",
            "open_audio_region_refs",
            "recent_onset_anchor_refs",
            "source_record_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, tuple_of_str(getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class OpenTemporalRegionObservation:
    open_region_observation_id: str
    schema_version: str
    created_at: str
    source_lane: str
    region_kind: str
    start_anchor_id: str
    latest_observed_anchor_id: str
    start_event_time_ns: int
    latest_observed_event_time_ns: int
    observed_offset_present: bool
    open_at_current_boundary: bool
    provisional_only: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    observation_window_id: str
    runtime_session_id: str
    perception_session_id: str
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, OPEN_TEMPORAL_REGION_SCHEMA_VERSION)
        if self.source_lane not in {"screen", "microphone"}:
            raise ValueError("open regions are limited to screen or microphone in Package 125")
        if self.region_kind not in {"observed_change_region", "observed_energy_region"}:
            raise ValueError("invalid open region kind")
        if self.latest_observed_event_time_ns < self.start_event_time_ns:
            raise ValueError("latest observed event time cannot precede start")
        if not self.provisional_only:
            raise ValueError("open region observations are provisional only")
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class TemporalRegionClosureLink:
    closure_link_id: str
    created_at: str
    open_region_observation_id: str
    finalized_temporal_span_id: str
    closure_anchor_id: str
    closure_event_time_ns: int
    source_trace_refs: tuple[str, ...]
    observation_window_id: str
    runtime_session_id: str
    perception_session_id: str
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class ObservationWindowExtensionCandidate:
    extension_candidate_id: str
    schema_version: str
    created_at: str
    observation_window_id: str
    runtime_session_id: str
    perception_session_id: str
    requested_extension_ns: int
    reason_codes: tuple[str, ...]
    temporal_tail_evidence_id: str
    source_temporal_refs: tuple[str, ...]
    source_lane_refs: tuple[str, ...]
    semantic_label: None
    thought_engine_used: bool
    memory_used: bool
    endocrine_signal_used: bool
    stimulus_ground_truth_used: bool
    candidate_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str
    active_capture_identity_id: str

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, OBSERVATION_EXTENSION_CANDIDATE_SCHEMA_VERSION)
        _require_null("semantic_label", self.semantic_label)
        reasons = tuple_of_str(self.reason_codes)
        if not reasons:
            raise ValueError("extension candidate requires at least one structural reason")
        invalid = set(reasons) - set(ALLOWED_EXTENSION_REASON_CODES)
        forbidden = set(reasons).intersection(FORBIDDEN_EXTENSION_REASON_CODES)
        if invalid or forbidden:
            raise ValueError("invalid extension candidate reason code")
        if any((self.thought_engine_used, self.memory_used, self.endocrine_signal_used, self.stimulus_ground_truth_used)):
            raise ValueError("extension candidate must not use Thought Engine, memory, endocrine, or stimulus ground truth")
        if self.candidate_status not in CANDIDATE_STATUSES:
            raise ValueError("invalid candidate status")
        object.__setattr__(self, "reason_codes", reasons)
        object.__setattr__(self, "source_temporal_refs", tuple_of_str(self.source_temporal_refs))
        object.__setattr__(self, "source_lane_refs", tuple_of_str(self.source_lane_refs))
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class ObservationExtensionPolicyDecision:
    extension_policy_decision_id: str
    schema_version: str
    created_at: str
    extension_candidate_id: str
    authorization_id: str
    decision: str
    authorization_valid: bool
    reason_allowed: bool
    budget_available: bool
    transport_integrity_valid: bool
    same_sensor_configuration: bool
    operator_interrupt_absent: bool
    requested_extension_ns: int
    granted_extension_ns: int
    failure_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    observation_window_id: str
    runtime_session_id: str
    perception_session_id: str
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, OBSERVATION_EXTENSION_POLICY_SCHEMA_VERSION)
        if self.decision not in POLICY_DECISIONS:
            raise ValueError("invalid policy decision")
        if self.decision == "allow" and self.granted_extension_ns <= 0:
            raise ValueError("allow decision requires a positive granted extension")
        if self.decision != "allow" and self.granted_extension_ns != 0:
            raise ValueError("blocked policy decisions cannot grant extension")
        object.__setattr__(self, "failure_reasons", tuple_of_str(self.failure_reasons))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class BoundedObservationExtensionInternalAction:
    internal_action_id: str
    schema_version: str
    created_at: str
    action_kind: str
    extension_policy_decision_id: str
    observation_window_id: str
    requested_extension_ns: int
    granted_extension_ns: int
    internal_only: bool
    external_side_effect: bool
    reversible_before_execution: bool
    raw_history_rewrite_allowed: bool
    action_selection_source: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    runtime_session_id: str
    perception_session_id: str
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, OBSERVATION_EXTENSION_INTERNAL_ACTION_SCHEMA_VERSION)
        if self.action_kind != "extend_observation_window":
            raise ValueError("Package 125 internal action kind must be extend_observation_window")
        if not self.internal_only or self.external_side_effect:
            raise ValueError("observation extension action must be internal-only with no external side effect")
        if not self.reversible_before_execution or self.raw_history_rewrite_allowed:
            raise ValueError("invalid observation extension action reversibility/raw-history flags")
        if self.action_selection_source != "bounded_structural_temporal_policy":
            raise ValueError("invalid observation extension action selection source")
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class DeadlineExtensionResult:
    deadline_extension_result_id: str
    schema_version: str
    created_at: str
    previous_deadline_ns: int
    requested_extension_ns: int
    requested_new_deadline_ns: int
    applied_new_deadline_ns: int
    hard_deadline_ns: int
    extension_count_after: int
    total_extension_ns_after: int
    policy_decision_id: str
    atomic_compare_and_set_succeeded: bool
    all_lane_deadlines_updated: bool
    stop_requested: bool
    extension_status: str
    failure_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, DEADLINE_EXTENSION_RESULT_SCHEMA_VERSION)
        if self.extension_status not in EXECUTION_STATUSES:
            raise ValueError("invalid deadline extension status")
        object.__setattr__(self, "failure_reasons", tuple_of_str(self.failure_reasons))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class ObservationWindowExtensionExecutionRecord:
    extension_execution_id: str
    schema_version: str
    created_at: str
    internal_action_id: str
    observation_window_id: str
    previous_deadline_ns: int
    requested_new_deadline_ns: int
    applied_new_deadline_ns: int
    screen_deadline_updated: bool
    audio_deadline_updated: bool
    host_state_deadline_updated: bool
    camera_deadline_updated: bool | None
    same_capture_sessions_preserved: bool
    sources_reopened: bool
    execution_status: str
    failure_kind: str | None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    runtime_session_id: str
    perception_session_id: str
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str
    capture_identity_before_id: str
    capture_identity_after_id: str
    alignment_origin_before_ns: int
    alignment_origin_after_ns: int
    participating_lanes: tuple[str, ...] = (
        "screen",
        "microphone",
        "host_state",
    )

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, OBSERVATION_EXTENSION_EXECUTION_SCHEMA_VERSION)
        if self.execution_status not in EXECUTION_STATUSES:
            raise ValueError("invalid execution status")
        object.__setattr__(
            self,
            "participating_lanes",
            tuple_of_str(self.participating_lanes),
        )
        if not self.participating_lanes or not set(
            self.participating_lanes
        ).issubset({"screen", "microphone", "host_state", "camera"}):
            raise ValueError("invalid Package 125 participating lanes")
        if self.execution_status == "applied":
            lane_updates = {
                "screen": self.screen_deadline_updated,
                "microphone": self.audio_deadline_updated,
                "host_state": self.host_state_deadline_updated,
                "camera": self.camera_deadline_updated,
            }
            if not all(
                lane_updates[lane] is True
                for lane in self.participating_lanes
            ):
                raise ValueError(
                    "successful Package 125 extension must update all participating lanes"
                )
            if not self.same_capture_sessions_preserved or self.sources_reopened:
                raise ValueError("successful Package 125 extension must preserve same sessions and reopen no source")
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class ObservationExtensionCancellationRecord:
    cancellation_id: str
    schema_version: str
    created_at: str
    target_extension_candidate_id: str
    target_internal_action_id: str | None
    requested_by: str
    reason: str
    cancellation_succeeded: bool
    deadline_already_extended: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, OBSERVATION_EXTENSION_CANCELLATION_SCHEMA_VERSION)
        if self.requested_by != "local_operator":
            raise ValueError("Package 125 cancellation must be requested by local_operator")
        if self.cancellation_succeeded and self.deadline_already_extended:
            raise ValueError("executed extension cannot be erased by cancellation")
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class ObservationWindowExtensionOutcome:
    extension_outcome_id: str
    schema_version: str
    created_at: str
    extension_execution_id: str
    observation_window_id: str
    additional_observation_ns: int
    open_visual_regions_before: int
    open_audio_regions_before: int
    finalized_visual_spans_after: int
    finalized_audio_spans_after: int
    post_event_context_ns: int
    required_lane_drops: int
    transport_faults: int
    capture_failures: int
    compile_failures: int
    extension_effect_status: str
    semantic_interpretation_created: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    runtime_session_id: str
    perception_session_id: str
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, OBSERVATION_EXTENSION_OUTCOME_SCHEMA_VERSION)
        if self.extension_effect_status not in OUTCOME_STATUSES:
            raise ValueError("invalid extension effect status")
        if self.semantic_interpretation_created:
            raise ValueError("Package 125 cannot create semantic interpretation")
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class ObservationExtensionEffectComparison:
    comparison_id: str
    schema_version: str
    created_at: str
    observation_window_id: str
    base_boundary_event_time_ns: int
    final_boundary_event_time_ns: int
    base_tail_evidence_id: str
    final_temporal_bundle_id: str
    base_open_region_count: int
    final_open_region_count: int
    newly_observed_closure_count: int
    newly_observed_post_event_context_ns: int
    same_source_sessions: bool
    same_alignment_origin: bool
    extension_changed_capture_result: bool
    memory_influence_used: bool
    stimulus_ground_truth_used_for_runtime_decision: bool
    source_trace_refs: tuple[str, ...]
    runtime_session_id: str
    perception_session_id: str
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str
    extension_execution_id: str
    extension_outcome_id: str
    capture_identity_before_id: str
    capture_identity_after_id: str
    transport_flush_record_id: str
    transport_flush_verified: bool
    flush_remaining_required_records: int

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, OBSERVATION_EXTENSION_COMPARISON_SCHEMA_VERSION)
        if self.memory_influence_used or self.stimulus_ground_truth_used_for_runtime_decision:
            raise ValueError("Package 125 comparison cannot use memory or stimulus ground truth for runtime decision")
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class Package125BoundedObservationExtensionAudit:
    audit_id: str
    schema_version: str
    created_at: str
    real_source_capture_verified: bool
    temporal_tail_evidence_verified: bool
    candidate_from_actual_temporal_evidence: bool
    session_authorization_verified: bool
    policy_gate_verified: bool
    internal_action_created: bool
    internal_action_kind_verified: bool
    deadline_extension_atomic: bool
    same_source_sessions_preserved: bool
    all_required_lanes_extended: bool
    extension_count: int
    granted_extension_ns: int
    event_closure_observed_after_base_deadline: bool
    post_event_context_observed: bool
    required_lane_drop_count: int
    backpressure_fault_count: int
    capture_failure_count: int
    compile_failure_count: int
    stable_control_did_not_extend: bool
    early_complete_control_did_not_extend: bool
    authorization_off_control_blocked: bool
    operator_interrupt_verified: bool
    stimulus_ground_truth_used_for_decision: bool
    package_112_score_changed: bool
    memory_write_created: bool
    external_action_created: bool
    focus_selection_created: bool
    thought_engine_used: bool
    output_created: bool
    subjective_time_claimed: bool
    waiting_semantics_claimed: bool
    novelty_semantics_claimed: bool
    object_or_audio_semantics_claimed: bool
    d_laplace_component_used: bool
    d_laplace_migration_performed: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    audit_status: str
    failure_reasons: tuple[str, ...]
    audit_mode: str
    target_observation_window_id: str
    target_runtime_session_id: str
    target_perception_session_id: str
    target_experiment_run_id: str
    target_audit_group_id: str
    target_scenario_name: str
    active_capture_identity_chain_verified: bool
    transport_flush_verified: bool
    flush_remaining_required_records: int
    operator_event_delivery_failure_count: int
    package_112_score_equivalence_record_id: str | None

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, PACKAGE_125_AUDIT_SCHEMA_VERSION)
        object.__setattr__(self, "failure_reasons", tuple_of_str(self.failure_reasons))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class ActiveCaptureSessionIdentity:
    active_capture_identity_id: str
    schema_version: str
    created_at: str
    identity_stage: str
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str
    runtime_session_id: str
    perception_session_id: str
    observation_window_id: str
    screen_capture_session_id: str
    audio_capture_session_id: str
    host_state_capture_session_id: str
    screen_descriptor_id: str
    audio_descriptor_id: str
    host_state_descriptor_id: str
    screen_config_sha256: str
    audio_config_sha256: str
    host_state_config_sha256: str
    window_handle: int
    render_endpoint_id: str
    alignment_origin_monotonic_ns: int
    clock_domain_ids: tuple[str, ...]
    observed_deadline_ns: int
    real_source_capture: bool
    sources_open: bool
    sources_reopened: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, ACTIVE_CAPTURE_SESSION_IDENTITY_SCHEMA_VERSION)
        if self.identity_stage not in {"capture_started", "deadline_extended", "capture_finalized"}:
            raise ValueError("invalid active capture identity stage")
        if self.alignment_origin_monotonic_ns < 0 or self.observed_deadline_ns <= 0:
            raise ValueError("invalid active capture timing identity")
        if self.sources_reopened:
            raise ValueError("Package 125 active capture identity cannot report reopened sources")
        object.__setattr__(self, "clock_domain_ids", tuple_of_str(self.clock_domain_ids))
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class ObservationOperatorEventDeliveryFailure:
    event_delivery_failure_id: str
    schema_version: str
    created_at: str
    event_kind: str
    runtime_session_id: str
    perception_session_id: str
    observation_window_id: str
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str
    exception_kind: str
    exception_message: str
    strict_mode: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, OPERATOR_EVENT_DELIVERY_FAILURE_SCHEMA_VERSION)
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class Package112ScoreEquivalenceRecord:
    score_equivalence_record_id: str
    schema_version: str
    created_at: str
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str
    runtime_session_id: str
    perception_session_id: str
    observation_window_id: str
    candidate_action_kind: str
    base_candidate_priority: int
    authoritative_score_before: int
    authoritative_score_after: int
    authoritative_readback_delta_before: int
    authoritative_readback_delta_after: int
    observation_extension_score_contribution: int
    package_112_score_changed: bool
    extension_context_read_only: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, PACKAGE_112_SCORE_EQUIVALENCE_SCHEMA_VERSION)
        if self.observation_extension_score_contribution != 0:
            raise ValueError("Package 125 score contribution must be zero")
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class Package125StimulusAuditManifest:
    stimulus_audit_manifest_id: str
    schema_version: str
    created_at: str
    experiment_run_id: str
    audit_group_id: str
    scenario_name: str
    runtime_result_frozen_at: str
    window_title: str
    window_handle: int
    render_endpoint_id: str
    stimulus_started_monotonic_ns: int
    stimulus_finished_monotonic_ns: int
    transition_records: tuple[dict[str, object], ...]
    consumed_by_runtime_decision: bool
    source_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, PACKAGE_125_STIMULUS_AUDIT_MANIFEST_SCHEMA_VERSION)
        if self.consumed_by_runtime_decision:
            raise ValueError("stimulus audit manifest cannot be consumed by runtime decision")
        object.__setattr__(self, "transition_records", tuple(dict(item) for item in self.transition_records))
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)
