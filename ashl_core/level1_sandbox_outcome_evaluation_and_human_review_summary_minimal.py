"""Evaluate a Level 1 sandbox outcome observation for human review."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .level1_sandbox_lesson_application_outcome_observation_minimal import (
    build_level1_sandbox_lesson_application_outcome_observation,
    check_level1_sandbox_lesson_application_outcome_observation,
)


COMMAND = "run-level1-sandbox-outcome-evaluation-and-human-review-summary-minimal-check"
FLOW = "level1_sandbox_outcome_evaluation_and_human_review_summary_minimal_v0"
RECORD_TYPE = "level1_sandbox_outcome_evaluation_and_human_review_summary"
SCHEMA_VERSION = "level1_sandbox_outcome_evaluation_and_human_review_summary_minimal_v0"
TARGET_SCOPE = "phase0_level1_sandbox_only"
SOURCE_RECORD_TYPE = "level1_sandbox_lesson_application_outcome_observation"

STATUS_PASSED = "passed_expected_sandbox_outcome"
STATUS_FAILED = "failed_expected_sandbox_outcome"
STATUS_INCONCLUSIVE = "inconclusive_missing_or_invalid_observation"
ALLOWED_EVALUATION_STATUSES = {STATUS_PASSED, STATUS_FAILED, STATUS_INCONCLUSIVE}

EXPECTED_FRONT_SYMBOL = "d"
EXPECTED_SANDBOX_ACTION = "check_before_retry"
SAFE_CLAIM = (
    "ASHL Core can evaluate a Phase0 Level 1 sandbox-only lesson application outcome "
    "and summarize the result for human review."
)
PASS_RESULT = "The Phase0 Level 1 sandbox-only outcome matched the expected sandbox behavior."

FORBIDDEN_EFFECTS = (
    "production_behavior_changed",
    "runtime_behavior_changed",
    "memory_written",
    "retention_written",
    "retained_jsonl_written",
    "predictor_mutated",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "proof_of_learning_claimed",
)
FORBIDDEN_SUMMARY_WORDING = (
    "ASHL Core learned the lesson.",
    "The model learned.",
    "Runtime behavior changed.",
    "Memory was updated.",
    "The predictor was improved.",
    "The lesson is ready for production.",
    "The system can now choose actions from this lesson.",
)
REQUIRED_HUMAN_SUMMARY_FIELDS = (
    "summary_type",
    "plain_language_result",
    "safe_claim",
    "not_proof_of_learning",
    "not_runtime_behavior_change",
    "not_memory_write",
    "not_predictor_mutation",
    "not_production_promotion",
)
TASK_QUEUE_NOTE_FALSE_FIELDS = (
    "task_queue_entry_is_approval",
    "completed_task_is_approval",
    "passing_tests_are_approval",
    "codex_generated_status_is_approval",
)
REQUIRED_FIELDS = (
    "record_type",
    "schema_version",
    "target_scope",
    "source_observation",
    "source_observation_record_type",
    "source_observation_target_scope",
    "source_observation_validation_valid",
    "observation_valid",
    "evaluation_status",
    "expected_front_symbol",
    "observed_front_symbol",
    "expected_sandbox_action",
    "observed_sandbox_action",
    "expected_blocks_retry_same_action_until_check",
    "observed_blocks_retry_same_action_until_check",
    "audit_record_present",
    "rollback_record_present",
    "human_review_summary",
    "forbidden_effects",
    "task_queue_note",
)


def build_level1_sandbox_outcome_evaluation_and_human_review_summary(
    observation_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic human-review evaluation from a Level 1 observation."""
    if observation_record is None:
        observation_record = build_level1_sandbox_lesson_application_outcome_observation()

    source_is_dict = isinstance(observation_record, dict)
    source_missing = not source_is_dict or not observation_record
    source = observation_record if source_is_dict else {}
    source_validation = (
        check_level1_sandbox_lesson_application_outcome_observation(source)
        if source_is_dict
        else {"valid": False, "error_codes": ["source_observation_not_dict"]}
    )
    observed_front_symbol = source.get("observed_front_symbol")
    observed_action = source.get("observed_sandbox_action")
    observed_block = source.get("observed_blocks_retry_same_action_until_check")
    audit_present = source.get("audit_record_present")
    rollback_present = source.get("rollback_record_present")
    source_record_type = source.get("record_type")
    source_scope = source.get("target_scope")
    forbidden_effects = _forbidden_effects_from_observation(source)
    source_usable = (
        not source_missing
        and source_is_dict
        and source_record_type == SOURCE_RECORD_TYPE
        and source_scope == TARGET_SCOPE
        and source.get("outcome_observed") is True
    )
    expected_behavior_matches = (
        observed_front_symbol == EXPECTED_FRONT_SYMBOL
        and observed_action == EXPECTED_SANDBOX_ACTION
        and observed_block is True
        and audit_present is True
        and rollback_present is True
        and all(value is False for value in forbidden_effects.values())
    )
    if not source_usable:
        evaluation_status = STATUS_INCONCLUSIVE
    elif expected_behavior_matches and source_validation.get("valid") is True:
        evaluation_status = STATUS_PASSED
    else:
        evaluation_status = STATUS_FAILED

    return {
        "record_type": RECORD_TYPE,
        "schema_version": SCHEMA_VERSION,
        "target_scope": TARGET_SCOPE,
        "source_observation": deepcopy(observation_record) if source_is_dict else None,
        "source_observation_record_type": source_record_type,
        "source_observation_target_scope": source_scope,
        "source_observation_validation_valid": source_validation.get("valid") is True,
        "observation_valid": source_validation.get("valid") is True,
        "evaluation_status": evaluation_status,
        "expected_front_symbol": EXPECTED_FRONT_SYMBOL,
        "observed_front_symbol": observed_front_symbol,
        "expected_sandbox_action": EXPECTED_SANDBOX_ACTION,
        "observed_sandbox_action": observed_action,
        "expected_blocks_retry_same_action_until_check": True,
        "observed_blocks_retry_same_action_until_check": observed_block is True,
        "audit_record_present": audit_present is True,
        "rollback_record_present": rollback_present is True,
        "human_review_summary": _human_review_summary(evaluation_status),
        "forbidden_effects": forbidden_effects,
        "task_queue_note": {
            "task_queue_entry_is_approval": False,
            "completed_task_is_approval": False,
            "passing_tests_are_approval": False,
            "codex_generated_status_is_approval": False,
        },
    }


