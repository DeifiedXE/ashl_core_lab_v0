"""Integrated teacher console operations for ASHL Core v1."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ashl_core_v1.lesson.correction_store import (
    list_teacher_corrections,
    list_teacher_revokes,
)
from ashl_core_v1.lesson.review_store import (
    list_pending_learning_digests,
    list_reviewed_learning_digests,
)
from ashl_core_v1.runtime.cradle_cases import list_cradle_case_ids
from ashl_core_v1.runtime.cradle_session import (
    close_cradle_session,
    load_current_cradle_session,
    run_case_in_cradle_session,
    start_cradle_session,
)
from ashl_core_v1.runtime.growth_readiness import build_controlled_growth_readiness_check
from ashl_core_v1.runtime.session_replay import (
    build_current_session_replay_summary,
    build_last_closed_session_replay_summary,
)


def build_teacher_console_status(base_dir: str | Path | None = None) -> dict[str, Any]:
    current_session = load_current_cradle_session(base_dir)
    has_active_session = current_session is not None and current_session.get("status") == "active"
    readiness = build_controlled_growth_readiness_check(base_dir)
    return {
        "has_active_session": has_active_session,
        "current_session_id": current_session["session_id"] if current_session else None,
        "turn_count": current_session["turn_count"] if current_session else 0,
        "last_case_id": current_session["last_case_id"] if current_session else None,
        "case_count_available": len(list_cradle_case_ids()),
        "session_persistence_available": _session_persistence_available(base_dir),
        "teacher_correction_available": _teacher_correction_available(base_dir),
        "readiness_summary": {
            "status": readiness["status"],
            "controlled_growth_minimum_ready": readiness["checked_capabilities"][
                "controlled_growth_minimum_ready"
            ],
            "daily_no_codex_ready": readiness["checked_capabilities"]["daily_no_codex_ready"],
        },
        "human_readable_status": _human_readable_status(current_session, has_active_session),
    }


def teacher_console_list_cases() -> dict[str, Any]:
    case_ids = list(list_cradle_case_ids())
    return {
        "case_count": len(case_ids),
        "case_ids": case_ids,
    }


def teacher_console_start_session(base_dir: str | Path | None = None) -> dict[str, Any]:
    return start_cradle_session(base_dir)


def teacher_console_run_case(
    case_id: str,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    return run_case_in_cradle_session(case_id, base_dir)


def teacher_console_run_all_cases(base_dir: str | Path | None = None) -> dict[str, Any]:
    case_results = []
    for case_id in list_cradle_case_ids():
        session = run_case_in_cradle_session(case_id, base_dir)
        case_results.append(
            {
                "case_id": case_id,
                "turn_count": session["turn_count"],
                "last_case_id": session["last_case_id"],
                "last_cycle_summary": session["last_cycle_summary"],
            }
        )
    current_session = load_current_cradle_session(base_dir)
    return {
        "case_count": len(case_results),
        "case_ids": [item["case_id"] for item in case_results],
        "case_results": case_results,
        "current_session": current_session,
    }


def teacher_console_replay_current(base_dir: str | Path | None = None) -> dict[str, Any]:
    return build_current_session_replay_summary(base_dir)


def teacher_console_replay_last_closed(base_dir: str | Path | None = None) -> dict[str, Any]:
    summary = build_last_closed_session_replay_summary(base_dir)
    if summary is None:
        return {
            "status": "not_found",
            "human_readable_replay": "not_found closed_session",
        }
    return summary


def teacher_console_readiness(base_dir: str | Path | None = None) -> dict[str, Any]:
    return build_controlled_growth_readiness_check(base_dir)


def teacher_console_close_session(base_dir: str | Path | None = None) -> dict[str, Any]:
    return close_cradle_session(base_dir)


def teacher_console_list_pending(base_dir: str | Path | None = None) -> dict[str, Any]:
    records = [digest.to_dict() for digest in list_pending_learning_digests(base_dir)]
    return {
        "pending_count": len(records),
        "pending_learning_digests": records,
    }


def teacher_console_show_reviewed(base_dir: str | Path | None = None) -> dict[str, Any]:
    records = [digest.to_dict() for digest in list_reviewed_learning_digests(base_dir)]
    return {
        "reviewed_count": len(records),
        "reviewed_learning_digests": records,
    }


def teacher_console_list_corrections(base_dir: str | Path | None = None) -> dict[str, Any]:
    records = list_teacher_corrections(base_dir)
    return {
        "correction_count": len(records),
        "teacher_corrections": records,
    }


def teacher_console_list_revokes(base_dir: str | Path | None = None) -> dict[str, Any]:
    records = list_teacher_revokes(base_dir)
    return {
        "revoke_count": len(records),
        "teacher_revokes": records,
    }


def _session_persistence_available(base_dir: str | Path | None) -> bool:
    return True


def _teacher_correction_available(base_dir: str | Path | None) -> bool:
    return True


def _human_readable_status(
    current_session: dict[str, Any] | None,
    has_active_session: bool,
) -> str:
    if current_session is None:
        return "Teacher console ready. No current cradle session."
    if has_active_session:
        return (
            "Teacher console ready. Active session "
            f"{current_session['session_id']} has {current_session['turn_count']} turn(s)."
        )
    return f"Teacher console ready. Last current session {current_session['session_id']} is closed."
