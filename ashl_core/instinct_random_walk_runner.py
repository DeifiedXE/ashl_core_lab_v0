"""Bounded seeded instinct/random walk runner for the larger symbolic sandbox."""

from __future__ import annotations

import random
from typing import Any

from .simulated_vision_larger_sandbox import (
    apply_larger_sandbox_action,
    build_initial_larger_sandbox_state,
    create_simulated_vision_larger_sandbox,
    front_symbol_from_larger_viewport,
    render_larger_sandbox_viewport,
)


INSTINCT_RANDOM_WALK_ACTION_WEIGHTS = {
    "look": 1,
    "turn_left": 1,
    "turn_right": 1,
    "move_forward": 2,
}


def run_instinct_random_walk(
    *,
    seed: int = 1,
    max_steps: int = 50,
    level_id: str = "simulated_vision_larger_sandbox_v0",
) -> dict[str, Any]:
    if max_steps < 0:
        raise ValueError("max_steps must be non-negative")

    level = create_simulated_vision_larger_sandbox()
    if level["level_id"] != level_id:
        raise ValueError(f"unsupported level_id: {level_id}")

    rng = random.Random(seed)
    actions = list(INSTINCT_RANDOM_WALK_ACTION_WEIGHTS)
    weights = [INSTINCT_RANDOM_WALK_ACTION_WEIGHTS[action] for action in actions]
    state = build_initial_larger_sandbox_state(level)
    initial_state = _public_state(state)
    visited_positions = {tuple(state["pos"])}
    step_trace: list[dict[str, Any]] = []
    experience_records: list[dict[str, Any]] = []

    for _ in range(max_steps):
        viewport_before = render_larger_sandbox_viewport(state, level)
        front_symbol_before = front_symbol_from_larger_viewport(viewport_before)
        selected_action = rng.choices(actions, weights=weights, k=1)[0]
        action_result = apply_larger_sandbox_action(state, level, selected_action)
        action_trace = action_result["trace"]
        state = action_result["state"]
        visited_positions.add(tuple(state["pos"]))
        position_changed = action_trace["before"]["pos"] != action_trace["after"]["pos"]
        experience_record = _build_experience_record(
            front_symbol=front_symbol_before,
            action=selected_action,
            outcome_type=action_trace["result"],
            failure_reasons=action_trace["failure_reasons"],
            effect_tags=action_trace["effect_tags"],
            position_changed=position_changed,
        )
        experience_records.append(experience_record)
        step_trace.append(
            {
                "tick": action_trace["tick"],
                "pos_before": action_trace["before"]["pos"],
                "facing_before": action_trace["before"]["facing"],
                "viewport_before": viewport_before,
                "front_symbol_before": front_symbol_before,
                "selected_action": selected_action,
                "result": action_trace["result"],
                "failure_reasons": action_trace["failure_reasons"],
                "effect_tags": action_trace["effect_tags"],
                "pos_after": action_trace["after"]["pos"],
                "facing_after": action_trace["after"]["facing"],
                "viewport_after": action_trace["viewport"],
                "experience_record": experience_record,
                "position_changed": position_changed,
            }
        )

    return {
        "command": "run-instinct-random-walk",
        "flow": "instinct_random_walk_runner_v0",
        "status": "ok",
        "level_id": level["level_id"],
        "seed": seed,
        "max_steps": max_steps,
        "action_weights": dict(INSTINCT_RANDOM_WALK_ACTION_WEIGHTS),
        "initial_state": initial_state,
        "step_trace": step_trace,
        "experience_summary": _summarize_experience(experience_records),
        "metrics": _build_metrics(step_trace, visited_positions, seed),
        "boundary_check": _boundary_check(),
        "notes": [
            "Round 1 bounded seeded random/instinct runner only.",
            "Action selection uses fixed weights and does not load prior experience.",
            "No reward bias, wall-experience influence, pathfinding, route planner, item collection, or long-term memory is used.",
            "Step traces and local experience outcomes are observation records, not proof of learning.",
        ],
    }


def _build_experience_record(
    *,
    front_symbol: str,
    action: str,
    outcome_type: str,
    failure_reasons: list[str],
    effect_tags: list[str],
    position_changed: bool,
) -> dict[str, Any]:
    return {
        "experience_key": f"front_symbol={front_symbol}|action={action}",
        "front_symbol": front_symbol,
        "action": action,
        "outcome_type": outcome_type,
        "failure_reasons": list(failure_reasons),
        "effect_tags": list(effect_tags),
        "position_changed": position_changed,
    }


def _summarize_experience(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "experience_count": len(records),
        "wall_blocked_experience_count": sum(1 for record in records if "wall_blocked" in record["failure_reasons"]),
        "item_contact_experience_count": sum(1 for record in records if "item_contact" in record["effect_tags"]),
        "passage_crossed_experience_count": sum(1 for record in records if "passage_crossed" in record["effect_tags"]),
        "exit_contact_experience_count": sum(1 for record in records if "exit_contact" in record["effect_tags"]),
        "experience_keys": sorted({record["experience_key"] for record in records}),
    }


def _build_metrics(step_trace: list[dict[str, Any]], visited_positions: set[tuple[int, int]], seed: int) -> dict[str, Any]:
    first_item_contact_step = next(
        (step["tick"] for step in step_trace if step["result"] == "item_contact"),
        None,
    )
    return {
        "step_count": len(step_trace),
        "look_count": sum(1 for step in step_trace if step["selected_action"] == "look"),
        "turn_left_count": sum(1 for step in step_trace if step["selected_action"] == "turn_left"),
        "turn_right_count": sum(1 for step in step_trace if step["selected_action"] == "turn_right"),
        "move_forward_count": sum(1 for step in step_trace if step["selected_action"] == "move_forward"),
        "wall_blocked_count": sum(1 for step in step_trace if "wall_blocked" in step["failure_reasons"]),
        "item_contact_count": sum(1 for step in step_trace if "item_contact" in step["effect_tags"]),
        "passage_crossed_count": sum(1 for step in step_trace if "passage_crossed" in step["effect_tags"]),
        "exit_contact_count": sum(1 for step in step_trace if "exit_contact" in step["effect_tags"]),
        "unique_positions_visited": len(visited_positions),
        "first_item_contact_step": first_item_contact_step,
        "random_seed": seed,
    }


def _boundary_check() -> dict[str, Any]:
    return {
        "instinct_random_walk_enabled": True,
        "round_1_only": True,
        "prior_experience_loaded": False,
        "experience_influence_enabled": False,
        "reward_bias_enabled": False,
        "dopamine_like_signal_enabled": False,
        "two_round_comparison_enabled": False,
        "simulated_vision_only": True,
        "larger_static_sandbox_used": True,
        "structured_symbols_only": True,
        "real_image_vision": False,
        "llm_vision_used": False,
        "llm_planning_used": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "full_map_visible_to_agent": False,
        "bounded_seeded_runner": True,
        "autonomous_action_loop_enabled": False,
        "item_collection_enabled": False,
        "exit_activation_enabled": False,
        "task_completion_enabled": False,
        "curiosity_enabled": False,
        "prediction_error_enabled": False,
        "place_memory_enabled": False,
        "home_sandbox_enabled": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "visual_understanding_claimed": False,
        "general_learning_claimed": False,
        "consciousness_claimed": False,
    }


def _public_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "pos": list(state["pos"]),
        "facing": state["facing"],
    }
