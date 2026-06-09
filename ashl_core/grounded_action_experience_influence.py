"""Runner-local influence from prior grounded action experience."""

from __future__ import annotations

from typing import Any

from .grounded_action_experience import build_experience_key, build_grounded_action_experience_record
from .simulated_vision_sandbox import (
    FIRST_PERSON_AGENT_VIEWPORT_POSITION,
    FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION,
    FIRST_PERSON_FRONT_SYMBOL_POSITION,
    apply_simulated_vision_action,
    create_simulated_vision_room,
    render_viewport,
)
from .simulated_vision_symbol_grounding import (
    SCENARIO_ORDER,
    build_symbol_grounding_scenarios,
    get_front_symbol_from_viewport,
)


FALLBACK_ACTION = "turn_right"


def build_experience_store(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
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


def lookup_grounded_experience(
    experience_store: dict[str, dict[str, Any]],
    front_symbol: str,
    action: str,
) -> dict[str, Any] | None:
    return experience_store.get(build_experience_key(front_symbol=front_symbol, action=action))


def choose_action_from_experience(
    front_symbol: str,
    candidate_action: str,
    experience_store: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    experience = lookup_grounded_experience(experience_store, front_symbol, candidate_action)
    if experience is None:
        return {
            "matching_experience_found": False,
            "experience_used_for_decision": False,
            "selected_action": candidate_action,
            "influence_applied": False,
            "influence_type": "none",
            "suppressed_action": None,
            "influence_reason": "no_matching_prior_experience",
        }
    if experience["outcome_type"] == "blocked" and "wall_blocked" in experience["failure_reasons"]:
        return {
            "matching_experience_found": True,
            "experience_used_for_decision": True,
            "selected_action": FALLBACK_ACTION,
            "influence_applied": True,
            "influence_type": "suppress",
            "suppressed_action": candidate_action,
            "influence_reason": f"prior_experience_front_symbol_{front_symbol}_{candidate_action}_blocked",
        }
    if experience["outcome_type"] == "item_contact" or "item_contact" in experience["effect_tags"]:
        influence_type = "allow_contact"
    else:
        influence_type = "allow"
    return {
        "matching_experience_found": True,
        "experience_used_for_decision": True,
        "selected_action": candidate_action,
        "influence_applied": False,
        "influence_type": influence_type,
        "suppressed_action": None,
        "influence_reason": f"prior_experience_front_symbol_{front_symbol}_{candidate_action}_{experience['outcome_type']}",
    }


def run_grounded_action_experience_influence_check(scenario: str | None = None) -> dict[str, Any]:
    level = create_simulated_vision_room()
    scenarios = build_symbol_grounding_scenarios(level)
    scenario_names = SCENARIO_ORDER if scenario is None else (scenario,)
    invalid = [name for name in scenario_names if name not in scenarios]
    if invalid:
        raise ValueError(f"unsupported grounded action experience influence scenario: {invalid[0]}")

    scenario_results = []
    experience_records = []
    for tick, scenario_name in enumerate(scenario_names, start=1):
        result = _run_single_influence_scenario(tick=tick, level=level, scenario=scenarios[scenario_name])
        scenario_results.append(result["scenario_result"])
        experience_records.append(result["experience_record"])

    experience_store = build_experience_store(experience_records)
    control_results = [_run_wall_without_prior_experience_control(level, scenarios["wall"])]
    summary = _build_summary(scenario_results, control_results)
    return {
        "command": "run-grounded-action-experience-influence-check",
        "flow": "grounded_action_experience_influence_v0",
        "status": "ok",
        "level_id": level["level_id"],
        "scenario_results": scenario_results,
        "control_results": control_results,
        "experience_store_summary": _build_store_summary(experience_store),
        "summary": summary,
        "boundary_check": {
            "simulated_vision_only": True,
            "structured_symbols_only": True,
            "first_person_viewport": True,
            "agent_viewport_position": FIRST_PERSON_AGENT_VIEWPORT_POSITION,
            "front_symbol_position": FIRST_PERSON_FRONT_SYMBOL_POSITION,
            "far_front_symbol_position": FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION,
            "centered_top_down_viewport": False,
            "real_image_vision": False,
            "llm_vision_used": False,
            "llm_planning_used": False,
            "pathfinding_used": False,
            "route_planner_added": False,
            "full_map_visible_to_agent": False,
            "grounded_action_experience_enabled": True,
            "grounded_action_experience_influence_enabled": True,
            "requires_prior_experience_for_influence": True,
            "no_experience_control_used": True,
            "action_selection_modified_in_this_runner_only": True,
            "existing_navigation_action_selection_modified": False,
            "experience_used_for_decision": any(
                result["experience_used_for_decision"] for result in scenario_results
            ),
            "session_local_only": True,
            "persistent_memory_write": False,
            "session_memory_write": False,
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
            "This tests see -> interact -> outcome -> experience -> later action influence.",
            "Influence requires a matching prior experience.",
            "The no-experience wall control proves seeing w alone does not suppress move_forward.",
        ],
    }


def _run_single_influence_scenario(
    *,
    tick: int,
    level: dict[str, Any],
    scenario: dict[str, Any],
) -> dict[str, Any]:
    trial1_state = scenario["state"]
    trial1_viewport = render_viewport(trial1_state, level)
    trial1_front_symbol = get_front_symbol_from_viewport(trial1_viewport)
    trial1_action_result = apply_simulated_vision_action(trial1_state, level, "move_forward")
    experience_record = build_grounded_action_experience_record(
        tick=tick,
        level_id=level["level_id"],
        state_before=trial1_state,
        viewport=trial1_viewport,
        front_symbol=trial1_front_symbol,
        action="move_forward",
        action_trace=trial1_action_result["trace"],
    )
    experience_store = build_experience_store([experience_record])
    trial2_state = scenario["state"]
    trial2_viewport = render_viewport(trial2_state, level)
    trial2_front_symbol = get_front_symbol_from_viewport(trial2_viewport)
    candidate_action = "move_forward"
    influence = choose_action_from_experience(trial2_front_symbol, candidate_action, experience_store)
    trial2_action_result = apply_simulated_vision_action(trial2_state, level, influence["selected_action"])
    trial2_trace = trial2_action_result["trace"]
    scenario_name = scenario["scenario"]
    influence_match = _influence_matches_expected_scenario(scenario_name, influence)
    return {
        "scenario_result": {
            "scenario": scenario_name,
            "trial1": {
                "front_symbol": trial1_front_symbol,
                "action": "move_forward",
                "outcome_type": experience_record["outcome_type"],
                "failure_reasons": experience_record["failure_reasons"],
                "effect_tags": experience_record["effect_tags"],
                "experience_recorded": True,
            },
            "trial2": {
                "front_symbol": trial2_front_symbol,
                "candidate_action": candidate_action,
                "selected_action": influence["selected_action"],
                "actual_outcome": trial2_trace["result"],
                "failure_reasons": trial2_trace["failure_reasons"],
                "effect_tags": ["item_contact"] if trial2_trace["result"] == "item_contact" else [],
                "position_changed": trial2_trace["before"]["pos"] != trial2_trace["after"]["pos"],
            },
            "experience_key": experience_record["experience_key"],
            "matching_experience_found": influence["matching_experience_found"],
            "experience_used_for_decision": influence["experience_used_for_decision"],
            "candidate_action": candidate_action,
            "selected_action": influence["selected_action"],
            "influence_applied": influence["influence_applied"],
            "influence_type": influence["influence_type"],
            "suppressed_action": influence["suppressed_action"],
            "influence_reason": influence["influence_reason"],
            "grounded_experience_influence_match": influence_match,
        },
        "experience_record": experience_record,
    }


def _run_wall_without_prior_experience_control(level: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    state = scenario["state"]
    viewport = render_viewport(state, level)
    front_symbol = get_front_symbol_from_viewport(viewport)
    candidate_action = "move_forward"
    influence = choose_action_from_experience(front_symbol, candidate_action, {})
    return {
        "control_name": "wall_without_prior_experience",
        "front_symbol": front_symbol,
        "candidate_action": candidate_action,
        "matching_experience_found": influence["matching_experience_found"],
        "selected_action": influence["selected_action"],
        "experience_used_for_decision": influence["experience_used_for_decision"],
        "influence_applied": influence["influence_applied"],
        "passed": (
            front_symbol == "w"
            and influence["selected_action"] == candidate_action
            and influence["experience_used_for_decision"] is False
            and influence["influence_applied"] is False
        ),
    }


def _influence_matches_expected_scenario(scenario_name: str, influence: dict[str, Any]) -> bool:
    if scenario_name == "wall":
        return (
            influence["matching_experience_found"] is True
            and influence["experience_used_for_decision"] is True
            and influence["selected_action"] != "move_forward"
            and influence["influence_type"] == "suppress"
        )
    if scenario_name == "empty":
        return (
            influence["matching_experience_found"] is True
            and influence["experience_used_for_decision"] is True
            and influence["selected_action"] == "move_forward"
            and influence["influence_type"] == "allow"
        )
    if scenario_name == "item":
        return (
            influence["matching_experience_found"] is True
            and influence["experience_used_for_decision"] is True
            and influence["selected_action"] == "move_forward"
            and influence["influence_type"] == "allow_contact"
        )
    return False


def _build_store_summary(experience_store: dict[str, dict[str, Any]]) -> dict[str, Any]:
    keys = sorted(experience_store)
    return {
        "experience_count": len(experience_store),
        "experience_keys": keys,
        "wall_experience_available": "front_symbol=w|action=move_forward" in experience_store,
        "empty_experience_available": "front_symbol=e|action=move_forward" in experience_store,
        "item_experience_available": "front_symbol=i|action=move_forward" in experience_store,
    }


def _build_summary(scenario_results: list[dict[str, Any]], control_results: list[dict[str, Any]]) -> dict[str, Any]:
    passed_count = sum(1 for result in scenario_results if result["grounded_experience_influence_match"])
    by_name = {result["scenario"]: result for result in scenario_results}
    no_experience_control_passed = all(control["passed"] for control in control_results)
    return {
        "scenario_count": len(scenario_results),
        "passed_count": passed_count,
        "failed_count": len(scenario_results) - passed_count,
        "wall_experience_influence_passed": by_name.get("wall", {}).get(
            "grounded_experience_influence_match", False
        ),
        "empty_experience_influence_passed": by_name.get("empty", {}).get(
            "grounded_experience_influence_match", False
        ),
        "item_experience_influence_passed": by_name.get("item", {}).get(
            "grounded_experience_influence_match", False
        ),
        "no_experience_control_passed": no_experience_control_passed,
        "all_grounded_action_experience_influence_checks_passed": (
            passed_count == len(scenario_results) and no_experience_control_passed
        ),
    }
