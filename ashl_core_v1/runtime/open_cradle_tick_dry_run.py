"""Teacher-gated open-cradle tick dry-run records for ASHL Core v1."""

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

LAST_TICK_DRY_RUN_FILE = "last_tick_dry_run.json"
TICK_DRY_RUN_HISTORY_FILE = "tick_dry_run_history.jsonl"

GATE_STATUSES = ("allowed_for_dry_run", "blocked", "needs_teacher_review")
DRY_RUN_STATUSES = ("dry_run_created", "teacher_review_required", "blocked_by_gate")

REQUIRED_CONTEXT_BLOCKED_SURFACES = (
    "automatic_tick_execution",
    "free_action_selection",
    "action_execution",
    "long_term_memory_write",
)

DRY_RUN_MATRIX: dict[str, dict[str, Any]] = {
    "observe_only": {
        "dry_run_kind": "observe_only_dry_run",
        "proposed_outputs": ("environment_observation_summary", "trace_summary"),
        "blocked_outputs": (
            "action_selection",
            "action_execution",
            "long_term_memory_write",
        ),
        "requires_teacher_followup": False,
    },
    "environment_state_refresh": {
        "dry_run_kind": "environment_refresh_dry_run",
        "proposed_outputs": (
            "environment_refresh_request",
            "missing_environment_state_note",
            "trace_summary",
        ),
        "blocked_outputs": (
            "action_execution",
            "free_action_selection",
            "long_term_memory_write",
        ),
        "requires_teacher_followup": False,
    },
    "manual_daily_case": {
        "dry_run_kind": "manual_daily_case_dry_run",
        "proposed_outputs": ("manual_case_plan", "expected_case_summary", "trace_summary"),
        "blocked_outputs": ("automatic_tick_execution", "free_action_selection"),
        "requires_teacher_followup": False,
    },
    "promotion_review_pending": {
        "dry_run_kind": "promotion_review_dry_run",
        "proposed_outputs": (
            "promotion_queue_summary",
            "suggested_teacher_review_prompt",
            "trace_summary",
        ),
        "blocked_outputs": (
            "long_term_memory_write",
            "automatic_memory_promotion",
            "action_execution",
        ),
        "requires_teacher_followup": True,
    },
    "review_pending": {
        "dry_run_kind": "review_pending_dry_run",
        "proposed_outputs": (
            "pending_review_summary",
            "suggested_teacher_review_prompt",
            "trace_summary",
        ),
        "blocked_outputs": (
            "automatic_review_resolution",
            "action_execution",
            "long_term_memory_write",
        ),
        "requires_teacher_followup": True,
    },
    "teacher_wait": {
        "dry_run_kind": "teacher_wait_dry_run",
        "proposed_outputs": (
            "caregiver_attention_summary",
            "wait_reason_summary",
            "trace_summary",
        ),
        "blocked_outputs": (
            "automatic_tick_execution",
            "free_action_selection",
            "action_execution",
        ),
        "requires_teacher_followup": True,
    },
    "stop": {
        "dry_run_kind": "stop_dry_run",
        "proposed_outputs": ("stop_reason_summary", "trace_summary"),
        "blocked_outputs": (
            "automatic_tick_execution",
            "action_execution",
            "long_term_memory_write",
        ),
        "requires_teacher_followup": False,
    },
}


