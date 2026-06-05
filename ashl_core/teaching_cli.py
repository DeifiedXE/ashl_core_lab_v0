"""Minimal Teaching CLI wrapper for existing lesson flows."""

from __future__ import annotations

import argparse
import json
from typing import Any

from .fake_sandbox import build_initial_sandbox_state, observe, pick_up
from .lesson_runner import run_lesson_causality_test, run_session_2a_with_lesson
from .lesson_store import (
    build_lesson_from_failure,
    generate_lesson_from_failure,
    select_lesson_for_context,
    select_lesson_for_decision_point,
)


DECISION_POINT = "before_retry_pick_up_cube"
UNKNOWN_FAILURE_REASON = "unmapped_obstacle_shadow"


def _unknown_failure_result() -> dict[str, Any]:
    return {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": UNKNOWN_FAILURE_REASON,
        "state": build_initial_sandbox_state(),
    }


def _west_failure_result() -> dict[str, Any]:
    return {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }


def _format_conflict_check(selection: dict[str, Any]) -> dict[str, Any]:
    return {
        "implemented": True,
        "conflict_detected": selection["conflict_detected"],
        "conflict_resolution": selection.get("conflict_resolution"),
        "review_required": selection.get("review_required", False),
        "review_status": selection.get("review_status"),
        "conflicting_lesson_ids": selection.get("conflicting_lesson_ids", []),
        "conflicting_actions": selection.get("conflicting_actions", []),
        "selected_lesson_id": selection.get("selected_lesson_id"),
        "selected_action": selection.get("selected_action"),
        "behavior_changed": selection.get("behavior_changed", False),
    }


def _default_lifecycle_lessons() -> list[dict[str, Any]]:
    old_lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    old_lesson["object_id"] = "cube_001"
    old_lesson["stale"] = True
    old_lesson["stale_reason"] = "manual: obsolete wording"
    old_lesson["superseded_by"] = "lesson_004"
    new_lesson = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": DECISION_POINT,
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "inactive",
        "stale": False,
        "stale_reason": None,
        "supersedes": "lesson_001",
        "confidence": "manual_fixture",
    }
    return [old_lesson, new_lesson]


