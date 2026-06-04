"""Minimal Teaching CLI wrapper for existing lesson flows."""

from __future__ import annotations

import argparse
import json
from typing import Any

from .fake_sandbox import build_initial_sandbox_state, observe, pick_up
from .lesson_runner import run_lesson_causality_test, run_session_2a_with_lesson
from .lesson_store import build_lesson_from_failure, generate_lesson_from_failure, select_lesson_for_decision_point


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
    return {
        "command": command,
        "status": "error",
        "error": "unknown_command",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ASHL Core minimal teaching CLI")
    parser.add_argument(
        "command",
        choices=["run-known-flow", "run-unknown-flow", "run-disable-reenable-flow", "run-conflict-check-flow"],
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_command(args.command), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
