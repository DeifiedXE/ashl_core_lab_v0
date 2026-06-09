"""Trace-only preview records for human-reviewed lesson candidates."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .lesson_candidate_from_failure_reason import (
    run_lesson_candidate_from_failure_reason_check,
    validate_lesson_candidate_record,
)
from .lesson_candidate_human_review_decision_schema import (
    run_lesson_candidate_human_review_decision_schema_check,
    validate_lesson_candidate_human_review_decision,
)


COMMAND = "run-reviewed-lesson-trace-preview-check"
FLOW = "reviewed_lesson_trace_preview_v0"

APPROVED_STATUS = "approved_for_preview"
BLOCKED_STATUSES = {
    "rejected": "rejected_decision_blocked",
    "needs_revision": "needs_revision_decision_blocked",
    "stale": "stale_decision_blocked",
}

ALLOWED_PREVIEW_TYPES = {
    "precondition_or_correction_trace",
    "avoid_repeat_failure_trace",
    "ask_for_help_trace",
}

REQUIRED_FIELDS = {
    "preview_id",
    "source_review_decision_id",
    "source_evidence_summary_id",
    "source_lesson_candidate_id",
    "source_failure_reason_id",
    "source_pair_id",
    "action_intent_id",
    "preview_status",
    "preview_content",
    "boundary_summary",
    "source_trace",
    "safety_flags",
}

REQUIRED_STATUS_FIELDS = {
    "created",
    "source_decision_status",
    "trace_only",
    "applied",
    "blocked_reasons",
}

REQUIRED_CONTENT_FIELDS = {
    "preview_type",
    "target_action_type",
    "correction_type",
    "correction_description",
    "changes_action_selection",
    "changes_action_behavior",
    "writes_memory",
    "mutates_predictor",
    "creates_persistent_rule",
}

REQUIRED_BOUNDARY_FIELDS = {
    "trace_only_preview",
    "lesson_application_allowed",
    "lesson_applied",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "predictor_modified",
    "persistent_rule_write",
    "persistent_learning",
    "autonomy_enabled",
}

REQUIRED_SAFETY_FLAGS = {
    "blocked_from_lesson_application",
    "blocked_from_action_selection",
    "blocked_from_action_behavior_change",
    "blocked_from_memory_write",
    "blocked_from_predictor_mutation",
    "blocked_from_persistent_rule_write",
}


def build_reviewed_lesson_trace_preview(
    lesson_candidate: dict[str, Any],
    review_decision: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a deterministic preview record without applying the lesson."""

    candidate = deepcopy(lesson_candidate)
    decision = deepcopy(review_decision) if review_decision is not None else None
    candidate_validation = validate_lesson_candidate_record(candidate)
    decision_validation = (
        validate_lesson_candidate_human_review_decision(decision)
        if isinstance(decision, dict)
        else {
            "review_decision_id": None,
            "valid": False,
            "error_codes": ["missing_review_decision"],
            "decision_status": None,
            "reviewed_by_human": False,
            "allows_preview": False,
            "allows_application": False,
        }
    )

    status = decision_validation.get("decision_status")
    blocked_reasons = _blocked_reasons(candidate, candidate_validation, decision, decision_validation)
    created = not blocked_reasons
    preview_type = _preview_type(candidate) if created else _preview_type(candidate)

    return {
        "preview_id": _preview_id(decision, candidate, status),
        "source_review_decision_id": None if decision is None else decision.get("review_decision_id"),
        "source_evidence_summary_id": None if decision is None else decision.get("source_evidence_summary_id"),
        "source_lesson_candidate_id": candidate.get("lesson_candidate_id"),
        "source_failure_reason_id": candidate.get("source_failure_reason_id"),
        "source_pair_id": candidate.get("source_pair_id"),
        "action_intent_id": candidate.get("action_intent_id"),
        "preview_status": {
            "created": created,
            "source_decision_status": status,
            "trace_only": True,
            "applied": False,
            "blocked_reasons": blocked_reasons,
        },
        "preview_content": {
            "preview_type": preview_type,
            "target_action_type": candidate.get("proposed_correction", {}).get("target_action_type"),
            "correction_type": candidate.get("proposed_correction", {}).get("correction_type"),
            "correction_description": candidate.get("proposed_correction", {}).get("description"),
            "changes_action_selection": False,
            "changes_action_behavior": False,
            "writes_memory": False,
            "mutates_predictor": False,
            "creates_persistent_rule": False,
        },
        "boundary_summary": _boundary_summary(),
        "source_trace": _source_trace(candidate, decision),
        "safety_flags": _safety_flags(),
    }


