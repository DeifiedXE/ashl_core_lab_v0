"""Compiler from Package 124 archive evidence to grounded temporal primitives."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.runtime.package_124_archive import verify_package_124_archive
from ashl_core_v1.runtime.package_124_types import PACKAGE_123_CYCLE_1_SESSION_ID, PACKAGE_123_CYCLE_2_SESSION_ID
from ashl_core_v1.runtime.package_124a_temporal_store import Package124ATemporalStore
from ashl_core_v1.runtime.temporal_clock_domain import (
    build_clock_domain_descriptor,
    build_cross_process_external_gap,
    evaluate_clock_quality,
)
from ashl_core_v1.runtime.temporal_context_sidecar import attach_temporal_context_sidecar
from ashl_core_v1.runtime.temporal_continuity_compiler import (
    compile_repeated_occurrence_structure,
    compile_temporal_continuity,
)
from ashl_core_v1.runtime.temporal_relation_compiler import (
    build_temporal_anchor,
    build_temporal_interval,
    build_temporal_span,
    derive_offset_to_onset_intervals,
    derive_repeated_onset_intervals,
    derive_temporal_relation,
)
from ashl_core_v1.runtime.temporal_types import (
    EXTERNAL_GAP_SCHEMA_VERSION,
    RUNTIME_STATE_SPAN_SCHEMA_VERSION,
    TEMPORAL_BUNDLE_SCHEMA_VERSION,
    TEMPORAL_CALIBRATION_AUDIT_SCHEMA_VERSION,
    GroundedTemporalPrimitiveBundle,
    RuntimeStateTemporalSpan,
    TemporalCalibrationAuditRecord,
    TemporalClockDomainDescriptor,
    TemporalClockQualityRecord,
    TemporalContinuityPrimitive,
    TemporalEventAnchor,
    TemporalIntervalPrimitive,
    TemporalPerceptionContextSidecar,
    TemporalRelationPrimitive,
    TemporalSpanPrimitive,
    RepeatedOccurrenceTemporalStructure,
    temporal_identity,
)


DEFAULT_PACKAGE_124_ARCHIVE = Path(
    r"C:\Users\zxc12\AppData\Local\ASHLCore\milestones\package_124_real_host_perception_growth_loop_v0_f31811e589acc322"
)
SOURCE_STATE_DIRNAME = "source_state"
REQUIRED_LANES = ("screen", "microphone", "host_state")


@dataclass(frozen=True)
class Package124ATemporalCompilationResult:
    archive_dir: str
    archive_verified: bool
    archive_opened_read_only: bool
    archive_fingerprint_before: str
    archive_fingerprint_after: str
    clock_domains: tuple[TemporalClockDomainDescriptor, ...]
    clock_quality_records: tuple[TemporalClockQualityRecord, ...]
    anchors: tuple[TemporalEventAnchor, ...]
    spans: tuple[TemporalSpanPrimitive, ...]
    intervals: tuple[TemporalIntervalPrimitive, ...]
    relations: tuple[TemporalRelationPrimitive, ...]
    continuity_records: tuple[TemporalContinuityPrimitive, ...]
    repeated_structures: tuple[RepeatedOccurrenceTemporalStructure, ...]
    runtime_state_spans: tuple[RuntimeStateTemporalSpan, ...]
    external_gaps: tuple[Any, ...]
    temporal_bundle: GroundedTemporalPrimitiveBundle
    temporal_sidecars: tuple[TemporalPerceptionContextSidecar, ...]
    source_coverage_records: tuple[dict[str, Any], ...]
    source_cycle_records: tuple[dict[str, Any], ...]
    replay_speed: float

    @property
    def archive_modified(self) -> bool:
        return self.archive_fingerprint_before != self.archive_fingerprint_after

    def identity_signature(self) -> dict[str, object]:
        return {
            "clock_domain_ids": tuple(item.clock_domain_id for item in self.clock_domains),
            "anchor_ids": tuple(item.temporal_anchor_id for item in self.anchors),
            "span_ids": tuple(item.temporal_span_id for item in self.spans),
            "interval_ids": tuple(item.temporal_interval_id for item in self.intervals),
            "relation_ids": tuple(item.temporal_relation_id for item in self.relations),
            "continuity_ids": tuple(item.temporal_continuity_id for item in self.continuity_records),
            "repeated_structure_ids": tuple(item.repeated_structure_id for item in self.repeated_structures),
            "external_gap_ids": tuple(item.external_gap_id for item in self.external_gaps),
            "temporal_bundle_id": self.temporal_bundle.temporal_bundle_id,
            "temporal_values_sha256": sha256_payload(
                {
                    "anchors": [_stable_record_payload(item, clear=("processing_time_ns", "replay_submission_time_ns")) for item in self.anchors],
                    "spans": [_stable_record_payload(item) for item in self.spans],
                    "intervals": [_stable_record_payload(item) for item in self.intervals],
                    "relations": [_stable_record_payload(item) for item in self.relations],
                    "continuity": [_stable_record_payload(item) for item in self.continuity_records],
                }
            ),
        }


def compile_package_124_archive_temporal_bundle(
    *,
    archive_dir: str | Path = DEFAULT_PACKAGE_124_ARCHIVE,
    state_dir: str | Path | None = None,
    replay_speed: float = 1.0,
    persist: bool = True,
    verify_archive: bool = True,
) -> Package124ATemporalCompilationResult:
    if replay_speed <= 0:
        raise ValueError("replay_speed must be positive")
    archive = Path(archive_dir).resolve()
    fingerprint_before = archive_tree_fingerprint(archive)
    verification = verify_package_124_archive(archive) if verify_archive else {"valid": True, "status": "preverified_read_only_archive"}
    evidence = read_package_124_temporal_evidence(archive)
    cycle_one = evidence["cycle_one"]
    cycle_two = evidence["cycle_two"]
    coverage = tuple(evidence["coverage"])

    clock_one = build_clock_domain_descriptor(
        process_instance_id=str(cycle_one["process_instance_id"]),
        operating_system_process_id=int(cycle_one["operating_system_process_id"]),
        utc_anchor=str(cycle_one["created_at"]),
        utc_anchor_monotonic_ns=0,
        source_trace_refs=tuple(cycle_one.get("source_trace_refs") or ()),
        comparable_across_processes=True,
    )
    clock_two = build_clock_domain_descriptor(
        process_instance_id=str(cycle_two["process_instance_id"]),
        operating_system_process_id=int(cycle_two["operating_system_process_id"]),
        utc_anchor=str(cycle_two["created_at"]),
        utc_anchor_monotonic_ns=0,
        source_trace_refs=tuple(cycle_two.get("source_trace_refs") or ()),
        comparable_across_processes=True,
    )
    event_times = tuple(
        value
        for item in coverage
        for value in (int(item["start_event_time_ns"]), int(item["end_event_time_ns"]))
    )
    quality_one = evaluate_clock_quality(clock_one, event_times)
    quality_two = evaluate_clock_quality(clock_two, tuple())
    anchors, spans, intervals, relations, continuity, repeated, runtime_spans = _compile_cycle_one_temporal_records(
        clock_one,
        cycle_one,
        coverage,
        replay_speed=replay_speed,
    )
    external_gap = build_cross_process_external_gap(
        previous_process_instance_id=clock_one.process_instance_id,
        current_process_instance_id=clock_two.process_instance_id,
        previous_last_event_utc=str(cycle_one["created_at"]),
        current_first_event_utc=str(cycle_two["created_at"]),
        previous_clock_domain_id=clock_one.clock_domain_id,
        current_clock_domain_id=clock_two.clock_domain_id,
        source_record_refs=(str(cycle_one["cycle_record_id"]), str(cycle_two["cycle_record_id"])),
        source_trace_refs=tuple(dict.fromkeys(tuple(cycle_one.get("source_trace_refs") or ()) + tuple(cycle_two.get("source_trace_refs") or ()))),
    )
    source_perception_refs = tuple(cycle_one.get("perception_readable_data_refs") or ())
    source_window_refs = tuple(str(item["alignment_window_id"]) for item in coverage)
    source_trace_refs = tuple(dict.fromkeys(ref for item in coverage for ref in tuple(item.get("source_trace_refs") or ())))
    bundle_payload = {
        "schema_version": TEMPORAL_BUNDLE_SCHEMA_VERSION,
        "clock_domain_refs": (clock_one.clock_domain_id, clock_two.clock_domain_id),
        "anchor_refs": tuple(item.temporal_anchor_id for item in anchors),
        "span_refs": tuple(item.temporal_span_id for item in spans),
        "interval_refs": tuple(item.temporal_interval_id for item in intervals),
        "relation_refs": tuple(item.temporal_relation_id for item in relations),
        "continuity_refs": tuple(item.temporal_continuity_id for item in continuity),
        "repeated_structure_refs": tuple(item.repeated_structure_id for item in repeated),
        "external_gap_refs": (external_gap.external_gap_id,),
        "source_perception_record_refs": source_perception_refs,
        "source_alignment_window_refs": source_window_refs,
        "source_trace_refs": source_trace_refs,
        "stimulus_ground_truth_used_for_compilation": False,
        "subjective_time_claimed": False,
        "rhythm_semantics_claimed": False,
        "waiting_semantics_claimed": False,
    }
    bundle = GroundedTemporalPrimitiveBundle(
        temporal_bundle_id=temporal_identity("grounded_temporal_bundle", bundle_payload),
        created_at=utc_now(),
        **bundle_payload,
    )
    sidecars = tuple(
        attach_temporal_context_sidecar(
            source_perception_record_id=source_ref,
            bundle=bundle,
            source_record_refs=(source_ref, bundle.temporal_bundle_id),
            source_trace_refs=source_trace_refs,
        )
        for source_ref in source_perception_refs[:4]
    )
    fingerprint_after = archive_tree_fingerprint(archive)
    result = Package124ATemporalCompilationResult(
        archive_dir=str(archive),
        archive_verified=bool(verification.get("valid")),
        archive_opened_read_only=True,
        archive_fingerprint_before=fingerprint_before,
        archive_fingerprint_after=fingerprint_after,
        clock_domains=(clock_one, clock_two),
        clock_quality_records=(quality_one, quality_two),
        anchors=anchors,
        spans=spans,
        intervals=intervals,
        relations=relations,
        continuity_records=continuity,
        repeated_structures=repeated,
        runtime_state_spans=runtime_spans,
        external_gaps=(external_gap,),
        temporal_bundle=bundle,
        temporal_sidecars=sidecars,
        source_coverage_records=coverage,
        source_cycle_records=(cycle_one, cycle_two),
        replay_speed=float(replay_speed),
    )
    if persist:
        if state_dir is None:
            raise ValueError("state_dir is required when persist=True")
        persist_temporal_compilation_result(state_dir, result)
    return result


def persist_temporal_compilation_result(state_dir: str | Path, result: Package124ATemporalCompilationResult) -> None:
    store = Package124ATemporalStore(state_dir)
    for record in result.clock_domains:
        store.append_record("temporal_clock_domains", record)
    for record in result.clock_quality_records:
        store.append_record("temporal_clock_quality", record)
    for record in result.anchors:
        store.append_record("temporal_event_anchors", record)
    for record in result.spans:
        store.append_record("temporal_span_primitives", record)
    for record in result.intervals:
        store.append_record("temporal_interval_primitives", record)
    for record in result.relations:
        store.append_record("temporal_relation_primitives", record)
    for record in result.continuity_records:
        store.append_record("temporal_continuity_primitives", record)
    for record in result.repeated_structures:
        store.append_record("temporal_repeated_structures", record)
    for record in result.runtime_state_spans:
        store.append_record("runtime_state_temporal_spans", record)
    for record in result.external_gaps:
        store.append_record("cross_process_external_gaps", record)
    store.append_record("grounded_temporal_bundles", result.temporal_bundle)
    for record in result.temporal_sidecars:
        store.append_record("temporal_context_sidecars", record)


def read_package_124_temporal_evidence(archive_dir: str | Path) -> dict[str, Any]:
    archive = Path(archive_dir).resolve()
    source = archive / SOURCE_STATE_DIRNAME
    package_123_db = source / "package_123_real_perception_v0" / "package_123.sqlite3"
    cycle_records = _payloads(package_123_db, "package_123_cycle_records")
    cycle_one = _find_payload(cycle_records, bounded_runtime_session_id=PACKAGE_123_CYCLE_1_SESSION_ID, cycle_index=1)
    cycle_two = _find_payload(cycle_records, bounded_runtime_session_id=PACKAGE_123_CYCLE_2_SESSION_ID, cycle_index=2)
    if not cycle_one or not cycle_two:
        raise KeyError("Package 124A requires exact Package 123 cycle records from the archive")
    coverage = tuple(
        item
        for item in _payloads(package_123_db, "package_123_alignment_window_coverage")
        if item.get("experiment_run_id") == cycle_one.get("experiment_run_id") and int(item.get("cycle_index", -1)) == 1
    )
    if not coverage:
        raise KeyError("Package 124A requires Cycle 1 alignment window coverage records")
    return {"cycle_one": cycle_one, "cycle_two": cycle_two, "coverage": coverage}


def calibrate_against_stimulus_after_compilation(
    *,
    archive_dir: str | Path = DEFAULT_PACKAGE_124_ARCHIVE,
    state_dir: str | Path,
    temporal_bundle_id: str | None = None,
    persist: bool = True,
) -> TemporalCalibrationAuditRecord:
    store = Package124ATemporalStore(state_dir)
    bundle = store.get_payload("grounded_temporal_bundles", temporal_bundle_id) if temporal_bundle_id else store.latest_payload("grounded_temporal_bundles")
    if not bundle:
        raise KeyError("compile temporal bundle before stimulus calibration")
    archive = Path(archive_dir).resolve()
    evidence = read_package_124_temporal_evidence(archive)
    cycle_one = evidence["cycle_one"]
    coverage = tuple(evidence["coverage"])
    stimulus = _find_payload(
        _payloads(archive / SOURCE_STATE_DIRNAME / "package_123_real_perception_v0" / "package_123.sqlite3", "stimulus_run_manifests"),
        experiment_run_id=cycle_one["experiment_run_id"],
    )
    transitions = tuple(stimulus.get("transitions") or ())
    visual_changes = _count_state_changes(transitions, "visual_state")
    audio_energy = sum(1 for item in transitions if item.get("audio_state") == "tone")
    observed_visual = sum(1 for item in coverage if (item.get("screen") or {}).get("salient_change_present"))
    observed_audio = sum(1 for item in coverage if (item.get("audio") or {}).get("salient_change_present"))
    observed_overlap = sum(1 for item in coverage if item.get("visual_audio_overlap_present"))
    failures: list[str] = []
    if observed_visual != visual_changes:
        failures.append("visual_transition_count_mismatch")
    if observed_audio != audio_energy:
        failures.append("audio_energy_count_mismatch")
    if observed_overlap != audio_energy:
        failures.append("overlap_count_mismatch")
    payload = {
        "schema_version": TEMPORAL_CALIBRATION_AUDIT_SCHEMA_VERSION,
        "temporal_bundle_id": str(bundle["temporal_bundle_id"]),
        "stimulus_manifest_id": str(stimulus.get("experiment_run_id") or ""),
        "stimulus_loaded_after_compilation": True,
        "stimulus_used_for_compilation": False,
        "observed_visual_transition_count": observed_visual,
        "expected_visual_transition_count": visual_changes,
        "observed_audio_energy_count": observed_audio,
        "expected_audio_energy_count": audio_energy,
        "observed_overlap_count": observed_overlap,
        "expected_overlap_count": audio_energy,
        "tolerance_ns": 500_000_000,
        "calibration_status": "calibrated_after_compilation" if not failures else "blocked_mismatch",
        "failure_reasons": tuple(failures),
        "source_record_refs": (str(stimulus.get("experiment_run_id") or ""), str(bundle["temporal_bundle_id"])),
        "source_trace_refs": tuple(bundle.get("source_trace_refs") or ()),
    }
    record = TemporalCalibrationAuditRecord(
        calibration_audit_id=temporal_identity("temporal_calibration", payload),
        created_at=utc_now(),
        **payload,
    )
    if persist:
        store.append_record("temporal_calibration_audits", record)
    return record


def verify_temporal_deterministic_replay(archive_dir: str | Path = DEFAULT_PACKAGE_124_ARCHIVE) -> dict[str, object]:
    first = compile_package_124_archive_temporal_bundle(archive_dir=archive_dir, persist=False, replay_speed=1.0, verify_archive=False)
    second = compile_package_124_archive_temporal_bundle(archive_dir=archive_dir, persist=False, replay_speed=1.0, verify_archive=False)
    return {
        "deterministic_identity_verified": first.identity_signature() == second.identity_signature(),
        "first_signature": first.identity_signature(),
        "second_signature": second.identity_signature(),
    }


def verify_replay_speed_independence(archive_dir: str | Path = DEFAULT_PACKAGE_124_ARCHIVE) -> dict[str, object]:
    one_x = compile_package_124_archive_temporal_bundle(archive_dir=archive_dir, persist=False, replay_speed=1.0, verify_archive=False)
    two_x = compile_package_124_archive_temporal_bundle(archive_dir=archive_dir, persist=False, replay_speed=2.0, verify_archive=False)
    max_safe = compile_package_124_archive_temporal_bundle(archive_dir=archive_dir, persist=False, replay_speed=4.0, verify_archive=False)
    one = one_x.identity_signature()
    return {
        "replay_speed_independence_verified": one == two_x.identity_signature() == max_safe.identity_signature(),
        "one_x_signature": one,
        "two_x_signature": two_x.identity_signature(),
        "maximum_safe_signature": max_safe.identity_signature(),
    }


def archive_tree_fingerprint(root: str | Path) -> str:
    base = Path(root)
    entries: list[dict[str, object]] = []
    for path in sorted(item for item in base.rglob("*") if item.is_file() and (item.name == "archive_manifest.json" or item.name == "ARCHIVE_READ_ONLY" or item.suffix.lower() in {".wal", ".journal"})):
        rel = path.relative_to(base).as_posix()
        data = path.read_bytes()
        entries.append({"relative_path": rel, "byte_length": len(data), "sha256": sha256_bytes(data)})
    return sha256_payload(entries)


def _compile_cycle_one_temporal_records(
    clock_domain: TemporalClockDomainDescriptor,
    cycle_one: dict[str, Any],
    coverage: tuple[dict[str, Any], ...],
    *,
    replay_speed: float,
) -> tuple[
    tuple[TemporalEventAnchor, ...],
    tuple[TemporalSpanPrimitive, ...],
    tuple[TemporalIntervalPrimitive, ...],
    tuple[TemporalRelationPrimitive, ...],
    tuple[TemporalContinuityPrimitive, ...],
    tuple[RepeatedOccurrenceTemporalStructure, ...],
    tuple[RuntimeStateTemporalSpan, ...],
]:
    ordered = tuple(sorted(coverage, key=lambda item: int(item["window_index"])))
    anchors: list[TemporalEventAnchor] = []
    anchor_by_key: dict[tuple[str, str], TemporalEventAnchor] = {}

    def anchor(item: dict[str, Any], point: str, event_time_ns: int, lane: str) -> TemporalEventAnchor:
        key = (str(item["alignment_window_id"]), point)
        if key not in anchor_by_key:
            event_sequence = int(item.get("window_index") or 0) * 2 + (1 if point.endswith("end") else 0)
            built = build_temporal_anchor(
                source_record_id=str(item["alignment_window_id"]),
                source_record_kind="package_123_alignment_window_coverage",
                source_lane=lane,
                clock_domain_id=clock_domain.clock_domain_id,
                normalized_event_time_ns=int(event_time_ns),
                source_native_time_ns=int(event_time_ns),
                processing_time_ns=int(event_time_ns / replay_speed) + 2_000,
                replay_submission_time_ns=int(event_time_ns / replay_speed) + 1_000,
                event_sequence_index=event_sequence,
                action_tick=None,
                timestamp_resolution_ns=1,
                timestamp_uncertainty_ns=1_000_000,
                source_record_refs=(str(item.get("coverage_record_id")), str(item["alignment_window_id"])),
                source_trace_refs=tuple(item.get("source_trace_refs") or ()),
            )
            anchor_by_key[key] = built
            anchors.append(built)
        return anchor_by_key[key]

    spans: list[TemporalSpanPrimitive] = []
    visual_spans: list[TemporalSpanPrimitive] = []
    audio_spans: list[TemporalSpanPrimitive] = []
    for item in ordered:
        start = anchor(item, "window_start", int(item["start_event_time_ns"]), "alignment_window")
        end = anchor(item, "window_end", int(item["end_event_time_ns"]), "alignment_window")
        if (item.get("screen") or {}).get("salient_change_present"):
            visual = build_temporal_span(
                span_kind="observed_change_region",
                start_anchor=start,
                end_anchor=end,
                source_lane="screen",
                source_region_refs=tuple((item.get("screen") or {}).get("primitive_record_refs") or ()),
                source_record_refs=(str(item.get("coverage_record_id")), str(item["alignment_window_id"])),
                source_trace_refs=tuple(item.get("source_trace_refs") or ()),
            )
            spans.append(visual)
            visual_spans.append(visual)
        if (item.get("audio") or {}).get("salient_change_present"):
            audio = build_temporal_span(
                span_kind="observed_energy_region",
                start_anchor=start,
                end_anchor=end,
                source_lane="microphone",
                source_region_refs=tuple((item.get("audio") or {}).get("primitive_record_refs") or ()),
                source_record_refs=(str(item.get("coverage_record_id")), str(item["alignment_window_id"])),
                source_trace_refs=tuple(item.get("source_trace_refs") or ()),
            )
            spans.append(audio)
            audio_spans.append(audio)

    first = ordered[0]
    last = ordered[-1]
    coverage_start = anchor(first, "coverage_start", int(first["start_event_time_ns"]), "alignment_window")
    coverage_end = anchor(last, "coverage_end", int(last["end_event_time_ns"]), "alignment_window")
    for lane in REQUIRED_LANES:
        spans.append(
            build_temporal_span(
                span_kind="source_presence_span",
                start_anchor=coverage_start,
                end_anchor=coverage_end,
                source_lane=lane,
                source_region_refs=tuple(str(item["alignment_window_id"]) for item in ordered),
                source_record_refs=tuple(str(item.get("coverage_record_id")) for item in ordered),
                source_trace_refs=tuple(dict.fromkeys(ref for item in ordered for ref in tuple(item.get("source_trace_refs") or ()))),
            )
        )
    spans.append(
        build_temporal_span(
            span_kind="alignment_coverage_span",
            start_anchor=coverage_start,
            end_anchor=coverage_end,
            source_lane=None,
            source_region_refs=tuple(str(item["alignment_window_id"]) for item in ordered),
            source_record_refs=tuple(str(item.get("coverage_record_id")) for item in ordered),
            source_trace_refs=tuple(dict.fromkeys(ref for item in ordered for ref in tuple(item.get("source_trace_refs") or ()))),
        )
    )
    anchors_tuple = tuple(anchors)
    anchors_by_id = {item.temporal_anchor_id: item for item in anchors_tuple}
    intervals = tuple(
        list(derive_repeated_onset_intervals(tuple(visual_spans), anchors_by_id))
        + list(derive_repeated_onset_intervals(tuple(audio_spans), anchors_by_id))
        + list(derive_offset_to_onset_intervals(tuple(visual_spans), anchors_by_id))
        + [
            build_temporal_interval(
                interval_kind="event_to_event",
                left_anchor=coverage_start,
                right_anchor=coverage_end,
                source_record_refs=(str(cycle_one["cycle_record_id"]),),
                source_trace_refs=tuple(cycle_one.get("source_trace_refs") or ()),
            )
        ]
    )
    relations = tuple(derive_temporal_relation(left, right) for left in visual_spans for right in audio_spans)
    continuity = (compile_temporal_continuity(ordered, required_lanes=REQUIRED_LANES),)
    repeated = (
        compile_repeated_occurrence_structure(tuple(visual_spans)),
        compile_repeated_occurrence_structure(tuple(audio_spans)),
    )
    runtime_payload = {
        "schema_version": RUNTIME_STATE_SPAN_SCHEMA_VERSION,
        "runtime_state": "running",
        "start_anchor_id": coverage_start.temporal_anchor_id,
        "end_anchor_id": coverage_end.temporal_anchor_id,
        "observed_duration_ns": int(last["end_event_time_ns"]) - int(first["start_event_time_ns"]),
        "open_span": False,
        "state_source_record_refs": (str(cycle_one["cycle_record_id"]), str(cycle_one["bounded_runtime_session_id"])),
        "source_trace_refs": tuple(cycle_one.get("source_trace_refs") or ()),
    }
    runtime_state = RuntimeStateTemporalSpan(
        runtime_state_span_id=temporal_identity("runtime_state_temporal_span", runtime_payload),
        **runtime_payload,
    )
    return anchors_tuple, tuple(spans), intervals, relations, continuity, repeated, (runtime_state,)


def _payloads(path: Path, table: str) -> tuple[dict[str, Any], ...]:
    connection = sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True)
    try:
        connection.row_factory = sqlite3.Row
        order = "row_id" if _table_has_column(connection, table, "row_id") else "created_at"
        rows = connection.execute(f"SELECT payload_json FROM {table} ORDER BY {order}").fetchall()
        return tuple(json.loads(str(row["payload_json"])) for row in rows)
    finally:
        connection.close()


def _table_has_column(connection: sqlite3.Connection, table: str, column: str) -> bool:
    return any(str(row["name"]) == column for row in connection.execute(f"PRAGMA table_info({table})").fetchall())


def _find_payload(payloads: tuple[dict[str, Any], ...], **matches: object) -> dict[str, Any]:
    for item in payloads:
        if all(item.get(key) == value for key, value in matches.items()):
            return dict(item)
    return {}


def _count_state_changes(transitions: tuple[dict[str, Any], ...], field_name: str) -> int:
    count = 0
    previous: object | None = None
    for item in transitions:
        current = item.get(field_name)
        if previous is not None and current != previous:
            count += 1
        previous = current
    return count


def _stable_record_payload(record: Any, *, clear: tuple[str, ...] = tuple()) -> dict[str, Any]:
    payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
    payload.pop("created_at", None)
    for key in clear:
        payload[key] = None
    return payload
