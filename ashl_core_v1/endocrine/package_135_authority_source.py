"""Read-only Package 133/134 authority evidence for Package 135."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.endocrine.drive_signal_trace_types import (
    PACKAGE_133_PASS_STATUS,
    PACKAGE_134_PASS_STATUS,
    SOURCE_EVIDENCE_SCHEMA_VERSION,
    Package134DriveNonRecoveryEvidenceRecord,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.state.package_134_package_133_source import (
    Package133SourceBundle,
    load_package_133_source_read_only,
)
from ashl_core_v1.state.persistent_self_state_schema import (
    ALLOWED_PERSISTENT_FIELDS,
    FORBIDDEN_AUTHORITIES,
)
from ashl_core_v1.state.persistent_session_recovery_store import package_134_store_path
from ashl_core_v1.state.persistent_session_recovery_types import ActiveSelfStateHeadRecord


_DRIVE_LIKE_KEYS = {
    "drive",
    "drive_signal",
    "drive_state",
    "endocrine",
    "tendency",
    "affordance",
    "purpose",
    "desire",
    "reward",
    "emotion",
    "action_preference",
}


@dataclass(frozen=True)
class Package135AuthoritySourceBundle:
    package_133: Package133SourceBundle
    package_134_audit: dict[str, Any]
    active_head: ActiveSelfStateHeadRecord
    recovery_pair: dict[str, Any]
    identity_bindings: tuple[dict[str, Any], ...]
    process_receipts: tuple[dict[str, Any], ...]
    non_recovery_evidence: Package134DriveNonRecoveryEvidenceRecord
    package_133_tree_sha256: str
    package_134_tree_sha256: str


def load_package_135_authority_sources_read_only(
    *,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
) -> Package135AuthoritySourceBundle:
    package_133_root = Path(package_133_state_dir).resolve()
    package_134_root = Path(package_134_state_dir).resolve()
    if package_133_root == package_134_root:
        raise ValueError("Package 133 and 134 evidence roots must be distinct")
    package_133_tree = source_tree_sha256(package_133_root)
    package_134_tree = source_tree_sha256(package_134_root)
    package_133 = load_package_133_source_read_only(package_133_root)
    database = package_134_store_path(package_134_root)
    if not database.is_file():
        raise FileNotFoundError(database)

    uri = f"file:{database.as_posix()}?mode=ro&immutable=1"
    with closing(sqlite3.connect(uri, uri=True, timeout=10.0)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        if str(connection.execute("PRAGMA integrity_check").fetchone()[0]) != "ok":
            raise RuntimeError("blocked_corrupt_package_134_store")
        audits = _load_payloads(connection, "package_134_audits")
        pairs = _load_payloads(connection, "persistent_session_recovery_pairs")
        bindings = _load_payloads(connection, "persistent_session_identity_bindings")
        receipts = _load_payloads(connection, "persistent_session_recovery_process_receipts")
        heads = _load_payloads(connection, "active_self_state_head")

    passing = tuple(item for item in audits if item.get("audit_status") == PACKAGE_134_PASS_STATUS)
    if len(passing) != 1:
        raise RuntimeError(f"blocked_package_134_audit_missing_or_ambiguous:{len(passing)}")
    if len(pairs) != 1 or len(bindings) != 2 or len(receipts) != 2 or len(heads) != 1:
        raise RuntimeError("blocked_package_134_recovery_evidence_cardinality")
    audit = dict(passing[0])
    pair = dict(pairs[0])
    active_head = ActiveSelfStateHeadRecord.from_dict(dict(heads[0]))
    _validate_package_134_boundary(
        package_133=package_133,
        audit=audit,
        pair=pair,
        bindings=bindings,
        receipts=receipts,
        active_head=active_head,
    )
    evidence = _build_non_recovery_evidence(
        package_133=package_133,
        audit=audit,
        pair=pair,
        bindings=bindings,
        active_head=active_head,
    )
    if source_tree_sha256(package_133_root) != package_133_tree:
        raise RuntimeError("blocked_package_133_source_changed_during_read")
    if source_tree_sha256(package_134_root) != package_134_tree:
        raise RuntimeError("blocked_package_134_source_changed_during_read")
    return Package135AuthoritySourceBundle(
        package_133=package_133,
        package_134_audit=audit,
        active_head=active_head,
        recovery_pair=pair,
        identity_bindings=bindings,
        process_receipts=receipts,
        non_recovery_evidence=evidence,
        package_133_tree_sha256=package_133_tree,
        package_134_tree_sha256=package_134_tree,
    )


def source_tree_sha256(source_root: str | Path) -> str:
    root = Path(source_root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_symlink():
            raise ValueError("Package 135 authority evidence cannot contain symlinks")
        if path.is_file():
            data = path.read_bytes()
            entries.append(
                {
                    "relative_path": path.relative_to(root).as_posix(),
                    "size_bytes": len(data),
                    "sha256": sha256_bytes(data),
                }
            )
    return sha256_payload(entries)


def _load_payloads(connection: sqlite3.Connection, table: str) -> tuple[dict[str, Any], ...]:
    rows = connection.execute(
        f"SELECT payload_json, payload_sha256 FROM {table} ORDER BY rowid"
    ).fetchall()
    payloads: list[dict[str, Any]] = []
    for row in rows:
        payload = json.loads(str(row["payload_json"]))
        if str(row["payload_sha256"]) != sha256_payload(payload):
            raise RuntimeError(f"blocked_corrupt_package_134_payload:{table}")
        payloads.append(payload)
    return tuple(payloads)


def _validate_package_134_boundary(
    *,
    package_133: Package133SourceBundle,
    audit: dict[str, Any],
    pair: dict[str, Any],
    bindings: tuple[dict[str, Any], ...],
    receipts: tuple[dict[str, Any], ...],
    active_head: ActiveSelfStateHeadRecord,
) -> None:
    required_true = (
        "package_133_source_unchanged",
        "package_133_only_representation_authority",
        "unique_lineage_and_leaf_verified",
        "parent_hash_chain_verified",
        "active_head_separate_from_history",
        "active_head_cas_verified",
        "active_head_hash_chain_verified",
        "session_identity_bindings_verified",
        "same_self_state_lineage_verified",
        "same_self_state_record_verified",
        "process_ids_distinct",
        "process_a_ended_before_process_b_started",
    )
    required_false = (
        "identity_fork_created",
        "memory_content_restored",
        "perception_history_restored",
        "working_readback_restored",
        "drive_state_restored",
        "attention_state_restored",
        "thought_engine_state_restored",
        "output_state_restored",
        "action_state_restored",
        "learning_created",
        "behavior_influence_created",
        "persistent_psychological_continuity_claimed",
    )
    if audit.get("package_133_audit_status") != PACKAGE_133_PASS_STATUS:
        raise RuntimeError("blocked_package_134_package_133_status_invalid")
    if audit.get("package_133_audit_id") != package_133.snapshot.package_133_audit_id:
        raise RuntimeError("blocked_package_133_audit_lineage_mismatch")
    if not all(audit.get(name) is True for name in required_true):
        raise RuntimeError("blocked_package_134_positive_boundary_invalid")
    if not all(audit.get(name) is False for name in required_false):
        raise RuntimeError("blocked_package_134_forbidden_recovery_authority")
    if audit.get("failure_reasons") != []:
        raise RuntimeError("blocked_package_134_audit_has_failures")
    if pair.get("comparison_status") != "passed_real_fresh_process_session_recovery":
        raise RuntimeError("blocked_package_134_recovery_pair_invalid")
    if pair.get("identity_fork_created") is not False:
        raise RuntimeError("blocked_package_134_identity_fork")
    if active_head.self_state_lineage_id != package_133.snapshot.self_state_lineage_id:
        raise RuntimeError("blocked_package_134_active_head_lineage_mismatch")
    if active_head.self_state_record_id != package_133.snapshot.leaf_self_state_record_id:
        raise RuntimeError("blocked_package_134_active_head_record_mismatch")
    if active_head.self_state_sha256 != package_133.snapshot.leaf_self_state_sha256:
        raise RuntimeError("blocked_package_134_active_head_state_hash_mismatch")
    forbidden_binding_fields = (
        "representation_payload_loaded",
        "memory_content_restored",
        "perception_history_restored",
        "working_readback_restored",
        "drive_state_restored",
        "attention_state_restored",
        "thought_engine_state_restored",
        "output_state_restored",
        "action_state_restored",
        "learning_created",
        "behavior_influence_created",
    )
    if any(item.get(name) is True for item in bindings for name in forbidden_binding_fields):
        raise RuntimeError("blocked_package_134_binding_restored_forbidden_state")
    if {item.get("binding_kind") for item in bindings} != {
        "initial_session_binding",
        "fresh_process_recovery_binding",
    }:
        raise RuntimeError("blocked_package_134_identity_binding_kinds_invalid")
    if len({int(item["operating_system_process_id"]) for item in receipts}) != 2:
        raise RuntimeError("blocked_package_134_process_boundary_invalid")
    if "drive_signal" not in FORBIDDEN_AUTHORITIES or "drive_signal" in ALLOWED_PERSISTENT_FIELDS:
        raise RuntimeError("blocked_package_133_drive_boundary_invalid")
    if _contains_drive_like_key(active_head.to_dict()):
        raise RuntimeError("blocked_package_134_active_head_contains_drive_field")


def _build_non_recovery_evidence(
    *,
    package_133: Package133SourceBundle,
    audit: dict[str, Any],
    pair: dict[str, Any],
    bindings: tuple[dict[str, Any], ...],
    active_head: ActiveSelfStateHeadRecord,
) -> Package134DriveNonRecoveryEvidenceRecord:
    payload: dict[str, Any] = {
        "evidence_id": "",
        "evidence_sha256": "",
        "schema_version": SOURCE_EVIDENCE_SCHEMA_VERSION,
        "created_at": utc_now(),
        "package_133_audit_id": package_133.snapshot.package_133_audit_id,
        "package_133_audit_status": package_133.snapshot.package_133_audit_status,
        "package_134_audit_id": str(audit["audit_id"]),
        "package_134_audit_status": str(audit["audit_status"]),
        "package_134_active_head_id": active_head.active_head_id,
        "package_134_active_head_sha256": active_head.active_head_sha256,
        "package_134_recovery_pair_id": str(pair["recovery_pair_id"]),
        "package_134_identity_binding_refs": tuple(str(item["binding_id"]) for item in bindings),
        "structural_identity_continuity_verified": True,
        "package_133_allowed_fields_exclude_drive": True,
        "active_head_drive_fields_absent": True,
        "drive_state_restored": False,
        "attention_state_restored": False,
        "working_readback_restored": False,
        "behavior_influence_created": False,
        "package_134_source_opened_read_only": True,
        "evidence_status": "verified_identity_recovery_without_drive_recovery",
        "source_record_refs": (
            package_133.snapshot.package_133_audit_id,
            str(audit["audit_id"]),
            active_head.active_head_id,
            str(pair["recovery_pair_id"]),
            *(str(item["binding_id"]) for item in bindings),
        ),
    }
    identity = dict(payload)
    identity.pop("evidence_id")
    identity.pop("evidence_sha256")
    identity.pop("created_at")
    digest = sha256_payload(identity)
    payload["evidence_sha256"] = digest
    payload["evidence_id"] = f"package_134_drive_non_recovery:{digest[:16]}"
    return Package134DriveNonRecoveryEvidenceRecord(**payload)


def _contains_drive_like_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower()
            if normalized in _DRIVE_LIKE_KEYS or any(
                normalized.startswith(f"{name}_") for name in _DRIVE_LIKE_KEYS
            ):
                return True
            if _contains_drive_like_key(item):
                return True
    elif isinstance(value, (list, tuple)):
        return any(_contains_drive_like_key(item) for item in value)
    return False
