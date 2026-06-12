"""Conclude Level 1 sandbox review and precheck future Level 2 readiness."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .level1_sandbox_outcome_evaluation_and_human_review_summary_minimal import (
    STATUS_FAILED,
    STATUS_INCONCLUSIVE,
    STATUS_PASSED,
    TARGET_SCOPE,
    build_level1_sandbox_outcome_evaluation_and_human_review_summary,
    validate_level1_sandbox_outcome_evaluation_and_human_review_summary,
)


COMMAND = "run-level1-sandbox-review-conclusion-and-level2-readiness-precheck-minimal-check"
FLOW = "level1_sandbox_review_conclusion_and_level2_readiness_precheck_minimal_v0"
RECORD_TYPE = "level1_sandbox_review_conclusion_and_level2_readiness_precheck"
SCHEMA_VERSION = "0.1"
SOURCE_RECORD_TYPE = "level1_sandbox_outcome_evaluation_and_human_review_summary"

CONCLUSION_PASSED = "level1_review_concluded_passed"
CONCLUSION_FAILED = "level1_review_concluded_failed"
CONCLUSION_INCONCLUSIVE = "level1_review_concluded_inconclusive"
CONCLUSION_MISSING_EVALUATION = "level1_review_blocked_missing_evaluation"
CONCLUSION_MISSING_SUMMARY = "level1_review_blocked_missing_human_summary"
CONCLUSION_BOUNDARY_VIOLATION = "level1_review_blocked_boundary_violation"
ALLOWED_CONCLUSION_STATUSES = {
    CONCLUSION_PASSED,
    CONCLUSION_FAILED,
    CONCLUSION_INCONCLUSIVE,
    CONCLUSION_MISSING_EVALUATION,
    CONCLUSION_MISSING_SUMMARY,
    CONCLUSION_BOUNDARY_VIOLATION,
}

PRECHECK_READY = "level2_precheck_ready_for_future_design_package"
PRECHECK_MISSING_LEVEL1_PASS = "level2_precheck_not_ready_missing_level1_pass"
PRECHECK_MISSING_REVIEW = "level2_precheck_not_ready_missing_review_conclusion"
PRECHECK_BOUNDARY_GAP = "level2_precheck_not_ready_boundary_gap"
PRECHECK_BLOCKED_FUTURE_PACKAGE = "level2_precheck_blocked_until_future_package"
ALLOWED_PRECHECK_STATUSES = {
    PRECHECK_READY,
    PRECHECK_MISSING_LEVEL1_PASS,
    PRECHECK_MISSING_REVIEW,
    PRECHECK_BOUNDARY_GAP,
    PRECHECK_BLOCKED_FUTURE_PACKAGE,
}

FORBIDDEN_FLAGS = (
    "proof_of_learning_claimed",
    "runtime_behavior_changed",
    "memory_written",
    "retained_jsonl_written",
    "retention_written",
    "predictor_mutated",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "production_promoted",
)
REQUIRED_FALSE_FIELDS = FORBIDDEN_FLAGS + (
    "level2_application_allowed",
    "level2_execution_allowed",
    "task_queue_completed_state_is_approval",
    "passing_tests_are_approval",
    "codex_generated_review_conclusion_is_approval",
    "level2_precheck_is_approval",
)
REQUIRED_FIELDS = (
    "record_type",
    "schema_version",
    "source_records",
    "level1_target_scope",
    "level1_evaluation_status",
    "human_summary_present",
    "human_summary_conservative",
    "proof_of_learning_claimed",
    "runtime_behavior_changed",
    "memory_written",
    "retained_jsonl_written",
    "retention_written",
    "predictor_mutated",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "production_promoted",
    "audit_present",
    "rollback_present",
    "level1_review_conclusion_status",
    "level2_readiness_precheck_status",
    "level2_application_allowed",
    "level2_execution_allowed",
    "future_package_required_for_level2",
    "task_queue_completed_state_is_approval",
    "passing_tests_are_approval",
    "codex_generated_review_conclusion_is_approval",
    "level2_precheck_is_approval",
    "notes",
)


def build_level1_sandbox_review_conclusion_and_level2_readiness_precheck(
    outcome_evaluation_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if outcome_evaluation_record is None:
        outcome_evaluation_record = build_level1_sandbox_outcome_evaluation_and_human_review_summary()

    source_is_dict = isinstance(outcome_evaluation_record, dict)
    source = outcome_evaluation_record if source_is_dict else {}
    validation = (
        validate_level1_sandbox_outcome_evaluation_and_human_review_summary(source)
        if source_is_dict
        else {"valid": False, "error_codes": ["source_evaluation_not_dict"]}
    )
    human_summary = source.get("human_review_summary")
    forbidden_effects = source.get("forbidden_effects") if isinstance(source.get("forbidden_effects"), dict) else {}
    human_summary_present = _human_summary_present(human_summary)
    human_summary_conservative = _human_summary_conservative(human_summary)
    flags = {
        "proof_of_learning_claimed": forbidden_effects.get("proof_of_learning_claimed") is True,
        "runtime_behavior_changed": forbidden_effects.get("runtime_behavior_changed") is True,
        "memory_written": forbidden_effects.get("memory_written") is True,
        "retained_jsonl_written": forbidden_effects.get("retained_jsonl_written") is True,
        "retention_written": forbidden_effects.get("retention_written") is True,
        "predictor_mutated": forbidden_effects.get("predictor_mutated") is True,
        "selected_action_created": forbidden_effects.get("selected_action_created") is True,
        "final_action_created": forbidden_effects.get("final_action_created") is True,
        "direct_command_created": forbidden_effects.get("direct_command_created") is True,
        "production_promoted": source.get("production_promoted") is True
        or forbidden_effects.get("production_behavior_changed") is True,
    }
    target_scope = source.get("target_scope")
    evaluation_status = source.get("evaluation_status")
    audit_present = source.get("audit_record_present") is True
    rollback_present = source.get("rollback_record_present") is True
    base_boundary_clear = (
        source_is_dict
        and validation.get("valid") is True
        and target_scope == TARGET_SCOPE
        and human_summary_conservative
        and all(value is False for value in flags.values())
    )
    passed_boundary_clear = base_boundary_clear and audit_present and rollback_present

    if not source_is_dict or source.get("record_type") != SOURCE_RECORD_TYPE:
        conclusion = CONCLUSION_MISSING_EVALUATION
    elif not human_summary_present:
        conclusion = CONCLUSION_MISSING_SUMMARY
    elif not base_boundary_clear:
        conclusion = CONCLUSION_BOUNDARY_VIOLATION
    elif evaluation_status == STATUS_PASSED and passed_boundary_clear:
        conclusion = CONCLUSION_PASSED
    elif evaluation_status == STATUS_FAILED:
        conclusion = CONCLUSION_FAILED
    elif evaluation_status == STATUS_INCONCLUSIVE:
        conclusion = CONCLUSION_INCONCLUSIVE
    else:
        conclusion = CONCLUSION_MISSING_EVALUATION

    if conclusion == CONCLUSION_PASSED:
        precheck = PRECHECK_READY
    elif conclusion in {CONCLUSION_FAILED, CONCLUSION_INCONCLUSIVE}:
        precheck = PRECHECK_MISSING_LEVEL1_PASS
    elif conclusion in {CONCLUSION_MISSING_EVALUATION, CONCLUSION_MISSING_SUMMARY}:
        precheck = PRECHECK_MISSING_REVIEW
    elif conclusion == CONCLUSION_BOUNDARY_VIOLATION:
        precheck = PRECHECK_BOUNDARY_GAP
    else:
        precheck = PRECHECK_BLOCKED_FUTURE_PACKAGE

    return {
        "record_type": RECORD_TYPE,
        "schema_version": SCHEMA_VERSION,
        "source_records": {
            "outcome_evaluation_record_type": source.get("record_type"),
            "human_review_summary_record_type": human_summary.get("summary_type")
            if isinstance(human_summary, dict)
            else None,
            "source_evaluation_valid": validation.get("valid") is True,
        },
        "source_outcome_evaluation": deepcopy(outcome_evaluation_record) if source_is_dict else None,
        "level1_target_scope": target_scope,
        "level1_evaluation_status": evaluation_status,
        "human_summary_present": human_summary_present,
        "human_summary_conservative": human_summary_conservative,
        **flags,
        "audit_present": audit_present,
        "rollback_present": rollback_present,
        "level1_review_conclusion_status": conclusion,
        "level2_readiness_precheck_status": precheck,
        "level2_application_allowed": False,
        "level2_execution_allowed": False,
        "future_package_required_for_level2": True,
        "task_queue_completed_state_is_approval": False,
        "passing_tests_are_approval": False,
        "codex_generated_review_conclusion_is_approval": False,
        "level2_precheck_is_approval": False,
        "notes": [
            "Level 1 sandbox review conclusion is sandbox-only.",
            "Level 2 readiness precheck allows only a future design/readiness package.",
            "No task queue entry, completed task, passing test, Codex-generated review conclusion, or Level 2 readiness precheck counts as explicit human application approval.",
        ],
    }


def validate_level1_sandbox_review_conclusion_and_level2_readiness_precheck(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing_field:{field}")
    if record.get("record_type") != RECORD_TYPE:
        errors.append("record_type_not_level1_sandbox_review_conclusion_and_level2_readiness_precheck")
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_not_0.1")
    source_records = record.get("source_records")
    if not isinstance(source_records, dict):
        errors.append("source_records_not_dict")
        source_records = {}
    conclusion = record.get("level1_review_conclusion_status")
    precheck = record.get("level2_readiness_precheck_status")
    if conclusion not in ALLOWED_CONCLUSION_STATUSES:
        errors.append("unknown_level1_review_conclusion_status")
    if precheck not in ALLOWED_PRECHECK_STATUSES:
        errors.append("unknown_level2_readiness_precheck_status")
    for field in REQUIRED_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if record.get("future_package_required_for_level2") is not True:
        errors.append("future_package_required_for_level2_not_true")
    if not isinstance(record.get("notes"), list) or not record.get("notes"):
        errors.append("notes_empty_or_not_list")

    base_boundary_clear = _base_boundary_clear(record)
    passed_boundary_clear = _passed_boundary_clear(record)
    if conclusion == CONCLUSION_PASSED:
        if record.get("level1_target_scope") != TARGET_SCOPE:
            errors.append("passed_level1_target_scope_not_phase0_level1_sandbox_only")
        if record.get("level1_evaluation_status") != STATUS_PASSED:
            errors.append("passed_level1_evaluation_status_not_passed_expected_sandbox_outcome")
        if source_records.get("outcome_evaluation_record_type") != SOURCE_RECORD_TYPE:
            errors.append("passed_source_outcome_evaluation_record_type_wrong")
        if source_records.get("source_evaluation_valid") is not True:
            errors.append("passed_source_evaluation_valid_not_true")
        if not passed_boundary_clear:
            errors.append("passed_boundary_not_clear")
        if precheck != PRECHECK_READY:
            errors.append("passed_precheck_not_ready_for_future_design_package")
    elif conclusion in {CONCLUSION_FAILED, CONCLUSION_INCONCLUSIVE}:
        if record.get("level1_evaluation_status") == STATUS_PASSED:
            errors.append("nonpassed_conclusion_has_passed_evaluation")
        if not base_boundary_clear:
            errors.append("nonpassed_conclusion_boundary_not_clear")
        if precheck != PRECHECK_MISSING_LEVEL1_PASS:
            errors.append("nonpassed_precheck_not_missing_level1_pass")
    elif conclusion == CONCLUSION_MISSING_EVALUATION:
        if source_records.get("outcome_evaluation_record_type") == SOURCE_RECORD_TYPE:
            errors.append("missing_evaluation_has_source_record_type")
        if precheck != PRECHECK_MISSING_REVIEW:
            errors.append("missing_evaluation_precheck_not_missing_review")
    elif conclusion == CONCLUSION_MISSING_SUMMARY:
        if record.get("human_summary_present") is not False:
            errors.append("missing_summary_human_summary_present_not_false")
        if precheck != PRECHECK_MISSING_REVIEW:
            errors.append("missing_summary_precheck_not_missing_review")
    elif conclusion == CONCLUSION_BOUNDARY_VIOLATION:
        if base_boundary_clear:
            errors.append("boundary_violation_boundary_clear")
        if precheck != PRECHECK_BOUNDARY_GAP:
            errors.append("boundary_violation_precheck_not_boundary_gap")

    return {
        "valid": not errors,
        "error_codes": errors,
        "level1_review_conclusion_status": conclusion,
        "level2_readiness_precheck_status": precheck,
        "level1_review_concluded_passed": conclusion == CONCLUSION_PASSED,
        "level2_precheck_ready_for_future_design_package": precheck == PRECHECK_READY,
        "level2_application_allowed": record.get("level2_application_allowed") is True,
        "level2_execution_allowed": record.get("level2_execution_allowed") is True,
        "proof_of_learning_claimed": record.get("proof_of_learning_claimed") is True,
        "runtime_behavior_changed": record.get("runtime_behavior_changed") is True,
        "memory_written": record.get("memory_written") is True,
        "predictor_mutated": record.get("predictor_mutated") is True,
        "production_promoted": record.get("production_promoted") is True,
        "task_queue_not_approval": (
            record.get("task_queue_completed_state_is_approval") is False
            and record.get("passing_tests_are_approval") is False
            and record.get("codex_generated_review_conclusion_is_approval") is False
            and record.get("level2_precheck_is_approval") is False
        ),
    }


def run_level1_sandbox_review_conclusion_and_level2_readiness_precheck_minimal_check() -> dict[str, Any]:
    records = _demo_records()
    validation_results = [
        validate_level1_sandbox_review_conclusion_and_level2_readiness_precheck(record) for record in records
    ]
    valid_results = [result for result in validation_results if result.get("valid")]
    invalid_results = [result for result in validation_results if not result.get("valid")]
    summary = {
        "level1_review_conclusion_result_count": len(records),
        "valid_level1_review_conclusion_count": sum(
            1 for result in valid_results if result.get("level1_review_concluded_passed") is True
        ),
        "valid_record_count": len(valid_results),
        "invalid_level1_review_conclusion_count": len(invalid_results),
        "level2_precheck_ready_count": sum(
            1 for result in valid_results if result.get("level2_precheck_ready_for_future_design_package") is True
        ),
        "level2_application_allowed_count": sum(
            1 for result in valid_results if result.get("level2_application_allowed") is True
        ),
        "level2_execution_allowed_count": sum(
            1 for result in valid_results if result.get("level2_execution_allowed") is True
        ),
        "proof_of_learning_claim_count": sum(
            1 for result in valid_results if result.get("proof_of_learning_claimed") is True
        ),
        "runtime_behavior_change_count": sum(
            1 for result in valid_results if result.get("runtime_behavior_changed") is True
        ),
        "memory_write_count": sum(1 for result in valid_results if result.get("memory_written") is True),
        "predictor_mutation_count": sum(1 for result in valid_results if result.get("predictor_mutated") is True),
        "production_promotion_count": sum(1 for result in valid_results if result.get("production_promoted") is True),
        "task_queue_not_approval_count": sum(
            1 for result in valid_results if result.get("task_queue_not_approval") is True
        ),
    }
    summary["all_level1_sandbox_review_conclusion_and_level2_precheck_checks_passed"] = (
        summary["valid_level1_review_conclusion_count"] == 1
        and summary["valid_record_count"] >= 3
        and summary["invalid_level1_review_conclusion_count"] >= 1
        and summary["level2_precheck_ready_count"] == 1
        and summary["level2_application_allowed_count"] == 0
        and summary["level2_execution_allowed_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
        and summary["runtime_behavior_change_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["predictor_mutation_count"] == 0
        and summary["production_promotion_count"] == 0
        and summary["task_queue_not_approval_count"] == len(valid_results)
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok"
        if summary["all_level1_sandbox_review_conclusion_and_level2_precheck_checks_passed"]
        else "failed",
        "review_conclusion_results": records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "level1_review_conclusion_only": True,
            "level2_readiness_precheck_only": True,
            "level2_application_allowed": False,
            "level2_execution_allowed": False,
            "future_package_required_for_level2": True,
            "task_queue_counts_as_approval": False,
            "passing_tests_count_as_approval": False,
            "codex_generated_review_conclusion_counts_as_approval": False,
            "level2_precheck_counts_as_approval": False,
            "runtime_behavior_changed": False,
            "memory_write": False,
            "retained_jsonl_write": False,
            "retention_write": False,
            "predictor_mutation": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "production_promoted": False,
            "proof_of_learning_claimed": False,
        },
    }


def _demo_records() -> list[dict[str, Any]]:
    passed = build_level1_sandbox_review_conclusion_and_level2_readiness_precheck()
    failed_source = build_level1_sandbox_outcome_evaluation_and_human_review_summary(
        _source_observation_with("observed_front_symbol", ".")
    )
    failed = build_level1_sandbox_review_conclusion_and_level2_readiness_precheck(failed_source)
    inconclusive = build_level1_sandbox_review_conclusion_and_level2_readiness_precheck(
        build_level1_sandbox_outcome_evaluation_and_human_review_summary({})
    )
    missing_summary_source = build_level1_sandbox_outcome_evaluation_and_human_review_summary()
    missing_summary_source.pop("human_review_summary", None)
    missing_summary = build_level1_sandbox_review_conclusion_and_level2_readiness_precheck(missing_summary_source)
    invalid = [
        _mutated(failed, ["level1_review_conclusion_status"], CONCLUSION_PASSED),
        _mutated(inconclusive, ["level1_review_conclusion_status"], CONCLUSION_PASSED),
        _mutated(passed, ["level2_application_allowed"], True),
        _mutated(passed, ["level2_execution_allowed"], True),
        _mutated(passed, ["future_package_required_for_level2"], False),
        _mutated(passed, ["task_queue_completed_state_is_approval"], True),
        _mutated(passed, ["passing_tests_are_approval"], True),
        _mutated(passed, ["codex_generated_review_conclusion_is_approval"], True),
        _mutated(passed, ["level2_precheck_is_approval"], True),
    ]
    for flag in FORBIDDEN_FLAGS:
        invalid.append(_mutated(passed, [flag], True))
    return [passed, failed, inconclusive, missing_summary] + invalid


def _source_observation_with(field: str, value: Any) -> dict[str, Any]:
    evaluation = build_level1_sandbox_outcome_evaluation_and_human_review_summary()
    source = deepcopy(evaluation["source_observation"])
    source[field] = value
    return source


def _human_summary_present(summary: Any) -> bool:
    return isinstance(summary, dict) and bool(summary.get("plain_language_result")) and bool(summary.get("safe_claim"))


def _human_summary_conservative(summary: Any) -> bool:
    if not isinstance(summary, dict):
        return False
    return (
        summary.get("not_proof_of_learning") is True
        and summary.get("not_runtime_behavior_change") is True
        and summary.get("not_memory_write") is True
        and summary.get("not_predictor_mutation") is True
        and summary.get("not_production_promotion") is True
        and "learned the lesson" not in repr(summary)
        and "proof of learning" not in repr(summary).lower()
    )


def _base_boundary_clear(record: dict[str, Any]) -> bool:
    return (
        record.get("level1_target_scope") == TARGET_SCOPE
        and record.get("human_summary_present") is True
        and record.get("human_summary_conservative") is True
        and all(record.get(flag) is False for flag in FORBIDDEN_FLAGS)
    )


def _passed_boundary_clear(record: dict[str, Any]) -> bool:
    return (
        _base_boundary_clear(record)
        and record.get("audit_present") is True
        and record.get("rollback_present") is True
    )


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
            run_level1_sandbox_review_conclusion_and_level2_readiness_precheck_minimal_check(),
            ensure_ascii=False,
            indent=2,
        )
    )
