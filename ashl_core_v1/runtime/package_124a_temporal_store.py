"""Append-only Package 124A temporal primitive store."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import canonical_json, sha256_payload, utc_now
from ashl_core_v1.runtime.temporal_types import TEMPORAL_STORE_SCHEMA_NAME, TEMPORAL_STORE_SCHEMA_VERSION


PACKAGE_124A_TEMPORAL_DIRNAME = "package_124a_temporal_foundation_v0"
PACKAGE_124A_TEMPORAL_FILENAME = "package_124a_temporal.sqlite3"


TABLE_KEY_FIELDS = {
    "temporal_clock_domains": "clock_domain_id",
    "temporal_clock_quality": "clock_quality_id",
    "temporal_event_anchors": "temporal_anchor_id",
    "temporal_span_primitives": "temporal_span_id",
    "temporal_interval_primitives": "temporal_interval_id",
    "temporal_relation_primitives": "temporal_relation_id",
    "temporal_continuity_primitives": "temporal_continuity_id",
    "temporal_repeated_structures": "repeated_structure_id",
    "runtime_state_temporal_spans": "runtime_state_span_id",
    "cross_process_external_gaps": "external_gap_id",
    "grounded_temporal_bundles": "temporal_bundle_id",
    "temporal_context_sidecars": "temporal_sidecar_id",
    "temporal_calibration_audits": "calibration_audit_id",
    "temporal_ordering_diagnostics": "diagnostic_id",
    "package_124a_temporal_audits": "audit_id",
}


class Package124ATemporalStore:
    def __init__(self, state_dir: str | Path) -> None:
        if state_dir is None:
            raise ValueError("explicit state_dir is required")
        self.state_dir = Path(state_dir)
        self.root_dir = self.state_dir / PACKAGE_124A_TEMPORAL_DIRNAME
        self.db_path = self.root_dir / PACKAGE_124A_TEMPORAL_FILENAME
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
        payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        id_column = TABLE_KEY_FIELDS[table]
        record_id = str(payload[id_column])
        self.append_payload(table, id_column, record_id, payload)

    def append_payload(self, table: str, id_column: str, record_id: str, payload: dict[str, Any]) -> None:
        if table not in TABLE_KEY_FIELDS:
            raise ValueError(f"unknown Package 124A temporal table: {table}")
        if id_column != TABLE_KEY_FIELDS[table]:
            raise ValueError("id column does not match temporal table")
        with self.connection() as connection:
            connection.execute(
                f"""
                INSERT OR IGNORE INTO {table} (
                    {id_column}, created_at, payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    record_id,
                    str(payload.get("created_at", utc_now())),
                    canonical_json(payload),
                    sha256_payload(payload),
                ),
            )

    def list_payloads(self, table: str) -> tuple[dict[str, Any], ...]:
        if table not in TABLE_KEY_FIELDS:
            raise ValueError(f"unknown Package 124A temporal table: {table}")
        with self.connection() as connection:
            rows = connection.execute(f"SELECT payload_json FROM {table} ORDER BY row_id").fetchall()
        return tuple(dict(json.loads(str(row["payload_json"]))) for row in rows)

    def get_payload(self, table: str, record_id: str) -> dict[str, Any]:
        if table not in TABLE_KEY_FIELDS:
            raise ValueError(f"unknown Package 124A temporal table: {table}")
        id_column = TABLE_KEY_FIELDS[table]
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} WHERE {id_column} = ?",
                (record_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"missing {table} record: {record_id}")
        return dict(json.loads(str(row["payload_json"])))

    def latest_payload(self, table: str) -> dict[str, Any] | None:
        with self.connection() as connection:
            row = connection.execute(f"SELECT payload_json FROM {table} ORDER BY row_id DESC LIMIT 1").fetchone()
        return dict(json.loads(str(row["payload_json"]))) if row else None

    def counts(self) -> dict[str, int]:
        result: dict[str, int] = {}
        with self.connection() as connection:
            for table in TABLE_KEY_FIELDS:
                row = connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
                result[table] = int(row["count"])
        return result

    def validate_schema(self) -> dict[str, object]:
        with self.connection() as connection:
            metadata = connection.execute("SELECT schema_name, schema_version FROM store_metadata").fetchone()
            tables = {
                str(row["name"])
                for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            }
        missing = (set(TABLE_KEY_FIELDS) | {"store_metadata"}) - tables
        return {
            "valid": bool(
                metadata
                and metadata["schema_name"] == TEMPORAL_STORE_SCHEMA_NAME
                and metadata["schema_version"] == TEMPORAL_STORE_SCHEMA_VERSION
                and not missing
            ),
            "missing_tables": tuple(sorted(missing)),
            "db_path": str(self.db_path),
        }

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS store_metadata (
                    schema_name TEXT PRIMARY KEY,
                    schema_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO store_metadata (schema_name, schema_version, created_at)
                VALUES (?, ?, ?)
                """,
                (TEMPORAL_STORE_SCHEMA_NAME, TEMPORAL_STORE_SCHEMA_VERSION, utc_now()),
            )
            for table, key_field in TABLE_KEY_FIELDS.items():
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                        row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        {key_field} TEXT NOT NULL UNIQUE,
                        created_at TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        payload_sha256 TEXT NOT NULL
                    )
                    """
                )


def package_124a_temporal_store_path(state_dir: str | Path) -> Path:
    return Path(state_dir) / PACKAGE_124A_TEMPORAL_DIRNAME / PACKAGE_124A_TEMPORAL_FILENAME
