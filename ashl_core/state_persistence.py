"""State persistence snapshots for ASHL Core."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .persistence import ensure_parent_dir


STATE_SNAPSHOT_FILE = "state_snapshot.json"
SESSION_SUMMARY_FILE = "session_summary.json"
LAST_TRACE_SUMMARY_FILE = "last_trace_summary.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: str | Path, item: dict[str, Any]) -> None:
    target = Path(path)
    ensure_parent_dir(target)
    target.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_json(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {}
    return json.loads(target.read_text(encoding="utf-8"))


def build_state_snapshot(states: dict[str, float], turn: int | None = None) -> dict[str, Any]:
    return {
        "type": "state_snapshot",
        "turn": turn,
        "states": dict(states),
        "updated_at": _now_iso(),
    }


def write_state_snapshot(data_dir: str | Path, snapshot: dict[str, Any]) -> None:
    _write_json(Path(data_dir) / STATE_SNAPSHOT_FILE, snapshot)


def read_state_snapshot(data_dir: str | Path) -> dict[str, Any]:
    return _read_json(Path(data_dir) / STATE_SNAPSHOT_FILE)


def build_session_summary(
    session_id: str,
    turn_count: int,
    last_input: str | None,
    last_intent: str | None,
    last_output: str | None,
) -> dict[str, Any]:
    return {
        "type": "session_summary",
        "session_id": session_id,
        "turn_count": turn_count,
        "last_input": last_input,
        "last_intent": last_intent,
        "last_output": last_output,
        "updated_at": _now_iso(),
    }


def write_session_summary(data_dir: str | Path, summary: dict[str, Any]) -> None:
    _write_json(Path(data_dir) / SESSION_SUMMARY_FILE, summary)


def read_session_summary(data_dir: str | Path) -> dict[str, Any]:
    return _read_json(Path(data_dir) / SESSION_SUMMARY_FILE)


def build_last_trace_summary(trace: dict[str, Any]) -> dict[str, Any]:
    final_events = trace.get("concept_result", {}).get("final_events", [])
    return {
        "type": "last_trace_summary",
        "input": trace.get("input"),
        "intent": trace.get("decision", {}).get("intent"),
        "final_output": trace.get("final_output"),
        "events": [event.get("name") for event in final_events if event.get("name")],
        "has_memory_candidate": trace.get("memory_candidate") is not None,
        "has_correction_pending": trace.get("correction_pending") is not None,
        "has_rule_candidate": trace.get("rule_candidate") is not None,
        "has_trial_suggestions": bool(trace.get("trial_suggestions")),
        "has_trial_feedback": trace.get("trial_feedback") is not None,
        "updated_at": _now_iso(),
    }


def write_last_trace_summary(data_dir: str | Path, summary: dict[str, Any]) -> None:
    _write_json(Path(data_dir) / LAST_TRACE_SUMMARY_FILE, summary)


def read_last_trace_summary(data_dir: str | Path) -> dict[str, Any]:
    return _read_json(Path(data_dir) / LAST_TRACE_SUMMARY_FILE)
