"""Controls, regressions, and final audit for Package 143."""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable

from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.thought.package_141_instinct_audit import repository_source_tree_sha256
from ashl_core_v1.thought.package_142_specialized_thought_runtime import (
    invalidate_specialized_results,
)
from ashl_core_v1.thought.package_143_coarse_workspace_runtime import (
    Package143Preflight,
    build_live_package_142_inputs,
    build_workspace_counterfactual_equivalence,
    load_package_142_workspace_evidence,
    load_package_143_preflight,
    open_ephemeral_workspace,
    recover_workspace_from_store,
    validate_no_forbidden_workspace_authority,
)
from ashl_core_v1.thought.package_143_coarse_workspace_store import (
    Package143CoarseWorkspaceStore,
)
from ashl_core_v1.thought.coarse_thought_workspace_types import (
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    CAPACITY,
    CONSUMER_SCOPE,
    CONTROL_NAMES,
    CONTROL_SCHEMA_VERSION,
    EVICTION_POLICY,
    PACKAGE_142_PASS_STATUS,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    CoarseThoughtWorkspaceAdmissionRecord,
    CoarseThoughtWorkspaceCascadeInvalidationRecord,
    CoarseThoughtWorkspaceClosureRecord,
    CoarseThoughtWorkspaceConflictCarriageRecord,
    CoarseThoughtWorkspaceConsumerBindingRecord,
    CoarseThoughtWorkspaceContractRecord,
    CoarseThoughtWorkspaceCounterfactualEquivalenceRecord,
    CoarseThoughtWorkspaceEntryRecord,
    CoarseThoughtWorkspaceEvictionRecord,
    CoarseThoughtWorkspaceFreshProcessResetRecord,
    Package143BoundaryControlResult,
    Package143CoarseThoughtWorkspaceAudit,
    Package143RegressionReceipt,
    build_hashed_record,
)


_TARGETED_BOUNDARY_MODULES = (
    "ashl_core_v1.tests.test_package_132_active_perception_attention_milestone",
    "ashl_core_v1.tests.test_package_140_persistent_self_state_drive_milestone",
)


