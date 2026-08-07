"""Package 133 representation-only self-state audit and regression runner."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.runtime.package_132_perception_attention_milestone_audit import (
    load_authoritative_closure_contract,
)
from ashl_core_v1.state.persistent_self_state_boundary import (
    build_state_like_structure_inventory,
    load_authoritative_self_state_contract,
    path_fingerprint,
)
from ashl_core_v1.state.persistent_self_state_lineage import (
    build_initial_self_state_record,
    build_self_state_lineage_validation_record,
    build_successor_self_state_records,
    validate_persistent_self_state_lineage,
)
from ashl_core_v1.state.persistent_self_state_schema import (
    AUDIT_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    CONTROL_NAMES,
    CONTROL_SCHEMA_VERSION,
    PACKAGE_132_PASS_STATUS,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    Package133BoundaryControlResult,
    Package133CrossSessionSelfStateSchemaAudit,
    Package133RegressionReceipt,
    PersistentSelfStateLineageValidationRecord,
    PersistentSelfStateRecord,
    PersistentSelfStateTransitionRecord,
)
from ashl_core_v1.state.persistent_self_state_store import (
    PersistentSelfStateStore,
)


PACKAGE_132_DATABASE = Path(
    "package_132_perception_attention_milestone_v0/package_132.sqlite3"
)

PACKAGE_134_MISSING_REQUIREMENTS = (
    "explicit_recovery_authorization_contract",
    "authoritative_active_head_compare_and_swap",
    "session_startup_load_and_identity_binding",
    "crash_interruption_and_partial_write_semantics",
    "recovery_selection_conflict_policy",
    "append_only_recovery_and_rollback_audit",
    "real_cross_process_recovery_run",
)

_STATE_ENGINE_REGRESSION_MODULES = (
    "ashl_core_v1.tests.test_cradle_state_persistence_handoff",
    "ashl_core_v1.tests.test_cradle_state_resume_precheck",
    "ashl_core_v1.tests.test_cradle_state_resume_selection_authorization",
    "ashl_core_v1.tests.test_cradle_state_restore_preview_resume_handoff",
    "ashl_core_v1.tests.test_state_engine_resume_continuity_audit",
    "ashl_core_v1.tests.test_session_persistence",
    "ashl_core_v1.tests.test_teacher_gated_session_store",
    "ashl_core_v1.tests.test_task_working_memory_lifecycle",
    "ashl_core_v1.tests.test_reviewed_concept_working_readback_preview",
    "ashl_core_v1.tests.test_operator_console_state_reader",
)


def preflight_package_133_cross_session_self_state_schema(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    package_132_state_dir: str | Path,
) -> dict[str, Any]:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    package_132_source = Path(package_132_state_dir).resolve()
    _validate_external_state_dir(root, output, (package_132_source,))
    source_head = _git_output(root, "rev-parse", "HEAD")
    package_132_audit = _read_package_132_audit(package_132_source)
    closure = load_authoritative_closure_contract(root)
    contract = load_authoritative_self_state_contract(root)
    inventory = build_state_like_structure_inventory(root)
    return {
        "source_head": source_head,
        "baseline_commit": BASELINE_COMMIT,
        "baseline_is_ancestor": _is_ancestor(root, BASELINE_COMMIT, source_head),
        "package_132_audit_id": package_132_audit["audit_id"],
        "package_132_audit_status": package_132_audit["audit_status"],
        "perception_line_status": package_132_audit["perception_line_status"],
        "package_132_source_fingerprint": path_fingerprint(package_132_source),
        "package_132_private_path_persisted": False,
        "closure_contract_id": closure.closure_contract_id,
        "persistent_self_state_contract_id": contract.contract_id,
        "state_like_structure_count": len(inventory),
        "state_like_inventory_verified": all(
            record.source_scan_verified for record in inventory
        ),
        "state_engine_continuity_authority_reused": (
            contract.state_engine_continuity_authority_reused
        ),
        "legacy_state_payload_reused": contract.legacy_state_payload_reused,
        "cross_session_recovery_enabled": contract.cross_session_recovery_enabled,
        "recognition_status": "ready_for_package_133_representation_chain",
    }


def create_package_133_representation_chain(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    parent_session_id: str,
    child_session_id: str,
) -> dict[str, Any]:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    _validate_external_state_dir(root, output, tuple())
    if parent_session_id == child_session_id:
        raise ValueError("Package 133 parent and child session provenance must differ")
    store = PersistentSelfStateStore(output)
    existing_states = store.list_payloads("persistent_self_state_records")
    if existing_states:
        existing_transitions = store.list_payloads(
            "persistent_self_state_transition_records"
        )
        existing_validations = store.list_payloads(
            "persistent_self_state_lineage_validations"
        )
        if (
            len(existing_states) < 2
            or len(existing_transitions) != len(existing_states) - 1
            or len(existing_validations) != len(existing_transitions)
        ):
            raise RuntimeError("Package 133 store contains an incomplete successor lineage")
        return {
            "contract": store.latest_payload(
                "persistent_self_state_representation_contracts"
            ),
            "parent": existing_states[0],
            "child": existing_states[1],
            "transition": existing_transitions[0],
            "lineage_validation": existing_validations[0],
            "existing_chain_reused": True,
        }
    contract = load_authoritative_self_state_contract(root)
    parent = build_initial_self_state_record(
        contract=contract,
        origin_session_id=parent_session_id,
    )
    child, transition = build_successor_self_state_records(
        parent=parent,
        contract=contract,
        source_session_id=child_session_id,
    )
    validation = build_self_state_lineage_validation_record(
        parent=parent,
        child=child,
        transition=transition,
    )
    _append_once(
        store,
        "persistent_self_state_representation_contracts",
        contract,
        contract.contract_id,
    )
    store.append_lineage_chain(
        parent=parent,
        child=child,
        transition=transition,
        validation=validation,
    )
    return {
        "contract": contract.to_dict(),
        "parent": parent.to_dict(),
        "child": child.to_dict(),
        "transition": transition.to_dict(),
        "lineage_validation": validation.to_dict(),
        "existing_chain_reused": False,
    }


def run_package_133_boundary_controls(
    *,
    contract: Any,
    parent: PersistentSelfStateRecord,
    child: PersistentSelfStateRecord,
    transition: PersistentSelfStateTransitionRecord,
    validation: PersistentSelfStateLineageValidationRecord,
    store: PersistentSelfStateStore,
) -> Package133BoundaryControlResult:
    def rejects(call: Callable[[], object]) -> bool:
        try:
            call()
        except (KeyError, TypeError, ValueError, RuntimeError):
            return True
        return False

    controls = {
        "raw_perception_rejected": rejects(lambda: replace(parent, raw_perception_embedded=True)),
        "world_fact_rejected": rejects(lambda: replace(parent, world_facts_embedded=True)),
        "memory_content_rejected": rejects(lambda: replace(parent, memory_content_embedded=True)),
        "semantic_history_rejected": rejects(lambda: replace(parent, semantic_history_embedded=True)),
        "output_content_rejected": rejects(lambda: replace(parent, output_content_embedded=True)),
        "recovery_authority_rejected": rejects(lambda: replace(parent, cross_session_recovery_authority=True)),
        "active_head_authority_rejected": rejects(lambda: replace(parent, active_head_selection_authority=True)),
        "behavior_influence_rejected": rejects(lambda: replace(parent, runtime_behavior_influence_authority=True)),
        "drive_signal_rejected": rejects(lambda: replace(parent, drive_signal_authority=True)),
        "memory_write_rejected": rejects(lambda: replace(parent, memory_write_authority=True)),
        "perception_control_rejected": rejects(lambda: replace(parent, perception_control_authority=True)),
        "action_selection_rejected": rejects(lambda: replace(parent, action_selection_authority=True)),
        "output_authority_rejected": rejects(lambda: replace(parent, output_authority=True)),
        "thought_engine_rejected": rejects(lambda: replace(parent, thought_engine_authority=True)),
        "unknown_persistent_field_rejected": rejects(
            lambda: replace(
                parent,
                persistent_field_names=parent.persistent_field_names + ("world_model",),
            )
        ),
        "same_session_successor_rejected": rejects(
            lambda: build_successor_self_state_records(
                parent=parent,
                contract=contract,
                source_session_id=parent.source_session_id,
            )
        ),
        "non_monotonic_version_rejected": rejects(
            lambda: replace(child, self_state_version=parent.self_state_version)
        ),
        "parent_hash_mismatch_rejected": rejects(
            lambda: replace(child, parent_self_state_sha256="0" * 64)
        ),
        "lineage_fork_rejected": rejects(
            lambda: _attempt_lineage_fork(
                store=store,
                contract=contract,
                parent=parent,
            )
        ),
        "store_mutation_rejected": all(
            rejects(call)
            for call in (
                lambda: store.update(),
                lambda: store.delete(),
                lambda: store.replace(),
                lambda: store.recover(),
                lambda: store.select_active_head(),
            )
        ),
    }
    ordered = tuple((name, controls[name]) for name in CONTROL_NAMES)
    identity_payload = {name: passed for name, passed in ordered}
    return Package133BoundaryControlResult(
        control_result_id=(
            f"package_133_controls:{sha256_payload(identity_payload)[:16]}"
        ),
        schema_version=CONTROL_SCHEMA_VERSION,
        created_at=utc_now(),
        controls=ordered,
        passed_count=sum(passed for _name, passed in ordered),
        expected_count=len(CONTROL_NAMES),
        controls_passed=all(passed for _name, passed in ordered),
    )


def run_package_133_regressions(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
) -> Package133RegressionReceipt:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    _validate_external_state_dir(root, output, tuple())
    store = PersistentSelfStateStore(output)
    pycache = store.root / "pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    commands: tuple[tuple[str, tuple[str, ...]], ...] = (
        (
            "targeted_package_133",
            (
                sys.executable,
                "-m",
                "unittest",
                "ashl_core_v1.tests.test_package_133_cross_session_self_state_schema",
            ),
        ),
        (
            "state_engine_and_state_like_regressions",
            (sys.executable, "-m", "unittest", *_STATE_ENGINE_REGRESSION_MODULES),
        ),
        (
            "package_132_regressions",
            (
                sys.executable,
                "-m",
                "unittest",
                "ashl_core_v1.tests.test_package_132_active_perception_attention_milestone",
            ),
        ),
        (
            "full_v1_unittest_discover",
            (sys.executable, "-m", "unittest", "discover"),
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
            timeout=1800,
            check=False,
        )
        combined = f"{completed.stdout}\n{completed.stderr}"
        results.append(
            (name, completed.returncode, sha256_bytes(combined.encode("utf-8")))
        )
        statuses[name] = completed.returncode == 0
    source_head = _git_output(root, "rev-parse", "HEAD")
    aggregate = all(statuses.values())
    receipt_core = {"source_head": source_head, "results": results}
    receipt = Package133RegressionReceipt(
        regression_receipt_id=(
            f"package_133_regressions:{sha256_payload(receipt_core)[:16]}"
        ),
        schema_version=REGRESSION_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        source_head=source_head,
        command_results=tuple(results),
        targeted_package_133_passed=statuses["targeted_package_133"],
        state_engine_regressions_passed=statuses[
            "state_engine_and_state_like_regressions"
        ],
        package_132_regressions_passed=statuses["package_132_regressions"],
        full_v1_discover_passed=statuses["full_v1_unittest_discover"],
        compileall_passed=statuses["compileall"],
        git_diff_check_passed=statuses["git_diff_check"],
        pycache_redirected_outside_repo=True,
        fresh_regressions_passed=aggregate,
    )
    _append_once(
        store,
        "package_133_regression_receipts",
        receipt,
        receipt.regression_receipt_id,
    )
    return receipt


def audit_package_133_cross_session_self_state_schema(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    package_132_state_dir: str | Path,
    append: bool = True,
) -> Package133CrossSessionSelfStateSchemaAudit:
    root = Path(ashl_root).resolve()
    output = Path(state_dir).resolve()
    package_132_source = Path(package_132_state_dir).resolve()
    _validate_external_state_dir(root, output, (package_132_source,))
    source_head = _git_output(root, "rev-parse", "HEAD")
    baseline_ancestor = _is_ancestor(root, BASELINE_COMMIT, source_head)

    package_132_before = _tree_snapshot(package_132_source)
    package_132_audit = _read_package_132_audit(package_132_source)
    closure = load_authoritative_closure_contract(root)
    contract = load_authoritative_self_state_contract(root)
    inventory_before = build_state_like_structure_inventory(root)

    store = PersistentSelfStateStore(output)
    states = store.list_payloads("persistent_self_state_records")
    transitions = store.list_payloads("persistent_self_state_transition_records")
    validations = store.list_payloads("persistent_self_state_lineage_validations")
    if (
        len(states) < 2
        or len(transitions) != len(states) - 1
        or len(validations) != len(transitions)
    ):
        raise RuntimeError("blocked_package_133_parent_child_representation_chain_missing")
    parent = PersistentSelfStateRecord.from_dict(states[0])
    child = PersistentSelfStateRecord.from_dict(states[1])
    transition = PersistentSelfStateTransitionRecord.from_dict(transitions[0])
    validation = PersistentSelfStateLineageValidationRecord(
        **{
            **validations[0],
            "failure_reasons": tuple(validations[0].get("failure_reasons") or ()),
            "source_record_refs": tuple(validations[0].get("source_record_refs") or ()),
        }
    )
    lineage = validate_persistent_self_state_lineage(parent, child, transition)
    controls = run_package_133_boundary_controls(
        contract=contract,
        parent=parent,
        child=child,
        transition=transition,
        validation=validation,
        store=store,
    )
    inventory_after = build_state_like_structure_inventory(root)
    package_132_after = _tree_snapshot(package_132_source)
    inventory_unchanged = _inventory_source_hashes(inventory_before) == _inventory_source_hashes(inventory_after)
    package_132_unchanged = package_132_before == package_132_after
    store_integrity = store.audit_integrity()
    regression = store.latest_payload("package_133_regression_receipts")

    package_132_verified = all(
        (
            package_132_audit.get("audit_status") == PACKAGE_132_PASS_STATUS,
            package_132_audit.get("perception_line_status")
            == "perception_capability_construction_line_frozen_after_package_132",
            package_132_audit.get("persistent_self_state_created") is False,
            package_132_audit.get("new_internal_action_created") is False,
            package_132_audit.get("failure_reasons") == [],
        )
    )
    inventory_verified = len(inventory_before) == 9 and all(
        record.source_scan_verified for record in inventory_before
    )
    continuity_reused = contract.state_engine_continuity_authority_reused and any(
        record.structure_kind == "state_engine_cradle_handoff"
        and record.self_state_classification
        == "continuity_authority_reused_boundary_only"
        for record in inventory_before
    )
    forbidden_content = {
        "raw_perception_persisted": parent.raw_perception_embedded
        or child.raw_perception_embedded,
        "world_fact_persisted": parent.world_facts_embedded
        or child.world_facts_embedded,
        "memory_content_persisted": parent.memory_content_embedded
        or child.memory_content_embedded,
        "semantic_history_persisted": parent.semantic_history_embedded
        or child.semantic_history_embedded,
        "output_content_persisted": parent.output_content_embedded
        or child.output_content_embedded,
    }
    forbidden_authority = {
        "cross_session_recovery_implemented": transition.recovery_performed,
        "active_head_created": bool(store_integrity["active_head_present"]),
        "runtime_behavior_influence_created": transition.behavior_influence_created,
        "drive_signal_created": transition.drive_signal_created,
        "memory_write_created": transition.memory_write_created,
        "perception_action_created": transition.perception_action_created,
        "thought_engine_used": parent.thought_engine_authority
        or child.thought_engine_authority,
        "output_created": transition.output_created,
        # Package 133's boundary is defined by its immutable records and store,
        # not by whether a later package exists in the repository.
        "package_134_implemented": bool(
            transition.recovery_performed
            or store_integrity["active_head_present"]
            or store_integrity["recovery_table_present"]
        ),
        "persistent_self_claimed": contract.persistent_self_claim_authorized,
    }
    checks = {
        "baseline_ancestor": baseline_ancestor,
        "package_132_audit": package_132_verified,
        "package_132_closure": (
            closure.perception_capability_construction_frozen
            and closure.next_core_package == "133"
            and "persistent_self_state" in closure.absent_capabilities
        ),
        "inventory_verified": inventory_verified,
        "inventory_sources_unchanged": inventory_unchanged,
        "package_132_source_unchanged": package_132_unchanged,
        "continuity_authority_reused": continuity_reused,
        "legacy_payload_not_reused": not contract.legacy_state_payload_reused,
        "representation_contract": (
            contract.parent_child_lineage_required
            and contract.append_only_persistence_required
            and not contract.cross_session_recovery_enabled
        ),
        "parent_child_lineage": bool(lineage["valid"] and validation.lineage_valid),
        "sessions_distinct": parent.source_session_id != child.source_session_id,
        "version_monotonic": child.self_state_version == parent.self_state_version + 1,
        "hash_chain": bool(
            lineage.get("parent_integrity_valid")
            and lineage.get("child_integrity_valid")
            and lineage.get("transition_integrity_valid")
            and lineage.get("parent_hash_link_exact")
        ),
        "append_only_store": bool(store_integrity["valid"]),
        "forbidden_content_absent": not any(forbidden_content.values()),
        "forbidden_authority_absent": not any(forbidden_authority.values()),
        "boundary_controls": controls.controls_passed,
        "fresh_regressions": bool(
            regression and regression.get("fresh_regressions_passed") is True
        ),
    }
    failures = tuple(name for name, passed in checks.items() if not passed)
    audit_status = PASS_STATUS if not failures else BLOCKED_STATUS
    audit_core = {
        "source_head": source_head,
        "package_132_audit_id": package_132_audit["audit_id"],
        "contract": contract.contract_sha256,
        "inventory": tuple(record.boundary_record_id for record in inventory_before),
        "parent": parent.self_state_record_id,
        "child": child.self_state_record_id,
        "transition": transition.transition_id,
        "lineage": validation.lineage_validation_id,
        "controls": controls.control_result_id,
        "regressions": regression.get("regression_receipt_id") if regression else None,
        "failures": failures,
    }
    audit_sha256 = sha256_payload(audit_core)
    audit = Package133CrossSessionSelfStateSchemaAudit(
        audit_id=f"package_133_audit:{audit_sha256[:16]}",
        audit_sha256=audit_sha256,
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        source_head=source_head,
        package_132_audit_id=str(package_132_audit["audit_id"]),
        package_132_audit_status=str(package_132_audit["audit_status"]),
        package_132_closure_verified=checks["package_132_closure"],
        perception_line_remains_frozen=checks["package_132_closure"],
        state_like_structure_count=len(inventory_before),
        state_like_inventory_verified=inventory_verified,
        state_like_sources_unchanged=inventory_unchanged,
        package_132_source_unchanged=package_132_unchanged,
        state_engine_continuity_authority_reused=continuity_reused,
        legacy_state_payload_reused=contract.legacy_state_payload_reused,
        representation_contract_id=contract.contract_id,
        representation_contract_verified=checks["representation_contract"],
        parent_self_state_record_id=parent.self_state_record_id,
        child_self_state_record_id=child.self_state_record_id,
        transition_id=transition.transition_id,
        lineage_validation_id=validation.lineage_validation_id,
        parent_child_lineage_verified=checks["parent_child_lineage"],
        parent_child_sessions_distinct=checks["sessions_distinct"],
        self_state_version_monotonic=checks["version_monotonic"],
        canonical_hash_chain_verified=checks["hash_chain"],
        append_only_store_verified=checks["append_only_store"],
        **forbidden_content,
        **forbidden_authority,
        boundary_controls_passed=controls.controls_passed,
        fresh_regressions_passed=checks["fresh_regressions"],
        audit_status=audit_status,
        failure_reasons=failures,
        package_134_missing_requirements=PACKAGE_134_MISSING_REQUIREMENTS,
        source_record_refs=(
            str(package_132_audit["audit_id"]),
            f"package_132_source:{path_fingerprint(package_132_source)[:16]}",
            contract.contract_id,
            parent.self_state_record_id,
            child.self_state_record_id,
            transition.transition_id,
            validation.lineage_validation_id,
            controls.control_result_id,
            str(regression.get("regression_receipt_id"))
            if regression
            else "package_133_regressions:missing",
        ),
    )
    if append:
        for record in inventory_before:
            _append_once(
                store,
                "state_like_structure_boundary_records",
                record,
                record.boundary_record_id,
            )
        _append_once(
            store,
            "persistent_self_state_representation_contracts",
            contract,
            contract.contract_id,
        )
        _append_once(
            store,
            "package_133_boundary_control_results",
            controls,
            controls.control_result_id,
        )
        _append_once(store, "package_133_audits", audit, audit.audit_id)
    return audit


def _attempt_lineage_fork(
    *,
    store: PersistentSelfStateStore,
    contract: Any,
    parent: PersistentSelfStateRecord,
) -> None:
    child, transition = build_successor_self_state_records(
        parent=parent,
        contract=contract,
        source_session_id="package_133_fork_control_session",
    )
    validation = build_self_state_lineage_validation_record(
        parent=parent,
        child=child,
        transition=transition,
    )
    store.append_lineage_chain(
        parent=parent,
        child=child,
        transition=transition,
        validation=validation,
    )


def _read_package_132_audit(state_dir: Path) -> dict[str, Any]:
    database = state_dir / PACKAGE_132_DATABASE
    if not database.is_file():
        raise FileNotFoundError(database)
    with closing(
        sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
    ) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        row = connection.execute(
            "SELECT payload_json, payload_sha256 FROM package_132_audits ORDER BY row_id DESC LIMIT 1"
        ).fetchone()
        integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
    if row is None or integrity != "ok":
        raise RuntimeError("blocked_package_132_audit_missing_or_invalid")
    payload = json.loads(str(row["payload_json"]))
    if str(row["payload_sha256"]) != sha256_payload(payload):
        raise RuntimeError("blocked_package_132_audit_payload_hash_mismatch")
    if payload.get("audit_status") != PACKAGE_132_PASS_STATUS:
        raise RuntimeError("blocked_package_132_audit_not_passed")
    return payload


def _tree_snapshot(root: Path) -> str:
    if not root.is_dir():
        raise FileNotFoundError(root)
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_symlink():
            raise ValueError("Package 133 evidence roots cannot contain symlinks")
        if path.is_file():
            data = path.read_bytes()
            entries.append(
                {
                    "relative_path": path.relative_to(root).as_posix(),
                    "size_bytes": len(data),
                    "sha256": sha256_bytes(data),
                }
            )
    return sha256_payload(entries)


def _inventory_source_hashes(records: tuple[Any, ...]) -> tuple[tuple[str, ...], ...]:
    return tuple(record.source_file_sha256s for record in records)


def _append_once(
    store: PersistentSelfStateStore,
    table: str,
    record: Any,
    record_id: str,
) -> None:
    if not store.has_record(table, record_id):
        store.append_generic_record(table, record)


def _validate_external_state_dir(
    repo_root: Path,
    state_dir: Path,
    evidence_sources: tuple[Path, ...],
) -> None:
    if _is_within(state_dir, repo_root):
        raise ValueError("Package 133 state_dir must be outside the repository")
    for source in evidence_sources:
        if state_dir == source or _is_within(state_dir, source) or _is_within(source, state_dir):
            raise ValueError("Package 133 output and evidence state roots must be separate")


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
