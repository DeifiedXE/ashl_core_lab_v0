"""Package 134 explicit fresh-process session recovery runtime."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, sha256_payload, stable_id, utc_now
from ashl_core_v1.state.package_134_package_133_source import (
    Package133SourceBundle,
    load_package_133_source_read_only,
    package_133_source_tree_sha256,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    ActiveHeadCASConflict,
    PersistentSessionRecoveryStore,
)
from ashl_core_v1.state.persistent_session_recovery_types import (
    ACTIVE_HEAD_AUTHORITY,
    AUTHORIZATION_SCHEMA_VERSION,
    BINDING_SCHEMA_VERSION,
    CAS_SCHEMA_VERSION,
    CONSUMPTION_SCHEMA_VERSION,
    HEAD_SCHEMA_VERSION,
    PAIR_SCHEMA_VERSION,
    PROCESS_SCHEMA_VERSION,
    REPRESENTATION_AUTHORITY,
    RESOLUTION_SCHEMA_VERSION,
    SHUTDOWN_SCHEMA_VERSION,
    ActiveHeadCASEventRecord,
    ActiveSelfStateHeadRecord,
    PersistentSessionIdentityBindingRecord,
    PersistentSessionRecoveryAuthorization,
    PersistentSessionRecoveryPairRecord,
    PersistentSessionRecoveryProcessReceipt,
    PersistentSessionRecoveryResolutionRecord,
    PersistentSessionShutdownRecord,
    RecoveryAuthorizationConsumptionRecord,
)


def preflight_persistent_session_recovery(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    state_dir: str | Path,
) -> dict[str, Any]:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    source = Path(package_133_state_dir).resolve()
    _validate_external_roots(root, output, source)
    bundle = load_package_133_source_read_only(source)
    store = PersistentSessionRecoveryStore(output)
    return {
        "baseline_head": _git_output(root, "rev-parse", "HEAD"),
        "package_133_audit_id": bundle.snapshot.package_133_audit_id,
        "package_133_audit_status": bundle.snapshot.package_133_audit_status,
        "package_133_source_snapshot_id": bundle.snapshot.source_snapshot_id,
        "self_state_lineage_id": bundle.snapshot.self_state_lineage_id,
        "canonical_leaf_self_state_record_id": bundle.snapshot.leaf_self_state_record_id,
        "canonical_leaf_self_state_sha256": bundle.snapshot.leaf_self_state_sha256,
        "unique_lineage_verified": bundle.snapshot.unique_lineage_verified,
        "unique_leaf_verified": bundle.snapshot.unique_leaf_verified,
        "parent_hash_chain_verified": bundle.snapshot.full_parent_hash_chain_verified,
        "package_133_recovery_authority_absent": bundle.snapshot.package_133_recovery_authority_absent,
        "package_134_active_head_count": store.active_head_count(),
        "recovery_readiness": "ready_for_explicit_fresh_process_recovery",
    }


def build_recovery_authorization(
    *,
    source: Package133SourceBundle,
    operation: str,
    target_session_id: str,
    target_process_instance_id: str,
    expected_head: ActiveSelfStateHeadRecord | None,
    created_at: str | None = None,
    expires_at: str | None = None,
) -> PersistentSessionRecoveryAuthorization:
    created = created_at or utc_now()
    expires = expires_at or (
        datetime.now(timezone.utc) + timedelta(minutes=10)
    ).isoformat()
    payload: dict[str, Any] = {
        "authorization_id": "",
        "authorization_sha256": "",
        "schema_version": AUTHORIZATION_SCHEMA_VERSION,
        "created_at": created,
        "expires_at": expires,
        "operation": operation,
        "authorization_source": "explicit_local_operator_request",
        "authorized_by": "local_operator",
        "explicit_authorization": True,
        "package_133_source_snapshot_ref": source.snapshot.source_snapshot_id,
        "target_self_state_lineage_id": source.snapshot.self_state_lineage_id,
        "target_self_state_record_id": source.snapshot.leaf_self_state_record_id,
        "target_self_state_sha256": source.snapshot.leaf_self_state_sha256,
        "expected_active_head_id": expected_head.active_head_id if expected_head else None,
        "expected_active_head_sha256": expected_head.active_head_sha256 if expected_head else None,
        "expected_head_revision": expected_head.head_revision if expected_head else 0,
        "expected_bound_session_id": expected_head.bound_session_id if expected_head else None,
        "target_session_id": target_session_id,
        "target_process_instance_id": target_process_instance_id,
        "one_use_only": True,
        "authorization_status": "authorized_for_exact_identity_transition",
        "source_record_refs": (
            source.snapshot.source_snapshot_id,
            source.snapshot.package_133_audit_id,
            source.snapshot.leaf_self_state_record_id,
            *(expected_head.source_record_refs[-1:] if expected_head else ()),
        ),
    }
    identity_payload = dict(payload)
    identity_payload.pop("authorization_id", None)
    identity_payload.pop("authorization_sha256", None)
    digest = sha256_payload(identity_payload)
    payload["authorization_sha256"] = digest
    payload["authorization_id"] = f"session_recovery_authorization:{digest[:16]}"
    return PersistentSessionRecoveryAuthorization(**payload)


def run_process_a_initialization(
    *,
    package_133_state_dir: str | Path,
    state_dir: str | Path,
    authorization_id: str,
    session_id: str,
    process_instance_id: str,
) -> dict[str, Any]:
    started = monotonic_ns()
    pid = os.getpid()
    source = load_package_133_source_read_only(package_133_state_dir)
    store = PersistentSessionRecoveryStore(state_dir)
    store.append_once("package_133_source_snapshots", source.snapshot)
    authorization = store.get_authorization(authorization_id)
    validate_recovery_authorization(
        store=store,
        authorization=authorization,
        source=source,
        operation="initialize_active_head",
        session_id=session_id,
        process_instance_id=process_instance_id,
    )
    head = build_initial_active_head(
        source=source,
        session_id=session_id,
        process_instance_id=process_instance_id,
        authorization_id=authorization.authorization_id,
    )
    cas_event = build_successful_cas_event(
        authorization=authorization,
        previous_head=None,
        new_head=head,
    )
    consumption = build_authorization_consumption(
        authorization=authorization,
        status="consumed_applied",
        failure_reason=None,
    )
    binding = build_identity_binding(
        source=source,
        head=head,
        binding_kind="initial_session_binding",
        session_id=session_id,
        process_instance_id=process_instance_id,
        operating_system_process_id=pid,
        recovered_from_session_id=None,
        authorization_id=authorization.authorization_id,
    )
    store.initialize_active_head_atomic(
        authorization=authorization,
        active_head=head,
        cas_event=cas_event,
        consumption=consumption,
        identity_binding=binding,
    )
    shutdown = build_clean_shutdown_record(
        head=head,
        session_id=session_id,
        process_instance_id=process_instance_id,
        operating_system_process_id=pid,
        identity_binding_id=binding.binding_id,
    )
    store.append_record("persistent_session_shutdown_records", shutdown)
    ended = monotonic_ns()
    receipt = build_process_receipt(
        process_role="process_a",
        process_instance_id=process_instance_id,
        operating_system_process_id=pid,
        session_id=session_id,
        started_monotonic_ns=started,
        ended_monotonic_ns=max(ended, started + 1),
        authorization_id=authorization.authorization_id,
        identity_binding_ref=binding.binding_id,
        active_head_before_sha256=None,
        active_head_after_sha256=head.active_head_sha256,
        shutdown_record_ref=shutdown.shutdown_record_id,
        worker_status="initialized_and_cleanly_shutdown",
        source_refs=(
            source.snapshot.source_snapshot_id,
            cas_event.cas_event_id,
            binding.binding_id,
            shutdown.shutdown_record_id,
        ),
    )
    store.append_record("persistent_session_recovery_process_receipts", receipt)
    return {
        "process_receipt_id": receipt.process_receipt_id,
        "process_instance_id": process_instance_id,
        "operating_system_process_id": pid,
        "session_id": session_id,
        "identity_binding_id": binding.binding_id,
        "active_head_id": head.active_head_id,
        "active_head_sha256": head.active_head_sha256,
        "head_revision": head.head_revision,
        "shutdown_record_id": shutdown.shutdown_record_id,
        "worker_status": receipt.worker_status,
    }


def run_process_b_recovery(
    *,
    package_133_state_dir: str | Path,
    state_dir: str | Path,
    authorization_id: str,
    session_id: str,
    process_instance_id: str,
) -> dict[str, Any]:
    started = monotonic_ns()
    pid = os.getpid()
    source = load_package_133_source_read_only(package_133_state_dir)
    store = PersistentSessionRecoveryStore(state_dir)
    store.append_once("package_133_source_snapshots", source.snapshot)
    authorization = store.get_authorization(authorization_id)
    validate_recovery_authorization(
        store=store,
        authorization=authorization,
        source=source,
        operation="recover_session",
        session_id=session_id,
        process_instance_id=process_instance_id,
    )
    try:
        head = store.get_active_head()
    except RuntimeError as error:
        return _record_blocked_worker(
            store=store,
            source=source,
            authorization=authorization,
            process_role="process_b",
            process_instance_id=process_instance_id,
            operating_system_process_id=pid,
            session_id=session_id,
            started_monotonic_ns=started,
            failure_reason=str(error),
            observed_head=None,
        )
    shutdowns = store.list_payloads("persistent_session_shutdown_records")
    resolution = build_recovery_resolution(
        source=source,
        authorization=authorization,
        head=head,
        active_head_candidate_count=store.active_head_count(),
        shutdown_payloads=shutdowns,
    )
    if resolution.decision != "allow_exact_recovery_cas":
        return _record_blocked_worker(
            store=store,
            source=source,
            authorization=authorization,
            process_role="process_b",
            process_instance_id=process_instance_id,
            operating_system_process_id=pid,
            session_id=session_id,
            started_monotonic_ns=started,
            failure_reason=resolution.failure_reasons[0],
            observed_head=head,
            resolution=resolution,
        )
    new_head = build_recovered_active_head(
        previous_head=head,
        authorization=authorization,
        session_id=session_id,
        process_instance_id=process_instance_id,
    )
    cas_event = build_successful_cas_event(
        authorization=authorization,
        previous_head=head,
        new_head=new_head,
    )
    consumption = build_authorization_consumption(
        authorization=authorization,
        status="consumed_applied",
        failure_reason=None,
    )
    binding = build_identity_binding(
        source=source,
        head=new_head,
        binding_kind="fresh_process_recovery_binding",
        session_id=session_id,
        process_instance_id=process_instance_id,
        operating_system_process_id=pid,
        recovered_from_session_id=head.bound_session_id,
        authorization_id=authorization.authorization_id,
    )
    try:
        store.recover_active_head_atomic(
            authorization=authorization,
            expected_head=head,
            new_head=new_head,
            cas_event=cas_event,
            consumption=consumption,
            identity_binding=binding,
            resolution=resolution,
        )
    except ActiveHeadCASConflict as error:
        return _record_blocked_worker(
            store=store,
            source=source,
            authorization=authorization,
            process_role="process_b",
            process_instance_id=process_instance_id,
            operating_system_process_id=pid,
            session_id=session_id,
            started_monotonic_ns=started,
            failure_reason=str(error),
            observed_head=store.get_active_head(),
        )
    ended = monotonic_ns()
    receipt = build_process_receipt(
        process_role="process_b",
        process_instance_id=process_instance_id,
        operating_system_process_id=pid,
        session_id=session_id,
        started_monotonic_ns=started,
        ended_monotonic_ns=max(ended, started + 1),
        authorization_id=authorization.authorization_id,
        identity_binding_ref=binding.binding_id,
        active_head_before_sha256=head.active_head_sha256,
        active_head_after_sha256=new_head.active_head_sha256,
        shutdown_record_ref=None,
        worker_status="fresh_process_recovery_completed",
        source_refs=(
            source.snapshot.source_snapshot_id,
            resolution.resolution_id,
            cas_event.cas_event_id,
            binding.binding_id,
        ),
    )
    store.append_record("persistent_session_recovery_process_receipts", receipt)
    return {
        "process_receipt_id": receipt.process_receipt_id,
        "process_instance_id": process_instance_id,
        "operating_system_process_id": pid,
        "session_id": session_id,
        "identity_binding_id": binding.binding_id,
        "active_head_id": new_head.active_head_id,
        "active_head_before_sha256": head.active_head_sha256,
        "active_head_sha256": new_head.active_head_sha256,
        "head_revision": new_head.head_revision,
        "recovered_from_session_id": head.bound_session_id,
        "resolution_id": resolution.resolution_id,
        "worker_status": receipt.worker_status,
    }


def run_real_fresh_process_recovery(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    state_dir: str | Path,
    allow_session_recovery: bool,
) -> dict[str, Any]:
    if not allow_session_recovery:
        raise RuntimeError("blocked_session_recovery_authorization_missing")
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    source_root = Path(package_133_state_dir).resolve()
    _validate_external_roots(root, output, source_root)
    source_before = package_133_source_tree_sha256(source_root)
    source = load_package_133_source_read_only(source_root)
    store = PersistentSessionRecoveryStore(output)
    if store.active_head_count() or store.count("persistent_session_recovery_process_receipts"):
        raise RuntimeError("blocked_package_134_state_dir_not_fresh")
    store.append_once("package_133_source_snapshots", source.snapshot)

    process_a_instance = stable_id("package_134_process_a")
    process_a_session = stable_id("package_134_session_a")
    authorization_a = build_recovery_authorization(
        source=source,
        operation="initialize_active_head",
        target_session_id=process_a_session,
        target_process_instance_id=process_a_instance,
        expected_head=None,
    )
    store.append_record("persistent_session_recovery_authorizations", authorization_a)
    process_a = run_recovery_worker_subprocess(
        ashl_root=root,
        package_133_state_dir=source_root,
        state_dir=output,
        process_role="process_a",
        authorization_id=authorization_a.authorization_id,
        session_id=process_a_session,
        process_instance_id=process_a_instance,
    )

    initialized_head = store.get_active_head()
    process_b_instance = stable_id("package_134_process_b")
    process_b_session = stable_id("package_134_session_b")
    authorization_b = build_recovery_authorization(
        source=source,
        operation="recover_session",
        target_session_id=process_b_session,
        target_process_instance_id=process_b_instance,
        expected_head=initialized_head,
    )
    store.append_record("persistent_session_recovery_authorizations", authorization_b)
    process_b = run_recovery_worker_subprocess(
        ashl_root=root,
        package_133_state_dir=source_root,
        state_dir=output,
        process_role="process_b",
        authorization_id=authorization_b.authorization_id,
        session_id=process_b_session,
        process_instance_id=process_b_instance,
    )
    source_after = package_133_source_tree_sha256(source_root)
    pair = build_recovery_pair(
        store=store,
        source=source,
        process_a=process_a,
        process_b=process_b,
        package_133_source_unchanged=(source_before == source_after),
    )
    store.append_record("persistent_session_recovery_pairs", pair)
    return {
        "process_a": process_a,
        "process_b": process_b,
        "initialization_authorization_id": authorization_a.authorization_id,
        "recovery_authorization_id": authorization_b.authorization_id,
        "recovery_pair_id": pair.recovery_pair_id,
        "recovery_pair_status": pair.comparison_status,
        "package_133_source_unchanged": source_before == source_after,
    }


def run_recovery_worker_subprocess(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    state_dir: str | Path,
    process_role: str,
    authorization_id: str,
    session_id: str,
    process_instance_id: str,
) -> dict[str, Any]:
    command = (
        sys.executable,
        "-m",
        "ashl_core_v1.state.package_134_persistent_session_recovery_worker",
        "--process-role",
        process_role,
        "--package-133-state-dir",
        str(Path(package_133_state_dir)),
        "--state-dir",
        str(Path(state_dir)),
        "--authorization-id",
        authorization_id,
        "--session-id",
        session_id,
        "--process-instance-id",
        process_instance_id,
    )
    environment = dict(os.environ)
    pycache = Path(state_dir) / "package_134_worker_pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    try:
        completed = subprocess.run(
            command,
            cwd=Path(ashl_root),
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30.0,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("blocked_package_134_worker_timeout") from error
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "Package 134 worker failed"
        raise RuntimeError(detail)
    lines = tuple(line for line in completed.stdout.splitlines() if line.strip())
    if not lines:
        raise RuntimeError("blocked_package_134_worker_receipt_missing")
    payload = dict(json.loads(lines[-1]))
    if payload.get("worker_status") not in {
        "initialized_and_cleanly_shutdown",
        "fresh_process_recovery_completed",
    }:
        raise RuntimeError("blocked_package_134_worker_status")
    return payload


def build_initial_active_head(
    *,
    source: Package133SourceBundle,
    session_id: str,
    process_instance_id: str,
    authorization_id: str,
) -> ActiveSelfStateHeadRecord:
    created = utc_now()
    payload: dict[str, Any] = {
        "active_head_id": f"active_self_state_head:{sha256_payload({'lineage': source.snapshot.self_state_lineage_id})[:16]}",
        "active_head_sha256": "",
        "schema_version": HEAD_SCHEMA_VERSION,
        "created_at": created,
        "updated_at": created,
        "self_state_lineage_id": source.snapshot.self_state_lineage_id,
        "self_state_record_id": source.snapshot.leaf_self_state_record_id,
        "self_state_sha256": source.snapshot.leaf_self_state_sha256,
        "self_state_version": source.snapshot.leaf_self_state_version,
        "lineage_generation": source.snapshot.leaf_lineage_generation,
        "head_revision": 1,
        "bound_session_id": session_id,
        "bound_process_instance_id": process_instance_id,
        "previous_active_head_sha256": None,
        "authority_status": "active_identity_binding",
        "representation_authority": REPRESENTATION_AUTHORITY,
        "active_head_authority": ACTIVE_HEAD_AUTHORITY,
        "source_record_refs": (
            source.snapshot.source_snapshot_id,
            source.snapshot.leaf_self_state_record_id,
            authorization_id,
        ),
    }
    digest_payload = dict(payload)
    digest_payload.pop("active_head_sha256", None)
    payload["active_head_sha256"] = sha256_payload(digest_payload)
    return ActiveSelfStateHeadRecord(**payload)


def build_recovered_active_head(
    *,
    previous_head: ActiveSelfStateHeadRecord,
    authorization: PersistentSessionRecoveryAuthorization,
    session_id: str,
    process_instance_id: str,
) -> ActiveSelfStateHeadRecord:
    payload = previous_head.to_dict()
    payload.update(
        {
            "active_head_sha256": "",
            "updated_at": utc_now(),
            "head_revision": previous_head.head_revision + 1,
            "bound_session_id": session_id,
            "bound_process_instance_id": process_instance_id,
            "previous_active_head_sha256": previous_head.active_head_sha256,
            "source_record_refs": previous_head.source_record_refs
            + (authorization.authorization_id,),
        }
    )
    digest_payload = dict(payload)
    digest_payload.pop("active_head_sha256", None)
    payload["active_head_sha256"] = sha256_payload(digest_payload)
    return ActiveSelfStateHeadRecord.from_dict(payload)


def build_successful_cas_event(
    *,
    authorization: PersistentSessionRecoveryAuthorization,
    previous_head: ActiveSelfStateHeadRecord | None,
    new_head: ActiveSelfStateHeadRecord,
) -> ActiveHeadCASEventRecord:
    core = {
        "authorization": authorization.authorization_id,
        "operation": authorization.operation,
        "previous": previous_head.active_head_sha256 if previous_head else None,
        "new": new_head.active_head_sha256,
    }
    return ActiveHeadCASEventRecord(
        cas_event_id=f"active_head_cas_event:{sha256_payload(core)[:16]}",
        schema_version=CAS_SCHEMA_VERSION,
        created_at=utc_now(),
        authorization_id=authorization.authorization_id,
        operation=authorization.operation,
        active_head_id=new_head.active_head_id,
        expected_head_revision=authorization.expected_head_revision,
        expected_active_head_sha256=authorization.expected_active_head_sha256,
        observed_head_revision=previous_head.head_revision if previous_head else None,
        observed_active_head_sha256=(
            previous_head.active_head_sha256 if previous_head else None
        ),
        previous_bound_session_id=(previous_head.bound_session_id if previous_head else None),
        requested_bound_session_id=new_head.bound_session_id,
        new_head_revision=new_head.head_revision,
        new_active_head_sha256=new_head.active_head_sha256,
        cas_succeeded=True,
        transaction_committed=True,
        self_state_record_unchanged=True,
        self_state_lineage_unchanged=True,
        failure_reason=None,
        source_record_refs=(
            authorization.authorization_id,
            new_head.active_head_id,
            new_head.self_state_record_id,
        ),
    )


def build_blocked_cas_event(
    *,
    authorization: PersistentSessionRecoveryAuthorization,
    observed_head: ActiveSelfStateHeadRecord | None,
    failure_reason: str,
) -> ActiveHeadCASEventRecord:
    core = {
        "authorization": authorization.authorization_id,
        "failure": failure_reason,
        "observed": observed_head.active_head_sha256 if observed_head else None,
    }
    return ActiveHeadCASEventRecord(
        cas_event_id=f"active_head_cas_event:{sha256_payload(core)[:16]}",
        schema_version=CAS_SCHEMA_VERSION,
        created_at=utc_now(),
        authorization_id=authorization.authorization_id,
        operation=authorization.operation,
        active_head_id=(
            observed_head.active_head_id
            if observed_head
            else str(authorization.expected_active_head_id or "active_self_state_head:missing")
        ),
        expected_head_revision=authorization.expected_head_revision,
        expected_active_head_sha256=authorization.expected_active_head_sha256,
        observed_head_revision=observed_head.head_revision if observed_head else None,
        observed_active_head_sha256=(observed_head.active_head_sha256 if observed_head else None),
        previous_bound_session_id=(observed_head.bound_session_id if observed_head else None),
        requested_bound_session_id=authorization.target_session_id,
        new_head_revision=None,
        new_active_head_sha256=None,
        cas_succeeded=False,
        transaction_committed=False,
        self_state_record_unchanged=True,
        self_state_lineage_unchanged=True,
        failure_reason=failure_reason,
        source_record_refs=(
            authorization.authorization_id,
            authorization.target_self_state_record_id,
        ),
    )


def build_authorization_consumption(
    *,
    authorization: PersistentSessionRecoveryAuthorization,
    status: str,
    failure_reason: str | None,
) -> RecoveryAuthorizationConsumptionRecord:
    return RecoveryAuthorizationConsumptionRecord(
        consumption_id=(
            f"recovery_authorization_consumption:{sha256_payload({'authorization': authorization.authorization_id})[:16]}"
        ),
        schema_version=CONSUMPTION_SCHEMA_VERSION,
        created_at=utc_now(),
        authorization_id=authorization.authorization_id,
        operation=authorization.operation,
        process_instance_id=authorization.target_process_instance_id,
        session_id=authorization.target_session_id,
        consumption_status=status,
        failure_reason=failure_reason,
        source_record_refs=(authorization.authorization_id,),
    )


def build_identity_binding(
    *,
    source: Package133SourceBundle,
    head: ActiveSelfStateHeadRecord,
    binding_kind: str,
    session_id: str,
    process_instance_id: str,
    operating_system_process_id: int,
    recovered_from_session_id: str | None,
    authorization_id: str,
) -> PersistentSessionIdentityBindingRecord:
    payload: dict[str, Any] = {
        "binding_id": "",
        "binding_sha256": "",
        "schema_version": BINDING_SCHEMA_VERSION,
        "created_at": utc_now(),
        "binding_kind": binding_kind,
        "session_id": session_id,
        "process_instance_id": process_instance_id,
        "operating_system_process_id": operating_system_process_id,
        "self_state_lineage_id": head.self_state_lineage_id,
        "self_state_record_id": head.self_state_record_id,
        "self_state_sha256": head.self_state_sha256,
        "self_state_version": head.self_state_version,
        "active_head_id": head.active_head_id,
        "active_head_sha256": head.active_head_sha256,
        "head_revision": head.head_revision,
        "recovered_from_session_id": recovered_from_session_id,
        "same_lineage_identity_verified": (
            head.self_state_lineage_id == source.snapshot.self_state_lineage_id
            and head.self_state_record_id == source.snapshot.leaf_self_state_record_id
            and head.self_state_sha256 == source.snapshot.leaf_self_state_sha256
        ),
        "parent_hash_chain_verified": source.snapshot.full_parent_hash_chain_verified,
        "representation_payload_loaded": False,
        "memory_content_restored": False,
        "perception_history_restored": False,
        "working_readback_restored": False,
        "drive_state_restored": False,
        "attention_state_restored": False,
        "thought_engine_state_restored": False,
        "output_state_restored": False,
        "action_state_restored": False,
        "learning_created": False,
        "behavior_influence_created": False,
        "binding_status": "bound_to_verified_package_133_identity",
        "source_record_refs": (
            source.snapshot.source_snapshot_id,
            head.self_state_record_id,
            head.active_head_id,
            authorization_id,
        ),
    }
    identity_payload = dict(payload)
    identity_payload.pop("binding_id", None)
    identity_payload.pop("binding_sha256", None)
    digest = sha256_payload(identity_payload)
    payload["binding_sha256"] = digest
    payload["binding_id"] = f"session_identity_binding:{digest[:16]}"
    return PersistentSessionIdentityBindingRecord(**payload)


def build_clean_shutdown_record(
    *,
    head: ActiveSelfStateHeadRecord,
    session_id: str,
    process_instance_id: str,
    operating_system_process_id: int,
    identity_binding_id: str,
) -> PersistentSessionShutdownRecord:
    core = {
        "head": head.active_head_sha256,
        "session": session_id,
        "process": process_instance_id,
    }
    return PersistentSessionShutdownRecord(
        shutdown_record_id=f"persistent_session_shutdown:{sha256_payload(core)[:16]}",
        schema_version=SHUTDOWN_SCHEMA_VERSION,
        created_at=utc_now(),
        session_id=session_id,
        process_instance_id=process_instance_id,
        operating_system_process_id=operating_system_process_id,
        active_head_id=head.active_head_id,
        active_head_sha256=head.active_head_sha256,
        head_revision=head.head_revision,
        shutdown_monotonic_ns=monotonic_ns(),
        shutdown_kind="clean_process_shutdown",
        clean_shutdown_verified=True,
        active_head_payload_modified=False,
        self_state_history_modified=False,
        source_record_refs=(head.active_head_id, identity_binding_id),
    )


def build_recovery_resolution(
    *,
    source: Package133SourceBundle,
    authorization: PersistentSessionRecoveryAuthorization,
    head: ActiveSelfStateHeadRecord,
    active_head_candidate_count: int,
    shutdown_payloads: tuple[dict[str, Any], ...],
) -> PersistentSessionRecoveryResolutionRecord:
    exact_shutdowns = tuple(
        item
        for item in shutdown_payloads
        if item.get("session_id") == head.bound_session_id
        and item.get("process_instance_id") == head.bound_process_instance_id
        and item.get("active_head_sha256") == head.active_head_sha256
        and item.get("head_revision") == head.head_revision
        and item.get("clean_shutdown_verified") is True
        and item.get("shutdown_kind") == "clean_process_shutdown"
    )
    head_matches_leaf = all(
        (
            head.self_state_lineage_id == source.snapshot.self_state_lineage_id,
            head.self_state_record_id == source.snapshot.leaf_self_state_record_id,
            head.self_state_sha256 == source.snapshot.leaf_self_state_sha256,
            head.self_state_version == source.snapshot.leaf_self_state_version,
            head.lineage_generation == source.snapshot.leaf_lineage_generation,
        )
    )
    expected_matches = all(
        (
            authorization.expected_active_head_id == head.active_head_id,
            authorization.expected_active_head_sha256 == head.active_head_sha256,
            authorization.expected_head_revision == head.head_revision,
            authorization.expected_bound_session_id == head.bound_session_id,
        )
    )
    checks = {
        "unique_active_head": active_head_candidate_count == 1,
        "unique_lineage": source.snapshot.unique_lineage_verified,
        "head_integrity": True,
        "head_matches_leaf": head_matches_leaf,
        "parent_hash_chain": source.snapshot.full_parent_hash_chain_verified,
        "previous_clean_shutdown": len(exact_shutdowns) == 1,
        "authorization_expected_head": expected_matches,
    }
    failures: list[str] = []
    if not checks["unique_active_head"]:
        failures.append("blocked_ambiguous_active_head")
    if not checks["unique_lineage"]:
        failures.append("blocked_ambiguous_self_state_lineage")
    if not checks["head_matches_leaf"]:
        failures.append("blocked_stale_active_head")
    if not checks["parent_hash_chain"]:
        failures.append("blocked_invalid_parent_hash_chain")
    if not checks["previous_clean_shutdown"]:
        failures.append("blocked_previous_session_shutdown_unverified")
    if not checks["authorization_expected_head"]:
        failures.append("blocked_active_head_cas_conflict")
    core = {
        "authorization": authorization.authorization_id,
        "head": head.active_head_sha256,
        "failures": failures,
    }
    return PersistentSessionRecoveryResolutionRecord(
        resolution_id=f"session_recovery_resolution:{sha256_payload(core)[:16]}",
        schema_version=RESOLUTION_SCHEMA_VERSION,
        created_at=utc_now(),
        authorization_id=authorization.authorization_id,
        target_session_id=authorization.target_session_id,
        package_133_source_snapshot_ref=source.snapshot.source_snapshot_id,
        active_head_candidate_count=active_head_candidate_count,
        self_state_lineage_candidate_count=1,
        unique_active_head_verified=checks["unique_active_head"],
        unique_self_state_lineage_verified=checks["unique_lineage"],
        head_payload_integrity_verified=checks["head_integrity"],
        head_matches_canonical_leaf=checks["head_matches_leaf"] and checks["authorization_expected_head"],
        parent_hash_chain_verified=checks["parent_hash_chain"],
        previous_clean_shutdown_verified=checks["previous_clean_shutdown"],
        stale_head_detected=not checks["head_matches_leaf"],
        corrupt_head_detected=False,
        ambiguous_recovery_detected=not (
            checks["unique_active_head"] and checks["unique_lineage"]
        ),
        fallback_selection_used=False,
        latest_record_guess_used=False,
        decision="allow_exact_recovery_cas" if not failures else "blocked_recovery",
        failure_reasons=tuple(failures),
        source_record_refs=(
            authorization.authorization_id,
            source.snapshot.source_snapshot_id,
            head.active_head_id,
            *(str(item["shutdown_record_id"]) for item in exact_shutdowns),
        ),
    )


def build_process_receipt(
    *,
    process_role: str,
    process_instance_id: str,
    operating_system_process_id: int,
    session_id: str,
    started_monotonic_ns: int,
    ended_monotonic_ns: int,
    authorization_id: str,
    identity_binding_ref: str | None,
    active_head_before_sha256: str | None,
    active_head_after_sha256: str | None,
    shutdown_record_ref: str | None,
    worker_status: str,
    source_refs: tuple[str, ...],
) -> PersistentSessionRecoveryProcessReceipt:
    core = {
        "role": process_role,
        "process": process_instance_id,
        "pid": operating_system_process_id,
        "session": session_id,
        "authorization": authorization_id,
        "started": started_monotonic_ns,
    }
    return PersistentSessionRecoveryProcessReceipt(
        process_receipt_id=f"persistent_session_process_receipt:{sha256_payload(core)[:16]}",
        schema_version=PROCESS_SCHEMA_VERSION,
        created_at=utc_now(),
        process_role=process_role,
        process_instance_id=process_instance_id,
        operating_system_process_id=operating_system_process_id,
        session_id=session_id,
        started_monotonic_ns=started_monotonic_ns,
        ended_monotonic_ns=ended_monotonic_ns,
        authorization_id=authorization_id,
        identity_binding_ref=identity_binding_ref,
        active_head_before_sha256=active_head_before_sha256,
        active_head_after_sha256=active_head_after_sha256,
        shutdown_record_ref=shutdown_record_ref,
        worker_status=worker_status,
        source_record_refs=source_refs,
    )


def build_recovery_pair(
    *,
    store: PersistentSessionRecoveryStore,
    source: Package133SourceBundle,
    process_a: dict[str, Any],
    process_b: dict[str, Any],
    package_133_source_unchanged: bool,
) -> PersistentSessionRecoveryPairRecord:
    receipts = {
        str(item["process_receipt_id"]): item
        for item in store.list_payloads("persistent_session_recovery_process_receipts")
    }
    bindings = {
        str(item["binding_id"]): item
        for item in store.list_payloads("persistent_session_identity_bindings")
    }
    receipt_a = receipts[str(process_a["process_receipt_id"])]
    receipt_b = receipts[str(process_b["process_receipt_id"])]
    binding_a = bindings[str(process_a["identity_binding_id"])]
    binding_b = bindings[str(process_b["identity_binding_id"])]
    head = store.get_active_head()
    core = {
        "process_a": receipt_a["process_receipt_id"],
        "process_b": receipt_b["process_receipt_id"],
        "head": head.active_head_sha256,
    }
    return PersistentSessionRecoveryPairRecord(
        recovery_pair_id=f"persistent_session_recovery_pair:{sha256_payload(core)[:16]}",
        schema_version=PAIR_SCHEMA_VERSION,
        created_at=utc_now(),
        process_a_receipt_ref=str(receipt_a["process_receipt_id"]),
        process_b_receipt_ref=str(receipt_b["process_receipt_id"]),
        process_ids_distinct=(
            int(receipt_a["operating_system_process_id"])
            != int(receipt_b["operating_system_process_id"])
        ),
        process_instance_ids_distinct=(
            receipt_a["process_instance_id"] != receipt_b["process_instance_id"]
        ),
        sessions_distinct=receipt_a["session_id"] != receipt_b["session_id"],
        process_a_ended_before_process_b_started=(
            int(receipt_a["ended_monotonic_ns"])
            < int(receipt_b["started_monotonic_ns"])
        ),
        process_a_clean_shutdown_verified=(
            receipt_a["worker_status"] == "initialized_and_cleanly_shutdown"
            and bool(receipt_a["shutdown_record_ref"])
        ),
        process_b_fresh_startup_verified=(
            receipt_b["worker_status"] == "fresh_process_recovery_completed"
        ),
        same_self_state_lineage=(
            binding_a["self_state_lineage_id"]
            == binding_b["self_state_lineage_id"]
            == source.snapshot.self_state_lineage_id
        ),
        same_self_state_record=(
            binding_a["self_state_record_id"]
            == binding_b["self_state_record_id"]
            == source.snapshot.leaf_self_state_record_id
        ),
        same_self_state_sha256=(
            binding_a["self_state_sha256"]
            == binding_b["self_state_sha256"]
            == source.snapshot.leaf_self_state_sha256
        ),
        active_head_revision_incremented_once=(
            int(binding_a["head_revision"]) == 1
            and int(binding_b["head_revision"]) == 2
            and head.head_revision == 2
        ),
        active_head_hash_chain_verified=(
            head.previous_active_head_sha256 == binding_a["active_head_sha256"]
            and head.active_head_sha256 == binding_b["active_head_sha256"]
        ),
        package_133_history_unchanged=package_133_source_unchanged,
        identity_fork_created=False,
        comparison_status="passed_real_fresh_process_session_recovery",
        source_record_refs=(
            source.snapshot.source_snapshot_id,
            str(receipt_a["process_receipt_id"]),
            str(receipt_b["process_receipt_id"]),
            str(binding_a["binding_id"]),
            str(binding_b["binding_id"]),
            head.active_head_id,
        ),
    )


def validate_recovery_authorization(
    *,
    store: PersistentSessionRecoveryStore,
    authorization: PersistentSessionRecoveryAuthorization,
    source: Package133SourceBundle,
    operation: str,
    session_id: str,
    process_instance_id: str,
) -> None:
    if store.authorization_consumed(authorization.authorization_id):
        raise RuntimeError("blocked_recovery_authorization_already_consumed")
    try:
        expires = datetime.fromisoformat(authorization.expires_at)
    except ValueError as error:
        raise RuntimeError("blocked_recovery_authorization_expiry_invalid") from error
    if expires.tzinfo is None or datetime.now(timezone.utc) >= expires:
        raise RuntimeError("blocked_recovery_authorization_expired")
    checks = (
        authorization.operation == operation,
        authorization.package_133_source_snapshot_ref == source.snapshot.source_snapshot_id,
        authorization.target_self_state_lineage_id == source.snapshot.self_state_lineage_id,
        authorization.target_self_state_record_id == source.snapshot.leaf_self_state_record_id,
        authorization.target_self_state_sha256 == source.snapshot.leaf_self_state_sha256,
        authorization.target_session_id == session_id,
        authorization.target_process_instance_id == process_instance_id,
    )
    if not all(checks):
        raise RuntimeError("blocked_recovery_authorization_scope_mismatch")


def _record_blocked_worker(
    *,
    store: PersistentSessionRecoveryStore,
    source: Package133SourceBundle,
    authorization: PersistentSessionRecoveryAuthorization,
    process_role: str,
    process_instance_id: str,
    operating_system_process_id: int,
    session_id: str,
    started_monotonic_ns: int,
    failure_reason: str,
    observed_head: ActiveSelfStateHeadRecord | None,
    resolution: PersistentSessionRecoveryResolutionRecord | None = None,
) -> dict[str, Any]:
    blocked_resolution = resolution or _build_generic_blocked_resolution(
        source=source,
        authorization=authorization,
        observed_head=observed_head,
        failure_reason=failure_reason,
    )
    cas_event = build_blocked_cas_event(
        authorization=authorization,
        observed_head=observed_head,
        failure_reason=failure_reason,
    )
    consumption = build_authorization_consumption(
        authorization=authorization,
        status="consumed_blocked",
        failure_reason=failure_reason,
    )
    store.append_blocked_recovery_attempt(
        cas_event=cas_event,
        consumption=consumption,
        resolution=blocked_resolution,
    )
    ended = monotonic_ns()
    receipt = build_process_receipt(
        process_role=process_role,
        process_instance_id=process_instance_id,
        operating_system_process_id=operating_system_process_id,
        session_id=session_id,
        started_monotonic_ns=started_monotonic_ns,
        ended_monotonic_ns=max(ended, started_monotonic_ns + 1),
        authorization_id=authorization.authorization_id,
        identity_binding_ref=None,
        active_head_before_sha256=(observed_head.active_head_sha256 if observed_head else None),
        active_head_after_sha256=(observed_head.active_head_sha256 if observed_head else None),
        shutdown_record_ref=None,
        worker_status="blocked",
        source_refs=(
            source.snapshot.source_snapshot_id,
            blocked_resolution.resolution_id,
            cas_event.cas_event_id,
        ),
    )
    store.append_record("persistent_session_recovery_process_receipts", receipt)
    return {
        "process_receipt_id": receipt.process_receipt_id,
        "process_instance_id": process_instance_id,
        "operating_system_process_id": operating_system_process_id,
        "session_id": session_id,
        "worker_status": "blocked",
        "failure_reason": failure_reason,
        "resolution_id": blocked_resolution.resolution_id,
    }


def _build_generic_blocked_resolution(
    *,
    source: Package133SourceBundle,
    authorization: PersistentSessionRecoveryAuthorization,
    observed_head: ActiveSelfStateHeadRecord | None,
    failure_reason: str,
) -> PersistentSessionRecoveryResolutionRecord:
    corrupt = "corrupt" in failure_reason
    missing = "missing_active_head" in failure_reason
    ambiguous = "ambiguous" in failure_reason
    stale = "stale" in failure_reason
    core = {
        "authorization": authorization.authorization_id,
        "failure": failure_reason,
        "head": observed_head.active_head_sha256 if observed_head else None,
    }
    return PersistentSessionRecoveryResolutionRecord(
        resolution_id=f"session_recovery_resolution:{sha256_payload(core)[:16]}",
        schema_version=RESOLUTION_SCHEMA_VERSION,
        created_at=utc_now(),
        authorization_id=authorization.authorization_id,
        target_session_id=authorization.target_session_id,
        package_133_source_snapshot_ref=source.snapshot.source_snapshot_id,
        active_head_candidate_count=0 if missing else (2 if ambiguous else 1),
        self_state_lineage_candidate_count=2 if "lineage" in failure_reason and ambiguous else 1,
        unique_active_head_verified=not (missing or ambiguous),
        unique_self_state_lineage_verified=not ("lineage" in failure_reason and ambiguous),
        head_payload_integrity_verified=not corrupt and observed_head is not None,
        head_matches_canonical_leaf=False,
        parent_hash_chain_verified=source.snapshot.full_parent_hash_chain_verified,
        previous_clean_shutdown_verified=False,
        stale_head_detected=stale,
        corrupt_head_detected=corrupt,
        ambiguous_recovery_detected=ambiguous,
        fallback_selection_used=False,
        latest_record_guess_used=False,
        decision="blocked_recovery",
        failure_reasons=(failure_reason,),
        source_record_refs=(
            authorization.authorization_id,
            source.snapshot.source_snapshot_id,
            *(observed_head.source_record_refs[-1:] if observed_head else ()),
        ),
    )


def _validate_external_roots(repo_root: Path, state_dir: Path, source_dir: Path) -> None:
    if _is_within(state_dir, repo_root):
        raise ValueError("Package 134 state_dir must be outside the repository")
    if state_dir == source_dir or _is_within(state_dir, source_dir) or _is_within(source_dir, state_dir):
        raise ValueError("Package 134 output and Package 133 evidence roots must be separate")


def _is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _git_output(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", *arguments),
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()
