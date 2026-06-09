"""Bounded grounded action experience records for symbolic simulated vision."""

from __future__ import annotations

from typing import Any

from .session_working_memory import build_state_snapshot_key
from .simulated_vision_sandbox import apply_simulated_vision_action, create_simulated_vision_room, render_viewport
from .simulated_vision_symbol_grounding import (
    SCENARIO_ORDER,
    build_symbol_grounding_scenarios,
    get_front_symbol_from_viewport,
)


def build_grounded_action_experience_record(
    *,
    tick: int,
    level_id: str,
    state_before: dict[str, Any],
    viewport: list[list[str]],
    front_symbol: str,
    action: str,
    action_trace: dict[str, Any],
) -> dict[str, Any]:
    position_before = action_trace["before"]["pos"]
    position_after = action_trace["after"]["pos"]
    outcome_type = action_trace["result"]
    effect_tags = ["item_contact"] if outcome_type == "item_contact" else []
    state_snapshot = {
        "level_id": level_id,
        "agent_pos": position_before,
        "facing": state_before["facing"],
        "front_symbol": front_symbol,
        "viewport": viewport,
    }
    return {
        "tick": tick,
        "level_id": level_id,
        "experience_key": build_experience_key(front_symbol=front_symbol, action=action),
        "state_key": build_state_snapshot_key(state_snapshot),
        "state_snapshot": state_snapshot,
        "front_symbol": front_symbol,
        "action": action,
        "outcome_type": outcome_type,
        "outcome_detail": None,
        "failure_reasons": action_trace["failure_reasons"],
        "effect_tags": effect_tags,
        "position_before": position_before,
        "position_after": position_after,
        "position_changed": position_before != position_after,
        "viewport": viewport,
        "metadata": {
            "source": "grounded_action_experience_v0",
            "chain": "see -> interact -> outcome -> experience record",
            "raw_result": action_trace["result"],
            "front_symbol_source": "current_viewport_front_center",
            "experience_used_for_decision": False,
        },
    }


def build_experience_key(*, front_symbol: str, action: str) -> str:
    return f"front_symbol={front_symbol}|action={action}"


def run_grounded_action_experience_check(scenario: str | None = None) -> dict[str, Any]:
    level = create_simulated_vision_room()
    scenarios = build_symbol_grounding_scenarios(level)
    scenario_names = SCENARIO_ORDER if scenario is None else (scenario,)
    invalid = [name for name in scenario_names if name not in scenarios]
    if invalid:
        raise ValueError(f"unsupported grounded action experience scenario: {invalid[0]}")

    scenario_results = []
    experience_records = []
    for tick, scenario_name in enumerate(scenario_names, start=1):
        result = _run_single_experience_scenario(
            tick=tick,
            level=level,
            scenario=scenarios[scenario_name],
        )
        scenario_results.append(result["scenario_result"])
        experience_records.append(result["experience_record"])

    experience_summary = _build_experience_summary(experience_records)
    return {
        "command": "run-grounded-action-experience-check",
        "flow": "grounded_action_experience_v0",
        "status": "ok",
        "level_id": level["level_id"],
        "scenario_results": scenario_results,
        "experience_records": experience_records,
        "experience_summary": experience_summary,
        "boundary_check": {
            "simulated_vision_only": True,
            "structured_symbols_only": True,
            "real_image_vision": False,
            "llm_vision_used": False,
            "llm_planning_used": False,
            "pathfinding_used": False,
            "route_planner_added": False,
            "full_map_visible_to_agent": False,
            "grounded_action_experience_enabled": True,
            "grounded_action_influence_enabled": False,
            "action_selection_modified": False,
            "experience_used_for_decision": False,
            "session_local_only": True,
            "session_memory_write": False,
            "persistent_memory_write": False,
            "lesson_store_write": False,
            "memory_layer_write": False,
            "long_term_memory_write": False,
            "item_seeking_added": False,
            "item_pickup_added": False,
            "inventory_added": False,
            "visual_understanding_claimed": False,
            "symbol_grounding_solved_claimed": False,
            "general_learning_claimed": False,
        },
        "notes": [
            "This records bounded grounded action experiences: visible front symbol + attempted action + immediate outcome.",
            "The current chain is see -> interact -> outcome -> experience record.",
            "Experience is not used to modify action selection.",
        ],
    }


def _run_single_experience_scenario(
    *,
    tick: int,
    level: dict[str, Any],
    scenario: dict[str, Any],
) -> dict[str, Any]:
    state = scenario["state"]
    viewport = render_viewport(state, level)
    front_symbol = get_front_symbol_from_viewport(viewport)
    action = "move_forward"
    action_result = apply_simulated_vision_action(state, level, action)
    action_trace = action_result["trace"]
    experience_record = build_grounded_action_experience_record(
        tick=tick,
        level_id=level["level_id"],
        state_before=state,
        viewport=viewport,
        front_symbol=front_symbol,
        action=action,
        action_trace=action_trace,
    )
    expected_outcome = scenario["expected_outcome"]
    if scenario["scenario"] == "item":
        experience_match = (
            front_symbol == "i"
            and experience_record["outcome_type"] == "item_contact"
            and "item_contact" in experience_record["effect_tags"]
        )
    else:
        experience_match = (
            front_symbol == scenario["expected_front_symbol"]
            and experience_record["outcome_type"] == expected_outcome
            and experience_record["failure_reasons"] == scenario["expected_failure_reasons"]
            and experience_record["position_changed"] is scenario["expected_position_changed"]
        )
    return {
        "scenario_result": {
            "scenario": scenario["scenario"],
            "initial_pos": list(state["pos"]),
            "initial_facing": state["facing"],
            "current_viewport": viewport,
            "front_symbol": front_symbol,
            "action": action,
            "expected_outcome": expected_outcome,
            "actual_outcome": action_trace["result"],
            "failure_reasons": action_trace["failure_reasons"],
            "effect_tags": experience_record["effect_tags"],
            "position_before": action_trace["before"]["pos"],
            "position_after": action_trace["after"]["pos"],
            "position_changed": experience_record["position_changed"],
            "experience_recorded": True,
            "experience_key": experience_record["experience_key"],
            "grounded_experience_match": experience_match,
        },
        "experience_record": experience_record,
    }


def _build_experience_summary(experience_records: list[dict[str, Any]]) -> dict[str, Any]:
    keys = {record["experience_key"] for record in experience_records}
    records_have_front_symbol = all(record.get("front_symbol") for record in experience_records)
    records_have_action = all(record.get("action") for record in experience_records)
    records_have_outcome = all(record.get("outcome_type") for record in experience_records)
    return {
        "experience_count": len(experience_records),
        "wall_experience_recorded": "front_symbol=w|action=move_forward" in keys,
        "empty_experience_recorded": "front_symbol=e|action=move_forward" in keys,
        "item_experience_recorded": "front_symbol=i|action=move_forward" in keys,
        "experience_records_have_front_symbol": records_have_front_symbol,
        "experience_records_have_action": records_have_action,
        "experience_records_have_outcome": records_have_outcome,
        "all_grounded_action_experiences_recorded": (
            len(experience_records) > 0
            and records_have_front_symbol
            and records_have_action
            and records_have_outcome
            and all(record.get("experience_key") for record in experience_records)
        ),
    }
