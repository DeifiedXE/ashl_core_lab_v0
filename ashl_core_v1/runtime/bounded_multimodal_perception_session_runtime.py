"""Bounded multimodal perception session runtime for Package 122."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.perception.hard_soft_perception_primitive_compiler import HardSoftPerceptionPrimitiveCompiler
from ashl_core_v1.perception.perception_primitive_store import PerceptionPrimitiveStore
from ashl_core_v1.runtime.bounded_embodied_session_runtime import BoundedEmbodiedSessionRuntime, BoundedEmbodiedSessionStatus
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import canonical_json, monotonic_ns, plain, sha256_payload, stable_id, utc_now
from ashl_core_v1.runtime.multimodal_alignment_window import assemble_alignment_windows
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
    BACKPRESSURE_SCHEMA_VERSION,
    DROPPED_SAMPLE_SCHEMA_VERSION,
    HOST_BODY_BRIDGE_SCHEMA_VERSION,
    LANE_ITEM_SCHEMA_VERSION,
    SESSION_AUDIT_SCHEMA_VERSION,
    SESSION_CONFIG_SCHEMA_VERSION,
    SESSION_RESULT_SCHEMA_VERSION,
    TIMELINE_SCHEMA_VERSION,
    ALIGNMENT_WINDOW_SCHEMA_VERSION,
    ArtifactBackedPerceptionTimelineManifest,
    BoundedMultimodalPerceptionSessionAuditRecord,
    BoundedMultimodalPerceptionSessionResult,
    MultimodalPerceptionSessionConfig,
    MultimodalPerceptionSessionMode,
    PerceptionBackpressureRecord,
    PerceptionDroppedSampleRecord,
    PerceptionLaneItem,
    build_default_multimodal_session_config,
)
from ashl_core_v1.runtime.perception_lane_queue import PerceptionLaneQueue
from ashl_core_v1.runtime.perception_low_level_event_policy import build_default_low_level_event_policy, choose_low_level_event_kind
from ashl_core_v1.runtime.perception_timeline import build_multimodal_perception_timeline
from ashl_core_v1.runtime.perception_to_host_body_event_adapter import (
    build_perception_host_body_event,
    build_perception_host_body_event_bridge_record,
)
from ashl_core_v1.runtime.trace_envelope import TraceEnvelope, build_trace_envelope


MULTIMODAL_STORE_DIRNAME = "bounded_multimodal_perception_sessions_v0"
MULTIMODAL_STORE_FILENAME = "multimodal_sessions.sqlite3"


@dataclass(frozen=True)
class PreparedArtifactReplayTransport:
    session_id: str
    manifest: ArtifactBackedPerceptionTimelineManifest
    config: MultimodalPerceptionSessionConfig
    lane_items: tuple[PerceptionLaneItem, ...]
    backpressure_records: tuple[PerceptionBackpressureRecord, ...]
    dropped_records: tuple[PerceptionDroppedSampleRecord, ...]
    windows: tuple[Any, ...]
    timeline: Any
    source_trace_refs: tuple[str, ...]


@dataclass(frozen=True)
class PreparedLiveCompiledTransport:
    session_id: str
    config: MultimodalPerceptionSessionConfig
    lane_items: tuple[PerceptionLaneItem, ...]
    backpressure_records: tuple[PerceptionBackpressureRecord, ...]
    dropped_records: tuple[PerceptionDroppedSampleRecord, ...]
    windows: tuple[Any, ...]
    timeline: Any
    source_trace_refs: tuple[str, ...]


@dataclass(frozen=True)
class ActiveCompiledAlignmentView:
    """Read-only alignment view over records captured by an active window."""

    session_id: str
    config: MultimodalPerceptionSessionConfig
    lane_items: tuple[PerceptionLaneItem, ...]
    windows: tuple[Any, ...]
    source_trace_refs: tuple[str, ...]


class MultimodalPerceptionSessionStore:
    def __init__(self, state_dir: str | Path) -> None:
        self.state_dir = Path(state_dir)
        self.root_dir = self.state_dir / MULTIMODAL_STORE_DIRNAME
        self.db_path = self.root_dir / MULTIMODAL_STORE_FILENAME
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.db_path))
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def connection(self) -> Any:
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def append_payload(self, table: str, id_column: str, record_id: str, payload: dict[str, Any]) -> None:
        with self.connection() as connection:
            connection.execute(
                f"INSERT INTO {table} ({id_column}, created_at, payload_json, payload_sha256) VALUES (?, ?, ?, ?)",
                (
                    record_id,
                    str(payload.get("created_at", utc_now())),
                    canonical_json(payload),
                    sha256_payload(payload),
                ),
            )

    def append_trace(self, trace: TraceEnvelope) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO multimodal_trace_envelopes (
                    trace_id, trace_schema_version, session_id, event_id, parent_event_id,
                    root_event_id, sequence_index, monotonic_tick, nesting_depth,
                    source_line, source_module, record_kind, record_id, trace_layer,
                    payload_schema, payload_snapshot_json, source_trace_refs_json,
                    source_record_refs_json, created_at, append_only, time_aligned,
                    payload_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trace.trace_id,
                    trace.trace_schema_version,
                    trace.session_id,
                    trace.event_id,
                    trace.parent_event_id,
                    trace.root_event_id,
                    trace.sequence_index,
                    trace.monotonic_tick,
                    trace.nesting_depth,
                    trace.source_line,
                    trace.source_module,
                    trace.record_kind,
                    trace.record_id,
                    trace.trace_layer,
                    trace.payload_schema,
                    canonical_json(trace.payload_snapshot),
                    canonical_json(trace.source_trace_refs),
                    canonical_json(trace.source_record_refs),
                    trace.created_at,
                    1 if trace.append_only else 0,
                    1 if trace.time_aligned else 0,
                    sha256_payload(trace.to_dict()),
                ),
            )

    def next_trace_sequence(self, session_id: str) -> int:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM multimodal_trace_envelopes WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        return int(row["count"])

    def get_payload(self, table: str, id_column: str, record_id: str) -> dict[str, Any]:
        rows = self.list_payloads(table, f"{id_column} = ?", (record_id,))
        if not rows:
            raise KeyError(f"missing {table} row: {record_id}")
        return rows[0]

    def list_payloads(self, table: str, where: str = "1 = 1", args: tuple[Any, ...] = tuple()) -> tuple[dict[str, Any], ...]:
        with self.connection() as connection:
            rows = connection.execute(f"SELECT payload_json FROM {table} WHERE {where} ORDER BY created_at", args).fetchall()
        return tuple(json.loads(str(row["payload_json"])) for row in rows)

    def list_traces(self, session_id: str | None = None) -> tuple[TraceEnvelope, ...]:
        where = "session_id = ?" if session_id else "1 = 1"
        args = (session_id,) if session_id else tuple()
        with self.connection() as connection:
            rows = connection.execute(
                f"SELECT * FROM multimodal_trace_envelopes WHERE {where} ORDER BY sequence_index",
                args,
            ).fetchall()
        return tuple(_trace_from_row(dict(row)) for row in rows)

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS multimodal_session_configs (
                    config_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS artifact_replay_manifests (
                    manifest_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS perception_lane_items (
                    lane_item_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS multimodal_alignment_windows (
                    alignment_window_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS multimodal_timelines (
                    timeline_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS perception_backpressure_records (
                    backpressure_record_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS perception_dropped_sample_records (
                    dropped_sample_record_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS perception_host_body_event_bridges (
                    bridge_record_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS internal_perception_focus_context_sidecars (
                    focus_context_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS multimodal_session_results (
                    result_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS multimodal_session_audits (
                    audit_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS multimodal_trace_envelopes (
                    trace_id TEXT PRIMARY KEY,
                    trace_schema_version TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    parent_event_id TEXT,
                    root_event_id TEXT NOT NULL,
                    sequence_index INTEGER NOT NULL,
                    monotonic_tick INTEGER NOT NULL,
                    nesting_depth INTEGER NOT NULL,
                    source_line TEXT NOT NULL,
                    source_module TEXT NOT NULL,
                    record_kind TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    trace_layer TEXT NOT NULL,
                    payload_schema TEXT NOT NULL,
                    payload_snapshot_json TEXT NOT NULL,
                    source_trace_refs_json TEXT NOT NULL,
                    source_record_refs_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    append_only INTEGER NOT NULL,
                    time_aligned INTEGER NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                """
            )


