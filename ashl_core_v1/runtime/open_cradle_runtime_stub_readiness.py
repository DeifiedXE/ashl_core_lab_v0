"""Readiness review for a minimal teacher-gated open-cradle runtime stub."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OPEN_CRADLE_RUNTIME_STUB_READINESS_ENV = (
    "ASHL_CORE_V1_OPEN_CRADLE_RUNTIME_STUB_READINESS_DIR"
)
DEFAULT_OPEN_CRADLE_RUNTIME_STUB_READINESS_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "open_cradle_runtime_stub_readiness"
)

LAST_RUNTIME_STUB_READINESS_REVIEW_FILE = "last_runtime_stub_readiness_review.json"
RUNTIME_STUB_READINESS_REVIEW_HISTORY_FILE = "runtime_stub_readiness_review_history.jsonl"

SUPPORTED_TICK_MODES = (
    "observe_only",
    "environment_state_refresh",
    "manual_daily_case",
    "promotion_review_pending",
    "review_pending",
    "teacher_wait",
    "stop",
)
TEACHER_GATED_MODES = (
    "promotion_review_pending",
    "review_pending",
    "teacher_wait",
    "manual_daily_case",
)
STILL_BLOCKED_SURFACES = (
    "automatic_tick_execution",
    "background_scheduler",
    "free_action_selection",
    "action_execution",
    "long_term_memory_write",
    "automatic_memory_promotion",
    "external_bridge_operation",
    "voice_output",
    "unity_home_operation",
    "open_ended_cradle_life",
    "autonomous_growth",
)
REQUIRED_CONTEXT_BLOCKED_SURFACES = (
    "automatic_tick_execution",
    "free_action_selection",
    "action_execution",
    "long_term_memory_write",
    "external_bridge_operation",
    "voice_output",
    "unity_home_operation",
)
MINIMAL_STUB_SCOPE = (
    "one_teacher_gated_tick_stub",
    "reads_latest_tick_context",
    "requires_latest_dry_run_audit_passed",
    "creates_tick_stub_record",
    "does_not_schedule_next_tick",
    "does_not_select_action",
    "does_not_execute_action",
    "does_not_write_long_term_memory",
    "does_not_call_external_bridge",
    "stops_after_one_record",
)
CURRENT_ALLOWED_CLAIM = (
    "ASHL Core v1 can review whether the existing tick_context builder, "
    "teacher-gated dry-run records, and dry-run audits are sufficient to start a "
    "minimal teacher-gated one-tick runtime stub package."
)
CURRENT_NOT_YET_CLAIM = (
    "This is not open cradle runtime.",
    "This is not automatic ticking.",
    "This is not a scheduler.",
    "This is not free action selection.",
    "This is not action execution.",
    "This is not long-term memory write.",
    "This is not autonomous growth.",
    "This is not Unity Home, voice, or external bridge operation.",
)
NEXT_READY_PACKAGE = (
    "Package 35: ASHL Core v1 Teacher-Gated One-Tick Runtime Stub Minimal v0"
)
NEXT_PATCH_PACKAGE = (
    "Package 35: ASHL Core v1 Runtime Stub Missing Prerequisite Patch Minimal v0"
)


def resolve_open_cradle_runtime_stub_readiness_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(OPEN_CRADLE_RUNTIME_STUB_READINESS_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_OPEN_CRADLE_RUNTIME_STUB_READINESS_DIR


def ensure_open_cradle_runtime_stub_readiness_store(
    base_dir: str | Path | None = None,
) -> Path:
    readiness_dir = resolve_open_cradle_runtime_stub_readiness_dir(base_dir)
    readiness_dir.mkdir(parents=True, exist_ok=True)
    (readiness_dir / RUNTIME_STUB_READINESS_REVIEW_HISTORY_FILE).touch(exist_ok=True)
    return readiness_dir


def collect_runtime_stub_readiness_sources(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    from ashl_core_v1.runtime.open_cradle_tick_context import (
        load_last_open_cradle_tick_context,
    )
    from ashl_core_v1.runtime.open_cradle_tick_dry_run import load_last_tick_dry_run
    from ashl_core_v1.runtime.open_cradle_tick_dry_run_audit import (
        load_last_tick_dry_run_audit,
    )

    tick_context = load_last_open_cradle_tick_context(base_dir)
    tick_dry_run = load_last_tick_dry_run(base_dir)
    tick_dry_run_audit = load_last_tick_dry_run_audit(base_dir)
    return {
        "tick_context": tick_context,
        "tick_dry_run": tick_dry_run,
        "tick_dry_run_audit": tick_dry_run_audit,
        "teacher_gate_status": _infer_teacher_gate_status(tick_dry_run),
    }


def evaluate_runtime_stub_readiness(sources: dict[str, Any]) -> dict[str, Any]:
    tick_context = sources.get("tick_context")
    dry_run = sources.get("tick_dry_run")
    audit = sources.get("tick_dry_run_audit")
    teacher_gate_status = sources.get("teacher_gate_status")

    tick_context_ready = (
        tick_context is not None
        and tick_context.get("tick_context_status") == "built"
        and bool(tick_context.get("recommended_tick_mode"))
        and bool(tick_context.get("blocked_next_surfaces"))
    )
    teacher_gate_ready = teacher_gate_status in {
        "allowed_for_dry_run",
        "needs_teacher_review",
    }
    dry_run_ready = (
        dry_run is not None
        and dry_run.get("dry_run_status") in {"dry_run_created", "teacher_review_required"}
        and bool(dry_run.get("dry_run_kind"))
        and isinstance(dry_run.get("proposed_outputs"), list)
        and isinstance(dry_run.get("blocked_outputs"), list)
    )
    dry_run_audit_passed = (
        audit is not None
        and audit.get("audit_passed") is True
        and audit.get("no_runtime_execution") is True
        and audit.get("no_action_selection") is True
        and audit.get("no_action_execution") is True
        and audit.get("no_long_term_memory_write") is True
        and audit.get("no_external_bridge") is True
    )
    blocked_surfaces_preserved = _blocked_surfaces_preserved(tick_context, audit)
    readiness = {
        "tick_context_ready": tick_context_ready,
        "teacher_gate_ready": teacher_gate_ready,
        "dry_run_ready": dry_run_ready,
        "dry_run_audit_passed": dry_run_audit_passed,
        "blocked_surfaces_preserved": blocked_surfaces_preserved,
    }
    readiness["missing_items"] = [
        key for key, value in readiness.items() if value is not True
    ]
    readiness["runtime_stub_design_ready"] = all(readiness[key] for key in (
        "tick_context_ready",
        "teacher_gate_ready",
        "dry_run_ready",
        "dry_run_audit_passed",
        "blocked_surfaces_preserved",
    ))
    readiness["runtime_stub_implementation_ready"] = readiness[
        "runtime_stub_design_ready"
    ]
    return readiness


def build_open_cradle_runtime_stub_readiness_review(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    sources = collect_runtime_stub_readiness_sources(base_dir)
    readiness = evaluate_runtime_stub_readiness(sources)
    tick_context = sources.get("tick_context") or {}
    dry_run = sources.get("tick_dry_run") or {}
    audit = sources.get("tick_dry_run_audit") or {}
    ready = readiness["runtime_stub_design_ready"]
    return {
        "review_id": _new_review_id(),
        "status": "ready" if ready else "not_ready",
        "source_tick_context_id": tick_context.get("tick_context_id"),
        "source_tick_dry_run_id": dry_run.get("tick_dry_run_id"),
        "source_tick_dry_run_audit_id": audit.get("tick_dry_run_audit_id"),
        "tick_context_ready": readiness["tick_context_ready"],
        "teacher_gate_ready": readiness["teacher_gate_ready"],
        "dry_run_ready": readiness["dry_run_ready"],
        "dry_run_audit_passed": readiness["dry_run_audit_passed"],
        "blocked_surfaces_preserved": readiness["blocked_surfaces_preserved"],
        "supported_tick_modes": list(SUPPORTED_TICK_MODES),
        "teacher_gated_modes": list(TEACHER_GATED_MODES),
        "runtime_stub_design_ready": readiness["runtime_stub_design_ready"],
        "runtime_stub_implementation_ready": readiness[
            "runtime_stub_implementation_ready"
        ],
        "minimal_stub_scope": list(MINIMAL_STUB_SCOPE),
        "required_teacher_gates": _required_teacher_gates(),
        "still_blocked_surfaces": list(STILL_BLOCKED_SURFACES),
        "missing_items": readiness["missing_items"],
        "current_allowed_claim": CURRENT_ALLOWED_CLAIM,
        "current_not_yet_claim": list(CURRENT_NOT_YET_CLAIM),
        "next_recommended_package": NEXT_READY_PACKAGE if ready else NEXT_PATCH_PACKAGE,
        "created_at": _now(),
        "trace_refs": _trace_refs(tick_context, dry_run, audit),
    }


def save_open_cradle_runtime_stub_readiness_review(
    review: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    readiness_dir = ensure_open_cradle_runtime_stub_readiness_store(base_dir)
    (readiness_dir / LAST_RUNTIME_STUB_READINESS_REVIEW_FILE).write_text(
        json.dumps(review, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (readiness_dir / RUNTIME_STUB_READINESS_REVIEW_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(review, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(review)


def load_last_open_cradle_runtime_stub_readiness_review(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = (
        resolve_open_cradle_runtime_stub_readiness_dir(base_dir)
        / LAST_RUNTIME_STUB_READINESS_REVIEW_FILE
    )
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_open_cradle_runtime_stub_readiness_reviews(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    path = (
        ensure_open_cradle_runtime_stub_readiness_store(base_dir)
        / RUNTIME_STUB_READINESS_REVIEW_HISTORY_FILE
    )
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return {
        "runtime_stub_readiness_review_count": len(records),
        "runtime_stub_readiness_reviews": records,
    }


def write_open_cradle_runtime_stub_readiness_report(
    path: str | Path | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    review = save_open_cradle_runtime_stub_readiness_review(
        build_open_cradle_runtime_stub_readiness_review(base_dir),
        base_dir,
    )
    output_path = (
        Path(path)
        if path is not None
        else Path(__file__).resolve().parents[1]
        / "docs"
        / "reports"
        / "v1_open_cradle_runtime_stub_readiness_review_v0.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_markdown(review), encoding="utf-8", newline="\n")
    return {
        "path": str(output_path),
        "review": review,
    }


def _infer_teacher_gate_status(dry_run: dict[str, Any] | None) -> str | None:
    if dry_run is None:
        return None
    if dry_run.get("teacher_gate_status"):
        return str(dry_run["teacher_gate_status"])
    dry_run_status = dry_run.get("dry_run_status")
    if dry_run_status == "dry_run_created":
        return "allowed_for_dry_run"
    if dry_run_status == "teacher_review_required":
        return "needs_teacher_review"
    if dry_run_status == "blocked_by_gate":
        return "blocked"
    return None


def _blocked_surfaces_preserved(
    tick_context: dict[str, Any] | None,
    audit: dict[str, Any] | None,
) -> bool:
    if tick_context is None or audit is None:
        return False
    context_blocked = set(tick_context.get("blocked_next_surfaces") or [])
    context_preserved = all(
        surface in context_blocked for surface in REQUIRED_CONTEXT_BLOCKED_SURFACES
    )
    return (
        context_preserved
        and audit.get("blocked_surfaces_preserved") is True
        and audit.get("no_external_bridge") is True
    )


def _required_teacher_gates() -> list[dict[str, str]]:
    return [
        {
            "gate_name": "missing_or_invalid_context_gate",
            "purpose": "block runtime stub when tick_context is missing or invalid",
            "blocks_when": "tick_context_ready is false",
            "allows_when": "tick_context_ready is true",
        },
        {
            "gate_name": "dry_run_audit_required_gate",
            "purpose": "require a passing dry-run audit before any stub package",
            "blocks_when": "dry_run_audit_passed is false",
            "allows_when": "dry_run_audit_passed is true",
        },
        {
            "gate_name": "review_pending_teacher_gate",
            "purpose": "preserve teacher control for review_pending mode",
            "blocks_when": "review_pending lacks teacher gate",
            "allows_when": "teacher-gated dry-run exists",
        },
        {
            "gate_name": "promotion_review_teacher_gate",
            "purpose": "prevent queued memory candidates from becoming memory",
            "blocks_when": "promotion review lacks teacher gate",
            "allows_when": "promotion review remains dry-run only",
        },
        {
            "gate_name": "teacher_wait_gate",
            "purpose": "stop when caregiver attention is required",
            "blocks_when": "teacher_wait has no teacher follow-up path",
            "allows_when": "teacher_wait remains a gated dry-run",
        },
        {
            "gate_name": "stop_mode_gate",
            "purpose": "keep stop mode non-executing",
            "blocks_when": "stop mode would schedule another tick",
            "allows_when": "stop mode creates only a record",
        },
        {
            "gate_name": "manual_run_only_gate",
            "purpose": "keep manual_daily_case bounded to manual operation",
            "blocks_when": "manual mode would become automatic execution",
            "allows_when": "manual mode remains teacher-gated and one-tick only",
        },
    ]


def _trace_refs(
    tick_context: dict[str, Any],
    dry_run: dict[str, Any],
    audit: dict[str, Any],
) -> list[str]:
    refs = []
    if tick_context.get("tick_context_id"):
        refs.append(f"tick_context:{tick_context['tick_context_id']}")
    if dry_run.get("tick_dry_run_id"):
        refs.append(f"tick_dry_run:{dry_run['tick_dry_run_id']}")
    if audit.get("tick_dry_run_audit_id"):
        refs.append(f"tick_dry_run_audit:{audit['tick_dry_run_audit_id']}")
    refs.extend(str(ref) for ref in tick_context.get("trace_refs") or [])
    return refs


def _render_markdown(review: dict[str, Any]) -> str:
    lines = [
        "# ASHL Core v1 Open Cradle Runtime Stub Readiness Review Minimal v0",
        "",
        f"review_id: {review['review_id']}",
        f"status: {review['status']}",
        f"runtime_stub_design_ready: {review['runtime_stub_design_ready']}",
        f"runtime_stub_implementation_ready: {review['runtime_stub_implementation_ready']}",
        "",
        "## Readiness",
        "",
    ]
    for key in (
        "tick_context_ready",
        "teacher_gate_ready",
        "dry_run_ready",
        "dry_run_audit_passed",
        "blocked_surfaces_preserved",
    ):
        lines.append(f"- {key}: {review[key]}")
    lines.extend(["", "## Minimal Stub Scope", ""])
    lines.extend(f"- {item}" for item in review["minimal_stub_scope"])
    lines.extend(["", "## Still Blocked Surfaces", ""])
    lines.extend(f"- {item}" for item in review["still_blocked_surfaces"])
    lines.extend(["", "## Missing Items", ""])
    lines.extend(f"- {item}" for item in review["missing_items"])
    lines.extend(["", "## Current Allowed Claim", "", review["current_allowed_claim"]])
    lines.extend(["", "## Current Not Yet Claim", ""])
    lines.extend(f"- {item}" for item in review["current_not_yet_claim"])
    lines.extend(["", "## Next Recommended Package", "", review["next_recommended_package"], ""])
    return "\n".join(lines)


def _new_review_id() -> str:
    return "open_cradle_runtime_stub_readiness_review_" + datetime.now(
        timezone.utc
    ).strftime("%Y%m%d%H%M%S%f")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
