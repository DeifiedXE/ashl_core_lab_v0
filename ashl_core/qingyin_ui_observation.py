"""Qingyin observation wrapper for the larger sandbox UI."""

from __future__ import annotations

from typing import Any


_SYMBOL_LABELS = {
    "w": "wall",
    "e": "empty",
    "i": "item",
    "d": "passage",
    "g": "exit placeholder",
    "x": "unseen",
    "a": "Qingyin",
}


def visible_symbols_from_viewport(viewport: list[list[str]]) -> list[str]:
    return sorted({symbol for row in viewport for symbol in row if symbol not in {"a", "x"}})


def build_qingyin_observation_state(ui_state: dict[str, Any]) -> dict[str, Any]:
    last_action_result = ui_state.get("last_action_result") or {}
    return {
        "name": "Qingyin",
        "mode": "manual_observation",
        "body": "symbolic_sandbox_body",
        "level_id": ui_state["level_id"],
        "pos": list(ui_state["pos"]),
        "facing": ui_state["facing"],
        "current_viewport": ui_state["viewport"],
        "front_symbol": ui_state["front_symbol"],
        "front_label": ui_state["front_label"],
        "visible_symbols": visible_symbols_from_viewport(ui_state["viewport"]),
        "visible_symbol_labels": [_SYMBOL_LABELS[symbol] for symbol in visible_symbols_from_viewport(ui_state["viewport"])],
        "last_action": last_action_result.get("action", "none"),
        "last_result": last_action_result.get("result", "none"),
        "last_effects": list(last_action_result.get("effects", [])),
        "last_failures": list(last_action_result.get("failures", [])),
        "can_act": ui_state["can_act"],
        "can_act_display": ui_state["can_act_display"],
        "cooldown_seconds": ui_state["action_cooldown_seconds"],
        "cooldown_remaining_seconds": ui_state["cooldown_remaining_seconds"],
        "cooldown_remaining_display": ui_state["cooldown_remaining_display"],
        "observation_note": "Manual observation only; user button presses drive actions.",
        "boundary_check": build_qingyin_observation_boundary_check(),
    }


def format_qingyin_log_entry(action: str, result: str, effects: list[str], failures: list[str]) -> str:
    if result == "cooldown_blocked":
        return "Action blocked by cooldown."
    if action == "look":
        return "Qingyin looked."
    if action == "turn_left":
        return "Qingyin turned left."
    if action == "turn_right":
        return "Qingyin turned right."
    if action == "move_forward" and result == "item_contact":
        return "Qingyin contacted an item."
    if action == "move_forward" and result == "exit_contact":
        return "Qingyin contacted an exit placeholder."
    if action == "move_forward" and result == "moved":
        return "Qingyin moved forward."
    if action == "move_forward" and result == "blocked":
        return "Qingyin was blocked."
    return f"Qingyin action observed: {action} -> {result}."


def build_qingyin_observation_boundary_check() -> dict[str, bool]:
    return {
        "qingyin_observation_bridge_enabled": True,
        "manual_observation_only": True,
        "autonomous_action_loop_enabled": False,
        "auto_exploration_enabled": False,
        "decision_loop_enabled": False,
        "llm_planning_used": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "action_selection_modified": False,
        "symbolic_sandbox_body": True,
        "real_robot_body": False,
        "real_image_vision": False,
        "computer_vision_used": False,
        "llm_vision_used": False,
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
        "symbol_grounding_solved_claimed": False,
        "general_learning_claimed": False,
        "consciousness_claimed": False,
    }
