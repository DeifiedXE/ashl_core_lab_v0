"""Tiny deterministic navigation sandbox for reaching fixed navigation goals."""

from __future__ import annotations

from typing import Any


INITIAL_MAP = (
    "#####",
    "#...#",
    "#.Q.#",
    "#..G#",
    "#####",
)

MULTI_GOAL_LEVEL_MAP = (
    "#######",
    "#Q....#",
    "#.###.#",
    "#....G#",
    "#######",
)

APPROACH_BOX_LEVEL_MAP = (
    "#######",
    "#Q....#",
    "#.###.#",
    "#...B.#",
    "#######",
)

MULTI_GOAL_SEQUENCE = ((3, 5), (3, 1))

DIRECTIONS = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

ALLOWED_NAVIGATION_ACTIONS = frozenset(
    {
        "move_up",
        "move_down",
        "move_left",
        "move_right",
        "wait",
    }
)

DEFAULT_CANDIDATE_ACTIONS = ("move_up", "move_down", "move_left", "move_right", "wait")


def build_initial_navigation_state() -> dict[str, Any]:
    return _state_from_grid(INITIAL_MAP)


def build_initial_multi_goal_navigation_state() -> dict[str, Any]:
    state = _state_from_grid(MULTI_GOAL_LEVEL_MAP)
    state["goal_sequence"] = MULTI_GOAL_SEQUENCE
    state["goal_index"] = 0
    state["goals_reached"] = 0
    state["goal_pos"] = MULTI_GOAL_SEQUENCE[0]
    state["grid"] = _render_grid(state)
    return state


def create_navigation_obstacle_level_state() -> dict[str, Any]:
    return _state_from_grid(MULTI_GOAL_LEVEL_MAP)


def create_navigation_approach_box_level_state() -> dict[str, Any]:
    return _approach_box_state_from_grid(APPROACH_BOX_LEVEL_MAP)


def validate_navigation_action(action: str) -> str:
    if action not in ALLOWED_NAVIGATION_ACTIONS:
        raise ValueError(f"unsupported navigation action: {action}")
    return action


def manhattan_distance_to_goal(agent_pos: tuple[int, int], goal_pos: tuple[int, int]) -> int:
    return abs(agent_pos[0] - goal_pos[0]) + abs(agent_pos[1] - goal_pos[1])


def manhattan_distance_to_box(agent_pos: tuple[int, int], box_pos: tuple[int, int]) -> int:
    return abs(agent_pos[0] - box_pos[0]) + abs(agent_pos[1] - box_pos[1])


def select_navigation_action_toward_goal(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...] | None = None,
) -> str:
    candidates = tuple(candidate_actions) if candidate_actions is not None else DEFAULT_CANDIDATE_ACTIONS
    validated_candidates = tuple(validate_navigation_action(action) for action in candidates)
    if not validated_candidates:
        raise ValueError("candidate_actions must include at least one action")

    agent_pos = tuple(state["agent_pos"])
    goal_pos = tuple(state["goal_pos"])
    current_distance = manhattan_distance_to_goal(agent_pos, goal_pos)
    for action in validated_candidates:
        if not action.startswith("move_"):
            continue
        _, direction = action.split("_", 1)
        target = _add(agent_pos, DIRECTIONS[direction])
        if _tile_at(state, target) == "#":
            continue
        if manhattan_distance_to_goal(target, goal_pos) < current_distance:
            return action
    return validated_candidates[0]


