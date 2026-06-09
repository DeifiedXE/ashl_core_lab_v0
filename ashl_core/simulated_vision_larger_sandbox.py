"""Static larger symbolic simulated vision sandbox."""

from __future__ import annotations

from typing import Any

from .simulated_vision_sandbox import (
    FIRST_PERSON_AGENT_VIEWPORT_POSITION,
    FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION,
    FIRST_PERSON_FRONT_SYMBOL_POSITION,
    SUPPORTED_FACINGS,
    turn_left,
    turn_right,
    validate_simulated_vision_action,
    viewport_cells_for_facing,
)


LARGER_LEVEL_ID = "simulated_vision_larger_sandbox_v0"
LARGER_SANDBOX_GRID = (
    "############",
    "#....#..I..#",
    "#.A.D......#",
    "#....#I....#",
    "###D####.###",
    "#..........#",
    "#.I.#......#",
    "#....#..I..E",
    "############",
)
LARGER_INITIAL_FACING = "north"
ALLOWED_LARGER_VIEWPORT_SYMBOLS = frozenset({"w", "e", "i", "d", "g", "x", "a"})

_FACING_DELTAS = {
    "north": (0, -1),
    "east": (1, 0),
    "south": (0, 1),
    "west": (-1, 0),
}
_SOURCE_TO_VIEWPORT_SYMBOL = {
    "#": "w",
    ".": "e",
    "A": "e",
    "I": "i",
    "D": "d",
    "E": "g",
}


def create_simulated_vision_larger_sandbox() -> dict[str, Any]:
    agent_starts = _positions_for_symbol("A")
    if len(agent_starts) != 1:
        raise ValueError("larger sandbox must contain exactly one agent start")
    return {
        "level_id": LARGER_LEVEL_ID,
        "grid": LARGER_SANDBOX_GRID,
        "agent_start": agent_starts[0],
        "initial_facing": LARGER_INITIAL_FACING,
        "items": tuple(_positions_for_symbol("I")),
        "doorways": tuple(_positions_for_symbol("D")),
        "exits": tuple(_positions_for_symbol("E")),
    }


def build_initial_larger_sandbox_state(level: dict[str, Any] | None = None) -> dict[str, Any]:
    level = level or create_simulated_vision_larger_sandbox()
    return {
        "level_id": level["level_id"],
        "pos": tuple(level["agent_start"]),
        "facing": level["initial_facing"],
        "tick": 0,
    }


def build_larger_sandbox_map_summary(level: dict[str, Any]) -> dict[str, Any]:
    grid = level["grid"]
    width = len(grid[0])
    if any(len(row) != width for row in grid):
        raise ValueError("larger sandbox grid rows must have stable width")
    unsupported = sorted({cell for row in grid for cell in row if cell not in _SOURCE_TO_VIEWPORT_SYMBOL})
    return {
        "width": width,
        "height": len(grid),
        "agent_start": list(level["agent_start"]),
        "initial_facing": level["initial_facing"],
        "item_count": len(level["items"]),
        "doorway_count": len(level["doorways"]),
        "exit_count": len(level["exits"]),
        "symbols_supported": sorted(_SOURCE_TO_VIEWPORT_SYMBOL),
        "unsupported_symbols": unsupported,
    }


def render_larger_sandbox_viewport(
    state: dict[str, Any],
    level: dict[str, Any],
    size: int = 3,
) -> list[list[str]]:
    rows = viewport_cells_for_facing(tuple(state["pos"]), state["facing"], size=size)
    center = tuple(state["pos"])
    return [["a" if pos == center else symbol_at_larger_sandbox(level, pos) for pos in row] for row in rows]


def symbol_at_larger_sandbox(level: dict[str, Any], pos: tuple[int, int]) -> str:
    x, y = pos
    grid = level["grid"]
    if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[y]):
        return "x"
    return _SOURCE_TO_VIEWPORT_SYMBOL[grid[y][x]]


def front_symbol_from_larger_viewport(viewport: list[list[str]]) -> str:
    row_index, col_index = FIRST_PERSON_FRONT_SYMBOL_POSITION
    return viewport[row_index][col_index]


def apply_larger_sandbox_action(
    state: dict[str, Any],
    level: dict[str, Any],
    action: str,
) -> dict[str, Any]:
    action = validate_simulated_vision_action(action)
    before = _snapshot_state(state)
    before_viewport = render_larger_sandbox_viewport(before, level)
    front_symbol = front_symbol_from_larger_viewport(before_viewport)
    after = _snapshot_state(state)
    target = _target_for_state(before) if action == "move_forward" else None
    failure_reasons: list[str] = []
    effect_tags: list[str] = []

    if action == "turn_left":
        after["facing"] = turn_left(before["facing"])
        result = "turned"
    elif action == "turn_right":
        after["facing"] = turn_right(before["facing"])
        result = "turned"
    elif action == "look":
        result = "observed"
    else:
        if front_symbol == "w":
            result = "blocked"
            failure_reasons = ["wall_blocked"]
        elif front_symbol == "i":
            after["pos"] = target
            result = "item_contact"
            effect_tags = ["item_contact"]
        elif front_symbol == "d":
            after["pos"] = target
            result = "moved"
            effect_tags = ["passage_crossed"]
        elif front_symbol == "g":
            after["pos"] = target
            result = "exit_contact"
            effect_tags = ["exit_contact"]
        else:
            after["pos"] = target
            result = "moved"

    after["tick"] = before["tick"] + 1
    return {
        "state": after,
        "trace": _build_action_trace(
            tick=after["tick"],
            action=action,
            before=before,
            after=after,
            result=result,
            viewport=render_larger_sandbox_viewport(after, level),
            front_symbol=front_symbol,
            failure_reasons=failure_reasons,
            effect_tags=effect_tags,
            target=target,
        ),
    }


