"""Deterministic prompt and decision-input leakage checks."""

from __future__ import annotations

import json
from typing import Any


def build_decision_input_snapshot(
    run_id: str,
    session_id: str,
    group: str,
    loaded_lesson_ids: list[str],
    visible_state: dict[str, Any],
    available_actions: list[str],
    visible_history_ids: list[str] | None = None,
    decision_input: str | None = None,
) -> dict[str, Any]:
    visible_history_ids = visible_history_ids or []
    if decision_input is None:
        decision_input = json.dumps(
            {
                "visible_state": visible_state,
                "available_actions": available_actions,
                "loaded_lesson_ids": loaded_lesson_ids,
                "visible_history_ids": visible_history_ids,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    return {
        "run_id": run_id,
        "session_id": session_id,
        "group": group,
        "loaded_lesson_ids": list(loaded_lesson_ids),
        "visible_state_keys": list(visible_state.keys()),
        "available_actions": list(available_actions),
        "visible_history_ids": visible_history_ids,
        "prompt_text_or_decision_input": decision_input,
        "leakage_check": None,
    }


def check_leakage(snapshot: dict[str, Any], allow_turn_tool: bool = False) -> dict[str, Any]:
    text_parts = [
        str(snapshot.get("prompt_text_or_decision_input", "")),
        json.dumps(snapshot.get("loaded_lesson_ids", []), ensure_ascii=False),
        json.dumps(snapshot.get("visible_state_keys", []), ensure_ascii=False),
        json.dumps(snapshot.get("visible_history_ids", []), ensure_ascii=False),
    ]
    text = " ".join(text_parts).lower()

    contains_turn_hint = "turn(east)" in text or "turn east" in text
    if not allow_turn_tool:
        contains_turn_hint = contains_turn_hint or "turn" in text

    result = {
        "contains_lesson_id": "lesson_001" in text,
        "contains_failure_reason": "not_facing_east" in text or "failure_reason" in text,
        "contains_east": "east" in text,
        "contains_turn_hint": contains_turn_hint,
        "contains_session_1_history": "session_1" in text or "session 1" in text,
        "contains_avatar_facing": "avatar_facing" in text,
        "contains_facing": "facing" in text,
        "contains_direction": "direction" in text,
        "passed": True,
    }
    result["passed"] = not any(
        [
            result["contains_lesson_id"],
            result["contains_failure_reason"],
            result["contains_east"],
            result["contains_turn_hint"],
            result["contains_session_1_history"],
            result["contains_avatar_facing"],
            result["contains_facing"],
            result["contains_direction"],
        ]
    )
    return result
