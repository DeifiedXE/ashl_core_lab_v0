"""Read-only authority reconciliation for Package 138."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.state.package_134_package_133_source import (
    Package133SourceBundle,
    load_package_133_source_read_only,
    package_133_source_tree_sha256,
)
from ashl_core_v1.state.package_137_self_state_review_store import (
    Package137SelfStateReviewStore,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    PersistentSessionRecoveryStore,
)
from ashl_core_v1.state.persistent_session_recovery_types import ActiveSelfStateHeadRecord
from ashl_core_v1.state.self_state_readback_types import (
    ACTIVE_HEAD_AUTHORITY,
    PACKAGE_133_PASS_STATUS,
    PACKAGE_134_PASS_STATUS,
    PACKAGE_137_PASS_STATUS,
    REVIEW_GATE_AUTHORITY,
    SELF_STATE_AUTHORITY,
    SOURCE_SCHEMA_VERSION,
    SelfStateReadbackAuthoritySourceBindingRecord,
)


@dataclass(frozen=True)
class Package138SourceBundle:
    package_133: Package133SourceBundle
    active_head: ActiveSelfStateHeadRecord
    active_identity_binding: dict[str, Any] | None
    active_session_shutdown: dict[str, Any] | None
    package_134_audit: dict[str, Any]
    package_137_audit: dict[str, Any]
    package_137_commit_receipt: dict[str, Any]
    source_binding: SelfStateReadbackAuthoritySourceBindingRecord


def load_package_138_sources_read_only(
    *,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
) -> Package138SourceBundle:
    p133_root = Path(package_133_state_dir).resolve()
    p134_root = Path(package_134_state_dir).resolve()
    p137_root = Path(package_137_state_dir).resolve()
    roots = (p133_root, p134_root, p137_root)
    if len(set(roots)) != 3 or not all(root.is_dir() for root in roots):
        raise RuntimeError("blocked_package_138_source_roots_missing_or_ambiguous")
    before = tuple(_authority_tree_sha256(root) for root in roots)
    p133 = load_package_133_source_read_only(p133_root)
    p134 = PersistentSessionRecoveryStore(p134_root)
    p137 = Package137SelfStateReviewStore(p137_root)
    p134_integrity = p134.audit_integrity()
    p137_integrity = p137.audit_integrity()
    if not p134_integrity["valid"] or not p137_integrity["valid"]:
        raise RuntimeError("blocked_package_138_source_store_integrity_failure")
    head = p134.get_active_head()
    active_identity_bindings = tuple(
        item
        for item in p134.list_payloads("persistent_session_identity_bindings")
        if item.get("active_head_id") == head.active_head_id
        and item.get("active_head_sha256") == head.active_head_sha256
        and item.get("head_revision") == head.head_revision
        and item.get("self_state_record_id") == head.self_state_record_id
        and item.get("self_state_sha256") == head.self_state_sha256
        and item.get("session_id") == head.bound_session_id
        and item.get("process_instance_id") == head.bound_process_instance_id
        and item.get("binding_status") == "bound_to_verified_package_133_identity"
    )
    if len(active_identity_bindings) > 1:
        raise RuntimeError("blocked_package_138_active_process_binding_missing_or_ambiguous")
    active_identity_binding = active_identity_bindings[0] if active_identity_bindings else None
    active_session_shutdowns = tuple(
        item
        for item in p134.list_payloads("persistent_session_shutdown_records")
        if item.get("active_head_id") == head.active_head_id
        and item.get("active_head_sha256") == head.active_head_sha256
        and item.get("head_revision") == head.head_revision
        and item.get("session_id") == head.bound_session_id
        and item.get("process_instance_id") == head.bound_process_instance_id
        and item.get("clean_shutdown_verified") is True
    )
    if len(active_session_shutdowns) > 1:
        raise RuntimeError("blocked_package_138_active_session_shutdown_ambiguous")
    active_session_shutdown = active_session_shutdowns[0] if active_session_shutdowns else None
    p134_audits = tuple(
        item
        for item in p134.list_payloads("package_134_audits")
        if item.get("audit_status") == PACKAGE_134_PASS_STATUS
    )
    p137_audits = tuple(
        item
        for item in p137.list_payloads("package_137_audits")
        if item.get("audit_status") == PACKAGE_137_PASS_STATUS
    )
    commits = tuple(
        item
        for item in p137.list_payloads("self_state_mutation_commit_receipts")
        if item.get("commit_status") == "committed_reviewed_self_state_successor"
    )
    if not p134_audits or not p137_audits or not commits:
        raise RuntimeError("blocked_package_138_passed_authority_evidence_missing")
    p134_audit = p134_audits[-1]
    p137_audit = p137_audits[-1]
    commit = commits[-1]
    leaf = p133.leaf
    exact = all(
        (
            head.self_state_record_id == leaf.self_state_record_id,
            head.self_state_sha256 == leaf.self_state_sha256,
            head.self_state_lineage_id == leaf.self_state_lineage_id,
            head.self_state_version == leaf.self_state_version,
            head.lineage_generation == leaf.lineage_generation,
            commit.get("child_self_state_record_id") == leaf.self_state_record_id,
            commit.get("child_self_state_sha256") == leaf.self_state_sha256,
        )
    )
    if not exact:
        raise RuntimeError("blocked_package_138_active_head_self_state_mismatch")
    cas_refs = {
        str(item.get("cas_event_id"))
        for item in p134.list_payloads("active_head_cas_events")
    }
    if str(commit.get("package_134_cas_event_id")) not in cas_refs:
        raise RuntimeError("blocked_package_138_package_137_cas_lineage_missing")
    if p133.package_133_audit.get("audit_status") != PACKAGE_133_PASS_STATUS:
        raise RuntimeError("blocked_package_138_package_133_audit_invalid")
    after = tuple(_authority_tree_sha256(root) for root in roots)
    if before != after:
        raise RuntimeError("blocked_package_138_authority_source_modified_during_read")
    payload: dict[str, Any] = {
        "source_binding_id": "",
        "source_binding_sha256": "",
        "schema_version": SOURCE_SCHEMA_VERSION,
        "created_at": utc_now(),
        "package_133_audit_id": str(p133.package_133_audit["audit_id"]),
        "package_133_audit_status": str(p133.package_133_audit["audit_status"]),
        "package_134_audit_id": str(p134_audit["audit_id"]),
        "package_134_audit_status": str(p134_audit["audit_status"]),
        "package_137_audit_id": str(p137_audit["audit_id"]),
        "package_137_audit_status": str(p137_audit["audit_status"]),
        "package_137_commit_receipt_ref": str(commit["commit_receipt_id"]),
        "package_137_review_ref": str(commit["review_id"]),
        "self_state_authority": SELF_STATE_AUTHORITY,
        "active_head_authority": ACTIVE_HEAD_AUTHORITY,
        "review_gate_authority": REVIEW_GATE_AUTHORITY,
        "active_head_id": head.active_head_id,
        "active_head_sha256": head.active_head_sha256,
        "head_revision": head.head_revision,
        "self_state_record_id": leaf.self_state_record_id,
        "self_state_sha256": leaf.self_state_sha256,
        "self_state_lineage_id": leaf.self_state_lineage_id,
        "self_state_version": leaf.self_state_version,
        "lineage_generation": leaf.lineage_generation,
        "package_133_tree_sha256": before[0],
        "package_134_tree_sha256": before[1],
        "package_137_tree_sha256": before[2],
        "exact_head_state_binding_verified": True,
        "parent_hash_chain_verified": p133.snapshot.full_parent_hash_chain_verified,
        "source_stores_read_only": True,
        "source_record_refs": (
            str(p133.package_133_audit["audit_id"]),
            str(p134_audit["audit_id"]),
            str(p137_audit["audit_id"]),
            str(commit["commit_receipt_id"]),
            str(commit["review_id"]),
            str(commit["package_134_cas_event_id"]),
            head.active_head_id,
            leaf.self_state_record_id,
        ),
    }
    source_binding = _hashed_record(
        SelfStateReadbackAuthoritySourceBindingRecord,
        payload,
        id_field="source_binding_id",
        hash_field="source_binding_sha256",
        prefix="self_state_readback_source_binding",
    )
    return Package138SourceBundle(
        package_133=p133,
        active_head=head,
        active_identity_binding=active_identity_binding,
        active_session_shutdown=active_session_shutdown,
        package_134_audit=p134_audit,
        package_137_audit=p137_audit,
        package_137_commit_receipt=commit,
        source_binding=source_binding,
    )


def authority_source_tree_hashes(
    *,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
) -> tuple[str, str, str]:
    return (
        package_133_source_tree_sha256(package_133_state_dir),
        _authority_tree_sha256(Path(package_134_state_dir).resolve()),
        _authority_tree_sha256(Path(package_137_state_dir).resolve()),
    )


def _authority_tree_sha256(root: Path) -> str:
    if not root.is_dir():
        raise FileNotFoundError(root)
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_symlink():
            raise ValueError("Package 138 authority source cannot contain symlinks")
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


def _hashed_record(
    record_type: type[Any],
    payload: dict[str, Any],
    *,
    id_field: str,
    hash_field: str,
    prefix: str,
) -> Any:
    identity = dict(payload)
    identity.pop(id_field, None)
    identity.pop(hash_field, None)
    identity.pop("created_at", None)
    digest = sha256_payload(identity)
    payload[id_field] = f"{prefix}:{digest[:16]}"
    payload[hash_field] = digest
    return record_type(**payload)
