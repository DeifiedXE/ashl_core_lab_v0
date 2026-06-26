"""Validate the ASHL Core R3A docs authority freeze document."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .refactor_r3_low_risk_docs_folder_plan_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    ROOT_AUTHORITY_DOCS,
    run_refactor_r3_low_risk_docs_folder_plan_minimal_check,
    validate_refactor_r3_low_risk_docs_folder_plan_minimal_record,
)


COMMAND = "run-refactor-r3a-docs-authority-freeze-minimal-check"
FLOW = "ashl_core_refactor_r3a_docs_authority_freeze_minimal_v0"
PACKAGE_ID = "PKG-ASHLCoreRefactorR3ADocsAuthorityFreeze-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b190"
BOUNDARY_INDEX_AFTER = "2026-06-09-b191"
DOC_PATH = Path("docs/ashl_core_refactor_r3a_docs_authority_freeze_v0.md")

FUTURE_MOVE_PRECONDITIONS = (
    "redirect_index_created=True",
    "old_path_lookup_rule_created=True",
    "new_path_lookup_rule_created=True",
    "README_updated=True",
    "codex_working_context_updated=True",
    "current_boundary_index_updated=True",
    "doc_consistency_tests_updated=True",
    "all_old_paths_resolvable=True",
    "all_new_paths_resolvable=True",
    "user_explicitly_approved_authority_doc_move=True",
)

SOURCE_DOC_REQUIREMENTS = {
    "r3_docs_folder_plan": (
        "docs/ashl_core_refactor_r3_low_risk_docs_folder_plan_v0.md",
        ("ASHL Core Refactor R3 Low-Risk Docs Folder Plan v0", "Root Authority Docs"),
    ),
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
    "current_boundary_index": (
        "docs/current_boundary_index.md",
        ("Boundary Index Version: 2026-06-09-b191", "R3A docs authority freeze"),
    ),
    "phase0_status": (
        "docs/phase0_status.md",
        ("Boundary Index Version: 2026-06-09-b191", "After b191, ASHL Core can validate an R3A docs authority freeze."),
    ),
    "capability_matrix": (
        "docs/phase0_capability_matrix.md",
        ("refactor r3a docs authority freeze minimal", "implemented_docs_authority_freeze"),
    ),
    "capability_inventory": (
        "docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md",
        ("Boundary Index `2026-06-09-b191`", "ASHL Core R3A docs authority freeze reports"),
    ),
    "working_context": (
        "docs/codex_working_context_summary.md",
        ("2026-06-09-b191", "ASHL Core R3A docs authority freeze"),
    ),
    "research_plan": (
        "docs/research_plan.md",
        ("ASHL Core Refactor R3A Docs Authority Freeze Minimal v0", "Root authority docs are frozen before future docs movement."),
    ),
}

NON_MOVEMENT_FIELDS = (
    "docs_moved",
    "docs_deleted",
    "docs_renamed",
    "docs_archived",
    "docs_lines_created",
    "archive_created",
    "path_references_changed",
    "python_imports_changed",
    "runtime_behavior_changed",
)

REQUIRED_SCHEMA_KEYS = {
    "command",
    "flow",
    "status",
    "package_id",
    "boundary",
    "source_r3_docs_folder_plan",
    "source_doc_readback",
    "r3a_authority_freeze_created",
    "r3_source_plan_read",
    "frozen_root_authority_docs_listed",
    "frozen_root_authority_doc_count",
    "all_required_authority_docs_present",
    "future_move_preconditions_listed",
    "redirect_required_before_move",
    "user_explicit_approval_required_before_authority_doc_move",
    "docs_moved",
    "docs_deleted",
    "docs_renamed",
    "docs_archived",
    "docs_lines_created",
    "archive_created",
    "path_references_changed",
    "python_imports_changed",
    "runtime_behavior_changed",
    "frozen_root_authority_doc_checks",
    "future_move_precondition_checks",
    "freeze_rule",
    "non_movement_statement",
    "cli_visible_summary",
    "human_summary",
}


def _read_doc(path: Path = DOC_PATH) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def build_refactor_r3a_docs_authority_freeze_minimal_record(
    doc_text: str | None = None,
) -> dict[str, Any]:
    source = run_refactor_r3_low_risk_docs_folder_plan_minimal_check()
    source_validation = validate_refactor_r3_low_risk_docs_folder_plan_minimal_record(source)
    if not source_validation["valid"]:
        raise ValueError("source_r3_docs_folder_plan_invalid")

    text = _read_doc() if doc_text is None else doc_text
    source_readback = _source_doc_readback()
    authority_doc_checks = _authority_doc_checks(text)
    precondition_checks = {item: item in text for item in FUTURE_MOVE_PRECONDITIONS}
    non_movement = {field: f"{field}=False" in text for field in NON_MOVEMENT_FIELDS}

    r3a_created = "ASHL Core Refactor R3A Docs Authority Freeze v0" in text
    r3_source_plan_read = source_readback["all_required_sources_read"] and source_readback["all_required_terms_found"]
    frozen_docs_listed = all(authority_doc_checks.values())
    required_docs_present = all(Path(path).exists() for path in ROOT_AUTHORITY_DOCS)
    preconditions_listed = all(precondition_checks.values())
    redirect_required = precondition_checks["redirect_index_created=True"]
    explicit_approval_required = precondition_checks["user_explicitly_approved_authority_doc_move=True"]
    freeze_rule = "root authority docs stay in docs/ root until a future explicit redirect/index package exists." in text
    non_movement_statement = all(non_movement.values())

    status = "ok" if all(
        (
            r3a_created,
            r3_source_plan_read,
            frozen_docs_listed,
            len(ROOT_AUTHORITY_DOCS) == 8,
            required_docs_present,
            preconditions_listed,
            redirect_required,
            explicit_approval_required,
            freeze_rule,
            non_movement_statement,
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
            "boundary_reason": "Adds a docs authority freeze validation boundary for future refactor work.",
            "runtime_capability_change": False,
            "b10_boundary_self_check_triggered": False,
            "b_counter": "B1/10",
        },
        "source_r3_docs_folder_plan": {
            "source_boundary_index": SOURCE_BOUNDARY_INDEX,
            "source_validated": True,
            "r3_docs_folder_plan_created": source.get("r3_docs_folder_plan_created") is True,
            "root_authority_docs_listed": source.get("root_authority_docs_listed") is True,
            "docs_moved": source.get("docs_moved") is True,
            "runtime_behavior_changed": source.get("runtime_behavior_changed") is True,
        },
        "source_doc_readback": source_readback,
        "r3a_authority_freeze_created": r3a_created,
        "r3_source_plan_read": r3_source_plan_read,
        "frozen_root_authority_docs_listed": frozen_docs_listed,
        "frozen_root_authority_doc_count": len(ROOT_AUTHORITY_DOCS),
        "all_required_authority_docs_present": required_docs_present,
        "future_move_preconditions_listed": preconditions_listed,
        "redirect_required_before_move": redirect_required,
        "user_explicit_approval_required_before_authority_doc_move": explicit_approval_required,
        "docs_moved": False,
        "docs_deleted": False,
        "docs_renamed": False,
        "docs_archived": False,
        "docs_lines_created": False,
        "archive_created": False,
        "path_references_changed": False,
        "python_imports_changed": False,
        "runtime_behavior_changed": False,
        "frozen_root_authority_doc_checks": authority_doc_checks,
        "future_move_precondition_checks": precondition_checks,
        "freeze_rule": {
            "root_authority_docs_stay_in_docs_root": freeze_rule,
            "future_explicit_redirect_index_package_required": redirect_required,
            "user_explicit_approval_required": explicit_approval_required,
        },
        "non_movement_statement": non_movement,
        "cli_visible_summary": [
            f"r3a_authority_freeze_created={r3a_created}",
            f"frozen_root_authority_doc_count={len(ROOT_AUTHORITY_DOCS)}",
            f"redirect_required_before_move={redirect_required}",
            "docs_moved=False",
            "docs_deleted=False",
            "docs_renamed=False",
            "runtime_behavior_changed=False",
        ],
        "human_summary": {
            "what_was_built": "A read-only R3A freeze rule for root authority docs.",
            "what_error_it_prevents": "It prevents future documentation cleanup from moving current status, capability, boundary, and plan entry points before redirect/index rules exist.",
            "what_did_not_change": "No docs were moved, deleted, renamed, archived, redirected, or reorganized; no imports or runtime behavior changed.",
            "plain_result": "The main docs stay pinned in place until a later explicit move plan exists.",
        },
    }


def validate_refactor_r3a_docs_authority_freeze_minimal_record(
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
        "r3a_authority_freeze_created": True,
        "r3_source_plan_read": True,
        "frozen_root_authority_docs_listed": True,
        "frozen_root_authority_doc_count": 8,
        "all_required_authority_docs_present": True,
        "future_move_preconditions_listed": True,
        "redirect_required_before_move": True,
        "user_explicit_approval_required_before_authority_doc_move": True,
        "docs_moved": False,
        "docs_deleted": False,
        "docs_renamed": False,
        "docs_archived": False,
        "docs_lines_created": False,
        "archive_created": False,
        "path_references_changed": False,
        "python_imports_changed": False,
        "runtime_behavior_changed": False,
    }
    for field, expected in expected_values.items():
        if record.get(field) != expected:
            errors.append(f"{field}_wrong")

    boundary = record.get("boundary", {})
    if boundary.get("boundary_index_version_before") != BOUNDARY_INDEX_BEFORE:
        errors.append("boundary_before_wrong")
    if boundary.get("boundary_index_version_after") != BOUNDARY_INDEX_AFTER:
        errors.append("boundary_after_wrong")
    if boundary.get("boundary_reason") != "Adds a docs authority freeze validation boundary for future refactor work.":
        errors.append("boundary_reason_wrong")
    if boundary.get("runtime_capability_change") is not False:
        errors.append("boundary_runtime_capability_change_wrong")
    if boundary.get("b10_boundary_self_check_triggered") is not False:
        errors.append("boundary_b10_trigger_wrong")
    if boundary.get("b_counter") != "B1/10":
        errors.append("boundary_b_counter_wrong")

    source = record.get("source_r3_docs_folder_plan", {})
    if source.get("source_validated") is not True:
        errors.append("source_not_validated")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_wrong")
    if source.get("r3_docs_folder_plan_created") is not True:
        errors.append("source_r3_plan_missing")
    if source.get("root_authority_docs_listed") is not True:
        errors.append("source_root_authority_docs_missing")
    if source.get("docs_moved") is not False:
        errors.append("source_docs_moved_wrong")
    if source.get("runtime_behavior_changed") is not False:
        errors.append("source_runtime_behavior_changed_wrong")

    source_readback = record.get("source_doc_readback", {})
    if source_readback.get("all_required_sources_read") is not True:
        errors.append("source_docs_not_read")
    if source_readback.get("all_required_terms_found") is not True:
        errors.append("source_doc_terms_missing")
    if source_readback.get("required_source_count") != len(SOURCE_DOC_REQUIREMENTS):
        errors.append("source_required_source_count_wrong")

    authority_docs = record.get("frozen_root_authority_doc_checks", {})
    if not isinstance(authority_docs, dict) or set(authority_docs) != set(ROOT_AUTHORITY_DOCS):
        errors.append("authority_doc_checks_keys_wrong")
    elif not all(authority_docs.values()):
        errors.append("authority_doc_checks_wrong")

    preconditions = record.get("future_move_precondition_checks", {})
    if not isinstance(preconditions, dict) or set(preconditions) != set(FUTURE_MOVE_PRECONDITIONS):
        errors.append("future_move_precondition_keys_wrong")
    elif not all(preconditions.values()):
        errors.append("future_move_preconditions_wrong")

    freeze_rule = record.get("freeze_rule", {})
    for field in (
        "root_authority_docs_stay_in_docs_root",
        "future_explicit_redirect_index_package_required",
        "user_explicit_approval_required",
    ):
        if freeze_rule.get(field) is not True:
            errors.append(f"freeze_rule_{field}_wrong")

    non_movement = record.get("non_movement_statement", {})
    if not isinstance(non_movement, dict) or set(non_movement) != set(NON_MOVEMENT_FIELDS):
        errors.append("non_movement_statement_keys_wrong")
    elif not all(non_movement.values()):
        errors.append("non_movement_statement_wrong")

    if not record.get("human_summary", {}).get("what_error_it_prevents"):
        errors.append("human_summary_error_prevention_empty")

    return {
        "valid": not errors,
        "error_codes": errors,
        "r3a_authority_freeze_created": record.get("r3a_authority_freeze_created") is True,
        "r3_source_plan_read": record.get("r3_source_plan_read") is True,
        "frozen_root_authority_docs_listed": record.get("frozen_root_authority_docs_listed") is True,
        "frozen_root_authority_doc_count": record.get("frozen_root_authority_doc_count"),
        "all_required_authority_docs_present": record.get("all_required_authority_docs_present") is True,
        "future_move_preconditions_listed": record.get("future_move_preconditions_listed") is True,
        "redirect_required_before_move": record.get("redirect_required_before_move") is True,
        "user_explicit_approval_required_before_authority_doc_move": (
            record.get("user_explicit_approval_required_before_authority_doc_move") is True
        ),
        "docs_moved": record.get("docs_moved") is True,
        "docs_deleted": record.get("docs_deleted") is True,
        "docs_renamed": record.get("docs_renamed") is True,
        "docs_archived": record.get("docs_archived") is True,
        "docs_lines_created": record.get("docs_lines_created") is True,
        "archive_created": record.get("archive_created") is True,
        "path_references_changed": record.get("path_references_changed") is True,
        "python_imports_changed": record.get("python_imports_changed") is True,
        "runtime_behavior_changed": record.get("runtime_behavior_changed") is True,
    }


def _authority_doc_checks(text: str) -> dict[str, bool]:
    return {doc: doc in text and Path(doc).exists() for doc in ROOT_AUTHORITY_DOCS}


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


def run_refactor_r3a_docs_authority_freeze_minimal_check() -> dict[str, Any]:
    record = build_refactor_r3a_docs_authority_freeze_minimal_record()
    validation = validate_refactor_r3a_docs_authority_freeze_minimal_record(record)
    record["status"] = "ok" if validation["valid"] else "failed"
    return record
