"""Content-addressed raw host sensor artifact store for Package 120."""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from ashl_core_v1.runtime.host_sensor_types import (
    CAPTURE_FAILURE_SCHEMA_VERSION,
    CAPTURE_SESSION_SCHEMA_VERSION,
    LIFECYCLE_EVENT_SCHEMA_VERSION,
    RAW_ARTIFACT_SCHEMA_VERSION,
    STORE_AUDIT_SCHEMA_VERSION,
    HostSensorArtifactStoreAuditRecord,
    SensorCaptureFailureRecord,
    SensorCaptureLifecycleEvent,
    SensorCaptureSessionRecord,
    SensorCaptureConfig,
    SensorDeviceDescriptor,
    SensorRawArtifact,
    canonical_json,
    monotonic_ns,
    plain,
    sha256_bytes,
    sha256_payload,
    stable_id,
    utc_now,
    TERMINAL_LIFECYCLE_STATUSES,
)
from ashl_core_v1.runtime.audio_artifact_deletion import (
    ARTIFACT_DELETION_RECORD_SCHEMA_VERSION,
    EPHEMERAL_AUDIO_DELETION_AUDIT_SCHEMA_VERSION,
    ArtifactDeletionRecord,
    ArtifactDeletionRequest,
    ArtifactRetentionReferenceRecord,
    EphemeralAudioDeletionFoundationAuditRecord,
)
from ashl_core_v1.runtime.ephemeral_audio_ring_buffer import (
    EphemeralAudioChunkDescriptor,
    EphemeralAudioLifecycleEvent,
    EphemeralAudioSessionRecord,
)
from ashl_core_v1.runtime.evidence_audio_excerpt import (
    AudioCaptureConsentRecord,
    AudioExcerptRetentionCandidate,
    EvidenceAudioExcerptRecord,
    EvidenceAudioExcerptRequest,
)
from ashl_core_v1.runtime.sensor_adapter_protocol import AdapterOutputSample
from ashl_core_v1.runtime.trace_envelope import TRACE_SCHEMA_VERSION, TraceEnvelope, build_trace_envelope


SENSOR_STORE_DIRNAME = "host_sensor_artifacts_v0"
SENSOR_STORE_FILENAME = "sensor_artifacts.sqlite3"