def validate_level1_sandbox_outcome_evaluation_and_human_review_summary(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing_field:{field}")
    if record.get("record_type") != RECORD_TYPE:
        errors.append("record_type_not_level1_sandbox_outcome_evaluation_and_human_review_summary")
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_not_level1_sandbox_outcome_evaluation_and_human_review_summary_minimal_v0")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_phase0_level1_sandbox_only")

    status = record.get("evaluation_status")
    if status not in ALLOWED_EVALUATION_STATUSES:
        errors.append("evaluation_status_unknown")

    source_usable = _source_is_usable(record)
    behavior_matches = _expected_behavior_matches(record)
    forbidden_effects_blocked = _forbidden_effects_blocked(record)
    if status == STATUS_PASSED:
        if record.get("observation_valid") is not True:
            errors.append("passed_observation_valid_not_true")
        if not source_usable:
            errors.append("passed_source_not_usable")
        if not behavior_matches:
            errors.append("passed_expected_behavior_not_matched")
        if not forbidden_effects_blocked:
            errors.append("passed_forbidden_effects_not_blocked")
    elif status == STATUS_FAILED:
        if not source_usable:
            errors.append("failed_source_not_usable")
        if behavior_matches:
            errors.append("failed_expected_behavior_matched")
        if not forbidden_effects_blocked:
            errors.append("failed_forbidden_effects_not_blocked")
    elif status == STATUS_INCONCLUSIVE:
        if source_usable and behavior_matches and record.get("observation_valid") is True:
            errors.append("inconclusive_source_is_valid_and_matched")
        if not forbidden_effects_blocked:
            errors.append("inconclusive_forbidden_effects_not_blocked")

    if record.get("expected_front_symbol") != EXPECTED_FRONT_SYMBOL:
        errors.append("expected_front_symbol_not_d")
    if record.get("expected_sandbox_action") != EXPECTED_SANDBOX_ACTION:
        errors.append("expected_sandbox_action_not_check_before_retry")
    if record.get("expected_blocks_retry_same_action_until_check") is not True:
        errors.append("expected_blocks_retry_same_action_until_check_not_true")

    _validate_human_summary(record.get("human_review_summary"), errors)
    _validate_task_queue_note(record.get("task_queue_note"), errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "evaluation_status": status,
        "passed_expected_sandbox_outcome": status == STATUS_PASSED,
        "failed_expected_sandbox_outcome": status == STATUS_FAILED,
        "inconclusive_missing_or_invalid_observation": status == STATUS_INCONCLUSIVE,
        "human_review_summary_present": _human_summary_present(record.get("human_review_summary")),
        "forbidden_effects_blocked": forbidden_effects_blocked,
        "task_queue_not_approval": _task_queue_note_blocked(record.get("task_queue_note")),
    }


