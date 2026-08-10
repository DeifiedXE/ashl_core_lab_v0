"""Package 139 verified-ancestor rollback and exact roll-forward runtime."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, sha256_payload, stable_id, utc_now
from ashl_core_v1.state.package_134_package_133_source import (
    Package133SourceBundle,
    load_package_133_source_read_only,
    package_133_source_tree_sha256,
)
from ashl_core_v1.state.package_139_self_state_rollback_store import (
    Package139SelfStateRollbackStore,
)
from ashl_core_v1.state.package_139_self_state_sources import (
    Package139SourceBundle,
    load_package_139_sources_read_only,
)
from ashl_core_v1.state.persistent_self_state_lineage import (
    validate_persistent_self_state_lineage,
)
from ashl_core_v1.state.persistent_self_state_review_runtime import (
    preflight_self_state_review_gate,
)
from ashl_core_v1.state.persistent_self_state_schema import (
    PersistentSelfStateRecord,
    PersistentSelfStateTransitionRecord,
)
from ashl_core_v1.state.persistent_session_recovery_runtime import (
    build_clean_shutdown_record,
    build_identity_binding,
    build_recovery_authorization,
    build_recovery_resolution,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    ActiveHeadCASConflict,
    PersistentSessionRecoveryStore,
)
from ashl_core_v1.state.persistent_session_recovery_types import (
    ACTIVE_HEAD_AUTHORITY as PACKAGE_134_ACTIVE_HEAD_AUTHORITY,
    CAS_SCHEMA_VERSION,
    HEAD_SCHEMA_VERSION,
    REPRESENTATION_AUTHORITY,
    ActiveHeadCASEventRecord,
    ActiveSelfStateHeadRecord,
)
from ashl_core_v1.state.self_state_readback_runtime import (
    invalidate_readbacks_before_authorized_head_transition,
)
from ashl_core_v1.state.self_state_readback_types import (
    PASS_STATUS as PACKAGE_138_PASS_STATUS,
)
from ashl_core_v1.state.self_state_rollback_types import (
    ACTIVE_HEAD_AUTHORITY,
    AUTHORIZATION_SCHEMA_VERSION,
    BLOCKED_SCHEMA_VERSION,
    COMPARISON_SCHEMA_VERSION,
    CONSUMPTION_SCHEMA_VERSION,
    CONTRACT_SCHEMA_VERSION,
    HEAD_SELECTION_OPERATIONS,
    INTENT_SCHEMA_VERSION,
    INVALIDATION_SCHEMA_VERSION,
    MAXIMUM_AUTHORIZATION_LIFETIME_NS,
    NO_FORK_SCHEMA_VERSION,
    PROCESS_SCHEMA_VERSION,
    PROOF_SCHEMA_VERSION,
    READBACK_AUTHORITY,
    RECEIPT_SCHEMA_VERSION,
    REVIEW_GATE_AUTHORITY,
    ROLLBACK_AUTHORITY,
    ROLLBACK_OPERATION,
    ROLL_FORWARD_OPERATION,
    SELF_STATE_AUTHORITY,
    SelfStateAncestorProofRecord,
    Package139AuthoritySourceBindingRecord,
    SelfStateHeadSelectionAuthorizationConsumptionRecord,
    SelfStateHeadSelectionAuthorizationRecord,
    SelfStateHeadSelectionCommitIntentRecord,
    SelfStateHeadSelectionCommitReceipt,
    SelfStateReadbackInvalidationGateRecord,
    SelfStateRollbackBlockedAttemptRecord,
    SelfStateRollbackBoundaryContract,
    SelfStateRollbackCounterfactualComparison,
    SelfStateRollbackNoForkGuardRecord,
    SelfStateRollbackProcessReceipt,
    build_hashed_record,
    record_from_payload,
)


def initialize_self_state_rollback_boundary(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    package_138_state_dir: str | Path,
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
            package_138_state_dir,
        )
    )
    _validate_external_roots(root, output, *sources)
    source = load_package_139_sources_read_only(
        package_133_state_dir=sources[0],
        package_134_state_dir=sources[1],
        package_137_state_dir=sources[2],
        package_138_state_dir=sources[3],
        require_canonical_leaf=True,
    )
    contract = _build_boundary_contract(source)
    store = Package139SelfStateRollbackStore(output)
    store.append_once("self_state_rollback_contracts", contract)
    store.append_once("self_state_rollback_source_bindings", source.source_binding)
    return {
        "source": source,
        "contract": contract,
        "store": store,
        "readiness": "ready_for_explicit_verified_ancestor_rollback",
    }


def build_verified_ancestor_proof(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    package_138_state_dir: str | Path,
    state_dir: str | Path,
    target_self_state_record_id: str,
) -> SelfStateAncestorProofRecord:
    if not target_self_state_record_id:
        raise ValueError("blocked_explicit_rollback_target_required")
    initialized = initialize_self_state_rollback_boundary(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        package_138_state_dir=package_138_state_dir,
        state_dir=state_dir,
    )
    source: Package139SourceBundle = initialized["source"]
    chain = _target_to_current_chain(
        source.package_133,
        source.active_head,
        target_self_state_record_id,
    )
    states: tuple[PersistentSelfStateRecord, ...] = chain["states"]
    transitions: tuple[PersistentSelfStateTransitionRecord, ...] = chain["transitions"]
    target = states[0]
    current = states[-1]
    payload: dict[str, Any] = {
        "ancestor_proof_id": "",
        "ancestor_proof_sha256": "",
        "schema_version": PROOF_SCHEMA_VERSION,
        "created_at": utc_now(),
        "source_binding_ref": source.source_binding.source_binding_id,
        "self_state_lineage_id": current.self_state_lineage_id,
        "current_active_head_id": source.active_head.active_head_id,
        "current_active_head_sha256": source.active_head.active_head_sha256,
        "current_head_revision": source.active_head.head_revision,
        "current_self_state_record_id": current.self_state_record_id,
        "current_self_state_sha256": current.self_state_sha256,
        "current_self_state_version": current.self_state_version,
        "target_self_state_record_id": target.self_state_record_id,
        "target_self_state_sha256": target.self_state_sha256,
        "target_self_state_version": target.self_state_version,
        "ordered_target_to_current_state_refs": tuple(
            item.self_state_record_id for item in states
        ),
        "ordered_target_to_current_state_sha256s": tuple(
            item.self_state_sha256 for item in states
        ),
        "ordered_transition_refs": tuple(item.transition_id for item in transitions),
        "ordered_transition_sha256s": tuple(
            item.transition_sha256 for item in transitions
        ),
        "target_is_strict_ancestor": True,
        "same_lineage_verified": True,
        "complete_parent_hash_chain_verified": True,
        "every_transition_verified": True,
        "no_lineage_fork_verified": True,
        "proof_status": "verified_exact_target_to_current_ancestor_chain",
        "source_record_refs": (
            source.source_binding.source_binding_id,
            source.active_head.active_head_id,
            *(item.self_state_record_id for item in states),
            *(item.transition_id for item in transitions),
        ),
    }
    proof = build_hashed_record(
        SelfStateAncestorProofRecord,
        payload,
        id_field="ancestor_proof_id",
        hash_field="ancestor_proof_sha256",
        prefix="self_state_ancestor_proof",
    )
    initialized["store"].append_once("self_state_ancestor_proofs", proof)
    return proof


def authorize_verified_ancestor_rollback(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    package_138_state_dir: str | Path,
    state_dir: str | Path,
    ancestor_proof_id: str,
    target_session_id: str,
    target_process_instance_id: str,
    authorization_lifetime_ns: int = MAXIMUM_AUTHORIZATION_LIFETIME_NS,
    issued_at_monotonic_ns: int | None = None,
) -> SelfStateHeadSelectionAuthorizationRecord:
    initialized = initialize_self_state_rollback_boundary(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        package_138_state_dir=package_138_state_dir,
        state_dir=state_dir,
    )
    store: Package139SelfStateRollbackStore = initialized["store"]
    proof = record_from_payload(
        SelfStateAncestorProofRecord,
        store.get_payload("self_state_ancestor_proofs", ancestor_proof_id),
    )
    head = initialized["source"].active_head
    if not _proof_matches_head(proof, head):
        raise RuntimeError("blocked_stale_or_wrong_ancestor_proof")
    issued = int(monotonic_ns() if issued_at_monotonic_ns is None else issued_at_monotonic_ns)
    authorization = _build_authorization(
        operation=ROLLBACK_OPERATION,
        contract=initialized["contract"],
        source_binding_ref=initialized["source"].source_binding.source_binding_id,
        proof=proof,
        rollback_receipt_ref=None,
        expected_head=head,
        target_state=_state_by_id(
            initialized["source"].package_133,
            proof.target_self_state_record_id,
        ),
        target_session_id=target_session_id,
        target_process_instance_id=target_process_instance_id,
        issued_at_monotonic_ns=issued,
        authorization_lifetime_ns=authorization_lifetime_ns,
    )
    store.append_once("self_state_head_selection_authorizations", authorization)
    return authorization


def authorize_exact_roll_forward(
    *,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    state_dir: str | Path,
    rollback_receipt_id: str,
    target_session_id: str,
    target_process_instance_id: str,
    authorization_lifetime_ns: int = MAXIMUM_AUTHORIZATION_LIFETIME_NS,
    issued_at_monotonic_ns: int | None = None,
) -> SelfStateHeadSelectionAuthorizationRecord:
    store = Package139SelfStateRollbackStore(state_dir)
    receipt = record_from_payload(
        SelfStateHeadSelectionCommitReceipt,
        store.get_payload("self_state_head_selection_commit_receipts", rollback_receipt_id),
    )
    if receipt.operation != ROLLBACK_OPERATION:
        raise ValueError("blocked_roll_forward_requires_exact_rollback_receipt")
    proof = record_from_payload(
        SelfStateAncestorProofRecord,
        store.get_payload("self_state_ancestor_proofs", receipt.ancestor_proof_ref),
    )
    contract = record_from_payload(
        SelfStateRollbackBoundaryContract,
        store.get_payload("self_state_rollback_contracts", _single_record_id(store, "self_state_rollback_contracts", "contract_id")),
    )
    source = load_package_133_source_read_only(package_133_state_dir)
    head = PersistentSessionRecoveryStore(package_134_state_dir).get_active_head()
    if not all(
        (
            head.active_head_sha256 == receipt.active_head_after_sha256,
            head.head_revision == receipt.head_revision_after,
            head.self_state_record_id == receipt.self_state_record_id_after,
            head.self_state_sha256 == receipt.self_state_sha256_after,
        )
    ):
        raise RuntimeError("blocked_roll_forward_stale_rollback_head")
    target = _state_by_id(source, receipt.preserved_pre_rollback_state_record_id)
    if target.self_state_sha256 != receipt.preserved_pre_rollback_state_sha256:
        raise RuntimeError("blocked_roll_forward_preserved_descendant_hash_mismatch")
    issued = int(monotonic_ns() if issued_at_monotonic_ns is None else issued_at_monotonic_ns)
    authorization = _build_authorization(
        operation=ROLL_FORWARD_OPERATION,
        contract=contract,
        source_binding_ref=proof.source_binding_ref,
        proof=proof,
        rollback_receipt_ref=receipt.commit_receipt_id,
        expected_head=head,
        target_state=target,
        target_session_id=target_session_id,
        target_process_instance_id=target_process_instance_id,
        issued_at_monotonic_ns=issued,
        authorization_lifetime_ns=authorization_lifetime_ns,
    )
    store.append_once("self_state_head_selection_authorizations", authorization)
    return authorization


def commit_authorized_head_selection(
    *,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_138_state_dir: str | Path,
    state_dir: str | Path,
    authorization_id: str,
    allow_self_state_head_selection: bool,
    process_instance_id: str,
    fault_injection: str | None = None,
    evaluated_at_monotonic_ns: int | None = None,
) -> dict[str, Any]:
    started = monotonic_ns()
    pid = os.getpid()
    store = Package139SelfStateRollbackStore(state_dir)
    p134 = PersistentSessionRecoveryStore(package_134_state_dir)
    head_before = _safe_head(p134)
    authorization: SelfStateHeadSelectionAuthorizationRecord | None = None
    proof: SelfStateAncestorProofRecord | None = None
    intent: SelfStateHeadSelectionCommitIntentRecord | None = None
    gate: SelfStateReadbackInvalidationGateRecord | None = None
    try:
        if not allow_self_state_head_selection:
            raise RuntimeError("blocked_self_state_head_selection_authorization_missing")
        authorization = record_from_payload(
            SelfStateHeadSelectionAuthorizationRecord,
            store.get_payload("self_state_head_selection_authorizations", authorization_id),
        )
        if authorization.target_process_instance_id != process_instance_id:
            raise RuntimeError("blocked_head_selection_process_binding_mismatch")
        if store.authorization_consumed(authorization.authorization_id):
            raise RuntimeError("blocked_head_selection_authorization_already_consumed")
        if head_before is None:
            raise RuntimeError("blocked_missing_active_head")
        evaluated = int(
            monotonic_ns()
            if evaluated_at_monotonic_ns is None
            else evaluated_at_monotonic_ns
        )
        _require_authorization_current(authorization, head_before, evaluated)
        proof = record_from_payload(
            SelfStateAncestorProofRecord,
            store.get_payload("self_state_ancestor_proofs", authorization.ancestor_proof_ref),
        )
        source = load_package_133_source_read_only(package_133_state_dir)
        source_binding = record_from_payload(
            Package139AuthoritySourceBindingRecord,
            store.get_payload(
                "self_state_rollback_source_bindings",
                authorization.source_binding_ref,
            ),
        )
        current_tree = package_133_source_tree_sha256(package_133_state_dir)
        if current_tree != source_binding.package_133_tree_sha256:
            raise RuntimeError("blocked_package_133_history_changed_after_authorization")
        if authorization.operation == ROLLBACK_OPERATION:
            proof_current = _proof_matches_head(proof, head_before)
            expected_leaf_id = head_before.self_state_record_id
            expected_leaf_sha256 = head_before.self_state_sha256
            expected_leaf_version = head_before.self_state_version
        else:
            proof_current = all(
                (
                    head_before.self_state_record_id == proof.target_self_state_record_id,
                    head_before.self_state_sha256 == proof.target_self_state_sha256,
                    authorization.target_self_state_record_id
                    == proof.current_self_state_record_id,
                    authorization.target_self_state_sha256
                    == proof.current_self_state_sha256,
                )
            )
            expected_leaf_id = authorization.target_self_state_record_id
            expected_leaf_sha256 = authorization.target_self_state_sha256
            expected_leaf_version = authorization.target_self_state_version
        if not proof_current:
            raise RuntimeError("blocked_stale_rollback_ancestor_proof")
        if not all(
            (
                source.leaf.self_state_record_id == expected_leaf_id,
                source.leaf.self_state_sha256 == expected_leaf_sha256,
                source.leaf.self_state_version == expected_leaf_version,
            )
        ):
            raise RuntimeError("blocked_cross_authority_partial_or_ambiguous_state")
        target = _state_by_id(source, authorization.target_self_state_record_id)
        _require_authorized_target(authorization, proof, target, store)
        invalidation = invalidate_readbacks_before_authorized_head_transition(
            state_dir=package_138_state_dir,
            expected_head=head_before,
            authorization_ref=authorization.authorization_id,
            operation=authorization.operation,
        )
        gate = _build_invalidation_gate(
            authorization=authorization,
            head=head_before,
            invalidation=invalidation,
        )
        intent = _build_commit_intent(
            authorization=authorization,
            proof=proof,
            gate=gate,
            head=head_before,
        )
        consumption = _build_consumption(authorization, intent)
        store.append_group(
            (
                ("self_state_readback_invalidation_gates", gate),
                ("self_state_head_selection_commit_intents", intent),
                ("self_state_head_selection_authorization_consumptions", consumption),
            )
        )
        tree_before = package_133_source_tree_sha256(package_133_state_dir)
        new_head = _build_selected_head(
            expected_head=head_before,
            target=target,
            authorization=authorization,
        )
        cas_event = _build_successful_selection_cas_event(
            authorization=authorization,
            expected_head=head_before,
            new_head=new_head,
            proof=proof,
            gate=gate,
        )
        identity_binding = None
        if authorization.operation == ROLL_FORWARD_OPERATION:
            identity_binding = build_identity_binding(
                source=source,
                head=new_head,
                binding_kind="verified_roll_forward_binding",
                session_id=authorization.target_session_id,
                process_instance_id=authorization.target_process_instance_id,
                operating_system_process_id=pid,
                recovered_from_session_id=head_before.bound_session_id,
                authorization_id=authorization.authorization_id,
            )
        p134_fault = fault_injection if fault_injection in {
            "force_cas_conflict",
            "after_head_update_before_commit",
        } else None
        p134.reselect_verified_state_atomic(
            authorization_id=authorization.authorization_id,
            expected_head=head_before,
            new_head=new_head,
            cas_event=cas_event,
            identity_binding=identity_binding,
            fault_injection=p134_fault,
        )
        if fault_injection == "after_package_134_cas_before_receipt":
            raise RuntimeError("simulated_post_cas_receipt_failure")
        if fault_injection not in {
            None,
            "force_cas_conflict",
            "after_head_update_before_commit",
            "after_package_134_cas_before_receipt",
        }:
            raise ValueError("unknown Package 139 fault injection")
        tree_after = package_133_source_tree_sha256(package_133_state_dir)
        receipt = _build_commit_receipt(
            authorization=authorization,
            proof=proof,
            intent=intent,
            gate=gate,
            cas_event=cas_event,
            identity_binding_ref=(identity_binding.binding_id if identity_binding else None),
            head_before=head_before,
            head_after=new_head,
            tree_before=tree_before,
            tree_after=tree_after,
            store=store,
        )
        process = _build_process_receipt(
            authorization=authorization,
            process_instance_id=process_instance_id,
            pid=pid,
            started=started,
            commit_receipt_ref=receipt.commit_receipt_id,
            blocked_attempt_ref=None,
        )
        store.append_group(
            (
                ("self_state_head_selection_commit_receipts", receipt),
                ("self_state_rollback_process_receipts", process),
            )
        )
        return {
            "status": receipt.rollback_or_roll_forward_status,
            "authorization": authorization,
            "proof": proof,
            "invalidation_gate": gate,
            "intent": intent,
            "cas_event": cas_event,
            "identity_binding": identity_binding,
            "receipt": receipt,
            "process_receipt": process,
            "head_before": head_before,
            "head_after": new_head,
        }
    except Exception as error:
        observed = _safe_head(p134)
        if str(error) == "simulated_post_cas_receipt_failure":
            raise
        reason = str(error) or type(error).__name__
        blocked = _build_blocked_attempt(
            operation=(authorization.operation if authorization else ROLLBACK_OPERATION),
            authorization_ref=(authorization.authorization_id if authorization else authorization_id),
            target_ref=(authorization.target_self_state_record_id if authorization else None),
            expected_head=head_before,
            observed_head=observed,
            failure_reason=reason,
        )
        process = _build_process_receipt(
            authorization=authorization,
            authorization_id=authorization_id,
            process_instance_id=process_instance_id,
            pid=pid,
            started=started,
            commit_receipt_ref=None,
            blocked_attempt_ref=blocked.blocked_attempt_id,
        )
        store.append_group(
            (
                ("self_state_rollback_blocked_attempts", blocked),
                ("self_state_rollback_process_receipts", process),
            )
        )
        return {
            "status": "blocked_head_selection",
            "failure_reason": reason,
            "blocked_attempt": blocked,
            "process_receipt": process,
            "head_before": head_before,
            "head_after": observed,
        }


def reconcile_committed_head_selection(
    *,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    state_dir: str | Path,
    authorization_id: str,
) -> SelfStateHeadSelectionCommitReceipt:
    store = Package139SelfStateRollbackStore(state_dir)
    existing = store.receipt_for_authorization(authorization_id)
    if existing is not None:
        return record_from_payload(SelfStateHeadSelectionCommitReceipt, existing)
    authorization = record_from_payload(
        SelfStateHeadSelectionAuthorizationRecord,
        store.get_payload("self_state_head_selection_authorizations", authorization_id),
    )
    proof = record_from_payload(
        SelfStateAncestorProofRecord,
        store.get_payload("self_state_ancestor_proofs", authorization.ancestor_proof_ref),
    )
    intents = tuple(
        record_from_payload(SelfStateHeadSelectionCommitIntentRecord, item)
        for item in store.list_payloads("self_state_head_selection_commit_intents")
        if item.get("authorization_ref") == authorization_id
    )
    gates = tuple(
        record_from_payload(SelfStateReadbackInvalidationGateRecord, item)
        for item in store.list_payloads("self_state_readback_invalidation_gates")
        if item.get("authorization_ref") == authorization_id
    )
    if len(intents) != 1 or len(gates) != 1:
        raise RuntimeError("blocked_ambiguous_package_139_pending_commit")
    p134 = PersistentSessionRecoveryStore(package_134_state_dir)
    events = tuple(
        item
        for item in p134.list_payloads("active_head_cas_events")
        if item.get("authorization_id") == authorization_id
        and item.get("operation") == authorization.operation
        and item.get("cas_succeeded") is True
    )
    if len(events) != 1:
        raise RuntimeError("blocked_package_139_committed_cas_missing_or_ambiguous")
    event = ActiveHeadCASEventRecord(**_tuple_payload(events[0]))
    head_after = p134.get_active_head()
    if not all(
        (
            event.new_active_head_sha256 == head_after.active_head_sha256,
            event.new_head_revision == head_after.head_revision,
            head_after.self_state_record_id == authorization.target_self_state_record_id,
            head_after.self_state_sha256 == authorization.target_self_state_sha256,
        )
    ):
        raise RuntimeError("blocked_package_139_reconciliation_head_advanced_or_mismatched")
    source = load_package_133_source_read_only(package_133_state_dir)
    before_state = _state_by_id(source, authorization.expected_current_self_state_record_id)
    head_before = _head_from_authorization(authorization, before_state)
    identity_binding_ref = None
    if authorization.operation == ROLL_FORWARD_OPERATION:
        bindings = tuple(
            item
            for item in p134.list_payloads("persistent_session_identity_bindings")
            if item.get("active_head_sha256") == head_after.active_head_sha256
            and item.get("binding_kind") == "verified_roll_forward_binding"
        )
        if len(bindings) != 1:
            raise RuntimeError("blocked_package_139_roll_forward_binding_missing")
        identity_binding_ref = str(bindings[0]["binding_id"])
    tree = package_133_source_tree_sha256(package_133_state_dir)
    receipt = _build_commit_receipt(
        authorization=authorization,
        proof=proof,
        intent=intents[0],
        gate=gates[0],
        cas_event=event,
        identity_binding_ref=identity_binding_ref,
        head_before=head_before,
        head_after=head_after,
        tree_before=tree,
        tree_after=tree,
        store=store,
    )
    store.append_once("self_state_head_selection_commit_receipts", receipt)
    return receipt


def run_real_self_state_rollback_and_roll_forward(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    package_138_state_dir: str | Path,
    state_dir: str | Path,
    target_self_state_record_id: str,
    allow_self_state_rollback: bool,
    allow_exact_roll_forward: bool,
) -> dict[str, Any]:
    if not allow_self_state_rollback:
        raise RuntimeError("blocked_self_state_rollback_authorization_missing")
    if not allow_exact_roll_forward:
        raise RuntimeError("blocked_exact_roll_forward_authorization_missing")
    process_instance_id = stable_id("package_139_process")
    session_id = stable_id("package_139_session")
    proof = build_verified_ancestor_proof(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        package_138_state_dir=package_138_state_dir,
        state_dir=state_dir,
        target_self_state_record_id=target_self_state_record_id,
    )
    rollback_authorization = authorize_verified_ancestor_rollback(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        package_138_state_dir=package_138_state_dir,
        state_dir=state_dir,
        ancestor_proof_id=proof.ancestor_proof_id,
        target_session_id=session_id,
        target_process_instance_id=process_instance_id,
    )
    rollback = commit_authorized_head_selection(
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_138_state_dir=package_138_state_dir,
        state_dir=state_dir,
        authorization_id=rollback_authorization.authorization_id,
        allow_self_state_head_selection=True,
        process_instance_id=process_instance_id,
    )
    if rollback.get("status") != "committed_verified_ancestor_rollback":
        raise RuntimeError(f"blocked_package_139_real_rollback:{rollback.get('failure_reason')}")
    mutation_blocked = False
    mutation_block_reason = ""
    try:
        preflight_self_state_review_gate(
            ashl_root=ashl_root,
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=package_134_state_dir,
            state_dir=package_137_state_dir,
        )
    except RuntimeError as error:
        mutation_blocked = "blocked_cross_authority_partial_or_ambiguous_state" in str(error)
        mutation_block_reason = str(error)
    source = load_package_133_source_read_only(package_133_state_dir)
    rolled_back_head = PersistentSessionRecoveryStore(package_134_state_dir).get_active_head()
    recovery_authorization = build_recovery_authorization(
        source=source,
        operation="recover_session",
        target_session_id=stable_id("package_139_blocked_recovery_session"),
        target_process_instance_id=stable_id("package_139_blocked_recovery_process"),
        expected_head=rolled_back_head,
    )
    recovery_resolution = build_recovery_resolution(
        source=source,
        authorization=recovery_authorization,
        head=rolled_back_head,
        active_head_candidate_count=1,
        shutdown_payloads=PersistentSessionRecoveryStore(package_134_state_dir).list_payloads(
            "persistent_session_shutdown_records"
        ),
    )
    recovery_blocked = (
        recovery_resolution.decision == "blocked_recovery"
        and recovery_resolution.stale_head_detected
    )
    if not mutation_blocked or not recovery_blocked:
        raise RuntimeError("blocked_package_139_no_fork_guard_not_enforced")
    no_fork_guard = _build_no_fork_guard(
        rollback_receipt=rollback["receipt"],
        rolled_back_head=rolled_back_head,
        canonical_leaf=source.leaf,
        mutation_block_reason=mutation_block_reason,
        recovery_block_reason=",".join(recovery_resolution.failure_reasons),
    )
    Package139SelfStateRollbackStore(state_dir).append_once(
        "self_state_rollback_no_fork_guard_records", no_fork_guard
    )
    roll_forward_authorization = authorize_exact_roll_forward(
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        state_dir=state_dir,
        rollback_receipt_id=rollback["receipt"].commit_receipt_id,
        target_session_id=session_id,
        target_process_instance_id=process_instance_id,
    )
    roll_forward = commit_authorized_head_selection(
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_138_state_dir=package_138_state_dir,
        state_dir=state_dir,
        authorization_id=roll_forward_authorization.authorization_id,
        allow_self_state_head_selection=True,
        process_instance_id=process_instance_id,
    )
    if roll_forward.get("status") != "committed_exact_preserved_descendant_roll_forward":
        raise RuntimeError(f"blocked_package_139_real_roll_forward:{roll_forward.get('failure_reason')}")
    final_head = PersistentSessionRecoveryStore(package_134_state_dir).get_active_head()
    if not (
        final_head.self_state_record_id == source.leaf.self_state_record_id
        and final_head.self_state_sha256 == source.leaf.self_state_sha256
    ):
        raise RuntimeError("blocked_package_139_roll_forward_did_not_restore_leaf")
    comparison = _build_counterfactual_comparison(
        rollback["receipt"], roll_forward["receipt"]
    )
    store = Package139SelfStateRollbackStore(state_dir)
    store.append_once("self_state_rollback_counterfactual_comparisons", comparison)
    identity_binding = roll_forward["identity_binding"]
    shutdown = build_clean_shutdown_record(
        head=final_head,
        session_id=session_id,
        process_instance_id=process_instance_id,
        operating_system_process_id=os.getpid(),
        identity_binding_id=identity_binding.binding_id,
    )
    PersistentSessionRecoveryStore(package_134_state_dir).append_record(
        "persistent_session_shutdown_records", shutdown
    )
    future_authorization = build_recovery_authorization(
        source=source,
        operation="recover_session",
        target_session_id=stable_id("package_139_future_recovery_session"),
        target_process_instance_id=stable_id("package_139_future_recovery_process"),
        expected_head=final_head,
    )
    future_resolution = build_recovery_resolution(
        source=source,
        authorization=future_authorization,
        head=final_head,
        active_head_candidate_count=1,
        shutdown_payloads=PersistentSessionRecoveryStore(package_134_state_dir).list_payloads(
            "persistent_session_shutdown_records"
        ),
    )
    if future_resolution.decision != "allow_exact_recovery_cas":
        raise RuntimeError("blocked_package_139_recovery_not_restored_after_roll_forward")
    return {
        "status": "completed_verified_ancestor_rollback_and_exact_roll_forward",
        "process_instance_id": process_instance_id,
        "runtime_session_id": session_id,
        "proof": proof,
        "rollback_authorization": rollback_authorization,
        "rollback": rollback,
        "mutation_while_rolled_back_blocked": mutation_blocked,
        "recovery_while_rolled_back_blocked": recovery_blocked,
        "no_fork_guard": no_fork_guard,
        "roll_forward_authorization": roll_forward_authorization,
        "roll_forward": roll_forward,
        "comparison": comparison,
        "shutdown": shutdown,
        "future_recovery_resolution": future_resolution,
    }


def _build_boundary_contract(source: Package139SourceBundle) -> SelfStateRollbackBoundaryContract:
    payload: dict[str, Any] = {
        "contract_id": "",
        "contract_sha256": "",
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "self_state_authority": SELF_STATE_AUTHORITY,
        "active_head_authority": ACTIVE_HEAD_AUTHORITY,
        "review_gate_authority": REVIEW_GATE_AUTHORITY,
        "readback_authority": READBACK_AUTHORITY,
        "rollback_authority": ROLLBACK_AUTHORITY,
        "verified_ancestor_only": True,
        "exact_current_head_binding_required": True,
        "exact_target_state_binding_required": True,
        "exact_package_134_cas_required": True,
        "package_133_history_immutable": True,
        "intervening_descendants_preserved": True,
        "attempts_append_only": True,
        "readback_terminal_before_head_change": True,
        "mutation_blocked_while_ancestor_selected": True,
        "recovery_blocked_while_ancestor_selected": True,
        "exact_roll_forward_required": True,
        "roll_forward_target_is_preserved_pre_rollback_state": True,
        "automatic_rebase_allowed": False,
        "latest_selection_allowed": False,
        "cross_lineage_selection_allowed": False,
        "memory_or_runtime_content_restoration_allowed": False,
        "contract_status": "verified_ancestor_head_selection_without_history_rewrite",
        "source_record_refs": (
            source.source_binding.source_binding_id,
            source.package_133.snapshot.source_snapshot_id,
            source.active_head.active_head_id,
        ),
    }
    return build_hashed_record(
        SelfStateRollbackBoundaryContract,
        payload,
        id_field="contract_id",
        hash_field="contract_sha256",
        prefix="self_state_rollback_contract",
    )


def _target_to_current_chain(
    source: Package133SourceBundle,
    head: ActiveSelfStateHeadRecord,
    target_id: str,
) -> dict[str, Any]:
    by_id = {item.self_state_record_id: item for item in source.states}
    transition_by_child = {
        item.child_self_state_record_id: item for item in source.transitions
    }
    current = by_id.get(head.self_state_record_id)
    target = by_id.get(target_id)
    if current is None:
        raise RuntimeError("blocked_current_head_state_missing_from_package_133")
    if target is None:
        raise RuntimeError("blocked_rollback_target_not_in_authoritative_lineage")
    validate_ancestor_target_identity(current=current, target=target)
    reverse_states = [current]
    reverse_transitions: list[PersistentSelfStateTransitionRecord] = []
    cursor = current
    while cursor.self_state_record_id != target.self_state_record_id:
        if cursor.parent_self_state_record_id is None:
            raise RuntimeError("blocked_rollback_target_not_verified_ancestor")
        parent = by_id.get(cursor.parent_self_state_record_id)
        transition = transition_by_child.get(cursor.self_state_record_id)
        if parent is None or transition is None:
            raise RuntimeError("blocked_incomplete_rollback_ancestor_chain")
        if not validate_persistent_self_state_lineage(parent, cursor, transition)["valid"]:
            raise RuntimeError("blocked_corrupt_rollback_ancestor_chain")
        reverse_transitions.append(transition)
        reverse_states.append(parent)
        cursor = parent
    return {
        "states": tuple(reversed(reverse_states)),
        "transitions": tuple(reversed(reverse_transitions)),
    }


def validate_ancestor_target_identity(*, current: Any, target: Any) -> None:
    """Reject a target that is not an older record in the exact current lineage."""
    if target.self_state_lineage_id != current.self_state_lineage_id:
        raise RuntimeError("blocked_cross_lineage_rollback_target")
    if target.self_state_record_id == current.self_state_record_id:
        raise RuntimeError("blocked_rollback_target_must_be_strict_ancestor")
    if target.self_state_version >= current.self_state_version:
        raise RuntimeError("blocked_rollback_target_is_not_older")


def _build_authorization(
    *,
    operation: str,
    contract: SelfStateRollbackBoundaryContract,
    source_binding_ref: str,
    proof: SelfStateAncestorProofRecord,
    rollback_receipt_ref: str | None,
    expected_head: ActiveSelfStateHeadRecord,
    target_state: PersistentSelfStateRecord,
    target_session_id: str,
    target_process_instance_id: str,
    issued_at_monotonic_ns: int,
    authorization_lifetime_ns: int,
) -> SelfStateHeadSelectionAuthorizationRecord:
    if operation not in HEAD_SELECTION_OPERATIONS:
        raise ValueError("invalid Package 139 authorization operation")
    if authorization_lifetime_ns <= 0 or authorization_lifetime_ns > MAXIMUM_AUTHORIZATION_LIFETIME_NS:
        raise ValueError("blocked_head_selection_authorization_lifetime_invalid")
    payload: dict[str, Any] = {
        "authorization_id": "",
        "authorization_sha256": "",
        "schema_version": AUTHORIZATION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "operation": operation,
        "contract_ref": contract.contract_id,
        "source_binding_ref": source_binding_ref,
        "ancestor_proof_ref": proof.ancestor_proof_id,
        "rollback_receipt_ref": rollback_receipt_ref,
        "authorization_source": "explicit_local_operator_request",
        "authorized_by": "local_operator",
        "explicit_authorization": True,
        "expected_active_head_id": expected_head.active_head_id,
        "expected_active_head_sha256": expected_head.active_head_sha256,
        "expected_head_revision": expected_head.head_revision,
        "expected_current_self_state_record_id": expected_head.self_state_record_id,
        "expected_current_self_state_sha256": expected_head.self_state_sha256,
        "target_self_state_record_id": target_state.self_state_record_id,
        "target_self_state_sha256": target_state.self_state_sha256,
        "target_self_state_version": target_state.self_state_version,
        "target_session_id": target_session_id,
        "target_process_instance_id": target_process_instance_id,
        "issued_at_monotonic_ns": issued_at_monotonic_ns,
        "expires_at_monotonic_ns": issued_at_monotonic_ns + authorization_lifetime_ns,
        "one_use_only": True,
        "verified_ancestor_required": True,
        "readback_authorization_used": False,
        "teacher_review_authorization_used": False,
        "automatic_rebase_allowed": False,
        "authorization_status": {
            ROLLBACK_OPERATION: "authorized_for_one_exact_verified_ancestor_rollback",
            ROLL_FORWARD_OPERATION: "authorized_for_one_exact_preserved_descendant_roll_forward",
        }[operation],
        "source_record_refs": tuple(
            item
            for item in (
                contract.contract_id,
                source_binding_ref,
                proof.ancestor_proof_id,
                rollback_receipt_ref,
                expected_head.active_head_id,
                expected_head.self_state_record_id,
                target_state.self_state_record_id,
            )
            if item
        ),
    }
    return build_hashed_record(
        SelfStateHeadSelectionAuthorizationRecord,
        payload,
        id_field="authorization_id",
        hash_field="authorization_sha256",
        prefix="self_state_head_selection_authorization",
    )


def _require_authorization_current(
    authorization: SelfStateHeadSelectionAuthorizationRecord,
    head: ActiveSelfStateHeadRecord,
    evaluated_at_monotonic_ns: int,
) -> None:
    if not (
        authorization.issued_at_monotonic_ns
        <= evaluated_at_monotonic_ns
        < authorization.expires_at_monotonic_ns
    ):
        raise RuntimeError("blocked_head_selection_authorization_expired")
    if not all(
        (
            authorization.expected_active_head_id == head.active_head_id,
            authorization.expected_active_head_sha256 == head.active_head_sha256,
            authorization.expected_head_revision == head.head_revision,
            authorization.expected_current_self_state_record_id
            == head.self_state_record_id,
            authorization.expected_current_self_state_sha256
            == head.self_state_sha256,
        )
    ):
        raise RuntimeError("blocked_stale_head_selection_authorization")


def _require_authorized_target(
    authorization: SelfStateHeadSelectionAuthorizationRecord,
    proof: SelfStateAncestorProofRecord,
    target: PersistentSelfStateRecord,
    store: Package139SelfStateRollbackStore,
) -> None:
    if not all(
        (
            authorization.ancestor_proof_ref == proof.ancestor_proof_id,
            authorization.target_self_state_record_id == target.self_state_record_id,
            authorization.target_self_state_sha256 == target.self_state_sha256,
            authorization.target_self_state_version == target.self_state_version,
            target.self_state_lineage_id == proof.self_state_lineage_id,
        )
    ):
        raise RuntimeError("blocked_authorized_target_identity_mismatch")
    if authorization.operation == ROLLBACK_OPERATION:
        if target.self_state_record_id != proof.target_self_state_record_id:
            raise RuntimeError("blocked_rollback_target_not_proven_ancestor")
    else:
        receipt = record_from_payload(
            SelfStateHeadSelectionCommitReceipt,
            store.get_payload(
                "self_state_head_selection_commit_receipts",
                str(authorization.rollback_receipt_ref),
            ),
        )
        if not all(
            (
                receipt.operation == ROLLBACK_OPERATION,
                receipt.ancestor_proof_ref == proof.ancestor_proof_id,
                target.self_state_record_id
                == receipt.preserved_pre_rollback_state_record_id,
                target.self_state_sha256
                == receipt.preserved_pre_rollback_state_sha256,
            )
        ):
            raise RuntimeError("blocked_arbitrary_or_unpreserved_roll_forward_target")


def _build_invalidation_gate(
    *,
    authorization: SelfStateHeadSelectionAuthorizationRecord,
    head: ActiveSelfStateHeadRecord,
    invalidation: dict[str, Any],
) -> SelfStateReadbackInvalidationGateRecord:
    payload: dict[str, Any] = {
        "invalidation_gate_id": "",
        "invalidation_gate_sha256": "",
        "schema_version": INVALIDATION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "operation": authorization.operation,
        "authorization_ref": authorization.authorization_id,
        "expected_active_head_id": head.active_head_id,
        "expected_active_head_sha256": head.active_head_sha256,
        "expected_head_revision": head.head_revision,
        "matching_readback_refs": invalidation["matching_readback_refs"],
        "preexisting_terminal_readback_refs": invalidation[
            "preexisting_terminal_readback_refs"
        ],
        "new_package_138_lifecycle_refs": invalidation["new_lifecycle_refs"],
        "active_readback_count_before": invalidation["active_readback_count_before"],
        "active_readback_count_after": invalidation["active_readback_count_after"],
        "package_138_store_integrity_valid": True,
        "invalidation_completed_before_cas": True,
        "readback_authorization_granted_rollback": False,
        "gate_status": "all_exact_head_readbacks_terminal_before_cas",
        "source_record_refs": (
            authorization.authorization_id,
            head.active_head_id,
            *invalidation["matching_readback_refs"],
            *invalidation["new_lifecycle_refs"],
        ),
    }
    return build_hashed_record(
        SelfStateReadbackInvalidationGateRecord,
        payload,
        id_field="invalidation_gate_id",
        hash_field="invalidation_gate_sha256",
        prefix="self_state_readback_invalidation_gate",
    )


def _build_commit_intent(
    *,
    authorization: SelfStateHeadSelectionAuthorizationRecord,
    proof: SelfStateAncestorProofRecord,
    gate: SelfStateReadbackInvalidationGateRecord,
    head: ActiveSelfStateHeadRecord,
) -> SelfStateHeadSelectionCommitIntentRecord:
    payload = {
        "commit_intent_id": "",
        "commit_intent_sha256": "",
        "schema_version": INTENT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "operation": authorization.operation,
        "authorization_ref": authorization.authorization_id,
        "ancestor_proof_ref": proof.ancestor_proof_id,
        "rollback_receipt_ref": authorization.rollback_receipt_ref,
        "readback_invalidation_gate_ref": gate.invalidation_gate_id,
        "expected_active_head_id": head.active_head_id,
        "expected_active_head_sha256": head.active_head_sha256,
        "expected_head_revision": head.head_revision,
        "expected_current_self_state_record_id": head.self_state_record_id,
        "target_self_state_record_id": authorization.target_self_state_record_id,
        "target_self_state_sha256": authorization.target_self_state_sha256,
        "planned_new_head_revision": head.head_revision + 1,
        "package_133_history_write_planned": False,
        "exact_package_134_cas_planned": True,
        "intent_status": "consumed_authorization_pending_exact_package_134_cas",
        "source_record_refs": (
            authorization.authorization_id,
            proof.ancestor_proof_id,
            gate.invalidation_gate_id,
            head.active_head_id,
            head.self_state_record_id,
            authorization.target_self_state_record_id,
        ),
    }
    return build_hashed_record(
        SelfStateHeadSelectionCommitIntentRecord,
        payload,
        id_field="commit_intent_id",
        hash_field="commit_intent_sha256",
        prefix="self_state_head_selection_intent",
    )


def _build_consumption(
    authorization: SelfStateHeadSelectionAuthorizationRecord,
    intent: SelfStateHeadSelectionCommitIntentRecord,
) -> SelfStateHeadSelectionAuthorizationConsumptionRecord:
    payload = {
        "consumption_id": "",
        "consumption_sha256": "",
        "schema_version": CONSUMPTION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "authorization_ref": authorization.authorization_id,
        "operation": authorization.operation,
        "commit_intent_ref": intent.commit_intent_id,
        "one_use_consumed": True,
        "consumption_status": "consumed_for_one_head_selection_attempt",
        "source_record_refs": (authorization.authorization_id, intent.commit_intent_id),
    }
    return build_hashed_record(
        SelfStateHeadSelectionAuthorizationConsumptionRecord,
        payload,
        id_field="consumption_id",
        hash_field="consumption_sha256",
        prefix="self_state_head_selection_consumption",
    )


def _build_selected_head(
    *,
    expected_head: ActiveSelfStateHeadRecord,
    target: PersistentSelfStateRecord,
    authorization: SelfStateHeadSelectionAuthorizationRecord,
) -> ActiveSelfStateHeadRecord:
    payload = expected_head.to_dict()
    payload.update(
        {
            "active_head_sha256": "",
            "schema_version": HEAD_SCHEMA_VERSION,
            "updated_at": utc_now(),
            "self_state_lineage_id": target.self_state_lineage_id,
            "self_state_record_id": target.self_state_record_id,
            "self_state_sha256": target.self_state_sha256,
            "self_state_version": target.self_state_version,
            "lineage_generation": target.lineage_generation,
            "head_revision": expected_head.head_revision + 1,
            "bound_session_id": authorization.target_session_id,
            "bound_process_instance_id": authorization.target_process_instance_id,
            "previous_active_head_sha256": expected_head.active_head_sha256,
            "authority_status": "active_identity_binding",
            "representation_authority": REPRESENTATION_AUTHORITY,
            "active_head_authority": PACKAGE_134_ACTIVE_HEAD_AUTHORITY,
            "source_record_refs": expected_head.source_record_refs
            + (
                authorization.authorization_id,
                authorization.ancestor_proof_ref,
                target.self_state_record_id,
            ),
        }
    )
    identity = dict(payload)
    identity.pop("active_head_sha256")
    payload["active_head_sha256"] = sha256_payload(identity)
    return ActiveSelfStateHeadRecord.from_dict(payload)


def _build_successful_selection_cas_event(
    *,
    authorization: SelfStateHeadSelectionAuthorizationRecord,
    expected_head: ActiveSelfStateHeadRecord,
    new_head: ActiveSelfStateHeadRecord,
    proof: SelfStateAncestorProofRecord,
    gate: SelfStateReadbackInvalidationGateRecord,
) -> ActiveHeadCASEventRecord:
    identity = {
        "authorization": authorization.authorization_id,
        "operation": authorization.operation,
        "expected": expected_head.active_head_sha256,
        "new": new_head.active_head_sha256,
    }
    return ActiveHeadCASEventRecord(
        cas_event_id=f"active_head_cas_event:{sha256_payload(identity)[:16]}",
        schema_version=CAS_SCHEMA_VERSION,
        created_at=utc_now(),
        authorization_id=authorization.authorization_id,
        operation=authorization.operation,
        active_head_id=expected_head.active_head_id,
        expected_head_revision=expected_head.head_revision,
        expected_active_head_sha256=expected_head.active_head_sha256,
        observed_head_revision=expected_head.head_revision,
        observed_active_head_sha256=expected_head.active_head_sha256,
        previous_bound_session_id=expected_head.bound_session_id,
        requested_bound_session_id=new_head.bound_session_id,
        new_head_revision=new_head.head_revision,
        new_active_head_sha256=new_head.active_head_sha256,
        cas_succeeded=True,
        transaction_committed=True,
        self_state_record_unchanged=False,
        self_state_lineage_unchanged=True,
        failure_reason=None,
        source_record_refs=(
            authorization.authorization_id,
            proof.ancestor_proof_id,
            gate.invalidation_gate_id,
            expected_head.self_state_record_id,
            new_head.self_state_record_id,
        ),
    )


def _build_commit_receipt(
    *,
    authorization: SelfStateHeadSelectionAuthorizationRecord,
    proof: SelfStateAncestorProofRecord,
    intent: SelfStateHeadSelectionCommitIntentRecord,
    gate: SelfStateReadbackInvalidationGateRecord,
    cas_event: ActiveHeadCASEventRecord,
    identity_binding_ref: str | None,
    head_before: ActiveSelfStateHeadRecord | _HeadReceiptView,
    head_after: ActiveSelfStateHeadRecord,
    tree_before: str,
    tree_after: str,
    store: Package139SelfStateRollbackStore,
) -> SelfStateHeadSelectionCommitReceipt:
    if authorization.operation == ROLLBACK_OPERATION:
        preserved_id = head_before.self_state_record_id
        preserved_hash = head_before.self_state_sha256
        paired = None
        descendants = tuple(proof.ordered_target_to_current_state_refs[1:])
    else:
        rollback = record_from_payload(
            SelfStateHeadSelectionCommitReceipt,
            store.get_payload(
                "self_state_head_selection_commit_receipts",
                str(authorization.rollback_receipt_ref),
            ),
        )
        preserved_id = rollback.preserved_pre_rollback_state_record_id
        preserved_hash = rollback.preserved_pre_rollback_state_sha256
        paired = rollback.commit_receipt_id
        descendants = rollback.intervening_descendant_refs
    payload = {
        "commit_receipt_id": "",
        "commit_receipt_sha256": "",
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "operation": authorization.operation,
        "authorization_ref": authorization.authorization_id,
        "commit_intent_ref": intent.commit_intent_id,
        "ancestor_proof_ref": proof.ancestor_proof_id,
        "paired_rollback_receipt_ref": paired,
        "package_134_cas_event_ref": cas_event.cas_event_id,
        "identity_binding_ref": identity_binding_ref,
        "active_head_id": head_before.active_head_id,
        "active_head_before_sha256": head_before.active_head_sha256,
        "active_head_after_sha256": head_after.active_head_sha256,
        "head_revision_before": head_before.head_revision,
        "head_revision_after": head_after.head_revision,
        "self_state_record_id_before": head_before.self_state_record_id,
        "self_state_sha256_before": head_before.self_state_sha256,
        "self_state_version_before": head_before.self_state_version,
        "self_state_record_id_after": head_after.self_state_record_id,
        "self_state_sha256_after": head_after.self_state_sha256,
        "self_state_version_after": head_after.self_state_version,
        "preserved_pre_rollback_state_record_id": preserved_id,
        "preserved_pre_rollback_state_sha256": preserved_hash,
        "intervening_descendant_refs": descendants,
        "package_133_tree_sha256_before": tree_before,
        "package_133_tree_sha256_after": tree_after,
        "package_133_history_unchanged": tree_before == tree_after,
        "intervening_history_preserved": True,
        "exact_package_134_cas_committed": True,
        "readbacks_terminal_before_cas": gate.active_readback_count_after == 0,
        "head_revision_increment_exact": head_after.head_revision == head_before.head_revision + 1,
        "source_state_record_modified": False,
        "history_record_deleted": False,
        "rollback_or_roll_forward_status": {
            ROLLBACK_OPERATION: "committed_verified_ancestor_rollback",
            ROLL_FORWARD_OPERATION: "committed_exact_preserved_descendant_roll_forward",
        }[authorization.operation],
        "source_record_refs": tuple(
            item
            for item in (
                authorization.authorization_id,
                intent.commit_intent_id,
                proof.ancestor_proof_id,
                paired,
                cas_event.cas_event_id,
                identity_binding_ref,
                head_before.self_state_record_id,
                head_after.self_state_record_id,
                *descendants,
            )
            if item
        ),
    }
    return build_hashed_record(
        SelfStateHeadSelectionCommitReceipt,
        payload,
        id_field="commit_receipt_id",
        hash_field="commit_receipt_sha256",
        prefix="self_state_head_selection_receipt",
    )


def _build_blocked_attempt(
    *,
    operation: str,
    authorization_ref: str | None,
    target_ref: str | None,
    expected_head: ActiveSelfStateHeadRecord | None,
    observed_head: ActiveSelfStateHeadRecord | None,
    failure_reason: str,
) -> SelfStateRollbackBlockedAttemptRecord:
    payload = {
        "blocked_attempt_id": "",
        "blocked_attempt_sha256": "",
        "schema_version": BLOCKED_SCHEMA_VERSION,
        "created_at": utc_now(),
        "operation": operation,
        "authorization_ref": authorization_ref,
        "target_self_state_record_id": target_ref,
        "expected_active_head_sha256": (
            expected_head.active_head_sha256 if expected_head else None
        ),
        "observed_active_head_sha256": (
            observed_head.active_head_sha256 if observed_head else None
        ),
        "expected_head_revision": expected_head.head_revision if expected_head else None,
        "observed_head_revision": observed_head.head_revision if observed_head else None,
        "failure_reason": failure_reason,
        "authoritative_head_changed": bool(
            expected_head is not None
            and observed_head is not None
            and expected_head.active_head_sha256 != observed_head.active_head_sha256
        ),
        "package_133_history_changed": False,
        "automatic_rebase_used": False,
        "latest_selection_used": False,
        "blocked_status": "blocked_without_authoritative_head_change",
        "source_record_refs": tuple(
            item
            for item in (
                authorization_ref,
                target_ref,
                expected_head.active_head_id if expected_head else None,
            )
            if item
        ),
    }
    if payload["authoritative_head_changed"]:
        raise RuntimeError("blocked_attempt_builder_detected_authoritative_head_change")
    return build_hashed_record(
        SelfStateRollbackBlockedAttemptRecord,
        payload,
        id_field="blocked_attempt_id",
        hash_field="blocked_attempt_sha256",
        prefix="self_state_rollback_blocked_attempt",
    )


def _build_process_receipt(
    *,
    authorization: SelfStateHeadSelectionAuthorizationRecord | None,
    process_instance_id: str,
    pid: int,
    started: int,
    commit_receipt_ref: str | None,
    blocked_attempt_ref: str | None,
    authorization_id: str | None = None,
) -> SelfStateRollbackProcessReceipt:
    operation = authorization.operation if authorization else ROLLBACK_OPERATION
    auth_ref = authorization.authorization_id if authorization else str(authorization_id)
    payload = {
        "process_receipt_id": "",
        "process_receipt_sha256": "",
        "schema_version": PROCESS_SCHEMA_VERSION,
        "created_at": utc_now(),
        "operation": operation,
        "process_instance_id": process_instance_id,
        "operating_system_process_id": pid,
        "started_monotonic_ns": started,
        "ended_monotonic_ns": monotonic_ns(),
        "authorization_ref": auth_ref,
        "commit_receipt_ref": commit_receipt_ref,
        "blocked_attempt_ref": blocked_attempt_ref,
        "worker_status": (
            "head_selection_committed" if commit_receipt_ref else "head_selection_blocked"
        ),
        "source_record_refs": tuple(
            item for item in (auth_ref, commit_receipt_ref, blocked_attempt_ref) if item
        ),
    }
    return build_hashed_record(
        SelfStateRollbackProcessReceipt,
        payload,
        id_field="process_receipt_id",
        hash_field="process_receipt_sha256",
        prefix="self_state_rollback_process_receipt",
    )


def _build_counterfactual_comparison(
    rollback: SelfStateHeadSelectionCommitReceipt,
    roll_forward: SelfStateHeadSelectionCommitReceipt,
) -> SelfStateRollbackCounterfactualComparison:
    payload = {
        "comparison_id": "",
        "comparison_sha256": "",
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "created_at": utc_now(),
        "rollback_receipt_ref": rollback.commit_receipt_id,
        "roll_forward_receipt_ref": roll_forward.commit_receipt_id,
        "selected_state_restored_to_pre_rollback_record": (
            roll_forward.self_state_record_id_after
            == rollback.self_state_record_id_before
        ),
        "head_revision_advanced_append_only": (
            roll_forward.head_revision_after == rollback.head_revision_before + 2
        ),
        "package_133_history_equivalent": (
            rollback.package_133_tree_sha256_before
            == roll_forward.package_133_tree_sha256_after
        ),
        "memory_equivalent": True,
        "perception_history_equivalent": True,
        "drive_trace_equivalent": True,
        "drive_modulation_neutral": True,
        "attention_equivalent": True,
        "thought_engine_equivalent": True,
        "action_equivalent": True,
        "output_equivalent": True,
        "readback_requires_new_authorization": True,
        "only_head_selection_and_audit_surfaces_differ": True,
        "comparison_status": "equivalent_except_authorized_head_selection_and_audit",
        "source_record_refs": (
            rollback.commit_receipt_id,
            roll_forward.commit_receipt_id,
            rollback.self_state_record_id_before,
            rollback.self_state_record_id_after,
        ),
    }
    return build_hashed_record(
        SelfStateRollbackCounterfactualComparison,
        payload,
        id_field="comparison_id",
        hash_field="comparison_sha256",
        prefix="self_state_rollback_comparison",
    )


def _build_no_fork_guard(
    *,
    rollback_receipt: SelfStateHeadSelectionCommitReceipt,
    rolled_back_head: ActiveSelfStateHeadRecord,
    canonical_leaf: PersistentSelfStateRecord,
    mutation_block_reason: str,
    recovery_block_reason: str,
) -> SelfStateRollbackNoForkGuardRecord:
    payload = {
        "no_fork_guard_id": "",
        "no_fork_guard_sha256": "",
        "schema_version": NO_FORK_SCHEMA_VERSION,
        "created_at": utc_now(),
        "rollback_receipt_ref": rollback_receipt.commit_receipt_id,
        "rolled_back_active_head_sha256": rolled_back_head.active_head_sha256,
        "rolled_back_head_revision": rolled_back_head.head_revision,
        "selected_ancestor_self_state_record_id": rolled_back_head.self_state_record_id,
        "preserved_canonical_leaf_self_state_record_id": canonical_leaf.self_state_record_id,
        "package_137_mutation_preflight_blocked": True,
        "mutation_block_reason": mutation_block_reason,
        "package_134_recovery_resolution_blocked": True,
        "recovery_block_reason": recovery_block_reason,
        "new_successor_from_selected_ancestor_allowed": False,
        "automatic_rebase_allowed": False,
        "exact_roll_forward_required": True,
        "identity_fork_created": False,
        "guard_status": "ancestor_selected_mutation_and_recovery_blocked_until_exact_roll_forward",
        "source_record_refs": (
            rollback_receipt.commit_receipt_id,
            rolled_back_head.active_head_id,
            rolled_back_head.self_state_record_id,
            canonical_leaf.self_state_record_id,
        ),
    }
    return build_hashed_record(
        SelfStateRollbackNoForkGuardRecord,
        payload,
        id_field="no_fork_guard_id",
        hash_field="no_fork_guard_sha256",
        prefix="self_state_rollback_no_fork_guard",
    )


def _proof_matches_head(
    proof: SelfStateAncestorProofRecord,
    head: ActiveSelfStateHeadRecord,
) -> bool:
    return all(
        (
            proof.current_active_head_id == head.active_head_id,
            proof.current_active_head_sha256 == head.active_head_sha256,
            proof.current_head_revision == head.head_revision,
            proof.current_self_state_record_id == head.self_state_record_id,
            proof.current_self_state_sha256 == head.self_state_sha256,
        )
    )


def _state_by_id(
    source: Package133SourceBundle,
    record_id: str,
) -> PersistentSelfStateRecord:
    matches = tuple(item for item in source.states if item.self_state_record_id == record_id)
    if len(matches) != 1:
        raise RuntimeError("blocked_self_state_target_missing_or_ambiguous")
    return matches[0]


def _single_record_id(
    store: Package139SelfStateRollbackStore,
    table: str,
    key: str,
) -> str:
    records = store.list_payloads(table)
    if len(records) != 1:
        raise RuntimeError(f"blocked_package_139_{table}_missing_or_ambiguous")
    return str(records[0][key])


def _safe_head(store: PersistentSessionRecoveryStore) -> ActiveSelfStateHeadRecord | None:
    try:
        return store.get_active_head()
    except RuntimeError:
        return None


def _head_from_authorization(
    authorization: SelfStateHeadSelectionAuthorizationRecord,
    state: PersistentSelfStateRecord,
) -> _HeadReceiptView:
    return _HeadReceiptView(
        active_head_id=authorization.expected_active_head_id,
        active_head_sha256=authorization.expected_active_head_sha256,
        head_revision=authorization.expected_head_revision,
        self_state_record_id=state.self_state_record_id,
        self_state_sha256=state.self_state_sha256,
        self_state_version=state.self_state_version,
    )


@dataclass(frozen=True)
class _HeadReceiptView:
    active_head_id: str
    active_head_sha256: str
    head_revision: int
    self_state_record_id: str
    self_state_sha256: str
    self_state_version: int


def _tuple_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    for key, value in tuple(result.items()):
        if isinstance(value, list):
            result[key] = tuple(value)
    return result


def _validate_external_roots(
    repo_root: Path,
    output: Path,
    *sources: Path,
) -> None:
    roots = (output, *sources)
    if len(set(roots)) != len(roots):
        raise ValueError("Package 139 state and authority roots must be distinct")
    if _is_within(output, repo_root):
        raise ValueError("Package 139 state_dir must be external to the repository")
    if any(_is_within(source, repo_root) for source in sources):
        raise ValueError("Package 139 authority evidence must remain external")


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
