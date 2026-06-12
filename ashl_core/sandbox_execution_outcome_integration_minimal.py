"""Sandbox execution outcome integration into trace evidence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .one_step_sandbox_action_execution_minimal import (
    build_one_step_sandbox_action_execution,
)


COMMAND = "run-sandbox-execution-outcome-integration-minimal-check"
FLOW = "sandbox_execution_outcome_integration_minimal_v0"
EXPECTED_ACTION = "check_before_retry"
EXPECTED_SANDBOX_ID = "phase0_toy_sandbox_obstacle_retry_failed"
EXPECTED_SCENARIO_ID = "obstacle_retry_failed_same_state"
EXPECTED_EXACT_KEY = "obstacle_retry_failed"

REQUIRED_PAIR_FIELDS = {
    "outcome_pair_id",
    "source_sandbox_execution_id",
    "action_context",
    "expected_outcome",
    "actual_outcome",
    "comparison_result",
    "human_summary",
    "blocked_flags",
}

REQUIRED_TRACE_FIELDS = {
    "action_outcome_trace_id",
    "source_outcome_pair_id",
    "trace_mode",
    "trace_result",
    "lesson_evidence_candidate_source",
    "human_summary",
    "blocked_flags",
}

REQUIRED_OUTCOME_FIELDS = {
    "checked_before_retry",
    "obstacle_detected",
    "retry_same_action_executed",
    "movement_executed",
    "real_world_effect",
    "production_effect",
}

REQUIRED_PAIR_HUMAN_SUMMARY = {
    "expected",
    "actual",
    "comparison",
    "plain_result",
}

REQUIRED_TRACE_HUMAN_SUMMARY = {
    "what_was_traced",
    "what_the_trace_says",
    "what_it_can_feed",
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
    "lesson_applied",
    "memory_write",
    "new_retention_written",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_sandbox_execution_outcome_pair(execution_result: dict[str, Any] | None = None) -> dict[str, Any]:
    source = execution_result or build_one_step_sandbox_action_execution()
    before = source.get("sandbox_before", {})
    after = source.get("sandbox_after", {})
    outcome = source.get("execution_outcome", {})
    actual = {
        "checked_before_retry": after.get("checked_before_retry"),
        "obstacle_detected": after.get("obstacle_detected"),
        "retry_same_action_executed": after.get("retry_same_action_executed"),
        "movement_executed": after.get("movement_executed"),
        "real_world_effect": outcome.get("real_world_effect"),
        "production_effect": outcome.get("production_effect"),
    }
    expected = _expected_outcome()
    mismatch_keys = [key for key in sorted(expected) if expected.get(key) != actual.get(key)]

    return {
        "outcome_pair_id": "sandbox_execution_outcome_pair_demo_001",
        "source_sandbox_execution_id": source.get(
            "sandbox_execution_id",
            "one_step_sandbox_action_execution_demo_001",
        ),
        "action_context": {
            "sandbox_id": before.get("sandbox_id", EXPECTED_SANDBOX_ID),
            "scenario_id": before.get("scenario_id", EXPECTED_SCENARIO_ID),
            "exact_key": before.get("exact_key", EXPECTED_EXACT_KEY),
            "executed_sandbox_action": source.get("executed_sandbox_action", EXPECTED_ACTION),
            "state_mutation_scope": outcome.get("state_mutation_scope", "sandbox_record_only"),
        },
        "expected_outcome": expected,
        "actual_outcome": actual,
        "comparison_result": {
            "outcome_match": not mismatch_keys,
            "failure_detected": False,
            "sandbox_check_success": not mismatch_keys,
            "mismatch_keys": mismatch_keys,
        },
        "human_summary": {
            "expected": "The sandbox check was expected to inspect before retrying and detect the obstacle without movement.",
            "actual": "The sandbox check inspected before retrying, detected the obstacle, and did not move.",
            "comparison": "Expected and actual sandbox outcomes match.",
            "plain_result": "The sandbox action did what it was expected to do, inside sandbox-only scope.",
        },
        "blocked_flags": _blocked_flags(),
    }


def build_sandbox_action_outcome_trace(outcome_pair: dict[str, Any] | None = None) -> dict[str, Any]:
    source = outcome_pair or build_sandbox_execution_outcome_pair()
    comparison = source.get("comparison_result", {})
    context = source.get("action_context", {})
    return {
        "action_outcome_trace_id": "sandbox_action_outcome_trace_demo_001",
        "source_outcome_pair_id": source.get("outcome_pair_id", "sandbox_execution_outcome_pair_demo_001"),
        "trace_mode": "sandbox_execution_outcome_trace_only",
        "trace_result": {
            "action_observed": context.get("executed_sandbox_action", EXPECTED_ACTION),
            "outcome_match": comparison.get("outcome_match"),
            "sandbox_check_success": comparison.get("sandbox_check_success"),
            "failure_detected": comparison.get("failure_detected"),
            "evidence_available": True,
            "state_mutation_scope": context.get("state_mutation_scope", "sandbox_record_only"),
        },
        "lesson_evidence_candidate_source": {
            "can_feed_lesson_evidence_candidate": True,
            "requires_human_review_before_lesson": True,
            "lesson_applied": False,
            "memory_write": False,
            "retention_write": False,
        },
        "human_summary": {
            "what_was_traced": "The one-step sandbox check action and its expected/actual outcome were traced.",
            "what_the_trace_says": "The check succeeded: the obstacle was detected before retry and no movement occurred.",
            "what_it_can_feed": "The trace may be shown as lesson-review evidence, but it does not apply a lesson.",
            "plain_result": "The sandbox execution result is now connected back into the outcome/evidence line.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_sandbox_execution_outcome_pair(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _check_top_level(record, REQUIRED_PAIR_FIELDS, errors)

    context = _section(record, "action_context", errors)
    if context.get("sandbox_id") != EXPECTED_SANDBOX_ID:
        errors.append("sandbox_id_not_phase0_toy_sandbox_obstacle_retry_failed")
    if context.get("scenario_id") != EXPECTED_SCENARIO_ID:
        errors.append("scenario_id_not_obstacle_retry_failed_same_state")
    if context.get("exact_key") != EXPECTED_EXACT_KEY:
        errors.append("exact_key_not_obstacle_retry_failed")
    if context.get("executed_sandbox_action") != EXPECTED_ACTION:
        errors.append("executed_sandbox_action_not_check_before_retry")
    if context.get("state_mutation_scope") != "sandbox_record_only":
        errors.append("state_mutation_scope_not_sandbox_record_only")

    expected = _section(record, "expected_outcome", errors)
    actual = _section(record, "actual_outcome", errors)
    for section_name, section in (("expected", expected), ("actual", actual)):
        _require_section_fields(f"{section_name}_outcome", section, REQUIRED_OUTCOME_FIELDS, errors)
        _require_true(section, "checked_before_retry", errors, prefix=section_name)
        _require_true(section, "obstacle_detected", errors, prefix=section_name)
        _require_false(section, "retry_same_action_executed", errors, prefix=section_name)
        _require_false(section, "movement_executed", errors, prefix=section_name)
        _require_false(section, "real_world_effect", errors, prefix=section_name)
        _require_false(section, "production_effect", errors, prefix=section_name)

    comparison = _section(record, "comparison_result", errors)
    _require_true(comparison, "outcome_match", errors)
    _require_false(comparison, "failure_detected", errors)
    _require_true(comparison, "sandbox_check_success", errors)
    if comparison.get("mismatch_keys") != []:
        errors.append("mismatch_keys_not_empty")

    _validate_human_summary(record, REQUIRED_PAIR_HUMAN_SUMMARY, errors)
    blocked_flags = _validate_blocked_flags(record, errors)

    return {
        "record_id": record.get("outcome_pair_id"),
        "valid": not errors,
        "error_codes": errors,
        "outcome_match": comparison.get("outcome_match") is True,
        "sandbox_check_success": comparison.get("sandbox_check_success") is True,
        **_blocked_flag_values(blocked_flags),
    }


def validate_sandbox_action_outcome_trace(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _check_top_level(record, REQUIRED_TRACE_FIELDS, errors)

    if record.get("trace_mode") != "sandbox_execution_outcome_trace_only":
        errors.append("trace_mode_not_sandbox_execution_outcome_trace_only")
    trace = _section(record, "trace_result", errors)
    if trace.get("action_observed") != EXPECTED_ACTION:
        errors.append("action_observed_not_check_before_retry")
    _require_true(trace, "outcome_match", errors, prefix="trace")
    _require_true(trace, "sandbox_check_success", errors, prefix="trace")
    _require_false(trace, "failure_detected", errors, prefix="trace")
    _require_true(trace, "evidence_available", errors, prefix="trace")
    if trace.get("state_mutation_scope") != "sandbox_record_only":
        errors.append("trace_state_mutation_scope_not_sandbox_record_only")

    source = _section(record, "lesson_evidence_candidate_source", errors)
    _require_true(source, "can_feed_lesson_evidence_candidate", errors)
    _require_true(source, "requires_human_review_before_lesson", errors)
    _require_false(source, "lesson_applied", errors)
    _require_false(source, "memory_write", errors)
    _require_false(source, "retention_write", errors)

    _validate_human_summary(record, REQUIRED_TRACE_HUMAN_SUMMARY, errors)
    blocked_flags = _validate_blocked_flags(record, errors)

    return {
        "record_id": record.get("action_outcome_trace_id"),
        "valid": not errors,
        "error_codes": errors,
        "evidence_available": trace.get("evidence_available") is True,
        "can_feed_lesson_evidence_candidate": source.get("can_feed_lesson_evidence_candidate") is True,
        "requires_human_review_before_lesson": source.get("requires_human_review_before_lesson") is True,
        **_blocked_flag_values(blocked_flags),
    }


def run_sandbox_execution_outcome_integration_minimal_check() -> dict[str, Any]:
    valid_pair = build_sandbox_execution_outcome_pair()
    valid_trace = build_sandbox_action_outcome_trace(valid_pair)
    outcome_pairs = [valid_pair, *_invalid_outcome_pairs(valid_pair)]
    action_outcome_traces = [valid_trace, *_invalid_action_outcome_traces(valid_trace)]
    pair_validations = [validate_sandbox_execution_outcome_pair(record) for record in outcome_pairs]
    trace_validations = [validate_sandbox_action_outcome_trace(record) for record in action_outcome_traces]
    summary = _build_summary(pair_validations, trace_validations)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "sandbox_execution_outcome_pairs": outcome_pairs,
        "sandbox_action_outcome_traces": action_outcome_traces,
        "valid_human_summaries": [
            outcome_pairs[0]["human_summary"],
            action_outcome_traces[0]["human_summary"],
        ],
        "validation_results": {
            "outcome_pairs": pair_validations,
            "action_outcome_traces": trace_validations,
        },
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Sandbox execution outcome may become evidence, but evidence is not learning, memory, or behavior change.",
            "The obstacle being detected is the successful result of checking before retrying.",
            "Lesson application, memory writes, retention writes, action selection, and proof claims remain blocked.",
        ],
    }


def _expected_outcome() -> dict[str, bool]:
    return {
        "checked_before_retry": True,
        "obstacle_detected": True,
        "retry_same_action_executed": False,
        "movement_executed": False,
        "real_world_effect": False,
        "production_effect": False,
    }


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _invalid_outcome_pairs(valid_pair: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for field, value, name in [
        ("sandbox_id", "bad_sandbox", "wrong_sandbox_id"),
        ("executed_sandbox_action", "retry_same_action", "wrong_executed_sandbox_action"),
        ("state_mutation_scope", "persistent_state", "wrong_state_mutation_scope"),
    ]:
        invalid = _copy_pair(valid_pair, name)
        invalid["action_context"][field] = value
        records.append(invalid)

    invalid = _copy_pair(valid_pair, "expected_checked_before_retry_false")
    invalid["expected_outcome"]["checked_before_retry"] = False
    records.append(invalid)

    for field, value in [
        ("checked_before_retry", False),
        ("obstacle_detected", False),
        ("retry_same_action_executed", True),
        ("movement_executed", True),
        ("real_world_effect", True),
        ("production_effect", True),
    ]:
        invalid = _copy_pair(valid_pair, f"actual_{field}_{value}")
        invalid["actual_outcome"][field] = value
        records.append(invalid)

    for field, value in [
        ("outcome_match", False),
        ("failure_detected", True),
        ("sandbox_check_success", False),
        ("mismatch_keys", ["obstacle_detected"]),
    ]:
        invalid = _copy_pair(valid_pair, f"{field}_{value}")
        invalid["comparison_result"][field] = value
        records.append(invalid)

    for field in sorted(REQUIRED_PAIR_HUMAN_SUMMARY):
        invalid = _copy_pair(valid_pair, f"empty_{field}")
        invalid["human_summary"][field] = ""
        records.append(invalid)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid = _copy_pair(valid_pair, flag)
        invalid["blocked_flags"][flag] = True
        records.append(invalid)

    return records


def _invalid_action_outcome_traces(valid_trace: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    invalid = _copy_trace(valid_trace, "bad_trace_mode")
    invalid["trace_mode"] = "production_trace"
    records.append(invalid)

    for field, value in [
        ("outcome_match", False),
        ("failure_detected", True),
        ("evidence_available", False),
    ]:
        invalid = _copy_trace(valid_trace, f"trace_{field}_{value}")
        invalid["trace_result"][field] = value
        records.append(invalid)

    for field, value in [
        ("can_feed_lesson_evidence_candidate", False),
        ("requires_human_review_before_lesson", False),
        ("lesson_applied", True),
        ("memory_write", True),
        ("retention_write", True),
    ]:
        invalid = _copy_trace(valid_trace, f"{field}_{value}")
        invalid["lesson_evidence_candidate_source"][field] = value
        records.append(invalid)

    for field in sorted(REQUIRED_TRACE_HUMAN_SUMMARY):
        invalid = _copy_trace(valid_trace, f"empty_{field}")
        invalid["human_summary"][field] = ""
        records.append(invalid)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid = _copy_trace(valid_trace, flag)
        invalid["blocked_flags"][flag] = True
        records.append(invalid)

    return records


def _build_summary(pair_validations: list[dict[str, Any]], trace_validations: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_pairs = [result for result in pair_validations if result["valid"]]
    valid_traces = [result for result in trace_validations if result["valid"]]
    all_validations = [*pair_validations, *trace_validations]
    summary: dict[str, int | bool] = {
        "sandbox_outcome_integration_result_count": len(pair_validations) + len(trace_validations),
        "valid_outcome_pair_count": len(valid_pairs),
        "valid_action_outcome_trace_count": len(valid_traces),
        "invalid_outcome_pair_count": sum(1 for result in pair_validations if not result["valid"]),
        "invalid_action_outcome_trace_count": sum(1 for result in trace_validations if not result["valid"]),
        "outcome_match_count": sum(1 for result in valid_pairs if result["outcome_match"]),
        "sandbox_check_success_count": sum(1 for result in valid_pairs if result["sandbox_check_success"]),
        "evidence_available_count": sum(1 for result in valid_traces if result["evidence_available"]),
        "can_feed_lesson_evidence_candidate_count": sum(
            1 for result in valid_traces if result["can_feed_lesson_evidence_candidate"]
        ),
        "requires_human_review_before_lesson_count": sum(
            1 for result in valid_traces if result["requires_human_review_before_lesson"]
        ),
        "lesson_applied_blocked_count": _count_error(all_validations, "lesson_applied_enabled")
        + _count_error(trace_validations, "lesson_applied_not_false"),
        "memory_write_blocked_count": _count_error(all_validations, "memory_write_enabled")
        + _count_error(trace_validations, "memory_write_not_false"),
        "retention_write_blocked_count": _count_error(trace_validations, "retention_write_not_false"),
        "production_action_selection_blocked_count": _count_error(
            all_validations,
            "production_action_selection_enabled",
        ),
        "runtime_action_selection_blocked_count": _count_error(all_validations, "runtime_action_selection_enabled"),
        "selected_action_created_blocked_count": _count_error(all_validations, "selected_action_created_enabled"),
        "final_action_created_blocked_count": _count_error(all_validations, "final_action_created_enabled"),
        "direct_action_command_blocked_count": _count_error(all_validations, "direct_action_command_enabled"),
        "real_navigation_changed_blocked_count": _count_error(all_validations, "real_navigation_changed_enabled"),
        "ui_behavior_changed_blocked_count": _count_error(all_validations, "ui_behavior_changed_enabled"),
        "persistent_policy_written_blocked_count": _count_error(
            all_validations,
            "persistent_policy_written_enabled",
        ),
        "general_behavior_changed_blocked_count": _count_error(all_validations, "general_behavior_changed_enabled"),
        "predictor_modified_blocked_count": _count_error(all_validations, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(all_validations, "proof_of_learning_claim_enabled"),
    }
    summary["all_sandbox_execution_outcome_integration_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["sandbox_outcome_integration_result_count"] == 61
        and summary["valid_outcome_pair_count"] == 1
        and summary["valid_action_outcome_trace_count"] == 1
        and summary["invalid_outcome_pair_count"] == 32
        and summary["invalid_action_outcome_trace_count"] == 27
        and summary["outcome_match_count"] == 1
        and summary["sandbox_check_success_count"] == 1
        and summary["evidence_available_count"] == 1
        and summary["can_feed_lesson_evidence_candidate_count"] == 1
        and summary["requires_human_review_before_lesson_count"] == 1
        and summary["lesson_applied_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["retention_write_blocked_count"] == 1
        and summary["production_action_selection_blocked_count"] == 2
        and summary["runtime_action_selection_blocked_count"] == 2
        and summary["selected_action_created_blocked_count"] == 2
        and summary["final_action_created_blocked_count"] == 2
        and summary["direct_action_command_blocked_count"] == 2
        and summary["persistent_policy_written_blocked_count"] == 2
        and summary["general_behavior_changed_blocked_count"] == 2
        and summary["predictor_modified_blocked_count"] == 2
        and summary["proof_of_learning_claim_blocked_count"] == 2
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "sandbox_outcome_integration_enabled": True,
        "new_sandbox_execution_added": False,
        "action_selection_added": False,
        "final_action_added": False,
        "direct_action_command_added": False,
        "lesson_application_added": False,
        "memory_write_added": False,
        "retention_write_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "valid_outcome_pair_count": summary.get("valid_outcome_pair_count"),
        "valid_action_outcome_trace_count": summary.get("valid_action_outcome_trace_count"),
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


def _require_true(section: dict[str, Any], field: str, errors: list[str], prefix: str | None = None) -> None:
    if section.get(field) is not True:
        errors.append(f"{prefix + '_' if prefix else ''}{field}_not_true")


def _require_false(section: dict[str, Any], field: str, errors: list[str], prefix: str | None = None) -> None:
    if section.get(field) is not False:
        errors.append(f"{prefix + '_' if prefix else ''}{field}_not_false")


def _validate_human_summary(record: dict[str, Any], required: set[str], errors: list[str]) -> None:
    human_summary = _section(record, "human_summary", errors)
    _require_section_fields("human_summary", human_summary, required, errors)
    for field in sorted(required):
        if not isinstance(human_summary.get(field), str) or not human_summary.get(field):
            errors.append(f"{field}_empty_or_not_string")


def _validate_blocked_flags(record: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    blocked_flags = _section(record, "blocked_flags", errors)
    _require_section_fields("blocked_flags", blocked_flags, REQUIRED_BLOCKED_FLAGS, errors)
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        if field in blocked_flags and blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")
    return blocked_flags


def _copy_pair(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["outcome_pair_id"] = f"{record['outcome_pair_id']}:{case_name}"
    return copied


def _copy_trace(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["action_outcome_trace_id"] = f"{record['action_outcome_trace_id']}:{case_name}"
    return copied


def _blocked_flag_values(blocked_flags: dict[str, Any]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])
