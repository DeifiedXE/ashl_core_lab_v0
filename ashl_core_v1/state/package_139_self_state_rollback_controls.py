"""Executable negative and no-fork controls for Package 139."""

from __future__ import annotations

import gc
import os
import shutil
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, stable_id, utc_now
from ashl_core_v1.state.package_134_package_133_source import (
    load_package_133_source_read_only,
)
from ashl_core_v1.state.package_139_self_state_rollback_store import (
    Package139SelfStateRollbackStore,
)
from ashl_core_v1.state.persistent_self_state_review_runtime import (
    preflight_self_state_review_gate,
)
from ashl_core_v1.state.persistent_self_state_store import package_133_store_path
from ashl_core_v1.state.persistent_session_recovery_runtime import (
    build_recovery_authorization,
    build_recovery_resolution,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    PersistentSessionRecoveryStore,
    package_134_store_path,
)
from ashl_core_v1.state.package_138_self_state_readback_store import (
    Package138SelfStateReadbackStore,
    package_138_store_path,
)
from ashl_core_v1.state.self_state_readback_types import BoundedSelfStateReadbackRecord
from ashl_core_v1.state.self_state_rollback_runtime import (
    authorize_exact_roll_forward,
    authorize_verified_ancestor_rollback,
    build_verified_ancestor_proof,
    commit_authorized_head_selection,
    reconcile_committed_head_selection,
    validate_ancestor_target_identity,
)
from ashl_core_v1.state.self_state_rollback_types import (
    AUTHORIZATION_SCHEMA_VERSION,
    CONTROL_CASE_SCHEMA_VERSION,
    CONTROL_NAMES,
    CONTROL_SCHEMA_VERSION,
    ROLL_FORWARD_OPERATION,
    Package139ControlCaseRecord,
    Package139ControlResult,
    SelfStateHeadSelectionAuthorizationRecord,
    build_hashed_record,
)


