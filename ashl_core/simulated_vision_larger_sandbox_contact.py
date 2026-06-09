"""Symbol contact smoke for the larger static simulated vision sandbox."""

from __future__ import annotations

from typing import Any

from .simulated_vision_larger_sandbox import (
    apply_larger_sandbox_action,
    create_simulated_vision_larger_sandbox,
    render_larger_sandbox_viewport,
)
from .simulated_vision_sandbox import (
    FIRST_PERSON_AGENT_VIEWPORT_POSITION,
    FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION,
    FIRST_PERSON_FRONT_SYMBOL_POSITION,
)


SCENARIO_ORDER = ("doorway", "item", "exit")
SCENARIOS = {
    "doorway": {
        "scenario": "doorway_d",
        "target_symbol": "d",
        "state": {"pos": (3, 2), "facing": "east", "tick": 0},
        "expected_outcome": "moved",
        "expected_effect_tag": "passage_crossed",
    },
    "item": {
        "scenario": "item_i",
        "target_symbol": "i",
        "state": {"pos": (8, 2), "facing": "north", "tick": 0},
        "expected_outcome": "item_contact",
        "expected_effect_tag": "item_contact",
    },
    "exit": {
        "scenario": "exit_g",
        "target_symbol": "g",
        "state": {"pos": (10, 7), "facing": "east", "tick": 0},
        "expected_outcome": "exit_contact",
        "expected_effect_tag": "exit_contact",
    },
}


def run_larger_sandbox_symbol_contact_smoke(scenario: str | None = None) -> dict[str, Any]:
    level = create_simulated_vision_larger_sandbox()
    scenario_names = SCENARIO_ORDER if scenario is None else (scenario,)
    invalid = [name for name in scenario_names if name not in SCENARIOS]
    if invalid:
        raise ValueError(f"unsupported larger sandbox contact scenario: {invalid[0]}")

    scenario_results = [_run_single_scenario(level, SCENARIOS[name]) for name in scenario_names]
    summary = _build_summary(scenario_results)
    return {
        "command": "run-larger-sandbox-symbol-contact-smoke",
        "flow": "larger_sandbox_symbol_contact_smoke_v0",
        "status": "ok",
        "level_id": level["level_id"],
        "scenario_results": scenario_results,
        "summary": summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "This smoke uses controlled scenario snapshots, not route planning.",
            "It checks immediate contact outcomes for d/i/g in the larger static sandbox.",
            "D remains a passable symbol, not a semantic room boundary given to the agent.",
            "No item collection, exit activation, task completion, curiosity, prediction error, or pathfinding is added.",
        ],
    }


def _run_single_scenario(level: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    state = _state_with_level(level, scenario["state"])
    current_viewport = render_larger_sandbox_viewport(state, level)
    action_result = apply_larger_sandbox_action(state, level, "move_forward")
    trace = action_result["trace"]
    position_before = trace["before"]["pos"]
    position_after = trace["after"]["pos"]
    expected_effect_tag = scenario["expected_effect_tag"]
    contact_match = (
        trace["front_symbol"] == scenario["target_symbol"]
        and trace["result"] == scenario["expected_outcome"]
        and trace["failure_reasons"] == []
        and expected_effect_tag in trace["effect_tags"]
        and position_before != position_after
    )
    return {
        "scenario": scenario["scenario"],
        "target_symbol": scenario["target_symbol"],
        "initial_pos": list(state["pos"]),
        "initial_facing": state["facing"],
        "current_viewport": current_viewport,
        "front_symbol": trace["front_symbol"],
        "action": "move_forward",
        "expected_outcome": scenario["expected_outcome"],
        "actual_outcome": trace["result"],
        "failure_reasons": trace["failure_reasons"],
        "effect_tags": trace["effect_tags"],
        "position_before": position_before,
        "position_after": position_after,
        "position_changed": position_before != position_after,
        "contact_match": contact_match,
    }


def _build_summary(scenario_results: list[dict[str, Any]]) -> dict[str, Any]:
    passed_count = sum(1 for result in scenario_results if result["contact_match"])
    by_name = {result["scenario"]: result for result in scenario_results}
    return {
        "scenario_count": len(scenario_results),
        "passed_count": passed_count,
        "failed_count": len(scenario_results) - passed_count,
        "doorway_contact_passed": by_name.get("doorway_d", {}).get("contact_match", False),
        "item_contact_passed": by_name.get("item_i", {}).get("contact_match", False),
        "exit_contact_passed": by_name.get("exit_g", {}).get("contact_match", False),
        "all_larger_sandbox_symbol_contact_checks_passed": passed_count == len(scenario_results),
    }


def _boundary_check() -> dict[str, Any]:
    return {
        "simulated_vision_only": True,
        "larger_static_sandbox_used": True,
        "symbol_contact_smoke_enabled": True,
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
        "doorway_contact_checked": True,
        "doorway_semantic_boundary_given_to_agent": False,
        "item_symbol_supported": True,
        "item_contact_checked": True,
        "item_collection_enabled": False,
        "item_pickup_enabled": False,
        "inventory_enabled": False,
        "exit_placeholder_supported": True,
        "exit_contact_checked": True,
        "exit_conditional_spawn_enabled": False,
        "task_completion_enabled": False,
        "win_condition_enabled": False,
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


def _state_with_level(level: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return {
        "level_id": level["level_id"],
        "pos": tuple(state["pos"]),
        "facing": state["facing"],
        "tick": state["tick"],
    }