def run_package_143_boundary_controls(
    preflight: Package143Preflight,
    *,
    ashl_root: str | Path,
    state_dir: str | Path | None = None,
    append_to: Package143CoarseWorkspaceStore | None = None,
) -> Package143BoundaryControlResult:
    base = 20_000_000_000
    live = build_live_package_142_inputs(preflight, base_monotonic_ns=base + 100)
    closed = live.closed.result
    opened = live.open.result
    conflict_results = tuple(item.result for item in live.conflict_outputs if item.result)
    if closed is None or opened is None or len(conflict_results) != 2:
        raise RuntimeError("blocked_package_143_control_source_generation")

    def rejected(call: Callable[[], Any]) -> bool:
        try:
            call()
        except (AttributeError, TypeError, ValueError, RuntimeError):
            return True
        return False

    session_counter = 0

    def workspace(offset: int = 0):
        nonlocal session_counter
        session_counter += 1
        return open_ephemeral_workspace(
            preflight,
            opened_at_monotonic_ns=base + offset,
            process_instance_id=f"control_process:{session_counter}",
            runtime_session_id=f"control_runtime:{session_counter}",
        )

    revoked_source = invalidate_specialized_results(
        output=live.closed,
        transition_kind="upstream_precursor_revoked",
        observed_at_monotonic_ns=base + 500,
    )

    duplicate_ws = workspace(1_000)
    duplicate_ws.admit_result(closed, admitted_at_monotonic_ns=base + 1_001)

    partial_ws = workspace(2_000)
    partial_ws.register_source_conflict(live.conflict)

    def eviction_run(offset: int):
        item = workspace(offset)
        item.admit_result(closed, admitted_at_monotonic_ns=base + offset + 1)
        item.admit_conflict(
            live.conflict,
            conflict_results,
            admitted_at_monotonic_ns=base + offset + 2,
        )
        return item.admit_result(
            opened,
            admitted_at_monotonic_ns=base + offset + 3,
        )

    eviction_a = eviction_run(3_000)
    eviction_b = eviction_run(4_000)

    live_second = build_live_package_142_inputs(
        preflight,
        base_monotonic_ns=base + 400,
    )
    conflict_second = tuple(
        item.result for item in live_second.conflict_outputs if item.result
    )
    atomic_ws = workspace(5_000)
    atomic_ws.admit_conflict(
        live.conflict,
        conflict_results,
        admitted_at_monotonic_ns=base + 5_001,
    )
    atomic_ws.admit_result(closed, admitted_at_monotonic_ns=base + 5_002)
    atomic_eviction = atomic_ws.admit_conflict(
        live_second.conflict,
        conflict_second,
        admitted_at_monotonic_ns=base + 5_003,
    )

    conflict_ws = workspace(6_000)
    conflict_output = conflict_ws.admit_conflict(
        live.conflict,
        conflict_results,
        admitted_at_monotonic_ns=base + 6_001,
    )
    conflict_carriage = conflict_output.conflict_carriage
    if conflict_carriage is None:
        raise RuntimeError("blocked_package_143_control_conflict_carriage")
    revocation_cascade = conflict_ws.cascade_invalidate(
        source_result_refs=(conflict_results[0].specialized_result_id,),
        transition_kind="source_result_revoked",
        observed_at_monotonic_ns=base + 6_002,
        source_invalidation_ref=revoked_source.invalidation_id,
    )

    expiry_ws = workspace(7_000)
    expiry_ws.admit_result(opened, admitted_at_monotonic_ns=base + 7_001)
    expiry_cascade = expiry_ws.cascade_invalidate(
        source_result_refs=(opened.specialized_result_id,),
        transition_kind="source_result_expired",
        observed_at_monotonic_ns=opened.expires_at_monotonic_ns,
    )

    counterfactual = build_workspace_counterfactual_equivalence(
        root=Path(ashl_root).resolve(),
        source_sha256_before=preflight.source.database_sha256,
        source_sha256_after=preflight.source.database_sha256,
        source_record_refs=(preflight.consumer_binding.consumer_binding_id,),
    )
    reset_payload = (
        Package143CoarseWorkspaceStore(state_dir).latest_payload(
            "coarse_workspace_fresh_process_resets"
        )
        if state_dir is not None
        else None
    )

    forbidden = lambda name: rejected(  # noqa: E731 - compact control matrix
        lambda: validate_no_forbidden_workspace_authority(**{name: True})
    )
    deterministic_eviction = bool(
        eviction_a.evictions
        and eviction_b.evictions
        and eviction_a.evictions[0].evicted_admission_group_id
        == eviction_b.evictions[0].evicted_admission_group_id
        and eviction_a.evictions[0].eviction_policy == EVICTION_POLICY
    )
    atomic_eviction_verified = bool(
        atomic_eviction.evictions
        and len(atomic_eviction.evictions[0].evicted_entry_refs) == 2
        and atomic_eviction.evictions[0].group_evicted_atomically
    )
    eviction_semantics_neutral = all(
        not any(
            (
                item.error_claimed,
                item.negation_claimed,
                item.forgetting_claimed,
                item.low_importance_claimed,
                item.behavior_suppression_claimed,
                item.winner_created,
            )
        )
        for item in eviction_a.evictions + atomic_eviction.evictions
    )
    checks = {
        "package_142_audit_missing_rejected": rejected(
            lambda: _require_package_142_audit(False, PACKAGE_142_PASS_STATUS)
        ),
        "package_142_audit_status_rejected": rejected(
            lambda: _require_package_142_audit(True, "blocked")
        ),
        "unknown_result_schema_rejected": rejected(
            lambda: replace(closed, schema_version="unknown")
        ),
        "unknown_conflict_schema_rejected": rejected(
            lambda: replace(live.conflict, schema_version="unknown")
        ),
        "expired_result_rejected": rejected(
            lambda: workspace(8_000).admit_result(
                closed,
                admitted_at_monotonic_ns=closed.expires_at_monotonic_ns,
            )
        ),
        "revoked_result_rejected": rejected(
            lambda: workspace(9_000).admit_result(
                closed,
                admitted_at_monotonic_ns=base + 9_001,
                source_invalidation=revoked_source,
            )
        ),
        "semantic_result_rejected": rejected(
            lambda: replace(closed, semantic_label="semantic")
        ),
        "authority_bearing_result_rejected": rejected(
            lambda: replace(closed, action_selection_authority=True)
        ),
        "wrong_conflict_lineage_rejected": rejected(
            lambda: replace(
                live.conflict,
                specialized_result_refs=(
                    closed.specialized_result_id,
                    opened.specialized_result_id,
                ),
            )
        ),
        "partial_conflict_admission_rejected": rejected(
            lambda: partial_ws.admit_result(
                conflict_results[0],
                admitted_at_monotonic_ns=base + 2_001,
            )
        ),
        "duplicate_entry_rejected": rejected(
            lambda: duplicate_ws.admit_result(
                closed,
                admitted_at_monotonic_ns=base + 1_002,
            )
        ),
        "capacity_overflow_rejected": all(
            item.admission.occupancy_before <= CAPACITY
            and len(item.entries) <= CAPACITY
            for item in (eviction_a, eviction_b, atomic_eviction)
        ),
        "oversized_group_rejected": rejected(
            lambda: workspace(10_000)._admit(  # type: ignore[attr-defined]
                results=(closed, opened, conflict_results[0], conflict_results[1]),
                conflict=None,
                admitted_at_monotonic_ns=base + 10_001,
                target_workspace_session_id=None,
                source_invalidation=None,
            )
        ),
        "deterministic_eviction_verified": deterministic_eviction,
        "atomic_conflict_eviction_verified": atomic_eviction_verified,
        "eviction_semantics_neutral_verified": eviction_semantics_neutral,
        "conflict_unresolved_preserved": (
            conflict_carriage.conflict_status_in_workspace
            == "unresolved_cross_family_conflict_preserved"
            and conflict_carriage.all_results_preserved
        ),
        "conflict_winner_rejected": rejected(
            lambda: replace(conflict_carriage, winner_entry_id="winner")
        ),
        "conflict_priority_rejected": rejected(
            lambda: replace(conflict_carriage, priority_used=True)
        ),
        "conflict_ranking_rejected": rejected(
            lambda: replace(conflict_carriage, ranking_used=True)
        ),
        "conflict_truth_selection_rejected": rejected(
            lambda: replace(conflict_carriage, truth_selection_created=True)
        ),
        "expiry_cascade_verified": (
            expiry_cascade.source_transition_kind == "source_result_expired"
            and expiry_cascade.orphan_entry_count_after == 0
        ),
        "revocation_cascade_verified": (
            revocation_cascade.source_transition_kind == "source_result_revoked"
            and revocation_cascade.conflict_group_invalidated_atomically
            and len(revocation_cascade.invalidated_workspace_entry_refs) == 2
        ),
        "orphan_entry_rejected": rejected(
            lambda: replace(expiry_cascade, orphan_entry_count_after=1)
        ),
        "cross_session_admission_rejected": rejected(
            lambda: workspace(11_000).admit_result(
                closed,
                admitted_at_monotonic_ns=base + 11_001,
                target_workspace_session_id="other_session",
            )
        ),
        "fresh_process_starts_empty_verified": bool(
            reset_payload
            and reset_payload.get("fresh_process_empty")
            and reset_payload.get("initial_entry_count") == 0
            and reset_payload.get("recovered_entry_count") == 0
        ),
        "workspace_recovery_rejected": rejected(
            lambda: recover_workspace_from_store("anything")
        ),
        "memory_write_rejected": forbidden("memory_write_created"),
        "self_state_write_rejected": forbidden("self_state_write_created"),
        "drive_input_rejected": forbidden("drive_input_used"),
        "readback_input_rejected": forbidden("self_state_readback_used"),
        "iterative_reasoning_rejected": forbidden("iterative_reasoning_created"),
        "recursive_rule_chaining_rejected": forbidden("recursive_rule_chaining_created"),
        "deep_search_rejected": forbidden("deep_search_created"),
        "conflict_resolution_rejected": forbidden("conflict_resolution_created"),
        "verification_proposal_rejected": forbidden("verification_proposal_created"),
        "action_selection_rejected": forbidden("selected_action_created"),
        "output_creation_rejected": forbidden("output_created"),
        "external_control_rejected": forbidden("external_control_created"),
        "package_144_capability_rejected": forbidden("package_144_implemented"),
        "llm_codex_network_use_rejected": all(
            forbidden(name) for name in ("llm_used", "codex_used", "network_used")
        ),
        "counterfactual_equivalence_verified": (
            counterfactual.counterfactual_status
            == "passed_coarse_workspace_counterfactual_equivalence"
        ),
    }
    passed_names = tuple(name for name in CONTROL_NAMES if checks.get(name, False))
    failed_names = tuple(name for name in CONTROL_NAMES if not checks.get(name, False))
    result = build_hashed_record(
        Package143BoundaryControlResult,
        {
            "control_result_id": "",
            "control_result_sha256": "",
            "schema_version": CONTROL_SCHEMA_VERSION,
            "created_at": utc_now(),
            "control_names": CONTROL_NAMES,
            "passed_control_names": passed_names,
            "failed_control_names": failed_names,
            "passed_count": len(passed_names),
            "controls_passed": not failed_names,
            "source_record_refs": (
                preflight.consumer_binding.consumer_binding_id,
                conflict_carriage.conflict_carriage_id,
                expiry_cascade.cascade_id,
                revocation_cascade.cascade_id,
                counterfactual.counterfactual_id,
            ),
        },
        id_field="control_result_id",
        hash_field="control_result_sha256",
        prefix="coarse_workspace_controls",
    )
    if append_to is not None:
        append_to.append_once("package_143_control_results", result)
    return result


