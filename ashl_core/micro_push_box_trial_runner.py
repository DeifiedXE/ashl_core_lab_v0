"""Finite need-state driven trial runner for the micro push-box sandbox."""

from __future__ import annotations

import random
from typing import Any

from ashl_core.micro_push_box_sandbox import (
    DIRECTIONS,
    apply_tactile_action,
    build_box_on_goal_need_state,
    build_initial_state,
    score_action_from_history,
    score_action_from_state_action_memory,
    score_action_goal_direction,
    select_action_for_need_state,
)


def run_need_state_driven_trial(
    candidate_actions: list[str] | tuple[str, ...],
    max_steps: int = 10,
    random_seed: int | str | bytes | None = None,
) -> dict[str, Any]:
    if max_steps < 0:
        raise ValueError("max_steps must be non-negative")

    rng = random.Random(random_seed)
    state = build_initial_state()
    steps: list[dict[str, Any]] = []
    final_result = None

    initial_need_state = build_box_on_goal_need_state(state)
    if initial_need_state["satisfied"]:
        return _build_trial_result(True, "need_satisfied", initial_need_state, final_result, steps)

    for step_index in range(max_steps):
        step_seed = rng.randrange(2**32)
        selection = _select_action_for_trial(state, candidate_actions, recent_steps=steps, random_seed=step_seed)
        action_result = apply_tactile_action(state, selection["selected_action"])
        state = action_result["state"]
        trace = action_result["trace"]
        final_result = trace["result"]
        need_state = trace["need_state"]
        steps.append(
            {
                "step_index": step_index,
                "selected_action": selection["selected_action"],
                "selection_reason": selection["selection_reason"],
                "selection_source": selection["selection_source"],
                "state_action_memory_used": selection["state_action_memory_used"],
                "stuck_detected_before_selection": selection["stuck_detected_before_selection"],
                "repetition_penalty_applied": selection["repetition_penalty_applied"],
                "tactile_result": trace["result"],
                "need_state": need_state,
                "agent_pos": trace["agent_pos"],
                "box_pos": trace["box_pos"],
                "trace": trace,
            }
        )
        if need_state["satisfied"]:
            return _build_trial_result(True, "need_satisfied", need_state, final_result, steps)

    final_need_state = build_box_on_goal_need_state(state)
    return _build_trial_result(False, "max_steps_reached", final_need_state, final_result, steps)


def run_need_state_driven_trial_batch(
    trial_count: int = 5,
    candidate_actions: list[str] | tuple[str, ...] | None = None,
    max_steps: int = 10,
    random_seed: int | str | bytes | None = None,
) -> dict[str, Any]:
    if trial_count < 0:
        raise ValueError("trial_count must be non-negative")

    candidates = tuple(candidate_actions) if candidate_actions is not None else ("move_up", "move_right", "push_down")
    trials = []
    for trial_index in range(trial_count):
        trial_seed = _trial_seed(random_seed, trial_index)
        trial = run_need_state_driven_trial(candidates, max_steps=max_steps, random_seed=trial_seed)
        trials.append(
            {
                "trial_index": trial_index,
                "completed_goal": trial["completed_goal"],
                "stop_reason": trial["stop_reason"],
                "step_count": trial["step_count"],
                "final_need_state": trial["final_need_state"],
                "selected_actions": [step["selected_action"] for step in trial["steps"]],
            }
        )

    step_counts = [trial["step_count"] for trial in trials]
    completed_count = sum(1 for trial in trials if trial["completed_goal"])
    return {
        "trial_count": trial_count,
        "completed_count": completed_count,
        "step_counts": step_counts,
        "average_step_count": (sum(step_counts) / len(step_counts)) if step_counts else 0,
        "min_step_count": min(step_counts) if step_counts else 0,
        "max_step_count": max(step_counts) if step_counts else 0,
        "trials": trials,
    }


