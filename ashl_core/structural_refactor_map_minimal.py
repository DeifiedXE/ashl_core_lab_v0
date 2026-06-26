"""Validate the ASHL Core structural refactor map document."""

from __future__ import annotations

from pathlib import Path
from typing import Any


COMMAND = "run-structural-refactor-map-minimal-check"
FLOW = "ashl_core_structural_refactor_map_minimal_v0"
PACKAGE_ID = "PKG-ASHLCoreStructuralRefactorMap-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b187"
BOUNDARY_INDEX_AFTER = "2026-06-09-b188"
DOC_PATH = Path("docs/ashl_core_structural_refactor_map_v0.md")

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

FUTURE_FOLDERS = (
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

COMPLETED_ANCHORS = (
    "Phase0 thought/action/memory mini-loop",
    "Phase1 session trace spine / frame / tick handoff / three-line index / closure",
    "Phase2 entry / source-link / unknown classification correction",
    "reviewed lesson memory candidate / memory write-read / retention / readback",
    "first_output / first_output_trace / mentor_feedback_trace",
    "symbolic eye / visual-spatial grounding",
    "Qingyin Bridge grounded capability map",
    "sandbox action chain",
    "endocrine-like trace / settling trace",
)

PARTIAL_ANCHORS = (
    "memory line should be integrated, not rebuilt",
    "first_output should be persisted / connected, not rebuilt",
    "symbolic eye should be connected to runtime focus, not replaced",
    "endocrine trace should become bounded context surface, not direct action authority",
)

DUPLICATE_FAMILIES = (
    "selected_action approval / selected_action minimal",
    "final_action approval / final_action minimal",
    "direct_command approval / direct_command minimal",
    "execution approval / execution minimal",
    "outcome feedback approval / outcome feedback minimal",
    "candidate reordering approval / candidate reordering minimal",
    "readback / index / closure audit packages",
)

NON_GOAL_PHRASES = (
    "No runtime behavior change.",
    "No file move.",
    "No file delete.",
    "No rename.",
    "No import path change.",
    "No module merge.",
    "No boundary expansion.",
    "No candidate input.",
    "No action selection.",
    "No execution.",
    "No memory write.",
    "No retention write.",
    "No predictor use.",
    "No endocrine feed.",
    "No production behavior.",
    "No learning or consciousness claim.",
)

REQUIRED_SCHEMA_KEYS = {
    "command",
    "flow",
    "status",
    "package_id",
    "boundary",
    "structural_refactor_map_created",
    "nine_lines_present",
    "line_count",
    "completed_do_not_rebuild_section_present",
    "partial_extend_only_section_present",
    "duplicate_merge_candidates_listed",
    "historical_archive_candidates_listed",
    "future_folder_suggestions_present",
    "runtime_behavior_changed",
    "files_moved",
    "files_deleted",
    "files_renamed",
    "imports_changed",
    "new_runtime_authority_created",
    "line_checks",
    "completed_do_not_rebuild_anchors",
    "partial_extend_only_anchors",
    "duplicate_merge_candidate_families",
    "historical_archive_candidate_summary",
    "proposed_refactor_phases",
    "future_folder_suggestions",
    "non_goals",
    "cli_visible_summary",
    "human_summary",
}


def _read_doc(path: Path = DOC_PATH) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def build_structural_refactor_map_minimal_record(doc_text: str | None = None) -> dict[str, Any]:
    text = _read_doc() if doc_text is None else doc_text
    line_checks = [_line_check(text, line_name) for line_name in STRUCTURAL_LINES]
    completed = {anchor: anchor in text for anchor in COMPLETED_ANCHORS}
    partial = {anchor: anchor in text for anchor in PARTIAL_ANCHORS}
    duplicates = {family: family in text for family in DUPLICATE_FAMILIES}
    future_folders = {folder: folder in text for folder in FUTURE_FOLDERS}
    non_goal_checks = {phrase: phrase in text for phrase in NON_GOAL_PHRASES}

    structural_refactor_map_created = bool(text) and "ASHL Core Structural Refactor Map v0" in text
    nine_lines_present = all(check["present"] for check in line_checks)
    completed_section = "## Completed Do-Not-Rebuild Anchors" in text
    partial_section = "## Partial Extend-Only Anchors" in text
    duplicate_section = "## Duplicate / Merge Candidate Families" in text and all(duplicates.values())
    historical_section = "## Historical / Archive Candidates" in text
    future_folder_suggestions = all(future_folders.values())
    non_goals_present = all(non_goal_checks.values())

    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok"
        if (
            structural_refactor_map_created
            and nine_lines_present
            and completed_section
            and partial_section
            and duplicate_section
            and historical_section
            and future_folder_suggestions
            and non_goals_present
        )
        else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Adds a structural refactor validation boundary preventing future duplicate/rebuild work.",
            "runtime_capability_change": False,
        },
        "structural_refactor_map_created": structural_refactor_map_created,
        "nine_lines_present": nine_lines_present,
        "line_count": sum(1 for check in line_checks if check["present"]),
        "completed_do_not_rebuild_section_present": completed_section and all(completed.values()),
        "partial_extend_only_section_present": partial_section and all(partial.values()),
        "duplicate_merge_candidates_listed": duplicate_section,
        "historical_archive_candidates_listed": historical_section,
        "future_folder_suggestions_present": future_folder_suggestions,
        "runtime_behavior_changed": False,
        "files_moved": False,
        "files_deleted": False,
        "files_renamed": False,
        "imports_changed": False,
        "new_runtime_authority_created": False,
        "line_checks": line_checks,
        "completed_do_not_rebuild_anchors": completed,
        "partial_extend_only_anchors": partial,
        "duplicate_merge_candidate_families": duplicates,
        "historical_archive_candidate_summary": {
            "section_present": historical_section,
            "files_deleted": False,
            "files_archived": False,
            "archive_candidates_listed_only": historical_section,
        },
        "proposed_refactor_phases": {
            "R1_structural_map_only": "R1: structural map only." in text,
            "R2_alias_plan_only_next": "R2: add package `__init__` wrappers / aliases." in text,
            "moves_performed_in_this_package": False,
            "imports_changed_in_this_package": False,
        },
        "future_folder_suggestions": future_folders,
        "non_goals": non_goal_checks,
        "cli_visible_summary": [
            f"structural_refactor_map_created={structural_refactor_map_created}",
            f"nine_lines_present={nine_lines_present}",
            f"line_count={sum(1 for check in line_checks if check['present'])}",
            "runtime_behavior_changed=False",
            "files_moved=False",
            "files_deleted=False",
            "files_renamed=False",
        ],
        "human_summary": {
            "what_was_built": "A nine-line structural refactor map and read-only checker.",
            "what_error_it_prevents": "It prevents future roadmap work from rebuilding existing organs or scattering new work into more minimal-package fog.",
            "what_did_not_change": "No file move, import change, runtime behavior, action authority, memory write, endocrine feed, or production behavior was created.",
            "plain_result": "ASHL Core now has a map for future refactor planning, not a refactor execution.",
        },
    }