def run_package_139_self_state_rollback_controls(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    package_138_state_dir: str | Path,
    state_dir: str | Path,
) -> Package139ControlResult:
    outcomes: dict[str, bool] = {}
    source = load_package_133_source_read_only(package_133_state_dir)
    target_id = source.states[-2].self_state_record_id
    with TemporaryDirectory(
        prefix="ashl_package_139_controls_", ignore_cleanup_errors=True
    ) as temporary:
        temporary_root = Path(temporary)

        scenario = _clone_scenario(
            temporary_root, "stale", package_134_state_dir, package_138_state_dir
        )
        prepared = _prepare_rollback(
            ashl_root, package_133_state_dir, scenario[0], package_137_state_dir,
            scenario[1], scenario[2], target_id,
        )
        stale = commit_authorized_head_selection(
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=scenario[0],
            package_138_state_dir=scenario[1],
            state_dir=scenario[2],
            authorization_id=prepared[1].authorization_id,
            allow_self_state_head_selection=True,
            process_instance_id=prepared[2],
            evaluated_at_monotonic_ns=prepared[1].expires_at_monotonic_ns,
        )
        outcomes["stale_authorization_blocked"] = _blocked_unchanged(stale)

        scenario = _clone_scenario(
            temporary_root, "wrong_ancestor", package_134_state_dir, package_138_state_dir
        )
        try:
            build_verified_ancestor_proof(
                ashl_root=ashl_root,
                package_133_state_dir=package_133_state_dir,
                package_134_state_dir=scenario[0],
                package_137_state_dir=package_137_state_dir,
                package_138_state_dir=scenario[1],
                state_dir=scenario[2],
                target_self_state_record_id="persistent_self_state:not_authoritative",
            )
        except RuntimeError as error:
            outcomes["wrong_ancestor_blocked"] = "not_in_authoritative_lineage" in str(error)
        else:
            outcomes["wrong_ancestor_blocked"] = False

        try:
            validate_ancestor_target_identity(
                current=source.leaf,
                target=SimpleNamespace(
                    self_state_lineage_id="self_state_lineage:cross_lineage_control",
                    self_state_record_id=source.root.self_state_record_id,
                    self_state_version=source.root.self_state_version,
                ),
            )
        except RuntimeError as error:
            outcomes["cross_lineage_target_blocked"] = "cross_lineage" in str(error)
        else:
            outcomes["cross_lineage_target_blocked"] = False

        scenario = _clone_scenario(
            temporary_root, "cas_conflict", package_134_state_dir, package_138_state_dir
        )
        prepared = _prepare_rollback(
            ashl_root, package_133_state_dir, scenario[0], package_137_state_dir,
            scenario[1], scenario[2], target_id,
        )
        conflict = commit_authorized_head_selection(
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=scenario[0],
            package_138_state_dir=scenario[1],
            state_dir=scenario[2],
            authorization_id=prepared[1].authorization_id,
            allow_self_state_head_selection=True,
            process_instance_id=prepared[2],
            fault_injection="force_cas_conflict",
        )
        outcomes["cas_conflict_head_unchanged"] = _blocked_unchanged(conflict)

        corrupt_root = temporary_root / "corrupt_p133"
        corrupt_db = corrupt_root / "package_133_cross_session_self_state_schema_v0" / "package_133.sqlite3"
        corrupt_db.parent.mkdir(parents=True)
        shutil.copy2(package_133_store_path(package_133_state_dir), corrupt_db)
        with sqlite3.connect(corrupt_db) as connection:
            connection.execute(
                "UPDATE persistent_self_state_records SET payload_sha256 = ? WHERE row_id = 1",
                ("0" * 64,),
            )
            connection.commit()
        try:
            load_package_133_source_read_only(corrupt_root)
        except RuntimeError:
            outcomes["corrupt_history_blocked"] = True
        else:
            outcomes["corrupt_history_blocked"] = False
        gc.collect()

        scenario = _clone_scenario(
            temporary_root, "partial", package_134_state_dir, package_138_state_dir
        )
        prepared = _prepare_rollback(
            ashl_root, package_133_state_dir, scenario[0], package_137_state_dir,
            scenario[1], scenario[2], target_id,
        )
        partial = commit_authorized_head_selection(
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=scenario[0],
            package_138_state_dir=scenario[1],
            state_dir=scenario[2],
            authorization_id=prepared[1].authorization_id,
            allow_self_state_head_selection=True,
            process_instance_id=prepared[2],
            fault_injection="after_head_update_before_commit",
        )
        outcomes["partial_package_134_transaction_rolled_back"] = _blocked_unchanged(partial)

        scenario = _clone_scenario(
            temporary_root, "reconcile", package_134_state_dir, package_138_state_dir
        )
        prepared = _prepare_rollback(
            ashl_root, package_133_state_dir, scenario[0], package_137_state_dir,
            scenario[1], scenario[2], target_id,
        )
        try:
            commit_authorized_head_selection(
                package_133_state_dir=package_133_state_dir,
                package_134_state_dir=scenario[0],
                package_138_state_dir=scenario[1],
                state_dir=scenario[2],
                authorization_id=prepared[1].authorization_id,
                allow_self_state_head_selection=True,
                process_instance_id=prepared[2],
                fault_injection="after_package_134_cas_before_receipt",
            )
        except RuntimeError as error:
            receipt = reconcile_committed_head_selection(
                package_133_state_dir=package_133_state_dir,
                package_134_state_dir=scenario[0],
                state_dir=scenario[2],
                authorization_id=prepared[1].authorization_id,
            )
            outcomes["post_cas_receipt_failure_reconciled"] = (
                "post_cas_receipt_failure" in str(error)
                and receipt.rollback_or_roll_forward_status
                == "committed_verified_ancestor_rollback"
            )
        else:
            outcomes["post_cas_receipt_failure_reconciled"] = False

        scenario = _clone_scenario(
            temporary_root, "reuse", package_134_state_dir, package_138_state_dir
        )
        prepared = _prepare_rollback(
            ashl_root, package_133_state_dir, scenario[0], package_137_state_dir,
            scenario[1], scenario[2], target_id,
        )
        first = commit_authorized_head_selection(
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=scenario[0],
            package_138_state_dir=scenario[1],
            state_dir=scenario[2],
            authorization_id=prepared[1].authorization_id,
            allow_self_state_head_selection=True,
            process_instance_id=prepared[2],
        )
        head_after_first = PersistentSessionRecoveryStore(scenario[0]).get_active_head()
        second = commit_authorized_head_selection(
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=scenario[0],
            package_138_state_dir=scenario[1],
            state_dir=scenario[2],
            authorization_id=prepared[1].authorization_id,
            allow_self_state_head_selection=True,
            process_instance_id=prepared[2],
        )
        head_after_second = PersistentSessionRecoveryStore(scenario[0]).get_active_head()
        outcomes["rollback_authorization_reuse_blocked"] = (
            first["status"] == "committed_verified_ancestor_rollback"
            and second["status"] == "blocked_head_selection"
            and head_after_first == head_after_second
        )

        scenario = _clone_scenario(
            temporary_root, "readback_authority", package_134_state_dir, package_138_state_dir
        )
        readback_authorization = Package138SelfStateReadbackStore(scenario[1]).latest_payload(
            "self_state_readback_authorizations"
        )
        before = PersistentSessionRecoveryStore(scenario[0]).get_active_head()
        misuse = commit_authorized_head_selection(
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=scenario[0],
            package_138_state_dir=scenario[1],
            state_dir=scenario[2],
            authorization_id=str(readback_authorization["authorization_id"]),
            allow_self_state_head_selection=True,
            process_instance_id=stable_id("package_139_readback_misuse"),
        )
        after = PersistentSessionRecoveryStore(scenario[0]).get_active_head()
        outcomes["readback_authorization_not_rollback_authority"] = (
            misuse["status"] == "blocked_head_selection" and before == after
        )

        scenario = _clone_scenario(
            temporary_root, "active_readback", package_134_state_dir, package_138_state_dir
        )
        active_readback_id = _append_active_readback(scenario[0], scenario[1])
        prepared = _prepare_rollback(
            ashl_root, package_133_state_dir, scenario[0], package_137_state_dir,
            scenario[1], scenario[2], target_id,
        )
        invalidated = commit_authorized_head_selection(
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=scenario[0],
            package_138_state_dir=scenario[1],
            state_dir=scenario[2],
            authorization_id=prepared[1].authorization_id,
            allow_self_state_head_selection=True,
            process_instance_id=prepared[2],
        )
        terminal = Package138SelfStateReadbackStore(scenario[1]).terminal_lifecycle_for(
            active_readback_id
        )
        outcomes["active_readback_invalidated_before_cas"] = bool(
            invalidated["status"] == "committed_verified_ancestor_rollback"
            and terminal
            and terminal["lifecycle_kind"]
            == "invalidated_before_authorized_active_head_transition"
        )

        scenario = _clone_scenario(
            temporary_root, "no_fork", package_134_state_dir, package_138_state_dir
        )
        prepared = _prepare_rollback(
            ashl_root, package_133_state_dir, scenario[0], package_137_state_dir,
            scenario[1], scenario[2], target_id,
        )
        rollback = commit_authorized_head_selection(
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=scenario[0],
            package_138_state_dir=scenario[1],
            state_dir=scenario[2],
            authorization_id=prepared[1].authorization_id,
            allow_self_state_head_selection=True,
            process_instance_id=prepared[2],
        )
        outcomes["mutation_while_rolled_back_blocked"] = _mutation_blocked(
            ashl_root, package_133_state_dir, scenario[0], package_137_state_dir
        )
        outcomes["recovery_while_rolled_back_blocked"] = _recovery_blocked(
            package_133_state_dir, scenario[0]
        )
        exact_authorization = authorize_exact_roll_forward(
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=scenario[0],
            state_dir=scenario[2],
            rollback_receipt_id=rollback["receipt"].commit_receipt_id,
            target_session_id=stable_id("package_139_control_roll_forward_session"),
            target_process_instance_id=prepared[2],
        )
        root_state = source.root
        invalid_payload = exact_authorization.to_dict()
        invalid_payload.update(
            {
                "authorization_id": "",
                "authorization_sha256": "",
                "target_self_state_record_id": root_state.self_state_record_id,
                "target_self_state_sha256": root_state.self_state_sha256,
                "target_self_state_version": root_state.self_state_version,
            }
        )
        arbitrary = build_hashed_record(
            SelfStateHeadSelectionAuthorizationRecord,
            invalid_payload,
            id_field="authorization_id",
            hash_field="authorization_sha256",
            prefix="self_state_head_selection_authorization",
        )
        Package139SelfStateRollbackStore(scenario[2]).append_once(
            "self_state_head_selection_authorizations", arbitrary
        )
        arbitrary_result = commit_authorized_head_selection(
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=scenario[0],
            package_138_state_dir=scenario[1],
            state_dir=scenario[2],
            authorization_id=arbitrary.authorization_id,
            allow_self_state_head_selection=True,
            process_instance_id=prepared[2],
        )
        outcomes["arbitrary_roll_forward_blocked"] = _blocked_unchanged(arbitrary_result)
        exact_result = commit_authorized_head_selection(
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=scenario[0],
            package_138_state_dir=scenario[1],
            state_dir=scenario[2],
            authorization_id=exact_authorization.authorization_id,
            allow_self_state_head_selection=True,
            process_instance_id=prepared[2],
        )
        final_head = PersistentSessionRecoveryStore(scenario[0]).get_active_head()
        outcomes["exact_roll_forward_restores_canonical_leaf"] = (
            exact_result["status"]
            == "committed_exact_preserved_descendant_roll_forward"
            and final_head.self_state_record_id == source.leaf.self_state_record_id
            and final_head.self_state_sha256 == source.leaf.self_state_sha256
        )

    primary_store = Package139SelfStateRollbackStore(state_dir)
    case_records = tuple(
        _build_control_case(
            control_name=name,
            passed=outcomes.get(name) is True,
            source_record_refs=(
                source.snapshot.source_snapshot_id,
                source.leaf.self_state_record_id,
            ),
        )
        for name in CONTROL_NAMES
    )
    primary_store.append_group(
        tuple(("package_139_control_cases", item) for item in case_records)
    )
    passed = tuple(name for name in CONTROL_NAMES if outcomes.get(name) is True)
    failures = tuple(name for name in CONTROL_NAMES if outcomes.get(name) is not True)
    payload = {
        "control_result_id": "",
        "control_result_sha256": "",
        "schema_version": CONTROL_SCHEMA_VERSION,
        "created_at": utc_now(),
        "control_names": CONTROL_NAMES,
        "passed_control_names": passed,
        "passed_count": len(passed),
        "controls_passed": not failures,
        "failure_reasons": failures,
        "source_record_refs": tuple(item.control_case_id for item in case_records)
        + tuple(
            str(item["commit_receipt_id"])
            for item in primary_store.list_payloads(
                "self_state_head_selection_commit_receipts"
            )
        ),
    }
    result = build_hashed_record(
        Package139ControlResult,
        payload,
        id_field="control_result_id",
        hash_field="control_result_sha256",
        prefix="package_139_controls",
    )
    primary_store.append_once("package_139_control_results", result)
    return result


