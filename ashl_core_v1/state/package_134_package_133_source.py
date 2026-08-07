"""Read-only Package 133 lineage resolver used by Package 134."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.state.persistent_self_state_lineage import (
    validate_persistent_self_state_lineage,
)
from ashl_core_v1.state.persistent_self_state_schema import (
    PACKAGE_132_PASS_STATUS,
    PASS_STATUS as PACKAGE_133_PASS_STATUS,
    PersistentSelfStateRecord,
    PersistentSelfStateTransitionRecord,
)
from ashl_core_v1.state.persistent_self_state_store import package_133_store_path
from ashl_core_v1.state.persistent_session_recovery_types import (
    SOURCE_SCHEMA_VERSION,
    Package133SelfStateSourceSnapshot,
)


@dataclass(frozen=True)
class Package133SourceBundle:
    snapshot: Package133SelfStateSourceSnapshot
    states: tuple[PersistentSelfStateRecord, ...]
    transitions: tuple[PersistentSelfStateTransitionRecord, ...]
    package_133_audit: dict[str, Any]

    @property
    def root(self) -> PersistentSelfStateRecord:
        return self.states[0]

    @property
    def leaf(self) -> PersistentSelfStateRecord:
        return self.states[-1]


def load_package_133_source_read_only(
    package_133_state_dir: str | Path,
) -> Package133SourceBundle:
    source_root = Path(package_133_state_dir).resolve()
    database = package_133_store_path(source_root)
    if not database.is_file():
        raise FileNotFoundError(database)
    tree_sha256 = package_133_source_tree_sha256(source_root)
    uri = f"file:{database.as_posix()}?mode=ro&immutable=1"
    with closing(sqlite3.connect(uri, uri=True, timeout=10.0)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
        if integrity != "ok":
            raise RuntimeError("blocked_corrupt_package_133_store")
        state_payloads = _load_payloads(connection, "persistent_self_state_records")
        transition_payloads = _load_payloads(
            connection, "persistent_self_state_transition_records"
        )
        validation_payloads = _load_payloads(
            connection, "persistent_self_state_lineage_validations"
        )
        audit_payloads = _load_payloads(connection, "package_133_audits")
    passing_audits = tuple(
        item for item in audit_payloads if item.get("audit_status") == PACKAGE_133_PASS_STATUS
    )
    if len(passing_audits) != 1:
        raise RuntimeError(
            f"blocked_package_133_audit_missing_or_ambiguous:{len(passing_audits)}"
        )
    audit = dict(passing_audits[0])
    _validate_package_133_audit_boundary(audit)
    try:
        states = tuple(
            sorted(
                (PersistentSelfStateRecord.from_dict(item) for item in state_payloads),
                key=lambda item: item.self_state_version,
            )
        )
        transitions = tuple(
            PersistentSelfStateTransitionRecord.from_dict(item)
            for item in transition_payloads
        )
    except (KeyError, TypeError, ValueError) as error:
        raise RuntimeError("blocked_invalid_package_133_self_state_record") from error
    graph = _validate_unique_lineage(states, transitions)
    if len(validation_payloads) != len(transitions):
        raise RuntimeError("blocked_package_133_lineage_validation_cardinality")
    root = graph["root"]
    leaf = graph["leaf"]
    if audit.get("parent_self_state_record_id") != root.self_state_record_id:
        raise RuntimeError("blocked_package_133_audit_root_mismatch")
    if audit.get("child_self_state_record_id") != leaf.self_state_record_id:
        raise RuntimeError("blocked_package_133_audit_leaf_mismatch")
    snapshot_payload: dict[str, Any] = {
        "source_snapshot_id": "",
        "source_snapshot_sha256": "",
        "schema_version": SOURCE_SCHEMA_VERSION,
        "created_at": utc_now(),
        "package_133_audit_id": str(audit["audit_id"]),
        "package_133_audit_status": str(audit["audit_status"]),
        "representation_contract_id": str(audit["representation_contract_id"]),
        "self_state_lineage_id": leaf.self_state_lineage_id,
        "root_self_state_record_id": root.self_state_record_id,
        "leaf_self_state_record_id": leaf.self_state_record_id,
        "leaf_self_state_sha256": leaf.self_state_sha256,
        "leaf_self_state_version": leaf.self_state_version,
        "leaf_lineage_generation": leaf.lineage_generation,
        "state_record_count": len(states),
        "transition_record_count": len(transitions),
        "lineage_validation_count": len(validation_payloads),
        "unique_lineage_verified": True,
        "unique_leaf_verified": True,
        "full_parent_hash_chain_verified": True,
        "forbidden_content_absent": True,
        "package_133_recovery_authority_absent": True,
        "source_tree_sha256": tree_sha256,
        "source_record_refs": (
            str(audit["audit_id"]),
            str(audit["representation_contract_id"]),
            *(item.self_state_record_id for item in states),
            *(item.transition_id for item in transitions),
        ),
    }
    hash_payload = dict(snapshot_payload)
    hash_payload.pop("source_snapshot_id", None)
    hash_payload.pop("source_snapshot_sha256", None)
    hash_payload.pop("created_at", None)
    digest = sha256_payload(hash_payload)
    snapshot_payload["source_snapshot_sha256"] = digest
    snapshot_payload["source_snapshot_id"] = f"package_133_source_snapshot:{digest[:16]}"
    snapshot = Package133SelfStateSourceSnapshot(**snapshot_payload)
    return Package133SourceBundle(
        snapshot=snapshot,
        states=states,
        transitions=transitions,
        package_133_audit=audit,
    )


def package_133_source_tree_sha256(source_root: str | Path) -> str:
    root = Path(source_root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_symlink():
            raise ValueError("Package 133 evidence source cannot contain symlinks")
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


def _load_payloads(
    connection: sqlite3.Connection,
    table: str,
) -> tuple[dict[str, Any], ...]:
    rows = connection.execute(
        f"SELECT record_id, payload_json, payload_sha256 FROM {table} ORDER BY row_id"
    ).fetchall()
    payloads: list[dict[str, Any]] = []
    for row in rows:
        payload = json.loads(str(row["payload_json"]))
        if str(row["payload_sha256"]) != sha256_payload(payload):
            raise RuntimeError(f"blocked_package_133_payload_hash_mismatch:{table}")
        payloads.append(payload)
    return tuple(payloads)


def _validate_package_133_audit_boundary(audit: dict[str, Any]) -> None:
    required_true = (
        "package_132_closure_verified",
        "perception_line_remains_frozen",
        "representation_contract_verified",
        "parent_child_lineage_verified",
        "canonical_hash_chain_verified",
        "append_only_store_verified",
        "boundary_controls_passed",
        "fresh_regressions_passed",
    )
    required_false = (
        "legacy_state_payload_reused",
        "raw_perception_persisted",
        "world_fact_persisted",
        "memory_content_persisted",
        "semantic_history_persisted",
        "output_content_persisted",
        "cross_session_recovery_implemented",
        "active_head_created",
        "runtime_behavior_influence_created",
        "drive_signal_created",
        "memory_write_created",
        "perception_action_created",
        "thought_engine_used",
        "output_created",
        "package_134_implemented",
        "persistent_self_claimed",
    )
    if audit.get("package_132_audit_status") != PACKAGE_132_PASS_STATUS:
        raise RuntimeError("blocked_package_133_package_132_baseline_invalid")
    if not all(audit.get(name) is True for name in required_true):
        raise RuntimeError("blocked_package_133_audit_positive_boundary_invalid")
    if not all(audit.get(name) is False for name in required_false):
        raise RuntimeError("blocked_package_133_audit_negative_boundary_invalid")
    if audit.get("failure_reasons") != []:
        raise RuntimeError("blocked_package_133_audit_has_failures")


def _validate_unique_lineage(
    states: tuple[PersistentSelfStateRecord, ...],
    transitions: tuple[PersistentSelfStateTransitionRecord, ...],
) -> dict[str, PersistentSelfStateRecord]:
    if not states:
        raise RuntimeError("blocked_missing_package_133_self_state_lineage")
    lineages = {item.self_state_lineage_id for item in states}
    if len(lineages) != 1:
        raise RuntimeError("blocked_ambiguous_self_state_lineage")
    by_id = {item.self_state_record_id: item for item in states}
    if len(by_id) != len(states):
        raise RuntimeError("blocked_duplicate_package_133_self_state_identity")
    children: dict[str, list[str]] = {item.self_state_record_id: [] for item in states}
    incoming: dict[str, int] = {item.self_state_record_id: 0 for item in states}
    transition_by_child: dict[str, PersistentSelfStateTransitionRecord] = {}
    for transition in transitions:
        parent = by_id.get(transition.parent_self_state_record_id)
        child = by_id.get(transition.child_self_state_record_id)
        if parent is None or child is None:
            raise RuntimeError("blocked_package_133_transition_endpoint_missing")
        result = validate_persistent_self_state_lineage(parent, child, transition)
        if not result["valid"]:
            raise RuntimeError("blocked_package_133_parent_hash_lineage_invalid")
        children[parent.self_state_record_id].append(child.self_state_record_id)
        incoming[child.self_state_record_id] += 1
        transition_by_child[child.self_state_record_id] = transition
    if any(len(items) > 1 for items in children.values()):
        raise RuntimeError("blocked_ambiguous_package_133_lineage_fork")
    roots = tuple(by_id[item] for item, count in incoming.items() if count == 0)
    leaves = tuple(by_id[item] for item, values in children.items() if not values)
    if len(roots) != 1 or len(leaves) != 1:
        raise RuntimeError("blocked_ambiguous_package_133_root_or_leaf")
    if len(transitions) != len(states) - 1:
        raise RuntimeError("blocked_incomplete_package_133_lineage")
    cursor = leaves[0]
    visited = {cursor.self_state_record_id}
    while cursor.parent_self_state_record_id is not None:
        parent = by_id.get(cursor.parent_self_state_record_id)
        transition = transition_by_child.get(cursor.self_state_record_id)
        if parent is None or transition is None:
            raise RuntimeError("blocked_incomplete_package_133_parent_chain")
        if cursor.parent_self_state_sha256 != parent.self_state_sha256:
            raise RuntimeError("blocked_package_133_parent_hash_mismatch")
        cursor = parent
        if cursor.self_state_record_id in visited:
            raise RuntimeError("blocked_package_133_lineage_cycle")
        visited.add(cursor.self_state_record_id)
    if len(visited) != len(states) or cursor.self_state_record_id != roots[0].self_state_record_id:
        raise RuntimeError("blocked_disconnected_package_133_lineage")
    return {"root": roots[0], "leaf": leaves[0]}
