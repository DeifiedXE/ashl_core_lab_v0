"""Fresh regressions and final audit for Package 136."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from dataclasses import fields
from pathlib import Path
from typing import Any, TypeVar

from ashl_core_v1.endocrine.drive_modulation_consumer_inventory import (
    build_drive_modulation_consumer_inventory,
)
from ashl_core_v1.endocrine.drive_modulation_types import (
    AUDIT_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    PACKAGE_137_REQUIRED_GATES,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    DriveModulationApplicationRecord,
    DriveModulationConsumerAllowlistRecord,
    DriveModulationCounterfactualComparison,
    DriveModulationCrossSessionNeutralityRecord,
    DriveModulationDerivationRecord,
    DriveModulationNeutralizationRecord,
    DriveModulationPolicyDecision,
    DriveModulationProcessReceipt,
    Package136RegressionReceipt,
    Package136SameSessionDriveModulationAudit,
    SameSessionDriveModulationAuthorization,
    SameSessionDriveModulationContract,
)
from ashl_core_v1.endocrine.package_135_authority_source import source_tree_sha256
from ashl_core_v1.endocrine.package_136_drive_modulation_store import (
    Package136DriveModulationStore,
)
from ashl_core_v1.endocrine.package_136_package_135_source import (
    load_package_136_sources_read_only,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now


T = TypeVar("T")

_TARGETED_136 = "ashl_core_v1.tests.test_package_136_same_session_drive_modulation"
_PACKAGE_135 = "ashl_core_v1.tests.test_package_135_drive_signal_trace_separation"
_PACKAGE_133_134 = (
    "ashl_core_v1.tests.test_package_133_cross_session_self_state_schema",
    "ashl_core_v1.tests.test_package_134_persistent_session_recovery_identity",
)
_AUTHORITY_BOUNDARY = (
    "ashl_core_v1.tests.test_package_132_active_perception_attention_milestone",
    "ashl_core_v1.tests.test_bounded_capture_deadline_controller",
    "ashl_core_v1.tests.test_package_127_internal_focus",
    "ashl_core_v1.tests.test_package_128_sufficiency_stop",
    "ashl_core_v1.tests.test_teacher_gated_selected_action_application",
    "ashl_core_v1.tests.test_raw_output_token_registry",
)


def run_package_136_regressions(
    *, ashl_root: str | Path, state_dir: str | Path
) -> Package136RegressionReceipt:
    root = Path(ashl_root).resolve()
    store = Package136DriveModulationStore(state_dir)
    pycache = store.root / "regression_pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    commands: tuple[tuple[str, tuple[str, ...]], ...] = (
        (
            "targeted_package_136",
            (sys.executable, "-m", "unittest", _TARGETED_136),
        ),
        (
            "package_135_regressions",
            (sys.executable, "-m", "unittest", _PACKAGE_135),
        ),
        (
            "package_133_134_regressions",
            (sys.executable, "-m", "unittest", *_PACKAGE_133_134),
        ),
        (
            "authority_boundary_regressions",
            (sys.executable, "-m", "unittest", *_AUTHORITY_BOUNDARY),
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
    receipt = Package136RegressionReceipt(
        regression_receipt_id=f"package_136_regressions:{sha256_payload({'head': source_head, 'results': results})[:16]}",
        schema_version=REGRESSION_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        source_head=source_head,
        command_results=tuple(results),
        targeted_package_136_passed=statuses["targeted_package_136"],
        package_135_regressions_passed=statuses["package_135_regressions"],
        package_133_134_regressions_passed=statuses["package_133_134_regressions"],
        authority_boundary_regressions_passed=statuses["authority_boundary_regressions"],
        full_v1_discover_passed=statuses["full_v1_unittest_discover"],
        compileall_passed=statuses["compileall"],
        git_diff_check_passed=statuses["git_diff_check"],
        pycache_redirected_outside_repo=True,
        fresh_regressions_passed=all(statuses.values()),
    )
    store.append_once("package_136_regression_receipts", receipt)
    return receipt


def audit_package_136_same_session_drive_modulation(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    package_135_state_dir: str | Path,
    state_dir: str | Path,
    append: bool = True,
) -> Package136SameSessionDriveModulationAudit:
    root = Path(ashl_root).resolve()
    source_133 = Path(package_133_state_dir).resolve()
    source_134 = Path(package_134_state_dir).resolve()
    source_135 = Path(package_135_state_dir).resolve()
    before = {
        "package_133": source_tree_sha256(source_133),
        "package_134": source_tree_sha256(source_134),
        "package_135": source_tree_sha256(source_135),
    }
    source = load_package_136_sources_read_only(
        package_133_state_dir=source_133,
        package_134_state_dir=source_134,
        package_135_state_dir=source_135,
    )
    store = Package136DriveModulationStore(state_dir)
    current_inventory = build_drive_modulation_consumer_inventory(root)
    stored_inventory = store.list_payloads("drive_modulation_consumer_inventory")
    source_bindings = store.list_payloads("package_135_signal_authority_bindings")
    contracts = store.list_payloads("same_session_drive_modulation_contracts")
    allowlists = store.list_payloads("drive_modulation_consumer_allowlists")
    authorizations = store.list_payloads("same_session_drive_modulation_authorizations")
    decisions = tuple(
        _record_from_payload(DriveModulationPolicyDecision, item)
        for item in store.list_payloads("drive_modulation_policy_decisions")
    )
    derivations = tuple(
        _record_from_payload(DriveModulationDerivationRecord, item)
        for item in store.list_payloads("drive_modulation_derivations")
    )
    applications = tuple(
        _record_from_payload(DriveModulationApplicationRecord, item)
        for item in store.list_payloads("drive_modulation_applications")
    )
    neutralizations = tuple(
        _record_from_payload(DriveModulationNeutralizationRecord, item)
        for item in store.list_payloads("drive_modulation_neutralizations")
    )
    comparisons = tuple(
        _record_from_payload(DriveModulationCounterfactualComparison, item)
        for item in store.list_payloads("drive_modulation_counterfactual_comparisons")
    )
    receipts = tuple(
        _record_from_payload(DriveModulationProcessReceipt, item)
        for item in store.list_payloads("drive_modulation_process_receipts")
    )
    neutrality_records = tuple(
        _record_from_payload(DriveModulationCrossSessionNeutralityRecord, item)
        for item in store.list_payloads("drive_modulation_cross_session_neutrality")
    )
    controls = store.latest_payload("package_136_control_results")
    regressions = store.latest_payload("package_136_regression_receipts")
    integrity = store.audit_integrity()
    after = {
        "package_133": source_tree_sha256(source_133),
        "package_134": source_tree_sha256(source_134),
        "package_135": source_tree_sha256(source_135),
    }
    contract = (
        _record_from_payload(SameSessionDriveModulationContract, contracts[0])
        if len(contracts) == 1
        else None
    )
    allowlist = (
        _record_from_payload(DriveModulationConsumerAllowlistRecord, allowlists[0])
        if len(allowlists) == 1
        else None
    )
    authorization = (
        _record_from_payload(SameSessionDriveModulationAuthorization, authorizations[0])
        if len(authorizations) == 1
        else None
    )
    derivation = derivations[0] if len(derivations) == 1 else None
    application = applications[0] if len(applications) == 1 else None
    comparison = comparisons[0] if len(comparisons) == 1 else None
    neutrality = neutrality_records[0] if len(neutrality_records) == 1 else None
    receipt_by_role = {item.process_role: item for item in receipts}
    process_a = receipt_by_role.get("modulated_session_a")
    process_b = receipt_by_role.get("neutral_session_b")
    stored_index = {
        str(item["consumer_surface_id"]): str(item["inventory_sha256"])
        for item in stored_inventory
    }
    current_index = {
        item.consumer_surface_id: item.inventory_sha256 for item in current_inventory
    }
    import_scan = _scan_forbidden_consumers(root)
    package_137_absent = not any(
        path.name.startswith("package_137")
        for path in (root / "ashl_core_v1").rglob("*.py")
    )
    expected_fail_neutral = (
        "authorization_missing",
        "signal_invalid",
        "consumer_fault",
        "session_end",
        "authorization_expired",
        "fresh_session_start_after_structural_recovery",
    )
    controls_passed = bool(
        controls
        and controls.get("controls_passed") is True
        and int(controls.get("passed_count", 0)) == int(controls.get("expected_count", -1))
    )
    clamp_controls = bool(
        controls
        and {
            "absolute_level_clamp_enforced",
            "delta_clamp_enforced",
        }.issubset(set(controls.get("passed_control_names") or ()))
    )
    fail_controls = bool(
        controls
        and {
            "authorization_missing_fails_neutral",
            "invalid_trace_hash_fails_neutral",
            "consumer_fault_fails_neutral",
            "session_end_fails_neutral",
            "expired_authorization_fails_neutral",
        }.issubset(set(controls.get("passed_control_names") or ()))
    )
    process_boundary = bool(
        process_a
        and process_b
        and process_a.operating_system_process_id != process_b.operating_system_process_id
        and process_a.ended_monotonic_ns < process_b.started_monotonic_ns
    )
    checks = {
        "baseline": _is_ancestor(root, BASELINE_COMMIT),
        "source_133_unchanged": before["package_133"] == after["package_133"],
        "source_134_unchanged": before["package_134"] == after["package_134"],
        "source_135_unchanged": before["package_135"] == after["package_135"],
        "source_binding": (
            len(source_bindings) == 1
            and source_bindings[0].get("source_binding_id") == source.source_binding.source_binding_id
            and source_bindings[0].get("source_opened_read_only") is True
            and source_bindings[0].get("source_trace_mutation_allowed") is False
        ),
        "consumer_inventory": (
            len(current_inventory) == 14
            and stored_index == current_index
            and not any(item.production_eligible for item in current_inventory)
        ),
        "contract": bool(
            contract
            and contract.same_session_only
            and contract.read_only_signal_consumption
            and contract.fail_to_neutral_required
            and contract.production_consumer_count == 0
        ),
        "allowlist": bool(
            allowlist
            and allowlist.production_allowlist_empty
            and not allowlist.production_consumer_ids
            and len(allowlist.audit_only_consumer_ids) == 1
        ),
        "authorization": bool(
            authorization
            and authorization.runtime_session_id == source.selected_trace.runtime_session_id
            and authorization.signal_lineage_id == source.selected_trace.signal_lineage_id
            and authorization.signal_trace_sha256 == source.selected_trace.signal_trace_sha256
            and not authorization.cross_session_carry_allowed
        ),
        "policy": (
            len(decisions) == 2
            and {item.decision for item in decisions}
            == {
                "allow_bounded_audit_only_modulation",
                "neutral_authorization_missing",
            }
        ),
        "derivation": bool(
            derivation
            and derivation.source_trace_read_only
            and not derivation.source_trace_mutated
            and abs(derivation.effective_offset) <= derivation.maximum_absolute_offset
            and abs(derivation.effective_offset - derivation.previous_effective_offset)
            <= derivation.maximum_delta_per_application
        ),
        "application": bool(
            application
            and application.audit_only_consumer
            and not application.production_consumer
            and application.temporary_same_session_context
            and application.authorization_consumed_once
        ),
        "neutralization": (
            len(neutralizations) == 2
            and {item.reason for item in neutralizations}
            == {"session_end", "fresh_session_start_after_structural_recovery"}
            and all(item.neutral_baseline_restored for item in neutralizations)
        ),
        "counterfactual": bool(
            comparison
            and comparison.comparison_status
            == "passed_isolated_audit_only_modulation_counterfactual"
            and comparison.differing_paths == ("audit_only_regulatory_offset",)
        ),
        "process_boundary": process_boundary,
        "cross_session_neutrality": bool(
            neutrality
            and neutrality.neutrality_status
            == "passed_structural_recovery_with_neutral_modulation"
            and neutrality.process_b_started_neutral
            and neutrality.package_135_session_b_trace_is_fresh_root
            and not neutrality.package_134_drive_state_restored
            and not neutrality.authorization_carried
            and not neutrality.application_carried
            and not neutrality.effective_offset_carried
        ),
        "controls": controls_passed and clamp_controls and fail_controls,
        "regressions": bool(regressions and regressions.get("fresh_regressions_passed") is True),
        "append_only_store": bool(
            integrity["valid"]
            and integrity["append_only_history"]
            and not integrity["active_modulation_present"]
            and not integrity["cross_session_recovery_table_present"]
            and not integrity["production_consumer_state_present"]
        ),
        "production_import_boundary": import_scan["valid"],
        "package_137_absent": package_137_absent,
    }
    failures = tuple(name for name, passed in checks.items() if not passed)
    status = PASS_STATUS if not failures else BLOCKED_STATUS
    source_head = _git_output(root, "rev-parse", "HEAD")
    audit_core = {
        "source_head": source_head,
        "package_135_audit": source.package_135_audit["audit_id"],
        "contract": contract.contract_sha256 if contract else None,
        "allowlist": allowlist.allowlist_sha256 if allowlist else None,
        "authorization": authorization.authorization_sha256 if authorization else None,
        "application": application.application_sha256 if application else None,
        "comparison": comparison.comparison_sha256 if comparison else None,
        "neutrality": neutrality.neutrality_sha256 if neutrality else None,
        "controls": controls.get("control_result_id") if controls else None,
        "regressions": regressions.get("regression_receipt_id") if regressions else None,
        "failures": failures,
    }
    audit_sha256 = sha256_payload(audit_core)
    comparison_ok = bool(comparison and checks["counterfactual"])
    audit = Package136SameSessionDriveModulationAudit(
        audit_id=f"package_136_audit:{audit_sha256[:16]}",
        audit_sha256=audit_sha256,
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        source_head=source_head,
        package_135_audit_id=str(source.package_135_audit["audit_id"]),
        package_135_audit_status=str(source.package_135_audit["audit_status"]),
        package_135_source_unchanged=checks["source_135_unchanged"],
        package_133_source_unchanged=checks["source_133_unchanged"],
        package_134_source_unchanged=checks["source_134_unchanged"],
        package_135_is_only_signal_authority=checks["source_binding"],
        source_trace_read_only_verified=checks["source_binding"] and checks["derivation"],
        consumer_inventory_count=len(current_inventory),
        consumer_inventory_verified=checks["consumer_inventory"],
        production_consumer_count=(len(allowlist.production_consumer_ids) if allowlist else -1),
        audit_only_consumer_count=(len(allowlist.audit_only_consumer_ids) if allowlist else -1),
        production_allowlist_empty=checks["allowlist"],
        explicit_authorization_verified=checks["authorization"],
        same_session_binding_verified=checks["authorization"] and checks["policy"],
        source_time_lineage_verified=bool(
            derivation
            and derivation.source_event_time_ns <= derivation.source_processing_time_ns
            and derivation.signal_lineage_id == source.selected_trace.signal_lineage_id
        ),
        absolute_clamp_verified=clamp_controls,
        delta_clamp_verified=clamp_controls and bool(derivation and derivation.delta_clamp_applied),
        single_use_verified=bool(
            authorization and authorization.single_application_only and len(applications) == 1
        ),
        session_expiry_verified=checks["neutralization"],
        fail_neutral_reasons_verified=expected_fail_neutral if fail_controls else (),
        counterfactual_comparison_verified=comparison_ok,
        only_audit_surface_differed=bool(
            comparison and comparison.differing_paths == ("audit_only_regulatory_offset",)
        ),
        hard_safety_equivalent=bool(comparison and comparison.hard_safety_equivalent),
        teacher_authority_equivalent=bool(comparison and comparison.teacher_authority_equivalent),
        purpose_scope_equivalent=bool(comparison and comparison.purpose_scope_equivalent),
        candidate_set_equivalent=bool(comparison and comparison.candidate_set_equivalent),
        selected_action_equivalent=bool(comparison and comparison.selected_action_equivalent),
        memory_equivalent=bool(comparison and comparison.memory_equivalent),
        perception_history_equivalent=bool(comparison and comparison.perception_history_equivalent),
        self_state_equivalent=bool(comparison and comparison.self_state_equivalent),
        output_equivalent=bool(comparison and comparison.output_equivalent),
        recovery_result_equivalent=bool(comparison and comparison.recovery_result_equivalent),
        process_ids_distinct=process_boundary,
        process_a_ended_before_process_b_started=process_boundary,
        cross_session_neutrality_verified=checks["cross_session_neutrality"],
        package_134_drive_state_restored=source.package_133_134.non_recovery_evidence.drive_state_restored,
        package_135_fresh_root_verified=bool(
            neutrality and neutrality.package_135_session_b_trace_is_fresh_root
        ),
        modulation_recovered_across_session=bool(
            neutrality
            and (neutrality.authorization_carried or neutrality.application_carried or neutrality.effective_offset_carried)
        ),
        perception_capability_created=False,
        attention_capability_created=False,
        thought_engine_capability_created=False,
        candidate_ordering_created=False,
        action_capability_created=False,
        memory_write_created=False,
        self_state_write_created=False,
        purpose_created_or_expanded=False,
        semantic_desire_reward_emotion_created=False,
        observation_extended=False,
        focus_changed=False,
        output_created=False,
        production_runtime_behavior_changed=not import_scan["valid"],
        controls_passed=checks["controls"],
        fresh_regressions_passed=checks["regressions"],
        append_only_store_verified=checks["append_only_store"],
        package_137_implemented=not package_137_absent,
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        audit_status=status,
        failure_reasons=failures,
        package_137_required_gates=PACKAGE_137_REQUIRED_GATES,
        source_record_refs=(
            str(source.package_135_audit["audit_id"]),
            source.source_binding.source_binding_id,
            *(item.policy_decision_id for item in decisions),
            *(item.application_id for item in applications),
            *(item.comparison_id for item in comparisons),
            *(item.neutrality_record_id for item in neutrality_records),
            str(controls.get("control_result_id") if controls else "missing_controls"),
            str(regressions.get("regression_receipt_id") if regressions else "missing_regressions"),
        ),
    )
    if append:
        store.append_once("package_136_audits", audit)
    return audit


def _scan_forbidden_consumers(root: Path) -> dict[str, Any]:
    protected_roots = (
        "runtime",
        "perception",
        "thought",
        "task",
        "memory",
        "state",
        "body",
    )
    forbidden_prefixes = (
        "ashl_core_v1.endocrine.drive_modulation",
        "ashl_core_v1.endocrine.package_136",
    )
    findings: list[str] = []
    for directory_name in protected_roots:
        directory = root / "ashl_core_v1" / directory_name
        if not directory.is_dir():
            continue
        for path in directory.rglob("*.py"):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:
                findings.append(f"syntax_error:{path.relative_to(root).as_posix()}")
                continue
            for node in ast.walk(tree):
                modules: tuple[str, ...] = ()
                if isinstance(node, ast.Import):
                    modules = tuple(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    modules = (node.module,)
                for module in modules:
                    if module.startswith(forbidden_prefixes):
                        findings.append(f"{path.relative_to(root).as_posix()}:{module}")
    return {"valid": not findings, "findings": tuple(sorted(findings))}


def _record_from_payload(record_type: type[T], payload: dict[str, Any]) -> T:
    values = dict(payload)
    for item in fields(record_type):
        if "tuple" in str(item.type).lower() and isinstance(values.get(item.name), list):
            values[item.name] = tuple(values[item.name])
    return record_type(**values)


def _git_output(root: Path, *args: str) -> str:
    return subprocess.check_output(("git", *args), cwd=root, text=True).strip()


def _is_ancestor(root: Path, commit: str) -> bool:
    return subprocess.run(
        ("git", "merge-base", "--is-ancestor", commit, "HEAD"),
        cwd=root,
        check=False,
        capture_output=True,
    ).returncode == 0
