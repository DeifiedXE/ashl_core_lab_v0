"""Minimal standing task trace for the AGE action sandbox."""

from __future__ import annotations

from typing import Any

from .action_sandbox import apply_action
from .body_state import build_body_state


def _lesson_candidate() -> dict[str, Any]:
    return {
        "type": "lesson_candidate",
        "lesson_kind": "body_transition",
        "content": "從 lying 到 standing_stable 需要中間姿態 sitting 與 balance",
        "status": "candidate",
        "audit_required": True,
    }


def run_standing_task() -> dict[str, Any]:
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

    return {
        "type": "standing_task_trace",
        "initial_state": "lying",
        "final_state": body["state"],
        "actions": actions,
        "failures": failures,
        "lesson_candidate": _lesson_candidate(),
        "success": body["state"] == "standing_stable",
    }
