"""Raising threshold review for ASHL Core v1 manual fixed-cradle operation."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.growth_readiness import build_controlled_growth_readiness_check


DEFAULT_REPORT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "reports"
    / "v1_raising_threshold_review_v0.md"
)

PACKAGE_RANGE = {
    "Package 1-5": "first-stage data shapes and fixed blocked circulation",
    "Package 6-10": "multi-case cradle circulation and milestone report",
    "Package 11-15": (
        "session persistence, replay, correction/revoke, controlled growth readiness"
    ),
    "Package 16-20": (
        "teacher console, daily run, backup/restore, first output candidate trace, "
        "raising threshold review"
    ),
}

CURRENT_ALLOWED_CLAIM = (
    "ASHL Core v1 can support manual fixed-cradle daily operation through an "
    "integrated teacher console, daily run script, session persistence, replay "
    "summaries, teacher correction/revoke records, backup/restore, and "
    "first-output candidate traces."
)

CURRENT_ALLOWED_CLAIM_ZH = (
    "清音 v1 現在可以支援手動固定初生艙日課：整合教師 console、daily run、"
    "session 保存、replay 摘要、教師修正與撤銷記錄、backup/restore，"
    "以及可審查的 first-output candidate trace。"
)

CURRENT_NOT_YET_CLAIM = (
    "This is not open-ended cradle life.",
    "This is not autonomous growth.",
    "This is not full long-term cultivation.",
    "This is not voice or Unity Home integration.",
    "This is not external bridge operation.",
)

CURRENT_NOT_YET_CLAIM_ZH = (
    "這還不是開放式初生艙生活。",
    "這還不是自主成長。",
    "這還不是完整長期培育。",
    "這還不是聲音或 Unity Home 整合。",
    "這還不是外部橋接操作。",
)

NEXT_RECOMMENDED_PACKAGES = {
    "Package 21": "ASHL Core v1 First Output Teacher Review Minimal v0",
    "Package 22": "ASHL Core v1 First Output Promotion Minimal v0",
    "Package 23": "ASHL Core v1 Daily Cradle Operation Audit Minimal v0",
    "Package 24": "ASHL Core v1 Cradle State Continuity Stress Test Minimal v0",
    "Package 25": "ASHL Core v1 Long-Term Cultivation Gap Report Minimal v0",
}


def build_raising_threshold_review(base_dir: str | Path | None = None) -> dict[str, Any]:
    readiness = build_controlled_growth_readiness_check(base_dir)
    thresholds = _build_thresholds(readiness)
    return {
        "title": "ASHL Core v1 Raising Threshold Review Minimal v0",
        "status": "manual_fixed_cradle_ready"
        if thresholds["manual_daily_cli_ready"]
        else "not_ready",
        "package_range": dict(PACKAGE_RANGE),
        "capability_summary": {
            "fixed_cradle_cases": "available",
            "manual_daily_operation": "available" if thresholds["manual_daily_cli_ready"] else "missing",
            "open_ended_life": "not_available",
            "long_term_cultivation": "not_available",
        },
        "thresholds": thresholds,
        "current_allowed_claim": CURRENT_ALLOWED_CLAIM,
        "current_allowed_claim_zh": CURRENT_ALLOWED_CLAIM_ZH,
        "current_not_yet_claim": list(CURRENT_NOT_YET_CLAIM),
        "current_not_yet_claim_zh": list(CURRENT_NOT_YET_CLAIM_ZH),
        "next_recommended_packages": dict(NEXT_RECOMMENDED_PACKAGES),
    }


def write_raising_threshold_review_report(path: str | Path | None = None) -> dict[str, Any]:
    review = build_raising_threshold_review()
    output_path = Path(path) if path is not None else DEFAULT_REPORT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_markdown(review), encoding="utf-8", newline="\n")
    return {
        "path": str(output_path),
        "review": review,
    }


def _build_thresholds(readiness: dict[str, Any]) -> dict[str, bool]:
    fixed_cradle_operation_ready = _module_has(
        "ashl_core_v1.runtime.cradle_runner",
        ("run_all_cradle_cases",),
    ) and _module_has("ashl_core_v1.runtime.cradle_summary", ("summarize_all_cradle_cases",))
    integrated_teacher_console_ready = _module_has(
        "ashl_core_v1.teacher_console.console",
        ("teacher_console_start_session", "teacher_console_run_case"),
    )
    daily_run_ready = _module_has("ashl_core_v1.runtime.daily_run", ("run_cradle_daily",))
    session_persistence_ready = _module_has(
        "ashl_core_v1.runtime.session_persistence",
        ("save_session_summary",),
    )
    session_replay_ready = _module_has(
        "ashl_core_v1.runtime.session_replay",
        ("build_current_session_replay_summary",),
    )
    teacher_correction_ready = _module_has(
        "ashl_core_v1.lesson.correction_store",
        ("create_teacher_correction", "create_teacher_revoke"),
    )
    backup_restore_ready = _module_has(
        "ashl_core_v1.runtime.backup_restore",
        ("create_v1_backup", "restore_v1_backup"),
    )
    first_output_candidate_trace_ready = _module_has(
        "ashl_core_v1.output.first_output_candidate",
        ("build_first_output_candidate_from_last_daily",),
    )
    controlled_growth_minimum_ready = readiness["checked_capabilities"][
        "controlled_growth_minimum_ready"
    ]
    manual_daily_cli_ready = all(
        (
            integrated_teacher_console_ready,
            daily_run_ready,
            session_persistence_ready,
            session_replay_ready,
            teacher_correction_ready,
            backup_restore_ready,
        )
    )
    return {
        "fixed_cradle_operation_ready": fixed_cradle_operation_ready,
        "manual_daily_cli_ready": manual_daily_cli_ready,
        "backup_restore_ready": backup_restore_ready,
        "teacher_correction_ready": teacher_correction_ready,
        "first_output_candidate_trace_ready": first_output_candidate_trace_ready,
        "controlled_growth_minimum_ready": controlled_growth_minimum_ready,
        "daily_no_codex_fixed_case_ready": manual_daily_cli_ready,
        "open_ended_cradle_life_ready": False,
        "long_term_cultivation_ready": False,
    }


def _module_has(module_name: str, names: tuple[str, ...]) -> bool:
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return False
    return all(hasattr(module, name) for name in names)


def _render_markdown(review: dict[str, Any]) -> str:
    lines = [
        f"# {review['title']}",
        "",
        f"Status: {review['status']}",
        "",
        "## Package Range",
        "",
    ]
    lines.extend(f"- {key}: {value}" for key, value in review["package_range"].items())
    lines.extend(["", "## Capability Summary", ""])
    lines.extend(f"- {key}: {value}" for key, value in review["capability_summary"].items())
    lines.extend(["", "## Thresholds", ""])
    lines.extend(f"- {key}: {value}" for key, value in review["thresholds"].items())
    lines.extend(
        [
            "",
            "## Current Allowed Claim",
            "",
            review["current_allowed_claim"],
            "",
            review["current_allowed_claim_zh"],
            "",
            "## Current Not Yet Claim",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in review["current_not_yet_claim"])
    lines.extend([""])
    lines.extend(f"- {item}" for item in review["current_not_yet_claim_zh"])
    lines.extend(["", "## Next Recommended Packages", ""])
    lines.extend(f"- {key}: {value}" for key, value in review["next_recommended_packages"].items())
    lines.append("")
    return "\n".join(lines)