def run_level1_sandbox_outcome_evaluation_and_human_review_summary_minimal_check() -> dict[str, Any]:
    records = _demo_records()
    validation_results = [
        validate_level1_sandbox_outcome_evaluation_and_human_review_summary(record) for record in records
    ]
    valid_results = [result for result in validation_results if result.get("valid")]
    summary = {
        "level1_sandbox_outcome_evaluation_result_count": len(records),
        "valid_evaluation_count": len(valid_results),
        "invalid_evaluation_count": len(records) - len(valid_results),
        "passed_expected_sandbox_outcome_count": sum(
            1 for result in valid_results if result.get("passed_expected_sandbox_outcome") is True
        ),
        "failed_expected_sandbox_outcome_count": sum(
            1 for result in valid_results if result.get("failed_expected_sandbox_outcome") is True
        ),
        "inconclusive_missing_or_invalid_observation_count": sum(
            1 for result in valid_results if result.get("inconclusive_missing_or_invalid_observation") is True
        ),
        "human_review_summary_count": sum(
            1 for result in valid_results if result.get("human_review_summary_present") is True
        ),
        "forbidden_effects_blocked_count": sum(
            1 for result in valid_results if result.get("forbidden_effects_blocked") is True
        ),
        "task_queue_not_approval_count": sum(
            1 for result in valid_results if result.get("task_queue_not_approval") is True
        ),
    }
    summary["all_level1_sandbox_outcome_evaluation_checks_passed"] = (
        summary["valid_evaluation_count"] == 4
        and summary["invalid_evaluation_count"] >= 1
        and summary["passed_expected_sandbox_outcome_count"] == 1
        and summary["failed_expected_sandbox_outcome_count"] == 2
        and summary["inconclusive_missing_or_invalid_observation_count"] == 1
        and summary["human_review_summary_count"] == 4
        and summary["forbidden_effects_blocked_count"] == 4
        and summary["task_queue_not_approval_count"] == 4
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_level1_sandbox_outcome_evaluation_checks_passed"] else "failed",
        "evaluation_records": records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "evaluation_only": True,
            "human_review_summary_only": True,
            "task_queue_counts_as_approval": False,
            "passing_tests_count_as_approval": False,
            "codex_generated_status_counts_as_approval": False,
            "lesson_applied": False,
            "runtime_behavior_changed": False,
            "memory_write": False,
            "retention_write": False,
            "retained_jsonl_write": False,
            "predictor_mutation": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "proof_of_learning_claimed": False,
        },
    }


def _demo_records() -> list[dict[str, Any]]:
    valid = build_level1_sandbox_outcome_evaluation_and_human_review_summary()
    source = build_level1_sandbox_lesson_application_outcome_observation()
    missing = build_level1_sandbox_outcome_evaluation_and_human_review_summary({})
    wrong_front = build_level1_sandbox_outcome_evaluation_and_human_review_summary(
        _mutated(source, ["observed_front_symbol"], ".")
    )
    wrong_action = build_level1_sandbox_outcome_evaluation_and_human_review_summary(
        _mutated(source, ["observed_sandbox_action"], "retry_same_action")
    )
    invalid = [
        _mutated(valid, ["evaluation_status"], "unknown"),
        _mutated(valid, ["target_scope"], "production"),
        _mutated(valid, ["source_observation_record_type"], "wrong"),
        _mutated(valid, ["source_observation_target_scope"], "production"),
        _mutated(valid, ["evaluation_status"], STATUS_FAILED),
        _mutated(wrong_front, ["evaluation_status"], STATUS_PASSED),
        _mutated(missing, ["evaluation_status"], STATUS_PASSED),
        _mutated(valid, ["audit_record_present"], False),
        _mutated(valid, ["rollback_record_present"], False),
        _mutated(valid, ["human_review_summary", "safe_claim"], "ASHL Core learned the lesson."),
        _mutated(valid, ["human_review_summary", "plain_language_result"], ""),
        _mutated(valid, ["task_queue_note", "task_queue_entry_is_approval"], True),
        _mutated(valid, ["task_queue_note", "completed_task_is_approval"], True),
        _mutated(valid, ["task_queue_note", "passing_tests_are_approval"], True),
        _mutated(valid, ["task_queue_note", "codex_generated_status_is_approval"], True),
    ]
    for flag in FORBIDDEN_EFFECTS:
        invalid.append(_mutated(valid, ["forbidden_effects", flag], True))
    return [valid, missing, wrong_front, wrong_action] + invalid


