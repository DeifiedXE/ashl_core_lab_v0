"""First-stage endocrine data shapes for ASHL Core v1."""

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
class EndocrineSignal:
    """Mimetic endocrine state-modulation signal."""

    endocrine_signal_id: str
    dopamine_like: float = 0.0
    norepinephrine_like: float = 0.0
    oxytocin_like: float = 0.0
    cortisol_like: float = 0.0
    modulation_notes: tuple[str, ...] = ()
    source_trace_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.endocrine_signal_id:
            raise ValueError("endocrine_signal_id is required")
        for field_name in (
            "dopamine_like",
            "norepinephrine_like",
            "oxytocin_like",
            "cortisol_like",
        ):
            object.__setattr__(self, field_name, _range_0_1(field_name, getattr(self, field_name)))
        object.__setattr__(
            self,
            "modulation_notes",
            _tuple_of_str("modulation_notes", self.modulation_notes),
        )
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "EndocrineSignal":
        return cls(**dict(data))
