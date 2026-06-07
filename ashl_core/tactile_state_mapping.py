"""Fixed tactile-result to state_key mapping."""

from __future__ import annotations


TACTILE_RESULT_TO_STATE_KEY = {
    "wall_blocked": "blocked",
    "box_blocked": "blocked",
    "box_contact": "observed",
    "box_pushed": "observed",
    "goal_reached": "observed",
    "empty": "quiet",
}


def map_tactile_result_to_state_key(result: str) -> str:
    if result not in TACTILE_RESULT_TO_STATE_KEY:
        raise ValueError(f"unsupported tactile result: {result}")
    return TACTILE_RESULT_TO_STATE_KEY[result]
