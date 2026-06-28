"""Third-tick readiness checks from task Working Memory for ASHL Core v1."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar

from ashl_core_v1.memory.task_working_memory_lifecycle import ActiveTaskFrame
from ashl_core_v1.runtime.two_tick_task_working_memory_continuity_audit import (
    TwoTickTaskWorkingMemoryContinuityAudit,
    build_two_tick_task_working_memory_continuity_audit_demo,
)


THIRD_TICK_READINESS_ENV = "ASHL_CORE_V1_THIRD_TICK_READINESS_FROM_TASK_WM_DIR"
DEFAULT_THIRD_TICK_READINESS_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "third_tick_readiness_from_task_working_memory"
)

LAST_THIRD_TICK_READINESS_FILE = "last_third_tick_readiness.json"
THIRD_TICK_READINESS_HISTORY_FILE = "third_tick_readiness_history.jsonl"

READINESS_KIND = "third_tick_readiness_from_task_working_memory"
READY_STATUS = "ready_for_future_third_tick_stub"
TERMINAL_TASK_STATUSES = (
    "completed",
    "failed",
    "aborted",
    "teacher_stopped",
    "system_stopped",
)


def _plain(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    return value


def _tuple_of_str(name: str, value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    refs = tuple(value)
    if not all(isinstance(item, str) for item in refs):
        raise TypeError(f"{name} must contain only strings")
    return refs


@dataclass(frozen=True)
class ThirdTickReadinessFromTaskWorkingMemory:
    """Readiness record for a future manual teacher-gated third tick."""

    ALLOWED_STATUSES: ClassVar[set[str]] = {
        "ready_for_future_third_tick_stub",
        "blocked_two_tick_audit_not_passed",
        "blocked_missing_active_task_frame",
        "blocked_task_id_mismatch",
        "blocked_not_working_memory_layer",
        "blocked_tick2_not_using_working_memory",
        "blocked_tick2_not_using_tick1_outcome",
        "blocked_tick2_not_using_tick1_hint",
        "blocked_active_task_closed",
        "blocked_no_next_tick_context",
        "blocked_teacher_gate_missing",
        "blocked_manual_trigger_missing",
        "blocked_third_tick_already_created",
        "blocked_automatic_loop_detected",
        "blocked_action_execution_detected",
        "blocked_direct_memory_promotion_detected",
    }

    readiness_id: str
    readiness_kind: str
    task_id: str
    active_task_frame_id: str
    two_tick_audit_id: str
    first_tick_stub_record_id: str
    second_tick_stub_record_id: str
    two_tick_audit_passed: bool
    same_task_id_preserved: bool
    working_memory_layer_confirmed: bool
    tick2_read_updated_working_memory: bool
    tick2_used_tick1_outcome: bool
    tick2_used_tick1_candidate_hint: bool
    active_task_can_continue: bool
    active_task_not_closed: bool
    next_tick_context_available: bool
    fresh_context_required: bool
    teacher_gate_required: bool
    manual_trigger_required: bool
    third_tick_dry_run_required: bool
    third_tick_audit_required: bool
    third_tick_created: bool
    automatic_loop_detected: bool
    scheduler_detected: bool
    free_action_selection_detected: bool
    action_execution_detected: bool
    direct_memory_promotion_detected: bool
    unity_voice_bridge_detected: bool
    readiness_status: str
    readiness_notes: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.readiness_id:
            raise ValueError("readiness_id is required")
        if self.readiness_kind != READINESS_KIND:
            raise ValueError(f"unknown readiness_kind: {self.readiness_kind}")
        if self.readiness_status not in self.ALLOWED_STATUSES:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        object.__setattr__(
            self,
            "readiness_notes",
            _tuple_of_str("readiness_notes", self.readiness_notes),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ThirdTickReadinessFromTaskWorkingMemory":
        return cls(**dict(data))


def build_third_tick_readiness_from_task_working_memory(
    two_tick_audit: TwoTickTaskWorkingMemoryContinuityAudit | dict[str, Any] | None,
    active_task_frame: ActiveTaskFrame | dict[str, Any] | None,
    *,
    next_tick_context_available: bool = True,
    fresh_context_required: bool = True,
    teacher_gate_required: bool = True,
    manual_trigger_required: bool = True,
    third_tick_dry_run_required: bool = True,
    third_tick_audit_required: bool = True,
    third_tick_created: bool | None = None,
    automatic_loop_detected: bool | None = None,
    scheduler_detected: bool | None = None,
    free_action_selection_detected: bool | None = None,
    action_execution_detected: bool | None = None,
    direct_memory_promotion_detected: bool | None = None,
    unity_voice_bridge_detected: bool | None = None,
) -> ThirdTickReadinessFromTaskWorkingMemory:
    audit = _record_dict(two_tick_audit)
    frame = _record_dict(active_task_frame)
    task_status = str(frame.get("task_status") or "")
    frame_task_id = str(frame.get("task_id") or "")
    audit_task_id = str(audit.get("task_id") or "")
    frame_id = str(frame.get("active_task_frame_id") or "")
    audit_frame_id = str(audit.get("active_task_frame_id") or "")
    two_tick_audit_passed = audit.get("continuity_status") == "passed"
    same_task_id_preserved = audit.get("same_task_id_preserved") is True
    working_memory_layer_confirmed = (
        audit.get("working_memory_layer_confirmed") is True
        and frame.get("memory_layer") == "working"
    )
    tick2_read_updated_working_memory = audit.get("tick2_read_updated_working_memory") is True
    tick2_used_tick1_outcome = audit.get("tick2_uses_tick1_outcome") is True
    tick2_used_tick1_candidate_hint = (
        audit.get("tick2_uses_tick1_candidate_hint") is True
    )
    active_task_not_closed = bool(frame) and task_status not in TERMINAL_TASK_STATUSES
    active_task_can_continue = (
        active_task_not_closed
        and task_status == "active"
        and frame.get("continue_allowed") is True
    )
    readiness = ThirdTickReadinessFromTaskWorkingMemory(
        readiness_id=_new_readiness_id(),
        readiness_kind=READINESS_KIND,
        task_id=frame_task_id or audit_task_id,
        active_task_frame_id=frame_id or audit_frame_id,
        two_tick_audit_id=str(audit.get("audit_id") or ""),
        first_tick_stub_record_id=str(audit.get("first_tick_stub_record_id") or ""),
        second_tick_stub_record_id=str(audit.get("second_tick_stub_record_id") or ""),
        two_tick_audit_passed=two_tick_audit_passed,
        same_task_id_preserved=same_task_id_preserved,
        working_memory_layer_confirmed=working_memory_layer_confirmed,
        tick2_read_updated_working_memory=tick2_read_updated_working_memory,
        tick2_used_tick1_outcome=tick2_used_tick1_outcome,
        tick2_used_tick1_candidate_hint=tick2_used_tick1_candidate_hint,
        active_task_can_continue=active_task_can_continue,
        active_task_not_closed=active_task_not_closed,
        next_tick_context_available=next_tick_context_available,
        fresh_context_required=fresh_context_required,
        teacher_gate_required=teacher_gate_required,
        manual_trigger_required=manual_trigger_required,
        third_tick_dry_run_required=third_tick_dry_run_required,
        third_tick_audit_required=third_tick_audit_required,
        third_tick_created=_override_or_audit(
            third_tick_created,
            audit.get("third_tick_created"),
        ),
        automatic_loop_detected=_override_or_audit(
            automatic_loop_detected,
            audit.get("automatic_loop_detected"),
        ),
        scheduler_detected=_override_or_audit(
            scheduler_detected,
            audit.get("scheduler_detected"),
        ),
        free_action_selection_detected=_override_or_audit(
            free_action_selection_detected,
            audit.get("free_action_selection_detected"),
        ),
        action_execution_detected=_override_or_audit(
            action_execution_detected,
            audit.get("action_execution_detected"),
        ),
        direct_memory_promotion_detected=_override_or_audit(
            direct_memory_promotion_detected,
            audit.get("direct_memory_promotion_detected"),
        ),
        unity_voice_bridge_detected=_override_or_audit(
            unity_voice_bridge_detected,
            audit.get("unity_voice_bridge_detected"),
        ),
        readiness_status="blocked_two_tick_audit_not_passed",
        readiness_notes=(),
        source_trace_refs=_source_trace_refs(audit, frame),
    )
    status = _readiness_status(readiness, audit, frame, audit_task_id, frame_task_id)
    readiness = ThirdTickReadinessFromTaskWorkingMemory(
        **{
            **readiness.to_dict(),
            "readiness_status": status,
            "readiness_notes": _readiness_notes(status),
        }
    )
    validate_third_tick_readiness_from_task_working_memory(readiness)
    return readiness


def validate_third_tick_readiness_from_task_working_memory(
    readiness: ThirdTickReadinessFromTaskWorkingMemory | dict[str, Any],
) -> dict[str, object]:
    record = readiness if isinstance(readiness, ThirdTickReadinessFromTaskWorkingMemory) else (
        ThirdTickReadinessFromTaskWorkingMemory.from_dict(readiness)
    )
    errors: list[str] = []
    if record.readiness_status == READY_STATUS:
        for field_name in (
            "two_tick_audit_passed",
            "same_task_id_preserved",
            "working_memory_layer_confirmed",
            "tick2_read_updated_working_memory",
            "tick2_used_tick1_outcome",
            "tick2_used_tick1_candidate_hint",
            "active_task_can_continue",
            "active_task_not_closed",
            "next_tick_context_available",
            "fresh_context_required",
            "teacher_gate_required",
            "manual_trigger_required",
            "third_tick_dry_run_required",
            "third_tick_audit_required",
        ):
            if getattr(record, field_name) is not True:
                errors.append(f"{field_name}_false")
        for field_name in (
            "third_tick_created",
            "automatic_loop_detected",
            "scheduler_detected",
            "free_action_selection_detected",
            "action_execution_detected",
            "direct_memory_promotion_detected",
            "unity_voice_bridge_detected",
        ):
            if getattr(record, field_name) is not False:
                errors.append(f"{field_name}_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "readiness_status": record.readiness_status,
        "task_id": record.task_id,
        "active_task_frame_id": record.active_task_frame_id,
    }


def build_ready_third_tick_readiness_demo() -> dict[str, object]:
    continuity_demo = build_two_tick_task_working_memory_continuity_audit_demo()
    audit = continuity_demo["audit"]
    active_frame = continuity_demo["updated_active_task_frame"]
    readiness = build_third_tick_readiness_from_task_working_memory(
        audit,
        active_frame,
    )
    return {
        "third_tick_readiness_record_created": True,
        "readiness": readiness.to_dict(),
        "two_tick_audit": audit,
        "active_task_frame": active_frame,
        **_readiness_output_fields(readiness),
    }


def build_blocked_closed_task_third_tick_readiness_demo() -> dict[str, object]:
    continuity_demo = build_two_tick_task_working_memory_continuity_audit_demo()
    audit = continuity_demo["audit"]
    active_frame = dict(continuity_demo["updated_active_task_frame"])
    active_frame["task_status"] = "failed"
    active_frame["continue_allowed"] = False
    active_frame["stop_reason"] = "blocked_front_obstacle"
    readiness = build_third_tick_readiness_from_task_working_memory(
        audit,
        active_frame,
    )
    return {
        "third_tick_readiness_record_created": True,
        "readiness": readiness.to_dict(),
        "two_tick_audit": audit,
        "active_task_frame": active_frame,
        **_readiness_output_fields(readiness),
    }


def resolve_third_tick_readiness_from_task_working_memory_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(THIRD_TICK_READINESS_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_THIRD_TICK_READINESS_DIR


def ensure_third_tick_readiness_from_task_working_memory_store(
    base_dir: str | Path | None = None,
) -> Path:
    readiness_dir = resolve_third_tick_readiness_from_task_working_memory_dir(base_dir)
    readiness_dir.mkdir(parents=True, exist_ok=True)
    (readiness_dir / THIRD_TICK_READINESS_HISTORY_FILE).touch(exist_ok=True)
    return readiness_dir


def run_third_tick_readiness_from_task_working_memory(
    base_dir: str | Path | None = None,
) -> dict[str, object]:
    demo = build_ready_third_tick_readiness_demo()
    readiness = save_third_tick_readiness_from_task_working_memory(
        demo["readiness"],
        base_dir,
    )
    return {
        **demo,
        "readiness": readiness,
        **_readiness_output_fields(
            ThirdTickReadinessFromTaskWorkingMemory.from_dict(readiness)
        ),
    }


def run_closed_task_blocked_third_tick_readiness_demo(
    base_dir: str | Path | None = None,
) -> dict[str, object]:
    demo = build_blocked_closed_task_third_tick_readiness_demo()
    readiness = save_third_tick_readiness_from_task_working_memory(
        demo["readiness"],
        base_dir,
    )
    return {
        **demo,
        "readiness": readiness,
        **_readiness_output_fields(
            ThirdTickReadinessFromTaskWorkingMemory.from_dict(readiness)
        ),
    }


def save_third_tick_readiness_from_task_working_memory(
    readiness: ThirdTickReadinessFromTaskWorkingMemory | dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, object]:
    record = readiness.to_dict() if isinstance(readiness, ThirdTickReadinessFromTaskWorkingMemory) else dict(readiness)
    validate_third_tick_readiness_from_task_working_memory(record)
    readiness_dir = ensure_third_tick_readiness_from_task_working_memory_store(base_dir)
    (readiness_dir / LAST_THIRD_TICK_READINESS_FILE).write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (readiness_dir / THIRD_TICK_READINESS_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return record


def load_last_third_tick_readiness_from_task_working_memory(
    base_dir: str | Path | None = None,
) -> dict[str, object] | None:
    path = (
        resolve_third_tick_readiness_from_task_working_memory_dir(base_dir)
        / LAST_THIRD_TICK_READINESS_FILE
    )
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_third_tick_readiness_from_task_working_memory(
    base_dir: str | Path | None = None,
) -> dict[str, object]:
    path = (
        ensure_third_tick_readiness_from_task_working_memory_store(base_dir)
        / THIRD_TICK_READINESS_HISTORY_FILE
    )
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "third_tick_readiness_count": len(records),
        "third_tick_readiness_records": records,
    }


def _record_dict(record: Any) -> dict[str, Any]:
    if record is None:
        return {}
    if hasattr(record, "to_dict"):
        return dict(record.to_dict())
    return dict(record)


def _override_or_audit(override: bool | None, audit_value: Any) -> bool:
    if override is not None:
        return override
    return audit_value is True


def _readiness_status(
    readiness: ThirdTickReadinessFromTaskWorkingMemory,
    audit: dict[str, Any],
    frame: dict[str, Any],
    audit_task_id: str,
    frame_task_id: str,
) -> str:
    if not readiness.two_tick_audit_passed:
        return "blocked_two_tick_audit_not_passed"
    if not frame:
        return "blocked_missing_active_task_frame"
    if not readiness.same_task_id_preserved or audit_task_id != frame_task_id:
        return "blocked_task_id_mismatch"
    if not readiness.working_memory_layer_confirmed:
        return "blocked_not_working_memory_layer"
    if not readiness.tick2_read_updated_working_memory:
        return "blocked_tick2_not_using_working_memory"
    if not readiness.tick2_used_tick1_outcome:
        return "blocked_tick2_not_using_tick1_outcome"
    if not readiness.tick2_used_tick1_candidate_hint:
        return "blocked_tick2_not_using_tick1_hint"
    if not readiness.active_task_not_closed or not readiness.active_task_can_continue:
        return "blocked_active_task_closed"
    if not readiness.next_tick_context_available or not readiness.fresh_context_required:
        return "blocked_no_next_tick_context"
    if (
        not readiness.teacher_gate_required
        or not readiness.third_tick_dry_run_required
        or not readiness.third_tick_audit_required
    ):
        return "blocked_teacher_gate_missing"
    if not readiness.manual_trigger_required:
        return "blocked_manual_trigger_missing"
    if readiness.third_tick_created:
        return "blocked_third_tick_already_created"
    if readiness.automatic_loop_detected or readiness.scheduler_detected:
        return "blocked_automatic_loop_detected"
    if readiness.free_action_selection_detected or readiness.action_execution_detected:
        return "blocked_action_execution_detected"
    if readiness.direct_memory_promotion_detected:
        return "blocked_direct_memory_promotion_detected"
    if readiness.unity_voice_bridge_detected:
        return "blocked_action_execution_detected"
    return READY_STATUS


def _readiness_notes(status: str) -> tuple[str, ...]:
    if status == READY_STATUS:
        return (
            "two_tick_working_memory_chain_ready_for_future_manual_teacher_gated_third_tick",
            "third_tick_not_created",
        )
    return (status,)


def _source_trace_refs(*records: dict[str, Any]) -> tuple[str, ...]:
    refs: list[str] = []
    for record in records:
        for ref in record.get("source_trace_refs") or ():
            refs.append(str(ref))
        for ref in record.get("trace_refs") or ():
            refs.append(str(ref))
        if record.get("audit_id"):
            refs.append(f"two_tick_task_working_memory_audit:{record['audit_id']}")
        if record.get("active_task_frame_id"):
            refs.append(f"active_task_frame:{record['active_task_frame_id']}")
    return tuple(dict.fromkeys(refs))


def _readiness_output_fields(
    readiness: ThirdTickReadinessFromTaskWorkingMemory,
) -> dict[str, object]:
    return {
        "third_tick_readiness_record_created": True,
        "readiness_status": readiness.readiness_status,
        "task_id": readiness.task_id,
        "active_task_frame_id": readiness.active_task_frame_id,
        "two_tick_audit_id": readiness.two_tick_audit_id,
        "two_tick_audit_passed": readiness.two_tick_audit_passed,
        "same_task_id_preserved": readiness.same_task_id_preserved,
        "working_memory_layer_confirmed": readiness.working_memory_layer_confirmed,
        "tick2_read_updated_working_memory": readiness.tick2_read_updated_working_memory,
        "tick2_used_tick1_outcome": readiness.tick2_used_tick1_outcome,
        "tick2_used_tick1_candidate_hint": readiness.tick2_used_tick1_candidate_hint,
        "active_task_can_continue": readiness.active_task_can_continue,
        "fresh_context_required": readiness.fresh_context_required,
        "teacher_gate_required": readiness.teacher_gate_required,
        "manual_trigger_required": readiness.manual_trigger_required,
        "third_tick_dry_run_required": readiness.third_tick_dry_run_required,
        "third_tick_audit_required": readiness.third_tick_audit_required,
        "third_tick_created": readiness.third_tick_created,
        "automatic_loop_detected": readiness.automatic_loop_detected,
        "action_execution_detected": readiness.action_execution_detected,
        "direct_memory_promotion_detected": readiness.direct_memory_promotion_detected,
    }


def _new_readiness_id() -> str:
    return "third_tick_readiness_from_task_working_memory_" + datetime.now(
        timezone.utc
    ).strftime("%Y%m%d%H%M%S%f")
