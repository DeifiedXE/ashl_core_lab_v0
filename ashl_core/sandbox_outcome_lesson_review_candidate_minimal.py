"""Sandbox outcome lesson-review candidate from action-outcome trace."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_execution_outcome_integration_minimal import build_sandbox_action_outcome_trace


COMMAND = "run-sandbox-outcome-lesson-review-candidate-minimal-check"
FLOW = "sandbox_outcome_lesson_review_candidate_minimal_v0"
CANDIDATE_MODE = "sandbox_outcome_lesson_review_candidate_only"
EXPECTED_SANDBOX_ID = "phase0_toy_sandbox_obstacle_retry_failed"
EXPECTED_SCENARIO_ID = "obstacle_retry_failed_same_state"
EXPECTED_EXACT_KEY = "obstacle_retry_failed"
EXPECTED_ACTION = "check_before_retry"

REQUIRED_FIELDS = {
    "lesson_review_candidate_id",
    "source_action_outcome_trace_id",
    "candidate_mode",
    "candidate_context",
    "candidate_content",
    "review_requirements",
    "human_summary",
    "blocked_flags",
}

REQUIRED_CANDIDATE_CONTEXT = {
    "sandbox_id",
    "scenario_id",
    "exact_key",
    "action_observed",
    "outcome_match",
    "sandbox_check_success",
    "failure_detected",
}

REQUIRED_CANDIDATE_CONTENT = {
    "candidate_type",
    "candidate_statement",
    "evidence_summary",
    "suggested_review_question",
    "confidence_scope",
}

REQUIRED_REVIEW_REQUIREMENTS = {
    "requires_human_review",
    "approved_for_lesson_application",
    "approved_for_memory_write",
    "approved_for_retention_write",
    "approved_for_predictor_mutation",
    "approved_for_runtime_behavior_change",
}

REQUIRED_HUMAN_SUMMARY = {
    "what_was_created",
    "what_the_candidate_says",
    "what_review_is_required",
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


def build_sandbox_outcome_lesson_review_candidate(
    action_outcome_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = action_outcome_trace or build_sandbox_action_outcome_trace()
    trace_result = source.get("trace_result", {})
    evidence_source = source.get("lesson_evidence_candidate_source", {})
    action = trace_result.get("action_observed", "")
    if not _source_trace_allows_candidate(trace_result, evidence_source):
        action = ""

    return {
        "lesson_review_candidate_id": "sandbox_outcome_lesson_review_candidate_demo_001",
        "source_action_outcome_trace_id": source.get(
            "action_outcome_trace_id",
            "sandbox_action_outcome_trace_demo_001",
        ),
        "candidate_mode": CANDIDATE_MODE,
        "candidate_context": {
            "sandbox_id": EXPECTED_SANDBOX_ID,
            "scenario_id": EXPECTED_SCENARIO_ID,
            "exact_key": EXPECTED_EXACT_KEY,
            "action_observed": action,
            "outcome_match": trace_result.get("outcome_match"),
            "sandbox_check_success": trace_result.get("sandbox_check_success"),
            "failure_detected": trace_result.get("failure_detected"),
        },
        "candidate_content": {
            "candidate_type": "successful_sandbox_check_evidence",
            "candidate_statement": (
                "In the controlled obstacle sandbox, check_before_retry detected the obstacle before retrying "
                "and prevented retry_same_action movement."
            ),
            "evidence_summary": (
                "checked_before_retry=True; obstacle_detected=True; retry_same_action_executed=False; "
                "movement_executed=False."
            ),
            "suggested_review_question": (
                "Should check_before_retry be considered useful evidence for obstacle_retry_failed scenarios?"
            ),
            "confidence_scope": "controlled_sandbox_only",
        },
        "review_requirements": {
            "requires_human_review": True,
            "approved_for_lesson_application": False,
            "approved_for_memory_write": False,
            "approved_for_retention_write": False,
            "approved_for_predictor_mutation": False,
            "approved_for_runtime_behavior_change": False,
        },
        "human_summary": {
            "what_was_created": "A lesson-review candidate was created from the sandbox action outcome trace.",
            "what_the_candidate_says": (
                "The controlled check_before_retry action succeeded by detecting the obstacle before retrying."
            ),
            "what_review_is_required": (
                "Human review is required before any lesson, memory write, retention write, predictor mutation, "
                "or behavior change."
            ),
            "plain_result": "The sandbox outcome can now be reviewed as lesson evidence, but no lesson has been applied.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_sandbox_outcome_lesson_review_candidate(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _check_top_level(record, REQUIRED_FIELDS, errors)

    if record.get("candidate_mode") != CANDIDATE_MODE:
        errors.append("candidate_mode_not_sandbox_outcome_lesson_review_candidate_only")

    context = _section(record, "candidate_context", errors)
    _require_section_fields("candidate_context", context, REQUIRED_CANDIDATE_CONTEXT, errors)
    if context.get("sandbox_id") != EXPECTED_SANDBOX_ID:
        errors.append("sandbox_id_not_phase0_toy_sandbox_obstacle_retry_failed")
    if context.get("scenario_id") != EXPECTED_SCENARIO_ID:
        errors.append("scenario_id_not_obstacle_retry_failed_same_state")
    if context.get("exact_key") != EXPECTED_EXACT_KEY:
        errors.append("exact_key_not_obstacle_retry_failed")
    if context.get("action_observed") != EXPECTED_ACTION:
        errors.append("action_observed_not_check_before_retry")
    _require_true(context, "outcome_match", errors)
    _require_true(context, "sandbox_check_success", errors)
    _require_false(context, "failure_detected", errors)

    content = _section(record, "candidate_content", errors)
    _require_section_fields("candidate_content", content, REQUIRED_CANDIDATE_CONTENT, errors)
    if content.get("candidate_type") != "successful_sandbox_check_evidence":
        errors.append("candidate_type_not_successful_sandbox_check_evidence")
    for field in ("candidate_statement", "evidence_summary", "suggested_review_question"):
        if not isinstance(content.get(field), str) or not content.get(field):
            errors.append(f"{field}_empty_or_not_string")
    if content.get("confidence_scope") != "controlled_sandbox_only":
        errors.append("confidence_scope_not_controlled_sandbox_only")

    requirements = _section(record, "review_requirements", errors)
    _require_section_fields("review_requirements", requirements, REQUIRED_REVIEW_REQUIREMENTS, errors)
    _require_true(requirements, "requires_human_review", errors)
    for field in (
        "approved_for_lesson_application",
        "approved_for_memory_write",
        "approved_for_retention_write",
        "approved_for_predictor_mutation",
        "approved_for_runtime_behavior_change",
    ):
        _require_false(requirements, field, errors)

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
        "lesson_review_candidate_id": record.get("lesson_review_candidate_id"),
        "valid": not errors,
        "error_codes": errors,
        "candidate_created": record.get("candidate_mode") == CANDIDATE_MODE,
        "requires_human_review": requirements.get("requires_human_review") is True,
        **_blocked_flag_values(blocked_flags),
    }


def run_sandbox_outcome_lesson_review_candidate_minimal_check() -> dict[str, Any]:
    valid_candidate = build_sandbox_outcome_lesson_review_candidate()
    records = [valid_candidate, *_invalid_demo_records(valid_candidate)]
    validation_results = [validate_sandbox_outcome_lesson_review_candidate(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "sandbox_outcome_lesson_review_candidates": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "A sandbox outcome may become a lesson-review candidate, but it must not become an applied lesson without human review.",
            "This is not an applied lesson, retained memory, or proof of learning.",
            "Memory writes, retention writes, predictor mutation, runtime behavior change, and action selection remain blocked.",
        ],
    }


def _source_trace_allows_candidate(trace_result: dict[str, Any], evidence_source: dict[str, Any]) -> bool:
    return (
        trace_result.get("action_observed") == EXPECTED_ACTION
        and trace_result.get("outcome_match") is True
        and trace_result.get("sandbox_check_success") is True
        and trace_result.get("failure_detected") is False
        and trace_result.get("evidence_available") is True
        and evidence_source.get("can_feed_lesson_evidence_candidate") is True
        and evidence_source.get("requires_human_review_before_lesson") is True
        and evidence_source.get("lesson_applied") is False
        and evidence_source.get("memory_write") is False
        and evidence_source.get("retention_write") is False
    )


def _invalid_demo_records(valid_candidate: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    invalid = _copy_case(valid_candidate, "bad_candidate_mode")
    invalid["candidate_mode"] = "applied_lesson"
    records.append(invalid)

    for field, value in [
        ("sandbox_id", "bad_sandbox"),
        ("scenario_id", "bad_scenario"),
        ("exact_key", "bad_key"),
        ("action_observed", "retry_same_action"),
        ("outcome_match", False),
        ("sandbox_check_success", False),
        ("failure_detected", True),
    ]:
        invalid = _copy_case(valid_candidate, f"{field}_{value}")
        invalid["candidate_context"][field] = value
        records.append(invalid)

    for field, value in [
        ("candidate_type", "applied_lesson"),
        ("candidate_statement", ""),
        ("evidence_summary", ""),
        ("suggested_review_question", ""),
        ("confidence_scope", "generalized_behavior"),
    ]:
        invalid = _copy_case(valid_candidate, f"{field}_{value}")
        invalid["candidate_content"][field] = value
        records.append(invalid)

    for field, value in [
        ("requires_human_review", False),
        ("approved_for_lesson_application", True),
        ("approved_for_memory_write", True),
        ("approved_for_retention_write", True),
        ("approved_for_predictor_mutation", True),
        ("approved_for_runtime_behavior_change", True),
    ]:
        invalid = _copy_case(valid_candidate, f"{field}_{value}")
        invalid["review_requirements"][field] = value
        records.append(invalid)

    for field in ("what_was_created", "what_review_is_required", "plain_result"):
        invalid = _copy_case(valid_candidate, f"empty_{field}")
        invalid["human_summary"][field] = ""
        records.append(invalid)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid = _copy_case(valid_candidate, flag)
        invalid["blocked_flags"][flag] = True
        records.append(invalid)

    return records


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "lesson_review_candidate_result_count": len(validation_results),
        "valid_lesson_review_candidate_count": len(valid_results),
        "invalid_lesson_review_candidate_count": sum(1 for result in validation_results if not result["valid"]),
        "candidate_created_count": sum(1 for result in valid_results if result["candidate_created"]),
        "requires_human_review_count": sum(1 for result in valid_results if result["requires_human_review"]),
        "approved_for_lesson_application_blocked_count": _count_error(
            validation_results,
            "approved_for_lesson_application_not_false",
        ),
        "approved_for_memory_write_blocked_count": _count_error(
            validation_results,
            "approved_for_memory_write_not_false",
        ),
        "approved_for_retention_write_blocked_count": _count_error(
            validation_results,
            "approved_for_retention_write_not_false",
        ),
        "approved_for_predictor_mutation_blocked_count": _count_error(
            validation_results,
            "approved_for_predictor_mutation_not_false",
        ),
        "approved_for_runtime_behavior_change_blocked_count": _count_error(
            validation_results,
            "approved_for_runtime_behavior_change_not_false",
        ),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "retention_write_blocked_count": _count_error(validation_results, "retention_write_enabled"),
        "new_retention_written_blocked_count": _count_error(validation_results, "new_retention_written_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "runtime_behavior_changed_blocked_count": _count_error(
            validation_results,
            "runtime_behavior_changed_enabled",
        ),
        "production_action_selection_blocked_count": _count_error(
            validation_results,
            "production_action_selection_enabled",
        ),
        "runtime_action_selection_blocked_count": _count_error(validation_results, "runtime_action_selection_enabled"),
        "selected_action_created_blocked_count": _count_error(
            validation_results,
            "selected_action_created_enabled",
        ),
        "final_action_created_blocked_count": _count_error(validation_results, "final_action_created_enabled"),
        "direct_action_command_blocked_count": _count_error(validation_results, "direct_action_command_enabled"),
        "persistent_policy_written_blocked_count": _count_error(
            validation_results,
            "persistent_policy_written_enabled",
        ),
        "general_behavior_changed_blocked_count": _count_error(
            validation_results,
            "general_behavior_changed_enabled",
        ),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
    }
    summary["all_sandbox_outcome_lesson_review_candidate_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["lesson_review_candidate_result_count"] == 39
        and summary["valid_lesson_review_candidate_count"] == 1
        and summary["invalid_lesson_review_candidate_count"] == 38
        and summary["candidate_created_count"] == 1
        and summary["requires_human_review_count"] == 1
        and summary["approved_for_lesson_application_blocked_count"] == 1
        and summary["approved_for_memory_write_blocked_count"] == 1
        and summary["approved_for_retention_write_blocked_count"] == 1
        and summary["approved_for_predictor_mutation_blocked_count"] == 1
        and summary["approved_for_runtime_behavior_change_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["retention_write_blocked_count"] == 1
        and summary["new_retention_written_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["runtime_behavior_changed_blocked_count"] == 1
        and summary["production_action_selection_blocked_count"] == 1
        and summary["runtime_action_selection_blocked_count"] == 1
        and summary["selected_action_created_blocked_count"] == 1
        and summary["final_action_created_blocked_count"] == 1
        and summary["direct_action_command_blocked_count"] == 1
        and summary["persistent_policy_written_blocked_count"] == 1
        and summary["general_behavior_changed_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "sandbox_outcome_lesson_review_candidate_enabled": True,
        "lesson_application_added": False,
        "memory_write_added": False,
        "retention_write_added": False,
        "predictor_mutation_added": False,
        "runtime_behavior_change_added": False,
        "action_selection_added": False,
        "final_action_added": False,
        "direct_action_command_added": False,
        "proof_of_learning_claimed": False,
        "valid_lesson_review_candidate_count": summary.get("valid_lesson_review_candidate_count"),
    }


def _check_top_level(record: dict[str, Any], required: set[str], errors: list[str]) -> None:
    missing_fields = sorted(field for field in required if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)
    extra_fields = sorted(field for field in record if field not in required)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)


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


def _blocked_flag_values(blocked_flags: dict[str, Any]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["lesson_review_candidate_id"] = f"{record['lesson_review_candidate_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])
