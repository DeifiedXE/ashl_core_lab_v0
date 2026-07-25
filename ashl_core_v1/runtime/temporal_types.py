"""Grounded temporal primitive record types for Package 124A."""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain, sha256_payload


CLOCK_DOMAIN_SCHEMA_VERSION = "ashl_temporal_clock_domain_descriptor_v0"
CLOCK_QUALITY_SCHEMA_VERSION = "ashl_temporal_clock_quality_v0"
TEMPORAL_ANCHOR_SCHEMA_VERSION = "ashl_temporal_event_anchor_v0"
TEMPORAL_SPAN_SCHEMA_VERSION = "ashl_temporal_span_primitive_v0"
TEMPORAL_INTERVAL_SCHEMA_VERSION = "ashl_temporal_interval_primitive_v0"
TEMPORAL_RELATION_SCHEMA_VERSION = "ashl_temporal_relation_primitive_v0"
TEMPORAL_CONTINUITY_SCHEMA_VERSION = "ashl_temporal_continuity_primitive_v0"
REPEATED_STRUCTURE_SCHEMA_VERSION = "ashl_repeated_occurrence_temporal_structure_v0"
RUNTIME_STATE_SPAN_SCHEMA_VERSION = "ashl_runtime_state_temporal_span_v0"
EXTERNAL_GAP_SCHEMA_VERSION = "ashl_cross_process_external_gap_v0"
ACTION_ORDINAL_SCHEMA_VERSION = "ashl_action_ordinal_position_v0"
TEMPORAL_BUNDLE_SCHEMA_VERSION = "ashl_grounded_temporal_primitive_bundle_v0"
TEMPORAL_CALIBRATION_AUDIT_SCHEMA_VERSION = "ashl_temporal_calibration_audit_v0"
TEMPORAL_CONTEXT_SIDECAR_SCHEMA_VERSION = "ashl_temporal_perception_context_sidecar_v0"
TEMPORAL_ORDERING_DIAGNOSTIC_SCHEMA_VERSION = "ashl_temporal_ordering_diagnostic_v0"
PACKAGE_124A_AUDIT_SCHEMA_VERSION = "ashl_package_124a_grounded_temporal_foundation_audit_v0"

TEMPORAL_STORE_SCHEMA_NAME = "ashl_package_124a_temporal_foundation_store"
TEMPORAL_STORE_SCHEMA_VERSION = "v0"

ALLOWED_CLOCK_QUALITY_STATUSES = ("verified", "verified_with_uncertainty", "indeterminate", "invalid")
ALLOWED_SPAN_KINDS = (
    "observed_change_region",
    "observed_energy_region",
    "alignment_coverage_span",
    "runtime_state_span",
    "source_presence_span",
)
ALLOWED_INTERVAL_KINDS = (
    "onset_to_onset",
    "offset_to_onset",
    "event_to_event",
    "state_transition_to_transition",
)
ALLOWED_CONTINUITY_STATUSES = (
    "continuous",
    "continuous_with_partial_edges",
    "interrupted",
    "indeterminate",
)
ALLOWED_RUNTIME_STATES = ("running", "sleeping", "stopped")
ALLOWED_GAP_STATUSES = (
    "measured_external_gap",
    "measured_with_uncertainty",
    "indeterminate_clock_change",
    "invalid",
)
ALLOWED_CALIBRATION_STATUSES = (
    "calibrated_after_compilation",
    "blocked_stimulus_loaded_too_early",
    "blocked_mismatch",
    "not_available",
)
ALLOWED_SIDECAR_AUTHORITIES = ("read_only_context",)
ALLOWED_AUDIT_STATUS = "passed_grounded_temporal_primitive_foundation_v0"


class TemporalRelationKind(str, Enum):
    BEFORE = "before"
    AFTER = "after"
    MEETS = "meets"
    OVERLAPS = "overlaps"
    CONTAINS = "contains"
    DURING = "during"
    EQUAL_SPAN = "equal_span"


def tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def record_dict(record: Any) -> dict[str, object]:
    return {field.name: plain(getattr(record, field.name)) for field in fields(record)}


def temporal_identity(prefix: str, payload: dict[str, Any], *, length: int = 12) -> str:
    return f"{prefix}:{sha256_payload(payload)[:length]}"


