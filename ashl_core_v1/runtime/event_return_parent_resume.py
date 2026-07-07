"""Record-only parent EventFrame resume after child EventFrame returns."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.runtime.continuous_event_loop import (
    EVENT_FRAME_SCHEMA_VERSION,
    SOURCE_ENGINE,
    RuntimeContinuousLoopTrace,
    RuntimeEventFrameRecord,
    RuntimeEventReturnRecord,
    RuntimeEventStackRecord,
    RuntimeEventTreeRecord,
    build_demo_nested_event_continuous_loop,
)
from ashl_core_v1.runtime.event_frame_dispatch_adapter import (
    DISPATCH_RETURN_PAYLOAD_SCHEMA_VERSION,
    RuntimeEventDispatchAudit,
    RuntimeEventDispatchResultRecord,
    RuntimeEventDispatchReturnPayloadRecord,
)


RESUME_REQUEST_SCHEMA_VERSION = "runtime_parent_frame_resume_request_v0"
RESUME_DECISION_SCHEMA_VERSION = "runtime_parent_frame_resume_decision_v0"
PARENT_RESUME_SCHEMA_VERSION = "runtime_parent_frame_resume_v0"
RESUME_STACK_UPDATE_SCHEMA_VERSION = "runtime_parent_frame_resume_stack_update_v0"
NESTED_RETURN_RESUME_TRACE_SCHEMA_VERSION = "runtime_nested_return_resume_trace_v0"
PARENT_RESUME_AUDIT_SCHEMA_VERSION = "runtime_parent_frame_resume_audit_v0"

ALLOWED_CHILD_RETURN_STATUSES = {
    "returned_success",
    "returned_blocked",
    "returned_unknown",
    "returned_deferred",
    "returned_fault",
}
ALLOWED_RESUME_REQUEST_STATUSES = {
    "parent_resume_request_created",
    "blocked_missing_parent_frame",
    "blocked_invalid_child_return",
    "blocked_scope_expansion_requested",
    "blocked_budget_extension_requested",
    "blocked_new_child_event_requested",
    "blocked_forbidden_authority_requested",
}
ALLOWED_RESUME_DECISIONS = {
    "resume_continue_parent",
    "resume_continue_parent_with_child_blocked",
    "resume_defer_parent",
    "resume_block_parent",
    "resume_fault_parent",
    "close_parent_after_child_success",
    "close_root_event",
    "blocked_missing_parent_frame",
    "blocked_invalid_return_payload",
    "blocked_parent_budget_exhausted",
    "blocked_forbidden_authority_detected",
}
ALLOWED_RESUME_STATUSES = {
    "parent_resumed_continue",
    "parent_resumed_continue_with_child_blocked",
    "parent_deferred_after_child_return",
    "parent_blocked_after_child_return",
    "parent_faulted_after_child_return",
    "parent_closed_after_child_return",
    "root_event_closed",
    "blocked_missing_parent_frame",
    "blocked_parent_budget_exhausted",
    "blocked_forbidden_authority_detected",
}
ALLOWED_STACK_UPDATE_STATUSES = {
    "stack_updated_parent_resumed",
    "stack_updated_parent_closed",
    "stack_updated_root_closed",
    "blocked_invalid_parent_child_order",
    "blocked_unclosed_child_frame",
    "blocked_stack_underflow",
    "blocked_stack_overflow",
}
ALLOWED_TRACE_STATUSES = {
    "nested_return_resume_trace_complete",
    "nested_return_resume_trace_complete_with_deferred_parent",
    "nested_return_resume_trace_blocked_missing_child_return",
    "nested_return_resume_trace_blocked_missing_parent_resume",
    "nested_return_resume_trace_blocked_invalid_stack_update",
    "nested_return_resume_trace_blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_parent_frame_resume_after_child_success",
    "passed_parent_frame_resume_after_child_blocked",
    "passed_parent_frame_deferred_after_child_unknown",
    "passed_parent_frame_faulted_after_child_fault",
    "passed_nested_return_resume_trace",
    "blocked_missing_parent_frame",
    "blocked_invalid_child_return",
    "blocked_invalid_resume_decision",
    "blocked_invalid_stack_update",
    "blocked_new_child_event_created",
    "blocked_dynamic_scheduling_detected",
    "blocked_external_execution_detected",
    "blocked_memory_write_detected",
    "blocked_automatic_learning_approval_detected",
    "blocked_recursive_learning_detected",
    "blocked_production_behavior_detected",
}

SAFE_CLAIM = (
    "ASHL Core v1 can consume bounded child EventFrame return payloads, "
    "record deterministic parent EventFrame resume decisions, update the "
    "EventStack after child returns, and verify nested return/resume traces."
)
BLOCKED_CLAIMS = (
    "no_live_autonomous_event_loop",
    "no_dynamic_child_event_scheduling",
    "no_free_event_creation",
    "no_engine_behavior_invocation_from_parent_resume",
    "no_external_execution",
    "no_memory_layer_write",
    "no_automatic_learning_approval",
    "no_recursive_learning",
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
        else:
            safe.append("_")
    return "_".join("".join(safe).split("_"))[:80] or "empty"


def _bool_payload(payload: dict[str, object], key: str) -> bool:
    return bool(payload.get(key, False))


@dataclass(frozen=True)
class RuntimeParentFrameResumeRequestRecord:
    parent_resume_request_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_child_event_frame_id: str
    source_parent_event_frame_id: str | None
    source_dispatch_return_payload_id: str | None
    source_runtime_event_return_id: str | None
    child_event_depth: int
    parent_event_depth: int | None
    child_return_status: str
    child_return_reason: str
    child_return_payload: dict[str, object]
    parent_resume_requested: bool
    parent_resume_request_status: str
    parent_resume_request_summary: str
    scope_expansion_requested: bool
    budget_extension_requested: bool
    new_child_event_requested: bool
    free_action_selection_requested: bool
    external_execution_requested: bool
    memory_layer_write_requested: bool
    automatic_learning_approval_requested: bool
    recursive_learning_requested: bool
    production_behavior_requested: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RESUME_REQUEST_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_parent_frame_resume_request_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.parent_resume_request_status not in ALLOWED_RESUME_REQUEST_STATUSES:
            raise ValueError(
                f"unknown parent_resume_request_status: {self.parent_resume_request_status}"
            )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeParentFrameResumeRequestRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeParentFrameResumeDecisionRecord:
    parent_resume_decision_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_parent_resume_request_id: str
    source_child_event_frame_id: str
    source_parent_event_frame_id: str | None
    child_return_status: str
    parent_event_status_before_resume: str | None
    parent_remaining_budget_ticks_before_resume: int | None
    child_ticks_used: int
    resume_decision: str
    resume_decision_reason: str
    resume_decision_summary: str
    parent_can_resume: bool
    parent_should_close: bool
    parent_should_defer: bool
    parent_should_block: bool
    parent_should_fault: bool
    parent_scope_preserved: bool
    parent_budget_preserved: bool
    new_child_event_creation_allowed: bool
    free_action_selection_allowed: bool
    external_execution_allowed: bool
    memory_layer_write_allowed: bool
    automatic_learning_approval_allowed: bool
    recursive_learning_allowed: bool
    production_behavior_allowed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RESUME_DECISION_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_parent_frame_resume_decision_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.resume_decision not in ALLOWED_RESUME_DECISIONS:
            raise ValueError(f"unknown resume_decision: {self.resume_decision}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeParentFrameResumeDecisionRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeParentFrameResumeRecord:
    parent_resume_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_parent_resume_decision_id: str
    source_child_event_frame_id: str
    source_parent_event_frame_id: str | None
    source_dispatch_return_payload_id: str | None
    parent_event_status_before_resume: str | None
    parent_event_status_after_resume: str | None
    parent_resumed: bool
    parent_closed: bool
    parent_deferred: bool
    parent_blocked: bool
    parent_faulted: bool
    parent_resume_tick_index: int | None
    child_return_status_consumed: bool
    child_return_payload_attached: bool
    parent_scope_after_resume: str | None
    parent_remaining_budget_ticks_after_resume: int | None
    new_child_event_created: bool
    dynamic_scheduling_created: bool
    free_action_selection_created: bool
    external_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    recursive_learning_created: bool
    production_behavior_created: bool
    resume_status: str
    resume_summary: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PARENT_RESUME_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_parent_frame_resume_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.resume_status not in ALLOWED_RESUME_STATUSES:
            raise ValueError(f"unknown resume_status: {self.resume_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeParentFrameResumeRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeParentFrameResumeStackUpdateRecord:
    resume_stack_update_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_parent_resume_id: str
    source_child_event_frame_id: str
    source_parent_event_frame_id: str | None
    stack_before_resume: tuple[str, ...]
    stack_after_child_pop: tuple[str, ...]
    stack_after_parent_resume: tuple[str, ...]
    child_frame_popped: bool
    parent_frame_on_top_after_pop: bool
    parent_frame_resumed_on_stack: bool
    stack_depth_before_resume: int
    stack_depth_after_resume: int
    stack_update_status: str
    stack_update_summary: str
    invalid_parent_child_order_detected: bool
    unclosed_child_frame_detected: bool
    stack_underflow_detected: bool
    stack_overflow_detected: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != RESUME_STACK_UPDATE_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_parent_frame_resume_stack_update_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.stack_update_status not in ALLOWED_STACK_UPDATE_STATUSES:
            raise ValueError(f"unknown stack_update_status: {self.stack_update_status}")
        for name in (
            "stack_before_resume",
            "stack_after_child_pop",
            "stack_after_parent_resume",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeParentFrameResumeStackUpdateRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeNestedReturnResumeTrace:
    nested_return_resume_trace_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_loop_trace_id: str | None
    source_event_tree_id: str | None
    return_sequence: tuple[str, ...]
    resume_sequence: tuple[str, ...]
    event_frame_ids: tuple[str, ...]
    parent_resume_ids: tuple[str, ...]
    stack_update_ids: tuple[str, ...]
    max_depth_observed: int
    all_child_returns_consumed: bool
    all_parent_resumes_recorded: bool
    all_frames_closed_or_validly_deferred: bool
    trace_status: str
    trace_summary: str
    new_child_event_created: bool
    dynamic_scheduling_created: bool
    external_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    recursive_learning_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != NESTED_RETURN_RESUME_TRACE_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_nested_return_resume_trace_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.trace_status not in ALLOWED_TRACE_STATUSES:
            raise ValueError(f"unknown trace_status: {self.trace_status}")
        for name in (
            "return_sequence",
            "resume_sequence",
            "event_frame_ids",
            "parent_resume_ids",
            "stack_update_ids",
            "source_trace_refs",
        ):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeNestedReturnResumeTrace":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeParentFrameResumeAudit:
    parent_resume_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_parent_resume_request_id: str | None
    source_parent_resume_decision_id: str | None
    source_parent_resume_id: str | None
    source_resume_stack_update_id: str | None
    source_nested_return_resume_trace_id: str | None
    child_return_valid: bool
    parent_frame_valid: bool
    resume_decision_valid: bool
    resume_record_valid: bool
    stack_update_valid: bool
    nested_trace_valid: bool
    parent_scope_preserved: bool
    parent_budget_preserved: bool
    child_return_payload_consumed: bool
    parent_resume_verified: bool
    no_new_child_event_created: bool
    no_dynamic_scheduling: bool
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
    no_production_behavior: bool
    no_thought_engine_behavior: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PARENT_RESUME_AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_parent_frame_resume_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeParentFrameResumeAudit":
        return cls(**dict(data))


def validate_runtime_parent_frame_resume_request(
    record: RuntimeParentFrameResumeRequestRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _resume_request(record)
    except Exception as error:  # pragma: no cover - defensive schema guard
        return {"valid": False, "error": str(error)}
    return {
        "valid": True,
        "parent_resume_request_id": item.parent_resume_request_id,
        "parent_resume_request_status": item.parent_resume_request_status,
    }


def validate_runtime_parent_frame_resume_decision(
    record: RuntimeParentFrameResumeDecisionRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _resume_decision(record)
    except Exception as error:  # pragma: no cover - defensive schema guard
        return {"valid": False, "error": str(error)}
    return {
        "valid": True,
        "parent_resume_decision_id": item.parent_resume_decision_id,
        "resume_decision": item.resume_decision,
    }


def validate_runtime_parent_frame_resume_record(
    record: RuntimeParentFrameResumeRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _parent_resume(record)
    except Exception as error:  # pragma: no cover - defensive schema guard
        return {"valid": False, "error": str(error)}
    return {
        "valid": True,
        "parent_resume_id": item.parent_resume_id,
        "resume_status": item.resume_status,
    }


def validate_runtime_parent_frame_resume_stack_update(
    record: RuntimeParentFrameResumeStackUpdateRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _stack_update(record)
    except Exception as error:  # pragma: no cover - defensive schema guard
        return {"valid": False, "error": str(error)}
    return {
        "valid": True,
        "resume_stack_update_id": item.resume_stack_update_id,
        "stack_update_status": item.stack_update_status,
    }


def validate_runtime_nested_return_resume_trace(
    record: RuntimeNestedReturnResumeTrace | dict[str, object],
) -> dict[str, object]:
    try:
        item = _nested_trace(record)
    except Exception as error:  # pragma: no cover - defensive schema guard
        return {"valid": False, "error": str(error)}
    return {
        "valid": True,
        "nested_return_resume_trace_id": item.nested_return_resume_trace_id,
        "trace_status": item.trace_status,
    }


def validate_runtime_parent_frame_resume_audit(
    record: RuntimeParentFrameResumeAudit | dict[str, object],
) -> dict[str, object]:
    try:
        item = _resume_audit(record)
    except Exception as error:  # pragma: no cover - defensive schema guard
        return {"valid": False, "error": str(error)}
    return {
        "valid": True,
        "parent_resume_audit_id": item.parent_resume_audit_id,
        "audit_status": item.audit_status,
    }


def build_runtime_parent_frame_resume_request(
    child_event_frame: RuntimeEventFrameRecord | dict[str, object],
    *,
    parent_event_frame: RuntimeEventFrameRecord | dict[str, object] | None = None,
    dispatch_return_payload: RuntimeEventDispatchReturnPayloadRecord | dict[str, object] | None = None,
    runtime_event_return: RuntimeEventReturnRecord | dict[str, object] | None = None,
    request_payload: dict[str, object] | None = None,
) -> RuntimeParentFrameResumeRequestRecord:
    child = _event_frame(child_event_frame)
    parent = _event_frame(parent_event_frame) if parent_event_frame is not None else None
    payload_flags = dict(request_payload or {})
    return_id: str | None = None
    runtime_return_id: str | None = None
    return_status = "returned_unknown"
    return_reason = "child_return_payload_not_supplied"
    return_payload: dict[str, object] = {}
    source_trace_refs = child.source_trace_refs

    if dispatch_return_payload is not None:
        dispatch_payload = _dispatch_return_payload(dispatch_return_payload)
        return_id = dispatch_payload.dispatch_return_payload_id
        return_status = dispatch_payload.return_status
        return_reason = dispatch_payload.return_reason
        return_payload = dict(dispatch_payload.return_payload)
        source_trace_refs = dispatch_payload.source_trace_refs or source_trace_refs
        payload_flags.setdefault(
            "new_child_event_requested",
            dispatch_payload.creates_new_event or dispatch_payload.requires_child_event,
        )
    if runtime_event_return is not None:
        event_return = _event_return(runtime_event_return)
        runtime_return_id = event_return.event_return_id
        return_status = event_return.return_status
        return_reason = event_return.return_reason
        return_payload = dict(event_return.return_payload)
        source_trace_refs = event_return.source_trace_refs or source_trace_refs
        payload_flags.setdefault(
            "new_child_event_requested",
            event_return.return_created_new_event_without_parent,
        )

    return_payload.setdefault("child_event_ticks_used", child.event_ticks_used)
    return_payload.setdefault("return_tick_index", child.closed_at_tick_index)
    parent_id = (
        parent.event_frame_id
        if parent is not None
        else child.parent_event_frame_id
    )
    parent_depth = parent.event_depth if parent is not None else None
    invalid_return = return_status not in ALLOWED_CHILD_RETURN_STATUSES
    non_root_missing_parent = child.event_depth > 1 and not parent_id
    forbidden_requested = any(
        _bool_payload(payload_flags, key)
        for key in (
            "free_action_selection_requested",
            "external_execution_requested",
            "memory_layer_write_requested",
            "automatic_learning_approval_requested",
            "recursive_learning_requested",
            "production_behavior_requested",
        )
    )
    scope_expansion = _bool_payload(payload_flags, "scope_expansion_requested")
    budget_extension = _bool_payload(payload_flags, "budget_extension_requested")
    new_child_event = _bool_payload(payload_flags, "new_child_event_requested")

    if invalid_return:
        status = "blocked_invalid_child_return"
    elif non_root_missing_parent:
        status = "blocked_missing_parent_frame"
    elif scope_expansion:
        status = "blocked_scope_expansion_requested"
    elif budget_extension:
        status = "blocked_budget_extension_requested"
    elif new_child_event:
        status = "blocked_new_child_event_requested"
    elif forbidden_requested:
        status = "blocked_forbidden_authority_requested"
    else:
        status = "parent_resume_request_created"

    return RuntimeParentFrameResumeRequestRecord(
        parent_resume_request_id=f"runtime_parent_frame_resume_request:{child.event_frame_id}:{_slug(return_status)}",
        schema_version=RESUME_REQUEST_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_child_event_frame_id=child.event_frame_id,
        source_parent_event_frame_id=parent_id,
        source_dispatch_return_payload_id=return_id,
        source_runtime_event_return_id=runtime_return_id,
        child_event_depth=child.event_depth,
        parent_event_depth=parent_depth,
        child_return_status=return_status,
        child_return_reason=return_reason,
        child_return_payload=return_payload,
        parent_resume_requested=True,
        parent_resume_request_status=status,
        parent_resume_request_summary=_request_summary(status, return_status),
        scope_expansion_requested=scope_expansion,
        budget_extension_requested=budget_extension,
        new_child_event_requested=new_child_event,
        free_action_selection_requested=_bool_payload(
            payload_flags, "free_action_selection_requested"
        ),
        external_execution_requested=_bool_payload(
            payload_flags, "external_execution_requested"
        ),
        memory_layer_write_requested=_bool_payload(
            payload_flags, "memory_layer_write_requested"
        ),
        automatic_learning_approval_requested=_bool_payload(
            payload_flags, "automatic_learning_approval_requested"
        ),
        recursive_learning_requested=_bool_payload(
            payload_flags, "recursive_learning_requested"
        ),
        production_behavior_requested=_bool_payload(
            payload_flags, "production_behavior_requested"
        ),
        source_trace_refs=source_trace_refs,
    )


def build_runtime_parent_frame_resume_decision(
    parent_resume_request: RuntimeParentFrameResumeRequestRecord | dict[str, object],
    *,
    parent_event_frame: RuntimeEventFrameRecord | dict[str, object] | None = None,
    close_parent_after_success: bool = False,
) -> RuntimeParentFrameResumeDecisionRecord:
    request = _resume_request(parent_resume_request)
    parent = _event_frame(parent_event_frame) if parent_event_frame is not None else None
    parent_status = parent.event_status if parent is not None else None
    remaining_budget = (
        parent.event_budget_ticks - parent.event_ticks_used
        if parent is not None
        else None
    )
    child_ticks_used = int(request.child_return_payload.get("child_event_ticks_used", 0))
    if request.parent_resume_request_status == "blocked_missing_parent_frame":
        decision = "blocked_missing_parent_frame"
    elif request.parent_resume_request_status == "blocked_invalid_child_return":
        decision = "blocked_invalid_return_payload"
    elif request.parent_resume_request_status == "blocked_forbidden_authority_requested":
        decision = "blocked_forbidden_authority_detected"
    elif request.parent_resume_request_status != "parent_resume_request_created":
        decision = "blocked_forbidden_authority_detected"
    elif remaining_budget is not None and remaining_budget <= 0:
        decision = "blocked_parent_budget_exhausted"
    elif request.source_parent_event_frame_id is None and request.child_event_depth == 1:
        decision = "close_root_event"
    elif request.child_return_status == "returned_success":
        decision = (
            "close_parent_after_child_success"
            if close_parent_after_success
            else "resume_continue_parent"
        )
    elif request.child_return_status == "returned_blocked":
        decision = "resume_continue_parent_with_child_blocked"
    elif request.child_return_status in {"returned_unknown", "returned_deferred"}:
        decision = "resume_defer_parent"
    elif request.child_return_status == "returned_fault":
        decision = "resume_fault_parent"
    else:
        decision = "blocked_invalid_return_payload"

    return RuntimeParentFrameResumeDecisionRecord(
        parent_resume_decision_id=f"runtime_parent_frame_resume_decision:{request.source_child_event_frame_id}:{_slug(decision)}",
        schema_version=RESUME_DECISION_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_parent_resume_request_id=request.parent_resume_request_id,
        source_child_event_frame_id=request.source_child_event_frame_id,
        source_parent_event_frame_id=request.source_parent_event_frame_id,
        child_return_status=request.child_return_status,
        parent_event_status_before_resume=parent_status,
        parent_remaining_budget_ticks_before_resume=remaining_budget,
        child_ticks_used=child_ticks_used,
        resume_decision=decision,
        resume_decision_reason=_decision_reason(decision, request.child_return_status),
        resume_decision_summary=_decision_summary(decision),
        parent_can_resume=decision.startswith("resume_continue"),
        parent_should_close=decision in {
            "close_parent_after_child_success",
            "close_root_event",
        },
        parent_should_defer=decision == "resume_defer_parent",
        parent_should_block=decision in {
            "resume_block_parent",
            "blocked_missing_parent_frame",
            "blocked_invalid_return_payload",
            "blocked_parent_budget_exhausted",
            "blocked_forbidden_authority_detected",
        },
        parent_should_fault=decision == "resume_fault_parent",
        parent_scope_preserved=True,
        parent_budget_preserved=True,
        new_child_event_creation_allowed=False,
        free_action_selection_allowed=False,
        external_execution_allowed=False,
        memory_layer_write_allowed=False,
        automatic_learning_approval_allowed=False,
        recursive_learning_allowed=False,
        production_behavior_allowed=False,
        source_trace_refs=request.source_trace_refs,
    )


def build_runtime_parent_frame_resume_record(
    parent_resume_request: RuntimeParentFrameResumeRequestRecord | dict[str, object],
    parent_resume_decision: RuntimeParentFrameResumeDecisionRecord | dict[str, object],
    *,
    parent_event_frame: RuntimeEventFrameRecord | dict[str, object] | None = None,
) -> RuntimeParentFrameResumeRecord:
    request = _resume_request(parent_resume_request)
    decision = _resume_decision(parent_resume_decision)
    parent = _event_frame(parent_event_frame) if parent_event_frame is not None else None
    resume_status = _resume_status_from_decision(decision.resume_decision)
    before_status = decision.parent_event_status_before_resume
    after_status = _parent_status_after_resume(resume_status)
    parent_resumed = resume_status in {
        "parent_resumed_continue",
        "parent_resumed_continue_with_child_blocked",
    }
    parent_closed = resume_status in {
        "parent_closed_after_child_return",
        "root_event_closed",
    }
    parent_deferred = resume_status == "parent_deferred_after_child_return"
    parent_blocked = resume_status in {
        "parent_blocked_after_child_return",
        "blocked_missing_parent_frame",
        "blocked_parent_budget_exhausted",
        "blocked_forbidden_authority_detected",
    }
    parent_faulted = resume_status == "parent_faulted_after_child_return"
    before_budget = decision.parent_remaining_budget_ticks_before_resume
    after_budget = None
    if before_budget is not None:
        after_budget = max(0, before_budget - 1) if not parent_blocked else before_budget
    return RuntimeParentFrameResumeRecord(
        parent_resume_id=f"runtime_parent_frame_resume:{request.source_child_event_frame_id}:{_slug(resume_status)}",
        schema_version=PARENT_RESUME_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_parent_resume_decision_id=decision.parent_resume_decision_id,
        source_child_event_frame_id=request.source_child_event_frame_id,
        source_parent_event_frame_id=request.source_parent_event_frame_id,
        source_dispatch_return_payload_id=request.source_dispatch_return_payload_id,
        parent_event_status_before_resume=before_status,
        parent_event_status_after_resume=after_status,
        parent_resumed=parent_resumed,
        parent_closed=parent_closed,
        parent_deferred=parent_deferred,
        parent_blocked=parent_blocked,
        parent_faulted=parent_faulted,
        parent_resume_tick_index=int(request.child_return_payload.get("return_tick_index", 0))
        if request.child_return_payload.get("return_tick_index") is not None
        else None,
        child_return_status_consumed=True,
        child_return_payload_attached=True,
        parent_scope_after_resume=parent.event_scope if parent is not None else None,
        parent_remaining_budget_ticks_after_resume=after_budget,
        new_child_event_created=False,
        dynamic_scheduling_created=False,
        free_action_selection_created=False,
        external_execution_created=False,
        memory_layer_write_performed=False,
        automatic_learning_approval_created=False,
        recursive_learning_created=False,
        production_behavior_created=False,
        resume_status=resume_status,
        resume_summary=_resume_summary(resume_status),
        source_trace_refs=request.source_trace_refs,
    )


def build_runtime_parent_frame_resume_stack_update(
    parent_resume: RuntimeParentFrameResumeRecord | dict[str, object],
    *,
    stack_before_resume: tuple[str, ...] | list[str] | None = None,
    force_invalid_parent_child_order: bool = False,
    force_unclosed_child_frame: bool = False,
    force_stack_underflow: bool = False,
    force_stack_overflow: bool = False,
) -> RuntimeParentFrameResumeStackUpdateRecord:
    resume = _parent_resume(parent_resume)
    child_id = resume.source_child_event_frame_id
    parent_id = resume.source_parent_event_frame_id
    before = tuple(stack_before_resume or ((parent_id, child_id) if parent_id else (child_id,)))
    before = tuple(item for item in before if item is not None)
    stack_underflow = force_stack_underflow or not before
    child_on_top = bool(before) and before[-1] == child_id
    invalid_order = force_invalid_parent_child_order or not child_on_top
    unclosed_child = force_unclosed_child_frame
    stack_overflow = force_stack_overflow
    if stack_underflow:
        after_child_pop = tuple()
        after_parent_resume = tuple()
        status = "blocked_stack_underflow"
    elif invalid_order:
        after_child_pop = before
        after_parent_resume = before
        status = "blocked_invalid_parent_child_order"
    elif unclosed_child:
        after_child_pop = before
        after_parent_resume = before
        status = "blocked_unclosed_child_frame"
    elif stack_overflow:
        after_child_pop = before[:-1]
        after_parent_resume = after_child_pop
        status = "blocked_stack_overflow"
    else:
        after_child_pop = before[:-1]
        if resume.resume_status == "root_event_closed":
            after_parent_resume = tuple()
            status = "stack_updated_root_closed"
        elif resume.parent_closed and parent_id and after_child_pop[-1:] == (parent_id,):
            after_parent_resume = after_child_pop[:-1]
            status = "stack_updated_parent_closed"
        else:
            after_parent_resume = after_child_pop
            status = "stack_updated_parent_resumed"
    parent_on_top = (
        parent_id is None and not after_child_pop
    ) or (bool(parent_id) and bool(after_child_pop) and after_child_pop[-1] == parent_id)
    return RuntimeParentFrameResumeStackUpdateRecord(
        resume_stack_update_id=f"runtime_parent_frame_resume_stack_update:{child_id}:{_slug(status)}",
        schema_version=RESUME_STACK_UPDATE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_parent_resume_id=resume.parent_resume_id,
        source_child_event_frame_id=child_id,
        source_parent_event_frame_id=parent_id,
        stack_before_resume=before,
        stack_after_child_pop=after_child_pop,
        stack_after_parent_resume=after_parent_resume,
        child_frame_popped=not any(
            (stack_underflow, invalid_order, unclosed_child, stack_overflow)
        ),
        parent_frame_on_top_after_pop=parent_on_top,
        parent_frame_resumed_on_stack=resume.parent_resumed and parent_on_top,
        stack_depth_before_resume=len(before),
        stack_depth_after_resume=len(after_parent_resume),
        stack_update_status=status,
        stack_update_summary=_stack_update_summary(status),
        invalid_parent_child_order_detected=invalid_order,
        unclosed_child_frame_detected=unclosed_child,
        stack_underflow_detected=stack_underflow,
        stack_overflow_detected=stack_overflow,
        source_trace_refs=resume.source_trace_refs,
    )


def build_runtime_nested_return_resume_trace(
    *,
    parent_resumes: tuple[RuntimeParentFrameResumeRecord, ...] | list[RuntimeParentFrameResumeRecord],
    stack_updates: tuple[RuntimeParentFrameResumeStackUpdateRecord, ...] | list[RuntimeParentFrameResumeStackUpdateRecord],
    event_frames: tuple[RuntimeEventFrameRecord, ...] | list[RuntimeEventFrameRecord],
    loop_trace: RuntimeContinuousLoopTrace | dict[str, object] | None = None,
    event_tree: RuntimeEventTreeRecord | dict[str, object] | None = None,
    force_missing_child_return: bool = False,
    force_missing_parent_resume: bool = False,
    force_forbidden_authority: bool = False,
) -> RuntimeNestedReturnResumeTrace:
    resumes = tuple(parent_resumes)
    updates = tuple(stack_updates)
    frames = tuple(event_frames)
    loop = _loop_trace(loop_trace) if loop_trace is not None else None
    tree = _event_tree(event_tree) if event_tree is not None else None
    frame_depth_by_id = {frame.event_frame_id: frame.event_depth for frame in frames}
    return_sequence = tuple(
        _return_sequence_item(resume, frame_depth_by_id)
        for resume in resumes
    )
    resume_sequence = tuple(
        _resume_sequence_item(resume, frame_depth_by_id)
        for resume in resumes
        if resume.source_parent_event_frame_id is not None and resume.parent_resumed
    )
    invalid_stack = any(
        update.stack_update_status.startswith("blocked_") for update in updates
    )
    missing_child_return = force_missing_child_return or not resumes
    missing_parent_resume = force_missing_parent_resume or len(resumes) != len(updates)
    forbidden = force_forbidden_authority or any(
        resume.new_child_event_created
        or resume.dynamic_scheduling_created
        or resume.external_execution_created
        or resume.memory_layer_write_performed
        or resume.automatic_learning_approval_created
        or resume.recursive_learning_created
        or resume.production_behavior_created
        for resume in resumes
    )
    if forbidden:
        status = "nested_return_resume_trace_blocked_forbidden_authority_detected"
    elif missing_child_return:
        status = "nested_return_resume_trace_blocked_missing_child_return"
    elif missing_parent_resume:
        status = "nested_return_resume_trace_blocked_missing_parent_resume"
    elif invalid_stack:
        status = "nested_return_resume_trace_blocked_invalid_stack_update"
    elif any(resume.parent_deferred for resume in resumes):
        status = "nested_return_resume_trace_complete_with_deferred_parent"
    else:
        status = "nested_return_resume_trace_complete"
    return RuntimeNestedReturnResumeTrace(
        nested_return_resume_trace_id="runtime_nested_return_resume_trace:package97_demo",
        schema_version=NESTED_RETURN_RESUME_TRACE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_loop_trace_id=loop.continuous_loop_trace_id if loop else None,
        source_event_tree_id=tree.event_tree_id if tree else None,
        return_sequence=return_sequence,
        resume_sequence=resume_sequence,
        event_frame_ids=tuple(frame.event_frame_id for frame in frames),
        parent_resume_ids=tuple(resume.parent_resume_id for resume in resumes),
        stack_update_ids=tuple(update.resume_stack_update_id for update in updates),
        max_depth_observed=max((frame.event_depth for frame in frames), default=0),
        all_child_returns_consumed=not missing_child_return,
        all_parent_resumes_recorded=not missing_parent_resume,
        all_frames_closed_or_validly_deferred=not invalid_stack and not forbidden,
        trace_status=status,
        trace_summary=_trace_summary(status),
        new_child_event_created=False,
        dynamic_scheduling_created=False,
        external_execution_created=force_forbidden_authority,
        memory_layer_write_performed=False,
        automatic_learning_approval_created=False,
        recursive_learning_created=False,
        production_behavior_created=False,
        source_trace_refs=tuple(
            ref for resume in resumes for ref in resume.source_trace_refs
        ),
    )


def build_runtime_parent_frame_resume_audit(
    *,
    parent_resume_request: RuntimeParentFrameResumeRequestRecord | dict[str, object] | None = None,
    parent_resume_decision: RuntimeParentFrameResumeDecisionRecord | dict[str, object] | None = None,
    parent_resume: RuntimeParentFrameResumeRecord | dict[str, object] | None = None,
    resume_stack_update: RuntimeParentFrameResumeStackUpdateRecord | dict[str, object] | None = None,
    nested_return_resume_trace: RuntimeNestedReturnResumeTrace | dict[str, object] | None = None,
) -> RuntimeParentFrameResumeAudit:
    request = _resume_request(parent_resume_request) if parent_resume_request is not None else None
    decision = _resume_decision(parent_resume_decision) if parent_resume_decision is not None else None
    resume = _parent_resume(parent_resume) if parent_resume is not None else None
    stack = _stack_update(resume_stack_update) if resume_stack_update is not None else None
    trace = _nested_trace(nested_return_resume_trace) if nested_return_resume_trace is not None else None
    blocked_reasons = _audit_blocked_reasons(request, decision, resume, stack, trace)
    audit_status = _audit_status(request, decision, resume, stack, trace, blocked_reasons)
    source_trace_refs = tuple()
    for item in (request, decision, resume, stack, trace):
        if item is not None:
            source_trace_refs += item.source_trace_refs
    return RuntimeParentFrameResumeAudit(
        parent_resume_audit_id=f"runtime_parent_frame_resume_audit:{_slug(audit_status)}",
        schema_version=PARENT_RESUME_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_parent_resume_request_id=request.parent_resume_request_id if request else None,
        source_parent_resume_decision_id=decision.parent_resume_decision_id if decision else None,
        source_parent_resume_id=resume.parent_resume_id if resume else None,
        source_resume_stack_update_id=stack.resume_stack_update_id if stack else None,
        source_nested_return_resume_trace_id=trace.nested_return_resume_trace_id if trace else None,
        child_return_valid=request is None
        or request.child_return_status in ALLOWED_CHILD_RETURN_STATUSES,
        parent_frame_valid=request is None
        or request.parent_resume_request_status != "blocked_missing_parent_frame",
        resume_decision_valid=decision is not None
        and not decision.resume_decision.startswith("blocked_"),
        resume_record_valid=resume is not None and not resume.resume_status.startswith("blocked_"),
        stack_update_valid=stack is None or not stack.stack_update_status.startswith("blocked_"),
        nested_trace_valid=trace is None or trace.trace_status.startswith("nested_return_resume_trace_complete"),
        parent_scope_preserved=decision is None or decision.parent_scope_preserved,
        parent_budget_preserved=decision is None or decision.parent_budget_preserved,
        child_return_payload_consumed=resume is None or resume.child_return_status_consumed,
        parent_resume_verified=resume is not None
        and (
            resume.parent_resumed
            or resume.parent_closed
            or resume.parent_deferred
            or resume.parent_faulted
        ),
        no_new_child_event_created="new_child_event_created" not in blocked_reasons,
        no_dynamic_scheduling="dynamic_scheduling_detected" not in blocked_reasons,
        no_autonomous_scheduler=True,
        no_open_ended_loop=True,
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
        no_free_action_selection="free_action_selection_detected" not in blocked_reasons,
        no_recursive_learning="recursive_learning_detected" not in blocked_reasons,
        no_production_behavior="production_behavior_detected" not in blocked_reasons,
        no_thought_engine_behavior=True,
        audit_status=audit_status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(blocked_reasons),
        source_trace_refs=source_trace_refs,
    )


def resume_parent_frame_from_child_return(
    child_event_frame: RuntimeEventFrameRecord | dict[str, object],
    *,
    parent_event_frame: RuntimeEventFrameRecord | dict[str, object] | None = None,
    dispatch_return_payload: RuntimeEventDispatchReturnPayloadRecord | dict[str, object] | None = None,
    request_payload: dict[str, object] | None = None,
    stack_before_resume: tuple[str, ...] | list[str] | None = None,
) -> dict[str, object]:
    child = _event_frame(child_event_frame)
    parent = _event_frame(parent_event_frame) if parent_event_frame is not None else None
    request = build_runtime_parent_frame_resume_request(
        child,
        parent_event_frame=parent,
        dispatch_return_payload=dispatch_return_payload,
        request_payload=request_payload,
    )
    decision = build_runtime_parent_frame_resume_decision(
        request,
        parent_event_frame=parent,
    )
    resume = build_runtime_parent_frame_resume_record(
        request,
        decision,
        parent_event_frame=parent,
    )
    stack_update = build_runtime_parent_frame_resume_stack_update(
        resume,
        stack_before_resume=stack_before_resume,
    )
    audit = build_runtime_parent_frame_resume_audit(
        parent_resume_request=request,
        parent_resume_decision=decision,
        parent_resume=resume,
        resume_stack_update=stack_update,
    )
    return {
        "runtime_parent_frame_resume_request": request.to_dict(),
        "runtime_parent_frame_resume_decision": decision.to_dict(),
        "runtime_parent_frame_resume": resume.to_dict(),
        "runtime_parent_frame_resume_stack_update": stack_update.to_dict(),
        "runtime_parent_frame_resume_audit": audit.to_dict(),
        "rendered_parent_resume_summary": render_parent_resume_summary_text(
            request,
            decision,
            resume,
            stack_update,
            audit,
        ),
    }


def build_demo_child_success_parent_continue() -> dict[str, object]:
    parent, child = _demo_parent_child_frames("success")
    return resume_parent_frame_from_child_return(
        child,
        parent_event_frame=parent,
        dispatch_return_payload=_demo_dispatch_return_payload(child, "returned_success"),
    )


def build_demo_child_blocked_parent_continue() -> dict[str, object]:
    parent, child = _demo_parent_child_frames("blocked")
    return resume_parent_frame_from_child_return(
        child,
        parent_event_frame=parent,
        dispatch_return_payload=_demo_dispatch_return_payload(child, "returned_blocked"),
    )


def build_demo_child_unknown_parent_deferred() -> dict[str, object]:
    parent, child = _demo_parent_child_frames("unknown")
    return resume_parent_frame_from_child_return(
        child,
        parent_event_frame=parent,
        dispatch_return_payload=_demo_dispatch_return_payload(child, "returned_unknown"),
    )


def build_demo_child_fault_parent_faulted() -> dict[str, object]:
    parent, child = _demo_parent_child_frames("fault")
    return resume_parent_frame_from_child_return(
        child,
        parent_event_frame=parent,
        dispatch_return_payload=_demo_dispatch_return_payload(child, "returned_fault"),
    )


def build_demo_nested_4_to_3_to_2_to_1_resume() -> dict[str, object]:
    loop_payload = build_demo_nested_event_continuous_loop()
    frames = tuple(
        RuntimeEventFrameRecord.from_dict(item)
        for item in loop_payload["runtime_event_frames"]
    )
    frame_by_depth = {frame.event_depth: frame for frame in frames}
    resumes: list[RuntimeParentFrameResumeRecord] = []
    stack_updates: list[RuntimeParentFrameResumeStackUpdateRecord] = []
    for depth in (4, 3, 2):
        child = frame_by_depth[depth]
        parent = frame_by_depth[depth - 1]
        payload = resume_parent_frame_from_child_return(
            child,
            parent_event_frame=parent,
            dispatch_return_payload=_demo_dispatch_return_payload(child, "returned_success"),
            stack_before_resume=tuple(
                frame_by_depth[item].event_frame_id for item in range(1, depth + 1)
            ),
        )
        resumes.append(
            RuntimeParentFrameResumeRecord.from_dict(
                payload["runtime_parent_frame_resume"]
            )
        )
        stack_updates.append(
            RuntimeParentFrameResumeStackUpdateRecord.from_dict(
                payload["runtime_parent_frame_resume_stack_update"]
            )
        )
    root = frame_by_depth[1]
    root_payload = resume_parent_frame_from_child_return(
        root,
        dispatch_return_payload=_demo_dispatch_return_payload(root, "returned_success"),
        stack_before_resume=(root.event_frame_id,),
    )
    resumes.append(
        RuntimeParentFrameResumeRecord.from_dict(
            root_payload["runtime_parent_frame_resume"]
        )
    )
    stack_updates.append(
        RuntimeParentFrameResumeStackUpdateRecord.from_dict(
            root_payload["runtime_parent_frame_resume_stack_update"]
        )
    )
    trace = build_runtime_nested_return_resume_trace(
        parent_resumes=tuple(resumes),
        stack_updates=tuple(stack_updates),
        event_frames=frames,
        loop_trace=RuntimeContinuousLoopTrace.from_dict(
            loop_payload["runtime_continuous_loop_trace"]
        ),
        event_tree=RuntimeEventTreeRecord.from_dict(loop_payload["runtime_event_tree"]),
    )
    audit = build_runtime_parent_frame_resume_audit(
        nested_return_resume_trace=trace,
        parent_resume=resumes[0],
        resume_stack_update=stack_updates[0],
    )
    return {
        "runtime_parent_frame_resumes": [resume.to_dict() for resume in resumes],
        "runtime_parent_frame_resume_stack_updates": [
            update.to_dict() for update in stack_updates
        ],
        "runtime_nested_return_resume_trace": trace.to_dict(),
        "runtime_parent_frame_resume_audit": audit.to_dict(),
        "rendered_nested_return_resume_tree": render_nested_return_resume_tree_text(trace),
    }


def build_demo_blocked_missing_parent_resume() -> dict[str, object]:
    child = _demo_event_frame(
        event_frame_id="runtime_event_frame:package97:missing_parent_child",
        event_depth=2,
        parent_event_frame_id=None,
        event_type="child_missing_parent",
    )
    return resume_parent_frame_from_child_return(
        child,
        dispatch_return_payload=_demo_dispatch_return_payload(child, "returned_success"),
        stack_before_resume=(child.event_frame_id,),
    )


def build_demo_blocked_new_child_event_requested_resume() -> dict[str, object]:
    parent, child = _demo_parent_child_frames("new_child_requested")
    return resume_parent_frame_from_child_return(
        child,
        parent_event_frame=parent,
        dispatch_return_payload=_demo_dispatch_return_payload(child, "returned_success"),
        request_payload={"new_child_event_requested": True},
    )


def build_demo_blocked_forbidden_authority_resume() -> dict[str, object]:
    parent, child = _demo_parent_child_frames("forbidden_authority")
    return resume_parent_frame_from_child_return(
        child,
        parent_event_frame=parent,
        dispatch_return_payload=_demo_dispatch_return_payload(child, "returned_success"),
        request_payload={"memory_layer_write_requested": True},
    )


def render_parent_resume_summary_text(
    request: RuntimeParentFrameResumeRequestRecord | dict[str, object],
    decision: RuntimeParentFrameResumeDecisionRecord | dict[str, object],
    resume: RuntimeParentFrameResumeRecord | dict[str, object],
    stack_update: RuntimeParentFrameResumeStackUpdateRecord | dict[str, object],
    audit: RuntimeParentFrameResumeAudit | dict[str, object],
) -> str:
    request_item = _resume_request(request)
    decision_item = _resume_decision(decision)
    resume_item = _parent_resume(resume)
    stack_item = _stack_update(stack_update)
    audit_item = _resume_audit(audit)
    return (
        f"{request_item.source_child_event_frame_id} returned "
        f"{request_item.child_return_status}; decision={decision_item.resume_decision}; "
        f"resume={resume_item.resume_status}; stack={stack_item.stack_update_status}; "
        f"audit={audit_item.audit_status}"
    )


def render_nested_return_resume_tree_text(
    trace: RuntimeNestedReturnResumeTrace | dict[str, object],
) -> str:
    item = _nested_trace(trace)
    lines = [f"trace_status={item.trace_status}"]
    lines.extend(f"return {entry}" for entry in item.return_sequence)
    lines.extend(f"resume {entry}" for entry in item.resume_sequence)
    return "\n".join(lines)


def _demo_parent_child_frames(suffix: str) -> tuple[RuntimeEventFrameRecord, RuntimeEventFrameRecord]:
    parent = _demo_event_frame(
        event_frame_id=f"runtime_event_frame:package97:{suffix}:event_1",
        event_depth=1,
        parent_event_frame_id=None,
        event_type="parent_event",
    )
    child = _demo_event_frame(
        event_frame_id=f"runtime_event_frame:package97:{suffix}:event_2",
        event_depth=2,
        parent_event_frame_id=parent.event_frame_id,
        event_type="child_event",
    )
    return parent, child


def _demo_event_frame(
    *,
    event_frame_id: str,
    event_depth: int,
    parent_event_frame_id: str | None,
    event_type: str,
) -> RuntimeEventFrameRecord:
    return RuntimeEventFrameRecord(
        event_frame_id=event_frame_id,
        schema_version=EVENT_FRAME_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_power_window_id="runtime_power_window:package97_demo",
        event_type=event_type,
        event_label=f"package97_{_slug(event_type)}",
        event_depth=event_depth,
        parent_event_frame_id=parent_event_frame_id,
        child_event_frame_ids=tuple(),
        opened_at_tick_index=event_depth,
        closed_at_tick_index=event_depth + 1,
        event_scope="bounded_runtime_window",
        event_budget_ticks=16,
        event_ticks_used=1,
        event_status="event_closed_returned",
        event_summary=f"Package 97 demo EventFrame depth {event_depth}.",
        return_payload_id=None,
        return_payload_status="none",
        child_scope_expansion_detected=False,
        budget_exceeded=False,
        unclosed_frame_detected=False,
        memory_write_performed=False,
        automatic_learning_approval_created=False,
        free_action_selection_created=False,
        external_execution_created=False,
        production_behavior_created=False,
        source_trace_refs=("package_97_parent_resume_demo",),
    )


def _demo_dispatch_return_payload(
    child: RuntimeEventFrameRecord,
    return_status: str,
) -> RuntimeEventDispatchReturnPayloadRecord:
    return RuntimeEventDispatchReturnPayloadRecord(
        dispatch_return_payload_id=f"runtime_event_dispatch_return_payload:package97:{child.event_frame_id}:{_slug(return_status)}",
        schema_version=DISPATCH_RETURN_PAYLOAD_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_dispatch_result_id=f"runtime_event_dispatch_result:package97:{child.event_frame_id}",
        source_event_frame_id=child.event_frame_id,
        parent_event_frame_id=child.parent_event_frame_id,
        target_engine="task_engine",
        event_type=child.event_type,
        return_status=return_status,
        return_reason=f"package97_demo_{return_status}",
        return_summary=f"Package 97 demo child return {return_status}.",
        return_payload={
            "child_event_frame_id": child.event_frame_id,
            "child_event_depth": child.event_depth,
            "child_event_ticks_used": child.event_ticks_used,
            "return_tick_index": child.closed_at_tick_index,
        },
        safe_for_event_frame_return=True,
        safe_for_parent_resume=True,
        creates_new_event=False,
        requires_child_event=False,
        requires_parent_resume=child.parent_event_frame_id is not None,
        external_execution_created=False,
        memory_layer_write_performed=False,
        automatic_learning_approval_created=False,
        free_action_selection_created=False,
        recursive_learning_created=False,
        production_behavior_created=False,
        source_trace_refs=child.source_trace_refs,
    )


def _request_summary(status: str, child_return_status: str) -> str:
    if status == "parent_resume_request_created":
        return f"Parent resume request created for child return {child_return_status}."
    if status == "blocked_missing_parent_frame":
        return "Parent resume request blocked because non-root child has no parent."
    if status == "blocked_invalid_child_return":
        return "Parent resume request blocked because child return is invalid."
    if status == "blocked_scope_expansion_requested":
        return "Parent resume request blocked because scope expansion was requested."
    if status == "blocked_budget_extension_requested":
        return "Parent resume request blocked because budget extension was requested."
    if status == "blocked_new_child_event_requested":
        return "Parent resume request blocked because new child event was requested."
    return "Parent resume request blocked because forbidden authority was requested."


def _decision_reason(decision: str, child_return_status: str) -> str:
    return f"{decision}_from_{child_return_status}"


def _decision_summary(decision: str) -> str:
    if decision == "resume_continue_parent":
        return "Parent can continue after child success."
    if decision == "resume_continue_parent_with_child_blocked":
        return "Parent can continue while preserving blocked child evidence."
    if decision == "resume_defer_parent":
        return "Parent deferred after child returned unknown or deferred."
    if decision == "resume_fault_parent":
        return "Parent faulted after child fault."
    if decision == "close_root_event":
        return "Root event closed after its own return."
    if decision == "close_parent_after_child_success":
        return "Parent closed after child success."
    return f"Parent resume blocked by {decision}."


def _resume_status_from_decision(decision: str) -> str:
    return {
        "resume_continue_parent": "parent_resumed_continue",
        "resume_continue_parent_with_child_blocked": (
            "parent_resumed_continue_with_child_blocked"
        ),
        "resume_defer_parent": "parent_deferred_after_child_return",
        "resume_block_parent": "parent_blocked_after_child_return",
        "resume_fault_parent": "parent_faulted_after_child_return",
        "close_parent_after_child_success": "parent_closed_after_child_return",
        "close_root_event": "root_event_closed",
        "blocked_missing_parent_frame": "blocked_missing_parent_frame",
        "blocked_invalid_return_payload": "blocked_forbidden_authority_detected",
        "blocked_parent_budget_exhausted": "blocked_parent_budget_exhausted",
        "blocked_forbidden_authority_detected": "blocked_forbidden_authority_detected",
    }[decision]


def _parent_status_after_resume(resume_status: str) -> str:
    if resume_status in {
        "parent_resumed_continue",
        "parent_resumed_continue_with_child_blocked",
    }:
        return "event_continued"
    if resume_status in {"parent_closed_after_child_return", "root_event_closed"}:
        return "event_closed_returned"
    if resume_status == "parent_deferred_after_child_return":
        return "event_deferred_after_child_return"
    if resume_status == "parent_faulted_after_child_return":
        return "event_faulted_after_child_return"
    return "event_blocked_after_child_return"


def _resume_summary(resume_status: str) -> str:
    return resume_status.replace("_", " ")


def _stack_update_summary(status: str) -> str:
    return status.replace("_", " ")


def _trace_summary(status: str) -> str:
    return status.replace("_", " ")


def _return_sequence_item(
    resume: RuntimeParentFrameResumeRecord,
    frame_depth_by_id: dict[str, int],
) -> str:
    child_depth = frame_depth_by_id.get(resume.source_child_event_frame_id, 0)
    parent_id = resume.source_parent_event_frame_id
    if parent_id is None:
        return f"event_{child_depth}_closed"
    parent_depth = frame_depth_by_id.get(parent_id, 0)
    return f"event_{child_depth}_returned_to_event_{parent_depth}"


def _resume_sequence_item(
    resume: RuntimeParentFrameResumeRecord,
    frame_depth_by_id: dict[str, int],
) -> str:
    child_depth = frame_depth_by_id.get(resume.source_child_event_frame_id, 0)
    parent_depth = frame_depth_by_id.get(resume.source_parent_event_frame_id or "", 0)
    return f"event_{parent_depth}_resumed_after_event_{child_depth}"


def _audit_blocked_reasons(
    request: RuntimeParentFrameResumeRequestRecord | None,
    decision: RuntimeParentFrameResumeDecisionRecord | None,
    resume: RuntimeParentFrameResumeRecord | None,
    stack: RuntimeParentFrameResumeStackUpdateRecord | None,
    trace: RuntimeNestedReturnResumeTrace | None,
) -> list[str]:
    reasons: list[str] = []
    if request is not None:
        if request.new_child_event_requested:
            reasons.append("new_child_event_created")
        if request.external_execution_requested:
            reasons.append("external_execution_detected")
        if request.memory_layer_write_requested:
            reasons.append("memory_write_detected")
        if request.automatic_learning_approval_requested:
            reasons.append("automatic_learning_approval_detected")
        if request.free_action_selection_requested:
            reasons.append("free_action_selection_detected")
        if request.recursive_learning_requested:
            reasons.append("recursive_learning_detected")
        if request.production_behavior_requested:
            reasons.append("production_behavior_detected")
    if resume is not None:
        if resume.new_child_event_created:
            reasons.append("new_child_event_created")
        if resume.dynamic_scheduling_created:
            reasons.append("dynamic_scheduling_detected")
        if resume.external_execution_created:
            reasons.append("external_execution_detected")
        if resume.memory_layer_write_performed:
            reasons.append("memory_write_detected")
        if resume.automatic_learning_approval_created:
            reasons.append("automatic_learning_approval_detected")
        if resume.recursive_learning_created:
            reasons.append("recursive_learning_detected")
        if resume.production_behavior_created:
            reasons.append("production_behavior_detected")
    if trace is not None:
        if trace.new_child_event_created:
            reasons.append("new_child_event_created")
        if trace.dynamic_scheduling_created:
            reasons.append("dynamic_scheduling_detected")
        if trace.external_execution_created:
            reasons.append("external_execution_detected")
        if trace.memory_layer_write_performed:
            reasons.append("memory_write_detected")
        if trace.automatic_learning_approval_created:
            reasons.append("automatic_learning_approval_detected")
        if trace.recursive_learning_created:
            reasons.append("recursive_learning_detected")
        if trace.production_behavior_created:
            reasons.append("production_behavior_detected")
    if decision is not None and not decision.new_child_event_creation_allowed:
        pass
    if stack is not None and stack.stack_update_status.startswith("blocked_"):
        reasons.append("invalid_stack_update")
    return list(dict.fromkeys(reasons))


def _audit_status(
    request: RuntimeParentFrameResumeRequestRecord | None,
    decision: RuntimeParentFrameResumeDecisionRecord | None,
    resume: RuntimeParentFrameResumeRecord | None,
    stack: RuntimeParentFrameResumeStackUpdateRecord | None,
    trace: RuntimeNestedReturnResumeTrace | None,
    blocked_reasons: list[str],
) -> str:
    priority = (
        ("new_child_event_created", "blocked_new_child_event_created"),
        ("dynamic_scheduling_detected", "blocked_dynamic_scheduling_detected"),
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
    if request is not None:
        if request.parent_resume_request_status == "blocked_missing_parent_frame":
            return "blocked_missing_parent_frame"
        if request.parent_resume_request_status == "blocked_invalid_child_return":
            return "blocked_invalid_child_return"
    if decision is not None and decision.resume_decision.startswith("blocked_"):
        return "blocked_invalid_resume_decision"
    if stack is not None and stack.stack_update_status.startswith("blocked_"):
        return "blocked_invalid_stack_update"
    if trace is not None:
        if trace.trace_status == "nested_return_resume_trace_complete":
            return "passed_nested_return_resume_trace"
        if trace.trace_status.endswith("invalid_stack_update"):
            return "blocked_invalid_stack_update"
    if resume is not None:
        if resume.parent_faulted:
            return "passed_parent_frame_faulted_after_child_fault"
        if resume.parent_deferred:
            return "passed_parent_frame_deferred_after_child_unknown"
        if resume.resume_status == "parent_resumed_continue_with_child_blocked":
            return "passed_parent_frame_resume_after_child_blocked"
    return "passed_parent_frame_resume_after_child_success"


def _event_frame(value: RuntimeEventFrameRecord | dict[str, object]) -> RuntimeEventFrameRecord:
    if isinstance(value, RuntimeEventFrameRecord):
        return value
    return RuntimeEventFrameRecord.from_dict(value)


def _event_return(value: RuntimeEventReturnRecord | dict[str, object]) -> RuntimeEventReturnRecord:
    if isinstance(value, RuntimeEventReturnRecord):
        return value
    return RuntimeEventReturnRecord.from_dict(value)


def _dispatch_return_payload(
    value: RuntimeEventDispatchReturnPayloadRecord | dict[str, object],
) -> RuntimeEventDispatchReturnPayloadRecord:
    if isinstance(value, RuntimeEventDispatchReturnPayloadRecord):
        return value
    return RuntimeEventDispatchReturnPayloadRecord.from_dict(value)


def _loop_trace(
    value: RuntimeContinuousLoopTrace | dict[str, object],
) -> RuntimeContinuousLoopTrace:
    if isinstance(value, RuntimeContinuousLoopTrace):
        return value
    return RuntimeContinuousLoopTrace.from_dict(value)


def _event_tree(value: RuntimeEventTreeRecord | dict[str, object]) -> RuntimeEventTreeRecord:
    if isinstance(value, RuntimeEventTreeRecord):
        return value
    return RuntimeEventTreeRecord.from_dict(value)


def _resume_request(
    value: RuntimeParentFrameResumeRequestRecord | dict[str, object],
) -> RuntimeParentFrameResumeRequestRecord:
    if isinstance(value, RuntimeParentFrameResumeRequestRecord):
        return value
    return RuntimeParentFrameResumeRequestRecord.from_dict(value)


def _resume_decision(
    value: RuntimeParentFrameResumeDecisionRecord | dict[str, object],
) -> RuntimeParentFrameResumeDecisionRecord:
    if isinstance(value, RuntimeParentFrameResumeDecisionRecord):
        return value
    return RuntimeParentFrameResumeDecisionRecord.from_dict(value)


def _parent_resume(
    value: RuntimeParentFrameResumeRecord | dict[str, object],
) -> RuntimeParentFrameResumeRecord:
    if isinstance(value, RuntimeParentFrameResumeRecord):
        return value
    return RuntimeParentFrameResumeRecord.from_dict(value)


def _stack_update(
    value: RuntimeParentFrameResumeStackUpdateRecord | dict[str, object],
) -> RuntimeParentFrameResumeStackUpdateRecord:
    if isinstance(value, RuntimeParentFrameResumeStackUpdateRecord):
        return value
    return RuntimeParentFrameResumeStackUpdateRecord.from_dict(value)


def _nested_trace(
    value: RuntimeNestedReturnResumeTrace | dict[str, object],
) -> RuntimeNestedReturnResumeTrace:
    if isinstance(value, RuntimeNestedReturnResumeTrace):
        return value
    return RuntimeNestedReturnResumeTrace.from_dict(value)


def _resume_audit(
    value: RuntimeParentFrameResumeAudit | dict[str, object],
) -> RuntimeParentFrameResumeAudit:
    if isinstance(value, RuntimeParentFrameResumeAudit):
        return value
    return RuntimeParentFrameResumeAudit.from_dict(value)
