"""Symbolic simulated vision sandbox with position, facing, and viewport."""

from __future__ import annotations

from typing import Any


LEVEL_ID = "simulated_vision_room_v0"
ROOM_GRID = (
    "#######",
    "#...I.#",
    "#.....#",
    "#.....#",
    "#.....#",
    "#.I...#",
    "#######",
)
AGENT_START = (3, 3)
INITIAL_FACING = "north"
SUPPORTED_FACINGS = ("north", "east", "south", "west")
SUPPORTED_ACTIONS = frozenset({"turn_left", "turn_right", "look", "move_forward"})
ALLOWED_VIEWPORT_SYMBOLS = frozenset({"w", "e", "i", "x", "a"})

_LEFT_TURN = {
    "north": "west",
    "west": "south",
    "south": "east",
    "east": "north",
}
_RIGHT_TURN = {
    "north": "east",
    "east": "south",
    "south": "west",
    "west": "north",
}
_FACING_DELTAS = {
    "north": (0, -1),
    "east": (1, 0),
    "south": (0, 1),
    "west": (-1, 0),
}
_VIEWPORT_AXES = {
    "north": ((0, -1), (1, 0)),
    "east": ((1, 0), (0, 1)),
    "south": ((0, 1), (-1, 0)),
    "west": ((-1, 0), (0, -1)),
}
FIRST_PERSON_AGENT_VIEWPORT_POSITION = [2, 1]
FIRST_PERSON_FRONT_SYMBOL_POSITION = [1, 1]
FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION = [0, 1]


def create_simulated_vision_room() -> dict[str, Any]:
    return {
        "level_id": LEVEL_ID,
        "grid": ROOM_GRID,
        "agent_start": AGENT_START,
        "initial_facing": INITIAL_FACING,
        "items": ((4, 1), (2, 5)),
    }


def build_initial_simulated_vision_state(level: dict[str, Any] | None = None) -> dict[str, Any]:
    level = level or create_simulated_vision_room()
    return {
        "level_id": level["level_id"],
        "pos": tuple(level["agent_start"]),
        "facing": level["initial_facing"],
        "tick": 0,
    }


def turn_left(facing: str) -> str:
    _validate_facing(facing)
    return _LEFT_TURN[facing]


def turn_right(facing: str) -> str:
    _validate_facing(facing)
    return _RIGHT_TURN[facing]


def render_viewport(state: dict[str, Any], level: dict[str, Any], size: int = 3) -> list[list[str]]:
    rows = viewport_cells_for_facing(tuple(state["pos"]), state["facing"], size=size)
    center = tuple(state["pos"])
    return [["a" if pos == center else _symbol_at(level, pos) for pos in row] for row in rows]


def viewport_cells_for_facing(
    agent_pos: tuple[int, int],
    facing: str,
    size: int = 3,
) -> list[list[tuple[int, int]]]:
    if size <= 0 or size % 2 == 0:
        raise ValueError("viewport size must be a positive odd number")
    _validate_facing(facing)
    forward_axis, right_axis = _VIEWPORT_AXES[facing]
    radius = size // 2
    center = tuple(agent_pos)
    rows: list[list[tuple[int, int]]] = []
    for row_index in range(size):
        forward_offset = size - 1 - row_index
        row = []
        for right_offset in range(-radius, radius + 1):
            pos = _add(center, _scale(forward_axis, forward_offset))
            pos = _add(pos, _scale(right_axis, right_offset))
            row.append(pos)
        rows.append(row)
    return rows


def look(state: dict[str, Any], level: dict[str, Any], size: int = 3) -> dict[str, Any]:
    viewport = render_viewport(state, level, size=size)
    visible_symbols = sorted({symbol for row in viewport for symbol in row})
    return {
        "pos": list(state["pos"]),
        "facing": state["facing"],
        "viewport": viewport,
        "visible_symbols": visible_symbols,
    }


def move_forward(state: dict[str, Any], level: dict[str, Any]) -> dict[str, Any]:
    before = _snapshot_state(state)
    target = _add(tuple(state["pos"]), _FACING_DELTAS[state["facing"]])
    target_symbol = _symbol_at(level, target)
    after = _snapshot_state(state)
    blocked = target_symbol == "w"
    failure_reasons: list[str] = []
    if blocked:
        result = "blocked"
        failure_reasons = ["wall_blocked"]
    elif target_symbol == "i":
        after["pos"] = target
        result = "item_contact"
    else:
        after["pos"] = target
        result = "moved"
    after["tick"] = before["tick"] + 1
    return {
        "state": after,
        "trace": _build_action_trace(
            tick=after["tick"],
            action="move_forward",
            before=before,
            after=after,
            result=result,
            failure_reasons=failure_reasons,
            viewport=render_viewport(after, level),
            target=target,
        ),
    }


