"""Milestone report builder for ASHL Core v1 multi-case cradle work."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.cradle_cases import list_cradle_case_ids
from ashl_core_v1.runtime.cradle_summary import summarize_all_cradle_cases
from ashl_core_v1.runtime.review_routing_matrix import check_all_cradle_cases_against_matrix


DEFAULT_REPORT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "reports"
    / "v1_multi_case_cradle_milestone_report_v0.md"
)


PACKAGE_RANGE = {
    "Package 1": "First-Stage Data Shapes Minimal v0",
    "Package 2": "Blocked Manual Circulation Sample Minimal v0",
    "Package 3": "Learning Review CLI Minimal v0",
    "Package 4": "Memory Learning Trace Query Minimal v0",
    "Package 5": "Fixed Circulation Runner Minimal v0",
    "Package 6": "Multi-Case Cradle Circulation Samples Minimal v0",
    "Package 7": "Multi-Case Cradle Runner Minimal v0",
    "Package 8": "Review Routing Expectation Matrix Minimal v0",
    "Package 9": "Cradle Run Summary CLI Minimal v0",
    "Package 10": "Multi-Case Cradle Milestone Report Minimal v0",
}

COMPLETED_CAPABILITIES = (
    "v1 has first-stage data shapes.",
    "v1 has a blocked manual circulation sample.",
    "v1 has a learning review CLI.",
    "v1 has memory learning trace query CLI.",
    "v1 has fixed blocked circulation runner.",
    "v1 has multi-case cradle samples.",
    "v1 has multi-case cradle runner.",
    "v1 has review/routing expectation matrix.",
    "v1 has human-readable cradle summaries.",
)

CURRENT_ALLOWED_CLAIM = (
    "ASHL Core v1 can run fixed first-stage cradle circulation cases where "
    "perception-readable data, endocrine signal, learning digest, teacher review "
    "record, reviewed learning digest, memory learning trace, memory routing trace, "
    "memory application data, thought read trace, influence trace, thought signal, "
    "and body action signal are linked and summarized across multiple controlled "
    "case types."
)

CURRENT_ALLOWED_CLAIM_ZH = (
    "清音 v1 現在可以在固定初生艙案例裡，跑出多種受教情境的完整資料循環，"
    "並能查審查、記憶追蹤、讀回與影響摘要。"
)

CURRENT_NOT_YET_CLAIM = (
    "This is not free runtime.",
    "This is not daily no-Codex raising yet.",
    "This is not open-ended cradle life.",
    "This is not cross-session growth.",
    "This is not voice or external bridge.",
    "This is not Unity Home integration.",
)

CURRENT_NOT_YET_CLAIM_ZH = (
    "這還不是清音正式開始生活。",
    "這還不是日常不用 Codex。",
    "這還不是長期培養。",
    "這還不是聲音、Unity Home 或外界橋接。",
)

NEXT_RECOMMENDED_PACKAGES = {
    "Package 11": "ASHL Core v1 Session Persistence Minimal v0",
    "Package 12": "ASHL Core v1 Cradle Session Start Close Minimal v0",
    "Package 13": "ASHL Core v1 Cradle Session Replay Summary Minimal v0",
    "Package 14": "ASHL Core v1 Teacher Correction and Revoke Minimal v0",
    "Package 15": "ASHL Core v1 Controlled Growth Readiness Check Minimal v0",
}

TEST_COMMANDS = (
    "py -3 -m unittest ashl_core_v1.tests.test_multi_case_cradle_milestone_report",
    "py -3 -m unittest discover ashl_core_v1",
    "git diff --check",
    "git status --short",
)


def build_multi_case_cradle_milestone_report() -> dict[str, Any]:
    summary = summarize_all_cradle_cases()
    matrix_result = check_all_cradle_cases_against_matrix()
    return {
        "title": "ASHL Core v1 Multi-Case Cradle Milestone Report v0",
        "status": "complete",
        "package_range": dict(PACKAGE_RANGE),
        "completed_capabilities": list(COMPLETED_CAPABILITIES),
        "case_inventory": list(list_cradle_case_ids()),
        "review_routing_summary": {
            "case_count": matrix_result["case_count"],
            "all_passed": matrix_result["all_passed"],
            "approved_count": summary["approved_count"],
            "blocked_by_review_count": summary["blocked_by_review_count"],
            "routed_count": summary["routed_count"],
            "not_routed_count": summary["not_routed_count"],
            "influence_visible_count": summary["influence_visible_count"],
        },
        "teacher_usability_summary": (
            "The user can seed and review learning digests, inspect reviewed records, "
            "query memory traces, run fixed cradle cases, validate routing, and read "
            "compact case summaries."
        ),
        "current_allowed_claim": CURRENT_ALLOWED_CLAIM,
        "current_allowed_claim_zh": CURRENT_ALLOWED_CLAIM_ZH,
        "current_not_yet_claim": list(CURRENT_NOT_YET_CLAIM),
        "current_not_yet_claim_zh": list(CURRENT_NOT_YET_CLAIM_ZH),
        "next_recommended_packages": dict(NEXT_RECOMMENDED_PACKAGES),
        "test_commands": list(TEST_COMMANDS),
    }


def write_multi_case_cradle_milestone_report(path: str | None = None) -> dict[str, Any]:
    report = build_multi_case_cradle_milestone_report()
    output_path = Path(path) if path is not None else DEFAULT_REPORT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_markdown(report), encoding="utf-8", newline="\n")
    return {
        "report": report,
        "path": str(output_path),
    }


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {report['title']}",
        "",
        f"Status: {report['status']}",
        "",
        "## Package Range",
        "",
    ]
    lines.extend(f"- {name}: {title}" for name, title in report["package_range"].items())
    lines.extend(["", "## Completed Capabilities", ""])
    lines.extend(f"- {item}" for item in report["completed_capabilities"])
    lines.extend(["", "## Case Inventory", ""])
    lines.extend(f"- {case_id}" for case_id in report["case_inventory"])
    lines.extend(["", "## Review Routing Summary", ""])
    for key, value in report["review_routing_summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Teacher Usability Summary",
            "",
            report["teacher_usability_summary"],
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
    lines.extend(["", "## Test Commands", ""])
    lines.extend(f"- `{command}`" for command in report["test_commands"])
    lines.append("")
    return "\n".join(lines)
