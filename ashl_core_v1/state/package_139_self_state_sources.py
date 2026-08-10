"""Read-only reconciliation of Package 133, 134, 137 and 138 authorities."""

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
from ashl_core_v1.state.package_138_self_state_readback_store import (
    Package138SelfStateReadbackStore,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    PersistentSessionRecoveryStore,
)
from ashl_core_v1.state.persistent_session_recovery_types import ActiveSelfStateHeadRecord
from ashl_core_v1.state.self_state_rollback_types import (
    PACKAGE_133_PASS_STATUS,
    PACKAGE_134_PASS_STATUS,
    PACKAGE_137_PASS_STATUS,
    PACKAGE_138_PASS_STATUS,
    SOURCE_SCHEMA_VERSION,
    Package139AuthoritySourceBindingRecord,
    build_hashed_record,
)


@dataclass(frozen=True)
class Package139SourceBundle:
    package_133: Package133SourceBundle
    active_head: ActiveSelfStateHeadRecord
    package_134_audit: dict[str, Any]
    package_137_audit: dict[str, Any]
    package_137_commit_receipt: dict[str, Any]
    package_138_audit: dict[str, Any]
    source_binding: Package139AuthoritySourceBindingRecord


def load_package_139_sources_read_only(
    *,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    package_138_state_dir: str | Path,
    require_canonical_leaf: bool = True,
) -> Package139SourceBundle:
    roots = tuple(
        Path(item).resolve()
        for item in (
            package_133_state_dir,
            package_134_state_dir,
            package_137_state_dir,
            package_138_state_dir,
        )
    )
    if len(set(roots)) != 4 or not all(root.is_dir() for root in roots):
        raise RuntimeError("blocked_package_139_source_roots_missing_or_ambiguous")
    p133_before = package_133_source_tree_sha256(roots[0])
    p137_before = authority_tree_sha256(roots[2])
    source = load_package_133_source_read_only(roots[0])
    p134 = PersistentSessionRecoveryStore(roots[1])
    p137 = Package137SelfStateReviewStore(roots[2])
    p138 = Package138SelfStateReadbackStore(roots[3])
    integrities = (
        p134.audit_integrity(),
        p137.audit_integrity(),
        p138.audit_integrity(),
    )
    if not all(item["valid"] for item in integrities):
        raise RuntimeError("blocked_package_139_source_store_integrity_failure")
    head = p134.get_active_head()
    p134_audit = _latest_passing_audit(
        p134.list_payloads("package_134_audits"),
        PACKAGE_134_PASS_STATUS,
        "package_134",
    )
    p137_audit = _latest_passing_audit(
        p137.list_payloads("package_137_audits"),
        PACKAGE_137_PASS_STATUS,
        "package_137",
    )
    p138_audit = _latest_passing_audit(
        p138.list_payloads("package_138_audits"),
        PACKAGE_138_PASS_STATUS,
        "package_138",
    )
    commits = tuple(
        item
        for item in p137.list_payloads("self_state_mutation_commit_receipts")
        if item.get("commit_status") == "committed_reviewed_self_state_successor"
    )
    if not commits:
        raise RuntimeError("blocked_package_139_package_137_commit_missing")
    commit = commits[-1]
    leaf = source.leaf
    if source.package_133_audit.get("audit_status") != PACKAGE_133_PASS_STATUS:
        raise RuntimeError("blocked_package_139_package_133_audit_invalid")
    if not all(
        (
            commit.get("child_self_state_record_id") == leaf.self_state_record_id,
            commit.get("child_self_state_sha256") == leaf.self_state_sha256,
            commit.get("package_134_active_head_advanced") is True,
        )
    ):
        raise RuntimeError("blocked_package_139_package_137_leaf_commit_mismatch")
    exact_leaf = all(
        (
            head.self_state_lineage_id == leaf.self_state_lineage_id,
            head.self_state_record_id == leaf.self_state_record_id,
            head.self_state_sha256 == leaf.self_state_sha256,
            head.self_state_version == leaf.self_state_version,
            head.lineage_generation == leaf.lineage_generation,
        )
    )
    if require_canonical_leaf and not exact_leaf:
        raise RuntimeError("blocked_package_139_active_head_not_canonical_leaf")
    p133_after = package_133_source_tree_sha256(roots[0])
    p137_after = authority_tree_sha256(roots[2])
    if p133_before != p133_after or p137_before != p137_after:
        raise RuntimeError("blocked_package_139_authority_source_modified_during_read")
    payload: dict[str, Any] = {
        "source_binding_id": "",
        "source_binding_sha256": "",
        "schema_version": SOURCE_SCHEMA_VERSION,
        "created_at": utc_now(),
        "package_133_audit_id": str(source.package_133_audit["audit_id"]),
        "package_133_audit_status": str(source.package_133_audit["audit_status"]),
        "package_134_audit_id": str(p134_audit["audit_id"]),
        "package_134_audit_status": str(p134_audit["audit_status"]),
        "package_137_audit_id": str(p137_audit["audit_id"]),
        "package_137_audit_status": str(p137_audit["audit_status"]),
        "package_138_audit_id": str(p138_audit["audit_id"]),
        "package_138_audit_status": str(p138_audit["audit_status"]),
        "self_state_lineage_id": leaf.self_state_lineage_id,
        "current_active_head_id": head.active_head_id,
        "current_active_head_sha256": head.active_head_sha256,
        "current_head_revision": head.head_revision,
        "current_self_state_record_id": head.self_state_record_id,
        "current_self_state_sha256": head.self_state_sha256,
        "canonical_leaf_self_state_record_id": leaf.self_state_record_id,
        "canonical_leaf_self_state_sha256": leaf.self_state_sha256,
        "active_head_matches_canonical_leaf": exact_leaf,
        "full_parent_hash_chain_verified": source.snapshot.full_parent_hash_chain_verified,
        "package_133_tree_sha256": p133_before,
        "package_137_tree_sha256": p137_before,
        "source_stores_integrity_verified": True,
        "source_record_refs": (
            str(source.package_133_audit["audit_id"]),
            str(p134_audit["audit_id"]),
            str(p137_audit["audit_id"]),
            str(p138_audit["audit_id"]),
            str(commit["commit_receipt_id"]),
            head.active_head_id,
            head.self_state_record_id,
        ),
    }
    binding = build_hashed_record(
        Package139AuthoritySourceBindingRecord,
        payload,
        id_field="source_binding_id",
        hash_field="source_binding_sha256",
        prefix="package_139_source_binding",
    )
    return Package139SourceBundle(
        package_133=source,
        active_head=head,
        package_134_audit=p134_audit,
        package_137_audit=p137_audit,
        package_137_commit_receipt=commit,
        package_138_audit=p138_audit,
        source_binding=binding,
    )


def authority_tree_sha256(root: str | Path) -> str:
    source_root = Path(root).resolve()
    if not source_root.is_dir():
        raise FileNotFoundError(source_root)
    entries: list[dict[str, Any]] = []
    for path in sorted(source_root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_symlink():
            raise ValueError("Package 139 authority source cannot contain symlinks")
        if path.is_file():
            data = path.read_bytes()
            entries.append(
                {
                    "relative_path": path.relative_to(source_root).as_posix(),
                    "size_bytes": len(data),
                    "sha256": sha256_bytes(data),
                }
            )
    return sha256_payload(entries)


def _latest_passing_audit(
    records: tuple[dict[str, Any], ...],
    status: str,
    owner: str,
) -> dict[str, Any]:
    passing = tuple(item for item in records if item.get("audit_status") == status)
    if not passing:
        raise RuntimeError(f"blocked_package_139_{owner}_passed_audit_missing")
    return dict(passing[-1])
