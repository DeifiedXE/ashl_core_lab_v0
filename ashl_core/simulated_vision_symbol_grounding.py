"""Bounded symbolic grounding checks for simulated vision symbols."""

from __future__ import annotations

from typing import Any

from .simulated_vision_sandbox import (
    apply_simulated_vision_action,
    create_simulated_vision_room,
    render_viewport,
)


SCENARIO_ORDER = ("wall", "empty", "item")


def get_front_symbol_from_viewport(viewport: list[list[str]]) -> str:
    if len(viewport) < 1 or len(viewport[0]) < 2:
        raise ValueError("viewport must include a front-center cell")
    return viewport[0][1]


def build_symbol_grounding_scenarios(level: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    level = level or create_simulated_vision_room()
    return {
        "wall": {
            "scenario": "wall",
            "state": {"level_id": level["level_id"], "pos": (3, 1), "facing": "north", "tick": 0},
            "expected_front_symbol": "w",
            "expected_outcome": "blocked",
            "expected_failure_reasons": ["wall_blocked"],
            "expected_position_changed": False,
        },
        "empty": {
            "scenario": "empty",
            "state": {"level_id": level["level_id"], "pos": (3, 3), "facing": "north", "tick": 0},
            "expected_front_symbol": "e",
            "expected_outcome": "moved",
            "expected_failure_reasons": [],
            "expected_position_changed": True,
        },
        "item": {
            "scenario": "item",
            "state": {"level_id": level["level_id"], "pos": (4, 2), "facing": "north", "tick": 0},
            "expected_front_symbol": "i",
            "expected_outcome": "item_contact",
            "expected_failure_reasons": [],
            "expected_position_changed": True,
            "expected_item_grounding": True,
        },
    }


def run_symbol_grounding_check(scenario: str | None = None) -> dict[str, Any]:
    level = create_simulated_vision_room()
    scenarios = build_symbol_grounding_scenarios(level)
    scenario_names = SCENARIO_ORDER if scenario is None else (scenario,)
    invalid = [name for name in scenario_names if name not in scenarios]
    if invalid:
        raise ValueError(f"unsupported symbol grounding scenario: {invalid[0]}")

    scenario_results = [_run_single_scenario(level, scenarios[name]) for name in scenario_names]
    summary = _build_summary(scenario_results)
    return {
        "command": "run-simulated-vision-symbol-grounding-check",
        "flow": "simulated_vision_symbol_grounding_check_v0",
        "status": "ok",
        "level_id": level["level_id"],
        "scenario_results": scenario_results,
        "summary": summary,
        "boundary_check": {
            "simulated_vision_only": True,
            "structured_symbols_only": True,
            "real_image_vision": False,
            "llm_vision_used": False,
            "llm_planning_used": False,
            "pathfinding_used": False,
            "full_map_visible_to_agent": False,
            "symbol_grounding_check_enabled": True,
            "symbol_grounding_solved_claimed": False,
            "visual_understanding_claimed": False,
            "action_selection_modified": False,
            "goal_bias_modified": False,
            "route_planner_added": False,
            "item_seeking_added": False,
            "inventory_added": False,
            "session_memory_write": False,
            "persistent_memory_write": False,
            "lesson_store_write": False,
            "memory_layer_write": False,
            "long_term_memory_write": False,
        },
        "notes": [
            "This checks a bounded symbolic relation between visible symbols and immediate move_forward outcomes.",
            "front-center is viewport[0][1] for the 3x3 viewport where the top row is forward.",
            "This does not claim visual understanding or solved symbol grounding.",
        ],
    }


def _run_single_scenario(level: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    state = scenario["state"]
    viewport = render_viewport(state, level)
    front_symbol = get_front_symbol_from_viewport(viewport)
    action_result = apply_simulated_vision_action(state, level, "move_forward")
    trace = action_result["trace"]
    position_before = trace["before"]["pos"]
    position_after = trace["after"]["pos"]
    position_changed = position_before != position_after
    grounding_match = (
        front_symbol == scenario["expected_front_symbol"]
        and trace["result"] == scenario["expected_outcome"]
        and trace["failure_reasons"] == scenario["expected_failure_reasons"]
        and position_changed is scenario["expected_position_changed"]
    )
    effect_tags = []
    item_grounding_match = None
    if scenario["scenario"] == "item":
        effect_tags = ["item_contact"] if trace["result"] == "item_contact" else []
        item_grounding_match = front_symbol == "i" and "item_contact" in effect_tags
        grounding_match = grounding_match and item_grounding_match
    result = {
        "scenario": scenario["scenario"],
        "initial_pos": list(state["pos"]),
        "initial_facing": state["facing"],
        "front_symbol": front_symbol,
        "current_viewport": viewport,
        "action": "move_forward",
        "expected_outcome": scenario["expected_outcome"],
        "actual_outcome": trace["result"],
        "failure_reasons": trace["failure_reasons"],
        "position_before": position_before,
        "position_after": position_after,
        "position_changed": position_changed,
        "grounding_match": grounding_match,
    }
    if scenario["scenario"] == "item":
        result["expected_item_grounding"] = scenario["expected_item_grounding"]
        result["actual_item_grounding"] = item_grounding_match
        result["item_grounding_match"] = item_grounding_match
        result["effect_tags"] = effect_tags
    return result


def _build_summary(scenario_results: list[dict[str, Any]]) -> dict[str, Any]:
    passed_count = sum(1 for result in scenario_results if result["grounding_match"])
    by_name = {result["scenario"]: result for result in scenario_results}
    return {
        "scenario_count": len(scenario_results),
        "passed_count": passed_count,
        "failed_count": len(scenario_results) - passed_count,
        "wall_grounding_passed": by_name.get("wall", {}).get("grounding_match", False),
        "empty_grounding_passed": by_name.get("empty", {}).get("grounding_match", False),
        "item_grounding_passed": by_name.get("item", {}).get("grounding_match", False),
        "all_grounding_checks_passed": passed_count == len(scenario_results),
    }
