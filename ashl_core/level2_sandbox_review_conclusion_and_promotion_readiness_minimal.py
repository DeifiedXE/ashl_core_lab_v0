"""Conclude the Level 2 sandbox review and record future design readiness."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .level2_sandbox_application_observation_evaluation_summary_minimal import (
    EVALUATION_INCONCLUSIVE,
    EVALUATION_PASSED,
    SAFE_CLAIM as LEVEL2_APPLICATION_SAFE_CLAIM,
    TARGET_SCOPE,
    build_level2_sandbox_application_evaluation_record,
    build_level2_sandbox_application_human_review_summary,
    build_level2_sandbox_application_observation_record,
    build_level2_sandbox_application_record,
    run_level2_sandbox_application_observation_evaluation_summary_minimal_check,
    validate_level2_sandbox_application_evaluation_record,
    validate_level2_sandbox_application_human_review_summary,
    validate_level2_sandbox_application_observation_record,
    validate_level2_sandbox_application_record,
)


COMMAND = "run-level2-sandbox-review-conclusion-and-promotion-readiness-minimal-check"
FLOW = "level2_sandbox_review_conclusion_and_promotion_readiness_minimal_v0"

CONCLUSION_RECORD_TYPE = "level2_sandbox_review_conclusion"
READINESS_RECORD_TYPE = "phase0_future_promotion_readiness"
SOURCE_CLOSED_LOOP_RECORD_TYPE = "level2_sandbox_application_observation_evaluation_summary"

CONCLUSION_PASSED = "concluded_level2_sandbox_review_passed"
CONCLUSION_FAILED = "concluded_level2_sandbox_review_failed"
CONCLUSION_INCONCLUSIVE = "concluded_level2_sandbox_review_inconclusive"
READINESS_READY = "ready_for_future_higher_level_design_package_only"
READINESS_FAILED = "not_ready_failed_level2_sandbox_review"
READINESS_INCONCLUSIVE = "not_ready_inconclusive_level2_sandbox_review"
READINESS_MISSING = "not_ready_missing_required_level2_closed_loop_inputs"

SAFE_CLAIM = (
    "ASHL Core can conclude a Phase0 Level 2 sandbox-only review and record conservative readiness "
    "for a future higher-level design package, while runtime behavior, memory, retained JSONL, "
    "retention, predictor mutation, action selection, production promotion, and proof-of-learning remain blocked."
)
FALSE_FIELDS = (
    "proof_of_learning_claimed",
    "runtime_behavior_changed",
    "memory_written",
    "retained_jsonl_written",
    "retention_written",
    "predictor_mutated",
    "selected_action_created",
    "final_action_created",
    "production_promotion_claimed",
)
READINESS_FALSE_FIELDS = (
    "ready_for_runtime_behavior_change",
    "ready_for_memory_write",
    "ready_for_retained_jsonl_write",
    "ready_for_predictor_mutation",
    "ready_for_production_promotion",
    "ready_for_selected_action",
    "ready_for_final_action",
    "promotion_performed",
    "proof_of_learning_claimed",
)


def build_level2_sandbox_review_conclusion(
    closed_loop_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if closed_loop_result is None:
        closed_loop_result = run_level2_sandbox_application_observation_evaluation_summary_minimal_check()

    application, observation, evaluation, human_review = _extract_closed_loop_records(closed_loop_result)
    app_valid = validate_level2_sandbox_application_record(application).get("valid") is True
    obs_valid = validate_level2_sandbox_application_observation_record(observation).get("valid") is True
    eval_validation = validate_level2_sandbox_application_evaluation_record(evaluation)
    eval_valid = eval_validation.get("valid") is True
    summary_valid = validate_level2_sandbox_application_human_review_summary(human_review).get("valid") is True
    evaluation_status = evaluation.get("evaluation_status")
    audit_present = application.get("audit_recorded") is True and observation.get("audit_still_present") is True
    rollback_present = (
        application.get("rollback_available") is True and observation.get("rollback_still_available") is True
    )
    no_forbidden = _source_forbidden_flags_clear(application, observation, evaluation, human_review)
    conservative_summary = _human_review_summary_is_conservative(human_review)
    if not (app_valid and obs_valid and eval_valid and summary_valid and audit_present and rollback_present):
        status = CONCLUSION_INCONCLUSIVE
    elif evaluation_status == EVALUATION_PASSED and no_forbidden and conservative_summary:
        status = CONCLUSION_PASSED
    elif evaluation_status == EVALUATION_INCONCLUSIVE:
        status = CONCLUSION_INCONCLUSIVE
    else:
        status = CONCLUSION_FAILED

    return {
        "record_type": CONCLUSION_RECORD_TYPE,
        "target_scope": TARGET_SCOPE,
        "source_closed_loop_record_type": SOURCE_CLOSED_LOOP_RECORD_TYPE,
        "level2_application_valid": app_valid,
        "level2_observation_valid": obs_valid,
        "level2_evaluation_status": evaluation_status,
        "human_review_summary_present": summary_valid,
        "audit_present": audit_present,
        "rollback_present": rollback_present,
        "review_conclusion_status": status,
        "review_conclusion_reason": _conclusion_reason(status),
        "source_human_review_conservative": conservative_summary,
        "proof_of_learning_claimed": False,
        "runtime_behavior_changed": False,
        "memory_written": False,
        "retained_jsonl_written": False,
        "retention_written": False,
        "predictor_mutated": False,
        "selected_action_created": False,
        "final_action_created": False,
        "production_promotion_claimed": False,
        "source_application_record": deepcopy(application),
        "source_observation_record": deepcopy(observation),
        "source_evaluation_record": deepcopy(evaluation),
        "source_human_review_summary_record": deepcopy(human_review),
    }


def validate_level2_sandbox_review_conclusion(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    status = record.get("review_conclusion_status")
    if record.get("record_type") != CONCLUSION_RECORD_TYPE:
        errors.append("record_type_not_level2_sandbox_review_conclusion")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_phase0_level2_sandbox_only")
    if record.get("source_closed_loop_record_type") != SOURCE_CLOSED_LOOP_RECORD_TYPE:
        errors.append("source_closed_loop_record_type_not_expected")
    if status not in {CONCLUSION_PASSED, CONCLUSION_FAILED, CONCLUSION_INCONCLUSIVE}:
        errors.append("review_conclusion_status_unknown")
    if status == CONCLUSION_PASSED:
        for field in (
            "level2_application_valid",
            "level2_observation_valid",
            "human_review_summary_present",
            "audit_present",
            "rollback_present",
            "source_human_review_conservative",
        ):
            if record.get(field) is not True:
                errors.append(f"{field}_not_true")
        if record.get("level2_evaluation_status") != EVALUATION_PASSED:
            errors.append("passed_conclusion_without_passed_evaluation")
    if not isinstance(record.get("review_conclusion_reason"), str) or not record.get(
        "review_conclusion_reason", ""
    ).strip():
        errors.append("review_conclusion_reason_empty")
    if _contains_proof_language(record.get("review_conclusion_reason", "")):
        errors.append("review_conclusion_reason_contains_proof_language")
    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {"valid": not errors, "error_codes": errors, "review_conclusion_status": status}


def build_phase0_future_promotion_readiness(
    review_conclusion: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if review_conclusion is None:
        review_conclusion = build_level2_sandbox_review_conclusion()
    conclusion_valid = validate_level2_sandbox_review_conclusion(review_conclusion).get("valid") is True
    conclusion_status = review_conclusion.get("review_conclusion_status")
    if conclusion_valid and conclusion_status == CONCLUSION_PASSED:
        readiness_status = READINESS_READY
        ready_for_design = True
    elif conclusion_valid and conclusion_status == CONCLUSION_FAILED:
        readiness_status = READINESS_FAILED
        ready_for_design = False
    elif conclusion_valid and conclusion_status == CONCLUSION_INCONCLUSIVE:
        readiness_status = READINESS_INCONCLUSIVE
        ready_for_design = False
    else:
        readiness_status = READINESS_MISSING
        ready_for_design = False
    return {
        "record_type": READINESS_RECORD_TYPE,
        "readiness_scope": "future_design_package_only",
        "readiness_status": readiness_status,
        "source_review_conclusion_status": conclusion_status,
        "source_review_conclusion_valid": conclusion_valid,
        "ready_for_future_higher_level_design_package": ready_for_design,
        "ready_for_runtime_behavior_change": False,
        "ready_for_memory_write": False,
        "ready_for_retained_jsonl_write": False,
        "ready_for_predictor_mutation": False,
        "ready_for_production_promotion": False,
        "ready_for_selected_action": False,
        "ready_for_final_action": False,
        "promotion_performed": False,
        "next_allowed_package_kind": "future_design_package_only",
        "human_review_required_for_any_future_boundary_change": True,
        "explicit_user_approval_required_for_any_future_application": True,
        "proof_of_learning_claimed": False,
        "source_review_conclusion": deepcopy(review_conclusion),
    }


def validate_phase0_future_promotion_readiness(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    status = record.get("readiness_status")
    if record.get("record_type") != READINESS_RECORD_TYPE:
        errors.append("record_type_not_phase0_future_promotion_readiness")
    if record.get("readiness_scope") != "future_design_package_only":
        errors.append("readiness_scope_not_future_design_package_only")
    if status not in {READINESS_READY, READINESS_FAILED, READINESS_INCONCLUSIVE, READINESS_MISSING}:
        errors.append("readiness_status_unknown")
    if status == READINESS_READY:
        if record.get("source_review_conclusion_status") != CONCLUSION_PASSED:
            errors.append("ready_without_passed_review_conclusion")
        if record.get("ready_for_future_higher_level_design_package") is not True:
            errors.append("ready_for_future_higher_level_design_package_not_true")
    else:
        if record.get("ready_for_future_higher_level_design_package") is not False:
            errors.append("not_ready_but_future_design_ready_true")
    if record.get("next_allowed_package_kind") != "future_design_package_only":
        errors.append("next_allowed_package_kind_not_future_design_package_only")
    for field in READINESS_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in (
        "human_review_required_for_any_future_boundary_change",
        "explicit_user_approval_required_for_any_future_application",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    return {"valid": not errors, "error_codes": errors, "readiness_status": status}


def run_level2_sandbox_review_conclusion_and_promotion_readiness_minimal_check() -> dict[str, Any]:
    valid_conclusion = build_level2_sandbox_review_conclusion()
    valid_readiness = build_phase0_future_promotion_readiness(valid_conclusion)
    invalid_conclusions = _invalid_conclusion_records(valid_conclusion)
    invalid_readiness = _invalid_readiness_records(valid_readiness)
    conclusion_results = [
        validate_level2_sandbox_review_conclusion(record) for record in [valid_conclusion] + invalid_conclusions
    ]
    readiness_results = [
        validate_phase0_future_promotion_readiness(record) for record in [valid_readiness] + invalid_readiness
    ]
    valid_conclusion_results = [result for result in conclusion_results if result["valid"]]
    valid_readiness_results = [result for result in readiness_results if result["valid"]]
    summary = {
        "valid_level2_sandbox_review_conclusion_count": len(valid_conclusion_results),
        "invalid_level2_sandbox_review_conclusion_count": len(conclusion_results) - len(valid_conclusion_results),
        "valid_promotion_readiness_count": len(valid_readiness_results),
        "invalid_promotion_readiness_count": len(readiness_results) - len(valid_readiness_results),
        "ready_for_future_design_package_only_count": sum(
            1 for result in valid_readiness_results if result.get("readiness_status") == READINESS_READY
        ),
        "runtime_behavior_changed_count": 0,
        "memory_written_count": 0,
        "retained_jsonl_written_count": 0,
        "predictor_mutated_count": 0,
        "selected_action_created_count": 0,
        "final_action_created_count": 0,
        "production_promotion_claimed_count": 0,
        "proof_of_learning_claimed_count": 0,
    }
    summary["all_level2_sandbox_review_conclusion_and_promotion_readiness_checks_passed"] = (
        summary["valid_level2_sandbox_review_conclusion_count"] == 1
        and summary["invalid_level2_sandbox_review_conclusion_count"] >= 1
        and summary["valid_promotion_readiness_count"] == 1
        and summary["invalid_promotion_readiness_count"] >= 1
        and summary["ready_for_future_design_package_only_count"] == 1
        and summary["runtime_behavior_changed_count"] == 0
        and summary["memory_written_count"] == 0
        and summary["retained_jsonl_written_count"] == 0
        and summary["predictor_mutated_count"] == 0
        and summary["selected_action_created_count"] == 0
        and summary["final_action_created_count"] == 0
        and summary["production_promotion_claimed_count"] == 0
        and summary["proof_of_learning_claimed_count"] == 0
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok"
        if summary["all_level2_sandbox_review_conclusion_and_promotion_readiness_checks_passed"]
        else "failed",
        "review_conclusion_records": [valid_conclusion] + invalid_conclusions,
        "promotion_readiness_records": [valid_readiness] + invalid_readiness,
        "review_conclusion_validation_results": conclusion_results,
        "promotion_readiness_validation_results": readiness_results,
        "summary": summary,
        "safe_claim": SAFE_CLAIM,
        "boundary": {
            "boundary_change_required": False,
            "boundary_index_update_required": False,
            "boundary_index_version_before": "2026-06-09-b73",
            "boundary_index_version_after": "2026-06-09-b73",
            "boundary_change_rationale": (
                "Conclusion and future-design readiness records do not change permission scope or runtime boundaries."
            ),
        },
        "boundary_check": {
            "conclusion_and_readiness_only": True,
            "future_design_package_only": True,
            "level3_sandbox_application_added": False,
            "level2_runtime_execution_added": False,
            "production_promotion_added": False,
            "runtime_behavior_change_added": False,
            "memory_write_added": False,
            "retained_jsonl_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "proof_of_learning_claimed": False,
        },
    }


def _extract_closed_loop_records(record: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    if not isinstance(record, dict):
        return {}, {}, {}, {}
    return (
        _first(record.get("application_records")),
        _first(record.get("observation_records")),
        _first(record.get("evaluation_records")),
        _first(record.get("human_review_summary_records")),
    )


def _first(value: Any) -> dict[str, Any]:
    return value[0] if isinstance(value, list) and value and isinstance(value[0], dict) else {}


def _source_forbidden_flags_clear(*records: dict[str, Any]) -> bool:
    forbidden = (
        "proof_of_learning_claimed",
        "runtime_behavior_changed",
        "runtime_behavior_observed",
        "memory_written",
        "memory_write_observed",
        "retained_jsonl_written",
        "retained_jsonl_write_observed",
        "retention_written",
        "retention_write_observed",
        "predictor_mutated",
        "predictor_mutation_observed",
        "selected_action_created",
        "selected_action_observed",
        "final_action_created",
        "final_action_observed",
        "production_behavior_changed",
        "production_behavior_observed",
        "production_promotion_claimed",
    )
    return all(record.get(field, False) is False for record in records for field in forbidden)


def _human_review_summary_is_conservative(record: dict[str, Any]) -> bool:
    return (
        record.get("source_evaluation_valid") is True
        and record.get("proof_of_learning_claimed") is False
        and record.get("safe_summary") == LEVEL2_APPLICATION_SAFE_CLAIM
        and not _contains_proof_language(record.get("safe_summary", ""))
    )


def _contains_proof_language(value: Any) -> bool:
    return isinstance(value, str) and "proof of learning" in value.lower()


def _conclusion_reason(status: str) -> str:
    if status == CONCLUSION_PASSED:
        return "Level 2 sandbox-only closed loop passed within sandbox scope with audit and rollback."
    if status == CONCLUSION_FAILED:
        return "Level 2 sandbox review did not pass the expected sandbox outcome."
    return "Level 2 sandbox review is inconclusive because required closed-loop inputs are missing or invalid."


def _invalid_conclusion_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    failed = _mutated(valid, ["level2_evaluation_status"], "failed_expected_level2_sandbox_outcome")
    inconclusive = _mutated(valid, ["level2_evaluation_status"], EVALUATION_INCONCLUSIVE)
    invalid = [
        _mutated(valid, ["level2_application_valid"], False),
        _mutated(valid, ["level2_observation_valid"], False),
        _mutated(valid, ["human_review_summary_present"], False),
        _mutated(valid, ["audit_present"], False),
        _mutated(valid, ["rollback_present"], False),
        _mutated(valid, ["target_scope"], "production"),
        _mutated(valid, ["target_scope"], "runtime"),
        _mutated(valid, ["target_scope"], "phase0_level3_sandbox_only"),
        _mutated(valid, ["runtime_behavior_changed"], True),
        _mutated(valid, ["memory_written"], True),
        _mutated(valid, ["retained_jsonl_written"], True),
        _mutated(valid, ["retention_written"], True),
        _mutated(valid, ["predictor_mutated"], True),
        _mutated(valid, ["selected_action_created"], True),
        _mutated(valid, ["final_action_created"], True),
        _mutated(valid, ["production_promotion_claimed"], True),
        _mutated(valid, ["proof_of_learning_claimed"], True),
        _mutated(valid, ["review_conclusion_reason"], "This is proof of learning."),
    ]
    return invalid + [failed, inconclusive]


def _invalid_readiness_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    failed = _mutated(valid, ["source_review_conclusion_status"], CONCLUSION_FAILED)
    inconclusive = _mutated(valid, ["source_review_conclusion_status"], CONCLUSION_INCONCLUSIVE)
    invalid = [
        _mutated(valid, ["readiness_scope"], "production"),
        _mutated(valid, ["source_review_conclusion_status"], CONCLUSION_FAILED),
        _mutated(valid, ["source_review_conclusion_status"], CONCLUSION_INCONCLUSIVE),
        _mutated(valid, ["ready_for_runtime_behavior_change"], True),
        _mutated(valid, ["ready_for_memory_write"], True),
        _mutated(valid, ["ready_for_retained_jsonl_write"], True),
        _mutated(valid, ["ready_for_predictor_mutation"], True),
        _mutated(valid, ["ready_for_production_promotion"], True),
        _mutated(valid, ["ready_for_selected_action"], True),
        _mutated(valid, ["ready_for_final_action"], True),
        _mutated(valid, ["promotion_performed"], True),
        _mutated(valid, ["proof_of_learning_claimed"], True),
        _mutated(valid, ["human_review_required_for_any_future_boundary_change"], False),
        _mutated(valid, ["explicit_user_approval_required_for_any_future_application"], False),
    ]
    return invalid + [failed, inconclusive]


def _mutated(record: dict[str, Any], path: list[str], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: dict[str, Any] = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(run_level2_sandbox_review_conclusion_and_promotion_readiness_minimal_check(), indent=2))
