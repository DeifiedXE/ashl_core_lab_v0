"""Memory candidate creation for ASHL Core."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .persistence import append_jsonl


MEMORY_CANDIDATES_FILE = "memory_candidates.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_memory_candidate(source_input: str, reason: str = "memory.candidate_requested") -> dict:
    return {
        "id": f"mem_cand_{uuid4().hex}",
        "type": "memory_candidate",
        "content": source_input.strip(),
        "source_input": source_input,
        "reason": reason,
        "status": "candidate",
        "audit_required": True,
        "created_at": _now_iso(),
    }


def create_memory_candidate(source_input: str, data_dir: str | Path = "data") -> dict:
    candidate = build_memory_candidate(source_input)
    append_jsonl(Path(data_dir) / MEMORY_CANDIDATES_FILE, candidate)
    return candidate