_CONTROL_OUTCOMES = {
    "stale_authorization_blocked": "expired exact authorization blocked with head unchanged",
    "wrong_ancestor_blocked": "non-authoritative target rejected before authorization",
    "cross_lineage_target_blocked": "cross-lineage target rejected",
    "cas_conflict_head_unchanged": "exact Package 134 CAS conflict left head unchanged",
    "corrupt_history_blocked": "corrupt Package 133 payload blocked source loading",
    "partial_package_134_transaction_rolled_back": "pre-commit Package 134 fault rolled back head transaction",
    "post_cas_receipt_failure_reconciled": "single committed CAS reconciled without a second CAS",
    "rollback_authorization_reuse_blocked": "consumed rollback authorization could not execute twice",
    "readback_authorization_not_rollback_authority": "Package 138 authorization could not authorize rollback",
    "active_readback_invalidated_before_cas": "active exact-head readback received terminal lifecycle before CAS",
    "mutation_while_rolled_back_blocked": "Package 137 mutation preflight blocked while ancestor selected",
    "recovery_while_rolled_back_blocked": "Package 134 recovery blocked while ancestor selected",
    "arbitrary_roll_forward_blocked": "unpreserved descendant target blocked",
    "exact_roll_forward_restores_canonical_leaf": "separately authorized exact preserved leaf restored",
}


