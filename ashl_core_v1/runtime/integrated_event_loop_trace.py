"""Integrated bounded runtime event-loop dispatch/resume traces."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.runtime.continuous_event_loop import (
    DEFAULT_MAX_DEPTH,
    NESTED_DEMO_TIMELINE,
    RuntimeContinuousLoopAudit,
    RuntimeContinuousLoopTrace,
    RuntimeEventFrameRecord,
    RuntimeEventReturnRecord,
    RuntimeEventStackRecord,
    RuntimeEventTreeRecord,
    RuntimePowerWindowRecord,
    RuntimeTickRecord,
    build_runtime_continuous_loop_audit,
    build_runtime_continuous_loop_trace,
    build_runtime_event_frames_from_timeline,
    build_runtime_event_return_records,
    build_runtime_event_stack_records,
    build_runtime_event_tree_record,
    build_runtime_power_window_record,
    build_runtime_tick_records_from_timeline,
    normalize_runtime_timeline_text,
)
from ashl_core_v1.runtime.event_frame_dispatch_adapter import (
    RuntimeEventDispatchAudit,
    RuntimeEventDispatchRequestRecord,
    RuntimeEventDispatchResultRecord,
    RuntimeEventDispatchReturnPayloadRecord,
    RuntimeEventDispatchRouteRecord,
    RuntimeEventHandlerAdapterRecord,
    classify_runtime_event_type,
    dispatch_event_frame_adapter_only,
)
from ashl_core_v1.runtime.event_return_parent_resume import (
    RuntimeNestedReturnResumeTrace,
    RuntimeParentFrameResumeAudit,
    RuntimeParentFrameResumeDecisionRecord,
    RuntimeParentFrameResumeRecord,
    RuntimeParentFrameResumeRequestRecord,
    RuntimeParentFrameResumeStackUpdateRecord,
    build_runtime_nested_return_resume_trace,
    build_runtime_parent_frame_resume_audit,
    resume_parent_frame_from_child_return,
)


SOURCE_ENGINE = "runtime"
INTEGRATED_EVENT_STEP_SCHEMA_VERSION = "runtime_integrated_event_step_v0"
INTEGRATED_DISPATCH_RESUME_LINK_SCHEMA_VERSION = (
    "runtime_integrated_dispatch_resume_link_v0"
)
INTEGRATED_LOOP_TRACE_SCHEMA_VERSION = "runtime_integrated_event_loop_trace_v0"
INTEGRATED_TIMELINE_RENDER_SCHEMA_VERSION = (
    "runtime_integrated_event_loop_timeline_render_v0"
)
INTEGRATED_LOOP_AUDIT_SCHEMA_VERSION = "runtime_integrated_event_loop_audit_v0"
INTEGRATED_LOOP_READINESS_SCHEMA_VERSION = (
    "runtime_integrated_event_loop_readiness_v0"
)

SIMPLE_TASK_TIMELINE = ".11."
NESTED_SENSE_TIMELINE = ".1221."
THOUGHT_DEFERRED_TIMELINE = ".12."
POWER_OFF_GAP_TIMELINE = "   ...1221   "

ALLOWED_STEP_KINDS = {
    "power_off_gap",
    "idle_heartbeat_step",
    "event_open_step",
    "event_continue_step",
    "event_dispatch_step",
    "event_return_step",
    "parent_resume_step",
    "stack_update_step",
    "event_close_step",
    "blocked_step",
}
ALLOWED_STEP_STATUSES = {
    "step_recorded",
    "step_recorded_idle",
    "step_recorded_power_off_gap",
    "step_recorded_event_dispatch_resume",
    "step_blocked_invalid_lineage",
    "step_blocked_missing_dispatch",
    "step_blocked_missing_return_payload",
    "step_blocked_missing_parent_resume",
    "step_blocked_forbidden_authority_detected",
}
ALLOWED_LINK_STATUSES = {
    "dispatch_resume_link_valid",
    "dispatch_resume_link_valid_root_close",
    "dispatch_resume_link_deferred_thought_engine",
    "blocked_missing_dispatch_result",
    "blocked_missing_return_payload",
    "blocked_missing_parent_resume",
    "blocked_invalid_stack_update",
    "blocked_forbidden_authority_detected",
}
ALLOWED_TRACE_STATUSES = {
    "integrated_event_loop_trace_complete",
    "integrated_event_loop_trace_complete_with_deferred_thought",
    "integrated_event_loop_trace_complete_with_power_off_gaps",
    "integrated_event_loop_trace_blocked_missing_dispatch",
    "integrated_event_loop_trace_blocked_missing_return",
    "integrated_event_loop_trace_blocked_missing_parent_resume",
    "integrated_event_loop_trace_blocked_invalid_stack",
    "integrated_event_loop_trace_blocked_unclosed_frame",
    "integrated_event_loop_trace_blocked_forbidden_authority_detected",
}
ALLOWED_RENDER_STATUSES = {
    "timeline_render_created",
    "timeline_render_created_with_deferred_thought",
    "timeline_render_blocked_invalid_trace",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_integrated_event_loop_dispatch_resume_trace",
    "passed_integrated_event_loop_with_deferred_thought",
    "passed_integrated_event_loop_with_power_off_gaps",
    "blocked_invalid_power_window",
    "blocked_invalid_tick_lineage",
    "blocked_missing_dispatch_lineage",
    "blocked_missing_return_payload",
    "blocked_missing_parent_resume",
    "blocked_invalid_stack_update",
    "blocked_unclosed_root_frame",
    "blocked_dynamic_child_event_scheduling_detected",
    "blocked_autonomous_scheduler_detected",
    "blocked_open_ended_loop_detected",
    "blocked_external_execution_detected",
    "blocked_memory_write_detected",
    "blocked_automatic_learning_approval_detected",
    "blocked_recursive_learning_detected",
    "blocked_thought_engine_fake_detected",
    "blocked_production_behavior_detected",
}
ALLOWED_READINESS_STATUSES = {
    "ready_for_fixed_runtime_playback_only",
    "ready_for_bounded_runtime_handler_binding_only",
    "not_ready_missing_integrated_loop_trace",
    "not_ready_boundary_failure",
    "blocked_forbidden_authority_detected",
}

TARGET_BY_FAMILY = {
    "runtime_event": "runtime",
    "state_event": "state_engine",
    "task_event": "task_engine",
    "sense_event": "sense_interface",
    "learning_event": "learning_engine",
    "memory_event": "memory_engine",
    "thought_event": "thought_engine",
    "output_event": "output_interface",
    "audit_event": "audit_layer",
    "unknown_event": "none",
}

SAFE_CLAIM = (
    "ASHL Core v1 can produce an integrated bounded runtime event-loop trace "
    "that connects power windows, ticks, nested EventFrames, adapter-only "
    "dispatch, safe return payloads, parent frame resume decisions, stack "
    "updates, event tree closure, timeline rendering, and audit/readiness "
    "records."
)
BLOCKED_CLAIMS = (
    "no_live_qingyin_runtime_session",
    "no_dynamic_child_event_scheduling",
    "no_autonomous_scheduler",
    "no_open_ended_loop",
    "no_free_action_selection",
    "no_external_execution",
    "no_memory_layer_write",
    "no_automatic_learning_approval",
    "no_recursive_learning",
    "no_thought_engine_cognition",
    "no_first_output",
    "not_awake",
)
READINESS_NEXT_PACKAGE = (
    "Package 99 / ASHL Core v1 Runtime Fixed Closed Loop Playback Over "
    "Event Frames Minimal v0"
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


@dataclass(frozen=True)
class RuntimeIntegratedEventStepRecord:
    integrated_event_step_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_power_window_id: str
    source_runtime_tick_id: str | None
    source_event_frame_id: str | None
    source_event_stack_id: str | None
    source_dispatch_request_id: str | None
    source_dispatch_route_id: str | None
    source_handler_adapter_id: str | None
    source_dispatch_result_id: str | None
    source_dispatch_return_payload_id: str | None
    source_parent_resume_id: str | None
    source_resume_stack_update_id: str | None
    tick_index: int
    timeline_symbol: str
    event_depth: int
    event_type: str | None
    event_family: str | None
    target_engine: str | None
    step_kind: str
    step_status: str
    step_summary: str
    event_frame_opened: bool
    event_frame_dispatched: bool
    return_payload_created: bool
    parent_resume_recorded: bool
    stack_updated: bool
    idle_tick: bool
    power_off_gap: bool
    dynamic_child_event_created: bool
    autonomous_scheduler_created: bool
    open_ended_loop_created: bool
    external_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    recursive_learning_created: bool
    thought_engine_behavior_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INTEGRATED_EVENT_STEP_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_integrated_event_step_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.step_kind not in ALLOWED_STEP_KINDS:
            raise ValueError(f"unknown step_kind: {self.step_kind}")
        if self.step_status not in ALLOWED_STEP_STATUSES:
            raise ValueError(f"unknown step_status: {self.step_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeIntegratedEventStepRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeIntegratedEventDispatchResumeLinkRecord:
    dispatch_resume_link_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_event_frame_id: str
    source_dispatch_request_id: str | None
    source_dispatch_result_id: str | None
    source_dispatch_return_payload_id: str | None
    source_child_event_frame_id: str | None
    source_parent_event_frame_id: str | None
    source_parent_resume_id: str | None
    source_resume_stack_update_id: str | None
    event_type: str
    event_family: str
    target_engine: str
    return_status: str
    parent_resume_status: str | None
    dispatch_to_return_link_valid: bool
    return_to_parent_resume_link_valid: bool
    stack_update_link_valid: bool
    link_status: str
    link_summary: str
    external_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    recursive_learning_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INTEGRATED_DISPATCH_RESUME_LINK_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_integrated_dispatch_resume_link_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.link_status not in ALLOWED_LINK_STATUSES:
            raise ValueError(f"unknown link_status: {self.link_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "RuntimeIntegratedEventDispatchResumeLinkRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeIntegratedEventLoopTrace:
    integrated_loop_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_power_window_id: str
    source_continuous_loop_trace_id: str | None
    source_event_tree_id: str | None
    source_continuous_loop_audit_id: str | None
    source_dispatch_audit_ids: tuple[str, ...]
    source_parent_resume_audit_ids: tuple[str, ...]
    integrated_event_step_ids: tuple[str, ...]
    dispatch_resume_link_ids: tuple[str, ...]
    timeline_text: str
    canonical_timeline_text: str
    rendered_timeline_text: str
    tick_count: int
    idle_tick_count: int
    event_tick_count: int
    power_off_gap_count: int
    event_frame_count: int
    dispatch_count: int
    return_payload_count: int
    parent_resume_count: int
    stack_update_count: int
    max_event_depth_observed: int
    all_event_frames_dispatched_or_idle: bool
    all_dispatches_returned: bool
    all_child_returns_resumed: bool
    all_event_frames_closed_or_validly_deferred: bool
    integrated_trace_status: str
    integrated_trace_summary: str
    dynamic_child_event_created: bool
    autonomous_scheduler_created: bool
    open_ended_loop_created: bool
    external_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    recursive_learning_created: bool
    thought_engine_behavior_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INTEGRATED_LOOP_TRACE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_integrated_event_loop_trace_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.integrated_trace_status not in ALLOWED_TRACE_STATUSES:
            raise ValueError(
                f"unknown integrated_trace_status: {self.integrated_trace_status}"
            )
        for name in (
            "source_dispatch_audit_ids",
            "source_parent_resume_audit_ids",
            "integrated_event_step_ids",
            "dispatch_resume_link_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeIntegratedEventLoopTrace":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeIntegratedEventLoopTimelineRenderRecord:
    integrated_timeline_render_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_integrated_loop_trace_id: str
    timeline_text: str
    canonical_timeline_text: str
    human_readable_tree_text: str
    compact_step_summary: tuple[str, ...]
    legend: dict[str, str]
    render_status: str
    render_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INTEGRATED_TIMELINE_RENDER_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_integrated_event_loop_timeline_render_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.render_status not in ALLOWED_RENDER_STATUSES:
            raise ValueError(f"unknown render_status: {self.render_status}")
        for name in ("compact_step_summary", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "RuntimeIntegratedEventLoopTimelineRenderRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeIntegratedEventLoopAudit:
    integrated_loop_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_integrated_loop_trace_id: str | None
    source_timeline_render_id: str | None
    power_window_valid: bool
    tick_lineage_valid: bool
    event_frame_lineage_valid: bool
    event_stack_lineage_valid: bool
    event_tree_valid: bool
    dispatch_lineage_valid: bool
    dispatch_return_payload_valid: bool
    parent_resume_lineage_valid: bool
    stack_update_lineage_valid: bool
    all_events_dispatched_or_validly_deferred: bool
    all_dispatches_returned: bool
    all_child_returns_resumed: bool
    all_root_frames_closed: bool
    bounded_window_confirmed: bool
    adapter_only_confirmed: bool
    record_only_confirmed: bool
    no_dynamic_child_event_scheduling: bool
    no_autonomous_scheduler: bool
    no_open_ended_loop: bool
    no_background_daemon: bool
    no_external_execution: bool
    no_unity_execution: bool
    no_bridge_execution: bool
    no_network_execution: bool
    no_filesystem_execution: bool
    no_memory_layer_write: bool
    no_core_memory_write: bool
    no_long_term_memory_write: bool
    no_archive_memory_write: bool
    no_anchor_write: bool
    no_automatic_learning_approval: bool
    no_free_action_selection: bool
    no_recursive_learning: bool
    no_thought_engine_behavior: bool
    no_production_behavior: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INTEGRATED_LOOP_AUDIT_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_integrated_event_loop_audit_v0"
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
    def from_dict(cls, data: dict[str, object]) -> "RuntimeIntegratedEventLoopAudit":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeIntegratedEventLoopReadinessRecord:
    integrated_loop_readiness_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_integrated_loop_audit_id: str
    current_verified_capability: str
    recommended_next_package: str
    recommended_next_reason: str
    ready_for_bounded_runtime_handler_binding: bool
    ready_for_fixed_runtime_playback_of_existing_closed_loop: bool
    ready_for_dynamic_child_event_scheduling: bool
    ready_for_autonomous_scheduler: bool
    ready_for_open_ended_loop: bool
    ready_for_external_execution: bool
    ready_for_memory_layer_write: bool
    ready_for_automatic_learning_approval: bool
    ready_for_recursive_learning: bool
    ready_for_thought_engine_runtime: bool
    ready_for_first_output: bool
    readiness_status: str
    readiness_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != INTEGRATED_LOOP_READINESS_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_integrated_event_loop_readiness_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.readiness_status not in ALLOWED_READINESS_STATUSES:
            raise ValueError(f"unknown readiness_status: {self.readiness_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(
        cls, data: dict[str, object]
    ) -> "RuntimeIntegratedEventLoopReadinessRecord":
        return cls(**dict(data))


def build_runtime_integrated_event_step_record(
    *,
    power_window: RuntimePowerWindowRecord | dict[str, object],
    tick: RuntimeTickRecord | dict[str, object] | None = None,
    event_frame: RuntimeEventFrameRecord | dict[str, object] | None = None,
    event_stack: RuntimeEventStackRecord | dict[str, object] | None = None,
    dispatch_request: RuntimeEventDispatchRequestRecord | dict[str, object] | None = None,
    dispatch_route: RuntimeEventDispatchRouteRecord | dict[str, object] | None = None,
    handler_adapter: RuntimeEventHandlerAdapterRecord | dict[str, object] | None = None,
    dispatch_result: RuntimeEventDispatchResultRecord | dict[str, object] | None = None,
    dispatch_return_payload: RuntimeEventDispatchReturnPayloadRecord | dict[str, object] | None = None,
    parent_resume: RuntimeParentFrameResumeRecord | dict[str, object] | None = None,
    resume_stack_update: RuntimeParentFrameResumeStackUpdateRecord | dict[str, object] | None = None,
    tick_index: int | None = None,
    timeline_symbol: str | None = None,
    step_kind: str | None = None,
    force_dynamic_child_event_created: bool = False,
    force_autonomous_scheduler_created: bool = False,
    force_open_ended_loop_created: bool = False,
    force_external_execution_created: bool = False,
    force_memory_layer_write_performed: bool = False,
    force_automatic_learning_approval_created: bool = False,
    force_recursive_learning_created: bool = False,
    force_thought_engine_behavior_created: bool = False,
    force_production_behavior_created: bool = False,
) -> RuntimeIntegratedEventStepRecord:
    window = _power_window(power_window)
    tick_record = _tick(tick) if tick is not None else None
    frame = _event_frame(event_frame) if event_frame is not None else None
    stack = _event_stack(event_stack) if event_stack is not None else None
    request = _dispatch_request(dispatch_request) if dispatch_request is not None else None
    route = _dispatch_route(dispatch_route) if dispatch_route is not None else None
    adapter = _handler_adapter(handler_adapter) if handler_adapter is not None else None
    result = _dispatch_result(dispatch_result) if dispatch_result is not None else None
    return_payload = (
        _dispatch_return_payload(dispatch_return_payload)
        if dispatch_return_payload is not None
        else None
    )
    resume = _parent_resume(parent_resume) if parent_resume is not None else None
    stack_update = (
        _resume_stack_update(resume_stack_update)
        if resume_stack_update is not None
        else None
    )

    event_type = frame.event_type if frame is not None else None
    if event_type is None and request is not None:
        event_type = request.event_type
    event_family = classify_runtime_event_type(event_type) if event_type else None
    target_engine = None
    for item in (route, adapter, result, return_payload):
        if item is not None and getattr(item, "target_engine", None):
            target_engine = getattr(item, "target_engine")
            break
    dynamic_child = force_dynamic_child_event_created or (
        return_payload is not None
        and (return_payload.creates_new_event or return_payload.requires_child_event)
    ) or (resume is not None and resume.new_child_event_created)
    external_execution = force_external_execution_created or any(
        bool(getattr(item, "external_execution_created", False))
        for item in (adapter, result, return_payload, resume)
        if item is not None
    )
    memory_write = force_memory_layer_write_performed or any(
        bool(getattr(item, "memory_layer_write_performed", False))
        for item in (adapter, result, return_payload, resume)
        if item is not None
    )
    automatic_learning = force_automatic_learning_approval_created or any(
        bool(getattr(item, "automatic_learning_approval_created", False))
        for item in (adapter, result, return_payload, resume)
        if item is not None
    )
    recursive_learning = force_recursive_learning_created or any(
        bool(getattr(item, "recursive_learning_created", False))
        for item in (adapter, result, return_payload, resume)
        if item is not None
    )
    production = force_production_behavior_created or any(
        bool(getattr(item, "production_behavior_created", False))
        for item in (adapter, result, return_payload, resume)
        if item is not None
    )
    thought_behavior = force_thought_engine_behavior_created or (
        route is not None
        and route.target_engine == "thought_engine"
        and adapter is not None
        and adapter.handler_invoked
    )
    forbidden = any(
        (
            dynamic_child,
            force_autonomous_scheduler_created,
            force_open_ended_loop_created,
            external_execution,
            memory_write,
            automatic_learning,
            recursive_learning,
            thought_behavior,
            production,
        )
    )
    resolved_kind = step_kind or _step_kind_from_tick(tick_record)
    if resolved_kind == "power_off_gap":
        resolved_status = "step_recorded_power_off_gap"
    elif resolved_kind == "idle_heartbeat_step":
        resolved_status = "step_recorded_idle"
    elif forbidden:
        resolved_status = "step_blocked_forbidden_authority_detected"
        resolved_kind = "blocked_step"
    elif frame is not None and request is None:
        resolved_status = "step_blocked_missing_dispatch"
    elif result is not None and return_payload is None:
        resolved_status = "step_blocked_missing_return_payload"
    elif return_payload is not None and frame is not None and frame.event_depth > 1 and resume is None:
        resolved_status = "step_blocked_missing_parent_resume"
    elif return_payload is not None and (resume is not None or frame is None or frame.event_depth == 1):
        resolved_status = "step_recorded_event_dispatch_resume"
    else:
        resolved_status = "step_recorded"
    return RuntimeIntegratedEventStepRecord(
        integrated_event_step_id=(
            f"runtime_integrated_event_step:{window.power_window_id}:"
            f"{tick_index if tick_index is not None else (tick_record.tick_index if tick_record else 0)}:"
            f"{_slug(resolved_kind)}"
        ),
        schema_version=INTEGRATED_EVENT_STEP_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_power_window_id=window.power_window_id,
        source_runtime_tick_id=tick_record.runtime_tick_id if tick_record else None,
        source_event_frame_id=frame.event_frame_id if frame else None,
        source_event_stack_id=stack.event_stack_id if stack else None,
        source_dispatch_request_id=request.dispatch_request_id if request else None,
        source_dispatch_route_id=route.dispatch_route_id if route else None,
        source_handler_adapter_id=adapter.handler_adapter_id if adapter else None,
        source_dispatch_result_id=result.dispatch_result_id if result else None,
        source_dispatch_return_payload_id=(
            return_payload.dispatch_return_payload_id if return_payload else None
        ),
        source_parent_resume_id=resume.parent_resume_id if resume else None,
        source_resume_stack_update_id=(
            stack_update.resume_stack_update_id if stack_update else None
        ),
        tick_index=(
            tick_index if tick_index is not None else (tick_record.tick_index if tick_record else 0)
        ),
        timeline_symbol=timeline_symbol or (tick_record.tick_symbol if tick_record else " "),
        event_depth=frame.event_depth if frame else (tick_record.active_event_depth if tick_record else 0),
        event_type=event_type,
        event_family=event_family,
        target_engine=target_engine,
        step_kind=resolved_kind,
        step_status=resolved_status,
        step_summary=_step_summary(resolved_status, event_type, target_engine),
        event_frame_opened=bool(tick_record and tick_record.created_event_frame),
        event_frame_dispatched=request is not None and result is not None,
        return_payload_created=return_payload is not None,
        parent_resume_recorded=resume is not None,
        stack_updated=stack_update is not None
        and not stack_update.stack_update_status.startswith("blocked_"),
        idle_tick=resolved_kind == "idle_heartbeat_step",
        power_off_gap=resolved_kind == "power_off_gap",
        dynamic_child_event_created=dynamic_child,
        autonomous_scheduler_created=force_autonomous_scheduler_created,
        open_ended_loop_created=force_open_ended_loop_created,
        external_execution_created=external_execution,
        memory_layer_write_performed=memory_write,
        automatic_learning_approval_created=automatic_learning,
        recursive_learning_created=recursive_learning,
        thought_engine_behavior_created=thought_behavior,
        production_behavior_created=production,
        source_trace_refs=window.source_trace_refs,
    )


def validate_runtime_integrated_event_step_record(
    record: RuntimeIntegratedEventStepRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _integrated_step(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.power_off_gap and item.source_runtime_tick_id is not None:
        errors.append("power_off_gap_has_tick")
    if item.idle_tick and item.source_event_frame_id is not None:
        errors.append("idle_tick_has_event_frame")
    if item.step_status == "step_recorded_event_dispatch_resume":
        if item.source_event_frame_id is None:
            errors.append("dispatch_resume_step_missing_event_frame")
        if item.source_dispatch_result_id is None:
            errors.append("dispatch_resume_step_missing_dispatch_result")
        if item.source_dispatch_return_payload_id is None:
            errors.append("dispatch_resume_step_missing_return_payload")
    for flag in (
        "dynamic_child_event_created",
        "autonomous_scheduler_created",
        "open_ended_loop_created",
        "external_execution_created",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
        "recursive_learning_created",
        "thought_engine_behavior_created",
        "production_behavior_created",
    ):
        if getattr(item, flag) and item.step_status != "step_blocked_forbidden_authority_detected":
            errors.append(f"{flag}_not_blocked")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "integrated_event_step_id": item.integrated_event_step_id,
        "step_status": item.step_status,
    }


def build_runtime_integrated_dispatch_resume_link_record(
    *,
    event_frame: RuntimeEventFrameRecord | dict[str, object],
    dispatch_request: RuntimeEventDispatchRequestRecord | dict[str, object] | None = None,
    dispatch_route: RuntimeEventDispatchRouteRecord | dict[str, object] | None = None,
    dispatch_result: RuntimeEventDispatchResultRecord | dict[str, object] | None = None,
    dispatch_return_payload: RuntimeEventDispatchReturnPayloadRecord | dict[str, object] | None = None,
    parent_resume: RuntimeParentFrameResumeRecord | dict[str, object] | None = None,
    resume_stack_update: RuntimeParentFrameResumeStackUpdateRecord | dict[str, object] | None = None,
    force_missing_dispatch_result: bool = False,
    force_missing_return_payload: bool = False,
    force_missing_parent_resume: bool = False,
    force_invalid_stack_update: bool = False,
    force_forbidden_authority: bool = False,
) -> RuntimeIntegratedEventDispatchResumeLinkRecord:
    frame = _event_frame(event_frame)
    request = _dispatch_request(dispatch_request) if dispatch_request is not None else None
    route = _dispatch_route(dispatch_route) if dispatch_route is not None else None
    result = _dispatch_result(dispatch_result) if dispatch_result is not None else None
    return_payload = (
        _dispatch_return_payload(dispatch_return_payload)
        if dispatch_return_payload is not None
        else None
    )
    resume = _parent_resume(parent_resume) if parent_resume is not None else None
    stack_update = (
        _resume_stack_update(resume_stack_update)
        if resume_stack_update is not None
        else None
    )
    event_family = route.event_family if route else classify_runtime_event_type(frame.event_type)
    target_engine = (
        route.target_engine
        if route
        else (return_payload.target_engine if return_payload else TARGET_BY_FAMILY[event_family])
    )
    missing_result = force_missing_dispatch_result or result is None
    missing_return = force_missing_return_payload or return_payload is None
    missing_parent = (
        force_missing_parent_resume
        or (frame.event_depth > 1 and resume is None)
    )
    invalid_stack = force_invalid_stack_update or (
        stack_update is not None and stack_update.stack_update_status.startswith("blocked_")
    )
    forbidden = force_forbidden_authority or any(
        bool(getattr(item, "external_execution_created", False))
        or bool(getattr(item, "memory_layer_write_performed", False))
        or bool(getattr(item, "automatic_learning_approval_created", False))
        or bool(getattr(item, "recursive_learning_created", False))
        or bool(getattr(item, "production_behavior_created", False))
        for item in (result, return_payload, resume)
        if item is not None
    ) or (return_payload is not None and return_payload.creates_new_event)
    dispatch_to_return_valid = (
        result is not None
        and return_payload is not None
        and return_payload.source_dispatch_result_id == result.dispatch_result_id
    )
    return_to_parent_valid = (
        frame.event_depth == 1
        and resume is not None
        and resume.resume_status == "root_event_closed"
    ) or (
        frame.event_depth > 1
        and resume is not None
        and resume.source_child_event_frame_id == frame.event_frame_id
        and resume.source_parent_event_frame_id == frame.parent_event_frame_id
    )
    stack_valid = stack_update is not None and not stack_update.stack_update_status.startswith("blocked_")
    if forbidden:
        status = "blocked_forbidden_authority_detected"
    elif missing_result:
        status = "blocked_missing_dispatch_result"
    elif missing_return:
        status = "blocked_missing_return_payload"
    elif missing_parent:
        status = "blocked_missing_parent_resume"
    elif invalid_stack or not stack_valid:
        status = "blocked_invalid_stack_update"
    elif target_engine == "thought_engine" and return_payload and return_payload.return_status == "returned_deferred":
        status = "dispatch_resume_link_deferred_thought_engine"
    elif frame.event_depth == 1 and resume and resume.resume_status == "root_event_closed":
        status = "dispatch_resume_link_valid_root_close"
    else:
        status = "dispatch_resume_link_valid"
    return RuntimeIntegratedEventDispatchResumeLinkRecord(
        dispatch_resume_link_id=(
            f"runtime_integrated_dispatch_resume_link:{frame.event_frame_id}:"
            f"{_slug(status)}"
        ),
        schema_version=INTEGRATED_DISPATCH_RESUME_LINK_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_event_frame_id=frame.event_frame_id,
        source_dispatch_request_id=request.dispatch_request_id if request else None,
        source_dispatch_result_id=result.dispatch_result_id if result else None,
        source_dispatch_return_payload_id=(
            return_payload.dispatch_return_payload_id if return_payload else None
        ),
        source_child_event_frame_id=frame.event_frame_id,
        source_parent_event_frame_id=frame.parent_event_frame_id,
        source_parent_resume_id=resume.parent_resume_id if resume else None,
        source_resume_stack_update_id=(
            stack_update.resume_stack_update_id if stack_update else None
        ),
        event_type=frame.event_type,
        event_family=event_family,
        target_engine=target_engine,
        return_status=return_payload.return_status if return_payload else "returned_unknown",
        parent_resume_status=resume.resume_status if resume else None,
        dispatch_to_return_link_valid=dispatch_to_return_valid,
        return_to_parent_resume_link_valid=return_to_parent_valid,
        stack_update_link_valid=stack_valid,
        link_status=status,
        link_summary=_link_summary(status, frame.event_type, target_engine),
        external_execution_created=any(
            bool(getattr(item, "external_execution_created", False))
            for item in (result, return_payload, resume)
            if item is not None
        ),
        memory_layer_write_performed=any(
            bool(getattr(item, "memory_layer_write_performed", False))
            for item in (result, return_payload, resume)
            if item is not None
        ),
        automatic_learning_approval_created=any(
            bool(getattr(item, "automatic_learning_approval_created", False))
            for item in (result, return_payload, resume)
            if item is not None
        ),
        recursive_learning_created=any(
            bool(getattr(item, "recursive_learning_created", False))
            for item in (result, return_payload, resume)
            if item is not None
        ),
        production_behavior_created=any(
            bool(getattr(item, "production_behavior_created", False))
            for item in (result, return_payload, resume)
            if item is not None
        ),
        source_trace_refs=frame.source_trace_refs,
    )


def validate_runtime_integrated_dispatch_resume_link_record(
    record: RuntimeIntegratedEventDispatchResumeLinkRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _dispatch_resume_link(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.link_status in {
        "dispatch_resume_link_valid",
        "dispatch_resume_link_valid_root_close",
        "dispatch_resume_link_deferred_thought_engine",
    }:
        if not item.dispatch_to_return_link_valid:
            errors.append("dispatch_to_return_link_invalid")
        if not item.return_to_parent_resume_link_valid:
            errors.append("return_to_parent_resume_link_invalid")
        if not item.stack_update_link_valid:
            errors.append("stack_update_link_invalid")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "dispatch_resume_link_id": item.dispatch_resume_link_id,
        "link_status": item.link_status,
    }


def build_runtime_integrated_event_loop_trace(
    *,
    power_window: RuntimePowerWindowRecord | dict[str, object],
    ticks: tuple[RuntimeTickRecord, ...] | list[RuntimeTickRecord | dict[str, object]],
    event_frames: tuple[RuntimeEventFrameRecord, ...] | list[RuntimeEventFrameRecord | dict[str, object]],
    event_stacks: tuple[RuntimeEventStackRecord, ...] | list[RuntimeEventStackRecord | dict[str, object]],
    event_tree: RuntimeEventTreeRecord | dict[str, object] | None,
    continuous_loop_trace: RuntimeContinuousLoopTrace | dict[str, object] | None = None,
    continuous_loop_audit: RuntimeContinuousLoopAudit | dict[str, object] | None = None,
    integrated_event_steps: tuple[RuntimeIntegratedEventStepRecord, ...] | list[RuntimeIntegratedEventStepRecord | dict[str, object]] = (),
    dispatch_resume_links: tuple[RuntimeIntegratedEventDispatchResumeLinkRecord, ...] | list[RuntimeIntegratedEventDispatchResumeLinkRecord | dict[str, object]] = (),
    dispatch_audits: tuple[RuntimeEventDispatchAudit, ...] | list[RuntimeEventDispatchAudit | dict[str, object]] = (),
    parent_resume_audits: tuple[RuntimeParentFrameResumeAudit, ...] | list[RuntimeParentFrameResumeAudit | dict[str, object]] = (),
    parent_resumes: tuple[RuntimeParentFrameResumeRecord, ...] | list[RuntimeParentFrameResumeRecord | dict[str, object]] = (),
    resume_stack_updates: tuple[RuntimeParentFrameResumeStackUpdateRecord, ...] | list[RuntimeParentFrameResumeStackUpdateRecord | dict[str, object]] = (),
    force_missing_dispatch: bool = False,
    force_missing_return: bool = False,
    force_missing_parent_resume: bool = False,
    force_invalid_stack: bool = False,
    force_unclosed_frame: bool = False,
    force_dynamic_child_event_created: bool = False,
    force_autonomous_scheduler_created: bool = False,
    force_open_ended_loop_created: bool = False,
    force_external_execution_created: bool = False,
    force_memory_layer_write_performed: bool = False,
    force_automatic_learning_approval_created: bool = False,
    force_recursive_learning_created: bool = False,
    force_thought_engine_behavior_created: bool = False,
    force_production_behavior_created: bool = False,
) -> RuntimeIntegratedEventLoopTrace:
    window = _power_window(power_window)
    tick_records = tuple(_tick(item) for item in ticks)
    frames = tuple(_event_frame(item) for item in event_frames)
    stacks = tuple(_event_stack(item) for item in event_stacks)
    tree = _event_tree(event_tree) if event_tree is not None else None
    loop_trace = _loop_trace(continuous_loop_trace) if continuous_loop_trace else None
    loop_audit = _loop_audit(continuous_loop_audit) if continuous_loop_audit else None
    steps = tuple(_integrated_step(item) for item in integrated_event_steps)
    links = tuple(_dispatch_resume_link(item) for item in dispatch_resume_links)
    dispatch_audit_records = tuple(_dispatch_audit(item) for item in dispatch_audits)
    parent_audit_records = tuple(_parent_resume_audit(item) for item in parent_resume_audits)
    resume_records = tuple(_parent_resume(item) for item in parent_resumes)
    update_records = tuple(_resume_stack_update(item) for item in resume_stack_updates)

    frame_ids = {frame.event_frame_id for frame in frames}
    linked_frame_ids = {link.source_event_frame_id for link in links}
    missing_dispatch = force_missing_dispatch or bool(frame_ids - linked_frame_ids) or any(
        link.link_status == "blocked_missing_dispatch_result" for link in links
    )
    missing_return = force_missing_return or any(
        link.link_status == "blocked_missing_return_payload" for link in links
    )
    missing_parent_resume = force_missing_parent_resume or any(
        link.link_status == "blocked_missing_parent_resume" for link in links
    )
    invalid_stack = force_invalid_stack or any(
        link.link_status == "blocked_invalid_stack_update"
        or update.stack_update_status.startswith("blocked_")
        for link in links
        for update in update_records[:1] or ()
    ) or any(update.stack_update_status.startswith("blocked_") for update in update_records)
    unclosed_frame = force_unclosed_frame or any(frame.unclosed_frame_detected for frame in frames)
    dynamic_child = force_dynamic_child_event_created or any(
        step.dynamic_child_event_created for step in steps
    )
    external_execution = force_external_execution_created or any(
        link.external_execution_created for link in links
    ) or any(step.external_execution_created for step in steps)
    memory_write = force_memory_layer_write_performed or any(
        link.memory_layer_write_performed for link in links
    ) or any(step.memory_layer_write_performed for step in steps)
    automatic_learning = force_automatic_learning_approval_created or any(
        link.automatic_learning_approval_created for link in links
    ) or any(step.automatic_learning_approval_created for step in steps)
    recursive_learning = force_recursive_learning_created or any(
        link.recursive_learning_created for link in links
    ) or any(step.recursive_learning_created for step in steps)
    production = force_production_behavior_created or any(
        link.production_behavior_created for link in links
    ) or any(step.production_behavior_created for step in steps)
    thought_behavior = force_thought_engine_behavior_created or any(
        step.thought_engine_behavior_created for step in steps
    )
    has_deferred_thought = any(
        link.link_status == "dispatch_resume_link_deferred_thought_engine"
        for link in links
    )
    forbidden = any(
        (
            dynamic_child,
            force_autonomous_scheduler_created,
            force_open_ended_loop_created,
            external_execution,
            memory_write,
            automatic_learning,
            recursive_learning,
            thought_behavior,
            production,
        )
    )
    if forbidden:
        status = "integrated_event_loop_trace_blocked_forbidden_authority_detected"
    elif missing_dispatch:
        status = "integrated_event_loop_trace_blocked_missing_dispatch"
    elif missing_return:
        status = "integrated_event_loop_trace_blocked_missing_return"
    elif missing_parent_resume:
        status = "integrated_event_loop_trace_blocked_missing_parent_resume"
    elif invalid_stack:
        status = "integrated_event_loop_trace_blocked_invalid_stack"
    elif unclosed_frame:
        status = "integrated_event_loop_trace_blocked_unclosed_frame"
    elif has_deferred_thought:
        status = "integrated_event_loop_trace_complete_with_deferred_thought"
    elif window.power_off_spans_observed:
        status = "integrated_event_loop_trace_complete_with_power_off_gaps"
    else:
        status = "integrated_event_loop_trace_complete"
    canonical = normalize_runtime_timeline_text(window.timeline_text)
    return RuntimeIntegratedEventLoopTrace(
        integrated_loop_trace_id=f"runtime_integrated_event_loop_trace:{window.power_window_id}",
        schema_version=INTEGRATED_LOOP_TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_power_window_id=window.power_window_id,
        source_continuous_loop_trace_id=loop_trace.continuous_loop_trace_id if loop_trace else None,
        source_event_tree_id=tree.event_tree_id if tree else None,
        source_continuous_loop_audit_id=(
            loop_audit.continuous_loop_audit_id if loop_audit else None
        ),
        source_dispatch_audit_ids=tuple(
            audit.dispatch_audit_id for audit in dispatch_audit_records
        ),
        source_parent_resume_audit_ids=tuple(
            audit.parent_resume_audit_id for audit in parent_audit_records
        ),
        integrated_event_step_ids=tuple(step.integrated_event_step_id for step in steps),
        dispatch_resume_link_ids=tuple(link.dispatch_resume_link_id for link in links),
        timeline_text=window.timeline_text,
        canonical_timeline_text=canonical,
        rendered_timeline_text=render_integrated_loop_tree_text(
            canonical_timeline_text=canonical,
            event_frames=frames,
            links=links,
        ),
        tick_count=len(tick_records),
        idle_tick_count=sum(1 for tick in tick_records if tick.tick_kind == "idle_heartbeat"),
        event_tick_count=sum(
            1
            for tick in tick_records
            if tick.tick_kind in {"event_frame_tick", "event_return_tick"}
        ),
        power_off_gap_count=window.power_off_spans_observed,
        event_frame_count=len(frames),
        dispatch_count=sum(
            1 for link in links if link.source_dispatch_result_id is not None
        ),
        return_payload_count=sum(
            1 for link in links if link.source_dispatch_return_payload_id is not None
        ),
        parent_resume_count=len(resume_records),
        stack_update_count=len(update_records),
        max_event_depth_observed=max((frame.event_depth for frame in frames), default=0),
        all_event_frames_dispatched_or_idle=not missing_dispatch,
        all_dispatches_returned=not missing_return,
        all_child_returns_resumed=not missing_parent_resume,
        all_event_frames_closed_or_validly_deferred=not unclosed_frame and not invalid_stack,
        integrated_trace_status=status,
        integrated_trace_summary=_trace_summary(status),
        dynamic_child_event_created=dynamic_child,
        autonomous_scheduler_created=force_autonomous_scheduler_created,
        open_ended_loop_created=force_open_ended_loop_created,
        external_execution_created=external_execution,
        memory_layer_write_performed=memory_write,
        automatic_learning_approval_created=automatic_learning,
        recursive_learning_created=recursive_learning,
        thought_engine_behavior_created=thought_behavior,
        production_behavior_created=production,
        source_trace_refs=window.source_trace_refs,
    )


def validate_runtime_integrated_event_loop_trace(
    record: RuntimeIntegratedEventLoopTrace | dict[str, object],
) -> dict[str, object]:
    try:
        item = _integrated_trace(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.event_frame_count and not item.all_event_frames_dispatched_or_idle:
        errors.append("event_frames_missing_dispatch")
    if item.dispatch_count and not item.all_dispatches_returned:
        errors.append("dispatches_missing_return")
    if not item.all_child_returns_resumed:
        errors.append("child_returns_missing_resume")
    for flag in (
        "dynamic_child_event_created",
        "autonomous_scheduler_created",
        "open_ended_loop_created",
        "external_execution_created",
        "memory_layer_write_performed",
        "automatic_learning_approval_created",
        "recursive_learning_created",
        "thought_engine_behavior_created",
        "production_behavior_created",
    ):
        if getattr(item, flag) and item.integrated_trace_status != "integrated_event_loop_trace_blocked_forbidden_authority_detected":
            errors.append(f"{flag}_not_blocked")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "integrated_loop_trace_id": item.integrated_loop_trace_id,
        "integrated_trace_status": item.integrated_trace_status,
    }


def build_runtime_integrated_event_loop_timeline_render(
    integrated_loop_trace: RuntimeIntegratedEventLoopTrace | dict[str, object],
) -> RuntimeIntegratedEventLoopTimelineRenderRecord:
    trace = _integrated_trace(integrated_loop_trace)
    if trace.integrated_trace_status.startswith("integrated_event_loop_trace_blocked"):
        status = "timeline_render_blocked_invalid_trace"
    elif trace.integrated_trace_status == "integrated_event_loop_trace_complete_with_deferred_thought":
        status = "timeline_render_created_with_deferred_thought"
    else:
        status = "timeline_render_created"
    compact = (
        f"ticks={trace.tick_count}",
        f"events={trace.event_frame_count}",
        f"dispatches={trace.dispatch_count}",
        f"returns={trace.return_payload_count}",
        f"parent_resumes={trace.parent_resume_count}",
        f"status={trace.integrated_trace_status}",
    )
    return RuntimeIntegratedEventLoopTimelineRenderRecord(
        integrated_timeline_render_id=f"runtime_integrated_event_loop_timeline_render:{trace.integrated_loop_trace_id}",
        schema_version=INTEGRATED_TIMELINE_RENDER_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_integrated_loop_trace_id=trace.integrated_loop_trace_id,
        timeline_text=trace.timeline_text,
        canonical_timeline_text=trace.canonical_timeline_text,
        human_readable_tree_text=trace.rendered_timeline_text,
        compact_step_summary=compact,
        legend={
            "space": "power_off_gap",
            ".": "idle_heartbeat",
            "1": "event_depth_1",
            "2": "event_depth_2",
            "3": "event_depth_3",
            "4": "event_depth_4",
            "D": "dispatch",
            "R": "return",
            "P": "parent_resume",
            "S": "stack_update",
        },
        render_status=status,
        render_summary=_render_summary(status),
        source_trace_refs=trace.source_trace_refs,
    )


def validate_runtime_integrated_event_loop_timeline_render(
    record: RuntimeIntegratedEventLoopTimelineRenderRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _timeline_render(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    for key in ("space", ".", "1", "2", "3", "4", "D", "R", "P", "S"):
        if key not in item.legend:
            errors.append(f"missing_legend:{key}")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "integrated_timeline_render_id": item.integrated_timeline_render_id,
        "render_status": item.render_status,
    }


def build_runtime_integrated_event_loop_audit(
    *,
    integrated_loop_trace: RuntimeIntegratedEventLoopTrace | dict[str, object] | None = None,
    timeline_render: RuntimeIntegratedEventLoopTimelineRenderRecord | dict[str, object] | None = None,
    power_window: RuntimePowerWindowRecord | dict[str, object] | None = None,
    ticks: tuple[RuntimeTickRecord, ...] | list[RuntimeTickRecord | dict[str, object]] = (),
    event_frames: tuple[RuntimeEventFrameRecord, ...] | list[RuntimeEventFrameRecord | dict[str, object]] = (),
    event_stacks: tuple[RuntimeEventStackRecord, ...] | list[RuntimeEventStackRecord | dict[str, object]] = (),
    event_tree: RuntimeEventTreeRecord | dict[str, object] | None = None,
    dispatch_resume_links: tuple[RuntimeIntegratedEventDispatchResumeLinkRecord, ...] | list[RuntimeIntegratedEventDispatchResumeLinkRecord | dict[str, object]] = (),
    force_invalid_power_window: bool = False,
    force_invalid_tick_lineage: bool = False,
    force_dynamic_child_event_scheduling: bool = False,
    force_autonomous_scheduler: bool = False,
    force_open_ended_loop: bool = False,
    force_external_execution: bool = False,
    force_memory_write: bool = False,
    force_automatic_learning_approval: bool = False,
    force_recursive_learning: bool = False,
    force_thought_engine_fake: bool = False,
    force_production_behavior: bool = False,
) -> RuntimeIntegratedEventLoopAudit:
    trace = _integrated_trace(integrated_loop_trace) if integrated_loop_trace is not None else None
    render = _timeline_render(timeline_render) if timeline_render is not None else None
    window = _power_window(power_window) if power_window is not None else None
    tick_records = tuple(_tick(item) for item in ticks)
    frame_records = tuple(_event_frame(item) for item in event_frames)
    stack_records = tuple(_event_stack(item) for item in event_stacks)
    tree = _event_tree(event_tree) if event_tree is not None else None
    links = tuple(_dispatch_resume_link(item) for item in dispatch_resume_links)
    blocked_reasons = _integrated_audit_blocked_reasons(
        trace=trace,
        window=window,
        ticks=tick_records,
        frames=frame_records,
        stacks=stack_records,
        tree=tree,
        links=links,
        force_invalid_power_window=force_invalid_power_window,
        force_invalid_tick_lineage=force_invalid_tick_lineage,
        force_dynamic_child_event_scheduling=force_dynamic_child_event_scheduling,
        force_autonomous_scheduler=force_autonomous_scheduler,
        force_open_ended_loop=force_open_ended_loop,
        force_external_execution=force_external_execution,
        force_memory_write=force_memory_write,
        force_automatic_learning_approval=force_automatic_learning_approval,
        force_recursive_learning=force_recursive_learning,
        force_thought_engine_fake=force_thought_engine_fake,
        force_production_behavior=force_production_behavior,
    )
    audit_status = _integrated_audit_status(trace, blocked_reasons)
    return RuntimeIntegratedEventLoopAudit(
        integrated_loop_audit_id=f"runtime_integrated_event_loop_audit:{_slug(audit_status)}",
        schema_version=INTEGRATED_LOOP_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_integrated_loop_trace_id=trace.integrated_loop_trace_id if trace else None,
        source_timeline_render_id=render.integrated_timeline_render_id if render else None,
        power_window_valid="invalid_power_window" not in blocked_reasons,
        tick_lineage_valid="invalid_tick_lineage" not in blocked_reasons,
        event_frame_lineage_valid=bool(frame_records) or trace is None,
        event_stack_lineage_valid="invalid_stack_update" not in blocked_reasons,
        event_tree_valid="unclosed_root_frame" not in blocked_reasons,
        dispatch_lineage_valid="missing_dispatch_lineage" not in blocked_reasons,
        dispatch_return_payload_valid="missing_return_payload" not in blocked_reasons,
        parent_resume_lineage_valid="missing_parent_resume" not in blocked_reasons,
        stack_update_lineage_valid="invalid_stack_update" not in blocked_reasons,
        all_events_dispatched_or_validly_deferred=trace is not None
        and trace.all_event_frames_dispatched_or_idle,
        all_dispatches_returned=trace is not None and trace.all_dispatches_returned,
        all_child_returns_resumed=trace is not None and trace.all_child_returns_resumed,
        all_root_frames_closed=trace is not None
        and trace.all_event_frames_closed_or_validly_deferred,
        bounded_window_confirmed=True,
        adapter_only_confirmed=True,
        record_only_confirmed=True,
        no_dynamic_child_event_scheduling=(
            "dynamic_child_event_scheduling_detected" not in blocked_reasons
        ),
        no_autonomous_scheduler="autonomous_scheduler_detected" not in blocked_reasons,
        no_open_ended_loop="open_ended_loop_detected" not in blocked_reasons,
        no_background_daemon=True,
        no_external_execution="external_execution_detected" not in blocked_reasons,
        no_unity_execution=True,
        no_bridge_execution=True,
        no_network_execution=True,
        no_filesystem_execution=True,
        no_memory_layer_write="memory_write_detected" not in blocked_reasons,
        no_core_memory_write=True,
        no_long_term_memory_write=True,
        no_archive_memory_write=True,
        no_anchor_write=True,
        no_automatic_learning_approval=(
            "automatic_learning_approval_detected" not in blocked_reasons
        ),
        no_free_action_selection=True,
        no_recursive_learning="recursive_learning_detected" not in blocked_reasons,
        no_thought_engine_behavior="thought_engine_fake_detected" not in blocked_reasons,
        no_production_behavior="production_behavior_detected" not in blocked_reasons,
        audit_status=audit_status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(blocked_reasons),
        source_trace_refs=trace.source_trace_refs if trace else tuple(),
    )


def validate_runtime_integrated_event_loop_audit(
    record: RuntimeIntegratedEventLoopAudit | dict[str, object],
) -> dict[str, object]:
    try:
        item = _integrated_audit(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    if item.audit_status.startswith("passed_"):
        required = (
            item.power_window_valid,
            item.tick_lineage_valid,
            item.dispatch_lineage_valid,
            item.dispatch_return_payload_valid,
            item.parent_resume_lineage_valid,
            item.stack_update_lineage_valid,
            item.no_dynamic_child_event_scheduling,
            item.no_external_execution,
            item.no_memory_layer_write,
            item.no_automatic_learning_approval,
            item.no_recursive_learning,
            item.no_thought_engine_behavior,
            item.no_production_behavior,
        )
        if not all(required):
            errors.append("passed_audit_has_failed_boundary")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "integrated_loop_audit_id": item.integrated_loop_audit_id,
        "audit_status": item.audit_status,
    }


def build_runtime_integrated_event_loop_readiness(
    integrated_loop_audit: RuntimeIntegratedEventLoopAudit | dict[str, object],
) -> RuntimeIntegratedEventLoopReadinessRecord:
    audit = _integrated_audit(integrated_loop_audit)
    if audit.audit_status.startswith("passed_"):
        status = "ready_for_fixed_runtime_playback_only"
        handler_ready = True
        playback_ready = True
    elif "forbidden" in audit.audit_status or any(
        reason.endswith("detected") for reason in audit.blocked_reasons
    ):
        status = "blocked_forbidden_authority_detected"
        handler_ready = False
        playback_ready = False
    elif audit.source_integrated_loop_trace_id is None:
        status = "not_ready_missing_integrated_loop_trace"
        handler_ready = False
        playback_ready = False
    else:
        status = "not_ready_boundary_failure"
        handler_ready = False
        playback_ready = False
    return RuntimeIntegratedEventLoopReadinessRecord(
        integrated_loop_readiness_id=f"runtime_integrated_event_loop_readiness:{audit.integrated_loop_audit_id}",
        schema_version=INTEGRATED_LOOP_READINESS_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_integrated_loop_audit_id=audit.integrated_loop_audit_id,
        current_verified_capability=SAFE_CLAIM,
        recommended_next_package=READINESS_NEXT_PACKAGE,
        recommended_next_reason=(
            "Run the already verified Package 94 closed loop as fixed bounded "
            "playback inside Runtime EventFrames without dynamic scheduling."
        ),
        ready_for_bounded_runtime_handler_binding=handler_ready,
        ready_for_fixed_runtime_playback_of_existing_closed_loop=playback_ready,
        ready_for_dynamic_child_event_scheduling=False,
        ready_for_autonomous_scheduler=False,
        ready_for_open_ended_loop=False,
        ready_for_external_execution=False,
        ready_for_memory_layer_write=False,
        ready_for_automatic_learning_approval=False,
        ready_for_recursive_learning=False,
        ready_for_thought_engine_runtime=False,
        ready_for_first_output=False,
        readiness_status=status,
        readiness_summary=_readiness_summary(status),
        source_trace_refs=audit.source_trace_refs,
    )


def validate_runtime_integrated_event_loop_readiness(
    record: RuntimeIntegratedEventLoopReadinessRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _readiness(record)
    except Exception as error:  # pragma: no cover - schema guard
        return {"valid": False, "error": str(error)}
    errors: list[str] = []
    for flag in (
        "ready_for_dynamic_child_event_scheduling",
        "ready_for_autonomous_scheduler",
        "ready_for_open_ended_loop",
        "ready_for_external_execution",
        "ready_for_memory_layer_write",
        "ready_for_automatic_learning_approval",
        "ready_for_recursive_learning",
        "ready_for_thought_engine_runtime",
        "ready_for_first_output",
    ):
        if getattr(item, flag):
            errors.append(f"{flag}_true")
    return {
        "valid": not errors,
        "error_codes": tuple(errors),
        "integrated_loop_readiness_id": item.integrated_loop_readiness_id,
        "readiness_status": item.readiness_status,
    }


def build_integrated_trace_from_demo_timeline(
    timeline_text: str,
    *,
    event_types_by_depth: dict[int, str] | None = None,
    force_missing_dispatch: bool = False,
    force_missing_parent_resume: bool = False,
    force_dynamic_scheduling: bool = False,
    force_forbidden_authority: bool = False,
    force_unclosed_frame: bool = False,
    force_invalid_stack: bool = False,
) -> dict[str, object]:
    event_types = event_types_by_depth or {
        1: "task_trial",
        2: "action_chain",
        3: "sense_observation",
        4: "outcome_evaluation",
    }
    power_window = build_runtime_power_window_record(
        timeline_text=timeline_text,
        source_trace_refs=("runtime_integrated_event_loop_demo",),
    )
    ticks = build_runtime_tick_records_from_timeline(power_window=power_window)
    frames = tuple(
        _retarget_frame_type(frame, event_types.get(frame.event_depth, frame.event_type))
        for frame in build_runtime_event_frames_from_timeline(
            power_window=power_window,
            leave_unclosed_at_end=force_unclosed_frame,
        )
    )
    returns = build_runtime_event_return_records(power_window=power_window)
    stacks = build_runtime_event_stack_records(
        power_window=power_window,
        invalid_parent_child_order_detected=force_invalid_stack,
        unclosed_frame_detected=force_unclosed_frame,
    )
    tree = build_runtime_event_tree_record(
        power_window=power_window,
        event_frames=frames,
        event_returns=returns,
    )
    loop_trace = build_runtime_continuous_loop_trace(
        power_window=power_window,
        ticks=ticks,
        event_frames=frames,
        event_stacks=stacks,
        event_returns=returns,
        event_tree=tree,
        forbidden_authority_detected=force_forbidden_authority,
    )
    loop_audit = build_runtime_continuous_loop_audit(
        loop_trace=loop_trace,
        event_tree=tree,
        ticks=ticks,
        event_frames=frames,
        event_stacks=stacks,
        event_returns=returns,
        memory_layer_write_performed=force_forbidden_authority,
    )
    frame_by_id = {frame.event_frame_id: frame for frame in frames}
    frame_by_depth = {frame.event_depth: frame for frame in frames}
    dispatch_requests: list[RuntimeEventDispatchRequestRecord] = []
    dispatch_routes: list[RuntimeEventDispatchRouteRecord] = []
    handler_adapters: list[RuntimeEventHandlerAdapterRecord] = []
    dispatch_results: list[RuntimeEventDispatchResultRecord] = []
    return_payloads: list[RuntimeEventDispatchReturnPayloadRecord] = []
    dispatch_audits: list[RuntimeEventDispatchAudit] = []
    return_payload_by_frame: dict[str, RuntimeEventDispatchReturnPayloadRecord] = {}

    for index, frame in enumerate(frames):
        if force_missing_dispatch and index == 0:
            continue
        dispatch_payload = dispatch_event_frame_adapter_only(frame)
        request = RuntimeEventDispatchRequestRecord.from_dict(
            dispatch_payload["runtime_event_dispatch_request"]
        )
        route = RuntimeEventDispatchRouteRecord.from_dict(
            dispatch_payload["runtime_event_dispatch_route"]
        )
        adapter = RuntimeEventHandlerAdapterRecord.from_dict(
            dispatch_payload["runtime_event_handler_adapter"]
        )
        result = RuntimeEventDispatchResultRecord.from_dict(
            dispatch_payload["runtime_event_dispatch_result"]
        )
        return_payload = RuntimeEventDispatchReturnPayloadRecord.from_dict(
            dispatch_payload["runtime_event_dispatch_return_payload"]
        )
        if force_dynamic_scheduling and index == len(frames) - 1:
            return_payload = replace(
                return_payload,
                creates_new_event=True,
                requires_child_event=True,
            )
        if force_forbidden_authority and index == 0:
            return_payload = replace(return_payload, memory_layer_write_performed=True)
        audit = RuntimeEventDispatchAudit.from_dict(
            dispatch_payload["runtime_event_dispatch_audit"]
        )
        dispatch_requests.append(request)
        dispatch_routes.append(route)
        handler_adapters.append(adapter)
        dispatch_results.append(result)
        return_payloads.append(return_payload)
        dispatch_audits.append(audit)
        return_payload_by_frame[frame.event_frame_id] = return_payload

    resume_requests: list[RuntimeParentFrameResumeRequestRecord] = []
    resume_decisions: list[RuntimeParentFrameResumeDecisionRecord] = []
    parent_resumes: list[RuntimeParentFrameResumeRecord] = []
    stack_updates: list[RuntimeParentFrameResumeStackUpdateRecord] = []
    parent_resume_audits: list[RuntimeParentFrameResumeAudit] = []
    parent_resume_by_frame: dict[str, RuntimeParentFrameResumeRecord] = {}
    stack_update_by_frame: dict[str, RuntimeParentFrameResumeStackUpdateRecord] = {}
    skipped_missing_parent = False

    for frame in sorted(frames, key=lambda item: item.event_depth, reverse=True):
        return_payload = return_payload_by_frame.get(frame.event_frame_id)
        if return_payload is None:
            continue
        if (
            force_missing_parent_resume
            and frame.event_depth > 1
            and not skipped_missing_parent
        ):
            skipped_missing_parent = True
            continue
        parent = (
            frame_by_id.get(frame.parent_event_frame_id)
            if frame.parent_event_frame_id
            else None
        )
        stack_before_resume = tuple(
            frame_by_depth[depth].event_frame_id
            for depth in range(1, frame.event_depth + 1)
            if depth in frame_by_depth
        )
        resume_payload = resume_parent_frame_from_child_return(
            frame,
            parent_event_frame=parent,
            dispatch_return_payload=return_payload,
            request_payload=(
                {"memory_layer_write_requested": True}
                if force_forbidden_authority and frame.event_depth == 1
                else None
            ),
            stack_before_resume=stack_before_resume,
        )
        request = RuntimeParentFrameResumeRequestRecord.from_dict(
            resume_payload["runtime_parent_frame_resume_request"]
        )
        decision = RuntimeParentFrameResumeDecisionRecord.from_dict(
            resume_payload["runtime_parent_frame_resume_decision"]
        )
        resume = RuntimeParentFrameResumeRecord.from_dict(
            resume_payload["runtime_parent_frame_resume"]
        )
        stack_update = RuntimeParentFrameResumeStackUpdateRecord.from_dict(
            resume_payload["runtime_parent_frame_resume_stack_update"]
        )
        audit = RuntimeParentFrameResumeAudit.from_dict(
            resume_payload["runtime_parent_frame_resume_audit"]
        )
        if force_invalid_stack and frame.event_depth == max(frame_by_depth):
            stack_update = replace(
                stack_update,
                stack_update_status="blocked_invalid_parent_child_order",
                invalid_parent_child_order_detected=True,
            )
        resume_requests.append(request)
        resume_decisions.append(decision)
        parent_resumes.append(resume)
        stack_updates.append(stack_update)
        parent_resume_audits.append(audit)
        parent_resume_by_frame[frame.event_frame_id] = resume
        stack_update_by_frame[frame.event_frame_id] = stack_update

    links: list[RuntimeIntegratedEventDispatchResumeLinkRecord] = []
    for index, frame in enumerate(frames):
        matching_request = _record_for_frame(dispatch_requests, frame.event_frame_id)
        matching_route = _record_for_frame(dispatch_routes, frame.event_frame_id)
        matching_result = _record_for_frame(dispatch_results, frame.event_frame_id)
        matching_return = return_payload_by_frame.get(frame.event_frame_id)
        link = build_runtime_integrated_dispatch_resume_link_record(
            event_frame=frame,
            dispatch_request=matching_request,
            dispatch_route=matching_route,
            dispatch_result=matching_result,
            dispatch_return_payload=matching_return,
            parent_resume=parent_resume_by_frame.get(frame.event_frame_id),
            resume_stack_update=stack_update_by_frame.get(frame.event_frame_id),
            force_missing_dispatch_result=force_missing_dispatch and index == 0,
            force_missing_parent_resume=(
                force_missing_parent_resume
                and frame.event_depth > 1
                and parent_resume_by_frame.get(frame.event_frame_id) is None
            ),
            force_invalid_stack_update=(
                force_invalid_stack
                and stack_update_by_frame.get(frame.event_frame_id) is not None
                and stack_update_by_frame[frame.event_frame_id].stack_update_status.startswith("blocked_")
            ),
        )
        links.append(link)

    steps = _build_integrated_steps(
        power_window=power_window,
        ticks=ticks,
        frames=frames,
        stacks=stacks,
        dispatch_requests=dispatch_requests,
        dispatch_routes=dispatch_routes,
        handler_adapters=handler_adapters,
        dispatch_results=dispatch_results,
        return_payloads=return_payloads,
        parent_resumes=parent_resumes,
        stack_updates=stack_updates,
        force_dynamic_scheduling=force_dynamic_scheduling,
        force_forbidden_authority=force_forbidden_authority,
    )
    nested_trace = build_runtime_nested_return_resume_trace(
        parent_resumes=tuple(parent_resumes),
        stack_updates=tuple(stack_updates),
        event_frames=frames,
        loop_trace=loop_trace,
        event_tree=tree,
        force_missing_parent_resume=force_missing_parent_resume,
        force_forbidden_authority=force_forbidden_authority,
    )
    nested_audit = build_runtime_parent_frame_resume_audit(
        nested_return_resume_trace=nested_trace,
        parent_resume=parent_resumes[0] if parent_resumes else None,
        resume_stack_update=stack_updates[0] if stack_updates else None,
    )
    parent_resume_audits.append(nested_audit)
    trace = build_runtime_integrated_event_loop_trace(
        power_window=power_window,
        ticks=ticks,
        event_frames=frames,
        event_stacks=stacks,
        event_tree=tree,
        continuous_loop_trace=loop_trace,
        continuous_loop_audit=loop_audit,
        integrated_event_steps=steps,
        dispatch_resume_links=links,
        dispatch_audits=dispatch_audits,
        parent_resume_audits=parent_resume_audits,
        parent_resumes=parent_resumes,
        resume_stack_updates=stack_updates,
        force_missing_dispatch=force_missing_dispatch,
        force_missing_parent_resume=force_missing_parent_resume,
        force_invalid_stack=force_invalid_stack,
        force_unclosed_frame=force_unclosed_frame,
        force_dynamic_child_event_created=force_dynamic_scheduling,
        force_memory_layer_write_performed=force_forbidden_authority,
    )
    render = build_runtime_integrated_event_loop_timeline_render(trace)
    audit = build_runtime_integrated_event_loop_audit(
        integrated_loop_trace=trace,
        timeline_render=render,
        power_window=power_window,
        ticks=ticks,
        event_frames=frames,
        event_stacks=stacks,
        event_tree=tree,
        dispatch_resume_links=links,
        force_dynamic_child_event_scheduling=force_dynamic_scheduling,
        force_memory_write=force_forbidden_authority,
    )
    readiness = build_runtime_integrated_event_loop_readiness(audit)
    return {
        "runtime_power_window": power_window.to_dict(),
        "runtime_ticks": [tick.to_dict() for tick in ticks],
        "runtime_event_frames": [frame.to_dict() for frame in frames],
        "runtime_event_stacks": [stack.to_dict() for stack in stacks],
        "runtime_event_returns": [item.to_dict() for item in returns],
        "runtime_event_tree": tree.to_dict(),
        "runtime_continuous_loop_trace": loop_trace.to_dict(),
        "runtime_continuous_loop_audit": loop_audit.to_dict(),
        "runtime_event_dispatch_requests": [item.to_dict() for item in dispatch_requests],
        "runtime_event_dispatch_routes": [item.to_dict() for item in dispatch_routes],
        "runtime_event_handler_adapters": [item.to_dict() for item in handler_adapters],
        "runtime_event_dispatch_results": [item.to_dict() for item in dispatch_results],
        "runtime_event_dispatch_return_payloads": [
            item.to_dict() for item in return_payloads
        ],
        "runtime_event_dispatch_audits": [item.to_dict() for item in dispatch_audits],
        "runtime_parent_frame_resume_requests": [
            item.to_dict() for item in resume_requests
        ],
        "runtime_parent_frame_resume_decisions": [
            item.to_dict() for item in resume_decisions
        ],
        "runtime_parent_frame_resumes": [item.to_dict() for item in parent_resumes],
        "runtime_parent_frame_resume_stack_updates": [
            item.to_dict() for item in stack_updates
        ],
        "runtime_parent_frame_resume_audits": [
            item.to_dict() for item in parent_resume_audits
        ],
        "runtime_nested_return_resume_trace": nested_trace.to_dict(),
        "runtime_integrated_event_steps": [item.to_dict() for item in steps],
        "runtime_integrated_dispatch_resume_links": [item.to_dict() for item in links],
        "runtime_integrated_event_loop_trace": trace.to_dict(),
        "runtime_integrated_event_loop_timeline_render": render.to_dict(),
        "runtime_integrated_event_loop_audit": audit.to_dict(),
        "runtime_integrated_event_loop_readiness": readiness.to_dict(),
        "rendered_integrated_loop_summary": render_integrated_loop_summary_text(trace, audit, readiness),
        "rendered_integrated_loop_tree": render.human_readable_tree_text,
    }


def build_demo_simple_task_dispatch_resume_trace() -> dict[str, object]:
    return build_integrated_trace_from_demo_timeline(
        SIMPLE_TASK_TIMELINE,
        event_types_by_depth={1: "candidate_ordering"},
    )


def build_demo_nested_sense_under_task_integrated_trace() -> dict[str, object]:
    return build_integrated_trace_from_demo_timeline(
        NESTED_SENSE_TIMELINE,
        event_types_by_depth={1: "task_trial", 2: "sense_observation"},
    )


def build_demo_four_level_integrated_dispatch_resume_trace() -> dict[str, object]:
    return build_integrated_trace_from_demo_timeline(
        NESTED_DEMO_TIMELINE,
        event_types_by_depth={
            1: "task_trial",
            2: "action_chain",
            3: "sense_observation",
            4: "outcome_evaluation",
        },
    )


def build_demo_thought_deferred_integrated_trace() -> dict[str, object]:
    return build_integrated_trace_from_demo_timeline(
        THOUGHT_DEFERRED_TIMELINE,
        event_types_by_depth={1: "task_trial", 2: "thought_preview"},
    )


def build_demo_power_off_gap_integrated_trace() -> dict[str, object]:
    return build_integrated_trace_from_demo_timeline(
        POWER_OFF_GAP_TIMELINE,
        event_types_by_depth={1: "task_trial", 2: "sense_observation"},
    )


def build_demo_blocked_missing_dispatch_integrated_trace() -> dict[str, object]:
    return build_integrated_trace_from_demo_timeline(
        SIMPLE_TASK_TIMELINE,
        event_types_by_depth={1: "candidate_ordering"},
        force_missing_dispatch=True,
    )


def build_demo_blocked_missing_parent_resume_integrated_trace() -> dict[str, object]:
    return build_integrated_trace_from_demo_timeline(
        NESTED_SENSE_TIMELINE,
        event_types_by_depth={1: "task_trial", 2: "sense_observation"},
        force_missing_parent_resume=True,
    )


def build_demo_blocked_dynamic_scheduling_integrated_trace() -> dict[str, object]:
    return build_integrated_trace_from_demo_timeline(
        NESTED_SENSE_TIMELINE,
        event_types_by_depth={1: "task_trial", 2: "sense_observation"},
        force_dynamic_scheduling=True,
    )


def build_demo_blocked_forbidden_authority_integrated_trace() -> dict[str, object]:
    return build_integrated_trace_from_demo_timeline(
        SIMPLE_TASK_TIMELINE,
        event_types_by_depth={1: "candidate_ordering"},
        force_forbidden_authority=True,
    )


def render_integrated_loop_summary_text(
    trace: RuntimeIntegratedEventLoopTrace | dict[str, object],
    audit: RuntimeIntegratedEventLoopAudit | dict[str, object] | None = None,
    readiness: RuntimeIntegratedEventLoopReadinessRecord | dict[str, object] | None = None,
) -> str:
    trace_record = _integrated_trace(trace)
    audit_record = _integrated_audit(audit) if audit is not None else None
    readiness_record = _readiness(readiness) if readiness is not None else None
    parts = [
        f"integrated_loop status={trace_record.integrated_trace_status}",
        f"ticks={trace_record.tick_count}",
        f"frames={trace_record.event_frame_count}",
        f"dispatches={trace_record.dispatch_count}",
        f"returns={trace_record.return_payload_count}",
        f"parent_resumes={trace_record.parent_resume_count}",
    ]
    if audit_record is not None:
        parts.append(f"audit={audit_record.audit_status}")
    if readiness_record is not None:
        parts.append(f"readiness={readiness_record.readiness_status}")
    return " ".join(parts)


def render_integrated_loop_tree_text(
    *,
    canonical_timeline_text: str,
    event_frames: tuple[RuntimeEventFrameRecord, ...] | list[RuntimeEventFrameRecord | dict[str, object]],
    links: tuple[RuntimeIntegratedEventDispatchResumeLinkRecord, ...] | list[RuntimeIntegratedEventDispatchResumeLinkRecord | dict[str, object]] = (),
) -> str:
    frames = tuple(_event_frame(item) for item in event_frames)
    link_by_frame = {
        link.source_event_frame_id: link
        for link in (_dispatch_resume_link(item) for item in links)
    }
    lines = [f"timeline {canonical_timeline_text}"]
    for frame in sorted(frames, key=lambda item: item.event_depth):
        indent = "  " * (frame.event_depth - 1)
        link = link_by_frame.get(frame.event_frame_id)
        target = link.target_engine if link else TARGET_BY_FAMILY[classify_runtime_event_type(frame.event_type)]
        return_status = link.return_status if link else "returned_unknown"
        resume_status = link.parent_resume_status if link else "missing_parent_resume"
        lines.append(
            f"{indent}event_{frame.event_depth} {frame.event_type} "
            f"D->{target} R->{return_status} P->{resume_status}"
        )
    return "\n".join(lines)


def _build_integrated_steps(
    *,
    power_window: RuntimePowerWindowRecord,
    ticks: tuple[RuntimeTickRecord, ...],
    frames: tuple[RuntimeEventFrameRecord, ...],
    stacks: tuple[RuntimeEventStackRecord, ...],
    dispatch_requests: list[RuntimeEventDispatchRequestRecord],
    dispatch_routes: list[RuntimeEventDispatchRouteRecord],
    handler_adapters: list[RuntimeEventHandlerAdapterRecord],
    dispatch_results: list[RuntimeEventDispatchResultRecord],
    return_payloads: list[RuntimeEventDispatchReturnPayloadRecord],
    parent_resumes: list[RuntimeParentFrameResumeRecord],
    stack_updates: list[RuntimeParentFrameResumeStackUpdateRecord],
    force_dynamic_scheduling: bool = False,
    force_forbidden_authority: bool = False,
) -> tuple[RuntimeIntegratedEventStepRecord, ...]:
    normalized = normalize_runtime_timeline_text(power_window.timeline_text)
    ticks_by_power_index = {tick.tick_index: tick for tick in ticks}
    stacks_by_tick = {stack.tick_index: stack for stack in stacks}
    frame_by_id = {frame.event_frame_id: frame for frame in frames}
    requests_by_frame = {item.source_event_frame_id: item for item in dispatch_requests}
    routes_by_frame = {item.source_event_frame_id: item for item in dispatch_routes}
    adapters_by_frame = {item.source_event_frame_id: item for item in handler_adapters}
    results_by_frame = {item.source_event_frame_id: item for item in dispatch_results}
    returns_by_frame = {item.source_event_frame_id: item for item in return_payloads}
    resumes_by_frame = {item.source_child_event_frame_id: item for item in parent_resumes}
    updates_by_frame = {item.source_child_event_frame_id: item for item in stack_updates}
    steps: list[RuntimeIntegratedEventStepRecord] = []
    power_tick_index = 0
    for position, symbol in enumerate(normalized):
        if symbol == " ":
            steps.append(
                build_runtime_integrated_event_step_record(
                    power_window=power_window,
                    tick_index=position,
                    timeline_symbol=" ",
                    step_kind="power_off_gap",
                )
            )
            continue
        power_tick_index += 1
        tick = ticks_by_power_index[power_tick_index]
        frame = frame_by_id.get(tick.active_event_frame_id)
        frame_id = frame.event_frame_id if frame else None
        step_kind = _step_kind_from_tick(tick)
        steps.append(
            build_runtime_integrated_event_step_record(
                power_window=power_window,
                tick=tick,
                event_frame=frame,
                event_stack=stacks_by_tick.get(tick.tick_index),
                dispatch_request=requests_by_frame.get(frame_id),
                dispatch_route=routes_by_frame.get(frame_id),
                handler_adapter=adapters_by_frame.get(frame_id),
                dispatch_result=results_by_frame.get(frame_id),
                dispatch_return_payload=returns_by_frame.get(frame_id),
                parent_resume=resumes_by_frame.get(frame_id),
                resume_stack_update=updates_by_frame.get(frame_id),
                step_kind=step_kind,
                force_dynamic_child_event_created=(
                    force_dynamic_scheduling and position == len(normalized) - 1
                ),
                force_memory_layer_write_performed=(
                    force_forbidden_authority and position == len(normalized) - 1
                ),
            )
        )
    return tuple(steps)


def _retarget_frame_type(
    frame: RuntimeEventFrameRecord,
    event_type: str,
) -> RuntimeEventFrameRecord:
    return replace(
        frame,
        event_type=event_type,
        event_label=f"event_{frame.event_depth}_{event_type}",
    )


def _record_for_frame(records: list[Any], frame_id: str) -> Any | None:
    for record in records:
        if getattr(record, "source_event_frame_id", None) == frame_id:
            return record
    return None


def _step_kind_from_tick(tick: RuntimeTickRecord | None) -> str:
    if tick is None:
        return "power_off_gap"
    if tick.tick_kind == "idle_heartbeat":
        return "idle_heartbeat_step"
    if tick.created_event_frame:
        return "event_open_step"
    if tick.closed_event_frame:
        return "event_return_step"
    return "event_continue_step"


def _step_summary(status: str, event_type: str | None, target_engine: str | None) -> str:
    if status == "step_recorded_idle":
        return "Idle heartbeat step recorded."
    if status == "step_recorded_power_off_gap":
        return "Power-off gap recorded without runtime tick."
    if status == "step_recorded_event_dispatch_resume":
        return f"{event_type} dispatched to {target_engine} and linked to return/resume."
    if status.startswith("step_blocked"):
        return f"Integrated step blocked: {status}."
    return "Integrated event step recorded."


def _link_summary(status: str, event_type: str, target_engine: str) -> str:
    if status == "dispatch_resume_link_deferred_thought_engine":
        return "Thought Engine event deferred without fake behavior."
    if status.startswith("blocked_"):
        return f"Dispatch/resume link blocked for {event_type}: {status}."
    return f"{event_type} dispatch to {target_engine} linked to return/resume."


def _trace_summary(status: str) -> str:
    if status == "integrated_event_loop_trace_complete":
        return "Integrated bounded event-loop dispatch/resume trace complete."
    if status == "integrated_event_loop_trace_complete_with_deferred_thought":
        return "Integrated trace complete with Thought Engine deferred."
    if status == "integrated_event_loop_trace_complete_with_power_off_gaps":
        return "Integrated trace complete with power-off gaps preserved."
    return f"Integrated trace blocked: {status}."


def _render_summary(status: str) -> str:
    if status == "timeline_render_created":
        return "Integrated timeline render created."
    if status == "timeline_render_created_with_deferred_thought":
        return "Integrated timeline render created with deferred Thought Engine."
    return "Integrated timeline render blocked because trace is invalid."


def _readiness_summary(status: str) -> str:
    if status == "ready_for_fixed_runtime_playback_only":
        return "Ready only for fixed bounded runtime playback and bounded handler binding."
    if status == "ready_for_bounded_runtime_handler_binding_only":
        return "Ready only for bounded runtime handler binding."
    return f"Integrated loop readiness blocked: {status}."


def _integrated_audit_blocked_reasons(
    *,
    trace: RuntimeIntegratedEventLoopTrace | None,
    window: RuntimePowerWindowRecord | None,
    ticks: tuple[RuntimeTickRecord, ...],
    frames: tuple[RuntimeEventFrameRecord, ...],
    stacks: tuple[RuntimeEventStackRecord, ...],
    tree: RuntimeEventTreeRecord | None,
    links: tuple[RuntimeIntegratedEventDispatchResumeLinkRecord, ...],
    force_invalid_power_window: bool,
    force_invalid_tick_lineage: bool,
    force_dynamic_child_event_scheduling: bool,
    force_autonomous_scheduler: bool,
    force_open_ended_loop: bool,
    force_external_execution: bool,
    force_memory_write: bool,
    force_automatic_learning_approval: bool,
    force_recursive_learning: bool,
    force_thought_engine_fake: bool,
    force_production_behavior: bool,
) -> list[str]:
    reasons: list[str] = []
    if trace is None:
        reasons.append("missing_integrated_loop_trace")
        return reasons
    if force_invalid_power_window or (window is not None and window.window_status != "power_window_valid"):
        reasons.append("invalid_power_window")
    if force_invalid_tick_lineage or any(tick.tick_status != "tick_recorded" for tick in ticks):
        reasons.append("invalid_tick_lineage")
    if trace.integrated_trace_status == "integrated_event_loop_trace_blocked_missing_dispatch" or any(
        link.link_status == "blocked_missing_dispatch_result" for link in links
    ):
        reasons.append("missing_dispatch_lineage")
    if trace.integrated_trace_status == "integrated_event_loop_trace_blocked_missing_return" or any(
        link.link_status == "blocked_missing_return_payload" for link in links
    ):
        reasons.append("missing_return_payload")
    if trace.integrated_trace_status == "integrated_event_loop_trace_blocked_missing_parent_resume" or any(
        link.link_status == "blocked_missing_parent_resume" for link in links
    ):
        reasons.append("missing_parent_resume")
    if trace.integrated_trace_status == "integrated_event_loop_trace_blocked_invalid_stack" or any(
        stack.stack_status.startswith("stack_blocked") for stack in stacks
    ) or any(link.link_status == "blocked_invalid_stack_update" for link in links):
        reasons.append("invalid_stack_update")
    if trace.integrated_trace_status == "integrated_event_loop_trace_blocked_unclosed_frame" or any(
        frame.unclosed_frame_detected for frame in frames
    ) or (tree is not None and tree.tree_unclosed_frame_count):
        reasons.append("unclosed_root_frame")
    if force_dynamic_child_event_scheduling or trace.dynamic_child_event_created:
        reasons.append("dynamic_child_event_scheduling_detected")
    if force_autonomous_scheduler or trace.autonomous_scheduler_created:
        reasons.append("autonomous_scheduler_detected")
    if force_open_ended_loop or trace.open_ended_loop_created:
        reasons.append("open_ended_loop_detected")
    if force_external_execution or trace.external_execution_created:
        reasons.append("external_execution_detected")
    if force_memory_write or trace.memory_layer_write_performed:
        reasons.append("memory_write_detected")
    if force_automatic_learning_approval or trace.automatic_learning_approval_created:
        reasons.append("automatic_learning_approval_detected")
    if force_recursive_learning or trace.recursive_learning_created:
        reasons.append("recursive_learning_detected")
    if force_thought_engine_fake or trace.thought_engine_behavior_created:
        reasons.append("thought_engine_fake_detected")
    if force_production_behavior or trace.production_behavior_created:
        reasons.append("production_behavior_detected")
    return reasons


def _integrated_audit_status(
    trace: RuntimeIntegratedEventLoopTrace | None,
    blocked_reasons: list[str],
) -> str:
    priority = (
        ("invalid_power_window", "blocked_invalid_power_window"),
        ("invalid_tick_lineage", "blocked_invalid_tick_lineage"),
        ("missing_dispatch_lineage", "blocked_missing_dispatch_lineage"),
        ("missing_return_payload", "blocked_missing_return_payload"),
        ("missing_parent_resume", "blocked_missing_parent_resume"),
        ("invalid_stack_update", "blocked_invalid_stack_update"),
        ("unclosed_root_frame", "blocked_unclosed_root_frame"),
        (
            "dynamic_child_event_scheduling_detected",
            "blocked_dynamic_child_event_scheduling_detected",
        ),
        ("autonomous_scheduler_detected", "blocked_autonomous_scheduler_detected"),
        ("open_ended_loop_detected", "blocked_open_ended_loop_detected"),
        ("external_execution_detected", "blocked_external_execution_detected"),
        ("memory_write_detected", "blocked_memory_write_detected"),
        (
            "automatic_learning_approval_detected",
            "blocked_automatic_learning_approval_detected",
        ),
        ("recursive_learning_detected", "blocked_recursive_learning_detected"),
        ("thought_engine_fake_detected", "blocked_thought_engine_fake_detected"),
        ("production_behavior_detected", "blocked_production_behavior_detected"),
    )
    for reason, status in priority:
        if reason in blocked_reasons:
            return status
    if trace and trace.integrated_trace_status == "integrated_event_loop_trace_complete_with_deferred_thought":
        return "passed_integrated_event_loop_with_deferred_thought"
    if trace and trace.integrated_trace_status == "integrated_event_loop_trace_complete_with_power_off_gaps":
        return "passed_integrated_event_loop_with_power_off_gaps"
    return "passed_integrated_event_loop_dispatch_resume_trace"


def _power_window(value: RuntimePowerWindowRecord | dict[str, object]) -> RuntimePowerWindowRecord:
    return value if isinstance(value, RuntimePowerWindowRecord) else RuntimePowerWindowRecord.from_dict(value)


def _tick(value: RuntimeTickRecord | dict[str, object]) -> RuntimeTickRecord:
    return value if isinstance(value, RuntimeTickRecord) else RuntimeTickRecord.from_dict(value)


def _event_frame(value: RuntimeEventFrameRecord | dict[str, object]) -> RuntimeEventFrameRecord:
    return value if isinstance(value, RuntimeEventFrameRecord) else RuntimeEventFrameRecord.from_dict(value)


def _event_stack(value: RuntimeEventStackRecord | dict[str, object]) -> RuntimeEventStackRecord:
    return value if isinstance(value, RuntimeEventStackRecord) else RuntimeEventStackRecord.from_dict(value)


def _event_tree(value: RuntimeEventTreeRecord | dict[str, object]) -> RuntimeEventTreeRecord:
    return value if isinstance(value, RuntimeEventTreeRecord) else RuntimeEventTreeRecord.from_dict(value)


def _loop_trace(value: RuntimeContinuousLoopTrace | dict[str, object]) -> RuntimeContinuousLoopTrace:
    return value if isinstance(value, RuntimeContinuousLoopTrace) else RuntimeContinuousLoopTrace.from_dict(value)


def _loop_audit(value: RuntimeContinuousLoopAudit | dict[str, object]) -> RuntimeContinuousLoopAudit:
    return value if isinstance(value, RuntimeContinuousLoopAudit) else RuntimeContinuousLoopAudit.from_dict(value)


def _dispatch_request(value: RuntimeEventDispatchRequestRecord | dict[str, object]) -> RuntimeEventDispatchRequestRecord:
    return value if isinstance(value, RuntimeEventDispatchRequestRecord) else RuntimeEventDispatchRequestRecord.from_dict(value)


def _dispatch_route(value: RuntimeEventDispatchRouteRecord | dict[str, object]) -> RuntimeEventDispatchRouteRecord:
    return value if isinstance(value, RuntimeEventDispatchRouteRecord) else RuntimeEventDispatchRouteRecord.from_dict(value)


def _handler_adapter(value: RuntimeEventHandlerAdapterRecord | dict[str, object]) -> RuntimeEventHandlerAdapterRecord:
    return value if isinstance(value, RuntimeEventHandlerAdapterRecord) else RuntimeEventHandlerAdapterRecord.from_dict(value)


def _dispatch_result(value: RuntimeEventDispatchResultRecord | dict[str, object]) -> RuntimeEventDispatchResultRecord:
    return value if isinstance(value, RuntimeEventDispatchResultRecord) else RuntimeEventDispatchResultRecord.from_dict(value)


def _dispatch_return_payload(value: RuntimeEventDispatchReturnPayloadRecord | dict[str, object]) -> RuntimeEventDispatchReturnPayloadRecord:
    return value if isinstance(value, RuntimeEventDispatchReturnPayloadRecord) else RuntimeEventDispatchReturnPayloadRecord.from_dict(value)


def _dispatch_audit(value: RuntimeEventDispatchAudit | dict[str, object]) -> RuntimeEventDispatchAudit:
    return value if isinstance(value, RuntimeEventDispatchAudit) else RuntimeEventDispatchAudit.from_dict(value)


def _parent_resume(value: RuntimeParentFrameResumeRecord | dict[str, object]) -> RuntimeParentFrameResumeRecord:
    return value if isinstance(value, RuntimeParentFrameResumeRecord) else RuntimeParentFrameResumeRecord.from_dict(value)


def _resume_stack_update(value: RuntimeParentFrameResumeStackUpdateRecord | dict[str, object]) -> RuntimeParentFrameResumeStackUpdateRecord:
    return value if isinstance(value, RuntimeParentFrameResumeStackUpdateRecord) else RuntimeParentFrameResumeStackUpdateRecord.from_dict(value)


def _parent_resume_audit(value: RuntimeParentFrameResumeAudit | dict[str, object]) -> RuntimeParentFrameResumeAudit:
    return value if isinstance(value, RuntimeParentFrameResumeAudit) else RuntimeParentFrameResumeAudit.from_dict(value)


def _integrated_step(value: RuntimeIntegratedEventStepRecord | dict[str, object]) -> RuntimeIntegratedEventStepRecord:
    return value if isinstance(value, RuntimeIntegratedEventStepRecord) else RuntimeIntegratedEventStepRecord.from_dict(value)


def _dispatch_resume_link(value: RuntimeIntegratedEventDispatchResumeLinkRecord | dict[str, object]) -> RuntimeIntegratedEventDispatchResumeLinkRecord:
    return value if isinstance(value, RuntimeIntegratedEventDispatchResumeLinkRecord) else RuntimeIntegratedEventDispatchResumeLinkRecord.from_dict(value)


def _integrated_trace(value: RuntimeIntegratedEventLoopTrace | dict[str, object]) -> RuntimeIntegratedEventLoopTrace:
    return value if isinstance(value, RuntimeIntegratedEventLoopTrace) else RuntimeIntegratedEventLoopTrace.from_dict(value)


def _timeline_render(value: RuntimeIntegratedEventLoopTimelineRenderRecord | dict[str, object]) -> RuntimeIntegratedEventLoopTimelineRenderRecord:
    return value if isinstance(value, RuntimeIntegratedEventLoopTimelineRenderRecord) else RuntimeIntegratedEventLoopTimelineRenderRecord.from_dict(value)


def _integrated_audit(value: RuntimeIntegratedEventLoopAudit | dict[str, object]) -> RuntimeIntegratedEventLoopAudit:
    return value if isinstance(value, RuntimeIntegratedEventLoopAudit) else RuntimeIntegratedEventLoopAudit.from_dict(value)


def _readiness(value: RuntimeIntegratedEventLoopReadinessRecord | dict[str, object]) -> RuntimeIntegratedEventLoopReadinessRecord:
    return value if isinstance(value, RuntimeIntegratedEventLoopReadinessRecord) else RuntimeIntegratedEventLoopReadinessRecord.from_dict(value)
