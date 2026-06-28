"""Minimal backup and restore utilities for ASHL Core v1 cradle data."""

from __future__ import annotations

import json
import os
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BACKUP_DIR_ENV = "ASHL_CORE_V1_BACKUP_DIR"
DEFAULT_SOURCE_BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_BACKUP_DIR = DEFAULT_SOURCE_BASE_DIR / "backups"

BACKUP_MANIFEST_FILE = "backup_manifest.json"

INCLUDED_PATHS = (
    "data/session_persistence",
    "data/cradle_session",
    "data/daily_run",
    "data/review_queue",
    "data/memory_traces",
    "data/teacher_corrections",
    "data/fixed_runner",
    "data/cradle_runner",
    "docs/reports",
)


def resolve_backup_dir(backup_dir: str | Path | None = None) -> Path:
    if backup_dir is not None:
        return Path(backup_dir)
    env_value = os.environ.get(BACKUP_DIR_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_BACKUP_DIR


def create_v1_backup(
    source_base_dir: str | Path | None = None,
    backup_dir: str | Path | None = None,
) -> dict[str, Any]:
    source_dir = Path(source_base_dir) if source_base_dir is not None else DEFAULT_SOURCE_BASE_DIR
    target_dir = resolve_backup_dir(backup_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    backup_id = _new_backup_id()
    backup_path = target_dir / f"{backup_id}.zip"
    included_files = _collect_included_files(source_dir)
    manifest = {
        "backup_id": backup_id,
        "created_at": _now(),
        "source_base_dir": str(source_dir),
        "included_paths": list(INCLUDED_PATHS),
        "included_files": [path.as_posix() for path in included_files],
        "file_count": len(included_files),
        "format_version": "v0",
    }
    with zipfile.ZipFile(backup_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            BACKUP_MANIFEST_FILE,
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        )
        for relative_path in included_files:
            archive.write(source_dir / relative_path, relative_path.as_posix())
    return {
        "backup_id": backup_id,
        "backup_path": str(backup_path),
        "manifest": manifest,
    }


def list_v1_backups(backup_dir: str | Path | None = None) -> dict[str, Any]:
    target_dir = resolve_backup_dir(backup_dir)
    backups = []
    if target_dir.exists():
        for path in sorted(target_dir.glob("backup_*.zip")):
            try:
                manifest = _read_manifest(path)
            except (FileNotFoundError, KeyError, zipfile.BadZipFile, json.JSONDecodeError):
                continue
            backups.append(
                {
                    "backup_id": manifest["backup_id"],
                    "backup_path": str(path),
                    "created_at": manifest["created_at"],
                    "file_count": manifest["file_count"],
                }
            )
    return {
        "backup_count": len(backups),
        "backups": backups,
    }


def inspect_v1_backup(
    backup_id: str,
    backup_dir: str | Path | None = None,
) -> dict[str, Any]:
    backup_path = _find_backup_path(backup_id, backup_dir)
    if backup_path is None:
        raise LookupError(f"backup not found: {backup_id}")
    return {
        "backup_id": backup_id,
        "backup_path": str(backup_path),
        "manifest": _read_manifest(backup_path),
    }


def restore_v1_backup(
    backup_id: str,
    restore_base_dir: str | Path | None = None,
    backup_dir: str | Path | None = None,
) -> dict[str, Any]:
    backup_path = _find_backup_path(backup_id, backup_dir)
    if backup_path is None:
        raise LookupError(f"backup not found: {backup_id}")

    restore_dir = Path(restore_base_dir) if restore_base_dir is not None else DEFAULT_SOURCE_BASE_DIR
    if restore_dir.exists() and any(restore_dir.iterdir()):
        raise RuntimeError(f"restore_target_not_empty: {restore_dir}")
    restore_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(backup_path, "r") as archive:
        archive.extractall(restore_dir)
    manifest = _read_manifest(backup_path)
    return {
        "backup_id": backup_id,
        "restore_base_dir": str(restore_dir),
        "restored_file_count": manifest["file_count"],
        "manifest": manifest,
    }


def _collect_included_files(source_dir: Path) -> list[Path]:
    files: list[Path] = []
    for included_path in INCLUDED_PATHS:
        path = source_dir / included_path
        if path.is_file():
            files.append(path.relative_to(source_dir))
        elif path.is_dir():
            for file_path in sorted(item for item in path.rglob("*") if item.is_file()):
                files.append(file_path.relative_to(source_dir))
    return files


def _find_backup_path(backup_id: str, backup_dir: str | Path | None) -> Path | None:
    target_dir = resolve_backup_dir(backup_dir)
    path = target_dir / f"{backup_id}.zip"
    if path.exists():
        return path
    return None


def _read_manifest(backup_path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(backup_path, "r") as archive:
        return json.loads(archive.read(BACKUP_MANIFEST_FILE).decode("utf-8"))


def _new_backup_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"backup_{stamp}_{uuid.uuid4().hex[:8]}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
