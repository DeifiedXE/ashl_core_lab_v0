"""SQLite store for Package 123 real perception two-cycle run records."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import canonical_json, plain, sha256_payload, utc_now
from ashl_core_v1.runtime.package_123_types import (
    Package123CycleRecord,
    Package123PreflightRecord,
    Package123RealPerceptionGrowthAuditRecord,
    Package123TwoCycleComparisonRecord,
    RealPerceptionReadbackInfluenceRecord,
    ReadbackLoadTimingRecord,
    StimulusRunManifest,
    StimulusTransitionRecord,
    BoundedWindowCaptureBinding,
    SystemAudioLoopbackSourceDescriptor,
    Package123ExperienceSourceProfile,
    package_123_store_path,
)
from ashl_core_v1.runtime.package_123_transport_integrity import (
    AlignmentWindowCoverageRecord,
    Package123RerunLineageRecord,
    Package123TransportFaultRecord,
    Package123TransportIntegritySummary,
    Package123TransportRepairAuditRecord,
    Package123TransportSoakRecord,
    TransportFlushRecord,
    TransportLaneReadinessRecord,
)


STORE_SCHEMA_NAME = "ashl_package_123_real_perception_store"
STORE_SCHEMA_VERSION = "v0"


TABLE_KEY_FIELDS = {
    "package_123_preflight_records": "preflight_id",
    "stimulus_run_manifests": "experiment_run_id",
    "stimulus_transition_records": "transition_id",
    "window_capture_bindings": "binding_id",
    "loopback_source_descriptors": "source_descriptor_id",
    "experience_source_profiles": "source_profile_id",
    "package_123_cycle_records": "cycle_record_id",
    "readback_load_timing_records": "timing_record_id",
    "readback_influence_records": "influence_record_id",
    "two_cycle_comparison_records": "comparison_id",
    "package_123_audit_records": "audit_id",
    "package_123_transport_lane_readiness": "readiness_record_id",
    "package_123_transport_flush_records": "flush_record_id",
    "package_123_alignment_window_coverage": "coverage_record_id",
    "package_123_transport_faults": "transport_fault_id",
    "package_123_transport_integrity_summaries": "integrity_summary_id",
    "package_123_transport_soak_records": "transport_soak_id",
    "package_123_rerun_lineage": "lineage_record_id",
    "package_123_transport_repair_audits": "audit_id",
}


class Package123CycleStore:
    def __init__(self, state_dir: str | Path) -> None:
        if state_dir is None:
            raise ValueError("explicit state_dir is required")
        self.state_dir = Path(state_dir)
        self.db_path = package_123_store_path(self.state_dir)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
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

    def validate_schema(self) -> dict[str, object]:
        with self.connection() as connection:
            row = connection.execute("SELECT schema_name, schema_version FROM store_metadata").fetchone()
            tables = {
                item["name"]
                for item in connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            }
        missing = (set(TABLE_KEY_FIELDS) | {"store_metadata"}) - tables
        return {
            "valid": row is not None
            and row["schema_name"] == STORE_SCHEMA_NAME
            and row["schema_version"] == STORE_SCHEMA_VERSION
            and not missing,
            "schema_name": row["schema_name"] if row else None,
            "schema_version": row["schema_version"] if row else None,
            "missing_tables": tuple(sorted(missing)),
            "db_path": str(self.db_path),
        }

    def append_preflight(self, record: Package123PreflightRecord) -> None:
        self._append("package_123_preflight_records", record.preflight_id, record.to_dict())

    def append_stimulus_manifest(self, manifest: StimulusRunManifest) -> None:
        self._append("stimulus_run_manifests", manifest.experiment_run_id, manifest.to_dict())
        for transition in manifest.transitions:
            self.append_stimulus_transition(transition)

    def append_stimulus_transition(self, record: StimulusTransitionRecord) -> None:
        self._append("stimulus_transition_records", record.transition_id, record.to_dict())

    def append_window_binding(self, record: BoundedWindowCaptureBinding) -> None:
        self._append("window_capture_bindings", record.binding_id, record.to_dict())

    def append_loopback_descriptor(self, record: SystemAudioLoopbackSourceDescriptor) -> None:
        self._append("loopback_source_descriptors", record.source_descriptor_id, record.to_dict())

    def append_source_profile(self, record: Package123ExperienceSourceProfile) -> None:
        self._append("experience_source_profiles", record.source_profile_id, record.to_dict())

    def append_cycle_record(self, record: Package123CycleRecord) -> None:
        self._append("package_123_cycle_records", record.cycle_record_id, record.to_dict())

    def append_readback_load_timing(self, record: ReadbackLoadTimingRecord) -> None:
        self._append("readback_load_timing_records", record.timing_record_id, record.to_dict())

    def append_readback_influence(self, record: RealPerceptionReadbackInfluenceRecord) -> None:
        self._append("readback_influence_records", record.influence_record_id, record.to_dict())

    def append_two_cycle_comparison(self, record: Package123TwoCycleComparisonRecord) -> None:
        self._append("two_cycle_comparison_records", record.comparison_id, record.to_dict())

    def append_audit(self, record: Package123RealPerceptionGrowthAuditRecord) -> None:
        self._append("package_123_audit_records", record.audit_id, record.to_dict())

    def append_transport_readiness(self, record: TransportLaneReadinessRecord) -> None:
        self._append("package_123_transport_lane_readiness", record.readiness_record_id, record.to_dict())

    def append_transport_flush(self, record: TransportFlushRecord) -> None:
        self._append("package_123_transport_flush_records", record.flush_record_id, record.to_dict())

    def append_alignment_window_coverage(self, record: AlignmentWindowCoverageRecord) -> None:
        self._append("package_123_alignment_window_coverage", record.coverage_record_id, record.to_dict())

    def append_transport_fault(self, record: Package123TransportFaultRecord) -> None:
        self._append("package_123_transport_faults", record.transport_fault_id, record.to_dict())

    def append_transport_integrity_summary(self, record: Package123TransportIntegritySummary) -> None:
        self._append("package_123_transport_integrity_summaries", record.integrity_summary_id, record.to_dict())

    def append_transport_soak(self, record: Package123TransportSoakRecord) -> None:
        self._append("package_123_transport_soak_records", record.transport_soak_id, record.to_dict())

    def append_rerun_lineage(self, record: Package123RerunLineageRecord) -> None:
        self._append("package_123_rerun_lineage", record.lineage_record_id, record.to_dict())

    def append_transport_repair_audit(self, record: Package123TransportRepairAuditRecord) -> None:
        self._append("package_123_transport_repair_audits", record.audit_id, record.to_dict())

    def get_payload(self, table: str, record_id: str) -> dict[str, Any]:
        key_field = TABLE_KEY_FIELDS[table]
        with self.connection() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} WHERE {key_field} = ?",
                (record_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"missing {table} record: {record_id}")
        return dict(json.loads(row["payload_json"]))

    def list_payloads(self, table: str) -> tuple[dict[str, Any], ...]:
        with self.connection() as connection:
            rows = connection.execute(f"SELECT payload_json FROM {table} ORDER BY row_id").fetchall()
        return tuple(dict(json.loads(row["payload_json"])) for row in rows)

    def latest_payload(self, table: str) -> dict[str, Any] | None:
        with self.connection() as connection:
            row = connection.execute(f"SELECT payload_json FROM {table} ORDER BY row_id DESC LIMIT 1").fetchone()
        return dict(json.loads(row["payload_json"])) if row else None

    def latest_cycle_record(self, cycle_index: int) -> dict[str, Any] | None:
        rows = [
            item
            for item in self.list_payloads("package_123_cycle_records")
            if int(item.get("cycle_index", -1)) == int(cycle_index)
        ]
        return rows[-1] if rows else None

    def latest_preflight(self, cycle_index: int | None = None) -> dict[str, Any] | None:
        rows = self.list_payloads("package_123_preflight_records")
        if cycle_index is not None:
            rows = tuple(item for item in rows if int(item.get("cycle_index", -1)) == int(cycle_index))
        return rows[-1] if rows else None

    def close(self) -> None:
        return None

    def _append(self, table: str, record_id: str, payload: dict[str, Any]) -> None:
        key_field = TABLE_KEY_FIELDS[table]
        created_at = str(payload.get("created_at") or utc_now())
        payload_json = canonical_json(payload)
        with self.connection() as connection:
            connection.execute(
                f"""
                INSERT INTO {table} (
                    {key_field}, created_at, payload_json, payload_sha256
                ) VALUES (?, ?, ?, ?)
                """,
                (record_id, created_at, payload_json, sha256_payload(payload)),
            )

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
                INSERT OR IGNORE INTO store_metadata (schema_name, schema_version, created_at)
                VALUES (?, ?, ?)
                """,
                (STORE_SCHEMA_NAME, STORE_SCHEMA_VERSION, utc_now()),
            )
            for table, key_field in TABLE_KEY_FIELDS.items():
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                        row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        {key_field} TEXT NOT NULL UNIQUE,
                        created_at TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        payload_sha256 TEXT NOT NULL
                    )
                    """
                )


def strip_package_123_raw_media(payload: dict[str, Any]) -> dict[str, Any]:
    """Defensive helper for CLI/status surfaces."""
    clean = dict(plain(payload))
    for key in ("data", "raw_bytes", "raw_pcm", "raw_image", "base64", "waveform"):
        clean.pop(key, None)
    return clean
