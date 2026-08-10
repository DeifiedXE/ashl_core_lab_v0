"""Append-only external evidence store for Package 139."""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from ashl_core_v1.runtime.host_sensor_types import canonical_json, plain, sha256_payload, utc_now


PACKAGE_DIR = "package_139_self_state_rollback_and_audit_v0"
DATABASE_NAME = "package_139.sqlite3"
STORE_SCHEMA_VERSION = "ashl_package_139_append_only_store_v0"

TABLE_KEYS = {
    "self_state_rollback_contracts": "contract_id",
    "self_state_rollback_source_bindings": "source_binding_id",
    "self_state_ancestor_proofs": "ancestor_proof_id",
    "self_state_head_selection_authorizations": "authorization_id",
    "self_state_readback_invalidation_gates": "invalidation_gate_id",
    "self_state_head_selection_commit_intents": "commit_intent_id",
    "self_state_head_selection_authorization_consumptions": "consumption_id",
    "self_state_head_selection_commit_receipts": "commit_receipt_id",
    "self_state_rollback_blocked_attempts": "blocked_attempt_id",
    "self_state_rollback_process_receipts": "process_receipt_id",
    "self_state_rollback_no_fork_guard_records": "no_fork_guard_id",
    "self_state_rollback_counterfactual_comparisons": "comparison_id",
    "package_139_control_cases": "control_case_id",
    "package_139_control_results": "control_result_id",
    "package_139_regression_receipts": "regression_receipt_id",
    "package_139_audits": "audit_id",
}

_WINDOWS_ABSOLUTE_PATH = re.compile(r"^[A-Za-z]:[\\/]")


class Package139SelfStateRollbackStore:
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
        self.append_group(((table, record),))

    def append_group(self, records: tuple[tuple[str, Any], ...]) -> None:
        if not records:
            raise ValueError("Package 139 append group cannot be empty")
        prepared: list[tuple[str, str, str, str, str, tuple[str, ...], tuple[Any, ...]]] = []
        for table, record in records:
            self._require_table(table)
            payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
            self._validate_payload(payload)
            extra_columns: tuple[str, ...] = ()
            extra_values: tuple[Any, ...] = ()
            if table == "self_state_head_selection_authorizations":
                extra_columns = ("operation",)
                extra_values = (str(payload["operation"]),)
            elif table == "self_state_head_selection_authorization_consumptions":
                extra_columns = ("authorization_id",)
                extra_values = (str(payload["authorization_ref"]),)
            elif table == "self_state_head_selection_commit_receipts":
                extra_columns = ("authorization_id", "operation")
                extra_values = (
                    str(payload["authorization_ref"]),
                    str(payload["operation"]),
                )
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
            for table, record_id, created_at, serialized, digest, columns, values in prepared:
                existing = connection.execute(
                    f"SELECT payload_json, payload_sha256 FROM {table} WHERE record_id = ?",
                    (record_id,),
                ).fetchone()
                if existing is not None:
                    persisted = self._verified_payload(existing, table)
                    incoming = json.loads(serialized)
                    if not _same_identity_payload(persisted, incoming):
                        raise ValueError(f"Package 139 identity collision: {record_id}")
                    continue
                column_sql = "" if not columns else ", " + ", ".join(columns)
                placeholder_sql = "" if not values else ", " + ", ".join("?" for _ in values)
                try:
                    connection.execute(
                        f"INSERT INTO {table} "
                        f"(record_id, created_at, payload_json, payload_sha256{column_sql}) "
                        f"VALUES (?, ?, ?, ?{placeholder_sql})",
                        (record_id, created_at, serialized, digest, *values),
                    )
                except sqlite3.IntegrityError as error:
                    raise ValueError(
                        f"Package 139 append-only uniqueness violation: {table}"
                    ) from error
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

    def authorization_consumed(self, authorization_id: str) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM self_state_head_selection_authorization_consumptions "
                "WHERE authorization_id = ? LIMIT 1",
                (authorization_id,),
            ).fetchone()
        return row is not None

    def receipt_for_authorization(self, authorization_id: str) -> dict[str, Any] | None:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT payload_json, payload_sha256 FROM self_state_head_selection_commit_receipts "
                "WHERE authorization_id = ? ORDER BY row_id",
                (authorization_id,),
            ).fetchall()
        if len(rows) > 1:
            raise RuntimeError("blocked_ambiguous_package_139_commit_receipt")
        return self._verified_payload(rows[0], "self_state_head_selection_commit_receipts") if rows else None

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
                "SELECT schema_version FROM package_139_store_metadata WHERE schema_name = ?",
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
            "persistent_self_state_records",
            "active_self_state_head",
            "working_readbacks",
            "memory_records",
            "drive_state",
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
            "package_133_history_table_present": "persistent_self_state_records" in tables,
            "package_134_active_head_table_present": "active_self_state_head" in tables,
            "failure_reasons": tuple(failures),
        }

    def update(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 139 evidence is append-only")

    def delete(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 139 evidence is append-only")

    def replace(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 139 evidence is append-only")

    @staticmethod
    def _verified_payload(row: sqlite3.Row, table: str) -> dict[str, Any]:
        payload = json.loads(str(row["payload_json"]))
        if str(row["payload_sha256"]) != sha256_payload(payload):
            raise RuntimeError(f"blocked_corrupt_package_139_payload:{table}")
        return payload

    @staticmethod
    def _validate_payload(payload: dict[str, Any]) -> None:
        if _contains_private_absolute_path(payload):
            raise ValueError("Package 139 records cannot persist private absolute paths")

    @staticmethod
    def _require_table(table: str) -> None:
        if table not in TABLE_KEYS:
            raise ValueError(f"unsupported Package 139 table: {table}")

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS package_139_store_metadata (
                    schema_name TEXT PRIMARY KEY,
                    schema_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO package_139_store_metadata (
                    schema_name, schema_version, created_at
                ) VALUES (?, ?, ?)
                """,
                (PACKAGE_DIR, STORE_SCHEMA_VERSION, utc_now()),
            )
            for table in TABLE_KEYS:
                extras = ""
                if table == "self_state_head_selection_authorizations":
                    extras = ", operation TEXT NOT NULL"
                elif table == "self_state_head_selection_authorization_consumptions":
                    extras = ", authorization_id TEXT NOT NULL UNIQUE"
                elif table == "self_state_head_selection_commit_receipts":
                    extras = ", authorization_id TEXT NOT NULL UNIQUE, operation TEXT NOT NULL"
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


def package_139_store_path(state_dir: str | Path) -> Path:
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
