"""Actual Package 134 recovery failure controls."""

from __future__ import annotations

import os
import shutil
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable

from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now
from ashl_core_v1.state.package_134_package_133_source import (
    Package133SourceBundle,
    load_package_133_source_read_only,
)
from ashl_core_v1.state.persistent_self_state_boundary import (
    load_authoritative_self_state_contract,
)
from ashl_core_v1.state.persistent_self_state_lineage import (
    build_initial_self_state_record,
    build_self_state_lineage_validation_record,
    build_successor_self_state_records,
)
from ashl_core_v1.state.persistent_self_state_store import (
    PersistentSelfStateStore,
    package_133_store_path,
)
from ashl_core_v1.state.persistent_session_recovery_runtime import (
    build_authorization_consumption,
    build_clean_shutdown_record,
    build_identity_binding,
    build_initial_active_head,
    build_recovered_active_head,
    build_recovery_authorization,
    build_recovery_resolution,
    build_successful_cas_event,
    validate_recovery_authorization,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    ActiveHeadCASConflict,
    PersistentSessionRecoveryStore,
)
from ashl_core_v1.state.persistent_session_recovery_types import (
    CONTROL_NAMES,
    CONTROL_SCHEMA_VERSION,
    ActiveSelfStateHeadRecord,
    Package134RecoveryControlResult,
    PersistentSessionRecoveryAuthorization,
)


def run_package_134_recovery_controls(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    state_dir: str | Path,
    append: bool = True,
) -> Package134RecoveryControlResult:
    source = load_package_133_source_read_only(package_133_state_dir)

    def passes(call: Callable[[], bool]) -> bool:
        try:
            return bool(call())
        except Exception:
            return False

    controls = {
        "authorization_missing_blocked": passes(_authorization_missing_blocked),
        "authorization_expired_blocked": passes(
            lambda: _authorization_expired_blocked(source)
        ),
        "authorization_reuse_blocked": passes(
            lambda: _authorization_reuse_blocked(source)
        ),
        "wrong_lineage_authorization_blocked": passes(
            lambda: _wrong_lineage_authorization_blocked(source)
        ),
        "missing_head_blocked": passes(_missing_head_blocked),
        "corrupt_head_blocked": passes(lambda: _corrupt_head_blocked(source)),
        "stale_head_blocked": passes(lambda: _stale_head_blocked(source)),
        "ambiguous_lineage_blocked": passes(
            lambda: _ambiguous_lineage_blocked(
                ashl_root=ashl_root,
                package_133_state_dir=package_133_state_dir,
            )
        ),
        "cas_conflict_blocked": passes(lambda: _cas_conflict_blocked(source)),
        "dirty_shutdown_blocked": passes(lambda: _dirty_shutdown_blocked(source)),
        "partial_write_rolled_back": passes(lambda: _partial_write_rolled_back(source)),
        "forbidden_content_and_authority_rejected": passes(
            lambda: _forbidden_content_and_authority_rejected(source)
        ),
    }
    ordered = tuple((name, controls[name]) for name in CONTROL_NAMES)
    result = Package134RecoveryControlResult(
        control_result_id=(
            f"package_134_recovery_controls:{sha256_payload(dict(ordered))[:16]}"
        ),
        schema_version=CONTROL_SCHEMA_VERSION,
        created_at=utc_now(),
        controls=ordered,
        passed_count=sum(flag for _name, flag in ordered),
        expected_count=len(CONTROL_NAMES),
        controls_passed=all(flag for _name, flag in ordered),
    )
    if append:
        PersistentSessionRecoveryStore(state_dir).append_once(
            "package_134_recovery_control_results", result
        )
    return result


def _authorization_missing_blocked() -> bool:
    with TemporaryDirectory() as directory:
        store = PersistentSessionRecoveryStore(directory)
        try:
            store.get_authorization("session_recovery_authorization:missing")
        except KeyError:
            return True
    return False


def _authorization_expired_blocked(source: Package133SourceBundle) -> bool:
    with TemporaryDirectory() as directory:
        store = PersistentSessionRecoveryStore(directory)
        authorization = build_recovery_authorization(
            source=source,
            operation="initialize_active_head",
            target_session_id="expired_session",
            target_process_instance_id="expired_process",
            expected_head=None,
            created_at="2000-01-01T00:00:00+00:00",
            expires_at="2000-01-01T00:01:00+00:00",
        )
        store.append_record("persistent_session_recovery_authorizations", authorization)
        return _rejects(
            lambda: validate_recovery_authorization(
                store=store,
                authorization=authorization,
                source=source,
                operation="initialize_active_head",
                session_id="expired_session",
                process_instance_id="expired_process",
            ),
            "expired",
        )


