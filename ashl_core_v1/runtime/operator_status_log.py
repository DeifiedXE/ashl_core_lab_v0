"""Operator status log helpers for Package 122B."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.operator_console_types import (
    STATUS_LOG_SCHEMA_VERSION,
    OperatorStatusLogEntry,
    OperatorStatusLogLevel,
)


def build_operator_status_log_entry(
    *,
    level: str,
    event_kind: str,
    operator_message: str,
    source_module: str,
    source_record_refs: tuple[str, ...] = tuple(),
    source_trace_refs: tuple[str, ...] = tuple(),
) -> OperatorStatusLogEntry:
    if level not in {item.value for item in OperatorStatusLogLevel}:
        raise ValueError("invalid operator status log level")
    return OperatorStatusLogEntry(
        status_log_id=stable_id("operator_status_log"),
        schema_version=STATUS_LOG_SCHEMA_VERSION,
        created_at=utc_now(),
        level=level,
        event_kind=event_kind,
        operator_message=operator_message,
        source_module=source_module,
        source_record_refs=source_record_refs,
        source_trace_refs=source_trace_refs,
        qingyin_output=False,
    )
