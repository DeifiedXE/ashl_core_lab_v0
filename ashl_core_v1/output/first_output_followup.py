"""Follow-up traces for promoted ASHL Core v1 first-output records."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.output.first_output_promotion import (
    list_first_output_records,
    load_last_first_output_record,
)


FIRST_OUTPUT_FOLLOWUP_ENV = "ASHL_CORE_V1_FIRST_OUTPUT_FOLLOWUP_DIR"
DEFAULT_FIRST_OUTPUT_FOLLOWUP_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "first_output_followups"
)

FIRST_OUTPUT_FOLLOWUP_RECORDS_FILE = "first_output_followup_records.jsonl"
LAST_FIRST_OUTPUT_FOLLOWUP_FILE = "last_first_output_followup.json"

ALLOWED_FOLLOWUP_KINDS = (
    "teacher_note",
    "teacher_question",
    "next_step_marker",
    "needs_observation",
    "hold_for_later",
)


def resolve_first_output_followup_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(FIRST_OUTPUT_FOLLOWUP_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_FIRST_OUTPUT_FOLLOWUP_DIR


def ensure_first_output_followup_store(base_dir: str | Path | None = None) -> Path:
    followup_dir = resolve_first_output_followup_dir(base_dir)
    followup_dir.mkdir(parents=True, exist_ok=True)
    (followup_dir / FIRST_OUTPUT_FOLLOWUP_RECORDS_FILE).touch(exist_ok=True)
    return followup_dir


def build_first_output_followup_record(
    first_output_record: dict[str, Any],
    followup_kind: str,
    teacher_note: str,
    next_step_hint: str | None = None,
) -> dict[str, Any]:
    if followup_kind not in ALLOWED_FOLLOWUP_KINDS:
        raise ValueError(f"unknown followup_kind: {followup_kind}")
    first_output_id = first_output_record.get("first_output_id")
    if not first_output_id:
        raise ValueError("first_output_id is required")
    return {
        "followup_id": _new_followup_id(first_output_id, followup_kind),
        "source_first_output_id": first_output_id,
        "source_candidate_id": first_output_record.get("source_candidate_id"),
        "source_review_id": first_output_record.get("source_review_id"),
        "followup_kind": followup_kind,
        "teacher_note": teacher_note,
        "next_step_hint": next_step_hint,
        "created_at": _now(),
        "trace_refs": list(first_output_record.get("trace_refs") or []),
    }


def follow_first_output(
    first_output_id: str,
    followup_kind: str,
    teacher_note: str,
    next_step_hint: str | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    first_output_record = _find_first_output_record(first_output_id, base_dir)
    if first_output_record is None:
        raise LookupError(f"first output record not found: {first_output_id}")
    followup = build_first_output_followup_record(
        first_output_record,
        followup_kind,
        teacher_note,
        next_step_hint,
    )
    return _save_first_output_followup(followup, base_dir)


def follow_last_first_output(
    followup_kind: str,
    teacher_note: str,
    next_step_hint: str | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    first_output_record = load_last_first_output_record(base_dir)
    if first_output_record is None:
        raise LookupError("last first output record not found")
    followup = build_first_output_followup_record(
        first_output_record,
        followup_kind,
        teacher_note,
        next_step_hint,
    )
    return _save_first_output_followup(followup, base_dir)


def load_last_first_output_followup(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = resolve_first_output_followup_dir(base_dir) / LAST_FIRST_OUTPUT_FOLLOWUP_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_first_output_followups(base_dir: str | Path | None = None) -> dict[str, Any]:
    path = ensure_first_output_followup_store(base_dir) / FIRST_OUTPUT_FOLLOWUP_RECORDS_FILE
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "followup_count": len(records),
        "followups": records,
    }


def _find_first_output_record(
    first_output_id: str,
    base_dir: str | Path | None,
) -> dict[str, Any] | None:
    return next(
        (
            record
            for record in list_first_output_records(base_dir)["first_output_records"]
            if record.get("first_output_id") == first_output_id
        ),
        None,
    )


def _save_first_output_followup(
    followup: dict[str, Any],
    base_dir: str | Path | None,
) -> dict[str, Any]:
    followup_dir = ensure_first_output_followup_store(base_dir)
    (followup_dir / LAST_FIRST_OUTPUT_FOLLOWUP_FILE).write_text(
        json.dumps(followup, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (followup_dir / FIRST_OUTPUT_FOLLOWUP_RECORDS_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(followup, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(followup)


def _new_followup_id(first_output_id: str, followup_kind: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"first_output_followup_{first_output_id}_{followup_kind}_{stamp}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