def _authorization_reuse_blocked(source: Package133SourceBundle) -> bool:
    with TemporaryDirectory() as directory:
        store, _head, authorization, _binding = _seed_initialized_store(
            source=source,
            state_dir=directory,
            clean_shutdown=False,
        )
        return _rejects(
            lambda: validate_recovery_authorization(
                store=store,
                authorization=authorization,
                source=source,
                operation="initialize_active_head",
                session_id=authorization.target_session_id,
                process_instance_id=authorization.target_process_instance_id,
            ),
            "already_consumed",
        )


def _wrong_lineage_authorization_blocked(source: Package133SourceBundle) -> bool:
    with TemporaryDirectory() as directory:
        store = PersistentSessionRecoveryStore(directory)
        valid = build_recovery_authorization(
            source=source,
            operation="initialize_active_head",
            target_session_id="wrong_lineage_session",
            target_process_instance_id="wrong_lineage_process",
            expected_head=None,
        )
        payload = valid.to_dict()
        payload["target_self_state_lineage_id"] = "self_state_lineage:wrong_lineage"
        payload["authorization_id"] = ""
        payload["authorization_sha256"] = ""
        identity = dict(payload)
        identity.pop("authorization_id", None)
        identity.pop("authorization_sha256", None)
        digest = sha256_payload(identity)
        payload["authorization_sha256"] = digest
        payload["authorization_id"] = f"session_recovery_authorization:{digest[:16]}"
        authorization = PersistentSessionRecoveryAuthorization.from_dict(payload)
        store.append_record("persistent_session_recovery_authorizations", authorization)
        return _rejects(
            lambda: validate_recovery_authorization(
                store=store,
                authorization=authorization,
                source=source,
                operation="initialize_active_head",
                session_id=authorization.target_session_id,
                process_instance_id=authorization.target_process_instance_id,
            ),
            "scope_mismatch",
        )


def _missing_head_blocked() -> bool:
    with TemporaryDirectory() as directory:
        store = PersistentSessionRecoveryStore(directory)
        return _rejects(store.get_active_head, "missing_active_head")


def _corrupt_head_blocked(source: Package133SourceBundle) -> bool:
    with TemporaryDirectory() as directory:
        store, _head, _authorization, _binding = _seed_initialized_store(
            source=source,
            state_dir=directory,
            clean_shutdown=True,
        )
        with store.connection() as connection:
            connection.execute(
                "UPDATE active_self_state_head SET payload_sha256 = ? WHERE singleton_key = 'active'",
                ("0" * 64,),
            )
            connection.commit()
        return _rejects(store.get_active_head, "corrupt_active_head")


def _stale_head_blocked(source: Package133SourceBundle) -> bool:
    with TemporaryDirectory() as directory:
        store, head, _authorization, binding = _seed_initialized_store(
            source=source,
            state_dir=directory,
            clean_shutdown=False,
        )
        root = source.root
        payload = head.to_dict()
        payload.update(
            {
                "active_head_sha256": "",
                "self_state_record_id": root.self_state_record_id,
                "self_state_sha256": root.self_state_sha256,
                "self_state_version": root.self_state_version,
                "lineage_generation": root.lineage_generation,
            }
        )
        digest_payload = dict(payload)
        digest_payload.pop("active_head_sha256", None)
        payload["active_head_sha256"] = sha256_payload(digest_payload)
        stale = ActiveSelfStateHeadRecord.from_dict(payload)
        shutdown = build_clean_shutdown_record(
            head=stale,
            session_id=stale.bound_session_id,
            process_instance_id=stale.bound_process_instance_id,
            operating_system_process_id=os.getpid(),
            identity_binding_id=binding.binding_id,
        )
        authorization = build_recovery_authorization(
            source=source,
            operation="recover_session",
            target_session_id="stale_child_session",
            target_process_instance_id="stale_child_process",
            expected_head=stale,
        )
        resolution = build_recovery_resolution(
            source=source,
            authorization=authorization,
            head=stale,
            active_head_candidate_count=1,
            shutdown_payloads=(shutdown.to_dict(),),
        )
        return (
            resolution.decision == "blocked_recovery"
            and resolution.stale_head_detected
            and "blocked_stale_active_head" in resolution.failure_reasons
        )


def _ambiguous_lineage_blocked(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
) -> bool:
    with TemporaryDirectory() as directory:
        copied_root = Path(directory) / "package_133_copy"
        copied_db = package_133_store_path(copied_root)
        copied_db.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(package_133_store_path(package_133_state_dir), copied_db)
        contract = load_authoritative_self_state_contract(ashl_root)
        parent = build_initial_self_state_record(
            contract=contract,
            origin_session_id="ambiguous_control_parent_session",
        )
        child, transition = build_successor_self_state_records(
            parent=parent,
            contract=contract,
            source_session_id="ambiguous_control_child_session",
        )
        validation = build_self_state_lineage_validation_record(
            parent=parent,
            child=child,
            transition=transition,
        )
        PersistentSelfStateStore(copied_root).append_lineage_chain(
            parent=parent,
            child=child,
            transition=transition,
            validation=validation,
        )
        return _rejects(
            lambda: load_package_133_source_read_only(copied_root),
            "ambiguous_self_state_lineage",
        )