def validate_structural_refactor_map_minimal_record(record: dict[str, Any]) -> dict[str, Any]:
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
        "structural_refactor_map_created": True,
        "nine_lines_present": True,
        "line_count": 9,
        "completed_do_not_rebuild_section_present": True,
        "partial_extend_only_section_present": True,
        "duplicate_merge_candidates_listed": True,
        "historical_archive_candidates_listed": True,
        "future_folder_suggestions_present": True,
        "runtime_behavior_changed": False,
        "files_moved": False,
        "files_deleted": False,
        "files_renamed": False,
        "imports_changed": False,
        "new_runtime_authority_created": False,
    }
    for field, expected in expected_values.items():
        if record.get(field) != expected:
            errors.append(f"{field}_wrong")

    boundary = record.get("boundary", {})
    if boundary.get("boundary_index_version_before") != BOUNDARY_INDEX_BEFORE:
        errors.append("boundary_before_wrong")
    if boundary.get("boundary_index_version_after") != BOUNDARY_INDEX_AFTER:
        errors.append("boundary_after_wrong")
    if boundary.get("boundary_reason") != "Adds a structural refactor validation boundary preventing future duplicate/rebuild work.":
        errors.append("boundary_reason_wrong")
    if boundary.get("runtime_capability_change") is not False:
        errors.append("boundary_runtime_capability_change_wrong")

    line_checks = record.get("line_checks", [])
    if not isinstance(line_checks, list) or len(line_checks) != 9:
        errors.append("line_checks_wrong_count")
    else:
        for check in line_checks:
            for field in (
                "present",
                "plain_role_present",
                "core_modules_present",
                "related_tests_present",
                "related_docs_present",
                "current_outputs_present",
                "partial_or_design_only_parts_present",
                "duplicate_or_merge_candidates_present",
                "historical_or_archive_candidates_present",
                "future_folder_suggestion_present",
            ):
                if check.get(field) is not True:
                    errors.append(f"line_{check.get('line_name')}_{field}_wrong")

    for field in (
        "completed_do_not_rebuild_anchors",
        "partial_extend_only_anchors",
        "duplicate_merge_candidate_families",
        "future_folder_suggestions",
        "non_goals",
    ):
        values = record.get(field, {})
        if not isinstance(values, dict) or not values or not all(values.values()):
            errors.append(f"{field}_wrong")

    historical = record.get("historical_archive_candidate_summary", {})
    if historical.get("section_present") is not True:
        errors.append("historical_section_missing")
    if historical.get("files_deleted") is not False or historical.get("files_archived") is not False:
        errors.append("historical_archive_side_effect_wrong")

    phases = record.get("proposed_refactor_phases", {})
    if phases.get("R1_structural_map_only") is not True:
        errors.append("phase_R1_missing")
    if phases.get("R2_alias_plan_only_next") is not True:
        errors.append("phase_R2_missing")
    if phases.get("moves_performed_in_this_package") is not False:
        errors.append("phase_moves_performed_wrong")
    if phases.get("imports_changed_in_this_package") is not False:
        errors.append("phase_imports_changed_wrong")

    if not record.get("human_summary", {}).get("what_error_it_prevents"):
        errors.append("human_summary_error_prevention_empty")

    return {
        "valid": not errors,
        "error_codes": errors,
        "structural_refactor_map_created": record.get("structural_refactor_map_created") is True,
        "nine_lines_present": record.get("nine_lines_present") is True,
        "line_count": record.get("line_count"),
        "completed_do_not_rebuild_section_present": record.get("completed_do_not_rebuild_section_present") is True,
        "partial_extend_only_section_present": record.get("partial_extend_only_section_present") is True,
        "duplicate_merge_candidates_listed": record.get("duplicate_merge_candidates_listed") is True,
        "historical_archive_candidates_listed": record.get("historical_archive_candidates_listed") is True,
        "future_folder_suggestions_present": record.get("future_folder_suggestions_present") is True,
        "runtime_behavior_changed": record.get("runtime_behavior_changed") is True,
        "files_moved": record.get("files_moved") is True,
        "files_deleted": record.get("files_deleted") is True,
        "files_renamed": record.get("files_renamed") is True,
        "imports_changed": record.get("imports_changed") is True,
        "new_runtime_authority_created": record.get("new_runtime_authority_created") is True,
    }


