"""Append-only external evidence store for Package 138."""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from ashl_core_v1.runtime.host_sensor_types import canonical_json, plain, sha256_payload, utc_now


PACKAGE_DIR = "package_138_self_state_readback_boundary_v0"
DATABASE_NAME = "package_138.sqlite3"
STORE_SCHEMA_VERSION = "ashl_package_138_store_v0"

TABLE_KEYS = {
    "self_state_readback_consumer_inventory": "inventory_record_id",
    "self_state_readback_source_bindings": "source_binding_id",
    "self_state_readback_contracts": "contract_id",
    "self_state_readback_consumer_allowlists": "allowlist_id",
    "self_state_readback_authorizations": "authorization_id",
    "bounded_self_state_readbacks": "readback_id",
    "self_state_readback_consumptions": "consumption_id",
    "self_state_readback_lifecycle_records": "lifecycle_id",
    "self_state_readback_blocked_attempts": "blocked_attempt_id",
    "self_state_readback_counterfactual_snapshots": "snapshot_id",
    "self_state_readback_counterfactual_comparisons": "comparison_id",
    "self_state_readback_process_receipts": "process_receipt_id",
    "self_state_readback_fresh_process_resets": "reset_record_id",
    "package_138_control_results": "control_result_id",
    "package_138_regression_receipts": "regression_receipt_id",
    "package_138_audits": "audit_id",
}

_WINDOWS_ABSOLUTE_PATH = re.compile(r"^[A-Za-z]:[\\/]")


