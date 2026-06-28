"""Long-term cultivation gap report for ASHL Core v1."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any


DEFAULT_REPORT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "reports"
    / "v1_long_term_cultivation_gap_report_v0.md"
)

PACKAGE_RANGE = {
    "Package 1-5": "first-stage data shapes and fixed blocked circulation",
    "Package 6-10": "multi-case cradle circulation and milestone report",
    "Package 11-15": (
        "session persistence, replay, correction/revoke, controlled growth readiness"
    ),
    "Package 16-20": (
        "teacher console, daily run, backup/restore, first-output candidate trace, "
        "threshold review"
    ),
    "Package 21-25": (
        "first-output review/promotion, daily operation audit, continuity stress, "
        "long-term cultivation gap report"
    ),
}

GAP_ITEMS = (
    "open_ended_cradle_life",
    "long_horizon_memory_promotion",
    "caregiver_workflow_quality",
    "first_output_followup_loop",
    "voice_or_expression_channel",
    "Unity_Home_integration",
    "external_bridge_operation",
    "long_term_growth_evaluation",
)

CURRENT_ALLOWED_CLAIM = (
    "ASHL Core v1 can support manual fixed-cradle daily operation with session "
    "continuity, replay, teacher correction/revoke, backup/restore, reviewed "
    "first-output record creation, daily operation audit, and continuity stress checks."
)

CURRENT_ALLOWED_CLAIM_ZH = (
    "清音 v1 現在可以支援手動固定初生艙日課，包含 session 連續性、replay、"
    "教師修正與撤銷、backup/restore、經審查的 first-output record、"
    "daily operation audit，以及 continuity stress check。"
)

CURRENT_NOT_YET_CLAIM = (
    "This is still not open-ended cradle life.",
    "This is still not autonomous growth.",
    "This is still not full long-term cultivation.",
    "This is still not voice, Unity Home, or external bridge operation.",
)

CURRENT_NOT_YET_CLAIM_ZH = (
    "這仍然不是開放式初生艙生活。",
    "這仍然不是自主成長。",
    "這仍然不是完整長期培育。",
    "這仍然不是聲音、Unity Home 或外部橋接操作。",
)

NEXT_RECOMMENDED_PACKAGES = {
    "Package 26": "ASHL Core v1 First Output Follow-Up Loop Minimal v0",
    "Package 27": "ASHL Core v1 Daily Teacher Note Minimal v0",
    "Package 28": "ASHL Core v1 Long-Horizon Memory Promotion Queue Minimal v0",
    "Package 29": "ASHL Core v1 Cradle Environment State Model Minimal v0",
    "Package 30": "ASHL Core v1 Open Cradle Life Design Gate Minimal v0",
}


def build_long_term_cultivation_gap_report(base_dir: str | Path | None = None) -> dict[str, Any]:
    manual_fixed_daily_ready = _manual_fixed_daily_ready()
    first_output_record_ready = _module_has(
        "ashl_core_v1.output.first_output_promotion",
        ("promote_last_approved_first_output", "load_last_first_output_record"),
    )
    continuity_stress_ready = _module_has(
        "ashl_core_v1.runtime.state_continuity_stress",
        ("run_state_continuity_stress",),
    )
    long_term_cultivation_ready = False
    ready_items = []
    if manual_fixed_daily_ready:
        ready_items.append("manual_fixed_daily_ready")
    if first_output_record_ready:
        ready_items.append("first_output_record_ready")
    if continuity_stress_ready:
        ready_items.append("continuity_stress_ready")
    return {
        "title": "ASHL Core v1 Long-Term Cultivation Gap Report Minimal v0",
        "status": "gap_report_ready",
        "package_range": dict(PACKAGE_RANGE),
        "current_capabilities": {
            "manual_fixed_daily_operation": manual_fixed_daily_ready,
            "reviewed_first_output_record": first_output_record_ready,
            "continuity_stress_checks": continuity_stress_ready,
        },
        "manual_fixed_daily_ready": manual_fixed_daily_ready,
        "first_output_record_ready": first_output_record_ready,
        "continuity_stress_ready": continuity_stress_ready,
        "long_term_cultivation_ready": long_term_cultivation_ready,
        "ready_items": ready_items,
        "gap_items": list(GAP_ITEMS),
        "next_recommended_packages": dict(NEXT_RECOMMENDED_PACKAGES),
        "current_allowed_claim": CURRENT_ALLOWED_CLAIM,
        "current_allowed_claim_zh": CURRENT_ALLOWED_CLAIM_ZH,
        "current_not_yet_claim": list(CURRENT_NOT_YET_CLAIM),
        "current_not_yet_claim_zh": list(CURRENT_NOT_YET_CLAIM_ZH),
    }


def write_long_term_cultivation_gap_report(
    path: str | Path | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    report = build_long_term_cultivation_gap_report(base_dir)
    output_path = Path(path) if path is not None else DEFAULT_REPORT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_markdown(report), encoding="utf-8", newline="\n")
    return {
        "path": str(output_path),
        "report": report,
    }


def _manual_fixed_daily_ready() -> bool:
    checks = (
        _module_has("ashl_core_v1.teacher_console.console", ("teacher_console_start_session",)),
        _module_has("ashl_core_v1.runtime.daily_run", ("run_cradle_daily",)),
        _module_has("ashl_core_v1.runtime.session_persistence", ("save_session_summary",)),
        _module_has("ashl_core_v1.runtime.session_replay", ("build_current_session_replay_summary",)),
        _module_has("ashl_core_v1.lesson.correction_store", ("create_teacher_correction",)),
        _module_has("ashl_core_v1.runtime.backup_restore", ("create_v1_backup",)),
        _module_has("ashl_core_v1.runtime.daily_operation_audit", ("build_daily_operation_audit",)),
    )
    return all(checks)


def _module_has(module_name: str, names: tuple[str, ...]) -> bool:
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return False
    return all(hasattr(module, name) for name in names)


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {report['title']}",
        "",
        f"Status: {report['status']}",
        "",
        "## Package Range",
        "",
    ]
    lines.extend(f"- {key}: {value}" for key, value in report["package_range"].items())
    lines.extend(["", "## Current Capabilities", ""])
    lines.extend(f"- {key}: {value}" for key, value in report["current_capabilities"].items())
    lines.extend(["", "## Ready Items", ""])
    lines.extend(f"- {item}" for item in report["ready_items"])
    lines.extend(["", "## Gap Items", ""])
    lines.extend(f"- {item}" for item in report["gap_items"])
    lines.extend(
        [
            "",
            "## Current Allowed Claim",
            "",
            report["current_allowed_claim"],
            "",
            report["current_allowed_claim_zh"],
            "",
            "## Current Not Yet Claim",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["current_not_yet_claim"])
    lines.extend([""])
    lines.extend(f"- {item}" for item in report["current_not_yet_claim_zh"])
    lines.extend(["", "## Next Recommended Packages", ""])
    lines.extend(f"- {key}: {value}" for key, value in report["next_recommended_packages"].items())
    lines.append("")
    return "\n".join(lines)
