"""Apply, observe, evaluate, and summarize one Phase0 Level 2 sandbox record."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .level2_sandbox_dry_run_observation_evaluation_summary_minimal import (
    EVALUATION_PASSED as DRY_RUN_EVALUATION_PASSED,
    build_level2_sandbox_dry_run_evaluation_record,
    build_level2_sandbox_dry_run_human_review_summary,
    validate_level2_sandbox_dry_run_evaluation_record,
    validate_level2_sandbox_dry_run_human_review_summary,
)
from .level2_sandbox_scenario_plan_minimal import (
    EXPECTED_OUTCOMES,
    PLANNED_FAILURE_CLASSES,
    PLANNED_STOP_CONDITIONS,
    build_level2_sandbox_scenario_plan,
    validate_level2_sandbox_scenario_plan,
)


COMMAND = "run-level2-sandbox-application-observation-evaluation-summary-minimal-check"
FLOW = "level2_sandbox_application_observation_evaluation_summary_minimal_v0"
TARGET_SCOPE = "phase0_level2_sandbox_only"
PHASE = "phase0"
SANDBOX_LEVEL = 2

APPLICATION_RECORD_TYPE = "level2_sandbox_application"
OBSERVATION_RECORD_TYPE = "level2_sandbox_application_observation"
EVALUATION_RECORD_TYPE = "level2_sandbox_application_evaluation"
SUMMARY_RECORD_TYPE = "level2_sandbox_application_human_review_summary"

APPLICATION_STATUS = "applied_to_level2_sandbox_only"
OBSERVATION_STATUS = "observed_level2_sandbox_application"
EVALUATION_PASSED = "passed_expected_level2_sandbox_outcome"
EVALUATION_FAILED = "failed_expected_level2_sandbox_outcome"
EVALUATION_INCONCLUSIVE = "inconclusive_missing_or_invalid_observation"
SUMMARY_STATUS = "conservative_level2_sandbox_application_review_summary"

APPROVAL_TEXT = "I explicitly approve Phase0 Level 2 sandbox-only application for this package."
SAFE_CLAIM = (
    "ASHL Core can apply and evaluate a reviewed lesson inside the Phase0 Level 2 sandbox scope "
    "only, with explicit user approval, audit, rollback, observation, evaluation, and human review summary."
)
FORBIDDEN_CLAIMS = (
    "runtime behavior changed",
    "production behavior changed",
    "memory written",
    "retained JSONL written",
    "retention written",
    "predictor mutated",
    "selected_action created",
    "final_action created",
    "direct command created",
    "proof of learning",
)
FALSE_FIELDS = (
    "runtime_behavior_changed",
    "production_behavior_changed",
    "memory_written",
    "retained_jsonl_written",
    "retention_written",
    "predictor_mutated",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "proof_of_learning_claimed",
)


def build_level2_explicit_user_approval_fixture(
    approval_source: str = "explicit_user_statement",
    approval_actor: str = "user",
    approver_role: str = "project_owner",
    approval_text: str = APPROVAL_TEXT,
) -> dict[str, Any]:
    explicit = (
        approval_source == "explicit_user_statement"
        and approval_actor == "user"
        and approver_role == "project_owner"
        and isinstance(approval_text, str)
        and bool(approval_text.strip())
    )
    return {
        "approval_source": approval_source,
        "approval_actor": approval_actor,
        "approver_role": approver_role,
        "approval_text": approval_text,
        "approval_text_present": bool(isinstance(approval_text, str) and approval_text.strip()),
        "explicit_user_statement_present": explicit,
        "codex_self_approval_allowed": False,
        "ai_self_approval_allowed": False,
        "task_queue_status_is_approval": False,
        "passing_tests_are_approval": False,
        "test_fixture_is_real_approval": False,
    }


def build_level2_sandbox_application_record(
    scenario_plan_record: dict[str, Any] | None = None,
    dry_run_evaluation_record: dict[str, Any] | None = None,
    dry_run_human_review_summary_record: dict[str, Any] | None = None,
    approval_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if scenario_plan_record is None:
        scenario_plan_record = build_level2_sandbox_scenario_plan()
    if dry_run_evaluation_record is None:
        dry_run_evaluation_record = build_level2_sandbox_dry_run_evaluation_record()
    if dry_run_human_review_summary_record is None:
        dry_run_human_review_summary_record = build_level2_sandbox_dry_run_human_review_summary(
            dry_run_evaluation_record
        )
    if approval_record is None:
        approval_record = build_level2_explicit_user_approval_fixture()

    scenario_valid = (
        isinstance(scenario_plan_record, dict)
        and validate_level2_sandbox_scenario_plan(scenario_plan_record).get("valid") is True
    )
    dry_run_eval_valid = (
        isinstance(dry_run_evaluation_record, dict)
        and validate_level2_sandbox_dry_run_evaluation_record(dry_run_evaluation_record).get("valid") is True
        and dry_run_evaluation_record.get("evaluation_status") == DRY_RUN_EVALUATION_PASSED
    )
    dry_run_summary_valid = (
        isinstance(dry_run_human_review_summary_record, dict)
        and validate_level2_sandbox_dry_run_human_review_summary(dry_run_human_review_summary_record).get("valid")
        is True
    )
    approval_valid = _approval_is_valid(approval_record)
    applied = scenario_valid and dry_run_eval_valid and dry_run_summary_valid and approval_valid

    return {
        "record_type": APPLICATION_RECORD_TYPE,
        "application_id": "level2_sandbox_application_demo_001",
        "phase": PHASE,
        "sandbox_level": SANDBOX_LEVEL,
        "target_scope": TARGET_SCOPE,
        "application_status": (
            APPLICATION_STATUS if applied else "blocked_missing_or_invalid_level2_application_prerequisite"
        ),
        "source_scenario_plan_id": "phase0_level2_scenario_plan_minimal_v0",
        "source_dry_run_evaluation_id": "level2_sandbox_dry_run_evaluation_demo_001",
        "source_human_review_summary_id": "level2_sandbox_dry_run_human_review_summary_demo_001",
        "source_scenario_plan_valid": scenario_valid,
        "source_dry_run_evaluation_valid": dry_run_eval_valid,
        "source_human_review_summary_valid": dry_run_summary_valid,
        "approval_checked": approval_valid,
        "approval_source": approval_record.get("approval_source") if isinstance(approval_record, dict) else None,
        "approval_actor": approval_record.get("approval_actor") if isinstance(approval_record, dict) else None,
        "approver_role": approval_record.get("approver_role") if isinstance(approval_record, dict) else None,
        "approval_text_present": (
            approval_record.get("approval_text_present") is True if isinstance(approval_record, dict) else False
        ),
        "level2_sandbox_application_performed": applied,
        "expected_sandbox_effect": dict(EXPECTED_OUTCOMES),
        "scenario_inputs": deepcopy(scenario_plan_record.get("planned_inputs", {}))
        if isinstance(scenario_plan_record, dict)
        else {},
        "expected_outcomes": dict(EXPECTED_OUTCOMES),
        "stop_conditions": list(PLANNED_STOP_CONDITIONS),
        "failure_classes": list(PLANNED_FAILURE_CLASSES),
        "runtime_behavior_changed": False,
        "production_behavior_changed": False,
        "memory_written": False,
        "retained_jsonl_written": False,
        "retention_written": False,
        "predictor_mutated": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "proof_of_learning_claimed": False,
        "task_queue_completion_counted_as_approval": False,
        "passing_tests_counted_as_approval": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_scenario_plan_record": deepcopy(scenario_plan_record) if isinstance(scenario_plan_record, dict) else None,
        "source_dry_run_evaluation_record": deepcopy(dry_run_evaluation_record)
        if isinstance(dry_run_evaluation_record, dict)
        else None,
        "source_human_review_summary_record": deepcopy(dry_run_human_review_summary_record)
        if isinstance(dry_run_human_review_summary_record, dict)
        else None,
        "approval_record": deepcopy(approval_record) if isinstance(approval_record, dict) else None,
    }


def validate_level2_sandbox_application_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != APPLICATION_RECORD_TYPE:
        errors.append("record_type_not_level2_sandbox_application")
    if record.get("phase") != PHASE:
        errors.append("phase_not_phase0")
    if record.get("sandbox_level") != SANDBOX_LEVEL:
        errors.append("sandbox_level_not_2")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_phase0_level2_sandbox_only")
    if record.get("application_status") != APPLICATION_STATUS:
        errors.append("application_status_not_applied_to_level2_sandbox_only")
    for field in (
        "source_scenario_plan_valid",
        "source_dry_run_evaluation_valid",
        "source_human_review_summary_valid",
        "approval_checked",
        "level2_sandbox_application_performed",
        "audit_recorded",
        "rollback_available",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    if record.get("approval_source") != "explicit_user_statement":
        errors.append("approval_source_not_explicit_user_statement")
    if record.get("approval_actor") != "user":
        errors.append("approval_actor_not_user")
    if record.get("approver_role") != "project_owner":
        errors.append("approver_role_not_project_owner")
    if record.get("approval_text_present") is not True:
        errors.append("approval_text_present_not_true")
    if record.get("expected_outcomes") != EXPECTED_OUTCOMES:
        errors.append("expected_outcomes_not_level2_plan")
    if set(record.get("stop_conditions", [])) != set(PLANNED_STOP_CONDITIONS):
        errors.append("stop_conditions_not_level2_plan")
    if set(record.get("failure_classes", [])) != set(PLANNED_FAILURE_CLASSES):
        errors.append("failure_classes_not_level2_plan")
    if record.get("task_queue_completion_counted_as_approval") is not False:
        errors.append("task_queue_completion_counted_as_approval_not_false")
    if record.get("passing_tests_counted_as_approval") is not False:
        errors.append("passing_tests_counted_as_approval_not_false")
    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    approval = record.get("approval_record")
    if not isinstance(approval, dict) or not _approval_is_valid(approval):
        errors.append("approval_record_invalid")
    return {"valid": not errors, "error_codes": errors}


def build_level2_sandbox_application_observation_record(
    application_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if application_record is None:
        application_record = build_level2_sandbox_application_record()
    source_is_dict = isinstance(application_record, dict)
    source = application_record if source_is_dict else {}
    source_valid = (
        source_is_dict and validate_level2_sandbox_application_record(source).get("valid") is True
    )
    return {
        "record_type": OBSERVATION_RECORD_TYPE,
        "observation_id": "level2_sandbox_application_observation_demo_001",
        "phase": PHASE,
        "sandbox_level": SANDBOX_LEVEL,
        "target_scope": TARGET_SCOPE,
        "source_application_id": source.get("application_id"),
        "source_application_valid": source_valid,
        "observation_status": (
            OBSERVATION_STATUS if source_valid else "inconclusive_missing_or_invalid_application"
        ),
        "observed_application_status": source.get("application_status"),
        "observed_scenario_inputs": deepcopy(source.get("scenario_inputs", {})),
        "observed_expected_outcomes": deepcopy(source.get("expected_outcomes", {})),
        "observed_stop_conditions": list(source.get("stop_conditions", [])),
        "observed_failure_classes": list(source.get("failure_classes", [])),
        "runtime_behavior_observed": False,
        "production_behavior_observed": False,
        "memory_write_observed": False,
        "retained_jsonl_write_observed": False,
        "retention_write_observed": False,
        "predictor_mutation_observed": False,
        "selected_action_observed": False,
        "final_action_observed": False,
        "direct_command_observed": False,
        "proof_of_learning_claim_observed": False,
        "audit_still_present": source.get("audit_recorded") is True,
        "rollback_still_available": source.get("rollback_available") is True,
        "source_application_record": deepcopy(application_record) if source_is_dict else None,
    }


def validate_level2_sandbox_application_observation_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != OBSERVATION_RECORD_TYPE:
        errors.append("record_type_not_level2_sandbox_application_observation")
    if record.get("phase") != PHASE:
        errors.append("phase_not_phase0")
    if record.get("sandbox_level") != SANDBOX_LEVEL:
        errors.append("sandbox_level_not_2")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_phase0_level2_sandbox_only")
    if record.get("source_application_valid") is not True:
        errors.append("source_application_valid_not_true")
    if record.get("observation_status") != OBSERVATION_STATUS:
        errors.append("observation_status_not_observed_level2_sandbox_application")
    if record.get("observed_application_status") != APPLICATION_STATUS:
        errors.append("observed_application_status_not_applied")
    if record.get("observed_expected_outcomes") != EXPECTED_OUTCOMES:
        errors.append("observed_expected_outcomes_not_expected")
    if set(record.get("observed_stop_conditions", [])) != set(PLANNED_STOP_CONDITIONS):
        errors.append("observed_stop_conditions_not_expected")
    if set(record.get("observed_failure_classes", [])) != set(PLANNED_FAILURE_CLASSES):
        errors.append("observed_failure_classes_not_expected")
    for field in (
        "runtime_behavior_observed",
        "production_behavior_observed",
        "memory_write_observed",
        "retained_jsonl_write_observed",
        "retention_write_observed",
        "predictor_mutation_observed",
        "selected_action_observed",
        "final_action_observed",
        "direct_command_observed",
        "proof_of_learning_claim_observed",
    ):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in ("audit_still_present", "rollback_still_available"):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    return {"valid": not errors, "error_codes": errors}


def build_level2_sandbox_application_evaluation_record(
    observation_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if observation_record is None:
        observation_record = build_level2_sandbox_application_observation_record()
    source_is_dict = isinstance(observation_record, dict)
    source = observation_record if source_is_dict else {}
    source_valid = (
        source_is_dict and validate_level2_sandbox_application_observation_record(source).get("valid") is True
    )
    forbidden_clear = _observation_has_no_forbidden_effects(source)
    expected_matched = source.get("observed_expected_outcomes") == EXPECTED_OUTCOMES
    stop_ok = set(source.get("observed_stop_conditions", [])) == set(PLANNED_STOP_CONDITIONS)
    failure_ok = set(source.get("observed_failure_classes", [])) == set(PLANNED_FAILURE_CLASSES)
    if source_valid and expected_matched and stop_ok and failure_ok and forbidden_clear:
        status = EVALUATION_PASSED
    elif source_valid:
        status = EVALUATION_FAILED
    else:
        status = EVALUATION_INCONCLUSIVE
    return {
        "record_type": EVALUATION_RECORD_TYPE,
        "evaluation_id": "level2_sandbox_application_evaluation_demo_001",
        "phase": PHASE,
        "sandbox_level": SANDBOX_LEVEL,
        "target_scope": TARGET_SCOPE,
        "source_observation_id": source.get("observation_id"),
        "source_observation_valid": source_valid,
        "evaluation_status": status,
        "expected_outcome_matched": expected_matched,
        "stop_conditions_respected": stop_ok,
        "failure_classification_valid": failure_ok,
        "no_forbidden_capability_detected": forbidden_clear,
        "proof_of_learning_claimed": False,
        "source_observation_record": deepcopy(observation_record) if source_is_dict else None,
    }


def validate_level2_sandbox_application_evaluation_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    status = record.get("evaluation_status")
    if record.get("record_type") != EVALUATION_RECORD_TYPE:
        errors.append("record_type_not_level2_sandbox_application_evaluation")
    if record.get("phase") != PHASE:
        errors.append("phase_not_phase0")
    if record.get("sandbox_level") != SANDBOX_LEVEL:
        errors.append("sandbox_level_not_2")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_phase0_level2_sandbox_only")
    if status not in {EVALUATION_PASSED, EVALUATION_FAILED, EVALUATION_INCONCLUSIVE}:
        errors.append("evaluation_status_unknown")
    if status == EVALUATION_PASSED:
        for field in (
            "source_observation_valid",
            "expected_outcome_matched",
            "stop_conditions_respected",
            "failure_classification_valid",
            "no_forbidden_capability_detected",
        ):
            if record.get(field) is not True:
                errors.append(f"{field}_not_true")
    elif status == EVALUATION_INCONCLUSIVE and record.get("source_observation_valid") is True:
        errors.append("inconclusive_source_observation_valid_not_false")
    if record.get("proof_of_learning_claimed") is not False:
        errors.append("proof_of_learning_claimed_not_false")
    return {"valid": not errors, "error_codes": errors, "evaluation_status": status}


def build_level2_sandbox_application_human_review_summary(
    evaluation_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if evaluation_record is None:
        evaluation_record = build_level2_sandbox_application_evaluation_record()
    source_is_dict = isinstance(evaluation_record, dict)
    source = evaluation_record if source_is_dict else {}
    source_valid = (
        source_is_dict and validate_level2_sandbox_application_evaluation_record(source).get("valid") is True
    )
    return {
        "record_type": SUMMARY_RECORD_TYPE,
        "summary_id": "level2_sandbox_application_human_review_summary_demo_001",
        "phase": PHASE,
        "sandbox_level": SANDBOX_LEVEL,
        "target_scope": TARGET_SCOPE,
        "source_evaluation_id": source.get("evaluation_id"),
        "source_evaluation_valid": source_valid,
        "summary_status": SUMMARY_STATUS,
        "safe_summary": SAFE_CLAIM,
        "allowed_claims": [SAFE_CLAIM],
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "proof_of_learning_claimed": False,
        "source_evaluation_record": deepcopy(evaluation_record) if source_is_dict else None,
    }


def validate_level2_sandbox_application_human_review_summary(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != SUMMARY_RECORD_TYPE:
        errors.append("record_type_not_level2_sandbox_application_human_review_summary")
    if record.get("phase") != PHASE:
        errors.append("phase_not_phase0")
    if record.get("sandbox_level") != SANDBOX_LEVEL:
        errors.append("sandbox_level_not_2")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_phase0_level2_sandbox_only")
    if record.get("source_evaluation_valid") is not True:
        errors.append("source_evaluation_valid_not_true")
    if record.get("summary_status") != SUMMARY_STATUS:
        errors.append("summary_status_not_conservative")
    if record.get("safe_summary") != SAFE_CLAIM:
        errors.append("safe_summary_not_allowed")
    if record.get("allowed_claims") != [SAFE_CLAIM]:
        errors.append("allowed_claims_not_conservative")
    if set(record.get("forbidden_claims", [])) != set(FORBIDDEN_CLAIMS):
        errors.append("forbidden_claims_not_complete")
    if record.get("proof_of_learning_claimed") is not False:
        errors.append("proof_of_learning_claimed_not_false")
    return {"valid": not errors, "error_codes": errors}


def run_level2_sandbox_application_observation_evaluation_summary_minimal_check() -> dict[str, Any]:
    valid_application = build_level2_sandbox_application_record()
    valid_observation = build_level2_sandbox_application_observation_record(valid_application)
    valid_evaluation = build_level2_sandbox_application_evaluation_record(valid_observation)
    valid_summary = build_level2_sandbox_application_human_review_summary(valid_evaluation)

    invalid_applications = _invalid_application_records(valid_application)
    invalid_observation = _mutated(valid_observation, ["source_application_valid"], False)
    invalid_evaluation = _mutated(valid_evaluation, ["proof_of_learning_claimed"], True)
    invalid_summary = _mutated(valid_summary, ["proof_of_learning_claimed"], True)

    application_results = [
        validate_level2_sandbox_application_record(record) for record in [valid_application] + invalid_applications
    ]
    observation_results = [
        validate_level2_sandbox_application_observation_record(valid_observation),
        validate_level2_sandbox_application_observation_record(invalid_observation),
    ]
    evaluation_results = [
        validate_level2_sandbox_application_evaluation_record(valid_evaluation),
        validate_level2_sandbox_application_evaluation_record(invalid_evaluation),
    ]
    summary_results = [
        validate_level2_sandbox_application_human_review_summary(valid_summary),
        validate_level2_sandbox_application_human_review_summary(invalid_summary),
    ]
    summary = {
        "valid_level2_sandbox_application_count": sum(1 for result in application_results if result["valid"]),
        "valid_level2_observation_count": sum(1 for result in observation_results if result["valid"]),
        "valid_level2_evaluation_count": sum(1 for result in evaluation_results if result["valid"]),
        "valid_level2_human_review_summary_count": sum(1 for result in summary_results if result["valid"]),
        "invalid_level2_records_blocked_count": (
            sum(1 for result in application_results if not result["valid"])
            + sum(1 for result in observation_results if not result["valid"])
            + sum(1 for result in evaluation_results if not result["valid"])
            + sum(1 for result in summary_results if not result["valid"])
        ),
        "forbidden_capability_detected_count": 0,
        "proof_of_learning_claim_detected_count": 0,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
    }
    summary["all_level2_sandbox_application_observation_evaluation_summary_checks_passed"] = (
        summary["valid_level2_sandbox_application_count"] == 1
        and summary["valid_level2_observation_count"] == 1
        and summary["valid_level2_evaluation_count"] == 1
        and summary["valid_level2_human_review_summary_count"] == 1
        and summary["invalid_level2_records_blocked_count"] >= 1
        and summary["forbidden_capability_detected_count"] == 0
        and summary["proof_of_learning_claim_detected_count"] == 0
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok"
        if summary["all_level2_sandbox_application_observation_evaluation_summary_checks_passed"]
        else "failed",
        "application_records": [valid_application] + invalid_applications,
        "observation_records": [valid_observation, invalid_observation],
        "evaluation_records": [valid_evaluation, invalid_evaluation],
        "human_review_summary_records": [valid_summary, invalid_summary],
        "application_validation_results": application_results,
        "observation_validation_results": observation_results,
        "evaluation_validation_results": evaluation_results,
        "human_review_summary_validation_results": summary_results,
        "summary": summary,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": "2026-06-09-b72",
            "boundary_index_version_after": "2026-06-09-b73",
            "boundary_change_rationale": (
                "Level 2 moves from dry-run-only into sandbox-only application, which changes the "
                "sandbox application permission boundary."
            ),
        },
        "boundary_check": {
            "level2_sandbox_only_application": True,
            "level2_runtime_execution": False,
            "production_behavior_change_added": False,
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


def _approval_is_valid(record: Any) -> bool:
    return (
        isinstance(record, dict)
        and record.get("approval_source") == "explicit_user_statement"
        and record.get("approval_actor") == "user"
        and record.get("approver_role") == "project_owner"
        and record.get("approval_text_present") is True
        and record.get("explicit_user_statement_present") is True
        and record.get("codex_self_approval_allowed") is False
        and record.get("ai_self_approval_allowed") is False
        and record.get("task_queue_status_is_approval") is False
        and record.get("passing_tests_are_approval") is False
        and record.get("test_fixture_is_real_approval") is False
    )


def _observation_has_no_forbidden_effects(record: dict[str, Any]) -> bool:
    return all(
        record.get(field) is False
        for field in (
            "runtime_behavior_observed",
            "production_behavior_observed",
            "memory_write_observed",
            "retained_jsonl_write_observed",
            "retention_write_observed",
            "predictor_mutation_observed",
            "selected_action_observed",
            "final_action_observed",
            "direct_command_observed",
            "proof_of_learning_claim_observed",
        )
    )


def _invalid_application_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalid = [
        _mutated(valid, ["approval_checked"], False),
        _mutated(valid, ["approval_source"], "codex"),
        _mutated(valid, ["approval_source"], "ai"),
        _mutated(valid, ["approval_source"], "task_queue"),
        _mutated(valid, ["approval_source"], "test_fixture"),
        _mutated(valid, ["approval_source"], "passing_tests"),
        _mutated(valid, ["approval_actor"], "codex"),
        _mutated(valid, ["approval_actor"], "ai"),
        _mutated(valid, ["approval_text_present"], False),
        _mutated(valid, ["source_scenario_plan_valid"], False),
        _mutated(valid, ["source_dry_run_evaluation_valid"], False),
        _mutated(valid, ["source_human_review_summary_valid"], False),
        _mutated(valid, ["target_scope"], "phase0_level2_sandbox_dry_run_only"),
        _mutated(valid, ["sandbox_level"], 1),
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
        _mutated(valid, ["audit_recorded"], False),
        _mutated(valid, ["rollback_available"], False),
        _mutated(valid, ["task_queue_completion_counted_as_approval"], True),
        _mutated(valid, ["passing_tests_counted_as_approval"], True),
    ]
    invalid.append(_mutated(valid, ["approval_record", "approval_source"], "codex"))
    invalid.append(_mutated(valid, ["approval_record", "approval_actor"], "ai"))
    invalid.append(_mutated(valid, ["approval_record", "task_queue_status_is_approval"], True))
    invalid.append(_mutated(valid, ["approval_record", "passing_tests_are_approval"], True))
    invalid.append(_mutated(valid, ["approval_record", "test_fixture_is_real_approval"], True))
    return invalid


def _mutated(record: dict[str, Any], path: list[str], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: dict[str, Any] = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(run_level2_sandbox_application_observation_evaluation_summary_minimal_check(), indent=2))
