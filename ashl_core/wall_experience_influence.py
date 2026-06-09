"""Runner-local wall-blocked experience influence check."""

from __future__ import annotations

from typing import Any

from .simulated_vision_larger_sandbox import (
    apply_larger_sandbox_action,
    create_simulated_vision_larger_sandbox,
    front_symbol_from_larger_viewport,
    render_larger_sandbox_viewport,
)


FALLBACK_ACTION = "turn_right"
WALL_EXPERIENCE_KEY = "front_symbol=w|action=move_forward"


def run_wall_experience_influence_check(*, seed: int = 1, max_steps: int = 50) -> dict[str, Any]:
    level = create_simulated_vision_larger_sandbox()
    wall_state = _build_wall_test_state(level)
    control_result = _run_no_experience_control(level, wall_state)
    prior_experience = _build_wall_blocked_prior_experience(level, wall_state)
    experience_store = build_wall_experience_store([prior_experience])
    influence_result = _run_wall_influence_scenario(level, wall_state, experience_store, prior_experience)
    summary = _build_summary(control_result, influence_result)
    return {
        "command": "run-wall-experience-influence-check",
        "flow": "wall_experience_influence_v0",
        "status": "ok" if summary["all_wall_experience_influence_checks_passed"] else "failed",
        "level_id": level["level_id"],
        "seed": seed,
        "max_steps": max_steps,
        "control_result": control_result,
        "influence_result": influence_result,
        "experience_store_summary": _build_store_summary(experience_store),
        "summary": summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Wall influence requires a matching prior wall-blocked experience.",
            "The no-experience control proves seeing w alone does not suppress move_forward.",
            "This runner uses deterministic suppress to turn_right for the matching wall-blocked case.",
            "No item reward bias, dopamine-like signal, pathfinding, route planning, or long-term memory is added.",
        ],
    }


