"""One-step sandbox action intent from a non-executing choice candidate."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .non_executing_action_choice_candidate_minimal import (
    build_non_executing_action_choice_candidate,
)


COMMAND = "run-one-step-sandbox-action-intent-minimal-check"
FLOW = "one_step_sandbox_action_intent_minimal_v0"
INTENT_MODE = "one_step_sandbox_intent_only"
EXPECTED_ACTION = "check_before_retry"
EXPECTED_SANDBOX_ID = "phase0_toy_sandbox_obstacle_retry_failed"
EXPECTED_SCENARIO_ID = "obstacle_retry_failed_same_state"
EXPECTED_EXACT_KEY = "obstacle_retry_failed"

REQUIRED_FIELDS = {
    "sandbox_action_intent_id",
    "source_choice_candidate_id",
    "intent_mode",
    "intended_sandbox_action",
    "sandbox_context",
    "intent_constraints",
    "allowed_next_layer",
    "human_summary",
    "blocked_flags",
}

REQUIRED_SANDBOX_CONTEXT = {
    "sandbox_id",
    "scenario_id",
    "exact_key",
    "state_summary",
    "one_step_only",
    "production_context",
}

REQUIRED_INTENT_CONSTRAINTS = {
    "intent_only",
    "sandbox_only",
    "one_step_only",
    "non_executing",
    "selected_action",
    "final_action",
    "action_execution",
    "direct_command",
    "runtime_action_selection",
    "persistent_policy",
    "rollback_required_before_execution",
    "audit_trace_required",
    "mentor_override_available",
}

REQUIRED_ALLOWED_NEXT_LAYER = {
    "may_enter_one_step_sandbox_action_execution",
    "may_enter_production_action_selection",
    "may_create_final_action",
    "may_execute_real_action",
    "may_create_direct_command",
    "may_write_persistent_policy",
}

REQUIRED_HUMAN_SUMMARY = {
    "what_was_created",
    "why_it_was_created",
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


def build_one_step_sandbox_action_intent(
    choice_candidate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = choice_candidate or build_non_executing_action_choice_candidate()
    constraints = source.get("choice_constraints", {})
    action = source.get("choice_candidate_action", "")
    choice_source = source.get("choice_source", {})

    if not _source_candidate_allows_intent(constraints):
        action = ""

    return {
        "sandbox_action_intent_id": "one_step_sandbox_action_intent_demo_001",
        "source_choice_candidate_id": source.get(
            "choice_candidate_id",
            "non_executing_action_choice_candidate_demo_001",
        ),
        "intent_mode": INTENT_MODE,
        "intended_sandbox_action": action,
        "sandbox_context": {
            "sandbox_id": EXPECTED_SANDBOX_ID,
            "scenario_id": choice_source.get("source_scenario_id", EXPECTED_SCENARIO_ID),
            "exact_key": choice_source.get("source_exact_key", EXPECTED_EXACT_KEY),
            "state_summary": (
                "Controlled sandbox state where retrying directly previously failed because of an obstacle."
            ),
            "one_step_only": True,
            "production_context": False,
        },
        "intent_constraints": {
            "intent_only": True,
            "sandbox_only": True,
            "one_step_only": True,
            "non_executing": True,
            "selected_action": False,
            "final_action": False,
            "action_execution": False,
            "direct_command": False,
            "runtime_action_selection": False,
            "persistent_policy": False,
            "rollback_required_before_execution": True,
            "audit_trace_required": True,
            "mentor_override_available": True,
        },
        "allowed_next_layer": {
            "may_enter_one_step_sandbox_action_execution": True,
            "may_enter_production_action_selection": False,
            "may_create_final_action": False,
            "may_execute_real_action": False,
            "may_create_direct_command": False,
            "may_write_persistent_policy": False,
        },
        "human_summary": {
            "what_was_created": "A one-step sandbox intent was created for check_before_retry.",
            "why_it_was_created": "The action was the non-executing choice candidate from the review chain.",
            "what_it_is_not": "It is not a selected action, final action, command, or execution.",
            "plain_result": "The system can prepare one sandbox-only action intent, but still cannot execute any action.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_one_step_sandbox_action_intent(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)
    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if record.get("intent_mode") != INTENT_MODE:
        errors.append("intent_mode_not_one_step_sandbox_intent_only")
    if record.get("intended_sandbox_action") != EXPECTED_ACTION:
        errors.append("intended_sandbox_action_not_check_before_retry")

    sandbox_context = _section(record, "sandbox_context", errors)
    _require_section_fields("sandbox_context", sandbox_context, REQUIRED_SANDBOX_CONTEXT, errors)
    if sandbox_context.get("sandbox_id") != EXPECTED_SANDBOX_ID:
        errors.append("sandbox_id_not_phase0_toy_sandbox_obstacle_retry_failed")
    if sandbox_context.get("scenario_id") != EXPECTED_SCENARIO_ID:
        errors.append("scenario_id_not_obstacle_retry_failed_same_state")
    if sandbox_context.get("exact_key") != EXPECTED_EXACT_KEY:
        errors.append("exact_key_not_obstacle_retry_failed")
    if not isinstance(sandbox_context.get("state_summary"), str) or not sandbox_context.get("state_summary"):
        errors.append("state_summary_empty_or_not_string")
    _require_true(sandbox_context, "one_step_only", errors)
    _require_false(sandbox_context, "production_context", errors)

    constraints = _section(record, "intent_constraints", errors)
    _require_section_fields("intent_constraints", constraints, REQUIRED_INTENT_CONSTRAINTS, errors)
    for field in (
        "intent_only",
        "sandbox_only",
        "one_step_only",
        "non_executing",
        "rollback_required_before_execution",
        "audit_trace_required",
        "mentor_override_available",
    ):
        _require_true(constraints, field, errors)
    for field in (
        "selected_action",
        "final_action",
        "action_execution",
        "direct_command",
        "runtime_action_selection",
        "persistent_policy",
    ):
        _require_false(constraints, field, errors)

    allowed_next = _section(record, "allowed_next_layer", errors)
    _require_section_fields("allowed_next_layer", allowed_next, REQUIRED_ALLOWED_NEXT_LAYER, errors)
    _require_true(allowed_next, "may_enter_one_step_sandbox_action_execution", errors)
    for field in (
        "may_enter_production_action_selection",
        "may_create_final_action",
        "may_execute_real_action",
        "may_create_direct_command",
        "may_write_persistent_policy",
    ):
        _require_false(allowed_next, field, errors)

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
        "sandbox_action_intent_id": record.get("sandbox_action_intent_id"),
        "valid": not errors,
        "error_codes": errors,
        "intent_action": record.get("intended_sandbox_action") == EXPECTED_ACTION,
        "intent_only": constraints.get("intent_only") is True,
        "sandbox_only": constraints.get("sandbox_only") is True,
        "one_step_only": constraints.get("one_step_only") is True and sandbox_context.get("one_step_only") is True,
        "non_executing": constraints.get("non_executing") is True,
        "not_selected_action": constraints.get("selected_action") is False,
        "not_final_action": constraints.get("final_action") is False,
        "not_action_execution": constraints.get("action_execution") is False,
        "not_direct_command": constraints.get("direct_command") is False,
        "not_runtime_action_selection": constraints.get("runtime_action_selection") is False,
        "rollback_required": constraints.get("rollback_required_before_execution") is True,
        "audit_trace_required": constraints.get("audit_trace_required") is True,
        "mentor_override_available": constraints.get("mentor_override_available") is True,
        "may_enter_one_step_sandbox_action_execution": (
            allowed_next.get("may_enter_one_step_sandbox_action_execution") is True
        ),
        **_blocked_flag_values(blocked_flags),
    }


def run_one_step_sandbox_action_intent_minimal_check() -> dict[str, Any]:
    valid_intent = build_one_step_sandbox_action_intent()
    records = [
        valid_intent,
        *_invalid_demo_records(valid_intent),
    ]
    validation_results = [validate_one_step_sandbox_action_intent(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "one_step_sandbox_action_intents": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Intent may say prepare to do this one sandbox step, but intent is not execution.",
            "One-step sandbox execution may be considered later only with rollback, audit, and mentor override.",
            "Production action selection, final actions, direct commands, persistent policy, and proof claims remain blocked.",
        ],
    }


def _source_candidate_allows_intent(constraints: dict[str, Any]) -> bool:
    return (
        constraints.get("candidate_only") is True
        and constraints.get("non_executing") is True
        and constraints.get("selected_action") is False
        and constraints.get("final_action") is False
        and constraints.get("action_execution") is False
        and constraints.get("direct_command") is False
        and constraints.get("runtime_action_selection") is False
        and constraints.get("may_enter_one_step_sandbox_action_intent") is True
    )


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


def _invalid_demo_records(valid_intent: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    top_level_cases = [
        ("intent_mode", "production_action_intent", "bad_intent_mode"),
        ("intended_sandbox_action", "ask_for_help", "wrong_intended_sandbox_action"),
    ]
    for field, value, name in top_level_cases:
        invalid = _copy_case(valid_intent, name)
        invalid[field] = value
        records.append(invalid)

    sandbox_cases = [
        ("sandbox_id", "production_sandbox", "wrong_sandbox_id"),
        ("scenario_id", "unclear_failure_same_state", "wrong_scenario_id"),
        ("exact_key", "unclear_failure_repeated", "wrong_exact_key"),
        ("state_summary", "", "empty_state_summary"),
        ("one_step_only", False, "sandbox_one_step_false"),
        ("production_context", True, "production_context_true"),
    ]
    for field, value, name in sandbox_cases:
        invalid = _copy_case(valid_intent, name)
        invalid["sandbox_context"][field] = value
        records.append(invalid)

    constraint_cases = [
        ("intent_only", False),
        ("sandbox_only", False),
        ("one_step_only", False),
        ("non_executing", False),
        ("selected_action", True),
        ("final_action", True),
        ("action_execution", True),
        ("direct_command", True),
        ("runtime_action_selection", True),
        ("persistent_policy", True),
        ("rollback_required_before_execution", False),
        ("audit_trace_required", False),
        ("mentor_override_available", False),
    ]
    for field, value in constraint_cases:
        invalid = _copy_case(valid_intent, f"{field}_{value}")
        invalid["intent_constraints"][field] = value
        records.append(invalid)

    allowed_cases = [
        ("may_enter_one_step_sandbox_action_execution", False),
        ("may_enter_production_action_selection", True),
        ("may_create_final_action", True),
        ("may_execute_real_action", True),
        ("may_create_direct_command", True),
        ("may_write_persistent_policy", True),
    ]
    for field, value in allowed_cases:
        invalid = _copy_case(valid_intent, f"{field}_{value}")
        invalid["allowed_next_layer"][field] = value
        records.append(invalid)

    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        invalid = _copy_case(valid_intent, f"empty_{field}")
        invalid["human_summary"][field] = ""
        records.append(invalid)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid = _copy_case(valid_intent, flag)
        invalid["blocked_flags"][flag] = True
        records.append(invalid)

    return records


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["sandbox_action_intent_id"] = f"{record['sandbox_action_intent_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "sandbox_action_intent_result_count": len(validation_results),
        "valid_sandbox_action_intent_result_count": len(valid_results),
        "invalid_sandbox_action_intent_result_count": sum(
            1 for result in validation_results if not result["valid"]
        ),
        "intent_action_count": sum(1 for result in valid_results if result["intent_action"]),
        "intent_only_count": sum(1 for result in valid_results if result["intent_only"]),
        "sandbox_only_count": sum(1 for result in valid_results if result["sandbox_only"]),
        "one_step_only_count": sum(1 for result in valid_results if result["one_step_only"]),
        "non_executing_count": sum(1 for result in valid_results if result["non_executing"]),
        "not_selected_action_count": sum(1 for result in valid_results if result["not_selected_action"]),
        "not_final_action_count": sum(1 for result in valid_results if result["not_final_action"]),
        "not_action_execution_count": sum(1 for result in valid_results if result["not_action_execution"]),
        "not_direct_command_count": sum(1 for result in valid_results if result["not_direct_command"]),
        "not_runtime_action_selection_count": sum(
            1 for result in valid_results if result["not_runtime_action_selection"]
        ),
        "rollback_required_count": sum(1 for result in valid_results if result["rollback_required"]),
        "audit_trace_required_count": sum(1 for result in valid_results if result["audit_trace_required"]),
        "mentor_override_available_count": sum(
            1 for result in valid_results if result["mentor_override_available"]
        ),
        "may_enter_one_step_sandbox_action_execution_count": sum(
            1 for result in valid_results if result["may_enter_one_step_sandbox_action_execution"]
        ),
        "bad_intent_mode_blocked_count": _count_error(
            validation_results,
            "intent_mode_not_one_step_sandbox_intent_only",
        ),
        "wrong_intended_sandbox_action_blocked_count": _count_error(
            validation_results,
            "intended_sandbox_action_not_check_before_retry",
        ),
        "wrong_sandbox_context_blocked_count": _count_errors(
            validation_results,
            {
                "sandbox_id_not_phase0_toy_sandbox_obstacle_retry_failed",
                "scenario_id_not_obstacle_retry_failed_same_state",
                "exact_key_not_obstacle_retry_failed",
            },
        ),
        "production_context_blocked_count": _count_error(validation_results, "production_context_not_false"),
        "selected_action_blocked_count": _count_error(validation_results, "selected_action_not_false"),
        "final_action_blocked_count": _count_error(validation_results, "final_action_not_false"),
        "action_execution_blocked_count": _count_error(validation_results, "action_execution_not_false"),
        "direct_command_blocked_count": _count_error(validation_results, "direct_command_not_false"),
        "runtime_action_selection_blocked_count": _count_error(
            validation_results,
            "runtime_action_selection_not_false",
        ),
        "persistent_policy_blocked_count": _count_error(validation_results, "persistent_policy_not_false"),
        "missing_rollback_audit_mentor_blocked_count": _count_errors(
            validation_results,
            {
                "rollback_required_before_execution_not_true",
                "audit_trace_required_not_true",
                "mentor_override_available_not_true",
            },
        ),
        "may_enter_execution_false_blocked_count": _count_error(
            validation_results,
            "may_enter_one_step_sandbox_action_execution_not_true",
        ),
        "may_enter_production_action_selection_blocked_count": _count_error(
            validation_results,
            "may_enter_production_action_selection_not_false",
        ),
        "may_create_final_action_blocked_count": _count_error(
            validation_results,
            "may_create_final_action_not_false",
        ),
        "may_execute_real_action_blocked_count": _count_error(
            validation_results,
            "may_execute_real_action_not_false",
        ),
        "may_create_direct_command_blocked_count": _count_error(
            validation_results,
            "may_create_direct_command_not_false",
        ),
        "may_write_persistent_policy_blocked_count": _count_error(
            validation_results,
            "may_write_persistent_policy_not_false",
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
    }
    summary["all_one_step_sandbox_action_intent_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["sandbox_action_intent_result_count"] == 51
        and summary["valid_sandbox_action_intent_result_count"] == 1
        and summary["invalid_sandbox_action_intent_result_count"] == 50
        and summary["intent_action_count"] == 1
        and summary["intent_only_count"] == 1
        and summary["sandbox_only_count"] == 1
        and summary["one_step_only_count"] == 1
        and summary["non_executing_count"] == 1
        and summary["not_selected_action_count"] == 1
        and summary["not_final_action_count"] == 1
        and summary["not_action_execution_count"] == 1
        and summary["not_direct_command_count"] == 1
        and summary["not_runtime_action_selection_count"] == 1
        and summary["rollback_required_count"] == 1
        and summary["audit_trace_required_count"] == 1
        and summary["mentor_override_available_count"] == 1
        and summary["may_enter_one_step_sandbox_action_execution_count"] == 1
        and summary["bad_intent_mode_blocked_count"] == 1
        and summary["wrong_intended_sandbox_action_blocked_count"] == 1
        and summary["wrong_sandbox_context_blocked_count"] == 3
        and summary["production_context_blocked_count"] == 1
        and summary["selected_action_blocked_count"] == 1
        and summary["final_action_blocked_count"] == 1
        and summary["action_execution_blocked_count"] == 1
        and summary["direct_command_blocked_count"] == 1
        and summary["runtime_action_selection_blocked_count"] == 1
        and summary["persistent_policy_blocked_count"] == 1
        and summary["missing_rollback_audit_mentor_blocked_count"] == 3
        and summary["may_enter_execution_false_blocked_count"] == 1
        and summary["may_enter_production_action_selection_blocked_count"] == 1
        and summary["may_create_final_action_blocked_count"] == 1
        and summary["may_execute_real_action_blocked_count"] == 1
        and summary["may_create_direct_command_blocked_count"] == 1
        and summary["may_write_persistent_policy_blocked_count"] == 1
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
        and summary["proof_of_learning_claim_blocked_count"] == 1
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "one_step_sandbox_action_intent_enabled": True,
        "intended_sandbox_action": EXPECTED_ACTION,
        "sandbox_id": EXPECTED_SANDBOX_ID,
        "intent_only": True,
        "sandbox_only": True,
        "one_step_only": True,
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
