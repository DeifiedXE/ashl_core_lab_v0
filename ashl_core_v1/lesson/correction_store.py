"""Teacher correction and revoke trail for ASHL Core v1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TEACHER_CORRECTION_ENV = "ASHL_CORE_V1_TEACHER_CORRECTION_DIR"
DEFAULT_TEACHER_CORRECTION_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "teacher_corrections"
)

TEACHER_CORRECTION_RECORDS_FILE = "teacher_correction_records.jsonl"
TEACHER_REVOKE_RECORDS_FILE = "teacher_revoke_records.jsonl"

ALLOWED_CORRECTION_TYPES = (
    "correct_note",
    "change_to_rejected",
    "change_to_deferred",
    "mark_wrong",
)

_REPLACEMENT_STATUS_BY_TYPE = {
    "correct_note": "note_corrected",
    "change_to_rejected": "rejected_requested",
    "change_to_deferred": "deferred_requested",
    "mark_wrong": "marked_wrong",
}


def resolve_teacher_correction_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(TEACHER_CORRECTION_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_TEACHER_CORRECTION_DIR


def ensure_teacher_correction_store(base_dir: str | Path | None = None) -> Path:
    correction_dir = resolve_teacher_correction_dir(base_dir)
    correction_dir.mkdir(parents=True, exist_ok=True)
    for file_name in (TEACHER_CORRECTION_RECORDS_FILE, TEACHER_REVOKE_RECORDS_FILE):
        (correction_dir / file_name).touch(exist_ok=True)
    return correction_dir


def create_teacher_correction(
    source_reviewed_digest_id: str,
    correction_type: str,
    teacher_note: str,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    if correction_type not in ALLOWED_CORRECTION_TYPES:
        raise ValueError(f"unknown correction type: {correction_type}")
    reviewed_digest = _find_reviewed_digest(source_reviewed_digest_id, base_dir)
    if reviewed_digest is None:
        raise LookupError(f"reviewed digest not found: {source_reviewed_digest_id}")

    record = {
        "correction_id": _next_record_id(
            "teacher_correction",
            source_reviewed_digest_id,
            list_teacher_corrections(base_dir),
        ),
        "source_reviewed_digest_id": source_reviewed_digest_id,
        "source_review_record_id": reviewed_digest.source_review_record_id,
        "correction_type": correction_type,
        "teacher_note": teacher_note,
        "replacement_status": _REPLACEMENT_STATUS_BY_TYPE[correction_type],
        "created_at": _now(),
    }
    _append_jsonl(_path(base_dir, TEACHER_CORRECTION_RECORDS_FILE), record)
    return record


def create_teacher_revoke(
    source_memory_learning_trace_id: str,
    revoke_reason: str,
    teacher_note: str,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    memory_trace = _find_memory_learning_trace(source_memory_learning_trace_id, base_dir)
    if memory_trace is None:
        raise LookupError(f"memory learning trace not found: {source_memory_learning_trace_id}")

    record = {
        "revoke_id": _next_record_id(
            "teacher_revoke",
            source_memory_learning_trace_id,
            list_teacher_revokes(base_dir),
        ),
        "source_reviewed_digest_id": memory_trace.source_reviewed_digest_id,
        "source_memory_learning_trace_id": source_memory_learning_trace_id,
        "revoke_reason": revoke_reason,
        "teacher_note": teacher_note,
        "created_at": _now(),
    }
    _append_jsonl(_path(base_dir, TEACHER_REVOKE_RECORDS_FILE), record)
    return record


def list_teacher_corrections(base_dir: str | Path | None = None) -> list[dict[str, Any]]:
    return _read_jsonl(_path(base_dir, TEACHER_CORRECTION_RECORDS_FILE))


def list_teacher_revokes(base_dir: str | Path | None = None) -> list[dict[str, Any]]:
    return _read_jsonl(_path(base_dir, TEACHER_REVOKE_RECORDS_FILE))


def build_teacher_correction_session_context(base_dir: str | Path | None = None) -> dict[str, Any]:
    from ashl_core_v1.runtime.session_replay import build_session_history_replay_summary

    return build_session_history_replay_summary(base_dir)


def _find_reviewed_digest(source_reviewed_digest_id: str, base_dir: str | Path | None):
    from ashl_core_v1.lesson.review_store import list_reviewed_learning_digests

    return next(
        (
            digest
            for digest in list_reviewed_learning_digests(base_dir)
            if digest.reviewed_digest_id == source_reviewed_digest_id
        ),
        None,
    )


def _find_memory_learning_trace(source_memory_learning_trace_id: str, base_dir: str | Path | None):
    from ashl_core_v1.memory.trace_store import find_memory_learning_trace

    return find_memory_learning_trace(source_memory_learning_trace_id, base_dir)


def _next_record_id(prefix: str, source_id: str, existing: list[dict[str, Any]]) -> str:
    safe_source = source_id.replace(":", "_")
    return f"{prefix}_{safe_source}_{len(existing) + 1:03d}"


def _path(base_dir: str | Path | None, file_name: str) -> Path:
    return ensure_teacher_correction_store(base_dir) / file_name


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
        file.write("\n")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
