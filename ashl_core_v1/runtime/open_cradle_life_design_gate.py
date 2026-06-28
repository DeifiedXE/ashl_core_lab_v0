"""Design gate for planning ASHL Core v1 open cradle life."""

from __future__ import annotations

import importlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.long_term_cultivation_gap_report import (
    build_long_term_cultivation_gap_report,
)


DEFAULT_REPORT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "reports"
    / "v1_open_cradle_life_design_gate_v0.md"
)

RUNTIME_GAPS = (
    "no_open_ended_event_loop",
    "no_autonomous_environment_ticking",
    "no_environment_scheduler",
    "no_free_action_policy",
    "no_long_horizon_memory_promotion_implementation",
    "no_caregiver_quality_workflow_beyond_cli",
    "no_Unity_Home_integration",
)

CURRENT_ALLOWED_CLAIM = (
    "ASHL Core v1 can support manual fixed-cradle daily operation and has design "
    "prerequisites for planning open cradle life: first-output follow-up, daily "
    "teacher notes, memory promotion queue, environment state model, and continuity "
    "stress checks."
)

CURRENT_NOT_YET_CLAIM = (
    "This is not open cradle life runtime.",
    "This is not autonomous environment ticking.",
    "This is not free action selection.",
    "This is not long-term cultivation readiness.",
    "This is not Unity Home, voice, or external bridge operation.",
)

NEXT_RECOMMENDED_PACKAGES = {
    "Package 31": "ASHL Core v1 Open Cradle Event Loop Design Minimal v0",
    "Package 32": "ASHL Core v1 Cradle Environment Tick Plan Minimal v0",
    "Package 33": "ASHL Core v1 Caregiver Workflow Quality Review Minimal v0",
    "Package 34": "ASHL Core v1 Long-Horizon Memory Promotion Review Minimal v0",
    "Package 35": "ASHL Core v1 Open Cradle Runtime Boundary Review Minimal v0",
}


def build_open_cradle_life_design_gate(base_dir: str | Path | None = None) -> dict[str, Any]:
    gap_report = build_long_term_cultivation_gap_report(base_dir)
    checks = {
        "fixed_daily_operation_ready": gap_report["manual_fixed_daily_ready"],
        "first_output_followup_ready": _module_has(
            "ashl_core_v1.output.first_output_followup",
            ("follow_last_first_output",),
        ),
        "daily_teacher_note_ready": _module_has(
            "ashl_core_v1.teacher_console.daily_teacher_note",
            ("write_daily_teacher_note",),
        ),
        "memory_promotion_queue_ready": _module_has(
            "ashl_core_v1.memory.promotion_queue",
            ("enqueue_memory_promotion_candidate",),
        ),
        "environment_state_model_ready": _module_has(
            "ashl_core_v1.environment.cradle_environment_state",
            ("build_cradle_environment_state_from_case",),
        ),
        "state_continuity_stress_ready": _module_has(
            "ashl_core_v1.runtime.state_continuity_stress",
            ("run_state_continuity_stress",),
        ),
    }
    design_ready = all(checks.values())
    ready_items = [key for key, value in checks.items() if value]
    missing_items = [key for key, value in checks.items() if not value]
    missing_items.extend(RUNTIME_GAPS)
    return {
        "gate_id": _new_gate_id(),
        "status": "design_ready" if design_ready else "design_not_ready",
        **checks,
        "open_cradle_life_design_ready": design_ready,
        "open_cradle_life_runtime_ready": False,
        "ready_items": ready_items,
        "missing_items": missing_items,
        "current_allowed_claim": CURRENT_ALLOWED_CLAIM,
        "current_not_yet_claim": list(CURRENT_NOT_YET_CLAIM),
        "next_recommended_packages": dict(NEXT_RECOMMENDED_PACKAGES),
        "created_at": _now(),
    }


def write_open_cradle_life_design_gate_report(
    path: str | Path | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    gate = build_open_cradle_life_design_gate(base_dir)
    output_path = Path(path) if path is not None else DEFAULT_REPORT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_markdown(gate), encoding="utf-8", newline="\n")
    return {
        "path": str(output_path),
        "gate": gate,
    }


def _module_has(module_name: str, names: tuple[str, ...]) -> bool:
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return False
    return all(hasattr(module, name) for name in names)


def _render_markdown(gate: dict[str, Any]) -> str:
    lines = [
        "# ASHL Core v1 Open Cradle Life Design Gate Minimal v0",
        "",
        f"gate_id: {gate['gate_id']}",
        f"status: {gate['status']}",
        f"open_cradle_life_design_ready: {gate['open_cradle_life_design_ready']}",
        f"open_cradle_life_runtime_ready: {gate['open_cradle_life_runtime_ready']}",
        "",
        "## Readiness",
        "",
    ]
    for key in (
        "fixed_daily_operation_ready",
        "first_output_followup_ready",
        "daily_teacher_note_ready",
        "memory_promotion_queue_ready",
        "environment_state_model_ready",
        "state_continuity_stress_ready",
    ):
        lines.append(f"- {key}: {gate[key]}")
    lines.extend(["", "## Missing Items", ""])
    lines.extend(f"- {item}" for item in gate["missing_items"])
    lines.extend(["", "## Current Allowed Claim", "", gate["current_allowed_claim"]])
    lines.extend(["", "## Current Not Yet Claim", ""])
    lines.extend(f"- {item}" for item in gate["current_not_yet_claim"])
    lines.extend(["", "## Next Recommended Packages", ""])
    lines.extend(
        f"- {name}: {title}" for name, title in gate["next_recommended_packages"].items()
    )
    lines.append("")
    return "\n".join(lines)


def _new_gate_id() -> str:
    return "open_cradle_life_design_gate_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
