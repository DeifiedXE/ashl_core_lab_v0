"""First-stage thought read and signal data shapes for ASHL Core v1."""

from dataclasses import dataclass, fields
from typing import Any


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
class ThoughtReadTrace:
    """Trace for memory application data read by thought."""

    thought_read_trace_id: str
    source_memory_application_data_refs: tuple[str, ...]
    read_reason: str
    read_result_summary: str
    uncertainty: float

    def __post_init__(self) -> None:
        if not self.thought_read_trace_id:
            raise ValueError("thought_read_trace_id is required")
        if not self.read_reason:
            raise ValueError("read_reason is required")
        object.__setattr__(
            self,
            "source_memory_application_data_refs",
            _tuple_of_str(
                "source_memory_application_data_refs",
                self.source_memory_application_data_refs,
            ),
        )
        object.__setattr__(self, "uncertainty", _range_0_1("uncertainty", self.uncertainty))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ThoughtReadTrace":
        return cls(**dict(data))


@dataclass(frozen=True)
class InfluenceTrace:
    """Trace for visible influence on a later thought or body signal."""

    influence_trace_id: str
    source_thought_read_trace_id: str
    affected_signal_ref: str
    influence_kind: str
    before_summary: str
    after_summary: str
    influence_visible: bool

    def __post_init__(self) -> None:
        for field_name in (
            "influence_trace_id",
            "source_thought_read_trace_id",
            "affected_signal_ref",
            "influence_kind",
        ):
            if not getattr(self, field_name):
                raise ValueError(f"{field_name} is required")
        object.__setattr__(self, "influence_visible", bool(self.influence_visible))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "InfluenceTrace":
        return cls(**dict(data))


@dataclass(frozen=True)
class ThoughtSignal:
    """Signal produced by the thought module for the body module."""

    thought_signal_id: str
    source_memory_application_data_refs: tuple[str, ...]
    source_endocrine_signal_refs: tuple[str, ...]
    source_thought_read_trace_refs: tuple[str, ...]
    body_intent_hint: str | None
    reason_codes: tuple[str, ...]
    uncertainty: float

    def __post_init__(self) -> None:
        if not self.thought_signal_id:
            raise ValueError("thought_signal_id is required")
        object.__setattr__(
            self,
            "source_memory_application_data_refs",
            _tuple_of_str(
                "source_memory_application_data_refs",
                self.source_memory_application_data_refs,
            ),
        )
        object.__setattr__(
            self,
            "source_endocrine_signal_refs",
            _tuple_of_str("source_endocrine_signal_refs", self.source_endocrine_signal_refs),
        )
        object.__setattr__(
            self,
            "source_thought_read_trace_refs",
            _tuple_of_str("source_thought_read_trace_refs", self.source_thought_read_trace_refs),
        )
        object.__setattr__(
            self,
            "reason_codes",
            _tuple_of_str("reason_codes", self.reason_codes),
        )
        object.__setattr__(self, "uncertainty", _range_0_1("uncertainty", self.uncertainty))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ThoughtSignal":
        return cls(**dict(data))
