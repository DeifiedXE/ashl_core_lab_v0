"""Replay summaries for ASHL Core v1 cradle sessions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.cradle_session import (
    list_cradle_session_history,
    load_current_cradle_session,
)


def build_current_session_replay_summary(base_dir: str | Path | None = None) -> dict[str, Any]:
    session = load_current_cradle_session(base_dir)
    if session is None:
        return {
            "status": "not_found",
            "session_id": None,
            "turn_count": 0,
            "case_count": 0,
            "case_sequence": [],
            "approved_count": 0,
            "blocked_by_review_count": 0,
            "routed_count": 0,
            "influence_visible_count": 0,
            "human_readable_replay": "not_found current_session",
        }
    return _build_single_session_summary(session)


def build_session_history_replay_summary(base_dir: str | Path | None = None) -> dict[str, Any]:
    sessions = [_build_single_session_summary(session) for session in list_cradle_session_history(base_dir)]
    total_turn_count = sum(int(session["turn_count"]) for session in sessions)
    total_case_count = sum(int(session["case_count"]) for session in sessions)
    latest_session_id = sessions[-1]["session_id"] if sessions else None
    return {
        "session_count": len(sessions),
        "sessions": sessions,
        "latest_session_id": latest_session_id,
        "total_turn_count": total_turn_count,
        "total_case_count": total_case_count,
        "human_readable_replay": _history_replay_text(sessions),
    }


def build_last_closed_session_replay_summary(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    history = list_cradle_session_history(base_dir)
    if not history:
        return None
    return _build_single_session_summary(history[-1])


def _build_single_session_summary(session: dict[str, Any]) -> dict[str, Any]:
    case_history = list(session.get("case_history", []))
    case_sequence = [entry["case_id"] for entry in case_history]
    approved_count = sum(1 for entry in case_history if _entry_value(entry, "review_status") == "approved")
    routed_count = sum(1 for entry in case_history if _entry_value(entry, "routing_status") == "routed")
    influence_visible_count = sum(1 for entry in case_history if bool(_entry_value(entry, "influence_visible")))
    case_count = len(case_history)
    return {
        "session_id": session["session_id"],
        "status": session["status"],
        "turn_count": session["turn_count"],
        "case_count": case_count,
        "case_sequence": case_sequence,
        "approved_count": approved_count,
        "blocked_by_review_count": case_count - approved_count,
        "routed_count": routed_count,
        "influence_visible_count": influence_visible_count,
        "human_readable_replay": _session_replay_text(case_history),
    }


def _entry_value(entry: dict[str, Any], key: str) -> Any:
    if key in entry:
        return entry[key]
    return entry.get("cycle_summary", {}).get(key)


def _session_replay_text(case_history: list[dict[str, Any]]) -> str:
    if not case_history:
        return "This session has no cradle cases yet."
    lines = [f"This session ran {len(case_history)} cradle cases:"]
    for index, entry in enumerate(case_history, start=1):
        case_id = entry["case_id"]
        review_status = _entry_value(entry, "review_status")
        routing_status = _entry_value(entry, "routing_status")
        influence = "visible influence" if _entry_value(entry, "influence_visible") else "no visible influence"
        lines.append(f"{index}. {case_id}: review={review_status}, routing={routing_status}, {influence}.")
    visible_count = sum(1 for entry in case_history if _entry_value(entry, "influence_visible"))
    lines.append(f"Visible influence appeared in {visible_count} case.")
    return "\n".join(lines)


def _history_replay_text(sessions: list[dict[str, Any]]) -> str:
    if not sessions:
        return "No closed cradle sessions found."
    total_cases = sum(session["case_count"] for session in sessions)
    return (
        f"Session history contains {len(sessions)} closed session(s) "
        f"with {total_cases} cradle case(s)."
    )
