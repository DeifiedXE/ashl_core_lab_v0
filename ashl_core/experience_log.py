"""Experience event and lesson candidate logging for AGE sandbox traces."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .persistence import append_jsonl, read_jsonl


EXPERIENCE_EVENTS_FILE = "experience_events.jsonl"
LESSON_CANDIDATES_FILE = "lesson_candidates.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def build_experience_event(action_result: dict[str, Any]) -> dict[str, Any] | None:
    required = ["action", "success", "from_state", "to_state"]
    if not isinstance(action_result, dict) or any(key not in action_result for key in required):
        return None

    return {
        "id": _new_id("exp"),
        "type": "experience_event",
        "source": "standing_task",
        "action": action_result["action"],
        "success": action_result["success"],
        "from_state": action_result["from_state"],
        "to_state": action_result["to_state"],
        "failure_reason": action_result.get("failure_reason"),
        "created_at": _now_iso(),
    }


def build_lesson_candidate_from_standing_trace(trace: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(trace, dict) or trace.get("success") is not True or trace.get("final_state") != "standing_stable":
        return None

    evidence = [
        failure.get("failure_reason")
        for failure in trace.get("failures", [])
        if failure.get("failure_reason")
    ]
    lesson = trace.get("lesson_candidate") or {}
    content = lesson.get("content", "從 lying 到 standing_stable 需要中間姿態 sitting 與 balance")

    return {
        "id": _new_id("lesson"),
        "type": "lesson_candidate",
        "lesson_kind": "body_transition",
        "content": content,
        "source": "standing_task",
        "status": "candidate",
        "audit_required": True,
        "evidence": evidence,
        "created_at": _now_iso(),
    }


def append_experience_event(data_dir: str | Path, event: dict[str, Any]) -> None:
    append_jsonl(Path(data_dir) / EXPERIENCE_EVENTS_FILE, event)


def list_experience_events(data_dir: str | Path) -> list[dict[str, Any]]:
    return read_jsonl(Path(data_dir) / EXPERIENCE_EVENTS_FILE)


def append_lesson_candidate(data_dir: str | Path, lesson: dict[str, Any]) -> None:
    append_jsonl(Path(data_dir) / LESSON_CANDIDATES_FILE, lesson)


def list_lesson_candidates(data_dir: str | Path) -> list[dict[str, Any]]:
    return read_jsonl(Path(data_dir) / LESSON_CANDIDATES_FILE)
