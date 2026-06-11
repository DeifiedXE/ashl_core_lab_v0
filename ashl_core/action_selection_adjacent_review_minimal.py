"""Action-selection-adjacent review for gated pre-action candidates."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .pre_action_consideration_candidate_minimal import EXPECTED_MAPPING
from .pre_action_consideration_gate_check_minimal import (
    build_pre_action_consideration_gate_result,
)


COMMAND = "run-action-selection-adjacent-review-minimal-check"
FLOW = "action_selection_adjacent_review_minimal_v0"
REVIEW_MODE = "action_selection_adjacent_review_only"
REVIEW_PRIORITY = [
    "check_before_retry",
    "slow_down_or_reduce_cost",
    "ask_for_help",
    "retry_same_action",
]

REQUIRED_FIELDS = {
    "review_id",
    "source_pre_action_gate_result_id",
    "review_mode",
    "review_items",
    "review_summary",
    "allowed_next_layer",
    "human_summary",
    "blocked_flags",
}

REQUIRED_REVIEW_SUMMARY = {
    "review_item_count",
    "most_review_worthy_candidate",
    "reason",
    "selection_made",
    "final_action_created",
}

REQUIRED_ALLOWED_NEXT_LAYER = {
    "may_enter_non_executing_action_choice_candidate",
    "may_enter_runtime_action_selection",
    "may_create_final_action",
    "may_execute_action",
    "may_create_direct_command",
    "may_write_persistent_policy",
}

REQUIRED_HUMAN_SUMMARY = {
    "what_was_reviewed",
    "most_review_worthy",
    "what_is_blocked",
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


def build_action_selection_adjacent_review(gate_result: dict[str, Any] | None = None) -> dict[str, Any]:
    source = gate_result or build_pre_action_consideration_gate_result()
    review_items = [_review_item(candidate) for candidate in source.get("gated_candidates", [])]
    most_review_worthy = _most_review_worthy_candidate(review_items)
    return {
        "review_id": "action_selection_adjacent_review_demo_001",
        "source_pre_action_gate_result_id": source.get(
            "pre_action_gate_result_id",
            "pre_action_consideration_gate_demo_001",
        ),
        "review_mode": REVIEW_MODE,
        "review_items": review_items,
        "review_summary": {
            "review_item_count": len(review_items),
            "most_review_worthy_candidate": most_review_worthy,
            "reason": "check_before_retry is the first deterministic review priority and passed all pre-action gates.",
            "selection_made": False,
            "final_action_created": False,
        },
        "allowed_next_layer": {
            "may_enter_non_executing_action_choice_candidate": True,
            "may_enter_runtime_action_selection": False,
            "may_create_final_action": False,
            "may_execute_action": False,
            "may_create_direct_command": False,
            "may_write_persistent_policy": False,
        },
        "human_summary": {
            "what_was_reviewed": "Three gated pre-action candidates were organized for action-selection-adjacent review.",
            "most_review_worthy": "check_before_retry is highlighted as the most review-worthy candidate, but it is not selected.",
            "what_is_blocked": "Runtime action selection, final actions, execution, direct commands, and persistent policy remain blocked.",
            "plain_result": "The system can review which action candidate looks most worth considering, but still cannot choose or execute an action.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_action_selection_adjacent_review(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)
    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if record.get("review_mode") != REVIEW_MODE:
        errors.append("review_mode_not_action_selection_adjacent_review_only")

    review_items = record.get("review_items")
    if not isinstance(review_items, list):
        errors.append("review_items_missing_or_not_list")
        review_items = []
    if len(review_items) != 3:
        errors.append("review_items_length_not_three")
    item_validations = [_validate_review_item(item) for item in review_items]
    for validation in item_validations:
        errors.extend(validation["error_codes"])

    review_summary = _section(record, "review_summary", errors)
    _require_section_fields("review_summary", review_summary, REQUIRED_REVIEW_SUMMARY, errors)
    if review_summary.get("review_item_count") != 3:
        errors.append("review_item_count_not_three")
    if review_summary.get("most_review_worthy_candidate") != "check_before_retry":
        errors.append("most_review_worthy_candidate_not_check_before_retry")
    if not isinstance(review_summary.get("reason"), str) or not review_summary.get("reason"):
        errors.append("review_summary_reason_empty_or_not_string")
    if review_summary.get("selection_made") is not False:
        errors.append("selection_made_not_false")
    if review_summary.get("final_action_created") is not False:
        errors.append("final_action_created_not_false")

    allowed_next = _section(record, "allowed_next_layer", errors)
    _require_section_fields("allowed_next_layer", allowed_next, REQUIRED_ALLOWED_NEXT_LAYER, errors)
    _require_true(allowed_next, "may_enter_non_executing_action_choice_candidate", errors)
    _require_false(allowed_next, "may_enter_runtime_action_selection", errors)
    _require_false(allowed_next, "may_create_final_action", errors)
    _require_false(allowed_next, "may_execute_action", errors)
    _require_false(allowed_next, "may_create_direct_command", errors)
    _require_false(allowed_next, "may_write_persistent_policy", errors)

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
        "review_id": record.get("review_id"),
        "valid": not errors,
        "error_codes": errors,
        "review_item_count": len(review_items),
        "review_only_item_count": sum(1 for result in item_validations if result["review_only"]),
        "not_selected_action_item_count": sum(1 for result in item_validations if result["not_selected_action"]),
        "not_final_action_item_count": sum(1 for result in item_validations if result["not_final_action"]),
        "not_action_execution_item_count": sum(1 for result in item_validations if result["not_action_execution"]),
        "most_review_worthy_candidate": review_summary.get("most_review_worthy_candidate") == "check_before_retry",
        "may_enter_non_executing_action_choice_candidate": (
            allowed_next.get("may_enter_non_executing_action_choice_candidate") is True
        ),
        "runtime_action_selection_blocked": allowed_next.get("may_enter_runtime_action_selection") is False,
        "final_action_blocked": allowed_next.get("may_create_final_action") is False,
        "action_execution_blocked": allowed_next.get("may_execute_action") is False,
        "direct_command_blocked": allowed_next.get("may_create_direct_command") is False,
        "persistent_policy_blocked": allowed_next.get("may_write_persistent_policy") is False,
        "obstacle_review_pass_count": _item_pass_count(item_validations, "obstacle_retry_failed_same_state"),
        "costly_retry_review_pass_count": _item_pass_count(item_validations, "costly_retry_same_state"),
        "unclear_failure_review_pass_count": _item_pass_count(item_validations, "unclear_failure_same_state"),
        **_blocked_flag_values(blocked_flags),
    }


def run_action_selection_adjacent_review_minimal_check() -> dict[str, Any]:
    valid_review = build_action_selection_adjacent_review()
    records = [
        valid_review,
        *_invalid_demo_records(valid_review),
    ]
    validation_results = [validate_action_selection_adjacent_review(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "action_selection_adjacent_reviews": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Review can organize candidates for future selection, but review is not selection.",
            "The most review-worthy candidate is a review highlight only.",
            "Runtime action selection, selected actions, final actions, execution, direct commands, and persistent policy remain blocked.",
        ],
    }


def _review_item(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario_id": candidate["scenario_id"],
        "exact_key": candidate["exact_key"],
        "reviewed_action": candidate["considered_action"],
        "review_reason": "Candidate passed pre-action gate and came from bounded positive runtime tendency delta.",
        "memory_influence_present": True,
        "safety_envelope_covered": True,
        "rollback_ready": True,
        "mentor_override_ready": True,
        "review_only": True,
        "selected_action": False,
        "final_action": False,
        "action_execution": False,
    }


def _most_review_worthy_candidate(review_items: list[dict[str, Any]]) -> str:
    reviewed_actions = {item.get("reviewed_action") for item in review_items}
    for action in REVIEW_PRIORITY:
        if action in reviewed_actions:
            return action
    return ""


def _validate_review_item(item: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(item, dict):
        return _review_item_validation_result("", "", "", False, False, False, False, errors + ["review_item_not_dict"])

    scenario_id = item.get("scenario_id")
    exact_key = item.get("exact_key")
    expected = EXPECTED_MAPPING.get(scenario_id)
    scenario_valid = expected is not None
    if not scenario_valid:
        errors.append("unknown_scenario_id")
    if exact_key not in {value[0] for value in EXPECTED_MAPPING.values()}:
        errors.append("unknown_exact_key")
    if expected is not None and exact_key != expected[0]:
        errors.append("scenario_exact_key_mismatch")

    reviewed_action = item.get("reviewed_action")
    if expected is not None and reviewed_action != expected[1]:
        errors.append(f"{scenario_id}_wrong_reviewed_action")

    if not isinstance(item.get("review_reason"), str) or not item.get("review_reason"):
        errors.append("review_reason_empty_or_not_string")
    for field in ("memory_influence_present", "safety_envelope_covered", "rollback_ready", "mentor_override_ready", "review_only"):
        if item.get(field) is not True:
            errors.append(f"{field}_not_true")
    if item.get("selected_action") is not False:
        errors.append("selected_action_not_false")
    if item.get("final_action") is not False:
        errors.append("final_action_not_false")
    if item.get("action_execution") is not False:
        errors.append("action_execution_not_false")

    review_only = item.get("review_only") is True
    not_selected = item.get("selected_action") is False
    not_final = item.get("final_action") is False
    not_execution = item.get("action_execution") is False
    item_pass = bool(
        scenario_valid
        and expected is not None
        and exact_key == expected[0]
        and reviewed_action == expected[1]
        and review_only
        and not_selected
        and not_final
        and not_execution
        and not errors
    )
    return _review_item_validation_result(
        str(scenario_id or ""),
        str(exact_key or ""),
        str(reviewed_action or ""),
        review_only,
        not_selected,
        not_final,
        not_execution,
        errors,
        item_pass=item_pass,
    )


def _review_item_validation_result(
    scenario_id: str,
    exact_key: str,
    reviewed_action: str,
    review_only: bool,
    not_selected_action: bool,
    not_final_action: bool,
    not_action_execution: bool,
    errors: list[str],
    item_pass: bool = False,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "exact_key": exact_key,
        "reviewed_action": reviewed_action,
        "review_only": review_only,
        "not_selected_action": not_selected_action,
        "not_final_action": not_final_action,
        "not_action_execution": not_action_execution,
        "item_pass": item_pass,
        "error_codes": errors,
    }


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


def _invalid_demo_records(valid_review: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    bad_mode = _copy_case(valid_review, "bad_review_mode")
    bad_mode["review_mode"] = "runtime_action_selection_review"
    records.append(bad_mode)

    missing_item = _copy_case(valid_review, "missing_review_item")
    missing_item["review_items"] = missing_item["review_items"][:2]
    records.append(missing_item)

    wrong_mapping = _copy_case(valid_review, "wrong_mapping")
    wrong_mapping["review_items"][0]["reviewed_action"] = "ask_for_help"
    records.append(wrong_mapping)

    item_cases = [
        ("review_reason", "", "empty_review_reason"),
        ("memory_influence_present", False, "memory_influence_present_false"),
        ("safety_envelope_covered", False, "safety_envelope_covered_false"),
        ("rollback_ready", False, "rollback_ready_false"),
        ("mentor_override_ready", False, "mentor_override_ready_false"),
        ("review_only", False, "review_only_false"),
        ("selected_action", True, "selected_action_true"),
        ("final_action", True, "final_action_true"),
        ("action_execution", True, "action_execution_true"),
    ]
    for field, value, name in item_cases:
        invalid = _copy_case(valid_review, name)
        invalid["review_items"][0][field] = value
        records.append(invalid)

    wrong_most = _copy_case(valid_review, "wrong_most_review_worthy")
    wrong_most["review_summary"]["most_review_worthy_candidate"] = "ask_for_help"
    records.append(wrong_most)

    selection_made = _copy_case(valid_review, "selection_made_true")
    selection_made["review_summary"]["selection_made"] = True
    records.append(selection_made)

    final_created = _copy_case(valid_review, "final_action_created_true")
    final_created["review_summary"]["final_action_created"] = True
    records.append(final_created)

    allowed_next_cases = [
        ("may_enter_runtime_action_selection", True),
        ("may_create_final_action", True),
        ("may_execute_action", True),
        ("may_create_direct_command", True),
        ("may_write_persistent_policy", True),
    ]
    for field, value in allowed_next_cases:
        invalid = _copy_case(valid_review, f"{field}_{value}")
        invalid["allowed_next_layer"][field] = value
        records.append(invalid)

    empty_summary = _copy_case(valid_review, "empty_human_summary")
    empty_summary["human_summary"]["plain_result"] = ""
    records.append(empty_summary)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid = _copy_case(valid_review, flag)
        invalid["blocked_flags"][flag] = True
        records.append(invalid)

    return records


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["review_id"] = f"{record['review_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    valid_result = valid_results[0] if valid_results else {}
    summary: dict[str, int | bool] = {
        "action_selection_adjacent_review_count": len(validation_results),
        "valid_action_selection_adjacent_review_count": len(valid_results),
        "invalid_action_selection_adjacent_review_count": sum(
            1 for result in validation_results if not result["valid"]
        ),
        "review_item_count": int(valid_result.get("review_item_count", 0)),
        "review_only_item_count": int(valid_result.get("review_only_item_count", 0)),
        "not_selected_action_item_count": int(valid_result.get("not_selected_action_item_count", 0)),
        "not_final_action_item_count": int(valid_result.get("not_final_action_item_count", 0)),
        "not_action_execution_item_count": int(valid_result.get("not_action_execution_item_count", 0)),
        "most_review_worthy_candidate_count": sum(
            1 for result in valid_results if result["most_review_worthy_candidate"]
        ),
        "may_enter_non_executing_action_choice_candidate_count": sum(
            1 for result in valid_results if result["may_enter_non_executing_action_choice_candidate"]
        ),
        "runtime_action_selection_blocked_count": sum(
            1 for result in valid_results if result["runtime_action_selection_blocked"]
        ),
        "final_action_blocked_count": sum(1 for result in valid_results if result["final_action_blocked"]),
        "action_execution_blocked_count": sum(
            1 for result in valid_results if result["action_execution_blocked"]
        ),
        "direct_command_blocked_count": sum(1 for result in valid_results if result["direct_command_blocked"]),
        "persistent_policy_blocked_count": sum(
            1 for result in valid_results if result["persistent_policy_blocked"]
        ),
        "obstacle_review_pass_count": int(valid_result.get("obstacle_review_pass_count", 0)),
        "costly_retry_review_pass_count": int(valid_result.get("costly_retry_review_pass_count", 0)),
        "unclear_failure_review_pass_count": int(valid_result.get("unclear_failure_review_pass_count", 0)),
        "bad_review_mode_blocked_count": _count_error(
            validation_results,
            "review_mode_not_action_selection_adjacent_review_only",
        ),
        "missing_review_item_blocked_count": _count_error(validation_results, "review_items_length_not_three"),
        "wrong_mapping_blocked_count": _count_errors_ending(validation_results, "_wrong_reviewed_action"),
        "empty_review_reason_blocked_count": _count_error(
            validation_results,
            "review_reason_empty_or_not_string",
        ),
        "memory_influence_present_false_blocked_count": _count_error(
            validation_results,
            "memory_influence_present_not_true",
        ),
        "safety_envelope_covered_false_blocked_count": _count_error(
            validation_results,
            "safety_envelope_covered_not_true",
        ),
        "rollback_ready_false_blocked_count": _count_error(validation_results, "rollback_ready_not_true"),
        "mentor_override_ready_false_blocked_count": _count_error(
            validation_results,
            "mentor_override_ready_not_true",
        ),
        "review_only_false_blocked_count": _count_error(validation_results, "review_only_not_true"),
        "selected_action_blocked_count": _count_error(validation_results, "selected_action_not_false"),
        "final_action_blocked_item_count": _count_error(validation_results, "final_action_not_false"),
        "action_execution_blocked_item_count": _count_error(validation_results, "action_execution_not_false"),
        "wrong_most_review_worthy_candidate_blocked_count": _count_error(
            validation_results,
            "most_review_worthy_candidate_not_check_before_retry",
        ),
        "selection_made_true_blocked_count": _count_error(validation_results, "selection_made_not_false"),
        "final_action_created_true_blocked_count": _count_error(
            validation_results,
            "final_action_created_not_false",
        ),
        "may_enter_runtime_action_selection_blocked_count": _count_error(
            validation_results,
            "may_enter_runtime_action_selection_not_false",
        ),
        "may_create_final_action_blocked_count": _count_error(
            validation_results,
            "may_create_final_action_not_false",
        ),
        "may_execute_action_blocked_count": _count_error(validation_results, "may_execute_action_not_false"),
        "may_create_direct_command_blocked_count": _count_error(
            validation_results,
            "may_create_direct_command_not_false",
        ),
        "may_write_persistent_policy_blocked_count": _count_error(
            validation_results,
            "may_write_persistent_policy_not_false",
        ),
        "empty_human_summary_blocked_count": _count_error(
            validation_results,
            "plain_result_empty_or_not_string",
        ),
        "proof_of_learning_claim_blocked_count": _count_error(
            validation_results,
            "proof_of_learning_claim_enabled",
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
    }
    summary["all_action_selection_adjacent_review_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["action_selection_adjacent_review_count"] == 41
        and summary["valid_action_selection_adjacent_review_count"] == 1
        and summary["invalid_action_selection_adjacent_review_count"] == 40
        and summary["review_item_count"] == 3
        and summary["review_only_item_count"] == 3
        and summary["not_selected_action_item_count"] == 3
        and summary["not_final_action_item_count"] == 3
        and summary["not_action_execution_item_count"] == 3
        and summary["most_review_worthy_candidate_count"] == 1
        and summary["may_enter_non_executing_action_choice_candidate_count"] == 1
        and summary["runtime_action_selection_blocked_count"] == 1
        and summary["final_action_blocked_count"] == 1
        and summary["action_execution_blocked_count"] == 1
        and summary["direct_command_blocked_count"] == 1
        and summary["persistent_policy_blocked_count"] == 1
        and summary["obstacle_review_pass_count"] == 1
        and summary["costly_retry_review_pass_count"] == 1
        and summary["unclear_failure_review_pass_count"] == 1
        and summary["bad_review_mode_blocked_count"] == 1
        and summary["missing_review_item_blocked_count"] == 1
        and summary["wrong_mapping_blocked_count"] == 1
        and summary["selected_action_blocked_count"] == 1
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
        "action_selection_adjacent_review_enabled": True,
        "review_item_count": summary["review_item_count"],
        "most_review_worthy_candidate": "check_before_retry",
        "review_is_selection": False,
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


def _item_pass_count(item_validations: list[dict[str, Any]], scenario_id: str) -> int:
    return sum(1 for result in item_validations if result["scenario_id"] == scenario_id and result["item_pass"])


def _blocked_flag_values(blocked_flags: dict[str, Any]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_errors_ending(validation_results: list[dict[str, Any]], suffix: str) -> int:
    return sum(1 for result in validation_results for error in result["error_codes"] if error.endswith(suffix))
