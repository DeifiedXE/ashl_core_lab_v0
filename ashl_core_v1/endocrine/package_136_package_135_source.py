"""Read-only Package 133-135 evidence source for Package 136."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.endocrine.drive_modulation_types import (
    PACKAGE_135_PASS_STATUS,
    SIGNAL_AUTHORITY,
    SOURCE_BINDING_SCHEMA_VERSION,
    Package135SignalAuthorityBindingRecord,
)
from ashl_core_v1.endocrine.drive_signal_trace_types import (
    DriveAuthoritySeparationRecord,
    DriveCrossSessionResetRecord,
    DriveRegulatorySignalTraceContract,
    DriveRegulatorySignalTraceRecord,
    DriveTraceProcessPairRecord,
    DriveTraceProcessReceipt,
)
from ashl_core_v1.endocrine.package_135_authority_source import (
    Package135AuthoritySourceBundle,
    load_package_135_authority_sources_read_only,
    source_tree_sha256,
)
from ashl_core_v1.endocrine.package_135_drive_signal_trace_store import (
    package_135_store_path,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now


@dataclass(frozen=True)
class Package136SourceBundle:
    package_133_134: Package135AuthoritySourceBundle
    package_135_audit: dict[str, Any]
    package_135_contract: DriveRegulatorySignalTraceContract
    package_135_separation: DriveAuthoritySeparationRecord
    selected_trace: DriveRegulatorySignalTraceRecord
    fresh_session_root_trace: DriveRegulatorySignalTraceRecord
    process_receipts: tuple[DriveTraceProcessReceipt, ...]
    process_pair: DriveTraceProcessPairRecord
    reset_record: DriveCrossSessionResetRecord
    source_binding: Package135SignalAuthorityBindingRecord
    package_135_tree_sha256: str


def load_package_136_sources_read_only(
    *,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_135_state_dir: str | Path,
) -> Package136SourceBundle:
    package_135_root = Path(package_135_state_dir).resolve()
    before_135 = source_tree_sha256(package_135_root)
    authority = load_package_135_authority_sources_read_only(
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
    )
    database = package_135_store_path(package_135_root)
    if not database.is_file():
        raise FileNotFoundError(database)
    uri = f"file:{database.as_posix()}?mode=ro&immutable=1"
    with closing(sqlite3.connect(uri, uri=True, timeout=10.0)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        if str(connection.execute("PRAGMA integrity_check").fetchone()[0]) != "ok":
            raise RuntimeError("blocked_corrupt_package_135_store")
        audits = _load_payloads(connection, "package_135_audits")
        contracts = _load_payloads(connection, "drive_trace_contracts")
        traces = _load_payloads(connection, "drive_signal_traces")
        separations = _load_payloads(connection, "drive_authority_separations")
        receipts = _load_payloads(connection, "drive_trace_process_receipts")
        pairs = _load_payloads(connection, "drive_trace_process_pairs")
        resets = _load_payloads(connection, "drive_cross_session_resets")

    passing = tuple(item for item in audits if item.get("audit_status") == PACKAGE_135_PASS_STATUS)
    if not passing:
        raise RuntimeError("blocked_package_135_audit_missing")
    audit = dict(passing[-1])
    if len(contracts) != 1 or len(separations) != 1 or len(pairs) != 1 or len(resets) != 1:
        raise RuntimeError("blocked_package_135_authority_evidence_cardinality")
    contract = _contract(contracts[0])
    separation = _separation(separations[0])
    typed_traces = tuple(DriveRegulatorySignalTraceRecord.from_dict(item) for item in traces)
    typed_receipts = tuple(_receipt(item) for item in receipts)
    process_pair = _pair(pairs[0])
    reset_record = _reset(resets[0])
    selected = tuple(item for item in typed_traces if item.sequence_index == 1)
    process_b_receipts = tuple(item for item in typed_receipts if item.process_role == "process_b")
    if len(selected) != 1 or len(process_b_receipts) != 1:
        raise RuntimeError("blocked_package_135_trace_selection_ambiguous")
    process_b_refs = set(process_b_receipts[0].signal_trace_refs)
    fresh_roots = tuple(
        item
        for item in typed_traces
        if item.signal_trace_id in process_b_refs
        and item.sequence_index == 0
        and item.parent_signal_trace_id is None
    )
    if len(fresh_roots) != 1:
        raise RuntimeError("blocked_package_135_fresh_root_missing_or_ambiguous")
    _validate_package_135_boundary(
        audit=audit,
        contract=contract,
        separation=separation,
        selected_trace=selected[0],
        fresh_root=fresh_roots[0],
        process_pair=process_pair,
        reset_record=reset_record,
        authority=authority,
    )
    binding = _build_source_binding(
        audit=audit,
        contract=contract,
        selected_trace=selected[0],
        fresh_root=fresh_roots[0],
        authority=authority,
    )
    if source_tree_sha256(package_135_root) != before_135:
        raise RuntimeError("blocked_package_135_source_changed_during_read")
    return Package136SourceBundle(
        package_133_134=authority,
        package_135_audit=audit,
        package_135_contract=contract,
        package_135_separation=separation,
        selected_trace=selected[0],
        fresh_session_root_trace=fresh_roots[0],
        process_receipts=typed_receipts,
        process_pair=process_pair,
        reset_record=reset_record,
        source_binding=binding,
        package_135_tree_sha256=before_135,
    )


def _load_payloads(connection: sqlite3.Connection, table: str) -> tuple[dict[str, Any], ...]:
    rows = connection.execute(
        f"SELECT payload_json, payload_sha256 FROM {table} ORDER BY row_id"
    ).fetchall()
    payloads: list[dict[str, Any]] = []
    for row in rows:
        payload = json.loads(str(row["payload_json"]))
        if str(row["payload_sha256"]) != sha256_payload(payload):
            raise RuntimeError(f"blocked_corrupt_package_135_payload:{table}")
        payloads.append(payload)
    return tuple(payloads)


def _contract(payload: dict[str, Any]) -> DriveRegulatorySignalTraceContract:
    values = dict(payload)
    values["allowed_source_kinds"] = tuple(values["allowed_source_kinds"])
    values["source_record_refs"] = tuple(values["source_record_refs"])
    return DriveRegulatorySignalTraceContract(**values)


def _separation(payload: dict[str, Any]) -> DriveAuthoritySeparationRecord:
    values = dict(payload)
    values["source_record_refs"] = tuple(values["source_record_refs"])
    return DriveAuthoritySeparationRecord(**values)


def _receipt(payload: dict[str, Any]) -> DriveTraceProcessReceipt:
    values = dict(payload)
    values["source_observation_refs"] = tuple(values["source_observation_refs"])
    values["signal_trace_refs"] = tuple(values["signal_trace_refs"])
    values["source_record_refs"] = tuple(values["source_record_refs"])
    return DriveTraceProcessReceipt(**values)


def _pair(payload: dict[str, Any]) -> DriveTraceProcessPairRecord:
    values = dict(payload)
    values["source_record_refs"] = tuple(values["source_record_refs"])
    return DriveTraceProcessPairRecord(**values)


def _reset(payload: dict[str, Any]) -> DriveCrossSessionResetRecord:
    values = dict(payload)
    values["source_record_refs"] = tuple(values["source_record_refs"])
    return DriveCrossSessionResetRecord(**values)


def _validate_package_135_boundary(
    *,
    audit: dict[str, Any],
    contract: DriveRegulatorySignalTraceContract,
    separation: DriveAuthoritySeparationRecord,
    selected_trace: DriveRegulatorySignalTraceRecord,
    fresh_root: DriveRegulatorySignalTraceRecord,
    process_pair: DriveTraceProcessPairRecord,
    reset_record: DriveCrossSessionResetRecord,
    authority: Package135AuthoritySourceBundle,
) -> None:
    required_true = (
        "package_133_remains_self_state_authority",
        "package_134_remains_recovery_authority",
        "trace_contract_verified",
        "source_provenance_verified",
        "trace_lineage_verified",
        "source_time_and_change_verified",
        "cross_session_reset_verified",
        "drive_tendency_affordance_purpose_action_separated",
        "append_only_store_verified",
    )
    required_false = (
        "package_134_drive_state_restored",
        "drive_trace_restored_across_session",
        "drive_trace_is_self_state_content",
        "drive_trace_is_memory_content",
        "runtime_modulation_created",
        "perception_modulation_created",
        "attention_modulation_created",
        "candidate_ordering_created",
        "thought_engine_influence_created",
        "memory_influence_created",
        "action_preference_created",
        "selected_action_created",
        "output_created",
        "purpose_created_or_expanded",
        "semantic_emotion_created",
        "package_136_modulation_authorized",
    )
    if not all(audit.get(name) is True for name in required_true):
        raise RuntimeError("blocked_package_135_positive_boundary_invalid")
    if not all(audit.get(name) is False for name in required_false):
        raise RuntimeError("blocked_package_135_forbidden_boundary_invalid")
    if audit.get("failure_reasons") != []:
        raise RuntimeError("blocked_package_135_audit_has_failures")
    if contract.authority_owner != SIGNAL_AUTHORITY or contract.runtime_modulation_allowed:
        raise RuntimeError("blocked_package_135_signal_authority_invalid")
    if contract.package_136_modulation_authorized:
        raise RuntimeError("blocked_package_135_improperly_authorized_package_136")
    if separation.separation_status != "passed_trace_only_authority_separation":
        raise RuntimeError("blocked_package_135_authority_separation_invalid")
    if selected_trace.runtime_session_id == fresh_root.runtime_session_id:
        raise RuntimeError("blocked_package_135_session_reset_missing")
    if fresh_root.sequence_index != 0 or fresh_root.parent_signal_trace_id is not None:
        raise RuntimeError("blocked_package_135_fresh_root_invalid")
    if process_pair.comparison_status != "passed_fresh_process_drive_trace_reset":
        raise RuntimeError("blocked_package_135_process_pair_invalid")
    if reset_record.reset_status != "passed_cross_session_drive_non_recovery":
        raise RuntimeError("blocked_package_135_reset_invalid")
    if authority.non_recovery_evidence.drive_state_restored:
        raise RuntimeError("blocked_package_134_drive_state_restored")
    if selected_trace.signal_trace_id not in set(audit.get("source_record_refs") or ()):
        raise RuntimeError("blocked_package_135_selected_trace_not_in_final_audit")


def _build_source_binding(
    *,
    audit: dict[str, Any],
    contract: DriveRegulatorySignalTraceContract,
    selected_trace: DriveRegulatorySignalTraceRecord,
    fresh_root: DriveRegulatorySignalTraceRecord,
    authority: Package135AuthoritySourceBundle,
) -> Package135SignalAuthorityBindingRecord:
    payload: dict[str, Any] = {
        "source_binding_id": "",
        "source_binding_sha256": "",
        "schema_version": SOURCE_BINDING_SCHEMA_VERSION,
        "created_at": utc_now(),
        "package_135_audit_id": str(audit["audit_id"]),
        "package_135_audit_status": str(audit["audit_status"]),
        "package_135_contract_id": contract.contract_id,
        "package_135_contract_sha256": contract.contract_sha256,
        "selected_signal_trace_id": selected_trace.signal_trace_id,
        "selected_signal_trace_sha256": selected_trace.signal_trace_sha256,
        "selected_runtime_session_id": selected_trace.runtime_session_id,
        "selected_signal_lineage_id": selected_trace.signal_lineage_id,
        "fresh_session_root_trace_id": fresh_root.signal_trace_id,
        "package_134_non_recovery_evidence_id": authority.non_recovery_evidence.evidence_id,
        "package_135_signal_authority": SIGNAL_AUTHORITY,
        "source_opened_read_only": True,
        "source_trace_mutation_allowed": False,
        "source_trace_recovery_allowed": False,
        "source_binding_status": "ready_for_same_session_audit_only_modulation",
        "source_record_refs": (
            str(audit["audit_id"]),
            contract.contract_id,
            selected_trace.signal_trace_id,
            fresh_root.signal_trace_id,
            authority.non_recovery_evidence.evidence_id,
        ),
    }
    identity = dict(payload)
    identity.pop("source_binding_id")
    identity.pop("source_binding_sha256")
    identity.pop("created_at")
    digest = sha256_payload(identity)
    payload["source_binding_id"] = f"package_135_signal_authority_binding:{digest[:16]}"
    payload["source_binding_sha256"] = digest
    return Package135SignalAuthorityBindingRecord(**payload)
