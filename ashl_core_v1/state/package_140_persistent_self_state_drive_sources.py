"""Query-only Package 133-139 evidence loading for the Package 140 milestone."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.endocrine.drive_modulation_types import (
    Package136SameSessionDriveModulationAudit,
)
from ashl_core_v1.endocrine.drive_signal_trace_types import (
    Package135DriveSignalTraceSeparationAudit,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload
from ashl_core_v1.state.persistent_self_state_drive_closure_types import (
    CLOSED_PACKAGE_IDS,
    EXPECTED_AUDIT_STATUSES,
)
from ashl_core_v1.state.persistent_self_state_review_types import (
    Package137PersistentSelfStateReviewGateAudit,
)
from ashl_core_v1.state.persistent_self_state_schema import (
    Package133CrossSessionSelfStateSchemaAudit,
)
from ashl_core_v1.state.persistent_session_recovery_types import (
    Package134PersistentSessionRecoveryAudit,
)
from ashl_core_v1.state.self_state_readback_types import (
    Package138SelfStateReadbackBoundaryAudit,
)
from ashl_core_v1.state.self_state_rollback_types import (
    Package139SelfStateRollbackAudit,
)


DATABASE_SPECS = {
    "133": (
        Path("package_133_cross_session_self_state_schema_v0/package_133.sqlite3"),
        "package_133_audits",
        Package133CrossSessionSelfStateSchemaAudit,
    ),
    "134": (
        Path("package_134_persistent_session_recovery_v0/package_134.sqlite3"),
        "package_134_audits",
        Package134PersistentSessionRecoveryAudit,
    ),
    "135": (
        Path("package_135_drive_signal_trace_separation_v0/package_135.sqlite3"),
        "package_135_audits",
        Package135DriveSignalTraceSeparationAudit,
    ),
    "136": (
        Path("package_136_same_session_drive_modulation_v0/package_136.sqlite3"),
        "package_136_audits",
        Package136SameSessionDriveModulationAudit,
    ),
    "137": (
        Path("package_137_persistent_self_state_review_gate_v0/package_137.sqlite3"),
        "package_137_audits",
        Package137PersistentSelfStateReviewGateAudit,
    ),
    "138": (
        Path("package_138_self_state_readback_boundary_v0/package_138.sqlite3"),
        "package_138_audits",
        Package138SelfStateReadbackBoundaryAudit,
    ),
    "139": (
        Path("package_139_self_state_rollback_and_audit_v0/package_139.sqlite3"),
        "package_139_audits",
        Package139SelfStateRollbackAudit,
    ),
}

REQUIRED_TABLES = {
    "133": {
        "persistent_self_state_representation_contracts",
        "persistent_self_state_records",
        "persistent_self_state_transition_records",
        "persistent_self_state_lineage_validations",
        "package_133_boundary_control_results",
        "package_133_audits",
    },
    "134": {
        "active_self_state_head",
        "active_head_cas_events",
        "persistent_session_recovery_pairs",
        "package_134_recovery_control_results",
        "package_134_audits",
    },
    "135": {
        "drive_trace_contracts",
        "package_134_drive_non_recovery_evidence",
        "drive_authority_separations",
        "drive_cross_session_resets",
        "drive_trace_process_pairs",
        "package_135_control_results",
        "package_135_audits",
    },
    "136": {
        "package_135_signal_authority_bindings",
        "same_session_drive_modulation_contracts",
        "drive_modulation_consumer_allowlists",
        "drive_modulation_cross_session_neutrality",
        "drive_modulation_counterfactual_comparisons",
        "package_136_control_results",
        "package_136_audits",
    },
    "137": {
        "teacher_authority_bindings",
        "self_state_teacher_reviews",
        "self_state_mutation_commit_receipts",
        "self_state_review_invariance_records",
        "package_137_control_results",
        "package_137_audits",
    },
    "138": {
        "self_state_readback_source_bindings",
        "self_state_readback_contracts",
        "self_state_readback_consumer_allowlists",
        "bounded_self_state_readbacks",
        "self_state_readback_lifecycle_records",
        "self_state_readback_fresh_process_resets",
        "self_state_readback_counterfactual_comparisons",
        "package_138_control_results",
        "package_138_audits",
    },
    "139": {
        "self_state_rollback_source_bindings",
        "self_state_rollback_contracts",
        "self_state_ancestor_proofs",
        "self_state_head_selection_commit_receipts",
        "self_state_rollback_no_fork_guard_records",
        "self_state_rollback_counterfactual_comparisons",
        "package_139_control_results",
        "package_139_audits",
    },
}


@dataclass(frozen=True)
class EvidenceTreeSnapshot:
    file_count: int
    byte_count: int
    tree_sha256: str


@dataclass(frozen=True)
class Package140PackageSource:
    package_id: str
    source_root: Path
    database_path: Path
    database_relative_path: str
    snapshot_before: EvidenceTreeSnapshot
    snapshot_after: EvidenceTreeSnapshot
    database_integrity_valid: bool
    all_payload_hashes_verified: bool
    payload_hash_count: int
    typed_audit_validation_passed: bool
    latest_audit: dict[str, Any]
    table_payloads: dict[str, tuple[dict[str, Any], ...]]


@dataclass(frozen=True)
class Package140SourceBundle:
    packages: dict[str, Package140PackageSource]


class ReadOnlyEvidenceDatabase:
    """SQLite reader that cannot initialize, migrate, or mutate an authority store."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path).resolve()
        if not self.database_path.is_file():
            raise FileNotFoundError(self.database_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            f"file:{self.database_path.as_posix()}?mode=ro&immutable=1",
            uri=True,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        return connection

    def integrity_valid(self) -> bool:
        with closing(self._connect()) as connection:
            return str(connection.execute("PRAGMA integrity_check").fetchone()[0]) == "ok"

    def payload_tables(self) -> tuple[str, ...]:
        with closing(self._connect()) as connection:
            tables = tuple(
                str(row[0])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
                ).fetchall()
                if not str(row[0]).startswith("sqlite_")
            )
            result: list[str] = []
            for table in tables:
                _validate_table_name(table)
                columns = {
                    str(row[1])
                    for row in connection.execute(f'PRAGMA table_info("{table}")').fetchall()
                }
                if {"payload_json", "payload_sha256"}.issubset(columns):
                    result.append(table)
        return tuple(result)

    def list_payloads(self, table: str) -> tuple[dict[str, Any], ...]:
        _validate_table_name(table)
        with closing(self._connect()) as connection:
            rows = connection.execute(
                f'SELECT payload_json, payload_sha256 FROM "{table}" ORDER BY rowid'
            ).fetchall()
        payloads: list[dict[str, Any]] = []
        for row in rows:
            payload = json.loads(str(row["payload_json"]))
            if str(row["payload_sha256"]) != sha256_payload(payload):
                raise RuntimeError(f"blocked_package_140_corrupt_payload:{table}")
            payloads.append(payload)
        return tuple(payloads)

    def load_and_verify_all_payloads(
        self,
    ) -> tuple[dict[str, tuple[dict[str, Any], ...]], int]:
        result: dict[str, tuple[dict[str, Any], ...]] = {}
        count = 0
        for table in self.payload_tables():
            payloads = self.list_payloads(table)
            result[table] = payloads
            count += len(payloads)
        return result, count


