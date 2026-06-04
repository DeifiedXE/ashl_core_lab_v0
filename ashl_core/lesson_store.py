"""In-memory lesson store helpers for deterministic lesson contribution tests."""

from __future__ import annotations

from typing import Any


def build_lesson_from_failure(session_id: str, failure_result: dict[str, Any]) -> dict[str, Any] | None:
    if failure_result.get("failure_reason") != "not_facing_east":
        return None
    return {
        "lesson_id": "lesson_001",
        "source_session": session_id,
        "source_failure_reason": "not_facing_east",
        "trigger": {
            "action": "pick_up",
            "target_type": "cube",
        },
        "condition": {
            "avatar_facing": "east",
        },
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "confidence": "tested_once",
    }


def list_active_lessons(lessons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [lesson for lesson in lessons if lesson.get("status") == "active"]


def find_applicable_lesson(lessons: list[dict[str, Any]], goal: dict[str, Any]) -> dict[str, Any] | None:
    if goal.get("action") != "pick_up":
        return None

    object_id = goal.get("object_id")
    target_type = goal.get("target_type")
    if object_id != "cube_001" and target_type != "cube":
        return None

    for lesson in list_active_lessons(lessons):
        trigger = lesson.get("trigger", {})
        if trigger.get("action") == "pick_up" and trigger.get("target_type") == "cube":
            return lesson
    return None
