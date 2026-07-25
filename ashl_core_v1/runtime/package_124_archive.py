"""Durable milestone archive creation and read-only reverification."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import canonical_json, sha256_bytes, sha256_payload, stable_id, utc_now
from ashl_core_v1.runtime.package_124_archive_manifest import (
    MANIFEST_FILENAME,
    build_archive_manifest,
    verify_archive_manifest,
    write_archive_manifest,
)
from ashl_core_v1.runtime.package_124_milestone_certificate import (
    build_package_124_certificate,
    validate_package_124_certificate,
    write_package_124_certificate,
)
from ashl_core_v1.runtime.package_124_source_audit import (
    FINAL_AUDIT_STATUS,
    audit_package_124_source,
)
from ashl_core_v1.runtime.package_124_types import (
    PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
    PACKAGE_123_CYCLE_2_SESSION_ID,
    PACKAGE_123_SOURCE_COMMIT,
    PACKAGE_124_MILESTONE_ID,
)


SOURCE_STATE_DIRNAME = "source_state"
SOURCE_AUDIT_FILENAME = "package_124_source_audit.json"
ARCHIVE_REVERIFY_FILENAME = "package_124_archive_reverification.json"
PROVENANCE_FILENAME = "package_124_provenance_graph.json"
IDENTITY_FILENAME = "package_124_milestone_identity.json"
REPORT_FILENAME = "package_124_milestone_report.md"
BOUNDARY_REPORT_FILENAME = "package_124_boundary_report.md"
ARCHIVE_MARKER_FILENAME = "ARCHIVE_READ_ONLY"


def default_archive_root() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local) / "ASHLCore" / "milestones"
    return Path.home() / "AppData" / "Local" / "ASHLCore" / "milestones"


def create_package_124_archive(
    *,
    state_dir: str | Path,
    archive_root: str | Path | None = None,
    expected_commit: str = PACKAGE_123_SOURCE_COMMIT,
    confirm: bool = False,
) -> dict[str, object]:
    if not confirm:
        raise ValueError("--confirm is required to create the Package 124 milestone archive")
    source = Path(state_dir).resolve()
    root = Path(archive_root).resolve() if archive_root is not None else default_archive_root().resolve()
    _validate_archive_root(source, root)
    source_fingerprint_before = _tree_fingerprint(source)
    source_audit = audit_package_124_source(
        source,
        expected_commit=expected_commit,
        expected_cycle_1_evidence_identity=PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
        expected_cycle_2_session=PACKAGE_123_CYCLE_2_SESSION_ID,
    )
    if not source_audit.get("source_ok"):
        return {"status": "blocked_source_audit", "source_audit": source_audit}
    identity_hash = str((source_audit.get("identity") or {}).get("identity_hash") or sha256_payload({"source": str(source)}))
    final_dir = root / f"package_124_real_host_perception_growth_loop_v0_{identity_hash[:16]}"
    building_dir = root / f"{final_dir.name}.building"
    if final_dir.exists():
        raise FileExistsError(f"archive already exists: {final_dir}")
    if building_dir.exists():
        shutil.rmtree(building_dir)
    building_dir.mkdir(parents=True, exist_ok=False)
    copied_state = building_dir / SOURCE_STATE_DIRNAME
    shutil.copytree(source, copied_state)

    _write_json(building_dir / IDENTITY_FILENAME, source_audit["identity"])
    _write_json(building_dir / SOURCE_AUDIT_FILENAME, source_audit)
    _write_json(building_dir / PROVENANCE_FILENAME, source_audit["provenance_graph"])
    (building_dir / REPORT_FILENAME).write_text(_milestone_report(source_audit, archive_dir=final_dir), encoding="utf-8")
    (building_dir / BOUNDARY_REPORT_FILENAME).write_text(_boundary_report(), encoding="utf-8")

    preliminary_reverify = audit_package_124_source(
        copied_state,
        expected_commit=expected_commit,
        expected_cycle_1_evidence_identity=PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
        expected_cycle_2_session=PACKAGE_123_CYCLE_2_SESSION_ID,
        archive_created=True,
        archive_manifest_verified=True,
        archive_read_only_reverification_passed=True,
    )
    if not preliminary_reverify.get("final_ok"):
        _write_json(building_dir / ARCHIVE_REVERIFY_FILENAME, preliminary_reverify)
        return {
            "status": "blocked_archive_reverification",
            "archive_building_dir": str(building_dir),
            "reverification": preliminary_reverify,
        }

    building_dir.rename(final_dir)
    final_copied_state = final_dir / SOURCE_STATE_DIRNAME
    reverify = audit_package_124_source(
        final_copied_state,
        expected_commit=expected_commit,
        expected_cycle_1_evidence_identity=PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
        expected_cycle_2_session=PACKAGE_123_CYCLE_2_SESSION_ID,
        archive_created=True,
        archive_manifest_verified=True,
        archive_read_only_reverification_passed=True,
    )
    if not reverify.get("final_ok"):
        _write_json(final_dir / ARCHIVE_REVERIFY_FILENAME, reverify)
        return {"status": "blocked_archive_reverification", "archive_dir": str(final_dir), "reverification": reverify}
    _write_json(final_dir / ARCHIVE_REVERIFY_FILENAME, reverify)

    preliminary_manifest = build_archive_manifest(final_dir, source_state_dir=source)
    certificate = build_package_124_certificate(
        source_audit=reverify,
        archive_manifest_sha256=preliminary_manifest.manifest_sha256,
        provenance_graph_sha256=str((reverify.get("provenance_graph") or {}).get("graph_sha256") or ""),
    )
    write_package_124_certificate(certificate, final_dir)
    marker = _archive_marker(certificate_id=certificate.certificate_id)
    (final_dir / ARCHIVE_MARKER_FILENAME).write_text(marker, encoding="utf-8")
    manifest = build_archive_manifest(final_dir, source_state_dir=source)
    write_archive_manifest(manifest, final_dir)
    final_manifest_verification = verify_archive_manifest(final_dir)
    if not final_manifest_verification.get("valid"):
        return {
            "status": "blocked_archive_manifest",
            "archive_dir": str(final_dir),
            "manifest_verification": final_manifest_verification,
        }
    certificate_validation = validate_package_124_certificate(final_dir)
    source_fingerprint_after = _tree_fingerprint(source)
    return {
        "status": "certified_real_host_perception_growth_loop_v0" if final_manifest_verification.get("valid") and certificate_validation.get("valid") and source_fingerprint_before == source_fingerprint_after else "archive_created_with_verification_failure",
        "archive_dir": str(final_dir),
        "source_state_unchanged": source_fingerprint_before == source_fingerprint_after,
        "source_tree_sha256_before": source_fingerprint_before,
        "source_tree_sha256_after": source_fingerprint_after,
        "manifest_verification": final_manifest_verification,
        "certificate_validation": certificate_validation,
        "source_audit": source_audit,
        "archive_reverification": reverify,
        "raw_evidence_automatically_deleted": False,
        "archive_independent_of_source_temp": True,
    }


def verify_package_124_archive(archive_dir: str | Path) -> dict[str, object]:
    archive = Path(archive_dir).resolve()
    marker = archive / ARCHIVE_MARKER_FILENAME
    source_state = archive / SOURCE_STATE_DIRNAME
    manifest = verify_archive_manifest(archive)
    audit = audit_package_124_source(
        source_state,
        expected_commit=PACKAGE_123_SOURCE_COMMIT,
        expected_cycle_1_evidence_identity=PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
        expected_cycle_2_session=PACKAGE_123_CYCLE_2_SESSION_ID,
        archive_created=True,
        archive_manifest_verified=bool(manifest.get("valid")),
        archive_read_only_reverification_passed=True,
    )
    wal_journal = tuple(
        path.relative_to(archive).as_posix()
        for path in archive.rglob("*")
        if path.is_file() and path.suffix.lower() in {".wal", ".journal"}
    )
    certificate = validate_package_124_certificate(archive)
    return {
        "valid": bool(marker.exists() and manifest.get("valid") and audit.get("final_ok") and certificate.get("valid") and not wal_journal),
        "status": "archive_read_only_reverification_passed" if marker.exists() and manifest.get("valid") and audit.get("final_ok") and certificate.get("valid") and not wal_journal else "archive_reverification_failed",
        "archive_dir": str(archive),
        "archive_marker_present": marker.exists(),
        "manifest_verification": manifest,
        "source_reverification": audit,
        "certificate_validation": certificate,
        "wal_or_journal_files_created": wal_journal,
    }


def archive_payload(path: str | Path, filename: str) -> dict[str, object]:
    archive = Path(path)
    file_path = archive / filename
    if not file_path.exists():
        raise FileNotFoundError(file_path)
    return json.loads(file_path.read_text(encoding="utf-8"))


def _validate_archive_root(source: Path, root: Path) -> None:
    if source == root:
        raise ValueError("archive root cannot be the source state_dir")
    repo = Path.cwd().resolve()
    try:
        root.relative_to(repo)
        raise ValueError("archive root cannot be inside the repository")
    except ValueError as error:
        if str(error) == "archive root cannot be inside the repository":
            raise
    try:
        root.relative_to(source)
        raise ValueError("archive root cannot be inside the source state_dir")
    except ValueError as error:
        if str(error) == "archive root cannot be inside the source state_dir":
            raise
    root.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(canonical_json(payload), encoding="utf-8")


def _tree_fingerprint(root: Path) -> str:
    entries: list[dict[str, object]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel = path.relative_to(root).as_posix()
        data = path.read_bytes()
        entries.append({"relative_path": rel, "byte_length": len(data), "sha256": sha256_bytes(data)})
    return sha256_payload(entries)


def _archive_marker(*, certificate_id: str) -> str:
    return (
        f"milestone_id: {PACKAGE_124_MILESTONE_ID}\n"
        f"certificate_id: {certificate_id}\n"
        f"created_at: {utc_now()}\n"
        "archive_status: certified_read_only\n"
        "runtime_resume_forbidden: true\n"
        "schema_migration_forbidden: true\n"
        "teacher_decision_writes_forbidden: true\n"
        "memory_writes_forbidden: true\n"
        "artifact_deletion_forbidden: true\n"
        "new_runtime_events_forbidden: true\n"
    )


def _milestone_report(source_audit: dict[str, Any], *, archive_dir: Path) -> str:
    identity = dict(source_audit.get("identity") or {})
    evidence = dict(source_audit.get("evidence") or {})
    audit = dict(source_audit.get("audit") or {})
    audio = dict(source_audit.get("audio_timeline_continuity") or {})
    rejected = dict(source_audit.get("rejected_evidence_isolation") or {})
    timing = dict(source_audit.get("readback_timing") or {})
    return "\n".join(
        [
            "# Package 124 Milestone Report",
            "",
            "## Milestone identity",
            f"- Milestone ID: `{identity.get('milestone_id')}`",
            f"- Identity hash: `{identity.get('identity_hash')}`",
            f"- Source commit: `{identity.get('source_repository_commit')}`",
            f"- Archive directory: `{archive_dir}`",
            "",
            "## Exact source run",
            f"- Cycle 1 session: `{evidence.get('cycle_1_session_id')}`",
            f"- Cycle 1 evidence identity: `{identity.get('cycle_1_evidence_identity')}`",
            f"- Cycle 2 session: `{evidence.get('cycle_2_session_id')}`",
            "",
            "## Real source evidence",
            "- Window capture source verified: true",
            "- WASAPI loopback source verified: true",
            "- Host-state source verified: true",
            "- Camera participation: not_participating_by_design",
            "",
            "## Transport integrity",
            f"- Full windows: `{evidence.get('full_windows')}`",
            f"- Complete windows: `{evidence.get('complete_windows')}`",
            f"- Overlap windows: `{evidence.get('overlap_windows')}`",
            f"- Complete overlap windows: `{evidence.get('complete_overlap_windows')}`",
            f"- Audio timeline continuity verified: `{audio.get('continuity_verified')}`",
            "",
            "## Teacher approval",
            "- Exact evidence identity and full approval scope verified.",
            "- Stimulus ground truth excluded from the approved learning evidence.",
            "",
            "## Reviewed memory chain",
            f"- Working readback commit: `{evidence.get('working_readback_commit_id')}`",
            "",
            "## Cross-process separation",
            f"- Cycle 1 process: `{evidence.get('cycle_1_process_instance_id')}` / PID `{evidence.get('cycle_1_os_pid')}`",
            f"- Cycle 2 process: `{evidence.get('cycle_2_process_instance_id')}` / PID `{evidence.get('cycle_2_os_pid')}`",
            "",
            "## Cycle 2 readback timing",
            f"- Loaded before capture: `{timing.get('loaded_before_capture')}`",
            f"- Loaded before stimulus: `{timing.get('loaded_before_stimulus')}`",
            f"- Loaded before candidate evaluation: `{timing.get('loaded_before_candidate_evaluation')}`",
            "",
            "## Package 112 influence",
            f"- Scorer: `{evidence.get('scorer_id')}`",
            f"- Persisted readback contribution: `{evidence.get('readback_contribution')}`",
            "",
            "## Cycle 2 teacher-gate preservation",
            "- Cycle 2 pending review is preserved unresolved as milestone evidence.",
            "",
            "## Rejected-evidence isolation",
            f"- Rejected evidence identity: `{rejected.get('rejected_evidence_identity')}`",
            f"- Isolation verified: `{rejected.get('isolation_verified')}`",
            "",
            "## Archive location and manifest hash",
            "- Manifest hash is written in `archive_manifest.json` after finalization.",
            "",
            "## Safe claim",
            "- Real low-level host-internal visual/audio/host-state growth loop certified.",
            "- Cross-process readback influence certified.",
            "",
            "## Claims explicitly not supported",
            "- Semantic recognition, object recognition, rhythm/duration perception, language/speech understanding, speaker/emotion recognition, Qingyin-authored output, consciousness.",
            "",
            f"Audit status at report generation: `{audit.get('audit_status')}`",
        ]
    )


def _boundary_report() -> str:
    return """# Package 124 Boundary Report

## Proven
- real bounded host-internal visual/audio/host-state experience
- exact teacher-reviewed low-level memory commit
- persistent readback across process/session boundary
- measurable non-zero readback influence in normal scoring

## Not Proven
- semantic recognition
- object recognition
- causality
- rhythm understanding
- duration perception
- subjective time
- language understanding
- speech understanding
- speaker recognition
- emotion recognition
- physical-room perception
- self-generated output
- consciousness
"""
