"""In-memory lesson store helpers for deterministic lesson contribution tests."""

from __future__ import annotations

from typing import Any


VALID_LESSON_STATUSES = {"active", "disabled"}


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


def set_lesson_status(lesson: dict[str, Any], status: str) -> dict[str, Any] | None:
    if status not in VALID_LESSON_STATUSES:
        return None
    updated = dict(lesson)
    updated["status"] = status
    return updated


def disable_lesson(lesson: dict[str, Any]) -> dict[str, Any]:
    return set_lesson_status(lesson, "disabled")


def enable_lesson(lesson: dict[str, Any]) -> dict[str, Any]:
    return set_lesson_status(lesson, "active")


def remove_lesson(lessons: list[dict[str, Any]], lesson_id: str) -> list[dict[str, Any]]:
    return [lesson for lesson in lessons if lesson.get("lesson_id") != lesson_id]


def find_applicable_lesson(lessons: list[dict[str, Any]], goal: dict[str, Any]) -> dict[str, Any] | None:
    if goal.get("action") != "pick_up":
        return None

    if goal.get("object_id") != "cube_001":
        return None

    for lesson in list_active_lessons(lessons):
        trigger = lesson.get("trigger", {})
        condition = lesson.get("condition", {})
        # Phase -1.1 keeps target_type metadata but uses strict object binding to avoid premature generalization.
        if (
            lesson.get("lesson_id") == "lesson_001"
            and trigger.get("action") == "pick_up"
            and condition.get("avatar_facing") == "east"
        ):
            return lesson
    return None
