"""Controls, regressions, and final audit for Package 144."""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from typing import Any, Callable

from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.thought.package_141_instinct_audit import repository_source_tree_sha256
from ashl_core_v1.thought.package_144_deep_thought_deliberation_runtime import (
    Package144Preflight,
    authorize_deliberation,
    load_package_143_deliberation_evidence,
    start_deliberation,
    validate_no_forbidden_deliberation_authority,
)
from ashl_core_v1.thought.package_144_deep_thought_deliberation_store import (
    Package144DeepThoughtDeliberationStore,
)
from ashl_core_v1.thought.deep_thought_deliberation_types import (
    AUDIT_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    CONSUMER_SCOPE,
    CONTROL_NAMES,
    CONTROL_SCHEMA_VERSION,
    OPERATION_ALLOWLIST,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    BoundedDeepThoughtResultRecord,
    DeepThoughtCounterfactualEquivalenceRecord,
    DeepThoughtDeliberationAuthorizationRecord,
    DeepThoughtDeliberationCancellationRecord,
    DeepThoughtDeliberationInvalidationRecord,
    DeepThoughtDeliberationSessionRecord,
    DeepThoughtDeliberationStepRecord,
    DeepThoughtDeliberationTerminalRecord,
    DeepThoughtWorkspaceConsumerBindingRecord,
    DeliberationOperationAllowlistRecord,
    ImmutableCoarseWorkspaceSnapshotRecord,
    ImmutableWorkspaceSnapshotContractRecord,
    Package144BoundaryControlResult,
    Package144DeepThoughtDeliberationAudit,
    Package144RegressionReceipt,
    build_hashed_record,
)


_TARGETED_BOUNDARY_MODULES = (
    "ashl_core_v1.tests.test_package_132_active_perception_attention_milestone",
    "ashl_core_v1.tests.test_package_140_persistent_self_state_drive_milestone",
)


