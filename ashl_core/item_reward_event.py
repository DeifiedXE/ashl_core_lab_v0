"""Non-subjective reward event data for item contact."""

from __future__ import annotations

from typing import Any

from .simulated_vision_larger_sandbox import (
    apply_larger_sandbox_action,
    create_simulated_vision_larger_sandbox,
    front_symbol_from_larger_viewport,
    render_larger_sandbox_viewport,
)


SUPPORTED_SCENARIOS = frozenset({"item"})


def run_item_reward_event_check(scenario: str | None = "item") -> dict[str, Any]:
    scenario_name = scenario or "item"
    if scenario_name not in SUPPORTED_SCENARIOS:
        raise ValueError(f"unsupported item reward event scenario: {scenario_name}")

    level = create_simulated_vision_larger_sandbox()
    scenario_result = _run_item_contact_scenario(level)
    reward_event = build_item_reward_event(
        tick=1,
        level_id=level["level_id"],
        scenario_result=scenario_result,
    )
    reward_summary = _build_reward_summary([reward_event])
    return {
        "command": "run-item-reward-event-check",
        "flow": "item_reward_event_v0",
        "status": "ok" if scenario_result["actual_outcome"] == "item_contact" else "failed",
        "level_id": level["level_id"],
        "scenario_result": scenario_result,
        "reward_event": reward_event,
        "reward_summary": reward_summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Item contact creates a non-subjective reward_event data record.",
            "dopamine_like_signal is a data field only.",
            "No reward-biased action tendency, item seeking, item collection, pathfinding, or long-term memory is added.",
        ],
    }


def build_item_reward_event(*, tick: int, level_id: str, scenario_result: dict[str, Any]) -> dict[str, Any]:
    position_after = list(scenario_result["position_after"])
    return {
        "event_id": f"item_reward:{level_id}:{tick}:{position_after[0]}_{position_after[1]}",
        "tick": tick,
        "level_id": level_id,
        "source": "grounded_action_experience",
        "trigger": "item_contact",
        "front_symbol": scenario_result["front_symbol"],
        "action": scenario_result["action"],
        "outcome_type": scenario_result["actual_outcome"],
        "effect_tags": list(scenario_result["effect_tags"]),
        "reward_type": "item_contact_reward",
        "reward_value": 1.0,
        "dopamine_like_signal": True,
        "non_subjective": True,
        "metadata": {
            "position_before": list(scenario_result["position_before"]),
            "position_after": position_after,
            "facing": scenario_result["initial_facing"],
            "viewport": scenario_result["current_viewport"],
        },
    }


def _run_item_contact_scenario(level: dict[str, Any]) -> dict[str, Any]:
    state = {
        "level_id": level["level_id"],
        "pos": (8, 2),
        "facing": "north",
        "tick": 0,
    }
    current_viewport = render_larger_sandbox_viewport(state, level)
    front_symbol = front_symbol_from_larger_viewport(current_viewport)
    action_result = apply_larger_sandbox_action(state, level, "move_forward")
    trace = action_result["trace"]
    position_before = trace["before"]["pos"]
    position_after = trace["after"]["pos"]
    return {
        "scenario": "item_contact_reward",
        "initial_pos": list(state["pos"]),
        "initial_facing": state["facing"],
        "current_viewport": current_viewport,
        "front_symbol": front_symbol,
        "action": "move_forward",
        "actual_outcome": trace["result"],
        "failure_reasons": list(trace["failure_reasons"]),
        "effect_tags": list(trace["effect_tags"]),
        "position_before": position_before,
        "position_after": position_after,
        "position_changed": position_before != position_after,
    }


def _build_reward_summary(reward_events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "reward_event_created": bool(reward_events),
        "reward_event_count": len(reward_events),
        "item_contact_reward_count": sum(
            1 for event in reward_events if event["reward_type"] == "item_contact_reward"
        ),
        "dopamine_like_signal_count": sum(1 for event in reward_events if event["dopamine_like_signal"]),
        "total_reward_value": sum(event["reward_value"] for event in reward_events),
        "non_subjective_reward_events": sum(1 for event in reward_events if event["non_subjective"]),
    }


def _boundary_check() -> dict[str, Any]:
    return {
        "item_reward_event_enabled": True,
        "dopamine_like_signal_enabled": True,
        "reward_bias_enabled": False,
        "item_seeking_enabled": False,
        "reward_used_for_action_selection": False,
        "simulated_vision_only": True,
        "larger_static_sandbox_used": True,
        "structured_symbols_only": True,
        "real_image_vision": False,
        "llm_vision_used": False,
        "llm_planning_used": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "full_map_visible_to_agent": False,
        "item_collection_enabled": False,
        "item_pickup_enabled": False,
        "inventory_enabled": False,
        "exit_activation_enabled": False,
        "task_completion_enabled": False,
        "curiosity_enabled": False,
        "prediction_error_enabled": False,
        "place_memory_enabled": False,
        "home_sandbox_enabled": False,
        "session_local_only": True,
        "persistent_memory_write": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "pleasure_claimed": False,
        "desire_claimed": False,
        "self_awareness_claimed": False,
        "visual_understanding_claimed": False,
        "symbol_grounding_solved_claimed": False,
        "general_learning_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }
