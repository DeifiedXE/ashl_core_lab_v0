"""Immutable records for Package 126 bounded perception reacquisition."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain


BASELINE_COMMIT = "acb543ed79a9d56bbf4a1660628200f8916497d2"
PACKAGE_126_PASS_STATUS = "passed_bounded_re_sampling_and_listen_again_internal_action_v0"
PACKAGE_126_SCHEMA_PREFIX = "ashl_package_126"

ALLOWED_ACTION_KINDS = ("capture_again", "listen_again")
ALLOWED_REQUEST_SOURCES = (
    "explicit_session_configuration",
    "explicit_local_operator_request",
)
ALLOWED_REASON_CODES = (
    "repeat_same_sampling_plan",
    "explicit_bounded_reacquisition",
    "explicit_audio_relisten",
    "operator_requested_additional_sample",
    "controlled_real_capability_verification",
)
FORBIDDEN_REASON_CODES = (
    "uncertain",
    "novel",
    "interesting",
    "curious",
    "memory_conflict",
    "recognition_failed",
    "probably_same_sound",
    "speaker_unclear",
    "language_unclear",
    "waiting_for_repeat",
)

MAXIMUM_REACQUISITION_COUNT_PER_CHAIN = 1
MAXIMUM_REACQUISITION_WINDOW_NS = 2_500_000_000
MAXIMUM_PARENT_TO_CHILD_GAP_NS = 5_000_000_000
MAXIMUM_TOTAL_CHAIN_DURATION_NS = 10_000_000_000


def _record_dict(record: Any) -> dict[str, object]:
    return {field.name: plain(getattr(record, field.name)) for field in fields(record)}


def _tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def _normalize_tuple_fields(record: Any, names: tuple[str, ...]) -> None:
    for name in names:
        object.__setattr__(record, name, _tuple_of_str(getattr(record, name)))


@dataclass(frozen=True)
class PerceptionReacquisitionAuthorization:
    authorization_id: str
    schema_version: str
    created_at: str
    parent_runtime_session_id: str
    parent_perception_session_id: str
    parent_observation_window_id: str
    authorization_source: str
    authorized_by: str
    allowed_action_kinds: tuple[str, ...]
    maximum_reacquisition_count: int
    maximum_reacquisition_window_ns: int
    maximum_parent_to_child_gap_ns: int
    maximum_total_chain_duration_ns: int
    same_plan_required: bool
    same_target_required: bool
    same_privacy_policy_required: bool
    expires_at_chain_end: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.authorization_source not in ALLOWED_REQUEST_SOURCES:
            raise ValueError("invalid reacquisition authorization source")
        if self.authorized_by != "local_operator":
            raise ValueError("Package 126 authorization must be local-operator authorized")
        if not set(self.allowed_action_kinds).issubset(ALLOWED_ACTION_KINDS):
            raise ValueError("authorization contains unsupported action kind")
        if not self.allowed_action_kinds:
            raise ValueError("authorization requires an action kind")
        if not 0 < self.maximum_reacquisition_count <= MAXIMUM_REACQUISITION_COUNT_PER_CHAIN:
            raise ValueError("maximum reacquisition count exceeds Package 126")
        if not 0 < self.maximum_reacquisition_window_ns <= MAXIMUM_REACQUISITION_WINDOW_NS:
            raise ValueError("maximum reacquisition window exceeds Package 126")
        if not 0 < self.maximum_parent_to_child_gap_ns <= MAXIMUM_PARENT_TO_CHILD_GAP_NS:
            raise ValueError("maximum parent-child gap exceeds Package 126")
        if not 0 < self.maximum_total_chain_duration_ns <= MAXIMUM_TOTAL_CHAIN_DURATION_NS:
            raise ValueError("maximum chain duration exceeds Package 126")
        if not (
            self.same_plan_required
            and self.same_target_required
            and self.same_privacy_policy_required
            and self.expires_at_chain_end
        ):
            raise ValueError("Package 126 authorization must preserve plan, target, privacy, and chain expiry")
        _normalize_tuple_fields(
            self,
            ("allowed_action_kinds", "source_record_refs", "source_trace_refs"),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class CompletedObservationWindowReference:
    completed_window_reference_id: str
    schema_version: str
    created_at: str
    runtime_session_id: str
    perception_session_id: str
    observation_window_id: str
    completion_status: str
    finalized_at_event_time_ns: int
    finalized_at_processing_time_ns: int
    participating_lanes: tuple[str, ...]
    required_lanes: tuple[str, ...]
    source_capture_session_refs: tuple[str, ...]
    sampling_plan_identity_ref: str
    final_temporal_bundle_ref: str
    required_lane_drop_count: int
    backpressure_fault_count: int
    capture_failure_count: int
    compile_failure_count: int
    flush_remaining_count: int
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.completion_status not in {"completed_clean", "active", "interrupted", "failed"}:
            raise ValueError("invalid completed-window reference status")
        for value in (
            self.required_lane_drop_count,
            self.backpressure_fault_count,
            self.capture_failure_count,
            self.compile_failure_count,
            self.flush_remaining_count,
        ):
            if value < 0:
                raise ValueError("parent integrity counts cannot be negative")
        _normalize_tuple_fields(
            self,
            (
                "participating_lanes",
                "required_lanes",
                "source_capture_session_refs",
                "source_record_refs",
                "source_trace_refs",
            ),
        )

    @property
    def completed_clean(self) -> bool:
        return self.completion_status == "completed_clean" and not any(
            (
                self.required_lane_drop_count,
                self.backpressure_fault_count,
                self.capture_failure_count,
                self.compile_failure_count,
                self.flush_remaining_count,
            )
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class SamplingPlanIdentityRecord:
    sampling_plan_identity_id: str
    schema_version: str
    created_at: str
    plan_kind: str
    modality_scope: tuple[str, ...]
    required_lanes: tuple[str, ...]
    participating_lanes: tuple[str, ...]
    screen_target_descriptor_hash: str | None
    screen_region_hash: str | None
    screen_capture_config_hash: str | None
    audio_endpoint_descriptor_hash: str | None
    audio_capture_config_hash: str | None
    audio_privacy_mode: str | None
    audio_blur_policy_version: str | None
    host_state_config_hash: str | None
    visual_compiler_version: str | None
    audio_compiler_version: str | None
    redaction_config_hash: str | None
    event_clock_domain: str
    processing_clock_domain: str
    replay_clock_domain: str | None
    canonical_plan_hash: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.plan_kind not in {"multimodal_same_plan", "audio_relisten_same_plan"}:
            raise ValueError("invalid Package 126 plan kind")
        if not self.canonical_plan_hash:
            raise ValueError("canonical plan hash is required")
        _normalize_tuple_fields(
            self,
            ("modality_scope", "required_lanes", "participating_lanes", "source_record_refs", "source_trace_refs"),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class PerceptionReacquisitionRequest:
    reacquisition_request_id: str
    schema_version: str
    created_at: str
    parent_window_reference_id: str
    authorization_id: str
    requested_action_kind: str
    requested_window_ns: int
    request_source: str
    request_reason_codes: tuple[str, ...]
    requested_plan_identity_ref: str
    thought_engine_used: bool
    memory_used: bool
    endocrine_signal_used: bool
    uncertainty_signal_used: bool
    novelty_signal_used: bool
    stimulus_ground_truth_used: bool
    request_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.requested_action_kind not in ALLOWED_ACTION_KINDS:
            raise ValueError("invalid reacquisition action kind")
        if self.request_source not in ALLOWED_REQUEST_SOURCES:
            raise ValueError("invalid reacquisition request source")
        if not 0 < self.requested_window_ns <= MAXIMUM_REACQUISITION_WINDOW_NS:
            raise ValueError("requested window exceeds Package 126")
        reasons = set(self.request_reason_codes)
        if not reasons or not reasons.issubset(ALLOWED_REASON_CODES) or reasons.intersection(FORBIDDEN_REASON_CODES):
            raise ValueError("invalid Package 126 reason code")
        if any(
            (
                self.thought_engine_used,
                self.memory_used,
                self.endocrine_signal_used,
                self.uncertainty_signal_used,
                self.novelty_signal_used,
                self.stimulus_ground_truth_used,
            )
        ):
            raise ValueError("Package 126 request may use only explicit bounded authorization")
        if self.request_status not in {"pending", "cancelled", "consumed", "blocked"}:
            raise ValueError("invalid request status")
        _normalize_tuple_fields(
            self,
            ("request_reason_codes", "source_record_refs", "source_trace_refs"),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class ReacquisitionEligibilityDecision:
    eligibility_decision_id: str
    schema_version: str
    created_at: str
    reacquisition_request_id: str
    decision: str
    parent_window_completed_clean: bool
    authorization_valid: bool
    action_kind_allowed: bool
    plan_identity_matches: bool
    target_identity_matches: bool
    privacy_policy_matches: bool
    reacquisition_budget_available: bool
    gap_budget_available: bool
    chain_duration_budget_available: bool
    prior_attempt_count: int
    parent_transport_integrity_valid: bool
    operator_stop_absent: bool
    granted_window_ns: int
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.decision not in {"allow", "block", "expired", "cancelled"}:
            raise ValueError("invalid reacquisition eligibility decision")
        if self.prior_attempt_count < 0:
            raise ValueError("prior attempt count cannot be negative")
        if self.decision == "allow":
            gates = (
                self.parent_window_completed_clean,
                self.authorization_valid,
                self.action_kind_allowed,
                self.plan_identity_matches,
                self.target_identity_matches,
                self.privacy_policy_matches,
                self.reacquisition_budget_available,
                self.gap_budget_available,
                self.chain_duration_budget_available,
                self.parent_transport_integrity_valid,
                self.operator_stop_absent,
            )
            if not all(gates) or self.failure_reasons or self.granted_window_ns <= 0:
                raise ValueError("allow decision requires every Package 126 gate")
        elif self.granted_window_ns != 0:
            raise ValueError("blocked, expired, or cancelled request cannot grant a window")
        _normalize_tuple_fields(
            self,
            ("failure_reasons", "source_record_refs", "source_trace_refs"),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class BoundedReacquisitionInternalAction:
    internal_action_id: str
    schema_version: str
    created_at: str
    action_kind: str
    eligibility_decision_id: str
    parent_observation_window_id: str
    requested_window_ns: int
    granted_window_ns: int
    internal_only: bool
    external_side_effect: bool
    creates_new_capture_window: bool
    reuses_old_artifact: bool
    replays_old_artifact: bool
    recompiles_old_artifact: bool
    selected_action_created: bool
    final_action_created: bool
    direct_command_created: bool
    action_source: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.action_kind not in ALLOWED_ACTION_KINDS:
            raise ValueError("invalid bounded reacquisition action kind")
        if not self.internal_only or self.external_side_effect or not self.creates_new_capture_window:
            raise ValueError("Package 126 action must remain internal and create a new capture window")
        if any(
            (
                self.reuses_old_artifact,
                self.replays_old_artifact,
                self.recompiles_old_artifact,
                self.selected_action_created,
                self.final_action_created,
                self.direct_command_created,
            )
        ):
            raise ValueError("Package 126 action crossed a replay or external-action boundary")
        if self.action_source != "explicit_bounded_perception_reacquisition_policy":
            raise ValueError("invalid Package 126 action source")
        _normalize_tuple_fields(self, ("source_record_refs", "source_trace_refs"))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class ReacquisitionCaptureExecution:
    reacquisition_execution_id: str
    schema_version: str
    created_at: str
    internal_action_id: str
    parent_runtime_session_id: str
    parent_perception_session_id: str
    parent_observation_window_id: str
    child_runtime_session_id: str
    child_perception_session_id: str
    child_observation_window_id: str
    parent_plan_identity_ref: str
    child_plan_identity_ref: str
    parent_capture_session_refs: tuple[str, ...]
    child_capture_session_refs: tuple[str, ...]
    parent_alignment_origin_ref: str
    child_alignment_origin_ref: str
    event_clock_domain_preserved: bool
    processing_clock_domain_preserved: bool
    capture_session_ids_reused: bool
    source_targets_preserved: bool
    source_configuration_preserved: bool
    privacy_policy_preserved: bool
    sources_reopened: bool
    old_artifact_reused: bool
    requested_window_ns: int
    actual_window_ns: int
    execution_status: str
    failure_kind: str | None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.execution_status not in {"completed_clean", "interrupted", "failed", "blocked"}:
            raise ValueError("invalid reacquisition execution status")
        if set(self.parent_capture_session_refs).intersection(self.child_capture_session_refs):
            object.__setattr__(self, "capture_session_ids_reused", True)
        if self.execution_status == "completed_clean":
            if (
                self.capture_session_ids_reused
                or not self.source_targets_preserved
                or not self.source_configuration_preserved
                or not self.privacy_policy_preserved
                or not self.sources_reopened
                or self.old_artifact_reused
            ):
                raise ValueError("clean reacquisition execution lacks derived identity proof")
        _normalize_tuple_fields(
            self,
            (
                "parent_capture_session_refs",
                "child_capture_session_refs",
                "source_record_refs",
                "source_trace_refs",
            ),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class CrossWindowTemporalContinuityLink:
    continuity_link_id: str
    schema_version: str
    created_at: str
    parent_observation_window_id: str
    child_observation_window_id: str
    parent_final_anchor_ref: str
    child_start_anchor_ref: str
    parent_final_event_time_ns: int
    child_start_event_time_ns: int
    external_gap_ns: int
    same_event_clock_domain: bool
    same_processing_clock_domain: bool
    windows_temporally_contiguous: bool
    gap_explicit: bool
    source_temporal_refs: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.parent_observation_window_id == self.child_observation_window_id:
            raise ValueError("cross-window link requires distinct windows")
        if self.external_gap_ns < 0:
            raise ValueError("external gap cannot be negative")
        if self.windows_temporally_contiguous or not self.gap_explicit:
            raise ValueError("Package 126 windows must preserve an explicit non-contiguous gap")
        _normalize_tuple_fields(
            self,
            ("source_temporal_refs", "source_record_refs", "source_trace_refs"),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class ReacquiredEvidenceSummary:
    reacquired_evidence_summary_id: str
    schema_version: str
    created_at: str
    reacquisition_execution_id: str
    child_observation_window_id: str
    child_temporal_bundle_ref: str
    visual_primitive_refs: tuple[str, ...]
    audio_primitive_refs: tuple[str, ...]
    host_state_record_refs: tuple[str, ...]
    child_required_windows_expected: int
    child_required_windows_complete: int
    child_required_lane_drop_count: int
    child_backpressure_fault_count: int
    child_capture_failure_count: int
    child_compile_failure_count: int
    child_flush_remaining_count: int
    new_visual_evidence_present: bool
    new_audio_evidence_present: bool
    new_host_state_evidence_present: bool
    raw_audio_retained: bool
    raw_parent_artifact_reused: bool
    semantic_interpretation_created: bool
    recognition_result_created: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.child_required_windows_complete > self.child_required_windows_expected:
            raise ValueError("complete child windows cannot exceed expected windows")
        if any(
            (
                self.raw_audio_retained,
                self.raw_parent_artifact_reused,
                self.semantic_interpretation_created,
                self.recognition_result_created,
            )
        ):
            raise ValueError("Package 126 evidence crossed privacy or semantic boundary")
        _normalize_tuple_fields(
            self,
            (
                "visual_primitive_refs",
                "audio_primitive_refs",
                "host_state_record_refs",
                "source_record_refs",
                "source_trace_refs",
            ),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class ReacquisitionEffectComparison:
    comparison_id: str
    schema_version: str
    created_at: str
    parent_observation_window_id: str
    child_observation_window_id: str
    action_kind: str
    parent_plan_identity_ref: str
    child_plan_identity_ref: str
    plan_identity_equal: bool
    capture_session_identity_distinct: bool
    external_gap_recorded: bool
    parent_evidence_record_count: int
    child_evidence_record_count: int
    child_new_evidence_present: bool
    action_changed_runtime_capture_history: bool
    low_level_pair_available_for_future_comparison: bool
    same_event_claimed: bool
    same_sound_claimed: bool
    recognition_claimed: bool
    memory_used: bool
    stimulus_ground_truth_used_for_runtime_decision: bool
    effect_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.action_kind not in ALLOWED_ACTION_KINDS:
            raise ValueError("invalid comparison action kind")
        if any(
            (
                self.same_event_claimed,
                self.same_sound_claimed,
                self.recognition_claimed,
                self.memory_used,
                self.stimulus_ground_truth_used_for_runtime_decision,
            )
        ):
            raise ValueError("Package 126 comparison must remain low-level and nonsemantic")
        if self.effect_status not in {"new_evidence_observed", "no_new_event_observed", "interrupted", "failed"}:
            raise ValueError("invalid reacquisition effect status")
        _normalize_tuple_fields(self, ("source_record_refs", "source_trace_refs"))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class ReacquisitionCancellationRecord:
    cancellation_id: str
    schema_version: str
    created_at: str
    target_request_id: str
    target_internal_action_id: str | None
    requested_by: str
    reason: str
    cancellation_succeeded: bool
    child_capture_started: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.requested_by != "local_operator":
            raise ValueError("reacquisition cancellation must be local-operator requested")
        if self.cancellation_succeeded and self.child_capture_started:
            raise ValueError("started child capture must be stopped, not cancelled")
        _normalize_tuple_fields(self, ("source_record_refs", "source_trace_refs"))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class EphemeralAudioDeletionVerificationRecord:
    deletion_record_id: str
    schema_version: str
    created_at: str
    child_observation_window_id: str
    ephemeral_audio_session_id: str
    content_sha256_before_deletion: str
    transient_file_path_fingerprint: str | None
    backend_transient_file_created: bool
    ring_buffer_overwritten: bool
    ring_buffer_live_bytes_after: int
    transient_file_absent_after: bool
    raw_audio_retained: bool
    deletion_verified: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.content_sha256_before_deletion:
            raise ValueError("ephemeral deletion verification requires a pre-clear content hash")
        if (
            not self.ring_buffer_overwritten
            or self.ring_buffer_live_bytes_after != 0
            or not self.transient_file_absent_after
            or self.raw_audio_retained
            or not self.deletion_verified
        ):
            raise ValueError("ephemeral audio deletion was not verified")
        _normalize_tuple_fields(self, ("source_record_refs", "source_trace_refs"))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package126ScoreEquivalenceRecord:
    score_equivalence_record_id: str
    schema_version: str
    created_at: str
    parent_observation_window_id: str
    authoritative_score_before: int
    authoritative_score_after: int
    package_126_score_contribution: int
    package_112_score_changed: bool
    reacquisition_context_read_only: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.authoritative_score_before != self.authoritative_score_after
            or self.package_126_score_contribution != 0
            or self.package_112_score_changed
            or not self.reacquisition_context_read_only
        ):
            raise ValueError("Package 126 changed Package 112 scoring")
        _normalize_tuple_fields(self, ("source_record_refs", "source_trace_refs"))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package126BoundedReacquisitionAudit:
    audit_id: str
    schema_version: str
    created_at: str
    baseline_commit: str
    package_125_baseline_verified: bool
    qm0_baseline_verified: bool
    capture_again_real_run_verified: bool
    listen_again_real_run_verified: bool
    capture_again_action_created: bool
    listen_again_action_created: bool
    parent_windows_completed_clean: bool
    child_windows_created: bool
    parent_child_plan_identity_equal: bool
    parent_child_target_identity_equal: bool
    parent_child_config_identity_equal: bool
    capture_session_ids_distinct: bool
    sources_reopened_verified: bool
    old_artifact_reused: bool
    cross_window_gap_recorded: bool
    windows_falsely_merged: bool
    child_new_visual_evidence_present: bool
    child_new_audio_evidence_present: bool
    child_new_host_state_evidence_present: bool
    listen_again_recognition_ephemeral_verified: bool
    raw_audio_retained: bool
    audio_deletion_verified: bool
    child_required_lane_drop_count: int
    child_backpressure_fault_count: int
    child_capture_failure_count: int
    child_compile_failure_count: int
    child_flush_remaining_count: int
    authorization_off_control_passed: bool
    parent_active_control_passed: bool
    plan_mismatch_control_passed: bool
    attempt_limit_control_passed: bool
    expired_request_control_passed: bool
    old_artifact_replay_control_passed: bool
    session_id_reuse_control_passed: bool
    transport_fault_control_passed: bool
    operator_stop_control_passed: bool
    audio_retention_violation_control_passed: bool
    no_event_child_control_passed: bool
    package_112_score_changed: bool
    memory_write_created: bool
    working_readback_created: bool
    focus_selection_created: bool
    evidence_sufficiency_runtime_created: bool
    uncertainty_signal_created: bool
    novelty_signal_created: bool
    thought_engine_used: bool
    output_created: bool
    external_control_created: bool
    same_event_claimed: bool
    same_sound_claimed: bool
    speaker_recognition_claimed: bool
    language_understanding_claimed: bool
    subjective_listening_claimed: bool
    package_127_implemented: bool
    package_128_implemented: bool
    d_laplace_component_used: bool
    d_laplace_migration_performed: bool
    dlm_1_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    audit_status: str
    failure_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _normalize_tuple_fields(self, ("failure_reasons", "source_trace_refs"))

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)