class BoundedMultimodalPerceptionSessionRuntime:
    def __init__(self, state_dir: str | Path) -> None:
        self.state_dir = Path(state_dir)
        self.store = MultimodalPerceptionSessionStore(self.state_dir)
        self.sensor_store = ContentAddressedSensorArtifactStore(self.state_dir)
        self.perception_compiler = HardSoftPerceptionPrimitiveCompiler(self.state_dir)
        self.perception_store = PerceptionPrimitiveStore(self.state_dir)
        self.embodied_runtime = BoundedEmbodiedSessionRuntime()
        self._traces: dict[str, list[str]] = {}

    def attach_internal_perception_focus_context(
        self,
        sidecar: Any,
        *,
        active_lane_items: tuple[PerceptionLaneItem, ...] = tuple(),
    ) -> dict[str, Any]:
        """Attach one read-only focus index to an existing full-frame lane."""

        payload = (
            sidecar.to_dict()
            if hasattr(sidecar, "to_dict")
            else dict(sidecar)
        )
        session_id = str(payload["child_perception_session_id"])
        readable_id = str(
            payload["full_frame_perception_readable_data_id"]
        )
        lane_items = tuple(
            item
            for item in self.store.list_payloads(
                "perception_lane_items"
            )
            if item.get("session_id") == session_id
        )
        persisted_matching = tuple(
            item
            for item in lane_items
            if item.get("source_kind") == "screen"
            and item.get("perception_readable_data_id") == readable_id
        )
        active_matching = tuple(
            item
            for item in active_lane_items
            if item.session_id == session_id
            and item.source_kind == "screen"
            and item.perception_readable_data_id == readable_id
        )
        matching = persisted_matching + active_matching
        if not matching:
            raise ValueError(
                "focus sidecar full-frame readable-data lineage mismatch"
            )
        if payload.get("read_only_context") is not True:
            raise ValueError("focus sidecar must be read-only")
        self.store.append_payload(
            "internal_perception_focus_context_sidecars",
            "focus_context_id",
            str(payload["focus_context_id"]),
            payload,
        )
        return payload

    def inspect_active_compiled_alignment(
        self,
        *,
        lane_items: tuple[PerceptionLaneItem, ...],
        config: MultimodalPerceptionSessionConfig,
        session_id: str,
    ) -> ActiveCompiledAlignmentView:
        """Build a bounded alignment view without finalizing or persisting it."""

        if (
            config.mode
            != MultimodalPerceptionSessionMode.LIVE_BOUNDED_MULTIMODAL_CAPTURE.value
        ):
            raise ValueError(
                "active alignment view requires live_bounded_multimodal_capture mode"
            )
        if not lane_items:
            raise ValueError("active alignment view requires lane items")
        if any(item.session_id != session_id for item in lane_items):
            raise ValueError("active lane item session identity mismatch")
        present = {item.source_kind for item in lane_items}
        missing = set(config.required_source_kinds) - present
        if missing:
            raise ValueError(
                f"active alignment view missing required lanes: {sorted(missing)}"
            )
        sorted_items = tuple(
            sorted(
                lane_items,
                key=lambda item: (
                    item.session_relative_ns,
                    item.lane_item_id,
                ),
            )
        )
        lane_limits = {
            "camera": config.camera_queue_depth,
            "screen": config.screen_queue_depth,
            "microphone": config.microphone_queue_depth,
            "host_state": config.host_state_queue_depth,
        }
        for lane, limit in lane_limits.items():
            count = sum(
                1 for item in sorted_items if item.source_kind == lane
            )
            if count > int(limit):
                raise ValueError(
                    f"active alignment view exceeds {lane} queue depth"
                )
        windows = assemble_alignment_windows(
            session_id=session_id,
            config=config,
            lane_items=sorted_items,
        )
        return ActiveCompiledAlignmentView(
            session_id=session_id,
            config=config,
            lane_items=sorted_items,
            windows=windows,
            source_trace_refs=tuple(
                dict.fromkeys(
                    ref
                    for item in sorted_items
                    for ref in item.source_trace_refs
                )
            ),
        )

    def run_artifact_backed_alignment_replay(
        self,
        manifest: ArtifactBackedPerceptionTimelineManifest,
        *,
        config: MultimodalPerceptionSessionConfig | None = None,
        working_readback_snapshot: tuple[dict[str, Any], ...] | list[dict[str, Any]] | None = None,
    ) -> BoundedMultimodalPerceptionSessionResult:
        prepared = self.prepare_artifact_backed_alignment_replay_transport(
            manifest,
            config=config,
        )
        return self.run_prepared_artifact_replay_to_teacher_gate(
            prepared,
            working_readback_snapshot=working_readback_snapshot,
        )

    def prepare_live_compiled_alignment_transport(
        self,
        *,
        lane_items: tuple[PerceptionLaneItem, ...],
        config: MultimodalPerceptionSessionConfig,
        session_id: str,
    ) -> PreparedLiveCompiledTransport:
        """Align already compiled live records without replay or teacher dispatch."""

        if config.mode != MultimodalPerceptionSessionMode.LIVE_BOUNDED_MULTIMODAL_CAPTURE.value:
            raise ValueError("live compiled transport requires live_bounded_multimodal_capture mode")
        if not lane_items:
            raise ValueError("live compiled transport requires lane items")
        if any(item.session_id != session_id for item in lane_items):
            raise ValueError("live lane item session identity mismatch")
        present = {item.source_kind for item in lane_items}
        missing = set(config.required_source_kinds) - present
        if missing:
            raise ValueError(f"live compiled transport missing required lanes: {sorted(missing)}")
        existing_timelines = self.store.list_payloads("multimodal_timelines")
        if any(item.get("session_id") == session_id for item in existing_timelines):
            raise ValueError("perception session_id already exists")

        self._traces[session_id] = []
        self.store.append_payload(
            "multimodal_session_configs",
            "config_id",
            config.config_id,
            config.to_dict(),
        )
        self._append_trace(
            session_id=session_id,
            record_kind="multimodal_session_started",
            record_id=session_id,
            payload_schema=SESSION_CONFIG_SCHEMA_VERSION,
            payload_snapshot={
                "mode": config.mode,
                "artifact_backed_replay": False,
                "live_precompiled_lanes": True,
                "real_life_experience_claimed": False,
                "config_sha256": config.config_sha256,
            },
            source_trace_refs=tuple(
                dict.fromkeys(ref for item in lane_items for ref in item.source_trace_refs)
            ),
        )
        accepted, backpressure, dropped = self._queue_live_lane_items(
            session_id=session_id,
            config=config,
            lane_items=lane_items,
        )
        windows = assemble_alignment_windows(
            session_id=session_id,
            config=config,
            lane_items=accepted,
        )
        for window in windows:
            self.store.append_payload(
                "multimodal_alignment_windows",
                "alignment_window_id",
                window.alignment_window_id,
                window.to_dict(),
            )
        timeline = build_multimodal_perception_timeline(
            session_id=session_id,
            config=config,
            lane_items=accepted,
            alignment_window_ids=tuple(
                window.alignment_window_id for window in windows
            ),
        )
        self.store.append_payload(
            "multimodal_timelines",
            "timeline_id",
            timeline.timeline_id,
            timeline.to_dict(),
        )
        refs = tuple(
            dict.fromkeys(
                tuple(ref for item in accepted for ref in item.source_trace_refs)
                + tuple(self._traces.get(session_id, ()))
            )
        )
        return PreparedLiveCompiledTransport(
            session_id=session_id,
            config=config,
            lane_items=accepted,
            backpressure_records=backpressure,
            dropped_records=dropped,
            windows=windows,
            timeline=timeline,
            source_trace_refs=refs,
        )

    def lane_item_from_compilation(
        self,
        *,
        session_id: str,
        session_relative_ms: int,
        compilation_bundle: Any,
    ) -> PerceptionLaneItem:
        return self._lane_item_from_bundle(
            session_id,
            session_relative_ms,
            compilation_bundle,
        )

    def prepare_artifact_backed_alignment_replay_transport(
        self,
        manifest: ArtifactBackedPerceptionTimelineManifest,
        *,
        config: MultimodalPerceptionSessionConfig | None = None,
        session_id: str | None = None,
    ) -> PreparedArtifactReplayTransport:
        config = config or build_default_multimodal_session_config(state_dir=self.state_dir)
        if config.mode != MultimodalPerceptionSessionMode.ARTIFACT_BACKED_ALIGNMENT_REPLAY.value:
            raise ValueError("artifact replay requires artifact_backed_alignment_replay mode")
        self._validate_manifest_sources(manifest, config)
        multimodal_session_id = session_id or stable_id("bounded_multimodal_perception_session")
        if session_id:
            existing_timelines = self.store.list_payloads("multimodal_timelines")
            if any(item.get("session_id") == session_id for item in existing_timelines):
                raise ValueError("perception session_id already exists")
        self._traces[multimodal_session_id] = []
        self.store.append_payload("multimodal_session_configs", "config_id", config.config_id, config.to_dict())
        self.store.append_payload("artifact_replay_manifests", "manifest_id", manifest.manifest_id, manifest.to_dict())
        self._append_trace(
            session_id=multimodal_session_id,
            record_kind="multimodal_session_started",
            record_id=multimodal_session_id,
            payload_schema=SESSION_CONFIG_SCHEMA_VERSION,
            payload_snapshot={
                "mode": config.mode,
                "artifact_backed_replay": True,
                "sources_captured_simultaneously": False,
                "real_life_experience_claimed": False,
                "config_sha256": config.config_sha256,
            },
            source_trace_refs=tuple(ref for item in manifest.input_refs for ref in item.source_trace_refs),
        )
        lane_items, backpressure_records, dropped_records = self._compile_manifest_to_lane_items(
            session_id=multimodal_session_id,
            manifest=manifest,
            config=config,
        )
        windows = assemble_alignment_windows(session_id=multimodal_session_id, config=config, lane_items=lane_items)
        for window in windows:
            self.store.append_payload("multimodal_alignment_windows", "alignment_window_id", window.alignment_window_id, window.to_dict())
            self._append_trace(
                session_id=multimodal_session_id,
                record_kind="multimodal_alignment_window",
                record_id=window.alignment_window_id,
                payload_schema=ALIGNMENT_WINDOW_SCHEMA_VERSION,
                payload_snapshot=window.to_dict(),
                source_trace_refs=window.source_trace_refs,
            )
        timeline = build_multimodal_perception_timeline(
            session_id=multimodal_session_id,
            config=config,
            lane_items=lane_items,
            alignment_window_ids=tuple(window.alignment_window_id for window in windows),
        )
        self.store.append_payload("multimodal_timelines", "timeline_id", timeline.timeline_id, timeline.to_dict())
        self._append_trace(
            session_id=multimodal_session_id,
            record_kind="multimodal_session_timeline",
            record_id=timeline.timeline_id,
            payload_schema=TIMELINE_SCHEMA_VERSION,
            payload_snapshot=timeline.to_dict(),
            source_trace_refs=timeline.source_trace_refs,
        )
        return PreparedArtifactReplayTransport(
            session_id=multimodal_session_id,
            manifest=manifest,
            config=config,
            lane_items=lane_items,
            backpressure_records=backpressure_records,
            dropped_records=dropped_records,
            windows=windows,
            timeline=timeline,
            source_trace_refs=tuple(dict.fromkeys(timeline.source_trace_refs + tuple(self._traces.get(multimodal_session_id, ())))),
        )

    def run_prepared_artifact_replay_to_teacher_gate(
        self,
        prepared: PreparedArtifactReplayTransport,
        *,
        working_readback_snapshot: tuple[dict[str, Any], ...] | list[dict[str, Any]] | None = None,
    ) -> BoundedMultimodalPerceptionSessionResult:
        multimodal_session_id = prepared.session_id
        config = prepared.config
        lane_items = prepared.lane_items
        windows = prepared.windows
        timeline = prepared.timeline
        package_115_state = self.embodied_runtime.create_session()
        package_115_session_id = package_115_state.session_id
        if working_readback_snapshot:
            self.embodied_runtime.attach_working_readback_snapshot(
                package_115_session_id,
                tuple(working_readback_snapshot),
            )
        bridge_ids: list[str] = []
        host_event_ids: list[str] = []
        pending_review_ids: tuple[str, ...] = tuple()
        policy = build_default_low_level_event_policy()
        for window in windows:
            window_items = _items_for_window(window, lane_items)
            if not window_items:
                continue
            event_kind = choose_low_level_event_kind(window, policy=policy)
            host_event = build_perception_host_body_event(
                session_id=multimodal_session_id,
                timeline_id=timeline.timeline_id,
                window=window,
                lane_items=window_items,
                emitted_event_kind=event_kind,
            )
            self.embodied_runtime.inject_host_body_event_record(
                package_115_session_id,
                host_event,
                fixture_kind="artifact_backed_multimodal_perception_replay",
                source_record_refs=(window.alignment_window_id,) + tuple(item.primitive_record_id for item in window_items),
            )
            bridge = build_perception_host_body_event_bridge_record(
                session_id=multimodal_session_id,
                timeline_id=timeline.timeline_id,
                window=window,
                emitted_event_kind=event_kind,
                host_body_event=host_event,
                lane_items=window_items,
                package_115_injection_succeeded=True,
            )
            bridge_ids.append(bridge.bridge_record_id)
            host_event_ids.append(host_event.host_body_event_id)
            self.store.append_payload("perception_host_body_event_bridges", "bridge_record_id", bridge.bridge_record_id, bridge.to_dict())
            self._append_trace(
                session_id=multimodal_session_id,
                record_kind="perception_host_body_event_bridge",
                record_id=bridge.bridge_record_id,
                payload_schema=HOST_BODY_BRIDGE_SCHEMA_VERSION,
                payload_snapshot=bridge.to_dict(),
                source_trace_refs=bridge.source_trace_refs,
            )
            run_result = self.embodied_runtime.run_until_blocked(package_115_session_id)
            pending_review_ids = run_result.pending_teacher_review_ids
            if self.embodied_runtime._states[package_115_session_id].status == BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW:
                break
        status = self.embodied_runtime._states[package_115_session_id].status
        stopped_at_teacher_gate = status == BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW
        result = BoundedMultimodalPerceptionSessionResult(
            result_id=stable_id("bounded_multimodal_perception_result"),
            schema_version=SESSION_RESULT_SCHEMA_VERSION,
            created_at=utc_now(),
            session_id=multimodal_session_id,
            mode=config.mode,
            config_id=config.config_id,
            config_sha256=config.config_sha256,
            timeline_id=timeline.timeline_id,
            compiled_primitive_ids=tuple(item.primitive_record_id for item in lane_items),
            perception_readable_data_ids=tuple(item.perception_readable_data_id for item in lane_items),
            alignment_window_ids=tuple(window.alignment_window_id for window in windows),
            bridge_record_ids=tuple(bridge_ids),
            host_body_event_ids=tuple(host_event_ids),
            backpressure_record_ids=tuple(item.backpressure_record_id for item in prepared.backpressure_records),
            dropped_sample_record_ids=tuple(item.dropped_sample_record_id for item in prepared.dropped_records),
            compilation_failure_ids=tuple(),
            package_115_session_id=package_115_session_id,
            pending_teacher_review_ids=pending_review_ids,
            stopped_at_teacher_gate=stopped_at_teacher_gate,
            automatic_teacher_decision_created=False,
            bounded_stop_reason="teacher_review_boundary" if stopped_at_teacher_gate else "completed_without_teacher_gate",
            result_status="completed_artifact_backed_replay" if stopped_at_teacher_gate else "completed_no_eventful_window",
            source_trace_refs=prepared.source_trace_refs,
        )
        self.store.append_payload("multimodal_session_results", "result_id", result.result_id, result.to_dict())
        self._append_trace(
            session_id=multimodal_session_id,
            record_kind="multimodal_session_stopped",
            record_id=result.result_id,
            payload_schema=SESSION_RESULT_SCHEMA_VERSION,
            payload_snapshot=result.to_dict(),
            source_trace_refs=result.source_trace_refs,
        )
        audit = audit_bounded_multimodal_perception_session(self.state_dir, result.session_id)
        self.store.append_payload("multimodal_session_audits", "audit_id", audit.audit_id, audit.to_dict())
        return result

    def _compile_manifest_to_lane_items(
        self,
        *,
        session_id: str,
        manifest: ArtifactBackedPerceptionTimelineManifest,
        config: MultimodalPerceptionSessionConfig,
    ) -> tuple[tuple[PerceptionLaneItem, ...], tuple[PerceptionBackpressureRecord, ...], tuple[PerceptionDroppedSampleRecord, ...]]:
        queues = {
            "camera": PerceptionLaneQueue(session_id=session_id, source_kind="camera", queue_depth_limit=config.camera_queue_depth, drop_policy=config.camera_drop_policy),
            "screen": PerceptionLaneQueue(session_id=session_id, source_kind="screen", queue_depth_limit=config.screen_queue_depth, drop_policy=config.screen_drop_policy),
            "microphone": PerceptionLaneQueue(session_id=session_id, source_kind="microphone", queue_depth_limit=config.microphone_queue_depth, drop_policy=config.microphone_drop_policy),
            "host_state": PerceptionLaneQueue(session_id=session_id, source_kind="host_state", queue_depth_limit=config.host_state_queue_depth, drop_policy=config.host_state_drop_policy),
        }
        lane_items: list[PerceptionLaneItem] = []
        backpressure: list[PerceptionBackpressureRecord] = []
        dropped: list[PerceptionDroppedSampleRecord] = []
        previous_visual: dict[str, str] = {}
        for input_ref in manifest.input_refs:
            if not input_ref.source_artifact_id:
                raise ValueError("artifact replay input must use source_artifact_id")
            bundle = self.perception_compiler.compile_artifact(input_ref.source_artifact_id)
            item = self._lane_item_from_bundle(session_id, input_ref.replay_relative_offset_ms, bundle)
            result = queues[item.source_kind].push(item)
            backpressure.extend(result.backpressure_records)
            dropped.extend(result.dropped_sample_records)
            if result.accepted:
                lane_items.append(item)
                self.store.append_payload("perception_lane_items", "lane_item_id", item.lane_item_id, item.to_dict())
                self._append_trace(
                    session_id=session_id,
                    record_kind="perception_lane_item",
                    record_id=item.lane_item_id,
                    payload_schema=LANE_ITEM_SCHEMA_VERSION,
                    payload_snapshot=item.to_dict(),
                    source_trace_refs=item.source_trace_refs,
                )
            if input_ref.source_kind in {"camera", "screen"}:
                previous_artifact = previous_visual.get(input_ref.source_kind)
                if previous_artifact:
                    change_bundle = self.perception_compiler.compile_visual_pair(
                        previous_artifact_id=previous_artifact,
                        current_artifact_id=input_ref.source_artifact_id,
                    )
                    change_item = self._lane_item_from_bundle(session_id, input_ref.replay_relative_offset_ms, change_bundle)
                    change_result = queues[change_item.source_kind].push(change_item)
                    backpressure.extend(change_result.backpressure_records)
                    dropped.extend(change_result.dropped_sample_records)
                    if change_result.accepted:
                        lane_items.append(change_item)
                        self.store.append_payload("perception_lane_items", "lane_item_id", change_item.lane_item_id, change_item.to_dict())
                        self._append_trace(
                            session_id=session_id,
                            record_kind="perception_lane_item",
                            record_id=change_item.lane_item_id,
                            payload_schema=LANE_ITEM_SCHEMA_VERSION,
                            payload_snapshot=change_item.to_dict(),
                            source_trace_refs=change_item.source_trace_refs,
                        )
                previous_visual[input_ref.source_kind] = input_ref.source_artifact_id
        for record in backpressure:
            self.store.append_payload("perception_backpressure_records", "backpressure_record_id", record.backpressure_record_id, record.to_dict())
            self._append_trace(session_id=session_id, record_kind="perception_backpressure", record_id=record.backpressure_record_id, payload_schema=BACKPRESSURE_SCHEMA_VERSION, payload_snapshot=record.to_dict(), source_trace_refs=record.source_trace_refs)
        for record in dropped:
            self.store.append_payload("perception_dropped_sample_records", "dropped_sample_record_id", record.dropped_sample_record_id, record.to_dict())
            self._append_trace(session_id=session_id, record_kind="perception_dropped_sample", record_id=record.dropped_sample_record_id, payload_schema=DROPPED_SAMPLE_SCHEMA_VERSION, payload_snapshot=record.to_dict(), source_trace_refs=record.source_trace_refs)
        lane_items.sort(key=lambda item: (item.session_relative_ns, item.lane_item_id))
        return tuple(lane_items), tuple(backpressure), tuple(dropped)

    def _queue_live_lane_items(
        self,
        *,
        session_id: str,
        config: MultimodalPerceptionSessionConfig,
        lane_items: tuple[PerceptionLaneItem, ...],
    ) -> tuple[
        tuple[PerceptionLaneItem, ...],
        tuple[PerceptionBackpressureRecord, ...],
        tuple[PerceptionDroppedSampleRecord, ...],
    ]:
        queues = {
            "camera": PerceptionLaneQueue(
                session_id=session_id,
                source_kind="camera",
                queue_depth_limit=config.camera_queue_depth,
                drop_policy=config.camera_drop_policy,
            ),
            "screen": PerceptionLaneQueue(
                session_id=session_id,
                source_kind="screen",
                queue_depth_limit=config.screen_queue_depth,
                drop_policy=config.screen_drop_policy,
            ),
            "microphone": PerceptionLaneQueue(
                session_id=session_id,
                source_kind="microphone",
                queue_depth_limit=config.microphone_queue_depth,
                drop_policy=config.microphone_drop_policy,
            ),
            "host_state": PerceptionLaneQueue(
                session_id=session_id,
                source_kind="host_state",
                queue_depth_limit=config.host_state_queue_depth,
                drop_policy=config.host_state_drop_policy,
            ),
        }
        accepted: list[PerceptionLaneItem] = []
        backpressure: list[PerceptionBackpressureRecord] = []
        dropped: list[PerceptionDroppedSampleRecord] = []
        for item in sorted(
            lane_items,
            key=lambda value: (value.session_relative_ns, value.lane_item_id),
        ):
            result = queues[item.source_kind].push(item)
            backpressure.extend(result.backpressure_records)
            dropped.extend(result.dropped_sample_records)
            if result.accepted:
                accepted.append(item)
                self.store.append_payload(
                    "perception_lane_items",
                    "lane_item_id",
                    item.lane_item_id,
                    item.to_dict(),
                )
        for record in backpressure:
            self.store.append_payload(
                "perception_backpressure_records",
                "backpressure_record_id",
                record.backpressure_record_id,
                record.to_dict(),
            )
        for record in dropped:
            self.store.append_payload(
                "perception_dropped_sample_records",
                "dropped_sample_record_id",
                record.dropped_sample_record_id,
                record.to_dict(),
            )
        return tuple(accepted), tuple(backpressure), tuple(dropped)

    def _lane_item_from_bundle(self, session_id: str, offset_ms: int, bundle: Any) -> PerceptionLaneItem:
        primitive = self.perception_store.get_primitive(bundle.primitive_record_id)
        readable = self.perception_store.get_perception_readable_data(bundle.perception_readable_data_id)
        uncertainty = float(primitive.get("quality_uncertainty", readable.get("uncertainty", 0.0)) or 0.0)
        return PerceptionLaneItem(
            lane_item_id=stable_id("perception_lane_item"),
            schema_version=LANE_ITEM_SCHEMA_VERSION,
            session_id=session_id,
            source_kind=bundle.source_kind,
            source_artifact_id=bundle.source_artifact_id,
            source_buffer_id=bundle.source_buffer_id,
            source_monotonic_ns=monotonic_ns(),
            session_relative_ns=offset_ms * 1_000_000,
            primitive_record_kind=bundle.primitive_record_kind,
            primitive_record_id=bundle.primitive_record_id,
            perception_readable_data_id=bundle.perception_readable_data_id,
            quality_uncertainty=uncertainty,
            source_trace_refs=bundle.source_trace_refs,
        )

    def _validate_manifest_sources(
        self,
        manifest: ArtifactBackedPerceptionTimelineManifest,
        config: MultimodalPerceptionSessionConfig,
    ) -> None:
        kinds = {item.source_kind for item in manifest.input_refs}
        enabled = set(config.enabled_source_kinds)
        required = set(config.required_source_kinds)
        unexpected = kinds - enabled
        if unexpected:
            raise ValueError(f"artifact replay manifest contains disabled sources: {sorted(unexpected)}")
        missing = required - kinds
        if missing:
            raise ValueError(f"artifact replay manifest missing required sources: {sorted(missing)}")
        for input_ref in manifest.input_refs:
            if not input_ref.source_artifact_id:
                raise ValueError("artifact replay requires source artifacts")
            artifact = self.sensor_store.get_artifact(input_ref.source_artifact_id)
            if artifact.get("source_kind") != input_ref.source_kind:
                raise ValueError("artifact source_kind mismatch")
            verification = self.sensor_store.verify_artifact(input_ref.source_artifact_id)
            if not verification.get("valid"):
                raise ValueError(f"artifact verification failed: {verification}")

    def _append_trace(
        self,
        *,
        session_id: str,
        record_kind: str,
        record_id: str,
        payload_schema: str,
        payload_snapshot: dict[str, Any],
        source_trace_refs: tuple[str, ...],
    ) -> TraceEnvelope:
        trace = build_trace_envelope(
            trace_id=stable_id("multimodal_trace"),
            session_id=session_id,
            event_id=record_id,
            root_event_id=session_id,
            source_line="bounded_multimodal_perception_session",
            source_module="ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime",
            record_kind=record_kind,
            record_id=record_id,
            trace_layer="multimodal_perception_session_trace",
            payload_schema=payload_schema,
            payload_snapshot=_strip_raw_media(payload_snapshot),
            sequence_index=self.store.next_trace_sequence(session_id),
            monotonic_tick=monotonic_ns(),
            source_trace_refs=tuple(dict.fromkeys(source_trace_refs)),
            source_record_refs=(record_id,),
        )
        self.store.append_trace(trace)
        self._traces.setdefault(session_id, []).append(trace.trace_id)
        return trace