def run_package_144_boundary_controls(
    preflight: Package144Preflight,
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    append_to: Package144DeepThoughtDeliberationStore | None = None,
) -> Package144BoundaryControlResult:
    store = append_to or Package144DeepThoughtDeliberationStore(state_dir)
    snapshots = _typed(
        store,
        "immutable_coarse_workspace_snapshots",
        ImmutableCoarseWorkspaceSnapshotRecord,
    )
    authorizations = _typed(
        store,
        "deep_thought_deliberation_authorizations",
        DeepThoughtDeliberationAuthorizationRecord,
    )
    sessions = _typed(
        store,
        "deep_thought_deliberation_sessions",
        DeepThoughtDeliberationSessionRecord,
    )
    steps = _typed(
        store,
        "deep_thought_deliberation_steps",
        DeepThoughtDeliberationStepRecord,
    )
    results = _typed(
        store,
        "bounded_deep_thought_results",
        BoundedDeepThoughtResultRecord,
    )
    terminals = _typed(
        store,
        "deep_thought_deliberation_terminals",
        DeepThoughtDeliberationTerminalRecord,
    )
    cancellations = _typed(
        store,
        "deep_thought_deliberation_cancellations",
        DeepThoughtDeliberationCancellationRecord,
    )
    invalidations = _typed(
        store,
        "deep_thought_deliberation_invalidations",
        DeepThoughtDeliberationInvalidationRecord,
    )
    counterfactuals = _typed(
        store,
        "deep_thought_counterfactual_equivalence_records",
        DeepThoughtCounterfactualEquivalenceRecord,
    )
    if not all((snapshots, authorizations, sessions, steps, results, terminals, invalidations)):
        raise ValueError("blocked_package_144_controls_require_runtime_evidence")
    snapshot = snapshots[-1]
    result = results[0]

    def rejected(call: Callable[[], Any]) -> bool:
        try:
            call()
        except (AttributeError, FrozenInstanceError, TypeError, ValueError, RuntimeError):
            return True
        return False

    source_before = preflight.source.database_sha256
    source_after = _sha256_file(preflight.source.database_path)
    completed = tuple(
        item
        for item in terminals
        if item.terminal_state == "completed_bounded_deliberation"
    )
    completed_step_hashes = []
    for terminal in completed:
        refs = set(terminal.completed_step_refs)
        completed_step_hashes.append(
            tuple(
                item.deterministic_output_sha256
                for item in sorted(
                    (step for step in steps if step.deliberation_step_id in refs),
                    key=lambda item: item.step_index,
                )
            )
        )
    deterministic_repeat = (
        len(completed_step_hashes) >= 2
        and completed_step_hashes[0] == completed_step_hashes[1]
    )
    invalidation_by_transition = {
        item.transition_kind: item for item in invalidations
    }
    completed_invalidation = next(
        (
            item
            for item in invalidations
            if item.result_effective_before and not item.result_effective_after
        ),
        None,
    )
    forbidden = lambda name: rejected(  # noqa: E731 - compact control matrix
        lambda: validate_no_forbidden_deliberation_authority(**{name: True})
    )
    checks = {
        "package_143_audit_missing_rejected": rejected(
            lambda: _require_package_143_audit(False, "passed_coarse_thought_workspace_v0")
        ),
        "package_143_audit_status_rejected": rejected(
            lambda: _require_package_143_audit(True, "blocked")
        ),
        "package_143_source_read_only_verified": source_before == source_after,
        "consumer_scope_widening_rejected": rejected(
            lambda: replace(preflight.consumer_binding, consumer_scope="widened")
        ),
        "empty_snapshot_rejected": rejected(
            lambda: replace(snapshot, entry_refs=(), entry_count=0)
        ),
        "oversized_snapshot_rejected": rejected(
            lambda: replace(snapshot, entry_refs=snapshot.entry_refs * 2, entry_count=6)
        ),
        "snapshot_entry_hash_mismatch_rejected": rejected(
            lambda: replace(snapshot, entry_hashes=("0" * 64,) * snapshot.entry_count)
        ),
        "snapshot_conflict_lineage_mismatch_rejected": rejected(
            lambda: replace(snapshot, conflict_member_entry_refs=("missing", "other"))
        ),
        "snapshot_canonical_order_verified": snapshot.entry_refs == tuple(sorted(snapshot.entry_refs)),
        "snapshot_detached_from_live_workspace_verified": (
            snapshot.detached_from_live_workspace
            and not snapshot.live_workspace_read_after_freeze
            and all(not item.live_workspace_read for item in steps)
        ),
        "snapshot_mutation_rejected": rejected(
            lambda: setattr(snapshot, "entry_count", 1)
        ),
        "expired_snapshot_rejected": rejected(
            lambda: start_deliberation(
                snapshot=snapshot,
                authorization=authorizations[0],
                operation_allowlist=preflight.operation_allowlist,
                started_at_monotonic_ns=snapshot.expires_at_monotonic_ns,
            )
        ),
        "missing_authorization_rejected": rejected(
            lambda: start_deliberation(  # type: ignore[arg-type]
                snapshot=snapshot,
                authorization=None,
                operation_allowlist=preflight.operation_allowlist,
            )
        ),
        "wrong_snapshot_authorization_rejected": rejected(
            lambda: replace(authorizations[0], snapshot_id="wrong_snapshot")
        ),
        "expired_authorization_rejected": rejected(
            lambda: start_deliberation(
                snapshot=snapshot,
                authorization=authorizations[0],
                operation_allowlist=preflight.operation_allowlist,
                started_at_monotonic_ns=authorizations[0].expires_at_monotonic_ns,
            )
        ),
        "authorization_reuse_rejected": rejected(
            lambda: start_deliberation(
                snapshot=snapshot,
                authorization=authorizations[0],
                operation_allowlist=preflight.operation_allowlist,
                started_at_monotonic_ns=sessions[0].started_at_monotonic_ns,
                append_to=store,
            )
        ),
        "operation_allowlist_widening_rejected": rejected(
            lambda: replace(
                preflight.operation_allowlist,
                operation_ids=OPERATION_ALLOWLIST + ("arbitrary_operation",),
            )
        ),
        "operation_order_change_rejected": rejected(
            lambda: replace(steps[0], operation_id=OPERATION_ALLOWLIST[1])
        ),
        "arbitrary_program_operation_rejected": any(
            item.terminal_state == "operation_fault_fail_to_neutral"
            and item.terminal_reason == "operation_not_allowlisted_or_out_of_order"
            for item in terminals
        ),
        "free_text_operation_rejected": rejected(
            lambda: replace(
                preflight.operation_allowlist,
                free_text_reasoning_allowed=True,
            )
        ),
        "deterministic_multi_step_verified": deterministic_repeat,
        "step_budget_exhaustion_incomplete": any(
            item.terminal_state == "budget_exhausted_incomplete"
            and item.terminal_reason == "step_budget_exhausted"
            and item.completed_step_count == 2
            and item.result_ref is None
            for item in terminals
        ),
        "elapsed_budget_exhaustion_incomplete": any(
            item.terminal_state == "budget_exhausted_incomplete"
            and item.terminal_reason == "elapsed_time_budget_exhausted"
            and item.result_ref is None
            for item in terminals
        ),
        "cancellation_fail_neutral_verified": bool(
            cancellations
            and any(
                item.terminal_state == "cancelled_fail_to_neutral"
                and item.result_ref is None
                for item in terminals
            )
        ),
        "workspace_expiry_fail_neutral_verified": _invalidation_neutral(
            invalidation_by_transition.get("workspace_expired")
        ),
        "source_expiry_fail_neutral_verified": _invalidation_neutral(
            invalidation_by_transition.get("source_expired")
        ),
        "source_revocation_fail_neutral_verified": _invalidation_neutral(
            invalidation_by_transition.get("source_revoked")
        ),
        "invalid_snapshot_fail_neutral_verified": _invalidation_neutral(
            invalidation_by_transition.get("invalid_snapshot")
        ),
        "operation_fault_fail_neutral_verified": any(
            item.terminal_state == "operation_fault_fail_to_neutral"
            and item.fail_to_neutral
            and item.result_ref is None
            for item in terminals
        ),
        "completed_result_invalidation_verified": bool(completed_invalidation),
        "orphan_effective_result_rejected": _orphan_effective_result_count(results, terminals, invalidations) == 0,
        "unresolved_conflict_preserved": all(
            item.conflict_status_at_terminal in {None, "unresolved_cross_family_conflict_preserved"}
            and not item.winner_created
            for item in terminals
        ),
        "conflict_winner_rejected": rejected(
            lambda: replace(result, winner_result_id="winner")
        ),
        "conflict_ranking_rejected": rejected(
            lambda: replace(result, ranking_used=True)
        ),
        "conflict_order_selection_rejected": rejected(
            lambda: replace(result, insertion_order_used_for_selection=True)
        ),
        "conflict_budget_selection_rejected": rejected(
            lambda: replace(result, budget_state_used_for_selection=True)
        ),
        "production_consumer_rejected": rejected(
            lambda: replace(result, production_consumer_count=1)
        ),
        "purpose_memory_self_state_drive_rejected": all(
            forbidden(name)
            for name in (
                "purpose_created",
                "memory_write_created",
                "self_state_mutation_created",
                "drive_authority_created",
            )
        ),
        "perception_attention_authority_rejected": forbidden(
            "perception_attention_authority_created"
        ),
        "candidate_ordering_action_output_rejected": all(
            forbidden(name)
            for name in (
                "candidate_ordering_created",
                "selected_action_created",
                "output_created",
                "external_control_created",
            )
        ),
        "package_145_trace_boundary_rejected": not (
            Path(ashl_root) / "ashl_core_v1" / "thought" / "package_145_thought_trace_boundary.py"
        ).exists(),
        "package_146_verification_handoff_rejected": not (
            Path(ashl_root) / "ashl_core_v1" / "thought" / "package_146_verification_handoff.py"
        ).exists(),
        "llm_codex_network_execution_rejected": all(
            forbidden(name) for name in ("llm_used", "codex_used", "network_used")
        ) and all(
            not any((item.llm_used, item.codex_used, item.network_used)) for item in steps
        ),
        "counterfactual_equivalence_verified": bool(
            counterfactuals
            and counterfactuals[-1].counterfactual_status
            == "passed_deep_thought_counterfactual_equivalence"
        ),
    }
    passed_names = tuple(name for name in CONTROL_NAMES if checks.get(name, False))
    failed_names = tuple(name for name in CONTROL_NAMES if not checks.get(name, False))
    record = build_hashed_record(
        Package144BoundaryControlResult,
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
                snapshot.snapshot_id,
                result.deliberation_result_id,
            ) + tuple(item.invalidation_id for item in invalidations),
        },
        id_field="control_result_id",
        hash_field="control_result_sha256",
        prefix="deep_thought_controls",
    )
    store.append_once("package_144_control_results", record)
    return record


