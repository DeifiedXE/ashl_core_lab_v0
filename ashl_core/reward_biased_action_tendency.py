"""Runner-local reward-biased immediate action tendency check."""

from __future__ import annotations

from typing import Any

from .item_reward_event import run_item_reward_event_check


REWARD_BIAS_KEY = "front_symbol=i|action=move_forward|reward_type=item_contact_reward"
BASE_ACTION_SCORE = 1.0
ITEM_REWARD_BIAS_DELTA = 0.5


def run_reward_biased_action_tendency_check() -> dict[str, Any]:
    reward_check = run_item_reward_event_check()
    level_id = reward_check["level_id"]
    control_result = _run_no_reward_control()
    reward_event = reward_check["reward_event"]
    reward_store = build_reward_store([reward_event])
    reward_bias_result = _run_with_item_reward(reward_event, reward_store)
    summary = _build_summary(control_result, reward_bias_result)
    return {
        "command": "run-reward-biased-action-tendency-check",
        "flow": "reward_biased_action_tendency_v0",
        "status": "ok" if summary["all_reward_biased_action_tendency_checks_passed"] else "failed",
        "level_id": level_id,
        "control_result": control_result,
        "reward_bias_result": reward_bias_result,
        "reward_store_summary": _build_reward_store_summary(reward_store),
        "summary": summary,
        "boundary_check": _boundary_check(),
        "notes": [
            "Reward bias requires a matching prior non-subjective item reward event.",
            "The no-reward control confirms seeing i alone does not apply reward bias.",
            "This is an immediate visible-front-symbol tendency check only, not item seeking or route planning.",
        ],
    }


def build_reward_store(reward_events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    store: dict[str, dict[str, Any]] = {}
    for event in reward_events:
        key = _reward_key(
            front_symbol=event["front_symbol"],
            action=event["action"],
            reward_type=event["reward_type"],
        )
        if key not in store:
            store[key] = {
                "front_symbol": event["front_symbol"],
                "action": event["action"],
                "reward_type": event["reward_type"],
                "reward_value": event["reward_value"],
                "dopamine_like_signal": event["dopamine_like_signal"],
                "count": 0,
                "event_ids": [],
            }
        store[key]["count"] += 1
        store[key]["event_ids"].append(event["event_id"])
    return store


def lookup_item_reward(
    reward_store: dict[str, dict[str, Any]],
    front_symbol: str,
    action: str,
) -> dict[str, Any] | None:
    return reward_store.get(
        _reward_key(front_symbol=front_symbol, action=action, reward_type="item_contact_reward")
    )


def score_action_with_reward_bias(
    *,
    front_symbol: str,
    candidate_action: str,
    reward_store: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    reward_event = lookup_item_reward(reward_store, front_symbol, candidate_action)
    if reward_event is None:
        reward_bias_delta = 0.0
        return {
            "front_symbol": front_symbol,
            "candidate_action": candidate_action,
            "matching_reward_event_found": False,
            "reward_bias_applied": False,
            "reward_used_for_decision": False,
            "selected_action": candidate_action,
            "base_action_score": BASE_ACTION_SCORE,
            "reward_bias_delta": reward_bias_delta,
            "final_action_score": BASE_ACTION_SCORE + reward_bias_delta,
        }
    reward_bias_delta = ITEM_REWARD_BIAS_DELTA
    return {
        "front_symbol": front_symbol,
        "candidate_action": candidate_action,
        "matching_reward_event_found": True,
        "reward_bias_applied": True,
        "reward_used_for_decision": True,
        "selected_action": candidate_action,
        "base_action_score": BASE_ACTION_SCORE,
        "reward_bias_delta": reward_bias_delta,
        "final_action_score": BASE_ACTION_SCORE + reward_bias_delta,
    }


def _run_no_reward_control() -> dict[str, Any]:
    score = score_action_with_reward_bias(
        front_symbol="i",
        candidate_action="move_forward",
        reward_store={},
    )
    score["scenario"] = "no_reward_control"
    score["passed"] = (
        score["front_symbol"] == "i"
        and score["candidate_action"] == "move_forward"
        and score["matching_reward_event_found"] is False
        and score["reward_bias_applied"] is False
        and score["reward_used_for_decision"] is False
        and score["reward_bias_delta"] == 0.0
        and score["final_action_score"] == score["base_action_score"]
    )
    return score


def _run_with_item_reward(reward_event: dict[str, Any], reward_store: dict[str, dict[str, Any]]) -> dict[str, Any]:
    score = score_action_with_reward_bias(
        front_symbol="i",
        candidate_action="move_forward",
        reward_store=reward_store,
    )
    score["scenario"] = "with_item_reward"
    score["trial1_reward_event"] = reward_event
    score["passed"] = (
        score["front_symbol"] == "i"
        and score["candidate_action"] == "move_forward"
        and score["matching_reward_event_found"] is True
        and score["reward_bias_applied"] is True
        and score["reward_used_for_decision"] is True
        and score["selected_action"] == "move_forward"
        and score["reward_bias_delta"] > 0.0
        and score["final_action_score"] > score["base_action_score"]
    )
    return score


def _build_reward_store_summary(reward_store: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "reward_event_count": sum(entry["count"] for entry in reward_store.values()),
        "reward_keys": sorted(reward_store),
        "item_contact_reward_available": REWARD_BIAS_KEY in reward_store,
        "dopamine_like_signal_count": sum(
            entry["count"] for entry in reward_store.values() if entry["dopamine_like_signal"]
        ),
        "total_reward_value": sum(entry["reward_value"] * entry["count"] for entry in reward_store.values()),
    }


def _build_summary(control_result: dict[str, Any], reward_bias_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "control_passed": control_result["passed"],
        "reward_bias_passed": reward_bias_result["passed"],
        "requires_prior_reward_for_bias": True,
        "all_reward_biased_action_tendency_checks_passed": (
            control_result["passed"] and reward_bias_result["passed"]
        ),
    }


def _boundary_check() -> dict[str, Any]:
    return {
        "reward_biased_action_tendency_enabled": True,
        "requires_prior_reward_for_bias": True,
        "no_reward_control_used": True,
        "item_reward_event_enabled": True,
        "dopamine_like_signal_enabled": True,
        "item_seeking_enabled": False,
        "route_planner_added": False,
        "pathfinding_used": False,
        "observed_map_route_use": False,
        "full_map_visible_to_agent": False,
        "action_selection_modified_in_this_runner_only": True,
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


def _reward_key(*, front_symbol: str, action: str, reward_type: str) -> str:
    return f"front_symbol={front_symbol}|action={action}|reward_type={reward_type}"