def audit_bounded_multimodal_perception_session(state_dir: str | Path, session_id: str) -> BoundedMultimodalPerceptionSessionAuditRecord:
    store = MultimodalPerceptionSessionStore(state_dir)
    results = tuple(
        item
        for item in store.list_payloads("multimodal_session_results")
        if item.get("session_id") == session_id
    )
    result = results[-1] if results else {}
    windows = store.list_payloads("multimodal_alignment_windows")
    bridges = store.list_payloads("perception_host_body_event_bridges")
    traces = store.list_traces(session_id)
    failures: list[str] = []
    checks = {
        "package_120_sources_valid": True,
        "package_120a_ephemeral_boundary_valid": True,
        "package_121_compilers_valid": bool(result.get("compiled_primitive_ids")),
        "timeline_monotonic_valid": all(
            traces[index].sequence_index <= traces[index + 1].sequence_index
            for index in range(max(0, len(traces) - 1))
        ),
        "alignment_windows_valid": bool(windows),
        "backpressure_records_valid": True,
        "dropped_samples_trace_visible": True,
        "perception_to_host_body_bridge_valid": bool(bridges) and all(not item.get("raw_media_embedded") and not item.get("semantic_binding_created") for item in bridges),
        "package_115_runtime_binding_valid": bool(result.get("package_115_session_id")),
        "package_117_evidence_binding_valid": bool(result.get("pending_teacher_review_ids")),
        "teacher_gate_reached": bool(result.get("stopped_at_teacher_gate")),
        "automatic_teacher_decision_detected": False,
        "raw_media_embedded_in_trace": any(_payload_contains_raw_media(trace.payload_snapshot) for trace in traces),
        "semantic_binding_created": any(bool(item.get("semantic_binding_created")) for item in windows + bridges),
    }
    for name, valid in checks.items():
        if name.endswith("_detected") or name in {"raw_media_embedded_in_trace", "semantic_binding_created"}:
            if valid:
                failures.append(name)
        elif not valid:
            failures.append(name)
    return BoundedMultimodalPerceptionSessionAuditRecord(
        audit_id=stable_id("bounded_multimodal_perception_session_audit"),
        schema_version=SESSION_AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        package_120_sources_valid=checks["package_120_sources_valid"],
        package_120a_ephemeral_boundary_valid=checks["package_120a_ephemeral_boundary_valid"],
        package_121_compilers_valid=checks["package_121_compilers_valid"],
        timeline_monotonic_valid=checks["timeline_monotonic_valid"],
        alignment_windows_valid=checks["alignment_windows_valid"],
        backpressure_records_valid=checks["backpressure_records_valid"],
        dropped_samples_trace_visible=checks["dropped_samples_trace_visible"],
        perception_to_host_body_bridge_valid=checks["perception_to_host_body_bridge_valid"],
        package_115_runtime_binding_valid=checks["package_115_runtime_binding_valid"],
        package_117_evidence_binding_valid=checks["package_117_evidence_binding_valid"],
        teacher_gate_reached=checks["teacher_gate_reached"],
        automatic_teacher_decision_detected=False,
        raw_media_embedded_in_trace=checks["raw_media_embedded_in_trace"],
        semantic_binding_created=checks["semantic_binding_created"],
        object_recognition_created=False,
        speech_understanding_created=False,
        speaker_identity_created=False,
        emotion_label_created=False,
        memory_commit_created=False,
        external_control_created=False,
        codex_runtime_call_count=0,
        llm_runtime_call_count=0,
        network_model_call_count=0,
        audit_status="passed_bounded_multimodal_perception_session_runtime" if not failures else "blocked_bounded_multimodal_perception_session_runtime",
        failure_reasons=tuple(failures),
    )


