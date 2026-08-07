"""Append-only external store for Package 136 evidence."""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from ashl_core_v1.runtime.host_sensor_types import canonical_json, plain, sha256_payload, utc_now


PACKAGE_DIR = "package_136_same_session_drive_modulation_v0"
DATABASE_NAME = "package_136.sqlite3"
STORE_SCHEMA_VERSION = "ashl_package_136_append_only_store_v0"

TABLE_KEYS = {
    "drive_modulation_consumer_inventory": "inventory_record_id",
    "package_135_signal_authority_bindings": "source_binding_id",
    "same_session_drive_modulation_contracts": "contract_id",
    "drive_modulation_consumer_allowlists": "allowlist_id",
    "same_session_drive_modulation_authorizations": "authorization_id",
    "drive_modulation_policy_decisions": "policy_decision_id",
    "drive_modulation_derivations": "derivation_id",
    "drive_modulation_applications": "application_id",
    "drive_modulation_neutralizations": "neutralization_id",
    "drive_modulation_boundary_snapshots": "snapshot_id",
    "drive_modulation_counterfactual_comparisons": "comparison_id",
    "drive_modulation_process_receipts": "process_receipt_id",
    "drive_modulation_cross_session_neutrality": "neutrality_record_id",
    "package_136_control_results": "control_result_id",
    "package_136_regression_receipts": "regression_receipt_id",
    "package_136_audits": "audit_id",
}

_WINDOWS_ABSOLUTE_PATH = re.compile(r"^[A-Za-z]:[\\/]")


class Package136DriveModulationStore:
    """Immutable history store with no active modulation or recovery authority."""

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
        self._validate_payload(payload)
        record_id = str(payload[TABLE_KEYS[table]])
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
            raise ValueError(f"append-only Package 136 record already exists: {record_id}") from error

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
            raise ValueError("append-only Package 136 record group contains an existing identity") from error

    def has_record(self, table: str, record_id: str) -> bool:
        self._require_table(table)
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT 1 FROM {table} WHERE record_id = ? LIMIT 1", (record_id,)
            ).fetchone()
        return row is not None

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

    def list_payloads(self, table: str) -> tuple[dict[str, Any], ...]:
        self._require_table(table)
        with self.connection() as connection:
            rows = connection.execute(
                f"SELECT payload_json, payload_sha256 FROM {table} ORDER BY row_id"
            ).fetchall()
        return tuple(self._verified_payload(row, table) for row in rows)

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
                "SELECT schema_version FROM package_136_store_metadata WHERE schema_name = ?",
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
            "active_modulation",
            "active_drive_modulation_head",
            "current_drive_modulation",
            "drive_modulation_recovery",
            "production_consumer_state",
            "memory_records",
            "self_state_records",
            "output_records",
        }
        present_forbidden = tuple(sorted(forbidden_tables & tables))
        valid = (
            integrity == "ok"
            and metadata is not None
            and str(metadata["schema_version"]) == STORE_SCHEMA_VERSION
            and set(TABLE_KEYS).issubset(tables)
            and not failures
            and not present_forbidden
        )
        return {
            "valid": valid,
            "integrity_check": integrity,
            "payload_failures": tuple(failures),
            "forbidden_tables_present": present_forbidden,
            "append_only_history": True,
            "active_modulation_present": "active_modulation" in tables,
            "cross_session_recovery_table_present": "drive_modulation_recovery" in tables,
            "production_consumer_state_present": "production_consumer_state" in tables,
        }

    def update(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 136 store is append-only")

    def delete(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 136 store is append-only")

    def select_active_modulation(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 136 has no active modulation persistence authority")

    def recover_modulation(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 136 modulation cannot be recovered across sessions")

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS package_136_store_metadata (
                    schema_name TEXT PRIMARY KEY,
                    schema_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "INSERT OR IGNORE INTO package_136_store_metadata (schema_name, schema_version, created_at) VALUES (?, ?, ?)",
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

    @staticmethod
    def _require_table(table: str) -> None:
        if table not in TABLE_KEYS:
            raise ValueError(f"unknown Package 136 table: {table}")

    @staticmethod
    def _validate_payload(payload: dict[str, Any]) -> None:
        if _contains_private_absolute_path(payload):
            raise ValueError("Package 136 records cannot persist private absolute paths")

    @staticmethod
    def _verified_payload(row: sqlite3.Row, table: str) -> dict[str, Any]:
        payload = json.loads(str(row["payload_json"]))
        if str(row["payload_sha256"]) != sha256_payload(payload):
            raise RuntimeError(f"Package 136 payload hash mismatch: {table}")
        return payload


def package_136_store_path(state_dir: str | Path) -> Path:
    return Path(state_dir) / PACKAGE_DIR / DATABASE_NAME


def _contains_private_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return bool(_WINDOWS_ABSOLUTE_PATH.match(value)) or value.startswith("/")
    if isinstance(value, dict):
        return any(_contains_private_absolute_path(item) for item in value.values())
    if isinstance(value, (tuple, list)):
        return any(_contains_private_absolute_path(item) for item in value)
    return False
