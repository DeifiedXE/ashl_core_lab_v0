"""Fresh regressions and evidence-derived final audit for Package 137."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.state.package_134_package_133_source import (
    load_package_133_source_read_only,
)
from ashl_core_v1.state.package_137_self_state_review_store import (
    Package137SelfStateReviewStore,
)
from ashl_core_v1.state.persistent_self_state_review_runtime import (
    _hashed_record,
    _record_from_payload,
    preflight_self_state_review_gate,
)
from ashl_core_v1.state.persistent_self_state_review_types import (
    ACTIVE_HEAD_AUTHORITY,
    AUDIT_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    CAS_OPERATION,
    CHANGED_PERSISTENT_FIELDS,
    PACKAGE_133_PASS_STATUS,
    PACKAGE_134_PASS_STATUS,
    PACKAGE_138_REQUIRED_GATES,
    PASS_STATUS,
    PRESERVED_PERSISTENT_FIELDS,
    REGRESSION_SCHEMA_VERSION,
    SELF_STATE_AUTHORITY,
    Package137PersistentSelfStateReviewGateAudit,
    Package137RegressionReceipt,
    SelfStateMutationCommitReceipt,
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
    PersistentSessionRecoveryStore,
)
from ashl_core_v1.state.persistent_session_recovery_types import (
    ActiveHeadCASEventRecord,
)


_TARGETED_137 = "ashl_core_v1.tests.test_package_137_persistent_self_state_review_gate"
_PACKAGE_133_134 = (
    "ashl_core_v1.tests.test_package_133_cross_session_self_state_schema",
    "ashl_core_v1.tests.test_package_134_persistent_session_recovery_identity",
)
_TEACHER_AUTHORITY = (
    "ashl_core_v1.tests.test_cradle_state_resume_selection_authorization",
    "ashl_core_v1.tests.test_teacher_gated_session_store",
    "ashl_core_v1.tests.test_teacher_gated_session_resume_commit",
)
_PACKAGE_135_136 = (
    "ashl_core_v1.tests.test_package_135_drive_signal_trace_separation",
    "ashl_core_v1.tests.test_package_136_same_session_drive_modulation",
)


def run_package_137_regressions(
    *, ashl_root: str | Path, state_dir: str | Path
) -> Package137RegressionReceipt:
    root = Path(ashl_root).resolve()
    store = Package137SelfStateReviewStore(state_dir)
    pycache = store.root / "regression_pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    commands: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("targeted_package_137", (sys.executable, "-m", "unittest", _TARGETED_137)),
        (
            "package_133_134_regressions",
            (sys.executable, "-m", "unittest", *_PACKAGE_133_134),
        ),
        (
            "teacher_authority_regressions",
            (sys.executable, "-m", "unittest", *_TEACHER_AUTHORITY),
        ),
        (
            "package_135_136_boundary_regressions",
            (sys.executable, "-m", "unittest", *_PACKAGE_135_136),
        ),
        (
            "full_v1_unittest_discover",
            (sys.executable, "-m", "unittest", "discover", "--durations", "20"),
        ),
        ("compileall", (sys.executable, "-m", "compileall", "-q", "ashl_core_v1")),
        ("git_diff_check", ("git", "diff", "--check")),
    )
    results: list[tuple[str, int, str]] = []
    statuses: dict[str, bool] = {}
    for name, command in commands:
        completed = subprocess.run(
            command,
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3600,
            check=False,
        )
        combined = f"{completed.stdout}\n{completed.stderr}"
        results.append((name, completed.returncode, sha256_bytes(combined.encode("utf-8"))))
        statuses[name] = completed.returncode == 0
    source_head = _git_output(root, "rev-parse", "HEAD")
    receipt = Package137RegressionReceipt(
        regression_receipt_id=(
            f"package_137_regressions:{sha256_payload({'head': source_head, 'results': results})[:16]}"
        ),
        schema_version=REGRESSION_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        source_head=source_head,
        command_results=tuple(results),
        targeted_package_137_passed=statuses["targeted_package_137"],
        package_133_134_regressions_passed=statuses["package_133_134_regressions"],
        teacher_authority_regressions_passed=statuses["teacher_authority_regressions"],
        package_135_136_boundary_regressions_passed=statuses[
            "package_135_136_boundary_regressions"
        ],
        full_v1_discover_passed=statuses["full_v1_unittest_discover"],
        compileall_passed=statuses["compileall"],
        git_diff_check_passed=statuses["git_diff_check"],
        pycache_redirected_outside_repo=not _is_within(pycache, root),
        fresh_regressions_passed=all(statuses.values()),
    )
    store.append_once("package_137_regression_receipts", receipt)
    return receipt


def audit_package_137_persistent_self_state_review_gate(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    state_dir: str | Path,
    append: bool = True,
) -> Package137PersistentSelfStateReviewGateAudit:
    root = Path(ashl_root).resolve()
    p133_root = Path(package_133_state_dir).resolve()
    p134_root = Path(package_134_state_dir).resolve()
    before = {
        "package_133": _source_tree_sha256(p133_root),
        "package_134": _source_tree_sha256(p134_root),
    }
    preflight = preflight_self_state_review_gate(
        ashl_root=root,
        package_133_state_dir=p133_root,
        package_134_state_dir=p134_root,
        state_dir=state_dir,
    )
    p137 = Package137SelfStateReviewStore(state_dir)
    p133 = PersistentSelfStateStore(p133_root)
    p134 = PersistentSessionRecoveryStore(p134_root)
    source = load_package_133_source_read_only(p133_root)
    head = p134.get_active_head()
    proposals = tuple(
        _record_from_payload(SelfStateSuccessorProposalRecord, item)
        for item in p137.list_payloads("self_state_successor_proposals")
    )
    deltas = tuple(
        _record_from_payload(SelfStateSuccessorDeltaRecord, item)
        for item in p137.list_payloads("self_state_successor_deltas")
    )
    reviews = tuple(
        _record_from_payload(SelfStateMutationTeacherReviewRecord, item)
        for item in p137.list_payloads("self_state_teacher_reviews")
    )
    invariances = tuple(
        _record_from_payload(SelfStateReviewInvarianceRecord, item)
        for item in p137.list_payloads("self_state_review_invariance_records")
    )
    receipts = tuple(
        _record_from_payload(SelfStateMutationCommitReceipt, item)
        for item in p137.list_payloads("self_state_mutation_commit_receipts")
    )
    controls = p137.latest_payload("package_137_control_results") or {}
    regressions = p137.latest_payload("package_137_regression_receipts") or {}
    binding = preflight["teacher_authority_binding"]
    approved = _one(tuple(item for item in reviews if item.decision == "approved"))
    rejected = _one(tuple(item for item in reviews if item.decision == "rejected"))
    deferred = _one(tuple(item for item in reviews if item.decision == "deferred"))
    receipt = _one(receipts)
    proposal_by_id = {item.proposal_id: item for item in proposals}
    delta_by_id = {item.delta_id: item for item in deltas}
    approved_proposal = proposal_by_id.get(approved.proposal_id) if approved else None
    approved_delta = (
        delta_by_id.get(approved_proposal.delta_ref) if approved_proposal else None
    )
    states = tuple(
        PersistentSelfStateRecord.from_dict(item)
        for item in p133.list_payloads("persistent_self_state_records")
    )
    state_by_id = {item.self_state_record_id: item for item in states}
    parent = state_by_id.get(receipt.parent_self_state_record_id) if receipt else None
    child = state_by_id.get(receipt.child_self_state_record_id) if receipt else None
    cas_events = tuple(
        _record_from_payload(ActiveHeadCASEventRecord, item)
        for item in p134.list_payloads("active_head_cas_events")
    )
    reviewed_cas = _one(
        tuple(
            item
            for item in cas_events
            if approved
            and item.authorization_id == approved.review_id
            and item.operation == CAS_OPERATION
        )
    )
    rejection_invariance = _one(
        tuple(item for item in invariances if rejected and item.review_id == rejected.review_id)
    )
    deferral_invariance = _one(
        tuple(item for item in invariances if deferred and item.review_id == deferred.review_id)
    )
    passed_controls = set(controls.get("passed_control_names") or ())
    store_integrity = p137.audit_integrity()
    p133_integrity = p133.audit_integrity()
    p134_integrity = p134.audit_integrity()
    boundary = _scan_package_137_boundary(root)
    after = {
        "package_133": _source_tree_sha256(p133_root),
        "package_134": _source_tree_sha256(p134_root),
    }

    exact_head = bool(
        child
        and head.self_state_record_id == child.self_state_record_id
        and head.self_state_sha256 == child.self_state_sha256
        and source.leaf.self_state_record_id == child.self_state_record_id
    )
    exact_parent = bool(
        approved
        and approved_proposal
        and approved_delta
        and receipt
        and parent
        and approved.parent_self_state_record_id == parent.self_state_record_id
        and approved.parent_self_state_sha256 == parent.self_state_sha256
        and approved_proposal.parent_self_state_record_id == parent.self_state_record_id
        and approved_delta.parent_self_state_record_id == parent.self_state_record_id
        and receipt.parent_self_state_record_id == parent.self_state_record_id
    )
    exact_delta = bool(
        approved
        and approved_proposal
        and approved_delta
        and approved.delta_ref == approved_delta.delta_id
        and approved.delta_sha256 == approved_delta.delta_sha256
        and approved_proposal.delta_sha256 == approved_delta.delta_sha256
    )
    allowlist = bool(
        approved_delta
        and approved_delta.changed_persistent_fields == CHANGED_PERSISTENT_FIELDS
        and approved_delta.preserved_persistent_fields == PRESERVED_PERSISTENT_FIELDS
        and approved_delta.complete_persistent_field_allowlist == ALLOWED_PERSISTENT_FIELDS
    )
    rejected_unchanged = bool(
        rejection_invariance
        and rejection_invariance.authoritative_self_state_unchanged
        and rejection_invariance.active_head_unchanged
    )
    deferred_unchanged = bool(
        deferral_invariance
        and deferral_invariance.authoritative_self_state_unchanged
        and deferral_invariance.active_head_unchanged
    )
    head_advanced = bool(
        receipt
        and reviewed_cas
        and receipt.package_134_active_head_advanced
        and reviewed_cas.cas_succeeded
        and reviewed_cas.transaction_committed
        and reviewed_cas.new_active_head_sha256 == head.active_head_sha256
    )
    head_revision_exact = bool(
        receipt
        and receipt.head_revision_after == receipt.head_revision_before + 1
        and head.head_revision == receipt.head_revision_after
    )
    append_only = bool(
        store_integrity["valid"]
        and p133_integrity["valid"]
        and p134_integrity["valid"]
        and not store_integrity["active_head_table_present"]
        and not store_integrity["self_state_history_table_present"]
        and parent
        and child
        and child.parent_self_state_record_id == parent.self_state_record_id
        and child.parent_self_state_sha256 == parent.self_state_sha256
    )
    checks = {
        "baseline_head": _git_commit_is_ancestor(root, BASELINE_COMMIT),
        "package_133_audit": preflight["package_133_audit_status"] == PACKAGE_133_PASS_STATUS,
        "package_134_audit": preflight["package_134_audit_status"] == PACKAGE_134_PASS_STATUS,
        "package_136_baseline": preflight["package_136_baseline_verified"],
        "authority_sources_unchanged_during_audit": before == after,
        "package_133_schema_authority": SELF_STATE_AUTHORITY == "package_133_immutable_self_state_lineage",
        "package_134_head_authority": head.active_head_authority == ACTIVE_HEAD_AUTHORITY,
        "existing_teacher_authority": bool(
            binding.existing_teacher_authority_reused
            and not binding.second_teacher_system_created
            and not binding.learning_approval_scope_reused
        ),
        "one_review_each": all((approved, rejected, deferred)) and len(reviews) == 3,
        "exact_head": exact_head,
        "exact_parent": exact_parent,
        "exact_delta": exact_delta,
        "persistent_allowlist": allowlist,
        "approved_successor": bool(receipt and receipt.cross_authority_commit_complete and child),
        "head_advanced": head_advanced,
        "head_revision": head_revision_exact,
        "rejected_unchanged": rejected_unchanged,
        "deferred_unchanged": deferred_unchanged,
        "controls": controls.get("controls_passed") is True,
        "stale_control": "stale_review_blocked_before_history_append" in passed_controls,
        "cas_control": "cas_conflict_blocked_without_rebase" in passed_controls,
        "partial_control": "cross_authority_partial_failure_visible_and_blocked" in passed_controls,
        "tamper_control": all(
            name in passed_controls
            for name in ("proposal_tampering_rejected", "review_target_tampering_rejected")
        ),
        "reuse_control": "approval_reuse_rejected" in passed_controls,
        "corrupt_controls": all(
            name in passed_controls
            for name in ("corrupt_package_133_store_blocked", "corrupt_package_134_store_blocked")
        ),
        "append_only": append_only,
        "boundary": boundary["valid"],
        "regressions": regressions.get("fresh_regressions_passed") is True,
    }
    failures = tuple(name for name, passed in checks.items() if not passed)
    status = PASS_STATUS if not failures else BLOCKED_STATUS
    payload: dict[str, Any] = {
        "audit_id": "",
        "audit_sha256": "",
        "schema_version": AUDIT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "baseline_commit": BASELINE_COMMIT,
        "source_head": _git_output(root, "rev-parse", "HEAD"),
        "package_133_audit_status": preflight["package_133_audit_status"],
        "package_134_audit_status": preflight["package_134_audit_status"],
        "package_136_baseline_verified": preflight["package_136_baseline_verified"],
        "package_133_only_schema_authority": checks["package_133_schema_authority"],
        "package_134_only_active_head_cas_authority": checks["package_134_head_authority"],
        "existing_teacher_authority_reused": checks["existing_teacher_authority"],
        "second_teacher_system_created": False,
        "exact_head_binding_verified": exact_head,
        "exact_parent_binding_verified": exact_parent,
        "exact_delta_binding_verified": exact_delta,
        "persistent_field_allowlist_preserved": allowlist,
        "approved_review_id": approved.review_id if approved else "missing_approved_review",
        "approved_successor_created": checks["approved_successor"],
        "approved_successor_is_immutable": append_only,
        "active_head_advanced_by_exact_cas": head_advanced,
        "head_revision_increment_exact": head_revision_exact,
        "rejected_review_id": rejected.review_id if rejected else "missing_rejected_review",
        "rejected_authorities_unchanged": rejected_unchanged,
        "deferred_review_id": deferred.review_id if deferred else "missing_deferred_review",
        "deferred_authorities_unchanged": deferred_unchanged,
        "stale_review_control_passed": checks["stale_control"],
        "cas_conflict_control_passed": checks["cas_control"],
        "partial_failure_control_passed": checks["partial_control"],
        "proposal_tamper_control_passed": checks["tamper_control"],
        "approval_reuse_control_passed": checks["reuse_control"],
        "corrupt_store_controls_passed": checks["corrupt_controls"],
        "all_controls_passed": checks["controls"],
        "append_only_history_verified": append_only,
        "parent_modified_in_place": False,
        "automatic_rebase_performed": False,
        "unauthorized_mutation_became_authoritative": False,
        "runtime_behavior_influence_created": False,
        "self_state_readback_created": False,
        "memory_influence_created": False,
        "drive_persisted": False,
        "perception_or_attention_created": False,
        "thought_engine_used": False,
        "action_created": False,
        "output_created": False,
        "package_138_implemented": boundary["package_138_implemented"],
        "llm_runtime_calls": 0,
        "codex_runtime_calls": 0,
        "network_runtime_calls": 0,
        "fresh_regressions_passed": checks["regressions"],
        "audit_status": status,
        "failure_reasons": failures,
        "package_138_required_gates": PACKAGE_138_REQUIRED_GATES,
        "source_record_refs": tuple(
            item
            for item in (
                preflight["package_133_audit_id"],
                preflight["package_134_audit_id"],
                binding.authority_binding_id,
                approved.review_id if approved else None,
                rejected.review_id if rejected else None,
                deferred.review_id if deferred else None,
                receipt.commit_receipt_id if receipt else None,
                reviewed_cas.cas_event_id if reviewed_cas else None,
                controls.get("control_result_id"),
                regressions.get("regression_receipt_id"),
            )
            if item
        ),
    }
    audit = _hashed_record(
        Package137PersistentSelfStateReviewGateAudit,
        payload,
        id_field="audit_id",
        hash_field="audit_sha256",
        prefix="package_137_audit",
    )
    if append:
        try:
            stored = p137.get_payload("package_137_audits", audit.audit_id)
        except KeyError:
            p137.append_once("package_137_audits", audit)
        else:
            existing = _record_from_payload(
                Package137PersistentSelfStateReviewGateAudit, stored
            )
            if existing.audit_sha256 != audit.audit_sha256:
                raise RuntimeError("blocked_package_137_audit_identity_collision")
            return existing
    return audit


def _scan_package_137_boundary(root: Path) -> dict[str, Any]:
    package_files = tuple(sorted((root / "ashl_core_v1/state").glob("*137*py"))) + tuple(
        sorted((root / "ashl_core_v1/state").glob("persistent_self_state_review_*.py"))
    )
    forbidden_import_prefixes = (
        "ashl_core_v1.memory",
        "ashl_core_v1.perception",
        "ashl_core_v1.endocrine",
        "ashl_core_v1.runtime.internal_action",
        "ashl_core_v1.runtime.output",
        "ashl_core_v1.thought",
    )
    forbidden_imports: list[str] = []
    for path in dict.fromkeys(package_files):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: tuple[str, ...] = ()
            if isinstance(node, ast.Import):
                names = tuple(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = (node.module,)
            for name in names:
                if name.startswith(forbidden_import_prefixes):
                    forbidden_imports.append(f"{path.name}:{name}")
    package_138_files = tuple(
        dict.fromkeys(
            tuple((root / "ashl_core_v1/state").glob("*138*.py"))
            + tuple((root / "ashl_core_v1/state").glob("self_state_readback_*.py"))
        )
    )
    downstream_forbidden_prefixes = (
        "ashl_core_v1.state.persistent_self_state_review_runtime",
        "ashl_core_v1.state.persistent_self_state_store",
    )
    downstream_forbidden_imports: list[str] = []
    for path in package_138_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: tuple[str, ...] = ()
            if isinstance(node, ast.Import):
                names = tuple(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = (node.module,)
            for name in names:
                if name.startswith(downstream_forbidden_prefixes):
                    downstream_forbidden_imports.append(f"{path.name}:{name}")
    return {
        "valid": not forbidden_imports and not downstream_forbidden_imports,
        "forbidden_imports": tuple(forbidden_imports + downstream_forbidden_imports),
        "package_138_implemented": False,
    }


def _one(items: tuple[Any, ...]) -> Any | None:
    return items[0] if len(items) == 1 else None


def _source_tree_sha256(source_root: Path) -> str:
    entries: list[dict[str, Any]] = []
    for path in sorted(source_root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_symlink():
            raise ValueError("Package 137 authority evidence cannot contain symlinks")
        if path.is_file():
            data = path.read_bytes()
            entries.append(
                {
                    "relative_path": path.relative_to(source_root).as_posix(),
                    "size_bytes": len(data),
                    "sha256": sha256_bytes(data),
                }
            )
    return sha256_payload(entries)


def _git_output(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ("git", *args),
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def _git_commit_is_ancestor(root: Path, commit: str) -> bool:
    completed = subprocess.run(
        ("git", "merge-base", "--is-ancestor", commit, "HEAD"),
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def _is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
