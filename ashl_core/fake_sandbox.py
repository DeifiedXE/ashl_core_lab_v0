"""Deterministic fake sandbox for Phase -1 lesson contribution tests."""

from __future__ import annotations

from typing import Any


def build_initial_sandbox_state(include_facing: bool = True) -> dict[str, Any]:
    state = {
        "avatar_facing": "north",
        "object_id": "cube_001",
        "holding": None,
    }
    if not include_facing:
        state.pop("avatar_facing")
    return state


def observe(state: dict[str, Any], visible_keys: list[str] | None = None) -> dict[str, Any]:
    if visible_keys is None:
        visible = dict(state)
    else:
        visible = {key: state[key] for key in visible_keys if key in state}
    return {
        "type": "sandbox_observation",
        "result": "success",
        "visible_state": visible,
    }


def turn(state: dict[str, Any], direction: str) -> dict[str, Any]:
    updated = dict(state)
    updated["avatar_facing"] = direction
    return {
        "type": "sandbox_action_result",
        "tool": "turn",
        "direction": direction,
        "result": "success",
        "state": updated,
    }


def pick_up(state: dict[str, Any], object_id: str) -> dict[str, Any]:
    updated = dict(state)
    if object_id != "cube_001":
        return {
            "type": "sandbox_action_result",
            "tool": "pick_up",
            "object_id": object_id,
            "result": "failed",
            "failure_reason": "unknown_object",
            "state": updated,
        }

    if state.get("avatar_facing") != "east":
        return {
            "type": "sandbox_action_result",
            "tool": "pick_up",
            "object_id": object_id,
            "result": "failed",
            "failure_reason": "not_facing_east",
            "state": updated,
        }

    updated["holding"] = object_id
    return {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": object_id,
        "result": "success",
        "failure_reason": None,
        "state": updated,
    }
