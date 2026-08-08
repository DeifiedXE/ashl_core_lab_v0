"""Evidence-producing negative controls for Package 138."""

from __future__ import annotations

import json
import shutil
import sqlite3
from dataclasses import fields
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, sha256_payload, stable_id, utc_now
from ashl_core_v1.state.package_138_self_state_readback_store import (
    DATABASE_NAME,
    PACKAGE_DIR,
    Package138SelfStateReadbackStore,
)
from ashl_core_v1.state.self_state_readback_runtime import (
    _hashed_record,
    create_self_state_readback_authorization,
    initialize_self_state_readback_boundary,
    run_self_state_readback_worker,
)
from ashl_core_v1.state.self_state_readback_types import (
    AUDIT_ONLY_CONSUMER_ID,
    CONTROL_NAMES,
    CONTROL_SCHEMA_VERSION,
    BoundedSelfStateReadbackRecord,
    Package138ControlResult,
    SelfStateReadbackAuthorizationRecord,
)


def run_package_138_self_state_readback_controls(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    state_dir: str | Path,
    append: bool = True,
) -> Package138ControlResult:
    store = Package138SelfStateReadbackStore(state_dir)
    existing = store.latest_payload("package_138_control_results")
    if existing is not None and existing.get("controls_passed") is True:
        return _record_from_payload(Package138ControlResult, existing)
    initialized = initialize_self_state_readback_boundary(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        state_dir=state_dir,
    )
    source = initialized["source"]
    contract = initialized["contract"]
    allowlist = initialized["allowlist"]
    outcomes: dict[str, bool] = {}
    evidence: list[str] = []

    outcomes["production_allowlist_empty"] = (
        allowlist.production_consumer_ids == ()
        and allowlist.implicit_consumer_ids == ()
        and allowlist.production_allowlist_empty
    )
    outcomes["implicit_consumer_rejected"] = _rejects(
        lambda: create_self_state_readback_authorization(
            ashl_root=ashl_root,
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=package_134_state_dir,
            package_137_state_dir=package_137_state_dir,
            state_dir=state_dir,
            runtime_session_id=source.active_head.bound_session_id,
            process_instance_id=stable_id("package_138_implicit_consumer_control"),
            consumer_id="implicit_runtime_consumer",
        ),
        "not_allowlisted",
    )
    outcomes["unknown_consumer_rejected"] = _rejects(
        lambda: create_self_state_readback_authorization(
            ashl_root=ashl_root,
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=package_134_state_dir,
            package_137_state_dir=package_137_state_dir,
            state_dir=state_dir,
            runtime_session_id=source.active_head.bound_session_id,
            process_instance_id=stable_id("package_138_unknown_consumer_control"),
            consumer_id="unknown_consumer",
        ),
        "not_allowlisted",
    )

    missing_process = stable_id("package_138_missing_authorization_control")
    missing = run_self_state_readback_worker(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        state_dir=state_dir,
        process_role="fresh_process_probe_b",
        runtime_session_id=source.active_head.bound_session_id,
        process_instance_id=missing_process,
        authorization_id=None,
    )
    outcomes["missing_authorization_rejected"] = (
        missing["status"] == "blocked_readback_authorization_missing"
        and not missing["blocked_attempt"].readback_created
    )
    evidence.append(missing["blocked_attempt"].blocked_attempt_id)

    consumed_authorization = _first_consumed_authorization(store)
    if consumed_authorization is None:
        raise RuntimeError("blocked_package_138_control_source_authorization_missing")
    process_id = source.active_head.bound_process_instance_id
    valid = _control_authorization(
        source=source,
        source_binding_ref=initialized["source_binding"].source_binding_id,
        original=consumed_authorization,
    )
    store.append_once("self_state_readback_authorizations", valid)
    evidence.append(valid.authorization_id)

    expired = _rehash_authorization(
        valid,
        {
            "issued_at_monotonic_ns": 1,
            "expires_at_monotonic_ns": 2,
        },
    )
    store.append_once("self_state_readback_authorizations", expired)
    expired_result = _run_blocked_worker(
        ashl_root, package_133_state_dir, package_134_state_dir,
        package_137_state_dir, state_dir, expired,
        expired.runtime_session_id, expired.process_instance_id,
    )
    outcomes["expired_authorization_rejected"] = _blocked_for(
        expired_result, "authorization_expired"
    )
    wrong_session = _run_blocked_worker(
        ashl_root, package_133_state_dir, package_134_state_dir,
        package_137_state_dir, state_dir, valid, "wrong_session", process_id,
    )
    outcomes["wrong_session_rejected"] = _blocked_for(
        wrong_session, "session_mismatch"
    )
    wrong_process = _run_blocked_worker(
        ashl_root, package_133_state_dir, package_134_state_dir,
        package_137_state_dir, state_dir, valid, valid.runtime_session_id, "wrong_process",
    )
    outcomes["wrong_process_rejected"] = _blocked_for(
        wrong_process, "process_mismatch"
    )
    mutations = (
        ("active_head_revision_mismatch_rejected", {"expected_head_revision": valid.expected_head_revision + 1}, "active_head_revision_mismatch"),
        ("active_head_hash_mismatch_rejected", {"expected_active_head_sha256": "0" * 64}, "active_head_hash_mismatch"),
        ("self_state_record_mismatch_rejected", {"expected_self_state_record_id": "persistent_self_state:wrong"}, "self_state_record_mismatch"),
        ("self_state_hash_mismatch_rejected", {"expected_self_state_sha256": "1" * 64}, "self_state_hash_mismatch"),
    )
    for name, changes, expected in mutations:
        tampered = _rehash_authorization(valid, changes)
        store.append_once("self_state_readback_authorizations", tampered)
        blocked_result = _run_blocked_worker(
            ashl_root, package_133_state_dir, package_134_state_dir,
            package_137_state_dir, state_dir, tampered,
            valid.runtime_session_id, valid.process_instance_id,
        )
        outcomes[name] = _blocked_for(blocked_result, expected)

    consumed = _first_consumed_authorization(store)
    reused = (
        _run_blocked_worker(
            ashl_root, package_133_state_dir, package_134_state_dir,
            package_137_state_dir, state_dir, consumed,
            consumed.runtime_session_id, consumed.process_instance_id,
        )
        if consumed else None
    )
    outcomes["authorization_reuse_rejected"] = bool(reused) and _blocked_for(
        reused or {}, "authorization_already_consumed"
    )
    reset = store.latest_payload("self_state_readback_fresh_process_resets")
    stale_records = store.list_payloads("self_state_readback_lifecycle_records")
    outcomes["stale_readback_invalidated_after_real_cas"] = bool(reset) and any(
        item.get("lifecycle_kind") == "stale_active_head_revision_changed"
        and item.get("readback_active_after") is False
        for item in stale_records
    )
    outcomes["silent_refresh_and_auto_rebind_rejected"] = bool(reset) and all(
        not item.get("automatically_refreshed") and not item.get("automatically_rebound")
        for item in stale_records
    )
    outcomes["prior_session_readback_not_recovered"] = bool(reset) and all(
        (
            not reset.get("prior_readback_restored"),
            not reset.get("prior_readback_consumable"),
            reset.get("fresh_authorization_required"),
        )
    )
    if reset:
        evidence.append(str(reset["reset_record_id"]))

    readback_payload = store.latest_payload("bounded_self_state_readbacks")
    outcomes["semantic_and_forbidden_field_injection_rejected"] = bool(readback_payload) and _rejects(
        lambda: _rehash_readback(readback_payload or {}, {"semantic_identity_created": True}),
        "semantic",
    )
    outcomes["teacher_scope_expansion_rejected"] = _rejects(
        lambda: _rehash_authorization(
            valid, {"teacher_consumer_approval_inferred": True}
        ),
        "teacher",
    )
    outcomes["behavior_authority_injection_rejected"] = bool(readback_payload) and _rejects(
        lambda: _rehash_readback(readback_payload or {}, {"runtime_behavior_authority": True}),
        "authority",
    )
    outcomes["corrupt_authority_or_readback_store_rejected"] = _corrupt_store_control(store)
    outcomes["append_only_store_enforced"] = all(
        _rejects(call, "append-only")
        for call in (
            lambda: store.update(),
            lambda: store.delete(),
            lambda: store.replace(),
        )
    )
    evidence.extend(f"validator:{name}" for name, passed in outcomes.items() if passed)
    for name in (
        "semantic_and_forbidden_field_injection_rejected",
        "teacher_scope_expansion_rejected",
        "behavior_authority_injection_rejected",
        "corrupt_authority_or_readback_store_rejected",
    ):
        if outcomes.get(name):
            blocked = _append_control_blocked_attempt(
                store=store,
                source=source,
                operation=name,
                failure_reason=f"blocked_{name}",
            )
            evidence.append(blocked.blocked_attempt_id)
    passed = tuple(name for name in CONTROL_NAMES if outcomes.get(name, False))
    result = Package138ControlResult(
        control_result_id=f"package_138_controls:{sha256_payload(outcomes)[:16]}",
        schema_version=CONTROL_SCHEMA_VERSION,
        created_at=utc_now(),
        control_names=CONTROL_NAMES,
        passed_control_names=passed,
        expected_count=len(CONTROL_NAMES),
        passed_count=len(passed),
        controls_passed=len(passed) == len(CONTROL_NAMES),
        evidence_refs=tuple(dict.fromkeys(evidence)),
    )
    if append:
        store.append_once("package_138_control_results", result)
    return result


