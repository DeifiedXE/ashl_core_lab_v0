"""Four-layer memory data models and IO helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .persistence import append_jsonl, ensure_parent_dir, read_jsonl


CORE_MEMORY_FILE = "core_memory.json"
LONG_TERM_MEMORY_FILE = "long_term_memory.jsonl"
WORKING_MEMORY_FILE = "working_memory.json"
ARCHIVE_MEMORY_FILE = "archive_memory.jsonl"

SUPPORTED_MEMORY_LAYERS = {"core", "long_term", "working", "archive"}
_DISALLOWED_CORE_WRITE_SOURCES = {
    "normal_user_input",
    "memory_candidate",
    "correction_label",
    "rule_candidate",
    "trial_suggestion",
    "trial_feedback",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_memory_layer_paths(data_dir: str | Path) -> dict[str, Path]:
    root = Path(data_dir)
    return {
        "core": root / CORE_MEMORY_FILE,
        "long_term": root / LONG_TERM_MEMORY_FILE,
        "working": root / WORKING_MEMORY_FILE,
        "archive": root / ARCHIVE_MEMORY_FILE,
    }


def build_memory_record(
    layer: str,
    content: str,
    source: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if layer not in SUPPORTED_MEMORY_LAYERS:
        return None
    return {
        "id": f"mem_{uuid4().hex}",
        "type": "memory_record",
        "layer": layer,
        "content": content,
        "source": source,
        "status": "active",
        "metadata": metadata or {},
        "created_at": _now_iso(),
    }


def append_long_term_memory(data_dir: str | Path, record: dict[str, Any]) -> None:
    append_jsonl(get_memory_layer_paths(data_dir)["long_term"], record)


def list_long_term_memory(data_dir: str | Path) -> list[dict[str, Any]]:
    return read_jsonl(get_memory_layer_paths(data_dir)["long_term"])


def write_working_memory_snapshot(data_dir: str | Path, snapshot: dict[str, Any]) -> None:
    path = get_memory_layer_paths(data_dir)["working"]
    ensure_parent_dir(path)
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")


def read_working_memory_snapshot(data_dir: str | Path) -> dict[str, Any]:
    path = get_memory_layer_paths(data_dir)["working"]
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def append_archive_memory(data_dir: str | Path, record: dict[str, Any]) -> None:
    append_jsonl(get_memory_layer_paths(data_dir)["archive"], record)


def list_archive_memory(data_dir: str | Path) -> list[dict[str, Any]]:
    return read_jsonl(get_memory_layer_paths(data_dir)["archive"])


def read_core_memory(data_dir: str | Path) -> dict[str, Any]:
    path = get_memory_layer_paths(data_dir)["core"]
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def is_core_memory_write_allowed(source: str) -> bool:
    if source in _DISALLOWED_CORE_WRITE_SOURCES:
        return False
    return source == "manual_versioned_update"
