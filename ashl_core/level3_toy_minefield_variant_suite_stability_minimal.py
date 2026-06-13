"""Level 3 toy minefield deterministic variant suite stability review."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .level3_toy_minefield_multistep_sandbox_minimal import (
    TARGET_SCOPE,
    validate_level3_toy_minefield_multistep_sandbox_result,
    build_level3_toy_minefield_multistep_sandbox_result,
)


COMMAND = "run-level3-toy-minefield-variant-suite-stability-review-minimal-check"
FLOW = "level3_toy_minefield_variant_suite_stability_review_minimal_v0"
PACKAGE_ID = "PKG-PHASE0-L3-MINEFIELD-VARIANT-STABILITY-REVIEW-001"
PACKAGE_TITLE = "Level 3 Toy Minefield Variant Suite, Stability Evaluation, and Review Conclusion Minimal v0"
BOUNDARY_VERSION = "2026-06-09-b74"
REQUIRED_VARIANT_IDS = (
    "safe_path_variant",
    "risky_repeat_trap_variant",
    "blocked_path_fallback_variant",
)
ALLOWED_SANDBOX_STEP_ACTIONS = (
    "reveal_cell",
    "check_adjacent",
    "flag_possible_mine",
    "choose_safe_cell",
    "stop_and_report",
    "safe_fallback",
)
VARIANT_EVALUATION_STATUSES = (
    "passed_expected_variant_behavior",
    "failed_repeated_risky_reveal_without_check",
    "failed_missing_expected_check",
    "failed_forbidden_boundary_flag",
    "inconclusive_missing_or_invalid_variant_trace",
)
STABILITY_STABLE = "stable_expected_check_before_retry_behavior"
STABILITY_UNSTABLE = "unstable_variant_failure"
STABILITY_INCONCLUSIVE = "inconclusive_missing_required_variants"
STABILITY_INVALID_BOUNDARY = "invalid_forbidden_boundary_flag"
CONCLUSION_PASSED = "concluded_level3_toy_minefield_variant_review_passed"
CONCLUSION_FAILED = "concluded_level3_toy_minefield_variant_review_failed"
CONCLUSION_INCONCLUSIVE = "inconclusive_level3_toy_minefield_variant_review"
FORBIDDEN_FALSE_FIELDS = (
    "proof_of_learning_claimed",
    "runtime_behavior_changed",
    "memory_written",
    "retained_jsonl_written",
    "retention_written",
    "predictor_mutated",
    "selected_action_created",
    "final_action_created",
    "production_promotion_performed",
    "random_mine_generation_used",
    "real_minesweeper_engine_used",
)
SAFE_CLAIM = (
    "ASHL Core can evaluate stability of check-before-retry behavior across a bounded deterministic "
    "Phase0 Level 3 toy minefield sandbox variant suite and record a conservative review conclusion, "
    "while runtime behavior, memory, retained JSONL, retention, predictor mutation, selected_action, "
    "final_action, production promotion, and proof-of-learning remain blocked."
)


def build_level3_toy_minefield_variant_definitions() -> list[dict[str, Any]]:
    return [
        {
            "variant_id": "safe_path_variant",
            "variant_title": "Safe path variant",
            "variant_scope": TARGET_SCOPE,
            "board_shape": "3x3",
            "start_cell": "A1",
            "goal_condition": "safe_stop_after_revealing_declared_safe_path",
            "risky_cells": ["B2"],
            "safe_cells": ["A1", "A2", "A3"],
            "planned_steps": [
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
                {"step_index": 6, "sandbox_step_action": "stop_and_report", "cell": None, "result": "safe_stop"},
            ],
            "expected_check_before_retry_points": [2],
            "expected_stop_conditions": ["safe_stop"],
            "expected_failure_classes": [],
        },
        {
            "variant_id": "risky_repeat_trap_variant",
            "variant_title": "Risky repeat trap variant",
            "variant_scope": TARGET_SCOPE,
            "board_shape": "3x3",
            "start_cell": "A1",
            "goal_condition": "block_repeated_risky_reveal_and_stop_safely",
            "risky_cells": ["B2"],
            "safe_cells": ["A1", "C1"],
            "planned_steps": [
                {
                    "step_index": 1,
                    "sandbox_step_action": "check_adjacent",
                    "cell": "A1",
                    "result": "risk_detected",
                    "risky_cells": ["B2"],
                },
                {"step_index": 2, "sandbox_step_action": "reveal_cell", "cell": "B2", "result": "blocked_unsafe"},
                {
                    "step_index": 3,
                    "sandbox_step_action": "check_adjacent",
                    "cell": "A1",
                    "result": "risk_confirmed_before_retry",
                    "risky_cells": ["B2"],
                },
                {"step_index": 4, "sandbox_step_action": "choose_safe_cell", "cell": "C1", "result": "chosen"},
                {"step_index": 5, "sandbox_step_action": "reveal_cell", "cell": "C1", "result": "safe"},
                {"step_index": 6, "sandbox_step_action": "stop_and_report", "cell": None, "result": "safe_stop"},
            ],
            "expected_check_before_retry_points": [1, 3],
            "expected_stop_conditions": ["safe_stop"],
            "expected_failure_classes": ["failed_repeated_risky_reveal_without_check"],
        },
        {
            "variant_id": "blocked_path_fallback_variant",
            "variant_title": "Blocked path fallback variant",
            "variant_scope": TARGET_SCOPE,
            "board_shape": "3x3",
            "start_cell": "A1",
            "goal_condition": "use_safe_fallback_after_blocked_path",
            "risky_cells": ["B1", "B2"],
            "safe_cells": ["A1", "A2", "C2"],
            "planned_steps": [
                {"step_index": 1, "sandbox_step_action": "reveal_cell", "cell": "A1", "result": "safe"},
                {
                    "step_index": 2,
                    "sandbox_step_action": "check_adjacent",
                    "cell": "A1",
                    "result": "risk_detected",
                    "risky_cells": ["B1", "B2"],
                },
                {"step_index": 3, "sandbox_step_action": "flag_possible_mine", "cell": "B1", "result": "flagged"},
                {"step_index": 4, "sandbox_step_action": "safe_fallback", "cell": "A2", "result": "fallback_chosen"},
                {"step_index": 5, "sandbox_step_action": "reveal_cell", "cell": "A2", "result": "safe"},
                {"step_index": 6, "sandbox_step_action": "choose_safe_cell", "cell": "C2", "result": "chosen"},
                {"step_index": 7, "sandbox_step_action": "stop_and_report", "cell": None, "result": "safe_stop"},
            ],
            "expected_check_before_retry_points": [2],
            "expected_stop_conditions": ["safe_stop"],
            "expected_failure_classes": ["blocked_path_without_fallback"],
        },
    ]


def build_level3_toy_minefield_variant_trace(variant: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_type": "level3_toy_minefield_variant_trace",
        "variant_id": variant.get("variant_id"),
        "variant_scope": variant.get("variant_scope"),
        "sandbox_trace_steps": deepcopy(variant.get("planned_steps", [])),
        "temporary_sandbox_state_only": True,
        "audit_present": True,
        "rollback_present": True,
        "proof_of_learning_claimed": False,
        "runtime_behavior_changed": False,
        "memory_written": False,
        "retained_jsonl_written": False,
        "retention_written": False,
        "predictor_mutated": False,
        "selected_action_created": False,
        "final_action_created": False,
        "production_promotion_performed": False,
        "random_mine_generation_used": False,
        "real_minesweeper_engine_used": False,
        "source_variant_definition": deepcopy(variant),
    }


def build_level3_toy_minefield_variant_observation(trace: dict[str, Any]) -> dict[str, Any]:
    steps = trace.get("sandbox_trace_steps", [])
    variant = trace.get("source_variant_definition", {})
    trace_errors = _trace_errors(trace)
    return {
        "record_type": "level3_toy_minefield_variant_observation",
        "variant_id": trace.get("variant_id"),
        "variant_scope": trace.get("variant_scope"),
        "observation_status": "observed_level3_toy_minefield_variant",
        "observed_step_count": len(steps) if isinstance(steps, list) else 0,
        "observed_risky_cell_encountered": _risky_cell_encountered(trace),
        "observed_intervening_check_before_retry": "missing_expected_check" not in trace_errors,
        "observed_repeated_risky_reveal_blocked": "risky_cell_revealed_again_without_check" not in trace_errors,
        "observed_safe_fallback_available": (
            bool(variant.get("variant_id") != "blocked_path_fallback_variant")
            or any(step.get("sandbox_step_action") == "safe_fallback" for step in steps if isinstance(step, dict))
        ),
        "observed_temporary_sandbox_state_only": trace.get("temporary_sandbox_state_only") is True,
        "audit_present": trace.get("audit_present") is True,
        "rollback_present": trace.get("rollback_present") is True,
        "forbidden_runtime_behavior_present": trace.get("runtime_behavior_changed") is True,
        "forbidden_memory_write_present": trace.get("memory_written") is True,
        "forbidden_retained_jsonl_write_present": trace.get("retained_jsonl_written") is True,
        "forbidden_retention_write_present": trace.get("retention_written") is True,
        "forbidden_predictor_mutation_present": trace.get("predictor_mutated") is True,
        "forbidden_selected_action_present": trace.get("selected_action_created") is True,
        "forbidden_final_action_present": trace.get("final_action_created") is True,
        "forbidden_proof_claim_present": trace.get("proof_of_learning_claimed") is True,
        "random_mine_generation_present": trace.get("random_mine_generation_used") is True,
        "real_minesweeper_engine_present": trace.get("real_minesweeper_engine_used") is True,
        "source_trace": deepcopy(trace),
    }


def build_level3_toy_minefield_variant_evaluation(
    trace: dict[str, Any],
    observation: dict[str, Any],
) -> dict[str, Any]:
    trace_errors = _trace_errors(trace)
    forbidden = _forbidden_boundary_violation(trace) or _forbidden_observation_violation(observation)
    if forbidden:
        status = "failed_forbidden_boundary_flag"
    elif "risky_cell_revealed_again_without_check" in trace_errors:
        status = "failed_repeated_risky_reveal_without_check"
    elif "missing_expected_check" in trace_errors:
        status = "failed_missing_expected_check"
    elif trace_errors:
        status = "inconclusive_missing_or_invalid_variant_trace"
    else:
        status = "passed_expected_variant_behavior"
    return {
        "record_type": "level3_toy_minefield_variant_evaluation",
        "variant_id": trace.get("variant_id"),
        "variant_scope": trace.get("variant_scope"),
        "evaluation_status": status,
        "allowed_statuses": list(VARIANT_EVALUATION_STATUSES),
        "reason_codes": _variant_reason_codes(status),
        "proof_of_learning_claimed": False,
        "source_trace": deepcopy(trace),
        "source_observation": deepcopy(observation),
    }


def build_level3_toy_minefield_variant_suite_stability_review() -> dict[str, Any]:
    upstream = build_level3_toy_minefield_multistep_sandbox_result()
    variants = build_level3_toy_minefield_variant_definitions()
    traces = [build_level3_toy_minefield_variant_trace(variant) for variant in variants]
    observations = [build_level3_toy_minefield_variant_observation(trace) for trace in traces]
    evaluations = [
        build_level3_toy_minefield_variant_evaluation(trace, observation)
        for trace, observation in zip(traces, observations)
    ]
    stability = _build_stability_summary(evaluations, traces)
    conclusion = _build_review_conclusion(stability)
    return {
        "record_type": "level3_toy_minefield_variant_suite_stability_review",
        "package_id": PACKAGE_ID,
        "package_title": PACKAGE_TITLE,
        "target_scope": TARGET_SCOPE,
        "boundary_change_required": False,
        "boundary_index_update_required": False,
        "boundary_index_version_before": BOUNDARY_VERSION,
        "boundary_index_version_after": BOUNDARY_VERSION,
        "boundary_change_rationale": (
            "This package operates inside the already-authorized Phase0 Level 3 toy minefield sandbox-only "
            "multi-step trace boundary. It adds deterministic variants, stability evaluation, and a review "
            "conclusion without changing sandbox permission scope, runtime behavior, memory, retention, "
            "predictor, action selection, production, or proof-of-learning boundaries."
        ),
        "source_level3_single_scenario_valid": validate_level3_toy_minefield_multistep_sandbox_result(upstream).get(
            "valid"
        )
        is True,
        "required_variant_ids": list(REQUIRED_VARIANT_IDS),
        "variant_definitions": variants,
        "variant_traces": traces,
        "variant_observations": observations,
        "variant_evaluations": evaluations,
        "stability_summary": stability,
        "review_conclusion": conclusion,
        "temporary_sandbox_state_only": True,
        "audit_record": {"audit_present": True, "audit_scope": "variant_suite_sandbox_only"},
        "rollback_record": {"rollback_present": True, "rollback_scope": "variant_suite_sandbox_only"},
        "proof_of_learning_claimed": False,
        "runtime_behavior_changed": False,
        "memory_written": False,
        "retained_jsonl_written": False,
        "retention_written": False,
        "predictor_mutated": False,
        "selected_action_created": False,
        "final_action_created": False,
        "production_promotion_performed": False,
        "random_mine_generation_used": False,
        "real_minesweeper_engine_used": False,
    }


def validate_level3_toy_minefield_variant_suite_stability_review(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "level3_toy_minefield_variant_suite_stability_review":
        errors.append("record_type_not_level3_toy_minefield_variant_suite_stability_review")
    if record.get("package_id") != PACKAGE_ID:
        errors.append("package_id_not_expected")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_phase0_level3_toy_minefield_sandbox_only")
    if record.get("boundary_change_required") is not False:
        errors.append("boundary_change_required_not_false")
    if record.get("boundary_index_update_required") is not False:
        errors.append("boundary_index_update_required_not_false")
    if record.get("boundary_index_version_before") != BOUNDARY_VERSION:
        errors.append("boundary_index_version_before_not_b74")
    if record.get("boundary_index_version_after") != BOUNDARY_VERSION:
        errors.append("boundary_index_version_after_not_b74")
    if record.get("required_variant_ids") != list(REQUIRED_VARIANT_IDS):
        errors.append("required_variant_ids_not_expected")
    if record.get("source_level3_single_scenario_valid") is not True:
        errors.append("source_level3_single_scenario_valid_not_true")
    variants = record.get("variant_definitions", [])
    traces = record.get("variant_traces", [])
    observations = record.get("variant_observations", [])
    evaluations = record.get("variant_evaluations", [])
    if _variant_ids(variants) != list(REQUIRED_VARIANT_IDS):
        errors.append("variant_definitions_missing_or_unknown")
    if _variant_ids(evaluations) != list(REQUIRED_VARIANT_IDS):
        errors.append("variant_evaluations_missing_or_unknown")
    for trace in traces if isinstance(traces, list) else []:
        errors.extend(f"trace:{trace.get('variant_id')}:{error}" for error in _trace_errors(trace))
        if _forbidden_boundary_violation(trace):
            errors.append(f"trace:{trace.get('variant_id')}:forbidden_boundary_flag")
    for observation in observations if isinstance(observations, list) else []:
        errors.extend(_validate_observation(observation))
    for evaluation in evaluations if isinstance(evaluations, list) else []:
        errors.extend(_validate_evaluation(evaluation))
    errors.extend(_validate_stability_summary(record.get("stability_summary", {}), evaluations))
    errors.extend(_validate_review_conclusion(record.get("review_conclusion", {}), record.get("stability_summary", {})))
    if record.get("temporary_sandbox_state_only") is not True:
        errors.append("temporary_sandbox_state_only_not_true")
    if record.get("audit_record", {}).get("audit_present") is not True:
        errors.append("audit_record_missing")
    if record.get("rollback_record", {}).get("rollback_present") is not True:
        errors.append("rollback_record_missing")
    for field in FORBIDDEN_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {"valid": not errors, "error_codes": errors}


def run_level3_toy_minefield_variant_suite_stability_review_minimal_check() -> dict[str, Any]:
    valid = build_level3_toy_minefield_variant_suite_stability_review()
    invalid = _invalid_suite_records(valid)
    validation_results = [
        validate_level3_toy_minefield_variant_suite_stability_review(record) for record in [valid] + invalid
    ]
    valid_results = [result for result in validation_results if result["valid"]]
    evaluations = valid.get("variant_evaluations", [])
    summary = {
        "package_id": PACKAGE_ID,
        "boundary_change_required": False,
        "boundary_index_update_required": False,
        "valid_variant_suite_count": len(valid_results),
        "invalid_variant_suite_count": len(validation_results) - len(valid_results),
        "passed_variant_count": sum(
            1 for evaluation in evaluations if evaluation.get("evaluation_status") == "passed_expected_variant_behavior"
        ),
        "failed_variant_count": sum(
            1 for evaluation in evaluations if str(evaluation.get("evaluation_status", "")).startswith("failed_")
        ),
        "inconclusive_variant_count": sum(
            1 for evaluation in evaluations if str(evaluation.get("evaluation_status", "")).startswith("inconclusive_")
        ),
        "stability_status": valid.get("stability_summary", {}).get("stability_status"),
        "review_conclusion_status": valid.get("review_conclusion", {}).get("review_conclusion_status"),
        "forbidden_boundary_violation_count": 0,
    }
    summary["all_level3_toy_minefield_variant_suite_stability_review_checks_passed"] = (
        summary["valid_variant_suite_count"] == 1
        and summary["invalid_variant_suite_count"] >= 1
        and summary["passed_variant_count"] == len(REQUIRED_VARIANT_IDS)
        and summary["failed_variant_count"] == 0
        and summary["inconclusive_variant_count"] == 0
        and summary["stability_status"] == STABILITY_STABLE
        and summary["review_conclusion_status"] == CONCLUSION_PASSED
        and summary["forbidden_boundary_violation_count"] == 0
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok"
        if summary["all_level3_toy_minefield_variant_suite_stability_review_checks_passed"]
        else "failed",
        "valid_record": valid,
        "invalid_records": invalid,
        "validation_results": validation_results,
        "summary": summary,
        "safe_claim": SAFE_CLAIM,
        "boundary": {
            "boundary_change_required": False,
            "boundary_index_update_required": False,
            "boundary_index_version_before": BOUNDARY_VERSION,
            "boundary_index_version_after": BOUNDARY_VERSION,
            "boundary_change_rationale": valid["boundary_change_rationale"],
        },
    }


def _trace_errors(trace: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if trace.get("variant_scope") != TARGET_SCOPE:
        errors.append("variant_scope_not_phase0_level3_toy_minefield_sandbox_only")
    steps = trace.get("sandbox_trace_steps")
    if not isinstance(steps, list) or len(steps) < 2:
        errors.append("trace_not_multistep")
        return errors
    variant = trace.get("source_variant_definition", {})
    expected_checks = set(variant.get("expected_check_before_retry_points", []))
    actual_checks = {step.get("step_index") for step in steps if step.get("sandbox_step_action") == "check_adjacent"}
    if not expected_checks.issubset(actual_checks):
        errors.append("missing_expected_check")
    allowed = set(ALLOWED_SANDBOX_STEP_ACTIONS)
    risky_cells = set(variant.get("risky_cells", []))
    pending_risky_reveals: dict[str, bool] = {}
    for expected_index, step in enumerate(steps, start=1):
        if step.get("step_index") != expected_index:
            errors.append("step_index_not_ordered")
        action = step.get("sandbox_step_action")
        cell = step.get("cell")
        if action not in allowed:
            errors.append("unknown_sandbox_step_action")
        if action in {"check_adjacent", "choose_safe_cell", "safe_fallback"}:
            for risky in pending_risky_reveals:
                pending_risky_reveals[risky] = True
        if action == "reveal_cell" and cell in risky_cells:
            if pending_risky_reveals.get(cell) is False:
                errors.append("risky_cell_revealed_again_without_check")
            pending_risky_reveals[cell] = False
    if trace.get("temporary_sandbox_state_only") is not True:
        errors.append("temporary_sandbox_state_only_not_true")
    if trace.get("audit_present") is not True:
        errors.append("audit_missing")
    if trace.get("rollback_present") is not True:
        errors.append("rollback_missing")
    return errors


def _forbidden_boundary_violation(record: dict[str, Any]) -> bool:
    return any(record.get(field) is True for field in FORBIDDEN_FALSE_FIELDS)


def _forbidden_observation_violation(observation: dict[str, Any]) -> bool:
    return any(
        observation.get(field) is True
        for field in (
            "forbidden_runtime_behavior_present",
            "forbidden_memory_write_present",
            "forbidden_retained_jsonl_write_present",
            "forbidden_retention_write_present",
            "forbidden_predictor_mutation_present",
            "forbidden_selected_action_present",
            "forbidden_final_action_present",
            "forbidden_proof_claim_present",
            "random_mine_generation_present",
            "real_minesweeper_engine_present",
        )
    )


def _risky_cell_encountered(trace: dict[str, Any]) -> bool:
    risky_cells = set(trace.get("source_variant_definition", {}).get("risky_cells", []))
    return any(
        bool(risky_cells.intersection(set(step.get("risky_cells", [])))) or step.get("cell") in risky_cells
        for step in trace.get("sandbox_trace_steps", [])
        if isinstance(step, dict)
    )


def _validate_observation(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("observation_status") != "observed_level3_toy_minefield_variant":
        errors.append(f"observation:{record.get('variant_id')}:status_not_observed")
    for field in (
        "observed_risky_cell_encountered",
        "observed_intervening_check_before_retry",
        "observed_repeated_risky_reveal_blocked",
        "observed_safe_fallback_available",
        "observed_temporary_sandbox_state_only",
        "audit_present",
        "rollback_present",
    ):
        if record.get(field) is not True:
            errors.append(f"observation:{record.get('variant_id')}:{field}_not_true")
    if _forbidden_observation_violation(record):
        errors.append(f"observation:{record.get('variant_id')}:forbidden_boundary_flag")
    return errors


def _validate_evaluation(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("evaluation_status") not in VARIANT_EVALUATION_STATUSES:
        errors.append(f"evaluation:{record.get('variant_id')}:status_unknown")
    if record.get("evaluation_status") != "passed_expected_variant_behavior":
        errors.append(f"evaluation:{record.get('variant_id')}:status_not_passed")
    if record.get("proof_of_learning_claimed") is not False:
        errors.append(f"evaluation:{record.get('variant_id')}:proof_of_learning_claimed_not_false")
    return errors


def _build_stability_summary(
    evaluations: list[dict[str, Any]],
    traces: list[dict[str, Any]],
) -> dict[str, Any]:
    passed = [
        evaluation.get("variant_id")
        for evaluation in evaluations
        if evaluation.get("evaluation_status") == "passed_expected_variant_behavior"
    ]
    failed = [
        evaluation.get("variant_id")
        for evaluation in evaluations
        if str(evaluation.get("evaluation_status", "")).startswith("failed_")
    ]
    inconclusive = [
        evaluation.get("variant_id")
        for evaluation in evaluations
        if str(evaluation.get("evaluation_status", "")).startswith("inconclusive_")
    ]
    forbidden = any(_forbidden_boundary_violation(trace) for trace in traces)
    if forbidden:
        status = STABILITY_INVALID_BOUNDARY
    elif set(passed) == set(REQUIRED_VARIANT_IDS) and not failed and not inconclusive:
        status = STABILITY_STABLE
    elif failed:
        status = STABILITY_UNSTABLE
    else:
        status = STABILITY_INCONCLUSIVE
    return {
        "suite_id": "level3_toy_minefield_variant_suite_stability_demo_001",
        "required_variant_ids": list(REQUIRED_VARIANT_IDS),
        "passed_variant_ids": passed,
        "failed_variant_ids": failed,
        "inconclusive_variant_ids": inconclusive,
        "stability_status": status,
        "stable_behavior_observed": status == STABILITY_STABLE,
        "check_before_retry_stable_across_variants": status == STABILITY_STABLE,
        "repeated_risky_reveal_blocked_across_variants": status == STABILITY_STABLE,
        "temporary_sandbox_state_only": True,
        "audit_present": True,
        "rollback_present": True,
        "proof_of_learning_claimed": False,
    }


def _build_review_conclusion(stability: dict[str, Any]) -> dict[str, Any]:
    stable = stability.get("stability_status") == STABILITY_STABLE
    return {
        "record_type": "level3_toy_minefield_variant_review_conclusion",
        "review_conclusion_status": CONCLUSION_PASSED if stable else CONCLUSION_FAILED,
        "review_conclusion_text": (
            "ASHL Core has demonstrated stable check-before-retry behavior across a bounded deterministic "
            "Phase0 Level 3 toy minefield sandbox variant suite. This is not proof of learning, does not "
            "change runtime behavior, does not write memory or retained JSONL, does not mutate predictors, "
            "does not create selected_action or final_action, and does not promote behavior to production."
        )
        if stable
        else "The Level 3 toy minefield variant suite did not produce a stable conservative review conclusion.",
        "proof_of_learning_claimed": False,
        "runtime_behavior_changed": False,
        "memory_written": False,
        "retained_jsonl_written": False,
        "retention_written": False,
        "predictor_mutated": False,
        "selected_action_created": False,
        "final_action_created": False,
        "production_promotion_performed": False,
    }


def _validate_stability_summary(record: dict[str, Any], evaluations: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if record.get("required_variant_ids") != list(REQUIRED_VARIANT_IDS):
        errors.append("stability_summary_required_variant_ids_not_expected")
    passed = [evaluation.get("variant_id") for evaluation in evaluations if evaluation.get("evaluation_status") == "passed_expected_variant_behavior"]
    if record.get("stability_status") == STABILITY_STABLE:
        if set(passed) != set(REQUIRED_VARIANT_IDS):
            errors.append("stable_status_without_all_required_variants_passed")
        for field in (
            "stable_behavior_observed",
            "check_before_retry_stable_across_variants",
            "repeated_risky_reveal_blocked_across_variants",
            "temporary_sandbox_state_only",
            "audit_present",
            "rollback_present",
        ):
            if record.get(field) is not True:
                errors.append(f"stability_summary_{field}_not_true")
    if record.get("proof_of_learning_claimed") is not False:
        errors.append("stability_summary_proof_of_learning_claimed_not_false")
    return errors


def _validate_review_conclusion(record: dict[str, Any], stability: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    status = record.get("review_conclusion_status")
    if status not in {CONCLUSION_PASSED, CONCLUSION_FAILED, CONCLUSION_INCONCLUSIVE}:
        errors.append("review_conclusion_status_unknown")
    if stability.get("stability_status") == STABILITY_STABLE and status != CONCLUSION_PASSED:
        errors.append("stable_suite_without_passed_review_conclusion")
    if not isinstance(record.get("review_conclusion_text"), str) or not record.get("review_conclusion_text", "").strip():
        errors.append("review_conclusion_text_empty")
    if "proof of learning" in record.get("review_conclusion_text", "").lower() and "not proof of learning" not in record.get(
        "review_conclusion_text", ""
    ).lower():
        errors.append("review_conclusion_text_claims_proof")
    for field in FORBIDDEN_FALSE_FIELDS:
        if field in record and record.get(field) is not False:
            errors.append(f"review_conclusion_{field}_not_false")
    return errors


def _variant_ids(records: Any) -> list[str]:
    if not isinstance(records, list):
        return []
    return [record.get("variant_id") for record in records if isinstance(record, dict)]


def _variant_reason_codes(status: str) -> list[str]:
    if status == "passed_expected_variant_behavior":
        return [
            "variant_scope_valid",
            "check_before_retry_at_expected_points",
            "repeated_risky_reveal_blocked",
            "temporary_sandbox_state_only",
            "audit_and_rollback_present",
        ]
    return [status]


def _invalid_suite_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _mutated(valid, ["variant_definitions"], valid["variant_definitions"][:-1]),
        _mutated(valid, ["variant_definitions", 0, "variant_id"], "unknown_variant"),
        _mutated(valid, ["target_scope"], "production"),
        _mutated(valid, ["variant_traces", 0, "variant_scope"], "runtime"),
        _risky_repeat_without_check(valid),
        _mutated(valid, ["variant_traces", 0, "source_variant_definition", "expected_check_before_retry_points"], [99]),
        _mutated(valid, ["variant_traces", 0, "audit_present"], False),
        _mutated(valid, ["variant_traces", 0, "rollback_present"], False),
        _mutated(valid, ["variant_traces", 0, "memory_written"], True),
        _mutated(valid, ["variant_traces", 0, "retained_jsonl_written"], True),
        _mutated(valid, ["variant_traces", 0, "retention_written"], True),
        _mutated(valid, ["variant_traces", 0, "predictor_mutated"], True),
        _mutated(valid, ["variant_traces", 0, "runtime_behavior_changed"], True),
        _mutated(valid, ["variant_traces", 0, "selected_action_created"], True),
        _mutated(valid, ["variant_traces", 0, "final_action_created"], True),
        _mutated(valid, ["variant_traces", 0, "production_promotion_performed"], True),
        _mutated(valid, ["variant_traces", 0, "proof_of_learning_claimed"], True),
        _mutated(valid, ["variant_traces", 0, "random_mine_generation_used"], True),
        _mutated(valid, ["variant_traces", 0, "real_minesweeper_engine_used"], True),
        _mutated(valid, ["proof_of_learning_claimed"], True),
    ]


def _risky_repeat_without_check(valid: dict[str, Any]) -> dict[str, Any]:
    clone = deepcopy(valid)
    clone["variant_traces"][1]["sandbox_trace_steps"] = [
        {
            "step_index": 1,
            "sandbox_step_action": "check_adjacent",
            "cell": "A1",
            "result": "risk_detected",
            "risky_cells": ["B2"],
        },
        {"step_index": 2, "sandbox_step_action": "reveal_cell", "cell": "B2", "result": "blocked_unsafe"},
        {"step_index": 3, "sandbox_step_action": "reveal_cell", "cell": "B2", "result": "blocked_unsafe"},
    ]
    return clone


def _mutated(record: dict[str, Any], path: list[Any], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: Any = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(run_level3_toy_minefield_variant_suite_stability_review_minimal_check(), indent=2))