def _build_trial_result(
    completed_goal: bool,
    stop_reason: str,
    final_need_state: dict[str, Any],
    final_result: str | None,
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "completed_goal": completed_goal,
        "stop_reason": stop_reason,
        "step_count": len(steps),
        "final_need_state": final_need_state,
        "final_result": final_result,
        "steps": steps,
    }


def _select_action_for_trial(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...],
    recent_steps: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    random_seed: int | str | bytes | None = None,
) -> dict[str, Any]:
    recent_steps = tuple(recent_steps or ())
    stuck_detected = detect_stuck_from_recent_steps(recent_steps)
    base_selection = select_action_for_need_state(state, candidate_actions, random_seed=random_seed)
    if base_selection["need_state"]["satisfied"]:
        return {
            **base_selection,
            "selection_source": "need_satisfied_wait",
            "state_action_memory_used": False,
            "stuck_detected_before_selection": stuck_detected,
            "repetition_penalty_applied": 0,
        }

    selected_action = base_selection["selected_action"]
    for action in _rank_candidate_actions_for_trial(state, base_selection["candidate_actions"], recent_steps):
        if score_action_goal_direction(state, action) <= 0:
            continue
        if not _push_contacts_box(state, action):
            continue
        selected_action = action
        break

    return {
        **base_selection,
        "selected_action": selected_action,
        "selection_reason": "need_unsatisfied_goal_bias_selection",
        "selection_source": "state_action_memory_plus_outcome_weight_plus_goal_bias_plus_repetition_penalty",
        "state_action_memory_used": True,
        "stuck_detected_before_selection": stuck_detected,
        "repetition_penalty_applied": score_action_repetition_penalty(recent_steps, selected_action),
    }


def detect_stuck_from_recent_steps(
    steps: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    window_size: int = 3,
) -> bool:
    if window_size <= 0:
        raise ValueError("window_size must be positive")
    if len(steps) < window_size:
        return False

    recent = tuple(steps[-window_size:])
    actions = [step.get("selected_action") for step in recent]
    if len(set(actions)) != 1:
        return False
    if any(step.get("tactile_result") == "goal_reached" for step in recent):
        return False

    values = [
        (step.get("need_state") or {}).get("current_value")
        for step in recent
    ]
    return len(set(values)) == 1


def score_action_repetition_penalty(
    steps: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    action: str,
    window_size: int = 3,
) -> int:
    if window_size <= 0:
        raise ValueError("window_size must be positive")
    recent = tuple(steps[-window_size:])
    repeat_count = sum(1 for step in recent if step.get("selected_action") == action)
    if repeat_count >= 3:
        return -4
    if repeat_count == 2:
        return -2
    return 0


def _rank_candidate_actions_for_trial(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...],
    recent_steps: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
) -> list[str]:
    indexed_scores = [
        (
            index,
            action,
            score_action_from_state_action_memory(state, action)
            + score_action_from_history(state, action)
            + score_action_goal_direction(state, action)
            + score_action_repetition_penalty(recent_steps, action),
        )
        for index, action in enumerate(candidate_actions)
    ]
    return [
        action
        for _, action, _ in sorted(indexed_scores, key=lambda item: (-item[2], item[0]))
    ]


def _push_contacts_box(state: dict[str, Any], action: str) -> bool:
    if not action.startswith("push_"):
        return False
    _, direction = action.split("_", 1)
    agent_pos = tuple(state["agent_pos"])
    box_pos = tuple(state["box_pos"])
    delta = DIRECTIONS[direction]
    return (agent_pos[0] + delta[0], agent_pos[1] + delta[1]) == box_pos


def _trial_seed(random_seed: int | str | bytes | None, trial_index: int) -> int | str | bytes | None:
    if random_seed is None:
        return None
    if isinstance(random_seed, int):
        return random_seed + trial_index
    if isinstance(random_seed, bytes):
        return random_seed + str(trial_index).encode("ascii")
    return f"{random_seed}{trial_index}"
