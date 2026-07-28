"""Orchestrator for the D-Laplace Q-M0 read-only migration audit."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

from ashl_core_v1.migration_audit import (
    D_LAPLACE_QM0_AUDIT_STATUS,
    D_LAPLACE_QM0_BLOCKED_STATUS,
    QINGYIN_MIGRATION_STATUS,
)
from ashl_core_v1.migration_audit.d_laplace_ashl_substitution_map import (
    build_ashl_substitution_map,
)
from ashl_core_v1.migration_audit.d_laplace_authority_scan import (
    scan_state_authority,
)
from ashl_core_v1.migration_audit.d_laplace_portability_classifier import (
    QM1_ALLOWED_KINDS,
    build_qm1_candidate_allowlist,
    classify_portable_mechanisms,
)
from ashl_core_v1.migration_audit.d_laplace_primitive_authorization_scan import (
    audit_primitive_authorization,
)
from ashl_core_v1.migration_audit.d_laplace_qm0_store import (
    DLaplaceQM0Store,
)
from ashl_core_v1.migration_audit.d_laplace_qm0_types import (
    DLaplaceQM0ReadOnlyMigrationAudit,
    MigrationContaminationFinding,
    plain,
    stable_id,
    utc_now,
)
from ashl_core_v1.migration_audit.d_laplace_self_audit_gate_map import (
    build_self_audit_gate_map,
)
from ashl_core_v1.migration_audit.d_laplace_semantic_contamination_scan import (
    scan_semantic_contamination,
)
from ashl_core_v1.migration_audit.d_laplace_source_manifest import (
    AUTHORITATIVE_DOCUMENT_NAMES,
    DLaplaceManifestSnapshot,
    build_source_artifact_record,
    build_source_manifest,
    manifests_identical,
)
from ashl_core_v1.migration_audit.d_laplace_source_reader import (
    DirectoryDLaplaceSource,
    DLaplaceSourceError,
    ReadOnlyDLaplaceSource,
    open_d_laplace_source,
)
from ashl_core_v1.migration_audit.d_laplace_static_dependency_scan import (
    scan_static_dependencies,
)


ASHL_BASELINE_COMMIT = "abc23707e68dc94b84e120b26d76ae1985bfbde7"
SOURCE_STATUS = (
    "D-LAPLACE PROJECT v1 | SYNTHETIC PHASE: COMPLETED | "
    "REAL-WORLD R TRACK: NOT ENTERED | "
    "PRIMITIVE-AUTHORIZATION DEPTH: UNRESOLVED | "
    "OVERALL SCOPE: SYNTHETIC RESEARCH CLOSED"
)


class DLaplaceQM0BlockedError(RuntimeError):
    def __init__(self, reasons: tuple[str, ...]) -> None:
        super().__init__("; ".join(reasons))
        self.status = D_LAPLACE_QM0_BLOCKED_STATUS
        self.reasons = reasons


def _run_git(
    root: Path,
    args: list[str],
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    return subprocess.run(
        ["git", "-c", "core.fsmonitor=false", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=check,
        env=environment,
    )


def _verify_ashl_baseline(ashl_root: Path) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    try:
        _run_git(
            ashl_root,
            ["merge-base", "--is-ancestor", ASHL_BASELINE_COMMIT, "HEAD"],
        )
    except (OSError, subprocess.CalledProcessError):
        reasons.append("package_125_baseline_commit_not_in_HEAD_history")
    return not reasons, tuple(reasons)


def _ashl_changed_paths(ashl_root: Path) -> tuple[str, ...]:
    committed_or_worktree = _run_git(
        ashl_root,
        ["diff", "--name-only", ASHL_BASELINE_COMMIT, "--"],
    ).stdout.splitlines()
    untracked = _run_git(
        ashl_root,
        ["ls-files", "--others", "--exclude-standard"],
    ).stdout.splitlines()
    return tuple(sorted(set(committed_or_worktree) | set(untracked)))


def _validate_external_state_dir(
    state_dir: Path,
    ashl_root: Path,
    source: ReadOnlyDLaplaceSource,
) -> None:
    resolved = state_dir.resolve()
    if resolved == ashl_root or resolved.is_relative_to(ashl_root):
        raise ValueError("Q-M0 state_dir must remain outside the ASHL repository")
    if isinstance(source, DirectoryDLaplaceSource) and (
        resolved == source.source_path
        or resolved.is_relative_to(source.source_path)
    ):
        raise ValueError("Q-M0 state_dir must remain outside D-Laplace source")


def _source_git_state(
    source: ReadOnlyDLaplaceSource,
) -> tuple[str | None, str | None]:
    if not isinstance(source, DirectoryDLaplaceSource):
        return None, None
    if not (source.source_path / ".git").exists():
        return None, None
    head = _run_git(source.source_path, ["rev-parse", "HEAD"]).stdout.strip()
    status = _run_git(
        source.source_path,
        ["status", "--porcelain=v1", "--untracked-files=all"],
    ).stdout
    return head, status


def _load_authoritative_documents(
    source: ReadOnlyDLaplaceSource,
    snapshot: DLaplaceManifestSnapshot,
) -> dict[str, tuple[str, str]]:
    by_name: dict[str, list[str]] = {}
    for path in snapshot.authoritative_document_refs:
        by_name.setdefault(PurePosixPath(path).name, []).append(path)
    missing = [
        name for name in AUTHORITATIVE_DOCUMENT_NAMES if name not in by_name
    ]
    ambiguous = [
        name for name, paths in by_name.items() if len(paths) != 1
    ]
    if missing or ambiguous:
        reasons = tuple(
            [f"missing_authoritative_document:{name}" for name in missing]
            + [f"ambiguous_authoritative_document:{name}" for name in ambiguous]
        )
        raise DLaplaceQM0BlockedError(reasons)
    return {
        name: (by_name[name][0], source.read_text(by_name[name][0]))
        for name in AUTHORITATIVE_DOCUMENT_NAMES
    }


def _verify_source_status(
    documents: dict[str, tuple[str, str]],
) -> tuple[bool, dict[str, object], tuple[str, ...]]:
    combined = "\n".join(text for _, text in documents.values()).upper()
    required = {
        "synthetic_phase_completed": r"SYNTHETIC PHASE\s*:\s*COMPLETED",
        "real_world_r_track_not_entered": (
            r"REAL-WORLD R TRACK\s*:\s*NOT ENTERED"
        ),
        "primitive_authorization_unresolved": (
            r"PRIMITIVE[- ]AUTHORIZATION DEPTH\s*:\s*UNRESOLVED"
        ),
        "overall_scope_synthetic_closed": (
            r"OVERALL SCOPE\s*:\s*SYNTHETIC RESEARCH CLOSED"
        ),
    }
    matched = {
        key: bool(re.search(pattern, combined))
        for key, pattern in required.items()
    }
    conflicts = {
        "real_world_entered_claim": bool(
            re.search(r"REAL-WORLD R TRACK\s*:\s*ENTERED", combined)
        ),
        "primitive_authorization_resolved_claim": bool(
            re.search(
                r"PRIMITIVE[- ]AUTHORIZATION DEPTH\s*:\s*RESOLVED",
                combined,
            )
        ),
    }
    reasons = [
        f"source_status_missing:{key}"
        for key, value in matched.items()
        if not value
    ]
    reasons.extend(
        f"source_status_conflict:{key}"
        for key, value in conflicts.items()
        if value
    )
    status = {
        "source_status": SOURCE_STATUS,
        "synthetic_phase": "COMPLETED" if matched["synthetic_phase_completed"] else "UNVERIFIED",
        "real_world_r_track": (
            "NOT ENTERED"
            if matched["real_world_r_track_not_entered"]
            and not conflicts["real_world_entered_claim"]
            else "UNVERIFIED"
        ),
        "primitive_authorization_depth": (
            "unresolved"
            if matched["primitive_authorization_unresolved"]
            and not conflicts["primitive_authorization_resolved_claim"]
            else "unverified"
        ),
        "overall_scope": (
            "SYNTHETIC RESEARCH CLOSED"
            if matched["overall_scope_synthetic_closed"]
            else "UNVERIFIED"
        ),
    }
    return not reasons, status, tuple(reasons)


def _manifest_difference(
    before: DLaplaceManifestSnapshot,
    after: DLaplaceManifestSnapshot,
) -> dict[str, object]:
    before_by_path = {record.relative_path: record for record in before.records}
    after_by_path = {record.relative_path: record for record in after.records}
    added = tuple(sorted(set(after_by_path) - set(before_by_path)))
    deleted = tuple(sorted(set(before_by_path) - set(after_by_path)))
    changed = tuple(
        sorted(
            path
            for path in set(before_by_path) & set(after_by_path)
            if (
                before_by_path[path].size_bytes != after_by_path[path].size_bytes
                or before_by_path[path].sha256 != after_by_path[path].sha256
            )
        )
    )
    return {
        "source_modified": bool(changed),
        "source_file_added": bool(added),
        "source_file_deleted": bool(deleted),
        "source_hash_changed": (
            before.manifest_sha256 != after.manifest_sha256
            or before.original_archive_sha256 != after.original_archive_sha256
        ),
        "added_paths": list(added),
        "deleted_paths": list(deleted),
        "changed_paths": list(changed),
    }


def _deduplicate_findings(
    findings: tuple[MigrationContaminationFinding, ...],
) -> tuple[MigrationContaminationFinding, ...]:
    return tuple(
        sorted(
            {finding.finding_id: finding for finding in findings}.values(),
            key=lambda item: item.finding_id,
        )
    )


def _write_bundle(
    store: DLaplaceQM0Store,
    *,
    artifact: object,
    before: DLaplaceManifestSnapshot,
    dependency_result: object,
    findings: tuple[MigrationContaminationFinding, ...],
    primitives: tuple[object, ...],
    gates: tuple[object, ...],
    candidates: tuple[object, ...],
    substitutions: tuple[object, ...],
    allowlist: object,
    report: dict[str, object],
) -> None:
    store.write_json(
        "source_manifest.json",
        {
            "source_artifact": plain(artifact),
            "manifest_sha256": before.manifest_sha256,
            "files": [record.to_dict() for record in before.records],
        },
    )
    store.write_json(
        "exclusion_manifest.json",
        {
            "manifest_sha256": before.manifest_sha256,
            "excluded_entries": [
                record.to_dict() for record in before.excluded_records
            ],
        },
    )
    store.write_json(
        "dependency_graph.json",
        {
            "modules": [
                module.to_dict() for module in dependency_result.modules
            ],
            "edges": [edge.to_dict() for edge in dependency_result.edges],
        },
    )
    store.write_json(
        "contamination_findings.json",
        {"findings": [finding.to_dict() for finding in findings]},
    )
    store.write_json(
        "primitive_authorization_findings.json",
        {"findings": [record.to_dict() for record in primitives]},
    )
    store.write_json(
        "self_audit_gate_coverage.json",
        {"gates": [record.to_dict() for record in gates]},
    )
    store.write_json(
        "portability_map.json",
        {"candidates": [record.to_dict() for record in candidates]},
    )
    store.write_json(
        "ashl_substitution_map.json",
        {"candidates": [record.to_dict() for record in substitutions]},
    )
    store.write_json("qm1_candidate_allowlist.json", plain(allowlist))
    store.write_json("qm0_report.json", report)


def run_qm0_read_only_audit(
    *,
    ashl_root: str | Path,
    d_laplace_source: str | Path,
    state_dir: str | Path,
) -> dict[str, object]:
    ashl_path = Path(ashl_root).resolve()
    if not (ashl_path / ".git").exists():
        raise ValueError("ashl_root must be the ASHL Git repository")
    baseline_verified, baseline_reasons = _verify_ashl_baseline(ashl_path)
    try:
        source = open_d_laplace_source(d_laplace_source)
    except DLaplaceSourceError as error:
        raise DLaplaceQM0BlockedError((str(error),)) from error
    state_path = Path(state_dir).resolve()
    _validate_external_state_dir(state_path, ashl_path, source)
    source_git_head_before, source_git_status_before = _source_git_state(source)
    before = build_source_manifest(source)
    documents = _load_authoritative_documents(source, before)
    status_verified, source_status, status_reasons = _verify_source_status(
        documents
    )
    if not status_verified:
        raise DLaplaceQM0BlockedError(status_reasons)
    artifact = build_source_artifact_record(
        before,
        source_status=SOURCE_STATUS,
    )
    dependency_result = scan_static_dependencies(source, before.records)
    dependency_findings = dependency_result.findings
    authority_findings = scan_state_authority(
        source,
        dependency_result.modules,
    )
    semantic_findings = scan_semantic_contamination(
        source,
        dependency_result.modules,
    )
    findings = _deduplicate_findings(
        (*dependency_findings, *authority_findings, *semantic_findings)
    )
    primitives = audit_primitive_authorization(
        source,
        dependency_result.modules,
        authoritative_document_refs=before.authoritative_document_refs,
    )
    gates = build_self_audit_gate_map(
        file_records=before.records,
        modules=dependency_result.modules,
        authoritative_document_refs=before.authoritative_document_refs,
        source=source,
    )
    migration_docs = tuple(
        path
        for path in before.authoritative_document_refs
        if PurePosixPath(path).name
        in {
            "06_QINGYIN_MIGRATION_BLUEPRINT.md",
            "06A_QINGYIN_SELF_AUDIT_ENGINE_REQUIREMENTS.md",
        }
    )
    candidates = classify_portable_mechanisms(
        dependency_result.modules,
        findings,
        migration_document_refs=migration_docs,
    )
    substitutions = build_ashl_substitution_map(candidates)
    allowlist = build_qm1_candidate_allowlist(candidates)
    after = build_source_manifest(source)
    source_git_head_after, source_git_status_after = _source_git_state(source)
    difference = _manifest_difference(before, after)
    source_git_unchanged = (
        source_git_head_before == source_git_head_after
        and source_git_status_before == source_git_status_after
    )
    source_unchanged = (
        manifests_identical(before, after)
        and not any(
            bool(difference[key])
            for key in (
                "source_modified",
                "source_file_added",
                "source_file_deleted",
                "source_hash_changed",
            )
        )
        and source_git_unchanged
    )
    changed_paths = _ashl_changed_paths(ashl_path)
    runtime_changed_paths = tuple(
        path
        for path in changed_paths
        if path.replace("\\", "/").startswith("ashl_core_v1/runtime/")
    )
    package_125_changed = any(
        "package_125" in path.casefold()
        or "observation_extension" in path.casefold()
        or "bounded_capture_deadline" in path.casefold()
        for path in runtime_changed_paths
    )
    package_126_implemented = any(
        path.replace("\\", "/").startswith("ashl_core_v1/runtime/")
        and "126" in path
        for path in changed_paths
    )
    candidate_by_id = {
        candidate.migration_candidate_id: candidate for candidate in candidates
    }
    invalid_allowlist = tuple(
        ref
        for ref in allowlist.mechanism_candidate_refs
        if ref not in candidate_by_id
        or candidate_by_id[ref].mechanism_kind not in QM1_ALLOWED_KINDS
    )
    failures = list(baseline_reasons)
    if not source_unchanged:
        failures.append("d_laplace_source_changed_during_audit")
    if not dependency_result.modules:
        failures.append("module_inventory_missing")
    if not findings:
        failures.append("contamination_and_authority_findings_missing")
    if not primitives:
        failures.append("primitive_authorization_findings_missing")
    if len(gates) != 12:
        failures.append("self_audit_gate_count_not_twelve")
    if any(
        gate.qingyin_integration_status != "not_integrated_qm0_read_only"
        for gate in gates
    ):
        failures.append("self_audit_gate_falsely_integrated")
    if not candidates:
        failures.append("portability_map_missing")
    if not substitutions:
        failures.append("ashl_substitution_map_missing")
    if invalid_allowlist:
        failures.append("qm1_allowlist_contains_forbidden_mechanism")
    if runtime_changed_paths:
        failures.append("ashl_runtime_modified")
    if package_125_changed:
        failures.append("package_125_behavior_changed")
    if package_126_implemented:
        failures.append("package_126_implemented")
    created_at = utc_now()
    audit_status = (
        D_LAPLACE_QM0_AUDIT_STATUS
        if not failures
        else "failed_d_laplace_qm0_read_only_migration_audit_v0"
    )
    audit = DLaplaceQM0ReadOnlyMigrationAudit(
        audit_id=stable_id(
            "d_laplace_qm0_read_only_migration_audit",
            {
                "created_at": created_at,
                "manifest": before.manifest_sha256,
                "status": audit_status,
            },
        ),
        schema_version="ashl_d_laplace_qm0_read_only_migration_audit_v0",
        created_at=created_at,
        ashl_baseline_commit=ASHL_BASELINE_COMMIT,
        package_125_baseline_verified=baseline_verified,
        source_artifact_id=artifact.source_artifact_id,
        source_kind=source.source_kind,
        source_status_verified=status_verified,
        synthetic_phase_completed=True,
        real_world_r_track_entered=False,
        primitive_authorization_depth="unresolved",
        source_manifest_before_hash=before.manifest_sha256,
        source_manifest_after_hash=after.manifest_sha256,
        source_unchanged=source_unchanged,
        dynamic_import_used=False,
        d_laplace_code_executed=False,
        d_laplace_experiment_started=False,
        module_inventory_count=len(dependency_result.modules),
        dependency_edge_count=len(dependency_result.edges),
        contamination_finding_count=len(findings),
        blocking_direct_migration_finding_count=sum(
            finding.severity == "blocking_for_direct_migration"
            for finding in findings
        ),
        blocking_qm1_finding_count=sum(
            finding.severity == "blocking_for_qm1" for finding in findings
        ),
        portable_candidate_count=sum(
            candidate.portability_status == "portable_mechanism_candidate"
            for candidate in candidates
        ),
        extraction_required_count=sum(
            candidate.extraction_required for candidate in candidates
        ),
        forbidden_direct_migration_count=sum(
            candidate.portability_status == "forbidden_direct_migration"
            for candidate in candidates
        ),
        unresolved_candidate_count=sum(
            candidate.portability_status == "unresolved"
            for candidate in candidates
        ),
        self_audit_gate_count=len(gates),
        self_audit_gate_integrated_count=0,
        self_audit_gate_incomplete_count=len(gates),
        qm1_allowlist_created=True,
        qm1_execution_authorized=False,
        ashl_runtime_modified=bool(runtime_changed_paths),
        qingyin_behavior_modified=False,
        organ_created=False,
        organ_migrated=False,
        cost_runtime_added=False,
        lifecycle_runtime_added=False,
        action_bid_runtime_added=False,
        memory_write_created=False,
        output_created=False,
        package_125_behavior_changed=package_125_changed,
        package_126_implemented=package_126_implemented,
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        qm0_audit_status=audit_status,
        qingyin_migration_status=QINGYIN_MIGRATION_STATUS,
        failure_reasons=tuple(failures),
        source_trace_refs=(
            artifact.source_artifact_id,
            allowlist.allowlist_id,
        ),
    )
    implementation_count = sum(
        module.evidence_status == "source_code_ast_parsed"
        and "/tests/" not in f"/{module.relative_path.casefold()}/"
        for module in dependency_result.modules
    )
    report = {
        "message": [
            "Q-M0 read-only audit passed."
            if audit_status == D_LAPLACE_QM0_AUDIT_STATUS
            else "Q-M0 read-only audit failed.",
            "Qingyin migration remains incomplete.",
            "No D-Laplace runtime component was imported.",
        ],
        "source_status": source_status,
        "source_artifact": artifact.to_dict(),
        "source_integrity": {
            **difference,
            "source_manifest_before": before.manifest_sha256,
            "source_manifest_after": after.manifest_sha256,
            "source_unchanged": source_unchanged,
            "source_git_unchanged": source_git_unchanged,
        },
        "static_audit_summary": {
            "implementation_modules_inventoried": implementation_count,
            "module_inventory_count": len(dependency_result.modules),
            "dependency_edges": len(dependency_result.edges),
            "import_time_side_effect_findings": sum(
                finding.category == "import_time_side_effect"
                for finding in findings
            ),
            "synthetic_semantics_findings": sum(
                finding.category
                in {
                    "synthetic_world_semantics",
                    "synthetic_task_score_semantics",
                }
                for finding in findings
            ),
            "teacher_rule_leakage_findings": sum(
                finding.category == "teacher_rule_leakage"
                for finding in findings
            ),
            "analysis_tag_reverse_flow_findings": sum(
                finding.category == "human_analysis_tag_runtime_leakage"
                and finding.severity != "informational"
                for finding in findings
            ),
            "reset_fork_overwrite_findings": sum(
                finding.category
                in {
                    "reset_authority",
                    "fork_authority",
                    "history_overwrite_authority",
                }
                for finding in findings
            ),
        },
        "primitive_authorization_summary": {
            "record_count": len(primitives),
            "bounded_low_level": sum(
                item.authorization_depth_status == "bounded_low_level_primitive"
                for item in primitives
            ),
            "suspicious_high_level": sum(
                item.authorization_depth_status
                == "suspicious_high_level_authorization"
                for item in primitives
            ),
            "direct_answer_templates": sum(
                item.authorization_depth_status == "direct_answer_template"
                for item in primitives
            ),
            "unresolved": sum(
                item.authorization_depth_status == "unresolved"
                for item in primitives
            ),
            "not_run": sum(
                item.authorization_depth_status == "not_run"
                for item in primitives
            ),
            "novelty_claim": (
                "downgraded_due_to_unresolved_primitive_authorization"
            ),
        },
        "self_audit_summary": {
            "gate_count": len(gates),
            "source_evidence_present": sum(
                gate.source_coverage_status == "source_evidence_present"
                for gate in gates
            ),
            "partial_source_evidence": sum(
                gate.source_coverage_status == "partial_source_evidence"
                for gate in gates
            ),
            "source_evidence_absent": sum(
                gate.source_coverage_status == "source_evidence_absent"
                for gate in gates
            ),
            "unresolved": sum(
                gate.source_coverage_status == "unresolved" for gate in gates
            ),
            "integrated_into_qingyin": 0,
        },
        "portability_summary": {
            "portable_mechanism_candidates": audit.portable_candidate_count,
            "semantic_or_authority_extraction_required": (
                audit.extraction_required_count
            ),
            "documentation_only_candidates": sum(
                candidate.portability_status == "documentation_only_candidate"
                for candidate in candidates
            ),
            "forbidden_direct_migrations": (
                audit.forbidden_direct_migration_count
            ),
            "unresolved_candidates": audit.unresolved_candidate_count,
        },
        "qm1_candidate_allowlist": allowlist.to_dict(),
        "ashl_substitution_summary": {
            status: sum(
                record.substitution_status == status for record in substitutions
            )
            for status in (
                "full_substitution_candidate",
                "partial_substitution_candidate",
                "supporting_mechanism_only",
                "never_substitute",
                "unresolved",
            )
        },
        "boundaries": {
            "d_laplace_code_imported": False,
            "d_laplace_code_executed": False,
            "d_laplace_experiment_started": False,
            "organ_created": False,
            "organ_migrated": False,
            "ashl_runtime_modified": bool(runtime_changed_paths),
            "qingyin_behavior_modified": False,
            "package_125_behavior_changed": package_125_changed,
            "package_126_implemented": package_126_implemented,
            "memory_write": False,
            "output": False,
            "llm_runtime_calls": 0,
            "codex_runtime_calls": 0,
            "network_runtime_calls": 0,
        },
        "audit": audit.to_dict(),
    }
    store = DLaplaceQM0Store(state_path)
    store.append("source_artifact", artifact.source_artifact_id, artifact)
    store.append_many(
        "source_file",
        [
            (record.source_file_record_id, record)
            for record in before.records
        ],
    )
    store.append_many(
        "module_inventory",
        [(record.module_record_id, record) for record in dependency_result.modules],
    )
    store.append_many(
        "contamination_finding",
        [(record.finding_id, record) for record in findings],
    )
    store.append_many(
        "primitive_authorization_finding",
        [(record.primitive_finding_id, record) for record in primitives],
    )
    store.append_many(
        "self_audit_gate",
        [(record.gate_record_id, record) for record in gates],
    )
    store.append_many(
        "migration_candidate",
        [(record.migration_candidate_id, record) for record in candidates],
    )
    store.append_many(
        "ashl_substitution_candidate",
        [
            (record.substitution_candidate_id, record)
            for record in substitutions
        ],
    )
    store.append("qm1_candidate_allowlist", allowlist.allowlist_id, allowlist)
    store.append("qm0_audit", audit.audit_id, audit)
    _write_bundle(
        store,
        artifact=artifact,
        before=before,
        dependency_result=dependency_result,
        findings=findings,
        primitives=primitives,
        gates=gates,
        candidates=candidates,
        substitutions=substitutions,
        allowlist=allowlist,
        report=report,
    )
    return report


def verify_stored_source_unchanged(
    *,
    state_dir: str | Path,
    d_laplace_source: str | Path,
) -> dict[str, object]:
    store = DLaplaceQM0Store(state_dir)
    stored = store.read_json("source_manifest.json")
    if not isinstance(stored, dict):
        raise ValueError("stored source manifest is invalid")
    source = open_d_laplace_source(d_laplace_source)
    current = build_source_manifest(source)
    stored_files = {
        row["relative_path"]: (row["size_bytes"], row["sha256"])
        for row in stored.get("files", [])
    }
    current_files = {
        row.relative_path: (row.size_bytes, row.sha256)
        for row in current.records
    }
    added = sorted(set(current_files) - set(stored_files))
    deleted = sorted(set(stored_files) - set(current_files))
    changed = sorted(
        path
        for path in set(stored_files) & set(current_files)
        if stored_files[path] != current_files[path]
    )
    artifact = stored.get("source_artifact", {})
    archive_unchanged = (
        artifact.get("original_archive_sha256")
        == current.original_archive_sha256
    )
    manifest_unchanged = (
        stored.get("manifest_sha256") == current.manifest_sha256
    )
    unchanged = (
        archive_unchanged
        and manifest_unchanged
        and not added
        and not deleted
        and not changed
    )
    return {
        "status": (
            "verified_d_laplace_source_unchanged"
            if unchanged
            else "failed_d_laplace_source_integrity_verification"
        ),
        "source_unchanged": unchanged,
        "source_modified": bool(changed),
        "source_file_added": bool(added),
        "source_file_deleted": bool(deleted),
        "source_hash_changed": not manifest_unchanged or not archive_unchanged,
        "added_paths": added,
        "deleted_paths": deleted,
        "changed_paths": changed,
    }
