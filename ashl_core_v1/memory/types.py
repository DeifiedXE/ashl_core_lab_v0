"""First-stage memory learning trace data shapes for ASHL Core v1."""

from dataclasses import dataclass, fields
from typing import Any, ClassVar


def _plain(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    return value


def _range_0_1(name: str, value: float) -> float:
    numeric = float(value)
    if not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{name} must be between 0.0 and 1.0")
    return numeric


def _tuple_of_str(name: str, value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    refs = tuple(value)
    if not all(isinstance(item, str) for item in refs):
        raise TypeError(f"{name} must contain only strings")
    return refs


@dataclass(frozen=True)
class MemoryLearningTrace:
    """Trace for how reviewed learning enters the memory system."""

    ALLOWED_ROUTING_STATUSES: ClassVar[set[str]] = {
        "routed",
        "held_for_review",
        "rejected",
        "deferred",
        "conflict_detected",
        "stale",
        "superseded",
    }

    memory_learning_trace_id: str
    source_reviewed_digest_id: str
    source_learning_digest_id: str
    source_review_record_id: str
    source_perception_refs: tuple[str, ...]
    source_endocrine_refs: tuple[str, ...]
    state_snapshot_ref: str | None
    session_summary_ref: str | None
    last_trace_summary_ref: str | None
    routing_status: str
    memory_layer_target: str | None
    trace_notes: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "memory_learning_trace_id",
            "source_reviewed_digest_id",
            "source_learning_digest_id",
            "source_review_record_id",
        ):
            if not getattr(self, field_name):
                raise ValueError(f"{field_name} is required")
        if self.routing_status not in self.ALLOWED_ROUTING_STATUSES:
            raise ValueError(f"unknown routing_status: {self.routing_status}")
        object.__setattr__(
            self,
            "source_perception_refs",
            _tuple_of_str("source_perception_refs", self.source_perception_refs),
        )
        object.__setattr__(
            self,
            "source_endocrine_refs",
            _tuple_of_str("source_endocrine_refs", self.source_endocrine_refs),
        )
        object.__setattr__(self, "trace_notes", _tuple_of_str("trace_notes", self.trace_notes))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "MemoryLearningTrace":
        return cls(**dict(data))


@dataclass(frozen=True)
class MemoryRoutingTrace:
    """Trace for memory-layer routing decisions."""

    ALLOWED_TARGET_LAYERS: ClassVar[set[str]] = {
        "working",
        "core",
        "long_term",
        "archive",
        "anchor",
        "none",
    }

    memory_routing_trace_id: str
    source_memory_learning_trace_id: str
    route_decision: str
    target_layer: str | None
    route_reason_codes: tuple[str, ...]
    confidence: float

    def __post_init__(self) -> None:
        if not self.memory_routing_trace_id:
            raise ValueError("memory_routing_trace_id is required")
        if not self.source_memory_learning_trace_id:
            raise ValueError("source_memory_learning_trace_id is required")
        if not self.route_decision:
            raise ValueError("route_decision is required")
        if self.target_layer is not None and self.target_layer not in self.ALLOWED_TARGET_LAYERS:
            raise ValueError(f"unknown target_layer: {self.target_layer}")
        object.__setattr__(
            self,
            "route_reason_codes",
            _tuple_of_str("route_reason_codes", self.route_reason_codes),
        )
        object.__setattr__(self, "confidence", _range_0_1("confidence", self.confidence))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "MemoryRoutingTrace":
        return cls(**dict(data))


@dataclass(frozen=True)
class MemoryApplicationData:
    """Memory data prepared for the thought module."""

    memory_application_data_id: str
    source_memory_learning_trace_refs: tuple[str, ...]
    source_memory_routing_trace_refs: tuple[str, ...]
    memory_items: tuple[dict[str, object], ...]
    read_scope: str
    routing_notes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.memory_application_data_id:
            raise ValueError("memory_application_data_id is required")
        if not self.read_scope:
            raise ValueError("read_scope is required")
        object.__setattr__(
            self,
            "source_memory_learning_trace_refs",
            _tuple_of_str(
                "source_memory_learning_trace_refs",
                self.source_memory_learning_trace_refs,
            ),
        )
        object.__setattr__(
            self,
            "source_memory_routing_trace_refs",
            _tuple_of_str(
                "source_memory_routing_trace_refs",
                self.source_memory_routing_trace_refs,
            ),
        )
        object.__setattr__(
            self,
            "memory_items",
            tuple(dict(item) for item in self.memory_items),
        )
        object.__setattr__(
            self,
            "routing_notes",
            _tuple_of_str("routing_notes", self.routing_notes),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "MemoryApplicationData":
        return cls(**dict(data))


@dataclass(frozen=True)
class StateSnapshotRef:
    """Reference to a state-persistence snapshot."""

    state_snapshot_ref_id: str
    state_snapshot_path: str | None
    state_summary: dict[str, object]

    def __post_init__(self) -> None:
        if not self.state_snapshot_ref_id:
            raise ValueError("state_snapshot_ref_id is required")
        object.__setattr__(self, "state_summary", dict(self.state_summary))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "StateSnapshotRef":
        return cls(**dict(data))


@dataclass(frozen=True)
class SessionSummaryRef:
    """Reference to a session summary."""

    session_summary_ref_id: str
    session_id: str
    turn_count: int
    summary: str

    def __post_init__(self) -> None:
        if not self.session_summary_ref_id:
            raise ValueError("session_summary_ref_id is required")
        if not self.session_id:
            raise ValueError("session_id is required")
        if self.turn_count < 0:
            raise ValueError("turn_count must be non-negative")

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SessionSummaryRef":
        return cls(**dict(data))


@dataclass(frozen=True)
class LastTraceSummaryRef:
    """Reference to the latest trace summary."""

    last_trace_summary_ref_id: str
    trace_id: str
    summary: str

    def __post_init__(self) -> None:
        if not self.last_trace_summary_ref_id:
            raise ValueError("last_trace_summary_ref_id is required")
        if not self.trace_id:
            raise ValueError("trace_id is required")

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "LastTraceSummaryRef":
        return cls(**dict(data))
