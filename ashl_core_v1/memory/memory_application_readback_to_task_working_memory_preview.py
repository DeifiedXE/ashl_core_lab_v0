"""Preview MemoryApplicationData readback as task Working Memory hints."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.memory.reviewed_learning_to_memory_trace import (
    list_memory_application_data_records,
)
from ashl_core_v1.memory.task_working_memory_lifecycle import create_active_task_frame


MEMORY_APPLICATION_READBACK_PREVIEW_ENV = (
    "ASHL_CORE_V1_MEMORY_APPLICATION_READBACK_PREVIEW_DIR"
)
DEFAULT_MEMORY_APPLICATION_READBACK_PREVIEW_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "memory_application_readback_preview"
)

MEMORY_READBACK_PREVIEWS_FILE = "memory_application_readback_previews.jsonl"
TASK_WORKING_MEMORY_READBACK_HINTS_FILE = "task_working_memory_readback_hints.jsonl"


def build_memory_application_readback_preview(
    *,
    memory_application_data_id: str,
    case_id: str,
    active_task_frame: dict[str, Any] | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    memory_data = _find_memory_application_data(memory_application_data_id, base_dir)
    frame = active_task_frame or create_active_task_frame(
        current_goal=f"preview memory readback for {case_id}",
        approved_scope="memory_readback_preview_only",
        task_id=f"preview_task:{case_id}",
        current_step="preview_start",
        source_trace_refs=("memory_readback_preview:start",),
    ).to_dict()
    hints = _hints_for_memory_data(memory_data)
    preview = {
        "readback_preview_id": _preview_id(memory_application_data_id),
        "source_memory_application_data_id": memory_application_data_id,
        "target_active_task_frame_id": frame["active_task_frame_id"],
        "task_id": frame["task_id"],
        "case_id": case_id,
        "readback_scope": "same_session_working_memory_preview",
        "readback_summary": _readback_summary(memory_data, hints),
        "suggested_working_memory_hints": list(hints),
        "source_trace_refs": _source_trace_refs(memory_data),
        "preview_only": True,
        "applied_to_working_memory": False,
        "runner_behavior_changed": False,
        "action_selection": False,
        "memory_write": False,
        "direct_memory_promotion": False,
        "scheduler_created": False,
    }
    hint_records = [
        {
            "hint_id": _hint_id(preview["readback_preview_id"], hint),
            "source_readback_preview_id": preview["readback_preview_id"],
            "active_task_frame_id": frame["active_task_frame_id"],
            "hint_kind": _hint_kind(hint),
            "hint_value": hint,
            "applied_to_working_memory": False,
            "preview_only": True,
        }
        for hint in hints
    ]
    return {
        "memory_application_readback_preview_created": True,
        "memory_application_readback_preview": preview,
        "task_working_memory_readback_hints": hint_records,
    }


def preview_memory_application_readback(
    *,
    memory_application_data_id: str,
    case_id: str,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    payload = build_memory_application_readback_preview(
        memory_application_data_id=memory_application_data_id,
        case_id=case_id,
        base_dir=base_dir,
    )
    return save_memory_application_readback_preview(payload, base_dir)


def preview_all_memory_application_readbacks(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    previews = [
        preview_memory_application_readback(
            memory_application_data_id=record["memory_application_data_id"],
            case_id=_case_id_for_memory_data(record),
            base_dir=base_dir,
        )
        for record in list_memory_application_data_records(base_dir)
    ]
    return {
        "memory_application_readback_preview_all_created": True,
        "preview_count": len(previews),
        "previews": previews,
    }


def save_memory_application_readback_preview(
    payload: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    preview_dir = ensure_memory_application_readback_preview_store(base_dir)
    _append_jsonl(
        preview_dir / MEMORY_READBACK_PREVIEWS_FILE,
        payload["memory_application_readback_preview"],
    )
    for hint in payload["task_working_memory_readback_hints"]:
        _append_jsonl(preview_dir / TASK_WORKING_MEMORY_READBACK_HINTS_FILE, hint)
    return dict(payload)


def list_memory_application_readback_previews(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    return _read_jsonl(
        resolve_memory_application_readback_preview_dir(base_dir)
        / MEMORY_READBACK_PREVIEWS_FILE
    )


def list_task_working_memory_readback_hints(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    return _read_jsonl(
        resolve_memory_application_readback_preview_dir(base_dir)
        / TASK_WORKING_MEMORY_READBACK_HINTS_FILE
    )


def resolve_memory_application_readback_preview_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(MEMORY_APPLICATION_READBACK_PREVIEW_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_MEMORY_APPLICATION_READBACK_PREVIEW_DIR


def ensure_memory_application_readback_preview_store(
    base_dir: str | Path | None = None,
) -> Path:
    preview_dir = resolve_memory_application_readback_preview_dir(base_dir)
    preview_dir.mkdir(parents=True, exist_ok=True)
    for file_name in (
        MEMORY_READBACK_PREVIEWS_FILE,
        TASK_WORKING_MEMORY_READBACK_HINTS_FILE,
    ):
        (preview_dir / file_name).touch(exist_ok=True)
    return preview_dir


def _find_memory_application_data(
    memory_application_data_id: str,
    base_dir: str | Path | None,
) -> dict[str, Any]:
    for record in list_memory_application_data_records(base_dir):
        if record.get("memory_application_data_id") == memory_application_data_id:
            return record
    raise LookupError(f"memory application data not found: {memory_application_data_id}")


def _hints_for_memory_data(memory_data: dict[str, Any]) -> tuple[str, ...]:
    kinds = {
        str(item.get("candidate_kind"))
        for item in memory_data.get("memory_items", [])
    }
    hints: list[str] = []
    if kinds & {"blocked_front_obstacle", "repeated_blocked"}:
        hints.extend(("observe_before_direct_retry", "avoid_same_failed_direct_retry"))
    if kinds & {"unknown_resolved", "needs_observe"}:
        hints.extend(("observe_or_adjust", "gather_context_first"))
    if kinds & {"successful_path", "success_simple_reach"}:
        hints.append("known_success_path_available")
    if kinds & {"expected_vs_actual_mismatch", "conflict_detected"}:
        hints.append("verify_expected_actual_before_retry")
    if not hints:
        hints.append("review_memory_context_before_retry")
    return tuple(dict.fromkeys(hints))


def _readback_summary(memory_data: dict[str, Any], hints: tuple[str, ...]) -> str:
    kinds = [
        str(item.get("candidate_kind"))
        for item in memory_data.get("memory_items", [])
    ]
    return f"Preview readback for {','.join(kinds)} suggests {','.join(hints)}."


def _case_id_for_memory_data(memory_data: dict[str, Any]) -> str:
    items = list(memory_data.get("memory_items") or [])
    if not items:
        return "unknown_case"
    candidate_kind = str(items[0].get("candidate_kind"))
    if candidate_kind in {"blocked_front_obstacle", "repeated_blocked"}:
        return "blocked_front_obstacle"
    if candidate_kind in {"unknown_resolved", "needs_observe"}:
        return "unknown_needs_observe"
    if candidate_kind in {"successful_path", "success_simple_reach"}:
        return "success_simple_reach"
    if candidate_kind in {"expected_vs_actual_mismatch", "conflict_detected"}:
        return "conflict_expected_vs_actual"
    return str(items[0].get("case_id") or "unknown_case")


def _source_trace_refs(memory_data: dict[str, Any]) -> list[str]:
    refs: list[str] = [memory_data["memory_application_data_id"]]
    for item in memory_data.get("memory_items", []):
        refs.extend(str(ref) for ref in item.get("source_tick_refs", []))
        refs.extend(str(ref) for ref in item.get("source_working_memory_update_refs", []))
    return list(dict.fromkeys(refs))


def _hint_kind(hint: str) -> str:
    if "observe" in hint or "context" in hint:
        return "observation_hint"
    if "success" in hint:
        return "success_path_hint"
    if "verify" in hint:
        return "conflict_check_hint"
    return "retry_control_hint"


def _preview_id(memory_application_data_id: str) -> str:
    return f"memory_readback_preview:{memory_application_data_id}:{_timestamp()}"


def _hint_id(preview_id: str, hint: str) -> str:
    return f"task_working_memory_readback_hint:{preview_id}:{hint}"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
        file.write("\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
