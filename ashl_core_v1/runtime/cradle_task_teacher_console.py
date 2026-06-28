"""Minimal task teacher console for ASHL Core v1 cradle runtime."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.bounded_teacher_gated_task_tick_runner import (
    list_bounded_teacher_gated_task_tick_runs,
    load_last_bounded_teacher_gated_task_tick_run,
    run_bounded_teacher_gated_task_tick_runner,
)
from ashl_core_v1.runtime.task_run_closure import (
    close_last_task_run,
    list_task_learning_digest_candidates,
    load_last_task_run_closure,
)
from ashl_core_v1.runtime.multi_case_cradle_task_suite import (
    list_cradle_task_suite_cases,
    load_last_multi_case_cradle_task_suite_summary,
    run_multi_case_cradle_task_case,
)


CRADLE_TASK_TEACHER_CONSOLE_ENV = "ASHL_CORE_V1_CRADLE_TASK_TEACHER_CONSOLE_DIR"
DEFAULT_CRADLE_TASK_TEACHER_CONSOLE_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "cradle_task_teacher_console"
)
TASK_CANDIDATE_MARKS_FILE = "task_learning_candidate_marks.json"

ALLOWED_CANDIDATE_MARK_STATUSES = {
    "teacher_seen",
    "ignored",
    "needs_manual_review",
}


def get_cradle_task_teacher_console_status(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    last_run = load_last_bounded_teacher_gated_task_tick_run(base_dir)
    last_closure = load_last_task_run_closure(base_dir)
    candidates = list_task_learning_digest_candidates(base_dir)
    marks = load_candidate_marks(base_dir)
    frame = (last_run or {}).get("final_active_task_frame") or {}
    return {
        "console_status_available": True,
        "last_run_id": _last_run_id(last_run),
        "active_task_frame_id": frame.get("active_task_frame_id"),
        "task_status": frame.get("task_status"),
        "last_tick": frame.get("current_tick"),
        "last_outcome": frame.get("last_outcome_label"),
        "pending_learning_candidate_count": _pending_candidate_count(candidates, marks),
        "last_closure_id": _last_closure_id(last_closure),
        "scheduler_created": False,
        "action_execution_used": False,
        "memory_write": False,
    }


def run_blocked_task_from_teacher_console(
    *,
    max_ticks: int = 5,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    run = run_bounded_teacher_gated_task_tick_runner(
        max_ticks=max_ticks,
        base_dir=base_dir,
    )
    return {
        "console_action": "run_blocked_task",
        "bounded_task_run": run,
        "status": get_cradle_task_teacher_console_status(base_dir),
        "scheduler_created": False,
        "action_execution_used": False,
        "memory_write": False,
    }


def list_cases_from_teacher_console() -> dict[str, Any]:
    return {"cases": list_cradle_task_suite_cases()}


def run_case_from_teacher_console(
    *,
    case_id: str,
    max_ticks: int = 5,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    case_run = run_multi_case_cradle_task_case(
        case_id,
        max_ticks=max_ticks,
        base_dir=base_dir,
    )
    return {
        "console_action": "run_case",
        "case_run": case_run,
        "status": get_cradle_task_teacher_console_status(base_dir),
        "scheduler_created": False,
        "action_execution_used": False,
        "memory_write": False,
    }


def show_suite_summary_from_teacher_console(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    payload = load_last_multi_case_cradle_task_suite_summary(base_dir)
    if payload is None:
        return {"status": "not_found", "error": "suite summary not found"}
    return dict(payload)


def close_last_run_from_teacher_console(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    closure = close_last_task_run(base_dir)
    return {
        "console_action": "close_last_run",
        "task_run_closure": closure,
        "status": get_cradle_task_teacher_console_status(base_dir),
        "memory_write": False,
    }


def show_working_memory_from_teacher_console(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    last_run = load_last_bounded_teacher_gated_task_tick_run(base_dir)
    frame = (last_run or {}).get("final_active_task_frame")
    if frame is None:
        return {
            "status": "not_found",
            "error": "working memory task frame not found",
        }
    return {
        "task_id": frame.get("task_id"),
        "current_goal": frame.get("current_goal"),
        "current_tick": frame.get("current_tick"),
        "current_step": frame.get("current_step"),
        "last_outcome_label": frame.get("last_outcome_label"),
        "next_candidate_hints": frame.get("next_candidate_hints", []),
        "continue_allowed": frame.get("continue_allowed"),
        "stop_reason": frame.get("stop_reason"),
    }


def show_last_run_from_teacher_console(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    last_run = load_last_bounded_teacher_gated_task_tick_run(base_dir)
    if last_run is None:
        return {"status": "not_found", "error": "last run not found"}
    return dict(last_run)


def show_learning_candidates_from_teacher_console(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    marks = load_candidate_marks(base_dir)
    candidates = []
    for candidate in list_task_learning_digest_candidates(base_dir):
        candidate_id = candidate["candidate_id"]
        candidates.append({**candidate, "teacher_mark_status": marks.get(candidate_id)})
    return {"task_learning_digest_candidates": candidates}


def mark_learning_candidate_from_teacher_console(
    *,
    candidate_id: str,
    status: str,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    if status not in ALLOWED_CANDIDATE_MARK_STATUSES:
        raise ValueError("candidate mark status must be teacher_seen, ignored, or needs_manual_review")
    candidates = list_task_learning_digest_candidates(base_dir)
    if candidate_id not in {candidate["candidate_id"] for candidate in candidates}:
        raise LookupError(f"candidate not found: {candidate_id}")
    marks = load_candidate_marks(base_dir)
    marks[candidate_id] = status
    save_candidate_marks(marks, base_dir)
    return {
        "candidate_marked": True,
        "candidate_id": candidate_id,
        "status": status,
        "approved": False,
        "reviewed_learning_digest_created": False,
        "memory_write": False,
        "marked_at": _now(),
    }


def load_candidate_marks(base_dir: str | Path | None = None) -> dict[str, str]:
    path = resolve_cradle_task_teacher_console_dir(base_dir) / TASK_CANDIDATE_MARKS_FILE
    if not path.exists():
        return {}
    return dict(json.loads(path.read_text(encoding="utf-8")))


def save_candidate_marks(
    marks: dict[str, str],
    base_dir: str | Path | None = None,
) -> dict[str, str]:
    console_dir = ensure_cradle_task_teacher_console_store(base_dir)
    path = console_dir / TASK_CANDIDATE_MARKS_FILE
    path.write_text(
        json.dumps(marks, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return dict(marks)


def resolve_cradle_task_teacher_console_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(CRADLE_TASK_TEACHER_CONSOLE_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_CRADLE_TASK_TEACHER_CONSOLE_DIR


def ensure_cradle_task_teacher_console_store(
    base_dir: str | Path | None = None,
) -> Path:
    console_dir = resolve_cradle_task_teacher_console_dir(base_dir)
    console_dir.mkdir(parents=True, exist_ok=True)
    return console_dir


def _last_run_id(last_run: dict[str, Any] | None) -> str | None:
    if not last_run:
        return None
    return last_run.get("bounded_task_tick_run_record", {}).get("run_id")


def _last_closure_id(last_closure: dict[str, Any] | None) -> str | None:
    if not last_closure:
        return None
    return last_closure.get("task_run_closure_record", {}).get(
        "task_run_closure_record_id"
    )


def _pending_candidate_count(
    candidates: list[dict[str, Any]],
    marks: dict[str, str],
) -> int:
    return sum(
        1
        for candidate in candidates
        if marks.get(candidate["candidate_id"]) != "ignored"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
