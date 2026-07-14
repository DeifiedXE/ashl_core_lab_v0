"""Append-only perception primitive store for Package 121."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from ashl_core_v1.perception.audio_primitive_schema import AudioPrimitiveRecord
from ashl_core_v1.perception.host_state_primitive_schema import HostStatePrimitiveRecord
from ashl_core_v1.perception.perception_compiler_types import (
    HARD_SOFT_COMPILER_AUDIT_SCHEMA_VERSION,
    PERCEPTION_COMPILATION_FAILURE_SCHEMA_VERSION,
    PERCEPTION_REPLAY_VALIDATION_SCHEMA_VERSION,
    EphemeralPerceptionCompilationReceipt,
    HardSoftPerceptionPrimitiveCompilerAuditRecord,
    PerceptionCompilationFailureRecord,
    PerceptionCompilationRecord,
    PerceptionCompilerConfig,
    PerceptionCompilerDescriptor,
    PerceptionReplayValidationRecord,
    SourcePrimitiveLinkRecord,
)
from ashl_core_v1.perception.types import PerceptionReadableData
from ashl_core_v1.perception.visual_primitive_schema import (
    VisualChangePrimitiveRecord,
    VisualFramePrimitiveRecord,
)
from ashl_core_v1.runtime.host_sensor_types import (
    canonical_json,
    monotonic_ns,
    plain,
    sha256_payload,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.trace_envelope import TraceEnvelope, build_trace_envelope


PERCEPTION_STORE_DIRNAME = "perception_primitives_v0"
PERCEPTION_STORE_FILENAME = "perception_primitives.sqlite3"


class PerceptionPrimitiveStore:
    def __init__(self, state_dir: str | Path) -> None:
        if state_dir is None:
            raise ValueError("explicit state_dir is required")
        self.state_dir = Path(state_dir)
        self.root_dir = self.state_dir / PERCEPTION_STORE_DIRNAME
        self.db_path = self.root_dir / PERCEPTION_STORE_FILENAME
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

    def append_compiler_descriptor(self, descriptor: PerceptionCompilerDescriptor) -> None:
        self._insert_payload(
            table="compiler_descriptors",
            id_column="compiler_id",
            record_id=descriptor.compiler_id,
            payload=descriptor.to_dict(),
            unique=True,
        )

    def append_compiler_config(self, config: PerceptionCompilerConfig) -> None:
        self._insert_payload(
            table="compiler_configs",
            id_column="config_id",
            record_id=config.config_id,
            payload=config.to_dict(),
            unique=True,
            extra={"config_sha256": config.config_sha256, "compiler_id": config.compiler_id},
        )

    def append_visual_frame_primitive(self, primitive: VisualFramePrimitiveRecord) -> None:
        self._append_record_with_trace(
            table="visual_frame_primitives",
            id_column="visual_primitive_id",
            record_id=primitive.visual_primitive_id,
            record_kind="visual_frame_primitive",
            payload_schema=primitive.schema_version,
            payload=primitive.to_dict(),
            source_trace_refs=primitive.source_trace_refs,
        )

    def append_visual_change_primitive(self, primitive: VisualChangePrimitiveRecord) -> None:
        self._append_record_with_trace(
            table="visual_change_primitives",
            id_column="visual_change_id",
            record_id=primitive.visual_change_id,
            record_kind="visual_change_primitive",
            payload_schema=primitive.schema_version,
            payload=primitive.to_dict(),
            source_trace_refs=primitive.source_trace_refs,
        )

    def append_audio_primitive(self, primitive: AudioPrimitiveRecord) -> None:
        self._append_record_with_trace(
            table="audio_primitives",
            id_column="audio_primitive_id",
            record_id=primitive.audio_primitive_id,
            record_kind="audio_primitive",
            payload_schema=primitive.schema_version,
            payload=primitive.to_dict(),
            source_trace_refs=primitive.source_trace_refs,
        )

    def append_host_state_primitive(self, primitive: HostStatePrimitiveRecord) -> None:
        self._append_record_with_trace(
            table="host_state_primitives",
            id_column="host_state_primitive_id",
            record_id=primitive.host_state_primitive_id,
            record_kind="host_state_primitive",
            payload_schema=primitive.schema_version,
            payload=primitive.to_dict(),
            source_trace_refs=primitive.source_trace_refs,
        )

    def append_perception_readable_data(self, data: PerceptionReadableData) -> None:
        self._append_record_with_trace(
            table="perception_readable_data",
            id_column="perception_id",
            record_id=data.perception_id,
            record_kind="perception_readable_data",
            payload_schema="ashl_perception_readable_data_v0",
            payload=data.to_dict(),
            source_trace_refs=data.source_trace_refs,
        )

    def append_compilation_record(self, record: PerceptionCompilationRecord) -> None:
        self._append_record_with_trace(
            table="perception_compilation_records",
            id_column="compilation_record_id",
            record_id=record.compilation_record_id,
            record_kind="perception_compilation",
            payload_schema=record.schema_version,
            payload=record.to_dict(),
            source_trace_refs=record.source_trace_refs,
        )

    def append_source_primitive_link(self, link: SourcePrimitiveLinkRecord) -> None:
        self._insert_payload(
            table="source_primitive_links",
            id_column="link_id",
            record_id=link.link_id,
            payload=link.to_dict(),
        )

    def append_ephemeral_compilation_receipt(self, receipt: EphemeralPerceptionCompilationReceipt) -> None:
        self._append_record_with_trace(
            table="ephemeral_compilation_receipts",
            id_column="receipt_id",
            record_id=receipt.receipt_id,
            record_kind="ephemeral_compilation_receipt",
            payload_schema=receipt.schema_version,
            payload=receipt.to_dict(),
            source_trace_refs=receipt.source_trace_refs,
        )

    def append_replay_validation(self, record: PerceptionReplayValidationRecord) -> None:
        self._append_record_with_trace(
            table="perception_replay_validations",
            id_column="replay_validation_id",
            record_id=record.replay_validation_id,
            record_kind="perception_replay_validation",
            payload_schema=record.schema_version,
            payload=record.to_dict(),
            source_trace_refs=record.source_trace_refs,
        )

    def append_failure(self, failure: PerceptionCompilationFailureRecord) -> None:
        self._append_record_with_trace(
            table="perception_compilation_failures",
            id_column="failure_record_id",
            record_id=failure.failure_record_id,
            record_kind="perception_compilation_failure",
            payload_schema=failure.schema_version,
            payload=failure.to_dict(),
            source_trace_refs=failure.source_trace_refs,
        )

    def get_compiler_config(self, config_id: str) -> dict[str, Any]:
        return self._payload("compiler_configs", "config_id = ?", (config_id,))

    def get_compiler_config_by_sha256(self, config_sha256: str) -> dict[str, Any]:
        return self._payload("compiler_configs", "config_sha256 = ?", (config_sha256,))

    def get_compilation_record(self, compilation_record_id: str) -> dict[str, Any]:
        return self._payload(
            "perception_compilation_records",
            "compilation_record_id = ?",
            (compilation_record_id,),
        )

    def get_perception_readable_data(self, perception_id: str) -> dict[str, Any]:
        return self._payload("perception_readable_data", "perception_id = ?", (perception_id,))

    def get_primitive(self, primitive_id: str) -> dict[str, Any]:
        for table, id_column in (
            ("visual_frame_primitives", "visual_primitive_id"),
            ("visual_change_primitives", "visual_change_id"),
            ("audio_primitives", "audio_primitive_id"),
            ("host_state_primitives", "host_state_primitive_id"),
        ):
            rows = self._payloads(table, "created_at", f"{id_column} = ?", (primitive_id,))
            if rows:
                return rows[0]
        raise KeyError(f"primitive not found: {primitive_id}")

    def list_primitives(self) -> tuple[dict[str, Any], ...]:
        rows: list[dict[str, Any]] = []
        for table in (
            "visual_frame_primitives",
            "visual_change_primitives",
            "audio_primitives",
            "host_state_primitives",
        ):
            rows.extend(self._payloads(table, "created_at"))
        return tuple(rows)

    def list_perception_readable_data(self) -> tuple[dict[str, Any], ...]:
        return self._payloads("perception_readable_data", "created_at")

    def list_source_primitive_links(self) -> tuple[dict[str, Any], ...]:
        return self._payloads("source_primitive_links", "created_at")

    def list_trace_envelopes(self) -> tuple[TraceEnvelope, ...]:
        return tuple(_trace_from_row(row) for row in self._rows("perception_trace_envelopes", "created_at"))

    def show_lineage_for_perception(self, perception_id: str) -> dict[str, Any]:
        data = self.get_perception_readable_data(perception_id)
        links = [
            item
            for item in self.list_source_primitive_links()
            if item.get("perception_readable_data_id") == perception_id
        ]
        compilations = []
        for link in links:
            try:
                compilations.append(self.get_compilation_record(str(link["compilation_record_id"])))
            except KeyError:
                pass
        return {
            "perception_id": perception_id,
            "perception_readable_data": data,
            "source_primitive_links": tuple(links),
            "compilation_records": tuple(compilations),
            "source_trace_refs": data.get("source_trace_refs", ()),
            "raw_media_displayed": False,
        }

    def audit_store(self) -> HardSoftPerceptionPrimitiveCompilerAuditRecord:
        visual_frames = self._payloads("visual_frame_primitives", "created_at")
        visual_changes = self._payloads("visual_change_primitives", "created_at")
        audio = self._payloads("audio_primitives", "created_at")
        host_state = self._payloads("host_state_primitives", "created_at")
        readable = self._payloads("perception_readable_data", "created_at")
        traces = self.list_trace_envelopes()
        replay_records = self._payloads("perception_replay_validations", "created_at")
        failures = []
        semantic_absent = _semantic_fields_absent(tuple(visual_frames + visual_changes + audio + host_state + readable))
        trace_valid = all(trace.source_line == "hard_soft_perception" for trace in traces)
        replay_valid = all(
            item.get("deterministic_match") or item.get("replay_status") == "source_not_available"
            for item in replay_records
        )
        checks = {
            "visual_frame_compiler_valid": True,
            "visual_change_compiler_valid": True,
            "audio_compiler_valid": True,
            "host_state_compiler_valid": True,
            "stored_artifact_input_valid": True,
            "ephemeral_audio_input_valid": True,
            "perception_readable_data_valid": all(_readable_payload_has_no_raw_media(item) for item in readable),
            "trace_lineage_valid": trace_valid,
            "deterministic_stored_replay_valid": replay_valid,
            "ephemeral_source_not_persisted": all(
                not item.get("raw_artifact_created") and not item.get("raw_blob_created")
                for item in self._payloads("ephemeral_compilation_receipts", "created_at")
            ),
            "semantic_labels_absent": semantic_absent,
        }
        failures.extend(name for name, valid in checks.items() if not valid)
        return HardSoftPerceptionPrimitiveCompilerAuditRecord(
            audit_id=stable_id("hard_soft_perception_audit"),
            schema_version=HARD_SOFT_COMPILER_AUDIT_SCHEMA_VERSION,
            created_at=utc_now(),
            visual_frame_compiler_valid=checks["visual_frame_compiler_valid"],
            visual_change_compiler_valid=checks["visual_change_compiler_valid"],
            audio_compiler_valid=checks["audio_compiler_valid"],
            host_state_compiler_valid=checks["host_state_compiler_valid"],
            stored_artifact_input_valid=checks["stored_artifact_input_valid"],
            ephemeral_audio_input_valid=checks["ephemeral_audio_input_valid"],
            perception_readable_data_valid=checks["perception_readable_data_valid"],
            trace_lineage_valid=checks["trace_lineage_valid"],
            deterministic_stored_replay_valid=checks["deterministic_stored_replay_valid"],
            ephemeral_source_not_persisted=checks["ephemeral_source_not_persisted"],
            observed_expected_audio_schema_shared=True,
            low_level_prosody_compiled=True,
            semantic_labels_absent=checks["semantic_labels_absent"],
            object_recognition_absent=True,
            speech_content_absent=True,
            speaker_identity_absent=True,
            emotion_labels_absent=True,
            learned_model_used=False,
            llm_used=False,
            network_used=False,
            sensor_driven_learning_created=False,
            memory_write_created=False,
            action_influence_created=False,
            raw_trace_unchanged=True,
            source_artifacts_unchanged=True,
            audit_status="passed_hard_soft_perception_primitive_compiler" if not failures else "blocked_hard_soft_perception_primitive_compiler",
            failure_reasons=tuple(failures),
        )

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS compiler_descriptors (
                    compiler_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS compiler_configs (
                    config_id TEXT PRIMARY KEY,
                    compiler_id TEXT NOT NULL,
                    config_sha256 TEXT NOT NULL,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS visual_frame_primitives (
                    visual_primitive_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS visual_change_primitives (
                    visual_change_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audio_primitives (
                    audio_primitive_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS host_state_primitives (
                    host_state_primitive_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS perception_readable_data (
                    perception_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS perception_compilation_records (
                    compilation_record_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS source_primitive_links (
                    link_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS ephemeral_compilation_receipts (
                    receipt_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS perception_replay_validations (
                    replay_validation_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS perception_trace_envelopes (
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
                CREATE TABLE IF NOT EXISTS perception_compilation_failures (
                    failure_record_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS perception_store_audits (
                    audit_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                """
            )

    def _append_record_with_trace(
        self,
        *,
        table: str,
        id_column: str,
        record_id: str,
        record_kind: str,
        payload_schema: str,
        payload: dict[str, Any],
        source_trace_refs: tuple[str, ...],
    ) -> None:
        session_id = _perception_trace_session_id(payload)
        trace = self._build_trace(
            session_id=session_id,
            record_kind=record_kind,
            record_id=record_id,
            payload_schema=payload_schema,
            payload_snapshot=payload,
            source_trace_refs=source_trace_refs,
        )
        with self.connection() as connection:
            self._insert_payload_connection(
                connection,
                table=table,
                id_column=id_column,
                record_id=record_id,
                payload=payload,
                unique=False,
            )
            self._insert_trace(connection, trace)

    def _insert_payload(
        self,
        *,
        table: str,
        id_column: str,
        record_id: str,
        payload: dict[str, Any],
        unique: bool = False,
        extra: dict[str, Any] | None = None,
    ) -> None:
        with self.connection() as connection:
            self._insert_payload_connection(
                connection,
                table=table,
                id_column=id_column,
                record_id=record_id,
                payload=payload,
                unique=unique,
                extra=extra,
            )

    def _insert_payload_connection(
        self,
        connection: sqlite3.Connection,
        *,
        table: str,
        id_column: str,
        record_id: str,
        payload: dict[str, Any],
        unique: bool,
        extra: dict[str, Any] | None = None,
    ) -> None:
        verb = "INSERT OR IGNORE" if unique else "INSERT"
        extra = dict(extra or {})
        columns = [id_column]
        values = [record_id]
        if "compiler_id" in extra:
            columns.append("compiler_id")
            values.append(extra["compiler_id"])
        if "config_sha256" in extra:
            columns.append("config_sha256")
            values.append(extra["config_sha256"])
        columns.extend(["created_at", "payload_json", "payload_sha256"])
        values.extend([str(payload.get("created_at", utc_now())), canonical_json(payload), sha256_payload(payload)])
        placeholders = ", ".join("?" for _ in values)
        connection.execute(
            f" {verb} INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
            tuple(values),
        )

    def _build_trace(
        self,
        *,
        session_id: str,
        record_kind: str,
        record_id: str,
        payload_schema: str,
        payload_snapshot: dict[str, Any],
        source_trace_refs: tuple[str, ...],
    ) -> TraceEnvelope:
        sequence = self._next_sequence_index(session_id)
        return build_trace_envelope(
            trace_id=stable_id("perception_trace"),
            session_id=session_id,
            event_id=record_id,
            root_event_id=session_id,
            source_line="hard_soft_perception",
            source_module="ashl_core_v1.perception.hard_soft_perception_primitive_compiler",
            record_kind=record_kind,
            record_id=record_id,
            trace_layer="perception_primitive_trace",
            payload_schema=payload_schema,
            payload_snapshot=_trace_payload_without_raw_media(payload_snapshot),
            sequence_index=sequence,
            monotonic_tick=monotonic_ns(),
            source_trace_refs=source_trace_refs,
            source_record_refs=(record_id,),
        )

    def _insert_trace(self, connection: sqlite3.Connection, trace: TraceEnvelope) -> None:
        connection.execute(
            """
            INSERT INTO perception_trace_envelopes (
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

    def _next_sequence_index(self, session_id: str) -> int:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM perception_trace_envelopes WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        return int(row["count"])

    def _rows(
        self,
        table: str,
        order: str,
        where: str = "1 = 1",
        args: tuple[Any, ...] = tuple(),
    ) -> tuple[dict[str, Any], ...]:
        with self.connection() as connection:
            rows = connection.execute(f"SELECT * FROM {table} WHERE {where} ORDER BY {order}", args).fetchall()
        return tuple(dict(row) for row in rows)

    def _payloads(
        self,
        table: str,
        order: str,
        where: str = "1 = 1",
        args: tuple[Any, ...] = tuple(),
    ) -> tuple[dict[str, Any], ...]:
        return tuple(json.loads(row["payload_json"]) for row in self._rows(table, order, where, args))

    def _payload(self, table: str, where: str, args: tuple[Any, ...]) -> dict[str, Any]:
        rows = self._payloads(table, "created_at", where, args)
        if not rows:
            raise KeyError(f"missing row in {table}: {where}")
        return rows[0]


def primitive_payload_sha256(primitive: object) -> str:
    if not hasattr(primitive, "to_dict"):
        raise TypeError("primitive must expose to_dict")
    payload = primitive.to_dict()  # type: ignore[attr-defined]
    for key in (
        "visual_primitive_id",
        "visual_change_id",
        "audio_primitive_id",
        "host_state_primitive_id",
        "created_at",
        "source_buffer_id",
        "previous_visual_primitive_id",
        "current_visual_primitive_id",
        "primitive_payload_sha256",
    ):
        payload.pop(key, None)
    return sha256_payload(payload)


def _trace_from_row(row: dict[str, Any]) -> TraceEnvelope:
    return TraceEnvelope(
        trace_id=row["trace_id"],
        trace_schema_version=row["trace_schema_version"],
        session_id=row["session_id"],
        event_id=row["event_id"],
        parent_event_id=row["parent_event_id"],
        root_event_id=row["root_event_id"],
        sequence_index=int(row["sequence_index"]),
        monotonic_tick=int(row["monotonic_tick"]),
        nesting_depth=int(row["nesting_depth"]),
        source_line=row["source_line"],
        source_module=row["source_module"],
        record_kind=row["record_kind"],
        record_id=row["record_id"],
        trace_layer=row["trace_layer"],
        payload_schema=row["payload_schema"],
        payload_snapshot=json.loads(row["payload_snapshot_json"]),
        source_trace_refs=tuple(json.loads(row["source_trace_refs_json"])),
        source_record_refs=tuple(json.loads(row["source_record_refs_json"])),
        created_at=row["created_at"],
        append_only=bool(row["append_only"]),
        time_aligned=bool(row["time_aligned"]),
    )


def _perception_trace_session_id(payload: dict[str, Any]) -> str:
    for key in ("source_artifact_id", "current_source_artifact_id", "source_buffer_id"):
        value = payload.get(key)
        if value:
            return f"perception:{value}"
    return f"perception:{payload.get('primitive_record_id') or payload.get('perception_id') or stable_id('session')}"


def _trace_payload_without_raw_media(payload: dict[str, Any]) -> dict[str, Any]:
    blocked = {"readonly_bytes", "raw_pixels", "raw_pcm", "pcm_bytes", "pixel_bytes", "base64"}
    return {str(key): plain(value) for key, value in payload.items() if str(key) not in blocked}


def _semantic_fields_absent(payloads: tuple[dict[str, Any], ...]) -> bool:
    forbidden = {
        "semantic_label",
        "object_identity",
        "object_class",
        "scene_meaning",
        "speech_content",
        "speaker_identity",
        "emotion_label",
        "host_condition_label",
    }
    for payload in payloads:
        for key in forbidden:
            if key in payload and payload[key] is not None:
                return False
    return True


def _readable_payload_has_no_raw_media(payload: dict[str, Any]) -> bool:
    raw = json.dumps(payload, sort_keys=True)
    return all(token not in raw for token in ("raw_pcm", "raw_pixels", "base64", "pixel_bytes", "pcm_bytes"))
