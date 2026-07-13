"""SQLite persistence for teacher-gated bounded embodied sessions."""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from ashl_core_v1.runtime.bounded_embodied_session_runtime import (
    BoundedEmbodiedSessionStage,
    BoundedEmbodiedSessionState,
    BoundedEmbodiedSessionStatus,
    PendingTeacherReviewRecord,
)
from ashl_core_v1.runtime.trace_envelope import TraceEnvelope
from ashl_core_v1.runtime.trace_envelope import (
    TraceIdentityCollisionError,
    trace_identity_matches,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import (
    ALLOWED_APPROVAL_SCOPES,
    FULL_COMMIT_APPROVAL_SCOPE,
    SessionLearningEvidenceSnapshot,
    calculate_evidence_identity_sha256,
    calculate_sha256,
    validate_session_learning_evidence_snapshot,
)


STORE_SCHEMA_NAME = "ashl_teacher_gated_session_store"
STORE_SCHEMA_VERSION = "v1"
LEGACY_STORE_SCHEMA_VERSION = "v0"
STORE_FILENAME = "ashl_bounded_session_v1.sqlite3"

ALLOWED_JOURNAL_KINDS = {
    "session_persisted",
    "teacher_decision_recorded",
    "session_resumed",
    "learning_pipeline_started",
    "learning_pipeline_completed",
    "interpretation_commit_prepared",
    "session_committed",
    "session_rolled_back",
    "session_paused",
    "session_failed",
}

ALLOWED_REVIEW_STATUSES = {
    "pending",
    "approved",
    "rejected",
    "deferred",
    "needs_more_evidence",
    "conflict_detected",
    "session_aborted",
}

FINAL_DECISIONS = {"approved", "rejected"}
ALLOWED_DECISIONS = FINAL_DECISIONS | {
    "deferred",
    "needs_more_evidence",
    "conflict_detected",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plain(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(_plain(value), ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def payload_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _json_loads(value: str | bytes | None, default: Any) -> Any:
    if not value:
        return default
    return json.loads(value)


def _tuple_of_str(value: Iterable[Any]) -> tuple[str, ...]:
    return tuple(str(item) for item in value)


@dataclass(frozen=True)
class PersistedCheckpoint:
    checkpoint_id: str
    session_id: str
    session_status: str
    session_state: dict[str, Any]
    event_stack: tuple[str, ...]
    working_readback_snapshot: tuple[str, ...]
    pending_review_refs: tuple[str, ...]
    trace_cursor: int
    runtime_records: dict[str, Any]


class TeacherGatedSessionStore:
    """Explicit-state-dir SQLite store for Package 116 session persistence."""

    def __init__(self, state_dir: str | Path) -> None:
        if state_dir is None:
            raise ValueError("state_dir is required")
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.state_dir / STORE_FILENAME
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.db_path))
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
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

    def validate_schema(self) -> dict[str, object]:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT schema_name, schema_version FROM store_metadata"
            ).fetchone()
            tables = {
                item["name"]
                for item in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
        required = {
            "store_metadata",
            "session_heads",
            "session_journal",
            "session_checkpoints",
            "trace_envelopes",
            "pending_teacher_reviews",
            "teacher_decisions",
            "reviewed_interpretation_commits",
            "working_readback_commits",
            "session_commit_records",
            "session_rollback_records",
            "learning_evidence_snapshots",
            "teacher_decision_target_bindings",
            "learning_pipeline_identity_bindings",
            "interpretation_provenance_bindings",
            "runtime_capability_profiles",
        }
        valid = (
            row is not None
            and row["schema_name"] == STORE_SCHEMA_NAME
            and row["schema_version"] == STORE_SCHEMA_VERSION
            and required.issubset(tables)
        )
        return {
            "valid": valid,
            "schema_name": row["schema_name"] if row else None,
            "schema_version": row["schema_version"] if row else None,
            "missing_tables": tuple(sorted(required - tables)),
            "db_path": str(self.db_path),
        }

    def list_sessions(self) -> tuple[dict[str, object], ...]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT session_id, current_status, current_checkpoint_id, version, updated_at "
                "FROM session_heads ORDER BY updated_at"
            ).fetchall()
        return tuple(dict(row) for row in rows)

    def persist_waiting_session(
        self,
        *,
        state: BoundedEmbodiedSessionState,
        traces: tuple[TraceEnvelope, ...],
        pending_reviews: tuple[PendingTeacherReviewRecord, ...],
        runtime_records: dict[str, Any],
        expected_version: int | None = None,
    ) -> str:
        if state.status != BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW:
            raise ValueError("only WAITING_TEACHER_REVIEW sessions can be persisted")
        checkpoint_id = self._checkpoint_id(state.session_id)
        with self.connection() as connection:
            connection.execute("BEGIN")
            try:
                for trace in traces:
                    self._insert_trace(connection, trace)
                snapshot = runtime_records.get("session_learning_evidence_snapshot")
                if snapshot is not None:
                    self._insert_evidence_snapshot(connection, snapshot)
                profile = runtime_records.get("runtime_capability_profile")
                if profile is not None:
                    self._insert_runtime_capability_profile(connection, profile)
                self._append_checkpoint(
                    connection,
                    checkpoint_id=checkpoint_id,
                    state=state,
                    runtime_records=runtime_records,
                )
                checkpoint_version = self._checkpoint_version(connection, checkpoint_id)
                for review in pending_reviews:
                    self._insert_pending_review(
                        connection,
                        review,
                        checkpoint_id=checkpoint_id,
                        checkpoint_version=checkpoint_version,
                    )
                self._upsert_session_head(
                    connection,
                    session_id=state.session_id,
                    status=state.status.value,
                    checkpoint_id=checkpoint_id,
                    expected_version=expected_version,
                )
                self._append_journal(
                    connection,
                    session_id=state.session_id,
                    journal_kind="session_persisted",
                    payload={
                        "checkpoint_id": checkpoint_id,
                        "trace_count": len(traces),
                        "pending_review_ids": [item.pending_teacher_review_id for item in pending_reviews],
                    },
                )
            except Exception:
                connection.rollback()
                raise
            connection.commit()
        return checkpoint_id

    def load_session_state(self, session_id: str) -> BoundedEmbodiedSessionState:
        checkpoint = self.load_latest_checkpoint(session_id)
        data = dict(checkpoint.session_state)
        data["status"] = BoundedEmbodiedSessionStatus(str(data["status"]))
        data["current_stage"] = BoundedEmbodiedSessionStage(str(data["current_stage"]))
        for name in (
            "event_stack_frame_ids",
            "closed_event_frame_ids",
            "working_readback_snapshot_refs",
            "pending_teacher_review_ids",
            "resolved_teacher_review_ids",
            "current_home_surface_link_ids",
            "boundary_failure_codes",
            "runtime_failure_codes",
        ):
            data[name] = tuple(data.get(name) or ())
        return BoundedEmbodiedSessionState(**data)

    def load_latest_checkpoint(self, session_id: str) -> PersistedCheckpoint:
        with self.connection() as connection:
            head = connection.execute(
                "SELECT current_checkpoint_id FROM session_heads WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if head is None:
                raise KeyError(f"session not found: {session_id}")
            row = connection.execute(
                "SELECT * FROM session_checkpoints WHERE checkpoint_id = ?",
                (head["current_checkpoint_id"],),
            ).fetchone()
        if row is None:
            raise KeyError(f"checkpoint not found for session: {session_id}")
        return PersistedCheckpoint(
            checkpoint_id=row["checkpoint_id"],
            session_id=row["session_id"],
            session_status=row["session_status"],
            session_state=dict(_json_loads(row["session_state_json"], {})),
            event_stack=tuple(_json_loads(row["event_stack_json"], [])),
            working_readback_snapshot=tuple(_json_loads(row["working_readback_snapshot_json"], [])),
            pending_review_refs=tuple(_json_loads(row["pending_review_refs_json"], [])),
            trace_cursor=int(row["trace_cursor"]),
            runtime_records=dict(_json_loads(row["runtime_records_json"], {})),
        )

    def list_trace_envelopes(self, session_id: str) -> tuple[TraceEnvelope, ...]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM trace_envelopes WHERE session_id = ? ORDER BY sequence_index",
                (session_id,),
            ).fetchall()
        return tuple(self._trace_from_row(row) for row in rows)

    def list_pending_reviews(self, session_id: str) -> tuple[PendingTeacherReviewRecord, ...]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM pending_teacher_reviews WHERE session_id = ? ORDER BY created_at",
                (session_id,),
            ).fetchall()
        return tuple(self._pending_review_from_row(row) for row in rows)

    def load_evidence_snapshot(self, evidence_snapshot_id: str) -> SessionLearningEvidenceSnapshot:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT * FROM learning_evidence_snapshots WHERE evidence_snapshot_id = ?",
                (evidence_snapshot_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"evidence snapshot not found: {evidence_snapshot_id}")
        return SessionLearningEvidenceSnapshot(
            evidence_snapshot_id=row["evidence_snapshot_id"],
            schema_version="ashl_session_learning_evidence_snapshot_v0",
            created_at=row["created_at"],
            session_id=row["session_id"],
            root_event_id=row["root_event_id"],
            source_event_id=row["source_event_id"],
            source_learning_evidence_packet_id=_json_loads(row["canonical_payload_json"], {}).get("source_learning_evidence_packet_id", ""),
            source_learning_feedback_mapping_id=_json_loads(row["canonical_payload_json"], {}).get("source_learning_feedback_mapping_id", ""),
            source_learning_feedback_bridge_id=_json_loads(row["canonical_payload_json"], {}).get("source_learning_feedback_bridge_id", ""),
            source_existing_review_adapter_id=_json_loads(row["canonical_payload_json"], {}).get("source_existing_review_adapter_id", ""),
            evidence_kind=row["evidence_kind"],
            evidence_theme=row["evidence_theme"],
            feedback_candidate_kind=row["feedback_candidate_kind"],
            feedback_candidate_scope=row["feedback_candidate_scope"],
            evidence_summary=str(_json_loads(row["canonical_payload_json"], {}).get("evidence_summary", "")),
            canonical_evidence_payload=dict(_json_loads(row["canonical_payload_json"], {})),
            source_record_refs=tuple(_json_loads(row["source_record_refs_json"], [])),
            source_trace_refs=tuple(_json_loads(row["source_trace_refs_json"], [])),
            canonical_payload_sha256=row["canonical_payload_sha256"],
            evidence_identity_sha256=row["evidence_identity_sha256"],
            immutable_snapshot=bool(row["immutable_snapshot"]),
            teacher_review_required=True,
            contains_raw_sensor_payload=False,
            contains_interpreted_memory=False,
        )

    def list_evidence_snapshots(self, session_id: str) -> tuple[SessionLearningEvidenceSnapshot, ...]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT evidence_snapshot_id FROM learning_evidence_snapshots WHERE session_id = ? ORDER BY created_at",
                (session_id,),
            ).fetchall()
        return tuple(self.load_evidence_snapshot(row["evidence_snapshot_id"]) for row in rows)

    def get_pending_review(self, pending_review_id: str) -> PendingTeacherReviewRecord:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT * FROM pending_teacher_reviews WHERE pending_teacher_review_id = ?",
                (pending_review_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"pending review not found: {pending_review_id}")
        return self._pending_review_from_row(row)

    def insert_teacher_decision(
        self,
        *,
        teacher_decision_id: str,
        session_id: str,
        pending_teacher_review_id: str,
        decision: str,
        reason_codes: tuple[str, ...],
        teacher_note: str,
        decision_source: str,
        source_trace_refs: tuple[str, ...],
        approval_scope: str,
        expected_evidence_identity_sha256: str | None = None,
        explicit_target_binding: bool = True,
        scope_sufficient_for_requested_operation: bool = False,
        resolve_review: bool = False,
    ) -> None:
        if decision not in ALLOWED_DECISIONS:
            raise ValueError(f"unknown teacher decision: {decision}")
        if decision_source != "teacher_interface":
            raise ValueError("decision_source must be teacher_interface")
        if approval_scope not in ALLOWED_APPROVAL_SCOPES:
            raise ValueError(f"unknown approval_scope: {approval_scope}")
        review = self.get_pending_review(pending_teacher_review_id)
        if review.session_id != session_id:
            raise ValueError("teacher decision targets a review from another session")
        if decision in FINAL_DECISIONS and scope_sufficient_for_requested_operation and self.final_decision_exists(pending_teacher_review_id):
            raise ValueError("duplicate final decision")
        if review.resolved:
            raise ValueError("teacher decision targets a resolved review")
        if not review.evidence_snapshot_id:
            raise ValueError("pending review is missing evidence snapshot binding")
        snapshot = self.load_evidence_snapshot(review.evidence_snapshot_id)
        validation = validate_session_learning_evidence_snapshot(snapshot)
        if not validation["valid"]:
            raise ValueError(f"invalid evidence snapshot: {validation['reasons']}")
        if expected_evidence_identity_sha256 and expected_evidence_identity_sha256 != snapshot.evidence_identity_sha256:
            raise ValueError("expected evidence hash does not match persisted evidence snapshot")
        if snapshot.evidence_identity_sha256 != review.evidence_identity_sha256:
            raise ValueError("pending review evidence identity does not match snapshot")
        if snapshot.canonical_payload_sha256 != review.canonical_payload_sha256:
            raise ValueError("pending review canonical payload hash does not match snapshot")
        checkpoint = self.load_latest_checkpoint(session_id)
        if review.target_session_checkpoint_id != checkpoint.checkpoint_id:
            raise ValueError("teacher decision targets a stale checkpoint")
        if review.target_checkpoint_version != self._checkpoint_version_by_id(checkpoint.checkpoint_id):
            raise ValueError("teacher decision targets a stale checkpoint version")
        payload = {
            "teacher_decision_id": teacher_decision_id,
            "session_id": session_id,
            "pending_teacher_review_id": pending_teacher_review_id,
            "decision": decision,
            "reason_codes": list(reason_codes),
            "teacher_note": teacher_note,
            "decision_source": decision_source,
            "source_trace_refs": list(source_trace_refs),
            "approval_scope": approval_scope,
            "target_evidence_snapshot_id": snapshot.evidence_snapshot_id,
            "target_evidence_identity_sha256": snapshot.evidence_identity_sha256,
            "target_canonical_payload_sha256": snapshot.canonical_payload_sha256,
            "target_review_nonce": review.review_nonce,
            "target_checkpoint_id": checkpoint.checkpoint_id,
            "target_checkpoint_version": review.target_checkpoint_version,
            "explicit_target_binding": explicit_target_binding,
            "scope_sufficient_for_requested_operation": scope_sufficient_for_requested_operation,
        }
        with self.connection() as connection:
            connection.execute("BEGIN")
            try:
                connection.execute(
                    """
                    INSERT INTO teacher_decisions (
                        teacher_decision_id, session_id, pending_teacher_review_id,
                        decision, reason_codes_json, teacher_note, decision_source,
                        created_at, source_trace_refs_json, payload_sha256,
                        approval_scope, target_evidence_snapshot_id,
                        target_evidence_identity_sha256, target_canonical_payload_sha256,
                        target_review_nonce, target_checkpoint_id, target_checkpoint_version,
                        explicit_target_binding, scope_sufficient_for_requested_operation
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        teacher_decision_id,
                        session_id,
                        pending_teacher_review_id,
                        decision,
                        canonical_json(reason_codes),
                        teacher_note,
                        decision_source,
                        _now(),
                        canonical_json(source_trace_refs),
                        payload_sha256(payload),
                        approval_scope,
                        snapshot.evidence_snapshot_id,
                        snapshot.evidence_identity_sha256,
                        snapshot.canonical_payload_sha256,
                        review.review_nonce,
                        checkpoint.checkpoint_id,
                        int(review.target_checkpoint_version or 0),
                        1 if explicit_target_binding else 0,
                        1 if scope_sufficient_for_requested_operation else 0,
                    ),
                )
                binding = {
                    "binding_id": f"teacher_decision_target_binding:{teacher_decision_id}",
                    **payload,
                    "created_at": _now(),
                }
                connection.execute(
                    """
                    INSERT INTO teacher_decision_target_bindings (
                        binding_id, teacher_decision_id, pending_teacher_review_id,
                        session_id, evidence_snapshot_id, evidence_identity_sha256,
                        canonical_payload_sha256, review_nonce, checkpoint_id,
                        checkpoint_version, approval_scope, created_at, payload_sha256
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        binding["binding_id"],
                        teacher_decision_id,
                        pending_teacher_review_id,
                        session_id,
                        snapshot.evidence_snapshot_id,
                        snapshot.evidence_identity_sha256,
                        snapshot.canonical_payload_sha256,
                        review.review_nonce,
                        checkpoint.checkpoint_id,
                        int(review.target_checkpoint_version or 0),
                        approval_scope,
                        binding["created_at"],
                        payload_sha256(binding),
                    ),
                )
                if resolve_review:
                    self._update_pending_review_status(connection, pending_teacher_review_id, decision)
                self._append_journal(
                    connection,
                    session_id=session_id,
                    journal_kind="teacher_decision_recorded",
                    payload=payload,
                )
            except Exception:
                connection.rollback()
                raise
            connection.commit()

    def get_teacher_decision(self, teacher_decision_id: str) -> dict[str, object]:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT * FROM teacher_decisions WHERE teacher_decision_id = ?",
                (teacher_decision_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"teacher decision not found: {teacher_decision_id}")
        return {
            "teacher_decision_id": row["teacher_decision_id"],
            "session_id": row["session_id"],
            "pending_teacher_review_id": row["pending_teacher_review_id"],
            "decision": row["decision"],
            "reason_codes": tuple(_json_loads(row["reason_codes_json"], [])),
            "teacher_note": row["teacher_note"],
            "decision_source": row["decision_source"],
            "created_at": row["created_at"],
            "source_trace_refs": tuple(_json_loads(row["source_trace_refs_json"], [])),
            "payload_sha256": row["payload_sha256"],
            "approval_scope": row["approval_scope"],
            "target_evidence_snapshot_id": row["target_evidence_snapshot_id"],
            "target_evidence_identity_sha256": row["target_evidence_identity_sha256"],
            "target_canonical_payload_sha256": row["target_canonical_payload_sha256"],
            "target_review_nonce": row["target_review_nonce"],
            "target_checkpoint_id": row["target_checkpoint_id"],
            "target_checkpoint_version": row["target_checkpoint_version"],
            "explicit_target_binding": bool(row["explicit_target_binding"]),
            "scope_sufficient_for_requested_operation": bool(row["scope_sufficient_for_requested_operation"]),
        }

    def list_teacher_decisions(self, session_id: str) -> tuple[dict[str, object], ...]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM teacher_decisions WHERE session_id = ? ORDER BY created_at",
                (session_id,),
            ).fetchall()
        return tuple(
            {
                "teacher_decision_id": row["teacher_decision_id"],
                "session_id": row["session_id"],
                "pending_teacher_review_id": row["pending_teacher_review_id"],
                "decision": row["decision"],
                "reason_codes": tuple(_json_loads(row["reason_codes_json"], [])),
                "teacher_note": row["teacher_note"],
                "decision_source": row["decision_source"],
                "created_at": row["created_at"],
                "source_trace_refs": tuple(_json_loads(row["source_trace_refs_json"], [])),
                "payload_sha256": row["payload_sha256"],
                "approval_scope": row["approval_scope"],
                "target_evidence_snapshot_id": row["target_evidence_snapshot_id"],
                "target_evidence_identity_sha256": row["target_evidence_identity_sha256"],
                "target_canonical_payload_sha256": row["target_canonical_payload_sha256"],
                "target_review_nonce": row["target_review_nonce"],
                "target_checkpoint_id": row["target_checkpoint_id"],
                "target_checkpoint_version": row["target_checkpoint_version"],
                "explicit_target_binding": bool(row["explicit_target_binding"]),
                "scope_sufficient_for_requested_operation": bool(row["scope_sufficient_for_requested_operation"]),
            }
            for row in rows
        )

    def final_decision_exists(self, pending_teacher_review_id: str) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM teacher_decisions WHERE pending_teacher_review_id = ? "
                "AND decision IN ('approved', 'rejected') "
                "AND scope_sufficient_for_requested_operation = 1 LIMIT 1",
                (pending_teacher_review_id,),
            ).fetchone()
        return row is not None

    def list_teacher_decision_target_bindings(self, session_id: str) -> tuple[dict[str, Any], ...]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM teacher_decision_target_bindings WHERE session_id = ? ORDER BY created_at",
                (session_id,),
            ).fetchall()
        return tuple(
            {
                "binding_id": row["binding_id"],
                "teacher_decision_id": row["teacher_decision_id"],
                "pending_teacher_review_id": row["pending_teacher_review_id"],
                "session_id": row["session_id"],
                "evidence_snapshot_id": row["evidence_snapshot_id"],
                "evidence_identity_sha256": row["evidence_identity_sha256"],
                "canonical_payload_sha256": row["canonical_payload_sha256"],
                "review_nonce": row["review_nonce"],
                "checkpoint_id": row["checkpoint_id"],
                "checkpoint_version": row["checkpoint_version"],
                "approval_scope": row["approval_scope"],
                "created_at": row["created_at"],
                "payload_sha256": row["payload_sha256"],
            }
            for row in rows
        )

    def list_learning_pipeline_identity_bindings(self, session_id: str) -> tuple[dict[str, Any], ...]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM learning_pipeline_identity_bindings WHERE session_id = ? ORDER BY created_at",
                (session_id,),
            ).fetchall()
        return tuple(
            {
                "binding_id": row["binding_id"],
                "session_id": row["session_id"],
                "evidence_snapshot_id": row["evidence_snapshot_id"],
                "evidence_identity_sha256": row["evidence_identity_sha256"],
                "pipeline_stage": row["pipeline_stage"],
                "target_record_kind": row["target_record_kind"],
                "target_record_id": row["target_record_id"],
                "source_binding_id": row["source_binding_id"],
                "source_trace_refs": tuple(_json_loads(row["source_trace_refs_json"], [])),
                "identity_preserved": True,
                "validator_passed": bool(row["validator_passed"]),
                "created_at": row["created_at"],
                "payload_sha256": row["payload_sha256"],
            }
            for row in rows
        )

    def list_interpretation_provenance_bindings(self, session_id: str) -> tuple[dict[str, Any], ...]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM interpretation_provenance_bindings WHERE session_id = ? ORDER BY created_at",
                (session_id,),
            ).fetchall()
        return tuple(
            {
                "provenance_binding_id": row["provenance_binding_id"],
                "session_id": row["session_id"],
                "reviewed_interpretation_commit_id": row["interpretation_commit_id"],
                "working_readback_commit_id": None,
                "evidence_snapshot_id": row["evidence_snapshot_id"],
                "evidence_identity_sha256": row["evidence_identity_sha256"],
                "teacher_approval_scope": None,
                "pipeline_identity_binding_ids": tuple(_json_loads(row["pipeline_binding_ids_json"], [])),
                "identity_chain_complete": bool(row["identity_chain_complete"]),
                "identity_chain_valid": bool(row["identity_chain_valid"]),
                "source_trace_refs": tuple(),
                "created_at": row["created_at"],
                "payload_sha256": row["payload_sha256"],
            }
            for row in rows
        )

    def append_trace_envelope(self, envelope: TraceEnvelope) -> TraceEnvelope:
        with self.connection() as connection:
            connection.execute("BEGIN")
            try:
                stored = self._insert_trace(connection, envelope)
            except TraceIdentityCollisionError:
                connection.rollback()
                self.append_failure_journal(
                    envelope.session_id,
                    "unknown",
                    _now(),
                    "blocked_trace_identity_collision",
                )
                raise
            except Exception:
                connection.rollback()
                raise
            connection.commit()
        return stored

    def update_session_checkpoint(
        self,
        *,
        state: BoundedEmbodiedSessionState,
        runtime_records: dict[str, Any],
        journal_kind: str,
        journal_payload: dict[str, Any],
    ) -> str:
        checkpoint_id = self._checkpoint_id(state.session_id)
        with self.connection() as connection:
            connection.execute("BEGIN")
            try:
                self._append_checkpoint(
                    connection,
                    checkpoint_id=checkpoint_id,
                    state=state,
                    runtime_records=runtime_records,
                )
                self._upsert_session_head(
                    connection,
                    session_id=state.session_id,
                    status=str(state.status.value if hasattr(state.status, "value") else state.status),
                    checkpoint_id=checkpoint_id,
                    expected_version=None,
                )
                self._append_journal(
                    connection,
                    session_id=state.session_id,
                    journal_kind=journal_kind,
                    payload=journal_payload,
                )
            except Exception:
                connection.rollback()
                raise
            connection.commit()
        return checkpoint_id

    def commit_approved_interpretation(
        self,
        *,
        state: BoundedEmbodiedSessionState,
        runtime_records: dict[str, Any],
        teacher_decision_id: str,
        interpretation_commit: dict[str, Any],
        working_readback_commit: dict[str, Any],
        session_commit_record: dict[str, Any],
        trace_envelopes: tuple[TraceEnvelope, ...],
        fail_after: str | None = None,
    ) -> None:
        with self.connection() as connection:
            connection.execute("BEGIN")
            try:
                for envelope in trace_envelopes:
                    self._insert_trace(connection, envelope)
                    if fail_after == envelope.record_kind:
                        raise RuntimeError(f"forced atomic failure after {envelope.record_kind}")
                self._insert_pipeline_identity_bindings(
                    connection,
                    tuple(interpretation_commit.get("pipeline_identity_bindings", ())),
                )
                if fail_after == "learning_pipeline_identity_bindings":
                    raise RuntimeError("forced atomic failure after pipeline identity bindings")
                self._insert_interpretation_commit(connection, interpretation_commit)
                if fail_after == "reviewed_interpretation_commits":
                    raise RuntimeError("forced atomic failure after interpretation commit")
                self._insert_working_readback_commit(connection, working_readback_commit)
                if fail_after == "working_readback_commits":
                    raise RuntimeError("forced atomic failure after working readback commit")
                provenance_binding = interpretation_commit.get("interpretation_provenance_binding")
                if provenance_binding:
                    self._insert_interpretation_provenance_binding(connection, provenance_binding)
                connection.execute(
                    """
                    INSERT INTO session_commit_records (
                        session_commit_id, session_id, teacher_decision_id,
                        reviewed_interpretation_commit_id, status_before, status_after,
                        raw_trace_count_before, raw_trace_count_after,
                        raw_trace_deleted_count, raw_trace_modified_count,
                        interpretation_commit_count, working_readback_commit_count,
                        atomic_transaction_committed, commit_status, commit_summary,
                        source_trace_refs_json, created_at, payload_sha256
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_commit_record["session_commit_id"],
                        state.session_id,
                        teacher_decision_id,
                        interpretation_commit["reviewed_interpretation_commit_id"],
                        session_commit_record["status_before"],
                        session_commit_record["status_after"],
                        int(session_commit_record["raw_trace_count_before"]),
                        int(session_commit_record["raw_trace_count_after"]),
                        int(session_commit_record["raw_trace_deleted_count"]),
                        int(session_commit_record["raw_trace_modified_count"]),
                        int(session_commit_record["interpretation_commit_count"]),
                        int(session_commit_record["working_readback_commit_count"]),
                        1 if session_commit_record["atomic_transaction_committed"] else 0,
                        session_commit_record["commit_status"],
                        session_commit_record["commit_summary"],
                        canonical_json(session_commit_record["source_trace_refs"]),
                        session_commit_record["created_at"],
                        payload_sha256(session_commit_record),
                    ),
                )
                self._append_checkpoint(
                    connection,
                    checkpoint_id=self._checkpoint_id(state.session_id),
                    state=state,
                    runtime_records=runtime_records,
                )
                self._upsert_session_head(
                    connection,
                    session_id=state.session_id,
                    status=BoundedEmbodiedSessionStatus.COMMITTED.value,
                    checkpoint_id=self._latest_checkpoint_id(connection, state.session_id),
                    expected_version=None,
                )
                self._append_journal(
                    connection,
                    session_id=state.session_id,
                    journal_kind="session_committed",
                    payload=session_commit_record,
                )
            except Exception:
                connection.rollback()
                self.append_failure_journal(state.session_id, str(state.status.value if hasattr(state.status, "value") else state.status), str(_now()), "commit_failed")
                raise
            connection.commit()

    def rollback_session(
        self,
        *,
        state: BoundedEmbodiedSessionState,
        runtime_records: dict[str, Any],
        rollback_record: dict[str, Any],
        trace_envelopes: tuple[TraceEnvelope, ...],
    ) -> None:
        with self.connection() as connection:
            connection.execute("BEGIN")
            try:
                for envelope in trace_envelopes:
                    self._insert_trace(connection, envelope)
                connection.execute(
                    """
                    INSERT INTO session_rollback_records (
                        session_rollback_id, session_id, teacher_decision_id, rollback_reason,
                        status_before, status_after, raw_trace_count_before,
                        raw_trace_count_after, raw_trace_deleted_count,
                        raw_trace_modified_count, uncommitted_interpretation_discarded,
                        working_state_invalidated, pending_review_final_status,
                        rollback_status, rollback_summary, source_trace_refs_json,
                        created_at, payload_sha256
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        rollback_record["session_rollback_id"],
                        state.session_id,
                        rollback_record.get("teacher_decision_id"),
                        rollback_record["rollback_reason"],
                        rollback_record["status_before"],
                        rollback_record["status_after"],
                        int(rollback_record["raw_trace_count_before"]),
                        int(rollback_record["raw_trace_count_after"]),
                        int(rollback_record["raw_trace_deleted_count"]),
                        int(rollback_record["raw_trace_modified_count"]),
                        1 if rollback_record["uncommitted_interpretation_discarded"] else 0,
                        1 if rollback_record["working_state_invalidated"] else 0,
                        rollback_record["pending_review_final_status"],
                        rollback_record["rollback_status"],
                        rollback_record["rollback_summary"],
                        canonical_json(rollback_record["source_trace_refs"]),
                        rollback_record["created_at"],
                        payload_sha256(rollback_record),
                    ),
                )
                self._append_checkpoint(
                    connection,
                    checkpoint_id=self._checkpoint_id(state.session_id),
                    state=state,
                    runtime_records=runtime_records,
                )
                self._upsert_session_head(
                    connection,
                    session_id=state.session_id,
                    status=BoundedEmbodiedSessionStatus.ROLLED_BACK.value,
                    checkpoint_id=self._latest_checkpoint_id(connection, state.session_id),
                    expected_version=None,
                )
                self._append_journal(
                    connection,
                    session_id=state.session_id,
                    journal_kind="session_rolled_back",
                    payload=rollback_record,
                )
            except Exception:
                connection.rollback()
                raise
            connection.commit()

    def pause_session(
        self,
        *,
        state: BoundedEmbodiedSessionState,
        runtime_records: dict[str, Any],
        trace_envelopes: tuple[TraceEnvelope, ...],
        pause_payload: dict[str, Any],
    ) -> None:
        with self.connection() as connection:
            connection.execute("BEGIN")
            try:
                for envelope in trace_envelopes:
                    self._insert_trace(connection, envelope)
                self._append_checkpoint(
                    connection,
                    checkpoint_id=self._checkpoint_id(state.session_id),
                    state=state,
                    runtime_records=runtime_records,
                )
                self._upsert_session_head(
                    connection,
                    session_id=state.session_id,
                    status=BoundedEmbodiedSessionStatus.PAUSED.value,
                    checkpoint_id=self._latest_checkpoint_id(connection, state.session_id),
                    expected_version=None,
                )
                self._append_journal(
                    connection,
                    session_id=state.session_id,
                    journal_kind="session_paused",
                    payload=pause_payload,
                )
            except Exception:
                connection.rollback()
                raise
            connection.commit()

    def append_failure_journal(
        self,
        session_id: str,
        status_before: str,
        created_at: str,
        reason: str,
    ) -> None:
        with self.connection() as connection:
            connection.execute("BEGIN")
            try:
                self._append_journal(
                    connection,
                    session_id=session_id,
                    journal_kind="session_failed",
                    payload={
                        "status_before": status_before,
                        "status_after": BoundedEmbodiedSessionStatus.FAILED.value,
                        "failure_reason": reason,
                        "created_at": created_at,
                    },
                )
                head = connection.execute(
                    "SELECT current_checkpoint_id FROM session_heads WHERE session_id = ?",
                    (session_id,),
                ).fetchone()
                if head is not None:
                    self._upsert_session_head(
                        connection,
                        session_id=session_id,
                        status=BoundedEmbodiedSessionStatus.FAILED.value,
                        checkpoint_id=head["current_checkpoint_id"],
                        expected_version=None,
                    )
            except Exception:
                connection.rollback()
                raise
            connection.commit()

    def load_active_working_readback(self) -> tuple[dict[str, Any], ...]:
        with self.connection() as connection:
            rows = connection.execute(
                """
                SELECT wr.working_readback_commit_id, wr.interpretation_commit_id,
                       wr.readback_payload_json, wr.source_trace_refs_json,
                       wr.source_evidence_snapshot_id, wr.evidence_identity_sha256,
                       wr.source_reviewed_interpretation_commit_id
                FROM working_readback_commits wr
                JOIN reviewed_interpretation_commits ic
                  ON ic.interpretation_commit_id = wr.interpretation_commit_id
                WHERE wr.active_for_future_sessions = 1
                  AND ic.commit_status = 'active'
                ORDER BY wr.created_at
                """
            ).fetchall()
        readback: list[dict[str, Any]] = []
        for row in rows:
            payload = dict(_json_loads(row["readback_payload_json"], {}))
            payload["working_readback_commit_id"] = row["working_readback_commit_id"]
            payload["interpretation_commit_id"] = row["interpretation_commit_id"]
            payload["source_trace_refs"] = tuple(_json_loads(row["source_trace_refs_json"], []))
            payload["source_evidence_snapshot_id"] = row["source_evidence_snapshot_id"]
            payload["evidence_identity_sha256"] = row["evidence_identity_sha256"]
            payload["source_reviewed_interpretation_commit_id"] = row["source_reviewed_interpretation_commit_id"]
            readback.append(payload)
        return tuple(readback)

    def raw_trace_payload_hashes(self, session_id: str) -> tuple[tuple[str, str], ...]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT trace_id, payload_sha256 FROM trace_envelopes "
                "WHERE session_id = ? AND trace_layer = 'raw' ORDER BY sequence_index",
                (session_id,),
            ).fetchall()
        return tuple((row["trace_id"], row["payload_sha256"]) for row in rows)

    def count_rows(self, table_name: str, session_id: str | None = None) -> int:
        if table_name not in {
            "session_journal",
            "session_checkpoints",
            "trace_envelopes",
            "pending_teacher_reviews",
            "teacher_decisions",
            "reviewed_interpretation_commits",
            "working_readback_commits",
            "session_commit_records",
            "session_rollback_records",
            "learning_evidence_snapshots",
            "teacher_decision_target_bindings",
            "learning_pipeline_identity_bindings",
            "interpretation_provenance_bindings",
            "runtime_capability_profiles",
        }:
            raise ValueError(f"unsupported table: {table_name}")
        query = f"SELECT COUNT(*) AS count FROM {table_name}"
        args: tuple[Any, ...] = ()
        if session_id is not None:
            query += " WHERE session_id = ?"
            args = (session_id,)
        with self.connection() as connection:
            row = connection.execute(query, args).fetchone()
        return int(row["count"])

    def validate_trace_table(self, session_id: str) -> dict[str, object]:
        traces = self.list_trace_envelopes(session_id)
        sequence_ok = [trace.sequence_index for trace in traces] == list(range(len(traces)))
        refs_seen: set[str] = set()
        refs_ok = True
        for trace in traces:
            for ref in trace.source_trace_refs:
                if ref not in refs_seen:
                    refs_ok = False
            refs_seen.add(trace.trace_id)
        return {
            "valid": sequence_ok and refs_ok,
            "trace_sequence_monotonic": sequence_ok,
            "trace_source_refs_valid": refs_ok,
            "trace_count": len(traces),
        }

    def _initialize(self) -> None:
        existing_version = self._existing_schema_version()
        if existing_version == LEGACY_STORE_SCHEMA_VERSION:
            backup_path = self.db_path.with_suffix(
                self.db_path.suffix + f".{LEGACY_STORE_SCHEMA_VERSION}.bak"
            )
            if not backup_path.exists():
                shutil.copy2(self.db_path, backup_path)
        elif existing_version not in (None, STORE_SCHEMA_VERSION):
            raise RuntimeError(f"unsupported store schema version: {existing_version}")
        with self.connection() as connection:
            if existing_version == LEGACY_STORE_SCHEMA_VERSION:
                connection.execute("BEGIN EXCLUSIVE")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS store_metadata (
                    schema_name TEXT PRIMARY KEY,
                    schema_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS session_heads (
                    session_id TEXT PRIMARY KEY,
                    current_status TEXT NOT NULL,
                    current_checkpoint_id TEXT,
                    version INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS session_journal (
                    journal_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    sequence_index INTEGER NOT NULL,
                    journal_kind TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    UNIQUE(session_id, sequence_index)
                );
                CREATE TABLE IF NOT EXISTS session_checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    checkpoint_version INTEGER NOT NULL,
                    session_status TEXT NOT NULL,
                    session_state_json TEXT NOT NULL,
                    event_stack_json TEXT NOT NULL,
                    working_readback_snapshot_json TEXT NOT NULL,
                    pending_review_refs_json TEXT NOT NULL,
                    trace_cursor INTEGER NOT NULL,
                    runtime_records_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    UNIQUE(session_id, checkpoint_version)
                );
                CREATE TABLE IF NOT EXISTS trace_envelopes (
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
                CREATE TABLE IF NOT EXISTS pending_teacher_reviews (
                    pending_teacher_review_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    source_learning_feedback_candidate_ref TEXT NOT NULL,
                    source_learning_evidence_packet_ref TEXT NOT NULL,
                    source_trace_refs_json TEXT NOT NULL,
                    review_kind TEXT NOT NULL,
                    current_review_status TEXT NOT NULL,
                    resolved INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS teacher_decisions (
                    teacher_decision_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    pending_teacher_review_id TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    reason_codes_json TEXT NOT NULL,
                    teacher_note TEXT NOT NULL,
                    decision_source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    source_trace_refs_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS reviewed_interpretation_commits (
                    interpretation_commit_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    teacher_decision_id TEXT NOT NULL,
                    reviewed_concept_ref TEXT NOT NULL,
                    memory_learning_trace_ref TEXT NOT NULL,
                    memory_routing_trace_ref TEXT NOT NULL,
                    memory_application_data_ref TEXT NOT NULL,
                    interpretation_payload_json TEXT NOT NULL,
                    source_trace_refs_json TEXT NOT NULL,
                    commit_status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS working_readback_commits (
                    working_readback_commit_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    interpretation_commit_id TEXT NOT NULL,
                    readback_payload_json TEXT NOT NULL,
                    source_trace_refs_json TEXT NOT NULL,
                    active_for_future_sessions INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS session_commit_records (
                    session_commit_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    teacher_decision_id TEXT NOT NULL,
                    reviewed_interpretation_commit_id TEXT NOT NULL,
                    status_before TEXT NOT NULL,
                    status_after TEXT NOT NULL,
                    raw_trace_count_before INTEGER NOT NULL,
                    raw_trace_count_after INTEGER NOT NULL,
                    raw_trace_deleted_count INTEGER NOT NULL,
                    raw_trace_modified_count INTEGER NOT NULL,
                    interpretation_commit_count INTEGER NOT NULL,
                    working_readback_commit_count INTEGER NOT NULL,
                    atomic_transaction_committed INTEGER NOT NULL,
                    commit_status TEXT NOT NULL,
                    commit_summary TEXT NOT NULL,
                    source_trace_refs_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS session_rollback_records (
                    session_rollback_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    teacher_decision_id TEXT,
                    rollback_reason TEXT NOT NULL,
                    status_before TEXT NOT NULL,
                    status_after TEXT NOT NULL,
                    raw_trace_count_before INTEGER NOT NULL,
                    raw_trace_count_after INTEGER NOT NULL,
                    raw_trace_deleted_count INTEGER NOT NULL,
                    raw_trace_modified_count INTEGER NOT NULL,
                    uncommitted_interpretation_discarded INTEGER NOT NULL,
                    working_state_invalidated INTEGER NOT NULL,
                    pending_review_final_status TEXT NOT NULL,
                    rollback_status TEXT NOT NULL,
                    rollback_summary TEXT NOT NULL,
                    source_trace_refs_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS learning_evidence_snapshots (
                    evidence_snapshot_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    root_event_id TEXT NOT NULL,
                    source_event_id TEXT NOT NULL,
                    evidence_kind TEXT NOT NULL,
                    evidence_theme TEXT NOT NULL,
                    feedback_candidate_kind TEXT NOT NULL,
                    feedback_candidate_scope TEXT NOT NULL,
                    canonical_payload_json TEXT NOT NULL,
                    canonical_payload_sha256 TEXT NOT NULL,
                    evidence_identity_sha256 TEXT NOT NULL,
                    source_record_refs_json TEXT NOT NULL,
                    source_trace_refs_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    immutable_snapshot INTEGER NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    UNIQUE(session_id, evidence_identity_sha256)
                );
                CREATE TABLE IF NOT EXISTS teacher_decision_target_bindings (
                    binding_id TEXT PRIMARY KEY,
                    teacher_decision_id TEXT UNIQUE NOT NULL,
                    pending_teacher_review_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    evidence_snapshot_id TEXT NOT NULL,
                    evidence_identity_sha256 TEXT NOT NULL,
                    canonical_payload_sha256 TEXT NOT NULL,
                    review_nonce TEXT NOT NULL,
                    checkpoint_id TEXT NOT NULL,
                    checkpoint_version INTEGER NOT NULL,
                    approval_scope TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS learning_pipeline_identity_bindings (
                    binding_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    evidence_snapshot_id TEXT NOT NULL,
                    evidence_identity_sha256 TEXT NOT NULL,
                    pipeline_stage TEXT NOT NULL,
                    target_record_kind TEXT NOT NULL,
                    target_record_id TEXT NOT NULL,
                    source_binding_id TEXT,
                    validator_passed INTEGER NOT NULL,
                    source_trace_refs_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    UNIQUE(pipeline_stage, target_record_id)
                );
                CREATE TABLE IF NOT EXISTS interpretation_provenance_bindings (
                    provenance_binding_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    interpretation_commit_id TEXT NOT NULL,
                    evidence_snapshot_id TEXT NOT NULL,
                    evidence_identity_sha256 TEXT NOT NULL,
                    pipeline_binding_ids_json TEXT NOT NULL,
                    identity_chain_complete INTEGER NOT NULL,
                    identity_chain_valid INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS runtime_capability_profiles (
                    profile_id TEXT PRIMARY KEY,
                    profile_version TEXT NOT NULL,
                    profile_json TEXT NOT NULL,
                    profile_sha256 TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            self._ensure_column(connection, "pending_teacher_reviews", "evidence_snapshot_id", "TEXT")
            self._ensure_column(connection, "pending_teacher_reviews", "evidence_identity_sha256", "TEXT")
            self._ensure_column(connection, "pending_teacher_reviews", "canonical_payload_sha256", "TEXT")
            self._ensure_column(connection, "pending_teacher_reviews", "target_session_checkpoint_id", "TEXT")
            self._ensure_column(connection, "pending_teacher_reviews", "target_checkpoint_version", "INTEGER")
            self._ensure_column(connection, "pending_teacher_reviews", "review_nonce", "TEXT")
            self._ensure_column(connection, "pending_teacher_reviews", "allowed_approval_scopes_json", "TEXT")
            self._ensure_column(connection, "pending_teacher_reviews", "required_commit_scope", "TEXT")
            self._ensure_column(connection, "teacher_decisions", "approval_scope", "TEXT")
            self._ensure_column(connection, "teacher_decisions", "target_evidence_snapshot_id", "TEXT")
            self._ensure_column(connection, "teacher_decisions", "target_evidence_identity_sha256", "TEXT")
            self._ensure_column(connection, "teacher_decisions", "target_canonical_payload_sha256", "TEXT")
            self._ensure_column(connection, "teacher_decisions", "target_review_nonce", "TEXT")
            self._ensure_column(connection, "teacher_decisions", "target_checkpoint_id", "TEXT")
            self._ensure_column(connection, "teacher_decisions", "target_checkpoint_version", "INTEGER")
            self._ensure_column(connection, "teacher_decisions", "explicit_target_binding", "INTEGER DEFAULT 0")
            self._ensure_column(connection, "teacher_decisions", "scope_sufficient_for_requested_operation", "INTEGER DEFAULT 0")
            self._ensure_column(connection, "reviewed_interpretation_commits", "source_evidence_snapshot_id", "TEXT")
            self._ensure_column(connection, "reviewed_interpretation_commits", "evidence_identity_sha256", "TEXT")
            self._ensure_column(connection, "reviewed_interpretation_commits", "teacher_approval_scope", "TEXT")
            self._ensure_column(connection, "reviewed_interpretation_commits", "pipeline_identity_binding_ids_json", "TEXT")
            self._ensure_column(connection, "reviewed_interpretation_commits", "identity_chain_complete", "INTEGER DEFAULT 0")
            self._ensure_column(connection, "reviewed_interpretation_commits", "identity_chain_valid", "INTEGER DEFAULT 0")
            self._ensure_column(connection, "working_readback_commits", "source_evidence_snapshot_id", "TEXT")
            self._ensure_column(connection, "working_readback_commits", "evidence_identity_sha256", "TEXT")
            self._ensure_column(connection, "working_readback_commits", "source_reviewed_interpretation_commit_id", "TEXT")
            connection.execute(
                """
                INSERT OR IGNORE INTO store_metadata (schema_name, schema_version, created_at)
                VALUES (?, ?, ?)
                """,
                (STORE_SCHEMA_NAME, STORE_SCHEMA_VERSION, _now()),
            )
            connection.execute(
                "UPDATE store_metadata SET schema_version = ? WHERE schema_name = ?",
                (STORE_SCHEMA_VERSION, STORE_SCHEMA_NAME),
            )
            if existing_version == LEGACY_STORE_SCHEMA_VERSION:
                connection.commit()

    def _existing_schema_version(self) -> str | None:
        if not self.db_path.exists():
            return None
        connection = sqlite3.connect(str(self.db_path))
        try:
            table = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='store_metadata'"
            ).fetchone()
            if table is None:
                return None
            row = connection.execute(
                "SELECT schema_version FROM store_metadata WHERE schema_name = ?",
                (STORE_SCHEMA_NAME,),
            ).fetchone()
            return None if row is None else str(row[0])
        finally:
            connection.close()

    def _ensure_column(
        self,
        connection: sqlite3.Connection,
        table_name: str,
        column_name: str,
        column_spec: str,
    ) -> None:
        existing = {
            str(row["name"])
            for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        }
        if column_name not in existing:
            connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_spec}")

    def _insert_trace(self, connection: sqlite3.Connection, envelope: TraceEnvelope) -> TraceEnvelope:
        duplicate = connection.execute(
            "SELECT * FROM trace_envelopes WHERE trace_id = ?",
            (envelope.trace_id,),
        ).fetchone()
        if duplicate is not None:
            existing = self._trace_from_row(duplicate)
            if trace_identity_matches(existing, envelope):
                return existing
            raise TraceIdentityCollisionError(
                f"blocked_trace_identity_collision: {envelope.trace_id}"
            )
        existing_rows = connection.execute(
            "SELECT trace_id, session_id, sequence_index, monotonic_tick "
            "FROM trace_envelopes WHERE session_id = ? ORDER BY sequence_index",
            (envelope.session_id,),
        ).fetchall()
        existing_ids = {row["trace_id"] for row in existing_rows}
        for ref in envelope.source_trace_refs:
            row = connection.execute(
                "SELECT session_id FROM trace_envelopes WHERE trace_id = ?",
                (ref,),
            ).fetchone()
            if row is None or ref not in existing_ids:
                raise ValueError(f"missing or future source_trace_ref: {ref}")
            if row["session_id"] != envelope.session_id:
                raise ValueError(f"cross-session source_trace_ref: {ref}")
        next_sequence = len(existing_rows)
        latest_tick = max((int(row["monotonic_tick"]) for row in existing_rows), default=-1)
        stored = TraceEnvelope(
            **{
                **envelope.to_dict(),
                "sequence_index": next_sequence,
                "monotonic_tick": max(next_sequence, latest_tick + 1),
            }
        )
        payload = stored.to_dict()
        connection.execute(
            """
            INSERT INTO trace_envelopes (
                trace_id, trace_schema_version, session_id, event_id, parent_event_id,
                root_event_id, sequence_index, monotonic_tick, nesting_depth,
                source_line, source_module, record_kind, record_id, trace_layer,
                payload_schema, payload_snapshot_json, source_trace_refs_json,
                source_record_refs_json, created_at, append_only, time_aligned,
                payload_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                stored.trace_id,
                stored.trace_schema_version,
                stored.session_id,
                stored.event_id,
                stored.parent_event_id,
                stored.root_event_id,
                stored.sequence_index,
                stored.monotonic_tick,
                stored.nesting_depth,
                stored.source_line,
                stored.source_module,
                stored.record_kind,
                stored.record_id,
                stored.trace_layer,
                stored.payload_schema,
                canonical_json(stored.payload_snapshot),
                canonical_json(stored.source_trace_refs),
                canonical_json(stored.source_record_refs),
                stored.created_at,
                1 if stored.append_only else 0,
                1 if stored.time_aligned else 0,
                payload_sha256(payload),
            ),
        )
        return stored

    def _append_checkpoint(
        self,
        connection: sqlite3.Connection,
        *,
        checkpoint_id: str,
        state: BoundedEmbodiedSessionState,
        runtime_records: dict[str, Any],
    ) -> None:
        version = self._next_checkpoint_version(connection, state.session_id)
        payload = {
            "checkpoint_id": checkpoint_id,
            "session_id": state.session_id,
            "checkpoint_version": version,
            "session_status": str(state.status.value if hasattr(state.status, "value") else state.status),
            "session_state": state.to_dict(),
            "event_stack": state.event_stack_frame_ids,
            "working_readback_snapshot": state.working_readback_snapshot_refs,
            "pending_review_refs": state.pending_teacher_review_ids,
            "trace_cursor": state.raw_trace_cursor,
            "runtime_records": runtime_records,
        }
        connection.execute(
            """
            INSERT INTO session_checkpoints (
                checkpoint_id, session_id, checkpoint_version, session_status,
                session_state_json, event_stack_json, working_readback_snapshot_json,
                pending_review_refs_json, trace_cursor, runtime_records_json,
                created_at, payload_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                checkpoint_id,
                state.session_id,
                version,
                payload["session_status"],
                canonical_json(payload["session_state"]),
                canonical_json(payload["event_stack"]),
                canonical_json(payload["working_readback_snapshot"]),
                canonical_json(payload["pending_review_refs"]),
                int(state.raw_trace_cursor),
                canonical_json(runtime_records),
                _now(),
                payload_sha256(payload),
            ),
        )

    def _append_journal(
        self,
        connection: sqlite3.Connection,
        *,
        session_id: str,
        journal_kind: str,
        payload: dict[str, Any],
    ) -> str:
        if journal_kind not in ALLOWED_JOURNAL_KINDS:
            raise ValueError(f"unknown journal_kind: {journal_kind}")
        sequence = self._next_journal_sequence(connection, session_id)
        journal_id = f"session_journal:{session_id}:{sequence}:{journal_kind}:{uuid4().hex[:8]}"
        connection.execute(
            """
            INSERT INTO session_journal (
                journal_id, session_id, sequence_index, journal_kind,
                payload_json, created_at, payload_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                journal_id,
                session_id,
                sequence,
                journal_kind,
                canonical_json(payload),
                _now(),
                payload_sha256(payload),
            ),
        )
        return journal_id

    def _insert_evidence_snapshot(
        self,
        connection: sqlite3.Connection,
        snapshot: SessionLearningEvidenceSnapshot | dict[str, Any],
    ) -> None:
        item = snapshot if isinstance(snapshot, SessionLearningEvidenceSnapshot) else SessionLearningEvidenceSnapshot.from_dict(dict(snapshot))
        validation = validate_session_learning_evidence_snapshot(item)
        if not validation["valid"]:
            raise ValueError(f"invalid evidence snapshot: {validation['reasons']}")
        payload = item.to_dict()
        connection.execute(
            """
            INSERT OR IGNORE INTO learning_evidence_snapshots (
                evidence_snapshot_id, session_id, root_event_id, source_event_id,
                evidence_kind, evidence_theme, feedback_candidate_kind,
                feedback_candidate_scope, canonical_payload_json,
                canonical_payload_sha256, evidence_identity_sha256,
                source_record_refs_json, source_trace_refs_json, created_at,
                immutable_snapshot, payload_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.evidence_snapshot_id,
                item.session_id,
                item.root_event_id,
                item.source_event_id,
                item.evidence_kind,
                item.evidence_theme,
                item.feedback_candidate_kind,
                item.feedback_candidate_scope,
                canonical_json(item.canonical_evidence_payload),
                item.canonical_payload_sha256,
                item.evidence_identity_sha256,
                canonical_json(item.source_record_refs),
                canonical_json(item.source_trace_refs),
                item.created_at,
                1 if item.immutable_snapshot else 0,
                payload_sha256(payload),
            ),
        )

    def _insert_runtime_capability_profile(
        self,
        connection: sqlite3.Connection,
        profile: Any,
    ) -> None:
        data = profile.to_dict() if hasattr(profile, "to_dict") else dict(profile)
        connection.execute(
            """
            INSERT OR IGNORE INTO runtime_capability_profiles (
                profile_id, profile_version, profile_json, profile_sha256, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                data["profile_id"],
                data["profile_version"],
                canonical_json(data),
                data["profile_sha256"],
                data["created_at"],
            ),
        )

    def _insert_pipeline_identity_bindings(
        self,
        connection: sqlite3.Connection,
        bindings: tuple[dict[str, Any], ...] | list[dict[str, Any]],
    ) -> None:
        for raw_binding in bindings:
            binding = raw_binding.to_dict() if hasattr(raw_binding, "to_dict") else dict(raw_binding)
            connection.execute(
                """
                INSERT OR IGNORE INTO learning_pipeline_identity_bindings (
                    binding_id, session_id, evidence_snapshot_id,
                    evidence_identity_sha256, pipeline_stage, target_record_kind,
                    target_record_id, source_binding_id, validator_passed,
                    source_trace_refs_json, created_at, payload_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    binding["binding_id"],
                    binding["session_id"],
                    binding["evidence_snapshot_id"],
                    binding["evidence_identity_sha256"],
                    binding["pipeline_stage"],
                    binding["target_record_kind"],
                    binding["target_record_id"],
                    binding.get("source_binding_id"),
                    1 if binding["validator_passed"] else 0,
                    canonical_json(binding["source_trace_refs"]),
                    binding["created_at"],
                    payload_sha256(binding),
                ),
            )

    def _insert_interpretation_provenance_binding(
        self,
        connection: sqlite3.Connection,
        binding: dict[str, Any],
    ) -> None:
        commit_id = binding.get("interpretation_commit_id") or binding.get("reviewed_interpretation_commit_id")
        pipeline_binding_ids = binding.get("pipeline_binding_ids") or binding.get("pipeline_identity_binding_ids") or tuple()
        identity_chain_complete = bool(binding.get("identity_chain_complete", binding.get("identity_chain_valid", False)))
        connection.execute(
            """
            INSERT INTO interpretation_provenance_bindings (
                provenance_binding_id, session_id, interpretation_commit_id,
                evidence_snapshot_id, evidence_identity_sha256,
                pipeline_binding_ids_json, identity_chain_complete,
                identity_chain_valid, created_at, payload_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                binding["provenance_binding_id"],
                binding["session_id"],
                commit_id,
                binding["evidence_snapshot_id"],
                binding["evidence_identity_sha256"],
                canonical_json(pipeline_binding_ids),
                1 if identity_chain_complete else 0,
                1 if binding["identity_chain_valid"] else 0,
                binding["created_at"],
                payload_sha256(binding),
            ),
        )

    def _insert_pending_review(
        self,
        connection: sqlite3.Connection,
        review: PendingTeacherReviewRecord,
        *,
        checkpoint_id: str | None = None,
        checkpoint_version: int | None = None,
    ) -> None:
        status = "session_aborted" if review.session_aborted else "pending"
        if status not in ALLOWED_REVIEW_STATUSES:
            raise ValueError(f"invalid review status: {status}")
        target_checkpoint_id = review.target_session_checkpoint_id or checkpoint_id
        target_version = review.target_checkpoint_version if review.target_checkpoint_version is not None else checkpoint_version
        connection.execute(
            """
            INSERT OR IGNORE INTO pending_teacher_reviews (
                pending_teacher_review_id, session_id,
                source_learning_feedback_candidate_ref,
                source_learning_evidence_packet_ref, source_trace_refs_json,
                review_kind, current_review_status, resolved, created_at, updated_at,
                evidence_snapshot_id, evidence_identity_sha256,
                canonical_payload_sha256, target_session_checkpoint_id,
                target_checkpoint_version, review_nonce,
                allowed_approval_scopes_json, required_commit_scope
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                review.pending_teacher_review_id,
                review.session_id,
                review.source_learning_feedback_candidate_ref,
                review.source_learning_evidence_packet_ref,
                canonical_json(review.source_trace_refs),
                review.review_kind,
                status,
                1 if review.resolved else 0,
                review.created_at,
                _now(),
                review.evidence_snapshot_id,
                review.evidence_identity_sha256,
                review.canonical_payload_sha256,
                target_checkpoint_id,
                target_version,
                review.review_nonce,
                canonical_json(review.allowed_approval_scopes),
                review.required_commit_scope,
            ),
        )

    def _update_pending_review_status(
        self,
        connection: sqlite3.Connection,
        pending_teacher_review_id: str,
        status: str,
    ) -> None:
        if status not in ALLOWED_REVIEW_STATUSES:
            raise ValueError(f"invalid review status: {status}")
        resolved = status in {"approved", "rejected", "session_aborted"}
        connection.execute(
            """
            UPDATE pending_teacher_reviews
            SET current_review_status = ?, resolved = ?, updated_at = ?
            WHERE pending_teacher_review_id = ?
            """,
            (status, 1 if resolved else 0, _now(), pending_teacher_review_id),
        )

    def _upsert_session_head(
        self,
        connection: sqlite3.Connection,
        *,
        session_id: str,
        status: str,
        checkpoint_id: str,
        expected_version: int | None,
    ) -> None:
        row = connection.execute(
            "SELECT version FROM session_heads WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            if expected_version not in (None, 0):
                raise RuntimeError("stale session head writer")
            connection.execute(
                """
                INSERT INTO session_heads (
                    session_id, current_status, current_checkpoint_id, version, updated_at
                ) VALUES (?, ?, ?, 1, ?)
                """,
                (session_id, status, checkpoint_id, _now()),
            )
            return
        current_version = int(row["version"])
        if expected_version is not None and expected_version != current_version:
            raise RuntimeError("stale session head writer")
        connection.execute(
            """
            UPDATE session_heads
            SET current_status = ?, current_checkpoint_id = ?, version = ?, updated_at = ?
            WHERE session_id = ?
            """,
            (status, checkpoint_id, current_version + 1, _now(), session_id),
        )

    def _insert_interpretation_commit(
        self,
        connection: sqlite3.Connection,
        commit: dict[str, Any],
    ) -> None:
        if commit["commit_status"] not in {"active", "deprecated", "superseded"}:
            raise ValueError("invalid interpretation commit_status")
        connection.execute(
            """
            INSERT INTO reviewed_interpretation_commits (
                interpretation_commit_id, session_id, teacher_decision_id,
                reviewed_concept_ref, memory_learning_trace_ref,
                memory_routing_trace_ref, memory_application_data_ref,
                interpretation_payload_json, source_trace_refs_json, commit_status,
                created_at, payload_sha256, source_evidence_snapshot_id,
                evidence_identity_sha256, teacher_approval_scope,
                pipeline_identity_binding_ids_json, identity_chain_complete,
                identity_chain_valid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                commit["reviewed_interpretation_commit_id"],
                commit["session_id"],
                commit["teacher_decision_id"],
                commit["source_reviewed_concept_ref"],
                commit["memory_learning_trace_ref"],
                commit["memory_routing_trace_ref"],
                commit["memory_application_data_ref"],
                canonical_json(commit["interpretation_payload"]),
                canonical_json(commit["source_trace_refs"]),
                commit["commit_status"],
                commit["created_at"],
                payload_sha256(commit),
                commit["source_evidence_snapshot_id"],
                commit["evidence_identity_sha256"],
                commit["teacher_approval_scope"],
                canonical_json(commit["pipeline_identity_binding_ids"]),
                1 if commit["identity_chain_complete"] else 0,
                1 if commit["identity_chain_valid"] else 0,
            ),
        )

    def _insert_working_readback_commit(
        self,
        connection: sqlite3.Connection,
        commit: dict[str, Any],
    ) -> None:
        connection.execute(
            """
            INSERT INTO working_readback_commits (
                working_readback_commit_id, session_id, interpretation_commit_id,
                readback_payload_json, source_trace_refs_json,
                active_for_future_sessions, created_at, payload_sha256,
                source_evidence_snapshot_id, evidence_identity_sha256,
                source_reviewed_interpretation_commit_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                commit["working_readback_commit_id"],
                commit["session_id"],
                commit["interpretation_commit_id"],
                canonical_json(commit["readback_payload"]),
                canonical_json(commit["source_trace_refs"]),
                1 if commit["active_for_future_sessions"] else 0,
                commit["created_at"],
                payload_sha256(commit),
                commit["source_evidence_snapshot_id"],
                commit["evidence_identity_sha256"],
                commit["source_reviewed_interpretation_commit_id"],
            ),
        )

    def _next_checkpoint_version(self, connection: sqlite3.Connection, session_id: str) -> int:
        row = connection.execute(
            "SELECT COALESCE(MAX(checkpoint_version), 0) AS version "
            "FROM session_checkpoints WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return int(row["version"]) + 1

    def _next_journal_sequence(self, connection: sqlite3.Connection, session_id: str) -> int:
        row = connection.execute(
            "SELECT COALESCE(MAX(sequence_index), -1) AS sequence "
            "FROM session_journal WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return int(row["sequence"]) + 1

    def _latest_checkpoint_id(self, connection: sqlite3.Connection, session_id: str) -> str:
        row = connection.execute(
            "SELECT checkpoint_id FROM session_checkpoints WHERE session_id = ? "
            "ORDER BY checkpoint_version DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"checkpoint not found: {session_id}")
        return str(row["checkpoint_id"])

    def _checkpoint_version(self, connection: sqlite3.Connection, checkpoint_id: str) -> int:
        row = connection.execute(
            "SELECT checkpoint_version FROM session_checkpoints WHERE checkpoint_id = ?",
            (checkpoint_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"checkpoint not found: {checkpoint_id}")
        return int(row["checkpoint_version"])

    def _checkpoint_version_by_id(self, checkpoint_id: str) -> int:
        with self.connection() as connection:
            return self._checkpoint_version(connection, checkpoint_id)

    def _checkpoint_id(self, session_id: str) -> str:
        return f"session_checkpoint:{session_id}:{uuid4().hex[:12]}"

    def _trace_from_row(self, row: sqlite3.Row) -> TraceEnvelope:
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
            payload_snapshot=dict(_json_loads(row["payload_snapshot_json"], {})),
            source_trace_refs=tuple(_json_loads(row["source_trace_refs_json"], [])),
            source_record_refs=tuple(_json_loads(row["source_record_refs_json"], [])),
            created_at=row["created_at"],
            append_only=bool(row["append_only"]),
            time_aligned=bool(row["time_aligned"]),
        )

    def _pending_review_from_row(self, row: sqlite3.Row) -> PendingTeacherReviewRecord:
        data = dict(row)
        status = str(row["current_review_status"])
        return PendingTeacherReviewRecord(
            pending_teacher_review_id=row["pending_teacher_review_id"],
            schema_version="ashl_pending_teacher_review_v0",
            created_at=row["created_at"],
            session_id=row["session_id"],
            source_learning_feedback_candidate_ref=row["source_learning_feedback_candidate_ref"],
            source_learning_evidence_packet_ref=row["source_learning_evidence_packet_ref"],
            source_trace_refs=tuple(_json_loads(row["source_trace_refs_json"], [])),
            review_kind=row["review_kind"],
            review_status="pending_teacher_review" if status == "pending" else status,
            review_summary="Persisted Package 116 teacher review state.",
            allowed_review_results=tuple(sorted(ALLOWED_DECISIONS)),
            teacher_decision=None if status == "pending" else status,
            teacher_reason_codes=tuple(),
            resolved=bool(row["resolved"]),
            session_aborted=status == "session_aborted",
            evidence_snapshot_id=str(data.get("evidence_snapshot_id") or ""),
            evidence_identity_sha256=str(data.get("evidence_identity_sha256") or ""),
            canonical_payload_sha256=str(data.get("canonical_payload_sha256") or ""),
            target_session_checkpoint_id=data.get("target_session_checkpoint_id"),
            target_checkpoint_version=data.get("target_checkpoint_version"),
            review_nonce=str(data.get("review_nonce") or ""),
            allowed_approval_scopes=tuple(
                _json_loads(data.get("allowed_approval_scopes_json"), list(ALLOWED_APPROVAL_SCOPES))
            ),
            required_commit_scope=str(data.get("required_commit_scope") or FULL_COMMIT_APPROVAL_SCOPE),
        )