def _human_review_summary(status: str) -> dict[str, Any]:
    if status == STATUS_PASSED:
        plain = PASS_RESULT
    elif status == STATUS_FAILED:
        plain = "The Phase0 Level 1 sandbox-only outcome did not match the expected sandbox behavior."
    else:
        plain = "The Phase0 Level 1 sandbox-only outcome could not be evaluated from the available observation."
    return {
        "summary_type": "phase0_level1_sandbox_outcome_review",
        "plain_language_result": plain,
        "safe_claim": SAFE_CLAIM,
        "not_proof_of_learning": True,
        "not_runtime_behavior_change": True,
        "not_memory_write": True,
        "not_predictor_mutation": True,
        "not_production_promotion": True,
    }


def _forbidden_effects_from_observation(source: dict[str, Any]) -> dict[str, bool]:
    return {
        "production_behavior_changed": source.get("production_behavior_changed") is True,
        "runtime_behavior_changed": source.get("runtime_behavior_changed") is True,
        "memory_written": source.get("memory_written") is True,
        "retention_written": source.get("retention_written") is True,
        "retained_jsonl_written": source.get("retained_jsonl_written") is True,
        "predictor_mutated": source.get("predictor_mutated") is True or source.get("predictor_modified") is True,
        "selected_action_created": source.get("selected_action_created") is True,
        "final_action_created": source.get("final_action_created") is True,
        "direct_command_created": source.get("direct_command_created") is True,
        "proof_of_learning_claimed": source.get("proof_of_learning_claimed") is True,
    }


def _source_is_usable(record: dict[str, Any]) -> bool:
    return (
        record.get("source_observation_record_type") == SOURCE_RECORD_TYPE
        and record.get("source_observation_target_scope") == TARGET_SCOPE
        and isinstance(record.get("source_observation"), dict)
    )


def _expected_behavior_matches(record: dict[str, Any]) -> bool:
    return (
        record.get("observed_front_symbol") == EXPECTED_FRONT_SYMBOL
        and record.get("observed_sandbox_action") == EXPECTED_SANDBOX_ACTION
        and record.get("observed_blocks_retry_same_action_until_check") is True
        and record.get("audit_record_present") is True
        and record.get("rollback_record_present") is True
    )


def _forbidden_effects_blocked(record: dict[str, Any]) -> bool:
    forbidden_effects = record.get("forbidden_effects")
    if not isinstance(forbidden_effects, dict):
        return False
    return all(forbidden_effects.get(flag) is False for flag in FORBIDDEN_EFFECTS)


def _validate_human_summary(summary: Any, errors: list[str]) -> None:
    if not isinstance(summary, dict):
        errors.append("human_review_summary_not_dict")
        return
    for field in REQUIRED_HUMAN_SUMMARY_FIELDS:
        if field not in summary:
            errors.append(f"human_review_summary_missing:{field}")
    if summary.get("summary_type") != "phase0_level1_sandbox_outcome_review":
        errors.append("human_review_summary_type_not_phase0_level1_sandbox_outcome_review")
    for field in ("plain_language_result", "safe_claim"):
        value = summary.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"human_review_summary_{field}_empty")
    if summary.get("safe_claim") != SAFE_CLAIM:
        errors.append("human_review_summary_safe_claim_not_allowed")
    for field in (
        "not_proof_of_learning",
        "not_runtime_behavior_change",
        "not_memory_write",
        "not_predictor_mutation",
        "not_production_promotion",
    ):
        if summary.get(field) is not True:
            errors.append(f"human_review_summary_{field}_not_true")
    text = repr(summary)
    for wording in FORBIDDEN_SUMMARY_WORDING:
        if wording in text:
            errors.append(f"forbidden_human_summary_wording:{wording}")


def _human_summary_present(summary: Any) -> bool:
    return (
        isinstance(summary, dict)
        and summary.get("summary_type") == "phase0_level1_sandbox_outcome_review"
        and isinstance(summary.get("plain_language_result"), str)
        and bool(summary.get("plain_language_result").strip())
        and summary.get("safe_claim") == SAFE_CLAIM
    )


def _validate_task_queue_note(note: Any, errors: list[str]) -> None:
    if not isinstance(note, dict):
        errors.append("task_queue_note_not_dict")
        return
    for field in TASK_QUEUE_NOTE_FALSE_FIELDS:
        if note.get(field) is not False:
            errors.append(f"task_queue_note_{field}_not_false")


def _task_queue_note_blocked(note: Any) -> bool:
    return isinstance(note, dict) and all(note.get(field) is False for field in TASK_QUEUE_NOTE_FALSE_FIELDS)


def _mutated(record: dict[str, Any], path: list[str], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: dict[str, Any] = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(
        json.dumps(
            run_level1_sandbox_outcome_evaluation_and_human_review_summary_minimal_check(),
            ensure_ascii=False,
            indent=2,
        )
    )