def validate_reviewed_lesson_trace_preview(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    status = _validate_status(record.get("preview_status"), errors)
    content = _validate_content(record.get("preview_content"), errors)
    boundary = _validate_boundary(record.get("boundary_summary"), errors)
    safety = _validate_safety_flags(record.get("safety_flags"), errors)
    _validate_linkage(record, errors)
    _validate_source_trace(record, errors)

    return {
        "preview_id": record.get("preview_id"),
        "source_review_decision_id": record.get("source_review_decision_id"),
        "source_lesson_candidate_id": record.get("source_lesson_candidate_id"),
        "source_failure_reason_id": record.get("source_failure_reason_id"),
        "source_pair_id": record.get("source_pair_id"),
        "action_intent_id": record.get("action_intent_id"),
        "valid": not errors,
        "error_codes": errors,
        "preview_created": status.get("created") is True,
        "source_decision_status": status.get("source_decision_status"),
        "preview_type": content.get("preview_type"),
        "trace_only_preview": boundary.get("trace_only_preview") is True,
        "lesson_application_allowed": boundary.get("lesson_application_allowed") is True,
        "lesson_applied": boundary.get("lesson_applied") is True,
        "action_selection_influence": boundary.get("action_selection_influence") is True,
        "action_behavior_changed": boundary.get("action_behavior_changed") is True,
        "memory_write": boundary.get("memory_write") is True,
        "predictor_modified": boundary.get("predictor_modified") is True,
        "persistent_rule_write": boundary.get("persistent_rule_write") is True,
        "persistent_learning": boundary.get("persistent_learning") is True,
        "autonomy_enabled": boundary.get("autonomy_enabled") is True,
        "blocked_from_lesson_application": safety.get("blocked_from_lesson_application") is True,
        "blocked_from_action_selection": safety.get("blocked_from_action_selection") is True,
    }


def run_reviewed_lesson_trace_preview_check() -> dict[str, Any]:
    decision_result = run_lesson_candidate_human_review_decision_schema_check()
    candidate_result = run_lesson_candidate_from_failure_reason_check()
    valid_candidate = next(
        candidate
        for candidate, validation in zip(
            candidate_result["lesson_candidate_records"],
            candidate_result["validation_results"],
        )
        if validation["valid"]
    )
    valid_decisions = [
        record
        for record, validation in zip(
            decision_result["review_decision_records"],
            decision_result["validation_results"],
        )
        if validation["valid"]
    ]
    preview_records = _build_demo_preview_records(valid_candidate, valid_decisions)
    validation_results = [validate_reviewed_lesson_trace_preview(record) for record in preview_records]
    summary = _build_summary(decision_result["summary"], validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "source_lesson_candidate": valid_candidate,
        "source_review_decisions": valid_decisions,
        "preview_records": preview_records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker creates trace-only lesson previews only from valid human approved_for_preview decisions.",
            "Rejected, needs_revision, stale, missing decision, and source mismatch cases are blocked.",
            "No lesson is applied, no action selection or behavior is changed, no memory is written, and no predictor or persistent rule is modified.",
        ],
    }


