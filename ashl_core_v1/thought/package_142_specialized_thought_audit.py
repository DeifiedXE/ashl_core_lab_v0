"""Controls, regression evidence, and final audit for Package 142."""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.thought.package_141_instinct_audit import repository_source_tree_sha256
from ashl_core_v1.thought.package_142_specialized_thought_runtime import (
    Package142Preflight,
    build_counterfactual_equivalence,
    create_cross_family_conflict,
    evaluate_specialized_precursor,
    invalidate_specialized_results,
    load_package_141_evidence,
    load_package_142_preflight,
    validate_no_forbidden_specialized_authority,
)
from ashl_core_v1.thought.package_142_specialized_thought_store import (
    Package142SpecializedThoughtStore,
)
from ashl_core_v1.thought.specialized_thought_types import (
    AUDIT_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    CLOSED_FAMILY_ID,
    CLOSED_RESULT,
    CONSUMER_SCOPE,
    CONTROL_NAMES,
    CONTROL_SCHEMA_VERSION,
    FAMILY_DEFINITIONS,
    OPEN_FAMILY_ID,
    OPEN_RESULT,
    PACKAGE_141_PASS_STATUS,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    BoundedSpecializedThoughtResultRecord,
    Package142BoundaryControlResult,
    Package142RegressionReceipt,
    Package142SpecializedThoughtAudit,
    SpecializedThoughtCascadeInvalidationRecord,
    SpecializedThoughtCounterfactualEquivalenceRecord,
    SpecializedThoughtCrossFamilyConflictRecord,
    SpecializedThoughtInstinctConsumerBindingRecord,
    SpecializedThoughtRuleEvaluationRecord,
    SpecializedThoughtRuleFamilyContractRecord,
    build_hashed_record,
)


_TARGETED_BOUNDARY_MODULES = (
    "ashl_core_v1.tests.test_package_132_active_perception_attention_milestone",
    "ashl_core_v1.tests.test_package_140_persistent_self_state_drive_milestone",
)


