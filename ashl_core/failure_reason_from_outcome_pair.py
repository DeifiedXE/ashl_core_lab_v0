"""Build v0-local failure_reason records from valid outcome pairs."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .expected_actual_outcome_pair_schema import validate_expected_actual_outcome_pair
from .outcome_pair_from_action_trial_trace import (
    build_expected_actual_outcome_pair_from_trial_trace,
    build_valid_mismatch_trial_trace,
    build_valid_no_mismatch_trial_trace,
)


COMMAND = "run-failure-reason-from-outcome-pair-check"
FLOW = "failure_reason_from_outcome_pair_v0"

ALLOWED_CATEGORIES = {
    "actual_outcome_did_not_match_expected_outcome",
    "actual_outcome_unknown",
    "expected_outcome_unknown",
    "blocked_or_unmet_expected_outcome",
}

REQUIRED_FIELDS = {
    "failure_reason_id",
    "source_pair_id",
    "action_intent_id",
    "category",
    "description",
    "evidence",
    "known",
    "source_trace",
    "review_boundary",
    "safety_flags",
}

REQUIRED_EVIDENCE_FIELDS = {
    "source_pair_id",
    "expected_outcome_id",
    "actual_outcome_id",
    "mismatch",
    "comparison_rule",
}

REQUIRED_REVIEW_BOUNDARY_FIELDS = {
    "review_required",
    "lesson_candidate_allowed",
    "lesson_application_allowed",
    "persistent_learning_allowed",
    "memory_write_allowed",
    "predictor_mutation_allowed",
}

REQUIRED_SAFETY_FLAGS = {
    "trace_only",
    "blocked_from_action_selection",
    "blocked_from_action_behavior_change",
    "blocked_from_lesson_application",
    "blocked_from_memory_write",
    "blocked_from_predictor_mutation",
    "blocked_from_persistent_rule_write",
    "lesson_candidate_created",
    "action_selection_influence",
    "action_behavior_changed",
    "lesson_application_runtime",
    "memory_write",
    "predictor_modified",
    "persistent_rule_write",
    "endocrine_control",
    "autonomy_enabled",
}

RUNTIME_FLAGS = {
    "action_selection_influence",
    "action_behavior_changed",
    "lesson_application_runtime",
    "lesson_candidate_created",
    "memory_write",
    "predictor_modified",
    "persistent_rule_write",
    "endocrine_control",
    "autonomy_enabled",
}


def build_failure_reason_from_outcome_pair(outcome_pair: dict[str, Any]) -> dict[str, Any] | None:
    pair_validation = validate_expected_actual_outcome_pair(outcome_pair)
    if not pair_validation["valid"]:
        raise ValueError("invalid_outcome_pair")
    if outcome_pair.get("mismatch") is False:
        return None
    if outcome_pair.get("mismatch") is not True:
        raise ValueError("invalid_outcome_pair")

    embedded_reason = outcome_pair.get("failure_reason") or {}
    category = embedded_reason.get("category")
    if category not in ALLOWED_CATEGORIES:
        category = "actual_outcome_did_not_match_expected_outcome"

    source_pair_id = outcome_pair["pair_id"]
    expected_outcome = outcome_pair["expected_outcome"]
    actual_outcome = outcome_pair["actual_outcome"]
    evidence = dict(embedded_reason.get("evidence") or {})
    evidence.update(
        {
            "source_pair_id": source_pair_id,
            "expected_outcome_id": expected_outcome.get("outcome_id"),
            "actual_outcome_id": actual_outcome.get("outcome_id"),
            "comparison_rule": evidence.get("comparison_rule")
            or (outcome_pair.get("source_trace") or {}).get("comparison_rule")
            or "structured_state_equality",
            "mismatch": True,
        }
    )
    action_intent = outcome_pair.get("action_intent") or {}
    return {
        "failure_reason_id": f"failure_reason:{source_pair_id}",
        "source_pair_id": source_pair_id,
        "action_intent_id": action_intent.get("action_intent_id"),
        "category": category,
        "description": embedded_reason.get("description")
        or "Actual outcome state differs from expected outcome state.",
        "evidence": evidence,
        "known": embedded_reason.get("known") is True,
        "source_trace": {
            "source": "failure_reason_from_outcome_pair",
            "outcome_pair_schema": "expected_actual_outcome_pair_schema",
            "source_pair_id": source_pair_id,
        },
        "review_boundary": _build_review_boundary(),
        "safety_flags": _build_safety_flags(),
    }


def validate_failure_reason_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    if record.get("category") not in ALLOWED_CATEGORIES:
        errors.append("unknown_category")
    if "known" in record and not isinstance(record.get("known"), bool):
        errors.append("known_not_boolean")

    evidence = record.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("missing_evidence")
        evidence = {}
    for field in sorted(REQUIRED_EVIDENCE_FIELDS):
        if field not in evidence:
            errors.append(f"missing_evidence_field:{field}")
    if evidence.get("source_pair_id") != record.get("source_pair_id"):
        errors.append("evidence_source_pair_mismatch")
    if evidence.get("mismatch") is not True:
        errors.append("evidence_mismatch_not_true")
    if not evidence.get("comparison_rule"):
        errors.append("evidence_comparison_rule_missing")

    _validate_source_trace(record.get("source_trace"), record.get("source_pair_id"), errors)
    review_boundary = _validate_review_boundary(record.get("review_boundary"), errors)
    safety_flags = _validate_safety_flags(record.get("safety_flags"), errors)

    return {
        "failure_reason_id": record.get("failure_reason_id"),
        "source_pair_id": record.get("source_pair_id"),
        "valid": not errors,
        "error_codes": errors,
        "category": record.get("category"),
        "known": record.get("known") is True,
        "review_required": review_boundary.get("review_required") is True,
        "trace_only": safety_flags.get("trace_only") is True,
        "lesson_candidate_created": safety_flags.get("lesson_candidate_created") is True,
        "action_selection_influence": safety_flags.get("action_selection_influence") is True,
        "action_behavior_changed": safety_flags.get("action_behavior_changed") is True,
        "lesson_application_runtime": safety_flags.get("lesson_application_runtime") is True,
        "memory_write": safety_flags.get("memory_write") is True,
        "predictor_modified": safety_flags.get("predictor_modified") is True,
        "persistent_rule_write": safety_flags.get("persistent_rule_write") is True,
        "endocrine_control": safety_flags.get("endocrine_control") is True,
        "autonomy_enabled": safety_flags.get("autonomy_enabled") is True,
    }


def run_failure_reason_from_outcome_pair_check() -> dict[str, Any]:
    outcome_pairs = _build_demo_outcome_pairs()
    pair_results = [_process_outcome_pair(pair) for pair in outcome_pairs]
    valid_reason = next(result["failure_reason"] for result in pair_results if result.get("failure_reason"))
    failure_reason_records = [valid_reason] + _build_invalid_failure_reason_records(valid_reason)
    validation_results = [validate_failure_reason_record(record) for record in failure_reason_records]
    summary = _build_summary(pair_results, validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "outcome_pairs": outcome_pairs,
        "pair_results": pair_results,
        "failure_reason_records": failure_reason_records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check builds independent v0-local failure_reason records from valid mismatch outcome pairs.",
            "mismatch false pairs produce no failure_reason and are counted as no_failure_reason_needed.",
            "Invalid outcome pairs do not produce valid failure_reason records.",
            "No lesson_candidate, action selection, behavior change, lesson application, memory write, predictor mutation, endocrine control, or autonomy is added.",
        ],
    }


def _build_demo_outcome_pairs() -> list[dict[str, Any]]:
    valid_mismatch = build_expected_actual_outcome_pair_from_trial_trace(build_valid_mismatch_trial_trace())
    valid_no_mismatch = build_expected_actual_outcome_pair_from_trial_trace(build_valid_no_mismatch_trial_trace())
    invalid_pair = deepcopy(valid_mismatch)
    invalid_pair["case_name"] = "invalid_unknown_vs_unknown_outcome_pair"
    invalid_pair["pair_id"] = "outcome_pair:invalid:unknown_vs_unknown"
    invalid_pair["expected_outcome"]["known"] = False
    invalid_pair["actual_outcome"]["known"] = False
    return [valid_mismatch, valid_no_mismatch, invalid_pair]


def _process_outcome_pair(outcome_pair: dict[str, Any]) -> dict[str, Any]:
    pair_validation = validate_expected_actual_outcome_pair(outcome_pair)
    try:
        failure_reason = build_failure_reason_from_outcome_pair(outcome_pair)
    except ValueError as exc:
        return {
            "case_name": outcome_pair.get("case_name"),
            "pair_id": outcome_pair.get("pair_id"),
            "pair_validation": pair_validation,
            "valid_outcome_pair": False,
            "failure_reason": None,
            "failure_reason_needed": False,
            "no_failure_reason_needed": False,
            "blocked_reason": str(exc),
        }
    return {
        "case_name": outcome_pair.get("case_name"),
        "pair_id": outcome_pair.get("pair_id"),
        "pair_validation": pair_validation,
        "valid_outcome_pair": pair_validation["valid"],
        "failure_reason": failure_reason,
        "failure_reason_needed": outcome_pair.get("mismatch") is True,
        "no_failure_reason_needed": outcome_pair.get("mismatch") is False and failure_reason is None,
        "blocked_reason": None,
    }


def _build_invalid_failure_reason_records(valid_reason: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    missing_source_pair = _copy_case(valid_reason, "missing_source_pair")
    missing_source_pair.pop("source_pair_id")
    records.append(missing_source_pair)

    unknown_category = _copy_case(valid_reason, "unknown_category")
    unknown_category["category"] = "free_form_unknown_failure"
    records.append(unknown_category)

    missing_evidence = _copy_case(valid_reason, "missing_evidence")
    missing_evidence.pop("evidence")
    records.append(missing_evidence)

    review_required_false = _copy_case(valid_reason, "review_required_false")
    review_required_false["review_boundary"]["review_required"] = False
    records.append(review_required_false)

    lesson_candidate_created = _copy_case(valid_reason, "lesson_candidate_created")
    lesson_candidate_created["safety_flags"]["lesson_candidate_created"] = True
    records.append(lesson_candidate_created)

    action_selection_unblocked = _copy_case(valid_reason, "action_selection_unblocked")
    action_selection_unblocked["safety_flags"]["blocked_from_action_selection"] = False
    records.append(action_selection_unblocked)

    lesson_application_unblocked = _copy_case(valid_reason, "lesson_application_unblocked")
    lesson_application_unblocked["review_boundary"]["lesson_application_allowed"] = True
    records.append(lesson_application_unblocked)

    memory_write_unblocked = _copy_case(valid_reason, "memory_write_unblocked")
    memory_write_unblocked["review_boundary"]["memory_write_allowed"] = True
    memory_write_unblocked["safety_flags"]["memory_write"] = True
    records.append(memory_write_unblocked)

    predictor_mutation_unblocked = _copy_case(valid_reason, "predictor_mutation_unblocked")
    predictor_mutation_unblocked["review_boundary"]["predictor_mutation_allowed"] = True
    predictor_mutation_unblocked["safety_flags"]["predictor_modified"] = True
    records.append(predictor_mutation_unblocked)

    persistent_rule_write_unblocked = _copy_case(valid_reason, "persistent_rule_write_unblocked")
    persistent_rule_write_unblocked["safety_flags"]["blocked_from_persistent_rule_write"] = False
    persistent_rule_write_unblocked["safety_flags"]["persistent_rule_write"] = True
    records.append(persistent_rule_write_unblocked)

    return records


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["case_name"] = case_name
    copied["failure_reason_id"] = f"{record['failure_reason_id']}:{case_name}"
    return copied


def _build_review_boundary() -> dict[str, bool]:
    return {
        "review_required": True,
        "lesson_candidate_allowed": True,
        "lesson_application_allowed": False,
        "persistent_learning_allowed": False,
        "memory_write_allowed": False,
        "predictor_mutation_allowed": False,
    }


def _build_safety_flags() -> dict[str, bool]:
    return {
        "trace_only": True,
        "blocked_from_action_selection": True,
        "blocked_from_action_behavior_change": True,
        "blocked_from_lesson_application": True,
        "blocked_from_memory_write": True,
        "blocked_from_predictor_mutation": True,
        "blocked_from_persistent_rule_write": True,
        "lesson_candidate_created": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "lesson_application_runtime": False,
        "memory_write": False,
        "predictor_modified": False,
        "persistent_rule_write": False,
        "endocrine_control": False,
        "autonomy_enabled": False,
    }


def _validate_source_trace(source_trace: Any, source_pair_id: Any, errors: list[str]) -> None:
    if not isinstance(source_trace, dict):
        errors.append("source_trace_missing_or_not_dict")
        return
    if source_trace.get("source") != "failure_reason_from_outcome_pair":
        errors.append("invalid_source_trace_source")
    if source_trace.get("outcome_pair_schema") != "expected_actual_outcome_pair_schema":
        errors.append("invalid_source_trace_outcome_pair_schema")
    if source_trace.get("source_pair_id") != source_pair_id:
        errors.append("source_trace_source_pair_mismatch")


def _validate_review_boundary(review_boundary: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(review_boundary, dict):
        errors.append("review_boundary_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_REVIEW_BOUNDARY_FIELDS):
        if field not in review_boundary:
            errors.append(f"review_boundary_missing_field:{field}")
    if review_boundary.get("review_required") is not True:
        errors.append("review_required_not_true")
    if review_boundary.get("lesson_candidate_allowed") is not True:
        errors.append("lesson_candidate_allowed_not_true")
    if review_boundary.get("lesson_application_allowed") is not False:
        errors.append("lesson_application_allowed_enabled")
    if review_boundary.get("persistent_learning_allowed") is not False:
        errors.append("persistent_learning_allowed_enabled")
    if review_boundary.get("memory_write_allowed") is not False:
        errors.append("memory_write_allowed_enabled")
    if review_boundary.get("predictor_mutation_allowed") is not False:
        errors.append("predictor_mutation_allowed_enabled")
    return review_boundary


def _validate_safety_flags(safety_flags: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(safety_flags, dict):
        errors.append("safety_flags_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_SAFETY_FLAGS):
        if field not in safety_flags:
            errors.append(f"missing_safety_flag:{field}")
    required_true_flags = {
        "trace_only": "trace_only_not_true",
        "blocked_from_action_selection": "action_selection_not_blocked",
        "blocked_from_action_behavior_change": "action_behavior_change_not_blocked",
        "blocked_from_lesson_application": "lesson_application_not_blocked",
        "blocked_from_memory_write": "memory_write_not_blocked",
        "blocked_from_predictor_mutation": "predictor_mutation_not_blocked",
        "blocked_from_persistent_rule_write": "persistent_rule_write_not_blocked",
    }
    for flag, error_code in required_true_flags.items():
        if safety_flags.get(flag) is not True:
            errors.append(error_code)
    for flag in sorted(RUNTIME_FLAGS):
        if safety_flags.get(flag) not in {False, 0}:
            errors.append(f"{flag}_enabled")
    return safety_flags


def _build_summary(
    pair_results: list[dict[str, Any]],
    validation_results: list[dict[str, Any]],
) -> dict[str, int]:
    valid_pair_results = [result for result in pair_results if result["valid_outcome_pair"]]
    valid_reason_results = [result for result in validation_results if result["valid"]]
    return {
        "outcome_pair_count": len(pair_results),
        "valid_outcome_pair_count": len(valid_pair_results),
        "invalid_outcome_pair_count": sum(1 for result in pair_results if not result["valid_outcome_pair"]),
        "mismatch_true_pair_count": sum(
            1 for result in valid_pair_results if result["pair_validation"]["mismatch"] is True
        ),
        "mismatch_false_pair_count": sum(
            1 for result in valid_pair_results if result["pair_validation"]["mismatch"] is False
        ),
        "failure_reason_record_count": len(validation_results),
        "valid_failure_reason_count": len(valid_reason_results),
        "invalid_failure_reason_count": sum(1 for result in validation_results if not result["valid"]),
        "no_failure_reason_needed_count": sum(1 for result in pair_results if result["no_failure_reason_needed"]),
        "missing_source_pair_blocked_count": _count_error(validation_results, "missing_required_field:source_pair_id"),
        "unknown_category_blocked_count": _count_error(validation_results, "unknown_category"),
        "missing_evidence_blocked_count": _count_error(validation_results, "missing_evidence"),
        "review_boundary_violation_blocked_count": _count_error(validation_results, "review_required_not_true"),
        "lesson_candidate_created_blocked_count": _count_error(
            validation_results, "lesson_candidate_created_enabled"
        ),
        "action_selection_unblocked_blocked_count": _count_error(validation_results, "action_selection_not_blocked"),
        "lesson_application_unblocked_blocked_count": _count_error(
            validation_results, "lesson_application_allowed_enabled"
        ),
        "memory_write_unblocked_blocked_count": _count_error(validation_results, "memory_write_allowed_enabled"),
        "predictor_mutation_unblocked_blocked_count": _count_error(
            validation_results, "predictor_mutation_allowed_enabled"
        ),
        "persistent_rule_write_unblocked_blocked_count": _count_error(
            validation_results, "persistent_rule_write_not_blocked"
        ),
        "action_selection_influence_count": _count_valid_flag(valid_reason_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_reason_results, "action_behavior_changed"),
        "lesson_application_runtime_count": _count_valid_flag(valid_reason_results, "lesson_application_runtime"),
        "lesson_candidate_created_count": _count_valid_flag(valid_reason_results, "lesson_candidate_created"),
        "memory_write_count": _count_valid_flag(valid_reason_results, "memory_write"),
        "predictor_modified_count": _count_valid_flag(valid_reason_results, "predictor_modified"),
        "persistent_rule_write_count": _count_valid_flag(valid_reason_results, "persistent_rule_write"),
        "endocrine_control_count": _count_valid_flag(valid_reason_results, "endocrine_control"),
        "autonomy_enabled_count": _count_valid_flag(valid_reason_results, "autonomy_enabled"),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["outcome_pair_count"] == 3
        and summary["valid_outcome_pair_count"] == 2
        and summary["invalid_outcome_pair_count"] == 1
        and summary["mismatch_true_pair_count"] >= 1
        and summary["mismatch_false_pair_count"] >= 1
        and summary["failure_reason_record_count"] == 11
        and summary["valid_failure_reason_count"] == 1
        and summary["invalid_failure_reason_count"] == 10
        and summary["no_failure_reason_needed_count"] >= 1
        and summary["missing_source_pair_blocked_count"] >= 1
        and summary["unknown_category_blocked_count"] >= 1
        and summary["missing_evidence_blocked_count"] >= 1
        and summary["review_boundary_violation_blocked_count"] >= 1
        and summary["lesson_candidate_created_blocked_count"] >= 1
        and summary["action_selection_unblocked_blocked_count"] >= 1
        and summary["lesson_application_unblocked_blocked_count"] >= 1
        and summary["memory_write_unblocked_blocked_count"] >= 1
        and summary["predictor_mutation_unblocked_blocked_count"] >= 1
        and summary["persistent_rule_write_unblocked_blocked_count"] >= 1
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["lesson_application_runtime_count"] == 0
        and summary["lesson_candidate_created_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["persistent_rule_write_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["autonomy_enabled_count"] == 0
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "failure_reason_from_outcome_pair_enabled": True,
        "trace_check_only": True,
        "uses_outcome_pair_from_action_trial_trace": True,
        "uses_expected_actual_outcome_pair_schema": True,
        "v0_local_failure_reason_validator": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "lesson_candidate_generation_added": False,
        "runtime_action_selection_added": False,
        "action_selection_modified": False,
        "new_action_behavior_added": False,
        "lesson_application_runtime_added": False,
        "automatic_lesson_application_added": False,
        "persistent_learning_added": False,
        "persistent_rule_write_added": False,
        "memory_write_added": False,
        "predictor_mutation_added": False,
        "perception_to_action_bridge_added": False,
        "focus_to_action_bridge_added": False,
        "active_focus_selection_added": False,
        "focus_application_added": False,
        "focus_applied_added": False,
        "attention_control_added": False,
        "endocrine_runtime_added": False,
        "endocrine_controlled_action_added": False,
        "autonomy_added": False,
        "semantic_vision_claimed": False,
        "consciousness_claimed": False,
        "subjective_claims_added": False,
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "lesson_application_runtime_count": summary["lesson_application_runtime_count"],
        "lesson_candidate_created_count": summary["lesson_candidate_created_count"],
        "memory_write_count": summary["memory_write_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "persistent_rule_write_count": summary["persistent_rule_write_count"],
        "endocrine_control_count": summary["endocrine_control_count"],
        "autonomy_enabled_count": summary["autonomy_enabled_count"],
    }


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
