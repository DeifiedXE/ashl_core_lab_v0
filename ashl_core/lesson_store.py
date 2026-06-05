"""In-memory lesson store helpers for deterministic lesson contribution tests."""

from __future__ import annotations

from typing import Any


VALID_LESSON_STATUSES = {"active", "disabled"}


def build_lesson_from_failure(session_id: str, failure_result: dict[str, Any]) -> dict[str, Any] | None:
    failure_reason = failure_result.get("failure_reason")
    known_mappings = {
        "not_facing_east": {
            "lesson_id": "lesson_001",
            "avatar_facing": "east",
            "suggested_action_before_retry": "turn(east)",
        },
        "not_facing_west": {
            "lesson_id": "lesson_002",
            "avatar_facing": "west",
            "suggested_action_before_retry": "turn(west)",
        },
    }
    mapping = known_mappings.get(failure_reason)
    if mapping is None:
        return None
    return {
        "lesson_id": mapping["lesson_id"],
        "source_session": session_id,
        "source_failure_reason": failure_reason,
        "trigger": {
            "action": "pick_up",
            "target_type": "cube",
        },
        "decision_point": "before_retry_pick_up_cube",
        "condition": {
            "avatar_facing": mapping["avatar_facing"],
        },
        "suggested_action_before_retry": mapping["suggested_action_before_retry"],
        "status": "active",
        "confidence": "tested_once",
    }


def generate_lesson_from_failure(session_id: str, failure_result: dict[str, Any]) -> dict[str, Any]:
    lesson = build_lesson_from_failure(session_id, failure_result)
    failure_reason = failure_result.get("failure_reason")
    if lesson is not None:
        return {
            "type": "lesson_generation_result",
            "lesson": lesson,
            "trace": {
                "generation_status": "supported_failure_reason",
                "reason": "known_failure_reason",
                "source_failure_reason": failure_reason,
                "executable_action": lesson["suggested_action_before_retry"],
            },
        }

    return {
        "type": "lesson_generation_result",
        "lesson": None,
        "trace": {
            "generation_status": "unknown_failure_reason",
            "reason": "unknown_failure_reason",
            "source_failure_reason": failure_reason,
            "executable_action": None,
            "known_failure_reasons": ["not_facing_east", "not_facing_west"],
        },
    }


