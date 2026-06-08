"""Finite need-state driven trial runner for the micro push-box sandbox."""

from __future__ import annotations

import random
from typing import Any

from ashl_core.micro_push_box_sandbox import (
    apply_tactile_action,
    build_box_on_goal_need_state,
    build_initial_state,
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
        selection = select_action_for_need_state(state, candidate_actions, random_seed=step_seed)
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
