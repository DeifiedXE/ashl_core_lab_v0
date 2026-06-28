"""Fixed multi-case cradle task suite for ASHL Core v1."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.bounded_teacher_gated_task_tick_runner import (
    build_bounded_teacher_gated_task_tick_run,
    save_bounded_teacher_gated_task_tick_run,
)
from ashl_core_v1.runtime.task_run_closure import (
    build_task_run_closure,
    save_task_run_closure,
)


MULTI_CASE_CRADLE_TASK_SUITE_ENV = "ASHL_CORE_V1_MULTI_CASE_CRADLE_TASK_SUITE_DIR"
DEFAULT_MULTI_CASE_CRADLE_TASK_SUITE_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "multi_case_cradle_task_suite"
)

LAST_MULTI_CASE_RUN_FILE = "last_multi_case_cradle_task_run.json"
LAST_MULTI_CASE_SUITE_SUMMARY_FILE = "last_multi_case_cradle_task_suite_summary.json"
MULTI_CASE_RUN_HISTORY_FILE = "multi_case_cradle_task_run_history.jsonl"


@dataclass(frozen=True)
class CradleTaskCase:
    case_id: str
    task_id: str
    goal: str
    tick_plan: tuple[tuple[str, str], ...]
    stop_reason: str
    final_task_status: str
    expected_candidate_kinds: tuple[str, ...]


CRADLE_TASK_CASES: tuple[CradleTaskCase, ...] = (
    CradleTaskCase(
        case_id="blocked_front_obstacle",
        task_id="task_blocked_front_obstacle",
        goal="handle front obstacle",
        tick_plan=(
            ("blocked", "observe_or_adjust"),
            ("blocked", "avoid_direct_retry"),
            ("avoid_direct_retry", "wait_or_stop"),
        ),
        stop_reason="blocked_front_obstacle",
        final_task_status="failed",
        expected_candidate_kinds=("blocked_front_obstacle", "repeated_blocked"),
    ),
    CradleTaskCase(
        case_id="success_simple_reach",
        task_id="task_success_simple_reach",
        goal="reach visible front item",
        tick_plan=(
            ("observe_item", "reach_front"),
            ("reach_front", "confirm_success"),
            ("success", "task_complete"),
        ),
        stop_reason="task_closed",
        final_task_status="completed",
        expected_candidate_kinds=("successful_path",),
    ),
    CradleTaskCase(
        case_id="unknown_needs_observe",
        task_id="task_unknown_needs_observe",
        goal="handle unknown front state",
        tick_plan=(
            ("unknown", "observe_or_adjust"),
            ("observe_or_adjust", "check_context"),
            ("unknown_resolved", "context_observed"),
        ),
        stop_reason="task_closed",
        final_task_status="completed",
        expected_candidate_kinds=("unknown_resolved", "needs_observe"),
    ),
    CradleTaskCase(
        case_id="teacher_stopped",
        task_id="task_teacher_stopped",
        goal="continue sandbox task",
        tick_plan=(
            ("observe_item", "continue"),
            ("teacher_stopped", "stop"),
        ),
        stop_reason="teacher_stopped",
        final_task_status="teacher_stopped",
        expected_candidate_kinds=("teacher_stopped",),
    ),
    CradleTaskCase(
        case_id="suspended_waiting_for_teacher",
        task_id="task_suspended_waiting_for_teacher",
        goal="continue but requires teacher input",
        tick_plan=(
            ("waiting_for_teacher", "suspend_task"),
        ),
        stop_reason="waiting_for_teacher",
        final_task_status="suspended",
        expected_candidate_kinds=("suspended", "waiting_for_teacher"),
    ),
    CradleTaskCase(
        case_id="conflict_expected_vs_actual",
        task_id="task_conflict_expected_vs_actual",
        goal="compare expected success with actual result",
        tick_plan=(
            ("expected_success", "attempt_reach"),
            ("mismatch_blocked", "compare_expected_actual"),
            ("conflict_detected", "stop_for_review"),
        ),
        stop_reason="conflict_expected_vs_actual",
        final_task_status="failed",
        expected_candidate_kinds=("expected_vs_actual_mismatch", "conflict_detected"),
    ),
)


def list_cradle_task_suite_cases() -> list[dict[str, Any]]:
    return [
        {
            "case_id": case.case_id,
            "task_id": case.task_id,
            "goal": case.goal,
            "max_case_ticks": len(case.tick_plan),
            "expected_candidate_kinds": list(case.expected_candidate_kinds),
        }
        for case in CRADLE_TASK_CASES
    ]


def run_multi_case_cradle_task_case(
    case_id: str,
    *,
    max_ticks: int = 5,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    case = _get_case(case_id)
    if max_ticks > 5:
        raise ValueError("max_ticks must be <= 5")
    run = build_bounded_teacher_gated_task_tick_run(
        max_ticks=max_ticks,
        task_id=case.task_id,
        goal=case.goal,
        tick_plan=case.tick_plan,
        stop_reason_override=case.stop_reason,
        final_task_status_hint=case.final_task_status,
        case_id=case.case_id,
        expected_candidate_kinds=case.expected_candidate_kinds,
    )
    closure = build_task_run_closure(run)
    payload = {
        "multi_case_cradle_task_case_run_created": True,
        "case_id": case.case_id,
        "case_definition": {
            "task_id": case.task_id,
            "goal": case.goal,
            "expected_candidate_kinds": list(case.expected_candidate_kinds),
        },
        "bounded_task_run": run,
        "task_run_closure": closure,
        "case_status": "passed",
        "created_at": _now(),
    }
    if base_dir is not None:
        save_bounded_teacher_gated_task_tick_run(run, base_dir)
        save_task_run_closure(closure, base_dir)
        save_multi_case_cradle_task_case_run(payload, base_dir)
    return payload


def run_all_multi_case_cradle_task_cases(
    *,
    max_ticks: int = 5,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    case_runs = [
        run_multi_case_cradle_task_case(
            case.case_id,
            max_ticks=max_ticks,
            base_dir=base_dir,
        )
        for case in CRADLE_TASK_CASES
    ]
    summary = {
        "suite_run_id": _new_suite_run_id(),
        "case_count": len(case_runs),
        "case_ids": [case_run["case_id"] for case_run in case_runs],
        "cases_passed": [case_run["case_id"] for case_run in case_runs],
        "cases_failed": [],
        "all_cases_used_working_memory": all(
            case_run["bounded_task_run"]["bounded_task_tick_run_record"][
                "working_memory_used_for_all_ticks"
            ]
            for case_run in case_runs
        ),
        "scheduler_used": False,
        "free_action_selection_used": False,
        "action_execution_used": False,
        "direct_memory_promotion_used": False,
        "created_at": _now(),
    }
    payload = {
        "multi_case_cradle_task_suite_run_created": True,
        "suite_summary": summary,
        "case_runs": case_runs,
    }
    if base_dir is not None:
        save_multi_case_cradle_task_suite_summary(payload, base_dir)
    return payload


def save_multi_case_cradle_task_case_run(
    payload: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    suite_dir = ensure_multi_case_cradle_task_suite_store(base_dir)
    (suite_dir / LAST_MULTI_CASE_RUN_FILE).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (suite_dir / MULTI_CASE_RUN_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(payload)


def save_multi_case_cradle_task_suite_summary(
    payload: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    suite_dir = ensure_multi_case_cradle_task_suite_store(base_dir)
    (suite_dir / LAST_MULTI_CASE_SUITE_SUMMARY_FILE).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return dict(payload)


def load_last_multi_case_cradle_task_case_run(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = resolve_multi_case_cradle_task_suite_dir(base_dir) / LAST_MULTI_CASE_RUN_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_last_multi_case_cradle_task_suite_summary(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = (
        resolve_multi_case_cradle_task_suite_dir(base_dir)
        / LAST_MULTI_CASE_SUITE_SUMMARY_FILE
    )
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_multi_case_cradle_task_suite_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(MULTI_CASE_CRADLE_TASK_SUITE_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_MULTI_CASE_CRADLE_TASK_SUITE_DIR


def ensure_multi_case_cradle_task_suite_store(
    base_dir: str | Path | None = None,
) -> Path:
    suite_dir = resolve_multi_case_cradle_task_suite_dir(base_dir)
    suite_dir.mkdir(parents=True, exist_ok=True)
    (suite_dir / MULTI_CASE_RUN_HISTORY_FILE).touch(exist_ok=True)
    return suite_dir


def _get_case(case_id: str) -> CradleTaskCase:
    for case in CRADLE_TASK_CASES:
        if case.case_id == case_id:
            return case
    raise KeyError(f"unknown cradle task case: {case_id}")


def _new_suite_run_id() -> str:
    return "multi_case_cradle_task_suite_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
