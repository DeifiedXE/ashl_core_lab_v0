"""Session-local observed map for symbolic simulated vision."""

from __future__ import annotations

from typing import Any

from .simulated_vision_sandbox import (
    apply_simulated_vision_action,
    build_initial_simulated_vision_state,
    create_simulated_vision_room,
)


DEFAULT_OBSERVED_MAP_ACTIONS = (
    "look",
    "move_forward",
    "move_forward",
    "turn_right",
    "look",
)

_VIEWPORT_AXES = {
    "north": ((0, -1), (1, 0)),
    "east": ((1, 0), (0, 1)),
    "south": ((0, 1), (-1, 0)),
    "west": ((-1, 0), (0, -1)),
}


def create_observed_local_map(level_id: str) -> dict[str, Any]:
    return {
        "level_id": level_id,
        "known_cells": {},
        "agent_pos": None,
        "facing": None,
        "tick": 0,
    }


def update_observed_map_from_viewport(
    observed_map: dict[str, Any],
    state: dict[str, Any],
    viewport: list[list[str]],
) -> dict[str, Any]:
    before_count = len(observed_map["known_cells"])
    newly_observed_cells = []
    updated_cells = []
    for pos, symbol in iter_viewport_world_symbols(state, viewport):
        if symbol == "x":
            continue
        stored_symbol = "e" if symbol == "a" else symbol
        key = _cell_key(pos)
        previous = observed_map["known_cells"].get(key)
        if previous is None:
            observed_map["known_cells"][key] = stored_symbol
            newly_observed_cells.append({"pos": list(pos), "symbol": stored_symbol})
        elif previous != stored_symbol:
            observed_map["known_cells"][key] = stored_symbol
            updated_cells.append(
                {"pos": list(pos), "previous_symbol": previous, "symbol": stored_symbol}
            )
    observed_map["agent_pos"] = tuple(state["pos"])
    observed_map["facing"] = state["facing"]
    observed_map["tick"] = state["tick"]
    return {
        "known_cell_count_before": before_count,
        "known_cell_count_after": len(observed_map["known_cells"]),
        "newly_observed_cells": newly_observed_cells,
        "updated_cells": updated_cells,
        "observed_local_map": serialize_observed_local_map(observed_map),
    }


def iter_viewport_world_symbols(
    state: dict[str, Any],
    viewport: list[list[str]],
) -> list[tuple[tuple[int, int], str]]:
    facing = state["facing"]
    if facing not in _VIEWPORT_AXES:
        raise ValueError(f"unsupported facing: {facing}")
    forward_axis, right_axis = _VIEWPORT_AXES[facing]
    size = len(viewport)
    radius = size // 2
    center = tuple(state["pos"])
    symbols: list[tuple[tuple[int, int], str]] = []
    for row_index, row in enumerate(viewport):
        forward_offset = radius - row_index
        for col_index, symbol in enumerate(row):
            right_offset = col_index - radius
            pos = _add(center, _scale(forward_axis, forward_offset))
            pos = _add(pos, _scale(right_axis, right_offset))
            symbols.append((pos, symbol))
    return symbols


def serialize_observed_local_map(observed_map: dict[str, Any]) -> dict[str, Any]:
    known_cells = [
        {"pos": list(pos), "symbol": symbol}
        for pos, symbol in sorted(
            ((_parse_cell_key(key), symbol) for key, symbol in observed_map["known_cells"].items()),
            key=lambda item: (item[0][1], item[0][0]),
        )
    ]
    return {
        "level_id": observed_map["level_id"],
        "known_cell_count": len(known_cells),
        "known_cells": known_cells,
        "rendered_observed_map": render_observed_local_map(observed_map),
    }


def render_observed_local_map(observed_map: dict[str, Any]) -> list[str]:
    if not observed_map["known_cells"]:
        return []
    positions = [_parse_cell_key(key) for key in observed_map["known_cells"]]
    agent_pos = tuple(observed_map["agent_pos"]) if observed_map.get("agent_pos") is not None else None
    if agent_pos is not None:
        positions.append(agent_pos)
    min_x = min(pos[0] for pos in positions)
    max_x = max(pos[0] for pos in positions)
    min_y = min(pos[1] for pos in positions)
    max_y = max(pos[1] for pos in positions)
    rows = []
    for y in range(min_y, max_y + 1):
        row = []
        for x in range(min_x, max_x + 1):
            if agent_pos == (x, y):
                row.append("a")
            else:
                row.append(observed_map["known_cells"].get(_cell_key((x, y)), "x"))
        rows.append("".join(row))
    return rows


