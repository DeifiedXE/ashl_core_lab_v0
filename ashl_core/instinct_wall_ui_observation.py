"""UI observation summaries for bounded instinct and wall influence experiments."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_empty_experiment_observation() -> dict[str, Any]:
    return {
        "mode": "none",
        "title": "No experiment observation",
        "seed": 1,
        "max_steps": 50,
        "random_walk": None,
        "wall_influence": None,
        "boundary_check": build_experiment_observation_boundary_check(),
        "log": [],
    }


def build_random_walk_observation(result: dict[str, Any]) -> dict[str, Any]:
    metrics = result["metrics"]
    experience_summary = result["experience_summary"]
    boundary = result["boundary_check"]
    return {
        "mode": "instinct_random_walk",
        "title": "Instinct Random Walk",
        "seed": result["seed"],
        "max_steps": result["max_steps"],
        "random_walk": {
            "step_count": metrics["step_count"],
            "wall_blocked_count": metrics["wall_blocked_count"],
            "item_contact_count": metrics["item_contact_count"],
            "first_item_contact_step": metrics["first_item_contact_step"],
            "experience_count": experience_summary["experience_count"],
            "experience_keys": list(experience_summary["experience_keys"]),
            "prior_experience_loaded": boundary["prior_experience_loaded"],
            "experience_influence_enabled": boundary["experience_influence_enabled"],
            "reward_bias_enabled": boundary["reward_bias_enabled"],
            "dopamine_like_signal_enabled": boundary["dopamine_like_signal_enabled"],
        },
        "wall_influence": None,
        "boundary_check": build_experiment_observation_boundary_check(),
        "log": _random_walk_log(metrics),
    }


def build_wall_influence_observation(result: dict[str, Any]) -> dict[str, Any]:
    control = result["control_result"]
    influence = result["influence_result"]
    boundary = result["boundary_check"]
    return {
        "mode": "wall_experience_influence",
        "title": "Wall Experience Influence",
        "seed": result["seed"],
        "max_steps": result["max_steps"],
        "random_walk": None,
        "wall_influence": {
            "control_passed": control["passed"],
            "influence_passed": influence["passed"],
            "selected_action_without_experience": control["selected_action"],
            "selected_action_with_wall_experience": influence["selected_action"],
            "experience_used_for_decision": influence["experience_used_for_decision"],
            "influence_type": influence["influence_type"],
            "item_reward_bias_enabled": boundary["item_reward_bias_enabled"],
            "dopamine_like_signal_enabled": boundary["dopamine_like_signal_enabled"],
        },
        "boundary_check": build_experiment_observation_boundary_check(),
        "log": _wall_influence_log(control, influence),
    }


def build_experiment_observation_boundary_check() -> dict[str, bool]:
    return {
        "instinct_random_walk_ui_observation_enabled": True,
        "wall_experience_influence_ui_observation_enabled": True,
        "bounded_runner_only": True,
        "continuous_autonomous_loop_enabled": False,
        "auto_exploration_enabled": False,
        "decision_loop_enabled": False,
        "random_walk_runner_available": True,
        "wall_experience_influence_available": True,
        "item_reward_bias_enabled": False,
        "dopamine_like_signal_enabled": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "llm_planning_used": False,
        "llm_vision_used": False,
        "action_selection_modified_by_ui": False,
        "item_collection_enabled": False,
        "exit_activation_enabled": False,
        "curiosity_enabled": False,
        "prediction_error_enabled": False,
        "place_memory_enabled": False,
        "home_sandbox_enabled": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "visual_understanding_claimed": False,
        "symbol_grounding_solved_claimed": False,
        "general_learning_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }


def copy_experiment_observation(observation: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(observation)


def _random_walk_log(metrics: dict[str, Any]) -> list[str]:
    log = ["Qingyin ran a bounded random walk sample."]
    if metrics["wall_blocked_count"]:
        log.append("Qingyin recorded wall-blocked experience.")
    if metrics["item_contact_count"]:
        log.append("Qingyin recorded item-contact experience.")
    return log


def _wall_influence_log(control: dict[str, Any], influence: dict[str, Any]) -> list[str]:
    log = []
    if control["passed"]:
        log.append("No-experience wall control passed.")
    if influence["passed"]:
        log.append("Wall experience influence check passed.")
    return log
