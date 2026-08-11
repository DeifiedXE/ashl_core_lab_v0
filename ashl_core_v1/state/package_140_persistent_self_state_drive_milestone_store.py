"""Append-only external audit store for the Package 140 milestone."""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from ashl_core_v1.runtime.host_sensor_types import canonical_json, plain, sha256_payload, utc_now


PACKAGE_DIR = "package_140_persistent_self_state_and_drive_milestone_v0"
DATABASE_NAME = "package_140.sqlite3"
STORE_SCHEMA_VERSION = "ashl_package_140_append_only_store_v0"

TABLE_KEYS = {
    "package_140_evidence_sources": "source_record_id",
    "package_140_authority_evidence": "authority_evidence_id",
    "package_140_cross_package_lineage": "lineage_record_id",
    "persistent_self_state_and_drive_capability_contracts": "capability_contract_id",
    "package_140_no_fork_revalidations": "no_fork_revalidation_id",
    "package_140_boundary_control_results": "control_result_id",
    "package_140_regression_receipts": "regression_receipt_id",
    "package_140_audits": "audit_id",
}

_WINDOWS_ABSOLUTE_PATH = re.compile(r"^[A-Za-z]:[\\/]")


class Package140PersistentSelfStateDriveMilestoneStore:
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

    def append_once(self, table: str, record: Any) -> None:
        self.append_group(((table, record),))

    def append_group(self, records: tuple[tuple[str, Any], ...]) -> None:
        if not records:
            raise ValueError("Package 140 append group cannot be empty")
        prepared: list[tuple[str, str, str, str, str]] = []
        for table, record in records:
            self._require_table(table)
            payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
            self._validate_payload(payload)
            prepared.append(
                (
                    table,
                    str(payload[TABLE_KEYS[table]]),
                    str(payload.get("created_at", utc_now())),
                    canonical_json(plain(payload)),
                    sha256_payload(plain(payload)),
                )
            )
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            for table, record_id, created_at, serialized, digest in prepared:
                existing = connection.execute(
                    f"SELECT payload_json, payload_sha256 FROM {table} WHERE record_id = ?",
                    (record_id,),
                ).fetchone()
                if existing is not None:
                    persisted = self._verified_payload(existing, table)
                    incoming = json.loads(serialized)
                    if not _same_identity_payload(persisted, incoming):
                        raise ValueError(f"Package 140 identity collision: {record_id}")
                    continue
                connection.execute(
                    f"INSERT INTO {table} "
                    "(record_id, created_at, payload_json, payload_sha256) "
                    "VALUES (?, ?, ?, ?)",
                    (record_id, created_at, serialized, digest),
                )
            connection.commit()

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
                "SELECT schema_version FROM package_140_store_metadata WHERE schema_name = ?",
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
            "persistent_self_state_records",
            "active_self_state_head",
            "drive_signal_traces",
            "drive_modulation_applications",
            "self_state_teacher_reviews",
            "bounded_self_state_readbacks",
            "self_state_head_selection_authorizations",
            "memory_records",
            "perception_history",
            "selected_actions",
            "output_records",
        }
        if tables.intersection(forbidden_tables):
            failures.append("forbidden_authority_table_present")
        valid = all(
            (
                integrity == "ok",
                set(TABLE_KEYS).issubset(tables),
                metadata is not None,
                not failures,
            )
        )
        return {
            "valid": valid,
            "integrity_check": integrity,
            "schema_version": str(metadata["schema_version"]) if metadata else None,
            "append_only_history": True,
            "authority_table_present": bool(tables.intersection(forbidden_tables)),
            "failure_reasons": tuple(failures),
        }

    def update(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 140 evidence is append-only")

    def delete(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 140 evidence is append-only")

    def replace(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 140 evidence is append-only")

    @staticmethod
    def _verified_payload(row: sqlite3.Row, table: str) -> dict[str, Any]:
        payload = json.loads(str(row["payload_json"]))
        if str(row["payload_sha256"]) != sha256_payload(payload):
            raise RuntimeError(f"blocked_corrupt_package_140_payload:{table}")
        return payload

    @staticmethod
    def _validate_payload(payload: dict[str, Any]) -> None:
        if _contains_private_absolute_path(payload):
            raise ValueError("Package 140 records cannot persist private absolute paths")

    @staticmethod
    def _require_table(table: str) -> None:
        if table not in TABLE_KEYS:
            raise ValueError(f"unsupported Package 140 table: {table}")

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS package_140_store_metadata (
                    schema_name TEXT PRIMARY KEY,
                    schema_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO package_140_store_metadata (
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


def package_140_store_path(state_dir: str | Path) -> Path:
    return Path(state_dir) / PACKAGE_DIR / DATABASE_NAME


def _contains_private_absolute_path(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_contains_private_absolute_path(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_private_absolute_path(item) for item in value)
    if isinstance(value, str):
        return value.startswith("/") or bool(_WINDOWS_ABSOLUTE_PATH.match(value))
    return False


def _same_identity_payload(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_identity = dict(left)
    right_identity = dict(right)
    left_identity.pop("created_at", None)
    right_identity.pop("created_at", None)
    return left_identity == right_identity
