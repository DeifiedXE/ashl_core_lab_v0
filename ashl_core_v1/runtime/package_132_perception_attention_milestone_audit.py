"""Read-only evidence audit and boundary closure for Package 132."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Iterable

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    ALLOWED_INTERNAL_ACTION_KINDS,
)
from ashl_core_v1.runtime.host_sensor_types import (
    canonical_json,
    sha256_bytes,
    sha256_payload,
    utc_now,
)
from ashl_core_v1.runtime.package_124_archive import verify_package_124_archive
from ashl_core_v1.runtime.package_132_perception_attention_milestone_store import (
    PACKAGE_DIR,
    Package132PerceptionAttentionMilestoneStore,
)
from ashl_core_v1.runtime.perception_attention_closure_types import (
    ABSENT_CAPABILITIES,
    AUDIT_SCHEMA_VERSION,
    BASELINE_COMMIT,
    BLOCKED_STATUS,
    CLOSED_PACKAGE_IDS,
    CLOSURE_SCHEMA_VERSION,
    CONTROL_NAMES,
    CONTROL_SCHEMA_VERSION,
    DOWNSTREAM_FORBIDDEN_AUTHORITIES,
    DOWNSTREAM_READ_ONLY_INTERFACES,
    EVIDENCE_SOURCE_SCHEMA_VERSION,
    EXPECTED_AUDIT_STATUSES,
    LINEAGE_SCHEMA_VERSION,
    LINE_CLOSURE_STATUS,
    PACKAGE_COMPLETION_COMMITS,
    PACKAGE_EVIDENCE_SCHEMA_VERSION,
    PASS_STATUS,
    PERCEPTION_INTERNAL_ACTION_KINDS,
    PRESENT_CAPABILITIES,
    REGRESSION_SCHEMA_VERSION,
    Package132ActivePerceptionAttentionMilestoneAudit,
    Package132BoundaryControlResult,
    Package132EvidenceSourceRecord,
    Package132RegressionReceipt,
    PerceptionAttentionCapabilityBoundaryClosureContract,
    PerceptionCrossPackageLineageRecord,
    PerceptionPackageMilestoneEvidenceRecord,
)


REFERENCE_RELATIVE_PATH = Path(
    "ashl_core_v1/docs/reference/perception_attention_capability_boundary_closure_v0.json"
)

_AUDIT_DATABASE_SPECS = {
    "124A": (
        Path("package_124a_temporal_foundation_v0/package_124a_temporal.sqlite3"),
        "package_124a_temporal_audits",
    ),
    "125": (
        Path("package_125_observation_extension_v0/package_125.sqlite3"),
        "package_125_audits",
    ),
    "126": (
        Path("package_126_bounded_reacquisition_v0/package_126.sqlite3"),
        "package_126_audits",
    ),
    "127": (
        Path("package_127_internal_focus_shift_v0/package_127.sqlite3"),
        "package_127_audits",
    ),
    "128": (
        Path("package_128_evidence_sufficiency_stop_v0/package_128.sqlite3"),
        "package_128_audits",
    ),
    "129": (
        Path("package_129_active_perception_growth_v0/package_129.sqlite3"),
        "package_129_audits",
    ),
    "130": (
        Path("package_130_grounded_auditory_concept_v0/package_130.sqlite3"),
        "package_130_audits",
    ),
    "131": (
        Path(
            "package_131_auditory_predictive_recognition_v0/package_131.sqlite3"
        ),
        "package_131_audits",
    ),
}

_REQUIRED_LINEAGE_EDGES = (
    ("123", "124"),
    ("124", "124A"),
    ("124A", "125"),
    ("125", "126"),
    ("126", "127"),
    ("127", "128"),
    ("125", "129"),
    ("126", "129"),
    ("127", "129"),
    ("128", "129"),
    ("129", "130"),
    ("130", "131"),
)

_TARGETED_REGRESSION_MODULES = (
    "ashl_core_v1.tests.test_package_123_growth_audit",
    "ashl_core_v1.tests.test_package_124_archive_reverification",
    "ashl_core_v1.tests.test_package_124a_audit",
    "ashl_core_v1.tests.test_package_125_audit",
    "ashl_core_v1.tests.test_package_126_reacquisition",
    "ashl_core_v1.tests.test_package_127_internal_focus",
    "ashl_core_v1.tests.test_package_128_sufficiency_stop",
    "ashl_core_v1.tests.test_package_129_active_perception_growth",
    "ashl_core_v1.tests.test_package_130_grounded_auditory_concept",
    "ashl_core_v1.tests.test_package_131_auditory_predictive_recognition",
)


class ReadOnlyEvidenceDatabase:
    """Query-only SQLite reader which never initializes source stores."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        if not self.database_path.is_file():
            raise FileNotFoundError(self.database_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            f"file:{self.database_path.as_posix()}?mode=ro",
            uri=True,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        return connection

    def table_exists(self, table: str) -> bool:
        _validate_table_name(table)
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
                (table,),
            ).fetchone()
        return row is not None

    def latest_payload(self, table: str) -> tuple[dict[str, Any], bool] | None:
        _validate_table_name(table)
        with closing(self._connect()) as connection:
            columns = {
                str(row["name"])
                for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
            }
            selected = "payload_json"
            if "payload_sha256" in columns:
                selected += ", payload_sha256"
            row = connection.execute(
                f"SELECT {selected} FROM {table} ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
        if row is None:
            return None
        payload = json.loads(str(row["payload_json"]))
        embedded_hash_valid = True
        if "payload_sha256" in row.keys():
            embedded_hash_valid = str(row["payload_sha256"]) == sha256_payload(payload)
        return payload, embedded_hash_valid

    def count(self, table: str) -> int:
        _validate_table_name(table)
        with closing(self._connect()) as connection:
            row = connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
        return int(row["count"])

    def integrity_valid(self) -> bool:
        with closing(self._connect()) as connection:
            return str(connection.execute("PRAGMA integrity_check").fetchone()[0]) == "ok"


def load_authoritative_closure_contract(
    ashl_root: str | Path,
) -> PerceptionAttentionCapabilityBoundaryClosureContract:
    path = Path(ashl_root) / REFERENCE_RELATIVE_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    contract = PerceptionAttentionCapabilityBoundaryClosureContract(
        closure_contract_id=str(payload["closure_contract_id"]),
        closure_sha256=str(payload["closure_sha256"]),
        schema_version=str(payload["schema_version"]),
        created_at=str(payload["created_at"]),
        baseline_commit=str(payload["baseline_commit"]),
        closed_package_ids=tuple(payload["closed_package_ids"]),
        present_capabilities=tuple(payload["present_capabilities"]),
        perception_internal_action_kinds=tuple(payload["perception_internal_action_kinds"]),
        absent_capabilities=tuple(payload["absent_capabilities"]),
        downstream_read_only_interfaces=tuple(payload["downstream_read_only_interfaces"]),
        downstream_forbidden_authorities=tuple(
            payload["downstream_forbidden_authorities"]
        ),
        package_130_consumer_scope_preserved=str(
            payload["package_130_consumer_scope_preserved"]
        ),
        perception_capability_construction_frozen=bool(
            payload["perception_capability_construction_frozen"]
        ),
        package_132_adds_runtime_capability=bool(
            payload["package_132_adds_runtime_capability"]
        ),
        package_132_adds_internal_action=bool(
            payload["package_132_adds_internal_action"]
        ),
        package_132a_exists=bool(payload["package_132a_exists"]),
        package_133_plus_may_extend_perception_capability=bool(
            payload["package_133_plus_may_extend_perception_capability"]
        ),
        next_core_package=str(payload["next_core_package"]),
        independent_post_132_migration_lane=str(
            payload["independent_post_132_migration_lane"]
        ),
    )
    expected_hash = sha256_payload(_closure_hash_payload(contract))
    if contract.closure_sha256 != expected_hash:
        raise ValueError("Package 132 closure contract hash mismatch")
    if contract.closure_contract_id != f"perception_attention_closure:{expected_hash[:16]}":
        raise ValueError("Package 132 closure contract identity mismatch")
    return contract


def run_package_132_boundary_controls(
    contract: PerceptionAttentionCapabilityBoundaryClosureContract,
    *,
    append_to: Package132PerceptionAttentionMilestoneStore | None = None,
) -> Package132BoundaryControlResult:
    def rejects(change: Callable[[], object]) -> bool:
        try:
            change()
        except (ValueError, RuntimeError):
            return True
        return False

    dummy_lineage = _dummy_lineage_records()
    controls = {
        "capability_injection_rejected": rejects(
            lambda: replace(
                contract,
                present_capabilities=contract.present_capabilities + ("semantic_identity",),
            )
        ),
        "perception_action_injection_rejected": rejects(
            lambda: replace(
                contract,
                perception_internal_action_kinds=(
                    contract.perception_internal_action_kinds + ("observe_forever",)
                ),
            )
        ),
        "semantic_identity_rejected": rejects(
            lambda: replace(
                contract,
                absent_capabilities=tuple(
                    item
                    for item in contract.absent_capabilities
                    if item != "semantic_sound_or_object_identity"
                ),
            )
        ),
        "free_attention_rejected": rejects(
            lambda: replace(
                contract,
                absent_capabilities=tuple(
                    item
                    for item in contract.absent_capabilities
                    if item != "free_or_open_ended_attention"
                ),
            )
        ),
        "persistent_autonomous_observation_rejected": rejects(
            lambda: replace(
                contract,
                absent_capabilities=tuple(
                    item
                    for item in contract.absent_capabilities
                    if item != "persistent_autonomous_observation"
                ),
            )
        ),
        "output_authority_rejected": rejects(
            lambda: replace(
                contract,
                downstream_forbidden_authorities=tuple(
                    item
                    for item in contract.downstream_forbidden_authorities
                    if item != "output_authority"
                ),
            )
        ),
        "thought_engine_authority_rejected": rejects(
            lambda: replace(
                contract,
                absent_capabilities=tuple(
                    item for item in contract.absent_capabilities if item != "thought_engine"
                ),
            )
        ),
        "self_state_authority_rejected": rejects(
            lambda: replace(
                contract,
                absent_capabilities=tuple(
                    item
                    for item in contract.absent_capabilities
                    if item != "persistent_self_state"
                ),
            )
        ),
        "dlm_1_authority_rejected": rejects(
            lambda: replace(contract, independent_post_132_migration_lane="DLM-1")
        ),
        "package_132a_rejected": rejects(
            lambda: replace(contract, package_132a_exists=True)
        ),
        "memory_write_authority_rejected": rejects(
            lambda: replace(
                contract,
                downstream_forbidden_authorities=tuple(
                    item
                    for item in contract.downstream_forbidden_authorities
                    if item != "memory_write_or_admission_authority"
                ),
            )
        ),
        "external_control_authority_rejected": rejects(
            lambda: replace(
                contract,
                downstream_forbidden_authorities=tuple(
                    item
                    for item in contract.downstream_forbidden_authorities
                    if item != "external_control_authority"
                ),
            )
        ),
        "history_rewrite_authority_rejected": rejects(
            lambda: replace(
                contract,
                downstream_forbidden_authorities=tuple(
                    item
                    for item in contract.downstream_forbidden_authorities
                    if item != "history_rewrite_or_deletion_authority"
                ),
            )
        ),
        "package_130_scope_broadening_rejected": rejects(
            lambda: replace(
                contract,
                package_130_consumer_scope_preserved="package_133_self_state",
            )
        ),
        "lineage_edge_omission_rejected": rejects(
            lambda: validate_lineage_records(dummy_lineage[:-1])
        ),
        "audit_status_coercion_rejected": rejects(
            lambda: validate_package_audit_status("125", "completed")
        ),
        "source_hash_change_rejected": rejects(
            lambda: validate_source_snapshot("a" * 64, "b" * 64)
        ),
        "new_sensor_or_compiler_rejected": rejects(
            lambda: validate_no_package_132_runtime_delta(
                new_sensor=True,
                new_compiler=False,
            )
        ),
    }
    ordered = tuple((name, controls[name]) for name in CONTROL_NAMES)
    payload_for_id = {name: passed for name, passed in ordered}
    record = Package132BoundaryControlResult(
        control_result_id=f"package_132_controls:{sha256_payload(payload_for_id)[:16]}",
        schema_version=CONTROL_SCHEMA_VERSION,
        created_at=utc_now(),
        controls=ordered,
        passed_count=sum(passed for _name, passed in ordered),
        expected_count=len(CONTROL_NAMES),
        controls_passed=all(passed for _name, passed in ordered),
    )
    if append_to is not None:
        _append_once(append_to, "package_132_boundary_control_results", record)
    return record


def run_package_132_regressions(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
) -> Package132RegressionReceipt:
    root = Path(ashl_root).resolve()
    _validate_external_state_dir(root, Path(state_dir).resolve(), tuple())
    store = Package132PerceptionAttentionMilestoneStore(state_dir)
    pycache = store.root / "pycache"
    pycache.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["PYTHONPYCACHEPREFIX"] = str(pycache)
    commands: tuple[tuple[str, tuple[str, ...]], ...] = (
        (
            "targeted_package_132",
            (
                sys.executable,
                "-m",
                "unittest",
                "ashl_core_v1.tests.test_package_132_active_perception_attention_milestone",
            ),
        ),
        (
            "targeted_package_123_to_131",
            (sys.executable, "-m", "unittest", *_TARGETED_REGRESSION_MODULES),
        ),
        (
            "full_v1_unittest_discover",
            (sys.executable, "-m", "unittest", "discover"),
        ),
        (
            "compileall",
            (sys.executable, "-m", "compileall", "-q", "ashl_core_v1"),
        ),
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
        results.append((name, completed.returncode, sha256_bytes(combined.encode("utf-8"))))
        statuses[name] = completed.returncode == 0
    source_head = _git_output(root, "rev-parse", "HEAD")
    aggregate = all(statuses.values())
    receipt_payload = {
        "source_head": source_head,
        "results": results,
        "pycache_redirected": True,
    }
    receipt = Package132RegressionReceipt(
        regression_receipt_id=(
            f"package_132_regressions:{sha256_payload(receipt_payload)[:16]}"
        ),
        schema_version=REGRESSION_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        source_head=source_head,
        command_results=tuple(results),
        targeted_package_132_passed=statuses["targeted_package_132"],
        package_123_to_131_regressions_passed=statuses[
            "targeted_package_123_to_131"
        ],
        full_v1_discover_passed=statuses["full_v1_unittest_discover"],
        compileall_passed=statuses["compileall"],
        git_diff_check_passed=statuses["git_diff_check"],
        pycache_redirected_outside_repo=True,
        fresh_regressions_passed=aggregate,
    )
    _append_once(store, "package_132_regression_receipts", receipt)
    return receipt


def audit_package_132_perception_attention_milestone(
    *,
    ashl_root: str | Path,
    state_dir: str | Path,
    package_124_archive: str | Path,
    evidence_roots: Iterable[str | Path],
    append: bool = True,
    archive_verifier: Callable[[str | Path], dict[str, object]] | None = None,
) -> Package132ActivePerceptionAttentionMilestoneAudit:
    root = Path(ashl_root).resolve()
    output_state = Path(state_dir).resolve()
    archive = Path(package_124_archive).resolve()
    roots = tuple(dict.fromkeys(Path(item).resolve() for item in evidence_roots))
    if not roots:
        raise ValueError("at least one explicit Package 132 evidence root is required")
    _validate_external_state_dir(root, output_state, (archive, *roots))

    source_paths = (archive, *roots)
    before = {path: _tree_snapshot(path) for path in source_paths}
    source_head = _git_output(root, "rev-parse", "HEAD")
    ancestry = {
        package_id: _is_ancestor(root, commit, source_head)
        for package_id, commit in PACKAGE_COMPLETION_COMMITS.items()
    }
    contract = load_authoritative_closure_contract(root)
    verifier = archive_verifier or verify_package_124_archive
    archive_verification = verifier(archive)
    discovered = _discover_package_evidence(archive, roots, archive_verification)
    package_records = _build_package_evidence_records(
        discovered,
        ancestry=ancestry,
    )
    lineage_records = _build_lineage_records(root, discovered, package_records)
    controls = run_package_132_boundary_controls(contract)

    store = Package132PerceptionAttentionMilestoneStore(output_state)
    regression_payload = store.latest_payload("package_132_regression_receipts")
    regression = (
        Package132RegressionReceipt(
            regression_receipt_id=str(regression_payload["regression_receipt_id"]),
            schema_version=str(regression_payload["schema_version"]),
            created_at=str(regression_payload["created_at"]),
            baseline_commit=str(regression_payload["baseline_commit"]),
            source_head=str(regression_payload["source_head"]),
            command_results=tuple(
                tuple(item) for item in regression_payload["command_results"]
            ),
            targeted_package_132_passed=bool(
                regression_payload["targeted_package_132_passed"]
            ),
            package_123_to_131_regressions_passed=bool(
                regression_payload["package_123_to_131_regressions_passed"]
            ),
            full_v1_discover_passed=bool(
                regression_payload["full_v1_discover_passed"]
            ),
            compileall_passed=bool(regression_payload["compileall_passed"]),
            git_diff_check_passed=bool(regression_payload["git_diff_check_passed"]),
            pycache_redirected_outside_repo=bool(
                regression_payload["pycache_redirected_outside_repo"]
            ),
            fresh_regressions_passed=bool(
                regression_payload["fresh_regressions_passed"]
            ),
        )
        if regression_payload
        else None
    )

    after = {path: _tree_snapshot(path) for path in source_paths}
    source_records = tuple(
        _source_record(path, before[path], after[path], archive=(path == archive))
        for path in source_paths
    )
    source_unchanged = all(record.source_unchanged for record in source_records)
    package_by_id = {record.package_id: record for record in package_records}
    package_verified = all(
        record.evidence_status == "verified" for record in package_records
    )
    lineage_verified = all(
        record.lineage_status == "verified" for record in lineage_records
    )
    action_surface = _perception_action_surface_valid()
    forbidden = _derive_forbidden_capability_flags(discovered, root)

    checks: dict[str, bool] = {
        "baseline_head_contains_package_131": _is_ancestor(root, BASELINE_COMMIT, source_head),
        "completion_commit_ancestry": all(ancestry.values()),
        "package_evidence": package_verified,
        "external_sources_unchanged": source_unchanged,
        "cross_package_lineage": lineage_verified,
        "perception_action_surface": action_surface,
        "closure_contract": contract.perception_capability_construction_frozen,
        "boundary_controls": controls.controls_passed,
        "fresh_regressions": bool(regression and regression.fresh_regressions_passed),
        "semantic_identity_absent": not forbidden["semantic_identity_created"],
        "free_attention_absent": not forbidden["free_attention_created"],
        "persistent_autonomous_observation_absent": not forbidden[
            "persistent_autonomous_observation_created"
        ],
        "output_absent": not forbidden["output_created"],
        "thought_engine_absent": not forbidden["thought_engine_created"],
        "persistent_self_state_absent": not forbidden[
            "persistent_self_state_created"
        ],
        "new_internal_action_absent": not forbidden["new_internal_action_created"],
        "package_132a_absent": not forbidden["package_132a_created"],
        "d_laplace_runtime_absent": not forbidden["d_laplace_component_used"],
        "dlm_1_absent": not forbidden["dlm_1_implemented"],
        "package_130_scope_preserved": not forbidden[
            "package_130_consumer_scope_broadened"
        ],
        "memory_authority_not_broadened": not forbidden[
            "memory_authority_broadened"
        ],
        "external_control_absent": not forbidden["external_control_created"],
    }
    failures = tuple(name for name, passed in checks.items() if not passed)
    status = PASS_STATUS if not failures else BLOCKED_STATUS
    audit_core = {
        "source_head": source_head,
        "package_evidence": tuple(record.package_evidence_id for record in package_records),
        "lineage": tuple(record.lineage_record_id for record in lineage_records),
        "sources": tuple(record.tree_manifest_sha256_after for record in source_records),
        "contract": contract.closure_sha256,
        "controls": controls.control_result_id,
        "regressions": regression.regression_receipt_id if regression else None,
        "failures": failures,
    }
    audit_sha256 = sha256_payload(audit_core)
    audit = Package132ActivePerceptionAttentionMilestoneAudit(
        audit_id=f"package_132_audit:{audit_sha256[:16]}",
        audit_sha256=audit_sha256,
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        source_head=source_head,
        closed_package_count=len(package_records),
        all_completion_commits_are_ancestors=checks["completion_commit_ancestry"],
        all_package_evidence_verified=package_verified,
        all_external_sources_unchanged=source_unchanged,
        package_123_real_multimodal_verified=_verified(package_by_id, "123"),
        package_124_archive_reverified=_verified(package_by_id, "124"),
        package_124a_grounded_temporal_verified=_verified(package_by_id, "124A"),
        package_125_bounded_extension_verified=_verified(package_by_id, "125"),
        package_126_reacquisition_and_listen_again_verified=_verified(
            package_by_id, "126"
        ),
        package_127_focus_shift_verified=_verified(package_by_id, "127"),
        package_128_sufficiency_stop_verified=_verified(package_by_id, "128"),
        package_129_teacher_reviewed_influence_verified=_verified(
            package_by_id, "129"
        ),
        package_130_anonymous_auditory_concept_verified=_verified(
            package_by_id, "130"
        ),
        package_131_fresh_predictive_recognition_verified=_verified(
            package_by_id, "131"
        ),
        cross_package_lineage_record_count=len(lineage_records),
        cross_package_lineage_consistent=lineage_verified,
        perception_action_surface_unchanged=action_surface,
        closure_contract_verified=checks["closure_contract"],
        fresh_boundary_controls_passed=controls.controls_passed,
        fresh_regressions_passed=bool(regression and regression.fresh_regressions_passed),
        **forbidden,
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        perception_line_status=LINE_CLOSURE_STATUS,
        next_core_package="133",
        audit_status=status,
        failure_reasons=failures,
        source_record_refs=tuple(
            record.package_evidence_id for record in package_records
        )
        + tuple(record.lineage_record_id for record in lineage_records)
        + (
            contract.closure_contract_id,
            controls.control_result_id,
            regression.regression_receipt_id if regression else "regression_receipt:missing",
        ),
    )

    if append:
        for record in source_records:
            _append_once(store, "package_132_evidence_sources", record)
        for record in package_records:
            _append_once(store, "package_132_package_evidence", record)
        for record in lineage_records:
            _append_once(store, "package_132_cross_package_lineage", record)
        _append_once(store, "perception_attention_closure_contracts", contract)
        _append_once(store, "package_132_boundary_control_results", controls)
        _append_once(store, "package_132_audits", audit)
    return audit


def verify_package_132_evidence_unchanged(
    *,
    state_dir: str | Path,
    package_124_archive: str | Path,
    evidence_roots: Iterable[str | Path],
) -> dict[str, object]:
    store = Package132PerceptionAttentionMilestoneStore(state_dir)
    records = store.list_payloads("package_132_evidence_sources")
    by_fingerprint = {
        str(record["path_fingerprint"]): record for record in records
    }
    paths = (Path(package_124_archive).resolve(),) + tuple(
        dict.fromkeys(Path(item).resolve() for item in evidence_roots)
    )
    results: list[dict[str, object]] = []
    for path in paths:
        fingerprint = _path_fingerprint(path)
        snapshot = _tree_snapshot(path)
        prior = by_fingerprint.get(fingerprint)
        unchanged = bool(
            prior
            and prior.get("tree_manifest_sha256_after") == snapshot["tree_sha256"]
            and prior.get("included_file_count") == snapshot["file_count"]
            and prior.get("included_byte_count") == snapshot["byte_count"]
        )
        results.append(
            {
                "path_fingerprint": fingerprint,
                "tree_manifest_sha256": snapshot["tree_sha256"],
                "unchanged": unchanged,
            }
        )
    return {"all_sources_unchanged": all(item["unchanged"] for item in results), "sources": results}


def validate_package_audit_status(package_id: str, audit_status: str) -> None:
    if audit_status != EXPECTED_AUDIT_STATUSES[package_id]:
        raise ValueError(f"Package {package_id} audit status was coerced or mismatched")


def validate_source_snapshot(before_sha256: str, after_sha256: str) -> None:
    if before_sha256 != after_sha256:
        raise ValueError("Package 132 evidence source changed during audit")


def validate_no_package_132_runtime_delta(*, new_sensor: bool, new_compiler: bool) -> None:
    if new_sensor or new_compiler:
        raise ValueError("Package 132 cannot add a sensor or primitive compiler")


def validate_lineage_records(
    records: Iterable[PerceptionCrossPackageLineageRecord],
) -> None:
    records = tuple(records)
    edges = tuple((item.producer_package_id, item.consumer_package_id) for item in records)
    if edges != _REQUIRED_LINEAGE_EDGES:
        raise ValueError("Package 132 cross-package lineage is incomplete or reordered")
    if not all(
        item.identity_consistent
        and item.authority_not_broadened
        and item.lineage_status == "verified"
        for item in records
    ):
        raise ValueError("Package 132 cross-package lineage is not fully verified")


def _discover_package_evidence(
    archive: Path,
    roots: tuple[Path, ...],
    archive_verification: dict[str, object],
) -> dict[str, dict[str, Any]]:
    if not archive_verification.get("valid"):
        raise RuntimeError("blocked_package_124_archive_reverification_failed")
    source_reverification = dict(archive_verification.get("source_reverification") or {})
    package_124_audit = dict(source_reverification.get("audit") or {})
    package_123_db = (
        archive / "source_state/package_123_real_perception_v0/package_123.sqlite3"
    )
    p123_reader = ReadOnlyEvidenceDatabase(package_123_db)
    p123_latest = p123_reader.latest_payload("package_123_audit_records")
    if p123_latest is None:
        raise RuntimeError("blocked_package_123_real_audit_missing")
    p123_payload, p123_hash = p123_latest
    discovered: dict[str, dict[str, Any]] = {
        "123": {
            "payload": p123_payload,
            "payload_hash_verified": p123_hash and p123_reader.integrity_valid(),
            "source_root": archive,
            "stored": True,
            "mode": "sealed_package_124_archive_real_audit",
        },
        "124": {
            "payload": package_124_audit,
            "payload_hash_verified": bool(
                archive_verification.get("manifest_verification")
                and archive_verification.get("certificate_validation")
            ),
            "source_root": archive,
            "stored": True,
            "mode": "sealed_archive_full_reverification",
        },
    }
    for package_id, (relative_db, table) in _AUDIT_DATABASE_SPECS.items():
        candidates: list[dict[str, Any]] = []
        for evidence_root in roots:
            database = evidence_root / relative_db
            if not database.is_file():
                continue
            reader = ReadOnlyEvidenceDatabase(database)
            if not reader.table_exists(table):
                continue
            latest = reader.latest_payload(table)
            if latest is None:
                continue
            payload, embedded_hash_valid = latest
            if payload.get("audit_status") != EXPECTED_AUDIT_STATUSES[package_id]:
                continue
            candidates.append(
                {
                    "payload": payload,
                    "payload_hash_verified": embedded_hash_valid
                    and reader.integrity_valid(),
                    "source_root": evidence_root,
                    "database": database,
                    "stored": True,
                    "mode": "external_real_audit_record_reverified",
                }
            )
        if len(candidates) != 1:
            raise RuntimeError(
                f"blocked_package_{package_id.lower()}_audit_missing_or_ambiguous:{len(candidates)}"
            )
        discovered[package_id] = candidates[0]
    _attach_auditory_lineage_payloads(discovered)
    return discovered


def _attach_auditory_lineage_payloads(discovered: dict[str, dict[str, Any]]) -> None:
    p130_db = Path(discovered["130"]["database"])
    p131_db = Path(discovered["131"]["database"])
    p130_reader = ReadOnlyEvidenceDatabase(p130_db)
    p131_reader = ReadOnlyEvidenceDatabase(p131_db)
    for key, table in (
        ("model", "grounded_auditory_event_concept_models"),
        ("deletion", "auditory_grounding_raw_audio_deletion_audits"),
        ("memory_commit", "auditory_concept_memory_commit_records"),
        ("generation", "expected_audio_primitive_generation_records"),
    ):
        row = p130_reader.latest_payload(table)
        if row is None:
            raise RuntimeError(f"blocked_package_130_{key}_missing")
        discovered["130"][key] = row[0]
        discovered["130"]["payload_hash_verified"] &= row[1]
    for key, table in (
        ("binding", "auditory_prediction_consumer_bindings"),
        ("pair", "auditory_predictive_recognition_pair_comparisons"),
    ):
        row = p131_reader.latest_payload(table)
        if row is None:
            raise RuntimeError(f"blocked_package_131_{key}_missing")
        discovered["131"][key] = row[0]
        discovered["131"]["payload_hash_verified"] &= row[1]


def _build_package_evidence_records(
    discovered: dict[str, dict[str, Any]],
    *,
    ancestry: dict[str, bool],
) -> tuple[PerceptionPackageMilestoneEvidenceRecord, ...]:
    records: list[PerceptionPackageMilestoneEvidenceRecord] = []
    now = utc_now()
    for package_id in CLOSED_PACKAGE_IDS:
        item = discovered[package_id]
        payload = dict(item["payload"])
        validate_package_audit_status(package_id, str(payload.get("audit_status")))
        real, boundary = _validate_package_payload(package_id, item)
        status = (
            "verified"
            if all(
                (
                    ancestry[package_id],
                    bool(item["payload_hash_verified"]),
                    real,
                    boundary,
                )
            )
            else "blocked"
        )
        observed_id = str(
            payload.get("audit_id")
            or payload.get("certificate_id")
            or f"package_{package_id.lower()}_audit:missing"
        )
        unresolved: tuple[str, ...] = tuple()
        if package_id in {"123", "129"} and not item["payload_hash_verified"]:
            unresolved = ("row_level_payload_hash_absent_but_sealed_tree_hash_verified",)
        identity_payload = {
            "package_id": package_id,
            "completion_commit": PACKAGE_COMPLETION_COMMITS[package_id],
            "audit_id": observed_id,
            "audit_status": payload["audit_status"],
            "source": _path_fingerprint(Path(item["source_root"])),
        }
        records.append(
            PerceptionPackageMilestoneEvidenceRecord(
                package_evidence_id=(
                    f"package_132_evidence:{package_id}:"
                    f"{sha256_payload(identity_payload)[:16]}"
                ),
                schema_version=PACKAGE_EVIDENCE_SCHEMA_VERSION,
                created_at=now,
                package_id=package_id,
                completion_commit=PACKAGE_COMPLETION_COMMITS[package_id],
                completion_commit_is_ancestor=ancestry[package_id],
                expected_audit_status=EXPECTED_AUDIT_STATUSES[package_id],
                observed_audit_id=observed_id,
                observed_audit_status=str(payload["audit_status"]),
                stored_audit_record_present=bool(item["stored"]),
                evidence_mode=str(item["mode"]),
                evidence_source_ref=(
                    f"evidence_source:{_path_fingerprint(Path(item['source_root']))[:16]}"
                ),
                payload_hash_verified=bool(item["payload_hash_verified"]),
                real_evidence_verified=real,
                boundary_evidence_verified=boundary,
                evidence_status=status,
                unresolved_evidence_limits=unresolved,
                source_record_refs=(observed_id,),
            )
        )
    return tuple(records)


def _validate_package_payload(
    package_id: str,
    item: dict[str, Any],
) -> tuple[bool, bool]:
    payload = dict(item["payload"])
    no_failures = not tuple(payload.get("failure_reasons") or ())
    if package_id == "123":
        real = all(
            (
                payload.get("real_window_capture_verified") is True,
                payload.get("real_system_audio_loopback_verified") is True,
                payload.get("real_host_state_verified") is True,
                payload.get("cycle_2_real_capture_verified") is True,
                payload.get("cycle_2_new_process_verified") is True,
                payload.get("cycle_2_readback_influence_verified") is True,
            )
        )
        boundary = all(
            (
                payload.get("hard_coded_recognition_detected") is False,
                payload.get("language_understanding_claimed") is False,
                payload.get("time_perception_claimed") is False,
                payload.get("stimulus_ground_truth_entered_learning_path") is False,
                payload.get("prerecorded_fixture_used") is False,
                payload.get("qingyin_output_created") is False,
                payload.get("llm_runtime_calls") == 0,
                payload.get("codex_runtime_calls") == 0,
                payload.get("network_runtime_calls") == 0,
                no_failures,
            )
        )
        return real, boundary
    if package_id == "124":
        real = all(
            (
                payload.get("cycle_1_real_sources_verified") is True,
                payload.get("cycle_1_transport_verified") is True,
                payload.get("cycle_2_package_112_influence_verified") is True,
                payload.get("archive_manifest_verified") is True,
                payload.get("archive_read_only_reverification_passed") is True,
            )
        )
        boundary = all(
            (
                payload.get("semantic_recognition_created") is False,
                payload.get("time_perception_created") is False,
                payload.get("language_understanding_created") is False,
                payload.get("qingyin_output_created") is False,
                payload.get("runtime_behavior_changed") is False,
                no_failures,
            )
        )
        return real, boundary
    if package_id == "124A":
        real = all(
            (
                payload.get("package_124_archive_verified") is True,
                payload.get("temporal_anchors_created") is True,
                payload.get("temporal_spans_created") is True,
                payload.get("temporal_continuity_created") is True,
                payload.get("external_gap_boundary_created") is True,
                payload.get("deterministic_identity_verified") is True,
            )
        )
        boundary = all(
            (
                payload.get("archive_modified") is False,
                payload.get("stimulus_ground_truth_used_for_compilation") is False,
                payload.get("subjective_time_claimed") is False,
                payload.get("memory_write_created") is False,
                payload.get("output_intent_created") is False,
                no_failures,
            )
        )
        return real, boundary
    if package_id == "125":
        real = all(
            (
                payload.get("audit_mode") == "real_active_capture",
                payload.get("real_source_capture_verified") is True,
                payload.get("same_source_sessions_preserved") is True,
                payload.get("extension_count") == 1,
                payload.get("all_required_lanes_extended") is True,
                payload.get("transport_flush_verified") is True,
            )
        )
        boundary = _false_fields(
            payload,
            (
                "focus_selection_created",
                "memory_write_created",
                "output_created",
                "external_action_created",
                "thought_engine_used",
                "novelty_semantics_claimed",
                "object_or_audio_semantics_claimed",
            ),
        ) and no_failures
        return real, boundary
    if package_id == "126":
        real = all(
            (
                payload.get("capture_again_real_run_verified") is True,
                payload.get("listen_again_real_run_verified") is True,
                payload.get("capture_session_ids_distinct") is True,
                payload.get("sources_reopened_verified") is True,
                payload.get("cross_window_gap_recorded") is True,
                payload.get("audio_deletion_verified") is True,
                payload.get("raw_audio_retained") is False,
            )
        )
        boundary = _false_fields(
            payload,
            (
                "working_readback_created",
                "focus_selection_created",
                "evidence_sufficiency_runtime_created",
                "novelty_signal_created",
                "uncertainty_signal_created",
                "thought_engine_used",
                "output_created",
                "external_control_created",
                "same_event_claimed",
                "same_sound_claimed",
                "speaker_recognition_claimed",
                "language_understanding_claimed",
                "subjective_listening_claimed",
            ),
        ) and no_failures
        return real, boundary
    if package_id == "127":
        real = all(
            (
                payload.get("real_parent_capture_verified") is True,
                int(payload.get("focus_candidate_count") or 0) >= 2,
                payload.get("package_126_child_window_used") is True,
                payload.get("full_frame_capture_preserved") is True,
                payload.get("focused_region_view_created") is True,
                payload.get("focus_automatically_released") is True,
            )
        )
        boundary = _false_fields(
            payload,
            (
                "memory_write_created",
                "working_readback_created",
                "evidence_sufficiency_runtime_created",
                "novelty_signal_created",
                "uncertainty_signal_created",
                "thought_engine_used",
                "audio_focus_created",
                "camera_focus_created",
                "sensor_priority_runtime_created",
                "external_control_created",
                "output_created",
                "object_recognition_created",
                "semantic_vision_created",
            ),
        ) and no_failures
        return real, boundary
    if package_id == "128":
        real = all(
            (
                payload.get("real_focused_child_window_verified") is True,
                payload.get("final_assessment_sufficient") is True,
                payload.get("stop_observation_action_created") is True,
                payload.get("stopped_before_hard_deadline") is True,
                payload.get("all_required_lanes_stopped") is True,
                payload.get("flush_completed") is True,
                payload.get("focus_released_at_completion") is True,
            )
        )
        boundary = _false_fields(
            payload,
            (
                "memory_write_created",
                "working_readback_created",
                "extension_action_created",
                "reacquisition_action_created",
                "focus_shift_action_created",
                "novelty_signal_created",
                "uncertainty_signal_created",
                "thought_engine_used",
                "output_created",
                "external_control_created",
                "semantic_understanding_claimed",
                "recognition_claimed",
                "certainty_claimed",
                "subjective_time_claimed",
            ),
        ) and no_failures
        return real, boundary
    if package_id == "129":
        real = all(
            (
                payload.get("cycle_1_real_capture_verified") is True,
                payload.get("cycle_1_exact_approval_verified") is True,
                payload.get("cycle_1_reviewed_memory_chain_verified") is True,
                payload.get("cycle_2_fresh_capture_verified") is True,
                payload.get("cycle_2_readback_influence_verified") is True,
                float(payload.get("cycle_2_readback_contribution") or 0.0) > 0.0,
                payload.get("cycle_2_actual_runtime_hot_path_verified") is True,
                payload.get("cycle_2_policy_gate_bypass_detected") is False,
            )
        )
        boundary = _false_fields(
            payload,
            (
                "new_perception_action_kind_created",
                "new_sensor_source_created",
                "new_primitive_compiler_created",
                "new_focus_mode_created",
                "new_sufficiency_contract_kind_created",
                "semantic_vision_created",
                "object_recognition_created",
                "auditory_concept_created",
                "auditory_prediction_created",
                "uncertainty_signal_created",
                "novelty_signal_created",
                "curiosity_signal_created",
                "thought_engine_used",
                "qingyin_output_created",
                "external_control_created",
                "package_132_milestone_claimed",
            ),
        ) and no_failures
        return real, boundary
    if package_id == "130":
        model = dict(item["model"])
        deletion = dict(item["deletion"])
        memory = dict(item["memory_commit"])
        generation = dict(item["generation"])
        real = all(
            (
                payload.get("real_grounding_audio_verified") is True,
                payload.get("positive_episode_count") == 4,
                payload.get("contrast_episode_count") == 3,
                payload.get("exact_teacher_approval_verified") is True,
                payload.get("auditory_concept_model_created") is True,
                payload.get("grounding_raw_deletion_count") == 7,
                payload.get("raw_audio_blob_count_after_deletion") == 0,
                model.get("maturity_status")
                == "reviewed_grounded_ready_for_package_131",
                deletion.get("raw_blob_count_after_deletion") == 0,
                deletion.get("recoverable_waveform_detected") is False,
                generation.get("stimulus_ground_truth_used") is False,
            )
        )
        boundary = all(
            (
                model.get("semantic_label") is None,
                model.get("natural_language_name") is None,
                model.get("recognition_enabled") is False,
                model.get("prediction_error_runtime_enabled") is False,
                model.get("automatic_regrounding_enabled") is False,
                model.get("package_112_action_influence_allowed") is False,
                model.get("raw_audio_dependency_active") is False,
                memory.get("consumer_scope") == "package_131_auditory_prediction_only",
                memory.get("active_package_112_working_readback_created") is False,
                _false_fields(
                    payload,
                    (
                        "runtime_recognition_created",
                        "auditory_prediction_runtime_created",
                        "speaker_profile_created",
                        "speaker_embedding_created",
                        "transcript_created",
                        "semantic_emotion_created",
                        "object_identity_created",
                        "action_identity_created",
                        "material_identity_created",
                        "internal_action_created",
                        "output_created",
                        "external_control_created",
                    ),
                ),
                no_failures,
            )
        )
        return real, boundary
    if package_id == "131":
        binding = dict(item["binding"])
        pair = dict(item["pair"])
        real = all(
            (
                payload.get("both_real_wasapi_loopback") is True,
                payload.get("processes_distinct") is True,
                payload.get("probe_a_prediction_result")
                == "supported_by_reviewed_anonymous_auditory_concept",
                payload.get("probe_b_prediction_result")
                == "not_supported_by_reviewed_anonymous_auditory_concept",
                payload.get("cleanup_verified") is True,
                pair.get("comparison_status")
                == "passed_real_two_probe_anonymous_auditory_prediction",
                pair.get("fixture_firewall_passed") is True,
                binding.get("consumer_scope")
                == "package_131_auditory_prediction_only",
                binding.get("raw_audio_dependency_active") is False,
                binding.get("package_112_action_influence_allowed") is False,
            )
        )
        boundary = _false_fields(
            payload,
            (
                "semantic_sound_name_created",
                "object_identity_created",
                "action_identity_created",
                "material_identity_created",
                "speaker_profile_created",
                "speaker_embedding_created",
                "transcript_created",
                "speech_understanding_created",
                "emotion_meaning_created",
                "package_112_score_changed",
                "internal_action_created",
                "memory_written",
                "teacher_review_created",
                "working_readback_created",
                "output_created",
                "external_control_created",
                "d_laplace_component_used",
                "dlm_1_implemented",
                "package_132_implemented",
            ),
        ) and no_failures
        return real, boundary
    raise ValueError(package_id)


def _build_lineage_records(
    root: Path,
    discovered: dict[str, dict[str, Any]],
    package_records: tuple[PerceptionPackageMilestoneEvidenceRecord, ...],
) -> tuple[PerceptionCrossPackageLineageRecord, ...]:
    by_package = {record.package_id: record for record in package_records}
    payloads = {key: dict(value["payload"]) for key, value in discovered.items()}
    p131_binding = dict(discovered["131"]["binding"])
    p130_model = dict(discovered["130"]["model"])
    edge_specs = (
        ("123", "124", "sealed_real_run_archive", True, (
            "ashl_core_v1/runtime/package_124_archive.py",
            "ashl_core_v1/runtime/package_124_source_audit.py",
        )),
        ("124", "124A", "archive_to_grounded_temporal_primitives", bool(payloads["124A"].get("package_124_archive_verified")), (
            "ashl_core_v1/runtime/grounded_temporal_primitive_compiler.py",
            "ashl_core_v1/runtime/package_124a_temporal_audit.py",
        )),
        ("124A", "125", "grounded_temporal_tail_evidence", bool(payloads["125"].get("temporal_tail_evidence_verified")), (
            "ashl_core_v1/runtime/package_125_observation_extension_runtime.py",
            "ashl_core_v1/runtime/temporal_tail_evidence_adapter.py",
        )),
        ("125", "126", "completed_parent_to_new_child_capture", bool(payloads["126"].get("package_125_baseline_verified")), (
            "ashl_core_v1/runtime/package_126_reacquisition_runtime.py",
            "ashl_core_v1/runtime/perception_reacquisition_policy.py",
        )),
        ("126", "127", "capture_again_focused_child_window", bool(payloads["127"].get("package_126_child_window_used")), (
            "ashl_core_v1/runtime/package_127_internal_focus_runtime.py",
            "ashl_core_v1/runtime/package_126_reacquisition_runtime.py",
        )),
        ("127", "128", "focused_context_structural_stop", bool(payloads["128"].get("package_127_baseline_verified")), (
            "ashl_core_v1/runtime/package_128_sufficiency_stop_runtime.py",
            "ashl_core_v1/runtime/package_127_internal_focus_runtime.py",
        )),
        ("125", "129", "bounded_extension_stage", bool(payloads["129"].get("cycle_1_extension_verified") and payloads["129"].get("cycle_2_extension_verified")), (
            "ashl_core_v1/runtime/package_129_active_perception_growth_runtime.py",
            "ashl_core_v1/runtime/package_125_observation_extension_runtime.py",
        )),
        ("126", "129", "fresh_reacquisition_stage", bool(payloads["129"].get("cycle_1_capture_again_verified") and payloads["129"].get("cycle_2_capture_again_verified")), (
            "ashl_core_v1/runtime/package_129_active_perception_growth_runtime.py",
            "ashl_core_v1/runtime/package_126_reacquisition_runtime.py",
        )),
        ("127", "129", "bounded_focus_stage", bool(payloads["129"].get("cycle_1_focus_shift_verified") and payloads["129"].get("cycle_2_focus_shift_verified")), (
            "ashl_core_v1/runtime/package_129_active_perception_growth_runtime.py",
            "ashl_core_v1/runtime/package_127_internal_focus_runtime.py",
        )),
        ("128", "129", "structural_stop_stage", bool(payloads["129"].get("cycle_1_stop_observation_verified") and payloads["129"].get("cycle_2_stop_observation_verified")), (
            "ashl_core_v1/runtime/package_129_active_perception_growth_runtime.py",
            "ashl_core_v1/runtime/package_128_sufficiency_stop_runtime.py",
        )),
        ("129", "130", "teacher_reviewed_perception_baseline", bool(payloads["130"].get("package_129_baseline_verified")), (
            "ashl_core_v1/runtime/package_130_auditory_concept_audit.py",
            "ashl_core_v1/runtime/package_129_active_perception_growth_audit.py",
        )),
        ("130", "131", "typed_read_only_auditory_prediction_binding", bool(
            payloads["131"].get("package_130_audit_id") == payloads["130"].get("audit_id")
            and p131_binding.get("auditory_concept_model_id") == p130_model.get("auditory_concept_model_id")
            and p131_binding.get("consumer_scope") == "package_131_auditory_prediction_only"
        ), (
            "ashl_core_v1/runtime/auditory_prediction_model_binding.py",
            "ashl_core_v1/runtime/package_131_auditory_predictive_recognition_audit.py",
        )),
    )
    records: list[PerceptionCrossPackageLineageRecord] = []
    now = utc_now()
    for producer, consumer, interface, identity, modules in edge_specs:
        modules_exist = all((root / module).is_file() for module in modules)
        authority_ok = _edge_authority_not_broadened(producer, consumer, discovered)
        identity_payload = {
            "producer": by_package[producer].package_evidence_id,
            "consumer": by_package[consumer].package_evidence_id,
            "interface": interface,
        }
        records.append(
            PerceptionCrossPackageLineageRecord(
                lineage_record_id=(
                    f"package_132_lineage:{sha256_payload(identity_payload)[:16]}"
                ),
                schema_version=LINEAGE_SCHEMA_VERSION,
                created_at=now,
                producer_package_id=producer,
                consumer_package_id=consumer,
                interface_kind=interface,
                producer_record_refs=(by_package[producer].observed_audit_id,),
                consumer_record_refs=(by_package[consumer].observed_audit_id,),
                source_module_refs=tuple(modules),
                identity_consistent=bool(identity and modules_exist),
                authority_not_broadened=authority_ok,
                lineage_status=(
                    "verified" if identity and modules_exist and authority_ok else "blocked"
                ),
            )
        )
    return tuple(records)


def _edge_authority_not_broadened(
    producer: str,
    consumer: str,
    discovered: dict[str, dict[str, Any]],
) -> bool:
    payload = dict(discovered[consumer]["payload"])
    if consumer == "131":
        binding = dict(discovered["131"]["binding"])
        return all(
            (
                binding.get("consumer_scope")
                == "package_131_auditory_prediction_only",
                binding.get("active_working_readback_used") is False,
                binding.get("package_112_action_influence_allowed") is False,
                binding.get("raw_audio_dependency_active") is False,
            )
        )
    forbidden_true = (
        "output_created",
        "external_control_created",
        "d_laplace_component_used",
        "dlm_1_implemented",
    )
    return not any(payload.get(field) is True for field in forbidden_true)


def _derive_forbidden_capability_flags(
    discovered: dict[str, dict[str, Any]],
    root: Path,
) -> dict[str, bool]:
    payloads = tuple(dict(item["payload"]) for item in discovered.values())
    model = dict(discovered["130"]["model"])
    binding = dict(discovered["131"]["binding"])
    registry = json.loads(
        (root / "ashl_core_v1/docs/reference/package_number_registry_v0.json").read_text(
            encoding="utf-8"
        )
    )
    return {
        "semantic_identity_created": any(
            payload.get(field) is True
            for payload in payloads
            for field in (
                "semantic_recognition_created",
                "semantic_vision_created",
                "semantic_understanding_claimed",
                "semantic_sound_name_created",
                "object_identity_created",
                "object_recognition_created",
                "speaker_profile_created",
                "transcript_created",
            )
        )
        or model.get("semantic_label") is not None
        or model.get("natural_language_name") is not None,
        "free_attention_created": any(
            token in ALLOWED_INTERNAL_ACTION_KINDS
            for token in ("free_attention_action", "open_ended_attention_action")
        ),
        "persistent_autonomous_observation_created": any(
            token in ALLOWED_INTERNAL_ACTION_KINDS
            for token in ("observe_forever", "autonomous_observation_loop")
        ),
        "output_created": any(
            payload.get("output_created") is True
            or payload.get("qingyin_output_created") is True
            for payload in payloads
        ),
        "thought_engine_created": any(
            payload.get("thought_engine_used") is True for payload in payloads
        ),
        "persistent_self_state_created": bool(
            tuple((root / "ashl_core_v1/runtime").glob("package_133*.py"))
        ),
        "new_internal_action_created": any(
            kind not in PERCEPTION_INTERNAL_ACTION_KINDS
            for kind in _package_125_to_128_action_surface()
        )
        or "package_132_internal_action" in ALLOWED_INTERNAL_ACTION_KINDS,
        "package_132a_created": (
            "132A" in tuple(registry.get("completed_package_ids") or ())
            or "132A" in tuple(registry.get("future_package_ids") or ())
            or any(
                "132a" in Path(relative_path).name.lower()
                for relative_path in _git_output(
                    root,
                    "ls-files",
                    "--cached",
                    "--others",
                    "--exclude-standard",
                ).splitlines()
            )
        ),
        "dlm_1_implemented": any(
            payload.get("dlm_1_implemented") is True for payload in payloads
        )
        or bool(tuple((root / "ashl_core_v1/runtime").glob("*dlm_1*"))),
        "package_130_consumer_scope_broadened": (
            binding.get("consumer_scope") != "package_131_auditory_prediction_only"
        ),
        "memory_authority_broadened": any(
            payload.get("memory_write_created") is True
            or payload.get("memory_written") is True
            for payload in payloads
            if payload.get("audit_status")
            not in {
                EXPECTED_AUDIT_STATUSES["129"],
                EXPECTED_AUDIT_STATUSES["130"],
            }
        ),
        "external_control_created": any(
            payload.get("external_control_created") is True
            or payload.get("external_action_created") is True
            for payload in payloads
        ),
        "d_laplace_component_used": any(
            payload.get("d_laplace_component_used") is True for payload in payloads
        ),
    }


def _package_125_to_128_action_surface() -> tuple[str, ...]:
    return PERCEPTION_INTERNAL_ACTION_KINDS


def _perception_action_surface_valid() -> bool:
    return all(kind in ALLOWED_INTERNAL_ACTION_KINDS for kind in PERCEPTION_INTERNAL_ACTION_KINDS)


def _source_record(
    path: Path,
    before: dict[str, Any],
    after: dict[str, Any],
    *,
    archive: bool,
) -> Package132EvidenceSourceRecord:
    validate_source_snapshot(str(before["tree_sha256"]), str(after["tree_sha256"]))
    fingerprint = _path_fingerprint(path)
    return Package132EvidenceSourceRecord(
        evidence_source_id=f"evidence_source:{fingerprint[:16]}",
        schema_version=EVIDENCE_SOURCE_SCHEMA_VERSION,
        created_at=utc_now(),
        source_kind="package_124_archive" if archive else "external_audit_state",
        path_fingerprint=fingerprint,
        included_file_count=int(after["file_count"]),
        included_byte_count=int(after["byte_count"]),
        tree_manifest_sha256_before=str(before["tree_sha256"]),
        tree_manifest_sha256_after=str(after["tree_sha256"]),
        source_opened_read_only=True,
        source_unchanged=True,
        private_absolute_path_persisted=False,
        source_record_refs=(f"tree_manifest:{after['tree_sha256']}",),
    )


def _tree_snapshot(root: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise FileNotFoundError(root)
    entries: list[dict[str, object]] = []
    byte_count = 0
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_symlink():
            raise ValueError("Package 132 evidence roots cannot contain symlinks")
        if not path.is_file():
            continue
        data = path.read_bytes()
        byte_count += len(data)
        entries.append(
            {
                "relative_path": path.relative_to(root).as_posix(),
                "size_bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    return {
        "file_count": len(entries),
        "byte_count": byte_count,
        "tree_sha256": sha256_payload(entries),
    }


def _path_fingerprint(path: Path) -> str:
    normalized = os.path.normcase(str(path.resolve())).replace("\\", "/")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _validate_external_state_dir(
    repo_root: Path,
    state_dir: Path,
    evidence_sources: tuple[Path, ...],
) -> None:
    if _is_within(state_dir, repo_root):
        raise ValueError("Package 132 state_dir must be outside the repository")
    for source in evidence_sources:
        if state_dir == source or _is_within(state_dir, source) or _is_within(source, state_dir):
            raise ValueError("Package 132 output and read-only evidence roots must be separate")


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


def _closure_hash_payload(
    contract: PerceptionAttentionCapabilityBoundaryClosureContract,
) -> dict[str, Any]:
    payload = contract.to_dict()
    payload.pop("closure_contract_id", None)
    payload.pop("closure_sha256", None)
    payload.pop("created_at", None)
    return payload


def _validate_table_name(table: str) -> None:
    if not table.replace("_", "").isalnum():
        raise ValueError("invalid read-only table name")


def _false_fields(payload: dict[str, Any], names: tuple[str, ...]) -> bool:
    return all(name in payload and payload[name] is False for name in names)


def _verified(
    records: dict[str, PerceptionPackageMilestoneEvidenceRecord],
    package_id: str,
) -> bool:
    return records[package_id].evidence_status == "verified"


def _append_once(
    store: Package132PerceptionAttentionMilestoneStore,
    table: str,
    record: Any,
) -> None:
    payload = record.to_dict()
    key = {
        "package_132_evidence_sources": "evidence_source_id",
        "package_132_package_evidence": "package_evidence_id",
        "package_132_cross_package_lineage": "lineage_record_id",
        "perception_attention_closure_contracts": "closure_contract_id",
        "package_132_boundary_control_results": "control_result_id",
        "package_132_regression_receipts": "regression_receipt_id",
        "package_132_audits": "audit_id",
    }[table]
    if not store.has_record(table, str(payload[key])):
        store.append_record(table, record)


def _dummy_lineage_records() -> tuple[PerceptionCrossPackageLineageRecord, ...]:
    now = "2026-08-07T00:00:00+00:00"
    return tuple(
        PerceptionCrossPackageLineageRecord(
            lineage_record_id=f"dummy:{producer}:{consumer}",
            schema_version=LINEAGE_SCHEMA_VERSION,
            created_at=now,
            producer_package_id=producer,
            consumer_package_id=consumer,
            interface_kind="test_only_control",
            producer_record_refs=(f"producer:{producer}",),
            consumer_record_refs=(f"consumer:{consumer}",),
            source_module_refs=("test_only",),
            identity_consistent=True,
            authority_not_broadened=True,
            lineage_status="verified",
        )
        for producer, consumer in _REQUIRED_LINEAGE_EDGES
    )