def _build_control_case(
    *,
    control_name: str,
    passed: bool,
    source_record_refs: tuple[str, ...],
) -> Package139ControlCaseRecord:
    outcome = _CONTROL_OUTCOMES[control_name]
    payload = {
        "control_case_id": "",
        "control_case_sha256": "",
        "schema_version": CONTROL_CASE_SCHEMA_VERSION,
        "created_at": utc_now(),
        "control_name": control_name,
        "validator_executed": True,
        "isolated_authority_clone_used": True,
        "expected_outcome": outcome,
        "observed_outcome": outcome if passed else "validator outcome did not match",
        "control_passed": passed,
        "production_authority_changed": False,
        "control_status": (
            "passed_expected_control_outcome" if passed else "failed_control_outcome"
        ),
        "source_record_refs": source_record_refs,
    }
    return build_hashed_record(
        Package139ControlCaseRecord,
        payload,
        id_field="control_case_id",
        hash_field="control_case_sha256",
        prefix="package_139_control_case",
    )


def _clone_scenario(
    temporary_root: Path,
    name: str,
    package_134_state_dir: str | Path,
    package_138_state_dir: str | Path,
) -> tuple[Path, Path, Path]:
    root = temporary_root / name
    p134 = root / "p134"
    p138 = root / "p138"
    output = root / "p139"
    p134_db = package_134_store_path(p134)
    p138_db = package_138_store_path(p138)
    p134_db.parent.mkdir(parents=True)
    p138_db.parent.mkdir(parents=True)
    shutil.copy2(package_134_store_path(package_134_state_dir), p134_db)
    shutil.copy2(package_138_store_path(package_138_state_dir), p138_db)
    return p134, p138, output


