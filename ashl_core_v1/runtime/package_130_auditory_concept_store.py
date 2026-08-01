"""Append-only external SQLite store for Package 130."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from ashl_core_v1.runtime.host_sensor_types import canonical_json, plain


PACKAGE_DIR = "package_130_grounded_auditory_concept_v0"
DATABASE_NAME = "package_130.sqlite3"

TABLE_KEYS = {
    "auditory_grounding_authorizations": "authorization_id",
    "auditory_source_condition_profiles": "source_condition_profile_id",
    "auditory_grounding_episodes": "episode_id",
    "auditory_grounding_example_assignments": "assignment_id",
    "auditory_concept_feature_projections": "feature_projection_id",
    "grounded_auditory_concept_candidates": "concept_candidate_id",
    "expected_audio_primitive_generation_records": "generation_id",
    "auditory_concept_prediction_error_records": "prediction_error_record_id",
    "auditory_concept_predictive_validations": "predictive_validation_id",
    "auditory_concept_maturity_assessments": "maturity_assessment_id",
    "grounded_auditory_event_concept_models": "model_record_id",
    "auditory_concept_contrast_sets": "contrast_set_id",
    "auditory_grounding_raw_audio_deletion_audits": "deletion_audit_id",
    "auditory_grounding_uncommitted_audio_cleanup_records": "cleanup_record_id",
    "auditory_grounding_process_receipts": "process_receipt_id",
    "auditory_grounding_fixture_manifests": "fixture_manifest_id",
    "auditory_concept_teacher_review_targets": "teacher_review_target_id",
    "auditory_concept_teacher_review_outcomes": "teacher_review_outcome_id",
    "auditory_concept_memory_commit_records": "memory_commit_record_id",
    "auditory_concept_control_results": "control_result_id",
    "auditory_concept_operator_events": "event_id",
    "auditory_concept_event_delivery_failures": "event_delivery_failure_id",
    "package_130_audits": "audit_id",
}


class Package130AuditoryConceptStore:
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
        key_name = TABLE_KEYS[table]
        self.append_payload(table, key_name, str(payload[key_name]), payload)

    def append_payload(
        self,
        table: str,
        key_name: str,
        record_id: str,
        payload: dict[str, Any],
    ) -> None:
        if table not in TABLE_KEYS or TABLE_KEYS[table] != key_name:
            raise ValueError(f"unsupported Package 130 table/key: {table}/{key_name}")
        serialized = canonical_json(plain(payload))
        with self.connection() as connection:
            try:
                connection.execute(
                    f"INSERT INTO {table} (record_id, payload_json) VALUES (?, ?)",
                    (str(record_id), serialized),
                )
            except sqlite3.IntegrityError as error:
                raise ValueError(f"append-only Package 130 record already exists: {record_id}") from error
            connection.commit()

    def list_payloads(self, table: str) -> tuple[dict[str, Any], ...]:
        self._require_table(table)
        with self.connection() as connection:
            rows = connection.execute(
                f"SELECT payload_json FROM {table} ORDER BY rowid"
            ).fetchall()
        return tuple(json.loads(str(row["payload_json"])) for row in rows)

    def latest_payload(self, table: str) -> dict[str, Any] | None:
        self._require_table(table)
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
        return json.loads(str(row["payload_json"])) if row else None

    def get_payload(self, table: str, record_id: str) -> dict[str, Any]:
        self._require_table(table)
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} WHERE record_id = ?",
                (str(record_id),),
            ).fetchone()
        if row is None:
            raise KeyError(record_id)
        return json.loads(str(row["payload_json"]))

    def count(self, table: str) -> int:
        self._require_table(table)
        with self.connection() as connection:
            row = connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
        return int(row["count"])

    def _require_table(self, table: str) -> None:
        if table not in TABLE_KEYS:
            raise ValueError(f"unsupported Package 130 table: {table}")

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
