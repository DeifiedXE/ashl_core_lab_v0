"""Complete a Level 2 sandbox dry-run evidence path without application."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .level2_sandbox_design_envelope_minimal import validate_level2_sandbox_design_envelope
from .level2_sandbox_scenario_plan_minimal import (
    EXPECTED_OUTCOMES,
    PLANNED_FAILURE_CLASSES,
    PLANNED_STOP_CONDITIONS,
    build_level2_sandbox_scenario_plan,
    validate_level2_sandbox_scenario_plan,
)


COMMAND = "run-level2-sandbox-dry-run-observation-evaluation-summary-minimal-check"
FLOW = "level2_sandbox_dry_run_observation_evaluation_summary_minimal_v0"
SCOPE = "phase0_level2_sandbox_dry_run_only"
DESIGN_SCOPE = "phase0_level2_sandbox_design_only"

DRY_RUN_RECORD_TYPE = "level2_sandbox_dry_run"
OBSERVATION_RECORD_TYPE = "level2_sandbox_dry_run_observation"
EVALUATION_RECORD_TYPE = "level2_sandbox_dry_run_evaluation"
SUMMARY_RECORD_TYPE = "level2_sandbox_dry_run_human_review_summary"

DRY_RUN_COMPLETED = "completed_dry_run_without_execution"
DRY_RUN_ALLOWED_STATUSES = {
    DRY_RUN_COMPLETED,
    "blocked_invalid_design_envelope",
    "blocked_invalid_scenario_plan",
    "blocked_outside_design_envelope",
    "blocked_forbidden_level2_application_claim",
    "blocked_forbidden_runtime_or_memory_claim",
}
EVALUATION_PASSED = "passed_expected_level2_dry_run"
EVALUATION_FAILED = "failed_expected_level2_dry_run"
EVALUATION_INCONCLUSIVE = "inconclusive_missing_or_invalid_dry_run_observation"
EVALUATION_BLOCKED = "blocked_forbidden_claim"
EVALUATION_ALLOWED_STATUSES = {
    EVALUATION_PASSED,
    EVALUATION_FAILED,
    EVALUATION_INCONCLUSIVE,
    EVALUATION_BLOCKED,
}
SAFE_CLAIM = (
    "ASHL Core can complete and evaluate a Level 2 sandbox dry run within the design envelope "
    "without performing Level 2 application or execution."
)
NOT_CLAIMED = (
    "level2_application",
    "level2_execution",
    "runtime_behavior_change",
    "memory_write",
    "retained_jsonl_write",
    "retention_write",
    "predictor_mutation",
    "selected_action",
    "final_action",
    "direct_command",
    "production_promotion",
    "proof_of_learning",
)
FALSE_FIELDS = (
    "level2_application_performed",
    "level2_execution_performed",
    "runtime_behavior_changed",
    "memory_written",
    "retained_jsonl_written",
    "retention_written",
    "predictor_mutated",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "production_behavior_changed",
    "proof_of_learning_claimed",
)


def build_level2_sandbox_dry_run_record(
    scenario_plan_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if scenario_plan_record is None:
        scenario_plan_record = build_level2_sandbox_scenario_plan()

    source_is_dict = isinstance(scenario_plan_record, dict)
    scenario = scenario_plan_record if source_is_dict else {}
    scenario_validation = (
        validate_level2_sandbox_scenario_plan(scenario) if source_is_dict else {"valid": False}
    )
    design_envelope = scenario.get("source_level2_design_envelope_record") if source_is_dict else None
    design_valid = (
        isinstance(design_envelope, dict)
        and validate_level2_sandbox_design_envelope(design_envelope).get("valid") is True
    )
    inside_envelope = (
        scenario.get("target_scope") == DESIGN_SCOPE
        and scenario.get("source_level2_design_envelope", {}).get("target_scope") == DESIGN_SCOPE
    )
    if scenario_validation.get("valid") is not True:
        status = "blocked_invalid_scenario_plan"
    elif not design_valid:
        status = "blocked_invalid_design_envelope"
    elif not inside_envelope:
        status = "blocked_outside_design_envelope"
    else:
        status = DRY_RUN_COMPLETED

    return {
        "record_type": DRY_RUN_RECORD_TYPE,
        "phase": "phase0",
        "scope": SCOPE,
        "source_scenario_plan": deepcopy(scenario_plan_record) if source_is_dict else None,
        "source_scenario_plan_valid": scenario_validation.get("valid") is True,
        "source_design_envelope_valid": design_valid,
        "scenario_inside_design_envelope": inside_envelope,
        "dry_run_only": True,
        "level2_application_performed": False,
        "level2_execution_performed": False,
        "runtime_behavior_changed": False,
        "memory_written": False,
        "retained_jsonl_written": False,
        "retention_written": False,
        "predictor_mutated": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "production_behavior_changed": False,
        "proof_of_learning_claimed": False,
        "required_inputs_checked": status == DRY_RUN_COMPLETED,
        "design_envelope_checked": design_valid,
        "scenario_plan_checked": scenario_validation.get("valid") is True,
        "planned_inputs_used": status == DRY_RUN_COMPLETED,
        "expected_outcomes_loaded": status == DRY_RUN_COMPLETED,
        "failure_classes_loaded": status == DRY_RUN_COMPLETED,
        "stop_conditions_loaded": status == DRY_RUN_COMPLETED,
        "task_queue_completed_status_is_approval": False,
        "passing_tests_are_proof_of_learning": False,
        "dry_run_evaluation_authorizes_level2_application": False,
        "planned_expected_outcomes": dict(EXPECTED_OUTCOMES),
        "planned_failure_classes": list(PLANNED_FAILURE_CLASSES),
        "planned_stop_conditions": list(PLANNED_STOP_CONDITIONS),
        "dry_run_status": status,
    }


def validate_level2_sandbox_dry_run_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != DRY_RUN_RECORD_TYPE:
        errors.append("record_type_not_level2_sandbox_dry_run")
    if record.get("phase") != "phase0":
        errors.append("phase_not_phase0")
    if record.get("scope") != SCOPE:
        errors.append("scope_not_phase0_level2_sandbox_dry_run_only")
    if record.get("dry_run_status") not in DRY_RUN_ALLOWED_STATUSES:
        errors.append("dry_run_status_unknown")
    if record.get("dry_run_status") != DRY_RUN_COMPLETED:
        errors.append("dry_run_status_not_completed_without_execution")
    if record.get("dry_run_only") is not True:
        errors.append("dry_run_only_not_true")
    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in (
        "required_inputs_checked",
        "design_envelope_checked",
        "scenario_plan_checked",
        "planned_inputs_used",
        "expected_outcomes_loaded",
        "failure_classes_loaded",
        "stop_conditions_loaded",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    if record.get("source_scenario_plan_valid") is not True:
        errors.append("source_scenario_plan_valid_not_true")
    if record.get("source_design_envelope_valid") is not True:
        errors.append("source_design_envelope_valid_not_true")
    if record.get("scenario_inside_design_envelope") is not True:
        errors.append("scenario_inside_design_envelope_not_true")
    if record.get("task_queue_completed_status_is_approval") is not False:
        errors.append("task_queue_completed_status_is_approval_not_false")
    if record.get("passing_tests_are_proof_of_learning") is not False:
        errors.append("passing_tests_are_proof_of_learning_not_false")
    if record.get("dry_run_evaluation_authorizes_level2_application") is not False:
        errors.append("dry_run_evaluation_authorizes_level2_application_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "level2_application_blocked": record.get("level2_application_performed") is False,
        "level2_execution_blocked": record.get("level2_execution_performed") is False,
        "forbidden_runtime_memory_predictor_claim_blocked": (
            record.get("runtime_behavior_changed") is False
            and record.get("memory_written") is False
            and record.get("retained_jsonl_written") is False
            and record.get("retention_written") is False
            and record.get("predictor_mutated") is False
        ),
        "proof_of_learning_claim_blocked": record.get("proof_of_learning_claimed") is False,
    }


def build_level2_sandbox_dry_run_observation_record(
    dry_run_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if dry_run_record is None:
        dry_run_record = build_level2_sandbox_dry_run_record()
    source_is_dict = isinstance(dry_run_record, dict)
    source = dry_run_record if source_is_dict else {}
    source_validation = validate_level2_sandbox_dry_run_record(source) if source_is_dict else {"valid": False}
    valid_source = source_validation.get("valid") is True
    return {
        "record_type": OBSERVATION_RECORD_TYPE,
        "source_record_type": source.get("record_type"),
        "scope": SCOPE,
        "source_dry_run_valid": valid_source,
        "observation_only": True,
        "observed_planned_inputs": valid_source and source.get("planned_inputs_used") is True,
        "observed_expected_outcomes": valid_source and source.get("expected_outcomes_loaded") is True,
        "observed_failure_classes": valid_source and source.get("failure_classes_loaded") is True,
        "observed_stop_conditions": valid_source and source.get("stop_conditions_loaded") is True,
        "observed_no_level2_application": source.get("level2_application_performed") is False,
        "observed_no_level2_execution": source.get("level2_execution_performed") is False,
        "observed_no_runtime_behavior_change": source.get("runtime_behavior_changed") is False,
        "observed_no_memory_write": source.get("memory_written") is False,
        "observed_no_retained_jsonl_write": source.get("retained_jsonl_written") is False,
        "observed_no_retention_write": source.get("retention_written") is False,
        "observed_no_predictor_mutation": source.get("predictor_mutated") is False,
        "observed_no_selected_action": source.get("selected_action_created") is False,
        "observed_no_final_action": source.get("final_action_created") is False,
        "observed_no_direct_command": source.get("direct_command_created") is False,
        "observed_no_production_behavior_change": source.get("production_behavior_changed") is False,
        "observed_no_proof_of_learning_claim": source.get("proof_of_learning_claimed") is False,
        "source_dry_run": deepcopy(dry_run_record) if source_is_dict else None,
    }


def validate_level2_sandbox_dry_run_observation_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != OBSERVATION_RECORD_TYPE:
        errors.append("record_type_not_level2_sandbox_dry_run_observation")
    if record.get("source_record_type") != DRY_RUN_RECORD_TYPE:
        errors.append("source_record_type_not_level2_sandbox_dry_run")
    if record.get("scope") != SCOPE:
        errors.append("scope_not_phase0_level2_sandbox_dry_run_only")
    if record.get("source_dry_run_valid") is not True:
        errors.append("source_dry_run_valid_not_true")
    if record.get("observation_only") is not True:
        errors.append("observation_only_not_true")
    for field in (
        "observed_planned_inputs",
        "observed_expected_outcomes",
        "observed_failure_classes",
        "observed_stop_conditions",
        "observed_no_level2_application",
        "observed_no_level2_execution",
        "observed_no_runtime_behavior_change",
        "observed_no_memory_write",
        "observed_no_retained_jsonl_write",
        "observed_no_retention_write",
        "observed_no_predictor_mutation",
        "observed_no_selected_action",
        "observed_no_final_action",
        "observed_no_direct_command",
        "observed_no_production_behavior_change",
        "observed_no_proof_of_learning_claim",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    return {"valid": not errors, "error_codes": errors}


def build_level2_sandbox_dry_run_evaluation_record(
    observation_record: dict[str, Any] | None = None,
    evaluation_status: str | None = None,
) -> dict[str, Any]:
    if observation_record is None:
        observation_record = build_level2_sandbox_dry_run_observation_record()
    source_is_dict = isinstance(observation_record, dict)
    source = observation_record if source_is_dict else {}
    source_validation = (
        validate_level2_sandbox_dry_run_observation_record(source) if source_is_dict else {"valid": False}
    )
    forbidden_claim_detected = not _observation_forbidden_claims_blocked(source)
    if evaluation_status is None:
        if forbidden_claim_detected:
            evaluation_status = EVALUATION_BLOCKED
        elif source_validation.get("valid") is True and _observation_matches_plan(source):
            evaluation_status = EVALUATION_PASSED
        elif source_validation.get("valid") is True:
            evaluation_status = EVALUATION_FAILED
        else:
            evaluation_status = EVALUATION_INCONCLUSIVE
    return {
        "record_type": EVALUATION_RECORD_TYPE,
        "source_record_type": source.get("record_type"),
        "scope": SCOPE,
        "source_observation_valid": source_validation.get("valid") is True,
        "evaluation_only": True,
        "evaluation_status": evaluation_status,
        "evaluation_reason": _evaluation_reason(evaluation_status),
        "no_level2_application_confirmed": source.get("observed_no_level2_application") is True,
        "no_level2_execution_confirmed": source.get("observed_no_level2_execution") is True,
        "no_runtime_behavior_change_confirmed": source.get("observed_no_runtime_behavior_change") is True,
        "no_memory_write_confirmed": source.get("observed_no_memory_write") is True,
        "no_retained_jsonl_write_confirmed": source.get("observed_no_retained_jsonl_write") is True,
        "no_retention_write_confirmed": source.get("observed_no_retention_write") is True,
        "no_predictor_mutation_confirmed": source.get("observed_no_predictor_mutation") is True,
        "no_selected_action_confirmed": source.get("observed_no_selected_action") is True,
        "no_final_action_confirmed": source.get("observed_no_final_action") is True,
        "no_direct_command_confirmed": source.get("observed_no_direct_command") is True,
        "no_production_behavior_change_confirmed": source.get("observed_no_production_behavior_change") is True,
        "no_proof_of_learning_claim_confirmed": source.get("observed_no_proof_of_learning_claim") is True,
        "passing_evaluation_authorizes_level2_application": False,
        "passing_evaluation_authorizes_runtime_behavior_change": False,
        "passing_evaluation_authorizes_memory_or_predictor_change": False,
        "source_observation": deepcopy(observation_record) if source_is_dict else None,
    }


def validate_level2_sandbox_dry_run_evaluation_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    status = record.get("evaluation_status")
    if record.get("record_type") != EVALUATION_RECORD_TYPE:
        errors.append("record_type_not_level2_sandbox_dry_run_evaluation")
    if status != EVALUATION_INCONCLUSIVE and record.get("source_record_type") != OBSERVATION_RECORD_TYPE:
        errors.append("source_record_type_not_level2_sandbox_dry_run_observation")
    if record.get("scope") != SCOPE:
        errors.append("scope_not_phase0_level2_sandbox_dry_run_only")
    if record.get("evaluation_only") is not True:
        errors.append("evaluation_only_not_true")
    if status not in EVALUATION_ALLOWED_STATUSES:
        errors.append("evaluation_status_unknown")
    if status == EVALUATION_PASSED:
        if record.get("source_observation_valid") is not True:
            errors.append("passed_source_observation_valid_not_true")
        for field in _EVALUATION_CONFIRM_FIELDS:
            if record.get(field) is not True:
                errors.append(f"{field}_not_true")
    elif status == EVALUATION_FAILED:
        if record.get("source_observation_valid") is not True:
            errors.append("failed_source_observation_valid_not_true")
    elif status == EVALUATION_INCONCLUSIVE:
        if record.get("source_observation_valid") is True:
            errors.append("inconclusive_source_observation_valid_not_false")
    elif status == EVALUATION_BLOCKED:
        if _evaluation_forbidden_claims_confirmed(record):
            errors.append("blocked_forbidden_claim_not_detected")
    if not isinstance(record.get("evaluation_reason"), str) or not record.get("evaluation_reason", "").strip():
        errors.append("evaluation_reason_empty")
    for field in (
        "passing_evaluation_authorizes_level2_application",
        "passing_evaluation_authorizes_runtime_behavior_change",
        "passing_evaluation_authorizes_memory_or_predictor_change",
    ):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {"valid": not errors, "error_codes": errors, "evaluation_status": status}


def build_level2_sandbox_dry_run_human_review_summary(
    evaluation_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if evaluation_record is None:
        evaluation_record = build_level2_sandbox_dry_run_evaluation_record()
    source_is_dict = isinstance(evaluation_record, dict)
    source = evaluation_record if source_is_dict else {}
    source_validation = (
        validate_level2_sandbox_dry_run_evaluation_record(source) if source_is_dict else {"valid": False}
    )
    return {
        "record_type": SUMMARY_RECORD_TYPE,
        "source_record_type": source.get("record_type"),
        "scope": SCOPE,
        "source_evaluation_valid": source_validation.get("valid") is True,
        "summary_type": "conservative_human_review",
        "safe_claim": SAFE_CLAIM,
        "plain_language_result": (
            "The Level 2 sandbox scenario was walked through as a dry run and evaluated without "
            "performing Level 2 application or execution."
        ),
        "not_claimed": list(NOT_CLAIMED),
        "proof_of_learning_claimed": False,
        "level2_application_authorized": False,
        "runtime_behavior_change_authorized": False,
        "memory_write_authorized": False,
        "retention_write_authorized": False,
        "predictor_mutation_authorized": False,
        "source_evaluation": deepcopy(evaluation_record) if source_is_dict else None,
    }


def validate_level2_sandbox_dry_run_human_review_summary(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != SUMMARY_RECORD_TYPE:
        errors.append("record_type_not_level2_sandbox_dry_run_human_review_summary")
    if record.get("source_record_type") != EVALUATION_RECORD_TYPE:
        errors.append("source_record_type_not_level2_sandbox_dry_run_evaluation")
    if record.get("scope") != SCOPE:
        errors.append("scope_not_phase0_level2_sandbox_dry_run_only")
    if record.get("source_evaluation_valid") is not True:
        errors.append("source_evaluation_valid_not_true")
    if record.get("summary_type") != "conservative_human_review":
        errors.append("summary_type_not_conservative_human_review")
    if record.get("safe_claim") != SAFE_CLAIM:
        errors.append("safe_claim_not_allowed")
    if set(record.get("not_claimed", [])) != set(NOT_CLAIMED):
        errors.append("not_claimed_not_explicit")
    if not isinstance(record.get("plain_language_result"), str) or not record.get("plain_language_result", "").strip():
        errors.append("plain_language_result_empty")
    for field in (
        "proof_of_learning_claimed",
        "level2_application_authorized",
        "runtime_behavior_change_authorized",
        "memory_write_authorized",
        "retention_write_authorized",
        "predictor_mutation_authorized",
    ):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {"valid": not errors, "error_codes": errors}


_EVALUATION_CONFIRM_FIELDS = (
    "no_level2_application_confirmed",
    "no_level2_execution_confirmed",
    "no_runtime_behavior_change_confirmed",
    "no_memory_write_confirmed",
    "no_retained_jsonl_write_confirmed",
    "no_retention_write_confirmed",
    "no_predictor_mutation_confirmed",
    "no_selected_action_confirmed",
    "no_final_action_confirmed",
    "no_direct_command_confirmed",
    "no_production_behavior_change_confirmed",
    "no_proof_of_learning_claim_confirmed",
)


def run_level2_sandbox_dry_run_observation_evaluation_summary_minimal_check() -> dict[str, Any]:
    valid_dry_run = build_level2_sandbox_dry_run_record()
    valid_observation = build_level2_sandbox_dry_run_observation_record(valid_dry_run)
    valid_evaluation = build_level2_sandbox_dry_run_evaluation_record(valid_observation)
    valid_summary = build_level2_sandbox_dry_run_human_review_summary(valid_evaluation)
    invalid_dry_runs = _invalid_dry_run_records(valid_dry_run)
    dry_run_results = [validate_level2_sandbox_dry_run_record(record) for record in [valid_dry_run] + invalid_dry_runs]
    observation_results = [validate_level2_sandbox_dry_run_observation_record(valid_observation)]
    evaluation_results = [validate_level2_sandbox_dry_run_evaluation_record(valid_evaluation)]
    summary_results = [validate_level2_sandbox_dry_run_human_review_summary(valid_summary)]
    valid_dry_run_results = [result for result in dry_run_results if result.get("valid")]
    invalid_dry_run_results = [result for result in dry_run_results if not result.get("valid")]
    summary = {
        "valid_level2_sandbox_dry_run_count": len(valid_dry_run_results),
        "valid_level2_sandbox_dry_run_observation_count": sum(1 for result in observation_results if result.get("valid")),
        "valid_level2_sandbox_dry_run_evaluation_count": sum(1 for result in evaluation_results if result.get("valid")),
        "valid_level2_sandbox_dry_run_human_review_summary_count": sum(
            1 for result in summary_results if result.get("valid")
        ),
        "invalid_level2_sandbox_dry_run_count": len(invalid_dry_run_results),
        "level2_application_blocked_count": _count_error(dry_run_results, "level2_application_performed_not_false"),
        "level2_execution_blocked_count": _count_error(dry_run_results, "level2_execution_performed_not_false"),
        "forbidden_runtime_memory_predictor_claim_blocked_count": sum(
            _count_error(dry_run_results, code)
            for code in (
                "runtime_behavior_changed_not_false",
                "memory_written_not_false",
                "retained_jsonl_written_not_false",
                "retention_written_not_false",
                "predictor_mutated_not_false",
            )
        ),
        "proof_of_learning_claim_blocked_count": _count_error(dry_run_results, "proof_of_learning_claimed_not_false"),
    }
    summary["all_level2_sandbox_dry_run_observation_evaluation_summary_checks_passed"] = (
        summary["valid_level2_sandbox_dry_run_count"] == 1
        and summary["valid_level2_sandbox_dry_run_observation_count"] == 1
        and summary["valid_level2_sandbox_dry_run_evaluation_count"] == 1
        and summary["valid_level2_sandbox_dry_run_human_review_summary_count"] == 1
        and summary["invalid_level2_sandbox_dry_run_count"] >= 1
        and summary["level2_application_blocked_count"] >= 1
        and summary["level2_execution_blocked_count"] >= 1
        and summary["forbidden_runtime_memory_predictor_claim_blocked_count"] >= 1
        and summary["proof_of_learning_claim_blocked_count"] >= 1
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": (
            "ok"
            if summary["all_level2_sandbox_dry_run_observation_evaluation_summary_checks_passed"]
            else "failed"
        ),
        "dry_run_records": [valid_dry_run] + invalid_dry_runs,
        "observation_records": [valid_observation],
        "evaluation_records": [valid_evaluation],
        "human_review_summary_records": [valid_summary],
        "dry_run_validation_results": dry_run_results,
        "observation_validation_results": observation_results,
        "evaluation_validation_results": evaluation_results,
        "human_review_summary_validation_results": summary_results,
        "summary": summary,
        "boundary_check": {
            "level2_dry_run_only": True,
            "level2_application_added": False,
            "level2_execution_added": False,
            "runtime_behavior_change_added": False,
            "memory_write_added": False,
            "retained_jsonl_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "production_promotion_added": False,
            "approval_replay_session_binding_added": False,
            "proof_of_learning_claimed": False,
        },
    }


def _invalid_dry_run_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _mutated(valid, ["source_design_envelope_valid"], False),
        _mutated(valid, ["source_scenario_plan_valid"], False),
        _mutated(valid, ["scenario_inside_design_envelope"], False),
        _mutated(valid, ["level2_application_performed"], True),
        _mutated(valid, ["level2_execution_performed"], True),
        _mutated(valid, ["runtime_behavior_changed"], True),
        _mutated(valid, ["memory_written"], True),
        _mutated(valid, ["retained_jsonl_written"], True),
        _mutated(valid, ["retention_written"], True),
        _mutated(valid, ["predictor_mutated"], True),
        _mutated(valid, ["selected_action_created"], True),
        _mutated(valid, ["final_action_created"], True),
        _mutated(valid, ["direct_command_created"], True),
        _mutated(valid, ["production_behavior_changed"], True),
        _mutated(valid, ["proof_of_learning_claimed"], True),
        _mutated(valid, ["task_queue_completed_status_is_approval"], True),
        _mutated(valid, ["passing_tests_are_proof_of_learning"], True),
        _mutated(valid, ["dry_run_evaluation_authorizes_level2_application"], True),
    ]


def _observation_matches_plan(record: dict[str, Any]) -> bool:
    return (
        record.get("observed_planned_inputs") is True
        and record.get("observed_expected_outcomes") is True
        and record.get("observed_failure_classes") is True
        and record.get("observed_stop_conditions") is True
    )


def _observation_forbidden_claims_blocked(record: dict[str, Any]) -> bool:
    return all(
        record.get(field) is True
        for field in (
            "observed_no_level2_application",
            "observed_no_level2_execution",
            "observed_no_runtime_behavior_change",
            "observed_no_memory_write",
            "observed_no_retained_jsonl_write",
            "observed_no_retention_write",
            "observed_no_predictor_mutation",
            "observed_no_selected_action",
            "observed_no_final_action",
            "observed_no_direct_command",
            "observed_no_production_behavior_change",
            "observed_no_proof_of_learning_claim",
        )
    )


def _evaluation_forbidden_claims_confirmed(record: dict[str, Any]) -> bool:
    return all(record.get(field) is True for field in _EVALUATION_CONFIRM_FIELDS)


def _evaluation_reason(status: str) -> str:
    if status == EVALUATION_PASSED:
        return "dry run matched scenario plan and stayed inside design envelope"
    if status == EVALUATION_FAILED:
        return "dry run observation was valid but did not match the planned Level 2 scenario"
    if status == EVALUATION_BLOCKED:
        return "dry run observation contained a forbidden claim"
    return "dry run observation was missing or invalid"


def _count_error(results: list[dict[str, Any]], code: str) -> int:
    return sum(1 for result in results if code in result.get("error_codes", []))


def _mutated(record: dict[str, Any], path: list[str], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: dict[str, Any] = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(run_level2_sandbox_dry_run_observation_evaluation_summary_minimal_check(), indent=2))
