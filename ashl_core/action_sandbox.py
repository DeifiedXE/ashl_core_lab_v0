"""Pure Python action sandbox for minimal body transitions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .body_state import build_body_state, clamp01, validate_body_state


VALID_ACTIONS = {"sit_up", "stand_up", "balance", "fall_down", "rest"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _result(
    action: str,
    success: bool,
    from_state: str,
    body_state: dict[str, Any],
    failure_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "type": "action_result",
        "action": action,
        "success": success,
        "from_state": from_state,
        "to_state": body_state["state"],
        "failure_reason": failure_reason,
        "body_state": body_state,
        "created_at": _now_iso(),
    }


def apply_action(body_state: dict[str, Any], action: str) -> dict[str, Any]:
    if not validate_body_state(body_state):
        fallback = build_body_state("fallen", stability=0.0, energy=0.0)
        return _result(action, False, "invalid", fallback, "invalid_body_state")

    from_state = body_state["state"]
    energy = body_state["energy"]

    if action not in VALID_ACTIONS:
        return _result(action, False, from_state, dict(body_state), "unknown_action")

    if action == "fall_down":
        return _result(action, True, from_state, build_body_state("fallen", stability=0.0, energy=energy))

    if action == "rest":
        rested = build_body_state(from_state, stability=body_state["stability"], energy=clamp01(energy + 0.2))
        return _result(action, True, from_state, rested)

    if from_state == "lying" and action == "stand_up":
        return _result(action, False, from_state, dict(body_state), "cannot_stand_directly_from_lying")

    if from_state == "lying" and action == "sit_up":
        return _result(action, True, from_state, build_body_state("sitting", stability=0.4, energy=energy))

    if from_state == "sitting" and action == "stand_up":
        return _result(action, True, from_state, build_body_state("standing_unstable", stability=0.45, energy=energy))

    if from_state == "standing_unstable" and action == "balance":
        return _result(action, True, from_state, build_body_state("standing_stable", stability=0.85, energy=energy))

    if from_state == "standing_stable" and action == "balance":
        return _result(action, True, from_state, build_body_state("standing_stable", stability=0.85, energy=energy))

    return _result(action, False, from_state, dict(body_state), "unsupported_transition")


def validate_action_result(result: dict[str, Any]) -> bool:
    return (
        isinstance(result, dict)
        and result.get("type") == "action_result"
        and isinstance(result.get("action"), str)
        and isinstance(result.get("success"), bool)
        and isinstance(result.get("from_state"), str)
        and isinstance(result.get("to_state"), str)
        and validate_body_state(result.get("body_state", {}))
        and isinstance(result.get("created_at"), str)
    )