def load_package_140_sources_read_only(
    package_state_dirs: dict[str, str | Path],
) -> Package140SourceBundle:
    if tuple(sorted(package_state_dirs)) != CLOSED_PACKAGE_IDS:
        raise RuntimeError("blocked_package_140_requires_exact_package_133_to_139_sources")
    roots = {package_id: Path(path).resolve() for package_id, path in package_state_dirs.items()}
    if len(set(roots.values())) != len(CLOSED_PACKAGE_IDS):
        raise RuntimeError("blocked_package_140_ambiguous_authority_source_roots")
    if not all(root.is_dir() for root in roots.values()):
        raise RuntimeError("blocked_package_140_authority_source_missing")

    packages: dict[str, Package140PackageSource] = {}
    for package_id in CLOSED_PACKAGE_IDS:
        root = roots[package_id]
        before = evidence_tree_snapshot(root)
        relative_database, audit_table, audit_type = DATABASE_SPECS[package_id]
        database = _resolve_database(root, relative_database)
        reader = ReadOnlyEvidenceDatabase(database)
        integrity = reader.integrity_valid()
        payloads, payload_count = reader.load_and_verify_all_payloads()
        missing = REQUIRED_TABLES[package_id].difference(payloads)
        if missing:
            raise RuntimeError(
                f"blocked_package_140_required_tables_missing:{package_id}:{','.join(sorted(missing))}"
            )
        audits = payloads[audit_table]
        if not audits:
            raise RuntimeError(f"blocked_package_140_package_{package_id}_audit_missing")
        latest_audit = dict(audits[-1])
        if latest_audit.get("audit_status") != EXPECTED_AUDIT_STATUSES[package_id]:
            raise RuntimeError(f"blocked_package_140_package_{package_id}_latest_audit_invalid")
        typed_audit = audit_type(**_tuple_tree(latest_audit))
        typed_valid = (
            getattr(typed_audit, "audit_status", None)
            == EXPECTED_AUDIT_STATUSES[package_id]
        )
        after = evidence_tree_snapshot(root)
        packages[package_id] = Package140PackageSource(
            package_id=package_id,
            source_root=root,
            database_path=database,
            database_relative_path=database.relative_to(root).as_posix(),
            snapshot_before=before,
            snapshot_after=after,
            database_integrity_valid=integrity,
            all_payload_hashes_verified=True,
            payload_hash_count=payload_count,
            typed_audit_validation_passed=typed_valid,
            latest_audit=latest_audit,
            table_payloads=payloads,
        )
    return Package140SourceBundle(packages=packages)


