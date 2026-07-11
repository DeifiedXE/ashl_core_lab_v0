"""Canonical append-only TraceEnvelope contract for ASHL Core v1 sessions."""

from __future__ import annotations

import copy
from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from typing import Any


TRACE_SCHEMA_VERSION = "ashl_trace_envelope_v1"

ALLOWED_SOURCE_LINES = (
    "runtime",
    "task",
    "state",
    "learning",
    "memory",
    "teacher_interface",
    "sense",
    "thought",
    "output",
    "audit",
    "host_body",
)

ALLOWED_TRACE_LAYERS = (
    "raw",
    "derived_evidence",
    "reviewed_interpretation",
    "runtime_control",
    "audit",
)

RAW_TRACE_FORBIDDEN_KEYS = {
    "concept_id",
    "reviewed_concept_id",
    "memory_learning_trace_id",
    "MemoryLearningTrace",
    "interpretation_summary",
    "reviewed_interpretation_summary",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tuple_of_str(value: tuple[str, ...] | list[str] | tuple[object, ...] | list[object]) -> tuple[str, ...]:
    return tuple(str(item) for item in value)


def _plain(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _contains_forbidden_key(value: Any, forbidden_keys: set[str]) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key) in forbidden_keys:
                return True
            if _contains_forbidden_key(item, forbidden_keys):
                return True
    elif isinstance(value, (list, tuple)):
        return any(_contains_forbidden_key(item, forbidden_keys) for item in value)
    return False


@dataclass(frozen=True)
class TraceEnvelope:
    trace_id: str
    trace_schema_version: str
    session_id: str
    event_id: str
    parent_event_id: str | None
    root_event_id: str
    sequence_index: int
    monotonic_tick: int
    nesting_depth: int
    source_line: str
    source_module: str
    record_kind: str
    record_id: str
    trace_layer: str
    payload_schema: str
    payload_snapshot: dict[str, Any]
    source_trace_refs: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    created_at: str
    append_only: bool
    time_aligned: bool

    def __post_init__(self) -> None:
        if self.trace_schema_version != TRACE_SCHEMA_VERSION:
            raise ValueError("trace_schema_version must be ashl_trace_envelope_v1")
        if not self.session_id:
            raise ValueError("session_id is required")
        if not self.event_id:
            raise ValueError("event_id is required")
        if not self.root_event_id:
            raise ValueError("root_event_id is required")
        if self.source_line not in ALLOWED_SOURCE_LINES:
            raise ValueError(f"unknown source_line: {self.source_line}")
        if self.trace_layer not in ALLOWED_TRACE_LAYERS:
            raise ValueError(f"unknown trace_layer: {self.trace_layer}")
        if not self.append_only:
            raise ValueError("TraceEnvelope must be append_only")
        if not self.time_aligned:
            raise ValueError("TraceEnvelope must be time_aligned")
        if self.trace_layer == "raw" and _contains_forbidden_key(self.payload_snapshot, RAW_TRACE_FORBIDDEN_KEYS):
            raise ValueError("raw TraceEnvelope payload contains interpreted or memory identifiers")
        if self.trace_layer in {"derived_evidence", "reviewed_interpretation", "audit"} and not self.source_trace_refs:
            raise ValueError("interpreted or audit TraceEnvelope requires source_trace_refs")
        object.__setattr__(self, "source_trace_refs", _tuple_of_str(self.source_trace_refs))
        object.__setattr__(self, "source_record_refs", _tuple_of_str(self.source_record_refs))
        object.__setattr__(self, "payload_snapshot", copy.deepcopy(dict(self.payload_snapshot)))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TraceEnvelope":
        return cls(**dict(data))


def build_trace_envelope(
    *,
    trace_id: str,
    session_id: str,
    event_id: str,
    root_event_id: str,
    source_line: str,
    source_module: str,
    record_kind: str,
    record_id: str,
    trace_layer: str,
    payload_schema: str,
    payload_snapshot: dict[str, Any],
    parent_event_id: str | None = None,
    sequence_index: int = -1,
    monotonic_tick: int = -1,
    nesting_depth: int = 0,
    source_trace_refs: tuple[str, ...] = tuple(),
    source_record_refs: tuple[str, ...] = tuple(),
    created_at: str | None = None,
) -> TraceEnvelope:
    return TraceEnvelope(
        trace_id=trace_id,
        trace_schema_version=TRACE_SCHEMA_VERSION,
        session_id=session_id,
        event_id=event_id,
        parent_event_id=parent_event_id,
        root_event_id=root_event_id,
        sequence_index=sequence_index,
        monotonic_tick=monotonic_tick,
        nesting_depth=nesting_depth,
        source_line=source_line,
        source_module=source_module,
        record_kind=record_kind,
        record_id=record_id,
        trace_layer=trace_layer,
        payload_schema=payload_schema,
        payload_snapshot=payload_snapshot,
        source_trace_refs=source_trace_refs,
        source_record_refs=source_record_refs,
        created_at=created_at or _now(),
        append_only=True,
        time_aligned=True,
    )


def validate_trace_envelope(envelope: TraceEnvelope | dict[str, object]) -> dict[str, object]:
    try:
        item = envelope if isinstance(envelope, TraceEnvelope) else TraceEnvelope.from_dict(envelope)
    except Exception as error:
        return {"valid": False, "status": "invalid_trace_envelope", "reasons": [str(error)]}
    return {
        "valid": True,
        "status": "trace_envelope_valid",
        "reasons": [],
        "trace_id": item.trace_id,
        "trace_layer": item.trace_layer,
    }


class TraceEnvelopeStore:
    """Append-only in-memory TraceEnvelope store."""

    def __init__(self) -> None:
        self._envelopes: list[TraceEnvelope] = []
        self._by_id: dict[str, TraceEnvelope] = {}

    def append(self, envelope: TraceEnvelope) -> TraceEnvelope:
        if envelope.trace_id in self._by_id:
            raise ValueError(f"duplicate trace_id: {envelope.trace_id}")
        next_sequence = len(self._envelopes)
        existing_ids = set(self._by_id)
        for ref in envelope.source_trace_refs:
            if ref not in existing_ids:
                raise ValueError(f"missing or future source_trace_ref: {ref}")
            if self._by_id[ref].session_id != envelope.session_id:
                raise ValueError(f"cross-session source_trace_ref: {ref}")
        stored = replace(
            envelope,
            sequence_index=next_sequence,
            monotonic_tick=max(next_sequence, self._envelopes[-1].monotonic_tick + 1 if self._envelopes else 0),
            payload_snapshot=copy.deepcopy(envelope.payload_snapshot),
            source_trace_refs=tuple(envelope.source_trace_refs),
            source_record_refs=tuple(envelope.source_record_refs),
        )
        self._envelopes.append(stored)
        self._by_id[stored.trace_id] = stored
        return stored

    def get(self, trace_id: str) -> TraceEnvelope:
        return self._by_id[trace_id]

    def list_by_session(self, session_id: str) -> tuple[TraceEnvelope, ...]:
        return tuple(item for item in self._envelopes if item.session_id == session_id)

    def list_by_event(self, event_id: str) -> tuple[TraceEnvelope, ...]:
        return tuple(item for item in self._envelopes if item.event_id == event_id)

    def list_by_source_line(self, source_line: str) -> tuple[TraceEnvelope, ...]:
        return tuple(item for item in self._envelopes if item.source_line == source_line)

    def list_after_sequence(self, sequence_index: int) -> tuple[TraceEnvelope, ...]:
        return tuple(item for item in self._envelopes if item.sequence_index > sequence_index)

    def latest_sequence(self) -> int:
        return self._envelopes[-1].sequence_index if self._envelopes else -1

    def validate_monotonic_order(self) -> bool:
        sequences = [item.sequence_index for item in self._envelopes]
        ticks = [item.monotonic_tick for item in self._envelopes]
        return sequences == list(range(len(sequences))) and all(
            earlier <= later for earlier, later in zip(ticks, ticks[1:])
        )

    def validate_source_refs(self) -> bool:
        seen: dict[str, TraceEnvelope] = {}
        for item in self._envelopes:
            for ref in item.source_trace_refs:
                if ref not in seen:
                    return False
                if seen[ref].session_id != item.session_id:
                    return False
            seen[item.trace_id] = item
        return True

    def update(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("TraceEnvelopeStore is append-only; update is forbidden")

    def replace(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("TraceEnvelopeStore is append-only; replace is forbidden")

    def delete(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("TraceEnvelopeStore is append-only; delete is forbidden")

    def __len__(self) -> int:
        return len(self._envelopes)


def validate_trace_envelope_store(store: TraceEnvelopeStore) -> dict[str, object]:
    monotonic = store.validate_monotonic_order()
    refs_valid = store.validate_source_refs()
    return {
        "valid": monotonic and refs_valid,
        "status": "trace_envelope_store_valid" if monotonic and refs_valid else "trace_envelope_store_invalid",
        "trace_sequence_monotonic": monotonic,
        "trace_source_refs_valid": refs_valid,
        "reasons": [] if monotonic and refs_valid else ["trace_sequence_or_refs_invalid"],
    }

