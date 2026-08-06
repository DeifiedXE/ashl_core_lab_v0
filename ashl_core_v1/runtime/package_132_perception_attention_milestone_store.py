"""Append-only external SQLite store for Package 132 audit records."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from ashl_core_v1.runtime.host_sensor_types import (
    canonical_json,
    plain,
    sha256_payload,
    utc_now,
)


PACKAGE_DIR = "package_132_perception_attention_milestone_v0"
DATABASE_NAME = "package_132.sqlite3"
STORE_SCHEMA_VERSION = "ashl_package_132_append_only_store_v0"

TABLE_KEYS = {
    "package_132_evidence_sources": "evidence_source_id",
    "package_132_package_evidence": "package_evidence_id",
    "package_132_cross_package_lineage": "lineage_record_id",
    "perception_attention_closure_contracts": "closure_contract_id",
    "package_132_boundary_control_results": "control_result_id",
    "package_132_regression_receipts": "regression_receipt_id",
    "package_132_audits": "audit_id",
}


class Package132PerceptionAttentionMilestoneStore:
    def __init__(self, state_dir: str | Path) -> None:
        if state_dir is None:
            raise ValueError("explicit external state_dir is required")
        self.state_dir = Path(state_dir)
        self.root = self.state_dir / PACKAGE_DIR
        self.root.mkdir(parents=True, exist_ok=True)
        self.database_path = self.root / DATABASE_NAME
        self._initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=30.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 30000")
        try:
            yield connection
        finally:
            connection.close()

    def append_record(self, table: str, record: Any) -> None:
        payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        key_name = TABLE_KEYS[table]
        self.append_payload(table, key_name, str(payload[key_name]), payload)

    def append_payload(
        self,
        table: str,
        key_name: str,
        record_id: str,
        payload: dict[str, Any],
    ) -> None:
        self._require_table(table)
        if TABLE_KEYS[table] != key_name:
            raise ValueError(f"unsupported Package 132 table/key: {table}/{key_name}")
        serialized = canonical_json(plain(payload))
        with self.connection() as connection:
            try:
                connection.execute(
                    f"""
                    INSERT INTO {table} (
                        record_id, created_at, payload_json, payload_sha256
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        str(record_id),
                        str(payload.get("created_at", utc_now())),
                        serialized,
                        sha256_payload(plain(payload)),
                    ),
                )
            except sqlite3.IntegrityError as error:
                raise ValueError(
                    f"append-only Package 132 record already exists: {record_id}"
                ) from error
            connection.commit()

    def list_payloads(self, table: str) -> tuple[dict[str, Any], ...]:
        self._require_table(table)
        with self.connection() as connection:
            rows = connection.execute(
                f"SELECT payload_json FROM {table} ORDER BY row_id"
            ).fetchall()
        return tuple(json.loads(str(row["payload_json"])) for row in rows)

    def latest_payload(self, table: str) -> dict[str, Any] | None:
        self._require_table(table)
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} ORDER BY row_id DESC LIMIT 1"
            ).fetchone()
        return json.loads(str(row["payload_json"])) if row else None

    def count(self, table: str) -> int:
        self._require_table(table)
        with self.connection() as connection:
            row = connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
        return int(row["count"])

    def has_record(self, table: str, record_id: str) -> bool:
        self._require_table(table)
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT 1 FROM {table} WHERE record_id = ? LIMIT 1",
                (str(record_id),),
            ).fetchone()
        return row is not None

    def audit_append_only_store(self) -> dict[str, object]:
        with self.connection() as connection:
            integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
            tables = {
                str(row["name"])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
            metadata = connection.execute(
                """
                SELECT schema_version FROM package_132_store_metadata
                WHERE schema_name = ?
                """,
                (PACKAGE_DIR,),
            ).fetchone()
        return {
            "valid": (
                integrity == "ok"
                and set(TABLE_KEYS).issubset(tables)
                and bool(metadata)
            ),
            "integrity_check": integrity,
            "schema_version": str(metadata["schema_version"]) if metadata else None,
        }

    @staticmethod
    def forbidden_mutation_operations() -> tuple[str, ...]:
        return ("update", "delete")

    def _require_table(self, table: str) -> None:
        if table not in TABLE_KEYS:
            raise ValueError(f"unsupported Package 132 table: {table}")

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS package_132_store_metadata (
                    schema_name TEXT PRIMARY KEY,
                    schema_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO package_132_store_metadata (
                    schema_name, schema_version, created_at
                ) VALUES (?, ?, ?)
                """,
                (PACKAGE_DIR, STORE_SCHEMA_VERSION, utc_now()),
            )
            for table in TABLE_KEYS:
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                        row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        record_id TEXT NOT NULL UNIQUE,
                        created_at TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        payload_sha256 TEXT NOT NULL
                    )
                    """
                )
            connection.commit()


def package_132_store_path(state_dir: str | Path) -> Path:
    return Path(state_dir) / PACKAGE_DIR / DATABASE_NAME
