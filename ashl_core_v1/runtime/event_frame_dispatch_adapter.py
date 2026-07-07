"""Adapter-only dispatch records for bounded runtime EventFrames."""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any

from ashl_core_v1.runtime.continuous_event_loop import (
    EVENT_FRAME_SCHEMA_VERSION,
    SOURCE_ENGINE,
    RuntimeEventFrameRecord,
)


DISPATCH_REQUEST_SCHEMA_VERSION = "runtime_event_dispatch_request_v0"
DISPATCH_ROUTE_SCHEMA_VERSION = "runtime_event_dispatch_route_v0"
HANDLER_ADAPTER_SCHEMA_VERSION = "runtime_event_handler_adapter_v0"
DISPATCH_RESULT_SCHEMA_VERSION = "runtime_event_dispatch_result_v0"
DISPATCH_RETURN_PAYLOAD_SCHEMA_VERSION = "runtime_event_dispatch_return_payload_v0"
DISPATCH_AUDIT_SCHEMA_VERSION = "runtime_event_dispatch_audit_v0"

DEFAULT_MAX_EVENT_BUDGET_TICKS = 256

TASK_EVENT_TYPES = {
    "task_initialization",
    "task_trial",
    "action_chain",
    "candidate_ordering",
    "selected_action_application",
    "final_action_application",
    "direct_command_creation",
    "sandbox_execution",
    "outcome_evaluation",
    "task_closure",
    "mismatch_detection",
}
SENSE_EVENT_TYPES = {
    "sense_observation",
    "sense_handoff",
}
LEARNING_EVENT_TYPES = {
    "learning_feedback_intake",
    "concept_candidate_review",
    "reviewed_concept_creation",
}
MEMORY_EVENT_TYPES = {
    "memory_readback",
    "working_readback_integration",
}
STATE_EVENT_TYPES = {
    "state_snapshot_request",
}
THOUGHT_EVENT_TYPES = {
    "thought_preview",
}
OUTPUT_EVENT_TYPES = {
    "output_candidate",
}
RUNTIME_EVENT_TYPES = {
    "idle_heartbeat",
}
AUDIT_EVENT_TYPES = {
    "loop_audit",
}

ALLOWED_EVENT_FAMILIES = {
    "runtime_event",
    "state_event",
    "task_event",
    "sense_event",
    "learning_event",
    "memory_event",
    "thought_event",
    "output_event",
    "audit_event",
    "unknown_event",
}
ALLOWED_DISPATCH_REQUEST_STATUSES = {
    "dispatch_request_created",
    "blocked_invalid_event_frame",
    "blocked_unknown_event_type",
    "blocked_forbidden_authority_requested",
    "blocked_unbounded_budget",
}
ALLOWED_TARGET_ENGINES = {
    "runtime",
    "state_engine",
    "task_engine",
    "sense_interface",
    "learning_engine",
    "memory_engine",
    "thought_engine",
    "output_interface",
    "audit_layer",
    "none",
}
ALLOWED_ROUTE_STATUSES = {
    "routed_to_runtime",
    "routed_to_state_engine",
    "routed_to_task_engine",
    "routed_to_sense_interface",
    "routed_to_learning_engine",
    "routed_to_memory_engine",
    "routed_to_output_interface",
    "routed_to_audit_layer",
    "deferred_thought_engine_not_available",
    "blocked_unknown_event_type",
    "blocked_handler_not_available",
    "blocked_forbidden_authority_detected",
}
ALLOWED_ADAPTER_KINDS = {
    "runtime_adapter",
    "state_engine_adapter",
    "task_engine_adapter",
    "sense_interface_adapter",
    "learning_engine_adapter",
    "memory_engine_adapter",
    "thought_engine_deferred_adapter",
    "output_interface_adapter",
    "audit_layer_adapter",
    "blocked_unknown_adapter",
}
ALLOWED_HANDLER_INVOCATION_MODES = {
    "record_only_adapter",
    "bounded_demo_adapter",
    "deferred_not_invoked",
    "blocked_not_invoked",
}
ALLOWED_ADAPTER_STATUSES = {
    "adapter_record_created",
    "adapter_demo_payload_created",
    "deferred_engine_not_available",
    "blocked_unknown_event_type",
    "blocked_forbidden_authority_detected",
}
ALLOWED_DISPATCH_RESULT_STATUSES = {
    "dispatch_completed_adapter_only",
    "dispatch_completed_bounded_demo",
    "dispatch_deferred_engine_not_available",
    "dispatch_blocked_unknown_event_type",
    "dispatch_blocked_forbidden_authority_detected",
    "dispatch_blocked_handler_failure",
}
ALLOWED_RETURN_STATUSES = {
    "returned_success",
    "returned_blocked",
    "returned_unknown",
    "returned_deferred",
    "returned_fault",
    "blocked_forbidden_authority_detected",
}
ALLOWED_AUDIT_STATUSES = {
    "passed_event_dispatch_adapter_only",
    "passed_event_dispatch_bounded_demo",
    "passed_thought_engine_deferred",
    "blocked_unknown_event_type",
    "blocked_invalid_route",
    "blocked_invalid_adapter",
    "blocked_external_execution_detected",
    "blocked_memory_write_detected",
    "blocked_automatic_learning_approval_detected",
    "blocked_free_action_selection_detected",
    "blocked_recursive_learning_detected",
    "blocked_production_behavior_detected",
    "blocked_thought_engine_fake_detected",
}