def run_simulated_vision_observed_map_demo(
    action_sequence: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    actions = tuple(action_sequence) if action_sequence is not None else DEFAULT_OBSERVED_MAP_ACTIONS
    level = create_simulated_vision_room()
    state = build_initial_simulated_vision_state(level)
    initial_state = _public_state(state)
    observed_map = create_observed_local_map(level["level_id"])
    action_trace = []
    observed_map_trace = []
    first_remembered_cell: tuple[int, int] | None = None
    first_remembered_symbol: str | None = None

    for action in actions:
        result = apply_simulated_vision_action(state, level, action)
        state = result["state"]
        trace = result["trace"]
        current_viewport = trace["viewport"]
        action_trace.append(
            {
                "tick": trace["tick"],
                "action": trace["action"],
                "before": trace["before"],
                "after": trace["after"],
                "result": trace["result"],
                "current_viewport": current_viewport,
                "failure_reasons": trace["failure_reasons"],
            }
        )
        update = update_observed_map_from_viewport(observed_map, state, current_viewport)
        if first_remembered_cell is None and update["newly_observed_cells"]:
            first = update["newly_observed_cells"][0]
            first_remembered_cell = tuple(first["pos"])
            first_remembered_symbol = first["symbol"]
        observed_map_trace.append(
            {
                "tick": trace["tick"],
                "action": trace["action"],
                "current_viewport": current_viewport,
                **update,
            }
        )

    checked_cell = _choose_persistence_check_cell(observed_map, state, action_trace[-1]["current_viewport"])
    if checked_cell is None:
        checked_cell = first_remembered_cell or (3, 3)
    previously_observed_symbol = observed_map["known_cells"].get(_cell_key(checked_cell), first_remembered_symbol)
    current_symbol = symbol_for_world_cell_in_viewport(checked_cell, state, action_trace[-1]["current_viewport"])
    remembered_symbol = observed_map["known_cells"].get(_cell_key(checked_cell))
    persistence_check = {
        "checked_cell": list(checked_cell),
        "previously_observed_symbol": previously_observed_symbol,
        "current_visibility": "in_current_viewport" if current_symbol != "x" else "not_in_current_viewport",
        "current_viewport_symbol_for_same_cell_or_x": current_symbol,
        "still_remembered_symbol": remembered_symbol,
        "passed": remembered_symbol == previously_observed_symbol and current_symbol == "x",
    }

    return {
        "command": "run-simulated-vision-observed-map-demo",
        "flow": "simulated_vision_observed_local_map_v0",
        "status": "ok",
        "level_id": level["level_id"],
        "initial_state": initial_state,
        "action_trace": action_trace,
        "observed_map_trace": observed_map_trace,
        "final_state": _public_state(state),
        "persistence_check": persistence_check,
        "boundary_check": {
            "simulated_vision_only": True,
            "structured_symbols_only": True,
            "real_image_vision": False,
            "llm_vision_used": False,
            "llm_planning_used": False,
            "pathfinding_used": False,
            "full_map_visible_to_agent": False,
            "observed_local_map_enabled": True,
            "observed_map_session_local": True,
            "x_does_not_erase_known_cells": True,
            "unseen_cells_not_inferred": True,
            "action_selection_modified": False,
            "goal_bias_modified": False,
            "route_planner_added": False,
            "item_seeking_added": False,
            "session_memory_write": False,
            "persistent_memory_write": False,
            "lesson_store_write": False,
            "memory_layer_write": False,
            "long_term_memory_write": False,
            "visual_understanding_claimed": False,
            "symbol_grounding_claimed": False,
        },
        "notes": [
            "current_viewport is what is visible now.",
            "observed_local_map is the session-local set of cells seen so far.",
            "x means currently unseen or unknown and does not erase known cells.",
        ],
    }


def symbol_for_world_cell_in_viewport(
    world_pos: tuple[int, int],
    state: dict[str, Any],
    viewport: list[list[str]],
) -> str:
    for pos, symbol in iter_viewport_world_symbols(state, viewport):
        if pos == world_pos:
            return symbol
    return "x"


def _choose_persistence_check_cell(
    observed_map: dict[str, Any],
    state: dict[str, Any],
    viewport: list[list[str]],
) -> tuple[int, int] | None:
    known_positions = sorted(
        (_parse_cell_key(key) for key in observed_map["known_cells"]),
        key=lambda pos: (pos[1], pos[0]),
    )
    for pos in known_positions:
        if symbol_for_world_cell_in_viewport(pos, state, viewport) == "x":
            return pos
    return None


def _public_state(state: dict[str, Any]) -> dict[str, Any]:
    return {"pos": list(state["pos"]), "facing": state["facing"]}


def _cell_key(pos: tuple[int, int]) -> str:
    return f"({pos[0]},{pos[1]})"


def _parse_cell_key(key: str) -> tuple[int, int]:
    left, right = key.strip("()").split(",", 1)
    return (int(left), int(right))


def _add(first: tuple[int, int], second: tuple[int, int]) -> tuple[int, int]:
    return (first[0] + second[0], first[1] + second[1])


def _scale(vector: tuple[int, int], amount: int) -> tuple[int, int]:
    return (vector[0] * amount, vector[1] * amount)
