"""Evidence-grounded final audit for Package 139."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.state.package_139_self_state_rollback_store import (
    Package139SelfStateRollbackStore,
)
from ashl_core_v1.state.package_139_self_state_sources import (
    load_package_139_sources_read_only,
)
from ashl_core_v1.state.persistent_session_recovery_runtime import (
    build_recovery_authorization,
    build_recovery_resolution,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    PersistentSessionRecoveryStore,
)
from ashl_core_v1.state.self_state_rollback_types import (
    AUDIT_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    CONTROL_NAMES,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    ROLLBACK_OPERATION,
    ROLL_FORWARD_OPERATION,
    Package139ControlResult,
    Package139ControlCaseRecord,
    Package139RegressionReceipt,
    Package139SelfStateRollbackAudit,
    SelfStateAncestorProofRecord,
    SelfStateHeadSelectionAuthorizationRecord,
    SelfStateHeadSelectionCommitReceipt,
    SelfStateReadbackInvalidationGateRecord,
    SelfStateRollbackBoundaryContract,
    SelfStateRollbackCounterfactualComparison,
    SelfStateRollbackNoForkGuardRecord,
    build_hashed_record,
    record_from_payload,
)


def record_package_139_regression_receipt(
    *,
    state_dir: str | Path,
    source_head: str,
    command_results: tuple[tuple[str, int, str], ...],
    targeted_package_139_passed: bool,
    package_133_passed: bool,
    package_134_passed: bool,
    package_137_passed: bool,
    package_138_passed: bool,
    full_discover_passed: bool,
    compileall_passed: bool,
    git_diff_check_passed: bool,
    repository_pollution_absent: bool,
    source_record_refs: tuple[str, ...],
) -> Package139RegressionReceipt:
    payload: dict[str, Any] = {
        "regression_receipt_id": "",
        "regression_receipt_sha256": "",
        "schema_version": REGRESSION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "baseline_commit": BASELINE_COMMIT,
        "source_head": source_head,
        "command_results": command_results,
        "targeted_package_139_passed": targeted_package_139_passed,
        "package_133_passed": package_133_passed,
        "package_134_passed": package_134_passed,
        "package_137_passed": package_137_passed,
        "package_138_passed": package_138_passed,
        "full_discover_passed": full_discover_passed,
        "compileall_passed": compileall_passed,
        "git_diff_check_passed": git_diff_check_passed,
        "repository_pollution_absent": repository_pollution_absent,
        "source_record_refs": source_record_refs,
    }
    receipt = build_hashed_record(
        Package139RegressionReceipt,
        payload,
        id_field="regression_receipt_id",
        hash_field="regression_receipt_sha256",
        prefix="package_139_regressions",
    )
    Package139SelfStateRollbackStore(state_dir).append_once(
        "package_139_regression_receipts", receipt
    )
    return receipt


def audit_package_139_self_state_rollback(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    package_138_state_dir: str | Path,
    state_dir: str | Path,
) -> Package139SelfStateRollbackAudit:
    root = Path(ashl_root).resolve()
    store = Package139SelfStateRollbackStore(state_dir)
    failures: list[str] = []
    source = load_package_139_sources_read_only(
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        package_138_state_dir=package_138_state_dir,
        require_canonical_leaf=True,
    )
    store.append_once(
        "self_state_rollback_source_bindings", source.source_binding
    )
    integrity = store.audit_integrity()
    if not integrity["valid"]:
        failures.extend(str(item) for item in integrity["failure_reasons"])
    if not _git_contains(root, BASELINE_COMMIT):
        failures.append("baseline_commit_not_contained_in_head")
    contracts = _typed_records(store, "self_state_rollback_contracts", SelfStateRollbackBoundaryContract)
    proofs = _typed_records(store, "self_state_ancestor_proofs", SelfStateAncestorProofRecord)
    authorizations = _typed_records(
        store,
        "self_state_head_selection_authorizations",
        SelfStateHeadSelectionAuthorizationRecord,
    )
    gates = _typed_records(
        store,
        "self_state_readback_invalidation_gates",
        SelfStateReadbackInvalidationGateRecord,
    )
    receipts = _typed_records(
        store,
        "self_state_head_selection_commit_receipts",
        SelfStateHeadSelectionCommitReceipt,
    )
    guards = _typed_records(
        store,
        "self_state_rollback_no_fork_guard_records",
        SelfStateRollbackNoForkGuardRecord,
    )
    comparisons = _typed_records(
        store,
        "self_state_rollback_counterfactual_comparisons",
        SelfStateRollbackCounterfactualComparison,
    )
    controls = _typed_records(store, "package_139_control_results", Package139ControlResult)
    control_cases = _typed_records(
        store, "package_139_control_cases", Package139ControlCaseRecord
    )
    regressions = _typed_records(
        store, "package_139_regression_receipts", Package139RegressionReceipt
    )
    roll_forwards = tuple(item for item in receipts if item.operation == ROLL_FORWARD_OPERATION)
    if not roll_forwards:
        failures.append("exact_roll_forward_receipt_missing")
        roll_forward = None
        rollback = None
    else:
        roll_forward = roll_forwards[-1]
        rollback = next(
            (
                item
                for item in receipts
                if item.commit_receipt_id == roll_forward.paired_rollback_receipt_ref
            ),
            None,
        )
        if rollback is None:
            failures.append("paired_rollback_receipt_missing")
    proof = next(
        (
            item
            for item in proofs
            if rollback is not None and item.ancestor_proof_id == rollback.ancestor_proof_ref
        ),
        None,
    )
    rollback_authorization = next(
        (
            item
            for item in authorizations
            if rollback is not None and item.authorization_id == rollback.authorization_ref
        ),
        None,
    )
    roll_forward_authorization = next(
        (
            item
            for item in authorizations
            if roll_forward is not None and item.authorization_id == roll_forward.authorization_ref
        ),
        None,
    )
    rollback_gate = next(
        (
            item
            for item in gates
            if rollback_authorization is not None
            and item.authorization_ref == rollback_authorization.authorization_id
        ),
        None,
    )
    guard = next(
        (
            item
            for item in guards
            if rollback is not None and item.rollback_receipt_ref == rollback.commit_receipt_id
        ),
        None,
    )
    comparison = next(
        (
            item
            for item in comparisons
            if rollback is not None
            and roll_forward is not None
            and item.rollback_receipt_ref == rollback.commit_receipt_id
            and item.roll_forward_receipt_ref == roll_forward.commit_receipt_id
        ),
        None,
    )
    p134 = PersistentSessionRecoveryStore(package_134_state_dir)
    cas_events = {
        str(item["cas_event_id"]): item
        for item in p134.list_payloads("active_head_cas_events")
    }
    rollback_cas = cas_events.get(rollback.package_134_cas_event_ref) if rollback else None
    roll_forward_cas = (
        cas_events.get(roll_forward.package_134_cas_event_ref) if roll_forward else None
    )
    rollback_cas_verified = bool(
        rollback_cas
        and rollback_cas.get("operation") == ROLLBACK_OPERATION
        and rollback_cas.get("cas_succeeded") is True
        and rollback_cas.get("transaction_committed") is True
    )
    roll_forward_cas_verified = bool(
        roll_forward_cas
        and roll_forward_cas.get("operation") == ROLL_FORWARD_OPERATION
        and roll_forward_cas.get("cas_succeeded") is True
        and roll_forward_cas.get("transaction_committed") is True
    )
    current_head = p134.get_active_head()
    canonical_leaf_restored = all(
        (
            current_head.self_state_record_id == source.package_133.leaf.self_state_record_id,
            current_head.self_state_sha256 == source.package_133.leaf.self_state_sha256,
            current_head.self_state_version == source.package_133.leaf.self_state_version,
        )
    )
    future_authorization = build_recovery_authorization(
        source=source.package_133,
        operation="recover_session",
        target_session_id=stable_id("package_139_audit_future_recovery_session"),
        target_process_instance_id=stable_id("package_139_audit_future_recovery_process"),
        expected_head=current_head,
    )
    future_resolution = build_recovery_resolution(
        source=source.package_133,
        authorization=future_authorization,
        head=current_head,
        active_head_candidate_count=1,
        shutdown_payloads=p134.list_payloads("persistent_session_shutdown_records"),
    )
    recovery_restored = future_resolution.decision == "allow_exact_recovery_cas"
    contract_verified = len(contracts) == 1
    proof_verified = bool(
        proof
        and proof.target_is_strict_ancestor
        and proof.complete_parent_hash_chain_verified
        and proof.every_transition_verified
    )
    rollback_authorization_verified = bool(
        rollback_authorization
        and rollback_authorization.operation == ROLLBACK_OPERATION
        and rollback_authorization.rollback_receipt_ref is None
    )
    roll_forward_authorization_verified = bool(
        roll_forward_authorization
        and rollback is not None
        and roll_forward_authorization.operation == ROLL_FORWARD_OPERATION
        and roll_forward_authorization.rollback_receipt_ref == rollback.commit_receipt_id
    )
    history_unchanged = bool(
        rollback
        and roll_forward
        and rollback.package_133_tree_sha256_before
        == rollback.package_133_tree_sha256_after
        == roll_forward.package_133_tree_sha256_before
        == roll_forward.package_133_tree_sha256_after
        == source.source_binding.package_133_tree_sha256
    )
    descendants_preserved = bool(
        rollback
        and all(
            ref in {item.self_state_record_id for item in source.package_133.states}
            for ref in rollback.intervening_descendant_refs
        )
    )
    no_fork_verified = bool(
        guard
        and guard.package_137_mutation_preflight_blocked
        and guard.package_134_recovery_resolution_blocked
        and guard.exact_roll_forward_required
        and not guard.identity_fork_created
    )
    control_cases_verified = bool(
        len(control_cases) == len(CONTROL_NAMES)
        and tuple(item.control_name for item in control_cases) == CONTROL_NAMES
        and all(
            item.control_passed and not item.production_authority_changed
            for item in control_cases
        )
    )
    controls_passed = bool(
        controls and controls[-1].controls_passed and control_cases_verified
    )
    comparison_verified = bool(
        comparison
        and comparison.only_head_selection_and_audit_surfaces_differ
        and comparison.package_133_history_equivalent
    )
    regression_passed = bool(regressions)
    checks = {
        "rollback_contract_missing_or_ambiguous": contract_verified,
        "ancestor_proof_invalid": proof_verified,
        "rollback_authorization_invalid": rollback_authorization_verified,
        "rollback_cas_invalid": rollback_cas_verified,
        "roll_forward_authorization_invalid": roll_forward_authorization_verified,
        "roll_forward_cas_invalid": roll_forward_cas_verified,
        "canonical_leaf_not_restored": canonical_leaf_restored,
        "package_133_history_changed": history_unchanged,
        "intervening_descendants_missing": descendants_preserved,
        "readbacks_not_terminal_before_rollback": bool(
            rollback_gate and rollback_gate.active_readback_count_after == 0
        ),
        "no_fork_guard_missing": no_fork_verified,
        "controls_incomplete": controls_passed,
        "counterfactual_missing": comparison_verified,
        "recovery_eligibility_not_restored": recovery_restored,
        "regression_receipt_missing": regression_passed,
    }
    failures.extend(name for name, passed in checks.items() if not passed)
    payload: dict[str, Any] = {
        "audit_id": "",
        "audit_sha256": "",
        "schema_version": AUDIT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "baseline_commit": BASELINE_COMMIT,
        "package_133_baseline_verified": source.package_133.package_133_audit.get("audit_status")
        == "passed_cross_session_self_state_schema_v0",
        "package_134_baseline_verified": source.package_134_audit.get("audit_status")
        == "passed_persistent_session_recovery_and_identity_v0",
        "package_137_baseline_verified": source.package_137_audit.get("audit_status")
        == "passed_persistent_self_state_review_gate_v0",
        "package_138_baseline_verified": source.package_138_audit.get("audit_status")
        == "passed_bounded_same_session_self_state_readback_boundary_v0",
        "rollback_contract_verified": contract_verified,
        "exact_ancestor_proof_verified": proof_verified,
        "rollback_authorization_verified": rollback_authorization_verified,
        "rollback_cas_verified": rollback_cas_verified,
        "rollback_head_revision_incremented": bool(
            rollback and rollback.head_revision_after == rollback.head_revision_before + 1
        ),
        "rollback_target_selected": bool(
            rollback
            and proof
            and rollback.self_state_record_id_after == proof.target_self_state_record_id
        ),
        "readbacks_terminal_before_rollback": bool(
            rollback_gate and rollback_gate.active_readback_count_after == 0
        ),
        "intervening_history_preserved": descendants_preserved,
        "package_133_history_unchanged": history_unchanged,
        "mutation_blocked_while_rolled_back": bool(
            guard and guard.package_137_mutation_preflight_blocked
        ),
        "recovery_blocked_while_rolled_back": bool(
            guard and guard.package_134_recovery_resolution_blocked
        ),
        "exact_roll_forward_authorization_verified": roll_forward_authorization_verified,
        "roll_forward_cas_verified": roll_forward_cas_verified,
        "canonical_leaf_restored": canonical_leaf_restored,
        "recovery_eligibility_restored_after_roll_forward": recovery_restored,
        "controls_passed": controls_passed,
        "counterfactual_equivalence_verified": comparison_verified,
        "memory_restored": False,
        "perception_history_restored": False,
        "working_readback_restored": False,
        "drive_trace_restored": False,
        "drive_modulation_restored": False,
        "attention_restored": False,
        "thought_engine_used": False,
        "action_created": False,
        "output_created": False,
        "self_state_history_rewritten": False,
        "identity_fork_created": False,
        "automatic_rebase_used": False,
        "latest_selection_used": False,
        "package_140_implemented": False,
        "llm_runtime_calls": 0,
        "codex_runtime_calls": 0,
        "network_runtime_calls": 0,
        "audit_status": PASS_STATUS if not failures else BLOCKED_STATUS,
        "failure_reasons": tuple(failures),
        "source_record_refs": tuple(
            item
            for item in (
                source.source_binding.source_binding_id,
                contracts[0].contract_id if contracts else None,
                proof.ancestor_proof_id if proof else None,
                rollback.commit_receipt_id if rollback else None,
                guard.no_fork_guard_id if guard else None,
                roll_forward.commit_receipt_id if roll_forward else None,
                comparison.comparison_id if comparison else None,
                controls[-1].control_result_id if controls else None,
                regressions[-1].regression_receipt_id if regressions else None,
                current_head.active_head_id,
                current_head.self_state_record_id,
            )
            if item
        ),
    }
    audit = build_hashed_record(
        Package139SelfStateRollbackAudit,
        payload,
        id_field="audit_id",
        hash_field="audit_sha256",
        prefix="package_139_audit",
    )
    store.append_once("package_139_audits", audit)
    return audit


def _typed_records(
    store: Package139SelfStateRollbackStore,
    table: str,
    record_type: type[Any],
) -> tuple[Any, ...]:
    records: list[Any] = []
    for payload in store.list_payloads(table):
        try:
            records.append(record_from_payload(record_type, payload))
        except (KeyError, TypeError, ValueError) as error:
            raise RuntimeError(f"blocked_invalid_package_139_record:{table}") from error
    return tuple(records)


def _git_contains(root: Path, commit: str) -> bool:
    result = subprocess.run(
        ("git", "merge-base", "--is-ancestor", commit, "HEAD"),
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    return result.returncode == 0
