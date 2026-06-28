"""Daily teacher notes linked to ASHL Core v1 fixed-cradle daily runs."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.daily_run import load_last_daily_run


DAILY_TEACHER_NOTE_ENV = "ASHL_CORE_V1_DAILY_TEACHER_NOTE_DIR"
DEFAULT_DAILY_TEACHER_NOTE_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "daily_teacher_notes"
)

DAILY_TEACHER_NOTES_FILE = "daily_teacher_notes.jsonl"
LAST_DAILY_TEACHER_NOTE_FILE = "last_daily_teacher_note.json"


def resolve_daily_teacher_note_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(DAILY_TEACHER_NOTE_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_DAILY_TEACHER_NOTE_DIR


def ensure_daily_teacher_note_store(base_dir: str | Path | None = None) -> Path:
    note_dir = resolve_daily_teacher_note_dir(base_dir)
    note_dir.mkdir(parents=True, exist_ok=True)
    (note_dir / DAILY_TEACHER_NOTES_FILE).touch(exist_ok=True)
    return note_dir


def build_daily_teacher_note(
    daily_run: dict[str, Any],
    note_text: str,
    attention_items: tuple[str, ...] = (),
    tomorrow_hint: str | None = None,
    first_output_followup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    daily_run_id = daily_run.get("daily_run_id")
    if not daily_run_id:
        raise ValueError("daily_run_id is required")
    session_id = daily_run.get("session_id")
    source_replay_ref = f"daily_run:{daily_run_id}:replay_summary"
    followup_id = None
    trace_refs = [f"daily_run:{daily_run_id}"]
    if session_id:
        trace_refs.append(f"session:{session_id}")
    trace_refs.append(source_replay_ref)
    if first_output_followup is not None:
        followup_id = first_output_followup.get("followup_id")
        if followup_id:
            trace_refs.append(f"first_output_followup:{followup_id}")
    return {
        "note_id": _new_note_id(str(daily_run_id)),
        "source_daily_run_id": daily_run_id,
        "source_session_id": session_id,
        "source_replay_ref": source_replay_ref,
        "source_first_output_followup_id": followup_id,
        "note_text": note_text,
        "attention_items": list(attention_items),
        "tomorrow_hint": tomorrow_hint,
        "created_at": _now(),
        "trace_refs": trace_refs,
    }


def write_daily_teacher_note(
    note_text: str,
    attention_items: tuple[str, ...] = (),
    tomorrow_hint: str | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.output.first_output_followup import load_last_first_output_followup

    daily_run = load_last_daily_run(base_dir)
    if daily_run is None:
        raise LookupError("last daily run not found")
    followup = load_last_first_output_followup(base_dir)
    note = build_daily_teacher_note(
        daily_run,
        note_text,
        attention_items,
        tomorrow_hint,
        followup,
    )
    return _save_daily_teacher_note(note, base_dir)


def load_last_daily_teacher_note(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = resolve_daily_teacher_note_dir(base_dir) / LAST_DAILY_TEACHER_NOTE_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_daily_teacher_notes(base_dir: str | Path | None = None) -> dict[str, Any]:
    path = ensure_daily_teacher_note_store(base_dir) / DAILY_TEACHER_NOTES_FILE
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "note_count": len(records),
        "notes": records,
    }


def _save_daily_teacher_note(
    note: dict[str, Any],
    base_dir: str | Path | None,
) -> dict[str, Any]:
    note_dir = ensure_daily_teacher_note_store(base_dir)
    (note_dir / LAST_DAILY_TEACHER_NOTE_FILE).write_text(
        json.dumps(note, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (note_dir / DAILY_TEACHER_NOTES_FILE).open("a", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(note, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(note)


def _new_note_id(daily_run_id: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"daily_teacher_note_{daily_run_id}_{stamp}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
