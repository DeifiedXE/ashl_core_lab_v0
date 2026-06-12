"""Phase 0 Level 1 first contact danger sandbox wrapper."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_outcome_lesson_review_candidate_minimal import (
    build_sandbox_outcome_lesson_review_candidate,
)


COMMAND = "run-phase0-level1-first-contact-danger-minimal-check"
FLOW = "phase0_level1_first_contact_danger_minimal_v0"
LEVEL_ID = "phase0_level1_first_contact_danger"
LEVEL_TITLE = "小關 1：第一次接觸，認識危險"
LEVEL_MODE = "one_step_symbolic_sandbox_level"
DANGER_SYMBOLS = {"d"}

REQUIRED_TOP_LEVEL = {
    "level_result_id",
    "level_info",
    "map_fixture",
    "symbol_detection",
    "action_path",
    "sandbox_outcome",
    "lesson_review_status",
    "human_summary",
    "blocked_flags",
}

REQUIRED_HUMAN_SUMMARY = {
    "what_was_tested",
    "what_happened",
    "what_the_result_means",
    "what_it_does_not_mean",
    "plain_result",
}

REQUIRED_BLOCKED_FLAGS = {
    "pathfinding_performed",
    "goal_reached_claim",
    "object_recognition",
    "semantic_vision",
    "production_action_selection",
    "runtime_action_selection",
    "selected_action_created",
    "final_action_created",
    "direct_action_command",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_policy_written",
    "general_behavior_changed",
    "lesson_applied",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_phase0_level1_first_contact_danger_result() -> dict[str, Any]:
    lesson_candidate = build_sandbox_outcome_lesson_review_candidate()
    context = lesson_candidate.get("candidate_context", {})
    requirements = lesson_candidate.get("review_requirements", {})
    content = lesson_candidate.get("candidate_content", {})
    front_symbol = "d"
    danger_ahead = front_symbol in DANGER_SYMBOLS

    return {
        "level_result_id": "phase0_level1_first_contact_danger_demo_001",
        "level_info": {
            "level_id": LEVEL_ID,
            "level_title": LEVEL_TITLE,
            "level_mode": LEVEL_MODE,
            "pathfinding_required": False,
            "goal_reach_required": False,
        },
        "map_fixture": {
            "map_size": [5, 5],
            "agent_position": [0, 0],
            "facing": "east",
            "front_cell_position": [1, 0],
            "front_symbol": front_symbol,
            "goal_position": [4, 4],
            "goal_used_in_v0": False,
        },
        "symbol_detection": {
            "front_symbol_checked": True,
            "front_symbol": front_symbol,
            "danger_ahead": danger_ahead,
            "symbol_fixture_only": True,
            "object_recognition": False,
            "semantic_vision": False,
        },
        "action_path": {
            "candidate_action": "check_before_retry",
            "choice_candidate_used": True,
            "sandbox_intent_created": True,
            "sandbox_action_executed": True,
            "executed_sandbox_action": "check_before_retry",
            "production_action_selection": False,
            "final_action_created": False,
        },
        "sandbox_outcome": {
            "checked_before_retry": True,
            "danger_detected": context.get("sandbox_check_success") is True,
            "obstacle_detected": True,
            "retry_same_action_executed": False,
            "movement_executed": False,
            "outcome_match": context.get("outcome_match"),
            "sandbox_check_success": context.get("sandbox_check_success"),
            "state_mutation_scope": "sandbox_record_only",
        },
        "lesson_review_status": {
            "lesson_review_candidate_ready": True,
            "requires_human_review": requirements.get("requires_human_review"),
            "lesson_applied": False,
            "memory_write": False,
            "retention_write": False,
            "predictor_modified": False,
            "candidate_statement": (
                "In the controlled danger sandbox, check_before_retry detected the danger before retrying "
                "and avoided retry_same_action movement."
            )
            if content.get("candidate_statement")
            else "",
        },
        "human_summary": {
            "what_was_tested": "Level 1 tested a one-step symbolic danger contact.",
            "what_happened": (
                "The front symbol d was detected as danger, and check_before_retry was executed once in the sandbox."
            ),
            "what_the_result_means": (
                "The sandbox action detected danger before retrying and did not move into the danger cell."
            ),
            "what_it_does_not_mean": (
                "This is not pathfinding, not lesson application, not object recognition, and not proof of learning."
            ),
            "plain_result": "Level 1 is passed as a controlled one-step sandbox danger check.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_phase0_level1_first_contact_danger_result(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _check_top_level(record, errors)

    level_info = _section(record, "level_info", errors)
    if level_info.get("level_id") != LEVEL_ID:
        errors.append("level_id_not_phase0_level1_first_contact_danger")
    if level_info.get("level_mode") != LEVEL_MODE:
        errors.append("level_mode_not_one_step_symbolic_sandbox_level")
    _require_false(level_info, "pathfinding_required", errors)
    _require_false(level_info, "goal_reach_required", errors)

    map_fixture = _section(record, "map_fixture", errors)
    if map_fixture.get("map_size") != [5, 5]:
        errors.append("map_size_not_5x5")
    if map_fixture.get("agent_position") != [0, 0]:
        errors.append("agent_position_not_origin")
    if map_fixture.get("facing") != "east":
        errors.append("facing_not_east")
    if map_fixture.get("front_cell_position") != [1, 0]:
        errors.append("front_cell_position_not_1_0")
    if map_fixture.get("front_symbol") != "d":
        errors.append("front_symbol_not_d")
    _require_false(map_fixture, "goal_used_in_v0", errors)

    symbol_detection = _section(record, "symbol_detection", errors)
    _require_true(symbol_detection, "front_symbol_checked", errors)
    if symbol_detection.get("front_symbol") != "d":
        errors.append("symbol_detection_front_symbol_not_d")
    _require_true(symbol_detection, "danger_ahead", errors)
    _require_true(symbol_detection, "symbol_fixture_only", errors)
    _require_false(symbol_detection, "object_recognition", errors)
    _require_false(symbol_detection, "semantic_vision", errors)

    action_path = _section(record, "action_path", errors)
    if action_path.get("candidate_action") != "check_before_retry":
        errors.append("candidate_action_not_check_before_retry")
    _require_true(action_path, "choice_candidate_used", errors)
    _require_true(action_path, "sandbox_intent_created", errors)
    _require_true(action_path, "sandbox_action_executed", errors)
    if action_path.get("executed_sandbox_action") != "check_before_retry":
        errors.append("executed_sandbox_action_not_check_before_retry")
    _require_false(action_path, "production_action_selection", errors)
    _require_false(action_path, "final_action_created", errors)

    sandbox_outcome = _section(record, "sandbox_outcome", errors)
    _require_true(sandbox_outcome, "checked_before_retry", errors)
    _require_true(sandbox_outcome, "danger_detected", errors)
    _require_true(sandbox_outcome, "obstacle_detected", errors)
    _require_false(sandbox_outcome, "retry_same_action_executed", errors)
    _require_false(sandbox_outcome, "movement_executed", errors)
    _require_true(sandbox_outcome, "outcome_match", errors)
    _require_true(sandbox_outcome, "sandbox_check_success", errors)
    if sandbox_outcome.get("state_mutation_scope") != "sandbox_record_only":
        errors.append("state_mutation_scope_not_sandbox_record_only")

    lesson_status = _section(record, "lesson_review_status", errors)
    _require_true(lesson_status, "lesson_review_candidate_ready", errors)
    _require_true(lesson_status, "requires_human_review", errors)
    _require_false(lesson_status, "lesson_applied", errors)
    _require_false(lesson_status, "memory_write", errors)
    _require_false(lesson_status, "retention_write", errors)
    _require_false(lesson_status, "predictor_modified", errors)
    if not isinstance(lesson_status.get("candidate_statement"), str) or not lesson_status.get("candidate_statement"):
        errors.append("candidate_statement_empty_or_not_string")

    human_summary = _section(record, "human_summary", errors)
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        if field not in human_summary:
            errors.append(f"missing_human_summary_field:{field}")
        elif not isinstance(human_summary.get(field), str) or not human_summary.get(field):
            errors.append(f"{field}_empty_or_not_string")

    blocked_flags = _section(record, "blocked_flags", errors)
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "level_result_id": record.get("level_result_id"),
        "valid": not errors,
        "error_codes": errors,
        "danger_symbol_detected": symbol_detection.get("front_symbol") == "d"
        and symbol_detection.get("danger_ahead") is True,
        "sandbox_action_executed": action_path.get("sandbox_action_executed") is True,
        "check_before_retry_executed": action_path.get("executed_sandbox_action") == "check_before_retry",
        "danger_detected": sandbox_outcome.get("danger_detected") is True,
        "movement_blocked": sandbox_outcome.get("movement_executed") is False
        and sandbox_outcome.get("retry_same_action_executed") is False,
        "outcome_match": sandbox_outcome.get("outcome_match") is True,
        "sandbox_check_success": sandbox_outcome.get("sandbox_check_success") is True,
        "lesson_review_candidate_ready": lesson_status.get("lesson_review_candidate_ready") is True,
        "requires_human_review": lesson_status.get("requires_human_review") is True,
    }


def run_phase0_level1_first_contact_danger_minimal_check() -> dict[str, Any]:
    valid_result = build_phase0_level1_first_contact_danger_result()
    records = [valid_result, *_invalid_demo_records(valid_result)]
    validation_results = [validate_phase0_level1_first_contact_danger_result(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "level_results": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "level_wrapper_added": True,
            "pathfinding_added": False,
            "goal_reach_claim_added": False,
            "object_recognition_added": False,
            "semantic_vision_added": False,
            "lesson_application_added": False,
            "memory_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "proof_of_learning_claimed": False,
        },
        "notes": [
            "Level 1 proves a controlled one-step danger contact loop, not learning, planning, or maze solving.",
            "The front symbol d is a deterministic symbolic fixture, not object recognition or semantic vision.",
        ],
    }


def _invalid_demo_records(valid_result: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    mutations = [
        ("level_info", "level_id", "bad_level"),
        ("level_info", "level_mode", "free_navigation_level"),
        ("level_info", "pathfinding_required", True),
        ("level_info", "goal_reach_required", True),
        ("map_fixture", "map_size", [4, 4]),
        ("map_fixture", "agent_position", [1, 1]),
        ("map_fixture", "facing", "north"),
        ("map_fixture", "front_cell_position", [0, 1]),
        ("map_fixture", "front_symbol", "."),
        ("map_fixture", "goal_used_in_v0", True),
        ("symbol_detection", "front_symbol_checked", False),
        ("symbol_detection", "front_symbol", "."),
        ("symbol_detection", "danger_ahead", False),
        ("symbol_detection", "symbol_fixture_only", False),
        ("symbol_detection", "object_recognition", True),
        ("symbol_detection", "semantic_vision", True),
        ("action_path", "candidate_action", "retry_same_action"),
        ("action_path", "choice_candidate_used", False),
        ("action_path", "sandbox_intent_created", False),
        ("action_path", "sandbox_action_executed", False),
        ("action_path", "executed_sandbox_action", "retry_same_action"),
        ("action_path", "production_action_selection", True),
        ("action_path", "final_action_created", True),
        ("sandbox_outcome", "checked_before_retry", False),
        ("sandbox_outcome", "danger_detected", False),
        ("sandbox_outcome", "obstacle_detected", False),
        ("sandbox_outcome", "retry_same_action_executed", True),
        ("sandbox_outcome", "movement_executed", True),
        ("sandbox_outcome", "outcome_match", False),
        ("sandbox_outcome", "sandbox_check_success", False),
        ("sandbox_outcome", "state_mutation_scope", "runtime_state"),
        ("lesson_review_status", "lesson_review_candidate_ready", False),
        ("lesson_review_status", "requires_human_review", False),
        ("lesson_review_status", "lesson_applied", True),
        ("lesson_review_status", "memory_write", True),
        ("lesson_review_status", "retention_write", True),
        ("lesson_review_status", "predictor_modified", True),
        ("lesson_review_status", "candidate_statement", ""),
    ]
    for section, field, value in mutations:
        invalid = _copy_case(valid_result, f"{section}_{field}")
        invalid[section][field] = value
        records.append(invalid)

    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        invalid = _copy_case(valid_result, f"empty_{field}")
        invalid["human_summary"][field] = ""
        records.append(invalid)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid = _copy_case(valid_result, flag)
        invalid["blocked_flags"][flag] = True
        records.append(invalid)

    return records


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "level1_result_count": len(validation_results),
        "valid_level1_result_count": len(valid_results),
        "invalid_level1_result_count": sum(1 for result in validation_results if not result["valid"]),
        "danger_symbol_detected_count": sum(1 for result in valid_results if result["danger_symbol_detected"]),
        "sandbox_action_executed_count": sum(1 for result in valid_results if result["sandbox_action_executed"]),
        "check_before_retry_executed_count": sum(
            1 for result in valid_results if result["check_before_retry_executed"]
        ),
        "danger_detected_count": sum(1 for result in valid_results if result["danger_detected"]),
        "movement_blocked_count": sum(1 for result in valid_results if result["movement_blocked"]),
        "outcome_match_count": sum(1 for result in valid_results if result["outcome_match"]),
        "sandbox_check_success_count": sum(1 for result in valid_results if result["sandbox_check_success"]),
        "lesson_review_candidate_ready_count": sum(
            1 for result in valid_results if result["lesson_review_candidate_ready"]
        ),
        "requires_human_review_count": sum(1 for result in valid_results if result["requires_human_review"]),
        "pathfinding_blocked_count": _count_error(validation_results, "pathfinding_required_not_false")
        + _count_error(validation_results, "pathfinding_performed_enabled"),
        "goal_reach_claim_blocked_count": _count_error(validation_results, "goal_reach_required_not_false")
        + _count_error(validation_results, "goal_reached_claim_enabled"),
        "object_recognition_blocked_count": _count_error(validation_results, "object_recognition_not_false")
        + _count_error(validation_results, "object_recognition_enabled"),
        "semantic_vision_blocked_count": _count_error(validation_results, "semantic_vision_not_false")
        + _count_error(validation_results, "semantic_vision_enabled"),
        "production_action_selection_blocked_count": _count_error(
            validation_results,
            "production_action_selection_not_false",
        )
        + _count_error(validation_results, "production_action_selection_enabled"),
        "runtime_action_selection_blocked_count": _count_error(validation_results, "runtime_action_selection_enabled"),
        "selected_action_created_blocked_count": _count_error(
            validation_results,
            "selected_action_created_enabled",
        ),
        "final_action_created_blocked_count": _count_error(validation_results, "final_action_created_not_false")
        + _count_error(validation_results, "final_action_created_enabled"),
        "direct_action_command_blocked_count": _count_error(validation_results, "direct_action_command_enabled"),
        "real_navigation_changed_blocked_count": _count_error(validation_results, "real_navigation_changed_enabled"),
        "ui_behavior_changed_blocked_count": _count_error(validation_results, "ui_behavior_changed_enabled"),
        "persistent_policy_written_blocked_count": _count_error(
            validation_results,
            "persistent_policy_written_enabled",
        ),
        "general_behavior_changed_blocked_count": _count_error(
            validation_results,
            "general_behavior_changed_enabled",
        ),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_not_false")
        + _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_not_false")
        + _count_error(validation_results, "memory_write_enabled"),
        "retention_write_blocked_count": _count_error(validation_results, "retention_write_not_false")
        + _count_error(validation_results, "retention_write_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_not_false")
        + _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
    }
    summary["all_phase0_level1_first_contact_danger_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["level1_result_count"] == 63
        and summary["valid_level1_result_count"] == 1
        and summary["invalid_level1_result_count"] == 62
        and summary["danger_symbol_detected_count"] == 1
        and summary["sandbox_action_executed_count"] == 1
        and summary["check_before_retry_executed_count"] == 1
        and summary["danger_detected_count"] == 1
        and summary["movement_blocked_count"] == 1
        and summary["outcome_match_count"] == 1
        and summary["sandbox_check_success_count"] == 1
        and summary["lesson_review_candidate_ready_count"] == 1
        and summary["requires_human_review_count"] == 1
        and summary["pathfinding_blocked_count"] >= 2
        and summary["goal_reach_claim_blocked_count"] >= 2
        and summary["object_recognition_blocked_count"] >= 2
        and summary["semantic_vision_blocked_count"] >= 2
        and summary["production_action_selection_blocked_count"] >= 2
        and summary["runtime_action_selection_blocked_count"] == 1
        and summary["selected_action_created_blocked_count"] == 1
        and summary["final_action_created_blocked_count"] >= 2
        and summary["direct_action_command_blocked_count"] == 1
        and summary["real_navigation_changed_blocked_count"] == 1
        and summary["ui_behavior_changed_blocked_count"] == 1
        and summary["persistent_policy_written_blocked_count"] == 1
        and summary["general_behavior_changed_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] >= 2
        and summary["memory_write_blocked_count"] >= 2
        and summary["retention_write_blocked_count"] >= 2
        and summary["predictor_modified_blocked_count"] >= 2
        and summary["proof_of_learning_claim_blocked_count"] == 1
    )


def _check_top_level(record: dict[str, Any], errors: list[str]) -> None:
    for field in sorted(REQUIRED_TOP_LEVEL):
        if field not in record:
            errors.append(f"missing_required_field:{field}")
    for field in sorted(record):
        if field not in REQUIRED_TOP_LEVEL:
            errors.append(f"unexpected_field:{field}")


def _section(record: dict[str, Any], field: str, errors: list[str]) -> dict[str, Any]:
    value = record.get(field)
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _require_true(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not True:
        errors.append(f"{field}_not_true")


def _require_false(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not False:
        errors.append(f"{field}_not_false")


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["level_result_id"] = f"{record['level_result_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])
