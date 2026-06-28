"""Planning precheck for a future teacher-gated two-tick runtime stub."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.teacher_gated_one_tick_runtime_stub import (
    ALLOWED_TRIGGER_KINDS,
    PRESERVED_BLOCKED_SURFACES,
    load_last_tick_stub_record,
)


TWO_TICK_PRECHECK_ENV = "ASHL_CORE_V1_TWO_TICK_RUNTIME_STUB_PRECHECK_DIR"
DEFAULT_TWO_TICK_PRECHECK_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "two_tick_runtime_stub_planning_precheck"
)

LAST_TWO_TICK_PRECHECK_FILE = "last_two_tick_precheck.json"
TWO_TICK_PRECHECK_HISTORY_FILE = "two_tick_precheck_history.jsonl"

READY_NEXT_PACKAGE = (
    "Package 37: ASHL Core v1 Teacher-Gated Two-Tick Runtime Stub Minimal v0"
)
PATCH_NEXT_PACKAGE = (
    "Package 37: ASHL Core v1 Two-Tick Runtime Stub Missing Prerequisite Patch Minimal v0"
)
CURRENT_ALLOWED_CLAIM = (
    "ASHL Core v1 can verify that the first teacher-gated one-tick runtime stub "
    "stayed within scope and can produce a planning precheck for a future "
    "teacher-gated second tick."
)
CURRENT_NOT_YET_CLAIM = (
    "This is not a second runtime tick.",
    "This is not a continuous runtime loop.",
    "This is not automatic ticking.",
    "This is not a scheduler.",
    "This is not free action selection.",
    "This is not action execution.",
    "This is not long-term memory write.",
    "This is not autonomous growth.",
    "This is not Unity Home, voice, or external bridge operation.",
)
SECOND_TICK_ALLOWED_SCOPE = (
    "create_one_second_tick_stub_record",
    "manual_trigger_only",
    "read_first_tick_stub_record_as_previous_trace",
    "build_fresh_tick_context",
    "run_teacher_gated_dry_run_again",
    "require_dry_run_audit_passed",
    "stop_after_second_tick",
)
SECOND_TICK_BLOCKED_SURFACES = (
    "automatic_third_tick",
    "automatic_tick_execution",
    "background_scheduler",
    "scheduler",
    "free_action_selection",
    "action_execution",
    "long_term_memory_write",
    "automatic_memory_promotion",
    "unity_home_operation",
    "voice_output",
    "external_bridge_operation",
    "open_ended_cradle_life",
    "autonomous_growth",
)
SECOND_TICK_REQUIRED_INPUTS = (
    "first_tick_stub_record",
    "fresh_tick_context",
    "teacher_gated_dry_run",
    "dry_run_audit_passed",
    "manual_trigger",
)
SECOND_TICK_STOP_CONDITIONS = (
    "stop_after_second_tick",
    "stop_if_teacher_review_required",
    "stop_if_dry_run_audit_failed",
    "stop_if_blocked_surface_missing",
    "stop_if_trigger_not_manual",
    "stop_if_context_missing",
)


def resolve_two_tick_runtime_stub_planning_precheck_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(TWO_TICK_PRECHECK_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_TWO_TICK_PRECHECK_DIR


def ensure_two_tick_runtime_stub_planning_precheck_store(
    base_dir: str | Path | None = None,
) -> Path:
    precheck_dir = resolve_two_tick_runtime_stub_planning_precheck_dir(base_dir)
    precheck_dir.mkdir(parents=True, exist_ok=True)
    (precheck_dir / TWO_TICK_PRECHECK_HISTORY_FILE).touch(exist_ok=True)
    return precheck_dir


def collect_two_tick_precheck_sources(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    return {
        "first_tick_stub_record": load_last_tick_stub_record(base_dir),
    }


def evaluate_first_tick_cleanliness(
    tick_stub_record: dict[str, Any] | None,
) -> dict[str, Any]:
    blocked_surfaces = set((tick_stub_record or {}).get("preserved_blocked_surfaces") or [])
    source_ids = tick_stub_record or {}
    result = {
        "first_tick_record_present": tick_stub_record is not None,
        "first_tick_stopped_after_one_tick": (tick_stub_record or {}).get(
            "stopped_after_one_tick"
        )
        is True,
        "first_tick_manual_trigger_only": (tick_stub_record or {}).get("trigger_kind")
        in ALLOWED_TRIGGER_KINDS,
        "first_tick_teacher_gated": (tick_stub_record or {}).get("teacher_gate_status")
        in {"allowed_for_one_tick_stub", "needs_teacher_review"},
        "first_tick_preserved_blocked_surfaces": all(
            surface in blocked_surfaces for surface in PRESERVED_BLOCKED_SURFACES
        ),
        "first_tick_no_scheduler": "background_scheduler" in blocked_surfaces,
        "first_tick_no_action_selection": "free_action_selection" in blocked_surfaces,
        "first_tick_no_action_execution": "action_execution" in blocked_surfaces,
        "first_tick_no_long_term_memory_write": "long_term_memory_write"
        in blocked_surfaces
        and "automatic_memory_promotion" in blocked_surfaces,
        "first_tick_no_external_bridge": "external_bridge_operation" in blocked_surfaces,
        "source_tick_context_present": bool(source_ids.get("source_tick_context_id")),
        "source_tick_dry_run_present": bool(source_ids.get("source_tick_dry_run_id")),
        "source_tick_dry_run_audit_present": bool(
            source_ids.get("source_tick_dry_run_audit_id")
        ),
    }
    clean_keys = (
        "first_tick_record_present",
        "first_tick_stopped_after_one_tick",
        "first_tick_manual_trigger_only",
        "first_tick_teacher_gated",
        "first_tick_preserved_blocked_surfaces",
        "first_tick_no_scheduler",
        "first_tick_no_action_selection",
        "first_tick_no_action_execution",
        "first_tick_no_long_term_memory_write",
        "first_tick_no_external_bridge",
    )
    ready_keys = (
        *clean_keys,
        "source_tick_context_present",
        "source_tick_dry_run_present",
        "source_tick_dry_run_audit_present",
    )
    result["first_tick_clean"] = all(result[key] for key in clean_keys)
    result["second_tick_planning_ready"] = all(result[key] for key in ready_keys)
    result["missing_items"] = [key for key in ready_keys if result[key] is not True]
    return result


def build_second_tick_context_plan(tick_stub_record: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_first_tick_stub_id": tick_stub_record.get("tick_stub_id"),
        "source_previous_tick_mode": tick_stub_record.get("tick_mode"),
        "source_previous_tick_stub_kind": tick_stub_record.get("tick_stub_kind"),
        "source_previous_tick_summary": tick_stub_record.get("tick_stub_summary"),
        "next_context_source_policy": [
            "derive_from_first_tick_stub_record",
            "plus_refresh_tick_context_before_second_tick",
        ],
        "required_refresh_sources": [
            "fresh_tick_context",
            "teacher_gated_dry_run",
            "dry_run_audit",
        ],
        "carry_forward_refs": _carry_forward_refs(tick_stub_record),
    }


def build_second_tick_gate_plan() -> dict[str, Any]:
    return {
        "gate_required": True,
        "gate_reason": "second_tick_must_repeat_teacher_gate_after_fresh_context",
        "requires_fresh_tick_context": True,
        "requires_teacher_gated_dry_run": True,
        "requires_dry_run_audit": True,
        "requires_manual_trigger": True,
    }


def build_two_tick_runtime_stub_planning_precheck(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    sources = collect_two_tick_precheck_sources(base_dir)
    first_tick = sources["first_tick_stub_record"]
    cleanliness = evaluate_first_tick_cleanliness(first_tick)
    ready = cleanliness["second_tick_planning_ready"]
    context_plan = (
        build_second_tick_context_plan(first_tick)
        if first_tick is not None
        else _missing_second_tick_context_plan()
    )
    precheck = {
        "precheck_id": _new_precheck_id(),
        "status": "ready" if ready else "not_ready",
        "source_first_tick_stub_id": (first_tick or {}).get("tick_stub_id"),
        "source_readiness_review_id": (first_tick or {}).get("source_readiness_review_id"),
        "source_tick_context_id": (first_tick or {}).get("source_tick_context_id"),
        "source_tick_dry_run_id": (first_tick or {}).get("source_tick_dry_run_id"),
        "source_tick_dry_run_audit_id": (first_tick or {}).get(
            "source_tick_dry_run_audit_id"
        ),
        "first_tick_record_present": cleanliness["first_tick_record_present"],
        "first_tick_clean": cleanliness["first_tick_clean"],
        "first_tick_stopped_after_one_tick": cleanliness[
            "first_tick_stopped_after_one_tick"
        ],
        "first_tick_manual_trigger_only": cleanliness["first_tick_manual_trigger_only"],
        "first_tick_teacher_gated": cleanliness["first_tick_teacher_gated"],
        "first_tick_preserved_blocked_surfaces": cleanliness[
            "first_tick_preserved_blocked_surfaces"
        ],
        "first_tick_no_scheduler": cleanliness["first_tick_no_scheduler"],
        "first_tick_no_action_selection": cleanliness["first_tick_no_action_selection"],
        "first_tick_no_action_execution": cleanliness["first_tick_no_action_execution"],
        "first_tick_no_long_term_memory_write": cleanliness[
            "first_tick_no_long_term_memory_write"
        ],
        "first_tick_no_external_bridge": cleanliness["first_tick_no_external_bridge"],
        "second_tick_planning_ready": ready,
        "second_tick_context_plan": context_plan,
        "second_tick_gate_plan": build_second_tick_gate_plan(),
        "second_tick_allowed_scope": list(SECOND_TICK_ALLOWED_SCOPE),
        "second_tick_blocked_surfaces": list(SECOND_TICK_BLOCKED_SURFACES),
        "second_tick_required_inputs": list(SECOND_TICK_REQUIRED_INPUTS),
        "second_tick_stop_conditions": list(SECOND_TICK_STOP_CONDITIONS),
        "missing_items": cleanliness["missing_items"],
        "next_recommended_package": READY_NEXT_PACKAGE if ready else PATCH_NEXT_PACKAGE,
        "current_allowed_claim": CURRENT_ALLOWED_CLAIM,
        "current_not_yet_claim": list(CURRENT_NOT_YET_CLAIM),
        "created_at": _now(),
        "trace_refs": _trace_refs(first_tick),
    }
    _validate_precheck(precheck)
    return precheck


def save_two_tick_runtime_stub_planning_precheck(
    precheck: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    _validate_precheck(precheck)
    precheck_dir = ensure_two_tick_runtime_stub_planning_precheck_store(base_dir)
    (precheck_dir / LAST_TWO_TICK_PRECHECK_FILE).write_text(
        json.dumps(precheck, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (precheck_dir / TWO_TICK_PRECHECK_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(precheck, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(precheck)


def load_last_two_tick_runtime_stub_planning_precheck(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = (
        resolve_two_tick_runtime_stub_planning_precheck_dir(base_dir)
        / LAST_TWO_TICK_PRECHECK_FILE
    )
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_two_tick_runtime_stub_planning_prechecks(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    path = (
        ensure_two_tick_runtime_stub_planning_precheck_store(base_dir)
        / TWO_TICK_PRECHECK_HISTORY_FILE
    )
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "two_tick_precheck_count": len(records),
        "two_tick_prechecks": records,
    }


def write_two_tick_runtime_stub_planning_precheck_report(
    path: str | Path | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    precheck = save_two_tick_runtime_stub_planning_precheck(
        build_two_tick_runtime_stub_planning_precheck(base_dir),
        base_dir,
    )
    output_path = (
        Path(path)
        if path is not None
        else Path(__file__).resolve().parents[1]
        / "docs"
        / "reports"
        / "v1_two_tick_runtime_stub_planning_precheck_v0.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_markdown(precheck), encoding="utf-8", newline="\n")
    return {
        "path": str(output_path),
        "precheck": precheck,
    }


def _missing_second_tick_context_plan() -> dict[str, Any]:
    return {
        "source_first_tick_stub_id": None,
        "source_previous_tick_mode": None,
        "source_previous_tick_stub_kind": None,
        "source_previous_tick_summary": None,
        "next_context_source_policy": [
            "derive_from_first_tick_stub_record",
            "plus_refresh_tick_context_before_second_tick",
        ],
        "required_refresh_sources": [
            "fresh_tick_context",
            "teacher_gated_dry_run",
            "dry_run_audit",
        ],
        "carry_forward_refs": [],
    }


def _carry_forward_refs(tick_stub_record: dict[str, Any]) -> list[str]:
    refs = []
    if tick_stub_record.get("tick_stub_id"):
        refs.append(f"first_tick_stub_record:{tick_stub_record['tick_stub_id']}")
    refs.extend(str(ref) for ref in tick_stub_record.get("trace_refs") or [])
    return refs


def _trace_refs(tick_stub_record: dict[str, Any] | None) -> list[str]:
    if tick_stub_record is None:
        return []
    refs = _carry_forward_refs(tick_stub_record)
    if tick_stub_record.get("source_tick_context_id"):
        refs.append(f"source_tick_context:{tick_stub_record['source_tick_context_id']}")
    if tick_stub_record.get("source_tick_dry_run_id"):
        refs.append(f"source_tick_dry_run:{tick_stub_record['source_tick_dry_run_id']}")
    if tick_stub_record.get("source_tick_dry_run_audit_id"):
        refs.append(
            "source_tick_dry_run_audit:"
            + str(tick_stub_record["source_tick_dry_run_audit_id"])
        )
    return refs


def _validate_precheck(precheck: dict[str, Any]) -> None:
    required = (
        "precheck_id",
        "status",
        "source_first_tick_stub_id",
        "source_readiness_review_id",
        "source_tick_context_id",
        "source_tick_dry_run_id",
        "source_tick_dry_run_audit_id",
        "first_tick_record_present",
        "first_tick_clean",
        "first_tick_stopped_after_one_tick",
        "first_tick_manual_trigger_only",
        "first_tick_teacher_gated",
        "first_tick_preserved_blocked_surfaces",
        "first_tick_no_scheduler",
        "first_tick_no_action_selection",
        "first_tick_no_action_execution",
        "first_tick_no_long_term_memory_write",
        "first_tick_no_external_bridge",
        "second_tick_planning_ready",
        "second_tick_context_plan",
        "second_tick_gate_plan",
        "second_tick_allowed_scope",
        "second_tick_blocked_surfaces",
        "second_tick_required_inputs",
        "second_tick_stop_conditions",
        "missing_items",
        "next_recommended_package",
        "current_allowed_claim",
        "current_not_yet_claim",
        "created_at",
        "trace_refs",
    )
    missing = [field for field in required if field not in precheck]
    if missing:
        raise ValueError("missing two-tick precheck fields: " + ", ".join(missing))


def _render_markdown(precheck: dict[str, Any]) -> str:
    lines = [
        "# ASHL Core v1 Teacher-Gated Two-Tick Runtime Stub Planning Precheck Minimal v0",
        "",
        f"precheck_id: {precheck['precheck_id']}",
        f"status: {precheck['status']}",
        f"first_tick_clean: {precheck['first_tick_clean']}",
        f"second_tick_planning_ready: {precheck['second_tick_planning_ready']}",
        "",
        "## First Tick Cleanliness",
        "",
    ]
    for key in (
        "first_tick_record_present",
        "first_tick_stopped_after_one_tick",
        "first_tick_manual_trigger_only",
        "first_tick_teacher_gated",
        "first_tick_preserved_blocked_surfaces",
        "first_tick_no_scheduler",
        "first_tick_no_action_selection",
        "first_tick_no_action_execution",
        "first_tick_no_long_term_memory_write",
        "first_tick_no_external_bridge",
    ):
        lines.append(f"- {key}: {precheck[key]}")
    lines.extend(["", "## Second Tick Allowed Scope", ""])
    lines.extend(f"- {item}" for item in precheck["second_tick_allowed_scope"])
    lines.extend(["", "## Second Tick Blocked Surfaces", ""])
    lines.extend(f"- {item}" for item in precheck["second_tick_blocked_surfaces"])
    lines.extend(["", "## Missing Items", ""])
    lines.extend(f"- {item}" for item in precheck["missing_items"])
    lines.extend(["", "## Current Allowed Claim", "", precheck["current_allowed_claim"]])
    lines.extend(["", "## Current Not Yet Claim", ""])
    lines.extend(f"- {item}" for item in precheck["current_not_yet_claim"])
    lines.extend(["", "## Next Recommended Package", "", precheck["next_recommended_package"], ""])
    return "\n".join(lines)


def _new_precheck_id() -> str:
    return "two_tick_runtime_stub_planning_precheck_" + datetime.now(
        timezone.utc
    ).strftime("%Y%m%d%H%M%S%f")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
