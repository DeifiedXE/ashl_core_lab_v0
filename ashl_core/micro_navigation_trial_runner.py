"""Bounded trial runner for the tiny navigation sandbox."""

from __future__ import annotations

from typing import Any

from ashl_core.micro_navigation_sandbox import (
    DEFAULT_CANDIDATE_ACTIONS,
    apply_multi_goal_navigation_action,
    apply_navigation_action,
    build_initial_multi_goal_navigation_state,
    build_initial_navigation_state,
    select_navigation_action_toward_goal,
)


def run_navigation_goal_trial(
    candidate_actions: list[str] | tuple[str, ...] | None = None,
    max_steps: int = 10,
) -> dict[str, Any]:
    if max_steps < 0:
        raise ValueError("max_steps must be non-negative")

    candidates = tuple(candidate_actions) if candidate_actions is not None else DEFAULT_CANDIDATE_ACTIONS
    state = build_initial_navigation_state()
    goal_pos = tuple(state["goal_pos"])
    steps: list[dict[str, Any]] = []

    for step_index in range(max_steps):
        if tuple(state["agent_pos"]) == goal_pos:
            break
        selected_action = select_navigation_action_toward_goal(state, candidates)
        action_result = apply_navigation_action(state, selected_action)
        state = action_result["state"]
        trace = action_result["trace"]
        steps.append(
            {
                "step_index": step_index,
                "selected_action": selected_action,
                "navigation_result": trace["result"],
                "agent_pos": trace["agent_pos"],
                "goal_pos": trace["goal_pos"],
                "distance_to_goal": trace["distance_to_goal"],
                "trace": trace,
            }
        )
        if tuple(state["agent_pos"]) == goal_pos:
            break

    completed_goal = tuple(state["agent_pos"]) == goal_pos
    return {
        "completed_goal": completed_goal,
        "step_count": len(steps),
        "stop_reason": "goal_reached" if completed_goal else "max_steps_reached",
        "final_agent_pos": tuple(state["agent_pos"]),
        "goal_pos": goal_pos,
        "selected_actions": [step["selected_action"] for step in steps],
        "steps": steps,
    }


def run_navigation_multi_goal_trial(
    candidate_actions: list[str] | tuple[str, ...] | None = None,
    max_steps: int = 20,
) -> dict[str, Any]:
    if max_steps < 0:
        raise ValueError("max_steps must be non-negative")

    candidates = tuple(candidate_actions) if candidate_actions is not None else DEFAULT_CANDIDATE_ACTIONS
    state = build_initial_multi_goal_navigation_state()
    goal_count = len(state["goal_sequence"])
    steps: list[dict[str, Any]] = []

    for step_index in range(max_steps):
        if state["goals_reached"] == goal_count:
            break
        selected_action = select_navigation_action_toward_goal(state, candidates)
        action_result = apply_multi_goal_navigation_action(state, selected_action)
        state = action_result["state"]
        trace = action_result["trace"]
        steps.append(
            {
                "step_index": step_index,
                "selected_action": selected_action,
                "navigation_result": trace["result"],
                "agent_pos": trace["agent_pos"],
                "goal_pos": trace["goal_pos"],
                "distance_to_goal": trace["distance_to_goal"],
                "goal_reached_this_step": trace["goal_reached_this_step"],
                "goal_index": trace["goal_index"],
                "goals_reached": trace["goals_reached"],
                "next_goal_spawned": trace["next_goal_spawned"],
                "trace": trace,
            }
        )
        if state["goals_reached"] == goal_count:
            break

    completed_all_goals = state["goals_reached"] == goal_count
    return {
        "completed_all_goals": completed_all_goals,
        "goals_reached": state["goals_reached"],
        "goal_count": goal_count,
        "step_count": len(steps),
        "stop_reason": "all_goals_reached" if completed_all_goals else "max_steps_reached",
        "final_agent_pos": tuple(state["agent_pos"]),
        "final_goal_pos": tuple(state["goal_pos"]),
        "selected_actions": [step["selected_action"] for step in steps],
        "steps": steps,
    }
