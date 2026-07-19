"""Append-only local operator console store for Package 122B."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import canonical_json, sha256_payload, utc_now
from ashl_core_v1.runtime.operator_console_types import (
    CANCELLATION_SCHEMA_VERSION,
    DISPATCH_RESULT_SCHEMA_VERSION,
    JSON_EVENT_SCHEMA_VERSION,
    OUTPUT_VOLUME_SCHEMA_VERSION,
    RATE_LIMIT_POLICY_SCHEMA_VERSION,
    RAW_OUTPUT_SEQUENCE_SCHEMA_VERSION,
    STATUS_LOG_SCHEMA_VERSION,
    TEXT_INPUT_SCHEMA_VERSION,
    TEXT_TIMELINE_SCHEMA_VERSION,
    LocalOperatorJsonEvent,
    LocalOutputVolumeState,
    OperatorStatusLogEntry,
    OutputCancellationRecord,
    OutputDispatchResultRecord,
    OutputRateLimitPolicy,
    RawOutputSequence,
    TextTimelineEntry,
)


LOCAL_OPERATOR_CONSOLE_DIRNAME = "local_operator_console_v0"
LOCAL_OPERATOR_CONSOLE_FILENAME = "operator_console.sqlite3"


class LocalOperatorConsoleStore:
    def __init__(self, state_dir: str | Path) -> None:
        if state_dir is None:
            raise ValueError("explicit state_dir is required")
        self.state_dir = Path(state_dir)
        self.root_dir = self.state_dir / LOCAL_OPERATOR_CONSOLE_DIRNAME
        self.db_path = self.root_dir / LOCAL_OPERATOR_CONSOLE_FILENAME
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

    def list_payloads(self, table: str, order_by: str = "created_at") -> tuple[dict[str, Any], ...]:
        with self.connection() as connection:
            rows = connection.execute(f"SELECT payload_json FROM {table} ORDER BY {order_by}").fetchall()
        return tuple(json.loads(str(row["payload_json"])) for row in rows)

    def get_payload(self, table: str, id_column: str, record_id: str) -> dict[str, Any]:
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} WHERE {id_column} = ?",
                (record_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"missing {table} row: {record_id}")
        return json.loads(str(row["payload_json"]))

    def set_hardware_preference(self, *, device_kind: str, enabled: bool, preferred_device_id: str | None = None) -> dict[str, Any]:
        if device_kind not in {"camera", "microphone"}:
            raise ValueError("device_kind must be camera or microphone")
        payload = {
            "preference_id": f"hardware_preference:{device_kind}:{utc_now()}",
            "schema_version": "ashl_hardware_enable_preference_v0",
            "created_at": utc_now(),
            "device_kind": device_kind,
            "enabled_preference": bool(enabled),
            "preferred_device_id": preferred_device_id,
            "device_opened": False,
            "source": "local_operator_console",
        }
        self.append_payload("hardware_enable_preferences", "preference_id", payload["preference_id"], payload)
        return payload

    def latest_hardware_preference(self, device_kind: str) -> dict[str, Any] | None:
        rows = [
            item
            for item in self.list_payloads("hardware_enable_preferences")
            if item.get("device_kind") == device_kind
        ]
        return rows[-1] if rows else None

    def append_output_volume_state(self, state: LocalOutputVolumeState) -> None:
        self.append_payload("output_volume_states", "volume_state_id", state.volume_state_id, state.to_dict())

    def latest_output_volume_state(self) -> dict[str, Any] | None:
        rows = self.list_payloads("output_volume_states")
        return rows[-1] if rows else None

    def append_external_text_input(self, record: Any) -> None:
        self.append_payload("external_text_inputs", "text_input_id", record.text_input_id, record.to_dict())

    def append_text_timeline_entry(self, entry: TextTimelineEntry) -> None:
        self.append_payload("text_timeline_entries", "timeline_entry_id", entry.timeline_entry_id, entry.to_dict())

    def append_raw_output_sequence(self, sequence: RawOutputSequence) -> None:
        self.append_payload("raw_output_sequences", "raw_output_sequence_id", sequence.raw_output_sequence_id, sequence.to_dict())

    def append_output_intent(self, intent: Any) -> None:
        self.append_payload("output_intents", "output_intent_id", intent.output_intent_id, intent.to_dict())

    def append_dispatch_result(self, result: OutputDispatchResultRecord) -> None:
        self.append_payload("output_dispatch_results", "dispatch_result_id", result.dispatch_result_id, result.to_dict())

    def append_cancellation(self, cancellation: OutputCancellationRecord) -> None:
        self.append_payload("output_cancellations", "cancellation_id", cancellation.cancellation_id, cancellation.to_dict())

    def append_status_log(self, entry: OperatorStatusLogEntry) -> None:
        self.append_payload("status_log_entries", "status_log_id", entry.status_log_id, entry.to_dict())

    def append_json_event(self, event: LocalOperatorJsonEvent) -> None:
        payload = event.to_dict()
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO operator_json_events
                    (event_id, sequence_index, created_at, payload_json, payload_sha256)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.sequence_index,
                    event.created_at,
                    canonical_json(payload),
                    sha256_payload(payload),
                ),
            )

    def append_rate_limit_policy(self, policy: OutputRateLimitPolicy) -> None:
        self.append_payload("output_rate_limit_policies", "policy_id", policy.policy_id, policy.to_dict())

    def latest_rate_limit_policy(self) -> dict[str, Any] | None:
        rows = self.list_payloads("output_rate_limit_policies")
        return rows[-1] if rows else None

    def has_dispatch_for_intent(self, output_intent_id: str) -> bool:
        return any(item.get("output_intent_id") == output_intent_id for item in self.list_payloads("output_dispatch_results"))

    def has_successful_cancellation_for_intent(self, output_intent_id: str) -> bool:
        return any(
            item.get("target_output_intent_id") == output_intent_id and item.get("cancellation_succeeded")
            for item in self.list_payloads("output_cancellations")
        )

    def pending_output_count(self) -> int:
        intents = self.list_payloads("output_intents")
        dispatched = {item.get("output_intent_id") for item in self.list_payloads("output_dispatch_results")}
        cancelled = {
            item.get("target_output_intent_id")
            for item in self.list_payloads("output_cancellations")
            if item.get("cancellation_succeeded")
        }
        return sum(1 for item in intents if item.get("output_intent_id") not in dispatched | cancelled)

    def next_event_sequence_index(self) -> int:
        with self.connection() as connection:
            row = connection.execute("SELECT COALESCE(MAX(sequence_index), -1) + 1 AS next_index FROM operator_json_events").fetchone()
        return int(row["next_index"])

    def latest_successful_dispatch_created_at(self) -> str | None:
        rows = [
            item
            for item in self.list_payloads("output_dispatch_results")
            if item.get("dispatch_status") == "dispatched"
        ]
        return str(rows[-1]["created_at"]) if rows else None

    def latest_successful_dispatch_age_ms(self) -> int | None:
        created_at = self.latest_successful_dispatch_created_at()
        if created_at is None:
            return None
        then = datetime.fromisoformat(created_at)
        now = datetime.now(timezone.utc)
        return int((now - then).total_seconds() * 1000)

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS operator_console_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS hardware_enable_preferences (
                    preference_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS output_volume_states (
                    volume_state_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS external_text_inputs (
                    text_input_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS text_timeline_entries (
                    timeline_entry_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS raw_output_sequences (
                    raw_output_sequence_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS output_intents (
                    output_intent_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS output_dispatch_results (
                    dispatch_result_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS output_cancellations (
                    cancellation_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS status_log_entries (
                    status_log_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS operator_json_events (
                    event_id TEXT PRIMARY KEY,
                    sequence_index INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS output_rate_limit_policies (
                    policy_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                """
            )


def build_default_console_store(state_dir: str | Path) -> LocalOperatorConsoleStore:
    store = LocalOperatorConsoleStore(state_dir)
    if store.latest_output_volume_state() is None:
        from ashl_core_v1.runtime.operator_console_types import build_default_output_volume_state

        store.append_output_volume_state(build_default_output_volume_state())
    if store.latest_rate_limit_policy() is None:
        store.append_rate_limit_policy(
            OutputRateLimitPolicy(
                policy_id="output_rate_limit_policy:default",
                schema_version=RATE_LIMIT_POLICY_SCHEMA_VERSION,
                minimum_interval_ms=2000,
                maximum_queue_depth=8,
                overflow_policy="reject_new_with_log",
            )
        )
    return store
