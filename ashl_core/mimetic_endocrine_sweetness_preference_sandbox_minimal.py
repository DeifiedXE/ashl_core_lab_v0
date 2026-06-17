"""Sandbox sweetness preference traces using mimetic dopamine-like responses."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .mimetic_endocrine_signal_schema import KNOWN_SIGNALS, validate_signal_record


COMMAND = "run-mimetic-endocrine-sweetness-preference-sandbox-minimal-check"
FLOW = "mimetic_endocrine_sweetness_preference_sandbox_minimal_v0"
PACKAGE_ID = "PKG-Phase0-MimeticEndocrineSweetnessPreferenceSandbox-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b107"
BOUNDARY_INDEX_AFTER = "2026-06-09-b108"
SANDBOX_ID = "mimetic_endocrine_sweetness_preference_sandbox_v0"
BASELINE_DOPAMINE = 0.2

BLOCKED_FLAGS = (
    "free_choice_added",
    "pathfinding_used",
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_preference_written",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "endocrine_runtime_state_persisted",
    "biological_hormone_claim_allowed",
    "subjective_pleasure_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
    "proof_of_learning_claim_allowed",
)


def build_mimetic_endocrine_sweetness_preference_sandbox_record() -> dict[str, Any]:
    stage0 = _build_stage0_trace()
    stage1 = _build_stage1_trace()
    stage2 = _build_stage2_trace()
    return {
        "record_type": "mimetic_endocrine_sweetness_preference_sandbox",
        "record_version": "v0",
        "preference_status": "completed_sandbox_sweetness_preference_trace",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "sandbox_context": {
            "sandbox_id": SANDBOX_ID,
            "sandbox_scope": "sandbox_only",
            "scenario_count": 3,
            "fixed_choice_fixture": True,
            "free_choice_added": False,
            "pathfinding_used": False,
            "production_behavior_changed": False,
        },
        "stage0_candy_calibration": stage0,
        "stage1_two_candy_paths": stage1,
        "stage2_obstacle_sweeter_path": stage2,
        "endocrine_response_summary": {
            "dopamine_like_response_trace_count": 4,
            "valid_dopamine_like_response_trace_count": 4,
            "stage0_calibration_completed": True,
            "stage0_each_candy_eaten_once": True,
            "stage1_sweeter_response_higher": True,
            "stage1_irreversible_choice_enforced": True,
            "stage2_obstacle_penalty_applied": True,
            "stage2_irreversible_choice_enforced": True,
            "stage2_sweeter_net_tendency_still_higher": True,
            "response_trace_only": True,
            "runtime_endocrine_state_persisted": False,
        },
        "preference_preview": {
            "stage1_preferred_path": "right_sweeter_candy",
            "stage1_reason": "sweeter candy has higher dopamine_like response value",
            "stage2_preferred_path": "right_mild_obstacle_sweeter_candy",
            "stage2_reason": "sweeter candy remains higher after mild obstacle cost",
            "choice_is_irreversible": True,
            "both_paths_consumed_after_choice": False,
            "preference_changed_by_sweetness": True,
            "obstacle_can_be_overcome_by_sweetness_preview": True,
            "action_selection_applied": False,
            "free_choice_applied": False,
        },
        "human_summary": {
            "what_was_tested": "A calibration stage and two irreversible controlled sandbox sweetness choices were evaluated with mimetic dopamine-like response traces.",
            "stage0_result": "The calibration stage let Qingyin taste each candy type once, producing one ordinary-candy and one sweeter-candy response trace.",
            "stage1_result": "When both paths were unobstructed, the calibrated sweeter candy response produced the stronger preference preview; only the chosen path was consumed.",
            "stage2_result": "When the sweeter candy had a mild obstacle cost, the sweeter path still had the higher net tendency preview; only the chosen path was consumed.",
            "what_is_blocked": "Free choice, pathfinding, production behavior, memory writes, retention writes, predictor mutation, persistent endocrine state, biological hormone claims, subjective pleasure claims, and proof claims remain blocked.",
            "plain_result": "The sandbox can show sweetness-sensitive mimetic endocrine response traces without turning them into autonomous action.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_mimetic_endocrine_sweetness_preference_sandbox_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "mimetic_endocrine_sweetness_preference_sandbox",
        "record_version": "v0",
        "preference_status": "completed_sandbox_sweetness_preference_trace",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    context = _dict(record.get("sandbox_context"), errors, "sandbox_context_missing")
    expected_context = {
        "sandbox_id": SANDBOX_ID,
        "sandbox_scope": "sandbox_only",
        "scenario_count": 3,
        "fixed_choice_fixture": True,
        "free_choice_added": False,
        "pathfinding_used": False,
        "production_behavior_changed": False,
    }
    for field, value in expected_context.items():
        if context.get(field) != value:
            errors.append(f"sandbox_context_{field}_not_expected")

    stage0 = _dict(record.get("stage0_candy_calibration"), errors, "stage0_missing")
    stage0_result = _validate_stage0(stage0)
    errors.extend(stage0_result["error_codes"])

    stage1 = _dict(record.get("stage1_two_candy_paths"), errors, "stage1_missing")
    stage1_result = _validate_stage1(stage1)
    errors.extend(stage1_result["error_codes"])

    stage2 = _dict(record.get("stage2_obstacle_sweeter_path"), errors, "stage2_missing")
    stage2_result = _validate_stage2(stage2)
    errors.extend(stage2_result["error_codes"])

    summary = _dict(record.get("endocrine_response_summary"), errors, "endocrine_response_summary_missing")
    expected_summary = {
        "dopamine_like_response_trace_count": 4,
        "valid_dopamine_like_response_trace_count": 4,
        "stage0_calibration_completed": True,
        "stage0_each_candy_eaten_once": True,
        "stage1_sweeter_response_higher": True,
        "stage1_irreversible_choice_enforced": True,
        "stage2_obstacle_penalty_applied": True,
        "stage2_irreversible_choice_enforced": True,
        "stage2_sweeter_net_tendency_still_higher": True,
        "response_trace_only": True,
        "runtime_endocrine_state_persisted": False,
    }
    for field, value in expected_summary.items():
        if summary.get(field) != value:
            errors.append(f"endocrine_response_summary_{field}_not_expected")

    preview = _dict(record.get("preference_preview"), errors, "preference_preview_missing")
    expected_preview = {
        "stage1_preferred_path": "right_sweeter_candy",
        "stage2_preferred_path": "right_mild_obstacle_sweeter_candy",
        "choice_is_irreversible": True,
        "both_paths_consumed_after_choice": False,
        "preference_changed_by_sweetness": True,
        "obstacle_can_be_overcome_by_sweetness_preview": True,
        "action_selection_applied": False,
        "free_choice_applied": False,
    }
    for field, value in expected_preview.items():
        if preview.get(field) != value:
            errors.append(f"preference_preview_{field}_not_expected")
    for field in ("stage1_reason", "stage2_reason"):
        if not isinstance(preview.get(field), str) or not preview.get(field).strip():
            errors.append(f"preference_preview_{field}_empty")

    human_summary = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in ("what_was_tested", "stage0_result", "stage1_result", "stage2_result", "what_is_blocked", "plain_result"):
        if not isinstance(human_summary.get(field), str) or not human_summary.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    blocked_flags = _dict(record.get("blocked_flags"), errors, "blocked_flags_missing")
    for field in BLOCKED_FLAGS:
        if blocked_flags.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "stage0_calibration_completed": stage0_result["calibration_completed"],
        "stage0_each_candy_eaten_once": stage0_result["each_candy_eaten_once"],
        "stage1_sweeter_response_higher": stage1_result["sweeter_response_higher"],
        "stage1_irreversible_choice_enforced": stage1_result["irreversible_choice_enforced"],
        "stage2_obstacle_penalty_applied": stage2_result["obstacle_penalty_applied"],
        "stage2_irreversible_choice_enforced": stage2_result["irreversible_choice_enforced"],
        "stage2_sweeter_net_tendency_still_higher": stage2_result["sweeter_net_tendency_still_higher"],
        "valid_dopamine_like_response_trace_count": stage0_result["valid_trace_count"]
        + stage1_result["valid_trace_count"]
        + stage2_result["valid_trace_count"],
        "preference_changed_by_sweetness": preview.get("preference_changed_by_sweetness") is True,
        "obstacle_can_be_overcome_by_sweetness_preview": preview.get("obstacle_can_be_overcome_by_sweetness_preview") is True,
        "free_choice_blocked": context.get("free_choice_added") is False and blocked_flags.get("free_choice_added") is False,
        "pathfinding_blocked": context.get("pathfinding_used") is False and blocked_flags.get("pathfinding_used") is False,
        "production_behavior_blocked": blocked_flags.get("production_behavior_changed") is False,
        "memory_write_blocked": blocked_flags.get("memory_write_performed") is False
        and blocked_flags.get("retained_jsonl_write_performed") is False,
        "retention_blocked": blocked_flags.get("retention_write_performed") is False,
        "predictor_mutation_blocked": blocked_flags.get("predictor_read_enabled") is False
        and blocked_flags.get("predictor_influence_enabled") is False
        and blocked_flags.get("predictor_mutation_performed") is False,
        "persistent_endocrine_state_blocked": blocked_flags.get("endocrine_runtime_state_persisted") is False,
        "subjective_claim_blocked": blocked_flags.get("subjective_pleasure_claim_allowed") is False
        and blocked_flags.get("biological_hormone_claim_allowed") is False,
        "proof_claim_blocked": blocked_flags.get("proof_of_learning_claim_allowed") is False
        and blocked_flags.get("autonomous_learning_claim_allowed") is False
        and blocked_flags.get("autonomous_action_claim_allowed") is False,
    }


def run_mimetic_endocrine_sweetness_preference_sandbox_minimal_check() -> dict[str, Any]:
    valid_record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
    valid_result = validate_mimetic_endocrine_sweetness_preference_sandbox_record(valid_record)
    invalid_results = [
        validate_mimetic_endocrine_sweetness_preference_sandbox_record(item)
        for item in _invalid_records(valid_record)
    ]
    summary = {
        "valid_sweetness_preference_sandbox_count": 1 if valid_result["valid"] else 0,
        "invalid_sweetness_preference_sandbox_count": sum(1 for result in invalid_results if not result["valid"]),
        "stage0_calibration_completed_count": 1 if valid_result["stage0_calibration_completed"] else 0,
        "stage0_each_candy_eaten_once_count": 1 if valid_result["stage0_each_candy_eaten_once"] else 0,
        "stage1_sweeter_response_higher_count": 1 if valid_result["stage1_sweeter_response_higher"] else 0,
        "stage1_irreversible_choice_enforced_count": 1 if valid_result["stage1_irreversible_choice_enforced"] else 0,
        "stage2_obstacle_penalty_applied_count": 1 if valid_result["stage2_obstacle_penalty_applied"] else 0,
        "stage2_irreversible_choice_enforced_count": 1 if valid_result["stage2_irreversible_choice_enforced"] else 0,
        "stage2_sweeter_net_tendency_still_higher_count": 1 if valid_result["stage2_sweeter_net_tendency_still_higher"] else 0,
        "valid_dopamine_like_response_trace_total": valid_result["valid_dopamine_like_response_trace_count"],
        "preference_changed_by_sweetness_count": 1 if valid_result["preference_changed_by_sweetness"] else 0,
        "obstacle_can_be_overcome_by_sweetness_preview_count": 1 if valid_result["obstacle_can_be_overcome_by_sweetness_preview"] else 0,
        "free_choice_blocked_count": 1 if valid_result["free_choice_blocked"] else 0,
        "pathfinding_blocked_count": 1 if valid_result["pathfinding_blocked"] else 0,
        "production_behavior_blocked_count": 1 if valid_result["production_behavior_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "persistent_endocrine_state_blocked_count": 1 if valid_result["persistent_endocrine_state_blocked"] else 0,
        "subjective_claim_blocked_count": 1 if valid_result["subjective_claim_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_sweetness_preference_sandbox_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_sweetness_preference_sandbox_count"] == 51
        and summary["valid_dopamine_like_response_trace_total"] == 4
        and summary["stage0_each_candy_eaten_once_count"] == 1
        and summary["stage1_sweeter_response_higher_count"] == 1
        and summary["stage1_irreversible_choice_enforced_count"] == 1
        and summary["stage2_irreversible_choice_enforced_count"] == 1
        and summary["stage2_sweeter_net_tendency_still_higher_count"] == 1
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_sweetness_preference_sandbox_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Adds sandbox-only sweetness-sensitive mimetic endocrine response traces and preference preview.",
        },
        "valid_record": valid_record,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
    }


def _build_stage0_trace() -> dict[str, Any]:
    ordinary = _path_response(
        "stage0_ordinary_candy_calibration",
        "ordinary_candy_calibration",
        sweetness=0.4,
        obstacle_cost=0.0,
        tick=1,
    )
    sweeter = _path_response(
        "stage0_sweeter_candy_calibration",
        "sweeter_candy_calibration",
        sweetness=0.8,
        obstacle_cost=0.0,
        tick=2,
    )
    return {
        "stage_id": "stage0_candy_calibration",
        "stage_goal": "taste each candy type once before irreversible path choices",
        "calibration_trials": [ordinary, sweeter],
        "ordinary_candy_eaten_count": 1,
        "sweeter_candy_eaten_count": 1,
        "each_candy_eaten_once": True,
        "choice_required": False,
        "action_selection_applied": False,
    }


def _build_stage1_trace() -> dict[str, Any]:
    left = _path_candidate("left_candy", sweetness=0.4, obstacle_cost=0.0)
    right = _path_candidate("right_sweeter_candy", sweetness=0.8, obstacle_cost=0.0)
    actual = _path_response("stage1_chosen_right_sweeter_candy", "right_sweeter_candy", sweetness=0.8, obstacle_cost=0.0, tick=3)
    return {
        "stage_id": "stage1_two_paths_both_candy",
        "stage_goal": "choose one of two unobstructed candy paths after calibration",
        "choice_candidates": [left, right],
        "preferred_path": "right_sweeter_candy",
        "actual_consumed_path": actual,
        "actual_consumed_path_count": 1,
        "unchosen_path_consumed": False,
        "return_after_choice_allowed": False,
        "irreversible_choice_enforced": True,
        "sweeter_response_higher": right["expected_dopamine_like_response_value"] > left["expected_dopamine_like_response_value"],
        "action_selection_applied": False,
    }


def _build_stage2_trace() -> dict[str, Any]:
    left = _path_candidate("left_easy_candy", sweetness=0.4, obstacle_cost=0.0)
    right = _path_candidate("right_mild_obstacle_sweeter_candy", sweetness=0.8, obstacle_cost=0.15)
    actual = _path_response(
        "stage2_chosen_right_mild_obstacle_sweeter_candy",
        "right_mild_obstacle_sweeter_candy",
        sweetness=0.8,
        obstacle_cost=0.15,
        tick=4,
    )
    return {
        "stage_id": "stage2_mild_obstacle_sweeter_path",
        "stage_goal": "choose one candy path where the sweeter candy has mild obstacle cost",
        "choice_candidates": [left, right],
        "obstacle_penalty_applied": True,
        "preferred_path": "right_mild_obstacle_sweeter_candy",
        "actual_consumed_path": actual,
        "actual_consumed_path_count": 1,
        "unchosen_path_consumed": False,
        "return_after_choice_allowed": False,
        "irreversible_choice_enforced": True,
        "sweeter_net_tendency_still_higher": right["expected_net_tendency_score"] > left["expected_net_tendency_score"],
        "action_selection_applied": False,
    }


def _path_candidate(path_id: str, *, sweetness: float, obstacle_cost: float) -> dict[str, Any]:
    dopamine_value = round(BASELINE_DOPAMINE + (sweetness * 0.65), 2)
    return {
        "path_id": path_id,
        "outcome": "candy_contact",
        "sweetness": sweetness,
        "obstacle_cost": obstacle_cost,
        "expected_dopamine_like_response_value": dopamine_value,
        "expected_net_tendency_score": round(dopamine_value - obstacle_cost, 2),
        "candidate_preview_only": True,
        "candy_consumed": False,
    }


def _path_response(case_id: str, path_id: str, *, sweetness: float, obstacle_cost: float, tick: int) -> dict[str, Any]:
    dopamine_value = round(BASELINE_DOPAMINE + (sweetness * 0.65), 2)
    signal = _dopamine_signal(case_id, path_id, sweetness, dopamine_value, tick)
    validation = validate_signal_record(signal)
    return {
        "case_id": case_id,
        "path_id": path_id,
        "outcome": "candy_contact",
        "sweetness": sweetness,
        "obstacle_cost": obstacle_cost,
        "dopamine_like_response_created": True,
        "dopamine_like_response_value": dopamine_value,
        "dopamine_like_signal_record": signal,
        "dopamine_like_signal_valid": validation["valid"],
        "net_tendency_score": round(dopamine_value - obstacle_cost, 2),
        "runtime_endocrine_state_persisted": False,
        "subjective_pleasure_claim": False,
    }


def _dopamine_signal(case_id: str, path_id: str, sweetness: float, value: float, tick: int) -> dict[str, Any]:
    definition = KNOWN_SIGNALS["dopamine_like"]
    return {
        "signal_name": "dopamine_like",
        "axis": definition["axis"],
        "value": value,
        "value_range": [0.0, 1.0],
        "baseline": BASELINE_DOPAMINE,
        "decay_rate": 0.1,
        "source_event_ids": [f"{case_id}:candy_contact"],
        "source_event_types": ["reward_event", "candy_contact", "sweetness_response"],
        "source_trace": {
            "trace_id": f"dopamine_like_sweetness_response:{case_id}",
            "trace_type": "mimetic_endocrine_sweetness_preference_sandbox",
            "path_id": path_id,
            "sweetness": sweetness,
            "runtime_event_applied": False,
        },
        "last_updated_tick": tick,
        "confidence": 1.0,
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_candidate_approval": True,
        "subjective_claim": False,
        "downstream_annotation_targets": list(definition["downstream_annotation_targets"]),
        "interaction_notes": "sandbox response trace only; no persistent endocrine runtime",
        "status": "valid_sweetness_response_trace",
        "validation_errors": [],
        "notes": "Functional dopamine_like response to controlled candy sweetness.",
    }


def _validate_stage0(stage: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if stage.get("stage_id") != "stage0_candy_calibration":
        errors.append("stage0_stage_id_not_expected")
    trials = stage.get("calibration_trials")
    if not isinstance(trials, list) or len(trials) != 2:
        errors.append("stage0_calibration_trials_not_expected")
        trials = []
    valid_trace_count = _validate_paths(trials, errors, "stage0")
    if stage.get("ordinary_candy_eaten_count") != 1:
        errors.append("stage0_ordinary_candy_eaten_count_not_one")
    if stage.get("sweeter_candy_eaten_count") != 1:
        errors.append("stage0_sweeter_candy_eaten_count_not_one")
    if stage.get("each_candy_eaten_once") is not True:
        errors.append("stage0_each_candy_eaten_once_not_true")
    if stage.get("choice_required") is not False:
        errors.append("stage0_choice_required")
    if stage.get("action_selection_applied") is not False:
        errors.append("stage0_action_selection_applied")
    return {
        "error_codes": errors,
        "valid_trace_count": valid_trace_count,
        "calibration_completed": valid_trace_count == 2 and stage.get("each_candy_eaten_once") is True,
        "each_candy_eaten_once": (
            stage.get("ordinary_candy_eaten_count") == 1
            and stage.get("sweeter_candy_eaten_count") == 1
            and stage.get("each_candy_eaten_once") is True
        ),
    }


def _validate_stage1(stage: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if stage.get("stage_id") != "stage1_two_paths_both_candy":
        errors.append("stage1_stage_id_not_expected")
    candidates = stage.get("choice_candidates")
    if not isinstance(candidates, list) or len(candidates) != 2:
        errors.append("stage1_choice_candidates_not_expected")
        candidates = []
    valid_candidate_count = _validate_candidates(candidates, errors, "stage1")
    actual = stage.get("actual_consumed_path")
    if not isinstance(actual, dict):
        errors.append("stage1_actual_consumed_path_missing")
        actual = {}
    valid_trace_count = _validate_paths([actual], errors, "stage1_actual") if actual else 0
    by_id = {path.get("path_id"): path for path in candidates if isinstance(path, dict)}
    left = by_id.get("left_candy", {})
    right = by_id.get("right_sweeter_candy", {})
    sweeter_response_higher = right.get("expected_dopamine_like_response_value", 0) > left.get(
        "expected_dopamine_like_response_value", 1
    )
    if not sweeter_response_higher:
        errors.append("stage1_sweeter_response_not_higher")
    if stage.get("preferred_path") != "right_sweeter_candy":
        errors.append("stage1_preferred_path_not_expected")
    if actual.get("path_id") != "right_sweeter_candy":
        errors.append("stage1_actual_consumed_path_not_expected")
    if stage.get("actual_consumed_path_count") != 1:
        errors.append("stage1_actual_consumed_path_count_not_one")
    if stage.get("unchosen_path_consumed") is not False:
        errors.append("stage1_unchosen_path_consumed")
    if stage.get("return_after_choice_allowed") is not False:
        errors.append("stage1_return_after_choice_allowed")
    if stage.get("irreversible_choice_enforced") is not True:
        errors.append("stage1_irreversible_choice_not_enforced")
    if stage.get("sweeter_response_higher") is not True:
        errors.append("stage1_sweeter_response_higher_not_true")
    if stage.get("action_selection_applied") is not False:
        errors.append("stage1_action_selection_applied")
    irreversible = (
        stage.get("actual_consumed_path_count") == 1
        and stage.get("unchosen_path_consumed") is False
        and stage.get("return_after_choice_allowed") is False
        and stage.get("irreversible_choice_enforced") is True
    )
    return {
        "error_codes": errors,
        "valid_trace_count": valid_trace_count,
        "sweeter_response_higher": (
            valid_candidate_count == 2 and sweeter_response_higher and stage.get("sweeter_response_higher") is True
        ),
        "irreversible_choice_enforced": irreversible,
    }


def _validate_stage2(stage: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if stage.get("stage_id") != "stage2_mild_obstacle_sweeter_path":
        errors.append("stage2_stage_id_not_expected")
    candidates = stage.get("choice_candidates")
    if not isinstance(candidates, list) or len(candidates) != 2:
        errors.append("stage2_choice_candidates_not_expected")
        candidates = []
    valid_candidate_count = _validate_candidates(candidates, errors, "stage2")
    actual = stage.get("actual_consumed_path")
    if not isinstance(actual, dict):
        errors.append("stage2_actual_consumed_path_missing")
        actual = {}
    valid_trace_count = _validate_paths([actual], errors, "stage2_actual") if actual else 0
    by_id = {path.get("path_id"): path for path in candidates if isinstance(path, dict)}
    left = by_id.get("left_easy_candy", {})
    right = by_id.get("right_mild_obstacle_sweeter_candy", {})
    obstacle_penalty_applied = right.get("obstacle_cost", 0) > 0
    sweeter_net_higher = right.get("expected_net_tendency_score", 0) > left.get("expected_net_tendency_score", 1)
    if not obstacle_penalty_applied:
        errors.append("stage2_obstacle_penalty_not_applied")
    if not sweeter_net_higher:
        errors.append("stage2_sweeter_net_tendency_not_higher")
    if stage.get("preferred_path") != "right_mild_obstacle_sweeter_candy":
        errors.append("stage2_preferred_path_not_expected")
    if actual.get("path_id") != "right_mild_obstacle_sweeter_candy":
        errors.append("stage2_actual_consumed_path_not_expected")
    if stage.get("actual_consumed_path_count") != 1:
        errors.append("stage2_actual_consumed_path_count_not_one")
    if stage.get("unchosen_path_consumed") is not False:
        errors.append("stage2_unchosen_path_consumed")
    if stage.get("return_after_choice_allowed") is not False:
        errors.append("stage2_return_after_choice_allowed")
    if stage.get("irreversible_choice_enforced") is not True:
        errors.append("stage2_irreversible_choice_not_enforced")
    if stage.get("obstacle_penalty_applied") is not True:
        errors.append("stage2_obstacle_penalty_applied_not_true")
    if stage.get("sweeter_net_tendency_still_higher") is not True:
        errors.append("stage2_sweeter_net_tendency_still_higher_not_true")
    if stage.get("action_selection_applied") is not False:
        errors.append("stage2_action_selection_applied")
    irreversible = (
        stage.get("actual_consumed_path_count") == 1
        and stage.get("unchosen_path_consumed") is False
        and stage.get("return_after_choice_allowed") is False
        and stage.get("irreversible_choice_enforced") is True
    )
    return {
        "error_codes": errors,
        "valid_trace_count": valid_trace_count,
        "obstacle_penalty_applied": obstacle_penalty_applied and stage.get("obstacle_penalty_applied") is True,
        "sweeter_net_tendency_still_higher": sweeter_net_higher
        and stage.get("sweeter_net_tendency_still_higher") is True
        and valid_candidate_count == 2,
        "irreversible_choice_enforced": irreversible,
    }


def _validate_candidates(paths: list[dict[str, Any]], errors: list[str], prefix: str) -> int:
    valid_count = 0
    for index, path in enumerate(paths, start=1):
        if not isinstance(path, dict):
            errors.append(f"{prefix}_candidate_{index}_not_dict")
            continue
        if path.get("outcome") != "candy_contact":
            errors.append(f"{prefix}_candidate_{index}_outcome_not_candy_contact")
        if path.get("candidate_preview_only") is not True:
            errors.append(f"{prefix}_candidate_{index}_not_preview_only")
        if path.get("candy_consumed") is not False:
            errors.append(f"{prefix}_candidate_{index}_candy_consumed")
        if not isinstance(path.get("expected_dopamine_like_response_value"), (int, float)):
            errors.append(f"{prefix}_candidate_{index}_expected_response_missing")
        if not isinstance(path.get("expected_net_tendency_score"), (int, float)):
            errors.append(f"{prefix}_candidate_{index}_expected_net_tendency_missing")
        if not any(code.startswith(f"{prefix}_candidate_{index}_") for code in errors):
            valid_count += 1
    return valid_count


def _validate_paths(paths: list[dict[str, Any]], errors: list[str], prefix: str) -> int:
    valid_trace_count = 0
    for index, path in enumerate(paths, start=1):
        if not isinstance(path, dict):
            errors.append(f"{prefix}_path_{index}_not_dict")
            continue
        if path.get("outcome") != "candy_contact":
            errors.append(f"{prefix}_path_{index}_outcome_not_candy_contact")
        if path.get("dopamine_like_response_created") is not True:
            errors.append(f"{prefix}_path_{index}_dopamine_response_not_created")
        if path.get("runtime_endocrine_state_persisted") is not False:
            errors.append(f"{prefix}_path_{index}_runtime_endocrine_state_persisted")
        if path.get("subjective_pleasure_claim") is not False:
            errors.append(f"{prefix}_path_{index}_subjective_pleasure_claim")
        signal = path.get("dopamine_like_signal_record")
        validation = validate_signal_record(signal) if isinstance(signal, dict) else {"valid": False}
        if validation["valid"] is not True:
            errors.append(f"{prefix}_path_{index}_dopamine_signal_invalid")
        else:
            valid_trace_count += 1
    return valid_trace_count


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def add(mutator) -> None:
        item = deepcopy(valid_record)
        mutator(item)
        invalids.append(item)

    add(lambda r: r.update({"record_type": "wrong"}))
    add(lambda r: r.update({"boundary_index_after": "2026-06-09-b107"}))
    add(lambda r: r["sandbox_context"].update({"sandbox_scope": "production"}))
    add(lambda r: r["sandbox_context"].update({"fixed_choice_fixture": False}))
    add(lambda r: r["sandbox_context"].update({"free_choice_added": True}))
    add(lambda r: r["sandbox_context"].update({"pathfinding_used": True}))
    add(lambda r: r["stage0_candy_calibration"].update({"stage_id": "wrong"}))
    add(lambda r: r["stage0_candy_calibration"].update({"ordinary_candy_eaten_count": 0}))
    add(lambda r: r["stage0_candy_calibration"].update({"sweeter_candy_eaten_count": 0}))
    add(lambda r: r["stage0_candy_calibration"].update({"each_candy_eaten_once": False}))
    add(lambda r: r["stage0_candy_calibration"].update({"choice_required": True}))
    add(lambda r: r["stage0_candy_calibration"]["calibration_trials"][0].update({"outcome": "blocked"}))
    add(lambda r: r["stage1_two_candy_paths"].update({"stage_id": "wrong"}))
    add(lambda r: r["stage1_two_candy_paths"].update({"preferred_path": "left_candy"}))
    add(lambda r: r["stage1_two_candy_paths"].update({"sweeter_response_higher": False}))
    add(lambda r: r["stage1_two_candy_paths"]["choice_candidates"][1].update({"expected_dopamine_like_response_value": 0.3}))
    add(lambda r: r["stage1_two_candy_paths"]["choice_candidates"][0].update({"candy_consumed": True}))
    add(lambda r: r["stage1_two_candy_paths"].update({"actual_consumed_path_count": 2}))
    add(lambda r: r["stage1_two_candy_paths"].update({"unchosen_path_consumed": True}))
    add(lambda r: r["stage1_two_candy_paths"].update({"return_after_choice_allowed": True}))
    add(lambda r: r["stage1_two_candy_paths"].update({"irreversible_choice_enforced": False}))
    add(lambda r: r["stage1_two_candy_paths"]["actual_consumed_path"].update({"path_id": "left_candy"}))
    add(lambda r: r["stage1_two_candy_paths"]["actual_consumed_path"].update({"subjective_pleasure_claim": True}))
    add(lambda r: r["stage1_two_candy_paths"]["actual_consumed_path"]["dopamine_like_signal_record"].update({"subjective_claim": True}))
    add(lambda r: r["stage2_obstacle_sweeter_path"].update({"stage_id": "wrong"}))
    add(lambda r: r["stage2_obstacle_sweeter_path"].update({"preferred_path": "left_easy_candy"}))
    add(lambda r: r["stage2_obstacle_sweeter_path"].update({"obstacle_penalty_applied": False}))
    add(lambda r: r["stage2_obstacle_sweeter_path"].update({"sweeter_net_tendency_still_higher": False}))
    add(lambda r: r["stage2_obstacle_sweeter_path"]["choice_candidates"][1].update({"obstacle_cost": 0.0}))
    add(lambda r: r["stage2_obstacle_sweeter_path"]["choice_candidates"][1].update({"expected_net_tendency_score": 0.2}))
    add(lambda r: r["stage2_obstacle_sweeter_path"].update({"actual_consumed_path_count": 2}))
    add(lambda r: r["stage2_obstacle_sweeter_path"].update({"unchosen_path_consumed": True}))
    add(lambda r: r["stage2_obstacle_sweeter_path"].update({"return_after_choice_allowed": True}))
    add(lambda r: r["stage2_obstacle_sweeter_path"].update({"irreversible_choice_enforced": False}))
    add(lambda r: r["endocrine_response_summary"].update({"valid_dopamine_like_response_trace_count": 3}))
    add(lambda r: r["endocrine_response_summary"].update({"stage0_each_candy_eaten_once": False}))
    add(lambda r: r["endocrine_response_summary"].update({"stage1_sweeter_response_higher": False}))
    add(lambda r: r["endocrine_response_summary"].update({"stage1_irreversible_choice_enforced": False}))
    add(lambda r: r["endocrine_response_summary"].update({"stage2_sweeter_net_tendency_still_higher": False}))
    add(lambda r: r["endocrine_response_summary"].update({"stage2_irreversible_choice_enforced": False}))
    add(lambda r: r["endocrine_response_summary"].update({"response_trace_only": False}))
    add(lambda r: r["endocrine_response_summary"].update({"runtime_endocrine_state_persisted": True}))
    add(lambda r: r["preference_preview"].update({"stage1_preferred_path": "left_candy"}))
    add(lambda r: r["preference_preview"].update({"stage2_preferred_path": "left_easy_candy"}))
    add(lambda r: r["preference_preview"].update({"choice_is_irreversible": False}))
    add(lambda r: r["preference_preview"].update({"both_paths_consumed_after_choice": True}))
    add(lambda r: r["preference_preview"].update({"preference_changed_by_sweetness": False}))
    add(lambda r: r["preference_preview"].update({"obstacle_can_be_overcome_by_sweetness_preview": False}))
    add(lambda r: r["preference_preview"].update({"action_selection_applied": True}))
    add(lambda r: r["human_summary"].update({"plain_result": ""}))
    add(lambda r: r["blocked_flags"].update({"proof_of_learning_claim_allowed": True}))
    return invalids


def _dict(value: Any, errors: list[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(code)
        return {}
    return value
