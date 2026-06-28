"""Task-level Working Memory lifecycle records for ASHL Core v1."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar


TASK_WORKING_MEMORY_LIFECYCLE_ENV = "ASHL_CORE_V1_TASK_WORKING_MEMORY_LIFECYCLE_DIR"
DEFAULT_TASK_WORKING_MEMORY_LIFECYCLE_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "task_working_memory_lifecycle"
)

LAST_TASK_WORKING_MEMORY_LIFECYCLE_DEMO_FILE = "last_task_working_memory_lifecycle_demo.json"
TASK_WORKING_MEMORY_LIFECYCLE_DEMO_HISTORY_FILE = (
    "task_working_memory_lifecycle_demo_history.jsonl"
)

WORKING_MEMORY_LAYER = "working"
WORKING_MEMORY_IS_FIVE_LAYER_MEMBER = True
DIRECT_PROMOTION_TO_OTHER_MEMORY_LAYER = False
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
class ActiveTaskFrame:
    """Active task state held inside Working Memory."""

    ALLOWED_STATUSES: ClassVar[set[str]] = {
        "active",
        "suspended",
        "completed",
        "failed",
        "aborted",
    }
    TERMINAL_STATUSES: ClassVar[set[str]] = {"completed", "failed", "aborted"}

    active_task_frame_id: str
    memory_layer: str
    task_id: str
    task_status: str
    current_goal: str
    approved_scope: str
    current_tick: int
    current_step: str | None
    recent_attempt_refs: tuple[str, ...]
    last_outcome_ref: str | None
    last_outcome_label: str | None
    next_candidate_hints: tuple[str, ...]
    blocked_reason: str | None
    continue_allowed: bool
    stop_reason: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.memory_layer != WORKING_MEMORY_LAYER:
            raise ValueError("ActiveTaskFrame memory_layer must be working")
        if not self.active_task_frame_id:
            raise ValueError("active_task_frame_id is required")
        if not self.task_id:
            raise ValueError("task_id is required")
        if self.task_status not in self.ALLOWED_STATUSES:
            raise ValueError(f"unknown task_status: {self.task_status}")
        if not self.current_goal:
            raise ValueError("current_goal is required")
        if not self.approved_scope:
            raise ValueError("approved_scope is required")
        if self.current_tick < 0:
            raise ValueError("current_tick must be non-negative")
        if self.task_status in self.TERMINAL_STATUSES and self.continue_allowed:
            raise ValueError("terminal task_status requires continue_allowed false")
        object.__setattr__(
            self,
            "recent_attempt_refs",
            _tuple_of_str("recent_attempt_refs", self.recent_attempt_refs),
        )
        object.__setattr__(
            self,
            "next_candidate_hints",
            _tuple_of_str("next_candidate_hints", self.next_candidate_hints),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ActiveTaskFrame":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskWorkingMemoryTickUpdate:
    """Record for how one tick changes task Working Memory."""

    task_working_memory_tick_update_id: str
    active_task_frame_id: str
    tick_id: str
    tick_number: int
    before_step: str | None
    after_step: str | None
    observed_outcome_ref: str | None
    observed_outcome_label: str | None
    working_memory_delta: dict[str, object]
    next_candidate_hints_added: tuple[str, ...]
    continue_allowed_after_update: bool
    stop_reason_after_update: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.task_working_memory_tick_update_id:
            raise ValueError("task_working_memory_tick_update_id is required")
        if not self.active_task_frame_id:
            raise ValueError("active_task_frame_id is required")
        if not self.tick_id:
            raise ValueError("tick_id is required")
        if self.tick_number < 0:
            raise ValueError("tick_number must be non-negative")
        object.__setattr__(self, "working_memory_delta", dict(self.working_memory_delta))
        object.__setattr__(
            self,
            "next_candidate_hints_added",
            _tuple_of_str(
                "next_candidate_hints_added",
                self.next_candidate_hints_added,
            ),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TaskWorkingMemoryTickUpdate":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskWorkingMemoryClosureRecord:
    """Closure summary for an active Working Memory task frame."""

    ALLOWED_FINAL_STATUSES: ClassVar[set[str]] = {
        "completed",
        "failed",
        "aborted",
        "suspended",
        "teacher_stopped",
        "system_stopped",
    }

    task_closure_record_id: str
    active_task_frame_id: str
    task_id: str
    final_task_status: str
    final_goal: str
    final_step: str | None
    final_outcome_label: str | None
    stop_reason: str
    tick_count: int
    recent_attempt_refs: tuple[str, ...]
    important_trace_refs: tuple[str, ...]
    closure_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.task_closure_record_id:
            raise ValueError("task_closure_record_id is required")
        if not self.active_task_frame_id:
            raise ValueError("active_task_frame_id is required")
        if not self.task_id:
            raise ValueError("task_id is required")
        if self.final_task_status not in self.ALLOWED_FINAL_STATUSES:
            raise ValueError(f"unknown final_task_status: {self.final_task_status}")
        if not self.final_goal:
            raise ValueError("final_goal is required")
        if not self.stop_reason:
            raise ValueError("stop_reason is required")
        if self.tick_count < 0:
            raise ValueError("tick_count must be non-negative")
        object.__setattr__(
            self,
            "recent_attempt_refs",
            _tuple_of_str("recent_attempt_refs", self.recent_attempt_refs),
        )
        object.__setattr__(
            self,
            "important_trace_refs",
            _tuple_of_str("important_trace_refs", self.important_trace_refs),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TaskWorkingMemoryClosureRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class TaskWorkingMemoryDispositionRecord:
    """Disposition decision for Working Memory content after task closure."""

    task_working_memory_disposition_id: str
    task_closure_record_id: str
    discard_scratch_refs: tuple[str, ...]
    session_summary_refs: tuple[str, ...]
    learning_digest_candidate_refs: tuple[str, ...]
    suspended_task_frame_refs: tuple[str, ...]
    freeze_or_rollback_refs: tuple[str, ...]
    disposition_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.task_working_memory_disposition_id:
            raise ValueError("task_working_memory_disposition_id is required")
        if not self.task_closure_record_id:
            raise ValueError("task_closure_record_id is required")
        for field_name in (
            "discard_scratch_refs",
            "session_summary_refs",
            "learning_digest_candidate_refs",
            "suspended_task_frame_refs",
            "freeze_or_rollback_refs",
            "source_trace_refs",
        ):
            object.__setattr__(
                self,
                field_name,
                _tuple_of_str(field_name, getattr(self, field_name)),
            )
        if _contains_direct_memory_promotion(self.to_dict()):
            raise ValueError("disposition must not directly promote working memory")

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TaskWorkingMemoryDispositionRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class SuspendedTaskFrame:
    """Minimal resumable Working Memory state for a suspended task."""

    suspended_task_frame_id: str
    source_active_task_frame_id: str
    source_task_closure_record_id: str
    task_id: str
    goal: str
    last_safe_step: str | None
    last_outcome_label: str | None
    pause_reason: str
    needed_next: str | None
    resume_hint: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "suspended_task_frame_id",
            "source_active_task_frame_id",
            "source_task_closure_record_id",
            "task_id",
            "goal",
            "pause_reason",
        ):
            if not getattr(self, field_name):
                raise ValueError(f"{field_name} is required")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SuspendedTaskFrame":
        return cls(**dict(data))


def create_active_task_frame(
    current_goal: str,
    approved_scope: str,
    task_id: str | None = None,
    current_step: str | None = None,
    source_trace_refs: tuple[str, ...] = (),
) -> ActiveTaskFrame:
    task_id = task_id or _new_task_id()
    return ActiveTaskFrame(
        active_task_frame_id=_new_active_task_frame_id(),
        memory_layer=WORKING_MEMORY_LAYER,
        task_id=task_id,
        task_status="active",
        current_goal=current_goal,
        approved_scope=approved_scope,
        current_tick=0,
        current_step=current_step,
        recent_attempt_refs=(),
        last_outcome_ref=None,
        last_outcome_label=None,
        next_candidate_hints=(),
        blocked_reason=None,
        continue_allowed=True,
        stop_reason=None,
        source_trace_refs=source_trace_refs,
    )


def apply_task_working_memory_tick_update(
    active_task_frame: ActiveTaskFrame,
    tick_id: str,
    after_step: str | None,
    observed_outcome_ref: str | None,
    observed_outcome_label: str | None,
    working_memory_delta: dict[str, object] | None = None,
    next_candidate_hints_added: tuple[str, ...] = (),
    continue_allowed_after_update: bool = True,
    stop_reason_after_update: str | None = None,
    source_trace_refs: tuple[str, ...] = (),
) -> dict[str, object]:
    delta = dict(working_memory_delta or {})
    if observed_outcome_label is not None:
        delta.setdefault("last_outcome_label", observed_outcome_label)
    if next_candidate_hints_added:
        delta.setdefault("next_candidate_hints_added", list(next_candidate_hints_added))
    update = TaskWorkingMemoryTickUpdate(
        task_working_memory_tick_update_id=_new_tick_update_id(),
        active_task_frame_id=active_task_frame.active_task_frame_id,
        tick_id=tick_id,
        tick_number=active_task_frame.current_tick + 1,
        before_step=active_task_frame.current_step,
        after_step=after_step,
        observed_outcome_ref=observed_outcome_ref,
        observed_outcome_label=observed_outcome_label,
        working_memory_delta=delta,
        next_candidate_hints_added=next_candidate_hints_added,
        continue_allowed_after_update=continue_allowed_after_update,
        stop_reason_after_update=stop_reason_after_update,
        source_trace_refs=(
            *active_task_frame.source_trace_refs,
            *source_trace_refs,
            f"tick:{tick_id}",
        ),
    )
    updated_frame = replace(
        active_task_frame,
        current_tick=update.tick_number,
        current_step=after_step,
        recent_attempt_refs=(
            *active_task_frame.recent_attempt_refs,
            f"tick_update:{update.task_working_memory_tick_update_id}",
        ),
        last_outcome_ref=observed_outcome_ref,
        last_outcome_label=observed_outcome_label,
        next_candidate_hints=(
            *active_task_frame.next_candidate_hints,
            *next_candidate_hints_added,
        ),
        blocked_reason=(
            observed_outcome_label if observed_outcome_label == "blocked" else None
        ),
        continue_allowed=continue_allowed_after_update,
        stop_reason=stop_reason_after_update,
        source_trace_refs=update.source_trace_refs,
    )
    return {
        "tick_update": update,
        "updated_active_task_frame": updated_frame,
    }


def close_task_working_memory(
    active_task_frame: ActiveTaskFrame,
    final_task_status: str,
    stop_reason: str,
    closure_summary: str | None = None,
    important_trace_refs: tuple[str, ...] = (),
) -> TaskWorkingMemoryClosureRecord:
    return TaskWorkingMemoryClosureRecord(
        task_closure_record_id=_new_closure_record_id(),
        active_task_frame_id=active_task_frame.active_task_frame_id,
        task_id=active_task_frame.task_id,
        final_task_status=final_task_status,
        final_goal=active_task_frame.current_goal,
        final_step=active_task_frame.current_step,
        final_outcome_label=active_task_frame.last_outcome_label,
        stop_reason=stop_reason,
        tick_count=active_task_frame.current_tick,
        recent_attempt_refs=active_task_frame.recent_attempt_refs,
        important_trace_refs=important_trace_refs,
        closure_summary=closure_summary
        or f"{active_task_frame.task_id} closed as {final_task_status}: {stop_reason}",
        source_trace_refs=(
            *active_task_frame.source_trace_refs,
            *important_trace_refs,
        ),
    )


def create_task_working_memory_disposition(
    closure_record: TaskWorkingMemoryClosureRecord,
    discard_scratch_refs: tuple[str, ...] = (),
    session_summary_refs: tuple[str, ...] = (),
    learning_digest_candidate_refs: tuple[str, ...] = (),
    suspended_task_frame_refs: tuple[str, ...] = (),
    freeze_or_rollback_refs: tuple[str, ...] = (),
    disposition_summary: str | None = None,
) -> TaskWorkingMemoryDispositionRecord:
    return TaskWorkingMemoryDispositionRecord(
        task_working_memory_disposition_id=_new_disposition_id(),
        task_closure_record_id=closure_record.task_closure_record_id,
        discard_scratch_refs=discard_scratch_refs,
        session_summary_refs=session_summary_refs,
        learning_digest_candidate_refs=learning_digest_candidate_refs,
        suspended_task_frame_refs=suspended_task_frame_refs,
        freeze_or_rollback_refs=freeze_or_rollback_refs,
        disposition_summary=disposition_summary
        or "Working Memory contents were routed by disposition decision.",
        source_trace_refs=(
            *closure_record.source_trace_refs,
            f"task_closure:{closure_record.task_closure_record_id}",
        ),
    )


def create_suspended_task_frame(
    active_task_frame: ActiveTaskFrame,
    closure_record: TaskWorkingMemoryClosureRecord,
    pause_reason: str,
    needed_next: str | None = None,
    resume_hint: str | None = None,
) -> SuspendedTaskFrame:
    return SuspendedTaskFrame(
        suspended_task_frame_id=_new_suspended_task_frame_id(),
        source_active_task_frame_id=active_task_frame.active_task_frame_id,
        source_task_closure_record_id=closure_record.task_closure_record_id,
        task_id=active_task_frame.task_id,
        goal=active_task_frame.current_goal,
        last_safe_step=active_task_frame.current_step,
        last_outcome_label=active_task_frame.last_outcome_label,
        pause_reason=pause_reason,
        needed_next=needed_next,
        resume_hint=resume_hint,
        source_trace_refs=(
            *active_task_frame.source_trace_refs,
            f"task_closure:{closure_record.task_closure_record_id}",
        ),
    )


def build_blocked_task_working_memory_lifecycle_demo() -> dict[str, object]:
    active_frame = create_active_task_frame(
        current_goal="handle front obstacle",
        approved_scope="sandbox_task_working_memory_only",
        task_id="task_front_obstacle_demo",
        current_step="step_forward",
        source_trace_refs=("demo:task_working_memory_lifecycle",),
    )
    update_result = apply_task_working_memory_tick_update(
        active_frame,
        tick_id="tick_001",
        after_step="step_forward",
        observed_outcome_ref="outcome:blocked_front_obstacle",
        observed_outcome_label="blocked",
        working_memory_delta={"last_outcome_label": "blocked"},
        next_candidate_hints_added=("observe_or_adjust",),
        continue_allowed_after_update=False,
        stop_reason_after_update="blocked_front_obstacle",
        source_trace_refs=("second_tick_stub:demo",),
    )
    tick_update = update_result["tick_update"]
    updated_frame = update_result["updated_active_task_frame"]
    assert isinstance(tick_update, TaskWorkingMemoryTickUpdate)
    assert isinstance(updated_frame, ActiveTaskFrame)
    closure = close_task_working_memory(
        updated_frame,
        final_task_status="failed",
        stop_reason="blocked_front_obstacle",
        closure_summary="Front obstacle task stopped after blocked outcome.",
        important_trace_refs=(f"tick_update:{tick_update.task_working_memory_tick_update_id}",),
    )
    learning_candidate_ref = (
        f"learning_digest_candidate:{closure.task_closure_record_id}:blocked_front_obstacle"
    )
    disposition = create_task_working_memory_disposition(
        closure,
        discard_scratch_refs=("scratch:front_obstacle_retry_notes",),
        session_summary_refs=(f"session_summary_candidate:{closure.task_closure_record_id}",),
        learning_digest_candidate_refs=(learning_candidate_ref,),
        disposition_summary=(
            "Discard scratch, keep session summary, and emit a learning digest candidate ref."
        ),
    )
    return {
        "task_working_memory_lifecycle_demo_created": True,
        "active_task_frame": active_frame.to_dict(),
        "updated_active_task_frame": updated_frame.to_dict(),
        "task_working_memory_tick_update": tick_update.to_dict(),
        "task_closure_record": closure.to_dict(),
        "task_working_memory_disposition": disposition.to_dict(),
        "active_task_frame_id": active_frame.active_task_frame_id,
        "task_working_memory_tick_update_id": tick_update.task_working_memory_tick_update_id,
        "task_closure_record_id": closure.task_closure_record_id,
        "task_working_memory_disposition_id": (
            disposition.task_working_memory_disposition_id
        ),
        "memory_layer": WORKING_MEMORY_LAYER,
        "working_memory_is_five_layer_member": WORKING_MEMORY_IS_FIVE_LAYER_MEMBER,
        "direct_promotion_to_other_memory_layer": DIRECT_PROMOTION_TO_OTHER_MEMORY_LAYER,
        "created_at": _now(),
    }


def resolve_task_working_memory_lifecycle_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(TASK_WORKING_MEMORY_LIFECYCLE_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_TASK_WORKING_MEMORY_LIFECYCLE_DIR


def ensure_task_working_memory_lifecycle_store(
    base_dir: str | Path | None = None,
) -> Path:
    lifecycle_dir = resolve_task_working_memory_lifecycle_dir(base_dir)
    lifecycle_dir.mkdir(parents=True, exist_ok=True)
    (lifecycle_dir / TASK_WORKING_MEMORY_LIFECYCLE_DEMO_HISTORY_FILE).touch(
        exist_ok=True
    )
    return lifecycle_dir


def run_task_working_memory_lifecycle_demo(
    base_dir: str | Path | None = None,
) -> dict[str, object]:
    return save_task_working_memory_lifecycle_demo(
        build_blocked_task_working_memory_lifecycle_demo(),
        base_dir,
    )


def save_task_working_memory_lifecycle_demo(
    demo: dict[str, object],
    base_dir: str | Path | None = None,
) -> dict[str, object]:
    lifecycle_dir = ensure_task_working_memory_lifecycle_store(base_dir)
    (lifecycle_dir / LAST_TASK_WORKING_MEMORY_LIFECYCLE_DEMO_FILE).write_text(
        json.dumps(demo, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (lifecycle_dir / TASK_WORKING_MEMORY_LIFECYCLE_DEMO_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(demo, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(demo)


def load_last_task_working_memory_lifecycle_demo(
    base_dir: str | Path | None = None,
) -> dict[str, object] | None:
    path = (
        resolve_task_working_memory_lifecycle_dir(base_dir)
        / LAST_TASK_WORKING_MEMORY_LIFECYCLE_DEMO_FILE
    )
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _contains_direct_memory_promotion(payload: dict[str, object]) -> bool:
    haystack = json.dumps(payload, ensure_ascii=False).lower()
    return any(f"{layer}:" in haystack for layer in FORBIDDEN_DIRECT_MEMORY_LAYERS)


def _new_task_id() -> str:
    return "task_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def _new_active_task_frame_id() -> str:
    return "active_task_frame_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _new_tick_update_id() -> str:
    return "task_working_memory_tick_update_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _new_closure_record_id() -> str:
    return "task_working_memory_closure_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _new_disposition_id() -> str:
    return "task_working_memory_disposition_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _new_suspended_task_frame_id() -> str:
    return "suspended_task_frame_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
