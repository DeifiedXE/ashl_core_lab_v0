"""Validate the ASHL Core R3 low-risk docs folder plan document."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .refactor_r2_compatibility_alias_plan_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    run_refactor_r2_compatibility_alias_plan_minimal_check,
    validate_refactor_r2_compatibility_alias_plan_minimal_record,
)


COMMAND = "run-refactor-r3-low-risk-docs-folder-plan-minimal-check"
FLOW = "ashl_core_refactor_r3_low_risk_docs_folder_plan_minimal_v0"
PACKAGE_ID = "PKG-ASHLCoreRefactorR3LowRiskDocsFolderPlan-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b189"
BOUNDARY_INDEX_AFTER = "2026-06-09-b190"
DOC_PATH = Path("docs/ashl_core_refactor_r3_low_risk_docs_folder_plan_v0.md")

SOURCE_DOC_REQUIREMENTS = {
    "structural_refactor_map": (
        "docs/ashl_core_structural_refactor_map_v0.md",
        ("ASHL Core Structural Refactor Map v0", "Nine-Line Current Map"),
    ),
    "r2_compatibility_alias_plan": (
        "docs/ashl_core_refactor_r2_compatibility_alias_plan_v0.md",
        ("ASHL Core Refactor R2 Compatibility Alias Plan v0", "R3 low-risk docs folder plan"),
    ),
    "line_document_index": (
        "docs/phase0_line_document_index.md",
        ("ASHL Core Phase0 Line Document Index", "Governance / Audit / Planning Line"),
    ),
    "capability_inventory": (
        "docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md",
        ("Boundary Index `2026-06-09-b190`", "ASHL Core R3 low-risk docs folder plan reports"),
    ),
    "phase0_status": (
        "docs/phase0_status.md",
        ("Boundary Index Version: 2026-06-09-b190", "After b190, ASHL Core can validate an R3 low-risk docs folder plan."),
    ),
    "capability_matrix": (
        "docs/phase0_capability_matrix.md",
        ("refactor r3 low-risk docs folder plan minimal", "implemented_docs_folder_planning_map"),
    ),
    "current_boundary_index": (
        "docs/current_boundary_index.md",
        ("Boundary Index Version: 2026-06-09-b190", "B0/10 self-check"),
    ),
    "working_context": (
        "docs/codex_working_context_summary.md",
        ("2026-06-09-b190", "ASHL Core R3 low-risk docs folder plan"),
    ),
}

ROOT_AUTHORITY_DOCS = (
    "docs/current_boundary_index.md",
    "docs/phase0_status.md",
    "docs/phase0_capability_matrix.md",
    "docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md",
    "docs/codex_working_context_summary.md",
    "docs/research_plan.md",
    "docs/phase0_line_document_index.md",
    "docs/phase1_to_phase5_growth_substrate_plan.md",
)

DOC_LINES = (
    "spine",
    "body",
    "thought",
    "memory",
    "perception",
    "bridge",
    "endocrine",
    "voice",
    "lesson",
    "governance",
)

FUTURE_DOC_FOLDERS = (
    "docs/authority/",
    "docs/lines/spine/",
    "docs/lines/body/",
    "docs/lines/thought/",
    "docs/lines/memory/",
    "docs/lines/perception/",
    "docs/lines/bridge/",
    "docs/lines/endocrine/",
    "docs/lines/voice/",
    "docs/lines/lesson/",
    "docs/lines/governance/",
    "docs/archive/boundary_index/",
    "docs/archive/milestone_logs/",
    "docs/archive/historical_progress/",
    "docs/archive/superseded_designs/",
    "docs/planning/",
    "docs/audits/",
)

ARCHIVE_CANDIDATE_TYPES = (
    "old boundary index snapshots",
    "milestone logs",
    "progress logs",
    "historical status compression docs",
    "superseded planning docs",
    "stale readiness checklists",
)

DESIGN_ONLY_DOC_TYPES = (
    "retina decoder design",
    "focus selector design",
    "mimetic endocrine system design",
    "Qingyin Bridge dual-eye design",
    "voice/audio/cochlea/vocal-organ design",
    "thought layering design",
    "memory framework design",
)

B10_SELF_CHECK_TERMS = (
    "report keys only from parsed runtime/checker output",
    "verified facts separated from assumptions",
    "exact key echo for boundary / records / observed results",
    "no repo mutation beyond this package",
    "no claim that planned folder movement already happened",
    "no claim that docs were moved",
    "no claim that imports changed",
    "no claim that runtime behavior changed",
)

BOUNDARY_AUDIT_TERMS = (
    "no production behavior",
    "no runtime behavior leak",
    "no memory write / retention write",
    "no predictor read / influence / mutation",
    "no direct endocrine feed",
    "no direct tendency feed",
    "no proof-of-learning claim",
    "no cross-purpose feedback",
    "no raw weighted sum direct decision",
    "no affordance used as desire",
    "no tendency override purpose or affordance gate",
    "no next-layer boundary content implemented",
)

REQUIRED_SCHEMA_KEYS = {
    "command",
    "flow",
    "status",
    "package_id",
    "boundary",
    "source_r2_alias_plan",
    "source_doc_readback",
    "r3_docs_folder_plan_created",
    "source_docs_read",
    "root_authority_docs_listed",
    "nine_line_docs_candidates_listed",
    "archive_candidates_listed",
    "design_only_docs_marked",
    "needs_review_before_move_listed",
    "move_allowed_now_all_false",
    "docs_moved",
    "docs_deleted",
    "docs_renamed",
    "python_modules_touched_for_refactor",
    "imports_changed",
    "runtime_behavior_changed",
    "b10_self_check_required",
    "b10_self_check_passed",
    "boundary_audit_passed",
    "target_docs_layout",
    "root_authority_doc_checks",
    "line_doc_checks",
    "archive_candidate_checks",
    "design_only_doc_checks",
    "needs_review_before_move_checks",
    "b10_self_check",
    "boundary_audit",
    "cli_visible_summary",
    "human_summary",
}


def _read_doc(path: Path = DOC_PATH) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def build_refactor_r3_low_risk_docs_folder_plan_minimal_record(
    doc_text: str | None = None,
) -> dict[str, Any]:
    source = run_refactor_r2_compatibility_alias_plan_minimal_check()
    source_validation = validate_refactor_r2_compatibility_alias_plan_minimal_record(source)
    if not source_validation["valid"]:
        raise ValueError("source_r2_compatibility_alias_plan_invalid")

    text = _read_doc() if doc_text is None else doc_text
    source_readback = _source_doc_readback()
    target_layout = {folder: folder in text for folder in FUTURE_DOC_FOLDERS}
    root_authority = {doc: doc in text for doc in ROOT_AUTHORITY_DOCS}
    line_doc_checks = [_line_doc_check(text, line) for line in DOC_LINES]
    archive_candidates = {kind: kind in text for kind in ARCHIVE_CANDIDATE_TYPES}
    design_only = {kind: kind in text for kind in DESIGN_ONLY_DOC_TYPES}
    needs_review = _needs_review_checks(text)
    b10_required = _b_number(BOUNDARY_INDEX_AFTER) % 10 == 0
    b10_self_check = {term: term in text for term in B10_SELF_CHECK_TERMS}
    b10_passed = all(b10_self_check.values()) if b10_required else None
    boundary_audit = {term: term in text for term in BOUNDARY_AUDIT_TERMS}

    r3_docs_folder_plan_created = bool(text) and "ASHL Core Refactor R3 Low-Risk Docs Folder Plan v0" in text
    source_docs_read = source_readback["all_required_sources_read"] and source_readback["all_required_terms_found"]
    root_authority_docs_listed = all(root_authority.values())
    nine_line_docs_candidates_listed = all(check["candidate_docs_listed"] for check in line_doc_checks)
    archive_candidates_listed = all(archive_candidates.values())
    design_only_docs_marked = all(design_only.values())
    needs_review_before_move_listed = all(needs_review.values())
    move_allowed_now_all_false = all(check["move_allowed_now_false"] for check in line_doc_checks)
    boundary_audit_passed = all(boundary_audit.values())

    status = "ok" if all(
        (
            r3_docs_folder_plan_created,
            source_docs_read,
            root_authority_docs_listed,
            nine_line_docs_candidates_listed,
            archive_candidates_listed,
            design_only_docs_marked,
            needs_review_before_move_listed,
            move_allowed_now_all_false,
            b10_passed is True if b10_required else True,
            boundary_audit_passed,
        )
    ) else "failed"

    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": status,
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Adds an R3 low-risk documentation folder planning boundary before any docs move.",
            "runtime_capability_change": False,
            "b10_boundary_self_check_triggered": b10_required,
        },
        "source_r2_alias_plan": {
            "source_boundary_index": SOURCE_BOUNDARY_INDEX,
            "source_validated": True,
            "r2_alias_plan_created": source.get("r2_alias_plan_created") is True,
            "files_moved": source.get("files_moved") is True,
            "imports_changed": source.get("imports_changed") is True,
            "runtime_behavior_changed": source.get("runtime_behavior_changed") is True,
        },
        "source_doc_readback": source_readback,
        "r3_docs_folder_plan_created": r3_docs_folder_plan_created,
        "source_docs_read": source_docs_read,
        "root_authority_docs_listed": root_authority_docs_listed,
        "nine_line_docs_candidates_listed": nine_line_docs_candidates_listed,
        "archive_candidates_listed": archive_candidates_listed,
        "design_only_docs_marked": design_only_docs_marked,
        "needs_review_before_move_listed": needs_review_before_move_listed,
        "move_allowed_now_all_false": move_allowed_now_all_false,
        "docs_moved": False,
        "docs_deleted": False,
        "docs_renamed": False,
        "python_modules_touched_for_refactor": False,
        "imports_changed": False,
        "runtime_behavior_changed": False,
        "b10_self_check_required": b10_required,
        "b10_self_check_passed": b10_passed,
        "boundary_audit_passed": boundary_audit_passed,
        "target_docs_layout": target_layout,
        "root_authority_doc_checks": root_authority,
        "line_doc_checks": line_doc_checks,
        "archive_candidate_checks": archive_candidates,
        "design_only_doc_checks": design_only,
        "needs_review_before_move_checks": needs_review,
        "b10_self_check": b10_self_check,
        "boundary_audit": boundary_audit,
        "cli_visible_summary": [
            f"r3_docs_folder_plan_created={r3_docs_folder_plan_created}",
            f"root_authority_docs_listed={root_authority_docs_listed}",
            f"nine_line_docs_candidates_listed={nine_line_docs_candidates_listed}",
            f"archive_candidates_listed={archive_candidates_listed}",
            "docs_moved=False",
            "imports_changed=False",
            "runtime_behavior_changed=False",
            f"b10_self_check_required={b10_required}",
            f"b10_self_check_passed={b10_passed}",
        ],
        "human_summary": {
            "what_was_built": "A read-only R3 documentation folder plan.",
            "what_error_it_prevents": "It prevents future documentation cleanup from moving authority docs by accident or treating design docs as runtime capability.",
            "what_did_not_change": "No docs were moved, deleted, renamed, or redirected; no Python imports, modules, aliases, or runtime behavior changed.",
            "plain_result": "The filing plan exists; the files stay where they are.",
        },
    }


def validate_refactor_r3_low_risk_docs_folder_plan_minimal_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = REQUIRED_SCHEMA_KEYS - set(record)
    unexpected = set(record) - REQUIRED_SCHEMA_KEYS
    if missing:
        errors.append("missing_" + ",".join(sorted(missing)))
    if unexpected:
        errors.append("unexpected_" + ",".join(sorted(unexpected)))

    expected_values = {
        "command": COMMAND,
        "flow": FLOW,
        "package_id": PACKAGE_ID,
        "r3_docs_folder_plan_created": True,
        "source_docs_read": True,
        "root_authority_docs_listed": True,
        "nine_line_docs_candidates_listed": True,
        "archive_candidates_listed": True,
        "design_only_docs_marked": True,
        "needs_review_before_move_listed": True,
        "move_allowed_now_all_false": True,
        "docs_moved": False,
        "docs_deleted": False,
        "docs_renamed": False,
        "python_modules_touched_for_refactor": False,
        "imports_changed": False,
        "runtime_behavior_changed": False,
        "b10_self_check_required": True,
        "b10_self_check_passed": True,
        "boundary_audit_passed": True,
    }
    for field, expected in expected_values.items():
        if record.get(field) != expected:
            errors.append(f"{field}_wrong")

    boundary = record.get("boundary", {})
    if boundary.get("boundary_index_version_before") != BOUNDARY_INDEX_BEFORE:
        errors.append("boundary_before_wrong")
    if boundary.get("boundary_index_version_after") != BOUNDARY_INDEX_AFTER:
        errors.append("boundary_after_wrong")
    if boundary.get("boundary_reason") != "Adds an R3 low-risk documentation folder planning boundary before any docs move.":
        errors.append("boundary_reason_wrong")
    if boundary.get("runtime_capability_change") is not False:
        errors.append("boundary_runtime_capability_change_wrong")
    if boundary.get("b10_boundary_self_check_triggered") is not True:
        errors.append("boundary_b10_trigger_wrong")

    source = record.get("source_r2_alias_plan", {})
    if source.get("source_validated") is not True:
        errors.append("source_not_validated")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_wrong")
    if source.get("r2_alias_plan_created") is not True:
        errors.append("source_r2_alias_plan_missing")
    if source.get("files_moved") is not False:
        errors.append("source_files_moved_wrong")
    if source.get("imports_changed") is not False:
        errors.append("source_imports_changed_wrong")
    if source.get("runtime_behavior_changed") is not False:
        errors.append("source_runtime_behavior_changed_wrong")

    source_readback = record.get("source_doc_readback", {})
    if source_readback.get("all_required_sources_read") is not True:
        errors.append("source_docs_not_read")
    if source_readback.get("all_required_terms_found") is not True:
        errors.append("source_doc_terms_missing")

    layout = record.get("target_docs_layout", {})
    if not isinstance(layout, dict) or not all(layout.get(folder) is True for folder in FUTURE_DOC_FOLDERS):
        errors.append("target_docs_layout_wrong")

    root_docs = record.get("root_authority_doc_checks", {})
    if not isinstance(root_docs, dict) or not all(root_docs.get(doc) is True for doc in ROOT_AUTHORITY_DOCS):
        errors.append("root_authority_docs_wrong")

    line_checks = record.get("line_doc_checks", [])
    if not isinstance(line_checks, list) or len(line_checks) != len(DOC_LINES):
        errors.append("line_doc_checks_wrong_count")
    else:
        for check in line_checks:
            for field in (
                "future_docs_folder_present",
                "candidate_docs_listed",
                "keep_in_root_docs_listed",
                "archive_candidates_listed",
                "needs_review_before_move_listed",
                "reason_present",
                "move_allowed_now_false",
            ):
                if check.get(field) is not True:
                    errors.append(f"{check.get('line_name')}_{field}_wrong")

    for field in (
        "archive_candidate_checks",
        "design_only_doc_checks",
        "needs_review_before_move_checks",
        "b10_self_check",
        "boundary_audit",
    ):
        checks = record.get(field, {})
        if not isinstance(checks, dict) or not checks or not all(checks.values()):
            errors.append(f"{field}_wrong")

    if not record.get("human_summary", {}).get("what_error_it_prevents"):
        errors.append("human_summary_error_prevention_empty")

    return {
        "valid": not errors,
        "error_codes": errors,
        "r3_docs_folder_plan_created": record.get("r3_docs_folder_plan_created") is True,
        "source_docs_read": record.get("source_docs_read") is True,
        "root_authority_docs_listed": record.get("root_authority_docs_listed") is True,
        "nine_line_docs_candidates_listed": record.get("nine_line_docs_candidates_listed") is True,
        "archive_candidates_listed": record.get("archive_candidates_listed") is True,
        "design_only_docs_marked": record.get("design_only_docs_marked") is True,
        "needs_review_before_move_listed": record.get("needs_review_before_move_listed") is True,
        "move_allowed_now_all_false": record.get("move_allowed_now_all_false") is True,
        "docs_moved": record.get("docs_moved") is True,
        "docs_deleted": record.get("docs_deleted") is True,
        "docs_renamed": record.get("docs_renamed") is True,
        "python_modules_touched_for_refactor": record.get("python_modules_touched_for_refactor") is True,
        "imports_changed": record.get("imports_changed") is True,
        "runtime_behavior_changed": record.get("runtime_behavior_changed") is True,
        "b10_self_check_required": record.get("b10_self_check_required") is True,
        "b10_self_check_passed": record.get("b10_self_check_passed") is True,
        "boundary_audit_passed": record.get("boundary_audit_passed") is True,
    }


def _source_doc_readback() -> dict[str, Any]:
    docs = []
    for source_id, (path_text, required_terms) in SOURCE_DOC_REQUIREMENTS.items():
        path = Path(path_text)
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        term_checks = {term: term in text for term in required_terms}
        docs.append(
            {
                "source_id": source_id,
                "path": path_text,
                "read": path.exists(),
                "required_terms_found": term_checks,
                "supports_current_claim": path.exists() and all(term_checks.values()),
            }
        )
    return {
        "source_documents": docs,
        "required_source_count": len(SOURCE_DOC_REQUIREMENTS),
        "all_required_sources_read": all(doc["read"] for doc in docs),
        "all_required_terms_found": all(doc["supports_current_claim"] for doc in docs),
    }


def _line_doc_check(text: str, line_name: str) -> dict[str, Any]:
    section = _section_for_line(text, line_name)
    return {
        "line_name": line_name,
        "future_docs_folder_present": f"docs/lines/{line_name}/" in section,
        "candidate_docs_listed": "Candidate docs:" in section and _bullet_count(section, "Candidate docs:") >= 2,
        "keep_in_root_docs_listed": "Keep in root docs:" in section,
        "archive_candidates_listed": "Archive candidates:" in section,
        "needs_review_before_move_listed": "Needs review before move:" in section,
        "reason_present": "Reason:" in section,
        "move_allowed_now_false": "move_allowed_now=false" in section,
    }


def _section_for_line(text: str, line_name: str) -> str:
    marker = f"### {line_name}"
    start = text.find(marker)
    if start < 0:
        return ""
    next_start = text.find("\n### ", start + len(marker))
    if next_start < 0:
        next_start = text.find("\n## ", start + len(marker))
    if next_start < 0:
        return text[start:]
    return text[start:next_start]


def _bullet_count(section: str, label: str) -> int:
    start = section.find(label)
    if start < 0:
        return 0
    next_label = section.find("\n\n", start + len(label))
    block = section[start:next_label] if next_label >= 0 else section[start:]
    return sum(1 for line in block.splitlines() if line.strip().startswith("- "))


def _needs_review_checks(text: str) -> dict[str, bool]:
    terms = (
        "root authority docs",
        "docs referenced by `docs/current_boundary_index.md`",
        "docs referenced by `docs/codex_working_context_summary.md`",
        "docs referenced by `README.md`",
        "docs referenced by `run_all_smoke_tests.py`",
        "docs referenced by targeted unit tests",
    )
    return {term: term in text for term in terms}


def _b_number(boundary_index: str) -> int:
    return int(boundary_index.rsplit("b", 1)[1])


def run_refactor_r3_low_risk_docs_folder_plan_minimal_check() -> dict[str, Any]:
    record = build_refactor_r3_low_risk_docs_folder_plan_minimal_record()
    validation = validate_refactor_r3_low_risk_docs_folder_plan_minimal_record(record)
    record["status"] = "ok" if validation["valid"] else "failed"
    return record
