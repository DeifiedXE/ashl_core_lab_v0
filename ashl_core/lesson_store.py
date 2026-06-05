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


def _review_matches_candidate(review: dict[str, Any], lesson: dict[str, Any]) -> bool:
    if review.get("candidate_lesson_id") != lesson.get("lesson_id"):
        return False

    supersedes = lesson.get("supersedes")
    if supersedes is not None and review.get("source_lesson_id") != supersedes:
        return False

    target_type = lesson.get("review_target_type")
    if target_type is not None and review.get("target_type") != target_type:
        return False

    target_id = lesson.get("review_target_id")
    if target_id is not None and review.get("target_id") != target_id:
        return False

    return True


def evaluate_review_gate(
    candidate_lesson: dict[str, Any],
    review_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    requires_review = candidate_lesson.get("requires_review") is True
    candidate_id = candidate_lesson.get("lesson_id")
    if not requires_review:
        return {
            "candidate_lesson_id": candidate_id,
            "requires_review": False,
            "matched_review_id": None,
            "review_state": None,
            "approval_state": None,
            "review_gate_passed": True,
            "included_in_selection_eligibility": False,
            "conflict_changed": False,
            "activation_changed": False,
            "reason": "review_gate_not_required",
        }

    matched_review = None
    for review in review_items or []:
        if _review_matches_candidate(review, candidate_lesson):
            matched_review = review
            break

    if matched_review is None:
        return {
            "candidate_lesson_id": candidate_id,
            "requires_review": True,
            "matched_review_id": None,
            "review_state": None,
            "approval_state": None,
            "review_gate_passed": False,
            "included_in_selection_eligibility": True,
            "conflict_changed": False,
            "activation_changed": False,
            "reason": "missing_required_review",
        }

    review_state = matched_review.get("review_state")
    approval_state = matched_review.get("approval_state")
    approved = review_state == "reviewed" and approval_state == "approved"
    if approved:
        reason = "approved_review_allows_selection_eligibility"
    elif review_state == "reviewed" and approval_state == "rejected":
        reason = "rejected_review_blocks_selection_eligibility"
    else:
        reason = "review_not_approved"

    return {
        "candidate_lesson_id": candidate_id,
        "requires_review": True,
        "matched_review_id": matched_review.get("id"),
        "review_state": review_state,
        "approval_state": approval_state,
        "review_gate_passed": approved,
        "included_in_selection_eligibility": True,
        "conflict_changed": False,
        "activation_changed": False,
        "reason": reason,
    }


def _review_gate_passes(lesson: dict[str, Any], review_items: list[dict[str, Any]] | None = None) -> bool:
    return evaluate_review_gate(lesson, review_items)["review_gate_passed"] is True


def _selectable_lessons_with_review_gate(
    lessons: list[dict[str, Any]],
    review_items: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    return [lesson for lesson in list_selectable_lessons(lessons) if _review_gate_passes(lesson, review_items)]


def _review_gate_traces(
    lessons: list[dict[str, Any]],
    review_items: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    return [evaluate_review_gate(lesson, review_items) for lesson in list_active_lessons(lessons)]


def _stale_skips(lessons: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {"lesson_id": lesson.get("lesson_id"), "skipped_reason": "stale"}
        for lesson in list_active_lessons(lessons)
        if lesson.get("stale") is True
    ]


def _lesson_matches_context(lesson: dict[str, Any], context: dict[str, Any] | None) -> bool:
    if context is None:
        return True
    return (
        lesson.get("decision_point") == context.get("decision_point")
        and lesson.get("trigger", {}).get("action") == context.get("task")
        and lesson.get("object_id", "cube_001") == context.get("object_id")
    )


def _lesson_matches_selection_context(lesson: dict[str, Any], selection_context: dict[str, Any] | None) -> bool:
    if selection_context is None:
        return True
    kind = selection_context.get("kind")
    if kind == "context":
        return _lesson_matches_context(lesson, selection_context.get("context"))
    if kind == "decision_point":
        return lesson.get("decision_point") == selection_context.get("decision_point")
    if kind == "failure_reason":
        return lesson.get("source_failure_reason") == selection_context.get("failure_reason")
    return False


def build_replacement_suggestions(
    lessons: list[dict[str, Any]],
    skipped_lessons: list[dict[str, str]],
    context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    by_id = {lesson.get("lesson_id"): lesson for lesson in lessons}
    suggestions = []
    for skipped in skipped_lessons:
        if skipped.get("skipped_reason") != "stale":
            continue

        source_lesson = by_id.get(skipped.get("lesson_id"))
        if source_lesson is None:
            continue

        replacement_id = source_lesson.get("superseded_by")
        if not replacement_id:
            continue

        candidate = by_id.get(replacement_id)
        candidate_exists = candidate is not None
        candidate_status = candidate.get("status") if candidate_exists else None
        candidate_stale = candidate.get("stale") is True if candidate_exists else None
        candidate_eligible = (
            candidate_exists
            and candidate_status == "active"
            and candidate_stale is False
            and _lesson_matches_context(candidate, context)
        )

        if not candidate_exists:
            reason = "replacement_candidate_missing"
        elif candidate_stale:
            reason = "replacement_candidate_stale"
        elif candidate_status != "active":
            reason = "replacement_candidate_not_active"
        elif not _lesson_matches_context(candidate, context):
            reason = "replacement_candidate_not_context_eligible"
        else:
            reason = "trace_only_supersede_replacement_suggestion"

        suggestions.append(
            {
                "source_lesson_id": source_lesson.get("lesson_id"),
                "source_skipped_reason": skipped.get("skipped_reason"),
                "superseded_by": replacement_id,
                "candidate_lesson_id": replacement_id,
                "candidate_exists": candidate_exists,
                "candidate_status": candidate_status,
                "candidate_stale": candidate_stale,
                "candidate_eligible": candidate_eligible,
                "activation_applied": False,
                "reason": reason,
            }
        )
    return suggestions


def build_strict_supersede_activations(
    lessons: list[dict[str, Any]],
    skipped_lessons: list[dict[str, str]],
    selection_context: dict[str, Any] | None = None,
    selected_lesson_id: str | None = None,
    conflict_detected: bool = False,
    review_items: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    by_id = {lesson.get("lesson_id"): lesson for lesson in lessons}
    activations = []
    for skipped in skipped_lessons:
        source_lesson = by_id.get(skipped.get("lesson_id"))
        if skipped.get("skipped_reason") != "stale" or source_lesson is None:
            continue

        candidate_id = source_lesson.get("superseded_by")
        if not candidate_id:
            continue

        candidate = by_id.get(candidate_id)
        old_lesson_stale = source_lesson.get("stale") is True
        old_lesson_has_superseded_by = bool(candidate_id)
        candidate_exists = candidate is not None
        candidate_active = candidate.get("status") == "active" if candidate_exists else False
        candidate_not_stale = candidate.get("stale") is not True if candidate_exists else False
        candidate_eligible = (
            candidate_exists
            and candidate_active
            and candidate_not_stale
            and _lesson_matches_selection_context(candidate, selection_context)
            and _review_gate_passes(candidate, review_items)
        )
        review_gate = evaluate_review_gate(candidate, review_items) if candidate_exists else None

        condition_values = {
            "old_lesson_stale": old_lesson_stale,
            "old_lesson_has_superseded_by": old_lesson_has_superseded_by,
            "candidate_exists": candidate_exists,
            "candidate_active": candidate_active,
            "candidate_not_stale": candidate_not_stale,
            "candidate_eligible": candidate_eligible,
        }
        failed_conditions = [name for name, value in condition_values.items() if value is not True]
        if conflict_detected and candidate_eligible:
            failed_conditions.append("conflict_unresolved")
        if candidate_eligible and selected_lesson_id != candidate_id and not conflict_detected:
            failed_conditions.append("candidate_selected")

        activations.append(
            {
                "source_lesson_id": source_lesson.get("lesson_id"),
                "candidate_lesson_id": candidate_id,
                "old_lesson_stale": old_lesson_stale,
                "old_lesson_has_superseded_by": old_lesson_has_superseded_by,
                "candidate_exists": candidate_exists,
                "candidate_active": candidate_active,
                "candidate_not_stale": candidate_not_stale,
                "candidate_eligible": candidate_eligible,
                "review_gate": review_gate,
                "activation_source": "supersede_link",
                "activation_applied": candidate_eligible and selected_lesson_id == candidate_id and not conflict_detected,
                "failed_conditions": failed_conditions,
                "chain_followed": False,
            }
        )
    return activations


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


def select_lesson_for_failure_reason(
    lessons: list[dict[str, Any]],
    failure_reason: str,
    review_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    skipped_lessons = _stale_skips(lessons)
    selection_context = {"kind": "failure_reason", "failure_reason": failure_reason}
    matches = [
        lesson
        for lesson in _selectable_lessons_with_review_gate(lessons, review_items)
        if lesson.get("source_failure_reason") == failure_reason
    ]
    selected = matches[0] if len(matches) == 1 else None
    supersede_activations = build_strict_supersede_activations(
        lessons,
        skipped_lessons,
        selection_context,
        selected_lesson_id=selected.get("lesson_id") if selected else None,
        review_items=review_items,
    )
    return {
        "type": "lesson_selection_result",
        "active_lesson_ids": [lesson.get("lesson_id") for lesson in list_active_lessons(lessons)],
        "skipped_lessons": skipped_lessons,
        "review_gates": _review_gate_traces(lessons, review_items),
        "replacement_suggestions": build_replacement_suggestions(lessons, skipped_lessons),
        "supersede_activations": supersede_activations,
        "supersede_activation": supersede_activations[0] if supersede_activations else None,
        "matched_failure_reason": failure_reason,
        "selected_lesson_id": selected.get("lesson_id") if selected else None,
        "selected_action": selected.get("suggested_action_before_retry") if selected else None,
        "selected_lesson": selected,
        "conflict_detected": False,
    }


def _actions_are_incompatible(actions: list[str]) -> bool:
    return "turn(east)" in actions and "turn(west)" in actions


def build_stable_conflict_key(
    lesson_ids: list[str],
    decision_point: str,
    conflict_type: str = "incompatible_actions",
) -> str:
    sorted_lesson_ids = sorted(str(lesson_id) for lesson_id in lesson_ids if lesson_id)
    return f"conflict:{decision_point}:{conflict_type}:{'+'.join(sorted_lesson_ids)}"


def build_conflict_review_resolution_preview(
    conflict_trace: dict[str, Any],
    review_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    stable_conflict_key = conflict_trace.get("stable_conflict_key")
    lesson_ids = set(conflict_trace.get("conflicting_lesson_ids", []))
    matched_review_items = []
    for review in review_items or []:
        if review.get("target_type") != "conflict":
            continue
        if review.get("target_id") != stable_conflict_key:
            continue

        source_lesson_id = review.get("source_lesson_id")
        candidate_lesson_id = review.get("candidate_lesson_id")
        if source_lesson_id not in lesson_ids or candidate_lesson_id not in lesson_ids:
            continue

        approval_state = review.get("approval_state")
        if approval_state == "approved":
            preview_suggestion = "candidate_has_human_approval"
        elif approval_state == "rejected":
            preview_suggestion = "candidate_has_human_rejection"
        else:
            preview_suggestion = "candidate_review_not_final"

        matched_review_items.append(
            {
                "review_id": review.get("id"),
                "target_type": review.get("target_type"),
                "target_id": review.get("target_id"),
                "source_lesson_id": source_lesson_id,
                "candidate_lesson_id": candidate_lesson_id,
                "review_state": review.get("review_state"),
                "approval_state": approval_state,
                "notes": review.get("notes"),
                "preview_suggestion": preview_suggestion,
            }
        )

    return {
        "conflict_id": conflict_trace.get("conflict_id"),
        "stable_conflict_key": stable_conflict_key,
        "matched_review_items": matched_review_items,
        "resolution_preview_applied": False,
        "conflict_changed": False,
        "selection_changed": False,
        "activation_changed": False,
        "reason": "trace_only_conflict_review_resolution_preview" if matched_review_items else "no_matching_review_item",
    }


def select_lesson_for_decision_point(
    lessons: list[dict[str, Any]],
    decision_point: str,
    review_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    active_lessons = list_active_lessons(lessons)
    skipped_lessons = _stale_skips(lessons)
    replacement_suggestions = build_replacement_suggestions(lessons, skipped_lessons)
    review_gates = _review_gate_traces(lessons, review_items)
    selection_context = {"kind": "decision_point", "decision_point": decision_point}
    matches = [
        lesson
        for lesson in _selectable_lessons_with_review_gate(lessons, review_items)
        if lesson.get("decision_point") == decision_point
    ]
    actions = [lesson.get("suggested_action_before_retry") for lesson in matches if lesson.get("suggested_action_before_retry")]
    lesson_ids = [lesson.get("lesson_id") for lesson in matches]

    if len(matches) >= 2 and _actions_are_incompatible(actions):
        stable_conflict_key = build_stable_conflict_key(lesson_ids, decision_point)
        supersede_activations = build_strict_supersede_activations(
            lessons,
            skipped_lessons,
            selection_context,
            selected_lesson_id=None,
            conflict_detected=True,
            review_items=review_items,
        )
        result = {
            "type": "lesson_selection_result",
            "decision_point": decision_point,
            "active_lesson_ids": [lesson.get("lesson_id") for lesson in active_lessons],
            "skipped_lessons": skipped_lessons,
            "review_gates": review_gates,
            "replacement_suggestions": replacement_suggestions,
            "supersede_activations": supersede_activations,
            "supersede_activation": supersede_activations[0] if supersede_activations else None,
            "matched_lesson_ids": lesson_ids,
            "conflict_id": stable_conflict_key,
            "conflict_id_stable": True,
            "stable_conflict_key": stable_conflict_key,
            "stability_source": "deterministic_conflict_metadata",
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
        result["conflict_review_resolution_preview"] = build_conflict_review_resolution_preview(result, review_items)
        return result

    selected = matches[0] if len(matches) == 1 else None
    supersede_activations = build_strict_supersede_activations(
        lessons,
        skipped_lessons,
        selection_context,
        selected_lesson_id=selected.get("lesson_id") if selected else None,
        review_items=review_items,
    )
    return {
        "type": "lesson_selection_result",
        "decision_point": decision_point,
        "active_lesson_ids": [lesson.get("lesson_id") for lesson in active_lessons],
        "skipped_lessons": skipped_lessons,
        "review_gates": review_gates,
        "replacement_suggestions": replacement_suggestions,
        "supersede_activations": supersede_activations,
        "supersede_activation": supersede_activations[0] if supersede_activations else None,
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


def select_lesson_for_context(
    lessons: list[dict[str, Any]],
    context: dict[str, Any],
    review_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    active_lessons = list_active_lessons(lessons)
    skipped_lessons = _stale_skips(lessons)
    replacement_suggestions = build_replacement_suggestions(lessons, skipped_lessons, context)
    review_gates = _review_gate_traces(lessons, review_items)
    selection_context = {"kind": "context", "context": context}
    task = context.get("task")
    object_id = context.get("object_id")
    decision_point = context.get("decision_point")
    matches = [
        lesson
        for lesson in _selectable_lessons_with_review_gate(lessons, review_items)
        if lesson.get("decision_point") == decision_point
        and lesson.get("trigger", {}).get("action") == task
        and lesson.get("object_id", "cube_001") == object_id
    ]
    selected = matches[0] if len(matches) == 1 else None
    supersede_activations = build_strict_supersede_activations(
        lessons,
        skipped_lessons,
        selection_context,
        selected_lesson_id=selected.get("lesson_id") if selected else None,
        review_items=review_items,
    )
    return {
        "type": "lesson_context_selection_result",
        "matched_task": task,
        "matched_object_id": object_id,
        "decision_point": decision_point,
        "active_lesson_ids": [lesson.get("lesson_id") for lesson in active_lessons],
        "skipped_lessons": skipped_lessons,
        "review_gates": review_gates,
        "replacement_suggestions": replacement_suggestions,
        "supersede_activations": supersede_activations,
        "supersede_activation": supersede_activations[0] if supersede_activations else None,
        "matched_lesson_ids": [lesson.get("lesson_id") for lesson in matches],
        "selected_lesson_id": selected.get("lesson_id") if selected else None,
        "selected_action": selected.get("suggested_action_before_retry") if selected else None,
        "selected_lesson": selected,
        "conflict_detected": False,
        "behavior_changed": selected is not None,
    }
