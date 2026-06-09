"""Controlled reward-biased random-walk-like action selection check."""

from __future__ import annotations

import random
from typing import Any

from .item_reward_event import run_item_reward_event_check
from .reward_biased_action_tendency import (
    BASE_ACTION_SCORE,
    ITEM_REWARD_BIAS_DELTA,
    build_reward_store,
    lookup_item_reward,
)


DEFAULT_LEVEL_ID = "simulated_vision_larger_sandbox_v0"
ACTION_ORDER = ("look", "turn_left", "turn_right", "move_forward")
BASE_ACTION_SCORES = {action: BASE_ACTION_SCORE for action in ACTION_ORDER}


def run_reward_biased_random_walk_check(
    *,
    seed: int = 1,
    trials: int = 20,
    level_id: str = DEFAULT_LEVEL_ID,
) -> dict[str, Any]:
    if trials < 0:
        raise ValueError("trials must be non-negative")

    reward_check = run_item_reward_event_check()
    if reward_check["level_id"] != level_id:
        raise ValueError(f"unsupported level_id for reward-biased random walk check: {level_id}")

    reward_event = reward_check["reward_event"]
    reward_store = build_reward_store([reward_event])
    no_reward_result = _run_condition(
        front_symbol="i",
        reward_store={},
        seed=seed,
        trials=trials,
        reward_event_count=0,
    )
    no_reward_result["reward_store_empty"] = True
    no_reward_result.pop("matching_reward_event_found")
    no_reward_result.pop("reward_bias_delta")

    with_reward_result = _run_condition(
        front_symbol="i",
        reward_store=reward_store,
        seed=seed,
        trials=trials,
        reward_event_count=1,
    )

    comparison = _build_comparison(no_reward_result, with_reward_result)
    return {
        "command": "run-reward-biased-random-walk-check",
        "flow": "reward_biased_random_walk_check_v0",
        "status": "ok" if comparison["reward_bias_effect_observed"] else "failed",
        "level_id": level_id,
        "seed": seed,
        "trials": trials,
        "no_reward_result": no_reward_result,
        "with_reward_result": with_reward_result,
        "comparison": comparison,
        "boundary_check": _boundary_check(),
        "notes": [
            "This check uses a controlled immediate front_symbol=i scenario only.",
            "Prior item_contact_reward increases move_forward score for this local candidate-action sample.",
            "This does not test whole-map item seeking, pathfinding, item collection, or long-term memory.",
        ],
    }


def score_actions_for_front_symbol(
    front_symbol: str,
    reward_store: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    action_scores = dict(BASE_ACTION_SCORES)
    matching_reward = lookup_item_reward(reward_store, front_symbol, "move_forward")
    matching_reward_event_found = matching_reward is not None
    reward_bias_delta = ITEM_REWARD_BIAS_DELTA if matching_reward_event_found else 0.0
    if matching_reward_event_found:
        action_scores["move_forward"] += reward_bias_delta
    return {
        "front_symbol": front_symbol,
        "matching_reward_event_found": matching_reward_event_found,
        "reward_bias_applied": matching_reward_event_found,
        "reward_bias_delta": reward_bias_delta,
        "action_scores": action_scores,
        "move_forward_score": action_scores["move_forward"],
    }


def sample_actions_from_scores(
    action_scores: dict[str, float],
    *,
    seed: int,
    trials: int,
) -> dict[str, Any]:
    rng = random.Random(seed)
    selected_action_counts = {action: 0 for action in ACTION_ORDER}
    selected_actions = []
    total_score = sum(action_scores[action] for action in ACTION_ORDER)

    for _ in range(trials):
        threshold = rng.random() * total_score
        cumulative = 0.0
        for action in ACTION_ORDER:
            cumulative += action_scores[action]
            if threshold < cumulative:
                selected_action_counts[action] += 1
                selected_actions.append(action)
                break

    return {
        "selected_actions": selected_actions,
        "selected_action_counts": selected_action_counts,
        "move_forward_selected_count": selected_action_counts["move_forward"],
    }


def _run_condition(
    *,
    front_symbol: str,
    reward_store: dict[str, dict[str, Any]],
    seed: int,
    trials: int,
    reward_event_count: int,
) -> dict[str, Any]:
    scored = score_actions_for_front_symbol(front_symbol, reward_store)
    sampled = sample_actions_from_scores(scored["action_scores"], seed=seed, trials=trials)
    return {
        "front_symbol": scored["front_symbol"],
        "reward_event_count": reward_event_count,
        "matching_reward_event_found": scored["matching_reward_event_found"],
        "reward_bias_applied": scored["reward_bias_applied"],
        "reward_bias_delta": scored["reward_bias_delta"],
        "action_scores": scored["action_scores"],
        "move_forward_score": scored["move_forward_score"],
        "selected_actions": sampled["selected_actions"],
        "selected_action_counts": sampled["selected_action_counts"],
        "move_forward_selected_count": sampled["move_forward_selected_count"],
    }


def _build_comparison(no_reward_result: dict[str, Any], with_reward_result: dict[str, Any]) -> dict[str, Any]:
    score_delta = with_reward_result["move_forward_score"] - no_reward_result["move_forward_score"]
    selected_delta = (
        with_reward_result["move_forward_selected_count"] - no_reward_result["move_forward_selected_count"]
    )
    with_reward_score_higher = score_delta > 0.0
    with_reward_selection_not_lower = selected_delta >= 0
    return {
        "move_forward_score_delta": score_delta,
        "move_forward_selected_count_delta": selected_delta,
        "with_reward_score_higher": with_reward_score_higher,
        "with_reward_selection_not_lower": with_reward_selection_not_lower,
        "reward_bias_effect_observed": with_reward_score_higher and with_reward_selection_not_lower,
    }


def _boundary_check() -> dict[str, Any]:
    return {
        "reward_biased_random_walk_check_enabled": True,
        "controlled_front_symbol_item_scenario": True,
        "whole_map_random_walk_improvement_claimed": False,
        "item_reward_event_enabled": True,
        "reward_biased_action_tendency_enabled": True,
        "requires_prior_reward_for_bias": True,
        "no_reward_control_used": True,
        "item_seeking_enabled": False,
        "route_planner_added": False,
        "pathfinding_used": False,
        "observed_map_route_use": False,
        "full_map_visible_to_agent": False,
        "random_walk_base_behavior_modified": False,
        "action_selection_modified_in_this_check_only": True,
        "existing_navigation_action_selection_modified": False,
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
