"""Controlled two-round comparison for wall experience and item reward tendency."""

from __future__ import annotations

from typing import Any

from .reward_biased_random_walk_check import DEFAULT_LEVEL_ID, run_reward_biased_random_walk_check
from .wall_experience_influence import run_wall_experience_influence_check


def run_two_round_instinct_reward_comparison(
    *,
    seed: int = 1,
    trials: int = 20,
    level_id: str = DEFAULT_LEVEL_ID,
) -> dict[str, Any]:
    if trials < 0:
        raise ValueError("trials must be non-negative")

    wall_check = run_wall_experience_influence_check(seed=seed)
    item_check = run_reward_biased_random_walk_check(seed=seed, trials=trials, level_id=level_id)
    if wall_check["level_id"] != level_id:
        raise ValueError(f"unsupported level_id for two-round instinct reward comparison: {level_id}")

    round1 = {
        "wall_control": _round1_wall_control(wall_check["control_result"]),
        "item_control": _round1_item_control(item_check["no_reward_result"]),
    }
    round2 = {
        "wall_with_experience": _round2_wall_with_experience(wall_check["influence_result"]),
        "item_with_reward": _round2_item_with_reward(item_check["with_reward_result"]),
    }
    comparison = _build_comparison(round1, round2)
    return {
        "command": "run-two-round-instinct-reward-comparison",
        "flow": "two_round_instinct_reward_comparison_v0",
        "status": "ok" if comparison["all_two_round_checks_passed"] else "failed",
        "level_id": level_id,
        "seed": seed,
        "trials": trials,
        "round1": round1,
        "round2": round2,
        "comparison": comparison,
        "boundary_check": _boundary_check(),
        "notes": [
            "Round 1 uses no carried wall experience and no carried item reward.",
            "Round 2 carries wall_blocked experience and item_contact_reward for controlled immediate scenarios.",
            "This comparison does not test whole-map item seeking, pathfinding, item collection, or long-term memory.",
        ],
    }


def _round1_wall_control(control_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "front_symbol": control_result["front_symbol"],
        "candidate_action": control_result["candidate_action"],
        "selected_action": control_result["selected_action"],
        "experience_used_for_decision": control_result["experience_used_for_decision"],
        "influence_applied": control_result["influence_applied"],
    }


def _round2_wall_with_experience(influence_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "carried_wall_experience": True,
        "front_symbol": influence_result["front_symbol"],
        "candidate_action": influence_result["candidate_action"],
        "selected_action": influence_result["selected_action"],
        "experience_used_for_decision": influence_result["experience_used_for_decision"],
        "influence_applied": influence_result["influence_applied"],
        "influence_type": influence_result["influence_type"],
    }


def _round1_item_control(no_reward_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "front_symbol": no_reward_result["front_symbol"],
        "candidate_action": "move_forward",
        "reward_bias_applied": no_reward_result["reward_bias_applied"],
        "move_forward_score": no_reward_result["move_forward_score"],
        "move_forward_selected_count": no_reward_result["move_forward_selected_count"],
    }


def _round2_item_with_reward(with_reward_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "carried_item_reward": True,
        "front_symbol": with_reward_result["front_symbol"],
        "candidate_action": "move_forward",
        "reward_bias_applied": with_reward_result["reward_bias_applied"],
        "reward_used_for_decision": with_reward_result["matching_reward_event_found"],
        "move_forward_score": with_reward_result["move_forward_score"],
        "reward_bias_delta": with_reward_result["reward_bias_delta"],
        "move_forward_selected_count": with_reward_result["move_forward_selected_count"],
    }


def _build_comparison(round1: dict[str, Any], round2: dict[str, Any]) -> dict[str, Any]:
    wall_round1 = round1["wall_control"]
    wall_round2 = round2["wall_with_experience"]
    item_round1 = round1["item_control"]
    item_round2 = round2["item_with_reward"]
    score_delta = item_round2["move_forward_score"] - item_round1["move_forward_score"]
    selected_delta = item_round2["move_forward_selected_count"] - item_round1["move_forward_selected_count"]
    wall_round2_improved = (
        wall_round1["selected_action"] == "move_forward"
        and wall_round1["experience_used_for_decision"] is False
        and wall_round2["carried_wall_experience"] is True
        and wall_round2["selected_action"] != "move_forward"
        and wall_round2["experience_used_for_decision"] is True
        and wall_round2["influence_applied"] is True
        and wall_round2["influence_type"] == "suppress"
    )
    item_round2_bias_improved = (
        item_round1["reward_bias_applied"] is False
        and item_round2["carried_item_reward"] is True
        and item_round2["reward_bias_applied"] is True
        and item_round2["reward_used_for_decision"] is True
        and score_delta > 0.0
        and selected_delta >= 0
    )
    return {
        "wall_round2_improved": wall_round2_improved,
        "item_round2_bias_improved": item_round2_bias_improved,
        "move_forward_score_delta_for_i": score_delta,
        "move_forward_selected_count_delta_for_i": selected_delta,
        "round2_uses_carried_experience": wall_round2["carried_wall_experience"]
        and wall_round2["experience_used_for_decision"],
        "round2_uses_carried_reward": item_round2["carried_item_reward"] and item_round2["reward_used_for_decision"],
        "all_two_round_checks_passed": wall_round2_improved and item_round2_bias_improved,
    }


def _boundary_check() -> dict[str, Any]:
    return {
        "two_round_instinct_reward_comparison_enabled": True,
        "controlled_immediate_tendency_comparison": True,
        "whole_map_item_seeking_claimed": False,
        "whole_map_random_walk_improvement_claimed": False,
        "wall_experience_influence_enabled": True,
        "item_reward_event_enabled": True,
        "reward_biased_action_tendency_enabled": True,
        "reward_biased_random_walk_check_enabled": True,
        "requires_prior_wall_experience_for_wall_influence": True,
        "requires_prior_reward_for_item_bias": True,
        "no_experience_controls_used": True,
        "item_seeking_enabled": False,
        "route_planner_added": False,
        "pathfinding_used": False,
        "observed_map_route_use": False,
        "full_map_visible_to_agent": False,
        "action_selection_modified_in_this_check_only": True,
        "existing_navigation_action_selection_modified": False,
        "random_walk_base_behavior_modified": False,
        "simulated_vision_only": True,
        "larger_static_sandbox_used": True,
        "structured_symbols_only": True,
        "real_image_vision": False,
        "llm_vision_used": False,
        "llm_planning_used": False,
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
