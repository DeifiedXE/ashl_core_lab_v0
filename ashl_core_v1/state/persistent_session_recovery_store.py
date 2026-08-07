"""Package 134 active-head authority and append-only recovery audit store."""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from ashl_core_v1.runtime.host_sensor_types import canonical_json, plain, sha256_payload, utc_now
from ashl_core_v1.state.persistent_session_recovery_types import (
    ActiveSelfStateHeadRecord,
    PersistentSessionRecoveryAuthorization,
)


PACKAGE_DIR = "package_134_persistent_session_recovery_v0"
DATABASE_NAME = "package_134.sqlite3"
STORE_SCHEMA_VERSION = "ashl_package_134_active_head_and_audit_store_v0"

TABLE_KEYS = {
    "package_133_source_snapshots": "source_snapshot_id",
    "persistent_session_recovery_authorizations": "authorization_id",
    "recovery_authorization_consumptions": "consumption_id",
    "active_head_cas_events": "cas_event_id",
    "persistent_session_identity_bindings": "binding_id",
    "persistent_session_shutdown_records": "shutdown_record_id",
    "persistent_session_recovery_resolutions": "resolution_id",
    "persistent_session_recovery_process_receipts": "process_receipt_id",
    "persistent_session_recovery_pairs": "recovery_pair_id",
    "package_134_recovery_control_results": "control_result_id",
    "package_134_regression_receipts": "regression_receipt_id",
    "package_134_audits": "audit_id",
}

_WINDOWS_ABSOLUTE_PATH = re.compile(r"^[A-Za-z]:[\\/]")


class ActiveHeadCASConflict(RuntimeError):
    """Raised when an active-head compare-and-swap loses its exact expectation."""