def _line_check(text: str, line_name: str) -> dict[str, Any]:
    section = _section_for_line(text, line_name)
    return {
        "line_name": line_name,
        "present": bool(section),
        "plain_role_present": "Plain role:" in section,
        "core_modules_present": "Current core modules:" in section,
        "related_tests_present": "Current tests:" in section,
        "related_docs_present": "Current docs:" in section,
        "current_outputs_present": "Current outputs:" in section,
        "partial_or_design_only_parts_present": "Partial or design-only parts:" in section,
        "duplicate_or_merge_candidates_present": "Duplicate or merge candidates:" in section,
        "historical_or_archive_candidates_present": "Historical or archive candidates:" in section,
        "future_folder_suggestion_present": "Future folder suggestion:" in section,
    }


def _section_for_line(text: str, line_name: str) -> str:
    marker = f"## {line_name}"
    start = text.find(marker)
    if start < 0:
        return ""
    next_start = text.find("\n## ", start + len(marker))
    if next_start < 0:
        return text[start:]
    return text[start:next_start]


def run_structural_refactor_map_minimal_check() -> dict[str, Any]:
    record = build_structural_refactor_map_minimal_record()
    validation = validate_structural_refactor_map_minimal_record(record)
    record["status"] = "ok" if validation["valid"] else "failed"
    return record