def _lesson_lifecycle_entry(
    lesson: dict[str, Any],
    selection: dict[str, Any] | None = None,
    conflict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    lesson_id = lesson.get("lesson_id")
    skipped_reason = None
    if selection is not None:
        skipped_reason = next(
            (
                item.get("skipped_reason")
                for item in selection.get("skipped_lessons", [])
                if item.get("lesson_id") == lesson_id
            ),
            None,
        )
    if skipped_reason is None and lesson.get("status") != "active":
        skipped_reason = "inactive"

    participates_in_conflict = False
    if conflict is not None:
        participates_in_conflict = lesson_id in conflict.get("conflicting_lesson_ids", [])

    return {
        "lesson_id": lesson_id,
        "status": lesson.get("status"),
        "stale": lesson.get("stale", False),
        "stale_reason": lesson.get("stale_reason"),
        "superseded_by": lesson.get("superseded_by"),
        "supersedes": lesson.get("supersedes"),
        "eligible_for_selection": lesson_id == (selection or {}).get("selected_lesson_id"),
        "skipped_reason": skipped_reason,
        "participates_in_conflict": participates_in_conflict,
    }


def _format_lifecycle_display(entries: list[dict[str, Any]]) -> str:
    lines = ["Lesson Lifecycle"]
    for entry in entries:
        lines.extend(
            [
                "",
                f"- id: {entry['lesson_id']}",
                f"  status: {entry['status']}",
                f"  stale: {str(entry['stale']).lower()}",
                f"  stale_reason: {entry['stale_reason'] or 'none'}",
                f"  superseded_by: {entry['superseded_by'] or 'none'}",
                f"  supersedes: {entry['supersedes'] or 'none'}",
                f"  eligible_for_selection: {str(entry['eligible_for_selection']).lower()}",
                f"  skipped_reason: {entry['skipped_reason'] or 'none'}",
                f"  participates_in_conflict: {str(entry['participates_in_conflict']).lower()}",
            ]
        )
    return "\n".join(lines)


def run_lifecycle_display(
    lessons: list[dict[str, Any]] | None = None,
    context: dict[str, Any] | None = None,
    decision_point: str = DECISION_POINT,
) -> dict[str, Any]:
    lesson_snapshot = [dict(lesson) for lesson in (lessons if lessons is not None else _default_lifecycle_lessons())]
    context = context or {"task": "pick_up", "object_id": "cube_001", "decision_point": decision_point}
    selection = select_lesson_for_context(lesson_snapshot, context)
    conflict = select_lesson_for_decision_point(lesson_snapshot, decision_point)
    entries = [_lesson_lifecycle_entry(lesson, selection=selection, conflict=conflict) for lesson in lesson_snapshot]
    return {
        "command": "run-lifecycle-display",
        "status": "ok",
        "read_only": True,
        "lessons": entries,
        "display": _format_lifecycle_display(entries),
        "selection_trace": selection,
        "conflict_check": _format_conflict_check(conflict),
        "notes": ["Lifecycle display is read-only and does not mutate lesson metadata."],
    }


def run_known_flow() -> dict[str, Any]:
    state = build_initial_sandbox_state()
    observation = observe(state)
    task_attempt = pick_up(state, "cube_001")
    generation = generate_lesson_from_failure("session_1", task_attempt)
    lesson = generation["lesson"]
    conflict_check = _format_conflict_check(select_lesson_for_decision_point([lesson], DECISION_POINT))
    rerun = run_session_2a_with_lesson(lesson)
    return {
        "command": "run-known-flow",
        "status": "ok" if lesson is not None and rerun["success"] else "failed",
        "failure_reason": task_attempt["failure_reason"],
        "observe": observation,
        "task_attempt": task_attempt,
        "lesson": lesson,
        "generation_status": generation["trace"]["generation_status"],
        "lesson_review": {
            "status": "reviewed",
            "conflict_check": conflict_check,
        },
        "conflict_check": conflict_check,
        "behavior_before": task_attempt["result"],
        "behavior_after": rerun["final_result"]["result"],
        "rerun": rerun,
        "notes": ["Conflict check is implemented in v1.9c."],
    }


def run_unknown_flow() -> dict[str, Any]:
    failure_result = _unknown_failure_result()
    generation = generate_lesson_from_failure("session_unknown", failure_result)
    control_attempt = pick_up(build_initial_sandbox_state(), "cube_001")
    return {
        "command": "run-unknown-flow",
        "status": "ok",
        "failure_reason": failure_result["failure_reason"],
        "lesson": generation["lesson"],
        "generation_status": generation["trace"]["generation_status"],
        "executable_action": generation["trace"]["executable_action"],
        "behavior_before": control_attempt["result"],
        "behavior_after": control_attempt["result"],
        "behavior_changed": False,
        "actions": ["observe()", "pick_up(cube_001)"],
        "trace": generation["trace"],
        "conflict_check": _format_conflict_check(select_lesson_for_decision_point([], DECISION_POINT)),
        "notes": ["Unknown failure reason uses v1.7b boundary behavior."],
    }


def run_disable_reenable_flow() -> dict[str, Any]:
    causality = run_lesson_causality_test()
    return {
        "command": "run-disable-reenable-flow",
        "status": "ok" if causality["passed"] else "failed",
        "enabled_result": causality["active"]["result"],
        "disabled_result": causality["disabled"]["result"],
        "reenabled_result": causality["re_enabled"]["result"],
        "removed_result": causality["removed"]["result"],
        "causality": causality,
        "conflict_check": {
            "implemented": True,
            "conflict_detected": False,
            "conflict_resolution": None,
            "review_required": False,
            "review_status": None,
            "conflicting_lesson_ids": [],
            "conflicting_actions": [],
        },
        "notes": ["CLI wrapper preserves v1.6 causal control."],
    }


def run_conflict_check_flow() -> dict[str, Any]:
    east_failure = pick_up(build_initial_sandbox_state(), "cube_001")
    lesson_east = build_lesson_from_failure("session_east", east_failure)
    lesson_west = build_lesson_from_failure("session_west", _west_failure_result())
    selection = select_lesson_for_decision_point([lesson_east, lesson_west], DECISION_POINT)
    return {
        "command": "run-conflict-check-flow",
        "status": "ok",
        "conflict_check": _format_conflict_check(selection),
        "selection_trace": selection,
        "notes": ["Conflict requires human review; no lesson action is applied."],
    }


def run_command(command: str) -> dict[str, Any]:
    if command == "run-known-flow":
        return run_known_flow()
    if command == "run-unknown-flow":
        return run_unknown_flow()
    if command == "run-disable-reenable-flow":
        return run_disable_reenable_flow()
    if command == "run-conflict-check-flow":
        return run_conflict_check_flow()
    if command == "run-lifecycle-display":
        return run_lifecycle_display()
    return {
        "command": command,
        "status": "error",
        "error": "unknown_command",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ASHL Core minimal teaching CLI")
    parser.add_argument(
        "command",
        choices=[
            "run-known-flow",
            "run-unknown-flow",
            "run-disable-reenable-flow",
            "run-conflict-check-flow",
            "run-lifecycle-display",
        ],
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_command(args.command), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
