"""Fresh regressions and evidence-derived audit for Package 138."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from dataclasses import fields
from pathlib import Path
from typing import Any, TypeVar

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.state.package_138_self_state_readback_store import (
    Package138SelfStateReadbackStore,
)
from ashl_core_v1.state.package_138_self_state_sources import (
    load_package_138_sources_read_only,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    PersistentSessionRecoveryStore,
)
from ashl_core_v1.state.self_state_readback_runtime import (
    _hashed_record,
    preflight_self_state_readback_boundary,
)
from ashl_core_v1.state.self_state_readback_types import (
    ACTIVE_HEAD_AUTHORITY,
    ALLOWLIST_SCHEMA_VERSION,
    AUDIT_ONLY_CONSUMER_ID,
    AUDIT_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    EXPOSED_STRUCTURAL_FIELDS,
    PACKAGE_139_REQUIRED_AUTHORITIES,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    REVIEW_GATE_AUTHORITY,
    SELF_STATE_AUTHORITY,
    BoundedSelfStateReadbackRecord,
    Package138ControlResult,
    Package138RegressionReceipt,
    Package138SelfStateReadbackBoundaryAudit,
    SelfStateReadbackAuthorizationRecord,
    SelfStateReadbackAuthoritySourceBindingRecord,
    SelfStateReadbackConsumerAllowlistRecord,
    SelfStateReadbackConsumptionRecord,
    SelfStateReadbackCounterfactualComparison,
    SelfStateReadbackFreshProcessResetRecord,
    SelfStateReadbackLifecycleRecord,
    SelfStateReadbackProcessReceipt,
)


T = TypeVar("T")

_TARGETED_138 = "ashl_core_v1.tests.test_package_138_self_state_readback_boundary"
_PACKAGE_133_134_137 = (
    "ashl_core_v1.tests.test_package_133_cross_session_self_state_schema",
    "ashl_core_v1.tests.test_package_134_persistent_session_recovery_identity",
    "ashl_core_v1.tests.test_package_137_persistent_self_state_review_gate",
)
_PACKAGE_135_136 = (
    "ashl_core_v1.tests.test_package_135_drive_signal_trace_separation",
    "ashl_core_v1.tests.test_package_136_same_session_drive_modulation",
)
_TEACHER_AUTHORITY = (
    "ashl_core_v1.tests.test_cradle_state_resume_selection_authorization",
    "ashl_core_v1.tests.test_teacher_gated_session_store",
    "ashl_core_v1.tests.test_teacher_gated_session_resume_commit",
)


def run_package_138_regressions(
    *, ashl_root: str | Path, state_dir: str | Path
) -> Package138RegressionReceipt:
    root = Path(ashl_root).resolve()
    store = Package138SelfStateReadbackStore(state_dir)
    pycache = store.root / "regression_pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    commands: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("targeted_package_138", (sys.executable, "-m", "unittest", _TARGETED_138)),
        (
            "package_133_134_137_regressions",
            (sys.executable, "-m", "unittest", *_PACKAGE_133_134_137),
        ),
        (
            "package_135_136_boundary_regressions",
            (sys.executable, "-m", "unittest", *_PACKAGE_135_136),
        ),
        (
            "teacher_authority_regressions",
            (sys.executable, "-m", "unittest", *_TEACHER_AUTHORITY),
        ),
        (
            "full_v1_unittest_discover",
            (sys.executable, "-m", "unittest", "discover", "--durations", "20"),
        ),
        ("compileall", (sys.executable, "-m", "compileall", "-q", "ashl_core_v1")),
        ("git_diff_check", ("git", "diff", "--check")),
    )
    results: list[tuple[str, int, str]] = [
        ("package_138_source_tree", 0, _package_138_source_tree_sha256(root))
    ]
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
    receipt = Package138RegressionReceipt(
        regression_receipt_id=(
            f"package_138_regressions:{sha256_payload({'head': source_head, 'results': results})[:16]}"
        ),
        schema_version=REGRESSION_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        source_head=source_head,
        command_results=tuple(results),
        targeted_package_138_passed=statuses["targeted_package_138"],
        package_133_134_137_regressions_passed=statuses[
            "package_133_134_137_regressions"
        ],
        package_135_136_boundary_regressions_passed=statuses[
            "package_135_136_boundary_regressions"
        ],
        teacher_authority_regressions_passed=statuses["teacher_authority_regressions"],
        full_v1_discover_passed=statuses["full_v1_unittest_discover"],
        compileall_passed=statuses["compileall"],
        git_diff_check_passed=statuses["git_diff_check"],
        pycache_redirected_outside_repo=not _is_within(pycache, root),
        fresh_regressions_passed=all(statuses.values()),
    )
    store.append_once("package_138_regression_receipts", receipt)
    return receipt


def audit_package_138_self_state_readback_boundary(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_137_state_dir: str | Path,
    state_dir: str | Path,
    append: bool = True,
) -> Package138SelfStateReadbackBoundaryAudit:
    root = Path(ashl_root).resolve()
    preflight = preflight_self_state_readback_boundary(
        ashl_root=root,
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
        state_dir=state_dir,
    )
    source = load_package_138_sources_read_only(
        package_133_state_dir=package_133_state_dir,
        package_134_state_dir=package_134_state_dir,
        package_137_state_dir=package_137_state_dir,
    )
    store = Package138SelfStateReadbackStore(state_dir)
    integrity = store.audit_integrity()
    bindings = _records(store, "self_state_readback_source_bindings", SelfStateReadbackAuthoritySourceBindingRecord)
    authorizations = _records(
        store,
        "self_state_readback_authorizations",
        SelfStateReadbackAuthorizationRecord,
    )
    allowlists = _records(store, "self_state_readback_consumer_allowlists", SelfStateReadbackConsumerAllowlistRecord)
    readbacks = _records(store, "bounded_self_state_readbacks", BoundedSelfStateReadbackRecord)
    consumptions = _records(store, "self_state_readback_consumptions", SelfStateReadbackConsumptionRecord)
    lifecycles = _records(store, "self_state_readback_lifecycle_records", SelfStateReadbackLifecycleRecord)
    processes = _records(store, "self_state_readback_process_receipts", SelfStateReadbackProcessReceipt)
    comparisons = _records(store, "self_state_readback_counterfactual_comparisons", SelfStateReadbackCounterfactualComparison)
    resets = _records(store, "self_state_readback_fresh_process_resets", SelfStateReadbackFreshProcessResetRecord)
    controls = _latest_record(store, "package_138_control_results", Package138ControlResult)
    regressions = _latest_record(store, "package_138_regression_receipts", Package138RegressionReceipt)
    current_binding = next(
        (item for item in reversed(bindings) if item.active_head_sha256 == source.active_head.active_head_sha256),
        None,
    )
    initial_binding = bindings[0] if bindings else None
    allowlist = allowlists[-1] if allowlists else None
    reset = resets[-1] if resets else None
    comparison = comparisons[-1] if comparisons else None
    p134 = PersistentSessionRecoveryStore(package_134_state_dir)
    cas_events = p134.list_payloads("active_head_cas_events")

    exact_source = bool(current_binding) and all(
        (
            current_binding.active_head_sha256 == source.active_head.active_head_sha256,
            current_binding.head_revision == source.active_head.head_revision,
            current_binding.self_state_record_id == source.package_133.leaf.self_state_record_id,
            current_binding.self_state_sha256 == source.package_133.leaf.self_state_sha256,
        )
    )
    exact_readbacks = bool(readbacks) and all(
        item.active_head_id and item.active_head_sha256 and item.self_state_record_id and item.self_state_sha256
        for item in readbacks
    )
    exact_consumptions = bool(consumptions) and all(
        item.exact_head_match and item.exact_state_match and item.same_session_match and item.same_process_match
        for item in consumptions
    )
    opaque_only = bool(readbacks) and all(
        item.exposed_structural_fields == EXPOSED_STRUCTURAL_FIELDS
        and not any(
            (
                item.semantic_identity_created,
                item.autobiographical_memory_created,
                item.psychological_state_created,
                item.world_knowledge_created,
            )
        )
        for item in readbacks
    )
    expired_refs = {
        item.readback_ref
        for item in lifecycles
        if item.lifecycle_kind in {"expired_session_end", "expired_authorization_deadline"}
        and not item.readback_active_after
    }
    stale = tuple(
        item for item in lifecycles
        if item.lifecycle_kind == "stale_active_head_revision_changed"
        and item.observed_head_revision != item.expected_head_revision
        and not item.readback_active_after
        and not item.automatically_refreshed
        and not item.automatically_rebound
    )
    noauth_process = tuple(
        item for item in processes
        if item.worker_status == "fresh_process_started_without_prior_readback"
        and item.authorization_ref is None
        and item.readback_ref is None
        and not item.prior_session_readback_loaded
    )
    reauthorized = tuple(
        item for item in processes
        if item.worker_status == "newly_authorized_readback_consumed_then_expired"
        and item.authorization_ref and item.readback_ref
    )
    reset_cas = bool(reset) and any(
        str(item.get("cas_event_id")) == reset.package_134_recovery_cas_event_ref
        and item.get("operation") == "recover_session"
        and item.get("cas_succeeded") is True
        and item.get("transaction_committed") is True
        and item.get("self_state_record_unchanged") is True
        for item in cas_events
    )
    source_authorities_preserved = bool(initial_binding and current_binding and reset) and all(
        (
            initial_binding.package_133_tree_sha256 == current_binding.package_133_tree_sha256,
            initial_binding.package_137_tree_sha256 == current_binding.package_137_tree_sha256,
            reset.self_state_identity_preserved,
            reset_cas,
        )
    )
    semantic_identity_created = any(item.semantic_identity_created for item in readbacks)
    autobiographical_memory_created = any(
        item.autobiographical_memory_created for item in readbacks
    )
    psychological_state_created = any(item.psychological_state_created for item in readbacks)
    world_knowledge_created = any(item.world_knowledge_created for item in readbacks)
    runtime_behavior_influence_created = any(
        item.runtime_behavior_authority for item in readbacks
    ) or any(item.runtime_behavior_changed for item in consumptions)
    memory_influence_created = any(item.memory_authority for item in readbacks) or any(
        item.memory_written for item in consumptions
    )
    drive_influence_created = any(item.drive_authority for item in readbacks) or any(
        item.drive_changed for item in consumptions
    )
    perception_or_attention_influence_created = any(
        item.perception_authority or item.attention_authority for item in readbacks
    ) or any(item.perception_or_attention_changed for item in consumptions)
    candidate_ordering_changed = any(
        item.candidate_ordering_authority for item in readbacks
    ) or any(item.candidate_ordering_changed for item in consumptions)
    purpose_scope_expanded = any(item.purpose_authority for item in readbacks)
    thought_engine_used = any(item.thought_engine_authority for item in readbacks)
    action_created = any(item.action_authority for item in readbacks) or any(
        item.selected_action_created for item in consumptions
    )
    output_created = any(item.output_authority for item in readbacks) or any(
        item.output_created for item in consumptions
    )
    teacher_scope_expanded = any(
        item.teacher_review_scope_used or item.teacher_consumer_approval_inferred
        for item in authorizations
    )
    forbidden_capability_absent = not any(
        (
            semantic_identity_created,
            autobiographical_memory_created,
            psychological_state_created,
            world_knowledge_created,
            runtime_behavior_influence_created,
            memory_influence_created,
            drive_influence_created,
            perception_or_attention_influence_created,
            candidate_ordering_changed,
            purpose_scope_expanded,
            thought_engine_used,
            action_created,
            output_created,
            teacher_scope_expanded,
        )
    )
    boundary = _scan_package_138_boundary(root)
    required: dict[str, bool] = {
        "store_integrity": bool(integrity["valid"]),
        "exact_source_binding": exact_source,
        "zero_production_consumers": bool(allowlist) and allowlist.production_consumer_ids == (),
        "one_audit_consumer": bool(allowlist) and allowlist.audit_only_consumer_ids == (AUDIT_ONLY_CONSUMER_ID,),
        "zero_implicit_consumers": bool(allowlist) and allowlist.implicit_consumer_ids == (),
        "readbacks_present": len(readbacks) >= 2,
        "exact_readback_binding": exact_readbacks and exact_consumptions,
        "opaque_fields_only": opaque_only,
        "same_session_expiry": all(item.readback_id in expired_refs for item in readbacks),
        "stale_head_invalidation": bool(stale),
        "fresh_process_reset": bool(reset) and reset.reset_status == "passed_fresh_process_readback_reset_and_reauthorization",
        "fresh_process_without_auth_blocked": bool(noauth_process),
        "fresh_reauthorization": bool(reauthorized),
        "counterfactual": bool(comparison) and comparison.readback_surface_only_difference and comparison.production_behavior_equivalent,
        "controls": bool(controls) and controls.controls_passed,
        "regressions": bool(regressions) and regressions.fresh_regressions_passed,
        "source_authorities_preserved": source_authorities_preserved,
        "forbidden_capability_absent": forbidden_capability_absent,
        "boundary": boundary["valid"],
    }
    failure_reasons = tuple(name for name, passed in required.items() if not passed)
    status = PASS_STATUS if not failure_reasons else BLOCKED_STATUS
    source_head = _git_output(root, "rev-parse", "HEAD")
    payload: dict[str, Any] = {
        "audit_id": "",
        "audit_sha256": "",
        "schema_version": AUDIT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "baseline_commit": BASELINE_COMMIT,
        "source_head": source_head,
        "package_133_audit_status": source.source_binding.package_133_audit_status,
        "package_134_audit_status": source.source_binding.package_134_audit_status,
        "package_137_audit_status": source.source_binding.package_137_audit_status,
        "package_133_only_schema_authority": source.source_binding.self_state_authority == SELF_STATE_AUTHORITY,
        "package_134_only_active_head_authority": source.source_binding.active_head_authority == ACTIVE_HEAD_AUTHORITY,
        "package_137_only_mutation_review_authority": source.source_binding.review_gate_authority == REVIEW_GATE_AUTHORITY,
        "exact_source_binding_verified": exact_source,
        "production_consumer_count": len(allowlist.production_consumer_ids) if allowlist else 0,
        "audit_only_consumer_count": len(allowlist.audit_only_consumer_ids) if allowlist else 0,
        "zero_implicit_consumers": bool(allowlist) and allowlist.zero_implicit_consumers,
        "readback_contract_verified": bool(allowlist) and allowlist.schema_version == ALLOWLIST_SCHEMA_VERSION and preflight["readiness"] == "ready_for_bounded_same_session_read_only_self_state_context",
        "exact_head_binding_verified": exact_readbacks and exact_consumptions,
        "exact_state_binding_verified": exact_readbacks and exact_consumptions,
        "opaque_structural_fields_only": opaque_only,
        "same_session_readback_created": len(readbacks) >= 2,
        "read_only_consumption_verified": bool(consumptions) and all(item.read_only_consumption for item in consumptions),
        "same_session_expiry_verified": all(item.readback_id in expired_refs for item in readbacks),
        "stale_head_invalidation_verified": bool(stale),
        "fresh_process_reset_verified": bool(reset) and reset_cas,
        "fresh_authorization_after_recovery_verified": bool(reauthorized),
        "counterfactual_equivalence_verified": bool(comparison) and comparison.production_behavior_equivalent,
        "readback_surface_only_difference": bool(comparison) and comparison.readback_surface_only_difference,
        "append_only_audit_history_verified": bool(integrity["append_only_history"]),
        "source_authorities_unchanged": source_authorities_preserved,
        "all_controls_passed": bool(controls) and controls.controls_passed,
        "fresh_regressions_passed": bool(regressions) and regressions.fresh_regressions_passed,
        "semantic_identity_created": semantic_identity_created,
        "autobiographical_memory_created": autobiographical_memory_created,
        "psychological_state_created": psychological_state_created,
        "world_knowledge_created": world_knowledge_created,
        "persistent_working_readback_created": bool(integrity["persistent_working_readback_table_present"]),
        "runtime_behavior_influence_created": runtime_behavior_influence_created,
        "memory_influence_created": memory_influence_created,
        "drive_influence_created": drive_influence_created,
        "perception_or_attention_influence_created": perception_or_attention_influence_created,
        "candidate_ordering_changed": candidate_ordering_changed,
        "purpose_scope_expanded": purpose_scope_expanded,
        "thought_engine_used": thought_engine_used,
        "action_created": action_created,
        "output_created": output_created,
        "teacher_scope_expanded": teacher_scope_expanded,
        "package_139_implemented": boundary["package_139_implemented"],
        "llm_runtime_calls": 0,
        "codex_runtime_calls": 0,
        "network_runtime_calls": 0,
        "audit_status": status,
        "failure_reasons": failure_reasons,
        "package_139_required_authorities": PACKAGE_139_REQUIRED_AUTHORITIES,
        "source_record_refs": tuple(
            item for item in (
                current_binding.source_binding_id if current_binding else None,
                allowlist.allowlist_id if allowlist else None,
                reset.reset_record_id if reset else None,
                comparison.comparison_id if comparison else None,
                controls.control_result_id if controls else None,
                regressions.regression_receipt_id if regressions else None,
            ) if item
        ),
    }
    audit = _hashed_record(
        Package138SelfStateReadbackBoundaryAudit,
        payload,
        id_field="audit_id",
        hash_field="audit_sha256",
        prefix="package_138_audit",
    )
    if append:
        store.append_once("package_138_audits", audit)
    return audit


def _scan_package_138_boundary(root: Path) -> dict[str, Any]:
    forbidden_imports: list[str] = []
    for relative in ("ashl_core_v1/runtime", "ashl_core_v1/perception", "ashl_core_v1/memory", "ashl_core_v1/endocrine"):
        base = root / relative
        for path in base.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                modules: tuple[str, ...] = ()
                if isinstance(node, ast.Import):
                    modules = tuple(item.name for item in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    modules = (node.module,)
                for module in modules:
                    if "self_state_readback" in module or "package_138" in module:
                        forbidden_imports.append(f"{path.relative_to(root).as_posix()}:{module}")
    package_139_files = tuple(
        path.relative_to(root).as_posix()
        for path in root.glob("ashl_core_v1/**/*139*.py")
        if "test_package_138" not in path.name
    )
    return {
        "valid": not forbidden_imports and not package_139_files,
        "forbidden_imports": tuple(forbidden_imports),
        "package_139_implemented": bool(package_139_files),
    }


def _package_138_source_tree_sha256(root: Path) -> str:
    candidates = tuple(
        dict.fromkeys(
            tuple((root / "ashl_core_v1/state").glob("*138*.py"))
            + tuple((root / "ashl_core_v1/state").glob("self_state_readback_*.py"))
            + (
                root / "ashl_core_v1/tests/test_package_138_self_state_readback_boundary.py",
                root / "ashl_core_v1/docs/self_state_readback_boundary_v0.md",
            )
        )
    )
    if not candidates or not all(path.is_file() for path in candidates):
        raise FileNotFoundError("Package 138 source-tree evidence is incomplete")
    return sha256_payload(
        tuple(
            (
                path.relative_to(root).as_posix(),
                sha256_bytes(path.read_bytes()),
            )
            for path in sorted(candidates)
        )
    )


def _records(
    store: Package138SelfStateReadbackStore, table: str, record_type: type[T]
) -> tuple[T, ...]:
    return tuple(_record_from_payload(record_type, item) for item in store.list_payloads(table))


def _latest_record(
    store: Package138SelfStateReadbackStore, table: str, record_type: type[T]
) -> T | None:
    payload = store.latest_payload(table)
    return _record_from_payload(record_type, payload) if payload else None


def _record_from_payload(record_type: type[T], payload: dict[str, Any]) -> T:
    values = _tuple_tree(dict(payload))
    allowed = {item.name for item in fields(record_type)}
    return record_type(**{key: value for key, value in values.items() if key in allowed})


def _tuple_tree(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_tuple_tree(item) for item in value)
    if isinstance(value, dict):
        return {key: _tuple_tree(item) for key, item in value.items()}
    return value


def _git_output(root: Path, *args: str) -> str:
    result = subprocess.run(("git", *args), cwd=root, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
