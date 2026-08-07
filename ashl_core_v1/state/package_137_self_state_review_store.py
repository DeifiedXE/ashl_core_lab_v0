"""Append-only Package 137 review and cross-authority commit evidence store."""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from ashl_core_v1.runtime.host_sensor_types import canonical_json, plain, sha256_payload, utc_now


PACKAGE_DIR = "package_137_persistent_self_state_review_gate_v0"
DATABASE_NAME = "package_137.sqlite3"
STORE_SCHEMA_VERSION = "ashl_package_137_append_only_review_gate_store_v0"

TABLE_KEYS = {
    "teacher_authority_bindings": "authority_binding_id",
    "self_state_successor_deltas": "delta_id",
    "self_state_successor_proposals": "proposal_id",
    "self_state_teacher_reviews": "review_id",
    "self_state_mutation_commit_intents": "commit_intent_id",
    "self_state_mutation_commit_receipts": "commit_receipt_id",
    "self_state_review_invariance_records": "invariance_id",
    "self_state_mutation_blocked_attempts": "blocked_attempt_id",
    "self_state_mutation_process_receipts": "process_receipt_id",
    "package_137_control_results": "control_result_id",
    "package_137_regression_receipts": "regression_receipt_id",
    "package_137_audits": "audit_id",
}

_WINDOWS_ABSOLUTE_PATH = re.compile(r"^[A-Za-z]:[\\/]")


class Package137SelfStateReviewStore:
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
                f"SELECT payload_sha256 FROM {table} WHERE record_id = ?",
                (record_id,),
            ).fetchone()
            if existing is not None:
                if str(existing["payload_sha256"]) != digest:
                    raise ValueError(f"Package 137 identity collision: {record_id}")
                connection.commit()
                return
            extra_columns: tuple[str, ...] = ()
            extra_values: tuple[str, ...] = ()
            if table == "self_state_teacher_reviews":
                extra_columns = ("proposal_id",)
                extra_values = (str(payload["proposal_id"]),)
            elif table == "self_state_mutation_commit_intents":
                extra_columns = ("review_id",)
                extra_values = (str(payload["review_id"]),)
            elif table == "self_state_mutation_commit_receipts":
                extra_columns = ("review_id",)
                extra_values = (str(payload["review_id"]),)
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
                raise ValueError(f"Package 137 append-only uniqueness violation: {table}") from error
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

    def review_exists_for_proposal(self, proposal_id: str) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM self_state_teacher_reviews WHERE proposal_id = ? LIMIT 1",
                (proposal_id,),
            ).fetchone()
        return row is not None

    def review_has_commit_receipt(self, review_id: str) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM self_state_mutation_commit_receipts WHERE review_id = ? LIMIT 1",
                (review_id,),
            ).fetchone()
        return row is not None

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
                "SELECT schema_version FROM package_137_store_metadata WHERE schema_name = ?",
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
            "drive_state",
            "memory_records",
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
            "active_head_table_present": "active_self_state_head" in tables,
            "self_state_history_table_present": "persistent_self_state_records" in tables,
            "failure_reasons": tuple(failures),
        }

    def update(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 137 review history is append-only")

    def delete(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 137 review history is append-only")

    def replace(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 137 review history is append-only")

    @staticmethod
    def _verified_payload(row: sqlite3.Row, table: str) -> dict[str, Any]:
        payload = json.loads(str(row["payload_json"]))
        if str(row["payload_sha256"]) != sha256_payload(payload):
            raise RuntimeError(f"blocked_corrupt_package_137_payload:{table}")
        return payload

    @staticmethod
    def _validate_payload(payload: dict[str, Any]) -> None:
        if _contains_private_absolute_path(payload):
            raise ValueError("Package 137 records cannot persist private absolute paths")

    @staticmethod
    def _require_table(table: str) -> None:
        if table not in TABLE_KEYS:
            raise ValueError(f"unsupported Package 137 table: {table}")

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS package_137_store_metadata (
                    schema_name TEXT PRIMARY KEY,
                    schema_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO package_137_store_metadata (
                    schema_name, schema_version, created_at
                ) VALUES (?, ?, ?)
                """,
                (PACKAGE_DIR, STORE_SCHEMA_VERSION, utc_now()),
            )
            for table in TABLE_KEYS:
                extras = ""
                if table == "self_state_teacher_reviews":
                    extras = ", proposal_id TEXT NOT NULL UNIQUE"
                elif table in {
                    "self_state_mutation_commit_intents",
                    "self_state_mutation_commit_receipts",
                }:
                    extras = ", review_id TEXT NOT NULL UNIQUE"
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


def package_137_store_path(state_dir: str | Path) -> Path:
    return Path(state_dir) / PACKAGE_DIR / DATABASE_NAME


def _contains_private_absolute_path(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_contains_private_absolute_path(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_private_absolute_path(item) for item in value)
    if isinstance(value, str):
        return value.startswith("/") or bool(_WINDOWS_ABSOLUTE_PATH.match(value))
    return False
