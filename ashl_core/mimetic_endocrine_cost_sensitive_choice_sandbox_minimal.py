"""Cost-sensitive sandbox choice traces for mimetic endocrine sweetness response."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .mimetic_endocrine_signal_schema import KNOWN_SIGNALS, validate_signal_record
from .mimetic_endocrine_sweetness_preference_sandbox_minimal import (
    build_mimetic_endocrine_sweetness_preference_sandbox_record,
    validate_mimetic_endocrine_sweetness_preference_sandbox_record,
)


COMMAND = "run-mimetic-endocrine-cost-sensitive-choice-sandbox-minimal-check"
FLOW = "mimetic_endocrine_cost_sensitive_choice_sandbox_minimal_v0"
PACKAGE_ID = "PKG-Phase0-MimeticEndocrineCostSensitiveChoiceSandbox-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b108"
BOUNDARY_INDEX_AFTER = "2026-06-09-b109"
SANDBOX_ID = "mimetic_endocrine_cost_sensitive_choice_sandbox_v0"
BASELINE_DOPAMINE = 0.2

BLOCKED_FLAGS = (
    "visual_detection_claimed",
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


def build_mimetic_endocrine_cost_sensitive_choice_sandbox_record() -> dict[str, Any]:
    source = build_mimetic_endocrine_sweetness_preference_sandbox_record()
    source_validation = validate_mimetic_endocrine_sweetness_preference_sandbox_record(source)
    scenario = _build_high_difficulty_choice_scenario()
    return {
        "record_type": "mimetic_endocrine_cost_sensitive_choice_sandbox",
        "record_version": "v0",
        "choice_status": "completed_sandbox_cost_sensitive_choice_trace",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "sandbox_context": {
            "sandbox_id": SANDBOX_ID,
            "sandbox_scope": "sandbox_only",
            "fixed_choice_fixture": True,
            "uses_symbolic_numeric_fixture": True,
            "visual_detection_claimed": False,
            "free_choice_added": False,
            "pathfinding_used": False,
            "production_behavior_changed": False,
        },
        "source_calibration": {
            "source_record_type": source["record_type"],
            "source_boundary_index": source["boundary_index_after"],
            "source_stage0_each_candy_eaten_once": source["stage0_candy_calibration"]["each_candy_eaten_once"],
            "source_valid": source_validation["valid"],
        },
        "high_difficulty_choice_scenario": scenario,
        "choice_result_summary": {
            "raw_sweeter_response_higher": True,
            "difficulty_cost_applied": True,
            "return_path_available": True,
            "sweeter_net_tendency_lower": True,
            "ordinary_easy_path_preferred": True,
            "hard_sweeter_path_not_forced": True,
            "chosen_path": "left_easy_ordinary_candy",
            "chosen_path_consumed": True,
            "unchosen_sweeter_path_consumed": False,
            "both_paths_consumed": False,
            "response_trace_only": True,
            "runtime_endocrine_state_persisted": False,
        },
        "human_summary": {
            "what_was_tested": "A high-difficulty sweeter candy path was compared against a much easier ordinary candy path.",
            "what_changed_from_previous": "Unlike the mild-obstacle case, the sweeter path has enough difficulty cost that its net tendency falls below the easy ordinary path.",
            "choice_result": "The fixed sandbox preview prefers the easy ordinary candy path rather than forcing the harder sweeter candy path.",
            "return_rule": "The hard sweeter path is returnable before candy consumption, so a failed or costly probe need not consume both candies.",
            "what_is_blocked": "Vision, free choice, pathfinding, production behavior, memory writes, retention writes, predictor mutation, persistent endocrine state, subjective pleasure claims, and proof claims remain blocked.",
            "plain_result": "The sandbox can show that sweetness response is cost-sensitive: higher sweetness does not automatically win when the path is much harder.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_mimetic_endocrine_cost_sensitive_choice_sandbox_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "mimetic_endocrine_cost_sensitive_choice_sandbox",
        "record_version": "v0",
        "choice_status": "completed_sandbox_cost_sensitive_choice_trace",
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
        "fixed_choice_fixture": True,
        "uses_symbolic_numeric_fixture": True,
        "visual_detection_claimed": False,
        "free_choice_added": False,
        "pathfinding_used": False,
        "production_behavior_changed": False,
    }
    for field, value in expected_context.items():
        if context.get(field) != value:
            errors.append(f"sandbox_context_{field}_not_expected")

    source = _dict(record.get("source_calibration"), errors, "source_calibration_missing")
    if source.get("source_record_type") != "mimetic_endocrine_sweetness_preference_sandbox":
        errors.append("source_calibration_source_record_type_not_expected")
    if source.get("source_boundary_index") != "2026-06-09-b108":
        errors.append("source_calibration_source_boundary_index_not_expected")
    if source.get("source_stage0_each_candy_eaten_once") is not True:
        errors.append("source_calibration_stage0_each_candy_eaten_once_not_true")
    if source.get("source_valid") is not True:
        errors.append("source_calibration_source_valid_not_true")

    scenario = _dict(record.get("high_difficulty_choice_scenario"), errors, "high_difficulty_choice_scenario_missing")
    scenario_result = _validate_high_difficulty_scenario(scenario)
    errors.extend(scenario_result["error_codes"])

    summary = _dict(record.get("choice_result_summary"), errors, "choice_result_summary_missing")
    expected_summary = {
        "raw_sweeter_response_higher": True,
        "difficulty_cost_applied": True,
        "return_path_available": True,
        "sweeter_net_tendency_lower": True,
        "ordinary_easy_path_preferred": True,
        "hard_sweeter_path_not_forced": True,
        "chosen_path": "left_easy_ordinary_candy",
        "chosen_path_consumed": True,
        "unchosen_sweeter_path_consumed": False,
        "both_paths_consumed": False,
        "response_trace_only": True,
        "runtime_endocrine_state_persisted": False,
    }
    for field, value in expected_summary.items():
        if summary.get(field) != value:
            errors.append(f"choice_result_summary_{field}_not_expected")

    human_summary = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in (
        "what_was_tested",
        "what_changed_from_previous",
        "choice_result",
        "return_rule",
        "what_is_blocked",
        "plain_result",
    ):
        if not isinstance(human_summary.get(field), str) or not human_summary.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    blocked_flags = _dict(record.get("blocked_flags"), errors, "blocked_flags_missing")
    for field in BLOCKED_FLAGS:
        if blocked_flags.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "source_calibration_valid": source.get("source_valid") is True,
        "raw_sweeter_response_higher": scenario_result["raw_sweeter_response_higher"],
        "difficulty_cost_applied": scenario_result["difficulty_cost_applied"],
        "return_path_available": scenario_result["return_path_available"],
        "sweeter_net_tendency_lower": scenario_result["sweeter_net_tendency_lower"],
        "ordinary_easy_path_preferred": scenario_result["ordinary_easy_path_preferred"],
        "hard_sweeter_path_not_forced": scenario_result["hard_sweeter_path_not_forced"],
        "chosen_path_consumed": scenario_result["chosen_path_consumed"],
        "both_paths_consumed": summary.get("both_paths_consumed") is False,
        "valid_dopamine_like_response_trace_count": scenario_result["valid_trace_count"],
        "visual_detection_blocked": context.get("visual_detection_claimed") is False
        and blocked_flags.get("visual_detection_claimed") is False,
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


def run_mimetic_endocrine_cost_sensitive_choice_sandbox_minimal_check() -> dict[str, Any]:
    valid_record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
    valid_result = validate_mimetic_endocrine_cost_sensitive_choice_sandbox_record(valid_record)
    invalid_results = [
        validate_mimetic_endocrine_cost_sensitive_choice_sandbox_record(item) for item in _invalid_records(valid_record)
    ]
    summary = {
        "valid_cost_sensitive_choice_sandbox_count": 1 if valid_result["valid"] else 0,
        "invalid_cost_sensitive_choice_sandbox_count": sum(1 for result in invalid_results if not result["valid"]),
        "source_calibration_valid_count": 1 if valid_result["source_calibration_valid"] else 0,
        "raw_sweeter_response_higher_count": 1 if valid_result["raw_sweeter_response_higher"] else 0,
        "difficulty_cost_applied_count": 1 if valid_result["difficulty_cost_applied"] else 0,
        "return_path_available_count": 1 if valid_result["return_path_available"] else 0,
        "sweeter_net_tendency_lower_count": 1 if valid_result["sweeter_net_tendency_lower"] else 0,
        "ordinary_easy_path_preferred_count": 1 if valid_result["ordinary_easy_path_preferred"] else 0,
        "hard_sweeter_path_not_forced_count": 1 if valid_result["hard_sweeter_path_not_forced"] else 0,
        "chosen_path_consumed_count": 1 if valid_result["chosen_path_consumed"] else 0,
        "both_paths_consumed_blocked_count": 1 if valid_result["both_paths_consumed"] else 0,
        "valid_dopamine_like_response_trace_total": valid_result["valid_dopamine_like_response_trace_count"],
        "visual_detection_blocked_count": 1 if valid_result["visual_detection_blocked"] else 0,
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
    summary["all_cost_sensitive_choice_sandbox_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_cost_sensitive_choice_sandbox_count"] == 39
        and summary["source_calibration_valid_count"] == 1
        and summary["raw_sweeter_response_higher_count"] == 1
        and summary["difficulty_cost_applied_count"] == 1
        and summary["return_path_available_count"] == 1
        and summary["sweeter_net_tendency_lower_count"] == 1
        and summary["ordinary_easy_path_preferred_count"] == 1
        and summary["hard_sweeter_path_not_forced_count"] == 1
        and summary["chosen_path_consumed_count"] == 1
        and summary["valid_dopamine_like_response_trace_total"] == 1
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_cost_sensitive_choice_sandbox_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Adds a sandbox-only cost-sensitive contrast for mimetic endocrine sweetness response.",
        },
        "valid_record": valid_record,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
    }


def _build_high_difficulty_choice_scenario() -> dict[str, Any]:
    ordinary = _path_candidate(
        "left_easy_ordinary_candy",
        sweetness=0.4,
        difficulty_cost=0.05,
        return_cost=0.0,
        return_available=True,
    )
    sweeter = _path_candidate(
        "right_high_difficulty_sweeter_candy",
        sweetness=0.9,
        difficulty_cost=0.55,
        return_cost=0.10,
        return_available=True,
    )
    actual = _path_response(
        "cost_sensitive_choice_left_easy_ordinary_candy",
        "left_easy_ordinary_candy",
        sweetness=0.4,
        difficulty_cost=0.05,
        return_cost=0.0,
        tick=5,
    )
    return {
        "scenario_id": "high_difficulty_sweeter_vs_easy_ordinary",
        "scenario_goal": "test whether high sweetness is outweighed by high difficulty cost",
        "choice_candidates": [ordinary, sweeter],
        "return_policy": {
            "return_after_probe_allowed": True,
            "return_before_candy_consumption_only": True,
            "return_path_available": True,
            "return_consumes_candy": False,
            "both_paths_can_be_consumed": False,
        },
        "raw_sweeter_response_higher": True,
        "difficulty_cost_applied": True,
        "sweeter_net_tendency_lower": True,
        "preferred_path": "left_easy_ordinary_candy",
        "hard_sweeter_path_not_forced": True,
        "actual_consumed_path": actual,
        "actual_consumed_path_count": 1,
        "unchosen_sweeter_path_consumed": False,
        "both_paths_consumed": False,
        "action_selection_applied": False,
    }


def _path_candidate(
    path_id: str, *, sweetness: float, difficulty_cost: float, return_cost: float, return_available: bool
) -> dict[str, Any]:
    dopamine_value = _dopamine_value(sweetness)
    total_cost = round(difficulty_cost + return_cost, 2)
    return {
        "path_id": path_id,
        "outcome": "candy_contact_possible",
        "sweetness": sweetness,
        "expected_dopamine_like_response_value": dopamine_value,
        "difficulty_cost": difficulty_cost,
        "return_cost": return_cost,
        "total_cost": total_cost,
        "expected_net_tendency_score": round(dopamine_value - total_cost, 2),
        "return_available": return_available,
        "candidate_preview_only": True,
        "candy_consumed": False,
    }


def _path_response(
    case_id: str,
    path_id: str,
    *,
    sweetness: float,
    difficulty_cost: float,
    return_cost: float,
    tick: int,
) -> dict[str, Any]:
    dopamine_value = _dopamine_value(sweetness)
    total_cost = round(difficulty_cost + return_cost, 2)
    signal = _dopamine_signal(case_id, path_id, sweetness, dopamine_value, tick)
    validation = validate_signal_record(signal)
    return {
        "case_id": case_id,
        "path_id": path_id,
        "outcome": "candy_contact",
        "sweetness": sweetness,
        "difficulty_cost": difficulty_cost,
        "return_cost": return_cost,
        "total_cost": total_cost,
        "dopamine_like_response_created": True,
        "dopamine_like_response_value": dopamine_value,
        "dopamine_like_signal_record": signal,
        "dopamine_like_signal_valid": validation["valid"],
        "net_tendency_score": round(dopamine_value - total_cost, 2),
        "runtime_endocrine_state_persisted": False,
        "subjective_pleasure_claim": False,
    }


def _dopamine_value(sweetness: float) -> float:
    return round(BASELINE_DOPAMINE + (sweetness * 0.65), 2)


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
        "source_event_types": ["reward_event", "candy_contact", "cost_sensitive_sweetness_response"],
        "source_trace": {
            "trace_id": f"dopamine_like_cost_sensitive_choice:{case_id}",
            "trace_type": "mimetic_endocrine_cost_sensitive_choice_sandbox",
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
        "interaction_notes": "sandbox cost-sensitive response trace only; no persistent endocrine runtime",
        "status": "valid_cost_sensitive_sweetness_response_trace",
        "validation_errors": [],
        "notes": "Functional dopamine_like response to controlled candy sweetness with difficulty cost.",
    }


def _validate_high_difficulty_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if scenario.get("scenario_id") != "high_difficulty_sweeter_vs_easy_ordinary":
        errors.append("scenario_id_not_expected")
    candidates = scenario.get("choice_candidates")
    if not isinstance(candidates, list) or len(candidates) != 2:
        errors.append("choice_candidates_not_expected")
        candidates = []
    valid_candidate_count = _validate_candidates(candidates, errors)
    by_id = {path.get("path_id"): path for path in candidates if isinstance(path, dict)}
    ordinary = by_id.get("left_easy_ordinary_candy", {})
    sweeter = by_id.get("right_high_difficulty_sweeter_candy", {})
    raw_sweeter_higher = sweeter.get("expected_dopamine_like_response_value", 0) > ordinary.get(
        "expected_dopamine_like_response_value", 1
    )
    difficulty_cost_applied = sweeter.get("difficulty_cost", 0) >= 0.55 and sweeter.get("total_cost", 0) >= 0.65
    sweeter_net_lower = sweeter.get("expected_net_tendency_score", 1) < ordinary.get("expected_net_tendency_score", 0)
    if not raw_sweeter_higher:
        errors.append("raw_sweeter_response_not_higher")
    if not difficulty_cost_applied:
        errors.append("difficulty_cost_not_applied")
    if not sweeter_net_lower:
        errors.append("sweeter_net_tendency_not_lower")
    if scenario.get("raw_sweeter_response_higher") is not True:
        errors.append("raw_sweeter_response_higher_not_true")
    if scenario.get("difficulty_cost_applied") is not True:
        errors.append("difficulty_cost_applied_not_true")
    if scenario.get("sweeter_net_tendency_lower") is not True:
        errors.append("sweeter_net_tendency_lower_not_true")

    return_policy = _dict(scenario.get("return_policy"), errors, "return_policy_missing")
    expected_return = {
        "return_after_probe_allowed": True,
        "return_before_candy_consumption_only": True,
        "return_path_available": True,
        "return_consumes_candy": False,
        "both_paths_can_be_consumed": False,
    }
    for field, value in expected_return.items():
        if return_policy.get(field) != value:
            errors.append(f"return_policy_{field}_not_expected")

    actual = scenario.get("actual_consumed_path")
    if not isinstance(actual, dict):
        errors.append("actual_consumed_path_missing")
        actual = {}
    valid_trace_count = _validate_response(actual, errors)
    if scenario.get("preferred_path") != "left_easy_ordinary_candy":
        errors.append("preferred_path_not_easy_ordinary")
    if scenario.get("hard_sweeter_path_not_forced") is not True:
        errors.append("hard_sweeter_path_not_forced_not_true")
    if actual.get("path_id") != "left_easy_ordinary_candy":
        errors.append("actual_consumed_path_not_easy_ordinary")
    if scenario.get("actual_consumed_path_count") != 1:
        errors.append("actual_consumed_path_count_not_one")
    if scenario.get("unchosen_sweeter_path_consumed") is not False:
        errors.append("unchosen_sweeter_path_consumed")
    if scenario.get("both_paths_consumed") is not False:
        errors.append("both_paths_consumed")
    if scenario.get("action_selection_applied") is not False:
        errors.append("action_selection_applied")
    return {
        "error_codes": errors,
        "valid_trace_count": valid_trace_count,
        "raw_sweeter_response_higher": raw_sweeter_higher and scenario.get("raw_sweeter_response_higher") is True,
        "difficulty_cost_applied": difficulty_cost_applied and scenario.get("difficulty_cost_applied") is True,
        "return_path_available": return_policy.get("return_path_available") is True,
        "sweeter_net_tendency_lower": sweeter_net_lower and scenario.get("sweeter_net_tendency_lower") is True,
        "ordinary_easy_path_preferred": scenario.get("preferred_path") == "left_easy_ordinary_candy",
        "hard_sweeter_path_not_forced": scenario.get("hard_sweeter_path_not_forced") is True,
        "chosen_path_consumed": actual.get("path_id") == "left_easy_ordinary_candy"
        and scenario.get("actual_consumed_path_count") == 1,
        "valid_candidate_count": valid_candidate_count,
    }


def _validate_candidates(paths: list[dict[str, Any]], errors: list[str]) -> int:
    valid_count = 0
    for index, path in enumerate(paths, start=1):
        if not isinstance(path, dict):
            errors.append(f"candidate_{index}_not_dict")
            continue
        if path.get("outcome") != "candy_contact_possible":
            errors.append(f"candidate_{index}_outcome_not_expected")
        if path.get("candidate_preview_only") is not True:
            errors.append(f"candidate_{index}_not_preview_only")
        if path.get("candy_consumed") is not False:
            errors.append(f"candidate_{index}_candy_consumed")
        if not isinstance(path.get("expected_dopamine_like_response_value"), (int, float)):
            errors.append(f"candidate_{index}_expected_response_missing")
        if not isinstance(path.get("expected_net_tendency_score"), (int, float)):
            errors.append(f"candidate_{index}_expected_net_missing")
        if path.get("return_available") is not True:
            errors.append(f"candidate_{index}_return_not_available")
        if not any(code.startswith(f"candidate_{index}_") for code in errors):
            valid_count += 1
    return valid_count


def _validate_response(path: dict[str, Any], errors: list[str]) -> int:
    if path.get("outcome") != "candy_contact":
        errors.append("actual_response_outcome_not_candy_contact")
    if path.get("dopamine_like_response_created") is not True:
        errors.append("actual_response_dopamine_not_created")
    if path.get("runtime_endocrine_state_persisted") is not False:
        errors.append("actual_response_runtime_endocrine_state_persisted")
    if path.get("subjective_pleasure_claim") is not False:
        errors.append("actual_response_subjective_pleasure_claim")
    signal = path.get("dopamine_like_signal_record")
    validation = validate_signal_record(signal) if isinstance(signal, dict) else {"valid": False}
    if validation["valid"] is not True:
        errors.append("actual_response_dopamine_signal_invalid")
        return 0
    return 1


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def add(mutator) -> None:
        item = deepcopy(valid_record)
        mutator(item)
        invalids.append(item)

    add(lambda r: r.update({"record_type": "wrong"}))
    add(lambda r: r.update({"boundary_index_after": "2026-06-09-b108"}))
    add(lambda r: r["sandbox_context"].update({"visual_detection_claimed": True}))
    add(lambda r: r["sandbox_context"].update({"free_choice_added": True}))
    add(lambda r: r["sandbox_context"].update({"pathfinding_used": True}))
    add(lambda r: r["source_calibration"].update({"source_valid": False}))
    add(lambda r: r["source_calibration"].update({"source_stage0_each_candy_eaten_once": False}))
    add(lambda r: r["high_difficulty_choice_scenario"].update({"scenario_id": "wrong"}))
    add(lambda r: r["high_difficulty_choice_scenario"]["choice_candidates"][1].update({"expected_dopamine_like_response_value": 0.3}))
    add(lambda r: r["high_difficulty_choice_scenario"]["choice_candidates"][1].update({"difficulty_cost": 0.1, "total_cost": 0.2}))
    add(lambda r: r["high_difficulty_choice_scenario"]["choice_candidates"][1].update({"expected_net_tendency_score": 0.9}))
    add(lambda r: r["high_difficulty_choice_scenario"]["choice_candidates"][0].update({"candy_consumed": True}))
    add(lambda r: r["high_difficulty_choice_scenario"]["choice_candidates"][1].update({"return_available": False}))
    add(lambda r: r["high_difficulty_choice_scenario"]["return_policy"].update({"return_after_probe_allowed": False}))
    add(lambda r: r["high_difficulty_choice_scenario"]["return_policy"].update({"return_before_candy_consumption_only": False}))
    add(lambda r: r["high_difficulty_choice_scenario"]["return_policy"].update({"return_path_available": False}))
    add(lambda r: r["high_difficulty_choice_scenario"]["return_policy"].update({"return_consumes_candy": True}))
    add(lambda r: r["high_difficulty_choice_scenario"]["return_policy"].update({"both_paths_can_be_consumed": True}))
    add(lambda r: r["high_difficulty_choice_scenario"].update({"raw_sweeter_response_higher": False}))
    add(lambda r: r["high_difficulty_choice_scenario"].update({"difficulty_cost_applied": False}))
    add(lambda r: r["high_difficulty_choice_scenario"].update({"sweeter_net_tendency_lower": False}))
    add(lambda r: r["high_difficulty_choice_scenario"].update({"preferred_path": "right_high_difficulty_sweeter_candy"}))
    add(lambda r: r["high_difficulty_choice_scenario"].update({"hard_sweeter_path_not_forced": False}))
    add(lambda r: r["high_difficulty_choice_scenario"]["actual_consumed_path"].update({"path_id": "right_high_difficulty_sweeter_candy"}))
    add(lambda r: r["high_difficulty_choice_scenario"].update({"actual_consumed_path_count": 2}))
    add(lambda r: r["high_difficulty_choice_scenario"].update({"unchosen_sweeter_path_consumed": True}))
    add(lambda r: r["high_difficulty_choice_scenario"].update({"both_paths_consumed": True}))
    add(lambda r: r["high_difficulty_choice_scenario"].update({"action_selection_applied": True}))
    add(lambda r: r["high_difficulty_choice_scenario"]["actual_consumed_path"].update({"subjective_pleasure_claim": True}))
    add(lambda r: r["high_difficulty_choice_scenario"]["actual_consumed_path"].update({"runtime_endocrine_state_persisted": True}))
    add(lambda r: r["choice_result_summary"].update({"raw_sweeter_response_higher": False}))
    add(lambda r: r["choice_result_summary"].update({"return_path_available": False}))
    add(lambda r: r["choice_result_summary"].update({"sweeter_net_tendency_lower": False}))
    add(lambda r: r["choice_result_summary"].update({"ordinary_easy_path_preferred": False}))
    add(lambda r: r["choice_result_summary"].update({"hard_sweeter_path_not_forced": False}))
    add(lambda r: r["choice_result_summary"].update({"chosen_path": "right_high_difficulty_sweeter_candy"}))
    add(lambda r: r["choice_result_summary"].update({"both_paths_consumed": True}))
    add(lambda r: r["human_summary"].update({"plain_result": ""}))
    add(lambda r: r["blocked_flags"].update({"proof_of_learning_claim_allowed": True}))
    return invalids


def _dict(value: Any, errors: list[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(code)
        return {}
    return value
