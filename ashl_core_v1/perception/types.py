"""First-stage perception data shapes for ASHL Core v1."""

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
class PerceptionReadableData:
    """Readable output produced by the hard/soft perception module."""

    perception_id: str
    source_kind: str
    source_ref: str | None
    readable_type: str
    readable_payload: dict[str, object]
    uncertainty: float
    source_trace_refs: tuple[str, ...]
    created_at_tick: int | None = None

    def __post_init__(self) -> None:
        if not self.perception_id:
            raise ValueError("perception_id is required")
        if not self.source_kind:
            raise ValueError("source_kind is required")
        if not self.readable_type:
            raise ValueError("readable_type is required")
        object.__setattr__(self, "readable_payload", dict(self.readable_payload))
        object.__setattr__(self, "uncertainty", _range_0_1("uncertainty", self.uncertainty))
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "PerceptionReadableData":
        return cls(**dict(data))
