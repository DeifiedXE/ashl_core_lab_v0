"""Safety envelope for reversible runtime tendency memory influence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .runtime_tendency_memory_influence_rollback_check_minimal import (
    build_runtime_tendency_memory_influence_rollback_result,
    validate_runtime_tendency_memory_influence_rollback_result,
)


COMMAND = "run-runtime-tendency-memory-influence-safety-envelope-minimal-check"
FLOW = "runtime_tendency_memory_influence_safety_envelope_minimal_v0"

REQUIRED_FIELDS = {
    "safety_envelope_id",
    "source_rollback_result_id",
    "scope",
    "limits",
    "required_guards",
    "allowed_future_use",
    "human_summary",
    "blocked_flags",
}

REQUIRED_SCOPE = {
    "runtime_tendency_only",
    "controlled_runner_only",
    "same_state_same_candidates_required",
    "exact_key_memory_signal_only",
    "production_action_selection_allowed",
}

REQUIRED_LIMITS = {
    "max_positive_delta",
    "max_negative_delta",
    "max_absolute_delta",
    "one_step_evaluation_only",
    "no_persistent_influence",
    "rollback_required",
}

REQUIRED_GUARDS = {
    "rollback_verified",
    "dirty_state_absent",
    "persistent_influence_absent",
    "mentor_override_available",
    "exploration_allowed",
    "audit_trace_required",
    "no_final_action_gate",
    "no_action_execution_gate",
}

REQUIRED_ALLOWED_FUTURE_USE = {
    "may_feed_pre_action_consideration_design",
    "may_feed_runtime_action_selection",
    "may_create_final_action",
    "may_execute_action",
    "may_write_policy",
}

REQUIRED_HUMAN_SUMMARY = {
    "what_is_allowed",
    "what_is_required",
    "what_is_blocked",
    "plain_result",
}

REQUIRED_BLOCKED_FLAGS = {
    "production_action_selection",
    "final_action_created",
    "action_executed",
    "direct_action_command",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_policy_written",
    "general_behavior_changed",
    "dirty_state_allowed",
    "persistent_influence_allowed",
    "exploration_blocked",
    "curiosity_overridden",
    "mentor_override_blocked",
    "lesson_applied",
    "memory_write",
    "new_retention_written",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_runtime_tendency_memory_influence_safety_envelope(
    rollback_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = rollback_result if rollback_result is not None else build_runtime_tendency_memory_influence_rollback_result()
    rollback_validation = validate_runtime_tendency_memory_influence_rollback_result(source)
    rollback_check = source.get("rollback_check", {}) if isinstance(source, dict) else {}
    rollback_verified = (
        rollback_validation["valid"]
        and rollback_validation["memory_on_changed_scores"]
        and rollback_validation["memory_off_again_matches_baseline"]
        and rollback_check.get("dirty_state_detected") is False
        and rollback_check.get("persistent_influence_detected") is False
    )

    return {
        "safety_envelope_id": "runtime_tendency_memory_influence_safety_envelope_demo_001",
        "source_rollback_result_id": source.get("rollback_result_id") if isinstance(source, dict) else None,
        "scope": {
            "runtime_tendency_only": True,
            "controlled_runner_only": True,
            "same_state_same_candidates_required": True,
            "exact_key_memory_signal_only": True,
            "production_action_selection_allowed": False,
        },
        "limits": {
            "max_positive_delta": 0.10,
            "max_negative_delta": -0.05,
            "max_absolute_delta": 0.10,
            "one_step_evaluation_only": True,
            "no_persistent_influence": True,
            "rollback_required": True,
        },
        "required_guards": {
            "rollback_verified": rollback_verified,
            "dirty_state_absent": rollback_check.get("dirty_state_detected") is False,
            "persistent_influence_absent": rollback_check.get("persistent_influence_detected") is False,
            "mentor_override_available": True,
            "exploration_allowed": True,
            "audit_trace_required": True,
            "no_final_action_gate": True,
            "no_action_execution_gate": True,
        },
        "allowed_future_use": {
            "may_feed_pre_action_consideration_design": True,
            "may_feed_runtime_action_selection": False,
            "may_create_final_action": False,
            "may_execute_action": False,
            "may_write_policy": False,
        },
        "human_summary": {
            "what_is_allowed": "Memory influence may alter controlled runtime tendency scores inside this bounded envelope.",
            "what_is_required": "Rollback, no dirty state, no persistent influence, mentor override, exploration allowance, and audit trace are required.",
            "what_is_blocked": "Final action selection, action execution, direct commands, persistent policy, and generalized behavior remain blocked.",
            "plain_result": "Runtime tendency memory influence is reversible and bounded, but still not allowed to select or execute actions.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_runtime_tendency_memory_influence_safety_envelope(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not isinstance(record.get("source_rollback_result_id"), str) or not record.get("source_rollback_result_id"):
        errors.append("source_rollback_result_id_empty_or_not_string")

    scope = _section(record, "scope", errors)
    _require_section_fields("scope", scope, REQUIRED_SCOPE, errors)
    _require_true(scope, "runtime_tendency_only", errors)
    _require_true(scope, "controlled_runner_only", errors)
    _require_true(scope, "same_state_same_candidates_required", errors)
    _require_true(scope, "exact_key_memory_signal_only", errors)
    _require_false(scope, "production_action_selection_allowed", errors)

    limits = _section(record, "limits", errors)
    _require_section_fields("limits", limits, REQUIRED_LIMITS, errors)
    _require_number_at_most(limits, "max_positive_delta", 0.10, errors)
    _require_number_at_least(limits, "max_negative_delta", -0.10, errors)
    _require_number_at_most(limits, "max_absolute_delta", 0.10, errors)
    _require_true(limits, "one_step_evaluation_only", errors)
    _require_true(limits, "no_persistent_influence", errors)
    _require_true(limits, "rollback_required", errors)

    guards = _section(record, "required_guards", errors)
    _require_section_fields("required_guards", guards, REQUIRED_GUARDS, errors)
    _require_true(guards, "rollback_verified", errors)
    _require_true(guards, "dirty_state_absent", errors)
    _require_true(guards, "persistent_influence_absent", errors)
    _require_true(guards, "mentor_override_available", errors)
    _require_true(guards, "exploration_allowed", errors)
    _require_true(guards, "audit_trace_required", errors)
    _require_true(guards, "no_final_action_gate", errors)
    _require_true(guards, "no_action_execution_gate", errors)

    allowed = _section(record, "allowed_future_use", errors)
    _require_section_fields("allowed_future_use", allowed, REQUIRED_ALLOWED_FUTURE_USE, errors)
    _require_true(allowed, "may_feed_pre_action_consideration_design", errors)
    _require_false(allowed, "may_feed_runtime_action_selection", errors)
    _require_false(allowed, "may_create_final_action", errors)
    _require_false(allowed, "may_execute_action", errors)
    _require_false(allowed, "may_write_policy", errors)

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
        "safety_envelope_id": record.get("safety_envelope_id"),
        "valid": not errors,
        "error_codes": errors,
        "rollback_verified": guards.get("rollback_verified") is True,
        "dirty_state_absent": guards.get("dirty_state_absent") is True,
        "persistent_influence_absent": guards.get("persistent_influence_absent") is True,
        "mentor_override_available": guards.get("mentor_override_available") is True,
        "exploration_allowed": guards.get("exploration_allowed") is True,
        "runtime_selection_blocked": allowed.get("may_feed_runtime_action_selection") is False,
        "final_action_blocked": allowed.get("may_create_final_action") is False,
        "action_execution_blocked": allowed.get("may_execute_action") is False,
        "policy_write_blocked": allowed.get("may_write_policy") is False,
        **_blocked_flag_values(blocked_flags),
    }


def run_runtime_tendency_memory_influence_safety_envelope_minimal_check() -> dict[str, Any]:
    valid_envelope = build_runtime_tendency_memory_influence_safety_envelope()
    records = [
        valid_envelope,
        *_invalid_demo_records(valid_envelope),
    ]
    validation_results = [
        validate_runtime_tendency_memory_influence_safety_envelope(record) for record in records
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "runtime_tendency_memory_influence_safety_envelopes": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Runtime tendency memory influence remains controlled-runner-only and reversible.",
            "The safety envelope blocks runtime action selection, final actions, action execution, direct commands, persistent policy writes, and generalized behavior.",
            "Mentor override, exploration allowance, audit trace, rollback, no dirty state, and no persistent influence remain required.",
        ],
    }


def _section(record: dict[str, Any], field: str, errors: list[str]) -> dict[str, Any]:
    value = record.get(field)
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _require_section_fields(
    section_name: str,
    section: dict[str, Any],
    required_fields: set[str],
    errors: list[str],
) -> None:
    for field in sorted(required_fields):
        if field not in section:
            errors.append(f"missing_{section_name}_field:{field}")


def _require_true(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not True:
        errors.append(f"{field}_not_true")


def _require_false(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not False:
        errors.append(f"{field}_not_false")


def _require_number_at_most(section: dict[str, Any], field: str, maximum: float, errors: list[str]) -> None:
    value = section.get(field)
    if not isinstance(value, (int, float)):
        errors.append(f"{field}_not_number")
    elif float(value) > maximum:
        errors.append(f"{field}_too_high")


def _require_number_at_least(section: dict[str, Any], field: str, minimum: float, errors: list[str]) -> None:
    value = section.get(field)
    if not isinstance(value, (int, float)):
        errors.append(f"{field}_not_number")
    elif float(value) < minimum:
        errors.append(f"{field}_too_low")


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _invalid_demo_records(valid_envelope: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    section_cases = [
        ("scope", "runtime_tendency_only", False),
        ("scope", "controlled_runner_only", False),
        ("scope", "same_state_same_candidates_required", False),
        ("scope", "exact_key_memory_signal_only", False),
        ("scope", "production_action_selection_allowed", True),
        ("limits", "max_absolute_delta", 0.11),
        ("limits", "one_step_evaluation_only", False),
        ("limits", "no_persistent_influence", False),
        ("limits", "rollback_required", False),
        ("required_guards", "rollback_verified", False),
        ("required_guards", "dirty_state_absent", False),
        ("required_guards", "persistent_influence_absent", False),
        ("required_guards", "mentor_override_available", False),
        ("required_guards", "exploration_allowed", False),
        ("required_guards", "audit_trace_required", False),
        ("required_guards", "no_final_action_gate", False),
        ("required_guards", "no_action_execution_gate", False),
        ("allowed_future_use", "may_feed_pre_action_consideration_design", False),
        ("allowed_future_use", "may_feed_runtime_action_selection", True),
        ("allowed_future_use", "may_create_final_action", True),
        ("allowed_future_use", "may_execute_action", True),
        ("allowed_future_use", "may_write_policy", True),
    ]
    for section, field, value in section_cases:
        invalid = _copy_case(valid_envelope, f"{field}_{value}")
        invalid[section][field] = value
        records.append(invalid)

    for field in ("what_is_allowed", "what_is_blocked", "plain_result"):
        invalid = _copy_case(valid_envelope, f"empty_{field}")
        invalid["human_summary"][field] = ""
        records.append(invalid)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid = _copy_case(valid_envelope, flag)
        invalid["blocked_flags"][flag] = True
        records.append(invalid)

    return records


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["safety_envelope_id"] = f"{record['safety_envelope_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "safety_envelope_count": len(validation_results),
        "valid_safety_envelope_count": len(valid_results),
        "invalid_safety_envelope_count": sum(1 for result in validation_results if not result["valid"]),
        "rollback_verified_count": sum(1 for result in valid_results if result["rollback_verified"]),
        "dirty_state_absent_count": sum(1 for result in valid_results if result["dirty_state_absent"]),
        "persistent_influence_absent_count": sum(
            1 for result in valid_results if result["persistent_influence_absent"]
        ),
        "mentor_override_available_count": sum(
            1 for result in valid_results if result["mentor_override_available"]
        ),
        "exploration_allowed_count": sum(1 for result in valid_results if result["exploration_allowed"]),
        "runtime_selection_blocked_count": sum(
            1 for result in valid_results if result["runtime_selection_blocked"]
        ),
        "final_action_blocked_count": sum(1 for result in valid_results if result["final_action_blocked"]),
        "action_execution_blocked_count": sum(
            1 for result in valid_results if result["action_execution_blocked"]
        ),
        "policy_write_blocked_count": sum(1 for result in valid_results if result["policy_write_blocked"]),
        "max_absolute_delta_violation_blocked_count": _count_error(
            validation_results, "max_absolute_delta_too_high"
        ),
        "production_action_selection_blocked_count": _count_error(
            validation_results, "production_action_selection_enabled"
        ),
        "final_action_created_blocked_count": _count_error(validation_results, "final_action_created_enabled"),
        "action_executed_blocked_count": _count_error(validation_results, "action_executed_enabled"),
        "direct_action_command_blocked_count": _count_error(validation_results, "direct_action_command_enabled"),
        "real_navigation_changed_blocked_count": _count_error(validation_results, "real_navigation_changed_enabled"),
        "ui_behavior_changed_blocked_count": _count_error(validation_results, "ui_behavior_changed_enabled"),
        "persistent_policy_written_blocked_count": _count_error(
            validation_results, "persistent_policy_written_enabled"
        ),
        "general_behavior_changed_blocked_count": _count_error(
            validation_results, "general_behavior_changed_enabled"
        ),
        "dirty_state_allowed_blocked_count": _count_error(validation_results, "dirty_state_allowed_enabled"),
        "persistent_influence_allowed_blocked_count": _count_error(
            validation_results, "persistent_influence_allowed_enabled"
        ),
        "exploration_blocked_count": _count_error(validation_results, "exploration_blocked_enabled"),
        "curiosity_overridden_blocked_count": _count_error(validation_results, "curiosity_overridden_enabled"),
        "mentor_override_blocked_count": _count_error(validation_results, "mentor_override_blocked_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(validation_results, "new_retention_written_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
        "runtime_tendency_only_false_blocked_count": _count_error(validation_results, "runtime_tendency_only_not_true"),
        "controlled_runner_only_false_blocked_count": _count_error(
            validation_results, "controlled_runner_only_not_true"
        ),
        "same_state_same_candidates_required_false_blocked_count": _count_error(
            validation_results, "same_state_same_candidates_required_not_true"
        ),
        "exact_key_memory_signal_only_false_blocked_count": _count_error(
            validation_results, "exact_key_memory_signal_only_not_true"
        ),
        "production_action_selection_allowed_true_blocked_count": _count_error(
            validation_results, "production_action_selection_allowed_not_false"
        ),
        "one_step_evaluation_only_false_blocked_count": _count_error(
            validation_results, "one_step_evaluation_only_not_true"
        ),
        "no_persistent_influence_false_blocked_count": _count_error(
            validation_results, "no_persistent_influence_not_true"
        ),
        "rollback_required_false_blocked_count": _count_error(validation_results, "rollback_required_not_true"),
        "rollback_verified_false_blocked_count": _count_error(validation_results, "rollback_verified_not_true"),
        "dirty_state_absent_false_blocked_count": _count_error(validation_results, "dirty_state_absent_not_true"),
        "persistent_influence_absent_false_blocked_count": _count_error(
            validation_results, "persistent_influence_absent_not_true"
        ),
        "mentor_override_available_false_blocked_count": _count_error(
            validation_results, "mentor_override_available_not_true"
        ),
        "exploration_allowed_false_blocked_count": _count_error(validation_results, "exploration_allowed_not_true"),
        "audit_trace_required_false_blocked_count": _count_error(
            validation_results, "audit_trace_required_not_true"
        ),
        "no_final_action_gate_false_blocked_count": _count_error(
            validation_results, "no_final_action_gate_not_true"
        ),
        "no_action_execution_gate_false_blocked_count": _count_error(
            validation_results, "no_action_execution_gate_not_true"
        ),
        "may_feed_pre_action_false_blocked_count": _count_error(
            validation_results, "may_feed_pre_action_consideration_design_not_true"
        ),
        "may_feed_runtime_action_selection_true_blocked_count": _count_error(
            validation_results, "may_feed_runtime_action_selection_not_false"
        ),
        "may_create_final_action_true_blocked_count": _count_error(
            validation_results, "may_create_final_action_not_false"
        ),
        "may_execute_action_true_blocked_count": _count_error(validation_results, "may_execute_action_not_false"),
        "may_write_policy_true_blocked_count": _count_error(validation_results, "may_write_policy_not_false"),
        "empty_what_is_allowed_blocked_count": _count_error(
            validation_results, "what_is_allowed_empty_or_not_string"
        ),
        "empty_what_is_blocked_blocked_count": _count_error(
            validation_results, "what_is_blocked_empty_or_not_string"
        ),
        "empty_plain_result_blocked_count": _count_error(validation_results, "plain_result_empty_or_not_string"),
    }
    summary["all_runtime_tendency_memory_influence_safety_envelope_minimal_checks_passed"] = _all_checks_passed(
        summary
    )
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["safety_envelope_count"] == 44
        and summary["valid_safety_envelope_count"] == 1
        and summary["invalid_safety_envelope_count"] == 43
        and summary["rollback_verified_count"] == 1
        and summary["dirty_state_absent_count"] == 1
        and summary["persistent_influence_absent_count"] == 1
        and summary["mentor_override_available_count"] == 1
        and summary["exploration_allowed_count"] == 1
        and summary["runtime_selection_blocked_count"] == 1
        and summary["final_action_blocked_count"] == 1
        and summary["action_execution_blocked_count"] == 1
        and summary["policy_write_blocked_count"] == 1
        and summary["max_absolute_delta_violation_blocked_count"] == 1
        and summary["production_action_selection_blocked_count"] == 1
        and summary["final_action_created_blocked_count"] == 1
        and summary["action_executed_blocked_count"] == 1
        and summary["direct_action_command_blocked_count"] == 1
        and summary["real_navigation_changed_blocked_count"] == 1
        and summary["ui_behavior_changed_blocked_count"] == 1
        and summary["persistent_policy_written_blocked_count"] == 1
        and summary["general_behavior_changed_blocked_count"] == 1
        and summary["dirty_state_allowed_blocked_count"] == 1
        and summary["persistent_influence_allowed_blocked_count"] == 1
        and summary["exploration_blocked_count"] == 1
        and summary["curiosity_overridden_blocked_count"] == 1
        and summary["mentor_override_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["new_retention_written_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["runtime_tendency_only_false_blocked_count"] == 1
        and summary["controlled_runner_only_false_blocked_count"] == 1
        and summary["same_state_same_candidates_required_false_blocked_count"] == 1
        and summary["exact_key_memory_signal_only_false_blocked_count"] == 1
        and summary["production_action_selection_allowed_true_blocked_count"] == 1
        and summary["one_step_evaluation_only_false_blocked_count"] == 1
        and summary["no_persistent_influence_false_blocked_count"] == 1
        and summary["rollback_required_false_blocked_count"] == 1
        and summary["rollback_verified_false_blocked_count"] == 1
        and summary["dirty_state_absent_false_blocked_count"] == 1
        and summary["persistent_influence_absent_false_blocked_count"] == 1
        and summary["mentor_override_available_false_blocked_count"] == 1
        and summary["exploration_allowed_false_blocked_count"] == 1
        and summary["audit_trace_required_false_blocked_count"] == 1
        and summary["no_final_action_gate_false_blocked_count"] == 1
        and summary["no_action_execution_gate_false_blocked_count"] == 1
        and summary["may_feed_pre_action_false_blocked_count"] == 1
        and summary["may_feed_runtime_action_selection_true_blocked_count"] == 1
        and summary["may_create_final_action_true_blocked_count"] == 1
        and summary["may_execute_action_true_blocked_count"] == 1
        and summary["may_write_policy_true_blocked_count"] == 1
        and summary["empty_what_is_allowed_blocked_count"] == 1
        and summary["empty_what_is_blocked_blocked_count"] == 1
        and summary["empty_plain_result_blocked_count"] == 1
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "runtime_tendency_memory_influence_safety_envelope_enabled": True,
        "controlled_runner_scope_required": True,
        "same_state_same_candidates_required": True,
        "exact_key_memory_signal_only": True,
        "max_absolute_delta": 0.10,
        "rollback_verified": True,
        "dirty_state_absent": True,
        "persistent_influence_absent": True,
        "mentor_override_available": True,
        "exploration_allowed": True,
        "audit_trace_required": True,
        "no_final_action_gate": True,
        "no_action_execution_gate": True,
        "runtime_action_selection_added": False,
        "final_action_creation_added": False,
        "action_execution_added": False,
        "direct_action_command_added": False,
        "real_navigation_change_added": False,
        "ui_behavior_change_added": False,
        "persistent_policy_write_added": False,
        "general_behavior_change_added": False,
        "proof_of_learning_claimed": False,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "valid_safety_envelope_count": summary["valid_safety_envelope_count"],
    }


def _blocked_flag_values(blocked_flags: dict[str, Any]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])
