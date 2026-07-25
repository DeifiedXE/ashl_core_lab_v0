"""Temporal continuity and repeated-structure compilers for Package 124A."""

from __future__ import annotations

from statistics import mean
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import utc_now
from ashl_core_v1.runtime.temporal_types import (
    REPEATED_STRUCTURE_SCHEMA_VERSION,
    TEMPORAL_CONTINUITY_SCHEMA_VERSION,
    RepeatedOccurrenceTemporalStructure,
    TemporalContinuityPrimitive,
    TemporalSpanPrimitive,
    temporal_identity,
)


def compile_temporal_continuity(
    coverage_records: tuple[dict[str, Any], ...],
    *,
    required_lanes: tuple[str, ...] = ("screen", "microphone", "host_state"),
    created_at: str | None = None,
) -> TemporalContinuityPrimitive:
    if not coverage_records:
        payload = {
            "schema_version": TEMPORAL_CONTINUITY_SCHEMA_VERSION,
            "coverage_start_ns": 0,
            "coverage_end_ns": 0,
            "required_lanes": tuple(required_lanes),
            "observed_lanes": tuple(),
            "complete_window_count": 0,
            "incomplete_window_count": 0,
            "partial_edge_window_count": 0,
            "uncovered_gap_count": 0,
            "maximum_uncovered_gap_ns": 0,
            "continuity_status": "indeterminate",
            "stable_data_counted_as_present": True,
            "silent_data_counted_as_present": True,
            "source_alignment_window_refs": tuple(),
            "source_record_refs": tuple(),
            "source_trace_refs": tuple(),
        }
        return TemporalContinuityPrimitive(
            temporal_continuity_id=temporal_identity("temporal_continuity", payload),
            created_at=created_at or utc_now(),
            **payload,
        )
    ordered = tuple(sorted(coverage_records, key=lambda item: (int(item.get("start_event_time_ns") or 0), int(item.get("window_index") or 0))))
    complete = tuple(item for item in ordered if bool(item.get("required_lanes_complete")))
    partial = tuple(item for item in ordered if bool(item.get("partial_edge_window")))
    observed_lanes = _observed_lanes(ordered, required_lanes)
    gaps = []
    previous_end: int | None = None
    for item in ordered:
        start = int(item.get("start_event_time_ns") or 0)
        end = int(item.get("end_event_time_ns") or 0)
        if previous_end is not None and start > previous_end:
            gaps.append(start - previous_end)
        previous_end = max(previous_end or end, end)
    incomplete_count = len(ordered) - len(complete)
    if gaps or incomplete_count:
        status = "continuous_with_partial_edges" if partial and incomplete_count == len(partial) and not gaps else "interrupted"
    else:
        status = "continuous"
    payload = {
        "schema_version": TEMPORAL_CONTINUITY_SCHEMA_VERSION,
        "coverage_start_ns": int(ordered[0].get("start_event_time_ns") or 0),
        "coverage_end_ns": int(max(int(item.get("end_event_time_ns") or 0) for item in ordered)),
        "required_lanes": tuple(required_lanes),
        "observed_lanes": observed_lanes,
        "complete_window_count": len(complete),
        "incomplete_window_count": incomplete_count,
        "partial_edge_window_count": len(partial),
        "uncovered_gap_count": len(gaps),
        "maximum_uncovered_gap_ns": max(gaps) if gaps else 0,
        "continuity_status": status,
        "stable_data_counted_as_present": True,
        "silent_data_counted_as_present": True,
        "source_alignment_window_refs": tuple(str(item.get("alignment_window_id") or "") for item in ordered),
        "source_record_refs": tuple(str(item.get("coverage_record_id") or item.get("alignment_window_id") or "") for item in ordered),
        "source_trace_refs": tuple(dict.fromkeys(ref for item in ordered for ref in tuple(item.get("source_trace_refs") or ()))),
    }
    return TemporalContinuityPrimitive(
        temporal_continuity_id=temporal_identity("temporal_continuity", payload),
        created_at=created_at or utc_now(),
        **payload,
    )


def compile_repeated_occurrence_structure(
    spans: tuple[TemporalSpanPrimitive, ...],
    *,
    created_at: str | None = None,
) -> RepeatedOccurrenceTemporalStructure:
    ordered = tuple(sorted(spans, key=lambda item: (item.start_event_time_ns, item.temporal_span_id)))
    intervals = tuple(
        int(ordered[index + 1].start_event_time_ns) - int(ordered[index].start_event_time_ns)
        for index in range(max(0, len(ordered) - 1))
    )
    durations = tuple(int(item.observed_duration_ns) for item in ordered)
    interval_mean = int(mean(intervals)) if intervals else None
    variation = int(max(intervals) - min(intervals)) if intervals else None
    payload = {
        "schema_version": REPEATED_STRUCTURE_SCHEMA_VERSION,
        "occurrence_refs": tuple(item.temporal_span_id for item in ordered),
        "occurrence_count": len(ordered),
        "inter_onset_intervals_ns": intervals,
        "observed_span_durations_ns": durations,
        "interval_min_ns": min(intervals) if intervals else None,
        "interval_max_ns": max(intervals) if intervals else None,
        "interval_mean_ns": interval_mean,
        "interval_variation_ns": variation,
        "regularity_semantic_label": None,
        "rhythm_semantics_claimed": False,
        "source_record_refs": tuple(dict.fromkeys(ref for item in ordered for ref in item.source_record_refs)),
        "source_trace_refs": tuple(dict.fromkeys(ref for item in ordered for ref in item.source_trace_refs)),
    }
    return RepeatedOccurrenceTemporalStructure(
        repeated_structure_id=temporal_identity("temporal_repeated_structure", payload),
        created_at=created_at or utc_now(),
        **payload,
    )


def _observed_lanes(records: tuple[dict[str, Any], ...], required_lanes: tuple[str, ...]) -> tuple[str, ...]:
    present: list[str] = []
    for lane in required_lanes:
        for item in records:
            key = "audio" if lane == "microphone" else lane
            lane_payload = item.get(key) or {}
            if lane_payload.get("source_artifact_present") or lane_payload.get("compiled_primitive_present"):
                present.append(lane)
                break
    return tuple(dict.fromkeys(present))
