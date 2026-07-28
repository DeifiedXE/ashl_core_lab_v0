"""External append-only store and generated Q-M0 report bundle."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from ashl_core_v1.migration_audit.d_laplace_qm0_types import (
    canonical_json,
    plain,
    sha256_payload,
    utc_now,
)


STORE_DIRNAME = "d_laplace_qm0_read_only_migration_audit_v0"
STORE_FILENAME = "qm0_audit.sqlite3"


class DLaplaceQM0Store:
    def __init__(self, state_dir: str | Path) -> None:
        if state_dir is None:
            raise ValueError("explicit external state_dir is required")
        self.state_dir = Path(state_dir).resolve()
        self.root_dir = self.state_dir / STORE_DIRNAME
        self.db_path = self.root_dir / STORE_FILENAME
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(str(self.db_path))
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_records (
                    sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_type TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS audit_records_type_sequence
                ON audit_records(record_type, sequence_id)
                """
            )

    def append(
        self,
        record_type: str,
        record_id: str,
        payload: object,
    ) -> None:
        normalized = plain(payload)
        payload_json = canonical_json(normalized)
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO audit_records (
                    record_type,
                    record_id,
                    created_at,
                    payload_sha256,
                    payload_json
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record_type,
                    record_id,
                    utc_now(),
                    sha256_payload(normalized),
                    payload_json,
                ),
            )

    def append_many(
        self,
        record_type: str,
        rows: list[tuple[str, object]] | tuple[tuple[str, object], ...],
    ) -> None:
        values = []
        for record_id, payload in rows:
            normalized = plain(payload)
            values.append(
                (
                    record_type,
                    record_id,
                    utc_now(),
                    sha256_payload(normalized),
                    canonical_json(normalized),
                )
            )
        with self.connection() as connection:
            connection.executemany(
                """
                INSERT INTO audit_records (
                    record_type,
                    record_id,
                    created_at,
                    payload_sha256,
                    payload_json
                ) VALUES (?, ?, ?, ?, ?)
                """,
                values,
            )

    def latest(self, record_type: str) -> dict[str, Any] | None:
        with self.connection() as connection:
            row = connection.execute(
                """
                SELECT payload_json
                FROM audit_records
                WHERE record_type = ?
                ORDER BY sequence_id DESC
                LIMIT 1
                """,
                (record_type,),
            ).fetchone()
        return json.loads(row[0]) if row else None

    def write_json(self, filename: str, payload: object) -> Path:
        if Path(filename).name != filename or not filename.endswith(".json"):
            raise ValueError("generated report filename must be a simple JSON name")
        path = self.root_dir / filename
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(
                plain(payload),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
        return path

    def read_json(self, filename: str) -> dict[str, Any] | list[Any]:
        path = self.root_dir / filename
        return json.loads(path.read_text(encoding="utf-8"))
