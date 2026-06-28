"""Three-tick task pattern audit for ASHL Core v1."""

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


THREE_TICK_PATTERN_AUDIT_ENV = "ASHL_CORE_V1_THREE_TICK_PATTERN_AUDIT_DIR"
DEFAULT_THREE_TICK_PATTERN_AUDIT_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "three_tick_task_pattern_audit"
)

LAST_THREE_TICK_PATTERN_AUDIT_FILE = "last_three_tick_task_pattern_audit.json"
THREE_TICK_PATTERN_AUDIT_HISTORY_FILE = "three_tick_task_pattern_audit_history.jsonl"


def build_three_tick_task_pattern_audit(
    tick_records: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
    working_memory_updates: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
) -> dict[str, Any]:
    ticks = list(tick_records or [])
    updates = list(working_memory_updates or [])
    status = _pattern_status(ticks, updates)
    task_ids = {tick.get("task_id") for tick in ticks if tick.get("task_id")}
    frame_ids = {
        tick.get("active_task_frame_id") for tick in ticks if tick.get("active_task_frame_id")
    }
    record = {
        "three_tick_task_pattern_audit_id": _new_audit_id(),
        "tick_count": len(ticks),
        "task_id": next(iter(task_ids), None) if len(task_ids) == 1 else None,
        "active_task_frame_id": next(iter(frame_ids), None) if len(frame_ids) == 1 else None,
        "same_task_id_preserved": len(task_ids) == 1 and len(ticks) == 3,
        "same_active_task_frame_lineage_preserved": len(frame_ids) == 1 and len(ticks) == 3,
        "tick2_reads_tick1_working_memory_update": _reads_previous_update(ticks, updates, 1, 2),
        "tick3_reads_tick2_working_memory_update": _reads_previous_update(ticks, updates, 2, 3),
        "each_tick_links_working_memory_update": len(updates) == len(ticks)
        and all(tick.get("task_working_memory_update_id") for tick in ticks),
        "teacher_gate_preserved_for_all_ticks": all(
            tick.get("teacher_gate_preserved") is True for tick in ticks
        ),
        "manual_trigger_preserved_for_all_ticks": all(
            tick.get("manual_trigger") is True for tick in ticks
        ),
        "each_tick_stops_after_creation": all(tick.get("tick_stopped") is True for tick in ticks),
        "fourth_tick_created": any(tick.get("tick_number") == 4 for tick in ticks),
        "automatic_loop_detected": any(tick.get("automatic_loop_created") is True for tick in ticks),
        "scheduler_detected": any(tick.get("scheduler_used") is True for tick in ticks),
        "action_execution_detected": any(tick.get("action_execution_used") is True for tick in ticks),
        "pattern_status": status,
        "pattern_notes": (status,) if status != "passed" else ("passed", "three_tick_task_pattern_preserved"),
        "created_at": _now(),
        "source_trace_refs": _trace_refs(ticks, updates),
    }
    return record


def build_three_tick_task_pattern_audit_demo() -> dict[str, Any]:
    fixture = build_three_tick_task_pattern_fixture()
    audit = build_three_tick_task_pattern_audit(
        fixture["tick_records"],
        fixture["working_memory_updates"],
    )
    return {
        "three_tick_task_pattern_audit_created": True,
        "three_tick_task_pattern_audit": audit,
        **fixture,
    }


def build_three_tick_task_pattern_fixture() -> dict[str, Any]:
    task_id = "handle_front_obstacle"
    frame = create_active_task_frame(
        current_goal="handle front obstacle",
        approved_scope="manual_teacher_gated_builder_demo",
        task_id=task_id,
        current_step="start",
        source_trace_refs=("demo:three_tick_task_pattern",),
    )
    tick_records: list[dict[str, Any]] = []
    updates: list[dict[str, Any]] = []
    current_frame: dict[str, Any] = frame.to_dict()
    previous_tick = None
    previous_update = None
    outcomes = (
        ("blocked", "observe_or_adjust"),
        ("observe_or_adjust", "check_context"),
        ("check_context", "avoid_direct_retry"),
    )
    for tick_number, (outcome, hint) in enumerate(outcomes, start=1):
        built = build_manual_teacher_gated_task_tick(
            task_id=task_id,
            active_task_frame=current_frame,
            previous_tick_stub_record=previous_tick,
            previous_working_memory_update=previous_update,
            tick_number=tick_number,
            teacher_gate={"teacher_gate_id": f"teacher_gate_{tick_number}"},
            fresh_context={"fresh_context_id": f"fresh_context_{tick_number}"},
            dry_run_stub={"dry_run_stub_id": f"dry_run_stub_{tick_number}"},
            audit_stub={"audit_stub_id": f"audit_stub_{tick_number}"},
            outcome_label=outcome,
            next_hint=hint,
        )
        previous_tick = built["manual_teacher_gated_tick_stub_record"]
        previous_update = built["task_working_memory_tick_update"]
        current_frame = built["updated_active_task_frame"]
        tick_records.append(previous_tick)
        updates.append(previous_update)
    return {
        "task_id": task_id,
        "active_task_frame_id": frame.active_task_frame_id,
        "tick_records": tick_records,
        "working_memory_updates": updates,
        "final_active_task_frame": current_frame,
    }


