"""Append-only State Engine store for Package 133 representation records."""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator

from ashl_core_v1.runtime.host_sensor_types import canonical_json, plain, sha256_payload, utc_now
from ashl_core_v1.state.persistent_self_state_lineage import (
    validate_persistent_self_state_lineage,
)
from ashl_core_v1.state.persistent_self_state_schema import (
    PersistentSelfStateLineageValidationRecord,
    PersistentSelfStateRecord,
    PersistentSelfStateTransitionRecord,
)


PACKAGE_DIR = "package_133_cross_session_self_state_schema_v0"
DATABASE_NAME = "package_133.sqlite3"
STORE_SCHEMA_VERSION = "ashl_package_133_append_only_self_state_store_v0"

GENERIC_TABLE_KEYS = {
    "state_like_structure_boundary_records": "boundary_record_id",
    "persistent_self_state_representation_contracts": "contract_id",
    "package_133_boundary_control_results": "control_result_id",
    "package_133_regression_receipts": "regression_receipt_id",
    "package_133_audits": "audit_id",
}

ALL_TABLES = (
    *GENERIC_TABLE_KEYS,
    "persistent_self_state_records",
    "persistent_self_state_transition_records",
    "persistent_self_state_lineage_validations",
)

_WINDOWS_ABSOLUTE_PATH = re.compile(r"^[A-Za-z]:[\\/]")


