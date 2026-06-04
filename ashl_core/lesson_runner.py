"""Deterministic Phase -1 lesson contribution runner."""

from __future__ import annotations

import json
from typing import Any

from .fake_sandbox import build_initial_sandbox_state, inspect, observe, pick_up, push, turn
from .lesson_store import build_lesson_from_failure, find_applicable_lesson
from .prompt_leakage_check import build_decision_input_snapshot, check_leakage


GOAL = {"action": "pick_up", "object_id": "cube_001", "target_type": "cube"}


def _decision_input(goal: dict[str, Any], visible_state: dict[str, Any], available_actions: list[str]) -> str:
    return json.dumps(
        {
            "goal": f"{goal['action']} {goal['object_id']}",
            "available_actions": available_actions,
            "current_state": visible_state,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def run_session_1() -> dict[str, Any]:
    state = build_initial_sandbox_state()
    result = pick_up(state, "cube_001")
    lesson = build_lesson_from_failure("session_1", result)
    return {
        "type": "lesson_session_result",
        "session_id": "session_1",
        "actions": [{"action": "pick_up(cube_001)", "result": result}],
        "final_result": result,
        "lesson": lesson,
        "success": result["result"] == "success",
    }


def run_session_2a_with_lesson(lesson: dict[str, Any]) -> dict[str, Any]:
    state = build_initial_sandbox_state()
    available_actions = ["observe", "turn", "pick_up"]
    observation = observe(state)
    snapshot = build_decision_input_snapshot(
        "run_2a",
        "session_2a",
        "2A",
        [lesson["lesson_id"]],
        observation["visible_state"],
        available_actions,
        decision_input=json.dumps(
            {
                "goal": "pick_up cube_001",
                "loaded_lesson_ids": [lesson["lesson_id"]],
                "lesson_suggested_action_before_retry": lesson["suggested_action_before_retry"],
                "current_state": observation["visible_state"],
                "available_actions": available_actions,
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
    )

    actions: list[dict[str, Any]] = [{"action": "observe()", "result": observation}]
    used_lesson_ids: list[str] = []
    applicable = find_applicable_lesson([lesson], GOAL)
    if applicable is not None:
        turned = turn(state, "east")
        state = turned["state"]
        used_lesson_ids.append(applicable["lesson_id"])
        actions.append({"action": "turn(east)", "result": turned, "caused_by_lesson_id": applicable["lesson_id"]})

    final_result = pick_up(state, "cube_001")
    actions.append({"action": "pick_up(cube_001)", "result": final_result})
    return {
        "type": "lesson_session_result",
        "session_id": "session_2a",
        "group": "2A",
        "decision_input_snapshot": snapshot,
        "actions": actions,
        "final_result": final_result,
        "used_lesson_ids": used_lesson_ids,
        "success": final_result["result"] == "success",
        "traceable_to": used_lesson_ids,
    }


def run_session_2b_without_lesson() -> dict[str, Any]:
    state = build_initial_sandbox_state()
    visible_state = observe(state, visible_keys=["object_id", "holding"])["visible_state"]
    available_actions = ["observe", "pick_up"]
    snapshot = build_decision_input_snapshot(
        "run_2b",
        "session_2b",
        "2B",
        [],
        visible_state,
        available_actions,
        decision_input=_decision_input(GOAL, visible_state, available_actions),
    )
    leakage = check_leakage(snapshot)
    snapshot["leakage_check"] = leakage

    observation = observe(state, visible_keys=["object_id", "holding"])
    final_result = pick_up(state, "cube_001")
    return {
        "type": "lesson_session_result",
        "session_id": "session_2b",
        "group": "2B",
        "decision_input_snapshot": snapshot,
        "actions": [
            {"action": "observe()", "result": observation},
            {"action": "pick_up(cube_001)", "result": final_result},
        ],
        "final_result": final_result,
        "used_lesson_ids": [],
        "success": final_result["result"] == "success",
    }


def run_session_2b2_without_lesson_with_turn_tool() -> dict[str, Any]:
    state = build_initial_sandbox_state()
    visible_state = observe(state, visible_keys=["object_id", "holding"])["visible_state"]
    available_actions = ["observe", "turn", "pick_up"]
    snapshot = build_decision_input_snapshot(
        "run_2b2",
        "session_2b2",
        "2B-2",
        [],
        visible_state,
        available_actions,
        decision_input=_decision_input(GOAL, visible_state, available_actions),
    )
    leakage = check_leakage(snapshot, allow_turn_tool=True)
    snapshot["leakage_check"] = leakage

    observation = observe(state, visible_keys=["object_id", "holding"])
    final_result = pick_up(state, "cube_001")
    return {
        "type": "lesson_session_result",
        "session_id": "session_2b2",
        "group": "2B-2",
        "decision_input_snapshot": snapshot,
        "actions": [
            {"action": "observe()", "result": observation},
            {"action": "pick_up(cube_001)", "result": final_result},
        ],
        "final_result": final_result,
        "used_lesson_ids": [],
        "success": final_result["result"] == "success",
    }


def run_phase_minus_one() -> dict[str, Any]:
    session_1 = run_session_1()
    lesson = session_1["lesson"]
    session_2a = run_session_2a_with_lesson(lesson)
    session_2b = run_session_2b_without_lesson()
    session_2b2 = run_session_2b2_without_lesson_with_turn_tool()
    snapshots = [
        session_2a["decision_input_snapshot"],
        session_2b["decision_input_snapshot"],
        session_2b2["decision_input_snapshot"],
    ]
    leakage_checks = [
        session_2b["decision_input_snapshot"]["leakage_check"],
        session_2b2["decision_input_snapshot"]["leakage_check"],
    ]
    summary = {
        "lesson_caused_behavior_shift": session_2a["success"] and not session_2b["success"] and not session_2b2["success"],
        "behavior_shift_traceable_to": session_2a["traceable_to"],
        "controls_failed_without_lesson": not session_2b["success"] and not session_2b2["success"],
        "leakage_passed": all(check["passed"] for check in leakage_checks),
    }
    return {
        "type": "phase_minus_one_result",
        "passed": all(
            [
                lesson is not None,
                session_2a["success"],
                not session_2b["success"],
                not session_2b2["success"],
                summary["lesson_caused_behavior_shift"],
                summary["behavior_shift_traceable_to"] == ["lesson_001"],
                summary["controls_failed_without_lesson"],
                summary["leakage_passed"],
            ]
        ),
        "session_1": session_1,
        "session_2a": session_2a,
        "session_2b": session_2b,
        "session_2b2": session_2b2,
        "snapshots": snapshots,
        "leakage_checks": leakage_checks,
        "summary": summary,
    }


def _lesson_001() -> dict[str, Any]:
    return run_session_1()["lesson"]


def _run_loaded_lesson_goal(lessons: list[dict[str, Any]], goal: dict[str, Any]) -> dict[str, Any]:
    state = build_initial_sandbox_state()
    available_actions = ["observe", "turn", goal["action"]]
    observation = observe(state)
    actions: list[dict[str, Any]] = [{"action": "observe()", "result": observation}]
    used_lesson_ids: list[str] = []

    applicable = find_applicable_lesson(lessons, goal)
    if applicable is not None:
        turned = turn(state, "east")
        state = turned["state"]
        used_lesson_ids.append(applicable["lesson_id"])
        actions.append({"action": "turn(east)", "result": turned, "caused_by_lesson_id": applicable["lesson_id"]})

    object_id = goal["object_id"]
    if goal["action"] == "pick_up":
        final_result = pick_up(state, object_id)
        action_name = f"pick_up({object_id})"
    elif goal["action"] == "push":
        final_result = push(state, object_id)
        action_name = f"push({object_id})"
    elif goal["action"] == "inspect":
        final_result = inspect(state, object_id)
        action_name = f"inspect({object_id})"
    else:
        final_result = {
            "type": "sandbox_action_result",
            "tool": goal["action"],
            "object_id": object_id,
            "result": "failed",
            "failure_reason": "unknown_action",
            "state": state,
        }
        action_name = f"{goal['action']}({object_id})"

    actions.append({"action": action_name, "result": final_result})
    return {
        "type": "negative_control_result",
        "goal": goal,
        "actions": actions,
        "final_result": final_result,
        "used_lesson_ids": used_lesson_ids,
        "success": final_result["result"] == "success",
        "turn_east_used": any(action["action"] == "turn(east)" for action in actions),
    }


def run_negative_control_wrong_object() -> dict[str, Any]:
    lesson = _lesson_001()
    result = _run_loaded_lesson_goal([lesson], {"action": "pick_up", "object_id": "cube_002", "target_type": "cube"})
    result["passed"] = result["used_lesson_ids"] == [] and not result["turn_east_used"]
    return result


def run_negative_control_wrong_action_push() -> dict[str, Any]:
    lesson = _lesson_001()
    result = _run_loaded_lesson_goal([lesson], {"action": "push", "object_id": "cube_001", "target_type": "cube"})
    result["passed"] = result["used_lesson_ids"] == [] and not result["turn_east_used"]
    return result


def run_negative_control_wrong_action_inspect() -> dict[str, Any]:
    lesson = _lesson_001()
    result = _run_loaded_lesson_goal([lesson], {"action": "inspect", "object_id": "cube_001", "target_type": "cube"})
    result["passed"] = result["used_lesson_ids"] == [] and not result["turn_east_used"]
    return result


def run_negative_control_wrong_condition() -> dict[str, Any]:
    wrong_lesson = dict(_lesson_001())
    wrong_lesson["lesson_id"] = "lesson_wrong_condition"
    wrong_lesson["condition"] = {"avatar_facing": "west"}
    wrong_lesson["suggested_action_before_retry"] = "turn(west)"
    result = _run_loaded_lesson_goal([wrong_lesson], {"action": "pick_up", "object_id": "cube_001", "target_type": "cube"})
    result["passed"] = (
        "lesson_wrong_condition" not in result["used_lesson_ids"]
        and not result["success"]
        and not result["turn_east_used"]
    )
    return result


def run_negative_control_unrelated_lesson() -> dict[str, Any]:
    unrelated = {
        "lesson_id": "lesson_unrelated",
        "source_session": "session_other",
        "source_failure_reason": "panel_closed",
        "trigger": {"action": "inspect", "target": "panel_001"},
        "condition": {},
        "suggested_action_before_retry": "do_nothing",
        "status": "active",
        "confidence": "synthetic",
    }
    result = _run_loaded_lesson_goal([unrelated], {"action": "pick_up", "object_id": "cube_001", "target_type": "cube"})
    result["passed"] = (
        result["used_lesson_ids"] == []
        and not result["success"]
        and result["final_result"]["failure_reason"] == "not_facing_east"
    )
    return result


def run_phase_minus_one_negative_controls() -> dict[str, Any]:
    wrong_object = run_negative_control_wrong_object()
    wrong_action_push = run_negative_control_wrong_action_push()
    wrong_action_inspect = run_negative_control_wrong_action_inspect()
    wrong_condition = run_negative_control_wrong_condition()
    unrelated_lesson = run_negative_control_unrelated_lesson()
    summary = {
        "lesson_001_strictly_bound_to_pick_up_cube_001": True,
        "no_wrong_object_generalization": wrong_object["passed"],
        "no_wrong_action_generalization": wrong_action_push["passed"] and wrong_action_inspect["passed"],
        "no_wrong_condition_success": wrong_condition["passed"],
        "no_unrelated_lesson_trigger": unrelated_lesson["passed"],
    }
    return {
        "type": "phase_minus_one_negative_controls_result",
        "passed": all(summary.values()),
        "wrong_object": wrong_object,
        "wrong_action_push": wrong_action_push,
        "wrong_action_inspect": wrong_action_inspect,
        "wrong_condition": wrong_condition,
        "unrelated_lesson": unrelated_lesson,
        "summary": summary,
    }