def run_package_143_regressions(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
) -> Package143RegressionReceipt:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    _validate_external_state_dir(root, output)
    store = Package143CoarseWorkspaceStore(output)
    pycache = store.root / "regression_pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    commands = (
        (
            "targeted_package_143",
            (
                sys.executable,
                "-m",
                "unittest",
                "ashl_core_v1.tests.test_package_143_coarse_thought_workspace",
            ),
        ),
        (
            "package_142_regressions",
            (
                sys.executable,
                "-m",
                "unittest",
                "ashl_core_v1.tests.test_package_142_specialized_thought_bounded_rules",
            ),
        ),
        (
            "package_132_140_boundary_regressions",
            (sys.executable, "-m", "unittest", *_TARGETED_BOUNDARY_MODULES),
        ),
        ("full_v1_discover", (sys.executable, "-m", "unittest", "discover")),
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
            check=False,
        )
        digest = sha256_payload({"stdout": completed.stdout, "stderr": completed.stderr})
        results.append((name, completed.returncode, digest))
        statuses[name] = completed.returncode == 0
        if completed.returncode != 0:
            raise RuntimeError(f"blocked_package_143_regression_failed:{name}:{digest}")
    pollution_absent = _repository_pollution_absent(root)
    results.append(
        (
            "repository_pollution_scan",
            0 if pollution_absent else 1,
            sha256_payload({"repository_pollution_absent": pollution_absent}),
        )
    )
    if not pollution_absent:
        raise RuntimeError("blocked_package_143_repository_pollution_detected")
    source_head = _git_output(root, "rev-parse", "HEAD")
    tree_hash = repository_source_tree_sha256(root)
    receipt = build_hashed_record(
        Package143RegressionReceipt,
        {
            "regression_receipt_id": "",
            "regression_receipt_sha256": "",
            "schema_version": REGRESSION_SCHEMA_VERSION,
            "created_at": utc_now(),
            "baseline_commit": BASELINE_COMMIT,
            "source_head": source_head,
            "source_tree_sha256": tree_hash,
            "command_results": tuple(results),
            "targeted_package_143_passed": statuses["targeted_package_143"],
            "package_142_regressions_passed": statuses["package_142_regressions"],
            "package_132_140_boundary_regressions_passed": statuses[
                "package_132_140_boundary_regressions"
            ],
            "full_v1_discover_passed": statuses["full_v1_discover"],
            "compileall_passed": statuses["compileall"],
            "git_diff_check_passed": statuses["git_diff_check"],
            "repository_pollution_absent": pollution_absent,
            "fresh_regressions_passed": all(statuses.values()) and pollution_absent,
            "source_record_refs": (
                f"git_head:{source_head}",
                f"source_tree:{tree_hash}",
            ),
        },
        id_field="regression_receipt_id",
        hash_field="regression_receipt_sha256",
        prefix="coarse_workspace_regressions",
    )
    store.append_once("package_143_regression_receipts", receipt)
    return receipt


