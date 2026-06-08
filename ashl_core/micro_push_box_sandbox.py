"""Tiny tactile push-box sandbox for deterministic contact traces."""

from __future__ import annotations

from copy import deepcopy
import random
from typing import Any


INITIAL_MAP = (
    "#####",
    "#...#",
    "#.QB#",
    "#..G#",
    "#####",
)

DIRECTIONS = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

ALLOWED_ACTION_SET = frozenset(
    {
        "touch_up",
        "touch_down",
        "touch_left",
        "touch_right",
        "move_up",
        "move_down",
        "move_left",
        "move_right",
        "push_up",
        "push_down",
        "push_left",
        "push_right",
        "wait",
    }
)

SUPPORTED_ACTIONS = tuple(
    action
    for prefix in ("touch", "move", "push")
    for action in (f"{prefix}_{direction}" for direction in ("up", "down", "left", "right"))
) + ("wait",)

BLOCKED_ACTION_RESULTS = frozenset({"box_blocked", "wall_blocked", "blocked"})

OUTCOME_WEIGHTS = {
    "box_blocked": -2,
    "wall_blocked": -2,
    "blocked": -2,
    "box_contact": 0,
    "empty": 0,
    "wait": 0,
    "box_pushed": 2,
    "goal_reached": 5,
}


def build_initial_state() -> dict[str, Any]:
    return _state_from_grid(INITIAL_MAP)


def validate_allowed_action(action: str) -> str:
    if action not in ALLOWED_ACTION_SET:
        raise ValueError(f"unsupported action: {action}")
    return action


def build_box_on_goal_need_state(state: dict[str, Any]) -> dict[str, Any]:
    current_value = 1 if tuple(state["box_pos"]) == tuple(state["goal_pos"]) else 0
    return {
        "need_name": "box_on_goal",
        "target_value": 1,
        "current_value": current_value,
        "satisfied": current_value == 1,
    }


def manhattan_distance_to_goal(box_pos: tuple[int, int], goal_pos: tuple[int, int]) -> int:
    return abs(box_pos[0] - goal_pos[0]) + abs(box_pos[1] - goal_pos[1])


def score_action_goal_direction(state: dict[str, Any], action: str) -> int:
    action = validate_allowed_action(action)
    if not action.startswith("push_"):
        return 0

    _, direction = action.split("_", 1)
    box_pos = tuple(state["box_pos"])
    goal_pos = tuple(state["goal_pos"])
    before_distance = manhattan_distance_to_goal(box_pos, goal_pos)
    after_distance = manhattan_distance_to_goal(_add(box_pos, DIRECTIONS[direction]), goal_pos)
    if after_distance < before_distance:
        return 2
    if after_distance > before_distance:
        return -2
    return 0


def suggest_next_action_avoiding_repeat_blocked(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...],
) -> str:
    validated_candidates = tuple(validate_allowed_action(action) for action in candidate_actions)
    blocked_actions = {
        entry.get("action")
        for entry in state.get("action_history", ())
        if entry.get("result") in BLOCKED_ACTION_RESULTS
    }

    for action in validated_candidates:
        if action not in blocked_actions:
            return action
    return "wait"


def score_action_from_history(state: dict[str, Any], action: str) -> int:
    action = validate_allowed_action(action)
    for entry in reversed(state.get("action_history", ())):
        if entry.get("action") == action:
            return OUTCOME_WEIGHTS.get(entry.get("result"), 0)
    return 0


def build_state_action_key(state: dict[str, Any], action: str) -> dict[str, Any]:
    action = validate_allowed_action(action)
    return {
        "agent_pos": tuple(state["agent_pos"]),
        "box_pos": tuple(state["box_pos"]),
        "goal_pos": tuple(state["goal_pos"]),
        "action": action,
    }


def find_previous_same_state_action_result(state: dict[str, Any], action: str) -> dict[str, Any] | None:
    key = build_state_action_key(state, action)
    for entry in reversed(state.get("action_history", ())):
        if (
            tuple(entry.get("agent_pos", ())) == key["agent_pos"]
            and tuple(entry.get("box_pos", ())) == key["box_pos"]
            and tuple(entry.get("goal_pos", ())) == key["goal_pos"]
            and entry.get("action") == key["action"]
        ):
            return entry
    return None


def score_action_from_state_action_memory(state: dict[str, Any], action: str) -> int:
    previous = find_previous_same_state_action_result(state, action)
    if previous is None:
        return 0
    return OUTCOME_WEIGHTS.get(previous.get("result"), 0)


