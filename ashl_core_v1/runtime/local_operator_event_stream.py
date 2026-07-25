"""Local operator JSON event stream for Package 122B."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.operator_console_types import JSON_EVENT_SCHEMA_VERSION, LocalOperatorJsonEvent


class LocalOperatorEventStream:
    def __init__(self, store: LocalOperatorConsoleStore) -> None:
        self.store = store

    def append_event(
        self,
        *,
        event_kind: str,
        source_record_refs: tuple[str, ...] = tuple(),
        source_trace_refs: tuple[str, ...] = tuple(),
        runtime_session_id: str | None = None,
        perception_session_id: str | None = None,
        observation_window_id: str | None = None,
    ) -> LocalOperatorJsonEvent:
        event = LocalOperatorJsonEvent(
            event_id=stable_id("local_operator_event"),
            schema_version=JSON_EVENT_SCHEMA_VERSION,
            sequence_index=self.store.next_event_sequence_index(),
            created_at=utc_now(),
            event_kind=event_kind,
            source_record_refs=source_record_refs,
            source_trace_refs=source_trace_refs,
            llm_used=False,
            codex_used=False,
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
        )
        self.store.append_json_event(event)
        return event

    def list_events(self) -> tuple[dict[str, object], ...]:
        return self.store.list_payloads("operator_json_events", "sequence_index")
