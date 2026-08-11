"""Boundary controls, regressions, and final audit for Package 141."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.thought.instinct_layer_types import (
    AUDIT_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    CLOSED_SPAN_RULE_ID,
    CONTROL_NAMES,
    CONTROL_SCHEMA_VERSION,
    INPUT_EVIDENCE_KIND,
    OPEN_REGION_RULE_ID,
    PACKAGE_132_AUDIT_STATUS,
    PACKAGE_132_CLOSURE_ID,
    PACKAGE_140_AUDIT_STATUS,
    PACKAGE_140_CONTRACT_ID,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    RULE_DEFINITIONS,
    BoundedInstinctSignalRecord,
    InstinctEvaluationBundleRecord,
    InstinctLayerAuthorityInventoryRecord,
    InstinctLayerConsumerBoundaryRecord,
    InstinctRuleContractRecord,
    Package141BoundaryControlResult,
    Package141InstinctLayerRuntimeAudit,
    Package141RegressionReceipt,
    build_hashed_record,
)
from ashl_core_v1.thought.package_141_instinct_runtime import (
    Package141Preflight,
    build_controlled_structural_checkpoint,
    evaluate_instinct_checkpoint,
    load_package_141_preflight,
    validate_no_forbidden_instinct_authority,
)
from ashl_core_v1.thought.package_141_instinct_store import Package141InstinctStore


_TARGETED_BOUNDARY_MODULES = (
    "ashl_core_v1.tests.test_package_128_sufficiency_stop",
    "ashl_core_v1.tests.test_package_132_active_perception_attention_milestone",
    "ashl_core_v1.tests.test_package_140_persistent_self_state_drive_milestone",
)


def run_package_141_boundary_controls(
    preflight: Package141Preflight,
    *,
    append_to: Package141InstinctStore | None = None,
) -> Package141BoundaryControlResult:
    closed = build_controlled_structural_checkpoint("closed")
    opened = build_controlled_structural_checkpoint("open")
    neutral = build_controlled_structural_checkpoint("neutral")
    conflict = build_controlled_structural_checkpoint("conflict")

    def rejected(call: Callable[[], Any]) -> bool:
        try:
            call()
        except (TypeError, ValueError, RuntimeError):
            return True
        return False

    def blocked(
        checkpoint: Any,
        *,
        input_kind: str | None = INPUT_EVIDENCE_KIND,
        safety: str = "clear",
        reason: str | None = None,
    ) -> bool:
        result = evaluate_instinct_checkpoint(
            preflight=preflight,
            checkpoint=checkpoint,
            input_evidence_kind=input_kind,
            hard_safety_gate_status=safety,
        )
        return bool(
            result.bundle.evaluation_status == "blocked_input"
            and (reason is None or reason in result.bundle.failure_reasons)
        )

    closed_first = evaluate_instinct_checkpoint(preflight=preflight, checkpoint=closed)
    closed_repeat = evaluate_instinct_checkpoint(preflight=preflight, checkpoint=closed)
    open_result = evaluate_instinct_checkpoint(preflight=preflight, checkpoint=opened)
    neutral_result = evaluate_instinct_checkpoint(preflight=preflight, checkpoint=neutral)
    conflict_result = evaluate_instinct_checkpoint(preflight=preflight, checkpoint=conflict)
    transport_checkpoint = replace(closed, required_lane_drop_count=1)

    checks = {
        "legacy_thought_signal_authority_rejected": blocked(
            closed,
            input_kind="legacy_thought_signal",
            reason="blocked_unknown_evidence_kind",
        ),
        "legacy_design_rule_authority_rejected": blocked(
            closed,
            input_kind="legacy_reflex_design_rule",
            reason="blocked_unknown_evidence_kind",
        ),
        "drive_input_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(drive_input_used=True)
        ),
        "self_state_readback_input_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(self_state_readback_used=True)
        ),
        "unknown_evidence_blocked": blocked(
            closed,
            input_kind="unknown_structural_record",
            reason="blocked_unknown_evidence_kind",
        ),
        "missing_evidence_blocked": blocked(
            None,
            input_kind=None,
            reason="blocked_missing_structural_evidence",
        ),
        "missing_lineage_blocked": rejected(
            lambda: replace(closed, runtime_session_id="")
        ),
        "transport_fault_blocked": blocked(
            transport_checkpoint,
            reason="blocked_transport_or_compiler_integrity",
        ),
        "hard_safety_block_precedence": blocked(
            closed,
            safety="blocked",
            reason="blocked_hard_safety_precedence",
        ),
        "teacher_authority_override_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(teacher_authority_overridden=True)
        ),
        "purpose_creation_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(purpose_created_or_expanded=True)
        ),
        "purpose_expansion_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(purpose_created_or_expanded=True)
        ),
        "semantic_injection_rejected": rejected(
            lambda: replace(closed, semantic_label="object")
        ),
        "confidence_injection_rejected": rejected(
            lambda: replace(closed, confidence_score=1.0)
        ),
        "selected_action_creation_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(selected_action_created=True)
        ),
        "motor_command_creation_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(motor_command_created=True)
        ),
        "memory_write_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(memory_write_created=True)
        ),
        "self_state_mutation_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(self_state_mutation_created=True)
        ),
        "perception_action_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(perception_action_created=True)
        ),
        "output_creation_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(output_created=True)
        ),
        "external_control_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(external_control_created=True)
        ),
        "deterministic_repeat_verified": bool(
            closed_first.bundle.deterministic_result_sha256
            == closed_repeat.bundle.deterministic_result_sha256
            and closed_first.bundle.matched_rule_ids
            == closed_repeat.bundle.matched_rule_ids
        ),
        "different_condition_different_firing_verified": bool(
            closed_first.bundle.matched_rule_ids == (CLOSED_SPAN_RULE_ID,)
            and open_result.bundle.matched_rule_ids == (OPEN_REGION_RULE_ID,)
        ),
        "neutral_no_match_verified": bool(
            neutral_result.bundle.evaluation_status == "neutral_no_rule_matched"
            and not neutral_result.signals
        ),
        "conflict_preserved_without_selection_verified": bool(
            conflict_result.bundle.evaluation_status == "conflict_preserved_no_selection"
            and conflict_result.conflict is not None
            and conflict_result.conflict.winner_rule_id is None
            and conflict_result.conflict.all_matches_preserved
            and not conflict_result.conflict.action_selection_created
        ),
        "random_rule_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(random_rule_used=True)
        ),
        "llm_codex_network_use_rejected": all(
            rejected(call)
            for call in (
                lambda: validate_no_forbidden_instinct_authority(llm_used=True),
                lambda: validate_no_forbidden_instinct_authority(codex_used=True),
                lambda: validate_no_forbidden_instinct_authority(network_used=True),
            )
        ),
        "package_142_capability_rejected": rejected(
            lambda: validate_no_forbidden_instinct_authority(package_142_implemented=True)
        ),
    }
    passed_names = tuple(name for name in CONTROL_NAMES if checks.get(name, False))
    failed_names = tuple(name for name in CONTROL_NAMES if not checks.get(name, False))
    result = build_hashed_record(
        Package141BoundaryControlResult,
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
                preflight.boundary.boundary_id,
                preflight.rule_contract.rule_contract_id,
                closed_first.bundle.evaluation_bundle_id,
                open_result.bundle.evaluation_bundle_id,
                neutral_result.bundle.evaluation_bundle_id,
                conflict_result.bundle.evaluation_bundle_id,
            ),
        },
        id_field="control_result_id",
        hash_field="control_result_sha256",
        prefix="instinct_controls",
    )
    if append_to is not None:
        append_to.append_once("package_141_control_results", result)
    return result


def run_package_141_regressions(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
) -> Package141RegressionReceipt:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    _validate_external_state_dir(root, output)
    store = Package141InstinctStore(output)
    pycache = store.root / "regression_pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    commands = (
        (
            "targeted_package_141",
            (sys.executable, "-m", "unittest", "ashl_core_v1.tests.test_package_141_instinct_layer_runtime"),
        ),
        (
            "package_128_132_140_regressions",
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
        output_digest = sha256_payload(
            {"stdout": completed.stdout, "stderr": completed.stderr}
        )
        results.append((name, completed.returncode, output_digest))
        statuses[name] = completed.returncode == 0
        if completed.returncode != 0:
            raise RuntimeError(
                f"blocked_package_141_regression_failed:{name}:{output_digest}"
            )
    pollution_absent = _repository_pollution_absent(root)
    results.append(
        (
            "repository_pollution_scan",
            0 if pollution_absent else 1,
            sha256_payload({"repository_pollution_absent": pollution_absent}),
        )
    )
    if not pollution_absent:
        raise RuntimeError("blocked_package_141_repository_pollution_detected")
    source_head = _git_output(root, "rev-parse", "HEAD")
    source_tree_sha256 = repository_source_tree_sha256(root)
    payload = {
        "regression_receipt_id": "",
        "regression_receipt_sha256": "",
        "schema_version": REGRESSION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "baseline_commit": BASELINE_COMMIT,
        "source_head": source_head,
        "source_tree_sha256": source_tree_sha256,
        "command_results": tuple(results),
        "targeted_package_141_passed": statuses["targeted_package_141"],
        "package_128_132_140_regressions_passed": statuses["package_128_132_140_regressions"],
        "full_v1_discover_passed": statuses["full_v1_discover"],
        "compileall_passed": statuses["compileall"],
        "git_diff_check_passed": statuses["git_diff_check"],
        "repository_pollution_absent": pollution_absent,
        "fresh_regressions_passed": all(statuses.values()) and pollution_absent,
        "source_record_refs": (f"git_head:{source_head}", f"source_tree:{source_tree_sha256}"),
    }
    receipt = build_hashed_record(
        Package141RegressionReceipt,
        payload,
        id_field="regression_receipt_id",
        hash_field="regression_receipt_sha256",
        prefix="instinct_regressions",
    )
    store.append_once("package_141_regression_receipts", receipt)
    return receipt


def audit_package_141_instinct_layer_runtime(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    package_132_state_dir: str | Path,
    package_140_state_dir: str | Path,
    append: bool = True,
) -> Package141InstinctLayerRuntimeAudit:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    _validate_external_state_dir(root, output)
    preflight = load_package_141_preflight(
        ashl_root=root,
        package_132_state_dir=package_132_state_dir,
        package_140_state_dir=package_140_state_dir,
    )
    store = Package141InstinctStore(output)
    inventory_payload = store.latest_payload("instinct_authority_inventories")
    boundary_payload = store.latest_payload("instinct_consumer_boundaries")
    contract_payload = store.latest_payload("instinct_rule_contracts")
    control_payload = store.latest_payload("package_141_control_results")
    regression_payload = store.latest_payload("package_141_regression_receipts")
    bundles = tuple(
        InstinctEvaluationBundleRecord(**item)
        for item in store.list_payloads("instinct_evaluation_bundles")
    )
    signals = tuple(
        BoundedInstinctSignalRecord(**item)
        for item in store.list_payloads("bounded_instinct_signals")
    )

    inventory = InstinctLayerAuthorityInventoryRecord(**inventory_payload) if inventory_payload else None
    boundary = InstinctLayerConsumerBoundaryRecord(**boundary_payload) if boundary_payload else None
    rule_contract = InstinctRuleContractRecord(**contract_payload) if contract_payload else None
    controls = Package141BoundaryControlResult(**control_payload) if control_payload else None
    regression = Package141RegressionReceipt(**regression_payload) if regression_payload else None

    matched = tuple(item for item in bundles if item.evaluation_status == "matched_single")
    neutral = tuple(item for item in bundles if item.evaluation_status == "neutral_no_rule_matched")
    blocked = tuple(item for item in bundles if item.evaluation_status == "blocked_input")
    conflicts = tuple(item for item in bundles if item.evaluation_status == "conflict_preserved_no_selection")
    deterministic_repeat = any(
        left.evaluation_bundle_id != right.evaluation_bundle_id
        and left.deterministic_result_sha256 == right.deterministic_result_sha256
        and left.matched_rule_ids == right.matched_rule_ids
        for index, left in enumerate(matched)
        for right in matched[index + 1 :]
    )
    different_condition = bool(
        any(item.matched_rule_ids == (CLOSED_SPAN_RULE_ID,) for item in matched)
        and any(item.matched_rule_ids == (OPEN_REGION_RULE_ID,) for item in matched)
    )
    events_valid = _required_operator_events_present(output)
    source_tree_matches = bool(
        regression
        and regression.source_tree_sha256 == repository_source_tree_sha256(root)
    )
    checks = {
        "package_132_closure": preflight.boundary.package_132_closure_contract_id == PACKAGE_132_CLOSURE_ID,
        "package_132_audit": preflight.boundary.package_132_audit_status == PACKAGE_132_AUDIT_STATUS,
        "package_140_closure": preflight.boundary.package_140_capability_contract_id == PACKAGE_140_CONTRACT_ID,
        "package_140_audit": preflight.boundary.package_140_audit_status == PACKAGE_140_AUDIT_STATUS,
        "inventory": bool(inventory and inventory.inventory_sha256 == preflight.inventory.inventory_sha256),
        "boundary": bool(boundary and boundary.boundary_sha256 == preflight.boundary.boundary_sha256),
        "rule_contract": bool(rule_contract and rule_contract.rule_contract_sha256 == preflight.rule_contract.rule_contract_sha256),
        "deterministic_repeat": deterministic_repeat,
        "different_condition": different_condition,
        "unknown_missing": bool(blocked and neutral),
        "conflict": bool(conflicts and all(len(item.matched_rule_ids) > 1 for item in conflicts)),
        "signals": bool(signals and all(item.revocable and not item.consumed_by_production_runtime for item in signals)),
        "controls": bool(controls and controls.controls_passed),
        "regressions": bool(regression and regression.fresh_regressions_passed and source_tree_matches),
        "events": events_valid,
        "store": bool(store.audit_integrity()["valid"]),
    }
    forbidden_bundle_flags = any(
        any(
            (
                item.purpose_created_or_expanded,
                item.selected_action_created,
                item.motor_command_created,
                item.memory_write_created,
                item.self_state_mutation_created,
                item.perception_action_created,
                item.output_created,
                item.external_control_created,
                item.llm_runtime_calls,
                item.codex_runtime_calls,
                item.network_runtime_calls,
            )
        )
        for item in bundles
    )
    failures = tuple(name for name, passed in checks.items() if not passed)
    if forbidden_bundle_flags:
        failures += ("forbidden_bundle_authority",)
    audit_status = PASS_STATUS if not failures else BLOCKED_STATUS
    source_head = _git_output(root, "rev-parse", "HEAD")
    payload: dict[str, Any] = {
        "audit_id": "",
        "audit_sha256": "",
        "schema_version": AUDIT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "baseline_commit": BASELINE_COMMIT,
        "source_head": source_head,
        "package_132_closure_verified": checks["package_132_closure"],
        "package_132_audit_verified": checks["package_132_audit"],
        "package_140_closure_verified": checks["package_140_closure"],
        "package_140_audit_verified": checks["package_140_audit"],
        "legacy_authority_inventory_verified": checks["inventory"],
        "one_production_input_interface_verified": bool(
            boundary and boundary.production_input_allowlist == (INPUT_EVIDENCE_KIND,)
        ),
        "production_drive_input_count": len(boundary.production_drive_input_allowlist) if boundary else -1,
        "production_readback_input_count": len(boundary.production_self_state_readback_input_allowlist) if boundary else -1,
        "production_output_consumer_count": len(boundary.production_output_consumer_allowlist) if boundary else -1,
        "rule_contract_verified": checks["rule_contract"],
        "fixed_rule_count": len(rule_contract.rule_definitions) if rule_contract else 0,
        "deterministic_repeat_verified": deterministic_repeat,
        "different_structural_condition_verified": different_condition,
        "unknown_missing_evidence_blocked_or_neutral": checks["unknown_missing"],
        "conflict_preserved_without_selection": checks["conflict"],
        "matched_evaluation_count": len(matched),
        "neutral_evaluation_count": len(neutral),
        "blocked_evaluation_count": len(blocked),
        "bounded_signal_count": len(signals),
        "signals_revocable": checks["signals"],
        "hard_safety_precedence_preserved": bool(boundary and boundary.hard_safety_precedence_preserved),
        "teacher_authority_precedence_preserved": bool(boundary and boundary.teacher_authority_precedence_preserved),
        "purpose_created_or_expanded": False,
        "candidate_ordering_created": False,
        "selected_action_created": False,
        "motor_command_created": False,
        "memory_write_created": False,
        "self_state_mutation_created": False,
        "perception_action_created": False,
        "output_created": False,
        "external_control_created": False,
        "semantic_identity_created": False,
        "emotion_or_personality_created": False,
        "package_142_implemented": False,
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
                preflight.boundary.package_132_audit_id,
                preflight.boundary.package_140_audit_id,
                inventory.inventory_id if inventory else None,
                boundary.boundary_id if boundary else None,
                rule_contract.rule_contract_id if rule_contract else None,
                controls.control_result_id if controls else None,
                regression.regression_receipt_id if regression else None,
            )
            if item
        ) + tuple(item.evaluation_bundle_id for item in bundles),
    }
    audit = build_hashed_record(
        Package141InstinctLayerRuntimeAudit,
        payload,
        id_field="audit_id",
        hash_field="audit_sha256",
        prefix="package_141_audit",
    )
    if append:
        store.append_once("package_141_audits", audit)
        _emit_audit_event(output, audit)
    return audit


def repository_source_tree_sha256(root: str | Path) -> str:
    repository = Path(root).resolve()
    completed = subprocess.run(
        ("git", "ls-files", "--cached", "--others", "--exclude-standard"),
        cwd=repository,
        capture_output=True,
        text=True,
        check=True,
    )
    entries: list[tuple[str, int, str]] = []
    for relative in sorted(line.strip() for line in completed.stdout.splitlines() if line.strip()):
        path = repository / relative
        if not path.is_file() or path.is_symlink():
            continue
        lowered = relative.replace("\\", "/").lower()
        if "__pycache__/" in lowered or lowered.endswith((".pyc", ".sqlite3", ".wav", ".pcm")):
            continue
        data = path.read_bytes()
        entries.append((relative.replace("\\", "/"), len(data), sha256_bytes(data)))
    return sha256_payload(entries)


def _required_operator_events_present(state_dir: Path) -> bool:
    try:
        events = LocalOperatorConsoleStore(state_dir).list_payloads(
            "operator_json_events", "sequence_index"
        )
    except (OSError, RuntimeError, sqlite3.Error, NameError):
        return False
    kinds = {str(item.get("event_kind")) for item in events}
    required = {
        "instinct_input_context_bound",
        "instinct_rule_evaluated",
        "bounded_instinct_signal_created",
        "instinct_rule_conflict_preserved",
        "instinct_evaluation_neutral",
        "instinct_evaluation_blocked",
        "instinct_evaluation_completed",
    }
    return required.issubset(kinds) and all(
        not item.get("llm_used")
        and not item.get("codex_used")
        and not item.get("network_used")
        for item in events
        if item.get("event_kind") in required
    )


def _emit_audit_event(
    state_dir: Path,
    audit: Package141InstinctLayerRuntimeAudit,
) -> None:
    from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream

    LocalOperatorEventStream(LocalOperatorConsoleStore(state_dir)).append_event(
        event_kind=(
            "package_141_audit_passed"
            if audit.audit_status == PASS_STATUS
            else "package_141_audit_blocked"
        ),
        source_record_refs=(audit.audit_id,),
        source_trace_refs=audit.source_record_refs,
    )


def _repository_pollution_absent(root: Path) -> bool:
    forbidden_names = {"package_141.sqlite3"}
    for path in root.rglob("*"):
        if any(part in {".git", ".venv"} for part in path.parts):
            continue
        if path.is_file() and (
            path.name in forbidden_names
            or path.suffix.lower() in {".wav", ".pcm"}
        ):
            return False
    return True


def _validate_external_state_dir(root: Path, output: Path) -> None:
    try:
        output.relative_to(root)
    except ValueError:
        return
    raise ValueError("Package 141 state_dir must be outside the repository")


def _git_output(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", *arguments),
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()