def audit_package_143_coarse_workspace(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    package_142_state_dir: str | Path,
    package_141_state_dir: str | Path,
    append: bool = True,
) -> Package143CoarseThoughtWorkspaceAudit:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    _validate_external_state_dir(root, output)
    source = load_package_142_workspace_evidence(package_142_state_dir)
    store = Package143CoarseWorkspaceStore(output)
    bindings = _typed(
        store,
        "coarse_workspace_consumer_bindings",
        CoarseThoughtWorkspaceConsumerBindingRecord,
    )
    contracts = _typed(
        store,
        "coarse_workspace_contracts",
        CoarseThoughtWorkspaceContractRecord,
    )
    admissions = _typed(
        store,
        "coarse_workspace_admissions",
        CoarseThoughtWorkspaceAdmissionRecord,
    )
    entries = _typed(store, "coarse_workspace_entries", CoarseThoughtWorkspaceEntryRecord)
    conflicts = _typed(
        store,
        "coarse_workspace_conflict_carriage_records",
        CoarseThoughtWorkspaceConflictCarriageRecord,
    )
    evictions = _typed(
        store,
        "coarse_workspace_evictions",
        CoarseThoughtWorkspaceEvictionRecord,
    )
    cascades = _typed(
        store,
        "coarse_workspace_cascade_invalidations",
        CoarseThoughtWorkspaceCascadeInvalidationRecord,
    )
    closures = _typed(
        store,
        "coarse_workspace_closures",
        CoarseThoughtWorkspaceClosureRecord,
    )
    resets = _typed(
        store,
        "coarse_workspace_fresh_process_resets",
        CoarseThoughtWorkspaceFreshProcessResetRecord,
    )
    counterfactuals = _typed(
        store,
        "coarse_workspace_counterfactual_equivalence_records",
        CoarseThoughtWorkspaceCounterfactualEquivalenceRecord,
    )
    controls_payload = store.latest_payload("package_143_control_results")
    regression_payload = store.latest_payload("package_143_regression_receipts")
    controls = Package143BoundaryControlResult(**controls_payload) if controls_payload else None
    regression = Package143RegressionReceipt(**regression_payload) if regression_payload else None
    binding = bindings[-1] if bindings else None
    contract = contracts[-1] if contracts else None
    source_after = _sha256_file(source.database_path)
    group_sizes = {
        item.admission_group_id: item.requested_entry_count for item in admissions
    }
    maximum_occupancy = 0
    for item in admissions:
        evicted = sum(group_sizes.get(ref, 0) for ref in item.eviction_group_refs)
        maximum_occupancy = max(
            maximum_occupancy,
            item.occupancy_before - evicted + item.requested_entry_count,
        )
    terminal_entry_refs = {
        ref for item in evictions for ref in item.evicted_entry_refs
    }.union(
        ref for item in cascades for ref in item.invalidated_workspace_entry_refs
    )
    orphan_entries = tuple(
        item for item in entries if item.workspace_entry_id not in terminal_entry_refs
    )
    source_read_only = bool(
        binding
        and binding.package_142_store_read_only
        and not binding.package_142_history_mutated
        and binding.package_142_source_database_sha256
        == source.database_sha256
        == source_after
    )
    checks = {
        "package_142_audit": (
            source.audit.audit_status == PACKAGE_142_PASS_STATUS
            and source.audit.source_head == BASELINE_COMMIT
        ),
        "source_read_only": source_read_only,
        "consumer_binding": bool(binding and binding.consumer_scope == CONSUMER_SCOPE),
        "contract": bool(
            contract
            and contract.maximum_entry_count == CAPACITY
            and contract.ephemeral
            and not contract.cross_session_recovery_allowed
        ),
        "admission": len(admissions) >= 3 and len(entries) >= 4,
        "capacity": maximum_occupancy == CAPACITY,
        "eviction": bool(
            evictions
            and all(
                item.eviction_policy == EVICTION_POLICY
                and item.group_evicted_atomically
                for item in evictions
            )
        ),
        "eviction_neutral": all(
            not any(
                (
                    item.error_claimed,
                    item.negation_claimed,
                    item.forgetting_claimed,
                    item.low_importance_claimed,
                    item.behavior_suppression_claimed,
                    item.winner_created,
                )
            )
            for item in evictions
        ),
        "conflict": bool(
            conflicts
            and all(
                item.conflict_status_in_workspace
                == "unresolved_cross_family_conflict_preserved"
                and item.winner_entry_id is None
                for item in conflicts
            )
        ),
        "expiry": any(
            item.source_transition_kind == "source_result_expired" for item in cascades
        ),
        "revocation": any(
            item.source_transition_kind == "source_result_revoked"
            and item.conflict_group_invalidated_atomically
            for item in cascades
        ),
        "no_orphans": not orphan_entries and bool(entries),
        "closed": bool(
            closures
            and all(
                item.entry_count_after_close == 0 and not item.workspace_recoverable
                for item in closures
            )
        ),
        "fresh_reset": bool(
            resets
            and resets[-1].fresh_process_empty
            and resets[-1].processes_distinct
            and resets[-1].recovered_entry_count == 0
        ),
        "counterfactual": bool(
            counterfactuals
            and counterfactuals[-1].counterfactual_status
            == "passed_coarse_workspace_counterfactual_equivalence"
        ),
        "controls": bool(controls and controls.controls_passed),
        "regressions": bool(
            regression
            and regression.fresh_regressions_passed
            and regression.source_tree_sha256 == repository_source_tree_sha256(root)
        ),
        "events": _required_events_present(output),
        "store": bool(store.audit_integrity()["valid"]),
    }
    failures = tuple(name for name, passed in checks.items() if not passed)
    status = PASS_STATUS if not failures else BLOCKED_STATUS
    payload = {
        "audit_id": "",
        "audit_sha256": "",
        "schema_version": "ashl_package_143_coarse_workspace_audit_v0",
        "created_at": utc_now(),
        "baseline_commit": BASELINE_COMMIT,
        "source_head": _git_output(root, "rev-parse", "HEAD"),
        "package_142_audit_verified": checks["package_142_audit"],
        "package_142_source_read_only_verified": checks["source_read_only"],
        "package_142_source_sha256_before": source.database_sha256,
        "package_142_source_sha256_after": source_after,
        "exact_consumer_binding_verified": checks["consumer_binding"],
        "workspace_contract_verified": checks["contract"],
        "capacity_limit": CAPACITY,
        "admission_count": len(admissions),
        "workspace_entry_count": len(entries),
        "maximum_observed_occupancy": maximum_occupancy,
        "capacity_boundary_verified": checks["capacity"],
        "deterministic_eviction_verified": checks["eviction"],
        "eviction_count": len(evictions),
        "eviction_semantics_neutral": checks["eviction_neutral"],
        "conflict_carriage_verified": checks["conflict"],
        "unresolved_conflict_count": len(conflicts),
        "conflict_winner_created": any(item.winner_entry_id is not None for item in conflicts),
        "expiry_cascade_verified": checks["expiry"],
        "revocation_cascade_verified": checks["revocation"],
        "orphan_workspace_entry_count": len(orphan_entries),
        "workspace_closed_empty": checks["closed"],
        "fresh_process_reset_verified": checks["fresh_reset"],
        "cross_session_recovery_used": False,
        "persistent_workspace_state_created": False,
        "direct_perception_input_count": 0,
        "production_drive_input_count": len(binding.drive_input_allowlist) if binding else -1,
        "production_readback_input_count": len(binding.self_state_readback_input_allowlist) if binding else -1,
        "production_output_consumer_count": len(binding.production_output_consumer_allowlist) if binding else -1,
        "iterative_reasoning_created": False,
        "recursive_rule_chaining_created": False,
        "deep_search_created": False,
        "conflict_resolution_created": False,
        "verification_proposal_created": False,
        "purpose_created_or_expanded": False,
        "candidate_ordering_created": False,
        "selected_action_created": False,
        "memory_write_created": False,
        "self_state_mutation_created": False,
        "perception_action_created": False,
        "output_created": False,
        "external_control_created": False,
        "semantic_identity_created": False,
        "package_144_implemented": False,
        "full_thought_engine_implemented": False,
        "llm_runtime_calls": 0,
        "codex_runtime_calls": 0,
        "network_runtime_calls": 0,
        "counterfactual_equivalence_verified": checks["counterfactual"],
        "controls_passed": checks["controls"],
        "regressions_passed": checks["regressions"],
        "audit_status": status,
        "failure_reasons": failures,
        "source_record_refs": tuple(
            item
            for item in (
                source.audit.audit_id,
                binding.consumer_binding_id if binding else None,
                contract.workspace_contract_id if contract else None,
                controls.control_result_id if controls else None,
                regression.regression_receipt_id if regression else None,
                counterfactuals[-1].counterfactual_id if counterfactuals else None,
                resets[-1].reset_record_id if resets else None,
            )
            if item
        )
        + tuple(item.conflict_carriage_id for item in conflicts),
    }
    audit = build_hashed_record(
        Package143CoarseThoughtWorkspaceAudit,
        payload,
        id_field="audit_id",
        hash_field="audit_sha256",
        prefix="package_143_audit",
    )
    if append:
        store.append_once("package_143_audits", audit)
        stream = LocalOperatorEventStream(LocalOperatorConsoleStore(output))
        stream.append_event(
            event_kind=(
                "package_143_audit_passed"
                if audit.audit_status == PASS_STATUS
                else "package_143_audit_blocked"
            ),
            source_record_refs=(audit.audit_id,) + audit.source_record_refs,
            source_trace_refs=("trace:package_143:final_audit",),
        )
    return audit


