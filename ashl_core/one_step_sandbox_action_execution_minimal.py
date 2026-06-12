"""One-step sandbox-only action execution from sandbox intent."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .one_step_sandbox_action_intent_minimal import (
    build_one_step_sandbox_action_intent,
)


COMMAND = "run-one-step-sandbox-action-execution-minimal-check"
FLOW = "one_step_sandbox_action_execution_minimal_v0"
EXECUTION_MODE = "one_step_sandbox_execution_only"
EXPECTED_ACTION = "check_before_retry"
EXPECTED_SANDBOX_ID = "phase0_toy_sandbox_obstacle_retry_failed"
EXPECTED_SCENARIO_ID = "obstacle_retry_failed_same_state"
EXPECTED_EXACT_KEY = "obstacle_retry_failed"

REQUIRED_FIELDS = {
    "sandbox_execution_id",
    "source_sandbox_action_intent_id",
    "execution_mode",
    "executed_sandbox_action",
    "sandbox_before",
    "sandbox_after",
    "execution_outcome",
    "audit_trace",
    "rollback_record",
    "human_summary",
    "blocked_flags",
}

REQUIRED_SANDBOX_BEFORE = {
    "sandbox_id",
    "scenario_id",
    "exact_key",
    "obstacle_ahead",
    "previous_action_failed",
    "previous_failure_reason",
    "production_context",
}

REQUIRED_SANDBOX_AFTER = {
    "sandbox_id",
    "checked_before_retry",
    "obstacle_detected",
    "retry_same_action_executed",
    "movement_executed",
    "production_context",
}

REQUIRED_EXECUTION_OUTCOME = {
    "sandbox_action_executed",
    "executed_once",
    "outcome_type",
    "outcome_summary",
    "real_world_effect",
    "production_effect",
    "state_mutation_scope",
}

REQUIRED_AUDIT_TRACE = {
    "audit_trace_required",
    "audit_trace_recorded",
    "source_intent_checked",
    "execution_boundary_checked",
    "blocked_flags_checked",
}

REQUIRED_ROLLBACK_RECORD = {
    "rollback_available",
    "rollback_required_before_execution",
    "rollback_scope",
    "rollback_result",
}

REQUIRED_HUMAN_SUMMARY = {
    "what_executed",
    "what_happened",
    "what_did_not_happen",
    "plain_result",
}

REQUIRED_BLOCKED_FLAGS = {
    "production_action_selection",
    "runtime_action_selection",
    "selected_action_created",
    "final_action_created",
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


def build_one_step_sandbox_action_execution(
    intent: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = intent or build_one_step_sandbox_action_intent()
    action = source.get("intended_sandbox_action", "")
    context = source.get("sandbox_context", {})

    if not _source_intent_allows_execution(source):
        action = ""

    return {
        "sandbox_execution_id": "one_step_sandbox_action_execution_demo_001",
        "source_sandbox_action_intent_id": source.get(
            "sandbox_action_intent_id",
            "one_step_sandbox_action_intent_demo_001",
        ),
        "execution_mode": EXECUTION_MODE,
        "executed_sandbox_action": action,
        "sandbox_before": {
            "sandbox_id": context.get("sandbox_id", EXPECTED_SANDBOX_ID),
            "scenario_id": context.get("scenario_id", EXPECTED_SCENARIO_ID),
            "exact_key": context.get("exact_key", EXPECTED_EXACT_KEY),
            "obstacle_ahead": True,
            "previous_action_failed": True,
            "previous_failure_reason": "blocked_by_obstacle",
            "production_context": False,
        },
        "sandbox_after": {
            "sandbox_id": context.get("sandbox_id", EXPECTED_SANDBOX_ID),
            "checked_before_retry": True,
            "obstacle_detected": True,
            "retry_same_action_executed": False,
            "movement_executed": False,
            "production_context": False,
        },
        "execution_outcome": {
            "sandbox_action_executed": True,
            "executed_once": True,
            "outcome_type": "sandbox_check_result",
            "outcome_summary": "The sandbox check detected the obstacle before retrying.",
            "real_world_effect": False,
            "production_effect": False,
            "state_mutation_scope": "sandbox_record_only",
        },
        "audit_trace": {
            "audit_trace_required": True,
            "audit_trace_recorded": True,
            "source_intent_checked": True,
            "execution_boundary_checked": True,
            "blocked_flags_checked": True,
        },
        "rollback_record": {
            "rollback_available": True,
            "rollback_required_before_execution": True,
            "rollback_scope": "sandbox_record_only",
            "rollback_result": "no_persistent_state_to_restore",
        },
        "human_summary": {
            "what_executed": "The toy sandbox executed check_before_retry once.",
            "what_happened": "The sandbox check detected an obstacle before retrying.",
            "what_did_not_happen": (
                "No real movement, final action, direct command, production behavior, or persistent policy was created."
            ),
            "plain_result": "The system executed one controlled sandbox-only check action and recorded the outcome.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_one_step_sandbox_action_execution(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)
    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if record.get("execution_mode") != EXECUTION_MODE:
        errors.append("execution_mode_not_one_step_sandbox_execution_only")
    if record.get("executed_sandbox_action") != EXPECTED_ACTION:
        errors.append("executed_sandbox_action_not_check_before_retry")

    before = _section(record, "sandbox_before", errors)
    _require_section_fields("sandbox_before", before, REQUIRED_SANDBOX_BEFORE, errors)
    if before.get("sandbox_id") != EXPECTED_SANDBOX_ID:
        errors.append("sandbox_before_sandbox_id_not_phase0_toy_sandbox_obstacle_retry_failed")
    if before.get("scenario_id") != EXPECTED_SCENARIO_ID:
        errors.append("scenario_id_not_obstacle_retry_failed_same_state")
    if before.get("exact_key") != EXPECTED_EXACT_KEY:
        errors.append("exact_key_not_obstacle_retry_failed")
    _require_true(before, "obstacle_ahead", errors)
    _require_true(before, "previous_action_failed", errors)
    if before.get("previous_failure_reason") != "blocked_by_obstacle":
        errors.append("previous_failure_reason_not_blocked_by_obstacle")
    _require_false(before, "production_context", errors)

    after = _section(record, "sandbox_after", errors)
    _require_section_fields("sandbox_after", after, REQUIRED_SANDBOX_AFTER, errors)
    if after.get("sandbox_id") != EXPECTED_SANDBOX_ID:
        errors.append("sandbox_after_sandbox_id_not_phase0_toy_sandbox_obstacle_retry_failed")
    _require_true(after, "checked_before_retry", errors)
    _require_true(after, "obstacle_detected", errors)
    _require_false(after, "retry_same_action_executed", errors)
    _require_false(after, "movement_executed", errors)
    _require_false(after, "production_context", errors)

    outcome = _section(record, "execution_outcome", errors)
    _require_section_fields("execution_outcome", outcome, REQUIRED_EXECUTION_OUTCOME, errors)
    _require_true(outcome, "sandbox_action_executed", errors)
    _require_true(outcome, "executed_once", errors)
    if outcome.get("outcome_type") != "sandbox_check_result":
        errors.append("outcome_type_not_sandbox_check_result")
    if not isinstance(outcome.get("outcome_summary"), str) or not outcome.get("outcome_summary"):
        errors.append("outcome_summary_empty_or_not_string")
    _require_false(outcome, "real_world_effect", errors)
    _require_false(outcome, "production_effect", errors)
    if outcome.get("state_mutation_scope") != "sandbox_record_only":
        errors.append("state_mutation_scope_not_sandbox_record_only")

    audit = _section(record, "audit_trace", errors)
    _require_section_fields("audit_trace", audit, REQUIRED_AUDIT_TRACE, errors)
    for field in sorted(REQUIRED_AUDIT_TRACE):
        _require_true(audit, field, errors)

    rollback = _section(record, "rollback_record", errors)
    _require_section_fields("rollback_record", rollback, REQUIRED_ROLLBACK_RECORD, errors)
    _require_true(rollback, "rollback_available", errors)
    _require_true(rollback, "rollback_required_before_execution", errors)
    if rollback.get("rollback_scope") != "sandbox_record_only":
        errors.append("rollback_scope_not_sandbox_record_only")
    if not isinstance(rollback.get("rollback_result"), str) or not rollback.get("rollback_result"):
        errors.append("rollback_result_empty_or_not_string")

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
        "sandbox_execution_id": record.get("sandbox_execution_id"),
        "valid": not errors,
        "error_codes": errors,
        "sandbox_action_executed": outcome.get("sandbox_action_executed") is True,
        "executed_once": outcome.get("executed_once") is True,
        "check_before_retry_executed": record.get("executed_sandbox_action") == EXPECTED_ACTION,
        "obstacle_detected": after.get("obstacle_detected") is True,
        "real_world_effect_blocked": outcome.get("real_world_effect") is False,
        "production_effect_blocked": outcome.get("production_effect") is False,
        "movement_executed_blocked": after.get("movement_executed") is False,
        "retry_same_action_executed_blocked": after.get("retry_same_action_executed") is False,
        "audit_trace_recorded": audit.get("audit_trace_recorded") is True,
        "rollback_available": rollback.get("rollback_available") is True,
        "sandbox_record_only": (
            outcome.get("state_mutation_scope") == "sandbox_record_only"
            and rollback.get("rollback_scope") == "sandbox_record_only"
        ),
        **_blocked_flag_values(blocked_flags),
    }


def run_one_step_sandbox_action_execution_minimal_check() -> dict[str, Any]:
    valid_execution = build_one_step_sandbox_action_execution()
    records = [
        valid_execution,
        *_invalid_demo_records(valid_execution),
    ]
    validation_results = [validate_one_step_sandbox_action_execution(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "one_step_sandbox_action_executions": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "A sandbox action may execute once inside a controlled toy sandbox, but it must not escape into production behavior.",
            "There is no final_action field, no selected_action field, and no direct command.",
            "The only true execution flag is sandbox_action_executed inside execution_outcome.",
        ],
    }


def _source_intent_allows_execution(source: dict[str, Any]) -> bool:
    constraints = source.get("intent_constraints", {})
    allowed_next = source.get("allowed_next_layer", {})
    return (
        source.get("intent_mode") == "one_step_sandbox_intent_only"
        and source.get("intended_sandbox_action") == EXPECTED_ACTION
        and constraints.get("sandbox_only") is True
        and constraints.get("one_step_only") is True
        and constraints.get("rollback_required_before_execution") is True
        and constraints.get("audit_trace_required") is True
        and constraints.get("mentor_override_available") is True
        and allowed_next.get("may_enter_one_step_sandbox_action_execution") is True
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


def _invalid_demo_records(valid_execution: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for field, value, name in [
        ("execution_mode", "production_execution", "bad_execution_mode"),
        ("executed_sandbox_action", "retry_same_action", "wrong_executed_sandbox_action"),
    ]:
        invalid = _copy_case(valid_execution, name)
        invalid[field] = value
        records.append(invalid)

    before_cases = [
        ("sandbox_id", "production_sandbox", "wrong_sandbox_id"),
        ("scenario_id", "unclear_failure_same_state", "wrong_scenario_id"),
        ("exact_key", "unclear_failure_repeated", "wrong_exact_key"),
        ("obstacle_ahead", False, "obstacle_ahead_false"),
        ("previous_action_failed", False, "previous_action_failed_false"),
        ("previous_failure_reason", "unknown", "wrong_previous_failure_reason"),
        ("production_context", True, "production_context_true"),
    ]
    for field, value, name in before_cases:
        invalid = _copy_case(valid_execution, name)
        invalid["sandbox_before"][field] = value
        records.append(invalid)

    after_cases = [
        ("checked_before_retry", False),
        ("obstacle_detected", False),
        ("retry_same_action_executed", True),
        ("movement_executed", True),
    ]
    for field, value in after_cases:
        invalid = _copy_case(valid_execution, f"{field}_{value}")
        invalid["sandbox_after"][field] = value
        records.append(invalid)

    outcome_cases = [
        ("sandbox_action_executed", False),
        ("executed_once", False),
        ("outcome_type", "production_action_result"),
        ("outcome_summary", ""),
        ("real_world_effect", True),
        ("production_effect", True),
        ("state_mutation_scope", "persistent_policy"),
    ]
    for field, value in outcome_cases:
        invalid = _copy_case(valid_execution, f"{field}_{value}")
        invalid["execution_outcome"][field] = value
        records.append(invalid)

    for field in sorted(REQUIRED_AUDIT_TRACE):
        invalid = _copy_case(valid_execution, f"{field}_false")
        invalid["audit_trace"][field] = False
        records.append(invalid)

    rollback_cases = [
        ("rollback_available", False),
        ("rollback_required_before_execution", False),
        ("rollback_scope", "persistent_state"),
        ("rollback_result", ""),
    ]
    for field, value in rollback_cases:
        invalid = _copy_case(valid_execution, f"{field}_{value}")
        invalid["rollback_record"][field] = value
        records.append(invalid)

    for field in ("what_executed", "what_did_not_happen", "plain_result"):
        invalid = _copy_case(valid_execution, f"empty_{field}")
        invalid["human_summary"][field] = ""
        records.append(invalid)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid = _copy_case(valid_execution, flag)
        invalid["blocked_flags"][flag] = True
        records.append(invalid)

    return records


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["sandbox_execution_id"] = f"{record['sandbox_execution_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "sandbox_execution_result_count": len(validation_results),
        "valid_sandbox_execution_result_count": len(valid_results),
        "invalid_sandbox_execution_result_count": sum(1 for result in validation_results if not result["valid"]),
        "sandbox_action_executed_count": sum(1 for result in valid_results if result["sandbox_action_executed"]),
        "executed_once_count": sum(1 for result in valid_results if result["executed_once"]),
        "check_before_retry_executed_count": sum(
            1 for result in valid_results if result["check_before_retry_executed"]
        ),
        "obstacle_detected_count": sum(1 for result in valid_results if result["obstacle_detected"]),
        "audit_trace_recorded_count": sum(1 for result in valid_results if result["audit_trace_recorded"]),
        "rollback_available_count": sum(1 for result in valid_results if result["rollback_available"]),
        "sandbox_record_only_count": sum(1 for result in valid_results if result["sandbox_record_only"]),
        "real_world_effect_blocked_count": _count_error(validation_results, "real_world_effect_not_false"),
        "production_effect_blocked_count": _count_error(validation_results, "production_effect_not_false"),
        "movement_executed_blocked_count": _count_error(validation_results, "movement_executed_not_false"),
        "retry_same_action_executed_blocked_count": _count_error(
            validation_results,
            "retry_same_action_executed_not_false",
        ),
        "production_action_selection_blocked_count": _count_error(
            validation_results,
            "production_action_selection_enabled",
        ),
        "runtime_action_selection_blocked_count": _count_error(
            validation_results,
            "runtime_action_selection_enabled",
        ),
        "selected_action_created_blocked_count": _count_error(
            validation_results,
            "selected_action_created_enabled",
        ),
        "final_action_created_blocked_count": _count_error(validation_results, "final_action_created_enabled"),
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
        "bad_execution_mode_blocked_count": _count_error(
            validation_results,
            "execution_mode_not_one_step_sandbox_execution_only",
        ),
        "wrong_executed_sandbox_action_blocked_count": _count_error(
            validation_results,
            "executed_sandbox_action_not_check_before_retry",
        ),
        "wrong_sandbox_context_blocked_count": _count_errors(
            validation_results,
            {
                "sandbox_before_sandbox_id_not_phase0_toy_sandbox_obstacle_retry_failed",
                "scenario_id_not_obstacle_retry_failed_same_state",
                "exact_key_not_obstacle_retry_failed",
            },
        ),
        "production_context_blocked_count": _count_error(validation_results, "production_context_not_false"),
        "audit_flags_false_blocked_count": _count_errors(
            validation_results,
            {
                "audit_trace_required_not_true",
                "audit_trace_recorded_not_true",
                "source_intent_checked_not_true",
                "execution_boundary_checked_not_true",
                "blocked_flags_checked_not_true",
            },
        ),
        "rollback_flags_false_blocked_count": _count_errors(
            validation_results,
            {
                "rollback_available_not_true",
                "rollback_required_before_execution_not_true",
            },
        ),
        "wrong_state_mutation_scope_blocked_count": _count_error(
            validation_results,
            "state_mutation_scope_not_sandbox_record_only",
        ),
        "wrong_rollback_scope_blocked_count": _count_error(
            validation_results,
            "rollback_scope_not_sandbox_record_only",
        ),
    }
    summary["all_one_step_sandbox_action_execution_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["sandbox_execution_result_count"] == 51
        and summary["valid_sandbox_execution_result_count"] == 1
        and summary["invalid_sandbox_execution_result_count"] == 50
        and summary["sandbox_action_executed_count"] == 1
        and summary["executed_once_count"] == 1
        and summary["check_before_retry_executed_count"] == 1
        and summary["obstacle_detected_count"] == 1
        and summary["audit_trace_recorded_count"] == 1
        and summary["rollback_available_count"] == 1
        and summary["sandbox_record_only_count"] == 1
        and summary["real_world_effect_blocked_count"] == 1
        and summary["production_effect_blocked_count"] == 1
        and summary["movement_executed_blocked_count"] == 1
        and summary["retry_same_action_executed_blocked_count"] == 1
        and summary["bad_execution_mode_blocked_count"] == 1
        and summary["wrong_executed_sandbox_action_blocked_count"] == 1
        and summary["wrong_sandbox_context_blocked_count"] == 3
        and summary["production_context_blocked_count"] == 1
        and summary["audit_flags_false_blocked_count"] == 5
        and summary["rollback_flags_false_blocked_count"] == 2
        and summary["wrong_state_mutation_scope_blocked_count"] == 1
        and summary["wrong_rollback_scope_blocked_count"] == 1
        and summary["production_action_selection_blocked_count"] == 1
        and summary["runtime_action_selection_blocked_count"] == 1
        and summary["selected_action_created_blocked_count"] == 1
        and summary["final_action_created_blocked_count"] == 1
        and summary["direct_action_command_blocked_count"] == 1
        and summary["persistent_policy_written_blocked_count"] == 1
        and summary["general_behavior_changed_blocked_count"] == 1
        and summary["semantic_or_fuzzy_match_used_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "one_step_sandbox_action_execution_enabled": True,
        "executed_sandbox_action": EXPECTED_ACTION,
        "sandbox_id": EXPECTED_SANDBOX_ID,
        "sandbox_action_executed": True,
        "executed_once": True,
        "real_world_effect_added": False,
        "production_effect_added": False,
        "selected_action_added": False,
        "runtime_action_selection_added": False,
        "final_action_creation_added": False,
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