def build_manual_teacher_gated_tick_builder_demo() -> dict[str, Any]:
    frame = create_active_task_frame(
        current_goal="builder demo",
        approved_scope="manual_single_tick_builder_demo",
        task_id="builder_demo_task",
        current_step="start",
    )
    built = build_manual_teacher_gated_task_tick(
        task_id=frame.task_id,
        active_task_frame=frame,
        previous_tick_stub_record=None,
        previous_working_memory_update=None,
        tick_number=1,
        teacher_gate={"teacher_gate_id": "teacher_gate_builder_demo"},
        fresh_context={"fresh_context_id": "fresh_context_builder_demo"},
        dry_run_stub={"dry_run_stub_id": "dry_run_stub_builder_demo"},
        audit_stub={"audit_stub_id": "audit_stub_builder_demo"},
        outcome_label="blocked",
        next_hint="observe_or_adjust",
    )
    return {
        "manual_teacher_gated_tick_builder_demo_created": True,
        **built,
    }


def run_three_tick_task_pattern_audit(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    return save_three_tick_task_pattern_audit(build_three_tick_task_pattern_audit_demo(), base_dir)


def run_manual_teacher_gated_tick_builder_demo(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    demo = build_manual_teacher_gated_tick_builder_demo()
    audit_dir = ensure_three_tick_task_pattern_audit_store(base_dir)
    (audit_dir / "last_manual_teacher_gated_tick_builder_demo.json").write_text(
        json.dumps(demo, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return demo


def save_three_tick_task_pattern_audit(
    payload: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    audit_dir = ensure_three_tick_task_pattern_audit_store(base_dir)
    (audit_dir / LAST_THREE_TICK_PATTERN_AUDIT_FILE).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (audit_dir / THREE_TICK_PATTERN_AUDIT_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(payload)


def load_last_three_tick_task_pattern_audit(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = resolve_three_tick_task_pattern_audit_dir(base_dir) / LAST_THREE_TICK_PATTERN_AUDIT_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_three_tick_task_pattern_audit_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(THREE_TICK_PATTERN_AUDIT_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_THREE_TICK_PATTERN_AUDIT_DIR


def ensure_three_tick_task_pattern_audit_store(base_dir: str | Path | None = None) -> Path:
    audit_dir = resolve_three_tick_task_pattern_audit_dir(base_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)
    (audit_dir / THREE_TICK_PATTERN_AUDIT_HISTORY_FILE).touch(exist_ok=True)
    return audit_dir


def _pattern_status(ticks: list[dict[str, Any]], updates: list[dict[str, Any]]) -> str:
    if len(ticks) < 1:
        return "blocked_missing_tick1"
    if len(ticks) < 2:
        return "blocked_missing_tick2"
    if len(ticks) < 3:
        return "blocked_missing_tick3"
    if len(ticks) != 3:
        return "blocked_fourth_tick_detected"
    if len({tick.get("task_id") for tick in ticks}) != 1:
        return "blocked_task_id_mismatch"
    if not _reads_previous_update(ticks, updates, 2, 3):
        return "blocked_tick3_not_reading_tick2_working_memory"
    if not all(tick.get("teacher_gate_preserved") is True for tick in ticks):
        return "blocked_teacher_gate_missing"
    if any(tick.get("automatic_loop_created") is True for tick in ticks):
        return "blocked_automatic_loop_detected"
    if any(tick.get("tick_number") == 4 for tick in ticks):
        return "blocked_fourth_tick_detected"
    return "passed"


def _reads_previous_update(
    ticks: list[dict[str, Any]],
    updates: list[dict[str, Any]],
    previous_tick_number: int,
    tick_number: int,
) -> bool:
    if len(ticks) < tick_number or len(updates) < previous_tick_number:
        return False
    previous_update_id = updates[previous_tick_number - 1].get(
        "task_working_memory_tick_update_id"
    )
    return ticks[tick_number - 1].get("previous_working_memory_update_id") == previous_update_id


def _trace_refs(ticks: list[dict[str, Any]], updates: list[dict[str, Any]]) -> list[str]:
    refs: list[str] = []
    for record in [*ticks, *updates]:
        refs.extend(str(ref) for ref in record.get("trace_refs") or [])
        refs.extend(str(ref) for ref in record.get("source_trace_refs") or [])
    return list(dict.fromkeys(refs))


def _new_audit_id() -> str:
    return "three_tick_task_pattern_audit_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
