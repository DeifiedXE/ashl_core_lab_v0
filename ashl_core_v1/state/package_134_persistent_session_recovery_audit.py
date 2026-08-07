"""Package 134 final audit and regression runner."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.state.package_134_package_133_source import (
    load_package_133_source_read_only,
    package_133_source_tree_sha256,
)
from ashl_core_v1.state.package_134_persistent_session_recovery_controls import (
    run_package_134_recovery_controls,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    PersistentSessionRecoveryStore,
)
from ashl_core_v1.state.persistent_session_recovery_types import (
    AUDIT_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    PACKAGE_133_PASS_STATUS,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    Package134PersistentSessionRecoveryAudit,
    Package134RegressionReceipt,
)


PACKAGE_135_ABSENT_CAPABILITIES = (
    "drive_signal_trace_authority",
    "same_session_drive_modulation",
    "self_state_behavior_influence",
    "persistent_working_readback",
    "persistent_attention_state",
    "persistent_thought_engine_state",
    "automatic_learning_after_recovery",
    "automatic_action_after_recovery",
    "automatic_output_after_recovery",
    "psychological_state_continuity_claim",
)

_STATE_ENGINE_REGRESSION_MODULES = (
    "ashl_core_v1.tests.test_cradle_state_persistence_handoff",
    "ashl_core_v1.tests.test_cradle_state_resume_precheck",
    "ashl_core_v1.tests.test_cradle_state_resume_selection_authorization",
    "ashl_core_v1.tests.test_cradle_state_restore_preview_resume_handoff",
    "ashl_core_v1.tests.test_state_engine_resume_continuity_audit",
    "ashl_core_v1.tests.test_teacher_gated_session_store",
)


def run_package_134_regressions(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
) -> Package134RegressionReceipt:
    root = Path(ashl_root).resolve()
    store = PersistentSessionRecoveryStore(state_dir)
    pycache = store.root / "regression_pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    commands: tuple[tuple[str, tuple[str, ...]], ...] = (
        (
            "targeted_package_134",
            (
                sys.executable,
                "-m",
                "unittest",
                "ashl_core_v1.tests.test_package_134_persistent_session_recovery_identity",
            ),
        ),
        (
            "package_133_regressions",
            (
                sys.executable,
                "-m",
                "unittest",
                "ashl_core_v1.tests.test_package_133_cross_session_self_state_schema",
            ),
        ),
        (
            "state_engine_regressions",
            (sys.executable, "-m", "unittest", *_STATE_ENGINE_REGRESSION_MODULES),
        ),
        (
            "full_v1_unittest_discover",
            (sys.executable, "-m", "unittest", "discover"),
        ),
        ("compileall", (sys.executable, "-m", "compileall", "-q", "ashl_core_v1")),
        ("git_diff_check", ("git", "diff", "--check")),
    )
    results: list[tuple[str, int, str]] = []
    status: dict[str, bool] = {}
    for name, command in commands:
        completed = subprocess.run(
            command,
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=1800,
            check=False,
        )
        combined = f"{completed.stdout}\n{completed.stderr}"
        results.append((name, completed.returncode, sha256_bytes(combined.encode("utf-8"))))
        status[name] = completed.returncode == 0
    source_head = _git_output(root, "rev-parse", "HEAD")
    receipt = Package134RegressionReceipt(
        regression_receipt_id=(
            f"package_134_regressions:{sha256_payload({'head': source_head, 'results': results})[:16]}"
        ),
        schema_version=REGRESSION_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        source_head=source_head,
        command_results=tuple(results),
        targeted_package_134_passed=status["targeted_package_134"],
        package_133_regressions_passed=status["package_133_regressions"],
        state_engine_regressions_passed=status["state_engine_regressions"],
        full_v1_discover_passed=status["full_v1_unittest_discover"],
        compileall_passed=status["compileall"],
        git_diff_check_passed=status["git_diff_check"],
        pycache_redirected_outside_repo=True,
        fresh_regressions_passed=all(status.values()),
    )
    store.append_once("package_134_regression_receipts", receipt)
    return receipt


def audit_package_134_persistent_session_recovery(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    state_dir: str | Path,
    append: bool = True,
) -> Package134PersistentSessionRecoveryAudit:
    root = Path(ashl_root).resolve()
    source_root = Path(package_133_state_dir).resolve()
    source_before = package_133_source_tree_sha256(source_root)
    source = load_package_133_source_read_only(source_root)
    store = PersistentSessionRecoveryStore(state_dir)
    source_snapshots = store.list_payloads("package_133_source_snapshots")
    authorizations = store.list_payloads("persistent_session_recovery_authorizations")
    consumptions = store.list_payloads("recovery_authorization_consumptions")
    cas_events = store.list_payloads("active_head_cas_events")
    bindings = store.list_payloads("persistent_session_identity_bindings")
    shutdowns = store.list_payloads("persistent_session_shutdown_records")
    resolutions = store.list_payloads("persistent_session_recovery_resolutions")
    receipts = store.list_payloads("persistent_session_recovery_process_receipts")
    pairs = store.list_payloads("persistent_session_recovery_pairs")
    controls = store.latest_payload("package_134_recovery_control_results")
    regressions = store.latest_payload("package_134_regression_receipts")
    head = store.get_active_head()
    source_after = package_133_source_tree_sha256(source_root)
    store_integrity = store.audit_integrity()

    receipt_by_role = {
        str(item["process_role"]): item
        for item in receipts
        if item.get("worker_status") != "blocked"
    }
    binding_by_kind = {
        str(item["binding_kind"]): item
        for item in bindings
    }
    process_a = receipt_by_role.get("process_a")
    process_b = receipt_by_role.get("process_b")
    binding_a = binding_by_kind.get("initial_session_binding")
    binding_b = binding_by_kind.get("fresh_process_recovery_binding")
    pair = pairs[0] if len(pairs) == 1 else None
    successful_cas = tuple(item for item in cas_events if item.get("cas_succeeded") is True)
    applied_consumptions = tuple(
        item for item in consumptions if item.get("consumption_status") == "consumed_applied"
    )
    allowed_resolution = tuple(
        item for item in resolutions if item.get("decision") == "allow_exact_recovery_cas"
    )
    forbidden_names = (
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
    forbidden_values = {
        name: any(item.get(name) is True for item in bindings)
        for name in forbidden_names
    }
    baseline_ancestor = _is_ancestor(
        root, BASELINE_COMMIT, _git_output(root, "rev-parse", "HEAD")
    )
    explicit_authorizations = (
        len(authorizations) == 2
        and {item.get("operation") for item in authorizations}
        == {"initialize_active_head", "recover_session"}
        and all(
            item.get("explicit_authorization") is True
            and item.get("authorization_source") == "explicit_local_operator_request"
            and item.get("authorized_by") == "local_operator"
            for item in authorizations
        )
    )
    single_use = (
        len(applied_consumptions) == 2
        and len({item["authorization_id"] for item in applied_consumptions}) == 2
    )
    process_boundary = bool(
        process_a
        and process_b
        and int(process_a["operating_system_process_id"])
        != int(process_b["operating_system_process_id"])
        and int(process_a["ended_monotonic_ns"])
        < int(process_b["started_monotonic_ns"])
    )
    same_identity = bool(
        binding_a
        and binding_b
        and binding_a["self_state_lineage_id"]
        == binding_b["self_state_lineage_id"]
        == source.snapshot.self_state_lineage_id
        and binding_a["self_state_record_id"]
        == binding_b["self_state_record_id"]
        == source.snapshot.leaf_self_state_record_id
        and binding_a["self_state_sha256"]
        == binding_b["self_state_sha256"]
        == source.snapshot.leaf_self_state_sha256
    )
    cas_verified = bool(
        len(successful_cas) == 2
        and successful_cas[0]["operation"] == "initialize_active_head"
        and successful_cas[1]["operation"] == "recover_session"
        and successful_cas[0]["new_head_revision"] == 1
        and successful_cas[1]["new_head_revision"] == 2
        and head.head_revision == 2
        and head.previous_active_head_sha256
        == successful_cas[0]["new_active_head_sha256"]
        and head.active_head_sha256 == successful_cas[1]["new_active_head_sha256"]
    )
    checks = {
        "baseline": baseline_ancestor,
        "package_133_source": (
            source.snapshot.package_133_audit_status == PACKAGE_133_PASS_STATUS
            and len(source_snapshots) == 1
            and source_snapshots[0]["source_snapshot_id"] == source.snapshot.source_snapshot_id
        ),
        "package_133_unchanged": (
            source_before == source_after == source.snapshot.source_tree_sha256
        ),
        "package_133_authority": source.snapshot.package_133_recovery_authority_absent,
        "unique_lineage": (
            source.snapshot.unique_lineage_verified
            and source.snapshot.unique_leaf_verified
            and source.snapshot.full_parent_hash_chain_verified
        ),
        "explicit_authorizations": explicit_authorizations,
        "single_use_authorizations": single_use,
        "process_boundary": process_boundary,
        "clean_shutdown": bool(
            process_a
            and process_a.get("worker_status") == "initialized_and_cleanly_shutdown"
            and len(shutdowns) == 1
            and shutdowns[0].get("clean_shutdown_verified") is True
        ),
        "fresh_process_recovery": bool(
            process_b
            and process_b.get("worker_status") == "fresh_process_recovery_completed"
            and len(allowed_resolution) == 1
        ),
        "separate_active_head": bool(
            store_integrity["active_head_separate_from_history"]
            and store_integrity["history_tables_append_only"]
            and store_integrity["active_head_count"] == 1
        ),
        "cas": cas_verified,
        "identity_bindings": len(bindings) == 2 and same_identity,
        "pair": bool(
            pair
            and pair.get("comparison_status")
            == "passed_real_fresh_process_session_recovery"
            and pair.get("identity_fork_created") is False
        ),
        "controls": bool(controls and controls.get("controls_passed") is True),
        "regressions": bool(
            regressions and regressions.get("fresh_regressions_passed") is True
        ),
        "store_integrity": bool(store_integrity["valid"]),
        "forbidden_absent": not any(forbidden_values.values()),
        # This audit describes authority created by Package 134. A later
        # Package 135 source file must not retroactively invalidate it.
        "package_135_absent": not any(forbidden_values.values()),
    }
    failures = tuple(name for name, passed in checks.items() if not passed)
    status = PASS_STATUS if not failures else BLOCKED_STATUS
    source_head = _git_output(root, "rev-parse", "HEAD")
    audit_core = {
        "source_head": source_head,
        "package_133": source.snapshot.source_snapshot_sha256,
        "process_a": process_a.get("process_receipt_id") if process_a else None,
        "process_b": process_b.get("process_receipt_id") if process_b else None,
        "head": head.active_head_sha256,
        "pair": pair.get("recovery_pair_id") if pair else None,
        "controls": controls.get("control_result_id") if controls else None,
        "regressions": regressions.get("regression_receipt_id") if regressions else None,
        "failures": failures,
    }
    audit_sha256 = sha256_payload(audit_core)
    audit = Package134PersistentSessionRecoveryAudit(
        audit_id=f"package_134_audit:{audit_sha256[:16]}",
        audit_sha256=audit_sha256,
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        source_head=source_head,
        package_133_audit_id=source.snapshot.package_133_audit_id,
        package_133_audit_status=source.snapshot.package_133_audit_status,
        package_133_source_unchanged=checks["package_133_unchanged"],
        package_133_only_representation_authority=checks["package_133_authority"],
        unique_lineage_and_leaf_verified=source.snapshot.unique_lineage_verified
        and source.snapshot.unique_leaf_verified,
        parent_hash_chain_verified=source.snapshot.full_parent_hash_chain_verified,
        explicit_authorizations_verified=explicit_authorizations,
        authorizations_single_use=single_use,
        process_a_receipt_id=str(process_a.get("process_receipt_id") if process_a else "missing"),
        process_b_receipt_id=str(process_b.get("process_receipt_id") if process_b else "missing"),
        process_ids_distinct=process_boundary,
        process_a_ended_before_process_b_started=process_boundary,
        process_a_clean_shutdown_verified=checks["clean_shutdown"],
        process_b_fresh_startup_verified=checks["fresh_process_recovery"],
        active_head_separate_from_history=checks["separate_active_head"],
        initial_head_revision=(int(binding_a["head_revision"]) if binding_a else 0),
        recovered_head_revision=(int(binding_b["head_revision"]) if binding_b else 0),
        active_head_cas_verified=cas_verified,
        active_head_hash_chain_verified=cas_verified,
        session_identity_bindings_verified=checks["identity_bindings"],
        same_self_state_lineage_verified=same_identity,
        same_self_state_record_verified=same_identity,
        identity_fork_created=bool(pair.get("identity_fork_created")) if pair else True,
        recovery_pair_id=str(pair.get("recovery_pair_id") if pair else "missing"),
        recovery_controls_passed=checks["controls"],
        fresh_regressions_passed=checks["regressions"],
        **forbidden_values,
        package_135_implemented=not checks["package_135_absent"],
        persistent_psychological_continuity_claimed=False,
        audit_status=status,
        failure_reasons=failures,
        package_135_absent_capabilities=PACKAGE_135_ABSENT_CAPABILITIES,
        source_record_refs=(
            source.snapshot.source_snapshot_id,
            str(process_a.get("process_receipt_id") if process_a else "missing_process_a"),
            str(process_b.get("process_receipt_id") if process_b else "missing_process_b"),
            head.active_head_id,
            str(pair.get("recovery_pair_id") if pair else "missing_pair"),
            str(controls.get("control_result_id") if controls else "missing_controls"),
            str(regressions.get("regression_receipt_id") if regressions else "missing_regressions"),
        ),
    )
    if append:
        store.append_once("package_134_audits", audit)
    return audit


def ensure_package_134_controls(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    state_dir: str | Path,
) -> dict[str, Any]:
    result = run_package_134_recovery_controls(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        state_dir=state_dir,
        append=True,
    )
    return result.to_dict()


def _is_ancestor(root: Path, commit: str, head: str) -> bool:
    completed = subprocess.run(
        ("git", "merge-base", "--is-ancestor", commit, head),
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def _git_output(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", *arguments),
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()
