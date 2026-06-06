"""Append-only JSONL persistence for first_output and mentor feedback traces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FIRST_OUTPUT_TRACES_FILENAME = "first_output_traces.jsonl"
MENTOR_FEEDBACK_TRACES_FILENAME = "mentor_feedback_traces.jsonl"

FIRST_OUTPUT_REQUIRED_FIELDS = (
    "trace_id",
    "trace_type",
    "session_id",
    "tick",
    "first_output",
    "llm_used",
    "engineering_stage",
)

MENTOR_FEEDBACK_REQUIRED_FIELDS = (
    "feedback_trace_id",
    "trace_type",
    "source_first_output_trace_id",
    "session_id",
    "tick",
    "mentor_feedback_label",
    "effect",
    "creates_lesson_candidate",
    "writes_lesson_store",
    "writes_memory_layer",
    "engineering_stage",
)


def append_jsonl_record(path: str | Path, record: dict[str, Any]) -> dict[str, Any]:
    """Append one JSON object as a single JSONL line without mutating input."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    record_copy = dict(record)
    with target.open("a", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(record_copy, ensure_ascii=False, separators=(",", ":")) + "\n")
    return {
        "path": str(target),
        "trace_id": record_copy.get("trace_id") or record_copy.get("feedback_trace_id"),
        "trace_type": record_copy.get("trace_type"),
        "append_only": True,
        "overwrite": False,
        "mutates_input": False,
    }


def append_first_output_trace(trace: dict[str, Any], data_dir: str | Path = "data") -> dict[str, Any]:
    """Validate and append a first_output_trace to data/first_output_traces.jsonl."""
    _require_fields(trace, FIRST_OUTPUT_REQUIRED_FIELDS)
    _require_value(trace, "trace_type", "first_output_trace")
    _require_value(trace, "llm_used", False)
    _require_value(trace, "engineering_stage", "test_object")
    return append_jsonl_record(Path(data_dir) / FIRST_OUTPUT_TRACES_FILENAME, trace)


def append_mentor_feedback_trace(trace: dict[str, Any], data_dir: str | Path = "data") -> dict[str, Any]:
    """Validate and append a mentor_feedback_trace to data/mentor_feedback_traces.jsonl."""
    _require_fields(trace, MENTOR_FEEDBACK_REQUIRED_FIELDS)
    _require_value(trace, "trace_type", "mentor_feedback_trace")
    _require_value(trace, "effect", "feedback_only")
    _require_value(trace, "creates_lesson_candidate", False)
    _require_value(trace, "writes_lesson_store", False)
    _require_value(trace, "writes_memory_layer", False)
    _require_value(trace, "engineering_stage", "test_object")
    return append_jsonl_record(Path(data_dir) / MENTOR_FEEDBACK_TRACES_FILENAME, trace)


def _require_fields(record: dict[str, Any], fields: tuple[str, ...]) -> None:
    missing = [field for field in fields if field not in record]
    if missing:
        raise ValueError(f"missing required field: {missing[0]}")


def _require_value(record: dict[str, Any], field: str, expected: Any) -> None:
    actual = record.get(field)
    if actual != expected:
        raise ValueError(f"{field} must be {expected!r}")
