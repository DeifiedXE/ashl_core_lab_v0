"""Manual fixed-cradle daily run script for ASHL Core v1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.cradle_cases import list_cradle_case_ids
DAILY_RUN_ENV = "ASHL_CORE_V1_DAILY_RUN_DIR"
DEFAULT_DAILY_RUN_DIR = Path(__file__).resolve().parents[1] / "data" / "daily_run"

LAST_DAILY_RUN_FILE = "last_daily_run.json"
DAILY_RUN_HISTORY_FILE = "daily_run_history.jsonl"
DAILY_REPORTS_DIR = "daily_reports"

BASIC_CASE_SET = (
    "blocked_front_obstacle",
    "success_front_step",
    "unknown_feedback",
    "teacher_rejected",
)
ALL_CASE_SET = tuple(list_cradle_case_ids())
CASE_SETS = {
    "basic": BASIC_CASE_SET,
    "all": ALL_CASE_SET,
}


def resolve_daily_run_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(DAILY_RUN_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_DAILY_RUN_DIR


def ensure_daily_run_store(base_dir: str | Path | None = None) -> Path:
    daily_dir = resolve_daily_run_dir(base_dir)
    daily_dir.mkdir(parents=True, exist_ok=True)
    (daily_dir / DAILY_RUN_HISTORY_FILE).touch(exist_ok=True)
    (daily_dir / DAILY_REPORTS_DIR).mkdir(parents=True, exist_ok=True)
    return daily_dir


def run_cradle_daily(
    case_set: str = "basic",
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.teacher_console.console import (
        teacher_console_close_session,
        teacher_console_readiness,
        teacher_console_replay_current,
        teacher_console_run_case,
        teacher_console_start_session,
    )

    if case_set not in CASE_SETS:
        raise ValueError(f"unknown case_set: {case_set}")

    daily_dir = ensure_daily_run_store(base_dir)
    started_at = _now()
    session = teacher_console_start_session(daily_dir)
    case_ids = list(CASE_SETS[case_set])
    for case_id in case_ids:
        session = teacher_console_run_case(case_id, daily_dir)

    replay_summary = teacher_console_replay_current(daily_dir)
    readiness_summary = teacher_console_readiness(daily_dir)
    closed_session = teacher_console_close_session(daily_dir)

    daily_run = {
        "daily_run_id": _new_daily_run_id(),
        "session_id": session["session_id"],
        "case_set": case_set,
        "case_ids": case_ids,
        "case_count": len(case_ids),
        "started_at": started_at,
        "closed_at": closed_session["closed_at"],
        "turn_count": closed_session["turn_count"],
        "replay_summary": replay_summary,
        "readiness_summary": readiness_summary,
        "report_path": None,
        "human_readable_daily_summary": _human_readable_daily_summary(replay_summary),
    }
    report = write_daily_report(daily_run, daily_dir)
    daily_run["report_path"] = report["path"]
    _save_daily_run(daily_run, daily_dir)
    return daily_run


def load_last_daily_run(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = resolve_daily_run_dir(base_dir) / LAST_DAILY_RUN_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_daily_report(
    daily_run: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    daily_dir = ensure_daily_run_store(base_dir)
    report_path = daily_dir / DAILY_REPORTS_DIR / f"{daily_run['daily_run_id']}.md"
    report_path.write_text(_render_daily_report(daily_run), encoding="utf-8", newline="\n")
    return {
        "daily_run_id": daily_run["daily_run_id"],
        "path": str(report_path),
    }


def _save_daily_run(daily_run: dict[str, Any], daily_dir: Path) -> None:
    (daily_dir / LAST_DAILY_RUN_FILE).write_text(
        json.dumps(daily_run, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (daily_dir / DAILY_RUN_HISTORY_FILE).open("a", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(daily_run, ensure_ascii=False, sort_keys=True))
        file.write("\n")


def _render_daily_report(daily_run: dict[str, Any]) -> str:
    lines = [
        "# ASHL Core v1 Daily Cradle Run Report",
        "",
        f"daily_run_id: {daily_run['daily_run_id']}",
        f"session_id: {daily_run['session_id']}",
        f"case_set: {daily_run['case_set']}",
        f"case_count: {daily_run['case_count']}",
        f"turn_count: {daily_run['turn_count']}",
        "",
        "## Case IDs",
        "",
    ]
    lines.extend(f"- {case_id}" for case_id in daily_run["case_ids"])
    lines.extend(
        [
            "",
            "## Replay Summary",
            "",
            daily_run["replay_summary"]["human_readable_replay"],
            "",
            "## Readiness Summary",
            "",
            f"status: {daily_run['readiness_summary']['status']}",
            "",
            "## Daily Summary",
            "",
            daily_run["human_readable_daily_summary"],
            "",
        ]
    )
    return "\n".join(lines)


def _human_readable_daily_summary(replay_summary: dict[str, Any]) -> str:
    return (
        "Daily cradle run completed. "
        f"Ran {replay_summary['case_count']} fixed cradle cases. "
        f"Visible influence appeared in {replay_summary['influence_visible_count']} cases. "
        "Session summary and replay summary were saved."
    )


def _new_daily_run_id() -> str:
    return "daily_run_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