def run_package_142_boundary_controls(
    preflight: Package142Preflight,
    *,
    ashl_root: str | Path,
    append_to: Package142SpecializedThoughtStore | None = None,
) -> Package142BoundaryControlResult:
    signal_map = {item.instinct_signal_id: item for item in preflight.source.signals}
    closed_signal = signal_map[preflight.source.closed_bundle.instinct_signal_refs[0]]
    open_signal = signal_map[preflight.source.open_bundle.instinct_signal_refs[0]]
    base = 10_000_000_000

    def rejected(call: Callable[[], Any]) -> bool:
        try:
            call()
        except (AttributeError, TypeError, ValueError, RuntimeError):
            return True
        return False

    closed = evaluate_specialized_precursor(
        preflight=preflight,
        family_id=CLOSED_FAMILY_ID,
        source_bundle=preflight.source.closed_bundle,
        source_signal=closed_signal,
        bound_at_monotonic_ns=base,
        evaluated_at_monotonic_ns=base + 1,
    )
    open_output = evaluate_specialized_precursor(
        preflight=preflight,
        family_id=OPEN_FAMILY_ID,
        source_bundle=preflight.source.open_bundle,
        source_signal=open_signal,
        bound_at_monotonic_ns=base + 10,
        evaluated_at_monotonic_ns=base + 11,
    )
    conflict_outputs = []
    for offset, signal_ref in enumerate(preflight.source.conflict_bundle.instinct_signal_refs, start=20):
        signal = signal_map[signal_ref]
        # The exact Package 141 annotation determines the family; no perception record is read.
        family_id = (
            CLOSED_FAMILY_ID
            if signal.bounded_annotation == "bounded_visual_closed_span_present"
            else OPEN_FAMILY_ID
        )
        conflict_outputs.append(
            evaluate_specialized_precursor(
                preflight=preflight,
                family_id=family_id,
                source_bundle=preflight.source.conflict_bundle,
                source_signal=signal,
                bound_at_monotonic_ns=base + offset,
                evaluated_at_monotonic_ns=base + offset + 1,
            )
        )
    conflict = create_cross_family_conflict(
        source_bundle=preflight.source.conflict_bundle,
        outputs=tuple(conflict_outputs),
    )
    expiry = invalidate_specialized_results(
        output=closed,
        transition_kind="upstream_precursor_expired",
        observed_at_monotonic_ns=closed.precursor_binding.expires_at_monotonic_ns,
    )
    revocation = invalidate_specialized_results(
        output=open_output,
        transition_kind="upstream_precursor_revoked",
        observed_at_monotonic_ns=open_output.evaluation.evaluated_at_monotonic_ns + 1,
    )
    expired_evaluation = evaluate_specialized_precursor(
        preflight=preflight,
        family_id=CLOSED_FAMILY_ID,
        source_bundle=preflight.source.closed_bundle,
        source_signal=closed_signal,
        bound_at_monotonic_ns=base + 100,
        evaluated_at_monotonic_ns=base + 100 + 1_000_000_000,
    )
    counterfactual = build_counterfactual_equivalence(
        root=Path(ashl_root).resolve(),
        source_sha256_before=preflight.source.database_sha256,
        source_sha256_after=preflight.source.database_sha256,
        source_record_refs=(preflight.consumer_binding.consumer_binding_id,),
    )

    forbidden = lambda name: rejected(  # noqa: E731 - compact control table
        lambda: validate_no_forbidden_specialized_authority(**{name: True})
    )
    checks = {
        "package_141_audit_missing_rejected": rejected(lambda: _require_package_141_audit(False, PACKAGE_141_PASS_STATUS)),
        "package_141_audit_status_rejected": rejected(lambda: _require_package_141_audit(True, "blocked")),
        "unknown_precursor_schema_rejected": rejected(lambda: replace(closed_signal, schema_version="unknown")),
        "unknown_precursor_annotation_rejected": rejected(lambda: replace(closed_signal, bounded_annotation="unknown")),
        "nonrevocable_precursor_rejected": rejected(lambda: replace(closed_signal, revocable=False)),
        "consumed_precursor_rejected": rejected(lambda: replace(closed_signal, consumed_by_production_runtime=True)),
        "wrong_family_input_rejected": rejected(
            lambda: evaluate_specialized_precursor(
                preflight=preflight,
                family_id=OPEN_FAMILY_ID,
                source_bundle=preflight.source.closed_bundle,
                source_signal=closed_signal,
            )
        ),
        "missing_precursor_lineage_rejected": rejected(
            lambda: evaluate_specialized_precursor(
                preflight=preflight,
                family_id=CLOSED_FAMILY_ID,
                source_bundle=preflight.source.open_bundle,
                source_signal=closed_signal,
            )
        ),
        "expired_precursor_blocked": expired_evaluation.evaluation.evaluation_status == "blocked_expired_precursor" and expired_evaluation.result is None,
        "revoked_precursor_blocked": rejected(
            lambda: evaluate_specialized_precursor(
                preflight=preflight,
                family_id=CLOSED_FAMILY_ID,
                source_bundle=preflight.source.closed_bundle,
                source_signal=closed_signal,
                precursor_revoked=True,
            )
        ),
        "specialized_result_as_input_rejected": rejected(
            lambda: evaluate_specialized_precursor(
                preflight=preflight,
                family_id=CLOSED_FAMILY_ID,
                source_bundle=preflight.source.closed_bundle,
                source_signal=closed.result,  # type: ignore[arg-type]
            )
        ),
        "recursive_same_family_evaluation_rejected": forbidden("recursive_input_used"),
        "arbitrary_rule_chaining_rejected": forbidden("arbitrary_rule_chaining_used"),
        "persistent_workspace_rejected": forbidden("workspace_created"),
        "iterative_search_rejected": forbidden("iterative_search_used"),
        "conflict_winner_rejected": rejected(lambda: replace(conflict, winner_result_id="winner")),
        "conflict_ranking_rejected": rejected(lambda: replace(conflict, ranking_used=True)),
        "conflict_voting_rejected": rejected(lambda: replace(conflict, voting_used=True)),
        "conflict_random_tie_break_rejected": rejected(lambda: replace(conflict, random_tie_break_used=True)),
        "semantic_injection_rejected": rejected(lambda: replace(closed.result, semantic_label="meaning")),
        "purpose_creation_rejected": forbidden("purpose_created_or_expanded"),
        "candidate_ordering_rejected": forbidden("candidate_ordering_created"),
        "selected_action_rejected": forbidden("selected_action_created"),
        "memory_write_rejected": forbidden("memory_write_created"),
        "self_state_mutation_rejected": forbidden("self_state_mutation_created"),
        "perception_action_rejected": forbidden("perception_action_created"),
        "output_creation_rejected": forbidden("output_created"),
        "external_control_rejected": forbidden("external_control_created"),
        "drive_input_rejected": forbidden("drive_input_used"),
        "self_state_readback_input_rejected": forbidden("self_state_readback_used"),
        "hard_safety_override_rejected": forbidden("hard_safety_overridden"),
        "teacher_authority_override_rejected": forbidden("teacher_authority_overridden"),
        "approved_purpose_expansion_rejected": forbidden("approved_purpose_scope_expanded"),
        "legacy_thought_signal_rejected": forbidden("legacy_thought_signal_used"),
        "direct_perception_input_rejected": forbidden("direct_perception_input_used"),
        "upstream_expiry_cascade_verified": expiry.transition_kind == "upstream_precursor_expired" and not expiry.result_valid_after_transition,
        "upstream_revocation_cascade_verified": revocation.transition_kind == "upstream_precursor_revoked" and not revocation.dangling_specialized_result,
        "counterfactual_equivalence_verified": counterfactual.counterfactual_status == "passed_specialized_thought_counterfactual_equivalence",
        "package_143_capability_rejected": forbidden("package_143_implemented"),
        "llm_codex_network_use_rejected": all(forbidden(name) for name in ("llm_used", "codex_used", "network_used")),
    }
    passed_names = tuple(name for name in CONTROL_NAMES if checks.get(name, False))
    failed_names = tuple(name for name in CONTROL_NAMES if not checks.get(name, False))
    result = build_hashed_record(
        Package142BoundaryControlResult,
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
                closed.evaluation.specialized_evaluation_id,
                open_output.evaluation.specialized_evaluation_id,
                conflict.conflict_id,
                expiry.invalidation_id,
                revocation.invalidation_id,
                counterfactual.counterfactual_id,
            ),
        },
        id_field="control_result_id",
        hash_field="control_result_sha256",
        prefix="specialized_controls",
    )
    if append_to is not None:
        append_to.append_once("package_142_control_results", result)
    return result