class PersistentSessionRecoveryStore:
    """Separate mutable head pointer plus immutable recovery history."""

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

    def append_record(self, table: str, record: Any) -> None:
        if table not in TABLE_KEYS:
            raise ValueError(f"unsupported Package 134 table: {table}")
        payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        record_id = str(payload[TABLE_KEYS[table]])
        self._validate_payload(payload)
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._insert_append_only(connection, table, record_id, payload)
            connection.commit()

    def append_once(self, table: str, record: Any) -> None:
        payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        record_id = str(payload[TABLE_KEYS[table]])
        if not self.has_record(table, record_id):
            self.append_record(table, record)

    def has_record(self, table: str, record_id: str) -> bool:
        self._require_table(table)
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT 1 FROM {table} WHERE record_id = ? LIMIT 1",
                (record_id,),
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

    def get_authorization(
        self, authorization_id: str
    ) -> PersistentSessionRecoveryAuthorization:
        return PersistentSessionRecoveryAuthorization.from_dict(
            self.get_payload("persistent_session_recovery_authorizations", authorization_id)
        )

    def authorization_consumed(self, authorization_id: str) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM recovery_authorization_consumptions WHERE authorization_id = ? LIMIT 1",
                (authorization_id,),
            ).fetchone()
        return row is not None

    def get_active_head(self) -> ActiveSelfStateHeadRecord:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT payload_json, payload_sha256 FROM active_self_state_head"
            ).fetchall()
        if not rows:
            raise RuntimeError("blocked_missing_active_head")
        if len(rows) != 1:
            raise RuntimeError("blocked_ambiguous_active_head")
        try:
            payload = self._verified_payload(rows[0], "active_self_state_head")
            return ActiveSelfStateHeadRecord.from_dict(payload)
        except (KeyError, TypeError, ValueError, RuntimeError) as error:
            raise RuntimeError("blocked_corrupt_active_head") from error

    def active_head_count(self) -> int:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM active_self_state_head"
            ).fetchone()
        return int(row["count"])

    def initialize_active_head_atomic(
        self,
        *,
        authorization: PersistentSessionRecoveryAuthorization,
        active_head: ActiveSelfStateHeadRecord,
        cas_event: Any,
        consumption: Any,
        identity_binding: Any,
    ) -> None:
        if authorization.operation != "initialize_active_head":
            raise ValueError("active-head initialization authorization required")
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._require_authorization_available(connection, authorization)
            existing = int(
                connection.execute(
                    "SELECT COUNT(*) FROM active_self_state_head"
                ).fetchone()[0]
            )
            if existing:
                raise ActiveHeadCASConflict("blocked_active_head_already_initialized")
            payload = active_head.to_dict()
            self._validate_payload(payload)
            connection.execute(
                """
                INSERT INTO active_self_state_head (
                    singleton_key, active_head_id, head_revision,
                    self_state_lineage_id, self_state_record_id,
                    bound_session_id, bound_process_instance_id,
                    payload_json, payload_sha256, updated_at
                ) VALUES ('active', ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    active_head.active_head_id,
                    active_head.head_revision,
                    active_head.self_state_lineage_id,
                    active_head.self_state_record_id,
                    active_head.bound_session_id,
                    active_head.bound_process_instance_id,
                    canonical_json(payload),
                    sha256_payload(payload),
                    active_head.updated_at,
                ),
            )
            self._insert_typed_group(
                connection,
                (
                    ("active_head_cas_events", cas_event),
                    ("recovery_authorization_consumptions", consumption),
                    ("persistent_session_identity_bindings", identity_binding),
                ),
            )
            connection.commit()

    def recover_active_head_atomic(
        self,
        *,
        authorization: PersistentSessionRecoveryAuthorization,
        expected_head: ActiveSelfStateHeadRecord,
        new_head: ActiveSelfStateHeadRecord,
        cas_event: Any,
        consumption: Any,
        identity_binding: Any,
        resolution: Any,
        fault_injection: str | None = None,
    ) -> None:
        if authorization.operation != "recover_session":
            raise ValueError("session recovery authorization required")
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._require_authorization_available(connection, authorization)
            row = connection.execute(
                "SELECT head_revision, payload_sha256, payload_json FROM active_self_state_head WHERE singleton_key = 'active'"
            ).fetchone()
            if row is None:
                raise ActiveHeadCASConflict("blocked_missing_active_head")
            current_payload = self._verified_payload(row, "active_self_state_head")
            current = ActiveSelfStateHeadRecord.from_dict(current_payload)
            if (
                current.head_revision != expected_head.head_revision
                or current.active_head_sha256 != expected_head.active_head_sha256
                or current.bound_session_id != expected_head.bound_session_id
            ):
                raise ActiveHeadCASConflict("blocked_active_head_cas_conflict")
            new_payload = new_head.to_dict()
            self._validate_payload(new_payload)
            result = connection.execute(
                """
                UPDATE active_self_state_head
                SET head_revision = ?, bound_session_id = ?,
                    bound_process_instance_id = ?, payload_json = ?,
                    payload_sha256 = ?, updated_at = ?
                WHERE singleton_key = 'active' AND head_revision = ? AND payload_sha256 = ?
                """,
                (
                    new_head.head_revision,
                    new_head.bound_session_id,
                    new_head.bound_process_instance_id,
                    canonical_json(new_payload),
                    sha256_payload(new_payload),
                    new_head.updated_at,
                    expected_head.head_revision,
                    sha256_payload(expected_head.to_dict()),
                ),
            )
            if result.rowcount != 1:
                raise ActiveHeadCASConflict("blocked_active_head_cas_conflict")
            self._insert_typed_group(
                connection,
                (
                    ("active_head_cas_events", cas_event),
                    ("recovery_authorization_consumptions", consumption),
                    ("persistent_session_identity_bindings", identity_binding),
                    ("persistent_session_recovery_resolutions", resolution),
                ),
            )
            if fault_injection == "after_head_update_before_commit":
                raise RuntimeError("simulated_partial_write_before_commit")
            if fault_injection is not None:
                raise ValueError("unknown Package 134 fault injection")
            connection.commit()

    def advance_reviewed_successor_atomic(
        self,
        *,
        review_id: str,
        expected_head: ActiveSelfStateHeadRecord,
        new_head: ActiveSelfStateHeadRecord,
        cas_event: Any,
        fault_injection: str | None = None,
    ) -> None:
        """Advance only to one exact reviewed Package 133 successor."""
        if not review_id:
            raise ValueError("review_id is required for reviewed-successor CAS")
        if cas_event.operation != "advance_reviewed_self_state_successor":
            raise ValueError("reviewed-successor CAS event operation is required")
        if cas_event.authorization_id != review_id:
            raise ValueError("reviewed-successor CAS review binding mismatch")
        if new_head.active_head_id != expected_head.active_head_id:
            raise ValueError("reviewed-successor CAS cannot replace active-head identity")
        if new_head.self_state_lineage_id != expected_head.self_state_lineage_id:
            raise ValueError("reviewed-successor CAS cannot change self-state lineage")
        if new_head.self_state_record_id == expected_head.self_state_record_id:
            raise ValueError("reviewed-successor CAS requires a distinct successor")
        if new_head.self_state_version != expected_head.self_state_version + 1:
            raise ValueError("reviewed-successor CAS version must increment exactly once")
        if new_head.lineage_generation != expected_head.lineage_generation + 1:
            raise ValueError("reviewed-successor CAS generation must increment exactly once")
        if new_head.head_revision != expected_head.head_revision + 1:
            raise ValueError("reviewed-successor CAS head revision must increment exactly once")
        if new_head.previous_active_head_sha256 != expected_head.active_head_sha256:
            raise ValueError("reviewed-successor CAS previous-head hash mismatch")
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            prior_events = connection.execute(
                "SELECT payload_json FROM active_head_cas_events ORDER BY row_id"
            ).fetchall()
            if any(
                json.loads(str(row["payload_json"])).get("authorization_id") == review_id
                for row in prior_events
            ):
                raise ActiveHeadCASConflict("blocked_teacher_review_already_consumed")
            row = connection.execute(
                "SELECT payload_json, payload_sha256 FROM active_self_state_head WHERE singleton_key = 'active'"
            ).fetchone()
            if row is None:
                raise ActiveHeadCASConflict("blocked_missing_active_head")
            current = ActiveSelfStateHeadRecord.from_dict(
                self._verified_payload(row, "active_self_state_head")
            )
            if (
                current.active_head_id != expected_head.active_head_id
                or current.active_head_sha256 != expected_head.active_head_sha256
                or current.head_revision != expected_head.head_revision
                or current.self_state_record_id != expected_head.self_state_record_id
                or current.self_state_sha256 != expected_head.self_state_sha256
            ):
                raise ActiveHeadCASConflict("blocked_active_head_cas_conflict")
            if fault_injection == "force_cas_conflict":
                raise ActiveHeadCASConflict("blocked_active_head_cas_conflict")
            new_payload = new_head.to_dict()
            self._validate_payload(new_payload)
            result = connection.execute(
                """
                UPDATE active_self_state_head
                SET head_revision = ?, self_state_lineage_id = ?,
                    self_state_record_id = ?, bound_session_id = ?,
                    bound_process_instance_id = ?, payload_json = ?,
                    payload_sha256 = ?, updated_at = ?
                WHERE singleton_key = 'active' AND head_revision = ? AND payload_sha256 = ?
                """,
                (
                    new_head.head_revision,
                    new_head.self_state_lineage_id,
                    new_head.self_state_record_id,
                    new_head.bound_session_id,
                    new_head.bound_process_instance_id,
                    canonical_json(new_payload),
                    sha256_payload(new_payload),
                    new_head.updated_at,
                    expected_head.head_revision,
                    sha256_payload(expected_head.to_dict()),
                ),
            )
            if result.rowcount != 1:
                raise ActiveHeadCASConflict("blocked_active_head_cas_conflict")
            self._insert_typed_group(
                connection,
                (("active_head_cas_events", cas_event),),
            )
            if fault_injection == "after_head_update_before_commit":
                raise RuntimeError("simulated_reviewed_successor_partial_write_before_commit")
            if fault_injection not in {None, "force_cas_conflict"}:
                raise ValueError("unknown reviewed-successor CAS fault injection")
            connection.commit()

    def append_blocked_recovery_attempt(
        self,
        *,
        cas_event: Any,
        consumption: Any,
        resolution: Any,
    ) -> None:
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._insert_typed_group(
                connection,
                (
                    ("active_head_cas_events", cas_event),
                    ("recovery_authorization_consumptions", consumption),
                    ("persistent_session_recovery_resolutions", resolution),
                ),
            )
            connection.commit()

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
                "SELECT schema_version FROM package_134_store_metadata WHERE schema_name = ?",
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
            head_rows = connection.execute(
                "SELECT payload_json, payload_sha256 FROM active_self_state_head"
            ).fetchall()
        for row in head_rows:
            try:
                ActiveSelfStateHeadRecord.from_dict(
                    self._verified_payload(row, "active_self_state_head")
                )
            except (KeyError, TypeError, ValueError, RuntimeError) as error:
                failures.append(f"invalid_active_head:{error}")
        valid = all(
            (
                integrity == "ok",
                set(TABLE_KEYS).issubset(tables),
                "active_self_state_head" in tables,
                metadata is not None,
                len(head_rows) <= 1,
                not failures,
            )
        )
        return {
            "valid": valid,
            "integrity_check": integrity,
            "schema_version": str(metadata["schema_version"]) if metadata else None,
            "active_head_count": len(head_rows),
            "history_tables_append_only": True,
            "active_head_separate_from_history": True,
            "failure_reasons": tuple(failures),
        }

    def update_history(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 134 history is append-only")

    def delete_history(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("Package 134 history is append-only")

    def _require_authorization_available(
        self,
        connection: sqlite3.Connection,
        authorization: PersistentSessionRecoveryAuthorization,
    ) -> None:
        row = connection.execute(
            "SELECT payload_json, payload_sha256 FROM persistent_session_recovery_authorizations WHERE record_id = ?",
            (authorization.authorization_id,),
        ).fetchone()
        if row is None:
            raise RuntimeError("blocked_recovery_authorization_missing")
        persisted = PersistentSessionRecoveryAuthorization.from_dict(
            self._verified_payload(row, "persistent_session_recovery_authorizations")
        )
        if persisted != authorization:
            raise RuntimeError("blocked_recovery_authorization_identity_mismatch")
        consumed = connection.execute(
            "SELECT 1 FROM recovery_authorization_consumptions WHERE authorization_id = ? LIMIT 1",
            (authorization.authorization_id,),
        ).fetchone()
        if consumed is not None:
            raise RuntimeError("blocked_recovery_authorization_already_consumed")

    def _insert_typed_group(
        self,
        connection: sqlite3.Connection,
        records: tuple[tuple[str, Any], ...],
    ) -> None:
        for table, record in records:
            payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
            self._insert_append_only(
                connection,
                table,
                str(payload[TABLE_KEYS[table]]),
                payload,
            )

    def _insert_append_only(
        self,
        connection: sqlite3.Connection,
        table: str,
        record_id: str,
        payload: dict[str, Any],
    ) -> None:
        self._require_table(table)
        self._validate_payload(payload)
        try:
            if table == "recovery_authorization_consumptions":
                connection.execute(
                    """
                    INSERT INTO recovery_authorization_consumptions (
                        record_id, authorization_id, created_at, payload_json, payload_sha256
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        record_id,
                        str(payload["authorization_id"]),
                        str(payload.get("created_at", utc_now())),
                        canonical_json(plain(payload)),
                        sha256_payload(plain(payload)),
                    ),
                )
            else:
                connection.execute(
                    f"INSERT INTO {table} (record_id, created_at, payload_json, payload_sha256) VALUES (?, ?, ?, ?)",
                    (
                        record_id,
                        str(payload.get("created_at", utc_now())),
                        canonical_json(plain(payload)),
                        sha256_payload(plain(payload)),
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"append-only Package 134 record already exists: {record_id}") from error

    @staticmethod
    def _verified_payload(row: sqlite3.Row, table: str) -> dict[str, Any]:
        payload = json.loads(str(row["payload_json"]))
        if str(row["payload_sha256"]) != sha256_payload(payload):
            raise RuntimeError(f"blocked_corrupt_payload:{table}")
        return payload

    @staticmethod
    def _validate_payload(payload: dict[str, Any]) -> None:
        if _contains_private_absolute_path(payload):
            raise ValueError("Package 134 records cannot persist private absolute paths")

    @staticmethod
    def _require_table(table: str) -> None:
        if table not in TABLE_KEYS:
            raise ValueError(f"unsupported Package 134 table: {table}")

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS package_134_store_metadata (
                    schema_name TEXT PRIMARY KEY,
                    schema_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS active_self_state_head (
                    singleton_key TEXT PRIMARY KEY CHECK(singleton_key = 'active'),
                    active_head_id TEXT NOT NULL UNIQUE,
                    head_revision INTEGER NOT NULL,
                    self_state_lineage_id TEXT NOT NULL,
                    self_state_record_id TEXT NOT NULL,
                    bound_session_id TEXT NOT NULL,
                    bound_process_instance_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO package_134_store_metadata (
                    schema_name, schema_version, created_at
                ) VALUES (?, ?, ?)
                """,
                (PACKAGE_DIR, STORE_SCHEMA_VERSION, utc_now()),
            )
            for table in TABLE_KEYS:
                if table == "recovery_authorization_consumptions":
                    connection.execute(
                        """
                        CREATE TABLE IF NOT EXISTS recovery_authorization_consumptions (
                            row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            record_id TEXT NOT NULL UNIQUE,
                            authorization_id TEXT NOT NULL UNIQUE,
                            created_at TEXT NOT NULL,
                            payload_json TEXT NOT NULL,
                            payload_sha256 TEXT NOT NULL
                        )
                        """
                    )
                else:
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


def package_134_store_path(state_dir: str | Path) -> Path:
    return Path(state_dir) / PACKAGE_DIR / DATABASE_NAME


def _contains_private_absolute_path(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_contains_private_absolute_path(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_private_absolute_path(item) for item in value)
    if isinstance(value, str):
        return value.startswith("/") or bool(_WINDOWS_ABSOLUTE_PATH.match(value))
    return False