def select_navigation_action_blocked_aware(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    candidates = tuple(candidate_actions) if candidate_actions is not None else DEFAULT_CANDIDATE_ACTIONS
    validated_candidates = tuple(validate_navigation_action(action) for action in candidates)
    if not validated_candidates:
        raise ValueError("candidate_actions must include at least one action")

    agent_pos = tuple(state["agent_pos"])
    goal_pos = tuple(state["goal_pos"])
    considered_moves: list[dict[str, Any]] = []
    blocked_candidates: list[str] = []
    best_action = None
    best_distance = None

    for action in validated_candidates:
        if not action.startswith("move_"):
            continue
        _, direction = action.split("_", 1)
        target = _add(agent_pos, DIRECTIONS[direction])
        if _tile_at(state, target) == "#":
            blocked_candidates.append(action)
            considered_moves.append({"action": action, "target": target, "blocked": True, "distance_to_goal": None})
            continue
        distance = manhattan_distance_to_goal(target, goal_pos)
        considered_moves.append({"action": action, "target": target, "blocked": False, "distance_to_goal": distance})
        if best_distance is None or distance < best_distance:
            best_action = action
            best_distance = distance

    selected_action = best_action if best_action is not None else validated_candidates[0]
    return {
        "selected_action": selected_action,
        "selection_rule": "blocked_aware_min_distance",
        "blocked_candidates": blocked_candidates,
        "considered_moves": considered_moves,
    }


def select_navigation_action_toward_box(
    state: dict[str, Any],
    candidate_actions: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    candidates = tuple(candidate_actions) if candidate_actions is not None else DEFAULT_CANDIDATE_ACTIONS
    validated_candidates = tuple(validate_navigation_action(action) for action in candidates)
    if not validated_candidates:
        raise ValueError("candidate_actions must include at least one action")

    agent_pos = tuple(state["agent_pos"])
    box_pos = tuple(state["box_pos"])
    considered_moves: list[dict[str, Any]] = []
    blocked_candidates: list[str] = []
    best_action = None
    best_distance = None

    for action in validated_candidates:
        if not action.startswith("move_"):
            continue
        _, direction = action.split("_", 1)
        target = _add(agent_pos, DIRECTIONS[direction])
        tile = _approach_box_tile_at(state, target)
        if tile in {"#", "B"}:
            blocked_candidates.append(action)
            considered_moves.append({"action": action, "target": target, "blocked": True, "distance_to_box": None})
            continue
        distance = manhattan_distance_to_box(target, box_pos)
        considered_moves.append({"action": action, "target": target, "blocked": False, "distance_to_box": distance})
        if best_distance is None or distance < best_distance:
            best_action = action
            best_distance = distance

    selected_action = best_action if best_action is not None else validated_candidates[0]
    return {
        "selected_action": selected_action,
        "selection_rule": "toward_box_blocked_aware_min_distance",
        "blocked_candidates": blocked_candidates,
        "considered_moves": considered_moves,
    }


def apply_navigation_action(state: dict[str, Any], action: str) -> dict[str, Any]:
    action = validate_navigation_action(action)
    before = _snapshot(state)
    after = _snapshot(state)
    blocked = False

    if action == "wait":
        result = "wait"
    else:
        _, direction = action.split("_", 1)
        target = _add(tuple(before["agent_pos"]), DIRECTIONS[direction])
        if _tile_at(before, target) == "#":
            result = "wall_blocked"
            blocked = True
        else:
            after["agent_pos"] = target
            result = "goal_reached" if target == tuple(before["goal_pos"]) else "moved"

    after["tick"] = before["tick"] + 1
    after["grid"] = _render_grid(after)
    trace = {
        "trace_type": "navigation_sandbox_trace",
        "tick": after["tick"],
        "action": action,
        "before": before,
        "after": after,
        "result": result,
        "blocked": blocked,
        "agent_pos": after["agent_pos"],
        "goal_pos": after["goal_pos"],
        "distance_to_goal": manhattan_distance_to_goal(tuple(after["agent_pos"]), tuple(after["goal_pos"])),
    }
    return {"state": after, "trace": trace}


def apply_navigation_approach_box_action(state: dict[str, Any], action: str) -> dict[str, Any]:
    action = validate_navigation_action(action)
    before = _snapshot(state)
    after = _snapshot(state)
    blocked = False

    if action == "wait":
        result = "wait"
    else:
        _, direction = action.split("_", 1)
        target = _add(tuple(before["agent_pos"]), DIRECTIONS[direction])
        tile = _approach_box_tile_at(before, target)
        if tile == "#":
            result = "wall_blocked"
            blocked = True
        elif tile == "B":
            result = "box_adjacent"
            blocked = True
        else:
            after["agent_pos"] = target
            result = "box_adjacent" if manhattan_distance_to_box(target, tuple(before["box_pos"])) == 1 else "moved"

    after["tick"] = before["tick"] + 1
    after["grid"] = _render_grid(after)
    distance_to_box = manhattan_distance_to_box(tuple(after["agent_pos"]), tuple(after["box_pos"]))
    trace = {
        "trace_type": "navigation_approach_box_trace",
        "tick": after["tick"],
        "action": action,
        "before": before,
        "after": after,
        "result": result,
        "blocked": blocked,
        "agent_pos": after["agent_pos"],
        "box_pos": after["box_pos"],
        "distance_to_box": distance_to_box,
        "box_adjacent": distance_to_box == 1,
    }
    return {"state": after, "trace": trace}


def apply_multi_goal_navigation_action(state: dict[str, Any], action: str) -> dict[str, Any]:
    action = validate_navigation_action(action)
    before = _snapshot(state)
    after = _snapshot(state)
    blocked = False
    goal_reached_this_step = False
    next_goal_spawned = False

    if action == "wait":
        result = "wait"
    else:
        _, direction = action.split("_", 1)
        target = _add(tuple(before["agent_pos"]), DIRECTIONS[direction])
        if _tile_at(before, target) == "#":
            result = "wall_blocked"
            blocked = True
        else:
            after["agent_pos"] = target
            if target == tuple(before["goal_pos"]):
                goal_reached_this_step = True
                after["goals_reached"] = before["goals_reached"] + 1
                after["goal_index"] = before["goal_index"] + 1
                if after["goal_index"] < len(after["goal_sequence"]):
                    after["goal_pos"] = tuple(after["goal_sequence"][after["goal_index"]])
                    next_goal_spawned = True
                result = "goal_reached"
            else:
                result = "moved"

    after["tick"] = before["tick"] + 1
    after["grid"] = _render_grid(after)
    trace = {
        "trace_type": "navigation_multi_goal_sandbox_trace",
        "tick": after["tick"],
        "action": action,
        "before": before,
        "after": after,
        "result": result,
        "blocked": blocked,
        "agent_pos": after["agent_pos"],
        "goal_pos": after["goal_pos"],
        "distance_to_goal": manhattan_distance_to_goal(tuple(after["agent_pos"]), tuple(after["goal_pos"])),
        "goal_reached_this_step": goal_reached_this_step,
        "goal_index": after["goal_index"],
        "goals_reached": after["goals_reached"],
        "next_goal_spawned": next_goal_spawned,
    }
    return {"state": after, "trace": trace}


def _state_from_grid(grid: tuple[str, ...]) -> dict[str, Any]:
    agent_pos = None
    goal_pos = None
    for row_index, row in enumerate(grid):
        for col_index, char in enumerate(row):
            if char == "Q":
                agent_pos = (row_index, col_index)
            elif char == "G":
                goal_pos = (row_index, col_index)
    if agent_pos is None or goal_pos is None:
        raise ValueError("navigation grid must include Q and G")
    state = {
        "base_grid": grid,
        "grid": grid,
        "agent_pos": agent_pos,
        "goal_pos": goal_pos,
        "tick": 0,
    }
    state["grid"] = _render_grid(state)
    return state


def _approach_box_state_from_grid(grid: tuple[str, ...]) -> dict[str, Any]:
    agent_pos = None
    box_pos = None
    for row_index, row in enumerate(grid):
        for col_index, char in enumerate(row):
            if char == "Q":
                agent_pos = (row_index, col_index)
            elif char == "B":
                box_pos = (row_index, col_index)
    if agent_pos is None or box_pos is None:
        raise ValueError("approach box grid must include Q and B")
    state = {
        "base_grid": grid,
        "grid": grid,
        "agent_pos": agent_pos,
        "box_pos": box_pos,
        "tick": 0,
    }
    state["grid"] = _render_grid(state)
    return state


def _snapshot(state: dict[str, Any]) -> dict[str, Any]:
    snapshot = {
        "base_grid": tuple(state.get("base_grid", INITIAL_MAP)),
        "grid": tuple(state["grid"]),
        "agent_pos": tuple(state["agent_pos"]),
        "tick": state["tick"],
    }
    if "goal_pos" in state:
        snapshot["goal_pos"] = tuple(state["goal_pos"])
    if "box_pos" in state:
        snapshot["box_pos"] = tuple(state["box_pos"])
    if "goal_sequence" in state:
        snapshot["goal_sequence"] = tuple(tuple(goal) for goal in state["goal_sequence"])
        snapshot["goal_index"] = state["goal_index"]
        snapshot["goals_reached"] = state["goals_reached"]
    return snapshot


def _render_grid(state: dict[str, Any]) -> tuple[str, ...]:
    base = [list(row) for row in state.get("base_grid", INITIAL_MAP)]
    for row_index, row in enumerate(base):
        for col_index, char in enumerate(row):
            if char in {"Q", "G"}:
                base[row_index][col_index] = "."
    agent_pos = tuple(state["agent_pos"])
    if "box_pos" in state:
        box_pos = tuple(state["box_pos"])
        base[box_pos[0]][box_pos[1]] = "B"
        if agent_pos != box_pos:
            base[agent_pos[0]][agent_pos[1]] = "Q"
    elif "goal_pos" in state:
        goal_pos = tuple(state["goal_pos"])
        if agent_pos == goal_pos:
            base[goal_pos[0]][goal_pos[1]] = "Q"
        else:
            base[goal_pos[0]][goal_pos[1]] = "G"
            base[agent_pos[0]][agent_pos[1]] = "Q"
    else:
        base[agent_pos[0]][agent_pos[1]] = "Q"
    return tuple("".join(row) for row in base)


def _tile_at(state: dict[str, Any], pos: tuple[int, int]) -> str:
    if pos == tuple(state["goal_pos"]):
        return "G"
    return state["grid"][pos[0]][pos[1]]


def _approach_box_tile_at(state: dict[str, Any], pos: tuple[int, int]) -> str:
    if pos == tuple(state["box_pos"]):
        return "B"
    return state["grid"][pos[0]][pos[1]]


def _add(pos: tuple[int, int], delta: tuple[int, int]) -> tuple[int, int]:
    return (pos[0] + delta[0], pos[1] + delta[1])
