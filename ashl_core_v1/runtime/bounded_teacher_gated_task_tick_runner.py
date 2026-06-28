"""Bounded teacher-gated task tick runner for ASHL Core v1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.memory.task_working_memory_lifecycle import create_active_task_frame
from ashl_core_v1.runtime.manual_teacher_gated_tick_builder import (
    build_manual_teacher_gated_task_tick,
)


BOUNDED_TASK_TICK_RUNNER_ENV = "ASHL_CORE_V1_BOUNDED_TASK_TICK_RUNNER_DIR"
DEFAULT_BOUNDED_TASK_TICK_RUNNER_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "bounded_task_tick_runner"
)

LAST_BOUNDED_TASK_TICK_RUN_FILE = "last_bounded_task_tick_run.json"
BOUNDED_TASK_TICK_RUN_HISTORY_FILE = "bounded_task_tick_run_history.jsonl"

MAX_ALLOWED_TICKS = 5
DEFAULT_TASK_ID = "handle_front_obstacle"
DEFAULT_GOAL = "handle front obstacle"
DETERMINISTIC_TICK_PLAN: tuple[tuple[str, str], ...] = (
    ("blocked", "observe_or_adjust"),
    ("observe_or_adjust", "check_context"),
    ("check_context", "avoid_direct_retry"),
    ("avoid_direct_retry", "wait_or_stop"),
    ("budget_stop", "budget_stop"),
)


def build_bounded_teacher_gated_task_tick_run(
    *,
    max_ticks: int = MAX_ALLOWED_TICKS,
    task_id: str = DEFAULT_TASK_ID,
    goal: str = DEFAULT_GOAL,
    close_after_tick: int | None = None,
    tick_plan: tuple[tuple[str, str], ...] | list[tuple[str, str]] | None = None,
    stop_reason_override: str | None = None,
    final_task_status_hint: str | None = None,
    case_id: str | None = None,
    expected_candidate_kinds: tuple[str, ...] | list[str] = (),
    initial_candidate_hints: tuple[str, ...] | list[str] = (),
) -> dict[str, Any]:
    if max_ticks < 1:
        raise ValueError("max_ticks must be at least 1")
    if max_ticks > MAX_ALLOWED_TICKS:
        raise ValueError("max_ticks must be <= 5")
    if close_after_tick is not None and close_after_tick < 1:
        raise ValueError("close_after_tick must be positive")

    frame = create_active_task_frame(
        current_goal=goal,
        approved_scope="bounded_teacher_gated_task_tick_runner",
        task_id=task_id,
        current_step="start",
        source_trace_refs=("bounded_task_tick_runner:start",),
    )
    current_frame: dict[str, Any] = frame.to_dict()
    if initial_candidate_hints:
        current_frame["next_candidate_hints"] = list(dict.fromkeys(initial_candidate_hints))
        current_frame["source_trace_refs"] = [
            *list(current_frame.get("source_trace_refs") or []),
            "initial_candidate_hints:bounded_runner",
        ]
    previous_tick: dict[str, Any] | None = None
    previous_update: dict[str, Any] | None = None
    tick_records: list[dict[str, Any]] = []
    updates: list[dict[str, Any]] = []

    plan = tuple(tick_plan or DETERMINISTIC_TICK_PLAN)
    if not plan:
        raise ValueError("tick_plan must not be empty")
    for tick_number, (outcome, hint) in enumerate(plan[:max_ticks], start=1):
        built = build_manual_teacher_gated_task_tick(
            task_id=task_id,
            active_task_frame=current_frame,
            previous_tick_stub_record=previous_tick,
            previous_working_memory_update=previous_update,
            tick_number=tick_number,
            teacher_gate={"teacher_gate_id": f"bounded_teacher_gate_{tick_number}"},
            fresh_context={"fresh_context_id": f"bounded_fresh_context_{tick_number}"},
            dry_run_stub={"dry_run_stub_id": f"bounded_dry_run_stub_{tick_number}"},
            audit_stub={"audit_stub_id": f"bounded_audit_stub_{tick_number}"},
            outcome_label=outcome,
            next_hint=hint,
        )
        previous_tick = built["manual_teacher_gated_tick_stub_record"]
        previous_update = built["task_working_memory_tick_update"]
        current_frame = built["updated_active_task_frame"]
        tick_records.append(previous_tick)
        updates.append(previous_update)
        if close_after_tick is not None and tick_number >= close_after_tick:
            current_frame = {
                **current_frame,
                "task_status": "completed",
                "continue_allowed": False,
                "stop_reason": "task_closed",
            }
            break

    actual_ticks = len(tick_records)
    stop_reason = (
        stop_reason_override
        or ("task_closed" if close_after_tick and actual_ticks >= close_after_tick else "budget_stop")
    )
    if stop_reason == "budget_stop":
        current_frame = {**current_frame, "continue_allowed": False, "stop_reason": "budget_stop"}

    record = {
        "run_id": _new_run_id(),
        "case_id": case_id,
        "task_id": task_id,
        "active_task_frame_id": frame.active_task_frame_id,
        "max_ticks": max_ticks,
        "actual_ticks": actual_ticks,
        "stop_reason": stop_reason,
        "final_task_status_hint": final_task_status_hint,
        "expected_candidate_kinds": list(expected_candidate_kinds),
        "initial_candidate_hints": list(initial_candidate_hints),
        "teacher_gate_preserved_for_all_ticks": all(
            tick.get("teacher_gate_preserved") is True for tick in tick_records
        ),
        "working_memory_used_for_all_ticks": _working_memory_used_for_all_ticks(
            tick_records,
            updates,
        ),
        "all_ticks_same_task": all(tick.get("task_id") == task_id for tick in tick_records),
        "all_ticks_manual_within_cli_run": all(
            tick.get("manual_trigger") is True for tick in tick_records
        ),
        "scheduler_used": False,
        "free_action_selection_used": False,
        "action_execution_used": False,
        "direct_memory_promotion_used": False,
        "created_at": _now(),
        "source_trace_refs": [
            f"active_task_frame:{frame.active_task_frame_id}",
            *[
                f"tick:{tick['manual_teacher_gated_tick_stub_record_id']}"
                for tick in tick_records
            ],
            *[
                f"task_working_memory_update:{update['task_working_memory_tick_update_id']}"
                for update in updates
            ],
        ],
    }
    summary = {
        "bounded_task_tick_run_summary_id": f"summary:{record['run_id']}",
        "run_id": record["run_id"],
        "task_id": task_id,
        "actual_ticks": actual_ticks,
        "stop_reason": stop_reason,
        "last_outcome_label": current_frame.get("last_outcome_label"),
        "last_candidate_hints": current_frame.get("next_candidate_hints", []),
    }
    return {
        "bounded_task_tick_run_created": True,
        "bounded_task_tick_run_record": record,
        "bounded_task_tick_run_summary": summary,
        "per_tick_stub_records": tick_records,
        "per_tick_working_memory_updates": updates,
        "final_active_task_frame": current_frame,
    }


def run_bounded_teacher_gated_task_tick_runner(
    *,
    max_ticks: int = MAX_ALLOWED_TICKS,
    base_dir: str | Path | None = None,
    close_after_tick: int | None = None,
    tick_plan: tuple[tuple[str, str], ...] | list[tuple[str, str]] | None = None,
    stop_reason_override: str | None = None,
    final_task_status_hint: str | None = None,
    case_id: str | None = None,
    expected_candidate_kinds: tuple[str, ...] | list[str] = (),
    initial_candidate_hints: tuple[str, ...] | list[str] = (),
) -> dict[str, Any]:
    payload = build_bounded_teacher_gated_task_tick_run(
        max_ticks=max_ticks,
        close_after_tick=close_after_tick,
        tick_plan=tick_plan,
        stop_reason_override=stop_reason_override,
        final_task_status_hint=final_task_status_hint,
        case_id=case_id,
        expected_candidate_kinds=expected_candidate_kinds,
        initial_candidate_hints=initial_candidate_hints,
    )
    return save_bounded_teacher_gated_task_tick_run(payload, base_dir)


def save_bounded_teacher_gated_task_tick_run(
    payload: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    run_dir = ensure_bounded_teacher_gated_task_tick_runner_store(base_dir)
    (run_dir / LAST_BOUNDED_TASK_TICK_RUN_FILE).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (run_dir / BOUNDED_TASK_TICK_RUN_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(payload)


def load_last_bounded_teacher_gated_task_tick_run(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = (
        resolve_bounded_teacher_gated_task_tick_runner_dir(base_dir)
        / LAST_BOUNDED_TASK_TICK_RUN_FILE
    )
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_bounded_teacher_gated_task_tick_runs(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    path = (
        resolve_bounded_teacher_gated_task_tick_runner_dir(base_dir)
        / BOUNDED_TASK_TICK_RUN_HISTORY_FILE
    )
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def resolve_bounded_teacher_gated_task_tick_runner_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(BOUNDED_TASK_TICK_RUNNER_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_BOUNDED_TASK_TICK_RUNNER_DIR


def ensure_bounded_teacher_gated_task_tick_runner_store(
    base_dir: str | Path | None = None,
) -> Path:
    run_dir = resolve_bounded_teacher_gated_task_tick_runner_dir(base_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / BOUNDED_TASK_TICK_RUN_HISTORY_FILE).touch(exist_ok=True)
    return run_dir


def _working_memory_used_for_all_ticks(
    tick_records: list[dict[str, Any]],
    updates: list[dict[str, Any]],
) -> bool:
    if len(tick_records) != len(updates):
        return False
    if not all(tick.get("task_working_memory_update_id") for tick in tick_records):
        return False
    if not all(update.get("task_working_memory_tick_update_id") for update in updates):
        return False
    for index in range(1, len(tick_records)):
        if tick_records[index].get("previous_working_memory_update_id") != updates[
            index - 1
        ].get("task_working_memory_tick_update_id"):
            return False
    return True


def _new_run_id() -> str:
    return "bounded_task_tick_run_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
