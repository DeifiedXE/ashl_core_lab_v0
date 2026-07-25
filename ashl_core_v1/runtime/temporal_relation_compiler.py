"""Span, interval and relation compilers for Package 124A."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import utc_now
from ashl_core_v1.runtime.temporal_types import (
    TEMPORAL_ANCHOR_SCHEMA_VERSION,
    TEMPORAL_INTERVAL_SCHEMA_VERSION,
    TEMPORAL_RELATION_SCHEMA_VERSION,
    TEMPORAL_SPAN_SCHEMA_VERSION,
    TemporalEventAnchor,
    TemporalIntervalPrimitive,
    TemporalRelationKind,
    TemporalRelationPrimitive,
    TemporalSpanPrimitive,
    temporal_identity,
)


def build_temporal_anchor(
    *,
    source_record_id: str,
    source_record_kind: str,
    source_lane: str,
    clock_domain_id: str,
    normalized_event_time_ns: int,
    source_native_time_ns: int | None = None,
    processing_time_ns: int | None = None,
    replay_submission_time_ns: int | None = None,
    event_sequence_index: int | None = None,
    action_tick: int | None = None,
    timestamp_resolution_ns: int = 1,
    timestamp_uncertainty_ns: int = 1_000_000,
    source_record_refs: tuple[str, ...] = tuple(),
    source_trace_refs: tuple[str, ...] = tuple(),
) -> TemporalEventAnchor:
    payload = {
        "schema_version": TEMPORAL_ANCHOR_SCHEMA_VERSION,
        "source_record_id": source_record_id,
        "source_record_kind": source_record_kind,
        "source_lane": source_lane,
        "clock_domain_id": clock_domain_id,
        "source_native_time_ns": source_native_time_ns,
        "normalized_event_time_ns": int(normalized_event_time_ns),
        "processing_time_ns": processing_time_ns,
        "replay_submission_time_ns": replay_submission_time_ns,
        "event_sequence_index": event_sequence_index,
        "action_tick": action_tick,
        "timestamp_resolution_ns": int(timestamp_resolution_ns),
        "timestamp_uncertainty_ns": int(timestamp_uncertainty_ns),
        "source_record_refs": tuple(source_record_refs or (source_record_id,)),
        "source_trace_refs": tuple(source_trace_refs),
    }
    identity_payload = {key: value for key, value in payload.items() if key not in {"processing_time_ns", "replay_submission_time_ns"}}
    return TemporalEventAnchor(
        temporal_anchor_id=temporal_identity("temporal_anchor", identity_payload),
        **payload,
    )


def build_temporal_span(
    *,
    span_kind: str,
    start_anchor: TemporalEventAnchor,
    end_anchor: TemporalEventAnchor,
    source_lane: str | None = None,
    source_region_refs: tuple[str, ...] = tuple(),
    source_record_refs: tuple[str, ...] = tuple(),
    source_trace_refs: tuple[str, ...] = tuple(),
    created_at: str | None = None,
) -> TemporalSpanPrimitive:
    start = int(start_anchor.normalized_event_time_ns)
    end = int(end_anchor.normalized_event_time_ns)
    payload = {
        "schema_version": TEMPORAL_SPAN_SCHEMA_VERSION,
        "span_kind": span_kind,
        "start_anchor_id": start_anchor.temporal_anchor_id,
        "end_anchor_id": end_anchor.temporal_anchor_id,
        "start_event_time_ns": start,
        "end_event_time_ns": end,
        "observed_duration_ns": end - start,
        "measurement_resolution_ns": max(start_anchor.timestamp_resolution_ns, end_anchor.timestamp_resolution_ns),
        "measurement_uncertainty_ns": max(start_anchor.timestamp_uncertainty_ns, end_anchor.timestamp_uncertainty_ns),
        "source_lane": source_lane,
        "source_region_refs": tuple(source_region_refs),
        "semantic_label": None,
        "subjective_duration_claimed": False,
        "source_record_refs": tuple(source_record_refs or tuple(dict.fromkeys(start_anchor.source_record_refs + end_anchor.source_record_refs))),
        "source_trace_refs": tuple(source_trace_refs or tuple(dict.fromkeys(start_anchor.source_trace_refs + end_anchor.source_trace_refs))),
    }
    return TemporalSpanPrimitive(
        temporal_span_id=temporal_identity("temporal_span", payload),
        created_at=created_at or utc_now(),
        **payload,
    )


def build_temporal_interval(
    *,
    interval_kind: str,
    left_anchor: TemporalEventAnchor,
    right_anchor: TemporalEventAnchor,
    source_record_refs: tuple[str, ...] = tuple(),
    source_trace_refs: tuple[str, ...] = tuple(),
    created_at: str | None = None,
) -> TemporalIntervalPrimitive:
    left = int(left_anchor.normalized_event_time_ns)
    right = int(right_anchor.normalized_event_time_ns)
    payload = {
        "schema_version": TEMPORAL_INTERVAL_SCHEMA_VERSION,
        "interval_kind": interval_kind,
        "left_anchor_id": left_anchor.temporal_anchor_id,
        "right_anchor_id": right_anchor.temporal_anchor_id,
        "left_event_time_ns": left,
        "right_event_time_ns": right,
        "interval_ns": right - left,
        "measurement_resolution_ns": max(left_anchor.timestamp_resolution_ns, right_anchor.timestamp_resolution_ns),
        "measurement_uncertainty_ns": max(left_anchor.timestamp_uncertainty_ns, right_anchor.timestamp_uncertainty_ns),
        "semantic_label": None,
        "source_record_refs": tuple(source_record_refs or tuple(dict.fromkeys(left_anchor.source_record_refs + right_anchor.source_record_refs))),
        "source_trace_refs": tuple(source_trace_refs or tuple(dict.fromkeys(left_anchor.source_trace_refs + right_anchor.source_trace_refs))),
    }
    return TemporalIntervalPrimitive(
        temporal_interval_id=temporal_identity("temporal_interval", payload),
        created_at=created_at or utc_now(),
        **payload,
    )


def derive_temporal_relation(
    left: TemporalSpanPrimitive,
    right: TemporalSpanPrimitive,
    *,
    comparison_tolerance_ns: int = 1_000_000,
    created_at: str | None = None,
) -> TemporalRelationPrimitive:
    ls = int(left.start_event_time_ns)
    le = int(left.end_event_time_ns)
    rs = int(right.start_event_time_ns)
    re = int(right.end_event_time_ns)
    tolerance = int(comparison_tolerance_ns)
    overlap = max(0, min(le, re) - max(ls, rs))
    if abs(ls - rs) <= tolerance and abs(le - re) <= tolerance:
        kind = TemporalRelationKind.EQUAL_SPAN.value
        gap_ns = 0
        overlap_ns = overlap
    elif ls <= rs and le >= re:
        kind = TemporalRelationKind.CONTAINS.value
        gap_ns = 0
        overlap_ns = overlap
    elif rs <= ls and re >= le:
        kind = TemporalRelationKind.DURING.value
        gap_ns = 0
        overlap_ns = overlap
    elif overlap > 0:
        kind = TemporalRelationKind.OVERLAPS.value
        gap_ns = 0
        overlap_ns = overlap
    elif abs(le - rs) <= tolerance or abs(re - ls) <= tolerance:
        kind = TemporalRelationKind.MEETS.value
        gap_ns = 0
        overlap_ns = 0
    elif le < rs - tolerance:
        kind = TemporalRelationKind.BEFORE.value
        gap_ns = rs - le
        overlap_ns = 0
    else:
        kind = TemporalRelationKind.AFTER.value
        gap_ns = ls - re
        overlap_ns = 0
    confidence = 1.0 if max(left.measurement_uncertainty_ns, right.measurement_uncertainty_ns) <= tolerance else 0.75
    payload = {
        "schema_version": TEMPORAL_RELATION_SCHEMA_VERSION,
        "relation_kind": kind,
        "left_temporal_ref": left.temporal_span_id,
        "right_temporal_ref": right.temporal_span_id,
        "gap_ns": gap_ns,
        "overlap_ns": overlap_ns,
        "comparison_tolerance_ns": tolerance,
        "relation_confidence": confidence,
        "relation_uncertainty_ns": max(left.measurement_uncertainty_ns, right.measurement_uncertainty_ns, tolerance),
        "semantic_label": None,
        "source_record_refs": tuple(dict.fromkeys(left.source_record_refs + right.source_record_refs)),
        "source_trace_refs": tuple(dict.fromkeys(left.source_trace_refs + right.source_trace_refs)),
    }
    return TemporalRelationPrimitive(
        temporal_relation_id=temporal_identity("temporal_relation", payload),
        created_at=created_at or utc_now(),
        **payload,
    )


def derive_repeated_onset_intervals(
    spans: tuple[TemporalSpanPrimitive, ...],
    anchors_by_id: dict[str, TemporalEventAnchor],
    *,
    interval_kind: str = "onset_to_onset",
) -> tuple[TemporalIntervalPrimitive, ...]:
    ordered = tuple(sorted(spans, key=lambda item: (item.start_event_time_ns, item.temporal_span_id)))
    intervals: list[TemporalIntervalPrimitive] = []
    for index in range(max(0, len(ordered) - 1)):
        left = anchors_by_id[ordered[index].start_anchor_id]
        right = anchors_by_id[ordered[index + 1].start_anchor_id]
        intervals.append(build_temporal_interval(interval_kind=interval_kind, left_anchor=left, right_anchor=right))
    return tuple(intervals)


def derive_offset_to_onset_intervals(
    spans: tuple[TemporalSpanPrimitive, ...],
    anchors_by_id: dict[str, TemporalEventAnchor],
) -> tuple[TemporalIntervalPrimitive, ...]:
    ordered = tuple(sorted(spans, key=lambda item: (item.start_event_time_ns, item.temporal_span_id)))
    intervals: list[TemporalIntervalPrimitive] = []
    for index in range(max(0, len(ordered) - 1)):
        left = anchors_by_id[ordered[index].end_anchor_id]
        right = anchors_by_id[ordered[index + 1].start_anchor_id]
        intervals.append(build_temporal_interval(interval_kind="offset_to_onset", left_anchor=left, right_anchor=right))
    return tuple(intervals)