def run_package_142_regressions(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
) -> Package142RegressionReceipt:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    _validate_external_state_dir(root, output)
    store = Package142SpecializedThoughtStore(output)
    pycache = store.root / "regression_pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    commands = (
        (
            "targeted_package_142",
            (sys.executable, "-m", "unittest", "ashl_core_v1.tests.test_package_142_specialized_thought_bounded_rules"),
        ),
        (
            "package_141_regressions",
            (sys.executable, "-m", "unittest", "ashl_core_v1.tests.test_package_141_instinct_layer_runtime"),
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
            raise RuntimeError(f"blocked_package_142_regression_failed:{name}:{digest}")
    pollution_absent = _repository_pollution_absent(root)
    results.append(("repository_pollution_scan", 0 if pollution_absent else 1, sha256_payload({"repository_pollution_absent": pollution_absent})))
    if not pollution_absent:
        raise RuntimeError("blocked_package_142_repository_pollution_detected")
    source_head = _git_output(root, "rev-parse", "HEAD")
    tree_hash = repository_source_tree_sha256(root)
    receipt = build_hashed_record(
        Package142RegressionReceipt,
        {
            "regression_receipt_id": "",
            "regression_receipt_sha256": "",
            "schema_version": REGRESSION_SCHEMA_VERSION,
            "created_at": utc_now(),
            "baseline_commit": BASELINE_COMMIT,
            "source_head": source_head,
            "source_tree_sha256": tree_hash,
            "command_results": tuple(results),
            "targeted_package_142_passed": statuses["targeted_package_142"],
            "package_141_regressions_passed": statuses["package_141_regressions"],
            "package_132_140_boundary_regressions_passed": statuses["package_132_140_boundary_regressions"],
            "full_v1_discover_passed": statuses["full_v1_discover"],
            "compileall_passed": statuses["compileall"],
            "git_diff_check_passed": statuses["git_diff_check"],
            "repository_pollution_absent": pollution_absent,
            "fresh_regressions_passed": all(statuses.values()) and pollution_absent,
            "source_record_refs": (f"git_head:{source_head}", f"source_tree:{tree_hash}"),
        },
        id_field="regression_receipt_id",
        hash_field="regression_receipt_sha256",
        prefix="specialized_regressions",
    )
    store.append_once("package_142_regression_receipts", receipt)
    return receipt


def audit_package_142_specialized_thought(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    package_141_state_dir: str | Path,
    append: bool = True,
) -> Package142SpecializedThoughtAudit:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    _validate_external_state_dir(root, output)
    source = load_package_141_evidence(package_141_state_dir)
    store = Package142SpecializedThoughtStore(output)
    bindings = _typed(store, "specialized_thought_consumer_bindings", SpecializedThoughtInstinctConsumerBindingRecord)
    families = _typed(store, "specialized_thought_rule_family_contracts", SpecializedThoughtRuleFamilyContractRecord)
    evaluations = _typed(store, "specialized_thought_rule_evaluations", SpecializedThoughtRuleEvaluationRecord)
    results = _typed(store, "bounded_specialized_thought_results", BoundedSpecializedThoughtResultRecord)
    conflicts = _typed(store, "specialized_thought_cross_family_conflicts", SpecializedThoughtCrossFamilyConflictRecord)
    invalidations = _typed(store, "specialized_thought_cascade_invalidations", SpecializedThoughtCascadeInvalidationRecord)
    counterfactuals = _typed(store, "specialized_thought_counterfactual_equivalence_records", SpecializedThoughtCounterfactualEquivalenceRecord)
    controls_payload = store.latest_payload("package_142_control_results")
    regression_payload = store.latest_payload("package_142_regression_receipts")
    controls = Package142BoundaryControlResult(**controls_payload) if controls_payload else None
    regression = Package142RegressionReceipt(**regression_payload) if regression_payload else None
    binding = bindings[-1] if bindings else None
    source_after = _sha256_file(source.database_path)
    grouped: dict[tuple[str, str], list[SpecializedThoughtRuleEvaluationRecord]] = {}
    for item in evaluations:
        if item.evaluation_status == "matched":
            grouped.setdefault((item.family_id, item.source_instinct_signal_refs[0]), []).append(item)
    deterministic_repeat = any(
        len(items) >= 2 and len({item.deterministic_result_sha256 for item in items}) == 1
        for items in grouped.values()
    )
    invalidated_refs = {
        ref for item in invalidations for ref in item.specialized_result_refs
    }
    dangling_count = sum(item.specialized_result_id not in invalidated_refs for item in results)
    family_allowlists = bool(
        len({item.family_id for item in families}) == len(FAMILY_DEFINITIONS)
        and all(len(item.input_annotation_allowlist) == 1 and len(item.output_annotation_allowlist) == 1 for item in families)
    )
    event_check = _required_events_present(output)
    store_check = store.audit_integrity()["valid"]
    source_read_only = bool(
        binding
        and binding.package_141_store_read_only
        and not binding.package_141_history_mutated
        and binding.package_141_source_database_sha256 == source.database_sha256 == source_after
    )
    checks = {
        "package_141_audit": source.audit.audit_status == PACKAGE_141_PASS_STATUS and source.audit.source_head == BASELINE_COMMIT,
        "source_read_only": source_read_only,
        "consumer_binding": bool(binding and binding.consumer_scope == CONSUMER_SCOPE),
        "families": family_allowlists,
        "deterministic_repeat": deterministic_repeat,
        "closed_firing": any(item.bounded_result_annotation == CLOSED_RESULT for item in results),
        "open_firing": any(item.bounded_result_annotation == OPEN_RESULT for item in results),
        "conflict": bool(conflicts and all(item.conflict_status == "unresolved_cross_family_conflict_preserved" and item.winner_result_id is None for item in conflicts)),
        "expiry": any(item.transition_kind == "upstream_precursor_expired" and not item.result_valid_after_transition for item in invalidations),
        "revocation": any(item.transition_kind == "upstream_precursor_revoked" and not item.result_valid_after_transition for item in invalidations),
        "no_dangling": dangling_count == 0 and bool(results),
        "counterfactual": bool(counterfactuals and counterfactuals[-1].counterfactual_status == "passed_specialized_thought_counterfactual_equivalence"),
        "controls": bool(controls and controls.controls_passed),
        "regressions": bool(regression and regression.fresh_regressions_passed and regression.source_tree_sha256 == repository_source_tree_sha256(root)),
        "events": event_check,
        "store": bool(store_check),
    }
    failures = tuple(name for name, passed in checks.items() if not passed)
    audit_status = PASS_STATUS if not failures else BLOCKED_STATUS
    payload = {
        "audit_id": "",
        "audit_sha256": "",
        "schema_version": AUDIT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "baseline_commit": BASELINE_COMMIT,
        "source_head": _git_output(root, "rev-parse", "HEAD"),
        "package_141_audit_verified": checks["package_141_audit"],
        "package_141_source_read_only_verified": checks["source_read_only"],
        "package_141_source_sha256_before": source.database_sha256,
        "package_141_source_sha256_after": source_after,
        "exact_consumer_binding_verified": checks["consumer_binding"],
        "direct_perception_input_count": 0,
        "legacy_thought_signal_input_count": 0,
        "production_drive_input_count": len(binding.production_drive_input_allowlist) if binding else -1,
        "production_readback_input_count": len(binding.production_self_state_readback_input_allowlist) if binding else -1,
        "production_output_consumer_count": len(binding.production_output_consumer_allowlist) if binding else -1,
        "specialized_rule_family_count": len({item.family_id for item in families}),
        "family_input_output_allowlists_verified": checks["families"],
        "deterministic_repeat_verified": checks["deterministic_repeat"],
        "closed_family_firing_verified": checks["closed_firing"],
        "open_family_firing_verified": checks["open_firing"],
        "cross_family_conflict_preserved": checks["conflict"],
        "unresolved_conflict_count": len(conflicts),
        "conflict_winner_created": any(item.winner_result_id is not None for item in conflicts),
        "precursor_expiry_cascade_verified": checks["expiry"],
        "precursor_revocation_cascade_verified": checks["revocation"],
        "dangling_specialized_result_count": dangling_count,
        "recursive_thought_created": False,
        "arbitrary_rule_chaining_created": False,
        "persistent_state_created": False,
        "workspace_created": False,
        "iterative_search_created": False,
        "counterfactual_equivalence_verified": checks["counterfactual"],
        "hard_safety_precedence_preserved": bool(binding and binding.hard_safety_precedence_preserved),
        "teacher_authority_precedence_preserved": bool(binding and binding.teacher_authority_precedence_preserved),
        "approved_purpose_scope_preserved": bool(binding and binding.approved_purpose_scope_preserved),
        "purpose_created_or_expanded": False,
        "candidate_ordering_created": False,
        "selected_action_created": False,
        "memory_write_created": False,
        "self_state_mutation_created": False,
        "perception_action_created": False,
        "output_created": False,
        "external_control_created": False,
        "semantic_identity_created": False,
        "package_143_implemented": False,
        "full_thought_engine_implemented": False,
        "llm_runtime_calls": 0,
        "codex_runtime_calls": 0,
        "network_runtime_calls": 0,
        "controls_passed": checks["controls"],
        "regressions_passed": checks["regressions"],
        "audit_status": audit_status,
        "failure_reasons": failures,
        "source_record_refs": tuple(
            item
            for item in (
                source.audit.audit_id,
                binding.consumer_binding_id if binding else None,
                controls.control_result_id if controls else None,
                regression.regression_receipt_id if regression else None,
                counterfactuals[-1].counterfactual_id if counterfactuals else None,
            )
            if item
        ) + tuple(item.conflict_id for item in conflicts),
    }
    audit = build_hashed_record(
        Package142SpecializedThoughtAudit,
        payload,
        id_field="audit_id",
        hash_field="audit_sha256",
        prefix="package_142_audit",
    )
    if append:
        store.append_once("package_142_audits", audit)
        stream = LocalOperatorEventStream(LocalOperatorConsoleStore(output))
        stream.append_event(
            event_kind="package_142_audit_passed" if audit.audit_status == PASS_STATUS else "package_142_audit_blocked",
            source_record_refs=(audit.audit_id,) + audit.source_record_refs,
            source_trace_refs=("trace:package_142:final_audit",),
        )
    return audit


def _typed(store: Package142SpecializedThoughtStore, table: str, record_type: type[Any]) -> tuple[Any, ...]:
    return tuple(record_type(**item) for item in store.list_payloads(table))


def _require_package_141_audit(present: bool, status: str) -> None:
    if not present:
        raise ValueError("blocked_missing_package_141_audit")
    if status != PACKAGE_141_PASS_STATUS:
        raise ValueError("blocked_package_141_audit_status")


def _required_events_present(state_dir: Path) -> bool:
    try:
        events = LocalOperatorConsoleStore(state_dir).list_payloads(
            "operator_json_events", "sequence_index"
        )
    except (OSError, RuntimeError, sqlite3.Error):
        return False
    kinds = {str(item.get("event_kind")) for item in events}
    required = {
        "specialized_thought_consumer_bound",
        "specialized_thought_rule_family_loaded",
        "specialized_thought_precursor_bound",
        "specialized_thought_rule_evaluated",
        "bounded_specialized_thought_result_created",
        "specialized_thought_cross_family_conflict_preserved",
        "specialized_thought_result_invalidated",
        "specialized_thought_counterfactual_verified",
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
    raise ValueError("Package 142 state_dir must be outside the Git repository")


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
    return sha256_bytes(path.read_bytes())
