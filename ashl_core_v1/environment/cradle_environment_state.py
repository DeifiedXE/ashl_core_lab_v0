"""Explicit environment state records for fixed ASHL Core v1 cradle cases."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.cradle_cases import build_cradle_case_sample, list_cradle_case_ids
from ashl_core_v1.runtime.cradle_session import load_current_cradle_session


CRADLE_ENVIRONMENT_STATE_ENV = "ASHL_CORE_V1_CRADLE_ENVIRONMENT_STATE_DIR"
DEFAULT_CRADLE_ENVIRONMENT_STATE_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "cradle_environment"
)

LAST_CRADLE_ENVIRONMENT_STATE_FILE = "last_cradle_environment_state.json"
CRADLE_ENVIRONMENT_STATE_HISTORY_FILE = "cradle_environment_state_history.jsonl"

_CASE_FRONT_STATE: dict[str, dict[str, Any]] = {
    "blocked_front_obstacle": {
        "kind": "obstacle",
        "blocked": True,
        "unknown": False,
        "object_id": "front_obstacle",
        "summary": "front is blocked by an obstacle",
        "available_operations": ("observe", "wait", "adjust"),
        "visible_objects": (
            {
                "object_id": "front_obstacle",
                "object_kind": "obstacle",
                "position": {"x": 0, "y": 1},
                "state": "blocking",
            },
        ),
        "interactive_objects": (),
    },
    "success_front_step": {
        "kind": "open",
        "blocked": False,
        "unknown": False,
        "object_id": None,
        "summary": "front is open after a successful step",
        "available_operations": ("observe", "step_forward"),
        "visible_objects": (),
        "interactive_objects": (),
    },
    "unknown_feedback": {
        "kind": "unknown",
        "blocked": False,
        "unknown": True,
        "object_id": None,
        "summary": "front state is unknown and needs observation",
        "available_operations": ("observe", "inspect", "wait"),
        "visible_objects": (),
        "interactive_objects": (),
    },
    "teacher_rejected": {
        "kind": "review_limited",
        "blocked": False,
        "unknown": True,
        "object_id": None,
        "summary": "teacher rejected the learning path; observe or wait",
        "available_operations": ("observe", "wait"),
        "visible_objects": (),
        "interactive_objects": (),
    },
    "teacher_deferred": {
        "kind": "review_limited",
        "blocked": False,
        "unknown": True,
        "object_id": None,
        "summary": "teacher deferred the learning path; observe or wait",
        "available_operations": ("observe", "wait"),
        "visible_objects": (),
        "interactive_objects": (),
    },
    "conflict_detected": {
        "kind": "review_limited",
        "blocked": False,
        "unknown": True,
        "object_id": None,
        "summary": "conflicting feedback needs review before trust",
        "available_operations": ("observe", "wait"),
        "visible_objects": (),
        "interactive_objects": (),
    },
    "stale_learning": {
        "kind": "outdated_trace",
        "blocked": False,
        "unknown": True,
        "object_id": None,
        "summary": "learning is stale and should be refreshed",
        "available_operations": ("observe", "inspect"),
        "visible_objects": (),
        "interactive_objects": (),
    },
    "superseded_learning": {
        "kind": "outdated_trace",
        "blocked": False,
        "unknown": True,
        "object_id": None,
        "summary": "learning was superseded and should be refreshed",
        "available_operations": ("observe", "inspect"),
        "visible_objects": (),
        "interactive_objects": (),
    },
}


def resolve_cradle_environment_state_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(CRADLE_ENVIRONMENT_STATE_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_CRADLE_ENVIRONMENT_STATE_DIR


def ensure_cradle_environment_state_store(base_dir: str | Path | None = None) -> Path:
    environment_dir = resolve_cradle_environment_state_dir(base_dir)
    environment_dir.mkdir(parents=True, exist_ok=True)
    (environment_dir / CRADLE_ENVIRONMENT_STATE_HISTORY_FILE).touch(exist_ok=True)
    return environment_dir


def build_cradle_environment_state_from_case(
    case_id: str,
    session_id: str | None = None,
    turn: int | None = None,
) -> dict[str, Any]:
    if case_id not in list_cradle_case_ids():
        raise ValueError(f"unknown cradle case id: {case_id}")
    sample = build_cradle_case_sample(case_id)
    cycle_summary = sample["cycle_summary"]
    mapping = _CASE_FRONT_STATE[case_id]
    front_state = {
        "kind": mapping["kind"],
        "blocked": mapping["blocked"],
        "unknown": mapping["unknown"],
        "object_id": mapping["object_id"],
        "summary": mapping["summary"],
    }
    environment_state = {
        "environment_state_id": _new_environment_state_id(case_id),
        "case_id": case_id,
        "session_id": session_id,
        "turn": turn,
        "position": {"x": 0, "y": 0},
        "facing": "north",
        "front_state": front_state,
        "visible_objects": [dict(item) for item in mapping["visible_objects"]],
        "interactive_objects": [dict(item) for item in mapping["interactive_objects"]],
        "available_operations": list(mapping["available_operations"]),
        "last_event_summary": cycle_summary["body_action_signal_type"],
        "state_summary": _state_summary(case_id, front_state, cycle_summary),
        "created_at": _now(),
        "trace_refs": _trace_refs(sample, session_id, turn),
    }
    return environment_state


def build_cradle_environment_state_from_last_session(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    session = load_current_cradle_session(base_dir)
    if session is None:
        raise LookupError("current cradle session not found")
    case_id = session.get("last_case_id")
    if not case_id:
        raise LookupError("last session case id not found")
    return build_cradle_environment_state_from_case(
        str(case_id),
        session_id=session.get("session_id"),
        turn=session.get("turn_count"),
    )


def save_cradle_environment_state(
    state: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    _validate_state(state)
    environment_dir = ensure_cradle_environment_state_store(base_dir)
    (environment_dir / LAST_CRADLE_ENVIRONMENT_STATE_FILE).write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (environment_dir / CRADLE_ENVIRONMENT_STATE_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(state, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(state)


def load_last_cradle_environment_state(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = resolve_cradle_environment_state_dir(base_dir) / LAST_CRADLE_ENVIRONMENT_STATE_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_cradle_environment_states(base_dir: str | Path | None = None) -> dict[str, Any]:
    path = ensure_cradle_environment_state_store(base_dir) / CRADLE_ENVIRONMENT_STATE_HISTORY_FILE
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "state_count": len(records),
        "environment_states": records,
    }


def _validate_state(state: dict[str, Any]) -> None:
    required = (
        "environment_state_id",
        "case_id",
        "session_id",
        "turn",
        "position",
        "facing",
        "front_state",
        "visible_objects",
        "interactive_objects",
        "available_operations",
        "last_event_summary",
        "state_summary",
        "created_at",
        "trace_refs",
    )
    missing = [field for field in required if field not in state]
    if missing:
        raise ValueError("missing environment state fields: " + ", ".join(missing))
    if state["case_id"] not in list_cradle_case_ids():
        raise ValueError(f"unknown cradle case id: {state['case_id']}")
    if not state["available_operations"]:
        raise ValueError("available_operations must be non-empty")


def _trace_refs(
    sample: dict[str, Any],
    session_id: str | None,
    turn: int | None,
) -> list[str]:
    refs = [
        sample["perception_readable_data"]["perception_id"],
        sample["memory_learning_trace"]["memory_learning_trace_id"],
        sample["body_action_signal"]["body_action_signal_id"],
    ]
    if session_id:
        refs.append(f"session:{session_id}")
    if turn is not None:
        refs.append(f"turn:{turn}")
    return refs


def _state_summary(
    case_id: str,
    front_state: dict[str, Any],
    cycle_summary: dict[str, Any],
) -> str:
    return (
        f"{case_id}: front_state={front_state['kind']}; "
        f"body_signal={cycle_summary['body_action_signal_type']}."
    )


def _new_environment_state_id(case_id: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"cradle_environment_state_{case_id}_{stamp}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