def _cas_conflict_blocked(source: Package133SourceBundle) -> bool:
    with TemporaryDirectory() as directory:
        store, head, _authorization, binding = _seed_initialized_store(
            source=source,
            state_dir=directory,
            clean_shutdown=True,
        )
        authorization_one = _append_recovery_authorization(
            store, source, head, "cas_session_one", "cas_process_one"
        )
        authorization_two = _append_recovery_authorization(
            store, source, head, "cas_session_two", "cas_process_two"
        )
        _apply_recovery(
            store=store,
            source=source,
            head=head,
            authorization=authorization_one,
        )
        new_head_two = build_recovered_active_head(
            previous_head=head,
            authorization=authorization_two,
            session_id=authorization_two.target_session_id,
            process_instance_id=authorization_two.target_process_instance_id,
        )
        event_two = build_successful_cas_event(
            authorization=authorization_two,
            previous_head=head,
            new_head=new_head_two,
        )
        consumption_two = build_authorization_consumption(
            authorization=authorization_two,
            status="consumed_applied",
            failure_reason=None,
        )
        binding_two = build_identity_binding(
            source=source,
            head=new_head_two,
            binding_kind="fresh_process_recovery_binding",
            session_id=authorization_two.target_session_id,
            process_instance_id=authorization_two.target_process_instance_id,
            operating_system_process_id=os.getpid(),
            recovered_from_session_id=head.bound_session_id,
            authorization_id=authorization_two.authorization_id,
        )
        resolution_two = build_recovery_resolution(
            source=source,
            authorization=authorization_two,
            head=head,
            active_head_candidate_count=1,
            shutdown_payloads=store.list_payloads("persistent_session_shutdown_records"),
        )
        try:
            store.recover_active_head_atomic(
                authorization=authorization_two,
                expected_head=head,
                new_head=new_head_two,
                cas_event=event_two,
                consumption=consumption_two,
                identity_binding=binding_two,
                resolution=resolution_two,
            )
        except ActiveHeadCASConflict:
            return store.get_active_head().bound_session_id == authorization_one.target_session_id
    return False


def _dirty_shutdown_blocked(source: Package133SourceBundle) -> bool:
    with TemporaryDirectory() as directory:
        store, head, _authorization, _binding = _seed_initialized_store(
            source=source,
            state_dir=directory,
            clean_shutdown=False,
        )
        authorization = build_recovery_authorization(
            source=source,
            operation="recover_session",
            target_session_id="dirty_child_session",
            target_process_instance_id="dirty_child_process",
            expected_head=head,
        )
        resolution = build_recovery_resolution(
            source=source,
            authorization=authorization,
            head=head,
            active_head_candidate_count=1,
            shutdown_payloads=tuple(),
        )
        return (
            resolution.decision == "blocked_recovery"
            and not resolution.previous_clean_shutdown_verified
            and "blocked_previous_session_shutdown_unverified"
            in resolution.failure_reasons
        )


def _partial_write_rolled_back(source: Package133SourceBundle) -> bool:
    with TemporaryDirectory() as directory:
        store, head, _authorization, _binding = _seed_initialized_store(
            source=source,
            state_dir=directory,
            clean_shutdown=True,
        )
        authorization = _append_recovery_authorization(
            store, source, head, "partial_child_session", "partial_child_process"
        )
        counts_before = {
            table: store.count(table)
            for table in (
                "active_head_cas_events",
                "recovery_authorization_consumptions",
                "persistent_session_identity_bindings",
                "persistent_session_recovery_resolutions",
            )
        }
        new_head, event, consumption, binding, resolution = _recovery_records(
            store=store,
            source=source,
            head=head,
            authorization=authorization,
        )
        try:
            store.recover_active_head_atomic(
                authorization=authorization,
                expected_head=head,
                new_head=new_head,
                cas_event=event,
                consumption=consumption,
                identity_binding=binding,
                resolution=resolution,
                fault_injection="after_head_update_before_commit",
            )
        except RuntimeError as error:
            if "simulated_partial_write" not in str(error):
                return False
        else:
            return False
        counts_after = {table: store.count(table) for table in counts_before}
        persisted_head = store.get_active_head()
        return (
            persisted_head.active_head_sha256 == head.active_head_sha256
            and persisted_head.head_revision == head.head_revision
            and counts_before == counts_after
            and not store.authorization_consumed(authorization.authorization_id)
        )


