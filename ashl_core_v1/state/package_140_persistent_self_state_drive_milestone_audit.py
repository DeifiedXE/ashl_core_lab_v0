"""Read-only evidence revalidation and closure audit for Package 140."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Iterable

from ashl_core_v1.endocrine.drive_modulation_types import (
    DriveModulationConsumerAllowlistRecord,
    DriveModulationCounterfactualComparison,
    DriveModulationCrossSessionNeutralityRecord,
    SameSessionDriveModulationContract,
)
from ashl_core_v1.endocrine.drive_signal_trace_types import (
    DriveAuthoritySeparationRecord,
    DriveCrossSessionResetRecord,
    DriveRegulatorySignalTraceContract,
    Package134DriveNonRecoveryEvidenceRecord,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now
from ashl_core_v1.state.package_140_persistent_self_state_drive_milestone_store import (
    Package140PersistentSelfStateDriveMilestoneStore,
)
from ashl_core_v1.state.package_140_persistent_self_state_drive_sources import (
    Package140PackageSource,
    Package140SourceBundle,
    evidence_tree_snapshot,
    load_package_140_sources_read_only,
    path_fingerprint,
)
from ashl_core_v1.state.persistent_self_state_drive_closure_types import (
    ABSENT_CAPABILITIES,
    AUDIT_SCHEMA_VERSION,
    AUTHORITY_BINDINGS,
    AUTHORITY_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    CLOSED_PACKAGE_IDS,
    CONTRACT_SCHEMA_VERSION,
    CONTROL_NAMES,
    CONTROL_SCHEMA_VERSION,
    EXPECTED_AUDIT_STATUSES,
    FORBIDDEN_DOWNSTREAM_EXPANSIONS,
    LINEAGE_SCHEMA_VERSION,
    LINE_CLOSURE_STATUS,
    NO_FORK_RULES,
    NO_FORK_SCHEMA_VERSION,
    PACKAGE_COMPLETION_COMMITS,
    PASS_STATUS,
    PRESENT_CAPABILITIES,
    REGRESSION_SCHEMA_VERSION,
    SOURCE_SCHEMA_VERSION,
    STABLE_CONSUMER_INTERFACES,
    Package140BoundaryControlResult,
    Package140EvidenceSourceRecord,
    Package140NoForkRuleRevalidationRecord,
    Package140PersistentSelfStateAndDriveMilestoneAudit,
    Package140RegressionReceipt,
    PersistentSelfStateAndDriveCapabilityContract,
    PersistentStateDriveAuthorityEvidenceRecord,
    PersistentStateDriveCrossPackageLineageRecord,
    build_hashed_record,
)
from ashl_core_v1.state.persistent_self_state_lineage import (
    validate_persistent_self_state_lineage,
)
from ashl_core_v1.state.persistent_self_state_review_types import (
    ExistingTeacherReviewAuthorityBindingRecord,
    SelfStateMutationCommitReceipt,
)
from ashl_core_v1.state.persistent_self_state_schema import (
    PersistentSelfStateRecord,
    PersistentSelfStateRepresentationContract,
    PersistentSelfStateTransitionRecord,
)
from ashl_core_v1.state.persistent_session_recovery_types import (
    ACTIVE_HEAD_AUTHORITY,
    ActiveHeadCASEventRecord,
    ActiveSelfStateHeadRecord,
    PersistentSessionRecoveryPairRecord,
)
from ashl_core_v1.state.self_state_readback_types import (
    SelfStateReadbackBoundaryContract,
    SelfStateReadbackConsumerAllowlistRecord,
    SelfStateReadbackCounterfactualComparison,
    SelfStateReadbackFreshProcessResetRecord,
)
from ashl_core_v1.state.self_state_rollback_types import (
    ROLLBACK_OPERATION,
    ROLL_FORWARD_OPERATION,
    SelfStateHeadSelectionCommitReceipt,
    SelfStateAncestorProofRecord,
    SelfStateRollbackBoundaryContract,
    SelfStateRollbackCounterfactualComparison,
    SelfStateRollbackNoForkGuardRecord,
)


REFERENCE_RELATIVE_PATH = Path(
    "ashl_core_v1/docs/reference/persistent_self_state_and_drive_capability_contract_v0.json"
)

_TARGETED_REGRESSION_MODULES = (
    "ashl_core_v1.tests.test_package_133_cross_session_self_state_schema",
    "ashl_core_v1.tests.test_package_134_persistent_session_recovery_identity",
    "ashl_core_v1.tests.test_package_135_drive_signal_trace_separation",
    "ashl_core_v1.tests.test_package_136_same_session_drive_modulation",
    "ashl_core_v1.tests.test_package_137_persistent_self_state_review_gate",
    "ashl_core_v1.tests.test_package_138_self_state_readback_boundary",
    "ashl_core_v1.tests.test_package_139_self_state_rollback_audit",
)


def load_authoritative_capability_contract(
    ashl_root: str | Path,
) -> PersistentSelfStateAndDriveCapabilityContract:
    path = Path(ashl_root).resolve() / REFERENCE_RELATIVE_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    contract = PersistentSelfStateAndDriveCapabilityContract(
        capability_contract_id=str(payload["capability_contract_id"]),
        capability_contract_sha256=str(payload["capability_contract_sha256"]),
        schema_version=str(payload["schema_version"]),
        created_at=str(payload["created_at"]),
        baseline_commit=str(payload["baseline_commit"]),
        closed_package_ids=tuple(payload["closed_package_ids"]),
        authority_bindings=tuple(tuple(item) for item in payload["authority_bindings"]),
        present_capabilities=tuple(payload["present_capabilities"]),
        absent_capabilities=tuple(payload["absent_capabilities"]),
        stable_consumer_interfaces=tuple(payload["stable_consumer_interfaces"]),
        forbidden_downstream_expansions=tuple(payload["forbidden_downstream_expansions"]),
        no_fork_rules=tuple(payload["no_fork_rules"]),
        production_drive_consumer_count=int(payload["production_drive_consumer_count"]),
        production_readback_consumer_count=int(payload["production_readback_consumer_count"]),
        authority_line_frozen=bool(payload["authority_line_frozen"]),
        stable_consumer_boundary=bool(payload["stable_consumer_boundary"]),
        package_140_adds_runtime_capability=bool(payload["package_140_adds_runtime_capability"]),
        package_140_adds_action=bool(payload["package_140_adds_action"]),
        package_140_adds_persistent_field=bool(payload["package_140_adds_persistent_field"]),
        package_140_adds_production_consumer=bool(payload["package_140_adds_production_consumer"]),
        package_141_plus_may_consume_existing_contracts=bool(payload["package_141_plus_may_consume_existing_contracts"]),
        package_141_plus_may_bypass_or_expand_authorities=bool(payload["package_141_plus_may_bypass_or_expand_authorities"]),
        new_authority_package_required_for_contract_expansion=bool(payload["new_authority_package_required_for_contract_expansion"]),
        structural_identity_is_psychological_continuity=bool(payload["structural_identity_is_psychological_continuity"]),
        next_core_package=str(payload["next_core_package"]),
        next_core_line=str(payload["next_core_line"]),
    )
    expected = sha256_payload(_contract_hash_payload(contract))
    if contract.capability_contract_sha256 != expected:
        raise ValueError("Package 140 capability contract hash mismatch")
    if contract.capability_contract_id != f"persistent_self_state_drive_contract:{expected[:16]}":
        raise ValueError("Package 140 capability contract identity mismatch")
    return contract


def run_package_140_boundary_controls(
    contract: PersistentSelfStateAndDriveCapabilityContract,
    *,
    append_to: Package140PersistentSelfStateDriveMilestoneStore | None = None,
) -> Package140BoundaryControlResult:
    def rejects(call: Callable[[], object]) -> bool:
        try:
            call()
        except (TypeError, ValueError):
            return True
        return False

    controls = {
        "authority_owner_injection_rejected": rejects(
            lambda: replace(
                contract,
                authority_bindings=(
                    ("133", "immutable_self_state_representation_and_history", "other_authority"),
                    *contract.authority_bindings[1:],
                ),
            )
        ),
        "self_state_field_expansion_rejected": rejects(
            lambda: replace(contract, present_capabilities=contract.present_capabilities + ("new_persistent_field",))
        ),
        "drive_persistence_rejected": rejects(
            lambda: replace(contract, absent_capabilities=tuple(item for item in contract.absent_capabilities if item != "persistent_or_recovered_drive"))
        ),
        "production_drive_consumer_rejected": rejects(
            lambda: replace(contract, production_drive_consumer_count=1)
        ),
        "production_readback_consumer_rejected": rejects(
            lambda: replace(contract, production_readback_consumer_count=1)
        ),
        "psychological_continuity_claim_rejected": rejects(
            lambda: replace(contract, structural_identity_is_psychological_continuity=True)
        ),
        "semantic_identity_rejected": rejects(
            lambda: replace(contract, absent_capabilities=tuple(item for item in contract.absent_capabilities if item != "semantic_identity"))
        ),
        "readback_behavior_authority_rejected": rejects(
            lambda: replace(contract, absent_capabilities=tuple(item for item in contract.absent_capabilities if item != "readback_behavior_authority"))
        ),
        "rollback_history_rewrite_rejected": rejects(
            lambda: replace(contract, no_fork_rules=tuple(item for item in contract.no_fork_rules if item != "package_133_history_remains_immutable"))
        ),
        "rollback_nonancestor_rejected": rejects(
            lambda: replace(contract, no_fork_rules=tuple(item for item in contract.no_fork_rules if item != "rollback_selects_one_explicit_strict_verified_ancestor_only"))
        ),
        "ancestor_active_mutation_rejected": rejects(
            lambda: replace(contract, no_fork_rules=tuple(item for item in contract.no_fork_rules if item != "selected_ancestor_blocks_package_137_mutation"))
        ),
        "ancestor_active_recovery_rejected": rejects(
            lambda: replace(contract, no_fork_rules=tuple(item for item in contract.no_fork_rules if item != "selected_ancestor_blocks_normal_package_134_recovery"))
        ),
        "arbitrary_roll_forward_rejected": rejects(
            lambda: replace(contract, no_fork_rules=tuple(item for item in contract.no_fork_rules if item != "only_separately_authorized_exact_roll_forward_to_preserved_descendant_is_allowed"))
        ),
        "automatic_rebase_or_latest_rejected": rejects(
            lambda: replace(contract, forbidden_downstream_expansions=tuple(item for item in contract.forbidden_downstream_expansions if item != "automatic_rebase_latest_selection_or_cross_lineage_rollback"))
        ),
        "thought_engine_authority_rejected": rejects(
            lambda: replace(contract, absent_capabilities=tuple(item for item in contract.absent_capabilities if item != "thought_engine"))
        ),
        "automatic_purpose_rejected": rejects(
            lambda: replace(contract, absent_capabilities=tuple(item for item in contract.absent_capabilities if item != "automatic_purpose"))
        ),
        "automatic_action_rejected": rejects(
            lambda: replace(contract, absent_capabilities=tuple(item for item in contract.absent_capabilities if item != "automatic_action"))
        ),
        "output_authority_rejected": rejects(
            lambda: replace(contract, absent_capabilities=tuple(item for item in contract.absent_capabilities if item != "output_authority"))
        ),
        "package_140_runtime_capability_rejected": rejects(
            lambda: replace(contract, package_140_adds_runtime_capability=True)
        ),
        "downstream_authority_bypass_rejected": rejects(
            lambda: replace(contract, package_141_plus_may_bypass_or_expand_authorities=True)
        ),
        "source_hash_change_rejected": rejects(
            lambda: validate_source_snapshot("0" * 64, "1" * 64)
        ),
        "audit_status_coercion_rejected": rejects(
            lambda: validate_package_140_audit_status("completed")
        ),
    }
    ordered = tuple(name for name in CONTROL_NAMES if controls.get(name))
    failures = tuple(name for name in CONTROL_NAMES if not controls.get(name))
    payload: dict[str, Any] = {
        "control_result_id": "",
        "control_result_sha256": "",
        "schema_version": CONTROL_SCHEMA_VERSION,
        "created_at": utc_now(),
        "control_names": CONTROL_NAMES,
        "passed_control_names": ordered,
        "passed_count": len(ordered),
        "controls_passed": not failures,
        "failure_reasons": failures,
        "source_record_refs": (contract.capability_contract_id,),
    }
    result = build_hashed_record(
        Package140BoundaryControlResult,
        payload,
        id_field="control_result_id",
        hash_field="control_result_sha256",
        prefix="package_140_controls",
    )
    if append_to is not None:
        append_to.append_once("package_140_boundary_control_results", result)
    return result


def run_package_140_regressions(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
) -> Package140RegressionReceipt:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    _validate_external_paths(root, output, ())
    store = Package140PersistentSelfStateDriveMilestoneStore(output)
    pycache = store.root / "regression_pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    commands = (
        (
            "targeted_package_140",
            (sys.executable, "-m", "unittest", "ashl_core_v1.tests.test_package_140_persistent_self_state_drive_milestone"),
        ),
        (
            "package_133_to_139",
            (sys.executable, "-m", "unittest", *_TARGETED_REGRESSION_MODULES),
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
                f"blocked_package_140_regression_failed:{name}:{output_digest}"
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
        raise RuntimeError("blocked_package_140_repository_pollution_detected")
    source_head = _git_output(root, "rev-parse", "HEAD")
    payload: dict[str, Any] = {
        "regression_receipt_id": "",
        "regression_receipt_sha256": "",
        "schema_version": REGRESSION_SCHEMA_VERSION,
        "created_at": utc_now(),
        "baseline_commit": BASELINE_COMMIT,
        "source_head": source_head,
        "command_results": tuple(results),
        "targeted_package_140_passed": statuses["targeted_package_140"],
        "package_133_to_139_regressions_passed": statuses["package_133_to_139"],
        "full_v1_discover_passed": statuses["full_v1_discover"],
        "compileall_passed": statuses["compileall"],
        "git_diff_check_passed": statuses["git_diff_check"],
        "repository_pollution_absent": pollution_absent,
        "pycache_redirected_outside_repo": not _is_within(pycache, root),
        "fresh_regressions_passed": all(statuses.values()) and pollution_absent,
        "source_record_refs": (f"git_head:{source_head}",),
    }
    receipt = build_hashed_record(
        Package140RegressionReceipt,
        payload,
        id_field="regression_receipt_id",
        hash_field="regression_receipt_sha256",
        prefix="package_140_regressions",
    )
    store.append_once("package_140_regression_receipts", receipt)
    return receipt


def audit_package_140_persistent_self_state_and_drive_milestone(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    package_state_dirs: dict[str, str | Path],
    append: bool = True,
) -> Package140PersistentSelfStateAndDriveMilestoneAudit:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    sources = tuple(Path(item).resolve() for item in package_state_dirs.values())
    _validate_external_paths(root, output, sources)
    source_head = _git_output(root, "rev-parse", "HEAD")
    ancestry = {
        package_id: _is_ancestor(root, commit, source_head)
        for package_id, commit in PACKAGE_COMPLETION_COMMITS.items()
    }
    contract = load_authoritative_capability_contract(root)
    bundle = load_package_140_sources_read_only(package_state_dirs)
    source_records = _build_source_records(bundle)
    authority_records = _build_authority_evidence_records(
        bundle,
        ancestry,
        source_records,
    )
    lineage_records = _build_lineage_records(root, bundle, authority_records)
    no_fork = _build_no_fork_revalidation(bundle)
    controls = run_package_140_boundary_controls(contract)

    store = Package140PersistentSelfStateDriveMilestoneStore(output)
    regression_payload = store.latest_payload("package_140_regression_receipts")
    regression = _typed(Package140RegressionReceipt, regression_payload) if regression_payload else None

    by_package = {record.package_id: record for record in authority_records}
    audit_flags = _derive_audit_flags(bundle, no_fork)
    checks = {
        "baseline_contains_package_139": _is_ancestor(root, BASELINE_COMMIT, source_head),
        "completion_commit_ancestry": all(ancestry.values()),
        "authority_evidence": all(record.evidence_status == "verified" for record in authority_records),
        "external_sources_unchanged": all(
            record.source_unchanged and record.source_opened_read_only
            for record in source_records
        ),
        "source_payload_hashes": all(record.all_payload_hashes_verified and record.database_integrity_valid for record in source_records),
        "cross_package_lineage": all(record.lineage_status == "verified" for record in lineage_records),
        "authority_ownership": all(record.authority_owner_verified for record in authority_records),
        "package_133_history": audit_flags["package_133_immutable_history_verified"],
        "package_133_no_fork": audit_flags["package_133_single_lineage_no_fork_verified"],
        "package_134_cas": audit_flags["package_134_active_head_cas_verified"],
        "package_134_recovery": audit_flags["package_134_structural_recovery_verified"],
        "canonical_leaf": audit_flags["final_active_head_matches_canonical_leaf"],
        "structural_identity": audit_flags["structural_cross_session_identity_continuity_verified"],
        "drive_trace": audit_flags["package_135_same_session_drive_trace_verified"],
        "modulation": audit_flags["package_136_bounded_modulation_infrastructure_verified"],
        "modulation_neutral": audit_flags["modulation_fail_to_neutral_verified"],
        "teacher_review": audit_flags["package_137_exact_teacher_review_gate_verified"],
        "readback": audit_flags["package_138_bounded_readback_verified"],
        "rollback": audit_flags["package_139_verified_ancestor_rollback_verified"],
        "roll_forward": audit_flags["package_139_exact_roll_forward_verified"],
        "no_fork": audit_flags["package_139_no_fork_rule_verified"],
        "capability_contract": contract.authority_line_frozen and contract.stable_consumer_boundary,
        "boundary_controls": controls.controls_passed,
        "fresh_regressions": bool(
            regression
            and regression.fresh_regressions_passed
            and regression.source_head == source_head
        ),
        "production_drive_consumers_zero": audit_flags["production_drive_consumer_count"] == 0,
        "production_readback_consumers_zero": audit_flags["production_readback_consumer_count"] == 0,
        "forbidden_capabilities_absent": not any(
            audit_flags[name]
            for name in (
                "complete_psychological_continuity_claimed",
                "drive_is_persistent_self_state",
                "drive_recovered_across_session",
                "modulation_cross_session_persisted",
                "unreviewed_self_state_mutation_authorized",
                "readback_behavior_authority_created",
                "memory_restored_by_rollback",
                "perception_history_restored_by_rollback",
                "drive_restored_by_rollback",
                "thought_restored_by_rollback",
                "action_restored_by_rollback",
                "output_restored_by_rollback",
                "semantic_identity_created",
                "autobiographical_state_created",
                "thought_engine_created",
                "automatic_purpose_created",
                "automatic_action_created",
                "output_authority_created",
                "package_140_runtime_capability_created",
                "package_140_action_created",
                "package_141_implemented",
                "dlm_1_implemented",
            )
        ),
    }
    failures = tuple(name for name, passed in checks.items() if not passed)
    status = PASS_STATUS if not failures else BLOCKED_STATUS
    payload: dict[str, Any] = {
        "audit_id": "",
        "audit_sha256": "",
        "schema_version": AUDIT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "baseline_commit": BASELINE_COMMIT,
        "source_head": source_head,
        "package_133_baseline_verified": _verified(by_package, "133"),
        "package_134_baseline_verified": _verified(by_package, "134"),
        "package_135_baseline_verified": _verified(by_package, "135"),
        "package_136_baseline_verified": _verified(by_package, "136"),
        "package_137_baseline_verified": _verified(by_package, "137"),
        "package_138_baseline_verified": _verified(by_package, "138"),
        "package_139_baseline_verified": _verified(by_package, "139"),
        "all_completion_commits_are_ancestors": checks["completion_commit_ancestry"],
        "all_authority_evidence_verified": checks["authority_evidence"],
        "all_external_sources_unchanged": checks["external_sources_unchanged"],
        "all_source_payload_hashes_verified": checks["source_payload_hashes"],
        "cross_package_lineage_record_count": len(lineage_records),
        "cross_package_lineage_consistent": checks["cross_package_lineage"],
        "authority_ownership_exact": checks["authority_ownership"],
        **audit_flags,
        "capability_contract_verified": checks["capability_contract"],
        "fresh_boundary_controls_passed": controls.controls_passed,
        "fresh_regressions_passed": checks["fresh_regressions"],
        "llm_runtime_calls": 0,
        "codex_runtime_calls": 0,
        "network_runtime_calls": 0,
        "authority_line_status": LINE_CLOSURE_STATUS,
        "next_core_package": "141",
        "audit_status": status,
        "failure_reasons": failures,
        "source_record_refs": tuple(record.source_record_id for record in source_records)
        + tuple(record.authority_evidence_id for record in authority_records)
        + tuple(record.lineage_record_id for record in lineage_records)
        + (
            no_fork.no_fork_revalidation_id,
            contract.capability_contract_id,
            controls.control_result_id,
            regression.regression_receipt_id if regression else "package_140_regressions:missing",
        ),
    }
    audit = build_hashed_record(
        Package140PersistentSelfStateAndDriveMilestoneAudit,
        payload,
        id_field="audit_id",
        hash_field="audit_sha256",
        prefix="package_140_audit",
    )
    if append:
        records: list[tuple[str, Any]] = []
        records.extend(("package_140_evidence_sources", item) for item in source_records)
        records.extend(("package_140_authority_evidence", item) for item in authority_records)
        records.extend(("package_140_cross_package_lineage", item) for item in lineage_records)
        records.extend(
            (
                ("persistent_self_state_and_drive_capability_contracts", contract),
                ("package_140_no_fork_revalidations", no_fork),
                ("package_140_boundary_control_results", controls),
                ("package_140_audits", audit),
            )
        )
        store.append_group(tuple(records))
    return audit


def verify_package_140_evidence_unchanged(
    *,
    state_dir: str | Path,
    package_state_dirs: dict[str, str | Path],
) -> dict[str, Any]:
    store = Package140PersistentSelfStateDriveMilestoneStore(state_dir)
    records = store.list_payloads("package_140_evidence_sources")
    latest_by_package = {str(record["package_id"]): record for record in records}
    results: list[dict[str, Any]] = []
    for package_id in CLOSED_PACKAGE_IDS:
        snapshot = evidence_tree_snapshot(package_state_dirs[package_id])
        prior = latest_by_package.get(package_id)
        unchanged = bool(
            prior
            and prior.get("tree_sha256_after") == snapshot.tree_sha256
            and prior.get("included_file_count") == snapshot.file_count
            and prior.get("included_byte_count") == snapshot.byte_count
        )
        results.append(
            {
                "package_id": package_id,
                "tree_sha256": snapshot.tree_sha256,
                "unchanged": unchanged,
            }
        )
    return {
        "all_sources_unchanged": all(item["unchanged"] for item in results),
        "sources": results,
    }


def validate_package_140_audit_status(status: str) -> None:
    if status not in {PASS_STATUS, BLOCKED_STATUS}:
        raise ValueError("invalid Package 140 audit status")


def validate_source_snapshot(before_sha256: str, after_sha256: str) -> None:
    if before_sha256 != after_sha256:
        raise ValueError("Package 140 authority source changed during read-only audit")


def validate_no_runtime_capability_delta(
    *,
    runtime_capability_created: bool,
    action_created: bool,
    production_consumer_created: bool,
) -> None:
    if any((runtime_capability_created, action_created, production_consumer_created)):
        raise ValueError("Package 140 cannot add runtime behavior or a production consumer")


def _build_source_records(
    bundle: Package140SourceBundle,
) -> tuple[Package140EvidenceSourceRecord, ...]:
    records: list[Package140EvidenceSourceRecord] = []
    now = utc_now()
    for package_id in CLOSED_PACKAGE_IDS:
        source = bundle.packages[package_id]
        unchanged = source.snapshot_before == source.snapshot_after
        validate_source_snapshot(
            source.snapshot_before.tree_sha256,
            source.snapshot_after.tree_sha256,
        )
        payload: dict[str, Any] = {
            "source_record_id": "",
            "source_record_sha256": "",
            "schema_version": SOURCE_SCHEMA_VERSION,
            "created_at": now,
            "package_id": package_id,
            "path_fingerprint": path_fingerprint(source.source_root),
            "database_relative_path": source.database_relative_path,
            "included_file_count": source.snapshot_after.file_count,
            "included_byte_count": source.snapshot_after.byte_count,
            "tree_sha256_before": source.snapshot_before.tree_sha256,
            "tree_sha256_after": source.snapshot_after.tree_sha256,
            "database_integrity_valid": source.database_integrity_valid,
            "all_payload_hashes_verified": source.all_payload_hashes_verified,
            "source_opened_read_only": True,
            "source_unchanged": unchanged,
            "private_absolute_path_persisted": False,
            "source_record_refs": (str(source.latest_audit["audit_id"]),),
        }
        records.append(
            build_hashed_record(
                Package140EvidenceSourceRecord,
                payload,
                id_field="source_record_id",
                hash_field="source_record_sha256",
                prefix="package_140_source",
            )
        )
    return tuple(records)


def _build_authority_evidence_records(
    bundle: Package140SourceBundle,
    ancestry: dict[str, bool],
    source_records: tuple[Package140EvidenceSourceRecord, ...],
) -> tuple[PersistentStateDriveAuthorityEvidenceRecord, ...]:
    records: list[PersistentStateDriveAuthorityEvidenceRecord] = []
    now = utc_now()
    source_by_package = {record.package_id: record for record in source_records}
    for package_id, role, owner in AUTHORITY_BINDINGS:
        source = bundle.packages[package_id]
        validation = _validate_package_authority(package_id, bundle)
        checks = (
            ancestry[package_id],
            source.database_integrity_valid,
            source.all_payload_hashes_verified,
            source.typed_audit_validation_passed,
            validation["authority_owner_verified"],
            validation["capability_evidence_verified"],
            validation["boundary_evidence_verified"],
            validation["failure_semantics_verified"],
            validation["real_evidence_verified"],
        )
        failures = tuple(
            name
            for name, passed in zip(
                (
                    "completion_commit_ancestry",
                    "database_integrity",
                    "payload_hashes",
                    "typed_audit_validation",
                    "authority_owner",
                    "capability_evidence",
                    "boundary_evidence",
                    "failure_semantics",
                    "real_evidence",
                ),
                checks,
            )
            if not passed
        )
        audit = source.latest_audit
        payload: dict[str, Any] = {
            "authority_evidence_id": "",
            "authority_evidence_sha256": "",
            "schema_version": AUTHORITY_SCHEMA_VERSION,
            "created_at": now,
            "package_id": package_id,
            "completion_commit": PACKAGE_COMPLETION_COMMITS[package_id],
            "completion_commit_is_ancestor": ancestry[package_id],
            "expected_audit_status": EXPECTED_AUDIT_STATUSES[package_id],
            "observed_audit_id": str(audit["audit_id"]),
            "observed_audit_sha256": str(audit["audit_sha256"]),
            "observed_audit_status": str(audit["audit_status"]),
            "stored_audit_payload_hash_verified": source.all_payload_hashes_verified,
            "typed_audit_validation_passed": source.typed_audit_validation_passed,
            "database_integrity_valid": source.database_integrity_valid,
            "all_store_payload_hashes_verified": source.all_payload_hashes_verified,
            "authority_role": role,
            "authority_owner": owner,
            "authority_owner_verified": validation["authority_owner_verified"],
            "capability_evidence_verified": validation["capability_evidence_verified"],
            "boundary_evidence_verified": validation["boundary_evidence_verified"],
            "failure_semantics_verified": validation["failure_semantics_verified"],
            "real_evidence_verified": validation["real_evidence_verified"],
            "evidence_source_ref": source_by_package[package_id].source_record_id,
            "evidence_status": "verified" if not failures else "blocked",
            "unresolved_evidence_limits": failures,
            "source_record_refs": (
                source_by_package[package_id].source_record_id,
                str(audit["audit_id"]),
            ),
        }
        records.append(
            build_hashed_record(
                PersistentStateDriveAuthorityEvidenceRecord,
                payload,
                id_field="authority_evidence_id",
                hash_field="authority_evidence_sha256",
                prefix="package_140_authority_evidence",
            )
        )
    return tuple(records)


def _validate_package_authority(
    package_id: str,
    bundle: Package140SourceBundle,
) -> dict[str, bool]:
    source = bundle.packages[package_id]
    tables = source.table_payloads
    audit = source.latest_audit
    try:
        if package_id == "133":
            contract = _typed(
                PersistentSelfStateRepresentationContract,
                _one(tables["persistent_self_state_representation_contracts"]),
            )
            states = tuple(
                PersistentSelfStateRecord.from_dict(item)
                for item in tables["persistent_self_state_records"]
            )
            transitions = tuple(
                PersistentSelfStateTransitionRecord.from_dict(item)
                for item in tables["persistent_self_state_transition_records"]
            )
            ordered = tuple(sorted(states, key=lambda item: item.self_state_version))
            by_child = {item.child_self_state_record_id: item for item in transitions}
            lineage = all(
                validate_persistent_self_state_lineage(
                    parent,
                    child,
                    by_child[child.self_state_record_id],
                )["valid"]
                for parent, child in zip(ordered, ordered[1:])
            )
            single_leaf = (
                len(ordered) == 3
                and len(transitions) == len(ordered) - 1
                and len({item.self_state_lineage_id for item in ordered}) == 1
                and len({item.parent_self_state_record_id for item in ordered[1:]})
                == len(ordered) - 1
            )
            owner = contract.authority_owner == "ashl_core_v1.state.state_engine"
            capability = lineage and single_leaf and audit.get("parent_child_lineage_verified") is True and audit.get("canonical_hash_chain_verified") is True
            boundary = all(
                (
                    audit.get("runtime_behavior_influence_created") is False,
                    audit.get("cross_session_recovery_implemented") is False,
                    audit.get("drive_signal_created") is False,
                    audit.get("memory_write_created") is False,
                    audit.get("output_created") is False,
                )
            )
            failure = audit.get("boundary_controls_passed") is True
            real = audit.get("parent_child_lineage_verified") is True and len(ordered) >= 2
        elif package_id == "134":
            head = ActiveSelfStateHeadRecord.from_dict(
                _one(tables["active_self_state_head"])
            )
            cas_events = tuple(
                _typed(ActiveHeadCASEventRecord, item)
                for item in tables["active_head_cas_events"]
            )
            pair = _typed(
                PersistentSessionRecoveryPairRecord,
                _one(tables["persistent_session_recovery_pairs"]),
            )
            owner = head.active_head_authority == ACTIVE_HEAD_AUTHORITY
            capability = all(
                (
                    pair.comparison_status == "passed_real_fresh_process_session_recovery",
                    audit.get("active_head_cas_verified") is True,
                    audit.get("same_self_state_lineage_verified") is True,
                    any(item.operation == "recover_session" and item.cas_succeeded for item in cas_events),
                )
            )
            boundary = all(
                (
                    audit.get("active_head_separate_from_history") is True,
                    audit.get("identity_fork_created") is False,
                    audit.get("behavior_influence_created") is False,
                    audit.get("persistent_psychological_continuity_claimed") is False,
                )
            )
            failure = audit.get("recovery_controls_passed") is True
            real = pair.process_ids_distinct and pair.process_a_ended_before_process_b_started
        elif package_id == "135":
            contract = _typed(
                DriveRegulatorySignalTraceContract,
                _one(tables["drive_trace_contracts"]),
            )
            non_recovery = _typed(
                Package134DriveNonRecoveryEvidenceRecord,
                _one(tables["package_134_drive_non_recovery_evidence"]),
            )
            separation = _typed(
                DriveAuthoritySeparationRecord,
                _one(tables["drive_authority_separations"]),
            )
            reset = _typed(
                DriveCrossSessionResetRecord,
                _one(tables["drive_cross_session_resets"]),
            )
            owner = contract.authority_owner == AUTHORITY_BINDINGS[2][2]
            capability = all(
                (
                    contract.same_session_lineage_required,
                    reset.target_trace_is_new_root,
                    reset.drive_lineages_distinct,
                    audit.get("trace_lineage_verified") is True,
                    audit.get("cross_session_reset_verified") is True,
                )
            )
            boundary = all(
                (
                    non_recovery.drive_state_restored is False,
                    separation.signal_creates_or_expands_purpose is False,
                    audit.get("drive_trace_is_self_state_content") is False,
                    audit.get("drive_trace_restored_across_session") is False,
                    audit.get("runtime_modulation_created") is False,
                )
            )
            failure = audit.get("controls_passed") is True
            real = audit.get("process_ids_distinct") is True and audit.get("process_a_ended_before_process_b_started") is True
        elif package_id == "136":
            contract = _typed(
                SameSessionDriveModulationContract,
                _one(tables["same_session_drive_modulation_contracts"]),
            )
            allowlist = _typed(
                DriveModulationConsumerAllowlistRecord,
                _one(tables["drive_modulation_consumer_allowlists"]),
            )
            neutrality = _typed(
                DriveModulationCrossSessionNeutralityRecord,
                _one(tables["drive_modulation_cross_session_neutrality"]),
            )
            comparison = _typed(
                DriveModulationCounterfactualComparison,
                _one(tables["drive_modulation_counterfactual_comparisons"]),
            )
            owner = contract.modulation_authority == AUTHORITY_BINDINGS[3][2]
            capability = all(
                (
                    contract.same_session_only,
                    contract.fail_to_neutral_required,
                    contract.production_consumer_count == 0,
                    allowlist.production_consumer_ids == (),
                    neutrality.process_b_started_neutral,
                    comparison.modulation_surface_different,
                )
            )
            boundary = all(
                (
                    audit.get("production_runtime_behavior_changed") is False,
                    audit.get("modulation_recovered_across_session") is False,
                    audit.get("self_state_write_created") is False,
                    audit.get("memory_write_created") is False,
                    audit.get("action_capability_created") is False,
                    audit.get("output_created") is False,
                )
            )
            failure = audit.get("controls_passed") is True and bool(audit.get("fail_neutral_reasons_verified"))
            real = neutrality.process_ids_distinct and neutrality.process_a_ended_before_process_b_started
        elif package_id == "137":
            binding = _typed(
                ExistingTeacherReviewAuthorityBindingRecord,
                _one(tables["teacher_authority_bindings"]),
            )
            receipt = _typed(
                SelfStateMutationCommitReceipt,
                _one(tables["self_state_mutation_commit_receipts"]),
            )
            decisions = {
                str(item.get("decision"))
                for item in tables["self_state_teacher_reviews"]
            }
            owner = audit.get("package_133_only_schema_authority") is True and audit.get("package_134_only_active_head_cas_authority") is True
            capability = all(
                (
                    binding.existing_teacher_authority_reused,
                    receipt.cross_authority_commit_complete,
                    receipt.review_consumed_once,
                    decisions == {"approved", "rejected", "deferred"},
                    audit.get("exact_head_binding_verified") is True,
                    audit.get("exact_parent_binding_verified") is True,
                    audit.get("exact_delta_binding_verified") is True,
                )
            )
            boundary = all(
                (
                    receipt.parent_modified_in_place is False,
                    receipt.drive_persisted is False,
                    receipt.runtime_behavior_influence_created is False,
                    audit.get("unauthorized_mutation_became_authoritative") is False,
                    audit.get("second_teacher_system_created") is False,
                )
            )
            failure = audit.get("all_controls_passed") is True and audit.get("partial_failure_control_passed") is True
            real = receipt.package_133_successor_appended and receipt.package_134_active_head_advanced
        elif package_id == "138":
            contract = _typed(
                SelfStateReadbackBoundaryContract,
                _one(tables["self_state_readback_contracts"]),
            )
            allowlist = _typed(
                SelfStateReadbackConsumerAllowlistRecord,
                _one(tables["self_state_readback_consumer_allowlists"]),
            )
            reset = _typed(
                SelfStateReadbackFreshProcessResetRecord,
                _one(tables["self_state_readback_fresh_process_resets"]),
            )
            comparison = _typed(
                SelfStateReadbackCounterfactualComparison,
                _one(tables["self_state_readback_counterfactual_comparisons"]),
            )
            owner = contract.readback_authority == AUTHORITY_BINDINGS[5][2]
            capability = all(
                (
                    contract.same_session_only,
                    contract.production_consumer_count == 0,
                    allowlist.production_consumer_ids == (),
                    allowlist.implicit_consumer_ids == (),
                    reset.prior_readback_restored is False,
                    reset.fresh_authorization_required,
                    comparison.readback_surface_only_difference,
                )
            )
            boundary = all(
                (
                    contract.runtime_behavior_authority_allowed is False,
                    contract.semantic_interpretation_allowed is False,
                    audit.get("runtime_behavior_influence_created") is False,
                    audit.get("memory_influence_created") is False,
                    audit.get("drive_influence_created") is False,
                    audit.get("output_created") is False,
                )
            )
            failure = audit.get("all_controls_passed") is True and audit.get("stale_head_invalidation_verified") is True
            real = reset.processes_distinct and reset.sessions_distinct
        else:
            contract = _typed(
                SelfStateRollbackBoundaryContract,
                _one(tables["self_state_rollback_contracts"]),
            )
            proof = _typed(
                SelfStateAncestorProofRecord,
                _one(tables["self_state_ancestor_proofs"]),
            )
            receipts = tuple(
                _typed(SelfStateHeadSelectionCommitReceipt, item)
                for item in tables["self_state_head_selection_commit_receipts"]
            )
            guard = _typed(
                SelfStateRollbackNoForkGuardRecord,
                _one(tables["self_state_rollback_no_fork_guard_records"]),
            )
            comparison = _typed(
                SelfStateRollbackCounterfactualComparison,
                _one(tables["self_state_rollback_counterfactual_comparisons"]),
            )
            owner = contract.rollback_authority == AUTHORITY_BINDINGS[6][2]
            capability = all(
                (
                    proof.target_is_strict_ancestor,
                    proof.complete_parent_hash_chain_verified,
                    len(receipts) == 2,
                    {item.operation for item in receipts}
                    == {ROLLBACK_OPERATION, ROLL_FORWARD_OPERATION},
                    guard.exact_roll_forward_required,
                    comparison.selected_state_restored_to_pre_rollback_record,
                    audit.get("canonical_leaf_restored") is True,
                )
            )
            boundary = all(
                (
                    contract.package_133_history_immutable,
                    contract.intervening_descendants_preserved,
                    guard.new_successor_from_selected_ancestor_allowed is False,
                    guard.identity_fork_created is False,
                    audit.get("self_state_history_rewritten") is False,
                    audit.get("memory_restored") is False,
                    audit.get("perception_history_restored") is False,
                    audit.get("drive_trace_restored") is False,
                    audit.get("output_created") is False,
                )
            )
            failure = audit.get("controls_passed") is True and guard.package_137_mutation_preflight_blocked and guard.package_134_recovery_resolution_blocked
            real = audit.get("rollback_cas_verified") is True and audit.get("roll_forward_cas_verified") is True
    except (KeyError, TypeError, ValueError):
        return {
            "authority_owner_verified": False,
            "capability_evidence_verified": False,
            "boundary_evidence_verified": False,
            "failure_semantics_verified": False,
            "real_evidence_verified": False,
        }
    return {
        "authority_owner_verified": bool(owner),
        "capability_evidence_verified": bool(capability),
        "boundary_evidence_verified": bool(boundary),
        "failure_semantics_verified": bool(failure),
        "real_evidence_verified": bool(real),
    }


def _build_lineage_records(
    root: Path,
    bundle: Package140SourceBundle,
    authority_records: tuple[PersistentStateDriveAuthorityEvidenceRecord, ...],
) -> tuple[PersistentStateDriveCrossPackageLineageRecord, ...]:
    tables = {package_id: bundle.packages[package_id].table_payloads for package_id in CLOSED_PACKAGE_IDS}
    audits = {package_id: bundle.packages[package_id].latest_audit for package_id in CLOSED_PACKAGE_IDS}
    by_package = {record.package_id: record for record in authority_records}
    states = tuple(
        PersistentSelfStateRecord.from_dict(item)
        for item in tables["133"]["persistent_self_state_records"]
    )
    leaf = max(states, key=lambda item: item.self_state_version)
    head = ActiveSelfStateHeadRecord.from_dict(_one(tables["134"]["active_self_state_head"]))
    cas_events = tuple(
        _typed(ActiveHeadCASEventRecord, item)
        for item in tables["134"]["active_head_cas_events"]
    )
    cas_by_id = {item.cas_event_id: item for item in cas_events}
    p135_non_recovery = _one(tables["135"]["package_134_drive_non_recovery_evidence"])
    p136_binding = _one(tables["136"]["package_135_signal_authority_bindings"])
    p137_commit = _one(tables["137"]["self_state_mutation_commit_receipts"])
    p138_binding = tables["138"]["self_state_readback_source_bindings"][-1]
    p139_binding = tables["139"]["self_state_rollback_source_bindings"][-1]
    p139_receipts = {
        str(item["operation"]): item
        for item in tables["139"]["self_state_head_selection_commit_receipts"]
    }

    p133_tree = bundle.packages["133"].snapshot_after.tree_sha256
    p137_tree = bundle.packages["137"].snapshot_after.tree_sha256
    edge_specs = (
        (
            "133", "134", "immutable_lineage_to_exact_active_head",
            head.self_state_record_id == leaf.self_state_record_id
            and head.self_state_sha256 == leaf.self_state_sha256
            and head.self_state_lineage_id == leaf.self_state_lineage_id,
            True,
            (
                "ashl_core_v1/state/persistent_self_state_schema.py",
                "ashl_core_v1/state/persistent_session_recovery_types.py",
            ),
        ),
        (
            "133", "135", "self_state_drive_content_separation",
            p135_non_recovery.get("package_133_audit_id") == audits["133"].get("audit_id")
            and p135_non_recovery.get("package_133_allowed_fields_exclude_drive") is True,
            True,
            (
                "ashl_core_v1/endocrine/drive_signal_trace_types.py",
                "ashl_core_v1/state/persistent_self_state_schema.py",
            ),
        ),
        (
            "134", "135", "structural_recovery_without_drive_recovery",
            p135_non_recovery.get("package_134_audit_id") == audits["134"].get("audit_id")
            and p135_non_recovery.get("package_134_active_head_id") == head.active_head_id,
            True,
            (
                "ashl_core_v1/endocrine/package_135_authority_source.py",
                "ashl_core_v1/state/persistent_session_recovery_types.py",
            ),
        ),
        (
            "135", "136", "read_only_trace_to_bounded_modulation_derivation",
            p136_binding.get("package_135_audit_id") == audits["135"].get("audit_id")
            and p136_binding.get("source_trace_mutation_allowed") is False,
            p136_binding.get("package_135_contract_sha256")
            == _one(tables["135"]["drive_trace_contracts"]).get("contract_sha256"),
            (
                "ashl_core_v1/endocrine/package_136_package_135_source.py",
                "ashl_core_v1/endocrine/drive_modulation_runtime.py",
            ),
        ),
        (
            "133", "137", "reviewed_successor_appended_to_immutable_history",
            p137_commit.get("child_self_state_record_id") == leaf.self_state_record_id
            and p137_commit.get("child_self_state_sha256") == leaf.self_state_sha256,
            True,
            (
                "ashl_core_v1/state/persistent_self_state_review_runtime.py",
                "ashl_core_v1/state/persistent_self_state_lineage.py",
            ),
        ),
        (
            "134", "137", "reviewed_successor_exact_active_head_cas",
            p137_commit.get("package_134_cas_event_id") in cas_by_id
            and cas_by_id[str(p137_commit.get("package_134_cas_event_id"))].operation
            == "advance_reviewed_self_state_successor",
            True,
            (
                "ashl_core_v1/state/persistent_self_state_review_runtime.py",
                "ashl_core_v1/state/persistent_session_recovery_store.py",
            ),
        ),
        (
            "137", "138", "review_gate_identity_to_read_only_binding",
            p138_binding.get("package_137_audit_id") == audits["137"].get("audit_id")
            and p138_binding.get("package_137_commit_receipt_ref")
            == p137_commit.get("commit_receipt_id"),
            p138_binding.get("package_137_tree_sha256") == p137_tree,
            (
                "ashl_core_v1/state/package_138_self_state_sources.py",
                "ashl_core_v1/state/self_state_readback_runtime.py",
            ),
        ),
        (
            "134", "138", "historical_exact_head_readback_binding",
            any(
                item.new_head_revision == int(p138_binding.get("head_revision"))
                and item.new_active_head_sha256 == p138_binding.get("active_head_sha256")
                for item in cas_events
            ),
            True,
            (
                "ashl_core_v1/state/package_138_self_state_sources.py",
                "ashl_core_v1/state/persistent_session_recovery_types.py",
            ),
        ),
        (
            "133", "139", "immutable_history_to_verified_ancestor_proof",
            p139_binding.get("current_self_state_record_id") == leaf.self_state_record_id
            and p139_binding.get("current_self_state_sha256") == leaf.self_state_sha256,
            p139_binding.get("package_133_tree_sha256") == p133_tree,
            (
                "ashl_core_v1/state/package_139_self_state_sources.py",
                "ashl_core_v1/state/self_state_rollback_runtime.py",
            ),
        ),
        (
            "134", "139", "rollback_and_roll_forward_exact_cas",
            all(
                item.get("package_134_cas_event_ref") in cas_by_id
                for item in p139_receipts.values()
            )
            and p139_binding.get("current_active_head_sha256") == head.active_head_sha256,
            True,
            (
                "ashl_core_v1/state/self_state_rollback_runtime.py",
                "ashl_core_v1/state/persistent_session_recovery_store.py",
            ),
        ),
        (
            "137", "139", "mutation_gate_blocked_while_ancestor_selected",
            p139_binding.get("package_137_audit_id") == audits["137"].get("audit_id"),
            p139_binding.get("package_137_tree_sha256") == p137_tree,
            (
                "ashl_core_v1/state/self_state_rollback_runtime.py",
                "ashl_core_v1/state/persistent_self_state_review_runtime.py",
            ),
        ),
        (
            "138", "139", "readback_terminal_before_head_selection",
            p139_binding.get("package_138_audit_id") == audits["138"].get("audit_id")
            and all(item.get("readbacks_terminal_before_cas") is True for item in p139_receipts.values()),
            True,
            (
                "ashl_core_v1/state/self_state_rollback_runtime.py",
                "ashl_core_v1/state/self_state_readback_runtime.py",
            ),
        ),
    )
    records: list[PersistentStateDriveCrossPackageLineageRecord] = []
    now = utc_now()
    for producer, consumer, interface, identity, source_hash, modules in edge_specs:
        modules_exist = all((root / item).is_file() for item in modules)
        authority_ok = by_package[producer].authority_owner_verified and by_package[consumer].authority_owner_verified
        failure_ok = by_package[consumer].failure_semantics_verified
        status = "verified" if all((identity, source_hash, modules_exist, authority_ok, failure_ok)) else "blocked"
        payload: dict[str, Any] = {
            "lineage_record_id": "",
            "lineage_record_sha256": "",
            "schema_version": LINEAGE_SCHEMA_VERSION,
            "created_at": now,
            "producer_package_id": producer,
            "consumer_package_id": consumer,
            "interface_kind": interface,
            "producer_record_refs": (by_package[producer].observed_audit_id,),
            "consumer_record_refs": (by_package[consumer].observed_audit_id,),
            "source_module_refs": modules,
            "identity_consistent": bool(identity and modules_exist),
            "source_hash_consistent": bool(source_hash),
            "authority_not_broadened": authority_ok,
            "failure_semantics_consistent": failure_ok,
            "lineage_status": status,
        }
        records.append(
            build_hashed_record(
                PersistentStateDriveCrossPackageLineageRecord,
                payload,
                id_field="lineage_record_id",
                hash_field="lineage_record_sha256",
                prefix="package_140_lineage",
            )
        )
    return tuple(records)


def _build_no_fork_revalidation(
    bundle: Package140SourceBundle,
) -> Package140NoForkRuleRevalidationRecord:
    p133 = bundle.packages["133"].table_payloads
    p134 = bundle.packages["134"].table_payloads
    p139 = bundle.packages["139"].table_payloads
    states = tuple(
        PersistentSelfStateRecord.from_dict(item)
        for item in p133["persistent_self_state_records"]
    )
    leaf = max(states, key=lambda item: item.self_state_version)
    head = ActiveSelfStateHeadRecord.from_dict(_one(p134["active_self_state_head"]))
    cas_events = {
        item.cas_event_id: item
        for item in (
            _typed(ActiveHeadCASEventRecord, payload)
            for payload in p134["active_head_cas_events"]
        )
    }
    contract = _typed(
        SelfStateRollbackBoundaryContract,
        _one(p139["self_state_rollback_contracts"]),
    )
    proof = _typed(
        SelfStateAncestorProofRecord,
        _one(p139["self_state_ancestor_proofs"]),
    )
    receipts = {
        item.operation: item
        for item in (
            _typed(SelfStateHeadSelectionCommitReceipt, payload)
            for payload in p139["self_state_head_selection_commit_receipts"]
        )
    }
    rollback = receipts[ROLLBACK_OPERATION]
    roll_forward = receipts[ROLL_FORWARD_OPERATION]
    guard = _typed(
        SelfStateRollbackNoForkGuardRecord,
        _one(p139["self_state_rollback_no_fork_guard_records"]),
    )
    comparison = _typed(
        SelfStateRollbackCounterfactualComparison,
        _one(p139["self_state_rollback_counterfactual_comparisons"]),
    )
    rollback_cas = cas_events[rollback.package_134_cas_event_ref]
    roll_forward_cas = cas_events[roll_forward.package_134_cas_event_ref]
    exact_leaf = all(
        (
            head.self_state_record_id == leaf.self_state_record_id,
            head.self_state_sha256 == leaf.self_state_sha256,
            roll_forward.self_state_record_id_after == leaf.self_state_record_id,
            roll_forward.self_state_sha256_after == leaf.self_state_sha256,
        )
    )
    payload: dict[str, Any] = {
        "no_fork_revalidation_id": "",
        "no_fork_revalidation_sha256": "",
        "schema_version": NO_FORK_SCHEMA_VERSION,
        "created_at": utc_now(),
        "active_head_id": head.active_head_id,
        "final_active_head_sha256": head.active_head_sha256,
        "final_head_revision": head.head_revision,
        "canonical_leaf_self_state_record_id": leaf.self_state_record_id,
        "canonical_leaf_self_state_sha256": leaf.self_state_sha256,
        "rollback_receipt_ref": rollback.commit_receipt_id,
        "roll_forward_receipt_ref": roll_forward.commit_receipt_id,
        "rollback_cas_event_ref": rollback_cas.cas_event_id,
        "roll_forward_cas_event_ref": roll_forward_cas.cas_event_id,
        "strict_verified_ancestor_selected": proof.target_is_strict_ancestor and proof.complete_parent_hash_chain_verified,
        "package_133_history_unchanged": rollback.package_133_history_unchanged and roll_forward.package_133_history_unchanged,
        "intervening_descendants_preserved": rollback.intervening_history_preserved and roll_forward.intervening_history_preserved,
        "mutation_blocked_while_ancestor_selected": guard.package_137_mutation_preflight_blocked,
        "recovery_blocked_while_ancestor_selected": guard.package_134_recovery_resolution_blocked,
        "new_successor_from_selected_ancestor_allowed": guard.new_successor_from_selected_ancestor_allowed,
        "automatic_rebase_used": guard.automatic_rebase_allowed,
        "latest_selection_used": contract.latest_selection_allowed,
        "cross_lineage_selection_used": contract.cross_lineage_selection_allowed,
        "exact_roll_forward_required": guard.exact_roll_forward_required and contract.exact_roll_forward_required,
        "exact_preserved_descendant_restored": comparison.selected_state_restored_to_pre_rollback_record,
        "canonical_leaf_restored": exact_leaf,
        "recovery_eligibility_restored": bundle.packages["139"].latest_audit.get("recovery_eligibility_restored_after_roll_forward") is True,
        "readbacks_terminal_before_head_changes": rollback.readbacks_terminal_before_cas and roll_forward.readbacks_terminal_before_cas,
        "fresh_readback_authorization_required": comparison.readback_requires_new_authorization,
        "identity_fork_created": guard.identity_fork_created,
        "no_fork_status": "revalidated_ancestor_selection_requires_exact_roll_forward_without_fork",
        "source_record_refs": (
            proof.ancestor_proof_id,
            rollback.commit_receipt_id,
            guard.no_fork_guard_id,
            roll_forward.commit_receipt_id,
            comparison.comparison_id,
            head.active_head_id,
            leaf.self_state_record_id,
        ),
    }
    return build_hashed_record(
        Package140NoForkRuleRevalidationRecord,
        payload,
        id_field="no_fork_revalidation_id",
        hash_field="no_fork_revalidation_sha256",
        prefix="package_140_no_fork",
    )


def _derive_audit_flags(
    bundle: Package140SourceBundle,
    no_fork: Package140NoForkRuleRevalidationRecord,
) -> dict[str, Any]:
    audits = {
        package_id: bundle.packages[package_id].latest_audit
        for package_id in CLOSED_PACKAGE_IDS
    }
    p133 = bundle.packages["133"].table_payloads
    p134 = bundle.packages["134"].table_payloads
    p136 = bundle.packages["136"].table_payloads
    p138 = bundle.packages["138"].table_payloads
    p139 = bundle.packages["139"].table_payloads
    states = tuple(
        PersistentSelfStateRecord.from_dict(item)
        for item in p133["persistent_self_state_records"]
    )
    transitions = tuple(
        PersistentSelfStateTransitionRecord.from_dict(item)
        for item in p133["persistent_self_state_transition_records"]
    )
    ordered = tuple(sorted(states, key=lambda item: item.self_state_version))
    by_child = {item.child_self_state_record_id: item for item in transitions}
    lineage_valid = all(
        validate_persistent_self_state_lineage(parent, child, by_child[child.self_state_record_id])["valid"]
        for parent, child in zip(ordered, ordered[1:])
    )
    head = ActiveSelfStateHeadRecord.from_dict(_one(p134["active_self_state_head"]))
    recovery_pair = _typed(
        PersistentSessionRecoveryPairRecord,
        _one(p134["persistent_session_recovery_pairs"]),
    )
    modulation_contract = _typed(
        SameSessionDriveModulationContract,
        _one(p136["same_session_drive_modulation_contracts"]),
    )
    modulation_allowlist = _typed(
        DriveModulationConsumerAllowlistRecord,
        _one(p136["drive_modulation_consumer_allowlists"]),
    )
    readback_contract = _typed(
        SelfStateReadbackBoundaryContract,
        _one(p138["self_state_readback_contracts"]),
    )
    readback_allowlist = _typed(
        SelfStateReadbackConsumerAllowlistRecord,
        _one(p138["self_state_readback_consumer_allowlists"]),
    )
    rollback_comparison = _typed(
        SelfStateRollbackCounterfactualComparison,
        _one(p139["self_state_rollback_counterfactual_comparisons"]),
    )
    final_leaf = max(ordered, key=lambda item: item.self_state_version)
    return {
        "package_133_immutable_history_verified": lineage_valid and len(transitions) == len(states) - 1,
        "package_133_single_lineage_no_fork_verified": len({item.self_state_lineage_id for item in ordered}) == 1 and len({item.parent_self_state_record_id for item in ordered[1:]}) == len(ordered) - 1,
        "package_134_active_head_cas_verified": head.head_revision == len(p134["active_head_cas_events"]) and audits["134"].get("active_head_cas_verified") is True,
        "package_134_structural_recovery_verified": recovery_pair.comparison_status == "passed_real_fresh_process_session_recovery",
        "final_active_head_matches_canonical_leaf": head.self_state_record_id == final_leaf.self_state_record_id and head.self_state_sha256 == final_leaf.self_state_sha256,
        "structural_cross_session_identity_continuity_verified": recovery_pair.same_self_state_lineage and recovery_pair.same_self_state_record and recovery_pair.same_self_state_sha256,
        "complete_psychological_continuity_claimed": bool(audits["134"].get("persistent_psychological_continuity_claimed")),
        "package_135_same_session_drive_trace_verified": audits["135"].get("trace_lineage_verified") is True and audits["135"].get("cross_session_reset_verified") is True,
        "drive_is_persistent_self_state": bool(audits["135"].get("drive_trace_is_self_state_content")),
        "drive_recovered_across_session": bool(audits["135"].get("drive_trace_restored_across_session")) or bool(audits["135"].get("package_134_drive_state_restored")),
        "package_136_bounded_modulation_infrastructure_verified": audits["136"].get("counterfactual_comparison_verified") is True and modulation_contract.fail_to_neutral_required,
        "production_drive_consumer_count": len(modulation_allowlist.production_consumer_ids),
        "modulation_fail_to_neutral_verified": audits["136"].get("cross_session_neutrality_verified") is True and audits["136"].get("session_expiry_verified") is True,
        "modulation_cross_session_persisted": bool(audits["136"].get("modulation_recovered_across_session")),
        "package_137_exact_teacher_review_gate_verified": audits["137"].get("exact_head_binding_verified") is True and audits["137"].get("exact_parent_binding_verified") is True and audits["137"].get("exact_delta_binding_verified") is True,
        "unreviewed_self_state_mutation_authorized": bool(audits["137"].get("unauthorized_mutation_became_authoritative")),
        "package_138_bounded_readback_verified": audits["138"].get("readback_contract_verified") is True and readback_contract.same_session_only,
        "production_readback_consumer_count": len(readback_allowlist.production_consumer_ids),
        "readback_behavior_authority_created": bool(audits["138"].get("runtime_behavior_influence_created")) or readback_contract.runtime_behavior_authority_allowed,
        "package_139_verified_ancestor_rollback_verified": audits["139"].get("rollback_cas_verified") is True and no_fork.strict_verified_ancestor_selected,
        "package_139_exact_roll_forward_verified": audits["139"].get("roll_forward_cas_verified") is True and no_fork.exact_preserved_descendant_restored,
        "package_139_no_fork_rule_verified": no_fork.identity_fork_created is False and no_fork.canonical_leaf_restored,
        "memory_restored_by_rollback": not rollback_comparison.memory_equivalent or bool(audits["139"].get("memory_restored")),
        "perception_history_restored_by_rollback": not rollback_comparison.perception_history_equivalent or bool(audits["139"].get("perception_history_restored")),
        "drive_restored_by_rollback": not rollback_comparison.drive_trace_equivalent or bool(audits["139"].get("drive_trace_restored")),
        "thought_restored_by_rollback": not rollback_comparison.thought_engine_equivalent or bool(audits["139"].get("thought_engine_used")),
        "action_restored_by_rollback": not rollback_comparison.action_equivalent or bool(audits["139"].get("action_created")),
        "output_restored_by_rollback": not rollback_comparison.output_equivalent or bool(audits["139"].get("output_created")),
        "semantic_identity_created": bool(audits["138"].get("semantic_identity_created")),
        "autobiographical_state_created": bool(audits["138"].get("autobiographical_memory_created")) or bool(audits["138"].get("psychological_state_created")),
        "thought_engine_created": any(bool(item.get("thought_engine_used") or item.get("thought_engine_influence_created") or item.get("thought_engine_capability_created")) for item in audits.values()),
        "automatic_purpose_created": any(bool(item.get("purpose_created_or_expanded") or item.get("purpose_scope_expanded")) for item in audits.values()),
        "automatic_action_created": any(bool(item.get("selected_action_created") or item.get("action_created") or item.get("action_capability_created")) for item in audits.values()),
        "output_authority_created": any(bool(item.get("output_created")) for item in audits.values()),
        "package_140_runtime_capability_created": False,
        "package_140_action_created": False,
        "package_141_implemented": False,
        "dlm_1_implemented": False,
    }


def _contract_hash_payload(
    contract: PersistentSelfStateAndDriveCapabilityContract,
) -> dict[str, Any]:
    payload = contract.to_dict()
    payload.pop("capability_contract_id", None)
    payload.pop("capability_contract_sha256", None)
    payload.pop("created_at", None)
    return payload


def _typed(record_type: type[Any], payload: dict[str, Any] | None) -> Any:
    if payload is None:
        raise ValueError(f"missing {record_type.__name__}")
    return record_type(**_tuple_tree(payload))


def _tuple_tree(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_tuple_tree(item) for item in value)
    if isinstance(value, dict):
        return {str(key): _tuple_tree(item) for key, item in value.items()}
    return value


def _one(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    items = tuple(records)
    if len(items) != 1:
        raise ValueError(f"expected exactly one record, found {len(items)}")
    return dict(items[0])


def _verified(
    records: dict[str, PersistentStateDriveAuthorityEvidenceRecord],
    package_id: str,
) -> bool:
    return records[package_id].evidence_status == "verified"


def _validate_external_paths(
    repo_root: Path,
    state_dir: Path,
    evidence_sources: tuple[Path, ...],
) -> None:
    if _is_within(state_dir, repo_root):
        raise ValueError("Package 140 state_dir must be outside the repository")
    for source in evidence_sources:
        if state_dir == source or _is_within(state_dir, source) or _is_within(source, state_dir):
            raise ValueError("Package 140 output and authority evidence roots must be separate")


def _is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _is_ancestor(root: Path, commit: str, head: str) -> bool:
    completed = subprocess.run(
        ("git", "merge-base", "--is-ancestor", commit, head),
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def _git_output(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", *arguments),
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def _repository_pollution_absent(root: Path) -> bool:
    untracked = _git_output(root, "ls-files", "--others", "--exclude-standard").splitlines()
    forbidden_suffixes = {".sqlite", ".sqlite3", ".db", ".wav", ".pcm"}
    for item in untracked:
        path = Path(item)
        if path.suffix.lower() in forbidden_suffixes or "__pycache__" in path.parts:
            return False
    return not any((root / "ashl_core_v1").rglob("package_140.sqlite3"))