def build_wall_experience_store(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    store: dict[str, dict[str, Any]] = {}
    for record in records:
        key = record["experience_key"]
        if key not in store:
            store[key] = {
                "front_symbol": record["front_symbol"],
                "action": record["action"],
                "outcome_type": record["outcome_type"],
                "failure_reasons": list(record["failure_reasons"]),
                "effect_tags": list(record["effect_tags"]),
                "count": 0,
            }
        store[key]["count"] += 1
    return store


def choose_action_with_wall_experience(
    *,
    front_symbol: str,
    candidate_action: str,
    experience_store: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    experience_key = _experience_key(front_symbol=front_symbol, action=candidate_action)
    experience = experience_store.get(experience_key)
    if experience is None:
        return {
            "matching_experience_found": False,
            "selected_action": candidate_action,
            "experience_used_for_decision": False,
            "influence_applied": False,
            "influence_type": "none",
            "suppressed_action": None,
            "influence_reason": "no_matching_prior_experience",
        }
    if experience["outcome_type"] == "blocked" and "wall_blocked" in experience["failure_reasons"]:
        return {
            "matching_experience_found": True,
            "selected_action": FALLBACK_ACTION,
            "experience_used_for_decision": True,
            "influence_applied": True,
            "influence_type": "suppress",
            "suppressed_action": candidate_action,
            "influence_reason": "matching_prior_wall_blocked_experience",
        }
    return {
        "matching_experience_found": True,
        "selected_action": candidate_action,
        "experience_used_for_decision": True,
        "influence_applied": False,
        "influence_type": "allow",
        "suppressed_action": None,
        "influence_reason": f"matching_prior_experience_outcome_{experience['outcome_type']}",
    }


def _run_no_experience_control(level: dict[str, Any], wall_state: dict[str, Any]) -> dict[str, Any]:
    front_symbol = _front_symbol_for_state(level, wall_state)
    candidate_action = "move_forward"
    selection = choose_action_with_wall_experience(
        front_symbol=front_symbol,
        candidate_action=candidate_action,
        experience_store={},
    )
    passed = (
        front_symbol == "w"
        and selection["matching_experience_found"] is False
        and selection["selected_action"] == candidate_action
        and selection["experience_used_for_decision"] is False
        and selection["influence_applied"] is False
    )
    return {
        "control_name": "wall_without_prior_experience",
        "front_symbol": front_symbol,
        "candidate_action": candidate_action,
        "matching_experience_found": selection["matching_experience_found"],
        "selected_action": selection["selected_action"],
        "experience_used_for_decision": selection["experience_used_for_decision"],
        "influence_applied": selection["influence_applied"],
        "passed": passed,
    }


def _run_wall_influence_scenario(
    level: dict[str, Any],
    wall_state: dict[str, Any],
    experience_store: dict[str, dict[str, Any]],
    prior_experience: dict[str, Any],
) -> dict[str, Any]:
    front_symbol = _front_symbol_for_state(level, wall_state)
    candidate_action = "move_forward"
    selection = choose_action_with_wall_experience(
        front_symbol=front_symbol,
        candidate_action=candidate_action,
        experience_store=experience_store,
    )
    action_result = apply_larger_sandbox_action(wall_state, level, selection["selected_action"])
    trace = action_result["trace"]
    passed = (
        front_symbol == "w"
        and selection["matching_experience_found"] is True
        and selection["selected_action"] != candidate_action
        and selection["selected_action"] == FALLBACK_ACTION
        and selection["experience_used_for_decision"] is True
        and selection["influence_applied"] is True
        and selection["influence_type"] == "suppress"
    )
    return {
        "scenario": "wall_with_prior_experience",
        "front_symbol": front_symbol,
        "prior_experience": _public_prior_experience(prior_experience),
        "candidate_action": candidate_action,
        "selected_action": selection["selected_action"],
        "matching_experience_found": selection["matching_experience_found"],
        "experience_used_for_decision": selection["experience_used_for_decision"],
        "influence_applied": selection["influence_applied"],
        "influence_type": selection["influence_type"],
        "suppressed_action": selection["suppressed_action"],
        "fallback_action": FALLBACK_ACTION,
        "selected_action_result": trace["result"],
        "passed": passed,
    }


def _build_wall_blocked_prior_experience(level: dict[str, Any], wall_state: dict[str, Any]) -> dict[str, Any]:
    viewport = render_larger_sandbox_viewport(wall_state, level)
    front_symbol = front_symbol_from_larger_viewport(viewport)
    action = "move_forward"
    action_result = apply_larger_sandbox_action(wall_state, level, action)
    trace = action_result["trace"]
    return {
        "experience_key": _experience_key(front_symbol=front_symbol, action=action),
        "front_symbol": front_symbol,
        "action": action,
        "outcome_type": trace["result"],
        "failure_reasons": list(trace["failure_reasons"]),
        "effect_tags": list(trace["effect_tags"]),
        "position_changed": trace["before"]["pos"] != trace["after"]["pos"],
    }


def _build_summary(control_result: dict[str, Any], influence_result: dict[str, Any]) -> dict[str, Any]:
    control_passed = control_result["passed"]
    influence_passed = influence_result["passed"]
    return {
        "control_passed": control_passed,
        "influence_passed": influence_passed,
        "requires_prior_experience_for_influence": True,
        "all_wall_experience_influence_checks_passed": control_passed and influence_passed,
    }


def _build_store_summary(experience_store: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "experience_count": len(experience_store),
        "experience_keys": sorted(experience_store),
        "wall_blocked_experience_available": WALL_EXPERIENCE_KEY in experience_store,
    }


def _boundary_check() -> dict[str, Any]:
    return {
        "wall_experience_influence_enabled": True,
        "requires_prior_experience_for_influence": True,
        "no_experience_control_used": True,
        "item_reward_bias_enabled": False,
        "dopamine_like_signal_enabled": False,
        "item_seeking_enabled": False,
        "two_round_item_comparison_enabled": False,
        "simulated_vision_only": True,
        "larger_static_sandbox_used": True,
        "structured_symbols_only": True,
        "real_image_vision": False,
        "llm_vision_used": False,
        "llm_planning_used": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "full_map_visible_to_agent": False,
        "action_selection_modified_in_this_runner_only": True,
        "existing_navigation_action_selection_modified": False,
        "session_local_only": True,
        "persistent_memory_write": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "item_collection_enabled": False,
        "exit_activation_enabled": False,
        "curiosity_enabled": False,
        "prediction_error_enabled": False,
        "place_memory_enabled": False,
        "home_sandbox_enabled": False,
        "visual_understanding_claimed": False,
        "symbol_grounding_solved_claimed": False,
        "general_learning_claimed": False,
        "consciousness_claimed": False,
    }


def _build_wall_test_state(level: dict[str, Any]) -> dict[str, Any]:
    return {
        "level_id": level["level_id"],
        "pos": (2, 1),
        "facing": "north",
        "tick": 0,
    }


def _front_symbol_for_state(level: dict[str, Any], state: dict[str, Any]) -> str:
    return front_symbol_from_larger_viewport(render_larger_sandbox_viewport(state, level))


def _experience_key(*, front_symbol: str, action: str) -> str:
    return f"front_symbol={front_symbol}|action={action}"


def _public_prior_experience(prior_experience: dict[str, Any]) -> dict[str, Any]:
    return {
        "front_symbol": prior_experience["front_symbol"],
        "action": prior_experience["action"],
        "outcome_type": prior_experience["outcome_type"],
        "failure_reasons": list(prior_experience["failure_reasons"]),
    }
