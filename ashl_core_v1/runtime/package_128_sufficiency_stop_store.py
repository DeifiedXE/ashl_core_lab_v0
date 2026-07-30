"""Append-only external-state store for Package 128."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import (
    canonical_json,
    sha256_payload,
    utc_now,
)


PACKAGE_128_DIRNAME = "package_128_evidence_sufficiency_stop_v0"
PACKAGE_128_FILENAME = "package_128.sqlite3"

TABLE_ID_COLUMNS = {
    "structural_sufficiency_contracts": "contract_id",
    "structural_evidence_checkpoints": "checkpoint_id",
    "structural_evidence_assessments": "assessment_id",
    "observation_stop_policy_decisions": "policy_decision_id",
    "stop_observation_internal_actions": "internal_action_id",
    "observation_stop_executions": "stop_execution_id",
    "observation_completion_records": "completion_record_id",
    "package_128_score_equivalence_records": "score_equivalence_record_id",
    "package_128_control_results": "control_result_id",
    "package_128_real_run_records": "real_run_record_id",
    "operator_event_delivery_failures": "event_delivery_failure_id",
    "package_128_audits": "audit_id",
}


class Package128SufficiencyStopStore:
    def __init__(self, state_dir: str | Path) -> None:
        if state_dir is None:
            raise ValueError("explicit external state_dir is required")
        self.state_dir = Path(state_dir)
        self.root_dir = self.state_dir / PACKAGE_128_DIRNAME
        self.db_path = self.root_dir / PACKAGE_128_FILENAME
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
        payload = (
            record.to_dict()
            if hasattr(record, "to_dict")
            else dict(record)
        )
        id_column = self._id_column(table)
        self.append_payload(
            table,
            id_column,
            str(payload[id_column]),
            payload,
        )

    def append_payload(
        self,
        table: str,
        id_column: str,
        record_id: str,
        payload: dict[str, Any],
    ) -> None:
        if id_column != self._id_column(table):
            raise ValueError("Package 128 id column mismatch")
        with self.connection() as connection:
            connection.execute(
                f"""
                INSERT INTO {table} (
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
        self._id_column(table)
        with self.connection() as connection:
            rows = connection.execute(
                f"SELECT payload_json FROM {table} ORDER BY rowid ASC"
            ).fetchall()
        return tuple(
            dict(json.loads(str(row["payload_json"]))) for row in rows
        )

    def get_payload(self, table: str, record_id: str) -> dict[str, Any]:
        id_column = self._id_column(table)
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} WHERE {id_column} = ?",
                (record_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"missing Package 128 record: {record_id}")
        return dict(json.loads(str(row["payload_json"])))

    def latest_payload(self, table: str) -> dict[str, Any] | None:
        self._id_column(table)
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} "
                "ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
        return dict(json.loads(str(row["payload_json"]))) if row else None

    def counts(self) -> dict[str, int]:
        result: dict[str, int] = {}
        with self.connection() as connection:
            for table in TABLE_ID_COLUMNS:
                row = connection.execute(
                    f"SELECT COUNT(*) AS count FROM {table}"
                ).fetchone()
                result[table] = int(row["count"])
        return result

    def validate_schema(self) -> dict[str, object]:
        with self.connection() as connection:
            tables = {
                str(row["name"])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
        missing = tuple(sorted(set(TABLE_ID_COLUMNS) - tables))
        return {
            "valid": not missing,
            "missing_tables": missing,
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
                INSERT OR IGNORE INTO store_metadata (
                    schema_name, schema_version, created_at
                ) VALUES (?, ?, ?)
                """,
                (
                    "ashl_package_128_sufficiency_stop_store",
                    "v0",
                    utc_now(),
                ),
            )
            for table, id_column in TABLE_ID_COLUMNS.items():
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                        {id_column} TEXT PRIMARY KEY,
                        created_at TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        payload_sha256 TEXT NOT NULL
                    )
                    """
                )

    @staticmethod
    def _id_column(table: str) -> str:
        try:
            return TABLE_ID_COLUMNS[table]
        except KeyError as error:
            raise ValueError(
                f"unknown Package 128 table: {table}"
            ) from error
