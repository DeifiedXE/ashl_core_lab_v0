"""Long-horizon memory promotion queue for ASHL Core v1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MEMORY_PROMOTION_QUEUE_ENV = "ASHL_CORE_V1_MEMORY_PROMOTION_QUEUE_DIR"
DEFAULT_MEMORY_PROMOTION_QUEUE_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "memory_promotion_queue"
)

MEMORY_PROMOTION_CANDIDATES_FILE = "memory_promotion_candidates.jsonl"
LAST_MEMORY_PROMOTION_CANDIDATE_FILE = "last_memory_promotion_candidate.json"

ALLOWED_SOURCE_KINDS = (
    "daily_teacher_note",
    "first_output_followup",
    "daily_operation_audit",
    "state_continuity_stress",
    "long_term_gap_item",
    "manual_note",
)
ALLOWED_PRIORITIES = ("low", "normal", "high")
DEFAULT_STATUS = "queued"


def resolve_memory_promotion_queue_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(MEMORY_PROMOTION_QUEUE_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_MEMORY_PROMOTION_QUEUE_DIR


def ensure_memory_promotion_queue_store(base_dir: str | Path | None = None) -> Path:
    queue_dir = resolve_memory_promotion_queue_dir(base_dir)
    queue_dir.mkdir(parents=True, exist_ok=True)
    (queue_dir / MEMORY_PROMOTION_CANDIDATES_FILE).touch(exist_ok=True)
    return queue_dir


def build_memory_promotion_candidate(
    source_kind: str,
    source_id: str,
    source_summary: str,
    promotion_reason: str,
    priority: str = "normal",
    trace_refs: tuple[str, ...] = (),
) -> dict[str, Any]:
    if source_kind not in ALLOWED_SOURCE_KINDS:
        raise ValueError(f"unknown source_kind: {source_kind}")
    if priority not in ALLOWED_PRIORITIES:
        raise ValueError(f"unknown priority: {priority}")
    if not source_id:
        raise ValueError("source_id is required")
    if not source_summary:
        raise ValueError("source_summary is required")
    if not promotion_reason:
        raise ValueError("promotion_reason is required")
    return {
        "promotion_candidate_id": _new_promotion_candidate_id(source_kind, source_id),
        "source_kind": source_kind,
        "source_id": source_id,
        "source_summary": source_summary,
        "promotion_reason": promotion_reason,
        "priority": priority,
        "status": DEFAULT_STATUS,
        "created_at": _now(),
        "trace_refs": list(trace_refs),
    }


def enqueue_memory_promotion_candidate(
    candidate: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    _validate_candidate(candidate)
    queue_dir = ensure_memory_promotion_queue_store(base_dir)
    (queue_dir / LAST_MEMORY_PROMOTION_CANDIDATE_FILE).write_text(
        json.dumps(candidate, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (queue_dir / MEMORY_PROMOTION_CANDIDATES_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(candidate, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(candidate)


def enqueue_last_teacher_note(
    promotion_reason: str,
    priority: str = "normal",
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.teacher_console.daily_teacher_note import load_last_daily_teacher_note

    note = load_last_daily_teacher_note(base_dir)
    if note is None:
        raise LookupError("last daily teacher note not found")
    candidate = build_memory_promotion_candidate(
        "daily_teacher_note",
        note["note_id"],
        note.get("note_text") or "daily teacher note",
        promotion_reason,
        priority,
        tuple(note.get("trace_refs") or []),
    )
    return enqueue_memory_promotion_candidate(candidate, base_dir)


def enqueue_last_first_output_followup(
    promotion_reason: str,
    priority: str = "normal",
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.output.first_output_followup import load_last_first_output_followup

    followup = load_last_first_output_followup(base_dir)
    if followup is None:
        raise LookupError("last first-output follow-up not found")
    candidate = build_memory_promotion_candidate(
        "first_output_followup",
        followup["followup_id"],
        followup.get("teacher_note") or "first-output follow-up",
        promotion_reason,
        priority,
        tuple(followup.get("trace_refs") or []),
    )
    return enqueue_memory_promotion_candidate(candidate, base_dir)


def enqueue_manual_promotion_candidate(
    source_summary: str,
    promotion_reason: str,
    priority: str = "normal",
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    candidate = build_memory_promotion_candidate(
        "manual_note",
        _new_manual_source_id(),
        source_summary,
        promotion_reason,
        priority,
        (),
    )
    return enqueue_memory_promotion_candidate(candidate, base_dir)


def list_memory_promotion_queue(base_dir: str | Path | None = None) -> dict[str, Any]:
    path = ensure_memory_promotion_queue_store(base_dir) / MEMORY_PROMOTION_CANDIDATES_FILE
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "candidate_count": len(records),
        "promotion_candidates": records,
    }


def load_last_memory_promotion_candidate(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = resolve_memory_promotion_queue_dir(base_dir) / LAST_MEMORY_PROMOTION_CANDIDATE_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_candidate(candidate: dict[str, Any]) -> None:
    required = (
        "promotion_candidate_id",
        "source_kind",
        "source_id",
        "source_summary",
        "promotion_reason",
        "priority",
        "status",
        "created_at",
        "trace_refs",
    )
    missing = [field for field in required if field not in candidate]
    if missing:
        raise ValueError("missing promotion candidate fields: " + ", ".join(missing))
    if candidate["source_kind"] not in ALLOWED_SOURCE_KINDS:
        raise ValueError(f"unknown source_kind: {candidate['source_kind']}")
    if candidate["priority"] not in ALLOWED_PRIORITIES:
        raise ValueError(f"unknown priority: {candidate['priority']}")
    if candidate["status"] != DEFAULT_STATUS:
        raise ValueError(f"unsupported status: {candidate['status']}")
    if not isinstance(candidate.get("trace_refs"), list):
        raise ValueError("trace_refs must be a list")


def _new_promotion_candidate_id(source_kind: str, source_id: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    safe_source = source_id.replace(":", "_")
    return f"memory_promotion_candidate_{source_kind}_{safe_source}_{stamp}"


def _new_manual_source_id() -> str:
    return "manual_note_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
