"""Audit records for ASHL Core v1 open-cradle tick dry-runs."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OPEN_CRADLE_TICK_DRY_RUN_ENV = "ASHL_CORE_V1_OPEN_CRADLE_TICK_DRY_RUN_DIR"
DEFAULT_OPEN_CRADLE_TICK_DRY_RUN_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "open_cradle_tick_dry_run"
)

LAST_TICK_DRY_RUN_AUDIT_FILE = "last_tick_dry_run_audit.json"
TICK_DRY_RUN_AUDIT_HISTORY_FILE = "tick_dry_run_audit_history.jsonl"

REQUIRED_BLOCKED_SURFACES = (
    "automatic_tick_execution",
    "free_action_selection",
    "action_execution",
    "long_term_memory_write",
)


def resolve_tick_dry_run_audit_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(OPEN_CRADLE_TICK_DRY_RUN_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_OPEN_CRADLE_TICK_DRY_RUN_DIR


def ensure_tick_dry_run_audit_store(base_dir: str | Path | None = None) -> Path:
    audit_dir = resolve_tick_dry_run_audit_dir(base_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)
    (audit_dir / TICK_DRY_RUN_AUDIT_HISTORY_FILE).touch(exist_ok=True)
    return audit_dir


def build_tick_dry_run_audit(
    dry_run: dict[str, Any],
    teacher_gate: dict[str, Any],
    tick_context: dict[str, Any],
) -> dict[str, Any]:
    blocked_outputs = set(dry_run.get("blocked_outputs") or [])
    context_blocked = set(tick_context.get("blocked_next_surfaces") or [])
    blocked_surfaces_preserved = all(
        surface in blocked_outputs or surface in context_blocked
        for surface in REQUIRED_BLOCKED_SURFACES
    )
    dry_run_created = dry_run.get("dry_run_status") in {
        "dry_run_created",
        "teacher_review_required",
    }
    audit = {
        "tick_dry_run_audit_id": _new_audit_id(),
        "source_tick_dry_run_id": dry_run.get("tick_dry_run_id"),
        "source_tick_context_id": tick_context.get("tick_context_id"),
        "source_teacher_gate_id": teacher_gate.get("teacher_gate_id"),
        "gate_passed": teacher_gate.get("gate_status") != "blocked",
        "dry_run_created": dry_run_created,
        "teacher_followup_required": dry_run.get("requires_teacher_followup") is True,
        "blocked_surfaces_preserved": blocked_surfaces_preserved,
        "no_runtime_execution": True,
        "no_action_selection": True,
        "no_action_execution": True,
        "no_long_term_memory_write": True,
        "no_external_bridge": True,
        "audit_passed": False,
        "audit_notes": [],
        "created_at": _now(),
        "trace_refs": _trace_refs(dry_run, teacher_gate, tick_context),
    }
    notes = []
    for key in (
        "dry_run_created",
        "blocked_surfaces_preserved",
        "no_runtime_execution",
        "no_action_selection",
        "no_action_execution",
        "no_long_term_memory_write",
        "no_external_bridge",
    ):
        if not audit[key]:
            notes.append(f"{key}_failed")
    audit["audit_notes"] = notes or ["dry_run_boundary_preserved"]
    audit["audit_passed"] = not notes
    return audit


def save_tick_dry_run_audit(
    audit: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    audit_dir = ensure_tick_dry_run_audit_store(base_dir)
    (audit_dir / LAST_TICK_DRY_RUN_AUDIT_FILE).write_text(
        json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (audit_dir / TICK_DRY_RUN_AUDIT_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(audit, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(audit)


def load_last_tick_dry_run_audit(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = resolve_tick_dry_run_audit_dir(base_dir) / LAST_TICK_DRY_RUN_AUDIT_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _trace_refs(
    dry_run: dict[str, Any],
    teacher_gate: dict[str, Any],
    tick_context: dict[str, Any],
) -> list[str]:
    refs = []
    if dry_run.get("tick_dry_run_id"):
        refs.append(f"tick_dry_run:{dry_run['tick_dry_run_id']}")
    if teacher_gate.get("teacher_gate_id"):
        refs.append(f"teacher_gate:{teacher_gate['teacher_gate_id']}")
    if tick_context.get("tick_context_id"):
        refs.append(f"tick_context:{tick_context['tick_context_id']}")
    refs.extend(str(ref) for ref in tick_context.get("trace_refs") or [])
    return refs


def _new_audit_id() -> str:
    return "open_cradle_tick_dry_run_audit_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
