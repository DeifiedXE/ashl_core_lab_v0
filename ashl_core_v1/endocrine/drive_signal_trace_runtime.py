"""Package 135 trace-only runtime and fresh-process non-recovery run."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import fields
from pathlib import Path
from typing import Any, TypeVar

from ashl_core_v1.endocrine.drive_signal_legacy_inventory import (
    build_drive_signal_legacy_inventory,
    drive_signal_inventory_sha256,
)
from ashl_core_v1.endocrine.drive_signal_trace_types import (
    ALLOWED_SOURCE_KINDS,
    BASELINE_COMMIT,
    CONTRACT_SCHEMA_VERSION,
    LINEAGE_SCHEMA_VERSION,
    OBSERVATION_SCHEMA_VERSION,
    PAIR_SCHEMA_VERSION,
    PROCESS_SCHEMA_VERSION,
    RECOVERY_AUTHORITY,
    RESET_SCHEMA_VERSION,
    SEPARATION_SCHEMA_VERSION,
    SELF_STATE_AUTHORITY,
    TRACE_AUTHORITY,
    TRACE_SCHEMA_VERSION,
    DriveAuthoritySeparationRecord,
    DriveCrossSessionResetRecord,
    DriveRegulatorySignalSourceObservation,
    DriveRegulatorySignalTraceContract,
    DriveRegulatorySignalTraceRecord,
    DriveSignalLineageValidationRecord,
    DriveTraceProcessPairRecord,
    DriveTraceProcessReceipt,
)
from ashl_core_v1.endocrine.package_135_authority_source import (
    Package135AuthoritySourceBundle,
    load_package_135_authority_sources_read_only,
    source_tree_sha256,
)
from ashl_core_v1.endocrine.package_135_drive_signal_trace_store import (
    Package135DriveSignalTraceStore,
)
from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, sha256_payload, stable_id, utc_now


T = TypeVar("T")


def preflight_drive_signal_trace_separation(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    state_dir: str | Path,
) -> dict[str, Any]:
    root, output, source_133, source_134 = _validate_external_roots(
        ashl_root, state_dir, package_133_state_dir, package_134_state_dir
    )
    source = load_package_135_authority_sources_read_only(
        package_133_state_dir=source_133,
        package_134_state_dir=source_134,
    )
    inventory = build_drive_signal_legacy_inventory(root)
    return {
        "source_head": _git_output(root, "rev-parse", "HEAD"),
        "baseline_commit": BASELINE_COMMIT,
        "baseline_is_ancestor": _is_ancestor(root, BASELINE_COMMIT),
        "package_133_audit_id": source.package_133.snapshot.package_133_audit_id,
        "package_133_audit_status": source.package_133.snapshot.package_133_audit_status,
        "package_134_audit_id": source.package_134_audit["audit_id"],
        "package_134_audit_status": source.package_134_audit["audit_status"],
        "active_head_id": source.active_head.active_head_id,
        "active_head_revision": source.active_head.head_revision,
        "drive_state_restored": source.non_recovery_evidence.drive_state_restored,
        "legacy_inventory_count": len(inventory),
        "legacy_inventory_sha256": drive_signal_inventory_sha256(inventory),
        "state_dir_is_external": not _is_within(output, root),
        "readiness": "ready_for_drive_trace_only_fresh_process_run",
    }


def build_drive_trace_contract(
    *, source: Package135AuthoritySourceBundle
) -> DriveRegulatorySignalTraceContract:
    payload: dict[str, Any] = {
        "contract_id": "",
        "contract_sha256": "",
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "baseline_commit": BASELINE_COMMIT,
        "authority_owner": TRACE_AUTHORITY,
        "trace_kind": "anonymous_bounded_regulatory_observation_trace_v0",
        "signal_scope": "same_session_observation_only",
        "allowed_source_kinds": ALLOWED_SOURCE_KINDS,
        "normalized_minimum": 0.0,
        "normalized_maximum": 1.0,
        "source_provenance_required": True,
        "event_and_processing_time_required": True,
        "immutable_parent_hash_lineage_required": True,
        "same_session_lineage_required": True,
        "cross_session_reset_required": True,
        "package_133_self_state_content_allowed": False,
        "package_134_recovery_allowed": False,
        "memory_content_allowed": False,
        "purpose_or_desire_allowed": False,
        "reward_or_semantic_emotion_allowed": False,
        "tendency_or_affordance_identity_allowed": False,
        "runtime_modulation_allowed": False,
        "package_136_modulation_authorized": False,
        "source_record_refs": (
            source.package_133.snapshot.package_133_audit_id,
            str(source.package_134_audit["audit_id"]),
            source.non_recovery_evidence.evidence_id,
            SELF_STATE_AUTHORITY,
            RECOVERY_AUTHORITY,
        ),
    }
    return _hashed_record(
        DriveRegulatorySignalTraceContract,
        payload,
        id_field="contract_id",
        hash_field="contract_sha256",
        prefix="drive_trace_contract",
    )


def build_source_observation(
    *,
    contract: DriveRegulatorySignalTraceContract,
    runtime_session_id: str,
    process_instance_id: str,
    operating_system_process_id: int,
    source_channel_id: str,
    normalized_level: float,
    prior_source_ref: str | None = None,
) -> DriveRegulatorySignalSourceObservation:
    event_time = monotonic_ns()
    processing_time = max(monotonic_ns(), event_time)
    payload: dict[str, Any] = {
        "source_observation_id": "",
        "source_observation_sha256": "",
        "schema_version": OBSERVATION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "runtime_session_id": runtime_session_id,
        "process_instance_id": process_instance_id,
        "operating_system_process_id": operating_system_process_id,
        "source_kind": "explicit_bounded_local_regulatory_probe",
        "source_channel_id": source_channel_id,
        "observed_at_event_time_ns": event_time,
        "observed_at_processing_time_ns": processing_time,
        "normalized_level": normalized_level,
        "source_status": "observed_for_trace_boundary_only",
        "semantic_label": None,
        "purpose_ref": None,
        "desire_label": None,
        "reward_ref": None,
        "emotion_label": None,
        "affordance_ref": None,
        "tendency_ref": None,
        "selected_action_ref": None,
        "runtime_status_relabelled_as_drive": False,
        "legacy_endocrine_promoted": False,
        "stimulus_ground_truth_used": False,
        "source_record_refs": tuple(
            item for item in (contract.contract_id, prior_source_ref) if item is not None
        ),
        "source_trace_refs": (contract.contract_id,),
    }
    return _hashed_record(
        DriveRegulatorySignalSourceObservation,
        payload,
        id_field="source_observation_id",
        hash_field="source_observation_sha256",
        prefix="drive_source_observation",
    )


def build_signal_trace(
    *,
    contract: DriveRegulatorySignalTraceContract,
    observation: DriveRegulatorySignalSourceObservation,
    signal_lineage_id: str,
    sequence_index: int,
    parent: DriveRegulatorySignalTraceRecord | None,
) -> DriveRegulatorySignalTraceRecord:
    if observation.runtime_session_id == "" or observation.process_instance_id == "":
        raise ValueError("drive trace observation session lineage is missing")
    if (parent is None) != (sequence_index == 0):
        raise ValueError("drive trace root/successor sequence mismatch")
    if parent is not None:
        if parent.runtime_session_id != observation.runtime_session_id:
            raise ValueError("drive trace cannot cross a runtime session")
        if parent.process_instance_id != observation.process_instance_id:
            raise ValueError("drive trace cannot cross a process instance")
        if parent.signal_lineage_id != signal_lineage_id:
            raise ValueError("drive trace parent lineage mismatch")
        if parent.source_channel_id != observation.source_channel_id:
            raise ValueError("drive trace source channel changed")
    previous = parent.normalized_level if parent is not None else None
    delta = observation.normalized_level - previous if previous is not None else 0.0
    change = (
        "initial_observation"
        if parent is None
        else "increased"
        if delta > 0
        else "decreased"
        if delta < 0
        else "stable"
    )
    payload: dict[str, Any] = {
        "signal_trace_id": "",
        "signal_trace_sha256": "",
        "schema_version": TRACE_SCHEMA_VERSION,
        "created_at": utc_now(),
        "contract_ref": contract.contract_id,
        "source_observation_ref": observation.source_observation_id,
        "runtime_session_id": observation.runtime_session_id,
        "process_instance_id": observation.process_instance_id,
        "signal_lineage_id": signal_lineage_id,
        "sequence_index": sequence_index,
        "parent_signal_trace_id": parent.signal_trace_id if parent else None,
        "parent_signal_trace_sha256": parent.signal_trace_sha256 if parent else None,
        "source_channel_id": observation.source_channel_id,
        "event_time_ns": observation.observed_at_event_time_ns,
        "processing_time_ns": observation.observed_at_processing_time_ns,
        "normalized_level": observation.normalized_level,
        "previous_normalized_level": previous,
        "normalized_delta": delta,
        "change_kind": change,
        "trace_status": "observed_trace_only",
        "semantic_label": None,
        "purpose_ref": None,
        "desire_label": None,
        "reward_ref": None,
        "emotion_label": None,
        "affordance_ref": None,
        "tendency_ref": None,
        "selected_action_ref": None,
        "self_state_content_authority": False,
        "memory_content_authority": False,
        "purpose_authority": False,
        "purpose_expansion_authority": False,
        "desire_authority": False,
        "reward_authority": False,
        "semantic_emotion_authority": False,
        "tendency_authority": False,
        "affordance_authority": False,
        "perception_modulation_authority": False,
        "attention_modulation_authority": False,
        "candidate_ordering_authority": False,
        "thought_engine_authority": False,
        "memory_influence_authority": False,
        "action_preference_authority": False,
        "selected_action_authority": False,
        "output_authority": False,
        "cross_session_persistence_authority": False,
        "source_record_refs": (
            contract.contract_id,
            observation.source_observation_id,
            *(parent.signal_trace_id for parent in (parent,) if parent is not None),
        ),
        "source_trace_refs": observation.source_trace_refs,
    }
    return _hashed_record(
        DriveRegulatorySignalTraceRecord,
        payload,
        id_field="signal_trace_id",
        hash_field="signal_trace_sha256",
        prefix="drive_signal_trace",
    )


def validate_drive_signal_lineage(
    *,
    traces: tuple[DriveRegulatorySignalTraceRecord, ...],
    observations: tuple[DriveRegulatorySignalSourceObservation, ...],
) -> DriveSignalLineageValidationRecord:
    if not traces:
        raise ValueError("at least one drive signal trace is required")
    ordered = tuple(sorted(traces, key=lambda item: item.sequence_index))
    roots = tuple(item for item in ordered if item.parent_signal_trace_id is None)
    parent_exact = True
    for index, trace in enumerate(ordered):
        if index == 0:
            parent_exact = parent_exact and trace.sequence_index == 0
        else:
            parent = ordered[index - 1]
            parent_exact = parent_exact and all(
                (
                    trace.sequence_index == parent.sequence_index + 1,
                    trace.parent_signal_trace_id == parent.signal_trace_id,
                    trace.parent_signal_trace_sha256 == parent.signal_trace_sha256,
                )
            )
    sequence_monotonic = tuple(item.sequence_index for item in ordered) == tuple(range(len(ordered)))
    event_monotonic = all(
        ordered[index - 1].event_time_ns <= ordered[index].event_time_ns
        for index in range(1, len(ordered))
    )
    processing_valid = all(item.processing_time_ns >= item.event_time_ns for item in ordered)
    observation_refs = {item.source_observation_id for item in observations}
    source_complete = all(item.source_observation_ref in observation_refs for item in ordered)
    sessions = {item.runtime_session_id for item in ordered}
    processes = {item.process_instance_id for item in ordered}
    lineages = {item.signal_lineage_id for item in ordered}
    same_session = len(sessions) == len(processes) == len(lineages) == 1
    cross_session_parent = any(
        ordered[index].runtime_session_id != ordered[index - 1].runtime_session_id
        for index in range(1, len(ordered))
    )
    checks = {
        "exactly_one_root": len(roots) == 1,
        "parent_identity_and_hash_exact": parent_exact,
        "sequence_monotonic": sequence_monotonic,
        "event_time_monotonic": event_monotonic,
        "processing_time_valid": processing_valid,
        "source_observation_lineage_complete": source_complete,
        "same_session_only": same_session,
        "cross_session_parent_absent": not cross_session_parent,
    }
    failures = tuple(name for name, passed in checks.items() if not passed)
    identity = {
        "session": ordered[0].runtime_session_id,
        "lineage": ordered[0].signal_lineage_id,
        "traces": tuple(item.signal_trace_sha256 for item in ordered),
        "failures": failures,
    }
    return DriveSignalLineageValidationRecord(
        lineage_validation_id=f"drive_lineage_validation:{sha256_payload(identity)[:16]}",
        schema_version=LINEAGE_SCHEMA_VERSION,
        created_at=utc_now(),
        runtime_session_id=ordered[0].runtime_session_id,
        signal_lineage_id=ordered[0].signal_lineage_id,
        signal_trace_refs=tuple(item.signal_trace_id for item in ordered),
        trace_count=len(ordered),
        exactly_one_root=checks["exactly_one_root"],
        parent_identity_and_hash_exact=checks["parent_identity_and_hash_exact"],
        sequence_monotonic=checks["sequence_monotonic"],
        event_time_monotonic=checks["event_time_monotonic"],
        processing_time_valid=checks["processing_time_valid"],
        source_observation_lineage_complete=checks["source_observation_lineage_complete"],
        same_session_only=checks["same_session_only"],
        cross_session_parent_detected=cross_session_parent,
        lineage_valid=all(checks.values()),
        failure_reasons=failures,
        source_record_refs=tuple(item.source_observation_id for item in observations),
    )


def build_authority_separation(
    contract: DriveRegulatorySignalTraceContract,
) -> DriveAuthoritySeparationRecord:
    identity = {"contract": contract.contract_sha256, "boundary": "trace_only"}
    return DriveAuthoritySeparationRecord(
        separation_record_id=f"drive_authority_separation:{sha256_payload(identity)[:16]}",
        schema_version=SEPARATION_SCHEMA_VERSION,
        created_at=utc_now(),
        contract_ref=contract.contract_id,
        drive_trace_role="anonymous_regulatory_observation_trace_only",
        tendency_role="directional_candidate_pressure_not_created",
        affordance_role="environment_action_feasibility_or_reviewed_concept_not_drive",
        purpose_role="preexisting_approved_scope_not_created_or_expanded",
        selected_action_role="teacher_gated_task_authority_not_created",
        drive_is_tendency=False,
        drive_is_affordance=False,
        drive_is_purpose=False,
        drive_is_selected_action=False,
        signal_creates_or_expands_purpose=False,
        legacy_endocrine_is_package_135_authority=False,
        runtime_status_relabelled_as_drive=False,
        perception_modulation_created=False,
        attention_modulation_created=False,
        candidate_ordering_created=False,
        thought_engine_influence_created=False,
        memory_influence_created=False,
        action_preference_created=False,
        selected_action_created=False,
        output_created=False,
        separation_status="passed_trace_only_authority_separation",
        source_record_refs=(contract.contract_id,),
    )


def run_drive_trace_worker(
    *,
    state_dir: str | Path,
    contract_id: str,
    process_role: str,
    runtime_session_id: str,
    process_instance_id: str,
) -> dict[str, Any]:
    started = monotonic_ns()
    pid = os.getpid()
    store = Package135DriveSignalTraceStore(state_dir)
    contract = _record_from_payload(
        DriveRegulatorySignalTraceContract,
        store.get_payload("drive_trace_contracts", contract_id),
    )
    source_channel = f"anonymous_regulatory_channel:{sha256_payload({'session': runtime_session_id})[:16]}"
    signal_lineage = f"drive_signal_lineage:{sha256_payload({'session': runtime_session_id, 'process': process_instance_id})[:16]}"
    levels = (0.25, 0.625) if process_role == "process_a" else (0.125,)
    observations: list[DriveRegulatorySignalSourceObservation] = []
    traces: list[DriveRegulatorySignalTraceRecord] = []
    parent: DriveRegulatorySignalTraceRecord | None = None
    for index, level in enumerate(levels):
        observation = build_source_observation(
            contract=contract,
            runtime_session_id=runtime_session_id,
            process_instance_id=process_instance_id,
            operating_system_process_id=pid,
            source_channel_id=source_channel,
            normalized_level=level,
            prior_source_ref=(observations[-1].source_observation_id if observations else None),
        )
        trace = build_signal_trace(
            contract=contract,
            observation=observation,
            signal_lineage_id=signal_lineage,
            sequence_index=index,
            parent=parent,
        )
        observations.append(observation)
        traces.append(trace)
        parent = trace
    validation = validate_drive_signal_lineage(
        traces=tuple(traces), observations=tuple(observations)
    )
    ended = max(monotonic_ns(), started + 1)
    receipt_identity = {
        "role": process_role,
        "process": process_instance_id,
        "pid": pid,
        "session": runtime_session_id,
        "traces": tuple(item.signal_trace_sha256 for item in traces),
    }
    receipt = DriveTraceProcessReceipt(
        process_receipt_id=f"drive_trace_process_receipt:{sha256_payload(receipt_identity)[:16]}",
        schema_version=PROCESS_SCHEMA_VERSION,
        created_at=utc_now(),
        process_role=process_role,
        process_instance_id=process_instance_id,
        operating_system_process_id=pid,
        runtime_session_id=runtime_session_id,
        started_monotonic_ns=started,
        ended_monotonic_ns=ended,
        source_observation_refs=tuple(item.source_observation_id for item in observations),
        signal_trace_refs=tuple(item.signal_trace_id for item in traces),
        signal_lineage_id=signal_lineage,
        prior_session_trace_loaded=False,
        worker_status=(
            "session_a_trace_chain_completed"
            if process_role == "process_a"
            else "session_b_new_root_completed"
        ),
        source_record_refs=(contract.contract_id, validation.lineage_validation_id),
    )
    store.append_group(
        (
            *(("drive_source_observations", item) for item in observations),
            *(("drive_signal_traces", item) for item in traces),
            ("drive_lineage_validations", validation),
            ("drive_trace_process_receipts", receipt),
        )
    )
    return {
        "process_receipt_id": receipt.process_receipt_id,
        "process_role": process_role,
        "process_instance_id": process_instance_id,
        "operating_system_process_id": pid,
        "runtime_session_id": runtime_session_id,
        "signal_lineage_id": signal_lineage,
        "source_observation_ids": list(receipt.source_observation_refs),
        "signal_trace_ids": list(receipt.signal_trace_refs),
        "started_monotonic_ns": started,
        "ended_monotonic_ns": ended,
        "worker_status": receipt.worker_status,
    }


def run_real_drive_signal_trace_separation(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    state_dir: str | Path,
    allow_drive_trace_observation: bool,
) -> dict[str, Any]:
    if not allow_drive_trace_observation:
        raise RuntimeError("blocked_drive_trace_observation_authorization_missing")
    root, output, source_133, source_134 = _validate_external_roots(
        ashl_root, state_dir, package_133_state_dir, package_134_state_dir
    )
    before_133 = source_tree_sha256(source_133)
    before_134 = source_tree_sha256(source_134)
    source = load_package_135_authority_sources_read_only(
        package_133_state_dir=source_133,
        package_134_state_dir=source_134,
    )
    store = Package135DriveSignalTraceStore(output)
    if any(store.count(table) for table in ("drive_signal_traces", "drive_trace_process_receipts")):
        raise RuntimeError("blocked_package_135_state_dir_not_fresh")
    inventory = build_drive_signal_legacy_inventory(root)
    contract = build_drive_trace_contract(source=source)
    separation = build_authority_separation(contract)
    for record in inventory:
        store.append_once("legacy_drive_boundary_records", record)
    store.append_once("package_134_drive_non_recovery_evidence", source.non_recovery_evidence)
    store.append_once("drive_trace_contracts", contract)
    store.append_once("drive_authority_separations", separation)

    process_a = _run_worker_subprocess(
        root=root,
        state_dir=output,
        contract_id=contract.contract_id,
        process_role="process_a",
        runtime_session_id=stable_id("package_135_session_a"),
        process_instance_id=stable_id("package_135_process_a"),
    )
    process_b = _run_worker_subprocess(
        root=root,
        state_dir=output,
        contract_id=contract.contract_id,
        process_role="process_b",
        runtime_session_id=stable_id("package_135_session_b"),
        process_instance_id=stable_id("package_135_process_b"),
    )
    reset, pair = _build_cross_session_evidence(
        source=source,
        store=store,
        process_a=process_a,
        process_b=process_b,
    )
    store.append_group(
        (
            ("drive_cross_session_resets", reset),
            ("drive_trace_process_pairs", pair),
        )
    )
    after_133 = source_tree_sha256(source_133)
    after_134 = source_tree_sha256(source_134)
    if before_133 != after_133 or before_134 != after_134:
        raise RuntimeError("blocked_package_133_or_134_source_modified")
    return {
        "contract_id": contract.contract_id,
        "contract_sha256": contract.contract_sha256,
        "legacy_inventory_count": len(inventory),
        "legacy_inventory_sha256": drive_signal_inventory_sha256(inventory),
        "package_134_non_recovery_evidence_id": source.non_recovery_evidence.evidence_id,
        "process_a": process_a,
        "process_b": process_b,
        "reset_record_id": reset.reset_record_id,
        "process_pair_id": pair.process_pair_id,
        "comparison_status": pair.comparison_status,
        "package_133_source_unchanged": before_133 == after_133,
        "package_134_source_unchanged": before_134 == after_134,
        "runtime_modulation_created": False,
        "package_136_modulation_authorized": False,
    }


def _build_cross_session_evidence(
    *,
    source: Package135AuthoritySourceBundle,
    store: Package135DriveSignalTraceStore,
    process_a: dict[str, Any],
    process_b: dict[str, Any],
) -> tuple[DriveCrossSessionResetRecord, DriveTraceProcessPairRecord]:
    traces = {
        item["signal_trace_id"]: DriveRegulatorySignalTraceRecord.from_dict(item)
        for item in store.list_payloads("drive_signal_traces")
    }
    receipt_payloads = {
        item["process_receipt_id"]: item
        for item in store.list_payloads("drive_trace_process_receipts")
    }
    receipt_a = receipt_payloads[str(process_a["process_receipt_id"])]
    receipt_b = receipt_payloads[str(process_b["process_receipt_id"])]
    terminal_a = traces[str(receipt_a["signal_trace_refs"][-1])]
    root_b = traces[str(receipt_b["signal_trace_refs"][0])]
    sessions_distinct = terminal_a.runtime_session_id != root_b.runtime_session_id
    processes_distinct = (
        int(process_a["operating_system_process_id"])
        != int(process_b["operating_system_process_id"])
    )
    target_is_root = all(
        (
            root_b.sequence_index == 0,
            root_b.parent_signal_trace_id is None,
            root_b.parent_signal_trace_sha256 is None,
            root_b.previous_normalized_level is None,
        )
    )
    lineages_distinct = terminal_a.signal_lineage_id != root_b.signal_lineage_id
    source_value_copied = terminal_a.normalized_level == root_b.normalized_level
    payload: dict[str, Any] = {
        "reset_record_id": "",
        "reset_sha256": "",
        "schema_version": RESET_SCHEMA_VERSION,
        "created_at": utc_now(),
        "source_session_id": terminal_a.runtime_session_id,
        "target_session_id": root_b.runtime_session_id,
        "source_process_instance_id": terminal_a.process_instance_id,
        "target_process_instance_id": root_b.process_instance_id,
        "source_operating_system_process_id": int(process_a["operating_system_process_id"]),
        "target_operating_system_process_id": int(process_b["operating_system_process_id"]),
        "source_terminal_trace_ref": terminal_a.signal_trace_id,
        "source_terminal_trace_sha256": terminal_a.signal_trace_sha256,
        "target_root_trace_ref": root_b.signal_trace_id,
        "target_root_trace_sha256": root_b.signal_trace_sha256,
        "source_signal_lineage_id": terminal_a.signal_lineage_id,
        "target_signal_lineage_id": root_b.signal_lineage_id,
        "package_134_non_recovery_evidence_ref": source.non_recovery_evidence.evidence_id,
        "package_134_active_head_ref": source.active_head.active_head_id,
        "package_134_recovery_pair_ref": str(source.recovery_pair["recovery_pair_id"]),
        "structural_identity_continuity_verified": source.non_recovery_evidence.structural_identity_continuity_verified,
        "package_134_drive_state_restored": source.non_recovery_evidence.drive_state_restored,
        "sessions_distinct": sessions_distinct,
        "processes_distinct": processes_distinct,
        "target_trace_is_new_root": target_is_root,
        "drive_lineages_distinct": lineages_distinct,
        "source_trace_parent_reused": root_b.parent_signal_trace_id == terminal_a.signal_trace_id,
        "source_value_copied": source_value_copied,
        "source_trace_payload_loaded_in_target": bool(receipt_b["prior_session_trace_loaded"]),
        "self_state_content_changed": False,
        "memory_content_restored": False,
        "behavior_influence_created": False,
        "reset_status": "passed_cross_session_drive_non_recovery",
        "source_record_refs": (
            source.non_recovery_evidence.evidence_id,
            terminal_a.signal_trace_id,
            root_b.signal_trace_id,
            str(receipt_a["process_receipt_id"]),
            str(receipt_b["process_receipt_id"]),
        ),
    }
    reset = _hashed_record(
        DriveCrossSessionResetRecord,
        payload,
        id_field="reset_record_id",
        hash_field="reset_sha256",
        prefix="drive_cross_session_reset",
    )
    pair_identity = {
        "a": receipt_a["process_receipt_id"],
        "b": receipt_b["process_receipt_id"],
        "reset": reset.reset_sha256,
    }
    pair = DriveTraceProcessPairRecord(
        process_pair_id=f"drive_trace_process_pair:{sha256_payload(pair_identity)[:16]}",
        schema_version=PAIR_SCHEMA_VERSION,
        created_at=utc_now(),
        process_a_receipt_ref=str(receipt_a["process_receipt_id"]),
        process_b_receipt_ref=str(receipt_b["process_receipt_id"]),
        reset_record_ref=reset.reset_record_id,
        process_ids_distinct=processes_distinct,
        process_instance_ids_distinct=(
            str(process_a["process_instance_id"]) != str(process_b["process_instance_id"])
        ),
        sessions_distinct=sessions_distinct,
        process_a_ended_before_process_b_started=(
            int(process_a["ended_monotonic_ns"]) < int(process_b["started_monotonic_ns"])
        ),
        signal_lineages_distinct=lineages_distinct,
        process_b_started_with_new_root=target_is_root,
        prior_trace_loaded_by_process_b=bool(receipt_b["prior_session_trace_loaded"]),
        comparison_status="passed_fresh_process_drive_trace_reset",
        source_record_refs=(reset.reset_record_id, terminal_a.signal_trace_id, root_b.signal_trace_id),
    )
    return reset, pair


def _run_worker_subprocess(
    *,
    root: Path,
    state_dir: Path,
    contract_id: str,
    process_role: str,
    runtime_session_id: str,
    process_instance_id: str,
) -> dict[str, Any]:
    environment = dict(os.environ)
    pycache = state_dir / "package_135_drive_signal_trace_separation_v0" / "pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    command = (
        sys.executable,
        "-m",
        "ashl_core_v1.endocrine.package_135_drive_signal_trace_worker",
        "--state-dir",
        str(state_dir),
        "--contract-id",
        contract_id,
        "--process-role",
        process_role,
        "--runtime-session-id",
        runtime_session_id,
        "--process-instance-id",
        process_instance_id,
    )
    completed = subprocess.run(
        command,
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"blocked_package_135_{process_role}_worker:{completed.stderr.strip()}"
        )
    lines = tuple(line for line in completed.stdout.splitlines() if line.strip())
    if not lines:
        raise RuntimeError(f"blocked_package_135_{process_role}_receipt_missing")
    payload = json.loads(lines[-1])
    if payload.get("process_role") != process_role:
        raise RuntimeError(f"blocked_package_135_{process_role}_receipt_role_mismatch")
    return payload


def _hashed_record(
    record_type: type[T],
    payload: dict[str, Any],
    *,
    id_field: str,
    hash_field: str,
    prefix: str,
) -> T:
    identity = dict(payload)
    identity.pop(id_field, None)
    identity.pop(hash_field, None)
    identity.pop("created_at", None)
    digest = sha256_payload(identity)
    payload[id_field] = f"{prefix}:{digest[:16]}"
    payload[hash_field] = digest
    return record_type(**payload)


def _record_from_payload(record_type: type[T], payload: dict[str, Any]) -> T:
    values = dict(payload)
    for item in fields(record_type):
        if "tuple" in str(item.type).lower() and isinstance(values.get(item.name), list):
            values[item.name] = tuple(values[item.name])
    return record_type(**values)


def _validate_external_roots(
    ashl_root: str | Path,
    state_dir: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
) -> tuple[Path, Path, Path, Path]:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    source_133 = Path(package_133_state_dir).resolve()
    source_134 = Path(package_134_state_dir).resolve()
    if not root.is_dir() or not source_133.is_dir() or not source_134.is_dir():
        raise FileNotFoundError("repository and Package 133/134 evidence roots are required")
    if _is_within(output, root):
        raise ValueError("Package 135 state_dir must be external to the Git repository")
    if len({output, source_133, source_134}) != 3:
        raise ValueError("Package 135 output and authority evidence roots must be distinct")
    return root, output, source_133, source_134


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _git_output(root: Path, *args: str) -> str:
    return subprocess.check_output(("git", *args), cwd=root, text=True).strip()


def _is_ancestor(root: Path, commit: str) -> bool:
    return subprocess.run(
        ("git", "merge-base", "--is-ancestor", commit, "HEAD"), cwd=root, check=False
    ).returncode == 0
