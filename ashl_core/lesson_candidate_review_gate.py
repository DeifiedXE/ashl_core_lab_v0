"""Review gate eligibility for trace-only lesson_candidate records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .lesson_candidate_from_failure_reason import (
    run_lesson_candidate_from_failure_reason_check,
    validate_lesson_candidate_record,
)


COMMAND = "run-lesson-candidate-review-gate-check"
FLOW = "lesson_candidate_review_gate_v0"

ALLOWED_GATE_STATUSES = {"pending_review", "blocked"}

REQUIRED_FIELDS = {
    "review_gate_result_id",
    "source_lesson_candidate_id",
    "source_failure_reason_id",
    "source_pair_id",
    "action_intent_id",
    "gate_status",
    "eligible_for_human_review",
    "blocked_reasons",
    "review_state",
    "source_trace",
    "review_boundary",
    "safety_flags",
}

REQUIRED_REVIEW_STATE_FIELDS = {
    "review_required",
    "pending_review",
    "approved",
    "rejected",
    "reviewed_by_human",
}

REQUIRED_REVIEW_BOUNDARY_FIELDS = {
    "lesson_application_allowed",
    "persistent_learning_allowed",
    "persistent_candidate_allowed",
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
    "persistent_candidate_created",
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


def evaluate_lesson_candidate_review_gate(lesson_candidate: dict[str, Any]) -> dict[str, Any]:
    """Return a trace-only review gate result.

    pending_review is not approval. eligible_for_human_review is not approval.
    This function never applies, persists, writes memory, mutates predictors, or changes action selection.
    """

    candidate_validation = validate_lesson_candidate_record(lesson_candidate)
    blocked_reasons = _blocked_reasons(lesson_candidate, candidate_validation)
    pending = not blocked_reasons
    source_lesson_candidate_id = lesson_candidate.get("lesson_candidate_id")
    return {
        "review_gate_result_id": f"lesson_review_gate:{source_lesson_candidate_id or 'missing'}",
        "source_lesson_candidate_id": source_lesson_candidate_id,
        "source_failure_reason_id": lesson_candidate.get("source_failure_reason_id"),
        "source_pair_id": lesson_candidate.get("source_pair_id"),
        "action_intent_id": lesson_candidate.get("action_intent_id"),
        "gate_status": "pending_review" if pending else "blocked",
        "eligible_for_human_review": pending,
        "blocked_reasons": blocked_reasons,
        "review_state": {
            "review_required": True,
            "pending_review": pending,
            "approved": False,
            "rejected": False,
            "reviewed_by_human": False,
        },
        "source_trace": {
            "source": "lesson_candidate_review_gate",
            "lesson_candidate_source": "lesson_candidate_from_failure_reason",
            "source_lesson_candidate_id": source_lesson_candidate_id,
        },
        "review_boundary": _build_review_boundary(),
        "safety_flags": _build_safety_flags(),
    }


def validate_lesson_candidate_review_gate_result(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    gate_status = record.get("gate_status")
    if gate_status not in ALLOWED_GATE_STATUSES:
        errors.append("unknown_gate_status")
    blocked_reasons = record.get("blocked_reasons")
    if not isinstance(blocked_reasons, list):
        errors.append("blocked_reasons_missing_or_not_list")
        blocked_reasons = []
    eligible = record.get("eligible_for_human_review")
    if gate_status == "pending_review" and (eligible is not True or blocked_reasons):
        errors.append("pending_review_consistency_violation")
    if gate_status == "blocked" and (eligible is not False or not blocked_reasons):
        errors.append("blocked_consistency_violation")

    review_state = _validate_review_state(record.get("review_state"), gate_status, errors)
    _validate_source_trace(record.get("source_trace"), record.get("source_lesson_candidate_id"), errors)
    review_boundary = _validate_review_boundary(record.get("review_boundary"), errors)
    safety_flags = _validate_safety_flags(record.get("safety_flags"), errors)

    return {
        "review_gate_result_id": record.get("review_gate_result_id"),
        "source_lesson_candidate_id": record.get("source_lesson_candidate_id"),
        "source_failure_reason_id": record.get("source_failure_reason_id"),
        "valid": not errors,
        "error_codes": errors,
        "gate_status": gate_status,
        "eligible_for_human_review": eligible is True,
        "pending_review": review_state.get("pending_review") is True,
        "approved": review_state.get("approved") is True,
        "rejected": review_state.get("rejected") is True,
        "reviewed_by_human": review_state.get("reviewed_by_human") is True,
        "persistent_candidate_created": safety_flags.get("persistent_candidate_created") is True,
        "action_selection_influence": safety_flags.get("action_selection_influence") is True,
        "action_behavior_changed": safety_flags.get("action_behavior_changed") is True,
        "lesson_application_runtime": safety_flags.get("lesson_application_runtime") is True,
        "memory_write": safety_flags.get("memory_write") is True,
        "predictor_modified": safety_flags.get("predictor_modified") is True,
        "persistent_rule_write": safety_flags.get("persistent_rule_write") is True,
        "endocrine_control": safety_flags.get("endocrine_control") is True,
        "autonomy_enabled": safety_flags.get("autonomy_enabled") is True,
        "review_boundary": review_boundary,
    }


def run_lesson_candidate_review_gate_check() -> dict[str, Any]:
    candidate_result = run_lesson_candidate_from_failure_reason_check()
    lesson_candidate_records = _build_demo_lesson_candidates(candidate_result["lesson_candidate_records"])
    candidate_validations = [validate_lesson_candidate_record(record) for record in lesson_candidate_records]
    review_gate_results = [evaluate_lesson_candidate_review_gate(record) for record in lesson_candidate_records]
    gate_validations = [validate_lesson_candidate_review_gate_result(record) for record in review_gate_results]
    summary = _build_summary(candidate_validations, review_gate_results, gate_validations)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "lesson_candidate_records": lesson_candidate_records,
        "candidate_validations": candidate_validations,
        "review_gate_results": review_gate_results,
        "gate_validations": gate_validations,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check evaluates whether trace-only lesson_candidate records may enter pending human review.",
            "pending_review is not approval, and eligible_for_human_review is not approval.",
            "Gate results do not approve, reject, apply, persist, write memory, mutate predictors, or change action selection.",
        ],
    }


def _build_demo_lesson_candidates(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    demo_records = [deepcopy(record) for record in records]
    valid_candidate = demo_records[0]

    rejected = _copy_case(valid_candidate, "rejected_true")
    rejected["review_boundary"]["rejected"] = True
    demo_records.append(rejected)

    persistent_candidate_created = _copy_case(valid_candidate, "persistent_candidate_created")
    persistent_candidate_created["safety_flags"]["persistent_candidate_created"] = True
    demo_records.append(persistent_candidate_created)
    return demo_records


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["case_name"] = case_name
    copied["lesson_candidate_id"] = f"{record['lesson_candidate_id']}:{case_name}"
    return copied


def _blocked_reasons(lesson_candidate: dict[str, Any], validation: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    error_codes = set(validation.get("error_codes", []))
    if not validation.get("valid"):
        reasons.append("invalid_lesson_candidate")
    if not lesson_candidate.get("source_failure_reason_id"):
        reasons.append("missing_source_failure_reason")
    review_boundary = lesson_candidate.get("review_boundary") if isinstance(lesson_candidate.get("review_boundary"), dict) else {}
    safety_flags = lesson_candidate.get("safety_flags") if isinstance(lesson_candidate.get("safety_flags"), dict) else {}
    if review_boundary.get("review_required") is not True:
        reasons.append("review_not_required")
    if review_boundary.get("approved") is True:
        reasons.append("already_approved")
    if review_boundary.get("rejected") is True:
        reasons.append("already_rejected")
    if review_boundary.get("lesson_application_allowed") is not False:
        reasons.append("lesson_application_unblocked")
    if review_boundary.get("persistent_learning_allowed") is not False:
        reasons.append("persistent_learning_unblocked")
    if review_boundary.get("memory_write_allowed") is not False:
        reasons.append("memory_write_unblocked")
    if review_boundary.get("predictor_mutation_allowed") is not False:
        reasons.append("predictor_mutation_unblocked")
    if safety_flags.get("approved_lesson") is True:
        reasons.append("approved_lesson_flag_set")
    if safety_flags.get("lesson_applied") is True:
        reasons.append("lesson_applied_flag_set")
    if safety_flags.get("blocked_from_action_selection") is not True:
        reasons.append("action_selection_unblocked")
    blocked_flag_reasons = {
        "blocked_from_action_behavior_change": "action_behavior_change_not_blocked",
        "blocked_from_lesson_application": "lesson_application_not_blocked",
        "blocked_from_memory_write": "memory_write_not_blocked",
        "blocked_from_predictor_mutation": "predictor_mutation_not_blocked",
        "blocked_from_persistent_rule_write": "persistent_rule_write_not_blocked",
    }
    for flag, reason in blocked_flag_reasons.items():
        if safety_flags.get(flag) is not True:
            reasons.append(reason)
    if safety_flags.get("persistent_candidate_created") is True:
        reasons.append("persistent_candidate_created")
    if safety_flags.get("trace_only") is not True:
        reasons.append("not_trace_only")
    for error_code in sorted(error_codes):
        if error_code.endswith("_enabled") and error_code not in {
            "approved_enabled",
            "rejected_enabled",
            "lesson_application_allowed_enabled",
            "persistent_learning_allowed_enabled",
            "memory_write_allowed_enabled",
            "predictor_mutation_allowed_enabled",
            "approved_lesson_enabled",
            "lesson_applied_enabled",
        }:
            reasons.append(error_code.removesuffix("_enabled"))
    return _dedupe(reasons)


def _dedupe(values: list[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def _build_review_boundary() -> dict[str, bool]:
    return {
        "lesson_application_allowed": False,
        "persistent_learning_allowed": False,
        "persistent_candidate_allowed": False,
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
        "persistent_candidate_created": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "lesson_application_runtime": False,
        "memory_write": False,
        "predictor_modified": False,
        "persistent_rule_write": False,
        "endocrine_control": False,
        "autonomy_enabled": False,
    }


def _validate_review_state(review_state: Any, gate_status: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(review_state, dict):
        errors.append("review_state_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_REVIEW_STATE_FIELDS):
        if field not in review_state:
            errors.append(f"review_state_missing_field:{field}")
    if review_state.get("review_required") is not True:
        errors.append("review_required_not_true")
    if gate_status == "pending_review" and review_state.get("pending_review") is not True:
        errors.append("pending_review_not_true")
    if gate_status == "blocked" and review_state.get("pending_review") is not False:
        errors.append("blocked_pending_review_not_false")
    if review_state.get("approved") is not False:
        errors.append("approved_enabled")
    if review_state.get("rejected") is not False:
        errors.append("rejected_enabled")
    if review_state.get("reviewed_by_human") is not False:
        errors.append("reviewed_by_human_enabled")
    return review_state


def _validate_source_trace(source_trace: Any, source_lesson_candidate_id: Any, errors: list[str]) -> None:
    if not isinstance(source_trace, dict):
        errors.append("source_trace_missing_or_not_dict")
        return
    if source_trace.get("source") != "lesson_candidate_review_gate":
        errors.append("invalid_source_trace_source")
    if source_trace.get("lesson_candidate_source") != "lesson_candidate_from_failure_reason":
        errors.append("invalid_lesson_candidate_source")
    if source_trace.get("source_lesson_candidate_id") != source_lesson_candidate_id:
        errors.append("source_trace_lesson_candidate_mismatch")


def _validate_review_boundary(review_boundary: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(review_boundary, dict):
        errors.append("review_boundary_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_REVIEW_BOUNDARY_FIELDS):
        if field not in review_boundary:
            errors.append(f"review_boundary_missing_field:{field}")
    for field in sorted(REQUIRED_REVIEW_BOUNDARY_FIELDS):
        if review_boundary.get(field) is not False:
            errors.append(f"{field}_enabled")
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
    false_flags = {"approved_lesson", "lesson_applied", "persistent_candidate_created"} | RUNTIME_FLAGS
    for flag in sorted(false_flags):
        if safety_flags.get(flag) not in {False, 0}:
            errors.append(f"{flag}_enabled")
    return safety_flags


def _build_summary(
    candidate_validations: list[dict[str, Any]],
    review_gate_results: list[dict[str, Any]],
    gate_validations: list[dict[str, Any]],
) -> dict[str, int]:
    valid_candidates = [result for result in candidate_validations if result["valid"]]
    blocked_results = [result for result in review_gate_results if result["gate_status"] == "blocked"]
    valid_gate_results = [result for result in gate_validations if result["valid"]]
    return {
        "lesson_candidate_record_count": len(candidate_validations),
        "valid_lesson_candidate_count": len(valid_candidates),
        "invalid_lesson_candidate_count": sum(1 for result in candidate_validations if not result["valid"]),
        "review_gate_result_count": len(review_gate_results),
        "pending_review_count": sum(1 for result in review_gate_results if result["gate_status"] == "pending_review"),
        "blocked_count": len(blocked_results),
        "eligible_for_human_review_count": sum(
            1 for result in review_gate_results if result["eligible_for_human_review"] is True
        ),
        "invalid_lesson_candidate_blocked_count": _count_blocked_reason(blocked_results, "invalid_lesson_candidate"),
        "missing_source_failure_reason_blocked_count": _count_blocked_reason(
            blocked_results, "missing_source_failure_reason"
        ),
        "review_not_required_blocked_count": _count_blocked_reason(blocked_results, "review_not_required"),
        "already_approved_blocked_count": _count_blocked_reason(blocked_results, "already_approved"),
        "already_rejected_blocked_count": _count_blocked_reason(blocked_results, "already_rejected"),
        "lesson_application_unblocked_blocked_count": _count_blocked_reason(
            blocked_results, "lesson_application_unblocked"
        ),
        "persistent_learning_unblocked_blocked_count": _count_blocked_reason(
            blocked_results, "persistent_learning_unblocked"
        ),
        "memory_write_unblocked_blocked_count": _count_blocked_reason(blocked_results, "memory_write_unblocked"),
        "predictor_mutation_unblocked_blocked_count": _count_blocked_reason(
            blocked_results, "predictor_mutation_unblocked"
        ),
        "approved_lesson_flag_blocked_count": _count_blocked_reason(blocked_results, "approved_lesson_flag_set"),
        "lesson_applied_flag_blocked_count": _count_blocked_reason(blocked_results, "lesson_applied_flag_set"),
        "action_selection_unblocked_blocked_count": _count_blocked_reason(
            blocked_results, "action_selection_unblocked"
        ),
        "persistent_candidate_created_count": _count_valid_flag(valid_gate_results, "persistent_candidate_created"),
        "action_selection_influence_count": _count_valid_flag(valid_gate_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_gate_results, "action_behavior_changed"),
        "lesson_application_runtime_count": _count_valid_flag(valid_gate_results, "lesson_application_runtime"),
        "memory_write_count": _count_valid_flag(valid_gate_results, "memory_write"),
        "predictor_modified_count": _count_valid_flag(valid_gate_results, "predictor_modified"),
        "persistent_rule_write_count": _count_valid_flag(valid_gate_results, "persistent_rule_write"),
        "endocrine_control_count": _count_valid_flag(valid_gate_results, "endocrine_control"),
        "autonomy_enabled_count": _count_valid_flag(valid_gate_results, "autonomy_enabled"),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["lesson_candidate_record_count"] == 15
        and summary["valid_lesson_candidate_count"] == 2
        and summary["invalid_lesson_candidate_count"] == 13
        and summary["review_gate_result_count"] == 15
        and summary["pending_review_count"] >= 1
        and summary["blocked_count"] >= 1
        and summary["eligible_for_human_review_count"] >= 1
        and summary["invalid_lesson_candidate_blocked_count"] >= 1
        and summary["missing_source_failure_reason_blocked_count"] >= 1
        and summary["review_not_required_blocked_count"] >= 1
        and summary["already_approved_blocked_count"] >= 1
        and summary["already_rejected_blocked_count"] >= 1
        and summary["lesson_application_unblocked_blocked_count"] >= 1
        and summary["persistent_learning_unblocked_blocked_count"] >= 1
        and summary["memory_write_unblocked_blocked_count"] >= 1
        and summary["predictor_mutation_unblocked_blocked_count"] >= 1
        and summary["approved_lesson_flag_blocked_count"] >= 1
        and summary["lesson_applied_flag_blocked_count"] >= 1
        and summary["action_selection_unblocked_blocked_count"] >= 1
        and summary["persistent_candidate_created_count"] == 0
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
        "lesson_candidate_review_gate_enabled": True,
        "trace_check_only": True,
        "uses_lesson_candidate_from_failure_reason": True,
        "v0_local_review_gate_validator": True,
        "pending_review_is_approval": False,
        "eligible_for_human_review_is_approval": False,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "lesson_candidate_approval_added": False,
        "lesson_candidate_rejection_runtime_added": False,
        "lesson_application_runtime_added": False,
        "automatic_lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_selection_modified": False,
        "new_action_behavior_added": False,
        "persistent_learning_added": False,
        "persistent_candidate_creation_added": False,
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
        "persistent_candidate_created_count": summary["persistent_candidate_created_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "lesson_application_runtime_count": summary["lesson_application_runtime_count"],
        "memory_write_count": summary["memory_write_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "persistent_rule_write_count": summary["persistent_rule_write_count"],
        "endocrine_control_count": summary["endocrine_control_count"],
        "autonomy_enabled_count": summary["autonomy_enabled_count"],
    }


def _count_blocked_reason(results: list[dict[str, Any]], reason: str) -> int:
    return sum(1 for result in results if reason in result.get("blocked_reasons", []))


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
