"""Local JSONL store for first-stage memory learning traces."""

from __future__ import annotations

import json
import os
from pathlib import Path

from ashl_core_v1.memory.types import (
    MemoryApplicationData,
    MemoryLearningTrace,
    MemoryRoutingTrace,
)
from ashl_core_v1.runtime.manual_samples import build_blocked_manual_circulation_sample
from ashl_core_v1.thought.types import InfluenceTrace, ThoughtReadTrace


MEMORY_TRACE_ENV = "ASHL_CORE_V1_MEMORY_TRACE_DIR"
DEFAULT_MEMORY_TRACE_DIR = Path(__file__).resolve().parents[1] / "data" / "memory_traces"

MEMORY_LEARNING_TRACES_FILE = "memory_learning_traces.jsonl"
MEMORY_ROUTING_TRACES_FILE = "memory_routing_traces.jsonl"
MEMORY_APPLICATION_DATA_FILE = "memory_application_data.jsonl"
THOUGHT_READ_TRACES_FILE = "thought_read_traces.jsonl"
INFLUENCE_TRACES_FILE = "influence_traces.jsonl"


def resolve_memory_trace_dir(data_dir: str | Path | None = None) -> Path:
    if data_dir is not None:
        return Path(data_dir)
    env_value = os.environ.get(MEMORY_TRACE_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_MEMORY_TRACE_DIR


def ensure_memory_trace_store(data_dir: str | Path | None = None) -> Path:
    trace_dir = resolve_memory_trace_dir(data_dir)
    trace_dir.mkdir(parents=True, exist_ok=True)
    for file_name in (
        MEMORY_LEARNING_TRACES_FILE,
        MEMORY_ROUTING_TRACES_FILE,
        MEMORY_APPLICATION_DATA_FILE,
        THOUGHT_READ_TRACES_FILE,
        INFLUENCE_TRACES_FILE,
    ):
        (trace_dir / file_name).touch(exist_ok=True)
    return trace_dir


def seed_blocked_sample_trace(data_dir: str | Path | None = None) -> dict[str, object]:
    sample = build_blocked_manual_circulation_sample()
    records = {
        "memory_learning_trace": MemoryLearningTrace.from_dict(sample["memory_learning_trace"]),
        "memory_routing_trace": MemoryRoutingTrace.from_dict(sample["memory_routing_trace"]),
        "memory_application_data": MemoryApplicationData.from_dict(sample["memory_application_data"]),
        "thought_read_trace": ThoughtReadTrace.from_dict(sample["thought_read_trace"]),
        "influence_trace": InfluenceTrace.from_dict(sample["influence_trace"]),
    }

    _upsert_by_id(
        _path(data_dir, MEMORY_LEARNING_TRACES_FILE),
        records["memory_learning_trace"].to_dict(),
        "memory_learning_trace_id",
    )
    _upsert_by_id(
        _path(data_dir, MEMORY_ROUTING_TRACES_FILE),
        records["memory_routing_trace"].to_dict(),
        "memory_routing_trace_id",
    )
    _upsert_by_id(
        _path(data_dir, MEMORY_APPLICATION_DATA_FILE),
        records["memory_application_data"].to_dict(),
        "memory_application_data_id",
    )
    _upsert_by_id(
        _path(data_dir, THOUGHT_READ_TRACES_FILE),
        records["thought_read_trace"].to_dict(),
        "thought_read_trace_id",
    )
    _upsert_by_id(
        _path(data_dir, INFLUENCE_TRACES_FILE),
        records["influence_trace"].to_dict(),
        "influence_trace_id",
    )
    return {key: value.to_dict() for key, value in records.items()}


def list_memory_learning_traces(data_dir: str | Path | None = None) -> list[MemoryLearningTrace]:
    return [
        MemoryLearningTrace.from_dict(record)
        for record in _read_jsonl(_path(data_dir, MEMORY_LEARNING_TRACES_FILE))
    ]


def list_memory_routing_traces(data_dir: str | Path | None = None) -> list[MemoryRoutingTrace]:
    return [
        MemoryRoutingTrace.from_dict(record)
        for record in _read_jsonl(_path(data_dir, MEMORY_ROUTING_TRACES_FILE))
    ]


def list_memory_application_data(data_dir: str | Path | None = None) -> list[MemoryApplicationData]:
    return [
        MemoryApplicationData.from_dict(record)
        for record in _read_jsonl(_path(data_dir, MEMORY_APPLICATION_DATA_FILE))
    ]


def list_thought_read_traces(data_dir: str | Path | None = None) -> list[ThoughtReadTrace]:
    return [
        ThoughtReadTrace.from_dict(record)
        for record in _read_jsonl(_path(data_dir, THOUGHT_READ_TRACES_FILE))
    ]


def list_influence_traces(data_dir: str | Path | None = None) -> list[InfluenceTrace]:
    return [
        InfluenceTrace.from_dict(record)
        for record in _read_jsonl(_path(data_dir, INFLUENCE_TRACES_FILE))
    ]


def find_memory_learning_trace(
    trace_id: str,
    data_dir: str | Path | None = None,
) -> MemoryLearningTrace | None:
    return next(
        (
            trace
            for trace in list_memory_learning_traces(data_dir)
            if trace.memory_learning_trace_id == trace_id
        ),
        None,
    )


def find_memory_learning_trace_by_reviewed_digest(
    reviewed_digest_id: str,
    data_dir: str | Path | None = None,
) -> MemoryLearningTrace | None:
    return next(
        (
            trace
            for trace in list_memory_learning_traces(data_dir)
            if trace.source_reviewed_digest_id == reviewed_digest_id
        ),
        None,
    )


def find_thought_reads_by_memory_application_data(
    memory_application_data_id: str,
    data_dir: str | Path | None = None,
) -> list[ThoughtReadTrace]:
    return [
        trace
        for trace in list_thought_read_traces(data_dir)
        if memory_application_data_id in trace.source_memory_application_data_refs
    ]


def find_influence_by_thought_read_trace(
    thought_read_trace_id: str,
    data_dir: str | Path | None = None,
) -> list[InfluenceTrace]:
    return [
        trace
        for trace in list_influence_traces(data_dir)
        if trace.source_thought_read_trace_id == thought_read_trace_id
    ]


def _path(data_dir: str | Path | None, file_name: str) -> Path:
    return ensure_memory_trace_store(data_dir) / file_name


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            file.write("\n")


def _upsert_by_id(path: Path, record: dict[str, object], id_field: str) -> None:
    records = _read_jsonl(path)
    record_id = record[id_field]
    remaining = [item for item in records if item.get(id_field) != record_id]
    remaining.append(record)
    _write_jsonl(path, remaining)
