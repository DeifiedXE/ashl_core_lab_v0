"""Minimal body state model for the AGE standing sandbox."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


VALID_BODY_STATES = {
    "lying",
    "sitting",
    "standing_unstable",
    "standing_stable",
    "fallen",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def build_body_state(state: str = "lying", stability: float = 0.0, energy: float = 1.0) -> dict[str, Any] | None:
    if state not in VALID_BODY_STATES:
        return None
    return {
        "type": "body_state",
        "state": state,
        "stability": clamp01(stability),
        "energy": clamp01(energy),
        "updated_at": _now_iso(),
    }


def validate_body_state(body: dict[str, Any]) -> bool:
    return (
        isinstance(body, dict)
        and body.get("type") == "body_state"
        and body.get("state") in VALID_BODY_STATES
        and 0.0 <= float(body.get("stability", -1.0)) <= 1.0
        and 0.0 <= float(body.get("energy", -1.0)) <= 1.0
        and isinstance(body.get("updated_at"), str)
    )


def set_body_state(body: dict[str, Any], state: str) -> dict[str, Any] | None:
    if not validate_body_state(body) or state not in VALID_BODY_STATES:
        return None
    updated = dict(body)
    updated["state"] = state
    updated["updated_at"] = _now_iso()
    return updated
