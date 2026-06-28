"""Apply memory readback preview hints into bounded task Working Memory."""

from __future__ import annotations

import json
import os
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.memory.memory_application_readback_to_task_working_memory_preview import (
    list_memory_application_readback_previews,
    list_task_working_memory_readback_hints,
)
from ashl_core_v1.memory.task_working_memory_lifecycle import ActiveTaskFrame


MEMORY_READBACK_APPLICATION_ENV = "ASHL_CORE_V1_MEMORY_READBACK_APPLICATION_DIR"
DEFAULT_MEMORY_READBACK_APPLICATION_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "memory_readback_application"
)

LAST_MEMORY_READBACK_APPLICATION_FILE = "last_memory_readback_application.json"
MEMORY_READBACK_APPLICATION_HISTORY_FILE = "memory_readback_application_history.jsonl"


def apply_memory_readback_to_task_working_memory(
    *,
    preview_id: str,
    active_task_frame_id: str,
    active_task_frame: dict[str, Any] | ActiveTaskFrame | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    preview = _find_preview(preview_id, base_dir)
    if preview["target_active_task_frame_id"] != active_task_frame_id:
        raise LookupError(f"active task frame not found for preview: {active_task_frame_id}")
    frame = _resolve_active_task_frame(preview, active_task_frame)
    if frame.active_task_frame_id != active_task_frame_id:
        raise LookupError(f"active task frame not found: {active_task_frame_id}")
    hint_records = _hint_records_for_preview(preview_id, base_dir)
    if not hint_records:
        raise LookupError(f"readback hints not found for preview: {preview_id}")
    before_hints = tuple(frame.next_candidate_hints)
    incoming_hints = tuple(str(hint["hint_value"]) for hint in hint_records)
    after_hints = tuple(dict.fromkeys((*before_hints, *incoming_hints)))
    updated_frame = replace(
        frame,
        next_candidate_hints=after_hints,
        source_trace_refs=(
            *frame.source_trace_refs,
            f"readback_application:{preview_id}",
        ),
    )
    working_memory_updated = after_hints != before_hints
    application = {
        "readback_application_id": _application_id(preview_id),
        "source_readback_preview_id": preview_id,
        "source_memory_application_data_id": preview["source_memory_application_data_id"],
        "target_active_task_frame_id": active_task_frame_id,
        "task_id": preview["task_id"],
        "case_id": preview["case_id"],
        "applied_hint_refs": [hint["hint_id"] for hint in hint_records],
        "applied_hint_values": list(incoming_hints),
        "before_next_candidate_hints": list(before_hints),
        "after_next_candidate_hints": list(after_hints),
        "working_memory_updated": working_memory_updated,
        "application_scope": "bounded_task_working_memory_only",
        "source_trace_refs": [
            *list(preview.get("source_trace_refs") or []),
            *[hint["hint_id"] for hint in hint_records],
        ],
        "updated_active_task_frame": updated_frame.to_dict(),
        "action_selection": False,
        "action_execution": False,
        "core_memory_write": False,
        "long_term_memory_write": False,
        "archive_memory_write": False,
        "anchor_layer_write": False,
        "direct_memory_promotion": False,
        "scheduler_created": False,
        "created_at": _now(),
    }
    applied_hints = [
        {
            "applied_readback_working_memory_hint_id": _applied_hint_id(
                application["readback_application_id"],
                hint["hint_id"],
            ),
            "source_readback_preview_id": preview_id,
            "source_hint_id": hint["hint_id"],
            "active_task_frame_id": active_task_frame_id,
            "hint_value": hint["hint_value"],
            "inserted_into_working_memory": hint["hint_value"] not in before_hints,
            "application_scope": "bounded_task_working_memory_only",
        }
        for hint in hint_records
    ]
    payload = {
        "memory_readback_application_created": True,
        "task_working_memory_readback_application_record": application,
        "applied_readback_working_memory_hints": applied_hints,
    }
    return save_memory_readback_application(payload, base_dir)


def save_memory_readback_application(
    payload: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    application_dir = ensure_memory_readback_application_store(base_dir)
    (application_dir / LAST_MEMORY_READBACK_APPLICATION_FILE).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (application_dir / MEMORY_READBACK_APPLICATION_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(payload)


def load_last_memory_readback_application(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = (
        resolve_memory_readback_application_dir(base_dir)
        / LAST_MEMORY_READBACK_APPLICATION_FILE
    )
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_memory_readback_applications(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    path = (
        resolve_memory_readback_application_dir(base_dir)
        / MEMORY_READBACK_APPLICATION_HISTORY_FILE
    )
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def resolve_memory_readback_application_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(MEMORY_READBACK_APPLICATION_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_MEMORY_READBACK_APPLICATION_DIR


def ensure_memory_readback_application_store(
    base_dir: str | Path | None = None,
) -> Path:
    application_dir = resolve_memory_readback_application_dir(base_dir)
    application_dir.mkdir(parents=True, exist_ok=True)
    (application_dir / MEMORY_READBACK_APPLICATION_HISTORY_FILE).touch(exist_ok=True)
    return application_dir


def _find_preview(preview_id: str, base_dir: str | Path | None) -> dict[str, Any]:
    for preview in list_memory_application_readback_previews(base_dir):
        if preview.get("readback_preview_id") == preview_id:
            return preview
    raise LookupError(f"readback preview not found: {preview_id}")


def _hint_records_for_preview(
    preview_id: str,
    base_dir: str | Path | None,
) -> list[dict[str, Any]]:
    return [
        hint
        for hint in list_task_working_memory_readback_hints(base_dir)
        if hint.get("source_readback_preview_id") == preview_id
    ]


def _resolve_active_task_frame(
    preview: dict[str, Any],
    active_task_frame: dict[str, Any] | ActiveTaskFrame | None,
) -> ActiveTaskFrame:
    if isinstance(active_task_frame, ActiveTaskFrame):
        return active_task_frame
    if active_task_frame is not None:
        return ActiveTaskFrame.from_dict(dict(active_task_frame))
    return ActiveTaskFrame(
        active_task_frame_id=preview["target_active_task_frame_id"],
        memory_layer="working",
        task_id=preview["task_id"],
        task_status="active",
        current_goal=f"apply readback for {preview['case_id']}",
        approved_scope="memory_readback_application_only",
        current_tick=0,
        current_step="readback_application_start",
        recent_attempt_refs=(),
        last_outcome_ref=None,
        last_outcome_label=None,
        next_candidate_hints=(),
        blocked_reason=None,
        continue_allowed=True,
        stop_reason=None,
        source_trace_refs=("memory_readback_application:start",),
    )


def _application_id(preview_id: str) -> str:
    return f"memory_readback_application:{preview_id}:{_timestamp()}"


def _applied_hint_id(application_id: str, hint_id: str) -> str:
    return f"applied_readback_hint:{application_id}:{hint_id}"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
