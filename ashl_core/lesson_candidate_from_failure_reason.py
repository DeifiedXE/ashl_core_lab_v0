"""Build trace-only lesson_candidate records from valid failure_reason records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .failure_reason_from_outcome_pair import (
    run_failure_reason_from_outcome_pair_check,
    validate_failure_reason_record,
)


COMMAND = "run-lesson-candidate-from-failure-reason-check"
FLOW = "lesson_candidate_from_failure_reason_v0"

ALLOWED_CANDIDATE_TYPES = {
    "precondition_or_correction",
    "avoid_repeat_failure",
    "ask_for_help_before_retry",
}

ALLOWED_CORRECTION_TYPES = {
    "check_before_retry",
    "require_precondition_check",
    "ask_for_help",
    "avoid_same_retry",
}

REQUIRED_FIELDS = {
    "lesson_candidate_id",
    "source_failure_reason_id",
    "source_pair_id",
    "action_intent_id",
    "candidate_type",
    "proposed_correction",
    "applicability",
    "confidence",
    "source_trace",
    "review_boundary",
    "safety_flags",
}

REQUIRED_REVIEW_BOUNDARY_FIELDS = {
    "review_required",
    "approved",
    "rejected",
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
    "approved_lesson",
    "lesson_applied",
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
    "memory_write",
    "predictor_modified",
    "persistent_rule_write",
    "endocrine_control",
    "autonomy_enabled",
}


def build_lesson_candidate_from_failure_reason(failure_reason: dict[str, Any]) -> dict[str, Any]:
    failure_validation = validate_failure_reason_record(failure_reason)
    if not failure_validation["valid"]:
        raise ValueError("invalid_failure_reason")

    source_failure_reason_id = failure_reason["failure_reason_id"]
    target_action_type = _target_action_type(failure_reason)
    return {
        "lesson_candidate_id": f"lesson_candidate:{source_failure_reason_id}",
        "source_failure_reason_id": source_failure_reason_id,
        "source_pair_id": failure_reason.get("source_pair_id"),
        "action_intent_id": failure_reason.get("action_intent_id"),
        "candidate_type": "precondition_or_correction",
        "proposed_correction": {
            "correction_type": "check_before_retry",
            "description": "Check whether the expected action target is reachable before retrying.",
            "target_action_type": target_action_type,
            "candidate_description_only": True,
            "correction_applied": False,
        },
        "applicability": {
            "source_category": failure_reason.get("category"),
            "requires_human_review": True,
            "generalization_allowed": False,
            "persistent_candidate_allowed": False,
        },
        "confidence": {
            "value": 0.0,
            "basis": "single_demo_failure_reason",
            "runtime_confidence": False,
        },
        "source_trace": {
            "source": "lesson_candidate_from_failure_reason",
            "failure_reason_source": "failure_reason_from_outcome_pair",
            "source_failure_reason_id": source_failure_reason_id,
        },
        "review_boundary": _build_review_boundary(),
        "safety_flags": _build_safety_flags(),
    }


def validate_lesson_candidate_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    if record.get("candidate_type") not in ALLOWED_CANDIDATE_TYPES:
        errors.append("unknown_candidate_type")

    proposed_correction = record.get("proposed_correction")
    if not isinstance(proposed_correction, dict):
        errors.append("proposed_correction_missing_or_not_dict")
        proposed_correction = {}
    if proposed_correction.get("correction_type") not in ALLOWED_CORRECTION_TYPES:
        errors.append("unknown_correction_type")
    if proposed_correction.get("candidate_description_only") is not True:
        errors.append("proposed_correction_not_description_only")
    if proposed_correction.get("correction_applied") not in {False, 0}:
        errors.append("correction_applied_enabled")

    _validate_applicability(record.get("applicability"), errors)
    _validate_confidence(record.get("confidence"), errors)
    _validate_source_trace(record.get("source_trace"), record.get("source_failure_reason_id"), errors)
    review_boundary = _validate_review_boundary(record.get("review_boundary"), errors)
    safety_flags = _validate_safety_flags(record.get("safety_flags"), errors)

    return {
        "lesson_candidate_id": record.get("lesson_candidate_id"),
        "source_failure_reason_id": record.get("source_failure_reason_id"),
        "source_pair_id": record.get("source_pair_id"),
        "action_intent_id": record.get("action_intent_id"),
        "valid": not errors,
        "error_codes": errors,
        "candidate_type": record.get("candidate_type"),
        "correction_type": proposed_correction.get("correction_type"),
        "review_required": review_boundary.get("review_required") is True,
        "approved": review_boundary.get("approved") is True,
        "rejected": review_boundary.get("rejected") is True,
        "trace_only": safety_flags.get("trace_only") is True,
        "approved_lesson": safety_flags.get("approved_lesson") is True,
        "lesson_applied": safety_flags.get("lesson_applied") is True,
        "action_selection_influence": safety_flags.get("action_selection_influence") is True,
        "action_behavior_changed": safety_flags.get("action_behavior_changed") is True,
        "lesson_application_runtime": safety_flags.get("lesson_application_runtime") is True,
        "memory_write": safety_flags.get("memory_write") is True,
        "predictor_modified": safety_flags.get("predictor_modified") is True,
        "persistent_rule_write": safety_flags.get("persistent_rule_write") is True,
        "endocrine_control": safety_flags.get("endocrine_control") is True,
        "autonomy_enabled": safety_flags.get("autonomy_enabled") is True,
    }


def run_lesson_candidate_from_failure_reason_check() -> dict[str, Any]:
    failure_reason_result = run_failure_reason_from_outcome_pair_check()
    failure_reason_records = failure_reason_result["failure_reason_records"]
    failure_results = [_process_failure_reason(record) for record in failure_reason_records]
    valid_candidate = next(result["lesson_candidate"] for result in failure_results if result.get("lesson_candidate"))
    lesson_candidate_records = [valid_candidate] + _build_invalid_lesson_candidate_records(valid_candidate)
    validation_results = [validate_lesson_candidate_record(record) for record in lesson_candidate_records]
    summary = _build_summary(failure_results, validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "failure_reason_records": failure_reason_records,
        "failure_results": failure_results,
        "lesson_candidate_records": lesson_candidate_records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check builds trace-only review-required lesson_candidate records from valid failure_reason records.",
            "Invalid failure_reason records do not produce valid lesson_candidate records.",
            "Generated candidates are not approved, applied, persisted, written to memory, used for action selection, or used to mutate predictors.",
        ],
    }


def _process_failure_reason(failure_reason: dict[str, Any]) -> dict[str, Any]:
    failure_validation = validate_failure_reason_record(failure_reason)
    try:
        lesson_candidate = build_lesson_candidate_from_failure_reason(failure_reason)
    except ValueError as exc:
        return {
            "failure_reason_id": failure_reason.get("failure_reason_id"),
            "failure_validation": failure_validation,
            "valid_failure_reason": False,
            "lesson_candidate": None,
            "candidate_generated": False,
            "blocked_reason": str(exc),
        }
    return {
        "failure_reason_id": failure_reason.get("failure_reason_id"),
        "failure_validation": failure_validation,
        "valid_failure_reason": failure_validation["valid"],
        "lesson_candidate": lesson_candidate,
        "candidate_generated": True,
        "blocked_reason": None,
    }


def _build_invalid_lesson_candidate_records(valid_candidate: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    missing_source = _copy_case(valid_candidate, "missing_failure_reason_source")
    missing_source.pop("source_failure_reason_id")
    records.append(missing_source)

    unknown_candidate_type = _copy_case(valid_candidate, "unknown_candidate_type")
    unknown_candidate_type["candidate_type"] = "free_form_lesson"
    records.append(unknown_candidate_type)

    unknown_correction_type = _copy_case(valid_candidate, "unknown_correction_type")
    unknown_correction_type["proposed_correction"]["correction_type"] = "move_anyway"
    records.append(unknown_correction_type)

    review_required_false = _copy_case(valid_candidate, "review_required_false")
    review_required_false["review_boundary"]["review_required"] = False
    records.append(review_required_false)

    approved_true = _copy_case(valid_candidate, "approved_true")
    approved_true["review_boundary"]["approved"] = True
    approved_true["safety_flags"]["approved_lesson"] = True
    records.append(approved_true)

    lesson_application_allowed = _copy_case(valid_candidate, "lesson_application_allowed")
    lesson_application_allowed["review_boundary"]["lesson_application_allowed"] = True
    records.append(lesson_application_allowed)

    persistent_learning_allowed = _copy_case(valid_candidate, "persistent_learning_allowed")
    persistent_learning_allowed["review_boundary"]["persistent_learning_allowed"] = True
    records.append(persistent_learning_allowed)

    memory_write_allowed = _copy_case(valid_candidate, "memory_write_allowed")
    memory_write_allowed["review_boundary"]["memory_write_allowed"] = True
    memory_write_allowed["safety_flags"]["memory_write"] = True
    records.append(memory_write_allowed)

    predictor_mutation_allowed = _copy_case(valid_candidate, "predictor_mutation_allowed")
    predictor_mutation_allowed["review_boundary"]["predictor_mutation_allowed"] = True
    predictor_mutation_allowed["safety_flags"]["predictor_modified"] = True
    records.append(predictor_mutation_allowed)

    action_selection_unblocked = _copy_case(valid_candidate, "action_selection_unblocked")
    action_selection_unblocked["safety_flags"]["blocked_from_action_selection"] = False
    records.append(action_selection_unblocked)

    lesson_applied = _copy_case(valid_candidate, "lesson_applied")
    lesson_applied["safety_flags"]["lesson_applied"] = True
    records.append(lesson_applied)

    action_selection_influence = _copy_case(valid_candidate, "action_selection_influence")
    action_selection_influence["safety_flags"]["action_selection_influence"] = True
    records.append(action_selection_influence)

    return records


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["case_name"] = case_name
    copied["lesson_candidate_id"] = f"{record['lesson_candidate_id']}:{case_name}"
    return copied


def _target_action_type(failure_reason: dict[str, Any]) -> str:
    action_intent_id = failure_reason.get("action_intent_id")
    return "move" if action_intent_id else "unknown"


def _build_review_boundary() -> dict[str, bool]:
    return {
        "review_required": True,
        "approved": False,
        "rejected": False,
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
        "approved_lesson": False,
        "lesson_applied": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "lesson_application_runtime": False,
        "memory_write": False,
        "predictor_modified": False,
        "persistent_rule_write": False,
        "endocrine_control": False,
        "autonomy_enabled": False,
    }


def _validate_applicability(applicability: Any, errors: list[str]) -> None:
    if not isinstance(applicability, dict):
        errors.append("applicability_missing_or_not_dict")
        return
    if applicability.get("requires_human_review") is not True:
        errors.append("requires_human_review_not_true")
    if applicability.get("generalization_allowed") is not False:
        errors.append("generalization_allowed_enabled")
    if applicability.get("persistent_candidate_allowed") is not False:
        errors.append("persistent_candidate_allowed_enabled")
    if not applicability.get("source_category"):
        errors.append("applicability_source_category_missing")


def _validate_confidence(confidence: Any, errors: list[str]) -> None:
    if not isinstance(confidence, dict):
        errors.append("confidence_missing_or_not_dict")
        return
    if confidence.get("value") != 0.0:
        errors.append("confidence_value_not_zero")
    if confidence.get("basis") != "single_demo_failure_reason":
        errors.append("confidence_basis_invalid")
    if confidence.get("runtime_confidence") is not False:
        errors.append("runtime_confidence_enabled")


def _validate_source_trace(source_trace: Any, source_failure_reason_id: Any, errors: list[str]) -> None:
    if not isinstance(source_trace, dict):
        errors.append("source_trace_missing_or_not_dict")
        return
    if source_trace.get("source") != "lesson_candidate_from_failure_reason":
        errors.append("invalid_source_trace_source")
    if source_trace.get("failure_reason_source") != "failure_reason_from_outcome_pair":
        errors.append("invalid_failure_reason_source")
    if source_trace.get("source_failure_reason_id") != source_failure_reason_id:
        errors.append("source_trace_failure_reason_mismatch")


def _validate_review_boundary(review_boundary: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(review_boundary, dict):
        errors.append("review_boundary_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_REVIEW_BOUNDARY_FIELDS):
        if field not in review_boundary:
            errors.append(f"review_boundary_missing_field:{field}")
    if review_boundary.get("review_required") is not True:
        errors.append("review_required_not_true")
    if review_boundary.get("approved") is not False:
        errors.append("approved_enabled")
    if review_boundary.get("rejected") is not False:
        errors.append("rejected_enabled")
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
    if safety_flags.get("approved_lesson") not in {False, 0}:
        errors.append("approved_lesson_enabled")
    if safety_flags.get("lesson_applied") not in {False, 0}:
        errors.append("lesson_applied_enabled")
    for flag in sorted(RUNTIME_FLAGS):
        if safety_flags.get(flag) not in {False, 0}:
            errors.append(f"{flag}_enabled")
    return safety_flags


def _build_summary(
    failure_results: list[dict[str, Any]],
    validation_results: list[dict[str, Any]],
) -> dict[str, int]:
    valid_failure_results = [result for result in failure_results if result["valid_failure_reason"]]
    valid_candidate_results = [result for result in validation_results if result["valid"]]
    return {
        "failure_reason_record_count": len(failure_results),
        "valid_failure_reason_count": len(valid_failure_results),
        "invalid_failure_reason_count": sum(1 for result in failure_results if not result["valid_failure_reason"]),
        "generated_lesson_candidate_count": sum(1 for result in failure_results if result["candidate_generated"]),
        "valid_lesson_candidate_count": len(valid_candidate_results),
        "invalid_lesson_candidate_count": sum(1 for result in validation_results if not result["valid"]),
        "missing_failure_reason_source_blocked_count": _count_error(
            validation_results, "missing_required_field:source_failure_reason_id"
        ),
        "unknown_candidate_type_blocked_count": _count_error(validation_results, "unknown_candidate_type"),
        "unknown_correction_type_blocked_count": _count_error(validation_results, "unknown_correction_type"),
        "review_required_missing_blocked_count": _count_error(validation_results, "review_required_not_true"),
        "approved_lesson_blocked_count": _count_error(validation_results, "approved_lesson_enabled"),
        "lesson_application_allowed_blocked_count": _count_error(
            validation_results, "lesson_application_allowed_enabled"
        ),
        "persistent_learning_allowed_blocked_count": _count_error(
            validation_results, "persistent_learning_allowed_enabled"
        ),
        "memory_write_allowed_blocked_count": _count_error(validation_results, "memory_write_allowed_enabled"),
        "predictor_mutation_allowed_blocked_count": _count_error(
            validation_results, "predictor_mutation_allowed_enabled"
        ),
        "action_selection_unblocked_blocked_count": _count_error(validation_results, "action_selection_not_blocked"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "action_selection_influence_count": _count_valid_flag(valid_candidate_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_candidate_results, "action_behavior_changed"),
        "lesson_application_runtime_count": _count_valid_flag(valid_candidate_results, "lesson_application_runtime"),
        "memory_write_count": _count_valid_flag(valid_candidate_results, "memory_write"),
        "predictor_modified_count": _count_valid_flag(valid_candidate_results, "predictor_modified"),
        "persistent_rule_write_count": _count_valid_flag(valid_candidate_results, "persistent_rule_write"),
        "endocrine_control_count": _count_valid_flag(valid_candidate_results, "endocrine_control"),
        "autonomy_enabled_count": _count_valid_flag(valid_candidate_results, "autonomy_enabled"),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["failure_reason_record_count"] == 11
        and summary["valid_failure_reason_count"] >= 1
        and summary["invalid_failure_reason_count"] == 10
        and summary["generated_lesson_candidate_count"] >= 1
        and summary["valid_lesson_candidate_count"] == 1
        and summary["invalid_lesson_candidate_count"] == 12
        and summary["missing_failure_reason_source_blocked_count"] >= 1
        and summary["unknown_candidate_type_blocked_count"] >= 1
        and summary["unknown_correction_type_blocked_count"] >= 1
        and summary["review_required_missing_blocked_count"] >= 1
        and summary["approved_lesson_blocked_count"] >= 1
        and summary["lesson_application_allowed_blocked_count"] >= 1
        and summary["persistent_learning_allowed_blocked_count"] >= 1
        and summary["memory_write_allowed_blocked_count"] >= 1
        and summary["predictor_mutation_allowed_blocked_count"] >= 1
        and summary["action_selection_unblocked_blocked_count"] >= 1
        and summary["lesson_applied_blocked_count"] >= 1
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["lesson_application_runtime_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["persistent_rule_write_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["autonomy_enabled_count"] == 0
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "lesson_candidate_from_failure_reason_enabled": True,
        "trace_check_only": True,
        "uses_failure_reason_from_outcome_pair": True,
        "v0_local_lesson_candidate_validator": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "lesson_candidate_approval_added": False,
        "lesson_application_runtime_added": False,
        "automatic_lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_selection_modified": False,
        "new_action_behavior_added": False,
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