def resolve_tick_dry_run_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(OPEN_CRADLE_TICK_DRY_RUN_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_OPEN_CRADLE_TICK_DRY_RUN_DIR


def ensure_tick_dry_run_store(base_dir: str | Path | None = None) -> Path:
    dry_run_dir = resolve_tick_dry_run_dir(base_dir)
    dry_run_dir.mkdir(parents=True, exist_ok=True)
    (dry_run_dir / TICK_DRY_RUN_HISTORY_FILE).touch(exist_ok=True)
    return dry_run_dir


def build_teacher_gate_for_tick_context(
    tick_context: dict[str, Any] | None,
    teacher_note: str | None = None,
) -> dict[str, Any]:
    blocked_reason = _gate_block_reason(tick_context)
    if blocked_reason:
        return _teacher_gate(
            tick_context,
            "blocked",
            blocked_reason,
            teacher_note,
            False,
        )
    assert tick_context is not None
    if _needs_teacher_review(tick_context):
        return _teacher_gate(
            tick_context,
            "needs_teacher_review",
            "teacher_review_required",
            teacher_note,
            True,
        )
    return _teacher_gate(
        tick_context,
        "allowed_for_dry_run",
        "dry_run_only_gate_passed",
        teacher_note,
        True,
    )


def build_tick_dry_run_record(
    tick_context: dict[str, Any],
    teacher_gate: dict[str, Any],
) -> dict[str, Any]:
    recommended_mode = tick_context.get("recommended_tick_mode")
    matrix = DRY_RUN_MATRIX.get(recommended_mode) or DRY_RUN_MATRIX["stop"]
    gate_status = teacher_gate.get("gate_status")
    dry_run_status = "dry_run_created"
    if gate_status == "blocked":
        dry_run_status = "blocked_by_gate"
    elif gate_status == "needs_teacher_review":
        dry_run_status = "teacher_review_required"
    blocked_outputs = _preserved_blocked_outputs(matrix, tick_context)
    requires_teacher_followup = bool(matrix["requires_teacher_followup"]) or gate_status == (
        "needs_teacher_review"
    )
    return {
        "tick_dry_run_id": _new_tick_dry_run_id(),
        "source_tick_context_id": tick_context.get("tick_context_id"),
        "source_teacher_gate_id": teacher_gate.get("teacher_gate_id"),
        "source_session_id": tick_context.get("source_session_id"),
        "recommended_tick_mode": recommended_mode,
        "dry_run_status": dry_run_status,
        "dry_run_kind": matrix["dry_run_kind"],
        "dry_run_summary": _dry_run_summary(recommended_mode, dry_run_status),
        "proposed_outputs": list(matrix["proposed_outputs"]) if gate_status != "blocked" else [],
        "blocked_outputs": blocked_outputs,
        "requires_teacher_followup": requires_teacher_followup,
        "created_at": _now(),
        "trace_refs": _trace_refs(tick_context, teacher_gate),
    }


def run_teacher_gated_tick_dry_run(
    base_dir: str | Path | None = None,
    teacher_note: str | None = None,
    preferred_mode: str | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.open_cradle_tick_context import (
        build_open_cradle_tick_context,
        save_open_cradle_tick_context,
    )
    from ashl_core_v1.runtime.open_cradle_tick_dry_run_audit import (
        build_tick_dry_run_audit,
        save_tick_dry_run_audit,
    )

    tick_context = save_open_cradle_tick_context(
        build_open_cradle_tick_context(base_dir, preferred_mode),
        base_dir,
    )
    teacher_gate = build_teacher_gate_for_tick_context(tick_context, teacher_note)
    dry_run = save_tick_dry_run(build_tick_dry_run_record(tick_context, teacher_gate), base_dir)
    audit = save_tick_dry_run_audit(
        build_tick_dry_run_audit(dry_run, teacher_gate, tick_context),
        base_dir,
    )
    return {
        "tick_dry_run_id": dry_run["tick_dry_run_id"],
        "source_tick_context_id": dry_run["source_tick_context_id"],
        "recommended_tick_mode": dry_run["recommended_tick_mode"],
        "teacher_gate_status": teacher_gate["gate_status"],
        "dry_run_status": dry_run["dry_run_status"],
        "dry_run_kind": dry_run["dry_run_kind"],
        "requires_teacher_followup": dry_run["requires_teacher_followup"],
        "proposed_outputs": dry_run["proposed_outputs"],
        "blocked_outputs": dry_run["blocked_outputs"],
        "audit_passed": audit["audit_passed"],
        "teacher_gate": teacher_gate,
        "tick_dry_run": dry_run,
        "tick_dry_run_audit": audit,
    }


def save_tick_dry_run(
    dry_run: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    _validate_tick_dry_run(dry_run)
    dry_run_dir = ensure_tick_dry_run_store(base_dir)
    (dry_run_dir / LAST_TICK_DRY_RUN_FILE).write_text(
        json.dumps(dry_run, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (dry_run_dir / TICK_DRY_RUN_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(dry_run, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(dry_run)


def load_last_tick_dry_run(base_dir: str | Path | None = None) -> dict[str, Any] | None:
    path = resolve_tick_dry_run_dir(base_dir) / LAST_TICK_DRY_RUN_FILE
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_tick_dry_run_history(base_dir: str | Path | None = None) -> dict[str, Any]:
    path = ensure_tick_dry_run_store(base_dir) / TICK_DRY_RUN_HISTORY_FILE
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "tick_dry_run_count": len(records),
        "tick_dry_runs": records,
    }


def _gate_block_reason(tick_context: dict[str, Any] | None) -> str | None:
    if tick_context is None:
        return "tick_context_missing"
    if not tick_context.get("tick_context_id"):
        return "source_tick_context_id_missing"
    if tick_context.get("recommended_tick_mode") not in DRY_RUN_MATRIX:
        return "recommended_tick_mode_unknown"
    blocked_next_surfaces = tick_context.get("blocked_next_surfaces")
    if not blocked_next_surfaces:
        return "blocked_next_surfaces_missing"
    for surface in REQUIRED_CONTEXT_BLOCKED_SURFACES:
        if surface not in blocked_next_surfaces:
            return f"blocked_next_surfaces_missing_{surface}"
    return None


def _needs_teacher_review(tick_context: dict[str, Any]) -> bool:
    return (
        bool(tick_context.get("pending_review_items"))
        or bool(tick_context.get("caregiver_attention_items"))
        or tick_context.get("recommended_tick_mode")
        in {"review_pending", "teacher_wait", "promotion_review_pending"}
    )


def _teacher_gate(
    tick_context: dict[str, Any] | None,
    gate_status: str,
    gate_reason: str,
    teacher_note: str | None,
    allowed_for_dry_run: bool,
) -> dict[str, Any]:
    return {
        "teacher_gate_id": _new_teacher_gate_id(),
        "source_tick_context_id": (tick_context or {}).get("tick_context_id"),
        "recommended_tick_mode": (tick_context or {}).get("recommended_tick_mode"),
        "gate_status": gate_status,
        "gate_reason": gate_reason,
        "teacher_note": teacher_note,
        "allowed_for_dry_run": allowed_for_dry_run,
        "created_at": _now(),
        "trace_refs": list((tick_context or {}).get("trace_refs") or []),
    }


def _preserved_blocked_outputs(
    matrix: dict[str, Any],
    tick_context: dict[str, Any],
) -> list[str]:
    outputs = list(matrix["blocked_outputs"])
    for surface in REQUIRED_CONTEXT_BLOCKED_SURFACES:
        if surface in tick_context.get("blocked_next_surfaces", []) and surface not in outputs:
            outputs.append(surface)
    return outputs


def _trace_refs(tick_context: dict[str, Any], teacher_gate: dict[str, Any]) -> list[str]:
    refs = []
    if tick_context.get("tick_context_id"):
        refs.append(f"tick_context:{tick_context['tick_context_id']}")
    if teacher_gate.get("teacher_gate_id"):
        refs.append(f"teacher_gate:{teacher_gate['teacher_gate_id']}")
    refs.extend(str(ref) for ref in tick_context.get("trace_refs") or [])
    return refs


def _validate_tick_dry_run(dry_run: dict[str, Any]) -> None:
    required = (
        "tick_dry_run_id",
        "source_tick_context_id",
        "source_teacher_gate_id",
        "source_session_id",
        "recommended_tick_mode",
        "dry_run_status",
        "dry_run_kind",
        "dry_run_summary",
        "proposed_outputs",
        "blocked_outputs",
        "requires_teacher_followup",
        "created_at",
        "trace_refs",
    )
    missing = [field for field in required if field not in dry_run]
    if missing:
        raise ValueError("missing tick dry-run fields: " + ", ".join(missing))
    if dry_run["dry_run_status"] not in DRY_RUN_STATUSES:
        raise ValueError(f"unknown dry_run_status: {dry_run['dry_run_status']}")


def _dry_run_summary(recommended_mode: str | None, dry_run_status: str) -> str:
    return f"{recommended_mode or 'unknown'} tick dry-run built with status {dry_run_status}."


def _new_teacher_gate_id() -> str:
    return "open_cradle_teacher_gate_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _new_tick_dry_run_id() -> str:
    return "open_cradle_tick_dry_run_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
