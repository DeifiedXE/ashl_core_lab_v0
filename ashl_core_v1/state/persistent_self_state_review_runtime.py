"""Package 137 exact teacher-reviewed immutable successor runtime."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import fields
from pathlib import Path
from tempfile import gettempdir
from typing import Any, TypeVar

from ashl_core_v1.runtime.host_sensor_types import (
    monotonic_ns,
    sha256_payload,
    stable_id,
    utc_now,
)
from ashl_core_v1.state.package_134_package_133_source import (
    Package133SourceBundle,
    load_package_133_source_read_only,
    package_133_source_tree_sha256,
)
from ashl_core_v1.state.package_137_self_state_review_store import (
    Package137SelfStateReviewStore,
)
from ashl_core_v1.state.persistent_self_state_boundary import (
    load_authoritative_self_state_contract,
)
from ashl_core_v1.state.persistent_self_state_lineage import (
    build_self_state_lineage_validation_record,
    build_successor_self_state_records,
)
from ashl_core_v1.state.persistent_self_state_review_authority import (
    build_existing_teacher_review_authority_binding,
    teacher_identity_allowed,
)
from ashl_core_v1.state.persistent_self_state_review_types import (
    ACTIVE_HEAD_AUTHORITY,
    ALLOWED_REVIEW_DECISIONS,
    BASELINE_COMMIT,
    BLOCKED_ATTEMPT_SCHEMA_VERSION,
    CAS_OPERATION,
    CHANGED_PERSISTENT_FIELDS,
    DELTA_SCHEMA_VERSION,
    INTENT_SCHEMA_VERSION,
    INVARIANCE_SCHEMA_VERSION,
    PACKAGE_133_PASS_STATUS,
    PACKAGE_134_PASS_STATUS,
    PACKAGE_136_PASS_STATUS,
    PRESERVED_PERSISTENT_FIELDS,
    PROCESS_SCHEMA_VERSION,
    PROPOSAL_SCHEMA_VERSION,
    RECEIPT_SCHEMA_VERSION,
    REVIEW_SCHEMA_VERSION,
    SelfStateMutationBlockedAttemptRecord,
    SelfStateMutationCommitIntentRecord,
    SelfStateMutationCommitReceipt,
    SelfStateMutationProcessReceipt,
    SelfStateMutationTeacherReviewRecord,
    SelfStateReviewInvarianceRecord,
    SelfStateSuccessorDeltaRecord,
    SelfStateSuccessorProposalRecord,
)
from ashl_core_v1.state.persistent_self_state_schema import (
    ALLOWED_PERSISTENT_FIELDS,
    PersistentSelfStateRecord,
)
from ashl_core_v1.state.persistent_self_state_store import PersistentSelfStateStore
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


T = TypeVar("T")


def preflight_self_state_review_gate(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    state_dir: str | Path,
) -> dict[str, Any]:
    root = Path(ashl_root).resolve()
    p133_root = Path(package_133_state_dir).resolve()
    p134_root = Path(package_134_state_dir).resolve()
    output = Path(state_dir).resolve()
    _validate_external_roots(root, output, p133_root, p134_root)
    source = load_package_133_source_read_only(p133_root)
    p133_store = PersistentSelfStateStore(p133_root)
    p134_store = PersistentSessionRecoveryStore(p134_root)
    p137_store = Package137SelfStateReviewStore(output)
    p133_integrity = p133_store.audit_integrity()
    p134_integrity = p134_store.audit_integrity()
    p137_integrity = p137_store.audit_integrity()
    head = p134_store.get_active_head()
    p134_audits = tuple(
        item
        for item in p134_store.list_payloads("package_134_audits")
        if item.get("audit_status") == PACKAGE_134_PASS_STATUS
    )
    if not p134_audits:
        raise RuntimeError("blocked_package_134_passed_audit_missing")
    if source.package_133_audit.get("audit_status") != PACKAGE_133_PASS_STATUS:
        raise RuntimeError("blocked_package_133_passed_audit_missing")
    if not all((p133_integrity["valid"], p134_integrity["valid"], p137_integrity["valid"])):
        raise RuntimeError("blocked_self_state_review_store_integrity_failure")
    if head.active_head_authority != ACTIVE_HEAD_AUTHORITY:
        raise RuntimeError("blocked_package_134_active_head_authority_mismatch")
    exact = _head_matches_state(head, source.leaf)
    if not exact:
        raise RuntimeError("blocked_cross_authority_partial_or_ambiguous_state")
    teacher_binding = build_existing_teacher_review_authority_binding(root)
    try:
        stored_binding = _record_from_payload(
            type(teacher_binding),
            p137_store.get_payload(
                "teacher_authority_bindings", teacher_binding.authority_binding_id
            ),
        )
    except KeyError:
        p137_store.append_once("teacher_authority_bindings", teacher_binding)
    else:
        if stored_binding.authority_binding_sha256 != teacher_binding.authority_binding_sha256:
            raise RuntimeError("blocked_existing_teacher_authority_binding_changed")
        teacher_binding = stored_binding
    registry = _load_registry(root)
    package_136_verified = bool(
        registry.get("current_package_id") in {"136", "137", "138", "139", "140", "141", "142", "143", "144"}
        and registry.get("package_status", {}).get("136") == "completed"
    )
    if not package_136_verified:
        raise RuntimeError("blocked_package_136_baseline_not_completed")
    return {
        "baseline_commit": BASELINE_COMMIT,
        "source": source,
        "head": head,
        "package_133_audit_id": source.package_133_audit["audit_id"],
        "package_133_audit_status": source.package_133_audit["audit_status"],
        "package_134_audit_id": p134_audits[-1]["audit_id"],
        "package_134_audit_status": p134_audits[-1]["audit_status"],
        "package_136_audit_status": PACKAGE_136_PASS_STATUS,
        "package_136_baseline_verified": package_136_verified,
        "teacher_authority_binding": teacher_binding,
        "active_head_matches_package_133_leaf": exact,
        "state_dir_is_external": not _is_within(output, root),
        "readiness": "ready_for_exact_teacher_reviewed_structural_successor",
    }


def create_self_state_successor_proposal(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    state_dir: str | Path,
    proposed_source_session_id: str,
    proposer_process_instance_id: str,
    created_at: str | None = None,
) -> dict[str, Any]:
    preflight = preflight_self_state_review_gate(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        state_dir=state_dir,
    )
    source: Package133SourceBundle = preflight["source"]
    parent = source.leaf
    head: ActiveSelfStateHeadRecord = preflight["head"]
    if not proposed_source_session_id or not proposer_process_instance_id:
        raise ValueError("Package 137 proposal session and process identity are required")
    if proposed_source_session_id == parent.source_session_id:
        raise ValueError("Package 137 successor requires distinct session provenance")
    if f"session:{proposed_source_session_id}" in parent.session_provenance_refs:
        raise ValueError("Package 137 cannot reuse prior session provenance")
    contract = load_authoritative_self_state_contract(ashl_root)
    child_created_at = created_at or utc_now()
    child, transition = build_successor_self_state_records(
        parent=parent,
        contract=contract,
        source_session_id=proposed_source_session_id,
        created_at=child_created_at,
    )
    delta = _build_delta(
        parent=parent,
        contract_ref=contract.contract_id,
        source_session_id=proposed_source_session_id,
        created_at=child_created_at,
    )
    proposal_payload: dict[str, Any] = {
        "proposal_id": "",
        "proposal_sha256": "",
        "schema_version": PROPOSAL_SCHEMA_VERSION,
        "created_at": child_created_at,
        "proposer_process_instance_id": proposer_process_instance_id,
        "proposed_source_session_id": proposed_source_session_id,
        "representation_contract_ref": contract.contract_id,
        "expected_active_head_id": head.active_head_id,
        "expected_active_head_sha256": head.active_head_sha256,
        "expected_head_revision": head.head_revision,
        "expected_bound_session_id": head.bound_session_id,
        "parent_self_state_record_id": parent.self_state_record_id,
        "parent_self_state_sha256": parent.self_state_sha256,
        "self_state_lineage_id": parent.self_state_lineage_id,
        "delta_ref": delta.delta_id,
        "delta_sha256": delta.delta_sha256,
        "proposed_child_created_at": child.created_at,
        "proposed_child_self_state_record_id": child.self_state_record_id,
        "proposed_child_self_state_sha256": child.self_state_sha256,
        "proposed_transition_id": transition.transition_id,
        "proposed_transition_sha256": transition.transition_sha256,
        "proposal_requires_teacher_review": True,
        "parent_or_head_modified": False,
        "successor_appended": False,
        "active_head_changed": False,
        "runtime_behavior_influence_created": False,
        "proposal_status": "pending_exact_teacher_review",
        "source_record_refs": (
            contract.contract_id,
            head.active_head_id,
            parent.self_state_record_id,
            delta.delta_id,
            child.self_state_record_id,
            transition.transition_id,
        ),
    }
    proposal = _hashed_record(
        SelfStateSuccessorProposalRecord,
        proposal_payload,
        id_field="proposal_id",
        hash_field="proposal_sha256",
        prefix="self_state_successor_proposal",
    )
    store = Package137SelfStateReviewStore(state_dir)
    store.append_once("self_state_successor_deltas", delta)
    store.append_once("self_state_successor_proposals", proposal)
    return {"delta": delta, "proposal": proposal, "child": child, "transition": transition}


def review_self_state_successor_proposal(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    state_dir: str | Path,
    proposal_id: str,
    decision: str,
    teacher_actor: str,
    teacher_role: str,
    teacher_note: str,
    explicit_teacher_action: bool,
    decision_reason_codes: tuple[str, ...] = ("exact_structural_successor_review",),
) -> dict[str, Any]:
    if decision not in ALLOWED_REVIEW_DECISIONS:
        raise ValueError("Package 137 supports approved, rejected or deferred only")
    if not explicit_teacher_action:
        raise ValueError("blocked_explicit_teacher_action_missing")
    if not teacher_identity_allowed(teacher_actor, teacher_role):
        raise ValueError("blocked_invalid_existing_teacher_identity")
    preflight = preflight_self_state_review_gate(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        state_dir=state_dir,
    )
    store = Package137SelfStateReviewStore(state_dir)
    if store.review_exists_for_proposal(proposal_id):
        raise RuntimeError("blocked_proposal_already_reviewed")
    proposal = _record_from_payload(
        SelfStateSuccessorProposalRecord,
        store.get_payload("self_state_successor_proposals", proposal_id),
    )
    delta = _record_from_payload(
        SelfStateSuccessorDeltaRecord,
        store.get_payload("self_state_successor_deltas", proposal.delta_ref),
    )
    head: ActiveSelfStateHeadRecord = preflight["head"]
    source: Package133SourceBundle = preflight["source"]
    _require_proposal_current(proposal, delta, head, source.leaf)
    binding = preflight["teacher_authority_binding"]
    tree_before = package_133_source_tree_sha256(package_133_state_dir)
    head_before = head
    review_payload: dict[str, Any] = {
        "review_id": "",
        "review_sha256": "",
        "schema_version": REVIEW_SCHEMA_VERSION,
        "created_at": utc_now(),
        "proposal_id": proposal.proposal_id,
        "proposal_sha256": proposal.proposal_sha256,
        "teacher_authority_binding_ref": binding.authority_binding_id,
        "decision": decision,
        "teacher_actor": teacher_actor,
        "teacher_role": teacher_role,
        "teacher_note": teacher_note,
        "decision_reason_codes": decision_reason_codes,
        "explicit_teacher_action": True,
        "exact_target_binding": True,
        "expected_active_head_id": proposal.expected_active_head_id,
        "expected_active_head_sha256": proposal.expected_active_head_sha256,
        "expected_head_revision": proposal.expected_head_revision,
        "parent_self_state_record_id": proposal.parent_self_state_record_id,
        "parent_self_state_sha256": proposal.parent_self_state_sha256,
        "delta_ref": proposal.delta_ref,
        "delta_sha256": proposal.delta_sha256,
        "proposed_child_self_state_record_id": proposal.proposed_child_self_state_record_id,
        "proposed_child_self_state_sha256": proposal.proposed_child_self_state_sha256,
        "one_use_only": True,
        "automatic_teacher_decision_created": False,
        "learning_approval_scope_used": False,
        "memory_write_authorized": False,
        "runtime_behavior_influence_authorized": False,
        "review_status": {
            "approved": "approved_exact_successor_only",
            "rejected": "rejected_no_authority_change",
            "deferred": "deferred_no_authority_change",
        }[decision],
        "source_record_refs": (
            binding.authority_binding_id,
            proposal.proposal_id,
            delta.delta_id,
            head.active_head_id,
            source.leaf.self_state_record_id,
        ),
    }
    review = _hashed_record(
        SelfStateMutationTeacherReviewRecord,
        review_payload,
        id_field="review_id",
        hash_field="review_sha256",
        prefix="self_state_teacher_review",
    )
    store.append_once("self_state_teacher_reviews", review)
    result: dict[str, Any] = {"review": review}
    if decision in {"rejected", "deferred"}:
        tree_after = package_133_source_tree_sha256(package_133_state_dir)
        head_after = PersistentSessionRecoveryStore(package_134_state_dir).get_active_head()
        invariance = _build_invariance(
            proposal=proposal,
            review=review,
            tree_before=tree_before,
            tree_after=tree_after,
            head_before=head_before,
            head_after=head_after,
        )
        store.append_once("self_state_review_invariance_records", invariance)
        result["invariance"] = invariance
    return result


def commit_approved_self_state_successor(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    state_dir: str | Path,
    review_id: str,
    process_instance_id: str,
    allow_self_state_mutation: bool,
    fault_injection: str | None = None,
) -> dict[str, Any]:
    started = monotonic_ns()
    pid = os.getpid()
    store = Package137SelfStateReviewStore(state_dir)
    if not allow_self_state_mutation:
        return _record_blocked_worker(
            store=store,
            proposal_id="missing_proposal",
            review_id=review_id,
            process_instance_id=process_instance_id,
            pid=pid,
            started=started,
            reason="blocked_self_state_mutation_authorization_missing",
        )
    review = _record_from_payload(
        SelfStateMutationTeacherReviewRecord,
        store.get_payload("self_state_teacher_reviews", review_id),
    )
    proposal = _record_from_payload(
        SelfStateSuccessorProposalRecord,
        store.get_payload("self_state_successor_proposals", review.proposal_id),
    )
    delta = _record_from_payload(
        SelfStateSuccessorDeltaRecord,
        store.get_payload("self_state_successor_deltas", proposal.delta_ref),
    )
    try:
        _require_review_exact(review, proposal, delta)
        if review.decision != "approved":
            raise RuntimeError("blocked_teacher_review_not_approved")
        if store.review_has_commit_receipt(review.review_id):
            raise RuntimeError("blocked_teacher_review_already_consumed")
        p134_store = PersistentSessionRecoveryStore(package_134_state_dir)
        if _p134_review_consumed(p134_store, review.review_id):
            raise RuntimeError("blocked_teacher_review_already_consumed")
        preflight = preflight_self_state_review_gate(
            ashl_root=ashl_root,
            package_133_state_dir=package_133_state_dir,
            package_134_state_dir=package_134_state_dir,
            state_dir=state_dir,
        )
        source: Package133SourceBundle = preflight["source"]
        head: ActiveSelfStateHeadRecord = preflight["head"]
        _require_proposal_current(proposal, delta, head, source.leaf)
        contract = load_authoritative_self_state_contract(ashl_root)
        child, transition = build_successor_self_state_records(
            parent=source.leaf,
            contract=contract,
            source_session_id=proposal.proposed_source_session_id,
            created_at=proposal.proposed_child_created_at,
        )
        validation = build_self_state_lineage_validation_record(
            parent=source.leaf,
            child=child,
            transition=transition,
        )
        _require_rebuilt_successor_exact(proposal, child, transition)
        intent = _build_commit_intent(
            proposal=proposal,
            review=review,
            child=child,
            transition=transition,
        )
        store.append_once("self_state_mutation_commit_intents", intent)
        p133_store = PersistentSelfStateStore(package_133_state_dir)
        p133_store.append_lineage_chain(
            parent=source.leaf,
            child=child,
            transition=transition,
            validation=validation,
        )
        if fault_injection == "after_package_133_append_before_package_134_cas":
            raise RuntimeError("simulated_cross_authority_partial_after_package_133_append")
        new_head = _build_reviewed_successor_head(
            expected_head=head,
            child=child,
            proposal=proposal,
            review=review,
            process_instance_id=process_instance_id,
        )
        cas_event = _build_reviewed_successor_cas_event(
            expected_head=head,
            new_head=new_head,
            proposal=proposal,
            review=review,
        )
        p134_fault = None
        if fault_injection == "cas_conflict_after_package_133_append":
            p134_fault = "force_cas_conflict"
        elif fault_injection == "after_head_update_before_commit":
            p134_fault = "after_head_update_before_commit"
        p134_store.advance_reviewed_successor_atomic(
            review_id=review.review_id,
            expected_head=head,
            new_head=new_head,
            cas_event=cas_event,
            fault_injection=p134_fault,
        )
        receipt = _build_success_receipt(
            intent=intent,
            proposal=proposal,
            review=review,
            child=child,
            transition=transition,
            validation_id=validation.lineage_validation_id,
            head_before=head,
            head_after=new_head,
            cas_event_id=cas_event.cas_event_id,
        )
        store.append_once("self_state_mutation_commit_receipts", receipt)
        ended = max(monotonic_ns(), started + 1)
        process = _build_process_receipt(
            process_instance_id=process_instance_id,
            pid=pid,
            started=started,
            ended=ended,
            proposal_id=proposal.proposal_id,
            review_id=review.review_id,
            commit_receipt_ref=receipt.commit_receipt_id,
            worker_status="approved_successor_committed_by_package_133_then_package_134_cas",
            source_refs=(receipt.commit_receipt_id, cas_event.cas_event_id),
        )
        store.append_once("self_state_mutation_process_receipts", process)
        return {
            "status": "committed_reviewed_self_state_successor",
            "proposal": proposal,
            "review": review,
            "child": child,
            "transition": transition,
            "validation": validation,
            "active_head_before": head,
            "active_head_after": new_head,
            "cas_event": cas_event,
            "commit_receipt": receipt,
            "process_receipt": process,
        }
    except (ActiveHeadCASConflict, KeyError, RuntimeError, TypeError, ValueError) as error:
        reason = str(error)
        p134_store = PersistentSessionRecoveryStore(package_134_state_dir)
        try:
            observed = p134_store.get_active_head()
        except RuntimeError:
            observed = None
        p133_appended = _proposal_child_exists(package_133_state_dir, proposal)
        partial = p133_appended and not bool(
            observed and observed.self_state_record_id == proposal.proposed_child_self_state_record_id
        )
        blocked = _build_blocked_attempt(
            proposal=proposal,
            review=review,
            reason=reason,
            observed_head=observed,
            p133_appended=p133_appended,
            p134_advanced=bool(
                observed and observed.self_state_record_id == proposal.proposed_child_self_state_record_id
            ),
            partial=partial,
        )
        store.append_once("self_state_mutation_blocked_attempts", blocked)
        ended = max(monotonic_ns(), started + 1)
        process = _build_process_receipt(
            process_instance_id=process_instance_id,
            pid=pid,
            started=started,
            ended=ended,
            proposal_id=proposal.proposal_id,
            review_id=review.review_id,
            commit_receipt_ref=None,
            worker_status="blocked_without_guessing_or_rebase",
            source_refs=(blocked.blocked_attempt_id,),
        )
        store.append_once("self_state_mutation_process_receipts", process)
        return {"status": "blocked", "blocked_attempt": blocked, "process_receipt": process}


def run_commit_worker_subprocess(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    state_dir: str | Path,
    review_id: str,
    process_instance_id: str,
    allow_self_state_mutation: bool,
) -> dict[str, Any]:
    command = (
        sys.executable,
        "-B",
        "-m",
        "ashl_core_v1.state.package_137_self_state_review_worker",
        "--ashl-root",
        str(Path(ashl_root).resolve()),
        "--package-133-state-dir",
        str(Path(package_133_state_dir).resolve()),
        "--package-134-state-dir",
        str(Path(package_134_state_dir).resolve()),
        "--state-dir",
        str(Path(state_dir).resolve()),
        "--review-id",
        review_id,
        "--process-instance-id",
        process_instance_id,
    )
    if allow_self_state_mutation:
        command += ("--allow-self-state-mutation",)
    environment = dict(os.environ)
    cache_root = Path(gettempdir()) / "ashl_package_137_pycache"
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
        raise RuntimeError(
            "blocked_package_137_commit_worker_failed:"
            + (result.stderr.strip() or result.stdout.strip() or str(result.returncode))
        )
    lines = tuple(line for line in result.stdout.splitlines() if line.strip())
    if not lines:
        raise RuntimeError("blocked_package_137_commit_worker_output_missing")
    return json.loads(lines[-1])


def run_real_persistent_self_state_review_gate(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    state_dir: str | Path,
    teacher_actor: str,
    teacher_role: str,
    teacher_note: str,
    confirm_teacher_approval: bool,
    allow_self_state_mutation: bool,
) -> dict[str, Any]:
    """Create reject/defer evidence, then commit one explicitly approved successor."""
    if not confirm_teacher_approval:
        raise RuntimeError("blocked_explicit_teacher_approval_confirmation_missing")
    if not allow_self_state_mutation:
        raise RuntimeError("blocked_self_state_mutation_authorization_missing")
    if not teacher_note.strip():
        raise ValueError("Package 137 teacher note is required")
    preflight = preflight_self_state_review_gate(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        state_dir=state_dir,
    )
    store = Package137SelfStateReviewStore(state_dir)
    if any(
        store.count(table)
        for table in (
            "self_state_successor_proposals",
            "self_state_teacher_reviews",
            "self_state_mutation_commit_intents",
            "self_state_mutation_commit_receipts",
            "package_137_audits",
        )
    ):
        raise RuntimeError("blocked_package_137_real_state_dir_not_fresh")

    rejected = create_self_state_successor_proposal(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        state_dir=state_dir,
        proposed_source_session_id=stable_id("package_137_rejected_successor_session"),
        proposer_process_instance_id=stable_id("package_137_rejected_proposer"),
    )
    rejected_review = review_self_state_successor_proposal(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        state_dir=state_dir,
        proposal_id=rejected["proposal"].proposal_id,
        decision="rejected",
        teacher_actor=teacher_actor,
        teacher_role=teacher_role,
        teacher_note="Rejected Package 137 structural successor boundary proof.",
        explicit_teacher_action=True,
        decision_reason_codes=("explicit_rejection_invariance_verification",),
    )
    deferred = create_self_state_successor_proposal(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        state_dir=state_dir,
        proposed_source_session_id=stable_id("package_137_deferred_successor_session"),
        proposer_process_instance_id=stable_id("package_137_deferred_proposer"),
    )
    deferred_review = review_self_state_successor_proposal(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        state_dir=state_dir,
        proposal_id=deferred["proposal"].proposal_id,
        decision="deferred",
        teacher_actor=teacher_actor,
        teacher_role=teacher_role,
        teacher_note="Deferred Package 137 structural successor boundary proof.",
        explicit_teacher_action=True,
        decision_reason_codes=("explicit_deferral_invariance_verification",),
    )
    approved = create_self_state_successor_proposal(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        state_dir=state_dir,
        proposed_source_session_id=stable_id("package_137_approved_successor_session"),
        proposer_process_instance_id=stable_id("package_137_approved_proposer"),
    )
    approved_review = review_self_state_successor_proposal(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        state_dir=state_dir,
        proposal_id=approved["proposal"].proposal_id,
        decision="approved",
        teacher_actor=teacher_actor,
        teacher_role=teacher_role,
        teacher_note=teacher_note,
        explicit_teacher_action=True,
        decision_reason_codes=("approve_exact_package_133_structural_successor_only",),
    )
    process_instance_id = stable_id("package_137_approved_commit_worker")
    committed = run_commit_worker_subprocess(
        ashl_root=ashl_root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        state_dir=state_dir,
        review_id=approved_review["review"].review_id,
        process_instance_id=process_instance_id,
        allow_self_state_mutation=True,
    )
    if committed.get("status") != "committed_reviewed_self_state_successor":
        raise RuntimeError("blocked_package_137_real_successor_commit")
    source_after = load_package_133_source_read_only(package_133_state_dir)
    head_after = PersistentSessionRecoveryStore(package_134_state_dir).get_active_head()
    if not _head_matches_state(head_after, source_after.leaf):
        raise RuntimeError("blocked_package_137_real_cross_authority_commit_incomplete")
    return {
        "status": "completed_real_teacher_reviewed_self_state_successor_run",
        "preflight": preflight,
        "rejected_proposal": rejected["proposal"],
        "rejected_review": rejected_review["review"],
        "rejected_invariance": rejected_review["invariance"],
        "deferred_proposal": deferred["proposal"],
        "deferred_review": deferred_review["review"],
        "deferred_invariance": deferred_review["invariance"],
        "approved_proposal": approved["proposal"],
        "approved_review": approved_review["review"],
        "commit_worker_result": committed,
        "active_head_after": head_after,
        "self_state_leaf_after": source_after.leaf,
    }


def _build_delta(
    *,
    parent: PersistentSelfStateRecord,
    contract_ref: str,
    source_session_id: str,
    created_at: str,
) -> SelfStateSuccessorDeltaRecord:
    payload: dict[str, Any] = {
        "delta_id": "",
        "delta_sha256": "",
        "schema_version": DELTA_SCHEMA_VERSION,
        "created_at": created_at,
        "representation_contract_ref": contract_ref,
        "self_state_lineage_id": parent.self_state_lineage_id,
        "parent_self_state_record_id": parent.self_state_record_id,
        "parent_self_state_sha256": parent.self_state_sha256,
        "from_self_state_version": parent.self_state_version,
        "to_self_state_version": parent.self_state_version + 1,
        "from_lineage_generation": parent.lineage_generation,
        "to_lineage_generation": parent.lineage_generation + 1,
        "changed_persistent_fields": CHANGED_PERSISTENT_FIELDS,
        "preserved_persistent_fields": PRESERVED_PERSISTENT_FIELDS,
        "complete_persistent_field_allowlist": ALLOWED_PERSISTENT_FIELDS,
        "representation_status_before": parent.representation_status,
        "representation_status_after": parent.representation_status,
        "governance_profile_before": parent.governance_profile_version,
        "governance_profile_after": parent.governance_profile_version,
        "proposed_source_session_id": source_session_id,
        "semantic_content_added": False,
        "memory_content_added": False,
        "perception_content_added": False,
        "drive_or_modulation_content_added": False,
        "output_content_added": False,
        "runtime_behavior_authority_added": False,
        "delta_status": "proposed_exact_structural_successor_delta",
        "source_record_refs": (contract_ref, parent.self_state_record_id),
    }
    return _hashed_record(
        SelfStateSuccessorDeltaRecord,
        payload,
        id_field="delta_id",
        hash_field="delta_sha256",
        prefix="self_state_successor_delta",
    )


def _build_commit_intent(
    *,
    proposal: SelfStateSuccessorProposalRecord,
    review: SelfStateMutationTeacherReviewRecord,
    child: PersistentSelfStateRecord,
    transition: Any,
) -> SelfStateMutationCommitIntentRecord:
    payload = {
        "commit_intent_id": "",
        "commit_intent_sha256": "",
        "schema_version": INTENT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "proposal_id": proposal.proposal_id,
        "review_id": review.review_id,
        "delta_ref": proposal.delta_ref,
        "expected_active_head_id": proposal.expected_active_head_id,
        "expected_active_head_sha256": proposal.expected_active_head_sha256,
        "expected_head_revision": proposal.expected_head_revision,
        "parent_self_state_record_id": proposal.parent_self_state_record_id,
        "parent_self_state_sha256": proposal.parent_self_state_sha256,
        "child_self_state_record_id": child.self_state_record_id,
        "child_self_state_sha256": child.self_state_sha256,
        "transition_id": transition.transition_id,
        "transition_sha256": transition.transition_sha256,
        "commit_order": (
            "append_package_133_immutable_successor",
            "advance_package_134_active_head_exact_cas",
            "append_package_137_commit_receipt",
        ),
        "automatic_rebase_allowed": False,
        "in_place_parent_mutation_allowed": False,
        "rollback_hides_history": False,
        "intent_status": "pending_exact_cross_authority_commit",
        "source_record_refs": (
            proposal.proposal_id,
            review.review_id,
            proposal.parent_self_state_record_id,
            child.self_state_record_id,
        ),
    }
    return _hashed_record(
        SelfStateMutationCommitIntentRecord,
        payload,
        id_field="commit_intent_id",
        hash_field="commit_intent_sha256",
        prefix="self_state_mutation_commit_intent",
    )


def _build_reviewed_successor_head(
    *,
    expected_head: ActiveSelfStateHeadRecord,
    child: PersistentSelfStateRecord,
    proposal: SelfStateSuccessorProposalRecord,
    review: SelfStateMutationTeacherReviewRecord,
    process_instance_id: str,
) -> ActiveSelfStateHeadRecord:
    payload: dict[str, Any] = {
        "active_head_id": expected_head.active_head_id,
        "active_head_sha256": "",
        "schema_version": HEAD_SCHEMA_VERSION,
        "created_at": expected_head.created_at,
        "updated_at": utc_now(),
        "self_state_lineage_id": child.self_state_lineage_id,
        "self_state_record_id": child.self_state_record_id,
        "self_state_sha256": child.self_state_sha256,
        "self_state_version": child.self_state_version,
        "lineage_generation": child.lineage_generation,
        "head_revision": expected_head.head_revision + 1,
        "bound_session_id": proposal.proposed_source_session_id,
        "bound_process_instance_id": process_instance_id,
        "previous_active_head_sha256": expected_head.active_head_sha256,
        "authority_status": "active_identity_binding",
        "representation_authority": REPRESENTATION_AUTHORITY,
        "active_head_authority": PACKAGE_134_ACTIVE_HEAD_AUTHORITY,
        "source_record_refs": (
            *expected_head.source_record_refs,
            proposal.proposal_id,
            review.review_id,
            child.self_state_record_id,
        ),
    }
    identity = dict(payload)
    identity.pop("active_head_sha256")
    payload["active_head_sha256"] = sha256_payload(identity)
    return ActiveSelfStateHeadRecord(**payload)


def _build_reviewed_successor_cas_event(
    *,
    expected_head: ActiveSelfStateHeadRecord,
    new_head: ActiveSelfStateHeadRecord,
    proposal: SelfStateSuccessorProposalRecord,
    review: SelfStateMutationTeacherReviewRecord,
) -> ActiveHeadCASEventRecord:
    identity = {
        "review": review.review_id,
        "expected": expected_head.active_head_sha256,
        "new": new_head.active_head_sha256,
        "operation": CAS_OPERATION,
    }
    return ActiveHeadCASEventRecord(
        cas_event_id=f"active_head_cas_event:{sha256_payload(identity)[:16]}",
        schema_version=CAS_SCHEMA_VERSION,
        created_at=utc_now(),
        authorization_id=review.review_id,
        operation=CAS_OPERATION,
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
            proposal.proposal_id,
            review.review_id,
            expected_head.self_state_record_id,
            new_head.self_state_record_id,
        ),
    )


def _build_success_receipt(
    *,
    intent: SelfStateMutationCommitIntentRecord,
    proposal: SelfStateSuccessorProposalRecord,
    review: SelfStateMutationTeacherReviewRecord,
    child: PersistentSelfStateRecord,
    transition: Any,
    validation_id: str,
    head_before: ActiveSelfStateHeadRecord,
    head_after: ActiveSelfStateHeadRecord,
    cas_event_id: str,
) -> SelfStateMutationCommitReceipt:
    payload = {
        "commit_receipt_id": "",
        "commit_receipt_sha256": "",
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "commit_intent_id": intent.commit_intent_id,
        "proposal_id": proposal.proposal_id,
        "review_id": review.review_id,
        "decision": review.decision,
        "parent_self_state_record_id": proposal.parent_self_state_record_id,
        "parent_self_state_sha256": proposal.parent_self_state_sha256,
        "child_self_state_record_id": child.self_state_record_id,
        "child_self_state_sha256": child.self_state_sha256,
        "transition_id": transition.transition_id,
        "lineage_validation_id": validation_id,
        "active_head_id": head_before.active_head_id,
        "active_head_before_sha256": head_before.active_head_sha256,
        "active_head_after_sha256": head_after.active_head_sha256,
        "head_revision_before": head_before.head_revision,
        "head_revision_after": head_after.head_revision,
        "package_134_cas_event_id": cas_event_id,
        "package_133_successor_appended": True,
        "package_134_active_head_advanced": True,
        "review_consumed_once": True,
        "cross_authority_commit_complete": True,
        "partial_failure_detected": False,
        "authoritative_state_changed": True,
        "parent_modified_in_place": False,
        "automatic_rebase_performed": False,
        "runtime_behavior_influence_created": False,
        "memory_write_created": False,
        "drive_persisted": False,
        "output_created": False,
        "commit_status": "committed_reviewed_self_state_successor",
        "failure_reason": None,
        "source_record_refs": (
            intent.commit_intent_id,
            proposal.proposal_id,
            review.review_id,
            child.self_state_record_id,
            transition.transition_id,
            validation_id,
            cas_event_id,
        ),
    }
    return _hashed_record(
        SelfStateMutationCommitReceipt,
        payload,
        id_field="commit_receipt_id",
        hash_field="commit_receipt_sha256",
        prefix="self_state_mutation_commit_receipt",
    )


def _build_invariance(
    *,
    proposal: SelfStateSuccessorProposalRecord,
    review: SelfStateMutationTeacherReviewRecord,
    tree_before: str,
    tree_after: str,
    head_before: ActiveSelfStateHeadRecord,
    head_after: ActiveSelfStateHeadRecord,
) -> SelfStateReviewInvarianceRecord:
    payload = {
        "invariance_id": "",
        "invariance_sha256": "",
        "schema_version": INVARIANCE_SCHEMA_VERSION,
        "created_at": utc_now(),
        "proposal_id": proposal.proposal_id,
        "review_id": review.review_id,
        "decision": review.decision,
        "package_133_tree_sha256_before": tree_before,
        "package_133_tree_sha256_after": tree_after,
        "active_head_sha256_before": head_before.active_head_sha256,
        "active_head_sha256_after": head_after.active_head_sha256,
        "active_head_revision_before": head_before.head_revision,
        "active_head_revision_after": head_after.head_revision,
        "authoritative_self_state_unchanged": tree_before == tree_after,
        "active_head_unchanged": head_before == head_after,
        "mutation_attempted": False,
        "invariance_status": f"{review.decision}_review_preserved_authoritative_state",
        "source_record_refs": (proposal.proposal_id, review.review_id, head_before.active_head_id),
    }
    return _hashed_record(
        SelfStateReviewInvarianceRecord,
        payload,
        id_field="invariance_id",
        hash_field="invariance_sha256",
        prefix="self_state_review_invariance",
    )


def _build_blocked_attempt(
    *,
    proposal: SelfStateSuccessorProposalRecord,
    review: SelfStateMutationTeacherReviewRecord | None,
    reason: str,
    observed_head: ActiveSelfStateHeadRecord | None,
    p133_appended: bool,
    p134_advanced: bool,
    partial: bool,
) -> SelfStateMutationBlockedAttemptRecord:
    payload = {
        "blocked_attempt_id": "",
        "blocked_attempt_sha256": "",
        "schema_version": BLOCKED_ATTEMPT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "proposal_id": proposal.proposal_id,
        "review_id": review.review_id if review else None,
        "failure_reason": reason,
        "observed_active_head_sha256": observed_head.active_head_sha256 if observed_head else None,
        "observed_head_revision": observed_head.head_revision if observed_head else None,
        "package_133_successor_appended": p133_appended,
        "package_134_active_head_advanced": p134_advanced,
        "partial_failure_detected": partial,
        "automatic_rebase_performed": False,
        "authoritative_state_changed": False,
        "blocked_status": "blocked_without_guessing_or_rebase",
        "source_record_refs": tuple(
            item
            for item in (
                proposal.proposal_id,
                review.review_id if review else None,
                observed_head.active_head_id if observed_head else None,
            )
            if item
        ),
    }
    return _hashed_record(
        SelfStateMutationBlockedAttemptRecord,
        payload,
        id_field="blocked_attempt_id",
        hash_field="blocked_attempt_sha256",
        prefix="self_state_mutation_blocked_attempt",
    )


def _build_process_receipt(
    *,
    process_instance_id: str,
    pid: int,
    started: int,
    ended: int,
    proposal_id: str,
    review_id: str,
    commit_receipt_ref: str | None,
    worker_status: str,
    source_refs: tuple[str, ...],
) -> SelfStateMutationProcessReceipt:
    payload = {
        "process_receipt_id": "",
        "process_receipt_sha256": "",
        "schema_version": PROCESS_SCHEMA_VERSION,
        "created_at": utc_now(),
        "process_instance_id": process_instance_id,
        "operating_system_process_id": pid,
        "started_monotonic_ns": started,
        "ended_monotonic_ns": ended,
        "proposal_id": proposal_id,
        "review_id": review_id,
        "commit_receipt_ref": commit_receipt_ref,
        "worker_status": worker_status,
        "source_record_refs": source_refs,
    }
    return _hashed_record(
        SelfStateMutationProcessReceipt,
        payload,
        id_field="process_receipt_id",
        hash_field="process_receipt_sha256",
        prefix="self_state_mutation_process_receipt",
    )


def _record_blocked_worker(
    *,
    store: Package137SelfStateReviewStore,
    proposal_id: str,
    review_id: str,
    process_instance_id: str,
    pid: int,
    started: int,
    reason: str,
) -> dict[str, Any]:
    ended = max(monotonic_ns(), started + 1)
    process = _build_process_receipt(
        process_instance_id=process_instance_id,
        pid=pid,
        started=started,
        ended=ended,
        proposal_id=proposal_id,
        review_id=review_id,
        commit_receipt_ref=None,
        worker_status=reason,
        source_refs=(review_id,),
    )
    store.append_once("self_state_mutation_process_receipts", process)
    return {"status": "blocked", "failure_reason": reason, "process_receipt": process}


def _require_proposal_current(
    proposal: SelfStateSuccessorProposalRecord,
    delta: SelfStateSuccessorDeltaRecord,
    head: ActiveSelfStateHeadRecord,
    parent: PersistentSelfStateRecord,
) -> None:
    checks = (
        proposal.expected_active_head_id == head.active_head_id,
        proposal.expected_active_head_sha256 == head.active_head_sha256,
        proposal.expected_head_revision == head.head_revision,
        proposal.expected_bound_session_id == head.bound_session_id,
        proposal.parent_self_state_record_id == parent.self_state_record_id,
        proposal.parent_self_state_sha256 == parent.self_state_sha256,
        proposal.self_state_lineage_id == parent.self_state_lineage_id,
        delta.delta_id == proposal.delta_ref,
        delta.delta_sha256 == proposal.delta_sha256,
        delta.parent_self_state_record_id == parent.self_state_record_id,
        delta.parent_self_state_sha256 == parent.self_state_sha256,
    )
    if not all(checks):
        raise RuntimeError("blocked_stale_review_or_exact_parent_head_mismatch")


def _require_review_exact(
    review: SelfStateMutationTeacherReviewRecord,
    proposal: SelfStateSuccessorProposalRecord,
    delta: SelfStateSuccessorDeltaRecord,
) -> None:
    checks = (
        review.proposal_id == proposal.proposal_id,
        review.proposal_sha256 == proposal.proposal_sha256,
        review.expected_active_head_id == proposal.expected_active_head_id,
        review.expected_active_head_sha256 == proposal.expected_active_head_sha256,
        review.expected_head_revision == proposal.expected_head_revision,
        review.parent_self_state_record_id == proposal.parent_self_state_record_id,
        review.parent_self_state_sha256 == proposal.parent_self_state_sha256,
        review.delta_ref == proposal.delta_ref == delta.delta_id,
        review.delta_sha256 == proposal.delta_sha256 == delta.delta_sha256,
        review.proposed_child_self_state_record_id == proposal.proposed_child_self_state_record_id,
        review.proposed_child_self_state_sha256 == proposal.proposed_child_self_state_sha256,
    )
    if not all(checks):
        raise RuntimeError("blocked_teacher_review_exact_target_mismatch")


def _require_rebuilt_successor_exact(
    proposal: SelfStateSuccessorProposalRecord,
    child: PersistentSelfStateRecord,
    transition: Any,
) -> None:
    if not all(
        (
            child.self_state_record_id == proposal.proposed_child_self_state_record_id,
            child.self_state_sha256 == proposal.proposed_child_self_state_sha256,
            transition.transition_id == proposal.proposed_transition_id,
            transition.transition_sha256 == proposal.proposed_transition_sha256,
        )
    ):
        raise RuntimeError("blocked_proposed_successor_reconstruction_mismatch")


def _head_matches_state(head: ActiveSelfStateHeadRecord, state: PersistentSelfStateRecord) -> bool:
    return all(
        (
            head.self_state_lineage_id == state.self_state_lineage_id,
            head.self_state_record_id == state.self_state_record_id,
            head.self_state_sha256 == state.self_state_sha256,
            head.self_state_version == state.self_state_version,
            head.lineage_generation == state.lineage_generation,
        )
    )


def _proposal_child_exists(
    package_133_state_dir: str | Path,
    proposal: SelfStateSuccessorProposalRecord,
) -> bool:
    try:
        payloads = PersistentSelfStateStore(package_133_state_dir).list_payloads(
            "persistent_self_state_records"
        )
    except (RuntimeError, ValueError):
        return False
    return any(
        item.get("self_state_record_id") == proposal.proposed_child_self_state_record_id
        for item in payloads
    )


def _p134_review_consumed(store: PersistentSessionRecoveryStore, review_id: str) -> bool:
    return any(
        item.get("authorization_id") == review_id
        and item.get("operation") == CAS_OPERATION
        for item in store.list_payloads("active_head_cas_events")
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
    identity.pop(id_field)
    identity.pop(hash_field)
    identity.pop("created_at", None)
    digest = sha256_payload(identity)
    payload[hash_field] = digest
    payload[id_field] = f"{prefix}:{digest[:16]}"
    return record_type(**payload)


def _record_from_payload(record_type: type[T], payload: dict[str, Any]) -> T:
    values = dict(payload)
    for item in fields(record_type):
        if "tuple" in str(item.type).lower() and isinstance(values.get(item.name), list):
            values[item.name] = tuple(values[item.name])
    return record_type(**values)


def _load_registry(root: Path) -> dict[str, Any]:
    path = root / "ashl_core_v1/docs/reference/package_number_registry_v0.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_external_roots(root: Path, output: Path, *sources: Path) -> None:
    if _is_within(output, root):
        raise ValueError("Package 137 state_dir must remain outside the repository")
    if any(_is_within(source, root) for source in sources):
        raise ValueError("Package 137 authority stores must remain outside the repository")
    if output in sources or any(left == right for index, left in enumerate(sources) for right in sources[index + 1 :]):
        raise ValueError("Package 137 state and authority roots must be distinct")


def _is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