def _prepare_rollback(
    ashl_root: str | Path,
    p133: str | Path,
    p134: str | Path,
    p137: str | Path,
    p138: str | Path,
    output: str | Path,
    target_id: str,
) -> tuple[Any, Any, str]:
    process = stable_id("package_139_control_process")
    proof = build_verified_ancestor_proof(
        ashl_root=ashl_root,
        package_133_state_dir=p133,
        package_134_state_dir=p134,
        package_137_state_dir=p137,
        package_138_state_dir=p138,
        state_dir=output,
        target_self_state_record_id=target_id,
    )
    authorization = authorize_verified_ancestor_rollback(
        ashl_root=ashl_root,
        package_133_state_dir=p133,
        package_134_state_dir=p134,
        package_137_state_dir=p137,
        package_138_state_dir=p138,
        state_dir=output,
        ancestor_proof_id=proof.ancestor_proof_id,
        target_session_id=stable_id("package_139_control_session"),
        target_process_instance_id=process,
    )
    return proof, authorization, process


def _blocked_unchanged(result: dict[str, Any]) -> bool:
    return bool(
        result.get("status") == "blocked_head_selection"
        and result.get("head_before") == result.get("head_after")
    )


def _mutation_blocked(
    ashl_root: str | Path,
    p133: str | Path,
    p134: str | Path,
    p137: str | Path,
) -> bool:
    try:
        preflight_self_state_review_gate(
            ashl_root=ashl_root,
            package_133_state_dir=p133,
            package_134_state_dir=p134,
            state_dir=p137,
        )
    except RuntimeError as error:
        return "blocked_cross_authority_partial_or_ambiguous_state" in str(error)
    return False


def _recovery_blocked(p133: str | Path, p134: str | Path) -> bool:
    source = load_package_133_source_read_only(p133)
    store = PersistentSessionRecoveryStore(p134)
    head = store.get_active_head()
    authorization = build_recovery_authorization(
        source=source,
        operation="recover_session",
        target_session_id=stable_id("package_139_control_recovery_session"),
        target_process_instance_id=stable_id("package_139_control_recovery_process"),
        expected_head=head,
    )
    resolution = build_recovery_resolution(
        source=source,
        authorization=authorization,
        head=head,
        active_head_candidate_count=1,
        shutdown_payloads=store.list_payloads("persistent_session_shutdown_records"),
    )
    return resolution.decision == "blocked_recovery" and resolution.stale_head_detected


def _append_active_readback(p134: str | Path, p138: str | Path) -> str:
    head = PersistentSessionRecoveryStore(p134).get_active_head()
    store = Package138SelfStateReadbackStore(p138)
    template = dict(store.latest_payload("bounded_self_state_readbacks") or {})
    if not template:
        raise RuntimeError("Package 139 active-readback control requires a Package 138 template")
    now = monotonic_ns()
    template.update(
        {
            "readback_id": "",
            "readback_sha256": "",
            "created_at": utc_now(),
            "authorization_ref": stable_id("package_139_control_readback_authorization"),
            "runtime_session_id": head.bound_session_id,
            "process_instance_id": head.bound_process_instance_id,
            "operating_system_process_id": os.getpid(),
            "active_head_id": head.active_head_id,
            "active_head_sha256": head.active_head_sha256,
            "head_revision": head.head_revision,
            "self_state_record_id": head.self_state_record_id,
            "self_state_sha256": head.self_state_sha256,
            "bound_at_monotonic_ns": now,
            "expires_at_monotonic_ns": now + 30_000_000_000,
            "source_record_refs": (
                head.active_head_id,
                head.self_state_record_id,
                "package_139_active_readback_control",
            ),
        }
    )
    for key, value in tuple(template.items()):
        if isinstance(value, list):
            template[key] = tuple(value)
    readback = build_hashed_record(
        BoundedSelfStateReadbackRecord,
        template,
        id_field="readback_id",
        hash_field="readback_sha256",
        prefix="bounded_self_state_readback",
    )
    store.append_once("bounded_self_state_readbacks", readback)
    return readback.readback_id
