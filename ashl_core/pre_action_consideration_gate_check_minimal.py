"""Gate pre-action candidates into action-selection-adjacent review only."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .pre_action_consideration_candidate_minimal import (
    EXPECTED_MAPPING,
    build_pre_action_consideration_candidates,
    validate_pre_action_consideration_candidate_result,
)
from .runtime_action_tendency_memory_influence_ab_minimal import CANDIDATE_ACTIONS
from .runtime_tendency_memory_influence_safety_envelope_minimal import (
    build_runtime_tendency_memory_influence_safety_envelope,
    validate_runtime_tendency_memory_influence_safety_envelope,
)


COMMAND = "run-pre-action-consideration-gate-check-minimal-check"
FLOW = "pre_action_consideration_gate_check_minimal_v0"

GATE_STATUS = "passed_for_action_selection_adjacent_review"

REQUIRED_FIELDS = {
    "pre_action_gate_result_id",
    "source_pre_action_candidate_result_id",
    "source_safety_envelope_id",
    "gate_status",
    "gated_candidates",
    "gate_checks",
    "allowed_next_layer",
    "human_summary",
    "blocked_flags",
}

REQUIRED_GATE_CHECKS = {
    "candidate_result_valid",
    "safety_envelope_valid",
    "all_candidates_pre_action_only",
    "all_candidates_not_final_action",
    "all_candidates_from_positive_delta",
    "all_candidates_exact_key_only",
    "max_absolute_delta_within_limit",
    "rollback_verified",
    "dirty_state_absent",
    "persistent_influence_absent",
    "mentor_override_available",
    "exploration_allowed",
    "audit_trace_required",
    "no_final_action_gate",
    "no_action_execution_gate",
}

REQUIRED_ALLOWED_NEXT_LAYER = {
    "may_enter_action_selection_adjacent_review",
    "may_enter_runtime_action_selection",
    "may_create_final_action",
    "may_execute_action",
    "may_create_direct_command",
    "may_write_persistent_policy",
}

REQUIRED_HUMAN_SUMMARY = {
    "what_passed",
    "why_it_passed",
    "what_is_still_blocked",
    "plain_result",
}

REQUIRED_BLOCKED_FLAGS = {
    "production_action_selection",
    "runtime_action_selection",
    "final_action_created",
    "action_selected",
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


def build_pre_action_consideration_gate_result(
    candidate_result: dict[str, Any] | None = None,
    safety_envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidates_source = candidate_result or build_pre_action_consideration_candidates()
    envelope = safety_envelope or build_runtime_tendency_memory_influence_safety_envelope()
    candidate_validation = validate_pre_action_consideration_candidate_result(candidates_source)
    envelope_validation = validate_runtime_tendency_memory_influence_safety_envelope(envelope)

    gate_checks = {
        "candidate_result_valid": candidate_validation["valid"],
        "safety_envelope_valid": envelope_validation["valid"],
        "all_candidates_pre_action_only": candidate_validation["pre_action_only_candidate_count"] == 3,
        "all_candidates_not_final_action": candidate_validation["not_final_action_candidate_count"] == 3,
        "all_candidates_from_positive_delta": candidate_validation["positive_delta_candidate_count"] == 3,
        "all_candidates_exact_key_only": candidate_validation["exact_key_candidate_count"] == 3,
        "max_absolute_delta_within_limit": _envelope_max_absolute_delta(envelope) <= 0.10,
        "rollback_verified": envelope_validation["rollback_verified"],
        "dirty_state_absent": envelope_validation["dirty_state_absent"],
        "persistent_influence_absent": envelope_validation["persistent_influence_absent"],
        "mentor_override_available": envelope_validation["mentor_override_available"],
        "exploration_allowed": envelope_validation["exploration_allowed"],
        "audit_trace_required": envelope.get("required_guards", {}).get("audit_trace_required") is True,
        "no_final_action_gate": envelope.get("required_guards", {}).get("no_final_action_gate") is True,
        "no_action_execution_gate": envelope.get("required_guards", {}).get("no_action_execution_gate") is True,
    }
    return {
        "pre_action_gate_result_id": "pre_action_consideration_gate_demo_001",
        "source_pre_action_candidate_result_id": candidates_source.get(
            "pre_action_candidate_result_id",
            "pre_action_consideration_candidate_demo_001",
        ),
        "source_safety_envelope_id": envelope.get(
            "safety_envelope_id",
            "runtime_tendency_memory_influence_safety_envelope_demo_001",
        ),
        "gate_status": GATE_STATUS,
        "gated_candidates": [_gated_candidate(candidate) for candidate in candidates_source.get("candidates", [])],
        "gate_checks": gate_checks,
        "allowed_next_layer": {
            "may_enter_action_selection_adjacent_review": True,
            "may_enter_runtime_action_selection": False,
            "may_create_final_action": False,
            "may_execute_action": False,
            "may_create_direct_command": False,
            "may_write_persistent_policy": False,
        },
        "human_summary": {
            "what_passed": "Three pre-action candidates passed the gate for action-selection-adjacent review.",
            "why_it_passed": "Candidates are exact-key sourced, positive-delta derived, bounded, reversible, mentor-overridable, and pre-action only.",
            "what_is_still_blocked": "Runtime action selection, final actions, action execution, direct commands, and persistent policy remain blocked.",
            "plain_result": "The system can pass bounded pre-action candidates into a review layer, but still cannot select or execute actions.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_pre_action_consideration_gate_result(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)
    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if record.get("gate_status") != GATE_STATUS:
        errors.append("gate_status_not_passed_for_action_selection_adjacent_review")

    gated_candidates = record.get("gated_candidates")
    if not isinstance(gated_candidates, list):
        errors.append("gated_candidates_missing_or_not_list")
        gated_candidates = []
    if len(gated_candidates) != 3:
        errors.append("gated_candidates_length_not_three")
    candidate_validations = [_validate_gated_candidate(candidate) for candidate in gated_candidates]
    for validation in candidate_validations:
        errors.extend(validation["error_codes"])

    gate_checks = _section(record, "gate_checks", errors)
    _require_section_fields("gate_checks", gate_checks, REQUIRED_GATE_CHECKS, errors)
    for field in sorted(REQUIRED_GATE_CHECKS):
        if gate_checks.get(field) is not True:
            errors.append(f"{field}_not_true")

    allowed_next = _section(record, "allowed_next_layer", errors)
    _require_section_fields("allowed_next_layer", allowed_next, REQUIRED_ALLOWED_NEXT_LAYER, errors)
    _require_true(allowed_next, "may_enter_action_selection_adjacent_review", errors)
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
        "pre_action_gate_result_id": record.get("pre_action_gate_result_id"),
        "valid": not errors,
        "error_codes": errors,
        "gated_candidate_count": len(gated_candidates),
        "gate_passed_candidate_count": sum(1 for result in candidate_validations if result["gate_passed"]),
        "allowed_for_action_selection_adjacent_review_count": sum(
            1 for result in candidate_validations if result["allowed_for_action_selection_adjacent_review"]
        ),
        "runtime_action_selection_blocked": allowed_next.get("may_enter_runtime_action_selection") is False,
        "final_action_blocked": allowed_next.get("may_create_final_action") is False,
        "action_execution_blocked": allowed_next.get("may_execute_action") is False,
        "direct_command_blocked": allowed_next.get("may_create_direct_command") is False,
        "persistent_policy_blocked": allowed_next.get("may_write_persistent_policy") is False,
        "candidate_result_valid": gate_checks.get("candidate_result_valid") is True,
        "safety_envelope_valid": gate_checks.get("safety_envelope_valid") is True,
        "rollback_verified": gate_checks.get("rollback_verified") is True,
        "mentor_override_available": gate_checks.get("mentor_override_available") is True,
        "exploration_allowed": gate_checks.get("exploration_allowed") is True,
        "audit_trace_required": gate_checks.get("audit_trace_required") is True,
        "obstacle_candidate_pass_count": _candidate_pass_count(
            candidate_validations,
            "obstacle_retry_failed_same_state",
        ),
        "costly_retry_candidate_pass_count": _candidate_pass_count(
            candidate_validations,
            "costly_retry_same_state",
        ),
        "unclear_failure_candidate_pass_count": _candidate_pass_count(
            candidate_validations,
            "unclear_failure_same_state",
        ),
        **_blocked_flag_values(blocked_flags),
    }


def run_pre_action_consideration_gate_check_minimal_check() -> dict[str, Any]:
    valid_result = build_pre_action_consideration_gate_result()
    records = [
        valid_result,
        *_invalid_demo_records(valid_result),
    ]
    validation_results = [validate_pre_action_consideration_gate_result(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "pre_action_consideration_gate_results": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Pre-action candidates may enter action-selection-adjacent review only.",
            "Runtime action selection, final actions, execution, direct commands, and persistent policy remain blocked.",
            "The gate is a data-layer check and does not select an action.",
        ],
    }


def _gated_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario_id": candidate["scenario_id"],
        "exact_key": candidate["exact_key"],
        "considered_action": candidate["considered_action"],
        "gate_passed": True,
        "gate_reason": "Candidate is pre-action only, exact-key sourced, positive-delta derived, and covered by the safety envelope.",
        "allowed_for_action_selection_adjacent_review": True,
        "allowed_for_runtime_action_selection": False,
        "allowed_for_final_action": False,
        "allowed_for_action_execution": False,
    }


def _validate_gated_candidate(candidate: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(candidate, dict):
        return _gated_candidate_validation_result("", "", "", False, False, errors + ["gated_candidate_not_dict"])

    scenario_id = candidate.get("scenario_id")
    exact_key = candidate.get("exact_key")
    expected = EXPECTED_MAPPING.get(scenario_id)
    scenario_valid = expected is not None
    if not scenario_valid:
        errors.append("unknown_scenario_id")
    if exact_key not in {value[0] for value in EXPECTED_MAPPING.values()}:
        errors.append("unknown_exact_key")
    if expected is not None and exact_key != expected[0]:
        errors.append("scenario_exact_key_mismatch")

    action = candidate.get("considered_action")
    action_valid = action in CANDIDATE_ACTIONS
    if not action_valid:
        errors.append("unknown_considered_action")
    if expected is not None and action_valid and action != expected[1]:
        errors.append(f"{scenario_id}_wrong_considered_action")

    gate_passed = candidate.get("gate_passed") is True
    if not gate_passed:
        errors.append("gate_passed_not_true")
    if not isinstance(candidate.get("gate_reason"), str) or not candidate.get("gate_reason"):
        errors.append("gate_reason_empty_or_not_string")

    adjacent_allowed = candidate.get("allowed_for_action_selection_adjacent_review") is True
    if not adjacent_allowed:
        errors.append("allowed_for_action_selection_adjacent_review_not_true")
    if candidate.get("allowed_for_runtime_action_selection") is not False:
        errors.append("allowed_for_runtime_action_selection_not_false")
    if candidate.get("allowed_for_final_action") is not False:
        errors.append("allowed_for_final_action_not_false")
    if candidate.get("allowed_for_action_execution") is not False:
        errors.append("allowed_for_action_execution_not_false")

    candidate_pass = bool(
        scenario_valid
        and expected is not None
        and exact_key == expected[0]
        and action == expected[1]
        and gate_passed
        and adjacent_allowed
        and candidate.get("allowed_for_runtime_action_selection") is False
        and candidate.get("allowed_for_final_action") is False
        and candidate.get("allowed_for_action_execution") is False
        and not errors
    )
    return _gated_candidate_validation_result(
        str(scenario_id or ""),
        str(exact_key or ""),
        str(action or ""),
        gate_passed,
        adjacent_allowed,
        errors,
        candidate_pass=candidate_pass,
    )


def _gated_candidate_validation_result(
    scenario_id: str,
    exact_key: str,
    considered_action: str,
    gate_passed: bool,
    adjacent_allowed: bool,
    errors: list[str],
    candidate_pass: bool = False,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "exact_key": exact_key,
        "considered_action": considered_action,
        "gate_passed": gate_passed,
        "allowed_for_action_selection_adjacent_review": adjacent_allowed,
        "candidate_pass": candidate_pass,
        "error_codes": errors,
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


def _envelope_max_absolute_delta(envelope: dict[str, Any]) -> float:
    value = envelope.get("limits", {}).get("max_absolute_delta")
    return float(value) if isinstance(value, (int, float)) else 999.0


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _invalid_demo_records(valid_result: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    bad_status = _copy_case(valid_result, "bad_gate_status")
    bad_status["gate_status"] = "runtime_action_selection_ready"
    records.append(bad_status)

    missing_candidate = _copy_case(valid_result, "missing_gated_candidate")
    missing_candidate["gated_candidates"] = missing_candidate["gated_candidates"][:2]
    records.append(missing_candidate)

    wrong_mappings = [
        (0, "ask_for_help", "wrong_obstacle_mapping"),
        (1, "check_before_retry", "wrong_costly_retry_mapping"),
        (2, "check_before_retry", "wrong_unclear_failure_mapping"),
    ]
    for index, action, name in wrong_mappings:
        invalid = _copy_case(valid_result, name)
        invalid["gated_candidates"][index]["considered_action"] = action
        records.append(invalid)

    candidate_cases = [
        ("gate_passed", False, "gate_passed_false"),
        ("gate_reason", "", "empty_gate_reason"),
        ("allowed_for_action_selection_adjacent_review", False, "adjacent_review_false"),
        ("allowed_for_runtime_action_selection", True, "runtime_action_selection_true"),
        ("allowed_for_final_action", True, "final_action_true"),
        ("allowed_for_action_execution", True, "action_execution_true"),
    ]
    for field, value, name in candidate_cases:
        invalid = _copy_case(valid_result, name)
        invalid["gated_candidates"][0][field] = value
        records.append(invalid)

    for field in sorted(REQUIRED_GATE_CHECKS):
        invalid = _copy_case(valid_result, f"{field}_false")
        invalid["gate_checks"][field] = False
        records.append(invalid)

    allowed_next_cases = [
        ("may_enter_runtime_action_selection", True),
        ("may_create_final_action", True),
        ("may_execute_action", True),
        ("may_create_direct_command", True),
        ("may_write_persistent_policy", True),
    ]
    for field, value in allowed_next_cases:
        invalid = _copy_case(valid_result, f"{field}_{value}")
        invalid["allowed_next_layer"][field] = value
        records.append(invalid)

    for field in ("why_it_passed", "plain_result"):
        invalid = _copy_case(valid_result, f"empty_{field}")
        invalid["human_summary"][field] = ""
        records.append(invalid)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid = _copy_case(valid_result, flag)
        invalid["blocked_flags"][flag] = True
        records.append(invalid)

    return records


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["pre_action_gate_result_id"] = f"{record['pre_action_gate_result_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    valid_result = valid_results[0] if valid_results else {}
    summary: dict[str, int | bool] = {
        "pre_action_gate_result_count": len(validation_results),
        "valid_pre_action_gate_result_count": len(valid_results),
        "invalid_pre_action_gate_result_count": sum(1 for result in validation_results if not result["valid"]),
        "gated_candidate_count": int(valid_result.get("gated_candidate_count", 0)),
        "gate_passed_candidate_count": int(valid_result.get("gate_passed_candidate_count", 0)),
        "allowed_for_action_selection_adjacent_review_count": int(
            valid_result.get("allowed_for_action_selection_adjacent_review_count", 0)
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
        "candidate_result_valid_count": sum(1 for result in valid_results if result["candidate_result_valid"]),
        "safety_envelope_valid_count": sum(1 for result in valid_results if result["safety_envelope_valid"]),
        "rollback_verified_count": sum(1 for result in valid_results if result["rollback_verified"]),
        "mentor_override_available_count": sum(
            1 for result in valid_results if result["mentor_override_available"]
        ),
        "exploration_allowed_count": sum(1 for result in valid_results if result["exploration_allowed"]),
        "audit_trace_required_count": sum(1 for result in valid_results if result["audit_trace_required"]),
        "obstacle_candidate_pass_count": int(valid_result.get("obstacle_candidate_pass_count", 0)),
        "costly_retry_candidate_pass_count": int(valid_result.get("costly_retry_candidate_pass_count", 0)),
        "unclear_failure_candidate_pass_count": int(valid_result.get("unclear_failure_candidate_pass_count", 0)),
        "bad_gate_status_blocked_count": _count_error(
            validation_results,
            "gate_status_not_passed_for_action_selection_adjacent_review",
        ),
        "missing_gated_candidate_blocked_count": _count_error(
            validation_results,
            "gated_candidates_length_not_three",
        ),
        "wrong_mapping_blocked_count": _count_errors_ending(validation_results, "_wrong_considered_action"),
        "gate_passed_false_blocked_count": _count_error(validation_results, "gate_passed_not_true"),
        "empty_gate_reason_blocked_count": _count_error(
            validation_results,
            "gate_reason_empty_or_not_string",
        ),
        "adjacent_review_false_blocked_count": _count_error(
            validation_results,
            "allowed_for_action_selection_adjacent_review_not_true",
        ),
        "runtime_action_selection_allowed_blocked_count": _count_error(
            validation_results,
            "allowed_for_runtime_action_selection_not_false",
        ),
        "final_action_allowed_blocked_count": _count_error(
            validation_results,
            "allowed_for_final_action_not_false",
        ),
        "action_execution_allowed_blocked_count": _count_error(
            validation_results,
            "allowed_for_action_execution_not_false",
        ),
        "candidate_result_valid_false_blocked_count": _count_error(
            validation_results,
            "candidate_result_valid_not_true",
        ),
        "safety_envelope_valid_false_blocked_count": _count_error(
            validation_results,
            "safety_envelope_valid_not_true",
        ),
        "rollback_verified_false_blocked_count": _count_error(
            validation_results,
            "rollback_verified_not_true",
        ),
        "mentor_override_available_false_blocked_count": _count_error(
            validation_results,
            "mentor_override_available_not_true",
        ),
        "exploration_allowed_false_blocked_count": _count_error(
            validation_results,
            "exploration_allowed_not_true",
        ),
        "audit_trace_required_false_blocked_count": _count_error(
            validation_results,
            "audit_trace_required_not_true",
        ),
        "no_final_action_gate_false_blocked_count": _count_error(
            validation_results,
            "no_final_action_gate_not_true",
        ),
        "no_action_execution_gate_false_blocked_count": _count_error(
            validation_results,
            "no_action_execution_gate_not_true",
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
        "empty_why_it_passed_blocked_count": _count_error(
            validation_results,
            "why_it_passed_empty_or_not_string",
        ),
        "empty_plain_result_blocked_count": _count_error(validation_results, "plain_result_empty_or_not_string"),
        "production_action_selection_blocked_count": _count_error(
            validation_results,
            "production_action_selection_enabled",
        ),
        "runtime_action_selection_flag_blocked_count": _count_error(
            validation_results,
            "runtime_action_selection_enabled",
        ),
        "final_action_created_blocked_count": _count_error(validation_results, "final_action_created_enabled"),
        "action_selected_blocked_count": _count_error(validation_results, "action_selected_enabled"),
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
    summary["all_pre_action_consideration_gate_check_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["pre_action_gate_result_count"] == 53
        and summary["valid_pre_action_gate_result_count"] == 1
        and summary["invalid_pre_action_gate_result_count"] == 52
        and summary["gated_candidate_count"] == 3
        and summary["gate_passed_candidate_count"] == 3
        and summary["allowed_for_action_selection_adjacent_review_count"] == 3
        and summary["runtime_action_selection_blocked_count"] == 1
        and summary["final_action_blocked_count"] == 1
        and summary["action_execution_blocked_count"] == 1
        and summary["direct_command_blocked_count"] == 1
        and summary["persistent_policy_blocked_count"] == 1
        and summary["candidate_result_valid_count"] == 1
        and summary["safety_envelope_valid_count"] == 1
        and summary["rollback_verified_count"] == 1
        and summary["mentor_override_available_count"] == 1
        and summary["exploration_allowed_count"] == 1
        and summary["audit_trace_required_count"] == 1
        and summary["obstacle_candidate_pass_count"] == 1
        and summary["costly_retry_candidate_pass_count"] == 1
        and summary["unclear_failure_candidate_pass_count"] == 1
        and summary["bad_gate_status_blocked_count"] == 1
        and summary["missing_gated_candidate_blocked_count"] == 1
        and summary["wrong_mapping_blocked_count"] == 3
        and summary["gate_passed_false_blocked_count"] == 1
        and summary["empty_gate_reason_blocked_count"] == 1
        and summary["adjacent_review_false_blocked_count"] == 1
        and summary["runtime_action_selection_allowed_blocked_count"] == 1
        and summary["final_action_allowed_blocked_count"] == 1
        and summary["action_execution_allowed_blocked_count"] == 1
        and summary["candidate_result_valid_false_blocked_count"] == 1
        and summary["safety_envelope_valid_false_blocked_count"] == 1
        and summary["rollback_verified_false_blocked_count"] == 1
        and summary["mentor_override_available_false_blocked_count"] == 1
        and summary["exploration_allowed_false_blocked_count"] == 1
        and summary["audit_trace_required_false_blocked_count"] == 1
        and summary["no_final_action_gate_false_blocked_count"] == 1
        and summary["no_action_execution_gate_false_blocked_count"] == 1
        and summary["may_enter_runtime_action_selection_blocked_count"] == 1
        and summary["may_create_final_action_blocked_count"] == 1
        and summary["may_execute_action_blocked_count"] == 1
        and summary["may_create_direct_command_blocked_count"] == 1
        and summary["may_write_persistent_policy_blocked_count"] == 1
        and summary["empty_why_it_passed_blocked_count"] == 1
        and summary["empty_plain_result_blocked_count"] == 1
        and summary["production_action_selection_blocked_count"] == 1
        and summary["runtime_action_selection_flag_blocked_count"] == 1
        and summary["final_action_created_blocked_count"] == 1
        and summary["action_selected_blocked_count"] == 1
        and summary["action_executed_blocked_count"] == 1
        and summary["direct_action_command_blocked_count"] == 1
        and summary["real_navigation_changed_blocked_count"] == 1
        and summary["ui_behavior_changed_blocked_count"] == 1
        and summary["persistent_policy_written_blocked_count"] == 1
        and summary["general_behavior_changed_blocked_count"] == 1
        and summary["semantic_or_fuzzy_match_used_blocked_count"] == 1
        and summary["exploration_blocked_count"] == 1
        and summary["curiosity_overridden_blocked_count"] == 1
        and summary["mentor_override_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["new_retention_written_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "pre_action_consideration_gate_enabled": True,
        "gated_candidate_count": summary["gated_candidate_count"],
        "gate_passed_candidate_count": summary["gate_passed_candidate_count"],
        "allowed_for_action_selection_adjacent_review_count": summary[
            "allowed_for_action_selection_adjacent_review_count"
        ],
        "runtime_action_selection_added": False,
        "final_action_creation_added": False,
        "action_selection_added": False,
        "action_execution_added": False,
        "direct_action_command_added": False,
        "persistent_policy_write_added": False,
        "general_behavior_change_added": False,
        "semantic_or_fuzzy_matching_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "top_level_field_count": len(REQUIRED_FIELDS),
    }


def _candidate_pass_count(candidate_validations: list[dict[str, Any]], scenario_id: str) -> int:
    return sum(
        1 for result in candidate_validations if result["scenario_id"] == scenario_id and result["candidate_pass"]
    )


def _blocked_flag_values(blocked_flags: dict[str, Any]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_errors_ending(validation_results: list[dict[str, Any]], suffix: str) -> int:
    return sum(1 for result in validation_results for error in result["error_codes"] if error.endswith(suffix))
