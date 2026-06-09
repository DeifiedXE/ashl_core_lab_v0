"""Observed-map smoke for the larger static simulated vision sandbox."""

from __future__ import annotations

from typing import Any

from .simulated_vision_larger_sandbox import (
    create_simulated_vision_larger_sandbox,
    build_larger_sandbox_map_summary,
    render_larger_sandbox_viewport,
)
from .simulated_vision_observed_map import (
    create_observed_local_map,
    serialize_observed_local_map,
    symbol_for_world_cell_in_viewport,
    update_observed_map_from_viewport,
)
from .simulated_vision_sandbox import (
    FIRST_PERSON_AGENT_VIEWPORT_POSITION,
    FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION,
    FIRST_PERSON_FRONT_SYMBOL_POSITION,
)


SCENARIO_DEFINITIONS = (
    {
        "scenario": "doorway_d",
        "target_symbol": "d",
        "state": {"pos": (3, 2), "facing": "east", "tick": 0},
        "observed_world_pos": (4, 2),
        "view_changed_state": {"pos": (2, 2), "facing": "north", "tick": 1},
    },
    {
        "scenario": "item_i",
        "target_symbol": "i",
        "state": {"pos": (8, 2), "facing": "north", "tick": 0},
        "observed_world_pos": (8, 1),
        "view_changed_state": {"pos": (2, 2), "facing": "north", "tick": 1},
    },
    {
        "scenario": "exit_g",
        "target_symbol": "g",
        "state": {"pos": (10, 7), "facing": "east", "tick": 0},
        "observed_world_pos": (11, 7),
        "view_changed_state": {"pos": (2, 2), "facing": "north", "tick": 1},
    },
)


