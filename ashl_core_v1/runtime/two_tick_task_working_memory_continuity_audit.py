"""Audit two-tick task continuity through Working Memory for ASHL Core v1."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar

from ashl_core_v1.memory.task_working_memory_lifecycle import (
    ActiveTaskFrame,
    TaskWorkingMemoryClosureRecord,
    TaskWorkingMemoryDispositionRecord,
    TaskWorkingMemoryTickUpdate,
    apply_task_working_memory_tick_update,
    close_task_working_memory,
    create_active_task_frame,
    create_task_working_memory_disposition,
)
from ashl_core_v1.runtime.teacher_gated_one_tick_runtime_stub import (
    PRESERVED_BLOCKED_SURFACES,
    load_last_tick_stub_record,
)
from ashl_core_v1.runtime.teacher_gated_two_tick_runtime_stub import (
    PRESERVED_SECOND_TICK_BLOCKED_SURFACES,
    load_last_second_tick_stub_record,
)


TWO_TICK_TASK_WM_AUDIT_ENV = "ASHL_CORE_V1_TWO_TICK_TASK_WM_AUDIT_DIR"
DEFAULT_TWO_TICK_TASK_WM_AUDIT_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "two_tick_task_working_memory_continuity_audit"
)

LAST_TWO_TICK_TASK_WM_AUDIT_FILE = "last_two_tick_task_working_memory_audit.json"
TWO_TICK_TASK_WM_AUDIT_HISTORY_FILE = "two_tick_task_working_memory_audit_history.jsonl"

AUDIT_KIND = "two_tick_task_working_memory_continuity_audit"
MANUAL_TRIGGERS = ("manual_cli", "manual_function_call")
FIRST_TICK_TEACHER_GATES = ("allowed_for_one_tick_stub", "needs_teacher_review")
SECOND_TICK_TEACHER_GATES = ("allowed_for_second_tick_stub", "needs_teacher_review")
FORBIDDEN_DIRECT_MEMORY_LAYERS = ("core", "long_term", "archive", "anchor")


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
class TwoTickTaskWorkingMemoryContinuityAudit:
    """Audit proof that tick 2 continues a task through Working Memory."""

    ALLOWED_STATUSES: ClassVar[set[str]] = {
        "passed",
        "failed",
        "blocked_missing_task_frame",
        "blocked_missing_tick1",
        "blocked_missing_tick2",
        "blocked_missing_tick1_update",
        "blocked_missing_tick2_working_memory_read",
        "blocked_task_id_mismatch",
        "blocked_not_working_memory_layer",
        "blocked_tick2_ignores_tick1_outcome",
        "blocked_tick2_ignores_working_memory_hint",
        "blocked_teacher_gate_missing",
        "blocked_second_tick_not_stopped",
        "blocked_third_tick_detected",
        "blocked_automatic_loop_detected",
        "blocked_action_execution_detected",
        "blocked_direct_memory_promotion_detected",
    }

    audit_id: str
    audit_kind: str
    task_id: str
    active_task_frame_id: str
    first_tick_stub_record_id: str
    second_tick_stub_record_id: str
    first_tick_update_id: str | None
    second_tick_update_id: str | None
    tick_sequence: tuple[int, int]
    same_task_id_preserved: bool
    working_memory_layer_confirmed: bool
    tick1_updated_working_memory: bool
    tick2_read_updated_working_memory: bool
    tick2_uses_tick1_outcome: bool
    tick2_uses_tick1_candidate_hint: bool
    tick2_continues_active_task_frame: bool
    teacher_gate_preserved: bool
    manual_trigger_preserved: bool
    second_tick_stopped: bool
    third_tick_created: bool
    automatic_loop_detected: bool
    scheduler_detected: bool
    free_action_selection_detected: bool
    action_execution_detected: bool
    direct_memory_promotion_detected: bool
    unity_voice_bridge_detected: bool
    continuity_status: str
    continuity_notes: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.audit_id:
            raise ValueError("audit_id is required")
        if self.audit_kind != AUDIT_KIND:
            raise ValueError(f"unknown audit_kind: {self.audit_kind}")
        if self.continuity_status not in self.ALLOWED_STATUSES:
            raise ValueError(f"unknown continuity_status: {self.continuity_status}")
        object.__setattr__(self, "tick_sequence", tuple(self.tick_sequence))
        if self.tick_sequence != (1, 2):
            raise ValueError("tick_sequence must be (1, 2)")
        object.__setattr__(
            self,
            "continuity_notes",
            _tuple_of_str("continuity_notes", self.continuity_notes),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TwoTickTaskWorkingMemoryContinuityAudit":
        return cls(**dict(data))


def build_two_tick_task_working_memory_continuity_audit(
    active_task_frame: ActiveTaskFrame | dict[str, Any] | None,
    first_tick_stub_record: dict[str, Any] | None,
    second_tick_stub_record: dict[str, Any] | None,
    first_tick_update: TaskWorkingMemoryTickUpdate | dict[str, Any] | None,
    second_tick_update: TaskWorkingMemoryTickUpdate | dict[str, Any] | None = None,
    task_closure_record: TaskWorkingMemoryClosureRecord | dict[str, Any] | None = None,
    task_working_memory_disposition: (
        TaskWorkingMemoryDispositionRecord | dict[str, Any] | None
    ) = None,
) -> TwoTickTaskWorkingMemoryContinuityAudit:
    task_frame = _record_dict(active_task_frame)
    tick1 = dict(first_tick_stub_record or {})
    tick2 = dict(second_tick_stub_record or {})
    update1 = _record_dict(first_tick_update)
    update2 = _record_dict(second_tick_update)
    closure = _record_dict(task_closure_record)
    disposition = _record_dict(task_working_memory_disposition)

    task_id = str(task_frame.get("task_id") or "")
    active_task_frame_id = str(task_frame.get("active_task_frame_id") or "")
    first_tick_id = str(tick1.get("tick_stub_id") or "")
    second_tick_id = str(tick2.get("second_tick_stub_id") or "")
    first_update_id = update1.get("task_working_memory_tick_update_id")
    second_update_id = update2.get("task_working_memory_tick_update_id")

    working_memory_layer_confirmed = task_frame.get("memory_layer") == "working" and bool(
        task_id
    )
    same_task_id_preserved = (
        bool(task_id)
        and _tick_links_task(tick1, task_id, active_task_frame_id)
        and _tick_links_task(tick2, task_id, active_task_frame_id)
    )
    tick1_updated_working_memory = (
        bool(update1)
        and update1.get("active_task_frame_id") == active_task_frame_id
        and bool(update1.get("observed_outcome_label"))
        and bool(update1.get("working_memory_delta"))
        and bool(update1.get("next_candidate_hints_added"))
    )
    tick2_continues_active_task_frame = _tick_links_active_frame(
        tick2,
        active_task_frame_id,
    )
    tick2_read_updated_working_memory = _tick_links_update(tick2, str(first_update_id or ""))
    tick2_uses_tick1_outcome = _tick_uses_outcome(
        tick2,
        str(update1.get("observed_outcome_label") or ""),
    )
    tick2_uses_tick1_candidate_hint = _tick_uses_any_hint(
        tick2,
        tuple(str(item) for item in update1.get("next_candidate_hints_added") or ()),
    )
    teacher_gate_preserved = (
        tick1.get("teacher_gate_status") in FIRST_TICK_TEACHER_GATES
        and tick2.get("teacher_gate_status") in SECOND_TICK_TEACHER_GATES
    )
    manual_trigger_preserved = (
        tick1.get("trigger_kind") in MANUAL_TRIGGERS
        and tick2.get("trigger_kind") in MANUAL_TRIGGERS
    )
    second_tick_stopped = tick2.get("stopped_after_second_tick") is True
    third_tick_created = tick2.get("third_tick_created") is True
    scheduler_detected = bool(tick2.get("scheduler_created")) or _blocked_missing(
        tick2,
        "background_scheduler",
    )
    free_action_selection_detected = bool(
        tick2.get("free_action_selection_created")
    ) or _blocked_missing(tick2, "free_action_selection")
    action_execution_detected = bool(tick2.get("action_execution_created")) or _blocked_missing(
        tick2,
        "action_execution",
    )
    automatic_loop_detected = (
        tick2.get("continuous_loop_created") is True
        or scheduler_detected
        or free_action_selection_detected
    )
    direct_memory_promotion_detected = _contains_direct_memory_promotion(
        task_frame,
        update1,
        update2,
        closure,
        disposition,
        tick1,
        tick2,
    )
    unity_voice_bridge_detected = (
        bool(tick2.get("unity_operation_created"))
        or bool(tick2.get("voice_output_created"))
        or bool(tick2.get("external_bridge_operation_created"))
        or _blocked_missing(tick2, "unity_home_operation")
        or _blocked_missing(tick2, "voice_output")
        or _blocked_missing(tick2, "external_bridge_operation")
    )

    notes = _continuity_notes(
        task_frame,
        tick1,
        tick2,
        update1,
        working_memory_layer_confirmed,
        same_task_id_preserved,
        tick1_updated_working_memory,
        tick2_read_updated_working_memory,
        tick2_uses_tick1_outcome,
        tick2_uses_tick1_candidate_hint,
        tick2_continues_active_task_frame,
        teacher_gate_preserved,
        manual_trigger_preserved,
        second_tick_stopped,
        third_tick_created,
        automatic_loop_detected,
        action_execution_detected,
        direct_memory_promotion_detected,
        unity_voice_bridge_detected,
    )
    audit = TwoTickTaskWorkingMemoryContinuityAudit(
        audit_id=_new_audit_id(),
        audit_kind=AUDIT_KIND,
        task_id=task_id,
        active_task_frame_id=active_task_frame_id,
        first_tick_stub_record_id=first_tick_id,
        second_tick_stub_record_id=second_tick_id,
        first_tick_update_id=str(first_update_id) if first_update_id else None,
        second_tick_update_id=str(second_update_id) if second_update_id else None,
        tick_sequence=(1, 2),
        same_task_id_preserved=same_task_id_preserved,
        working_memory_layer_confirmed=working_memory_layer_confirmed,
        tick1_updated_working_memory=tick1_updated_working_memory,
        tick2_read_updated_working_memory=tick2_read_updated_working_memory,
        tick2_uses_tick1_outcome=tick2_uses_tick1_outcome,
        tick2_uses_tick1_candidate_hint=tick2_uses_tick1_candidate_hint,
        tick2_continues_active_task_frame=tick2_continues_active_task_frame,
        teacher_gate_preserved=teacher_gate_preserved,
        manual_trigger_preserved=manual_trigger_preserved,
        second_tick_stopped=second_tick_stopped,
        third_tick_created=third_tick_created,
        automatic_loop_detected=automatic_loop_detected,
        scheduler_detected=scheduler_detected,
        free_action_selection_detected=free_action_selection_detected,
        action_execution_detected=action_execution_detected,
        direct_memory_promotion_detected=direct_memory_promotion_detected,
        unity_voice_bridge_detected=unity_voice_bridge_detected,
        continuity_status=_continuity_status(notes),
        continuity_notes=notes,
        source_trace_refs=_source_trace_refs(
            task_frame,
            tick1,
            tick2,
            update1,
            update2,
            closure,
            disposition,
        ),
    )
    validate_two_tick_task_working_memory_continuity_audit(audit)
    return audit


def validate_two_tick_task_working_memory_continuity_audit(
    audit: TwoTickTaskWorkingMemoryContinuityAudit | dict[str, Any],
) -> dict[str, object]:
    record = audit if isinstance(audit, TwoTickTaskWorkingMemoryContinuityAudit) else (
        TwoTickTaskWorkingMemoryContinuityAudit.from_dict(audit)
    )
    errors: list[str] = []
    if record.continuity_status == "passed":
        for field_name in (
            "same_task_id_preserved",
            "working_memory_layer_confirmed",
            "tick1_updated_working_memory",
            "tick2_read_updated_working_memory",
            "tick2_uses_tick1_outcome",
            "tick2_uses_tick1_candidate_hint",
            "tick2_continues_active_task_frame",
            "teacher_gate_preserved",
            "manual_trigger_preserved",
            "second_tick_stopped",
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
        "continuity_status": record.continuity_status,
        "task_id": record.task_id,
        "active_task_frame_id": record.active_task_frame_id,
    }


def build_two_tick_task_working_memory_continuity_audit_demo() -> dict[str, object]:
    active_frame = create_active_task_frame(
        current_goal="handle front obstacle",
        approved_scope="sandbox_working_memory_continuity_audit_only",
        task_id="handle_front_obstacle",
        current_step="step_forward",
        source_trace_refs=("demo:two_tick_task_working_memory_continuity_audit",),
    )
    update_result = apply_task_working_memory_tick_update(
        active_frame,
        tick_id="tick_1_stub",
        after_step="step_forward",
        observed_outcome_ref="outcome:blocked_front_obstacle",
        observed_outcome_label="blocked",
        working_memory_delta={"last_outcome_label": "blocked"},
        next_candidate_hints_added=("observe_or_adjust",),
        continue_allowed_after_update=True,
        source_trace_refs=("first_tick_stub:tick_1_stub",),
    )
    tick1_update = update_result["tick_update"]
    updated_frame = update_result["updated_active_task_frame"]
    assert isinstance(tick1_update, TaskWorkingMemoryTickUpdate)
    assert isinstance(updated_frame, ActiveTaskFrame)
    closure = close_task_working_memory(
        updated_frame,
        final_task_status="failed",
        stop_reason="blocked_front_obstacle",
        important_trace_refs=(f"tick_update:{tick1_update.task_working_memory_tick_update_id}",),
    )
    disposition = create_task_working_memory_disposition(
        closure,
        discard_scratch_refs=("scratch:front_obstacle_retry_notes",),
        session_summary_refs=(f"session_summary_candidate:{closure.task_closure_record_id}",),
        learning_digest_candidate_refs=(
            f"learning_digest_candidate:{closure.task_closure_record_id}:blocked",
        ),
    )
    first_tick = _demo_first_tick_stub(active_frame, tick1_update)
    second_tick = _demo_second_tick_stub(active_frame, tick1_update, first_tick)
    audit = build_two_tick_task_working_memory_continuity_audit(
        active_frame,
        first_tick,
        second_tick,
        tick1_update,
        None,
        closure,
        disposition,
    )
    return {
        "two_tick_task_working_memory_continuity_audit_created": True,
        "audit": audit.to_dict(),
        "active_task_frame": active_frame.to_dict(),
        "updated_active_task_frame": updated_frame.to_dict(),
        "first_tick_stub_record": first_tick,
        "second_tick_stub_record": second_tick,
        "first_tick_working_memory_update": tick1_update.to_dict(),
        "task_closure_record": closure.to_dict(),
        "task_working_memory_disposition": disposition.to_dict(),
        **_audit_output_fields(audit),
    }


def resolve_two_tick_task_working_memory_continuity_audit_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(TWO_TICK_TASK_WM_AUDIT_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_TWO_TICK_TASK_WM_AUDIT_DIR


def ensure_two_tick_task_working_memory_continuity_audit_store(
    base_dir: str | Path | None = None,
) -> Path:
    audit_dir = resolve_two_tick_task_working_memory_continuity_audit_dir(base_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)
    (audit_dir / TWO_TICK_TASK_WM_AUDIT_HISTORY_FILE).touch(exist_ok=True)
    return audit_dir


def run_two_tick_task_working_memory_continuity_audit(
    base_dir: str | Path | None = None,
) -> dict[str, object]:
    demo = build_two_tick_task_working_memory_continuity_audit_demo()
    audit = save_two_tick_task_working_memory_continuity_audit(
        demo["audit"],
        base_dir,
    )
    return {
        **demo,
        "audit": audit,
        **_audit_output_fields(TwoTickTaskWorkingMemoryContinuityAudit.from_dict(audit)),
    }


def save_two_tick_task_working_memory_continuity_audit(
    audit: TwoTickTaskWorkingMemoryContinuityAudit | dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, object]:
    record = audit.to_dict() if isinstance(audit, TwoTickTaskWorkingMemoryContinuityAudit) else dict(audit)
    validate_two_tick_task_working_memory_continuity_audit(record)
    audit_dir = ensure_two_tick_task_working_memory_continuity_audit_store(base_dir)
    (audit_dir / LAST_TWO_TICK_TASK_WM_AUDIT_FILE).write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (audit_dir / TWO_TICK_TASK_WM_AUDIT_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return record


def load_last_two_tick_task_working_memory_continuity_audit(
    base_dir: str | Path | None = None,
) -> dict[str, object] | None:
    path = (
        resolve_two_tick_task_working_memory_continuity_audit_dir(base_dir)
        / LAST_TWO_TICK_TASK_WM_AUDIT_FILE
    )
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_two_tick_task_working_memory_continuity_audits(
    base_dir: str | Path | None = None,
) -> dict[str, object]:
    path = (
        ensure_two_tick_task_working_memory_continuity_audit_store(base_dir)
        / TWO_TICK_TASK_WM_AUDIT_HISTORY_FILE
    )
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "two_tick_task_working_memory_continuity_audit_count": len(records),
        "two_tick_task_working_memory_continuity_audits": records,
    }


def collect_two_tick_task_working_memory_continuity_audit_sources(
    base_dir: str | Path | None = None,
) -> dict[str, object]:
    return {
        "first_tick_stub_record": load_last_tick_stub_record(base_dir),
        "second_tick_stub_record": load_last_second_tick_stub_record(base_dir),
    }


def _record_dict(record: Any) -> dict[str, Any]:
    if record is None:
        return {}
    if hasattr(record, "to_dict"):
        return dict(record.to_dict())
    return dict(record)


def _tick_links_task(record: dict[str, Any], task_id: str, active_task_frame_id: str) -> bool:
    if record.get("task_id") == task_id:
        return True
    refs = _record_text(record)
    return f"task:{task_id}" in refs or f"active_task_frame:{active_task_frame_id}" in refs


def _tick_links_active_frame(record: dict[str, Any], active_task_frame_id: str) -> bool:
    if not active_task_frame_id:
        return False
    if record.get("source_active_task_frame_id") == active_task_frame_id:
        return True
    return f"active_task_frame:{active_task_frame_id}" in _record_text(record)


def _tick_links_update(record: dict[str, Any], update_id: str) -> bool:
    if not update_id:
        return False
    refs = record.get("source_task_working_memory_update_refs") or ()
    if update_id in refs:
        return True
    return f"task_working_memory_update:{update_id}" in _record_text(record)


def _tick_uses_outcome(record: dict[str, Any], outcome_label: str) -> bool:
    return bool(outcome_label) and outcome_label in _tick_semantic_text(record)


def _tick_uses_any_hint(record: dict[str, Any], hints: tuple[str, ...]) -> bool:
    text = _tick_semantic_text(record)
    return any(hint and hint in text for hint in hints)


def _blocked_missing(record: dict[str, Any], surface: str) -> bool:
    blocked = set(record.get("preserved_blocked_surfaces") or [])
    return surface not in blocked


def _contains_direct_memory_promotion(*records: dict[str, Any]) -> bool:
    haystack = json.dumps(records, ensure_ascii=False).lower()
    return any(f"{layer}:" in haystack for layer in FORBIDDEN_DIRECT_MEMORY_LAYERS)


def _record_text(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, sort_keys=True).lower()


def _tick_semantic_text(record: dict[str, Any]) -> str:
    semantic_parts: list[str] = []
    for key in (
        "trace_refs",
        "source_trace_refs",
        "second_tick_summary",
        "tick_stub_summary",
        "working_memory_context_summary",
        "reason_summary",
    ):
        value = record.get(key)
        if isinstance(value, (list, tuple)):
            semantic_parts.extend(str(item) for item in value)
        elif value is not None:
            semantic_parts.append(str(value))
    return " ".join(semantic_parts).lower()


def _continuity_notes(
    task_frame: dict[str, Any],
    tick1: dict[str, Any],
    tick2: dict[str, Any],
    update1: dict[str, Any],
    working_memory_layer_confirmed: bool,
    same_task_id_preserved: bool,
    tick1_updated_working_memory: bool,
    tick2_read_updated_working_memory: bool,
    tick2_uses_tick1_outcome: bool,
    tick2_uses_tick1_candidate_hint: bool,
    tick2_continues_active_task_frame: bool,
    teacher_gate_preserved: bool,
    manual_trigger_preserved: bool,
    second_tick_stopped: bool,
    third_tick_created: bool,
    automatic_loop_detected: bool,
    action_execution_detected: bool,
    direct_memory_promotion_detected: bool,
    unity_voice_bridge_detected: bool,
) -> tuple[str, ...]:
    if not task_frame:
        return ("blocked_missing_task_frame",)
    if not working_memory_layer_confirmed:
        return ("blocked_not_working_memory_layer",)
    if not tick1:
        return ("blocked_missing_tick1",)
    if not tick2:
        return ("blocked_missing_tick2",)
    if not same_task_id_preserved:
        return ("blocked_task_id_mismatch",)
    if not update1:
        return ("blocked_missing_tick1_update",)
    if not tick1_updated_working_memory:
        return ("blocked_missing_tick1_update",)
    if not tick2_continues_active_task_frame or not tick2_read_updated_working_memory:
        return ("blocked_missing_tick2_working_memory_read",)
    if not tick2_uses_tick1_outcome:
        return ("blocked_tick2_ignores_tick1_outcome",)
    if not tick2_uses_tick1_candidate_hint:
        return ("blocked_tick2_ignores_working_memory_hint",)
    if not teacher_gate_preserved or not manual_trigger_preserved:
        return ("blocked_teacher_gate_missing",)
    if not second_tick_stopped:
        return ("blocked_second_tick_not_stopped",)
    if third_tick_created:
        return ("blocked_third_tick_detected",)
    if automatic_loop_detected:
        return ("blocked_automatic_loop_detected",)
    if action_execution_detected:
        return ("blocked_action_execution_detected",)
    if direct_memory_promotion_detected:
        return ("blocked_direct_memory_promotion_detected",)
    if unity_voice_bridge_detected:
        return ("failed",)
    return ("passed", "tick2_continues_task_through_working_memory")


def _continuity_status(notes: tuple[str, ...]) -> str:
    return "passed" if notes and notes[0] == "passed" else notes[0]


def _source_trace_refs(*records: dict[str, Any]) -> tuple[str, ...]:
    refs: list[str] = []
    for record in records:
        for ref in record.get("source_trace_refs") or ():
            refs.append(str(ref))
        for ref in record.get("trace_refs") or ():
            refs.append(str(ref))
    return tuple(dict.fromkeys(refs))


def _demo_first_tick_stub(
    active_frame: ActiveTaskFrame,
    tick1_update: TaskWorkingMemoryTickUpdate,
) -> dict[str, Any]:
    return {
        "tick_stub_id": "tick_1_stub",
        "source_readiness_review_id": "readiness_review_demo",
        "source_tick_context_id": "tick_context_1_demo",
        "source_tick_dry_run_id": "tick_dry_run_1_demo",
        "source_tick_dry_run_audit_id": "tick_dry_run_audit_1_demo",
        "trigger_kind": "manual_function_call",
        "teacher_gate_status": "allowed_for_one_tick_stub",
        "tick_stub_status": "tick_stub_record_created",
        "tick_mode": "observe_only",
        "tick_stub_kind": "observe_only_stub",
        "tick_stub_summary": "tick 1 recorded blocked outcome for front obstacle task",
        "read_sources": ["runtime_stub_readiness_review", "tick_context"],
        "produced_surfaces": ["tick_stub_record", "observation_trace_summary"],
        "preserved_blocked_surfaces": list(PRESERVED_BLOCKED_SURFACES),
        "stopped_after_one_tick": True,
        "created_at": _now(),
        "trace_refs": [
            f"task:{active_frame.task_id}",
            f"active_task_frame:{active_frame.active_task_frame_id}",
            f"task_working_memory_update:{tick1_update.task_working_memory_tick_update_id}",
            f"outcome:{tick1_update.observed_outcome_label}",
            "hint:observe_or_adjust",
        ],
    }


def _demo_second_tick_stub(
    active_frame: ActiveTaskFrame,
    tick1_update: TaskWorkingMemoryTickUpdate,
    first_tick: dict[str, Any],
) -> dict[str, Any]:
    return {
        "second_tick_stub_id": "tick_2_stub",
        "source_first_tick_stub_id": first_tick["tick_stub_id"],
        "source_two_tick_precheck_id": "two_tick_precheck_demo",
        "source_fresh_tick_context_id": "tick_context_2_demo",
        "source_second_tick_dry_run_id": "tick_dry_run_2_demo",
        "source_second_tick_dry_run_audit_id": "tick_dry_run_audit_2_demo",
        "trigger_kind": "manual_function_call",
        "teacher_gate_status": "allowed_for_second_tick_stub",
        "second_tick_status": "second_tick_stub_record_created",
        "second_tick_mode": "observe_only",
        "second_tick_stub_kind": "observe_only_second_stub",
        "second_tick_summary": "tick 2 read blocked outcome and observe_or_adjust hint",
        "previous_tick_summary": first_tick["tick_stub_summary"],
        "fresh_context_used": True,
        "second_dry_run_used": True,
        "second_audit_used": True,
        "produced_surfaces": ["second_tick_stub_record", "observation_trace_summary"],
        "preserved_blocked_surfaces": list(PRESERVED_SECOND_TICK_BLOCKED_SURFACES),
        "stopped_after_second_tick": True,
        "third_tick_created": False,
        "continuous_loop_created": False,
        "created_at": _now(),
        "source_active_task_frame_id": active_frame.active_task_frame_id,
        "source_task_working_memory_update_refs": (
            tick1_update.task_working_memory_tick_update_id,
        ),
        "trace_refs": [
            f"task:{active_frame.task_id}",
            f"active_task_frame:{active_frame.active_task_frame_id}",
            f"task_working_memory_update:{tick1_update.task_working_memory_tick_update_id}",
            f"outcome:{tick1_update.observed_outcome_label}",
            "hint:observe_or_adjust",
        ],
    }


def _audit_output_fields(
    audit: TwoTickTaskWorkingMemoryContinuityAudit,
) -> dict[str, object]:
    return {
        "two_tick_task_working_memory_continuity_audit_created": True,
        "continuity_status": audit.continuity_status,
        "task_id": audit.task_id,
        "active_task_frame_id": audit.active_task_frame_id,
        "first_tick_stub_record_id": audit.first_tick_stub_record_id,
        "second_tick_stub_record_id": audit.second_tick_stub_record_id,
        "same_task_id_preserved": audit.same_task_id_preserved,
        "working_memory_layer_confirmed": audit.working_memory_layer_confirmed,
        "tick1_updated_working_memory": audit.tick1_updated_working_memory,
        "tick2_read_updated_working_memory": audit.tick2_read_updated_working_memory,
        "tick2_uses_tick1_outcome": audit.tick2_uses_tick1_outcome,
        "tick2_uses_tick1_candidate_hint": audit.tick2_uses_tick1_candidate_hint,
        "third_tick_created": audit.third_tick_created,
        "automatic_loop_detected": audit.automatic_loop_detected,
        "direct_memory_promotion_detected": audit.direct_memory_promotion_detected,
    }


def _new_audit_id() -> str:
    return "two_tick_task_working_memory_continuity_audit_" + datetime.now(
        timezone.utc
    ).strftime("%Y%m%d%H%M%S%f")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