def evidence_tree_snapshot(root: str | Path) -> EvidenceTreeSnapshot:
    source_root = Path(root).resolve()
    if not source_root.is_dir():
        raise FileNotFoundError(source_root)
    entries: list[dict[str, Any]] = []
    byte_count = 0
    for path in sorted(source_root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_symlink():
            raise ValueError("Package 140 authority evidence cannot contain symlinks")
        if not path.is_file():
            continue
        data = path.read_bytes()
        byte_count += len(data)
        entries.append(
            {
                "relative_path": path.relative_to(source_root).as_posix(),
                "size_bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    return EvidenceTreeSnapshot(
        file_count=len(entries),
        byte_count=byte_count,
        tree_sha256=sha256_payload(entries),
    )


def path_fingerprint(path: str | Path) -> str:
    normalized = os.path.normcase(str(Path(path).resolve())).replace("\\", "/")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _resolve_database(root: Path, relative_database: Path) -> Path:
    direct = root / relative_database
    nested = root / relative_database.name
    candidates = tuple(
        dict.fromkeys(
            candidate.resolve()
            for candidate in (direct, nested, *root.rglob(relative_database.name))
            if candidate.is_file()
        )
    )
    if len(candidates) != 1:
        raise RuntimeError(
            f"blocked_package_140_database_missing_or_ambiguous:{relative_database.name}:{len(candidates)}"
        )
    return candidates[0]


def _tuple_tree(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_tuple_tree(item) for item in value)
    if isinstance(value, dict):
        return {str(key): _tuple_tree(item) for key, item in value.items()}
    return value


def _validate_table_name(table: str) -> None:
    if not table.replace("_", "").isalnum():
        raise ValueError("invalid read-only evidence table name")