def run_larger_sandbox_observed_map_smoke(
    action_sequence: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    # action_sequence is accepted for CLI consistency; v0 uses controlled snapshots, not route execution.
    _ = action_sequence
    level = create_simulated_vision_larger_sandbox()
    map_summary = build_larger_sandbox_map_summary(level)
    observed_map = create_observed_local_map(level["level_id"])

    scenario_results = []
    persistence_checks = []
    for definition in SCENARIO_DEFINITIONS:
        result, persistence_check = _run_scenario(level, observed_map, definition)
        scenario_results.append(result)
        persistence_checks.append(persistence_check)

    serialized_map = serialize_observed_local_map(observed_map)
    remembered_symbols = sorted({cell["symbol"] for cell in serialized_map["known_cells"]})
    total_map_cells = map_summary["width"] * map_summary["height"]
    observed_map_summary = {
        "known_cell_count": serialized_map["known_cell_count"],
        "remembered_symbols": remembered_symbols,
        "remembered_d_count": _count_symbol(serialized_map, "d"),
        "remembered_i_count": _count_symbol(serialized_map, "i"),
        "remembered_g_count": _count_symbol(serialized_map, "g"),
        "unseen_cells_not_inferred": serialized_map["known_cell_count"] < total_map_cells,
        "x_does_not_erase_known_cells": all(check["passed"] for check in persistence_checks),
    }
    boundary = _boundary_check(
        doorway_remembered=observed_map_summary["remembered_d_count"] > 0,
        item_remembered=observed_map_summary["remembered_i_count"] > 0,
        exit_remembered=observed_map_summary["remembered_g_count"] > 0,
        x_does_not_erase=observed_map_summary["x_does_not_erase_known_cells"],
        unseen_not_inferred=observed_map_summary["unseen_cells_not_inferred"],
    )
    return {
        "command": "run-larger-sandbox-observed-map-smoke",
        "flow": "larger_sandbox_observed_map_smoke_v0",
        "status": "ok",
        "level_id": level["level_id"],
        "map_summary": {
            "width": map_summary["width"],
            "height": map_summary["height"],
            "item_count": map_summary["item_count"],
            "doorway_count": map_summary["doorway_count"],
            "exit_count": map_summary["exit_count"],
        },
        "scenario_results": scenario_results,
        "observed_map_summary": observed_map_summary,
        "persistence_checks": persistence_checks,
        "boundary_check": boundary,
        "notes": [
            "This smoke uses controlled scenario snapshots, not route planning.",
            "observed_local_map records d/i/g from current first-person viewports.",
            "x means not visible now and does not erase previously observed d/i/g cells.",
            "No item collection, exit activation, curiosity, prediction error, pathfinding, or place memory is added.",
        ],
    }


def _run_scenario(
    level: dict[str, Any],
    observed_map: dict[str, Any],
    definition: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    state = _state_with_level(level, definition["state"])
    target_symbol = definition["target_symbol"]
    observed_world_pos = definition["observed_world_pos"]
    current_viewport = render_larger_sandbox_viewport(state, level)
    known_before = len(observed_map["known_cells"])
    update = update_observed_map_from_viewport(observed_map, state, current_viewport)
    remembered_symbol = observed_map["known_cells"].get(_cell_key(observed_world_pos))

    view_changed_state = _state_with_level(level, definition["view_changed_state"])
    view_changed_viewport = render_larger_sandbox_viewport(view_changed_state, level)
    update_observed_map_from_viewport(observed_map, view_changed_state, view_changed_viewport)
    current_symbol = symbol_for_world_cell_in_viewport(observed_world_pos, view_changed_state, view_changed_viewport)
    still_remembered_symbol = observed_map["known_cells"].get(_cell_key(observed_world_pos))
    visible_symbol_found = target_symbol in {symbol for row in current_viewport for symbol in row}
    still_remembered = still_remembered_symbol == target_symbol and current_symbol == "x"
    scenario_result = {
        "scenario": definition["scenario"],
        "target_symbol": target_symbol,
        "initial_state": _public_state(state),
        "current_viewport": current_viewport,
        "visible_symbol_found": visible_symbol_found,
        "observed_world_pos": list(observed_world_pos),
        "known_cell_count_before": known_before,
        "known_cell_count_after": update["known_cell_count_after"],
        "view_changed_state": _public_state(view_changed_state),
        "view_changed_viewport": view_changed_viewport,
        "still_remembered": still_remembered,
        "passed": visible_symbol_found and remembered_symbol == target_symbol and still_remembered,
    }
    persistence_check = {
        "symbol": target_symbol,
        "checked_cell": list(observed_world_pos),
        "previously_observed_symbol": remembered_symbol,
        "current_visibility": "in_current_viewport" if current_symbol != "x" else "not_in_current_viewport",
        "still_remembered_symbol": still_remembered_symbol,
        "passed": still_remembered,
    }
    return scenario_result, persistence_check


def _boundary_check(
    *,
    doorway_remembered: bool,
    item_remembered: bool,
    exit_remembered: bool,
    x_does_not_erase: bool,
    unseen_not_inferred: bool,
) -> dict[str, Any]:
    return {
        "simulated_vision_only": True,
        "larger_static_sandbox_used": True,
        "observed_local_map_enabled": True,
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
        "doorway_remembered": doorway_remembered,
        "item_symbol_supported": True,
        "item_remembered": item_remembered,
        "exit_placeholder_supported": True,
        "exit_remembered": exit_remembered,
        "x_does_not_erase_known_cells": x_does_not_erase,
        "unseen_cells_not_inferred": unseen_not_inferred,
        "item_collection_enabled": False,
        "exit_conditional_spawn_enabled": False,
        "task_completion_enabled": False,
        "curiosity_enabled": False,
        "prediction_error_enabled": False,
        "place_memory_enabled": False,
        "home_sandbox_enabled": False,
        "action_selection_modified": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "visual_understanding_claimed": False,
        "symbol_grounding_solved_claimed": False,
        "general_learning_claimed": False,
    }


def _count_symbol(serialized_map: dict[str, Any], symbol: str) -> int:
    return sum(1 for cell in serialized_map["known_cells"] if cell["symbol"] == symbol)


def _state_with_level(level: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return {
        "level_id": level["level_id"],
        "pos": tuple(state["pos"]),
        "facing": state["facing"],
        "tick": state["tick"],
    }


def _public_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "pos": list(state["pos"]),
        "facing": state["facing"],
    }


def _cell_key(pos: tuple[int, int]) -> str:
    return f"({pos[0]},{pos[1]})"
