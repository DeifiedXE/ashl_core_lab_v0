"""Minimal session persistence helpers for ASHL Core v1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SESSION_PERSISTENCE_ENV = "ASHL_CORE_V1_SESSION_PERSISTENCE_DIR"
DEFAULT_SESSION_PERSISTENCE_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "session_persistence"
)

STATE_SNAPSHOT_FILE = "state_snapshot.json"
SESSION_SUMMARY_FILE = "session_summary.json"
LAST_TRACE_SUMMARY_FILE = "last_trace_summary.json"


def build_state_snapshot(
    session_id: str,
    turn: int,
    state_values: dict[str, object],
) -> dict[str, Any]:
    if not session_id:
        raise ValueError("session_id is required")
    if turn < 0:
        raise ValueError("turn must be non-negative")
    return {
        "session_id": session_id,
        "turn": turn,
        "state_values": dict(state_values),
        "updated_at": _now(),
    }


def build_session_summary(
    session_id: str,
    turn_count: int,
    last_case_id: str | None,
    last_summary: str,
) -> dict[str, Any]:
    if not session_id:
        raise ValueError("session_id is required")
    if turn_count < 0:
        raise ValueError("turn_count must be non-negative")
    return {
        "session_id": session_id,
        "turn_count": turn_count,
        "last_case_id": last_case_id,
        "last_summary": last_summary,
        "updated_at": _now(),
    }


def build_last_trace_summary(
    trace_id: str,
    case_id: str,
    summary: str,
    source_refs: tuple[str, ...] = (),
) -> dict[str, Any]:
    if not trace_id:
        raise ValueError("trace_id is required")
    if not case_id:
        raise ValueError("case_id is required")
    refs = tuple(source_refs)
    if not all(isinstance(ref, str) for ref in refs):
        raise TypeError("source_refs must contain only strings")
    return {
        "trace_id": trace_id,
        "case_id": case_id,
        "summary": summary,
        "source_refs": list(refs),
        "updated_at": _now(),
    }


def save_state_snapshot(snapshot: dict[str, Any], base_dir: str | Path | None = None) -> dict[str, Any]:
    return _save_json(STATE_SNAPSHOT_FILE, snapshot, base_dir)


def load_state_snapshot(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    return _load_json(STATE_SNAPSHOT_FILE, base_dir)


def save_session_summary(summary: dict[str, Any], base_dir: str | Path | None = None) -> dict[str, Any]:
    return _save_json(SESSION_SUMMARY_FILE, summary, base_dir)


def load_session_summary(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    return _load_json(SESSION_SUMMARY_FILE, base_dir)


def save_last_trace_summary(summary: dict[str, Any], base_dir: str | Path | None = None) -> dict[str, Any]:
    return _save_json(LAST_TRACE_SUMMARY_FILE, summary, base_dir)


def load_last_trace_summary(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    return _load_json(LAST_TRACE_SUMMARY_FILE, base_dir)


def resolve_session_persistence_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(SESSION_PERSISTENCE_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_SESSION_PERSISTENCE_DIR


def _save_json(file_name: str, payload: dict[str, Any], base_dir: str | Path | None) -> dict[str, Any]:
    path = resolve_session_persistence_dir(base_dir) / file_name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return dict(payload)


def _load_json(file_name: str, base_dir: str | Path | None) -> dict[str, Any] | None:
    path = resolve_session_persistence_dir(base_dir) / file_name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