def _blocked_reasons(
    candidate: dict[str, Any],
    candidate_validation: dict[str, Any],
    decision: dict[str, Any] | None,
    decision_validation: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    if decision is None:
        reasons.append("missing_review_decision")
    if not candidate_validation["valid"]:
        reasons.append("invalid_lesson_candidate")
    if not decision_validation["valid"]:
        reasons.append("invalid_review_decision")

    status = decision_validation.get("decision_status")
    if status in BLOCKED_STATUSES:
        reasons.append(BLOCKED_STATUSES[status])
    elif status != APPROVED_STATUS:
        reasons.append("not_approved_for_preview")

    if decision is not None and decision.get("source_lesson_candidate_id") != candidate.get("lesson_candidate_id"):
        reasons.append("source_linkage_mismatch")
    if decision_validation.get("reviewed_by_human") is not True:
        reasons.append("reviewed_by_human_not_true")
    if decision_validation.get("allows_preview") is not True:
        reasons.append("preview_not_allowed_by_decision")
    if decision_validation.get("allows_application") is True:
        reasons.append("lesson_application_allowed")
    if candidate_validation.get("approved_lesson") is True:
        reasons.append("approved_lesson_blocked")
    if candidate_validation.get("lesson_applied") is True:
        reasons.append("lesson_applied_blocked")
    return _dedupe(reasons)


def _build_demo_preview_records(
    valid_candidate: dict[str, Any],
    valid_decisions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_status = {decision["decision"]["status"]: decision for decision in valid_decisions}
    records = [
        build_reviewed_lesson_trace_preview(valid_candidate, by_status[APPROVED_STATUS]),
        build_reviewed_lesson_trace_preview(valid_candidate, by_status["rejected"]),
        build_reviewed_lesson_trace_preview(valid_candidate, by_status["needs_revision"]),
        build_reviewed_lesson_trace_preview(valid_candidate, by_status["stale"]),
        build_reviewed_lesson_trace_preview(valid_candidate, None),
    ]

    base = records[0]
    records.append(_mutate(base, "source_linkage_mismatch", ("source_trace", "source_lesson_candidate_id"), "other"))
    records.append(_mutate(base, "unknown_preview_type", ("preview_content", "preview_type"), "free_form_trace"))

    for field, value in [
        ("lesson_application_allowed", True),
        ("lesson_applied", True),
        ("action_selection_influence", True),
        ("action_behavior_changed", True),
        ("memory_write", True),
        ("predictor_modified", True),
        ("persistent_rule_write", True),
        ("persistent_learning", True),
        ("trace_only_preview", False),
    ]:
        records.append(_mutate(base, field, ("boundary_summary", field), value))

    for field in sorted(REQUIRED_SAFETY_FLAGS):
        records.append(_mutate(base, field, ("safety_flags", field), False))

    return records


def _validate_status(status: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(status, dict):
        errors.append("preview_status_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_STATUS_FIELDS):
        if field not in status:
            errors.append(f"preview_status_missing_field:{field}")
    if status.get("created") is not True:
        errors.append("preview_not_created")
    decision_status = status.get("source_decision_status")
    if decision_status == "rejected":
        errors.append("rejected_decision_blocked")
    elif decision_status == "needs_revision":
        errors.append("needs_revision_decision_blocked")
    elif decision_status == "stale":
        errors.append("stale_decision_blocked")
    elif decision_status != APPROVED_STATUS:
        errors.append("not_approved_for_preview")
    if status.get("trace_only") is not True:
        errors.append("trace_only_status_not_true")
    if status.get("applied") not in {False, 0}:
        errors.append("preview_applied_enabled")
    blocked_reasons = status.get("blocked_reasons", [])
    if blocked_reasons:
        for reason in blocked_reasons:
            errors.append(reason)
    return status


def _validate_content(content: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(content, dict):
        errors.append("preview_content_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_CONTENT_FIELDS):
        if field not in content:
            errors.append(f"preview_content_missing_field:{field}")
    if content.get("preview_type") not in ALLOWED_PREVIEW_TYPES:
        errors.append("unknown_preview_type")
    false_flags = {
        "changes_action_selection": "action_selection_influence_enabled",
        "changes_action_behavior": "action_behavior_changed_enabled",
        "writes_memory": "memory_write_enabled",
        "mutates_predictor": "predictor_modified_enabled",
        "creates_persistent_rule": "persistent_rule_write_enabled",
    }
    for field, error_code in false_flags.items():
        if content.get(field) not in {False, 0}:
            errors.append(error_code)
    return content


def _validate_boundary(boundary: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(boundary, dict):
        errors.append("boundary_summary_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_BOUNDARY_FIELDS):
        if field not in boundary:
            errors.append(f"boundary_summary_missing_field:{field}")
    if boundary.get("trace_only_preview") is not True:
        errors.append("trace_only_preview_not_true")
    false_flags = {
        "lesson_application_allowed": "lesson_application_allowed_enabled",
        "lesson_applied": "lesson_applied_enabled",
        "action_selection_influence": "action_selection_influence_enabled",
        "action_behavior_changed": "action_behavior_changed_enabled",
        "memory_write": "memory_write_enabled",
        "predictor_modified": "predictor_modified_enabled",
        "persistent_rule_write": "persistent_rule_write_enabled",
        "persistent_learning": "persistent_learning_enabled",
        "autonomy_enabled": "autonomy_enabled",
    }
    for field, error_code in false_flags.items():
        if boundary.get(field) not in {False, 0}:
            errors.append(error_code)
    return boundary


def _validate_safety_flags(safety: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(safety, dict):
        errors.append("safety_flags_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_SAFETY_FLAGS):
        if field not in safety:
            errors.append(f"missing_safety_flag:{field}")
    required_true = {
        "blocked_from_lesson_application": "lesson_application_not_blocked",
        "blocked_from_action_selection": "action_selection_not_blocked",
        "blocked_from_action_behavior_change": "action_behavior_change_not_blocked",
        "blocked_from_memory_write": "memory_write_not_blocked",
        "blocked_from_predictor_mutation": "predictor_mutation_not_blocked",
        "blocked_from_persistent_rule_write": "persistent_rule_write_not_blocked",
    }
    for field, error_code in required_true.items():
        if safety.get(field) is not True:
            errors.append(error_code)
    return safety


def _validate_linkage(record: dict[str, Any], errors: list[str]) -> None:
    for field in [
        "source_review_decision_id",
        "source_evidence_summary_id",
        "source_lesson_candidate_id",
        "source_failure_reason_id",
        "source_pair_id",
        "action_intent_id",
    ]:
        if not record.get(field):
            errors.append(f"missing_source_linkage:{field}")
    if not record.get("source_review_decision_id"):
        errors.append("missing_review_decision")


def _validate_source_trace(record: dict[str, Any], errors: list[str]) -> None:
    source_trace = record.get("source_trace")
    if not isinstance(source_trace, dict):
        errors.append("source_trace_missing_or_not_dict")
        return
    expected = {
        "source": "reviewed_lesson_trace_preview",
        "review_decision_source": "lesson_candidate_human_review_decision_schema",
        "evidence_summary_source": "lesson_candidate_review_evidence_summary",
        "lesson_candidate_source": "lesson_candidate_from_failure_reason",
    }
    for field, value in expected.items():
        if source_trace.get(field) != value:
            errors.append(f"invalid_source_trace:{field}")
    for field in [
        "source_review_decision_id",
        "source_evidence_summary_id",
        "source_lesson_candidate_id",
        "source_failure_reason_id",
        "source_pair_id",
        "action_intent_id",
    ]:
        if source_trace.get(field) != record.get(field):
            errors.append("source_linkage_mismatch")
            break


def _build_summary(
    decision_summary: dict[str, Any],
    validation_results: list[dict[str, Any]],
) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "review_decision_record_count": decision_summary["review_decision_record_count"],
        "valid_review_decision_count": decision_summary["valid_review_decision_count"],
        "approved_for_preview_count": decision_summary["approved_for_preview_count"],
        "rejected_count": decision_summary["rejected_count"],
        "needs_revision_count": decision_summary["needs_revision_count"],
        "stale_count": decision_summary["stale_count"],
        "preview_record_count": len(validation_results),
        "valid_preview_count": len(valid_results),
        "invalid_preview_count": sum(1 for result in validation_results if not result["valid"]),
        "blocked_preview_count": sum(1 for result in validation_results if not result["valid"]),
        "rejected_preview_blocked_count": _count_error(validation_results, "rejected_decision_blocked"),
        "needs_revision_preview_blocked_count": _count_error(validation_results, "needs_revision_decision_blocked"),
        "stale_preview_blocked_count": _count_error(validation_results, "stale_decision_blocked"),
        "missing_review_decision_blocked_count": _count_error(validation_results, "missing_review_decision"),
        "source_linkage_mismatch_blocked_count": _count_error(validation_results, "source_linkage_mismatch"),
        "unknown_preview_type_blocked_count": _count_error(validation_results, "unknown_preview_type"),
        "lesson_application_allowed_blocked_count": _count_error(
            validation_results, "lesson_application_allowed_enabled"
        ),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "action_selection_influence_blocked_count": _count_error(
            validation_results, "action_selection_influence_enabled"
        ),
        "action_behavior_changed_blocked_count": _count_error(validation_results, "action_behavior_changed_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "predictor_mutation_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "persistent_rule_write_blocked_count": _count_error(validation_results, "persistent_rule_write_enabled"),
        "persistent_learning_blocked_count": _count_error(validation_results, "persistent_learning_enabled"),
        "lesson_application_runtime_count": 0,
        "action_selection_influence_count": _count_valid_flag(valid_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "persistent_rule_write_count": _count_valid_flag(valid_results, "persistent_rule_write"),
        "autonomy_enabled_count": _count_valid_flag(valid_results, "autonomy_enabled"),
    }
    summary["all_reviewed_lesson_trace_preview_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["review_decision_record_count"] == 13
        and summary["valid_review_decision_count"] == 4
        and summary["approved_for_preview_count"] == 1
        and summary["rejected_count"] == 1
        and summary["needs_revision_count"] == 1
        and summary["stale_count"] == 1
        and summary["preview_record_count"] == 22
        and summary["valid_preview_count"] == 1
        and summary["invalid_preview_count"] == 21
        and summary["blocked_preview_count"] == 21
        and summary["rejected_preview_blocked_count"] >= 1
        and summary["needs_revision_preview_blocked_count"] >= 1
        and summary["stale_preview_blocked_count"] >= 1
        and summary["missing_review_decision_blocked_count"] >= 1
        and summary["source_linkage_mismatch_blocked_count"] >= 1
        and summary["unknown_preview_type_blocked_count"] >= 1
        and summary["lesson_application_allowed_blocked_count"] >= 1
        and summary["lesson_applied_blocked_count"] >= 1
        and summary["action_selection_influence_blocked_count"] >= 1
        and summary["action_behavior_changed_blocked_count"] >= 1
        and summary["memory_write_blocked_count"] >= 1
        and summary["predictor_mutation_blocked_count"] >= 1
        and summary["persistent_rule_write_blocked_count"] >= 1
        and summary["persistent_learning_blocked_count"] >= 1
        and summary["lesson_application_runtime_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["persistent_rule_write_count"] == 0
        and summary["autonomy_enabled_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "reviewed_lesson_trace_preview_enabled": True,
        "trace_only_preview": True,
        "requires_valid_lesson_candidate": True,
        "requires_valid_human_review_decision": True,
        "approved_for_preview_only": True,
        "lesson_application_allowed": False,
        "lesson_applied": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "memory_write": False,
        "predictor_modified": False,
        "persistent_rule_write": False,
        "persistent_learning": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "runtime_action_selection_added": False,
        "new_action_behavior_added": False,
        "llm_planning_used": False,
        "pathfinding_used": False,
        "route_replay_added": False,
        "autonomy_enabled": False,
        "lesson_application_runtime_count": summary["lesson_application_runtime_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "memory_write_count": summary["memory_write_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "persistent_rule_write_count": summary["persistent_rule_write_count"],
        "autonomy_enabled_count": summary["autonomy_enabled_count"],
        "proof_of_learning_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }


def _preview_type(candidate: dict[str, Any]) -> str:
    return {
        "precondition_or_correction": "precondition_or_correction_trace",
        "avoid_repeat_failure": "avoid_repeat_failure_trace",
        "ask_for_help_before_retry": "ask_for_help_trace",
    }.get(candidate.get("candidate_type"), "unknown_trace")


def _boundary_summary() -> dict[str, bool]:
    return {
        "trace_only_preview": True,
        "lesson_application_allowed": False,
        "lesson_applied": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "memory_write": False,
        "predictor_modified": False,
        "persistent_rule_write": False,
        "persistent_learning": False,
        "autonomy_enabled": False,
    }


def _source_trace(candidate: dict[str, Any], decision: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "source": "reviewed_lesson_trace_preview",
        "review_decision_source": "lesson_candidate_human_review_decision_schema",
        "evidence_summary_source": "lesson_candidate_review_evidence_summary",
        "lesson_candidate_source": "lesson_candidate_from_failure_reason",
        "source_review_decision_id": None if decision is None else decision.get("review_decision_id"),
        "source_evidence_summary_id": None if decision is None else decision.get("source_evidence_summary_id"),
        "source_lesson_candidate_id": candidate.get("lesson_candidate_id"),
        "source_failure_reason_id": candidate.get("source_failure_reason_id"),
        "source_pair_id": candidate.get("source_pair_id"),
        "action_intent_id": candidate.get("action_intent_id"),
    }


def _safety_flags() -> dict[str, bool]:
    return {
        "blocked_from_lesson_application": True,
        "blocked_from_action_selection": True,
        "blocked_from_action_behavior_change": True,
        "blocked_from_memory_write": True,
        "blocked_from_predictor_mutation": True,
        "blocked_from_persistent_rule_write": True,
    }


def _preview_id(decision: dict[str, Any] | None, candidate: dict[str, Any], status: Any) -> str:
    source = "missing_review_decision" if decision is None else decision.get("review_decision_id")
    return f"lesson_trace_preview:{_ascii_safe(source)}:{_ascii_safe(candidate.get('lesson_candidate_id'))}:{_ascii_safe(status)}"


def _mutate(record: dict[str, Any], case_name: str, path: tuple[str, str], value: Any) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["case_name"] = case_name
    copied["preview_id"] = f"{record['preview_id']}:{case_name}"
    copied[path[0]][path[1]] = value
    return copied


def _dedupe(values: list[str]) -> list[str]:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)