def list_active_lessons(lessons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [lesson for lesson in lessons if lesson.get("status") == "active"]


def list_selectable_lessons(lessons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [lesson for lesson in list_active_lessons(lessons) if lesson.get("stale") is not True]


def _stale_skips(lessons: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {"lesson_id": lesson.get("lesson_id"), "skipped_reason": "stale"}
        for lesson in list_active_lessons(lessons)
        if lesson.get("stale") is True
    ]


def set_lesson_stale(lesson: dict[str, Any], stale: bool) -> dict[str, Any]:
    updated = dict(lesson)
    updated["stale"] = bool(stale)
    return updated


def mark_lesson_stale(lesson: dict[str, Any]) -> dict[str, Any]:
    return set_lesson_stale(lesson, True)


def unmark_lesson_stale(lesson: dict[str, Any]) -> dict[str, Any]:
    return set_lesson_stale(lesson, False)


def link_lesson_supersede(old_lesson: dict[str, Any], new_lesson: dict[str, Any]) -> dict[str, Any]:
    old_id = old_lesson.get("lesson_id")
    new_id = new_lesson.get("lesson_id")
    updated_old = dict(old_lesson)
    updated_new = dict(new_lesson)

    old_status = old_lesson.get("status")
    new_status = new_lesson.get("status")
    old_stale = old_lesson.get("stale")
    new_stale = new_lesson.get("stale")

    updated_old["superseded_by"] = new_id
    updated_new["supersedes"] = old_id

    return {
        "type": "lesson_supersede_link_result",
        "supersede_linked": old_id is not None and new_id is not None,
        "old_lesson": updated_old,
        "new_lesson": updated_new,
        "trace": {
            "supersede_linked": old_id is not None and new_id is not None,
            "old_lesson_id": old_id,
            "new_lesson_id": new_id,
            "old_superseded_by": updated_old.get("superseded_by"),
            "new_supersedes": updated_new.get("supersedes"),
            "old_status_changed": updated_old.get("status") != old_status,
            "new_status_changed": updated_new.get("status") != new_status,
            "status_changed": updated_old.get("status") != old_status or updated_new.get("status") != new_status,
            "old_stale_changed": updated_old.get("stale") != old_stale,
            "new_stale_changed": updated_new.get("stale") != new_stale,
            "selection_behavior_changed": False,
        },
    }


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

    for lesson in list_selectable_lessons(lessons):
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


def select_lesson_for_failure_reason(lessons: list[dict[str, Any]], failure_reason: str) -> dict[str, Any]:
    matches = [
        lesson
        for lesson in list_selectable_lessons(lessons)
        if lesson.get("source_failure_reason") == failure_reason
    ]
    selected = matches[0] if len(matches) == 1 else None
    return {
        "type": "lesson_selection_result",
        "active_lesson_ids": [lesson.get("lesson_id") for lesson in list_active_lessons(lessons)],
        "skipped_lessons": _stale_skips(lessons),
        "matched_failure_reason": failure_reason,
        "selected_lesson_id": selected.get("lesson_id") if selected else None,
        "selected_action": selected.get("suggested_action_before_retry") if selected else None,
        "selected_lesson": selected,
        "conflict_detected": False,
    }


def _actions_are_incompatible(actions: list[str]) -> bool:
    return "turn(east)" in actions and "turn(west)" in actions


def select_lesson_for_decision_point(lessons: list[dict[str, Any]], decision_point: str) -> dict[str, Any]:
    active_lessons = list_active_lessons(lessons)
    skipped_lessons = _stale_skips(lessons)
    matches = [lesson for lesson in list_selectable_lessons(lessons) if lesson.get("decision_point") == decision_point]
    actions = [lesson.get("suggested_action_before_retry") for lesson in matches if lesson.get("suggested_action_before_retry")]
    lesson_ids = [lesson.get("lesson_id") for lesson in matches]

    if len(matches) >= 2 and _actions_are_incompatible(actions):
        return {
            "type": "lesson_selection_result",
            "decision_point": decision_point,
            "active_lesson_ids": [lesson.get("lesson_id") for lesson in active_lessons],
            "skipped_lessons": skipped_lessons,
            "matched_lesson_ids": lesson_ids,
            "conflict_detected": True,
            "conflict_resolution": "require_review",
            "review_required": True,
            "review_status": "pending_human_review",
            "conflicting_lesson_ids": lesson_ids,
            "conflicting_actions": actions,
            "selected_lesson_id": None,
            "selected_action": None,
            "selected_lesson": None,
            "behavior_changed": False,
        }

    selected = matches[0] if len(matches) == 1 else None
    return {
        "type": "lesson_selection_result",
        "decision_point": decision_point,
        "active_lesson_ids": [lesson.get("lesson_id") for lesson in active_lessons],
        "skipped_lessons": skipped_lessons,
        "matched_lesson_ids": lesson_ids,
        "conflict_detected": False,
        "conflict_resolution": None,
        "review_required": False,
        "review_status": None,
        "conflicting_lesson_ids": [],
        "conflicting_actions": [],
        "selected_lesson_id": selected.get("lesson_id") if selected else None,
        "selected_action": selected.get("suggested_action_before_retry") if selected else None,
        "selected_lesson": selected,
        "behavior_changed": selected is not None,
    }


def select_lesson_for_context(lessons: list[dict[str, Any]], context: dict[str, Any]) -> dict[str, Any]:
    active_lessons = list_active_lessons(lessons)
    skipped_lessons = _stale_skips(lessons)
    task = context.get("task")
    object_id = context.get("object_id")
    decision_point = context.get("decision_point")
    matches = [
        lesson
        for lesson in list_selectable_lessons(lessons)
        if lesson.get("decision_point") == decision_point
        and lesson.get("trigger", {}).get("action") == task
        and lesson.get("object_id", "cube_001") == object_id
    ]
    selected = matches[0] if len(matches) == 1 else None
    return {
        "type": "lesson_context_selection_result",
        "matched_task": task,
        "matched_object_id": object_id,
        "decision_point": decision_point,
        "active_lesson_ids": [lesson.get("lesson_id") for lesson in active_lessons],
        "skipped_lessons": skipped_lessons,
        "matched_lesson_ids": [lesson.get("lesson_id") for lesson in matches],
        "selected_lesson_id": selected.get("lesson_id") if selected else None,
        "selected_action": selected.get("suggested_action_before_retry") if selected else None,
        "selected_lesson": selected,
        "conflict_detected": False,
        "behavior_changed": selected is not None,
    }
