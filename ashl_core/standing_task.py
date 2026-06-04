"""Minimal standing task trace for the AGE action sandbox."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .action_sandbox import apply_action
from .body_state import build_body_state
from .experience_log import (
    append_experience_event,
    append_lesson_candidate,
    build_experience_event,
    build_lesson_candidate_from_standing_trace,
)


def _lesson_candidate() -> dict[str, Any]:
    return {
        "type": "lesson_candidate",
        "lesson_kind": "body_transition",
        "content": "從 lying 到 standing_stable 需要中間姿態 sitting 與 balance",
        "status": "candidate",
        "audit_required": True,
    }


def run_standing_task(persist_experience: bool = False, data_dir: str | Path = "data") -> dict[str, Any]:
    body = build_body_state("lying")
    actions: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for action in ["stand_up", "sit_up", "stand_up", "balance"]:
        result = apply_action(body, action)
        actions.append(result)
        if not result["success"]:
            failures.append(
                {
                    "action": result["action"],
                    "from_state": result["from_state"],
                    "failure_reason": result["failure_reason"],
                }
            )
        body = result["body_state"]

    trace = {
        "type": "standing_task_trace",
        "initial_state": "lying",
        "final_state": body["state"],
        "actions": actions,
        "failures": failures,
        "lesson_candidate": _lesson_candidate(),
        "success": body["state"] == "standing_stable",
        "experience_persistence": None,
    }

    if persist_experience:
        events = [
            event
            for event in (build_experience_event(action_result) for action_result in actions)
            if event is not None
        ]
        for event in events:
            append_experience_event(data_dir, event)

        lesson = build_lesson_candidate_from_standing_trace(trace)
        if lesson is not None:
            append_lesson_candidate(data_dir, lesson)

        trace["experience_persistence"] = {
            "experience_events_written": len(events),
            "lesson_candidate_written": lesson is not None,
            "files": ["experience_events.jsonl", "lesson_candidates.jsonl"],
        }

    return trace
