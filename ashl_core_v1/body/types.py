"""First-stage body action data shapes for ASHL Core v1."""

from dataclasses import dataclass, fields
from typing import Any


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
class BodyActionSignal:
    """Action signal produced by the mimetic body module."""

    body_action_signal_id: str
    source_thought_signal_id: str
    action_signal_type: str
    target_channel: str
    arguments: dict[str, object]
    expected_feedback_kind: str | None
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "body_action_signal_id",
            "source_thought_signal_id",
            "action_signal_type",
            "target_channel",
        ):
            if not getattr(self, field_name):
                raise ValueError(f"{field_name} is required")
        object.__setattr__(self, "arguments", dict(self.arguments))
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "BodyActionSignal":
        return cls(**dict(data))
