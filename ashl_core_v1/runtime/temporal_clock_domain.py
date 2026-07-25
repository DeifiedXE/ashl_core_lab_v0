"""Clock-domain helpers for grounded temporal primitives."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import utc_now
from ashl_core_v1.runtime.temporal_types import (
    ACTION_ORDINAL_SCHEMA_VERSION,
    CLOCK_DOMAIN_SCHEMA_VERSION,
    CLOCK_QUALITY_SCHEMA_VERSION,
    EXTERNAL_GAP_SCHEMA_VERSION,
    TEMPORAL_ORDERING_DIAGNOSTIC_SCHEMA_VERSION,
    ActionOrdinalPosition,
    CrossProcessExternalGapRecord,
    TemporalClockDomainDescriptor,
    TemporalClockQualityRecord,
    TemporalOrderingDiagnostic,
    temporal_identity,
)


DEFAULT_MONOTONIC_RESOLUTION_NS = 1
DEFAULT_UNCERTAINTY_NS = 1_000_000


def parse_utc(value: str) -> datetime:
    normalized = str(value).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("UTC timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def build_clock_domain_descriptor(
    *,
    process_instance_id: str,
    operating_system_process_id: int,
    utc_anchor: str,
    utc_anchor_monotonic_ns: int,
    monotonic_origin_ns: int = 0,
    operating_system_boot_identity: str | None = None,
    nominal_resolution_ns: int = DEFAULT_MONOTONIC_RESOLUTION_NS,
    measured_uncertainty_ns: int = DEFAULT_UNCERTAINTY_NS,
    comparable_across_processes: bool = True,
    source_trace_refs: tuple[str, ...] = tuple(),
    created_at: str | None = None,
) -> TemporalClockDomainDescriptor:
    parse_utc(utc_anchor)
    payload = {
        "schema_version": CLOCK_DOMAIN_SCHEMA_VERSION,
        "process_instance_id": process_instance_id,
        "operating_system_process_id": int(operating_system_process_id),
        "monotonic_clock_kind": "python_time_monotonic_ns",
        "monotonic_origin_ns": int(monotonic_origin_ns),
        "utc_anchor": utc_anchor,
        "utc_anchor_monotonic_ns": int(utc_anchor_monotonic_ns),
        "operating_system_boot_identity": operating_system_boot_identity,
        "nominal_resolution_ns": int(nominal_resolution_ns),
        "measured_uncertainty_ns": int(measured_uncertainty_ns),
        "comparable_within_process": True,
        "comparable_across_processes": bool(comparable_across_processes),
        "cross_process_comparison_method": "persisted_utc_anchor_with_recorded_uncertainty",
        "source_trace_refs": tuple(source_trace_refs),
    }
    return TemporalClockDomainDescriptor(
        clock_domain_id=temporal_identity("temporal_clock_domain", payload),
        created_at=created_at or utc_now(),
        **payload,
    )


def evaluate_clock_quality(
    clock_domain: TemporalClockDomainDescriptor,
    observed_event_times_ns: tuple[int, ...],
    *,
    comparison_uncertainty_ns: int | None = None,
    created_at: str | None = None,
) -> TemporalClockQualityRecord:
    failures: list[str] = []
    try:
        parse_utc(clock_domain.utc_anchor)
        utc_anchor_valid = True
    except Exception:
        utc_anchor_valid = False
        failures.append("utc_anchor_invalid")
    monotonic_non_decreasing = all(
        int(observed_event_times_ns[index]) <= int(observed_event_times_ns[index + 1])
        for index in range(max(0, len(observed_event_times_ns) - 1))
    )
    if not monotonic_non_decreasing:
        failures.append("monotonic_time_decreased")
    uncertainty = int(comparison_uncertainty_ns if comparison_uncertainty_ns is not None else clock_domain.measured_uncertainty_ns)
    status = "verified" if utc_anchor_valid and monotonic_non_decreasing and uncertainty <= 1_000_000 else "verified_with_uncertainty"
    if not utc_anchor_valid or not monotonic_non_decreasing:
        status = "invalid"
    payload = {
        "schema_version": CLOCK_QUALITY_SCHEMA_VERSION,
        "clock_domain_id": clock_domain.clock_domain_id,
        "monotonic_non_decreasing": monotonic_non_decreasing,
        "utc_anchor_valid": utc_anchor_valid,
        "wall_clock_backward_jump_detected": False,
        "wall_clock_forward_jump_detected": False,
        "maximum_observed_clock_drift_ns": None,
        "comparison_uncertainty_ns": uncertainty,
        "quality_status": status,
        "failure_reasons": tuple(failures),
    }
    return TemporalClockQualityRecord(
        clock_quality_id=temporal_identity("temporal_clock_quality", payload),
        created_at=created_at or utc_now(),
        **payload,
    )


def build_cross_process_external_gap(
    *,
    previous_process_instance_id: str,
    current_process_instance_id: str,
    previous_last_event_utc: str,
    current_first_event_utc: str,
    previous_clock_domain_id: str,
    current_clock_domain_id: str,
    comparison_uncertainty_ns: int = DEFAULT_UNCERTAINTY_NS,
    source_record_refs: tuple[str, ...] = tuple(),
    source_trace_refs: tuple[str, ...] = tuple(),
    created_at: str | None = None,
) -> CrossProcessExternalGapRecord:
    failure = False
    wall_clock_adjustment = False
    external_gap_ns: int | None
    try:
        previous_utc = parse_utc(previous_last_event_utc)
        current_utc = parse_utc(current_first_event_utc)
        external_gap_ns = int((current_utc - previous_utc).total_seconds() * 1_000_000_000)
        if external_gap_ns < 0:
            wall_clock_adjustment = True
            failure = True
            external_gap_ns = None
    except Exception:
        failure = True
        external_gap_ns = None
    status = "indeterminate_clock_change" if failure else "measured_with_uncertainty" if comparison_uncertainty_ns else "measured_external_gap"
    payload = {
        "schema_version": EXTERNAL_GAP_SCHEMA_VERSION,
        "previous_process_instance_id": previous_process_instance_id,
        "current_process_instance_id": current_process_instance_id,
        "previous_last_event_utc": previous_last_event_utc,
        "current_first_event_utc": current_first_event_utc,
        "external_gap_ns": external_gap_ns,
        "comparison_uncertainty_ns": int(comparison_uncertainty_ns),
        "previous_clock_domain_id": previous_clock_domain_id,
        "current_clock_domain_id": current_clock_domain_id,
        "wall_clock_adjustment_detected": wall_clock_adjustment,
        "gap_status": status,
        "discovered_after_resume": True,
        "experienced_during_gap": False,
        "synthetic_ticks_created": False,
        "source_record_refs": tuple(source_record_refs),
        "source_trace_refs": tuple(source_trace_refs),
    }
    return CrossProcessExternalGapRecord(
        external_gap_id=temporal_identity("cross_process_external_gap", payload),
        created_at=created_at or utc_now(),
        **payload,
    )


def build_action_ordinal_position(action_tick: int, session_id: str) -> ActionOrdinalPosition:
    return ActionOrdinalPosition(
        schema_version=ACTION_ORDINAL_SCHEMA_VERSION,
        action_tick=int(action_tick),
        session_id=session_id,
        elapsed_time_claimed=False,
    )


def build_ordering_diagnostics(records: tuple[dict[str, Any], ...]) -> tuple[TemporalOrderingDiagnostic, ...]:
    """Detect processing/event-time order disagreement without rewriting history."""
    diagnostics: list[TemporalOrderingDiagnostic] = []
    ordered_by_sequence = sorted(
        records,
        key=lambda item: (
            int(item.get("event_sequence_index", item.get("sequence_index", 0)) or 0),
            str(item.get("source_record_id") or item.get("record_id") or ""),
        ),
    )
    previous_event_time: int | None = None
    previous_processing_time: int | None = None
    for item in ordered_by_sequence:
        event_time = int(item.get("event_time_ns", item.get("normalized_event_time_ns", 0)) or 0)
        processing_time = item.get("processing_time_ns")
        processing_time = int(processing_time) if processing_time is not None else None
        disagree = False
        if previous_event_time is not None and previous_processing_time is not None and processing_time is not None:
            disagree = event_time < previous_event_time and processing_time >= previous_processing_time
        if previous_event_time is not None and event_time < previous_event_time:
            disagree = True
        status = "processing_order_disagrees_with_event_time" if disagree else "ok"
        payload = {
            "schema_version": TEMPORAL_ORDERING_DIAGNOSTIC_SCHEMA_VERSION,
            "source_record_id": str(item.get("source_record_id") or item.get("record_id") or ""),
            "event_sequence_index": item.get("event_sequence_index", item.get("sequence_index")),
            "event_time_ns": event_time,
            "processing_time_ns": processing_time,
            "event_order_processing_order_disagree": disagree,
            "diagnostic_status": status,
        }
        diagnostics.append(
            TemporalOrderingDiagnostic(
                diagnostic_id=temporal_identity("temporal_ordering_diagnostic", payload),
                **payload,
            )
        )
        previous_event_time = event_time
        if processing_time is not None:
            previous_processing_time = processing_time
    return tuple(diagnostics)
