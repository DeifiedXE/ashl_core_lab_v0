"""Explicit cradle session lifecycle helpers for ASHL Core v1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.cradle_cases import build_cradle_case_sample, list_cradle_case_ids
from ashl_core_v1.runtime.cradle_summary import summarize_cradle_case
from ashl_core_v1.runtime.session_persistence import (
    build_last_trace_summary,
    build_session_summary,
    build_state_snapshot,
    save_last_trace_summary,
    save_session_summary,
    save_state_snapshot,
)


CRADLE_SESSION_ENV = "ASHL_CORE_V1_CRADLE_SESSION_DIR"
DEFAULT_CRADLE_SESSION_DIR = Path(__file__).resolve().parents[1] / "data" / "cradle_session"

CURRENT_SESSION_FILE = "current_session.json"
SESSION_HISTORY_FILE = "session_history.jsonl"


def resolve_cradle_session_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(CRADLE_SESSION_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_CRADLE_SESSION_DIR


def ensure_cradle_session_store(base_dir: str | Path | None = None) -> Path:
    session_dir = resolve_cradle_session_dir(base_dir)
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / SESSION_HISTORY_FILE).touch(exist_ok=True)
    return session_dir


def start_cradle_session(base_dir: str | Path | None = None) -> dict[str, Any]:
    existing = load_current_cradle_session(base_dir)
    if existing is not None and existing.get("status") == "active":
        raise RuntimeError(f"active cradle session already exists: {existing['session_id']}")

    session = {
        "session_id": _new_session_id(),
        "status": "active",
        "turn_count": 0,
        "started_at": _now(),
        "closed_at": None,
        "case_history": [],
        "last_case_id": None,
        "last_cycle_summary": None,
        "last_trace_summary_ref": None,
    }
    _write_current_session(session, base_dir)
    return dict(session)


def run_case_in_cradle_session(
    case_id: str,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    session = load_current_cradle_session(base_dir)
    if session is None or session.get("status") != "active":
        raise RuntimeError("active cradle session not found")
    if case_id not in list_cradle_case_ids():
        raise ValueError(f"unknown cradle case id: {case_id}")

    sample = build_cradle_case_sample(case_id)
    cycle_summary = dict(sample["cycle_summary"])
    human_summary = summarize_cradle_case(case_id)["human_readable_summary"]
    turn = int(session["turn_count"]) + 1
    memory_trace = sample["memory_learning_trace"]
    last_trace_summary_ref = memory_trace["last_trace_summary_ref"]

    history_entry = {
        "turn": turn,
        "case_id": case_id,
        "case_summary": human_summary,
        "cycle_summary": cycle_summary,
        "review_status": cycle_summary["review_status"],
        "routing_status": cycle_summary["routing_status"],
        "influence_visible": cycle_summary["influence_visible"],
        "last_trace_summary_ref": last_trace_summary_ref,
        "ran_at": _now(),
    }

    session["turn_count"] = turn
    session["case_history"] = [*session["case_history"], history_entry]
    session["last_case_id"] = case_id
    session["last_cycle_summary"] = cycle_summary
    session["last_trace_summary_ref"] = last_trace_summary_ref
    _write_current_session(session, base_dir)
    _update_session_persistence(session, sample, human_summary, base_dir)
    return dict(session)


def close_cradle_session(base_dir: str | Path | None = None) -> dict[str, Any]:
    session = load_current_cradle_session(base_dir)
    if session is None or session.get("status") != "active":
        raise RuntimeError("active cradle session not found")

    session["status"] = "closed"
    session["closed_at"] = _now()
    _write_current_session(session, base_dir)
    _append_session_history(session, base_dir)
    return dict(session)


def load_current_cradle_session(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = resolve_cradle_session_dir(base_dir) / CURRENT_SESSION_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_cradle_session_history(base_dir: str | Path | None = None) -> list[dict[str, Any]]:
    path = ensure_cradle_session_store(base_dir) / SESSION_HISTORY_FILE
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def _update_session_persistence(
    session: dict[str, Any],
    sample: dict[str, Any],
    human_summary: str,
    base_dir: str | Path | None,
) -> None:
    persistence_dir = None
    if base_dir is not None:
        persistence_dir = resolve_cradle_session_dir(base_dir) / "session_persistence"

    state_snapshot = build_state_snapshot(
        session_id=session["session_id"],
        turn=session["turn_count"],
        state_values={
            "status": session["status"],
            "last_case_id": session["last_case_id"],
            "case_history_count": len(session["case_history"]),
        },
    )
    session_summary = build_session_summary(
        session_id=session["session_id"],
        turn_count=session["turn_count"],
        last_case_id=session["last_case_id"],
        last_summary=human_summary,
    )
    memory_trace = sample["memory_learning_trace"]
    last_trace_summary = build_last_trace_summary(
        trace_id=memory_trace["memory_learning_trace_id"],
        case_id=session["last_case_id"],
        summary=human_summary,
        source_refs=(
            sample["perception_readable_data"]["perception_id"],
            sample["learning_review_record"]["review_record_id"],
            memory_trace["memory_learning_trace_id"],
        ),
    )
    save_state_snapshot(state_snapshot, persistence_dir)
    save_session_summary(session_summary, persistence_dir)
    save_last_trace_summary(last_trace_summary, persistence_dir)


def _write_current_session(session: dict[str, Any], base_dir: str | Path | None) -> None:
    path = ensure_cradle_session_store(base_dir) / CURRENT_SESSION_FILE
    path.write_text(
        json.dumps(session, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _append_session_history(session: dict[str, Any], base_dir: str | Path | None) -> None:
    path = ensure_cradle_session_store(base_dir) / SESSION_HISTORY_FILE
    with path.open("a", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(session, ensure_ascii=False, sort_keys=True))
        file.write("\n")


def _new_session_id() -> str:
    return "cradle_session_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
