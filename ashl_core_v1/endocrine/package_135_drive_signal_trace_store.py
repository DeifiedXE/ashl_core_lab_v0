"""Append-only external evidence store for Package 135."""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from ashl_core_v1.runtime.host_sensor_types import canonical_json, plain, sha256_payload, utc_now


PACKAGE_DIR = "package_135_drive_signal_trace_separation_v0"
DATABASE_NAME = "package_135.sqlite3"
STORE_SCHEMA_VERSION = "ashl_package_135_drive_signal_trace_append_only_store_v0"

TABLE_KEYS = {
    "legacy_drive_boundary_records": "boundary_record_id",
    "drive_trace_contracts": "contract_id",
    "package_134_drive_non_recovery_evidence": "evidence_id",
    "drive_source_observations": "source_observation_id",
    "drive_signal_traces": "signal_trace_id",
    "drive_lineage_validations": "lineage_validation_id",
    "drive_authority_separations": "separation_record_id",
    "drive_cross_session_resets": "reset_record_id",
    "drive_trace_process_receipts": "process_receipt_id",
    "drive_trace_process_pairs": "process_pair_id",
    "package_135_control_results": "control_result_id",
    "package_135_regression_receipts": "regression_receipt_id",
    "package_135_audits": "audit_id",
}

_WINDOWS_ABSOLUTE_PATH = re.compile(r"^[A-Za-z]:[\\/]")


class Package135DriveSignalTraceStore:
    """Stores immutable Package 135 history and deliberately has no active head."""

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
        self._require_table(table)
        payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        record_id = str(payload[TABLE_KEYS[table]])
        self._validate_payload(payload)
        try:
            with self.connection() as connection:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    f"INSERT INTO {table} (record_id, created_at, payload_json, payload_sha256) VALUES (?, ?, ?, ?)",
                    (
                        record_id,
                        str(payload.get("created_at", utc_now())),
                        canonical_json(plain(payload)),
                        sha256_payload(plain(payload)),
                    ),
                )
                connection.commit()
        except sqlite3.IntegrityError as error:
            raise ValueError(f"append-only Package 135 record already exists: {record_id}") from error

    def append_once(self, table: str, record: Any) -> None:
        payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        record_id = str(payload[TABLE_KEYS[table]])
        if not self.has_record(table, record_id):
            self.append_record(table, record)

    def append_group(self, records: tuple[tuple[str, Any], ...]) -> None:
        prepared: list[tuple[str, str, dict[str, Any]]] = []
        for table, record in records:
            self._require_table(table)
            payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
            self._validate_payload(payload)
            prepared.append((table, str(payload[TABLE_KEYS[table]]), payload))
        try:
            with self.connection() as connection:
                connection.execute("BEGIN IMMEDIATE")
                for table, record_id, payload in prepared:
                    connection.execute(
                        f"INSERT INTO {table} (record_id, created_at, payload_json, payload_sha256) VALUES (?, ?, ?, ?)",
                        (
                            record_id,
                            str(payload.get("created_at", utc_now())),
                            canonical_json(plain(payload)),
                            sha256_payload(plain(payload)),
                        ),
                    )
                connection.commit()
        except sqlite3.IntegrityError as error:
            raise ValueError("append-only Package 135 record group contains an existing identity") from error

    def has_record(self, table: str, record_id: str) -> bool:
        self._require_table(table)
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT 1 FROM {table} WHERE record_id = ? LIMIT 1", (record_id,)
            ).fetchone()
        return row is not None

    def list_payloads(self, table: str) -> tuple[dict[str, Any], ...]:
        self._require_table(table)
        with self.connection() as connection:
            rows = connection.execute(
                f"SELECT payload_json, payload_sha256 FROM {table} ORDER BY row_id"
            ).fetchall()
        return tuple(self._verified_payload(row, table) for row in rows)

    def get_payload(self, table: str, record_id: str) -> dict[str, Any]:
        self._require_table(table)
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json, payload_sha256 FROM {table} WHERE record_id = ?",
                (record_id,),
            ).fetchone()
        if row is None:
            raise KeyError(record_id)
        return self._verified_payload(row, table)

    def latest_payload(self, table: str) -> dict[str, Any] | None:
        self._require_table(table)
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json, payload_sha256 FROM {table} ORDER BY row_id DESC LIMIT 1"
            ).fetchone()
        return self._verified_payload(row, table) if row else None

    def count(self, table: str) -> int:
        self._require_table(table)
        with self.connection() as connection:
            row = connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
        return int(row["count"])

    def audit_integrity(self) -> dict[str, Any]:
        failures: list[str] = []
        with self.connection() as connection:
            integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
            tables = {
                str(row["name"])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
            metadata = connection.execute(
                "SELECT schema_version FROM package_135_store_metadata WHERE schema_name = ?",
                (PACKAGE_DIR,),
            ).fetchone()
            for table in TABLE_KEYS:
                rows = connection.execute(
                    f"SELECT payload_json, payload_sha256 FROM {table} ORDER BY row_id"
                ).fetchall()
                for row in rows:
                    try:
                        self._verified_payload(row, table)
                    except RuntimeError as error:
                        failures.append(str(error))
        forbidden_tables = {
            "active_head",
            "active_drive_head",
            "drive_signal_current_state",
            "drive_signal_recovery",
            "memory_records",
            "selected_actions",
            "outputs",
        }
        valid = all(
            (
                integrity == "ok",
                set(TABLE_KEYS).issubset(tables),
                metadata is not None,
                not forbidden_tables.intersection(tables),
                not failures,
            )
        )
        return {
            "valid": valid,
            "integrity_check": integrity,
            "schema_version": str(metadata["schema_version"]) if metadata else None,
            "append_only_history": True,
            "active_drive_head_present": False,
            "cross_session_recovery_table_present": False,
            "forbidden_tables_absent": not forbidden_tables.intersection(tables),
            "failure_reasons": tuple(failures),
        }

    def update(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 135 records are append-only")

    def delete(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 135 records are append-only")

    def select_active_head(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 135 has no active drive head")

    def recover(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 135 drive traces are not recoverable")

    @staticmethod
    def _verified_payload(row: sqlite3.Row, table: str) -> dict[str, Any]:
        payload = json.loads(str(row["payload_json"]))
        if str(row["payload_sha256"]) != sha256_payload(payload):
            raise RuntimeError(f"blocked_corrupt_package_135_payload:{table}")
        return payload

    @staticmethod
    def _validate_payload(payload: dict[str, Any]) -> None:
        if _contains_private_absolute_path(payload):
            raise ValueError("Package 135 records cannot persist private absolute paths")

    @staticmethod
    def _require_table(table: str) -> None:
        if table not in TABLE_KEYS:
            raise ValueError(f"unsupported Package 135 table: {table}")

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS package_135_store_metadata (
                    schema_name TEXT PRIMARY KEY,
                    schema_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO package_135_store_metadata (
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


def package_135_store_path(state_dir: str | Path) -> Path:
    return Path(state_dir) / PACKAGE_DIR / DATABASE_NAME


def _contains_private_absolute_path(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_contains_private_absolute_path(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_private_absolute_path(item) for item in value)
    if isinstance(value, str):
        return value.startswith("/") or bool(_WINDOWS_ABSOLUTE_PATH.match(value))
    return False
