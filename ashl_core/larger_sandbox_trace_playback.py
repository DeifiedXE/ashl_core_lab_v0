"""Recorded trace playback helpers for larger sandbox UI observation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_empty_playback_state() -> dict[str, Any]:
    return {
        "playback_trace": [],
        "playback_index": 0,
        "playback_length": 0,
        "playback_mode": "none",
        "playback_seed": 1,
        "playback_max_steps": 50,
        "current_step": None,
        "boundary_check": build_trace_playback_boundary_check(),
    }


def build_playback_state_from_random_walk(result: dict[str, Any]) -> dict[str, Any]:
    playback_trace = [_compact_playback_step(step) for step in result.get("step_trace", [])]
    state = {
        "playback_trace": playback_trace,
        "playback_index": 0,
        "playback_length": len(playback_trace),
        "playback_mode": "recorded_random_walk",
        "playback_seed": result["seed"],
        "playback_max_steps": result["max_steps"],
        "current_step": playback_trace[0] if playback_trace else None,
        "boundary_check": build_trace_playback_boundary_check(),
    }
    return state


def set_playback_index(playback_state: dict[str, Any], index: int) -> dict[str, Any]:
    state = copy_playback_state(playback_state)
    length = state["playback_length"]
    if length <= 0:
        state["playback_index"] = 0
        state["current_step"] = None
        return state
    state["playback_index"] = min(max(index, 0), length - 1)
    state["current_step"] = state["playback_trace"][state["playback_index"]]
    return state


def next_playback_step(playback_state: dict[str, Any]) -> dict[str, Any]:
    return set_playback_index(playback_state, playback_state.get("playback_index", 0) + 1)


def previous_playback_step(playback_state: dict[str, Any]) -> dict[str, Any]:
    return set_playback_index(playback_state, playback_state.get("playback_index", 0) - 1)


def reset_playback_step(playback_state: dict[str, Any]) -> dict[str, Any]:
    return set_playback_index(playback_state, 0)


def copy_playback_state(playback_state: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(playback_state)


def build_trace_playback_boundary_check() -> dict[str, bool]:
    return {
        "trace_playback_enabled": True,
        "playback_from_recorded_trace_only": True,
        "server_side_autonomous_loop_enabled": False,
        "client_side_playback_only": False,
        "auto_exploration_enabled": False,
        "decision_loop_enabled": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "manual_state_modified_by_playback": False,
        "random_walk_runner_available": True,
        "reward_bias_enabled": False,
        "dopamine_like_signal_enabled": False,
        "item_collection_enabled": False,
        "exit_activation_enabled": False,
        "curiosity_enabled": False,
        "prediction_error_enabled": False,
        "place_memory_enabled": False,
        "home_sandbox_enabled": False,
        "long_term_memory_write": False,
        "visual_understanding_claimed": False,
        "general_learning_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }


def _compact_playback_step(step: dict[str, Any]) -> dict[str, Any]:
    compact = {
        "tick": step["tick"],
        "pos_before": list(step["pos_before"]),
        "facing_before": step["facing_before"],
        "viewport_before": deepcopy(step["viewport_before"]),
        "front_symbol_before": step["front_symbol_before"],
        "selected_action": step["selected_action"],
        "result": step["result"],
        "failure_reasons": list(step["failure_reasons"]),
        "effect_tags": list(step["effect_tags"]),
        "pos_after": list(step["pos_after"]),
        "facing_after": step["facing_after"],
        "viewport_after": deepcopy(step["viewport_after"]),
    }
    compact["readable_text"] = _format_playback_text(compact)
    return compact


def _format_playback_text(step: dict[str, Any]) -> str:
    symbol = step["front_symbol_before"]
    action = step["selected_action"]
    result = step["result"]
    if action == "look":
        return f"Step {step['tick']}: Qingyin looked while front symbol was {symbol}."
    if action == "turn_left":
        return f"Step {step['tick']}: Qingyin saw front symbol {symbol} and turned left."
    if action == "turn_right":
        return f"Step {step['tick']}: Qingyin saw front symbol {symbol} and turned right."
    if result == "blocked":
        return f"Step {step['tick']}: Qingyin saw front symbol {symbol} and tried move_forward. Result: blocked."
    if result == "item_contact":
        return f"Step {step['tick']}: Qingyin saw item and contacted it."
    if result == "moved":
        return f"Step {step['tick']}: Qingyin saw front symbol {symbol} and moved forward."
    if result == "exit_contact":
        return f"Step {step['tick']}: Qingyin saw exit placeholder and contacted it."
    return f"Step {step['tick']}: random/instinct selected action {action}. Result: {result}."