def rank_candidate_actions_by_state_action_memory(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...],
) -> list[str]:
    validated_candidates = tuple(validate_allowed_action(action) for action in candidate_actions)
    indexed_scores = [
        (index, action, score_action_from_state_action_memory(state, action))
        for index, action in enumerate(validated_candidates)
    ]
    return [
        action
        for _, action, _ in sorted(indexed_scores, key=lambda item: (-item[2], item[0]))
    ]


def suggest_next_action_by_state_action_memory(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...],
) -> str:
    ranked = rank_candidate_actions_by_state_action_memory(state, candidate_actions)
    if not ranked:
        raise ValueError("candidate_actions must include at least one action")
    return ranked[0]


def rank_candidate_actions_by_outcome_weight(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...],
) -> list[str]:
    validated_candidates = tuple(validate_allowed_action(action) for action in candidate_actions)
    indexed_scores = [
        (index, action, score_action_from_history(state, action))
        for index, action in enumerate(validated_candidates)
    ]
    return [
        action
        for _, action, _ in sorted(indexed_scores, key=lambda item: (-item[2], item[0]))
    ]


def suggest_next_action_by_outcome_weight(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...],
) -> str:
    ranked = rank_candidate_actions_by_outcome_weight(state, candidate_actions)
    if not ranked:
        raise ValueError("candidate_actions must include at least one action")
    return ranked[0]


def rank_candidate_actions_with_goal_bias(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...],
) -> list[str]:
    validated_candidates = tuple(validate_allowed_action(action) for action in candidate_actions)
    indexed_scores = [
        (
            index,
            action,
            score_action_from_history(state, action) + score_action_goal_direction(state, action),
        )
        for index, action in enumerate(validated_candidates)
    ]
    return [
        action
        for _, action, _ in sorted(indexed_scores, key=lambda item: (-item[2], item[0]))
    ]


def suggest_next_action_with_goal_bias(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...],
) -> str:
    ranked = rank_candidate_actions_with_goal_bias(state, candidate_actions)
    if not ranked:
        raise ValueError("candidate_actions must include at least one action")
    return ranked[0]


def select_intrinsic_action(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...],
    random_seed: int | str | bytes | None = None,
) -> str:
    validated_candidates = tuple(validate_allowed_action(action) for action in candidate_actions)
    if not validated_candidates:
        raise ValueError("candidate_actions must include at least one action")

    scored_candidates = [
        (action, score_action_from_history(state, action))
        for action in validated_candidates
    ]
    best_score = max(score for _, score in scored_candidates)
    best_candidates = [
        action
        for action, score in scored_candidates
        if score == best_score
    ]
    rng = random.Random(random_seed)
    return rng.choice(best_candidates)


def select_action_for_need_state(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...],
    random_seed: int | str | bytes | None = None,
) -> dict[str, Any]:
    validated_candidates = tuple(validate_allowed_action(action) for action in candidate_actions)
    if not validated_candidates:
        raise ValueError("candidate_actions must include at least one action")

    need_state = build_box_on_goal_need_state(state)
    if need_state["satisfied"]:
        selected_action = "wait"
        selection_reason = "need_satisfied_wait"
    else:
        selected_action = select_intrinsic_action(state, validated_candidates, random_seed=random_seed)
        selection_reason = "need_unsatisfied_intrinsic_selection"

    return {
        "selected_action": selected_action,
        "need_state": need_state,
        "selection_reason": selection_reason,
        "candidate_actions": list(validated_candidates),
    }


def apply_tactile_action(state: dict[str, Any], action: str) -> dict[str, Any]:
    action = validate_allowed_action(action)

    before = _snapshot(state)
    after_state = _snapshot(state)
    result = "empty"
    contact = "none"
    blocked = False

    if action == "wait":
        after_state["tick"] = before["tick"] + 1
        return _build_trace_result(action, before, after_state, contact, "wait", blocked)

    prefix, direction = action.split("_", 1)
    delta = DIRECTIONS[direction]
    target = _add(before["agent_pos"], delta)
    contact = _contact_at(before, target)

    if prefix == "touch":
        result, blocked = _touch_result(contact)
    elif prefix == "move":
        result, blocked = _move(after_state, target, contact)
    elif prefix == "push":
        result, blocked, contact = _push(after_state, target, delta, contact)

    after_state["tick"] = before["tick"] + 1
    return _build_trace_result(action, before, after_state, contact, result, blocked)


