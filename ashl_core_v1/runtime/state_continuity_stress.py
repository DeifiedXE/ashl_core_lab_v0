"""Repeated fixed daily cradle run continuity stress check."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.daily_run import DAILY_RUN_HISTORY_FILE, load_last_daily_run, run_cradle_daily
from ashl_core_v1.runtime.session_persistence import (
    load_last_trace_summary,
    load_session_summary,
    load_state_snapshot,
)


STATE_CONTINUITY_STRESS_ENV = "ASHL_CORE_V1_STATE_CONTINUITY_STRESS_DIR"
DEFAULT_STATE_CONTINUITY_STRESS_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "state_continuity_stress"
)

LAST_STATE_CONTINUITY_STRESS_FILE = "last_state_continuity_stress.json"
STATE_CONTINUITY_STRESS_HISTORY_FILE = "state_continuity_stress_history.jsonl"


def resolve_state_continuity_stress_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(STATE_CONTINUITY_STRESS_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_STATE_CONTINUITY_STRESS_DIR


def ensure_state_continuity_stress_store(base_dir: str | Path | None = None) -> Path:
    stress_dir = resolve_state_continuity_stress_dir(base_dir)
    stress_dir.mkdir(parents=True, exist_ok=True)
    (stress_dir / STATE_CONTINUITY_STRESS_HISTORY_FILE).touch(exist_ok=True)
    return stress_dir


def run_state_continuity_stress(
    runs: int = 3,
    case_set: str = "basic",
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    if runs <= 0:
        raise ValueError("runs must be positive")
    stress_dir = ensure_state_continuity_stress_store(base_dir)
    daily_runs = [run_cradle_daily(case_set, stress_dir) for _ in range(runs)]
    last_daily = load_last_daily_run(stress_dir)
    session_history_count = _jsonl_count(stress_dir / "session_history.jsonl")
    daily_history_count = _jsonl_count(stress_dir / DAILY_RUN_HISTORY_FILE)
    persistence_dir = stress_dir / "session_persistence"
    replay_history_present = session_history_count >= runs
    state = {
        "stress_id": _new_stress_id(),
        "runs_requested": runs,
        "runs_completed": len(daily_runs),
        "case_set": case_set,
        "daily_run_ids": [daily_run["daily_run_id"] for daily_run in daily_runs],
        "session_ids": [daily_run["session_id"] for daily_run in daily_runs],
        "turn_counts": [daily_run["turn_count"] for daily_run in daily_runs],
        "session_history_count": session_history_count,
        "daily_history_count": daily_history_count,
        "state_snapshot_present": load_state_snapshot(persistence_dir) is not None,
        "session_summary_present": load_session_summary(persistence_dir) is not None,
        "last_trace_summary_present": load_last_trace_summary(persistence_dir) is not None,
        "replay_history_present": replay_history_present,
        "created_at": _now(),
    }
    mismatches = _mismatches(state, last_daily is not None)
    state["mismatches"] = mismatches
    state["continuity_passed"] = not mismatches
    state["human_readable_summary"] = _human_readable_summary(state)
    _save_stress(state, stress_dir)
    return state


def load_last_state_continuity_stress(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = resolve_state_continuity_stress_dir(base_dir) / LAST_STATE_CONTINUITY_STRESS_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _mismatches(state: dict[str, Any], last_daily_present: bool) -> list[str]:
    checks = {
        "runs_completed_matches_requested": state["runs_completed"] == state["runs_requested"],
        "daily_run_id_count_matches_runs": len(state["daily_run_ids"]) == state["runs_requested"],
        "session_id_count_matches_runs": len(state["session_ids"]) == state["runs_requested"],
        "turn_counts_positive": all(turn > 0 for turn in state["turn_counts"]),
        "session_history_count_sufficient": state["session_history_count"] >= state["runs_requested"],
        "daily_history_count_sufficient": state["daily_history_count"] >= state["runs_requested"],
        "state_snapshot_present": state["state_snapshot_present"],
        "session_summary_present": state["session_summary_present"],
        "last_trace_summary_present": state["last_trace_summary_present"],
        "replay_history_present": state["replay_history_present"],
        "last_daily_present": last_daily_present,
    }
    return [key for key, passed in checks.items() if not passed]


def _save_stress(stress: dict[str, Any], stress_dir: Path) -> None:
    (stress_dir / LAST_STATE_CONTINUITY_STRESS_FILE).write_text(
        json.dumps(stress, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (stress_dir / STATE_CONTINUITY_STRESS_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(stress, ensure_ascii=False, sort_keys=True))
        file.write("\n")


def _jsonl_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _human_readable_summary(state: dict[str, Any]) -> str:
    if state["continuity_passed"]:
        return f"State continuity stress passed for {state['runs_completed']} fixed daily run(s)."
    return "State continuity stress failed: " + ", ".join(state["mismatches"])


def _new_stress_id() -> str:
    return "state_continuity_stress_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