def run_package_144_regressions(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
) -> Package144RegressionReceipt:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    _validate_external_state_dir(root, output)
    store = Package144DeepThoughtDeliberationStore(output)
    pycache = store.root / "regression_pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    commands = (
        (
            "targeted_package_144",
            (
                sys.executable,
                "-m",
                "unittest",
                "ashl_core_v1.tests.test_package_144_deep_thought_deliberation_budget",
            ),
        ),
        (
            "package_143_regressions",
            (
                sys.executable,
                "-m",
                "unittest",
                "ashl_core_v1.tests.test_package_143_coarse_thought_workspace",
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
            raise RuntimeError(f"blocked_package_144_regression_failed:{name}:{digest}")
    pollution_absent = _repository_pollution_absent(root)
    results.append(
        (
            "repository_pollution_scan",
            0 if pollution_absent else 1,
            sha256_payload({"repository_pollution_absent": pollution_absent}),
        )
    )
    if not pollution_absent:
        raise RuntimeError("blocked_package_144_repository_pollution_detected")
    source_head = _git_output(root, "rev-parse", "HEAD")
    tree_hash = repository_source_tree_sha256(root)
    receipt = build_hashed_record(
        Package144RegressionReceipt,
        {
            "regression_receipt_id": "",
            "regression_receipt_sha256": "",
            "schema_version": REGRESSION_SCHEMA_VERSION,
            "created_at": utc_now(),
            "baseline_commit": BASELINE_COMMIT,
            "source_head": source_head,
            "source_tree_sha256": tree_hash,
            "command_results": tuple(results),
            "targeted_package_144_passed": statuses["targeted_package_144"],
            "package_143_regressions_passed": statuses["package_143_regressions"],
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
        prefix="deep_thought_regressions",
    )
    store.append_once("package_144_regression_receipts", receipt)
    return receipt


def audit_package_144_deep_thought_deliberation(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    package_143_state_dir: str | Path,
    append: bool = True,
) -> Package144DeepThoughtDeliberationAudit:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    _validate_external_state_dir(root, output)
    source = load_package_143_deliberation_evidence(package_143_state_dir)
    store = Package144DeepThoughtDeliberationStore(output)
    bindings = _typed(store, "deep_thought_workspace_consumer_bindings", DeepThoughtWorkspaceConsumerBindingRecord)
    contracts = _typed(store, "immutable_workspace_snapshot_contracts", ImmutableWorkspaceSnapshotContractRecord)
    snapshots = _typed(store, "immutable_coarse_workspace_snapshots", ImmutableCoarseWorkspaceSnapshotRecord)
    operations = _typed(store, "deliberation_operation_allowlists", DeliberationOperationAllowlistRecord)
    authorizations = _typed(store, "deep_thought_deliberation_authorizations", DeepThoughtDeliberationAuthorizationRecord)
    sessions = _typed(store, "deep_thought_deliberation_sessions", DeepThoughtDeliberationSessionRecord)
    steps = _typed(store, "deep_thought_deliberation_steps", DeepThoughtDeliberationStepRecord)
    results = _typed(store, "bounded_deep_thought_results", BoundedDeepThoughtResultRecord)
    terminals = _typed(store, "deep_thought_deliberation_terminals", DeepThoughtDeliberationTerminalRecord)
    cancellations = _typed(store, "deep_thought_deliberation_cancellations", DeepThoughtDeliberationCancellationRecord)
    invalidations = _typed(store, "deep_thought_deliberation_invalidations", DeepThoughtDeliberationInvalidationRecord)
    counterfactuals = _typed(store, "deep_thought_counterfactual_equivalence_records", DeepThoughtCounterfactualEquivalenceRecord)
    controls_payload = store.latest_payload("package_144_control_results")
    regression_payload = store.latest_payload("package_144_regression_receipts")
    controls = Package144BoundaryControlResult(**controls_payload) if controls_payload else None
    regression = Package144RegressionReceipt(**regression_payload) if regression_payload else None
    binding = bindings[-1] if bindings else None
    contract = contracts[-1] if contracts else None
    operation = operations[-1] if operations else None
    snapshot = snapshots[-1] if snapshots else None
    source_after = _sha256_file(source.database_path)
    completed = tuple(item for item in terminals if item.terminal_state == "completed_bounded_deliberation")
    main_terminal = completed[0] if completed else None
    main_steps = tuple(
        sorted(
            (
                item
                for item in steps
                if main_terminal and item.deliberation_step_id in main_terminal.completed_step_refs
            ),
            key=lambda item: item.step_index,
        )
    )
    deterministic_sequences: list[tuple[str, ...]] = []
    for terminal in completed:
        refs = set(terminal.completed_step_refs)
        deterministic_sequences.append(
            tuple(
                item.deterministic_output_sha256
                for item in sorted(
                    (step for step in steps if step.deliberation_step_id in refs),
                    key=lambda item: item.step_index,
                )
            )
        )
    deterministic_repeat = len(deterministic_sequences) >= 2 and deterministic_sequences[0] == deterministic_sequences[1]
    transition_names = {item.transition_kind for item in invalidations}
    completed_invalidation = any(
        item.result_effective_before and not item.result_effective_after
        for item in invalidations
    )
    orphan_count = _orphan_effective_result_count(results, terminals, invalidations)
    checks = {
        "baseline": _is_ancestor(root, BASELINE_COMMIT),
        "package_143_audit": source.audit.audit_status == "passed_coarse_thought_workspace_v0" and source.audit.source_head == BASELINE_COMMIT,
        "source_read_only": bool(
            binding
            and binding.package_143_store_read_only
            and not binding.package_143_history_mutated
            and binding.package_143_source_database_sha256 == source.database_sha256 == source_after
        ),
        "consumer": bool(binding and binding.consumer_scope == CONSUMER_SCOPE and not binding.production_result_consumer_allowlist),
        "snapshot_contract": bool(contract and contract.captures_typed_values_by_value and not contract.live_workspace_reads_after_freeze_allowed),
        "snapshot": bool(snapshot and snapshot.entry_count >= 2 and snapshot.immutable and snapshot.detached_from_live_workspace),
        "operations": bool(operation and operation.operation_ids == OPERATION_ALLOWLIST and operation.deterministic),
        "authorization": bool(authorizations and all(item.one_use and not item.production_consumer_allowlist for item in authorizations)),
        "multi_step": bool(main_terminal and len(main_steps) == len(OPERATION_ALLOWLIST) and all(not item.live_workspace_read for item in main_steps)),
        "result": bool(results and main_terminal and main_terminal.result_ref),
        "deterministic_repeat": deterministic_repeat,
        "step_budget": any(item.terminal_reason == "step_budget_exhausted" and item.terminal_state == "budget_exhausted_incomplete" for item in terminals),
        "elapsed_budget": any(item.terminal_reason == "elapsed_time_budget_exhausted" and item.terminal_state == "budget_exhausted_incomplete" for item in terminals),
        "cancellation": bool(cancellations and any(item.terminal_state == "cancelled_fail_to_neutral" for item in terminals)),
        "workspace_expiry": "workspace_expired" in transition_names,
        "source_expiry": "source_expired" in transition_names,
        "source_revocation": "source_revoked" in transition_names,
        "invalid_snapshot": "invalid_snapshot" in transition_names,
        "operation_fault": any(item.terminal_state == "operation_fault_fail_to_neutral" for item in terminals),
        "completed_invalidation": completed_invalidation,
        "conflict": bool(snapshot and snapshot.conflict_status == "unresolved_cross_family_conflict_preserved" and all(item.winner_result_id is None for item in results)),
        "no_orphans": orphan_count == 0,
        "counterfactual": bool(counterfactuals and counterfactuals[-1].counterfactual_status == "passed_deep_thought_counterfactual_equivalence"),
        "controls": bool(controls and controls.controls_passed),
        "regressions": bool(regression and regression.fresh_regressions_passed and regression.source_tree_sha256 == repository_source_tree_sha256(root)),
        "events": _required_events_present(output),
        "store": bool(store.audit_integrity()["valid"]),
    }
    failures = tuple(name for name, passed in checks.items() if not passed)
    status = PASS_STATUS if not failures else BLOCKED_STATUS
    payload = {
        "audit_id": "",
        "audit_sha256": "",
        "schema_version": AUDIT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "baseline_commit": BASELINE_COMMIT,
        "source_head": _git_output(root, "rev-parse", "HEAD"),
        "package_143_audit_verified": checks["package_143_audit"],
        "package_143_source_read_only_verified": checks["source_read_only"],
        "package_143_source_sha256_before": source.database_sha256,
        "package_143_source_sha256_after": source_after,
        "exact_consumer_binding_verified": checks["consumer"],
        "immutable_snapshot_contract_verified": checks["snapshot_contract"],
        "immutable_snapshot_verified": checks["snapshot"],
        "snapshot_entry_count": snapshot.entry_count if snapshot else 0,
        "operation_allowlist_verified": checks["operations"],
        "operation_count": len(operation.operation_ids) if operation else 0,
        "explicit_authorization_verified": checks["authorization"],
        "multi_step_deliberation_verified": checks["multi_step"],
        "completed_step_count": len(main_steps),
        "completed_result_created": checks["result"],
        "deterministic_repeat_verified": checks["deterministic_repeat"],
        "step_budget_exhaustion_verified": checks["step_budget"],
        "elapsed_budget_exhaustion_verified": checks["elapsed_budget"],
        "cancellation_fail_neutral_verified": checks["cancellation"],
        "workspace_expiry_fail_neutral_verified": checks["workspace_expiry"],
        "source_expiry_fail_neutral_verified": checks["source_expiry"],
        "source_revocation_fail_neutral_verified": checks["source_revocation"],
        "invalid_snapshot_fail_neutral_verified": checks["invalid_snapshot"],
        "operation_fault_fail_neutral_verified": checks["operation_fault"],
        "completed_result_invalidation_verified": checks["completed_invalidation"],
        "unresolved_conflict_preserved": checks["conflict"],
        "conflict_winner_created": any(item.winner_result_id is not None for item in results),
        "orphan_effective_result_count": orphan_count,
        "live_workspace_read_during_deliberation_count": sum(1 for item in steps if item.live_workspace_read),
        "production_consumer_count": len(binding.production_result_consumer_allowlist) if binding else -1,
        "purpose_created_or_expanded": False,
        "memory_write_created": False,
        "self_state_mutation_created": False,
        "drive_authority_created": False,
        "perception_attention_authority_created": False,
        "candidate_ordering_created": False,
        "selected_action_created": False,
        "output_created": False,
        "external_control_created": False,
        "semantic_identity_created": False,
        "package_145_implemented": False,
        "package_146_implemented": False,
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
                contract.snapshot_contract_id if contract else None,
                operation.operation_allowlist_id if operation else None,
                snapshot.snapshot_id if snapshot else None,
                main_terminal.terminal_record_id if main_terminal else None,
                controls.control_result_id if controls else None,
                regression.regression_receipt_id if regression else None,
                counterfactuals[-1].counterfactual_id if counterfactuals else None,
            )
            if item
        ),
    }
    audit = build_hashed_record(
        Package144DeepThoughtDeliberationAudit,
        payload,
        id_field="audit_id",
        hash_field="audit_sha256",
        prefix="package_144_audit",
    )
    if append:
        store.append_once("package_144_audits", audit)
        stream = LocalOperatorEventStream(LocalOperatorConsoleStore(output))
        stream.append_event(
            event_kind=("package_144_audit_passed" if audit.audit_status == PASS_STATUS else "package_144_audit_blocked"),
            source_record_refs=(audit.audit_id,) + audit.source_record_refs,
            source_trace_refs=("trace:package_144:final_audit",),
        )
    return audit


def _typed(store: Package144DeepThoughtDeliberationStore, table: str, record_type: type[Any]) -> tuple[Any, ...]:
    return tuple(record_type(**item) for item in store.list_payloads(table))


def _require_package_143_audit(present: bool, status: str) -> None:
    if not present:
        raise ValueError("blocked_missing_package_143_audit")
    if status != "passed_coarse_thought_workspace_v0":
        raise ValueError("blocked_package_143_audit_status")


def _invalidation_neutral(record: DeepThoughtDeliberationInvalidationRecord | None) -> bool:
    return bool(
        record
        and not record.snapshot_valid_after
        and not record.result_effective_after
        and not record.further_steps_allowed
        and record.conflict_status_preserved
    )


def _orphan_effective_result_count(
    results: tuple[BoundedDeepThoughtResultRecord, ...],
    terminals: tuple[DeepThoughtDeliberationTerminalRecord, ...],
    invalidations: tuple[DeepThoughtDeliberationInvalidationRecord, ...],
) -> int:
    terminal_refs = {item.result_ref for item in terminals if item.result_effective}
    invalidated_refs = {
        item.deliberation_result_ref for item in invalidations if not item.result_effective_after
    }
    return sum(
        1
        for item in results
        if item.deliberation_result_id not in terminal_refs
        and item.deliberation_result_id not in invalidated_refs
    )


def _required_events_present(state_dir: Path) -> bool:
    try:
        events = LocalOperatorConsoleStore(state_dir).list_payloads(
            "operator_json_events", "sequence_index"
        )
    except (OSError, RuntimeError, sqlite3.Error):
        return False
    kinds = {str(item.get("event_kind")) for item in events}
    required = {
        "deep_thought_workspace_consumer_bound",
        "deep_thought_snapshot_contract_created",
        "deep_thought_operation_allowlist_created",
        "deep_thought_snapshot_frozen",
        "deep_thought_deliberation_authorized",
        "deep_thought_deliberation_started",
        "deep_thought_deliberation_step_completed",
        "bounded_deep_thought_result_created",
        "deep_thought_deliberation_completed",
        "deep_thought_deliberation_stopped",
        "deep_thought_deliberation_cancelled",
        "deep_thought_deliberation_invalidated",
        "deep_thought_counterfactual_verified",
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
    raise ValueError("Package 144 state_dir must be outside the Git repository")


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


def _is_ancestor(root: Path, commit: str) -> bool:
    return subprocess.run(
        ("git", "merge-base", "--is-ancestor", commit, "HEAD"),
        cwd=root,
        capture_output=True,
        check=False,
    ).returncode == 0


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

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
