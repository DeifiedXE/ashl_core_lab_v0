"""Validate the ASHL Core R4 first tiny docs move redirect-index plan."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .refactor_r3a_docs_authority_freeze_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    ROOT_AUTHORITY_DOCS,
    run_refactor_r3a_docs_authority_freeze_minimal_check,
    validate_refactor_r3a_docs_authority_freeze_minimal_record,
)


COMMAND = "run-refactor-r4-first-tiny-docs-move-redirect-index-plan-minimal-check"
FLOW = "ashl_core_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_v0"
PACKAGE_ID = "PKG-ASHLCoreRefactorR4FirstTinyDocsMoveRedirectIndexPlan-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b191"
BOUNDARY_INDEX_AFTER = "2026-06-09-b192"
DOC_PATH = Path("docs/ashl_core_refactor_r4_first_tiny_docs_move_redirect_index_plan_v0.md")

PREFERRED_CANDIDATE_OLD_PATH = "docs/milestone_logs/mimetic_endocrine_line_milestone_2026-06-09.md"
PREFERRED_CANDIDATE_NEW_PATH = "docs/archive/milestone_logs/mimetic_endocrine_line_milestone_2026-06-09.md"
FALLBACK_MILESTONE_CANDIDATES = (
    "docs/milestone_logs/experience_abstraction_layer_milestone_2026-06-09.md",
    "docs/milestone_logs/generalized_memory_line_milestone_2026-06-09.md",
    "docs/milestone_logs/instinct_reward_line_milestone_2026-06-09.md",
    "docs/milestone_logs/integrated_experience_session_trace_milestone_2026-06-09.md",
)

FUTURE_MOVE_PRECONDITIONS = (
    "selected_candidate_exists=True",
    "selected_candidate_not_root_authority=True",
    "selected_candidate_is_historical_or_archive_candidate=True",
    "redirect_index_entry_created=True",
    "old_path_lookup_rule_created=True",
    "new_path_lookup_rule_created=True",
    "doc_consistency_tests_updated=True",
    "README_updated_if_referenced=True",
    "codex_working_context_updated_if_referenced=True",
    "current_boundary_index_updated_if_referenced=True",
    "all_old_paths_resolvable=True",
    "all_new_paths_resolvable=True",
    "git_diff_check_passed=True",
    "targeted_tests_passed=True",
    "smoke_passed=True",
)

SOURCE_DOC_REQUIREMENTS = {
    "structural_refactor_map": (
        "docs/ashl_core_structural_refactor_map_v0.md",
        ("ASHL Core Structural Refactor Map v0", "Historical or archive candidates"),
    ),
    "r2_compatibility_alias_plan": (
        "docs/ashl_core_refactor_r2_compatibility_alias_plan_v0.md",
        ("ASHL Core Refactor R2 Compatibility Alias Plan v0", "R3 low-risk docs folder plan"),
    ),
    "r3_docs_folder_plan": (
        "docs/ashl_core_refactor_r3_low_risk_docs_folder_plan_v0.md",
        ("ASHL Core Refactor R3 Low-Risk Docs Folder Plan v0", "milestone logs"),
    ),
    "r3a_authority_freeze": (
        "docs/ashl_core_refactor_r3a_docs_authority_freeze_v0.md",
        ("ASHL Core Refactor R3A Docs Authority Freeze v0", "Frozen Root Authority Docs"),
    ),
    "current_boundary_index": (
        "docs/current_boundary_index.md",
        ("Boundary Index Version: 2026-06-09-b192", "R4 first tiny docs move redirect-index plan"),
    ),
    "phase0_status": (
        "docs/phase0_status.md",
        ("Boundary Index Version: 2026-06-09-b192", "After b192, ASHL Core can validate an R4 first tiny docs move redirect-index plan."),
    ),
    "capability_matrix": (
        "docs/phase0_capability_matrix.md",
        ("refactor r4 first tiny docs move redirect-index plan minimal", "implemented_first_tiny_docs_move_plan"),
    ),
    "capability_inventory": (
        "docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md",
        ("Boundary Index `2026-06-09-b192`", "ASHL Core R4 first tiny docs move redirect-index plan reports"),
    ),
    "working_context": (
        "docs/codex_working_context_summary.md",
        ("2026-06-09-b192", "ASHL Core R4 first tiny docs move redirect-index plan"),
    ),
    "line_document_index": (
        "docs/phase0_line_document_index.md",
        ("ASHL Core Phase0 Line Document Index", "Governance / Audit / Planning Line"),
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
    "source_r3a_authority_freeze",
    "source_doc_readback",
    "r4_tiny_docs_move_plan_created",
    "source_plans_read",
    "selected_candidate_old_path",
    "planned_candidate_new_path",
    "selected_candidate_exists",
    "fallback_candidate_used",
    "fallback_reason",
    "selected_candidate_not_root_authority",
    "selected_candidate_is_historical_or_archive_candidate",
    "root_authority_candidate_selected",
    "frozen_authority_docs_protected",
    "redirect_index_plan_created",
    "future_move_preconditions_listed",
    "docs_moved",
    "docs_deleted",
    "docs_renamed",
    "docs_archived",
    "docs_lines_created",
    "archive_created",
    "path_references_changed",
    "python_imports_changed",
    "runtime_behavior_changed",
    "frozen_authority_doc_checks",
    "redirect_index_plan",
    "future_move_precondition_checks",
    "non_movement_statement",
    "cli_visible_summary",
    "human_summary",
}


def _read_doc(path: Path = DOC_PATH) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def build_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_record(
    doc_text: str | None = None,
) -> dict[str, Any]:
    source = run_refactor_r3a_docs_authority_freeze_minimal_check()
    source_validation = validate_refactor_r3a_docs_authority_freeze_minimal_record(source)
    if not source_validation["valid"]:
        raise ValueError("source_r3a_docs_authority_freeze_invalid")

    text = _read_doc() if doc_text is None else doc_text
    source_readback = _source_doc_readback()
    candidate = _select_candidate()
    old_path = candidate["old_path"]
    new_path = candidate["new_path"]
    frozen_checks = {doc: doc in text and Path(doc).exists() for doc in ROOT_AUTHORITY_DOCS}
    precondition_checks = {item: item in text for item in FUTURE_MOVE_PRECONDITIONS}
    non_movement = {field: f"{field}=False" in text for field in NON_MOVEMENT_FIELDS}
    redirect_plan = _redirect_index_plan(text, old_path, new_path)

    plan_created = "ASHL Core Refactor R4 First Tiny Docs Move Redirect Index Plan v0" in text
    source_plans_read = source_readback["all_required_sources_read"] and source_readback["all_required_terms_found"]
    selected_exists = Path(old_path).exists()
    not_root_authority = old_path not in ROOT_AUTHORITY_DOCS
    historical_candidate = _is_historical_or_archive_candidate(old_path)
    root_authority_selected = old_path in ROOT_AUTHORITY_DOCS
    frozen_protected = all(frozen_checks.values()) and not root_authority_selected
    redirect_created = all(redirect_plan.values())
    preconditions_listed = all(precondition_checks.values())
    non_movement_statement = all(non_movement.values())

    status = "ok" if all(
        (
            plan_created,
            source_plans_read,
            selected_exists,
            not_root_authority,
            historical_candidate,
            not root_authority_selected,
            frozen_protected,
            redirect_created,
            preconditions_listed,
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
            "boundary_reason": "Adds the first tiny docs move redirect-index planning validation boundary.",
            "runtime_capability_change": False,
            "b10_boundary_self_check_triggered": False,
            "b_counter": "B2/10",
        },
        "source_r3a_authority_freeze": {
            "source_boundary_index": SOURCE_BOUNDARY_INDEX,
            "source_validated": True,
            "r3a_authority_freeze_created": source.get("r3a_authority_freeze_created") is True,
            "frozen_root_authority_doc_count": source.get("frozen_root_authority_doc_count"),
            "frozen_authority_docs_protected": source.get("frozen_root_authority_docs_listed") is True,
            "docs_moved": source.get("docs_moved") is True,
            "runtime_behavior_changed": source.get("runtime_behavior_changed") is True,
        },
        "source_doc_readback": source_readback,
        "r4_tiny_docs_move_plan_created": plan_created,
        "source_plans_read": source_plans_read,
        "selected_candidate_old_path": old_path,
        "planned_candidate_new_path": new_path,
        "selected_candidate_exists": selected_exists,
        "fallback_candidate_used": candidate["fallback_candidate_used"],
        "fallback_reason": candidate["fallback_reason"],
        "selected_candidate_not_root_authority": not_root_authority,
        "selected_candidate_is_historical_or_archive_candidate": historical_candidate,
        "root_authority_candidate_selected": root_authority_selected,
        "frozen_authority_docs_protected": frozen_protected,
        "redirect_index_plan_created": redirect_created,
        "future_move_preconditions_listed": preconditions_listed,
        "docs_moved": False,
        "docs_deleted": False,
        "docs_renamed": False,
        "docs_archived": False,
        "docs_lines_created": False,
        "archive_created": False,
        "path_references_changed": False,
        "python_imports_changed": False,
        "runtime_behavior_changed": False,
        "frozen_authority_doc_checks": frozen_checks,
        "redirect_index_plan": redirect_plan,
        "future_move_precondition_checks": precondition_checks,
        "non_movement_statement": non_movement,
        "cli_visible_summary": [
            f"r4_tiny_docs_move_plan_created={plan_created}",
            f"selected_candidate_not_root_authority={not_root_authority}",
            f"redirect_index_plan_created={redirect_created}",
            f"future_move_preconditions_listed={preconditions_listed}",
            "docs_moved=False",
            "path_references_changed=False",
            "runtime_behavior_changed=False",
        ],
        "human_summary": {
            "what_was_built": "A read-only R4 plan for one future low-risk docs move.",
            "what_error_it_prevents": "It prevents the first docs move from losing old-path lookup or accidentally touching frozen root authority docs.",
            "what_did_not_change": "No docs were moved, archived, deleted, renamed, redirected, or reorganized; no imports or runtime behavior changed.",
            "plain_result": "One historical milestone log has a planned future archive path, but the file stays where it is.",
        },
    }


def validate_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_record(
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
        "r4_tiny_docs_move_plan_created": True,
        "source_plans_read": True,
        "selected_candidate_exists": True,
        "selected_candidate_not_root_authority": True,
        "selected_candidate_is_historical_or_archive_candidate": True,
        "root_authority_candidate_selected": False,
        "frozen_authority_docs_protected": True,
        "redirect_index_plan_created": True,
        "future_move_preconditions_listed": True,
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

    old_path = record.get("selected_candidate_old_path")
    new_path = record.get("planned_candidate_new_path")
    if old_path in ROOT_AUTHORITY_DOCS:
        errors.append("selected_candidate_is_root_authority")
    if not isinstance(old_path, str) or not old_path.startswith("docs/milestone_logs/"):
        errors.append("selected_candidate_old_path_wrong")
    if not isinstance(new_path, str) or not (
        new_path.startswith("docs/archive/") or new_path.startswith("docs/lines/")
    ):
        errors.append("planned_candidate_new_path_wrong")

    boundary = record.get("boundary", {})
    if boundary.get("boundary_index_version_before") != BOUNDARY_INDEX_BEFORE:
        errors.append("boundary_before_wrong")
    if boundary.get("boundary_index_version_after") != BOUNDARY_INDEX_AFTER:
        errors.append("boundary_after_wrong")
    if boundary.get("boundary_reason") != "Adds the first tiny docs move redirect-index planning validation boundary.":
        errors.append("boundary_reason_wrong")
    if boundary.get("runtime_capability_change") is not False:
        errors.append("boundary_runtime_capability_change_wrong")
    if boundary.get("b10_boundary_self_check_triggered") is not False:
        errors.append("boundary_b10_trigger_wrong")
    if boundary.get("b_counter") != "B2/10":
        errors.append("boundary_b_counter_wrong")

    source = record.get("source_r3a_authority_freeze", {})
    if source.get("source_validated") is not True:
        errors.append("source_not_validated")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_wrong")
    if source.get("r3a_authority_freeze_created") is not True:
        errors.append("source_r3a_freeze_missing")
    if source.get("frozen_root_authority_doc_count") != 8:
        errors.append("source_frozen_doc_count_wrong")
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

    frozen_checks = record.get("frozen_authority_doc_checks", {})
    if not isinstance(frozen_checks, dict) or set(frozen_checks) != set(ROOT_AUTHORITY_DOCS):
        errors.append("frozen_authority_doc_checks_keys_wrong")
    elif not all(frozen_checks.values()):
        errors.append("frozen_authority_doc_checks_wrong")

    redirect_plan = record.get("redirect_index_plan", {})
    if not isinstance(redirect_plan, dict) or not redirect_plan or not all(redirect_plan.values()):
        errors.append("redirect_index_plan_wrong")

    preconditions = record.get("future_move_precondition_checks", {})
    if not isinstance(preconditions, dict) or set(preconditions) != set(FUTURE_MOVE_PRECONDITIONS):
        errors.append("future_move_precondition_keys_wrong")
    elif not all(preconditions.values()):
        errors.append("future_move_preconditions_wrong")

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
        "r4_tiny_docs_move_plan_created": record.get("r4_tiny_docs_move_plan_created") is True,
        "source_plans_read": record.get("source_plans_read") is True,
        "selected_candidate_old_path": old_path,
        "planned_candidate_new_path": new_path,
        "selected_candidate_exists": record.get("selected_candidate_exists") is True,
        "fallback_candidate_used": record.get("fallback_candidate_used") is True,
        "selected_candidate_not_root_authority": record.get("selected_candidate_not_root_authority") is True,
        "selected_candidate_is_historical_or_archive_candidate": (
            record.get("selected_candidate_is_historical_or_archive_candidate") is True
        ),
        "root_authority_candidate_selected": record.get("root_authority_candidate_selected") is True,
        "frozen_authority_docs_protected": record.get("frozen_authority_docs_protected") is True,
        "redirect_index_plan_created": record.get("redirect_index_plan_created") is True,
        "future_move_preconditions_listed": record.get("future_move_preconditions_listed") is True,
        "docs_moved": record.get("docs_moved") is True,
        "docs_deleted": record.get("docs_deleted") is True,
        "docs_renamed": record.get("docs_renamed") is True,
        "docs_archived": record.get("docs_archived") is True,
        "path_references_changed": record.get("path_references_changed") is True,
        "python_imports_changed": record.get("python_imports_changed") is True,
        "runtime_behavior_changed": record.get("runtime_behavior_changed") is True,
    }


def _select_candidate() -> dict[str, Any]:
    if Path(PREFERRED_CANDIDATE_OLD_PATH).exists():
        return {
            "old_path": PREFERRED_CANDIDATE_OLD_PATH,
            "new_path": PREFERRED_CANDIDATE_NEW_PATH,
            "fallback_candidate_used": False,
            "fallback_reason": "",
        }
    for old_path in FALLBACK_MILESTONE_CANDIDATES:
        if Path(old_path).exists():
            name = Path(old_path).name
            return {
                "old_path": old_path,
                "new_path": f"docs/archive/milestone_logs/{name}",
                "fallback_candidate_used": True,
                "fallback_reason": "source_candidate_missing",
            }
    return {
        "old_path": PREFERRED_CANDIDATE_OLD_PATH,
        "new_path": PREFERRED_CANDIDATE_NEW_PATH,
        "fallback_candidate_used": True,
        "fallback_reason": "source_candidate_missing",
    }


def _is_historical_or_archive_candidate(path: str) -> bool:
    return path.startswith("docs/milestone_logs/") and path.endswith(".md")


def _redirect_index_plan(text: str, old_path: str, new_path: str) -> dict[str, bool]:
    terms = {
        "old_path": old_path,
        "new_path": new_path,
        "move_type": "docs_archive_milestone_log",
        "authority_level": "historical_context_only",
        "old_path_policy": "redirect_lookup_required",
        "new_path_policy": "canonical_after_move",
        "requires_readme_update": '"requires_readme_update": true',
        "requires_working_context_update": '"requires_working_context_update": false',
        "requires_current_boundary_update": '"requires_current_boundary_update": false',
        "requires_doc_consistency_update": '"requires_doc_consistency_update": true',
        "old_path_lookup_rule": "old path lookup rule",
        "new_path_lookup_rule": "new path lookup rule",
    }
    return {key: value in text for key, value in terms.items()}


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


def run_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_check() -> dict[str, Any]:
    record = build_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_record()
    validation = validate_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_record(record)
    record["status"] = "ok" if validation["valid"] else "failed"
    return record
