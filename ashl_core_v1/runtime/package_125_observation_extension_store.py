"""Append-only SQLite store for Package 125 observation-extension records."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import canonical_json, plain, sha256_payload


PACKAGE_125_STORE_DIRNAME = "package_125_observation_extension_v0"
PACKAGE_125_STORE_FILENAME = "package_125.sqlite3"


TABLE_ID_COLUMNS = {
    "observation_window_authorizations": "authorization_id",
    "observation_window_states": "observation_window_state_id",
    "active_capture_session_identities": "active_capture_identity_id",
    "temporal_tail_evidence": "temporal_tail_evidence_id",
    "open_temporal_region_observations": "open_region_observation_id",
    "temporal_region_closure_links": "closure_link_id",
    "observation_extension_candidates": "extension_candidate_id",
    "observation_extension_policy_decisions": "extension_policy_decision_id",
    "observation_extension_internal_actions": "internal_action_id",
    "observation_extension_executions": "extension_execution_id",
    "observation_extension_cancellations": "cancellation_id",
    "observation_extension_outcomes": "extension_outcome_id",
    "observation_extension_comparisons": "comparison_id",
    "operator_event_delivery_failures": "event_delivery_failure_id",
    "package_112_score_equivalence_records": "score_equivalence_record_id",
    "package_125_stimulus_audit_manifests": "stimulus_audit_manifest_id",
    "package_125_audits": "audit_id",
}


class Package125ObservationExtensionStore:
    def __init__(self, state_dir: str | Path) -> None:
        if state_dir is None:
            raise ValueError("explicit state_dir is required")
        self.state_dir = Path(state_dir)
        self.root_dir = self.state_dir / PACKAGE_125_STORE_DIRNAME
        self.db_path = self.root_dir / PACKAGE_125_STORE_FILENAME
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

    def append_record(self, table: str, record: Any) -> None:
        if not hasattr(record, "to_dict"):
            raise TypeError("append_record requires a dataclass record with to_dict")
        self.append_payload(table, record.to_dict())

    def append_payload(self, table: str, payload: dict[str, Any]) -> None:
        id_column = self._id_column(table)
        record_id = str(payload[id_column])
        created_at = str(payload.get("created_at", ""))
        payload_json = canonical_json(plain(payload))
        with self.connection() as connection:
            connection.execute(
                f"""
                INSERT INTO {table} ({id_column}, created_at, payload_json, payload_sha256)
                VALUES (?, ?, ?, ?)
                """,
                (record_id, created_at, payload_json, sha256_payload(payload)),
            )

    def get_payload(self, table: str, record_id: str) -> dict[str, Any]:
        id_column = self._id_column(table)
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} WHERE {id_column} = ?",
                (record_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"record not found in {table}: {record_id}")
        return json.loads(row["payload_json"])

    def list_payloads(self, table: str) -> tuple[dict[str, Any], ...]:
        self._id_column(table)
        with self.connection() as connection:
            rows = connection.execute(
                f"SELECT payload_json FROM {table} ORDER BY rowid ASC"
            ).fetchall()
        return tuple(json.loads(row["payload_json"]) for row in rows)

    def list_payloads_matching(self, table: str, **matches: object) -> tuple[dict[str, Any], ...]:
        return tuple(
            payload
            for payload in self.list_payloads(table)
            if all(payload.get(key) == value for key, value in matches.items())
        )

    def latest_payload(self, table: str) -> dict[str, Any] | None:
        self._id_column(table)
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
        return json.loads(row["payload_json"]) if row else None

    def counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        with self.connection() as connection:
            for table in TABLE_ID_COLUMNS:
                row = connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
                counts[table] = int(row["count"])
        return counts

    def validate_schema(self) -> dict[str, Any]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
            ).fetchall()
        names = tuple(row["name"] for row in rows)
        missing = tuple(sorted(set(TABLE_ID_COLUMNS) - set(names)))
        return {"valid": not missing, "tables": names, "missing_tables": missing}

    def _initialize(self) -> None:
        with self.connection() as connection:
            self._migrate_observation_window_state_key(connection)
            for table, id_column in TABLE_ID_COLUMNS.items():
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                        {id_column} TEXT PRIMARY KEY,
                        created_at TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        payload_sha256 TEXT NOT NULL
                    )
                    """
                )

    @staticmethod
    def _migrate_observation_window_state_key(connection: sqlite3.Connection) -> None:
        existing = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'observation_window_states'"
        ).fetchone()
        if existing is None:
            return
        columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(observation_window_states)").fetchall()
        }
        if "observation_window_state_id" in columns:
            return
        connection.execute("ALTER TABLE observation_window_states RENAME TO observation_window_states_legacy_v0")
        connection.execute(
            """
            CREATE TABLE observation_window_states (
                observation_window_state_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL
            )
            """
        )
        rows = connection.execute(
            """
            SELECT observation_window_id, created_at, payload_json, payload_sha256
            FROM observation_window_states_legacy_v0
            ORDER BY rowid ASC
            """
        ).fetchall()
        for row in rows:
            connection.execute(
                """
                INSERT INTO observation_window_states (
                    observation_window_state_id, created_at, payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    f"legacy_observation_window_state:{row['observation_window_id']}",
                    row["created_at"],
                    row["payload_json"],
                    row["payload_sha256"],
                ),
            )

    def _id_column(self, table: str) -> str:
        try:
            return TABLE_ID_COLUMNS[table]
        except KeyError as exc:
            raise ValueError(f"unknown Package 125 table: {table}") from exc


def build_package_125_store(state_dir: str | Path) -> Package125ObservationExtensionStore:
    return Package125ObservationExtensionStore(state_dir)
