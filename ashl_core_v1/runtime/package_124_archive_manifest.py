"""Archive manifest helpers for Package 124."""

from __future__ import annotations

from pathlib import Path

from ashl_core_v1.runtime.host_sensor_types import canonical_json, sha256_bytes, sha256_payload, stable_id, utc_now
from ashl_core_v1.runtime.package_124_types import (
    PACKAGE_124_ARCHIVE_MANIFEST_SCHEMA_VERSION,
    PACKAGE_124_MILESTONE_ID,
    Package124ArchiveFileEntry,
    Package124ArchiveManifest,
)


MANIFEST_FILENAME = "archive_manifest.json"


def build_archive_manifest(archive_dir: str | Path, *, source_state_dir: str | Path) -> Package124ArchiveManifest:
    root = Path(archive_dir)
    entries: list[Package124ArchiveFileEntry] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel == MANIFEST_FILENAME:
            continue
        data = path.read_bytes()
        entries.append(Package124ArchiveFileEntry(relative_path=rel, byte_length=len(data), sha256=sha256_bytes(data)))
    payload = {
        "milestone_id": PACKAGE_124_MILESTONE_ID,
        "archive_dir": str(root),
        "source_state_dir": str(source_state_dir),
        "entries": [entry.to_dict() for entry in entries],
    }
    manifest_sha = sha256_payload(payload)
    return Package124ArchiveManifest(
        manifest_id=stable_id("package_124_archive_manifest"),
        schema_version=PACKAGE_124_ARCHIVE_MANIFEST_SCHEMA_VERSION,
        created_at=utc_now(),
        milestone_id=PACKAGE_124_MILESTONE_ID,
        archive_dir=str(root),
        source_state_dir=str(source_state_dir),
        file_count=len(entries),
        total_byte_count=sum(entry.byte_length for entry in entries),
        entries=tuple(entries),
        manifest_sha256=manifest_sha,
    )


def write_archive_manifest(manifest: Package124ArchiveManifest, archive_dir: str | Path) -> Path:
    path = Path(archive_dir) / MANIFEST_FILENAME
    path.write_text(canonical_json(manifest.to_dict()), encoding="utf-8")
    return path


def verify_archive_manifest(archive_dir: str | Path) -> dict[str, object]:
    root = Path(archive_dir)
    manifest_path = root / MANIFEST_FILENAME
    if not manifest_path.exists():
        return {"valid": False, "status": "manifest_missing", "failure_reasons": ("manifest_missing",)}
    import json

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    reasons: list[str] = []
    entries = tuple(manifest.get("entries") or ())
    root_resolved = root.resolve()
    for entry in entries:
        rel = str(entry.get("relative_path") or "")
        rel_path = Path(rel)
        if rel_path.is_absolute() or ".." in rel_path.parts:
            reasons.append(f"path_escape:{rel}")
            continue
        path = (root / rel_path).resolve()
        try:
            path.relative_to(root_resolved)
        except ValueError:
            reasons.append(f"path_escape:{rel}")
            continue
        if not path.exists():
            reasons.append(f"missing_file:{rel}")
            continue
        data = path.read_bytes()
        expected_length = int(entry["byte_length"]) if entry.get("byte_length") is not None else -1
        if len(data) != expected_length:
            reasons.append(f"length_mismatch:{rel}")
        if sha256_bytes(data) != entry.get("sha256"):
            reasons.append(f"hash_mismatch:{rel}")
    expected_sha = sha256_payload(
        {
            "milestone_id": manifest.get("milestone_id"),
            "archive_dir": manifest.get("archive_dir"),
            "source_state_dir": manifest.get("source_state_dir"),
            "entries": entries,
        }
    )
    if expected_sha != manifest.get("manifest_sha256"):
        reasons.append("manifest_sha256_mismatch")
    return {
        "valid": not reasons,
        "status": "archive_manifest_verified" if not reasons else "archive_manifest_invalid",
        "failure_reasons": tuple(reasons),
        "manifest_sha256": manifest.get("manifest_sha256"),
        "file_count": len(entries),
        "total_byte_count": sum(int(entry.get("byte_length") or 0) for entry in entries),
    }
