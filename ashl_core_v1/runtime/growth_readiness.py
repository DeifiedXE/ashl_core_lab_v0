"""Controlled growth readiness check for ASHL Core v1."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any


DEFAULT_REPORT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "reports"
    / "v1_controlled_growth_readiness_report_v0.md"
)

REQUIRED_READY_KEYS = (
    "data_shapes_ready",
    "multi_case_cradle_ready",
    "review_cli_ready",
    "memory_trace_query_ready",
    "review_routing_matrix_ready",
    "summary_cli_ready",
    "session_persistence_ready",
    "session_start_close_ready",
    "session_replay_ready",
    "teacher_correction_ready",
)

CURRENT_ALLOWED_CLAIM = (
    "ASHL Core v1 can run multiple fixed first-stage cradle circulation cases, "
    "review and summarize them, persist session summaries, replay session history, "
    "and record teacher correction/revoke traces."
)

CURRENT_ALLOWED_CLAIM_ZH = (
    "清音 v1 現在可以跑多種固定初生艙案例，產生審查與記憶追蹤摘要，保存 session 摘要，"
    "讀回 session 歷史，並記錄教師修正與撤銷。"
)

CURRENT_NOT_YET_CLAIM = (
    "This is not daily no-Codex raising yet.",
    "This is not open-ended cradle life.",
    "This is not autonomous growth.",
    "This is not voice, Unity Home, or external bridge.",
    "This is not long-term cultivation readiness.",
)

CURRENT_NOT_YET_CLAIM_ZH = (
    "這還不是日常無 Codex 養育。",
    "這還不是開放式初生艙生活。",
    "這還不是自主成長。",
    "這還不是聲音、Unity Home 或外部橋接。",
    "這還不是長期培育準備完成。",
)

NEXT_RECOMMENDED_PACKAGES = {
    "Package 16": "ASHL Core v1 Integrated Teacher Console Minimal v0",
    "Package 17": "ASHL Core v1 Cradle Daily Run Script Minimal v0",
    "Package 18": "ASHL Core v1 Backup Restore Minimal v0",
    "Package 19": "ASHL Core v1 First Output Candidate Trace Minimal v0",
    "Package 20": "ASHL Core v1 Raising Threshold Review Minimal v0",
}


def build_controlled_growth_readiness_check(base_dir: str | Path | None = None) -> dict[str, Any]:
    checks = {
        "data_shapes_ready": _module_has(
            "ashl_core_v1.body.types",
            ("BodyActionSignal",),
        )
        and _module_has("ashl_core_v1.memory.types", ("MemoryLearningTrace",))
        and _module_has("ashl_core_v1.lesson.types", ("ReviewedLearningDigest",)),
        "multi_case_cradle_ready": _module_has(
            "ashl_core_v1.runtime.cradle_runner",
            ("run_cradle_case", "run_all_cradle_cases"),
        ),
        "review_cli_ready": _module_has("ashl_core_v1.lesson.review_cli", ("main", "build_parser")),
        "memory_trace_query_ready": _module_has("ashl_core_v1.memory.trace_cli", ("main", "build_parser")),
        "review_routing_matrix_ready": _module_has(
            "ashl_core_v1.runtime.review_routing_matrix",
            ("check_all_cradle_cases_against_matrix",),
        ),
        "summary_cli_ready": _module_has("ashl_core_v1.runtime.cradle_summary_cli", ("main", "build_parser")),
        "session_persistence_ready": _module_has(
            "ashl_core_v1.runtime.session_persistence",
            ("build_state_snapshot", "save_session_summary", "load_session_summary"),
        ),
        "session_start_close_ready": _module_has(
            "ashl_core_v1.runtime.cradle_session",
            ("start_cradle_session", "run_case_in_cradle_session", "close_cradle_session"),
        ),
        "session_replay_ready": _module_has(
            "ashl_core_v1.runtime.session_replay",
            ("build_current_session_replay_summary", "build_session_history_replay_summary"),
        ),
        "teacher_correction_ready": _module_has(
            "ashl_core_v1.lesson.correction_store",
            ("create_teacher_correction", "create_teacher_revoke"),
        ),
        "daily_no_codex_ready": False,
    }
    checks["controlled_growth_minimum_ready"] = all(checks[key] for key in REQUIRED_READY_KEYS)
    ready_items = [key for key, value in checks.items() if value is True]
    not_ready_items = [key for key, value in checks.items() if value is False]
    return {
        "title": "ASHL Core v1 Controlled Growth Readiness Check Minimal v0",
        "status": "ready" if checks["controlled_growth_minimum_ready"] else "not_ready",
        "checked_capabilities": checks,
        "ready_items": ready_items,
        "not_ready_items": not_ready_items,
        "current_allowed_claim": CURRENT_ALLOWED_CLAIM,
        "current_allowed_claim_zh": CURRENT_ALLOWED_CLAIM_ZH,
        "current_not_yet_claim": list(CURRENT_NOT_YET_CLAIM),
        "current_not_yet_claim_zh": list(CURRENT_NOT_YET_CLAIM_ZH),
        "next_recommended_packages": dict(NEXT_RECOMMENDED_PACKAGES),
    }


def write_controlled_growth_readiness_report(path: str | Path | None = None) -> dict[str, Any]:
    report = build_controlled_growth_readiness_check()
    output_path = Path(path) if path is not None else DEFAULT_REPORT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_markdown(report), encoding="utf-8", newline="\n")
    return {
        "path": str(output_path),
        "report": report,
    }


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
        "## Checked Capabilities",
        "",
    ]
    for key, value in report["checked_capabilities"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Ready Items", ""])
    lines.extend(f"- {item}" for item in report["ready_items"])
    lines.extend(["", "## Not Ready Items", ""])
    lines.extend(f"- {item}" for item in report["not_ready_items"])
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
    lines.extend(f"- {name}: {title}" for name, title in report["next_recommended_packages"].items())
    lines.append("")
    return "\n".join(lines)
