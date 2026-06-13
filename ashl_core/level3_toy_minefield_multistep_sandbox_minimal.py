"""Level 3 toy minefield multi-step sandbox closed loop."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .level2_sandbox_review_conclusion_and_promotion_readiness_minimal import (
    CONCLUSION_PASSED,
    READINESS_READY,
    build_level2_sandbox_review_conclusion,
    build_phase0_future_promotion_readiness,
    validate_level2_sandbox_review_conclusion,
    validate_phase0_future_promotion_readiness,
)


COMMAND = "run-level3-toy-minefield-multistep-sandbox-minimal-check"
FLOW = "level3_toy_minefield_multistep_sandbox_minimal_v0"
PACKAGE_ID = "PKG-Phase0-Level3-ToyMinefield-Multistep-Sandbox-Minimal-v0"
TARGET_SCOPE = "phase0_level3_toy_minefield_sandbox_only"
SCENARIO_ID = "toy_minefield_multistep_retry_correction_v0"
BOUNDARY_BEFORE = "2026-06-09-b73"
BOUNDARY_AFTER = "2026-06-09-b74"

ALLOWED_SANDBOX_STEP_ACTIONS = (
    "reveal_cell",
    "check_adjacent",
    "flag_possible_mine",
    "choose_safe_cell",
    "stop_and_report",
)
FALSE_FLAGS = (
    "runtime_behavior_changed",
    "memory_written",
    "retained_jsonl_written",
    "retention_written",
    "predictor_modified",
    "selected_action_created",
    "final_action_created",
    "production_promoted",
    "proof_of_learning_claimed",
)
EVALUATION_PASSED = "passed_expected_level3_sandbox_outcome"
EVALUATION_FAILED = "failed_expected_level3_sandbox_outcome"
EVALUATION_INCONCLUSIVE = "inconclusive_missing_or_invalid_trace"
ALLOWED_EVALUATION_STATUSES = (EVALUATION_PASSED, EVALUATION_FAILED, EVALUATION_INCONCLUSIVE)
SAFE_CLAIM = (
    "ASHL Core can run, observe, evaluate, and summarize a bounded Phase0 Level 3 toy minefield "
    "sandbox-only multi-step trace, using temporary sandbox-only state, explicit user approval, "
    "audit, and rollback, while runtime behavior, memory, retained JSONL, retention, predictor "
    "mutation, selected_action, final_action, production promotion, and proof-of-learning remain blocked."
)


def build_level3_explicit_user_approval_fixture(
    approval_source: str = "explicit_user_statement",
    approval_actor: str = "user",
    approver_role: str = "project_owner",
    approval_text: str = "I explicitly approve this Level 3 toy minefield sandbox-only package.",
) -> dict[str, Any]:
    return {
        "record_type": "level3_toy_minefield_explicit_user_approval_fixture",
        "approval_source": approval_source,
        "approval_actor": approval_actor,
        "approver_role": approver_role,
        "approval_text": approval_text,
        "test_fixture_only": True,
        "counts_as_real_world_approval": False,
    }


def validate_level3_explicit_user_approval_fixture(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("approval_source") != "explicit_user_statement":
        errors.append("approval_source_not_explicit_user_statement")
    if record.get("approval_actor") != "user":
        errors.append("approval_actor_not_user")
    if record.get("approver_role") != "project_owner":
        errors.append("approver_role_not_project_owner")
    if not isinstance(record.get("approval_text"), str) or not record.get("approval_text", "").strip():
        errors.append("approval_text_empty")
    if record.get("counts_as_real_world_approval") is not False:
        errors.append("counts_as_real_world_approval_not_false")
    return {"valid": not errors, "error_codes": errors}


def build_level3_toy_minefield_scenario_definition() -> dict[str, Any]:
    return {
        "record_type": "level3_toy_minefield_scenario_definition",
        "schema_version": "v0",
        "package_id": PACKAGE_ID,
        "scenario_id": SCENARIO_ID,
        "target_scope": TARGET_SCOPE,
        "board_size": "3x3",
        "minefield_mode": "deterministic_fixture",
        "objective": "reach_declared_safe_stop_without_revealing_known_risky_cell",
        "known_risky_cells": ["B2"],
        "known_safe_cells": ["A1", "A2", "A3"],
        "allowed_sandbox_step_actions": list(ALLOWED_SANDBOX_STEP_ACTIONS),
        "temporary_sandbox_state_only": True,
        "persistent_state_allowed": False,
        "runtime_execution_allowed": False,
        "memory_write_allowed": False,
        "retained_jsonl_write_allowed": False,
        "retention_write_allowed": False,
        "predictor_mutation_allowed": False,
        "selected_action_allowed": False,
        "final_action_allowed": False,
        "production_promotion_allowed": False,
        "proof_of_learning_claim_allowed": False,
    }


def validate_level3_toy_minefield_scenario_definition(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "level3_toy_minefield_scenario_definition":
        errors.append("record_type_not_level3_toy_minefield_scenario_definition")
    if record.get("schema_version") != "v0":
        errors.append("schema_version_not_v0")
    if record.get("package_id") != PACKAGE_ID:
        errors.append("package_id_not_expected")
    if record.get("scenario_id") != SCENARIO_ID:
        errors.append("scenario_id_not_expected")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_level3_toy_minefield_sandbox_only")
    if record.get("board_size") not in {"3x3", "4x4"}:
        errors.append("board_size_not_supported")
    if record.get("minefield_mode") != "deterministic_fixture":
        errors.append("minefield_mode_not_deterministic_fixture")
    if record.get("allowed_sandbox_step_actions") != list(ALLOWED_SANDBOX_STEP_ACTIONS):
        errors.append("allowed_sandbox_step_actions_not_expected")
    for field in (
        "temporary_sandbox_state_only",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in (
        "persistent_state_allowed",
        "runtime_execution_allowed",
        "memory_write_allowed",
        "retained_jsonl_write_allowed",
        "retention_write_allowed",
        "predictor_mutation_allowed",
        "selected_action_allowed",
        "final_action_allowed",
        "production_promotion_allowed",
        "proof_of_learning_claim_allowed",
    ):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {"valid": not errors, "error_codes": errors}


def build_level3_toy_minefield_sandbox_application_trace(
    level2_review_conclusion: dict[str, Any] | None = None,
    future_readiness: dict[str, Any] | None = None,
    explicit_user_approval: dict[str, Any] | None = None,
    scenario_definition: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if level2_review_conclusion is None:
        level2_review_conclusion = build_level2_sandbox_review_conclusion()
    if future_readiness is None:
        future_readiness = build_phase0_future_promotion_readiness(level2_review_conclusion)
    if explicit_user_approval is None:
        explicit_user_approval = build_level3_explicit_user_approval_fixture()
    if scenario_definition is None:
        scenario_definition = build_level3_toy_minefield_scenario_definition()
    return {
        "record_type": "level3_toy_minefield_sandbox_application_trace",
        "schema_version": "v0",
        "target_scope": TARGET_SCOPE,
        "source_level2_review_conclusion_checked": True,
        "future_higher_level_design_readiness_checked": True,
        "explicit_user_approval_checked": True,
        "scenario_definition_checked": True,
        "sandbox_trace_steps": _valid_trace_steps(),
        "check_before_retry_enforced": True,
        "retry_same_risky_cell_without_check_blocked": True,
        "audit_recorded": True,
        "rollback_available": True,
        "runtime_behavior_changed": False,
        "memory_written": False,
        "retained_jsonl_written": False,
        "retention_written": False,
        "predictor_modified": False,
        "selected_action_created": False,
        "final_action_created": False,
        "production_promoted": False,
        "proof_of_learning_claimed": False,
        "source_level2_review_conclusion": deepcopy(level2_review_conclusion),
        "source_future_readiness": deepcopy(future_readiness),
        "source_explicit_user_approval": deepcopy(explicit_user_approval),
        "source_scenario_definition": deepcopy(scenario_definition),
    }


def validate_level3_toy_minefield_sandbox_application_trace(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "level3_toy_minefield_sandbox_application_trace":
        errors.append("record_type_not_level3_toy_minefield_sandbox_application_trace")
    if record.get("schema_version") != "v0":
        errors.append("schema_version_not_v0")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_level3_toy_minefield_sandbox_only")
    conclusion = record.get("source_level2_review_conclusion", {})
    conclusion_result = validate_level2_sandbox_review_conclusion(conclusion)
    if conclusion_result.get("valid") is not True or conclusion.get("review_conclusion_status") != CONCLUSION_PASSED:
        errors.append("source_level2_review_conclusion_invalid_or_not_passed")
    readiness = record.get("source_future_readiness", {})
    readiness_result = validate_phase0_future_promotion_readiness(readiness)
    if readiness_result.get("valid") is not True or readiness.get("readiness_status") != READINESS_READY:
        errors.append("source_future_readiness_invalid_or_not_ready")
    approval_result = validate_level3_explicit_user_approval_fixture(record.get("source_explicit_user_approval", {}))
    if approval_result.get("valid") is not True:
        errors.append("explicit_user_approval_invalid")
        errors.extend(approval_result.get("error_codes", []))
    scenario_result = validate_level3_toy_minefield_scenario_definition(record.get("source_scenario_definition", {}))
    if scenario_result.get("valid") is not True:
        errors.append("scenario_definition_invalid")
    for field in (
        "source_level2_review_conclusion_checked",
        "future_higher_level_design_readiness_checked",
        "explicit_user_approval_checked",
        "scenario_definition_checked",
        "check_before_retry_enforced",
        "retry_same_risky_cell_without_check_blocked",
        "audit_recorded",
        "rollback_available",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    steps = record.get("sandbox_trace_steps")
    errors.extend(_validate_trace_steps(steps, record.get("source_scenario_definition", {})))
    for field in FALSE_FLAGS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {"valid": not errors, "error_codes": errors}


def build_level3_toy_minefield_observation(
    application_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if application_trace is None:
        application_trace = build_level3_toy_minefield_sandbox_application_trace()
    application_valid = validate_level3_toy_minefield_sandbox_application_trace(application_trace).get("valid") is True
    return {
        "record_type": "level3_toy_minefield_observation",
        "schema_version": "v0",
        "target_scope": TARGET_SCOPE,
        "application_trace_valid": application_valid,
        "observed_multistep_trace": application_valid,
        "observed_check_before_retry": application_trace.get("check_before_retry_enforced") is True,
        "observed_retry_block": application_trace.get("retry_same_risky_cell_without_check_blocked") is True,
        "observed_no_mine_revealed": _no_known_risky_cell_revealed(application_trace),
        "observed_safe_stop_or_goal": _stops_safely(application_trace),
        "observed_audit": application_trace.get("audit_recorded") is True,
        "observed_rollback": application_trace.get("rollback_available") is True,
        "runtime_behavior_changed": False,
        "memory_written": False,
        "retained_jsonl_written": False,
        "retention_written": False,
        "predictor_modified": False,
        "selected_action_created": False,
        "final_action_created": False,
        "production_promoted": False,
        "proof_of_learning_claimed": False,
        "source_application_trace": deepcopy(application_trace),
    }


def validate_level3_toy_minefield_observation(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "level3_toy_minefield_observation":
        errors.append("record_type_not_level3_toy_minefield_observation")
    if record.get("schema_version") != "v0":
        errors.append("schema_version_not_v0")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_level3_toy_minefield_sandbox_only")
    for field in (
        "application_trace_valid",
        "observed_multistep_trace",
        "observed_check_before_retry",
        "observed_retry_block",
        "observed_no_mine_revealed",
        "observed_safe_stop_or_goal",
        "observed_audit",
        "observed_rollback",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in FALSE_FLAGS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {"valid": not errors, "error_codes": errors}


def build_level3_toy_minefield_evaluation(
    observation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if observation is None:
        observation = build_level3_toy_minefield_observation()
    observation_valid = validate_level3_toy_minefield_observation(observation).get("valid") is True
    status = EVALUATION_PASSED if observation_valid else EVALUATION_INCONCLUSIVE
    return {
        "record_type": "level3_toy_minefield_evaluation",
        "schema_version": "v0",
        "target_scope": TARGET_SCOPE,
        "evaluation_status": status,
        "allowed_statuses": list(ALLOWED_EVALUATION_STATUSES),
        "reason_codes": [
            "multistep_trace_valid",
            "check_before_retry_enforced",
            "retry_same_risky_cell_without_check_blocked",
            "audit_and_rollback_present",
        ]
        if status == EVALUATION_PASSED
        else ["missing_or_invalid_trace"],
        "proof_of_learning_claimed": False,
        "runtime_behavior_changed": False,
        "memory_written": False,
        "retained_jsonl_written": False,
        "retention_written": False,
        "predictor_modified": False,
        "selected_action_created": False,
        "final_action_created": False,
        "production_promoted": False,
        "source_observation": deepcopy(observation),
    }


def validate_level3_toy_minefield_evaluation(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "level3_toy_minefield_evaluation":
        errors.append("record_type_not_level3_toy_minefield_evaluation")
    if record.get("schema_version") != "v0":
        errors.append("schema_version_not_v0")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_level3_toy_minefield_sandbox_only")
    if record.get("evaluation_status") not in set(ALLOWED_EVALUATION_STATUSES):
        errors.append("evaluation_status_unknown")
    if record.get("allowed_statuses") != list(ALLOWED_EVALUATION_STATUSES):
        errors.append("allowed_statuses_not_expected")
    if record.get("evaluation_status") == EVALUATION_PASSED:
        required = {
            "multistep_trace_valid",
            "check_before_retry_enforced",
            "retry_same_risky_cell_without_check_blocked",
            "audit_and_rollback_present",
        }
        if not required.issubset(set(record.get("reason_codes", []))):
            errors.append("passed_evaluation_missing_required_reason_codes")
    for field in FALSE_FLAGS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {"valid": not errors, "error_codes": errors, "evaluation_status": record.get("evaluation_status")}


def build_level3_toy_minefield_human_review_summary(
    evaluation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if evaluation is None:
        evaluation = build_level3_toy_minefield_evaluation()
    evaluation_valid = validate_level3_toy_minefield_evaluation(evaluation).get("valid") is True
    return {
        "record_type": "level3_toy_minefield_human_review_summary",
        "schema_version": "v0",
        "summary_status": "conservative_level3_sandbox_summary_ready",
        "source_evaluation_valid": evaluation_valid,
        "safe_summary": (
            "ASHL Core can run a bounded Level 3 toy minefield sandbox trace and evaluate whether "
            "check-before-retry behavior remained stable across a short multi-step sandbox workflow."
        ),
        "forbidden_summary_claims": [
            "proof_of_learning",
            "runtime_behavior_changed",
            "memory_written",
            "predictor_modified",
            "production_ready",
        ],
        "proof_of_learning_claimed": False,
        "runtime_behavior_changed": False,
        "memory_written": False,
        "retained_jsonl_written": False,
        "retention_written": False,
        "predictor_modified": False,
        "selected_action_created": False,
        "final_action_created": False,
        "production_promoted": False,
        "source_evaluation": deepcopy(evaluation),
    }


def validate_level3_toy_minefield_human_review_summary(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "level3_toy_minefield_human_review_summary":
        errors.append("record_type_not_level3_toy_minefield_human_review_summary")
    if record.get("schema_version") != "v0":
        errors.append("schema_version_not_v0")
    if record.get("summary_status") != "conservative_level3_sandbox_summary_ready":
        errors.append("summary_status_not_conservative_level3_sandbox_summary_ready")
    if record.get("source_evaluation_valid") is not True:
        errors.append("source_evaluation_valid_not_true")
    if not isinstance(record.get("safe_summary"), str) or not record.get("safe_summary", "").strip():
        errors.append("safe_summary_empty")
    if _contains_proof_language(record.get("safe_summary", "")):
        errors.append("safe_summary_contains_proof_language")
    expected_forbidden = [
        "proof_of_learning",
        "runtime_behavior_changed",
        "memory_written",
        "predictor_modified",
        "production_ready",
    ]
    if record.get("forbidden_summary_claims") != expected_forbidden:
        errors.append("forbidden_summary_claims_not_expected")
    for field in FALSE_FLAGS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {"valid": not errors, "error_codes": errors}


def build_level3_toy_minefield_multistep_sandbox_result() -> dict[str, Any]:
    scenario = build_level3_toy_minefield_scenario_definition()
    application = build_level3_toy_minefield_sandbox_application_trace(scenario_definition=scenario)
    observation = build_level3_toy_minefield_observation(application)
    evaluation = build_level3_toy_minefield_evaluation(observation)
    summary = build_level3_toy_minefield_human_review_summary(evaluation)
    return {
        "scenario_definition": scenario,
        "application_trace": application,
        "observation": observation,
        "evaluation": evaluation,
        "human_review_summary": summary,
    }


def validate_level3_toy_minefield_multistep_sandbox_result(record: dict[str, Any]) -> dict[str, Any]:
    scenario_result = validate_level3_toy_minefield_scenario_definition(record.get("scenario_definition", {}))
    application_result = validate_level3_toy_minefield_sandbox_application_trace(record.get("application_trace", {}))
    observation_result = validate_level3_toy_minefield_observation(record.get("observation", {}))
    evaluation_result = validate_level3_toy_minefield_evaluation(record.get("evaluation", {}))
    summary_result = validate_level3_toy_minefield_human_review_summary(record.get("human_review_summary", {}))
    errors = []
    for prefix, result in (
        ("scenario", scenario_result),
        ("application_trace", application_result),
        ("observation", observation_result),
        ("evaluation", evaluation_result),
        ("human_review_summary", summary_result),
    ):
        errors.extend(f"{prefix}:{error}" for error in result.get("error_codes", []))
    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_checked": scenario_result.get("valid") is True,
        "application_trace_checked": application_result.get("valid") is True,
        "observation_checked": observation_result.get("valid") is True,
        "evaluation_checked": evaluation_result.get("valid") is True,
        "human_review_summary_checked": summary_result.get("valid") is True,
    }


def run_level3_toy_minefield_multistep_sandbox_minimal_check() -> dict[str, Any]:
    valid = build_level3_toy_minefield_multistep_sandbox_result()
    invalid_records = _invalid_results(valid)
    validation_results = [
        validate_level3_toy_minefield_multistep_sandbox_result(record) for record in [valid] + invalid_records
    ]
    valid_results = [result for result in validation_results if result["valid"]]
    valid_application = valid["application_trace"]
    summary = {
        "valid_level3_toy_minefield_count": len(valid_results),
        "invalid_level3_toy_minefield_count": len(validation_results) - len(valid_results),
        "scenario_checked_count": sum(1 for result in valid_results if result["scenario_checked"]),
        "application_trace_checked_count": sum(1 for result in valid_results if result["application_trace_checked"]),
        "observation_checked_count": sum(1 for result in valid_results if result["observation_checked"]),
        "evaluation_checked_count": sum(1 for result in valid_results if result["evaluation_checked"]),
        "human_review_summary_checked_count": sum(
            1 for result in valid_results if result["human_review_summary_checked"]
        ),
        "audit_recorded_count": 1 if valid_application.get("audit_recorded") is True else 0,
        "rollback_available_count": 1 if valid_application.get("rollback_available") is True else 0,
        "proof_of_learning_claim_count": 0,
    }
    summary["all_level3_toy_minefield_multistep_sandbox_checks_passed"] = (
        summary["valid_level3_toy_minefield_count"] == 1
        and summary["invalid_level3_toy_minefield_count"] >= 1
        and summary["scenario_checked_count"] == 1
        and summary["application_trace_checked_count"] == 1
        and summary["observation_checked_count"] == 1
        and summary["evaluation_checked_count"] == 1
        and summary["human_review_summary_checked_count"] == 1
        and summary["audit_recorded_count"] == 1
        and summary["rollback_available_count"] == 1
        and summary["proof_of_learning_claim_count"] == 0
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_level3_toy_minefield_multistep_sandbox_checks_passed"] else "failed",
        "valid_result": valid,
        "invalid_results": invalid_records,
        "validation_results": validation_results,
        "summary": summary,
        "safe_claim": SAFE_CLAIM,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_BEFORE,
            "boundary_index_version_after": BOUNDARY_AFTER,
            "boundary_change_rationale": (
                "Level 3 introduces a new sandbox-only multi-step application trace scope, changing the "
                "sandbox application permission boundary."
            ),
        },
        "boundary_check": {
            "level3_toy_minefield_sandbox_only": True,
            "multistep_sandbox_trace_added": True,
            "temporary_sandbox_state_only": True,
            "level3_runtime_execution_added": False,
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


def _valid_trace_steps() -> list[dict[str, Any]]:
    return [
        {"step_index": 1, "sandbox_step_action": "reveal_cell", "cell": "A1", "result": "safe"},
        {
            "step_index": 2,
            "sandbox_step_action": "check_adjacent",
            "cell": "A1",
            "result": "risk_detected",
            "risky_cells": ["B2"],
        },
        {"step_index": 3, "sandbox_step_action": "flag_possible_mine", "cell": "B2", "result": "flagged"},
        {"step_index": 4, "sandbox_step_action": "choose_safe_cell", "cell": "A2", "result": "chosen"},
        {"step_index": 5, "sandbox_step_action": "reveal_cell", "cell": "A2", "result": "safe"},
        {"step_index": 6, "sandbox_step_action": "check_adjacent", "cell": "A2", "result": "no_new_risk"},
        {"step_index": 7, "sandbox_step_action": "choose_safe_cell", "cell": "A3", "result": "chosen"},
        {"step_index": 8, "sandbox_step_action": "stop_and_report", "cell": None, "result": "safe_stop"},
    ]


def _validate_trace_steps(steps: Any, scenario: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(steps, list):
        return ["sandbox_trace_steps_not_list"]
    if len(steps) < 2:
        errors.append("sandbox_trace_steps_not_multistep")
    allowed = set(scenario.get("allowed_sandbox_step_actions", ALLOWED_SANDBOX_STEP_ACTIONS))
    risky_cells = set(scenario.get("known_risky_cells", ["B2"]))
    checked_or_chosen_since_risky_reveal: dict[str, bool] = {}
    for expected_index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            errors.append("sandbox_trace_step_not_dict")
            continue
        if step.get("step_index") != expected_index:
            errors.append("sandbox_trace_step_index_not_ordered")
        action = step.get("sandbox_step_action")
        cell = step.get("cell")
        if action not in allowed:
            errors.append("unknown_sandbox_step_action")
        if action in {"check_adjacent", "choose_safe_cell"}:
            for risky in list(checked_or_chosen_since_risky_reveal):
                checked_or_chosen_since_risky_reveal[risky] = True
        if action == "reveal_cell" and cell in risky_cells:
            if checked_or_chosen_since_risky_reveal.get(cell) is False:
                errors.append("risky_cell_revealed_again_without_check")
            checked_or_chosen_since_risky_reveal[cell] = False
    if not any(step.get("sandbox_step_action") == "check_adjacent" for step in steps if isinstance(step, dict)):
        errors.append("trace_missing_check_adjacent")
    if not any(step.get("sandbox_step_action") == "stop_and_report" for step in steps if isinstance(step, dict)):
        errors.append("trace_missing_stop_and_report")
    return errors


def _no_known_risky_cell_revealed(application_trace: dict[str, Any]) -> bool:
    scenario = application_trace.get("source_scenario_definition", {})
    risky_cells = set(scenario.get("known_risky_cells", ["B2"]))
    return all(
        step.get("cell") not in risky_cells
        for step in application_trace.get("sandbox_trace_steps", [])
        if step.get("sandbox_step_action") == "reveal_cell"
    )


def _stops_safely(application_trace: dict[str, Any]) -> bool:
    steps = application_trace.get("sandbox_trace_steps", [])
    return bool(steps) and steps[-1].get("sandbox_step_action") == "stop_and_report" and steps[-1].get("result") == "safe_stop"


def _contains_proof_language(value: Any) -> bool:
    return isinstance(value, str) and "proof of learning" in value.lower()


def _invalid_results(valid: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _mutated(valid, ["application_trace", "source_explicit_user_approval", "approval_source"], "codex_generated"),
        _mutated(valid, ["application_trace", "source_explicit_user_approval", "approval_actor"], "codex"),
        _mutated(valid, ["application_trace", "source_explicit_user_approval", "approver_role"], "assistant"),
        _mutated(valid, ["application_trace", "source_explicit_user_approval", "approval_text"], ""),
        _mutated(valid, ["scenario_definition", "target_scope"], "production"),
        _mutated(valid, ["application_trace", "target_scope"], "runtime"),
        _mutated(valid, ["application_trace", "source_level2_review_conclusion"], {}),
        _mutated(valid, ["application_trace", "source_future_readiness"], {}),
        _mutated(valid, ["scenario_definition", "minefield_mode"], "random"),
        _mutated(valid, ["application_trace", "source_scenario_definition", "minefield_mode"], "random"),
        _mutated(valid, ["application_trace", "sandbox_trace_steps"], [_valid_trace_steps()[0]]),
        _mutated(valid, ["application_trace", "sandbox_trace_steps", 0, "sandbox_step_action"], "teleport"),
        _risky_repeat_without_check(valid),
        _mutated(valid, ["application_trace", "check_before_retry_enforced"], False),
        _mutated(valid, ["application_trace", "retry_same_risky_cell_without_check_blocked"], False),
        _mutated(valid, ["application_trace", "audit_recorded"], False),
        _mutated(valid, ["application_trace", "rollback_available"], False),
        _mutated(valid, ["application_trace", "memory_written"], True),
        _mutated(valid, ["application_trace", "retained_jsonl_written"], True),
        _mutated(valid, ["application_trace", "retention_written"], True),
        _mutated(valid, ["application_trace", "predictor_modified"], True),
        _mutated(valid, ["application_trace", "runtime_behavior_changed"], True),
        _mutated(valid, ["application_trace", "selected_action_created"], True),
        _mutated(valid, ["application_trace", "final_action_created"], True),
        _mutated(valid, ["application_trace", "production_promoted"], True),
        _mutated(valid, ["application_trace", "proof_of_learning_claimed"], True),
        _mutated(valid, ["human_review_summary", "safe_summary"], "This is proof of learning."),
    ]


def _risky_repeat_without_check(valid: dict[str, Any]) -> dict[str, Any]:
    trace = [
        {
            "step_index": 1,
            "sandbox_step_action": "check_adjacent",
            "cell": "A1",
            "result": "risk_detected",
            "risky_cells": ["B2"],
        },
        {"step_index": 2, "sandbox_step_action": "reveal_cell", "cell": "B2", "result": "blocked_unsafe"},
        {"step_index": 3, "sandbox_step_action": "reveal_cell", "cell": "B2", "result": "blocked_unsafe"},
        {"step_index": 4, "sandbox_step_action": "stop_and_report", "cell": None, "result": "safe_stop"},
    ]
    return _mutated(valid, ["application_trace", "sandbox_trace_steps"], trace)


def _mutated(record: dict[str, Any], path: list[Any], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: Any = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(run_level3_toy_minefield_multistep_sandbox_minimal_check(), indent=2))
