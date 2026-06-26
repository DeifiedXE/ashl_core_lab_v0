"""Validate the ASHL Core R2 compatibility alias plan document."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .structural_refactor_map_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    run_structural_refactor_map_minimal_check,
    validate_structural_refactor_map_minimal_record,
)


COMMAND = "run-refactor-r2-compatibility-alias-plan-minimal-check"
FLOW = "ashl_core_refactor_r2_compatibility_alias_plan_minimal_v0"
PACKAGE_ID = "PKG-ASHLCoreRefactorR2CompatibilityAliasPlan-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b188"
BOUNDARY_INDEX_AFTER = "2026-06-09-b189"
DOC_PATH = Path("docs/ashl_core_refactor_r2_compatibility_alias_plan_v0.md")

STRUCTURAL_LINES = (
    "action_body_motor",
    "thought_purpose",
    "memory_retention_influence",
    "vision_eye_focus",
    "qingyin_bridge_capability",
    "mimetic_endocrine_settling",
    "voice_audio_first_output",
    "lesson_review_evidence",
    "governance_audit_documentation",
)

TARGET_FOLDERS = (
    "ashl_core/spine/",
    "ashl_core/body/",
    "ashl_core/thought/",
    "ashl_core/memory/",
    "ashl_core/perception/",
    "ashl_core/bridge/",
    "ashl_core/endocrine/",
    "ashl_core/voice/",
    "ashl_core/lesson/",
    "ashl_core/governance/",
)

COMPATIBILITY_STRATEGY_TERMS = (
    "old_module_path remains importable",
    "new_module_path becomes canonical",
    "old path re-exports from new path",
    "tests first validate both paths",
    "old path deprecation happens only after compatibility passes",
)

IMPORT_TEST_PLAN_TERMS = (
    "old import still works",
    "new import works",
    "old and new expose same public function names",
    "old and new output same deterministic sample record",
    "all existing tests still pass",
    "smoke still passes",
)

PHASE_GATE_TERMS = (
    "R1 structural map completed",
    "R2 compatibility alias plan",
    "R3 low-risk docs folder plan",
    "R4 first small module move with compatibility shim",
    "R5 duplicate gate family consolidation plan",
    "R6 import/test update",
    "R7 old-path deprecation only after compatibility passes",
)

NON_MOVEMENT_TERMS = (
    "R2 must not move files.",
    "R2 must not rename modules.",
    "R2 must not change imports.",
    "R2 must not merge modules.",
    "R2 must not delete old paths.",
)

REQUIRED_TABLE_HEADERS = (
    "old_module_path",
    "future_new_module_path",
    "line",
    "alias_strategy",
    "risk_level",
    "move_allowed_now",
)

FORBIDDEN_SIDE_EFFECT_FIELDS = (
    "files_moved",
    "files_renamed",
    "imports_changed",
    "modules_merged",
    "old_paths_deleted",
    "runtime_behavior_changed",
)

REQUIRED_SCHEMA_KEYS = {
    "command",
    "flow",
    "status",
    "package_id",
    "boundary",
    "source_structural_map",
    "r2_alias_plan_created",
    "target_package_layout_present",
    "compatibility_strategy_present",
    "alias_candidate_table_present",
    "nine_lines_have_alias_candidates",
    "spine_alias_candidates_present",
    "import_compatibility_test_plan_present",
    "refactor_phase_gate_present",
    "files_moved",
    "files_renamed",
    "imports_changed",
    "modules_merged",
    "old_paths_deleted",
    "runtime_behavior_changed",
    "target_package_layout",
    "alias_candidate_counts",
    "table_header_checks",
    "compatibility_strategy_checks",
    "import_compatibility_test_plan_checks",
    "refactor_phase_gate_checks",
    "non_movement_rule_checks",
    "cli_visible_summary",
    "human_summary",
}


def _read_doc(path: Path = DOC_PATH) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def build_refactor_r2_compatibility_alias_plan_minimal_record(
    doc_text: str | None = None,
) -> dict[str, Any]:
    source = run_structural_refactor_map_minimal_check()
    source_validation = validate_structural_refactor_map_minimal_record(source)
    if not source_validation["valid"]:
        raise ValueError("source_structural_refactor_map_invalid")

    text = _read_doc() if doc_text is None else doc_text
    layout = {folder: folder in text for folder in TARGET_FOLDERS}
    table_headers = {header: header in text for header in REQUIRED_TABLE_HEADERS}
    compatibility = {term: term in text for term in COMPATIBILITY_STRATEGY_TERMS}
    import_plan = {term: term in text for term in IMPORT_TEST_PLAN_TERMS}
    phase_gate = {term: term in text for term in PHASE_GATE_TERMS}
    non_movement = {term: term in text for term in NON_MOVEMENT_TERMS}
    alias_counts = _alias_candidate_counts(text)

    r2_alias_plan_created = bool(text) and "ASHL Core Refactor R2 Compatibility Alias Plan v0" in text
    target_package_layout_present = all(layout.values())
    compatibility_strategy_present = all(compatibility.values())
    alias_candidate_table_present = "## Alias Candidate Table" in text and all(table_headers.values())
    nine_lines_have_alias_candidates = all(alias_counts.get(line, 0) >= 2 for line in STRUCTURAL_LINES)
    spine_alias_candidates_present = alias_counts.get("spine", 0) >= 2
    import_compatibility_test_plan_present = all(import_plan.values())
    refactor_phase_gate_present = all(phase_gate.values())
    non_movement_rule_present = all(non_movement.values())

    status = "ok" if all(
        (
            r2_alias_plan_created,
            target_package_layout_present,
            compatibility_strategy_present,
            alias_candidate_table_present,
            nine_lines_have_alias_candidates,
            spine_alias_candidates_present,
            import_compatibility_test_plan_present,
            refactor_phase_gate_present,
            non_movement_rule_present,
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
            "boundary_reason": "Adds an R2 compatibility alias planning boundary before future file moves.",
            "runtime_capability_change": False,
        },
        "source_structural_map": {
            "source_boundary_index": SOURCE_BOUNDARY_INDEX,
            "source_validated": True,
            "structural_refactor_map_created": source.get("structural_refactor_map_created") is True,
            "nine_lines_present": source.get("nine_lines_present") is True,
            "line_count": source.get("line_count"),
            "files_moved": source.get("files_moved") is True,
            "imports_changed": source.get("imports_changed") is True,
            "runtime_behavior_changed": source.get("runtime_behavior_changed") is True,
        },
        "r2_alias_plan_created": r2_alias_plan_created,
        "target_package_layout_present": target_package_layout_present,
        "compatibility_strategy_present": compatibility_strategy_present,
        "alias_candidate_table_present": alias_candidate_table_present,
        "nine_lines_have_alias_candidates": nine_lines_have_alias_candidates,
        "spine_alias_candidates_present": spine_alias_candidates_present,
        "import_compatibility_test_plan_present": import_compatibility_test_plan_present,
        "refactor_phase_gate_present": refactor_phase_gate_present,
        "files_moved": False,
        "files_renamed": False,
        "imports_changed": False,
        "modules_merged": False,
        "old_paths_deleted": False,
        "runtime_behavior_changed": False,
        "target_package_layout": layout,
        "alias_candidate_counts": alias_counts,
        "table_header_checks": table_headers,
        "compatibility_strategy_checks": compatibility,
        "import_compatibility_test_plan_checks": import_plan,
        "refactor_phase_gate_checks": phase_gate,
        "non_movement_rule_checks": non_movement,
        "cli_visible_summary": [
            f"r2_alias_plan_created={r2_alias_plan_created}",
            f"nine_lines_have_alias_candidates={nine_lines_have_alias_candidates}",
            "files_moved=False",
            "imports_changed=False",
            "runtime_behavior_changed=False",
        ],
        "human_summary": {
            "what_was_built": "A read-only R2 compatibility alias plan.",
            "what_error_it_prevents": "It prevents future folder refactor work from breaking old imports or duplicating modules before compatibility tests exist.",
            "what_did_not_change": "No files were moved, renamed, merged, deleted, imported from new paths, or given runtime authority.",
            "plain_result": "New homes are planned, but old doors are not touched.",
        },
    }


def validate_refactor_r2_compatibility_alias_plan_minimal_record(
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
        "r2_alias_plan_created": True,
        "target_package_layout_present": True,
        "compatibility_strategy_present": True,
        "alias_candidate_table_present": True,
        "nine_lines_have_alias_candidates": True,
        "spine_alias_candidates_present": True,
        "import_compatibility_test_plan_present": True,
        "refactor_phase_gate_present": True,
        "files_moved": False,
        "files_renamed": False,
        "imports_changed": False,
        "modules_merged": False,
        "old_paths_deleted": False,
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
    if boundary.get("boundary_reason") != "Adds an R2 compatibility alias planning boundary before future file moves.":
        errors.append("boundary_reason_wrong")
    if boundary.get("runtime_capability_change") is not False:
        errors.append("boundary_runtime_capability_change_wrong")

    source = record.get("source_structural_map", {})
    if source.get("source_validated") is not True:
        errors.append("source_not_validated")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_wrong")
    if source.get("structural_refactor_map_created") is not True:
        errors.append("source_structural_map_missing")
    if source.get("nine_lines_present") is not True or source.get("line_count") != 9:
        errors.append("source_lines_wrong")
    if source.get("files_moved") is not False:
        errors.append("source_files_moved_wrong")
    if source.get("imports_changed") is not False:
        errors.append("source_imports_changed_wrong")
    if source.get("runtime_behavior_changed") is not False:
        errors.append("source_runtime_behavior_changed_wrong")

    layout = record.get("target_package_layout", {})
    if not isinstance(layout, dict) or not all(layout.get(folder) is True for folder in TARGET_FOLDERS):
        errors.append("target_layout_wrong")

    alias_counts = record.get("alias_candidate_counts", {})
    for line in STRUCTURAL_LINES:
        if alias_counts.get(line, 0) < 2:
            errors.append(f"{line}_alias_candidate_count_low")
    if alias_counts.get("spine", 0) < 2:
        errors.append("spine_alias_candidate_count_low")

    for field in (
        "table_header_checks",
        "compatibility_strategy_checks",
        "import_compatibility_test_plan_checks",
        "refactor_phase_gate_checks",
        "non_movement_rule_checks",
    ):
        checks = record.get(field, {})
        if not isinstance(checks, dict) or not checks or not all(checks.values()):
            errors.append(f"{field}_wrong")

    if not record.get("human_summary", {}).get("what_error_it_prevents"):
        errors.append("human_summary_error_prevention_empty")

    return {
        "valid": not errors,
        "error_codes": errors,
        "r2_alias_plan_created": record.get("r2_alias_plan_created") is True,
        "target_package_layout_present": record.get("target_package_layout_present") is True,
        "compatibility_strategy_present": record.get("compatibility_strategy_present") is True,
        "alias_candidate_table_present": record.get("alias_candidate_table_present") is True,
        "nine_lines_have_alias_candidates": record.get("nine_lines_have_alias_candidates") is True,
        "spine_alias_candidates_present": record.get("spine_alias_candidates_present") is True,
        "import_compatibility_test_plan_present": record.get("import_compatibility_test_plan_present") is True,
        "refactor_phase_gate_present": record.get("refactor_phase_gate_present") is True,
        "files_moved": record.get("files_moved") is True,
        "files_renamed": record.get("files_renamed") is True,
        "imports_changed": record.get("imports_changed") is True,
        "modules_merged": record.get("modules_merged") is True,
        "old_paths_deleted": record.get("old_paths_deleted") is True,
        "runtime_behavior_changed": record.get("runtime_behavior_changed") is True,
    }


def _alias_candidate_counts(text: str) -> dict[str, int]:
    counts = {line: text.count(f"| `{line}` |") for line in STRUCTURAL_LINES}
    counts["spine"] = text.count("| `spine` |")
    return counts


def run_refactor_r2_compatibility_alias_plan_minimal_check() -> dict[str, Any]:
    record = build_refactor_r2_compatibility_alias_plan_minimal_record()
    validation = validate_refactor_r2_compatibility_alias_plan_minimal_record(record)
    record["status"] = "ok" if validation["valid"] else "failed"
    return record
