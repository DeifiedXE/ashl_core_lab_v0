"""Package 138 bounded same-session self-state readback runtime."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import fields, replace
from pathlib import Path
from tempfile import gettempdir
from types import SimpleNamespace
from typing import Any, TypeVar

from ashl_core_v1.runtime.host_sensor_types import (
    monotonic_ns,
    sha256_bytes,
    sha256_payload,
    stable_id,
    utc_now,
)
from ashl_core_v1.state.package_137_self_state_review_store import (
    Package137SelfStateReviewStore,
)
from ashl_core_v1.state.package_138_self_state_readback_store import (
    Package138SelfStateReadbackStore,
)
from ashl_core_v1.state.package_138_self_state_sources import (
    Package138SourceBundle,
    authority_source_tree_hashes,
    load_package_138_sources_read_only,
)
from ashl_core_v1.state.persistent_session_recovery_runtime import (
    build_clean_shutdown_record,
    build_recovery_authorization,
    run_process_b_recovery,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    PersistentSessionRecoveryStore,
)
from ashl_core_v1.state.self_state_readback_consumer_inventory import (
    build_self_state_readback_consumer_inventory,
    consumer_inventory_sha256,
)
from ashl_core_v1.state.self_state_readback_types import (
    ACTIVE_HEAD_AUTHORITY,
    ALLOWLIST_SCHEMA_VERSION,
    AUDIT_ONLY_CONSUMER_ID,
    AUTHORIZATION_SCHEMA_VERSION,
    BLOCKED_SCHEMA_VERSION,
    COMPARISON_SCHEMA_VERSION,
    CONTRACT_SCHEMA_VERSION,
    CONSUMPTION_SCHEMA_VERSION,
    EXPOSED_PROVENANCE_FIELDS,
    EXPOSED_STRUCTURAL_FIELDS,
    LIFECYCLE_SCHEMA_VERSION,
    MAXIMUM_AUTHORIZATION_LIFETIME_NS,
    OFFICIAL_AUTHORIZATION_LIFETIME_NS,
    PROCESS_SCHEMA_VERSION,
    READBACK_AUTHORITY,
    READBACK_SCHEMA_VERSION,
    RESET_SCHEMA_VERSION,
    REVIEW_GATE_AUTHORITY,
    SELF_STATE_AUTHORITY,
    SNAPSHOT_SCHEMA_VERSION,
    BoundedSelfStateReadbackRecord,
    SelfStateReadbackAuthorizationRecord,
    SelfStateReadbackBlockedAttemptRecord,
    SelfStateReadbackBoundaryContract,
    SelfStateReadbackConsumerAllowlistRecord,
    SelfStateReadbackConsumptionRecord,
    SelfStateReadbackCounterfactualComparison,
    SelfStateReadbackCounterfactualSnapshot,
    SelfStateReadbackFreshProcessResetRecord,
    SelfStateReadbackLifecycleRecord,
    SelfStateReadbackProcessReceipt,
)


T = TypeVar("T")


def preflight_self_state_readback_boundary(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    state_dir: str | Path,
) -> dict[str, Any]:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    sources = tuple(
        Path(item).resolve()
        for item in (
            package_133_state_dir,
            package_134_state_dir,
            package_137_state_dir,
        )
    )
    _validate_external_roots(root, output, *sources)
    bundle = load_package_138_sources_read_only(
        package_133_state_dir=sources[0],
        package_134_state_dir=sources[1],
        package_137_state_dir=sources[2],
    )
    inventory = build_self_state_readback_consumer_inventory(root)
    production = tuple(item.consumer_surface_id for item in inventory if item.production_eligible)
    audit_only = tuple(item.consumer_surface_id for item in inventory if item.audit_only_eligible)
    if production or audit_only != (AUDIT_ONLY_CONSUMER_ID,):
        raise RuntimeError("blocked_package_138_consumer_inventory_boundary")
    registry = _load_registry(root)
    if not (
        registry.get("current_package_id") in {"137", "138", "139"}
        and registry.get("package_status", {}).get("137") == "completed"
    ):
        raise RuntimeError("blocked_package_137_baseline_not_completed")
    store = Package138SelfStateReadbackStore(output)
    if not store.audit_integrity()["valid"]:
        raise RuntimeError("blocked_package_138_store_integrity_failure")
    return {
        "baseline_commit": _git_output(root, "rev-parse", "HEAD"),
        "source": bundle,
        "inventory": inventory,
        "production_consumer_ids": production,
        "audit_only_consumer_ids": audit_only,
        "state_dir_is_external": not _is_within(output, root),
        "readiness": "ready_for_bounded_same_session_read_only_self_state_context",
    }


def initialize_self_state_readback_boundary(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    state_dir: str | Path,
) -> dict[str, Any]:
    preflight = preflight_self_state_readback_boundary(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        state_dir=state_dir,
    )
    inventory = preflight["inventory"]
    source: Package138SourceBundle = preflight["source"]
    contract = _build_contract()
    allowlist = _build_allowlist(
        contract=contract,
        inventory_sha256=consumer_inventory_sha256(inventory),
        inventory_refs=tuple(item.inventory_record_id for item in inventory),
    )
    store = Package138SelfStateReadbackStore(state_dir)
    for item in inventory:
        store.append_once("self_state_readback_consumer_inventory", item)
    store.append_once("self_state_readback_source_bindings", source.source_binding)
    store.append_once("self_state_readback_contracts", contract)
    store.append_once("self_state_readback_consumer_allowlists", allowlist)
    return {
        "source": preflight["source"],
        "source_binding": source.source_binding,
        "contract": contract,
        "allowlist": allowlist,
        "inventory": inventory,
    }


def create_self_state_readback_authorization(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    state_dir: str | Path,
    runtime_session_id: str,
    process_instance_id: str,
    consumer_id: str = AUDIT_ONLY_CONSUMER_ID,
    authorization_lifetime_ns: int = OFFICIAL_AUTHORIZATION_LIFETIME_NS,
    issued_at_monotonic_ns: int | None = None,
) -> SelfStateReadbackAuthorizationRecord:
    initialized = initialize_self_state_readback_boundary(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        state_dir=state_dir,
    )
    source: Package138SourceBundle = initialized["source"]
    allowlist: SelfStateReadbackConsumerAllowlistRecord = initialized["allowlist"]
    store = Package138SelfStateReadbackStore(state_dir)
    rejection: str | None = None
    if not runtime_session_id or not process_instance_id:
        rejection = "blocked_self_state_readback_session_or_process_identity_missing"
    elif consumer_id not in allowlist.audit_only_consumer_ids:
        rejection = "blocked_self_state_readback_consumer_not_allowlisted"
    elif runtime_session_id != source.active_head.bound_session_id:
        rejection = "blocked_self_state_readback_active_session_mismatch"
    elif process_instance_id != source.active_head.bound_process_instance_id:
        rejection = "blocked_self_state_readback_active_process_mismatch"
    elif source.active_identity_binding is None:
        rejection = "blocked_self_state_readback_active_process_binding_missing"
    elif source.active_session_shutdown is not None:
        rejection = "blocked_self_state_readback_active_session_already_shutdown"
    elif int(source.active_identity_binding["operating_system_process_id"]) != os.getpid():
        rejection = "blocked_self_state_readback_operating_system_process_mismatch"
    elif authorization_lifetime_ns <= 0 or authorization_lifetime_ns > MAXIMUM_AUTHORIZATION_LIFETIME_NS:
        rejection = "blocked_self_state_readback_authorization_lifetime_invalid"
    if rejection:
        blocked = _build_blocked_attempt(
            operation="authorize_readback",
            runtime_session_id=runtime_session_id or "missing_session",
            process_instance_id=process_instance_id or "missing_process",
            consumer_id=consumer_id or "missing_consumer",
            authorization_ref=None,
            readback_ref=None,
            expected_head=source.active_head,
            observed_head=source.active_head,
            failure_reason=rejection,
        )
        store.append_once("self_state_readback_blocked_attempts", blocked)
        raise ValueError(rejection)
    issued = int(monotonic_ns() if issued_at_monotonic_ns is None else issued_at_monotonic_ns)
    head = source.active_head
    payload: dict[str, Any] = {
        "authorization_id": "",
        "authorization_sha256": "",
        "schema_version": AUTHORIZATION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "contract_ref": initialized["contract"].contract_id,
        "allowlist_ref": allowlist.allowlist_id,
        "source_binding_ref": source.source_binding.source_binding_id,
        "authorization_source": "explicit_session_configuration",
        "authorized_by": "local_operator",
        "explicit_authorization": True,
        "runtime_session_id": runtime_session_id,
        "process_instance_id": process_instance_id,
        "consumer_id": consumer_id,
        "expected_active_head_id": head.active_head_id,
        "expected_active_head_sha256": head.active_head_sha256,
        "expected_head_revision": head.head_revision,
        "expected_self_state_record_id": head.self_state_record_id,
        "expected_self_state_sha256": head.self_state_sha256,
        "issued_at_monotonic_ns": issued,
        "expires_at_monotonic_ns": issued + int(authorization_lifetime_ns),
        "one_binding_only": True,
        "same_session_only": True,
        "teacher_review_scope_used": False,
        "teacher_consumer_approval_inferred": False,
        "authorization_status": "authorized_for_one_exact_same_session_readback",
        "source_record_refs": (
            initialized["contract"].contract_id,
            allowlist.allowlist_id,
            source.source_binding.source_binding_id,
            source.package_137_audit["audit_id"],
            source.package_137_commit_receipt["review_id"],
            head.active_head_id,
            head.self_state_record_id,
        ),
    }
    authorization = _hashed_record(
        SelfStateReadbackAuthorizationRecord,
        payload,
        id_field="authorization_id",
        hash_field="authorization_sha256",
        prefix="self_state_readback_authorization",
    )
    store.append_once("self_state_readback_authorizations", authorization)
    return authorization


def validate_readback_authorization(
    *,
    authorization: SelfStateReadbackAuthorizationRecord,
    contract: SelfStateReadbackBoundaryContract,
    allowlist: SelfStateReadbackConsumerAllowlistRecord,
    source: Package138SourceBundle,
    store: Package138SelfStateReadbackStore,
    runtime_session_id: str,
    process_instance_id: str,
    consumer_id: str,
    evaluated_at_monotonic_ns: int,
) -> tuple[str, ...]:
    failures: list[str] = []
    head = source.active_head
    if not authorization.explicit_authorization:
        failures.append("authorization_not_explicit")
    if authorization.contract_ref != contract.contract_id or authorization.allowlist_ref != allowlist.allowlist_id:
        failures.append("authorization_contract_or_allowlist_mismatch")
    if consumer_id != authorization.consumer_id or consumer_id not in allowlist.audit_only_consumer_ids:
        failures.append("consumer_not_allowlisted")
    if runtime_session_id != authorization.runtime_session_id:
        failures.append("session_mismatch")
    if runtime_session_id != head.bound_session_id:
        failures.append("active_head_session_mismatch")
    if process_instance_id != authorization.process_instance_id:
        failures.append("process_mismatch")
    if process_instance_id != head.bound_process_instance_id:
        failures.append("active_head_process_mismatch")
    if authorization.expected_active_head_id != head.active_head_id:
        failures.append("active_head_id_mismatch")
    if authorization.expected_active_head_sha256 != head.active_head_sha256:
        failures.append("active_head_hash_mismatch")
    if authorization.expected_head_revision != head.head_revision:
        failures.append("active_head_revision_mismatch")
    if authorization.expected_self_state_record_id != head.self_state_record_id:
        failures.append("self_state_record_mismatch")
    if authorization.expected_self_state_sha256 != head.self_state_sha256:
        failures.append("self_state_hash_mismatch")
    if store.authorization_has_readback(authorization.authorization_id):
        failures.append("authorization_already_consumed")
    if not (
        authorization.issued_at_monotonic_ns
        <= evaluated_at_monotonic_ns
        < authorization.expires_at_monotonic_ns
    ):
        failures.append("authorization_expired")
    if source.active_identity_binding is None:
        failures.append("active_process_binding_missing")
    if source.active_session_shutdown is not None:
        failures.append("active_session_already_shutdown")
    if source.active_identity_binding is not None and int(
        source.active_identity_binding["operating_system_process_id"]
    ) != os.getpid():
        failures.append("operating_system_process_mismatch")
    if authorization.teacher_review_scope_used or authorization.teacher_consumer_approval_inferred:
        failures.append("teacher_scope_expansion")
    try:
        source_binding = store.get_payload(
            "self_state_readback_source_bindings", authorization.source_binding_ref
        )
    except KeyError:
        failures.append("authorization_source_binding_missing")
    else:
        if not all(
            (
                source_binding.get("active_head_sha256")
                == authorization.expected_active_head_sha256,
                source_binding.get("head_revision") == authorization.expected_head_revision,
                source_binding.get("self_state_record_id")
                == authorization.expected_self_state_record_id,
                source_binding.get("self_state_sha256")
                == authorization.expected_self_state_sha256,
            )
        ):
            failures.append("authorization_source_binding_invalid")
    return tuple(failures)


def run_self_state_readback_worker(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    state_dir: str | Path,
    process_role: str,
    runtime_session_id: str,
    process_instance_id: str,
    authorization_id: str | None,
) -> dict[str, Any]:
    started = monotonic_ns()
    pid = os.getpid()
    initialized = initialize_self_state_readback_boundary(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        state_dir=state_dir,
    )
    source: Package138SourceBundle = initialized["source"]
    store = Package138SelfStateReadbackStore(state_dir)
    if authorization_id is None:
        blocked = _build_blocked_attempt(
            operation="create_readback",
            runtime_session_id=runtime_session_id,
            process_instance_id=process_instance_id,
            consumer_id=AUDIT_ONLY_CONSUMER_ID,
            authorization_ref=None,
            readback_ref=None,
            expected_head=source.active_head,
            observed_head=source.active_head,
            failure_reason="blocked_readback_authorization_missing",
        )
        ended = max(monotonic_ns(), started + 1)
        receipt = _build_process_receipt(
            process_role=process_role,
            process_instance_id=process_instance_id,
            operating_system_process_id=pid,
            runtime_session_id=runtime_session_id,
            started=started,
            ended=ended,
            authorization_ref=None,
            readback_ref=None,
            consumption_ref=None,
            lifecycle_ref=None,
            blocked_attempt_ref=blocked.blocked_attempt_id,
            worker_status="fresh_process_started_without_prior_readback",
            source_refs=(blocked.blocked_attempt_id,),
        )
        store.append_once("self_state_readback_blocked_attempts", blocked)
        store.append_once("self_state_readback_process_receipts", receipt)
        return {
            "status": "blocked_readback_authorization_missing",
            "blocked_attempt": blocked,
            "process_receipt": receipt,
        }
    authorization = _record_from_payload(
        SelfStateReadbackAuthorizationRecord,
        store.get_payload("self_state_readback_authorizations", authorization_id),
    )
    failures = validate_readback_authorization(
        authorization=authorization,
        contract=initialized["contract"],
        allowlist=initialized["allowlist"],
        source=source,
        store=store,
        runtime_session_id=runtime_session_id,
        process_instance_id=process_instance_id,
        consumer_id=AUDIT_ONLY_CONSUMER_ID,
        evaluated_at_monotonic_ns=monotonic_ns(),
    )
    if failures:
        blocked = _build_blocked_attempt(
            operation="create_readback",
            runtime_session_id=runtime_session_id,
            process_instance_id=process_instance_id,
            consumer_id=AUDIT_ONLY_CONSUMER_ID,
            authorization_ref=authorization.authorization_id,
            readback_ref=None,
            expected_head=_head_from_authorization(authorization),
            observed_head=source.active_head,
            failure_reason="blocked_" + failures[0],
        )
        ended = max(monotonic_ns(), started + 1)
        receipt = _build_process_receipt(
            process_role=process_role,
            process_instance_id=process_instance_id,
            operating_system_process_id=pid,
            runtime_session_id=runtime_session_id,
            started=started,
            ended=ended,
            authorization_ref=authorization.authorization_id,
            readback_ref=None,
            consumption_ref=None,
            lifecycle_ref=None,
            blocked_attempt_ref=blocked.blocked_attempt_id,
            worker_status="fresh_process_started_without_prior_readback",
            source_refs=(authorization.authorization_id, blocked.blocked_attempt_id),
        )
        store.append_once("self_state_readback_blocked_attempts", blocked)
        store.append_once("self_state_readback_process_receipts", receipt)
        return {"status": "blocked", "blocked_attempt": blocked, "process_receipt": receipt}
    readback = _build_readback(
        authorization=authorization,
        source=source,
        operating_system_process_id=pid,
        bound_at_monotonic_ns=monotonic_ns(),
    )
    store.append_once("bounded_self_state_readbacks", readback)
    consumption = _build_consumption(
        readback=readback,
        authorization=authorization,
        source=source,
        consumed_at_monotonic_ns=monotonic_ns(),
    )
    store.append_once("self_state_readback_consumptions", consumption)
    comparison = None
    if process_role == "primary_session_a":
        absent, present, comparison = build_readback_counterfactual(
            ashl_root=ashl_root,
            source=source,
            runtime_session_id=runtime_session_id,
            readback=readback,
        )
        store.append_once("self_state_readback_counterfactual_snapshots", absent)
        store.append_once("self_state_readback_counterfactual_snapshots", present)
        store.append_once("self_state_readback_counterfactual_comparisons", comparison)
    lifecycle = _build_lifecycle(
        readback=readback,
        observed_head=source.active_head,
        lifecycle_kind="expired_session_end",
        terminal_reason="same_session_worker_ended",
        occurred_at_monotonic_ns=max(monotonic_ns(), readback.bound_at_monotonic_ns + 1),
    )
    store.append_once("self_state_readback_lifecycle_records", lifecycle)
    ended = max(monotonic_ns(), started + 1)
    receipt = _build_process_receipt(
        process_role=process_role,
        process_instance_id=process_instance_id,
        operating_system_process_id=pid,
        runtime_session_id=runtime_session_id,
        started=started,
        ended=ended,
        authorization_ref=authorization.authorization_id,
        readback_ref=readback.readback_id,
        consumption_ref=consumption.consumption_id,
        lifecycle_ref=lifecycle.lifecycle_id,
        blocked_attempt_ref=None,
        worker_status=(
            "readback_consumed_then_expired_in_same_session"
            if process_role == "primary_session_a"
            else "newly_authorized_readback_consumed_then_expired"
        ),
        source_refs=(
            authorization.authorization_id,
            readback.readback_id,
            consumption.consumption_id,
            lifecycle.lifecycle_id,
        ),
    )
    store.append_once("self_state_readback_process_receipts", receipt)
    return {
        "status": "readback_consumed_and_expired",
        "authorization": authorization,
        "readback": readback,
        "consumption": consumption,
        "lifecycle": lifecycle,
        "comparison": comparison,
        "process_receipt": receipt,
    }


def run_readback_worker_subprocess(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    state_dir: str | Path,
    process_role: str,
    runtime_session_id: str,
    process_instance_id: str,
    authorization_id: str | None,
) -> dict[str, Any]:
    command = (
        sys.executable,
        "-B",
        "-m",
        "ashl_core_v1.state.package_138_self_state_readback_worker",
        "--ashl-root",
        str(Path(ashl_root).resolve()),
        "--package-133-state-dir",
        str(Path(package_133_state_dir).resolve()),
        "--package-134-state-dir",
        str(Path(package_134_state_dir).resolve()),
        "--package-137-state-dir",
        str(Path(package_137_state_dir).resolve()),
        "--state-dir",
        str(Path(state_dir).resolve()),
        "--process-role",
        process_role,
        "--runtime-session-id",
        runtime_session_id,
        "--process-instance-id",
        process_instance_id,
    )
    if authorization_id:
        command += ("--authorization-id", authorization_id)
    environment = dict(os.environ)
    cache_root = Path(gettempdir()) / "ashl_package_138_pycache"
    cache_root.mkdir(parents=True, exist_ok=True)
    environment["PYTHONPYCACHEPREFIX"] = str(cache_root)
    result = subprocess.run(
        command,
        cwd=Path(ashl_root).resolve(),
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "Package 138 worker failed"
        raise RuntimeError(f"blocked_package_138_worker_failed:{detail}")
    lines = tuple(line for line in result.stdout.splitlines() if line.strip())
    if not lines:
        raise RuntimeError("blocked_package_138_worker_receipt_missing")
    return dict(json.loads(lines[-1]))


def run_recovered_session_readback_worker(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    state_dir: str | Path,
    recovery_authorization_id: str,
    runtime_session_id: str,
    process_instance_id: str,
    process_role: str,
    probe_missing_authorization: bool,
) -> dict[str, Any]:
    recovery = run_process_b_recovery(
        package_133_state_dir=package_133_state_dir,
        state_dir=package_134_state_dir,
        authorization_id=recovery_authorization_id,
        session_id=runtime_session_id,
        process_instance_id=process_instance_id,
    )
    if recovery.get("worker_status") != "fresh_process_recovery_completed":
        raise RuntimeError("blocked_package_138_in_process_recovery_failed")
    if int(recovery["operating_system_process_id"]) != os.getpid():
        raise RuntimeError("blocked_package_138_recovery_process_identity_mismatch")
    p134 = PersistentSessionRecoveryStore(package_134_state_dir)
    head = p134.get_active_head()
    if not (
        head.bound_session_id == runtime_session_id
        and head.bound_process_instance_id == process_instance_id
    ):
        raise RuntimeError("blocked_package_138_recovered_head_process_binding_mismatch")
    missing = None
    if probe_missing_authorization:
        missing = run_self_state_readback_worker(
            ashl_root=ashl_root,
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=package_134_state_dir,
            package_137_state_dir=package_137_state_dir,
            state_dir=state_dir,
            process_role="fresh_process_probe_b",
            runtime_session_id=runtime_session_id,
            process_instance_id=process_instance_id,
            authorization_id=None,
        )
    authorization = create_self_state_readback_authorization(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        state_dir=state_dir,
        runtime_session_id=runtime_session_id,
        process_instance_id=process_instance_id,
    )
    readback_role = "primary_session_a" if process_role == "session_a" else "reauthorized_session_b"
    readback = run_self_state_readback_worker(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        state_dir=state_dir,
        process_role=readback_role,
        runtime_session_id=runtime_session_id,
        process_instance_id=process_instance_id,
        authorization_id=authorization.authorization_id,
    )
    receipt = readback["process_receipt"]
    shutdown = replace(
        build_clean_shutdown_record(
            head=head,
            session_id=runtime_session_id,
            process_instance_id=process_instance_id,
            operating_system_process_id=os.getpid(),
            identity_binding_id=str(recovery["identity_binding_id"]),
        ),
        created_at=receipt.created_at,
        shutdown_monotonic_ns=receipt.ended_monotonic_ns,
        source_record_refs=(
            head.active_head_id,
            str(recovery["identity_binding_id"]),
            receipt.process_receipt_id,
        ),
    )
    p134.append_record("persistent_session_shutdown_records", shutdown)
    return {
        "status": "recovered_readback_consumed_and_cleanly_shutdown",
        "recovery": recovery,
        "missing_authorization_probe": missing,
        "authorization": authorization,
        "readback_result": readback,
        "shutdown": shutdown,
    }


def run_recovered_session_readback_subprocess(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    state_dir: str | Path,
    recovery_authorization_id: str,
    runtime_session_id: str,
    process_instance_id: str,
    process_role: str,
    probe_missing_authorization: bool,
) -> dict[str, Any]:
    command = (
        sys.executable,
        "-B",
        "-m",
        "ashl_core_v1.state.package_138_self_state_readback_worker",
        "--ashl-root", str(Path(ashl_root).resolve()),
        "--package-133-state-dir", str(Path(package_133_state_dir).resolve()),
        "--package-134-state-dir", str(Path(package_134_state_dir).resolve()),
        "--package-137-state-dir", str(Path(package_137_state_dir).resolve()),
        "--state-dir", str(Path(state_dir).resolve()),
        "--process-role", process_role,
        "--runtime-session-id", runtime_session_id,
        "--process-instance-id", process_instance_id,
        "--recovery-authorization-id", recovery_authorization_id,
        "--recover-before-readback",
    )
    if probe_missing_authorization:
        command += ("--probe-missing-authorization",)
    environment = dict(os.environ)
    cache_root = Path(gettempdir()) / "ashl_package_138_pycache"
    cache_root.mkdir(parents=True, exist_ok=True)
    environment["PYTHONPYCACHEPREFIX"] = str(cache_root)
    result = subprocess.run(
        command,
        cwd=Path(ashl_root).resolve(),
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "Package 138 recovered worker failed"
        raise RuntimeError(f"blocked_package_138_recovered_worker_failed:{detail}")
    lines = tuple(line for line in result.stdout.splitlines() if line.strip())
    if not lines:
        raise RuntimeError("blocked_package_138_recovered_worker_receipt_missing")
    return dict(json.loads(lines[-1]))


def build_readback_counterfactual(
    *,
    ashl_root: str | Path,
    source: Package138SourceBundle,
    runtime_session_id: str,
    readback: BoundedSelfStateReadbackRecord,
) -> tuple[
    SelfStateReadbackCounterfactualSnapshot,
    SelfStateReadbackCounterfactualSnapshot,
    SelfStateReadbackCounterfactualComparison,
]:
    invariants = _authority_invariant_payload(ashl_root=ashl_root, source=source)
    absent = _build_counterfactual_snapshot(
        branch_kind="readback_absent",
        runtime_session_id=runtime_session_id,
        readback_surface_sha256=None,
        invariants=invariants,
        source_refs=(source.source_binding.source_binding_id,),
    )
    present = _build_counterfactual_snapshot(
        branch_kind="readback_present",
        runtime_session_id=runtime_session_id,
        readback_surface_sha256=readback.readback_sha256,
        invariants=invariants,
        source_refs=(source.source_binding.source_binding_id, readback.readback_id),
    )
    equivalence_fields = (
        "runtime_behavior_sha256",
        "selected_action_sha256",
        "memory_sha256",
        "drive_sha256",
        "perception_history_sha256",
        "self_state_history_sha256",
        "active_head_sha256",
        "output_sha256",
        "recovery_result_sha256",
    )
    equal = all(getattr(absent, name) == getattr(present, name) for name in equivalence_fields)
    payload: dict[str, Any] = {
        "comparison_id": "",
        "comparison_sha256": "",
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "created_at": utc_now(),
        "absent_snapshot_ref": absent.snapshot_id,
        "present_snapshot_ref": present.snapshot_id,
        "differing_paths": ("readback_surface",),
        "readback_surface_only_difference": equal and absent.readback_surface_sha256 is None and bool(present.readback_surface_sha256),
        "runtime_behavior_equivalent": absent.runtime_behavior_sha256 == present.runtime_behavior_sha256,
        "selected_action_equivalent": absent.selected_action_sha256 == present.selected_action_sha256,
        "memory_equivalent": absent.memory_sha256 == present.memory_sha256,
        "drive_equivalent": absent.drive_sha256 == present.drive_sha256,
        "perception_history_equivalent": absent.perception_history_sha256 == present.perception_history_sha256,
        "self_state_history_equivalent": absent.self_state_history_sha256 == present.self_state_history_sha256,
        "active_head_equivalent": absent.active_head_sha256 == present.active_head_sha256,
        "output_equivalent": absent.output_sha256 == present.output_sha256,
        "recovery_result_equivalent": absent.recovery_result_sha256 == present.recovery_result_sha256,
        "production_behavior_equivalent": not absent.production_behavior_changed and not present.production_behavior_changed,
        "comparison_status": "passed_readback_surface_only_counterfactual",
        "source_record_refs": (absent.snapshot_id, present.snapshot_id, readback.readback_id),
    }
    comparison = _hashed_record(
        SelfStateReadbackCounterfactualComparison,
        payload,
        id_field="comparison_id",
        hash_field="comparison_sha256",
        prefix="self_state_readback_counterfactual_comparison",
    )
    return absent, present, comparison


def run_real_self_state_readback_boundary(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    state_dir: str | Path,
    allow_self_state_readback: bool,
    allow_fresh_process_recovery: bool,
) -> dict[str, Any]:
    if not allow_self_state_readback:
        raise RuntimeError("blocked_self_state_readback_authorization_missing")
    if not allow_fresh_process_recovery:
        raise RuntimeError("blocked_package_138_recovery_verification_authorization_missing")
    store = Package138SelfStateReadbackStore(state_dir)
    if store.count("self_state_readback_process_receipts"):
        raise RuntimeError("blocked_package_138_state_dir_not_fresh")
    source_hashes_before = authority_source_tree_hashes(
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
    )
    initialized = initialize_self_state_readback_boundary(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        state_dir=state_dir,
    )
    initial_source = load_package_138_sources_read_only(
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
    )
    p134_store = PersistentSessionRecoveryStore(package_134_state_dir)
    p137_store = Package137SelfStateReviewStore(package_137_state_dir)
    initial_head = p134_store.get_active_head()
    prior_shutdown, p137_process, shutdown_derived = _ensure_exact_package_137_shutdown(
        p134_store=p134_store,
        p137_store=p137_store,
        head=initial_head,
        commit=initial_source.package_137_commit_receipt,
    )
    source_133 = initial_source.package_133
    process_a_instance = stable_id("package_138_readback_process_a")
    session_a = stable_id("package_138_readback_session_a")
    recovery_authorization_a = build_recovery_authorization(
        source=source_133,
        operation="recover_session",
        target_session_id=session_a,
        target_process_instance_id=process_a_instance,
        expected_head=initial_head,
    )
    p134_store.append_record(
        "persistent_session_recovery_authorizations", recovery_authorization_a
    )
    process_a_result = run_recovered_session_readback_subprocess(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        state_dir=state_dir,
        recovery_authorization_id=recovery_authorization_a.authorization_id,
        runtime_session_id=session_a,
        process_instance_id=process_a_instance,
        process_role="session_a",
        probe_missing_authorization=False,
    )
    readback_result_a = process_a_result["readback_result"]
    authorization_a = _record_from_payload(
        SelfStateReadbackAuthorizationRecord, process_a_result["authorization"]
    )
    process_a_receipt = _record_from_payload(
        SelfStateReadbackProcessReceipt,
        readback_result_a["process_receipt"],
    )
    readback_a = _record_from_payload(
        BoundedSelfStateReadbackRecord, readback_result_a["readback"]
    )
    lifecycle_a = _record_from_payload(
        SelfStateReadbackLifecycleRecord, readback_result_a["lifecycle"]
    )
    head_before = p134_store.get_active_head()
    if not (
        head_before.bound_session_id == session_a
        and head_before.bound_process_instance_id == process_a_instance
        and readback_a.active_head_sha256 == head_before.active_head_sha256
        and process_a_receipt.operating_system_process_id
        == int(process_a_result["recovery"]["operating_system_process_id"])
    ):
        raise RuntimeError("blocked_package_138_session_a_identity_binding_mismatch")
    recovery_process_instance = stable_id("package_138_readback_process_b")
    session_b = stable_id("package_138_recovered_session_b")
    recovery_authorization = build_recovery_authorization(
        source=source_133,
        operation="recover_session",
        target_session_id=session_b,
        target_process_instance_id=recovery_process_instance,
        expected_head=head_before,
    )
    p134_store.append_record("persistent_session_recovery_authorizations", recovery_authorization)
    process_b_result = run_recovered_session_readback_subprocess(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        state_dir=state_dir,
        recovery_authorization_id=recovery_authorization.authorization_id,
        runtime_session_id=session_b,
        process_instance_id=recovery_process_instance,
        process_role="session_b",
        probe_missing_authorization=True,
    )
    head_after = p134_store.get_active_head()
    if not (
        head_after.bound_session_id == session_b
        and head_after.bound_process_instance_id == recovery_process_instance
    ):
        raise RuntimeError("blocked_package_138_session_b_identity_binding_mismatch")
    stale = _build_lifecycle(
        readback=readback_a,
        observed_head=head_after,
        lifecycle_kind="stale_active_head_revision_changed",
        terminal_reason="active_head_revision_changed_after_explicit_recovery",
        occurred_at_monotonic_ns=max(monotonic_ns(), readback_a.bound_at_monotonic_ns + 1),
    )
    store.append_once("self_state_readback_lifecycle_records", stale)

    process_b_probe = process_b_result["missing_authorization_probe"]
    process_b_receipt = _record_from_payload(
        SelfStateReadbackProcessReceipt,
        process_b_probe["process_receipt"],
    )
    blocked_b = _record_from_payload(
        SelfStateReadbackBlockedAttemptRecord,
        process_b_probe["blocked_attempt"],
    )
    authorization_b = _record_from_payload(
        SelfStateReadbackAuthorizationRecord, process_b_result["authorization"]
    )
    process_b_authorized = process_b_result["readback_result"]
    readback_b = _record_from_payload(BoundedSelfStateReadbackRecord, process_b_authorized["readback"])
    process_b_authorized_receipt = _record_from_payload(
        SelfStateReadbackProcessReceipt, process_b_authorized["process_receipt"]
    )
    if process_b_authorized_receipt.operating_system_process_id != process_b_receipt.operating_system_process_id:
        raise RuntimeError("blocked_package_138_session_b_probe_and_readback_process_mismatch")
    recovery_events_a = tuple(
        item
        for item in p134_store.list_payloads("active_head_cas_events")
        if item.get("authorization_id") == recovery_authorization_a.authorization_id
    )
    recovery_events = tuple(
        item
        for item in p134_store.list_payloads("active_head_cas_events")
        if item.get("authorization_id") == recovery_authorization.authorization_id
    )
    if len(recovery_events_a) != 1 or len(recovery_events) != 1:
        raise RuntimeError("blocked_package_138_recovery_cas_event_missing_or_ambiguous")
    reset_payload: dict[str, Any] = {
        "reset_record_id": "",
        "reset_sha256": "",
        "schema_version": RESET_SCHEMA_VERSION,
        "created_at": utc_now(),
        "process_a_receipt_ref": process_a_receipt.process_receipt_id,
        "process_b_receipt_ref": process_b_receipt.process_receipt_id,
        "process_a_operating_system_process_id": process_a_receipt.operating_system_process_id,
        "process_b_operating_system_process_id": process_b_receipt.operating_system_process_id,
        "process_a_session_id": session_a,
        "process_b_session_id": session_b,
        "initial_active_head_sha256": initial_head.active_head_sha256,
        "initial_head_revision": initial_head.head_revision,
        "package_137_shutdown_record_ref": str(prior_shutdown["shutdown_record_id"]),
        "package_137_process_receipt_ref": str(p137_process["process_receipt_id"]),
        "package_137_shutdown_evidence_derived": shutdown_derived,
        "prior_readback_ref": readback_a.readback_id,
        "prior_readback_expiry_ref": lifecycle_a.lifecycle_id,
        "process_a_recovery_authorization_ref": recovery_authorization_a.authorization_id,
        "process_a_recovery_cas_event_ref": str(recovery_events_a[0]["cas_event_id"]),
        "process_a_shutdown_ref": str(process_a_result["shutdown"]["shutdown_record_id"]),
        "package_134_recovery_authorization_ref": recovery_authorization.authorization_id,
        "package_134_recovery_cas_event_ref": str(recovery_events[0]["cas_event_id"]),
        "active_head_sha256_before": head_before.active_head_sha256,
        "active_head_sha256_after": head_after.active_head_sha256,
        "head_revision_before": head_before.head_revision,
        "head_revision_after": head_after.head_revision,
        "self_state_record_id_before": head_before.self_state_record_id,
        "self_state_record_id_after": head_after.self_state_record_id,
        "stale_lifecycle_ref": stale.lifecycle_id,
        "missing_authorization_blocked_attempt_ref": blocked_b.blocked_attempt_id,
        "fresh_authorization_ref": authorization_b.authorization_id,
        "fresh_readback_ref": readback_b.readback_id,
        "processes_distinct": process_a_receipt.operating_system_process_id != process_b_receipt.operating_system_process_id,
        "sessions_distinct": session_a != session_b,
        "head_revision_incremented": head_after.head_revision == head_before.head_revision + 1,
        "self_state_identity_preserved": head_after.self_state_record_id == head_before.self_state_record_id,
        "prior_readback_restored": False,
        "prior_readback_consumable": False,
        "fresh_authorization_required": True,
        "fresh_binding_created": True,
        "prior_clean_shutdown_verified": True,
        "process_a_head_session_process_binding_verified": True,
        "process_b_head_session_process_binding_verified": True,
        "automatic_refresh_performed": False,
        "automatic_rebind_performed": False,
        "reset_status": "passed_fresh_process_readback_reset_and_reauthorization",
        "source_record_refs": (
            process_a_receipt.process_receipt_id,
            process_b_receipt.process_receipt_id,
            str(prior_shutdown["shutdown_record_id"]),
            str(p137_process["process_receipt_id"]),
            readback_a.readback_id,
            lifecycle_a.lifecycle_id,
            recovery_authorization_a.authorization_id,
            str(recovery_events_a[0]["cas_event_id"]),
            str(process_a_result["shutdown"]["shutdown_record_id"]),
            recovery_authorization.authorization_id,
            str(recovery_events[0]["cas_event_id"]),
            stale.lifecycle_id,
            blocked_b.blocked_attempt_id,
            authorization_b.authorization_id,
            readback_b.readback_id,
        ),
    }
    reset = _hashed_record(
        SelfStateReadbackFreshProcessResetRecord,
        reset_payload,
        id_field="reset_record_id",
        hash_field="reset_sha256",
        prefix="self_state_readback_fresh_process_reset",
    )
    store.append_once("self_state_readback_fresh_process_resets", reset)
    source_hashes_after = authority_source_tree_hashes(
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
    )
    return {
        "status": "completed_real_bounded_self_state_readback_boundary",
        "initial_source_binding": initialized["source_binding"],
        "contract": initialized["contract"],
        "allowlist": initialized["allowlist"],
        "authorization_a": authorization_a,
        "initial_head": initial_head,
        "package_137_shutdown": prior_shutdown,
        "package_137_shutdown_evidence_derived": shutdown_derived,
        "process_a_recovery_authorization": recovery_authorization_a,
        "process_a": process_a_result,
        "head_before_recovery": head_before,
        "recovery_authorization": recovery_authorization,
        "recovery_result": process_b_result["recovery"],
        "head_after_recovery": head_after,
        "stale_lifecycle": stale,
        "process_b_without_authorization": process_b_probe,
        "authorization_b": authorization_b,
        "process_b_authorized": process_b_authorized,
        "fresh_process_reset": reset,
        "package_133_unchanged": source_hashes_before[0] == source_hashes_after[0],
        "package_137_unchanged": source_hashes_before[2] == source_hashes_after[2],
        "package_134_changed_only_by_explicit_recovery": (
            source_hashes_before[1] != source_hashes_after[1]
            and head_before.head_revision == initial_head.head_revision + 1
            and head_after.head_revision == head_before.head_revision + 1
        ),
    }


def _ensure_exact_package_137_shutdown(
    *,
    p134_store: PersistentSessionRecoveryStore,
    p137_store: Package137SelfStateReviewStore,
    head: Any,
    commit: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    processes = tuple(
        item
        for item in p137_store.list_payloads("self_state_mutation_process_receipts")
        if item.get("worker_status")
        == "approved_successor_committed_by_package_133_then_package_134_cas"
        and item.get("process_instance_id") == head.bound_process_instance_id
        and item.get("commit_receipt_ref") == commit.get("commit_receipt_id")
    )
    if len(processes) != 1:
        raise RuntimeError("blocked_package_138_exact_package_137_process_receipt_missing_or_ambiguous")
    process = processes[0]
    exact_shutdowns = tuple(
        item
        for item in p134_store.list_payloads("persistent_session_shutdown_records")
        if item.get("session_id") == head.bound_session_id
        and item.get("process_instance_id") == head.bound_process_instance_id
        and item.get("active_head_sha256") == head.active_head_sha256
        and item.get("head_revision") == head.head_revision
        and item.get("clean_shutdown_verified") is True
    )
    if len(exact_shutdowns) > 1:
        raise RuntimeError("blocked_package_138_ambiguous_prior_shutdown")
    if exact_shutdowns:
        return exact_shutdowns[0], process, False
    shutdown = replace(
        build_clean_shutdown_record(
            head=head,
            session_id=head.bound_session_id,
            process_instance_id=head.bound_process_instance_id,
            operating_system_process_id=int(process["operating_system_process_id"]),
            identity_binding_id=str(commit["commit_receipt_id"]),
        ),
        created_at=str(process["created_at"]),
        shutdown_monotonic_ns=int(process["ended_monotonic_ns"]),
        source_record_refs=(
            head.active_head_id,
            str(commit["commit_receipt_id"]),
            str(process["process_receipt_id"]),
            str(commit["package_134_cas_event_id"]),
        ),
    )
    p134_store.append_record("persistent_session_shutdown_records", shutdown)
    return shutdown.to_dict(), process, True


def _build_contract() -> SelfStateReadbackBoundaryContract:
    payload: dict[str, Any] = {
        "contract_id": "",
        "contract_sha256": "",
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "readback_authority": READBACK_AUTHORITY,
        "self_state_authority": SELF_STATE_AUTHORITY,
        "active_head_authority": ACTIVE_HEAD_AUTHORITY,
        "review_gate_authority": REVIEW_GATE_AUTHORITY,
        "exposed_structural_fields": EXPOSED_STRUCTURAL_FIELDS,
        "exposed_provenance_fields": EXPOSED_PROVENANCE_FIELDS,
        "maximum_authorization_lifetime_ns": MAXIMUM_AUTHORIZATION_LIFETIME_NS,
        "production_consumer_count": 0,
        "audit_only_consumer_count": 1,
        "explicit_authorization_required": True,
        "exact_head_binding_required": True,
        "exact_state_binding_required": True,
        "same_session_only": True,
        "same_process_binding_required": True,
        "expiry_required": True,
        "stale_on_head_revision_change": True,
        "automatic_follow_allowed": False,
        "automatic_refresh_allowed": False,
        "automatic_rebind_allowed": False,
        "cross_session_recovery_allowed": False,
        "persistent_working_readback_allowed": False,
        "semantic_interpretation_allowed": False,
        "runtime_behavior_authority_allowed": False,
        "teacher_scope_expansion_allowed": False,
        "contract_status": "bounded_same_session_read_only_zero_production_consumers",
        "source_record_refs": (
            "authority:package_133_immutable_self_state_lineage",
            "authority:package_134_separate_active_head_cas_authority",
            "authority:package_137_exact_teacher_reviewed_self_state_successor_only",
        ),
    }
    return _hashed_record(
        SelfStateReadbackBoundaryContract,
        payload,
        id_field="contract_id",
        hash_field="contract_sha256",
        prefix="self_state_readback_contract",
    )


def _build_allowlist(
    *,
    contract: SelfStateReadbackBoundaryContract,
    inventory_sha256: str,
    inventory_refs: tuple[str, ...],
) -> SelfStateReadbackConsumerAllowlistRecord:
    payload: dict[str, Any] = {
        "allowlist_id": "",
        "allowlist_sha256": "",
        "schema_version": ALLOWLIST_SCHEMA_VERSION,
        "created_at": utc_now(),
        "contract_ref": contract.contract_id,
        "inventory_sha256": inventory_sha256,
        "production_consumer_ids": tuple(),
        "audit_only_consumer_ids": (AUDIT_ONLY_CONSUMER_ID,),
        "implicit_consumer_ids": tuple(),
        "production_allowlist_empty": True,
        "zero_implicit_consumers": True,
        "exact_consumer_id_match_required": True,
        "allowlist_status": "zero_production_one_audit_only_consumer",
        "source_record_refs": (contract.contract_id, *inventory_refs),
    }
    return _hashed_record(
        SelfStateReadbackConsumerAllowlistRecord,
        payload,
        id_field="allowlist_id",
        hash_field="allowlist_sha256",
        prefix="self_state_readback_consumer_allowlist",
    )


def _build_readback(
    *,
    authorization: SelfStateReadbackAuthorizationRecord,
    source: Package138SourceBundle,
    operating_system_process_id: int,
    bound_at_monotonic_ns: int,
) -> BoundedSelfStateReadbackRecord:
    state = source.package_133.leaf
    head = source.active_head
    if source.active_identity_binding is None:
        raise RuntimeError("blocked_package_138_active_process_binding_missing")
    if operating_system_process_id != int(
        source.active_identity_binding["operating_system_process_id"]
    ):
        raise RuntimeError("blocked_package_138_operating_system_process_binding_mismatch")
    payload: dict[str, Any] = {
        "readback_id": "",
        "readback_sha256": "",
        "schema_version": READBACK_SCHEMA_VERSION,
        "created_at": utc_now(),
        "authorization_ref": authorization.authorization_id,
        "contract_ref": authorization.contract_ref,
        "allowlist_ref": authorization.allowlist_ref,
        "source_binding_ref": authorization.source_binding_ref,
        "runtime_session_id": authorization.runtime_session_id,
        "process_instance_id": authorization.process_instance_id,
        "operating_system_process_id": operating_system_process_id,
        "consumer_id": authorization.consumer_id,
        "active_head_id": head.active_head_id,
        "active_head_sha256": head.active_head_sha256,
        "head_revision": head.head_revision,
        "self_state_record_id": state.self_state_record_id,
        "self_state_sha256": state.self_state_sha256,
        "representation_contract_ref": state.representation_contract_ref,
        "parent_self_state_record_id": state.parent_self_state_record_id,
        "parent_self_state_sha256": state.parent_self_state_sha256,
        "origin_session_id": state.origin_session_id,
        "source_session_id": state.source_session_id,
        "session_provenance_refs_sha256": sha256_payload(state.session_provenance_refs),
        "transition_provenance_ref": state.transition_provenance_ref,
        "exposed_structural_fields": EXPOSED_STRUCTURAL_FIELDS,
        "self_state_lineage_id": state.self_state_lineage_id,
        "self_state_version": state.self_state_version,
        "lineage_generation": state.lineage_generation,
        "representation_status": state.representation_status,
        "governance_profile_version": state.governance_profile_version,
        "bound_at_monotonic_ns": bound_at_monotonic_ns,
        "expires_at_monotonic_ns": authorization.expires_at_monotonic_ns,
        "read_only": True,
        "same_session_only": True,
        "active_runtime_slot_persisted": False,
        "semantic_identity_created": False,
        "autobiographical_memory_created": False,
        "psychological_state_created": False,
        "world_knowledge_created": False,
        "runtime_behavior_authority": False,
        "memory_authority": False,
        "drive_authority": False,
        "perception_authority": False,
        "attention_authority": False,
        "candidate_ordering_authority": False,
        "purpose_authority": False,
        "thought_engine_authority": False,
        "action_authority": False,
        "output_authority": False,
        "binding_status": "active_same_session_audit_only_readback",
        "source_record_refs": (
            authorization.authorization_id,
            source.source_binding.source_binding_id,
            head.active_head_id,
            state.self_state_record_id,
            state.representation_contract_ref,
        ),
    }
    return _hashed_record(
        BoundedSelfStateReadbackRecord,
        payload,
        id_field="readback_id",
        hash_field="readback_sha256",
        prefix="bounded_self_state_readback",
    )


def _build_consumption(
    *,
    readback: BoundedSelfStateReadbackRecord,
    authorization: SelfStateReadbackAuthorizationRecord,
    source: Package138SourceBundle,
    consumed_at_monotonic_ns: int,
) -> SelfStateReadbackConsumptionRecord:
    head = source.active_head
    if source.active_identity_binding is None:
        raise RuntimeError("blocked_package_138_active_process_binding_missing")
    payload: dict[str, Any] = {
        "consumption_id": "",
        "consumption_sha256": "",
        "schema_version": CONSUMPTION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "readback_ref": readback.readback_id,
        "authorization_ref": authorization.authorization_id,
        "runtime_session_id": readback.runtime_session_id,
        "process_instance_id": readback.process_instance_id,
        "consumer_id": readback.consumer_id,
        "consumed_at_monotonic_ns": consumed_at_monotonic_ns,
        "observed_active_head_sha256": head.active_head_sha256,
        "observed_head_revision": head.head_revision,
        "observed_self_state_sha256": head.self_state_sha256,
        "exact_head_match": readback.active_head_sha256 == head.active_head_sha256 and readback.head_revision == head.head_revision,
        "exact_state_match": readback.self_state_record_id == head.self_state_record_id and readback.self_state_sha256 == head.self_state_sha256,
        "same_session_match": readback.runtime_session_id == authorization.runtime_session_id,
        "same_process_match": all(
            (
                readback.process_instance_id == authorization.process_instance_id,
                readback.process_instance_id == head.bound_process_instance_id,
                readback.operating_system_process_id
                == int(source.active_identity_binding["operating_system_process_id"]),
            )
        ),
        "within_expiry": readback.bound_at_monotonic_ns <= consumed_at_monotonic_ns < readback.expires_at_monotonic_ns,
        "read_only_consumption": True,
        "structural_fields_only": True,
        "runtime_behavior_changed": False,
        "memory_written": False,
        "drive_changed": False,
        "perception_or_attention_changed": False,
        "candidate_ordering_changed": False,
        "selected_action_created": False,
        "output_created": False,
        "consumption_status": "consumed_read_only_audit_surface",
        "source_record_refs": (
            readback.readback_id,
            authorization.authorization_id,
            head.active_head_id,
            head.self_state_record_id,
        ),
    }
    return _hashed_record(
        SelfStateReadbackConsumptionRecord,
        payload,
        id_field="consumption_id",
        hash_field="consumption_sha256",
        prefix="self_state_readback_consumption",
    )


def _build_lifecycle(
    *,
    readback: BoundedSelfStateReadbackRecord,
    observed_head: Any,
    lifecycle_kind: str,
    terminal_reason: str,
    occurred_at_monotonic_ns: int,
    additional_source_refs: tuple[str, ...] = (),
) -> SelfStateReadbackLifecycleRecord:
    payload: dict[str, Any] = {
        "lifecycle_id": "",
        "lifecycle_sha256": "",
        "schema_version": LIFECYCLE_SCHEMA_VERSION,
        "created_at": utc_now(),
        "readback_ref": readback.readback_id,
        "runtime_session_id": readback.runtime_session_id,
        "lifecycle_kind": lifecycle_kind,
        "occurred_at_monotonic_ns": occurred_at_monotonic_ns,
        "expected_active_head_sha256": readback.active_head_sha256,
        "expected_head_revision": readback.head_revision,
        "observed_active_head_sha256": observed_head.active_head_sha256,
        "observed_head_revision": observed_head.head_revision,
        "readback_active_after": False,
        "automatically_refreshed": False,
        "automatically_rebound": False,
        "carried_to_another_session": False,
        "terminal_reason": terminal_reason,
        "source_record_refs": (
            readback.readback_id,
            observed_head.active_head_id,
            *additional_source_refs,
        ),
    }
    return _hashed_record(
        SelfStateReadbackLifecycleRecord,
        payload,
        id_field="lifecycle_id",
        hash_field="lifecycle_sha256",
        prefix="self_state_readback_lifecycle",
    )


def invalidate_readbacks_before_authorized_head_transition(
    *,
    state_dir: str | Path,
    expected_head: Any,
    authorization_ref: str,
    operation: str,
    occurred_at_monotonic_ns: int | None = None,
) -> dict[str, Any]:
    """Terminate every live readback bound to one exact pre-transition head."""
    if operation not in {
        "rollback_to_verified_ancestor",
        "roll_forward_to_preserved_descendant",
    }:
        raise ValueError("invalid authorized active-head transition")
    if not authorization_ref:
        raise ValueError("active-head transition authorization reference is required")
    store = Package138SelfStateReadbackStore(state_dir)
    integrity = store.audit_integrity()
    if not integrity["valid"]:
        raise RuntimeError("blocked_corrupt_package_138_readback_store")
    matching_payloads = tuple(
        item
        for item in store.list_payloads("bounded_self_state_readbacks")
        if item.get("active_head_id") == expected_head.active_head_id
        and item.get("active_head_sha256") == expected_head.active_head_sha256
        and item.get("head_revision") == expected_head.head_revision
        and item.get("self_state_record_id") == expected_head.self_state_record_id
        and item.get("self_state_sha256") == expected_head.self_state_sha256
    )
    terminal_before: list[str] = []
    invalidated: list[str] = []
    occurred = int(monotonic_ns() if occurred_at_monotonic_ns is None else occurred_at_monotonic_ns)
    for payload in matching_payloads:
        readback = _record_from_payload(BoundedSelfStateReadbackRecord, payload)
        if store.terminal_lifecycle_for(readback.readback_id) is not None:
            terminal_before.append(readback.readback_id)
            continue
        lifecycle = _build_lifecycle(
            readback=readback,
            observed_head=expected_head,
            lifecycle_kind="invalidated_before_authorized_active_head_transition",
            terminal_reason=f"authorized_head_transition:{operation}",
            occurred_at_monotonic_ns=occurred,
            additional_source_refs=(authorization_ref,),
        )
        store.append_once("self_state_readback_lifecycle_records", lifecycle)
        invalidated.append(lifecycle.lifecycle_id)
    active_after = tuple(
        item["readback_id"]
        for item in matching_payloads
        if store.terminal_lifecycle_for(str(item["readback_id"])) is None
    )
    if active_after:
        raise RuntimeError("blocked_active_package_138_readback_remains_before_head_change")
    return {
        "matching_readback_refs": tuple(
            str(item["readback_id"]) for item in matching_payloads
        ),
        "preexisting_terminal_readback_refs": tuple(terminal_before),
        "new_lifecycle_refs": tuple(invalidated),
        "active_readback_count_before": len(invalidated),
        "active_readback_count_after": 0,
        "all_matching_readbacks_terminal": True,
        "operation": operation,
        "authorization_ref": authorization_ref,
    }


def _build_blocked_attempt(
    *,
    operation: str,
    runtime_session_id: str,
    process_instance_id: str,
    consumer_id: str,
    authorization_ref: str | None,
    readback_ref: str | None,
    expected_head: Any,
    observed_head: Any,
    failure_reason: str,
) -> SelfStateReadbackBlockedAttemptRecord:
    payload: dict[str, Any] = {
        "blocked_attempt_id": "",
        "blocked_attempt_sha256": "",
        "schema_version": BLOCKED_SCHEMA_VERSION,
        "created_at": utc_now(),
        "operation": operation,
        "runtime_session_id": runtime_session_id,
        "process_instance_id": process_instance_id,
        "consumer_id": consumer_id,
        "authorization_ref": authorization_ref,
        "readback_ref": readback_ref,
        "expected_head_revision": getattr(expected_head, "head_revision", None),
        "observed_head_revision": getattr(observed_head, "head_revision", None),
        "expected_active_head_sha256": getattr(expected_head, "active_head_sha256", None),
        "observed_active_head_sha256": getattr(observed_head, "active_head_sha256", None),
        "failure_reason": failure_reason,
        "readback_created": False,
        "consumption_created": False,
        "silent_latest_selected": False,
        "automatically_refreshed": False,
        "automatically_rebound": False,
        "authoritative_state_changed": False,
        "source_record_refs": tuple(
            item
            for item in (authorization_ref, readback_ref, getattr(observed_head, "active_head_id", None))
            if item
        ),
    }
    return _hashed_record(
        SelfStateReadbackBlockedAttemptRecord,
        payload,
        id_field="blocked_attempt_id",
        hash_field="blocked_attempt_sha256",
        prefix="self_state_readback_blocked_attempt",
    )


def _authority_invariant_payload(
    *,
    ashl_root: str | Path,
    source: Package138SourceBundle,
) -> dict[str, str]:
    root = Path(ashl_root).resolve()
    return {
        "runtime_behavior_sha256": _source_set_sha256(
            root,
            (
                "ashl_core_v1/runtime/no_codex_runtime_guard.py",
                "ashl_core_v1/runtime/perception_attention_closure_types.py",
            ),
        ),
        "selected_action_sha256": sha256_payload({"selected_action": None, "package_138_access": "none"}),
        "memory_sha256": _tree_python_sha256(root / "ashl_core_v1" / "memory"),
        "drive_sha256": _tree_python_sha256(root / "ashl_core_v1" / "endocrine"),
        "perception_history_sha256": sha256_payload(
            {
                "perception_tree": _tree_python_sha256(root / "ashl_core_v1" / "perception"),
                "history_loaded": False,
            }
        ),
        "self_state_history_sha256": source.source_binding.package_133_tree_sha256,
        "active_head_sha256": source.active_head.active_head_sha256,
        "output_sha256": _source_set_sha256(
            root,
            (
                "ashl_core_v1/runtime/raw_output_token_registry.py",
                "ashl_core_v1/runtime/operator_console_types.py",
            ),
        ),
        "recovery_result_sha256": sha256_payload(
            {
                "active_head_id": source.active_head.active_head_id,
                "active_head_sha256": source.active_head.active_head_sha256,
                "head_revision": source.active_head.head_revision,
                "self_state_record_id": source.active_head.self_state_record_id,
            }
        ),
    }


def _build_counterfactual_snapshot(
    *,
    branch_kind: str,
    runtime_session_id: str,
    readback_surface_sha256: str | None,
    invariants: dict[str, str],
    source_refs: tuple[str, ...],
) -> SelfStateReadbackCounterfactualSnapshot:
    payload: dict[str, Any] = {
        "snapshot_id": "",
        "snapshot_sha256": "",
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "branch_kind": branch_kind,
        "runtime_session_id": runtime_session_id,
        "readback_surface_present": readback_surface_sha256 is not None,
        "readback_surface_sha256": readback_surface_sha256,
        **invariants,
        "candidate_ordering_changed": False,
        "selected_action_created": False,
        "memory_write_created": False,
        "drive_changed": False,
        "perception_history_changed": False,
        "self_state_history_changed": False,
        "active_head_changed": False,
        "output_created": False,
        "recovery_result_changed": False,
        "production_behavior_changed": False,
        "source_record_refs": source_refs,
    }
    return _hashed_record(
        SelfStateReadbackCounterfactualSnapshot,
        payload,
        id_field="snapshot_id",
        hash_field="snapshot_sha256",
        prefix="self_state_readback_counterfactual_snapshot",
    )


def _build_process_receipt(
    *,
    process_role: str,
    process_instance_id: str,
    operating_system_process_id: int,
    runtime_session_id: str,
    started: int,
    ended: int,
    authorization_ref: str | None,
    readback_ref: str | None,
    consumption_ref: str | None,
    lifecycle_ref: str | None,
    blocked_attempt_ref: str | None,
    worker_status: str,
    source_refs: tuple[str, ...],
) -> SelfStateReadbackProcessReceipt:
    payload: dict[str, Any] = {
        "process_receipt_id": "",
        "process_receipt_sha256": "",
        "schema_version": PROCESS_SCHEMA_VERSION,
        "created_at": utc_now(),
        "process_role": process_role,
        "process_instance_id": process_instance_id,
        "operating_system_process_id": operating_system_process_id,
        "runtime_session_id": runtime_session_id,
        "started_monotonic_ns": started,
        "ended_monotonic_ns": ended,
        "authorization_ref": authorization_ref,
        "readback_ref": readback_ref,
        "consumption_ref": consumption_ref,
        "lifecycle_ref": lifecycle_ref,
        "blocked_attempt_ref": blocked_attempt_ref,
        "active_context_present_at_process_end": False,
        "prior_session_readback_loaded": False,
        "worker_status": worker_status,
        "source_record_refs": source_refs,
    }
    return _hashed_record(
        SelfStateReadbackProcessReceipt,
        payload,
        id_field="process_receipt_id",
        hash_field="process_receipt_sha256",
        prefix="self_state_readback_process_receipt",
    )


def _head_from_authorization(authorization: SelfStateReadbackAuthorizationRecord) -> Any:
    return SimpleNamespace(
        active_head_id=authorization.expected_active_head_id,
        active_head_sha256=authorization.expected_active_head_sha256,
        head_revision=authorization.expected_head_revision,
    )


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
        if isinstance(values.get(item.name), list):
            values[item.name] = _tuple_tree(values[item.name])
    return record_type(**values)


def _tuple_tree(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_tuple_tree(item) for item in value)
    if isinstance(value, dict):
        return {key: _tuple_tree(item) for key, item in value.items()}
    return value


def _source_set_sha256(root: Path, relative_paths: tuple[str, ...]) -> str:
    payload = []
    for relative in relative_paths:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        payload.append((relative, sha256_bytes(path.read_bytes())))
    return sha256_payload(payload)


def _tree_python_sha256(root: Path) -> str:
    if not root.is_dir():
        raise FileNotFoundError(root)
    return sha256_payload(
        tuple(
            (
                path.relative_to(root).as_posix(),
                sha256_bytes(path.read_bytes()),
            )
            for path in sorted(root.rglob("*.py"), key=lambda item: item.as_posix().lower())
            if "__pycache__" not in path.parts
        )
    )


def _validate_external_roots(root: Path, output: Path, *sources: Path) -> None:
    if _is_within(output, root):
        raise ValueError("Package 138 state_dir must be external to the repository")
    if len(set(sources)) != len(sources) or output in sources:
        raise ValueError("Package 138 authority roots must be distinct")
    if not all(source.is_dir() for source in sources):
        raise FileNotFoundError("Package 138 authority source directory is missing")


def _is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.relative_to(parent)
        return True
    except ValueError:
        return False


def _load_registry(root: Path) -> dict[str, Any]:
    path = root / "ashl_core_v1/docs/reference/package_number_registry_v0.json"
    return dict(json.loads(path.read_text(encoding="utf-8")))


def _git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", *args),
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()
