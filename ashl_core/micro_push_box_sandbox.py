"""Tiny tactile push-box sandbox for deterministic contact traces."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


INITIAL_MAP = (
    "#####",
    "#...#",
    "#.QB#",
    "#..G#",
    "#####",
)

DIRECTIONS = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

SUPPORTED_ACTIONS = tuple(
    f"{prefix}_{direction}"
    for prefix in ("touch", "move", "push")
    for direction in ("up", "down", "left", "right")
)


def build_initial_state() -> dict[str, Any]:
    return _state_from_grid(INITIAL_MAP)


def apply_tactile_action(state: dict[str, Any], action: str) -> dict[str, Any]:
    if action not in SUPPORTED_ACTIONS:
        raise ValueError(f"unsupported action: {action}")

    prefix, direction = action.split("_", 1)
    before = _snapshot(state)
    after_state = _snapshot(state)
    delta = DIRECTIONS[direction]
    target = _add(before["agent_pos"], delta)
    contact = _contact_at(before, target)
    result = "empty"
    blocked = False

    if prefix == "touch":
        result, blocked = _touch_result(contact)
    elif prefix == "move":
        result, blocked = _move(after_state, target, contact)
    elif prefix == "push":
        result, blocked, contact = _push(after_state, target, delta, contact)

    after_state["tick"] = before["tick"] + 1
    trace = {
        "trace_type": "tactile_sandbox_trace",
        "tick": after_state["tick"],
        "action": action,
        "before": before,
        "after": _snapshot(after_state),
        "contact": contact,
        "result": result,
        "blocked": blocked,
        "agent_pos": after_state["agent_pos"],
        "box_pos": after_state["box_pos"],
        "goal_pos": after_state["goal_pos"],
    }
    return {"state": after_state, "trace": trace}


def _state_from_grid(grid: tuple[str, ...]) -> dict[str, Any]:
    agent_pos = box_pos = goal_pos = None
    normalized = []
    for row_index, row in enumerate(grid):
        normalized_row = []
        for col_index, cell in enumerate(row):
            pos = (row_index, col_index)
            if cell == "Q":
                agent_pos = pos
                normalized_row.append(".")
            elif cell == "B":
                box_pos = pos
                normalized_row.append(".")
            elif cell == "G":
                goal_pos = pos
                normalized_row.append("G")
            else:
                normalized_row.append(cell)
        normalized.append("".join(normalized_row))
    if agent_pos is None or box_pos is None or goal_pos is None:
        raise ValueError("grid must include Q, B, and G")
    return {
        "grid": tuple(normalized),
        "agent_pos": agent_pos,
        "box_pos": box_pos,
        "goal_pos": goal_pos,
        "tick": 0,
    }


def _snapshot(state: dict[str, Any]) -> dict[str, Any]:
    copied = deepcopy(state)
    copied["grid"] = tuple(copied["grid"])
    copied["agent_pos"] = tuple(copied["agent_pos"])
    copied["box_pos"] = tuple(copied["box_pos"])
    copied["goal_pos"] = tuple(copied["goal_pos"])
    return copied


def _add(pos: tuple[int, int], delta: tuple[int, int]) -> tuple[int, int]:
    return (pos[0] + delta[0], pos[1] + delta[1])


def _cell_at(state: dict[str, Any], pos: tuple[int, int]) -> str:
    row, col = pos
    if row < 0 or col < 0 or row >= len(state["grid"]) or col >= len(state["grid"][row]):
        return "#"
    return state["grid"][row][col]


def _contact_at(state: dict[str, Any], pos: tuple[int, int]) -> str:
    if pos == state["box_pos"]:
        return "box"
    if _cell_at(state, pos) == "#":
        return "wall"
    if pos == state["goal_pos"]:
        return "goal"
    return "empty"


def _touch_result(contact: str) -> tuple[str, bool]:
    if contact == "wall":
        return "wall_blocked", True
    if contact == "box":
        return "box_contact", False
    if contact == "goal":
        return "goal_reached", False
    return "empty", False


def _move(state: dict[str, Any], target: tuple[int, int], contact: str) -> tuple[str, bool]:
    if contact == "wall":
        return "wall_blocked", True
    if contact == "box":
        return "box_blocked", True
    state["agent_pos"] = target
    if contact == "goal":
        return "goal_reached", False
    return "empty", False


def _push(
    state: dict[str, Any],
    target: tuple[int, int],
    delta: tuple[int, int],
    contact: str,
) -> tuple[str, bool, str]:
    if contact == "wall":
        return "wall_blocked", True, contact
    if contact != "box":
        return "empty", True, contact

    box_destination = _add(state["box_pos"], delta)
    destination_contact = _contact_at({**state, "box_pos": (-1, -1)}, box_destination)
    if destination_contact == "wall" or destination_contact == "box":
        return "box_blocked", True, "box"

    state["agent_pos"] = target
    state["box_pos"] = box_destination
    if box_destination == state["goal_pos"]:
        return "goal_reached", False, "box"
    return "box_pushed", False, "box"