def _run_blocked_worker(
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    state_dir: str | Path,
    authorization: SelfStateReadbackAuthorizationRecord,
    runtime_session_id: str,
    process_instance_id: str,
) -> dict[str, Any]:
    return run_self_state_readback_worker(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        state_dir=state_dir,
        process_role="fresh_process_probe_b",
        runtime_session_id=runtime_session_id,
        process_instance_id=process_instance_id,
        authorization_id=authorization.authorization_id,
    )


def _blocked_for(result: dict[str, Any], reason: str) -> bool:
    blocked = result.get("blocked_attempt")
    return bool(blocked) and reason in blocked.failure_reason


def _append_control_blocked_attempt(
    *,
    store: Package138SelfStateReadbackStore,
    source: Any,
    operation: str,
    failure_reason: str,
) -> Any:
    from ashl_core_v1.state.self_state_readback_runtime import _build_blocked_attempt

    blocked = _build_blocked_attempt(
        operation=operation,
        runtime_session_id=source.active_head.bound_session_id,
        process_instance_id=stable_id(f"package_138_{operation}"),
        consumer_id=AUDIT_ONLY_CONSUMER_ID,
        authorization_ref=None,
        readback_ref=None,
        expected_head=source.active_head,
        observed_head=source.active_head,
        failure_reason=failure_reason,
    )
    store.append_once("self_state_readback_blocked_attempts", blocked)
    return blocked