def primitive_payload_hash(record: Any) -> str:
    payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
    payload = {
        key: value
        for key, value in payload.items()
        if key not in {"created_at", "primitive_payload_sha256"}
    }
    return sha256_payload(payload)


def _require_schema(actual: str, expected: str) -> None:
    if actual != expected:
        raise ValueError(f"invalid schema_version: {actual}")


def _require_null(name: str, value: Any) -> None:
    if value is not None:
        raise ValueError(f"{name} must be null")


@dataclass(frozen=True)
class TemporalClockDomainDescriptor:
    clock_domain_id: str
    schema_version: str
    created_at: str
    process_instance_id: str
    operating_system_process_id: int
    monotonic_clock_kind: str
    monotonic_origin_ns: int
    utc_anchor: str
    utc_anchor_monotonic_ns: int
    operating_system_boot_identity: str | None
    nominal_resolution_ns: int
    measured_uncertainty_ns: int
    comparable_within_process: bool
    comparable_across_processes: bool
    cross_process_comparison_method: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, CLOCK_DOMAIN_SCHEMA_VERSION)
        if not self.comparable_within_process:
            raise ValueError("clock domain must be comparable within process")
        if self.cross_process_comparison_method != "persisted_utc_anchor_with_recorded_uncertainty":
            raise ValueError("invalid cross-process comparison method")
        if int(self.nominal_resolution_ns) <= 0:
            raise ValueError("nominal_resolution_ns must be positive")
        if int(self.measured_uncertainty_ns) < 0:
            raise ValueError("measured_uncertainty_ns cannot be negative")
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class TemporalClockQualityRecord:
    clock_quality_id: str
    schema_version: str
    created_at: str
    clock_domain_id: str
    monotonic_non_decreasing: bool
    utc_anchor_valid: bool
    wall_clock_backward_jump_detected: bool
    wall_clock_forward_jump_detected: bool
    maximum_observed_clock_drift_ns: int | None
    comparison_uncertainty_ns: int
    quality_status: str
    failure_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, CLOCK_QUALITY_SCHEMA_VERSION)
        if self.quality_status not in ALLOWED_CLOCK_QUALITY_STATUSES:
            raise ValueError("invalid clock quality status")
        object.__setattr__(self, "failure_reasons", tuple_of_str(self.failure_reasons))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class TemporalEventAnchor:
    temporal_anchor_id: str
    schema_version: str
    source_record_id: str
    source_record_kind: str
    source_lane: str
    clock_domain_id: str
    source_native_time_ns: int | None
    normalized_event_time_ns: int
    processing_time_ns: int | None
    replay_submission_time_ns: int | None
    event_sequence_index: int | None
    action_tick: int | None
    timestamp_resolution_ns: int
    timestamp_uncertainty_ns: int
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, TEMPORAL_ANCHOR_SCHEMA_VERSION)
        if self.timestamp_resolution_ns <= 0:
            raise ValueError("timestamp_resolution_ns must be positive")
        if self.timestamp_uncertainty_ns < 0:
            raise ValueError("timestamp_uncertainty_ns cannot be negative")
        if self.event_sequence_index is not None and self.event_sequence_index < 0:
            raise ValueError("event_sequence_index cannot be negative")
        if self.action_tick is not None and self.action_tick < 0:
            raise ValueError("action_tick cannot be negative")
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class TemporalSpanPrimitive:
    temporal_span_id: str
    schema_version: str
    created_at: str
    span_kind: str
    start_anchor_id: str
    end_anchor_id: str
    start_event_time_ns: int
    end_event_time_ns: int
    observed_duration_ns: int
    measurement_resolution_ns: int
    measurement_uncertainty_ns: int
    source_lane: str | None
    source_region_refs: tuple[str, ...]
    semantic_label: None
    subjective_duration_claimed: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, TEMPORAL_SPAN_SCHEMA_VERSION)
        if self.span_kind not in ALLOWED_SPAN_KINDS:
            raise ValueError("invalid temporal span kind")
        expected_duration = int(self.end_event_time_ns) - int(self.start_event_time_ns)
        if expected_duration < 0:
            raise ValueError("temporal span duration cannot be negative")
        if expected_duration == 0:
            raise ValueError("zero-duration evidence remains an anchor, not a span")
        if self.observed_duration_ns != expected_duration:
            raise ValueError("observed_duration_ns must equal end - start")
        _require_null("semantic_label", self.semantic_label)
        if self.subjective_duration_claimed:
            raise ValueError("subjective duration claim is forbidden")
        object.__setattr__(self, "source_region_refs", tuple_of_str(self.source_region_refs))
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class TemporalIntervalPrimitive:
    temporal_interval_id: str
    schema_version: str
    created_at: str
    interval_kind: str
    left_anchor_id: str
    right_anchor_id: str
    left_event_time_ns: int
    right_event_time_ns: int
    interval_ns: int
    measurement_resolution_ns: int
    measurement_uncertainty_ns: int
    semantic_label: None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, TEMPORAL_INTERVAL_SCHEMA_VERSION)
        if self.interval_kind not in ALLOWED_INTERVAL_KINDS:
            raise ValueError("invalid temporal interval kind")
        expected = int(self.right_event_time_ns) - int(self.left_event_time_ns)
        if self.interval_ns != expected:
            raise ValueError("interval_ns must equal right - left")
        _require_null("semantic_label", self.semantic_label)
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class TemporalRelationPrimitive:
    temporal_relation_id: str
    schema_version: str
    created_at: str
    relation_kind: str
    left_temporal_ref: str
    right_temporal_ref: str
    gap_ns: int | None
    overlap_ns: int | None
    comparison_tolerance_ns: int
    relation_confidence: float
    relation_uncertainty_ns: int
    semantic_label: None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, TEMPORAL_RELATION_SCHEMA_VERSION)
        if self.relation_kind not in {item.value for item in TemporalRelationKind}:
            raise ValueError("invalid temporal relation kind")
        if self.comparison_tolerance_ns < 0:
            raise ValueError("comparison_tolerance_ns cannot be negative")
        if not 0.0 <= float(self.relation_confidence) <= 1.0:
            raise ValueError("relation_confidence must be 0.0..1.0")
        _require_null("semantic_label", self.semantic_label)
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class TemporalContinuityPrimitive:
    temporal_continuity_id: str
    schema_version: str
    created_at: str
    coverage_start_ns: int
    coverage_end_ns: int
    required_lanes: tuple[str, ...]
    observed_lanes: tuple[str, ...]
    complete_window_count: int
    incomplete_window_count: int
    partial_edge_window_count: int
    uncovered_gap_count: int
    maximum_uncovered_gap_ns: int
    continuity_status: str
    stable_data_counted_as_present: bool
    silent_data_counted_as_present: bool
    source_alignment_window_refs: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, TEMPORAL_CONTINUITY_SCHEMA_VERSION)
        if self.coverage_end_ns < self.coverage_start_ns:
            raise ValueError("coverage end cannot precede start")
        if self.continuity_status not in ALLOWED_CONTINUITY_STATUSES:
            raise ValueError("invalid continuity status")
        if not self.stable_data_counted_as_present or not self.silent_data_counted_as_present:
            raise ValueError("stable and silent data must count as temporally present")
        object.__setattr__(self, "required_lanes", tuple_of_str(self.required_lanes))
        object.__setattr__(self, "observed_lanes", tuple_of_str(self.observed_lanes))
        object.__setattr__(self, "source_alignment_window_refs", tuple_of_str(self.source_alignment_window_refs))
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class RepeatedOccurrenceTemporalStructure:
    repeated_structure_id: str
    schema_version: str
    created_at: str
    occurrence_refs: tuple[str, ...]
    occurrence_count: int
    inter_onset_intervals_ns: tuple[int, ...]
    observed_span_durations_ns: tuple[int, ...]
    interval_min_ns: int | None
    interval_max_ns: int | None
    interval_mean_ns: int | None
    interval_variation_ns: int | None
    regularity_semantic_label: None
    rhythm_semantics_claimed: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, REPEATED_STRUCTURE_SCHEMA_VERSION)
        object.__setattr__(self, "occurrence_refs", tuple_of_str(self.occurrence_refs))
        object.__setattr__(self, "inter_onset_intervals_ns", tuple(int(item) for item in self.inter_onset_intervals_ns))
        object.__setattr__(self, "observed_span_durations_ns", tuple(int(item) for item in self.observed_span_durations_ns))
        if self.occurrence_count != len(self.occurrence_refs):
            raise ValueError("occurrence_count mismatch")
        _require_null("regularity_semantic_label", self.regularity_semantic_label)
        if self.rhythm_semantics_claimed:
            raise ValueError("rhythm semantics are forbidden")
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class RuntimeStateTemporalSpan:
    runtime_state_span_id: str
    schema_version: str
    runtime_state: str
    start_anchor_id: str
    end_anchor_id: str | None
    observed_duration_ns: int | None
    open_span: bool
    state_source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, RUNTIME_STATE_SPAN_SCHEMA_VERSION)
        if self.runtime_state not in ALLOWED_RUNTIME_STATES:
            raise ValueError("invalid runtime state")
        if self.open_span and self.observed_duration_ns is not None:
            raise ValueError("open runtime state spans cannot claim duration")
        if not self.open_span and self.end_anchor_id is None:
            raise ValueError("closed runtime state spans need an end anchor")
        object.__setattr__(self, "state_source_record_refs", tuple_of_str(self.state_source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class CrossProcessExternalGapRecord:
    external_gap_id: str
    schema_version: str
    created_at: str
    previous_process_instance_id: str
    current_process_instance_id: str
    previous_last_event_utc: str
    current_first_event_utc: str
    external_gap_ns: int | None
    comparison_uncertainty_ns: int
    previous_clock_domain_id: str
    current_clock_domain_id: str
    wall_clock_adjustment_detected: bool
    gap_status: str
    discovered_after_resume: bool
    experienced_during_gap: bool
    synthetic_ticks_created: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, EXTERNAL_GAP_SCHEMA_VERSION)
        if self.gap_status not in ALLOWED_GAP_STATUSES:
            raise ValueError("invalid external gap status")
        if not self.discovered_after_resume:
            raise ValueError("external gaps must be discovered after resume")
        if self.experienced_during_gap or self.synthetic_ticks_created:
            raise ValueError("shutdown/sleep gaps cannot be experienced or filled with synthetic ticks")
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class ActionOrdinalPosition:
    action_tick: int
    session_id: str
    elapsed_time_claimed: bool
    schema_version: str = ACTION_ORDINAL_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, ACTION_ORDINAL_SCHEMA_VERSION)
        if self.action_tick < 0:
            raise ValueError("action_tick cannot be negative")
        if self.elapsed_time_claimed:
            raise ValueError("action_tick is ordinal and cannot claim elapsed time")

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class GroundedTemporalPrimitiveBundle:
    temporal_bundle_id: str
    schema_version: str
    created_at: str
    clock_domain_refs: tuple[str, ...]
    anchor_refs: tuple[str, ...]
    span_refs: tuple[str, ...]
    interval_refs: tuple[str, ...]
    relation_refs: tuple[str, ...]
    continuity_refs: tuple[str, ...]
    repeated_structure_refs: tuple[str, ...]
    external_gap_refs: tuple[str, ...]
    source_perception_record_refs: tuple[str, ...]
    source_alignment_window_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    stimulus_ground_truth_used_for_compilation: bool
    subjective_time_claimed: bool
    rhythm_semantics_claimed: bool
    waiting_semantics_claimed: bool

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, TEMPORAL_BUNDLE_SCHEMA_VERSION)
        for name in (
            "clock_domain_refs",
            "anchor_refs",
            "span_refs",
            "interval_refs",
            "relation_refs",
            "continuity_refs",
            "repeated_structure_refs",
            "external_gap_refs",
            "source_perception_record_refs",
            "source_alignment_window_refs",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, tuple_of_str(getattr(self, name)))
        if self.stimulus_ground_truth_used_for_compilation:
            raise ValueError("stimulus ground truth must not compile temporal primitives")
        if self.subjective_time_claimed or self.rhythm_semantics_claimed or self.waiting_semantics_claimed:
            raise ValueError("subjective time, rhythm and waiting claims are forbidden")

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class TemporalCalibrationAuditRecord:
    calibration_audit_id: str
    schema_version: str
    created_at: str
    temporal_bundle_id: str
    stimulus_manifest_id: str | None
    stimulus_loaded_after_compilation: bool
    stimulus_used_for_compilation: bool
    observed_visual_transition_count: int
    expected_visual_transition_count: int | None
    observed_audio_energy_count: int
    expected_audio_energy_count: int | None
    observed_overlap_count: int
    expected_overlap_count: int | None
    tolerance_ns: int
    calibration_status: str
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, TEMPORAL_CALIBRATION_AUDIT_SCHEMA_VERSION)
        if self.calibration_status not in ALLOWED_CALIBRATION_STATUSES:
            raise ValueError("invalid temporal calibration status")
        if self.stimulus_used_for_compilation:
            raise ValueError("stimulus schedule cannot be used for compilation")
        object.__setattr__(self, "failure_reasons", tuple_of_str(self.failure_reasons))
        object.__setattr__(self, "source_record_refs", tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class TemporalPerceptionContextSidecar:
    temporal_sidecar_id: str
    schema_version: str
    created_at: str
    source_perception_record_id: str
    temporal_bundle_id: str
    anchor_refs: tuple[str, ...]
    span_refs: tuple[str, ...]
    relation_refs: tuple[str, ...]
    continuity_refs: tuple[str, ...]
    sidecar_authority: str
    read_only: bool
    scoring_authority: bool
    memory_write_authority: bool
    action_selection_authority: bool
    output_authority: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, TEMPORAL_CONTEXT_SIDECAR_SCHEMA_VERSION)
        if self.sidecar_authority not in ALLOWED_SIDECAR_AUTHORITIES:
            raise ValueError("invalid temporal sidecar authority")
        if not self.read_only:
            raise ValueError("temporal sidecar must be read-only")
        if self.scoring_authority or self.memory_write_authority or self.action_selection_authority or self.output_authority:
            raise ValueError("temporal sidecar has context authority only")
        for name in ("anchor_refs", "span_refs", "relation_refs", "continuity_refs", "source_record_refs", "source_trace_refs"):
            object.__setattr__(self, name, tuple_of_str(getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class TemporalOrderingDiagnostic:
    diagnostic_id: str
    schema_version: str
    source_record_id: str
    event_sequence_index: int | None
    event_time_ns: int
    processing_time_ns: int | None
    event_order_processing_order_disagree: bool
    diagnostic_status: str

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, TEMPORAL_ORDERING_DIAGNOSTIC_SCHEMA_VERSION)
        if self.diagnostic_status not in {"ok", "processing_order_disagrees_with_event_time"}:
            raise ValueError("invalid temporal ordering diagnostic status")

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)


