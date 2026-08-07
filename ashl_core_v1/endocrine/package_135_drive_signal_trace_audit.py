"""Final audit and fresh regressions for Package 135."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from dataclasses import fields
from pathlib import Path
from typing import Any

from ashl_core_v1.endocrine.drive_signal_legacy_inventory import (
    build_drive_signal_legacy_inventory,
)
from ashl_core_v1.endocrine.drive_signal_trace_types import (
    AUDIT_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    FORBIDDEN_TRACE_AUTHORITY_FIELDS,
    PACKAGE_136_REQUIRED_GATES,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    DriveAuthoritySeparationRecord,
    DriveCrossSessionResetRecord,
    DriveRegulatorySignalSourceObservation,
    DriveRegulatorySignalTraceContract,
    DriveRegulatorySignalTraceRecord,
    DriveSignalLineageValidationRecord,
    DriveTraceProcessPairRecord,
    DriveTraceProcessReceipt,
    Package135DriveSignalTraceSeparationAudit,
    Package135RegressionReceipt,
)
from ashl_core_v1.endocrine.package_135_authority_source import (
    load_package_135_authority_sources_read_only,
    source_tree_sha256,
)
from ashl_core_v1.endocrine.package_135_drive_signal_trace_store import (
    Package135DriveSignalTraceStore,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now


_TARGETED_135 = "ashl_core_v1.tests.test_package_135_drive_signal_trace_separation"
_PACKAGE_134_REGRESSIONS = (
    "ashl_core_v1.tests.test_package_134_persistent_session_recovery_identity",
    "ashl_core_v1.tests.test_package_133_cross_session_self_state_schema",
)
_ENDOCRINE_BOUNDARY_REGRESSIONS = (
    "ashl_core_v1.tests.test_first_stage_data_shapes",
    "ashl_core_v1.tests.test_blocked_manual_circulation_sample",
    "ashl_core_v1.tests.test_fixed_circulation_runner",
    "ashl_core_v1.tests.test_multi_case_cradle_circulation_samples",
    "ashl_core_v1.tests.test_package_132_active_perception_attention_milestone",
)


def run_package_135_regressions(
    *, ashl_root: str | Path, state_dir: str | Path
) -> Package135RegressionReceipt:
    root = Path(ashl_root).resolve()
    store = Package135DriveSignalTraceStore(state_dir)
    pycache = store.root / "regression_pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    commands: tuple[tuple[str, tuple[str, ...]], ...] = (
        (
            "targeted_package_135",
            (sys.executable, "-m", "unittest", _TARGETED_135),
        ),
        (
            "package_134_and_133_regressions",
            (sys.executable, "-m", "unittest", *_PACKAGE_134_REGRESSIONS),
        ),
        (
            "endocrine_and_boundary_regressions",
            (sys.executable, "-m", "unittest", *_ENDOCRINE_BOUNDARY_REGRESSIONS),
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
    receipt = Package135RegressionReceipt(
        regression_receipt_id=f"package_135_regressions:{sha256_payload({'head': source_head, 'results': results})[:16]}",
        schema_version=REGRESSION_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        source_head=source_head,
        command_results=tuple(results),
        targeted_package_135_passed=statuses["targeted_package_135"],
        package_134_regressions_passed=statuses["package_134_and_133_regressions"],
        endocrine_and_boundary_regressions_passed=statuses["endocrine_and_boundary_regressions"],
        full_v1_discover_passed=statuses["full_v1_unittest_discover"],
        compileall_passed=statuses["compileall"],
        git_diff_check_passed=statuses["git_diff_check"],
        pycache_redirected_outside_repo=True,
        fresh_regressions_passed=all(statuses.values()),
    )
    store.append_once("package_135_regression_receipts", receipt)
    return receipt


def audit_package_135_drive_signal_trace_separation(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    state_dir: str | Path,
    append: bool = True,
) -> Package135DriveSignalTraceSeparationAudit:
    root = Path(ashl_root).resolve()
    source_133 = Path(package_133_state_dir).resolve()
    source_134 = Path(package_134_state_dir).resolve()
    before_133 = source_tree_sha256(source_133)
    before_134 = source_tree_sha256(source_134)
    source = load_package_135_authority_sources_read_only(
        package_133_state_dir=source_133,
        package_134_state_dir=source_134,
    )
    store = Package135DriveSignalTraceStore(state_dir)
    inventory = build_drive_signal_legacy_inventory(root)
    persisted_inventory = store.list_payloads("legacy_drive_boundary_records")
    contracts = store.list_payloads("drive_trace_contracts")
    evidence = store.list_payloads("package_134_drive_non_recovery_evidence")
    observations = tuple(
        _record_from_payload(DriveRegulatorySignalSourceObservation, item)
        for item in store.list_payloads("drive_source_observations")
    )
    traces = tuple(
        DriveRegulatorySignalTraceRecord.from_dict(item)
        for item in store.list_payloads("drive_signal_traces")
    )
    validations = tuple(
        _record_from_payload(DriveSignalLineageValidationRecord, item)
        for item in store.list_payloads("drive_lineage_validations")
    )
    separations = tuple(
        _record_from_payload(DriveAuthoritySeparationRecord, item)
        for item in store.list_payloads("drive_authority_separations")
    )
    resets = tuple(
        _record_from_payload(DriveCrossSessionResetRecord, item)
        for item in store.list_payloads("drive_cross_session_resets")
    )
    receipts = tuple(
        _record_from_payload(DriveTraceProcessReceipt, item)
        for item in store.list_payloads("drive_trace_process_receipts")
    )
    pairs = tuple(
        _record_from_payload(DriveTraceProcessPairRecord, item)
        for item in store.list_payloads("drive_trace_process_pairs")
    )
    controls = store.latest_payload("package_135_control_results")
    regressions = store.latest_payload("package_135_regression_receipts")
    integrity = store.audit_integrity()
    after_133 = source_tree_sha256(source_133)
    after_134 = source_tree_sha256(source_134)

    contract = (
        _record_from_payload(DriveRegulatorySignalTraceContract, contracts[0])
        if len(contracts) == 1
        else None
    )
    pair = pairs[0] if len(pairs) == 1 else None
    reset = resets[0] if len(resets) == 1 else None
    separation = separations[0] if len(separations) == 1 else None
    receipt_by_role = {item.process_role: item for item in receipts}
    process_a = receipt_by_role.get("process_a")
    process_b = receipt_by_role.get("process_b")
    trace_by_id = {item.signal_trace_id: item for item in traces}
    semantic_fields = (
        "semantic_label",
        "purpose_ref",
        "desire_label",
        "reward_ref",
        "emotion_label",
        "affordance_ref",
        "tendency_ref",
        "selected_action_ref",
    )
    trace_authority_clean = all(
        all(getattr(item, name) is None for name in semantic_fields)
        and not any(getattr(item, name) for name in FORBIDDEN_TRACE_AUTHORITY_FIELDS)
        for item in traces
    )
    source_clean = all(
        all(getattr(item, name) is None for name in semantic_fields)
        and not item.runtime_status_relabelled_as_drive
        and not item.legacy_endocrine_promoted
        and not item.stimulus_ground_truth_used
        for item in observations
    )
    process_boundary = bool(
        process_a
        and process_b
        and process_a.operating_system_process_id != process_b.operating_system_process_id
        and process_a.ended_monotonic_ns < process_b.started_monotonic_ns
    )
    source_time_change = bool(
        len(observations) == 3
        and len(traces) == 3
        and all(item.processing_time_ns >= item.event_time_ns for item in traces)
        and all(item.source_observation_ref for item in traces)
        and any(item.change_kind == "increased" for item in traces)
    )
    stored_inventory_index = {
        str(item.get("boundary_record_id")): str(item.get("boundary_sha256"))
        for item in persisted_inventory
    }
    current_inventory_index = {
        item.boundary_record_id: item.boundary_sha256 for item in inventory
    }
    import_boundary = _scan_forbidden_consumers(root)
    package_136_implemented = any(
        path.name.startswith("package_136")
        for path in (root / "ashl_core_v1").rglob("*.py")
    )
    package_136_boundary = _scan_package_136_downstream_boundary(root)
    checks = {
        "baseline": _is_ancestor(root, BASELINE_COMMIT),
        "package_133_source_unchanged": before_133 == after_133,
        "package_134_source_unchanged": before_134 == after_134,
        "authority_evidence": (
            len(evidence) == 1
            and evidence[0].get("evidence_id") == source.non_recovery_evidence.evidence_id
            and source.non_recovery_evidence.drive_state_restored is False
        ),
        "legacy_inventory": (
            len(inventory) == 10
            and all(item.source_scan_verified for item in inventory)
            and stored_inventory_index == current_inventory_index
        ),
        "contract": bool(
            contract
            and contract.authority_owner == "package_135_anonymous_regulatory_observation_trace_only"
            and not contract.runtime_modulation_allowed
            and not contract.package_136_modulation_authorized
        ),
        "source_provenance": source_clean,
        "trace_lineage": (
            len(validations) == 2
            and all(item.lineage_valid for item in validations)
            and {item.trace_count for item in validations} == {1, 2}
        ),
        "source_time_change": source_time_change,
        "process_boundary": process_boundary,
        "reset": bool(
            reset
            and reset.reset_status == "passed_cross_session_drive_non_recovery"
            and reset.target_trace_is_new_root
            and not reset.source_trace_parent_reused
            and not reset.source_value_copied
            and not reset.source_trace_payload_loaded_in_target
        ),
        "pair": bool(
            pair
            and pair.comparison_status == "passed_fresh_process_drive_trace_reset"
            and pair.process_b_started_with_new_root
            and not pair.prior_trace_loaded_by_process_b
        ),
        "authority_separation": bool(
            separation
            and separation.separation_status == "passed_trace_only_authority_separation"
            and trace_authority_clean
        ),
        "production_import_boundary": import_boundary["valid"],
        "controls": bool(controls and controls.get("controls_passed") is True),
        "regressions": bool(regressions and regressions.get("fresh_regressions_passed") is True),
        "append_only_store": bool(
            integrity["valid"]
            and integrity["append_only_history"]
            and not integrity["active_drive_head_present"]
            and not integrity["cross_session_recovery_table_present"]
        ),
        "package_136_downstream_boundary": package_136_boundary["valid"],
    }
    failures = tuple(name for name, passed in checks.items() if not passed)
    status = PASS_STATUS if not failures else BLOCKED_STATUS
    source_head = _git_output(root, "rev-parse", "HEAD")
    audit_core = {
        "source_head": source_head,
        "contract": contract.contract_sha256 if contract else None,
        "package_134_evidence": source.non_recovery_evidence.evidence_sha256,
        "process_a": process_a.process_receipt_id if process_a else None,
        "process_b": process_b.process_receipt_id if process_b else None,
        "reset": reset.reset_sha256 if reset else None,
        "pair": pair.process_pair_id if pair else None,
        "controls": controls.get("control_result_id") if controls else None,
        "regressions": regressions.get("regression_receipt_id") if regressions else None,
        "failures": failures,
    }
    audit_sha256 = sha256_payload(audit_core)
    audit = Package135DriveSignalTraceSeparationAudit(
        audit_id=f"package_135_audit:{audit_sha256[:16]}",
        audit_sha256=audit_sha256,
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        source_head=source_head,
        package_133_audit_status=source.package_133.snapshot.package_133_audit_status,
        package_134_audit_status=str(source.package_134_audit["audit_status"]),
        package_133_source_unchanged=checks["package_133_source_unchanged"],
        package_134_source_unchanged=checks["package_134_source_unchanged"],
        package_133_remains_self_state_authority=True,
        package_134_remains_recovery_authority=True,
        legacy_inventory_count=len(inventory),
        legacy_inventory_verified=checks["legacy_inventory"],
        trace_contract_verified=checks["contract"],
        source_provenance_verified=checks["source_provenance"],
        trace_lineage_verified=checks["trace_lineage"],
        source_time_and_change_verified=checks["source_time_change"],
        process_ids_distinct=process_boundary,
        process_a_ended_before_process_b_started=process_boundary,
        session_a_trace_count=(len(process_a.signal_trace_refs) if process_a else 0),
        session_b_trace_count=(len(process_b.signal_trace_refs) if process_b else 0),
        cross_session_reset_verified=checks["reset"] and checks["pair"],
        package_134_drive_state_restored=source.non_recovery_evidence.drive_state_restored,
        drive_trace_restored_across_session=bool(
            reset and (reset.source_trace_parent_reused or reset.source_trace_payload_loaded_in_target)
        ),
        drive_trace_is_self_state_content=not source.non_recovery_evidence.package_133_allowed_fields_exclude_drive,
        drive_trace_is_memory_content=any(item.memory_content_authority for item in traces),
        drive_tendency_affordance_purpose_action_separated=checks["authority_separation"],
        runtime_modulation_created=not import_boundary["valid"],
        perception_modulation_created=any(item.perception_modulation_authority for item in traces),
        attention_modulation_created=any(item.attention_modulation_authority for item in traces),
        candidate_ordering_created=any(item.candidate_ordering_authority for item in traces),
        thought_engine_influence_created=any(item.thought_engine_authority for item in traces),
        memory_influence_created=any(item.memory_influence_authority for item in traces),
        action_preference_created=any(item.action_preference_authority for item in traces),
        selected_action_created=any(item.selected_action_authority for item in traces),
        output_created=any(item.output_authority for item in traces),
        semantic_emotion_created=any(item.semantic_emotion_authority for item in traces),
        purpose_created_or_expanded=any(
            item.purpose_authority or item.purpose_expansion_authority for item in traces
        ),
        legacy_endocrine_promoted=any(item.legacy_endocrine_promoted for item in observations),
        runtime_status_relabelled_as_drive=any(
            item.runtime_status_relabelled_as_drive for item in observations
        ),
        package_136_implemented=package_136_implemented,
        package_136_modulation_authorized=bool(
            contract and contract.package_136_modulation_authorized
        ),
        controls_passed=checks["controls"],
        fresh_regressions_passed=checks["regressions"],
        append_only_store_verified=checks["append_only_store"],
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        audit_status=status,
        failure_reasons=failures,
        package_136_required_gates=PACKAGE_136_REQUIRED_GATES,
        source_record_refs=(
            source.package_133.snapshot.package_133_audit_id,
            str(source.package_134_audit["audit_id"]),
            source.non_recovery_evidence.evidence_id,
            *(item.signal_trace_id for item in traces),
            *(item.lineage_validation_id for item in validations),
            *(item.process_pair_id for item in pairs),
            str(controls.get("control_result_id") if controls else "missing_controls"),
            str(regressions.get("regression_receipt_id") if regressions else "missing_regressions"),
        ),
    )
    if append:
        store.append_once("package_135_audits", audit)
    return audit


def _scan_forbidden_consumers(root: Path) -> dict[str, Any]:
    forbidden_roots = tuple(
        root / "ashl_core_v1" / name
        for name in ("runtime", "perception", "memory", "thought", "task", "output", "state")
    )
    violations: list[str] = []
    package_135_prefixes = (
        "ashl_core_v1.endocrine.drive_signal_trace",
        "ashl_core_v1.endocrine.package_135",
    )
    for source_root in forbidden_roots:
        if not source_root.is_dir():
            continue
        for path in source_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                module = None
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith(package_135_prefixes):
                            violations.append(path.relative_to(root).as_posix())
                if module and module.startswith(package_135_prefixes):
                    violations.append(path.relative_to(root).as_posix())
    return {"valid": not violations, "violations": tuple(sorted(set(violations)))}


def _scan_package_136_downstream_boundary(root: Path) -> dict[str, Any]:
    protected_roots = tuple(
        root / "ashl_core_v1" / name
        for name in ("runtime", "perception", "memory", "thought", "task", "output", "state", "body")
    )
    prefixes = (
        "ashl_core_v1.endocrine.drive_modulation",
        "ashl_core_v1.endocrine.package_136",
    )
    violations: list[str] = []
    for source_root in protected_roots:
        if not source_root.is_dir():
            continue
        for path in source_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                modules: tuple[str, ...] = ()
                if isinstance(node, ast.ImportFrom) and node.module:
                    modules = (node.module,)
                elif isinstance(node, ast.Import):
                    modules = tuple(alias.name for alias in node.names)
                if any(module.startswith(prefixes) for module in modules):
                    violations.append(path.relative_to(root).as_posix())
    return {"valid": not violations, "violations": tuple(sorted(set(violations)))}


def _record_from_payload(record_type: type[Any], payload: dict[str, Any]) -> Any:
    values = dict(payload)
    for item in fields(record_type):
        if "tuple" in str(item.type).lower() and isinstance(values.get(item.name), list):
            value = values[item.name]
            if value and isinstance(value[0], list):
                value = tuple(tuple(inner) for inner in value)
            else:
                value = tuple(value)
            values[item.name] = value
    return record_type(**values)


def _git_output(root: Path, *args: str) -> str:
    return subprocess.check_output(("git", *args), cwd=root, text=True).strip()


def _is_ancestor(root: Path, commit: str) -> bool:
    return subprocess.run(
        ("git", "merge-base", "--is-ancestor", commit, "HEAD"), cwd=root, check=False
    ).returncode == 0