TARGET_BY_FAMILY = {
    "runtime_event": ("runtime", "routed_to_runtime", "runtime_adapter"),
    "state_event": ("state_engine", "routed_to_state_engine", "state_engine_adapter"),
    "task_event": ("task_engine", "routed_to_task_engine", "task_engine_adapter"),
    "sense_event": (
        "sense_interface",
        "routed_to_sense_interface",
        "sense_interface_adapter",
    ),
    "learning_event": (
        "learning_engine",
        "routed_to_learning_engine",
        "learning_engine_adapter",
    ),
    "memory_event": (
        "memory_engine",
        "routed_to_memory_engine",
        "memory_engine_adapter",
    ),
    "output_event": (
        "output_interface",
        "routed_to_output_interface",
        "output_interface_adapter",
    ),
    "audit_event": ("audit_layer", "routed_to_audit_layer", "audit_layer_adapter"),
}

SAFE_CLAIM = (
    "ASHL Core v1 can route bounded Runtime EventFrames through adapter-only "
    "dispatch records to target engine lanes and produce safe return payloads "
    "for parent EventFrame resume."
)
BLOCKED_CLAIMS = (
    "no_live_autonomous_event_dispatcher",
    "no_dynamic_child_event_scheduling",
    "no_free_event_creation",
    "no_live_engine_behavior_invocation",
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
class RuntimeEventDispatchRequestRecord:
    dispatch_request_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_event_frame_id: str
    source_power_window_id: str | None
    source_runtime_tick_id: str | None
    event_type: str
    event_label: str
    event_depth: int
    event_scope: str
    event_budget_ticks: int
    event_payload: dict[str, object]
    dispatch_requested: bool
    dispatch_request_status: str
    dispatch_request_summary: str
    free_action_selection_requested: bool
    external_execution_requested: bool
    memory_layer_write_requested: bool
    automatic_learning_approval_requested: bool
    recursive_learning_requested: bool
    production_behavior_requested: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DISPATCH_REQUEST_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_event_dispatch_request_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.dispatch_request_status not in ALLOWED_DISPATCH_REQUEST_STATUSES:
            raise ValueError(
                f"unknown dispatch_request_status: {self.dispatch_request_status}"
            )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeEventDispatchRequestRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeEventDispatchRouteRecord:
    dispatch_route_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_dispatch_request_id: str
    source_event_frame_id: str
    event_type: str
    event_family: str
    target_engine: str
    target_handler_name: str | None
    handler_available: bool
    handler_required: bool
    route_status: str
    route_reason: str
    route_summary: str
    route_is_adapter_only: bool
    route_invokes_engine_runtime: bool
    external_execution_allowed: bool
    memory_layer_write_allowed: bool
    automatic_learning_approval_allowed: bool
    free_action_selection_allowed: bool
    recursive_learning_allowed: bool
    production_behavior_allowed: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DISPATCH_ROUTE_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_event_dispatch_route_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.event_family not in ALLOWED_EVENT_FAMILIES:
            raise ValueError(f"unknown event_family: {self.event_family}")
        if self.target_engine not in ALLOWED_TARGET_ENGINES:
            raise ValueError(f"unknown target_engine: {self.target_engine}")
        if self.route_status not in ALLOWED_ROUTE_STATUSES:
            raise ValueError(f"unknown route_status: {self.route_status}")
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeEventDispatchRouteRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeEventHandlerAdapterRecord:
    handler_adapter_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_dispatch_route_id: str
    source_event_frame_id: str
    target_engine: str
    target_handler_name: str | None
    adapter_kind: str
    adapter_status: str
    adapter_summary: str
    input_payload_shape: str
    output_payload_shape: str
    handler_invoked: bool
    handler_invocation_mode: str
    bounded_demo_only: bool
    adapter_record_only: bool
    created_task_record: bool
    created_sense_record: bool
    created_learning_record: bool
    created_memory_record: bool
    created_state_record: bool
    created_output_record: bool
    created_thought_record: bool
    external_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    free_action_selection_created: bool
    recursive_learning_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != HANDLER_ADAPTER_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_event_handler_adapter_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.target_engine not in ALLOWED_TARGET_ENGINES:
            raise ValueError(f"unknown target_engine: {self.target_engine}")
        if self.adapter_kind not in ALLOWED_ADAPTER_KINDS:
            raise ValueError(f"unknown adapter_kind: {self.adapter_kind}")
        if self.adapter_status not in ALLOWED_ADAPTER_STATUSES:
            raise ValueError(f"unknown adapter_status: {self.adapter_status}")
        if self.handler_invocation_mode not in ALLOWED_HANDLER_INVOCATION_MODES:
            raise ValueError(
                f"unknown handler_invocation_mode: {self.handler_invocation_mode}"
            )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeEventHandlerAdapterRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeEventDispatchResultRecord:
    dispatch_result_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_dispatch_request_id: str
    source_dispatch_route_id: str
    source_handler_adapter_id: str
    source_event_frame_id: str
    target_engine: str
    dispatch_result_status: str
    dispatch_result_reason: str
    dispatch_result_summary: str
    handler_available: bool
    handler_completed: bool
    result_payload: dict[str, object]
    return_payload_required: bool
    return_payload_id: str | None
    parent_event_frame_id: str | None
    parent_resume_allowed: bool
    external_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    free_action_selection_created: bool
    recursive_learning_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DISPATCH_RESULT_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_event_dispatch_result_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.target_engine not in ALLOWED_TARGET_ENGINES:
            raise ValueError(f"unknown target_engine: {self.target_engine}")
        if self.dispatch_result_status not in ALLOWED_DISPATCH_RESULT_STATUSES:
            raise ValueError(
                f"unknown dispatch_result_status: {self.dispatch_result_status}"
            )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeEventDispatchResultRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeEventDispatchReturnPayloadRecord:
    dispatch_return_payload_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_dispatch_result_id: str
    source_event_frame_id: str
    parent_event_frame_id: str | None
    target_engine: str
    event_type: str
    return_status: str
    return_reason: str
    return_summary: str
    return_payload: dict[str, object]
    safe_for_event_frame_return: bool
    safe_for_parent_resume: bool
    creates_new_event: bool
    requires_child_event: bool
    requires_parent_resume: bool
    external_execution_created: bool
    memory_layer_write_performed: bool
    automatic_learning_approval_created: bool
    free_action_selection_created: bool
    recursive_learning_created: bool
    production_behavior_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DISPATCH_RETURN_PAYLOAD_SCHEMA_VERSION:
            raise ValueError(
                "schema_version must be runtime_event_dispatch_return_payload_v0"
            )
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.target_engine not in ALLOWED_TARGET_ENGINES:
            raise ValueError(f"unknown target_engine: {self.target_engine}")
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
    def from_dict(
        cls, data: dict[str, object]
    ) -> "RuntimeEventDispatchReturnPayloadRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class RuntimeEventDispatchAudit:
    dispatch_audit_id: str
    schema_version: str
    created_at: str
    source_engine: str
    source_dispatch_request_id: str | None
    source_dispatch_route_id: str | None
    source_handler_adapter_id: str | None
    source_dispatch_result_id: str | None
    source_dispatch_return_payload_id: str | None
    event_frame_valid: bool
    event_type_classified: bool
    route_valid: bool
    adapter_valid: bool
    dispatch_result_valid: bool
    return_payload_valid: bool
    target_engine: str | None
    handler_available: bool
    handler_invoked: bool
    adapter_only_confirmed: bool
    bounded_demo_only_confirmed: bool
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
    no_thought_engine_faked: bool
    audit_status: str
    safe_claim: str
    blocked_claims: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != DISPATCH_AUDIT_SCHEMA_VERSION:
            raise ValueError("schema_version must be runtime_event_dispatch_audit_v0")
        if self.source_engine != SOURCE_ENGINE:
            raise ValueError("source_engine must be runtime")
        if self.target_engine is not None and self.target_engine not in ALLOWED_TARGET_ENGINES:
            raise ValueError(f"unknown target_engine: {self.target_engine}")
        if self.audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"unknown audit_status: {self.audit_status}")
        for name in ("blocked_claims", "blocked_reasons", "source_trace_refs"):
            object.__setattr__(self, name, _tuple_of_str(name, getattr(self, name)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RuntimeEventDispatchAudit":
        return cls(**dict(data))


def classify_runtime_event_type(event_type: str) -> str:
    if event_type in RUNTIME_EVENT_TYPES:
        return "runtime_event"
    if event_type in STATE_EVENT_TYPES:
        return "state_event"
    if event_type in TASK_EVENT_TYPES:
        return "task_event"
    if event_type in SENSE_EVENT_TYPES:
        return "sense_event"
    if event_type in LEARNING_EVENT_TYPES:
        return "learning_event"
    if event_type in MEMORY_EVENT_TYPES:
        return "memory_event"
    if event_type in THOUGHT_EVENT_TYPES:
        return "thought_event"
    if event_type in OUTPUT_EVENT_TYPES:
        return "output_event"
    if event_type in AUDIT_EVENT_TYPES:
        return "audit_event"
    return "unknown_event"


def validate_runtime_event_dispatch_request(
    record: RuntimeEventDispatchRequestRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _dispatch_request(record)
    except Exception as error:  # pragma: no cover - defensive schema guard
        return {"valid": False, "error": str(error)}
    return {
        "valid": True,
        "dispatch_request_id": item.dispatch_request_id,
        "dispatch_request_status": item.dispatch_request_status,
    }


def validate_runtime_event_dispatch_route(
    record: RuntimeEventDispatchRouteRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _dispatch_route(record)
    except Exception as error:  # pragma: no cover - defensive schema guard
        return {"valid": False, "error": str(error)}
    return {
        "valid": True,
        "dispatch_route_id": item.dispatch_route_id,
        "route_status": item.route_status,
    }


def validate_runtime_event_handler_adapter(
    record: RuntimeEventHandlerAdapterRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _handler_adapter(record)
    except Exception as error:  # pragma: no cover - defensive schema guard
        return {"valid": False, "error": str(error)}
    return {
        "valid": True,
        "handler_adapter_id": item.handler_adapter_id,
        "adapter_status": item.adapter_status,
    }


def validate_runtime_event_dispatch_result(
    record: RuntimeEventDispatchResultRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _dispatch_result(record)
    except Exception as error:  # pragma: no cover - defensive schema guard
        return {"valid": False, "error": str(error)}
    return {
        "valid": True,
        "dispatch_result_id": item.dispatch_result_id,
        "dispatch_result_status": item.dispatch_result_status,
    }


def validate_runtime_event_dispatch_return_payload(
    record: RuntimeEventDispatchReturnPayloadRecord | dict[str, object],
) -> dict[str, object]:
    try:
        item = _return_payload(record)
    except Exception as error:  # pragma: no cover - defensive schema guard
        return {"valid": False, "error": str(error)}
    return {
        "valid": True,
        "dispatch_return_payload_id": item.dispatch_return_payload_id,
        "return_status": item.return_status,
    }


def validate_runtime_event_dispatch_audit(
    record: RuntimeEventDispatchAudit | dict[str, object],
) -> dict[str, object]:
    try:
        item = _dispatch_audit(record)
    except Exception as error:  # pragma: no cover - defensive schema guard
        return {"valid": False, "error": str(error)}
    return {
        "valid": True,
        "dispatch_audit_id": item.dispatch_audit_id,
        "audit_status": item.audit_status,
    }


def build_runtime_event_dispatch_request(
    event_frame: RuntimeEventFrameRecord | dict[str, object],
    *,
    event_payload: dict[str, object] | None = None,
    source_runtime_tick_id: str | None = None,
    max_event_budget_ticks: int = DEFAULT_MAX_EVENT_BUDGET_TICKS,
) -> RuntimeEventDispatchRequestRecord:
    payload = dict(event_payload or {})
    created_at = _now()
    try:
        frame = _event_frame(event_frame)
        event_type = frame.event_type
        event_label = frame.event_label
        event_depth = frame.event_depth
        event_scope = frame.event_scope
        event_budget_ticks = frame.event_budget_ticks
        source_event_frame_id = frame.event_frame_id
        source_power_window_id = frame.source_power_window_id
        source_trace_refs = frame.source_trace_refs
        invalid_frame = frame.schema_version != EVENT_FRAME_SCHEMA_VERSION
    except Exception:
        event_type = str(payload.get("event_type", "unknown"))
        event_label = str(payload.get("event_label", "invalid_event_frame"))
        event_depth = int(payload.get("event_depth", 0) or 0)
        event_scope = str(payload.get("event_scope", "invalid_event_scope"))
        event_budget_ticks = int(payload.get("event_budget_ticks", 0) or 0)
        source_event_frame_id = str(payload.get("source_event_frame_id", "invalid_event_frame"))
        source_power_window_id = None
        source_trace_refs = tuple()
        invalid_frame = True

    forbidden_requested = any(
        _bool_payload(payload, key)
        for key in (
            "free_action_selection_requested",
            "external_execution_requested",
            "memory_layer_write_requested",
            "automatic_learning_approval_requested",
            "recursive_learning_requested",
            "production_behavior_requested",
        )
    )
    event_family = classify_runtime_event_type(event_type)
    if invalid_frame:
        status = "blocked_invalid_event_frame"
    elif event_family == "unknown_event":
        status = "blocked_unknown_event_type"
    elif forbidden_requested:
        status = "blocked_forbidden_authority_requested"
    elif event_budget_ticks <= 0 or event_budget_ticks > max_event_budget_ticks:
        status = "blocked_unbounded_budget"
    else:
        status = "dispatch_request_created"

    return RuntimeEventDispatchRequestRecord(
        dispatch_request_id=f"runtime_event_dispatch_request:{source_event_frame_id}:{_slug(event_type)}",
        schema_version=DISPATCH_REQUEST_SCHEMA_VERSION,
        created_at=created_at,
        source_engine=SOURCE_ENGINE,
        source_event_frame_id=source_event_frame_id,
        source_power_window_id=source_power_window_id,
        source_runtime_tick_id=source_runtime_tick_id,
        event_type=event_type,
        event_label=event_label,
        event_depth=event_depth,
        event_scope=event_scope,
        event_budget_ticks=event_budget_ticks,
        event_payload=payload,
        dispatch_requested=True,
        dispatch_request_status=status,
        dispatch_request_summary=_dispatch_request_summary(status, event_type),
        free_action_selection_requested=_bool_payload(
            payload, "free_action_selection_requested"
        ),
        external_execution_requested=_bool_payload(
            payload, "external_execution_requested"
        ),
        memory_layer_write_requested=_bool_payload(
            payload, "memory_layer_write_requested"
        ),
        automatic_learning_approval_requested=_bool_payload(
            payload, "automatic_learning_approval_requested"
        ),
        recursive_learning_requested=_bool_payload(
            payload, "recursive_learning_requested"
        ),
        production_behavior_requested=_bool_payload(
            payload, "production_behavior_requested"
        ),
        source_trace_refs=source_trace_refs,
    )


def build_runtime_event_dispatch_route(
    dispatch_request: RuntimeEventDispatchRequestRecord | dict[str, object],
    *,
    thought_handler_available: bool = False,
) -> RuntimeEventDispatchRouteRecord:
    request = _dispatch_request(dispatch_request)
    event_family = classify_runtime_event_type(request.event_type)
    target_engine = "none"
    route_status = "blocked_unknown_event_type"
    adapter_kind = "blocked_unknown_adapter"
    handler_available = False
    target_handler_name = None
    route_reason = "event_type_unknown_or_blocked"

    if request.dispatch_request_status == "blocked_forbidden_authority_requested":
        route_status = "blocked_forbidden_authority_detected"
        route_reason = "forbidden_authority_was_requested"
    elif request.dispatch_request_status in {
        "blocked_invalid_event_frame",
        "blocked_unbounded_budget",
    }:
        route_status = "blocked_handler_not_available"
        route_reason = request.dispatch_request_status
    elif event_family == "thought_event":
        target_engine = "thought_engine"
        route_status = (
            "routed_to_runtime"
            if thought_handler_available
            else "deferred_thought_engine_not_available"
        )
        adapter_kind = "thought_engine_deferred_adapter"
        handler_available = thought_handler_available
        target_handler_name = "handle_thought_event_adapter" if thought_handler_available else None
        route_reason = "thought_engine_not_available" if not thought_handler_available else "thought_engine_available"
    elif event_family in TARGET_BY_FAMILY:
        target_engine, route_status, adapter_kind = TARGET_BY_FAMILY[event_family]
        handler_available = True
        target_handler_name = f"handle_{_slug(request.event_type)}_adapter"
        route_reason = f"{event_family}_mapped_to_{target_engine}"

    return RuntimeEventDispatchRouteRecord(
        dispatch_route_id=f"runtime_event_dispatch_route:{request.source_event_frame_id}:{_slug(request.event_type)}",
        schema_version=DISPATCH_ROUTE_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_dispatch_request_id=request.dispatch_request_id,
        source_event_frame_id=request.source_event_frame_id,
        event_type=request.event_type,
        event_family=event_family,
        target_engine=target_engine,
        target_handler_name=target_handler_name,
        handler_available=handler_available,
        handler_required=event_family != "unknown_event",
        route_status=route_status,
        route_reason=route_reason,
        route_summary=_route_summary(route_status, request.event_type, target_engine),
        route_is_adapter_only=True,
        route_invokes_engine_runtime=False,
        external_execution_allowed=False,
        memory_layer_write_allowed=False,
        automatic_learning_approval_allowed=False,
        free_action_selection_allowed=False,
        recursive_learning_allowed=False,
        production_behavior_allowed=False,
        source_trace_refs=request.source_trace_refs,
    )


def build_runtime_event_handler_adapter(
    dispatch_route: RuntimeEventDispatchRouteRecord | dict[str, object],
) -> RuntimeEventHandlerAdapterRecord:
    route = _dispatch_route(dispatch_route)
    adapter_kind = _adapter_kind_for_route(route)
    adapter_status = "adapter_record_created"
    invocation_mode = "record_only_adapter"
    if route.route_status == "deferred_thought_engine_not_available":
        adapter_status = "deferred_engine_not_available"
        invocation_mode = "deferred_not_invoked"
    elif route.route_status == "blocked_unknown_event_type":
        adapter_status = "blocked_unknown_event_type"
        invocation_mode = "blocked_not_invoked"
    elif route.route_status == "blocked_forbidden_authority_detected":
        adapter_status = "blocked_forbidden_authority_detected"
        invocation_mode = "blocked_not_invoked"
    elif route.route_status == "blocked_handler_not_available":
        adapter_status = "blocked_unknown_event_type"
        invocation_mode = "blocked_not_invoked"

    return RuntimeEventHandlerAdapterRecord(
        handler_adapter_id=f"runtime_event_handler_adapter:{route.source_event_frame_id}:{_slug(route.event_type)}",
        schema_version=HANDLER_ADAPTER_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_dispatch_route_id=route.dispatch_route_id,
        source_event_frame_id=route.source_event_frame_id,
        target_engine=route.target_engine,
        target_handler_name=route.target_handler_name,
        adapter_kind=adapter_kind,
        adapter_status=adapter_status,
        adapter_summary=_adapter_summary(adapter_status, route.target_engine),
        input_payload_shape="RuntimeEventDispatchRequestRecord.event_payload",
        output_payload_shape="RuntimeEventDispatchResultRecord.result_payload",
        handler_invoked=False,
        handler_invocation_mode=invocation_mode,
        bounded_demo_only=True,
        adapter_record_only=True,
        created_task_record=False,
        created_sense_record=False,
        created_learning_record=False,
        created_memory_record=False,
        created_state_record=False,
        created_output_record=False,
        created_thought_record=False,
        external_execution_created=False,
        memory_layer_write_performed=False,
        automatic_learning_approval_created=False,
        free_action_selection_created=False,
        recursive_learning_created=False,
        production_behavior_created=False,
        source_trace_refs=route.source_trace_refs,
    )


def build_runtime_event_dispatch_result(
    dispatch_request: RuntimeEventDispatchRequestRecord | dict[str, object],
    dispatch_route: RuntimeEventDispatchRouteRecord | dict[str, object],
    handler_adapter: RuntimeEventHandlerAdapterRecord | dict[str, object],
) -> RuntimeEventDispatchResultRecord:
    request = _dispatch_request(dispatch_request)
    route = _dispatch_route(dispatch_route)
    adapter = _handler_adapter(handler_adapter)
    status = "dispatch_completed_adapter_only"
    reason = "adapter_only_dispatch_completed"
    completed = True
    if route.route_status == "deferred_thought_engine_not_available":
        status = "dispatch_deferred_engine_not_available"
        reason = "thought_engine_handler_not_available"
        completed = False
    elif route.route_status == "blocked_unknown_event_type":
        status = "dispatch_blocked_unknown_event_type"
        reason = "event_type_unknown"
        completed = False
    elif route.route_status in {
        "blocked_forbidden_authority_detected",
        "blocked_handler_not_available",
    }:
        status = (
            "dispatch_blocked_forbidden_authority_detected"
            if route.route_status == "blocked_forbidden_authority_detected"
            else "dispatch_blocked_handler_failure"
        )
        reason = route.route_reason
        completed = False

    return_payload_id = (
        f"runtime_event_dispatch_return_payload:{request.source_event_frame_id}:{_slug(request.event_type)}"
    )
    return RuntimeEventDispatchResultRecord(
        dispatch_result_id=f"runtime_event_dispatch_result:{request.source_event_frame_id}:{_slug(request.event_type)}",
        schema_version=DISPATCH_RESULT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_dispatch_request_id=request.dispatch_request_id,
        source_dispatch_route_id=route.dispatch_route_id,
        source_handler_adapter_id=adapter.handler_adapter_id,
        source_event_frame_id=request.source_event_frame_id,
        target_engine=route.target_engine,
        dispatch_result_status=status,
        dispatch_result_reason=reason,
        dispatch_result_summary=_dispatch_result_summary(status, route.target_engine),
        handler_available=route.handler_available,
        handler_completed=completed,
        result_payload={
            "event_type": request.event_type,
            "event_family": route.event_family,
            "target_engine": route.target_engine,
            "adapter_only": True,
            "handler_invoked": adapter.handler_invoked,
        },
        return_payload_required=True,
        return_payload_id=return_payload_id,
        parent_event_frame_id=str(request.event_payload.get("parent_event_frame_id"))
        if request.event_payload.get("parent_event_frame_id")
        else None,
        parent_resume_allowed=completed,
        external_execution_created=False,
        memory_layer_write_performed=False,
        automatic_learning_approval_created=False,
        free_action_selection_created=False,
        recursive_learning_created=False,
        production_behavior_created=False,
        source_trace_refs=request.source_trace_refs,
    )


def build_runtime_event_dispatch_return_payload(
    dispatch_result: RuntimeEventDispatchResultRecord | dict[str, object],
    *,
    parent_event_frame_id: str | None = None,
) -> RuntimeEventDispatchReturnPayloadRecord:
    result = _dispatch_result(dispatch_result)
    status = {
        "dispatch_completed_adapter_only": "returned_success",
        "dispatch_completed_bounded_demo": "returned_success",
        "dispatch_deferred_engine_not_available": "returned_deferred",
        "dispatch_blocked_unknown_event_type": "returned_blocked",
        "dispatch_blocked_forbidden_authority_detected": "returned_blocked",
        "dispatch_blocked_handler_failure": "returned_fault",
    }[result.dispatch_result_status]
    parent_id = parent_event_frame_id or result.parent_event_frame_id
    event_type = str(result.result_payload.get("event_type", "unknown"))
    return RuntimeEventDispatchReturnPayloadRecord(
        dispatch_return_payload_id=result.return_payload_id
        or f"runtime_event_dispatch_return_payload:{result.source_event_frame_id}:{_slug(event_type)}",
        schema_version=DISPATCH_RETURN_PAYLOAD_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_dispatch_result_id=result.dispatch_result_id,
        source_event_frame_id=result.source_event_frame_id,
        parent_event_frame_id=parent_id,
        target_engine=result.target_engine,
        event_type=event_type,
        return_status=status,
        return_reason=result.dispatch_result_reason,
        return_summary=_return_summary(status, result.target_engine),
        return_payload={
            "dispatch_result_id": result.dispatch_result_id,
            "dispatch_result_status": result.dispatch_result_status,
            "target_engine": result.target_engine,
            "completed": status == "returned_success",
            "blocked": status == "returned_blocked",
            "deferred": status == "returned_deferred",
            "fault": status == "returned_fault",
        },
        safe_for_event_frame_return=True,
        safe_for_parent_resume=True,
        creates_new_event=False,
        requires_child_event=False,
        requires_parent_resume=parent_id is not None,
        external_execution_created=False,
        memory_layer_write_performed=False,
        automatic_learning_approval_created=False,
        free_action_selection_created=False,
        recursive_learning_created=False,
        production_behavior_created=False,
        source_trace_refs=result.source_trace_refs,
    )


def build_runtime_event_dispatch_audit(
    dispatch_request: RuntimeEventDispatchRequestRecord | dict[str, object],
    dispatch_route: RuntimeEventDispatchRouteRecord | dict[str, object],
    handler_adapter: RuntimeEventHandlerAdapterRecord | dict[str, object],
    dispatch_result: RuntimeEventDispatchResultRecord | dict[str, object],
    return_payload: RuntimeEventDispatchReturnPayloadRecord | dict[str, object],
) -> RuntimeEventDispatchAudit:
    request = _dispatch_request(dispatch_request)
    route = _dispatch_route(dispatch_route)
    adapter = _handler_adapter(handler_adapter)
    result = _dispatch_result(dispatch_result)
    payload = _return_payload(return_payload)
    event_frame_valid = request.dispatch_request_status != "blocked_invalid_event_frame"
    event_type_classified = route.event_family != "unknown_event"
    route_valid = route.route_status not in {
        "blocked_unknown_event_type",
        "blocked_handler_not_available",
        "blocked_forbidden_authority_detected",
    }
    adapter_valid = adapter.adapter_status not in {
        "blocked_unknown_event_type",
        "blocked_forbidden_authority_detected",
    }
    result_valid = not result.dispatch_result_status.startswith("dispatch_blocked")
    return_valid = payload.return_status in {"returned_success", "returned_deferred"}
    no_thought_faked = not (
        route.target_engine == "thought_engine"
        and (adapter.handler_invoked or adapter.created_thought_record)
    )
    blocked_reasons: list[str] = []
    if request.external_execution_requested or not (
        not adapter.external_execution_created
        and not result.external_execution_created
        and not payload.external_execution_created
    ):
        blocked_reasons.append("external_execution_detected")
    if request.memory_layer_write_requested or not (
        not adapter.memory_layer_write_performed
        and not result.memory_layer_write_performed
        and not payload.memory_layer_write_performed
    ):
        blocked_reasons.append("memory_write_detected")
    if request.automatic_learning_approval_requested or not (
        not adapter.automatic_learning_approval_created
        and not result.automatic_learning_approval_created
        and not payload.automatic_learning_approval_created
    ):
        blocked_reasons.append("automatic_learning_approval_detected")
    if request.free_action_selection_requested or not (
        not adapter.free_action_selection_created
        and not result.free_action_selection_created
        and not payload.free_action_selection_created
    ):
        blocked_reasons.append("free_action_selection_detected")
    if request.recursive_learning_requested or not (
        not adapter.recursive_learning_created
        and not result.recursive_learning_created
        and not payload.recursive_learning_created
    ):
        blocked_reasons.append("recursive_learning_detected")
    if request.production_behavior_requested or not (
        not adapter.production_behavior_created
        and not result.production_behavior_created
        and not payload.production_behavior_created
    ):
        blocked_reasons.append("production_behavior_detected")
    if not no_thought_faked:
        blocked_reasons.append("thought_engine_fake_detected")

    audit_status = _audit_status(
        blocked_reasons=blocked_reasons,
        route=route,
        adapter_valid=adapter_valid,
    )
    return RuntimeEventDispatchAudit(
        dispatch_audit_id=f"runtime_event_dispatch_audit:{request.source_event_frame_id}:{_slug(request.event_type)}",
        schema_version=DISPATCH_AUDIT_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_dispatch_request_id=request.dispatch_request_id,
        source_dispatch_route_id=route.dispatch_route_id,
        source_handler_adapter_id=adapter.handler_adapter_id,
        source_dispatch_result_id=result.dispatch_result_id,
        source_dispatch_return_payload_id=payload.dispatch_return_payload_id,
        event_frame_valid=event_frame_valid,
        event_type_classified=event_type_classified,
        route_valid=route_valid,
        adapter_valid=adapter_valid,
        dispatch_result_valid=result_valid,
        return_payload_valid=return_valid,
        target_engine=route.target_engine,
        handler_available=route.handler_available,
        handler_invoked=adapter.handler_invoked,
        adapter_only_confirmed=adapter.adapter_record_only and not adapter.handler_invoked,
        bounded_demo_only_confirmed=adapter.bounded_demo_only,
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
        no_thought_engine_faked=no_thought_faked,
        audit_status=audit_status,
        safe_claim=SAFE_CLAIM,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_reasons=tuple(blocked_reasons),
        source_trace_refs=request.source_trace_refs,
    )


def dispatch_event_frame_adapter_only(
    event_frame: RuntimeEventFrameRecord | dict[str, object],
    *,
    event_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    request = build_runtime_event_dispatch_request(
        event_frame,
        event_payload=event_payload,
    )
    route = build_runtime_event_dispatch_route(request)
    adapter = build_runtime_event_handler_adapter(route)
    result = build_runtime_event_dispatch_result(request, route, adapter)
    frame = _event_frame(event_frame) if request.dispatch_request_status != "blocked_invalid_event_frame" else None
    parent_id = frame.parent_event_frame_id if frame else None
    return_payload = build_runtime_event_dispatch_return_payload(
        result,
        parent_event_frame_id=parent_id,
    )
    audit = build_runtime_event_dispatch_audit(
        request,
        route,
        adapter,
        result,
        return_payload,
    )
    return {
        "runtime_event_dispatch_request": request.to_dict(),
        "runtime_event_dispatch_route": route.to_dict(),
        "runtime_event_handler_adapter": adapter.to_dict(),
        "runtime_event_dispatch_result": result.to_dict(),
        "runtime_event_dispatch_return_payload": return_payload.to_dict(),
        "runtime_event_dispatch_audit": audit.to_dict(),
        "rendered_dispatch_summary": render_dispatch_summary_text(
            request,
            route,
            result,
            return_payload,
            audit,
        ),
    }


def build_demo_task_event_dispatch() -> dict[str, object]:
    return dispatch_event_frame_adapter_only(_demo_event_frame("candidate_ordering"))


def build_demo_sense_event_dispatch() -> dict[str, object]:
    return dispatch_event_frame_adapter_only(_demo_event_frame("sense_observation"))


def build_demo_learning_event_dispatch() -> dict[str, object]:
    return dispatch_event_frame_adapter_only(_demo_event_frame("learning_feedback_intake"))


def build_demo_memory_event_dispatch() -> dict[str, object]:
    return dispatch_event_frame_adapter_only(_demo_event_frame("memory_readback"))


def build_demo_state_event_dispatch() -> dict[str, object]:
    return dispatch_event_frame_adapter_only(_demo_event_frame("state_snapshot_request"))


def build_demo_output_event_dispatch() -> dict[str, object]:
    return dispatch_event_frame_adapter_only(_demo_event_frame("output_candidate"))


def build_demo_thought_event_deferred_dispatch() -> dict[str, object]:
    return dispatch_event_frame_adapter_only(_demo_event_frame("thought_preview"))


def build_demo_unknown_event_blocked_dispatch() -> dict[str, object]:
    return dispatch_event_frame_adapter_only(_demo_event_frame("summon_dragon"))


def build_demo_forbidden_authority_blocked_dispatch() -> dict[str, object]:
    return dispatch_event_frame_adapter_only(
        _demo_event_frame("candidate_ordering"),
        event_payload={"external_execution_requested": True},
    )


def render_dispatch_summary_text(
    request: RuntimeEventDispatchRequestRecord | dict[str, object],
    route: RuntimeEventDispatchRouteRecord | dict[str, object],
    result: RuntimeEventDispatchResultRecord | dict[str, object],
    return_payload: RuntimeEventDispatchReturnPayloadRecord | dict[str, object],
    audit: RuntimeEventDispatchAudit | dict[str, object],
) -> str:
    request_item = _dispatch_request(request)
    route_item = _dispatch_route(route)
    result_item = _dispatch_result(result)
    return_item = _return_payload(return_payload)
    audit_item = _dispatch_audit(audit)
    return (
        f"{request_item.event_type} -> {route_item.target_engine} "
        f"({route_item.route_status}) -> {result_item.dispatch_result_status} "
        f"-> {return_item.return_status}; audit={audit_item.audit_status}"
    )


def _demo_event_frame(event_type: str) -> RuntimeEventFrameRecord:
    event_slug = _slug(event_type)
    return RuntimeEventFrameRecord(
        event_frame_id=f"runtime_event_frame:package96_demo:{event_slug}",
        schema_version=EVENT_FRAME_SCHEMA_VERSION,
        created_at=_now(),
        source_engine=SOURCE_ENGINE,
        source_power_window_id="runtime_power_window:package96_demo",
        event_type=event_type,
        event_label=f"package96_demo_{event_slug}",
        event_depth=2,
        parent_event_frame_id="runtime_event_frame:package96_demo:parent",
        child_event_frame_ids=tuple(),
        opened_at_tick_index=2,
        closed_at_tick_index=3,
        event_scope="bounded_runtime_window",
        event_budget_ticks=16,
        event_ticks_used=1,
        event_status="event_closed_returned",
        event_summary=f"Package 96 demo EventFrame for {event_type}.",
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
        source_trace_refs=("package_96_event_dispatch_demo",),
    )


def _dispatch_request_summary(status: str, event_type: str) -> str:
    if status == "dispatch_request_created":
        return f"Dispatch request created for bounded event type {event_type}."
    if status == "blocked_invalid_event_frame":
        return "Dispatch request blocked because EventFrame is invalid."
    if status == "blocked_unknown_event_type":
        return f"Dispatch request blocked because event type {event_type} is unknown."
    if status == "blocked_unbounded_budget":
        return "Dispatch request blocked because event budget is unbounded."
    return "Dispatch request blocked because forbidden authority was requested."


def _route_summary(status: str, event_type: str, target_engine: str) -> str:
    if status.startswith("routed_to_"):
        return f"Event type {event_type} routed to {target_engine} adapter lane."
    if status == "deferred_thought_engine_not_available":
        return "Thought event deferred because Thought Engine is not available."
    if status == "blocked_forbidden_authority_detected":
        return "Route blocked because forbidden authority was detected."
    return "Route blocked because event type or handler is unavailable."


def _adapter_summary(status: str, target_engine: str) -> str:
    if status == "adapter_record_created":
        return f"Adapter-only record created for {target_engine}."
    if status == "deferred_engine_not_available":
        return "Adapter deferred because the target engine is not available."
    if status == "blocked_forbidden_authority_detected":
        return "Adapter blocked because forbidden authority was detected."
    return "Adapter blocked because no supported event type was available."


def _dispatch_result_summary(status: str, target_engine: str) -> str:
    if status == "dispatch_completed_adapter_only":
        return f"Adapter-only dispatch completed for {target_engine}."
    if status == "dispatch_deferred_engine_not_available":
        return "Dispatch deferred because the target engine is not available."
    if status == "dispatch_blocked_unknown_event_type":
        return "Dispatch blocked because event type is unknown."
    if status == "dispatch_blocked_forbidden_authority_detected":
        return "Dispatch blocked because forbidden authority was detected."
    return "Dispatch blocked because handler failed or was unavailable."


def _return_summary(status: str, target_engine: str) -> str:
    if status == "returned_success":
        return f"Dispatch returned success from {target_engine} adapter lane."
    if status == "returned_deferred":
        return f"Dispatch returned deferred from {target_engine} adapter lane."
    if status == "returned_blocked":
        return f"Dispatch returned blocked from {target_engine} adapter lane."
    if status == "returned_fault":
        return f"Dispatch returned fault from {target_engine} adapter lane."
    return "Dispatch return payload blocked by forbidden authority."


def _adapter_kind_for_route(route: RuntimeEventDispatchRouteRecord) -> str:
    if route.route_status == "blocked_unknown_event_type":
        return "blocked_unknown_adapter"
    if route.target_engine == "thought_engine":
        return "thought_engine_deferred_adapter"
    for _family, (_target, _status, adapter_kind) in TARGET_BY_FAMILY.items():
        if route.target_engine == _target:
            return adapter_kind
    return "blocked_unknown_adapter"


def _audit_status(
    *,
    blocked_reasons: list[str],
    route: RuntimeEventDispatchRouteRecord,
    adapter_valid: bool,
) -> str:
    priority = (
        ("external_execution_detected", "blocked_external_execution_detected"),
        ("memory_write_detected", "blocked_memory_write_detected"),
        (
            "automatic_learning_approval_detected",
            "blocked_automatic_learning_approval_detected",
        ),
        ("free_action_selection_detected", "blocked_free_action_selection_detected"),
        ("recursive_learning_detected", "blocked_recursive_learning_detected"),
        ("production_behavior_detected", "blocked_production_behavior_detected"),
        ("thought_engine_fake_detected", "blocked_thought_engine_fake_detected"),
    )
    for reason, status in priority:
        if reason in blocked_reasons:
            return status
    if route.route_status == "blocked_unknown_event_type":
        return "blocked_unknown_event_type"
    if not adapter_valid:
        return "blocked_invalid_adapter"
    if route.route_status == "deferred_thought_engine_not_available":
        return "passed_thought_engine_deferred"
    if route.route_status == "blocked_handler_not_available":
        return "blocked_invalid_route"
    return "passed_event_dispatch_adapter_only"


def _event_frame(
    value: RuntimeEventFrameRecord | dict[str, object],
) -> RuntimeEventFrameRecord:
    if isinstance(value, RuntimeEventFrameRecord):
        return value
    return RuntimeEventFrameRecord.from_dict(value)


def _dispatch_request(
    value: RuntimeEventDispatchRequestRecord | dict[str, object],
) -> RuntimeEventDispatchRequestRecord:
    if isinstance(value, RuntimeEventDispatchRequestRecord):
        return value
    return RuntimeEventDispatchRequestRecord.from_dict(value)


def _dispatch_route(
    value: RuntimeEventDispatchRouteRecord | dict[str, object],
) -> RuntimeEventDispatchRouteRecord:
    if isinstance(value, RuntimeEventDispatchRouteRecord):
        return value
    return RuntimeEventDispatchRouteRecord.from_dict(value)


def _handler_adapter(
    value: RuntimeEventHandlerAdapterRecord | dict[str, object],
) -> RuntimeEventHandlerAdapterRecord:
    if isinstance(value, RuntimeEventHandlerAdapterRecord):
        return value
    return RuntimeEventHandlerAdapterRecord.from_dict(value)


def _dispatch_result(
    value: RuntimeEventDispatchResultRecord | dict[str, object],
) -> RuntimeEventDispatchResultRecord:
    if isinstance(value, RuntimeEventDispatchResultRecord):
        return value
    return RuntimeEventDispatchResultRecord.from_dict(value)


def _return_payload(
    value: RuntimeEventDispatchReturnPayloadRecord | dict[str, object],
) -> RuntimeEventDispatchReturnPayloadRecord:
    if isinstance(value, RuntimeEventDispatchReturnPayloadRecord):
        return value
    return RuntimeEventDispatchReturnPayloadRecord.from_dict(value)


def _dispatch_audit(
    value: RuntimeEventDispatchAudit | dict[str, object],
) -> RuntimeEventDispatchAudit:
    if isinstance(value, RuntimeEventDispatchAudit):
        return value
    return RuntimeEventDispatchAudit.from_dict(value)