def _first_consumed_authorization(
    store: Package138SelfStateReadbackStore,
) -> SelfStateReadbackAuthorizationRecord | None:
    for payload in reversed(store.list_payloads("self_state_readback_authorizations")):
        if store.authorization_has_readback(str(payload["authorization_id"])):
            return _record_from_payload(SelfStateReadbackAuthorizationRecord, payload)
    return None


def _rehash_authorization(
    original: SelfStateReadbackAuthorizationRecord,
    changes: dict[str, Any],
) -> SelfStateReadbackAuthorizationRecord:
    payload = original.to_dict()
    payload.update(changes)
    payload["authorization_id"] = ""
    payload["authorization_sha256"] = ""
    return _hashed_record(
        SelfStateReadbackAuthorizationRecord,
        payload,
        id_field="authorization_id",
        hash_field="authorization_sha256",
        prefix="self_state_readback_authorization",
    )


def _control_authorization(
    *,
    source: Any,
    source_binding_ref: str,
    original: SelfStateReadbackAuthorizationRecord,
) -> SelfStateReadbackAuthorizationRecord:
    issued = monotonic_ns()
    return _rehash_authorization(
        original,
        {
            "created_at": utc_now(),
            "source_binding_ref": source_binding_ref,
            "runtime_session_id": source.active_head.bound_session_id,
            "process_instance_id": source.active_head.bound_process_instance_id,
            "expected_active_head_id": source.active_head.active_head_id,
            "expected_active_head_sha256": source.active_head.active_head_sha256,
            "expected_head_revision": source.active_head.head_revision,
            "expected_self_state_record_id": source.active_head.self_state_record_id,
            "expected_self_state_sha256": source.active_head.self_state_sha256,
            "issued_at_monotonic_ns": issued,
            "expires_at_monotonic_ns": issued + 30_000_000_000,
            "source_record_refs": (
                source_binding_ref,
                source.active_head.active_head_id,
                source.active_head.self_state_record_id,
                "control_only_invalid_record_construction",
            ),
        },
    )


def _rehash_readback(
    original: dict[str, Any], changes: dict[str, Any]
) -> BoundedSelfStateReadbackRecord:
    payload = dict(original)
    payload.update(changes)
    payload["readback_id"] = ""
    payload["readback_sha256"] = ""
    return _hashed_record(
        BoundedSelfStateReadbackRecord,
        payload,
        id_field="readback_id",
        hash_field="readback_sha256",
        prefix="bounded_self_state_readback",
    )


def _corrupt_store_control(store: Package138SelfStateReadbackStore) -> bool:
    with TemporaryDirectory() as temporary:
        target_root = Path(temporary) / PACKAGE_DIR
        target_root.mkdir(parents=True)
        target = target_root / DATABASE_NAME
        shutil.copy2(store.database_path, target)
        connection = sqlite3.connect(target)
        try:
            row = connection.execute(
                "SELECT row_id, payload_json FROM self_state_readback_contracts ORDER BY row_id LIMIT 1"
            ).fetchone()
            if row is None:
                return False
            payload = json.loads(str(row[1]))
            payload["contract_status"] = "corrupt"
            connection.execute(
                "UPDATE self_state_readback_contracts SET payload_json = ? WHERE row_id = ?",
                (json.dumps(payload, sort_keys=True), int(row[0])),
            )
            connection.commit()
        finally:
            connection.close()
        return not Package138SelfStateReadbackStore(temporary).audit_integrity()["valid"]


def _rejects(operation: Callable[[], Any], expected: str) -> bool:
    try:
        operation()
    except (KeyError, RuntimeError, TypeError, ValueError) as error:
        return expected.lower() in str(error).lower()
    return False


def _record_from_payload(record_type: type[Any], payload: dict[str, Any]) -> Any:
    values = dict(payload)
    for item in fields(record_type):
        if isinstance(values.get(item.name), list):
            values[item.name] = tuple(values[item.name])
    return record_type(**values)
