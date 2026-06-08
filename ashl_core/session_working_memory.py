"""Session-local generic state-action-outcome working memory."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


SUPPORTED_OUTCOME_TYPES = {
    "moved",
    "blocked",
    "no_progress",
    "entered_trap",
    "goal_progress",
    "goal_reached",
    "unknown",
}


def create_session_working_memory(max_records: int = 20) -> dict[str, Any]:
    if max_records <= 0:
        raise ValueError("max_records must be positive")
    return {
        "type": "session_working_memory",
        "scope": "session_local",
        "max_records": max_records,
        "records": [],
        "boundary": {
            "session_local_only": True,
            "persistent_memory_write": False,
            "lesson_store_write": False,
            "memory_layer_write": False,
            "long_term_memory_write": False,
            "action_selection_modified": False,
            "used_llm": False,
            "used_pathfinding": False,
        },
    }


def build_session_outcome_record(
    *,
    tick: int,
    state_snapshot: dict[str, Any],
    action: str,
    outcome_type: str,
    failure_reasons: list[str] | tuple[str, ...] | None = None,
    metadata: dict[str, Any] | None = None,
    state_key: str | None = None,
    target: Any = None,
    outcome_detail: str | None = None,
    effect_tags: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    if outcome_type not in SUPPORTED_OUTCOME_TYPES:
        raise ValueError(f"unsupported outcome_type: {outcome_type}")
    if failure_reasons is None:
        normalized_failure_reasons: list[str] = []
    elif isinstance(failure_reasons, (list, tuple)):
        normalized_failure_reasons = [str(reason) for reason in failure_reasons]
    else:
        raise TypeError("failure_reasons must be a list")
    return {
        "tick": tick,
        "state_key": state_key,
        "state_snapshot": deepcopy(state_snapshot),
        "action": action,
        "target": deepcopy(target),
        "outcome_type": outcome_type,
        "outcome_detail": outcome_detail,
        "failure_reasons": normalized_failure_reasons,
        "effect_tags": list(effect_tags or []),
        "metadata": deepcopy(metadata or {}),
    }


def append_outcome_record(memory: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    _validate_memory(memory)
    _validate_record(record)
    memory["records"].append(deepcopy(record))
    max_records = memory["max_records"]
    if len(memory["records"]) > max_records:
        memory["records"] = memory["records"][-max_records:]
    return memory


def query_recent_outcomes(
    memory: dict[str, Any],
    *,
    state_snapshot: dict[str, Any] | None = None,
    action: str | None = None,
    outcome_type: str | None = None,
) -> list[dict[str, Any]]:
    _validate_memory(memory)
    results = []
    for record in memory["records"]:
        if state_snapshot is not None and record["state_snapshot"] != state_snapshot:
            continue
        if action is not None and record["action"] != action:
            continue
        if outcome_type is not None and record["outcome_type"] != outcome_type:
            continue
        results.append(deepcopy(record))
    return results


def clear_session_working_memory(memory: dict[str, Any]) -> dict[str, Any]:
    _validate_memory(memory)
    memory["records"] = []
    return memory


def _validate_memory(memory: dict[str, Any]) -> None:
    if memory.get("type") != "session_working_memory":
        raise ValueError("memory must be a session_working_memory")
    if "records" not in memory or not isinstance(memory["records"], list):
        raise ValueError("memory records must be a list")
    if "max_records" not in memory or memory["max_records"] <= 0:
        raise ValueError("memory max_records must be positive")


def _validate_record(record: dict[str, Any]) -> None:
    required_fields = {"tick", "state_snapshot", "action", "outcome_type", "failure_reasons", "metadata"}
    missing = required_fields.difference(record)
    if missing:
        raise ValueError(f"missing required record fields: {sorted(missing)}")
    if record["outcome_type"] not in SUPPORTED_OUTCOME_TYPES:
        raise ValueError(f"unsupported outcome_type: {record['outcome_type']}")
    if not isinstance(record["failure_reasons"], list):
        raise TypeError("failure_reasons must be a list")