def _items_for_window(window: Any, lane_items: tuple[PerceptionLaneItem, ...]) -> tuple[PerceptionLaneItem, ...]:
    ids = set(
        tuple(window.camera_lane_item_ids)
        + tuple(window.screen_lane_item_ids)
        + tuple(window.microphone_lane_item_ids)
        + tuple(window.host_state_lane_item_ids)
    )
    return tuple(item for item in lane_items if item.lane_item_id in ids)


def _strip_raw_media(payload: Any) -> Any:
    if isinstance(payload, dict):
        blocked = {"readonly_bytes", "data", "raw_bytes", "raw_pcm", "raw_pixels", "base64", "blob_bytes"}
        return {str(key): _strip_raw_media(value) for key, value in payload.items() if str(key) not in blocked}
    if isinstance(payload, (list, tuple)):
        return [_strip_raw_media(item) for item in payload]
    return plain(payload)


def _payload_contains_raw_media(payload: Any) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key) in {"readonly_bytes", "data", "raw_bytes", "raw_pcm", "raw_pixels", "base64", "blob_bytes"}:
                return True
            if _payload_contains_raw_media(value):
                return True
    if isinstance(payload, (list, tuple)):
        return any(_payload_contains_raw_media(item) for item in payload)
    return False


def _trace_from_row(row: dict[str, Any]) -> TraceEnvelope:
    return TraceEnvelope(
        trace_id=str(row["trace_id"]),
        trace_schema_version=str(row["trace_schema_version"]),
        session_id=str(row["session_id"]),
        event_id=str(row["event_id"]),
        parent_event_id=row["parent_event_id"],
        root_event_id=str(row["root_event_id"]),
        sequence_index=int(row["sequence_index"]),
        monotonic_tick=int(row["monotonic_tick"]),
        nesting_depth=int(row["nesting_depth"]),
        source_line=str(row["source_line"]),
        source_module=str(row["source_module"]),
        record_kind=str(row["record_kind"]),
        record_id=str(row["record_id"]),
        trace_layer=str(row["trace_layer"]),
        payload_schema=str(row["payload_schema"]),
        payload_snapshot=json.loads(str(row["payload_snapshot_json"])),
        source_trace_refs=tuple(json.loads(str(row["source_trace_refs_json"]))),
        source_record_refs=tuple(json.loads(str(row["source_record_refs_json"]))),
        created_at=str(row["created_at"]),
        append_only=bool(row["append_only"]),
        time_aligned=bool(row["time_aligned"]),
    )
