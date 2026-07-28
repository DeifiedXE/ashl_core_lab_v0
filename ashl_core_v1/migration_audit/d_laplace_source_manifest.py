"""Deterministic D-Laplace source and exclusion manifests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from ashl_core_v1.migration_audit.d_laplace_qm0_types import (
    DLaplaceSourceArtifactRecord,
    DLaplaceSourceFileRecord,
    sha256_payload,
    stable_id,
    utc_now,
)
from ashl_core_v1.migration_audit.d_laplace_source_reader import (
    ReadOnlyDLaplaceSource,
    SourceEntry,
)


AUTHORITATIVE_DOCUMENT_NAMES = (
    "00_START_HERE.md",
    "01_D_LAPLACE_V1_FORMAL_DEFINITION.md",
    "04_FAILURES_AND_CORRECTIONS.md",
    "06_QINGYIN_MIGRATION_BLUEPRINT.md",
    "06A_QINGYIN_SELF_AUDIT_ENGINE_REQUIREMENTS.md",
    "09_FINAL_CLOSEOUT_DECLARATION.md",
    "11_PROJECT_HANDOFF_PROMPT.md",
)
GENERATED_COMPONENTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".hypothesis",
    "build",
    "dist",
    "site-packages",
}
ARCHIVED_OUTPUT_COMPONENTS = {
    "outputs",
    "output",
    "archived_outputs",
    "raw_outputs",
}
BINARY_SUFFIXES = {
    ".npy",
    ".npz",
    ".pickle",
    ".pkl",
    ".joblib",
    ".pt",
    ".pth",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".wav",
    ".mp3",
    ".mp4",
    ".avi",
    ".bin",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".pyc",
}
SEMANTIC_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".csv",
    ".ps1",
}


@dataclass(frozen=True)
class DLaplaceManifestSnapshot:
    source_kind: str
    original_archive_sha256: str | None
    source_path_fingerprint: str
    records: tuple[DLaplaceSourceFileRecord, ...]
    manifest_sha256: str
    authoritative_document_refs: tuple[str, ...]

    @property
    def included_records(self) -> tuple[DLaplaceSourceFileRecord, ...]:
        return tuple(
            record for record in self.records if record.included_in_semantic_scan
        )

    @property
    def excluded_records(self) -> tuple[DLaplaceSourceFileRecord, ...]:
        return tuple(
            record for record in self.records if not record.included_in_semantic_scan
        )


def _role_and_exclusion(
    entry: SourceEntry,
) -> tuple[str, bool, str | None]:
    path = PurePosixPath(entry.relative_path)
    parts = {part.casefold() for part in path.parts}
    suffix = path.suffix.casefold()
    basename = path.name
    if entry.is_symlink:
        return "generated_or_environment", False, "symlink_not_followed"
    generated = sorted(parts & GENERATED_COMPONENTS)
    if generated:
        return (
            "generated_or_environment",
            False,
            f"generated_or_environment:{generated[0]}",
        )
    archived = sorted(parts & ARCHIVED_OUTPUT_COMPONENTS)
    if archived:
        return "archived_output", False, f"archived_output:{archived[0]}"
    if suffix in BINARY_SUFFIXES:
        return "archived_output", False, f"binary_or_executable_data:{suffix}"
    if basename in AUTHORITATIVE_DOCUMENT_NAMES:
        return "authoritative_doc", True, None
    if "tests" in parts or basename.startswith("test_"):
        return "test", suffix in SEMANTIC_SUFFIXES, (
            None if suffix in SEMANTIC_SUFFIXES else "unsupported_test_file_kind"
        )
    if suffix == ".py" or suffix == ".ps1":
        return "implementation", True, None
    if suffix in {".toml", ".yaml", ".yml", ".json"} or basename in {
        "requirements.txt",
        "pyproject.toml",
        "poetry.lock",
    }:
        return "configuration", True, None
    if suffix in {".md", ".txt", ".csv"}:
        return "historical_doc", True, None
    return "unknown", False, "unsupported_semantic_file_kind"


def build_source_manifest(
    source: ReadOnlyDLaplaceSource,
) -> DLaplaceManifestSnapshot:
    records: list[DLaplaceSourceFileRecord] = []
    authoritative_refs: list[str] = []
    entries = source.entries()
    entry_hashes = source.entry_hashes(entries)
    for entry in entries:
        role, included, exclusion_reason = _role_and_exclusion(entry)
        content_hash = entry_hashes[entry.relative_path]
        record_id = stable_id(
            "d_laplace_source_file",
            {
                "relative_path": entry.relative_path,
                "size_bytes": entry.size_bytes,
                "sha256": content_hash,
            },
        )
        record = DLaplaceSourceFileRecord(
            source_file_record_id=record_id,
            relative_path=entry.relative_path,
            file_kind=PurePosixPath(entry.relative_path).suffix.casefold()
            or ("symlink" if entry.is_symlink else "no_extension"),
            size_bytes=entry.size_bytes,
            sha256=content_hash,
            included_in_semantic_scan=included,
            exclusion_reason=exclusion_reason,
            source_role=role,
            source_trace_refs=(),
        )
        records.append(record)
        if role == "authoritative_doc":
            authoritative_refs.append(entry.relative_path)
    ordered = tuple(sorted(records, key=lambda item: item.relative_path.casefold()))
    manifest_hash = sha256_payload(
        [
            {
                "relative_path": record.relative_path,
                "size_bytes": record.size_bytes,
                "sha256": record.sha256,
                "included_in_semantic_scan": record.included_in_semantic_scan,
                "exclusion_reason": record.exclusion_reason,
            }
            for record in ordered
        ]
    )
    return DLaplaceManifestSnapshot(
        source_kind=source.source_kind,
        original_archive_sha256=source.original_archive_sha256,
        source_path_fingerprint=source.path_fingerprint,
        records=ordered,
        manifest_sha256=manifest_hash,
        authoritative_document_refs=tuple(sorted(authoritative_refs)),
    )


def build_source_artifact_record(
    snapshot: DLaplaceManifestSnapshot,
    *,
    source_status: str,
) -> DLaplaceSourceArtifactRecord:
    payload = {
        "source_kind": snapshot.source_kind,
        "source_path_fingerprint": snapshot.source_path_fingerprint,
        "archive_sha256": snapshot.original_archive_sha256,
        "manifest_sha256": snapshot.manifest_sha256,
    }
    return DLaplaceSourceArtifactRecord(
        source_artifact_id=stable_id("d_laplace_source_artifact", payload),
        schema_version="ashl_d_laplace_source_artifact_v0",
        created_at=utc_now(),
        source_kind=snapshot.source_kind,
        source_path_fingerprint=snapshot.source_path_fingerprint,
        original_archive_sha256=snapshot.original_archive_sha256,
        included_file_count=len(snapshot.included_records),
        excluded_entry_count=len(snapshot.excluded_records),
        authoritative_document_refs=snapshot.authoritative_document_refs,
        source_status=source_status,
        source_trace_refs=(),
    )


def manifests_identical(
    before: DLaplaceManifestSnapshot,
    after: DLaplaceManifestSnapshot,
) -> bool:
    return (
        before.source_kind == after.source_kind
        and before.original_archive_sha256 == after.original_archive_sha256
        and before.manifest_sha256 == after.manifest_sha256
        and before.records == after.records
    )