def _typed(store: Package143CoarseWorkspaceStore, table: str, record_type: type[Any]) -> tuple[Any, ...]:
    return tuple(record_type(**item) for item in store.list_payloads(table))


def _require_package_142_audit(present: bool, status: str) -> None:
    if not present:
        raise ValueError("blocked_missing_package_142_audit")
    if status != PACKAGE_142_PASS_STATUS:
        raise ValueError("blocked_package_142_audit_status")


def _required_events_present(state_dir: Path) -> bool:
    try:
        events = LocalOperatorConsoleStore(state_dir).list_payloads(
            "operator_json_events", "sequence_index"
        )
    except (OSError, RuntimeError, sqlite3.Error):
        return False
    kinds = {str(item.get("event_kind")) for item in events}
    required = {
        "coarse_workspace_consumer_bound",
        "coarse_workspace_contract_created",
        "coarse_workspace_session_started",
        "coarse_workspace_result_admitted",
        "coarse_workspace_conflict_carried",
        "coarse_workspace_capacity_eviction",
        "coarse_workspace_entry_invalidated",
        "coarse_workspace_closed",
        "coarse_workspace_fresh_process_reset_verified",
        "coarse_workspace_counterfactual_verified",
    }
    return required.issubset(kinds) and all(
        not item.get("llm_used")
        and not item.get("codex_used")
        and not item.get("network_used")
        for item in events
        if item.get("event_kind") in required
    )


def _validate_external_state_dir(root: Path, output: Path) -> None:
    try:
        output.relative_to(root)
    except ValueError:
        return
    raise ValueError("Package 143 state_dir must be outside the Git repository")


def _repository_pollution_absent(root: Path) -> bool:
    completed = subprocess.run(
        ("git", "status", "--porcelain", "--untracked-files=all"),
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    forbidden_suffixes = (".sqlite3", ".wav", ".pcm", ".pyc")
    for line in completed.stdout.splitlines():
        path = line[3:].strip().strip('"').lower()
        if path.endswith(forbidden_suffixes) or "__pycache__/" in path:
            return False
    return True


def _git_output(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ("git", *arguments),
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _sha256_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()