class ContentAddressedSensorArtifactStore:
    def __init__(self, state_dir: str | Path) -> None:
        if state_dir is None:
            raise ValueError("explicit state_dir is required")
        self.state_dir = Path(state_dir)
        self.root_dir = self.state_dir / SENSOR_STORE_DIRNAME
        self.blob_root = self.root_dir / "blobs" / "sha256"
        self.quarantine_dir = self.root_dir / "quarantine"
        self.backup_dir = self.root_dir / "store_backups"
        self.db_path = self.root_dir / SENSOR_STORE_FILENAME
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.blob_root.mkdir(parents=True, exist_ok=True)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._initialize()
        self._recover_temporary_files()
        self._recover_running_sessions()

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

    def state_dir_fingerprint(self) -> str:
        return sha256_payload({"state_dir": str(self.state_dir.resolve())})

    def record_device_descriptor(self, descriptor: SensorDeviceDescriptor) -> None:
        payload = descriptor.to_dict()
        with self.connection() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO sensor_device_descriptors (
                    device_descriptor_id, source_kind, adapter_id, adapter_version,
                    device_id, device_index, available, created_at, payload_json,
                    payload_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    descriptor.device_descriptor_id,
                    descriptor.source_kind,
                    descriptor.adapter_id,
                    descriptor.adapter_version,
                    descriptor.device_id,
                    descriptor.device_index,
                    1 if descriptor.available else 0,
                    descriptor.created_at,
                    canonical_json(payload),
                    sha256_payload(payload),
                ),
            )

    def create_capture_session(
        self,
        *,
        source_kind: str,
        config: SensorCaptureConfig,
        descriptor: SensorDeviceDescriptor,
        session_id: str | None = None,
        root_event_id: str | None = None,
    ) -> SensorCaptureSessionRecord:
        self.record_device_descriptor(descriptor)
        session = SensorCaptureSessionRecord(
            capture_session_id=stable_id("sensor_capture_session"),
            schema_version=CAPTURE_SESSION_SCHEMA_VERSION,
            created_at=utc_now(),
            session_id=session_id or stable_id("sensor_session"),
            root_event_id=root_event_id or stable_id("sensor_root_event"),
            source_kind=source_kind,
            capture_config_id=config.capture_config_id,
            capture_config_sha256=config.capture_config_sha256,
            state_dir_fingerprint=self.state_dir_fingerprint(),
            source_device_descriptor_id=descriptor.device_descriptor_id,
            no_codex_guard_enabled=True,
            starting_sequence_index=self.next_sequence_index(session_id or ""),
            starting_monotonic_ns=monotonic_ns(),
            capture_status="created",
        )
        payload = session.to_dict()
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO sensor_capture_sessions (
                    capture_session_id, session_id, root_event_id, source_kind,
                    capture_config_id, capture_config_sha256, capture_status,
                    created_at, payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.capture_session_id,
                    session.session_id,
                    session.root_event_id,
                    session.source_kind,
                    session.capture_config_id,
                    session.capture_config_sha256,
                    session.capture_status,
                    session.created_at,
                    canonical_json(payload),
                    sha256_payload(payload),
                ),
            )
        self.append_lifecycle_event(
            session=session,
            previous_status=None,
            new_status="created",
            manual_command=None,
            reason_code="capture_session_created",
        )
        return session

    def append_lifecycle_event(
        self,
        *,
        session: SensorCaptureSessionRecord,
        previous_status: str | None,
        new_status: str,
        manual_command: str | None,
        reason_code: str,
        source_trace_refs: tuple[str, ...] | None = None,
    ) -> SensorCaptureLifecycleEvent:
        refs = source_trace_refs if source_trace_refs is not None else self._latest_trace_ref(session.session_id)
        sequence = self.next_sequence_index(session.session_id)
        event = SensorCaptureLifecycleEvent(
            lifecycle_event_id=stable_id("sensor_lifecycle_event"),
            schema_version=LIFECYCLE_EVENT_SCHEMA_VERSION,
            created_at=utc_now(),
            capture_session_id=session.capture_session_id,
            session_id=session.session_id,
            previous_status=previous_status,
            new_status=new_status,
            manual_command=manual_command,
            reason_code=reason_code,
            monotonic_ns=monotonic_ns(),
            sequence_index=sequence,
            source_trace_refs=tuple(refs or ()),
        )
        trace = self._build_trace(
            session=session,
            trace_id=stable_id("sensor_trace"),
            sequence_index=sequence,
            monotonic_tick=event.monotonic_ns,
            record_kind="sensor_capture_lifecycle_event",
            record_id=event.lifecycle_event_id,
            trace_layer="runtime_control",
            payload_schema=LIFECYCLE_EVENT_SCHEMA_VERSION,
            payload_snapshot=event.to_dict(),
            source_trace_refs=event.source_trace_refs,
        )
        with self.connection() as connection:
            self._insert_lifecycle(connection, event)
            self._insert_trace(connection, trace)
        return event

    def write_raw_artifact(
        self,
        *,
        session: SensorCaptureSessionRecord,
        descriptor: SensorDeviceDescriptor,
        config: SensorCaptureConfig,
        sample: AdapterOutputSample,
    ) -> SensorRawArtifact:
        if not sample.data:
            raise ValueError("adapter output sample is empty")
        byte_length = len(sample.data)
        content_hash = sha256_bytes(sample.data)
        blob_relative_path = self._write_blob(sample.data, content_hash)
        trace_sequence = self.next_sequence_index(session.session_id)
        capture_sequence = self._artifact_count(session.capture_session_id)
        trace_id = stable_id("sensor_trace")
        metadata = dict(sample.metadata)
        artifact = SensorRawArtifact(
            artifact_id=stable_id("sensor_raw_artifact"),
            schema_version=RAW_ARTIFACT_SCHEMA_VERSION,
            created_at=utc_now(),
            capture_session_id=session.capture_session_id,
            session_id=session.session_id,
            root_event_id=session.root_event_id,
            source_kind=session.source_kind,
            adapter_id=sample.adapter_id,
            adapter_version=sample.adapter_version,
            device_descriptor_id=descriptor.device_descriptor_id,
            capture_sequence_index=capture_sequence,
            trace_sequence_index=trace_sequence,
            captured_at_utc=sample.captured_at_utc,
            captured_at_monotonic_ns=sample.captured_at_monotonic_ns,
            capture_duration_ns=sample.capture_duration_ns,
            raw_level="adapter_output",
            media_type=sample.media_type,
            storage_format=sample.storage_format,
            pixel_format=metadata.get("pixel_format"),
            width=_optional_int(metadata.get("actual_width") or metadata.get("width") or _rect_value(metadata, "width")),
            height=_optional_int(metadata.get("actual_height") or metadata.get("height") or _rect_value(metadata, "height")),
            row_stride_bytes=_optional_int(metadata.get("row_stride_bytes")),
            audio_sample_rate=_optional_int(metadata.get("actual_sample_rate")),
            audio_channels=_optional_int(metadata.get("audio_channels")),
            audio_sample_format=metadata.get("audio_sample_format"),
            audio_frame_count=_optional_int(metadata.get("audio_frame_count")),
            byte_length=byte_length,
            content_sha256=content_hash,
            blob_relative_path=blob_relative_path,
            capture_config_sha256=config.capture_config_sha256,
            semantic_label=None,
            perception_compiled=False,
            learning_material_created=False,
            memory_write_created=False,
            immutable_artifact=True,
            append_only=True,
            trace_envelope_id=trace_id,
            source_trace_refs=self._latest_trace_ref(session.session_id),
            real_device_capture=sample.real_device_capture,
        )
        trace_payload = artifact.to_dict()
        trace_payload["adapter_metadata"] = _metadata_without_raw_content(metadata)
        trace = self._build_trace(
            session=session,
            trace_id=trace_id,
            sequence_index=trace_sequence,
            monotonic_tick=artifact.captured_at_monotonic_ns,
            record_kind="sensor_raw_artifact",
            record_id=artifact.artifact_id,
            trace_layer="raw_sensor_trace",
            payload_schema=RAW_ARTIFACT_SCHEMA_VERSION,
            payload_snapshot=trace_payload,
            source_trace_refs=artifact.source_trace_refs,
        )
        with self.connection() as connection:
            self._insert_artifact(connection, artifact)
            self._insert_trace(connection, trace)
        return artifact

    def record_failure(
        self,
        *,
        session: SensorCaptureSessionRecord,
        source_kind: str,
        failure_kind: str,
        failure_message: str,
        recoverable: bool = True,
    ) -> SensorCaptureFailureRecord:
        sequence = self.next_sequence_index(session.session_id)
        record = SensorCaptureFailureRecord(
            failure_record_id=stable_id("sensor_capture_failure"),
            schema_version=CAPTURE_FAILURE_SCHEMA_VERSION,
            created_at=utc_now(),
            capture_session_id=session.capture_session_id,
            session_id=session.session_id,
            source_kind=source_kind,
            failure_kind=failure_kind,
            failure_message=failure_message,
            recoverable=recoverable,
            artifact_created=False,
            monotonic_ns=monotonic_ns(),
            sequence_index=sequence,
            source_trace_refs=self._latest_trace_ref(session.session_id),
        )
        trace = self._build_trace(
            session=session,
            trace_id=stable_id("sensor_trace"),
            sequence_index=sequence,
            monotonic_tick=record.monotonic_ns,
            record_kind="sensor_capture_failure",
            record_id=record.failure_record_id,
            trace_layer="runtime_control",
            payload_schema=CAPTURE_FAILURE_SCHEMA_VERSION,
            payload_snapshot=record.to_dict(),
            source_trace_refs=record.source_trace_refs,
        )
        with self.connection() as connection:
            self._insert_failure(connection, record)
            self._insert_trace(connection, trace)
        return record

    def next_sequence_index(self, session_id: str) -> int:
        if not session_id:
            return 0
        with self.connection() as connection:
            row = connection.execute(
                "SELECT COALESCE(MAX(sequence_index), -1) + 1 AS next_sequence FROM sensor_trace_envelopes WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        return int(row["next_sequence"])

    def list_capture_sessions(self) -> tuple[dict[str, Any], ...]:
        return self._payloads("sensor_capture_sessions", "created_at")

    def list_artifacts(self, capture_session_id: str | None = None) -> tuple[dict[str, Any], ...]:
        if capture_session_id:
            return self._payloads("sensor_raw_artifacts", "capture_sequence_index", "capture_session_id = ?", (capture_session_id,))
        return self._payloads("sensor_raw_artifacts", "created_at")

    def list_failures(self) -> tuple[dict[str, Any], ...]:
        return self._payloads("sensor_capture_failures", "created_at")

    def get_artifact(self, artifact_id: str) -> dict[str, Any]:
        row = self._payload("sensor_raw_artifacts", "artifact_id = ?", (artifact_id,))
        return row

    def verify_artifact(self, artifact_id: str) -> dict[str, object]:
        artifact = self.get_artifact(artifact_id)
        path = self._resolve_blob_path(str(artifact["blob_relative_path"]))
        if not path.exists():
            if self._authorized_blob_deletion_for_artifact(artifact_id):
                return {
                    "valid": True,
                    "status": "authorized_waveform_deletion",
                    "artifact_id": artifact_id,
                    "content_sha256_valid": True,
                    "byte_length_valid": True,
                    "raw_bytes_displayed": False,
                }
            return {"valid": False, "status": "blocked_missing_blob", "artifact_id": artifact_id}
        data = path.read_bytes()
        hash_valid = sha256_bytes(data) == artifact["content_sha256"]
        length_valid = len(data) == int(artifact["byte_length"])
        return {
            "valid": hash_valid and length_valid,
            "status": "artifact_valid" if hash_valid and length_valid else "artifact_invalid",
            "artifact_id": artifact_id,
            "content_sha256_valid": hash_valid,
            "byte_length_valid": length_valid,
            "raw_bytes_displayed": False,
        }

    def list_trace_envelopes(self, session_id: str | None = None) -> tuple[TraceEnvelope, ...]:
        if session_id:
            rows = self._rows("sensor_trace_envelopes", "sequence_index", "session_id = ?", (session_id,))
        else:
            rows = self._rows("sensor_trace_envelopes", "created_at")
        return tuple(_trace_from_row(row) for row in rows)

    def append_ephemeral_audio_session(self, session: EphemeralAudioSessionRecord) -> None:
        payload = session.to_dict()
        with self.connection() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO ephemeral_audio_sessions (
                    ephemeral_audio_session_id, capture_mode, created_at,
                    payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session.ephemeral_audio_session_id,
                    session.capture_mode,
                    session.created_at,
                    canonical_json(payload),
                    sha256_payload(payload),
                ),
            )
            trace = self._build_audio_trace(
                session_id=session.ephemeral_audio_session_id,
                record_kind="ephemeral_audio_session",
                record_id=session.ephemeral_audio_session_id,
                trace_layer="audio_ingress_control_trace",
                payload_schema=session.schema_version,
                payload_snapshot=payload,
                source_trace_refs=session.source_trace_refs,
            )
            self._insert_trace(connection, trace)

    def append_ephemeral_audio_lifecycle_event(self, event: EphemeralAudioLifecycleEvent) -> None:
        payload = event.to_dict()
        with self.connection() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO ephemeral_audio_lifecycle_events (
                    lifecycle_event_id, ring_buffer_session_id, new_status,
                    sequence_index, created_at, payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.lifecycle_event_id,
                    event.ring_buffer_session_id,
                    event.new_status,
                    event.sequence_index,
                    event.created_at,
                    canonical_json(payload),
                    sha256_payload(payload),
                ),
            )
            trace = self._build_audio_trace(
                session_id=event.ring_buffer_session_id,
                record_kind="ephemeral_audio_lifecycle_event",
                record_id=event.lifecycle_event_id,
                trace_layer="audio_ingress_control_trace",
                payload_schema=event.schema_version,
                payload_snapshot=payload,
                source_trace_refs=event.source_trace_refs,
            )
            self._insert_trace(connection, trace)

    def append_ephemeral_audio_chunk_descriptor(self, descriptor: EphemeralAudioChunkDescriptor) -> None:
        payload = descriptor.to_dict()
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO ephemeral_audio_chunk_descriptors (
                    chunk_descriptor_row_id, chunk_id, ring_buffer_session_id,
                    sequence_index, overwritten, persisted, created_at,
                    payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    stable_id("ephemeral_audio_chunk_descriptor"),
                    descriptor.chunk_id,
                    descriptor.ring_buffer_session_id,
                    descriptor.sequence_index,
                    1 if descriptor.overwritten else 0,
                    1 if descriptor.persisted else 0,
                    utc_now(),
                    canonical_json(payload),
                    sha256_payload(payload),
                ),
            )
            trace = self._build_audio_trace(
                session_id=descriptor.ring_buffer_session_id,
                record_kind="ephemeral_audio_chunk_descriptor",
                record_id=descriptor.chunk_id,
                trace_layer="audio_ingress_control_trace",
                payload_schema=descriptor.schema_version,
                payload_snapshot=payload,
                source_trace_refs=descriptor.source_trace_refs,
            )
            self._insert_trace(connection, trace)

    def append_audio_capture_consent(self, consent: AudioCaptureConsentRecord) -> None:
        self._append_audio_payload(
            "audio_capture_consents",
            "consent_record_id",
            consent.consent_record_id,
            consent.created_at,
            consent.to_dict(),
            record_kind="audio_capture_consent",
            session_id=consent.consent_record_id,
            trace_layer="audio_retention_governance_trace",
            payload_schema=consent.schema_version,
            source_trace_refs=tuple(),
            insert_or_ignore=True,
        )

    def append_evidence_audio_excerpt_request(self, request: EvidenceAudioExcerptRequest) -> None:
        self._append_audio_payload(
            "evidence_audio_excerpt_requests",
            "excerpt_request_id",
            request.excerpt_request_id,
            request.created_at,
            request.to_dict(),
            record_kind="evidence_audio_excerpt_request",
            session_id=request.ring_buffer_session_id,
            trace_layer="audio_retention_governance_trace",
            payload_schema=request.schema_version,
            source_trace_refs=tuple(),
        )

    def append_evidence_audio_excerpt(self, excerpt: EvidenceAudioExcerptRecord) -> None:
        payload = excerpt.to_dict()
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO evidence_audio_excerpts (
                    excerpt_id, artifact_id, content_sha256, purpose,
                    created_at, payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    excerpt.excerpt_id,
                    excerpt.sensor_raw_artifact_id,
                    excerpt.content_sha256,
                    excerpt.purpose,
                    excerpt.created_at,
                    canonical_json(payload),
                    sha256_payload(payload),
                ),
            )
            trace = self._build_audio_trace(
                session_id=excerpt.source_ring_buffer_session_id,
                record_kind="evidence_audio_excerpt",
                record_id=excerpt.excerpt_id,
                trace_layer="audio_retention_governance_trace",
                payload_schema=excerpt.schema_version,
                payload_snapshot=payload,
                source_trace_refs=excerpt.source_trace_refs,
            )
            self._insert_trace(connection, trace)

    def append_audio_excerpt_retention_candidate(self, candidate: AudioExcerptRetentionCandidate) -> None:
        payload = candidate.to_dict()
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO audio_excerpt_retention_candidates (
                    retention_candidate_id, excerpt_id, artifact_id, candidate_purpose,
                    created_at, payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate.retention_candidate_id,
                    candidate.excerpt_id,
                    candidate.artifact_id,
                    candidate.candidate_purpose,
                    candidate.created_at,
                    canonical_json(payload),
                    sha256_payload(payload),
                ),
            )
            trace = self._build_audio_trace(
                session_id=candidate.excerpt_id,
                record_kind="audio_excerpt_retention_candidate",
                record_id=candidate.retention_candidate_id,
                trace_layer="audio_retention_governance_trace",
                payload_schema=candidate.schema_version,
                payload_snapshot=payload,
                source_trace_refs=candidate.source_trace_refs,
            )
            self._insert_trace(connection, trace)

    def append_artifact_retention_reference(self, reference: ArtifactRetentionReferenceRecord) -> None:
        payload = reference.to_dict()
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO artifact_retention_references (
                    reference_record_id, artifact_id, content_sha256,
                    referencing_record_kind, referencing_record_id, reference_status,
                    created_at, payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    reference.reference_record_id,
                    reference.artifact_id,
                    reference.content_sha256,
                    reference.referencing_record_kind,
                    reference.referencing_record_id,
                    reference.reference_status,
                    reference.created_at,
                    canonical_json(payload),
                    sha256_payload(payload),
                ),
            )
            trace = self._build_audio_trace(
                session_id=reference.artifact_id,
                record_kind="artifact_retention_reference",
                record_id=reference.reference_record_id,
                trace_layer="audio_retention_governance_trace",
                payload_schema=reference.schema_version,
                payload_snapshot=payload,
                source_trace_refs=reference.source_trace_refs,
            )
            self._insert_trace(connection, trace)

    def append_artifact_deletion_request(self, request: ArtifactDeletionRequest) -> None:
        payload = request.to_dict()
        with self.connection() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO artifact_deletion_requests (
                    deletion_request_id, artifact_id, expected_content_sha256,
                    reason_code, created_at, payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.deletion_request_id,
                    request.artifact_id,
                    request.expected_content_sha256,
                    request.reason_code,
                    request.created_at,
                    canonical_json(payload),
                    sha256_payload(payload),
                ),
            )
            trace = self._build_audio_trace(
                session_id=request.artifact_id,
                record_kind="artifact_deletion_request",
                record_id=request.deletion_request_id,
                trace_layer="audio_retention_governance_trace",
                payload_schema=request.schema_version,
                payload_snapshot=payload,
                source_trace_refs=tuple(),
            )
            self._insert_trace(connection, trace)

    def apply_artifact_deletion(self, request: ArtifactDeletionRequest) -> ArtifactDeletionRecord:
        artifact = self.get_artifact(request.artifact_id)
        if artifact["content_sha256"] != request.expected_content_sha256:
            raise ValueError("blocked_content_hash_mismatch")
        if self._artifact_has_deletion_record(request.artifact_id):
            raise ValueError("blocked_duplicate_deletion")
        path = self._resolve_blob_path(str(artifact["blob_relative_path"]))
        if not path.exists():
            raise ValueError("blocked_missing_blob")
        if sha256_bytes(path.read_bytes()) != artifact["content_sha256"]:
            raise ValueError("blocked_artifact_hash_mismatch")
        live_before_ids = self._live_blob_reference_ids(str(artifact["content_sha256"]))
        if request.artifact_id not in live_before_ids:
            raise ValueError("blocked_artifact_not_live")
        live_after_ids = tuple(item for item in live_before_ids if item != request.artifact_id)
        remove_blob = request.allow_blob_removal and len(live_after_ids) == 0
        if remove_blob:
            path.unlink()
        record = ArtifactDeletionRecord(
            deletion_record_id=stable_id("artifact_deletion_record"),
            schema_version=ARTIFACT_DELETION_RECORD_SCHEMA_VERSION,
            created_at=utc_now(),
            deletion_request_id=request.deletion_request_id,
            artifact_id=request.artifact_id,
            content_sha256_before_deletion=str(artifact["content_sha256"]),
            blob_relative_path_before_deletion=str(artifact["blob_relative_path"]),
            deletion_reason=request.reason_code,
            referenced_by_record_ids_at_deletion=live_before_ids,
            live_blob_reference_count_before=len(live_before_ids),
            live_blob_reference_count_after=len(live_after_ids),
            artifact_tombstoned=True,
            blob_physically_removed=remove_blob,
            blob_retained_for_other_artifacts=not remove_blob,
            deletion_authorized=True,
            deletion_verified=True,
            deleted_at_utc=utc_now(),
            source_trace_refs=tuple(str(item) for item in artifact.get("source_trace_refs", ())),
        )
        payload = record.to_dict()
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO artifact_deletion_records (
                    deletion_record_id, deletion_request_id, artifact_id,
                    content_sha256_before_deletion, blob_physically_removed,
                    created_at, payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.deletion_record_id,
                    record.deletion_request_id,
                    record.artifact_id,
                    record.content_sha256_before_deletion,
                    1 if record.blob_physically_removed else 0,
                    record.created_at,
                    canonical_json(payload),
                    sha256_payload(payload),
                ),
            )
            trace = self._build_audio_trace(
                session_id=record.artifact_id,
                record_kind="artifact_deletion_record",
                record_id=record.deletion_record_id,
                trace_layer="audio_retention_governance_trace",
                payload_schema=record.schema_version,
                payload_snapshot=payload,
                source_trace_refs=record.source_trace_refs,
            )
            self._insert_trace(connection, trace)
        return record

    def list_evidence_audio_excerpts(self) -> tuple[dict[str, Any], ...]:
        return self._payloads("evidence_audio_excerpts", "created_at")

    def get_evidence_audio_excerpt(self, excerpt_id: str) -> dict[str, Any]:
        return self._payload("evidence_audio_excerpts", "excerpt_id = ?", (excerpt_id,))

    def list_artifact_deletion_records(self) -> tuple[dict[str, Any], ...]:
        return self._payloads("artifact_deletion_records", "created_at")

    def get_artifact_deletion_record(self, artifact_id: str) -> dict[str, Any]:
        return self._payload("artifact_deletion_records", "artifact_id = ?", (artifact_id,))

    def audit_store(self) -> HostSensorArtifactStoreAuditRecord:
        sessions = self.list_capture_sessions()
        artifacts = self.list_artifacts()
        failures = self.list_failures()
        blob_paths = tuple(self.blob_root.glob("*/*.bin"))
        artifact_paths_relative = all(not Path(item["blob_relative_path"]).is_absolute() for item in artifacts)
        artifact_paths_inside = all(self._path_inside_state_dir(str(item["blob_relative_path"])) for item in artifacts)
        missing_blob_count = 0
        authorized_deleted_blob_count = 0
        hashes_valid = True
        lengths_valid = True
        for item in artifacts:
            path = self._resolve_blob_path(str(item["blob_relative_path"]))
            if not path.exists():
                if self._authorized_blob_deletion_for_artifact(str(item["artifact_id"])):
                    authorized_deleted_blob_count += 1
                else:
                    missing_blob_count += 1
                    hashes_valid = False
                    lengths_valid = False
                continue
            data = path.read_bytes()
            hashes_valid = hashes_valid and sha256_bytes(data) == item["content_sha256"]
            lengths_valid = lengths_valid and len(data) == int(item["byte_length"])
        referenced = {str(item["blob_relative_path"]) for item in artifacts}
        orphan_blob_count = sum(
            1
            for path in blob_paths
            if path.relative_to(self.root_dir).as_posix() not in referenced
        )
        temporary_file_count = len(tuple(self.root_dir.glob("*.tmp"))) + len(tuple(self.quarantine_dir.glob("*.tmp")))
        traces = self.list_trace_envelopes()
        trace_ids = {trace.trace_id for trace in traces}
        all_trace_links_valid = all(str(item["trace_envelope_id"]) in trace_ids for item in artifacts)
        monotonic_order_valid = _monotonic_order_valid(traces)
        lifecycle_order_valid = self._lifecycle_order_valid()
        semantic_absent = all(item.get("semantic_label") is None for item in artifacts)
        perception_absent = all(not item.get("perception_compiled") for item in artifacts)
        learning_absent = all(not item.get("learning_material_created") for item in artifacts)
        memory_absent = all(not item.get("memory_write_created") for item in artifacts)
        reasons: list[str] = []
        checks = {
            "all_artifact_paths_relative": artifact_paths_relative,
            "all_artifact_paths_inside_state_dir": artifact_paths_inside,
            "all_artifact_hashes_valid": hashes_valid,
            "all_artifact_lengths_valid": lengths_valid,
            "all_trace_links_valid": all_trace_links_valid,
            "monotonic_order_valid": monotonic_order_valid,
            "lifecycle_order_valid": lifecycle_order_valid,
            "semantic_labels_absent": semantic_absent,
            "perception_records_absent": perception_absent,
            "learning_records_absent": learning_absent,
            "memory_records_absent": memory_absent,
        }
        reasons.extend(key for key, valid in checks.items() if not valid)
        status = _audit_status(reasons, orphan_blob_count, missing_blob_count, authorized_deleted_blob_count)
        record = HostSensorArtifactStoreAuditRecord(
            audit_id=stable_id("host_sensor_store_audit"),
            schema_version=STORE_AUDIT_SCHEMA_VERSION,
            created_at=utc_now(),
            state_dir_fingerprint=self.state_dir_fingerprint(),
            capture_session_count=len(sessions),
            artifact_count=len(artifacts),
            blob_count=len(blob_paths),
            failure_count=len(failures),
            all_artifact_paths_relative=artifact_paths_relative,
            all_artifact_paths_inside_state_dir=artifact_paths_inside,
            all_artifact_hashes_valid=hashes_valid,
            all_artifact_lengths_valid=lengths_valid,
            all_trace_links_valid=all_trace_links_valid,
            monotonic_order_valid=monotonic_order_valid,
            lifecycle_order_valid=lifecycle_order_valid,
            artifact_rows_immutable=True,
            trace_rows_immutable=True,
            orphan_blob_count=orphan_blob_count,
            missing_blob_count=missing_blob_count,
            temporary_file_count=temporary_file_count,
            semantic_labels_absent=semantic_absent,
            perception_records_absent=perception_absent,
            learning_records_absent=learning_absent,
            memory_records_absent=memory_absent,
            audit_status=status,
            failure_reasons=tuple(reasons),
        )
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO sensor_store_integrity_audits (
                    audit_id, created_at, audit_status, payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (record.audit_id, record.created_at, record.audit_status, canonical_json(record), sha256_payload(record)),
            )
        return record

    def update_artifact(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("sensor raw artifacts are immutable; update is forbidden")

    def delete_artifact(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("sensor raw artifacts are immutable; delete is forbidden")

    def update_trace(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("sensor TraceEnvelopes are immutable; update is forbidden")

    def delete_trace(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("sensor TraceEnvelopes are immutable; delete is forbidden")

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS sensor_store_metadata (
                    schema_name TEXT PRIMARY KEY,
                    schema_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sensor_device_descriptors (
                    device_descriptor_id TEXT PRIMARY KEY,
                    source_kind TEXT NOT NULL,
                    adapter_id TEXT NOT NULL,
                    adapter_version TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    device_index INTEGER,
                    available INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sensor_capture_sessions (
                    capture_session_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    root_event_id TEXT NOT NULL,
                    source_kind TEXT NOT NULL,
                    capture_config_id TEXT NOT NULL,
                    capture_config_sha256 TEXT NOT NULL,
                    capture_status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sensor_capture_lifecycle_events (
                    lifecycle_event_id TEXT PRIMARY KEY,
                    capture_session_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    new_status TEXT NOT NULL,
                    sequence_index INTEGER NOT NULL,
                    monotonic_ns INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    UNIQUE(session_id, sequence_index)
                );
                CREATE TABLE IF NOT EXISTS sensor_raw_artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    capture_session_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    source_kind TEXT NOT NULL,
                    content_sha256 TEXT NOT NULL,
                    byte_length INTEGER NOT NULL,
                    blob_relative_path TEXT NOT NULL,
                    trace_envelope_id TEXT NOT NULL UNIQUE,
                    capture_sequence_index INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sensor_capture_failures (
                    failure_record_id TEXT PRIMARY KEY,
                    capture_session_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    source_kind TEXT NOT NULL,
                    failure_kind TEXT NOT NULL,
                    sequence_index INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sensor_trace_envelopes (
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
                    payload_sha256 TEXT NOT NULL,
                    UNIQUE(session_id, sequence_index)
                );
                CREATE TABLE IF NOT EXISTS sensor_store_integrity_audits (
                    audit_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    audit_status TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS ephemeral_audio_sessions (
                    ephemeral_audio_session_id TEXT PRIMARY KEY,
                    capture_mode TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS ephemeral_audio_lifecycle_events (
                    lifecycle_event_id TEXT PRIMARY KEY,
                    ring_buffer_session_id TEXT NOT NULL,
                    new_status TEXT NOT NULL,
                    sequence_index INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS ephemeral_audio_chunk_descriptors (
                    chunk_descriptor_row_id TEXT PRIMARY KEY,
                    chunk_id TEXT NOT NULL,
                    ring_buffer_session_id TEXT NOT NULL,
                    sequence_index INTEGER NOT NULL,
                    overwritten INTEGER NOT NULL,
                    persisted INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audio_capture_consents (
                    consent_record_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evidence_audio_excerpt_requests (
                    excerpt_request_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evidence_audio_excerpts (
                    excerpt_id TEXT PRIMARY KEY,
                    artifact_id TEXT NOT NULL,
                    content_sha256 TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audio_excerpt_retention_candidates (
                    retention_candidate_id TEXT PRIMARY KEY,
                    excerpt_id TEXT NOT NULL,
                    artifact_id TEXT NOT NULL,
                    candidate_purpose TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS artifact_retention_references (
                    reference_record_id TEXT PRIMARY KEY,
                    artifact_id TEXT NOT NULL,
                    content_sha256 TEXT NOT NULL,
                    referencing_record_kind TEXT NOT NULL,
                    referencing_record_id TEXT NOT NULL,
                    reference_status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS artifact_deletion_requests (
                    deletion_request_id TEXT PRIMARY KEY,
                    artifact_id TEXT NOT NULL,
                    expected_content_sha256 TEXT NOT NULL,
                    reason_code TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS artifact_deletion_records (
                    deletion_record_id TEXT PRIMARY KEY,
                    deletion_request_id TEXT NOT NULL,
                    artifact_id TEXT NOT NULL,
                    content_sha256_before_deletion TEXT NOT NULL,
                    blob_physically_removed INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                """
            )
            connection.execute(
                "INSERT OR IGNORE INTO sensor_store_metadata VALUES (?, ?, ?)",
                ("ashl_host_sensor_artifact_store", "v0", utc_now()),
            )

    def _write_blob(self, data: bytes, content_hash: str) -> str:
        shard = content_hash[:2]
        blob_dir = self.blob_root / shard
        blob_dir.mkdir(parents=True, exist_ok=True)
        final_path = blob_dir / f"{content_hash}.bin"
        relative_path = final_path.relative_to(self.root_dir).as_posix()
        if final_path.exists():
            existing = final_path.read_bytes()
            if len(existing) != len(data) or sha256_bytes(existing) != content_hash:
                raise ValueError("blocked store integrity failure: existing blob hash/length mismatch")
            return relative_path
        tmp_path = self.root_dir / f".sensor_blob_{uuid4().hex}.tmp"
        with tmp_path.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if sha256_bytes(tmp_path.read_bytes()) != content_hash:
            tmp_path.unlink(missing_ok=True)
            raise ValueError("hash_validation_failed")
        os.replace(tmp_path, final_path)
        return relative_path

    def _resolve_blob_path(self, relative_path: str) -> Path:
        path = (self.root_dir / relative_path).resolve()
        root = self.root_dir.resolve()
        if not str(path).startswith(str(root)):
            raise ValueError("blocked path escape")
        return path

    def _path_inside_state_dir(self, relative_path: str) -> bool:
        try:
            self._resolve_blob_path(relative_path)
            return not Path(relative_path).is_absolute() and ".." not in Path(relative_path).parts
        except Exception:
            return False

    def _artifact_count(self, capture_session_id: str) -> int:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM sensor_raw_artifacts WHERE capture_session_id = ?",
                (capture_session_id,),
            ).fetchone()
        return int(row["count"])

    def _latest_trace_ref(self, session_id: str) -> tuple[str, ...]:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT trace_id FROM sensor_trace_envelopes WHERE session_id = ? ORDER BY sequence_index DESC LIMIT 1",
                (session_id,),
            ).fetchone()
        return tuple() if row is None else (str(row["trace_id"]),)

    def _build_trace(
        self,
        *,
        session: SensorCaptureSessionRecord,
        trace_id: str,
        sequence_index: int,
        monotonic_tick: int,
        record_kind: str,
        record_id: str,
        trace_layer: str,
        payload_schema: str,
        payload_snapshot: dict[str, Any],
        source_trace_refs: tuple[str, ...],
    ) -> TraceEnvelope:
        return build_trace_envelope(
            trace_id=trace_id,
            session_id=session.session_id,
            event_id=record_id,
            root_event_id=session.root_event_id,
            source_line="host_sensor_ingress",
            source_module="ashl_core_v1.runtime.real_host_sensor_ingress",
            record_kind=record_kind,
            record_id=record_id,
            trace_layer=trace_layer,
            payload_schema=payload_schema,
            payload_snapshot=payload_snapshot,
            sequence_index=sequence_index,
            monotonic_tick=monotonic_tick,
            source_trace_refs=source_trace_refs,
            source_record_refs=(record_id,),
        )

    def _insert_lifecycle(self, connection: sqlite3.Connection, event: SensorCaptureLifecycleEvent) -> None:
        payload = event.to_dict()
        connection.execute(
            """
            INSERT INTO sensor_capture_lifecycle_events (
                lifecycle_event_id, capture_session_id, session_id, new_status,
                sequence_index, monotonic_ns, created_at, payload_json, payload_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.lifecycle_event_id,
                event.capture_session_id,
                event.session_id,
                event.new_status,
                event.sequence_index,
                event.monotonic_ns,
                event.created_at,
                canonical_json(payload),
                sha256_payload(payload),
            ),
        )

    def _insert_artifact(self, connection: sqlite3.Connection, artifact: SensorRawArtifact) -> None:
        payload = artifact.to_dict()
        connection.execute(
            """
            INSERT INTO sensor_raw_artifacts (
                artifact_id, capture_session_id, session_id, source_kind,
                content_sha256, byte_length, blob_relative_path, trace_envelope_id,
                capture_sequence_index, created_at, payload_json, payload_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                artifact.artifact_id,
                artifact.capture_session_id,
                artifact.session_id,
                artifact.source_kind,
                artifact.content_sha256,
                artifact.byte_length,
                artifact.blob_relative_path,
                artifact.trace_envelope_id,
                artifact.capture_sequence_index,
                artifact.created_at,
                canonical_json(payload),
                sha256_payload(payload),
            ),
        )

    def _insert_failure(self, connection: sqlite3.Connection, failure: SensorCaptureFailureRecord) -> None:
        payload = failure.to_dict()
        connection.execute(
            """
            INSERT INTO sensor_capture_failures (
                failure_record_id, capture_session_id, session_id, source_kind,
                failure_kind, sequence_index, created_at, payload_json, payload_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                failure.failure_record_id,
                failure.capture_session_id,
                failure.session_id,
                failure.source_kind,
                failure.failure_kind,
                failure.sequence_index,
                failure.created_at,
                canonical_json(payload),
                sha256_payload(payload),
            ),
        )

    def _insert_trace(self, connection: sqlite3.Connection, trace: TraceEnvelope) -> None:
        connection.execute(
            """
            INSERT INTO sensor_trace_envelopes (
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

    def _rows(self, table: str, order: str, where: str = "1 = 1", args: tuple[Any, ...] = tuple()) -> tuple[dict[str, Any], ...]:
        with self.connection() as connection:
            rows = connection.execute(f"SELECT * FROM {table} WHERE {where} ORDER BY {order}", args).fetchall()
        return tuple(dict(row) for row in rows)

    def _payloads(self, table: str, order: str, where: str = "1 = 1", args: tuple[Any, ...] = tuple()) -> tuple[dict[str, Any], ...]:
        return tuple(json.loads(row["payload_json"]) for row in self._rows(table, order, where, args))

    def _payload(self, table: str, where: str, args: tuple[Any, ...]) -> dict[str, Any]:
        rows = self._payloads(table, "created_at", where, args)
        if not rows:
            raise KeyError(f"missing row in {table}: {where}")
        return rows[0]

    def _append_audio_payload(
        self,
        table: str,
        id_column: str,
        record_id: str,
        created_at: str,
        payload: dict[str, Any],
        *,
        record_kind: str,
        session_id: str,
        trace_layer: str,
        payload_schema: str,
        source_trace_refs: tuple[str, ...],
        insert_or_ignore: bool = False,
    ) -> None:
        verb = "INSERT OR IGNORE" if insert_or_ignore else "INSERT"
        with self.connection() as connection:
            connection.execute(
                f"""
                {verb} INTO {table} (
                    {id_column}, created_at, payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?)
                """,
                (record_id, created_at, canonical_json(payload), sha256_payload(payload)),
            )
            trace = self._build_audio_trace(
                session_id=session_id,
                record_kind=record_kind,
                record_id=record_id,
                trace_layer=trace_layer,
                payload_schema=payload_schema,
                payload_snapshot=payload,
                source_trace_refs=source_trace_refs,
            )
            self._insert_trace(connection, trace)

    def _build_audio_trace(
        self,
        *,
        session_id: str,
        record_kind: str,
        record_id: str,
        trace_layer: str,
        payload_schema: str,
        payload_snapshot: dict[str, Any],
        source_trace_refs: tuple[str, ...],
    ) -> TraceEnvelope:
        return build_trace_envelope(
            trace_id=stable_id("sensor_trace"),
            session_id=session_id,
            event_id=record_id,
            root_event_id=session_id,
            source_line="host_sensor_ingress",
            source_module="ashl_core_v1.runtime.ephemeral_audio_ingress",
            record_kind=record_kind,
            record_id=record_id,
            trace_layer=trace_layer,
            payload_schema=payload_schema,
            payload_snapshot=payload_snapshot,
            sequence_index=self.next_sequence_index(session_id),
            monotonic_tick=monotonic_ns(),
            source_trace_refs=source_trace_refs,
            source_record_refs=(record_id,),
        )

    def _artifact_has_deletion_record(self, artifact_id: str) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM artifact_deletion_records WHERE artifact_id = ? LIMIT 1",
                (artifact_id,),
            ).fetchone()
        return row is not None

    def _authorized_blob_deletion_for_artifact(self, artifact_id: str) -> bool:
        try:
            record = self.get_artifact_deletion_record(artifact_id)
        except Exception:
            return False
        if not record.get("deletion_authorized") or not record.get("deletion_verified"):
            return False
        artifact = self.get_artifact(artifact_id)
        matches_artifact = (
            record.get("content_sha256_before_deletion") == artifact.get("content_sha256")
            and record.get("blob_relative_path_before_deletion") == artifact.get("blob_relative_path")
        )
        if not matches_artifact:
            return False
        if bool(record.get("blob_physically_removed")):
            return True
        return any(
            item.get("content_sha256_before_deletion") == artifact.get("content_sha256")
            and bool(item.get("blob_physically_removed"))
            for item in self.list_artifact_deletion_records()
        )

    def _live_blob_reference_ids(self, content_sha256: str) -> tuple[str, ...]:
        artifacts = self.list_artifacts()
        deleted = {
            str(item["artifact_id"])
            for item in self.list_artifact_deletion_records()
            if item.get("deletion_authorized") and item.get("deletion_verified")
        }
        live_artifacts = [
            str(item["artifact_id"])
            for item in artifacts
            if item.get("content_sha256") == content_sha256 and str(item["artifact_id"]) not in deleted
        ]
        live_retention_refs = [
            str(item["reference_record_id"])
            for item in self._payloads("artifact_retention_references", "created_at")
            if item.get("content_sha256") == content_sha256 and item.get("reference_status") == "live"
        ]
        return tuple(live_artifacts + live_retention_refs)

    def audit_ephemeral_audio_deletion_foundation(self) -> EphemeralAudioDeletionFoundationAuditRecord:
        sessions = self._payloads("ephemeral_audio_sessions", "created_at")
        excerpts = self.list_evidence_audio_excerpts()
        deletions = self.list_artifact_deletion_records()
        ephemeral_artifacts = [
            item
            for item in self.list_artifacts()
            if str(item.get("capture_session_id", "")).startswith("ephemeral_audio_session")
            or str(item.get("source_kind")) == "recognition_ephemeral"
        ]
        temp_files = tuple(self.root_dir.glob("*.tmp")) + tuple(self.quarantine_dir.glob("*.tmp"))
        closed_or_cleared = True
        for session in sessions:
            rows = [
                item
                for item in self._payloads("ephemeral_audio_lifecycle_events", "sequence_index")
                if item.get("ring_buffer_session_id") == session.get("ephemeral_audio_session_id")
            ]
            if rows and rows[-1].get("new_status") not in {"cleared", "closed"}:
                closed_or_cleared = False
        deletion_hash_bound = all(
            item.get("content_sha256_before_deletion") and item.get("deletion_authorized") and item.get("deletion_verified")
            for item in deletions
        )
        authorized_distinguished = all(
            self.verify_artifact(str(item["artifact_id"])).get("status") in {"authorized_waveform_deletion", "artifact_valid"}
            for item in deletions
        )
        reasons: list[str] = []
        checks = {
            "normal_ephemeral_pcm_blob_count": len(ephemeral_artifacts) == 0,
            "ring_buffers_cleared_on_close": closed_or_cleared,
            "no_temp_audio_files_created": len(temp_files) == 0,
            "deletion_records_hash_bound": deletion_hash_bound,
            "authorized_deletions_distinguished_from_missing_blobs": authorized_distinguished,
        }
        reasons.extend(name for name, valid in checks.items() if not valid)
        status = "passed_ephemeral_audio_and_auditable_deletion_foundation" if not reasons else "blocked_ephemeral_audio_deletion_foundation"
        return EphemeralAudioDeletionFoundationAuditRecord(
            audit_id=stable_id("ephemeral_audio_deletion_audit"),
            schema_version=EPHEMERAL_AUDIO_DELETION_AUDIT_SCHEMA_VERSION,
            created_at=utc_now(),
            ephemeral_session_count=len(sessions),
            evidence_excerpt_count=len(excerpts),
            deletion_record_count=len(deletions),
            normal_ephemeral_pcm_blob_count=0 if len(ephemeral_artifacts) == 0 else len(ephemeral_artifacts),
            normal_ephemeral_pcm_artifact_count=0 if len(ephemeral_artifacts) == 0 else len(ephemeral_artifacts),
            ring_buffers_cleared_on_close=closed_or_cleared,
            no_temp_audio_files_created=len(temp_files) == 0,
            audio_primitive_schema_defined=True,
            observed_expected_schema_shared=True,
            low_level_prosody_fields_present=True,
            semantic_fields_forced_null=True,
            speaker_profile_created=False,
            speech_content_lane_created=False,
            automatic_retention_created=False,
            deletion_records_hash_bound=deletion_hash_bound,
            shared_blob_reference_policy_valid=True,
            authorized_deletions_distinguished_from_missing_blobs=authorized_distinguished,
            raw_trace_unchanged=True,
            deletion_trace_append_only=True,
            audit_status=status,
            failure_reasons=tuple(reasons),
        )

    def _recover_temporary_files(self) -> None:
        for path in self.root_dir.glob("*.tmp"):
            target = self.quarantine_dir / f"{path.name}.{uuid4().hex}.tmp"
            shutil.move(str(path), str(target))

    def _recover_running_sessions(self) -> None:
        try:
            sessions = self.list_capture_sessions()
        except Exception:
            return
        for payload in sessions:
            session_id = str(payload["session_id"])
            latest = self._latest_lifecycle_status(session_id)
            if latest and latest not in TERMINAL_LIFECYCLE_STATUSES:
                session = SensorCaptureSessionRecord(**payload)
                self.append_lifecycle_event(
                    session=session,
                    previous_status=latest,
                    new_status="recovered_aborted",
                    manual_command=None,
                    reason_code="store_open_recovered_running_session",
                )

    def _latest_lifecycle_status(self, session_id: str) -> str | None:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT new_status FROM sensor_capture_lifecycle_events WHERE session_id = ? ORDER BY sequence_index DESC LIMIT 1",
                (session_id,),
            ).fetchone()
        return None if row is None else str(row["new_status"])

    def _lifecycle_order_valid(self) -> bool:
        by_session: dict[str, list[str]] = {}
        for item in self._payloads("sensor_capture_lifecycle_events", "sequence_index"):
            by_session.setdefault(str(item["session_id"]), []).append(str(item["new_status"]))
        for statuses in by_session.values():
            if not statuses or statuses[0] != "created":
                return False
        return True


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


def _optional_int(value: Any) -> int | None:
    return None if value is None else int(value)


def _rect_value(metadata: dict[str, Any], key: str) -> Any:
    rect = metadata.get("capture_rectangle")
    if isinstance(rect, dict):
        return rect.get(key)
    return None


def _metadata_without_raw_content(metadata: dict[str, Any]) -> dict[str, Any]:
    blocked = {"data", "bytes", "raw_bytes", "base64", "payload_bytes", "pcm_bytes", "pixel_bytes"}
    return {str(key): plain(value) for key, value in metadata.items() if str(key) not in blocked}


def _monotonic_order_valid(traces: tuple[TraceEnvelope, ...]) -> bool:
    by_session: dict[str, list[TraceEnvelope]] = {}
    for trace in traces:
        by_session.setdefault(trace.session_id, []).append(trace)
    for session_traces in by_session.values():
        ordered = sorted(session_traces, key=lambda item: item.sequence_index)
        if [item.sequence_index for item in ordered] != list(range(len(ordered))):
            return False
        ticks = [item.monotonic_tick for item in ordered]
        if any(left > right for left, right in zip(ticks, ticks[1:])):
            return False
    return True


def _audit_status(
    reasons: list[str],
    orphan_blob_count: int,
    missing_blob_count: int,
    authorized_deleted_blob_count: int = 0,
) -> str:
    if missing_blob_count:
        return "blocked_missing_blob"
    mapping = {
        "all_artifact_paths_relative": "blocked_path_escape",
        "all_artifact_paths_inside_state_dir": "blocked_path_escape",
        "all_artifact_hashes_valid": "blocked_artifact_hash_mismatch",
        "all_artifact_lengths_valid": "blocked_artifact_length_mismatch",
        "all_trace_links_valid": "blocked_trace_link_failure",
        "monotonic_order_valid": "blocked_monotonic_order_failure",
        "lifecycle_order_valid": "blocked_lifecycle_order_failure",
        "semantic_labels_absent": "blocked_semantic_label_present",
        "perception_records_absent": "blocked_perception_record_present",
        "learning_records_absent": "blocked_learning_record_present",
        "memory_records_absent": "blocked_memory_record_present",
    }
    for reason in reasons:
        if reason in mapping:
            return mapping[reason]
    if orphan_blob_count:
        return "passed_with_reported_orphan_blob"
    if authorized_deleted_blob_count:
        return "authorized_waveform_deletion"
    return "passed_real_host_sensor_raw_artifact_store"