class PersistentSelfStateStore:
    """Dedicated State Engine extension with no active-head or recovery API."""

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

    def append_generic_record(self, table: str, record: Any) -> None:
        if table not in GENERIC_TABLE_KEYS:
            raise ValueError(f"unsupported Package 133 generic table: {table}")
        payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        key = GENERIC_TABLE_KEYS[table]
        self._append_payload(table, str(payload[key]), payload)

    def append_inventory(self, records: Iterable[Any]) -> None:
        for record in records:
            self.append_generic_record("state_like_structure_boundary_records", record)

    def append_lineage_chain(
        self,
        *,
        parent: PersistentSelfStateRecord,
        child: PersistentSelfStateRecord,
        transition: PersistentSelfStateTransitionRecord,
        validation: PersistentSelfStateLineageValidationRecord,
    ) -> None:
        lineage = validate_persistent_self_state_lineage(parent, child, transition)
        if not lineage["valid"] or not validation.lineage_valid:
            raise ValueError("cannot persist an invalid self-state lineage")
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._insert_state(connection, parent)
            self._insert_state(connection, child)
            self._insert_typed_payload(
                connection,
                "persistent_self_state_transition_records",
                transition.transition_id,
                transition.to_dict(),
                extra=(
                    transition.self_state_lineage_id,
                    transition.parent_self_state_record_id,
                    transition.child_self_state_record_id,
                ),
            )
            self._insert_typed_payload(
                connection,
                "persistent_self_state_lineage_validations",
                validation.lineage_validation_id,
                validation.to_dict(),
                extra=(
                    validation.self_state_lineage_id,
                    validation.parent_self_state_record_id,
                    validation.child_self_state_record_id,
                    validation.transition_id,
                ),
            )
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
                (record_id,),
            ).fetchone()
        return row is not None

    def audit_integrity(self) -> dict[str, Any]:
        failures: list[str] = []
        with self.connection() as connection:
            integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
            table_names = {
                str(row["name"])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
            metadata = connection.execute(
                "SELECT schema_version FROM package_133_store_metadata WHERE schema_name = ?",
                (PACKAGE_DIR,),
            ).fetchone()
            for table in ALL_TABLES:
                rows = connection.execute(
                    f"SELECT record_id, payload_json, payload_sha256 FROM {table} ORDER BY row_id"
                ).fetchall()
                for row in rows:
                    payload = json.loads(str(row["payload_json"]))
                    if str(row["payload_sha256"]) != sha256_payload(payload):
                        failures.append(f"payload_hash_mismatch:{table}:{row['record_id']}")
                    if _contains_private_absolute_path(payload):
                        failures.append(f"private_absolute_path:{table}:{row['record_id']}")
            state_rows = connection.execute(
                "SELECT payload_json FROM persistent_self_state_records ORDER BY self_state_version"
            ).fetchall()
            transition_rows = connection.execute(
                "SELECT payload_json FROM persistent_self_state_transition_records ORDER BY row_id"
            ).fetchall()
        states: dict[str, PersistentSelfStateRecord] = {}
        for row in state_rows:
            try:
                state = PersistentSelfStateRecord.from_dict(json.loads(str(row["payload_json"])))
                states[state.self_state_record_id] = state
            except (KeyError, TypeError, ValueError) as error:
                failures.append(f"invalid_self_state_record:{error}")
        for row in transition_rows:
            try:
                transition = PersistentSelfStateTransitionRecord.from_dict(
                    json.loads(str(row["payload_json"]))
                )
                parent = states[transition.parent_self_state_record_id]
                child = states[transition.child_self_state_record_id]
                if not validate_persistent_self_state_lineage(parent, child, transition)["valid"]:
                    failures.append(f"invalid_persisted_lineage:{transition.transition_id}")
            except (KeyError, TypeError, ValueError) as error:
                failures.append(f"invalid_transition_record:{error}")
        forbidden_tables = {
            "active_self_state_head",
            "self_state_recovery_sessions",
            "self_state_behavior_influences",
            "self_state_drive_signals",
        }
        if table_names.intersection(forbidden_tables):
            failures.append("forbidden_authority_table_present")
        valid = all(
            (
                integrity == "ok",
                set(ALL_TABLES).issubset(table_names),
                metadata is not None,
                not failures,
            )
        )
        return {
            "valid": valid,
            "integrity_check": integrity,
            "schema_version": str(metadata["schema_version"]) if metadata else None,
            "active_head_present": "active_self_state_head" in table_names,
            "recovery_table_present": "self_state_recovery_sessions" in table_names,
            "failure_reasons": tuple(failures),
        }

    def update(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("PersistentSelfStateStore is append-only; update is forbidden")

    def delete(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("PersistentSelfStateStore is append-only; delete is forbidden")

    def replace(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("PersistentSelfStateStore is append-only; replace is forbidden")

    def recover(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 133 does not implement cross-session recovery")

    def select_active_head(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 133 does not create active self-state authority")

    def _append_payload(self, table: str, record_id: str, payload: dict[str, Any]) -> None:
        if _contains_private_absolute_path(payload):
            raise ValueError("Package 133 records cannot persist private absolute paths")
        serialized = canonical_json(plain(payload))
        payload_hash = sha256_payload(plain(payload))
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._insert_or_verify(
                connection,
                table,
                record_id,
                str(payload.get("created_at", utc_now())),
                serialized,
                payload_hash,
            )
            connection.commit()

    def _insert_state(
        self,
        connection: sqlite3.Connection,
        state: PersistentSelfStateRecord,
    ) -> None:
        payload = state.to_dict()
        if _contains_private_absolute_path(payload):
            raise ValueError("self-state record contains a private absolute path")
        serialized = canonical_json(payload)
        payload_hash = sha256_payload(payload)
        existing = connection.execute(
            "SELECT payload_sha256 FROM persistent_self_state_records WHERE record_id = ?",
            (state.self_state_record_id,),
        ).fetchone()
        if existing is not None:
            if str(existing["payload_sha256"]) != payload_hash:
                raise ValueError("self-state record identity collision")
            return
        if state.parent_self_state_record_id is not None:
            parent = connection.execute(
                "SELECT record_id, self_state_sha256 FROM persistent_self_state_records WHERE record_id = ?",
                (state.parent_self_state_record_id,),
            ).fetchone()
            if parent is None or str(parent["self_state_sha256"]) != state.parent_self_state_sha256:
                raise ValueError("self-state parent must exist with the exact hash before child append")
            fork = connection.execute(
                "SELECT record_id FROM persistent_self_state_records WHERE parent_self_state_record_id = ?",
                (state.parent_self_state_record_id,),
            ).fetchone()
            if fork is not None:
                raise ValueError("Package 133 lineage fork is forbidden")
        try:
            connection.execute(
                """
                INSERT INTO persistent_self_state_records (
                    record_id, created_at, self_state_lineage_id, self_state_version,
                    lineage_generation, parent_self_state_record_id,
                    self_state_sha256, source_session_id, payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.self_state_record_id,
                    state.created_at,
                    state.self_state_lineage_id,
                    state.self_state_version,
                    state.lineage_generation,
                    state.parent_self_state_record_id,
                    state.self_state_sha256,
                    state.source_session_id,
                    serialized,
                    payload_hash,
                ),
            )
        except sqlite3.IntegrityError as error:
            raise ValueError("persistent self-state append-only constraint failed") from error

    def _insert_typed_payload(
        self,
        connection: sqlite3.Connection,
        table: str,
        record_id: str,
        payload: dict[str, Any],
        *,
        extra: tuple[str, ...],
    ) -> None:
        if _contains_private_absolute_path(payload):
            raise ValueError("Package 133 typed record contains a private absolute path")
        serialized = canonical_json(payload)
        payload_hash = sha256_payload(payload)
        existing = connection.execute(
            f"SELECT payload_sha256 FROM {table} WHERE record_id = ?",
            (record_id,),
        ).fetchone()
        if existing is not None:
            if str(existing["payload_sha256"]) != payload_hash:
                raise ValueError(f"Package 133 identity collision: {record_id}")
            return
        placeholders = ", ".join("?" for _item in extra)
        columns = {
            "persistent_self_state_transition_records": (
                "self_state_lineage_id, parent_self_state_record_id, child_self_state_record_id"
            ),
            "persistent_self_state_lineage_validations": (
                "self_state_lineage_id, parent_self_state_record_id, child_self_state_record_id, transition_id"
            ),
        }[table]
        try:
            connection.execute(
                f"""
                INSERT INTO {table} (
                    record_id, created_at, {columns}, payload_json, payload_sha256
                ) VALUES (?, ?, {placeholders}, ?, ?)
                """,
                (
                    record_id,
                    str(payload["created_at"]),
                    *extra,
                    serialized,
                    payload_hash,
                ),
            )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"Package 133 typed append constraint failed: {record_id}") from error

    @staticmethod
    def _insert_or_verify(
        connection: sqlite3.Connection,
        table: str,
        record_id: str,
        created_at: str,
        serialized: str,
        payload_hash: str,
    ) -> None:
        existing = connection.execute(
            f"SELECT payload_sha256 FROM {table} WHERE record_id = ?",
            (record_id,),
        ).fetchone()
        if existing is not None:
            if str(existing["payload_sha256"]) != payload_hash:
                raise ValueError(f"Package 133 identity collision: {record_id}")
            return
        connection.execute(
            f"""
            INSERT INTO {table} (record_id, created_at, payload_json, payload_sha256)
            VALUES (?, ?, ?, ?)
            """,
            (record_id, created_at, serialized, payload_hash),
        )

    def _require_table(self, table: str) -> None:
        if table not in ALL_TABLES:
            raise ValueError(f"unsupported Package 133 table: {table}")

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS package_133_store_metadata (
                    schema_name TEXT PRIMARY KEY,
                    schema_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO package_133_store_metadata (
                    schema_name, schema_version, created_at
                ) VALUES (?, ?, ?)
                """,
                (PACKAGE_DIR, STORE_SCHEMA_VERSION, utc_now()),
            )
            for table in GENERIC_TABLE_KEYS:
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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS persistent_self_state_records (
                    row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    self_state_lineage_id TEXT NOT NULL,
                    self_state_version INTEGER NOT NULL,
                    lineage_generation INTEGER NOT NULL,
                    parent_self_state_record_id TEXT UNIQUE,
                    self_state_sha256 TEXT NOT NULL,
                    source_session_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    UNIQUE(self_state_lineage_id, self_state_version),
                    FOREIGN KEY(parent_self_state_record_id)
                        REFERENCES persistent_self_state_records(record_id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS persistent_self_state_transition_records (
                    row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    self_state_lineage_id TEXT NOT NULL,
                    parent_self_state_record_id TEXT NOT NULL UNIQUE,
                    child_self_state_record_id TEXT NOT NULL UNIQUE,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    FOREIGN KEY(parent_self_state_record_id)
                        REFERENCES persistent_self_state_records(record_id),
                    FOREIGN KEY(child_self_state_record_id)
                        REFERENCES persistent_self_state_records(record_id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS persistent_self_state_lineage_validations (
                    row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    self_state_lineage_id TEXT NOT NULL,
                    parent_self_state_record_id TEXT NOT NULL,
                    child_self_state_record_id TEXT NOT NULL,
                    transition_id TEXT NOT NULL UNIQUE,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    FOREIGN KEY(parent_self_state_record_id)
                        REFERENCES persistent_self_state_records(record_id),
                    FOREIGN KEY(child_self_state_record_id)
                        REFERENCES persistent_self_state_records(record_id),
                    FOREIGN KEY(transition_id)
                        REFERENCES persistent_self_state_transition_records(record_id)
                )
                """
            )
            connection.commit()


def package_133_store_path(state_dir: str | Path) -> Path:
    return Path(state_dir) / PACKAGE_DIR / DATABASE_NAME


def _contains_private_absolute_path(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_contains_private_absolute_path(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_private_absolute_path(item) for item in value)
    if isinstance(value, str):
        return value.startswith("/") or bool(_WINDOWS_ABSOLUTE_PATH.match(value))
    return False
