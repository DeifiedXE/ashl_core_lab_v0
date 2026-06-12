"""Non-executing action choice candidate from adjacent review."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .action_selection_adjacent_review_minimal import (
    REVIEW_MODE,
    build_action_selection_adjacent_review,
)


COMMAND = "run-non-executing-action-choice-candidate-minimal-check"
FLOW = "non_executing_action_choice_candidate_minimal_v0"
CHOICE_MODE = "non_executing_choice_candidate_only"
EXPECTED_ACTION = "check_before_retry"
EXPECTED_SCENARIO_ID = "obstacle_retry_failed_same_state"
EXPECTED_EXACT_KEY = "obstacle_retry_failed"

REQUIRED_FIELDS = {
    "choice_candidate_id",
    "source_review_id",
    "choice_mode",
    "choice_candidate_action",
    "choice_source",
    "choice_constraints",
    "human_summary",
    "blocked_flags",
}

REQUIRED_CHOICE_SOURCE = {
    "source_review_mode",
    "source_most_review_worthy_candidate",
    "source_scenario_id",
    "source_exact_key",
    "source_reason",
}

REQUIRED_CHOICE_CONSTRAINTS = {
    "candidate_only",
    "non_executing",
    "selected_action",
    "final_action",
    "action_execution",
    "direct_command",
    "runtime_action_selection",
    "may_enter_one_step_sandbox_action_intent",
}

REQUIRED_HUMAN_SUMMARY = {
    "what_was_named",
    "why_it_was_named",
    "what_it_is_not",
    "plain_result",
}

REQUIRED_BLOCKED_FLAGS = {
    "production_action_selection",
    "runtime_action_selection",
    "selected_action_created",
    "final_action_created",
    "action_executed",
    "direct_action_command",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_policy_written",
    "general_behavior_changed",
    "semantic_or_fuzzy_match_used",
    "exploration_blocked",
    "curiosity_overridden",
    "mentor_override_blocked",
    "lesson_applied",
    "memory_write",
    "new_retention_written",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_non_executing_action_choice_candidate(
    review_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = review_result or build_action_selection_adjacent_review()
    choice_action = source.get("review_summary", {}).get("most_review_worthy_candidate", "")
    source_item = _source_item_for_action(source.get("review_items", []), choice_action)
    return {
        "choice_candidate_id": "non_executing_action_choice_candidate_demo_001",
        "source_review_id": source.get("review_id", "action_selection_adjacent_review_demo_001"),
        "choice_mode": CHOICE_MODE,
        "choice_candidate_action": choice_action,
        "choice_source": {
            "source_review_mode": source.get("review_mode", REVIEW_MODE),
            "source_most_review_worthy_candidate": choice_action,
            "source_scenario_id": source_item.get("scenario_id"),
            "source_exact_key": source_item.get("exact_key"),
            "source_reason": "check_before_retry was highlighted as the most review-worthy candidate.",
        },
        "choice_constraints": {
            "candidate_only": True,
            "non_executing": True,
            "selected_action": False,
            "final_action": False,
            "action_execution": False,
            "direct_command": False,
            "runtime_action_selection": False,
            "may_enter_one_step_sandbox_action_intent": True,
        },
        "human_summary": {
            "what_was_named": "check_before_retry was named as a non-executing action choice candidate.",
            "why_it_was_named": "It was the most review-worthy candidate from the action-selection-adjacent review.",
            "what_it_is_not": "It is not a selected action, final action, command, or execution.",
            "plain_result": "The system can name one action candidate for non-executing intent preparation, but still cannot choose or execute an action.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_non_executing_action_choice_candidate(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)
    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if record.get("choice_mode") != CHOICE_MODE:
        errors.append("choice_mode_not_non_executing_choice_candidate_only")
    if record.get("choice_candidate_action") != EXPECTED_ACTION:
        errors.append("choice_candidate_action_not_check_before_retry")

    choice_source = _section(record, "choice_source", errors)
    _require_section_fields("choice_source", choice_source, REQUIRED_CHOICE_SOURCE, errors)
    if choice_source.get("source_review_mode") != REVIEW_MODE:
        errors.append("source_review_mode_not_action_selection_adjacent_review_only")
    if choice_source.get("source_most_review_worthy_candidate") != record.get("choice_candidate_action"):
        errors.append("source_most_review_worthy_candidate_mismatch")
    if choice_source.get("source_scenario_id") != EXPECTED_SCENARIO_ID:
        errors.append("source_scenario_id_not_obstacle_retry_failed_same_state")
    if choice_source.get("source_exact_key") != EXPECTED_EXACT_KEY:
        errors.append("source_exact_key_not_obstacle_retry_failed")
    if not isinstance(choice_source.get("source_reason"), str) or not choice_source.get("source_reason"):
        errors.append("source_reason_empty_or_not_string")

    constraints = _section(record, "choice_constraints", errors)
    _require_section_fields("choice_constraints", constraints, REQUIRED_CHOICE_CONSTRAINTS, errors)
    _require_true(constraints, "candidate_only", errors)
    _require_true(constraints, "non_executing", errors)
    _require_false(constraints, "selected_action", errors)
    _require_false(constraints, "final_action", errors)
    _require_false(constraints, "action_execution", errors)
    _require_false(constraints, "direct_command", errors)
    _require_false(constraints, "runtime_action_selection", errors)
    _require_true(constraints, "may_enter_one_step_sandbox_action_intent", errors)

    human_summary = _section(record, "human_summary", errors)
    _require_section_fields("human_summary", human_summary, REQUIRED_HUMAN_SUMMARY, errors)
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        if not isinstance(human_summary.get(field), str) or not human_summary.get(field):
            errors.append(f"{field}_empty_or_not_string")

    blocked_flags = _section(record, "blocked_flags", errors)
    _require_section_fields("blocked_flags", blocked_flags, REQUIRED_BLOCKED_FLAGS, errors)
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        if field in blocked_flags and blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "choice_candidate_id": record.get("choice_candidate_id"),
        "valid": not errors,
        "error_codes": errors,
        "choice_candidate_action": record.get("choice_candidate_action") == EXPECTED_ACTION,
        "candidate_only": constraints.get("candidate_only") is True,
        "non_executing": constraints.get("non_executing") is True,
        "not_selected_action": constraints.get("selected_action") is False,
        "not_final_action": constraints.get("final_action") is False,
        "not_action_execution": constraints.get("action_execution") is False,
        "not_direct_command": constraints.get("direct_command") is False,
        "not_runtime_action_selection": constraints.get("runtime_action_selection") is False,
        "may_enter_one_step_sandbox_action_intent": (
            constraints.get("may_enter_one_step_sandbox_action_intent") is True
        ),
        **_blocked_flag_values(blocked_flags),
    }


def run_non_executing_action_choice_candidate_minimal_check() -> dict[str, Any]:
    valid_candidate = build_non_executing_action_choice_candidate()
    records = [
        valid_candidate,
        *_invalid_demo_records(valid_candidate),
    ]
    validation_results = [validate_non_executing_action_choice_candidate(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "non_executing_action_choice_candidates": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "A choice candidate is allowed to be named, but it is not a selected action, final action, command, or execution.",
            "The next layer may prepare one-step sandbox intent only.",
            "Production action selection, runtime action selection, execution, direct commands, and persistent policy remain blocked.",
        ],
    }


def _source_item_for_action(review_items: Any, action: str) -> dict[str, Any]:
    if not isinstance(review_items, list):
        return {}
    for item in review_items:
        if isinstance(item, dict) and item.get("reviewed_action") == action:
            return item
    return {}


def _section(record: dict[str, Any], field: str, errors: list[str]) -> dict[str, Any]:
    value = record.get(field)
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _require_section_fields(section_name: str, section: dict[str, Any], required: set[str], errors: list[str]) -> None:
    for field in sorted(required):
        if field not in section:
            errors.append(f"missing_{section_name}_field:{field}")


def _require_true(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not True:
        errors.append(f"{field}_not_true")


def _require_false(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not False:
        errors.append(f"{field}_not_false")


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _invalid_demo_records(valid_candidate: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    bad_mode = _copy_case(valid_candidate, "bad_choice_mode")
    bad_mode["choice_mode"] = "runtime_action_selection_choice"
    records.append(bad_mode)

    wrong_action = _copy_case(valid_candidate, "wrong_choice_candidate_action")
    wrong_action["choice_candidate_action"] = "ask_for_help"
    wrong_action["choice_source"]["source_most_review_worthy_candidate"] = "ask_for_help"
    records.append(wrong_action)

    source_cases = [
        ("source_most_review_worthy_candidate", "ask_for_help", "source_most_review_worthy_mismatch"),
        ("source_scenario_id", "unclear_failure_same_state", "wrong_source_scenario_id"),
        ("source_exact_key", "unclear_failure_repeated", "wrong_source_exact_key"),
        ("source_reason", "", "empty_source_reason"),
    ]
    for field, value, name in source_cases:
        invalid = _copy_case(valid_candidate, name)
        invalid["choice_source"][field] = value
        records.append(invalid)

    constraint_cases = [
        ("candidate_only", False),
        ("non_executing", False),
        ("selected_action", True),
        ("final_action", True),
        ("action_execution", True),
        ("direct_command", True),
        ("runtime_action_selection", True),
        ("may_enter_one_step_sandbox_action_intent", False),
    ]
    for field, value in constraint_cases:
        invalid = _copy_case(valid_candidate, f"{field}_{value}")
        invalid["choice_constraints"][field] = value
        records.append(invalid)

    for field in ("what_was_named", "what_it_is_not", "plain_result"):
        invalid = _copy_case(valid_candidate, f"empty_{field}")
        invalid["human_summary"][field] = ""
        records.append(invalid)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid = _copy_case(valid_candidate, flag)
        invalid["blocked_flags"][flag] = True
        records.append(invalid)

    return records


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["choice_candidate_id"] = f"{record['choice_candidate_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "choice_candidate_result_count": len(validation_results),
        "valid_choice_candidate_result_count": len(valid_results),
        "invalid_choice_candidate_result_count": sum(1 for result in validation_results if not result["valid"]),
        "choice_candidate_action_count": sum(1 for result in valid_results if result["choice_candidate_action"]),
        "candidate_only_count": sum(1 for result in valid_results if result["candidate_only"]),
        "non_executing_count": sum(1 for result in valid_results if result["non_executing"]),
        "not_selected_action_count": sum(1 for result in valid_results if result["not_selected_action"]),
        "not_final_action_count": sum(1 for result in valid_results if result["not_final_action"]),
        "not_action_execution_count": sum(1 for result in valid_results if result["not_action_execution"]),
        "not_direct_command_count": sum(1 for result in valid_results if result["not_direct_command"]),
        "not_runtime_action_selection_count": sum(
            1 for result in valid_results if result["not_runtime_action_selection"]
        ),
        "may_enter_one_step_sandbox_action_intent_count": sum(
            1 for result in valid_results if result["may_enter_one_step_sandbox_action_intent"]
        ),
        "bad_choice_mode_blocked_count": _count_error(
            validation_results,
            "choice_mode_not_non_executing_choice_candidate_only",
        ),
        "wrong_choice_candidate_action_blocked_count": _count_error(
            validation_results,
            "choice_candidate_action_not_check_before_retry",
        ),
        "source_mismatch_blocked_count": _count_errors(
            validation_results,
            {
                "source_most_review_worthy_candidate_mismatch",
                "source_scenario_id_not_obstacle_retry_failed_same_state",
                "source_exact_key_not_obstacle_retry_failed",
            },
        ),
        "selected_action_blocked_count": _count_error(validation_results, "selected_action_not_false"),
        "final_action_blocked_count": _count_error(validation_results, "final_action_not_false"),
        "action_execution_blocked_count": _count_error(validation_results, "action_execution_not_false"),
        "direct_command_blocked_count": _count_error(validation_results, "direct_command_not_false"),
        "runtime_action_selection_blocked_count": _count_error(
            validation_results,
            "runtime_action_selection_not_false",
        ),
        "production_action_selection_blocked_count": _count_error(
            validation_results,
            "production_action_selection_enabled",
        ),
        "runtime_action_selection_flag_blocked_count": _count_error(
            validation_results,
            "runtime_action_selection_enabled",
        ),
        "selected_action_created_blocked_count": _count_error(
            validation_results,
            "selected_action_created_enabled",
        ),
        "final_action_created_blocked_count": _count_error(validation_results, "final_action_created_enabled"),
        "action_executed_blocked_count": _count_error(validation_results, "action_executed_enabled"),
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
        "semantic_or_fuzzy_match_used_blocked_count": _count_error(
            validation_results,
            "semantic_or_fuzzy_match_used_enabled",
        ),
        "exploration_blocked_count": _count_error(validation_results, "exploration_blocked_enabled"),
        "curiosity_overridden_blocked_count": _count_error(validation_results, "curiosity_overridden_enabled"),
        "mentor_override_blocked_count": _count_error(validation_results, "mentor_override_blocked_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(validation_results, "new_retention_written_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
        "candidate_only_false_blocked_count": _count_error(validation_results, "candidate_only_not_true"),
        "non_executing_false_blocked_count": _count_error(validation_results, "non_executing_not_true"),
        "may_enter_one_step_false_blocked_count": _count_error(
            validation_results,
            "may_enter_one_step_sandbox_action_intent_not_true",
        ),
        "empty_what_was_named_blocked_count": _count_error(
            validation_results,
            "what_was_named_empty_or_not_string",
        ),
        "empty_what_it_is_not_blocked_count": _count_error(
            validation_results,
            "what_it_is_not_empty_or_not_string",
        ),
        "empty_plain_result_blocked_count": _count_error(validation_results, "plain_result_empty_or_not_string"),
        "empty_source_reason_blocked_count": _count_error(validation_results, "source_reason_empty_or_not_string"),
    }
    summary["all_non_executing_action_choice_candidate_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["choice_candidate_result_count"] == 37
        and summary["valid_choice_candidate_result_count"] == 1
        and summary["invalid_choice_candidate_result_count"] == 36
        and summary["choice_candidate_action_count"] == 1
        and summary["candidate_only_count"] == 1
        and summary["non_executing_count"] == 1
        and summary["not_selected_action_count"] == 1
        and summary["not_final_action_count"] == 1
        and summary["not_action_execution_count"] == 1
        and summary["not_direct_command_count"] == 1
        and summary["not_runtime_action_selection_count"] == 1
        and summary["may_enter_one_step_sandbox_action_intent_count"] == 1
        and summary["bad_choice_mode_blocked_count"] == 1
        and summary["wrong_choice_candidate_action_blocked_count"] == 1
        and summary["source_mismatch_blocked_count"] == 3
        and summary["candidate_only_false_blocked_count"] == 1
        and summary["non_executing_false_blocked_count"] == 1
        and summary["selected_action_blocked_count"] == 1
        and summary["final_action_blocked_count"] == 1
        and summary["action_execution_blocked_count"] == 1
        and summary["direct_command_blocked_count"] == 1
        and summary["runtime_action_selection_blocked_count"] == 1
        and summary["may_enter_one_step_false_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["production_action_selection_blocked_count"] == 1
        and summary["runtime_action_selection_flag_blocked_count"] == 1
        and summary["selected_action_created_blocked_count"] == 1
        and summary["final_action_created_blocked_count"] == 1
        and summary["action_executed_blocked_count"] == 1
        and summary["direct_action_command_blocked_count"] == 1
        and summary["persistent_policy_written_blocked_count"] == 1
        and summary["general_behavior_changed_blocked_count"] == 1
        and summary["semantic_or_fuzzy_match_used_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "non_executing_action_choice_candidate_enabled": True,
        "choice_candidate_action": EXPECTED_ACTION,
        "candidate_only": True,
        "non_executing": True,
        "selected_action_added": False,
        "runtime_action_selection_added": False,
        "final_action_creation_added": False,
        "action_execution_added": False,
        "direct_action_command_added": False,
        "persistent_policy_write_added": False,
        "general_behavior_change_added": False,
        "semantic_or_fuzzy_matching_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "top_level_field_count": len(REQUIRED_FIELDS),
    }


def _blocked_flag_values(blocked_flags: dict[str, Any]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_errors(validation_results: list[dict[str, Any]], error_codes: set[str]) -> int:
    return sum(1 for result in validation_results if any(error in result["error_codes"] for error in error_codes))