def run_simulated_vision_larger_sandbox_demo(
    action_sequence: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    actions = tuple(action_sequence) if action_sequence is not None else (
        "look",
        "turn_right",
        "look",
        "move_forward",
        "look",
        "turn_left",
        "look",
    )
    level = create_simulated_vision_larger_sandbox()
    state = build_initial_larger_sandbox_state(level)
    initial_state = _public_state(state)
    action_trace = []
    for action in actions:
        result = apply_larger_sandbox_action(state, level, action)
        state = result["state"]
        action_trace.append(result["trace"])
    return {
        "command": "run-simulated-vision-larger-sandbox-demo",
        "flow": "simulated_vision_larger_sandbox_static_runtime_v0",
        "status": "ok",
        "level_id": level["level_id"],
        "initial_state": initial_state,
        "map_summary": build_larger_sandbox_map_summary(level),
        "action_trace": action_trace,
        "final_state": _public_state(state),
        "boundary_check": _boundary_check(),
        "notes": [
            "This is a static larger symbolic simulated vision test room.",
            "D is passable but is not taught as a semantic room boundary.",
            "E is a static exit placeholder only; there is no conditional exit activation.",
            "No item collection, curiosity, prediction error, pathfinding, place memory, or home sandbox is added.",
        ],
    }


def _boundary_check() -> dict[str, Any]:
    return {
        "simulated_vision_only": True,
        "larger_static_sandbox_enabled": True,
        "structured_symbols_only": True,
        "real_image_vision": False,
        "llm_vision_used": False,
        "llm_planning_used": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "full_map_visible_to_agent": False,
        "first_person_viewport": True,
        "agent_viewport_position": FIRST_PERSON_AGENT_VIEWPORT_POSITION,
        "front_symbol_position": FIRST_PERSON_FRONT_SYMBOL_POSITION,
        "far_front_symbol_position": FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION,
        "centered_top_down_viewport": False,
        "doorway_symbol_supported": True,
        "doorway_passable": True,
        "doorway_semantic_boundary_given_to_agent": False,
        "exit_placeholder_supported": True,
        "exit_conditional_spawn_enabled": False,
        "task_completion_enabled": False,
        "item_collection_enabled": False,
        "item_pickup_enabled": False,
        "inventory_enabled": False,
        "curiosity_enabled": False,
        "prediction_error_enabled": False,
        "place_memory_enabled": False,
        "home_sandbox_enabled": False,
        "action_selection_modified": False,
        "existing_navigation_action_selection_modified": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "visual_understanding_claimed": False,
        "symbol_grounding_solved_claimed": False,
        "general_learning_claimed": False,
    }


def _positions_for_symbol(symbol: str) -> list[tuple[int, int]]:
    return [
        (x, y)
        for y, row in enumerate(LARGER_SANDBOX_GRID)
        for x, cell in enumerate(row)
        if cell == symbol
    ]


def _target_for_state(state: dict[str, Any]) -> tuple[int, int]:
    return _add(tuple(state["pos"]), _FACING_DELTAS[state["facing"]])


def _build_action_trace(
    *,
    tick: int,
    action: str,
    before: dict[str, Any],
    after: dict[str, Any],
    result: str,
    viewport: list[list[str]],
    front_symbol: str,
    failure_reasons: list[str],
    effect_tags: list[str],
    target: tuple[int, int] | None,
) -> dict[str, Any]:
    return {
        "tick": tick,
        "action": action,
        "before": _public_state(before),
        "after": _public_state(after),
        "result": result,
        "viewport": viewport,
        "front_symbol": front_symbol,
        "failure_reasons": failure_reasons,
        "effect_tags": effect_tags,
        "target": list(target) if target is not None else None,
    }


def _snapshot_state(state: dict[str, Any]) -> dict[str, Any]:
    facing = state["facing"]
    if facing not in SUPPORTED_FACINGS:
        raise ValueError(f"unsupported facing: {facing}")
    return {
        "level_id": state["level_id"],
        "pos": tuple(state["pos"]),
        "facing": facing,
        "tick": state["tick"],
    }


def _public_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "pos": list(state["pos"]),
        "facing": state["facing"],
    }


def _add(first: tuple[int, int], second: tuple[int, int]) -> tuple[int, int]:
    return (first[0] + second[0], first[1] + second[1])
