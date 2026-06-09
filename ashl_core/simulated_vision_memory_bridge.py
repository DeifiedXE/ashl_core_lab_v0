"""Session-local memory bridge for symbolic simulated vision traces."""

from __future__ import annotations

from typing import Any

from .session_working_memory import (
    append_outcome_record,
    build_session_outcome_record,
    clear_session_working_memory,
    create_session_working_memory,
    query_recent_outcomes,
)
from .simulated_vision_sandbox import (
    FIRST_PERSON_AGENT_VIEWPORT_POSITION,
    FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION,
    FIRST_PERSON_FRONT_SYMBOL_POSITION,
    apply_simulated_vision_action,
    build_initial_simulated_vision_state,
    create_simulated_vision_room,
)


DEFAULT_MEMORY_BRIDGE_ACTIONS = (
    "look",
    "turn_right",
    "look",
    "move_forward",
    "look",
    "turn_left",
    "look",
)


def run_simulated_vision_memory_bridge_demo(
    action_sequence: list[str] | tuple[str, ...] | None = None,
    max_records: int = 20,
) -> dict[str, Any]:
    actions = tuple(action_sequence) if action_sequence is not None else DEFAULT_MEMORY_BRIDGE_ACTIONS
    level = create_simulated_vision_room()
    state = build_initial_simulated_vision_state(level)
    initial_state = _public_state(state)
    memory = create_session_working_memory(max_records=max_records)
    action_trace = []

    for action in actions:
        action_result = apply_simulated_vision_action(state, level, action)
        state = action_result["state"]
        trace = action_result["trace"]
        action_trace.append(trace)
        append_outcome_record(memory, _build_memory_record(trace=trace, level_id=level["level_id"]))

    records_before_clear = query_recent_outcomes(memory)
    sample_state_key = records_before_clear[0]["state_key"] if records_before_clear else None
    query_by_state_key = (
        query_recent_outcomes(memory, state_key=sample_state_key) if sample_state_key is not None else []
    )
    query_summary = {
        "record_count_before_clear": len(records_before_clear),
        "query_by_action_look_count": len(query_recent_outcomes(memory, action="look")),
        "query_by_action_turn_right_count": len(query_recent_outcomes(memory, action="turn_right")),
        "query_by_action_move_forward_count": len(query_recent_outcomes(memory, action="move_forward")),
        "query_by_outcome_type_blocked_count": len(query_recent_outcomes(memory, outcome_type="blocked")),
        "query_by_failure_reason_wall_blocked_count": sum(
            1 for record in records_before_clear if "wall_blocked" in record["failure_reasons"]
        ),
        "query_by_visible_symbol_i_count": sum(
            1 for record in records_before_clear if "i" in record["state_snapshot"].get("visible_symbols", [])
        ),
        "query_by_visible_symbol_w_count": sum(
            1 for record in records_before_clear if "w" in record["state_snapshot"].get("visible_symbols", [])
        ),
        "query_by_state_key_count": len(query_by_state_key),
    }
    clear_session_working_memory(memory)
    return {
        "command": "run-simulated-vision-memory-bridge-demo",
        "flow": "simulated_vision_session_memory_bridge_v0",
        "status": "ok",
        "level_id": level["level_id"],
        "max_records": max_records,
        "initial_state": initial_state,
        "action_trace": action_trace,
        "memory_records": records_before_clear,
        "query_summary": query_summary,
        "clear_summary": {
            "cleared": True,
            "record_count_after_clear": len(memory["records"]),
        },
        "final_state": _public_state(state),
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
            "full_map_visible_to_agent": False,
            "session_memory_write": True,
            "session_memory_cleared": True,
            "persistent_memory_write": False,
            "lesson_store_write": False,
            "memory_layer_write": False,
            "long_term_memory_write": False,
            "action_selection_modified": False,
            "goal_bias_modified": False,
            "visual_understanding_claimed": False,
            "symbol_grounding_claimed": False,
        },
        "notes": [
            "This bridge records symbolic simulated vision observations into session-local memory.",
            "Session Working Memory is cleared at session end.",
            "Memory records do not influence action selection.",
        ],
    }


def _build_memory_record(*, trace: dict[str, Any], level_id: str) -> dict[str, Any]:
    viewport = trace["viewport"]
    visible_symbols = sorted({symbol for row in viewport for symbol in row})
    after = trace["after"]
    before = trace["before"]
    state_snapshot = {
        "level_id": level_id,
        "agent_pos": after["pos"],
        "facing": after["facing"],
        "viewport": viewport,
        "visible_symbols": visible_symbols,
    }
    target = trace.get("target")
    metadata = {
        "source": "simulated_vision_memory_bridge_v0",
        "event_type": _event_type_for_trace(trace),
        "viewport": viewport,
        "visible_symbols": visible_symbols,
        "before_pos": before["pos"],
        "before_facing": before["facing"],
        "after_pos": after["pos"],
        "after_facing": after["facing"],
        "result": trace["result"],
        "raw_result": trace["result"],
    }
    if target is not None:
        metadata["target_pos"] = target
    if trace["result"] == "blocked":
        metadata["blocked_at"] = target
    return build_session_outcome_record(
        tick=trace["tick"],
        state_snapshot=state_snapshot,
        action=trace["action"],
        target=target,
        outcome_type=_outcome_type_for_trace(trace),
        failure_reasons=trace["failure_reasons"],
        metadata=metadata,
    )


def _event_type_for_trace(trace: dict[str, Any]) -> str:
    if trace["action"] == "look":
        return "observed"
    if trace["action"] in {"turn_left", "turn_right"}:
        return "orientation_changed"
    return "movement"


def _outcome_type_for_trace(trace: dict[str, Any]) -> str:
    if trace["result"] == "blocked":
        return "blocked"
    if trace["action"] == "look":
        return "goal_progress"
    return "moved"


def _public_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "pos": list(state["pos"]),
        "facing": state["facing"],
    }
