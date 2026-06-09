"""Human/manual review decision schema for lesson_candidate evidence summaries."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .lesson_candidate_review_evidence_summary import (
    run_lesson_candidate_review_evidence_summary_check,
    validate_lesson_candidate_review_evidence_summary,
)


COMMAND = "run-lesson-candidate-human-review-decision-schema-check"
FLOW = "lesson_candidate_human_review_decision_schema_v0"

ALLOWED_STATUSES = {"approved_for_preview", "rejected", "needs_revision", "stale"}

REQUIRED_FIELDS = {
    "review_decision_id",
    "source_evidence_summary_id",
    "source_lesson_candidate_id",
    "source_review_gate_result_id",
    "source_failure_reason_id",
    "source_pair_id",
    "action_intent_id",
    "decision",
    "reviewer_trace",
    "review_reason",
    "decision_scope",
    "boundary_summary",
    "source_trace",
    "safety_flags",
}

REQUIRED_LINKAGE_FIELDS = {
    "source_evidence_summary_id",
    "source_lesson_candidate_id",
    "source_review_gate_result_id",
    "source_failure_reason_id",
    "source_pair_id",
    "action_intent_id",
}

REQUIRED_DECISION_FIELDS = {
    "status",
    "reviewed_by_human",
    "approved_for_lesson_application",
    "approved_for_persistent_learning",
    "approved_for_memory_write",
    "approved_for_predictor_mutation",
}

REQUIRED_REVIEWER_TRACE_FIELDS = {
    "reviewer_type",
    "review_mode",
    "review_timestamp",
    "reviewer_id",
}

REQUIRED_REVIEW_REASON_FIELDS = {
    "reason_code",
    "description",
    "uses_evidence_summary",
}

REQUIRED_DECISION_SCOPE_FIELDS = {
    "allows_preview",
    "allows_application",
    "allows_action_selection_influence",
    "allows_memory_write",
    "allows_persistent_rule_write",
    "allows_predictor_mutation",
}

REQUIRED_BOUNDARY_FIELDS = {
    "lesson_applied",
    "behavior_preview_created",
    "action_selection_influence",
    "memory_write",
    "predictor_modified",
    "persistent_rule_write",
    "autonomy_enabled",
    "lesson_application_runtime",
}

REQUIRED_SAFETY_FLAGS = {
    "trace_only_decision",
    "blocked_from_lesson_application",
    "blocked_from_action_selection",
    "blocked_from_action_behavior_change",
    "blocked_from_memory_write",
    "blocked_from_predictor_mutation",
    "blocked_from_persistent_rule_write",
}

DISALLOWED_STATUSES = {
    "approved_for_application",
    "applied",
    "persistent",
    "memory_write",
    "predictor_mutation",
}


def build_lesson_candidate_human_review_decision(
    evidence_summary: dict[str, Any],
    status: str = "approved_for_preview",
    *,
    reviewer_id: str = "demo_human_reviewer",
    reason_code: str | None = None,
) -> dict[str, Any]:
    """Build a schema-only human review decision record.

    approved_for_preview allows only a future trace-only preview package. It does
    not approve lesson application, memory writes, persistence, predictor
    mutation, action selection influence, or behavior changes.
    """

    status = status
    allows_preview = status == "approved_for_preview"
    return {
        "review_decision_id": f"human_review_decision:{evidence_summary.get('evidence_summary_id') or 'missing'}:{status}",
        "source_evidence_summary_id": evidence_summary.get("evidence_summary_id"),
        "source_lesson_candidate_id": evidence_summary.get("source_lesson_candidate_id"),
        "source_review_gate_result_id": evidence_summary.get("source_review_gate_result_id"),
        "source_failure_reason_id": evidence_summary.get("source_failure_reason_id"),
        "source_pair_id": evidence_summary.get("source_pair_id"),
        "action_intent_id": evidence_summary.get("action_intent_id"),
        "decision": {
            "status": status,
            "reviewed_by_human": True,
            "approved_for_lesson_application": False,
            "approved_for_persistent_learning": False,
            "approved_for_memory_write": False,
            "approved_for_predictor_mutation": False,
        },
        "reviewer_trace": {
            "reviewer_type": "human",
            "review_mode": "manual",
            "review_timestamp": None,
            "reviewer_id": reviewer_id,
        },
        "review_reason": {
            "reason_code": reason_code or _default_reason_code(status),
            "description": _default_reason_description(status),
            "uses_evidence_summary": True,
        },
        "decision_scope": {
            "allows_preview": allows_preview,
            "allows_application": False,
            "allows_action_selection_influence": False,
            "allows_memory_write": False,
            "allows_persistent_rule_write": False,
            "allows_predictor_mutation": False,
        },
        "boundary_summary": _build_boundary_summary(),
        "source_trace": _build_source_trace(),
        "safety_flags": _build_safety_flags(),
    }


def validate_lesson_candidate_human_review_decision(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    _validate_linkage(record, errors)
    decision = _validate_decision(record.get("decision"), errors)
    reviewer_trace = _validate_reviewer_trace(record.get("reviewer_trace"), errors)
    _validate_review_reason(record.get("review_reason"), errors)
    decision_scope = _validate_decision_scope(record.get("decision_scope"), decision.get("status"), errors)
    boundary_summary = _validate_boundary_summary(record.get("boundary_summary"), errors)
    safety_flags = _validate_safety_flags(record.get("safety_flags"), errors)
    _validate_source_trace(record.get("source_trace"), errors)

    return {
        "review_decision_id": record.get("review_decision_id"),
        "source_evidence_summary_id": record.get("source_evidence_summary_id"),
        "source_lesson_candidate_id": record.get("source_lesson_candidate_id"),
        "source_review_gate_result_id": record.get("source_review_gate_result_id"),
        "source_failure_reason_id": record.get("source_failure_reason_id"),
        "source_pair_id": record.get("source_pair_id"),
        "action_intent_id": record.get("action_intent_id"),
        "valid": not errors,
        "error_codes": errors,
        "decision_status": decision.get("status"),
        "reviewed_by_human": decision.get("reviewed_by_human") is True,
        "reviewer_type": reviewer_trace.get("reviewer_type"),
        "review_mode": reviewer_trace.get("review_mode"),
        "allows_preview": decision_scope.get("allows_preview") is True,
        "allows_application": decision_scope.get("allows_application") is True,
        "lesson_application_runtime": boundary_summary.get("lesson_application_runtime") is True,
        "memory_write": boundary_summary.get("memory_write") is True,
        "predictor_modified": boundary_summary.get("predictor_modified") is True,
        "persistent_rule_write": boundary_summary.get("persistent_rule_write") is True,
        "action_selection_influence": boundary_summary.get("action_selection_influence") is True,
        "autonomy_enabled": boundary_summary.get("autonomy_enabled") is True,
        "trace_only_decision": safety_flags.get("trace_only_decision") is True,
    }


def run_lesson_candidate_human_review_decision_schema_check() -> dict[str, Any]:
    evidence_result = run_lesson_candidate_review_evidence_summary_check()
    valid_evidence_summary = next(
        summary
        for summary, validation in zip(
            evidence_result["evidence_summaries"],
            evidence_result["evidence_summary_validations"],
        )
        if validation["valid"]
    )
    review_decision_records = _build_demo_decision_records(valid_evidence_summary)
    validation_results = [
        validate_lesson_candidate_human_review_decision(record) for record in review_decision_records
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "source_evidence_summary": valid_evidence_summary,
        "review_decision_records": review_decision_records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This schema/checker records human/manual decisions for lesson_candidate evidence summaries.",
            "approved_for_preview permits only a future trace-only preview package.",
            "No behavior preview, lesson application, action selection influence, memory write, persistence, predictor mutation, or autonomy is added.",
        ],
    }


def _build_demo_decision_records(evidence_summary: dict[str, Any]) -> list[dict[str, Any]]:
    records = [
        build_lesson_candidate_human_review_decision(evidence_summary, "approved_for_preview"),
        build_lesson_candidate_human_review_decision(evidence_summary, "rejected"),
        build_lesson_candidate_human_review_decision(evidence_summary, "needs_revision"),
        build_lesson_candidate_human_review_decision(evidence_summary, "stale"),
    ]

    missing_evidence = _copy_case(records[0], "missing_evidence_linkage")
    missing_evidence.pop("source_evidence_summary_id")
    records.append(missing_evidence)

    non_human = _copy_case(records[0], "non_human_reviewer")
    non_human["reviewer_trace"]["reviewer_type"] = "llm"
    records.append(non_human)

    automatic = _copy_case(records[0], "automatic_review_mode")
    automatic["reviewer_trace"]["review_mode"] = "automatic"
    records.append(automatic)

    approved_for_application = _copy_case(records[0], "approved_for_application")
    approved_for_application["decision"]["status"] = "approved_for_application"
    approved_for_application["decision"]["approved_for_lesson_application"] = True
    approved_for_application["decision_scope"]["allows_application"] = True
    records.append(approved_for_application)

    memory_write = _copy_case(records[0], "memory_write_allowed")
    memory_write["decision"]["approved_for_memory_write"] = True
    memory_write["decision_scope"]["allows_memory_write"] = True
    memory_write["boundary_summary"]["memory_write"] = True
    records.append(memory_write)

    predictor_mutation = _copy_case(records[0], "predictor_mutation_allowed")
    predictor_mutation["decision"]["approved_for_predictor_mutation"] = True
    predictor_mutation["decision_scope"]["allows_predictor_mutation"] = True
    predictor_mutation["boundary_summary"]["predictor_modified"] = True
    records.append(predictor_mutation)

    behavior_preview = _copy_case(records[0], "behavior_preview_created")
    behavior_preview["boundary_summary"]["behavior_preview_created"] = True
    records.append(behavior_preview)

    lesson_applied = _copy_case(records[0], "lesson_applied")
    lesson_applied["boundary_summary"]["lesson_applied"] = True
    lesson_applied["boundary_summary"]["lesson_application_runtime"] = True
    records.append(lesson_applied)

    action_selection = _copy_case(records[0], "action_selection_influence")
    action_selection["decision_scope"]["allows_action_selection_influence"] = True
    action_selection["boundary_summary"]["action_selection_influence"] = True
    records.append(action_selection)

    return records


def _validate_linkage(record: dict[str, Any], errors: list[str]) -> None:
    for field in sorted(REQUIRED_LINKAGE_FIELDS):
        if not record.get(field):
            errors.append(f"missing_source_linkage:{field}")


def _validate_decision(decision: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(decision, dict):
        errors.append("decision_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_DECISION_FIELDS):
        if field not in decision:
            errors.append(f"decision_missing_field:{field}")
    status = decision.get("status")
    if status in DISALLOWED_STATUSES:
        errors.append("disallowed_decision_status")
    elif status not in ALLOWED_STATUSES:
        errors.append("unknown_decision_status")
    if decision.get("reviewed_by_human") is not True:
        errors.append("reviewed_by_human_not_true")
    false_flags = {
        "approved_for_lesson_application": "approved_for_application_enabled",
        "approved_for_persistent_learning": "approved_for_persistent_learning_enabled",
        "approved_for_memory_write": "approved_for_memory_write_enabled",
        "approved_for_predictor_mutation": "approved_for_predictor_mutation_enabled",
    }
    for field, error_code in false_flags.items():
        if decision.get(field) not in {False, 0}:
            errors.append(error_code)
    return decision


def _validate_reviewer_trace(reviewer_trace: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(reviewer_trace, dict):
        errors.append("reviewer_trace_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_REVIEWER_TRACE_FIELDS):
        if field not in reviewer_trace:
            errors.append(f"reviewer_trace_missing_field:{field}")
    if reviewer_trace.get("reviewer_type") != "human":
        errors.append("non_human_reviewer")
    if reviewer_trace.get("review_mode") != "manual":
        errors.append("automatic_review_mode")
    if not reviewer_trace.get("reviewer_id"):
        errors.append("reviewer_id_missing")
    return reviewer_trace


def _validate_review_reason(review_reason: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(review_reason, dict):
        errors.append("review_reason_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_REVIEW_REASON_FIELDS):
        if field not in review_reason:
            errors.append(f"review_reason_missing_field:{field}")
    if not review_reason.get("reason_code"):
        errors.append("review_reason_code_missing")
    if not review_reason.get("description"):
        errors.append("review_reason_description_missing")
    if review_reason.get("uses_evidence_summary") is not True:
        errors.append("review_reason_not_using_evidence_summary")
    return review_reason


def _validate_decision_scope(decision_scope: Any, status: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(decision_scope, dict):
        errors.append("decision_scope_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_DECISION_SCOPE_FIELDS):
        if field not in decision_scope:
            errors.append(f"decision_scope_missing_field:{field}")
    if status == "approved_for_preview":
        if decision_scope.get("allows_preview") is not True:
            errors.append("approved_for_preview_requires_preview_scope")
    elif status in {"rejected", "needs_revision", "stale"}:
        if decision_scope.get("allows_preview") not in {False, 0}:
            errors.append(f"{status}_must_not_allow_preview")
    forbidden = {
        "allows_application": "allows_application_enabled",
        "allows_action_selection_influence": "allows_action_selection_influence_enabled",
        "allows_memory_write": "allows_memory_write_enabled",
        "allows_persistent_rule_write": "allows_persistent_rule_write_enabled",
        "allows_predictor_mutation": "allows_predictor_mutation_enabled",
    }
    for field, error_code in forbidden.items():
        if decision_scope.get(field) not in {False, 0}:
            errors.append(error_code)
    return decision_scope


def _validate_boundary_summary(boundary_summary: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(boundary_summary, dict):
        errors.append("boundary_summary_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_BOUNDARY_FIELDS):
        if field not in boundary_summary:
            errors.append(f"boundary_summary_missing_field:{field}")
    false_flags = {
        "lesson_applied": "lesson_applied_enabled",
        "behavior_preview_created": "behavior_preview_created_enabled",
        "action_selection_influence": "action_selection_influence_enabled",
        "memory_write": "memory_write_enabled",
        "predictor_modified": "predictor_modified_enabled",
        "persistent_rule_write": "persistent_rule_write_enabled",
        "autonomy_enabled": "autonomy_enabled",
        "lesson_application_runtime": "lesson_application_runtime_enabled",
    }
    for field, error_code in false_flags.items():
        if boundary_summary.get(field) not in {False, 0}:
            errors.append(error_code)
    return boundary_summary


def _validate_source_trace(source_trace: Any, errors: list[str]) -> None:
    if not isinstance(source_trace, dict):
        errors.append("source_trace_missing_or_not_dict")
        return
    expected = {
        "source": "lesson_candidate_human_review_decision_schema",
        "evidence_summary_source": "lesson_candidate_review_evidence_summary",
        "lesson_candidate_source": "lesson_candidate_from_failure_reason",
    }
    for field, value in expected.items():
        if source_trace.get(field) != value:
            errors.append(f"invalid_source_trace:{field}")


def _validate_safety_flags(safety_flags: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(safety_flags, dict):
        errors.append("safety_flags_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_SAFETY_FLAGS):
        if field not in safety_flags:
            errors.append(f"missing_safety_flag:{field}")
    required_true = {
        "trace_only_decision": "trace_only_decision_not_true",
        "blocked_from_lesson_application": "lesson_application_not_blocked",
        "blocked_from_action_selection": "action_selection_not_blocked",
        "blocked_from_action_behavior_change": "action_behavior_change_not_blocked",
        "blocked_from_memory_write": "memory_write_not_blocked",
        "blocked_from_predictor_mutation": "predictor_mutation_not_blocked",
        "blocked_from_persistent_rule_write": "persistent_rule_write_not_blocked",
    }
    for field, error_code in required_true.items():
        if safety_flags.get(field) is not True:
            errors.append(error_code)
    return safety_flags


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid_results = [result for result in validation_results if result["valid"]]
    return {
        "review_decision_record_count": len(validation_results),
        "valid_review_decision_count": len(valid_results),
        "invalid_review_decision_count": sum(1 for result in validation_results if not result["valid"]),
        "approved_for_preview_count": _count_valid_status(valid_results, "approved_for_preview"),
        "rejected_count": _count_valid_status(valid_results, "rejected"),
        "needs_revision_count": _count_valid_status(valid_results, "needs_revision"),
        "stale_count": _count_valid_status(valid_results, "stale"),
        "missing_evidence_linkage_blocked_count": _count_error(
            validation_results, "missing_source_linkage:source_evidence_summary_id"
        ),
        "non_human_reviewer_blocked_count": _count_error(validation_results, "non_human_reviewer"),
        "automatic_review_blocked_count": _count_error(validation_results, "automatic_review_mode"),
        "approved_for_application_blocked_count": _count_error(
            validation_results, "approved_for_application_enabled"
        ),
        "memory_write_allowed_blocked_count": _count_error(validation_results, "approved_for_memory_write_enabled"),
        "predictor_mutation_allowed_blocked_count": _count_error(
            validation_results, "approved_for_predictor_mutation_enabled"
        ),
        "behavior_preview_created_blocked_count": _count_error(
            validation_results, "behavior_preview_created_enabled"
        ),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "action_selection_influence_blocked_count": _count_error(
            validation_results, "action_selection_influence_enabled"
        ),
        "lesson_application_runtime_count": _count_valid_flag(valid_results, "lesson_application_runtime"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "persistent_rule_write_count": _count_valid_flag(valid_results, "persistent_rule_write"),
        "action_selection_influence_count": _count_valid_flag(valid_results, "action_selection_influence"),
        "autonomy_enabled_count": _count_valid_flag(valid_results, "autonomy_enabled"),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["review_decision_record_count"] == 13
        and summary["valid_review_decision_count"] == 4
        and summary["invalid_review_decision_count"] == 9
        and summary["approved_for_preview_count"] == 1
        and summary["rejected_count"] == 1
        and summary["needs_revision_count"] == 1
        and summary["stale_count"] == 1
        and summary["missing_evidence_linkage_blocked_count"] >= 1
        and summary["non_human_reviewer_blocked_count"] >= 1
        and summary["automatic_review_blocked_count"] >= 1
        and summary["approved_for_application_blocked_count"] >= 1
        and summary["memory_write_allowed_blocked_count"] >= 1
        and summary["predictor_mutation_allowed_blocked_count"] >= 1
        and summary["behavior_preview_created_blocked_count"] >= 1
        and summary["lesson_applied_blocked_count"] >= 1
        and summary["action_selection_influence_blocked_count"] >= 1
        and summary["lesson_application_runtime_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["persistent_rule_write_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["autonomy_enabled_count"] == 0
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "lesson_candidate_human_review_decision_schema_enabled": True,
        "schema_check_only": True,
        "human_manual_review_required": True,
        "approved_for_preview_is_application_approval": False,
        "behavior_preview_created": False,
        "lesson_application_runtime_added": False,
        "runtime_action_selection_added": False,
        "action_selection_modified": False,
        "new_action_behavior_added": False,
        "persistent_learning_added": False,
        "persistent_candidate_creation_added": False,
        "persistent_rule_write_added": False,
        "memory_write_added": False,
        "predictor_mutation_added": False,
        "automatic_review_decision_added": False,
        "llm_review_decision_added": False,
        "autonomy_added": False,
        "semantic_vision_claimed": False,
        "consciousness_claimed": False,
        "subjective_claims_added": False,
        "lesson_application_runtime_count": summary["lesson_application_runtime_count"],
        "memory_write_count": summary["memory_write_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "persistent_rule_write_count": summary["persistent_rule_write_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "autonomy_enabled_count": summary["autonomy_enabled_count"],
    }


def _build_boundary_summary() -> dict[str, bool]:
    return {
        "lesson_applied": False,
        "behavior_preview_created": False,
        "action_selection_influence": False,
        "memory_write": False,
        "predictor_modified": False,
        "persistent_rule_write": False,
        "autonomy_enabled": False,
        "lesson_application_runtime": False,
    }


def _build_source_trace() -> dict[str, str]:
    return {
        "source": "lesson_candidate_human_review_decision_schema",
        "evidence_summary_source": "lesson_candidate_review_evidence_summary",
        "lesson_candidate_source": "lesson_candidate_from_failure_reason",
    }


def _build_safety_flags() -> dict[str, bool]:
    return {
        "trace_only_decision": True,
        "blocked_from_lesson_application": True,
        "blocked_from_action_selection": True,
        "blocked_from_action_behavior_change": True,
        "blocked_from_memory_write": True,
        "blocked_from_predictor_mutation": True,
        "blocked_from_persistent_rule_write": True,
    }


def _default_reason_code(status: str) -> str:
    return {
        "approved_for_preview": "evidence_sufficient_for_preview",
        "rejected": "evidence_rejected_by_human",
        "needs_revision": "human_review_needs_revision",
        "stale": "human_review_marked_stale",
    }.get(status, "invalid_decision_status")


def _default_reason_description(status: str) -> str:
    return {
        "approved_for_preview": "Evidence summary is sufficient to allow a future trace-only preview.",
        "rejected": "Human reviewer rejected this lesson candidate for preview.",
        "needs_revision": "Human reviewer requested revision before any preview.",
        "stale": "Human reviewer marked this evidence path as stale.",
    }.get(status, "Invalid decision status for this schema.")


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["case_name"] = case_name
    copied["review_decision_id"] = f"{record['review_decision_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_status(valid_results: list[dict[str, Any]], status: str) -> int:
    return sum(1 for result in valid_results if result.get("decision_status") == status)


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
