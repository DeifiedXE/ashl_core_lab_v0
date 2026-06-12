"""Generic human lesson-review decision gate for evidence sources."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .phase0_level1_contrast_sample_set_minimal import build_phase0_level1_contrast_sample_set


COMMAND = "run-generic-lesson-review-decision-minimal-check"
FLOW = "generic_lesson_review_decision_minimal_v0"
DECISION_ID = "generic_lesson_review_decision_demo_001"
ALLOWED_SOURCE_TYPES = {
    "sandbox_outcome_trace",
    "action_outcome_trace",
    "visual_trace",
    "failure_reason_trace",
    "path_trace",
    "contrast_sample_set",
    "phase0_level1_contrast_sample_set",
}
ALLOWED_DECISIONS = {
    "accepted_for_reviewed_lesson_preview",
    "rejected",
    "needs_more_evidence",
}
REQUIRED_TOP_LEVEL = {
    "lesson_review_decision_id",
    "decision_mode",
    "source",
    "candidate_summary",
    "human_review_decision",
    "decision_result",
    "allowed_next_layer",
    "human_summary",
    "blocked_flags",
}
REQUIRED_HUMAN_SUMMARY = {
    "what_was_reviewed",
    "decision",
    "what_can_happen_next",
    "what_is_blocked",
    "plain_result",
}
REQUIRED_BLOCKED_FLAGS = {
    "lesson_applied",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_modified",
    "runtime_behavior_changed",
    "production_action_selection",
    "runtime_action_selection",
    "selected_action_created",
    "final_action_created",
    "direct_action_command",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_policy_written",
    "general_behavior_changed",
    "proof_of_learning_claim",
}
NEXT_LAYER_FIELDS = {
    "may_enter_reviewed_lesson_preview",
    "may_enter_lesson_dry_run",
    "may_apply_lesson",
    "may_write_memory",
    "may_write_retention",
    "may_mutate_predictor",
    "may_change_runtime_behavior",
}


def build_generic_lesson_review_decision(
    source_record: dict[str, Any] | None = None,
    decision: str = "accepted_for_reviewed_lesson_preview",
) -> dict[str, Any]:
    if source_record is None:
        source_record = build_phase0_level1_contrast_sample_set()

    sample_set_id = source_record.get("sample_set_id", "unknown_source_trace")
    level_id = source_record.get("level_info", {}).get("level_id", "unknown_source")
    contrast = source_record.get("contrast_result", {})
    source = {
        "source_type": "phase0_level1_contrast_sample_set",
        "source_id": level_id,
        "source_trace_ref": sample_set_id,
        "source_confidence_scope": "controlled_sandbox_only",
    }
    candidate_summary = {
        "candidate_type": "contrast_supported_lesson_review_candidate",
        "candidate_statement": (
            "In controlled Level 1 danger fixtures, check_before_retry is useful when danger is present, "
            "retry_same_action is unsafe when danger is present, and check_before_retry can be neutral "
            "when no danger is present."
        ),
        "evidence_summary": "success/failure/neutral contrast sample set is present.",
        "requires_human_review": True,
    }
    if not contrast.get("supports_lesson_review_candidate"):
        candidate_summary["evidence_summary"] = "source contrast evidence is not ready."

    return {
        "lesson_review_decision_id": _decision_id(decision),
        "decision_mode": "generic_human_lesson_review_decision",
        "source": source,
        "candidate_summary": candidate_summary,
        "human_review_decision": _human_review_decision(decision),
        "decision_result": _decision_result(decision),
        "allowed_next_layer": _allowed_next_layer(decision),
        "human_summary": _human_summary(decision),
        "blocked_flags": _blocked_flags(),
    }


def validate_generic_lesson_review_decision(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _check_top_level(record, errors)

    if record.get("decision_mode") != "generic_human_lesson_review_decision":
        errors.append("decision_mode_not_generic_human_lesson_review_decision")

    source = _section(record, "source", errors)
    if source.get("source_type") not in ALLOWED_SOURCE_TYPES:
        errors.append("unknown_source_type")
    for field in ("source_id", "source_trace_ref", "source_confidence_scope"):
        _require_non_empty(source, field, errors)

    candidate = _section(record, "candidate_summary", errors)
    for field in ("candidate_type", "candidate_statement", "evidence_summary"):
        _require_non_empty(candidate, field, errors)
    _require_true(candidate, "requires_human_review", errors)

    review = _section(record, "human_review_decision", errors)
    decision = review.get("decision")
    if decision not in ALLOWED_DECISIONS:
        errors.append("unknown_decision")
    for field in ("reviewer", "review_reason", "reviewed_at"):
        _require_non_empty(review, field, errors)

    decision_result = _section(record, "decision_result", errors)
    allowed_next = _section(record, "allowed_next_layer", errors)
    _validate_decision_result(decision, decision_result, errors)
    _validate_allowed_next_layer(decision, allowed_next, errors)

    for field in (
        "lesson_applied",
        "memory_write",
        "retention_write",
        "predictor_modified",
        "runtime_behavior_changed",
    ):
        _require_false(decision_result, field, errors)

    human_summary = _section(record, "human_summary", errors)
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        _require_non_empty(human_summary, field, errors)

    blocked_flags = _section(record, "blocked_flags", errors)
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "lesson_review_decision_id": record.get("lesson_review_decision_id"),
        "valid": not errors,
        "error_codes": errors,
        "decision": decision,
        "accepted_for_preview": decision_result.get("accepted_for_reviewed_lesson_preview") is True,
        "rejected": decision_result.get("rejected") is True,
        "needs_more_evidence": decision_result.get("needs_more_evidence") is True,
        "may_enter_reviewed_lesson_preview": allowed_next.get("may_enter_reviewed_lesson_preview") is True,
        "may_enter_lesson_dry_run": allowed_next.get("may_enter_lesson_dry_run") is True,
    }


def run_generic_lesson_review_decision_minimal_check() -> dict[str, Any]:
    valid_records = [
        build_generic_lesson_review_decision(decision="accepted_for_reviewed_lesson_preview"),
        build_generic_lesson_review_decision(decision="rejected"),
        build_generic_lesson_review_decision(decision="needs_more_evidence"),
    ]
    records = valid_records + _build_invalid_records()
    validation_results = [validate_generic_lesson_review_decision(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_generic_lesson_review_decision_minimal_checks_passed"] else "failed",
        "lesson_review_decisions": records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "generic_decision_gate_only": True,
            "source_specific_sandbox_channel_created": False,
            "lesson_application_added": False,
            "memory_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "runtime_behavior_change_added": False,
            "proof_of_learning_claimed": False,
        },
        "notes": [
            "Different evidence sources may enter the same lesson review decision gate.",
            "The decision gate does not apply lessons.",
        ],
    }


def _decision_id(decision: str) -> str:
    suffix = {
        "accepted_for_reviewed_lesson_preview": "accepted_001",
        "rejected": "rejected_001",
        "needs_more_evidence": "needs_more_evidence_001",
    }.get(decision, "invalid_001")
    return f"{DECISION_ID}:{suffix}"


def _human_review_decision(decision: str) -> dict[str, Any]:
    reasons = {
        "accepted_for_reviewed_lesson_preview": "The contrast set is sufficient to preview a lesson, but not to apply it.",
        "rejected": "The candidate should not continue from this review decision.",
        "needs_more_evidence": "The candidate needs more evidence before preview or dry-run.",
    }
    return {
        "decision": decision,
        "reviewer": "human_mentor",
        "review_reason": reasons.get(decision, "Invalid decision for negative control."),
        "reviewed_at": "static_demo_timestamp",
    }


def _decision_result(decision: str) -> dict[str, bool]:
    return {
        "accepted_for_reviewed_lesson_preview": decision == "accepted_for_reviewed_lesson_preview",
        "rejected": decision == "rejected",
        "needs_more_evidence": decision == "needs_more_evidence",
        "lesson_applied": False,
        "memory_write": False,
        "retention_write": False,
        "predictor_modified": False,
        "runtime_behavior_changed": False,
    }


def _allowed_next_layer(decision: str) -> dict[str, bool]:
    accepted = decision == "accepted_for_reviewed_lesson_preview"
    return {
        "may_enter_reviewed_lesson_preview": accepted,
        "may_enter_lesson_dry_run": accepted,
        "may_apply_lesson": False,
        "may_write_memory": False,
        "may_write_retention": False,
        "may_mutate_predictor": False,
        "may_change_runtime_behavior": False,
    }


def _human_summary(decision: str) -> dict[str, str]:
    decision_text = {
        "accepted_for_reviewed_lesson_preview": "The candidate was accepted for reviewed lesson preview only.",
        "rejected": "The candidate was rejected and cannot continue.",
        "needs_more_evidence": "The candidate needs more evidence and cannot continue yet.",
    }.get(decision, "The decision is invalid.")
    next_text = {
        "accepted_for_reviewed_lesson_preview": "It may enter reviewed lesson preview or dry-run.",
        "rejected": "No next layer is allowed.",
        "needs_more_evidence": "No next layer is allowed until more evidence is reviewed.",
    }.get(decision, "No next layer is allowed.")
    return {
        "what_was_reviewed": "A Level 1 contrast-supported lesson-review candidate was reviewed.",
        "decision": decision_text,
        "what_can_happen_next": next_text,
        "what_is_blocked": (
            "Lesson application, memory writes, retention writes, predictor mutation, and runtime behavior change remain blocked."
        ),
        "plain_result": "The generic decision gate recorded a human review decision without applying a lesson.",
    }


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _build_invalid_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    valid_accepted = build_generic_lesson_review_decision(decision="accepted_for_reviewed_lesson_preview")
    valid_rejected = build_generic_lesson_review_decision(decision="rejected")
    valid_more = build_generic_lesson_review_decision(decision="needs_more_evidence")

    records.append(_mutate(valid_accepted, ["decision_mode"], "bad_mode", "bad_decision_mode"))
    records.append(_mutate(valid_accepted, ["source", "source_type"], "unknown_trace", "unknown_source_type"))
    records.append(_mutate(valid_accepted, ["source", "source_id"], "", "empty_source_id"))
    records.append(_mutate(valid_accepted, ["candidate_summary", "candidate_statement"], "", "empty_candidate_statement"))
    records.append(_mutate(valid_accepted, ["candidate_summary", "requires_human_review"], False, "requires_human_review_false"))
    records.append(_mutate(valid_accepted, ["human_review_decision", "decision"], "applied", "unknown_decision"))
    records.append(_mutate(valid_accepted, ["decision_result", "accepted_for_reviewed_lesson_preview"], False, "accepted_result_mismatch"))
    records.append(_mutate(valid_rejected, ["decision_result", "rejected"], False, "rejected_result_mismatch"))
    records.append(_mutate(valid_more, ["decision_result", "needs_more_evidence"], False, "needs_more_evidence_result_mismatch"))
    for field in (
        "may_apply_lesson",
        "may_write_memory",
        "may_write_retention",
        "may_mutate_predictor",
        "may_change_runtime_behavior",
    ):
        records.append(_mutate(valid_accepted, ["allowed_next_layer", field], True, f"accepted_{field}"))
    records.append(
        _mutate(valid_rejected, ["allowed_next_layer", "may_enter_reviewed_lesson_preview"], True, "rejected_may_enter_preview")
    )
    records.append(
        _mutate(valid_more, ["allowed_next_layer", "may_enter_lesson_dry_run"], True, "needs_more_evidence_may_dry_run")
    )
    records.append(_mutate(valid_accepted, ["human_review_decision", "reviewer"], "", "empty_reviewer"))
    records.append(_mutate(valid_accepted, ["human_review_decision", "review_reason"], "", "empty_review_reason"))
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        records.append(_mutate(valid_accepted, ["human_summary", field], "", f"empty_{field}"))
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        records.append(_mutate(valid_accepted, ["blocked_flags", field], True, field))
    return records


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "lesson_review_decision_result_count": len(validation_results),
        "valid_lesson_review_decision_count": len(valid_results),
        "invalid_lesson_review_decision_count": sum(1 for result in validation_results if not result["valid"]),
        "accepted_for_preview_count": sum(1 for result in valid_results if result["accepted_for_preview"]),
        "rejected_count": sum(1 for result in valid_results if result["rejected"]),
        "needs_more_evidence_count": sum(1 for result in valid_results if result["needs_more_evidence"]),
        "may_enter_reviewed_lesson_preview_count": sum(
            1 for result in valid_results if result["may_enter_reviewed_lesson_preview"]
        ),
        "may_enter_lesson_dry_run_count": sum(1 for result in valid_results if result["may_enter_lesson_dry_run"]),
        "lesson_application_blocked_count": _count_error(validation_results, "may_apply_lesson_not_false")
        + _count_error(validation_results, "lesson_applied_not_false")
        + _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "may_write_memory_not_false")
        + _count_error(validation_results, "memory_write_not_false")
        + _count_error(validation_results, "memory_write_enabled"),
        "retention_write_blocked_count": _count_error(validation_results, "may_write_retention_not_false")
        + _count_error(validation_results, "retention_write_not_false")
        + _count_error(validation_results, "retention_write_enabled"),
        "predictor_mutation_blocked_count": _count_error(validation_results, "may_mutate_predictor_not_false")
        + _count_error(validation_results, "predictor_modified_not_false")
        + _count_error(validation_results, "predictor_modified_enabled"),
        "runtime_behavior_change_blocked_count": _count_error(validation_results, "may_change_runtime_behavior_not_false")
        + _count_error(validation_results, "runtime_behavior_changed_not_false")
        + _count_error(validation_results, "runtime_behavior_changed_enabled"),
        "unknown_source_type_blocked_count": _count_error(validation_results, "unknown_source_type"),
        "unknown_decision_blocked_count": _count_error(validation_results, "unknown_decision"),
        "decision_inconsistency_blocked_count": _count_error(validation_results, "decision_result_inconsistent")
        + _count_error(validation_results, "allowed_next_layer_inconsistent"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
    }
    summary["all_generic_lesson_review_decision_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["lesson_review_decision_result_count"] == 42
        and summary["valid_lesson_review_decision_count"] == 3
        and summary["invalid_lesson_review_decision_count"] == 39
        and summary["accepted_for_preview_count"] == 1
        and summary["rejected_count"] == 1
        and summary["needs_more_evidence_count"] == 1
        and summary["may_enter_reviewed_lesson_preview_count"] == 1
        and summary["may_enter_lesson_dry_run_count"] == 1
        and summary["lesson_application_blocked_count"] >= 2
        and summary["memory_write_blocked_count"] >= 2
        and summary["retention_write_blocked_count"] >= 2
        and summary["predictor_mutation_blocked_count"] >= 2
        and summary["runtime_behavior_change_blocked_count"] >= 2
        and summary["unknown_source_type_blocked_count"] == 1
        and summary["unknown_decision_blocked_count"] == 1
        and summary["decision_inconsistency_blocked_count"] >= 5
        and summary["proof_of_learning_claim_blocked_count"] == 1
    )


def _validate_decision_result(decision: Any, result: dict[str, Any], errors: list[str]) -> None:
    expected = _decision_result(decision if isinstance(decision, str) else "")
    for field, expected_value in expected.items():
        if result.get(field) is not expected_value:
            errors.append(f"{field}_not_{str(expected_value).lower()}")
    if decision in ALLOWED_DECISIONS and any(result.get(field) is not value for field, value in expected.items()):
        errors.append("decision_result_inconsistent")


def _validate_allowed_next_layer(decision: Any, allowed: dict[str, Any], errors: list[str]) -> None:
    expected = _allowed_next_layer(decision if isinstance(decision, str) else "")
    for field in sorted(NEXT_LAYER_FIELDS):
        if field not in allowed:
            errors.append(f"missing_allowed_next_layer:{field}")
        elif allowed.get(field) is not expected[field]:
            errors.append(f"{field}_not_{str(expected[field]).lower()}")
    if decision in ALLOWED_DECISIONS and any(allowed.get(field) is not value for field, value in expected.items()):
        errors.append("allowed_next_layer_inconsistent")


def _check_top_level(record: dict[str, Any], errors: list[str]) -> None:
    for field in sorted(REQUIRED_TOP_LEVEL):
        if field not in record:
            errors.append(f"missing_required_field:{field}")
    for field in sorted(record):
        if field not in REQUIRED_TOP_LEVEL:
            errors.append(f"unexpected_field:{field}")


def _section(record: dict[str, Any], field: str, errors: list[str]) -> dict[str, Any]:
    value = record.get(field)
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _require_non_empty(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if field not in section:
        errors.append(f"missing_field:{field}")
    elif not isinstance(section.get(field), str) or not section.get(field):
        errors.append(f"{field}_empty_or_not_string")


def _require_true(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not True:
        errors.append(f"{field}_not_true")


def _require_false(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not False:
        errors.append(f"{field}_not_false")


def _mutate(record: dict[str, Any], path: list[str], value: Any, suffix: str) -> dict[str, Any]:
    mutated = deepcopy(record)
    current = mutated
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value
    mutated["lesson_review_decision_id"] = f"{record.get('lesson_review_decision_id')}:{suffix}"
    return mutated


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


if __name__ == "__main__":
    import json

    print(json.dumps(run_generic_lesson_review_decision_minimal_check(), ensure_ascii=False, indent=2))