@dataclass(frozen=True)
class Package124AGroundedTemporalFoundationAudit:
    audit_id: str
    schema_version: str
    created_at: str
    package_124_archive_verified: bool
    archive_opened_read_only: bool
    archive_modified: bool
    clock_domains_verified: bool
    event_processing_time_separated: bool
    replay_time_separated: bool
    stimulus_time_separated: bool
    temporal_anchors_created: bool
    temporal_spans_created: bool
    temporal_intervals_created: bool
    temporal_relations_created: bool
    temporal_continuity_created: bool
    external_gap_boundary_created: bool
    stable_data_counted_as_present: bool
    silent_data_counted_as_present: bool
    deterministic_identity_verified: bool
    replay_speed_independence_verified: bool
    stimulus_ground_truth_used_for_compilation: bool
    temporal_sidecar_attached: bool
    temporal_sidecar_read_only: bool
    package_112_score_changed: bool
    memory_write_created: bool
    internal_action_created: bool
    output_intent_created: bool
    subjective_time_claimed: bool
    subjective_duration_claimed: bool
    waiting_semantics_claimed: bool
    rhythm_semantics_claimed: bool
    human_clock_concepts_created: bool
    old_v02_document_modified: bool
    v03_reconciliation_created: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    audit_status: str
    failure_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_schema(self.schema_version, PACKAGE_124A_AUDIT_SCHEMA_VERSION)
        object.__setattr__(self, "failure_reasons", tuple_of_str(self.failure_reasons))

    def to_dict(self) -> dict[str, object]:
        return record_dict(self)
