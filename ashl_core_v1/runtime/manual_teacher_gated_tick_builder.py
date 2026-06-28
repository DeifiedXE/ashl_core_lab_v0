"""Reusable single-tick teacher-gated task stub builder for ASHL Core v1."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.memory.task_working_memory_lifecycle import (
    ActiveTaskFrame,
    TaskWorkingMemoryTickUpdate,
    apply_task_working_memory_tick_update,
)


def build_manual_teacher_gated_task_tick(
    *,
    task_id: str,
    active_task_frame: ActiveTaskFrame | dict[str, Any],
    previous_tick_stub_record: dict[str, Any] | None,
    previous_working_memory_update: TaskWorkingMemoryTickUpdate | dict[str, Any] | None,
    tick_number: int,
    teacher_gate: dict[str, Any],
    fresh_context: dict[str, Any],
    dry_run_stub: dict[str, Any],
    audit_stub: dict[str, Any],
    outcome_label: str,
    next_hint: str,
    recursive_call_requested: bool = False,
    automatic_loop_requested: bool = False,
    scheduler_requested: bool = False,
    free_action_selection_requested: bool = False,
) -> dict[str, Any]:
    if recursive_call_requested:
        raise ValueError("manual tick builder cannot recursively call itself")
    if automatic_loop_requested or scheduler_requested:
        raise ValueError("manual tick builder cannot create automatic loops or schedulers")
    if free_action_selection_requested:
        raise ValueError("manual tick builder cannot perform free action selection")
    if tick_number < 1:
        raise ValueError("tick_number must be positive")
    if not teacher_gate.get("teacher_gate_preserved", True):
        raise ValueError("teacher gate must be preserved")
    frame = (
        active_task_frame
        if isinstance(active_task_frame, ActiveTaskFrame)
        else ActiveTaskFrame.from_dict(dict(active_task_frame))
    )
    if frame.task_id != task_id:
        raise ValueError("task_id must match active task frame")
    frame_dict = frame.to_dict()
    frame_dict["current_tick"] = max(int(frame_dict.get("current_tick") or 0), tick_number - 1)
    frame = ActiveTaskFrame.from_dict(frame_dict)
    previous_update_id = _update_id(previous_working_memory_update)
    update_result = apply_task_working_memory_tick_update(
        frame,
        tick_id=f"manual_teacher_gated_tick_{tick_number}",
        after_step=f"manual_tick_{tick_number}_{next_hint}",
        observed_outcome_ref=f"outcome:{outcome_label}",
        observed_outcome_label=outcome_label,
        working_memory_delta={
            "manual_tick_number": tick_number,
            "previous_working_memory_update_id": previous_update_id,
        },
        next_candidate_hints_added=(next_hint,),
        continue_allowed_after_update=True,
        source_trace_refs=(
            f"previous_tick:{_previous_tick_id(previous_tick_stub_record)}",
            f"previous_working_memory_update:{previous_update_id}",
        ),
    )
    update = update_result["tick_update"]
    assert isinstance(update, TaskWorkingMemoryTickUpdate)
    tick_record = {
        "manual_teacher_gated_tick_stub_record_id": _new_tick_stub_id(tick_number),
        "task_id": task_id,
        "active_task_frame_id": frame.active_task_frame_id,
        "previous_tick_stub_record_id": _previous_tick_id(previous_tick_stub_record),
        "previous_working_memory_update_id": previous_update_id,
        "task_working_memory_update_id": update.task_working_memory_tick_update_id,
        "tick_number": tick_number,
        "manual_trigger": True,
        "teacher_gate_preserved": True,
        "fresh_context_used": True,
        "dry_run_stub_used": True,
        "audit_stub_used": True,
        "tick_stopped": True,
        "next_tick_created": False,
        "scheduler_used": False,
        "automatic_loop_created": False,
        "free_action_selection_used": False,
        "action_execution_used": False,
        "direct_memory_promotion_used": False,
        "recursive_call_used": False,
        "outcome_label": outcome_label,
        "next_candidate_hint": next_hint,
        "created_at": _now(),
        "trace_refs": [
            f"task:{task_id}",
            f"active_task_frame:{frame.active_task_frame_id}",
            f"task_working_memory_update:{update.task_working_memory_tick_update_id}",
            f"previous_working_memory_update:{previous_update_id}",
            f"teacher_gate:{teacher_gate.get('teacher_gate_id', 'manual')}",
            f"fresh_context:{fresh_context.get('fresh_context_id', 'manual')}",
            f"dry_run_stub:{dry_run_stub.get('dry_run_stub_id', 'manual')}",
            f"audit_stub:{audit_stub.get('audit_stub_id', 'manual')}",
        ],
    }
    return {
        "manual_teacher_gated_tick_stub_record": tick_record,
        "task_working_memory_tick_update": update.to_dict(),
        "updated_active_task_frame": update_result["updated_active_task_frame"].to_dict(),
        "tick_creation_summary": {
            "tick_number": tick_number,
            "task_id": task_id,
            "created_exactly_one_tick": True,
            "scheduler_used": False,
            "action_execution_used": False,
            "recursive_call_used": False,
        },
    }


def _previous_tick_id(previous_tick_stub_record: dict[str, Any] | None) -> str | None:
    if not previous_tick_stub_record:
        return None
    return (
        previous_tick_stub_record.get("manual_teacher_gated_tick_stub_record_id")
        or previous_tick_stub_record.get("third_tick_stub_record_id")
        or previous_tick_stub_record.get("second_tick_stub_id")
        or previous_tick_stub_record.get("tick_stub_id")
    )


def _update_id(update: TaskWorkingMemoryTickUpdate | dict[str, Any] | None) -> str | None:
    if update is None:
        return None
    if isinstance(update, TaskWorkingMemoryTickUpdate):
        return update.task_working_memory_tick_update_id
    return dict(update).get("task_working_memory_tick_update_id")


def _new_tick_stub_id(tick_number: int) -> str:
    return "manual_teacher_gated_tick_" + str(tick_number) + "_" + datetime.now(
        timezone.utc
    ).strftime("%Y%m%d%H%M%S%f")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
