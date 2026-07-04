"""Bounded runtime continuity records with nested event frames."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any


SOURCE_ENGINE = "runtime"
POWER_WINDOW_SCHEMA_VERSION = "runtime_power_window_v0"
TICK_SCHEMA_VERSION = "runtime_tick_v0"
EVENT_FRAME_SCHEMA_VERSION = "runtime_event_frame_v0"
EVENT_STACK_SCHEMA_VERSION = "runtime_event_stack_v0"
EVENT_RETURN_SCHEMA_VERSION = "runtime_event_return_v0"
EVENT_TREE_SCHEMA_VERSION = "runtime_event_tree_v0"
LOOP_TRACE_SCHEMA_VERSION = "runtime_continuous_loop_trace_v0"
LOOP_AUDIT_SCHEMA_VERSION = "runtime_continuous_event_loop_audit_v0"

DEFAULT_MAX_DEPTH = 4
DEFAULT_MAX_FRAME_COUNT = 64
NESTED_DEMO_TIMELINE = ".......1(22222(333(4444)333)222222222)1"

ALLOWED_POWER_STATES = {"power_on", "power_off", "mixed_power_window"}
ALLOWED_WINDOW_KINDS = {
    "bounded_demo_window",
    "bounded_test_window",
    "timeline_parse_window",
}
ALLOWED_WINDOW_STATUSES = {
    "power_window_valid",
    "power_window_blocked_tick_during_power_off",
    "power_window_blocked_unbounded",
    "power_window_blocked_scheduler_detected",
}
ALLOWED_TICK_KINDS = {
    "idle_heartbeat",
    "event_frame_tick",
    "event_return_tick",
    "blocked_tick",
}
ALLOWED_TICK_STATUSES = {
    "tick_recorded",
    "tick_blocked_power_off",
    "tick_blocked_invalid_event_depth",
    "tick_blocked_unbounded_event",
}
ALLOWED_EVENT_STATUSES = {
    "event_opened",
    "event_continued",
    "event_closed_returned",
    "event_blocked_budget_exceeded",
    "event_blocked_invalid_parent",
    "event_blocked_child_scope_expansion",
    "event_blocked_unclosed_at_window_end",
    "event_blocked_forbidden_authority_detected",
}
ALLOWED_RETURN_PAYLOAD_STATUSES = {
    "returned_success",
    "returned_blocked",
    "returned_unknown",
    "returned_deferred",
    "returned_fault",
    "none",
}
ALLOWED_STACK_STATUSES = {
    "stack_valid",
    "stack_empty_idle",
    "stack_blocked_max_depth_exceeded",
    "stack_blocked_invalid_parent_child_order",
    "stack_blocked_unclosed_frame",
}
ALLOWED_RETURN_STATUSES = {
    "returned_success",
    "returned_blocked",
    "returned_unknown",
    "returned_deferred",
    "returned_fault",
    "blocked_invalid_parent_return",
    "blocked_scope_mutation_detected",
    "blocked_forbidden_authority_detected",
}
ALLOWED_TREE_STATUSES = {
    "tree_valid_all_frames_closed",
    "tree_valid_with_blocked_unclosed_frames",
    "tree_blocked_invalid_parent_child_link",
    "tree_blocked_missing_return",
    "tree_blocked_unbounded_growth",
}
ALLOWED_LOOP_TRACE_STATUSES = {
    "loop_trace_valid",
    "loop_trace_valid_with_power_off_gaps",
    "loop_trace_blocked_power_off_tick",
    "loop_trace_blocked_unclosed_event",
    "loop_trace_blocked_unbounded",
    "loop_trace_blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_continuous_event_loop_nested_frame_demo",
    "passed_idle_only_loop_demo",
    "passed_power_off_gap_respected",
    "blocked_power_off_tick_detected",
    "blocked_invalid_event_stack",
    "blocked_unclosed_event_frame",
    "blocked_unbounded_loop",
    "blocked_autonomous_scheduler_detected",
    "blocked_open_ended_loop_detected",
    "blocked_external_execution_detected",
    "blocked_memory_write_detected",
    "blocked_automatic_learning_approval_detected",
    "blocked_recursive_learning_detected",
    "blocked_production_behavior_detected",
}

SAFE_CLAIM = (
    "ASHL Core v1 can represent a bounded runtime continuity window with "
    "power-off gaps, idle heartbeat ticks, nested EventFrames, EventStack "
    "snapshots, child-event returns, event tree traces, and safety audits."
)
BLOCKED_CLAIMS = (
    "no_live_continuous_runtime_session",
    "no_autonomous_scheduler",
    "no_open_ended_loop",
    "no_free_event_creation",
    "no_external_execution",
    "no_recursive_learning",
    "no_memory_layer_write",
    "no_thought_engine_cognition",
    "not_awake",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plain(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def _tuple_of_str(name: str, value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    items = tuple(value)
    if not all(isinstance(item, str) for item in items):
        raise TypeError(f"{name} must contain only strings")
    return items


def _slug(text: str) -> str:
    safe = []
    for char in text:
        if char.isalnum():
            safe.append(char.lower())
        elif char == ".":
            safe.append("dot")
        elif char == " ":
            safe.append("off")
        elif char.isdigit():
            safe.append(char)
        else:
            safe.append("_")
    value = "_".join("".join(safe).split("_"))[:80]
    return value or "empty"


def normalize_runtime_timeline_text(timeline_text: str) -> str:
    """Remove human nesting markers while preserving runtime symbols."""

    return "".join(char for char in timeline_text if char not in "()")


def parse_runtime_timeline_symbols(
    timeline_text: str,
    *,
    max_depth: int = DEFAULT_MAX_DEPTH,
    unbounded: bool = False,
) -> tuple[str, ...]:
    """Parse and validate runtime timeline symbols.

    Parentheses are visual notation only. Spaces are preserved as power-off
    gaps, dots are idle heartbeats, and digits define event depth.
    """

    if unbounded or "while true" in timeline_text.lower():
        raise ValueError("unbounded_loop_requested")
    symbols = _parse_runtime_timeline_symbols_for_recording(timeline_text)
    active_depth = 0
    for symbol in symbols:
        if symbol == " ":
            active_depth = 0
            continue
        if symbol == ".":
            active_depth = 0
            continue
        if symbol.isdigit():
            depth = int(symbol)
            if depth > max_depth:
                raise ValueError("max_depth_exceeded")
            if active_depth == 0 and depth != 1:
                raise ValueError("event_depth_started_without_parent")
            if depth > active_depth + 1:
                raise ValueError("event_depth_jump_without_parent")
            active_depth = depth
    return symbols


def _parse_runtime_timeline_symbols_for_recording(
    timeline_text: str,
) -> tuple[str, ...]:
    if "while true" in timeline_text.lower():
        return tuple()
    normalized = normalize_runtime_timeline_text(timeline_text)
    symbols: list[str] = []
    for char in normalized:
        if char == " " or char == "." or char.isdigit():
            if char.isdigit() and char == "0":
                raise ValueError("invalid_event_depth:0")
            symbols.append(char)
            continue
        raise ValueError(f"invalid_timeline_symbol:{char}")
    return tuple(symbols)


@dataclass(frozen=True)
class RuntimePowerWindowRecord:
    power_window_id: str
    schema_version: str
    created_at: str
    source_engine: str
    power_state: str
    window_kind: str
    timeline_text: str
    parsed_timeline_symbols: tuple[str, ...]
    power_on_ticks_allowed: int
    power_on_ticks_created: int
    power_off_spans_observed: int
    tick_created_during_power_off: bool
    window_status: str
    window_summary: str
    autonomous_scheduler_created: bool
    open_ended_loop_created: bool
    background_daemon_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != POWER_WINDOW_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_power_window_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.power_state not in ALLOWED_POWER_STATES:
            raise ValueError(f"unknown power_state: {self.power_state}")
        if self.window_kind not in ALLOWED_WINDOW_KINDS:
            raise ValueError(f"unknown window_kind: {self.window_kind}")
        if self.window_status not in ALLOWED_WINDOW_STATUSES:
            raise ValueError(f"unknown window_status: {self.window_status}")
        for name in ("parsed_timeline_symbols", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimePowerWindowRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeTickRecord:
    runtime_tick_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_power_window_id: str
    tick_index: int
    tick_symbol: str
    power_state: str
    tick_kind: str
    active_event_frame_id: str | None
    active_event_depth: int
    event_stack_snapshot: tuple[str, ...]
    tick_status: str
    tick_summary: str
    state_snapshot_ref: str | None
    session_summary_ref: str | None
    last_trace_summary_ref: str | None
    created_event_frame: bool
    closed_event_frame: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    external_execution_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != TICK_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_tick_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.power_state not in {"power_on", "power_off"}:
            raise ValueError(f"unknown tick power_state: {self.power_state}")
        if self.tick_kind not in ALLOWED_TICK_KINDS:
            raise ValueError(f"unknown tick_kind: {self.tick_kind}")
        if self.tick_status not in ALLOWED_TICK_STATUSES:
            raise ValueError(f"unknown tick_status: {self.tick_status}")
        for name in ("event_stack_snapshot", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeTickRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeEventFrameRecord:
    event_frame_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_power_window_id: str
    event_type: str
    event_label: str
    event_depth: int
    parent_event_frame_id: str | None
    child_event_frame_ids: tuple[str, ...]
    opened_at_tick_index: int
    closed_at_tick_index: int | None
    event_scope: str
    event_budget_ticks: int
    event_ticks_used: int
    event_status: str
    event_summary: str
    return_payload_id: str | None
    return_payload_status: str | None
    child_scope_expansion_detected: bool
    budget_exceeded: bool
    unclosed_frame_detected: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    free_action_selection_created: bool
    external_execution_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVENT_FRAME_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_event_frame_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.event_status not in ALLOWED_EVENT_STATUSES:
            raise ValueError(f"unknown event_status: {self.event_status}")
        if self.return_payload_status not in ALLOWED_RETURN_PAYLOAD_STATUSES:
            raise ValueError(
                f"unknown return_payload_status: {self.return_payload_status}"
            )
        for name in ("child_event_frame_ids", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeEventFrameRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeEventStackRecord:
    event_stack_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_power_window_id: str
    tick_index: int
    stack_frame_ids: tuple[str, ...]
    stack_depth: int
    top_event_frame_id: str | None
    stack_status: str
    stack_summary: str
    max_depth_allowed: int
    max_depth_observed: int
    stack_overflow_detected: bool
    invalid_parent_child_order_detected: bool
    unclosed_frame_detected: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVENT_STACK_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_event_stack_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.stack_status not in ALLOWED_STACK_STATUSES:
            raise ValueError(f"unknown stack_status: {self.stack_status}")
        for name in ("stack_frame_ids", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeEventStackRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeEventReturnRecord:
    event_return_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_event_frame_id: str
    parent_event_frame_id: str | None
    return_tick_index: int
    return_status: str
    return_reason: str
    return_summary: str
    return_payload: dict[str, object]
    parent_resumed: bool
    parent_resume_tick_index: int | None
    return_scope_changed_parent: bool
    return_created_new_event_without_parent: bool
    memory_write_performed: bool
    automatic_learning_approval_created: bool
    external_execution_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVENT_RETURN_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_event_return_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.return_status not in ALLOWED_RETURN_STATUSES:
            raise ValueError(f"unknown return_status: {self.return_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeEventReturnRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeEventTreeRecord:
    event_tree_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_power_window_id: str
    root_event_frame_ids: tuple[str, ...]
    all_event_frame_ids: tuple[str, ...]
    event_return_ids: tuple[str, ...]
    tree_depth_max: int
    tree_frame_count: int
    tree_closed_frame_count: int
    tree_unclosed_frame_count: int
    tree_status: str
    tree_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EVENT_TREE_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_event_tree_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.tree_status not in ALLOWED_TREE_STATUSES:
            raise ValueError(f"unknown tree_status: {self.tree_status}")
        for name in ("root_event_frame_ids", "all_event_frame_ids", "event_return_ids", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeEventTreeRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeContinuousLoopTrace:
    continuous_loop_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_power_window_id: str
    timeline_text: str
    normalized_timeline_text: str
    tick_ids: tuple[str, ...]
    event_frame_ids: tuple[str, ...]
    event_stack_ids: tuple[str, ...]
    event_return_ids: tuple[str, ...]
    event_tree_id: str | None
    idle_tick_count: int
    event_tick_count: int
    power_off_span_count: int
    max_event_depth_observed: int
    loop_trace_status: str
    loop_trace_summary: str
    continuous_loop_interrupted: bool
    power_off_processed_as_tick: bool
    unbounded_loop_detected: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != LOOP_TRACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_continuous_loop_trace_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.loop_trace_status not in ALLOWED_LOOP_TRACE_STATUSES:
            raise ValueError(f"unknown loop_trace_status: {self.loop_trace_status}")
        for name in ("tick_ids", "event_frame_ids", "event_stack_ids", "event_return_ids", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeContinuousLoopTrace":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeContinuousLoopAudit:
    continuous_loop_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_continuous_loop_trace_id: str
    source_event_tree_id: str | None
    power_off_gaps_respected: bool
    idle_ticks_valid: bool
    event_frames_valid: bool
    event_stack_valid: bool
    event_returns_valid: bool
    event_tree_valid: bool
    nested_event_return_verified: bool
    parent_resume_verified: bool
    bounded_window_verified: bool
    no_autonomous_scheduler: bool
    no_open_ended_loop: bool
    no_background_daemon: bool
    no_free_action_selection: bool
    no_external_execution: bool
    no_unity_execution: bool
    no_bridge_execution: bool
    no_memory_layer_write: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_automatic_learning_approval: bool
    no_recursive_learning: bool
    no_production_behavior: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != LOOP_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_continuous_event_loop_audit_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeContinuousLoopAudit":
        return cls(**dict(data))


def build_runtime_power_window_record(
    *,
    timeline_text: str,
    window_kind: str = "bounded_demo_window",
    tick_created_during_power_off: bool = False,
    unbounded: bool = False,
    autonomous_scheduler_created: bool = False,
    open_ended_loop_created: bool = False,
    background_daemon_created: bool = False,
    created_at: str | None = None,
    source_trace_refs: tuple[str, ...] = ("runtime_continuous_event_loop_demo",),
) -> RuntimePowerWindowRecord:
    normalized = normalize_runtime_timeline_text(timeline_text)
    unbounded_requested = unbounded or "while true" in timeline_text.lower()
    symbols = (
        tuple()
        if unbounded_requested
        else _parse_runtime_timeline_symbols_for_recording(timeline_text)
    )
    power_off_count = sum(1 for symbol in symbols if symbol == " ")
    tick_count = sum(1 for symbol in symbols if symbol != " ")
    if tick_count and power_off_count:
        power_state = "mixed_power_window"
    elif tick_count:
        power_state = "power_on"
    else:
        power_state = "power_off"
    if unbounded_requested or open_ended_loop_created:
        status = "power_window_blocked_unbounded"
    elif autonomous_scheduler_created or background_daemon_created:
        status = "power_window_blocked_scheduler_detected"
    elif tick_created_during_power_off:
        status = "power_window_blocked_tick_during_power_off"
    else:
        status = "power_window_valid"
    return RuntimePowerWindowRecord(
        power_window_id=f"runtime_power_window:{_slug(normalized)}",
        schema_version=POWER_WINDOW_SCHEMA_VERSION,
        created_at=created_at or _now(),
        source_engine=SOURCE_ENGINE,
        power_state=power_state,
        window_kind=window_kind,
        timeline_text=timeline_text,
        parsed_timeline_symbols=symbols,
        power_on_ticks_allowed=tick_count,
        power_on_ticks_created=tick_count + (1 if tick_created_during_power_off else 0),
        power_off_spans_observed=power_off_count,
        tick_created_during_power_off=tick_created_during_power_off,
        window_status=status,
        window_summary=_power_window_summary(status, tick_count, power_off_count),
        autonomous_scheduler_created=autonomous_scheduler_created,
        open_ended_loop_created=open_ended_loop_created,
        background_daemon_created=background_daemon_created,
        source_trace_refs=source_trace_refs,
    )


def validate_runtime_power_window_record(
    power_window: RuntimePowerWindowRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _power_window(power_window)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_power_window:{error}",)}
    errors: list[str] = []
    if record.window_status == "power_window_valid":
        if record.tick_created_during_power_off:
            errors.append("tick_created_during_power_off")
        if record.autonomous_scheduler_created:
            errors.append("autonomous_scheduler_created")
        if record.open_ended_loop_created:
            errors.append("open_ended_loop_created")
        if record.background_daemon_created:
            errors.append("background_daemon_created")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "power_window_id": record.power_window_id,
        "window_status": record.window_status,
    }


def build_runtime_tick_records_from_timeline(
    *,
    power_window: RuntimePowerWindowRecord | dict[str, object],
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> tuple[RuntimeTickRecord, ...]:
    window = _power_window(power_window)
    analysis = _analyze_timeline(window, max_depth=max_depth)
    records: list[RuntimeTickRecord] = []
    for tick in analysis["ticks"]:
        stack_snapshot = tuple(tick["stack"])
        symbol = str(tick["symbol"])
        invalid_depth = bool(tick.get("invalid_depth"))
        power_off_tick = bool(tick.get("power_off_tick"))
        if power_off_tick:
            tick_kind = "blocked_tick"
            tick_status = "tick_blocked_power_off"
        elif invalid_depth:
            tick_kind = "blocked_tick"
            tick_status = "tick_blocked_invalid_event_depth"
        elif window.window_status == "power_window_blocked_unbounded":
            tick_kind = "blocked_tick"
            tick_status = "tick_blocked_unbounded_event"
        elif symbol == ".":
            tick_kind = "idle_heartbeat"
            tick_status = "tick_recorded"
        elif bool(tick.get("closed")):
            tick_kind = "event_return_tick"
            tick_status = "tick_recorded"
        else:
            tick_kind = "event_frame_tick"
            tick_status = "tick_recorded"
        active_depth = int(tick.get("depth", len(stack_snapshot)))
        records.append(
            RuntimeTickRecord(
                runtime_tick_id=f"runtime_tick:{window.power_window_id}:{tick['index']}",
                schema_version=TICK_SCHEMA_VERSION,
                created_at=window.created_at,
                source_engine=SOURCE_ENGINE,
                source_power_window_id=window.power_window_id,
                tick_index=int(tick["index"]),
                tick_symbol=symbol,
                power_state="power_off" if power_off_tick else "power_on",
                tick_kind=tick_kind,
                active_event_frame_id=stack_snapshot[-1] if stack_snapshot else None,
                active_event_depth=active_depth,
                event_stack_snapshot=stack_snapshot,
                tick_status=tick_status,
                tick_summary=_tick_summary(tick_kind, tick_status, symbol),
                state_snapshot_ref=None,
                session_summary_ref=None,
                last_trace_summary_ref=None,
                created_event_frame=bool(tick.get("created")),
                closed_event_frame=bool(tick.get("closed")),
                memory_write_performed=False,
                automatic_learning_approval_created=False,
                external_execution_created=False,
                source_trace_refs=window.source_trace_refs,
            )
        )
    return tuple(records)


def validate_runtime_tick_record(
    tick: RuntimeTickRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _tick(tick)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_tick:{error}",)}
    errors: list[str] = []
    if record.power_state == "power_off" and record.tick_status != "tick_blocked_power_off":
        errors.append("power_off_tick_not_blocked")
    for flag in (
        "memory_write_performed",
        "automatic_learning_approval_created",
        "external_execution_created",
    ):
        if getattr(record, flag) is not False:
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "runtime_tick_id": record.runtime_tick_id,
        "tick_status": record.tick_status,
    }


def build_runtime_event_frames_from_timeline(
    *,
    power_window: RuntimePowerWindowRecord | dict[str, object],
    max_depth: int = DEFAULT_MAX_DEPTH,
    event_budget_ticks: int = 64,
    leave_unclosed_at_end: bool = False,
    force_budget_exceeded: bool = False,
    force_child_scope_expansion: bool = False,
    force_forbidden_authority: bool = False,
) -> tuple[RuntimeEventFrameRecord, ...]:
    window = _power_window(power_window)
    analysis = _analyze_timeline(
        window,
        max_depth=max_depth,
        event_budget_ticks=event_budget_ticks,
        leave_unclosed_at_end=leave_unclosed_at_end,
        force_budget_exceeded=force_budget_exceeded,
        force_child_scope_expansion=force_child_scope_expansion,
        force_forbidden_authority=force_forbidden_authority,
    )
    return tuple(analysis["frames"])


def validate_runtime_event_frame_record(
    event_frame: RuntimeEventFrameRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _event_frame(event_frame)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_event_frame:{error}",)}
    errors: list[str] = []
    if record.event_depth == 1 and record.parent_event_frame_id is not None:
        errors.append("root_frame_has_parent")
    if record.event_depth > 1 and record.parent_event_frame_id is None:
        errors.append("child_frame_missing_parent")
    if record.event_ticks_used > record.event_budget_ticks and not record.budget_exceeded:
        errors.append("budget_exceeded_not_marked")
    for flag in (
        "memory_write_performed",
        "automatic_learning_approval_created",
        "free_action_selection_created",
        "external_execution_created",
        "production_behavior_created",
    ):
        if getattr(record, flag) and record.event_status != "event_blocked_forbidden_authority_detected":
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "event_frame_id": record.event_frame_id,
        "event_status": record.event_status,
    }


def build_runtime_event_stack_records(
    *,
    power_window: RuntimePowerWindowRecord | dict[str, object],
    max_depth: int = DEFAULT_MAX_DEPTH,
    invalid_parent_child_order_detected: bool = False,
    unclosed_frame_detected: bool = False,
) -> tuple[RuntimeEventStackRecord, ...]:
    window = _power_window(power_window)
    analysis = _analyze_timeline(window, max_depth=max_depth)
    records: list[RuntimeEventStackRecord] = []
    for tick in analysis["ticks"]:
        stack = tuple(tick["stack"])
        overflow = len(stack) > max_depth or bool(tick.get("max_depth_exceeded"))
        invalid_order = invalid_parent_child_order_detected or bool(
            tick.get("invalid_depth")
        )
        if overflow:
            status = "stack_blocked_max_depth_exceeded"
        elif invalid_order:
            status = "stack_blocked_invalid_parent_child_order"
        elif unclosed_frame_detected:
            status = "stack_blocked_unclosed_frame"
        elif not stack:
            status = "stack_empty_idle"
        else:
            status = "stack_valid"
        records.append(
            RuntimeEventStackRecord(
                event_stack_id=f"runtime_event_stack:{window.power_window_id}:{tick['index']}",
                schema_version=EVENT_STACK_SCHEMA_VERSION,
                created_at=window.created_at,
                source_engine=SOURCE_ENGINE,
                source_power_window_id=window.power_window_id,
                tick_index=int(tick["index"]),
                stack_frame_ids=stack,
                stack_depth=len(stack),
                top_event_frame_id=stack[-1] if stack else None,
                stack_status=status,
                stack_summary=_stack_summary(status, len(stack)),
                max_depth_allowed=max_depth,
                max_depth_observed=max(len(stack), int(tick.get("depth", 0))),
                stack_overflow_detected=overflow,
                invalid_parent_child_order_detected=invalid_order,
                unclosed_frame_detected=unclosed_frame_detected,
                source_trace_refs=window.source_trace_refs,
            )
        )
    return tuple(records)


def validate_runtime_event_stack_record(
    event_stack: RuntimeEventStackRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _event_stack(event_stack)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_event_stack:{error}",)}
    errors: list[str] = []
    if record.stack_depth != len(record.stack_frame_ids):
        errors.append("stack_depth_mismatch")
    if record.stack_depth and record.top_event_frame_id != record.stack_frame_ids[-1]:
        errors.append("top_frame_mismatch")
    if record.stack_depth > record.max_depth_allowed and not record.stack_overflow_detected:
        errors.append("stack_overflow_not_marked")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "event_stack_id": record.event_stack_id,
        "stack_status": record.stack_status,
    }


def build_runtime_event_return_records(
    *,
    power_window: RuntimePowerWindowRecord | dict[str, object],
    max_depth: int = DEFAULT_MAX_DEPTH,
    return_scope_changed_parent: bool = False,
    return_created_new_event_without_parent: bool = False,
    force_forbidden_authority: bool = False,
) -> tuple[RuntimeEventReturnRecord, ...]:
    window = _power_window(power_window)
    analysis = _analyze_timeline(
        window,
        max_depth=max_depth,
        return_scope_changed_parent=return_scope_changed_parent,
        return_created_new_event_without_parent=return_created_new_event_without_parent,
        force_return_forbidden_authority=force_forbidden_authority,
    )
    return tuple(analysis["returns"])


def validate_runtime_event_return_record(
    event_return: RuntimeEventReturnRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _event_return(event_return)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_event_return:{error}",)}
    errors: list[str] = []
    if record.return_scope_changed_parent and record.return_status != "blocked_scope_mutation_detected":
        errors.append("scope_mutation_not_blocked")
    for flag in (
        "memory_write_performed",
        "automatic_learning_approval_created",
        "external_execution_created",
    ):
        if getattr(record, flag) and record.return_status != "blocked_forbidden_authority_detected":
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "event_return_id": record.event_return_id,
        "return_status": record.return_status,
    }


def build_runtime_event_tree_record(
    *,
    power_window: RuntimePowerWindowRecord | dict[str, object],
    event_frames: tuple[RuntimeEventFrameRecord, ...] | list[RuntimeEventFrameRecord | dict[str, object]],
    event_returns: tuple[RuntimeEventReturnRecord, ...] | list[RuntimeEventReturnRecord | dict[str, object]],
    max_frame_count: int = DEFAULT_MAX_FRAME_COUNT,
    force_missing_return: bool = False,
    force_unbounded_growth: bool = False,
    created_at: str | None = None,
) -> RuntimeEventTreeRecord:
    window = _power_window(power_window)
    frames = tuple(_event_frame(frame) for frame in event_frames)
    returns = tuple(_event_return(item) for item in event_returns)
    return_frame_ids = {item.source_event_frame_id for item in returns}
    roots = tuple(frame.event_frame_id for frame in frames if frame.parent_event_frame_id is None)
    all_ids = tuple(frame.event_frame_id for frame in frames)
    child_map = {frame.event_frame_id: frame.child_event_frame_ids for frame in frames}
    reachable = set()

    def visit(frame_id: str) -> None:
        if frame_id in reachable:
            return
        reachable.add(frame_id)
        for child_id in child_map.get(frame_id, ()):
            visit(child_id)

    for root in roots:
        visit(root)
    invalid_link = bool(set(all_ids) - reachable)
    closed = tuple(
        frame for frame in frames if frame.event_status == "event_closed_returned"
    )
    missing_return = force_missing_return or any(
        frame.parent_event_frame_id is not None and frame.event_frame_id not in return_frame_ids
        for frame in closed
    )
    unclosed = tuple(frame for frame in frames if frame.unclosed_frame_detected)
    if force_unbounded_growth or len(frames) > max_frame_count:
        status = "tree_blocked_unbounded_growth"
    elif invalid_link:
        status = "tree_blocked_invalid_parent_child_link"
    elif missing_return:
        status = "tree_blocked_missing_return"
    elif unclosed:
        status = "tree_valid_with_blocked_unclosed_frames"
    else:
        status = "tree_valid_all_frames_closed"
    return RuntimeEventTreeRecord(
        event_tree_id=f"runtime_event_tree:{window.power_window_id}",
        schema_version=EVENT_TREE_SCHEMA_VERSION,
        created_at=created_at or window.created_at,
        source_engine=SOURCE_ENGINE,
        source_power_window_id=window.power_window_id,
        root_event_frame_ids=roots,
        all_event_frame_ids=all_ids,
        event_return_ids=tuple(item.event_return_id for item in returns),
        tree_depth_max=max((frame.event_depth for frame in frames), default=0),
        tree_frame_count=len(frames),
        tree_closed_frame_count=len(closed),
        tree_unclosed_frame_count=len(unclosed),
        tree_status=status,
        tree_summary=_tree_summary(status, len(frames)),
        source_trace_refs=window.source_trace_refs,
    )


def validate_runtime_event_tree_record(
    event_tree: RuntimeEventTreeRecord | dict[str, object],
) -> dict[str, object]:
    try:
        record = _event_tree(event_tree)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_event_tree:{error}",)}
    errors: list[str] = []
    if record.tree_frame_count != len(record.all_event_frame_ids):
        errors.append("tree_frame_count_mismatch")
    if record.tree_unclosed_frame_count and record.tree_status == "tree_valid_all_frames_closed":
        errors.append("unclosed_count_with_all_closed_status")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "event_tree_id": record.event_tree_id,
        "tree_status": record.tree_status,
    }


def build_runtime_continuous_loop_trace(
    *,
    power_window: RuntimePowerWindowRecord | dict[str, object],
    ticks: tuple[RuntimeTickRecord, ...] | list[RuntimeTickRecord | dict[str, object]],
    event_frames: tuple[RuntimeEventFrameRecord, ...] | list[RuntimeEventFrameRecord | dict[str, object]],
    event_stacks: tuple[RuntimeEventStackRecord, ...] | list[RuntimeEventStackRecord | dict[str, object]],
    event_returns: tuple[RuntimeEventReturnRecord, ...] | list[RuntimeEventReturnRecord | dict[str, object]],
    event_tree: RuntimeEventTreeRecord | dict[str, object] | None,
    forbidden_authority_detected: bool = False,
    created_at: str | None = None,
) -> RuntimeContinuousLoopTrace:
    window = _power_window(power_window)
    tick_records = tuple(_tick(item) for item in ticks)
    frame_records = tuple(_event_frame(item) for item in event_frames)
    stack_records = tuple(_event_stack(item) for item in event_stacks)
    return_records = tuple(_event_return(item) for item in event_returns)
    tree = _event_tree(event_tree) if event_tree is not None else None
    idle_count = sum(1 for tick in tick_records if tick.tick_kind == "idle_heartbeat")
    event_count = sum(
        1
        for tick in tick_records
        if tick.tick_kind in {"event_frame_tick", "event_return_tick"}
    )
    unclosed = any(frame.unclosed_frame_detected for frame in frame_records)
    unbounded = window.window_status == "power_window_blocked_unbounded"
    power_off_tick = window.tick_created_during_power_off or any(
        tick.power_state == "power_off" for tick in tick_records
    )
    if power_off_tick:
        status = "loop_trace_blocked_power_off_tick"
    elif unbounded:
        status = "loop_trace_blocked_unbounded"
    elif forbidden_authority_detected:
        status = "loop_trace_blocked_forbidden_authority_detected"
    elif unclosed:
        status = "loop_trace_blocked_unclosed_event"
    elif window.power_off_spans_observed:
        status = "loop_trace_valid_with_power_off_gaps"
    else:
        status = "loop_trace_valid"
    return RuntimeContinuousLoopTrace(
        continuous_loop_trace_id=f"runtime_continuous_loop_trace:{window.power_window_id}",
        schema_version=LOOP_TRACE_SCHEMA_VERSION,
        created_at=created_at or window.created_at,
        source_engine=SOURCE_ENGINE,
        source_power_window_id=window.power_window_id,
        timeline_text=window.timeline_text,
        normalized_timeline_text=normalize_runtime_timeline_text(window.timeline_text),
        tick_ids=tuple(tick.runtime_tick_id for tick in tick_records),
        event_frame_ids=tuple(frame.event_frame_id for frame in frame_records),
        event_stack_ids=tuple(stack.event_stack_id for stack in stack_records),
        event_return_ids=tuple(item.event_return_id for item in return_records),
        event_tree_id=tree.event_tree_id if tree else None,
        idle_tick_count=idle_count,
        event_tick_count=event_count,
        power_off_span_count=window.power_off_spans_observed,
        max_event_depth_observed=max(
            (stack.max_depth_observed for stack in stack_records),
            default=0,
        ),
        loop_trace_status=status,
        loop_trace_summary=_loop_trace_summary(status),
        continuous_loop_interrupted=False,
        power_off_processed_as_tick=power_off_tick,
        unbounded_loop_detected=unbounded,
        source_trace_refs=window.source_trace_refs,
    )


def validate_runtime_continuous_loop_trace(
    loop_trace: RuntimeContinuousLoopTrace | dict[str, object],
) -> dict[str, object]:
    try:
        record = _loop_trace(loop_trace)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_loop_trace:{error}",)}
    errors: list[str] = []
    if record.continuous_loop_interrupted:
        errors.append("continuous_loop_interrupted")
    if record.power_off_processed_as_tick and record.loop_trace_status != "loop_trace_blocked_power_off_tick":
        errors.append("power_off_tick_not_blocked")
    if record.unbounded_loop_detected and record.loop_trace_status != "loop_trace_blocked_unbounded":
        errors.append("unbounded_loop_not_blocked")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "continuous_loop_trace_id": record.continuous_loop_trace_id,
        "loop_trace_status": record.loop_trace_status,
    }


def build_runtime_continuous_loop_audit(
    *,
    loop_trace: RuntimeContinuousLoopTrace | dict[str, object],
    event_tree: RuntimeEventTreeRecord | dict[str, object] | None,
    ticks: tuple[RuntimeTickRecord, ...] | list[RuntimeTickRecord | dict[str, object]] = (),
    event_frames: tuple[RuntimeEventFrameRecord, ...] | list[RuntimeEventFrameRecord | dict[str, object]] = (),
    event_stacks: tuple[RuntimeEventStackRecord, ...] | list[RuntimeEventStackRecord | dict[str, object]] = (),
    event_returns: tuple[RuntimeEventReturnRecord, ...] | list[RuntimeEventReturnRecord | dict[str, object]] = (),
    autonomous_scheduler_created: bool = False,
    open_ended_loop_created: bool = False,
    background_daemon_created: bool = False,
    free_action_selection_created: bool = False,
    external_execution_created: bool = False,
    unity_execution_created: bool = False,
    bridge_execution_created: bool = False,
    memory_layer_write_performed: bool = False,
    core_memory_write_performed: bool = False,
    long_term_memory_write_performed: bool = False,
    archive_memory_write_performed: bool = False,
    anchor_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    recursive_learning_created: bool = False,
    production_behavior_created: bool = False,
    created_at: str | None = None,
) -> RuntimeContinuousLoopAudit:
    trace = _loop_trace(loop_trace)
    tree = _event_tree(event_tree) if event_tree is not None else None
    tick_records = tuple(_tick(item) for item in ticks)
    frame_records = tuple(_event_frame(item) for item in event_frames)
    stack_records = tuple(_event_stack(item) for item in event_stacks)
    return_records = tuple(_event_return(item) for item in event_returns)
    power_off_ok = not trace.power_off_processed_as_tick
    idle_ok = all(validate_runtime_tick_record(tick)["valid"] for tick in tick_records)
    frames_ok = all(
        frame.event_status
        not in {
            "event_blocked_budget_exceeded",
            "event_blocked_invalid_parent",
            "event_blocked_child_scope_expansion",
            "event_blocked_unclosed_at_window_end",
            "event_blocked_forbidden_authority_detected",
        }
        for frame in frame_records
    )
    stacks_ok = all(stack.stack_status in {"stack_valid", "stack_empty_idle"} for stack in stack_records)
    returns_ok = all(item.return_status == "returned_success" for item in return_records)
    tree_ok = tree is None or tree.tree_status == "tree_valid_all_frames_closed"
    no_memory = not (
        memory_layer_write_performed
        or core_memory_write_performed
        or long_term_memory_write_performed
        or archive_memory_write_performed
        or anchor_write_performed
    )
    no_external = not (
        external_execution_created or unity_execution_created or bridge_execution_created
    )
    blocked_reasons: list[str] = []
    if not power_off_ok:
        blocked_reasons.append("power_off_tick_detected")
    if not stacks_ok:
        blocked_reasons.append("invalid_event_stack")
    if any(frame.unclosed_frame_detected for frame in frame_records):
        blocked_reasons.append("unclosed_event_frame")
    if trace.unbounded_loop_detected:
        blocked_reasons.append("unbounded_loop")
    if autonomous_scheduler_created:
        blocked_reasons.append("autonomous_scheduler_detected")
    if open_ended_loop_created:
        blocked_reasons.append("open_ended_loop_detected")
    if not no_external:
        blocked_reasons.append("external_execution_detected")
    if not no_memory:
        blocked_reasons.append("memory_write_detected")
    if automatic_learning_approval_created:
        blocked_reasons.append("automatic_learning_approval_detected")
    if recursive_learning_created:
        blocked_reasons.append("recursive_learning_detected")
    if production_behavior_created:
        blocked_reasons.append("production_behavior_detected")
    status = _audit_status(
        blocked_reasons=blocked_reasons,
        trace=trace,
    )
    return RuntimeContinuousLoopAudit(
        continuous_loop_audit_id=f"runtime_continuous_loop_audit:{trace.continuous_loop_trace_id}",
        schema_version=LOOP_AUDIT_SCHEMA_VERSION,
        created_at=created_at or trace.created_at,
        source_engine=SOURCE_ENGINE,
        source_continuous_loop_trace_id=trace.continuous_loop_trace_id,
        source_event_tree_id=tree.event_tree_id if tree else None,
        power_off_gaps_respected=power_off_ok,
        idle_ticks_valid=idle_ok,
        event_frames_valid=frames_ok,
        event_stack_valid=stacks_ok,
        event_returns_valid=returns_ok,
        event_tree_valid=tree_ok,
        nested_event_return_verified=bool(return_records) and returns_ok,
        parent_resume_verified=all(
            item.parent_resumed or item.parent_event_frame_id is None
            for item in return_records
        ),
        bounded_window_verified=not trace.unbounded_loop_detected,
        no_autonomous_scheduler=not autonomous_scheduler_created,
        no_open_ended_loop=not open_ended_loop_created,
        no_background_daemon=not background_daemon_created,
        no_free_action_selection=not free_action_selection_created,
        no_external_execution=not external_execution_created,
        no_unity_execution=not unity_execution_created,
        no_bridge_execution=not bridge_execution_created,
        no_memory_layer_write=not memory_layer_write_performed,
        no_core_memory_write=not core_memory_write_performed,
        no_long_term_memory_write=not long_term_memory_write_performed,
        no_archive_memory_write=not archive_memory_write_performed,
        no_anchor_write=not anchor_write_performed,
        no_automatic_learning_approval=not automatic_learning_approval_created,
        no_recursive_learning=not recursive_learning_created,
        no_production_behavior=not production_behavior_created,
        audit_status=status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(blocked_reasons),
        source_trace_refs=trace.source_trace_refs,
    )


def validate_runtime_continuous_loop_audit(
    loop_audit: RuntimeContinuousLoopAudit | dict[str, object],
) -> dict[str, object]:
    try:
        record = _loop_audit(loop_audit)
    except (TypeError, ValueError, KeyError) as error:
        return {"valid": False, "error_codes": (f"invalid_loop_audit:{error}",)}
    errors: list[str] = []
    if record.audit_status.startswith("passed_"):
        for flag in (
            "power_off_gaps_respected",
            "idle_ticks_valid",
            "event_frames_valid",
            "event_stack_valid",
            "event_returns_valid",
            "event_tree_valid",
            "bounded_window_verified",
            "no_autonomous_scheduler",
            "no_open_ended_loop",
            "no_background_daemon",
            "no_free_action_selection",
            "no_external_execution",
            "no_unity_execution",
            "no_bridge_execution",
            "no_memory_layer_write",
            "no_core_memory_write",
            "no_long_term_memory_write",
            "no_archive_memory_write",
            "no_anchor_write",
            "no_automatic_learning_approval",
            "no_recursive_learning",
            "no_production_behavior",
        ):
            if getattr(record, flag) is not True:
                errors.append(f"{flag}_false")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "continuous_loop_audit_id": record.continuous_loop_audit_id,
        "audit_status": record.audit_status,
    }


def render_runtime_timeline_from_trace(
    loop_trace: RuntimeContinuousLoopTrace | dict[str, object],
) -> str:
    return _loop_trace(loop_trace).normalized_timeline_text


def render_event_tree_text(event_tree: RuntimeEventTreeRecord | dict[str, object]) -> str:
    tree = _event_tree(event_tree)
    return (
        f"event_tree depth={tree.tree_depth_max} frames={tree.tree_frame_count} "
        f"closed={tree.tree_closed_frame_count} status={tree.tree_status}"
    )


def build_demo_idle_only_continuous_loop() -> dict[str, object]:
    return _build_loop_bundle(".....")


def build_demo_power_off_gap_continuous_loop() -> dict[str, object]:
    return _build_loop_bundle("   .....   ")


def build_demo_nested_event_continuous_loop() -> dict[str, object]:
    return _build_loop_bundle(NESTED_DEMO_TIMELINE)


def build_demo_blocked_invalid_depth_jump_loop() -> dict[str, object]:
    return _build_loop_bundle(".13", invalid_event_stack=True)


def build_demo_blocked_power_off_tick_violation_loop() -> dict[str, object]:
    return _build_loop_bundle(" .", tick_created_during_power_off=True)


def build_demo_blocked_unbounded_loop_attempt() -> dict[str, object]:
    return _build_loop_bundle("while true", unbounded=True)


def build_demo_blocked_forbidden_authority_loop() -> dict[str, object]:
    return _build_loop_bundle(
        NESTED_DEMO_TIMELINE,
        external_execution_created=True,
        memory_layer_write_performed=True,
        automatic_learning_approval_created=True,
        recursive_learning_created=True,
        production_behavior_created=True,
    )


def build_demo_blocked_continuous_loop(case: str) -> dict[str, object]:
    cases = {
        "invalid-depth-jump": build_demo_blocked_invalid_depth_jump_loop,
        "power-off-tick": build_demo_blocked_power_off_tick_violation_loop,
        "unbounded-loop": build_demo_blocked_unbounded_loop_attempt,
        "forbidden-authority": build_demo_blocked_forbidden_authority_loop,
    }
    try:
        return cases[case]()
    except KeyError as error:
        raise ValueError(f"unknown continuous loop blocked case: {case}") from error


def audit_runtime_timeline(
    *,
    timeline_text: str,
    max_depth: int = DEFAULT_MAX_DEPTH,
    unbounded: bool = False,
) -> dict[str, object]:
    invalid_event_stack = False
    try:
        parse_runtime_timeline_symbols(
            timeline_text,
            max_depth=max_depth,
            unbounded=unbounded,
        )
    except ValueError:
        invalid_event_stack = not (unbounded or "while true" in timeline_text.lower())
    return _build_loop_bundle(
        timeline_text,
        max_depth=max_depth,
        unbounded=unbounded,
        invalid_event_stack=invalid_event_stack,
    )


def _build_loop_bundle(
    timeline_text: str,
    *,
    max_depth: int = DEFAULT_MAX_DEPTH,
    tick_created_during_power_off: bool = False,
    unbounded: bool = False,
    invalid_event_stack: bool = False,
    leave_unclosed_at_end: bool = False,
    autonomous_scheduler_created: bool = False,
    open_ended_loop_created: bool = False,
    background_daemon_created: bool = False,
    external_execution_created: bool = False,
    memory_layer_write_performed: bool = False,
    automatic_learning_approval_created: bool = False,
    recursive_learning_created: bool = False,
    production_behavior_created: bool = False,
) -> dict[str, object]:
    power_window = build_runtime_power_window_record(
        timeline_text=timeline_text,
        tick_created_during_power_off=tick_created_during_power_off,
        unbounded=unbounded,
        autonomous_scheduler_created=autonomous_scheduler_created,
        open_ended_loop_created=open_ended_loop_created,
        background_daemon_created=background_daemon_created,
    )
    ticks = build_runtime_tick_records_from_timeline(
        power_window=power_window,
        max_depth=max_depth,
    )
    frames = build_runtime_event_frames_from_timeline(
        power_window=power_window,
        max_depth=max_depth,
        leave_unclosed_at_end=leave_unclosed_at_end,
    )
    returns = build_runtime_event_return_records(
        power_window=power_window,
        max_depth=max_depth,
    )
    stacks = build_runtime_event_stack_records(
        power_window=power_window,
        max_depth=max_depth,
        invalid_parent_child_order_detected=invalid_event_stack,
        unclosed_frame_detected=leave_unclosed_at_end,
    )
    tree = build_runtime_event_tree_record(
        power_window=power_window,
        event_frames=frames,
        event_returns=returns,
    )
    trace = build_runtime_continuous_loop_trace(
        power_window=power_window,
        ticks=ticks,
        event_frames=frames,
        event_stacks=stacks,
        event_returns=returns,
        event_tree=tree,
        forbidden_authority_detected=(
            external_execution_created
            or memory_layer_write_performed
            or automatic_learning_approval_created
            or recursive_learning_created
            or production_behavior_created
        ),
    )
    audit = build_runtime_continuous_loop_audit(
        loop_trace=trace,
        event_tree=tree,
        ticks=ticks,
        event_frames=frames,
        event_stacks=stacks,
        event_returns=returns,
        autonomous_scheduler_created=autonomous_scheduler_created,
        open_ended_loop_created=open_ended_loop_created,
        background_daemon_created=background_daemon_created,
        external_execution_created=external_execution_created,
        memory_layer_write_performed=memory_layer_write_performed,
        automatic_learning_approval_created=automatic_learning_approval_created,
        recursive_learning_created=recursive_learning_created,
        production_behavior_created=production_behavior_created,
    )
    return {
        "runtime_power_window": power_window.to_dict(),
        "runtime_ticks": [tick.to_dict() for tick in ticks],
        "runtime_event_frames": [frame.to_dict() for frame in frames],
        "runtime_event_stacks": [stack.to_dict() for stack in stacks],
        "runtime_event_returns": [item.to_dict() for item in returns],
        "runtime_event_tree": tree.to_dict(),
        "runtime_continuous_loop_trace": trace.to_dict(),
        "runtime_continuous_loop_audit": audit.to_dict(),
        "rendered_timeline": render_runtime_timeline_from_trace(trace),
        "rendered_event_tree": render_event_tree_text(tree),
    }


def _analyze_timeline(
    power_window: RuntimePowerWindowRecord,
    *,
    max_depth: int = DEFAULT_MAX_DEPTH,
    event_budget_ticks: int = 64,
    leave_unclosed_at_end: bool = False,
    force_budget_exceeded: bool = False,
    force_child_scope_expansion: bool = False,
    force_forbidden_authority: bool = False,
    return_scope_changed_parent: bool = False,
    return_created_new_event_without_parent: bool = False,
    force_return_forbidden_authority: bool = False,
) -> dict[str, object]:
    frame_data: dict[str, dict[str, object]] = {}
    return_data: list[RuntimeEventReturnRecord] = []
    open_frames: dict[int, str] = {}
    tick_data: list[dict[str, object]] = []
    frame_counter = 0
    tick_index = 0
    previous_depth = 0

    def open_frame(depth: int, tick: int, invalid_parent: bool = False) -> str:
        nonlocal frame_counter
        frame_counter += 1
        parent_id = open_frames.get(depth - 1) if depth > 1 else None
        frame_id = (
            f"runtime_event_frame:{power_window.power_window_id}:d{depth}:n{frame_counter}"
        )
        if parent_id and parent_id in frame_data:
            frame_data[parent_id]["child_ids"].append(frame_id)
        frame_data[frame_id] = {
            "event_frame_id": frame_id,
            "event_depth": depth,
            "parent_event_frame_id": parent_id,
            "child_ids": [],
            "opened_at_tick_index": tick,
            "closed_at_tick_index": None,
            "event_ticks_used": 0,
            "event_status": "event_blocked_invalid_parent" if invalid_parent else "event_opened",
            "return_payload_id": None,
            "return_payload_status": "none",
            "child_scope_expansion_detected": False,
            "budget_exceeded": False,
            "unclosed_frame_detected": False,
            "memory_write_performed": False,
            "automatic_learning_approval_created": False,
            "free_action_selection_created": False,
            "external_execution_created": False,
            "production_behavior_created": False,
        }
        if not invalid_parent:
            open_frames[depth] = frame_id
        return frame_id

    def close_frame(frame_id: str, tick: int) -> None:
        data = frame_data[frame_id]
        if data["event_status"] == "event_blocked_invalid_parent":
            return
        data["closed_at_tick_index"] = tick
        data["event_status"] = "event_closed_returned"
        parent_id = data["parent_event_frame_id"]
        return_status = "returned_success"
        if return_scope_changed_parent:
            return_status = "blocked_scope_mutation_detected"
        elif force_return_forbidden_authority:
            return_status = "blocked_forbidden_authority_detected"
        return_payload_status = (
            "returned_blocked" if return_status.startswith("blocked_") else return_status
        )
        event_return_id = f"runtime_event_return:{frame_id}:t{tick}"
        data["return_payload_id"] = event_return_id
        data["return_payload_status"] = return_payload_status
        return_data.append(
            RuntimeEventReturnRecord(
                event_return_id=event_return_id,
                schema_version=EVENT_RETURN_SCHEMA_VERSION,
                created_at=power_window.created_at,
                source_engine=SOURCE_ENGINE,
                source_event_frame_id=frame_id,
                parent_event_frame_id=parent_id,
                return_tick_index=tick,
                return_status=return_status,
                return_reason="event_depth_returned_to_parent",
                return_summary=f"Event frame {frame_id} returned at tick {tick}.",
                return_payload={
                    "event_frame_id": frame_id,
                    "event_depth": data["event_depth"],
                    "status": return_payload_status,
                },
                parent_resumed=parent_id is not None,
                parent_resume_tick_index=tick if parent_id else None,
                return_scope_changed_parent=return_scope_changed_parent,
                return_created_new_event_without_parent=return_created_new_event_without_parent,
                memory_write_performed=False,
                automatic_learning_approval_created=False,
                external_execution_created=force_return_forbidden_authority,
                source_trace_refs=power_window.source_trace_refs,
            )
        )

    for symbol in power_window.parsed_timeline_symbols:
        if symbol == " ":
            for depth in sorted(open_frames.keys(), reverse=True):
                close_frame(open_frames[depth], tick_index)
            open_frames.clear()
            previous_depth = 0
            continue
        tick_index += 1
        if symbol == ".":
            closed = bool(open_frames)
            for depth in sorted(open_frames.keys(), reverse=True):
                close_frame(open_frames[depth], tick_index)
            open_frames.clear()
            tick_data.append(
                {
                    "index": tick_index,
                    "symbol": symbol,
                    "depth": 0,
                    "stack": tuple(),
                    "created": False,
                    "closed": closed,
                }
            )
            previous_depth = 0
            continue
        depth = int(symbol)
        created = False
        closed = False
        invalid_depth = False
        max_depth_exceeded = depth > max_depth
        if max_depth_exceeded:
            invalid_depth = True
        elif previous_depth == 0 and depth != 1:
            invalid_depth = True
            open_frame(depth, tick_index, invalid_parent=True)
        elif depth > previous_depth + 1:
            invalid_depth = True
            open_frame(depth, tick_index, invalid_parent=True)
        else:
            if depth <= previous_depth:
                for closing_depth in sorted(
                    [item for item in open_frames if item > depth],
                    reverse=True,
                ):
                    close_frame(open_frames[closing_depth], tick_index)
                    del open_frames[closing_depth]
                    closed = True
            if depth not in open_frames:
                open_frame(depth, tick_index)
                created = True
            for active_depth in range(1, depth + 1):
                frame_id = open_frames.get(active_depth)
                if frame_id:
                    frame_data[frame_id]["event_ticks_used"] = (
                        int(frame_data[frame_id]["event_ticks_used"]) + 1
                    )
            previous_depth = depth
        stack = tuple(open_frames[item] for item in sorted(open_frames) if item <= depth)
        tick_data.append(
            {
                "index": tick_index,
                "symbol": symbol,
                "depth": depth,
                "stack": stack,
                "created": created,
                "closed": closed,
                "invalid_depth": invalid_depth,
                "max_depth_exceeded": max_depth_exceeded,
            }
        )

    if open_frames:
        for depth in sorted(open_frames.keys(), reverse=True):
            frame_id = open_frames[depth]
            if leave_unclosed_at_end:
                frame_data[frame_id]["event_status"] = (
                    "event_blocked_unclosed_at_window_end"
                )
                frame_data[frame_id]["unclosed_frame_detected"] = True
            else:
                close_frame(frame_id, tick_index)

    frame_records: list[RuntimeEventFrameRecord] = []
    for data in frame_data.values():
        event_ticks_used = int(data["event_ticks_used"])
        status = str(data["event_status"])
        budget_exceeded = force_budget_exceeded or event_ticks_used > event_budget_ticks
        child_scope_expansion = (
            force_child_scope_expansion and int(data["event_depth"]) > 1
        )
        if budget_exceeded:
            status = "event_blocked_budget_exceeded"
        if child_scope_expansion:
            status = "event_blocked_child_scope_expansion"
        if force_forbidden_authority:
            status = "event_blocked_forbidden_authority_detected"
        frame_records.append(
            RuntimeEventFrameRecord(
                event_frame_id=str(data["event_frame_id"]),
                schema_version=EVENT_FRAME_SCHEMA_VERSION,
                created_at=power_window.created_at,
                source_engine=SOURCE_ENGINE,
                source_power_window_id=power_window.power_window_id,
                event_type=_event_type_for_depth(int(data["event_depth"])),
                event_label=_event_label_for_depth(int(data["event_depth"])),
                event_depth=int(data["event_depth"]),
                parent_event_frame_id=data["parent_event_frame_id"],
                child_event_frame_ids=tuple(data["child_ids"]),
                opened_at_tick_index=int(data["opened_at_tick_index"]),
                closed_at_tick_index=data["closed_at_tick_index"],
                event_scope=(
                    "expanded_runtime_scope"
                    if child_scope_expansion
                    else "bounded_runtime_window"
                ),
                event_budget_ticks=event_budget_ticks,
                event_ticks_used=event_ticks_used,
                event_status=status,
                event_summary=_event_frame_summary(status, int(data["event_depth"])),
                return_payload_id=data["return_payload_id"],
                return_payload_status=data["return_payload_status"],
                child_scope_expansion_detected=child_scope_expansion,
                budget_exceeded=budget_exceeded,
                unclosed_frame_detected=bool(data["unclosed_frame_detected"]),
                memory_write_performed=False,
                automatic_learning_approval_created=False,
                free_action_selection_created=force_forbidden_authority,
                external_execution_created=force_forbidden_authority,
                production_behavior_created=force_forbidden_authority,
                source_trace_refs=power_window.source_trace_refs,
            )
        )
    return {"ticks": tick_data, "frames": frame_records, "returns": return_data}


def _audit_status(
    *,
    blocked_reasons: list[str],
    trace: RuntimeContinuousLoopTrace,
) -> str:
    priority = (
        ("power_off_tick_detected", "blocked_power_off_tick_detected"),
        ("invalid_event_stack", "blocked_invalid_event_stack"),
        ("unclosed_event_frame", "blocked_unclosed_event_frame"),
        ("unbounded_loop", "blocked_unbounded_loop"),
        ("autonomous_scheduler_detected", "blocked_autonomous_scheduler_detected"),
        ("open_ended_loop_detected", "blocked_open_ended_loop_detected"),
        ("external_execution_detected", "blocked_external_execution_detected"),
        ("memory_write_detected", "blocked_memory_write_detected"),
        (
            "automatic_learning_approval_detected",
            "blocked_automatic_learning_approval_detected",
        ),
        ("recursive_learning_detected", "blocked_recursive_learning_detected"),
        ("production_behavior_detected", "blocked_production_behavior_detected"),
    )
    for reason, status in priority:
        if reason in blocked_reasons:
            return status
    if trace.event_tick_count > 0:
        return "passed_continuous_event_loop_nested_frame_demo"
    if trace.power_off_span_count > 0:
        return "passed_power_off_gap_respected"
    return "passed_idle_only_loop_demo"


def _event_type_for_depth(depth: int) -> str:
    return {
        1: "task_trial",
        2: "action_chain",
        3: "sense_observation",
        4: "mismatch_detection",
    }.get(depth, f"runtime_event_depth_{depth}")


def _event_label_for_depth(depth: int) -> str:
    return {
        1: "event_1_task_trial",
        2: "event_2_action_chain",
        3: "event_3_sense_observation",
        4: "event_4_mismatch_detection",
    }.get(depth, f"event_{depth}_runtime")


def _power_window_summary(status: str, tick_count: int, power_off_count: int) -> str:
    if status == "power_window_valid":
        return (
            f"Power window valid with {tick_count} power-on ticks and "
            f"{power_off_count} power-off spans."
        )
    if status == "power_window_blocked_tick_during_power_off":
        return "Power window blocked because a tick was created during power-off."
    if status == "power_window_blocked_unbounded":
        return "Power window blocked because an unbounded loop was requested."
    return "Power window blocked because scheduler or daemon authority was detected."


def _tick_summary(tick_kind: str, tick_status: str, symbol: str) -> str:
    if tick_status != "tick_recorded":
        return f"Tick blocked for symbol {symbol}."
    if tick_kind == "idle_heartbeat":
        return "Idle heartbeat tick recorded."
    if tick_kind == "event_return_tick":
        return "Event return/resume tick recorded."
    return "Event frame tick recorded."


def _event_frame_summary(status: str, depth: int) -> str:
    if status == "event_closed_returned":
        return f"Depth {depth} event frame closed and returned."
    if status == "event_blocked_budget_exceeded":
        return f"Depth {depth} event frame blocked by budget."
    if status == "event_blocked_invalid_parent":
        return f"Depth {depth} event frame blocked by invalid parent."
    if status == "event_blocked_child_scope_expansion":
        return f"Depth {depth} event frame blocked by child scope expansion."
    if status == "event_blocked_unclosed_at_window_end":
        return f"Depth {depth} event frame blocked because it remained unclosed."
    if status == "event_blocked_forbidden_authority_detected":
        return f"Depth {depth} event frame blocked by forbidden authority."
    return f"Depth {depth} event frame opened or continued."


def _stack_summary(status: str, depth: int) -> str:
    if status == "stack_empty_idle":
        return "Idle tick has empty event stack."
    if status == "stack_valid":
        return f"Event stack valid at depth {depth}."
    return f"Event stack blocked with status {status}."


def _tree_summary(status: str, count: int) -> str:
    if status == "tree_valid_all_frames_closed":
        return f"Event tree valid with {count} closed frame records."
    if status == "tree_valid_with_blocked_unclosed_frames":
        return "Event tree recorded blocked unclosed frames."
    return f"Event tree blocked with status {status}."


def _loop_trace_summary(status: str) -> str:
    return {
        "loop_trace_valid": "Continuous loop trace valid.",
        "loop_trace_valid_with_power_off_gaps": (
            "Continuous loop trace valid and power-off gaps were preserved."
        ),
        "loop_trace_blocked_power_off_tick": (
            "Continuous loop trace blocked because power-off was processed as a tick."
        ),
        "loop_trace_blocked_unclosed_event": (
            "Continuous loop trace blocked because an event frame was unclosed."
        ),
        "loop_trace_blocked_unbounded": (
            "Continuous loop trace blocked because an unbounded loop was requested."
        ),
        "loop_trace_blocked_forbidden_authority_detected": (
            "Continuous loop trace blocked by forbidden authority."
        ),
    }[status]


def _power_window(
    value: RuntimePowerWindowRecord | dict[str, object],
) -> RuntimePowerWindowRecord:
    if isinstance(value, RuntimePowerWindowRecord):
        return value
    return RuntimePowerWindowRecord.from_dict(value)


def _tick(value: RuntimeTickRecord | dict[str, object]) -> RuntimeTickRecord:
    if isinstance(value, RuntimeTickRecord):
        return value
    return RuntimeTickRecord.from_dict(value)


def _event_frame(
    value: RuntimeEventFrameRecord | dict[str, object],
) -> RuntimeEventFrameRecord:
    if isinstance(value, RuntimeEventFrameRecord):
        return value
    return RuntimeEventFrameRecord.from_dict(value)


def _event_stack(
    value: RuntimeEventStackRecord | dict[str, object],
) -> RuntimeEventStackRecord:
    if isinstance(value, RuntimeEventStackRecord):
        return value
    return RuntimeEventStackRecord.from_dict(value)


def _event_return(
    value: RuntimeEventReturnRecord | dict[str, object],
) -> RuntimeEventReturnRecord:
    if isinstance(value, RuntimeEventReturnRecord):
        return value
    return RuntimeEventReturnRecord.from_dict(value)


def _event_tree(
    value: RuntimeEventTreeRecord | dict[str, object],
) -> RuntimeEventTreeRecord:
    if isinstance(value, RuntimeEventTreeRecord):
        return value
    return RuntimeEventTreeRecord.from_dict(value)


def _loop_trace(
    value: RuntimeContinuousLoopTrace | dict[str, object],
) -> RuntimeContinuousLoopTrace:
    if isinstance(value, RuntimeContinuousLoopTrace):
        return value
    return RuntimeContinuousLoopTrace.from_dict(value)


def _loop_audit(
    value: RuntimeContinuousLoopAudit | dict[str, object],
) -> RuntimeContinuousLoopAudit:
    if isinstance(value, RuntimeContinuousLoopAudit):
        return value
    return RuntimeContinuousLoopAudit.from_dict(value)