def apply_simulated_vision_action(
    state: dict[str, Any],
    level: dict[str, Any],
    action: str,
) -> dict[str, Any]:
    action = validate_simulated_vision_action(action)
    if action == "move_forward":
        return move_forward(state, level)

    before = _snapshot_state(state)
    after = _snapshot_state(state)
    if action == "turn_left":
        after["facing"] = turn_left(before["facing"])
        result = "turned"
    elif action == "turn_right":
        after["facing"] = turn_right(before["facing"])
        result = "turned"
    else:
        result = "observed"
    after["tick"] = before["tick"] + 1
    return {
        "state": after,
        "trace": _build_action_trace(
            tick=after["tick"],
            action=action,
            before=before,
            after=after,
            result=result,
            failure_reasons=[],
            viewport=render_viewport(after, level),
        ),
    }


def run_simulated_vision_viewport_demo(
    action_sequence: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    actions = tuple(action_sequence) if action_sequence is not None else (
        "look",
        "move_forward",
        "look",
        "move_forward",
        "look",
        "turn_right",
        "look",
    )
    level = create_simulated_vision_room()
    state = build_initial_simulated_vision_state(level)
    initial_state = _public_state(state)
    action_trace = []
    for action in actions:
        result = apply_simulated_vision_action(state, level, action)
        state = result["state"]
        action_trace.append(result["trace"])
    return {
        "command": "run-simulated-vision-viewport-demo",
        "flow": "simulated_vision_facing_viewport_v0",
        "status": "ok",
        "level_id": level["level_id"],
        "initial_state": initial_state,
        "action_trace": action_trace,
        "final_state": _public_state(state),
        "boundary_check": {
            "simulated_vision_only": True,
            "first_person_viewport": True,
            "agent_viewport_position": FIRST_PERSON_AGENT_VIEWPORT_POSITION,
            "front_symbol_position": FIRST_PERSON_FRONT_SYMBOL_POSITION,
            "far_front_symbol_position": FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION,
            "centered_top_down_viewport": False,
            "real_image_vision": False,
            "structured_symbols_only": True,
            "full_map_visible_to_agent": False,
            "facing_supported": True,
            "turn_left_supported": True,
            "turn_right_supported": True,
            "look_supported": True,
            "move_forward_supported": True,
            "pathfinding_used": False,
            "llm_vision_used": False,
            "llm_planning_used": False,
            "session_memory_write": False,
            "lesson_store_write": False,
            "memory_layer_write": False,
            "long_term_memory_write": False,
        },
        "notes": [
            "This is structured symbolic simulated vision, not real image vision.",
            "The agent receives only a bounded first-person rotated viewport, not the full map as vision.",
            "The agent marker is at viewport[2][1]; immediate front is viewport[1][1].",
            "Session Working Memory bridge is deferred to next package.",
        ],
    }


def validate_simulated_vision_action(action: str) -> str:
    if action not in SUPPORTED_ACTIONS:
        raise ValueError(f"unsupported simulated vision action: {action}")
    return action


def _validate_facing(facing: str) -> None:
    if facing not in SUPPORTED_FACINGS:
        raise ValueError(f"unsupported facing: {facing}")


def _build_action_trace(
    *,
    tick: int,
    action: str,
    before: dict[str, Any],
    after: dict[str, Any],
    result: str,
    failure_reasons: list[str],
    viewport: list[list[str]],
    target: tuple[int, int] | None = None,
) -> dict[str, Any]:
    trace = {
        "tick": tick,
        "action": action,
        "before": _public_state(before),
        "after": _public_state(after),
        "result": result,
        "viewport": viewport,
        "failure_reasons": failure_reasons,
    }
    if target is not None:
        trace["target"] = list(target)
    return trace


def _snapshot_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "level_id": state["level_id"],
        "pos": tuple(state["pos"]),
        "facing": state["facing"],
        "tick": state["tick"],
    }


def _public_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "pos": list(state["pos"]),
        "facing": state["facing"],
    }


def _symbol_at(level: dict[str, Any], pos: tuple[int, int]) -> str:
    x, y = pos
    grid = level["grid"]
    if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[y]):
        return "x"
    tile = grid[y][x]
    if tile == "#":
        return "w"
    if tile == "I":
        return "i"
    return "e"


def _add(first: tuple[int, int], second: tuple[int, int]) -> tuple[int, int]:
    return (first[0] + second[0], first[1] + second[1])


def _scale(vector: tuple[int, int], amount: int) -> tuple[int, int]:
    return (vector[0] * amount, vector[1] * amount)
