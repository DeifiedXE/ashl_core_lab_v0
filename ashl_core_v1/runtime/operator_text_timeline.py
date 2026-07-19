"""Text input and timeline helpers for Package 122B."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.runtime.operator_console_types import (
    RAW_OUTPUT_SEQUENCE_SCHEMA_VERSION,
    TEXT_INPUT_SCHEMA_VERSION,
    TEXT_TIMELINE_SCHEMA_VERSION,
    ExternalTextInputRecord,
    RawOutputSequence,
    TextTimelineEntry,
    TextTimelineEntryKind,
)
from ashl_core_v1.runtime.raw_output_token_registry import validate_raw_output_tokens


def submit_local_text_input(
    store: LocalOperatorConsoleStore,
    *,
    text: str,
    source_trace_refs: tuple[str, ...] = tuple(),
) -> tuple[ExternalTextInputRecord, TextTimelineEntry]:
    record = ExternalTextInputRecord(
        text_input_id=stable_id("external_text_input"),
        schema_version=TEXT_INPUT_SCHEMA_VERSION,
        created_at=utc_now(),
        input_text=str(text),
        input_source="local_operator_console",
        input_actor="user",
        interpretation_status="received_unprocessed",
        grounding_status="not_grounded",
        forwarded_to_runtime=False,
        forwarded_port=None,
        source_trace_refs=source_trace_refs,
    )
    entry = TextTimelineEntry(
        timeline_entry_id=stable_id("text_timeline_entry"),
        schema_version=TEXT_TIMELINE_SCHEMA_VERSION,
        created_at=utc_now(),
        entry_kind=TextTimelineEntryKind.USER_INPUT.value,
        display_text=str(text),
        source_actor="user",
        source_record_id=record.text_input_id,
        semantic_status="received_unprocessed",
        fixture_only=False,
        qingyin_authored=False,
        source_trace_refs=record.source_trace_refs,
    )
    store.append_external_text_input(record)
    store.append_text_timeline_entry(entry)
    LocalOperatorEventStream(store).append_event(
        event_kind="user_text_received",
        source_record_refs=(record.text_input_id, entry.timeline_entry_id),
        source_trace_refs=record.source_trace_refs,
    )
    return record, entry


def build_fixture_raw_output_sequence(
    *,
    token_codes: tuple[str, ...],
    source_record_refs: tuple[str, ...] = ("fixture:operator_console",),
) -> RawOutputSequence:
    tokens = validate_raw_output_tokens(token_codes)
    return RawOutputSequence(
        raw_output_sequence_id=stable_id("raw_output_sequence"),
        schema_version=RAW_OUTPUT_SEQUENCE_SCHEMA_VERSION,
        created_at=utc_now(),
        token_codes=tokens,
        source_kind="fixture",
        source_record_refs=source_record_refs,
        semantic_label=None,
        qingyin_authored=False,
        fixture_only=True,
        provenance_complete=True,
    )


def append_raw_output_timeline_entry(
    store: LocalOperatorConsoleStore,
    *,
    display_text: str,
    source_record_id: str,
    source_actor: str,
    fixture_only: bool,
    qingyin_authored: bool,
    source_trace_refs: tuple[str, ...] = tuple(),
) -> TextTimelineEntry:
    entry = TextTimelineEntry(
        timeline_entry_id=stable_id("text_timeline_entry"),
        schema_version=TEXT_TIMELINE_SCHEMA_VERSION,
        created_at=utc_now(),
        entry_kind=TextTimelineEntryKind.QINGYIN_RAW_OUTPUT.value,
        display_text=display_text,
        source_actor=source_actor,
        source_record_id=source_record_id,
        semantic_status="ungrounded",
        fixture_only=fixture_only,
        qingyin_authored=qingyin_authored,
        source_trace_refs=source_trace_refs,
    )
    store.append_text_timeline_entry(entry)
    return entry
