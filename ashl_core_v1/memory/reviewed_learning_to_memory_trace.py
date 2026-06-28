"""Build memory trace records from reviewed cradle learning records."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.memory.types import (
    MemoryApplicationData,
    MemoryLearningTrace,
    MemoryRoutingTrace,
)


REVIEWED_LEARNING_TO_MEMORY_TRACE_ENV = (
    "ASHL_CORE_V1_REVIEWED_LEARNING_TO_MEMORY_TRACE_DIR"
)
DEFAULT_REVIEWED_LEARNING_TO_MEMORY_TRACE_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "reviewed_learning_to_memory_trace"
)

MEMORY_LEARNING_TRACES_FILE = "memory_learning_traces.jsonl"
MEMORY_ROUTING_TRACES_FILE = "memory_routing_traces.jsonl"
MEMORY_APPLICATION_DATA_FILE = "memory_application_data.jsonl"


def build_memory_trace_from_reviewed_learning(
    reviewed_id: str,
    *,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    reviewed_record = _find_reviewed_record(reviewed_id, base_dir)
    reviewed_digest = dict(reviewed_record["reviewed_learning_digest"])
    status = reviewed_digest["review_status"]
    if status != "approved" or reviewed_digest.get("memory_entry_allowed") is not True:
        return {
            "memory_trace_created": False,
            "reviewed_id": reviewed_id,
            "routing_status": "held_for_review",
            "memory_application_data_created": False,
            "reason": f"review status {status} is not approved for memory entry",
            "core_memory_write": False,
            "long_term_memory_write": False,
            "archive_memory_write": False,
            "anchor_layer_write": False,
            "direct_memory_promotion": False,
        }
    memory_trace = MemoryLearningTrace(
        memory_learning_trace_id=_memory_learning_trace_id(reviewed_id),
        source_reviewed_digest_id=reviewed_id,
        source_learning_digest_id=reviewed_digest["source_learning_digest_id"],
        source_review_record_id=reviewed_digest["source_review_record_id"],
        source_perception_refs=tuple(reviewed_record.get("source_tick_refs") or ()),
        source_endocrine_refs=(),
        state_snapshot_ref=None,
        session_summary_ref=reviewed_record.get("source_run_id"),
        last_trace_summary_ref=reviewed_record.get("source_candidate_id"),
        routing_status="routed",
        memory_layer_target="working",
        trace_notes=(
            "routed_for_working_memory_readback",
            "no_core_long_term_archive_anchor_write",
        ),
    )
    routing_trace = MemoryRoutingTrace(
        memory_routing_trace_id=_memory_routing_trace_id(reviewed_id),
        source_memory_learning_trace_id=memory_trace.memory_learning_trace_id,
        route_decision="routed_for_working_memory_readback",
        target_layer="working",
        route_reason_codes=(
            "approved_reviewed_learning",
            str(reviewed_digest["reviewed_payload"].get("candidate_kind")),
        ),
        confidence=0.8,
    )
    application_data = MemoryApplicationData(
        memory_application_data_id=_memory_application_data_id(reviewed_id),
        source_memory_learning_trace_refs=(memory_trace.memory_learning_trace_id,),
        source_memory_routing_trace_refs=(routing_trace.memory_routing_trace_id,),
        memory_items=(
            {
                "source_reviewed_digest_id": reviewed_id,
                "source_candidate_id": reviewed_record["source_candidate_id"],
                "source_run_id": reviewed_record["source_run_id"],
                "source_tick_refs": list(reviewed_record.get("source_tick_refs") or []),
                "source_working_memory_update_refs": list(
                    reviewed_digest["reviewed_payload"].get(
                        "source_working_memory_update_refs",
                        [],
                    )
                ),
                "candidate_kind": reviewed_digest["reviewed_payload"].get(
                    "candidate_kind"
                ),
                "candidate_summary": reviewed_digest["reviewed_payload"].get(
                    "candidate_summary"
                ),
                "teacher_note": reviewed_digest["reviewed_payload"].get("teacher_note"),
            },
        ),
        read_scope="working_memory_readback_preview",
        routing_notes=("target_layer:working", "preview_readback_only"),
    )
    return {
        "memory_trace_created": True,
        "reviewed_id": reviewed_id,
        "memory_learning_trace": memory_trace.to_dict(),
        "memory_routing_trace": routing_trace.to_dict(),
        "memory_application_data": application_data.to_dict(),
        "routing_status": "routed_for_working_memory_readback",
        "target_layer": "working",
        "core_memory_write": False,
        "long_term_memory_write": False,
        "archive_memory_write": False,
        "anchor_layer_write": False,
        "direct_memory_promotion": False,
        "action_selection": False,
        "scheduler_created": False,
    }


def save_memory_trace_bundle(
    bundle: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    if not bundle.get("memory_trace_created"):
        return dict(bundle)
    memory_dir = ensure_reviewed_learning_to_memory_trace_store(base_dir)
    _append_jsonl(memory_dir / MEMORY_LEARNING_TRACES_FILE, bundle["memory_learning_trace"])
    _append_jsonl(memory_dir / MEMORY_ROUTING_TRACES_FILE, bundle["memory_routing_trace"])
    _append_jsonl(
        memory_dir / MEMORY_APPLICATION_DATA_FILE,
        bundle["memory_application_data"],
    )
    return dict(bundle)


def build_and_save_memory_trace_from_reviewed_learning(
    reviewed_id: str,
    *,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    return save_memory_trace_bundle(
        build_memory_trace_from_reviewed_learning(reviewed_id, base_dir=base_dir),
        base_dir,
    )


def build_all_approved_reviewed_learning_memory_traces(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    bundles = []
    for record in _reviewed_records(base_dir):
        reviewed_id = record["cradle_reviewed_learning_record_id"]
        if record.get("memory_entry_allowed") is True:
            bundles.append(
                build_and_save_memory_trace_from_reviewed_learning(
                    reviewed_id,
                    base_dir=base_dir,
                )
            )
    return {
        "memory_trace_build_all_created": True,
        "approved_reviewed_count": len(bundles),
        "memory_trace_bundles": bundles,
    }


def list_memory_learning_trace_records(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    return _read_jsonl(
        resolve_reviewed_learning_to_memory_trace_dir(base_dir)
        / MEMORY_LEARNING_TRACES_FILE
    )


def list_memory_routing_trace_records(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    return _read_jsonl(
        resolve_reviewed_learning_to_memory_trace_dir(base_dir)
        / MEMORY_ROUTING_TRACES_FILE
    )


def list_memory_application_data_records(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    return _read_jsonl(
        resolve_reviewed_learning_to_memory_trace_dir(base_dir)
        / MEMORY_APPLICATION_DATA_FILE
    )


def resolve_reviewed_learning_to_memory_trace_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(REVIEWED_LEARNING_TO_MEMORY_TRACE_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_REVIEWED_LEARNING_TO_MEMORY_TRACE_DIR


def ensure_reviewed_learning_to_memory_trace_store(
    base_dir: str | Path | None = None,
) -> Path:
    memory_dir = resolve_reviewed_learning_to_memory_trace_dir(base_dir)
    memory_dir.mkdir(parents=True, exist_ok=True)
    for file_name in (
        MEMORY_LEARNING_TRACES_FILE,
        MEMORY_ROUTING_TRACES_FILE,
        MEMORY_APPLICATION_DATA_FILE,
    ):
        (memory_dir / file_name).touch(exist_ok=True)
    return memory_dir


def _find_reviewed_record(
    reviewed_id: str,
    base_dir: str | Path | None,
) -> dict[str, Any]:
    for record in _reviewed_records(base_dir):
        if record.get("cradle_reviewed_learning_record_id") == reviewed_id:
            return record
    raise LookupError(f"reviewed learning record not found: {reviewed_id}")


def _reviewed_records(base_dir: str | Path | None) -> list[dict[str, Any]]:
    from ashl_core_v1.lesson.cradle_learning_candidate_review import (
        list_cradle_reviewed_learning_records,
    )

    return list_cradle_reviewed_learning_records(base_dir)


def _memory_learning_trace_id(reviewed_id: str) -> str:
    return f"memory_learning_trace:{reviewed_id}:{_timestamp()}"


def _memory_routing_trace_id(reviewed_id: str) -> str:
    return f"memory_routing_trace:{reviewed_id}:{_timestamp()}"


def _memory_application_data_id(reviewed_id: str) -> str:
    return f"memory_application_data:{reviewed_id}:{_timestamp()}"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
        file.write("\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
