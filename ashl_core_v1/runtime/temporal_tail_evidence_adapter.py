"""Incremental temporal-tail evidence adapter for Package 125."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.observation_window_types import (
    DEFAULT_TAIL_GUARD_NS,
    OPEN_TEMPORAL_REGION_SCHEMA_VERSION,
    REQUIRED_LANES,
    TEMPORAL_REGION_CLOSURE_LINK_SCHEMA_VERSION,
    TEMPORAL_TAIL_EVIDENCE_SCHEMA_VERSION,
    ObservationWindowState,
    OpenTemporalRegionObservation,
    TemporalRegionClosureLink,
    TemporalTailEvidenceRecord,
)
from ashl_core_v1.runtime.temporal_relation_compiler import build_temporal_anchor, build_temporal_span
from ashl_core_v1.runtime.temporal_types import temporal_identity


@dataclass(frozen=True)
class TemporalTailEvidenceResult:
    tail_evidence: TemporalTailEvidenceRecord
    open_regions: tuple[OpenTemporalRegionObservation, ...]
    clock_domain_id: str


def build_temporal_tail_evidence(
    *,
    observation_window: ObservationWindowState,
    coverage_records: tuple[Any, ...] | list[Any],
    temporal_bundle_or_context_id: str,
    evaluated_at_event_time_ns: int,
    tail_guard_ns: int = DEFAULT_TAIL_GUARD_NS,
    clock_domain_id: str = "package_125_same_process_clock_domain",
    backpressure_fault_count: int = 0,
) -> TemporalTailEvidenceResult:
    """Build structural tail evidence from actual Package 123 coverage rows.

    The function consumes alignment coverage records only. It does not accept or
    read a stimulus manifest, so candidate creation cannot depend on schedule
    ground truth.
    """

    payloads = tuple(_payload(item) for item in coverage_records)
    records = tuple(
        sorted(
            (
                item
                for item in payloads
                if not observation_window.experiment_run_id
                or str(item.get("experiment_run_id") or "") == observation_window.experiment_run_id
            ),
            key=lambda item: int(item.get("window_index", 0)),
        )
    )
    deadline = int(observation_window.current_deadline_event_time_ns)
    eval_time = int(evaluated_at_event_time_ns)
    remaining = max(0, deadline - eval_time)
    in_scope = tuple(item for item in records if int(item.get("end_event_time_ns", 0)) <= deadline)
    tail_start = max(0, deadline - int(tail_guard_ns))
    tail_records = tuple(item for item in in_scope if int(item.get("end_event_time_ns", 0)) > tail_start)
    open_regions: list[OpenTemporalRegionObservation] = []
    onset_refs: list[str] = []
    for lane, key, region_kind in (
        ("screen", "screen", "observed_change_region"),
        ("microphone", "audio", "observed_energy_region"),
    ):
        region = _open_region_from_tail(
            tail_records,
            lane=lane,
            coverage_key=key,
            region_kind=region_kind,
            deadline=deadline,
            clock_domain_id=clock_domain_id,
            observation_window=observation_window,
        )
        if region is not None:
            open_regions.append(region)
            onset_refs.append(region.start_anchor_id)
    capture_failures = sum(_lane_count(item, "capture_failure_count") for item in in_scope)
    compile_failures = sum(_lane_count(item, "compile_failure_count") for item in in_scope)
    dropped = sum(_lane_count(item, "dropped_record_count") for item in in_scope)
    complete = all(bool(item.get("required_lanes_complete")) for item in in_scope if _full_window(item))
    continuous = bool(in_scope) and complete
    source_records = tuple(
        dict.fromkeys(
            tuple(str(item.get("coverage_record_id") or item.get("alignment_window_id") or "") for item in tail_records)
            + tuple(ref for region in open_regions for ref in region.source_record_refs)
        )
    )
    source_traces = tuple(dict.fromkeys(ref for item in tail_records for ref in tuple(item.get("source_trace_refs") or ())))
    evidence_payload = {
        "schema_version": TEMPORAL_TAIL_EVIDENCE_SCHEMA_VERSION,
        "observation_window_id": observation_window.observation_window_id,
        "temporal_bundle_or_context_id": temporal_bundle_or_context_id,
        "evaluated_at_event_time_ns": eval_time,
        "current_deadline_event_time_ns": deadline,
        "remaining_window_ns": remaining,
        "open_visual_region_refs": tuple(item.open_region_observation_id for item in open_regions if item.source_lane == "screen"),
        "open_audio_region_refs": tuple(item.open_region_observation_id for item in open_regions if item.source_lane == "microphone"),
        "recent_onset_anchor_refs": tuple(onset_refs),
        "continuous_source_coverage": continuous,
        "required_lane_delivery_complete": complete,
        "capture_failure_count": capture_failures,
        "compile_failure_count": compile_failures,
        "dropped_required_record_count": dropped,
        "backpressure_fault_count": int(backpressure_fault_count),
        "semantic_label": None,
        "structural_tail_only": True,
        "source_record_refs": tuple(ref for ref in source_records if ref),
        "source_trace_refs": source_traces,
        "runtime_session_id": observation_window.runtime_session_id,
        "perception_session_id": observation_window.perception_session_id,
        "experiment_run_id": observation_window.experiment_run_id,
        "audit_group_id": observation_window.audit_group_id,
        "scenario_name": observation_window.scenario_name,
        "active_capture_identity_id": observation_window.active_capture_identity_id,
    }
    evidence = TemporalTailEvidenceRecord(
        temporal_tail_evidence_id=temporal_identity("temporal_tail_evidence", evidence_payload),
        created_at=utc_now(),
        **evidence_payload,
    )
    return TemporalTailEvidenceResult(evidence, tuple(open_regions), clock_domain_id)


def build_closure_links(
    *,
    open_regions: tuple[OpenTemporalRegionObservation, ...],
    coverage_records: tuple[Any, ...] | list[Any],
    base_deadline_event_time_ns: int,
    final_deadline_event_time_ns: int,
    clock_domain_id: str = "package_125_same_process_clock_domain",
    compiled_temporal_records: list[Any] | None = None,
) -> tuple[TemporalRegionClosureLink, ...]:
    payloads = tuple(_payload(item) for item in coverage_records)
    expected_run_ids = {item.experiment_run_id for item in open_regions if item.experiment_run_id}
    records = tuple(
        sorted(
            (
                item
                for item in payloads
                if not expected_run_ids or str(item.get("experiment_run_id") or "") in expected_run_ids
            ),
            key=lambda item: int(item.get("window_index", 0)),
        )
    )
    links: list[TemporalRegionClosureLink] = []
    for region in open_regions:
        key = "screen" if region.source_lane == "screen" else "audio"
        closing = None
        for item in records:
            start = int(item.get("start_event_time_ns", 0))
            end = int(item.get("end_event_time_ns", 0))
            if start < int(base_deadline_event_time_ns) or end > int(final_deadline_event_time_ns):
                continue
            if not bool((_lane(item, key)).get("salient_change_present")):
                closing = item
                break
        if closing is None:
            continue
        closure_time = int(closing.get("start_event_time_ns", base_deadline_event_time_ns))
        start_anchor = build_temporal_anchor(
            source_record_id=region.open_region_observation_id,
            source_record_kind="open_temporal_region_observation",
            source_lane=region.source_lane,
            clock_domain_id=clock_domain_id,
            normalized_event_time_ns=region.start_event_time_ns,
            source_native_time_ns=region.start_event_time_ns,
            event_sequence_index=None,
            source_record_refs=region.source_record_refs,
            source_trace_refs=region.source_trace_refs,
        )
        closure_anchor = build_temporal_anchor(
            source_record_id=str(closing.get("alignment_window_id") or closing.get("coverage_record_id")),
            source_record_kind="package_123_alignment_window_coverage",
            source_lane=region.source_lane,
            clock_domain_id=clock_domain_id,
            normalized_event_time_ns=closure_time,
            source_native_time_ns=closure_time,
            event_sequence_index=int(closing.get("window_index", 0)) * 2,
            source_record_refs=(str(closing.get("coverage_record_id") or closing.get("alignment_window_id")),),
            source_trace_refs=tuple(closing.get("source_trace_refs") or ()),
        )
        span = build_temporal_span(
            span_kind=region.region_kind,
            start_anchor=start_anchor,
            end_anchor=closure_anchor,
            source_lane=region.source_lane,
            source_region_refs=(region.open_region_observation_id,),
            source_record_refs=tuple(dict.fromkeys(region.source_record_refs + (str(closing.get("coverage_record_id") or ""),))),
            source_trace_refs=tuple(dict.fromkeys(region.source_trace_refs + tuple(closing.get("source_trace_refs") or ()))),
        )
        if compiled_temporal_records is not None:
            compiled_temporal_records.extend((start_anchor, closure_anchor, span))
        payload = {
            "open_region_observation_id": region.open_region_observation_id,
            "finalized_temporal_span_id": span.temporal_span_id,
            "closure_anchor_id": closure_anchor.temporal_anchor_id,
            "closure_event_time_ns": closure_time,
            "source_trace_refs": tuple(dict.fromkeys(region.source_trace_refs + tuple(closing.get("source_trace_refs") or ()))),
        }
        links.append(
            TemporalRegionClosureLink(
                closure_link_id=temporal_identity("temporal_region_closure_link", payload),
                created_at=utc_now(),
                observation_window_id=region.observation_window_id,
                runtime_session_id=region.runtime_session_id,
                perception_session_id=region.perception_session_id,
                experiment_run_id=region.experiment_run_id,
                audit_group_id=region.audit_group_id,
                scenario_name=region.scenario_name,
                **payload,
            )
        )
    return tuple(links)


def _open_region_from_tail(
    records: tuple[dict[str, Any], ...],
    *,
    lane: str,
    coverage_key: str,
    region_kind: str,
    deadline: int,
    clock_domain_id: str,
    observation_window: ObservationWindowState,
) -> OpenTemporalRegionObservation | None:
    salient = tuple(item for item in records if bool((_lane(item, coverage_key)).get("salient_change_present")))
    if not salient:
        return None
    last = records[-1] if records else salient[-1]
    if not bool((_lane(last, coverage_key)).get("salient_change_present")):
        return None
    start = salient[0]
    latest = salient[-1]
    start_anchor = build_temporal_anchor(
        source_record_id=str(start.get("alignment_window_id") or start.get("coverage_record_id")),
        source_record_kind="package_123_alignment_window_coverage",
        source_lane=lane,
        clock_domain_id=clock_domain_id,
        normalized_event_time_ns=int(start.get("start_event_time_ns", 0)),
        source_native_time_ns=int(start.get("start_event_time_ns", 0)),
        event_sequence_index=int(start.get("window_index", 0)) * 2,
        source_record_refs=(str(start.get("coverage_record_id") or start.get("alignment_window_id")),),
        source_trace_refs=tuple(start.get("source_trace_refs") or ()),
    )
    latest_anchor = build_temporal_anchor(
        source_record_id=str(latest.get("alignment_window_id") or latest.get("coverage_record_id")),
        source_record_kind="package_123_alignment_window_coverage",
        source_lane=lane,
        clock_domain_id=clock_domain_id,
        normalized_event_time_ns=min(deadline, int(latest.get("end_event_time_ns", deadline))),
        source_native_time_ns=min(deadline, int(latest.get("end_event_time_ns", deadline))),
        event_sequence_index=int(latest.get("window_index", 0)) * 2 + 1,
        source_record_refs=(str(latest.get("coverage_record_id") or latest.get("alignment_window_id")),),
        source_trace_refs=tuple(latest.get("source_trace_refs") or ()),
    )
    payload = {
        "schema_version": OPEN_TEMPORAL_REGION_SCHEMA_VERSION,
        "source_lane": lane,
        "region_kind": region_kind,
        "start_anchor_id": start_anchor.temporal_anchor_id,
        "latest_observed_anchor_id": latest_anchor.temporal_anchor_id,
        "start_event_time_ns": int(start.get("start_event_time_ns", 0)),
        "latest_observed_event_time_ns": min(deadline, int(latest.get("end_event_time_ns", deadline))),
        "observed_offset_present": False,
        "open_at_current_boundary": True,
        "provisional_only": True,
        "source_record_refs": tuple(str(item.get("coverage_record_id") or item.get("alignment_window_id")) for item in salient),
        "source_trace_refs": tuple(dict.fromkeys(ref for item in salient for ref in tuple(item.get("source_trace_refs") or ()))),
        "observation_window_id": observation_window.observation_window_id,
        "runtime_session_id": observation_window.runtime_session_id,
        "perception_session_id": observation_window.perception_session_id,
        "experiment_run_id": observation_window.experiment_run_id,
        "audit_group_id": observation_window.audit_group_id,
        "scenario_name": observation_window.scenario_name,
    }
    return OpenTemporalRegionObservation(
        open_region_observation_id=temporal_identity("open_temporal_region", payload),
        created_at=utc_now(),
        **payload,
    )


def _payload(record: Any) -> dict[str, Any]:
    if hasattr(record, "to_dict"):
        return dict(record.to_dict())
    return dict(record)


def _lane(record: dict[str, Any], key: str) -> dict[str, Any]:
    return dict(record.get(key) or {})


def _lane_count(record: dict[str, Any], field_name: str) -> int:
    total = 0
    for key in ("screen", "audio", "host_state"):
        total += int((_lane(record, key)).get(field_name) or 0)
    return total


def _full_window(record: dict[str, Any]) -> bool:
    return bool(record.get("full_window_inside_common_envelope", True))
