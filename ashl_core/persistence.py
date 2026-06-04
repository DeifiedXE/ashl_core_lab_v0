"""JSONL persistence helpers for ASHL Core."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ensure_parent_dir(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def append_jsonl(path: str | Path, item: dict[str, Any]) -> None:
    target = Path(path)
    ensure_parent_dir(target)
    with target.open("a", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []

    rows: list[dict[str, Any]] = []
    with target.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows
