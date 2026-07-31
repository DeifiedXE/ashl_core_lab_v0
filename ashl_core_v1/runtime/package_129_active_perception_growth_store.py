"""Append-only external SQLite store for Package 129."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from ashl_core_v1.runtime.host_sensor_types import canonical_json, plain


PACKAGE_DIR = "package_129_active_perception_growth_v0"
DATABASE_NAME = "package_129.sqlite3"

TABLE_KEYS = {
    "active_perception_stage_records": "stage_record_id",
    "active_perception_cycle_records": "cycle_record_id",
    "active_perception_readback_load_timing": "timing_record_id",
    "active_perception_readback_influence": "influence_record_id",
    "active_perception_cycle2_review_preservation": "preservation_record_id",
    "active_perception_two_cycle_comparisons": "comparison_id",
    "active_perception_process_receipts": "process_receipt_id",
    "active_perception_control_results": "control_result_id",
    "active_perception_fixture_manifests": "fixture_manifest_id",
    "active_perception_event_delivery_failures": "event_delivery_failure_id",
    "package_129_audits": "audit_id",
}


class Package129ActivePerceptionGrowthStore:
    def __init__(self, state_dir: str | Path) -> None:
        self.state_dir = Path(state_dir)
        self.root = self.state_dir / PACKAGE_DIR
        self.root.mkdir(parents=True, exist_ok=True)
        self.database_path = self.root / DATABASE_NAME
        self._initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()

    def append_record(self, table: str, record: Any) -> None:
        payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        key = TABLE_KEYS[table]
        self.append_payload(table, key, str(payload[key]), payload)

    def append_payload(
        self,
        table: str,
        key_name: str,
        record_id: str,
        payload: dict[str, Any],
    ) -> None:
        if table not in TABLE_KEYS or TABLE_KEYS[table] != key_name:
            raise ValueError(f"unsupported Package 129 table/key: {table}/{key_name}")
        serialized = canonical_json(plain(payload))
        with self.connection() as connection:
            try:
                connection.execute(
                    f"""
                    INSERT INTO {table} (record_id, payload_json)
                    VALUES (?, ?)
                    """,
                    (str(record_id), serialized),
                )
            except sqlite3.IntegrityError as error:
                raise ValueError(
                    f"append-only Package 129 record already exists: {record_id}"
                ) from error
            connection.commit()

    def list_payloads(self, table: str) -> tuple[dict[str, Any], ...]:
        if table not in TABLE_KEYS:
            raise ValueError(f"unsupported Package 129 table: {table}")
        with self.connection() as connection:
            rows = connection.execute(
                f"SELECT payload_json FROM {table} ORDER BY rowid"
            ).fetchall()
        return tuple(json.loads(str(row["payload_json"])) for row in rows)

    def latest_payload(self, table: str) -> dict[str, Any] | None:
        if table not in TABLE_KEYS:
            raise ValueError(f"unsupported Package 129 table: {table}")
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
        return json.loads(str(row["payload_json"])) if row else None

    def get_payload(self, table: str, record_id: str) -> dict[str, Any]:
        if table not in TABLE_KEYS:
            raise ValueError(f"unsupported Package 129 table: {table}")
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} WHERE record_id = ?",
                (str(record_id),),
            ).fetchone()
        if row is None:
            raise KeyError(record_id)
        return json.loads(str(row["payload_json"]))

    def latest_cycle(self, cycle_index: int) -> dict[str, Any] | None:
        matches = tuple(
            item
            for item in self.list_payloads("active_perception_cycle_records")
            if int(item.get("cycle_index", 0)) == int(cycle_index)
        )
        return matches[-1] if matches else None

    def count(self, table: str) -> int:
        if table not in TABLE_KEYS:
            raise ValueError(f"unsupported Package 129 table: {table}")
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT COUNT(*) AS count FROM {table}"
            ).fetchone()
        return int(row["count"])

    def _initialize(self) -> None:
        with self.connection() as connection:
            for table in TABLE_KEYS:
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                        record_id TEXT PRIMARY KEY,
                        payload_json TEXT NOT NULL
                    )
                    """
                )
            connection.commit()