def _build_trace_result(
    action: str,
    before: dict[str, Any],
    after_state: dict[str, Any],
    contact: str,
    result: str,
    blocked: bool,
) -> dict[str, Any]:
    history = _history_for_action(before.get("action_history", ()), action)
    after_state["action_history"] = tuple(before.get("action_history", ())) + (
        {
            "agent_pos": before["agent_pos"],
            "box_pos": before["box_pos"],
            "goal_pos": before["goal_pos"],
            "action": action,
            "result": result,
            "tick": after_state["tick"],
            "blocked": blocked,
            "contact": contact,
        },
    )
    trace = {
        "trace_type": "tactile_sandbox_trace",
        "tick": after_state["tick"],
        "action": action,
        "before": before,
        "after": _snapshot(after_state),
        "contact": contact,
        "result": result,
        "blocked": blocked,
        "history": history,
        "need_state": build_box_on_goal_need_state(after_state),
        "agent_pos": after_state["agent_pos"],
        "box_pos": after_state["box_pos"],
        "goal_pos": after_state["goal_pos"],
    }
    return {"state": after_state, "trace": trace}


def _state_from_grid(grid: tuple[str, ...]) -> dict[str, Any]:
    agent_pos = box_pos = goal_pos = None
    normalized = []
    for row_index, row in enumerate(grid):
        normalized_row = []
        for col_index, cell in enumerate(row):
            pos = (row_index, col_index)
            if cell == "Q":
                agent_pos = pos
                normalized_row.append(".")
            elif cell == "B":
                box_pos = pos
                normalized_row.append(".")
            elif cell == "G":
                goal_pos = pos
                normalized_row.append("G")
            else:
                normalized_row.append(cell)
        normalized.append("".join(normalized_row))
    if agent_pos is None or box_pos is None or goal_pos is None:
        raise ValueError("grid must include Q, B, and G")
    return {
        "grid": tuple(normalized),
        "agent_pos": agent_pos,
        "box_pos": box_pos,
        "goal_pos": goal_pos,
        "tick": 0,
        "action_history": (),
    }


def _snapshot(state: dict[str, Any]) -> dict[str, Any]:
    copied = deepcopy(state)
    copied["grid"] = tuple(copied["grid"])
    copied["agent_pos"] = tuple(copied["agent_pos"])
    copied["box_pos"] = tuple(copied["box_pos"])
    copied["goal_pos"] = tuple(copied["goal_pos"])
    copied["action_history"] = tuple(copied.get("action_history", ()))
    return copied


def _history_for_action(action_history: tuple[dict[str, Any], ...], action: str) -> dict[str, Any]:
    for entry in reversed(action_history):
        if entry.get("action") == action:
            return {
                "same_action_attempted_before": True,
                "previous_same_action_result": entry.get("result"),
                "previous_same_action_tick": entry.get("tick"),
            }
    return {"same_action_attempted_before": False}


def _add(pos: tuple[int, int], delta: tuple[int, int]) -> tuple[int, int]:
    return (pos[0] + delta[0], pos[1] + delta[1])


def _cell_at(state: dict[str, Any], pos: tuple[int, int]) -> str:
    row, col = pos
    if row < 0 or col < 0 or row >= len(state["grid"]) or col >= len(state["grid"][row]):
        return "#"
    return state["grid"][row][col]


def _contact_at(state: dict[str, Any], pos: tuple[int, int]) -> str:
    if pos == state["box_pos"]:
        return "box"
    if _cell_at(state, pos) == "#":
        return "wall"
    if pos == state["goal_pos"]:
        return "goal"
    return "empty"


def _touch_result(contact: str) -> tuple[str, bool]:
    if contact == "wall":
        return "wall_blocked", True
    if contact == "box":
        return "box_contact", False
    if contact == "goal":
        return "goal_reached", False
    return "empty", False


def _move(state: dict[str, Any], target: tuple[int, int], contact: str) -> tuple[str, bool]:
    if contact == "wall":
        return "wall_blocked", True
    if contact == "box":
        return "box_blocked", True
    state["agent_pos"] = target
    if contact == "goal":
        return "goal_reached", False
    return "empty", False


def _push(
    state: dict[str, Any],
    target: tuple[int, int],
    delta: tuple[int, int],
    contact: str,
) -> tuple[str, bool, str]:
    if contact == "wall":
        return "wall_blocked", True, contact
    if contact != "box":
        return "empty", True, contact

    box_destination = _add(state["box_pos"], delta)
    destination_contact = _contact_at({**state, "box_pos": (-1, -1)}, box_destination)
    if destination_contact == "wall" or destination_contact == "box":
        return "box_blocked", True, "box"

    state["agent_pos"] = target
    state["box_pos"] = box_destination
    if box_destination == state["goal_pos"]:
        return "goal_reached", False, "box"
    return "box_pushed", False, "box"
