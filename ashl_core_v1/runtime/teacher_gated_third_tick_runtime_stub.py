"""Teacher-gated third-tick runtime stub for ASHL Core v1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.memory.task_working_memory_lifecycle import (
    ActiveTaskFrame,
    TaskWorkingMemoryTickUpdate,
    apply_task_working_memory_tick_update,
)
from ashl_core_v1.runtime.third_tick_readiness_from_task_working_memory import (
    READY_STATUS,
    build_blocked_closed_task_third_tick_readiness_demo,
    build_ready_third_tick_readiness_demo,
)


THIRD_TICK_RUNTIME_STUB_ENV = "ASHL_CORE_V1_THIRD_TICK_RUNTIME_STUB_DIR"
DEFAULT_THIRD_TICK_RUNTIME_STUB_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "teacher_gated_third_tick_runtime_stub"
)

LAST_THIRD_TICK_STUB_FILE = "last_third_tick_stub_record.json"
THIRD_TICK_STUB_HISTORY_FILE = "third_tick_stub_record_history.jsonl"


def resolve_third_tick_runtime_stub_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(THIRD_TICK_RUNTIME_STUB_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_THIRD_TICK_RUNTIME_STUB_DIR


def ensure_third_tick_runtime_stub_store(base_dir: str | Path | None = None) -> Path:
    stub_dir = resolve_third_tick_runtime_stub_dir(base_dir)
    stub_dir.mkdir(parents=True, exist_ok=True)
    (stub_dir / THIRD_TICK_STUB_HISTORY_FILE).touch(exist_ok=True)
    return stub_dir


def build_teacher_gated_third_tick_runtime_stub(
    readiness_demo: dict[str, Any] | None = None,
    *,
    manual_trigger: bool = True,
) -> dict[str, Any]:
    demo = readiness_demo or build_ready_third_tick_readiness_demo()
    readiness = dict(demo.get("readiness") or {})
    active_frame = dict(demo.get("active_task_frame") or {})
    status = readiness.get("readiness_status")
    if status != READY_STATUS:
        return _blocked_third_tick_payload(readiness, active_frame, str(status))

    active_frame = dict(active_frame)
    active_frame["current_tick"] = max(int(active_frame.get("current_tick") or 0), 2)
    frame = ActiveTaskFrame.from_dict(active_frame)
    update_result = apply_task_working_memory_tick_update(
        frame,
        tick_id="tick_3_stub",
        after_step="third_tick_observe_or_adjust",
        observed_outcome_ref="outcome:third_tick_stub_observed",
        observed_outcome_label="third_tick_stub_observed",
        working_memory_delta={
            "third_tick_readiness_id": readiness["readiness_id"],
            "third_tick_stub_created": True,
        },
        next_candidate_hints_added=("manual_review_before_fourth_tick",),
        continue_allowed_after_update=False,
        stop_reason_after_update="third_tick_stub_stop",
        source_trace_refs=(
            f"third_tick_readiness:{readiness['readiness_id']}",
            f"two_tick_audit:{readiness['two_tick_audit_id']}",
        ),
    )
    update = update_result["tick_update"]
    assert isinstance(update, TaskWorkingMemoryTickUpdate)
    record = {
        "third_tick_stub_record_id": _new_third_tick_stub_id(),
        "task_id": readiness["task_id"],
        "active_task_frame_id": readiness["active_task_frame_id"],
        "source_third_tick_readiness_id": readiness["readiness_id"],
        "source_two_tick_audit_id": readiness["two_tick_audit_id"],
        "source_second_tick_stub_record_id": readiness["second_tick_stub_record_id"],
        "source_task_working_memory_update_refs": [
            f"task_working_memory_update:{update.task_working_memory_tick_update_id}",
        ],
        "tick_number": 3,
        "manual_trigger": manual_trigger,
        "teacher_gate_preserved": True,
        "fresh_context_used": True,
        "working_memory_read": True,
        "third_tick_created": True,
        "third_tick_stopped": True,
        "next_tick_created": False,
        "scheduler_used": False,
        "automatic_loop_created": False,
        "free_action_selection_used": False,
        "action_execution_used": False,
        "direct_memory_promotion_used": False,
        "unity_voice_bridge_used": False,
        "third_tick_status": "third_tick_stub_record_created",
        "created_at": _now(),
        "source_trace_refs": [
            f"active_task_frame:{readiness['active_task_frame_id']}",
            f"third_tick_readiness:{readiness['readiness_id']}",
            f"two_tick_audit:{readiness['two_tick_audit_id']}",
            f"second_tick_stub:{readiness['second_tick_stub_record_id']}",
            f"task_working_memory_update:{update.task_working_memory_tick_update_id}",
        ],
    }
    audit_stub = {
        "third_tick_audit_stub_id": _new_third_tick_audit_id(),
        "source_third_tick_stub_record_id": record["third_tick_stub_record_id"],
        "teacher_gate_preserved": True,
        "manual_trigger_preserved": manual_trigger,
        "third_tick_stopped": True,
        "next_tick_created": False,
        "scheduler_used": False,
        "action_execution_used": False,
        "direct_memory_promotion_used": False,
        "audit_status": "passed",
        "created_at": _now(),
    }
    return {
        "third_tick_runtime_stub_created": True,
        "third_tick_stub_record": record,
        "third_tick_working_memory_update": update.to_dict(),
        "third_tick_audit_stub": audit_stub,
        "third_tick_stub_record_id": record["third_tick_stub_record_id"],
        "task_id": record["task_id"],
        "active_task_frame_id": record["active_task_frame_id"],
        "source_second_tick_stub_record_id": record["source_second_tick_stub_record_id"],
        "third_tick_created": True,
        "third_tick_stopped": True,
        "next_tick_created": False,
        "created_at": _now(),
    }


def run_teacher_gated_third_tick_runtime_stub(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    return save_third_tick_stub_record(build_teacher_gated_third_tick_runtime_stub(), base_dir)


def run_blocked_third_tick_runtime_stub_demo(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    return save_third_tick_stub_record(
        build_teacher_gated_third_tick_runtime_stub(
            build_blocked_closed_task_third_tick_readiness_demo()
        ),
        base_dir,
    )


def save_third_tick_stub_record(
    payload: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    _validate_payload(payload)
    stub_dir = ensure_third_tick_runtime_stub_store(base_dir)
    (stub_dir / LAST_THIRD_TICK_STUB_FILE).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (stub_dir / THIRD_TICK_STUB_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(payload)


def load_last_third_tick_stub_record(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = resolve_third_tick_runtime_stub_dir(base_dir) / LAST_THIRD_TICK_STUB_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_third_tick_stub_records(base_dir: str | Path | None = None) -> dict[str, Any]:
    path = ensure_third_tick_runtime_stub_store(base_dir) / THIRD_TICK_STUB_HISTORY_FILE
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "third_tick_stub_record_count": len(records),
        "third_tick_stub_records": records,
    }


def _blocked_third_tick_payload(
    readiness: dict[str, Any],
    active_frame: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    record = {
        "third_tick_stub_record_id": _new_third_tick_stub_id(),
        "task_id": readiness.get("task_id") or active_frame.get("task_id"),
        "active_task_frame_id": readiness.get("active_task_frame_id")
        or active_frame.get("active_task_frame_id"),
        "source_third_tick_readiness_id": readiness.get("readiness_id"),
        "source_two_tick_audit_id": readiness.get("two_tick_audit_id"),
        "source_second_tick_stub_record_id": readiness.get("second_tick_stub_record_id"),
        "source_task_working_memory_update_refs": [],
        "tick_number": 3,
        "manual_trigger": True,
        "teacher_gate_preserved": False,
        "fresh_context_used": False,
        "working_memory_read": False,
        "third_tick_created": False,
        "third_tick_stopped": True,
        "next_tick_created": False,
        "scheduler_used": False,
        "automatic_loop_created": False,
        "free_action_selection_used": False,
        "action_execution_used": False,
        "direct_memory_promotion_used": False,
        "unity_voice_bridge_used": False,
        "third_tick_status": "blocked_by_readiness",
        "blocked_reason": reason,
        "created_at": _now(),
        "source_trace_refs": [],
    }
    return {
        "third_tick_runtime_stub_created": False,
        "third_tick_stub_record": record,
        "third_tick_working_memory_update": None,
        "third_tick_audit_stub": {
            "third_tick_audit_stub_id": _new_third_tick_audit_id(),
            "source_third_tick_stub_record_id": record["third_tick_stub_record_id"],
            "audit_status": "blocked_by_readiness",
            "blocked_reason": reason,
            "created_at": _now(),
        },
        "third_tick_stub_record_id": record["third_tick_stub_record_id"],
        "task_id": record["task_id"],
        "active_task_frame_id": record["active_task_frame_id"],
        "third_tick_created": False,
        "third_tick_stopped": True,
        "next_tick_created": False,
        "created_at": _now(),
    }


def _validate_payload(payload: dict[str, Any]) -> None:
    if "third_tick_stub_record" not in payload:
        raise ValueError("third_tick_stub_record is required")
    record = payload["third_tick_stub_record"]
    if record.get("tick_number") != 3:
        raise ValueError("third tick record must have tick_number 3")
    if record.get("next_tick_created") is not False:
        raise ValueError("third tick must not create a next tick")
    if record.get("scheduler_used") is not False:
        raise ValueError("third tick must not use scheduler")
    if record.get("action_execution_used") is not False:
        raise ValueError("third tick must not execute actions")
    if record.get("direct_memory_promotion_used") is not False:
        raise ValueError("third tick must not directly promote memory")


def _new_third_tick_stub_id() -> str:
    return "third_tick_stub_record_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _new_third_tick_audit_id() -> str:
    return "third_tick_audit_stub_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