def _forbidden_content_and_authority_rejected(source: Package133SourceBundle) -> bool:
    with TemporaryDirectory() as directory:
        _store, _head, _authorization, binding = _seed_initialized_store(
            source=source,
            state_dir=directory,
            clean_shutdown=False,
        )
        forbidden = (
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
        return all(
            _rejects(
                lambda name=name: replace(binding, **{name: True}),
                "forbidden content or authority",
            )
            for name in forbidden
        )


def _seed_initialized_store(
    *,
    source: Package133SourceBundle,
    state_dir: str | Path,
    clean_shutdown: bool,
) -> tuple[
    PersistentSessionRecoveryStore,
    ActiveSelfStateHeadRecord,
    PersistentSessionRecoveryAuthorization,
    Any,
]:
    store = PersistentSessionRecoveryStore(state_dir)
    authorization = build_recovery_authorization(
        source=source,
        operation="initialize_active_head",
        target_session_id="control_parent_session",
        target_process_instance_id="control_parent_process",
        expected_head=None,
    )
    store.append_record("persistent_session_recovery_authorizations", authorization)
    head = build_initial_active_head(
        source=source,
        session_id=authorization.target_session_id,
        process_instance_id=authorization.target_process_instance_id,
        authorization_id=authorization.authorization_id,
    )
    event = build_successful_cas_event(
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
        session_id=authorization.target_session_id,
        process_instance_id=authorization.target_process_instance_id,
        operating_system_process_id=os.getpid(),
        recovered_from_session_id=None,
        authorization_id=authorization.authorization_id,
    )
    store.initialize_active_head_atomic(
        authorization=authorization,
        active_head=head,
        cas_event=event,
        consumption=consumption,
        identity_binding=binding,
    )
    if clean_shutdown:
        shutdown = build_clean_shutdown_record(
            head=head,
            session_id=head.bound_session_id,
            process_instance_id=head.bound_process_instance_id,
            operating_system_process_id=os.getpid(),
            identity_binding_id=binding.binding_id,
        )
        store.append_record("persistent_session_shutdown_records", shutdown)
    return store, head, authorization, binding


def _append_recovery_authorization(
    store: PersistentSessionRecoveryStore,
    source: Package133SourceBundle,
    head: ActiveSelfStateHeadRecord,
    session_id: str,
    process_instance_id: str,
) -> PersistentSessionRecoveryAuthorization:
    authorization = build_recovery_authorization(
        source=source,
        operation="recover_session",
        target_session_id=session_id,
        target_process_instance_id=process_instance_id,
        expected_head=head,
    )
    store.append_record("persistent_session_recovery_authorizations", authorization)
    return authorization


def _recovery_records(
    *,
    store: PersistentSessionRecoveryStore,
    source: Package133SourceBundle,
    head: ActiveSelfStateHeadRecord,
    authorization: PersistentSessionRecoveryAuthorization,
) -> tuple[Any, Any, Any, Any, Any]:
    resolution = build_recovery_resolution(
        source=source,
        authorization=authorization,
        head=head,
        active_head_candidate_count=1,
        shutdown_payloads=store.list_payloads("persistent_session_shutdown_records"),
    )
    new_head = build_recovered_active_head(
        previous_head=head,
        authorization=authorization,
        session_id=authorization.target_session_id,
        process_instance_id=authorization.target_process_instance_id,
    )
    event = build_successful_cas_event(
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
        session_id=authorization.target_session_id,
        process_instance_id=authorization.target_process_instance_id,
        operating_system_process_id=os.getpid(),
        recovered_from_session_id=head.bound_session_id,
        authorization_id=authorization.authorization_id,
    )
    return new_head, event, consumption, binding, resolution


def _apply_recovery(
    *,
    store: PersistentSessionRecoveryStore,
    source: Package133SourceBundle,
    head: ActiveSelfStateHeadRecord,
    authorization: PersistentSessionRecoveryAuthorization,
) -> ActiveSelfStateHeadRecord:
    new_head, event, consumption, binding, resolution = _recovery_records(
        store=store,
        source=source,
        head=head,
        authorization=authorization,
    )
    store.recover_active_head_atomic(
        authorization=authorization,
        expected_head=head,
        new_head=new_head,
        cas_event=event,
        consumption=consumption,
        identity_binding=binding,
        resolution=resolution,
    )
    return new_head


def _rejects(call: Callable[[], object], expected_fragment: str) -> bool:
    try:
        call()
    except (KeyError, RuntimeError, TypeError, ValueError) as error:
        return expected_fragment in str(error)
    return False
