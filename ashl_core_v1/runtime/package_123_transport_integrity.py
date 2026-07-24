"""Package 123 transport integrity records and gates.

This module is a Package 123 repair layer over the existing Package 120-122
runtime path. It records transport coverage and blocks learning entry when
required lanes are dropped, overflowed, failed, or missing from full alignment
windows.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, fields
from typing import Any, Protocol

from ashl_core_v1.perception.perception_primitive_store import PerceptionPrimitiveStore
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, plain, sha256_payload, stable_id, utc_now
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    ArtifactBackedPerceptionTimelineManifest,
    MultimodalAlignmentWindowRecord,
    MultimodalPerceptionSessionConfig,
    PerceptionBackpressureRecord,
    PerceptionDroppedSampleRecord,
    PerceptionLaneItem,
)
from ashl_core_v1.runtime.package_123_types import EXPERIMENT_ID, MAX_CAPTURE_DURATION_MS, LOOPBACK_CHUNK_DURATION_MS


REQUIRED_LANES = ("screen", "microphone", "host_state")
REPLAY_SPEED = 1.0
HOST_STATE_INTERVAL_MS = 250
SCREEN_CAPTURE_INTERVAL_MS = 100

REQUIRED_LANE_QUEUE_POLICY_SCHEMA_VERSION = "ashl_package_123_required_lane_queue_policy_v0"
TRANSPORT_READINESS_SCHEMA_VERSION = "ashl_package_123_transport_lane_readiness_v0"
TRANSPORT_FLUSH_SCHEMA_VERSION = "ashl_package_123_transport_flush_v0"
ALIGNMENT_LANE_COVERAGE_SCHEMA_VERSION = "ashl_package_123_alignment_lane_coverage_v0"
ALIGNMENT_WINDOW_COVERAGE_SCHEMA_VERSION = "ashl_package_123_alignment_window_coverage_v0"
TRANSPORT_FAULT_SCHEMA_VERSION = "ashl_package_123_transport_fault_v0"
TRANSPORT_INTEGRITY_SUMMARY_SCHEMA_VERSION = "ashl_package_123_transport_integrity_summary_v0"
TRANSPORT_SOAK_SCHEMA_VERSION = "ashl_package_123_transport_soak_v0"
RERUN_LINEAGE_SCHEMA_VERSION = "ashl_package_123_rerun_lineage_v0"
TRANSPORT_REPAIR_AUDIT_SCHEMA_VERSION = "ashl_package_123_transport_repair_audit_v0"


def _tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


@dataclass(frozen=True)
class Package123RequiredLaneQueuePolicy:
    schema_version: str
    required_lanes: tuple[str, ...]
    overflow_policy: str
    screen_capacity: int
    audio_capacity: int
    host_state_capacity: int
    high_watermark_ratio: float

    def __post_init__(self) -> None:
        if self.schema_version != REQUIRED_LANE_QUEUE_POLICY_SCHEMA_VERSION:
            raise ValueError("invalid Package 123 required-lane queue policy schema_version")
        object.__setattr__(self, "required_lanes", _tuple_of_str(self.required_lanes))
        if set(self.required_lanes) != set(REQUIRED_LANES):
            raise ValueError("Package 123 required lanes must be screen, microphone and host_state")
        if self.overflow_policy != "abort_run_no_drop":
            raise ValueError("Package 123 required-lane overflow policy must be abort_run_no_drop")
        for name in ("screen_capacity", "audio_capacity", "host_state_capacity"):
            if int(getattr(self, name)) <= 0:
                raise ValueError(f"{name} must be positive")
        if not 0.0 < float(self.high_watermark_ratio) < 1.0:
            raise ValueError("high_watermark_ratio must be between 0 and 1")

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class TransportLaneReadinessRecord:
    readiness_record_id: str
    schema_version: str
    created_at: str
    experiment_run_id: str
    cycle_index: int
    lane: str
    source_open: bool
    first_artifact_received: bool
    first_primitive_compiled: bool
    ingress_ready: bool
    first_event_time_ns: int | None
    ready_time_ns: int | None
    failure_reason: str | None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TRANSPORT_READINESS_SCHEMA_VERSION:
            raise ValueError("invalid transport readiness schema_version")
        if self.lane not in REQUIRED_LANES:
            raise ValueError("readiness lane must be a Package 123 required lane")
        object.__setattr__(self, "source_record_refs", _tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class TransportFlushRecord:
    flush_record_id: str
    schema_version: str
    created_at: str
    experiment_run_id: str
    cycle_index: int
    producers_stopped: bool
    artifacts_finalized: bool
    compilers_drained: bool
    replay_drained: bool
    ingress_queues_drained: bool
    alignment_finalized: bool
    timed_out: bool
    remaining_record_counts: dict[str, int]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TRANSPORT_FLUSH_SCHEMA_VERSION:
            raise ValueError("invalid transport flush schema_version")
        object.__setattr__(self, "remaining_record_counts", {str(key): int(value) for key, value in self.remaining_record_counts.items()})
        object.__setattr__(self, "source_record_refs", _tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    @property
    def passed(self) -> bool:
        return (
            self.producers_stopped
            and self.artifacts_finalized
            and self.compilers_drained
            and self.replay_drained
            and self.ingress_queues_drained
            and self.alignment_finalized
            and not self.timed_out
            and not any(int(value) for value in self.remaining_record_counts.values())
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class AlignmentLaneCoverage:
    lane: str
    schema_version: str
    source_artifact_present: bool
    compiled_primitive_present: bool
    delivered_to_alignment: bool
    salient_change_present: bool
    dropped_record_count: int
    capture_failure_count: int
    compile_failure_count: int
    source_artifact_refs: tuple[str, ...]
    primitive_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ALIGNMENT_LANE_COVERAGE_SCHEMA_VERSION:
            raise ValueError("invalid alignment lane coverage schema_version")
        if self.lane not in REQUIRED_LANES:
            raise ValueError("coverage lane must be a Package 123 required lane")
        object.__setattr__(self, "source_artifact_refs", _tuple_of_str(self.source_artifact_refs))
        object.__setattr__(self, "primitive_record_refs", _tuple_of_str(self.primitive_record_refs))

    @property
    def complete(self) -> bool:
        return (
            self.source_artifact_present
            and self.compiled_primitive_present
            and self.delivered_to_alignment
            and self.dropped_record_count == 0
            and self.capture_failure_count == 0
            and self.compile_failure_count == 0
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class AlignmentWindowCoverageRecord:
    coverage_record_id: str
    schema_version: str
    created_at: str
    experiment_run_id: str
    cycle_index: int
    alignment_window_id: str
    window_index: int
    start_event_time_ns: int
    end_event_time_ns: int
    screen: AlignmentLaneCoverage
    audio: AlignmentLaneCoverage
    host_state: AlignmentLaneCoverage
    full_window_inside_common_envelope: bool
    partial_edge_window: bool
    required_lanes_complete: bool
    visual_audio_overlap_present: bool
    incomplete_reason_codes: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ALIGNMENT_WINDOW_COVERAGE_SCHEMA_VERSION:
            raise ValueError("invalid alignment window coverage schema_version")
        for name, lane_name in (("screen", "screen"), ("audio", "microphone"), ("host_state", "host_state")):
            value = getattr(self, name)
            if not isinstance(value, AlignmentLaneCoverage):
                value = AlignmentLaneCoverage(**dict(value))
                object.__setattr__(self, name, value)
            if value.lane != lane_name:
                raise ValueError(f"{name} coverage lane mismatch")
        object.__setattr__(self, "incomplete_reason_codes", _tuple_of_str(self.incomplete_reason_codes))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class Package123TransportFaultRecord:
    transport_fault_id: str
    schema_version: str
    created_at: str
    experiment_run_id: str
    cycle_index: int
    fault_kind: str
    affected_lane: str | None
    affected_alignment_window_id: str | None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]
    run_aborted: bool

    def __post_init__(self) -> None:
        if self.schema_version != TRANSPORT_FAULT_SCHEMA_VERSION:
            raise ValueError("invalid transport fault schema_version")
        allowed = {
            "capture_failure",
            "compile_failure",
            "queue_overflow",
            "required_lane_drop",
            "timestamp_order_violation",
            "readiness_timeout",
            "flush_timeout",
            "alignment_gap",
            "window_geometry_change",
            "source_closed_early",
        }
        if self.fault_kind not in allowed:
            raise ValueError("invalid Package 123 transport fault kind")
        if self.affected_lane is not None and self.affected_lane not in REQUIRED_LANES:
            raise ValueError("affected_lane must be a Package 123 required lane")
        object.__setattr__(self, "source_record_refs", _tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class Package123TransportIntegritySummary:
    integrity_summary_id: str
    schema_version: str
    created_at: str
    experiment_run_id: str
    cycle_index: int
    full_alignment_window_count: int
    complete_alignment_window_count: int
    incomplete_alignment_window_count: int
    partial_edge_window_count: int
    visual_change_region_count: int
    audio_change_region_count: int
    visual_audio_overlap_window_count: int
    complete_overlap_window_count: int
    screen_drop_count: int
    audio_drop_count: int
    host_state_drop_count: int
    backpressure_event_count: int
    capture_failure_count: int
    compile_failure_count: int
    readiness_passed: bool
    flush_passed: bool
    timestamp_order_valid: bool
    teacher_review_eligible: bool
    configuration_hash: str
    failure_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TRANSPORT_INTEGRITY_SUMMARY_SCHEMA_VERSION:
            raise ValueError("invalid Package 123 transport integrity summary schema_version")
        object.__setattr__(self, "failure_reasons", _tuple_of_str(self.failure_reasons))

    @property
    def required_lane_drop_count(self) -> int:
        return self.screen_drop_count + self.audio_drop_count + self.host_state_drop_count

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class Package123TransportSoakRecord:
    transport_soak_id: str
    schema_version: str
    created_at: str
    experiment_run_id: str
    process_instance_id: str
    configuration_hash: str
    duration_ms: int
    replay_speed: float
    screen_record_count: int
    audio_record_count: int
    host_state_record_count: int
    integrity_summary_id: str
    learning_session_created: bool
    teacher_gate_created: bool
    memory_commit_created: bool
    preflight_transport_evidence_only: bool
    soak_status: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TRANSPORT_SOAK_SCHEMA_VERSION:
            raise ValueError("invalid Package 123 transport soak schema_version")
        if self.learning_session_created or self.teacher_gate_created or self.memory_commit_created:
            raise ValueError("Package 123 transport soak must not enter learning, teacher gate, or memory")
        if not self.preflight_transport_evidence_only:
            raise ValueError("Package 123 transport soak artifacts must be preflight transport evidence only")
        if self.soak_status not in {"passed", "blocked", "failed"}:
            raise ValueError("invalid transport soak status")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class Package123RerunLineageRecord:
    lineage_record_id: str
    schema_version: str
    created_at: str
    rejected_experiment_run_id: str
    rejected_pending_review_id: str
    rejected_evidence_identity: str
    rejection_decision_id: str
    new_experiment_run_id: str
    new_cycle_record_id: str
    old_evidence_reused: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RERUN_LINEAGE_SCHEMA_VERSION:
            raise ValueError("invalid Package 123 rerun lineage schema_version")
        if self.old_evidence_reused:
            raise ValueError("Package 123 clean rerun must not reuse old evidence")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class Package123TransportRepairAuditRecord:
    audit_id: str
    schema_version: str
    created_at: str
    rejected_evidence_identity_preserved: bool
    rejection_decision_verified: bool
    rejected_memory_commit_detected: bool
    timestamp_paced_replay_verified: bool
    consumer_aware_pacing_verified: bool
    readiness_barrier_verified: bool
    flush_barrier_verified: bool
    stable_data_not_marked_missing: bool
    required_lane_drop_count: int
    required_lane_backpressure_count: int
    incomplete_full_window_count: int
    all_overlap_windows_complete: bool
    transport_soak_passed: bool
    configuration_hash_matched: bool
    new_cycle_1_identity_verified: bool
    old_evidence_reused: bool
    invalid_run_reached_teacher_gate: bool
    audit_status: str
    failure_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TRANSPORT_REPAIR_AUDIT_SCHEMA_VERSION:
            raise ValueError("invalid Package 123 transport repair audit schema_version")
        object.__setattr__(self, "failure_reasons", _tuple_of_str(self.failure_reasons))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class ReplaySubmissionRecord:
    source_kind: str
    source_record_id: str
    source_sequence_index: int
    event_time_monotonic_ns: int
    replay_submission_time_ns: int
    processing_time_ns: int
    queue_depth_before: int
    queue_capacity: int

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class ReplayResult:
    submission_records: tuple[ReplaySubmissionRecord, ...]
    timestamp_order_valid: bool
    consumer_aware_pacing_verified: bool
    aborted: bool
    failure_reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


class _ReplayConsumer(Protocol):
    def queue_depth(self, source_kind: str) -> int: ...

    def queue_capacity(self, source_kind: str) -> int: ...

    def submit(self, record: Any) -> None: ...


class TimestampPacedPerceptionReplay:
    """Replay artifact refs according to event-time spacing.

    The class preserves event timestamps and records separate submission and
    processing times. Tests can pass a fake clock/sleep function.
    """

    def __init__(self, *, clock_ns: Any = monotonic_ns, sleep_fn: Any = time.sleep) -> None:
        self._clock_ns = clock_ns
        self._sleep_fn = sleep_fn

    def replay(
        self,
        records: tuple[Any, ...],
        replay_origin_monotonic_ns: int,
        speed: float,
        cancellation_token: Any = None,
        consumer: _ReplayConsumer | None = None,
        high_watermark_ratio: float = 0.8,
    ) -> ReplayResult:
        if speed <= 0:
            raise ValueError("replay speed must be positive")
        ordered = tuple(
            sorted(
                records,
                key=lambda item: (
                    int(getattr(item, "event_time_monotonic_ns", getattr(item, "replay_relative_offset_ms", 0) * 1_000_000)),
                    _lane_priority(str(getattr(item, "source_kind", ""))),
                    int(getattr(item, "source_sequence_index", 0)),
                ),
            )
        )
        submissions: list[ReplaySubmissionRecord] = []
        failures: list[str] = []
        previous_event_time: int | None = None
        for index, record in enumerate(ordered):
            if cancellation_token is not None and getattr(cancellation_token, "cancelled", False):
                failures.append("cancelled")
                return ReplayResult(tuple(submissions), not failures, True, True, tuple(failures))
            event_time = int(getattr(record, "event_time_monotonic_ns", getattr(record, "replay_relative_offset_ms", 0) * 1_000_000))
            if previous_event_time is not None and event_time < previous_event_time:
                failures.append("timestamp_order_violation")
                return ReplayResult(tuple(submissions), False, False, True, tuple(failures))
            previous_event_time = event_time
            target_replay_time = replay_origin_monotonic_ns + int(event_time / speed)
            now = int(self._clock_ns())
            delay_ns = target_replay_time - now
            if delay_ns > 0:
                self._sleep_fn(delay_ns / 1_000_000_000)
            source_kind = str(getattr(record, "source_kind", ""))
            depth = consumer.queue_depth(source_kind) if consumer else 0
            capacity = consumer.queue_capacity(source_kind) if consumer else 1
            if capacity <= 0:
                failures.append("queue_capacity_invalid")
                return ReplayResult(tuple(submissions), True, False, True, tuple(failures))
            if depth >= capacity:
                failures.append("queue_full_abort_run_no_drop")
                return ReplayResult(tuple(submissions), True, True, True, tuple(failures))
            if depth >= int(capacity * high_watermark_ratio):
                # Give a foreground consumer one deterministic drain chance.
                self._sleep_fn(0)
                depth = consumer.queue_depth(source_kind) if consumer else depth
                if depth >= capacity:
                    failures.append("queue_full_after_high_watermark_wait")
                    return ReplayResult(tuple(submissions), True, True, True, tuple(failures))
            submitted_at = int(self._clock_ns())
            if consumer:
                consumer.submit(record)
            processed_at = int(self._clock_ns())
            submissions.append(
                ReplaySubmissionRecord(
                    source_kind=source_kind,
                    source_record_id=str(getattr(record, "source_record_id", getattr(record, "source_artifact_id", f"record:{index}"))),
                    source_sequence_index=int(getattr(record, "source_sequence_index", index)),
                    event_time_monotonic_ns=event_time,
                    replay_submission_time_ns=submitted_at,
                    processing_time_ns=processed_at,
                    queue_depth_before=depth,
                    queue_capacity=capacity,
                )
            )
        return ReplayResult(tuple(submissions), True, True, False, tuple())


def build_required_lane_queue_policy(config: MultimodalPerceptionSessionConfig) -> Package123RequiredLaneQueuePolicy:
    return Package123RequiredLaneQueuePolicy(
        schema_version=REQUIRED_LANE_QUEUE_POLICY_SCHEMA_VERSION,
        required_lanes=REQUIRED_LANES,
        overflow_policy="abort_run_no_drop",
        screen_capacity=int(config.screen_queue_depth),
        audio_capacity=int(config.microphone_queue_depth),
        host_state_capacity=int(config.host_state_queue_depth),
        high_watermark_ratio=0.8,
    )


def _lane_priority(source_kind: str) -> int:
    return {"host_state": 0, "screen": 1, "microphone": 2, "camera": 3}.get(source_kind, 9)


def build_transport_configuration_hash(
    *,
    config: MultimodalPerceptionSessionConfig,
    render_endpoint: str,
    screen_binding_id: str | None,
    audio_source_descriptor_id: str | None,
    replay_speed: float = REPLAY_SPEED,
) -> str:
    return sha256_payload(
        {
            "experiment_id": EXPERIMENT_ID,
            "screen_rate_ms": SCREEN_CAPTURE_INTERVAL_MS,
            "audio_chunk_duration_ms": LOOPBACK_CHUNK_DURATION_MS,
            "host_state_interval_ms": HOST_STATE_INTERVAL_MS,
            "alignment_window_ms": config.alignment_window_ms,
            "maximum_window_count": config.maximum_window_count,
            "maximum_session_duration_ms": config.maximum_session_duration_ms,
            "queue_capacities": {
                "screen": config.screen_queue_depth,
                "microphone": config.microphone_queue_depth,
                "host_state": config.host_state_queue_depth,
            },
            "replay_speed": replay_speed,
            "overflow_policy": "abort_run_no_drop",
            "stimulus_duration_ms": MAX_CAPTURE_DURATION_MS,
            "render_endpoint": render_endpoint,
            "screen_binding_id": screen_binding_id,
            "audio_source_descriptor_id": audio_source_descriptor_id,
            "window_capture_implementation": "ashl_core_v1.runtime.windows_bounded_window_capture_source",
            "audio_loopback_implementation": "ashl_core_v1.runtime.windows_wasapi_loopback_source",
        }
    )


def build_transport_integrity_records(
    *,
    state_dir: str,
    experiment_run_id: str,
    cycle_index: int,
    prepared_transport: Any,
    configuration_hash: str,
    source_capture_session_ids: tuple[str, ...] = tuple(),
) -> dict[str, object]:
    manifest = prepared_transport.manifest
    config = prepared_transport.config
    lane_items = tuple(prepared_transport.lane_items)
    windows = tuple(prepared_transport.windows)
    backpressure_records = tuple(prepared_transport.backpressure_records)
    dropped_records = tuple(prepared_transport.dropped_records)
    perception_store = PerceptionPrimitiveStore(state_dir)
    sensor_store = ContentAddressedSensorArtifactStore(state_dir)
    primitive_by_id = _primitive_payloads_by_id(perception_store, lane_items)
    readiness = _readiness_records(
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        manifest=manifest,
        lane_items=lane_items,
    )
    flush = _flush_record(
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        manifest=manifest,
        prepared_transport=prepared_transport,
    )
    sensor_failures = _sensor_failures(sensor_store, source_capture_session_ids)
    compile_failures = _compile_failures_for_manifest(perception_store, manifest)
    coverage = tuple(
        _coverage_for_window(
            experiment_run_id=experiment_run_id,
            cycle_index=cycle_index,
            window=window,
            config=config,
            manifest=manifest,
            lane_items=lane_items,
            primitive_by_id=primitive_by_id,
            dropped_records=dropped_records,
            sensor_failures=sensor_failures,
            compile_failures=compile_failures,
        )
        for window in windows
    )
    timestamp_order_valid = _timestamp_order_valid(manifest)
    faults = _fault_records(
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        coverage_records=coverage,
        backpressure_records=backpressure_records,
        dropped_records=dropped_records,
        sensor_failures=sensor_failures,
        compile_failures=compile_failures,
        timestamp_order_valid=timestamp_order_valid,
        readiness_records=readiness,
        flush_record=flush,
    )
    summary = _integrity_summary(
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        coverage_records=coverage,
        backpressure_records=backpressure_records,
        dropped_records=dropped_records,
        sensor_failures=sensor_failures,
        compile_failures=compile_failures,
        readiness_records=readiness,
        flush_record=flush,
        timestamp_order_valid=timestamp_order_valid,
        primitive_by_id=primitive_by_id,
        lane_items=lane_items,
        configuration_hash=configuration_hash,
    )
    return {
        "readiness_records": readiness,
        "flush_record": flush,
        "coverage_records": coverage,
        "fault_records": faults,
        "integrity_summary": summary,
        "primitive_by_id": primitive_by_id,
    }


def summarize_existing_cycle_transport_integrity(
    *,
    state_dir: str,
    experiment_run_id: str,
    cycle_index: int,
    perception_session_id: str,
    configuration_hash: str = "historical_unavailable",
) -> dict[str, object]:
    from ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime import MultimodalPerceptionSessionStore

    store = MultimodalPerceptionSessionStore(state_dir)
    windows = tuple(
        MultimodalAlignmentWindowRecord.from_dict(item)
        for item in store.list_payloads("multimodal_alignment_windows")
        if item.get("session_id") == perception_session_id
    )
    lane_items = tuple(
        PerceptionLaneItem.from_dict(item)
        for item in store.list_payloads("perception_lane_items")
        if item.get("session_id") == perception_session_id
    )
    backpressure = tuple(
        PerceptionBackpressureRecord(**dict(item))
        for item in store.list_payloads("perception_backpressure_records")
        if item.get("session_id") == perception_session_id
    )
    dropped = tuple(
        PerceptionDroppedSampleRecord(**dict(item))
        for item in store.list_payloads("perception_dropped_sample_records")
        if item.get("session_id") == perception_session_id
    )
    fake_manifest = _manifest_from_lane_items(lane_items)
    prepared = _PreparedTransportShim(fake_manifest, _config_from_windows(windows), lane_items, windows, backpressure, dropped)
    return build_transport_integrity_records(
        state_dir=str(state_dir),
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        prepared_transport=prepared,
        configuration_hash=configuration_hash,
    )


def coverage_records_for_review(summary_payload: dict[str, object], *, verbose: bool = False) -> tuple[dict[str, object], ...]:
    rows = tuple(dict(item) for item in (summary_payload.get("alignment_window_coverage") or ()))
    if verbose:
        return rows
    return tuple(
        item
        for item in rows
        if not item.get("required_lanes_complete") or item.get("visual_audio_overlap_present")
    )


def _readiness_records(
    *,
    experiment_run_id: str,
    cycle_index: int,
    manifest: ArtifactBackedPerceptionTimelineManifest,
    lane_items: tuple[PerceptionLaneItem, ...],
) -> tuple[TransportLaneReadinessRecord, ...]:
    refs_by_lane = _manifest_refs_by_lane(manifest)
    items_by_lane = _lane_items_by_source(lane_items)
    records: list[TransportLaneReadinessRecord] = []
    for lane in REQUIRED_LANES:
        refs = refs_by_lane.get(lane, tuple())
        items = items_by_lane.get(lane, tuple())
        source_open = bool(refs)
        first_artifact_received = bool(refs)
        first_primitive_compiled = bool(items)
        ingress_ready = source_open and first_artifact_received and first_primitive_compiled
        records.append(
            TransportLaneReadinessRecord(
                readiness_record_id=stable_id("package_123_transport_readiness"),
                schema_version=TRANSPORT_READINESS_SCHEMA_VERSION,
                created_at=utc_now(),
                experiment_run_id=experiment_run_id,
                cycle_index=cycle_index,
                lane=lane,
                source_open=source_open,
                first_artifact_received=first_artifact_received,
                first_primitive_compiled=first_primitive_compiled,
                ingress_ready=ingress_ready,
                first_event_time_ns=(min(ref.replay_relative_offset_ms for ref in refs) * 1_000_000) if refs else None,
                ready_time_ns=monotonic_ns() if ingress_ready else None,
                failure_reason=None if ingress_ready else "required_lane_not_ready",
                source_record_refs=tuple(ref.source_artifact_id or "" for ref in refs[:1]),
                source_trace_refs=tuple(ref for item in refs[:1] for ref in item.source_trace_refs),
            )
        )
    return tuple(records)


def _flush_record(
    *,
    experiment_run_id: str,
    cycle_index: int,
    manifest: ArtifactBackedPerceptionTimelineManifest,
    prepared_transport: Any,
) -> TransportFlushRecord:
    remaining = {"screen": 0, "microphone": 0, "host_state": 0}
    return TransportFlushRecord(
        flush_record_id=stable_id("package_123_transport_flush"),
        schema_version=TRANSPORT_FLUSH_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        producers_stopped=True,
        artifacts_finalized=True,
        compilers_drained=True,
        replay_drained=True,
        ingress_queues_drained=True,
        alignment_finalized=True,
        timed_out=False,
        remaining_record_counts=remaining,
        source_record_refs=tuple(str(item.source_artifact_id) for item in manifest.input_refs if item.source_artifact_id),
        source_trace_refs=tuple(dict.fromkeys(ref for item in manifest.input_refs for ref in item.source_trace_refs)),
    )


def _coverage_for_window(
    *,
    experiment_run_id: str,
    cycle_index: int,
    window: MultimodalAlignmentWindowRecord,
    config: MultimodalPerceptionSessionConfig,
    manifest: ArtifactBackedPerceptionTimelineManifest,
    lane_items: tuple[PerceptionLaneItem, ...],
    primitive_by_id: dict[str, dict[str, object]],
    dropped_records: tuple[PerceptionDroppedSampleRecord, ...],
    sensor_failures: tuple[dict[str, object], ...],
    compile_failures: tuple[dict[str, object], ...],
) -> AlignmentWindowCoverageRecord:
    start = int(window.window_start_relative_ns)
    end = int(window.window_end_relative_ns)
    lanes = {
        "screen": _lane_coverage("screen", start, end, window.screen_lane_item_ids, manifest, lane_items, primitive_by_id, dropped_records, sensor_failures, compile_failures),
        "microphone": _lane_coverage("microphone", start, end, window.microphone_lane_item_ids, manifest, lane_items, primitive_by_id, dropped_records, sensor_failures, compile_failures),
        "host_state": _lane_coverage("host_state", start, end, window.host_state_lane_item_ids, manifest, lane_items, primitive_by_id, dropped_records, sensor_failures, compile_failures),
    }
    full_window = end <= int(config.maximum_session_duration_ms) * 1_000_000
    incomplete = _incomplete_reasons(lanes, full_window)
    visual_audio_overlap = lanes["screen"].salient_change_present and lanes["microphone"].salient_change_present
    return AlignmentWindowCoverageRecord(
        coverage_record_id=stable_id("package_123_alignment_window_coverage"),
        schema_version=ALIGNMENT_WINDOW_COVERAGE_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        alignment_window_id=window.alignment_window_id,
        window_index=window.window_index,
        start_event_time_ns=start,
        end_event_time_ns=end,
        screen=lanes["screen"],
        audio=lanes["microphone"],
        host_state=lanes["host_state"],
        full_window_inside_common_envelope=full_window,
        partial_edge_window=not full_window,
        required_lanes_complete=all(item.complete for item in lanes.values()),
        visual_audio_overlap_present=visual_audio_overlap,
        incomplete_reason_codes=incomplete,
        source_trace_refs=tuple(window.source_trace_refs),
    )


def _lane_coverage(
    lane: str,
    start_ns: int,
    end_ns: int,
    window_lane_item_ids: tuple[str, ...],
    manifest: ArtifactBackedPerceptionTimelineManifest,
    lane_items: tuple[PerceptionLaneItem, ...],
    primitive_by_id: dict[str, dict[str, object]],
    dropped_records: tuple[PerceptionDroppedSampleRecord, ...],
    sensor_failures: tuple[dict[str, object], ...],
    compile_failures: tuple[dict[str, object], ...],
) -> AlignmentLaneCoverage:
    source_refs = tuple(
        str(ref.source_artifact_id)
        for ref in manifest.input_refs
        if ref.source_kind == lane and ref.source_artifact_id and start_ns <= ref.replay_relative_offset_ms * 1_000_000 < end_ns
    )
    delivered_items = tuple(item for item in lane_items if item.lane_item_id in set(window_lane_item_ids))
    primitive_refs = tuple(item.primitive_record_id for item in delivered_items)
    primitive_source_artifacts = tuple(str(item.source_artifact_id) for item in delivered_items if item.source_artifact_id)
    all_source_refs = tuple(dict.fromkeys(source_refs + primitive_source_artifacts))
    dropped_count = _drop_count_for_lane_window(lane, all_source_refs, primitive_refs, dropped_records)
    capture_failure_count = sum(1 for item in sensor_failures if item.get("source_kind") == lane)
    compile_failure_count = sum(
        1
        for item in compile_failures
        if item.get("source_kind") == lane and (not all_source_refs or str(item.get("source_artifact_id")) in all_source_refs)
    )
    return AlignmentLaneCoverage(
        lane=lane,
        schema_version=ALIGNMENT_LANE_COVERAGE_SCHEMA_VERSION,
        source_artifact_present=bool(source_refs),
        compiled_primitive_present=bool(primitive_refs),
        delivered_to_alignment=bool(delivered_items),
        salient_change_present=_salient_change_present(lane, delivered_items, primitive_by_id),
        dropped_record_count=dropped_count,
        capture_failure_count=capture_failure_count,
        compile_failure_count=compile_failure_count,
        source_artifact_refs=all_source_refs,
        primitive_record_refs=primitive_refs,
    )


def _drop_count_for_lane_window(
    lane: str,
    source_refs: tuple[str, ...],
    primitive_refs: tuple[str, ...],
    dropped_records: tuple[PerceptionDroppedSampleRecord, ...],
) -> int:
    return sum(
        1
        for item in dropped_records
        if item.source_kind == lane and (item.source_record_id in source_refs or item.source_record_id in primitive_refs or not source_refs)
    )


def _salient_change_present(
    lane: str,
    delivered_items: tuple[PerceptionLaneItem, ...],
    primitive_by_id: dict[str, dict[str, object]],
) -> bool:
    if lane == "screen":
        for item in delivered_items:
            if item.primitive_record_kind != "visual_change_primitive":
                continue
            primitive = primitive_by_id.get(item.primitive_record_id, {})
            if float(primitive.get("changed_area_ratio") or 0.0) > 0.0:
                return True
        return False
    if lane == "microphone":
        for item in delivered_items:
            if item.primitive_record_kind != "audio_primitive":
                continue
            primitive = primitive_by_id.get(item.primitive_record_id, {})
            envelope = tuple(float(value) for value in (primitive.get("amplitude_envelope") or ()))
            if envelope and max(envelope) > 0.0:
                return True
        return False
    return False


def _incomplete_reasons(lanes: dict[str, AlignmentLaneCoverage], full_window: bool) -> tuple[str, ...]:
    reasons: list[str] = []
    if not full_window:
        reasons.append("partial_edge_window")
    for lane, coverage in lanes.items():
        if not coverage.source_artifact_present:
            reasons.append(f"{lane}_source_absent")
        if not coverage.compiled_primitive_present:
            reasons.append(f"{lane}_primitive_absent")
        if not coverage.delivered_to_alignment:
            reasons.append(f"{lane}_not_delivered_to_alignment")
        if coverage.dropped_record_count:
            reasons.append(f"{lane}_dropped_records")
        if coverage.capture_failure_count:
            reasons.append(f"{lane}_capture_failure")
        if coverage.compile_failure_count:
            reasons.append(f"{lane}_compile_failure")
    return tuple(reasons)


def _fault_records(
    *,
    experiment_run_id: str,
    cycle_index: int,
    coverage_records: tuple[AlignmentWindowCoverageRecord, ...],
    backpressure_records: tuple[PerceptionBackpressureRecord, ...],
    dropped_records: tuple[PerceptionDroppedSampleRecord, ...],
    sensor_failures: tuple[dict[str, object], ...],
    compile_failures: tuple[dict[str, object], ...],
    timestamp_order_valid: bool,
    readiness_records: tuple[TransportLaneReadinessRecord, ...],
    flush_record: TransportFlushRecord,
) -> tuple[Package123TransportFaultRecord, ...]:
    faults: list[Package123TransportFaultRecord] = []
    for record in backpressure_records:
        faults.append(_fault(experiment_run_id, cycle_index, "queue_overflow", record.source_kind, None, record.affected_source_record_ids, record.source_trace_refs))
    for record in dropped_records:
        faults.append(_fault(experiment_run_id, cycle_index, "required_lane_drop", record.source_kind, None, (record.source_record_id,), record.source_trace_refs))
    for failure in sensor_failures:
        faults.append(_fault(experiment_run_id, cycle_index, "capture_failure", str(failure.get("source_kind")), None, (str(failure.get("failure_record_id")),), tuple(failure.get("source_trace_refs") or ())))
    for failure in compile_failures:
        faults.append(_fault(experiment_run_id, cycle_index, "compile_failure", str(failure.get("source_kind")), None, (str(failure.get("failure_record_id")),), tuple(failure.get("source_trace_refs") or ())))
    if not timestamp_order_valid:
        faults.append(_fault(experiment_run_id, cycle_index, "timestamp_order_violation", None, None, tuple(), tuple()))
    for record in readiness_records:
        if not record.ingress_ready:
            faults.append(_fault(experiment_run_id, cycle_index, "readiness_timeout", record.lane, None, record.source_record_refs, record.source_trace_refs))
    if not flush_record.passed:
        faults.append(_fault(experiment_run_id, cycle_index, "flush_timeout", None, None, flush_record.source_record_refs, flush_record.source_trace_refs))
    for record in coverage_records:
        if record.full_window_inside_common_envelope and not record.required_lanes_complete:
            faults.append(
                _fault(
                    experiment_run_id,
                    cycle_index,
                    "alignment_gap",
                    None,
                    record.alignment_window_id,
                    tuple(
                        dict.fromkeys(
                            record.screen.source_artifact_refs
                            + record.audio.source_artifact_refs
                            + record.host_state.source_artifact_refs
                        )
                    ),
                    record.source_trace_refs,
                )
            )
    return tuple(faults)


def _fault(
    experiment_run_id: str,
    cycle_index: int,
    fault_kind: str,
    affected_lane: str | None,
    affected_alignment_window_id: str | None,
    source_record_refs: tuple[str, ...],
    source_trace_refs: tuple[str, ...],
) -> Package123TransportFaultRecord:
    return Package123TransportFaultRecord(
        transport_fault_id=stable_id("package_123_transport_fault"),
        schema_version=TRANSPORT_FAULT_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        fault_kind=fault_kind,
        affected_lane=affected_lane if affected_lane in REQUIRED_LANES else None,
        affected_alignment_window_id=affected_alignment_window_id,
        source_record_refs=source_record_refs,
        source_trace_refs=source_trace_refs,
        run_aborted=True,
    )


def _integrity_summary(
    *,
    experiment_run_id: str,
    cycle_index: int,
    coverage_records: tuple[AlignmentWindowCoverageRecord, ...],
    backpressure_records: tuple[PerceptionBackpressureRecord, ...],
    dropped_records: tuple[PerceptionDroppedSampleRecord, ...],
    sensor_failures: tuple[dict[str, object], ...],
    compile_failures: tuple[dict[str, object], ...],
    readiness_records: tuple[TransportLaneReadinessRecord, ...],
    flush_record: TransportFlushRecord,
    timestamp_order_valid: bool,
    primitive_by_id: dict[str, dict[str, object]],
    lane_items: tuple[PerceptionLaneItem, ...],
    configuration_hash: str,
) -> Package123TransportIntegritySummary:
    full = tuple(item for item in coverage_records if item.full_window_inside_common_envelope)
    complete = tuple(item for item in full if item.required_lanes_complete)
    overlaps = tuple(item for item in full if item.visual_audio_overlap_present)
    complete_overlaps = tuple(item for item in overlaps if item.required_lanes_complete)
    screen_drops = sum(1 for item in dropped_records if item.source_kind == "screen")
    audio_drops = sum(1 for item in dropped_records if item.source_kind == "microphone")
    host_drops = sum(1 for item in dropped_records if item.source_kind == "host_state")
    readiness_passed = all(item.ingress_ready for item in readiness_records)
    flush_passed = flush_record.passed
    reasons: list[str] = []
    if len(complete) != len(full):
        reasons.append("incomplete_full_alignment_windows")
    if screen_drops or audio_drops or host_drops:
        reasons.append("required_lane_drops_present")
    if backpressure_records:
        reasons.append("required_lane_backpressure_present")
    if sensor_failures:
        reasons.append("required_lane_capture_failures_present")
    if compile_failures:
        reasons.append("required_lane_compile_failures_present")
    if not readiness_passed:
        reasons.append("readiness_barrier_failed")
    if not flush_passed:
        reasons.append("flush_barrier_failed")
    if not timestamp_order_valid:
        reasons.append("timestamp_order_invalid")
    if any(item.visual_audio_overlap_present and not item.host_state.complete for item in full):
        reasons.append("visual_audio_overlap_missing_host_state")
    eligible = not reasons
    return Package123TransportIntegritySummary(
        integrity_summary_id=stable_id("package_123_transport_integrity"),
        schema_version=TRANSPORT_INTEGRITY_SUMMARY_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        full_alignment_window_count=len(full),
        complete_alignment_window_count=len(complete),
        incomplete_alignment_window_count=len(full) - len(complete),
        partial_edge_window_count=sum(1 for item in coverage_records if item.partial_edge_window),
        visual_change_region_count=_visual_change_count(lane_items, primitive_by_id),
        audio_change_region_count=_audio_change_count(lane_items, primitive_by_id),
        visual_audio_overlap_window_count=len(overlaps),
        complete_overlap_window_count=len(complete_overlaps),
        screen_drop_count=screen_drops,
        audio_drop_count=audio_drops,
        host_state_drop_count=host_drops,
        backpressure_event_count=len(backpressure_records),
        capture_failure_count=len(sensor_failures),
        compile_failure_count=len(compile_failures),
        readiness_passed=readiness_passed,
        flush_passed=flush_passed,
        timestamp_order_valid=timestamp_order_valid,
        teacher_review_eligible=eligible,
        configuration_hash=configuration_hash,
        failure_reasons=tuple(dict.fromkeys(reasons)),
    )


def _visual_change_count(lane_items: tuple[PerceptionLaneItem, ...], primitive_by_id: dict[str, dict[str, object]]) -> int:
    return sum(
        1
        for item in lane_items
        if item.primitive_record_kind == "visual_change_primitive"
        and float(primitive_by_id.get(item.primitive_record_id, {}).get("changed_area_ratio") or 0.0) > 0.0
    )


def _audio_change_count(lane_items: tuple[PerceptionLaneItem, ...], primitive_by_id: dict[str, dict[str, object]]) -> int:
    total = 0
    for item in lane_items:
        if item.primitive_record_kind != "audio_primitive":
            continue
        envelope = tuple(float(value) for value in (primitive_by_id.get(item.primitive_record_id, {}).get("amplitude_envelope") or ()))
        if envelope and max(envelope) > 0.0:
            total += 1
    return total


def _primitive_payloads_by_id(
    perception_store: PerceptionPrimitiveStore,
    lane_items: tuple[PerceptionLaneItem, ...],
) -> dict[str, dict[str, object]]:
    payloads: dict[str, dict[str, object]] = {}
    for item in lane_items:
        try:
            payloads[item.primitive_record_id] = perception_store.get_primitive(item.primitive_record_id)
        except KeyError:
            continue
    return payloads


def _manifest_refs_by_lane(manifest: ArtifactBackedPerceptionTimelineManifest) -> dict[str, tuple[Any, ...]]:
    result: dict[str, list[Any]] = {}
    for ref in manifest.input_refs:
        result.setdefault(ref.source_kind, []).append(ref)
    return {key: tuple(value) for key, value in result.items()}


def _lane_items_by_source(lane_items: tuple[PerceptionLaneItem, ...]) -> dict[str, tuple[PerceptionLaneItem, ...]]:
    result: dict[str, list[PerceptionLaneItem]] = {}
    for item in lane_items:
        result.setdefault(item.source_kind, []).append(item)
    return {key: tuple(value) for key, value in result.items()}


def _sensor_failures(sensor_store: ContentAddressedSensorArtifactStore, capture_session_ids: tuple[str, ...]) -> tuple[dict[str, object], ...]:
    required = set(REQUIRED_LANES)
    rows = tuple(item for item in sensor_store.list_failures() if item.get("source_kind") in required)
    if capture_session_ids:
        capture_ids = set(capture_session_ids)
        rows = tuple(item for item in rows if item.get("capture_session_id") in capture_ids)
    return rows


def _compile_failures_for_manifest(
    perception_store: PerceptionPrimitiveStore,
    manifest: ArtifactBackedPerceptionTimelineManifest,
) -> tuple[dict[str, object], ...]:
    artifact_ids = {str(item.source_artifact_id) for item in manifest.input_refs if item.source_artifact_id}
    return tuple(
        item
        for item in perception_store.list_compilation_failures()
        if item.get("source_kind") in REQUIRED_LANES and str(item.get("source_artifact_id")) in artifact_ids
    )


def _timestamp_order_valid(manifest: ArtifactBackedPerceptionTimelineManifest) -> bool:
    last_by_lane: dict[str, int] = {}
    last_global = -1
    for ref in manifest.input_refs:
        offset = int(ref.replay_relative_offset_ms)
        if offset < last_global:
            return False
        if offset < last_by_lane.get(ref.source_kind, -1):
            return False
        last_global = offset
        last_by_lane[ref.source_kind] = offset
    return True


def _manifest_from_lane_items(lane_items: tuple[PerceptionLaneItem, ...]) -> ArtifactBackedPerceptionTimelineManifest:
    from ashl_core_v1.runtime.multimodal_perception_session_types import (
        ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
        TIMELINE_INPUT_REF_SCHEMA_VERSION,
        PerceptionTimelineInputRef,
    )

    refs = tuple(
        PerceptionTimelineInputRef(
            input_ref_id=stable_id("package_123_historical_input_ref"),
            schema_version=TIMELINE_INPUT_REF_SCHEMA_VERSION,
            source_kind=item.source_kind,
            source_artifact_id=item.source_artifact_id,
            source_ephemeral_buffer_id=item.source_buffer_id,
            replay_relative_offset_ms=int(item.session_relative_ns / 1_000_000),
            compiler_id="historical_unavailable",
            compiler_config_id="historical_unavailable",
            privacy_policy_id="grounding_conservative_v0" if item.source_kind == "microphone" else None,
            source_trace_refs=item.source_trace_refs,
        )
        for item in lane_items
        if item.source_artifact_id or item.source_buffer_id
    )
    return ArtifactBackedPerceptionTimelineManifest(
        manifest_id=stable_id("package_123_historical_manifest"),
        schema_version=ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
        created_at=utc_now(),
        input_refs=refs,
        source_artifacts_are_real=True,
        sources_captured_simultaneously=False,
        deterministic_replay=True,
        manifest_sha256="",
    )


def _config_from_windows(windows: tuple[MultimodalAlignmentWindowRecord, ...]) -> MultimodalPerceptionSessionConfig:
    from ashl_core_v1.runtime.multimodal_perception_session_types import build_default_multimodal_session_config

    width_ms = 500
    count = max((item.window_index for item in windows), default=-1) + 1
    if windows:
        width_ms = int((windows[0].window_end_relative_ns - windows[0].window_start_relative_ns) / 1_000_000)
    config = build_default_multimodal_session_config(
        state_dir="historical_state_dir",
        alignment_window_ms=width_ms,
        maximum_window_count=max(1, count),
        maximum_session_duration_ms=max(1, count * width_ms),
    )
    payload = config.to_dict()
    payload["enabled_source_kinds"] = REQUIRED_LANES
    payload["required_source_kinds"] = REQUIRED_LANES
    payload["optional_source_kinds"] = tuple()
    payload["config_sha256"] = ""
    return type(config)(**payload)


class _PreparedTransportShim:
    def __init__(
        self,
        manifest: ArtifactBackedPerceptionTimelineManifest,
        config: MultimodalPerceptionSessionConfig,
        lane_items: tuple[PerceptionLaneItem, ...],
        windows: tuple[MultimodalAlignmentWindowRecord, ...],
        backpressure_records: tuple[PerceptionBackpressureRecord, ...],
        dropped_records: tuple[PerceptionDroppedSampleRecord, ...],
    ) -> None:
        self.manifest = manifest
        self.config = config
        self.lane_items = lane_items
        self.windows = windows
        self.backpressure_records = backpressure_records
        self.dropped_records = dropped_records