class Package138SelfStateReadbackStore:
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
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 30000")
        try:
            yield connection
        finally:
            connection.close()

    def append_once(self, table: str, record: Any) -> None:
        self._require_table(table)
        payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        record_id = str(payload[TABLE_KEYS[table]])
        self._validate_payload(payload)
        serialized = canonical_json(plain(payload))
        digest = sha256_payload(plain(payload))
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                f"SELECT payload_json, payload_sha256 FROM {table} WHERE record_id = ?",
                (record_id,),
            ).fetchone()
            if existing is not None:
                existing_payload = self._verified_payload(existing, table)
                if not _same_identity_payload(existing_payload, plain(payload)):
                    raise ValueError(f"Package 138 identity collision: {record_id}")
                connection.commit()
                return
            extra_columns: tuple[str, ...] = ()
            extra_values: tuple[str, ...] = ()
            if table == "bounded_self_state_readbacks":
                extra_columns = ("authorization_id",)
                extra_values = (str(payload["authorization_ref"]),)
            elif table == "self_state_readback_consumptions":
                extra_columns = ("readback_id",)
                extra_values = (str(payload["readback_ref"]),)
            column_sql = "" if not extra_columns else ", " + ", ".join(extra_columns)
            placeholder_sql = "" if not extra_values else ", " + ", ".join("?" for _ in extra_values)
            try:
                connection.execute(
                    f"""
                    INSERT INTO {table} (
                        record_id, created_at, payload_json, payload_sha256{column_sql}
                    ) VALUES (?, ?, ?, ?{placeholder_sql})
                    """,
                    (
                        record_id,
                        str(payload.get("created_at", utc_now())),
                        serialized,
                        digest,
                        *extra_values,
                    ),
                )
            except sqlite3.IntegrityError as error:
                raise ValueError(f"Package 138 append-only uniqueness violation: {table}") from error
            connection.commit()

    def append_group(self, records: tuple[tuple[str, Any], ...]) -> None:
        if not records:
            raise ValueError("Package 138 append group cannot be empty")
        prepared: list[tuple[str, str, str, str, str, tuple[str, ...], tuple[str, ...]]] = []
        for table, record in records:
            self._require_table(table)
            payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
            self._validate_payload(payload)
            extra_columns: tuple[str, ...] = ()
            extra_values: tuple[str, ...] = ()
            if table == "bounded_self_state_readbacks":
                extra_columns = ("authorization_id",)
                extra_values = (str(payload["authorization_ref"]),)
            elif table == "self_state_readback_consumptions":
                extra_columns = ("readback_id",)
                extra_values = (str(payload["readback_ref"]),)
            prepared.append(
                (
                    table,
                    str(payload[TABLE_KEYS[table]]),
                    str(payload.get("created_at", utc_now())),
                    canonical_json(plain(payload)),
                    sha256_payload(plain(payload)),
                    extra_columns,
                    extra_values,
                )
            )
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            for table, record_id, created_at, serialized, digest, extra_columns, extra_values in prepared:
                existing = connection.execute(
                    f"SELECT payload_json, payload_sha256 FROM {table} WHERE record_id = ?",
                    (record_id,),
                ).fetchone()
                if existing is not None:
                    existing_payload = self._verified_payload(existing, table)
                    incoming_payload = json.loads(serialized)
                    if not _same_identity_payload(existing_payload, incoming_payload):
                        raise ValueError(f"Package 138 identity collision: {record_id}")
                    continue
                column_sql = "" if not extra_columns else ", " + ", ".join(extra_columns)
                placeholder_sql = "" if not extra_values else ", " + ", ".join("?" for _ in extra_values)
                connection.execute(
                    f"INSERT INTO {table} (record_id, created_at, payload_json, payload_sha256{column_sql}) "
                    f"VALUES (?, ?, ?, ?{placeholder_sql})",
                    (record_id, created_at, serialized, digest, *extra_values),
                )
            connection.commit()

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

    def authorization_has_readback(self, authorization_id: str) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM bounded_self_state_readbacks WHERE authorization_id = ? LIMIT 1",
                (authorization_id,),
            ).fetchone()
        return row is not None

    def readback_has_consumption(self, readback_id: str) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM self_state_readback_consumptions WHERE readback_id = ? LIMIT 1",
                (readback_id,),
            ).fetchone()
        return row is not None

    def terminal_lifecycle_for(self, readback_id: str) -> dict[str, Any] | None:
        records = tuple(
            item
            for item in self.list_payloads("self_state_readback_lifecycle_records")
            if item.get("readback_ref") == readback_id
        )
        return records[-1] if records else None

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
                "SELECT schema_version FROM package_138_store_metadata WHERE schema_name = ?",
                (PACKAGE_DIR,),
            ).fetchone()
            for table in TABLE_KEYS:
                rows = connection.execute(
                    f"SELECT record_id, payload_json, payload_sha256 FROM {table} ORDER BY row_id"
                ).fetchall()
                for row in rows:
                    try:
                        self._verified_payload(row, table)
                    except RuntimeError as error:
                        failures.append(str(error))
        forbidden_tables = {
            "active_self_state_head",
            "persistent_self_state_records",
            "working_readback",
            "working_readbacks",
            "memory_records",
            "drive_state",
            "perception_history",
            "selected_actions",
            "output_records",
        }
        if tables.intersection(forbidden_tables):
            failures.append("forbidden_authority_or_working_readback_table_present")
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
            "active_head_table_present": "active_self_state_head" in tables,
            "self_state_history_table_present": "persistent_self_state_records" in tables,
            "persistent_working_readback_table_present": bool(
                tables.intersection({"working_readback", "working_readbacks"})
            ),
            "failure_reasons": tuple(failures),
        }

    def update(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 138 evidence is append-only")

    def delete(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 138 evidence is append-only")

    def replace(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 138 evidence is append-only")

    @staticmethod
    def _verified_payload(row: sqlite3.Row, table: str) -> dict[str, Any]:
        payload = json.loads(str(row["payload_json"]))
        if str(row["payload_sha256"]) != sha256_payload(payload):
            raise RuntimeError(f"blocked_corrupt_package_138_payload:{table}")
        return payload

    @staticmethod
    def _validate_payload(payload: dict[str, Any]) -> None:
        if _contains_private_absolute_path(payload):
            raise ValueError("Package 138 records cannot persist private absolute paths")

    @staticmethod
    def _require_table(table: str) -> None:
        if table not in TABLE_KEYS:
            raise ValueError(f"unsupported Package 138 table: {table}")

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS package_138_store_metadata (
                    schema_name TEXT PRIMARY KEY,
                    schema_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO package_138_store_metadata (
                    schema_name, schema_version, created_at
                ) VALUES (?, ?, ?)
                """,
                (PACKAGE_DIR, STORE_SCHEMA_VERSION, utc_now()),
            )
            for table in TABLE_KEYS:
                extras = ""
                if table == "bounded_self_state_readbacks":
                    extras = ", authorization_id TEXT NOT NULL UNIQUE"
                elif table == "self_state_readback_consumptions":
                    extras = ", readback_id TEXT NOT NULL UNIQUE"
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                        row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        record_id TEXT NOT NULL UNIQUE,
                        created_at TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        payload_sha256 TEXT NOT NULL
                        {extras}
                    )
                    """
                )
            connection.commit()


def package_138_store_path(state_dir: str | Path) -> Path:
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
